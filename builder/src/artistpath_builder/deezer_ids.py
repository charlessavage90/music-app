"""Frozen MusicBrainz artist -> Deezer artist id map (2026-08-02 snapshot).

WHY IT EXISTS
`BYP-13` is a live user-facing defect: a card plays a clip by a DIFFERENT
ARTIST OF THE SAME NAME, because the app resolves clips by searching the
artist's name. Measured at 9.4% (denominator 160) and 6.1% (denominator 49).
A MusicBrainz-recorded Deezer artist id names the exact artist, so a clip found
through it cannot be the wrong same-named one. The api tries the id first and
falls back to name search, so a missing id is exactly today's behaviour.

ONE MAP FOR ANY ARCHIVE -- and that is NOT the drop-list mistake repeated
`no_release_drop.py` is per-archive because it encodes a DECISION ABOUT A
POPULATION. A Deezer id is a PROPERTY OF AN ARTIST: an MBID maps to the same
Deezer artist whatever similarity archive is being built, so one map is correct
here where one list was wrong there. The failure modes differ in the way that
matters -- a missing id degrades to name search, while a wrong drop list
silently removes the wrong artists. This fails safe; that failed silent.

Extracted over the ADOPTED artifact's population. An artist outside it gets no
id and falls back to name search: a coverage gap, never a wrong answer. Before
an `ALG-B` artifact is ever served, re-extract over its population -- recorded
as a deferral in NEXT.md.

A DATED SNAPSHOT, like the drop lists
The build must never re-resolve these over the network: `build_from_archive` is
offline by a hard rule and spec section 9 requires byte-identical output for
identical input. Refreshing the map is a deliberate act with its own decision,
not a silent build-time behaviour.

Deezer only. Over the artists the app actually delivers, Deezer alone covers
92.9% of card impressions and adding Apple reaches 94.1%. The Deezer id path is
measured (`tail_clips.py:137`); an Apple-id path has never been run here.
Figures: `builder/analysis/2026-08-02-dsp-ids/dsp_ids.json`.
"""

from __future__ import annotations

import json

from functools import lru_cache
from pathlib import Path

# sha256 of json.dumps(sorted(deezer_ids.items()), sort_keys=True), as recorded
# in NEXT.md and reproduced by builder/analysis/2026-08-02-dsp-ids/dsp_ids.py.
DEEZER_IDS_SHA256 = "7d204111284c7e50450d20af704168d26846a2607f761ef5103eef0514b52fb6"

DEEZER_IDS_PATH = Path(__file__).parent / "data" / "deezer_artist_ids_20260802.json"


@lru_cache(maxsize=1)
def load_deezer_ids() -> dict[str, str]:
    """MBID -> Deezer artist id, for every graph artist MusicBrainz links."""
    payload = json.loads(DEEZER_IDS_PATH.read_text(encoding="utf-8"))
    return payload["deezer_ids"]
