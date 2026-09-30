"""Resolve up to three preview clips per presented artist — one source per ARTIST, whichever side it
is on (`DRP-AM7-6`). Adapted by copy from `LAL-`'s `lal_clips.py`.

Output goes to the sealed dir as a runtime file: preview URLs are signed and live about fifteen
minutes, so this is re-run just before serving and after every break, followed by a server restart
(clips are embedded at server start).

Also writes, sealed, **per row the count of artists with no clip that appear on only one side**
(`DRP-AM7-5`; `LAL-` results §4 item 2, #137). The count names no side, but it is sealed anyway and
read only by the write-up session. The runner sees only the L/R silent-slot totals below.

    cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \\
      ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_clips.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dsl_common import CLIPS_PER_ARTIST, ROOT, TOKENS, in_dir, sealed_path  # noqa: E402

_api = str(ROOT / "api" / "src")
if _api not in sys.path:
    sys.path.insert(0, _api)
from artistpath_api.clips import ClipResolver, InMemoryClipCache  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402

CONCURRENCY = 2
DELAY_S = 0.15


def _urllib_fetch(url: str, params: dict) -> dict:
    if not url.startswith("https://"):
        raise ValueError("clip catalogue URLs are https only")
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}" if q else url, headers={"User-Agent": "artistpath-dsl/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 — https enforced above
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


async def default_fetch(url: str, params: dict) -> dict:
    return await asyncio.to_thread(_urllib_fetch, url, params)


async def resolve_artist(resolver, mbid: str, name: str, deezer_id: str, limit: int) -> list[dict]:
    """Up to `limit` distinct clips, in the resolver's own order. A failure is an empty list, which
    the page shows as "no clip found" on the card (`DRP-AM7-4`)."""
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
    """Card slots with no clip, per page side (L/R, never roles) — the runner's 'conspicuously
    emptier' check."""
    counts = {tok: 0 for tok in TOKENS}
    for pair in page["pairs"]:
        for row in pair["rows"]:
            for tok in TOKENS:
                counts[tok] += sum(1 for a in row[tok]["artists"] if not clips.get(a["mbid"]))
    return counts


def single_side_clipless(page: dict, clips: dict) -> dict[str, dict[str, int]]:
    """#137: per row, artists with no clip that appear on only ONE side of that row."""
    out: dict[str, dict[str, int]] = {}
    for pair in page["pairs"]:
        for row in pair["rows"]:
            sides = {tok: {a["mbid"] for a in row[tok]["artists"]} for tok in TOKENS}
            only = sides["L"] ^ sides["R"]
            out.setdefault(pair["key"], {})[str(row["depth"])] = sum(1 for mb in only if not clips.get(mb))
    return out


def main() -> int:
    sealed = json.loads(sealed_path("dsl_sealed.json").read_text("utf-8"))
    page = json.loads(in_dir("dsl_page_data.json").read_text("utf-8"))
    names = {a["mbid"]: a["name"] for p in page["pairs"] for r in p["rows"] for t in TOKENS for a in r[t]["artists"]}
    artists = [(m, names[m], sealed["clip_source"].get(m, "")) for m in sorted(names)]
    out = asyncio.run(resolve_all(artists))
    sealed_path("dsl_clips.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    sealed_path("dsl_clip_tells.json").write_text(json.dumps(
        {"what": "DRP-AM7-5 / #137: per row, clipless artists on only one side. Sealed; decides nothing.",
         "single_side_clipless": single_side_clipless(page, out)}, indent=2), encoding="utf-8")
    silent = silent_slots_by_side(page, out)
    print(f"resolved {sum(1 for v in out.values() if v)}/{len(out)} artists, {sum(len(v) for v in out.values())} "
          f"tracks; silent card slots L {silent['L']}, R {silent['R']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
