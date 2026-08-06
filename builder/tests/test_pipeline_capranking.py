"""The §2.8 tie-break defect: top-k selection must rank UNCLIPPED strengths.

p99_log_clip collapses the top ~1% of raw scores to exactly 1.0. While the
mutual-kNN top-k ranked those clipped values, every ceiling-saturated list
was decided by the lowest-MBID tie-break — which is how The Beatles kept 7
of 100 neighbours and Radiohead kept none (Phase 1 log §2.8). The cap must
rank the unclipped damped strengths while the artifact still carries the
clipped scores.
"""

import json

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

X = "a" * 36       # the saturated artist
STRONG = "e" * 36  # genuinely stronger neighbour (cooc 200) — HIGHER mbid
WEAK = "c" * 36    # weaker neighbour (cooc 150) — LOWER mbid, so it wins
                   # X's one slot iff selection wrongly ranks clipped scores


def _pad(i: int) -> str:
    # Padding mbids sort above X, WEAK and STRONG.
    return f"f{i:035d}"


def _body(rows: list[tuple[str, int]]) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": m, "name": m[:4], "comment": "", "score": s}
            for m, s in rows
        ]
    ).encode()


def _seed(archive, source) -> None:
    def put(mbid, rows):
        archive.put(f"similar/{source.name}/{mbid}.json", _body(rows))

    put(X, [(STRONG, 200), (WEAK, 150)])
    put(STRONG, [(X, 200)])
    put(WEAK, [(X, 150)])
    # 200 mutual padding pairs at cooc 100 hold the p99 down at 100, so both
    # of X's edges land above it and clip to exactly 1.0 — reproducing the
    # ceiling-saturation regime of §2.8 in miniature.
    for i in range(200):
        a, b = _pad(2 * i), _pad(2 * i + 1)
        put(a, [(b, 100)])
        put(b, [(a, 100)])


def _build(tmp_path):
    # drop_unlistenable pinned off: cap ranking is the subject; the synthetic
    # archive is covered by no ULF- census (factor-table-control idiom).
    #
    # cap_strategy pinned to mutual_knn since the MSW- adoption of 2026-08-06
    # moved the default: max_neighbours_per_artist below is a mutual_knn knob
    # that trimmed_union ignores entirely, so left on the new default this
    # helper would silently stop testing the thing it names. require_fame
    # pinned off for the usual reason — no fame stage on this archive.
    config = BuilderConfig(
        requests_per_second=1000.0,
        max_neighbours_per_artist=1,
        drop_unlistenable=False,
        cap_strategy="mutual_knn",
        require_fame=False,
    )
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed(archive, source)
    return build_from_archive(config, archive, source)


def test_topk_selection_ranks_unclipped_strengths_not_clipped_scores(tmp_path):
    graph = _build(tmp_path)
    # k=1: X's one slot must go to STRONG (cooc 200), not to WEAK — WEAK only
    # wins if the MBID tie-break over two clipped 1.0s is deciding. The
    # largest-component step then keeps {X, STRONG} (X carries the lowest
    # MBID, so its size-2 component beats the padding pairs' ties).
    assert X in graph.mbids and STRONG in graph.mbids
    assert WEAK not in graph.mbids
    x = graph.mbids.index(X)
    row = list(graph.neighbours[graph.offsets[x] : graph.offsets[x + 1]])
    assert row == [graph.mbids.index(STRONG)]


def test_emitted_scores_are_still_clipped(tmp_path):
    # The fix changes membership, never the emitted values: X's surviving
    # edge is above the p99 and must still carry the ceiling score of 1.0,
    # not the raw strength that ranked it.
    graph = _build(tmp_path)
    x = graph.mbids.index(X)
    scores = list(graph.scores[graph.offsets[x] : graph.offsets[x + 1]])
    assert scores == [1.0]
