"""TAS-6's selection half and the RED instrument check.

RUN EARLY, DELIBERATELY. The plan puts both in Task 7, after TAS-5. They are
brought forward because the red check is what makes TAS-4 believable at all,
and carrying an unverified gate result through two more tasks is the risk the
deferral was written to prevent. The ROUTING halves of both stay in Task 7 --
they need tas_route.py, which does not exist yet.
"""

from __future__ import annotations

import numpy as np

from tas_guard import (
    famous_to_obscure,
    is_adverse,
    permuted_labels_among_labelled,
    randomised_labels,
)
from tas_select import mask_tag
from tas_signal import LOWER_HALF, TOP_1PCT
from td_turnover import mask_multiplicative, uniform_field

# The capture builder is imported rather than copied so the two test modules
# cannot disagree about what a capture looks like.
from test_tas_select import _write_capture  # noqa: E402


def test_randomised_labels_preserve_the_labelled_share():
    original = {"a": {"rock"}, "b": set(), "c": {"jazz", "pop"}}
    shuffled = randomised_labels(original, seed=1)
    assert sum(1 for v in shuffled.values() if v) == 2
    assert set(shuffled) == set(original)


def test_randomised_labels_actually_move_assignments():
    # The share test above passes for a shuffle that returned the identity, so
    # the property that matters is pinned separately: the red check is worthless
    # if the "randomised" frame is the real one.
    original = {f"m{i:03d}": {f"g{i}"} for i in range(200)}
    shuffled = randomised_labels(original, seed=7)
    moved = sum(1 for k in original if shuffled[k] != original[k])
    assert moved > 150


def test_randomised_labels_are_deterministic_under_a_seed():
    original = {f"m{i:03d}": {f"g{i}"} for i in range(50)}
    assert randomised_labels(original, seed=3) == randomised_labels(original, seed=3)


def test_adverse_at_ten_percent_reduction():
    assert is_adverse(baseline=100, arm=90) is True
    assert is_adverse(baseline=100, arm=91) is False
    assert is_adverse(baseline=0, arm=0) is False


def test_adverse_is_one_directional():
    # TAS-6 is a GUARD, never a success signal. Growth is not "good news" it
    # can report -- it is simply not adverse.
    assert is_adverse(baseline=100, arm=150) is False


def test_famous_to_obscure_needs_one_end_famous_and_one_end_obscure():
    # The spec names the quantity but not its boundary. Fixed here as the
    # literal reading, reusing the bands TAS-1 already uses: one end in the top
    # 1%, the other in the lower half. The broader `fo` class of tas_select is
    # "everything spanning", which includes two mid-tier artists and would
    # overstate famous->obscure supply.
    pctl = np.array([0.995, 0.20, 0.70, 0.996], dtype=np.float64)
    n = 4
    assert TOP_1PCT == 0.99 and LOWER_HALF == 0.50  # boundaries come from tas_signal
    assert famous_to_obscure(np.array([0 * n + 1], dtype=np.int64), pctl, n) == 1  # famous+obscure
    assert famous_to_obscure(np.array([0 * n + 2], dtype=np.int64), pctl, n) == 0  # famous+mid
    assert famous_to_obscure(np.array([1 * n + 2], dtype=np.int64), pctl, n) == 0  # obscure+mid
    assert famous_to_obscure(np.array([0 * n + 3], dtype=np.int64), pctl, n) == 0  # famous+famous


def test_famous_to_obscure_skips_nodes_missing_from_the_frame():
    pctl = np.array([np.nan, 0.20], dtype=np.float64)
    assert famous_to_obscure(np.array([0 * 2 + 1], dtype=np.int64), pctl, 2) == 0


# --------------------------------------------------------------- TAS-AM3a
def test_am3a_the_new_ranking_path_is_bit_identical_to_the_verified_one(tmp_path):
    # TAS-AM3a. The replacement for the withdrawn red check: prove the device
    # can register a large change by giving it one whose answer is already
    # committed. Bit-identity is the strong form -- it says the new code path
    # IS td_turnover's verified one, not merely that it resembles it.
    cap = _write_capture(tmp_path, n_candidates=60)
    for lam in (0.25, 2.0):
        field = uniform_field(cap.s_node, cap.s_cand, cap.n, 303, True)
        assert np.array_equal(
            mask_tag(cap, field, lam), mask_multiplicative(cap, lam, 303, True)
        ), f"ranking path diverged from td_turnover at lambda={lam}"


# --------------------------------------------------------------- TAS-AM3b
def test_am3b_permutation_holds_the_labelled_SET_fixed_not_just_its_size():
    # This is the one knob the naive shuffle got wrong. Moving label sets among
    # ALL artists preserves the labelled COUNT but changes WHICH artists are
    # labelled, which halved the pairs where the rule acts -- a second knob.
    original = {"a": {"rock"}, "b": set(), "c": {"jazz"}, "d": set(), "e": {"pop"}}
    permuted = permuted_labels_among_labelled(original, seed=5)
    assert {k for k, v in permuted.items() if v} == {"a", "c", "e"}
    assert all(permuted[k] == set() for k in ("b", "d"))


def test_am3b_permutation_moves_which_labels_an_artist_holds():
    original = {f"m{i:03d}": ({f"g{i}"} if i % 2 else set()) for i in range(200)}
    permuted = permuted_labels_among_labelled(original, seed=11)
    labelled = [k for k, v in original.items() if v]
    moved = sum(1 for k in labelled if permuted[k] != original[k])
    assert moved > len(labelled) * 0.7


def test_am3b_permutation_is_deterministic_under_a_seed():
    original = {f"m{i:03d}": ({f"g{i}"} if i % 3 else set()) for i in range(60)}
    assert (permuted_labels_among_labelled(original, seed=2)
            == permuted_labels_among_labelled(original, seed=2))
