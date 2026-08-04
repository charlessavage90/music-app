from gbl_pairs import rank_familiarity, resolve_in


class FakeStore:
    names = ["Radiohead", "Sigur Rós", "Boards of Canada", "Radiohead"]
    mbids = ["m0", "m1", "m2", "m3"]


def test_rank_familiarity_aggregates_and_filters_skips():
    history = [
        {"artistName": "Songs: Ohia", "msPlayed": 442_106},
        {"artistName": "Songs: Ohia", "msPlayed": 366_826},
        {"artistName": "Songs: Ohia", "msPlayed": 4_249},      # skip: not a play
        {"artistName": "Destroyer", "msPlayed": 16_035},        # skip: not a play
        {"artistName": "The Beta Band", "msPlayed": 200_000},
    ]
    library = {"tracks": [{"artist": "Destroyer", "album": "x", "track": "y", "uri": "u"}]}
    rows = rank_familiarity(history, library)
    by_name = {r["name"]: r for r in rows}
    assert by_name["Songs: Ohia"]["plays"] == 2
    assert by_name["Songs: Ohia"]["ms_played"] == 442_106 + 366_826 + 4_249
    assert rows[0]["name"] == "Songs: Ohia"          # sorted by ms_played desc
    assert by_name["Destroyer"]["in_library"] is True
    assert by_name["Destroyer"]["plays"] == 0        # library alone is not a play
    assert by_name["The Beta Band"]["in_library"] is False


def test_resolve_in_is_accent_insensitive_and_returns_all_matches():
    s = FakeStore()
    assert resolve_in(s, "sigur ros") == [1]
    assert resolve_in(s, "Radiohead") == [0, 3]   # ambiguity stays visible
    assert resolve_in(s, "Nobody") == []
