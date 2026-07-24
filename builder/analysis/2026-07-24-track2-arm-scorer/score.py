"""C1-C6 over routed paths, plus the guards and diagnostics. Pre-registration §2.2.

Reads `paths.json` (from `run_arms.py`) and `fame.json` (from `fame.py`). Deterministic,
offline, and re-runnable: no network, so a criterion bug costs a re-score and never a
re-route or a re-fetch.

Criteria, and where each is defined:
  C1  relative depth contrast vs P, d >= 10        §2.2 -- mean dF <= -1.0, dF<0 in >= 75%
  C2  absolute reach vs B_unk at d15/d20           §2.2 -- >= 4 of 8 analysis pairs
  C3  within-arm depth gradient (F2)               §2.2 -- median F d20 <= d5 - 0.5
  C4  payload guard                                §2.2 -- mean interiors >= P's mean - 1
  C6  proxy coverage                               §2.2 as amended by A12 -- REPORTED, NOT GATED
  C5  no-regression inspection at d0               §1.5 -- vs BOTH P and A0 (A8); inspected
  C7  dislike/known divergence                     §1.5 -- stage 2 only, needs a dislike walk

Diagnostics that gate nothing:
  F5      sustained confinement across consecutive snapshots
  repeats most-repeated interiors across pairs (Attack 2's only offline proxy)
  track   d0 endpoint-fame tracking (A14a, on WGLL value 9)
  floor   fraction of relaxations carrying a non-zero floor term (PR-A)

**A12: C6 does not gate.** Under A11 an unmatched interior is scored at the fame floor
rather than dropped, so match failure marks the obscurity the sweep exists to reach.
Gating on coverage would cap an arm near 5.6% obscure interiors. It is reported because
it still measures how much of a score rests on the absence assumption.

**A13: guard-infeasible cells are already dropped from ALL arms** by `run_arms.py`, so a
None here is absent in every arm and cannot make missingness correlate with arm.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = HERE.parent / "2026-07-24-track2-fame-proxy-wikipedia"

C1_MEAN_MAX = -1.0
C1_FRAC_MIN = 0.75
C2_PAIRS_MIN = 4
C3_DROP_MIN = 0.5
C4_SLACK = 1.0
C1_DEPTHS = (10, 15, 20)
C2_DEPTHS = (15, 20)


def b_unk() -> float:
    """B_unk in fame units, read from the committed proxy score rather than restated."""
    s = json.loads((PROXY / "score.json").read_text(encoding="utf-8"))
    return math.log10(1.0 + int(s["b_unk"]["threshold"]))


def interiors(path, names) -> list[str]:
    return [names[str(n)] for n in path[1:-1]] if path else []


def cell_median(path, names, F) -> float | None:
    ints = interiors(path, names)
    return statistics.median([F[n] for n in ints]) if ints else None


def score_arm(arm, doc, F, analysis_pairs, B):
    names, paths = doc["node_names"], doc["paths"]
    P, A = paths["P"], paths[arm]

    # --- C1: paired per cell against P, analysis set, d >= 10 -------------------
    deltas = []
    for pair in analysis_pairs:
        for d in C1_DEPTHS:
            mp = cell_median(P[pair][str(d)], names, F)
            ma = cell_median(A[pair][str(d)], names, F)
            if mp is not None and ma is not None:
                deltas.append(ma - mp)
    c1_mean = statistics.mean(deltas) if deltas else float("nan")
    c1_frac = (sum(1 for x in deltas if x < 0) / len(deltas)) if deltas else 0.0
    c1 = bool(deltas) and c1_mean <= C1_MEAN_MAX and c1_frac >= C1_FRAC_MIN

    # --- C2: absolute reach below the owner-calibrated band ---------------------
    reached = []
    for pair in analysis_pairs:
        hit = any(F[n] < B
                  for d in C2_DEPTHS
                  for n in interiors(A[pair][str(d)], names))
        if hit:
            reached.append(pair)
    c2 = len(reached) >= C2_PAIRS_MIN

    # --- C3: within-arm gradient, pooled across pairs ---------------------------
    def pooled(d):
        vals = [F[n] for pair in analysis_pairs for n in interiors(A[pair][str(d)], names)]
        return statistics.median(vals) if vals else None
    m5, m20 = pooled(5), pooled(20)
    c3_drop = (m5 - m20) if (m5 is not None and m20 is not None) else float("nan")
    c3 = c3_drop >= C3_DROP_MIN

    # --- C4: payload -- fewer-but-obscurer is not a win (WGLL value 2) ----------
    def mean_count(src):
        c = [len(interiors(src[pair][str(d)], names))
             for pair in analysis_pairs for d in C1_DEPTHS if src[pair][str(d)]]
        return statistics.mean(c) if c else 0.0
    c4_arm, c4_p = mean_count(A), mean_count(P)
    c4 = c4_arm >= c4_p - C4_SLACK

    # --- C6: REPORTED, not gated (A12) -----------------------------------------
    distinct = {n for pair in analysis_pairs for d in C1_DEPTHS
                for n in interiors(A[pair][str(d)], names)}
    cov = (sum(1 for n in distinct if F[n] > 0.0) / len(distinct)) if distinct else 0.0

    # --- F5: sustained confinement (>= 3 consecutive snapshots changing only the
    #     same node group). A single local deviation is expected (WGLL value 7).
    confined = []
    snaps = [str(d) for d in doc["snapshots"]]
    for pair in analysis_pairs:
        run, groups = 0, []
        for a, b in zip(snaps, snaps[1:]):
            pa, pb = A[pair][a], A[pair][b]
            if not pa or not pb:
                run = 0
                continue
            changed = set(interiors(pa, names)) ^ set(interiors(pb, names))
            if changed and groups and changed <= groups[-1]:
                run += 1
            else:
                run = 0
            groups.append(changed | (groups[-1] if groups else set()))
            if run >= 3:
                confined.append(pair)
                break
    return {
        "C1": {"pass": c1, "mean_dF": c1_mean, "frac_negative": c1_frac, "n_cells": len(deltas)},
        "C2": {"pass": c2, "pairs_reached": len(reached), "of": len(analysis_pairs),
               "which": reached},
        "C3": {"pass": c3, "drop_d5_to_d20": c3_drop},
        "C4": {"pass": c4, "mean_interiors": c4_arm, "P_mean": c4_p},
        "C6_reported_not_gated": {"coverage": cov, "distinct_interiors": len(distinct),
                                  "gap_vs_P_points": None},
        "F5_confinement": sorted(confined),
    }


def endpoint_tracking(arm, doc, F, pairs):
    """A14a / WGLL value 9: does d0 interior fame track the endpoints' fame?

    Weak by construction -- the pair set is famous-heavy, so there is little range. Kept
    honest by reporting the per-pair values rather than only a correlation.
    """
    names, A = doc["node_names"], doc["paths"][arm]
    rows = []
    for pair in pairs:
        p0 = A[pair]["0"]
        if not p0:
            continue
        ends = [names[str(p0[0])], names[str(p0[-1])]]
        ints = interiors(p0, names)
        if not ints:
            continue
        rows.append({"pair": pair,
                     "endpoint_mean_F": statistics.mean([F[e] for e in ends]),
                     "d0_interior_median_F": statistics.median([F[n] for n in ints])})
    if len(rows) < 3:
        return {"rows": rows, "correlation": None}
    xs = [r["endpoint_mean_F"] for r in rows]
    ys = [r["d0_interior_median_F"] for r in rows]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return {"rows": rows, "correlation": (num / den) if den else None}


def repeated_interiors(arm, doc, pairs, top=8):
    """Attack 2's only offline proxy: interiors recurring across UNRELATED pairs.

    A configuration whose top interiors recur across pairs with nothing in common is
    routing everything into one corner, which C1-C3 can all pass while every journey ends
    in the same place.
    """
    names, A = doc["node_names"], doc["paths"][arm]
    seen: dict[str, set[str]] = {}
    for pair in pairs:
        for d in doc["snapshots"]:
            for n in interiors(A[pair][str(d)], names):
                seen.setdefault(n, set()).add(pair)
    ranked = sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return [{"artist": n, "n_pairs": len(ps)} for n, ps in ranked[:top] if len(ps) > 1]


def d0_regression(arm, doc, pairs):
    """C5: d0 node overlap against BOTH P and A0 (amendment A8), listed for inspection."""
    names, paths = doc["node_names"], doc["paths"]
    out = []
    for pair in pairs:
        a = paths[arm][pair]["0"]
        for ref in ("P", "A0"):
            if ref not in paths or ref == arm:
                continue
            r = paths[ref][pair]["0"]
            if not a or not r:
                continue
            sa, sr = set(interiors(a, names)), set(interiors(r, names))
            if sa != sr:
                out.append({"pair": pair, "vs": ref,
                            "overlap": len(sa & sr) / len(sa | sr) if (sa | sr) else 1.0,
                            "arm_path": [names[str(n)] for n in a],
                            "ref_path": [names[str(n)] for n in r]})
    return out


def choose_W(results, eligible):
    """Rule R1, pre-registered in §1.4 and applied to data, never to taste.

    The factorial cell with the largest primary contrast that does not violate C4; ties ->
    fewer changed columns from A0; if no cell moves C1 in the right direction, W := A7 so
    the attachment arms still get tested.
    """
    changed_cols = {"A0": 0, "A1": 1, "A2": 1, "A3": 1, "A4": 2, "A5": 2, "A6": 2, "A7": 3}
    viable = [a for a in eligible
              if a in results and results[a]["C4"]["pass"]
              and results[a]["C1"]["mean_dF"] < 0]
    if not viable:
        return "A7", "no cell moved C1 in the right direction; R1's fallback applies"
    best = min(viable, key=lambda a: (results[a]["C1"]["mean_dF"], changed_cols[a]))
    return best, f"largest C1 contrast among C4-passing cells (mean dF {results[best]['C1']['mean_dF']:.3f})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", default=str(HERE / "paths.json"))
    ap.add_argument("--fame", default=str(HERE / "fame.json"))
    ap.add_argument("--out", default=str(HERE / "scores.json"))
    args = ap.parse_args()

    doc = json.loads(Path(args.paths).read_text(encoding="utf-8"))
    F = json.loads(Path(args.fame).read_text(encoding="utf-8"))["fame"]
    B = b_unk()
    held = set(doc.get("held_out_pairs", []))
    analysis = [p for p in doc["pairs"] if p not in held]

    print(f"B_unk = {B:.3f} fame units   analysis pairs: {len(analysis)}   "
          f"held-out: {len(held)}")
    if doc.get("dropped_cells_d7"):
        print(f"D7: {len(doc['dropped_cells_d7'])} cell(s) dropped from ALL arms uniformly")

    results, extras = {}, {}
    for arm in doc["arms"]:
        results[arm] = score_arm(arm, doc, F, analysis, B)
        extras[arm] = {
            "endpoint_tracking_A14": endpoint_tracking(arm, doc, F, analysis),
            "repeated_interiors": repeated_interiors(arm, doc, analysis),
            "C5_d0_changes": d0_regression(arm, doc, analysis) if arm != "P" else [],
            "floor_active_frac": (doc["arm_stats"][arm]["floor_active"]
                                  / max(1, doc["arm_stats"][arm]["examined"])),
        }
    pcov = results["P"]["C6_reported_not_gated"]["coverage"]
    for arm in results:
        c6 = results[arm]["C6_reported_not_gated"]
        c6["gap_vs_P_points"] = 100.0 * (pcov - c6["coverage"])

    from arms import R1_ELIGIBLE
    W, why = choose_W(results, R1_ELIGIBLE)

    print(f"\n{'arm':<5} {'C1 meandF':>10} {'C1 frac':>8} {'C2':>6} {'C3 drop':>8} "
          f"{'C4 int':>7} {'cov%':>6}  gates")
    for arm in doc["arms"]:
        r = results[arm]
        gates = "".join(g if r[g]["pass"] else g.lower()
                        for g in ("C1", "C2", "C3", "C4")) if arm != "P" else "(baseline)"
        print(f"{arm:<5} {r['C1']['mean_dF']:>10.3f} {r['C1']['frac_negative']:>8.2f} "
              f"{r['C2']['pairs_reached']:>4}/{r['C2']['of']} {r['C3']['drop_d5_to_d20']:>8.3f} "
              f"{r['C4']['mean_interiors']:>7.2f} "
              f"{r['C6_reported_not_gated']['coverage']*100:>5.1f}  {gates}")
    print("\nUPPERCASE = passed, lowercase = failed. C6 is reported, not gated (A12).")
    print(f"R1 selects W = {W}  ({why})")

    Path(args.out).write_text(json.dumps(
        {"b_unk_fame_units": B, "analysis_pairs": analysis,
         "W": W, "W_rationale": why, "results": results, "diagnostics": extras},
        indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
