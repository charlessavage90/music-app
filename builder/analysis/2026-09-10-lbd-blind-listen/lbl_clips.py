"""Resolve up to three preview clips per presented artist — one source for BOTH sides.

Output goes to the sealed dir as a runtime file: preview URLs are signed and live about fifteen
minutes (`GBL-` run log §3), so this is re-run just before serving and after every break, followed
by a server restart (clips are embedded at server start).

Non-differential by construction (`LBD-AM5-5`): each artist resolves through the app's own
`ClipResolver.resolve(mbid, name, deezer_artist_id, index)` with the NAME and the recorded DEEZER ID
taken from the SERVED map by MBID, whichever side the artist appears on. `GBL-` forced name search
because its two artifacts disagreed on ids; here one source serves both sides, so the app's
identity-first path is used and the wrong-artist class (`BYP-13`) shrinks for both at once. The
extra tracks are the app's own "try another track" (`index`), answering `CAU-` §2.3.

    cd <worktree>/builder && UV_LINK_MODE=copy uv run python -u \\
      analysis/2026-09-10-lbd-blind-listen/lbl_clips.py --listen 1
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import urllib.parse
import urllib.request

from lbl_common import CLIPS_PER_ARTIST, LISTENS, MAPS_PIN, SERVED, TOKENS, in_dir, load_map, sealed_path, use_api_src

use_api_src()
from artistpath_api.clips import ClipResolver, InMemoryClipCache  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402

CONCURRENCY = 2
DELAY_S = 0.15


def _urllib_fetch(url: str, params: dict) -> dict:
    if not url.startswith("https://"):
        raise ValueError("clip catalogue URLs are https only")
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}" if q else url, headers={"User-Agent": "artistpath-lbl/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 — https enforced above
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


async def default_fetch(url: str, params: dict) -> dict:
    return await asyncio.to_thread(_urllib_fetch, url, params)


async def resolve_artist(resolver, mbid: str, name: str, deezer_id: str, limit: int) -> list[dict]:
    """Up to `limit` distinct clips, in the resolver's own order. A failure is a silent card."""
    clips: list[dict] = []
    try:
        first = await resolver.resolve(mbid, name, deezer_artist_id=deezer_id, index=0)
        indices = range(min(first.count, limit))
        results = [first] + [await resolver.resolve(mbid, name, deezer_artist_id=deezer_id, index=i)
                             for i in indices if i > 0]
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
    """Card slots with no clip, per page side — the runner's 'conspicuously emptier' check. Sides
    are L/R, never maps, so this carries no arm identity."""
    counts = {tok: 0 for tok in TOKENS}
    for pair in page["pairs"]:
        for row in pair["rows"]:
            for tok in TOKENS:
                counts[tok] += sum(1 for a in row[tok]["artists"] if not clips.get(a["mbid"]))
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", type=int, required=True, choices=LISTENS)
    args = ap.parse_args(argv)
    pins = json.loads(MAPS_PIN.read_text(encoding="utf-8"))[f"listen{args.listen}"]
    store = load_map(SERVED, pins["served_sha256"])["store"]
    page = json.loads(in_dir(f"lbl_listen{args.listen}_page_data.json").read_text("utf-8"))
    mbids = sorted({a["mbid"] for p in page["pairs"] for r in p["rows"] for t in TOKENS for a in r[t]["artists"]})
    artists = [(m, store.names[store.id_by_mbid[m]], store.deezer_id_of(store.id_by_mbid[m])) for m in mbids]
    out = asyncio.run(resolve_all(artists))
    sealed_path(f"lbl_listen{args.listen}_clips.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    hits = sum(1 for v in out.values() if v)
    tracks = sum(len(v) for v in out.values())
    silent = silent_slots_by_side(page, out)
    print(f"resolved {hits}/{len(out)} artists, {tracks} tracks; silent card slots L {silent['L']}, R {silent['R']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
