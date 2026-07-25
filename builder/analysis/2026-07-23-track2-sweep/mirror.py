"""A parameterised mirror of production `find_path`, for the Track 2 Stage A sweep.

**No shipped code is edited before adoption** (pre-registration §1.2), so the sweep's
knobs live here. `SweepConfig.production()` must reproduce `api.pathfinding.find_path`
**byte-identically** — that is the gate in `verify_mirror.py`, and log §3.10 says a
non-identical path means stop, the harness is wrong.

Byte-identity is a stronger requirement than "same algorithm", so three things are
deliberate rather than incidental:

1. **The cost terms are summed in production's order.** Floating-point addition is not
   associative; reordering these six terms can change the last bit of a cost and so
   change which of two near-equal paths wins.
2. **Optional terms are added only when active**, never as `+ 0.0`, so the production
   configuration executes the identical expression.
3. **The heap entries are `(cost, node)` exactly as production**, so ties break on node
   id the same way, and neighbours are visited in CSR order.

Knobs implemented, per pre-registration §1.3–§1.4 as amended:
  J-cur  `jump_currency`  raw | pctl (mean-matched by default — amendment A3)
  J-mag  `w_jump`
  S-mag  `w_sim`
  F      `floor_mode`     raw | pctl | off, with the pctl relax constant from A2
  toll   `toll_s`         additive toll on score-1.0 edges (amendment A1)
         `toll_hops`      the same toll in multiples of `w_hop` (Track 2F)
  guard  `guard_min_intermediary`  guard G (§4); OFF for the verification step
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, replace

import numpy as np

from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion

RAW = "raw"
PCTL = "pctl"
OFF = "off"


@dataclass(frozen=True, slots=True)
class SweepConfig:
    # --- production cost weights (ApiConfig defaults; cited, not re-derived) ---
    w_sim: float = 3.0
    w_jump: float = 1.0
    w_floor: float = 1.0
    w_hop: float = 0.02
    w_avoid: float = 1.0
    w_degree_hub: float = 0.0

    # --- production bypass shaping, RAW currency ---
    floor_relax_known: float = 0.15
    floor_relax_dislike: float = 0.08
    avoid_penalty: float = 0.5
    avoid_decay: float = 0.5
    avoid_radius: int = 2

    # --- sweep knobs ---
    jump_currency: str = RAW
    # Amendment A3: the pctl level is mean-matched by definition, so J-cur is a genuine
    # one-column contrast. Arm A1u sets this False to expose the scale component.
    jump_mean_match: bool = True

    floor_mode: str = RAW
    # Amendment A2: pre-registered HERE, deliberately not read from ApiConfig — reusing
    # the shipped 0.15 is exactly what left the FL arms inert at every scored depth.
    floor_relax_known_pctl: float = 0.05
    # NOT pre-registered: Stage A is all-`known`, so this is only reachable by the §1.5
    # F4 dislike walk. Chosen to preserve production's dislike:known relax ratio.
    floor_relax_dislike_pctl: float = 0.05 * (0.08 / 0.15)

    # Amendment A1: additive toll on ceiling-saturated edges. None = off.
    # Active toll magnitude is w_sim * (1 - toll_s).
    toll_s: float | None = None
    # Track 2F: the SAME knob, specified in the currency §1.4 pre-registered it in.
    # `toll_s` is w_sim-dependent, so one value means two different tolls under two
    # different W -- which is exactly what A17(b) caught after the fact, §1.4's
    # 7.5x/30x figures having been quoted for an S-mag of 3.0 while W carried 1.5.
    # This names its own basis and is w_sim-independent: toll = toll_hops * w_hop.
    # Mutually exclusive with toll_s; None = off, so production is untouched.
    #
    # NB for reproduction arms: the two specifications are NOT bit-identical at the
    # same nominal magnitude (1.5*(1-0.80) = 0.29999999999999993 against
    # 15*0.02 = 0.30000000000000004), so an arm reproducing a committed toll_s run
    # must keep toll_s. Track 2F pre-registration §4, run order step 3.
    toll_hops: float | None = None

    def __post_init__(self) -> None:
        if self.toll_s is not None and self.toll_hops is not None:
            raise ValueError(
                "toll_s and toll_hops are two specifications of one knob; set one. "
                f"got toll_s={self.toll_s}, toll_hops={self.toll_hops}"
            )

    # Guard G (§4). OFF for mirror verification, then enabled uniformly (G5a).
    guard_min_intermediary: bool = False

    @classmethod
    def production(cls) -> "SweepConfig":
        """The configuration that must reproduce shipped `find_path` exactly."""
        return cls()

    def with_(self, **kw) -> "SweepConfig":
        return replace(self, **kw)


@dataclass(frozen=True, slots=True)
class MirrorContext:
    """Artifact-derived quantities, computed once per run."""

    pctl: np.ndarray          # float64, average-rank percentile (P6)
    jump_scale_pctl: float    # mean|dpop_raw| / mean|dpctl| over all directed edges

    @classmethod
    def build(cls, store: GraphStore) -> "MirrorContext":
        n = len(store.mbids)
        pop = np.asarray(store.pop_raw, dtype=np.float64)

        # P6: average rank over N, ties averaged. Deterministic; np.argsort alone
        # is order-dependent among ties.
        order = np.argsort(pop, kind="stable")
        ranks = np.empty(n, dtype=np.float64)
        srt = pop[order]
        i = 0
        while i < n:
            j = i
            while j + 1 < n and srt[j + 1] == srt[i]:
                j += 1
            ranks[order[i : j + 1]] = (i + j) / 2.0
            i = j + 1
        pctl = ranks / (n - 1)

        src = np.repeat(np.arange(n, dtype=np.int64), np.diff(store.offsets))
        dst = np.asarray(store.neighbours, dtype=np.int64)
        mean_raw = float(np.abs(pop[src] - pop[dst]).mean())
        mean_pctl = float(np.abs(pctl[src] - pctl[dst]).mean())
        return cls(pctl=pctl, jump_scale_pctl=mean_raw / mean_pctl)


def _relaxed_floor(base: float, excludes: list[Exclusion], relax_known: float,
                   relax_dislike: float) -> float:
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    n_dislike = sum(1 for e in excludes if e.reason == DISLIKE)
    return max(0.0, base - relax_known * n_known - relax_dislike * n_dislike)


def _avoidance_map(store: GraphStore, disliked: list[int], cfg: SweepConfig) -> dict[int, float]:
    penalties: dict[int, float] = {}
    for start in disliked:
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


def _dijkstra(
    store: GraphStore,
    source: int,
    target: int,
    hard: set[int],
    avoid: dict[int, float],
    cfg: SweepConfig,
    ctx: MirrorContext,
    excludes: list[Exclusion],
    masked_edge: tuple[int, int] | None,
    stats: dict[str, int] | None = None,
) -> list[int] | None:
    use_pctl_jump = cfg.jump_currency == PCTL
    w_jump_eff = cfg.w_jump
    if use_pctl_jump and cfg.jump_mean_match:
        w_jump_eff = cfg.w_jump * ctx.jump_scale_pctl

    floor_val = 0.0
    floor_on = cfg.floor_mode != OFF
    if floor_on:
        if cfg.floor_mode == PCTL:
            base = min(float(ctx.pctl[source]), float(ctx.pctl[target]))
            floor_val = _relaxed_floor(base, excludes, cfg.floor_relax_known_pctl,
                                       cfg.floor_relax_dislike_pctl)
        else:
            base = min(float(store.pop_raw[source]), float(store.pop_raw[target]))
            floor_val = _relaxed_floor(base, excludes, cfg.floor_relax_known,
                                       cfg.floor_relax_dislike)

    toll_on = cfg.toll_s is not None or cfg.toll_hops is not None
    if cfg.toll_hops is not None:
        toll = cfg.toll_hops * cfg.w_hop
    elif cfg.toll_s is not None:
        toll = cfg.w_sim * (1.0 - cfg.toll_s)
    else:
        toll = 0.0

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
        pctl_u = float(ctx.pctl[u])
        for v, sim in store.neighbours_of(u):
            if v in hard:
                continue
            if masked_edge is not None and u == masked_edge[0] and v == masked_edge[1]:
                continue
            pop_raw_v = float(store.pop_raw[v])
            pctl_v = float(ctx.pctl[v])

            jump = abs(pctl_u - pctl_v) if use_pctl_jump else abs(pop_raw_u - pop_raw_v)
            if not floor_on:
                floor_pen = 0.0
            elif cfg.floor_mode == PCTL:
                floor_pen = max(0.0, floor_val - pctl_v)
            else:
                floor_pen = max(0.0, floor_val - pop_raw_v)

            if stats is not None:
                stats["examined"] += 1
                if floor_pen > 0.0:
                    stats["floor_active"] += 1

            # Production's term order, preserved exactly — see module docstring.
            cost = (
                cfg.w_sim * (1.0 - float(sim))
                + w_jump_eff * jump
                + cfg.w_floor * floor_pen
                + cfg.w_avoid * avoid.get(v, 0.0)
                + cfg.w_degree_hub * float(store.degree_hub_penalty[v])
                + cfg.w_hop
            )
            if toll_on and float(sim) >= 1.0:
                cost += toll

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


def find_path_mirror(
    store: GraphStore,
    source: int,
    target: int,
    excludes: list[Exclusion],
    cfg: SweepConfig,
    ctx: MirrorContext,
    stats: dict[str, int] | None = None,
) -> list[int] | None:
    """Least-cost path under `cfg`. With `SweepConfig.production()`, byte-identical
    to `api.pathfinding.find_path`."""
    if source == target:
        return [source]

    hard = {e.node for e in excludes} - {source, target}
    avoid = _avoidance_map(store, [e.node for e in excludes if e.reason == DISLIKE], cfg)

    path = _dijkstra(store, source, target, hard, avoid, cfg, ctx, excludes, None, stats)

    # Guard G (§4): a journey has at least one stop. Exclusions are node-based and
    # cannot forbid an edge, so mask the direct edge and re-run. Only the
    # source->target direction is masked: a shortest path to `target` cannot use the
    # reverse direction, since the search stops when `target` is popped.
    if cfg.guard_min_intermediary and path is not None and len(path) == 2:
        path = _dijkstra(store, source, target, hard, avoid, cfg, ctx, excludes,
                         (source, target), stats)

    return path
