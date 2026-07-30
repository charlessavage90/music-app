"""POST-HOC probe: how much of the adopted proxy's floor is RESOLUTION FAILURE?

NOT PRE-REGISTERED, AND SAYS SO. This question was raised BY fp_floor_reach's
result, not before it. fp_floor_reach measured 2.4-5.3% of routed interiors at
the floor using the MBID join, while Track 2's own committed fame_cache.json
records 185 of 1,296 scored artists (14.3%) as unmatched. Those two numbers
describe the same artists under two different resolution methods, and the gap
between them is the quantity here.

WHY IT MATTERS SEPARATELY FROM COVERAGE
  An artist at the floor because nobody wrote an article is a fact about the
  world; the instrument is reporting correctly. An artist at the floor because
  a NAME SEARCH failed is an instrument defect, and it is scored as maximal
  obscurity -- the direction that flatters any arm diving toward the tail
  (the A18 shape).

  The split cannot be read off either number alone, which is why this runs.

READ, fixed before executing (the numbers above are already known; this is the
new comparison):
  If most of Track 2's unmatched artists DO have an English article by MBID,
  the floor was substantially an artifact of name resolution rather than a
  measurement of obscurity. I will report the split, name the artists, and
  NOT infer that any Track 2 verdict changes -- re-reading a committed result
  is a separate decision with its own cost, and belongs to the owner.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_resolution_gap.py
"""

from __future__ import annotations

import collections
import hashlib
import json

from artistpath_builder.artifact import deserialise

from fp_common import ADOPTED, ADOPTED_SHA, HERE, band_of, fame_frame

TRACK2 = HERE.parent / "2026-07-24-track2-arm-scorer"
OUT = HERE / "fp_resolution_gap.json"


def main() -> None:
    wikidata = json.loads((HERE / "fp_wikidata.json").read_text(encoding="utf-8"))
    cache = json.loads((TRACK2 / "fame_cache.json").read_text(encoding="utf-8"))
    frame = fame_frame()

    payload = ADOPTED.read_bytes()
    if hashlib.sha256(payload).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    graph = deserialise(payload)

    # Track 2's cache is keyed by NAME. Names are not unique in the artifact --
    # that non-uniqueness is the very hazard under examination (GOOSE/Goose) --
    # so ambiguous names are counted and excluded rather than guessed at.
    by_name: dict[str, list[str]] = collections.defaultdict(list)
    for mbid, name in zip(graph.mbids, graph.names):
        by_name[name].append(mbid)

    unmatched = [n for n, v in cache.items() if not v.get("matched")]
    resolved_now, still_absent, ambiguous, not_in_graph = [], [], [], []
    for name in unmatched:
        candidates = by_name.get(name, [])
        if not candidates:
            not_in_graph.append(name)
            continue
        if len(candidates) > 1:
            ambiguous.append(name)
            continue
        rec = wikidata.get(candidates[0])
        if rec and rec.get("enwiki"):
            resolved_now.append((name, candidates[0], rec["enwiki"], rec["wikis"],
                                 band_of(frame[candidates[0]])))
        else:
            still_absent.append(name)

    checkable = len(resolved_now) + len(still_absent)
    summary = {
        "post_hoc": True,
        "track2_scored_artists": len(cache),
        "track2_unmatched": len(unmatched),
        "unmatched_resolvable_by_mbid": len(resolved_now),
        "unmatched_genuinely_absent": len(still_absent),
        "unmatched_name_ambiguous_in_graph": len(ambiguous),
        "unmatched_not_in_artifact": len(not_in_graph),
        "resolution_failure_share_of_checkable": (
            round(len(resolved_now) / checkable, 4) if checkable else None
        ),
        "recovered": [
            {"name": n, "mbid": m, "article": a, "languages": w, "band": b}
            for n, m, a, w, b in sorted(resolved_now, key=lambda r: -r[3])
        ],
        "ambiguous_names": sorted(ambiguous),
    }
    OUT.write_text(json.dumps(summary, indent=1), encoding="utf-8")

    print(f"Track 2 scored {len(cache)} distinct artists; {len(unmatched)} "
          f"({len(unmatched) / len(cache):.1%}) scored at the FLOOR as unmatched.")
    print(f"  of those, checkable against the artifact by unique name: {checkable}")
    print(f"    DO have an English article (resolution failure): {len(resolved_now)}")
    print(f"    genuinely have none (instrument correct):        {len(still_absent)}")
    print(f"  name ambiguous in the artifact (excluded):         {len(ambiguous)}")
    print(f"  not present in the artifact at all (excluded):     {len(not_in_graph)}")
    if checkable:
        print(f"\n  -> {len(resolved_now) / checkable:.1%} of the checkable floor "
              f"was RESOLUTION FAILURE, not obscurity")
    print("\n  most-documented artists wrongly placed at the floor:")
    for n, m, a, w, b in sorted(resolved_now, key=lambda r: -r[3])[:10]:
        print(f"    {n[:32]:32} {w:>3} language wikis  band={b}")
    print(f"\n-> {OUT.name}")


if __name__ == "__main__":
    main()
