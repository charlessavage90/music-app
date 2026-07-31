"""REL-7 and REL-2(a): one pass over the MusicBrainz ARTIST dump.

TWO OUTPUTS, AND THEY ARE DELIBERATELY NOT INTERCHANGEABLE

  REL-2(a) -- the MBID -> Discogs artist id mapping, from each artist's
    `discogs` url-rel. This is the half of the Discogs ceiling that lives on
    the MusicBrainz side. Without it the mapping would be a nine-hour pass at
    the web service's 1 req/s, or name matching -- the population-mismatch
    trap that killed every external popularity source, explicitly rejected in
    spec section 7.

  REL-7 -- artist-level tags/genres from the dump, for a CENSUS-scale
    comparison against the committed tas_tags frame (COH-5 sampled n=872).
    The dumps are 2026-07-28/29 snapshots and tas_tags was collected live on
    2026-07-30, so without this, snapshot drift would be indistinguishable
    from a finding.

  REL-7 SUPPLIES A TOLERANCE, NEVER A POPULATION. It is walled off from F0 by
  spec section 1's held-constant row: using the dump's artist tags to define
  "unlabelled" would move every coverage figure for a reason unrelated to
  aggregation. rel_common.f0_label_sets() is the only definition.

ORDERING: this runs FIRST. REL-C1's pass tolerance is REL-7's drift figure,
so the cross-check must exist before the liveness check can be judged.

Run from `builder/` (measured 2.2 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-31-release-tag-coverage/rel_artist_dump.py
"""

from __future__ import annotations

import json
import re
import time

from rel_common import (
    BAND_ORDER,
    HERE,
    MB_ARTIST,
    band_of,
    f0_label_sets,
    fame_frame,
    graph_mbids,
    labels_from,
    lb_genre_sets,
)

OUT_INDEX = HERE / "rel_artist_index_raw.json"
OUT = HERE / "rel_artist.json"

# Every line is parsed -- there is deliberately NO substring pre-filter. The
# dump orders object keys arbitrarily, so a cheap textual test for "is this
# one of ours" would have to match an MBID anywhere in the record, including
# inside a relation to a DIFFERENT artist, and would silently keep the wrong
# rows. The measured pass is ~2 min; the correctness is worth more than that.
_DISCOGS_ID = re.compile(r"discogs\.com/artist/(\d+)")


def discogs_id_of(record: dict) -> str | None:
    for rel in record.get("relations") or []:
        if rel.get("type") != "discogs":
            continue
        resource = (rel.get("url") or {}).get("resource") or ""
        match = _DISCOGS_ID.search(resource)
        if match:
            return match.group(1)
    return None


def collect(wanted: set[str]) -> dict[str, dict]:
    """One streaming pass. Keeps only the artists in the adopted artifact."""
    found: dict[str, dict] = {}
    began = time.time()
    nbytes = 0
    with MB_ARTIST.open("rb") as fh:
        for line in fh:
            nbytes += len(line)
            record = json.loads(line)
            mbid = record.get("id")
            if mbid not in wanted:
                continue
            found[mbid] = {
                "genres": sorted(labels_from(record, "genres")),
                "tags": sorted(labels_from(record, "tags")),
                "discogs": discogs_id_of(record),
            }
            if len(found) % 10000 == 0:
                rate = nbytes / max(time.time() - began, 1e-9) / 1e6
                print(f"  {len(found)}/{len(wanted)} matched  ({rate:.0f} MB/s)", flush=True)
    print(f"  pass done in {(time.time() - began) / 60:.1f} min", flush=True)
    return found


