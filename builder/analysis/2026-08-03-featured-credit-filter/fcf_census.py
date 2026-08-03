"""Size the FEATURED-CREDIT class on both censused populations.

DIAGNOSTIC ONLY. Adopts nothing, fixes no criterion, sets no bar. The rule
shape is already ruled (NEXT.md top block, 2026-08-02 night): a keep-check
extending the adopted no-release drop rule, never a purge. This census sizes
the class that rule would evaluate, prices the clip stage, and checks the
detector against the two worked instances. The rule document is written after
this census and BEFORE any clip result exists.

THE CLASS (fame-instrument execution log §5a)
  Artists that are in the deliverable population only because CREDITS count as
  release groups: every release-group credit they carry is a shared credit --
  they are never the sole credited artist on anything. A MusicBrainz credit
  creates the node, quarter-weight co-listens (LBS-1, FEATURED_ARTIST_WEIGHT
  0.25) create its similarity edges, and the adopted drop rule never evaluates
  it because it only sees artists with ZERO release groups. Worked instances:
  田島賢 (7e4f57b3, video-game-soundtrack contributions) and TJ Brown
  (f62c24cd, features on streamer-adjacent releases -- the keeper case,
  8,274 Spotify monthly listeners).

THE SPLIT IS RE-DERIVED CLEAN, NOT READ OFF rel_rg_raw.json
  That file's "a" flag folds in the REL- type exclusions (compilation, live,
  broadcast...), so an artist whose only sole credits are live albums would
  read as featured-credit when they are a real act. Sole credit here is
  rel_common.rg_artist_id(record) == mbid alone: exactly one credited artist,
  and it is this one. No type filter.

WHAT IS RECORDED PER ARTIST, so the rule document can fix the predicate with
the data visible rather than re-running the pass:
  total  release-group credits of any shape
  sole   credits where the artist is the only one   (primary existence)
  first  multi-artist credits where the artist is listed FIRST ("A feat. B"
         puts A first; a first-listed artist may be a primary act whose every
         release carries features)

IMPORTED, NEVER REIMPLEMENTED
  Populations and the artist-dump pass come from ctc_census (manifest-verified
  ALG-B cell union; DSP/discogs/type extraction) and cb_metrics (the adopted
  artifact's path and sha). Two readers would be two chances to disagree.

SOURCES, all local, no network:
  MB release-group dump   ~18 GiB   ~2.4 min   the credit split
  MB artist dump          ~17 GiB   ~2-4 min   DSP links for class members

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-featured-credit-filter/fcf_census.py
"""

from __future__ import annotations

import json
import sys
import time

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent

