"""A0-gate review: is the raw floor arm-invariant, and how large is the d1-d5 asymmetry?

Three questions, all MECHANICAL. Nothing here is scored: no fame proxy is touched, no
C1/C2/C3 statistic is computed. Only floor-term activity, path-level in-graph popularity
exposure, and cell identity between one-knob twins.

Part 1  arithmetic — the relaxed raw floor value per pair per depth, and the depth at
        which it provably reaches zero (`ceil(base_raw / floor_relax_known)`).
Part 2  structural bound — the largest firing rate ANY arm could show at each depth,
        being the fraction of directed CSR edges whose head sits below that depth's
        floor. Arm-independent, so it bounds the asymmetry from above.
Part 3  routed — three arm families, each as a floor-on / floor-off one-knob pair:
          P     / A0     : production weights            (w_jump 1.0 raw, w_sim 3.0)
          A6r   / A6     : joint magnitude, raw          (w_jump 0.3 raw, w_sim 1.5)
          Xr    / X      : the pre-registered corner     (w_jump 0,       w_sim 1.5)
        Each walks the scripted policy independently (all-`known`, victim = most-popular
        interior by in-graph popularity, ties -> lowest node id), guard G ON in every arm.
        Recorded per (arm, pair, depth): relaxations examined, relaxations with a
        non-zero floor term, the chosen path, its interiors below the floor, the floor
        cost the path actually pays, and min/median interior raw popularity.

Run from `api/`:
    PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \
        ../builder/analysis/2026-07-23-track2-a0-review/floor_asymmetry.py
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
OUT = Path(__file__).resolve().parent

MAX_DEPTH = 20
RELAX_KNOWN = 0.15        # ApiConfig.floor_relax_known — cited, not re-derived
RELAX_KNOWN_PCTL = 0.05   # pre-registration A2, NOT ApiConfig


def walk(store, src, dst, cfg, ctx, pop, find_path_mirror, Exclusion, KNOWN, base_floor):
    """Scripted all-`known` walk. Returns per-depth records."""
    excludes: list = []
    recs = []
    for d in range(MAX_DEPTH + 1):
        stats = {"examined": 0, "floor_active": 0}
        path = find_path_mirror(store, src, dst, excludes, cfg, ctx, stats)
        floor_d = max(0.0, base_floor - RELAX_KNOWN * d)
        rec = {
            "depth": d,
            "examined": stats["examined"],
            "floor_active": stats["floor_active"],
            "floor_value": floor_d,
            "path": path,
        }
        if path is None:
            recs.append(rec)
            break
        interior = path[1:-1]
        rec["n_interior"] = len(interior)
        if interior:
            ip = pop[interior]
            rec["min_interior_pop"] = float(ip.min())
            rec["median_interior_pop"] = float(np.median(ip))
            short = np.maximum(0.0, floor_d - ip)
            rec["n_below_floor"] = int((short > 0).sum())
            rec["max_shortfall"] = float(short.max())
            # floor cost the path actually pays: the term is charged on every edge INTO
            # a node, so every node after the source, target included.
            tail = pop[path[1:]]
            rec["path_floor_cost"] = float(np.maximum(0.0, floor_d - tail).sum())
        recs.append(rec)
        if not interior:
            break
        victim = min(interior, key=lambda v: (-pop[v], v))
        excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
    return recs


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from verify_mirror import ANALYSIS_PAIRS, HELD_OUT_PAIRS

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = np.asarray(ctx.pctl, dtype=np.float64)
    n = len(store.mbids)
    print(f"N={n}  E={len(store.neighbours)}  jump_scale_pctl={ctx.jump_scale_pctl:.6f}\n")

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    PAIRS = list(ANALYSIS_PAIRS) + list(HELD_OUT_PAIRS)

    # ---------------- Part 1: arithmetic ----------------
    print("=== PART 1 — relaxed raw floor value by depth (arm-invariant given depth) ===")
    print(f"{'pair':<38} {'base_raw':>9} {'d5':>7} {'d6':>7} {'d7':>7} {'zero@':>6}"
          f" {'base_pctl':>10} {'pctl@d5':>8} {'pctl@d20':>9}")
    part1 = []
    for a, b in PAIRS:
        ia, ib = by_name[a], by_name[b]
        base = min(float(pop[ia]), float(pop[ib]))
        base_p = min(float(pctl[ia]), float(pctl[ib]))
        zero_at = int(np.ceil(base / RELAX_KNOWN))
        f = {d: max(0.0, base - RELAX_KNOWN * d) for d in range(0, 9)}
        p5 = max(0.0, base_p - RELAX_KNOWN_PCTL * 5)
        p20 = max(0.0, base_p - RELAX_KNOWN_PCTL * 20)
        print(f"{a + ' -> ' + b:<38} {base:9.4f} {f[5]:7.4f} {f[6]:7.4f} {f[7]:7.4f}"
              f" {zero_at:6d} {base_p:10.4f} {p5:8.4f} {p20:9.4f}")
        part1.append({"pair": f"{a} -> {b}", "base_raw": base, "zero_at": zero_at,
                      "floor_by_depth": f, "base_pctl": base_p,
                      "pctl_floor_d5": p5, "pctl_floor_d20": p20})
    print(f"\nmax over pairs of ceil(base_raw/{RELAX_KNOWN}) = "
          f"{max(p['zero_at'] for p in part1)}   "
          f"(pairs with floor still > 0 at d6: "
          f"{sum(1 for p in part1 if p['floor_by_depth'][6] > 0)}/{len(part1)})")

    # ---------------- Part 2: structural upper bound ----------------
    print("\n=== PART 2 — arm-independent upper bound on floor-term firing ===")
    src_arr = np.repeat(np.arange(n, dtype=np.int64), np.diff(store.offsets))
    dst_arr = np.asarray(store.neighbours, dtype=np.int64)
    head_pop = pop[dst_arr]
    E = len(dst_arr)
    print("fraction of ALL directed edges whose head sits below the floor "
          "(= max possible firing rate for ANY arm at that depth)")
    print(f"{'pair':<38} " + " ".join(f"{'d'+str(d):>8}" for d in range(0, 8)))
    part2 = []
    for rec in part1:
        row = []
        for d in range(0, 8):
            fv = rec["floor_by_depth"][d]
            row.append(float((head_pop < fv).sum()) / E * 100.0)
        print(f"{rec['pair']:<38} " + " ".join(f"{v:8.3f}" for v in row))
        part2.append({"pair": rec["pair"], "max_firing_pct_by_depth": row})
    print("(units: % of the 898,006 directed CSR entries)")

    # ---------------- Part 3: routed arms ----------------
    prod = SweepConfig.production().with_(guard_min_intermediary=True)
    ARMS = {
        # family, floor state
        "P":   prod,
        "A0":  prod.with_(floor_mode="off", w_floor=0.0),
        "A6r": prod.with_(w_jump=0.3, w_sim=1.5),
        "A6":  prod.with_(w_jump=0.3, w_sim=1.5, floor_mode="off", w_floor=0.0),
        "Xr":  prod.with_(jump_currency="pctl", w_jump=0.0, w_sim=1.5),
        "X":   prod.with_(jump_currency="pctl", w_jump=0.0, w_sim=1.5,
                          floor_mode="off", w_floor=0.0),
    }
    FAMILIES = [("P", "A0"), ("A6r", "A6"), ("Xr", "X")]

    print("\n=== PART 3 — routed walks, guard G ON in every arm ===")
    results: dict[str, dict[str, list]] = {k: {} for k in ARMS}
    for a, b in PAIRS:
        ia, ib = by_name[a], by_name[b]
        base = min(float(pop[ia]), float(pop[ib]))
        for name, cfg in ARMS.items():
            results[name][f"{a} -> {b}"] = walk(
                store, ia, ib, cfg, ctx, pop, find_path_mirror,
                Exclusion, KNOWN, base)

    print("\n-- 3a. floor-term firing rate by depth, pooled over 12 pairs "
          "(floor-ON arms only) --")
    print(f"{'depth':>5} " + " ".join(f"{a:>26}" for a, _ in FAMILIES))
    for d in range(0, 9):
        cells = []
        for on, _ in FAMILIES:
            ex = fa = 0
            for pr in results[on].values():
                for r in pr:
                    if r["depth"] == d:
                        ex += r["examined"]
                        fa += r["floor_active"]
            pct = 100.0 * fa / max(1, ex)
            cells.append(f"{fa:>9,}/{ex:>9,} {pct:6.3f}%")
        print(f"{'d'+str(d):>5} " + " ".join(f"{c:>26}" for c in cells))

    print("\n-- 3b. one-knob floor contrast: cells where floor-ON != floor-OFF --")
    print(f"{'depth':>5} " + " ".join(f"{on+'/'+off:>14}" for on, off in FAMILIES))
    for d in range(0, 9):
        cells = []
        for on, off in FAMILIES:
            diff = tot = 0
            for key in results[on]:
                ron = [r for r in results[on][key] if r["depth"] == d]
                roff = [r for r in results[off][key] if r["depth"] == d]
                if ron and roff:
                    tot += 1
                    if ron[0]["path"] != roff[0]["path"]:
                        diff += 1
            cells.append(f"{diff:>5}/{tot:<8}")
        print(f"{'d'+str(d):>5} " + " ".join(f"{c:>14}" for c in cells))

    print("\n-- 3c. path-level floor exposure, pooled over 12 pairs --")
    print(f"{'arm':<5}{'depth':>6} {'cells':>6} {'interiors':>10} {'below floor':>12}"
          f" {'max shortfall':>14} {'mean path floor cost':>21} {'min int pop':>12}")
    part3c = []
    for name in ARMS:
        for d in range(0, 8):
            rows = [r for pr in results[name].values() for r in pr
                    if r["depth"] == d and r.get("path")]
            if not rows:
                continue
            ints = sum(r["n_interior"] for r in rows)
            below = sum(r.get("n_below_floor", 0) for r in rows)
            mx = max((r.get("max_shortfall", 0.0) for r in rows), default=0.0)
            cost = float(np.mean([r.get("path_floor_cost", 0.0) for r in rows]))
            mn = min((r.get("min_interior_pop", 1.0) for r in rows), default=float("nan"))
            print(f"{name:<5}{'d'+str(d):>6} {len(rows):>6} {ints:>10} {below:>12}"
                  f" {mx:14.4f} {cost:21.4f} {mn:12.4f}")
            part3c.append({"arm": name, "depth": d, "cells": len(rows),
                           "interiors": ints, "below_floor": below,
                           "max_shortfall": mx, "mean_path_floor_cost": cost,
                           "min_interior_pop": mn})
        print()

    print("-- 3d. the d0 cells where the floor changes the path, per family --")
    for on, off in FAMILIES:
        for key in results[on]:
            ron = [r for r in results[on][key] if r["depth"] == 0][0]
            roff = [r for r in results[off][key] if r["depth"] == 0][0]
            if ron["path"] != roff["path"]:
                nm = lambda ns: " -> ".join(  # noqa: E731
                    f"{store.names[i]} ({pop[i]:.4f})" for i in ns)
                print(f"  [{on} vs {off}] {key}  floor={ron['floor_value']:.4f}")
                print(f"      {on:<4}: {nm(ron['path'])}")
                print(f"      {off:<4}: {nm(roff['path'])}")

    print("\n-- 3e. per-pair firing at d5/d6/d7, floor-ON arms (Q1's threshold test) --")
    print(f"{'pair':<38} " + " ".join(f"{on+' d'+str(d):>12}"
                                      for on, _ in FAMILIES for d in (5, 6, 7)))
    for key in results["P"]:
        cells = []
        for on, _ in FAMILIES:
            for d in (5, 6, 7):
                rr = [r for r in results[on][key] if r["depth"] == d]
                cells.append(f"{rr[0]['floor_active']:>12,}" if rr else f"{'-':>12}")
        print(f"{key:<38} " + " ".join(cells))

    (OUT / "raw_results.json").write_text(json.dumps(
        {"artifact_sha256": digest, "part1": part1, "part2": part2, "part3c": part3c,
         "arms": {k: {kk: [{a: b for a, b in r.items()} for r in v]
                      for kk, v in vv.items()} for k, vv in results.items()}},
        indent=1), encoding="utf-8")
    print(f"\nwrote {OUT / 'raw_results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
