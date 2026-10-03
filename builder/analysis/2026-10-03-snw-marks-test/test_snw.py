"""Tests for `SNW-` (#271). Synthetic data and the 500-node fixture only: no test reads the listen's
answer files, the page data or the unblind result, and none touches a real map or the model."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import snw_test as s

FIXTURE = s.ROOT / "api" / "tests" / "fixtures" / "graph-fixture.bin"


# ---- helpers -----------------------------------------------------------------------------------
def synth_steps(n_journeys_per_side=24, steps_per_journey=(5, 8), marks_per_side=(9, 43), values=None,
                seed=0, signal=0.0):
    """Two sides of journeys; marks spread at random; values N(0,1) per measure, marked steps shifted
    down by `signal` (so signal 0 is the null)."""
    rng = np.random.default_rng(seed)
    J, I, SIDE, END, M = [], [], [], [], []
    j = 0
    for side in (0, 1):
        n = steps_per_journey[side]
        starts = []
        for _ in range(n_journeys_per_side):
            starts.append(len(J))
            for i in range(n):
                J.append(j); I.append(i); SIDE.append(side); END.append(i in (0, n - 1)); M.append(False)
            j += 1
        idx = [k for k, sd in enumerate(SIDE) if sd == side]
        for k in rng.choice(idx, size=marks_per_side[side], replace=False):
            M[k] = True
    st = s.Steps(np.array(J), np.array(I), np.array(SIDE), np.array(END), np.ones(len(J), bool), np.array(M))
    for m in s.MEASURES:
        v = rng.normal(size=len(J)) if values is None else values[m]
        st.values[m] = v - signal * st.marked
    st.ident = [(sd, (str(jj), str(ii))) for sd, jj, ii in zip(SIDE, J, I)]
    return st


def page_and_answers():
    pairs, rows, mapping = [], {}, {}
    for p in range(s.N_PAIRS):
        key = f"a{p}|b{p}"
        mapping[key] = {"L": "challenger", "R": "incumbent"} if p % 2 else {"L": "incumbent", "R": "challenger"}
        prow, rows[key] = [], {}
        for d in s.DEPTHS:
            sides = {t: {"artists": [{"mbid": f"{key}-{d}-{t}-{i}", "name": "", "disambiguation": ""}
                                     for i in range(6)]} for t in s.TOKENS}
            prow.append({"depth": int(d), **sides})
            rows[key][d] = {"q1": "L", "q2": "R", "q1_strength": "slight", "q2_strength": "strong",
                            "identify": "no", "known_everyone": False, "clip_blocked": False,
                            "marked_all": True, "known": {"L": [], "R": []},
                            "weak": {"L": [0, 2], "R": []}, "notes": ""}
        pairs.append({"key": key, "a": "", "b": "", "rows": prow})
    return {"pairs": pairs}, {"rows": rows}, {"mapping_unsealed": mapping, "maps": {
        r: {"sha256": s.MAPS[r][1]} for r in s.ROLES}, "read": "DSL-R3", "axes": {}}


# ---- inputs: only the weak marks and the side mapping are read ---------------------------------
def test_answer_projection_reads_weak_marks_only():
    _page, verdicts, _res = page_and_answers()
    base = s.weak_marks_only(verdicts)
    other = copy.deepcopy(verdicts)
    for key in other["rows"]:
        for d in other["rows"][key]:
            e = other["rows"][key][d]
            e.update(q1="none", q2="none", q1_strength=None, q2_strength=None, identify="yes_left",
                     known_everyone=True, clip_blocked=True, notes="changed")
            e["known"] = {"L": ["x"], "R": ["y"]}
    assert s.weak_marks_only(other) == base
    minimal = {"rows": {k: {d: {"weak": e["weak"]} for d, e in v.items()} for k, v in verdicts["rows"].items()}}
    assert s.weak_marks_only(minimal) == base   # nothing else is even touched


def test_result_projection_ignores_the_verdict():
    _p, _v, res = page_and_answers()
    a = s.side_mapping_only(res)
    res2 = {**res, "read": "DSL-R1", "axes": {"x": 1}, "DSL-P": {}, "DSL-E": {}}
    assert s.side_mapping_only(res2) == a
    assert s.side_mapping_only({"mapping_unsealed": res["mapping_unsealed"], "maps": res["maps"]}) == a


def test_build_journeys_maps_tokens_to_roles():
    page, verdicts, res = page_and_answers()
    js = s.build_journeys(page, s.weak_marks_only(verdicts), res["mapping_unsealed"])
    assert len(js) == s.N_PAIRS * 3 * 2
    j = next(x for x in js if x.key == "a1|b1" and x.token == "L")
    assert j.role == "challenger" and j.weak == [0, 2] and j.n_steps == 5


@pytest.mark.parametrize("breakage", ["missing_row", "bad_index", "missing_mapping", "seven_pairs"])
def test_build_journeys_refuses_incomplete_run_state(breakage):
    page, verdicts, res = page_and_answers()
    weak = s.weak_marks_only(verdicts)
    mapping = res["mapping_unsealed"]
    if breakage == "missing_row":
        del weak["a0|b0"]["10"]
    elif breakage == "bad_index":
        weak["a0|b0"]["5"]["L"] = [5]          # 6 artists -> steps 0..4
    elif breakage == "missing_mapping":
        del mapping["a3|b3"]
    else:
        page["pairs"].pop()
    with pytest.raises(s.Refused):
        s.build_journeys(page, weak, mapping)


# ---- the measures ------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def store():
    from artistpath_api.graph_store import GraphStore
    return GraphStore.load(FIXTURE)


def test_similarity_is_the_stored_edge_score(store):
    u = 7
    for v, sc in list(store.neighbours_of(u))[:5]:
        assert s.edge_similarity(store, u, v) == pytest.approx(float(sc))
    non = next(v for v in range(store.artist_count) if v != u and v not in {n for n, _ in store.neighbours_of(u)})
    with pytest.raises(s.Refused):
        s.edge_similarity(store, u, non)


def test_shared_neighbours_by_hand(store):
    u = 11
    for v, _ in list(store.neighbours_of(u))[:5]:
        nu = {n for n, _ in store.neighbours_of(u)}
        nv = {n for n, _ in store.neighbours_of(v)}
        inter = len(nu & nv)
        assert s.shared_neighbours(store, u, v) == pytest.approx(inter / max(1, len(nu) + len(nv) - inter))


def test_shared_neighbours_matches_the_exploration_source(store):
    """The restatement equals `r2nsim_core._shared`'s `jac` on every connection of the fixture. This
    test imports the exploration code; the experiment never does."""
    pytest.importorskip("scipy")
    import importlib.util
    spec = importlib.util.spec_from_file_location("r2nsim_core", s.ROOT / "exploration" / "r2-nsim" / "r2nsim_core.py")
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    ctx = SimpleNamespace(store=store, n=store.artist_count, pctl=np.zeros(store.artist_count))
    sh = core._shared(ctx)
    ours = np.array([s.shared_neighbours(store, int(a), int(b)) for a, b in zip(sh["src"], sh["nbr"])])
    assert np.allclose(ours, sh["jac"])


def test_rater_prompt_is_rate_py_verbatim():
    src = (s.ROOT / "exploration" / "kit" / "rate.py").read_text(encoding="utf-8")
    assert f'PROMPT_HEAD = """{s.PROMPT_HEAD}"""' in src
    for part in ("You are a music expert", "including obscure ones.", "Answer only in the exact format requested."):
        assert part in src and part in s.SYSTEM
    assert 'os.environ.get("RATER_MODEL", "sonnet")' in src and s.RATER_MODEL == "sonnet"
    assert "BATCH = 40" in src and s.RATER_BATCH == 40


def test_rater_parse_cache_and_lookup(tmp_path, monkeypatch, store):
    assert s.parse_ratings("1 3\n2. U\n3) 0\n9 2\n", 3) == {0: 3, 1: "U", 2: 0}
    c1, c2 = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    c1.write_text('{"k": "A || B", "r": 1}\nnot json\n{"k": "A || B", "r": 2}\n', encoding="utf-8")
    c2.write_text('{"k": "C || D", "r": "U"}\n', encoding="utf-8")
    assert s.load_rater_cache(c1, c2, tmp_path / "absent") == {"A || B": 2, "C || D": "U"}
    assert s.rater_key("Zed", "Abba") == "Abba || Zed"

    monkeypatch.setattr(s, "RATER_CACHE_OWN", tmp_path / "own.jsonl")
    calls = []

    def fake(lines):
        calls.append(lines)
        return "\n".join(f"{i+1} {'U' if i == 0 else 2}" for i in range(len(lines)))

    u = 3
    vs = [v for v, _ in store.neighbours_of(u)][:3]
    triples = [(store, u, v) for v in vs]
    cached_key = s.rater_key(store.names[u], store.names[vs[2]])
    lookup = s.make_rater_lookup({cached_key: 3}, rate=lambda todo: s.rate_missing(todo, call=fake))
    got = lookup(triples)
    assert got[2] == 3 and len(calls) == 1 and len(calls[0]) == 2
    assert lookup.provenance["from_pinned_cache"] == 1 and lookup.provenance["rated_fresh"] == 2
    assert s.load_rater_cache(tmp_path / "own.jsonl")   # fresh answers were appended


def test_unscorable_rater_is_nan_not_zero(store):
    u = 5
    vs = [v for v, _ in store.neighbours_of(u)][:2]
    mb = store.mbids
    j = s.Journey("k", "5", "L", "incumbent", [mb[vs[0]], mb[u], mb[vs[1]]], [0])
    st = s.score_steps([j], {"incumbent": store, "challenger": store}, lambda tr: ["U", 2])
    assert np.isnan(st.values["rater"][0]) and st.values["rater"][1] == 2.0
    assert st.end.tolist() == [True, True] and st.marked.tolist() == [True, False]


# ---- the statistic -----------------------------------------------------------------------------
def test_concordance_by_hand():
    st = s.Steps(np.array([0, 0, 0, 1, 1]), np.array([0, 1, 2, 0, 1]), np.zeros(5, int), np.zeros(5, bool),
                 np.ones(5, bool), np.array([True, False, False, False, True]))
    st.values["similarity"] = np.array([0.1, 0.5, 0.1, 0.9, 0.2])
    w, p = s.concordance_draws(st, "similarity", st.marked[None, :])
    # journey 0: marked 0.1 vs 0.5 (win) and 0.1 (tie); journey 1: 0.2 vs 0.9 (win)
    assert w[0] == pytest.approx(2.5) and p[0] == 3


def test_a_measure_that_only_separates_journeys_cannot_score():
    """Constant within each journey, lower on the journeys that carry marks: within-journey C is 0.5."""
    st = synth_steps(seed=1)
    for m in s.MEASURES:
        jm = np.array([st.marked[st.journey == j].any() for j in st.journey])
        st.values[m] = np.where(jm, 0.0, 1.0)
    r = s.evaluate(st, n_draws=500)
    for m in s.MEASURES:
        assert r["measures"][m]["C"]["pooled"] == pytest.approx(0.5)
        assert r["measures"][m]["outcome"] == "does_not_fire"


def test_null_draws_keep_each_journeys_mark_count():
    st = synth_steps(seed=2)
    d = s.null_marks(st, 50, 3)
    for j in np.unique(st.journey):
        idx = st.journey == j
        assert (d[:, idx].sum(1) == st.marked[idx].sum()).all()


def test_fires_on_strong_signal_and_not_on_the_null():
    strong = s.evaluate(synth_steps(seed=4, signal=1.5), n_draws=2000)
    assert all(strong["measures"][m]["outcome"] == "fires" for m in s.MEASURES)
    null = s.evaluate(synth_steps(seed=5), n_draws=2000)
    assert not any(null["measures"][m]["outcome"] == "fires" for m in s.MEASURES)


def test_chance_firing_rate_is_bounded_by_construction():
    r = s.evaluate(synth_steps(seed=6), n_draws=3000)
    for m in s.MEASURES:
        assert r["measures"][m]["chance_firing_rate"] <= s.MEASURE_ALPHA + 0.005
    assert r["chance_any_measure_fires"] <= s.FAMILY_ALPHA + 0.01


def test_side_disagreement_blocks_firing():
    st = synth_steps(seed=7)
    for m in s.MEASURES:   # strong signal on the candidate side, reversed on today's
        st.values[m] = st.values[m] - 2.0 * (st.marked & (st.side == 1)) + 2.0 * (st.marked & (st.side == 0))
    r = s.evaluate(st, n_draws=1000)
    for m in s.MEASURES:
        assert r["measures"][m]["C"]["candidate"] > 0.8 and r["measures"][m]["C"]["today"] < 0.5
        assert r["measures"][m]["outcome"] == "does_not_fire" and not r["measures"][m]["F3_both_sides_agree"]


def test_too_few_marks_on_a_side_is_unreadable():
    r = s.evaluate(synth_steps(seed=8, marks_per_side=(4, 43), signal=2.0), n_draws=500)
    assert all(r["measures"][m]["outcome"] == "unreadable" for m in s.MEASURES)


def test_descriptive_shift_moves_marks_and_drops_the_overflow():
    st = s.Steps(np.array([0, 0, 0]), np.array([0, 1, 2]), np.zeros(3, int), np.array([True, False, True]),
                 np.ones(3, bool), np.array([False, False, True]))
    assert s.shifted_marks(st, -1).tolist() == [False, True, False]
    assert s.shifted_marks(st, 1).tolist() == [False, False, False]
    st9 = synth_steps(seed=9)
    d = s.descriptive(st9)
    assert d["decides"].startswith("nothing") and set(d) >= set(s.MEASURES)
    assert d["rater_comparable_with_map_measures"] is True
    marked_cand = np.nonzero(st9.marked & (st9.side == 1))[0]
    st9.values["rater"][marked_cand[: len(marked_cand) // 5]] = np.nan   # 20 % unscorable
    assert s.descriptive(st9)["rater_comparable_with_map_measures"] is False


# ---- run state ---------------------------------------------------------------------------------
def _fixture_walk(store, start, n):
    path, seen = [start], {start}
    while len(path) < n:
        nxt = next(v for v, _ in store.neighbours_of(path[-1]) if v not in seen)
        path.append(nxt); seen.add(nxt)
    return [store.mbids[v] for v in path]


def test_rate_only_reads_no_answer_file(tmp_path, monkeypatch, store):
    """The rating step must work with NO dsl_verdicts.json present at all."""
    page, _v, res = page_and_answers()
    for p_i, pair in enumerate(page["pairs"]):
        for row in pair["rows"]:
            for t_i, t in enumerate(s.TOKENS):
                row[t]["artists"] = [{"mbid": m, "name": "", "disambiguation": ""}
                                     for m in _fixture_walk(store, 10 * p_i + t_i, 5)]
    (tmp_path / "dsl_page_data.json").write_text(json.dumps(page), encoding="utf-8")
    (tmp_path / "dsl_result.json").write_text(json.dumps(res), encoding="utf-8")
    monkeypatch.setattr(s, "DSL_DIR", tmp_path)
    monkeypatch.setattr(s, "RATER_CACHE_OWN", tmp_path / "own.jsonl")
    monkeypatch.setattr(s, "check_run_state", lambda: None)
    monkeypatch.setattr(s, "check_inputs", lambda: None)
    monkeypatch.setattr(s, "load_store", lambda role: store)
    monkeypatch.setattr(s, "rate_missing", lambda todo, call=None: {k: 2 for k, *_ in todo})
    assert s.main(["--rate-only"]) == 0
    assert not (tmp_path / "dsl_verdicts.json").exists()
    with pytest.raises(FileNotFoundError):   # the read itself does need the answers
        monkeypatch.setattr(s, "RATER_CACHE_OWN", tmp_path / "absent.jsonl")
        s.main([])


def test_refuses_a_second_run(tmp_path, monkeypatch):
    res = tmp_path / "snw_result.json"
    res.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(s, "RESULT", res)
    with pytest.raises(s.Refused, match="run-once"):
        s.check_run_state()


def test_pins_are_the_ones_271_names():
    assert s.MAPS["incumbent"][0].as_posix() == "C:/dev/music-app/builder/scratch/graph-lba-a6.bin"
    assert s.MAPS["challenger"][0].as_posix() == "C:/unsung-fast/drp-stage3a/graph-drp-s1.bin"
    assert s.MAPS["incumbent"][1].startswith("28311d81") and s.MAPS["challenger"][1].startswith("418fe666")
    assert s.sha256_lf(s.RATER_CACHE_SRC) == s.RATER_CACHE_SRC_SHA_LF
