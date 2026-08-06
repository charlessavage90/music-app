"""Artist-path routing: cost function, Dijkstra, and the two-signal bypass.

Pure over an in-memory GraphStore. No I/O. The cost function is spec section
4.1; the bypass behaviours are spec section 4.3.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore

DISLIKE = "dislike"  # "not for me"
KNOWN = "known"      # "know them already"


@dataclass(frozen=True, slots=True)
class Exclusion:
    node: int
    reason: str  # DISLIKE or KNOWN


def effective_floor_raw(
    base_floor_raw: float, excludes: list[Exclusion], cfg: ApiConfig
) -> float:
    """Soften the obscurity floor as the user keeps bypassing (spec 4.3).

    Each successive bypass lifts the floor globally, letting the path reach
    less famous artists. "Known" relaxes more than "dislike": knowing the
    artists means the popular route is exhausted and novelty is the goal.

    Floor and relaxation are both in RAW popularity units, not percentile —
    a fixed raw step is a very different distance at the top of the
    distribution than in the tail (log §2.12).

    This is also the only depth-graduated device in the cost function:
    everything else is static per request, and only the exclusion set and this
    floor know how many bypasses have happened.
    """
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    n_dislike = sum(1 for e in excludes if e.reason == DISLIKE)
    relaxed = (
        base_floor_raw
        - cfg.floor_relax_known * n_known
        - cfg.floor_relax_dislike * n_dislike
    )
    return max(0.0, relaxed)


def avoidance_map(store: GraphStore, disliked_ids: list[int], cfg: ApiConfig) -> dict[int, float]:
    """Soft penalty on the neighbourhood of each 'not for me' artist (spec 4.3).

    Decays with graph distance, zero beyond cfg.avoid_radius hops. This steers
    the path around a disliked stylistic region instead of offering a
    near-identical substitute.
    """
    penalties: dict[int, float] = {}
    for start in disliked_ids:
        seen = {start}
        frontier = {start}
        for hop in range(1, cfg.avoid_radius + 1):
            nxt: set[int] = set()
            penalty = cfg.avoid_penalty * (cfg.avoid_decay ** (hop - 1))
            for u in frontier:
                for v, _ in store.neighbours_of(u):
                    if v not in seen:
                        seen.add(v)
                        nxt.add(v)
                        penalties[v] = max(penalties.get(v, 0.0), penalty)
            frontier = nxt
    return penalties


def find_path(
    store: GraphStore,
    source: int,
    target: int,
    excludes: list[Exclusion],
    cfg: ApiConfig,
    forbidden_edge: tuple[int, int] | None = None,
) -> list[int] | None:
    """Least-cost path from source to target under the spec 4.1 cost function.

    A full regeneration every call (spec 4.3): no reuse of any previous path.
    Returns None only if hard exclusions disconnect the two endpoints.
    """
    if source == target:
        return [source]

    # Hard exclusions skip nodes entirely, but never the endpoints themselves.
    hard = {e.node for e in excludes} - {source, target}

    # Undirected: forbidding (a, b) must also forbid (b, a). Used to force a
    # detour when the least-cost path is the two chosen artists and nothing
    # else (F1). Empty in the ordinary case, so this costs one set lookup.
    banned: set[tuple[int, int]] = set()
    if forbidden_edge is not None:
        a, b = forbidden_edge
        banned = {(a, b), (b, a)}

    base_floor_raw = min(float(store.pop_raw[source]), float(store.pop_raw[target]))
    floor_raw = effective_floor_raw(base_floor_raw, excludes, cfg)
    avoid = avoidance_map(
        store, [e.node for e in excludes if e.reason == DISLIKE], cfg
    )

    # The fame ramp is a constant multiplier for the whole request: the number
    # of `known` presses is known before the search starts, so it is not part
    # of the search state.
    #
    # `ramp_fame_on` skips the term entirely when it would be zero. Note what
    # that IS and IS NOT worth: at k = 0 the multiplier is exactly 0.0, so
    # `cost += 0.0 * fame` is numerically identical to not adding it, and the
    # guard buys nothing arithmetically — measured, not assumed (a perturbation
    # applying the term unconditionally left every test green). The mirror's
    # "never as + 0.0" rule served byte-identity of serialised probe output,
    # which is not this file's problem. What the guard does buy here is the
    # skipped array lookup per edge, and a single place where "is the ramp
    # live" is decided.
    #
    # MSW-G2 — no path moves at k = 0 — is therefore a guard against the ramp
    # FIRING when it should not (a miscounted k, a stray max(1, ...)), and it
    # discriminates: that perturbation turns three tests red.
    #
    # The store check is a second line behind create_app's boot refusal: a
    # fameless artifact reaching here routes as it always did rather than
    # raising mid-request in front of a user.
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    ramp_fame = cfg.w_known_ramp_fame_pctl * n_known
    ramp_fame_on = ramp_fame != 0.0 and store.fame_lb_pctl is not None

    dist = {source: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        pop_raw_u = float(store.pop_raw[u])
        for v, sim in store.neighbours_of(u):
            if v in hard:
                continue
            if (u, v) in banned:
                continue
            pop_raw_v = float(store.pop_raw[v])
            # Every popularity term here is in RAW currency. A percentile
            # variant is the subject of the Track 2 sweep
            # (specs/2026-07-23-track2-preregistration.md §1.3); if one is
            # adopted, the new quantities carry `pctl` in their names.
            cost = (
                cfg.w_sim * (1.0 - float(sim))
                + cfg.w_jump * abs(pop_raw_u - pop_raw_v)
                + cfg.w_floor * max(0.0, floor_raw - pop_raw_v)
                + cfg.w_avoid * avoid.get(v, 0.0)
                + cfg.w_degree_hub * float(store.degree_hub_penalty[v])
                + cfg.w_hop
            )
            # Fame-currency `known` ramp, semantics preserved from the CRE-
            # mirror the blind listen and coherence audit actually ran on:
            # relaxation targets only, and the TARGET ENDPOINT IS EXEMPT
            # because the final hop into B is on every complete path exactly
            # once — tolling it adds the same constant to every alternative and
            # distorts nothing. Added only when live; see ramp_fame_on above.
            if ramp_fame_on and v != target:
                cost += ramp_fame * float(store.fame_lb_pctl[v])
            nd = d + cost
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if target not in prev:
        return None
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1]


# How a journey came to have (or lack) an artist between its two endpoints.
# The frontend cannot re-derive this: once a stop is forced in, the result is
# indistinguishable from an ordinary path. Requirement and success condition:
# docs/superpowers/2026-07-25-gate1-clips-and-ux-execution-log.md section 16.
STOP_NATURAL = "natural"              # the least-cost path already had a stop
STOP_FORCED = "forced"                # the two are neighbours; a stop was inserted
STOP_ADJACENT_ONLY = "adjacent_only"  # neighbours, and nothing connects them both


def find_journey(
    store: GraphStore,
    source: int,
    target: int,
    excludes: list[Exclusion],
    cfg: ApiConfig,
) -> tuple[list[int], str] | None:
    """A path with at least one artist between the endpoints where possible.

    Every journey needs at least one stop (owner's decision, 2026-07-25). When
    the least-cost path is the two chosen artists and nothing else, search again
    with their direct connection forbidden; the same cost function chooses the
    detour, so no new scoring is introduced and this stays outside the paused
    path-quality work.

    Some pairs cannot be given a stop at all: some artists hold a single
    connection in the graph (findings/2026-07-25-mutual-knn-stranding.md,
    MKS-3), so their one neighbour has no route back except that connection
    (same document, MKS-6, for the resulting pair-level count). Those fall
    back to the two-card path and say so rather than returning nothing,
    because a no-path result must only ever come from user exclusions.

    The second search re-reads the same exclusions, so a stop is never forced
    through an artist the user has already rejected.
    """
    path = find_path(store, source, target, excludes, cfg)
    if path is None:
        return None
    if len(path) != 2:
        # Includes the degenerate source == target case, which is length 1.
        return path, STOP_NATURAL

    detour = find_path(
        store, source, target, excludes, cfg, forbidden_edge=(source, target)
    )
    if detour is None:
        return path, STOP_ADJACENT_ONLY
    return detour, STOP_FORCED
