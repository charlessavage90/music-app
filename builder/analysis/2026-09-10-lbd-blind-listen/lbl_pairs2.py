"""`LBL-` listen 2's pair table, emitted from the pre-screen. No MBID is ever transcribed by hand.

`LBD-AM6`. The selection was made by `lbl_prescreen2.py`, whose rule and thresholds were committed
before it ran; this script only takes the top of its ranked survivors and writes the table the
harness pins. It computes nothing and decides nothing, so it carries no threshold of its own.

  primary  = survivors ranked 1-8
  reserve  = survivors ranked 9-12, in rank order

The pre-screen's map-labelled detail is deliberately NOT copied here: this file is safe for the
blind runner to read, and `lbl_prescreen2.json` is not.

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-10-lbd-blind-listen/lbl_pairs2.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from lbl_common import PAIRS_PER_LISTEN, RESERVES_PER_LISTEN, in_dir, sha256_of

PRESCREEN = in_dir("lbl_prescreen2.json")
WANTED = PAIRS_PER_LISTEN + RESERVES_PER_LISTEN


def slim(row: dict) -> dict:
    """Endpoints and the familiarity count that ranked them. Never the per-map detail."""
    return {side: {k: row[side][k] for k in ("name", "mbid", "rank", "minutes")} for side in ("a", "b")} | {
        "familiar_interior": row["familiarity"]["familiar_interior"],
        "distinct_interior": row["familiarity"]["distinct_interior"],
    }


def render_md(out: dict) -> None:
    """The human-readable table. Restates no count the pre-screen owns."""
    lines = ["# `LBL-` listen 2 pairs — `LBD-AM6`", "",
             "Selected by `lbl_prescreen2.py` from the candidate draw, ranked by fewest familiar "
             "interior artists. **Every count — pool, drawn, survivors, and why each rejected pair "
             "failed — is owned by [`lbl_prescreen2.md`](lbl_prescreen2.md) and is restated nowhere, "
             "including here.** The two figures on each row below are that pair's own.", ""]
    for part, title in (("primary", "Primary"), ("reserve", "Reserve, in order")):
        lines += [f"## {title}", "", "| # | A | B | familiar interiors / distinct |", "|---|---|---|---:|"]
        for i, p in enumerate(out[part], 1):
            lines.append(f"| {i} | {p['a']['name']} | {p['b']['name']} | "
                         f"{p['familiar_interior']}/{p['distinct_interior']} |")
        lines.append("")
    in_dir("lbl_pairs2.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md-only", action="store_true",
                    help="re-render the table from the committed lbl_pairs2.json. The pinned JSON is "
                         "NOT rewritten: its sha256 is pinned in lbl_common and a fresh timestamp "
                         "would break the harness's G3 gate for no gain.")
    args = ap.parse_args(argv)

    if args.md_only:
        out = json.loads(in_dir("lbl_pairs2.json").read_text(encoding="utf-8"))
        render_md(out)
        print("[pairs2] re-rendered lbl_pairs2.md; lbl_pairs2.json untouched", flush=True)
        return 0

    pre = json.loads(PRESCREEN.read_text(encoding="utf-8"))
    survivors = pre["survivors_ranked"]
    if len(survivors) < WANTED:
        raise SystemExit(f"only {len(survivors)} survivors; {WANTED} are needed. "
                         "Report the counts to the owner; do not write a partial table.")
    rows = [slim(r) for r in survivors[:WANTED]]
    out = {
        "amendment": "LBD-AM6",
        "listen": 2,
        "comparison": "LBD-A0V (incumbent) against LBD-A5V (challenger) — unchanged from LBD-AM5-5",
        "selected_by": {"script": "lbl_prescreen2.py", "script_sha256": pre["script_sha256"],
                        "output": PRESCREEN.name, "output_sha256": sha256_of(PRESCREEN),
                        "thresholds": pre["thresholds"], "counts": pre["counts"]},
        "note": "Ranked by fewest interior artists the owner's export shows he is familiar with. "
                "Selection was on the magnitude of journey difference and on familiarity, never on "
                "direction. Safe for a blind runner to read: no per-map detail is copied here.",
        "primary": rows[:PAIRS_PER_LISTEN],
        "reserve": rows[PAIRS_PER_LISTEN:WANTED],
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    in_dir("lbl_pairs2.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    render_md(out)
    print(f"[pairs2] wrote lbl_pairs2.json sha256 {sha256_of(in_dir('lbl_pairs2.json'))}", flush=True)
    for p in out["primary"]:
        print(f"[pairs2] primary  {p['a']['name']} -> {p['b']['name']}", flush=True)
    for p in out["reserve"]:
        print(f"[pairs2] reserve  {p['a']['name']} -> {p['b']['name']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
