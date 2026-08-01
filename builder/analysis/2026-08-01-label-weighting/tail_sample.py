"""The no-release tail sample: 20 artists for the owner's manual spot check.

DELIBERATELY OUTSIDE THE `WGT-` PRE-REGISTRATION (its §8): descriptive product
research with no criterion and no bar. The question it feeds is the owner's --
do artists with no release on any source we hold belong in a listening journey
at all -- and the answer comes from his manual research, not from anything
computed here. This script only fixes the draw so the sample cannot be
cherry-picked, and enriches each artist with everything we already hold.

POPULATION: graph artists with NO MusicBrainz release group (absent or empty in
the committed `rel_rg_raw.json`) AND NO Discogs release (no bucket through the
committed artist index). Labels are NOT a filter -- an artist page can carry
tags without any release existing.

DRAW: seed fixed below, 4 artists from each within-population popularity
quintile, so the packet shows the range of the tail rather than five copies of
its middle.

CLIP CHECK: the app's own resolution order and name rule -- Deezer search then
iTunes search, accepting a result only when `same_artist` folds equal -- via
plain HTTP with a pause. An artist with no resolvable clip is a silent card in
the app regardless of merit, which is the one mechanical fact worth attaching
before a human spends time.

Run from `builder/` (network: ~40 light requests):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-01-label-weighting/tail_sample.py
"""

from __future__ import annotations

