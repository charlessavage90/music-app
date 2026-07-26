"""Choose which names to poll for real fame, and the sample that validates the choice.

Polling all 12,041 names with the canonical A11/A15 resolver is ~120,000 API
requests. `Wikipedia:Database_download` asks for "at least a second delay between
requests" and "one or two simultaneous HTTP connections", which makes that a
day-and-a-half run; going faster was measured to degrade into repeated hard
failures that the canonical resolver converts into *fame-floor scores* (see
`transport.py`). So the set is screened first.

**The screen (the owner's, 2026-07-26).** In-graph popularity is a poor guide to
household fame *at the top* (Phase 1 log §2.11 — a lo-fi producer and a Beatle
score alike) but a usable one *at the bottom*. Sort by it, poll the top few
hundred, and the rest cannot contain a household name.

**Why it is sound here specifically**, and this is the part that does the work:
popularity is score-weighted in-degree accumulated at `pipeline.py:206-216`,
*before* `mutual_knn_cap` (227), `symmetrise` (230) and `largest_component` (231) —
so it is summed over the **full uncapped neighbour lists**. The reciprocity rule
destroys a stranded artist's degree and leaves its popularity untouched. Degree and
popularity are not just different currencies (§2.6); they are read at different
stages of the build, and the screen rides on the stage the defect does not reach.
Validated in `verify_screen.py`: all five `MKS-2` artists present in this set rank
in the **top 11 of 6,396**, against a cut at 400.

**Two roles, and the second is not optional.**

  - `screen` — the top `--cut` by popularity in each set. The deliverable's ranked
    lists are drawn from here.
  - `control` — a seeded random sample from *below* the cut. This exists because
    `verify_screen.py`'s ground truth is mildly circular: `MKS-2` found those six
    artists by noticing recognisable names among low-degree ones, which already
    correlates with being well-connected pre-cap. The control tests the screen
    against cases nothing selected for fame. If a control artist comes back more
    famous than the screened set's weakest, the screen leaked and the cut must
    move — and that is a result the report must state either way.

The known failure direction, stated before the run: an artist famous in a
population the snowball crawl under-covers has few in-graph neighbours pointing at
it, so it sits low on popularity while being a household name. This is the same
blind-spot direction A11 already accepts for Wikipedia-absence, so the two
instruments do not cross-check each other. The control sample is the only thing
here that can catch it.

Run from `api/` (needs no network):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-26-low-degree-census/select_poll_set.py
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 20260726  # fixed so the control sample is reproducible and cannot be reshuffled


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cut", type=int, default=400,
                    help="how many top-popularity nodes to poll per degree set")
    ap.add_argument("--control", type=int, default=200,
                    help="random nodes from BELOW the cut, per degree set")
    args = ap.parse_args()

    doc = json.loads((HERE / "low_degree.json").read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    out: dict[str, list] = {"screen": [], "control": []}
    summary = []

    for key in ("degree_1", "degree_2"):
        rows = [r for r in doc[key] if (r["name"] or "").strip()]
        # Ties on lowest mbid, matching the builder's own determinism convention
        # (spec §9) so the cut is reproducible rather than dict-order dependent.
        order = sorted(rows, key=lambda r: (-r["pop_raw"], r["mbid"]))
        screen = order[:args.cut]
        below = order[args.cut:]
        control = rng.sample(below, min(args.control, len(below)))

        for r in screen:
            out["screen"].append({**r, "role": "screen", "set": key})
        for r in control:
            out["control"].append({**r, "role": "control", "set": key})
        summary.append((key, len(rows), len(screen), len(below), len(control),
                        screen[-1]["pop_raw"] if screen else 0.0))

    names = sorted({r["name"] for r in out["screen"] + out["control"]})
    dest = HERE / "poll_set.json"
    dest.write_text(json.dumps({
        "artifact_sha256": doc["artifact_sha256"],
        "cut": args.cut, "control_per_set": args.control, "seed": SEED,
        "screen": out["screen"], "control": out["control"],
        "distinct_names": names,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"{'set':<10} {'named':>7} {'screen':>7} {'below':>7} {'control':>8} "
          f"{'cut pop_raw':>12}")
    for key, tot, ns, nb, nc, cutpop in summary:
        print(f"{key:<10} {tot:>7,} {ns:>7} {nb:>7,} {nc:>8} {cutpop:>12.6f}")
    print(f"\n{len(names):,} distinct name(s) to poll "
          f"({len(out['screen'])} screen + {len(out['control'])} control)")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
