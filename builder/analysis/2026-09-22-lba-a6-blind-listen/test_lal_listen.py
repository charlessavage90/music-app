"""The listen's pure parts: page validation, the tally and its invariance, the strike, the page-leak
guard, the side deal and the Deezer-id refusal. No map, no network."""
import itertools
import random
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from lal_common import AXES, DEPTHS, IDENTIFY, MARGIN, STRENGTHS
from lal_pairs_final import apply_strike
from lal_page import apply_post, missing_slots, row_complete
from lal_unblind import RunIncomplete, descriptive, listen_read, tally

HERE = Path(__file__).resolve().parent
KEYS = [f"a{i}|b{i}" for i in range(8)]


def entry(q1="L", q2="L", s1="slight", s2="slight", identify="no", known=False, clip=False):
    return {"q1": q1, "q2": q2, "q1_strength": s1 if q1 != "none" else None,
            "q2_strength": s2 if q2 != "none" else None, "identify": identify,
            "known_everyone": known, "clip_blocked": clip, "notes": ""}


def full_state(fn=lambda k, d: entry()):
    return {"rows": {k: {str(d): fn(k, d) for d in DEPTHS} for k in KEYS},
            "pairs": {k: {"collapse": "", "notes": ""} for k in KEYS}}


def mapping(left_challenger=KEYS[:4]):
    return {k: ({"L": "challenger", "R": "incumbent"} if k in left_challenger
                else {"L": "incumbent", "R": "challenger"}) for k in KEYS}


# --- page ---------------------------------------------------------------------------------------

def test_a_complete_row_needs_identify_and_both_flags():
    assert row_complete(entry())
    e = entry()
    del e["identify"]
    assert not row_complete(e)
    e = entry()
    del e["known_everyone"]
    assert not row_complete(e)


def test_a_pick_without_strength_is_incomplete_and_no_preference_refuses_one():
    assert not row_complete({**entry(), "q1_strength": None})
    assert not row_complete({**entry(q1="none"), "q1_strength": "slight"})


def test_apply_post_refuses_a_missing_identify():
    body = {"pair": KEYS[0], "depth": 0, "q1": "L", "q2": "none", "q1_strength": "strong"}
    with pytest.raises(ValueError, match="identify"):
        apply_post({"rows": {}, "pairs": {}}, "/row", body, KEYS)


def test_apply_post_stores_a_valid_row_with_flags():
    state = {"rows": {}, "pairs": {}}
    apply_post(state, "/row", {"pair": KEYS[0], "depth": 10, "q1": "R", "q2": "none", "q1_strength": "strong",
                               "identify": "yes_left", "known_everyone": True}, KEYS)
    e = state["rows"][KEYS[0]]["10"]
    assert e["identify"] == "yes_left" and e["known_everyone"] is True and e["clip_blocked"] is False
    assert row_complete(e)


def test_status_lists_missing_rows_and_pairs():
    assert len(missing_slots({"rows": {}, "pairs": {}}, KEYS)) == len(KEYS) * (len(DEPTHS) + 1)


def test_the_page_carries_every_frozen_wording_and_vocabulary_verbatim():
    html = (HERE / "lal_page.html").read_text(encoding="utf-8")
    for s in ("At this point, which side holds together better as a journey — each step a sensible next listen?",
              "At this point, which side gives you more artists that are new to you?",
              "On this row, can you tell which side is the new map?",
              "Every artist that differed between the two sides was already known to me",
              "a clip problem stopped me judging this row",
              "Did either side collapse into a random walk into obscurity? If so, which and where?",
              "no clip found"):
        assert s in html, s
    for v in (*STRENGTHS, *IDENTIFY):
        assert f'"{v}"' in html
    assert "Trade-off" not in html   # LBL-Q3 is dropped (LBA-AM6-4)


def test_the_identification_question_starts_hidden():
    html = (HERE / "lal_page.html").read_text(encoding="utf-8")
    assert re.search(r'idP\.className = "q hidden"', html)


# --- tally --------------------------------------------------------------------------------------

def test_no_read_before_the_full_run_state():
    s = full_state()
    del s["pairs"][KEYS[0]]
    with pytest.raises(RunIncomplete):
        tally(s, mapping())


def test_all_picks_for_the_candidate_is_a_pass():
    m = mapping()
    s = full_state(lambda k, d: entry(q1="L" if m[k]["L"] == "challenger" else "R",
                                      q2="L" if m[k]["L"] == "challenger" else "R"))
    out = tally(s, m)
    assert out["read"] == "LAL-R1" and out["axes"]["coherence"]["margin_toward_candidate"] == 24


def test_all_no_preference_is_a_tie_and_clip_loss_makes_it_underpowered():
    assert tally(full_state(lambda k, d: entry("none", "none")), mapping())["read"] == "LAL-R2"
    assert tally(full_state(lambda k, d: entry("none", "none", clip=True)), mapping())["read"] == "LAL-R4"


def test_a_split_is_fail():
    axes = {"coherence": {"verdict": "candidate_better"}, "novelty": {"verdict": "served_better"}}
    assert listen_read(axes) == ("LAL-R3", ["novelty"])


def test_the_margin_bar_is_eight():
    assert MARGIN == 8
    m = mapping()
    # 8 rows toward the candidate on coherence, the rest no preference
    rows = [(k, d) for k in KEYS for d in DEPTHS][:8]
    s = full_state(lambda k, d: entry(q1=("L" if m[k]["L"] == "challenger" else "R") if (k, d) in rows else "none",
                                      q2="none"))
    assert tally(s, m)["axes"]["coherence"]["verdict"] == "candidate_better"
    rows7 = rows[:7]
    s7 = full_state(lambda k, d: entry(q1=("L" if m[k]["L"] == "challenger" else "R") if (k, d) in rows7 else "none",
                                       q2="none"))
    assert tally(s7, m)["axes"]["coherence"]["verdict"] == "no_detectable_difference"


