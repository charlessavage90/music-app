import json
from pathlib import Path

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import (
    CANDIDATE_ALGORITHM,
    PRODUCTION_ALGORITHM,
    BuilderConfig,
)
from artistpath_builder.frontier import reconstruct_referenced, rewrite_checkpoint
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C, D = ("a" * 36, "b" * 36, "c" * 36, "d" * 36)


def _similar(*mbids: str) -> bytes:
    rows = [
        {"artist_mbid": m, "name": m[0].upper(), "score": 100 - i}
        for i, m in enumerate(mbids)
    ]
    return json.dumps(rows).encode()


@pytest.fixture
def config():
    return BuilderConfig(algorithm=CANDIDATE_ALGORITHM)


def _archive(tmp_path, config, entries):
    archive = LocalArchive(tmp_path / "archive")
    prefix = f"similar/listenbrainz/{config.algorithm}/"
    for mbid, payload in entries.items():
        archive.put(f"{prefix}{mbid}.json", payload)
    return archive


def test_referenced_is_the_union_of_every_neighbour(tmp_path, config):
    archive = _archive(tmp_path, config, {A: _similar(B, C), B: _similar(C, D)})
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {
        B,
        C,
        D,
    }


def test_other_algorithms_subtree_is_ignored(tmp_path, config):
    # CEXR-7a: a naive archive.keys() walk ingests another algorithm's data.
    archive = _archive(tmp_path, config, {A: _similar(B)})
    archive.put("similar/listenbrainz/some_other_algorithm/xx.json", _similar(D))
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {B}


def test_fame_keys_are_ignored(tmp_path, config):
    # CEXR-7a: fame records live in the same archive under fame/.
    #
    # The payload is deliberately SIMILARITY-shaped rather than a real fame
    # record. A real one ({"total_user_count": ...}) parses to [] whatever the
    # walk does, so it cannot tell a scoped walk from a naive one and the test
    # would pass with no prefix guard at all — verified by mutation before this
    # was changed. Shaped like similarity, only the prefix guard keeps D out.
    archive = _archive(tmp_path, config, {A: _similar(B)})
    archive.put(f"fame/{C}.json", _similar(D))
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {B}


def test_unparseable_payload_is_skipped_not_fatal(tmp_path, config):
    archive = _archive(tmp_path, config, {A: _similar(B), C: b"{not json"})
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {B}


def _checkpoint(tmp_path, algorithm, done, discovered) -> Path:
    path = tmp_path / "checkpoint.json"
    path.write_text(
        json.dumps(
            {
                "algorithm": algorithm,
                "done": sorted(done),
                "discovered": sorted(discovered),
            },
            sort_keys=True,
        )
    )
    return path


def test_rewrite_unions_and_preserves_done_as_a_subset(tmp_path, config):
    # A crawled artist nobody names must survive the rewrite.
    path = _checkpoint(tmp_path, config.algorithm, done={A, D}, discovered={A, D})
    stats = rewrite_checkpoint(path, config, referenced={A, B, C})
    state = json.loads(path.read_text())
    assert set(state["done"]) <= set(state["discovered"])
    assert D in set(state["discovered"])
    assert stats == {"done": 2, "discovered": 4, "frontier": 2}


def test_rewrite_is_idempotent(tmp_path, config):
    path = _checkpoint(tmp_path, config.algorithm, done={A}, discovered={A})
    first = rewrite_checkpoint(path, config, referenced={A, B})
    after_first = path.read_text()
    second = rewrite_checkpoint(path, config, referenced={A, B})
    assert first == second
    assert path.read_text() == after_first


def test_rewrite_refuses_a_checkpoint_from_another_algorithm(tmp_path, config):
    path = _checkpoint(tmp_path, PRODUCTION_ALGORITHM, done={A}, discovered={A})
    with pytest.raises(ValueError, match="refusing"):
        rewrite_checkpoint(path, config, referenced={B})


def test_rewrite_backs_up_the_original_first(tmp_path, config):
    path = _checkpoint(tmp_path, config.algorithm, done={A}, discovered={A})
    original = path.read_text()
    rewrite_checkpoint(path, config, referenced={A, B})
    assert (tmp_path / "checkpoint.json.bak").read_text() == original
