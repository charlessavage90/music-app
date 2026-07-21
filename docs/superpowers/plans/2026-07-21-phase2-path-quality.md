# Phase 2 — Path Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two structural defects in the similarity graph (an inverted neighbour cap and a percentile clip that makes ~half of all routed hops free), then decide the damping question against metrics that cannot be gamed the way the previous ones were.

**Architecture:** Two tracks. **Track A** builds measurement infrastructure in `api/` — degree-controlled path metrics, null models, a bad-path screen, an MBID-keyed panel, and an HTML path exporter — using artifacts that already exist, with no graph builds. **Track B** changes `builder/` scoring behind config knobs and builds six artifacts in a fixed sequence, each adopted or rejected on its own evidence before the next.

**Tech Stack:** Python 3.14, numpy, pytest, `uv` for env management. New dependency: `scipy` (Wilcoxon signed-rank), added to the api `dev` extra only.

## Global Constraints

- **Environment:** the project is under OneDrive on Windows. Prefix **every** `uv` command with `UV_LINK_MODE=copy` or it fails with hardlink errors. Each package has its own `.venv`; `cd` into `builder/` or `api/` before running `uv`.
- **Encoding:** set `PYTHONIOENCODING=utf-8` on any command that prints artist names, or the Windows console codec raises `UnicodeEncodeError` on non-Latin-1 characters.
- **Determinism is a hard requirement** (original design §9): identical input must produce byte-identical output. Every ordering decision must be explicit — IDs are assigned in sorted-MBID order, ties break on lowest MBID.
- **The builder must never touch the network during `build`.** `builder/tests/test_replay.py` enforces this by injecting a fetcher that raises. It must keep passing, unmodified.
- **`builder/` and `api/` share no code.** The `APG1` binary artifact is the only contract. Do not import across them; do not add a shared package.
- **The `APG1` format does not change in this phase.** Only the values written into `scores`, and the node set, change.
- **Numbers live in one document.** `docs/superpowers/findings/2026-07-21-scoring-adjudication.md` is the quantitative record. Cite section numbers; never copy a figure into a spec, plan, or code comment.
- **Snyk:** run `snyk_code_scan` on new or modified Python and fix what it reports before committing.
- **Never optimise against the bad-path detector.** It is a rejection screen only.

## Decisions this plan makes that the spec left open

| Question | Decision | Why |
|---|---|---|
| Cap fix approach (§B4 precondition 1) | **Mutual k-NN**: keep edge `(u,v)` iff `v ∈ topK(u)` **and** `u ∈ topK(v)` | The only option that yields a hard degree bound and is symmetric by construction. Alternatives either don't bound degree (union-kNN) or break symmetry. Risk: it prunes more aggressively, so Task 12 measures largest-component retention and **fails the task if retention drops below 90 %**. |
| Popularity confound (§6.1) | **`w_jump = 0` evaluation arm**, not a frozen-popularity build | Evaluation-time only, so it costs no builds. With `w_floor` a proven no-op and `w_hub` dormant, cost reduces to `w_sim·(1−sim) + w_hop`, removing the popularity channel entirely. |
| Bad-path detector signals (§B1) | Non-musical interior entity; zero-common-neighbour hop; ≥3 consecutive interior nodes in one micro-cluster | The first three of the spec's four candidates. The fourth (degree/popularity discontinuity) is dropped: `max_interior_degree` and `mean_interior_pop` already report it, and adding it would make the screen partly redundant with the metrics it is meant to be independent of. |
| Where build provenance lives | A sidecar `<artifact>.json` manifest, not the `APG1` header | The format does not change in this phase (global constraint). A sidecar gives provenance without touching the builder↔api contract. |

---

## File Structure

**Track A — `api/` (measurement; no builder changes, no graph builds)**

| File | Responsibility |
|---|---|
| `api/src/artistpath_api/evaluation.py` *(modify)* | Pure metrics over a `GraphStore`. Gains neighbour-set primitives, Adamic–Adar, overlap coefficient, Jaccard, `hubfrac`, ceiling-hop fraction. No I/O. |
| `api/src/artistpath_api/badpath.py` *(create)* | The bad-path rejection screen. Separate file: it is a *screen*, not a metric, and keeping it out of `evaluation.py` makes it structurally impossible to add to the objective by accident. |
| `api/eval/nulls.py` *(create)* | Degree-biased random walk and configuration-model rewiring. |
| `api/eval/panel.py` *(create)* | Panel generation and loading, MBID-keyed. |
| `api/eval/panel.json` *(create, committed)* | The frozen panel. Data, not code. |
| `api/eval/stats.py` *(create)* | Paired Wilcoxon with Holm correction. |
| `api/eval/diagnostics.py` *(create)* | Per-artifact structural diagnostics table. |
| `api/eval/run_baseline.py` *(rewrite)* | Drives metrics over the panel; emits results + diagnostics. |
| `api/eval/export_paths.py` *(create)* | Self-contained HTML, artifacts side by side, rank/score/degree per hop. |

**Track B — `builder/` (scoring; produces artifacts)**

| File | Responsibility |
|---|---|
| `builder/src/artistpath_builder/config.py` *(modify)* | New knobs: `cap_strategy`, `similarity_rescale`, `filter_special_purpose`. |
| `builder/src/artistpath_builder/graph.py` *(modify)* | `mutual_knn_cap()` — the symmetrisation-aware cap. |
| `builder/src/artistpath_builder/pipeline.py` *(modify)* | Entity filter, damping in log space, rescale strategy dispatch. |
| `builder/src/artistpath_builder/manifest.py` *(create)* | Build provenance sidecar. |
| `builder/src/artistpath_builder/cli.py` *(modify)* | Pass the new knobs; write the manifest. |

---

# Track A — Measurement infrastructure

## Task 1: Build timing and provenance manifest

Resolves spec §8 risk 1 (build wall-clock unknown, blocks scheduling) and §8 risk 3 (artifacts have no provenance — the root cause of the confounded comparison in §1.1).

**Files:**
- Create: `builder/src/artistpath_builder/manifest.py`
- Modify: `builder/src/artistpath_builder/cli.py` (`cmd_build`, around line 103)
- Test: `builder/tests/test_manifest.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `build_manifest(graph, config, payload, elapsed_seconds) -> dict` and `write_manifest(path: Path, manifest: dict) -> None`. Task 15 reads these sidecars to label arms.

- [ ] **Step 1: Write the failing test**

```python
# builder/tests/test_manifest.py
import json
from pathlib import Path

from artistpath_builder.config import BuilderConfig
from artistpath_builder.manifest import build_manifest, write_manifest


class _FakeGraph:
    artist_count = 3
    edge_count = 4


def test_manifest_records_config_and_shape():
    m = build_manifest(_FakeGraph(), BuilderConfig(), b"abc", elapsed_seconds=12.5)
    assert m["artists"] == 3
    assert m["edges"] == 4
    assert m["elapsed_seconds"] == 12.5
    assert m["sha256"] == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    # Every tunable that changes the artifact must be recorded.
    assert m["config"]["similarity_damping"] == 0.0
    assert m["config"]["max_neighbours_per_artist"] == 50


def test_manifest_records_git_commit():
    m = build_manifest(_FakeGraph(), BuilderConfig(), b"abc", elapsed_seconds=1.0)
    # 40-char sha, or "unknown" when git is unavailable.
    assert len(m["git_commit"]) == 40 or m["git_commit"] == "unknown"


def test_write_manifest_is_sidecar_json(tmp_path: Path):
    out = tmp_path / "graph-test.bin"
    write_manifest(out, {"artists": 3})
    sidecar = tmp_path / "graph-test.bin.json"
    assert json.loads(sidecar.read_text(encoding="utf-8"))["artists"] == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_manifest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.manifest'`

- [ ] **Step 3: Write the implementation**

```python
# builder/src/artistpath_builder/manifest.py
"""Build provenance, written as a sidecar next to every artifact.

Four graphs once sat in builder/scratch/ with no record of which commit built
them, and were compared as though they differed in one variable. They differed
in two, and that invalidated two separate analyses. Every build now records
what produced it.

A sidecar rather than an APG1 header field: the artifact format is the
builder/api contract and is deliberately not changed in this phase.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from artistpath_builder.config import BuilderConfig


def _git_commit() -> str:
    """Current HEAD, or "unknown" outside a git checkout."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and len(commit) == 40 else "unknown"


def build_manifest(
    graph, config: BuilderConfig, payload: bytes, elapsed_seconds: float
) -> dict:
    """Everything needed to reproduce or identify this artifact."""
    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "elapsed_seconds": round(elapsed_seconds, 1),
        "artists": graph.artist_count,
        "edges": graph.edge_count,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "config": dataclasses.asdict(config),
    }


def write_manifest(artifact_path: Path, manifest: dict) -> None:
    """Write `<artifact>.json` beside the artifact."""
    sidecar = artifact_path.with_suffix(artifact_path.suffix + ".json")
    sidecar.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_manifest.py -v`
Expected: PASS, 3 passed

- [ ] **Step 5: Wire it into `cmd_build` and time the build**

Replace `cmd_build` in `builder/src/artistpath_builder/cli.py` (currently at line 103):

```python
def cmd_build(args) -> int:
    config = _config(args)
    started = time.monotonic()
    graph = build_from_archive(config, _archive(args), ListenBrainzSource(config))
    payload = serialise(graph)
    elapsed = time.monotonic() - started
    out = Path(args.out)
    out.write_bytes(payload)
    write_manifest(out, build_manifest(graph, config, payload, elapsed))
    mean_edges = graph.edge_count / graph.artist_count if graph.artist_count else 0
    logging.info(
        "wrote %s: %d artists, %d edges (%.1f per artist), %.1f MB, %.0fs",
        args.out,
        graph.artist_count,
        graph.edge_count,
        mean_edges,
        len(payload) / 1e6,
        elapsed,
    )
    return 0
```

Add to the imports at the top of `cli.py`:

```python
import time

from artistpath_builder.manifest import build_manifest, write_manifest
```

- [ ] **Step 6: Run the full builder suite**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, 69 passed (66 existing + 3 new)

- [ ] **Step 7: Measure a real 75k build — this is the scheduling input**

Run:
```bash
cd builder && UV_LINK_MODE=copy uv run artistpath-build build \
  --archive-dir ./scratch/graph-archive --out scratch/graph-timing-probe.bin
```
Record the logged elapsed time by writing it to **`builder/scratch/BUILD-TIMING.txt`** (gitignored, and the same directory the artifacts land in):

```bash
echo "75k build from archive: <N> seconds, measured <date>, commit $(git rev-parse --short HEAD)" \
  > builder/scratch/BUILD-TIMING.txt
```

Task 15 Step 2 reads that file to decide how to run the six builds. **If a build exceeds 30 minutes**, Task 15 runs them sequentially in the background rather than interactively.

Then delete the probe artifact: `rm builder/scratch/graph-timing-probe.bin*`

- [ ] **Step 8: Commit**

```bash
git add builder/src/artistpath_builder/manifest.py builder/src/artistpath_builder/cli.py builder/tests/test_manifest.py
git commit -m "feat(builder): record build provenance in an artifact sidecar"
```

---

## Task 2: Neighbour-set primitives and degree-controlled overlap metrics

Implements spec §B1's objective and guard. Adamic–Adar becomes primary; the overlap coefficient is the mandatory degree-neutrality cross-check; Jaccard is demoted to a diagnostic.

**Files:**
- Modify: `api/src/artistpath_api/evaluation.py`
- Test: `api/tests/test_evaluation.py`

**Interfaces:**
- Consumes: `GraphStore` (`offsets`, `neighbours`, `scores`, `popularity`).
- Produces: `neighbours_array(store, node) -> np.ndarray`, `common_neighbours(store, u, v) -> np.ndarray`, `adamic_adar(store, u, v) -> float`, `overlap_coefficient(store, u, v) -> float`, `jaccard(store, u, v) -> float`, `geometric_mean(values) -> float`. Tasks 3, 5, 7 and 8 use these.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_evaluation.py`:

```python
import math

import numpy as np

from artistpath_api.evaluation import (
    adamic_adar,
    common_neighbours,
    geometric_mean,
    jaccard,
    neighbours_array,
    overlap_coefficient,
)


def _triangle_with_hub():
    # 0 and 1 are adjacent and share two common neighbours: 2 (degree 2) and
    # 3 (degree 4, a hub). Node 3 also links 4 and 5 to inflate its degree.
    return make_store(
        names=list("ABCDEF"),
        popularity=[0.5] * 6,
        undirected_edges=[
            (0, 1, 0.9),
            (0, 2, 0.9), (1, 2, 0.9),
            (0, 3, 0.9), (1, 3, 0.9),
            (3, 4, 0.9), (3, 5, 0.9),
        ],
    )


def test_neighbours_array_is_sorted_and_excludes_self():
    store = _triangle_with_hub()
    assert list(neighbours_array(store, 0)) == [1, 2, 3]


def test_common_neighbours_excludes_the_two_endpoints():
    # 0 and 1 are each other's neighbours, but neither is a *common* neighbour.
    store = _triangle_with_hub()
    assert list(common_neighbours(store, 0, 1)) == [2, 3]


def test_adamic_adar_discounts_the_hub():
    # AA = 1/log(deg 2) + 1/log(deg 4) = 1/log(2) + 1/log(4).
    store = _triangle_with_hub()
    expected = 1 / math.log(2) + 1 / math.log(4)
    assert adamic_adar(store, 0, 1) == pytest.approx(expected, rel=1e-9)
    # The hub contributes strictly less than the low-degree node — the whole point.
    assert 1 / math.log(4) < 1 / math.log(2)


def test_overlap_coefficient_divides_by_the_smaller_degree():
    # |CN| = 2; deg(0) = 3, deg(1) = 3; min = 3.
    store = _triangle_with_hub()
    assert overlap_coefficient(store, 0, 1) == pytest.approx(2 / 3, rel=1e-9)


def test_jaccard_uses_union_including_the_endpoints():
    # N(0) = {1,2,3}, N(1) = {0,2,3}. Intersection {2,3} = 2; union {0,1,2,3} = 4.
    store = _triangle_with_hub()
    assert jaccard(store, 0, 1) == pytest.approx(2 / 4, rel=1e-9)


