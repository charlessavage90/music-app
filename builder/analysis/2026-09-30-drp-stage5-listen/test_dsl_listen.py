"""The listen's pure parts: page validation and marks, the tally and its invariance, DSL-P and DSL-E
and theirs, the strike and tier selection, the pre-screen's gates and step-2 parsers, the page-leak
guard, the side deal and the metadata refusal. No map, no network."""
import itertools
import random
from pathlib import Path
from types import SimpleNamespace

import pytest

from dsl_common import AXES, DEPTHS, IDENTIFY, MARGIN, STRENGTHS, sha256_lf
from dsl_page import apply_post, missing_slots, row_complete, row_paths
from dsl_pairs_final import apply_strike
from dsl_prescreen import (WANTED, exploration_mbids, g5_names, resolve_names, screen, select,
                           tier_of)
from dsl_unblind import RunIncomplete, descriptive, listen_read, proxy_read, step_read, tally

HERE = Path(__file__).resolve().parent
KEYS = [f"a{i}|b{i}" for i in range(8)]
# Every journey: endpoints + 4 middle artists = 5 steps. Challenger middles are c*, incumbent i*.
PATHS = {"challenger": lambda k, d: [f"{k}s", f"c{k}{d}1", f"c{k}{d}2", "shared", f"c{k}{d}3", f"{k}t"],
         "incumbent": lambda k, d: [f"{k}s", f"i{k}{d}1", "shared", f"i{k}{d}2", f"i{k}{d}3", f"{k}t"]}


def entry(q1="L", q2="L", s1="slight", s2="slight", identify="no", known_all=False, clip=False,
          known=None, weak=None):
    return {"q1": q1, "q2": q2, "q1_strength": s1 if q1 != "none" else None,
            "q2_strength": s2 if q2 != "none" else None, "identify": identify,
            "known_everyone": known_all, "clip_blocked": clip, "notes": "", "marked_all": True,
            "known": known or {"L": [], "R": []}, "weak": weak or {"L": [], "R": []}}


def full_state(fn=lambda k, d: entry()):
    return {"rows": {k: {str(d): fn(k, d) for d in DEPTHS} for k in KEYS}}


def mapping(left_challenger=KEYS[:4]):
    return {k: ({"L": "challenger", "R": "incumbent"} if k in left_challenger
                else {"L": "incumbent", "R": "challenger"}) for k in KEYS}


def sealed(m=None, fame=None):
    m = m or mapping()
    journeys = {r: {k: {str(d): {"path_mbids": PATHS[r](k, d), "fame_pctl_interior": [0.8] * 4, "length": 6,
                                 "added_connections_traversed": 0} for d in DEPTHS} for k in KEYS} for r in PATHS}
    all_mb = {mb for r in journeys.values() for k in r.values() for j in k.values() for mb in j["path_mbids"]}
    return {"mapping": m, "journeys": journeys, "fame_by_mbid": fame or {mb: 0.85 for mb in all_mb}}


def page_data():
    return {"pairs": [{"key": k, "a": "A", "b": "B", "rows": [
        {"depth": d, "L": {"artists": [{"mbid": mb} for mb in PATHS["challenger"](k, d)]},
         "R": {"artists": [{"mbid": mb} for mb in PATHS["incumbent"](k, d)]}} for d in DEPTHS]} for k in KEYS]}


# --- page ---------------------------------------------------------------------------------------

def body(**kw):
    b = {"pair": KEYS[0], "depth": 10, "q1": "R", "q2": "none", "q1_strength": "strong",
         "identify": "yes_left", "known_everyone": False, "marked_all": True,
         "known": {"L": [], "R": []}, "weak": {"L": [], "R": []}}
    b.update(kw)
    return b


def test_a_complete_row_needs_identify_flags_and_the_marking_tick():
    assert row_complete(entry())
    for field in ("identify", "known_everyone", "marked_all", "known", "weak"):
        e = entry()
        del e[field]
        assert not row_complete(e), field
    assert not row_complete({**entry(), "marked_all": False})


def test_a_pick_without_strength_is_incomplete_and_no_preference_refuses_one():
    assert not row_complete({**entry(), "q1_strength": None})
    assert not row_complete({**entry(q1="none"), "q1_strength": "slight"})


def test_apply_post_refuses_a_save_without_the_marking_tick():
    with pytest.raises(ValueError, match="marked every artist"):
        apply_post({"rows": {}}, "/row", body(marked_all=False), KEYS, row_paths(page_data()))


