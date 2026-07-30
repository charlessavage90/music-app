# Graph Rebuild — Track A Implementation Plan (`GR`)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Role: ACTIVE.** Written 2026-07-29, cold from the committed record, per
[`../2026-07-29-HANDOFF-reciprocity.md`](../2026-07-29-HANDOFF-reciprocity.md) and
`NEXT.md`. Identifier series `GR-`, collision-checked against `docs/` (no prior use).

**Goal:** Make an `ALG-B` trial build *possible* and *run one*, so the two live deferrals it
gates — `RC-P2`'s predicted build refusal and `RC-H1`'s component-membership question — are
answered from a real build, and the owner's parked re-crawl decision has its full price
attached. Nothing is adopted; no production default changes.

**Architecture:** Three small builder changes (a standing drop rule in the pipeline, a CLI
algorithm override, algorithm-scoped archive keys), verified by a full rebuild from the
production archive, then one pre-registered experiment (capped `ALG-B` trial crawl into a
fresh archive + trial build read against the acceptance clauses and component structure).

**Tech Stack:** Python (`builder/` package only — `api/` and `frontend/` are untouched),
pytest, the existing `LocalArchive`/`Crawler`/`build_from_archive` pipeline.

## Global constraints

- **Nothing is adopted by this plan.** `BuilderConfig.algorithm` keeps its
  `contribution_5` default (flipping it *is* the re-crawl decision — `NEXT.md`, owner's);
  `ApiConfig.graph_path` is untouched; the adopted artifact remains
  `graph-t15-tiebreakfix.bin` (sha256 `4cb84ef9…`, authoritative record:
  `findings/2026-07-23-tiebreak-fix-adoption.md`).
- **The production archive is read-only for every task here.** It lives at
  `builder/scratch/graph-archive/` (75,000 responses). Any task that would write to it is
  mis-executing — the trial crawl writes to a fresh directory *and* to algorithm-scoped
  keys, belt and braces.
- **Do not weaken `check_acceptance` to unblock anything** (`acceptance.py` module
  docstring; `NEXT.md` "must not be changed"). GR-1 implements the drop; the tripwire
  stays.
- **`UV_LINK_MODE=copy` on every `uv` command; `cd builder` first.** Long jobs:
  `python -u` / `PYTHONUNBUFFERED=1` (a redirected job with a 0-byte log is running, not
  dead). `PYTHONIOENCODING=utf-8` on anything printing artist names.
- **No experimental arm runs before its pre-registration is committed** (GR-5 before GR-6;
  the commit timestamp is the evidence).
- **Per the global security instruction:** run `snyk_code_scan` over new/modified builder
  code after each code task (GR-1..GR-3), fix, rescan until clean, before that task's
  commit is considered done.
- **Figures:** this plan restates none. Scoring/path-quality figures live in
  `findings/2026-07-21-scoring-adjudication.md`; `RC`/`AS` measurement figures in
  `builder/analysis/2026-07-29-*/`; operational cost figures in the RC execution log §6.
- **Naming:** any new popularity- or degree-derived quantity names its currency in its
  identifier (`CLAUDE.md`). No task here should need one; a task that finds it does stops
  and says so.

## Whose decisions bound this plan

| Owner's (not taken here) | This plan's (taken, with reasoning shown) |
|---|---|
| The `ALG-B` **re-crawl** itself (4¼ h, new archive, retires path-quality figures) — PARKED in `NEXT.md` | Running a **capped trial crawl** into a scratch archive: methodology/run-count territory, ~1–2 h of machine time, nothing user-facing, nothing adopted. Named here so the spend is visible before execution. |
| Adoption of anything; any blind listen (`REQ-38`) | Task order, instruments, harness design, pre-registration contents |
| Re-reading Track 3's verdict under `PRODUCT-REQUIREMENTS.md` §10 | Which acceptance clauses the trial build reads (they are `RC-P2`'s two, fixed by the record) |

Why the trial crawl is this plan's call and not the parked re-crawl: `NEXT.md` itself
defers `RC-P2` to "the first `ALG-B` trial build" and keeps the capped crawl alive as "the
only way to reach component membership (`RC-H1`)". The parked item is the *production*
re-crawl — the one that writes the archive the app would be rebuilt from. If the owner
reads this differently, GR-5/GR-6 wait; GR-1–GR-4 are due regardless (the drop rule gates
*any* rebuild).

## Strand order — why this is not the pre-2026-07-29 order restored

