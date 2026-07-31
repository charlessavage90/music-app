"""REL-C1, REL-C2, REL-3 and REL-4: the instrument checks and the reads that
depend on them.

NOTHING IN HERE MAY BE READ UNTIL BOTH CHECKS PASS (spec section 5). A green
result from a new instrument is not evidence until the instrument has been
shown to go red, so main() refuses to print the criteria when a check fails.

REL-C2's SHUFFLE, AND THE ONE THING IT CANNOT DO
  It permutes which artist owns which release group, preserving each artist's
  release COUNT. That is informative for REL-3: under shuffled ownership the
  aggregated set is a random artist's genres, so matched agreement must
  collapse toward chance.

  It is NOT informative for REL-1 and must never be quoted as if it were.
  Coverage is near-invariant under this shuffle BY CONSTRUCTION -- a randomly
  assigned album still carries tags, so a randomly assigned artist still ends
  up labelled. Randomising ownership RELOCATES coverage rather than destroying
  it. The shuffled coverage figure is printed anyway, precisely so that
  invariance is visible rather than assumed.

  This is written down because TAS-AM3 is the worked example of a red check
  that could not fire as written: a Jaccard device cannot produce large change
  on a randomised LABEL frame, because randomising labels destroys overlap
  rather than randomising it. The axis matters, and this shuffle moves
  ownership, not labels.

Run from `builder/`, AFTER rel_artist_dump.py and rel_rg_dump.py:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-31-release-tag-coverage/rel_score.py
"""

from __future__ import annotations

import json
import random
import statistics

from rel_common import (
    BAND_ORDER,
    HERE,
    band_of,
    f0_label_sets,
    fame_frame,
    graph_mbids,
    jaccard,
    lb_genre_sets,
)
from rel_artist_dump import OUT as ARTIST_OUT, OUT_INDEX as ARTIST_INDEX
from rel_rg_dump import OUT_RAW as RG_RAW, frame_sets

OUT = HERE / "rel_score.json"
SEED = 20260731

# REL-3's bars, fixed in the pre-registration before any run.
MATCHED_OVER_NULL = 3.0
ZERO_OVERLAP_MARGIN = 0.20


def held_out_scores(
    mbids: list[str], f0: dict[str, set[str]], agg: dict[str, set[str]]
) -> tuple[list[float], int, int]:
    """REL-3 over artists LABELLED today: aggregate them as if they were not.

    Returns (jaccards, zero_overlap_count, scorable_count). Artists whose
    aggregation produced nothing are NOT scored as zero -- an unscorable case
    is not a wrong answer, and folding it in would understate the device by
    exactly the amount its coverage falls short.
    """
    scores: list[float] = []
    zero = 0
    for mbid in mbids:
        if not f0[mbid]:
            continue
        value = jaccard(agg[mbid], f0[mbid])
        if value is None:
            continue
        scores.append(value)
        if value == 0.0:
            zero += 1
    return scores, zero, len(scores)


def shuffled(per_artist: dict[str, list[dict]], mbids: list[str]) -> dict[str, list[dict]]:
    """REL-C2: permute ownership, preserve each artist's release count."""
    rng = random.Random(SEED)
    flat = [rg for mbid in mbids for rg in per_artist.get(mbid, ())]
    rng.shuffle(flat)
    out: dict[str, list[dict]] = {}
    cursor = 0
    for mbid in mbids:
        count = len(per_artist.get(mbid, ()))
        out[mbid] = flat[cursor : cursor + count]
        cursor += count
    return out


