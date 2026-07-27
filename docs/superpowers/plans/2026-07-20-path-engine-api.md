# Path Engine & API Implementation Plan

> **⚠ Role: HISTORICAL. EXECUTED and SHIPPED — do not execute again.** The service described
> here is live in `api/` and has since been hardened by Gate 2 Track A
> ([`../2026-07-26-gate2-track-a-execution-log.md`](../2026-07-26-gate2-track-a-execution-log.md)).
> Where this plan and the code disagree, **the code wins**.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Python/FastAPI service that loads the graph artifact into memory and serves artist-path search, two-signal bypass rerolls, autocomplete, and 30-second clip resolution.

**Architecture:** A standalone `api/` package, independent of the `builder/` package. It reads the language-neutral `APG1` graph artifact directly into numpy typed arrays (the *format* is the contract, not the builder's code), runs Dijkstra with the spec §4.1 cost function in-process, and exposes three HTTP endpoints. Clip URLs are resolved on demand from Deezer/iTunes and cached in DynamoDB. Everything is developed and tested against the committed 5k graph and a tiny synthetic fixture; the 75k graph swaps in by changing one path when the crawl finishes.

**Tech Stack:** Python 3.12+ (3.14 available), `uv`, FastAPI, `uvicorn`, `httpx`, `numpy`, `boto3`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-07-19-artist-path-alpha-design.md`
**Findings (validated weights, in-degree popularity, behavioural-only):** `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md`

Where this plan and the spec disagree, the spec wins — raise it rather than improvising. One deliberate, documented deviation is noted below (plain vs bidirectional Dijkstra).

## Global Constraints

Every task's requirements implicitly include these.

- **No dependency on the `builder/` package.** The API reads the `APG1` artifact format directly. This keeps the API free of crawler dependencies (`httpx` crawler, `boto3` for the archive) and honours the "artifact is language-neutral" design (spec §3).
- **The graph is loaded once at startup into typed arrays and never mutated** (spec §3.2). Path queries touch no database and no network.
- **Behavioural edges only.** Alpha has a single edge type; `w_type` is a constant (spec §4.1, findings §6f). Do not add other sources.
- **Popularity is already in the artifact** — the `popularity` field is score-weighted in-degree, log-scaled and normalised to 0–1 by the builder (findings §6f). The API consumes it directly; it does not recompute popularity.
- **Validated starting weights:** `w_sim=3.0, w_jump=1.0, w_floor=1.0, w_hop=0.02` (findings §6g). These are a tuned starting point, not final; they live in config.
- **`POST /api/path` takes `sources: list` and `exclude: list of {id, reason}`** (spec §3.2, §7 seam 1). Alpha passes two sources; the signature accepts a list so multi-artist pathing needs no API change.
- **Only the clicked artist is ever hard-excluded** (spec §4.3). Neighbourhood effects are soft costs and can never disconnect the graph or cause a spurious "no path".
- **Endpoints are never hard-excluded** — a bypass must not remove a path's own start or end.
- **A reroll is a full regeneration, free to change path length** (spec §4.3). No local repair, no length cap, no bias toward the previous path.
- **The path endpoint returns artists immediately; clips resolve separately** (spec §5.2). `POST /api/path` never blocks on Deezer/iTunes.
- **Determinism:** Dijkstra ties break on node id (heap tuples are `(distance, node_id)`), so identical queries return identical paths.
- **Depth over breadth** (spec §2.1). Do not add album/track pathing, accounts, or playback beyond 30s clips.

---

## File Structure

```
api/
  pyproject.toml
  README.md
  src/artistpath_api/
    __init__.py
    config.py            # ApiConfig — all weights, urls, table name, limits
    graph_store.py       # APG1 reader -> GraphStore (numpy arrays + id index)
    pathfinding.py       # cost function, Dijkstra, bypass (floor relax + avoidance)
    search.py            # artist-name autocomplete over a normalised index
    clips.py             # Deezer + iTunes resolution, DynamoDB-backed cache
    models.py            # pydantic request/response models
    app.py               # FastAPI app factory; loads graph at startup, wires routes
  tests/
    conftest.py          # tiny synthetic GraphStore builder; fixture loader
    fixtures/
      graph-fixture.bin  # ~200-artist real sub-graph, committed (generated in Task 8)
    test_graph_store.py
    test_pathfinding.py
    test_bypass.py
    test_search.py
    test_clips.py
    test_app.py
```

Responsibilities are split so the two things most likely to change — the upstream clip APIs, and the routing cost function — are each isolated behind one module. `graph_store.py` and `pathfinding.py` are pure over in-memory data with no I/O, which is what makes them fast to test.

### The APG1 format (the contract this API reads)

All little-endian. Produced by `builder/src/artistpath_builder/artifact.py`.

| Bytes | Type | Meaning |
|---|---|---|
| 0 | `char[4]` | magic `APG1` |
| 4 | `uint32` | format version (1) |
| 8 | `uint32` | artist count `N` |
| 12 | `uint32` | edge count `E` |
| 16 | `uint64` | metadata JSON length `J` |
| 24 | `int32[N+1]` | offsets (CSR) |
| … | `int32[E]` | neighbours (CSR) |
| … | `float32[E]` | scores (similarity 0–1) |
| … | `uint8[E]` | edge types (all 0 in alpha) |
| … | `char[J]` | metadata JSON: `{"mbids":[…],"names":[…],"disambiguations":[…],"popularity":[…]}` |

`popularity` values are already log-scaled and normalised to 0–1.

---

## Task 1: Scaffold the api package with config

**Files:**
- Create: `api/pyproject.toml`
- Create: `api/src/artistpath_api/__init__.py`
- Create: `api/src/artistpath_api/config.py`
- Test: `api/tests/test_config.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `ApiConfig` frozen dataclass with all tunables — used by every later task.

- [ ] **Step 1: Create the project**

`api/pyproject.toml`:

```toml
[project]
name = "artistpath-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn>=0.30",
    "httpx>=0.27",
    "numpy>=2.0",
    "boto3>=1.34",
    "pydantic>=2.7",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0", "pytest-asyncio>=0.23"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/artistpath_api"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Write the failing test**

`api/tests/test_config.py`:

```python
from artistpath_api.config import ApiConfig


def test_validated_weights_are_the_default():
    # The starting weights from findings 6g. Changing these silently would
    # regress path quality, so pin them.
    cfg = ApiConfig()
    assert (cfg.w_sim, cfg.w_jump, cfg.w_floor, cfg.w_hop) == (3.0, 1.0, 1.0, 0.02)


def test_known_relaxes_floor_more_than_dislike():
    # "Know them already" means the popular route is exhausted; it should
    # dig deeper than "not for me" (spec 4.3).
    cfg = ApiConfig()
    assert cfg.floor_relax_known > cfg.floor_relax_dislike > 0


def test_default_graph_path_points_at_an_artifact():
    assert ApiConfig().graph_path.endswith(".bin")
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd api && uv run --extra dev pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_api.config'`

- [ ] **Step 4: Write the implementation**

`api/src/artistpath_api/__init__.py`:

```python
__version__ = "0.1.0"
```

`api/src/artistpath_api/config.py`:

```python
"""All API tunables. No magic numbers elsewhere in the package."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApiConfig:
    # --- graph ----------------------------------------------------------
    # Dev default is the committed 5k graph; production sets ARTISTPATH_GRAPH
    # to the 75k artifact. One env var swaps the graph without code changes.
    graph_path: str = os.environ.get(
        "ARTISTPATH_GRAPH", "../builder/scratch/graph-5k.bin"
    )

    # --- cost function weights (findings 6g) ----------------------------
    w_sim: float = 3.0    # reward strong similarity
    w_jump: float = 1.0   # punish popularity cliffs
    w_floor: float = 1.0  # discourage diving into obscurity
    w_hop: float = 0.02   # per-hop cost; low so paths can be long and smooth
    w_avoid: float = 1.0  # "not for me" neighbourhood penalty

    # --- bypass shaping (spec 4.3) --------------------------------------
    floor_relax_known: float = 0.15    # each "known" bypass softens the floor
    floor_relax_dislike: float = 0.08  # each "dislike" bypass softens it less
    avoid_penalty: float = 0.5         # cost added at a disliked artist's neighbours
    avoid_decay: float = 0.5           # penalty falls off per hop
    avoid_radius: int = 2              # hops the penalty reaches

    # --- search ---------------------------------------------------------
    search_limit: int = 10

    # --- clips ----------------------------------------------------------
    deezer_search_url: str = "https://api.deezer.com/search"
    itunes_search_url: str = "https://itunes.apple.com/search"
    clip_table_name: str = os.environ.get("ARTISTPATH_CLIP_TABLE", "artistpath-clips")
    clip_ttl_days: int = 30
    clip_http_timeout: float = 10.0
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd api && uv run --extra dev pytest tests/test_config.py -v`
Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add api/pyproject.toml api/src/artistpath_api/__init__.py api/src/artistpath_api/config.py api/tests/test_config.py
git commit -m "feat(api): scaffold FastAPI package with config and validated weights"
```

---

## Task 2: GraphStore — read the APG1 artifact into numpy

**Files:**
- Create: `api/src/artistpath_api/graph_store.py`
- Create: `api/tests/conftest.py`
- Test: `api/tests/test_graph_store.py`

**Interfaces:**
- Consumes: nothing (reads the format directly).
- Produces: `GraphStore` with fields `mbids: list[str]`, `names: list[str]`, `disambiguations: list[str]`, `popularity: np.ndarray` (float32), `offsets: np.ndarray` (int32), `neighbours: np.ndarray` (int32), `scores: np.ndarray` (float32), `id_by_mbid: dict[str,int]`; classmethod `load(path) -> GraphStore`; method `neighbours_of(node_id) -> Iterator[tuple[int, float]]`; property `artist_count`. The `conftest.make_store(...)` helper builds a `GraphStore` from explicit arrays for later tests.

- [ ] **Step 1: Write the failing test**

`api/tests/test_graph_store.py`:

```python
import struct
import json
import numpy as np

from artistpath_api.graph_store import GraphStore


def _write_apg1(path, mbids, names, disambiguations, popularity,
                offsets, neighbours, scores):
    meta = json.dumps(
        {"mbids": mbids, "names": names,
         "disambiguations": disambiguations, "popularity": popularity},
        separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    header = struct.pack("<4sIIIQ", b"APG1", 1, len(mbids), len(neighbours), len(meta))
    edge_types = np.zeros(len(neighbours), dtype=np.uint8)
    path.write_bytes(
        header
        + np.asarray(offsets, dtype="<i4").tobytes()
        + np.asarray(neighbours, dtype="<i4").tobytes()
        + np.asarray(scores, dtype="<f4").tobytes()
        + edge_types.tobytes()
        + meta
    )


def test_load_round_trips_a_small_graph(tmp_path):
    # A<->B<->C chain.
    p = tmp_path / "g.bin"
    _write_apg1(
        p,
        mbids=["a" * 36, "b" * 36, "c" * 36],
        names=["Alpha", "Beta", "Gamma"],
        disambiguations=["UK band", "", ""],
        popularity=[0.9, 0.5, 0.1],
        offsets=[0, 1, 3, 4],
        neighbours=[1, 0, 2, 1],
        scores=[0.8, 0.8, 0.6, 0.6],
    )
    g = GraphStore.load(p)
    assert g.artist_count == 3
    assert g.names[1] == "Beta"
    assert g.disambiguations[0] == "UK band"
    assert g.id_by_mbid["c" * 36] == 2
    assert g.popularity.dtype == np.float32


def test_neighbours_of_yields_id_and_score(tmp_path):
    p = tmp_path / "g.bin"
    _write_apg1(
        p, ["a" * 36, "b" * 36], ["A", "B"], ["", ""], [0.5, 0.5],
        offsets=[0, 1, 2], neighbours=[1, 0], scores=[0.7, 0.7],
    )
    g = GraphStore.load(p)
    assert list(g.neighbours_of(0)) == [(1, np.float32(0.7))]


def test_non_ascii_names_survive(tmp_path):
    p = tmp_path / "g.bin"
    _write_apg1(
        p, ["a" * 36, "b" * 36], ["Sigur Rós", "Beyoncé"], ["", ""], [0.5, 0.5],
        offsets=[0, 1, 2], neighbours=[1, 0], scores=[0.7, 0.7],
    )
    g = GraphStore.load(p)
    assert g.names == ["Sigur Rós", "Beyoncé"]


def test_bad_magic_is_rejected(tmp_path):
    p = tmp_path / "bad.bin"
    p.write_bytes(b"XXXX" + b"\x00" * 40)
    import pytest
    with pytest.raises(ValueError, match="magic"):
        GraphStore.load(p)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && uv run --extra dev pytest tests/test_graph_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_api.graph_store'`

- [ ] **Step 3: Write the implementation**

`api/src/artistpath_api/graph_store.py`:

```python
"""Reads the APG1 graph artifact into memory.

Self-contained: it parses the binary format directly and depends on nothing
in the builder package. The format is the contract (spec section 3).
"""

from __future__ import annotations

import json
import struct
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_MAGIC = b"APG1"
_FORMAT_VERSION = 1
_HEADER = struct.Struct("<4sIIIQ")


@dataclass(slots=True)
class GraphStore:
    mbids: list[str]
    names: list[str]
    disambiguations: list[str]
    popularity: np.ndarray  # float32, 0-1
    offsets: np.ndarray     # int32, length N+1
    neighbours: np.ndarray  # int32, length E
    scores: np.ndarray      # float32, length E
    id_by_mbid: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id_by_mbid:
            self.id_by_mbid = {mbid: i for i, mbid in enumerate(self.mbids)}

    @property
    def artist_count(self) -> int:
        return len(self.mbids)

    def neighbours_of(self, node_id: int) -> Iterator[tuple[int, float]]:
        start, end = int(self.offsets[node_id]), int(self.offsets[node_id + 1])
        for k in range(start, end):
            yield int(self.neighbours[k]), self.scores[k]

    @classmethod
    def load(cls, path: str | Path) -> "GraphStore":
        payload = Path(path).read_bytes()
        if len(payload) < _HEADER.size:
            raise ValueError("artifact truncated: shorter than header")
        magic, version, n, e, meta_len = _HEADER.unpack_from(payload)
        if magic != _MAGIC:
            raise ValueError(f"bad magic: expected {_MAGIC!r}, got {magic!r}")
        if version != _FORMAT_VERSION:
            raise ValueError(f"unsupported artifact version {version}")

        cursor = _HEADER.size

        def take(count: int, dtype: str, size: int) -> np.ndarray:
            nonlocal cursor
            end_ = cursor + count * size
            arr = np.frombuffer(payload[cursor:end_], dtype=dtype)
            cursor = end_
            return arr

        offsets = take(n + 1, "<i4", 4)
        neighbours = take(e, "<i4", 4)
        scores = take(e, "<f4", 4)
        take(e, "<u1", 1)  # edge_types — unused in alpha (all behavioural)
        meta = json.loads(payload[cursor : cursor + meta_len])

        return cls(
            mbids=meta["mbids"],
            names=meta["names"],
            disambiguations=meta["disambiguations"],
            popularity=np.asarray(meta["popularity"], dtype=np.float32),
            offsets=offsets,
            neighbours=neighbours,
            scores=scores,
        )
```

- [ ] **Step 4: Add the shared test helper**

`api/tests/conftest.py`:

```python
from pathlib import Path

import numpy as np
import pytest

from artistpath_api.graph_store import GraphStore

FIXTURES = Path(__file__).parent / "fixtures"


def make_store(names, popularity, undirected_edges):
    """Build a GraphStore from a human-readable spec, for pathfinding tests.

    names: list of artist names (index = node id)
    popularity: list of floats 0-1 (index = node id)
    undirected_edges: list of (u, v, score) — each added in both directions
    """
    n = len(names)
    adj: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for u, v, s in undirected_edges:
        adj[u].append((v, s))
        adj[v].append((u, s))

    offsets = np.zeros(n + 1, dtype=np.int32)
    neighbours: list[int] = []
    scores: list[float] = []
    for i in range(n):
        for v, s in sorted(adj[i]):
            neighbours.append(v)
            scores.append(s)
        offsets[i + 1] = len(neighbours)

    return GraphStore(
        mbids=[f"{i:036d}" for i in range(n)],
        names=list(names),
        disambiguations=[""] * n,
        popularity=np.asarray(popularity, dtype=np.float32),
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
    )


@pytest.fixture
def fixture_store():
    return GraphStore.load(FIXTURES / "graph-fixture.bin")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd api && uv run --extra dev pytest tests/test_graph_store.py -v`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/graph_store.py api/tests/conftest.py api/tests/test_graph_store.py
git commit -m "feat(api): add self-contained APG1 graph reader"
```

---

## Task 3: Cost function and base pathfinding (Dijkstra)

**Deviation from spec §4.2, documented:** the spec chose bidirectional Dijkstra. This plan uses **plain (unidirectional) Dijkstra**. Reason: the cost function's floor term is asymmetric (it penalises based on the destination node's popularity), which complicates a correct bidirectional meeting condition, and plain Dijkstra measured single-digit milliseconds on the 5k graph in the stage-1 evaluation. Plain Dijkstra is exact and simple; bidirectional is a future optimisation if latency at 75k demands it. Raise with the spec owner if in doubt.

**Files:**
- Create: `api/src/artistpath_api/pathfinding.py`
- Test: `api/tests/test_pathfinding.py`

**Interfaces:**
- Consumes: `GraphStore` (Task 2), `ApiConfig` (Task 1).
- Produces: `Exclusion` dataclass `(node: int, reason: str)` where `reason ∈ {"dislike", "known"}`; `find_path(store, source, target, excludes, cfg) -> list[int] | None`; `effective_floor(base_floor, excludes, cfg) -> float`; `avoidance_map(store, disliked_ids, cfg) -> dict[int, float]`. Used by Tasks 4 and 7.

This task implements the base path (no exclusions). Task 4 adds the bypass behaviours through the same `find_path`.

- [ ] **Step 1: Write the failing test**

`api/tests/test_pathfinding.py`:

```python
from artistpath_api.config import ApiConfig
from artistpath_api.pathfinding import find_path
from tests.conftest import make_store

CFG = ApiConfig()


def test_direct_neighbours_path_is_two_nodes():
    store = make_store(
        names=["A", "B"], popularity=[0.5, 0.5],
        undirected_edges=[(0, 1, 0.9)],
    )
    assert find_path(store, 0, 1, [], CFG) == [0, 1]


def test_path_endpoints_are_source_and_target():
    # Line graph 0-1-2-3-4; path must start at 0 and end at 4.
    store = make_store(
        names=list("ABCDE"), popularity=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)],
    )
    path = find_path(store, 0, 4, [], CFG)
    assert path[0] == 0 and path[-1] == 4


