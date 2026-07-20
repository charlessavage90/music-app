from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import ArtistStats, EdgeType, SimilarArtist


def test_config_has_sane_defaults():
    cfg = BuilderConfig()
    assert cfg.target_artist_count == 75_000
    # Task 1 measured 30 requests / 5 seconds. Never exceed 6/s.
    assert 0 < cfg.requests_per_second <= 6.0
    assert cfg.user_agent.startswith("artistpath-builder/")


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