The handoff's four strands: algorithm selection (**done**, AS) → `AS-H2` stranding
(**answered** on the connection-count half, RC; `RC-H1` residual) → cap selection under
`MKS-5b` → nameless-artist drop rule. This plan covers the **residual of strand 2**
(`RC-H1`, needs a real build) plus **strand 4 pulled forward** — the handoff's own
instruction: the drop rule is "the plan's first build blocker, not a late item", because
`check_acceptance` refuses any rebuild until it lands. **Strand 3 (cap-selection
simulation) is deliberately behind the seam at the end of this plan**: `RC-A2` shows the
cap and the algorithm *interact* (four top-0.1% artists sit at rank 50–97 in their own
candidates' lists under `ALG-B`), so designing the simulation before the trial build's
structure exists would bake the unknown in. Its design must consume `RC-A2` and the stored
full candidate lists (`rc_raw_records.json` re-scored at different `k`, no re-fetching) —
recorded in `NEXT.md`'s deferral table, not re-planned here.

## Factor table (and what each comparison is barred from)

| build | source algorithm | crawl coverage | drop rule (GR-1) | isolating baseline |
|---|---|---|---|---|
| adopted `graph-t15-tiebreakfix.bin` | ALG-E | full 75k | absent | — |
| **GR-4** verification rebuild | ALG-E | full 75k (same archive) | present | adopted artifact — differs by exactly one column |
| **GR-6** ALG-E control build | ALG-E | capped N | present | GR-4 — differs by exactly one column (coverage) |
| **GR-6** ALG-B trial build | ALG-B | capped N | present | the ALG-E control — differs by exactly one column (algorithm) |

- **GR-4 vs adopted** supports: "what does the drop rule alone change" (node/edge deltas).
- **ALG-B trial vs adopted or vs GR-4** is **barred** from any quantitative claim — two
  columns differ (algorithm *and* coverage). This is why the RC track existed; do not
  re-derive stranding rates from the trial build against production.
- **ALG-B trial vs ALG-E control** supports algorithm-knob claims *at matched coverage* —
  and the control arm is nearly **free**: every ALG-E response for any reachable artist is
  already in the production archive, so `_archive_or_fetch` serves it without a network
  call. (The two arms' BFS frontiers still differ — the neighbour lists differ — so
  "matched coverage" means matched *target and procedure*, not identical artist sets;
  GR-5 must state which reads that limits.)

**Held constant, and why each is genuinely constant under the intervention:**

- `max_neighbours_per_artist=50` and the mutual-k-NN rule: no task touches `graph.py` or
  the cap call; `MKS-5b` bars changing them without a simulated bound, and nothing here
  turns on their value being right.
- `similarity_rescale="p99_log_clip"`, `similarity_damping=0.0`: untouched;
  `damping=0.0` also means GR-1's mass-marginal change is score-inert in production
  (`damped_strength` ignores mass at `d=0` — the p99 scale can still shift slightly
  because dropped edges leave the flat list; GR-4 records the resulting deltas).
- `check_acceptance` and `PRODUCTION_ACCEPTANCE`: no task edits them. **Not constant
  across arms by *effect*, deliberately:** the trial build is expected to fail global-shape
  bounds trivially (a capped graph cannot hit 60k–90k nodes), which is why GR-6 reads the
  two `RC-P2` clauses individually via a harness instead of running `cmd_build`.
- The blank-name check fires on the production archive **today** (33 nameless artists,
  measured at F8, `builder/analysis/2026-07-24-track2-p8b-harness-review/`) — it is *not*
  inert in any arm here: GR-1 lands before every build in this plan, so all built arms
  carry the drop rule. That is the dormant-term check: the drop rule cannot switch itself
  on in only the successful arms because it is on everywhere.

## Names this plan asserts about the repo (grep-verified at authoring, 2026-07-29)

`build_from_archive`, `harvest_identities`, `largest_component`, `check_acceptance`,
`PRODUCTION_ACCEPTANCE` (`famous_min_degree_floor=8`, `famous_sample=25`,
`canonical_names` incl. `"R.E.M."`), `ArtifactRejected`, `Crawler.similar_key`,
`Crawler._load_checkpoint`, `Crawler._save_checkpoint`, `cli._config`, `cmd_build`
(`getattr(args, "criteria", PRODUCTION_ACCEPTANCE)` — in-process criteria substitution is
the sanctioned route; there is deliberately no CLI escape hatch), `BuilderConfig.algorithm`
(frozen dataclass, default `contribution_5`), archive key shape
`similar/listenbrainz/{mbid}.json`, `builder/analysis/2026-07-29-reciprocity-sampling/rc_raw_records.json`.
Executor: re-grep anything you are about to modify; anything that no longer resolves means
the repo moved after authoring — stop and say so.

---

### Task GR-1: The nameless-artist drop rule

The owner's 2026-07-28 decision (drop, not backfill), recorded in `NEXT.md` and in
`acceptance.py`'s module docstring, whose success condition this task discharges half of
(GR-4 discharges the other half). A standing build rule: any future crawl can mint new
nameless nodes the same way.

**Files:**
- Modify: `builder/src/artistpath_builder/pipeline.py` (inside `build_from_archive`,
  immediately after the special-purpose filter block that ends `excluded = set()`)
- Test: `builder/tests/test_pipeline_dropnameless.py` (create)

**Interfaces:**
- Consumes: `harvest_identities` (mbid → `(name, disambiguation)`), the `known` set and
  `excluded` set already in scope at that point in `build_from_archive`.
- Produces: no signature changes. Behavioural contract for later tasks: **no graph emitted
  by `build_from_archive` contains a blank-named node**, and a node whose only edges led
  to dropped nodes falls out at the largest-component prune.

- [ ] **Step 1: Write the failing tests**

```python
# builder/tests/test_pipeline_dropnameless.py
"""The nameless-artist drop rule (owner decision 2026-07-28, NEXT.md; REQ-2).

A nameless artist is unsearchable, clipless, and renderable only as a blank
card, so `build_from_archive` drops it before the largest-component prune —
and a neighbour stranded by the drop is pruned rather than kept dangling.
"""

import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C, N, S = ("a" * 36, "b" * 36, "c" * 36, "d" * 36, "e" * 36)

# A <-> B <-> C is a healthy named core. N is nameless: every row that
# mentions it carries an empty name. S is a satellite whose only tie is to N.
SIMILAR = {
    A: [(B, "Beta", 10)],
    B: [(A, "Alpha", 10), (C, "Gamma", 5), (N, "", 4)],
    C: [(B, "Beta", 5)],
    N: [(B, "Beta", 4), (S, "Sigma", 6)],
    S: [(N, "", 6)],
}


def _similar_body(mbid: str) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": n, "name": name, "comment": "", "score": score}
            for n, name, score in SIMILAR[mbid]
        ]
    ).encode()


@pytest.fixture
def archive(tmp_path):
    source = ListenBrainzSource(BuilderConfig())
    archive = LocalArchive(tmp_path / "archive")
    for mbid in SIMILAR:
        archive.put(f"similar/{source.name}/{mbid}.json", _similar_body(mbid))
    return archive


def _build(archive):
    config = BuilderConfig()
    return build_from_archive(config, archive, ListenBrainzSource(config))


def test_nameless_artist_is_dropped(archive):
    assert N not in _build(archive).mbids


def test_stranded_neighbour_of_dropped_node_is_pruned_not_dangling(archive):
    # S's only edge is to N. With N dropped, S must fall out at the
    # largest-component prune — never survive as an edgeless node.
    graph = _build(archive)
    assert S not in graph.mbids
    assert sorted(graph.mbids) == sorted([A, B, C])


def test_every_emitted_artist_has_a_name(archive):
    assert all(name.strip() for name in _build(archive).names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run (from `builder/`): `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pipeline_dropnameless.py`
Expected: FAIL — `N` (and `S`) present in `graph.mbids`, blank name in `graph.names`.

- [ ] **Step 3: Implement the drop in `build_from_archive`**

Insert directly after the `if config.filter_special_purpose: … else: excluded = set()`
block (currently `pipeline.py:140-150`), before "Pass 1":

```python
    # Nameless artists are dropped, unconditionally (owner decision
    # 2026-07-28, recorded in NEXT.md; REQ-2). An artist whose name never
    # appears in any neighbour row is unsearchable, clipless, and renderable
    # only as a blank card. Dropped here, beside the placeholder entities and
    # before the mass computation, so it contributes to no marginal — and a
    # neighbour stranded by the drop falls out at the largest-component
    # prune rather than dangling.
    nameless = {
        mbid
        for mbid, (name, _disambiguation) in identities.items()
        if not name.strip()
    }
    # An artist with an archived response that never appears as anyone's
    # neighbour has no identity row at all: same defect, same fate.
    nameless |= known - identities.keys()
    if nameless & known:
        logger.info("dropped %d nameless artists", len(nameless & known))
    excluded |= nameless
    known -= nameless
```

No config knob: `REQ-2` is a Must and the acceptance check's zero is "the only defensible
count" — a switch to turn the rule off would be an escape hatch on that guard.

- [ ] **Step 4: Run the new tests, then the whole builder suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: new tests PASS; full suite green (baseline 2026-07-29: 115 passed — AS log §10).
Two existing behaviours must not regress: determinism (`test_replay.py` byte-identical
rebuild) and `test_uncrawled_neighbours_are_not_nodes`.

- [ ] **Step 5: Snyk scan, then commit**

Run `snyk_code_scan` over the diff; fix and rescan until clean.

```bash
git add builder/tests/test_pipeline_dropnameless.py builder/src/artistpath_builder/pipeline.py
git commit -m "GR-1: drop nameless artists during build, before the component prune"
```

---

### Task GR-2: `--algorithm` for trial runs, default untouched

**Files:**
- Modify: `builder/src/artistpath_builder/config.py` (module constants + the `algorithm`
  field default)
- Modify: `builder/src/artistpath_builder/cli.py` (`_config`, and the `crawl` / `build`
  subparsers)
- Test: `builder/tests/test_cli.py` (append), `builder/tests/test_config.py` (append)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `config.PRODUCTION_ALGORITHM: str` and `config.PERMITTED_ALGORITHMS:
  tuple[str, ...]` (GR-3 imports both); `artistpath-build crawl|build --algorithm <value>`
  threading into `BuilderConfig(algorithm=…)`.

- [ ] **Step 1: Write the failing tests**

Append to `builder/tests/test_config.py`:

```python
def test_default_algorithm_is_production():
    from artistpath_builder.config import PRODUCTION_ALGORITHM, BuilderConfig

    assert BuilderConfig().algorithm == PRODUCTION_ALGORITHM
    assert "contribution_5" in PRODUCTION_ALGORITHM


def test_permitted_algorithms_is_the_closed_enum_of_six():
    from artistpath_builder.config import PERMITTED_ALGORITHMS, PRODUCTION_ALGORITHM

    assert len(PERMITTED_ALGORITHMS) == 6
    assert PRODUCTION_ALGORITHM in PERMITTED_ALGORITHMS
    assert len(set(PERMITTED_ALGORITHMS)) == 6
```

Append to `builder/tests/test_cli.py`:

```python
import argparse

import pytest

from artistpath_builder.cli import _config
from artistpath_builder.config import PERMITTED_ALGORITHMS, PRODUCTION_ALGORITHM

ALG_B = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)


