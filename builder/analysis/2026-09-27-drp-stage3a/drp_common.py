"""Shared pieces for the DRP- stage-3a instruments. Decides nothing on its own.

Governing document: docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md
(`DRP-`), §4 (pairs and the ladder), §5 (criteria), §6 (gates), §8 stage 3a. Execute-from-body
convention since `DRP-AM5`: every rule below cites the body section it implements.

Sealing (§8, binding on 3a-3d): no committed output names an interior artist. Per-journey outputs
hold node ids only. Endpoint names may appear. Anything name-bearing beyond endpoints is written
under OUT (outside the repository), and only its sha256 is committed.

Every script here routes with the SHIPPED `artistpath_api.pathfinding.find_journey`, loaded from
this worktree's `api/src`, asserted unchanged after importing `cre_ladder.victim_key`
(graph-descriptives' module-identity asserts, carried by §4).
"""
from __future__ import annotations

import hashlib
import heapq
import json
import random
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # this worktree
sys.path.insert(0, str(ROOT / "api" / "src"))

# ---- pinned inputs (read-only) -----------------------------------------------------------------
A0_GRAPH = Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin")
A0_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
GD_OUT = ROOT / "builder/analysis/2026-09-27-issue-200-graph-descriptives/graph_descriptives.out.txt"

# ---- outputs outside the repository (gitignored state never enters this tree) ------------------
OUT = Path(r"C:\unsung-fast\drp-stage3a")
S1_GRAPH = OUT / "graph-drp-s1.bin"

# ---- §4: draw rule -----------------------------------------------------------------------------
DRP_SEED = 20260928
GD_SEED = 20260927
N_PAIRS = 40
STRATA = (  # (identifier, lo, hi, hi_inclusive)
    ("DRP-T1", 0.99, 1.0, True),
    ("DRP-T2", 0.95, 0.99, False),
    ("DRP-MID", 0.30, 0.70, True),
)
FAMOUS = ("DRP-T1", "DRP-T2")
MAX_K = 20
BAND = (7, 8, 9, 10)

# ---- §5 / §6 constants, carried, never tuned ---------------------------------------------------
INSTRUMENT_FLOOR = 0.015
G6_BAR = 0.025
BOOT_SEED = 20260928
BOOT_N = 10_000


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def refuse(msg: str, code: int = 2) -> None:
    print(f"REFUSING: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def verify(path: Path, expect: str) -> str:
    """sha256 must equal the sidecar's top-level `sha256` and the pin, before anything is read."""
    got = sha256_of(path)
    side = json.loads(path.with_name(path.name + ".json").read_text(encoding="utf-8"))["sha256"]
    if not (got == side == expect):
        refuse(f"{path.name} sha256 {got}; sidecar {side}; pin {expect}")
    print(f"sha256 OK  {path.name}  {got} (== sidecar == pin)", flush=True)
    return got


# ---- shipped router, identity-asserted ---------------------------------------------------------
from artistpath_api import pathfinding as _pf_mod  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402,F401
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import (  # noqa: E402,F401
    DISLIKE, KNOWN, Exclusion, avoidance_map, effective_floor_raw, find_journey)

_API_SRC = (ROOT / "api" / "src").resolve()
PF_FILE = Path(_pf_mod.__file__).resolve()
assert _API_SRC in PF_FILE.parents, f"pathfinding loaded from {PF_FILE}, not {_API_SRC}"
sys.path.insert(0, str(ROOT / "builder/analysis/2026-08-03-cap-reevaluation"))
from cre_ladder import victim_key  # noqa: E402  -- ONLY victim_key is used (§4)

assert Path(sys.modules["artistpath_api.pathfinding"].__file__).resolve() == PF_FILE
assert sys.modules["artistpath_api.pathfinding"].find_journey is find_journey
CEILING = "ceiling"  # DRP-P3's third reason string (§2.1); unused at stage 3a except by G10


def raw_fame(payload: bytes, n: int) -> list:
    """`fame_lb` straight from the APG1 metadata blob (graph_descriptives.py's cursor arithmetic)."""
    header = struct.Struct("<4sIIIQ")
    magic, _v, hn, e, meta_len = header.unpack_from(payload)
    assert magic == b"APG1" and hn == n
    cursor = header.size + (hn + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor: cursor + meta_len])
    fame = meta.get("fame_lb")
    assert fame is not None and len(fame) == n, "artifact carries no/short fame_lb"
    return fame


class Map:
    """One routed map: the shipped GraphStore plus the arrays every instrument reads."""

    def __init__(self, path: Path, expect_sha: str) -> None:
        self.sha = verify(path, expect_sha)
        payload = path.read_bytes()
        self.store = GraphStore.from_bytes(payload)
        self.n = self.store.artist_count
        self.fame = raw_fame(payload, self.n)
        del payload
        self.pctl = np.asarray(self.store.fame_lb_pctl, dtype=np.float64)
        if not np.array_equal(self.pctl, GraphStore.fame_percentiles(self.fame)):
            refuse(f"{path.name}: store fame_lb_pctl != fame_percentiles(raw fame_lb)", 3)
        self.measured = np.array([v is not None for v in self.fame], dtype=bool)
        self.mbids = list(self.store.mbids)
        # victim_key reads NaN at nulls (graph-descriptives, jfx_g1a_reverify); the ceiling and
        # DRP-C11 read the shipped pctl with nulls at 0.0 (DRP-AM5-O2).
        self.key = victim_key(np.where(self.measured, self.pctl, np.nan),
                              self.store.pop_raw, self.store.mbids)
        self.distinct = np.unique(self.pctl)
        self.off = self.store.offsets.tolist()
        self.nbr = self.store.neighbours.tolist()
        self.pl = self.pctl.tolist()

    def interior_median(self, path) -> float:
        vals = [self.pl[v] for v in path[1:-1] if self.measured[v]]
        return float(np.median(vals)) if vals else float("nan")


