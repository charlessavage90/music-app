"""POST-HOC probe (GRT-P3): is ALG-B's measured cost a property of the
algorithm, or of the cap it was measured at?

NOT pre-registered, and labelled as such. Run 2026-07-29 to answer a
sequencing question the owner asked after the GRT read: is there a meaningful
advantage to running Track B (cap selection, MKS-5b) BEFORE the ALG-B
re-crawl? Every ALG-B measurement so far was taken at k=50, and RC-A2 located
the collapsed top-0.1% artists at rank 50-97 in their own candidates' lists —
just outside the cut. So the question is cheaply answerable offline.

Read-only, no network. Reads the GRT trial archive already on disk.

⚠ THREE CAVEATS, and none of them is small:

  1. It ranks candidates on the RAW SOURCE SCORE. The real pipeline ranks on
     damped, unclipped strengths computed over the whole graph
     (`pipeline.damped_strength`), so these degrees approximate the builder's
     rather than reproduce them.
  2. It runs on a 3,000-node trial archive, not the 74k production graph.
     Degree distributions do not transfer between the two.
  3. It measures ONLY the benefit side of raising k. MKS-5b exists because
     loosening the both-ways cap restores unbounded degree, and removing
     unbounded hubs is what `capfix` won its blind listen for. A number here
     is an input to the cap-selection simulation, NEVER a licence to change k.

So this probe justifies RUNNING the simulation. It does not select a k, and
must not be cited as though it had.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"
ALG_B = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)
ARCHIVE = SCRATCH / "grt-archive-algb" / "similar" / "listenbrainz" / ALG_B

# The four top-0.1% artists RC-A2 found reciprocating nothing under ALG-B.
NAMES_OF_INTEREST = ("R.E.M.", "Pixies", "The xx", "PJ Harvey")
KS = (50, 60, 75, 100)
FLOOR = 8  # acceptance.PRODUCTION_ACCEPTANCE.famous_min_degree_floor


def load() -> tuple[dict[str, list[tuple[str, float]]], dict[str, str]]:
    lists: dict[str, list[tuple[str, float]]] = {}
    names: dict[str, str] = {}
    for path in ARCHIVE.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        rows = data[0] if data and isinstance(data[0], list) else data
        ordered = sorted(
            (
                (r["artist_mbid"], float(r["score"]), r.get("name") or "")
                for r in rows
                if isinstance(r, dict)
                and r.get("artist_mbid")
                and r.get("score") is not None
                and r["artist_mbid"] != path.stem
            ),
            key=lambda t: (-t[1], t[0]),  # same tie-break as the source parser
        )
        lists[path.stem] = [(m, s) for m, s, _ in ordered]
        for mbid, _score, name in ordered:
            if name and mbid not in names:
                names[mbid] = name
    return lists, names


def degrees_at_k(lists, k: int) -> dict[str, int]:
    """Mutual kNN: keep (u,v) only if each endpoint is in the other's top-k."""
    topk = {u: {m for m, _ in cands[:k]} for u, cands in lists.items()}
    deg: dict[str, int] = defaultdict(int)
    for u, nbrs in topk.items():
        for v in nbrs:
            if v in topk and u in topk[v]:
                deg[u] += 1
    return deg


def main() -> None:
    lists, names = load()
    by_name = {
        names[m]: m for m in lists if names.get(m) in NAMES_OF_INTEREST
    }
    degs = {k: degrees_at_k(lists, k) for k in KS}

    out: dict = {
        "probe": "GRT-P3",
        "pre_registered": False,
        "archive": str(ARCHIVE),
        "responses": len(lists),
        "floor": FLOOR,
        "caveats": [
            "ranks on raw source score, not pipeline damped strengths",
            "3,000-node trial archive, not the 74k production graph",
            "measures only the benefit of raising k; MKS-5b's hub cost is unmeasured here",
        ],
        "artists": {},
        "population": {},
    }
    for name in NAMES_OF_INTEREST:
        mbid = by_name.get(name)
        if not mbid:
            out["artists"][name] = {"in_archive": False}
            continue
        out["artists"][name] = {
            "in_archive": True,
            "top100_fully_fetched": all(m in lists for m, _ in lists[mbid][:100]),
            "degree": {str(k): degs[k].get(mbid, 0) for k in KS},
        }
    for k in KS:
        vals = list(degs[k].values())
        out["population"][str(k)] = {
            "nodes_with_an_edge": len(vals),
            "below_floor": sum(1 for v in vals if v < FLOOR),
            "below_floor_share": round(
                sum(1 for v in vals if v < FLOOR) / max(1, len(lists)), 4
            ),
            "mean_degree": round(sum(vals) / max(1, len(vals)), 2),
        }

    (HERE / "grt_k_sensitivity.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
