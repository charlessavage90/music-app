"""`TCE-` — do artists with almost nothing of their own recorded get artificially
strong links?

Governing document:
  docs/superpowers/specs/2026-08-06-thin-catalogue-edge-preregistration.md
  committed 31166c9, amended by TCE-AM1 (dfe8a63) and TCE-AM2 (b757ea1),
  ALL BEFORE this script computed any outcome value.

Execution order is fixed by the prereg §6 and is ENFORCED STRUCTURALLY here,
not just intended:

  phase 0  provenance: TCE-G1 MBIDs read from a COMMITTED source (TCE-AM2)
  phase 1  reference sets + the MBIDs whose catalogue size is needed
  phase 2  one streaming pass over the MB release-group dump -> counts
  phase 3  TCE-G1  instrument validation, FIRST AND ALONE. Fail => VOID.
  phase 4  TCE-G2  coverage floor. Below 0.95 => VOID.
  phase 5  ALL run-state quantities, PER ARM (TCE-AM2), WRITTEN TO DISK
  phase 6  outcomes -- and it RELOADS phase 5's file first, so no outcome can
           have informed a run-state quantity
  phase 7  the three TCE-AM1 mitigations, incl. the top-20 eyeball dump

Run from `api/` (it loads the adopted artifact through the API's GraphStore):

  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
    ../builder/analysis/2026-08-06-tce-thin-catalogue/tce_run.py

The dump pass is cached to rg_counts.json.gz; re-runs skip it.

This directory OWNS its figures. Cite it; never restate them.
"""
import array
import gzip
import json
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
# TCE-AM2: the prereg's TCE-G1 table shows MBIDs ellipsis-truncated. The
# authoritative full values come from this COMMITTED file, and the source is
# recorded in the output.
G1_SOURCE = "../builder/analysis/2026-08-06-laura-lee-closure/ll_closure.json"

COUNTS_CACHE = os.path.join(HERE, "rg_counts.json.gz")
EXISTS_CACHE = os.path.join(HERE, "artist_exists.json.gz")
RUNSTATE = os.path.join(HERE, "tce_runstate.json")
RESULT = os.path.join(HERE, "tce_result.json")
EYEBALL = os.path.join(HERE, "tce_eyeball_top20.json")

MIN_LIST = 30          # prereg §1
TOP_K = 10             # prereg §4.1
COVERAGE_FLOOR = 0.95  # TCE-G2

# TCE-G1 required answers (prereg §3). Keys index into G1_SOURCE's "subjects".
G1_REQUIRED = {
    "laura_lee_khruangbin": ("== 0", lambda c: c == 0),
    "laura_lee_soul": (">= 20", lambda c: c >= 20),
    "leon_bridges": (">= 5", lambda c: c >= 5),
    "khruangbin": (">= 5", lambda c: c >= 5),
}


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
    """M_R = P(X < x) + 0.5 P(X = x). Null mean is exactly 0.5 (TCE-C3)."""
    lo, hi = max(0, T - (L - k)), min(k, T)
    below = sum(hyp_pmf(L, T, k, j) for j in range(lo, x))
    return below + 0.5 * hyp_pmf(L, T, k, x)


def c5_null_for(L, T, k):
    """P_null(upper-tail mid-p <= 0.05) for one artist. TCE-C5's null is the
    mean of this across the census -- base-rate dependent, so computed from
    (L_R, T_R) BEFORE any x_R is read (TCE-AM1/AM2)."""
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


def delta(L, T, k, x):
    return x / k - (T - x) / (L - k)