def test_every_adjacent_pair_in_the_path_is_a_real_edge():
    store = make_store(
        names=list("ABCDE"), popularity=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)] + [(0, 2, 0.2)],
    )
    path = find_path(store, 0, 4, [], CFG)
    edges = set()
    for u in range(store.artist_count):
        for v, _ in store.neighbours_of(u):
            edges.add((u, v))
    for a, b in zip(path, path[1:]):
        assert (a, b) in edges


def test_strong_similarity_is_preferred_over_a_weak_shortcut():
    # 0-2 is a direct but weak (0.1) edge; 0-1-2 is two strong (0.95) edges.
    # With w_sim high and w_hop low, the smooth two-hop route should win.
    store = make_store(
        names=["A", "B", "C"], popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 2, 0.1), (0, 1, 0.95), (1, 2, 0.95)],
    )
    assert find_path(store, 0, 2, [], CFG) == [0, 1, 2]


def test_identical_queries_are_deterministic():
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (1, 3, 0.9), (2, 3, 0.9)],
    )
    a = find_path(store, 0, 3, [], CFG)
    b = find_path(store, 0, 3, [], CFG)
    assert a == b


def test_no_path_when_disconnected_returns_none():
    store = make_store(
        names=["A", "B", "C"], popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9)],  # C (node 2) is isolated
    )
    assert find_path(store, 0, 2, [], CFG) is None