def test_apply_post_stores_marks_validated_against_the_rows_own_journeys():
    state = {"rows": {}}
    k = KEYS[0]
    apply_post(state, "/row", body(known={"L": [f"c{k}101", "shared"], "R": [f"i{k}101"]},
                                   weak={"L": [0, 4, 0], "R": [2]}), KEYS, row_paths(page_data()))
    e = state["rows"][k]["10"]
    assert e["known"] == {"L": sorted([f"c{k}101", "shared"]), "R": [f"i{k}101"]}
    assert e["weak"] == {"L": [0, 4], "R": [2]}
    assert row_complete(e)


@pytest.mark.parametrize("bad", [
    {"known": {"L": ["a0|b0s"], "R": []}},              # an endpoint is not a middle card
    {"known": {"L": ["i" + KEYS[0] + "101"], "R": []}}, # that artist is on the other side
    {"weak": {"L": [5], "R": []}},                      # 5 steps -> indices 0..4
    {"weak": {"L": [True], "R": []}},
    {"known": {"X": []}},
])
def test_apply_post_refuses_marks_the_row_cannot_carry(bad):
    with pytest.raises(ValueError):
        apply_post({"rows": {}}, "/row", body(**bad), KEYS, row_paths(page_data()))


def test_status_lists_missing_rows_only():
    assert len(missing_slots({"rows": {}}, KEYS)) == len(KEYS) * len(DEPTHS)


def test_the_page_carries_every_frozen_wording_and_vocabulary_verbatim():
    html = (HERE / "dsl_page.html").read_text(encoding="utf-8")
    for s in ("At this point, which side holds together better as a journey — each step a sensible next listen?",
              "At this point, which side gives you more artists that are new to you?",
              "On this row, can you tell which side is the new version?",
              "Every artist that differed between the two sides was already known to me",
              "a clip problem stopped me judging this row",
              "I know this artist",
              "I have marked every artist I know on this row",
              "this step doesn't fit",
              "no clip found",
              "recognise as an artist you have listened to or would know by\nname"):
        assert s in html, s
    for v in (*STRENGTHS, *IDENTIFY):
        assert f'"{v}"' in html
    assert "collapse into a random walk" not in html   # the pair-end box is dropped (DRP-AM7-4)
    assert 'idP.className = "q hidden"' in html


# --- tally --------------------------------------------------------------------------------------

def test_no_read_before_the_full_run_state():
    s = full_state()
    del s["rows"][KEYS[0]]["20"]
    for fn in (lambda: tally(s, mapping()), lambda: proxy_read(s, sealed()), lambda: step_read(s, sealed())):
        with pytest.raises(RunIncomplete):
            fn()


def test_all_picks_for_the_candidate_is_a_pass():
    m = mapping()
    s = full_state(lambda k, d: entry(q1="L" if m[k]["L"] == "challenger" else "R",
                                      q2="L" if m[k]["L"] == "challenger" else "R"))
    out = tally(s, m)
    assert out["read"] == "DSL-R1" and out["axes"]["coherence"]["margin_toward_candidate"] == 24


def test_all_no_preference_is_a_tie_and_clip_loss_makes_it_underpowered():
    assert tally(full_state(lambda k, d: entry("none", "none")), mapping())["read"] == "DSL-R2"
    assert tally(full_state(lambda k, d: entry("none", "none", clip=True)), mapping())["read"] == "DSL-R4"


def test_a_split_is_fail_on_the_losing_axis():
    axes = {"coherence": {"verdict": "today_better"}, "novelty": {"verdict": "candidate_better"}}
    assert listen_read(axes) == ("DSL-R3", ["coherence"])


def test_the_margin_bar_is_eight():
    assert MARGIN == 8
    m = mapping()
    rows = [(k, d) for k in KEYS for d in DEPTHS]
    for n, want in ((8, "candidate_better"), (7, "no_detectable_difference")):
        s = full_state(lambda k, d: entry(q1=("L" if m[k]["L"] == "challenger" else "R") if (k, d) in rows[:n] else "none",
                                          q2="none"))
        assert tally(s, m)["axes"]["coherence"]["verdict"] == want


