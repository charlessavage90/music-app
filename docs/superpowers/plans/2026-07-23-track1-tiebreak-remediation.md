# Track 1 — Tie-break Remediation Implementation Plan

> **⚠ Role: COMPLETE. EXECUTED 2026-07-23 — do not execute again.** The fix landed and the
> rebuilt artifact was **adopted**; the app has routed on `graph-t15-tiebreakfix.bin` since.
> Outcomes: [`../2026-07-23-repair-and-retune-execution-log.md`](../2026-07-23-repair-and-retune-execution-log.md);
> artifact identity: [`../findings/2026-07-23-tiebreak-fix-adoption.md`](../findings/2026-07-23-tiebreak-fix-adoption.md).
> Where those and this plan disagree, **they win**. Re-running this rebuilds and re-adopts an
> artifact, which is the owner's call.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the §2.8 tie-break defect — `mutual_knn_cap` must rank top-k on unclipped damped strengths, not p99-clipped scores — then rebuild, verify against §2.8 Arm 2, and adopt the repaired 75k artifact.

> **Role: COMPLETE — executed 2026-07-23; do not execute again.** The repaired artifact
> (`graph-t15-tiebreakfix.bin`) was built, verified, and adopted. Outcomes and the
> execution record are in `../2026-07-23-repair-and-retune-execution-log.md`; the
> artifact's identity is owned by `../findings/2026-07-23-tiebreak-fix-adoption.md`. The
> task checkboxes below are left unchecked as the historical plan record — this banner,
> not the checkboxes, conveys completion.

**Architecture:** One new optional `ranking` argument on `mutual_knn_cap` (builder), one wiring change in `build_from_archive`, no API changes, no APG1 format changes. Verification is a committed analysis script asserting the rebuild reproduces the Phase 1 log §2.8 Arm 2 topology and changes nothing else.

**Tech Stack:** Python 3 / uv / pytest (builder package), numpy, the existing `artistpath-build` CLI.

**Governing documents:** `docs/superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md` (spec, §3 is this track); `docs/superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md` §2.8 (the defect and the validated intervention this reproduces).

**Scope seam (spec §2):** This plan is Track 1 only. Track 2 (cost-function retune) gets its own plan, authored after this track lands, because its protocol must pass an `ml-graph-analyst` review and its pre-registration fixes values this track's outputs inform. Do not start Track 2 work from this plan.

## Global Constraints

