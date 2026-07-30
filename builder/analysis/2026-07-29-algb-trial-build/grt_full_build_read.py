"""GRT-P4 (post-hoc): the two open questions, answered at PRODUCTION scale.

Governing document:
docs/superpowers/specs/2026-07-29-algb-trial-build-preregistration.md

The trial build ran at 3,000 artists and left two questions explicitly open:

  GRT-P2  Does the acceptance guard still cover the artists it names, once
          the graph is full-size? R.E.M. left the top-25-by-popularity
          sample at trial scale, so the degree floor never inspected it.
          "Rank among 2,904 is not rank among 74,000."
  GRT-C4  Component membership. At trial scale the pre-registered ratio bar
          was undefined because the control's readable exclusion rate was
          exactly zero (GRT-P1).

Both are now answerable from two REAL full builds differing in exactly one
column (the source algorithm), both carrying the drop rule:

  ALG-E   scratch/graph-dropnameless-verify.bin   (GR-4)
  ALG-B   scratch/graph-algb-full.bin             (overnight crawl)

Read-only. Adopts nothing. Fame bands use percentile RANK over the adopted
artifact, the same frame the trial-scale scorer used, so the two scales are
comparable.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

from artistpath_builder.acceptance import PRODUCTION_ACCEPTANCE as ACC
from artistpath_builder.artifact import deserialise

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"

ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
ARMS = {
    "ALG-E": SCRATCH / "graph-dropnameless-verify.bin",
    "ALG-B": SCRATCH / "graph-algb-full.bin",
}
# Pre-prune populations, taken from each build's own log line
# ("largest component: X of Y artists"). Y is not recoverable from the
# artifact, which holds only the component.
PRE_PRUNE = {"ALG-E": 74_957, "ALG-B": 74_966}

WATCH = ("R.E.M.", "Pixies", "The xx", "PJ Harvey", "Radiohead", "The Beatles")
BANDS = (
    ("top 0.1%", 0.999, 1.0001),
    ("top 1%", 0.99, 0.999),
    ("top 10%", 0.90, 0.99),
    ("upper half", 0.50, 0.90),
    ("lower half", 0.0, 0.50),
)


ALG_B_KEY = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)
ARCHIVES = {
    "ALG-E": SCRATCH / "graph-archive" / "similar" / "listenbrainz",
    "ALG-B": SCRATCH / "grt-archive-algb" / "similar" / "listenbrainz" / ALG_B_KEY,
}


def crawled_mbids(label: str) -> set[str]:
    """Artists whose OWN response this arm holds. The two arms' BFS frontiers
    diverge, so this is not the same set for both — which is the whole reason
    the band figures are restricted to it."""
    return {p.stem for p in ARCHIVES[label].glob("*.json")}


def load(path: Path):
    return deserialise(path.read_bytes())


def ruler() -> dict[str, float]:
    payload = ADOPTED.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != ADOPTED_SHA:
        raise SystemExit(f"adopted artifact mismatch: {actual}")
    g = deserialise(payload)
    pop = np.asarray(g.pop_raw, dtype=np.float64)
    order = pop.argsort(kind="stable")
    pctl = np.empty_like(pop)
    pctl[order] = np.arange(len(pop)) / (len(pop) - 1)
    return {m: float(pctl[i]) for i, m in enumerate(g.mbids)}


def band_of(p: float | None) -> str | None:
    if p is None:
        return None
    for name, lo, hi in BANDS:
        if lo <= p < hi:
            return name
    return None


def read_arm(label: str, graph, frame: dict[str, float]) -> dict:
    deg = np.diff(graph.offsets).astype(np.int64)
    pop = np.asarray(graph.pop_raw, dtype=np.float64)
    order = np.argsort(-pop, kind="stable")
    top = deg[order[: ACC.famous_sample]]
    present = set(graph.mbids)

    watch = {}
    for name in WATCH:
        if name not in graph.names:
            watch[name] = {"in_component": False}
            continue
        i = graph.names.index(name)
        rank = int(np.where(order == i)[0][0])
        watch[name] = {
            "in_component": True,
            "degree": int(deg[i]),
            "popularity_rank": rank,
            "inside_top25_sample": rank < ACC.famous_sample,
            "below_floor": int(deg[i]) < ACC.famous_min_degree_floor,
        }

    # GRT-C4 at production scale, per fame band.
    #
    # ⚠ Restricted to artists THIS ARM ACTUALLY CRAWLED, and that restriction
    # is load-bearing. The two arms' BFS frontiers diverge — ALG-B never
    # fetched 31% of the adopted artifact's artists, and reached ~23k the
    # adopted crawl never saw. Measuring "absent from the component" against
    # the adopted frame therefore conflates NEVER CRAWLED with STRANDED, and
    # the first draft of this probe did exactly that: it reported 55.8% of
    # below-median artists "absent" under ALG-B when the stranded share is
    # 7.0%. Both denominators are reported so the gap is visible rather than
    # absorbed.
    crawled = crawled_mbids(label)
    per_band = {}
    members = defaultdict(list)
    for mbid, p in frame.items():
        b = band_of(p)
        if b:
            members[b].append(mbid)
    for name, _lo, _hi in BANDS:
        ms = members.get(name, [])
        in_arm = [m for m in ms if m in crawled]
        stranded = [m for m in in_arm if m not in present]
        per_band[name] = {
            "in_adopted_frame": len(ms),
            "crawled_by_this_arm": len(in_arm),
            "never_crawled": len(ms) - len(in_arm),
            "crawled_then_stranded": len(stranded),
            # THE figure: of what this arm crawled, what did it strand.
            "stranded_share_of_crawled": round(
                len(stranded) / max(1, len(in_arm)), 5
            ),
        }

    return {
        "nodes": graph.artist_count,
        "edges": graph.edge_count,
        "pre_prune": PRE_PRUNE[label],
        "excluded": PRE_PRUNE[label] - graph.artist_count,
        "exclusion_rate": round(
            1 - graph.artist_count / PRE_PRUNE[label], 5
        ),
        "acceptance_top25": {
            "median_degree": float(statistics.median(top.tolist())),
            "median_floor": ACC.famous_median_degree_floor,
            "median_passes": statistics.median(top.tolist())
            >= ACC.famous_median_degree_floor,
            "min_degree": int(top.min()),
            "min_floor": ACC.famous_min_degree_floor,
            "min_passes": int(top.min()) >= ACC.famous_min_degree_floor,
        },
        "canonical_absent": sorted(
            n for n in ACC.canonical_names if n not in set(graph.names)
        ),
        "watched_artists": watch,
        "band_absence": per_band,
    }


def main() -> None:
    frame = ruler()
    out = {"probe": "GRT-P4", "pre_registered": False, "arms": {}}
    for label, path in ARMS.items():
        out["arms"][label] = read_arm(label, load(path), frame)
        out["arms"][label]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()

    e, b = out["arms"]["ALG-E"], out["arms"]["ALG-B"]
    out["comparison"] = {
        "exclusion_rate_ALG_E": e["exclusion_rate"],
        "exclusion_rate_ALG_B": b["exclusion_rate"],
        "ratio": round(b["exclusion_rate"] / e["exclusion_rate"], 2)
        if e["exclusion_rate"]
        else None,
        "bar": 2.0,
        "extra_artists_stranded_by_ALG_B": b["excluded"] - e["excluded"],
    }
    (HERE / "grt_full_build_read.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
