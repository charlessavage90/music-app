import json

from artistpath_builder.popularity import (
    aggregate_listeners,
    iter_listen_artists,
    read_popularity,
    write_popularity,
)

A, B = ("a" * 36, "b" * 36)


def _listen(user: str, mbids: list[str]) -> str:
    return json.dumps(
        {
            "user_name": user,
            "track_metadata": {"mbid_mapping": {"artist_mbids": mbids}},
        }
    )


def test_extracts_artist_and_user():
    assert list(iter_listen_artists([_listen("alice", [A])])) == [(A, "alice")]


def test_a_listen_crediting_several_artists_yields_each():
    pairs = list(iter_listen_artists([_listen("alice", [A, B])]))
    assert sorted(pairs) == [(A, "alice"), (B, "alice")]


def test_duplicate_artist_within_one_listen_is_collapsed():
    assert list(iter_listen_artists([_listen("alice", [A, A])])) == [(A, "alice")]


def test_unmapped_listens_are_skipped():
    line = json.dumps({"user_name": "alice", "track_metadata": {}})
    assert list(iter_listen_artists([line])) == []


def test_malformed_lines_are_skipped_not_raised():
    # A 191GB dump will contain some. Losing a row beats aborting the run.
    lines = ["not json", "", _listen("alice", [A]), "{]"]
    assert list(iter_listen_artists(lines)) == [(A, "alice")]


def test_bytes_lines_are_accepted():
    assert list(iter_listen_artists([_listen("alice", [A]).encode()])) == [(A, "alice")]


def test_counts_distinct_listeners_not_plays():
    # Spec 4.1: one obsessive listener must not outweigh many casual ones.
    pairs = [(A, "alice")] * 500 + [(B, "bob"), (B, "carol")]
    assert aggregate_listeners(pairs) == {A: 1, B: 2}


def test_aggregate_of_nothing_is_empty():
    assert aggregate_listeners([]) == {}


def test_popularity_table_round_trips(tmp_path):
    path = tmp_path / "popularity.json"
    write_popularity({B: 2, A: 1}, path)
    assert read_popularity(path) == {A: 1, B: 2}


def test_popularity_table_is_written_deterministically(tmp_path):
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    write_popularity({B: 2, A: 1}, first)
    write_popularity({A: 1, B: 2}, second)
    assert first.read_bytes() == second.read_bytes()