- Prefix every `uv` command with `UV_LINK_MODE=copy` (OneDrive breaks hardlinks). Run `uv` from inside `builder/`.
- Anything printing artist names needs `PYTHONIOENCODING=utf-8`.
- Long-running Python with redirected output needs `python -u` (buffered jobs write 0-byte logs and look hung).
- Determinism is a hard requirement (alpha design spec §9): every ordering decision explicit, ties break on lowest MBID.
- **Figures rule:** expected values inside verification scripts are copies-for-execution and must carry a comment citing Phase 1 log §2.8, which owns them. Do not restate them in any new prose document except the one findings doc this plan creates (which then owns the *new* artifact's identity figures).
- Branch: `phase1-repair-and-retune` (exists, pushed). Commit per task. No `frontend/` changes; the only permitted `api/` change is Task 4's `ApiConfig.graph_path` default flip (spec §1 decision 4) — routing code stays untouched.
- Artifacts are gitignored; a checksum in the findings doc is their only identity. Never `git add -A` (another session may share this tree).

---

### Task 1: `ranking` parameter on `mutual_knn_cap`

**Files:**
- Modify: `builder/src/artistpath_builder/graph.py:57-85` (the `mutual_knn_cap` function)
- Test: `builder/tests/test_graph.py`

**Interfaces:**
- Consumes: existing `mutual_knn_cap(adjacency: Adjacency, k: int) -> Adjacency` and `Adjacency = dict[str, dict[str, float]]`.
- Produces: `mutual_knn_cap(adjacency: Adjacency, k: int, ranking: Adjacency | None = None) -> Adjacency`. When `ranking` is given, top-k membership is decided by `ranking[node][dst]` (descending, ties on lowest MBID); emitted scores always come from `adjacency`. `ranking=None` preserves the old behaviour exactly. `ValueError` if `ranking`'s node set differs from `adjacency`'s; `KeyError` (natural, loud) if `ranking` is missing an edge that `adjacency` has. Task 2 relies on this exact signature.

- [ ] **Step 1: Write the failing tests**

Append to `builder/tests/test_graph.py` (add `import pytest` to the imports at the top — the file does not currently import it):

```python
def test_mutual_knn_ranks_on_the_ranking_argument_when_given():
    # The Phase 1 log §2.8 defect scenario: emitted scores tied at the p99
    # ceiling, unclipped strengths distinct. Selection must follow the
    # ranking, not fall through to the MBID tie-break over the tied scores.
    adjacency = {
        "a": {"e": 1.0, "c": 1.0},  # both clipped to the ceiling
        "e": {"a": 1.0},
        "c": {"a": 1.0},
    }
    ranking = {
        "a": {"e": 5.3, "c": 5.0},  # unclipped: e is genuinely stronger
        "e": {"a": 5.3},
        "c": {"a": 5.0},
    }
    capped = mutual_knn_cap(adjacency, k=1, ranking=ranking)
    assert "e" in capped["a"]
    assert "c" not in capped["a"]


def test_mutual_knn_without_ranking_keeps_the_old_tie_break():
    # Same inputs, no ranking: the lowest MBID wins the tie, as before.
    adjacency = {
        "a": {"e": 1.0, "c": 1.0},
        "e": {"a": 1.0},
        "c": {"a": 1.0},
    }
    capped = mutual_knn_cap(adjacency, k=1)
    assert "c" in capped["a"]
    assert "e" not in capped["a"]


def test_mutual_knn_emits_adjacency_scores_not_ranking_values():
    # The ranking decides membership only; the artifact still carries the
    # rescaled scores.
    adjacency = {
        "a": {"e": 1.0},
        "e": {"a": 1.0},
    }
    ranking = {
        "a": {"e": 5.3},
        "e": {"a": 5.3},
    }
    capped = mutual_knn_cap(adjacency, k=1, ranking=ranking)
    assert capped["a"]["e"] == 1.0


def test_mutual_knn_ranking_ties_still_break_on_lowest_mbid():
    # Determinism (design §9) must survive the new argument: genuinely tied
    # unclipped strengths resolve the same way every run.
    adjacency = {
        "a": {"e": 0.9, "c": 0.8},
        "e": {"a": 0.9},
        "c": {"a": 0.8},
    }
    ranking = {
        "a": {"e": 2.0, "c": 2.0},
        "e": {"a": 2.0},
        "c": {"a": 2.0},
    }
    capped = mutual_knn_cap(adjacency, k=1, ranking=ranking)
    assert "c" in capped["a"]


def test_mutual_knn_rejects_ranking_with_a_different_node_set():
    with pytest.raises(ValueError, match="ranking"):
        mutual_knn_cap({"a": {}}, k=1, ranking={"b": {}})
```

- [ ] **Step 2: Run the new tests to verify they fail**

```bash
cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_graph.py -k ranking
```

Expected: FAIL — `TypeError: mutual_knn_cap() got an unexpected keyword argument 'ranking'` (and the no-ranking tie-break test passes, since it exercises current behaviour).

- [ ] **Step 3: Implement**

Replace the whole `mutual_knn_cap` function in `builder/src/artistpath_builder/graph.py` with:

```python
def mutual_knn_cap(
    adjacency: Adjacency, k: int, ranking: Adjacency | None = None
) -> Adjacency:
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

    `ranking`, when given, supplies the values used to order each node's
    top-k; emitted scores still come from `adjacency`. It exists because the
    p99 clip collapses the top ~1% of scores to exactly 1.0, and ranking those
    tied values let the MBID tie-break decide which neighbours a saturated
    artist kept — which is how the most famous artists lost nearly all their
    edges (Phase 1 log §2.8). Callers that rescale destructively must pass the
    pre-rescale strengths here. `ranking` must cover exactly the nodes of
    `adjacency` (ValueError otherwise) and every edge of `adjacency`
    (KeyError otherwise — loud by design).

    Ties break on lowest MBID, matching every other ordering decision in this
    module (design §9).
    """
    if ranking is not None and set(ranking) != set(adjacency):
        raise ValueError(
            "ranking must cover exactly the nodes of adjacency; top-k "
            "selection over a different node set is undefined"
        )
    rank_of = ranking if ranking is not None else adjacency

    top_k: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(
            ((dst, rank_of[node][dst]) for dst in edges),
            key=lambda pair: (-pair[1], pair[0]),
        )
        top_k[node] = {dst for dst, _score in ranked[:k]}

    result: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in top_k[node] and node in top_k.get(dst, set()):
                result[node][dst] = score
    return result
```

- [ ] **Step 4: Run the full builder graph tests**

```bash
cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_graph.py
```

Expected: PASS, including all pre-existing `mutual_knn` tests (the `ranking=None` path is byte-for-byte the old algorithm).

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/graph.py builder/tests/test_graph.py
git commit -m "feat(builder): mutual_knn_cap accepts a ranking separate from emitted scores

The p99 clip ties the top ~1% of scores at exactly 1.0, so ranking the
clipped values let the MBID tie-break decide which neighbours a saturated
artist kept (Phase 1 log 2.8). The cap can now rank pre-rescale strengths
while still emitting rescaled scores. ranking=None is unchanged behaviour."
```

---

### Task 2: Wire unclipped ranking through `build_from_archive`

**Files:**
- Modify: `builder/src/artistpath_builder/pipeline.py:218` (the `mutual_knn_cap` call, plus a ranking dict built just above it)
- Test: `builder/tests/test_pipeline_capranking.py` (new file)

**Interfaces:**
- Consumes: Task 1's `mutual_knn_cap(adjacency, k, ranking=...)`; existing `scored_adjacency: dict[str, list[tuple[str, float]]]` (unclipped damped strengths, built at `pipeline.py:178-192`).
- Produces: `build_from_archive` output whose top-k selection is decided by unclipped strengths. No signature changes anywhere.

- [ ] **Step 1: Write the failing test**

Create `builder/tests/test_pipeline_capranking.py`:

```python
"""The §2.8 tie-break defect: top-k selection must rank UNCLIPPED strengths.

p99_log_clip collapses the top ~1% of raw scores to exactly 1.0. While the
mutual-kNN top-k ranked those clipped values, every ceiling-saturated list
was decided by the lowest-MBID tie-break — which is how The Beatles kept 7
of 100 neighbours and Radiohead kept none (Phase 1 log §2.8). The cap must
rank the unclipped damped strengths while the artifact still carries the
clipped scores.
"""

import json

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

X = "a" * 36       # the saturated artist
STRONG = "e" * 36  # genuinely stronger neighbour (cooc 200) — HIGHER mbid
WEAK = "c" * 36    # weaker neighbour (cooc 150) — LOWER mbid, so it wins
                   # X's one slot iff selection wrongly ranks clipped scores


def _pad(i: int) -> str:
    # Padding mbids sort above X, WEAK and STRONG.
    return f"f{i:035d}"


def _body(rows: list[tuple[str, int]]) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": m, "name": m[:4], "comment": "", "score": s}
            for m, s in rows
        ]
    ).encode()