def test_metrics_are_zero_when_no_common_neighbours():
    store = make_store(
        names=list("AB"), popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert list(common_neighbours(store, 0, 1)) == []
    assert adamic_adar(store, 0, 1) == 0.0
    assert overlap_coefficient(store, 0, 1) == 0.0
    assert jaccard(store, 0, 1) == 0.0


def test_adamic_adar_skips_degree_one_common_neighbours():
    # log(1) = 0 would divide by zero. A degree-1 node cannot be a common
    # neighbour of two distinct nodes, but the guard must exist regardless.
    store = _triangle_with_hub()
    assert math.isfinite(adamic_adar(store, 0, 1))


def test_geometric_mean_is_robust_to_a_single_zero():
    # A plain product would collapse to 0; the epsilon floor keeps it finite
    # and ordered, so one bad hop does not erase the rest of the path.
    assert geometric_mean([1.0, 1.0, 1.0]) == pytest.approx(1.0)
    assert geometric_mean([4.0, 1.0]) == pytest.approx(2.0)
    assert 0.0 < geometric_mean([1.0, 0.0]) < 1.0
    assert geometric_mean([]) == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_evaluation.py -v`
Expected: FAIL with `ImportError: cannot import name 'adamic_adar'`

- [ ] **Step 3: Write the implementation**

Add to `api/src/artistpath_api/evaluation.py`, after the existing `edge_score`:

```python
# Common-neighbour overlap floors at this value before log-space aggregation,
# so one zero-overlap hop cannot erase an entire path's score. Measured
# zero-rate on the 75k graph is 0.7% (adjudication §4.3).
_GEO_EPSILON = 1e-6


def neighbours_array(store: GraphStore, node: int) -> np.ndarray:
    """This node's neighbour ids as a sorted int32 view over the CSR row.

    graph.py sorts each CSR row by destination id at build time, so this is
    already sorted and needs no copy — which is what lets the set operations
    below run in O(d_u + d_v) with no Python sets.
    """
    start, end = int(store.offsets[node]), int(store.offsets[node + 1])
    return store.neighbours[start:end]


def common_neighbours(store: GraphStore, u: int, v: int) -> np.ndarray:
    """Neighbours shared by u and v, excluding u and v themselves.

    Endpoint convention (spec §B1): for an *adjacent* pair, u is always in
    N(v) and v is always in N(u), while u is never in N(u). Left in, the two
    endpoints would inflate every adjacent pair's overlap by a constant that
    varies with degree. They are excluded here and included in the union for
    `jaccard`, which is the conventional definition.
    """
    shared = np.intersect1d(
        neighbours_array(store, u), neighbours_array(store, v), assume_unique=True
    )
    return shared[(shared != u) & (shared != v)]


def adamic_adar(store: GraphStore, u: int, v: int) -> float:
    """Sum of 1/log(degree) over common neighbours.

    The primary objective. Overlap through a hub counts for little; overlap
    through an obscure artist counts for a lot — which is the property raw
    Jaccard lacks (it correlates -0.639 with max-degree, adjudication §4.1).
    """
    total = 0.0
    for w in common_neighbours(store, u, v):
        degree = out_degree(store, int(w))
        if degree > 1:  # log(1) == 0
            total += 1.0 / math.log(degree)
    return total


def overlap_coefficient(store: GraphStore, u: int, v: int) -> float:
    """|N(u) & N(v)| / min(deg u, deg v) — the degree-neutrality guard.

    Adamic-Adar is flat in max-degree but couples to min-degree at Spearman
    +0.578, a measured channel an optimiser could exploit. This is near-neutral
    on both axes and is the control for that channel (adjudication §4.2-4.3).
    Report both; never adopt on Adamic-Adar alone.
    """
    smaller = min(out_degree(store, u), out_degree(store, v))
    if smaller == 0:
        return 0.0
    return len(common_neighbours(store, u, v)) / smaller


def jaccard(store: GraphStore, u: int, v: int) -> float:
    """|N(u) & N(v)| / |N(u) | N(v)| — DIAGNOSTIC ONLY.

    Retained so its redundancy stays visible in the results table, not as an
    objective. It is structurally bounded by min(d_u,d_v)/max(d_u,d_v), so it
    is a near-deterministic function of max_interior_degree rather than an
    independent check (adjudication §4.1).
    """
    union = np.union1d(neighbours_array(store, u), neighbours_array(store, v))
    if union.size == 0:
        return 0.0
    return len(common_neighbours(store, u, v)) / union.size


def geometric_mean(values: list[float]) -> float:
    """Geometric mean with an epsilon floor.

    Aggregation for per-hop overlap. A bottleneck (min) over 7-9 hops is
    dominated by one noisy node; a plain product collapses to zero on any
    single zero-overlap hop. The floor keeps the ordering meaningful.
    """
    if not values:
        return 0.0
    logs = [math.log(max(v, _GEO_EPSILON)) for v in values]
    return math.exp(sum(logs) / len(logs))
```

Add `import math` to the imports at the top of `evaluation.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_evaluation.py -v`
Expected: PASS, all tests including the 8 new ones

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/evaluation.py api/tests/test_evaluation.py
git commit -m "feat(eval): degree-controlled overlap metrics with an overlap-coefficient guard"
```

---

## Task 3: Rework PathMetrics — hubfrac, ceiling hops, overlap aggregates

Replaces the binary `hub_traversed` (0.642 by chance at length 7.4) with `hubfrac`, and adds the ceiling-hop fraction that made every prior comparison uninterpretable.

**Files:**
- Modify: `api/src/artistpath_api/evaluation.py`
- Test: `api/tests/test_evaluation.py`

**Interfaces:**
- Consumes: Task 2's `adamic_adar`, `overlap_coefficient`, `jaccard`, `geometric_mean`.
- Produces: reworked `PathMetrics` dataclass with fields `length`, `hubfrac`, `max_interior_degree`, `mean_interior_pop`, `max_interior_pop`, `bottleneck_sim`, `mean_sim`, `ceiling_hops`, `adamic_adar`, `overlap_coefficient`, `jaccard`; `path_metrics(store, path, hub_nodes) -> PathMetrics`; `summarise(metrics) -> dict`. Tasks 7, 8, 9 consume these.

**Note the signature change:** `path_metrics` now takes `hub_nodes: set[int]` (a frozen hub set) instead of `hub_threshold: int`. The per-graph top-1 % threshold moves between builds (363 in v3, 278 in cosine), so a variant could "improve" purely by compressing its degree distribution. Existing callers must be updated.

- [ ] **Step 1: Write the failing tests**

Replace `test_hub_detection_flags_high_degree_interior_node`, `test_endpoints_are_not_counted_as_hubs`, `test_bottleneck_is_the_weakest_link` and `test_summarise_aggregates_hub_rate` in `api/tests/test_evaluation.py` with:

```python
def test_hubfrac_is_the_fraction_of_interior_nodes_that_are_hubs():
    # Path 1->0->2->3 has interior [0, 2]; only node 0 is in the hub set.
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9), (2, 3, 0.9)],
    )
    m = path_metrics(store, [1, 0, 2, 3], hub_nodes={0})
    assert m.hubfrac == pytest.approx(0.5)
    assert m.max_interior_degree == 3


def test_hubfrac_ignores_endpoints_even_when_they_are_hubs():
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9)],
    )
    m = path_metrics(store, [0, 1], hub_nodes={0})
    assert m.hubfrac == 0.0


def test_hubfrac_is_zero_for_a_path_with_no_interior():
    store = make_store(
        names=list("AB"), popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert path_metrics(store, [0, 1], hub_nodes=set()).hubfrac == 0.0


def test_ceiling_hops_counts_free_similarity_edges():
    # Two hops: one at exactly 1.0 (free — w_sim*(1-sim) == 0), one at 0.5.
    store = make_store(
        names=list("ABC"), popularity=[0.5] * 3,
        undirected_edges=[(0, 1, 1.0), (1, 2, 0.5)],
    )
    m = path_metrics(store, [0, 1, 2], hub_nodes=set())
    assert m.ceiling_hops == pytest.approx(0.5)


def test_bottleneck_is_the_weakest_link():
    store = make_store(
        names=list("ABC"), popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.2)],
    )
    m = path_metrics(store, [0, 1, 2], hub_nodes=set())
    assert m.bottleneck_sim == pytest.approx(0.2, abs=1e-6)
    assert m.mean_sim == pytest.approx(0.55, abs=1e-6)


def test_summarise_aggregates_hubfrac_and_ceiling_hops():
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 1.0), (0, 2, 1.0), (0, 3, 0.5), (2, 3, 0.5)],
    )
    a = path_metrics(store, [1, 0, 2, 3], hub_nodes={0})   # hubfrac 0.5
    b = path_metrics(store, [1, 0], hub_nodes={0})          # hubfrac 0.0
    s = summarise([a, b])
    assert s["n"] == 2
    assert s["mean_hubfrac"] == pytest.approx(0.25)
    assert "mean_adamic_adar" in s
    assert "mean_overlap_coefficient" in s
    assert "mean_ceiling_hops" in s
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_evaluation.py -v`
Expected: FAIL with `TypeError: path_metrics() got an unexpected keyword argument 'hub_nodes'`

- [ ] **Step 3: Rewrite `PathMetrics`, `path_metrics` and `summarise`**

Replace the existing `PathMetrics` dataclass, `path_metrics` and `summarise` in `api/src/artistpath_api/evaluation.py`:

```python
@dataclass(frozen=True, slots=True)
class PathMetrics:
    length: int                  # nodes in the path
    hubfrac: float               # fraction of INTERIOR nodes in the frozen hub set
    max_interior_degree: int
    mean_interior_pop: float
    max_interior_pop: float
    bottleneck_sim: float        # diagnostic — derived from the scores under test
    mean_sim: float              # diagnostic
    ceiling_hops: float          # fraction of hops at score 1.0 — see below
    adamic_adar: float           # PRIMARY objective, geometric mean over hops
    overlap_coefficient: float   # mandatory degree-neutrality guard
    jaccard: float               # diagnostic only


def path_metrics(
    store: GraphStore, path: list[int], hub_nodes: set[int]
) -> PathMetrics:
    """Measure one path. Interior = nodes excluding the two user-chosen endpoints.

    `hub_nodes` is a FROZEN set of node ids, not a per-graph threshold. The
    top-1% degree cutoff moves between builds, so a threshold would let a
    variant "improve" purely by compressing its degree distribution.

    `ceiling_hops` is the fraction of hops whose similarity is exactly 1.0.
    Those hops cost w_sim*(1 - 1.0) == 0, so the router picks among them on
    w_jump and w_hop alone — effectively on noise. This is the defect that
    made every prior cross-artifact comparison uninterpretable, and it is
    invisible in every other metric here (adjudication §2.5).
    """
    interior = path[1:-1]
    degs = [out_degree(store, n) for n in interior]
    pops = [float(store.popularity[n]) for n in interior]
    hops = list(zip(path, path[1:]))
    sims = [edge_score(store, a, b) for a, b in hops]

    return PathMetrics(
        length=len(path),
        hubfrac=(sum(n in hub_nodes for n in interior) / len(interior))
        if interior
        else 0.0,
        max_interior_degree=max(degs) if degs else 0,
        mean_interior_pop=(sum(pops) / len(pops)) if pops else 0.0,
        max_interior_pop=max(pops) if pops else 0.0,
        bottleneck_sim=min(sims) if sims else 1.0,
        mean_sim=(sum(sims) / len(sims)) if sims else 1.0,
        ceiling_hops=(sum(s >= 1.0 for s in sims) / len(sims)) if sims else 0.0,
        adamic_adar=geometric_mean([adamic_adar(store, a, b) for a, b in hops]),
        overlap_coefficient=geometric_mean(
            [overlap_coefficient(store, a, b) for a, b in hops]
        ),
        jaccard=geometric_mean([jaccard(store, a, b) for a, b in hops]),
    )


def summarise(metrics: list[PathMetrics]) -> dict[str, float]:
    """Aggregate a set of path metrics into headline numbers."""
    n = len(metrics)
    if n == 0:
        return {}
    return {
        "n": n,
        "mean_hubfrac": sum(m.hubfrac for m in metrics) / n,
        "mean_length": sum(m.length for m in metrics) / n,
        "mean_max_interior_degree": sum(m.max_interior_degree for m in metrics) / n,
        "mean_interior_pop": sum(m.mean_interior_pop for m in metrics) / n,
        "mean_bottleneck_sim": sum(m.bottleneck_sim for m in metrics) / n,
        "mean_sim": sum(m.mean_sim for m in metrics) / n,
        "mean_ceiling_hops": sum(m.ceiling_hops for m in metrics) / n,
        "mean_adamic_adar": sum(m.adamic_adar for m in metrics) / n,
        "mean_overlap_coefficient": sum(m.overlap_coefficient for m in metrics) / n,
        "mean_jaccard": sum(m.jaccard for m in metrics) / n,
    }


def hub_node_set(store: GraphStore, top_fraction: float) -> set[int]:
    """Node ids in the top `top_fraction` by out-degree, as a frozen set.

    Computed ONCE on the control build and reused across every variant.
    """
    degrees = np.diff(store.offsets)
    cutoff = np.quantile(degrees, 1.0 - top_fraction)
    return {int(i) for i in np.where(degrees >= cutoff)[0]}
```

- [ ] **Step 4: Speed up `edge_score`, which is now called on every hop**

Replace `edge_score` in `api/src/artistpath_api/evaluation.py`:

```python
def edge_score(store: GraphStore, u: int, v: int) -> float:
    """Similarity of the u->v edge, or 0.0 if not adjacent.

    Binary search over the CSR row rather than a linear scan: graph.py sorts
    each row by destination id, and a linear scan over a degree-11,243 hub was
    costing more than everything else in this module combined.
    """
    start, end = int(store.offsets[u]), int(store.offsets[u + 1])
    row = store.neighbours[start:end]
    pos = int(np.searchsorted(row, v))
    if pos < row.size and int(row[pos]) == v:
        return float(store.scores[start + pos])
    return 0.0
```

- [ ] **Step 5: Update the one existing caller — THROWAWAY, keep it minimal**

> **`api/eval/run_baseline.py` is rewritten from scratch in Task 15 Step 1.**
> Every line you touch here is discarded. Make the smallest change that keeps
> the suite green — do not tidy this file, do not restructure it, do not add
> tests for it. If it looks like it deserves better, that is what Task 15 is
> for. (Task 15's rewrite is intentional, not a mistake to be reverted.)

In `api/eval/run_baseline.py`, `run_variant` currently passes `hub_threshold`. Change line 69 so the suite stays green:

```python
            metrics.append(path_metrics(store, path, hub_threshold))
```
becomes
```python
            metrics.append(path_metrics(store, path, hub_nodes))
```
and change the `run_variant` signature from `hub_threshold` to `hub_nodes`, and in `main()` replace:
```python
    hub_threshold = degree_percentile_threshold(store, 0.01)
```
with
```python
    hub_nodes = hub_node_set(store, 0.01)
```
updating the two uses below it. Import `hub_node_set` instead of `degree_percentile_threshold`.

- [ ] **Step 6: Run the full api suite**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, all tests

- [ ] **Step 7: Commit**

```bash
git add api/src/artistpath_api/evaluation.py api/tests/test_evaluation.py api/eval/run_baseline.py
git commit -m "feat(eval): replace binary hub metric with hubfrac; add ceiling-hop fraction"
```

---

## Task 4: Null models

Implements spec §A3 — the outstanding experiment. Without a configuration-model null there is no way to tell topological hub-seeking from scoring-caused hub-seeking, and the committed record currently contains both conclusions.

**Files:**
- Create: `api/eval/nulls.py`
- Test: `api/tests/test_nulls.py`

**Interfaces:**
- Consumes: `GraphStore`, Task 3's `path_metrics` / `hub_node_set`.
- Produces: `degree_biased_walk(store, source, length, rng) -> list[int]`, `configuration_model_rewire(store, rng) -> GraphStore`. Task 10 runs the experiment.

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_nulls.py
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from nulls import configuration_model_rewire, degree_biased_walk  # noqa: E402

from tests.conftest import make_store


def _ring_with_hub():
    return make_store(
        names=list("ABCDE"),
        popularity=[0.5] * 5,
        undirected_edges=[
            (0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9), (3, 4, 0.9), (4, 0, 0.9),
        ],
    )


def test_degree_biased_walk_returns_requested_length():
    store = _ring_with_hub()
    rng = np.random.default_rng(0)
    walk = degree_biased_walk(store, source=0, length=4, rng=rng)
    assert len(walk) == 4
    assert walk[0] == 0


def test_degree_biased_walk_only_steps_along_real_edges():
    store = _ring_with_hub()
    rng = np.random.default_rng(0)
    walk = degree_biased_walk(store, source=0, length=5, rng=rng)
    for u, v in zip(walk, walk[1:]):
        start, end = int(store.offsets[u]), int(store.offsets[u + 1])
        assert v in store.neighbours[start:end]


def test_rewire_preserves_the_degree_sequence_exactly():
    store = _ring_with_hub()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    assert list(np.diff(rewired.offsets)) == list(np.diff(store.offsets))


def test_rewire_preserves_node_count_and_edge_count():
    store = _ring_with_hub()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    assert rewired.artist_count == store.artist_count
    assert rewired.neighbours.size == store.neighbours.size


def test_rewire_produces_no_self_loops():
    store = _ring_with_hub()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    for u in range(rewired.artist_count):
        start, end = int(rewired.offsets[u]), int(rewired.offsets[u + 1])
        assert u not in rewired.neighbours[start:end]


def test_rewire_is_deterministic_under_a_fixed_seed():
    store = _ring_with_hub()
    a = configuration_model_rewire(store, np.random.default_rng(11))
    b = configuration_model_rewire(store, np.random.default_rng(11))
    assert np.array_equal(a.neighbours, b.neighbours)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_nulls.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nulls'`

- [ ] **Step 3: Write the implementation**

```python
# api/eval/nulls.py
"""Null models for path-quality metrics.

A rate with no null model measures nothing. Hub-traversal read 94-98% and
looked alarming; a degree-biased null puts it at 61-68% by chance at typical
path lengths, and the real finding only existed once someone built the null.

Two nulls, answering different questions:

- `degree_biased_walk` — what a router that ignores scores entirely produces.
  Its stationary distribution is proportional to degree, so it is the right
  baseline for "does the router seek hubs beyond what a blind walker hits?"
- `configuration_model_rewire` — preserves the degree sequence exactly but
  randomises who connects to whom, destroying all community structure. Re-run
  the router on it and the question becomes "is hub-seeking a property of the
  SCORING, or of the degree sequence?" That is the one the committed record
  disagrees with itself about (adjudication §5.3).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402


def degree_biased_walk(
    store: GraphStore, source: int, length: int, rng: np.random.Generator
) -> list[int]:
    """A uniform random walk of `length` nodes starting at `source`.

    Uniform over neighbours makes the walk degree-biased in its stationary
    distribution — high-degree nodes are visited more often precisely because
    more edges lead to them. That bias is the point: it is what the observed
    hub fraction must beat to count as a finding.
    """
    walk = [source]
    current = source
    for _ in range(length - 1):
        start, end = int(store.offsets[current]), int(store.offsets[current + 1])
        if end <= start:
            break
        current = int(store.neighbours[rng.integers(start, end)])
        walk.append(current)
    return walk


def configuration_model_rewire(
    store: GraphStore, rng: np.random.Generator
) -> GraphStore:
    """Randomise edge endpoints while preserving every node's degree exactly.

    Double-edge swap on the undirected edge list: pick two edges (a,b) and
    (c,d), replace them with (a,d) and (c,b). Every endpoint keeps its degree
    by construction. Swaps producing a self-loop or a duplicate edge are
    rejected and retried, which is what keeps the result a simple graph.

    Scores are carried along with their edges. They are meaningless in the
    rewired graph — that is intentional. This null is for the score-free
    question of whether the DEGREE SEQUENCE alone explains hub-seeking.
    """
    # Undirected edge list: keep u < v so each edge appears once.
    us, vs = [], []
    for u in range(store.artist_count):
        start, end = int(store.offsets[u]), int(store.offsets[u + 1])
        for k in range(start, end):
            v = int(store.neighbours[k])
            if u < v:
                us.append(u)
                vs.append(v)
    us_arr = np.asarray(us, dtype=np.int64)
    vs_arr = np.asarray(vs, dtype=np.int64)
    m = us_arr.size
    if m < 2:
        return store

    existing = {(int(a), int(b)) for a, b in zip(us_arr, vs_arr)}

    # 10 swap attempts per edge is the standard mixing heuristic for
    # double-edge-swap randomisation.
    for _ in range(10 * m):
        i, j = int(rng.integers(m)), int(rng.integers(m))
        if i == j:
            continue
        a, b = int(us_arr[i]), int(vs_arr[i])
        c, d = int(us_arr[j]), int(vs_arr[j])
        if len({a, b, c, d}) < 4:
            continue
        new_i = (min(a, d), max(a, d))
        new_j = (min(c, b), max(c, b))
        if new_i in existing or new_j in existing:
            continue
        existing.discard((min(a, b), max(a, b)))
        existing.discard((min(c, d), max(c, d)))
        existing.add(new_i)
        existing.add(new_j)
        us_arr[i], vs_arr[i] = new_i
        us_arr[j], vs_arr[j] = new_j

    return _store_from_edges(store, us_arr, vs_arr)


def _store_from_edges(
    template: GraphStore, us: np.ndarray, vs: np.ndarray
) -> GraphStore:
    """Rebuild CSR arrays from an undirected edge list, mirroring each edge."""
    n = template.artist_count
    rows: list[list[int]] = [[] for _ in range(n)]
    for a, b in zip(us, vs):
        rows[int(a)].append(int(b))
        rows[int(b)].append(int(a))

    offsets = np.zeros(n + 1, dtype=np.int32)
    neighbours: list[int] = []
    for i in range(n):
        for v in sorted(rows[i]):  # deterministic within-row order
            neighbours.append(v)
        offsets[i + 1] = len(neighbours)

    return GraphStore(
        mbids=list(template.mbids),
        names=list(template.names),
        disambiguations=list(template.disambiguations),
        popularity=template.popularity.copy(),
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.full(len(neighbours), 0.5, dtype=np.float32),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_nulls.py -v`
Expected: PASS, 6 passed

- [ ] **Step 5: Commit**

```bash
git add api/eval/nulls.py api/tests/test_nulls.py
git commit -m "feat(eval): degree-biased walk and configuration-model null models"
```

---

## Task 5: Bad-path detector

Implements spec §B1. Every overlap-based objective scores the *La La Land* chain well, so this is the only instrument that catches the project's recurring failure.

**Files:**
- Create: `api/src/artistpath_api/badpath.py`
- Test: `api/tests/test_badpath.py`

**Interfaces:**
- Consumes: `GraphStore`, Task 2's `common_neighbours` / `jaccard`.
- Produces: `BadPathReport` dataclass (`flagged: bool`, `reasons: list[str]`), `screen_path(store, path) -> BadPathReport`. Tasks 7, 8 and 15 report the count.

**This is a screen, not an objective.** It lives outside `evaluation.py` so it cannot be added to the optimisation target by accident. Nothing in this plan optimises against it.

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_badpath.py
import numpy as np

from artistpath_api.badpath import screen_path
from artistpath_api.graph_store import GraphStore
from tests.conftest import make_store


def _store_with_disambiguations(names, disambiguations, undirected_edges):
    base = make_store(
        names=names, popularity=[0.5] * len(names), undirected_edges=undirected_edges
    )
    return GraphStore(
        mbids=base.mbids,
        names=base.names,
        disambiguations=list(disambiguations),
        popularity=base.popularity,
        offsets=base.offsets,
        neighbours=base.neighbours,
        scores=base.scores,
    )


def test_flags_a_special_purpose_interior_node():
    store = _store_with_disambiguations(
        names=["A", "[unknown]", "C"],
        disambiguations=["", "Special Purpose Artist - do not add releases", ""],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    report = screen_path(store, [0, 1, 2])
    assert report.flagged is True
    assert any("non-musical" in r for r in report.reasons)


def test_flags_an_interior_node_with_no_name():
    store = _store_with_disambiguations(
        names=["A", "", "C"],
        disambiguations=["", "", ""],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    assert screen_path(store, [0, 1, 2]).flagged is True


def test_does_not_flag_a_special_purpose_ENDPOINT():
    # Endpoints are user-chosen. Only interior nodes are the router's fault.
    store = _store_with_disambiguations(
        names=["[unknown]", "B", "C"],
        disambiguations=["Special Purpose Artist", "", ""],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    assert screen_path(store, [0, 1, 2]).flagged is False


def test_flags_a_hop_with_no_common_neighbours():
    # 0-1 and 1-2 are adjacent but 1-2 share nothing: a leap with no context.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 3, 0.9), (1, 3, 0.9), (1, 2, 0.9)],
    )
    report = screen_path(store, [0, 1, 2])
    assert report.flagged is True
    assert any("no common neighbour" in r for r in report.reasons)


def test_flags_three_consecutive_nodes_from_one_micro_cluster():
    # 1,2,3 form a tight clique with each other and nothing else — the
    # signature of a film cast list or a label roster.
    store = make_store(
        names=list("ABCDEF"), popularity=[0.5] * 6,
        undirected_edges=[
            (0, 1, 0.9),
            (1, 2, 0.9), (2, 3, 0.9), (1, 3, 0.9),
            (3, 4, 0.9), (4, 5, 0.9), (0, 5, 0.9), (0, 4, 0.9),
        ],
    )
    report = screen_path(store, [0, 1, 2, 3, 4])
    assert any("micro-cluster" in r for r in report.reasons)


def test_does_not_flag_a_clean_path():
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[
            (0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9), (0, 2, 0.5), (1, 3, 0.5),
        ],
    )
    report = screen_path(store, [0, 1, 2, 3])
    assert report.flagged is False
    assert report.reasons == []


def test_short_paths_are_never_flagged():
    store = make_store(
        names=list("AB"), popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert screen_path(store, [0, 1]).flagged is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_badpath.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_api.badpath'`

- [ ] **Step 3: Write the implementation**

```python
# api/src/artistpath_api/badpath.py
"""A rejection screen for incoherent paths.

NOT AN OBJECTIVE. Never optimise against this. An earlier tuning run improved
every headline metric while routing through unrelated foreign-scene artists and
a MusicBrainz editor account; a detector added to the objective would be gamed
the same way. It lives outside evaluation.py so it cannot be wired into the
optimisation target by accident.

It exists because every overlap-based metric is structurally blind to the
failure this project keeps hitting: a chain of dense, mutually-overlapping
micro-neighbourhoods (a film cast list) scores WELL on Adamic-Adar, on the
overlap coefficient, and on Jaccard (adjudication §4.3).

Three signals, all restricted to INTERIOR nodes — endpoints are user-chosen and
never the router's fault.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from artistpath_api.evaluation import common_neighbours, jaccard
from artistpath_api.graph_store import GraphStore

# MusicBrainz marks placeholder entities this way in the disambiguation field.
# Matching on disambiguation, never on name: 22 nodes have bracketed names and
# 15 of them are real bands ([Alexandros], [dunkelbunt], [:SITD:], ...).
_NON_MUSICAL = re.compile(r"special purpose", re.IGNORECASE)

# Pairwise neighbour-set Jaccard above which two adjacent interior nodes count
# as "the same tight cluster". Calibrated in Step 5 against known-bad paths.
_MICRO_CLUSTER_JACCARD = 0.5

# Consecutive interior nodes from one cluster before the run is flagged.
_MICRO_CLUSTER_RUN = 3


@dataclass(frozen=True, slots=True)
class BadPathReport:
    flagged: bool
    reasons: list[str] = field(default_factory=list)


def screen_path(store: GraphStore, path: list[int]) -> BadPathReport:
    """Flag a path a human would call incoherent. Interior nodes only."""
    reasons: list[str] = []
    interior = path[1:-1]
    if not interior:
        return BadPathReport(flagged=False, reasons=[])

    for node in interior:
        if _NON_MUSICAL.search(store.disambiguations[node] or ""):
            reasons.append(
                f"non-musical interior entity: {store.names[node]!r}"
            )
        elif not (store.names[node] or "").strip():
            reasons.append(f"non-musical interior entity: unnamed node {node}")

    for u, v in zip(path, path[1:]):
        if len(common_neighbours(store, u, v)) == 0:
            reasons.append(
                f"hop with no common neighbour: "
                f"{store.names[u]!r} -> {store.names[v]!r}"
            )

    run = 1
    for u, v in zip(interior, interior[1:]):
        if jaccard(store, u, v) >= _MICRO_CLUSTER_JACCARD:
            run += 1
            if run >= _MICRO_CLUSTER_RUN:
                reasons.append(
                    f"micro-cluster run of {run} interior nodes ending at "
                    f"{store.names[v]!r}"
                )
                break
        else:
            run = 1

    return BadPathReport(flagged=bool(reasons), reasons=reasons)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_badpath.py -v`
Expected: PASS, 7 passed

- [ ] **Step 5: Calibrate against real known-bad and known-good paths**

> **JUDGEMENT STEP — required reading first:**
> `docs/superpowers/findings/2026-07-21-scoring-adjudication.md` **§4.3**
> (why every overlap metric scores the *La La Land* path well) and **§2.3**
> (the decoded path itself).
>
> Calibration is a two-sided target and both sides are load-bearing. The
> temptation is to loosen thresholds until the known-bad path flags. Resist it:
> a screen that fires on everything passes a one-sided check and is worthless
> as adoption criterion 5. **Report the false-positive count on the good set
> with every threshold you try, and stop at the loosest setting that still
> separates them.**
>
> **If you cannot separate them at any threshold, stop and report that.** A
> failed calibration is a real result — it means these three signals do not
> capture the failure, and inventing a fourth to force a pass would be exactly
> the objective-gaming this screen exists to prevent.

Write a throwaway probe (in your scratch directory, **not** the repo):

```python
# calibrate_badpath.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path("api/src").resolve()))
from artistpath_api.badpath import screen_path
from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path

CASES = [
    # (graph, source name, target name, expected_flagged)
    ("builder/scratch/graph-75k-cosine.bin", "Miles Davis", "Daft Punk", True),
    ("builder/scratch/graph-75k-v3.bin", "Miles Davis", "Daft Punk", False),
    ("builder/scratch/graph-75k-v3.bin", "Burzum", "Dolly Parton", False),
]

for graph, src_name, dst_name, expected in CASES:
    store = GraphStore.load(graph)
    src = next(i for i, n in enumerate(store.names) if n == src_name)
    dst = next(i for i, n in enumerate(store.names) if n == dst_name)
    path = find_path(store, src, dst, [], ApiConfig())
    report = screen_path(store, path)
    status = "OK " if report.flagged == expected else "MISS"
    print(f"{status} {Path(graph).name:24s} {src_name} -> {dst_name}")
    print(f"     path: {' -> '.join(store.names[n] for n in path)}")
    print(f"     flagged={report.flagged} expected={expected}")
    for r in report.reasons:
        print(f"       - {r}")
```

Run: `PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python calibrate_badpath.py` from the repo root, with the api venv active (`cd api` first and adjust the paths, or run `uv run --project api`).

**Calibration target:** the cosine *La La Land* path must flag; both v3 paths must not. If it misses, adjust `_MICRO_CLUSTER_JACCARD` (try 0.4, then 0.35) or `_MICRO_CLUSTER_RUN`. **Do not loosen it until it flags everything** — a screen that fires on every path is as useless as one that never fires. Record the final thresholds and the false-positive count in the commit message.

- [ ] **Step 6: Lock the calibration into a test**

Append to `api/tests/test_badpath.py` a regression test using the tuned constants, so a future change to the thresholds fails loudly:

```python
def test_calibrated_thresholds_are_pinned():
    # Changing these silently would change what the screen rejects, and the
    # screen is criterion 5 of the adoption decision. Calibrated in Task 5
    # against the cosine La La Land path (must flag) and the v3 Miles Davis ->
    # Daft Punk and Burzum -> Dolly Parton paths (must not).
    from artistpath_api import badpath

    assert badpath._MICRO_CLUSTER_JACCARD == 0.5   # update if recalibrated
    assert badpath._MICRO_CLUSTER_RUN == 3
```

- [ ] **Step 7: Run the api suite and Snyk**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS

Then run `snyk_code_scan` on `api/src/artistpath_api`. Expected: 0 issues.

- [ ] **Step 8: Commit**

```bash
git add api/src/artistpath_api/badpath.py api/tests/test_badpath.py
git commit -m "feat(eval): bad-path rejection screen, calibrated on known-bad paths"
```

---

## Task 6: MBID-keyed evaluation panel

Implements spec §B2. The existing panel draws random *node indices* under a fixed seed; indices shift when the node set changes, so it can silently compare different artists across variants.

**Files:**
- Create: `api/eval/panel.py`
- Create: `api/eval/panel.json` (generated, committed)
- Test: `api/tests/test_panel.py`

**Interfaces:**
- Consumes: `GraphStore`.
- Produces: `generate_panel(store, rng) -> dict`, `load_panel(path) -> dict`, `resolve_pairs(store, panel, stratum, held_out=None) -> tuple[list[tuple[int,int]], list[str]]` returning `(pairs, dropped_mbids)`. Tasks 7, 8, 15 consume these.

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_panel.py
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from panel import generate_panel, load_panel, resolve_pairs  # noqa: E402

from tests.conftest import make_store


def _store(n=40):
    edges = [(i, (i + 1) % n, 0.9) for i in range(n)]
    edges += [(0, i, 0.9) for i in range(2, 12)]  # give node 0 a high degree
    return make_store(
        names=[f"artist{i}" for i in range(n)],
        popularity=[i / n for i in range(n)],
        undirected_edges=edges,
    )


def test_generate_panel_has_all_four_strata():
    panel = generate_panel(_store(), np.random.default_rng(42))
    assert set(panel["strata"]) == {
        "random", "obscure", "popularity_weighted", "hand_picked"
    }


def test_panel_pairs_are_mbid_keyed_not_index_keyed():
    panel = generate_panel(_store(), np.random.default_rng(42))
    first = panel["strata"]["random"][0]
    assert isinstance(first["from"], str) and len(first["from"]) == 36
    assert isinstance(first["to"], str)


def test_panel_pairs_are_deduped():
    panel = generate_panel(_store(), np.random.default_rng(42))
    for pairs in panel["strata"].values():
        keys = [(p["from"], p["to"]) for p in pairs]
        assert len(keys) == len(set(keys))


def test_no_pair_has_identical_endpoints():
    panel = generate_panel(_store(), np.random.default_rng(42))
    for pairs in panel["strata"].values():
        for p in pairs:
            assert p["from"] != p["to"]


def test_held_out_slice_is_flagged_and_disjoint():
    panel = generate_panel(_store(), np.random.default_rng(42))
    aggregated = [
        p
        for name in ("random", "obscure", "popularity_weighted")
        for p in panel["strata"][name]
    ]
    held = [p for p in aggregated if p.get("held_out")]
    analysis = [p for p in aggregated if not p.get("held_out")]
    assert held and analysis
    assert not ({(p["from"], p["to"]) for p in held}
                & {(p["from"], p["to"]) for p in analysis})


def test_hand_picked_pairs_are_never_held_out():
    # They are qualitative-only and never enter aggregates or the held-out check.
    panel = generate_panel(_store(), np.random.default_rng(42))
    assert all(not p.get("held_out") for p in panel["strata"]["hand_picked"])


def test_resolve_pairs_reports_dropped_mbids_rather_than_substituting():
    store = _store()
    panel = {
        "strata": {
            "random": [
                {"from": store.mbids[0], "to": store.mbids[1]},
                {"from": "missing-mbid-aaaaaaaaaaaaaaaaaaaaaaaa", "to": store.mbids[2]},
            ]
        }
    }
    pairs, dropped = resolve_pairs(store, panel, "random")
    assert pairs == [(0, 1)]
    assert dropped == ["missing-mbid-aaaaaaaaaaaaaaaaaaaaaaaa"]


def test_load_panel_rejects_a_malformed_file(tmp_path: Path):
    bad = tmp_path / "panel.json"
    bad.write_text(json.dumps({"nope": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="strata"):
        load_panel(bad)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_panel.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'panel'`

- [ ] **Step 3: Write the implementation**

```python
# api/eval/panel.py
"""The frozen evaluation panel, keyed by MBID.

The panel this replaces drew random NODE INDICES under a fixed seed. Indices
are assigned in sorted-MBID order over whatever survives the largest-component
prune, so any change to the node set shifts them and the "frozen" panel
silently compares different artists between runs.

Four strata. The three aggregated ones total 130 pairs; `hand_picked` is
qualitative only and is NEVER pooled into an aggregate — it was adversarially
selected on the d=0 graph, so regression to the mean guarantees it improves
under any variant.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402

N_RANDOM = 50
N_OBSCURE = 50
N_POPULARITY_WEIGHTED = 30

# Held-out counts per stratum. Computed only AFTER a candidate is chosen on the
# remaining 100, and used solely for adoption criterion 6.
HELD_OUT = {"random": 12, "obscure": 12, "popularity_weighted": 6}

OBSCURE_MAX_DEGREE = 5

# Pairs that produced known-bad or known-good paths in real use. Qualitative
# only. Resolved by name at generation time; missing names are skipped with a
# warning rather than failing the build.
HAND_PICKED_NAMES = [
    ("Miles Davis", "Daft Punk"),
    ("Burzum", "Dolly Parton"),
    ("Cayetana", "Coheed and Cambria"),
    ("Young Gun Silver Fox", "The Format"),
    ("Miles Davis", "Stan Getz"),
    ("Ella Fitzgerald", "Justin Timberlake"),
    ("Radiohead", "Dolly Parton"),
    ("Aphex Twin", "Johnny Cash"),
]


def _sample_pairs(candidates, n, rng, weights=None):
    """Draw `n` distinct unordered pairs from `candidates`."""
    seen: set[tuple[int, int]] = set()
    pairs: list[tuple[int, int]] = []
    attempts = 0
    while len(pairs) < n and attempts < n * 1000:
        attempts += 1
        a, b = rng.choice(candidates, size=2, replace=False, p=weights)
        a, b = int(a), int(b)
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        pairs.append((a, b))
    return pairs


def generate_panel(store: GraphStore, rng: np.random.Generator) -> dict:
    """Build the panel from a reference graph. Run ONCE; commit the result."""
    n = store.artist_count
    degrees = np.diff(store.offsets)
    all_nodes = np.arange(n)

    obscure = np.where(degrees <= OBSCURE_MAX_DEGREE)[0]
    if obscure.size < 2:
        obscure = all_nodes

    # Popularity-weighted: uniform sampling over 75k nodes is dominated by the
    # obscure tail, so without this stratum the panel never tests the
    # mainstream -> mainstream case real users actually query.
    pop = np.asarray(store.popularity, dtype=np.float64)
    weights = pop / pop.sum() if pop.sum() > 0 else None

    drawn = {
        "random": _sample_pairs(all_nodes, N_RANDOM, rng),
        "obscure": _sample_pairs(obscure, N_OBSCURE, rng),
        "popularity_weighted": _sample_pairs(
            all_nodes, N_POPULARITY_WEIGHTED, rng, weights=weights
        ),
    }

    by_name = {name: i for i, name in enumerate(store.names)}
    hand = []
    for src, dst in HAND_PICKED_NAMES:
        if src in by_name and dst in by_name and by_name[src] != by_name[dst]:
            hand.append((by_name[src], by_name[dst]))

    strata: dict[str, list[dict]] = {}
    for name, pairs in drawn.items():
        held = HELD_OUT.get(name, 0)
        strata[name] = [
            {
                "from": store.mbids[a],
                "to": store.mbids[b],
                "from_name": store.names[a],
                "to_name": store.names[b],
                "held_out": i < held,
            }
            for i, (a, b) in enumerate(pairs)
        ]
    strata["hand_picked"] = [
        {
            "from": store.mbids[a],
            "to": store.mbids[b],
            "from_name": store.names[a],
            "to_name": store.names[b],
            "held_out": False,
        }
        for a, b in hand
    ]

    return {
        "note": (
            "Frozen MBID-keyed panel. hand_picked is qualitative only and must "
            "never be pooled into an aggregate."
        ),
        "aggregated_strata": ["random", "obscure", "popularity_weighted"],
        "strata": strata,
    }


def load_panel(path: str | Path) -> dict:
    panel = json.loads(Path(path).read_text(encoding="utf-8"))
    if "strata" not in panel:
        raise ValueError("malformed panel: missing 'strata' key")
    return panel


def resolve_pairs(
    store: GraphStore,
    panel: dict,
    stratum: str,
    held_out: bool | None = None,
) -> tuple[list[tuple[int, int]], list[str]]:
    """Resolve MBID pairs to node ids for one graph.

    `held_out=None` returns every pair, `False` the analysis slice, `True` the
    held-out slice. Unresolvable MBIDs are REPORTED, never silently skipped —
    a variant with a different node set must be visible, not papered over.
    """
    pairs: list[tuple[int, int]] = []
    dropped: list[str] = []
    for entry in panel["strata"].get(stratum, []):
        if held_out is not None and bool(entry.get("held_out")) != held_out:
            continue
        a = store.id_by_mbid.get(entry["from"])
        b = store.id_by_mbid.get(entry["to"])
        if a is None:
            dropped.append(entry["from"])
            continue
        if b is None:
            dropped.append(entry["to"])
            continue
        pairs.append((a, b))
    return pairs, dropped
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_panel.py -v`
Expected: PASS, 8 passed

- [ ] **Step 5: Generate and commit the real panel**

```bash
cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -c "
import sys, json, numpy as np
from pathlib import Path
sys.path.insert(0, 'eval'); sys.path.insert(0, 'src')
from panel import generate_panel
from artistpath_api.graph_store import GraphStore
store = GraphStore.load('../builder/scratch/graph-75k-v3.bin')
panel = generate_panel(store, np.random.default_rng(42))
Path('eval/panel.json').write_text(json.dumps(panel, indent=2, ensure_ascii=False), encoding='utf-8')
for name, rows in panel['strata'].items():
    print(name, len(rows), 'held_out:', sum(bool(r['held_out']) for r in rows))
"
```

Expected output: `random 50 held_out: 12`, `obscure 50 held_out: 12`, `popularity_weighted 30 held_out: 6`, `hand_picked 8 held_out: 0`.

**If `hand_picked` is fewer than 8**, one or more names did not resolve. Print the missing ones and either correct the spelling against `store.names` or drop that pair from `HAND_PICKED_NAMES` — do not leave a silently short stratum.

- [ ] **Step 6: Commit**

```bash
git add api/eval/panel.py api/eval/panel.json api/tests/test_panel.py
git commit -m "feat(eval): frozen MBID-keyed panel with a held-out slice"
```

---

## Task 7: Structural diagnostics

Implements spec §B7. Every structural defect found so far was invisible in the existing summary output.

**Files:**
- Create: `api/eval/diagnostics.py`
- Test: `api/tests/test_diagnostics.py`

**Interfaces:**
- Consumes: `GraphStore`.
- Produces: `artifact_diagnostics(store, cap: int) -> dict`. Tasks 8 and 15 render it.

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_diagnostics.py
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from diagnostics import artifact_diagnostics  # noqa: E402

from tests.conftest import make_store


def _hub_store():
    # Node 0 has degree 5; nodes 1-5 have degree 1. Cap of 2 is exceeded by node 0.
    return make_store(
        names=[f"n{i}" for i in range(6)],
        popularity=[0.9] + [0.1] * 5,
        undirected_edges=[(0, i, 1.0) for i in range(1, 6)],
    )


def test_reports_nodes_exceeding_the_configured_cap():
    d = artifact_diagnostics(_hub_store(), cap=2)
    assert d["nodes_over_cap"] == 1
    assert d["max_degree"] == 5
    assert d["cap"] == 2


def test_reports_saturated_edges_and_their_destination_degrees():
    # All edges are 1.0 and all point at or from the hub.
    d = artifact_diagnostics(_hub_store(), cap=2)
    assert d["saturated_edges"] == 10          # 5 undirected edges, both directions
    assert d["saturated_dst_median_degree"] > 0


def test_reports_degree_and_popularity_quantiles():
    d = artifact_diagnostics(_hub_store(), cap=2)
    for key in ("degree_p50", "degree_p99", "pop_p25", "pop_p50", "pop_p75"):
        assert key in d


def test_handles_a_graph_with_no_saturated_edges():
    store = make_store(
        names=list("AB"), popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.4)]
    )
    d = artifact_diagnostics(store, cap=50)
    assert d["saturated_edges"] == 0
    assert d["saturated_dst_median_degree"] == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_diagnostics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'diagnostics'`

- [ ] **Step 3: Write the implementation**

```python
# api/eval/diagnostics.py
"""Per-artifact structural diagnostics.

Every structural defect this project has found was invisible in the summary
output that existed at the time — the clip ceiling, the cap asymmetry, the
confounded artifact provenance. All of them fall straight out of these numbers.

`nodes_over_cap` in particular makes the cap defect legible: the current output
reports only post-symmetrisation degree, in which a configured cap of 50 and an
observed maximum of 11,243 sit side by side without the contradiction ever
surfacing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402


def artifact_diagnostics(store: GraphStore, cap: int) -> dict:
    """Structural summary of one built artifact."""
    degrees = np.diff(store.offsets)
    pop = np.asarray(store.popularity, dtype=np.float64)
    scores = np.asarray(store.scores, dtype=np.float64)

    saturated = np.isclose(scores, 1.0)
    saturated_dsts = store.neighbours[saturated]

    with np.errstate(divide="ignore", invalid="ignore"):
        log_deg = np.log1p(degrees.astype(np.float64))
        edge_src_degrees = np.repeat(log_deg, degrees)
        corr = (
            float(np.corrcoef(scores, edge_src_degrees)[0, 1])
            if scores.size > 1
            else 0.0
        )

    return {
        "artists": int(store.artist_count),
        "edges": int(scores.size),
        "cap": cap,
        "nodes_over_cap": int((degrees > cap).sum()),
        "max_degree": int(degrees.max()) if degrees.size else 0,
        "degree_p50": float(np.percentile(degrees, 50)) if degrees.size else 0.0,
        "degree_p99": float(np.percentile(degrees, 99)) if degrees.size else 0.0,
        "pop_p25": float(np.percentile(pop, 25)) if pop.size else 0.0,
        "pop_p50": float(np.percentile(pop, 50)) if pop.size else 0.0,
        "pop_p75": float(np.percentile(pop, 75)) if pop.size else 0.0,
        "saturated_edges": int(saturated.sum()),
        "saturated_dst_median_degree": (
            float(np.median(degrees[saturated_dsts])) if saturated_dsts.size else 0.0
        ),
        "corr_score_log_degree": corr if np.isfinite(corr) else 0.0,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_diagnostics.py -v`
Expected: PASS, 4 passed

- [ ] **Step 5: Commit**

```bash
git add api/eval/diagnostics.py api/tests/test_diagnostics.py
git commit -m "feat(eval): per-artifact structural diagnostics"
```

---

## Task 8: Paired statistics

Implements spec §B8. The same endpoint pairs appear in every arm, so measurements are strongly paired and comparing aggregate means throws away most of the power.

**Files:**
- Create: `api/eval/stats.py`
- Modify: `api/pyproject.toml` (add `scipy` to the `dev` extra)
- Test: `api/tests/test_stats.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `paired_comparison(control, candidate) -> dict` with keys `n`, `median_delta`, `p_value`; `holm_correct(p_values) -> list[float]`. Task 15 consumes both.

- [ ] **Step 1: Add the dependency**

In `api/pyproject.toml`, change the dev extra:

```toml
dev = ["pytest>=8.0", "pytest-cov>=5.0", "pytest-asyncio>=0.23", "scipy>=1.14"]
```

Run: `cd api && UV_LINK_MODE=copy uv sync --extra dev`
Expected: scipy installed.

- [ ] **Step 2: Write the failing tests**

```python
# api/tests/test_stats.py
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from stats import holm_correct, paired_comparison  # noqa: E402


def test_paired_comparison_detects_a_consistent_improvement():
    control = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17]
    candidate = [c + 0.05 for c in control]
    result = paired_comparison(control, candidate)
    assert result["n"] == 8
    assert result["median_delta"] == pytest.approx(0.05, abs=1e-9)
    assert result["p_value"] < 0.05


def test_paired_comparison_finds_no_effect_when_there_is_none():
    control = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
    candidate = [0.11, 0.19, 0.31, 0.39, 0.51, 0.59, 0.71, 0.79]
    assert paired_comparison(control, candidate)["p_value"] > 0.05


def test_identical_inputs_yield_p_value_one():
    values = [0.1, 0.2, 0.3, 0.4, 0.5]
    result = paired_comparison(values, values)
    assert result["median_delta"] == 0.0
    assert result["p_value"] == 1.0


def test_mismatched_lengths_are_rejected():
    with pytest.raises(ValueError, match="same length"):
        paired_comparison([1.0, 2.0], [1.0])


def test_holm_correction_is_monotone_and_bounded():
    corrected = holm_correct([0.01, 0.02, 0.03])
    assert corrected == sorted(corrected)
    assert all(0.0 <= p <= 1.0 for p in corrected)
    # Smallest p gets the largest multiplier (x3 here).
    assert corrected[0] == pytest.approx(0.03)


def test_holm_correction_preserves_input_order():
    corrected = holm_correct([0.03, 0.01])
    assert corrected[1] < corrected[0]
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_stats.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'stats'`

- [ ] **Step 4: Write the implementation**

```python
# api/eval/stats.py
"""Paired significance testing for arm-vs-control comparisons.

Every arm routes the SAME endpoint pairs, so per-pair measurements are strongly
correlated. Comparing aggregate means discards that pairing and most of the
power with it. Wilcoxon signed-rank on per-pair deltas is the non-parametric
paired test, which matters because these metrics are heavily skewed.

Holm correction because each metric is compared across several arms; without it
the chance of one arm looking significant by luck rises with the arm count.
"""

from __future__ import annotations

from scipy.stats import wilcoxon


def paired_comparison(control: list[float], candidate: list[float]) -> dict:
    """Wilcoxon signed-rank on per-pair deltas (candidate - control)."""
    if len(control) != len(candidate):
        raise ValueError("control and candidate must be the same length")
    deltas = [b - a for a, b in zip(control, candidate)]
    n = len(deltas)
    ordered = sorted(deltas)
    median = (
        0.0
        if n == 0
        else ordered[n // 2]
        if n % 2
        else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    )
    if n == 0 or all(d == 0 for d in deltas):
        return {"n": n, "median_delta": 0.0, "p_value": 1.0}
    _, p = wilcoxon(candidate, control, zero_method="zsplit")
    return {"n": n, "median_delta": float(median), "p_value": float(p)}


def holm_correct(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni step-down correction. Returns values in input order."""
    m = len(p_values)
    if m == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda pair: pair[1])
    corrected = [0.0] * m
    running = 0.0
    for rank, (original_index, p) in enumerate(indexed):
        adjusted = min(1.0, p * (m - rank))
        running = max(running, adjusted)  # enforce monotonicity
        corrected[original_index] = running
    return corrected
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_stats.py -v`
Expected: PASS, 6 passed

- [ ] **Step 6: Commit**

```bash
git add api/eval/stats.py api/tests/test_stats.py api/pyproject.toml api/uv.lock
git commit -m "feat(eval): paired Wilcoxon comparison with Holm correction"
```

---

## Task 9: Path export tool

Implements spec §A1. Rank is mandatory: the v3 defect is invisible in scores (twelve consecutive `1.0000`s) and obvious in rank.

**Files:**
- Create: `api/eval/export_paths.py`
- Test: `api/tests/test_export_paths.py`

**Interfaces:**
- Consumes: Tasks 5, 6, 7 (`screen_path`, `load_panel`/`resolve_pairs`, `artifact_diagnostics`).
- Produces: `neighbour_rank(store, u, v) -> int | None`, `render_html(artifacts, panel, rows) -> str`, and a CLI entry point.

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_export_paths.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from export_paths import neighbour_rank, render_html  # noqa: E402

from tests.conftest import make_store


def test_neighbour_rank_is_one_based_by_descending_score():
    # Node 0's neighbours: 1 (0.9), 2 (0.5), 3 (0.1).
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.5), (0, 3, 0.1)],
    )
    assert neighbour_rank(store, 0, 1) == 1
    assert neighbour_rank(store, 0, 2) == 2
    assert neighbour_rank(store, 0, 3) == 3


def test_neighbour_rank_is_none_for_a_non_neighbour():
    store = make_store(
        names=list("ABC"), popularity=[0.5] * 3, undirected_edges=[(0, 1, 0.9)]
    )
    assert neighbour_rank(store, 0, 2) is None


def test_render_html_is_self_contained():
    html = render_html(
        artifacts=[{"label": "control", "diagnostics": {"artists": 3, "edges": 4}}],
        panel_name="test",
        rows=[],
    )
    assert "<style" in html
    # A strict CSP applies to nothing here, but an external asset would make
    # the file useless when opened from disk.
    assert "http://" not in html and "https://" not in html


def test_render_html_marks_ceiling_hops_and_flagged_paths():
    rows = [
        {
            "pair": "A -> C",
            "cells": [
                {
                    "label": "control",
                    "hops": [
                        {"name": "A", "rank": None, "score": None, "degree": 2},
                        {"name": "B", "rank": 1, "score": 1.0, "degree": 900},
                        {"name": "C", "rank": 3, "score": 0.4, "degree": 2},
                    ],
                    "flagged": True,
                    "reasons": ["non-musical interior entity: 'B'"],
                }
            ],
        }
    ]
    html = render_html(artifacts=[{"label": "control", "diagnostics": {}}],
                       panel_name="test", rows=rows)
    assert "ceiling" in html      # the 1.0 hop is marked
    assert "flagged" in html
    assert "non-musical" in html
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_export_paths.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'export_paths'`

- [ ] **Step 3: Write the implementation**

```python
# api/eval/export_paths.py
"""Side-by-side path comparison as one self-contained HTML file.

RANK IS MANDATORY, NOT DECORATIVE. The defect that invalidated two analyses was
invisible in scores — twelve consecutive 1.0000s — and obvious in rank. A tool
that shows only scores would have missed it, exactly as the original review did.

Showing the DECODED PATH is equally mandatory. The opposite failure also
happened: neighbour rankings improved under a change whose routed paths got
worse. Both views, one screen.

Usage:
    cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python \\
        eval/export_paths.py out.html graph-a.bin graph-b.bin
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from artistpath_api.badpath import screen_path  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_path  # noqa: E402
from diagnostics import artifact_diagnostics  # noqa: E402
from panel import load_panel, resolve_pairs  # noqa: E402

_CSS = """
body{font:14px/1.5 system-ui,sans-serif;margin:2rem;background:#fff;color:#111}
table{border-collapse:collapse;width:100%;margin-bottom:2rem}
th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;vertical-align:top}
th{background:#f4f4f4}
.wrap{overflow-x:auto}
.hop{white-space:nowrap}
.ceiling{background:#ffe0e0;font-weight:600}
.hub{color:#a00}
.flagged{background:#fff4d6}
.reason{color:#a05000;font-size:12px}
.muted{color:#777;font-size:12px}
@media(prefers-color-scheme:dark){
 body{background:#111;color:#eee}th{background:#222}th,td{border-color:#333}
 .ceiling{background:#4a1f1f}.flagged{background:#3a3116}.reason{color:#e0b070}
}
"""


def neighbour_rank(store: GraphStore, u: int, v: int) -> int | None:
    """1-based rank of v within u's neighbour list, ordered by descending score.

    This is the view that makes a saturated ceiling visible: twelve neighbours
    all scoring 1.0000 look identical by score and are ranks 1-12 by position.
    """
    start, end = int(store.offsets[u]), int(store.offsets[u + 1])
    row_ids = store.neighbours[start:end]
    row_scores = store.scores[start:end]
    order = np.argsort(-row_scores, kind="stable")
    for rank, idx in enumerate(order, start=1):
        if int(row_ids[idx]) == v:
            return rank
    return None


def _hops(store: GraphStore, path: list[int], hub_cutoff: int) -> list[dict]:
    degrees = np.diff(store.offsets)
    out = []
    for position, node in enumerate(path):
        previous = path[position - 1] if position else None
        out.append(
            {
                "name": store.names[node] or f"<unnamed {node}>",
                "rank": neighbour_rank(store, previous, node) if previous is not None else None,
                "score": (
                    float(store.scores[
                        int(store.offsets[previous])
                        + int(np.searchsorted(
                            store.neighbours[
                                int(store.offsets[previous]):int(store.offsets[previous + 1])
                            ], node))
                    ])
                    if previous is not None
                    else None
                ),
                "degree": int(degrees[node]),
                "hub": bool(degrees[node] >= hub_cutoff),
            }
        )
    return out


def render_html(artifacts: list[dict], panel_name: str, rows: list[dict]) -> str:
    """One self-contained page. No external assets — it is opened from disk."""
    parts = [f"<title>artistpath path comparison</title><style>{_CSS}</style>"]
    parts.append(f"<h1>Path comparison — panel: {html.escape(panel_name)}</h1>")

    parts.append("<h2>Artifact diagnostics</h2><div class='wrap'><table><tr><th>metric</th>")
    for a in artifacts:
        parts.append(f"<th>{html.escape(a['label'])}</th>")
    parts.append("</tr>")
    keys = sorted({k for a in artifacts for k in a.get("diagnostics", {})})
    for key in keys:
        parts.append(f"<tr><td>{html.escape(key)}</td>")
        for a in artifacts:
            value = a.get("diagnostics", {}).get(key, "")
            shown = f"{value:.4g}" if isinstance(value, float) else str(value)
            parts.append(f"<td>{html.escape(shown)}</td>")
        parts.append("</tr>")
    parts.append("</table></div>")

    parts.append("<h2>Paths</h2><div class='wrap'><table><tr><th>pair</th>")
    for a in artifacts:
        parts.append(f"<th>{html.escape(a['label'])}</th>")
    parts.append("</tr>")
    for row in rows:
        parts.append(f"<tr><td>{html.escape(row['pair'])}</td>")
        for cell in row["cells"]:
            css = " class='flagged'" if cell.get("flagged") else ""
            parts.append(f"<td{css}>")
            for hop in cell["hops"]:
                classes = []
                if hop["score"] is not None and hop["score"] >= 1.0:
                    classes.append("ceiling")
                if hop.get("hub"):
                    classes.append("hub")
                attr = f" class='hop {' '.join(classes)}'" if classes else " class='hop'"
                detail = (
                    f" <span class='muted'>[rank {hop['rank']}, "
                    f"{hop['score']:.4f}, deg {hop['degree']}]</span>"
                    if hop["rank"] is not None
                    else f" <span class='muted'>[deg {hop['degree']}]</span>"
                )
                parts.append(f"<div{attr}>{html.escape(hop['name'])}{detail}</div>")
            for reason in cell.get("reasons", []):
                parts.append(f"<div class='reason'>⚠ {html.escape(reason)}</div>")
            parts.append("</td>")
        parts.append("</tr>")
    parts.append("</table></div>")
    return "".join(parts)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    out_path = Path(sys.argv[1])
    graph_paths = sys.argv[2:]

    panel = load_panel(Path(__file__).parent / "panel.json")
    stores = [(Path(p).name, GraphStore.load(p)) for p in graph_paths]
    cfg = ApiConfig()

    artifacts = [
        {"label": label, "diagnostics": artifact_diagnostics(store, cap=50)}
        for label, store in stores
    ]
    hub_cutoffs = {
        label: int(np.quantile(np.diff(store.offsets), 0.99))
        for label, store in stores
    }

    rows = []
    for stratum in ("hand_picked", "random", "obscure", "popularity_weighted"):
        for entry in panel["strata"].get(stratum, []):
            cells = []
            for label, store in stores:
                a = store.id_by_mbid.get(entry["from"])
                b = store.id_by_mbid.get(entry["to"])
                if a is None or b is None:
                    cells.append({"label": label, "hops": [], "flagged": False,
                                  "reasons": ["endpoint absent from this artifact"]})
                    continue
                path = find_path(store, a, b, [], cfg)
                if not path:
                    cells.append({"label": label, "hops": [], "flagged": False,
                                  "reasons": ["no path"]})
                    continue
                report = screen_path(store, path)
                cells.append(
                    {
                        "label": label,
                        "hops": _hops(store, path, hub_cutoffs[label]),
                        "flagged": report.flagged,
                        "reasons": report.reasons,
                    }
                )
            rows.append(
                {
                    "pair": f"[{stratum}] {entry['from_name']} -> {entry['to_name']}",
                    "cells": cells,
                }
            )

    out_path.write_text(render_html(artifacts, "panel.json", rows), encoding="utf-8")
    print(f"wrote {out_path} ({out_path.stat().st_size / 1000:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_export_paths.py -v`
Expected: PASS, 4 passed

- [ ] **Step 5: Produce the first real export and read it**

```bash
cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python eval/export_paths.py \
  ../scratch-export.html \
  ../builder/scratch/graph-75k-v3.bin ../builder/scratch/graph-75k-cosine.bin
```

Open it. **Confirm three things before proceeding:** the *La La Land* chain appears in the cosine column and is flagged; the v3 column shows a run of red `ceiling` hops; ranks are visible on every hop. If any is missing, the tool is not yet doing its job — fix it before Task 15 depends on it.

- [ ] **Step 6: Commit**

```bash
git add api/eval/export_paths.py api/tests/test_export_paths.py
git commit -m "feat(eval): side-by-side path exporter showing rank, score and degree"
```

---

## Task 10: Run the configuration-model experiment (Step A gate)

Implements spec §A3 and closes the standing contradiction between findings §2 ("hub-seeking is topological") and §5.1 ("caused by the scoring").

**Files:**
- Create: `docs/superpowers/findings/2026-07-22-configuration-model-null.md`
- Test: none — this is an experiment, not a component. Its correctness is Task 4's tests.

**Interfaces:**
- Consumes: Tasks 3, 4, 6 (`path_metrics`, `hub_node_set`, `configuration_model_rewire`, `degree_biased_walk`, panel).
- Produces: a finding that sets Task 14's damping grid.

- [ ] **Step 1: Write the experiment script**

Write to your scratch directory as `run_null_experiment.py` (throwaway — not committed):

```python
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "eval")

from artistpath_api.config import ApiConfig
from artistpath_api.evaluation import (
    bfs_shortest_path, hub_node_set, path_metrics, similarity_only_path, summarise,
)
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path
from nulls import configuration_model_rewire, degree_biased_walk
from panel import load_panel, resolve_pairs

store = GraphStore.load("../builder/scratch/graph-75k-v3.bin")
panel = load_panel("eval/panel.json")
hub_nodes = hub_node_set(store, 0.01)
cfg = ApiConfig()

pairs = []
for stratum in ("random", "obscure", "popularity_weighted"):
    got, dropped = resolve_pairs(store, panel, stratum)
    pairs.extend(got)
    if dropped:
        print(f"WARNING {stratum}: dropped {len(dropped)} unresolvable mbids")
print(f"{len(pairs)} pairs")

def measure(label, graph, router):
    metrics = []
    for a, b in pairs:
        path = router(graph, a, b)
        if path and len(path) >= 3:
            metrics.append(path_metrics(graph, path, hub_nodes))
    s = summarise(metrics)
    print(f"{label:34s} hubfrac {s['mean_hubfrac']:.4f}  "
          f"len {s['mean_length']:.1f}  maxdeg {s['mean_max_interior_degree']:.0f}")
    return s

print("\n--- OBSERVED GRAPH ---")
full = measure("FULL cost function", store, lambda g, a, b: find_path(g, a, b, [], cfg))
sim = measure("similarity-only", store, similarity_only_path)
bfs = measure("plain BFS", store, bfs_shortest_path)

print("\n--- WALK NULL (degree-biased) ---")
rng = np.random.default_rng(42)
walk_metrics = []
for (a, _b), length in zip(pairs, [int(round(full["mean_length"]))] * len(pairs)):
    walk = degree_biased_walk(store, a, length, rng)
    if len(walk) >= 3:
        walk_metrics.append(path_metrics(store, walk, hub_nodes))
walk = summarise(walk_metrics)
print(f"{'degree-biased walk':34s} hubfrac {walk['mean_hubfrac']:.4f}")

print("\n--- CONFIGURATION-MODEL NULL (rewired, degree sequence preserved) ---")
rewired = configuration_model_rewire(store, np.random.default_rng(42))
rewired_hub_nodes = hub_node_set(rewired, 0.01)
rw_metrics = []
for a, b in pairs:
    path = bfs_shortest_path(rewired, a, b)
    if path and len(path) >= 3:
        rw_metrics.append(path_metrics(rewired, path, rewired_hub_nodes))
rw = summarise(rw_metrics)
print(f"{'BFS on rewired graph':34s} hubfrac {rw['mean_hubfrac']:.4f}  "
      f"len {rw['mean_length']:.1f}")

print("\n--- ENRICHMENT vs walk null ---")
for label, s in (("FULL", full), ("sim-only", sim), ("BFS", bfs), ("BFS-rewired", rw)):
    print(f"  {label:14s} {s['mean_hubfrac'] / walk['mean_hubfrac']:.2f}x")
```

- [ ] **Step 2: Run it**

Run: `cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python run_null_experiment.py`

Expected runtime: ~15–25 minutes (130 pairs × 4 routers at ~4 s/path, plus the rewire).

- [ ] **Step 3: Interpret against the pre-registered decision rule**

> **JUDGEMENT STEP — required reading first:**
> `docs/superpowers/findings/2026-07-21-scoring-adjudication.md` **§5.3** (why
> the walk null alone licenses the wrong inference) and **§6 claims 19–22**
> (what this experiment is resolving).
>
> This step decides a question the committed record currently answers **both
> ways**: findings §2 said hub-seeking is topological, §5.1 said it is caused by
> the scoring. §2 was struck through on evidence that did not reproduce. Do not
> assume §5.1 is therefore correct — that is the mistake that produced this
> whole thread.
>
> **The decision rule below is pre-registered. Apply it to the numbers you get;
> do not adjust it to fit them.** "Topological" is an acceptable and useful
> answer that makes the rest of the phase cheaper.

Write the interpretation **before** looking at further numbers:

- **BFS-on-rewired hubfrac ≈ BFS-on-observed hubfrac** → hub-seeking is **topological**. The degree sequence alone explains it, no scoring change reaches it, findings §2 is reinstated, and the damping grid in Task 14 narrows to `d ∈ {0, 0.5}` as a confirmation rather than a search.
- **BFS-on-rewired hubfrac substantially lower** → hub-seeking depends on **community structure**, which scoring shapes. §5.1's conclusion survives its broken evidence, and Task 14 runs the full grid.

- [ ] **Step 4: Write the finding**

Create `docs/superpowers/findings/2026-07-22-configuration-model-null.md` with: the measured table, the command that produced it, the interpretation against the rule above, and an explicit statement of which of findings §2 / §5.1 it upholds. Follow the house rule — this is a new quantitative record, so it owns its numbers, and it must link from `2026-07-21-scoring-adjudication.md` §6 as the resolution of claims 19 and 22.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/findings/2026-07-22-configuration-model-null.md docs/superpowers/findings/2026-07-21-scoring-adjudication.md
git commit -m "findings: configuration-model null settles topological vs scoring hub-seeking"
```

---

# Track B — Builder changes

## Task 11: Entity filter

Implements spec §B3. A correctness fix worth ~0 on hub metrics — do not credit it with anything.

**Files:**
- Modify: `builder/src/artistpath_builder/config.py`, `builder/src/artistpath_builder/pipeline.py`
- Test: `builder/tests/test_pipeline_filters.py`

**Interfaces:**
- Consumes: `BuilderConfig`.
- Produces: `is_special_purpose(disambiguation: str) -> bool` in `pipeline.py`; `BuilderConfig.filter_special_purpose: bool = True`.

- [ ] **Step 1: Write the failing tests**

```python
# builder/tests/test_pipeline_filters.py
from artistpath_builder.pipeline import is_special_purpose


def test_flags_musicbrainz_special_purpose_artists():
    assert is_special_purpose("Special Purpose Artist - Do not add releases here")
    assert is_special_purpose("special purpose artist")
    assert is_special_purpose("SPECIAL PURPOSE")


def test_does_not_flag_real_bands_with_bracketed_names():
    # 22 nodes have bracketed names; 15 are real bands. A name-based filter
    # would delete all of them, which is why this matches on disambiguation.
    for disambiguation in (
        "",
        "Swedish indiepopband",
        "Shadows in the Dark",
        "ex-[Champagne]",
        "UK drum & bass producers Andy C & Ant Miles",
    ):
        assert not is_special_purpose(disambiguation)


def test_handles_none_and_empty():
    assert not is_special_purpose("")
    assert not is_special_purpose(None)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_pipeline_filters.py -v`
Expected: FAIL with `ImportError: cannot import name 'is_special_purpose'`

- [ ] **Step 3: Add the config knob**

In `builder/src/artistpath_builder/config.py`, under `# --- graph ---`:

```python
    # Drop MusicBrainz placeholder entities ([unknown], [traditional],
    # [no artist], [anonymous], [theatre], [dialogue], [Disney]). Matched on
    # the DISAMBIGUATION field, never the name: 22 nodes have bracketed names
    # and 15 of them are real bands. This is a correctness fix and is worth
    # approximately nothing on hub metrics — see the Phase 2 spec §1.5.
    filter_special_purpose: bool = True
```

- [ ] **Step 4: Implement the filter**

In `builder/src/artistpath_builder/pipeline.py`, add near the top:

```python
import re

# MusicBrainz marks placeholder entities in the disambiguation field.
_SPECIAL_PURPOSE = re.compile(r"special purpose", re.IGNORECASE)


def is_special_purpose(disambiguation: str | None) -> bool:
    """True for MusicBrainz placeholder entities, matched on disambiguation."""
    return bool(_SPECIAL_PURPOSE.search(disambiguation or ""))
```

Then in `build_from_archive`, immediately after `identities = harvest_identities(...)` and **before** the Pass 1 mass computation, insert:

```python
    # Drop placeholder entities BEFORE the mass computation, so they
    # contribute to no marginal. Mass is computed over the full uncapped
    # neighbour list, so leaving them in would perturb every score slightly.
    if config.filter_special_purpose:
        excluded = {
            mbid
            for mbid, (_name, disambiguation) in identities.items()
            if is_special_purpose(disambiguation)
        }
        if excluded:
            logger.info("filtered %d special-purpose entities", len(excluded))
        known -= excluded
    else:
        excluded = set()
```

Then in Pass 1, change the neighbour parse to drop excluded neighbours:

```python
    for mbid in sorted(known):
        neighbours = [
            n
            for n in source.parse(payloads[mbid], exclude_mbid=mbid)
            if n.mbid not in excluded
        ]
        raw_lists[mbid] = neighbours
        mass[mbid] = sum(n.score for n in neighbours) or 1.0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, all tests including the 3 new ones. **`test_replay.py` must still pass unmodified.**

- [ ] **Step 6: Commit**

```bash
git add builder/src/artistpath_builder/config.py builder/src/artistpath_builder/pipeline.py builder/tests/test_pipeline_filters.py
git commit -m "feat(builder): drop MusicBrainz special-purpose entities by disambiguation"
```

---

## Task 12: Symmetrisation-aware neighbour cap

Implements spec §B4 precondition 1. The cap is currently applied before symmetrisation, so it truncates the obscure tail while leaving hubs unbounded — a configured cap of 50 against an observed maximum of 11,243.

**Files:**
- Modify: `builder/src/artistpath_builder/config.py`, `builder/src/artistpath_builder/graph.py`, `builder/src/artistpath_builder/pipeline.py`
- Test: `builder/tests/test_graph.py`

**Interfaces:**
- Consumes: `Adjacency` (`dict[str, dict[str, float]]`).
- Produces: `mutual_knn_cap(adjacency, k) -> Adjacency` in `graph.py`; `BuilderConfig.cap_strategy: str` with values `"pre_symmetrise"` (current) and `"mutual_knn"`.

- [ ] **Step 1: Write the failing tests**

Append to `builder/tests/test_graph.py`:

```python
from artistpath_builder.graph import mutual_knn_cap


def test_mutual_knn_bounds_every_node_degree():
    # A star: the centre "hub" is in everyone's list, so pre-symmetrisation
    # capping leaves it unbounded. Mutual k-NN must bound it at k.
    adjacency = {"hub": {}}
    for i in range(10):
        leaf = f"leaf{i}"
        adjacency["hub"][leaf] = 1.0 - i * 0.01
        adjacency[leaf] = {"hub": 1.0}
    capped = mutual_knn_cap(adjacency, k=3)
    assert all(len(edges) <= 3 for edges in capped.values())


def test_mutual_knn_keeps_only_edges_in_both_top_k():
    # a's top-1 is b; b's top-1 is c. So a-b survives only if b also ranks a
    # first, which it does not.
    adjacency = {
        "a": {"b": 0.9, "c": 0.1},
        "b": {"c": 0.9, "a": 0.5},
        "c": {"b": 0.9, "a": 0.1},
    }
    capped = mutual_knn_cap(adjacency, k=1)
    assert "b" in capped["c"] and "c" in capped["b"]
    assert "b" not in capped.get("a", {})


def test_mutual_knn_output_is_symmetric():
    adjacency = {
        "a": {"b": 0.9, "c": 0.8},
        "b": {"a": 0.9, "c": 0.7},
        "c": {"a": 0.8, "b": 0.7},
    }
    capped = mutual_knn_cap(adjacency, k=2)
    for src, edges in capped.items():
        for dst, score in edges.items():
            assert capped[dst][src] == score


def test_mutual_knn_breaks_score_ties_on_lowest_mbid():
    # Determinism (design §9): equal scores must resolve the same way every run.
    adjacency = {
        "a": {"b": 0.5, "c": 0.5},
        "b": {"a": 0.5},
        "c": {"a": 0.5},
    }
    first = mutual_knn_cap(adjacency, k=1)
    second = mutual_knn_cap(adjacency, k=1)
    assert first == second
    assert "b" in first["a"]  # lowest mbid wins the tie


def test_mutual_knn_is_a_noop_below_the_cap():
    adjacency = {"a": {"b": 0.9}, "b": {"a": 0.9}}
    assert mutual_knn_cap(adjacency, k=50) == adjacency
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_graph.py -v`
Expected: FAIL with `ImportError: cannot import name 'mutual_knn_cap'`

- [ ] **Step 3: Implement the cap**

Add to `builder/src/artistpath_builder/graph.py`:

```python
def mutual_knn_cap(adjacency: Adjacency, k: int) -> Adjacency:
    """Keep edge (u,v) only if v is in u's top-k AND u is in v's top-k.

    The cap this replaces was applied BEFORE symmetrisation. Symmetrisation
    adds a reverse edge for every incoming one and nothing bounds how many
    neighbour lists an artist appears in, so the cap truncated the obscure
    tail — where alternative routes are scarcest — while leaving hubs
    completely unbounded. A configured cap of 50 produced an observed maximum
    degree of 11,243.

    Mutual k-NN is the only formulation that both bounds degree at k and stays
    symmetric by construction: union-kNN does not bound degree, and capping
    after symmetrisation breaks symmetry again. It prunes harder than the old
    scheme, so callers must check largest-component retention.

    Ties break on lowest MBID, matching every other ordering decision in this
    module (design §9).
    """
    top_k: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(edges.items(), key=lambda pair: (-pair[1], pair[0]))
        top_k[node] = {dst for dst, _score in ranked[:k]}

    result: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in top_k[node] and node in top_k.get(dst, set()):
                result[node][dst] = score
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_graph.py -v`
Expected: PASS

- [ ] **Step 5: Add the config knob and wire it in**

In `builder/src/artistpath_builder/config.py`:

```python
    # How the neighbour cap is applied.
    #   "pre_symmetrise" — legacy: cap each artist's own list, then symmetrise.
    #                      Bounds nothing after symmetrisation.
    #   "mutual_knn"     — keep an edge only if each endpoint ranks the other
    #                      in its top-k. Bounds degree at k, stays symmetric.
    # Retained as a knob only until Phase 2 concludes; delete the loser then
    # (Phase 2 spec §8 risk 4).
    cap_strategy: str = "pre_symmetrise"
```

In `builder/src/artistpath_builder/pipeline.py`, replace the cap-and-symmetrise section. The current line 100 is:

```python
        scored_adjacency[mbid] = scored[: config.max_neighbours_per_artist]
```

Change it to keep the full list when using mutual k-NN, because that strategy needs every candidate before deciding:

```python
        scored_adjacency[mbid] = (
            scored
            if config.cap_strategy == "mutual_knn"
            else scored[: config.max_neighbours_per_artist]
        )
```

Then replace line 127 (`adjacency = symmetrise(adjacency)`) with:

```python
    if config.cap_strategy == "mutual_knn":
        adjacency = mutual_knn_cap(adjacency, config.max_neighbours_per_artist)
    adjacency = symmetrise(adjacency)
```

Add `mutual_knn_cap` to the `from artistpath_builder.graph import (...)` block.

- [ ] **Step 6: Add the cap-invariant test**

Append to `builder/tests/test_graph.py`:

```python
def test_symmetrise_preserves_the_mutual_knn_degree_bound():
    # The invariant the old scheme never satisfied: after symmetrisation, no
    # node exceeds the cap. Nothing in the codebase asserted this, which is how
    # a cap of 50 and a max degree of 11,243 coexisted unnoticed.
    adjacency = {"hub": {}}
    for i in range(20):
        leaf = f"leaf{i:02d}"
        adjacency["hub"][leaf] = 1.0 - i * 0.01
        adjacency[leaf] = {"hub": 1.0}
    capped = symmetrise(mutual_knn_cap(adjacency, k=4))
    assert max(len(edges) for edges in capped.values()) <= 4
```

- [ ] **Step 7: Run the full builder suite**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, all tests. `test_replay.py` unmodified and green.

- [ ] **Step 8: Verify component retention on the real graph — this is a GATE**

Build the cap-fix arm and check retention:

```bash
cd builder && UV_LINK_MODE=copy uv run python -c "
from artistpath_builder.config import BuilderConfig
from artistpath_builder.archive import LocalArchive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.pipeline import build_from_archive
from pathlib import Path
for strategy in ('pre_symmetrise', 'mutual_knn'):
    cfg = BuilderConfig(cap_strategy=strategy)
    g = build_from_archive(cfg, LocalArchive(Path('./scratch/graph-archive')), ListenBrainzSource(cfg))
    print(f'{strategy:16s} artists={g.artist_count:,} edges={g.edge_count:,}')
"
```

**Gate:** if `mutual_knn` retains fewer than 90 % of `pre_symmetrise`'s artists, **stop and report**. Mutual k-NN disconnects the periphery, and losing a tenth of the graph is a worse defect than the one being fixed. Fall back to raising `max_neighbours_per_artist` alongside the strategy change, and re-measure.

- [ ] **Step 9: Commit**

```bash
git add builder/src/artistpath_builder/graph.py builder/src/artistpath_builder/config.py builder/src/artistpath_builder/pipeline.py builder/tests/test_graph.py
git commit -m "feat(builder): symmetrisation-aware mutual k-NN neighbour cap"
```

---

## Task 13: Rescale strategy — rank transform, with byte-identity preserved for the control

Implements spec §B4 precondition 2. The p99 clip yields zero-cost edges in every build; 30–82 % of routed hops currently cost zero similarity.

**Files:**
- Modify: `builder/src/artistpath_builder/config.py`, `builder/src/artistpath_builder/pipeline.py`
- Test: `builder/tests/test_pipeline_rescale.py`

**Interfaces:**
- Consumes: `BuilderConfig`.
- Produces: `rescale_scores(values: list[float], strategy: str, damping: float) -> list[float]` in `pipeline.py`; `BuilderConfig.similarity_rescale: str` with values `"p99_log_clip"` (current) and `"percentile_rank"`.

> ### ⚠ This task and Task 14 are coupled. Do not reorder them.
>
> **Task 13 writes `rescale_scores` expecting RAW co-occurrence values.
> Task 14 changes every caller to pass LOG-SPACE values**, and therefore
> modifies the `p99_log_clip` branch to `expm1` its input back to raw space.
>
> That round-trip is exact only at `d = 0` — which is fine, because `d = 0` is
> the only arm that uses the legacy rescale. But if Task 14 lands without that
> change, the control arm silently applies `log1p` twice, byte-identity breaks,
> and every downstream comparison is invalid.
>
> **Task 14 Step 5 re-runs this task's byte-identity check.** That gate is what
> catches the mistake. Do not skip it, and do not "fix" a byte-identity failure
> by relaxing the assertion.

- [ ] **Step 1: Write the failing tests**

```python
# builder/tests/test_pipeline_rescale.py
import math

import numpy as np
import pytest

from artistpath_builder.pipeline import rescale_scores


def test_p99_log_clip_reproduces_the_legacy_expression_exactly():
    # Byte-identity for the control arm. The legacy expression is
    # min(1, log1p(v) / log1p(p99)), with p99 computed in RAW space —
    # np.percentile with linear interpolation does not commute with log1p.
    values = [float(i) for i in range(1, 201)]
    scale = float(np.percentile(values, 99))
    expected = [min(1.0, math.log1p(v) / math.log1p(scale)) for v in values]
    got = rescale_scores(values, strategy="p99_log_clip", damping=0.0)
    assert got == pytest.approx(expected, abs=0.0)


def test_percentile_rank_is_uniform_and_has_no_ceiling_tie_mass():
    values = [float(i) for i in range(1, 1001)]
    got = rescale_scores(values, strategy="percentile_rank", damping=0.0)
    assert min(got) >= 0.0 and max(got) <= 1.0
    # A rank transform has at most one value at the ceiling, unlike the clip
    # which saturates ~1% of edges by construction.
    assert sum(1 for g in got if g >= 1.0) <= 1
    assert 0.45 <= float(np.median(got)) <= 0.55


def test_percentile_rank_preserves_ordering():
    values = [5.0, 1.0, 3.0, 9.0]
    got = rescale_scores(values, strategy="percentile_rank", damping=0.0)
    assert sorted(range(4), key=lambda i: values[i]) == sorted(
        range(4), key=lambda i: got[i]
    )


def test_percentile_rank_handles_negative_values():
    # Damping in log space produces negatives. A rank transform handles them;
    # the clamp this replaces collapsed them all into one tie at the floor.
    values = [-3.0, -1.0, 0.0, 2.0]
    got = rescale_scores(values, strategy="percentile_rank", damping=0.5)
    assert all(0.0 <= g <= 1.0 for g in got)
    assert got[0] < got[1] < got[2] < got[3]


def test_rescale_never_emits_nan_or_all_zero():
    # The degeneracy guard. Dropping the centring under the clip rescale
    # clamps 99.98% of edges at d=0.5 and makes p99(raw) == 0, which emits nan.
    # That must fail loudly, never ship silently.
    for strategy in ("p99_log_clip", "percentile_rank"):
        for damping in (0.0, 0.25, 0.5, 0.75, 1.0):
            got = rescale_scores(
                [float(i) for i in range(1, 101)], strategy=strategy, damping=damping
            )
            assert not any(math.isnan(g) for g in got), (strategy, damping)
            assert any(g > 0.0 for g in got), (strategy, damping)


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="unknown rescale strategy"):
        rescale_scores([1.0], strategy="nope", damping=0.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_pipeline_rescale.py -v`
Expected: FAIL with `ImportError: cannot import name 'rescale_scores'`

- [ ] **Step 3: Add the config knob**

In `builder/src/artistpath_builder/config.py`:

```python
    # How raw edge strength is mapped into 0-1.
    #   "p99_log_clip"    — legacy: min(1, log1p(v)/log1p(p99)). Saturates ~1%
    #                       of edges at exactly 1.0, and those cost
    #                       w_sim*(1-1.0) == 0 — free similarity. 30-82% of
    #                       routed hops currently sit at that ceiling.
    #   "percentile_rank" — rank transform. No ceiling tie-mass, and it handles
    #                       the negative values that log-space damping produces
    #                       without a clamp.
    # Retained as a knob only until Phase 2 concludes (spec §8 risk 4).
    similarity_rescale: str = "p99_log_clip"
```

- [ ] **Step 4: Implement `rescale_scores`**

Add to `builder/src/artistpath_builder/pipeline.py`:

```python
def rescale_scores(
    values: list[float], strategy: str, damping: float
) -> list[float]:
    """Map raw edge strengths into 0-1.

    `damping` is accepted so the degeneracy guard can be enforced here: under
    the clip rescale with d > 0 the centring term is mandatory, and without it
    the p99 collapses to zero and the whole array becomes nan.
    """
    if not values:
        return []

    if strategy == "p99_log_clip":
        scale = float(np.percentile(values, 99))
        if scale <= 0:
            raise ValueError(
                f"degenerate p99 ({scale}) under damping={damping}: the clip "
                "rescale requires the centring term when damping > 0. Use "
                "percentile_rank, or restore the centring."
            )
        log_scale = math.log1p(scale)
        return [
            min(1.0, math.log1p(max(0.0, v)) / log_scale) for v in values
        ]

    if strategy == "percentile_rank":
        order = np.argsort(np.asarray(values, dtype=np.float64), kind="stable")
        ranks = np.empty(len(values), dtype=np.float64)
        ranks[order] = np.arange(len(values), dtype=np.float64)
        denominator = max(len(values) - 1, 1)
        return [float(r / denominator) for r in ranks]

    raise ValueError(f"unknown rescale strategy: {strategy!r}")
```

- [ ] **Step 5: Wire it into `build_from_archive`**

Replace the rescale block in `pipeline.py` (currently lines 102–125) with:

```python
    # Map raw strength into 0-1 per the configured strategy. See
    # BuilderConfig.similarity_rescale for why the legacy clip is a defect.
    flat: list[float] = []
    layout: list[tuple[str, list[str]]] = []
    for mbid, scored in scored_adjacency.items():
        layout.append((mbid, [dst for dst, _ in scored]))
        flat.extend(value for _dst, value in scored)

    rescaled = rescale_scores(
        flat, strategy=config.similarity_rescale, damping=config.similarity_damping
    )

    indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    cursor = 0
    for mbid, dsts in layout:
        edges = {}
        for dst in dsts:
            edges[dst] = rescaled[cursor]
            cursor += 1
        adjacency[mbid] = edges
        for dst, score in edges.items():
            indegree[dst] += score
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, all tests

- [ ] **Step 7: Prove byte-identity of the control arm**

```bash
cd builder && UV_LINK_MODE=copy uv run artistpath-build build \
  --archive-dir ./scratch/graph-archive --out scratch/graph-control.bin
python -c "
import hashlib, pathlib
a = hashlib.sha256(pathlib.Path('scratch/graph-control.bin').read_bytes()).hexdigest()
b = hashlib.sha256(pathlib.Path('scratch/graph-75k-v3.bin').read_bytes()).hexdigest()
print('control', a)
print('v3     ', b)
print('IDENTICAL' if a == b else 'DIFFERENT — investigate before proceeding')
"
```

**Gate:** the default config (`pre_symmetrise`, `p99_log_clip`, `d = 0.0`) must reproduce `graph-75k-v3.bin` **byte for byte**, except that `filter_special_purpose = True` now removes 7 nodes. So expect DIFFERENT — re-run with `filter_special_purpose=False` to confirm the refactor itself changed nothing:

```bash
cd builder && UV_LINK_MODE=copy uv run python -c "
from artistpath_builder.config import BuilderConfig
from artistpath_builder.archive import LocalArchive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.artifact import serialise
from pathlib import Path
import hashlib
cfg = BuilderConfig(filter_special_purpose=False)
g = build_from_archive(cfg, LocalArchive(Path('./scratch/graph-archive')), ListenBrainzSource(cfg))
print(hashlib.sha256(serialise(g)).hexdigest())
print(hashlib.sha256(Path('scratch/graph-75k-v3.bin').read_bytes()).hexdigest())
"
```

These two **must** match. If they do not, the refactor changed behaviour and every downstream comparison is invalid — stop and fix.

- [ ] **Step 8: Commit**

```bash
git add builder/src/artistpath_builder/config.py builder/src/artistpath_builder/pipeline.py builder/tests/test_pipeline_rescale.py
git commit -m "feat(builder): percentile-rank rescale strategy; byte-identical legacy path"
```

---

## Task 14: Damping in log space

Implements spec §B4 Factor d. Damping currently multiplies the raw score before `log1p`; it must be applied in log space so it composes correctly with the rank rescale.

**Files:**
- Modify: `builder/src/artistpath_builder/pipeline.py`
- Test: `builder/tests/test_pipeline_damping.py`

**Interfaces:**
- Consumes: `BuilderConfig.similarity_damping`, `BuilderConfig.similarity_rescale`.
- Produces: `damped_strength(cooc, mass_a, mass_b, damping) -> float` in `pipeline.py`.

> ### ⚠ Read before starting: this task breaks Task 13's assumption on purpose.
>
> Task 13 wrote `rescale_scores` expecting **raw co-occurrence** input. This
> task makes every caller pass **log-space** values instead, because
> `damped_strength` returns `log1p(cooc) − d·(…)`.
>
> **Step 4 therefore MUST change the `p99_log_clip` branch to `expm1` its input
> back to raw space.** Skip it and the control arm applies `log1p` twice: the
> scores change, byte-identity with `graph-75k-v3.bin` breaks, and every arm
> comparison in Task 15 becomes uninterpretable — the exact class of error that
> invalidated two prior analyses in this project.
>
> The `expm1`/`log1p` round-trip is exact only at `d = 0`. That is acceptable
> because `d = 0` is the only arm using the legacy rescale; every damped arm
> uses `percentile_rank`. **Step 5's byte-identity re-check is the gate.**

- [ ] **Step 1: Write the failing tests**

```python
# builder/tests/test_pipeline_damping.py
import math

import pytest

from artistpath_builder.pipeline import damped_strength


def test_damping_zero_is_plain_log1p():
    assert damped_strength(100.0, 1000.0, 2000.0, damping=0.0) == pytest.approx(
        math.log1p(100.0)
    )


def test_damping_subtracts_log_mass_in_log_space():
    # log1p(cooc) - d * (log m_a + log m_b)
    expected = math.log1p(100.0) - 0.5 * (math.log(1000.0) + math.log(2000.0))
    assert damped_strength(100.0, 1000.0, 2000.0, damping=0.5) == pytest.approx(
        expected
    )


def test_damping_penalises_the_popular_pair_more():
    # Same co-occurrence, different marginals: the popular pair must score lower.
    obscure = damped_strength(50.0, 100.0, 100.0, damping=0.5)
    popular = damped_strength(50.0, 10000.0, 10000.0, damping=0.5)
    assert obscure > popular


def test_negative_results_are_returned_not_clamped():
    # The clamp this replaces collapsed everything below zero into one tie at
    # the floor — the ceiling defect mirrored. The rank rescale handles
    # negatives natively.
    assert damped_strength(1.0, 100000.0, 100000.0, damping=1.0) < 0.0


def test_zero_mass_does_not_raise():
    assert math.isfinite(damped_strength(10.0, 0.0, 0.0, damping=0.5))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest tests/test_pipeline_damping.py -v`
Expected: FAIL with `ImportError: cannot import name 'damped_strength'`

- [ ] **Step 3: Implement it**

Add to `builder/src/artistpath_builder/pipeline.py`:

```python
def damped_strength(
    cooc: float, mass_a: float, mass_b: float, damping: float
) -> float:
    """Popularity-damped edge strength, computed IN LOG SPACE.

        log1p(cooc) - d * (log mass_a + log mass_b)

    d = 0 is raw association, d = 0.5 is cosine, d = 1 is PMI up to a constant.

    No `- 2*log(median_mass)` centring: under the rank rescale it is a global
    additive constant and provably inert. It is mandatory only under the legacy
    clip rescale, where `rescale_scores` raises rather than silently emitting
    nan.

    No clamp at zero. Negative values are meaningful ordering information and
    the rank transform consumes them directly.
    """
    strength = math.log1p(max(0.0, cooc))
    if damping:
        strength -= damping * (math.log(max(mass_a, 1.0)) + math.log(max(mass_b, 1.0)))
    return strength
```

- [ ] **Step 4: Wire it into Pass 2**

In `build_from_archive`, replace the Pass 2 scoring comprehension (currently lines 88–100):

```python
    for mbid in sorted(known):
        mass_a = mass[mbid]
        scored = [
            (n.mbid, damped_strength(n.score, mass_a, mass[n.mbid], damping))
            for n in raw_lists[mbid]
            if n.mbid in known
        ]
        # Cap AFTER correction — the corrected ranking differs from the raw one.
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        scored_adjacency[mbid] = (
            scored
            if config.cap_strategy == "mutual_knn"
            else scored[: config.max_neighbours_per_artist]
        )
```

Then in `rescale_scores`'s `p99_log_clip` branch, the input is now already log-space, so the legacy path must not apply `log1p` twice. Change the branch to accept a pre-logged input flag — simplest correct form:

```python
    if strategy == "p99_log_clip":
        # Legacy path: input is already log1p(cooc) from damped_strength at
        # d = 0, so exponentiate back to raw space to reproduce the original
        # expression exactly. Only valid at d = 0, which is the control arm.
        raw = [math.expm1(max(0.0, v)) for v in values]
        scale = float(np.percentile(raw, 99))
        ...
```

- [ ] **Step 5: Re-verify byte-identity**

Re-run Task 13 Step 7's second command. The hashes **must** still match. If they do not, the log-space refactor changed the control arm — stop and fix.

- [ ] **Step 6: Run the full builder suite and Snyk**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, all tests

Run `snyk_code_scan` on `builder/src/artistpath_builder`. Expected: 0 issues.

- [ ] **Step 7: Commit**

```bash
git add builder/src/artistpath_builder/pipeline.py builder/tests/test_pipeline_damping.py
git commit -m "feat(builder): apply damping in log space without centring or clamping"
```

---

## Task 15: Build the arms, evaluate, decide

The experiment. Everything before this exists to make this task's answer trustworthy.

**Files:**
- Modify: `api/eval/run_baseline.py` (rewrite to drive the panel and emit the full results table)
- Create: `docs/superpowers/findings/2026-07-22-phase2-sweep-results.md`

**Interfaces:**
- Consumes: every Track A component and every Track B knob.
- Produces: an adoption decision, and the adopted artifact's sha256.

**Build sequence** (spec §B5) — each arm adopted or rejected on its own evidence before the next:

| Arm | `cap_strategy` | `similarity_rescale` | `similarity_damping` |
|---|---|---|---|
| 1 control | `pre_symmetrise` | `p99_log_clip` | 0.0 |
| 2 cap fix | `mutual_knn` | `p99_log_clip` | 0.0 |
| 3 rescale fix | `mutual_knn` | `percentile_rank` | 0.0 |
| 4 damping | `mutual_knn` | `percentile_rank` | 0.25 |
| 5 damping | `mutual_knn` | `percentile_rank` | 0.5 |
| 6 damping | `mutual_knn` | `percentile_rank` | 0.75 |

**Entity filter is ON in every arm**, so it is never confounded with anything.

- [ ] **Step 1: Rewrite `run_baseline.py`**

Replace the whole file. It must: load `panel.json`; resolve the analysis slice (`held_out=False`) per arm; run the FULL router **and** a `w_jump = 0` router (spec §6.1, resolving the popularity confound at evaluation time rather than with an extra build); compute `summarise` plus the bad-path count; emit `artifact_diagnostics`; and write per-pair metric vectors to a JSON file so Task 15 Step 4 can run paired tests without re-routing.

```python
# api/eval/run_baseline.py
"""Evaluate one artifact over the frozen panel.

Usage:
    cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python \\
        eval/run_baseline.py <graph.bin> <label> [--held-out]

Writes eval/results-<label>.json with per-pair metric vectors, so paired
significance tests run later without re-routing 130 paths.
"""

from __future__ import annotations

import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from artistpath_api.badpath import screen_path
from artistpath_api.config import ApiConfig
from artistpath_api.evaluation import (
    PathMetrics,
    hub_node_set,
    path_metrics,
    summarise,
)
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path
from diagnostics import artifact_diagnostics
from panel import load_panel, resolve_pairs

AGGREGATED = ("random", "obscure", "popularity_weighted")
HUB_SET_CACHE = Path(__file__).parent / "hub-nodes-control.json"


def load_or_freeze_hub_set(store: GraphStore) -> set[int]:
    """Hub set frozen by MBID from the control build.

    A per-graph top-1% threshold moves between builds (363 vs 278 measured),
    so a variant could "improve" purely by compressing its degree distribution.
    """
    if HUB_SET_CACHE.exists():
        mbids = json.loads(HUB_SET_CACHE.read_text(encoding="utf-8"))
        return {store.id_by_mbid[m] for m in mbids if m in store.id_by_mbid}
    nodes = hub_node_set(store, 0.01)
    HUB_SET_CACHE.write_text(
        json.dumps(sorted(store.mbids[i] for i in nodes)), encoding="utf-8"
    )
    return nodes


def main() -> int:
    graph_path, label = sys.argv[1], sys.argv[2]
    held_out = "--held-out" in sys.argv

    store = GraphStore.load(graph_path)
    panel = load_panel(Path(__file__).parent / "panel.json")
    hub_nodes = load_or_freeze_hub_set(store)

    full_cfg = ApiConfig()
    # w_jump = 0 removes the popularity channel entirely: w_floor is a proven
    # no-op and w_hub is dormant, so cost reduces to w_sim*(1-sim) + w_hop.
    # Popularity is derived from the scores, so it is NOT frozen across arms
    # even with identical weights (spec §6.1).
    no_jump_cfg = dataclasses.replace(full_cfg, w_jump=0.0)

    output: dict = {"label": label, "graph": graph_path, "held_out": held_out}
    output["diagnostics"] = artifact_diagnostics(store, cap=50)

    for router_name, cfg in (("full", full_cfg), ("w_jump_0", no_jump_cfg)):
        per_pair: list[dict] = []
        metrics: list[PathMetrics] = []
        flagged = 0
        started = time.time()
        for stratum in AGGREGATED:
            pairs, dropped = resolve_pairs(
                store, panel, stratum, held_out=held_out
            )
            if dropped:
                print(f"WARNING {stratum}: {len(dropped)} unresolvable mbids: {dropped[:3]}")
            for a, b in pairs:
                path = find_path(store, a, b, [], cfg)
                if not path or len(path) < 3:
                    continue
                m = path_metrics(store, path, hub_nodes)
                report = screen_path(store, path)
                flagged += int(report.flagged)
                metrics.append(m)
                per_pair.append(
                    {
                        "stratum": stratum,
                        "from": store.mbids[a],
                        "to": store.mbids[b],
                        **dataclasses.asdict(m),
                        "flagged": report.flagged,
                    }
                )
        output[router_name] = {
            "per_pair": per_pair,
            "summary": summarise(metrics),
            "flagged_paths": flagged,
            "seconds": round(time.time() - started, 1),
        }
        s = output[router_name]["summary"]
        print(
            f"{label:22s} {router_name:9s} n={s.get('n', 0):3d} "
            f"AA {s.get('mean_adamic_adar', 0):.4f}  "
            f"OC {s.get('mean_overlap_coefficient', 0):.4f}  "
            f"hubfrac {s.get('mean_hubfrac', 0):.4f}  "
            f"ceiling {s.get('mean_ceiling_hops', 0):.3f}  "
            f"len {s.get('mean_length', 0):.1f}  flagged {flagged}"
        )

    suffix = "-heldout" if held_out else ""
    out = Path(__file__).parent / f"results-{label}{suffix}.json"
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Build all six arms**

Read `builder/scratch/BUILD-TIMING.txt` (written by Task 1 Step 7) and multiply by six. If that total exceeds ~30 minutes, run the loop below with `run_in_background` rather than interactively.

```bash
cd builder
for arm in \
  "control:pre_symmetrise:p99_log_clip:0.0" \
  "capfix:mutual_knn:p99_log_clip:0.0" \
  "rankfix:mutual_knn:percentile_rank:0.0" \
  "d025:mutual_knn:percentile_rank:0.25" \
  "d050:mutual_knn:percentile_rank:0.5" \
  "d075:mutual_knn:percentile_rank:0.75" ; do
  IFS=: read -r name cap rescale damping <<< "$arm"
  UV_LINK_MODE=copy uv run python -c "
from artistpath_builder.config import BuilderConfig
from artistpath_builder.archive import LocalArchive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.artifact import serialise
from artistpath_builder.manifest import build_manifest, write_manifest
from pathlib import Path
import time
cfg = BuilderConfig(cap_strategy='$cap', similarity_rescale='$rescale', similarity_damping=$damping)
t = time.monotonic()
g = build_from_archive(cfg, LocalArchive(Path('./scratch/graph-archive')), ListenBrainzSource(cfg))
payload = serialise(g)
out = Path('scratch/graph-$name.bin')
out.write_bytes(payload)
write_manifest(out, build_manifest(g, cfg, payload, time.monotonic() - t))
print('$name', g.artist_count, g.edge_count)
"
done
```

**Assert the node sets match** before comparing anything:

```bash
cd api && UV_LINK_MODE=copy uv run python -c "
from artistpath_api.graph_store import GraphStore
import sys
names = ['control','capfix','rankfix','d025','d050','d075']
stores = {n: GraphStore.load(f'../builder/scratch/graph-{n}.bin') for n in names}
base = stores['control'].mbids
for n, s in stores.items():
    same = s.mbids == base
    print(f'{n:8s} artists={s.artist_count:,} node_set_identical={same}')
"
```

If a node set differs, `resolve_pairs` will report drop-outs and the comparison restricts to the intersection — that is handled, but **record it in the findings**.

- [ ] **Step 3: Evaluate every arm on the analysis slice**

```bash
cd api
for n in control capfix rankfix d025 d050 d075; do
  PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python eval/run_baseline.py \
    ../builder/scratch/graph-$n.bin $n
done
```

The hub set is frozen from whichever arm runs first — run `control` first so it anchors.

- [ ] **Step 4: Run the paired tests**

```bash
cd api && UV_LINK_MODE=copy uv run python -c "
import json, sys
from pathlib import Path
sys.path.insert(0, 'eval')
from stats import holm_correct, paired_comparison

arms = ['capfix','rankfix','d025','d050','d075']
control = json.loads(Path('eval/results-control.json').read_text())
for metric in ('adamic_adar','overlap_coefficient','hubfrac','ceiling_hops'):
    print(f'\n=== {metric} ===')
    raw = []
    for arm in arms:
        cand = json.loads(Path(f'eval/results-{arm}.json').read_text())
        key = lambda r: (r['from'], r['to'])
        c = {key(r): r[metric] for r in control['full']['per_pair']}
        a = {key(r): r[metric] for r in cand['full']['per_pair']}
        shared = sorted(set(c) & set(a))
        res = paired_comparison([c[k] for k in shared], [a[k] for k in shared])
        raw.append((arm, res))
    corrected = holm_correct([r['p_value'] for _a, r in raw])
    for (arm, res), p in zip(raw, corrected):
        print(f'  {arm:8s} n={res[\"n\"]:3d} median_delta {res[\"median_delta\"]:+.4f} p={p:.4f}')
"
```

- [ ] **Step 5: Export paths and read them**

```bash
cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python eval/export_paths.py \
  ../phase2-comparison.html \
  ../builder/scratch/graph-control.bin ../builder/scratch/graph-capfix.bin \
  ../builder/scratch/graph-rankfix.bin ../builder/scratch/graph-d025.bin \
  ../builder/scratch/graph-d050.bin ../builder/scratch/graph-d075.bin
```

**Read it.** This is adoption criterion 5 and it is not delegable to the metrics — every overlap objective scores the *La La Land* path well.

- [ ] **Step 6: Apply the adoption criterion**

> ### 🛑 STOP — human decision point. Do not decide this autonomously.
>
> **Required reading:** `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`
> **§4.3** (overlap metrics are blind to the failure mode), **§6** (27 prior
> claims and their status), and **§7** (what follows for Phase 2).
>
> Present the evidence and the recommendation to the user; **do not adopt an
> arm without their confirmation.** This project has twice adopted a change on
> metrics that later proved wrong — once endorsing a router that routed through
> a MusicBrainz editor account, once rejecting the scoring that was actually
> better. Both passed a metrics check.
>
> Three things that must not happen here:
> - **Do not relax a criterion to produce a winner.** All six or no adoption.
> - **Do not treat criterion 5 as a formality.** Read the exported paths. Every
>   overlap objective scores the *La La Land* chain well.
> - **Do not report a criterion as met without the number that shows it.**

A candidate is adopted only if **all six** hold (spec §B9):

1. Adamic–Adar improves over control, paired-significant after Holm.
2. Overlap coefficient improves too. **AA up with OC flat or down means the arm moved along AA's +0.578 min-degree channel — reject it.**
3. `hubfrac` moves toward the null **without** `mean_max_interior_degree` collapsing below it.
4. `mean_ceiling_hops` below 0.30.
5. Read paths show no junk hops **and** `flagged_paths` does not rise.
6. The held-out slice reproduces 1–4.

**"No candidate beats the control" is a pre-authorised outcome.** Do not relax the criterion to produce a winner.

- [ ] **Step 7: Confirm on the held-out slice — only after choosing**

```bash
cd api
PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python eval/run_baseline.py \
  ../builder/scratch/graph-control.bin control --held-out
PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python eval/run_baseline.py \
  ../builder/scratch/graph-<WINNER>.bin <WINNER> --held-out
```

Re-run Step 4's comparison against the `-heldout.json` files. If criteria 1–4 do not reproduce, **the result was an over-fit — do not adopt.**

- [ ] **Step 8: Write the findings document**

Create `docs/superpowers/findings/2026-07-22-phase2-sweep-results.md`: the arm table with every diagnostic, the paired-test results with corrected p-values, the held-out confirmation, the decision against each of the six criteria, and the adopted artifact's **sha256 from its manifest** (artifacts are gitignored and cannot be committed). Link it from the adjudication's §6.

- [ ] **Step 9: Commit**

```bash
git add api/eval/run_baseline.py api/eval/results-*.json api/eval/hub-nodes-control.json docs/superpowers/findings/2026-07-22-phase2-sweep-results.md
git commit -m "findings: Phase 2 sweep results and adoption decision"
```

---

## Task 16: Adopt

**Files:**
- Modify: `builder/src/artistpath_builder/config.py` (defaults + comment), `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md`, `docs/superpowers/specs/2026-07-21-phase2-path-quality-design.md` (status), `CLAUDE.md`
- Test: existing suites

- [ ] **Step 1: Set the adopted defaults**

Update `BuilderConfig`'s `cap_strategy`, `similarity_rescale` and `similarity_damping` to the adopted values. **Delete the losing option** from each knob's docstring and raise `ValueError` on it — spec §8 risk 4 requires the loser be removed, not left as a permanently supported mode.

Rewrite the `similarity_damping` comment: it currently says "0.0 is provisional… decided after that". Replace with the adopted value, the evidence, and a link to `2026-07-22-phase2-sweep-results.md`. **Do not restate figures** — cite the section.

- [ ] **Step 2: Regenerate the 5k dev fixture from the adopted graph**

```bash
cd builder && UV_LINK_MODE=copy uv run artistpath-build fixture \
  --graph scratch/graph-<WINNER>.bin --out scratch/graph-5k.bin --size 5000
```

- [ ] **Step 3: Regenerate the committed test fixture**

```bash
cd builder && UV_LINK_MODE=copy uv run artistpath-build fixture \
  --graph scratch/graph-<WINNER>.bin --out tests/fixtures/graph-fixture.bin --size 500
cp tests/fixtures/graph-fixture.bin ../api/tests/fixtures/graph-fixture.bin
```

- [ ] **Step 4: Run every suite**

```bash
cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd ../api && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd ../frontend && npm test
```

Expected: all green. Fixture-dependent assertions may need updating — if a test asserts a specific path through the old fixture, update the expectation and **say so in the commit message**; do not weaken the assertion.

- [ ] **Step 5: Update the docs**

- Spec: `**Status:**` → `implemented, adopted <value>`.
- Roadmap: mark Phase 2 complete; correct anything the sweep overturned.
- `CLAUDE.md`: the "Popularity = score-weighted in-degree" and pathfinding sections if the adopted scoring changed their description. Also fix `api/src/artistpath_api/config.py:12-13`, whose comment still calls `graph-5k.bin` "the committed 5k graph" — the same stale claim already corrected in `CLAUDE.md`.

- [ ] **Step 6: Run Snyk on everything modified**

Run `snyk_code_scan` on `builder/src/artistpath_builder` and `api/src/artistpath_api`. Expected: 0 issues.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: adopt Phase 2 scoring; regenerate fixtures"
```

---

## Self-review notes

**Spec coverage.** §A1 → Task 9. §A3 → Tasks 4, 10. §B1 → Tasks 2, 3, 5. §B2 → Task 6. §B3 → Task 11. §B4 precondition 1 → Task 12. §B4 precondition 2 → Task 13. §B4 factor d → Task 14. §B5 → Task 15. §B7 → Task 7. §B8 → Task 8. §B9 → Task 15 Steps 6–7. §B10 → Task 16. §6.1 → Task 15 Step 1 (`w_jump = 0` router). §7 testing → distributed across tasks; the cap invariant is Task 12 Step 6, the degeneracy guard Task 13 Step 1, bad-path calibration Task 5 Steps 5–6. §8 risk 1 → Task 1 Step 7. §8 risk 3 → Task 1. §8 risk 4 → Task 16 Step 1.

**Deliberately not implemented:** §B6 (support/shrinkage axis) and §B6a (external popularity anchor) are marked deferred in the spec and are out of scope here.

**Known sharp edge.** Task 14 Step 4 changes `rescale_scores`'s `p99_log_clip` branch to `expm1` its input, because Task 13 wrote that branch expecting raw values while Task 14 makes every caller pass log-space values. That round-trip is exact only at `d = 0`, which is the only arm using the legacy rescale — but the two tasks must not be reordered, and Task 14 Step 5's byte-identity re-check is what catches it if they are. **This warning is repeated inside both Task 13 and Task 14**, because a worker executing one task in isolation will not read this section.

## Execution notes

**Three steps are judgement, not implementation**, and each carries a required-reading block naming the sections of the adjudication that must be read first:

| Step | Decision | Autonomy |
|---|---|---|
| Task 5 Step 5 | Bad-path detector calibration | Delegable. Report thresholds *and* the false-positive count. A failed calibration is a valid result — do not invent a signal to force a pass. |
| Task 10 Step 3 | Topological vs scoring-caused hub-seeking | Delegable against the pre-registered rule. Do not adjust the rule to fit the numbers. |
| **Task 15 Step 6** | **Which arm to adopt** | **Human decision. Present evidence, do not adopt without confirmation.** |

**Gates that stop work rather than warn** — none of these may be relaxed to proceed:

- Task 12 Step 8 — mutual k-NN must retain ≥90 % of artists.
- Task 13 Step 7 and Task 14 Step 5 — the control arm must be byte-identical to `graph-75k-v3.bin` with `filter_special_purpose=False`.
- Task 5 Step 5 — the detector must separate known-bad from known-good.
- Task 15 Step 7 — the held-out slice must reproduce criteria 1–4.

**`api/eval/run_baseline.py` is rewritten wholesale in Task 15 Step 1.** Task 3 Step 5 patches it only to keep the suite green; that work is discarded by design.

**Task 1 Step 7 measures a real 75k build.** Everything about how Task 15 is scheduled depends on that number, so it is not optional and cannot be estimated.
