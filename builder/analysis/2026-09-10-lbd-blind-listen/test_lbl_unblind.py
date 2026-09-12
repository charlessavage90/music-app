"""The reads are the part of the harness that turns answers into a verdict, so every branch of
`LBD-AM5-5` is exercised here, including the two edges of the bar (8 fires, 7 does not)."""
import pytest

from lbl_common import DEPTHS, MARGIN
from lbl_unblind import RunIncomplete, axis_read, listen_read, sentence, tally

KEYS = [f"a{i}|b{i}" for i in range(8)]
ROWS = [(k, str(d)) for k in KEYS for d in DEPTHS]   # 24


def mapping():
    # Challenger always on the left, so "L" is a challenger pick — the tests read plainly.
    return {k: {"L": "challenger", "R": "incumbent"} for k in KEYS}


def state(q1: list[str], q2: list[str], blocked: set[int] = frozenset()):
    rows = {}
    for i, (k, d) in enumerate(ROWS):
        rows.setdefault(k, {})[d] = {"q1": q1[i], "q2": q2[i], "clip_blocked": i in blocked, "notes": ""}
    return {"rows": rows, "pairs": {k: {"collapse": "", "notes": ""} for k in KEYS}}


def picks(left: int, right: int) -> list[str]:
    return ["L"] * left + ["R"] * right + ["none"] * (24 - left - right)


def test_the_bar_is_eight_of_twenty_four():
    assert MARGIN == 8 and len(ROWS) == 24


def test_a_margin_of_exactly_eight_fires_and_seven_does_not():
    assert axis_read(state(picks(10, 2), picks(0, 0))["rows"], mapping(), "q1")["verdict"] == "challenger_better"
    assert axis_read(state(picks(9, 2), picks(0, 0))["rows"], mapping(), "q1")["verdict"] == "no_detectable_difference"
    assert axis_read(state(picks(2, 10), picks(0, 0))["rows"], mapping(), "q1")["verdict"] == "incumbent_better"


def test_pass_needs_a_win_and_no_loss():
    out = tally(state(picks(12, 1), picks(3, 3)), mapping())
    assert out["read"] == "LBL-R1" and out["axes_named"] == ["coherence"]


def test_a_split_is_fail_on_the_losing_axis():
    out = tally(state(picks(12, 1), picks(1, 12)), mapping())
    assert out["read"] == "LBL-R3" and out["axes_named"] == ["novelty"]


def test_both_axes_below_the_bar_is_a_tie():
    assert tally(state(picks(5, 3), picks(4, 4)), mapping())["read"] == "LBL-R2"


def test_eight_clip_blocked_no_preference_rows_make_an_axis_underpowered():
    blocked = set(range(16, 24))          # the eight "none" rows at the end
    out = tally(state(picks(10, 6), picks(4, 4), blocked), mapping())
    assert out["axes"]["coherence"]["verdict"] == "underpowered"
    assert out["read"] == "LBL-R4"


def test_seven_lost_rows_are_not_underpowered():
    blocked = set(range(17, 24))
    assert tally(state(picks(10, 6), picks(4, 4), blocked), mapping())["read"] == "LBL-R2"


def test_a_decisive_margin_stands_however_many_rows_were_lost():
    blocked = set(range(10, 24))
    out = tally(state(picks(9, 1), picks(4, 4), blocked), mapping())
    assert out["axes"]["coherence"]["verdict"] == "challenger_better" and out["read"] == "LBL-R1"


def test_a_blocked_row_with_a_clear_pick_is_not_lost():
    out = axis_read(state(picks(24, 0), picks(0, 0), set(range(24)))["rows"], mapping(), "q1")
    assert out["clip_blocked_no_preference_rows"] == 0


def test_the_shuffled_side_is_what_counts_not_the_letter():
    flipped = {k: {"L": "incumbent", "R": "challenger"} for k in KEYS}
    assert axis_read(state(picks(12, 0), picks(0, 0))["rows"], flipped, "q1")["verdict"] == "incumbent_better"


def test_a_missing_row_licenses_no_read():
    s = state(picks(12, 1), picks(3, 3))
    del s["rows"][KEYS[3]]["10"]
    with pytest.raises(RunIncomplete):
        tally(s, mapping())


def test_a_missing_pair_entry_licenses_no_read():
    s = state(picks(12, 1), picks(3, 3))
    del s["pairs"][KEYS[0]]
    with pytest.raises(RunIncomplete):
        tally(s, mapping())


def test_listen_read_order_puts_a_loss_before_a_win():
    axes = {"coherence": {"verdict": "challenger_better"}, "novelty": {"verdict": "incumbent_better"}}
    assert listen_read(axes) == ("LBL-R3", ["novelty"])


def test_sentences_are_the_amendments_with_the_axis_substituted():
    assert sentence(1, "LBL-R3", ["novelty"]) == "The lists ListenBrainz published give better journeys on novelty."
    assert sentence(1, "LBL-R2", []) == "My ear cannot tell our recomputed lists from ListenBrainz's own."


