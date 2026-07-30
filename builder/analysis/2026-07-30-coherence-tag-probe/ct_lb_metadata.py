"""COH-5: is ListenBrainz's batched metadata endpoint a faithful fast transport
for MusicBrainz tag data?

WHY (owner's question, raised mid-run 2026-07-30)
  The MB web service's 1 req/s is what forced step 1 down to a 1,275-artist
  sample (full graph ~21 h). LB's `GET /1/metadata/artist/` serves
  MB-derived metadata BATCHED, so if it is faithful, a full-graph tag frame
  costs minutes-to-hours, not a day -- for this probe's successors and for
  any instrument a future pre-registration builds.

  FRAMING THAT MATTERS: LB here is a TRANSPORT for MusicBrainz's tag data,
  not an independent source. The standing hazard ("LB and English Wikipedia
  under-represent the same artists; their agreement is a shared blind spot")
  is about LB as a FAME source and does not transfer to this question. The
  question is fidelity to MB's own answers, measured artist by artist.

NOT PART OF THE KILL GATE
  The gate is already fixed in ct_mb_sample.py (MB direct + P136) and this
  probe cannot move it in either direction. Descriptive only.

WHAT IS COMPARED, ON THE SAME SEEDED SAMPLE
  For every artist the banded sample already fetched from MB directly:
  LB tags carrying a `genre_mbid` (the genre-whitelisted tags) against MB's
  `genres` list, both normalised by ct_common.norm_genre; all-tags likewise;
  plus coverage per band and wall-clock throughput.

PREDICTIONS, FIXED BEFORE THE RUN
  - Fidelity: >= 90% of artists resolved by both sources have IDENTICAL
    normalised genre sets (same data, sync lag only). Refuted below 90%,
    in which case MB direct stays the only reference and the 21 h / dump
    cost stands.
  - Coverage: LB's >= 1-genre-tag rate lands within 3 points of MB direct's
    genre rate in every band. Refuted if lower by more than 3 points
    anywhere (would mean LB filters or lags in the tail -- the exact place
    it would need to be trusted).
  - Speed: >= 10x MB direct's ~0.9 artists/s.

Run from `builder/` (after ct_mb_sample.py has completed):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-coherence-tag-probe/ct_lb_metadata.py
"""

from __future__ import annotations

import json
import time
import urllib.parse
from typing import Any

from ct_common import (
    BAND_ORDER,
    HERE,
    band_of,
    fame_frame,
    get_json,
    load_partial,
    mb_genre_set,
    mb_tag_set,
    norm_genre,
    save_partial,
)
from ct_mb_sample import sample_mbids

LB_URL = "https://api.listenbrainz.org/1/metadata/artist/?%s"
BATCH = 50
PAUSE = 0.3
MB_RAW = HERE / "ct_mb_sample_raw.json"
OUT_RAW = HERE / "ct_lb_metadata_raw.json"
OUT = HERE / "ct_lb_metadata.json"


def parse_artists(payload: Any) -> dict[str, dict]:
    """Lenient over the response envelope; strict about per-artist content.

    The docs do not pin the envelope (list vs mbid-keyed dict), so both are
    accepted. An unrecognised shape raises with a snippet -- that is a
    finding about the endpoint, not a condition to paper over.
    """
    if isinstance(payload, dict):
        items = []
        for k, v in payload.items():
            if isinstance(v, dict):
                v = {"artist_mbid": k, **v}
            items.append(v)
    elif isinstance(payload, list):
        items = payload
    else:
        raise RuntimeError(f"unrecognised envelope: {str(payload)[:300]}")
    out: dict[str, dict] = {}
    for item in items:
        mbid = item.get("artist_mbid") or item.get("mbid")
        if not mbid:
            raise RuntimeError(f"artist without mbid: {str(item)[:300]}")
        tags = item.get("tag", {}).get("artist", [])
        out[mbid] = {
            "genres": [t["tag"] for t in tags if t.get("genre_mbid")],
            "tags": [t["tag"] for t in tags],
        }
    return out


def main() -> None:
    frame = fame_frame()
    sampled = sample_mbids(frame)
    flat = [m for b in BAND_ORDER for m in sampled[b]]
    mb = load_partial(MB_RAW)
    if any(m not in mb for m in flat):
        raise SystemExit("ct_mb_sample_raw.json is incomplete; run ct_mb_sample.py first")

    done: dict[str, Any] = load_partial(OUT_RAW)
    pending = [m for m in flat if m not in done]
    began = time.time()
    for start in range(0, len(pending), BATCH):
        chunk = pending[start : start + BATCH]
        qs = urllib.parse.urlencode(
            {"artist_mbids": ",".join(chunk), "inc": "tag"}
        )
        status, payload = get_json(LB_URL % qs, timeout=120)
        if status != 200:
            raise RuntimeError(f"LB returned {status}")
        got = parse_artists(payload)
        for m in chunk:
            done[m] = got.get(m)  # absent = LB knows nothing for it
        save_partial(OUT_RAW, done)
        print(f"  lb {min(start + BATCH, len(pending))}/{len(pending)}", flush=True)
        time.sleep(PAUSE)
    elapsed = time.time() - began if pending else float("nan")

    def lb_sets(m: str) -> tuple[set[str], set[str]]:
        rec = done.get(m)
        if not rec:
            return set(), set()
        return (
            {norm_genre(g) for g in rec["genres"]},
            {norm_genre(t) for t in rec["tags"]},
        )

    per_band: dict[str, dict] = {}
    both = ident = 0
    print(f"\n{'band':>12} {'n':>5} {'MB genre':>9} {'LB genre':>9} {'LB tag':>8} {'identical':>10}")
    for b in BAND_ORDER:
        mbids = sampled[b]
        n = len(mbids)
        mb_g = sum(1 for m in mbids if mb_genre_set(mb.get(m)))
        lb_g = sum(1 for m in mbids if lb_sets(m)[0])
        lb_t = sum(1 for m in mbids if lb_sets(m)[1])
        band_both = [m for m in mbids if mb_genre_set(mb.get(m)) and done.get(m)]
        band_ident = sum(1 for m in band_both if mb_genre_set(mb.get(m)) == lb_sets(m)[0])
        both += len(band_both)
        ident += band_ident
        per_band[b] = {
            "n": n,
            "mb_genre": mb_g,
            "lb_genre": lb_g,
            "lb_tag": lb_t,
            "both_resolved": len(band_both),
            "identical_genre_sets": band_ident,
        }
        print(
            f"{b:>12} {n:>5} {mb_g / n:>8.1%} {lb_g / n:>8.1%} {lb_t / n:>7.1%} "
            f"{(band_ident / len(band_both)) if band_both else 0:>9.1%}"
        )

    rate = len(pending) / elapsed if pending else 0
    print(f"\nfidelity: {ident}/{both} identical genre sets "
          f"({ident / both:.1%})" if both else "\nfidelity: nothing comparable")
    if pending:
        print(f"throughput: {rate:.1f} artists/s (MB direct ~0.9/s)")

    OUT.write_text(
        json.dumps(
            {
                "identical_genre_sets": ident,
                "both_resolved": both,
                "artists_per_second": round(rate, 2),
                "bands": per_band,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
