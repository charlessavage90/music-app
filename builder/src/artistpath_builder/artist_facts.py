"""Frozen MusicBrainz structured artist facts (2026-09-05 snapshot).

WHY STRUCTURED FIELDS AND NOT PROSE (spec section 4.5)
A prose description is DROPPED, not deferred. MusicBrainz holds no
biographies; Wikipedia shares the fame floor and would be rich for the famous
and empty for everyone this app exists to find; Last.fm is barred; and
LLM-generated prose was rejected on HARM, because the hallucination rate is
inversely correlated with fame -- it would publish invented biographical
claims about real, often living, often obscure musicians, with the errors
concentrated on the people least able to notice them.

Structured facts orient without pre-empting the verdict -- "German duo,
1993-2008" tells you where you are and gets out of the way -- and they cannot
be wrong. Do not re-open this as "we could just use Wikipedia for the ones
that have it": that IS the fame floor, considered and declined.

Genre tags are DEFERRED, not dropped (spec section 4.6). `LUX-E6` gates them.

ABSENCE IS THE EMPTY STATE (`L4-D3`)
An artist with nothing to say is ABSENT from this map, never present with an
empty dict, and an individual missing field is omitted rather than stored as
null. A present-but-empty entry would make the frontend render a blank row it
has no way to distinguish from a real one.

  The exception, and it is deliberate: `end` and `ended` are kept even when
  falsy. `"ended": false` is the POSITIVE claim that an artist is still
  active, which is not the same as not knowing.

Same freezing, sha-pinning and re-extraction obligation as `dsp_links.py`:
extracted over the union of the served artifact and both 2026-08-02-era
artifacts, never re-resolved at build time (`build_from_archive` is offline by
a hard rule; spec section 9 requires byte-identical output for identical
input). Before a DIFFERENT artifact is served, re-extract over its population.

Coverage is measured and owned by
builder/analysis/2026-09-05-lux4-extract/README.md section 3 -- read it there.
That section is NOT a `LUX-E2` read: `LUX-E2`'s threshold is stated over
delivered cards on a sample, and it remains blocked. That section is
NOT a `LUX-E2` read: `LUX-E2`'s threshold is stated over delivered cards on a
sample, and it remains blocked.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# sha256 of json.dumps(sorted(artist_facts.items()), sort_keys=True),
# reproduced by builder/analysis/2026-09-05-lux4-extract/lux4_extract.py.
ARTIST_FACTS_SHA256 = "f55d3369986db8b4e4b62c082d6a608d430b3bf91929998abfadbff072d3b88b"

ARTIST_FACTS_PATH = Path(__file__).parent / "data" / "artist_facts_20260905.json"


@lru_cache(maxsize=1)
def load_artist_facts() -> dict[str, dict]:
    """MBID -> the structured fields MusicBrainz records for that artist.

    Keys, all optional: `type`, `country`, `area`, `begin`, `end`, `ended`.
    An artist with none is absent from the mapping entirely.
    """
    payload = json.loads(ARTIST_FACTS_PATH.read_text(encoding="utf-8"))
    return payload["artist_facts"]
