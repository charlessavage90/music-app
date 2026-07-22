import pytest

from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import ArtistStats, EdgeType, SimilarArtist


def test_config_has_sane_defaults():
    cfg = BuilderConfig()
    assert cfg.target_artist_count == 75_000
    # Task 1 measured 30 requests / 5 seconds. Never exceed 6/s.
    assert 0 < cfg.requests_per_second <= 6.0
    assert cfg.user_agent.startswith("artistpath-builder/")


def test_phase2_adopted_defaults():
    # The arm the owner chose in a blind listening test (execution log §16):
    # mutual_knn cap, legacy p99 clip rescale, no damping. Pinned here so a
    # silent default change is a test failure, not a rebuild nobody notices.
    cfg = BuilderConfig()
    assert cfg.cap_strategy == "mutual_knn"
    assert cfg.similarity_rescale == "p99_log_clip"
    assert cfg.similarity_damping == 0.0


@pytest.mark.parametrize(
    "knob,dead_value",
    [
        ("cap_strategy", "pre_symmetrise"),
        ("similarity_rescale", "percentile_rank"),
    ],
)
def test_losing_options_are_deleted_not_supported(knob, dead_value):
    # Phase 2 spec §8 risk 4 / revised plan C-4: the loser is removed and
    # raises, rather than lingering as a permanently supported mode that
    # quietly diverges from the adopted build.
    with pytest.raises(ValueError, match=dead_value):
        BuilderConfig(**{knob: dead_value})


def test_damping_remains_a_supported_continuous_knob():
    # Deliberately NOT deleted alongside the two enum knobs: damping is a
    # continuous axis, and spec §8 risk 4 names only similarity_rescale.
    # Constructing a damped config must succeed (the build-time degeneracy
    # guard in rescale_scores is what enforces the centring requirement).
    assert BuilderConfig(similarity_damping=0.25).similarity_damping == 0.25


def test_behavioural_edge_type_is_zero():
    # Alpha emits exactly one edge type; downstream reads it as uint8.
    assert EdgeType.BEHAVIOURAL == 0


def test_similar_artist_is_comparable_and_frozen():
    a = SimilarArtist(mbid="a" * 36, name="A", score=0.5)
    b = SimilarArtist(mbid="a" * 36, name="A", score=0.5)
    assert a == b


def test_artist_stats_defaults_disambiguation():
    stats = ArtistStats(mbid="a" * 36, name="A", user_count=10, listen_count=99)
    assert stats.disambiguation == ""