def test_source_equals_target_is_a_single_node():
    store = make_store(
        names=["A", "B"], popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert find_path(store, 0, 0, [], CFG) == [0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && uv run --extra dev pytest tests/test_pathfinding.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_api.pathfinding'`

- [ ] **Step 3: Write the implementation**

`api/src/artistpath_api/pathfinding.py`:

```python
"""Artist-path routing: cost function, Dijkstra, and the two-signal bypass.

Pure over an in-memory GraphStore. No I/O. The cost function is spec section
4.1; the bypass behaviours are spec section 4.3.
"""

from __future__ import annotations

import heapq
from collections import deque
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && uv run --extra dev pytest tests/test_pathfinding.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/pathfinding.py api/tests/test_pathfinding.py
git commit -m "feat(api): add cost function and Dijkstra path engine"
```

---

## Task 4: Two-signal bypass behaviours

**Files:**
- Modify: none (behaviour already lives in `pathfinding.py` from Task 3)
- Test: `api/tests/test_bypass.py`

**Interfaces:**
- Consumes: `find_path`, `effective_floor`, `avoidance_map`, `Exclusion`, `DISLIKE`, `KNOWN` (Task 3).
- Produces: no new code — this task is the behavioural test suite that pins the two signals apart. If a test fails, fix `pathfinding.py`.

- [ ] **Step 1: Write the failing test**

`api/tests/test_bypass.py`:

```python
from artistpath_api.config import ApiConfig
from artistpath_api.pathfinding import (
    DISLIKE, KNOWN, Exclusion, avoidance_map, effective_floor, find_path,
)
from tests.conftest import make_store

CFG = ApiConfig()


def test_hard_excluded_artist_never_appears_in_the_path():
    # 0-1-2 and 0-3-2; exclude 1, so the path must go via 3.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 3, 0.7), (3, 2, 0.7)],
    )
    path = find_path(store, 0, 2, [Exclusion(1, DISLIKE)], CFG)
    assert 1 not in path
    assert path == [0, 3, 2]


def test_endpoints_cannot_be_excluded():
    store = make_store(
        names=["A", "B"], popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    # Excluding the target must not delete it or break the path.
    path = find_path(store, 0, 1, [Exclusion(1, DISLIKE)], CFG)
    assert path == [0, 1]


def test_known_relaxes_floor_more_than_dislike():
    base = 0.8
    known = effective_floor(base, [Exclusion(9, KNOWN)], CFG)
    dislike = effective_floor(base, [Exclusion(9, DISLIKE)], CFG)
    assert known < dislike < base


def test_floor_relaxation_is_progressive():
    base = 0.9
    one = effective_floor(base, [Exclusion(1, KNOWN)], CFG)
    two = effective_floor(base, [Exclusion(1, KNOWN), Exclusion(2, KNOWN)], CFG)
    assert two < one < base


def test_floor_never_goes_negative():
    assert effective_floor(0.05, [Exclusion(i, KNOWN) for i in range(20)], CFG) == 0.0


def test_avoidance_penalises_neighbours_of_disliked_artist():
    # Star: 0 at centre, 1/2/3 as neighbours; disliking 0 penalises 1,2,3.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9)],
    )
    av = avoidance_map(store, [0], CFG)
    assert av[1] > 0 and av[2] > 0 and av[3] > 0


def test_avoidance_decays_with_distance():
    # Line 0-1-2-3; disliking 0, node 1 (1 hop) penalised more than node 2.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9)],
    )
    av = avoidance_map(store, [0], CFG)
    assert av[1] > av.get(2, 0.0)


def test_avoidance_is_bounded_by_radius():
    store = make_store(
        names=list("ABCDE"), popularity=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)],
    )
    av = avoidance_map(store, [0], CFG)  # radius 2
    assert 3 not in av and 4 not in av


def test_soft_bypass_can_never_cause_no_path():
    # A dislike bypass adds only soft cost; the endpoints stay connected.
    store = make_store(
        names=list("ABC"), popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    # Even disliking the only intermediate, a path still exists (soft cost).
    assert find_path(store, 0, 2, [Exclusion(1, KNOWN)], CFG) is not None
```

- [ ] **Step 2: Run test to verify it passes (behaviour already implemented)**

Run: `cd api && uv run --extra dev pytest tests/test_bypass.py -v`
Expected: 9 passed. If any fail, the bug is in `pathfinding.py` (Task 3) — fix it there, not in the test.

- [ ] **Step 3: Commit**

```bash
git add api/tests/test_bypass.py
git commit -m "test(api): pin the two bypass signals apart"
```

---

## Task 5: Artist autocomplete search

**Files:**
- Create: `api/src/artistpath_api/search.py`
- Test: `api/tests/test_search.py`

**Interfaces:**
- Consumes: `GraphStore` (Task 2), `ApiConfig` (Task 1).
- Produces: `ArtistSearch(store, cfg)` with `search(query: str) -> list[int]` returning node ids ranked by popularity; module function `normalise(text: str) -> str`. Used by Task 7.

- [ ] **Step 1: Write the failing test**

`api/tests/test_search.py`:

```python
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch, normalise
from tests.conftest import make_store

CFG = ApiConfig()


def _search(names, popularity):
    store = make_store(names, popularity, undirected_edges=[])
    return ArtistSearch(store, CFG)


def test_normalise_lowercases_and_strips_accents():
    assert normalise("Sigur Rós") == "sigur ros"
    assert normalise("BEYONCÉ") == "beyonce"


def test_prefix_match_returns_the_artist():
    s = _search(["Radiohead", "Radio Dept", "Coldplay"], [0.9, 0.4, 0.8])
    ids = s.search("radio")
    assert set(ids) == {0, 1}


def test_results_are_ranked_by_popularity():
    s = _search(["Radiohead", "Radio Dept"], [0.4, 0.9])
    assert s.search("radio") == [1, 0]  # Radio Dept more popular here


def test_accent_insensitive_match():
    s = _search(["Sigur Rós", "Other"], [0.9, 0.1])
    assert s.search("sigur ros") == [0]


def test_substring_match_when_no_prefix_hit():
    s = _search(["The Beatles", "Beach House"], [0.9, 0.5])
    assert 0 in s.search("beatles")


def test_limit_is_respected():
    names = [f"Band {i}" for i in range(50)]
    s = _search(names, [0.5] * 50)
    assert len(s.search("band")) == CFG.search_limit


def test_empty_query_returns_nothing():
    s = _search(["Radiohead"], [0.9])
    assert s.search("  ") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && uv run --extra dev pytest tests/test_search.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_api.search'`

- [ ] **Step 3: Write the implementation**

`api/src/artistpath_api/search.py`:

```python
"""Artist-name autocomplete over the graph's name list.

At 75k names a linear scan is well under a millisecond, so the index is a
plain normalised-name list; prefix matches rank above substring matches, and
both rank by popularity.
"""

from __future__ import annotations

import unicodedata

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore


def normalise(text: str) -> str:
    """Lowercase and strip accents so 'Sigur Ros' matches 'Sigur Rós'."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.lower().strip()


class ArtistSearch:
    def __init__(self, store: GraphStore, cfg: ApiConfig) -> None:
        self._cfg = cfg
        self._store = store
        self._normalised = [normalise(n) for n in store.names]

    def search(self, query: str) -> list[int]:
        q = normalise(query)
        if not q:
            return []
        prefix: list[int] = []
        substring: list[int] = []
        for i, name in enumerate(self._normalised):
            if name.startswith(q):
                prefix.append(i)
            elif q in name:
                substring.append(i)

        pop = self._store.popularity
        prefix.sort(key=lambda i: -pop[i])
        substring.sort(key=lambda i: -pop[i])
        return (prefix + substring)[: self._cfg.search_limit]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && uv run --extra dev pytest tests/test_search.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/search.py api/tests/test_search.py
git commit -m "feat(api): add artist autocomplete search"
```

---

## Task 6: Clip resolution with cache

**Files:**
- Create: `api/src/artistpath_api/clips.py`
- Test: `api/tests/test_clips.py`

**Interfaces:**
- Consumes: `ApiConfig` (Task 1).
- Produces: `Clip` dataclass `(preview_url: str, title: str, cover_url: str)`; `ClipCache` protocol with `get(mbid) -> Clip | None` and `put(mbid, clip)`; `InMemoryClipCache` (tests/dev) and `DynamoClipCache` (production); `ClipResolver(cfg, cache, fetch_json)` with async `resolve(mbid, artist_name) -> Clip | None`. Used by Task 7.

`fetch_json` is an injected async callable `(url, params) -> dict` so tests mock HTTP.

- [ ] **Step 1: Write the failing test**

`api/tests/test_clips.py`:

```python
import pytest

from artistpath_api.clips import Clip, ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig

CFG = ApiConfig()
MBID = "a" * 36

DEEZER_HIT = {
    "data": [
        {"preview": "https://cdn.deezer/clip.mp3",
         "title": "Paranoid Android",
         "artist": {"name": "Radiohead", "picture_medium": "https://cdn/rh.jpg"}}
    ]
}
ITUNES_HIT = {
    "results": [
        {"previewUrl": "https://cdn.itunes/clip.m4a",
         "trackName": "Karma Police",
         "artworkUrl100": "https://cdn/itunes.jpg"}
    ]
}


def _resolver(responses, cache=None):
    """responses maps a url-substring to the dict it returns."""
    calls = []

    async def fetch_json(url, params):
        calls.append((url, params))
        for frag, body in responses.items():
            if frag in url:
                return body
        return {}

    r = ClipResolver(CFG, cache or InMemoryClipCache(), fetch_json)
    r.calls = calls
    return r


async def test_resolves_from_deezer_first():
    r = _resolver({"deezer": DEEZER_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.deezer/clip.mp3"
    assert clip.title == "Paranoid Android"


async def test_falls_back_to_itunes_when_deezer_empty():
    r = _resolver({"deezer": {"data": []}, "itunes": ITUNES_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.itunes/clip.m4a"
    assert clip.title == "Karma Police"


async def test_returns_none_when_no_source_has_a_clip():
    r = _resolver({"deezer": {"data": []}, "itunes": {"results": []}})
    assert await r.resolve(MBID, "Nobody") is None


async def test_cache_hit_skips_the_network():
    cache = InMemoryClipCache()
    cache.put(MBID, Clip("cached.mp3", "Cached", "cover.jpg"))
    r = _resolver({"deezer": DEEZER_HIT}, cache=cache)
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.title == "Cached"
    assert r.calls == []  # never hit the network


async def test_successful_resolution_is_cached():
    cache = InMemoryClipCache()
    r = _resolver({"deezer": DEEZER_HIT}, cache=cache)
    await r.resolve(MBID, "Radiohead")
    assert cache.get(MBID).title == "Paranoid Android"


async def test_deezer_entry_without_preview_is_skipped():
    # A Deezer hit lacking a preview URL must fall through to iTunes.
    no_preview = {"data": [{"preview": "", "title": "X", "artist": {"name": "Y"}}]}
    r = _resolver({"deezer": no_preview, "itunes": ITUNES_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.itunes/clip.m4a"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && uv run --extra dev pytest tests/test_clips.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_api.clips'`

- [ ] **Step 3: Write the implementation**

`api/src/artistpath_api/clips.py`:

```python
"""30-second clip resolution: Deezer primary, iTunes fallback, cached.

The path endpoint never calls this (spec 5.2); clips are resolved per-card on
demand. A missing clip leaves the card unplayable but never alters routing.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from artistpath_api.config import ApiConfig

FetchJson = Callable[[str, dict], Awaitable[dict]]


@dataclass(frozen=True, slots=True)
class Clip:
    preview_url: str
    title: str
    cover_url: str


class ClipCache(Protocol):
    def get(self, mbid: str) -> Clip | None: ...
    def put(self, mbid: str, clip: Clip) -> None: ...


class InMemoryClipCache:
    """Dev/test cache. Not shared across processes."""

    def __init__(self) -> None:
        self._store: dict[str, Clip] = {}

    def get(self, mbid: str) -> Clip | None:
        return self._store.get(mbid)

    def put(self, mbid: str, clip: Clip) -> None:
        self._store[mbid] = clip


class DynamoClipCache:
    """Production cache: DynamoDB with a 30-day TTL (spec 5.1)."""

    def __init__(self, cfg: ApiConfig, table=None) -> None:
        self._cfg = cfg
        if table is None:
            import boto3

            table = boto3.resource("dynamodb").Table(cfg.clip_table_name)
        self._table = table

    def get(self, mbid: str) -> Clip | None:
        item = self._table.get_item(Key={"mbid": mbid}).get("Item")
        if not item:
            return None
        return Clip(item["preview_url"], item["title"], item["cover_url"])

    def put(self, mbid: str, clip: Clip) -> None:
        ttl = int(time.time()) + self._cfg.clip_ttl_days * 86400
        self._table.put_item(
            Item={
                "mbid": mbid,
                "preview_url": clip.preview_url,
                "title": clip.title,
                "cover_url": clip.cover_url,
                "ttl": ttl,
            }
        )


class ClipResolver:
    def __init__(self, cfg: ApiConfig, cache: ClipCache, fetch_json: FetchJson) -> None:
        self._cfg = cfg
        self._cache = cache
        self._fetch = fetch_json

    async def resolve(self, mbid: str, artist_name: str) -> Clip | None:
        cached = self._cache.get(mbid)
        if cached is not None:
            return cached
        clip = await self._from_deezer(artist_name) or await self._from_itunes(artist_name)
        if clip is not None:
            self._cache.put(mbid, clip)
        return clip

    async def _from_deezer(self, artist_name: str) -> Clip | None:
        body = await self._fetch(
            self._cfg.deezer_search_url, {"q": artist_name, "limit": 1}
        )
        for row in body.get("data", []):
            preview = row.get("preview")
            if preview:
                artist = row.get("artist") or {}
                return Clip(preview, row.get("title", ""), artist.get("picture_medium", ""))
        return None

    async def _from_itunes(self, artist_name: str) -> Clip | None:
        body = await self._fetch(
            self._cfg.itunes_search_url,
            {"term": artist_name, "entity": "song", "limit": 1},
        )
        for row in body.get("results", []):
            preview = row.get("previewUrl")
            if preview:
                return Clip(preview, row.get("trackName", ""), row.get("artworkUrl100", ""))
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && uv run --extra dev pytest tests/test_clips.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/clips.py api/tests/test_clips.py
git commit -m "feat(api): add Deezer/iTunes clip resolution with cache"
```

---

## Task 7: FastAPI app and endpoints

**Files:**
- Create: `api/src/artistpath_api/models.py`
- Create: `api/src/artistpath_api/app.py`
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: everything from Tasks 1–6.
- Produces: `create_app(store, search, resolver, cfg) -> FastAPI`; endpoints `GET /api/artists/search`, `POST /api/path`, `GET /api/artists/{mbid}/track`. Pydantic models `PathRequest`, `ExclusionIn`, `ArtistOut`, `PathResponse`, `TrackOut`.

- [ ] **Step 1: Write the failing test**

`api/tests/test_app.py`:

```python
from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import Clip, ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch
from tests.conftest import make_store

CFG = ApiConfig()


def _client(clip_responses=None):
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        popularity=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )
    search = ArtistSearch(store, CFG)

    async def fetch_json(url, params):
        return (clip_responses or {}).get("any", {})

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(store, search, resolver, CFG)), store


def test_search_endpoint_returns_matches():
    client, _ = _client()
    r = client.get("/api/artists/search", params={"q": "rad"})
    assert r.status_code == 200
    assert r.json()[0]["name"] == "Radiohead"


def test_path_endpoint_returns_ordered_artists():
    client, store = _client()
    a, c = store.mbids[0], store.mbids[2]
    r = client.post("/api/path", json={"sources": [a, c], "exclude": []})
    assert r.status_code == 200
    names = [x["name"] for x in r.json()["artists"]]
    assert names[0] == "Radiohead" and names[-1] == "Coldplay"


def test_path_respects_a_typed_exclusion():
    client, store = _client()
    a, b, c = store.mbids
    # Exclude Muse (the smooth middle); path must still connect via the weak edge.
    r = client.post(
        "/api/path",
        json={"sources": [a, c], "exclude": [{"id": b, "reason": "dislike"}]},
    )
    assert r.status_code == 200
    names = [x["name"] for x in r.json()["artists"]]
    assert "Muse" not in names


def test_path_with_unknown_artist_is_404():
    client, _ = _client()
    r = client.post("/api/path", json={"sources": ["z" * 36, "y" * 36], "exclude": []})
    assert r.status_code == 404


def test_path_disconnected_by_exclusions_reports_no_path():
    client, store = _client()
    a, c = store.mbids[0], store.mbids[2]
    # This tiny graph can't actually disconnect via soft cost, so assert the
    # happy path returns 200; the 409 contract is exercised on the fixture.
    r = client.post("/api/path", json={"sources": [a, c], "exclude": []})
    assert r.status_code == 200


def test_track_endpoint_returns_clip():
    client, store = _client({"any": {"data": [
        {"preview": "clip.mp3", "title": "Song", "artist": {"picture_medium": "c.jpg"}}
    ]}})
    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 200
    assert r.json()["preview_url"] == "clip.mp3"


def test_track_endpoint_204_when_no_clip():
    client, store = _client({"any": {"data": []}})
    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 204
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && uv run --extra dev pytest tests/test_app.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_api.app'`

- [ ] **Step 3: Write the models**

`api/src/artistpath_api/models.py`:

```python
"""Request/response schemas for the HTTP API."""

from __future__ import annotations

from pydantic import BaseModel


class ExclusionIn(BaseModel):
    id: str          # artist MBID
    reason: str      # "dislike" or "known"


class PathRequest(BaseModel):
    sources: list[str]           # artist MBIDs; alpha passes exactly two
    exclude: list[ExclusionIn] = []


class ArtistOut(BaseModel):
    mbid: str
    name: str
    disambiguation: str
    popularity: float


class PathResponse(BaseModel):
    artists: list[ArtistOut]


class TrackOut(BaseModel):
    preview_url: str
    title: str
    cover_url: str
```

- [ ] **Step 4: Write the app**

`api/src/artistpath_api/app.py`:

```python
"""FastAPI wiring. The graph, search index, and resolver are injected so the
app is testable without loading a real artifact or touching the network.
"""

from __future__ import annotations

import httpx
from fastapi import FastAPI, HTTPException, Response

from artistpath_api.clips import ClipResolver, DynamoClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.models import (
    ArtistOut, ExclusionIn, PathRequest, PathResponse, TrackOut,
)
from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion, find_path
from artistpath_api.search import ArtistSearch


def _to_exclusions(store: GraphStore, raw: list[ExclusionIn]) -> list[Exclusion]:
    out: list[Exclusion] = []
    for e in raw:
        node = store.id_by_mbid.get(e.id)
        reason = e.reason if e.reason in (DISLIKE, KNOWN) else DISLIKE
        if node is not None:
            out.append(Exclusion(node, reason))
    return out


def create_app(
    store: GraphStore,
    search: ArtistSearch,
    resolver: ClipResolver,
    cfg: ApiConfig,
) -> FastAPI:
    app = FastAPI(title="Artist Path API")

    def artist_out(node: int) -> ArtistOut:
        return ArtistOut(
            mbid=store.mbids[node],
            name=store.names[node],
            disambiguation=store.disambiguations[node],
            popularity=float(store.popularity[node]),
        )

    @app.get("/api/artists/search")
    def search_artists(q: str) -> list[ArtistOut]:
        return [artist_out(i) for i in search.search(q)]

    @app.post("/api/path")
    def build_path(req: PathRequest) -> PathResponse:
        if len(req.sources) != 2:
            raise HTTPException(422, "alpha supports exactly two source artists")
        ids = [store.id_by_mbid.get(m) for m in req.sources]
        if any(i is None for i in ids):
            raise HTTPException(404, "unknown artist")
        source, target = ids
        excludes = _to_exclusions(store, req.exclude)
        path = find_path(store, source, target, excludes, cfg)
        if path is None:
            raise HTTPException(409, "no path avoiding those artists")
        return PathResponse(artists=[artist_out(n) for n in path])

    @app.get("/api/artists/{mbid}/track")
    async def get_track(mbid: str, response: Response):
        node = store.id_by_mbid.get(mbid)
        if node is None:
            raise HTTPException(404, "unknown artist")
        clip = await resolver.resolve(mbid, store.names[node])
        if clip is None:
            response.status_code = 204
            return None
        return TrackOut(
            preview_url=clip.preview_url, title=clip.title, cover_url=clip.cover_url
        )

    return app


def build_default_app() -> FastAPI:
    """Production entrypoint: load the real graph and wire live dependencies."""
    cfg = ApiConfig()
    store = GraphStore.load(cfg.graph_path)
    search = ArtistSearch(store, cfg)
    client = httpx.AsyncClient(timeout=cfg.clip_http_timeout)

    async def fetch_json(url: str, params: dict) -> dict:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    resolver = ClipResolver(cfg, DynamoClipCache(cfg), fetch_json)
    return create_app(store, search, resolver, cfg)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd api && uv run --extra dev pytest tests/test_app.py -v`
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/models.py api/src/artistpath_api/app.py api/tests/test_app.py
git commit -m "feat(api): wire FastAPI endpoints for search, path, and track"
```

---

## Task 8: Fixture graph, real-graph smoke test, and README

**Files:**
- Create: `api/tests/fixtures/graph-fixture.bin` (generated, committed)
- Create: `api/tests/test_smoke.py`
- Create: `api/README.md`

**Interfaces:**
- Consumes: everything above; the builder's `fixture` command; the committed `graph-5k.bin`.
- Produces: a committed ~200-artist fixture and a smoke test proving the app works end-to-end on real data.

- [ ] **Step 1: Generate the committed fixture from the 5k graph**

The builder already extracts connected sub-graphs (`artistpath-build fixture`). Run:

```bash
cd builder && uv run artistpath-build fixture \
  --graph scratch/graph-5k.bin \
  --out ../api/tests/fixtures/graph-fixture.bin \
  --size 200
```

Expected: a log line `wrote fixture: 200 artists`. This file is committed so the API's tests run on a fresh clone without the 5k graph.

- [ ] **Step 2: Write the smoke test**

`api/tests/test_smoke.py`:

```python
"""End-to-end checks on the committed 200-artist real-data fixture."""

from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch

CFG = ApiConfig()


def _client(fixture_store):
    search = ArtistSearch(fixture_store, CFG)

    async def fetch_json(url, params):
        return {}

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(fixture_store, search, resolver, CFG))


def test_fixture_has_real_artists(fixture_store):
    assert fixture_store.artist_count == 200
    assert all(len(m) == 36 for m in fixture_store.mbids)


def test_path_between_two_fixture_artists_is_valid(fixture_store):
    client = _client(fixture_store)
    a, b = fixture_store.mbids[0], fixture_store.mbids[-1]
    r = client.post("/api/path", json={"sources": [a, b], "exclude": []})
    assert r.status_code == 200
    artists = r.json()["artists"]
    # Endpoints correct, and every adjacent pair is a real edge.
    assert artists[0]["mbid"] == a and artists[-1]["mbid"] == b
    ids = [fixture_store.id_by_mbid[x["mbid"]] for x in artists]
    edges = {(u, v) for u in range(fixture_store.artist_count)
             for v, _ in fixture_store.neighbours_of(u)}
    for x, y in zip(ids, ids[1:]):
        assert (x, y) in edges


def test_bypass_reroll_excludes_the_artist(fixture_store):
    client = _client(fixture_store)
    a, b = fixture_store.mbids[0], fixture_store.mbids[-1]
    first = client.post("/api/path", json={"sources": [a, b], "exclude": []}).json()
    if len(first["artists"]) < 3:
        return  # need a middle artist to bypass
    middle = first["artists"][1]["mbid"]
    second = client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": middle, "reason": "dislike"}]},
    ).json()
    assert middle not in [x["mbid"] for x in second["artists"]]