# --- LBD-AM6: listen 2's reads are UNCHANGED, and the new items decide nothing --------------------

EXTRAS = ("tradeoff", "strength")


def with_extras(s: dict, strength: str = "strong", tradeoff: str = "no") -> dict:
    """Add LBL-Q3 and LBL-Q4 answers to every row of a state built by `state()`."""
    for k, depths in s["rows"].items():
        for d, entry in depths.items():
            entry["tradeoff"] = tradeoff
            for q in ("q1", "q2"):
                entry[f"{q}_strength"] = strength if entry[q] in ("L", "R") else None
    return s


def test_listen_twos_sentences_are_the_amendments_own():
    assert sentence(2, "LBL-R2", []) == "My ear cannot tell the two bars apart."
    assert sentence(2, "LBL-R1", ["coherence"]) == (
        "The two-listener bar gives better journeys on coherence, and no worse on the other.")
    assert sentence(2, "LBL-R3", ["novelty"]) == "ListenBrainz's own bar gives better journeys on novelty."


def test_listen_two_says_bars_where_listen_one_said_lists():
    """The comparison changed; the shape of the read did not. A copied listen-1 sentence here would
    claim listen 2 measured something it does not."""
    assert "recomputed lists" not in sentence(2, "LBL-R2", [])
    assert "bar" in sentence(2, "LBL-R3", ["novelty"])


def test_the_bar_and_the_row_count_are_unchanged_for_listen_two():
    assert MARGIN == 8 and len(ROWS) == 24


@pytest.mark.parametrize("strength", ["slight", "strong"])
def test_the_verdict_does_not_move_with_pick_strength(strength):
    """LBL-R1-R4 count rows. If strength could change a verdict, the reads would not be unchanged."""
    out = tally(with_extras(state(picks(12, 1), picks(3, 3)), strength=strength), mapping(), EXTRAS)
    assert out["read"] == "LBL-R1" and out["axes"]["coherence"]["margin_toward_challenger"] == 11


@pytest.mark.parametrize("tradeoff", ["yes", "no"])
def test_the_verdict_does_not_move_with_the_tradeoff_answer(tradeoff):
    out = tally(with_extras(state(picks(5, 3), picks(4, 4)), tradeoff=tradeoff), mapping(), EXTRAS)
    assert out["read"] == "LBL-R2"


def test_a_listen_two_row_missing_its_strength_licenses_no_read():
    s = with_extras(state(picks(12, 1), picks(3, 3)))
    s["rows"][KEYS[2]]["10"]["q1_strength"] = None      # the pick is still "L"
    with pytest.raises(RunIncomplete):
        tally(s, mapping(), EXTRAS)


def test_a_listen_two_row_missing_its_tradeoff_licenses_no_read():
    s = with_extras(state(picks(12, 1), picks(3, 3)))
    del s["rows"][KEYS[1]]["0"]["tradeoff"]
    with pytest.raises(RunIncomplete):
        tally(s, mapping(), EXTRAS)


def test_the_same_state_reads_fine_without_the_extras_demanded():
    """Listen 1's run state is not retroactively incomplete."""
    assert tally(state(picks(12, 1), picks(3, 3)), mapping())["read"] == "LBL-R1"


def test_the_descriptive_read_counts_strength_by_role_and_says_it_decides_nothing():
    from lbl_unblind import descriptive_extras
    s = with_extras(state(picks(10, 2), picks(0, 0)), strength="strong", tradeoff="yes")
    out = descriptive_extras(s, mapping(), EXTRAS)
    assert out["pick_strength"]["coherence"]["strong"] == {"challenger": 10, "incumbent": 2}
    assert out["pick_strength"]["coherence"]["slight"] == {"challenger": 0, "incumbent": 0}
    assert out["tradeoff_rows"] == {"yes": 24, "no": 0, "of_rows": 24}
    assert "decides" in out and "nothing" in out["decides"]


def test_the_descriptive_read_reports_a_mixture_as_a_mixture():
    from lbl_unblind import descriptive_extras
    s = state(picks(4, 0), picks(0, 0))
    for i, (k, d) in enumerate(ROWS):
        entry = s["rows"][k][d]
        entry["tradeoff"] = "yes" if i < 5 else "no"
        for q in ("q1", "q2"):
            entry[f"{q}_strength"] = (["slight", "strong"][i % 2]) if entry[q] in ("L", "R") else None
    out = descriptive_extras(s, mapping(), EXTRAS)
    coherence = out["pick_strength"]["coherence"]
    assert coherence["slight"]["challenger"] + coherence["strong"]["challenger"] == 4
    assert out["tradeoff_rows"]["yes"] == 5


def test_the_descriptive_read_is_absent_when_the_listen_did_not_ask():
    from lbl_unblind import descriptive_extras
    out = descriptive_extras(state(picks(4, 0), picks(0, 0)), mapping(), ())
    assert set(out) == {"decides"}
