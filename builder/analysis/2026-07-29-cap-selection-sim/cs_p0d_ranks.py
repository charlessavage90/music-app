"""CS-P0d -- WHERE in the candidate list the obscure candidates sit, and whether the
list is truncated against them.

Read-only. Asserts the artifact sha256. Builds nothing, touches no network.

WHY. CS-P0c found that the crawl returns EXACTLY 100 candidates for every top-1%
artist -- the source's `limit_100` -- and that superstars get zero candidates below the
top decile within those 100. Two different remedies follow depending on one fact:

  * If obscure candidates cluster at the BOTTOM of the returned list (ranks ~80-100),
    the list is truncated against them and `limit` is the binding constraint. Remedy:
    re-crawl at a higher limit. Cheap to state, expensive to run (a full re-crawl).
  * If they are spread through the list, `limit` is not what is excluding them, and a
    higher limit would return more of the same. Remedy: the `threshold` lever (STC-6)
    or a different algorithm -- a different re-crawl, not a bigger one.

Both remedies are re-crawls and both are the owner's call; this only says WHICH.

Reported for the top 1% (where obscure candidates exist to rank) and, separately, the
saturation check: what share of ALL archived artists come back at exactly the limit.
An artist below the limit was not truncated, so its zero-obscure-candidates reading is
a statement about the source's opinion rather than about the cut-off.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/cs_p0d_ranks.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "src"))

ARCHIVE = ROOT / "builder" / "scratch" / "graph-archive"
GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
OUT = HERE / "cs_p0d_ranks.json"
LIMIT = 100  # from BuilderConfig.algorithm: "..._limit_100_..."


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    sorted_values = values[order]
    start = 0
    for end in range(1, len(sorted_values) + 1):
        if end == len(sorted_values) or sorted_values[end] != sorted_values[start]:
            if end - start > 1:
                ranks[order[start:end]] = ranks[order[start:end]].mean()
            start = end
    return ranks / max(1, len(values) - 1)


def main() -> int:
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print("ARTIFACT MISMATCH", file=sys.stderr)
        return 2

    from artistpath_api.graph_store import GraphStore
    from artistpath_builder.archive import LocalArchive
    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.sources.listenbrainz import ListenBrainzSource

    graph = GraphStore.load(GRAPH)
    pop_pctl = percentile_ranks(np.asarray(graph.pop_raw, dtype=np.float64))
    id_of = {m: i for i, m in enumerate(graph.mbids)}

    archive = LocalArchive(ARCHIVE)
    source = ListenBrainzSource(BuilderConfig())
    prefix = f"similar/{source.name}/"

    def candidates_of(mbid: str):
        payload = archive.get(f"{prefix}{mbid}.json")
        return None if payload is None else source.parse(payload, exclude_mbid=mbid)

    # (a) Where obscure candidates rank, for the top 1%.
    top1 = np.flatnonzero(pop_pctl >= 0.99)
    obscure_ranks: list[int] = []
    last_decile_obscure = 0
    total_obscure = 0
    for count, node in enumerate(top1, 1):
        if count % 200 == 0:
            print(f"  top1% scanned {count}/{len(top1)}", flush=True)
        cand = candidates_of(graph.mbids[int(node)])
        if not cand:
            continue
        # `parse` returns neighbours sorted by descending score, so index == rank-1.
        for rank, neighbour in enumerate(cand, 1):
            j = id_of.get(neighbour.mbid)
            if j is not None and pop_pctl[j] < 0.90:
                obscure_ranks.append(rank)
                total_obscure += 1
                if rank > 0.9 * LIMIT:
                    last_decile_obscure += 1

    ranks_arr = np.array(obscure_ranks, dtype=np.float64)

    # (b) Saturation: what share of ALL archived artists return exactly the limit.
    all_nodes = np.arange(graph.artist_count)
    rng = np.random.default_rng(20260729)  # fixed seed -- determinism (design SS9)
    sample = rng.choice(all_nodes, size=3000, replace=False)
    returned_counts: list[int] = []
    for count, node in enumerate(sample, 1):
        if count % 500 == 0:
            print(f"  sample scanned {count}/{len(sample)}", flush=True)
        cand = candidates_of(graph.mbids[int(node)])
        if cand is not None:
            returned_counts.append(len(cand))
    counts_arr = np.array(returned_counts, dtype=np.float64)

    report = {
        "artifact_sha256": actual,
        "source_limit": LIMIT,
        "obscure_candidate_ranks_top1pct": {
            "total_obscure_candidates": total_obscure,
            "mean_rank": round(float(ranks_arr.mean()), 3) if ranks_arr.size else None,
            "median_rank": float(np.median(ranks_arr)) if ranks_arr.size else None,
            "p25_rank": float(np.percentile(ranks_arr, 25)) if ranks_arr.size else None,
            "p75_rank": float(np.percentile(ranks_arr, 75)) if ranks_arr.size else None,
            "share_in_last_decile_of_list": (
                round(last_decile_obscure / total_obscure, 6) if total_obscure else None
            ),
            "reading": (
                "mean rank near LIMIT => the list is truncated against obscure "
                "candidates and `limit` binds; mean rank near the middle => it is not."
            ),
        },
        "saturation_random_sample": {
            "sampled": int(counts_arr.size),
            "seed": 20260729,
            "mean_returned": round(float(counts_arr.mean()), 3),
            "share_at_limit": round(float((counts_arr >= LIMIT).mean()), 6),
            "median_returned": float(np.median(counts_arr)),
        },
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
