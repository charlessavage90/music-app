"""The fame-currency `known` ramp (`MSW-`, Task 7).

Plain sentence for the whole feature: each press of "know them already" adds a
toll on widely-listened-to artists, so the tenth press pushes much harder
toward the obscure than the first does.

The semantics are copied from the `CRE-` mirror (`cre_mirror.py`), which is the
implementation the blind listen and the coherence audit actually ran on, and
three of its rules are load-bearing rather than incidental:

1. **k is fixed per request.** The number of `known` bypasses is known before
   the search starts, so the ramp is a constant multiplier and not part of the
   search state. Making it depend on path depth would be a different device.
2. **The target endpoint is exempt.** The final hop into B is on every complete
   path exactly once, so tolling it adds the same constant to every
   alternative and distorts nothing — while making the arithmetic harder to
   reason about.
3. **No path moves at k = 0** — `MSW-G2`. The mirror states this as "added only
   when live, never as `+ 0.0`", but that phrasing does not survive contact
   with this file: at k = 0 the multiplier is exactly 0.0, so adding the term
   is *numerically identical* to skipping it. Measured, not assumed — a
   perturbation applying the term unconditionally left every test here green.
   The mirror's rule served byte-identity of serialised probe output, which is
   not this file's problem.

   So `MSW-G2` is a guard against the ramp **firing when it should not** — a
   miscounted press, a stray `max(1, ...)` — and it does discriminate: that
   perturbation turns three of these tests red.

   It only discriminates over a store that CARRIES fame. Measured over the
   fameless fixture it passes whatever the ramp code does, which is how the
   first version of these tests was written and why `_with_fame` exists.
"""

import numpy as np
import pytest

from artistpath_api.config import ApiConfig
from artistpath_api.pathfinding import KNOWN, DISLIKE, Exclusion, find_path

from conftest import make_store


def _store_with_fame(fame_pctl, **kwargs):
    """A 4-node line a-b-c-d, with fame percentiles supplied directly."""
    store = make_store(
        names=["a", "b", "c", "d"],
        pop_raw=[0.5, 0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9)],
        **kwargs,
    )
    store.fame_lb_pctl = np.asarray(fame_pctl, dtype=np.float64)
    return store


def _diamond(fame_pctl):
    """a -> (b | c) -> d, both routes otherwise identical.

    The only thing distinguishing b from c is fame, so the ramp alone decides.
    """
    store = make_store(
        names=["a", "b", "c", "d"],
        pop_raw=[0.5, 0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (1, 3, 0.9), (2, 3, 0.9)],
    )
    store.fame_lb_pctl = np.asarray(fame_pctl, dtype=np.float64)
    return store


def _with_fame(store):
    """The 500-node fixture, given a deterministic spread of fame percentiles.

    MSW-G2 MUST be measured over a store that CARRIES fame. Measured over a
    fameless one it passes no matter what the ramp code does, because the
    term cannot fire either way — verified by perturbation: applying the term
    unconditionally (the `+ 0.0` form the rule forbids) left the fameless
    version of these tests green.
    """
    n = store.artist_count
    store.fame_lb_pctl = np.linspace(0.0, 1.0, n, dtype=np.float64)
    return store


def _pairs():
    for source in range(0, 400, 37):
        for target in range(1, 401, 53):
            if source != target:
                yield source, target


def test_ramp_off_changes_no_path(fixture_store):
    # MSW-G2, first half: fame present, knob off. Every path is the path that
    # shipped.
    store = _with_fame(fixture_store)
    off = ApiConfig(w_known_ramp_fame_pctl=0.0)
    baseline = ApiConfig()
    for source, target in _pairs():
        assert find_path(store, source, target, [], off) == find_path(
            store, source, target, [], baseline
        )


def test_ramp_on_with_no_known_presses_changes_no_path(fixture_store):
    # MSW-G2, the half that matters: fame present AND the knob live, but k = 0.
    # The multiplier is zero, so the term must not be applied at all — this is
    # the case that distinguishes "not added" from "added as + 0.0", and it is
    # only a real test because the store carries fame.
    store = _with_fame(fixture_store)
    hot = ApiConfig(w_known_ramp_fame_pctl=0.03)
    baseline = ApiConfig()
    for source, target in _pairs():
        assert find_path(store, source, target, [], hot) == find_path(
            store, source, target, [], baseline
        )


def test_the_ramp_does_move_paths_on_this_fixture_when_pressed(fixture_store):
    # The red control for the two tests above. If a `known` press changed
    # nothing here either, their green would mean "this fixture is insensitive
    # to the ramp", not "the ramp is correctly inert at k = 0".
    store = _with_fame(fixture_store)
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.5)
    pressed = [Exclusion(node=499, reason=KNOWN)]
    moved = [
        (s, t)
        for s, t in _pairs()
        if find_path(store, s, t, pressed, cfg)
        != find_path(store, s, t, pressed, ApiConfig())
    ]
    assert moved, "the ramp moved no path at all — the gates above prove nothing"


def test_a_known_press_steers_away_from_the_widely_listened_to():
    # b is maximally famous, c maximally obscure; otherwise the two routes are
    # identical. One "know them already" press must route through c.
    store = _diamond([0.0, 1.0, 0.0, 0.0])
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.5)
    path = find_path(store, 0, 3, [Exclusion(node=99, reason=KNOWN)], cfg)
    assert path == [0, 2, 3]


