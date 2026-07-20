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


def effective_floor(base_floor: float, excludes: list[Exclusion], cfg: ApiConfig) -> float:
    """Soften the obscurity floor as the user keeps bypassing (spec 4.3).

    Each successive bypass lifts the floor globally, letting the path reach
    less famous artists. "Known" relaxes more than "dislike": knowing the
    artists means the popular route is exhausted and novelty is the goal.
    """
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    n_dislike = sum(1 for e in excludes if e.reason == DISLIKE)
    relaxed = base_floor - cfg.floor_relax_known * n_known - cfg.floor_relax_dislike * n_dislike
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
) -> list[int] | None:
    """Least-cost path from source to target under the spec 4.1 cost function.

    A full regeneration every call (spec 4.3): no reuse of any previous path.
    Returns None only if hard exclusions disconnect the two endpoints.
    """
    if source == target:
        return [source]

    # Hard exclusions skip nodes entirely, but never the endpoints themselves.
    hard = {e.node for e in excludes} - {source, target}

    base_floor = min(float(store.popularity[source]), float(store.popularity[target]))
    floor = effective_floor(base_floor, excludes, cfg)
    avoid = avoidance_map(
        store, [e.node for e in excludes if e.reason == DISLIKE], cfg
    )

    dist = {source: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        pop_u = float(store.popularity[u])
        for v, sim in store.neighbours_of(u):
            if v in hard:
                continue
            pop_v = float(store.popularity[v])
            cost = (
                cfg.w_sim * (1.0 - float(sim))
                + cfg.w_jump * abs(pop_u - pop_v)
                + cfg.w_floor * max(0.0, floor - pop_v)
                + cfg.w_avoid * avoid.get(v, 0.0)
                + cfg.w_hop
            )
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