# ---- §4: the pair draw -------------------------------------------------------------------------
def draw(rng: random.Random, pool: list[int], n: int = N_PAIRS) -> list[tuple[int, int]]:
    """rng.sample(pool, 2) as (source, target); a repeated unordered pair is rejected."""
    seen, out = set(), []
    while len(out) < n:
        s, t = rng.sample(pool, 2)
        k = frozenset((s, t))
        if k in seen:
            continue
        seen.add(k)
        out.append((s, t))
    return out


def stratum_pool(m: Map, lo: float, hi: float, hi_incl: bool) -> list[int]:
    ids = np.arange(m.n)
    upper = (m.pctl <= hi) if hi_incl else (m.pctl < hi)
    return [int(i) for i in ids[m.measured & (m.pctl >= lo) & upper]]


def replication_pairs(m: Map) -> list[tuple[int, int]]:
    """graph-descriptives' own FAMOUS draw (seed 20260927, both >= 0.95), by its script's rule.

    Its MID draw is consumed from the same generator afterwards; returned too, for DRP-G1.
    """
    ids = np.arange(m.n)
    famous_pool = [int(i) for i in ids[m.measured & (m.pctl >= 0.95)]]
    mid_pool = [int(i) for i in ids[m.measured & (m.pctl >= 0.30) & (m.pctl <= 0.70)]]
    rng = random.Random(GD_SEED)
    fam = draw(rng, famous_pool)
    mid = draw(rng, mid_pool)
    return fam, mid


# ---- §4: the ladder ----------------------------------------------------------------------------
def ladder(m: Map, cfg, s: int, t: int, rule: str, rng: random.Random | None = None,
           max_k: int = MAX_K) -> list:
    """Presses 0..max_k, every press KNOWN, exclusions cumulative.

    Returns one entry per depth reached: (path as node ids | None, stop rule). The ladder stops
    after a None journey or an empty interior (§4's drop rule reads both).
    rule "primary": victim = min(interiors, key=victim_key). rule "random": victim =
    interiors[rng.randrange(len(interiors))], interiors in path order, nulls eligible (§4).
    """
    ex: list = []
    out = []
    for _k in range(max_k + 1):
        res = find_journey(m.store, s, t, ex, cfg)
        if res is None:
            out.append((None, "none"))
            break
        path, stop = res
        out.append((list(path), stop))
        interior = path[1:-1]
        if not interior:
            break
        if rule == "primary":
            victim = min(interior, key=m.key)
        elif rule == "random":
            victim = interior[rng.randrange(len(interior))]
        else:
            raise ValueError(rule)
        ex = ex + [Exclusion(node=victim, reason=KNOWN)]
    return out


def feasible(lad: list, k: int) -> bool:
    """§4: (pair, depth) infeasible if the journey is None, has no interior, or the ladder stopped."""
    return k < len(lad) and lad[k][0] is not None and len(lad[k][0]) > 2


def random_rng(s: int, stratum: str, i: int) -> random.Random:
    """§4: one instance per (seed, stratum, pair), created once, consumed across the presses."""
    return random.Random(f"DRP:{s}:{stratum}:{i}")


# ---- DRP-C11: the headroom instrument's own minimax search -------------------------------------
def bottleneck(m: Map, s: int, t: int, excl: set[int]) -> float:
    """Smallest possible highest-interior fame_lb_pctl over every s-t path with >= 1 interior.

    Direct s-t edge forbidden (exactly the journeys find_journey can return with a stop),
    endpoints exempt, nodes in `excl` removed, nulls at 0.0 (the shipped frame, DRP-AM5-O2).
    Its own heap search; never calls find_journey (DRP-G9(d)'s independence). inf if none.
    Same algorithm as the stage-1 critique's probe (drp_ceiling_probe.py), whose b0 passed an
    independent BFS check on 80 of 80 pairs.
    """
    off, nbr, pl = m.off, m.nbr, m.pl
    excl = set(excl) - {s, t}
    best: dict[int, float] = {}
    pq: list = []
    for w in nbr[off[s]:off[s + 1]]:
        if w == t or w in excl:
            continue
        lw = pl[w]
        if lw < best.get(w, 2.0):
            best[w] = lw
            heapq.heappush(pq, (lw, w))
    done: set[int] = set()
    while pq:
        lu, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        row = nbr[off[u]:off[u + 1]]
        for w in row:
            if w == t:
                return lu  # u != s by construction; the first popped neighbour of t is optimal
        for w in row:
            if w == s or w in excl or w in done:
                continue
            lw = lu if lu >= pl[w] else pl[w]
            if lw < best.get(w, 2.0):
                best[w] = lw
                heapq.heappush(pq, (lw, w))
    return float("inf")


def ceiling_excludes(m: Map, c: float, s: int, t: int) -> list:
    """§2.1 DRP-P3: every interior with fame_lb_pctl > c, strictly, endpoints exempt."""
    over = np.flatnonzero(m.pctl > c)
    return [Exclusion(node=int(v), reason=CEILING) for v in over if v != s and v != t]


def f_max(k: int) -> float:
    """§2.1 DRP-P3 schedule, float64."""
    return 1.0 if k <= 3 else max(0.0, 1.0 - 0.015 * (k - 3))


def write_json(path: Path, obj) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
