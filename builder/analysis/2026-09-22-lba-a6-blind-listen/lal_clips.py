"""Resolve up to three preview clips per presented artist — one source per ARTIST, whichever side
it is on (`LBA-AM6-6`). Adapted by copy from listen 2's `lbl_clips.py`.

Output goes to the sealed dir as a runtime file: preview URLs are signed and live about fifteen
minutes, so this is re-run just before serving and after every break, followed by a server restart
(clips are embedded at server start).

Each artist resolves through the app's own `ClipResolver.resolve(mbid, name, deezer_artist_id,
index)` with name and Deezer id from `lal_generate.artist_source`: the candidate artifact where it
holds the artist and records an id, otherwise the served artifact, otherwise name search.

    cd <tree>/builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \\
      analysis/2026-09-22-lba-a6-blind-listen/lal_clips.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import CLIPS_PER_ARTIST, TOKENS, in_dir, load_pinned_maps, sealed_path, use_api_src  # noqa: E402

use_api_src()
from artistpath_api.clips import ClipResolver, InMemoryClipCache  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402

CONCURRENCY = 2
DELAY_S = 0.15


def _urllib_fetch(url: str, params: dict) -> dict:
    if not url.startswith("https://"):
        raise ValueError("clip catalogue URLs are https only")
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}" if q else url, headers={"User-Agent": "artistpath-lal/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 — https enforced above
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


async def default_fetch(url: str, params: dict) -> dict:
    return await asyncio.to_thread(_urllib_fetch, url, params)


async def resolve_artist(resolver, mbid: str, name: str, deezer_id: str, limit: int) -> list[dict]:
    """Up to `limit` distinct clips, in the resolver's own order. A failure is an empty list, which
    the page shows as "no clip found" on the card (`LBA-AM6-4`)."""
    clips: list[dict] = []
    try:
        first = await resolver.resolve(mbid, name, deezer_artist_id=deezer_id, index=0)
        results = [first] + [await resolver.resolve(mbid, name, deezer_artist_id=deezer_id, index=i)
                             for i in range(1, min(first.count, limit))]
    except Exception:
        return clips
    for r in results:
        if r.clip and r.clip.preview_url and r.clip.preview_url not in {c["preview_url"] for c in clips}:
            clips.append({"preview_url": r.clip.preview_url, "title": r.clip.title, "cover_url": r.clip.cover_url})
    return clips


async def resolve_all(artists: list[tuple[str, str, str]], fetch_json=default_fetch,
                      limit: int = CLIPS_PER_ARTIST) -> dict[str, list[dict]]:
    resolver = ClipResolver(cfg=ApiConfig(), cache=InMemoryClipCache(), fetch_json=fetch_json)
    sem = asyncio.Semaphore(CONCURRENCY)
    out: dict[str, list[dict]] = {}

    async def one(mbid: str, name: str, deezer_id: str) -> None:
        async with sem:
            out[mbid] = await resolve_artist(resolver, mbid, name, deezer_id, limit)
            await asyncio.sleep(DELAY_S)

    await asyncio.gather(*(one(*a) for a in artists))
    return out


def silent_slots_by_side(page: dict, clips: dict) -> dict[str, int]:
    """Card slots with no clip, per page side (L/R, never maps) — the runner's 'conspicuously
    emptier' check."""
    counts = {tok: 0 for tok in TOKENS}
    for pair in page["pairs"]:
        for row in pair["rows"]:
            for tok in TOKENS:
                counts[tok] += sum(1 for a in row[tok]["artists"] if not clips.get(a["mbid"]))
    return counts


def main() -> int:
    from lal_generate import artist_source

    maps = load_pinned_maps()
    info = artist_source(maps["incumbent"]["store"], maps["challenger"]["store"])
    page = json.loads(in_dir("lal_page_data.json").read_text("utf-8"))
    mbids = sorted({a["mbid"] for p in page["pairs"] for r in p["rows"] for t in TOKENS for a in r[t]["artists"]})
    artists = [(m, info(m)[0], info(m)[2]) for m in mbids]
    out = asyncio.run(resolve_all(artists))
    sealed_path("lal_clips.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    silent = silent_slots_by_side(page, out)
    print(f"resolved {sum(1 for v in out.values() if v)}/{len(out)} artists, {sum(len(v) for v in out.values())} "
          f"tracks; silent card slots L {silent['L']}, R {silent['R']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
