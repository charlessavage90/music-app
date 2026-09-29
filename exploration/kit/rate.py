"""Coherence screen: a model rates each step of a journey (does B plausibly follow A?).

Noisy and cheap; only there to kill obviously broken variants. Each unordered artist pair is rated
once and cached in step_cache.jsonl (shared by every variant and every subagent; append-only).

Scale: 3 = same scene/sound, an obvious next track; 2 = plausible neighbour; 1 = a stretch;
0 = jarring / unrelated. "U" (rater doesn't know either artist well enough) is stored as "U" and
left out of the averages; the share of U is reported so an unrateable variant is visible.

Uses the local `claude` CLI headless (no API key on this machine), lean flags, run from a temp dir
so no project hooks or CLAUDE.md load.
"""
from __future__ import annotations

import json
import shutil
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent
CACHE = KIT / "step_cache.jsonl"
MODEL = os.environ.get("RATER_MODEL", "sonnet")
BATCH = 40
WORKERS = 6
CLAUDE = shutil.which("claude.cmd") or shutil.which("claude") or "claude"

SYSTEM = (
    "You are a music expert with deep knowledge of artists across all genres, eras and countries, "
    "including obscure ones. You rate artist-to-artist transitions in a listening journey. "
    "Answer only in the exact format requested."
)

PROMPT_HEAD = """For each numbered pair below, rate how naturally the second artist follows the first in a
listening journey (like consecutive songs on a well-made radio station or playlist):

3 = same scene or clearly kindred sound; an obvious next track
2 = plausible neighbour; a listener of one would likely enjoy the other
1 = a stretch; some thread connects them but it is a jump
0 = jarring or unrelated
U = you genuinely do not know one of the artists well enough to judge (use sparingly; judge from
    your best knowledge plus the metadata where you reasonably can)

Metadata in brackets is MusicBrainz type / country / start year / disambiguation where known.
Reply with one line per pair, exactly "<number> <rating>", nothing else.

"""


def load_cache() -> dict:
    out = {}
    if CACHE.exists():
        for line in CACHE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    d = json.loads(line)
                    out[d["k"]] = d["r"]
                except Exception:
                    pass
    return out


def meta(ctx, v) -> str:
    f = ctx.store.facts_of(v)
    bits = [f.get("type"), f.get("country") or f.get("area"), (f.get("begin") or "")[:4] or None]
    dis = ctx.store.disambiguations[v] if v < len(ctx.store.disambiguations) else ""
    if dis:
        bits.append(dis)
    return ", ".join(b for b in bits if b)


def call_model(lines: list[str]) -> str:
    prompt = PROMPT_HEAD + "\n".join(lines)
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            [CLAUDE, "-p", "--model", MODEL, "--system-prompt", SYSTEM, "--tools", "",
             "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
             "--output-format", "text"],
            input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=td, timeout=600)
    return r.stdout


def rate_steps(ctx, steps: list[tuple[int, int]]) -> dict:
    """steps: (u, v) node pairs. Returns {step_key: rating} for all of them (cached or new)."""
    from qlook import step_key
    cache = load_cache()
    todo, seen = [], set()
    for u, v in steps:
        k = step_key(ctx, u, v)
        if k not in cache and k not in seen:
            seen.add(k)
            todo.append((k, u, v))
    if todo:
        print(f"[rate] {len(todo)} new steps to rate ({len(cache)} cached), model {MODEL}", flush=True)
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]

    def work(batch):
        lines = [f"{i+1}. {ctx.names[u]} [{meta(ctx, u)}]  ->  {ctx.names[v]} [{meta(ctx, v)}]"
                 for i, (_, u, v) in enumerate(batch)]
        for _attempt in range(2):
            txt = call_model(lines)
            got = {}
            for m in re.finditer(r"^\s*(\d+)[.):]?\s+([0-3]|U)\b", txt, re.M):
                i = int(m.group(1)) - 1
                if 0 <= i < len(batch):
                    r = m.group(2)
                    got[batch[i][0]] = int(r) if r.isdigit() else "U"
            if len(got) >= len(batch) * 0.9:
                break
        with CACHE.open("a", encoding="utf-8") as fh:
            fh.write("".join(json.dumps({"k": k, "r": r}, ensure_ascii=False) + "\n" for k, r in got.items()))
        return got

    with ThreadPoolExecutor(WORKERS) as ex:
        for got in ex.map(work, batches):
            cache.update(got)
    return {step_key(ctx, u, v): cache.get(step_key(ctx, u, v)) for u, v in steps}


def rate_run(ctx, rows) -> dict:
    steps = []
    for r in rows:
        for d in r["ladder"]:
            p = d["path"]
            if p:
                steps += list(zip(p, p[1:]))
    rated = rate_steps(ctx, steps)
    vals = list(rated.values())
    nu = sum(1 for x in vals if x == "U")
    print(f"[rate] {len(vals)} steps, {nu} unknown ({nu/max(1,len(vals))*100:.0f}%)", flush=True)
    return rated
