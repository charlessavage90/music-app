"""`JFX-` criteria, computed from `jfx_routes.json`. No routing, no network.

**Governing:** `specs/2026-08-09-journey-fame-exposure-preregistration.md` as amended
by `JFX-AM1`, which governs §2/§3/§4 where they disagree with the original text.

Every criterion below carries the plain sentence fixed in §3 **before any result
existed**, quoted rather than paraphrased, because owner-facing text must give the
identifier *and* the sentence.

## The statistic, and its sign convention (stated once)

Per journey: the **median interior fame** in `log10(1 + fame_lb)` (`AM1.2`), interiors
without a measurement **excluded** (§2's null rule) and counted for `C7`.

Everything downstream is a **paired median of per-pair differences** — §2's definition,
and `AM1.5` is explicit that `G1a` and `G1b` are both computed on it rather than over
pooled levels, because `DD-P3H-2` had a **sign flip** from exactly that difference.

- A **drop** `D_X = median_pairs[ m_X(d0) - m_X(d20) ]`, so **positive means fame went
  DOWN** as the user pressed — the direction the product wants.
- A **step** `median_pairs[ m_B(d2) - m_B(d1) ]`, so **positive means fame ROSE** over
  that step, which is the failure direction for `G1a`.

## Two things this file will not do

- **`JFX-C2` gets no materiality threshold.** Withdrawn before commit on the owner's
  agreement (§3): it gates nothing and fires no branch, so a bar could only decide in
  advance which differences the write-up calls material. All three strata are printed
  side by side with intervals and the reader draws the comparison.
- **`G1b` is not evaluated when `D_A`'s interval includes zero.** `AM1.5`'s viability
  clause: the ratio equivalence holds only for `D_A > 0`. Then `G1b` is **undefined —
  not passed and not fired** — and the report says so in those words.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from jfx_stats import (  # noqa: E402
    C6_FLOOR_FIRE_PP,
    C7_NULL_SHARE_PP,
    STEP_RISE_EFFECT_LOG10,
    g1b_contrast,
    joint_bootstrap,
    one_sided_lower,
    paired_median_ci,
    seeded,
    simultaneous_band,
    two_sided,
)

ROUTES = HERE / "jfx_routes.json"
PAIRSET = HERE / "jfx_pairset.json"
OUT = HERE / "jfx_results.json"

DEPTHS = (0, 5, 10, 20)
STEPS = ((0, 5), (5, 10), (10, 20))
G1B_BAR = 0.67

SENTENCES = {
    "JFX-G1": "Does pressing \"dig deeper\" still keep making the middle of the "
              "journey less famous, press after press?",
    "JFX-C1": "On the bigger map, is the typical artist in the middle of a journey "
              "more famous or less famous than before?",
    "JFX-C2": "Does that answer differ depending on whether you picked two famous "
              "artists or two obscure ones?",
    "JFX-C3": "Do journeys get longer — and if they do, do they buy more discovery "
              "for it?",
    "JFX-C4": "How many more artists can now appear in a journey at all, or be "
              "found in search?",
    "JFX-C5": "Have famous artists been pushed out?",
    "JFX-C6": "Did the obscurity-floor rule start firing on the bigger map when it "
              "never used to?",
    "JFX-C7": "How many artists in the middle have no listener measurement at all, "
              "and does that differ between the two maps?",
}


def journey_median(rec: dict) -> float | None:
    """Median interior fame for one journey, or None if nothing is measurable."""
    vals = rec["interior_log_fame"]
    return statistics.median(vals) if vals else None


def build_records(routes: dict) -> tuple[list[dict], dict]:
    """One record per pair carrying BOTH arms at ALL FOUR depths.

    `AM1.5`'s joint bootstrap resamples the pair carrying both arms and all four
    depths together; a pair missing any cell cannot participate in the contrast, so
    it is dropped from the paired analysis and **counted**, never imputed.
    """
    a_rows, b_rows = routes["JFX-A"], routes["JFX-B"]
    records, dropped = [], {"missing_cell": 0, "one_arm_only": 0}
    for pk in sorted(a_rows):
        if pk not in b_rows:
            dropped["one_arm_only"] += 1
            continue
        a, b = a_rows[pk], b_rows[pk]
        rec = {"pair": pk, "stratum": a["stratum"], "A": {}, "B": {}}
        ok = True
        for arm, src in (("A", a), ("B", b)):
            for d in DEPTHS:
                cell = src["depths"].get(str(d))
                if cell is None:
                    ok = False
                    break
                med = journey_median(cell)
                if med is None:
                    ok = False
                    break
                rec[arm][d] = {
                    "median_log_fame": med,
                    "path_length": cell["path_length"],
                    "interior_n": cell["interior_n"],
                    "null_n": cell["interior_null_n"],
                    "floor_fired": cell["floor_fired"],
                    "kind": cell["kind"],
                }
            if not ok:
                break
        if ok:
            records.append(rec)
        else:
            dropped["missing_cell"] += 1
    return records, dropped


# --- statistics computed on one (re)sample of pairs -------------------------

def _drop(sample, arm) -> float:
    return statistics.median(
        [r[arm][0]["median_log_fame"] - r[arm][20]["median_log_fame"] for r in sample]
    )


def _step(sample, d1, d2) -> float:
    return statistics.median(
        [r["B"][d2]["median_log_fame"] - r["B"][d1]["median_log_fame"] for r in sample]
    )


def all_statistics(sample) -> dict:
    out = {
        "D_A": _drop(sample, "A"),
        "D_B": _drop(sample, "B"),
    }
    out["T"] = g1b_contrast(out["D_B"], out["D_A"], G1B_BAR)
    for d1, d2 in STEPS:
        out[f"step_{d1}_{d2}"] = _step(sample, d1, d2)
    return out


def paired_mean_ci(diffs, rng, reps: int = 10_000) -> list[float]:
    """Percentile bootstrap interval on the paired MEAN. `AM1.11`.

    Read 9's trigger is *"the median is null and the mean's interval excludes
    zero (or the converse)"* — so the mean needs an interval, and the frozen
    `ULC-` estimator only intervals the median. Same resampling convention
    (resample the differences, `rng.randrange`, percentile bounds) so the two
    intervals are read on the same footing.

    ⚠ An earlier version of this file triggered read 9 on *"fewer than half the
    pairs moved"*. That is `AM1.11`'s RATIONALE for why the median lacks power,
    not its trigger — and importing a rationale as a condition silently
    suppressed the report at exactly the depths where the two statistics
    disagreed. Found by reading the d10/d20 rows against the amendment.
    """
    n = len(diffs)
    draws = sorted(
        statistics.fmean([diffs[rng.randrange(n)] for _ in range(n)])
        for _ in range(reps)
    )
    return two_sided(draws)


def share(records, arm, depth, field) -> float:
    return 100.0 * sum(1 for r in records if r[arm][depth][field]) / len(records)


def null_share(records, arm, depth) -> float:
    """Share of INTERIOR ARTISTS (not journeys) with no measurement. §2 / C7."""
    nulls = sum(r[arm][depth]["null_n"] for r in records)
    total = sum(r[arm][depth]["interior_n"] for r in records)
    return 100.0 * nulls / total if total else 0.0


def null_share_all(routes, arm_key, depth) -> float:
    """`C7` over EVERY routed journey, not only those in the paired set.

    The paired set drops any pair whose journey has **no measured interior at
    all** — its median is undefined — and those are precisely the most
    null-heavy journeys. So `null_share` over the paired records **under-reports
    the real exposure**, and reporting only that number would let the statistic's
    own exclusion rule hide the thing `C7` exists to expose.

    Both are printed. The paired figure is what the gradient is computed on; this
    one is what a person actually meets.
    """
    nulls = total = 0
    for rec in routes[arm_key].values():
        cell = rec["depths"].get(str(depth))
        if cell is None:
            continue
        nulls += cell["interior_null_n"]
        total += cell["interior_n"]
    return 100.0 * nulls / total if total else 0.0


def fmt_ci(ci) -> str:
    return f"[{ci[0]:+.4f}, {ci[1]:+.4f}]"


def main() -> int:
    if not ROUTES.is_file():
        raise SystemExit(f"missing {ROUTES.name}; run jfx_route.py first")
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    meta = routes.get("_meta", {})
    if meta.get("smoke_run_limit"):
        print("⚠ " + "=" * 68)
        print("⚠ SMOKE RUN — jfx_route.py was run with --limit "
              f"{meta['smoke_run_limit']}. §2 fixes the analysed set at 100 per")
        print("⚠ stratum. NOTHING BELOW IS A RESULT. Wiring check only.")
        print("⚠ " + "=" * 68 + "\n")
    pairset = json.loads(PAIRSET.read_text(encoding="utf-8"))

    records, dropped = build_records(routes)
    n = len(records)
    print("=" * 72)
    print("JFX- RESULTS — measured")
    print("=" * 72)
    print(f"\npairs routed in both arms at all four depths: {n}")
    print(f"   dropped, a missing or unmeasurable cell: {dropped['missing_cell']}")
    print(f"   dropped, present in one arm only:        {dropped['one_arm_only']}")
    if n == 0:
        raise SystemExit("no paired records; nothing can be computed")
    by_stratum: dict[str, list] = {}
    for r in records:
        by_stratum.setdefault(r["stratum"], []).append(r)
    print("   per stratum: " + ", ".join(
        f"{k} {len(v)}" for k, v in sorted(by_stratum.items())))

    # ---- §4 presupposition ------------------------------------------------
    print("\n§4 presupposes all 300 pairs routed in both arms at all four depths,")
    print("   with C6 and C7 both reported. Both validity checks are below.")

    point = all_statistics(records)
    draws = joint_bootstrap(records, seeded("JFX-joint"), all_statistics)

    # ---- JFX-C6 / C7: the validity checks, FIRST (§4 reads 7 and 8) -------
    print("\n" + "-" * 72)
    print(f"JFX-C6 — {SENTENCES['JFX-C6']}")
    print("-" * 72)
    c6_fired, c6_rows = False, {}
    for d in DEPTHS:
        a_s, b_s = share(records, "A", d, "floor_fired"), share(records, "B", d, "floor_fired")
        c6_rows[d] = {"A_pct": a_s, "B_pct": b_s, "delta_pp": b_s - a_s}
        hot = (b_s - a_s) >= C6_FLOOR_FIRE_PP
        c6_fired |= hot
        print(f"   d{d:<3} A {a_s:6.2f}%   B {b_s:6.2f}%   Δ {b_s - a_s:+6.2f} pp"
              + ("   ← ≥ 5 pp" if hot else ""))
    if c6_fired:
        print("\n   ⚠ JFX-C6 FIRES §4 read 7: EVERY READING IN THIS REPORT IS VOID")
        print("     AS A ONE-KNOB ATTRIBUTION, and this report says so in those words.")

    print("\n" + "-" * 72)
    print(f"JFX-C7 — {SENTENCES['JFX-C7']}")
    print("-" * 72)
    c7_fired, c7_rows = False, {}
    print("   paired set (what the gradient is computed on):")
    for d in DEPTHS:
        a_s, b_s = null_share(records, "A", d), null_share(records, "B", d)
        a_all, b_all = null_share_all(routes, "JFX-A", d), null_share_all(routes, "JFX-B", d)
        c7_rows[d] = {"A_pct": a_s, "B_pct": b_s, "delta_pp": b_s - a_s,
                      "A_pct_all_journeys": a_all, "B_pct_all_journeys": b_all}
        hot = (b_s - a_s) >= C7_NULL_SHARE_PP
        c7_fired |= hot
        print(f"   d{d:<3} A {a_s:6.2f}%   B {b_s:6.2f}%   Δ {b_s - a_s:+6.2f} pp"
              + ("   ← ≥ 2 pp" if hot else ""))
    print("   ALL routed journeys (what a person actually meets — the paired set")
    print("   drops journeys with no measured interior at all, which are exactly")
    print("   the most null-heavy, so the rows above UNDER-report the exposure):")
    for d in DEPTHS:
        row = c7_rows[d]
        print(f"   d{d:<3} A {row['A_pct_all_journeys']:6.2f}%   "
              f"B {row['B_pct_all_journeys']:6.2f}%   "
              f"Δ {row['B_pct_all_journeys'] - row['A_pct_all_journeys']:+6.2f} pp")
    # AM1.7's depth-conditional half: a rising null share ATTENUATES that arm's
    # own gradient, because the ramp pulls routes onto artists §2 discards.
    rising = {arm: c7_rows[DEPTHS[-1]][f"{arm}_pct"] > c7_rows[DEPTHS[0]][f"{arm}_pct"]
              for arm in ("A", "B")}
    for arm, up in rising.items():
        if up:
            print(f"   ⚠ AM1.7: the null share RISES WITH DEPTH in JFX-{arm}, so that")
            print(f"     arm's measured gradient is ATTENUATED. Stated, per AM1.7.")
    if c7_fired:
        print("\n   ⚠ JFX-C7 fires §4 read 8: the fame comparison carries a known")
        print("     upward bias in whichever arm has more nulls (§2).")

    # ---- JFX-G1 -----------------------------------------------------------
    print("\n" + "=" * 72)
    print(f"JFX-G1 (GATE) — {SENTENCES['JFX-G1']}")
    print("=" * 72)

    step_names = [f"step_{a}_{b}" for a, b in STEPS]
    band = simultaneous_band({k: draws[k] for k in step_names},
                             {k: point[k] for k in step_names})
    print("\nG1a — on JFX-B, does each press keep making the middle less famous?")
    print("   (positive = fame ROSE over that step = the failure direction)")
    g1a_step_fail = []
    for (d1, d2), name in zip(STEPS, step_names):
        lo, hi = band[name]
        excl_zero = lo > 0.0
        big = point[name] >= STEP_RISE_EFFECT_LOG10
        fails = excl_zero and big
        g1a_step_fail.append(fails)
        print(f"   d{d1}→d{d2}: {point[name]:+.4f}  simultaneous band "
              f"{fmt_ci([lo, hi])}"
              + ("   ← FAILS" if fails else ""))
    print(f"   (a step fails only if its band excludes zero AND the rise is "
          f"≥ {STEP_RISE_EFFECT_LOG10} log10 — AM1.6)")

    d_b_ci = two_sided(draws["D_B"])
    overall_ok = point["D_B"] > 0 and d_b_ci[0] > 0
    print(f"\n   overall d0→d20 drop on JFX-B: {point['D_B']:+.4f} "
          f"CI {fmt_ci(d_b_ci)}"
          + ("   ✓ below d0, CI excludes zero" if overall_ok else "   ← FAILS"))
    g1a_pass = overall_ok and not any(g1a_step_fail)
    print(f"\n   G1a: {'PASS' if g1a_pass else '**FAIL**'}")
    print("   ⚠ AM1.3: G1a is a WEAK test in the absolute — victim_key deletes the")
    print("     most famous interior twenty times, so part of any decrease is")
    print("     mechanical. It is NOT evidence the product works for a user.")

    d_a_ci = two_sided(draws["D_A"])
    t_a = point["D_A"] / max((d_a_ci[1] - d_a_ci[0]) / 4.0, 1e-12)
    d_a_viable = d_a_ci[0] > 0
    print(f"\nG1b — is JFX-B's drop at least {G1B_BAR:.0%} of JFX-A's?")
    print(f"   D_A (adopted map): {point['D_A']:+.4f}  CI {fmt_ci(d_a_ci)}  "
          f"t_A ≈ {t_a:.2f}")
    print(f"   D_B (bigger map):  {point['D_B']:+.4f}  CI {fmt_ci(d_b_ci)}")
    g1b_state = None
    if not d_a_viable:
        g1b_state = "undefined"
        print("\n   ⚠ D_A's bootstrap interval does NOT exclude zero.")
        print("     JFX-G1b is UNDEFINED, NOT PASSED AND NOT FIRED (AM1.5's")
        print("     viability clause). The ratio equivalence holds only for D_A > 0.")
        print("     The adoption question falls to G1a plus the gradients.")
    else:
        r_hat = point["D_B"] / point["D_A"]
        t_lo = one_sided_lower(draws["T"])
        fires = point["T"] < 0
        g1b_state = "fires" if fires else "pass"
        print(f"\n   R̂ = {r_hat:.3f}  (point estimate only — AM1.5: never interval it)")
        print(f"   T = D_B − {G1B_BAR}·D_A = {point['T']:+.4f}   one-sided 95% lower "
              f"bound {t_lo:+.4f}")
        print(f"   G1b: {'**FIRES** (below the bar)' if fires else 'PASS'}")
        # AM1.9: the realised press-count equivalence, beside the ratio.
        if r_hat > 0:
            print(f"   AM1.9 realised press-count equivalence: reaching JFX-A's "
                  f"20-press")
            print(f"     distance takes ≈ {20 / r_hat:.0f} presses on JFX-B "
                  f"(the translation the bar was set on, measured not assumed)")

    # ---- gradients --------------------------------------------------------
    print("\n" + "-" * 72)
    print(f"JFX-C1 — {SENTENCES['JFX-C1']}")
    print("-" * 72)
    print("   (B − A per pair; NEGATIVE = the bigger map's middles are LESS famous)")
    c1_rows = {}
    for d in DEPTHS:
        diffs = [r["B"][d]["median_log_fame"] - r["A"][d]["median_log_fame"]
                 for r in records]
        ci = paired_median_ci(diffs, seeded(f"JFX-C1-d{d}"))
        mean = statistics.fmean(diffs)
        mean_ci = paired_mean_ci(diffs, seeded(f"JFX-C1-mean-d{d}"))
        moved = sum(1 for x in diffs if abs(x) > 1e-12)
        c1_rows[d] = {"median": ci["median_diff"], "ci95": ci["ci95"],
                      "mean": mean, "mean_ci95": mean_ci, "pairs_moved": moved}
        print(f"   d{d:<3} median {ci['median_diff']:+.4f} CI {fmt_ci(ci['ci95'])}")
        print(f"        mean {mean:+.4f} CI {fmt_ci(mean_ci)}"
              f"   pairs that moved {moved}/{len(diffs)}")
    # AM1.11 read 9: where one statistic is null and the other's interval
    # excludes zero, state it and report both. The gate stays on the MEDIAN —
    # promoting the mean would change what passes and is the owner's call, not
    # a bookkeeping fix.
    for d in DEPTHS:
        row = c1_rows[d]
        med_null = row["ci95"][0] <= 0 <= row["ci95"][1]
        mean_null = row["mean_ci95"][0] <= 0 <= row["mean_ci95"][1]
        if med_null == mean_null:
            continue
        null_one, live_one = ("median", "mean") if med_null else ("mean", "median")
        print(f"\n   ⚠ AM1.11 READ 9 FIRES AT d{d}: the {null_one} is null while the")
        print(f"     {live_one}'s interval EXCLUDES ZERO. Both are reported above.")
        print(f"       median {row['median']:+.4f} CI {fmt_ci(row['ci95'])}")
        print(f"       mean   {row['mean']:+.4f} CI {fmt_ci(row['mean_ci95'])}")
        print(f"     {row['pairs_moved']}/{len(records)} pairs moved, so the change is")
        print(f"     BALANCED in direction (median 0) but NOT in magnitude.")
        print(f"     ⚠ In plain terms: as many journeys got a less famous middle as")
        print(f"       a more famous one, but the ones that got MORE famous moved")
        print(f"       FURTHER. The gate stays on the median (AM1.11); promoting the")
        print(f"       mean would change what passes and is the OWNER'S call.")

    print("\n" + "-" * 72)
    print(f"JFX-C2 — {SENTENCES['JFX-C2']}")
    print("-" * 72)
    print("   (no materiality threshold, deliberately — §3. Read the numbers.)")
    c2_rows = {}
    for stratum, rows in sorted(by_stratum.items()):
        c2_rows[stratum] = {}
        for d in DEPTHS:
            diffs = [r["B"][d]["median_log_fame"] - r["A"][d]["median_log_fame"]
                     for r in rows]
            ci = paired_median_ci(diffs, seeded(f"JFX-C2-{stratum}-d{d}"))
            c2_rows[stratum][d] = {"median": ci["median_diff"], "ci95": ci["ci95"],
                                   "n": len(rows)}
            print(f"   {stratum} d{d:<3} n={len(rows):3d}  "
                  f"median {ci['median_diff']:+.4f} CI {fmt_ci(ci['ci95'])}")

    print("\n" + "-" * 72)
    print(f"JFX-C3 — {SENTENCES['JFX-C3']}")
    print("-" * 72)
    print("   §3 read rule: a length increase is acceptable ONLY where the same")
    print("   stratum also shows an interior-fame decrease.")
    c3_rows = {}
    for stratum, rows in sorted(by_stratum.items()):
        c3_rows[stratum] = {}
        for d in DEPTHS:
            diffs = [r["B"][d]["path_length"] - r["A"][d]["path_length"]
                     for r in rows]
            med_len = statistics.median(diffs)
            fame_down = c2_rows[stratum][d]["median"] < 0
            verdict = ""
            if med_len > 0:
                verdict = ("  longer AND fame down — acceptable per §3"
                           if fame_down else
                           "  ⚠ LONGER AND NOT LESS FAMOUS — a loss on both counts")
            c3_rows[stratum][d] = {"median_length_delta": med_len,
                                   "fame_down": fame_down}
            print(f"   {stratum} d{d:<3} median length change "
                  f"{med_len:+.1f}{verdict}")

    # ---- carried from the no-routing stage --------------------------------
    print("\n" + "-" * 72)
    print(f"JFX-C4 — {SENTENCES['JFX-C4']}")
    print(f"JFX-C5 — {SENTENCES['JFX-C5']}")
    print("-" * 72)
    c4, c5 = pairset["JFX-C4"], pairset["JFX-C5"]
    print(f"   C4: JFX-A only {c4['only_in_A']:,}   both {c4['in_both']:,}   "
          f"JFX-B only {c4['only_in_B']:,}   net {c4['net']:+,}")
    print(f"   AM1.8 |A \\ B| = {pairset['AM1.8_direct_count_A_minus_B']:,}")
    print(f"   C5: {c5['survived']:,}/{c5['pool']:,} = {c5['share'] * 100:.2f}% "
          f"(bar {c5['bar']:.0%}) → {'PASS' if c5['pass'] else '**FAIL**'}")

    # ---- REQ-Q1(a): the matched-only recomputation ------------------------
    print("\n" + "-" * 72)
    print("REQ-Q1(a) — the primary statistic recomputed over journeys with ZERO")
    print("null interiors, alongside the headline. (DD-D8: ~45% of a passing arm's")
    print("effect was once carried by artists at the fame floor.)")
    print("-" * 72)
    clean = [r for r in records
             if all(r[arm][d]["null_n"] == 0 for arm in ("A", "B") for d in DEPTHS)]
    print(f"   journeys with no null interior in any cell: {len(clean)}/{n}")
    matched = None
    if len(clean) >= 5:
        m_point = all_statistics(clean)
        m_draws = joint_bootstrap(clean, seeded("JFX-joint-matched"), all_statistics)
        matched = {
            "n": len(clean),
            "D_A": m_point["D_A"], "D_A_ci95": two_sided(m_draws["D_A"]),
            "D_B": m_point["D_B"], "D_B_ci95": two_sided(m_draws["D_B"]),
            "T": m_point["T"], "T_lower95": one_sided_lower(m_draws["T"]),
        }
        print(f"   D_A {m_point['D_A']:+.4f} CI {fmt_ci(matched['D_A_ci95'])}")
        print(f"   D_B {m_point['D_B']:+.4f} CI {fmt_ci(matched['D_B_ci95'])}")
        print(f"   T   {m_point['T']:+.4f}  one-sided lower "
              f"{matched['T_lower95']:+.4f}")
    else:
        print("   too few clean journeys to recompute; reported as such, not skipped")

    # ---- §5, restated so no reader has to go looking ----------------------
    print("\n" + "=" * 72)
    print("§5 — what this design CANNOT support")
    print("=" * 72)
    print("   • No claim that ADDING ARTISTS caused any effect. The arms differ by")
    print("     three things (§0) — plus the drop-payload change AM1.8 added, so")
    print("     four. No arm here isolates them.")
    print("   • No claim about coherence or whether journeys sound good. No")
    print("     listening is involved; REQ-9 puts novelty behind coherence.")
    print("   • No cross-arm comparison in percentile currency (§2).")
    print("   • Nothing about JFX-A vs the pre-MSW- world.")
    if c6_fired:
        print("\n   ⚠ AND: JFX-C6 fired, so EVERY READING ABOVE IS VOID AS A")
        print("     ONE-KNOB ATTRIBUTION (§4 read 7).")

    OUT.write_text(json.dumps({
        "status": "JFX- computed criteria. Nothing adopted, nothing deployed.",
        "governing": "specs/2026-08-09-journey-fame-exposure-preregistration.md",
        "smoke_run_limit": meta.get("smoke_run_limit"),
        "n_pairs": n, "dropped": dropped,
        "per_stratum_n": {k: len(v) for k, v in sorted(by_stratum.items())},
        "JFX-G1": {
            "G1a": {"pass": bool(g1a_pass), "overall_D_B": point["D_B"],
                    "overall_ci95": d_b_ci,
                    "steps": {name: {"point": point[name], "band": band[name],
                                     "fails": bool(f)}
                              for name, f in zip(step_names, g1a_step_fail)}},
            "G1b": {"state": g1b_state, "bar": G1B_BAR,
                    "D_A": point["D_A"], "D_A_ci95": d_a_ci, "t_A": t_a,
                    "D_B": point["D_B"], "T": point["T"],
                    "T_lower95": one_sided_lower(draws["T"]),
                    "R_hat": (point["D_B"] / point["D_A"]) if d_a_viable else None},
        },
        "JFX-C1": c1_rows, "JFX-C2": c2_rows, "JFX-C3": c3_rows,
        "JFX-C4": c4, "JFX-C5": c5,
        "JFX-C6": {"rows": c6_rows, "fires_read_7": bool(c6_fired)},
        "JFX-C7": {"rows": c7_rows, "fires_read_8": bool(c7_fired),
                   "rises_with_depth": rising},
        "REQ-Q1a_matched_only": matched,
        "sentences": SENTENCES,
    }, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
