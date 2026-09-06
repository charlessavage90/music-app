"""Frozen MusicBrainz artist -> Spotify / Apple Music artist id maps
(2026-09-05 snapshot).

WHY IT EXISTS
`LUX-4` puts a "listen on" link on every journey card. MusicBrainz already
records URL relations to both services, so the ids are free and exact -- no
name search, and therefore none of the wrong-same-named-artist risk that
`BYP-13` is about.

ONE MAP FOR ANY ARCHIVE -- and that is NOT the drop-list mistake repeated
A Spotify id is a PROPERTY OF AN ARTIST, exactly as a Deezer id is: an MBID
maps to the same Spotify artist whatever similarity archive is being built.
`no_release_drop.py` is per-archive because it encodes a DECISION ABOUT A
POPULATION; this does not. A missing id degrades to a search URL, which is a
coverage gap and never a wrong answer.

WHY IDS AND NOT URLS (`L4-D2`)
The id tail is stored and the frontend composes the URL. Storing full URLs
would bake a hostname into every entry and into every artifact forever, and a
URL-scheme change would then need a rebuild rather than a frontend edit.

IDS ARE NORMALISED AT EXTRACTION, AND THE APPLE ONES HAD TO BE
MusicBrainz records the same Apple artist under two URL shapes --
`music.apple.com/us/artist/name/657515` and
`itunes.apple.com/us/artist/name/id657515` -- which yield different tails for
one artist. Every Apple id here is the bare numeric form; the `id` prefix is
stripped during extraction so ONE URL template works for all of them. Spotify
ids are 22-character base62 and anything else is rejected rather than shipped
(a `spotify:artist:` URI url-encoded into a URL field was the case in the
2026-07-28 dump). Rejection happens during extraction, never afterwards, so a
malformed relation cannot consume an artist's slot and block a later valid one.

A DATED SNAPSHOT, like the drop lists and `deezer_ids`
The build must never re-resolve these over the network: `build_from_archive`
is offline by a hard rule and spec section 9 requires byte-identical output
for identical input.

STANDING OBLIGATION -- the same one `deezer_ids.py` carries, and it is
discharged by the same act. Extracted over a population that is the union of
the served artifact (sha 43dd82bb...) and both 2026-08-02-era artifacts.
Before a DIFFERENT artifact is ever served, re-extract over its population.
An artist outside the extracted population gets no id and falls back to a
search link.

  WHY THE UNION AND NOT JUST THE SERVED MAP: `deezer_ids.py` was extracted
  over the two 2026-08-02 artifacts alone, and the served map -- built four
  days later from a LATER ALG-B crawl -- has 2,687 artists in neither, all of
  which consequently carry no Deezer id at all. Figures and the consequence:
  builder/analysis/2026-09-05-lux4-extract/README.md, sections 1 and 4.

Source and figures owner: builder/analysis/2026-09-05-lux4-extract/.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# sha256 of json.dumps(sorted(<map>.items()), sort_keys=True), reproduced by
# builder/analysis/2026-09-05-lux4-extract/lux4_extract.py.
SPOTIFY_IDS_SHA256 = "e618b286ae93d6b52c211a04b1195be03d6f804040c572265d125ca599dc4595"
APPLE_IDS_SHA256 = "e33f67d22485c1817b3a0c7cabad5bc732d472d07531b3c5d74644cf0693e5a9"

DSP_LINKS_PATH = Path(__file__).parent / "data" / "dsp_links_20260905.json"


@lru_cache(maxsize=1)
def load_dsp_links() -> tuple[dict[str, str], dict[str, str]]:
    """(spotify_ids, apple_ids), MBID -> platform id tail.

    An artist absent from either map has no recorded link on that service and
    the frontend falls back to a search URL. Absence is the normal case for
    roughly a third of the map and is never an error.
    """
    payload = json.loads(DSP_LINKS_PATH.read_text(encoding="utf-8"))
    return payload["spotify_ids"], payload["apple_ids"]
