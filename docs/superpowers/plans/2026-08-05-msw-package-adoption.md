# `MSW-` Map Switch: Adopting the Listened Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `ULC-A4` — candidate data set + trimmed-union connection rule + gentle fame-currency `known` ramp — as the production map and router, with the merged un-listenable filter on.

**Architecture:** Four implementation jobs, then rebuild/verify/adopt/deploy. (1) Port `cap_trimmed_union` from the frozen Track B harness into shipped builder code. (2) Add a `fame` fetch stage to the builder — crawl-shaped: fetches ListenBrainz listener counts into the archive, so `build` stays offline. (3) Carry `fame_lb_raw` in the APG1 artifact as an additive metadata key (the `deezer_ids` precedent). (4) Add the fame-percentile ramp term to the API cost function behind a config knob defaulting off. Then: fetch fame for the candidate archive, build, verify, flip defaults, deploy.

**Tech Stack:** Python (builder + api), numpy, FastAPI; no frontend changes.

**Owner authority note (read before executing):** This adoption is an **owner override of the standing `GBL-` null** (margin 3 vs bar 5; pre-registered consequence "production stands"). Taken knowingly by the owner 2026-08-05, informed by `CAU-` (coherence meets his bar; `CAU-` §5.4). It must be recorded as an override in the execution log and PR body — never as something `GBL-` or `CAU-` licensed.

## Global Constraints

- Prefix every `uv` command with `UV_LINK_MODE=copy`; run from the owning package directory (`builder/` or `api/`).
- `PYTHONIOENCODING=utf-8` on anything printing artist names; `python -u` on any long/backgrounded job.
- **Determinism (builder spec §9):** byte-identical output for identical archive input. The fame data becomes part of the archive input; `build` never touches the network (the replay test proves it — do not break it).
- **Currency in the name:** every new quantity names its basis — `fame_lb_raw` (nullable count), `fame_lb_pctl` (percentile). Never reuse `pop_raw`/`popularity` for fame. Wire-contract exemptions (`popularity` APG1 key, API JSON field) stay untouched.
- **Figures live in their owning documents** — this plan restates none. Exposure figures: `findings/2026-08-05-unlistenable-class-results.md`. Adopted-graph identity: checksum in `findings/2026-07-23-tiebreak-fix-adoption.md`.
- **Identifier namespace:** `MSW-` (collision-checked free across all refs 2026-08-05). Gates: `MSW-G1`–`G3`. Verification checks: `MSW-V1`–`V4`.
- `builder/` and `api/` **share no code**; the APG1 format is the contract. Both parsers change in lockstep by hand (Tasks 5 and 6).
- Per the global security instruction: `snyk_code_scan` on new first-party code before the branch merges (Task 11).
- **This plan compares nothing** — no arms, no factor table owed. The experiment record already exists (`CRE-`, `GBL-`, `CAU-`); this is an implementation of the already-chosen `B-S1-P1a` shape.

## Named deviations from the listened arm (`B-S1-P1a`)

State these wherever the deployed package is described; they are why the deployed thing is "a new candidate", not the listened arm re-created:

