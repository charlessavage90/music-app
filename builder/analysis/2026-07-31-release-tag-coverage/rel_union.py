"""REL-4: does the second source add anything the first one misses?

F6 = F1 (MusicBrainz release groups) UNION F4/F5 (Discogs). Reported as the
INCREMENTAL gain over F1, never as a total -- spec section 2.

ALSO THE LABEL-LEVEL AGREEMENT WHERE BOTH SOURCES FIRE, WITH ITS CONFOUND
NAMED. Two sources agreeing is worth more than either alone and two sources
disagreeing is a finding. But the two speak different vocabularies:
MusicBrainz is a folksonomy ("modern classical", "post-punk"), Discogs `genre`
is a CLOSED 15-VALUE list ("Classical", "Rock") and `style` a ~600-value one.
Exact-match agreement is therefore depressed for reasons of VOCABULARY rather
than of disagreement, and the figure must not be read as "the sources
contradict each other". Reported with a coarse-match column beside it --
whether the sets share ANY label -- which is the reading that survives the
vocabulary gap.

Run from `builder/`, AFTER rel_rg_dump.py and rel_discogs.py:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-31-release-tag-coverage/rel_union.py
"""

from __future__ import annotations

import json
import statistics

from rel_common import (
    BAND_ORDER,
    HERE,
    band_of,
    f0_label_sets,
    fame_frame,
    graph_mbids,
    jaccard,
)
from rel_artist_dump import OUT_INDEX as ARTIST_INDEX
from rel_discogs import OUT_RAW as DISCOGS_RAW
from rel_rg_dump import OUT_RAW as RG_RAW, frame_sets

OUT = HERE / "rel_union.json"


def main() -> None:
    frame = fame_frame()
    mbids = graph_mbids()
    f0 = f0_label_sets()

    per_artist = json.loads(RG_RAW.read_text(encoding="utf-8"))
    f1 = frame_sets(per_artist, mbids, field="g", strict=True)

    index = json.loads(ARTIST_INDEX.read_text(encoding="utf-8"))
    per_discogs = json.loads(DISCOGS_RAW.read_text(encoding="utf-8"))
    mbid_to_discogs = {m: r["discogs"] for m, r in index.items() if r.get("discogs")}

    def discogs_sets(field: str) -> dict[str, set[str]]:
        out = {}
        for mbid in mbids:
            bucket = per_discogs.get(mbid_to_discogs.get(mbid) or "")
            out[mbid] = set(bucket[field]) if bucket else set()
        return out

    f4, f5 = discogs_sets("g"), discogs_sets("s")
    f6 = {m: f1[m] | f4[m] | f5[m] for m in mbids}

    print(f"{'band':>12} {'n':>7} {'F0':>7} {'F1':>7} {'F4':>7} {'F6':>7} "
          f"{'REL-4':>7}")
    cover: dict[str, dict] = {}
    for b in BAND_ORDER:
        band = [m for m in mbids if band_of(frame[m]) == b]
        n = len(band)
        if not n:
            continue
        row = {
            name: sum(1 for m in band if f0[m] or sets[m]) / n
            for name, sets in (("F1", f1), ("F4", f4), ("F5", f5), ("F6", f6))
        }
        row["F0"] = sum(1 for m in band if f0[m]) / n
        row["rel_4_increment"] = row["F6"] - row["F1"]
        cover[b] = {"n": n, **{k: round(v, 4) for k, v in row.items()}}
        print(f"{b:>12} {n:>7} {row['F0']:>6.1%} {row['F1']:>6.1%} "
              f"{row['F4']:>6.1%} {row['F6']:>6.1%} "
              f"{row['rel_4_increment'] * 100:>+6.1f}")

    # --- agreement where BOTH sources fire, on artists unlabelled today
    both = [m for m in mbids if not f0[m] and f1[m] and (f4[m] or f5[m])]
    exact = [
        v for m in both if (v := jaccard(f1[m], f4[m] | f5[m])) is not None
    ]
    any_shared = sum(1 for m in both if f1[m] & (f4[m] | f5[m]))
    print(f"\nREL-4 agreement, on {len(both):,} unlabelled artists both sources reach:")
    print(f"  median Jaccard (vocabularies differ -- see docstring): "
          f"{statistics.median(exact) if exact else 0:.3f}")
    print(f"  share sharing at least one label:                     "
          f"{any_shared / len(both) if both else 0:.1%}")

    # How many artists does each source reach ALONE?
    lower = [m for m in mbids if band_of(frame[m]) == "lower half" and not f0[m]]
    only_mb = sum(1 for m in lower if f1[m] and not (f4[m] or f5[m]))
    only_dg = sum(1 for m in lower if (f4[m] or f5[m]) and not f1[m])
    neither = sum(1 for m in lower if not f1[m] and not (f4[m] or f5[m]))
    print(f"\nlower-half unlabelled ({len(lower):,}): MB only {only_mb:,}, "
          f"Discogs only {only_dg:,}, both {len(lower) - only_mb - only_dg - neither:,}, "
          f"neither {neither:,}")

    OUT.write_text(
        json.dumps(
            {
                "coverage": cover,
                "rel_4_agreement": {
                    "artists_both_sources_reach": len(both),
                    "median_jaccard": round(
                        statistics.median(exact) if exact else 0.0, 4
                    ),
                    "share_sharing_any_label": round(
                        any_shared / len(both), 4
                    ) if both else None,
                    "vocabulary_confound": "MB folksonomy vs Discogs' closed "
                    "15-value genre list -- exact match is depressed by "
                    "vocabulary, not by disagreement",
                },
                "lower_half_unlabelled_reach": {
                    "n": len(lower),
                    "mb_only": only_mb,
                    "discogs_only": only_dg,
                    "both": len(lower) - only_mb - only_dg - neither,
                    "neither": neither,
                },
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
