import pytest

from artistpath_builder.archive import LocalArchive


def test_put_then_get_round_trips(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put("similar/abc.json", b'{"hello":"world"}')
    assert archive.get("similar/abc.json") == b'{"hello":"world"}'


def test_get_missing_key_returns_none(tmp_path):
    assert LocalArchive(tmp_path).get("nope.json") is None


def test_has_reports_presence(tmp_path):
    archive = LocalArchive(tmp_path)
    assert not archive.has("k.json")
    archive.put("k.json", b"x")
    assert archive.has("k.json")


def test_keys_lists_everything_written(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put("similar/b.json", b"1")
    archive.put("similar/a.json", b"2")
    assert sorted(archive.keys()) == ["similar/a.json", "similar/b.json"]


def test_payload_is_stored_byte_identical(tmp_path):
    # Archived bytes must never be reformatted. Replay determinism depends
    # on replaying exactly what the server sent.
    archive = LocalArchive(tmp_path)
    payload = b'{"b":2,  "a":1}\n\n'
    archive.put("raw.json", payload)
    assert archive.get("raw.json") == payload


def test_key_traversal_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        LocalArchive(tmp_path).put("../escape.json", b"x")
