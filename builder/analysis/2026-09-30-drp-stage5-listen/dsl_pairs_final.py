"""Apply the owner's strike to the drawn pairs and write `dsl_pairs.json` (`DRP-AM7-2` step 9).

He sees the twelve pairs as ENDPOINT NAMES ONLY — no interior, length or side — and may strike any.
A struck primary is filled by the next unstruck reserve **of the same tier**; if that tier has none
left, by the next unstruck reserve of the other tier (recorded). A struck reserve simply leaves.
Fewer than 8 pairs left: stop — he supplies pairs, which must pass the same gates.

After this runs, its printed sha256 is pinned as `dsl_common.DSL_PAIRS_SHA` by commit.

    cd api && uv run python ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_pairs_final.py --strike 3 11
    (1-based positions in dsl_pairs_drawn.json's primary-then-reserve order; none = no strike)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dsl_common import DSL_PAIRS, PAIRS_PER_LISTEN, in_dir, sha256_lf  # noqa: E402


def apply_strike(drawn: dict, struck: set[int]) -> dict:
    ordered = drawn["primary"] + drawn["reserve"]
    if any(i < 1 or i > len(ordered) for i in struck):
        raise SystemExit(f"strike positions must be 1..{len(ordered)}")
    n_primary = len(drawn["primary"])
    reserves = [p for i, p in enumerate(drawn["reserve"], n_primary + 1) if i not in struck]
    primary, fills = [], []
    for i, p in enumerate(drawn["primary"], 1):
        if i not in struck:
            primary.append(p)
            continue
        same = next((r for r in reserves if r["tier"] == p["tier"]), None)
        pick = same or (reserves[0] if reserves else None)
        if pick is None:
            raise SystemExit(f"primary {i} is struck and the reserves are exhausted; the owner supplies "
                             "pairs, which must pass the same gates")
        reserves.remove(pick)
        primary.append(pick)
        fills.append({"position": i, "filled_by": f"{pick['a']['name']} → {pick['b']['name']}",
                      "same_tier": same is not None})
    if len(primary) < PAIRS_PER_LISTEN:
        raise SystemExit(f"only {len(primary)} pairs; the owner supplies pairs, which must pass the same gates")
    return {"primary": primary, "reserve": reserves, "fills": fills,
            "struck": [{"position": i, "a": ordered[i - 1]["a"]["name"], "b": ordered[i - 1]["b"]["name"]}
                       for i in sorted(struck)]}


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strike", type=int, nargs="*", default=[])
    args = ap.parse_args(argv)
    drawn_file = in_dir("dsl_pairs_drawn.json")
    drawn = json.loads(drawn_file.read_text(encoding="utf-8"))
    final = apply_strike(drawn, set(args.strike))
    doc = {"what": "DRP-AM7-2 step 9: the listen's pairs after the owner's strike. Names, MBIDs, tiers, pool ranks only.",
           "drawn_file": {"name": drawn_file.name, "sha256_lf": sha256_lf(drawn_file)},
           **final, "finished_utc": datetime.now(timezone.utc).isoformat()}
    DSL_PAIRS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {DSL_PAIRS.name}: {len(final['primary'])} primary, {len(final['reserve'])} reserve, "
          f"{len(final['struck'])} struck; sha256 (LF) {sha256_lf(DSL_PAIRS)} — pin it as DSL_PAIRS_SHA")
    return 0


if __name__ == "__main__":
    sys.exit(main())