import json
import random
import sys
import time
import urllib.parse
import urllib.request
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (_TAS, _REL, ROOT / "api" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from artistpath_api.clips import same_artist  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from tas_common import ADOPTED, ADOPTED_SHA  # noqa: E402

SEED = "20260801-tail-sample"
PER_BAND = 4
BANDS = 5
PAUSE = 0.6

OUT_JSON = HERE / "tail_sample.json"
OUT_MD = HERE / "TAIL-SAMPLE.md"

DEEZER = "https://api.deezer.com/search?%s"
ITUNES = "https://itunes.apple.com/search?%s"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "artistpath-tail-sample"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def clip_check(name: str) -> dict:
    """The app's resolution order and name rule, one artist, best effort."""
    try:
        body = get_json(DEEZER % urllib.parse.urlencode({"q": name, "limit": 5}))
        for row in body.get("data", []):
            artist = row.get("artist") or {}
            if row.get("preview") and same_artist(artist.get("name"), name):
                return {"resolves": True, "source": "deezer",
                        "track": str(row.get("title") or "")}
    except Exception as e:  # noqa: BLE001 -- a spot check records, never raises
        deezer_err = str(e)
    else:
        deezer_err = None
    time.sleep(PAUSE)
    try:
        body = get_json(ITUNES % urllib.parse.urlencode(
            {"term": name, "entity": "song", "limit": 5}))
        for row in body.get("results", []):
            if row.get("previewUrl") and same_artist(row.get("artistName"), name):
                return {"resolves": True, "source": "itunes",
                        "track": str(row.get("trackName") or "")}
    except Exception as e:  # noqa: BLE001
        return {"resolves": False, "source": None,
                "errors": [x for x in (deezer_err, str(e)) if x]}
    return {"resolves": False, "source": None,
            "errors": [x for x in (deezer_err,) if x]}


def main() -> None:
    digest = sha256(ADOPTED.read_bytes()).hexdigest()
    if digest != ADOPTED_SHA:
        raise SystemExit(f"artifact mismatch: {digest} != {ADOPTED_SHA}")
    store = GraphStore.load(ADOPTED)

    rg = json.loads((_REL / "rel_rg_raw.json").read_text(encoding="utf-8"))
    index = json.loads((_REL / "rel_artist_index_raw.json").read_text(encoding="utf-8"))
    discogs = json.loads((_REL / "rel_discogs_raw.json").read_text(encoding="utf-8"))

    def has_discogs(mbid: str) -> bool:
        did = (index.get(mbid) or {}).get("discogs")
        return bool(did and discogs.get(did))

    ids = [i for i, m in enumerate(store.mbids)
           if not rg.get(m) and not has_discogs(m)]
    print(f"no-release population: {len(ids)} of {len(store.mbids)} artists", flush=True)

    pop = store.pop_raw
    ids.sort(key=lambda i: float(pop[i]))
    rng = random.Random(SEED)
    picked: list[int] = []
    for b in range(BANDS):
        band = ids[b * len(ids) // BANDS: (b + 1) * len(ids) // BANDS]
        picked.extend(sorted(rng.sample(band, min(PER_BAND, len(band)))))

    order = np_rank = sorted(range(len(store.mbids)), key=lambda i: float(pop[i]))
    pctl_of = {i: r / (len(order) - 1) for r, i in enumerate(np_rank)}

    rows = []
    for i in picked:
        name = store.names[i]
        neigh = sorted(store.neighbours_of(i), key=lambda t: -t[1])[:3]
        print(f"  checking clip: {name}", flush=True)
        clip = clip_check(name)
        time.sleep(PAUSE)
        rows.append({
            "mbid": store.mbids[i],
            "name": name,
            "disambiguation": store.disambiguations[i],
            "pop_raw": round(float(pop[i]), 4),
            "pop_pctl_in_graph": round(pctl_of[i], 4),
            "degree": int(sum(1 for _ in store.neighbours_of(i))),
            "top_neighbours": [
                {"name": store.names[j], "score": round(float(s), 3)}
                for j, s in neigh],
            "clip": clip,
            "musicbrainz": f"https://musicbrainz.org/artist/{store.mbids[i]}",
            "youtube_search":
                "https://www.youtube.com/results?"
                + urllib.parse.urlencode({"search_query": name}),
            "spotify_search":
                "https://open.spotify.com/search/" + urllib.parse.quote(name),
        })

    OUT_JSON.write_text(json.dumps({
        "note": "Descriptive product research, outside the WGT- pre-registration "
                "by its §8. No criterion, no bar; the seed fixes the draw.",
        "seed": SEED,
        "population": "no MB release group and no Discogs release",
        "population_size": len(ids),
        "graph_size": len(store.mbids),
        "artifact_sha256": digest,
        "sample": rows,
    }, indent=1), encoding="utf-8")

    lines = [
        "# The no-release tail: 20 artists for manual review",
        "",
        f"Population: **{len(ids):,}** of {len(store.mbids):,} graph artists have no "
        "MusicBrainz release group and no Discogs release. Four artists drawn from each "
        f"popularity quintile of that population, seed `{SEED}` — obscurest band first.",
        "",
        "**The question, and only you can answer it:** would this artist belong in the "
        "middle of a listening journey? The clip column is mechanical — the app's own "
        "Deezer→iTunes resolution with its own name rule — everything else is your "
        "research. YouTube/Spotify links are prefab searches, not claims they exist "
        "there.",
        "",
        "| # | Artist | Disambiguation | Pop pctl | Degree | Clip | Top neighbours | Links |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for k, r in enumerate(rows, 1):
        clip = (f"✅ {r['clip']['source']}" if r["clip"]["resolves"] else "❌ none")
        nb = ", ".join(n["name"] for n in r["top_neighbours"]) or "—"
        lines.append(
            f"| {k} | **{r['name']}** | {r['disambiguation'] or '—'} "
            f"| {r['pop_pctl_in_graph']:.0%} | {r['degree']} | {clip} | {nb} "
            f"| [MB]({r['musicbrainz']}) · [YT]({r['youtube_search']}) · "
            f"[Sp]({r['spotify_search']}) |")
    lines += [
        "",
        "Notes worth capturing per artist: real act vs data ghost; active vs defunct; "
        "would *you* want to land on them mid-journey; does anything play anywhere.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    resolved = sum(1 for r in rows if r["clip"]["resolves"])
    print(f"\nwrote {OUT_MD.name} and {OUT_JSON.name}; "
          f"{resolved}/{len(rows)} clips resolve", flush=True)


if __name__ == "__main__":
    main()