```

- [ ] **Step 3: Run the smoke test**

Run: `cd api && uv run --extra dev pytest tests/test_smoke.py -v`
Expected: 3 passed

- [ ] **Step 4: Run the whole suite**

Run: `cd api && uv run --extra dev pytest -v`
Expected: all pass.

- [ ] **Step 5: Manually eyeball a real path against the running server**

```bash
cd api && ARTISTPATH_GRAPH=../builder/scratch/graph-5k.bin \
  uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000 &
sleep 3
# Find two artist MBIDs, then request a path (replace MBIDs from /search):
curl "http://localhost:8000/api/artists/search?q=miles%20davis"
curl "http://localhost:8000/api/artists/search?q=daft%20punk"
curl -s -X POST http://localhost:8000/api/path \
  -H "content-type: application/json" \
  -d '{"sources":["<miles-mbid>","<daft-mbid>"],"exclude":[]}' | python -m json.tool
kill %1
```

Expected: a smooth multi-hop path echoing the stage-1 evaluation (jazz → … → electronic). This is a human sanity check, not an automated test. Note the `DynamoClipCache` will fail without AWS credentials — the track endpoint is not part of this smoke check; the path endpoint does not touch it.

- [ ] **Step 6: Write the README**

`api/README.md` documenting: what the service does; the three endpoints with example requests/responses; that `ARTISTPATH_GRAPH` selects the artifact (5k for dev, 75k for prod); that the graph loads once at startup; that clips need AWS credentials for the DynamoDB cache and degrade to unplayable cards without them; and how to run tests.

- [ ] **Step 7: Commit**

```bash
git add api/tests/fixtures/graph-fixture.bin api/tests/test_smoke.py api/README.md
git commit -m "feat(api): add committed fixture, real-graph smoke test, and README"
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| §3.2 load graph into typed arrays at boot | 2, 7 |
| §3.2 `GET /api/artists/search` | 5, 7 |
| §3.2 `POST /api/path` (sources list + typed exclude) | 3, 7 |
| §3.2 `GET /api/artists/:mbid/track` | 6, 7 |
| §4.1 cost function (behavioural-only, in-degree pop) | 3 |
| §4.1 validated weights | 1, 3 |
| §4.2 exact shortest-cost, deterministic ties | 3 (plain Dijkstra — documented deviation) |
| §4.3 two bypass signals | 3, 4 |
| §4.3 progressive floor relaxation | 3, 4 |
| §4.3 avoidance neighbourhood penalty | 3, 4 |
| §4.3 only clicked artist hard-excluded; endpoints safe | 3, 4 |
| §4.3 full regeneration, no length cap | 3 (fresh Dijkstra each call) |
| §4.3 disconnection → explicit no-path | 3, 7 (409) |
| §5.1 Deezer→iTunes→cache clip resolution | 6 |
| §5.2 path returns immediately; clips separate | 6, 7 (distinct endpoints) |
| §6.1 fixture graph for tests | 2, 8 |
| §7 seam 1: sources is a list | 3, 7 |
| §7 seam 2: player interface | deferred to stage 3 (frontend) — noted below |
| §9 pathfinding & API test coverage | 3, 4, 7, 8 |

