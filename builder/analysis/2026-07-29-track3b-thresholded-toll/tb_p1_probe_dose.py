"""TB-P1 probe 1 — the §2 dose derivation, the §0 floor row, and the knee boundary.

Read-only. Asserts the artifact sha256 (TB-G3 / DD-G3 discipline).

Answers, from committed data only (`t3_paths.json` P walks on `pairs_v2.json`):

  (1) the knee's set identity: does {pctl <= 0.90} == {pctl < 0.90} on this artifact?
      (TB-P3 removes the "top decile"; the device is zero at pctl <= 0.90.)
  (2) the pctl distribution of P's SCORED interiors in the C1 window, per cell and
      pooled -- the premise §2 takes from PLA-R2 (median ~0.998), which was measured
      on a different pair set.
  (3) the realised toll each w in {0.10, 0.30, 1.00} produces on those interiors, in
      w_hop units, at k = 10 and k = 20 -- per interior and per whole path -- and the
      same quantity for Track 3's device on the same cells, which is the comparison
      §2's "comparable in the currency that matters" claim rests on.
  (4) DD-D4's floor bases and last-live k, recomputed from the artifact.
  (5) adjacency of every pairs_v2 pair (the §0 guard-G row's exposure argument).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p1_probe_dose.py
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
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
T3 = ROOT / "builder" / "analysis" / "2026-07-28-track3-depth-descent"

KNEE = 0.90
W_HOP = 0.02              # ApiConfig default, cited not re-derived
TB_W = (0.10, 0.30, 1.00)
DD_W = (0.01, 0.03, 0.10)
C1_WINDOW = (10, 15, 20)


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}")

    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pctl = ctx.pctl
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    n = len(store.mbids)
    print(f"N = {n:,}  directed CSR entries = {len(store.neighbours):,}\n")

    # ---- (1) knee set identity -------------------------------------------------
    print("== (1) the knee at 0.90: is {pctl <= 0.90} the same set as {pctl < 0.90}? ==")
    eq = int((pctl == KNEE).sum())
    lt = int((pctl < KNEE).sum())
    le = int((pctl <= KNEE).sum())
    below_gap = float(pctl[pctl < KNEE].max())
    above_gap = float(pctl[pctl > KNEE].min())
    print(f"  nodes with pctl exactly 0.90 : {eq}")
    print(f"  pctl <  0.90 : {lt:,} ({100*lt/n:.3f} %)   pctl <= 0.90 : {le:,}")
    print(f"  nearest below 0.90: {below_gap:.10f}   nearest above: {above_gap:.10f}")
    print(f"  smallest positive per-node toll factor (pctl-0.90): {above_gap - KNEE:.3e}")
    # largest tie-block anywhere, and the tie block straddling the knee
    order = np.argsort(pop, kind="stable")
    srt = pop[order]
    _, counts = np.unique(srt, return_counts=True)
    print(f"  largest pop_raw tie block: {counts.max():,} nodes "
          f"(pctl is average-rank, so a block sits at one pctl value)\n")

    # ---- load committed P walks ------------------------------------------------
    paths_doc = json.loads((T3 / "t3_paths.json").read_text(encoding="utf-8"))
    assert paths_doc["artifact_sha256"] == digest
    pairs_doc = json.loads((T3 / "pairs_v2.json").read_text(encoding="utf-8"))
    assert pairs_doc["artifact_sha256"] == digest
    analysis = [e["pair"] for e in pairs_doc["analysis_pairs"]]
    held_out = [e["pair"] for e in pairs_doc["held_out_pairs"]]
    dropped = set(paths_doc["dropped_cells_d7"])
    P = paths_doc["paths"]["P"]

    def cells(pairs, depths):
        for pr in pairs:
            for d in depths:
                if f"{pr}@d{d}" in dropped:
                    continue
                p = P[pr][str(d)]
                if p:
                    yield pr, d, p

    # ---- (2) pctl of P's scored interiors, C1 window ---------------------------
    print("== (2) pctl of production's scored interiors, C1 window, ANALYSIS pairs ==")
    print("   (the premise §2 imports from PLA-R2, which was measured on Track 2's set)")
    print(f"   {'pair':<44}{'d':>3}{'n':>4}{'medPctl':>9}{'meanPctl':>10}"
          f"{'>knee':>7}{'medAbove':>10}")
    pooled_all, pooled_above, per_cell_med = [], [], []
    n_int_tot = 0
    for pr, d, p in cells(analysis, C1_WINDOW):
        iv = [float(pctl[v]) for v in p[1:-1]]
        above = [x for x in iv if x > KNEE]
        pooled_all += iv
        pooled_above += above
        per_cell_med.append(statistics.median(iv))
        n_int_tot += len(iv)
        print(f"   {pr[:43]:<44}{d:>3}{len(iv):>4}{statistics.median(iv):9.4f}"
              f"{statistics.mean(iv):10.4f}{len(above):>7}"
              f"{(statistics.median(above) if above else float('nan')):10.4f}")
    print(f"\n   pooled interiors n={len(pooled_all)}   median pctl "
          f"{statistics.median(pooled_all):.4f}   mean {statistics.mean(pooled_all):.4f}")
    print(f"   share above the knee: {len(pooled_above)}/{len(pooled_all)} = "
          f"{100*len(pooled_above)/len(pooled_all):.1f} %")
    print(f"   pooled ABOVE-knee median pctl {statistics.median(pooled_above):.4f}  "
          f"mean {statistics.mean(pooled_above):.4f}  "
          f"min {min(pooled_above):.4f}  max {max(pooled_above):.4f}")
    qs = np.quantile(np.array(pooled_above), [0.05, 0.25, 0.5, 0.75, 0.95])
    print(f"   above-knee pctl quantiles 5/25/50/75/95: "
          + "  ".join(f"{q:.4f}" for q in qs))
    print(f"   mean of per-cell medians (all interiors): "
          f"{statistics.mean(per_cell_med):.4f}\n")

    # same, on Track 2's own pair set, to locate PLA-R2's figure
    print("   for contrast, PLA-R2's own pair set (Track 2 paths.json, arm P, d>=10):")
    t2 = ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer" / "paths.json"
    t2doc = json.loads(t2.read_text(encoding="utf-8"))
    t2P = t2doc["paths"]["P"]
    t2pool = [float(pctl[v]) for pr in t2P for d in C1_WINDOW
              if t2P[pr].get(str(d)) for v in t2P[pr][str(d)][1:-1]]
    if t2pool:
        t2above = [x for x in t2pool if x > KNEE]
        print(f"     n={len(t2pool)}  median {statistics.median(t2pool):.4f}  "
              f"above-knee {len(t2above)}/{len(t2pool)} = "
              f"{100*len(t2above)/len(t2pool):.1f} %  "
              f"above-knee median {statistics.median(t2above):.4f}\n")

    # ---- (3) realised toll ------------------------------------------------------
    print("== (3) realised toll in w_hop units on production's own C1-window interiors ==")
    print("   TB device: w*k*max(0, pctl-0.90).  Track 3 device: w*k*pctl.")
    for k in (10, 20):
        print(f"\n   -- at k = {k} --")
        print(f"   {'arm':<8}{'w':>6}  per ABOVE-KNEE interior (w_hop units)"
              f"        per WHOLE PATH")
        print(f"   {'':<8}{'':>6}  {'p5':>7}{'p25':>7}{'med':>7}{'p75':>7}{'p95':>7}"
              f"{'max':>7}   {'med':>9}{'mean':>9}")
        for lbl, w in zip(("TB-A1", "TB-A2", "TB-A3"), TB_W):
            per = np.array([w * k * (x - KNEE) / W_HOP for x in pooled_above])
            path_tolls = []
            for pr, d, p in cells(analysis, C1_WINDOW):
                path_tolls.append(sum(w * k * max(0.0, float(pctl[v]) - KNEE)
                                      for v in p[1:-1]) / W_HOP)
            q = np.quantile(per, [0.05, 0.25, 0.5, 0.75, 0.95])
            print(f"   {lbl:<8}{w:>6.2f}  " + "".join(f"{x:7.1f}" for x in q)
                  + f"{per.max():7.1f}   {statistics.median(path_tolls):9.1f}"
                    f"{statistics.mean(path_tolls):9.1f}")
        print(f"   {'-'*70}")
        print(f"   {'arm':<8}{'w':>6}  per INTERIOR (all interiors are charged)"
              f"          per WHOLE PATH")
        for lbl, w in zip(("DD-A1", "DD-A2", "DD-A3"), DD_W):
            per = np.array([w * k * x / W_HOP for x in pooled_all])
            path_tolls = []
            for pr, d, p in cells(analysis, C1_WINDOW):
                path_tolls.append(sum(w * k * float(pctl[v]) for v in p[1:-1]) / W_HOP)
            q = np.quantile(per, [0.05, 0.25, 0.5, 0.75, 0.95])
            print(f"   {lbl:<8}{w:>6.2f}  " + "".join(f"{x:7.1f}" for x in q)
                  + f"{per.max():7.1f}   {statistics.median(path_tolls):9.1f}"
                    f"{statistics.mean(path_tolls):9.1f}")

    # the document's own arithmetic, checked at its own premise and at the measured one
    print("\n   §2's claim, checked at both premises (k = 10, per interior, w_hop units):")
    for prem, lbl in ((0.998, "§2's premise (PLA-R2, other pair set)"),
                      (statistics.median(pooled_above), "measured, above-knee median"),
                      (statistics.median(pooled_all), "measured, all-interior median")):
        row = "  ".join(f"{w}: {w*10*max(0.0, prem-KNEE)/W_HOP:5.1f}x" for w in TB_W)
        print(f"     pctl {prem:.4f}  {row}   [{lbl}]")

    # ---- (4) floor bases (DD-D4) -----------------------------------------------
    print("\n== (4) DD-D4 recomputed: floor base = min(pop_raw) over endpoints, "
          "relax 0.15/known ==")
    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i
    bases = []
    for grp, key in (("analysis", "analysis_pairs"), ("held_out", "held_out_pairs")):
        for e in pairs_doc[key]:
            s, t = by_name[e["src"]], by_name[e["dst"]]
            base = min(float(pop[s]), float(pop[t]))
            last = max([k for k in range(0, 21) if base - 0.15 * k > 0.0], default=-1)
            bases.append(base)
            print(f"   {e['pair'][:47]:<49} base {base:.4f}  alive for k <= {last}")
    print(f"   scored-set floor bases: min {min(bases):.4f}  max {max(bases):.4f}")
    print(f"   dead from k = {max([k for k in range(21) if max(bases)-0.15*k > 0])+1} "
          f"on the strongest pair; shallowest scored depth is d5")

    # ---- (5) adjacency ----------------------------------------------------------
    print("\n== (5) adjacency of every pairs_v2 pair (guard-G exposure) ==")
    adj_scored = []
    for grp, key in (("analysis", "analysis_pairs"), ("held_out", "held_out_pairs")):
        for e in pairs_doc[key]:
            s, t = by_name[e["src"]], by_name[e["dst"]]
            nb = {int(v) for v, _ in store.neighbours_of(s)}
            if t in nb:
                adj_scored.append(e["pair"])
    print(f"   scored pairs that are adjacent: {len(adj_scored)} {adj_scored}")
    adj_anchor = []
    for p in pairs_doc["unscored_anchor_pairs"]:
        a, b = p.split(" -> ")
        s, t = by_name[a], by_name[b]
        if t in {int(v) for v, _ in store.neighbours_of(s)}:
            adj_anchor.append(p)
    print(f"   unscored anchors that are adjacent: {len(adj_anchor)} {adj_anchor}")

    # ---- (6) TB-C2 well-definedness --------------------------------------------
    print("\n== (6) TB-C2 pooling on this pair set (d5 / d20, analysis) ==")
    print(f"   A13 drop recorded in t3_paths.json: {sorted(dropped)}")
    surv = []
    for pr in analysis:
        c5 = P[pr]["5"]
        c20 = P[pr]["20"]
        d5_dropped = f"{pr}@d5" in dropped
        d20_dropped = f"{pr}@d20" in dropped
        ok = c5 and c20 and not d5_dropped and not d20_dropped
        n5 = len(c5) - 2 if c5 else 0
        n20 = len(c20) - 2 if c20 else 0
        print(f"   {pr[:47]:<49} d5 interiors {n5:>3}  d20 interiors {n20:>3}  "
              f"{'KEPT' if ok else 'REMOVED (A13)'}")
        if ok:
            surv.append(pr)
    print(f"   pairs surviving TB-C2's 'present at both depths' rule: {len(surv)}/8")
    print(f"   cells with 0 interiors: "
          f"{sum(1 for pr in analysis for d in (5, 20) if P[pr][str(d)] and len(P[pr][str(d)])==2)}")
    print(f"   cells with 1 interior : "
          f"{sum(1 for pr in analysis for d in (5, 20) if P[pr][str(d)] and len(P[pr][str(d)])==3)}")
    print(f"   held-out pairs (supplementary table): {len(held_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