def _seed(archive, source) -> None:
    def put(mbid, rows):
        archive.put(f"similar/{source.name}/{mbid}.json", _body(rows))

    put(X, [(STRONG, 200), (WEAK, 150)])
    put(STRONG, [(X, 200)])
    put(WEAK, [(X, 150)])
    # 200 mutual padding pairs at cooc 100 hold the p99 down at 100, so both
    # of X's edges land above it and clip to exactly 1.0 — reproducing the
    # ceiling-saturation regime of §2.8 in miniature.
    for i in range(200):
        a, b = _pad(2 * i), _pad(2 * i + 1)
        put(a, [(b, 100)])
        put(b, [(a, 100)])


def _build(tmp_path):
    config = BuilderConfig(requests_per_second=1000.0, max_neighbours_per_artist=1)
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed(archive, source)
    return build_from_archive(config, archive, source)


def test_topk_selection_ranks_unclipped_strengths_not_clipped_scores(tmp_path):
    graph = _build(tmp_path)
    # k=1: X's one slot must go to STRONG (cooc 200), not to WEAK — WEAK only
    # wins if the MBID tie-break over two clipped 1.0s is deciding. The
    # largest-component step then keeps {X, STRONG} (X carries the lowest
    # MBID, so its size-2 component beats the padding pairs' ties).
    assert X in graph.mbids and STRONG in graph.mbids
    assert WEAK not in graph.mbids
    x = graph.mbids.index(X)
    row = list(graph.neighbours[graph.offsets[x] : graph.offsets[x + 1]])
    assert row == [graph.mbids.index(STRONG)]


def test_emitted_scores_are_still_clipped(tmp_path):
    # The fix changes membership, never the emitted values: X's surviving
    # edge is above the p99 and must still carry the ceiling score of 1.0,
    # not the raw strength that ranked it.
    graph = _build(tmp_path)
    x = graph.mbids.index(X)
    scores = list(graph.scores[graph.offsets[x] : graph.offsets[x + 1]])
    assert scores == [1.0]
```

- [ ] **Step 2: Run it to verify the discriminating test fails**

```bash
cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pipeline_capranking.py
```

Expected: `test_topk_selection_ranks_unclipped_strengths_not_clipped_scores` FAILS on `assert STRONG in graph.mbids` (current code keeps WEAK via the tie-break). `test_emitted_scores_are_still_clipped` may pass already — it guards the invariant through the next step.

- [ ] **Step 3: Wire the ranking through the pipeline**

In `builder/src/artistpath_builder/pipeline.py`, replace the single line

```python
    adjacency = mutual_knn_cap(adjacency, config.max_neighbours_per_artist)
```

with:

```python
    # Rank the cap on UNCLIPPED strengths. The clip rescale ties the top ~1%
    # of scores at exactly 1.0; ranking those tied values let the MBID
    # tie-break decide which neighbours a saturated artist kept, collapsing
    # the most famous artists to near-zero degree (Phase 1 log §2.8). The
    # emitted scores are still the rescaled ones.
    ranking: Adjacency = {
        mbid: {dst: strength for dst, strength in scored}
        for mbid, scored in scored_adjacency.items()
    }
    adjacency = mutual_knn_cap(
        adjacency, config.max_neighbours_per_artist, ranking=ranking
    )
```

- [ ] **Step 4: Run the whole builder suite**

```bash
cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q
```

Expected: ALL PASS — including `test_replay.py::test_rebuild_from_archive_is_byte_identical_with_no_network` (the change is deterministic, so byte-identity across rebuilds must hold).

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/pipeline.py builder/tests/test_pipeline_capranking.py
git commit -m "fix(builder): rank the mutual-kNN cap on unclipped strengths

Reproduces the Phase 1 log 2.8 Arm 2 intervention in the shipped builder:
top-k membership follows the pre-rescale damped strengths, emitted scores
stay p99-clipped, popularity (summed pre-cap) is untouched."
```