def test_config_threads_algorithm_override():
    args = argparse.Namespace(target=None, algorithm=ALG_B)
    assert _config(args).algorithm == ALG_B
    assert ALG_B in PERMITTED_ALGORITHMS


def test_config_rejects_a_value_outside_the_closed_enum():
    args = argparse.Namespace(target=None, algorithm="definitely_not_a_real_algorithm")
    with pytest.raises(SystemExit):
        _config(args)


def test_config_default_algorithm_is_production():
    assert _config(argparse.Namespace()).algorithm == PRODUCTION_ALGORITHM
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q -k "algorithm"`
Expected: FAIL with `ImportError: cannot import name 'PRODUCTION_ALGORITHM'`.

- [ ] **Step 3: Implement**

`config.py` — above `BuilderConfig`, and change the field to reference the constant:

```python
# The live endpoint's `algorithm` parameter is a CLOSED ENUM of exactly these
# six values — validated 2026-07-29 (CS-P0e; probes and 400s recorded in
# builder/analysis/2026-07-29-cap-selection-sim/cs_p0e_algorithms.json).
# Arm labels ALG-A..ALG-F are the AS pre-registration's. Do not add values:
# anything else returns HTTP 400.
PRODUCTION_ALGORITHM = (  # ALG-E — the adopted 75k archive's algorithm
    "session_based_days_7500_session_300_contribution_5"
    "_threshold_10_limit_100_filter_True_skip_30"
)
PERMITTED_ALGORITHMS = (
    PRODUCTION_ALGORITHM,
    # ALG-B — the named re-crawl candidate (AS log §7); differs from
    # production by contribution_3.
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30",
    # ALG-A
    "session_based_days_1825_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30",
    # ALG-F
    "session_based_days_1800_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30",
    # ALG-D
    "session_based_days_75_session_300_contribution_5"
    "_threshold_10_limit_100_filter_True_skip_30",
    # ALG-C
    "session_based_days_9000_session_300_contribution_5"
    "_threshold_15_limit_50_skip_30",
)
```

and in `BuilderConfig`:

```python
    algorithm: str = PRODUCTION_ALGORITHM