def _random_marks(rng, k, d, m):
    known = {t: [mb for mb in PATHS[m[k][t]](k, d)[1:-1] if rng.random() < 0.5] for t in ("L", "R")}
    weak = {t: [i for i in range(5) if rng.random() < 0.3] for t in ("L", "R")}
    return known, weak


def test_the_verdict_is_invariant_to_strength_identification_known_everyone_and_both_mark_sets():
    """DRP-AM7-10: identical under every assignment of DSL-Q3, DSL-Q4, DSL-K, DSL-M and DSL-W."""
    m = mapping()
    rng = random.Random(7)
    picks = {(k, d): (rng.choice("LR") if rng.random() < 0.6 else "none", rng.choice(["L", "R", "none"]))
             for k in KEYS for d in DEPTHS}
    base = tally(full_state(lambda k, d: entry(*picks[(k, d)])), m)
    for s1, idf, ka in itertools.product(STRENGTHS, IDENTIFY, (False, True)):
        assert tally(full_state(lambda k, d: entry(*picks[(k, d)], s1=s1, s2=s1, identify=idf, known_all=ka)), m) == base
    for _ in range(50):
        def row(k, d):
            known, weak = _random_marks(rng, k, d, m)
            return entry(*picks[(k, d)], s1=rng.choice(STRENGTHS), s2=rng.choice(STRENGTHS),
                         identify=rng.choice(IDENTIFY), known_all=rng.random() < 0.5, known=known, weak=weak)
        assert tally(full_state(row), m) == base


def test_dsl_p_and_dsl_e_are_invariant_to_every_pick_strength_and_identification():
    """DRP-AM7-10: DSL-P and DSL-E identical under every assignment of DSL-Q1 to DSL-Q4."""
    m = mapping()
    rng = random.Random(11)
    marks = {(k, d): _random_marks(rng, k, d, m) for k in KEYS for d in DEPTHS}
    sd = sealed(m)
    base_p = proxy_read(full_state(lambda k, d: entry(known=marks[(k, d)][0], weak=marks[(k, d)][1])), sd)
    base_e = step_read(full_state(lambda k, d: entry(known=marks[(k, d)][0], weak=marks[(k, d)][1])), sd)
    for _ in range(50):
        def row(k, d):
            q1, q2 = rng.choice(["L", "R", "none"]), rng.choice(["L", "R", "none"])
            return entry(q1, q2, s1=rng.choice(STRENGTHS), s2=rng.choice(STRENGTHS), identify=rng.choice(IDENTIFY),
                         known_all=rng.random() < 0.5, known=marks[(k, d)][0], weak=marks[(k, d)][1])
        s = full_state(row)
        assert proxy_read(s, sd) == base_p and step_read(s, sd) == base_e


# --- DSL-P --------------------------------------------------------------------------------------

def _mark_candidate_middles(frac_known: float, m):
    """Mark `frac_known` of each row's candidate-only middles as known, on the candidate side."""
    def row(k, d):
        tok = "L" if m[k]["L"] == "challenger" else "R"
        cand = [mb for mb in PATHS["challenger"](k, d)[1:-1] if mb != "shared"]
        n = round(frac_known * len(cand))
        known = {"L": [], "R": []}
        known[tok] = cand[:n]
        return entry(known=known)
    return full_state(row)


def test_dsl_p_population_is_candidate_only_middles_and_fires_on_a_strict_majority():
    m = mapping()
    out = proxy_read(_mark_candidate_middles(0.0, m), sealed(m))
    assert out["n"] == 8 * 3 * 3            # "shared" is on both sides of every row, so it is excluded
    assert out["fires"] is False and out["readable"] and out["outcome"] == "does_not_fire"
    out = proxy_read(_mark_candidate_middles(2 / 3, m), sealed(m))
    assert out["known"] == 48 and out["threshold"] == 37 and out["fires"] is True
    out = proxy_read(_mark_candidate_middles(1 / 3, m), sealed(m))
    assert out["known"] == 24 and out["fires"] is False


def test_dsl_p_counts_an_artist_known_if_marked_on_any_card_and_reports_mixed_marking():
    m = mapping()
    s = _mark_candidate_middles(0.0, m)
    k = KEYS[0]
    tok = "L" if m[k]["L"] == "challenger" else "R"
    s["rows"][k]["5"]["known"][tok] = ["shared"]   # 'shared' appears on 48 cards; marked on one
    out = proxy_read(s, sealed(m))
    assert out["artists_marked_on_some_cards_not_others"] == 1
    assert out["known"] == 0                        # 'shared' is not in the candidate-only population


