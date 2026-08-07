"""`TCR-` — the thin-catalogue probe, re-run under externally anchored gates.

Governing document:
  docs/superpowers/specs/2026-08-06-thin-catalogue-rerun-preregistration.md
  committed, with g1_anchors.json and this runner, BEFORE the dump counter ran
  against any gate anchor and before any outcome value existed.

Predecessor: the VOID `TCE-` run (../2026-08-06-tce-thin-catalogue/), whose
record stands untouched. Its gate fired; no outcome was computed there and
none is inherited here.

Execution order is fixed by the prereg §6 and ENFORCED STRUCTURALLY:

  phase 0  anchors: TCR-G1 MBIDs and bands read from the COMMITTED
           g1_anchors.json; Laura Lee MBIDs from the committed ll_closure.json
  phase 1  reference sets (WITH scores, for the §0.1 tie rule) + needed MBIDs
  phase 2  one streaming pass over the MB release-group dump -> counts
  phase 3  TCR-G1  instrument validation, FIRST AND ALONE. Fail => VOID.
           Both Laura Lees reported as run state, adjudicating NOTHING.
  phase 4  TCR-G2  coverage floor via the ARTIST dump. Below 0.95 => VOID.
  phase 5  ALL run-state quantities, PER ARM, WRITTEN TO DISK
  phase 6  outcomes -- reloads phase 5's file first, so no outcome can have
           informed a run-state quantity. Rank-10 boundary ties resolved by
           EXACT average-rank expectation (prereg §0.1), both arms.
  phase 7  the three §4.4 mitigations, incl. the top-20 eyeball dump

Run from `api/` (it loads the adopted artifact through the API's GraphStore):

  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
    ../builder/analysis/2026-08-06-tcr-thin-catalogue-rerun/tcr_run.py

Dump passes cache to rg_counts.json.gz / artist_exists.json.gz (gitignored);
they are rebuilt here rather than reused from the TCE- directory because the
needed-MBID set now includes the gate anchors.

This directory OWNS its figures. Cite it; never restate them.
"""
import array
import gzip
import json
import math
import os
import statistics
import sys
import time
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = ("../builder/scratch/grt-archive-algb/similar/listenbrainz/"
           "session_based_days_7500_session_300_contribution_3_threshold_10_"
           "limit_100_filter_True_skip_30/")
GRAPH = "../builder/scratch/graph-msw-tu50.bin"
GRAPH_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
DUMP = "../builder/scratch/mb-json-dumps/release-group/mbdump/release-group"
ARTIST_DUMP = "../builder/scratch/mb-json-dumps/artist/mbdump/artist"
ANCHORS = os.path.join(HERE, "g1_anchors.json")            # committed
LL_SOURCE = "../builder/analysis/2026-08-06-laura-lee-closure/ll_closure.json"

COUNTS_CACHE = os.path.join(HERE, "rg_counts.json.gz")
EXISTS_CACHE = os.path.join(HERE, "artist_exists.json.gz")
RUNSTATE = os.path.join(HERE, "tcr_runstate.json")
RESULT = os.path.join(HERE, "tcr_result.json")
EYEBALL = os.path.join(HERE, "tcr_eyeball_top20.json")

MIN_LIST = 30          # prereg §1
TOP_K = 10             # prereg §4.1
COVERAGE_FLOOR = 0.95  # TCR-G2

# TCR-G1 gate cells (prereg §3 table). Band = live ± max(2, ceil(0.05*live))
# for nonzero cells; the zero cell is exact. Recomputed here from the
# committed anchors and asserted against the prereg's literal table values,
# so a drifted copy of either fails loudly instead of silently governing.
PREREG_BANDS = {
    "alana_haim": (0, 0),
    "andrew_vanwyngarden": (2, 6),
    "leon_bridges": (35, 39),
    "khruangbin": (56, 62),
    "radiohead": (554, 614),
}


def band_for(live):
    if live == 0:
        return (0, 0)
    tol = max(2, math.ceil(0.05 * live))
    return (live - tol, live + tol)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg))


T0 = time.time()


# ---------------------------------------------------------------- statistics
def hyp_pmf(L, T, k, x):
    """P(X = x), X ~ Hypergeometric(population L, successes T, draws k)."""
    lo, hi = max(0, T - (L - k)), min(k, T)
    if x < lo or x > hi:
        return 0.0
    return comb(T, x) * comb(L - T, k - x) / comb(L, k)


