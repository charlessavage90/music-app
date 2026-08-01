"""Which HALF of the Discogs increment blunts the signal? (diagnostic, not a criterion)

NOT A `TAS-` CRITERION, NOT PRE-REGISTERED, AND IT LICENSES NOTHING. It fixes no
bar, adopts nothing, changes no vocabulary and moves no default. `TAS-AM4`'s
committed `W0`/`W1`/`W6` figures are REPRODUCED here, never replaced --
`tas_frame_eval.json` stays the record for those three.

WHY THIS EXISTS. `TAS-AM4` evaluated `W6` = `W1` + Discogs genre + Discogs style
as ONE step and reported that the enriched frame blunts discrimination. But
Discogs ships two label columns and `rel_discogs.py` keeps them deliberately
separate, warning at its head that "merging Discogs genre into any agreement
statistic would inflate it badly":

    F4  genre  -- a CLOSED 15-value list (Rock, Pop, Electronic, Jazz...)
    F5  style  -- a ~600-value list (indie rock, psychedelic rock...)

So `W6` moved TWO knobs and the fall was attributed to neither. This decomposes
it. `NEXT.md`'s deferred row asked for exactly this -- "a cheap read on whether
coarse agreement suffices for what TAS- does, answerable against the committed
TAS- harness with no rebuild".

FACTOR TABLE -- every variant's baseline differs by EXACTLY ONE column.

    frame   W0   +F1   +F4   +F5    baseline        isolates
    ----------------------------------------------------------------
    W0      y     -     -     -     --              (the committed frame)
    W1      y     y     -     -     W0              F1
    W4      y     y     y     -     W1              F4
    W5      y     y     -     y     W1              F5
    W6      y     y     y     y     W5 and W4       F4 (vs W5), F5 (vs W4)

F4 and F5 are each isolated TWICE, independently. Agreement between the two
isolations is what makes the attribution measured rather than argued.

HELD CONSTANT, and why each is genuinely constant under this intervention:

  the capture      One file, passed in, and `td_turnover.py --verify` asserts it
                   reproduces `ALG-E-mutual_knn-k50.bin` edge-for-edge. Nothing
                   here rebuilds anything.
  the population   Every frame is scored on `W0`'s scorable set. Labels only ever
                   ACCUMULATE (W0 subset of W1 subset of W4/W5 subset of W6), so
                   that set is scorable under all five and the comparison is
                   genuinely one-knob. This is `TAS-AM4` section 13.2's control,
                   reused rather than reinvented -- without it the frame and the
                   population move together.
  the statistics   `signal_on`, `acting_slot_share`, `iqr`, `spearman` are all
                   IMPORTED from the committed modules. A second copy would be
                   free to drift from the figures this is meant to build on.
  the vocabulary   REL-'s own aggregation, attributability filter and
                   normalisation, imported from its committed helpers.

SUBSTRATE: the pre-cap `ALG-E` capture, per `TAS-AM2` -- `TAS-2`/`TAS-3` ask about
the candidates SELECTION CHOOSES AMONG, and the built artifact has already
discarded the ones that lost. `TAS-AM2`'s standing constraint applies to every
figure below: NO READ MAY COMPARE A CAPTURE-SIDE FIGURE AGAINST AN ARTIFACT-SIDE
ONE.

READING THE OUTPUT. `median_iqr` is the within-list spread -- HIGHER is better
discrimination. `spearman_vs_similarity` is redundancy with the similarity score
already in the graph -- LOWER means the labels carry more information similarity
did not already have. `acting_slot_share` is reach: the share of candidate slots
where both ends carry labels and the rule can act at all.

THE SPREAD FIGURE IS SCALE-SENSITIVE and the redundancy figure is not. Adding any
source gives artists more labels, which compresses a Jaccard somewhat regardless
of quality, so the magnitude of a spread change is weaker evidence than its
direction. The rank correlation is scale-free and is the corroborating reading.

Run from `builder/` (~15 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_frame_split.py \
        --capture <path>/alge_capture.npz
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tas_common import HERE, graph_mbids
from tas_frame_eval import acting_slot_share, signal_on
from tas_tags import label_sets
from td_turnover import Capture

_REL = HERE.parent / "2026-07-31-release-tag-coverage"
if str(_REL) not in sys.path:
    sys.path.insert(0, str(_REL))

OUT = HERE / "tas_frame_split.json"

# TAS-AM4's committed figures, for the reproduction check. If these stop matching,
# the harness has drifted and nothing below counts.
COMMITTED = {"W0": 0.1726, "W1": 0.16, "W6": 0.1418}

FRAMES = ("W0", "W1", "W4", "W5", "W6")


def five_frames() -> dict[str, dict[str, set[str]]]:
    """W0/W1/W4/W5/W6 through REL-'s committed helpers -- never reimplemented."""
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
    return {
        "W0": w0,
        "W1": w1,
        "W4": {m: w1[m] | f4[m] for m in mbids},
        "W5": {m: w1[m] | f5[m] for m in mbids},
        "W6": {m: w1[m] | f4[m] | f5[m] for m in mbids},
    }


