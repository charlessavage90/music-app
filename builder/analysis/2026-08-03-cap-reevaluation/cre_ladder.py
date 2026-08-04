"""The §0.3 ladder: journey semantics, fame-currency victim rule, uniform drop.

JOURNEY SEMANTICS (dependency (6)): the harness mirrors find_journey, the
function the app actually calls -- a directly-adjacent pair yields a
forced-detour interior rather than vanishing from the record. The committed
`walk` helpers mirror find_path and break on empty interiors; that precedent
silently unread exactly the pairs union arms make adjacent (prereg §9).

The mirror cfg runs with guard_min_intermediary=False here BECAUSE journey()
itself performs the guard's masked re-run (the same mechanism), plus the
adjacent_only fallback the guard lacks. CRE-G1(a) proves the combination
reproduces production find_journey exactly.
"""
from __future__ import annotations

from cre_common import MAX_DEPTH, use_frozen
from cre_mirror import _avoidance_map, _dijkstra, find_path_mirror

use_frozen("api_src")
from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion  # noqa: E402


def journey(store, s, t, excludes, cfg, ctx, stats=None):
    # Pin 8: journey() IS the guard (same masked re-run) plus the
    # adjacent_only fallback the guard lacks; both live at once would turn
    # adjacent-only pairs into None and cascade through the uniform drop.
    assert cfg.guard_min_intermediary is False
    path = find_path_mirror(store, s, t, excludes, cfg, ctx, stats)
    if path is None:
        return None, "none"
    if len(path) != 2:
        return path, "natural"
    hard = {e.node for e in excludes} - {s, t}
    # Production's own predicate (pathfinding.py), not its complement: this is
    # a byte-identity harness, and the two differ the moment a third exclusion
    # reason exists (analyst m16). Identically empty on the all-known ladder.
    avoid = _avoidance_map(store, [e.node for e in excludes
                                   if e.reason == DISLIKE], cfg)
    detour = _dijkstra(store, s, t, hard, avoid, cfg, ctx, excludes,
                       (s, t), stats)
    return (path, "adjacent_only") if detour is None else (detour, "forced")


def victim_key(fame_measured, pop, mbids):
    """Highest fame_lb_pctl first; ruler-null interiors after every measured
    one; ties by pop_raw desc then lowest MBID (§0.3, plan pin 3)."""
    import math

    def key(v: int):
        f = float(fame_measured[v])
        return ((-f) if not math.isnan(f) else 1.0, -float(pop[v]), mbids[v])

    return key


def walk_journey(store, s, t, cfg, ctx, fame_measured, pop, mbids, stats=None):
    """All-`known` journey ladder, depths 0..MAX_DEPTH. Always MAX_DEPTH+1
    entries; infeasible cells are (None, "none"), never a short list."""
    key = victim_key(fame_measured, pop, mbids)
    excludes: list = []
    out: list[tuple[list[int] | None, str]] = []
    for _ in range(MAX_DEPTH + 1):
        path, kind = journey(store, s, t, excludes, cfg, ctx, stats)
        out.append((path, kind))
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break  # adjacent_only: no victim to press
        victim = min(interior, key=key)
        excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
    out.extend([(None, "none")] * (MAX_DEPTH + 1 - len(out)))
    return out


def assert_cost_decomposition(store, ctx, cfg, excludes, path,
                              masked_edge=None, tol=1e-9):
    """CRE-G2(b), the independent form (analyst B1 replaced the first draft,
    which compared the toll formula to itself and could not fail).

    Two clauses, both against references the decomposition does not share:
    (1) the breakdown's TOTAL equals the SEARCH's own accumulated cost for
        this exact path (a fresh deterministic _dijkstra call records
        stats["path_cost"]) -- a wrong k inside the search, a term added or
        omitted inside the search, or a mis-plumbed array all fire here;
    (2) the breakdown's ramp component equals r * k * sum(fame_pctl) over the
        returned interiors -- the prereg's stated formula, now anchored to a
        total that clause (1) has tied to the instrument.
    `masked_edge` replays a forced-detour journey's second search exactly.
    """
    from cre_mirror import term_breakdown

    hard = {e.node for e in excludes} - {path[0], path[-1]}
    avoid = _avoidance_map(store, [e.node for e in excludes
                                   if e.reason == DISLIKE], cfg)
    stats: dict = {"examined": 0, "floor_active": 0}
    replay = _dijkstra(store, path[0], path[-1], hard, avoid, cfg, ctx,
                       excludes, masked_edge, stats)
    if replay != path:
        raise SystemExit("CRE-G2(b) FAILED: replay returned a different path")

    rows = term_breakdown(store, ctx, cfg, excludes, path)
    total = sum(sum(r.values()) for r in rows)
    if abs(total - stats["path_cost"]) > tol:
        raise SystemExit(
            f"CRE-G2(b) FAILED: decomposition {total} != search cost "
            f"{stats['path_cost']}"
        )
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    expected = (cfg.w_known_ramp_fame_pctl * n_known
                * sum(float(ctx.fame_pctl[v]) for v in path[1:-1]))
    got = sum(r["ramp_fame"] for r in rows)
    if abs(got - expected) > tol:
        raise SystemExit(
            f"CRE-G2(b) FAILED: ramp component {got} != r*k*sum(fame) {expected}"
        )
