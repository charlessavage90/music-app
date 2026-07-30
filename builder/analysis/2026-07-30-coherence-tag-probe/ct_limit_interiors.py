"""COH-3: genre coverage exactly where a successful obscurity push would go.

WHY THIS SET
  FPC-9's result is the sharpest fact about the fame ruler: on the most
  obscure route this artifact admits (Track 3's LIMIT arm), 38.7% of
  delivered interiors are invisible to it. A coherence instrument that goes
  dark on that same set fails in the same place the fame proxy does -- so
  the banded sample (ct_mb_sample) is the gate, and THIS is the
  decision-relevant spot check: can the genre union see the artists the
  obscurity work would actually deliver?

  DESCRIPTIVE ONLY -- no gate, no threshold. It rides on whichever verdict
  the banded gate returns and is reported beside it either way (it is cheap:
  the LIMIT arm delivers ~62 distinct interiors).

PREDICTION, FIXED BEFORE THE RUN
  Union-genre coverage on the LIMIT interiors lands at or above the
  lower-half banded figure, because routed interiors need degree >= 2 and
  even the most obscure routable artists sit above the band's floor of
  never-routable ones. Refuted if materially below (> 6 points).

Run from `builder/` (after ct_wikidata_genres.py):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-coherence-tag-probe/ct_limit_interiors.py
"""

from __future__ import annotations

import hashlib
import json
import statistics

from artistpath_builder.artifact import deserialise

from ct_common import (
    ADOPTED,
    ADOPTED_SHA,
    HERE,
    fame_frame,
    fetch_mb_artists,
    load_partial,
    mb_genre_set,
)

TRACK3 = HERE.parent / "2026-07-28-track3-depth-descent"
P136_RAW = HERE / "ct_wikidata_genres.json"
OUT_RAW = HERE / "ct_limit_tags_raw.json"
OUT = HERE / "ct_limit_interiors.json"


def main() -> None:
    paths = json.loads((TRACK3 / "gap_paths.json").read_text(encoding="utf-8"))
    if paths["artifact_sha256"] != ADOPTED_SHA:
        raise SystemExit("Track 3 paths were routed on a different artifact")
    payload = ADOPTED.read_bytes()
    if hashlib.sha256(payload).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    mbids = list(deserialise(payload).mbids)

    interiors: set[str] = set()
    for _pair, by_depth in paths["paths"]["LIMIT"].items():
        for walk in by_depth.values():
            if walk:
                interiors.update(mbids[i] for i in walk[1:-1])
    distinct = sorted(interiors)

    p136 = json.loads(P136_RAW.read_text(encoding="utf-8"))
    done = load_partial(OUT_RAW)
    done = fetch_mb_artists(distinct, done, OUT_RAW, label="limit-interiors")

    frame = fame_frame()
    covered = [m for m in distinct if mb_genre_set(done.get(m)) or p136.get(m)]
    n = len(distinct)
    out = {
        "distinct_interiors": n,
        "union_genre_covered": len(covered),
        "union_genre_rate": round(len(covered) / n, 4),
        "mb_genre_rate": round(sum(1 for m in distinct if mb_genre_set(done.get(m))) / n, 4),
        "p136_rate": round(sum(1 for m in distinct if p136.get(m)) / n, 4),
        "median_interior_pctl": round(statistics.median(frame[m] for m in distinct), 4),
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nLIMIT-arm distinct interiors: {n}")
    print(f"  union genre covered: {out['union_genre_rate']:.1%} "
          f"(MB {out['mb_genre_rate']:.1%}, P136 {out['p136_rate']:.1%})")
    print(f"  median interior pctl: {out['median_interior_pctl']:.4f}")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
