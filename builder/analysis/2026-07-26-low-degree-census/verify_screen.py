"""Is in-graph popularity a safe screen for finding the famous end of this set?

The owner's methodology note: in-graph popularity is a poor guide to household fame
*at the top* (Phase 1 log §2.11), but a usable screen *at the bottom* — so sort the
degree<=2 set by it, poll only the top few hundred for real fame, and if none of
those are household names the rest are not either.

**Why the note is stronger than it claims, and this is the load-bearing fact.**
Popularity in this artifact is score-weighted in-degree accumulated at
`pipeline.py:206-216`, which runs **before** `mutual_knn_cap` (227), `symmetrise`
(230) and `largest_component` (231). So it is summed over the FULL UNCAPPED
neighbour lists. A famous artist stranded to one connection by the reciprocity rule
therefore keeps the in-degree of every artist that ever pointed at it: the stranding
destroys the artist's degree and leaves its popularity untouched. Within this
population popularity and degree are not merely different currencies (§2.6) — they
are measured at different stages of the build, and the screen rides on the one the
defect does not touch.

**Where the screen can still fail, stated before running it.** It requires
high-fame => high in-graph popularity. That breaks for an artist famous in a
population the crawl under-covers: the frontier is a snowball from one bootstrap,
so an act with few in-graph neighbours pointing at it can be a household name
outside the graph's genre coverage. Note this is the *same* blind-spot direction
A11 already accepts for Wikipedia-absence, so the two instruments do not
cross-check each other here.

So the screen is not asserted. Three checks:

  **S1 (ground truth).** `MKS-2` names six recognisable artists independently found
  stranded at one connection. If the screen is sound, all six land inside the
  proposed cut. A miss falsifies the screen directly, on cases nobody chose for it.

  **S2 (saturation).** `pop_raw` is log-scaled to 0-1 and the top of the artifact
  saturates. If the set's top few hundred are tied at one value, "top N" is decided
  by tie-break rather than by popularity, and N must grow or the cut must change.

  **S3 (non-artist entities).** The build drops MusicBrainz placeholders by matching
  'special purpose' in the disambiguation, and nothing else. So this reports what
  actually remains in the set that looks non-artist, rather than assuming the filter
  was sufficient.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-26-low-degree-census/verify_screen.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

# From MKS-2 — found by the stranding finding, not chosen by this screen.
MKS2_NAMES = ["Meat Loaf", "Elbow", "The Cult", "The Streets", "Nada Surf", "Pretenders"]

# Patterns that suggest a container/placeholder rather than an artist. Deliberately
# broader than the build's own 'special purpose' filter, because the point is to
# find what that filter let through.
SUSPECT = re.compile(
    r"^\s*(various|various artists|unknown|\[unknown\]|no artist|soundtrack|"
    r"traditional|anonymous|\[anonymous\]|untitled|n/?a|none|test)\s*$",
    re.IGNORECASE,
)
SUSPECT_DISAMBIG = re.compile(r"special purpose|placeholder|not an artist", re.IGNORECASE)

CUT = 400  # the proposed screen depth, per set


def main() -> None:
    doc = json.loads((HERE / "low_degree.json").read_text(encoding="utf-8"))
    d1, d2 = doc["degree_1"], doc["degree_2"]
    both = d1 + d2
    print(f"degree 1 = {len(d1):,}   degree 2 = {len(d2):,}   both = {len(both):,}")

    # ---- the LCC question, answered from the artifact itself -----------------
    print("\n=== counted after the largest-component prune? ===")
    print("The artifact is written from `pruned`, which is built from `keep = "
          "largest_component(...)` (pipeline.py:231-238), so every node read here is "
          "already post-prune. The observable consequence:")
    degs = np.array([r["degree"] for r in both])
    print(f"  minimum degree anywhere in these sets : {degs.min()}")
    print("  -> no degree-0 nodes exist, which is what a post-prune count must show; "
          "a pre-prune count would include isolated artists and disconnected islands.")
    # Every neighbour of a node in the set must itself be in the artifact.
    orphan = sum(1 for r in both for nb in r["neighbours"] if nb["degree"] < 1)
    print(f"  neighbours with degree < 1            : {orphan}  (must be 0)")

    # ---- S3: non-artist entities -------------------------------------------
    print("\n=== S3: non-artist entities remaining in the set ===")
    print("The build's only filter is `is_special_purpose`, a case-insensitive match on "
          "the literal 'special purpose' in the MusicBrainz disambiguation "
          "(pipeline.py:42-47). Nothing else is excluded by type.")
    by_name = [r for r in both if SUSPECT.match(r["name"] or "")]
    by_dis = [r for r in both if SUSPECT_DISAMBIG.search(r["disambiguation"] or "")]
    nameless = [r for r in both if not (r["name"] or "").strip()]
    print(f"  container-ish names (Various Artists, [unknown], ...) : {len(by_name)}")
    for r in by_name[:15]:
        print(f"      {r['name']!r}  deg {r['degree']}  dis={r['disambiguation']!r}")
    print(f"  disambiguation still flagging a placeholder           : {len(by_dis)}")
    for r in by_dis[:10]:
        print(f"      {r['name']!r}  dis={r['disambiguation']!r}")
    print(f"  nameless nodes (an artifact defect, not artists)      : {len(nameless)}")

    # ---- S2: saturation ----------------------------------------------------
    print("\n=== S2: is pop_raw saturated at the top of this set? ===")
    for label, rows in (("degree 1", d1), ("degree 2", d2)):
        pops = np.array([r["pop_raw"] for r in rows])
        order = np.sort(pops)[::-1]
        cut_val = order[min(CUT, len(order)) - 1]
        ties_at_max = int((pops == order[0]).sum())
        ties_at_cut = int((pops == cut_val).sum())
        print(f"  {label}: max {order[0]:.6f}  cut@{CUT} {cut_val:.6f}  "
              f"min {order[-1]:.6f}")
        print(f"      nodes tied at the max {ties_at_max}, tied at the cut value "
              f"{ties_at_cut}  -> {'TIE-DECIDED' if ties_at_cut > 5 else 'clean cut'}")

    # ---- S1: ground truth ---------------------------------------------------
    print(f"\n=== S1: do MKS-2's six known stranded artists fall inside the top {CUT}? ===")
    ranks: dict[str, tuple] = {}
    for label, rows in (("degree 1", d1), ("degree 2", d2)):
        order = sorted(rows, key=lambda r: -r["pop_raw"])
        for i, r in enumerate(order, 1):
            if r["name"] in MKS2_NAMES:
                ranks.setdefault(r["name"], (label, i, len(order), r["pop_raw"],
                                             r["degree"]))
    worst = 0
    for nm in MKS2_NAMES:
        if nm not in ranks:
            print(f"  {nm:<12} NOT FOUND in the degree<=2 sets")
            continue
        label, i, tot, pop, deg = ranks[nm]
        inside = "inside" if i <= CUT else "OUTSIDE"
        worst = max(worst, i)
        print(f"  {nm:<12} {label}, rank {i:>5} of {tot:,} by popularity  "
              f"pop_raw {pop:.4f}  deg {deg}  -> {inside} top {CUT}")
    print(f"\n  deepest MKS-2 artist sits at rank {worst}.")
    print(f"  -> a cut at {CUT} {'HOLDS' if worst <= CUT else 'FAILS'} on the six cases "
          "the stranding finding produced independently.")


if __name__ == "__main__":
    main()
