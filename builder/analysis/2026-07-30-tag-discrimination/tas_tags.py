"""TAS tag frame: union-genre labels for every node of the adopted artifact.

TRANSPORT: ListenBrainz batched metadata, 50 MBIDs per request. COH-5
measured it 99.9% identical to MusicBrainz direct and ~29x faster -- full
artifact in ~47 minutes against ~21 hours. LB is a TRANSPORT for MB's data
here, not an independent source; the shared-blind-spot hazard is about FAME
signal and does not transfer to this fidelity question.

VOCABULARY (spec section 1): LB genre-whitelisted tags UNION Wikidata P136,
through the frozen ct_common.norm_genre. NOT the widest tag union -- COH-6
measured that as near-identical in the tail.

THE P136 HALF DOES NOT COME FROM THE FPC OR COH OUTPUTS, AND THE PLAN WAS
WRONG ABOUT THIS. fp_wikidata.json holds item presence (qid, wikis, enwiki),
no genres at all; ct_wikidata_genres.json holds genre COUNTS ({"genres": 10}),
not labels, because COH-1 only ever needed presence. Labels are collected by
tas_wikidata.py, which is why that file exists. Run it first.

Resumable: re-run after any interruption; it re-fetches nothing.

Run from `builder/` (~47 min, unattended):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_tags.py
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
from typing import Any

from tas_common import HERE, get_json, graph_mbids, load_partial, norm_genre, save_partial
from tas_wikidata import OUT_RAW as WIKIDATA_RAW

_COH = HERE.parent / "2026-07-30-coherence-tag-probe"
if str(_COH) not in sys.path:
    sys.path.insert(0, str(_COH))
from ct_lb_metadata import parse_artists  # noqa: E402

LB_URL = "https://api.listenbrainz.org/1/metadata/artist/?%s"
BATCH = 50
PAUSE = 0.3
OUT_RAW = HERE / "tas_tags_raw.json"
OUT = HERE / "tas_tags.json"


def merge_union_genre(lb_record: dict | None, wd_labels: list[str]) -> set[str]:
    """Union genre for one artist. Genre-whitelisted only, never all tags.

    Empty normalised labels are dropped: norm_genre can return "" for a label
    that is only punctuation, and an empty string would otherwise read as a
    genre shared by every artist carrying one -- a false agreement.
    """
    out: set[str] = set()
    if lb_record:
        out |= {norm_genre(g) for g in lb_record.get("genres", [])}
    out |= {norm_genre(label) for label in wd_labels}
    return {label for label in out if label}


def collect() -> dict[str, Any]:
    mbids = graph_mbids()
    done: dict[str, Any] = load_partial(OUT_RAW)
    pending = [m for m in mbids if m not in done]
    print(f"{len(done)} already done, {len(pending)} to fetch", flush=True)
    began = time.time()
    for start in range(0, len(pending), BATCH):
        chunk = pending[start : start + BATCH]
        qs = urllib.parse.urlencode({"artist_mbids": ",".join(chunk), "inc": "tag"})
        status, payload = get_json(LB_URL % qs, timeout=120)
        if status != 200:
            raise RuntimeError(f"LB returned {status}")
        got = parse_artists(payload)
        for mbid in chunk:
            done[mbid] = got.get(mbid)  # absent = LB knows nothing for it
        save_partial(OUT_RAW, done)
        seen = min(start + BATCH, len(pending))
        if seen % 2500 < BATCH:
            rate = seen / max(time.time() - began, 1e-9)
            print(f"  lb {seen}/{len(pending)} ({rate:.1f}/s)", flush=True)
        time.sleep(PAUSE)
    return done


def label_sets() -> dict[str, set[str]]:
    """MBID -> union genre set for EVERY graph node; empty where unlabelled."""
    lb = load_partial(OUT_RAW)
    wd = load_partial(WIKIDATA_RAW)
    return {
        mbid: merge_union_genre(lb.get(mbid), (wd.get(mbid) or {}).get("genres", []))
        for mbid in graph_mbids()
    }


def main() -> None:
    # LB collection is independent of Wikidata -- different endpoint, different
    # raw file -- so the two collectors can run in parallel and this does not
    # gate them. The guard sits before the SUMMARY, which is the first thing
    # that actually reads both halves.
    collect()

    wd = load_partial(WIKIDATA_RAW)
    missing = [m for m in graph_mbids() if m not in wd]
    if missing:
        raise SystemExit(
            f"the P136 half is incomplete: {len(missing)} of {len(graph_mbids())} "
            f"artists absent from {WIKIDATA_RAW.name}. Run tas_wikidata.py to "
            "completion, then re-run this (LB collection above is already saved "
            "and will not refetch). Existence alone is NOT enough -- a partial "
            "frame would silently read as 'these artists have no genres'."
        )

    sets = label_sets()
    labelled = sum(1 for s in sets.values() if s)
    OUT.write_text(
        json.dumps(
            {
                "nodes": len(sets),
                "labelled": labelled,
                "labelled_share": round(labelled / len(sets), 4),
                "mean_labels_where_labelled": round(
                    sum(len(s) for s in sets.values()) / max(labelled, 1), 2
                ),
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"{labelled}/{len(sets)} labelled -> {OUT.name}")


if __name__ == "__main__":
    main()