def test_dsl_p_counts_a_candidate_only_artist_known_if_marked_on_any_one_of_its_cards():
    m = mapping()
    sd = sealed(m)
    k = KEYS[0]
    for d in map(str, DEPTHS):                       # one candidate-only artist on all three rows
        sd["journeys"]["challenger"][k][d]["path_mbids"][1] = "recurring"
    s = _mark_candidate_middles(0.0, m)
    tok = "L" if m[k]["L"] == "challenger" else "R"
    s["rows"][k]["10"]["known"][tok] = ["recurring"]  # marked on one of its three cards
    out = proxy_read(s, sd)
    assert out["known"] == 1 and out["artists_marked_on_some_cards_not_others"] == 1


def test_dsl_p_is_unreadable_below_ten():
    m = {KEYS[0]: mapping()[KEYS[0]]}
    sd = sealed(m)
    s = {"rows": {KEYS[0]: {str(d): entry() for d in DEPTHS}}}
    out = proxy_read(s, sd)
    assert out["n"] == 9 and out["readable"] is False and out["fires"] is False and out["outcome"] == "unreadable"


def test_dsl_p_bands_are_half_open_and_report_both_populations():
    m = mapping()
    sd = sealed(m, fame=None)
    for mb in list(sd["fame_by_mbid"]):
        sd["fame_by_mbid"][mb] = 0.70 if mb.startswith("c") else (0.99 if mb.startswith("i") else None)
    out = proxy_read(_mark_candidate_middles(0.0, m), sd)
    assert set(out["by_band_candidate_only"]) == {"[0.70, 0.80)"}
    assert set(out["by_band_incumbent_only_reference"]) == {"0.99 and above"}
    assert sum(b["n"] for b in out["by_band_candidate_only"].values()) == out["n"]   # catch-alls: rows sum to n


# --- DSL-E --------------------------------------------------------------------------------------

def _weak_on(m, steps_by_role):
    def row(k, d):
        weak = {t: list(steps_by_role.get(m[k][t], [])) for t in ("L", "R")}
        return entry(weak=weak)
    return full_state(row)


def test_dsl_e_fires_when_candidate_marks_concentrate_on_end_steps():
    m = mapping()
    out = step_read(_weak_on(m, {"challenger": [0]}), sealed(m))      # every mark on the first step
    c = out["candidate"]
    assert c["end_share_of_steps"] == pytest.approx(2 / 5) and c["end_share_of_marks"] == 1.0
    assert out["fires"] is True


def test_dsl_e_does_not_fire_on_middle_marks_or_too_few_marks():
    m = mapping()
    assert step_read(_weak_on(m, {"challenger": [2]}), sealed(m))["fires"] is False
    s = _weak_on(m, {})
    for k in KEYS[:2]:
        tok = "L" if m[k]["L"] == "challenger" else "R"
        s["rows"][k]["5"]["weak"][tok] = [0, 4]
    out = step_read(s, sealed(m))
    assert out["candidate"]["marks"] == 4
    assert out["fires"] is False and out["outcome"] == "unreadable"     # 4 < 8 marks: not "not at the ends"


def test_dsl_e_needs_a_majority_not_only_the_ratio():
    """S5R-4: on long journeys 1.5x the base rate is below half; the plain sentence says "mostly"."""
    m = mapping()
    sd = sealed(m)
    for r in sd["journeys"].values():                                  # 9 cards -> 8 steps, base 2/8
        for k in r.values():
            for j in k.values():
                j["path_mbids"] = j["path_mbids"][:1] + [f"x{i}" for i in range(7)] + j["path_mbids"][-1:]
    out = step_read(_weak_on(m, {"challenger": [0, 7, 1, 2, 3]}), sd)  # end share 2/5 = 0.4 >= 1.5 x 0.25
    assert out["candidate"]["end_share_of_marks"] == pytest.approx(0.4)
    assert out["fires"] is False and out["outcome"] == "does_not_fire"
    out = step_read(_weak_on(m, {"challenger": [0, 7, 1]}), sd)        # 2/3: majority and >= 0.375
    assert out["fires"] is True


