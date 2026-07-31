"""TAS-AM4: does the signal SURVIVE enriching the frame with REL-'s labels?

THIS DOES NOT CHANGE section 1's VOCABULARY. The committed frame stays pinned and
every committed TAS- figure stands on it. This measures candidate frames BESIDE
the committed one; adopting one would be a further amendment and the owner's
trigger.

THE QUESTION, and why the answer is not obvious. TAS-6 went adverse because
unlabelled candidates -- disproportionately obscure -- get squeezed out at the
cap boundary, and REL- more than doubles lower-half coverage, which attacks that
cause directly. But REL-3 measured the recovered labels as landing in the right
REGION rather than recovering an artist's genres.

  That matters more here than for a coverage instrument. TAS-'s agreement is
  ITSELF a Jaccard, computed BETWEEN TWO ARTISTS. If both sides are derived the
  errors compound, and the direction is unknown in advance: drift toward broad
  common genres makes unrelated artists look alike and FLATTENS the signal;
  independent errors ATTENUATE it toward zero. Both destroy discrimination,
  which is this probe's whole premise. A frame can raise coverage and kill the
  device at the same time.

FRAMES (TAS-AM4), one knob apart:
  W0  the committed section 1 frame -- the isolating baseline
  W1  W0 + REL- F1 (MusicBrainz release-group genres, strict attributability)
  W6  W1 + Discogs genre + Discogs style (REL-'s F6 added to W0)

READS, fixed in TAS-AM4 BEFORE this ran:
  1. TAS-2's EXISTING bars apply unchanged. Median within-list IQR below 0.02
     kills a candidate for TAS- and no coverage figure rescues it; below 0.10 it
     carries the weak-signal flag.
  2. A material fall in spread against W0 -- even while clearing the bar -- is
     the HEADLINE, not a footnote under the coverage gain.
  3. TAS-3 stays DIAGNOSTIC with no bar. A rise in rank correlation or in the
     already-ordered share is the flattening failure showing up a second time.
  4. The share of slots where the rule ACTS is descriptive, and is what would
     drive any TAS-6 improvement.
  5. Nothing here licenses a TAS-4/TAS-6 re-run, an adoption or a rebuild, and
     TAS-6's adverse verdict on the committed frame is NOT softened by a better
     frame existing.

SUBSTRATE: the pre-cap capture (TAS-AM2) -- TAS-2/TAS-3 are selection-side.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_frame_eval.py --capture <path.npz>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

import statistics

from tas_common import HERE, agreement, graph_mbids
from tas_signal import TAS2_KILL_IQR, TAS2_WEAK_FLAG_IQR, _tas2_tas3, iqr, spearman
from tas_tags import label_sets
from td_turnover import Capture

_REL = HERE.parent / "2026-07-31-release-tag-coverage"
if str(_REL) not in sys.path:
    sys.path.insert(0, str(_REL))

OUT = HERE / "tas_frame_eval.json"


def candidate_frames() -> dict[str, dict[str, set[str]]]:
    """W0 / W1 / W6 per TAS-AM4, built through REL-'s own committed helpers.

    Imported, never reimplemented: REL-'s aggregation, attributability filter
    and normalisation are its record's, and a second implementation here would
    be free to drift from the figures this evaluation is meant to build on.
    """
    from rel_artist_dump import OUT_INDEX as ARTIST_INDEX
    from rel_discogs import OUT_RAW as DISCOGS_RAW
    from rel_rg_dump import OUT_RAW as RG_RAW, frame_sets

    mbids = graph_mbids()
    w0 = label_sets()

    per_artist = json.loads(RG_RAW.read_text(encoding="utf-8"))
    f1 = frame_sets(per_artist, mbids, field="g", strict=True)

    index = json.loads(ARTIST_INDEX.read_text(encoding="utf-8"))
    per_discogs = json.loads(DISCOGS_RAW.read_text(encoding="utf-8"))
    mbid_to_discogs = {m: r["discogs"] for m, r in index.items() if r.get("discogs")}

    def discogs_sets(field: str) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for mbid in mbids:
            bucket = per_discogs.get(mbid_to_discogs.get(mbid) or "")
            out[mbid] = set(bucket[field]) if bucket else set()
        return out

    f4, f5 = discogs_sets("g"), discogs_sets("s")
    w1 = {m: w0.get(m, set()) | f1[m] for m in mbids}
    w6 = {m: w1[m] | f4[m] | f5[m] for m in mbids}
    return {"W0": w0, "W1": w1, "W6": w6}


def signal_on(
    labels: dict[str, set[str]], capture_path: str, restrict: set[str] | None
) -> dict:
    """TAS-2/TAS-3 over the capture, optionally on a FIXED artist population.

    WHY THIS EXISTS, and it is a correction to this evaluation's first run.
    `_tas2_tas3` scores every artist it CAN score, and enrichment makes many
    more artists scorable -- 38,782 lists under W0 against 58,117 under W6. So
    the raw W0-vs-W6 spread comparison moves two things at once: the frame, and
    the population it is measured over. The newly scorable artists are exactly
    the obscure ones REL- reached, and there is every reason to expect their
    spread to differ, so a fall in the pooled median could be composition alone
    with the original population untouched. Those two have opposite
    implications and TAS-AM4's read 2 presupposes the like-for-like one.

    `restrict` fixes the population to W0's scorable set. Because labels only
    ever ACCUMULATE (W0 subset of W1 subset of W6), that set is scorable under
    every frame, so the restricted comparison is genuinely one-knob.

    The loop is duplicated from tas_signal rather than that committed module
    being edited -- its figures are in the record. The statistics themselves
    (iqr, spearman, agreement) are imported, and main() asserts that this
    reproduces `_tas2_tas3` exactly when unrestricted.
    """
    # Every array is materialised HERE, never indexed off `z` inside the loop.
    # np.load returns a LAZY NpzFile: each z["rank"] decompresses the whole
    # 4M-element array, so a single such access inside the inner loop turns a
    # three-minute pass into an unbounded one. That is not hypothetical -- it
    # was in the first draft of this function and cost a run.
    z = np.load(capture_path, allow_pickle=True)
    offsets, cand, rank = z["offsets"], z["cand"], z["rank"]
    mbids = list(z["mbids"])

    spreads: list[float] = []
    rho_pairs: list[tuple[float, float]] = []
    identical_order = considered = 0
    scorable: set[str] = set()

    for u_idx, mbid_u in enumerate(mbids):
        u_set = labels.get(mbid_u)
        if not u_set:
            continue
        if restrict is not None and mbid_u not in restrict:
            continue
        lo, hi = int(offsets[u_idx]), int(offsets[u_idx + 1])
        values: list[tuple[float, float]] = []
        for pos in range(lo, hi):
            a = agreement(u_set, labels.get(mbids[int(cand[pos])], set()))
            if a is not None:
                values.append((float(rank[pos]), a))
        spread = iqr([a for _s, a in values])
        if spread is None:
            continue
        scorable.add(mbid_u)
        spreads.append(spread)
        rho_pairs.extend(values)
        considered += 1
        by_strength = [a for _s, a in sorted(values, key=lambda p: -p[0])]
        if by_strength == sorted(by_strength, reverse=True):
            identical_order += 1

    median_iqr = statistics.median(spreads) if spreads else 0.0
    return {
        "lists_considered": considered,
        "median_iqr": round(median_iqr, 4),
        "kills": bool(spreads) and median_iqr < TAS2_KILL_IQR,
        "weak_signal_flag": bool(spreads) and median_iqr < TAS2_WEAK_FLAG_IQR,
        "spearman": round(spearman(rho_pairs), 4) if rho_pairs else None,
        "identical_order_share": (
            round(identical_order / considered, 4) if considered else None
        ),
        "_scorable": scorable,
    }


def acting_slot_share(cap: Capture, labels: dict[str, set[str]]) -> float:
    """Share of directed candidate slots where BOTH ends carry labels.

    Where either end is bare the device takes the neutral value and cannot
    discriminate, so this is the reach of the rule -- and the quantity that
    would drive any TAS-6 improvement (TAS-AM4 read 4).
    """
    labelled = np.array([bool(labels.get(m)) for m in cap.mbids])
    return float((labelled[cap.s_node] & labelled[cap.s_cand]).mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True, help="alge_capture.npz from td_capture.py")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cap = Capture(Path(args.capture))
    frames = candidate_frames()

    # W0's scorable set is the fixed population for the one-knob comparison.
    # Labels only accumulate, so it is scorable under every candidate frame.
    print("--- W0, establishing the fixed population ---", flush=True)
    w0_own = signal_on(frames["W0"], args.capture, restrict=None)
    fixed_population = w0_own.pop("_scorable")

    rows: dict[str, dict] = {}
    for name, labels in frames.items():
        print(f"--- {name} ---", flush=True)
        signal = _tas2_tas3(labels, args.capture)
        if name == "W0":
            # The duplicated loop must reproduce the committed module exactly,
            # or the restricted figures below are measuring something else.
            assert w0_own["median_iqr"] == signal["median_iqr"], "loop diverged from tas_signal"
            assert w0_own["lists_considered"] == signal["lists_considered"]
        fixed = signal_on(labels, args.capture, restrict=fixed_population)
        fixed.pop("_scorable")
        rows[name] = {
            "on_fixed_W0_population": fixed,
            "labelled_nodes": sum(1 for s in labels.values() if s),
            "acting_slot_share": round(acting_slot_share(cap, labels), 4),
            "tas2_median_iqr": signal["median_iqr"],
            "tas2_mean_iqr": signal["mean_iqr"],
            "tas2_kills": signal["kills"],
            "tas2_weak_signal_flag": signal["weak_signal_flag"],
            "tas3_spearman": signal["spearman_strength_vs_agreement"],
            "tas3_identical_order_share": signal["identical_order_share"],
            "lists_considered": signal["lists_considered"],
            "lists_excluded_too_few_labelled": signal["lists_excluded_too_few_labelled"],
        }
        print(json.dumps(rows[name], indent=1), flush=True)

    base = rows["W0"]
    for name, row in rows.items():
        if name == "W0":
            continue
        # POOLED: confounded by composition -- the frame AND the population move.
        row["iqr_change_vs_W0_POOLED_CONFOUNDED"] = round(
            (row["tas2_median_iqr"] - base["tas2_median_iqr"]) / base["tas2_median_iqr"], 4
        )
        # ONE-KNOB: same artists, different frame. This is what read 2 asks for.
        row["iqr_change_vs_W0_fixed_population"] = round(
            (row["on_fixed_W0_population"]["median_iqr"]
             - base["on_fixed_W0_population"]["median_iqr"])
            / base["on_fixed_W0_population"]["median_iqr"], 4
        )
        row["acting_slot_change_vs_W0"] = round(
            (row["acting_slot_share"] - base["acting_slot_share"]) / base["acting_slot_share"], 4
        )

    result = {
        "substrate": "pre-cap capture of the ALG-E archive (TAS-AM2, selection side). "
                     "Section 1's vocabulary is UNCHANGED; these are candidates measured "
                     "beside the committed frame, not an adoption.",
        "bars": {
            "tas2_kill_iqr": TAS2_KILL_IQR,
            "tas2_weak_flag_iqr": TAS2_WEAK_FLAG_IQR,
            "note": "TAS-2's EXISTING bars, reused unchanged (TAS-AM4). TAS-3 is "
                    "diagnostic and carries no bar, as in section 2.",
        },
        "frames": rows,
        "any_candidate_killed": any(
            row["tas2_kills"] for name, row in rows.items() if name != "W0"
        ),
    }
    Path(args.out).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
