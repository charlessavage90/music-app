import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler, TransientFetchError
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C, D = ("a" * 36, "b" * 36, "c" * 36, "d" * 36)


def _similar(*mbids: str) -> bytes:
    rows = [
        {"artist_mbid": m, "name": m[0].upper(), "score": 100 - i}
        for i, m in enumerate(mbids)
    ]
    return json.dumps(rows).encode()


def _stats(mbid: str, users: int = 10) -> bytes:
    return json.dumps(
        {
            "payload": {
                "artist_mbid": mbid,
                "artist_name": mbid[0].upper(),
                "total_user_count": users,
                "total_listen_count": users * 7,
            }
        }
    ).encode()


class FakeFetcher:
    """Serves a small similarity graph: A -> B -> C -> D."""

    NEIGHBOURS = {A: (B,), B: (A, C), C: (B, D), D: (C,)}

    def __init__(self, fail_times: int = 0):
        self.calls: list[str] = []
        self.fail_times = fail_times

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        if self.fail_times > 0:
            self.fail_times -= 1
            raise TransientFetchError("429 slow down")
        for mbid, neighbours in self.NEIGHBOURS.items():
            if mbid in url:
                return _similar(*neighbours)
        return b"[]"


@pytest.fixture
def config():
    return BuilderConfig(requests_per_second=1000.0, checkpoint_every=1)


def _crawler(tmp_path, config, fetcher, name="checkpoint.json"):
    return Crawler(
        config=config,
        archive=LocalArchive(tmp_path / "archive"),
        source=ListenBrainzSource(config),
        fetcher=fetcher,
        checkpoint_path=tmp_path / name,
    )


def test_crawl_archives_similarity(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert crawler.archive.has(crawler.similar_key(A))


def test_crawl_never_fetches_per_artist_stats(tmp_path, config):
    # The stats endpoint costs ~23s a call (findings 6a). Popularity comes
    # from the spark dump instead; reintroducing this call would take the
    # crawl from ~7 hours to ~3 weeks.
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert not any("/listeners" in url for url in crawler.fetcher.calls)


def test_responses_are_archived_verbatim(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert crawler.archive.get(crawler.similar_key(A)) == _similar(B)


def test_snowball_discovers_artists_beyond_the_bootstrap(tmp_path, config):
    # The whole point of the amendment: starting from A alone must reach D.
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert crawler.discovered == {A, B, C, D}


def test_discovery_stops_at_target_count(tmp_path, config):
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=2
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([A])
    assert len(crawler.discovered) == 2


def test_already_archived_artists_are_not_refetched(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    before = len(crawler.fetcher.calls)

    resumed = _crawler(tmp_path, config, FakeFetcher(), name="checkpoint2.json")
    resumed.crawl([A])
    assert resumed.fetcher.calls == []
    assert before > 0


def test_transient_failures_are_retried(tmp_path, config):
    fetcher = FakeFetcher(fail_times=2)
    crawler = _crawler(tmp_path, config, fetcher)
    crawler.crawl([A])
    assert crawler.archive.has(crawler.similar_key(A))


def test_exhausted_retries_records_failure_and_continues(tmp_path):
    cfg = BuilderConfig(requests_per_second=1000.0, max_retries=2, checkpoint_every=1)
    crawler = _crawler(tmp_path, cfg, FakeFetcher(fail_times=999))
    crawler.crawl([A])
    # A single bad artist must not abort an 8-hour crawl.
    assert A in crawler.failures