def main() -> None:
    frame = fame_frame()
    mbids = graph_mbids()
    f0 = f0_label_sets()
    per_artist = json.loads(RG_RAW.read_text(encoding="utf-8"))
    artist_summary = json.loads(ARTIST_OUT.read_text(encoding="utf-8"))
    index = json.loads(ARTIST_INDEX.read_text(encoding="utf-8"))

    drift = artist_summary["rel_7_fidelity"]["overall_drift_share"]
    print(f"REL-7 drift (REL-C1's tolerance): {drift:.2%}")

    # ---------- REL-C1 (as corrected by REL-AM2): does the AGGREGATION CODE
    # recover an answer we already have?
    #
    # Two defects in the first version, both fixed here. It compared against
    # F0 (LB U P136) and so failed on P136's contribution, the same conflation
    # REL-AM1 fixed in REL-7. And fixing only the comparand would have made it
    # compare the dump's genres against the LB half -- which is exactly what
    # REL-7 measures, so it would have passed by construction and tested NO
    # CODE. A check that duplicates another measurement is not a check.
    #
    # So it now runs the real path: give each artist one attributable
    # pseudo-release carrying their own dump-level genres, push it through the
    # SAME frame_sets() that builds F1, and require set equality against the LB
    # half. This exercises frame_sets, aggregate, the strict-filter flag and
    # the MBID keying -- the machinery REL-1 actually rides on.
    lb_only = lb_genre_sets()
    synthetic = {
        m: [{"g": sorted((index.get(m) or {}).get("genres") or []), "t": [], "a": True}]
        for m in mbids
    }
    recovered_sets = frame_sets(synthetic, mbids, field="g", strict=True)
    # Set equality, not a count match: a pipeline labelling the right NUMBER of
    # artists with the WRONG labels must fail, and counts would let it through.
    disagree = [m for m in mbids if recovered_sets[m] != lb_only[m]]
    c1_gap = len(disagree) / len(mbids)
    c1_tolerance = max(drift, 0.005)
    c1_pass = c1_gap <= c1_tolerance + 1e-9
    print(f"REL-C1: aggregation path over artist-level tags disagrees with the "
          f"LB half on {len(disagree):,}/{len(mbids):,} artists ({c1_gap:.2%}, "
          f"tolerance {c1_tolerance:.2%}) -> {'PASS' if c1_pass else 'FAIL'}")

    # ---------- REL-C2: shuffle ownership
    f1 = frame_sets(per_artist, mbids, field="g", strict=True)
    shuffled_per_artist = shuffled(per_artist, mbids)
    f1_shuf = frame_sets(shuffled_per_artist, mbids, field="g", strict=True)

    matched, matched_zero, matched_n = held_out_scores(mbids, f0, f1)
    null, null_zero, null_n = held_out_scores(mbids, f0, f1_shuf)
    med_matched = statistics.median(matched) if matched else 0.0
    med_null = statistics.median(null) if null else 0.0
    ratio = med_matched / med_null if med_null else float("inf")

    lower = [m for m in mbids if band_of(frame[m]) == "lower half"]
    cov_real = sum(1 for m in lower if f0[m] or f1[m]) / len(lower)
    cov_shuf = sum(1 for m in lower if f0[m] or f1_shuf[m]) / len(lower)
    print(f"REL-C2: lower-half coverage real {cov_real:.1%} vs shuffled "
          f"{cov_shuf:.1%} -- near-invariant BY CONSTRUCTION, and this figure "
          f"is NOT evidence about REL-1")
    c2_pass = matched_n > 0 and null_n > 0
    print(f"REL-C2: scorable matched {matched_n:,}, scorable null {null_n:,} "
          f"-> {'PASS' if c2_pass else 'FAIL'}")

    if not (c1_pass and c2_pass):
        print("\nINSTRUMENT CHECK FAILED -- no criterion is read. "
              "Spec section 5: the instrument is repaired or withdrawn first, "
              "and any repair after a result exists is a section 8 amendment.")
        OUT.write_text(
            json.dumps(
                {
                    "instrument_checks": {
                        "rel_c1_pass": c1_pass,
                        "rel_c1_gap": round(c1_gap, 4),
                        "rel_c2_pass": c2_pass,
                    },
                    "criteria_read": False,
                },
                indent=1,
            ),
            encoding="utf-8",
        )
        raise SystemExit(1)

    # ---------- REL-3
    zero_matched = matched_zero / matched_n
    zero_null = null_zero / null_n
    ratio_ok = ratio >= MATCHED_OVER_NULL
    zero_ok = (zero_null - zero_matched) >= ZERO_OVERLAP_MARGIN
    print(f"\nREL-3 median Jaccard: matched {med_matched:.3f} vs null "
          f"{med_null:.3f}  ratio {ratio:.2f} (bar {MATCHED_OVER_NULL}) "
          f"-> {'PASS' if ratio_ok else 'FAIL'}")
    print(f"REL-3 zero-overlap: matched {zero_matched:.1%} vs null "
          f"{zero_null:.1%}  margin {(zero_null - zero_matched) * 100:.1f} pts "
          f"(bar {ZERO_OVERLAP_MARGIN * 100:.0f}) "
          f"-> {'PASS' if zero_ok else 'FAIL'}")
    print(f"REL-3 share at Jaccard >= 0.5: "
          f"{sum(1 for v in matched if v >= 0.5) / matched_n:.1%}")

    OUT.write_text(
        json.dumps(
            {
                "instrument_checks": {
                    "rel_c1_pass": c1_pass,
                    "rel_c1_gap": round(c1_gap, 4),
                    "rel_c1_tolerance": round(c1_tolerance, 4),
                    "rel_c2_pass": c2_pass,
                    "rel_c2_lower_half_coverage_real": round(cov_real, 4),
                    "rel_c2_lower_half_coverage_shuffled": round(cov_shuf, 4),
                },
                "criteria_read": True,
                "rel_3": {
                    "scorable_matched": matched_n,
                    "scorable_null": null_n,
                    "median_matched": round(med_matched, 4),
                    "median_null": round(med_null, 4),
                    "ratio": round(ratio, 3),
                    "ratio_bar": MATCHED_OVER_NULL,
                    "ratio_pass": ratio_ok,
                    "zero_overlap_matched": round(zero_matched, 4),
                    "zero_overlap_null": round(zero_null, 4),
                    "zero_overlap_margin_bar": ZERO_OVERLAP_MARGIN,
                    "zero_overlap_pass": zero_ok,
                    "share_at_half_or_better": round(
                        sum(1 for v in matched if v >= 0.5) / matched_n, 4
                    ),
                },
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