```

`cli.py` — replace `_config` (validation lives at the CLI boundary, not in
`BuilderConfig.__post_init__`: analysis harnesses construct configs directly and own their
own validation, and a frozen dataclass stays a dumb container):

```python
def _config(args) -> BuilderConfig:
    """Allow the discovery cap and the source algorithm to be overridden for
    trial runs. The DEFAULT stays the production algorithm: flipping the
    default is the re-crawl decision, which is the owner's (NEXT.md)."""
    overrides: dict = {}
    target = getattr(args, "target", None)
    if target:
        overrides["target_artist_count"] = target
    algorithm = getattr(args, "algorithm", None)
    if algorithm:
        if algorithm not in PERMITTED_ALGORITHMS:
            raise SystemExit(
                f"unknown algorithm {algorithm!r}: the endpoint accepts a "
                "closed enum of six values (CS-P0e) — see "
                "artistpath_builder.config.PERMITTED_ALGORITHMS"
            )
        overrides["algorithm"] = algorithm
    return BuilderConfig(**overrides)
```

Import `PERMITTED_ALGORITHMS` from `artistpath_builder.config` at the top of `cli.py`,
and add to **both** the `crawl` and `build` subparsers (build needs it because GR-3 keys
the archive *read* on it too):

```python
    p_crawl.add_argument(
        "--algorithm",
        default=None,
        help="source algorithm for trial runs; default is production's (ALG-E)",
    )
