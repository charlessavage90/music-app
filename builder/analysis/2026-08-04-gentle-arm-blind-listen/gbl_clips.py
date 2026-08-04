"""Resolve one preview clip per presented artist, name-based for BOTH arms.

Output goes to the sealed dir as a runtime file: preview URLs are signed and
expire, so this is re-run on listen day, minutes before serving.

Non-differential by construction: every artist resolves via
`resolve(mbid, name, deezer_artist_id="")` -- the name-based path -- for both
arms, so clip quality cannot become an arm tell. V0's artifact predates
`deezer_ids` anyway; forcing "" makes the arms symmetric regardless of what
B-S1 carries. `BYP-13` (a clip by a different artist of the same name) is live
and shared; the page tells the owner to ignore clip failures unless they differ
by side (spec §4).
"""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.parse
import urllib.request

from gbl_common import ROOT, in_dir, sealed_path

sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.clips import ClipResolver, InMemoryClipCache  # noqa: E402
from artistpath_api.config import ApiConfig                        # noqa: E402

CONCURRENCY = 2
DELAY_S = 0.15   # politeness; ~500 artists in 2-3 minutes


def _urllib_fetch(url: str, params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}" if q else url,
                                 headers={"User-Agent": "artistpath-gbl/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


async def default_fetch(url: str, params: dict) -> dict:
    return await asyncio.to_thread(_urllib_fetch, url, params)


async def resolve_all(artists: list[tuple[str, str]], fetch_json=default_fetch) -> dict:
    resolver = ClipResolver(cfg=ApiConfig(), cache=InMemoryClipCache(),
                            fetch_json=fetch_json)
    sem = asyncio.Semaphore(CONCURRENCY)
    out: dict[str, dict | None] = {}

    async def one(mbid: str, name: str) -> None:
        async with sem:
            try:
                clip = await resolver.resolve(mbid, name, deezer_artist_id="")
            except Exception:
                clip = None   # a clip is decorative; a miss is a silent card
            out[mbid] = (None if clip is None else
                         {"preview_url": clip.preview_url, "title": clip.title,
                          "cover_url": clip.cover_url})
            await asyncio.sleep(DELAY_S)

    await asyncio.gather(*(one(m, n) for m, n in artists))
    return out


def main() -> int:
    page = json.loads(in_dir("gbl_page_data.json").read_text("utf-8"))
    seen: dict[str, str] = {}
    for pair in page["pairs"]:
        for row in pair["rows"]:
            for side in ("L", "R"):
                for a in row[side]["artists"]:
                    seen[a["mbid"]] = a["name"]
    out = asyncio.run(resolve_all(sorted(seen.items())))
    sealed_path("gbl_clips.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    hits = sum(1 for v in out.values() if v)
    print(f"resolved {hits}/{len(out)} artists", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
