from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch, normalise
from tests.conftest import make_store

CFG = ApiConfig()


def _search(names, popularity):
    store = make_store(names, popularity, undirected_edges=[])
    return ArtistSearch(store, CFG)


def test_normalise_lowercases_and_strips_accents():
    assert normalise("Sigur Rós") == "sigur ros"
    assert normalise("BEYONCÉ") == "beyonce"


def test_prefix_match_returns_the_artist():
    s = _search(["Radiohead", "Radio Dept", "Coldplay"], [0.9, 0.4, 0.8])
    ids = s.search("radio")
    assert set(ids) == {0, 1}


def test_results_are_ranked_by_popularity():
    s = _search(["Radiohead", "Radio Dept"], [0.4, 0.9])
    assert s.search("radio") == [1, 0]  # Radio Dept more popular here


def test_accent_insensitive_match():
    s = _search(["Sigur Rós", "Other"], [0.9, 0.1])
    assert s.search("sigur ros") == [0]


def test_substring_match_when_no_prefix_hit():
    s = _search(["The Beatles", "Beach House"], [0.9, 0.5])
    assert 0 in s.search("beatles")


def test_limit_is_respected():
    names = [f"Band {i}" for i in range(50)]
    s = _search(names, [0.5] * 50)
    assert len(s.search("band")) == CFG.search_limit


def test_empty_query_returns_nothing():
    s = _search(["Radiohead"], [0.9])
    assert s.search("  ") == []