```

```python
    p_build.add_argument(
        "--algorithm",
        default=None,
        help="which algorithm's archive tree to build from; default production's",
    )
```

- [ ] **Step 4: Run the tests**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, full suite green.

- [ ] **Step 5: Snyk scan, then commit**

```bash
git add builder/src/artistpath_builder/config.py builder/src/artistpath_builder/cli.py builder/tests/test_cli.py builder/tests/test_config.py
git commit -m "GR-2: --algorithm override for trial runs; default stays production (ALG-E)"
```

---

### Task GR-3: Algorithm-scoped archive keys and a checkpoint guard (`RC-H3`)

The archive key `similar/listenbrainz/{mbid}.json` does not encode the algorithm, so a
re-crawl aimed at the existing archive would **silently return production data** — and the
checkpoint has the same hazard (a resumed crawl under a different algorithm would skip
every "done" artist). Both close here. The production archive keeps its flat layout: it
predates scoping, 75k files do not get moved, and its layout is part of how every existing
script finds it.

**Files:**
- Modify: `builder/src/artistpath_builder/crawl.py` (`similar_key`, `_load_checkpoint`,
  `_save_checkpoint`)
- Modify: `builder/src/artistpath_builder/pipeline.py` (prefix selection in
  `build_from_archive`)
- Test: `builder/tests/test_crawl.py` (append), `builder/tests/test_replay.py` (append)

**Interfaces:**
- Consumes: `PRODUCTION_ALGORITHM` from GR-2.
- Produces: key contract — production algorithm ⇒ `similar/{source}/{mbid}.json` (flat,
  unchanged); any other algorithm ⇒ `similar/{source}/{algorithm}/{mbid}.json`. Checkpoint
  JSON gains an `"algorithm"` field; a missing field means the production algorithm
  (every existing checkpoint predates this change). GR-6's harness relies on both.

- [ ] **Step 1: Write the failing tests**

Append to `builder/tests/test_crawl.py` (reuse that file's existing fixture style for
constructing a `Crawler`; the fragments below show the assertions that matter):

```python
from artistpath_builder.config import BuilderConfig, PRODUCTION_ALGORITHM

ALG_B = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)
MBID = "a" * 36


def _crawler(tmp_path, config):
    from artistpath_builder.archive import LocalArchive
    from artistpath_builder.crawl import Crawler
    from artistpath_builder.sources.listenbrainz import ListenBrainzSource

    return Crawler(
        config=config,
        archive=LocalArchive(tmp_path / "archive"),
        source=ListenBrainzSource(config),
        fetcher=lambda url: b"[]",
        checkpoint_path=tmp_path / "checkpoint.json",
    )


def test_production_algorithm_keeps_the_flat_archive_key(tmp_path):
    crawler = _crawler(tmp_path, BuilderConfig())
    assert crawler.similar_key(MBID) == f"similar/listenbrainz/{MBID}.json"


def test_nondefault_algorithm_gets_its_own_archive_subtree(tmp_path):
    crawler = _crawler(tmp_path, BuilderConfig(algorithm=ALG_B))
    assert crawler.similar_key(MBID) == f"similar/listenbrainz/{ALG_B}/{MBID}.json"


def test_checkpoint_refuses_to_resume_under_a_different_algorithm(tmp_path):
    import pytest

    _crawler(tmp_path, BuilderConfig()).crawl([MBID])  # writes a checkpoint
    with pytest.raises(ValueError, match="RC-H3"):
        _crawler(tmp_path, BuilderConfig(algorithm=ALG_B))


def test_legacy_checkpoint_without_algorithm_field_still_resumes(tmp_path):
    import json

    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [], "discovered": []})
    )
    _crawler(tmp_path, BuilderConfig())  # must not raise
```

Append to `builder/tests/test_replay.py`:

```python
ALG_B = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)


def test_build_reads_only_its_own_algorithms_subtree(tmp_path):
    # The same mbid holds DIFFERENT payloads flat (production) and scoped
    # (ALG-B). Each build must see only its own; the flat build must not
    # sweep the sub-tree in through the shared prefix.
    flat_config = BuilderConfig(requests_per_second=1000.0)
    algb_config = BuilderConfig(requests_per_second=1000.0, algorithm=ALG_B)
    source = ListenBrainzSource(flat_config)
    archive = LocalArchive(tmp_path / "archive")
    _seed_archive(archive, source, [A, B, C])  # flat: A<->B<->C
    # ALG-B tree: only A and B, and A's list omits C entirely.
    for mbid in (A, B):
        archive.put(f"similar/{source.name}/{ALG_B}/{mbid}.json", _similar_body(mbid))

    flat_graph = build_from_archive(flat_config, archive, source)
    algb_graph = build_from_archive(algb_config, archive, ListenBrainzSource(algb_config))

    assert sorted(flat_graph.mbids) == sorted([A, B, C])
    assert C not in algb_graph.mbids  # C was never crawled under ALG-B
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q -k "algorithm or checkpoint or subtree"`
Expected: FAIL — scoped key not produced, no `ValueError`, flat build sweeps the sub-tree.

- [ ] **Step 3: Implement**

`crawl.py` — import `PRODUCTION_ALGORITHM`; replace `similar_key`:

```python
    def similar_key(self, mbid: str) -> str:
        # The production archive predates algorithm-scoped keys and keeps its
        # flat layout. Every other algorithm gets its own sub-tree, so two
        # algorithms' responses can never be mistaken for one another (RC-H3).
        if self.config.algorithm == PRODUCTION_ALGORITHM:
            return f"similar/{self.source.name}/{mbid}.json"
        return f"similar/{self.source.name}/{self.config.algorithm}/{mbid}.json"
