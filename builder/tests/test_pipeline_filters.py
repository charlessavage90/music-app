from artistpath_builder.pipeline import is_special_purpose


def test_flags_musicbrainz_special_purpose_artists():
    assert is_special_purpose("Special Purpose Artist - Do not add releases here")
    assert is_special_purpose("special purpose artist")
    assert is_special_purpose("SPECIAL PURPOSE")


def test_does_not_flag_real_bands_with_bracketed_names():
    # 22 nodes have bracketed names; 15 are real bands. A name-based filter
    # would delete all of them, which is why this matches on disambiguation.
    for disambiguation in (
        "",
        "Swedish indiepopband",
        "Shadows in the Dark",
        "ex-[Champagne]",
        "UK drum & bass producers Andy C & Ant Miles",
    ):
        assert not is_special_purpose(disambiguation)


def test_handles_none_and_empty():
    assert not is_special_purpose("")
    assert not is_special_purpose(None)
