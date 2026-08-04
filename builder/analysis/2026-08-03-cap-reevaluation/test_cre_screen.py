"""`CRE-T7`'s screen arithmetic, and the baseline carve-out.

`CRE-C6` screens a cell out **iff** the zero-supply pair count makes a `CRE-C1`
median pass arithmetically impossible -- strictly more than half the readable
pairs. At the full 22-pair draw that is 12, not 11, and the boundary is where a
screen either fires wrongly or fails to fire.
"""
from __future__ import annotations

import json

import pytest

from cre_common import in_dir
# Imported, never re-implemented: a local copy passes while the module
# diverges, which is exactly what the closeout B3 tamper check caught here.
from cre_screen import BASELINE_CELLS, STAGED_BARRED, screens_out


@pytest.mark.parametrize("zero,denom,expected", [
    (12, 22, True),    # more than half -- a median pass is impossible
    (11, 22, False),   # exactly half -- the median can still land on the bar
    (22, 22, True),
    (0, 22, False),
    (8, 14, True),     # recomputed denominator after CRE-G3 drops
    (7, 14, False),    # exactly half again
    (0, 0, False),     # no readable pairs: not a screen, an unreadable cell
])
def test_screen_out_arithmetic(zero, denom, expected):
    assert screens_out(zero, denom) is expected


def test_eleven_of_twentytwo_does_not_screen_but_twelve_does():
    """The plan's worked boundary, stated explicitly so a later edit that turns
    `>` into `>=` fails here rather than silently screening a live cell."""
    assert screens_out(11, 22) is False
    assert screens_out(12, 22) is True


def test_baseline_cells_are_the_ones_named_in_prereg_0_2():
    # A baseline is an instrument, not a candidate: it sweeps even when screened.
    assert BASELINE_CELLS == {"E-S0", "E-S1", "B-S0", "B-S1"}
    # The (D1-branch) cells are absent because CRE-D1 fired not_supported.
    assert "B-S2" not in BASELINE_CELLS


def test_staged_cells_are_barred_from_candidacy():
    assert STAGED_BARRED == {"E-S3", "B-S3"}


def test_committed_screen_honours_the_baseline_carve_out():
    """On the committed output: any screened cell that is a named baseline must
    be marked as sweeping anyway."""
    path = in_dir("cre_screen.json")
    if not path.exists():
        pytest.skip("run cre_screen.py first")
    doc = json.loads(path.read_text(encoding="utf-8"))
    for name, row in doc["cells"].items():
        c6 = row["CRE_C6"]
        if c6["screened_out"] and row["is_isolating_baseline"]:
            assert c6["sweeps_anyway_as_baseline"] is True, name
        # Pin (c): undefined pairs never enter the denominator.
        undefined = c6["undefined_pairs"]
        assert c6["readable_pairs_denominator"] + undefined == len(c6["per_pair"])


def test_committed_screen_holds_the_cleanup_constant():
    """One cleaned pre-cap population per data set -- the held-constant claim,
    checked on the committed record rather than only inside the run."""
    path = in_dir("cre_screen.json")
    if not path.exists():
        pytest.skip("run cre_screen.py first")
    doc = json.loads(path.read_text(encoding="utf-8"))
    for ds in ("ALG-E", "ALG-B"):
        vals = {r["CRE_C3"]["cleaned_pre_cap_population"]
                for r in doc["cells"].values() if r["data_set"] == ds}
        assert len(vals) <= 1, f"{ds}: pre-cap population varies across cells {vals}"