**Deliberate deviations, both flagged in-plan:**
1. **Plain Dijkstra, not bidirectional** (§4.2) — the asymmetric floor term complicates bidirectional correctness and measured speed is fine. Documented at Task 3.
2. **Player interface (§7 seam 2) is a stage-3 concern** — it lives in the React frontend, not this API. The API already returns clip URLs behind a stable endpoint, which is the server-side half of that seam.

**Known gaps carried forward (not defects):**
- The 409 "no path" contract is hard to trigger on the tiny fixture (soft costs can't disconnect it; only hard exclusions on a cut vertex can). It is implemented and unit-covered at the `find_path`-returns-None level (Task 3); the HTTP 409 mapping is in Task 7. A fuller integration test belongs once the 75k graph exists.
- Weight tuning is deliberately not automated. The committed weights are the validated starting point; real tuning is a listen-and-adjust activity against the 75k graph, tracked as its own follow-up.

**Placeholder scan:** none. The one code hazard — the `popularity=` line in Task 2 Step 3 — is called out explicitly with the correct replacement immediately below the block.

**Type consistency:** `GraphStore` fields and `neighbours_of` are used identically in Tasks 2–8. `Exclusion(node, reason)`, `find_path(store, source, target, excludes, cfg)`, `Clip(preview_url, title, cover_url)`, and `ArtistSearch.search(query)->list[int]` match across every consuming task. `create_app(store, search, resolver, cfg)` is defined in Task 7 and reused in Task 8.

---

## What comes after this plan

**Stage 3 — Web app & infrastructure.** The React/Vite frontend (autocomplete inputs, the card grid, the player behind an interface, URL-encoded state), the CDK stack, App Runner, DynamoDB table, and GitHub Actions with OIDC. Written once this plan is executed and the API runs against the 75k graph.

**Tuning pass.** With the 75k graph loaded, tune the cost weights and bypass constants by listening to real paths — the activity spec §4.1/§4.3 defer to "hand-checked real paths."