def test_without_the_press_the_famous_route_is_not_penalised():
    # Same graph, no press: the tie is decided by something other than fame,
    # so the ramp is demonstrably what moved the path in the test above.
    store = _diamond([0.0, 1.0, 0.0, 0.0])
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.5)
    assert find_path(store, 0, 3, [], cfg) == find_path(store, 0, 3, [], ApiConfig())


def test_a_dislike_press_does_not_drive_the_ramp():
    # The ramp is the KNOWN device. "Not for me" shapes the path by a different
    # mechanism (a neighbourhood penalty) and must not pick this term up.
    # Disliking the source penalises b and c equally (both are one hop from
    # it), so the avoidance term cannot break the tie — leaving the fame ramp
    # as the only thing that could, and it must not fire.
    store = _diamond([0.0, 1.0, 0.0, 0.0])
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.5)
    with_dislike = find_path(store, 0, 3, [Exclusion(node=0, reason=DISLIKE)], cfg)
    assert with_dislike == find_path(store, 0, 3, [], ApiConfig())


def test_the_ramp_scales_with_the_number_of_known_presses():
    # A weak knob that cannot overcome the fame gap at k=1 must overcome it by
    # k=4: this is the "tenth press pushes harder than the first" property, and
    # without it the device is just a static fame penalty.
    store = _diamond([0.0, 1.0, 0.0, 0.0])
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.02, w_sim=3.0)
    # make the obscure route slightly worse on similarity, so fame has to
    # accumulate before it wins
    store.scores[:] = np.asarray(
        [0.9 if v != 2 else 0.85 for v in store.neighbours], dtype=np.float32
    )
    one = find_path(store, 0, 3, [Exclusion(node=99, reason=KNOWN)], cfg)
    many = find_path(
        store, 0, 3, [Exclusion(node=90 + i, reason=KNOWN) for i in range(8)], cfg
    )
    assert one == [0, 1, 3]
    assert many == [0, 2, 3]


def test_the_target_endpoint_is_exempt_from_the_toll():
    # d is the target and maximally famous. Tolling it would add the same
    # constant to every route, so no press count may make the search avoid it —
    # and it must not become unreachable.
    store = _store_with_fame([0.0, 0.0, 0.0, 1.0])
    cfg = ApiConfig(w_known_ramp_fame_pctl=1.0)
    presses = [Exclusion(node=90 + i, reason=KNOWN) for i in range(20)]
    assert find_path(store, 0, 3, presses, cfg) == [0, 1, 2, 3]


def test_a_fameless_store_ignores_the_ramp_rather_than_crashing():
    # Belt and braces behind app.py's boot refusal: if a fameless store ever
    # reaches the router with the knob on, it must route as it always did
    # rather than raise mid-request in front of a user.
    store = make_store(
        names=["a", "b", "c"],
        pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    assert store.fame_lb_pctl is None
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.5)
    assert find_path(store, 0, 2, [Exclusion(node=99, reason=KNOWN)], cfg) == [0, 1, 2]


def test_the_default_knob_is_the_adopted_value():
    # ADOPTED 2026-08-06 (MSW-) at 0.01 — the CRE- sweep's `P1a` arm, flipped
    # from 0.0 in one commit with cap_strategy and require_fame. This assertion
    # was `== 0.0` until that commit; it is pinned rather than deleted so a
    # silent change to the adopted value is a test failure, not a reroute
    # nobody notices.
    assert ApiConfig().w_known_ramp_fame_pctl == 0.01


# --- boot refusal ----------------------------------------------------------


def test_boot_refuses_the_ramp_over_a_fameless_artifact():
    """A misconfigured artifact must refuse to START, not serve quietly.

    With the ramp on and no fame data, every "know them already" press would
    silently do less than it claims. That failure looks like a weak feature
    rather than a broken one, which is exactly the kind that reaches
    production and stays there.
    """
    from artistpath_api.app import create_app
    from artistpath_api.search import ArtistSearch

    store = make_store(
        names=["a", "b"], pop_raw=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.01)
    with pytest.raises(ValueError, match="fame"):
        create_app(store, ArtistSearch(store, cfg), None, cfg)


def test_boot_allows_the_ramp_over_an_artifact_that_carries_fame():
    # Deliberately built from a BARE ApiConfig() since the MSW- adoption of
    # 2026-08-06: this is now the SHIPPED configuration, so this test is what
    # catches a release that flips the ramp on while shipping a fameless
    # artifact — the one combination create_app refuses.
    from artistpath_api.app import create_app
    from artistpath_api.search import ArtistSearch

    store = make_store(
        names=["a", "b"], pop_raw=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    store.fame_lb_pctl = np.asarray([0.0, 1.0], dtype=np.float64)
    cfg = ApiConfig()
    assert cfg.w_known_ramp_fame_pctl != 0.0  # the default carries the ramp
    assert create_app(store, ArtistSearch(store, cfg), None, cfg) is not None


def test_boot_allows_a_fameless_artifact_while_the_ramp_is_off():
    # The ramp is pinned OFF explicitly. It used to inherit the default, which
    # was 0.0 until the MSW- adoption of 2026-08-06 — after which a bare
    # ApiConfig() over a fameless store is exactly the combination the boot
    # guard refuses, and this test asserted the opposite. Fame-less artifacts
    # remain supported with the ramp off; that is what this pins.
    from artistpath_api.app import create_app
    from artistpath_api.search import ArtistSearch

    store = make_store(
        names=["a", "b"], pop_raw=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    cfg = ApiConfig(w_known_ramp_fame_pctl=0.0)
    assert create_app(store, ArtistSearch(store, cfg), None, cfg) is not None