---

### Task 3: Rebuild the 75k artifact and verify it against §2.8 Arm 2

**Files:**
- Create: `builder/scratch/graph-t15-tiebreakfix.bin` (+ auto-written `.json` manifest sidecar) — gitignored, identified by checksum
- Create: `builder/analysis/2026-07-23-tiebreak-fix-verification/verify.py`
- Create: `builder/analysis/2026-07-23-tiebreak-fix-verification/README.md`

**Interfaces:**
- Consumes: Task 2's builder; archive at `builder/scratch/graph-archive/`; adopted `builder/scratch/graph-t15-capfix.bin` (sha256 asserted in-script); `GraphStore.load` from `api/src` (the established analysis-script pattern).
- Produces: a verified artifact whose sha256 Task 4 records; a committed verification script and its run output.

- [ ] **Step 1: Rebuild twice and confirm determinism**

```bash
cd builder
UV_LINK_MODE=copy uv run artistpath-build build --archive-dir scratch/graph-archive --out scratch/graph-t15-tiebreakfix.bin
UV_LINK_MODE=copy uv run artistpath-build build --archive-dir scratch/graph-archive --out scratch/graph-t15-tiebreakfix-repro.bin
```

Expected: each run logs `wrote ... 74193 artists, 898006 edges` in ~30s (Arm 2's shape; if N/E differ from that, STOP — do not proceed to verification, investigate the build path first). Then:

```bash
cd builder/scratch
sha256sum graph-t15-tiebreakfix.bin graph-t15-tiebreakfix-repro.bin
```

Expected: two identical hashes. Then delete the repro pair:

```bash
rm graph-t15-tiebreakfix-repro.bin graph-t15-tiebreakfix-repro.bin.json
```

- [ ] **Step 2: Write the verification script**

Create `builder/analysis/2026-07-23-tiebreak-fix-verification/verify.py`:

```python
"""Verify the tie-break-fix rebuild against Phase 1 log §2.8 Arm 2.

Asserts (a) the rebuilt artifact reproduces the Arm 2 topology — the
one-knob unclipped-ranking intervention — and (b) everything the fix must
NOT change is unchanged against adopted capfix: emitted scores on shared
edges are bit-identical, popularity ordering is preserved (values shift
only by the min/max renormalisation over a node set that regained
Radiohead).

Expected values are COPIES FOR EXECUTION, cited from Phase 1 log §2.8,
which owns them. Artifact-only; runs in seconds. Paths hardcoded — this is
a record of what was executed, not a maintained tool.
"""

import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore  # noqa: E402

CAPFIX = ROOT / "builder" / "scratch" / "graph-t15-capfix.bin"
NEW = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"

# Preconditions: measure the artifacts we think we have (log §5 checksums).
assert hashlib.sha256(CAPFIX.read_bytes()).hexdigest() == (
    "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237"
)
new_sha = hashlib.sha256(NEW.read_bytes()).hexdigest()

cap = GraphStore.load(CAPFIX)
new = GraphStore.load(NEW)


def node(g: GraphStore, name: str) -> int:
    """Resolve a name to its most popular node (duplicate names exist, §2.2)."""
    idx = [i for i, n in enumerate(g.names) if n == name]
    assert idx, f"{name!r} not found"
    return max(idx, key=lambda i: float(g.popularity[i]))


def degree(g: GraphStore, i: int) -> int:
    return int(g.offsets[i + 1] - g.offsets[i])


# --- (a) Arm 2 topology (all expected values: Phase 1 log §2.8) ------------
deg = np.diff(new.offsets)
assert new.artist_count == 74_193, new.artist_count
assert int(new.scores.size) == 898_006, new.scores.size
assert int(np.median(deg)) == 9, np.median(deg)
frac_lt8 = float((deg < 8).mean())
assert abs(frac_lt8 - 0.449) < 0.002, frac_lt8
assert int(deg.max()) <= 50, deg.max()

expected_degrees = {  # §2.8 Arm 2 column
    "Radiohead": 50,
    "The Beatles": 50,
    "Coldplay": 50,
    "R.E.M.": 47,
}
for name, want in expected_degrees.items():
    got = degree(new, node(new, name))
    assert got == want, f"{name}: degree {got}, expected {want}"
assert not [n for n in cap.names if n == "Radiohead"], (
    "capfix unexpectedly contains Radiohead — wrong baseline artifact?"
)

# --- (b) invariance against capfix ------------------------------------------


def edge_scores(g: GraphStore) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for u in range(g.artist_count):
        mu = g.mbids[u]
        for k in range(int(g.offsets[u]), int(g.offsets[u + 1])):
            out[(mu, g.mbids[int(g.neighbours[k])])] = float(g.scores[k])
    return out


cap_edges = edge_scores(cap)
new_edges = edge_scores(new)
shared = set(cap_edges) & set(new_edges)
assert len(shared) > 890_000, len(shared)
diffs = [k for k in shared if cap_edges[k] != new_edges[k]]
assert not diffs, f"{len(diffs)} shared edges changed score; first: {diffs[:3]}"

shared_mbids = sorted(set(cap.mbids) & set(new.mbids))
pc = np.array([cap.popularity[cap.id_by_mbid[m]] for m in shared_mbids])
pn = np.array([new.popularity[new.id_by_mbid[m]] for m in shared_mbids])
assert float(np.abs(pc - pn).max()) < 0.02, np.abs(pc - pn).max()
# Ordering preserved: rank vectors (double argsort) must correlate ~1.
rc = np.argsort(np.argsort(pc, kind="stable"), kind="stable").astype(float)
rn = np.argsort(np.argsort(pn, kind="stable"), kind="stable").astype(float)
assert float(np.corrcoef(rc, rn)[0, 1]) > 0.9999

print("ALL CHECKS PASSED")
print(f"graph-t15-tiebreakfix.bin sha256 = {new_sha}")
print(f"N={new.artist_count} E={new.scores.size}")
print(f"nodes only in new: {sorted(set(new.mbids) - set(cap.mbids))}")
print(f"shared edges: {len(shared)}  (capfix E={cap.scores.size})")
for name in expected_degrees:
    i = node(new, name)
    print(f"{name}: degree {degree(new, i)}, popularity {float(new.popularity[i]):.3f}")
```

- [ ] **Step 3: Run it**

```bash
cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-23-tiebreak-fix-verification/verify.py
```

Expected: `ALL CHECKS PASSED`, then the sha256 and summary lines. Copy the full output — Task 4's findings doc records it. If any assert fires, STOP: the rebuild does not reproduce Arm 2, and the discrepancy must be understood before anything is adopted (the likeliest suspects are the wrong archive directory or a stale artifact under a reused name).

- [ ] **Step 4: Write the README**

Create `builder/analysis/2026-07-23-tiebreak-fix-verification/README.md`:

```markdown
# Tie-break fix verification — Track 1 of the repair+retune spec

`verify.py` asserts that `graph-t15-tiebreakfix.bin` (built by the fixed
builder: `mutual_knn_cap` ranking unclipped strengths) reproduces the
Phase 1 log §2.8 Arm 2 topology, and that emitted scores on shared edges
and popularity ordering are unchanged against adopted `capfix`.

Expected values inside the script are copies for execution — **cite the
Phase 1 log §2.8 and the adoption findings doc, not this script.**

Needs `builder/scratch/graph-t15-capfix.bin` and
`builder/scratch/graph-t15-tiebreakfix.bin` (gitignored; identified by
sha256, asserted in-script). Paths hardcoded deliberately: this is a
record of what was executed, not a maintained tool.

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-23-tiebreak-fix-verification/verify.py` (from `builder/`).
```

- [ ] **Step 5: Commit**

```bash
git add builder/analysis/2026-07-23-tiebreak-fix-verification/
git commit -m "test(analysis): verify the tie-break-fix rebuild against log 2.8 Arm 2

Asserts Arm 2 topology (N, E, famous-artist degrees, global shape) and
invariance of shared-edge scores and popularity ordering vs capfix."
```

---

### Task 4: Adopt — dev default flipped to the 75k artifact, smoke check, adoption record

> **Amended 2026-07-23 (owner, spec §1 decision input 4):** the 5k dev fixture is
> retired — its small shape makes manual results untrustworthy, unit tests run on the
> committed 500-node fixtures instead, and its seeding once produced a famous-artist-free
> dev graph (Phase 2 log §19). Dev now defaults to the full adopted artifact.

**Files:**
- Modify: `api/src/artistpath_api/config.py:11-18` (the `graph_path` default and its comment)
- Modify: `CLAUDE.md` (api dev-server command block; the "No dev or production graph artifact is in git" paragraph)
- Modify: `README.md`, `api/README.md`, `frontend/README.md` (dev-run lines naming `graph-5k.bin`)
- Modify: `.claude/agents/ml-graph-analyst.md:38` (the `graph-5k.bin` "quick iteration" mention)
- Create: `docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`
- Modify: `docs/README.md` (current-state block + findings table row)
- Modify: `docs/superpowers/TEST-QUEUE.md` (new QUEUED entry at the top)

**Interfaces:**
- Consumes: Task 3's verified `graph-t15-tiebreakfix.bin` and the `verify.py` output (sha256, degree lines).
- Produces: the adopted-artifact record every later session resolves identity against; an API that boots the adopted 75k artifact by default.

- [ ] **Step 1: Flip the dev default to the adopted artifact**

In `api/src/artistpath_api/config.py`, replace the `graph_path` block (lines 11–18, from the `# --- graph ---` header through the closing paren) with:

```python
    # --- graph ----------------------------------------------------------
    # Default is the ADOPTED 75k artifact, by name — flipped at each adoption
    # (spec 2026-07-23 §1 decision 4; closeout checks this default is not
    # stale). It is gitignored: a fresh clone copies it (or the archive) from
    # another machine and verifies the sha256 against
    # docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md.
    # The retired 5k dev fixture is NOT a substitute — its snowball shape
    # misrepresents the obscure tail, which is what bypass work exercises.
    # One env var swaps the graph without code changes.
    graph_path: str = os.environ.get(
        "ARTISTPATH_GRAPH", "../builder/scratch/graph-t15-tiebreakfix.bin"
    )
```

- [ ] **Step 2: Smoke-check through the flipped default**

Run from `api/` so the relative default resolves exactly as the dev server would:

```bash
cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u - <<'EOF'
from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path

cfg = ApiConfig()
assert cfg.graph_path.endswith("graph-t15-tiebreakfix.bin"), cfg.graph_path
g = GraphStore.load(cfg.graph_path)
names = set(g.names)
for want in ("Radiohead", "The Beatles"):
    assert want in names, f"{want} missing from the adopted artifact"
src = g.names.index("Radiohead")
dst = g.names.index("The Beatles")
path = find_path(g, src, dst, [], cfg)
assert path and path[0] == src and path[-1] == dst
print(" -> ".join(g.names[i] for i in path))
EOF
```

Expected: an artist path printed, Radiohead first, The Beatles last. (Radiohead being *searchable at all* is new behaviour — it was absent from the previous adopted graph.)

- [ ] **Step 2b: Update the dev-run guidance that names `graph-5k.bin`**

Four small text edits, same substance in each — the dev default is now the adopted
artifact, `ARTISTPATH_GRAPH` still overrides, and `graph-5k.bin` is retired:

1. `CLAUDE.md` api command block: the dev-server example becomes

   ```bash
   # dev server — boots the ADOPTED 75k graph by default (ApiConfig.graph_path);
   # ARTISTPATH_GRAPH overrides:
   uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
   ```

   and in the "No dev or production graph artifact is in git" paragraph, replace the
   sentence starting `Build `graph-5k.bin` locally from an archive` with: "On a fresh
   clone, copy the adopted 75k artifact (or the archive, and rebuild in ~30 s) from
   another machine — identity by the checksum in
   `docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`. The 5k dev fixture
   is retired; the `fixture` command remains only for the committed 500-node test
   fixtures."
2. `README.md`: same replacement for its `graph-5k.bin` copy line and dev-server line.
3. `api/README.md`: the `ARTISTPATH_GRAPH` table row default becomes
   `../builder/scratch/graph-t15-tiebreakfix.bin` ("the adopted artifact; flipped at
   each adoption"), and the dev-run example drops the env var.
4. `frontend/README.md`: dev-run line drops the `ARTISTPATH_GRAPH=` prefix.
5. `.claude/agents/ml-graph-analyst.md:38`: replace the parenthetical with
   `(`graph-75k.bin` and successors; the dev API boots the adopted artifact by default)`.

- [ ] **Step 3: Run the API test suite**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q
```

Expected: ALL PASS (api tests inject committed 500-node fixtures, so the default flip
must not disturb them — a failure here means some test secretly depended on the default
path, which would itself be worth fixing before proceeding).

- [ ] **Step 4: Write the adoption findings doc**

Create `docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md` — substituting the sha256 and the verification output block from Task 3's run where marked:

```markdown
# Adoption record — `graph-t15-tiebreakfix.bin` (the §2.8 tie-break fix)

**Role: AUTHORITATIVE for the adopted 75k artifact's identity.** Written
2026-07-23. This document owns the new artifact's identity figures; the
defect and the intervention that validated this fix are owned by the
Phase 1 log §2.8 — cite mechanism claims from there, not from here.

## What was adopted

The 75k artifact built by the fixed builder — `mutual_knn_cap` ranks top-k
on unclipped damped strengths; emitted scores stay `p99_log_clip`;
popularity unchanged (summed pre-cap). Governing design:
`../specs/2026-07-23-defect-remediation-and-cost-retune-design.md` §3.

| artifact | sha256 |
|---|---|
| `builder/scratch/graph-t15-tiebreakfix.bin` **(ADOPTED)** | `<sha256 from verify.py output>` |

Supersedes `graph-t15-capfix.bin` (sha `c8af6eac…`) as the artifact the app
routes on. capfix remains on disk as the §2 baseline.

## Adoption basis — why no listening test

Phase 1 log §4.1 closed this: the fix's topology (= §2.8 Arm 2 = rankfix's)
is identical to capfix on stratification and tail behaviour; a listen would
burn the owner's ear on a null. What changes is confined to
ceiling-saturated famous artists' neighbourhoods (~0.4 % of nodes), verified
below. The owner's ordinary use is the post-adoption check (TEST-QUEUE).

## Verification (script: `builder/analysis/2026-07-23-tiebreak-fix-verification/verify.py`)

All §2.8 Arm 2 topology assertions passed; shared-edge scores bit-identical
to capfix; popularity ordering preserved. Run output:

```
<full verify.py output block>
```

## Dev default

`ApiConfig.graph_path` now defaults to this artifact (spec §1 decision 4 —
the 5k dev fixture is retired; unit tests keep the committed 500-node
fixtures). Smoke-checked through the default: Radiohead and The Beatles
findable; Radiohead → The Beatles routes.
```

- [ ] **Step 5: Update `docs/README.md`**

In the current-state block, replace the line

```markdown
  - **Decided 2026-07-23:** the owner chose **repair + retune** — fix the §2.8 tie-break
```

and its continuation lines (through `…relaxation of the listening-test prohibition.`) with:

```markdown
  - **Decided 2026-07-23:** the owner chose **repair + retune** — governing design
    `superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md`; its §1
    also records the nine-names verdict (in-graph popularity ≠ fame at the top,
    confirmed) and the owner's relaxation of the listening-test prohibition.
  - **Track 1 is DONE, 2026-07-23: the §2.8 tie-break is fixed and the rebuilt artifact
    is adopted.** The app now routes on `graph-t15-tiebreakfix.bin` — identity and
    verification in `superpowers/findings/2026-07-23-tiebreak-fix-adoption.md` (the
    authoritative record for the adopted artifact's checksum). Radiohead is back;
    famous-artist neighbourhoods are score-ranked, not MBID-ranked. Track 2 (cost-function
    retune) is next and has its own plan.
```

And add to the **Authoritative** table:

```markdown
| `superpowers/findings/2026-07-23-tiebreak-fix-adoption.md` | Identity (sha256) and verification record of the **adopted** 75k artifact, post tie-break fix. |
```

- [ ] **Step 6: Queue the use-the-app entry**

Add at the top of `docs/superpowers/TEST-QUEUE.md` (below the header block):

```markdown
## QUEUED — 2026-07-23 — tie-break fix adopted: famous-artist neighbourhoods changed

**What changed.** The graph the app routes on. The §2.8 tie-break fix is in: top-k
selection now ranks unclipped strengths, so ceiling-saturated famous artists keep their
genuinely strongest neighbours instead of the lowest-MBID ones. ~0.4 % of nodes change
neighbours; everything else is verified identical
(`findings/2026-07-23-tiebreak-fix-adoption.md`). The dev API now boots the full
adopted artifact by default — the 5k fixture is retired, so what you test is what
the record measured.

**What to exercise:**

1. **Search Radiohead.** It was absent from the previous graph entirely; it must now be
   searchable and routable. This is the headline change — worth ten seconds.
2. **Routes that end at or pass through very famous artists** (The Beatles, Coldplay,
   Muse, Nine Inch Nails…). Their neighbourhoods went from ~4–7 arbitrary survivors to
   ~50 score-ranked ones, so first paths and bypaths around them may genuinely differ.
3. **A couple of ordinary mid-popularity paths** as a regression check — these should
   feel unchanged (their neighbourhoods are untouched).

**What "wrong" would look like:** a "no path" without exclusions (structurally
impossible, so a real defect); an artist that was searchable yesterday now absent;
famous-endpoint paths that feel *worse* than before. Clip bugs remain known, unrelated,
and queued (C1/C2).

**Best bug report:** the URL from the address bar.
```

- [ ] **Step 7: Commit**

```bash
git add api/src/artistpath_api/config.py CLAUDE.md README.md api/README.md frontend/README.md .claude/agents/ml-graph-analyst.md docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md docs/README.md docs/superpowers/TEST-QUEUE.md
git commit -m "feat: adopt graph-t15-tiebreakfix.bin; dev defaults to the 75k artifact

Track 1 of the repair+retune design: the 2.8 tie-break fix is built,
verified against Arm 2, and adopted without a listen per log 4.1. The 5k
dev fixture is retired (spec s1 decision 4) - ApiConfig.graph_path now
defaults to the adopted artifact; use-the-app entry queued."
```

---

### Task 5: Snyk scan, execution log, push, PR

**Files:**
- Create: `docs/superpowers/2026-07-23-repair-and-retune-execution-log.md`
- Modify: `docs/README.md` (Active table row for the new log)
- Modify: `CLAUDE.md` (orient-table "next action" row)

**Interfaces:**
- Consumes: everything committed in Tasks 1–4.
- Produces: the retained execution log Track 2's session starts from; a draft PR.

- [ ] **Step 1: Snyk scan the new/changed first-party code**

Run the Snyk MCP code scan (`snyk_code_scan`) over the repo (changed Python: `builder/src/artistpath_builder/graph.py`, `builder/src/artistpath_builder/pipeline.py`, the two test files, `builder/analysis/2026-07-23-tiebreak-fix-verification/verify.py`, `api/src/artistpath_api/config.py`). Fix any issue it reports in *these files* using the result context, rescan until they are clean. (Pre-existing accepted findings — the `listen.html` XSS trio, log §7.1 item 3 — are recorded as accepted; do not "fix" them here.)

- [ ] **Step 2: Start the Track execution log**

Create `docs/superpowers/2026-07-23-repair-and-retune-execution-log.md`:

```markdown
# Repair + retune — execution log

**Role: ACTIVE.** The retained execution log for the work governed by
`specs/2026-07-23-defect-remediation-and-cost-retune-design.md`. Appended
per task, not only at closeout. Figures: artifact identity lives in
`findings/2026-07-23-tiebreak-fix-adoption.md`; defect mechanics live in the
Phase 1 log §2.8. This log records decisions and deviations, not numbers.

## Track 1 — tie-break remediation (2026-07-23)

- **T1** `mutual_knn_cap` gained an optional `ranking` argument (membership
  by ranking, scores from adjacency; ValueError on node-set mismatch;
  `ranking=None` is the old behaviour, byte-for-byte). TDD; all builder
  graph tests pass.
- **T2** `build_from_archive` passes the unclipped `scored_adjacency`
  strengths as the ranking. New regression test reproduces the §2.8
  ceiling-saturation regime in miniature and asserts the slot goes to the
  genuinely stronger neighbour; a second test pins emitted scores to the
  clipped values. Full builder suite green, including byte-identity replay.
- **T3** 75k rebuild ×2 (determinism confirmed by identical sha256), then
  `analysis/2026-07-23-tiebreak-fix-verification/verify.py`: Arm 2 topology
  reproduced; shared-edge scores bit-identical to capfix; popularity
  ordering preserved. <note any deviation here, or "no deviations">
- **T4** Adopted. Identity: `findings/2026-07-23-tiebreak-fix-adoption.md`.
  The 5k dev fixture is retired (spec §1 decision 4): `ApiConfig.graph_path`
  defaults to the adopted 75k artifact, smoke-checked through the default
  (Radiohead + Beatles present, path routes). The only api edit in Track 1
  is that default; routing code untouched. No frontend changes.
  TEST-QUEUE entry queued.
- **Seam:** Track 1 ends here per spec §2. Track 2 (cost-function retune)
  starts from the spec §4 + this log + the adoption findings doc, with its
  own plan, an `ml-graph-analyst` protocol review, and a pre-registration
  that fixes the primary effect size and pair set before any arm runs.

## Track 2 — cost-function retune

*(not started — next session begins here)*
```

- [ ] **Step 3: Update the doc map and CLAUDE.md orient row**

Add to `docs/README.md`'s **Active** table:

```markdown
| `superpowers/2026-07-23-repair-and-retune-execution-log.md` | Retained execution log for the repair+retune work. Track 1 record; Track 2 continues it. |
```

In `CLAUDE.md`'s orient table, replace the "What is the next action?" row's content with:

```markdown
| **What is the next action?** | **Track 2 of the repair+retune design** — the cost-function retune. Read `docs/superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md` §4 and the execution log `docs/superpowers/2026-07-23-repair-and-retune-execution-log.md`. Track 1 (the §2.8 tie-break fix) is DONE and adopted — artifact identity in `docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`. The Phase 1 log's §2 remains the defect record; its §2.12 diagnosis (cost-function problem, not graph problem) is what Track 2 acts on. |
```

- [ ] **Step 4: Commit and push, open the draft PR**

```bash
git add docs/superpowers/2026-07-23-repair-and-retune-execution-log.md docs/README.md CLAUDE.md
git commit -m "docs: Track 1 execution log; point the orient table at Track 2"
git push
```

Then open the draft PR:

```bash
gh pr create --draft --title "Repair + retune, Track 1: fix the 2.8 tie-break and adopt the rebuilt graph" --body "$(cat <<'EOF'
Track 1 of docs/superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md.

- mutual_knn_cap ranks top-k on UNCLIPPED damped strengths (the Phase 1 log
  2.8 Arm 2 intervention, now in the shipped builder); emitted scores stay
  p99-clipped; popularity untouched.
- 75k rebuild verified against Arm 2 topology (Radiohead restored, degree
  50; Beatles 7 -> 50) and against capfix for shared-edge score
  bit-identity. Adopted by structural equivalence per log 4.1 - no listen.
- Adopted-artifact identity (sha256): docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md
  (artifacts are gitignored; the checksum is their only identity).
- Execution log: docs/superpowers/2026-07-23-repair-and-retune-execution-log.md
- Owner decisions recorded 2026-07-23: repair+retune route; nine-names
  verdict (popularity != fame at the top - external fame proxy for Track 2
  scoring); listening-test prohibition scoped to closed verdicts only; the
  5k dev fixture is retired - ApiConfig.graph_path defaults to the adopted
  75k artifact (dev tests what the record measured).
- Deferred, unchanged: p99 ceiling rescale (behind a measured trigger),
  cap_strategy redesign, clips C1/C2, frontend UX.
- Track 2 (cost-function retune) follows on this branch with its own plan.

Gates: builder suite green (incl. byte-identity replay), api suite green,
verify.py ALL CHECKS PASSED, Snyk clean on changed files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Wr5XKZ2kEiMoikK8qvh1N9
EOF
)"
```

Expected: PR URL printed. Leave it draft — Track 2 lands on the same branch or its own follow-up branch; the closeout skill's D5 governs the final body.
