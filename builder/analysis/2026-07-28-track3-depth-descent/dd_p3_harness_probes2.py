"""DD-P3 harness review, follow-up probes: A11 guard exposure, DD-C2 composition,
DD-C4 hop-set sensitivity, endpoint-resolution identity, guard-G attribution.

Read-only. Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/dd_p3_harness_probes2.py
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
C1_DEPTHS = (10, 15, 20)


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT
    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import walk

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    P = json.loads((HERE / "t3_paths.json").read_text(encoding="utf-8"))
    FA = json.loads((HERE / "t3_fame.json").read_text(encoding="utf-8"))
    V2 = json.loads((HERE / "pairs_v2.json").read_text(encoding="utf-8"))
    F, MB, NM = FA["fame"], P["node_mbids"], FA["names"]
    matched = {m for m, r in FA["rows"].items() if r.get("matched")}
    notable = set(FA["potentially_notable_unmatched"])
    arms = P["arms"]
    analysis = [p for p in P["pairs"] if P["splits"][p] == "analysis"]

    def cell(a, p, d):
        return P["paths"][a][p][str(d)]

    def fs(path, drop: set[str] = frozenset()):
        return [F[MB[str(n)]] for n in path[1:-1] if MB[str(n)] not in drop]

    print("== fame table covers every node in the paths file ==")
    print(f"  node_mbids in t3_paths: {len(MB)}   fame entries: {len(F)}   "
          f"missing: {len([m for m in MB.values() if m not in F])}")
    print(f"  nameless_nodes: {FA['nameless_nodes']}   coverage {FA['coverage']:.4f}\n")

    # ---- A11 guard: what DD-C1 looks like if the flagged-notable unmatched are NOT
    #      maximal reach.  Two counterfactuals bracketing the owner's one-glance call.
    print("== A11 notable-unmatched sensitivity of DD-C1 (analysis, d>=10) ==")
    print(f"{'arm':<7}{'as scored':>11}{'notable dropped':>17}{'all unmatched drop':>21}")
    for a in arms:
        base, dropn, dropall = [], [], []
        for p in analysis:
            for d in C1_DEPTHS:
                pa, pp = cell(a, p, d), cell("P", p, d)
                if not pa or not pp:
                    continue
                base.append(statistics.mean(fs(pa)) - statistics.mean(fs(pp)))
                va, vp = fs(pa, notable), fs(pp, notable)
                if va and vp:
                    dropn.append(statistics.mean(va) - statistics.mean(vp))
                ua = [F[MB[str(n)]] for n in pa[1:-1] if MB[str(n)] in matched]
                up = [F[MB[str(n)]] for n in pp[1:-1] if MB[str(n)] in matched]
                if ua and up:
                    dropall.append(statistics.mean(ua) - statistics.mean(up))
        print(f"{a:<7}{statistics.mean(base):>11.3f}{statistics.mean(dropn):>17.3f}"
              f"{statistics.mean(dropall):>21.3f}")

    print("\n== share of DD-C1 cell-mean depression attributable to F=0 interiors ==")
    for a in arms:
        tot = sum(1 for p in analysis for d in C1_DEPTHS if cell(a, p, d)
                  for n in cell(a, p, d)[1:-1])
        zero = sum(1 for p in analysis for d in C1_DEPTHS if cell(a, p, d)
                   for n in cell(a, p, d)[1:-1] if MB[str(n)] not in matched)
        nz = sum(1 for p in analysis for d in C1_DEPTHS if cell(a, p, d)
                 for n in cell(a, p, d)[1:-1] if MB[str(n)] in notable)
        print(f"  {a:<7} interiors {tot:>4}  unmatched(F=0) {zero:>4} "
              f"({100 * zero / tot:5.1f} %)  of which A11-flagged notable {nz}")

    # ---- DD-C2 composition ----
    print("\n== DD-C2 under four pooling choices ==")
    nod = [p for p in analysis if p != "Openzone Bar -> Gjallarhorn"]
    print(f"{'arm':<7}{'as scored':>11}{'pair dropped':>14}{'per-pair med':>14}"
          f"{'both':>8}")
    for a in arms:
        def pooled(d, pairs):
            return [f for p in pairs if cell(a, p, d) for f in fs(cell(a, p, d))]

        def med(d, pairs):
            return statistics.median(pooled(d, pairs))
        as_scored = med(5, analysis) - med(20, analysis)
        dropped = med(5, nod) - med(20, nod)
        pm = lambda d, ps: statistics.median(  # noqa: E731
            [statistics.median(fs(cell(a, p, d))) for p in ps if cell(a, p, d)])
        perpair = pm(5, analysis) - pm(20, analysis)
        both = pm(5, nod) - pm(20, nod)
        print(f"{a:<7}{as_scored:>11.3f}{dropped:>14.3f}{perpair:>14.3f}{both:>8.3f}")

    # ---- DD-C4 hop sets ----
    print("\n== DD-C4 under two readings of 'interior hops' ==")
    offsets, neighbours, scores = (np.asarray(store.offsets),
                                   np.asarray(store.neighbours),
                                   np.asarray(store.scores))

    def sim(u, v):
        row = neighbours[offsets[u]:offsets[u + 1]]
        return float(scores[offsets[u] + int(np.nonzero(row == v)[0][0])])
    med_all, med_int = {}, {}
    for a in arms:
        A_, I_ = [], []
        for p in analysis:
            for d in C1_DEPTHS:
                q = cell(a, p, d)
                if not q:
                    continue
                A_ += [sim(q[i], q[i + 1]) for i in range(len(q) - 1)]
                I_ += [sim(q[i], q[i + 1]) for i in range(1, len(q) - 2)]
        med_all[a], med_int[a] = statistics.median(A_), statistics.median(I_)
    print(f"{'arm':<7}{'all hops':>10}{'drop':>8}{'flag':>6}"
          f"{'interior-only':>15}{'drop':>8}{'flag':>6}")
    for a in arms:
        da, di = med_all["P"] - med_all[a], med_int["P"] - med_int[a]
        print(f"{a:<7}{med_all[a]:>10.3f}{da:>8.3f}{'FLAG' if da > 0.10 else '-':>6}"
              f"{med_int[a]:>15.3f}{di:>8.3f}{'FLAG' if di > 0.10 else '-':>6}")

    # ---- endpoint name resolution ----
    print("\n== endpoint resolution: name -> node id ==")
    by_name: dict[str, int] = {}
    dup = Counter(store.names)
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i
    entries = (V2["analysis_pairs"] + V2["held_out_pairs"])
    amb = []
    for e in entries:
        for role in ("src", "dst"):
            nm = e[role]
            if dup[nm] > 1:
                amb.append((e["pair"], role, nm, dup[nm]))
    print(f"  scored endpoints whose NAME is shared by >1 node: {len(amb)}  {amb}")
    stored_ids = [k for k in entries[0] if "node" in k or k.endswith("_id")]
    print(f"  pairs_v2 entry fields: {sorted(entries[0])}")
    if stored_ids:
        mism = [(e["pair"], k, e[k]) for e in entries for k in stored_ids
                if e[k] != by_name[e[k.split("_")[0]]]]
        print(f"  stored-id vs resolved-id mismatches: {len(mism)} {mism}")

    # ---- guard-G attribution ----
    print("\n== guard-G attribution: which pairs fire, per arm ==")
    for a, w in (("P", 0.0), ("DD-A3", 0.10)):
        cfg = SweepConfig.production().with_(guard_min_intermediary=True)
        if w:
            cfg = cfg.with_(w_known_ramp_pctl=w)
        total = 0
        for p in P["pairs"]:
            src, dst = p.split(" -> ")
            st = {"examined": 0, "floor_active": 0, "guard_fired": 0}
            walk(store, by_name[src], by_name[dst], cfg, ctx, pop,
                 find_path_mirror, Exclusion, KNOWN, st)
            if st["guard_fired"]:
                print(f"  {a:<7} {p:<44} guard fired {st['guard_fired']}/21 depths")
            total += st["guard_fired"]
        print(f"  {a:<7} TOTAL {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
