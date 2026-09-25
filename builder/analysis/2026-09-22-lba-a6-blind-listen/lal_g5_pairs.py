"""Derive the `LBA-G5` pair log from the API's own telemetry (`LBA-AM5`).

The API prints one JSON event per journey request on stdout (`telemetry.py`), carrying both
endpoint names. During the gate that stdout is captured to files under
`C:/unsung-fast/lbd-artifacts/lba-g5-logs/`, so the owner never writes a pair by hand.

A JOURNEY is a request with no exclusions (`bypass_depth == 0`); every later request with
exclusions is a reroll of the journey before it, not a new pair. Output is one line per journey,
in the order requested: `from → to  (rerolls: N)`. Pairs and counts only — never a verdict
(`LBA-AM4` bar 1).

Usage:  python lal_g5_pairs.py [--exclude "FROM → TO"]... <log file or directory>...
        (a directory means every *.log in it; --exclude drops every event of that pair, for traffic
        that was not the owner's — issue #215)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def path_events(lines):
    """Yield the `path` telemetry events in `lines`, skipping everything else (uvicorn access
    lines, startup noise, truncated lines)."""
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("event") == "path":
            yield event


def drop_pairs(events, excluded):
    """Drop every event whose (source, target) names are in `excluded`. Applied BEFORE folding, so
    a dropped pair's rerolls cannot attach to a journey on either side of it."""
    return [e for e in events if (e["source"]["name"], e["target"]["name"]) not in excluded]


def journeys(events):
    """Fold events into journeys: a depth-0 request opens one, later rerolls count against it.
    A reroll arriving before any journey (a log that starts mid-walk) is attached to a journey
    whose pair is taken from the reroll itself, so no pair is ever dropped."""
    out: list[dict] = []
    for e in events:
        pair = (e["source"]["name"], e["target"]["name"])
        if e.get("bypass_depth", 0) == 0 or not out or out[-1]["pair"] != pair:
            out.append({"pair": pair, "rerolls": 0 if e.get("bypass_depth", 0) == 0 else 1})
        else:
            out[-1]["rerolls"] += 1
    return out


def render(journeys_):
    return [f"{a} → {b}  (rerolls: {j['rerolls']})" for j in journeys_ for a, b in [j["pair"]]]


def read_paths(args):
    files: list[Path] = []
    for a in args:
        p = Path(a)
        files.extend(sorted(p.glob("*.log")) if p.is_dir() else [p])
    for f in files:
        yield from f.read_text(encoding="utf-8", errors="replace").splitlines()


if __name__ == "__main__":
    args, excluded = sys.argv[1:], set()
    while args[:1] == ["--exclude"] and len(args) > 1:
        a, _, b = args[1].partition(" → ")
        excluded.add((a, b))
        args = args[2:]
    if not args:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(render(journeys(drop_pairs(path_events(read_paths(args)), excluded)))))
