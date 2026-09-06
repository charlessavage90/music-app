"""LUX-4 extraction: Spotify/Apple artist ids and structured artist facts.

ONE offline pass over the MusicBrainz artist dump produces both payloads, so
the info card and the streaming links ship on ONE rebuild. That pairing is the
point of `LUX-4`; splitting it costs a second rebuild.

WHY THIS IS A NEW SCRIPT RATHER THAN AN EDIT TO `2026-08-02-dsp-ids/dsp_ids.py`
  The plan said to modify that script and reuse the population set it already
  builds. Two things make that wrong, both measured 2026-09-05:

  1. **Its population does not cover the served map.** It scans the union of
     `graph-t15-tiebreakfix.bin` and `graph-algb-full.bin` -- the artifacts
     adopted and under test on 2026-08-02. The map the app serves today,
     `graph-msw-tu50.bin`, was built four days later from a LATER ALG-B crawl,
     and **2,687 of its 58,838 artists (4.6%) are in neither**. That script's
     docstring argues its ALG-B build is "a superset of anything a final ALG-B
     build produces" -- true for a build from the 2026-07-30 archive, and false
     across the crawl extension that followed. Reusing it would silently omit
     links and facts for 4.6% of every journey.
  2. **Its outputs are pinned.** `deezer_ids.py` ships a map whose sha is
     reproduced by that script; re-running it with a different population
     changes that sha and breaks the shipped map's reproduction claim. A
     frozen probe's value is that it is frozen.

  So: that script and its outputs are untouched, and this one owns the LUX-4
  payloads and their figures.

POPULATION: the union of all three artifacts, verified by sha before reading.
  A superset is safe by construction -- an MBID absent from a given build is a
  no-op -- and it means a future build of either lineage stays covered. Banding
  is against the SERVED map's popularity percentiles; artists outside it cannot
  be banded and are excluded from the band table rather than folded into a band
  they are not in.

  The percentile computed here is a RANK. `pop_raw` in the artifact is a value
  and never a rank (log section 2.12); the two are not interchangeable.

A DATED SNAPSHOT, like the drop lists. The dump is the 2026-07-28 MusicBrainz
export. The build must NEVER re-resolve these over the network:
`build_from_archive` is offline by a hard rule and spec section 9 requires
byte-identical builds. Refreshing is a deliberate act.

WHAT THIS DELIBERATELY DOES NOT DO: it does not re-extract Deezer ids. The
shipped Deezer map carries the same 4.6% gap described above -- all 2,687 of
those artists have no recorded id and can only resolve a clip by NAME SEARCH,
which is the `BYP-13` exposure. Refreshing it here would change the artifact's
existing `deezer_ids` key and so break `L4-T7`'s control arm, whose whole job is
to prove this change touches nothing that already existed. Recorded as its own
finding in README.md; the fix is the owner's call and its own track.

Read-only, offline, no network. Minutes over the 17 GB dump -- run with
`python -u`, or it writes a 0-byte log and looks dead while working.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 \
        uv run python analysis/2026-09-05-lux4-extract/lux4_extract.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
for _p in (ROOT / "api" / "src",):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402

DUMP = ROOT / "builder/scratch/mb-json-dumps/artist/mbdump/artist"
SCRATCH = ROOT / "builder/scratch"

# Every artifact is verified against its recorded sha before a byte is read.
# Several graphs sit in scratch/ and they are NOT interchangeable.
SERVED = SCRATCH / "graph-msw-tu50.bin"
SERVED_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
ALGB_FULL = SCRATCH / "graph-algb-full.bin"
ALGB_FULL_SHA = "d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f"
T15 = SCRATCH / "graph-t15-tiebreakfix.bin"
T15_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

DSP = {
    "open.spotify.com": "spotify",
    "spotify.com": "spotify",
    "music.apple.com": "apple",
    "itunes.apple.com": "apple",
    "deezer.com": "deezer",
    "tidal.com": "tidal",
    "listen.tidal.com": "tidal",
}

# LUX-4 adds spotify to what 2026-08-02 kept. Named rather than inline so a
# test can assert it and the next platform is a one-line change in one place.
# Deezer is deliberately ABSENT: see the docstring's final paragraph.
KEPT_PLATFORMS = ("apple", "spotify")

BANDS = ["top 1%", "90-99%", "50-90%", "10-50%", "bottom 10%"]


def host_of(url: str) -> str:
    if "://" not in url:
        return ""
    h = url.split("/")[2].lower()
    return h[4:] if h.startswith("www.") else h


def id_tail(url: str) -> str:
    """The platform id at the end of a relation URL.

    Any query string is stripped first: MusicBrainz records Apple links with
    locale parameters (`?l=en`) often enough to matter.
    """
    return url.split("?")[0].rstrip("/").split("/")[-1]


# Spotify web ids are 22-character base62. Apple artist ids are numeric, but
# MusicBrainz records them under TWO URL shapes -- music.apple.com/.../657515
# and itunes.apple.com/.../id657515 -- which yield different tails for the same
# artist. Normalising here rather than in the frontend means one id shape ships
# and the URL template stays a single string.
_SPOTIFY_ID = re.compile(r"[A-Za-z0-9]{22}\Z")
_APPLE_ID = re.compile(r"(?:id)?([0-9]+)", re.IGNORECASE)


def is_artist_url(url: str) -> bool:
    """Does this relation point at an ARTIST page rather than an album?

    MusicBrainz artist records carry a handful of relations to albums and
    playlists alongside the artist pages -- 27 album and 2 playlist URLs in the
    first 200,000 records of the 2026-07-28 dump, against 80,549 artist ones.
    A Spotify ALBUM id is also 22-character base62, so `normalise_id` cannot
    tell one from the other and would ship an album link on an artist card.
    Both services put the entity kind in the path, so check that instead.
    """
    segments = [seg for seg in url.split("?")[0].split("/") if seg]
    return "artist" in segments


def normalise_id(platform: str, tail: str) -> str:
    """The platform id, or "" if this relation does not carry a usable one.

    Returning "" rather than storing junk is load-bearing: the caller uses
    `setdefault`, so a rejected id must NOT consume the slot -- an artist whose
    first relation is malformed can still be rescued by a later, valid one.
    That is why this runs during extraction and not as a post-pass over the
    written payload, where the losing relations are already gone.

    Observed in the 2026-09-05 dump and each rejected or repaired here:
      `id1227497528`  15,140 iTunes-shaped Apple ids -> `1227497528`
      `id293029227#`  a trailing fragment
      `artist%3ALost%20Children%20Of%20Babylon`  a `spotify:` URI in a URL field
    """
    if platform == "spotify":
        return tail if _SPOTIFY_ID.fullmatch(tail) else ""
    if platform == "apple":
        m = _APPLE_ID.fullmatch(tail)
        return m.group(1) if m else ""
    return ""


def clean_date(value: str | None) -> str | None:
    """A MusicBrainz date, or None if it has no usable year.

    MusicBrainz partial dates can omit the YEAR while keeping month and day --
    `????-06-05`. 404 artists in the 2026-07-28 dump carry one, and rendered
    verbatim they would put "????-06-05" on a card. A date with no year cannot
    say when an artist began or ended, so it is treated as absent.
    """
    if not value:
        return None
    return value if re.match(r"^\d{4}", value) else None


def facts_of(record: dict) -> dict:
    """The structured MusicBrainz fields the info card renders.

    Absent fields are OMITTED rather than stored as null, and an artist with
    nothing to say yields `{}` and is left out of the map entirely (`L4-D3`:
    absence is the empty state). The exception is `end`/`ended`, which are
    meaningful when falsy -- "ended: false" is the positive claim that an
    artist is still active, which is not the same as not knowing.
    """
    facts: dict = {}
    if record.get("type"):
        facts["type"] = record["type"]
    if record.get("country"):
        facts["country"] = record["country"]
    area = record.get("area") or {}
    if area.get("name"):
        facts["area"] = area["name"]
    span = record.get("life-span") or {}
    begin = clean_date(span.get("begin"))
    end = clean_date(span.get("end"))
    if begin:
        facts["begin"] = begin
    # Cleaned values, deliberately: a life span whose only dates are yearless
    # carries no information and must not produce an `end`/`ended` pair either.
    if begin or end:
        facts["end"] = end
        facts["ended"] = bool(span.get("ended"))
    return facts


def band_of(pctl: float) -> str:
    if pctl >= 99.0:
        return "top 1%"
    if pctl >= 90.0:
        return "90-99%"
    if pctl >= 50.0:
        return "50-90%"
    if pctl >= 10.0:
        return "10-50%"
    return "bottom 10%"


def _verify(path: Path, expected: str) -> None:
    if not path.exists():
        raise SystemExit(f"missing artifact: {path}")
    actual = sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(
            f"{path.name} sha mismatch -- refusing to extract\n"
            f"  expected {expected}\n  actual   {actual}"
        )


def _write(path: Path, payload: dict) -> None:
    """Compact on disk, deliberately.

    These are machine-read maps of ~90k artists; `indent=1` cost 3.5 MB of
    permanently-committed repo for a file nobody reads by eye. The separators
    are pinned here so the script and its committed output stay byte-identical
    -- a payload whose generator no longer reproduces it is not frozen data,
    it is a coincidence.
    """
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def _sha_items(m: dict) -> str:
    return sha256(json.dumps(sorted(m.items()), sort_keys=True).encode()).hexdigest()


def main() -> None:
    for path, expected in (
        (SERVED, SERVED_SHA),
        (ALGB_FULL, ALGB_FULL_SHA),
        (T15, T15_SHA),
    ):
        _verify(path, expected)
    if not DUMP.exists():
        raise SystemExit(f"artist dump not found at {DUMP}")

    served = GraphStore.load(SERVED)
    served_set = set(served.mbids)
    other = set(GraphStore.load(ALGB_FULL).mbids) | set(GraphStore.load(T15).mbids)
    population = served_set | other
    print(
        f"served {len(served_set):,}  other-lineages {len(other):,}  "
        f"population {len(population):,}  "
        f"served-only {len(served_set - other):,}",
        flush=True,
    )

    pop = np.asarray(served.pop_raw, dtype=np.float64)
    order = pop.argsort()
    ranks = np.empty(len(pop))
    ranks[order] = np.arange(len(pop)) / max(1, len(pop) - 1) * 100.0
    band_by_mbid = {m: band_of(float(ranks[i])) for i, m in enumerate(served.mbids)}

    spotify: dict[str, str] = {}
    apple: dict[str, str] = {}
    artist_facts: dict[str, dict] = {}
    seen_in_dump: set[str] = set()
    rejected: Counter = Counter()
    scanned = 0

    with DUMP.open(encoding="utf-8") as f:
        for line in f:
            scanned += 1
            if scanned % 500_000 == 0:
                print(
                    f"  ...{scanned:,} scanned, {len(spotify):,} spotify, "
                    f"{len(apple):,} apple, {len(artist_facts):,} facts",
                    flush=True,
                )
            d = json.loads(line)
            mbid = d.get("id")
            if mbid not in population:
                continue
            seen_in_dump.add(mbid)

            facts = facts_of(d)
            if facts:
                artist_facts.setdefault(mbid, facts)

            for r in d.get("relations") or []:
                url = (r.get("url") or {}).get("resource")
                if not url:
                    continue
                platform = DSP.get(host_of(url))
                if platform not in KEPT_PLATFORMS:
                    continue
                usable = is_artist_url(url)
                ident = normalise_id(platform, id_tail(url)) if usable else ""
                if not ident:
                    rejected[platform] += 1
                    continue
                # First VALID wins, deterministically: the dump is read in its
                # own order and setdefault makes a later relation a no-op.
                target = spotify if platform == "spotify" else apple
                target.setdefault(mbid, ident)

    # --- LUX-E3: coverage by popularity band, over the SERVED map ------------
    total: Counter = Counter()
    s_band: Counter = Counter()
    a_band: Counter = Counter()
    f_band: Counter = Counter()
    for m in served_set:
        b = band_by_mbid[m]
        total[b] += 1
        if m in spotify:
            s_band[b] += 1
        if m in apple:
            a_band[b] += 1
        if m in artist_facts:
            f_band[b] += 1

    hdr = (
        f"{'band':<12}{'artists':>9}{'spotify':>9}{'apple':>9}{'facts':>9}"
        f"{'spotify %':>11}{'apple %':>9}"
    )
    print()
    print(hdr)
    print("-" * len(hdr))
    for b in BANDS:
        t = total[b]
        print(
            f"{b:<12}{t:>9,}{s_band[b]:>9,}{a_band[b]:>9,}{f_band[b]:>9,}"
            f"{(s_band[b] / t * 100 if t else 0):>10.1f}%"
            f"{(a_band[b] / t * 100 if t else 0):>8.1f}%"
        )
    t = sum(total.values())
    print("-" * len(hdr))
    print(
        f"{'SERVED':<12}{t:>9,}{sum(s_band.values()):>9,}"
        f"{sum(a_band.values()):>9,}{sum(f_band.values()):>9,}"
        f"{sum(s_band.values()) / t * 100:>10.1f}%"
        f"{sum(a_band.values()) / t * 100:>8.1f}%"
    )

    served_spotify = {m: i for m, i in spotify.items() if m in served_set}
    served_apple = {m: i for m, i in apple.items() if m in served_set}
    served_facts = {m: v for m, v in artist_facts.items() if m in served_set}

    substrates = {
        "served": {"file": SERVED.name, "sha256": SERVED_SHA},
        "algb_full": {"file": ALGB_FULL.name, "sha256": ALGB_FULL_SHA},
        "t15": {"file": T15.name, "sha256": T15_SHA},
    }
    common = {
        "extracted_at": "2026-09-05",
        "dump": "MusicBrainz JSON artist dump, 2026-07-28",
        "population": (
            "union of the served map and both 2026-08-02-era artifacts; a "
            "superset is safe by construction and keeps a future build of "
            "either lineage covered"
        ),
        "population_sha256": SERVED_SHA,
        "substrates": substrates,
    }

    links = dict(common)
    links.update(
        {
            "status": (
                "Frozen 2026-09-05 snapshot of MusicBrainz artist -> Spotify "
                "and Apple artist id. Never re-resolved at build time."
            ),
            "counts": {
                "population": len(population),
                "matched_in_dump": len(seen_in_dump),
                "spotify_ids": len(spotify),
                "apple_ids": len(apple),
                "spotify_ids_served": len(served_spotify),
                "apple_ids_served": len(served_apple),
                "relations_rejected_as_unusable": dict(rejected),
            },
            "coverage_by_popularity_percentile_band": {
                b: {"artists": total[b], "spotify": s_band[b], "apple": a_band[b]}
                for b in BANDS
            },
            "spotify_ids_sha256": _sha_items(spotify),
            "apple_ids_sha256": _sha_items(apple),
            "spotify_ids": dict(sorted(spotify.items())),
            "apple_ids": dict(sorted(apple.items())),
        }
    )
    _write(HERE / "dsp_links.json", links)

    facts_payload = dict(common)
    facts_payload.update(
        {
            "status": (
                "Frozen 2026-09-05 snapshot of structured MusicBrainz artist "
                "fields. Absent fields are omitted; an artist with no facts is "
                "absent from the map entirely (L4-D3)."
            ),
            "counts": {
                "population": len(population),
                "artist_facts": len(artist_facts),
                "artist_facts_served": len(served_facts),
            },
            "coverage_by_popularity_percentile_band": {
                b: {"artists": total[b], "facts": f_band[b]} for b in BANDS
            },
            "artist_facts_sha256": _sha_items(artist_facts),
            "artist_facts": dict(sorted(artist_facts.items())),
        }
    )
    _write(HERE / "artist_facts.json", facts_payload)

    print(f"rejected relations (not an artist page, or unusable id): {dict(rejected)}")
    print(
        f"\nwrote dsp_links.json    spotify={_sha_items(spotify)[:12]} "
        f"apple={_sha_items(apple)[:12]}"
    )
    print(f"wrote artist_facts.json facts={_sha_items(artist_facts)[:12]}")


if __name__ == "__main__":
    main()
