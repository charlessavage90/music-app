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


def test_matches_real_archive_disambiguation_variants():
    # Measured against the 7 canonical special-purpose entities in the 75k
    # archive: casing varies, and [unknown] uses an en dash (U+2013) where
    # the others use an ASCII hyphen after "Artist". The matcher keys only
    # on the phrase "special purpose", so neither varies the result.
    real_variants = (
        "Special Purpose Artist - Do not add releases here, if possible.",
        "special purpose artist",
        "Special Purpose Artist",
        "Special Purpose Artist – Do not add releases here, if possible.",
    )
    for disambiguation in real_variants:
        assert is_special_purpose(disambiguation)
