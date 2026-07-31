"""TAS-4 selection simulation -- the properties that must not drift.

WHY THESE TESTS DO NOT MATCH THE PLAN'S DRAFT. The implementation plan wrote
these against `simulate_top_k(strengths, labels, lam, k, own) -> set[str]`, an
MBID-keyed function taking one artist's candidate dict. The real substrate is
`td_turnover.Capture`: int-id CSR arrays with selection expressed as a BOOLEAN
MASK over one flattened candidate array, and turnover computed by numpy set ops
on packed `u * n + v` edge keys. The plan's Step 5 predicted a keying mismatch;
it is a data-model mismatch. The PROPERTIES the plan pinned are all preserved
below -- lambda=0 exactness, a genre match promoted past a stronger mismatch,
and an unlabelled candidate not demoted -- rewritten against the real interface.

The captures used here are synthesised in tmp_path and loaded through the REAL
`Capture` class, so the ordering key under test is the one the run uses.
"""

from __future__ import annotations

import numpy as np
import pytest

from tas_common import neutral_for
from tas_select import agreement_field, classify_keys, edge_turnover, mask_tag
from tas_signal import edge_class
from td_turnover import K, Capture

SELF = "m00"


def _write_capture(tmp_path, n_candidates: int):
    """One binding node (0) with `n_candidates`, every other node inert.

    Strengths descend by 0.001 so a candidate just outside the top-50 sits one
    thousandth below the last one inside -- the margin a lambda arm must cross.
    """
    n = n_candidates + 1
    mbids = [f"m{i:02d}" for i in range(n)]
    lengths = [n_candidates] + [1] * n_candidates
    offsets = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(lengths, out=offsets[1:])

    cand, rank = [], []
    for j in range(1, n):  # node 0's candidates, strongest first
        cand.append(j)
        rank.append(1.0 - (j - 1) * 0.001)
    for _ in range(1, n):  # every other node lists node 0 only
        cand.append(0)
        rank.append(0.5)

    path = tmp_path / "cap.npz"
    np.savez_compressed(
        path,
        offsets=offsets,
        cand=np.array(cand, dtype=np.int32),
        rank=np.array(rank, dtype=np.float64),
        mbids=np.array(mbids, dtype=object),
    )
    return Capture(path)


@pytest.fixture
def cap(tmp_path):
    return _write_capture(tmp_path, n_candidates=60)


def _labels(**overrides) -> dict[str, set[str]]:
    """Everyone shares "rock" with the binding node unless overridden."""
    labels = {f"m{i:02d}": {"rock"} for i in range(61)}
    labels.update(overrides)
    return labels


def test_lambda_zero_reproduces_the_baseline_selection_exactly(cap):
    # Spec section 4's GREEN check on the selection side, and section 1's
    # property 1: the multiplier is exactly 1, not approximately. If this ever
    # fails, no turnover figure from this module counts.
    labels = _labels()
    field = agreement_field(cap, labels)
    assert np.array_equal(mask_tag(cap, field, 0.0), cap.pos < K)


def test_lambda_can_promote_a_genre_match_past_a_stronger_mismatch(cap):
    # m50 is the last candidate inside the top-50 and shares nothing; m51 is
    # the first one outside and matches exactly. Their strengths differ by
    # 0.001, so only the agreement term can reorder them.
    labels = _labels(m50={"jazz"}, **{f"m{i}": {"jazz"} for i in range(52, 61)})
    field = agreement_field(cap, labels)
    selected = mask_tag(cap, field, 2.0)

    slots = {int(c): int(cap.offsets[0]) + i for i, c in enumerate(cap.s_cand[: cap.lengths[0]])}
    assert selected[slots[51]], "a full genre match just outside the cap was not promoted"
    assert not selected[slots[50]], "a genre mismatch at the boundary was not displaced"


def test_unlabelled_candidate_takes_the_shared_neutral_never_zero(cap):
    # The neutral rule is the pre-registration's ONE DORMANT TERM: inert at
    # lambda=0, active in every arm. Zero is a positive claim of dissimilarity
    # and unlabelled artists are disproportionately the obscure ones, so a
    # zero here would push DD-F1 the wrong way.
    labels = _labels(m01=set())
    field = agreement_field(cap, labels)
    slot = int(cap.offsets[0]) + list(cap.s_cand[: cap.lengths[0]]).index(1)

    expected = neutral_for(labels[SELF], [labels[f"m{c:02d}"] for c in cap.s_cand[: cap.lengths[0]]])
    assert field[slot] == expected
    assert field[slot] > 0.0


def test_an_unlabelled_candidate_with_a_strength_lead_still_survives(cap):
    # The same rule, observed where it matters: through selection rather than
    # in the field. m01 is unlabelled AND the strongest candidate.
    labels = _labels(m01=set())
    field = agreement_field(cap, labels)
    slots = {int(c): int(cap.offsets[0]) + i for i, c in enumerate(cap.s_cand[: cap.lengths[0]])}
    assert mask_tag(cap, field, 1.0)[slots[1]]


def test_turnover_counts_creations_and_not_only_deletions():
    # TAS-AM1's correction, pinned. TD-2 measured that per-artist swap counting
    # sees only the drop, while every swap also PROMOTES a neighbour -- which
    # is why turnover is ~2.11x the swap rate and the original bar admitted
    # ~8.4% of all connections differing as a "kill".
    base = np.array([10, 20, 30], dtype=np.int64)
    arm = np.array([20, 30, 40], dtype=np.int64)
    result = edge_turnover(base, arm)
    assert result["deleted"] == 1
    assert result["created"] == 1
    assert result["turnover_share"] == pytest.approx(2 / 3)
    assert list(result["deleted_keys"]) == [10]
    assert list(result["created_keys"]) == [40]


def test_vectorised_classifier_agrees_with_the_scalar_one():
    # classify_keys is a vectorised twin of tas_signal.edge_class. It shares
    # the band boundaries by import, but the branch structure is rewritten, so
    # the agreement is pinned rather than assumed.
    percentiles = [0.0, 0.2, 0.4999, 0.5, 0.8, 0.9899, 0.99, 1.0]
    n = len(percentiles)
    pctl = np.array(percentiles, dtype=np.float64)
    keys, expected = [], {"ff": 0, "fo": 0, "oo": 0}
    for u, pu in enumerate(percentiles):
        for v, pv in enumerate(percentiles):
            if u >= v:
                continue
            keys.append(u * n + v)
            expected[edge_class(pu, pv)] += 1
    counts = classify_keys(np.array(keys, dtype=np.int64), pctl, n)
    assert counts["unframed"] == 0
    assert {c: counts[c] for c in ("ff", "fo", "oo")} == expected


def test_a_node_missing_from_the_fame_frame_is_unframed_not_obscure():
    # The capture and the adopted artifact differ by a handful of nodes
    # (TAS-AM2). Defaulting a missing percentile to 0.0 would silently class
    # those connections as obscure-obscure and quietly move a per-class figure.
    pctl = np.array([np.nan, 0.2], dtype=np.float64)
    counts = classify_keys(np.array([0 * 2 + 1], dtype=np.int64), pctl, 2)
    assert counts["unframed"] == 1
    assert counts["oo"] == 0
