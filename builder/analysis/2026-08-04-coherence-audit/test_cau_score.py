import json

import pytest

import cau_score
from cau_common import C1_FAIL, C1_PASS, G1_BAR, N_INJECT


def make(n_real, verdicts, control_verdicts, looked_up=None):
    """One journey with n_real interior slots + N_INJECT controls appended.

    Controls sit at the END so that dropping the exclusion logic changes the
    denominator -- if controls were interleaved a buggy scorer could still
    accidentally produce the right count.
    """
    arts = [{"mbid": "A", "name": "A", "role": "endpoint"}]
    arts += [{"mbid": f"r{i}", "name": f"r{i}", "role": "interior"}
             for i in range(n_real)]
    arts += [{"mbid": f"c{i}", "name": f"c{i}", "role": "interior"}
             for i in range(N_INJECT)]
    arts += [{"mbid": "Z", "name": "Z", "role": "endpoint"}]
    page = {"journeys": [{"id": "J", "artists": arts}]}

    slots = {}
    for i, v in enumerate(verdicts):
        slots[f"J#{i + 1}"] = {"verdict": v, "looked_up": bool(
            looked_up[i] if looked_up else False), "note": ""}
    for i, v in enumerate(control_verdicts):
        slots[f"J#{n_real + 1 + i}"] = {"verdict": v, "looked_up": False, "note": ""}

    sealed = {"injections": {f"k{i}": {"slot": f"J#{n_real + 1 + i}"}
                             for i in range(N_INJECT)}}
    return page, {"slots": slots, "journey_notes": {"J": ""}}, sealed


def exclude(sealed, *slots):
    """CAU-AM3: mark control-adjacent slots, which are judged but not scored."""
    for k, s in zip(sorted(sealed["injections"]), slots):
        sealed["injections"][k]["excluded_slot"] = s
    return sealed


ALL_REJECT = ["doesnt_fit"] * N_INJECT


def test_g1_failure_voids_everything_and_computes_no_readings():
    # 9 of 12 rejected, one below the bar of 10.
    controls = ["doesnt_fit"] * (G1_BAR - 1) + ["fits"] * (N_INJECT - G1_BAR + 1)
    page, judged, sealed = make(4, ["fits"] * 4, controls)
    out = cau_score.evaluate(page, judged, sealed)
    assert out["CAU_G1"]["pass"] is False
    assert out["VOID"] is True
    assert out["readings"] is None, "a blunt instrument must produce NO readings"


def test_g1_exactly_at_bar_passes():
    controls = ["doesnt_fit"] * G1_BAR + ["fits"] * (N_INJECT - G1_BAR)
    page, judged, sealed = make(4, ["fits"] * 4, controls)
    out = cau_score.evaluate(page, judged, sealed)
    assert out["CAU_G1"]["pass"] is True
    assert out["VOID"] is False


def test_c1_boundaries_are_inclusive_the_way_the_spec_reads():
    # exactly the bar -> meets_bar
    n = 100
    v = ["fits"] * int(C1_PASS * n) + ["doesnt_fit"] * (n - int(C1_PASS * n))
    page, judged, sealed = make(n, v, ALL_REJECT)
    assert cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C1"]["branch"] \
        == "meets_bar"

    # exactly the lower bar -> below_bar
    v = ["fits"] * int(C1_FAIL * n) + ["doesnt_fit"] * (n - int(C1_FAIL * n))
    page, judged, sealed = make(n, v, ALL_REJECT)
    assert cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C1"]["branch"] \
        == "below_bar"

    # between -> ambiguous, and the spec forbids a default
    v = ["fits"] * 60 + ["doesnt_fit"] * 40
    page, judged, sealed = make(n, v, ALL_REJECT)
    r = cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C1"]
    assert r["branch"] == "ambiguous"
    assert "real improvement" in r["sentence"]


def test_controls_are_excluded_from_both_denominators():
    # Every real slot fits; every control is rejected. If controls leaked into
    # D_all the fraction would be 4/16, not 4/4.
    page, judged, sealed = make(4, ["fits"] * 4, ALL_REJECT)
    d = cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C1"]["D_all"]
    assert d["n"] == 4
    assert d["fits_frac"] == 1.0
    assert d["doesnt_fit"] == 0, "a control leaked into the real denominator"


def test_d_lookup_is_the_looked_up_subset_only():
    page, judged, sealed = make(
        4, ["fits", "doesnt_fit", "fits", "doesnt_fit"], ALL_REJECT,
        looked_up=[True, True, False, False])
    r = cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C1"]
    assert r["D_all"]["n"] == 4 and r["D_all"]["fits_frac"] == 0.5
    assert r["D_lookup"]["n"] == 2 and r["D_lookup"]["fits_frac"] == 0.5


def test_c2_counts_only_real_slots_and_fires_at_the_trigger():
    page, judged, sealed = make(
        5, ["doesnt_fit"] * 3 + ["fits"] * 2, ALL_REJECT)
    c2 = cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C2"]
    assert c2["worst_journey_doesnt_fit"] == 3, \
        "the 12 rejected controls must not count toward a wrecked journey"
    assert c2["fires"] is True


def test_c3_fires_above_its_trigger():
    page, judged, sealed = make(
        10, ["cant_tell"] * 2 + ["fits"] * 8, ALL_REJECT)
    c3 = cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C3"]
    assert c3["cant_tell_frac"] == 0.2
    assert c3["fires"] is True


def test_incomplete_run_licenses_no_read():
    page, judged, sealed = make(4, ["fits"] * 4, ALL_REJECT)
    del judged["slots"]["J#2"]
    with pytest.raises(cau_score.RunIncomplete):
        cau_score.evaluate(page, judged, sealed)


def test_am3_control_adjacent_slots_are_judged_but_not_scored():
    """The excluded slot was judged next to a fake artist. Scoring it would import
    exactly the bias CAU-AM3 exists to remove."""
    page, judged, sealed = make(
        4, ["fits", "fits", "fits", "doesnt_fit"], ALL_REJECT)
    exclude(sealed, "J#4")            # the doesnt_fit one sat beside a control
    r = cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C1"]
    assert r["D_all"]["n"] == 3, "the control-adjacent slot must leave D_all"
    assert r["D_all"]["fits_frac"] == 1.0
    assert r["D_all"]["excluded_control_adjacent"] == 1


def test_am3_exclusion_also_applies_to_d_lookup_and_c2():
    page, judged, sealed = make(
        5, ["doesnt_fit"] * 3 + ["fits"] * 2, ALL_REJECT,
        looked_up=[True] * 5)
    exclude(sealed, "J#1", "J#2")     # two of the three doesnt_fit are excluded
    out = cau_score.evaluate(page, judged, sealed)["readings"]
    assert out["CAU_C1"]["D_all"]["n"] == 3
    assert out["CAU_C1"]["D_lookup"]["n"] == 3, "D_lookup must honour the exclusion"
    assert out["CAU_C2"]["worst_journey_doesnt_fit"] == 1,         "an excluded slot must not count toward a wrecked journey"
    assert out["CAU_C2"]["fires"] is False


def test_missing_excluded_slot_key_does_not_silently_drop_the_exclusion():
    """A sealed file written before CAU-AM3 has no excluded_slot. The scorer must
    then score everything rather than guess -- and the build asserts the key is
    present, so this path only ever sees an old file."""
    page, judged, sealed = make(4, ["fits"] * 4, ALL_REJECT)
    r = cau_score.evaluate(page, judged, sealed)["readings"]["CAU_C1"]
    assert r["D_all"]["n"] == 4
    assert r["D_all"]["excluded_control_adjacent"] == 0