def test_dsl_e_threshold_is_one_and_a_half_times_the_base_rate():
    # base rate 2/5 = 0.4; 1.5x = 0.6. Marks on steps 0, 1 and 2 -> end share 1/3: no. 0, 4, 1 -> 2/3: yes.
    m = mapping()
    assert step_read(_weak_on(m, {"challenger": [0, 1, 2]}), sealed(m))["fires"] is False
    assert step_read(_weak_on(m, {"challenger": [0, 1, 4]}), sealed(m))["fires"] is True


def test_dsl_e_reports_today_as_a_reference_and_does_not_read_it():
    m = mapping()
    out = step_read(_weak_on(m, {"incumbent": [0, 4]}), sealed(m))
    assert out["today_reference"]["end_marks"] == 48 and out["fires"] is False


# --- descriptive --------------------------------------------------------------------------------

def test_identification_is_scored_against_the_sealed_mapping():
    m = mapping(left_challenger=KEYS)
    d = descriptive(full_state(lambda k, dd: entry(identify="yes_left")), m)
    assert d["DSL-Q4_identification"]["5"] == {"no": 0, "yes_right": 8, "yes_wrong": 0}


def test_axes_are_the_two_frozen_questions():
    assert AXES == {"q1": "coherence", "q2": "novelty"}


# --- selection, strike --------------------------------------------------------------------------

def ranked(n1, n2):
    mk = lambda t, i: {"a": {"name": f"{t}A{i}", "mbid": f"{t}a{i}", "rank": i},  # noqa: E731
                       "b": {"name": f"{t}B{i}", "mbid": f"{t}b{i}", "rank": i}}
    return {"DRP-T1": [mk("1", i) for i in range(n1)], "DRP-T2": [mk("2", i) for i in range(n2)]}


def test_select_takes_four_and_two_per_tier():
    out = select(ranked(9, 9))
    assert [p["tier"] for p in out["primary"]] == ["DRP-T1"] * 4 + ["DRP-T2"] * 4
    assert [p["tier"] for p in out["reserve"]] == ["DRP-T1"] * 2 + ["DRP-T2"] * 2
    assert out["primary"][0]["a"]["mbid"] == "1a0" and out["reserve"][0]["a"]["mbid"] == "1a4"


def test_a_short_tier_is_filled_from_the_other_in_its_rank_order():
    out = select(ranked(3, 10))
    assert [p["tier"] for p in out["primary"]] == ["DRP-T1"] * 3 + ["DRP-T2"] * 5
    assert [p["tier"] for p in out["reserve"]] == ["DRP-T2"] * 4
    assert [p["a"]["mbid"] for p in out["primary"][3:]] == ["2a0", "2a1", "2a2", "2a3", "2a4"]


def test_fewer_than_twelve_survivors_selects_nothing():
    assert WANTED == 12 and select(ranked(5, 6)) is None


def test_a_struck_primary_is_filled_by_the_same_tier_first():
    drawn = select(ranked(9, 9))
    out = apply_strike(drawn, {5})                     # position 5 is the first DRP-T2 primary
    assert out["primary"][4]["a"]["mbid"] == "2a4"     # DRP-T2's first reserve, not DRP-T1's
    assert out["fills"][0]["same_tier"] is True
    assert [r["a"]["mbid"] for r in out["reserve"]] == ["1a4", "1a5", "2a5"]


def test_a_tier_with_no_reserve_left_borrows_from_the_other():
    drawn = select(ranked(9, 9))
    out = apply_strike(drawn, {5, 11, 12})             # strike a T2 primary and both T2 reserves
    assert out["primary"][4]["tier"] == "DRP-T1" and out["fills"][0]["same_tier"] is False


def test_striking_past_the_reserves_stops():
    with pytest.raises(SystemExit):
        apply_strike(select(ranked(9, 9)), {1, 2, 3, 4, 5})


# --- pre-screen gates and step-2 parsers ----------------------------------------------------------

def per_side(inc, ch):
    return {"incumbent": inc, "challenger": ch}


def test_gate_l_d_n_in_order():
    ok = {d: ["x1", "x2", "x3"] for d in DEPTHS}
    other = {d: ["y1", "y2", "y3"] for d in DEPTHS}
    assert screen(per_side(ok, other), familiar=set())[0] is None
    short = {**other, 10: ["y1", "y2"]}
    assert screen(per_side(ok, short), set())[0].startswith("L")
    missing = {d: v for d, v in other.items() if d != 20}
    assert screen(per_side(ok, missing), set())[0].startswith("L")
    same_at_5 = {**other, 5: ["x1", "x2", "x3"]}
    assert screen(per_side(ok, same_at_5), set())[0].startswith("D")
    assert screen(per_side(ok, other), familiar={"x1", "x2", "x3", "y1", "y2", "y3"})[0].startswith("N")


