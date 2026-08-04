"""`CRE-T6`'s properties: the `S2` device's degeneracy and its liveness.

The degeneracy gate is the one that matters. `S2` must be **one knob** away from
`S1` (prereg §0.2 names `S1` as its isolating baseline), and the way that is
proved is: with an agreement table that is undefined everywhere, `cap_tag_limited`
must reproduce `cap_trimmed_union(trim="weakest_first")` exactly.

**Why the tuple key makes that identity exact rather than merely observed**
(analyst M4a): every `a_eff` collapses to one constant `c`, so the first key
element is `strength * c`. A constant multiplier is only monotone
**non-decreasing** in IEEE doubles -- two distinct strengths can collapse to the
same product -- so the first element alone would leave those pairs to be broken by
`_desc(v)`, which is *not* strength order. The second element is the raw strength,
which restores it. The identity therefore holds by construction, and the earlier
"a constant multiplier preserves the order" argument must not be restated.
"""
from __future__ import annotations

import pytest

from cre_build import cap_tag_limited
from cre_common import use_frozen

use_frozen("track_b", "tag_disc")
from cb_build_variants import cap_trimmed_union  # noqa: E402


class AllNone:
    kind = "all_none"

    def labelled(self, mbid):
        return False

    def a(self, u, v):
        return None


class OneZero:
    """Ranks exactly one edge at agreement 0; everything else is strongly
    agreed. The zero edge must be deleted first at an over-budget node."""

    kind = "one_zero"

    def __init__(self, pair):
        self.pair = frozenset(pair)

    def labelled(self, mbid):
        return True

    def a(self, u, v):
        return 0.0 if frozenset((u, v)) == self.pair else 0.9


def _fixture(n=8):
    """A hub `h` joined to n leaves at distinct strengths, plus a leaf-leaf ring
    so symmetrise has something to keep."""
    names = [f"L{i:02d}" for i in range(n)]
    ranking = {"h": {}}
    adjacency = {"h": {}}
    for i, name in enumerate(names):
        strength = 1.0 + i          # all distinct
        ranking["h"][name] = strength
        adjacency["h"][name] = 0.5 + i / 100.0
        ranking[name] = {"h": strength}
        adjacency[name] = {"h": 0.5 + i / 100.0}
    pop = {k: 0.5 for k in list(adjacency)}
    return adjacency, ranking, pop, names


def test_degeneracy_all_none_reproduces_trimmed_union_exactly():
    adjacency, ranking, pop, _ = _fixture()
    d = 4
    mine = cap_tag_limited(adjacency, ranking, pop, j=50, d=d, agree=AllNone())
    theirs = cap_trimmed_union(adjacency, ranking, pop, j=50, d=d,
                               trim="weakest_first")
    assert mine == theirs


class AllZero:
    """Agreement measured at exactly 0 on every edge -- the block analyst M4
    found on ~3.9% of real edges, here made total."""

    kind = "all_zero"

    def labelled(self, mbid):
        return True

    def a(self, u, v):
        return 0.0


def test_strength_order_survives_a_total_product_degeneracy():
    """The property the tuple's SECOND element exists for.

    With agreement exactly 0 everywhere, the first key element is `strength * 0`
    = 0.0 for every edge, so it ties on all of them. Under a bare product key the
    order would then fall to `_desc(v)` -- highest MBID first, with similarity
    playing no part, which is what M4 objected to. The second element restores
    the strength order, so the result must still equal `weakest_first`.

    This is used instead of the IEEE product-collapse case the plan describes:
    a search over 2,000,000 adjacent doubles found **no** pair whose product with
    the 0.15 neutral constant collapses, which matches the plan's own note that
    collapses measure at zero on today's edge scores. The all-zero block is the
    constructible degeneracy, and it exercises the same key element harder --
    every edge ties rather than a rare pair.
    """
    adjacency, ranking, pop, _ = _fixture(n=6)
    mine = cap_tag_limited(adjacency, ranking, pop, j=50, d=3, agree=AllZero())
    theirs = cap_trimmed_union(adjacency, ranking, pop, j=50, d=3,
                               trim="weakest_first")
    assert mine == theirs


def test_a_bare_product_key_would_fail_that_property():
    """The red half: shows the previous test is not vacuous by demonstrating
    that dropping the middle element genuinely changes the surviving set."""
    adjacency, ranking, pop, _ = _fixture(n=6)
    from cb_build_variants import _desc, _top_j
    from artistpath_builder.graph import symmetrise

    d = 3
    keep = _top_j(ranking, adjacency, 50, lambda u, v: (-ranking[u][v], v))
    unioned = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in keep[node] or node in keep.get(dst, set()):
                unioned[node][dst] = score
    result = symmetrise(unioned)
    for node in sorted(result, key=lambda n: (-len(result[n]), n)):
        excess = len(result[node]) - d
        if excess <= 0:
            continue
        # BARE PRODUCT KEY -- the form M4 rejected.
        doomed = sorted(result[node], key=lambda v: (0.0, _desc(v)))[:excess]
        for victim in doomed:
            result[node].pop(victim, None)
            result[victim].pop(node, None)

    theirs = cap_trimmed_union(adjacency, ranking, pop, j=50, d=d,
                               trim="weakest_first")
    assert result != theirs, (
        "the bare-product key happens to agree here, so the test above proves "
        "nothing -- pick a fixture where MBID order and strength order differ")


