"""Tests for TAS-1 / TAS-2 / TAS-3 helpers.

The class boundaries below are not arbitrary: they land exactly on the BANDS
definitions imported from cb_metrics ("top 1%" starts at 0.99, "lower half"
is 0.0-0.50), so TAS-1's classes are comparable with COH-2's bands rather
than a private invention.
"""

from __future__ import annotations

import pytest

from tas_signal import edge_class, iqr, spearman


def test_edge_class_by_fame_percentile():
    assert edge_class(0.995, 0.996) == "ff"   # both top 1%
    assert edge_class(0.995, 0.30) == "fo"    # famous x lower half
    assert edge_class(0.20, 0.30) == "oo"     # both lower half


def test_edge_class_boundaries_match_the_imported_BANDS():
    # 0.99 is the bottom of "top 1%"; 0.50 the top of "lower half".
    assert edge_class(0.99, 0.99) == "ff"
    assert edge_class(0.9899, 0.9899) == "fo"  # neither famous nor both-lower
    assert edge_class(0.4999, 0.4999) == "oo"
    assert edge_class(0.50, 0.50) == "fo"      # upper half is neither


def test_iqr_of_flat_signal_is_zero():
    assert iqr([0.4, 0.4, 0.4, 0.4]) == 0.0


def test_iqr_detects_spread():
    assert iqr([0.0, 0.2, 0.4, 0.6, 0.8]) > 0.10


def test_iqr_needs_four_points():
    # Fewer than four cannot form quartiles; returning 0.0 would read as
    # "flat" and push toward a kill on no evidence, so it must be excluded
    # by the caller rather than silently scored.
    assert iqr([0.1, 0.9]) is None
    assert iqr([0.1, 0.5, 0.9]) is None


def test_spearman_is_one_for_a_monotone_relationship():
    # THE failure mode TAS-3 exists to name: if agreement rises with
    # strength, then strength * (1 + lambda*agreement) preserves the order
    # strength alone gave, and lambda is inert at EVERY value.
    pairs = [(0.1, 0.2), (0.2, 0.3), (0.3, 0.7), (0.4, 0.9)]
    assert spearman(pairs) == pytest.approx(1.0)


def test_spearman_is_minus_one_when_reversed():
    pairs = [(0.1, 0.9), (0.2, 0.7), (0.3, 0.3), (0.4, 0.2)]
    assert spearman(pairs) == pytest.approx(-1.0)


def test_spearman_near_zero_when_unrelated():
    pairs = [(0.1, 0.5), (0.2, 0.1), (0.3, 0.9), (0.4, 0.3)]
    assert abs(spearman(pairs)) < 0.9
