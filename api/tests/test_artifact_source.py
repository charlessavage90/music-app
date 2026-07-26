import hashlib

import pytest

from artistpath_api.artifact_source import load_graph, parse_s3_uri
from tests.test_graph_store import _good


def test_parses_an_s3_uri_into_bucket_and_key():
    assert parse_s3_uri("s3://my-bucket/graphs/g.bin") == ("my-bucket", "graphs/g.bin")


def test_rejects_a_non_s3_uri():
    with pytest.raises(ValueError, match="not an s3"):
        parse_s3_uri("/local/path.bin")


def test_loads_through_an_injected_reader():
    payload = _good()
    store = load_graph("s3://b/k.bin", reader=lambda uri: payload)
    assert store.artist_count == 2


def test_accepts_a_matching_checksum_and_records_it():
    payload = _good()
    digest = hashlib.sha256(payload).hexdigest()
    store = load_graph("s3://b/k.bin", expected_sha256=digest, reader=lambda uri: payload)
    assert store.source_sha256 == digest


def test_refuses_to_load_on_a_checksum_mismatch():
    payload = _good()
    with pytest.raises(ValueError, match="checksum mismatch"):
        load_graph("s3://b/k.bin", expected_sha256="0" * 64, reader=lambda uri: payload)


def test_empty_expected_checksum_skips_verification():
    payload = _good()
    store = load_graph("s3://b/k.bin", expected_sha256="", reader=lambda uri: payload)
    assert store.artist_count == 2