def mid_p(L, T, k, x):
    """M_R = P(X < x) + 0.5 P(X = x). Null mean is exactly 0.5 (TCR-C3)."""
    lo, hi = max(0, T - (L - k)), min(k, T)
    below = sum(hyp_pmf(L, T, k, j) for j in range(lo, x))
    return below + 0.5 * hyp_pmf(L, T, k, x)


def c5_null_for(L, T, k):
    """P_null(upper-tail mid-p <= 0.05) for one artist. Base-rate dependent,
    so computed from (L_R, T_R) BEFORE any x_R is read (prereg §4.3/§6)."""
    lo, hi = max(0, T - (L - k)), min(k, T)
    tot = 0.0
    for x in range(lo, hi + 1):
        if (1.0 - mid_p(L, T, k, x)) <= 0.05:
            tot += hyp_pmf(L, T, k, x)
    return tot


def ceiling_term(L, T, k):
    """What Δ_R would be if every thin neighbour sat in the top k."""
    x = min(k, T)
    return x / k - (T - x) / (L - k)


def top_slots(scores):
    """The §0.1 tie rule's block geometry for one sorted list.

    Returns (idx_cut, block_lo, block_hi) where idx_cut = TOP_K when no block
    spans the rank-10 boundary; otherwise the maximal equal-score block is
    positions block_lo..block_hi (0-indexed) with block_lo <= 9 < block_hi.
    """
    if len(scores) <= TOP_K or scores[TOP_K - 1] != scores[TOP_K]:
        return TOP_K, None, None
    s = scores[TOP_K - 1]
    lo = TOP_K - 1
    while lo > 0 and scores[lo - 1] == s:
        lo -= 1
    hi = TOP_K
    while hi + 1 < len(scores) and scores[hi + 1] == s:
        hi += 1
    return None, lo, hi


def tie_stats(members_thin, scores):
    """(E[X], list of (x, p)) for thin-in-top-10 under the §0.1 tie rule.

    members_thin: per-position 0/1 thinness for the sorted list.
    Exact expectation over a uniformly random ordering of the boundary block:
    X = x_above + H, H ~ Hypergeometric(n_block, t_block, s_slots).
    """
    cut, lo, hi = top_slots(scores)
    if cut is not None:
        x = sum(members_thin[:cut])
        return float(x), [(x, 1.0)]
    n = hi - lo + 1
    t = sum(members_thin[lo:hi + 1])
    s = TOP_K - lo
    x_above = sum(members_thin[:lo])
    dist = []
    for h in range(max(0, t - (n - s)), min(s, t) + 1):
        dist.append((x_above + h, hyp_pmf(n, t, s, h)))
    ex = sum(x * p for x, p in dist)
    return ex, dist


# ------------------------------------------------------------------ phase 1-2
def load_reference_sets():
    """(arm -> {ref_mbid: (idx array, score array)}), plus bookkeeping.

    Lists are sorted by (score desc, mbid asc) — deterministic, and the
    ordering the §0.1 tie rule is defined over.
    """
    idx_of, mbid_of = {}, []

    def idx(m):
        i = idx_of.get(m)
        if i is None:
            i = len(mbid_of)
            idx_of[m] = i
            mbid_of.append(m)
        return i

    # --- arm A: the raw archive ---
    arm_a, names = {}, {}
    files = os.listdir(ARCHIVE)
    log("arm A: scanning %d archive files" % len(files))
    for n, fn in enumerate(files):
        if not fn.endswith(".json"):
            continue
        if n and n % 20000 == 0:
            log("   ...%d" % n)
        with open(os.path.join(ARCHIVE, fn), encoding="utf-8") as fh:
            rows = json.load(fh)
        if len(rows) < MIN_LIST:
            continue
        ref = fn[:-5]
        rows.sort(key=lambda r: (-r["score"], r["artist_mbid"]))
        arr, sco = array.array("i"), array.array("d")
        for r in rows:
            m = r["artist_mbid"]
            arr.append(idx(m))
            sco.append(r["score"])
            if m not in names:
                names[m] = r["name"]
        arm_a[ref] = (arr, sco)
        idx(ref)
    log("arm A: %d reference artists (list >= %d)" % (len(arm_a), MIN_LIST))

    # --- arm B: the adopted artifact ---
    sys.path.insert(0, os.path.join(os.getcwd(), "src"))
    from artistpath_api.graph_store import GraphStore
    g = GraphStore.load(GRAPH)
    if g.source_sha256 and g.source_sha256 != GRAPH_SHA:
        raise SystemExit("artifact sha mismatch: %s" % g.source_sha256)
    arm_b = {}
    for i in range(g.artist_count):
        nb = g.neighbours_of(i)
        if len(nb) < MIN_LIST:
            continue
        nb = sorted(nb, key=lambda t: (-t[1], g.mbids[t[0]]))
        arr, sco = array.array("i"), array.array("d")
        for j, s in nb:
            m = g.mbids[j]
            arr.append(idx(m))
            sco.append(s)
            if m not in names:
                names[m] = g.names[j]
        arm_b[g.mbids[i]] = (arr, sco)
        idx(g.mbids[i])
    log("arm B: %d reference artists (degree >= %d)" % (len(arm_b), MIN_LIST))
    return arm_a, arm_b, idx_of, mbid_of, names


