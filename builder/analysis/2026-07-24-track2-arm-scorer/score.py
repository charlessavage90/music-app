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
C3_DEPTHS = (5, 20)
# Every depth some criterion reads. The blank-name assertion below is scoped to these:
# a blank interior at an unscored depth cannot bias any statistic.
SCORED_DEPTHS = tuple(sorted(set(C1_DEPTHS) | set(C2_DEPTHS) | set(C3_DEPTHS)))


def blank_scored_cells(doc) -> dict[str, list[str]]:
    """Cells whose scored interiors include a blank-named node. P8b F8's assertion.

    **Why a CELL and not a NODE.** The tempting fix is to drop the blank node from the
    statistic. That is silently directional: a blank name resolves to F = 0, so it drags
    C1's median and C3's d20 median *down* — i.e. toward passing — and it appears
    preferentially in the arms that dive, which is where blank names concentrate (2.7x in
    the bottom popularity decile) and never in P, which has none. Removing the node
    improves whichever arm produced it; removing the CELL from every arm cannot favour
    any of them. That is A13's rule -- missingness must not correlate with arm -- applied
    to a second cause of contamination.

    Returns {cell_key: [arm, ...]}, the arms in which each cell is contaminated. The cell
    is dropped from all of them or from none.
    """
    names = doc["node_names"]
    out: dict[str, list[str]] = {}
    for arm, by_pair in doc["paths"].items():
        for pair, by_depth in by_pair.items():
            for d in SCORED_DEPTHS:
                path = by_depth.get(str(d))
                if not path:
                    continue
                if any(not names[str(n)].strip() for n in path[1:-1]):
                    out.setdefault(f"{pair}@d{d}", []).append(arm)
    return {k: sorted(v) for k, v in sorted(out.items())}


def apply_uniform_blank_drop(doc, blank_cells) -> None:
    """Remove every contaminated cell from EVERY arm, in place. A13's rule, second cause.

    A function rather than four lines inline in `main`, because the property that makes it
    correct — the cell leaves the control as well as the treatment — is the whole point and
    has to be testable. It was inline first, and closeout B3 caught that: mutating it to
    drop per-arm (the directional bug this exists to prevent) left `verify_c2_guards.py`
    passing clean, because the test applied its own loop rather than this code path.
    """
    for cell in blank_cells:
        pair, _, dtag = cell.rpartition("@d")
        for arm in doc["paths"]:
            doc["paths"][arm][pair][dtag] = None


def b_unk() -> float:
    """B_unk in fame units, read from the committed proxy score rather than restated."""
    s = json.loads((PROXY / "score.json").read_text(encoding="utf-8"))
    return math.log10(1.0 + int(s["b_unk"]["threshold"]))


def interiors(path, keys) -> list[str]:
    """Interior nodes as fame-table keys (mbids -- P8b F8), never names."""
    return [keys[str(n)] for n in path[1:-1]] if path else []


def cell_median(path, keys, F) -> float | None:
    ints = interiors(path, keys)
    return statistics.median([F[n] for n in ints]) if ints else None