```

`_save_checkpoint` — add the field to the JSON payload:

```python
        self.checkpoint_path.write_text(
            json.dumps(
                {
                    "algorithm": self.config.algorithm,
                    "done": sorted(self._done),
                    "discovered": sorted(self.discovered),
                },
                sort_keys=True,
            )
        )
```

`_load_checkpoint` — guard before returning:

```python
        state = json.loads(self.checkpoint_path.read_text())
        stored = state.get("algorithm", PRODUCTION_ALGORITHM)
        if stored != self.config.algorithm:
            raise ValueError(
                f"checkpoint {self.checkpoint_path} was written by a crawl "
                f"under {stored!r}; refusing to resume it under "
                f"{self.config.algorithm!r} (RC-H3 — a resumed crawl would "
                "silently skip every artist the other algorithm finished)"
            )
```

`pipeline.py` — replace the prefix block at the top of `build_from_archive`:

```python
    if config.algorithm == PRODUCTION_ALGORITHM:
        prefix = f"similar/{source.name}/"
    else:
        prefix = f"similar/{source.name}/{config.algorithm}/"
    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix) : -len(".json")]
        if "/" in mbid:
            # A scoped sub-tree nested under the flat production layout —
            # another algorithm's data, never this build's (RC-H3).
            continue
        payload = archive.get(key)
        if payload is not None:
            payloads[mbid] = payload