def delta(rows: dict[str, dict], a: str, b: str) -> dict:
    """b relative to a. Spread as a proportion, reach and redundancy as differences."""
    return {
        "spread_change": round(
            (rows[b]["median_iqr"] - rows[a]["median_iqr"]) / rows[a]["median_iqr"], 4),
        "reach_change_pts": round(
            rows[b]["acting_slot_share"] - rows[a]["acting_slot_share"], 4),
        "redundancy_change": round(
            rows[b]["spearman_vs_similarity"] - rows[a]["spearman_vs_similarity"], 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True,
                    help="alge_capture.npz from td_capture.py")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cap = Capture(Path(args.capture))
    frames = five_frames()

    # The fixed population is W0's scorable set -- TAS-AM4 section 13.2's control.
    fixed = set(signal_on(frames["W0"], args.capture, restrict=None)["_scorable"])
    print(f"fixed population (W0 scorable): {len(fixed)} lists", flush=True)

    rows: dict[str, dict] = {}
    for name in FRAMES:
        labels = frames[name]
        s = signal_on(labels, args.capture, restrict=fixed)
        s.pop("_scorable", None)
        rows[name] = {
            "median_iqr": s["median_iqr"],
            "spearman_vs_similarity": s["spearman"],
            "identical_order_share": s["identical_order_share"],
            "labelled_nodes": sum(1 for v in labels.values() if v),
            "acting_slot_share": round(acting_slot_share(cap, labels), 4),
            "lists_considered": s["lists_considered"],
        }
        print(f"{name}: {json.dumps(rows[name])}", flush=True)

    base = rows["W0"]["median_iqr"]
    for row in rows.values():
        row["spread_change_vs_W0"] = round((row["median_iqr"] - base) / base, 4)

    reproduction = {
        "committed": COMMITTED,
        "measured": {k: rows[k]["median_iqr"] for k in COMMITTED},
        "all_match": all(rows[k]["median_iqr"] == v for k, v in COMMITTED.items()),
    }

    result = {
        "note": "DIAGNOSTIC ONLY. Not a TAS- criterion, not pre-registered, licenses "
                "nothing. TAS-AM4's committed W0/W1/W6 figures are reproduced, not "
                "replaced; tas_frame_eval.json stays their record.",
        "substrate": "pre-cap ALG-E capture (TAS-AM2). Never compare these against an "
                     "artifact-side figure.",
        "capture": args.capture,
        "fixed_population_lists": len(fixed),
        "reproduction_check": reproduction,
        "frames": rows,
        "isolations_of_F4_the_closed_15_value_genre_list": {
            "W1_to_W4": delta(rows, "W1", "W4"),
            "W5_to_W6": delta(rows, "W5", "W6"),
        },
        "isolations_of_F5_the_600_value_style_list": {
            "W1_to_W5": delta(rows, "W1", "W5"),
            "W4_to_W6": delta(rows, "W4", "W6"),
        },
    }

    if not reproduction["all_match"]:
        print(json.dumps(reproduction, indent=1))
        raise SystemExit(
            "REPRODUCTION CHECK FAILED -- this harness no longer reproduces "
            "TAS-AM4's committed figures. Nothing above counts."
        )

    Path(args.out).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("\n" + json.dumps({
        "F4_isolations": result["isolations_of_F4_the_closed_15_value_genre_list"],
        "F5_isolations": result["isolations_of_F5_the_600_value_style_list"],
        "reproduction_all_match": reproduction["all_match"],
    }, indent=1))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
