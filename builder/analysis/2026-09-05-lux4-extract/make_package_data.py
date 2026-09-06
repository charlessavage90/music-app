"""Turn the extraction payloads into shipped package data, and pin the shas.

Kept as a script rather than done by hand because it is the step where a
payload and the module that vouches for it can silently drift apart. It writes
both data files and rewrites both modules' sha constants from the SAME read, so
they cannot disagree.

TRIMMED, following `deezer_artist_ids_20260802.json`: package data carries the
header prose, the identity sha and the map. Coverage tables and counts stay in
the analysis payload and the README, which own the figures.

Run from `builder/`:
    UV_LINK_MODE=copy uv run python analysis/2026-09-05-lux4-extract/make_package_data.py
"""

from __future__ import annotations

import io
import json
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE.parents[1] / "src" / "artistpath_builder"
DATA = SRC / "data"

_POPULATION = (
    "union of the served artifact graph-msw-tu50.bin (43dd82bb...) and both "
    "2026-08-02-era artifacts; a superset is safe by construction and keeps a "
    "future build of either lineage covered"
)
_DUMP = "MusicBrainz JSON artist dump, 2026-07-28"
_SOURCE = "analysis/2026-09-05-lux4-extract/"


def _sha_items(m: dict) -> str:
    return sha256(json.dumps(sorted(m.items()), sort_keys=True).encode()).hexdigest()


def _write(path: Path, payload: dict) -> None:
    """Compact, and pinned so the generator reproduces its own output."""
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def _pin(module: Path, constant: str, value: str) -> None:
    """Rewrite one sha constant in place, refusing if it is already correct."""
    text = io.open(module, encoding="utf-8").read()
    import re

    pattern = re.compile(rf'^{constant} = "[^"]*"$', re.MULTILINE)
    if not pattern.search(text):
        raise SystemExit(f"{module.name}: no assignment for {constant}")
    io.open(module, "w", encoding="utf-8").write(
        pattern.sub(f'{constant} = "{value}"', text)
    )
    print(f"  pinned {constant} = {value[:16]}...")


def main() -> None:
    links = json.loads((HERE / "dsp_links.json").read_text(encoding="utf-8"))
    facts = json.loads((HERE / "artist_facts.json").read_text(encoding="utf-8"))

    spotify = links["spotify_ids"]
    apple = links["apple_ids"]
    artist_facts = facts["artist_facts"]

    # Recomputed here rather than copied from the payload's own key: the point
    # of the identity block is to catch a file that no longer matches it.
    spotify_sha = _sha_items(spotify)
    apple_sha = _sha_items(apple)
    facts_sha = _sha_items(artist_facts)
    for name, computed, recorded in (
        ("spotify_ids", spotify_sha, links["spotify_ids_sha256"]),
        ("apple_ids", apple_sha, links["apple_ids_sha256"]),
        ("artist_facts", facts_sha, facts["artist_facts_sha256"]),
    ):
        if computed != recorded:
            raise SystemExit(
                f"{name}: payload disagrees with its own identity block\n"
                f"  recorded {recorded}\n  computed {computed}"
            )

    _write(
        DATA / "dsp_links_20260905.json",
        {
            "status": (
                "Frozen 2026-09-05 snapshot. MusicBrainz artist -> Spotify and "
                "Apple Music artist id. Never re-resolved at build time."
            ),
            "purpose": (
                "Deep-link a journey card to the artist on each service. Ids, "
                "not URLs (L4-D2): the frontend composes the URL."
            ),
            "dump": _DUMP,
            "population": _POPULATION,
            "ids_are_normalised": (
                "Apple ids are the bare numeric form; MusicBrainz records the "
                "same artist as .../657515 and .../id657515 and the id prefix "
                "is stripped at extraction so one URL template works. Spotify "
                "ids are 22-char base62; anything else is rejected."
            ),
            "source": _SOURCE,
            "spotify_ids_sha256": spotify_sha,
            "apple_ids_sha256": apple_sha,
            "spotify_ids": dict(sorted(spotify.items())),
            "apple_ids": dict(sorted(apple.items())),
        },
    )
    _write(
        DATA / "artist_facts_20260905.json",
        {
            "status": (
                "Frozen 2026-09-05 snapshot of structured MusicBrainz artist "
                "fields. Never re-resolved at build time."
            ),
            "purpose": (
                "Orient a listener on a journey card without prose. Prose is "
                "DROPPED not deferred (spec 4.5); tags are DEFERRED not "
                "dropped (spec 4.6)."
            ),
            "dump": _DUMP,
            "population": _POPULATION,
            "absence_is_the_empty_state": (
                "An artist with no facts is absent; a missing field is omitted "
                "rather than null. end/ended are kept when falsy because "
                '"ended: false" is the positive claim that an artist is active.'
            ),
            "source": _SOURCE,
            "artist_facts_sha256": facts_sha,
            "artist_facts": dict(sorted(artist_facts.items())),
        },
    )

    for path in (DATA / "dsp_links_20260905.json", DATA / "artist_facts_20260905.json"):
        print(f"wrote {path.name}  {path.stat().st_size / 1024:,.0f}K")

    _pin(SRC / "dsp_links.py", "SPOTIFY_IDS_SHA256", spotify_sha)
    _pin(SRC / "dsp_links.py", "APPLE_IDS_SHA256", apple_sha)
    _pin(SRC / "artist_facts.py", "ARTIST_FACTS_SHA256", facts_sha)


if __name__ == "__main__":
    main()
