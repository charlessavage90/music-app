"""How good are the MusicBrainz -> Deezer artist links, really?

The id path removes name matching, but it substitutes a new dependency:
MusicBrainz's link accuracy. Radiohead's recorded link points at a Deezer page
named "Radiohead" with 473 fans and 0 albums -- a duplicate, not the real one.

Two outcomes matter and they are not the same:
  DEAD  the linked page has no top track -> resolver falls back to name search,
        which is exactly today's behaviour. Fails safe.
  LIVE  the linked page returns a track -> that is what the card plays. Better
        than name search IF the page is the real artist, worse if it is a thin
        duplicate of one.

`nb_fan` separates them in practice: the real artist's page carries orders of
magnitude more followers than a duplicate.

Sampled over artists the app ACTUALLY DELIVERS, not the population.
"""
from __future__ import annotations

import json
import random
import sys
import time
import urllib.request

from pathlib import Path

ROOT = Path("C:/dev/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-30-coherence-tag-probe"))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_journey  # noqa: E402
from ct_common import ADOPTED  # noqa: E402

BUILT = ROOT / "builder/scratch/graph-deezerid-verify.bin"
PAIRS = ROOT / "builder/analysis/2026-07-30-tag-discrimination/tas_pairs.json"
SAMPLE = 60
PAUSE = 1.2


def get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "artistpath-verify"})
    return json.loads(urllib.request.urlopen(req, timeout=20).read())


def main() -> None:
    routing = GraphStore.load(ADOPTED)
    built = GraphStore.load(BUILT)
    cfg = ApiConfig()
    pairs = json.loads(PAIRS.read_text(encoding="utf-8"))["pairs"]

    delivered: list[int] = []
    for a, b, _cls in pairs:
        si, ti = routing.id_by_mbid.get(a), routing.id_by_mbid.get(b)
        if si is None or ti is None:
            continue
        res = find_journey(routing, si, ti, [], cfg)
        if res is None:
            continue
        delivered.extend(res[0][1:-1])

    # Map to the built artifact, which is where the ids live.
    with_id = []
    for node in dict.fromkeys(delivered):
        mbid = routing.mbids[node]
        n2 = built.id_by_mbid.get(mbid)
        if n2 is not None and built.deezer_id_of(n2):
            with_id.append((mbid, routing.names[node], built.deezer_id_of(n2)))

    random.seed(20260802)
    sample = random.sample(with_id, min(SAMPLE, len(with_id)))
    print(f"delivered interiors with an id: {len(with_id)}; sampling {len(sample)}",
          flush=True)

    dead = live = errors = 0
    thin: list[tuple] = []
    for mbid, name, aid in sample:
        try:
            top = get(f"https://api.deezer.com/artist/{aid}/top?limit=1")
            has_track = bool((top.get("data") or [{}])[0].get("preview")) \
                if top.get("data") else False
            info = get(f"https://api.deezer.com/artist/{aid}")
            fans = info.get("nb_fan", 0)
            same_name = (info.get("name") or "").strip().lower() == name.strip().lower()
            if has_track:
                live += 1
                if fans < 1000:
                    thin.append((name, aid, fans, info.get("name")))
            else:
                dead += 1
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"  error {name}: {type(e).__name__}", flush=True)
        time.sleep(PAUSE)

    n = live + dead
    print(f"\nchecked {n} (+{errors} errors)")
    print(f"  LIVE  (id serves a track, replaces name search): {live}  ({live/n*100:.0f}%)")
    print(f"  DEAD  (no track, falls back to name search):     {dead}  ({dead/n*100:.0f}%)")
    print(f"\n  of the LIVE ones, thin pages (<1000 fans): {len(thin)}")
    for name, aid, fans, dname in thin[:10]:
        print(f"    {name!r} -> id {aid} name={dname!r} fans={fans}")


if __name__ == "__main__":
    main()
