"""Size the no-release tail of the CANDIDATE (ALG-B) population.

DIAGNOSTIC ONLY. Adopts nothing, fixes no criterion, sets no bar. It applies
the ALREADY-ADOPTED drop rule's two release signals to a second population, so
it has no degrees of freedom to bias: the rule was frozen 2026-08-01 and this
does not reopen it.

WHAT IT IS FOR
  The adopted drop list was censused over the ADOPTED (ALG-E) graph, so it
  covers only 36.6% of the candidate population. Comparing the two data sets
  with the cleanup applied to one and not the other would put an uncontrolled
  variable in the arm that matters. This measures what a candidate-side census
  would cost, by counting how many candidate artists carry neither release
  signal and would therefore go to the expensive clip-resolution stage.

  It deliberately STOPS SHORT of the clip check, which is the multi-hour,
  network-bound half and the only half with a snapshot hazard.

POPULATION
  The union of all twelve built ALG-B cells, each verified against its manifest
  sidecar. A union rather than one cell because the connection rule is not
  decided: a capped cell would under-cover whatever rule wins.

WHAT IS REUSED RATHER THAN RECOMPUTED
  The REL- probe already censused today's population. 51,115 of the candidate's
  74,960 artists are in it, so only the remaining 23,845 need dump passes.
  Re-scanning the covered ones would risk two readers disagreeing.

SOURCES, all local, no network:
  MB artist dump          16.1 GiB   ~2.2 min   discogs id + DSP links
  MB release-group dump   16.8 GiB   ~2.4 min   has >= 1 release group
  Discogs releases XML    57.4 GiB  ~22.2 min   has >= 1 release

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-candidate-tail-census/ctc_census.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import xml.etree.ElementTree as ET

from collections import defaultdict
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (str(ROOT / "api" / "src"), str(ROOT / "builder" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from artistpath_api.graph_store import GraphStore  # noqa: E402

SCRATCH = ROOT / "builder" / "scratch"
CELLS = SCRATCH / "cb-cells"
MB_ARTIST = SCRATCH / "mb-json-dumps" / "artist" / "mbdump" / "artist"
MB_RELEASE_GROUP = SCRATCH / "mb-json-dumps" / "release-group" / "mbdump" / "release-group"
DISCOGS_RELEASES = SCRATCH / "discogs-data-dump" / "discogs_20260601_releases.xml"
OUT = HERE / "ctc_census.json"

# Same convention as rel_artist_dump.discogs_id_of -- matched, not reinvented,
# so the two censuses are comparable rather than merely adjacent.
_DISCOGS_ID = re.compile(r"discogs\.com/artist/(\d+)")

# Same DSP set as tail_signals.py: a link implies a distributor placed the
# catalogue, which is the drop rule's keep-side evidence.
DSP_HOSTS = {
    "open.spotify.com": "spotify", "spotify.com": "spotify",
    "music.apple.com": "apple", "itunes.apple.com": "apple",
    "deezer.com": "deezer", "tidal.com": "tidal", "listen.tidal.com": "tidal",
}


def host_of(url: str) -> str:
    if "://" not in url:
        return ""
    host = url.split("/")[2].lower()
    return host[4:] if host.startswith("www.") else host


def discogs_id_of(record: dict) -> str | None:
    for rel in record.get("relations") or []:
        if rel.get("type") != "discogs":
            continue
        match = _DISCOGS_ID.search((rel.get("url") or {}).get("resource") or "")
        if match:
            return match.group(1)
    return None


def candidate_population() -> set[str]:
    """Union of every built ALG-B cell, each verified against its manifest."""
    population: set[str] = set()
    cells = sorted(CELLS.glob("ALG-B-*.bin"))
    if not cells:
        raise SystemExit(f"no ALG-B cells under {CELLS}")
    for path in cells:
        manifest = json.loads(Path(f"{path}.json").read_text(encoding="utf-8"))
        recorded = manifest.get("sha256") or manifest.get("artifact_sha256")
        if sha256(path.read_bytes()).hexdigest() != recorded:
            raise SystemExit(f"{path.name}: manifest mismatch")
        population |= set(GraphStore.load(path).mbids)
    print(f"population: {len(population):,} from {len(cells)} verified cells", flush=True)
    return population


def pass_artist(wanted: set[str]) -> dict[str, dict]:
    """MB artist dump: discogs id and DSP links for the uncensused artists."""
    found: dict[str, dict] = {}
    began = time.time()
    with MB_ARTIST.open(encoding="utf-8") as fh:
        for line in fh:
            record = json.loads(line)
            mbid = record.get("id")
            if mbid not in wanted:
                continue
            dsps = set()
            for rel in record.get("relations") or []:
                url = (rel.get("url") or {}).get("resource")
                if url and host_of(url) in DSP_HOSTS:
                    dsps.add(DSP_HOSTS[host_of(url)])
            found[mbid] = {
                "discogs": discogs_id_of(record),
                "dsp": sorted(dsps),
                "type": record.get("type"),
            }
            if len(found) % 5_000 == 0:
                print(f"  artist: {len(found):,}/{len(wanted):,} matched", flush=True)
            if len(found) == len(wanted):
                break
    print(f"  artist pass: {len(found):,} matched in "
          f"{(time.time() - began) / 60:.1f} min", flush=True)
    return found


def pass_release_group(wanted: set[str]) -> set[str]:
    """MB release-group dump: which uncensused artists have >= 1 release group."""
    have: set[str] = set()
    began = time.time()
    seen = 0
    with MB_RELEASE_GROUP.open("rb") as fh:
        for line in fh:
            seen += 1
            record = json.loads(line)
            for credit in record.get("artist-credit") or []:
                mbid = ((credit or {}).get("artist") or {}).get("id")
                if mbid in wanted:
                    have.add(mbid)
            if seen % 500_000 == 0:
                print(f"  release-group: {seen:,} scanned, {len(have):,} artists hit",
                      flush=True)
    print(f"  release-group pass: {len(have):,} of {len(wanted):,} have one, in "
          f"{(time.time() - began) / 60:.1f} min", flush=True)
    return have


def pass_discogs(wanted: set[str]) -> set[str]:
    """Discogs releases XML: which discogs artist ids have >= 1 release.

    Presence only -- no labels, no counts. Memory is bounded by clearing the
    root as well as the element; clearing the element alone leaves emptied
    shells attached and the tree still grows over ~20M releases (rel_discogs).
    """
    have: set[str] = set()
    began = time.time()
    seen = 0
    context = ET.iterparse(str(DISCOGS_RELEASES), events=("start", "end"))
    _event, root = next(context)
    for event, elem in context:
        if event != "end" or elem.tag != "release":
            continue
        seen += 1
        artists = elem.find("artists")
        if artists is not None:
            for node in artists:
                artist_id = node.findtext("id")
                if artist_id and artist_id in wanted:
                    have.add(artist_id)
        elem.clear()
        root.clear()
        if seen % 2_000_000 == 0:
            print(f"  discogs: {seen:,} releases, {len(have):,} ids hit "
                  f"({(time.time() - began) / 60:.1f} min)", flush=True)
    print(f"  discogs pass: {len(have):,} of {len(wanted):,} ids have a release, in "
          f"{(time.time() - began) / 60:.1f} min", flush=True)
    return have


def main() -> None:
    for path in (MB_ARTIST, MB_RELEASE_GROUP, DISCOGS_RELEASES):
        if not path.exists():
            raise SystemExit(f"missing dump: {path}")

    population = candidate_population()

    index = json.loads((_REL / "rel_artist_index_raw.json").read_text(encoding="utf-8"))
    rg = json.loads((_REL / "rel_rg_raw.json").read_text(encoding="utf-8"))
    discogs = json.loads((_REL / "rel_discogs_raw.json").read_text(encoding="utf-8"))
    censused = set(index) | set(rg)

    uncensused = population - censused
    print(f"covered by REL-: {len(population & censused):,}; "
          f"needing a pass: {len(uncensused):,}", flush=True)

    artists = pass_artist(uncensused)
    has_rg_new = pass_release_group(uncensused)

    new_discogs_ids = {
        rec["discogs"] for rec in artists.values() if rec.get("discogs")
    } - set(discogs)
    print(f"new discogs ids to check: {len(new_discogs_ids):,}", flush=True)
    has_discogs_new = pass_discogs(new_discogs_ids) if new_discogs_ids else set()

    def has_release_group(mbid: str) -> bool:
        return bool(rg.get(mbid)) if mbid in censused else mbid in has_rg_new

    def has_discogs_release(mbid: str) -> bool:
        if mbid in censused:
            did = (index.get(mbid) or {}).get("discogs")
            return bool(did and discogs.get(did))
        did = (artists.get(mbid) or {}).get("discogs")
        return bool(did and (did in has_discogs_new or discogs.get(did)))

    tail = sorted(
        m for m in population
        if not has_release_group(m) and not has_discogs_release(m)
    )
    with_dsp = [
        m for m in tail
        if (artists.get(m) or {}).get("dsp")
        or (m in censused and False)  # DSP unknown for censused artists here
    ]

    payload = {
        "status": "DIAGNOSTIC. Sizes the candidate-side census. Adopts nothing.",
        "population": {
            "candidate_union_of_cells": len(population),
            "already_censused_by_REL": len(population & censused),
            "freshly_censused_here": len(uncensused),
        },
        "no_release_tail": {
            "count": len(tail),
            "share_of_population": round(len(tail) / len(population), 4),
            "of_which_uncensused_before": sum(1 for m in tail if m in uncensused),
            "with_a_dsp_link_among_freshly_censused": len(with_dsp),
        },
        "note": (
            "The clip-resolution half of the adopted rule is NOT run here. The "
            "tail count is the population that would go to it, so the clip "
            "stage costs roughly 45 min per 1,400 artists from this count."
        ),
        "tail_mbids": tail,
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"\nCANDIDATE NO-RELEASE TAIL: {len(tail):,} of {len(population):,} "
          f"({100 * len(tail) / len(population):.1f}%)", flush=True)
    print(f"clip stage would be ~{len(tail) / 1400 * 45 / 60:.1f} h", flush=True)
    print(f"-> {OUT.name}", flush=True)


if __name__ == "__main__":
    main()
