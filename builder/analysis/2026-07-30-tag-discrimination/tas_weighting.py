"""Should shared labels be weighted by how RARE they are? (diagnostic, not a criterion)

NOT A `TAS-` CRITERION, NOT PRE-REGISTERED, AND IT LICENSES NOTHING. It fixes no
bar, adopts nothing, changes no vocabulary and moves no default. §1's device is
**unchanged**: agreement is still plain Jaccard over the `COH-2` union genre, and
every committed `TAS-` figure stands on it. Adopting a weighted device would be a
§1 change, which is an §8 amendment, which is the owner's trigger.

WHY THIS EXISTS. The owner observed that plain Jaccard has no concept of a label
being BROAD. Two artists tagged only `rock` share everything they have and score
1.0 -- a perfect match -- while two artists sharing `indie rock` and `shoegaze`
but differing on a third label score 0.5. A tag shared by two artists and almost
nobody else is far more informative than one shared by five thousand, and the
committed device treats them identically.

THE WEIGHTED VARIANT under test: the same Jaccard, with each label contributing
`log(N / artists_carrying_it)` instead of 1. Rare labels count for more. This is
the standard inverse-frequency shape; nothing here claims it is the *best*
weighting, only that it is an aggressive one, which is what makes a null
informative -- if even this leaves selection unchanged, the ordering is robust.

SUBSTRATE: the pre-cap `ALG-E` capture, per `TAS-AM2` -- the question is about
the candidates SELECTION CHOOSES AMONG. Reading D also lives on the capture, so
no reading here crosses `TAS-AM2`'s line. The vocabulary statistics in reading A
are properties of the label frame itself and are substrate-independent.

FOUR READINGS:

  A  vocabulary shape -- how concentrated is the label frame, and how much of
     the agreement in it is carried by a handful of broad words.
  B  does label COUNT track fame? (it does -- and see D for why that matters
     less than it sounds)
  C  the decision-relevant pair: does one artist's candidate list REORDER, and
     would different neighbours actually survive the cap?
  D  a RETRACTION, kept because a falsified prediction is worth more on the
     record than off it. This session predicted that famous artists' long tails
     of stray tags would suppress their agreement through the Jaccard
     denominator, making the device partly a fame measurement. Measured, the
     effect is approximately zero. See the note on reading D below.

READING C IS THE ONE THAT DECIDES. Rank correlation and turnover measure
different things and this probe reports both, because they point different ways:
an artist's candidate list barely reorders, yet the map changes materially. THE
CAP IS WHAT RECONCILES THEM -- only the top 50 survive, so a small shuffle right
at the cut line changes who is kept even when the ordering is otherwise intact.
Turnover is the decision-relevant statistic for that reason; ordering similarity
alone would have said "decoration" and been wrong.

THE SPREAD COMPARISON IS SCALE-CONFOUNDED AND IS REPORTED, NOT RELIED ON. The
weighted measure deliberately compresses its range -- sharing a common label now
contributes almost nothing -- so its interquartile spread falls mechanically
whether or not it discriminates less. Comparing spread across two MEASURES is not
the comparison that statistic was built for (comparing two VOCABULARIES under one
measure is). The scale-free reading is C's rank correlation.

Run from `builder/` (~10 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_weighting.py \
        --capture <path>/alge_capture.npz
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path

import numpy as np

from tas_common import GLOBAL_NEUTRAL_FALLBACK, HERE, agreement, fame_frame
from tas_select import LAMBDAS, edge_turnover, mask_tag
from tas_signal import iqr
from tas_tags import label_sets
from td_turnover import Capture, mutual_undirected

OUT = HERE / "tas_weighting.json"
TOP_N = 20


def idf_table(
    labels: dict[str, set[str]], n_artists: int
) -> tuple[dict[str, float], Counter]:
    """Rarity weight per label, and the raw document frequencies behind it."""
    df: Counter = Counter()
    for s in labels.values():
        for lab in s:
            df[lab] += 1
    return {lab: math.log(n_artists / c) for lab, c in df.items()}, df


def weighted_agreement(a: set[str], b: set[str], idf: dict[str, float]) -> float | None:
    """Jaccard with each label contributing its rarity. None if either side is bare."""
    if not a or not b:
        return None
    wu = sum(idf.get(x, 0.0) for x in (a | b))
    if wu <= 0:
        return None
    return sum(idf.get(x, 0.0) for x in (a & b)) / wu


def _neutral(values: list[float]) -> float:
    """The §1 neutral rule, applied to whichever measure is in use."""
    return statistics.median(values) if len(values) >= 2 else GLOBAL_NEUTRAL_FALLBACK


def build_fields(cap: Capture, labels: dict[str, set[str]], idf: dict[str, float]):
    """Plain and weighted agreement for every candidate slot, plus raw-pair records.

    One pass. `raw` keeps only slots where BOTH ends carry labels, which is the
    population readings A(shared) and D need.
    """
    sets = [labels.get(m, set()) for m in cap.mbids]
    plain = np.empty(cap.total, dtype=np.float64)
    weighted = np.empty(cap.total, dtype=np.float64)
    raw_ag: list[float] = []
    raw_size: list[float] = []

    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if lo == hi:
            continue
        own = sets[u]
        cand_sets = [sets[c] for c in cap.s_cand[lo:hi]]
        p_raw = [agreement(own, c) for c in cand_sets]
        w_raw = [weighted_agreement(own, c, idf) for c in cand_sets]
        p_n = _neutral([v for v in p_raw if v is not None])
        w_n = _neutral([v for v in w_raw if v is not None])
        for i, cand in enumerate(cand_sets):
            plain[lo + i] = p_n if p_raw[i] is None else p_raw[i]
            weighted[lo + i] = w_n if w_raw[i] is None else w_raw[i]
            if p_raw[i] is not None:
                raw_ag.append(p_raw[i])
                raw_size.append((len(own) + len(cand)) / 2.0)
        if u % 15000 == 0:
            print(f"  fields {u}/{cap.n}", flush=True)
    return plain, weighted, np.array(raw_ag), np.array(raw_size)


def spearman(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < 3:
        return None
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    d = math.sqrt(float((rx * rx).sum()) * float((ry * ry).sum()))
    return float((rx * ry).sum() / d) if d else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cap = Capture(Path(args.capture))
    labels = label_sets()
    frame = fame_frame()
    idf, df = idf_table(labels, cap.n)

    # ---- A: vocabulary shape (frame-only, substrate-independent) ----
    total_occ = sum(df.values())
    top = {lab for lab, _ in df.most_common(TOP_N)}
    a_read = {
        "distinct_labels": len(df),
        "artist_label_occurrences": total_occ,
        f"top{TOP_N}_share_of_occurrences": round(sum(df[l] for l in top) / total_occ, 4),
        "labels_on_exactly_one_artist": sum(1 for n in df.values() if n == 1),
        "singleton_share_of_vocabulary": round(
            sum(1 for n in df.values() if n == 1) / len(df), 4),
        "most_common": [[lab, n] for lab, n in df.most_common(15)],
        "note": "A label carried by exactly ONE artist can never create agreement "
                "with anyone, so the useful rare labels are those on a handful.",
    }
    print(f"[A] {json.dumps({k: v for k, v in a_read.items() if k != 'most_common'})}",
          flush=True)

    # ---- B: does label COUNT track fame? ----
    sized = [(frame[m], len(labels.get(m, set()))) for m in cap.mbids
             if m in frame and labels.get(m)]
    pct = np.array([p for p, _ in sized])
    size = np.array([s for _, s in sized], dtype=float)
    b_read = {
        "labelled_artists_with_a_fame_percentile": len(sized),
        "spearman_fame_vs_label_count": round(spearman(pct, size), 4),
        "median_label_count_by_fame_decile": {
            f"{lo/10:.1f}-{(lo+1)/10:.1f}": float(np.median(size[
                (pct >= lo / 10) & (pct < (lo + 1) / 10)]))
            for lo in range(10)
            if ((pct >= lo / 10) & (pct < (lo + 1) / 10)).sum()
        },
    }
    print(f"[B] spearman(fame, label count) = {b_read['spearman_fame_vs_label_count']}",
          flush=True)

    plain, weighted, raw_ag, raw_size = build_fields(cap, labels, idf)

    # ---- C: does the candidate list reorder, and does the map change? ----
    rhos, rhos_binding = [], []
    p_iqrs, w_iqrs = [], []
    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if hi - lo < 3:
            continue
        r = spearman(plain[lo:hi], weighted[lo:hi])
        if r is not None:
            rhos.append(r)
            if bool(cap.binds[u]):
                rhos_binding.append(r)
        pi, wi = iqr(list(plain[lo:hi])), iqr(list(weighted[lo:hi]))
        if pi is not None and wi is not None:
            p_iqrs.append(pi)
            w_iqrs.append(wi)

    def describe(vals):
        a = np.array(vals)
        return {
            "artists": len(a),
            "median": round(float(np.median(a)), 4),
            "p10": round(float(np.percentile(a, 10)), 4),
            "share_below_0.99": round(float((a < 0.99).mean()), 4),
            "share_below_0.9": round(float((a < 0.9).mean()), 4),
        }

    turnover = {}
    for lam in LAMBDAS:
        base = mutual_undirected(cap, mask_tag(cap, plain, lam))
        arm = mutual_undirected(cap, mask_tag(cap, weighted, lam))
        t = edge_turnover(base, arm)
        turnover[str(lam)] = {
            "plain_edges": int(base.size),
            "weighted_edges": int(arm.size),
            "turnover_share": t["turnover_share"],
        }
        print(f"  lambda={lam}: turnover {t['turnover_share']*100:.2f}%", flush=True)

    c_read = {
        "within_list_rank_correlation": {
            "all_artists": describe(rhos),
            "where_cap_binds": describe(rhos_binding),
        },
        "selection_turnover_same_lambda_only_the_measure_differs": turnover,
        "spread_REPORTED_NOT_RELIED_ON": {
            "plain_median_iqr": round(float(np.median(p_iqrs)), 4),
            "weighted_median_iqr": round(float(np.median(w_iqrs)), 4),
            "why_not_relied_on": "Comparing IQR across two MEASURES is scale-confounded; "
                                 "the weighted measure compresses its range by design. The "
                                 "scale-free reading is the rank correlation above.",
        },
        "read": "The lambda=0 cell MUST be exactly 0.00% -- both measures are forced to "
                "select identically there. Rank correlation says the list barely reorders; "
                "turnover says the map changes materially. The CAP reconciles them: only "
                "the top 50 survive, so a shuffle at the cut line changes who is kept.",
    }

    # ---- D: the retraction ----
    d_read = {
        "labelled_candidate_slots": int(raw_ag.size),
        "spearman_label_count_vs_agreement": round(spearman(raw_size, raw_ag), 4),
        "retraction": "This session predicted that famous artists' long tails of stray "
                      "tags would suppress agreement through the Jaccard denominator "
                      "STRONGLY ENOUGH to make the device partly a fame measurement. "
                      "Label count IS strongly fame-linked (reading B), and the effect on "
                      "agreement is present and negative -- but weak. The strong form of "
                      "the prediction is RETRACTED.",
        "substrate_changes_this_number_and_that_is_the_point": "Measured on the pre-cap "
            "CANDIDATE slots (this reading) the correlation is about -0.13. Measured over "
            "the adopted artifact's surviving EDGES it is about -0.02. Both are weak, and "
            "they are not comparable -- TAS-AM2 forbids reading one against the other. The "
            "gap is itself informative: surviving edges are the strong pairs, where "
            "agreement is high whatever the label count, so the denominator effect has "
            "less room to show among them. An earlier statement in this session that the "
            "effect was 'approximately zero' was true of the artifact reading and "
            "OVERSTATED the retraction for the selection-side one.",
        "do_not_read_banded_medians_as_a_trend": "Artists with one label each can only "
                                                 "score 0.0 or 1.0, so a band median of "
                                                 "0.5 means 'about half match', not "
                                                 "'small sets agree strongly'. The rank "
                                                 "correlation is the honest statistic.",
    }
    print(f"[D] spearman(label count, agreement) = "
          f"{d_read['spearman_label_count_vs_agreement']}", flush=True)

    Path(args.out).write_text(json.dumps({
        "note": "DIAGNOSTIC ONLY. Not a TAS- criterion, not pre-registered, licenses "
                "nothing. Section 1's device is UNCHANGED and every committed TAS- "
                "figure stands on plain Jaccard.",
        "substrate": "pre-cap ALG-E capture (TAS-AM2). No reading here crosses to the "
                     "artifact side.",
        "capture": args.capture,
        "weighting_under_test": "log(N / artists_carrying_the_label) per label",
        "A_vocabulary_shape": a_read,
        "B_label_count_vs_fame": b_read,
        "C_does_it_reorder_and_does_the_map_change": c_read,
        "D_retracted_prediction": d_read,
    }, indent=1), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