1. **The un-listenable filter is on** (`drop_unlistenable`, default since PR #80). The listened builds predate it. This is the change the owner is adopting *for*.
2. **Percentile frame.** The `CRE-` harness framed `fame_lb_pctl` against the *previously adopted* artifact's non-null values (a fixed experimental ruler). Shipped semantics: the frame is **the served artifact's own non-null `fame_lb_raw` values, computed at API boot**. Plain sentence: *the app ranks each artist's obscurity against everyone else on its own map, not against a frozen list from an older map.* A shipped ruler pinned to a retired artifact would go stale at every future adoption.
3. **Null pricing.** In the shipped artifact every artist carries a fame record by construction (Task 4's refusal), so the harness's "absent from snapshot → neutral 0.5" class cannot arise. Nulls (measured zero listeners) price at percentile 0.0 — maximal obscurity, same direction as the harness's `frame.pctl(0)`.

## Handoff seams (chosen at authoring time — 12 tasks is past the ~8-task line)

- **Seam 1** after Task 5 (builder side complete: cap + fame stage + artifact key). Retire the session; commit state is the handoff.
- **Seam 2** after Task 7 (API side complete; everything default-off).
- **Seam 3** after Task 10 (artifact built and verified, nothing adopted). **The Seam-3 session must not be the session that reads the verification results and decides — report to the owner at this seam.**
- **Seam 4** after Task 12 (adopted and deployed; closeout).

At each seam: append to `docs/superpowers/2026-08-05-msw-execution-log.md` per task (decisions and reasoning, not narration), update the draft PR body, hand off.

---

### Task 1: Port `trimmed_union_cap` into shipped builder code

**Files:**
- Modify: `builder/src/artistpath_builder/graph.py` (add function after `mutual_knn_cap`, which ends near line 126)
- Test: `builder/tests/test_graph.py` (append)

**Interfaces:**
- Consumes: `symmetrise(adjacency)` (`graph.py:58`), `Adjacency = dict[str, dict[str, float]]`
- Produces: `trimmed_union_cap(adjacency: Adjacency, top_j: int, degree_ceiling: int, *, ranking: Adjacency) -> Adjacency` — used by Task 2's pipeline seam.

The source of truth is the frozen `cap_trimmed_union` in `builder/analysis/2026-07-30-track-b-cap-selection/cb_build_variants.py:163-256` (`weakest_first` trim only — `banded_quota` lost Track B's selection and is not ported; YAGNI). The equivalence test against the frozen implementation is the guard on the port, so a transcription slip fails loudly rather than shipping a subtly different rule.

- [ ] **Step 1: Write the failing tests**

```python
# append to builder/tests/test_graph.py

def _random_adjacency(seed: int, n: int = 60, per_node: int = 12) -> dict:
    """Synthetic scored adjacency shaped like pipeline output: string mbids,
    per-node dicts of dst -> score."""
    import random
    rng = random.Random(seed)
    mbids = [f"{i:04d}-mbid" for i in range(n)]
    adjacency = {}
    for m in mbids:
        dsts = rng.sample([x for x in mbids if x != m], per_node)
        adjacency[m] = {d: rng.random() for d in dsts}
    return adjacency


def test_trimmed_union_cap_bounds_degree_and_is_symmetric():
    adjacency = _random_adjacency(1)
    ranking = adjacency  # ranking on the same strengths is fine for the property
    result = trimmed_union_cap(adjacency, 5, 5, ranking=ranking)
    for node, edges in result.items():
        assert len(edges) <= 5
        for dst in edges:
            assert node in result[dst], "must stay symmetric after trimming"


def test_trimmed_union_cap_is_deterministic():
    adjacency = _random_adjacency(2)
    a = trimmed_union_cap(adjacency, 5, 5, ranking=adjacency)
    b = trimmed_union_cap(adjacency, 5, 5, ranking=adjacency)
    assert a == b


def test_trimmed_union_cap_keeps_reverse_only_edges_under_ceiling():
    # A node u that does not rank v, while v ranks u top-j: the union must
    # admit the edge (that is what "union" buys over mutual k-NN).
    adjacency = {
        "aaaa": {"bbbb": 0.9},
        "bbbb": {"aaaa": 0.9, "cccc": 0.5},
        "cccc": {"bbbb": 0.5},
    }
    result = trimmed_union_cap(adjacency, 1, 5, ranking=adjacency)
    # b ranks a top-1; c->b is b's reverse-only edge and survives under the ceiling
    assert "cccc" in result["bbbb"]


def test_trimmed_union_cap_matches_frozen_track_b_implementation():
    """The port is byte-equivalent to the frozen Track B cap on random input.

    Imports the frozen module read-only, per the alias policy in
    builder/analysis/README.md — never write new *shipped* code against it;
    a test asserting equivalence is the sanctioned direction.
    """
    import sys
    from pathlib import Path
    frozen_dir = Path(__file__).resolve().parents[1] / (
        "analysis/2026-07-30-track-b-cap-selection")
    sys.path.insert(0, str(frozen_dir))
    try:
        from cb_build_variants import cap_trimmed_union
    finally:
        sys.path.remove(str(frozen_dir))
    for seed in (3, 4, 5):
        adjacency = _random_adjacency(seed)
        frozen = cap_trimmed_union(adjacency, adjacency, {}, j=5, d=5,
                                   trim="weakest_first")
        ported = trimmed_union_cap(adjacency, 5, 5, ranking=adjacency)
        assert ported == frozen, f"seed {seed}: port diverges from frozen cap"
```

Also add `trimmed_union_cap` to the existing `from artistpath_builder.graph import ...` line at the top of the test file.

- [ ] **Step 2: Run tests to verify they fail**

From `builder/`: `UV_LINK_MODE=copy uv run --extra dev pytest -q -k trimmed_union`
Expected: FAIL — `ImportError: cannot import name 'trimmed_union_cap'`

- [ ] **Step 3: Implement `trimmed_union_cap` in `graph.py`**

```python
def trimmed_union_cap(
    adjacency: Adjacency,
    top_j: int,
    degree_ceiling: int,
    *,
    ranking: Adjacency,
) -> Adjacency:
    """Non-reciprocal supply rule: top-j UNION, then a hard degree ceiling.

    ADOPTED with the 2026-08-05 map switch (Track B selection `TUw-50-50`,
    the `B-S1` cell; findings/2026-07-30-track-b-cap-selection-results.md).
    Union alone bounds nothing — a famous artist appears in unboundedly many
    lists — so the ceiling deletes WHOLE EDGES, weakest pair-strength first,
    because truncating one endpoint's row would break symmetry again (the
    pre-symmetrise defect, Phase 2).

    BOUND: degree <= degree_ceiling by construction. Single pass suffices:
    nodes are processed in a fixed order and deletion only lowers degrees, so
    a node brought to the ceiling cannot later rise above it.

    Determinism: top-j ties break on lowest MBID; nodes are processed by
    (-degree, mbid); deletions are weakest-first with ties dropping the
    HIGHEST neighbour MBID first. Byte-for-byte the frozen Track B rule
    (cb_build_variants.cap_trimmed_union, weakest_first) — the equivalence
    test in test_graph.py pins the two together.
    """
    keep: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(edges, key=lambda dst: (-ranking[node][dst], dst))
        keep[node] = set(ranked[:top_j])

    unioned: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in keep[node] or node in keep.get(dst, set()):
                unioned[node][dst] = score
    result = symmetrise(unioned)

    # Symmetric strength so both endpoints agree on which edge is weakest.
    def strength(u: str, v: str) -> float:
        return max(
            ranking.get(u, {}).get(v, float("-inf")),
            ranking.get(v, {}).get(u, float("-inf")),
        )

    class _desc:
        """Reverses string order so strength ties drop the highest MBID first."""
        __slots__ = ("value",)

        def __init__(self, value: str) -> None:
            self.value = value

        def __lt__(self, other: "_desc") -> bool:
            return self.value > other.value

        def __eq__(self, other: object) -> bool:
            return isinstance(other, _desc) and self.value == other.value

    for node in sorted(result, key=lambda n: (-len(result[n]), n)):
        excess = len(result[node]) - degree_ceiling
        if excess <= 0:
            continue
        doomed = sorted(
            result[node], key=lambda v: (strength(node, v), _desc(v))
        )[:excess]
        for victim in doomed:
            result[node].pop(victim, None)
            result[victim].pop(node, None)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

`UV_LINK_MODE=copy uv run --extra dev pytest -q -k trimmed_union`
Expected: 4 passed. Then the full suite: `UV_LINK_MODE=copy uv run --extra dev pytest -q` — no regressions.

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/graph.py builder/tests/test_graph.py
git commit -m "MSW-: port trimmed_union_cap (TUw shape) into shipped builder, pinned to the frozen Track B rule"
```

---

### Task 2: Wire `cap_strategy="trimmed_union"` through config and pipeline

**Files:**
- Modify: `builder/src/artistpath_builder/config.py` (the `cap_strategy` field ~line 81 and its `__post_init__` validation ~line 202)
- Modify: `builder/src/artistpath_builder/pipeline.py:352-354` (the cap seam)
- Test: `builder/tests/test_config.py`, `builder/tests/test_pipeline.py` (append)

**Interfaces:**
- Consumes: `trimmed_union_cap` (Task 1).
- Produces: `BuilderConfig.cap_strategy` accepting `"mutual_knn" | "trimmed_union"`; new knobs `union_top_j: int = 50`, `union_degree_ceiling: int = 50`. **Defaults stay `mutual_knn` until Task 11** — the adoption flip is one commit, checked by closeout.

- [ ] **Step 1: Write the failing tests**

```python
# builder/tests/test_config.py — append
def test_trimmed_union_is_a_permitted_cap_strategy():
    cfg = BuilderConfig(cap_strategy="trimmed_union")
    assert cfg.union_top_j == 50 and cfg.union_degree_ceiling == 50

def test_unknown_cap_strategy_still_raises():
    with pytest.raises(ValueError):
        BuilderConfig(cap_strategy="pre_symmetrise")
```

```python
# builder/tests/test_pipeline.py — append
def test_trimmed_union_build_bounds_degree(archive_fixture):
    """Same archive, trimmed_union strategy: every node's degree <= ceiling.
    Uses the existing offline-archive fixture the replay test uses."""
    cfg = replace(FIXTURE_CONFIG, cap_strategy="trimmed_union",
                  union_top_j=5, union_degree_ceiling=5)
    graph, _ = build_from_archive(cfg, archive_fixture)   # match existing call shape
    degrees = np.diff(graph.offsets)
    assert int(degrees.max()) <= 5

def test_mutual_knn_build_is_byte_identical_before_and_after_the_seam(archive_fixture):
    """MSW-G1: the refactored cap seam must not move a byte of the default
    build. Serialised bytes are compared, not just structure."""
    a = serialise(build_from_archive(FIXTURE_CONFIG, archive_fixture)[0])
    b = serialise(build_from_archive(FIXTURE_CONFIG, archive_fixture)[0])
    assert hashlib.sha256(a).hexdigest() == hashlib.sha256(b).hexdigest()
```

Adapt fixture/config names to what `test_pipeline.py` actually uses (the replay test's offline archive fixture); `build_from_archive`'s true return shape is at `pipeline.py:117`. **`MSW-G1` proper:** before touching the seam, build the committed 500-node test fixture archive once with current `main` code and record the sha256 in the execution log; after the change, the same build must reproduce that sha. If the current tests already pin a fixture-build sha, cite that instead of recording a new one.

- [ ] **Step 2: Run to verify failure** — `UV_LINK_MODE=copy uv run --extra dev pytest -q -k "trimmed_union or byte_identical"`. Expected: FAIL (unknown strategy raises).

- [ ] **Step 3: Implement**

In `config.py`: extend the field comment (the ADOPTED/`LOST` history stays; add the trimmed-union sentence citing Track B results), add the two knobs beside it:

```python
    cap_strategy: str = "mutual_knn"
    # trimmed_union knobs (Track B `TUw-50-50`, adopted with the 2026-08-05
    # map switch). Ignored under mutual_knn.
    union_top_j: int = 50
    union_degree_ceiling: int = 50
```

and in `__post_init__` replace the `!= "mutual_knn"` check:

```python
        if self.cap_strategy not in ("mutual_knn", "trimmed_union"):
            raise ValueError(
                f"cap_strategy={self.cap_strategy!r} is not supported. "
                "Permitted: 'mutual_knn', 'trimmed_union'. The legacy "
                "'pre_symmetrise' remains deleted (Phase 2 spec §8 risk 4)."
            )
```

In `pipeline.py:352`, replace the direct call with the strategy dispatch:

```python
    if config.cap_strategy == "trimmed_union":
        adjacency = trimmed_union_cap(
            adjacency, config.union_top_j, config.union_degree_ceiling,
            ranking=ranking,
        )
    else:
        adjacency = mutual_knn_cap(
            adjacency, config.max_neighbours_per_artist, ranking=ranking
        )
```

(import `trimmed_union_cap` beside `mutual_knn_cap` at `pipeline.py:32`).

- [ ] **Step 4: Run the full builder suite** — `UV_LINK_MODE=copy uv run --extra dev pytest -q`. Expected: all pass, including the replay/determinism tests untouched.

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/config.py builder/src/artistpath_builder/pipeline.py builder/tests/test_config.py builder/tests/test_pipeline.py
git commit -m "MSW-: cap_strategy=trimmed_union wired through the pipeline seam; mutual_knn default untouched (MSW-G1)"
```

---

### Task 3: The `fame` fetch stage — network to archive, never to build

**Files:**
- Create: `builder/src/artistpath_builder/fame.py`
- Modify: `builder/src/artistpath_builder/cli.py` (new `fame` subcommand)
- Test: `builder/tests/test_fame.py`

**Interfaces:**
- Consumes: `LocalArchive`/`S3Archive` (`archive.py:28,57` — `put`/`get`/`has`/`keys`).
- Produces: archive keys `fame/<mbid>.json`, each `{"fame_lb_raw": <int or null>, "fetched": "YYYY-MM-DD"}`; `fetch_fame(archive, mbids, fetcher, *, batch_size, today) -> FameFetchReport`; `load_fame(archive, mbids) -> dict[str, int | None]` (raises `MissingFameError` listing absentees — Task 4 consumes this).

Design, fixed here: the stage fetches for **every artist in the archive's similarity population**, resumable via `archive.has()` (mirrors the crawl's checkpoint semantics — already-fetched mbids are skipped, which also makes re-runs cheap). Instrument: ListenBrainz `POST /1/popularity/artist` → `total_user_count`, exactly the adopted `FAM-` instrument (`fi_union_snapshot.manifest.json` names it). Batched under the server's `MAX_ITEMS_PER_GET` truncation limit — `fi_fetch.py` reads it from ListenBrainz master; use the same batch size it used and name it in a comment. A `--seed <fi_union_snapshot.json>` option imports the frozen 2026-08-02 snapshot's values (sha-verified against `fi_union_snapshot.manifest.json`) as already-fetched records dated 2026-08-02, so ~93k artists cost zero requests. **A null is a measured absence and is stored, not skipped** — `has()` must return True for it, or resume re-fetches every null forever.

- [ ] **Step 1: Write the failing tests** — `test_fame.py` with an in-memory fake fetcher (the injected-fetcher pattern the crawl tests use):

```python
def test_fetch_writes_one_record_per_mbid_and_preserves_nulls(tmp_path):
    archive = LocalArchive(tmp_path)
    calls = []
    def fetcher(batch):
        calls.append(list(batch))
        return {m: (None if m.endswith("b") else 7) for m in batch}
    report = fetch_fame(archive, ["aa", "bb"], fetcher, batch_size=50,
                        today="2026-08-05")
    assert json.loads(archive.get("fame/aa.json"))["fame_lb_raw"] == 7
    assert json.loads(archive.get("fame/bb.json"))["fame_lb_raw"] is None
    assert report.fetched == 2

def test_fetch_resumes_past_existing_records_including_nulls(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put("fame/aa.json", b'{"fame_lb_raw": null, "fetched": "2026-08-02"}')
    seen = []
    def fetcher(batch):
        seen.extend(batch); return {m: 1 for m in batch}
    fetch_fame(archive, ["aa", "bb"], fetcher, batch_size=50, today="2026-08-05")
    assert seen == ["bb"], "a stored null must not be re-fetched"

def test_load_fame_raises_naming_the_missing(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put("fame/aa.json", b'{"fame_lb_raw": 3, "fetched": "2026-08-05"}')
    with pytest.raises(MissingFameError) as e:
        load_fame(archive, ["aa", "bb"])
    assert "bb" in str(e.value) and "1" in str(e.value)

def test_seed_import_marks_snapshot_values_fetched(tmp_path):
    archive = LocalArchive(tmp_path)
    snap = tmp_path / "snap.json"
    snap.write_text('{"aa": 12, "bb": null}')
    seed_fame(archive, snap, expected_sha256=hashlib.sha256(
        snap.read_bytes()).hexdigest())
    assert json.loads(archive.get("fame/aa.json"))["fame_lb_raw"] == 12
    assert archive.has("fame/bb.json")

def test_seed_refuses_a_wrong_sha(tmp_path):
    archive = LocalArchive(tmp_path)
    snap = tmp_path / "snap.json"; snap.write_text("{}")
    with pytest.raises(ValueError):
        seed_fame(archive, snap, expected_sha256="0" * 64)
```

- [ ] **Step 2: Run to verify failure** — `UV_LINK_MODE=copy uv run --extra dev pytest -q -k fame`. Expected: FAIL, module missing.

- [ ] **Step 3: Implement `fame.py`** — `fetch_fame` batches pending mbids in sorted order (determinism of request order; the archive result is order-independent anyway), calls the injected fetcher, writes one JSON record per mbid; `seed_fame` verifies the sha then bulk-writes; `load_fame` reads `fame/<mbid>.json` for each requested mbid, collecting absentees and raising `MissingFameError` with the count and first 10 mbids. The real fetcher (`lb_fame_fetcher(config)`) lives beside `http_fetcher` in `crawl.py`'s style: rate-limited via `BuilderConfig.requests_per_second`, retries via `max_retries`, the `FAM-` endpoint constant with the truncation-limit comment. Wire `cmd_fame` into `cli.py` (`fame --archive-dir ... [--s3-bucket/--s3-prefix] [--seed PATH --seed-sha SHA]`), deriving the mbid population the same way `cmd_build` derives its known set from the archive.

- [ ] **Step 4: Run to verify pass** — `UV_LINK_MODE=copy uv run --extra dev pytest -q -k fame`; then full suite.

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/fame.py builder/src/artistpath_builder/cli.py builder/tests/test_fame.py
git commit -m "MSW-: fame fetch stage — ListenBrainz listener counts into the archive, seedable from the frozen FAM- snapshot"
```

---

### Task 4: `build` reads fame offline and refuses an uncovered population

**Files:**
- Modify: `builder/src/artistpath_builder/pipeline.py` (`build_from_archive`, near where drop lists are applied), `builder/src/artistpath_builder/graph.py` (the `Graph` dataclass, line 21)
- Test: `builder/tests/test_pipeline.py` (append)

**Interfaces:**
- Consumes: `load_fame` / `MissingFameError` (Task 3).
- Produces: `Graph.fame_lb_raw: list[int | None] = field(default_factory=list)` — **defaulted, for the same two load-bearing reasons as `deezer_ids`** (`graph.py:36-39`: frozen probes call positionally; empty list must keep old artifacts byte-identical). Populated in node-id order for every kept node.

This is the `ULC-F1` pattern applied to fame: a graph artist with no fame record means the fetch population and the build population diverged — **refuse to build**, never default. Plain sentence: *the app is about to start steering by a number, so an artist that number was never collected for is a build error, not a shrug.* Gate id: **`MSW-G3`**, exercised in Step 4 of Task 8 against the real archive.

- [ ] **Step 1: Write the failing tests**

```python
def test_build_carries_fame_for_every_node(archive_with_fame_fixture):
    graph, _ = build_from_archive(FIXTURE_CONFIG, archive_with_fame_fixture)
    assert len(graph.fame_lb_raw) == len(graph.mbids)

def test_build_refuses_when_a_graph_artist_lacks_fame(archive_fixture):
    # archive_fixture has similarity data but no fame/ records at all
    with pytest.raises(MissingFameError):
        build_from_archive(FIXTURE_CONFIG, archive_fixture)

def test_build_without_fame_stage_stays_supported_for_frozen_probes(archive_fixture):
    # require_fame=False (the era-pinned escape hatch): identical to today's output
    cfg = replace(FIXTURE_CONFIG, require_fame=False)
    graph, _ = build_from_archive(cfg, archive_fixture)
    assert graph.fame_lb_raw == []
```

Build `archive_with_fame_fixture` as a conftest fixture: the existing offline archive fixture plus `fame/<mbid>.json` records written for all its artists (values arbitrary, at least one null).

- [ ] **Step 2: Run to verify failure.** Expected: FAIL (`fame_lb_raw` attribute missing; `require_fame` unknown).

> **DEVIATION taken during execution: `require_fame` defaults to `False` here, not `True`.** Until Task 11 the shipped router does not read fame, so a fame-less build is genuinely valid and defaulting to `True` would assert a requirement that is not yet true — breaking every existing synthetic-archive test for a property that does not yet matter. It is flipped to `True` in Task 11 alongside `cap_strategy` and the ramp knob, which is the commit where it *becomes* true, and it is treated exactly like `cap_strategy` here: added inert, flipped at adoption. **Task 9's real build passes `require_fame=True` explicitly**, so the artifact this plan ships is covered either way, and the API's boot check (Task 7) is an independent second guard. Task 11 Step 0's era-pinning covers this field too.

- [ ] **Step 3: Implement** — add `require_fame: bool = False` to `BuilderConfig` (comment: the escape hatch exists so frozen-era probe configs and the committed test fixtures still build; era-pinned analysis constructs configs directly, same policy as the two old drop flags). In `build_from_archive`, after the kept node set is final (post-`largest_component`, where `pruned` exists at `pipeline.py:359`): if `require_fame`, call `load_fame(archive, sorted(keep))` and thread the values into the `Graph` in node-id order; else leave `fame_lb_raw` empty. `MissingFameError` propagates — that IS the refusal.

- [ ] **Step 4: Run the full builder suite.** The replay test must still pass — `load_fame` reads the archive, not the network, so the raising-fetcher injection proves the property still holds.

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/config.py builder/src/artistpath_builder/pipeline.py builder/src/artistpath_builder/graph.py builder/tests/
git commit -m "MSW-: build reads fame from the archive and refuses an uncovered population (MSW-G3, the ULC-F1 pattern)"
```

---

### Task 5: The artifact carries `fame_lb` as an additive key

**Files:**
- Modify: `builder/src/artistpath_builder/artifact.py:36-57` (`serialise`; and `deserialise` symmetrically)
- Test: `builder/tests/test_artifact.py` (append)

**Interfaces:**
- Consumes: `Graph.fame_lb_raw` (Task 4).
- Produces: APG1 metadata key `"fame_lb"` — list of int-or-null, index-aligned with `mbids`. **Additive, `FORMAT_VERSION` NOT bumped, omitted when empty** — copy the `deezer_ids` rationale comment (`artifact.py:46-56`) and cite it: both parsers check version for strict equality, and unconditional writing would change the bytes of every frozen-probe artifact.

- [ ] **Step 1: Write the failing tests**

```python
def test_fame_lb_round_trips_with_nulls():
    g = _tiny_graph()                       # existing test helper in this file
    g.fame_lb_raw = [3, None, 0][: len(g.mbids)]
    assert deserialise(serialise(g)).fame_lb_raw == g.fame_lb_raw

def test_empty_fame_omits_the_key_and_preserves_bytes():
    g = _tiny_graph()
    before = serialise(g)                   # fame_lb_raw defaults to []
    assert b'"fame_lb"' not in before
    g2 = _tiny_graph(); g2.fame_lb_raw = []
    assert serialise(g2) == before

def test_artifact_without_fame_deserialises_with_empty_fame():
    g = _tiny_graph()
    assert deserialise(serialise(g)).fame_lb_raw == []
```

(Use the file's actual tiny-graph helper name; if none exists, build a 3-node `Graph` inline the way the existing round-trip test does.)

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — in `serialise`, beside the `deezer_ids` block: `if graph.fame_lb_raw: meta["fame_lb"] = graph.fame_lb_raw`, with the wire-key comment (`fame_lb` is the APG1 wire key; the in-memory identifier carries the full currency `fame_lb_raw`). In `deserialise`: `fame_lb_raw=meta.get("fame_lb", [])`.
- [ ] **Step 4: Run the full builder suite** — the committed 500-node fixtures (no fame key) must still load everywhere.
- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/artifact.py builder/tests/test_artifact.py
git commit -m "MSW-: APG1 additive key fame_lb, deezer_ids pattern — version unbumped, omitted when empty"
```

**→ Seam 1. Retire the session here.** Execution-log entry per task is already written; PR body updated; next session starts at Task 6 with only the committed record.

---

### Task 6: API `GraphStore` reads fame and builds the percentile frame at boot

**Files:**
- Modify: `api/src/artistpath_api/graph_store.py` (dataclass fields near line 41; `deserialise`/load path near line 183)
- Test: `api/tests/test_graph_store.py` (append; the raw-bytes helper is at `test_graph_store.py:18` and `:97`)

**Interfaces:**
- Consumes: APG1 `"fame_lb"` key (Task 5's contract — **written by hand on this side; no shared code, by design**).
- Produces: `GraphStore.fame_lb_pctl: np.ndarray | None` — float64 in [0,1], length N when the artifact carries fame, `None` otherwise. Task 7's cost term and boot check consume exactly this.

Percentile rule (shipped semantics — Named deviation 2): frame = the artifact's own non-null `fame_lb_raw` values. For non-null value x: `pctl(x) = (count of frame values < x) / max(1, len(frame) - 1)`, clipped to [0,1]; nulls → 0.0. Implemented vectorised: `np.searchsorted(sorted_frame, values, side="left")`. Plain sentence beside it in the code: *0 means nobody on this map has fewer recorded listeners; 1 means nobody has more.*

- [ ] **Step 1: Write the failing tests**

```python
def test_fame_pctl_ranks_within_the_artifacts_own_frame():
    payload = _artifact(fame_lb=[10, None, 20, 30])   # extend the helper at :18
    store = GraphStore.load_bytes(payload)             # match existing loader name
    p = store.fame_lb_pctl
    assert p[1] == 0.0                                 # null: maximal obscurity
    assert p[0] < p[2] < p[3]
    assert p[3] == 1.0

def test_fame_pctl_is_none_without_the_key():
    store = GraphStore.load_bytes(_artifact())         # no fame_lb key
    assert store.fame_lb_pctl is None

def test_fame_shorter_than_n_is_rejected():
    payload = _artifact(fame_lb=[1])                   # N > 1 in the helper
    with pytest.raises(ArtifactError):
        GraphStore.load_bytes(payload)
```

Extend the `_artifact` helper (`test_graph_store.py:97`) with an optional `fame_lb` metadata entry; match the real loader entry point and error type used by the neighbouring tests (`test_graph_store.py:119-132`).

- [ ] **Step 2: Run to verify failure** — from `api/`: `UV_LINK_MODE=copy uv run --extra dev pytest -q -k fame`.
- [ ] **Step 3: Implement** — load `meta.get("fame_lb")`; if present: validate `len == N` (reject short/long like the `mbids` check at `graph_store.py:176`), then compute the frame and the array once at load; store `None` when absent. Field comment carries currency + frame rule + the plain sentence.
- [ ] **Step 4: Run the api suite** — `UV_LINK_MODE=copy uv run --extra dev pytest -q`. The committed fixtures (fameless) exercise the `None` path everywhere.
- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/graph_store.py api/tests/test_graph_store.py
git commit -m "MSW-: GraphStore reads fame_lb and builds fame_lb_pctl at boot; fameless artifacts load unchanged"
```

---

### Task 7: The ramp term in the cost function, behind a default-off knob

**Files:**
- Modify: `api/src/artistpath_api/config.py` (weights block, after `w_degree_hub` at line 54), `api/src/artistpath_api/pathfinding.py` (cost loop, lines 130-137; and `find_journey`'s second search inherits it for free), `api/src/artistpath_api/app.py` (boot validation beside the sha check)
- Test: `api/tests/test_pathfinding.py`, `api/tests/test_app.py` (append)

**Interfaces:**
- Consumes: `GraphStore.fame_lb_pctl` (Task 6), `Exclusion.reason == KNOWN` (existing).
- Produces: `ApiConfig.w_known_ramp_fame_pctl: float = 0.0` — **default 0.0 in this task; Task 11 flips it to the adopted 0.01** (`P1a`, `cre_common.py:81`).

Semantics, copied from the verified mirror (`cre_mirror.py:268-278, 341-345`) and stated as invariants in the code comment: k = count of `known` exclusions, fixed per request, so the ramp is a constant multiplier, not search state; applied to **relaxation targets only**; **the target endpoint is exempt** (the final hop into B is on every complete path exactly once, so tolling it adds a constant and distorts nothing); **added only when live, never as `+ 0.0`** — at k = 0 or knob 0.0 the cost arithmetic is byte-identical to today's (**`MSW-G2`**). Plain sentence for the knob comment: *each press of "know them already" adds a toll on widely-listened-to artists, so the tenth press pushes much harder toward the obscure than the first.*

- [ ] **Step 1: Write the failing tests**

```python
def test_ramp_off_leaves_costs_byte_identical(monkeypatch_store_with_fame):
    """MSW-G2: knob 0.0 → identical dist maps to a build with no ramp code.
    Assert on find_path output equality across every fixture pair the existing
    pathfinding tests use, at k=0 and k=3 known exclusions."""

def test_ramp_prices_fame_on_relaxation_targets_only():
    # 4-node line a-b-c-d with fame_pctl [0, 1, 0, 0], one KNOWN exclusion,
    # knob 1.0: the a->d path cost includes exactly 1.0 * 1 * fame[b] + ... for
    # interior nodes, and d (target) contributes zero ramp.
    # Reuse the ladder identity from cre_ladder.py:110-115: ramp component
    # == r * k * sum(fame_pctl over relaxed interior nodes).

def test_ramp_scales_with_known_count():
    # same store: cost delta at k=2 is twice the delta at k=1 for the same path

def test_boot_refuses_ramp_on_a_fameless_artifact():
    # ApiConfig(w_known_ramp_fame_pctl=0.01) + fixture without fame_lb:
    # create_app raises at boot with a message naming both facts. Same
    # philosophy as the sha check: a misconfigured artifact refuses to start.

def test_ramp_disabled_and_fameless_boots_fine():
    # knob 0.0 + fameless fixture: today's world keeps working
```

Write these as real tests against the actual store/test fixtures (the in-memory injected store pattern from `conftest.py`); the comments above are the specification of each body.

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement**

`config.py` (after `w_degree_hub`):

```python
    # "known" bypass ramp in FAME percentile currency (fame_lb_pctl; the
    # CRE- adopted device, arm B-S1-P1a). Each press of "know them already"
    # adds a toll on widely-listened-to artists, so the tenth press pushes
    # much harder toward the obscure than the first. 0.0 = off (and the cost
    # arithmetic is then byte-identical to the pre-ramp router: the term is
    # added only when live, never as + 0.0).
    w_known_ramp_fame_pctl: float = 0.0
```

`pathfinding.py`, before the Dijkstra loop (beside `floor_raw` at line 103-104):

```python
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    ramp_fame = cfg.w_known_ramp_fame_pctl * n_known
    ramp_fame_on = ramp_fame != 0.0 and store.fame_lb_pctl is not None
```

and inside the loop, after the existing `cost = (...)` block (line 137):

```python
            # Fame-currency `known` ramp (CRE-; mirror rules preserved):
            # relaxation target only, target endpoint exempt, added only when
            # live — never as `+ 0.0` — so k=0 stays byte-identical (MSW-G2).
            if ramp_fame_on and v != target:
                cost += ramp_fame * float(store.fame_lb_pctl[v])
```

`app.py`, beside the sha verification: if `cfg.w_known_ramp_fame_pctl > 0.0 and store.fame_lb_pctl is None`, raise at boot naming the knob and the artifact.

- [ ] **Step 4: Run the full api suite.** Expected: all pass; existing pathfinding tests prove `MSW-G2` (they run with knob 0.0).
- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/config.py api/src/artistpath_api/pathfinding.py api/src/artistpath_api/app.py api/tests/
git commit -m "MSW-: fame-currency known ramp behind w_known_ramp_fame_pctl (default 0.0); boot refuses ramp-on over a fameless artifact (MSW-G2)"
```

**→ Seam 2. Retire the session.** Everything shipped is default-off; the app's behaviour is unchanged everywhere.

---

### Task 8: Fetch fame for the candidate archive (network, resumable)

**Files:**
- No source changes. Operational: run the Task 3 stage against `builder/scratch/grt-archive-algb/` (75,000 responses, verified on disk — `ULC-` results §4.1).

- [ ] **Step 1: Back up the frozen snapshot first.** `fi_union_snapshot.json` is gitignored, single-machine, and this plan's cheapest-to-lose dependency (the `MSW-` weakest link named in planning). Copy it and its manifest to the S3 archive bucket (or any second machine) and record where in the execution log, before anything else runs.

- [ ] **Step 2: Seed.** From `builder/`:

```bash
UV_LINK_MODE=copy uv run python -u -m artistpath_builder.cli fame \
  --archive-dir ./scratch/grt-archive-algb \
  --seed ./analysis/2026-08-02-fame-instrument/fi_union_snapshot.json \
  --seed-sha d9d6d5d340a81875dd795067d6332a40d813ebfb5b8258048290c27f34662ae8
```

(sha from `fi_union_snapshot.manifest.json` — copied from the sidecar, never transcribed from memory; adjust the invocation to the real CLI name from Task 3.)

- [ ] **Step 3: Fetch the remainder.** Same command; the report says how many were fetched fresh (expected: the archive population minus snapshot overlap — the snapshot covers the union of the two *pruned artifact* populations, so archive artists that were dropped or pruned in the 2026-07-30 build will fetch fresh). Run with `python -u`; expect minutes-to-an-hour at `requests_per_second`. **A stored null is a result** — the report's `fetched + skipped` must equal the archive population at the end.

- [ ] **Step 4: Record** counts, date, and elapsed time in the execution log. This snapshot date is part of the artifact's identity — it goes in the manifest sidecar notes in Task 9.

- [ ] **Step 5: Commit** (execution log only — the archive is gitignored).

```bash
git add docs/superpowers/2026-08-05-msw-execution-log.md
git commit -m "MSW-: fame coverage complete over the candidate archive; counts and provenance in the log"
```

---

### Task 9: Build the candidate artifact and its manifest

**Files:**
- Operational; no source changes expected.

- [ ] **Step 1: Exercise `MSW-G3` for real, before the real build.** Temporarily move one `fame/<mbid>.json` for a known-kept artist out of the archive, run `build`, confirm it **refuses** with `MissingFameError` naming the artist; restore the file. Record the refusal output in the execution log — a green instrument that has never gone red is not evidence (working-style memory).

- [ ] **Step 2: Build.** From `builder/`:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u -m artistpath_builder.cli build \
  --archive-dir ./scratch/grt-archive-algb \
  --out ./scratch/graph-msw-tu50.bin \
  --cap-strategy trimmed_union
```

If the CLI has no `--cap-strategy` flag, add one in this task (mirroring how `cmd_build` already surfaces config fields; one flag, one test asserting it reaches `BuilderConfig`). `drop_unlistenable` is already the default (`config.py:192`). Acceptance checks (`acceptance.py`) run as part of build — a failure stops this plan and goes to the owner; do not route around it.

- [ ] **Step 3: Manifest.** Confirm the sidecar `graph-msw-tu50.bin.json` was written (`manifest.py` — `build_manifest`/`write_manifest` are wired into `cmd_build`); add the fame snapshot provenance (fetch dates, seed sha) if the manifest supports notes, else record them beside the sha in the execution log. **The sha256 in this sidecar is the artifact's identity from here on** — every later step cites it from the sidecar, never by hand (`DEP-24`).

- [ ] **Step 4: Determinism spot-check.** Build a second time to a different filename; `sha256` must match byte-for-byte. Record both hashes in the log.

- [ ] **Step 5: Commit** (log + any CLI flag change).

```bash
git add -- docs/superpowers/2026-08-05-msw-execution-log.md builder/src/artistpath_builder/cli.py builder/tests/
git commit -m "MSW-: candidate artifact built deterministically under trimmed_union + drop_unlistenable + fame; identity in the sidecar"
```

---

### Task 10: Verify — the nine named artists, exposure re-measured, and a real boot

**Files:**
- Create: `builder/analysis/2026-08-05-msw-verification/msw_verify.py` (+ its committed JSON output)
- Operational: local API boot + e2e.

- [ ] **Step 1: `MSW-V1` — the `CAU-` "nothing to listen to" artists are gone.** `msw_verify.py` loads the new artifact and asserts, for each of the nine names from `CAU-` results §1 (`CAU-C3` table + Rick Davies's second slot): Rick Davies, Max Martin, Brad Delson, Joey Kramer, Dallas Taylor, John McVie — resolved to their MBIDs via the *old* candidate artifact's metadata (`graph-algb-full.bin`, sha-verified) — **absent from the new artifact's node set** (dropped by the filter), or if present, the reason is recorded (present-with-releases is a legitimate outcome for Four Tet-class cases; Four Tet and the two DOESN'T-FIT session players are *not* on this list). Output: one JSON row per artist, `{name, mbid, in_old, in_new, verdict}`. **If any of the six core names survives, stop and report to the owner before Task 11** — it means the filter's real-world behaviour diverges from its census, which is exactly what `CAU-` §3 weakest-link 2 asked to have checked.

- [ ] **Step 2: `MSW-V2` — exposure, post-fix.** Re-run the `ULC-` exposure harness (`builder/analysis/2026-08-05-unlistenable-class/ulc_exposure.py`, adapted read-only — do not edit the frozen original; import or copy into `msw_verify.py`'s directory with provenance comment) against the new artifact for the `A4` journey set. Report the measured share beside the frozen pre-fix figure **by citation** (`ULC-` results §1.3). This is a report row, not a gate: no threshold was pre-registered, so no read fires — it goes to the owner as *measured, then inference, then weakest link* per the presentation rules.

- [ ] **Step 3: `MSW-V3` — boot and press.** Boot the API against the new artifact (`ARTISTPATH_GRAPH=../builder/scratch/graph-msw-tu50.bin`, `w_known_ramp_fame_pctl` via env if surfaced, else a one-line local override noted in the log), `npm run dev`, and run the Playwright e2e suite (`npm run test:e2e`). Then generate three known-pair journeys by hand (pairs from the `GBL-` set, e.g. The War On Drugs → Sigur Rós) at d0 and after several `known` presses; confirm journeys build, clips play, deeper presses visibly shift the interior. Record what was pressed and seen.

- [ ] **Step 4: `MSW-V4` — dispatch `ml-graph-analyst` on the frame deviation (derivation only).** One targeted question, verbatim: *"Named deviation 2: the shipped `fame_lb_pctl` frame is the new artifact's own non-null `fame_lb_raw` values; the listened arm's frame was the adopted artifact's (`cre_common.py` §ruler). Over the new artifact's node set, derive the distribution of `|pctl_shipped − pctl_CRE_frame|`, and the resulting per-hop ramp cost difference at r = 0.01, k ∈ {1, 10, 20}, relative to the other cost terms' magnitudes. Figures only — no recommendation."* Inputs: the new artifact, `graph-t15-tiebreakfix.bin` (sha-verified), the fame archive/snapshot. The bound goes into the Seam 3 report as measurement; whether the deviation is acceptable is the owner's Task 11 call. (Null pricing needs no dispatch — the analyst already measured that class inert in `CRE-`; cite `cre_common.py`'s header.) **Conditional, not scheduled:** if Task 9's build showed a structural metric (LCC share, degree distribution, stranding) moving beyond what `B-S1`'s recorded diagnostics predict, that is the property-or-bug trigger — dispatch it then, same rules.

- [ ] **Step 5: Commit** the verification script + JSON + log.

```bash
git add builder/analysis/2026-08-05-msw-verification/ docs/superpowers/2026-08-05-msw-execution-log.md
git commit -m "MSW-V1..V4: nine-artist filter check, post-fix exposure re-measure, live boot, frame-deviation bound"
```

**→ Seam 3. Report to the owner** — verification figures (measured / inferred / weakest link / options), and wait for his go on Task 11. Adoption is his column; this seam is the deliberate stop.

---

### Task 11: Adopt — flip the three defaults, record the override, scan

**Files:**
- Modify: `api/src/artistpath_api/config.py:20-22` (`graph_path` default), `api/src/artistpath_api/config.py` (`w_known_ramp_fame_pctl` 0.0 → 0.01), `builder/src/artistpath_builder/config.py:81` (`cap_strategy` default → `"trimmed_union"`)
- Test: `api/tests/test_config.py:18` (`test_default_graph_path_points_at_an_artifact` — update the expected name)

- [ ] **Step 0 (added during Task 2 execution — do not skip): era-pin the three callers that inherit the `cap_strategy` default.** `grt_score.py:145,155`, `calibrate.py:232`, `cre_build.py:389` all construct `BuilderConfig` without setting `cap_strategy`, so the flip below silently changes what each builds. Add `cap_strategy="mutual_knn"` **and `require_fame=False`** beside each one's existing drop pins, **in this same commit**. The `require_fame` half is the harder failure: none of those archives has ever had the `fame` stage run against it, so an unpinned flip makes all three **refuse to build** outright. `cre_build.py` is the sharp case: its `gate()` (line 410) compares its mirror against a live `build_from_archive` for byte-identity, so an unpinned flip makes that gate compare two different cap rules and report a mirror divergence — the wrong diagnosis for the right symptom. Rationale is recorded at the site in `test_pipeline_mirrors.py`'s `RECORDED_FIELDS`.

- [ ] **Step 1: Flip all three in one commit**, each with its comment updated to cite this adoption (the `graph_path` comment's "flipped at each adoption" rule is the pattern; closeout checks defaults were actually flipped). `w_known_ramp_fame_pctl: float = 0.01` cites `P1a` and `cre_common.py`'s `RAMPS` as the adopted value's source.
- [ ] **Step 2: Run both suites** (`builder/`, `api/`) and `npm test`. The api default-graph test pins the new name.
- [ ] **Step 3: Record the override.** Execution-log section, three sentences fixed here: *This adoption overrides the `GBL-` null (margin 3 vs bar 5; pre-registered consequence "production stands"). The owner took it knowingly on 2026-08-05, on `CAU-`'s coherence pass at his bar and the un-listenable filter fix, which make the deployed package a new candidate under the run-once rule. Neither `GBL-` nor `CAU-` licensed it; his authority did.* The PR body carries the same paragraph.
- [ ] **Step 4: Snyk scan** (global instruction): `snyk_code_scan` over the new/modified first-party code (`builder/src`, `api/src`); fix and rescan until clean; record the outcome in the log.
- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/config.py builder/src/artistpath_builder/config.py api/tests/test_config.py docs/superpowers/2026-08-05-msw-execution-log.md
git commit -m "MSW- ADOPTION: default graph -> graph-msw-tu50.bin, ramp 0.01 (P1a), cap_strategy trimmed_union; GBL- override recorded"
```

---

### Task 12: Deploy, queue the hand test, close out

**Files:**
- Operational (deploy per `infra/README.md`); Modify: `docs/superpowers/TEST-QUEUE.md` (one QUEUED entry — there is something to press)

- [ ] **Step 1: Upload artifact + sidecar to S3** per `infra/README.md:259-269` (the `aws s3 cp` pair, then the `head-object` size check against the sidecar). Mind the deploy-environment traps (`memory/deploy-environment-traps.md`): Git Bash vs WSL PATHs, MSYS path rewriting.
- [ ] **Step 2: Deploy** with `ARTISTPATH_DEPLOY_GRAPH_KEY=graph-msw-tu50.bin` and `ARTISTPATH_DEPLOY_SIDECAR=../builder/scratch/graph-msw-tu50.bin.json` (`infra/README.md:52-53`); `app.py` reads the sha from the sidecar (never set it by hand, `infra/README.md:97`). **Not** `-c stage=storage` — the full stage (`deploy_stage.py`'s guard exists because the storage stage deletes the CloudFront distribution).
- [ ] **Step 3: Verify live** per `infra/README.md:515-533`: `/health` must report the new sha, artist count, and edge count matching the sidecar.
- [ ] **Step 4: Queue the owner's hand test** in `TEST-QUEUE.md`: the new map is live; press "know them already" repeatedly on a favourite pair and see whether later presses dig deeper than earlier ones; report any dead card (an artist with nothing to play) — that class was filtered and one appearing is a finding.
- [ ] **Step 5: Run `closeout`** (the full ritual — this is significant work landing). It owns the `NEXT.md` rewrite, the doc-map rows, D6, and PR finalisation. Merge via the PR.

---

## Self-review record

- **Spec coverage:** `ULC-A4`'s three ingredients → Tasks 2 (rule), 8-9 (data), 7+11 (ramp); filter-on → default already shipped, verified in 10; owner's "deploy, live with it" → 11-12 with the override recorded; the promised exposure re-measure → `MSW-V2`; the `CAU-` nine-artist check promised in conversation → `MSW-V1`.
- **Placeholder scan:** clean — every step carries its content or names the exact file/line it adapts. Two deliberate adapt-points (fixture names in Tasks 2/6/7, CLI flag in 9) name the file and line to copy from, which is instruction, not placeholder.
- **Type consistency:** `trimmed_union_cap(adjacency, top_j, degree_ceiling, *, ranking)` consistent across Tasks 1/2; `fame_lb_raw: list[int | None]` across 4/5; `fame_lb_pctl: np.ndarray | None` across 6/7; knob name `w_known_ramp_fame_pctl` across 7/10/11.
- **Claims-vs-repo:** every named file:line was read this session (`config.py:81/192/202`, `pipeline.py:32/117/352`, `artifact.py:35-57`, `graph.py:21-39/58/75`, `graph_store.py:41/176/183`, `pathfinding.py:103-137`, `config.py:20-54` api, `cre_common.py:81`, `cre_mirror.py:268-345`, `cb_build_variants.py:163-256`, `archive.py:28-57`, `infra/README.md:52-269/515-533`, api `test_graph_store.py:18/97/119`).