# ------------------------------------------------------------------ phase 1-2
def load_reference_sets():
    """Returns (arm -> {mbid: array of neighbour idx in rank order}), mbid<->idx."""
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
        arr = array.array("i")
        for r in rows:                       # archive order IS score order
            m = r["artist_mbid"]
            arr.append(idx(m))
            if m not in names:
                names[m] = r["name"]
        arm_a[ref] = arr
        idx(ref)
    log("arm A: %d reference artists (list >= %d)" % (len(arm_a), MIN_LIST))

    # --- arm B: the adopted artifact ---
    sys.path.insert(0, os.path.join(os.getcwd(), "src"))
    from artistpath_api.graph_store import GraphStore
    g = GraphStore.load(GRAPH)
    if g.source_sha256 and g.source_sha256 != GRAPH_SHA:
        raise SystemExit("artifact sha mismatch: %s" % g.source_sha256)
    arm_b, ties = {}, 0
    for i in range(g.artist_count):
        nb = sorted(g.neighbours_of(i), key=lambda t: -t[1])
        if len(nb) < MIN_LIST:
            continue
        # §0.1: p99_log_clip is non-monotone at the top, so ties concentrate
        # exactly where this probe looks. Count boundary-spanning ties.
        if len(nb) > TOP_K and nb[TOP_K - 1][1] == nb[TOP_K][1]:
            ties += 1
        arr = array.array("i")
        for j, _s in nb:
            m = g.mbids[j]
            arr.append(idx(m))
            if m not in names:
                names[m] = g.names[j]
        arm_b[g.mbids[i]] = arr
        idx(g.mbids[i])
    log("arm B: %d reference artists (degree >= %d), %d with a rank-10 boundary tie"
        % (len(arm_b), MIN_LIST, ties))
    return arm_a, arm_b, idx_of, mbid_of, names, ties


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
    """MBIDs from `needed` that exist in the MusicBrainz artist dump.

    Establishes existence so that TCE-G2 can tell a real artist with no
    releases from an MBID that is simply gone.
    """
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
                         "2026-08-06-thin-catalogue-edge-preregistration.md"),
           "amendments_in_force": ["TCE-AM1", "TCE-AM2"],
           "artifact_sha256": GRAPH_SHA}

    arm_a, arm_b, idx_of, mbid_of, names, ties_b = load_reference_sets()
    needed = set(idx_of)
    log("catalogue size needed for %d distinct MBIDs" % len(needed))
    counts = build_counts(needed)

    # count by index, -1 = unresolved (absent from the dump entirely)
    cnt = array.array("i", [-1] * len(mbid_of))
    for m, c in counts.items():
        i = idx_of.get(m)
        if i is not None:
            cnt[i] = c
    # An MBID present in the dump with zero credited release-groups never
    # appears in `counts`. Absence from the dump and zero credits are NOT the
    # same thing, and TCE-G2 turns on the difference -- so resolve it below.

    # ---------------------------------------------------------- phase 3: G1
    log("phase 3: TCE-G1, first and alone")
    with open(G1_SOURCE, encoding="utf-8") as fh:
        g1src = json.load(fh)
    g1 = {"mbid_source": G1_SOURCE, "cells": {}, "passed": True}
    for key, (desc, test) in G1_REQUIRED.items():
        mbid = g1src["subjects"][key]["mbid"]
        c = counts.get(mbid, 0)
        ok = test(c)
        g1["cells"][key] = {"mbid": mbid, "label": g1src["subjects"][key]["label"],
                            "required": desc, "release_groups": c, "pass": ok}
        g1["passed"] &= ok
        log("   %-24s %-40s rg=%-5d required %-6s %s"
            % (key, g1src["subjects"][key]["label"][:40], c, desc,
               "PASS" if ok else "FAIL"))
    out["TCE_G1"] = g1
    if not g1["passed"]:
        out["verdict"] = "VOID -- TCE-G1 failed. No outcome computed."
        json.dump(out, open(RESULT, "w", encoding="utf-8"), indent=1)
        log("VOID: TCE-G1 failed. Stopping before any outcome value.")
        return

    # ------------------------------------------------- phase 4: TCE-G2
    # An artist with zero release-groups is ABSENT from the release-group dump,
    # so that dump alone cannot tell "no releases" from "this MBID does not
    # exist". It is not a hypothetical difference: this archive is known to
    # carry deleted MBIDs (the no-name artists dropped 2026-07-29, all three of
    # which MusicBrainz reports as not found). Treating those as thin would
    # inflate the base rate with non-artists -- exactly the failure TCE-AM1's
    # cost section warns the mean-based criteria are vulnerable to. So
    # existence is established from the ARTIST dump, a second streaming pass.
    exists = load_artist_existence(needed)
    for i in range(len(mbid_of)):
        if cnt[i] < 0:
            cnt[i] = 0

    resolved = array.array("b", [1 if mbid_of[i] in exists else 0
                                 for i in range(len(mbid_of))])
    seen = tot = 0
    for _ref, arr in arm_a.items():
        tot += len(arr)
        seen += sum(resolved[j] for j in arr)
    coverage = seen / tot
    out["TCE_G2"] = {"coverage": round(coverage, 6), "floor": COVERAGE_FLOOR,
                     "passed": coverage >= COVERAGE_FLOOR,
                     "arm_a_neighbour_slots": tot,
                     "resolved_slots": seen,
                     "basis": "presence in the MusicBrainz artist JSON dump"}
    log("phase 4: TCE-G2 coverage %.5f over %d arm-A neighbour slots -> %s"
        % (coverage, tot, "PASS" if coverage >= COVERAGE_FLOOR else "FAIL"))
    if coverage < COVERAGE_FLOOR:
        out["verdict"] = "VOID -- TCE-G2 coverage below floor. No outcome computed."
        json.dump(out, open(RESULT, "w", encoding="utf-8"), indent=1)
        log("VOID: TCE-G2 failed. Stopping before any outcome value.")
        return

    # Unresolved neighbours are excluded from BOTH numerator and denominator
    # (prereg §3) -- which also discharges TCE-AM1 mitigation 3, since the
    # hypergeometric is then fed the POST-exclusion list length by construction.
    for refs in (arm_a, arm_b):
        for ref in list(refs):
            refs[ref] = array.array("i", [j for j in refs[ref] if resolved[j]])
    dropped_a = sum(1 for r, a in arm_a.items() if len(a) < MIN_LIST)
    for refs in (arm_a, arm_b):
        for ref in [r for r, a in refs.items() if len(a) < MIN_LIST]:
            del refs[ref]
    log("   post-exclusion: arm A %d refs (%d fell below the floor), arm B %d"
        % (len(arm_a), dropped_a, len(arm_b)))
    out["TCE_G2"]["arm_a_refs_lost_to_exclusion"] = dropped_a

    thin = array.array("b", [1 if (resolved[i] and cnt[i] == 0) else 0
                             for i in range(len(mbid_of))])

    # --------------------------------------- phase 5: run state, PER ARM
    log("phase 5: run-state per arm (TCE-AM2), before any x_R")
    runstate = {}
    per_arm_lt = {}
    for arm, refs in (("A", arm_a), ("B", arm_b)):
        LT = []
        for ref, arr in refs.items():
            L = len(arr)
            T = sum(thin[j] for j in arr)
            LT.append((ref, L, T))
        per_arm_lt[arm] = LT
        n = len(LT)
        base = sum(T for _r, _L, T in LT) / sum(L for _r, L, _T in LT)
        pinned = sum(1 for _r, _L, T in LT if T == 0) / n
        C = statistics.median(ceiling_term(L, T, TOP_K) for _r, L, T in LT)
        c5null = sum(c5_null_for(L, T, TOP_K) for _r, L, T in LT) / n
        runstate[arm] = {
            "reference_artists": n,
            "thin_base_rate": round(base, 6),
            "TCE_G3_share_T_eq_0": round(pinned, 6),
            "TCE_G3_bars_C1_read": pinned > 0.5,
            "ceiling_C": round(C, 6),
            "C1_bands": {"enriched_at": round(0.50 * C, 6),
                         "indeterminate_at": round(0.25 * C, 6),
                         "no_resolution": C < 0.10},
            "TCE_C5_null": round(c5null, 6),
            "list_len_median": statistics.median(L for _r, L, _T in LT),
        }
        log("   arm %s: n=%d base=%.5f  T=0 share=%.4f  C=%.4f  C5null=%.4f%s"
            % (arm, n, base, pinned, C, c5null,
               "   *** TCE-G3 BARS C1 ***" if pinned > 0.5 else ""))
    runstate["arm_B_rank10_boundary_ties"] = ties_b
    json.dump(runstate, open(RUNSTATE, "w", encoding="utf-8"), indent=1)
    log("phase 5: written to %s" % os.path.basename(RUNSTATE))

    # --------------------------------------- phase 6: outcomes (reload first)
    runstate = json.load(open(RUNSTATE, encoding="utf-8"))
    log("phase 6: run-state reloaded from disk; computing outcomes")
    out["run_state"] = runstate
    out["outcomes"] = {}
    contrib = {}
    for arm, refs in (("A", arm_a), ("B", arm_b)):
        rs = runstate[arm]
        deltas, mids, sx, sex, c5hits = [], [], 0, 0.0, 0
        rows = []
        for ref, L, T in per_arm_lt[arm]:
            arr = refs[ref]
            x = sum(thin[j] for j in arr[:TOP_K])
            deltas.append(delta(L, T, TOP_K, x))
            M = mid_p(L, T, TOP_K, x)
            mids.append(M)
            sx += x
            sex += TOP_K * T / L
            if (1.0 - M) <= 0.05:
                c5hits += 1
            rows.append((M, x, T, L, ref))
        n = len(deltas)
        C1 = statistics.median(deltas)
        C3 = sum(mids) / n
        C4 = (sx / sex) if sex else float("nan")
        C5 = c5hits / n
        C = rs["ceiling_C"]

        if rs["TCE_G3_bars_C1_read"]:
            c1band = "no_read_licensed (TCE-G3: over half of reference artists have T_R=0)"
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
        ratio = C5 / rs["TCE_C5_null"] if rs["TCE_C5_null"] else float("inf")

        out["outcomes"][arm] = {
            "TCE_C1_median_delta": round(C1, 6), "TCE_C1_band": c1band,
            "TCE_C3_mean_midp": round(C3, 6), "TCE_C3_band": c3band,
            "TCE_C4_excess_ratio": round(C4, 6), "TCE_C4_band": c4band,
            "TCE_C5_share": round(C5, 6),
            "TCE_C5_null": rs["TCE_C5_null"],
            "TCE_C5_ratio_to_null": round(ratio, 4),
            "TCE_C5_concentrated": ratio >= 2.0,
            "delta_distribution": {
                "mean": round(sum(deltas) / n, 6),
                "p10": round(statistics.quantiles(deltas, n=10)[0], 6),
                "p90": round(statistics.quantiles(deltas, n=10)[-1], 6),
                "share_positive": round(sum(1 for d in deltas if d > 0) / n, 6),
                "share_zero": round(sum(1 for d in deltas if d == 0) / n, 6),
            },
        }
        log("   arm %s: C1=%+.4f [%s]  C3=%.4f [%s]  C4=%.3f [%s]  C5=%.4f (null %.4f, x%.2f)"
            % (arm, C1, c1band, C3, c3band, C4, c4band, C5, rs["TCE_C5_null"], ratio))
        rows.sort(key=lambda r: (-r[0], -r[1]))
        contrib[arm] = rows[:20]

    # ------------------------------ phase 7: mitigation 2, the eyeball dump
    log("phase 7: top-20 contributor dump for the eyeball read")
    eye = {}
    for arm, rows in contrib.items():
        refs = arm_a if arm == "A" else arm_b
        eye[arm] = []
        for M, x, T, L, ref in rows:
            arr = refs[ref]
            eye[arm].append({
                "reference_mbid": ref,
                "reference_name": names.get(ref, "?"),
                "mid_p": round(M, 6), "thin_in_top10": x,
                "thin_total": T, "list_len": L,
                "top10": [{"rank": i + 1, "mbid": mbid_of[j],
                           "name": names.get(mbid_of[j], "?"),
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