def test_liveness_a_zero_agreement_edge_is_deleted_first():
    """The device must actually re-order deletions, not merely be wired in."""
    adjacency, ranking, pop, names = _fixture()
    strongest = names[-1]                      # would survive on strength alone
    survives = cap_tag_limited(adjacency, ranking, pop, j=50, d=4,
                               agree=AllNone())
    assert strongest in survives["h"], "fixture: the strongest edge should survive"

    killed = cap_tag_limited(adjacency, ranking, pop, j=50, d=4,
                             agree=OneZero(("h", strongest)))
    assert strongest not in killed["h"], (
        "the zero-agreement edge survived -- the device is not live")


def test_agreement_kinds_are_the_three_pre_registered_ones():
    from cre_tags import KINDS

    assert KINDS == ("real", "label_scramble", "vote_scramble")


def test_vote_scramble_preserves_each_artists_multiset_of_strengths():
    """CRE-AM1's sentence, made a property: the vote-scramble destroys which tag
    a vote attaches to and preserves the artist's vote-distribution shape."""
    from cre_tags import _rel_table_vote_scrambled
    from wav_read import rel_table

    per = {
        "a": {"A": {"rock": 9.0, "pop": 4.0, "jazz": 1.0}, "W": {}, "G": {}, "D": {}},
        "b": {"A": {"folk": 7.0, "punk": 2.0}, "W": {}, "G": {}, "D": {}},
    }
    real, real_smax = rel_table(per)
    scram, scram_smax = _rel_table_vote_scrambled(per)
    for m in per:
        assert sorted(real[m].values()) == pytest.approx(
            sorted(scram[m].values())), f"{m}: strength multiset changed"
        assert set(real[m]) == set(scram[m]), f"{m}: label set changed"
        assert real_smax[m] == scram_smax[m]
    # And it must actually move something, or it is not a control.
    assert any(real[m] != scram[m] for m in per)


def _stub_tag_sources(monkeypatch):
    """Replace only the expensive inputs (`five_frames`, `masses`, and the vote
    normalisation) so `agreement_table`'s own caching rule can be exercised in
    milliseconds. `idf_table` is deliberately left REAL: it is the function whose
    output depends on `n_artists`, so stubbing it would test a restatement of the
    rule instead of the rule."""
    import cre_tags

    w4 = {"a": {"rock"}, "b": {"rock", "pop"}, "c": {"pop", "jazz"}}
    monkeypatch.setattr(cre_tags, "five_frames", lambda: {"W4": w4})
    monkeypatch.setattr(cre_tags, "masses", lambda: {m: {} for m in w4})
    monkeypatch.setattr(cre_tags, "rel_table", lambda per: ({}, {}))
    monkeypatch.setattr(cre_tags, "rel_for",
                        lambda rel, smax, m, labs: {x: 1.0 for x in labs})
    monkeypatch.setattr(cre_tags, "_CACHE", {})
    return cre_tags


def test_agreement_table_cache_is_keyed_on_n_artists_not_kind_alone(monkeypatch):
    """The cache must not hand a table built at one `n_artists` to a caller that
    asked for another.

    Keyed on `kind` alone the hit returns before `n_artists` is consulted, so the
    second call here would receive the first call's table and every agreement it
    reports would be computed at the wrong idf. No caller varies `n_artists`
    today, which is what makes this silent rather than loud: the sweeps would have
    produced a wrong number, not an error.
    """
    cre_tags = _stub_tag_sources(monkeypatch)

    small = cre_tags.agreement_table("real", n_artists=10)
    large = cre_tags.agreement_table("real", n_artists=10_000)

    assert small is not large, "the second n_artists got the first one's table"
    assert small._idf != large._idf, (
        "fixture: idf must genuinely differ across these two n_artists, or the "
        "assertion above proves nothing")


def test_agreement_table_still_caches_within_one_n_artists(monkeypatch):
    """The red half of the test above: a key that never hits would also pass it.

    Building the real tables costs minutes (`masses()` dominates the S2 cells),
    so a cache that stopped caching would be a real regression -- and it is
    invisible to a correctness assertion.
    """
    cre_tags = _stub_tag_sources(monkeypatch)

    first = cre_tags.agreement_table("real", n_artists=10)
    again = cre_tags.agreement_table("real", n_artists=10)

    assert again is first, "the cache stopped caching"


def test_label_scramble_preserves_exactly_which_artists_are_labelled():
    from tas_guard import permuted_labels_among_labelled

    labels = {"a": {"rock"}, "b": {"jazz", "funk"}, "c": set(), "d": {"pop"}}
    out = permuted_labels_among_labelled(labels, seed=20260803)
    assert {k for k, v in out.items() if v} == {k for k, v in labels.items() if v}
    assert sorted(len(v) for v in out.values()) == sorted(
        len(v) for v in labels.values())
