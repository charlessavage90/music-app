"""Archive-side measurement: which edges mutual k-NN removes, and from whom.

READ-ONLY. Reads the crawl archive; writes nothing, rebuilds nothing.
Owns the reciprocity figures in
`docs/superpowers/findings/2026-07-25-mutual-knn-stranding.md`.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-25-mutual-knn-stranding/reciprocity.py

The model here must match `pipeline.build_from_archive` exactly or its output
means nothing, so it is validated against the shipped graph before reporting
(see `validate()`). Two details are load-bearing and both were got wrong on the
first attempt:

  * **k is `BuilderConfig.max_neighbours_per_artist` = 50**, not 15. The `t15`
    in the artifact filename is a run tag, not the cap.
  * **The candidate list is filtered to crawled artists** (`known` in the
    pipeline) before the top-k is taken. Skipping that filter lets entries that
    the builder never considers push real neighbours out of the window.

Ranking is on unclipped strengths at `similarity_damping = 0.0`, which is the
raw ListenBrainz score — so ordering by `score` reproduces the builder's
ranking. If damping ever becomes non-zero this model must apply
`damped_strength` instead.
"""

from __future__ import annotations

import json
import random
import statistics as st
from functools import lru_cache
from pathlib import Path

ARCHIVE = Path("scratch/graph-archive/similar/listenbrainz")
K = 50  # BuilderConfig.max_neighbours_per_artist

# Predicted-neighbour sets that must match the shipped graph exactly.
# Sourced from the adopted artifact via degree_and_bridges.py.
EXPECTED = {
    "e9c832b0-384b-4ee6-aec0-111372784aac": (  # Pretenders
        "Blondie", "Crowded House", "Paul McCartney", "Roxy Music",
        "The Bangles", "The Cars",
    ),
    "3cb3928a-526c-4a3d-93c5-53315fa9bde0": ("Doves",),        # Elbow
    "b134d1bf-c7c7-4427-93ac-9fdbc2b59ef1": ("Tim Curry",),    # Meat Loaf
    "8846e4ff-0c19-4af2-872b-7a8dc7497f68": ("The Sisters of Mercy",),
    "6f607087-9c46-4bb2-a884-e4efc764554c": ("Dizzee Rascal",),
    "b9a2a9a6-7a40-48a6-bcb1-8eff5b89ad5b": ("Rogue Wave",),   # Nada Surf
}

KNOWN = {p.stem for p in ARCHIVE.glob("*.json")}


@lru_cache(maxsize=200_000)
def top_k(mbid: str) -> tuple[tuple[str, str, float], ...] | None:
    """An artist's own top-K candidates, as the builder computes them."""
    f = ARCHIVE / f"{mbid}.json"
    if not f.exists():
        return None
    rows = json.loads(f.read_text(encoding="utf-8"))
    scored = [
        (r["artist_mbid"], r.get("name", ""), r.get("score", 0))
        for r in rows
        if r.get("artist_mbid") in KNOWN and r.get("artist_mbid") != mbid
    ]
    scored.sort(key=lambda t: (-t[2], t[0]))  # ties on lowest MBID, as the builder
    return tuple(scored[:K])


def mutual(mbid: str) -> list[str] | None:
    """Neighbours surviving the both-ways rule: the artist's final edges."""
    mine = top_k(mbid)
    if mine is None:
        return None
    out = []
    for dst, name, _score in mine:
        theirs = top_k(dst)
        if theirs and mbid in {x[0] for x in theirs}:
            out.append(name)
    return out


def validate() -> None:
    """Refuse to report figures from a model that disagrees with the graph."""
    for mbid, expected in EXPECTED.items():
        got = tuple(sorted(mutual(mbid) or []))
        if got != tuple(sorted(expected)):
            raise SystemExit(
                f"model does not reproduce the shipped graph for {mbid}:\n"
                f"  expected {sorted(expected)}\n  got      {list(got)}"
            )
    print(f"model validated against {len(EXPECTED)} known artists in the graph")


def main() -> None:
    print(f"crawled artists: {len(KNOWN)}, k = {K}")
    validate()

    print("\n=== who reciprocates, for the stranded artists ===")
    for mbid, expected in EXPECTED.items():
        mine = top_k(mbid) or ()
        keeps = mutual(mbid) or []
        print(
            f"  {mbid}: own top-{K} = {len(mine)}, mutual = {len(keeps)}"
            f"  {sorted(keeps)}"
        )
        # The dropped head of the list is the finding: an artist's most
        # similar neighbours are the ones least likely to reciprocate.
        dropped = [n for _, n, _ in mine[:6] if n not in set(expected)]
        print(f"      top of its own list, dropped: {dropped}")

    random.seed(0)
    sample = random.sample(sorted(KNOWN), 150)
    rates, degrees = [], []
    for mbid in sample:
        mine = top_k(mbid)
        if not mine:
            continue
        keeps = mutual(mbid) or []
        degrees.append(len(keeps))
        rates.append(len(keeps) / len(mine))

    print(f"\n=== random sample of {len(rates)} crawled artists ===")
    print(
        f"mutual share of own top-{K}: mean {st.mean(rates):.1%}, "
        f"median {st.median(rates):.1%}"
    )
    print(
        f"resulting degree: median {st.median(degrees):.0f}, "
        f"mean {st.mean(degrees):.1f}"
    )
    for cut in (1, 2):
        share = 100 * sum(1 for d in degrees if d <= cut) / len(degrees)
        print(f"artists left with <= {cut} connection(s): {share:.1f}%")


if __name__ == "__main__":
    main()
