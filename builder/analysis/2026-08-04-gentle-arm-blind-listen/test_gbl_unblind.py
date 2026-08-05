import pytest

from gbl_unblind import RunIncomplete, ear_tracking, tally

MAPPING = {f"p{i}": {"L": ("V0" if i % 2 else "G"),
                     "R": ("G" if i % 2 else "V0")} for i in range(8)}


def rows_with(g_wins: int, v_wins: int):
    """Build 8 pairs x d10/d20 rows: first g_wins deep rows pick G's token,
    next v_wins pick V0's token, remainder 'none'. All d0 rows pick V0's token
    to prove d0 is excluded."""
    picks = (["G"] * g_wins + ["V0"] * v_wins + ["none"] * 16)[:16]
    rows, i = {}, 0
    for k, m in MAPPING.items():
        tok = {v: t for t, v in m.items()}
        rows[k] = {"0": tok["V0"]}
        for d in ("10", "20"):
            p = picks[i]; i += 1
            rows[k][d] = tok[p] if p != "none" else "none"
    return rows


def test_spec_worked_example_9_4_fires_for_g():
    out = tally(rows_with(9, 4), MAPPING)
    assert out["deep_rows"] == 16
    assert out["clear_picks"] == {"G": 9, "V0": 4}
    assert out["margin"] == 5
    assert out["branch"] == "G_better"


def test_spec_worked_example_10_6_is_the_null():
    out = tally(rows_with(10, 6), MAPPING)
    assert out["margin"] == 4
    assert out["branch"] == "no_detectable_difference"


def test_v0_side_fires_symmetrically():
    assert tally(rows_with(2, 8), MAPPING)["branch"] == "V0_better"


def test_d0_rows_never_enter_the_tally():
    out = tally(rows_with(0, 0), MAPPING)
    assert out["clear_picks"] == {"G": 0, "V0": 0}   # despite 8 d0 picks


def test_incomplete_run_refuses_a_read():
    rows = rows_with(9, 4)
    del rows["p3"]["20"]
    with pytest.raises(RunIncomplete):
        tally(rows, MAPPING)


def test_the_margin_is_the_scaled_bar_not_the_unscaled_one():
    # GBL-CORR1: the spec's prose, worked examples and arithmetic all say 5;
    # its branch table said 3 until 2026-08-04. A tally built against the table
    # would fire on 8-5. Pinned here so the two can never drift apart again.
    assert tally(rows_with(8, 5), MAPPING)["branch"] == "no_detectable_difference"
    assert tally(rows_with(9, 4), MAPPING)["branch"] == "G_better"


def _sealed(fame_a, fame_b, payload_a, payload_b):
    """One pair, one deep row, picked side = whichever token maps to G."""
    mapping = {"p0": {"L": "G", "R": "V0"}}

    def arm(fame, payload):
        return {"pairs": {"p0": {
            "10": {"metrics": {"fame_pctl_interior": fame, "payload": payload,
                               "top1pct_degree_frac": 0.0, "length": 4}},
            "20": {"metrics": {"fame_pctl_interior": fame, "payload": payload,
                               "top1pct_degree_frac": 0.0, "length": 4}},
        }}}

    return {"mapping": mapping,
            "arms": {"G": arm(fame_a, payload_a), "V0": arm(fame_b, payload_b)}}


def test_ear_tracking_compares_measured_interiors_only():
    # The censoring blind spot is live: a journey that digs deeper delivers more
    # artists the ruler cannot read. Those must not be scored as anything --
    # counting a None as obscure would manufacture the very trend under test.
    sealed = _sealed(fame_a=[0.2, None], fame_b=[0.8, 0.9],
                     payload_a=2, payload_b=1)
    rows = {"p0": {"0": "none", "10": "L", "20": "L"}}
    out = ear_tracking(rows, sealed)
    assert out["rows"] == 2
    assert out["fame_lower"] == 2       # 0.2 < 0.85, the None ignored
    assert out["payload_higher"] == 2


def test_ear_tracking_skips_a_row_with_no_measured_interior_on_one_side():
    sealed = _sealed(fame_a=[None, None], fame_b=[0.8],
                     payload_a=2, payload_b=1)
    rows = {"p0": {"0": "none", "10": "L", "20": "none"}}
    out = ear_tracking(rows, sealed)
    assert out["rows"] == 1
    assert out["fame_lower"] == 0       # unreadable, not favourable
    assert out["payload_higher"] == 1


def test_ear_tracking_ignores_no_preference_rows():
    sealed = _sealed([0.2], [0.8], 2, 1)
    rows = {"p0": {"0": "L", "10": "none", "20": "none"}}
    assert ear_tracking(rows, sealed)["rows"] == 0