```

(import `PRODUCTION_ALGORITHM` in `pipeline.py` as well.)

- [ ] **Step 4: Run the full builder suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS. `test_replay.py`'s byte-identical test is the regression sentinel — the
flat path must be byte-for-byte what it was.

- [ ] **Step 5: Snyk scan, then commit**

```bash
git add builder/src/artistpath_builder/crawl.py builder/src/artistpath_builder/pipeline.py builder/tests/test_crawl.py builder/tests/test_replay.py
git commit -m "GR-3: algorithm-scoped archive keys and checkpoint guard (RC-H3)"
```

---

### Task GR-4: Verification rebuild from the production archive

Discharges the second half of the drop-rule success condition ("this check then passes on
a rebuild") and regression-checks GR-3's flat-path read against the real archive. **The
output is a verification artifact, not an adoption**: it goes to `builder/scratch/`, is
gitignored, and nothing points the API at it.

**Files:**
- Create: `builder/scratch/graph-dropnameless-verify.bin` (+ its `.json` manifest sidecar,
  written automatically) — gitignored, recorded by checksum in the execution log only.
- Modify: the retained execution log for this track (append the deltas).

**Interfaces:**
- Consumes: GR-1 (the drop), GR-3 (the flat prefix path).
- Produces: the recorded node/edge/dropped-count deltas GR-5 cites, and the evidence line
  that closes `acceptance.py`'s deferral.

**Gate `GR-G1`** — plain sentence, fixed now: *"a rebuild of today's map from today's
data, with the blank-name artists dropped, is accepted by the build's own safety
checks."* Effect size: **binary — any refusal at all is a failure**, because zero nameless
artists is the only defensible count (`acceptance.py`) and every other clause held on this
same archive before. On failure: do not weaken any check; read the refusal text, fix the
defect, re-run. A failure here is a GR-1 defect by construction.

- [ ] **Step 1: Confirm the baseline refusal (the tripwire fires today)**

From `builder/`:

```bash
UV_LINK_MODE=copy uv run artistpath-build build --archive-dir ./scratch/graph-archive --out ./scratch/graph-dropnameless-verify.bin
```

Run this on the commit **before** GR-1 (`git stash` the working tree or run it first,
before GR-1 merges) — expected: `ArtifactRejected` naming N artist(s) with no name. If it
*passes* pre-GR-1, stop: the record (33 nameless, F8) no longer matches the archive, and
that needs saying before anything else. *(If executing tasks strictly in order, run this
step at the start of GR-1 instead and record the refusal text then.)*

- [ ] **Step 2: Run the rebuild with GR-1..GR-3 in place**

Same command. Expected: completes in ~2 minutes, logs `dropped 33 nameless artists`,
`check_acceptance` passes, artifact + manifest written.

- [ ] **Step 3: Record the deltas**

Against the adopted artifact (74,193 artists / 898,006 edges — RC log §7): record new node
count, edge count, dropped count, and sha256 from the manifest sidecar (never transcribed
by hand) in the execution log. Expected shape: nodes down by 33 plus any pruned
satellites; edge count may move slightly in **either** direction — removing a nameless
artist from a top-50 list promotes the 51st candidate into the mutual-k-NN cap, so new
edges can appear. Explain any delta that does not fit that shape rather than filing it.

- [ ] **Step 4: Commit the log entry**

```bash
git add docs/superpowers/2026-07-29-graph-rebuild-track-a-execution-log.md
git commit -m "GR-4: production-archive rebuild passes acceptance with the drop rule in place"
```

(The `.bin` and its sidecar are gitignored and stay in `scratch/`.)

---

### Task GR-5: The trial-build pre-registration (document; committed before any arm runs)

The experiment itself. This task writes and commits
`docs/superpowers/specs/2026-07-29-algb-trial-build-preregistration.md` — GR-6 executes
it. The plan constrains the design; it deliberately does **not** fix thresholds here,
because fixing them is the pre-registration's job and doing it twice creates two copies.

**Files:**
- Create: `docs/superpowers/specs/2026-07-29-algb-trial-build-preregistration.md`

**Interfaces:**
- Consumes: GR-2's `--algorithm`, GR-3's key contract, GR-4's recorded deltas.
- Produces: the committed document GR-6 executes; its identifier series (namespaced,
  collision-checked — `GRT-` is suggested, check it before use).

**The document must contain, each per the named standing rule:**

- [ ] **Step 1: Draft with this checklist, every item present**

1. **Factor table** with the four builds from this plan's table, plus a **held-constant
   section** listing every fixed term and why the intervention cannot un-fix it
   (`CLAUDE.md` "Writing and reviewing plans here" — both sub-rules).
2. **Two arms:** capped `ALG-B` crawl (fresh archive directory, scoped keys, own
   checkpoint) and the **coverage-matched `ALG-E` control** (same target, fresh checkpoint,
   archive dir *may* be the production archive read-only? **No** — point it at a fresh
   directory too; ALG-E responses will be fetched only for artists outside the production
   75k, which should be ~none, so it stays near-free while keeping the production archive
   untouched by any crawl process. State the observed fetch count; if it is not ~0, say
   so — it means ALG-E's frontier left the production crawl's coverage, which is itself a
   finding). *(Correction while drafting: `_archive_or_fetch` reads the configured archive
   — a fresh dir means ALG-E responses are re-fetched, N requests, not free. Either accept
   that cost or run the control against the production archive with the crawl process
   proven write-free for it — every key already exists, `put` is only reached on a fetch.
   The pre-registration picks one and says why; do not leave both alive.)*
3. **Target choice with its cost derivation** from RC log §6's per-request figures,
   re-measured at execution day (the endpoint's speed moved 6× between measurements) —
   and the readable-core discipline from
   `builder/analysis/2026-07-29-trial-crawl-calibration/`: which artists' degrees are
   decided by data vs by where the crawl stopped, stated **per read**.
4. **The `RC-P2` read**: does the ALG-B build fail `famous_min_degree_floor` (8, over the
   top 25 by popularity) and/or lose any of the 24 `canonical_names` — R.E.M. is the named
   prediction — from the largest component, **evaluated conditional on readability** (a
   floor failure on an artist whose candidate lists were not all fetched is a coverage
   artifact, not a confirmation). Read via a committed harness calling
   `build_from_archive` + per-clause checks, never `cmd_build` (global-shape bounds fail
   trivially on a capped build, and the CLI has no criteria escape hatch by design).
5. **The `RC-H1` read**: component membership under ALG-B — within-arm and against the
   ALG-E control, with the coverage caveat stated in the read itself.
6. **Every gate and branch trigger carries its own effect size** — or the explicit
   sentence that any difference is decisive, and why. (The Track 2 A0-vs-P lesson.)
7. **Every read names the run state it presupposes**; any instruction keeping a run alive
   gets its own sentence, never a subordinate clause. (The stage-2 lesson.)
8. **Stratum-aware reads** where fame bands are involved (`AS-H1`'s discharge condition —
   this is a successor algorithm pre-registration, so it is bound by it).
9. **A plain-language sentence beside every criterion, arm, and branch, fixed before any
   result exists** — the "could the owner disagree with this?" standard.
10. **What is barred:** any quantitative ALG-B-vs-production-artifact comparison (two-knob
    confound, per this plan's factor table); any `k` change (`MKS-5b` — strand 3's
    territory); any adoption language.
11. **Run hygiene:** `PYTHONUNBUFFERED=1`/`python -u` on the crawl, fresh checkpoint
    paths, zero writes into `builder/scratch/graph-archive/` asserted after the run
    (**gate `GR-G2`**, plain sentence fixed now: *"the irreplaceable production archive
    contains exactly as many files after the trial as before"* — binary, any write is a
    failure because the archive cannot be re-gathered).

- [ ] **Step 2: Check every function/file/config value the document names resolves**

Grep each named symbol (the GR-2/GR-3 interfaces above). Anything unresolved is stale or
not-yet-built — fix before committing.

- [ ] **Step 3: Commit — before any collection code runs**

```bash
git add docs/superpowers/specs/2026-07-29-algb-trial-build-preregistration.md
git commit -m "GR-5: pre-registration for the ALG-B trial build, committed before any arm runs"
```

---

### Task GR-6: Execute the trial build per the pre-registration

**Files:**
- Create: `builder/analysis/2026-07-29-algb-trial-build/` — runner + scorer harness,
  **committed before any result exists** (the RC/AS pattern), then results JSON.
- Create (gitignored, in `builder/scratch/`): the two trial archives, checkpoints, and
  built trial graphs.
- Modify: the execution log (per-task append, not only at closeout).

**Interfaces:**
- Consumes: everything above; the committed GR-5 document governs — where this plan and
  it disagree, **it** governs, because it is the fresher, finer-grained design.
- Produces: the answered `RC-P2` and `RC-H1` deferrals; the figures for the owner's
  re-crawl decision package.

- [ ] **Step 1: Write and commit the harness (runner + scorer) before running anything**
- [ ] **Step 2: Run the ALG-B trial crawl** (background, unbuffered, fresh archive dir +
  checkpoint; budget from the pre-registration)
- [ ] **Step 3: Run the ALG-E control arm** per the pre-registration's chosen design
- [ ] **Step 4: Build both trial graphs via the harness; run the pre-registered reads**
- [ ] **Step 5: Assert `GR-G2`** (production archive file count unchanged) **and record
  every gate outcome, fired or not, with its figure**
- [ ] **Step 6: Append results to the execution log and commit**

```bash
git add builder/analysis/2026-07-29-algb-trial-build/ docs/superpowers/2026-07-29-graph-rebuild-track-a-execution-log.md
git commit -m "GR-6: ALG-B trial build executed and read against the pre-registration"
```

**Presentation of results follows `CLAUDE.md` "How to present results to the owner"**:
Measured / inferred-in-plain-language / weakest link / options — the summary must carry
both halves of the ALG-B record (what it delivers at the famous end *and* what it strands
at the obscure end; "no summary may keep one half without the other" — `NEXT.md`), and
every identifier gets its fixed plain sentence.

---

## After GR-6: the seam (planned here, at authoring time)

**This plan ends at GR-6. Retire the session at that point**: run `closeout` (execution
log distilled, deferral conditions updated in `NEXT.md`, test queue entry, PR finalised),
write the handoff. Six tasks is inside the 8-task ceiling; the next body of work is a
different design problem with new inputs, which is exactly what a fresh session reads
cold:

- **Track B — the cap-selection simulation** (strand 3, still owed under `MKS-5b`): its
  own plan, written by a session that reads GR-6's results, `RC-A2`, `CS-P0f`, and
  re-scores `rc_raw_records.json` at candidate `k` values without re-fetching. It must
  answer Phase 1 log §2.10's coupling before proposing any rule, per `MKS-5b`.
- **The owner's decision package** — whether to run the full `ALG-B` re-crawl — assembled
  from: AS (the lift), RC (the stranding price, both readings), GR-4 (drop-rule deltas),
  GR-6 (build refusal confirmed/refuted + component membership), Track B's bound. The
  decision itself, the re-crawl, and the blind listen stay **PARKED** exactly as
  `NEXT.md` has them.

## Self-review (run at authoring)

- **Spec coverage:** handoff item 1 (drop rule first, gates first build) → GR-1 + GR-4;
  handoff item 2 (cap/algorithm interaction) → strand-order section + Track B seam;
  `RC-P2` → GR-5.4/GR-6; `RC-H1` → GR-5.5/GR-6; `RC-H3` → GR-3; "no way to select the
  algorithm" → GR-2; `AS-H1` discharge condition → GR-5.8. No gap found.
- **Placeholder scan:** GR-5/GR-6 deliberately defer thresholds and harness code to the
  pre-registration — that is the pre-registration discipline, not a placeholder: fixing
  thresholds twice (plan and pre-reg) is the two-copies drift this repo documents. All
  code tasks carry real code.
- **Type consistency:** `PRODUCTION_ALGORITHM` / `PERMITTED_ALGORITHMS` names match
  between GR-2's definition and GR-3's imports and tests; `similar_key` contract matches
  the pipeline prefix rule; checkpoint field name `"algorithm"` consistent between save,
  load, and tests.
- **Known weakest link:** the GR-5 control-arm design has two live options (fresh dir with
  re-fetch cost vs read-only production archive) — flagged inline as a decision the
  pre-registration must close, not left implicit.