def score_arm(arm, doc, F, analysis_pairs, B, guard):
    """`guard` carries the A11 flags, keyed like F: `notable` and `nameless` mbid sets."""
    keys, paths = doc["node_mbids"], doc["paths"]
    P, A = paths["P"], paths[arm]

    # --- C1: paired per cell against P, analysis set, d >= 10 -------------------
    deltas = []
    for pair in analysis_pairs:
        for d in C1_DEPTHS:
            mp = cell_median(P[pair][str(d)], keys, F)
            ma = cell_median(A[pair][str(d)], keys, F)
            if mp is not None and ma is not None:
                deltas.append(ma - mp)
    c1_mean = statistics.mean(deltas) if deltas else float("nan")
    c1_frac = (sum(1 for x in deltas if x < 0) / len(deltas)) if deltas else 0.0
    c1 = bool(deltas) and c1_mean <= C1_MEAN_MAX and c1_frac >= C1_FRAC_MIN

    # --- C2: absolute reach below the owner-calibrated band ---------------------
    # `potentially_notable` -> COUNTED, and REPORTED (P8b F2). A11 pre-registered
    # unmatched-as-floor with an owner one-glance check, so the flag is an audit hook,
    # not a filter; silently excluding these would change the adopted encoding. What was
    # missing is that nothing read the flag: `fame.py` computes it graph-wide over all
    # names including endpoints, which no criterion scores. Here it is narrowed to the
    # interiors at the C2 depths a pass actually rests on.
    #
    # Blank-named interiors are NOT handled here. They are removed at CELL level from
    # every arm before scoring (`blank_scored_cells`), because a per-criterion node
    # exclusion is directional -- see that function.
    reached, rests_on_notable = [], {}
    for pair in analysis_pairs:
        hits = [n
                for d in C2_DEPTHS
                for n in interiors(A[pair][str(d)], keys)
                if F[n] < B]
        if hits:
            reached.append(pair)
            flagged = sorted({n for n in hits if n in guard["notable"]})
            # Only load-bearing if the flagged ones are the ONLY reason this pair
            # reached: that is the case a glance from the owner could overturn.
            if flagged and len(flagged) == len({*hits}):
                rests_on_notable[pair] = flagged
    c2 = len(reached) >= C2_PAIRS_MIN

    # --- C3: within-arm gradient, pooled across pairs ---------------------------
    def pooled(d):
        vals = [F[n] for pair in analysis_pairs for n in interiors(A[pair][str(d)], keys)]
        return statistics.median(vals) if vals else None
    m5, m20 = pooled(5), pooled(20)
    c3_drop = (m5 - m20) if (m5 is not None and m20 is not None) else float("nan")
    c3 = c3_drop >= C3_DROP_MIN

    # --- C4: payload -- fewer-but-obscurer is not a win (WGLL value 2) ----------
    def mean_count(src):
        c = [len(interiors(src[pair][str(d)], keys))
             for pair in analysis_pairs for d in C1_DEPTHS if src[pair][str(d)]]
        return statistics.mean(c) if c else 0.0
    c4_arm, c4_p = mean_count(A), mean_count(P)
    c4 = c4_arm >= c4_p - C4_SLACK

    # --- C6: REPORTED, not gated (A12) -----------------------------------------
    distinct = {n for pair in analysis_pairs for d in C1_DEPTHS
                for n in interiors(A[pair][str(d)], keys)}
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
            changed = set(interiors(pa, keys)) ^ set(interiors(pb, keys))
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
               "which": reached,
               # P8b F2: a pass that rests ONLY on flagged-notable interiors is the one
               # the owner's glance could overturn. Empty means the pass is unconditional.
               "rests_only_on_flagged_notable": rests_on_notable},
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
    keys, A = doc["node_mbids"], doc["paths"][arm]
    rows = []
    for pair in pairs:
        p0 = A[pair]["0"]
        if not p0:
            continue
        ends = [keys[str(p0[0])], keys[str(p0[-1])]]
        ints = interiors(p0, keys)
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
    keys, names, A = doc["node_mbids"], doc["node_names"], doc["paths"][arm]
    id_of = {keys[k]: k for k in keys}
    seen: dict[str, set[str]] = {}
    for pair in pairs:
        for d in doc["snapshots"]:
            for n in interiors(A[pair][str(d)], keys):
                seen.setdefault(n, set()).add(pair)
    ranked = sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    # Reported by name for readability, counted by mbid for correctness.
    return [{"artist": names[id_of[n]], "mbid": n, "n_pairs": len(ps)}
            for n, ps in ranked[:top] if len(ps) > 1]


