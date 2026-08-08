import json
import os

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import (
    Crawler,
    FrontierExhausted,
    TransientFetchError,
)
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


def test_target_caps_fetches_and_the_frontier_is_still_recorded(tmp_path, config):
    # CEX-2: target_artist_count bounds artists FETCHED, not artists
    # discovered. The old bound discarded neighbours at the target, which is
    # ULC-F3: the frontier was never recorded, so a resume rebuilt an empty
    # queue and exited 0 processed while reading as success.
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=2
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([A])

    assert len(crawler._done) == 2
    assert len(crawler.discovered) > len(crawler._done)
    assert crawler.discovered >= crawler._done


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


class _CrashAfter:
    """Wraps a fetcher and raises a non-transient error after n calls, to
    simulate a process crash or a network/system failure mid-crawl."""

    def __init__(self, inner, n):
        self.inner = inner
        self.n = n
        self.calls = 0

    def __call__(self, url):
        self.calls += 1
        if self.calls > self.n:
            raise RuntimeError("simulated crash / network drop")
        return self.inner(url)


def test_resume_continues_pending_frontier_after_crash(tmp_path, config):
    # A crash mid-crawl leaves artists discovered but unprocessed. The
    # checkpoint stores the discovered/done sets, not the queue, so resume
    # must rebuild the frontier from their difference — otherwise it restarts
    # with an empty queue and silently finishes a half-graph.
    crasher = _CrashAfter(FakeFetcher(), n=2)
    first = _crawler(tmp_path, config, crasher)
    with pytest.raises(RuntimeError):
        first.crawl([A])
    # Partial progress: some processed, more discovered than done.
    assert first._done < first.discovered
    assert len(first._done) < 4

    # Resume: same archive and checkpoint, healthy fetcher.
    resumed = _crawler(tmp_path, config, FakeFetcher())
    resumed.crawl([A])
    assert resumed.discovered == {A, B, C, D}
    assert {A, B, C, D}.issubset(resumed._done)


ALG_B = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)


def test_production_algorithm_keeps_the_flat_archive_key(tmp_path, config):
    # 75,000 existing responses live at this layout and are not moved.
    crawler = _crawler(tmp_path, config, FakeFetcher())
    assert crawler.similar_key(A) == f"similar/listenbrainz/{A}.json"


def test_nondefault_algorithm_gets_its_own_archive_subtree(tmp_path):
    # RC-H3: the key did not encode the algorithm, so ALG-B responses stored
    # beside production ones would be served to every future build as if they
    # were production data.
    cfg = BuilderConfig(requests_per_second=1000.0, algorithm=ALG_B)
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    assert crawler.similar_key(A) == f"similar/listenbrainz/{ALG_B}/{A}.json"


def test_checkpoint_refuses_to_resume_under_a_different_algorithm(tmp_path, config):
    # Same hazard on the other axis: a resumed crawl would treat the other
    # algorithm's finished artists as done and silently skip every one.
    _crawler(tmp_path, config, FakeFetcher()).crawl([A])
    algb = BuilderConfig(requests_per_second=1000.0, algorithm=ALG_B)
    with pytest.raises(ValueError, match="RC-H3"):
        _crawler(tmp_path, algb, FakeFetcher())


def test_legacy_checkpoint_without_algorithm_field_still_resumes(tmp_path, config):
    # Every checkpoint written before this change predates the field; a
    # missing field means the production algorithm, not a refusal.
    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [A], "discovered": [A, B]})
    )
    crawler = _crawler(tmp_path, config, FakeFetcher())
    assert crawler.discovered == {A, B}


def test_failed_artists_are_retried_on_a_fresh_run(tmp_path):
    # A server outage that exhausts retries must not permanently skip an
    # artist — a later run, after the server recovers, must retry it.
    cfg = BuilderConfig(requests_per_second=1000.0, max_retries=2, checkpoint_every=1)
    down = _crawler(tmp_path, cfg, FakeFetcher(fail_times=999))
    down.crawl([A])
    assert A in down.failures
    assert not down.archive.has(down.similar_key(A))
    assert A not in down._done  # not marked done, so it stays retryable

    recovered = _crawler(tmp_path, cfg, FakeFetcher())
    recovered.crawl([A])
    assert recovered.archive.has(recovered.similar_key(A))
    assert A in recovered._done


def test_raises_when_the_frontier_is_empty_but_more_was_asked_for(tmp_path):
    # The ULC-F3 signature: discovered == done, target above done.
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=99
    )
    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [A, B], "discovered": [A, B]})
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    with pytest.raises(FrontierExhausted, match="refrontier"):
        crawler.crawl([])


def test_does_not_raise_when_the_bootstrap_supplies_new_work(tmp_path):
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=99
    )
    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [A], "discovered": [A]})
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([C])
    assert C in crawler._done


def test_does_not_raise_when_the_graph_was_genuinely_exhausted(tmp_path):
    # CEXR-5: an idempotent re-run after a completed crawl must not be
    # mistaken for ULC-F3.
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=99
    )
    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [A, B], "discovered": [A, B], "exhausted": True})
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([])  # must not raise


def test_a_completed_crawl_records_that_it_exhausted_the_graph(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert json.loads((tmp_path / "checkpoint.json").read_text())["exhausted"] is True


def test_checkpoint_is_written_via_a_temp_file_then_renamed(tmp_path, config, monkeypatch):
    # A truncated checkpoint is the only unrecoverable failure in a 4-hour run.
    seen: list[str] = []
    real_replace = os.replace

    def spy(src, dst):
        seen.append(str(src))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])

    assert seen, "checkpoint was not written through os.replace"
    assert all(src.endswith(".tmp") for src in seen)
    assert json.loads((tmp_path / "checkpoint.json").read_text())["done"]
