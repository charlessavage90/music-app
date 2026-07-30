"""Step 1: how far does the Wikipedia fame FLOOR actually reach?

THE QUESTION THIS SETTLES, AND WHY IT COMES FIRST
  Under A11 an artist with no English Wikipedia article scores F = 0 -- the
  floor -- rather than being dropped. So the fame ruler has no resolution
  below the floor: it cannot separate an artist with 4,000 annual pageviews
  from one with none, nor either from a nameless node (A18).

  If the floor catches a small share of what the router actually delivers,
  this whole line of work is a refinement. If it catches a large share AT
  DEPTH, then every fame-currency criterion this project has run -- C1's
  depth gradient, C3's "progressively", REQ-13's "bypass must increase
  delivered novelty" -- has been reading a BINARY in the exact region it was
  built to measure. That is the number, and it decides how much the rest
  matters.

WRITTEN BEFORE THE RESULT WAS SEEN (the honest analogue of pre-registration
for a descriptive probe; commit timestamp is the evidence):
  Expectation -- the floor share among routed interiors RISES with bypass
  depth, because depth is what drives the router toward obscurity. Aggregate
  floor share across Track 2's whole scored population is already known to be
  14.3% (185 of 1,296 unmatched in its committed fame_cache.json), so a flat
  profile would sit near that. I expect d20 materially above d0.
  I will call >= 25% of interiors at the floor at any scored depth "the ruler
  is substantially blind there", and < 10% at every depth "a refinement, not
  a defect". Between those, weakened not refuted -- and I will say so rather
  than picking the side that suits.

  NOTE THE ASYMMETRY, stated in advance: a HIGH floor share is not by itself
  proof the instrument is wrong. Reaching artists nobody wrote an article
  about is partly what SUCCESS looks like for this product. What it proves is
  that the instrument cannot SEE that success, which is a different claim and
  the only one this probe supports.

SOURCE OF PATHS
  ../2026-07-24-track2-arm-scorer/paths.json, whose artifact_sha256 is the
  adopted artifact's, so its node indices resolve directly against it. Read
  only; nothing is re-routed and no arm is re-scored.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_floor_reach.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from artistpath_builder.artifact import deserialise

from fp_common import ADOPTED, ADOPTED_SHA, HERE, band_of, fame_frame

TRACK2 = HERE.parent / "2026-07-24-track2-arm-scorer"
OUT = HERE / "fp_floor_reach.json"


def adopted_index() -> list[str]:
    payload = ADOPTED.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != ADOPTED_SHA:
        raise SystemExit(f"adopted artifact mismatch: {actual}")
    return list(deserialise(payload).mbids)


def main() -> None:
    wikidata = json.loads((HERE / "fp_wikidata.json").read_text(encoding="utf-8"))
    lb = json.loads((HERE / "fp_listenbrainz.json").read_text(encoding="utf-8"))
    paths = json.loads((TRACK2 / "paths.json").read_text(encoding="utf-8"))
    if paths["artifact_sha256"] != ADOPTED_SHA:
        raise SystemExit("Track 2 paths were routed on a different artifact")

    mbids = adopted_index()
    frame = fame_frame()

    def has_article(mbid: str) -> bool:
        rec = wikidata.get(mbid)
        return bool(rec and rec.get("enwiki"))

    def has_lb(mbid: str) -> bool:
        return bool(lb.get(mbid))

    # Interiors only: endpoints are user-chosen anchors (REQ-3) and are not
    # what any discovery criterion reads.
    per_depth: dict[str, dict] = {}
    for depth in paths["snapshots"]:
        interiors: list[str] = []
        for arm, by_pair in paths["paths"].items():
            for _pair, by_depth in by_pair.items():
                walk = by_depth.get(str(depth))
                if not walk:
                    continue
                interiors.extend(mbids[i] for i in walk[1:-1])
        distinct = sorted(set(interiors))
        if not distinct:
            continue
        per_depth[str(depth)] = {
            "interior_slots": len(interiors),
            "distinct_interiors": len(distinct),
            # Both denominators, per the GRT-P4 lesson: a share over distinct
            # artists and a share over delivered slots answer different
            # questions, and quoting one alone has misled here before.
            "floor_share_distinct": round(
                sum(1 for m in distinct if not has_article(m)) / len(distinct), 4
            ),
            "floor_share_slots": round(
                sum(1 for m in interiors if not has_article(m)) / len(interiors), 4
            ),
            "lb_covered_distinct": round(
                sum(1 for m in distinct if has_lb(m)) / len(distinct), 4
            ),
            "median_band": sorted(
                (band_of(frame[m]) or "?") for m in distinct
            )[len(distinct) // 2],
        }

    summary = {
        "source": "../2026-07-24-track2-arm-scorer/paths.json",
        "artifact_sha256": ADOPTED_SHA,
        "arms_pooled": paths["arms"],
        "per_depth": per_depth,
    }
    OUT.write_text(json.dumps(summary, indent=1), encoding="utf-8")

    print("Floor reach among Track 2's ROUTED INTERIORS (all arms pooled)")
    print(f"{'depth':>6} {'distinct':>9} {'slots':>7} "
          f"{'no EN article':>14} {'of slots':>9} {'LB covered':>11}")
    for depth, row in per_depth.items():
        print(f"{depth:>6} {row['distinct_interiors']:>9} {row['interior_slots']:>7} "
              f"{row['floor_share_distinct']:>13.1%} {row['floor_share_slots']:>9.1%} "
              f"{row['lb_covered_distinct']:>11.1%}")
    print(f"\n-> {OUT.name}")


if __name__ == "__main__":
    main()
