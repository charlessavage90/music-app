"""CS-P0f -- is the source `score` symmetric, and what does mutual k-NN therefore test?

Read-only over the archive. Answers a specific question asked 2026-07-29:

    `score` is a co-occurrence count -- the number of times two artists turn up
    together in someone's listening. Co-occurrence is symmetric by construction. So
    does the mutual k-NN reciprocity requirement duplicate a cut the score already
    makes?

The answer turns on a fact, not an argument, so it is measured:

  (1) SYMMETRY. For pairs where BOTH artists have an archived response, does
      score(A->B) equal score(B->A)? If yes, the quantity carries no directional
      information and `symmetrise`'s "keep the stronger" is a no-op on it.
  (2) RANK ASYMMETRY. For those same pairs, what is rank(B in A's list) vs
      rank(A in B's list)? A symmetric score can still produce wildly asymmetric
      ranks, because a rank depends on the artist's OTHER scores.
  (3) WHO LOSES. Among pairs the mutual test rejects, which direction fails, and
      how does the popularity gap between the endpoints relate to it?

(3) is the point. If the score is symmetric, then "is A in B's top-k" is decided
entirely by B's other co-occurrence counts -- i.e. by how much listening B attracts.
So the reciprocity test would be reading a POPULARITY quantity while presenting as a
similarity filter. That is the documented mechanism of Phase 1 log SS2.10 (famous->obscure
edges depleted below a structure-preserving null), and this script checks whether the
arithmetic actually supports that reading.

CURRENCY. `pop_pctl` is computed by ranking the artifact's `pop_raw`. `pop_raw` is
never read as a rank (CLAUDE.md; log SS2.12).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/cs_p0f_symmetry.py
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
OUT = HERE / "cs_p0f_symmetry.json"
K = 50  # BuilderConfig.max_neighbours_per_artist
SEED = 20260729
SAMPLE_ARTISTS = 400


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
    pctl_of = {m: float(pop_pctl[i]) for i, m in enumerate(graph.mbids)}
    name_of = {m: graph.names[i] for i, m in enumerate(graph.mbids)}

    archive = LocalArchive(ARCHIVE)
    source = ListenBrainzSource(BuilderConfig())
    prefix = f"similar/{source.name}/"

    cache: dict[str, dict[str, float] | None] = {}
    rank_cache: dict[str, dict[str, int]] = {}

    def lists_for(mbid: str):
        if mbid not in cache:
            payload = archive.get(f"{prefix}{mbid}.json")
            if payload is None:
                cache[mbid] = None
                rank_cache[mbid] = {}
            else:
                neighbours = source.parse(payload, exclude_mbid=mbid)
                cache[mbid] = {n.mbid: n.score for n in neighbours}
                rank_cache[mbid] = {n.mbid: i + 1 for i, n in enumerate(neighbours)}
        return cache[mbid]

    rng = np.random.default_rng(SEED)
    sample = rng.choice(graph.artist_count, size=SAMPLE_ARTISTS, replace=False)

    equal = 0
    unequal = 0
    ratios: list[float] = []
    rank_pairs: list[tuple[int, int]] = []
    rejected_direction: list[dict[str, object]] = []
    both_in = 0
    one_way = 0
    examples: list[dict[str, object]] = []

    for count, node in enumerate(sample, 1):
        if count % 100 == 0:
            print(f"  {count}/{SAMPLE_ARTISTS}", flush=True)
        a = graph.mbids[int(node)]
        a_list = lists_for(a)
        if not a_list:
            continue
        for b, score_ab in a_list.items():
            b_list = lists_for(b)
            if not b_list or a not in b_list:
                continue
            score_ba = b_list[a]
            if score_ab == score_ba:
                equal += 1
            else:
                unequal += 1
                lo, hi = sorted((score_ab, score_ba))
                if lo > 0:
                    ratios.append(hi / lo)
            rank_ab = rank_cache[a][b]
            rank_ba = rank_cache[b][a]
            rank_pairs.append((rank_ab, rank_ba))

            a_top = rank_ab <= K
            b_top = rank_ba <= K
            if a_top and b_top:
                both_in += 1
            elif a_top or b_top:
                one_way += 1
                # The mutual test REJECTS this edge. Which endpoint refused it?
                refuser, refused = (b, a) if a_top else (a, b)
                gap = pctl_of.get(refuser, 0.0) - pctl_of.get(refused, 0.0)
                rejected_direction.append({
                    "refuser_pctl": pctl_of.get(refuser, 0.0),
                    "refused_pctl": pctl_of.get(refused, 0.0),
                    "gap": gap,
                })
                if len(examples) < 12 and abs(gap) > 0.3:
                    examples.append({
                        "kept_it_in_top_k": name_of.get(refused, "?"),
                        "kept_pctl": round(pctl_of.get(refused, 0.0), 4),
                        "refused_it": name_of.get(refuser, "?"),
                        "refuser_pctl": round(pctl_of.get(refuser, 0.0), 4),
                        "rank_each_way": [rank_ab, rank_ba],
                    })

    gaps = np.array([r["gap"] for r in rejected_direction], dtype=np.float64)
    ranks_arr = np.array(rank_pairs, dtype=np.float64)

    report = {
        "artifact_sha256": actual,
        "k": K,
        "seed": SEED,
        "sampled_artists": SAMPLE_ARTISTS,
        "reciprocated_pairs_examined": equal + unequal,
        "symmetry": {
            "score_identical_both_directions": equal,
            "score_differs": unequal,
            "share_identical": round(equal / max(1, equal + unequal), 6),
            "max_ratio_when_differing": round(float(max(ratios)), 4) if ratios else None,
        },
        "rank_asymmetry": {
            "mean_abs_rank_difference": round(float(np.abs(ranks_arr[:, 0] - ranks_arr[:, 1]).mean()), 3) if ranks_arr.size else None,
            "median_abs_rank_difference": float(np.median(np.abs(ranks_arr[:, 0] - ranks_arr[:, 1]))) if ranks_arr.size else None,
            "spearman_rank_vs_rank": (
                round(float(np.corrcoef(ranks_arr[:, 0], ranks_arr[:, 1])[0, 1]), 4)
                if ranks_arr.size > 2 else None
            ),
        },
        "mutual_test": {
            "both_endpoints_rank_each_other_in_top_k": both_in,
            "only_one_does_EDGE_REJECTED": one_way,
            "rejection_share": round(one_way / max(1, both_in + one_way), 6),
        },
        "who_refuses": {
            "note": (
                "gap = refuser_pctl - refused_pctl. Positive means the MORE popular "
                "endpoint is the one that failed to rank the other in its top-k, i.e. "
                "the famous->obscure direction is what the mutual test cuts."
            ),
            "mean_gap": round(float(gaps.mean()), 4) if gaps.size else None,
            "median_gap": round(float(np.median(gaps)), 4) if gaps.size else None,
            "share_refuser_more_popular": round(float((gaps > 0).mean()), 6) if gaps.size else None,
            "rejections_examined": int(gaps.size),
        },
        "examples": examples,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "examples"}, indent=2))
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
