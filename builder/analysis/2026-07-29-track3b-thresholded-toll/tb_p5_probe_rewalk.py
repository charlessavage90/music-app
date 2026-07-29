"""TB-P5 probe 1 — independent re-walk of all four Track 3b arms.

Reimplements, from the *production* cost function (`api/.../pathfinding.py`) plus the
pre-registration §1 text for the device, everything `run_arms_tb.py` obtained by
importing `mirror.py` and `run_arms.py`:

  * average-rank percentile (computed by a different algorithm than
    `MirrorContext.build`, then cross-checked against it),
  * the edge cost including `w * k * max(0, pctl(v) - 0.90)` on the relaxation target,
    destination exempt, added only when live,
  * Dijkstra,
  * the all-`known` walk and its victim rule (most popular interior, ties -> lowest id).

Then compares every snapshot path against the committed `tb_paths.json`, and recomputes
the victim counters at every depth 0..19 (the committed file only stores snapshots, so
the counters cannot be re-derived from it).

Scored pairs only (12) — anchors are descriptive and add 4/16 of the runtime.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p5_probe_rewalk.py
"""

from __future__ import annotations

import hashlib
import heapq
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
T3 = ROOT / "builder" / "analysis" / "2026-07-28-track3-depth-descent"

WS = {"P": 0.0, "TB-A1": 0.10, "TB-A2": 0.30, "TB-A3": 1.00}
KNEE = 0.90
MAX_DEPTH = 20
SNAPSHOTS = (0, 1, 2, 3, 5, 7, 10, 15, 20)

# production weights, read off ApiConfig at run time (never restated) -- see below.


def avg_rank_pctl(pop: np.ndarray) -> np.ndarray:
    """Average-rank percentile, by unique-value grouping (not the sort-scan of
    MirrorContext.build). Same definition, different route."""
    n = pop.size
    vals, inv, counts = np.unique(pop, return_inverse=True, return_counts=True)
    last = np.cumsum(counts) - 1                 # 0-based last index in sorted order
    first = last - counts + 1
    avg = (first + last) / 2.0
    return avg[inv] / (n - 1)


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # TB-G3
    print(f"artifact ok: sha256 {digest[:8]}...{digest[-7:]}")

    from artistpath_api.config import ApiConfig
    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext

    cfg = ApiConfig()
    store = GraphStore.load(GRAPH)
    offsets = np.asarray(store.offsets, dtype=np.int64)
    nbrs = np.asarray(store.neighbours, dtype=np.int64)
    scores = np.asarray(store.scores, dtype=np.float32)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    dhp = np.asarray(store.degree_hub_penalty, dtype=np.float64)

    pctl = avg_rank_pctl(pop)
    mirror_pctl = MirrorContext.build(store).pctl
    assert np.array_equal(pctl, mirror_pctl), "pctl route disagreement"
    print(f"pctl reproduces MirrorContext.build exactly (N={pop.size:,})")

    w_sim, w_jump, w_floor = cfg.w_sim, cfg.w_jump, cfg.w_floor
    w_avoid, w_hub, w_hop = cfg.w_avoid, cfg.w_degree_hub, cfg.w_hop
    relax_known = cfg.floor_relax_known

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    doc = json.loads((T3 / "pairs_v2.json").read_text(encoding="utf-8"))
    scored = [(e["pair"], e["src"], e["dst"])
              for key in ("analysis_pairs", "held_out_pairs") for e in doc[key]]

    def dijkstra(src: int, dst: int, hard: set[int], floor_val: float,
                 thresh: float) -> list[int] | None:
        thresh_on = thresh != 0.0
        dist = {src: 0.0}
        prev: dict[int, int] = {}
        pq: list[tuple[float, int]] = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if u == dst:
                break
            if d > dist.get(u, float("inf")):
                continue
            pop_u = float(pop[u])
            lo, hi = int(offsets[u]), int(offsets[u + 1])
            for idx in range(lo, hi):
                v = int(nbrs[idx])
                if v in hard:
                    continue
                pop_v = float(pop[v])
                cost = (
                    w_sim * (1.0 - float(scores[idx]))
                    + w_jump * abs(pop_u - pop_v)
                    + w_floor * max(0.0, floor_val - pop_v)
                    + w_avoid * 0.0
                    + w_hub * float(dhp[v])
                    + w_hop
                )
                if thresh_on and v != dst:
                    cost += thresh * max(0.0, float(pctl[v]) - KNEE)
                nd = d + cost
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        if dst not in prev:
            return None
        path = [dst]
        while path[-1] != src:
            path.append(prev[path[-1]])
        return path[::-1]

    committed = json.loads((HERE / "tb_paths.json").read_text(encoding="utf-8"))
    assert committed["artifact_sha256"] == digest

    report: dict = {"artifact_sha256": digest, "arms": {}}
    t0 = time.time()
    total_mismatch = 0
    for arm, w in WS.items():
        sub_by_depth = [0] * MAX_DEPTH
        tot_by_depth = [0] * MAX_DEPTH
        mismatch: list[str] = []
        guard_would_fire = 0
        for key, a, b in scored:
            src, dst = by_name[a], by_name[b]
            base_floor = min(float(pop[src]), float(pop[dst]))
            excl: list[int] = []
            for d in range(MAX_DEPTH + 1):
                floor_val = max(0.0, base_floor - relax_known * len(excl))
                path = dijkstra(src, dst, set(excl), floor_val, w * len(excl))
                if path is not None and len(path) == 2:
                    guard_would_fire += 1
                if d in SNAPSHOTS:
                    got = committed["paths"][arm][key][str(d)]
                    if got != path:
                        mismatch.append(f"{key}@d{d}")
                if path is None:
                    break
                interior = path[1:-1]
                if not interior:
                    break
                if d < MAX_DEPTH:
                    victim0 = min(interior, key=lambda v: (-pop[v], v))
                    tot_by_depth[d] += 1
                    if float(pctl[victim0]) < KNEE:
                        sub_by_depth[d] += 1
                victim = min(interior, key=lambda v: (-pop[v], v))
                excl = excl + [victim]
        total_mismatch += len(mismatch)
        report["arms"][arm] = {
            "w": w,
            "snapshot_cells_compared": len(scored) * len(SNAPSHOTS),
            "path_mismatches": mismatch,
            "sub_decile_victims": sum(sub_by_depth),
            "victims_total": sum(tot_by_depth),
            "sub_decile_by_depth": sub_by_depth,
            "guard_g_would_fire_on_scored_pairs": guard_would_fire,
        }
        vs = committed["victim_stats"][arm]
        print(f"  {arm:<7} w={w:<5} ({time.time() - t0:6.1f}s)  "
              f"path mismatches {len(mismatch)}/{len(scored) * len(SNAPSHOTS)}   "
              f"sub-decile victims mine {sum(sub_by_depth)}/{sum(tot_by_depth)} "
              f"vs committed {vs['sub_decile_victims']}/{vs['victims_total']}   "
              f"by-depth match {sub_by_depth == vs['sub_decile_by_depth']}   "
              f"guard-G on scored pairs {guard_would_fire}")

    report["total_path_mismatches"] = total_mismatch
    (HERE / "tb_p5_rewalk.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"\ntotal snapshot-path mismatches across all arms: {total_mismatch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
