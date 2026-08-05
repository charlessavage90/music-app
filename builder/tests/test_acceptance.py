"""The acceptance check must reject the §2.8 defect, not merely pass.

The negative case is built through the pre-Track-1 code path: the SAME archive,
with exactly one knob moved — whether `mutual_knn_cap` ranks top-k on the
clipped scores (the defect) or on the unclipped strengths (the fix). That is
the same one-knob intervention log §2.8 used to determine the mechanism.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from artistpath_builder import graph as graph_mod
from artistpath_builder import pipeline as pipeline_mod
from artistpath_builder.acceptance import (
    AcceptanceCriteria,
    ArtifactRejected,
    check_acceptance,
)
from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.graph import Graph
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

K = 4
N_FAMOUS = 10
N_SAT = 20
N_PAD_CLIQUES = 6
PAD_CLIQUE_SIZE = 40

DESIGNATED = 300  # a famous artist's genuinely strongest satellites
ORDINARY = 260    # its remaining satellites — still above the p99 ceiling
PADDING = 100     # bulk edges, below the ceiling; they set the p99


def _famous_mbid(i: int) -> str:
    # Famous artists carry HIGH mbids, so the lowest-mbid tie-break works
    # against them — the arrangement log §2.8 records in the real data.
    return f"f{i:035d}"


def _sat_mbid(j: int) -> str:
    return f"0{j:035d}"


def _pad_mbid(c: int, i: int) -> str:
    return f"9{c:017d}{i:018d}"


def _body(rows: list[tuple[str, str, int]]) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": m, "name": name, "comment": "", "score": score}
            for m, name, score in rows
        ]
    ).encode()


def _seed(archive: LocalArchive, source: ListenBrainzSource) -> None:
    """A miniature ceiling-saturation regime.

    Every famous artist lists every satellite above the p99, so its whole
    list saturates at exactly 1.0 and its top-k is decided purely by the
    mbid tie-break — the §2.8 regime. Satellites are over-subscribed (ten
    famous artists compete for four slots each), which is what makes the
    reciprocity fail rather than merely reshuffle.

    Each satellite is designated by two consecutive famous artists, so the
    surviving structure is one connected component rather than ten stars.
    """
    names: dict[str, str] = {}
    lists: dict[str, list[tuple[str, int]]] = {}

    def add(a: str, b: str, score: int) -> None:
        lists.setdefault(a, []).append((b, score))
        lists.setdefault(b, []).append((a, score))

    for i in range(N_FAMOUS):
        names[_famous_mbid(i)] = f"FAMOUS-{i:02d}"
    for j in range(N_SAT):
        names[_sat_mbid(j)] = f"sat-{j:02d}"

    for i in range(N_FAMOUS):
        designated = {(2 * i + t) % N_SAT for t in range(4)}
        for j in range(N_SAT):
            add(
                _famous_mbid(i),
                _sat_mbid(j),
                DESIGNATED if j in designated else ORDINARY,
            )

    # Padding cliques hold the p99 down so only the famous band saturates.
    # Sized under the famous component so `largest_component` keeps the part
    # under test. Their scores are all equal, so they behave identically
    # under both rankings and cannot contribute to the contrast.
    for c in range(N_PAD_CLIQUES):
        for a in range(PAD_CLIQUE_SIZE):
            names[_pad_mbid(c, a)] = f"pad-{c}-{a:02d}"
            for b in range(a + 1, PAD_CLIQUE_SIZE):
                add(_pad_mbid(c, a), _pad_mbid(c, b), PADDING)

    for mbid, rows in lists.items():
        archive.put(
            f"similar/{source.name}/{mbid}.json",
            _body([(dst, names.get(dst, ""), score) for dst, score in rows]),
        )


def _build(tmp_path, *, defective: bool) -> Graph:
    """Build the same archive with clipped (defective) or unclipped ranking."""
    # drop_unlistenable pinned off: acceptance is the subject; the synthetic
    # archive is covered by no ULF- census (factor-table-control idiom).
    config = BuilderConfig(max_neighbours_per_artist=K, drop_unlistenable=False)
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed(archive, source)

    real_cap = graph_mod.mutual_knn_cap
    if defective:
        # Pre-Track-1 behaviour: rank the top-k on the emitted (clipped)
        # scores by discarding the unclipped ranking the fix supplies.
        pipeline_mod.mutual_knn_cap = (
            lambda adjacency, k, ranking=None: real_cap(adjacency, k)
        )
    try:
        return build_from_archive(config, archive, source)
    finally:
        pipeline_mod.mutual_knn_cap = real_cap


# Scaled to the miniature: k is 4 here, not 50.
MINIATURE = AcceptanceCriteria(
    canonical_names=tuple(f"FAMOUS-{i:02d}" for i in range(N_FAMOUS)),
    famous_sample=N_FAMOUS,
    famous_median_degree_floor=3.0,
    famous_min_degree_floor=2,
    node_count=(20, 200),
    edge_count=(40, 2_000),
    median_degree=(1.0, 10.0),
)


def test_healthy_build_is_accepted(tmp_path):
    graph = _build(tmp_path, defective=False)
    check_acceptance(graph, MINIATURE)


def test_tiebreak_defect_is_rejected(tmp_path):
    """The negative case: same archive, clipped ranking, defect reproduced."""
    graph = _build(tmp_path, defective=True)

    # The defect must actually be present, or the test proves nothing about
    # the check. This is the §2.8 signature: famous artists dropped out of
    # the largest connected component entirely.
    survivors = [n for n in graph.names if n.startswith("FAMOUS-")]
    assert len(survivors) < N_FAMOUS, (
        "fixture did not reproduce the defect; the check was never exercised"
    )

    with pytest.raises(ArtifactRejected) as excinfo:
        check_acceptance(graph, MINIATURE)
    assert "canonical artist" in str(excinfo.value)


def _graph(names: list[str], degrees: list[int], pop: list[float]) -> Graph:
    """A hand-built graph with the given per-node degree and popularity.

    Neighbour identity is irrelevant to every criterion under test, so the
    rows are filled with node 0.
    """
    offsets = np.zeros(len(names) + 1, dtype=np.int32)
    for i, degree in enumerate(degrees):
        offsets[i + 1] = offsets[i] + degree
    total = int(offsets[-1])
    return Graph(
        mbids=[f"{i:036d}" for i in range(len(names))],
        names=names,
        disambiguations=[""] * len(names),
        pop_raw=pop,
        offsets=offsets,
        neighbours=np.zeros(total, dtype=np.int32),
        scores=np.ones(total, dtype=np.float32),
        edge_types=np.zeros(total, dtype=np.uint8),
    )


def _healthy(n: int = 40) -> tuple[list[str], list[int], list[float]]:
    names = [f"artist-{i:02d}" for i in range(n)]
    degrees = [20] * n
    pop = [1.0 - i / n for i in range(n)]
    return names, degrees, pop


CRITERIA = AcceptanceCriteria(
    canonical_names=("artist-00",),
    famous_sample=10,
    famous_median_degree_floor=10.0,
    famous_min_degree_floor=5,
    node_count=(10, 100),
    edge_count=(100, 2_000),
    median_degree=(5.0, 40.0),
)


def test_famous_median_degree_floor_rejects_a_top_of_distribution_collapse():
    """The §2.8 signature with nobody deleted: only the famous collapse."""
    names, degrees, pop = _healthy()
    for i in range(10):  # the ten most popular
        degrees[i] = 4
    with pytest.raises(ArtifactRejected, match="median degree"):
        check_acceptance(_graph(names, degrees, pop), CRITERIA)


def test_famous_min_degree_floor_rejects_a_single_near_isolated_star():
    names, degrees, pop = _healthy()
    degrees[0] = 1  # the single most popular artist, all but cut off
    with pytest.raises(ArtifactRejected, match="minimum degree"):
        check_acceptance(_graph(names, degrees, pop), CRITERIA)


def test_shape_bounds_reject_a_graph_that_lost_most_of_its_nodes():
    names, degrees, pop = _healthy(n=9)
    with pytest.raises(ArtifactRejected, match="artist count"):
        check_acceptance(_graph(names, degrees, pop), CRITERIA)


def test_every_violation_is_reported_at_once():
    names, degrees, pop = _healthy()
    names[0] = "renamed"          # canonical artist absent
    degrees[:10] = [2] * 10       # famous collapse
    problems = None
    try:
        check_acceptance(_graph(names, degrees, pop), CRITERIA)
    except ArtifactRejected as exc:
        problems = str(exc)
    assert problems is not None
    assert "canonical artist" in problems
    assert "median degree" in problems


def test_healthy_graph_passes():
    check_acceptance(_graph(*_healthy()), CRITERIA)


def test_a_nameless_artist_is_rejected():
    """The F8 defect: 33 of these are in the adopted 75k artifact.

    A nameless artist is unsearchable, cannot resolve a clip, and can only
    ever surface as a blank interior card — see `acceptance.py`. The check
    takes no criterion, so it fires against the scaled-down set too.
    """
    names, degrees, pop = _healthy()
    names[5] = ""
    with pytest.raises(ArtifactRejected, match="carry no name"):
        check_acceptance(_graph(names, degrees, pop), CRITERIA)


def test_a_whitespace_only_name_is_rejected():
    """`.strip()`, not falsiness: " " is as unusable as "" and less visible."""
    names, degrees, pop = _healthy()
    names[5] = "   "
    with pytest.raises(ArtifactRejected, match="carry no name"):
        check_acceptance(_graph(names, degrees, pop), CRITERIA)


def test_the_nameless_check_names_the_mbid_not_the_name():
    """A blank name cannot identify itself in an error message.

    Every other violation can quote the artist's name; this one structurally
    cannot, so it must quote the mbid or be undiagnosable.
    """
    names, degrees, pop = _healthy()
    names[5] = ""
    with pytest.raises(ArtifactRejected) as excinfo:
        check_acceptance(_graph(names, degrees, pop), CRITERIA)
    assert f"{5:036d}" in str(excinfo.value)
