"""FPC-2's own weakest link, tested rather than merely named.

WHAT FPC-2 RESTS ON, AND WHY THAT IS THIN
  fp_floor_reach measured floor reach over Track 2's arms on Track 2's pair
  set -- pre-registered for a different question and skewed toward famous
  endpoints. Its conclusion ("a refinement, not a defect") could therefore be
  an artifact of never asking the router to go anywhere obscure. I named that
  as the weakest link; this probe attacks it.

WHY TRACK 3's DATA IS THE RIGHT ATTACK, AND A HARDER ONE
  Two independent reasons, and the second is what makes this decisive:

  1. Its pair set is genuinely more obscure at one end (famous -> mid, e.g.
     "The Mills Brothers -> Tracey Chattaway"), so routed interiors sit lower
     by construction.
  2. It carries a LIMIT arm, which is the w -> infinity min-sum-percentile
     path (its own note). That is the MOST OBSCURE ROUTE THE GRAPH ADMITS
     between those endpoints -- not a tuned candidate but the ceiling. If the
     fame ruler can still see the interiors of the limit route, it can see
     anything a router could ever deliver on this graph.

READ, FIXED BEFORE EXECUTION
  - If the LIMIT arm's floor share is >= 25% of distinct interiors at any
    depth, FPC-2's verdict is CONDITIONAL on production's current pricing:
    the instrument goes blind exactly where a successful obscurity push would
    take the router, and FPC-3's latent-blindness reading is strengthened from
    an inference about the population to a measured property of the reachable
    route.
  - If the LIMIT arm stays under 10% at every depth, FPC-2 is ROBUST: even the
    most obscure route this graph admits stays inside the ruler's range, and
    the fame instrument is adequate for path-level criteria on THIS artifact.
    I will say so plainly, and it weakens the case for changing currency.
  - Between 10% and 25%: weakened, not refuted, and reported as such.

  Note what this cannot do either way: it is bounded by the ARTIFACT. A graph
  rebuilt to carry famous->obscure edges (the DD-F1 remedy) would move the
  reachable route, and no measurement on this artifact can anticipate that.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_floor_reach_t3.py
"""

from __future__ import annotations

import hashlib
import json
import statistics

from artistpath_builder.artifact import deserialise

from fp_common import ADOPTED, ADOPTED_SHA, HERE, band_of, fame_frame

TRACK3 = HERE.parent / "2026-07-28-track3-depth-descent"
OUT = HERE / "fp_floor_reach_t3.json"


def main() -> None:
    wikidata = json.loads((HERE / "fp_wikidata.json").read_text(encoding="utf-8"))
    lb = json.loads((HERE / "fp_listenbrainz.json").read_text(encoding="utf-8"))
    paths = json.loads((TRACK3 / "gap_paths.json").read_text(encoding="utf-8"))
    if paths["artifact_sha256"] != ADOPTED_SHA:
        raise SystemExit("Track 3 paths were routed on a different artifact")

    payload = ADOPTED.read_bytes()
    if hashlib.sha256(payload).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    mbids = list(deserialise(payload).mbids)
    frame = fame_frame()

    def floored(mbid: str) -> bool:
        rec = wikidata.get(mbid)
        return not (rec and rec.get("enwiki"))

    out: dict[str, dict] = {}
    for arm, by_pair in paths["paths"].items():
        for depth in paths["snapshots"]:
            interiors: list[str] = []
            for _pair, by_depth in by_pair.items():
                walk = by_depth.get(str(depth))
                if walk:
                    interiors.extend(mbids[i] for i in walk[1:-1])
            if not interiors:
                continue
            distinct = sorted(set(interiors))
            pctls = [frame[m] for m in distinct]
            out[f"{arm}@d{depth}"] = {
                "arm": arm,
                "depth": depth,
                "distinct_interiors": len(distinct),
                "interior_slots": len(interiors),
                "floor_share_distinct": round(
                    sum(1 for m in distinct if floored(m)) / len(distinct), 4),
                "floor_share_slots": round(
                    sum(1 for m in interiors if floored(m)) / len(interiors), 4),
                "lb_covered_distinct": round(
                    sum(1 for m in distinct if lb.get(m)) / len(distinct), 4),
                # Median interior percentile says how obscure the route
                # actually got -- without it a low floor share is unreadable,
                # because it cannot be told from "never went anywhere".
                "median_interior_pctl": round(statistics.median(pctls), 4),
                "median_interior_band": band_of(statistics.median(pctls)),
            }

    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")

    print("FPC-2 weakest-link test -- Track 3 pairs, including the LIMIT "
          "(most-obscure-admissible) arm")
    print(f"{'cell':>12} {'distinct':>9} {'no EN art':>10} {'of slots':>9} "
          f"{'LB':>7} {'median interior':>16}")
    for key, row in out.items():
        print(f"{key:>12} {row['distinct_interiors']:>9} "
              f"{row['floor_share_distinct']:>9.1%} {row['floor_share_slots']:>9.1%} "
              f"{row['lb_covered_distinct']:>6.1%} "
              f"{row['median_interior_pctl']:>8.4f} ({row['median_interior_band']})")

    limit = [r for k, r in out.items() if r["arm"] == "LIMIT"]
    if limit:
        worst = max(r["floor_share_distinct"] for r in limit)
        verdict = ("CONDITIONAL -- blind where a successful push would go"
                   if worst >= 0.25 else
                   "ROBUST -- even the most obscure admissible route stays in range"
                   if worst < 0.10 else "WEAKENED, not refuted")
        print(f"\nLIMIT arm worst floor share = {worst:.1%}  ->  {verdict}")
    print(f"\n-> {OUT.name}")


if __name__ == "__main__":
    main()
