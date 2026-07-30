"""COH-6, POST-HOC AND LABELLED AS SUCH: coverage under the widest vocabulary.

OWNER-REQUESTED after the gate fired (2026-07-30): recompute coverage using
ALL tags, not only the genre-whitelisted subset the frozen instrument
definition used. This is a descriptive addendum:

  - It CANNOT un-fire the gate. The gate was committed on the genre union
    and killed at 35.3% vs 50%; this read exists to inform whether a future
    TAGS-vocabulary instrument would be worth its own probe -- which would
    need its own committed gate, designed cold.
  - No predictions are claimed. The per-band tag columns were already
    printed by ct_mb_sample and ct_lb_metadata before this file was written,
    so there is nothing left to pre-commit ("committed before looking" is
    not available, and pretending otherwise would be worse than saying so).

WHAT IT COMPUTES, all from data already on disk plus one small LB fetch:
  Per band, over the same seeded sample: coverage under the widest union
  (any MB tag | any LB tag | any MB genre | any P136 statement), beside the
  gate's genre union for contrast. Then the same two numbers for the 62
  LIMIT-arm interiors (LB tags fetched here; seconds).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-coherence-tag-probe/ct_alltags_read.py
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse

from artistpath_builder.artifact import deserialise

from ct_common import (
    ADOPTED,
    ADOPTED_SHA,
    BAND_ORDER,
    HERE,
    fame_frame,
    get_json,
    load_partial,
    mb_genre_set,
    mb_tag_set,
    norm_genre,
    save_partial,
)
from ct_mb_sample import sample_mbids

P136_RAW = HERE / "ct_wikidata_genres.json"
MB_RAW = HERE / "ct_mb_sample_raw.json"
LB_RAW = HERE / "ct_lb_metadata_raw.json"
LIMIT_MB_RAW = HERE / "ct_limit_tags_raw.json"
LIMIT_LB_RAW = HERE / "ct_limit_lb_raw.json"
OUT = HERE / "ct_alltags_read.json"
TRACK3 = HERE.parent / "2026-07-28-track3-depth-descent"


def lb_tags(rec) -> set[str]:
    if not rec:
        return set()
    return {norm_genre(t) for t in rec.get("tags", [])}


def fetch_lb(mbids: list[str], out_path) -> dict:
    done = load_partial(out_path)
    pending = [m for m in mbids if m not in done]
    for start in range(0, len(pending), 50):
        chunk = pending[start : start + 50]
        qs = urllib.parse.urlencode({"artist_mbids": ",".join(chunk), "inc": "tag"})
        status, payload = get_json(
            "https://api.listenbrainz.org/1/metadata/artist/?" + qs, timeout=120
        )
        if status != 200:
            raise RuntimeError(f"LB returned {status}")
        items = payload if isinstance(payload, list) else [
            {"artist_mbid": k, **v} for k, v in payload.items() if isinstance(v, dict)
        ]
        got = {}
        for item in items:
            tags = item.get("tag", {}).get("artist", [])
            got[item.get("artist_mbid") or item.get("mbid")] = {
                "tags": [t["tag"] for t in tags]
            }
        for m in chunk:
            done[m] = got.get(m)
        save_partial(out_path, done)
        time.sleep(0.3)
    return done


def main() -> None:
    frame = fame_frame()
    p136 = json.loads(P136_RAW.read_text(encoding="utf-8"))
    mb = load_partial(MB_RAW)
    lb = load_partial(LB_RAW)
    sampled = sample_mbids(frame)

    def widest(m: str, mb_store, lb_store) -> bool:
        return bool(
            mb_tag_set(mb_store.get(m))
            or mb_genre_set(mb_store.get(m))
            or lb_tags(lb_store.get(m))
            or p136.get(m)
        )

    def genre_union(m: str, mb_store) -> bool:
        return bool(mb_genre_set(mb_store.get(m)) or p136.get(m))

    bands: dict[str, dict] = {}
    print(f"{'band':>12} {'n':>5} {'genre union (gate)':>19} {'widest (any tag)':>17}")
    for b in BAND_ORDER:
        mbids = sampled[b]
        n = len(mbids)
        g = sum(1 for m in mbids if genre_union(m, mb))
        w = sum(1 for m in mbids if widest(m, mb, lb))
        bands[b] = {"n": n, "genre_union": g, "widest": w}
        print(f"{b:>12} {n:>5} {g / n:>18.1%} {w / n:>16.1%}")

    paths = json.loads((TRACK3 / "gap_paths.json").read_text(encoding="utf-8"))
    if paths["artifact_sha256"] != ADOPTED_SHA:
        raise SystemExit("Track 3 paths were routed on a different artifact")
    payload = ADOPTED.read_bytes()
    if hashlib.sha256(payload).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    mbid_list = list(deserialise(payload).mbids)
    interiors: set[str] = set()
    for by_depth in paths["paths"]["LIMIT"].values():
        for walk in by_depth.values():
            if walk:
                interiors.update(mbid_list[i] for i in walk[1:-1])
    distinct = sorted(interiors)

    limit_mb = load_partial(LIMIT_MB_RAW)
    limit_lb = fetch_lb(distinct, LIMIT_LB_RAW)
    lg = sum(1 for m in distinct if genre_union(m, limit_mb))
    lw = sum(1 for m in distinct if widest(m, limit_mb, limit_lb))
    print(f"\nLIMIT interiors (n={len(distinct)}): "
          f"genre union {lg / len(distinct):.1%} -> widest {lw / len(distinct):.1%}")

    OUT.write_text(
        json.dumps(
            {
                "note": "COH-6, post-hoc owner-requested read; cannot move the gate",
                "bands": bands,
                "limit_interiors": {
                    "n": len(distinct),
                    "genre_union": lg,
                    "widest": lw,
                },
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