def build_counts(needed_mbids):
    if os.path.exists(COUNTS_CACHE):
        log("counts: loading cache")
        with gzip.open(COUNTS_CACHE, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    log("counts: streaming the release-group dump (~2-3 min)")
    counts = {}
    n = 0
    with open(DUMP, encoding="utf-8") as fh:
        for line in fh:
            n += 1
            if n % 500000 == 0:
                log("   ...%d release-groups" % n)
            try:
                d = json.loads(line)
            except ValueError:
                continue
            for credit in d.get("artist-credit", []):
                aid = credit.get("artist", {}).get("id")
                if aid is not None and aid in needed_mbids:
                    counts[aid] = counts.get(aid, 0) + 1
    log("counts: %d release-groups scanned, %d needed MBIDs have >=1" % (n, len(counts)))
    with gzip.open(COUNTS_CACHE, "wt", encoding="utf-8") as fh:
        json.dump(counts, fh)
    return counts


def load_artist_existence(needed):
    """MBIDs from `needed` present in the MusicBrainz artist dump, so TCR-G2
    can tell a real artist with no releases from an MBID that is gone."""
    if os.path.exists(EXISTS_CACHE):
        log("existence: loading cache")
        with gzip.open(EXISTS_CACHE, "rt", encoding="utf-8") as fh:
            return set(json.load(fh))
    log("existence: streaming the artist dump (~2-3 min)")
    found, n = set(), 0
    with open(ARTIST_DUMP, encoding="utf-8") as fh:
        for line in fh:
            n += 1
            if n % 500000 == 0:
                log("   ...%d artists" % n)
            try:
                aid = json.loads(line).get("id")
            except ValueError:
                continue
            if aid in needed:
                found.add(aid)
    log("existence: %d artists scanned, %d of %d needed MBIDs exist"
        % (n, len(found), len(needed)))
    with gzip.open(EXISTS_CACHE, "wt", encoding="utf-8") as fh:
        json.dump(sorted(found), fh)
    return found


def main():
    out = {"governing": ("docs/superpowers/specs/"
                         "2026-08-06-thin-catalogue-rerun-preregistration.md"),
           "predecessor_void_run": "builder/analysis/2026-08-06-tce-thin-catalogue/",
           "artifact_sha256": GRAPH_SHA}

    # ------------------------------------------------------- phase 0: anchors
    with open(ANCHORS, encoding="utf-8") as fh:
        anchors = json.load(fh)
    gate = {}
    for key, (blo, bhi) in PREREG_BANDS.items():
        row = anchors["candidates"][key]
        if not row["unambiguous"]:
            raise SystemExit("%s is not unambiguous in the committed anchors" % key)
        live = row["live_release_group_count"]
        if band_for(live) != (blo, bhi):
            raise SystemExit("band drift for %s: prereg %s vs anchors-derived %s"
                             % (key, (blo, bhi), band_for(live)))
        gate[key] = {"mbid": row["mbid"], "name": row["name"], "live": live,
                     "band": (blo, bhi)}
    with open(LL_SOURCE, encoding="utf-8") as fh:
        llsrc = json.load(fh)
    ll_report = {k: {"mbid": llsrc["subjects"][k]["mbid"],
                     "label": llsrc["subjects"][k]["label"]}
                 for k in ("laura_lee_khruangbin", "laura_lee_soul")}
    out["anchor_source"] = os.path.basename(ANCHORS)
    out["laura_lee_source"] = LL_SOURCE

    arm_a, arm_b, idx_of, mbid_of, names = load_reference_sets()
    needed = set(idx_of)
    for c in gate.values():
        needed.add(c["mbid"])
    for c in ll_report.values():
        needed.add(c["mbid"])
    log("catalogue size needed for %d distinct MBIDs (incl. gate anchors)" % len(needed))
    counts = build_counts(needed)

    cnt = array.array("i", [-1] * len(mbid_of))
    for m, c in counts.items():
        i = idx_of.get(m)
        if i is not None:
            cnt[i] = c

    # ---------------------------------------------------------- phase 3: G1
    log("phase 3: TCR-G1, first and alone -- externally anchored bands")
    g1 = {"anchor_source": os.path.basename(ANCHORS), "cells": {}, "passed": True}
    for key, c in gate.items():
        measured = counts.get(c["mbid"], 0)
        blo, bhi = c["band"]
        ok = blo <= measured <= bhi
        g1["cells"][key] = {"mbid": c["mbid"], "name": c["name"],
                            "live_2026_08_06": c["live"],
                            "required_band": [blo, bhi],
                            "dump_release_groups": measured, "pass": ok}
        g1["passed"] &= ok
        log("   %-22s live=%-4d band=[%d,%d]  dump=%-4d %s"
            % (key, c["live"], blo, bhi, measured, "PASS" if ok else "FAIL"))
    out["TCR_G1"] = g1

    # Both Laura Lees: REPORTED run state, adjudicating nothing (prereg §3).
    out["laura_lee_reported_run_state"] = {
        k: {"mbid": v["mbid"], "label": v["label"],
            "dump_release_groups": counts.get(v["mbid"], 0),
            "gate_cell": False,
            "reason": ("known MusicBrainz mis-filing between the two Laura Lees "
                       "(../2026-08-06-tce-thin-catalogue/miscredit.json) "
                       "contaminates them as ground truth")}
        for k, v in ll_report.items()}
    for k, v in out["laura_lee_reported_run_state"].items():
        log("   reported (not a gate cell): %-22s dump=%d" % (k, v["dump_release_groups"]))

    if not g1["passed"]:
        out["verdict"] = "VOID -- TCR-G1 failed. No outcome computed."
        json.dump(out, open(RESULT, "w", encoding="utf-8"), indent=1)
        log("VOID: TCR-G1 failed. Stopping before any outcome value.")
        return

    # ------------------------------------------------- phase 4: TCR-G2
    exists = load_artist_existence(needed)
    for i in range(len(mbid_of)):
        if cnt[i] < 0:
            cnt[i] = 0

    resolved = array.array("b", [1 if mbid_of[i] in exists else 0
                                 for i in range(len(mbid_of))])
    seen = tot = 0
    for _ref, (arr, _sco) in arm_a.items():
        tot += len(arr)
        seen += sum(resolved[j] for j in arr)
    coverage = seen / tot
    out["TCR_G2"] = {"coverage": round(coverage, 6), "floor": COVERAGE_FLOOR,
                     "passed": coverage >= COVERAGE_FLOOR,
                     "arm_a_neighbour_slots": tot, "resolved_slots": seen,
                     "basis": "presence in the MusicBrainz artist JSON dump"}
    log("phase 4: TCR-G2 coverage %.5f over %d arm-A neighbour slots -> %s"
        % (coverage, tot, "PASS" if coverage >= COVERAGE_FLOOR else "FAIL"))
    if coverage < COVERAGE_FLOOR:
        out["verdict"] = "VOID -- TCR-G2 coverage below floor. No outcome computed."
        json.dump(out, open(RESULT, "w", encoding="utf-8"), indent=1)
        log("VOID: TCR-G2 failed. Stopping before any outcome value.")
        return

    # Unresolved neighbours leave both numerator and denominator; downstream
    # quantities therefore use POST-exclusion lengths by construction
    # (mitigation 3). Scores travel with their entries so the tie rule sees
    # the filtered list.
    for refs in (arm_a, arm_b):
        for ref in list(refs):
            arr, sco = refs[ref]
            keep = [k for k in range(len(arr)) if resolved[arr[k]]]
            refs[ref] = (array.array("i", [arr[k] for k in keep]),
                         array.array("d", [sco[k] for k in keep]))
    dropped_a = sum(1 for _r, (a, _s) in arm_a.items() if len(a) < MIN_LIST)
    for refs in (arm_a, arm_b):
        for ref in [r for r, (a, _s) in refs.items() if len(a) < MIN_LIST]:
            del refs[ref]
    log("   post-exclusion: arm A %d refs (%d fell below the floor), arm B %d"
        % (len(arm_a), dropped_a, len(arm_b)))
    out["TCR_G2"]["arm_a_refs_lost_to_exclusion"] = dropped_a

    thin = array.array("b", [1 if (resolved[i] and cnt[i] == 0) else 0
                             for i in range(len(mbid_of))])

    # --------------------------------------- phase 5: run state, PER ARM
    log("phase 5: run-state per arm, before any x_R is read")
    runstate = {}
    per_arm_lt = {}
    for arm, refs in (("A", arm_a), ("B", arm_b)):
        LT, ties = [], 0
        for ref, (arr, sco) in refs.items():
            L = len(arr)
            T = sum(thin[j] for j in arr)
            LT.append((ref, L, T))
            if top_slots(sco)[0] is None:
                ties += 1
        per_arm_lt[arm] = LT
        n = len(LT)
        base = sum(T for _r, _L, T in LT) / sum(L for _r, L, _T in LT)
        pinned = sum(1 for _r, _L, T in LT if T == 0) / n
        C = statistics.median(ceiling_term(L, T, TOP_K) for _r, L, T in LT)
        c5null = sum(c5_null_for(L, T, TOP_K) for _r, L, T in LT) / n
        runstate[arm] = {
            "reference_artists": n,
            "thin_base_rate": round(base, 6),
            "TCR_G3_share_T_eq_0": round(pinned, 6),
            "TCR_G3_bars_C1_read": pinned > 0.5,
            "ceiling_C": round(C, 6),
            "C1_bands": {"enriched_at": round(0.50 * C, 6),
                         "indeterminate_at": round(0.25 * C, 6),
                         "no_resolution": C < 0.10},
            "TCR_C5_null": round(c5null, 6),
            "list_len_median": statistics.median(L for _r, L, _T in LT),
            "rank10_boundary_ties_post_exclusion": ties,
        }
        log("   arm %s: n=%d base=%.5f  T=0 share=%.4f  C=%.4f  C5null=%.4f  ties=%d%s"
            % (arm, n, base, pinned, C, c5null, ties,
               "   *** TCR-G3 BARS C1 ***" if pinned > 0.5 else ""))
    json.dump(runstate, open(RUNSTATE, "w", encoding="utf-8"), indent=1)
    log("phase 5: written to %s" % os.path.basename(RUNSTATE))

    # --------------------------------------- phase 6: outcomes (reload first)
    runstate = json.load(open(RUNSTATE, encoding="utf-8"))
    log("phase 6: run-state reloaded from disk; computing outcomes")
    out["run_state"] = runstate
    out["outcomes"] = {}
    contrib = {}
    thin_by_thresh = {t: array.array("b", [1 if (resolved[i] and cnt[i] <= t) else 0
                                           for i in range(len(mbid_of))])
                      for t in (1, 2, 5, 10)}
    for arm, refs in (("A", arm_a), ("B", arm_b)):
        rs = runstate[arm]
        deltas, mids, sx, sex, c5mass = [], [], 0.0, 0.0, 0.0
        rows = []
        grad_deltas = {t: [] for t in thin_by_thresh}
        for ref, L, T in per_arm_lt[arm]:
            arr, sco = refs[ref]
            members_thin = [thin[j] for j in arr]
            ex, dist = tie_stats(members_thin, sco)
            d = ex / TOP_K - (T - ex) / (L - TOP_K)
            deltas.append(d)
            EM = sum(p * mid_p(L, T, TOP_K, x) for x, p in dist)
            mids.append(EM)
            sx += ex
            sex += TOP_K * T / L
            hitmass = sum(p for x, p in dist if (1.0 - mid_p(L, T, TOP_K, x)) <= 0.05)
            c5mass += hitmass
            rows.append((EM, ex, T, L, ref))
            for t, tarr in thin_by_thresh.items():
                mt = [tarr[j] for j in arr]
                Tt = sum(mt)
                ext, _ = tie_stats(mt, sco)
                grad_deltas[t].append(ext / TOP_K - (Tt - ext) / (L - TOP_K))
        n = len(deltas)
        C1 = statistics.median(deltas)
        C3 = sum(mids) / n
        C4 = (sx / sex) if sex else float("nan")
        C5 = c5mass / n
        C = rs["ceiling_C"]

        if rs["TCR_G3_bars_C1_read"]:
            c1band = "no_read_licensed (TCR-G3: over half of reference artists have T_R=0)"
        elif rs["C1_bands"]["no_resolution"]:
            c1band = "no_resolution (C < 0.10)"
        elif C1 >= 0.50 * C:
            c1band = "enriched"
        elif C1 >= 0.25 * C:
            c1band = "indeterminate"
        elif C1 > -0.25 * C:
            c1band = "null"
        else:
            c1band = "depleted"
        c3band = ("enriched" if C3 >= 0.55 else "indeterminate" if C3 >= 0.52
                  else "null" if C3 > 0.48 else "depleted")
        c4band = ("enriched" if C4 >= 1.5 else "indeterminate" if C4 >= 1.2
                  else "null" if C4 > 0.8 else "depleted")
        ratio = C5 / rs["TCR_C5_null"] if rs["TCR_C5_null"] else float("inf")

        out["outcomes"][arm] = {
            "TCR_C1_median_delta": round(C1, 6), "TCR_C1_band": c1band,
            "TCR_C3_mean_midp": round(C3, 6), "TCR_C3_band": c3band,
            "TCR_C4_excess_ratio": round(C4, 6), "TCR_C4_band": c4band,
            "TCR_C5_share": round(C5, 6),
            "TCR_C5_null": rs["TCR_C5_null"],
            "TCR_C5_ratio_to_null": round(ratio, 4),
            "TCR_C5_concentrated": ratio >= 2.0,
            "delta_distribution": {
                "mean": round(sum(deltas) / n, 6),
                "p10": round(statistics.quantiles(deltas, n=10)[0], 6),
                "p90": round(statistics.quantiles(deltas, n=10)[-1], 6),
                "share_positive": round(sum(1 for d in deltas if d > 1e-12) / n, 6),
                "share_zero": round(sum(1 for d in deltas if abs(d) <= 1e-12) / n, 6),
            },
            "descriptive_gradient_median_delta": {
                ("thin_le_%d" % t): round(statistics.median(g), 6)
                for t, g in grad_deltas.items()},
        }
        log("   arm %s: C1=%+.4f [%s]  C3=%.4f [%s]  C4=%.3f [%s]  C5=%.4f (null %.4f, x%.2f)"
            % (arm, C1, c1band, C3, c3band, C4, c4band, C5, rs["TCR_C5_null"], ratio))
        rows.sort(key=lambda r: (-r[0], -r[1]))
        contrib[arm] = rows[:20]

    # ------------------------------ phase 7: mitigation 2, the eyeball dump
    log("phase 7: top-20 contributor dump for the eyeball read")
    eye = {}
    for arm, rowlist in contrib.items():
        refs = arm_a if arm == "A" else arm_b
        eye[arm] = []
        for EM, ex, T, L, ref in rowlist:
            arr, sco = refs[ref]
            eye[arm].append({
                "reference_mbid": ref,
                "reference_name": names.get(ref, "?"),
                "expected_mid_p": round(EM, 6), "expected_thin_in_top10": round(ex, 4),
                "thin_total": T, "list_len": L,
                "top10": [{"rank": i + 1, "mbid": mbid_of[j],
                           "name": names.get(mbid_of[j], "?"),
                           "score": sco[i],
                           "release_groups": cnt[j],
                           "thin": bool(thin[j])}
                          for i, j in enumerate(arr[:TOP_K])],
            })
    json.dump(eye, open(EYEBALL, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    out["verdict"] = "computed"
    json.dump(out, open(RESULT, "w", encoding="utf-8"), indent=1)
    log("wrote %s, %s, %s" % (os.path.basename(RESULT), os.path.basename(RUNSTATE),
                              os.path.basename(EYEBALL)))


if __name__ == "__main__":
    main()