def main() -> None:
    frame = fame_frame()
    mbids = graph_mbids()
    wanted = set(mbids)
    f0 = f0_label_sets()

    # The index is a pure function of the dump, which is a frozen local file,
    # so re-reading 17 GB to recompute it would buy nothing. Delete the index
    # to force a fresh pass.
    if OUT_INDEX.exists():
        found = json.loads(OUT_INDEX.read_text(encoding="utf-8"))
        print(f"reusing {OUT_INDEX.name} ({len(found)} artists) -- delete it to re-scan")
    else:
        found = collect(wanted)
        OUT_INDEX.write_text(json.dumps(found), encoding="utf-8")

    missing = [m for m in mbids if m not in found]

    # --- REL-7, as corrected by REL-AM1.
    # The first implementation compared the dump's `genres` against F0, which
    # is LB genres UNION Wikidata P136. Those differ by an ENTIRE SOURCE, so
    # the result measured P136's contribution, not snapshot drift -- and
    # REL-C1's tolerance is this figure, so a loose one would stop the
    # liveness check ever going red. Like is now compared with like: the
    # dump's genres against the LB genre half of the frame alone, the same
    # quantity COH-5 measured at n=872. P136 is reported separately because it
    # is worth knowing and is NOT drift.
    lb_only = lb_genre_sets()
    print(f"\n{'band':>12} {'n':>7} {'LB half':>8} {'dump':>7} {'drift':>7} "
          f"{'both':>7} {'identical':>10} {'P136 adds':>10}")
    per_band: dict[str, dict] = {}
    tot_both = tot_ident = 0
    for b in BAND_ORDER:
        band_mbids = [m for m in mbids if band_of(frame[m]) == b]
        n = len(band_mbids)
        if not n:
            continue
        lb_lab = sum(1 for m in band_mbids if lb_only[m])
        dump_lab = sum(1 for m in band_mbids if (found.get(m) or {}).get("genres"))
        both = [m for m in band_mbids if lb_only[m] and (found.get(m) or {}).get("genres")]
        ident = sum(1 for m in both if set(found[m]["genres"]) == lb_only[m])
        tot_both += len(both)
        tot_ident += ident
        drift = abs(lb_lab - dump_lab) / n
        p136_adds = sum(1 for m in band_mbids if f0[m] and not lb_only[m]) / n
        per_band[b] = {
            "n": n,
            "lb_half_labelled": lb_lab,
            "dump_labelled": dump_lab,
            "both_labelled": len(both),
            "identical_genre_sets": ident,
            "drift_share": round(drift, 4),
            "p136_only_share": round(p136_adds, 4),
        }
        print(f"{b:>12} {n:>7} {lb_lab / n:>7.1%} {dump_lab / n:>6.1%} "
              f"{drift:>6.2%} {len(both):>7} "
              f"{(ident / len(both)) if both else 0:>9.1%} {p136_adds:>9.1%}")

    overall_drift = abs(
        sum(1 for m in mbids if lb_only[m])
        - sum(1 for m in mbids if (found.get(m) or {}).get("genres"))
    ) / len(mbids)

    # --- REL-2(a): the mapping half of the Discogs ceiling
    print(f"\n{'band':>12} {'n':>7} {'unlabelled':>11} {'unlab w/ discogs':>17}")
    mapping: dict[str, dict] = {}
    for b in BAND_ORDER:
        band_mbids = [m for m in mbids if band_of(frame[m]) == b]
        unlab = [m for m in band_mbids if not f0[m]]
        if not band_mbids:
            continue
        with_d = sum(1 for m in unlab if (found.get(m) or {}).get("discogs"))
        all_d = sum(1 for m in band_mbids if (found.get(m) or {}).get("discogs"))
        mapping[b] = {
            "n": len(band_mbids),
            "unlabelled": len(unlab),
            "unlabelled_with_discogs": with_d,
            "unlabelled_with_discogs_share": round(with_d / len(unlab), 4) if unlab else None,
            "all_with_discogs_share": round(all_d / len(band_mbids), 4),
        }
        share = f"{with_d / len(unlab):.1%}" if unlab else "n/a"
        print(f"{b:>12} {len(band_mbids):>7} {len(unlab):>11} {share:>17}")

    OUT.write_text(
        json.dumps(
            {
                "graph_nodes": len(mbids),
                "matched_in_dump": len(found),
                "absent_from_dump": len(missing),
                "rel_7_fidelity": {
                    "comparison": "MB artist dump `genres` vs the LB half of the "
                                  "frame alone -- NOT vs F0 (REL-AM1)",
                    "bands": per_band,
                    "both_labelled": tot_both,
                    "identical_genre_sets": tot_ident,
                    "overall_drift_share": round(overall_drift, 4),
                },
                "rel_2a_discogs_mapping": mapping,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"\nabsent from dump: {len(missing)}")
    print(f"REL-7 overall drift: {overall_drift:.2%}  -> REL-C1 tolerance")
    print(f"-> {OUT.name}, {OUT_INDEX.name}")


if __name__ == "__main__":
    main()
