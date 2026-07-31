"""Pins the REL- device, and above all the DORMANT TERM.

The validity filter is inert in F0 and active in every arm, so the baseline
cannot reveal a bad choice of filter and every arm can. It is fixed in the
pre-registration before any run; these tests are what stop it moving
afterwards. Same job test_tas_common.py does for TAS-'s neutral rule.

Run from `builder/`:
    UV_LINK_MODE=copy uv run --extra dev pytest -q \
        analysis/2026-07-31-release-tag-coverage/
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rel_common import (  # noqa: E402
    EXCLUDED_PRIMARY,
    EXCLUDED_SECONDARY,
    aggregate,
    discogs_is_attributable,
    jaccard,
    labels_from,
    rg_artist_id,
    rg_is_attributable,
)

SOLO = [{"artist": {"id": "aaa"}}]
DUO = [{"artist": {"id": "aaa"}}, {"artist": {"id": "bbb"}}]


def rg(**kwargs) -> dict:
    base = {"artist-credit": SOLO, "primary-type": "Album", "secondary-types": []}
    base.update(kwargs)
    return base


# --------------------------------------------------------------- the filter


def test_a_solo_studio_album_is_attributable():
    assert rg_is_attributable(rg()) is True


def test_a_collaboration_is_not_attributable():
    """The other party's genres would be attributed to this artist."""
    assert rg_is_attributable(rg(**{"artist-credit": DUO})) is False


def test_a_compilation_is_not_attributable():
    """A compilation carries a curator's genres, not the artist's."""
    assert rg_is_attributable(rg(**{"secondary-types": ["Compilation"]})) is False


def test_a_broadcast_is_not_attributable():
    assert rg_is_attributable(rg(**{"primary-type": "Broadcast"})) is False


def test_every_excluded_secondary_type_actually_excludes():
    """The filter is only as good as its list; a typo would silently admit."""
    for excluded in EXCLUDED_SECONDARY:
        record = rg(**{"secondary-types": [excluded.title()]})
        assert rg_is_attributable(record) is False, excluded


def test_the_filter_is_case_insensitive_both_ways():
    assert rg_is_attributable(rg(**{"secondary-types": ["COMPILATION"]})) is False
    assert rg_is_attributable(rg(**{"primary-type": "broadcast"})) is False


def test_an_unlisted_secondary_type_does_not_exclude():
    """Soundtrack and Demo are deliberately NOT excluded -- they are the
    artist's own work. If that changes it is an amendment, not a tidy-up."""
    assert rg_is_attributable(rg(**{"secondary-types": ["Soundtrack"]})) is True
    assert rg_is_attributable(rg(**{"secondary-types": ["Demo"]})) is True


def test_the_excluded_sets_are_frozen_and_nonempty():
    assert isinstance(EXCLUDED_PRIMARY, frozenset) and EXCLUDED_PRIMARY
    assert isinstance(EXCLUDED_SECONDARY, frozenset) and EXCLUDED_SECONDARY


# ------------------------------------------------------------ discogs half


def test_discogs_various_artists_is_never_attributable():
    """Discogs id 194 is Various Artists -- a curator's genres."""
    assert discogs_is_attributable(["194"]) is False


def test_discogs_sole_credit_is_attributable():
    assert discogs_is_attributable(["5108415"]) is True


def test_discogs_multi_credit_is_not_attributable():
    assert discogs_is_attributable(["5108415", "1005346"]) is False


def test_discogs_empty_credit_is_not_attributable():
    assert discogs_is_attributable([]) is False


# ----------------------------------------------------------------- labels


def test_labels_are_normalised_and_deduplicated():
    record = {"genres": [{"name": "Hip-Hop"}, {"name": "hip hop"}, {"name": "Rock Music"}]}
    assert labels_from(record, "genres") == {"hip hop", "rock"}


def test_empty_normalised_labels_are_dropped():
    """norm_genre("-") is "", which would otherwise read as a genre shared by
    every artist carrying one -- a false agreement."""
    assert labels_from({"genres": [{"name": "-"}, {"name": "Jazz"}]}, "genres") == {"jazz"}


def test_a_missing_field_is_an_empty_set_not_an_error():
    assert labels_from({}, "genres") == set()


def test_rg_artist_id_is_none_when_not_sole_credit():
    assert rg_artist_id(rg()) == "aaa"
    assert rg_artist_id(rg(**{"artist-credit": DUO})) is None


# ------------------------------------------------------------- aggregation


def test_aggregate_is_the_union_over_releases():
    assert aggregate([{"jazz"}, {"funk", "jazz"}, set()]) == {"jazz", "funk"}


def test_aggregate_of_nothing_is_empty():
    assert aggregate([]) == set()


def test_minimum_support_is_one_release():
    """Fixed in the spec: the median unlabelled lower-half artist has 2
    release groups, so a >= 2 threshold would discard most of the target
    population by construction."""
    assert aggregate([{"funk"}]) == {"funk"}


# ---------------------------------------------------------------- jaccard


def test_jaccard_is_none_not_zero_when_a_side_is_empty():
    """None means "cannot be scored", never "disagrees". REL-3 counts the two
    separately; folding unscorables in as zeros would understate the device by
    exactly the amount its coverage falls short."""
    assert jaccard(set(), {"jazz"}) is None
    assert jaccard({"jazz"}, set()) is None


def test_jaccard_values():
    assert jaccard({"jazz"}, {"jazz"}) == 1.0
    assert jaccard({"jazz"}, {"rock"}) == 0.0
    assert jaccard({"jazz", "funk"}, {"jazz"}) == 0.5
