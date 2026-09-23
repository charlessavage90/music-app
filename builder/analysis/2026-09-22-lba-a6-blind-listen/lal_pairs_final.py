"""Apply the owner's strike to the drawn pairs and write `lal_pairs.json` (`LBA-AM6-2` step 9).

He saw the twelve pairs as ENDPOINT NAMES ONLY — no interior, no length, no map — and may strike any.
A struck primary is filled by the next reserve, in order; a struck reserve simply leaves. Fewer than
8 pairs left: stop — he supplies pairs, which must pass the same gates.

    cd builder && UV_LINK_MODE=copy uv run python analysis/2026-09-22-lba-a6-blind-listen/lal_pairs_final.py --strike 3 11
    (numbers are 1-based positions in lal_pairs_drawn.json's primary-then-reserve order; none = no strike)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import LAL_PAIRS, PAIRS_PER_LISTEN, in_dir, sha256_of  # noqa: E402


def apply_strike(drawn: dict, struck: set[int]) -> dict:
    ordered = drawn["primary"] + drawn["reserve"]
    if any(i < 1 or i > len(ordered) for i in struck):
        raise SystemExit(f"strike positions must be 1..{len(ordered)}")
    kept = [p for i, p in enumerate(ordered, 1) if i not in struck]
    if len(kept) < PAIRS_PER_LISTEN:
        raise SystemExit(f"only {len(kept)} pairs left after the strike; the owner supplies pairs, "
                         "which must pass the same gates")
    return {"primary": kept[:PAIRS_PER_LISTEN], "reserve": kept[PAIRS_PER_LISTEN:],
            "struck": [{"position": i, "a": ordered[i - 1]["a"]["name"], "b": ordered[i - 1]["b"]["name"]}
                       for i in sorted(struck)]}


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strike", type=int, nargs="*", default=[])
    ap.add_argument("--drawn", default="lal_pairs_drawn_am7.json",
                    help="the draw to strike from; LBA-AM7 supersedes lal_pairs_drawn.json")
    args = ap.parse_args(argv)
    drawn_file = in_dir(args.drawn)
    drawn = json.loads(drawn_file.read_text(encoding="utf-8"))
    final = apply_strike(drawn, set(args.strike))
    doc = {"what": "LBA-AM6-2: the listen's pairs after the owner's strike. Names, MBIDs, pool ranks only.",
           "drawn_file": {"name": drawn_file.name, "sha256": sha256_of(drawn_file)},
           **final, "finished_utc": datetime.now(timezone.utc).isoformat()}
    LAL_PAIRS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {LAL_PAIRS.name}: {len(final['primary'])} primary, {len(final['reserve'])} reserve, "
          f"{len(final['struck'])} struck; sha256 {sha256_of(LAL_PAIRS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
