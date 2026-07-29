"""TB-P3 — the ceiling go/no-go gate, in the dd_d6_gap emit/score split (TB-P1 F8).

`--emit`  recomputes TB-P3's ceiling per C1-window cell (importing the machinery from
          `tb_p1_probe_ceiling`, so there is exactly one implementation), ASSERTS each
          cell reproduces the review's committed stats in `tb_p1_ceiling.json`
          (interior count and median pctl exact, base cost to 1e-9), and writes
          `tb_ceiling_paths.json` in the committed `fame.py` paths-doc shape.
          TB-P2a is then: run `../2026-07-24-track2-arm-scorer/fame.py
          --paths tb_ceiling_paths.json --out tb_ceiling_fame.json`.

`--score` reads the gate. Per analysis C1-window cell: mean interior F(ceiling) minus
          mean interior F(P); the GATE statistic is the mean over cells, against
          TB-P3(a)'s pre-committed -1.0 (prereg §5 as amended: a fail is strong
          evidence, not proof — TB-P1 F3). The cell-median variant is reported beside.
          TB-G4 half: asserts no scored interior is blank-named and reports the A11
          `potentially_notable_unmatched` count over ceiling interiors.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p3_ceiling.py --emit
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-24-track2-arm-scorer/fame.py \
        --paths <this dir>/tb_ceiling_paths.json --out <this dir>/tb_ceiling_fame.json
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p3_ceiling.py --score
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
T3 = ROOT / "builder" / "analysis" / "2026-07-28-track3-depth-descent"

C1_WINDOW = (10, 15, 20)
GATE_MAX = -1.0  # TB-P3(a), prereg §5


def emit() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"  # TB-G3
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import walk
    from tb_p1_probe_ceiling import KNEE, base_cost, dijkstra, med_pctl

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pctl = ctx.pctl
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    cfg = SweepConfig.production().with_(guard_min_intermediary=True)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prv = by_name.get(nm)
        if prv is None or pop[i] > pop[prv]:
            by_name[nm] = i

    pairs_doc = json.loads((T3 / "pairs_v2.json").read_text(encoding="utf-8"))
    assert pairs_doc["artifact_sha256"] == digest
    entries = [dict(e, split="analysis") for e in pairs_doc["analysis_pairs"]]
    entries += [dict(e, split="held_out") for e in pairs_doc["held_out_pairs"]]

    committed = {(c["pair"], c["depth"]): c
                 for c in json.loads((HERE / "tb_p1_ceiling.json").read_text(
                     encoding="utf-8"))["cells"] if c["state"] == "ok"}
    dropped = set(json.loads((T3 / "t3_paths.json").read_text(encoding="utf-8"))
                  ["dropped_cells_d7"])

    below = pctl < KNEE
    p_paths: dict[str, dict[str, list[int]]] = {}
    c_paths: dict[str, dict[str, list[int]]] = {}
    splits: dict[str, str] = {}
    checked = 0
    for e in entries:
        src, dst = by_name[e["src"]], by_name[e["dst"]]
        stats = {"examined": 0, "floor_active": 0, "guard_fired": 0}
        paths = walk(store, src, dst, cfg, ctx, pop, find_path_mirror,
                     Exclusion, KNOWN, stats)
        victims: list[int] = []
        for p in paths:
            if p is None or not p[1:-1]:
                break
            victims.append(min(p[1:-1], key=lambda v: (-pop[v], v)))

        splits[e["pair"]] = e["split"]
        for d in C1_WINDOW:
            key = f"{e['pair']}@d{d}"
            p = paths[d]
            if p is None or key in dropped:
                continue
            hard = set(victims[:d]) - {src, dst}
            allowed = below.copy()
            allowed[src] = allowed[dst] = True
            ceil = dijkstra(store, pctl, pop, src, dst, allowed, hard, 0.0)
            assert ceil is not None, f"ceiling vanished at {key} (DD-P1 says it exists)"
            assert all(float(pctl[v]) < KNEE for v in ceil[1:-1])

            # Cross-check against the review's committed per-cell stats (TB-P1 F2).
            c = committed[(e["pair"], d)]
            assert len(ceil) - 2 == c["ceil_int"], f"{key}: interior count moved"
            assert med_pctl(pctl, ceil) == c["ceil_med"], f"{key}: median pctl moved"
            assert abs(base_cost(store, pop, ceil) - c["ceil_base"]) < 1e-9, key
            assert len(p) - 2 == c["p_int"], f"{key}: P moved"
            checked += 1

            p_paths.setdefault(e["pair"], {})[str(d)] = p
            c_paths.setdefault(e["pair"], {})[str(d)] = ceil

    print(f"cross-check: {checked} cells reproduce tb_p1_ceiling.json exactly")

    seen = {n for by_pair in (p_paths, c_paths) for by_d in by_pair.values()
            for path in by_d.values() for n in path}
    out = {
        "artifact_sha256": digest,
        "note": "TB-P3 ceiling paths for TB-P2a fame resolution; shape = fame.py paths-doc",
        "splits": splits,
        "paths": {"P": p_paths, "CEIL": c_paths},
        "node_names": {str(n): store.names[n] for n in sorted(seen)},
        "node_mbids": {str(n): store.mbids[n] for n in sorted(seen)},
    }
    (HERE / "tb_ceiling_paths.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {HERE / 'tb_ceiling_paths.json'}  ({len(seen)} distinct nodes)")
    return 0


def score() -> int:
    doc = json.loads((HERE / "tb_ceiling_paths.json").read_text(encoding="utf-8"))
    assert doc["artifact_sha256"] == EXPECT
    fame_doc = json.loads((HERE / "tb_ceiling_fame.json").read_text(encoding="utf-8"))
    F = fame_doc["fame"]
    names, mbids = doc["node_names"], doc["node_mbids"]
    flagged = set(fame_doc["potentially_notable_unmatched"])

    # TB-G4 half: no scored interior may be blank-named.
    for arm in ("P", "CEIL"):
        for pair, by_d in doc["paths"][arm].items():
            for d, path in by_d.items():
                for n in path[1:-1]:
                    assert names[str(n)].strip(), f"blank-named interior {n} in {arm} {pair}@d{d}"
    print("TB-G4 blank-name assertion over all scored interiors: PASS")

    def cell_stats(path):
        fs = [F[mbids[str(n)]] for n in path[1:-1]]
        return statistics.mean(fs), statistics.median(fs)

    deltas_mean, deltas_median, rows = [], [], []
    n_flagged = 0
    for pair, by_d in doc["paths"]["CEIL"].items():
        if doc["splits"][pair] != "analysis":
            continue
        for d, ceil in sorted(by_d.items(), key=lambda kv: int(kv[0])):
            p = doc["paths"]["P"][pair][d]
            cm, cmed = cell_stats(ceil)
            pm, pmed = cell_stats(p)
            deltas_mean.append(cm - pm)
            deltas_median.append(cmed - pmed)
            n_flagged += sum(1 for n in ceil[1:-1] if mbids[str(n)] in flagged)
            rows.append((pair, int(d), cm - pm, cmed - pmed))

    print(f"\nTB-P3(a) — ceiling fame gap vs P, analysis C1-window ({len(rows)} cells)")
    print(f"{'pair':<42}{'d':>3}{'d(meanF)':>10}{'d(medF)':>10}")
    for pair, d, dm, dmed in rows:
        print(f"{pair[:41]:<42}{d:>3}{dm:>10.3f}{dmed:>10.3f}")

    gate = statistics.mean(deltas_mean)
    med_variant = statistics.mean(deltas_median)
    print(f"\n  GATE statistic (mean over cells of mean-interior-F gap): {gate:+.3f}")
    print(f"  cell-median variant (reported beside, gates nothing):     {med_variant:+.3f}")
    print(f"  cells clearing -1.0 individually: "
          f"{sum(1 for x in deltas_mean if x <= GATE_MAX)}/{len(deltas_mean)}")
    print(f"  A11 potentially-notable-unmatched ceiling interiors: {n_flagged} "
          f"(reported per TB-G4; guard read at TB-C1(i) if arms run)")
    verdict = "PASS — arms may run" if gate <= GATE_MAX else "FAIL — TB-R3, arms are not run"
    print(f"\n  TB-P3(a) GATE vs {GATE_MAX}: {verdict}")

    (HERE / "tb_p3_gate.json").write_text(json.dumps({
        "artifact_sha256": EXPECT,
        "gate_statistic_mean_of_cell_mean_gap": gate,
        "variant_mean_of_cell_median_gap": med_variant,
        "threshold": GATE_MAX,
        "pass": gate <= GATE_MAX,
        "cells": [{"pair": p, "depth": d, "d_mean_F": dm, "d_median_F": dmed}
                  for p, d, dm, dmed in rows],
        "a11_flagged_ceiling_interiors": n_flagged,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {HERE / 'tb_p3_gate.json'}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true")
    g.add_argument("--score", action="store_true")
    args = ap.parse_args()
    raise SystemExit(emit() if args.emit else score())
