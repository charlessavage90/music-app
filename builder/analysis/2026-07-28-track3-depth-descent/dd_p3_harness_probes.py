"""DD-P3 second half (harness review): independent recomputation of the Track 3 scores.

Read-only. Imports NOTHING from `score_t3.py` — every statistic below is recomputed
from `t3_paths.json` + `t3_fame.json` by a separate route, including a second,
independent implementation of the average-rank percentile that `MirrorContext.pctl`
provides (unique-value grouping instead of the sorted run-scan), so a bug in one is
not silently shared by the other.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/dd_p3_harness_probes.py
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

C1_DEPTHS = (10, 15, 20)


def pctl_independent(pop: np.ndarray) -> np.ndarray:
    """Average-rank percentile, by unique-value grouping rather than a run-scan."""
    n = pop.size
    uniq, inv, counts = np.unique(pop, return_inverse=True, return_counts=True)
    last = np.cumsum(counts) - 1            # last 0-based rank of each unique value
    first = last - counts + 1
    avg = (first + last) / 2.0
    return avg[inv] / (n - 1)


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    from artistpath_api.graph_store import GraphStore

    sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
    from mirror import MirrorContext

    store = GraphStore.load(GRAPH)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = pctl_independent(pop)
    pctl_mirror = MirrorContext.build(store).pctl
    print(f"artifact {digest[:8]}  N={len(pop):,}")
    print(f"[pctl] independent vs MirrorContext max|diff| = "
          f"{np.abs(pctl - pctl_mirror).max():.3e}\n")

    offsets = np.asarray(store.offsets)
    neighbours = np.asarray(store.neighbours)
    scores = np.asarray(store.scores)

    def sim(u, v):
        row = neighbours[offsets[u]:offsets[u + 1]]
        return float(scores[offsets[u] + int(np.nonzero(row == v)[0][0])])

    P = json.loads((HERE / "t3_paths.json").read_text(encoding="utf-8"))
    FA = json.loads((HERE / "t3_fame.json").read_text(encoding="utf-8"))
    F, MB = FA["fame"], P["node_mbids"]
    matched = {m for m, r in FA["rows"].items() if r.get("matched")}
    notable = set(FA["potentially_notable_unmatched"])
    arms = P["arms"]
    analysis = [p for p in P["pairs"] if P["splits"][p] == "analysis"]
    held = [p for p in P["pairs"] if P["splits"][p] == "held_out"]
    anchors = [p for p in P["pairs"] if P["splits"][p] == "anchor"]

    def cell(a, p, d):
        return P["paths"][a][p][str(d)]

    def ints(path):
        return path[1:-1]

    def fs(path):
        return [F[MB[str(n)]] for n in ints(path)]

    # ---------------- D: uniform-drop audit ----------------
    print("== D: missingness audit ==")
    bad = []
    per_depth_missing = {}
    for p in P["pairs"]:
        for d in P["snapshots"]:
            present = tuple(cell(a, p, d) is not None for a in arms)
            if len(set(present)) != 1:
                bad.append((p, d, present))
            if not present[0]:
                per_depth_missing[f"{p}@d{d}"] = True
    print(f"cells whose presence differs between arms: {len(bad)}  {bad}")
    print(f"missing cells (all arms): {sorted(per_depth_missing)}")
    print(f"declared dropped_cells_d7: {P['dropped_cells_d7']}")
    # empty-interior cells would also be arm-correlated if they existed
    empty = [(a, p, d) for a in arms for p in P["pairs"] for d in P["snapshots"]
             if cell(a, p, d) and not ints(cell(a, p, d))]
    print(f"cells with a path but no interior (guard-G violation): {len(empty)}\n")

    # ---------------- B: DD-G2 recheck ----------------
    print("== B: DD-G2 recheck from the paths file ==")
    diff = [(a, p) for a in arms if a != "P" for p in P["pairs"]
            if cell(a, p, 0) != cell("P", p, 0)]
    print(f"d0 differences vs P over {len(P['pairs'])} pairs x {len(arms) - 1} arms: "
          f"{len(diff)}  {diff}")
    # d1 is the first depth at which k > 0
    d1diff = {a: sum(1 for p in P["pairs"] if cell(a, p, 1) != cell("P", p, 1))
              for a in arms if a != "P"}
    print(f"d1 differences vs P (device live at k=1): {d1diff}\n")

    # ---------------- guard-G accounting ----------------
    print("== guard-G firing, reconstructed ==")
    for p in anchors:
        lens = [len(cell("P", p, d)) - 1 if cell("P", p, d) else None
                for d in P["snapshots"]]
        adj = sim(cell("P", p, 0)[0], cell("P", p, 0)[-1]) if _adjacent(
            neighbours, offsets, cell("P", p, 0)[0], cell("P", p, 0)[-1]) else None
        print(f"  {p:<28} endpoints adjacent: {adj is not None}  "
              f"P hop-counts at snapshots {lens}")
    print()

    # ---------------- E: recompute the criteria ----------------
    print("== E: independent recomputation (analysis pairs) ==")
    hdr = (f"{'arm':<7}{'C1mean':>9}{'C1med':>9}{'neg%':>7}{'n':>4}"
           f"{'C2':>8}{'C2nodrop':>10}{'C2/pair':>9}"
           f"{'C5cell':>8}{'C5dist':>8}{'C6':>8}{'C4all':>8}{'C4int':>8}{'unm%':>7}")
    print(hdr)
    out = {}
    for a in arms:
        dmean, dmed, dlen = [], [], []
        for p in analysis:
            for d in C1_DEPTHS:
                pa, pp = cell(a, p, d), cell("P", p, d)
                if not pa or not pp:
                    continue
                dmean.append(statistics.mean(fs(pa)) - statistics.mean(fs(pp)))
                dmed.append(statistics.median(fs(pa)) - statistics.median(fs(pp)))
                dlen.append(len(ints(pa)) - len(ints(pp)))

        def pooled(d, pairs):
            return [f for p in pairs if cell(a, p, d) for f in fs(cell(a, p, d))]
        f5, f20 = pooled(5, analysis), pooled(20, analysis)
        c2 = statistics.median(f5) - statistics.median(f20)
        nod = [p for p in analysis if p != "Openzone Bar -> Gjallarhorn"]
        c2_nodrop = (statistics.median(pooled(5, nod))
                     - statistics.median(pooled(20, nod)))
        # length-unweighted: per-pair median first, then median across pairs
        pm5 = [statistics.median(fs(cell(a, p, 5))) for p in analysis if cell(a, p, 5)]
        pm20 = [statistics.median(fs(cell(a, p, 20))) for p in analysis if cell(a, p, 20)]
        c2_pair = statistics.median(pm5) - statistics.median(pm20)

        per_cell, distinct = [], set()
        for p in analysis:
            for d in C1_DEPTHS:
                q = cell(a, p, d)
                if not q:
                    continue
                sub = [n for n in ints(q) if pctl[n] < 0.90]
                per_cell.append(len(sub))
                distinct.update(sub)

        allhops, inthops = [], []
        for p in analysis:
            for d in C1_DEPTHS:
                q = cell(a, p, d)
                if not q:
                    continue
                allhops += [sim(q[i], q[i + 1]) for i in range(len(q) - 1)]
                inthops += [sim(q[i], q[i + 1]) for i in range(1, len(q) - 2)]

        ivals = [MB[str(n)] for p in analysis for d in C1_DEPTHS
                 if cell(a, p, d) for n in ints(cell(a, p, d))]
        unm = 100.0 * sum(1 for m in ivals if m not in matched) / len(ivals)

        out[a] = {
            "c1_mean": statistics.mean(dmean), "c1_median_stat": statistics.mean(dmed),
            "neg": 100 * sum(1 for x in dmean if x < 0) / len(dmean), "n": len(dmean),
            "c2": c2, "c2_nodrop": c2_nodrop, "c2_pair": c2_pair,
            "c5_cell": statistics.mean(per_cell), "c5_distinct": len(distinct),
            "c6": statistics.mean(dlen),
            "c4_all": statistics.median(allhops), "c4_int": statistics.median(inthops),
            "unmatched_pct": unm,
            "notable_hits": sorted({m for m in ivals if m in notable}),
            "n_interiors": len(ivals),
        }
        r = out[a]
        print(f"{a:<7}{r['c1_mean']:>9.3f}{r['c1_median_stat']:>9.3f}{r['neg']:>6.0f}%"
              f"{r['n']:>4}{r['c2']:>8.3f}{r['c2_nodrop']:>10.3f}{r['c2_pair']:>9.3f}"
              f"{r['c5_cell']:>8.2f}{r['c5_distinct']:>8}{r['c6']:>+8.2f}"
              f"{r['c4_all']:>8.3f}{r['c4_int']:>8.3f}{r['unmatched_pct']:>6.1f}%")

    # ---------------- F: unmatched-floor sensitivity ----------------
    print("\n== F: DD-C1 with unmatched interiors EXCLUDED (matched-only means) ==")
    for a in arms:
        d2 = []
        for p in analysis:
            for d in C1_DEPTHS:
                pa, pp = cell(a, p, d), cell("P", p, d)
                if not pa or not pp:
                    continue
                va = [F[MB[str(n)]] for n in ints(pa) if MB[str(n)] in matched]
                vp = [F[MB[str(n)]] for n in ints(pp) if MB[str(n)] in matched]
                if va and vp:
                    d2.append(statistics.mean(va) - statistics.mean(vp))
        print(f"  {a:<7} matched-only C1 = {statistics.mean(d2):+.3f}  "
              f"(n={len(d2)}, neg {100 * sum(1 for x in d2 if x < 0) / len(d2):.0f} %)")

    print("\n== F: A11 potentially-notable unmatched artists inside scored C1 cells ==")
    for a in arms:
        hits = out[a]["notable_hits"]
        print(f"  {a:<7} {len(hits)} distinct: "
              f"{[FA['names'][m] for m in hits]}")

    print("\n== held-out slice, DD-C1 (stability check) ==")
    for a in arms:
        d3 = []
        for p in held:
            for d in C1_DEPTHS:
                pa, pp = cell(a, p, d), cell("P", p, d)
                if pa and pp:
                    d3.append(statistics.mean(fs(pa)) - statistics.mean(fs(pp)))
        print(f"  {a:<7} held-out C1 = {statistics.mean(d3):+.3f} "
              f"(n={len(d3)}, neg {100 * sum(1 for x in d3 if x < 0) / len(d3):.0f} %)")

    print("\n== interior counts by depth (DD-C2's length confound, per arm) ==")
    for a in arms:
        row = []
        for d in (5, 20):
            cs = [len(ints(cell(a, p, d))) for p in analysis if cell(a, p, d)]
            row.append(f"d{d}: mean {statistics.mean(cs):.2f} pooled {sum(cs)}")
        print(f"  {a:<7} " + "   ".join(row))
    return 0


def _adjacent(neighbours, offsets, u, v) -> bool:
    return bool(np.any(neighbours[offsets[u]:offsets[u + 1]] == v))


if __name__ == "__main__":
    raise SystemExit(main())
