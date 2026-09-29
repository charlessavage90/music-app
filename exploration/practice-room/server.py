"""Practice room: type a pair, press Dig deeper side by side on today's app and the finalists.

EXPLORATORY. Local only. Loads the served map once, imports each variant file (the same
`journey(ctx, s, t, pressed, prev)` interface as the quick-look kit), and reuses the API's own
search and clip resolver by import (nothing in api/ is modified).

    cd api && PYTHONIOENCODING=utf-8 uv run python -u ../exploration/practice-room/server.py
    then open http://127.0.0.1:8765
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(EXP / "kit"))

import httpx  # noqa: E402
import uvicorn  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse, Response  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from qlook import Ctx  # noqa: E402
from artistpath_api.clips import CatalogueUnavailable, ClipResolver, InMemoryClipCache  # noqa: E402
from artistpath_api.search import ArtistSearch  # noqa: E402

# (id, label shown on the column, variant file relative to exploration/, one-line description)
VARIANTS = [
    ("today", "Today's app", "baseline/today.py", "The shipped router, each press a 'known' exclusion."),
]


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem + "_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return mod


ctx = Ctx()
search = ArtistSearch(ctx.store, ctx.cfg)
mods = {}
for vid, _label, rel, _desc in VARIANTS:
    m = load(EXP / rel)
    if hasattr(m, "setup"):
        m.setup(ctx)
    mods[vid] = m
memo: dict = {}

client = httpx.AsyncClient(timeout=ctx.cfg.clip_http_timeout)


async def fetch_json(url: str, params: dict) -> dict:
    r = await client.get(url, params=params)
    if r.status_code == 429 or r.status_code >= 500:
        raise CatalogueUnavailable(f"{r.status_code} from {url}")
    r.raise_for_status()
    return r.json()


resolver = ClipResolver(ctx.cfg, InMemoryClipCache(), fetch_json)
app = FastAPI()


def node_of(mbid: str) -> int:
    n = ctx.store.id_by_mbid.get(mbid)
    if n is None:
        raise HTTPException(404, f"unknown artist {mbid}")
    return n


def artist(n: int) -> dict:
    return {"mbid": ctx.store.mbids[n], "name": ctx.names[n],
            "fame": round(ctx.pl[n] * 100, 1), "measured": bool(ctx.measured[n])}


def journey(vid: str, s: int, t: int, pressed: tuple):
    key = (vid, s, t, pressed)
    if key not in memo:
        prev = journey(vid, s, t, pressed[:-1]) if pressed else None
        memo[key] = mods[vid].journey(ctx, s, t, list(pressed), prev)
    return memo[key]


class JourneyReq(BaseModel):
    variant: str
    source: str
    target: str
    pressed: list[str] = []


@app.get("/")
def index():
    return FileResponse(HERE / "index.html")


@app.get("/api/variants")
def variants():
    return [{"id": v, "label": lab, "desc": d} for v, lab, _r, d in VARIANTS]


@app.get("/api/search")
def do_search(q: str):
    return [artist(n) for n in search.search(q)[:10]]


@app.post("/api/journey")
def do_journey(req: JourneyReq):
    if req.variant not in mods:
        raise HTTPException(404, "unknown variant")
    s, t = node_of(req.source), node_of(req.target)
    pressed = tuple(node_of(m) for m in req.pressed)
    path = journey(req.variant, s, t, pressed)
    if not path:
        return {"artists": [], "note": "no journey"}
    mids = [ctx.pl[v] for v in path[1:-1] if ctx.measured[v]]
    mids.sort()
    med = mids[len(mids) // 2] if mids else None
    return {"artists": [artist(v) for v in path],
            "median_mid_fame": round(med * 100, 1) if med is not None else None}


@app.get("/api/track/{mbid}")
async def track(mbid: str, index: int = 0):
    n = node_of(mbid)
    res = await resolver.resolve(mbid, ctx.names[n], ctx.store.deezer_id_of(n), index)
    if res.clip is None:
        return Response(status_code=204)
    return {"preview_url": res.clip.preview_url, "title": res.clip.title,
            "cover_url": res.clip.cover_url, "count": res.count}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