def test_the_verdict_is_invariant_to_strength_identification_and_known_everyone():
    """LBA-AM6-8: the verdict must be identical under every assignment of LAL-Q3, LAL-Q4 and LAL-K."""
    m = mapping()
    rng = random.Random(7)
    picks = {(k, d): (rng.choice("LR") if rng.random() < 0.6 else "none", rng.choice(["L", "R", "none"]))
             for k in KEYS for d in DEPTHS}
    base = tally(full_state(lambda k, d: entry(*picks[(k, d)])), m)
    for s1, idf, known in itertools.product(STRENGTHS, IDENTIFY, (False, True)):
        s = full_state(lambda k, d: entry(*picks[(k, d)], s1=s1, s2=s1, identify=idf, known=known))
        assert tally(s, m) == base
    for _ in range(50):
        s = full_state(lambda k, d: entry(*picks[(k, d)], s1=rng.choice(STRENGTHS), s2=rng.choice(STRENGTHS),
                                          identify=rng.choice(IDENTIFY), known=rng.random() < 0.5))
        assert tally(s, m) == base


def test_identification_is_scored_against_the_sealed_mapping():
    m = mapping(left_challenger=KEYS)   # candidate on the left everywhere
    d = descriptive(full_state(lambda k, dd: entry(identify="yes_left")), m)
    assert d["LAL-Q4_identification"]["0"] == {"no": 0, "yes_right": 8, "yes_wrong": 0}


def test_tradeoff_rows_are_computed_as_opposite_clear_picks():
    d = descriptive(full_state(lambda k, dd: entry(q1="L", q2="R")), mapping())
    assert d["computed_tradeoff_rows"]["rows"] == 24
    d = descriptive(full_state(lambda k, dd: entry(q1="L", q2="none")), mapping())
    assert d["computed_tradeoff_rows"]["rows"] == 0


def test_axes_are_the_two_frozen_questions():
    assert AXES == {"q1": "coherence", "q2": "novelty"}


# --- strike -------------------------------------------------------------------------------------

def drawn():
    p = lambda i: {"a": {"name": f"A{i}", "mbid": f"a{i}", "rank": i}, "b": {"name": f"B{i}", "mbid": f"b{i}", "rank": i}}  # noqa: E731
    return {"primary": [p(i) for i in range(1, 9)], "reserve": [p(i) for i in range(9, 13)]}


def test_no_strike_keeps_the_draw():
    out = apply_strike(drawn(), set())
    assert [x["a"]["mbid"] for x in out["primary"]] == [f"a{i}" for i in range(1, 9)]
    assert len(out["reserve"]) == 4


def test_a_struck_primary_is_filled_by_the_next_reserve():
    out = apply_strike(drawn(), {3})
    assert [x["a"]["mbid"] for x in out["primary"]] == ["a1", "a2", "a4", "a5", "a6", "a7", "a8", "a9"]
    assert [x["a"]["mbid"] for x in out["reserve"]] == ["a10", "a11", "a12"]


def test_striking_below_eight_stops():
    with pytest.raises(SystemExit):
        apply_strike(drawn(), {1, 2, 3, 4, 5})


# --- generation's pure guards --------------------------------------------------------------------

gen = pytest.importorskip("lal_generate", reason="needs the api package on the path")


def test_the_deal_is_balanced_four_four():
    for seed in range(20):
        m = gen.deal_mapping(KEYS, random.Random(seed))
        assert sum(v["L"] == "challenger" for v in m.values()) == 4


def test_page_leak_guard_refuses_an_undesigned_field_and_a_role_word():
    page = {"pairs": [{"key": "a|b", "a": "A", "b": "B",
                       "rows": [{"depth": 0, "L": {"artists": []}, "R": {"artists": []}}]}]}
    gen.assert_page_data_clean(page)
    with pytest.raises(SystemExit):
        gen.assert_page_data_clean({**page, "listen": "x"})
    bad = {"pairs": [{**page["pairs"][0], "key": "candidate|b"}]}
    with pytest.raises(SystemExit):
        gen.assert_page_data_clean(bad)


def test_names_are_not_scanned_for_role_words():
    page = {"pairs": [{"key": "a|b", "a": "The Candidate", "b": "B",
                       "rows": [{"depth": 0, "L": {"artists": [{"mbid": "m", "name": "Served", "disambiguation": "production duo"}]},
                                 "R": {"artists": []}}]}]}
    gen.assert_page_data_clean(page)


def store(ids: dict):
    order = list(ids)
    return SimpleNamespace(id_by_mbid={m: i for i, m in enumerate(order)},
                           deezer_id_of=lambda i: ids[order[i]], names=order, disambiguations=[""] * len(order))


def test_deezer_ids_conflict_only_when_both_record_different_ids():
    served = store({"m1": "1", "m2": "", "m3": "3"})
    cand = store({"m1": "1", "m2": "2", "m3": "9", "m4": "4"})
    assert gen.conflicting_deezer_ids(served, cand) == ["m3"]


def test_one_source_per_artist_whichever_side():
    served = store({"m1": "", "m2": "22"})
    cand = store({"m1": "11", "m3": "33"})
    info = gen.artist_source(served, cand)
    assert info("m1") == ("m1", "", "11") and info("m2") == ("m2", "", "22") and info("m3") == ("m3", "", "33")
