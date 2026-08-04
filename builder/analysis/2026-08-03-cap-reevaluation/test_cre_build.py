"""`CRE-T5`'s properties that must not drift.

The heavy structural check is `cre_build.gate()` (green x2 + red), which runs
against the real archives and is recorded in `cre_build_gate.json`. These are the
cheap invariants that should fail fast in the test suite instead.
"""
from __future__ import annotations

import pytest

from cre_build import SUPPLY, STAGED_BARRED, assemble_cleaned
from cre_common import use_frozen

use_frozen("track_b")
from artistpath_builder.config import BuilderConfig  # noqa: E402


def _cfg(**kw) -> BuilderConfig:
    return BuilderConfig(**kw)


def test_cleanup_is_held_constant_and_the_assert_fires():
    """Plan Global Constraints: both drop flags on in EVERY cell. A cell with
    either off is not in this design, and the harness must refuse it rather
    than quietly building an uncontrolled substrate."""
    for off in ("drop_no_release_tail", "drop_featured_credit"):
        with pytest.raises(AssertionError, match="cleanup constant"):
            assemble_cleaned(_cfg(**{off: False}), None, None, None)


def test_both_drop_flags_default_on():
    # Asserted, never set (the harness relies on these being the shipped
    # defaults; if that ever changes, the assert above becomes a trap).
    cfg = _cfg()
    assert cfg.drop_no_release_tail is True
    assert cfg.drop_featured_credit is True


def test_uncapped_is_staged_and_barred_from_candidacy():
    # UC is a reference row only (prereg §0.2 / plan Global Constraints); the
    # manifest must say so, which starts here.
    assert "S3" in STAGED_BARRED
    assert SUPPLY["S3"][0] == "UC"
    assert STAGED_BARRED <= set(SUPPLY)


def test_supply_axis_is_the_four_pre_registered_rules():
    assert set(SUPPLY) == {"S0", "S0b", "S1", "S3"}
    assert [SUPPLY[k][0] for k in ("S0", "S0b", "S1", "S3")] == [
        "MK50", "MK100", "TUw-50-50", "UC"
    ]


def test_diagnostics_contract_is_declared():
    """`nodes_entering_cap`, `pop_log_low` and `pop_log_high` are the §0.3
    instrumentation row's inputs; every manifest carries them. Checked against
    the committed gate output rather than by rebuilding (3+ minutes a cell)."""
    import json
    from cre_common import in_dir

    path = in_dir("cre_build_gate.json")
    if not path.exists():
        pytest.skip("run cre_build.py --gate first")
    doc = json.loads(path.read_text(encoding="utf-8"))
    for data_set, row in doc["greens"].items():
        diag = row["diagnostics"]
        for field in ("nodes_entering_cap", "pop_log_low", "pop_log_high"):
            assert field in diag, f"{data_set} diagnostics missing {field}"
        assert diag["pop_log_high"] > diag["pop_log_low"]
        assert diag["nodes_entering_cap"] >= diag["nodes_after_prune"]
        # Cleanup actually bit on both data sets, rather than the flags merely
        # being set: a zero here would mean the drop lists never applied.
        assert diag["dropped_no_release_tail"] > 0
        assert diag["dropped_featured_credit"] > 0