_CTC = HERE.parent / "2026-08-02-candidate-tail-census"
_TRACK_B = HERE.parent / "2026-07-30-track-b-cap-selection"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (str(_CTC), str(_TRACK_B)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ctc_census inserts api/src and builder/src into sys.path at import time.
from ctc_census import MB_RELEASE_GROUP, candidate_population, pass_artist  # noqa: E402
from cb_metrics import ADOPTED, ADOPTED_SHA  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_builder.no_release_drop import load_drop_mbids  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, PRODUCTION_ALGORITHM  # noqa: E402

OUT = HERE / "fcf_census.json"

WORKED_INSTANCES = {
    "7e4f57b3-569f-4cde-9ad8-87d9a474fd41": "田島賢",
    "f62c24cd-6101-4588-a3e9-d364fe358cc3": "TJ Brown",
}


def adopted_population() -> set[str]:
    """The adopted artifact's artists, sha-verified first."""
    actual = sha256(ADOPTED.read_bytes()).hexdigest()
    if actual != ADOPTED_SHA:
        raise SystemExit(f"adopted artifact mismatch: {actual} != {ADOPTED_SHA}")
    population = set(GraphStore.load(ADOPTED).mbids)
    print(f"adopted population: {len(population):,} (sha verified)", flush=True)
    return population


def credit_split(wanted: set[str]) -> tuple[dict, dict, dict]:
    """One streaming pass over the release-group dump: total / sole / first.

    Offset bookkeeping is not needed here (no checkpoint: the pass is ~2.4 min,
    cheaper than the machinery), but iteration is binary-mode line streaming,
    the same idiom as every other reader of these dumps.
    """
    total: dict[str, int] = defaultdict(int)
    sole: dict[str, int] = defaultdict(int)
    first: dict[str, int] = defaultdict(int)
    began = time.time()
    seen = 0
    with MB_RELEASE_GROUP.open("rb") as fh:
        for line in fh:
            seen += 1
            record = json.loads(line)
            credits = record.get("artist-credit") or []
            for position, credit in enumerate(credits):
                mbid = ((credit or {}).get("artist") or {}).get("id")
                if mbid not in wanted:
                    continue
                total[mbid] += 1
                if len(credits) == 1:
                    sole[mbid] += 1
                elif position == 0:
                    first[mbid] += 1
            if seen % 500_000 == 0:
                print(f"  release-group: {seen:,} scanned, "
                      f"{len(total):,} artists hit", flush=True)
    print(f"  release-group pass: {len(total):,} of {len(wanted):,} artists have "
          f"a credit, in {(time.time() - began) / 60:.1f} min", flush=True)
    return dict(total), dict(sole), dict(first)


def main() -> None:
    if not MB_RELEASE_GROUP.exists():
        raise SystemExit(f"missing dump: {MB_RELEASE_GROUP}")

    adopted = adopted_population()
    candidate = candidate_population()
    wanted = adopted | candidate
    print(f"union: {len(wanted):,}", flush=True)

    total, sole, first = credit_split(wanted)

    # The class: >= 1 credit, none of them sole. Computed over the union so
    # one artist-dump pass covers both populations' members.
    members = {m for m in wanted if total.get(m, 0) > 0 and sole.get(m, 0) == 0}

    # Consistency check: the class is disjoint from both no-release drop lists
    # by construction (those artists have ZERO release-group credits). A
    # non-empty intersection means the detector or the census is wrong.
    for algorithm in (PRODUCTION_ALGORITHM, CANDIDATE_ALGORITHM):
        overlap = members & load_drop_mbids(algorithm)
        if overlap:
            raise SystemExit(
                f"class overlaps the {algorithm} drop list: {len(overlap)}"
            )
    print("disjointness check against both drop lists: clean", flush=True)

    signals = pass_artist(members)

    dsp = {m for m in members if (signals.get(m) or {}).get("dsp")}
    discogs_id = {m for m in members if (signals.get(m) or {}).get("discogs")}
    discogs_raw = json.loads(
        (_REL / "rel_discogs_raw.json").read_text(encoding="utf-8")
    )
    discogs_release = {
        m for m in discogs_id
        if discogs_raw.get((signals.get(m) or {}).get("discogs"))
    }
    discogs_unknown = {
        m for m in discogs_id
        if (signals.get(m) or {}).get("discogs") not in discogs_raw
    }

    def block(population: set[str], label: str) -> dict:
        mine = members & population
        types = Counter((signals.get(m) or {}).get("type") or "None" for m in mine)
        out = {
            "population": len(population),
            "class": len(mine),
            "share_of_population": round(len(mine) / len(population), 4),
            "of_class_first_listed_on_any_multi_credit": sum(
                1 for m in mine if first.get(m, 0) > 0
            ),
            "of_class_with_dsp_link": len(mine & dsp),
            "of_class_with_discogs_id": len(mine & discogs_id),
            "of_class_with_known_discogs_release": len(mine & discogs_release),
            "of_class_discogs_id_uncensused_by_REL": len(mine & discogs_unknown),
            "artist_type_split": dict(types.most_common()),
        }
        print(f"\n{label}: class {out['class']:,} of {out['population']:,} "
              f"({100 * out['share_of_population']:.1f}%), "
              f"{out['of_class_with_dsp_link']:,} with a DSP link", flush=True)
        return out

    adopted_block = block(adopted, "ADOPTED (ALG-E)")
    candidate_block = block(candidate, "CANDIDATE (ALG-B)")

    worked = {}
    for mbid, name in WORKED_INSTANCES.items():
        worked[mbid] = {
            "name": name,
            "in_class": mbid in members,
            "total_rg_credits": total.get(mbid, 0),
            "sole_credits": sole.get(mbid, 0),
            "first_listed_multi_credits": first.get(mbid, 0),
            "signals": signals.get(mbid),
            "in_adopted": mbid in adopted,
            "in_candidate": mbid in candidate,
        }
        print(f"\nworked instance {name} ({mbid[:8]}): "
              f"in_class={worked[mbid]['in_class']} "
              f"total={worked[mbid]['total_rg_credits']} "
              f"sole={worked[mbid]['sole_credits']} "
              f"first={worked[mbid]['first_listed_multi_credits']} "
              f"dsp={(signals.get(mbid) or {}).get('dsp')}", flush=True)

    clip_targets = len(dsp)
    payload = {
        "status": "DIAGNOSTIC. Sizes the featured-credit class. Adopts nothing.",
        "class_rule": (
            ">= 1 release-group credit of any shape, none of them sole. Sole "
            "is rg_artist_id(record) == mbid alone -- no type exclusions; see "
            "the module docstring for why rel_rg_raw.json's flag is not this."
        ),
        "union": len(wanted),
        "class_union": len(members),
        "adopted": adopted_block,
        "candidate": candidate_block,
        "worked_instances": worked,
        "clip_stage_estimate": {
            "targets_with_dsp_link_union": clip_targets,
            "note": (
                "Only DSP-linked members go to the clip stage (the keep-check "
                "cuts the rest regardless of clip, tail_droplist.py:112). "
                "~45 min per 1,400 artists, tail_clips.py measured."
            ),
            "hours": round(clip_targets / 1400 * 45 / 60, 1),
        },
        "class_mbids": sorted(members),
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"\nFEATURED-CREDIT CLASS: {len(members):,} across the union; "
          f"clip stage ~{payload['clip_stage_estimate']['hours']} h "
          f"for {clip_targets:,} DSP-linked members", flush=True)
    print(f"-> {OUT.name}", flush=True)


if __name__ == "__main__":
    main()
