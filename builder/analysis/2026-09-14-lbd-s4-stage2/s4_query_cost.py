"""`LBA-M1`'s query-cost half, and `LBA-G1`(b) — one arm against the served map, back to back.

§4: "median and p95 wall-clock of the shipped `find_journey` at **d0**, no exclusions, `ApiConfig`
defaults, over a fixed pair set drawn once and reused for every arm — the same process, the same
machine, the arm's map and the served map measured back to back."

WHY ONLY d0, read from source rather than assumed (`LBA-D5`'s block, re-verified here):
`pathfinding.py:130-132` computes `ramp_fame = cfg.w_known_ramp_fame_pctl * n_known`, and
`n_known` is `sum(1 for e in excludes if e.reason == KNOWN)` (`:130`). With `excludes=[]` that is
exactly `0.0`, so `ramp_fame_on` is False and a fame-free build takes the production cost
function's exact values. At any deeper depth the ramp is live and fame is absent, so no deeper
depth is measurable here. That limit is stated, not worked around.

"BACK TO BACK" IS IMPLEMENTED PER PAIR, not per run. For each pair the served map is timed and
then the arm is timed, so machine drift over the run cancels within every pair rather than only in
aggregate. The ratio the gate reads is then a ratio of two medians taken under the same conditions,
which is the property §5 calls the bar's strength ("machine state cancels").

⚠ The gate fires on the MEDIAN alone. p95 is reported beside it because §5 requires it — the
Gate 2->3 review's cited two-second figure is a TAIL while the gate reads a median, and reporting
one without the other invites the two to be confused.

⚠ This measures WHAT IT COSTS TO SERVE A QUERY, never whether the answer is good. §9 bars any
routing or path-quality claim beyond this, and a denser map is not a better journey until a
listener says so (`REQ-38`).

    uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_query_cost.py --arm LBA-A2
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))

import artistpath_api.graph_store as gs  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.pathfinding import find_journey  # noqa: E402

from s4_common import sha256_of  # noqa: E402

ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
SERVED = Path(r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin")
PAIRSET = HERE / "s4_pairset.json"


def timed(store, cfg, ia: int, ib: int) -> tuple[float, int]:
    started = time.perf_counter()
    result = find_journey(store, ia, ib, [], cfg)
    elapsed = time.perf_counter() - started
    hops = len(result[0]) if result else 0
    return elapsed, hops


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, help="e.g. LBA-A2")
    ap.add_argument("--artifact", type=Path, default=None)
    args = ap.parse_args(argv)

    pairset = json.loads(PAIRSET.read_text(encoding="utf-8"))
    pair_file = Path(pairset["pair_file"])
    if sha256_of(pair_file) != pairset["pair_file_sha256"]:
        raise SystemExit("REFUSING: the pair file is not the one that was pinned before timing began")
    pairs = [line.split("\t") for line in pair_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(pairs) != pairset["n_pairs"]:
        raise SystemExit("REFUSING: the pair file does not hold the drawn number of pairs")

    artifact = args.artifact or Path(pairset["maps"][args.arm])
    cfg = ApiConfig()
    print(f"[qc] {args.arm}: {artifact.name}  {len(pairs)} pairs  ApiConfig defaults  d0, no exclusions",
          flush=True)

    served = gs.GraphStore.load(SERVED)
    arm = gs.GraphStore.load(artifact)
    served_index = {m: i for i, m in enumerate(served.mbids)}
    arm_index = {m: i for i, m in enumerate(arm.mbids)}

    # One warm-up pair on each, discarded: the first Dijkstra in a process pays import-time and
    # allocator costs that belong to neither map.
    a0, b0 = pairs[0]
    timed(served, cfg, served_index[a0], served_index[b0])
    timed(arm, cfg, arm_index[a0], arm_index[b0])

    served_times: list[float] = []
    arm_times: list[float] = []
    served_nulls = arm_nulls = 0
    for a, b in pairs:
        t_s, h_s = timed(served, cfg, served_index[a], served_index[b])
        t_a, h_a = timed(arm, cfg, arm_index[a], arm_index[b])
        served_times.append(t_s)
        arm_times.append(t_a)
        served_nulls += 1 if h_s == 0 else 0
        arm_nulls += 1 if h_a == 0 else 0

    def stats(xs: list[float]) -> dict:
        ordered = sorted(xs)
        return {
            "p50_s": round(statistics.median(ordered), 6),
            "p95_s": round(ordered[int(0.95 * (len(ordered) - 1))], 6),
            "mean_s": round(statistics.fmean(ordered), 6),
            "min_s": round(ordered[0], 6),
            "max_s": round(ordered[-1], 6),
            "p50_ms": round(statistics.median(ordered) * 1000, 3),
            "p95_ms": round(ordered[int(0.95 * (len(ordered) - 1))] * 1000, 3),
        }

    s_stats, a_stats = stats(served_times), stats(arm_times)
    ratio = a_stats["p50_s"] / s_stats["p50_s"] if s_stats["p50_s"] else float("inf")
    fires = ratio > 2.0

    record = {
        "arm": args.arm,
        "artifact": str(artifact),
        "artifact_sha256": sha256_of(artifact),
        "served_artifact": str(SERVED),
        "pairs": len(pairs),
        "pair_file_sha256": pairset["pair_file_sha256"],
        "depth": "d0 — no exclusions, so n_known = 0, ramp_fame = 0.0 and the fame ramp is OFF "
                 "(pathfinding.py:130-132). No deeper depth is measurable on a fame-free build.",
        "interleaving": "per pair: served timed, then the arm timed, so drift cancels within each pair",
        "served": s_stats,
        "arm": a_stats,
        "served_paths_empty": served_nulls,
        "arm_paths_empty": arm_nulls,
        "lba_g1b": {
            "statistic": "the arm's median d0 wall-clock / the served map's, same process, same pairs",
            "ratio_p50": round(ratio, 4),
            "bar": 2.0,
            "fires": fires,
            "reads_median_only": True,
            "p95_reported_beside_it_not_read": {"served_p95_ms": s_stats["p95_ms"],
                                                "arm_p95_ms": a_stats["p95_ms"]},
        },
        "served_local_median_d0_ms": s_stats["p50_ms"],
        "served_local_median_note": ("the quantity §5 records as being on NO document — LBA-M1 "
                                     "supplies it as a by-product of its own ratio, which is why "
                                     "the gate supplies its own calibration"),
        "bars": "This measures the COST of serving a query, never whether the answer is good (§9).",
        "script_sha256": sha256_of(Path(__file__)),
        "measured_utc": datetime.now(timezone.utc).isoformat(),
    }
    out = HERE / f"s4_query_cost_{args.arm}.json"
    out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"[qc] served p50 {s_stats['p50_ms']:.3f} ms  p95 {s_stats['p95_ms']:.3f} ms", flush=True)
    print(f"[qc] {args.arm:<8} p50 {a_stats['p50_ms']:.3f} ms  p95 {a_stats['p95_ms']:.3f} ms", flush=True)
    print(f"[qc] LBA-G1(b) ratio {ratio:.4f}  bar 2.0  fires={fires}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
