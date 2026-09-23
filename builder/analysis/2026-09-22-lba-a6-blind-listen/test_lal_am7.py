"""`LBA-AM7`'s pure parts: the per-artist stats, the resolution rule, familiarity, and the pool."""
from types import SimpleNamespace

from lal_common import ROLES
from lal_pool_am7 import MIN_MS, artist_stats, familiar_mbids, name_index, resolve
from lal_prescreen_am7 import pool_from_known

INC, CHA = ROLES
norm = str.lower


def s(artist, track, ms=MIN_MS, ts="2020-01-01T00:00:00Z"):
    return {"master_metadata_album_artist_name": artist, "spotify_track_uri": track, "ms_played": ms, "ts": ts}


def test_breadth_ranks_above_volume_so_a_playlist_single_sinks():
    recs = [s("Single", "t1")] * 50 + [s("Broad", f"b{i}") for i in range(5)]
    out = artist_stats(recs)
    assert [a["name"] for a in out] == ["Broad", "Single"]
    assert out[1] == {"name": "Single", "distinct_tracks": 1, "plays": 50, "years": 1, "minutes": 25}


def test_streams_under_thirty_seconds_and_nameless_records_do_not_count():
    out = artist_stats([s("A", "t1", ms=MIN_MS - 1), s(None, "t2"), s("A", "t3", ts="2016-05-01")])
    assert out == [{"name": "A", "distinct_tracks": 1, "plays": 1, "years": 1, "minutes": 0}]


def store(names, mbids):
    return SimpleNamespace(names=names, mbids=mbids)


def stores_and_indexes(inc, cha):
    st = {INC: store(*inc), CHA: store(*cha)}
    return st, {r: name_index(st[r], norm) for r in ROLES}


def test_resolution_needs_one_node_in_each_map_with_the_same_mbid():
    st, ix = stores_and_indexes((["A", "B", "C", "C"], ["ma", "mb", "mc1", "mc2"]),
                                (["A", "B", "D"], ["ma", "mX", "md"]))
    stats = [{"name": n} for n in ("A", "B", "C", "D")]
    out = resolve(stats, st, ix, norm, excluded={})
    assert out[0]["mbid"] == "ma"
    assert out[1]["excluded"] == "different MBIDs in the two maps"
    assert out[2]["excluded"] == "not exactly one node in both maps"
    assert out[3]["excluded"] == "not exactly one node in both maps"


def test_presented_endpoints_stay_excluded():
    st, ix = stores_and_indexes((["A"], ["ma"]), (["A"], ["ma"]))
    assert resolve([{"name": "A"}], st, ix, norm, {"ma": "GBL-AM1"})[0]["excluded"].endswith("(GBL-AM1)")


def test_familiarity_takes_every_homonym_in_either_map():
    st, ix = stores_and_indexes((["C", "C"], ["c1", "c2"]), (["C", "E"], ["c3", "e"]))
    assert familiar_mbids([{"name": "C"}], st, ix, norm) == {"c1", "c2", "c3"}


def test_the_pool_keeps_order_and_rank_is_position():
    known = {"pool": [{"name": "A", "mbid": "a"}, {"name": "B", "mbid": "b"}, {"name": "C", "mbid": "c"}]}
    nodes = {INC: {"a", "b", "c"}, CHA: {"a", "c"}}
    out = pool_from_known(known, {}, nodes)
    assert [(r["rank"], r["name"], r.get("excluded")) for r in out] == [
        (1, "A", None), (2, "B", "not a node of both maps"), (3, "C", None)]