def d0_regression(arm, doc, pairs):
    """C5: d0 node overlap against BOTH P and A0 (amendment A8), listed for inspection."""
    keys, names, paths = doc["node_mbids"], doc["node_names"], doc["paths"]
    out = []
    for pair in pairs:
        a = paths[arm][pair]["0"]
        for ref in ("P", "A0"):
            if ref not in paths or ref == arm:
                continue
            r = paths[ref][pair]["0"]
            if not a or not r:
                continue
            sa, sr = set(interiors(a, keys)), set(interiors(r, keys))
            if sa != sr:
                out.append({"pair": pair, "vs": ref,
                            "overlap": len(sa & sr) / len(sa | sr) if (sa | sr) else 1.0,
                            # Paths shown by name -- this is the human inspection list.
                            "arm_path": [names[str(n)] for n in a],
                            "ref_path": [names[str(n)] for n in r]})
    return out


def one_column_contrasts(doc, F, analysis_pairs, arm_defs, package_contrasts=None):
    """P8b F9: compute each arm against ITS OWN isolating baseline, not only against P.

    §1.4 is explicit that attribution to a knob comes only from the chain of comparisons
    differing by exactly one column. Every criterion above is scored against P, which is
    the right *outcome* reference but the wrong *attribution* reference: A5-vs-P differs
    from P by two columns and cannot tell you what either did.

    `Arm.baseline` and `PACKAGE_CONTRASTS` encoded that chain from the start and nothing
    read them, which made the package-contrast note exactly the thing A16's rule exists
    to catch -- a disclaimer nothing consumes -- one level down from where A16 found it.

    The delta computed here is the same paired-cell median difference C1 uses, so it is
    directly comparable to the C1 column, just re-referenced.
    """
    keys, paths = doc["node_mbids"], doc["paths"]
    if package_contrasts is None:
        from arms import PACKAGE_CONTRASTS as package_contrasts

    def delta(arm, base):
        """C1's paired-cell statistic, re-referenced from P to `base`."""
        deltas = []
        for pair in analysis_pairs:
            for d in C1_DEPTHS:
                mb = cell_median(paths[base][pair][str(d)], keys, F)
                ma = cell_median(paths[arm][pair][str(d)], keys, F)
                if mb is not None and ma is not None:
                    deltas.append(ma - mb)
        return {
            "vs": base,
            "mean_dF": statistics.mean(deltas) if deltas else float("nan"),
            "frac_negative": (sum(1 for x in deltas if x < 0) / len(deltas))
                             if deltas else 0.0,
            "n_cells": len(deltas),
        }

    def present(*names):
        return all(n in paths for n in names)

    # The isolating chain: each arm against the arm one column away. `Arm.baseline`
    # already encodes it, INCLUDING for A6/A7 — whose baselines are A2/A4, not A0.
    # Package-ness is a property of the PAIR, not of the arm: A7-vs-A4 is a clean
    # one-column contrast and A7-vs-A0 is the three-column package. Keying this by
    # arm name would mislabel the clean ones.
    isolating = {a.name: delta(a.name, a.baseline)
                 for a in arm_defs
                 if a.baseline is not None and present(a.name, a.baseline)}

    # The named packages, computed rather than merely disclaimed. §1.4 requires them
    # to be visible AND unattributable; A16's rule is that a disclaimer nothing reads
    # is not a control, so they are reported with the warning attached to the figure.
    package = {f"{a} vs {b}": {**delta(a, b), "cannot_attribute": why}
               for (a, b), why in package_contrasts.items() if present(a, b)}

    return {"isolating": isolating, "package": package}


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
    ap.add_argument("--blank-cells", choices=("fail", "drop"), default="fail",
                    help="what to do when a scored interior has no name (P8b F8). "
                         "'fail' (default) raises and lists them. 'drop' applies the "
                         "PRE-REGISTERED response: remove the affected cells from ALL "
                         "arms uniformly and report them. Decided before stage 1 ran, "
                         "not after seeing which arm trips it.")
    ap.add_argument("--arms-module", metavar="PY",
                    help="Track 2F: take arm definitions (the isolating chain and the "
                         "package list) from this file rather than from `arms.py`. Must "
                         "be the same module the run used. Additive and default off.")
    ap.add_argument("--also-drop", metavar="PATHS_JSON",
                    help="union another run's dropped_cells_d7 into this one before "
                         "scoring. This is the re-score `run_arms.py --stage2` asks for "
                         "when stage 2 finds a cell stage 1 did not (A13 across the "
                         "stage boundary, P8b F3). Scoring is offline, so it is free.")
    args = ap.parse_args()

    doc = json.loads(Path(args.paths).read_text(encoding="utf-8"))
    if args.also_drop:
        other = json.loads(Path(args.also_drop).read_text(encoding="utf-8"))
        if other.get("artifact_sha256") != doc.get("artifact_sha256"):
            raise SystemExit("--also-drop ran on a different artifact; not comparable")
        extra = set(other.get("dropped_cells_d7", [])) - set(doc.get("dropped_cells_d7", []))
        for cell in extra:
            pair, _, dtag = cell.rpartition("@d")
            for arm in doc["paths"]:
                doc["paths"][arm][pair][dtag] = None
        doc["dropped_cells_d7"] = sorted(set(doc.get("dropped_cells_d7", [])) | extra)
        print(f"--also-drop: {len(extra)} additional cell(s) dropped from ALL arms")
    fame_doc = json.loads(Path(args.fame).read_text(encoding="utf-8"))
    F = fame_doc["fame"]
    # Both keyed by mbid, like F (P8b F8). `notable` is an audit hook; `nameless` is a
    # reach exclusion. See C2 in `score_arm` for why they are treated differently.
    guard = {"notable": set(fame_doc.get("potentially_notable_unmatched", [])),
             "nameless": set(fame_doc.get("nameless_nodes", []))}
    # F13: nothing else binds these two files. A name-keyed fame.json would silently
    # score every interior at the floor (no mbid would ever hit), so fail loud instead.
    if not fame_doc.get("keyed_by", "").startswith("mbid"):
        raise SystemExit("fame.json is not mbid-keyed; re-run fame.py (P8b F8)")
    # P8b F8's assertion, failing loud by default. The exposure this closes is
    # DIRECTIONAL, not noise: blank names sit 2.7x concentrated in the bottom
    # popularity decile, resolve to F = 0, and P has none — so contamination arrives
    # in the diving arms and nowhere else, and it arrives pointing at "pass".
    blank_cells = blank_scored_cells(doc)
    if blank_cells:
        print(f"\nP8b F8 — {len(blank_cells)} scored cell(s) contain a blank-named "
              f"interior:")
        for cell, arms_hit in blank_cells.items():
            print(f"  - {cell}   in: {', '.join(arms_hit)}")
        if args.blank_cells == "fail":
            raise SystemExit(
                "\nRefusing to score. A blank-named interior is an artifact defect that\n"
                "resolves to the fame floor, so it reads as maximal obscurity and biases\n"
                "C1 and C3 toward passing — in the diving arms only. The pre-registered\n"
                "response is a UNIFORM cell drop: re-run with --blank-cells drop.\n"
                "Do NOT drop the node instead; that is the directional fix this refuses."
            )
        apply_uniform_blank_drop(doc, blank_cells)
        doc["dropped_cells_blank_name"] = sorted(blank_cells)
        print(f"  -> dropped from ALL {len(doc['paths'])} arms uniformly "
              f"(pre-registered response; A13's rule applied to a second cause)")
    else:
        doc["dropped_cells_blank_name"] = []

    B = b_unk()
    held = set(doc.get("held_out_pairs", []))
    analysis = [p for p in doc["pairs"] if p not in held]

    print(f"B_unk = {B:.3f} fame units   analysis pairs: {len(analysis)}   "
          f"held-out: {len(held)}")
    if doc.get("dropped_cells_d7"):
        print(f"D7: {len(doc['dropped_cells_d7'])} cell(s) dropped from ALL arms uniformly")

    results, extras = {}, {}
    for arm in doc["arms"]:
        results[arm] = score_arm(arm, doc, F, analysis, B, guard)
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

    from arms import STAGE1, R1_ELIGIBLE, stage2
    packages = None

    if args.arms_module:
        # Track 2F: the run used externally-defined arms, so the isolating chain and the
        # package list must come from the SAME module that defined them -- reading them
        # from `arms` would silently drop every new arm out of the attribution table,
        # which is the "disclaimer nothing reads" failure one level down (A16).
        import importlib.util

        spec = importlib.util.spec_from_file_location("_arms_module", args.arms_module)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        arm_defs = mod.build_arms({a.name: a for a in STAGE1})
        packages = getattr(mod, "PACKAGE_CONTRASTS", {})
        # R1 selected W in Track 2 and W is an INPUT here, not an output. Running the
        # rule again on a different arm set would print a selection nobody asked for.
        W, why = doc["arms"][0], "not applicable: W is an input to this run, not selected"
        if "A7" in doc["arms"]:
            W, why = "A7", "W fixed as Track 2's R1 fallback; not re-selected here"
    else:
        W, why = choose_W(results, R1_ELIGIBLE)
        # Arm definitions for whichever stage this file holds. Stage 2's attachments are
        # not in STAGE1, so the isolating chain for them is rebuilt from the recorded W.
        arm_defs = list(STAGE1)
        stage2_w = doc.get("stage2_w")
        if stage2_w:
            w_cfg = next(a.cfg for a in STAGE1 if a.name == stage2_w)
            arm_defs += stage2(stage2_w, w_cfg)
    contrasts = one_column_contrasts(doc, F, analysis, arm_defs, packages)

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

    # F9: attribution table. Separate from the gate table above on purpose -- that one
    # answers "did this arm clear the bar", this one answers "what did the knob do".
    if contrasts["isolating"]:
        print("\nisolating one-column contrasts (P8b F9) — each arm vs the arm one "
              "column away.\nThese are the ONLY contrasts a knob effect may be "
              "attributed to (§1.4).")
        print(f"{'arm':<5} {'vs':>5} {'mean dF':>9} {'frac<0':>7} {'cells':>6}  knob")
        for a in arm_defs:
            c = contrasts["isolating"].get(a.name)
            if c:
                print(f"{a.name:<5} {c['vs']:>5} {c['mean_dF']:>9.3f} "
                      f"{c['frac_negative']:>7.2f} {c['n_cells']:>6}  {a.reading}")
    if contrasts["package"]:
        print("\npackage contrasts — computed, and NOT attributable to any single knob:")
        for label, c in sorted(contrasts["package"].items()):
            print(f"  {label:<12} mean dF {c['mean_dF']:>7.3f} over {c['n_cells']:>3} "
                  f"cells   [{c['cannot_attribute']}]")

    # F2/F8: an auditable C2. Silence here means no pass depended on a flagged artist.
    for arm in doc["arms"]:
        c2 = results[arm]["C2"]
        if c2["rests_only_on_flagged_notable"]:
            print(f"\n⚠ {arm}: C2 pass rests ONLY on flagged-notable interiors in "
                  f"{len(c2['rests_only_on_flagged_notable'])} pair(s) — owner glance "
                  f"required before this counts (A11 guard, wired per P8b F2):")
            for pair, mbids in sorted(c2["rests_only_on_flagged_notable"].items()):
                shown = ", ".join(fame_doc["names"].get(m, m) for m in mbids)
                print(f"    {pair}: {shown}")

    label = "W" if args.arms_module else "R1 selects W ="
    print(f"\n{label} {W}  ({why})")

    Path(args.out).write_text(json.dumps(
        {"b_unk_fame_units": B, "analysis_pairs": analysis,
         "blank_name_cells_dropped": doc["dropped_cells_blank_name"],
         "W": W, "W_rationale": why, "results": results,
         "one_column_contrasts": contrasts, "diagnostics": extras},
        indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
