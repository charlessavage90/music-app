"""The ruler and pair set -- the properties that must not drift.

Governing document: docs/superpowers/specs/2026-08-03-cap-reevaluation-preregistration.md
Operational document: docs/superpowers/plans/2026-08-03-cap-reeval-execution-plan.md (CRE-T1)
"""
from __future__ import annotations

import numpy as np
import pytest

from cre_common import FRAME_N, Ruler, famous_pairs, use_frozen

# The toy-frame test imports fi_stats directly, so the frozen fame directory must
# be on sys.path regardless of which test runs first (the Ruler fixture would
# otherwise be the only thing putting it there).
use_frozen("fame")


@pytest.fixture(scope="module")
def ruler() -> Ruler:
    """Constructed once -- it loads the snapshot and the adopted artifact."""
    return Ruler()


def test_frame_n_is_the_prereg_frame(ruler):
    # CRE-G1c. 74,151 is the adopted artifact's non-null fame_lb_raw count
    # (fi_validation.json FAM-1.adopted_population.non_null) -- NOT the
    # artifact's 74,193 nodes and NOT the snapshot's 93,067 keys.
    assert ruler.frame_n == FRAME_N == 74_151


def test_midrank_formula_on_a_toy_frame():
    # pctl(v) = (|{f<v}| + (|{f=v}|+1)/2) / N over [1,1,2,5]:
    #   pctl(1) = (0 + 1.5)/4, pctl(2) = (2 + 1)/4, pctl(5) = (3 + 1)/4
    from fi_stats import Frame
    f = Frame(np.array([1, 1, 2, 5], dtype=np.int64))
    got = f.pctl(np.array([1, 2, 5, 3, 999]))
    assert got[0] == pytest.approx(1.5 / 4)
    assert got[1] == pytest.approx(3.0 / 4)
    assert got[2] == pytest.approx(4.0 / 4)
    # absent value 3: (|{f<3}| + 0.5)/4
    assert got[3] == pytest.approx(3.5 / 4)
    # FAM-AM1.6: above the frame maximum takes the maximum's percentile.
    assert got[4] == got[2]


def test_null_price_sits_below_every_measured_value(ruler):
    # Plan pin 2, present-but-null class: priced at frame.pctl(0). Asserted
    # against the frame minimum DIRECTLY (analyst m10: a loose absolute bound
    # let the name claim more than the assertion checked).
    assert ruler.device_null_pctl < ruler.min_measured_pctl


def test_absent_class_is_priced_at_the_neutral_prior(ruler):
    # Plan pin 2, absent-from-snapshot class: never fetched, obscurity unknown,
    # priced at 0.5 so the device neither seeks nor avoids it.
    assert ruler.device_absent_pctl == 0.5
    assert ruler.status_of("00000000-0000-0000-0000-000000000000") == "absent"


def test_famous_pairs_are_the_22_committed_ones():
    pairs = famous_pairs()
    assert len(pairs) == 22
    assert {p[0] for p in pairs} == {"ff-top01pct", "ff-top1pct"}
    assert all(a != b for _, a, b in pairs)