def test_tier_of_reads_the_lattice_bounds():
    strata = (("DRP-T1", 0.99, 1.0, True), ("DRP-T2", 0.95, 0.99, False), ("DRP-MID", 0.30, 0.70, True))
    assert tier_of(1.0, True, strata) == "DRP-T1" and tier_of(0.99, True, strata) == "DRP-T1"
    assert tier_of(0.9899, True, strata) == "DRP-T2" and tier_of(0.95, True, strata) == "DRP-T2"
    assert tier_of(0.5, True, strata) is None and tier_of(1.0, False, strata) is None


def test_g5_names_parses_only_pair_lines():
    text = "# head\n- Guster → Wishbone Ash  (rerolls: 21)\n- A b → C  (rerolls: 0)\nnot - X → Y\n"
    assert g5_names(text) == {"Guster", "Wishbone Ash", "A b", "C"}


def test_exploration_mbids_reads_columns_three_and_four_and_refuses_a_short_line():
    assert exploration_mbids("# c\nA\tB\tm1\tm2\tkit\n") == {"m1", "m2"}
    with pytest.raises(SystemExit):
        exploration_mbids("A\tB\tm1\n")


def test_resolve_names_over_excludes_homonyms_and_reports_misses():
    found, missing = resolve_names({"Nirvana", "Nobody"}, ["Nirvana", "nirvana", "Other"], ["m1", "m2", "m3"],
                                   str.lower)
    assert found == {"m1", "m2"} and missing == ["Nobody"]


def test_pins_are_computed_on_lf_bytes(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"x\r\ny\r\n")
    b.write_bytes(b"x\ny\n")
    assert sha256_lf(a) == sha256_lf(b)


# --- generation's pure guards --------------------------------------------------------------------

gen = pytest.importorskip("dsl_generate")


def test_the_deal_is_balanced_four_four():
    for seed in range(20):
        dm = gen.deal_mapping(KEYS, random.Random(seed))
        assert sum(v["L"] == "challenger" for v in dm.values()) == 4


def test_page_leak_guard_refuses_an_undesigned_field_and_a_side_word():
    page = {"pairs": [{"key": "a|b", "a": "A", "b": "B",
                       "rows": [{"depth": 5, "L": {"artists": []}, "R": {"artists": []}}]}]}
    gen.assert_page_data_clean(page)
    with pytest.raises(SystemExit):
        gen.assert_page_data_clean({**page, "listen": "x"})
    for word in ("candidate", "today", "ceiling", "tier"):
        with pytest.raises(SystemExit):
            gen.assert_page_data_clean({"pairs": [{**page["pairs"][0], "key": f"{word}|b"}]})


def test_names_are_not_scanned_for_side_words():
    page = {"pairs": [{"key": "a|b", "a": "Today Is The Day", "b": "B",
                       "rows": [{"depth": 5, "L": {"artists": [{"mbid": "m", "name": "Ceiling Fan", "disambiguation": "candidate"}]},
                                 "R": {"artists": []}}]}]}
    gen.assert_page_data_clean(page)


def store(rows: dict):
    order = list(rows)
    return SimpleNamespace(id_by_mbid={m: i for i, m in enumerate(order)},
                           names=[rows[m][0] for m in order], disambiguations=[rows[m][1] for m in order],
                           deezer_id_of=lambda i: rows[order[i]][2])


def test_metadata_conflicts_catch_any_difference_or_a_one_sided_mbid():
    a = store({"m1": ("A", "", "1"), "m2": ("B", "x", ""), "m3": ("C", "", "3")})
    assert gen.metadata_conflicts(a, store({"m1": ("A", "", "1"), "m2": ("B", "x", ""), "m3": ("C", "", "3")})) == []
    assert gen.metadata_conflicts(a, store({"m1": ("A", "", "9"), "m2": ("B", "y", ""), "m3": ("C", "", "3"),
                                            "m4": ("D", "", "")})) == ["m1", "m2", "m4"]
    assert gen.metadata_conflicts(a, store({"m1": ("A", "", "1"), "m2": ("B", "x", ""), "m3": ("c", "", "3")})) == ["m3"]
