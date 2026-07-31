"""Tests for the TAS agreement device.

These pin the ONE dormant term of the pre-registration (spec section 0): the
neutral value for unlabelled pairs is inert at lambda = 0 and active in every
arm, so it is fixed by test rather than by discipline. A change to any
expectation here is a change to a committed pre-registration and needs a
section 8 amendment.
"""

from __future__ import annotations

from tas_common import (
    GLOBAL_NEUTRAL_FALLBACK,
    agreement,
    neutral_for,
    resolved_agreement,
)


def test_agreement_is_jaccard():
    assert agreement({"rock", "pop"}, {"rock"}) == 0.5
    assert agreement({"rock"}, {"rock"}) == 1.0
    assert agreement({"rock"}, {"jazz"}) == 0.0


def test_agreement_is_none_when_either_side_unlabelled():
    # Spec section 1: missing labels are NOT a claim of dissimilarity. None
    # means "unknown"; only resolved_agreement turns it into a number.
    assert agreement(set(), {"rock"}) is None
    assert agreement({"rock"}, set()) is None
    assert agreement(set(), set()) is None


def test_neutral_is_the_median_agreement_against_the_ARTIST_not_each_other():
    # The neutral value is the median agreement between the artist and its
    # own labelled candidates -- not between candidates. Agreements against
    # {"rock"} are 1.0, 0.5, 0.0, so the median is 0.5.
    own = {"rock"}
    candidates = [{"rock"}, {"rock", "pop"}, {"jazz"}]
    assert neutral_for(own, candidates) == 0.5


def test_neutral_ignores_unlabelled_candidates():
    # An unlabelled candidate carries no information and must not drag the
    # neutral value toward any particular number.
    own = {"rock"}
    assert neutral_for(own, [{"rock"}, set(), {"jazz"}, set()]) == 0.5


def test_neutral_falls_back_globally_below_two_labelled_candidates():
    assert neutral_for({"rock"}, []) == GLOBAL_NEUTRAL_FALLBACK
    assert neutral_for({"rock"}, [{"rock"}]) == GLOBAL_NEUTRAL_FALLBACK
    # An artist with no labels of its own can form no median at all.
    assert neutral_for(set(), [{"rock"}, {"jazz"}]) == GLOBAL_NEUTRAL_FALLBACK


def test_the_fallback_is_not_zero():
    # Zero is a positive claim of dissimilarity. Applying it to missing data
    # would demote unlabelled candidates, which are disproportionately the
    # obscure ones -- pushing DD-F1 the wrong way. This is the hazard TAS-6
    # guards, and the fallback is the first line of defence.
    assert GLOBAL_NEUTRAL_FALLBACK > 0.0


def test_unlabelled_pair_resolves_to_neutral_never_zero():
    assert resolved_agreement(set(), {"rock"}, neutral=0.42) == 0.42
    assert resolved_agreement({"rock"}, set(), neutral=0.42) == 0.42
    assert resolved_agreement({"rock"}, {"rock"}, neutral=0.42) == 1.0


def test_a_labelled_mismatch_is_zero_and_is_NOT_the_neutral_value():
    # The device must distinguish "we know these share nothing" from "we do
    # not know". Collapsing them is exactly the error the neutral rule exists
    # to prevent, and it would be invisible at lambda = 0.
    assert resolved_agreement({"rock"}, {"jazz"}, neutral=0.42) == 0.0
