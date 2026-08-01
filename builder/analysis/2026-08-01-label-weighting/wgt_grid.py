"""The `WGT-` grid: instrument checks, the fame-leak gate, and the 15 cells.

Governing document:
`docs/superpowers/specs/2026-08-01-label-weighting-probe-preregistration.md`.
DIAGNOSTIC ONLY: no `TAS-` criterion, bar, vocabulary or substrate changes,
nothing is adopted, and every committed `TAS-` figure stands on plain Jaccard.

ORDER, per the pre-registration §9: the four instrument checks (`WGT-0a`-`0d`)
must pass before anything else is read; `WGT-1` (the fame-leak gate) runs and
FIXES the evidence table before any agreement cell; then the fifteen cells.
`EV-R` is absent here by construction -- it exists only if `WGT-4` admits it,
and the `evidence⁺` re-run is a separate invocation with `--with-release`.

ONE RESOLUTION PATH. Every measure -- plain, identity, rarity, evidence, and
the singleton-excluded diagnostic -- is computed in a single pass per frame
from shared intersection/union sets, with the §1 neutral rule recomputed per
measure per artist through the same median-or-global-fallback shape the
committed scripts use. Absolute agreement values are NOT comparable across
cells (the neutral is a quantile of each cell's own distribution); every
cross-cell read below is an ordering, a turnover, or a sign.

EVIDENCE IS FRAME-INDEPENDENT, an implementation clarification of the table's
"(genre or style, per frame)" parenthetical: `e(a, l)` is computed once per
(artist, label) over the union of all sources, and frames only select which
labels participate. This keeps every frame isolation one-knob -- membership
only -- which the parenthetical's literal reading would have broken.

`EV-G` counts release groups whose genres OR tags carry the label (attributable
only): RG-level tags are the same namespace as RG-level genres, and the genre
row is the whitelisted subset, so counting only `g` would undercount support
for labels MusicBrainz has not yet whitelisted.

Run from `builder/` (~30-75 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-01-label-weighting/wgt_grid.py \
        --capture <path>/alge_capture.npz
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (_TAS, _REL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from tas_common import GLOBAL_NEUTRAL_FALLBACK, fame_frame, graph_mbids  # noqa: E402
from tas_frame_eval import acting_slot_share  # noqa: E402
from tas_frame_split import five_frames  # noqa: E402
from tas_select import LAMBDAS, edge_turnover, mask_tag  # noqa: E402
from tas_signal import iqr  # noqa: E402
from tas_weighting import build_fields, idf_table, spearman  # noqa: E402
from td_turnover import Capture, mutual_undirected  # noqa: E402

OUT = HERE / "wgt_grid.json"
VOTES = HERE / "wgt_artist_votes.json"
RELEASE_RAW = HERE / "wgt_release_raw.json"

# Execution log §14.1's recorded capture sha -- WGT-0d.
CAPTURE_SHA = "893609e97fb31f2a679a5e8005f7488d771414658d671a9eee979a757b550d90"

S_CAP = 8.0
LEAK_BAR = 0.50          # WGT-1
SCHEMES = ("plain", "rarity", "evidence")
FRAMES = ("W0", "W1", "W4", "W5", "W6")


# ---------------------------------------------------------------- evidence

def evidence_weights(with_release: bool) -> tuple[dict[str, dict[str, float]], dict]:
    """e(a, l) for every (artist, label) across all sources, plus WGT-1's gate.

    Returns the per-artist e-dicts and the leak reading that fixed the table.
    An ingredient crossing the leak bar DEGRADES TO PRESENCE -- the source
    never vanishes, its strength claim does (pre-registration §4).
    """
    from rel_artist_dump import OUT_INDEX as ARTIST_INDEX
    from rel_discogs import OUT_RAW as DISCOGS_RAW
    from rel_rg_dump import OUT_RAW as RG_RAW
    from tas_wikidata import OUT_RAW as WD_RAW

    votes = json.loads(VOTES.read_text(encoding="utf-8"))
    wd = json.loads(WD_RAW.read_text(encoding="utf-8"))
    rg = json.loads(RG_RAW.read_text(encoding="utf-8"))
    index = json.loads(ARTIST_INDEX.read_text(encoding="utf-8"))
    discogs = json.loads(DISCOGS_RAW.read_text(encoding="utf-8"))
    release = (json.loads(RELEASE_RAW.read_text(encoding="utf-8"))
               if with_release else {})

    from tas_common import norm_genre  # noqa: PLC0415 -- the one frozen normaliser

    mbids = graph_mbids()
    frame = fame_frame()

    # Per-artist per-source label masses.
    per: dict[str, dict[str, dict[str, float]]] = {}
    for m in mbids:
        src: dict[str, dict[str, float]] = {}
        src["A"] = {lab: max(float(v), 0.0)
                    for lab, v in (votes.get(m) or {}).items()}
        src["W"] = {norm_genre(g): 1.0
                    for g in ((wd.get(m) or {}).get("genres") or []) if norm_genre(g)}
        g_counts: Counter = Counter()
        for rec in rg.get(m) or []:
            if not rec.get("a"):
                continue
            for lab in set(rec.get("g") or []) | set(rec.get("t") or []):
                g_counts[lab] += 1
        src["G"] = dict(g_counts)
        did = (index.get(m) or {}).get("discogs")
        bucket = discogs.get(did or "") or {}
        src["D"] = {lab: 1.0
                    for lab in set(bucket.get("g") or []) | set(bucket.get("s") or [])}
        if with_release:
            src["R"] = {lab: float(n)
                        for lab, n in ((release.get(m) or {}).get("labels") or {}).items()}
        per[m] = src

    # WGT-1: leak per strength ingredient, labelled artists with a fame value.
    def leak_of(key: str) -> float | None:
        xs, ys = [], []
        for m, src in per.items():
            if m not in frame:
                continue
            mass = sum(src.get(key, {}).values())
            if any(src[k] for k in src):
                xs.append(frame[m])
                ys.append(mass)
        return spearman(np.array(xs), np.array(ys))

    leaks = {"EV-A_votes": leak_of("A"), "EV-G_rg_count": leak_of("G")}
    if with_release:
        leaks["EV-R_release_count"] = leak_of("R")
    degraded = {k for k, v in leaks.items() if v is not None and abs(v) >= LEAK_BAR}

    def strength(src: dict[str, dict[str, float]], lab: str) -> float:
        s = 0.0
        s += (1.0 if src["A"].get(lab) else 0.0) if "EV-A_votes" in degraded \
            else src["A"].get(lab, 0.0)
        s += src["W"].get(lab, 0.0)
        s += (1.0 if src["G"].get(lab) else 0.0) if "EV-G_rg_count" in degraded \
            else src["G"].get(lab, 0.0)
        s += src["D"].get(lab, 0.0)
        if "R" in src:
            s += (1.0 if src["R"].get(lab) else 0.0) \
                if "EV-R_release_count" in degraded else src["R"].get(lab, 0.0)
        return s

    fallbacks = 0
    e_all: dict[str, dict[str, float]] = {}
    for m, src in per.items():
        labs = set().union(*(src[k].keys() for k in src)) if src else set()
        e_m: dict[str, float] = {}
        for lab in labs:
            s = strength(src, lab)
            if s <= 0:
                s, fallbacks = 1.0, fallbacks + 1
            e_m[lab] = min(1.0, math.log1p(s) / math.log1p(S_CAP))
        e_all[m] = e_m
    gate = {
        "bar": LEAK_BAR,
        "spearman_vs_fame_labelled_artists": {
            k: (round(v, 4) if v is not None else None) for k, v in leaks.items()},
        "degraded_to_presence": sorted(degraded),
        "s0_fallbacks": fallbacks,
        "note": "FPC-9 caveat: computed where fame is measurable, blind exactly "
                "where the leak would matter most.",
    }
    return e_all, gate


def e_for(e_all: dict[str, dict[str, float]], m: str, labels: set[str]) -> dict[str, float]:
    """Frame-membership filter over the frame-independent e(a, l), with the s=1
    floor for frame labels no source explains (transport mismatches)."""
    base = e_all.get(m, {})
    floor = math.log1p(1.0) / math.log1p(S_CAP)
    return {lab: base.get(lab, floor) for lab in labels}


# ---------------------------------------------------------------- the pass

def frame_pass(cap: Capture, labels: dict[str, set[str]], idf: dict[str, float],
               df: Counter, e_all: dict[str, dict[str, float]]) -> dict:
    """All measures for one frame in a single pass over the capture slots."""
    n9 = math.log1p(S_CAP)
    sets = [labels.get(m, set()) for m in cap.mbids]
    evs = [e_for(e_all, m, labels.get(m, set())) for m in cap.mbids]

    measures = ("plain", "identity", "rarity", "evidence", "rarity_nosingle")
    fields = {k: np.empty(cap.total, dtype=np.float64) for k in measures}
    raw: dict[str, list[list[tuple[int, float]]]] = {k: [] for k in measures}
    strengths: list[list[float]] = []
    owners: list[int] = []
    singleton_den = total_den = 0.0
    identity_mismatch = 0

    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if lo == hi:
            continue
        own, e_u = sets[u], evs[u]
        vals: dict[str, list[float | None]] = {k: [] for k in measures}
        for pos in range(lo, hi):
            c = int(cap.s_cand[pos])
            cand, e_c = sets[c], evs[c]
            if not own or not cand:
                for k in measures:
                    vals[k].append(None)
                continue
            inter, union = own & cand, own | cand
            p = len(inter) / len(union)
            ident = math.fsum(1.0 for _ in inter) / math.fsum(1.0 for _ in union)
            if p != ident:
                identity_mismatch += 1
            r_un = sum(idf.get(x, 0.0) for x in union)
            r_in = sum(idf.get(x, 0.0) for x in inter)
            rar = (r_in / r_un) if r_un > 0 else None
            ev_un = sum(idf.get(x, 0.0) * max(e_u.get(x, 0.0), e_c.get(x, 0.0))
                        for x in union)
            ev_in = sum(idf.get(x, 0.0) * min(e_u[x], e_c[x]) for x in inter)
            ev = (ev_in / ev_un) if ev_un > 0 else None
            ns_un = sum(idf.get(x, 0.0) for x in union if df[x] > 1)
            ns_in = sum(idf.get(x, 0.0) for x in inter if df[x] > 1)
            ns = (ns_in / ns_un) if ns_un > 0 else None
            if r_un > 0:
                total_den += r_un
                singleton_den += sum(idf.get(x, 0.0) for x in union if df[x] == 1)
            for k, v in (("plain", p), ("identity", ident), ("rarity", rar),
                         ("evidence", ev), ("rarity_nosingle", ns)):
                vals[k].append(v)
        for k in measures:
            got = [(i, v) for i, v in enumerate(vals[k]) if v is not None]
            neutral = (statistics.median([v for _i, v in got]) if len(got) >= 2
                       else GLOBAL_NEUTRAL_FALLBACK)
            for i, v in enumerate(vals[k]):
                fields[k][lo + i] = neutral if v is None else v
            raw[k].append(got)
        strengths.append([float(cap.s_rank[pos]) for pos in range(lo, hi)])
        owners.append(u)
        if u % 15000 == 0:
            print(f"    pass {u}/{cap.n}", flush=True)

    return {"fields": fields, "raw": raw, "strengths": strengths, "owners": owners,
            "identity_mismatch": identity_mismatch,
            "singleton_union_mass_share": round(singleton_den / total_den, 4)
            if total_den else None,
            "n9": n9}


def describe(vals: list[float]) -> dict:
    a = np.array(vals)
    return {"artists": len(a), "median": round(float(np.median(a)), 4),
            "p10": round(float(np.percentile(a, 10)), 4),
            "share_below_0.99": round(float((a < 0.99).mean()), 4),
            "share_below_0.9": round(float((a < 0.9).mean()), 4)}


def spearman_pairs(pairs: list[tuple[float, float]]) -> float | None:
    x = np.array([a for a, _ in pairs])
    y = np.array([b for _, b in pairs])
    return spearman(x, y)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--with-release", action="store_true",
                    help="evidence-plus re-run, only after WGT-4 admits EV-R")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    # ---- WGT-0d: provenance ----
    digest = hashlib.sha256(Path(args.capture).read_bytes()).hexdigest()
    if digest != CAPTURE_SHA:
        raise SystemExit(f"WGT-0d FAILED: capture sha {digest} != recorded {CAPTURE_SHA}")
    print("WGT-0d PASS: capture sha matches the recorded value", flush=True)

    cap = Capture(Path(args.capture))
    frames = five_frames()
    fame = fame_frame()

    # ---- WGT-1 fixes the evidence table before any cell ----
    e_all, gate = evidence_weights(args.with_release)
    print(f"WGT-1: {gate['spearman_vs_fame_labelled_artists']} "
          f"degraded={gate['degraded_to_presence']}", flush=True)

    # ---- WGT-0b: the committed (W0, rarity) path, reproduced first ----
    committed = json.loads((_TAS / "tas_weighting.json").read_text(encoding="utf-8"))
    idf0, df0 = idf_table(frames["W0"], cap.n)
    t0 = time.time()
    plain0, weighted0, _ra, _rs = build_fields(cap, frames["W0"], idf0)
    print(f"  committed W0 fields in {(time.time() - t0) / 60:.1f} min", flush=True)
    rep_turnover = {}
    for lam in LAMBDAS:
        base = mutual_undirected(cap, mask_tag(cap, plain0, lam))
        arm = mutual_undirected(cap, mask_tag(cap, weighted0, lam))
        rep_turnover[str(lam)] = edge_turnover(base, arm)["turnover_share"]
    want = committed["C_does_it_reorder_and_does_the_map_change"][
        "selection_turnover_same_lambda_only_the_measure_differs"]
    for lam, share in rep_turnover.items():
        if abs(share - want[lam]["turnover_share"]) > 5e-5:
            raise SystemExit(f"WGT-0b FAILED at lambda={lam}: "
                             f"{share} != {want[lam]['turnover_share']}")
    print("WGT-0b PASS: committed W0 rarity turnovers reproduced at every lambda",
          flush=True)

    split_committed = json.loads(
        (_TAS / "tas_frame_split.json").read_text(encoding="utf-8"))

    results: dict = {"frames": {}}
    scorable_w0: set[int] | None = None

    for fname in FRAMES:
        print(f"[{fname}]", flush=True)
        idf, df = idf_table(frames[fname], cap.n)
        data = frame_pass(cap, frames[fname], idf, df, e_all)

        # ---- WGT-0a: identity, both halves ----
        if data["identity_mismatch"]:
            raise SystemExit(f"WGT-0a FAILED on {fname}: "
                             f"{data['identity_mismatch']} slot mismatches")
        for lam in LAMBDAS:
            mp = mask_tag(cap, data["fields"]["plain"], lam)
            mi = mask_tag(cap, data["fields"]["identity"], lam)
            if not np.array_equal(mp, mi):
                raise SystemExit(f"WGT-0a FAILED on {fname} selection at lambda={lam}")
        if fname == "W0":
            if not (np.array_equal(data["fields"]["plain"], plain0)
                    and np.array_equal(data["fields"]["rarity"], weighted0)):
                raise SystemExit("WGT-0b FAILED: generalized pass diverges from "
                                 "the committed build_fields on W0")
            print("  WGT-0b PASS: generalized pass == committed fields, elementwise",
                  flush=True)
        print(f"  WGT-0a PASS on {fname}", flush=True)

        # Fixed population: W0's scorable lists (owners with a computable spread).
        if scorable_w0 is None:
            scorable_w0 = {u for u, got in zip(data["owners"], data["raw"]["plain"])
                           if iqr([v for _i, v in got]) is not None}
            print(f"  fixed population: {len(scorable_w0)} lists", flush=True)

        frow: dict = {"cells": {}}
        frow["acting_slot_share"] = round(
            acting_slot_share(cap, frames[fname]), 4)

        for scheme, key in (("plain", "plain"), ("rarity", "rarity"),
                            ("evidence", "evidence"),
                            ("rarity_nosingle", "rarity_nosingle")):
            spreads, pairs = [], []
            for u, got, strength in zip(data["owners"], data["raw"][key],
                                        data["strengths"]):
                if u not in scorable_w0:
                    continue
                s = iqr([v for _i, v in got])
                if s is None:
                    continue
                spreads.append(s)
                # raw values only, paired with their slots' strengths -- the
                # committed signal_on shape; neutral-filled slots never pool.
                pairs.extend((strength[i], v) for i, v in got)
            cell = {
                "median_iqr": round(statistics.median(spreads), 4) if spreads else None,
                "spearman_vs_similarity": round(spearman_pairs(pairs), 4)
                if pairs else None,
            }
            if scheme != "plain":
                rhos, rhos_b, turn = [], [], {}
                pf, sf = data["fields"]["plain"], data["fields"][key]
                for u in range(cap.n):
                    lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
                    if hi - lo < 3:
                        continue
                    r = spearman(pf[lo:hi], sf[lo:hi])
                    if r is not None:
                        rhos.append(r)
                        if bool(cap.binds[u]):
                            rhos_b.append(r)
                for lam in LAMBDAS:
                    base = mutual_undirected(cap, mask_tag(cap, pf, lam))
                    arm = mutual_undirected(cap, mask_tag(cap, sf, lam))
                    t = edge_turnover(base, arm)
                    if lam == 0.0 and t["turnover_share"] != 0.0:
                        raise SystemExit(f"WGT-0c FAILED: {fname}/{scheme} "
                                         f"lambda=0 turnover != 0")
                    turn[str(lam)] = {"turnover_share": t["turnover_share"]}
                cell["rank_correlation_vs_plain"] = {
                    "all": describe(rhos), "where_cap_binds": describe(rhos_b)}
                cell["selection_turnover_vs_plain"] = turn
            frow["cells"][scheme] = cell
            print(f"  {scheme}: iqr={cell['median_iqr']} "
                  f"rho_sim={cell['spearman_vs_similarity']}", flush=True)

        frow["singleton_union_mass_share_rarity"] = data["singleton_union_mass_share"]
        results["frames"][fname] = frow

        # Plain cells must reproduce tas_frame_split's committed rows.
        got = frow["cells"]["plain"]["median_iqr"]
        want_row = split_committed["frames"][fname]["median_iqr"]
        if abs(got - want_row) > 5e-5:
            raise SystemExit(f"plain reproduction FAILED on {fname}: "
                             f"{got} != {want_row}")
        print(f"  plain reproduction PASS ({got})", flush=True)

    print("WGT-0c PASS: lambda=0 turnover exactly 0 in every cell", flush=True)

    # ---- WGT-2: the style question, sign-based ----
    def deltas(scheme: str, stat: str) -> dict:
        c = {f: results["frames"][f]["cells"][scheme][stat] for f in FRAMES}
        return {"style_W5_vs_W1": round(c["W5"] - c["W1"], 4),
                "style_W6_vs_W4": round(c["W6"] - c["W4"], 4),
                "genre_W4_vs_W1": round(c["W4"] - c["W1"], 4),
                "genre_W6_vs_W5": round(c["W6"] - c["W5"], 4)}

    wgt2 = {}
    for scheme in ("rarity", "evidence"):
        sp, rd = deltas(scheme, "median_iqr"), deltas(scheme, "spearman_vs_similarity")
        style_spread_ok = sp["style_W5_vs_W1"] >= 0 and sp["style_W6_vs_W4"] >= 0
        style_red_ok = rd["style_W5_vs_W1"] <= 0 and rd["style_W6_vs_W4"] <= 0
        if style_spread_ok and style_red_ok:
            verdict = "REVERSED"
        elif (sp["style_W5_vs_W1"] < 0 and sp["style_W6_vs_W4"] < 0
              and rd["style_W5_vs_W1"] > 0 and rd["style_W6_vs_W4"] > 0):
            verdict = "NOT_REVERSED"
        else:
            verdict = "UNRESOLVED"
        wgt2[scheme] = {"spread_deltas": sp, "redundancy_deltas": rd,
                        "verdict": verdict}
    results["WGT-2_style_question"] = wgt2
    results["WGT-1_fame_leak_gate"] = gate
    results["with_release"] = args.with_release
    results["capture_sha256"] = digest
    results["note"] = ("DIAGNOSTIC ONLY, WGT- pre-registration governs. Absolute "
                       "agreement values are not comparable across cells; reads "
                       "are orderings, turnovers and signs.")

    Path(args.out).write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"\nwrote {args.out}", flush=True)
    for scheme, row in wgt2.items():
        print(f"WGT-2 [{scheme}]: {row['verdict']}", flush=True)


if __name__ == "__main__":
    main()
