"""`DSL-G1` — the listen's generator is the candidate the lattice measured (`DRP-AM7-3`).

Run by the PREPARATION session, first, before the pre-screen. Re-runs the primary ladder for every
`DRP-T1` and `DRP-T2` pair in `drp_pairs.json`, on both sides, through `dsl_journeys.side_ladder`,
and asserts node-for-node equality at every depth 0–20 with the committed stage-3b cells
(`DRP-S0P0.json`, `DRP-S1P3.json`, identity-checked on LF-normalised bytes). **Effect size: exact;
any divergence fails.**

**Red control:** the same ladders on `DRP-S1` with the ceiling OFF must diverge from `DRP-S1P3` on at
least one pair at some depth ≥ 4, or the ceiling is not being applied.

**Sealing.** This script prints and writes COUNTS ONLY — never a path, never a node id beyond the
pair index. Its output, `dsl_g1.json`, is not side-labelled in any way a runner could use.

    cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \\
      ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_g1.py [--smoke N]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dsl_common import (CELL_A0, CELL_A0_SHA, CELL_S1P3, CELL_S1P3_SHA, DRP_PAIRS, DRP_PAIRS_SHA,  # noqa: E402
                        G1_RESULT, TIERS, pinned_json, sha256_lf)

RED_MIN_DEPTH = 4   # the ceiling is inert at presses 0-3 (f_max = 1.0), so divergence can only start here


def paths_of(lad: list[dict]) -> list:
    """The per-depth journeys as the cell files record them: `path` (node ids, or None) per depth."""
    return [rec.get("path") for rec in lad]


def cell_index(cell: dict) -> dict[tuple[str, int], list]:
    """(set, pair index) -> per-depth paths, primary rule only."""
    return {(p["set"], p["i"]): [d.get("path") for d in p["depths"]]
            for p in cell["pairs"] if p["rule"] == "primary" and p["set"] in TIERS}


def compare(got: list, want: list) -> bool:
    return len(got) == len(want) and all(g == w for g, w in zip(got, want))


def diverges_from(depth_from: int, got: list, want: list) -> bool:
    return any((got[k] if k < len(got) else None) != (want[k] if k < len(want) else None)
               for k in range(depth_from, max(len(got), len(want))))


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", type=int, default=0, help="first N pairs per tier; writes nothing")
    args = ap.parse_args(argv)

    from dsl_journeys import cfg, load_maps, side_ladder

    pairs = pinned_json(DRP_PAIRS, DRP_PAIRS_SHA)
    cells = {"incumbent": pinned_json(CELL_A0, CELL_A0_SHA), "challenger": pinned_json(CELL_S1P3, CELL_S1P3_SHA)}
    maps = load_maps()
    for role, cell in cells.items():
        if cell["graph_sha256"] != maps[role].sha:
            raise SystemExit(f"DSL-G1 REFUSED: {role}'s cell was built on {cell['graph_sha256']}, "
                             f"the loaded map is {maps[role].sha}")
    ref = {role: cell_index(cell) for role, cell in cells.items()}
    config = cfg()

    counts = {role: {"pairs": 0, "identical": 0, "diverged": []} for role in cells}
    red = {"pairs": 0, "diverged_at_or_after_press_4": 0}
    t0 = time.time()
    for tier in TIERS:
        plist = pairs["strata"][tier]["pairs"]
        for p in (plist[: args.smoke] if args.smoke else plist):
            s, t, i = p["source"], p["target"], p["i"]
            status = {}
            for role in cells:
                same = compare(paths_of(side_ladder(role, maps[role], s, t, config)), ref[role][(tier, i)])
                counts[role]["pairs"] += 1
                counts[role]["identical"] += same
                if not same:
                    counts[role]["diverged"].append([tier, i])
                status[role] = "ok" if same else "DIVERGED"
            off = paths_of(side_ladder("challenger", maps["challenger"], s, t, config, ceiling=False))
            red["pairs"] += 1
            red["diverged_at_or_after_press_4"] += diverges_from(RED_MIN_DEPTH, off, ref["challenger"][(tier, i)])
            print(f"[g1] {tier} pair {i}: incumbent {status['incumbent']}; challenger {status['challenger']}  "
                  f"{time.time() - t0:.0f}s", flush=True)

    passed = all(not c["diverged"] for c in counts.values())
    red_ok = red["diverged_at_or_after_press_4"] >= 1
    verdict = "PASS" if passed and red_ok else "FAIL"
    print(f"[g1] reproduction {'exact' if passed else 'DIVERGED'}; red control "
          f"{red['diverged_at_or_after_press_4']}/{red['pairs']} diverged (needs >= 1): {verdict}", flush=True)
    if args.smoke:
        # A smoke run's red control may legitimately see no divergence on a handful of pairs; only
        # reproduction is judged here.
        print("[g1] smoke run: nothing written", flush=True)
        return 0 if passed else 1
    here = Path(__file__).resolve().parent
    out = {
        "what": "DSL-G1 (DRP-AM7-3): the listen generator reproduces the DRP-S0P0 and DRP-S1P3 cells, "
                "primary rule, every DRP-T1/DRP-T2 pair, depths 0-20. Counts only.",
        "verdict": verdict,
        "reproduction": counts,
        "red_control": {**red, "passed": red_ok, "rule": "ceiling off on DRP-S1 must diverge from DRP-S1P3 "
                        "at some press >= 4 on >= 1 pair"},
        "map_sha256": {"incumbent": maps["incumbent"].sha, "challenger": maps["challenger"].sha},
        "cell_sha256_lf": {"incumbent": sha256_lf(CELL_A0), "challenger": sha256_lf(CELL_S1P3)},
        "harness_sha256_lf": {n: sha256_lf(here / n) for n in ("dsl_g1.py", "dsl_journeys.py", "dsl_common.py")},
        "seconds": round(time.time() - t0, 1),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    G1_RESULT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
