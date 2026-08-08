# Crawl Extension (`CEX-`) Implementation Plan

**Role: ACTIVE operational plan for the `CEX-` track. NOT YET EXECUTED — do not mark tasks
done without doing them.** The governing document is
[`specs/2026-08-07-crawl-extension-design.md`](../specs/2026-08-07-crawl-extension-design.md)
and **it governs where the two disagree**. Status lives in [`NEXT.md`](../NEXT.md), never here.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the crawl extendable — it currently exits `0 processed` and reads as success — then extend it from 75,000 to 117,302 artists.

**Architecture:** A new `frontier.py` reconstructs the lost frontier from the archive (every archived response lists its neighbours), exposed as `artistpath-build refrontier`. `crawl.py`'s loop moves its bound from *artists discovered* to *artists fetched*, so the frontier is never discarded again, and gains a refusal so the failure stops being silent. Then the operational sequence: snapshot, crawl, fame, re-census, build.

**Tech Stack:** Python 3.12, `uv`, pytest. No new dependencies.

**Governing spec:** [`docs/superpowers/specs/2026-08-07-crawl-extension-design.md`](../specs/2026-08-07-crawl-extension-design.md) (revised 2026-08-08 — **read its §10 amendment log**). Review of record: `builder/analysis/2026-08-07-cex-frontier/2026-08-07-cex-design-review.md`.

## Global Constraints

- **Every `uv` command is prefixed `UV_LINK_MODE=copy`.** Run from `builder/`.
- **`PYTHONIOENCODING=utf-8` on anything printing artist names**; `python -u` on any long job.
- **The algorithm is ALG-B** (`CANDIDATE_ALGORITHM`, `contribution_3`) — **the adopted map's lineage**. `BuilderConfig.algorithm` still defaults to **ALG-E**, so **every** operational command passes `--algorithm` explicitly. Never flip the default; that is the owner's decision (`config.py:56-58`).
- **Do not widen `check_acceptance`'s bounds.** It will reject the extended build on **both** node and edge bounds. That is an owner stop (`acceptance.py:139`).
- **Determinism is required** (spec §9): every ordering decision explicit, sorted iteration everywhere.
- **Never write to the archive from a probe.** Use a read-only overlay implementing the `RawArchive` protocol.
- **Branch:** `crawl-extension-design` (already open). Push after every task.

---

### Task 1: `reconstruct_referenced` — rebuild the frontier from the archive

**Files:**
- Create: `builder/src/artistpath_builder/frontier.py`
- Test: `builder/tests/test_frontier.py`

**Interfaces:**
- Consumes: `similar_prefix(config, source)` from `pipeline.py`; `SimilaritySource.parse(payload, exclude_mbid=...)`.
- Produces: `reconstruct_referenced(archive: RawArchive, config: BuilderConfig, source: SimilaritySource) -> set[str]` — every MBID named as a neighbour by any archived response under this algorithm's prefix.

- [ ] **Step 1: Write the failing tests**

```python
# builder/tests/test_frontier.py
import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig
from artistpath_builder.frontier import reconstruct_referenced
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C, D = ("a" * 36, "b" * 36, "c" * 36, "d" * 36)


def _similar(*mbids: str) -> bytes:
    rows = [
        {"artist_mbid": m, "name": m[0].upper(), "score": 100 - i}
        for i, m in enumerate(mbids)
    ]
    return json.dumps(rows).encode()


@pytest.fixture
def config():
    return BuilderConfig(algorithm=CANDIDATE_ALGORITHM)


def _archive(tmp_path, config, entries):
    archive = LocalArchive(tmp_path / "archive")
    prefix = f"similar/listenbrainz/{config.algorithm}/"
    for mbid, payload in entries.items():
        archive.put(f"{prefix}{mbid}.json", payload)
    return archive


def test_referenced_is_the_union_of_every_neighbour(tmp_path, config):
    archive = _archive(tmp_path, config, {A: _similar(B, C), B: _similar(C, D)})
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {
        B,
        C,
        D,
    }


def test_other_algorithms_subtree_is_ignored(tmp_path, config):
    # CEXR-7a: a naive archive.keys() walk ingests another algorithm's data.
    archive = _archive(tmp_path, config, {A: _similar(B)})
    archive.put("similar/listenbrainz/some_other_algorithm/xx.json", _similar(D))
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {B}


def test_fame_keys_are_ignored(tmp_path, config):
    # CEXR-7a: fame records live in the same archive under fame/.
    archive = _archive(tmp_path, config, {A: _similar(B)})
    archive.put(f"fame/{C}.json", json.dumps({"total_user_count": 5}).encode())
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {B}


def test_unparseable_payload_is_skipped_not_fatal(tmp_path, config):
    archive = _archive(tmp_path, config, {A: _similar(B), C: b"{not json"})
    assert reconstruct_referenced(archive, config, ListenBrainzSource(config)) == {B}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_frontier.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'artistpath_builder.frontier'`

- [ ] **Step 3: Write the implementation**

```python
# builder/src/artistpath_builder/frontier.py
"""Reconstruct the crawl frontier the checkpoint never recorded (ULC-F3).

`crawl.py` used to stop RECORDING neighbours once discovery reached the target,
so the frontier beyond it was lost and a resume rebuilt an empty queue. The
frontier is recoverable offline: every archived response lists its neighbours.

Enumeration goes through `pipeline.similar_prefix` — the same definition `fame`
and `build` use — rather than a private walk. A second copy of that rule is the
divergence class `test_pipeline_mirrors.py` exists to guard.
"""

from __future__ import annotations

import logging

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import similar_prefix
from artistpath_builder.sources.base import SimilaritySource

logger = logging.getLogger(__name__)


def reconstruct_referenced(
    archive: RawArchive,
    config: BuilderConfig,
    source: SimilaritySource,
) -> set[str]:
    """Every MBID named as a neighbour by any archived response.

    Sorted iteration: the result is a set, but a deterministic read order keeps
    logging and any future short-circuit reproducible (spec section 9).
    """
    prefix = similar_prefix(config, source)
    referenced: set[str] = set()
    scanned = 0
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix) : -len(".json")]
        if "/" in mbid:
            # A scoped sub-tree nested under the flat production layout —
            # another algorithm's data, never this reconstruction's.
            continue
        payload = archive.get(key)
        if payload is None:
            continue
        try:
            referenced.update(
                neighbour.mbid for neighbour in source.parse(payload, exclude_mbid=mbid)
            )
        except ValueError:
            logger.warning("unparseable similarity payload for %s", mbid)
            continue
        scanned += 1
    logger.info("scanned %d responses, %d distinct mbids referenced", scanned, len(referenced))
    return referenced
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_frontier.py`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/frontier.py builder/tests/test_frontier.py
git commit -m "CEX-1: reconstruct the frontier from the archive"
git push
```

---

### Task 2: `rewrite_checkpoint` — union, never replace

**Files:**
- Modify: `builder/src/artistpath_builder/frontier.py`
- Modify: `builder/tests/test_frontier.py`

**Interfaces:**
- Consumes: `reconstruct_referenced` from Task 1.
- Produces: `rewrite_checkpoint(checkpoint_path: Path, config: BuilderConfig, referenced: set[str]) -> dict[str, int]` returning `{"done": int, "discovered": int, "frontier": int}`.

**Why union, not replace (`CEXR-7b`):** `crawl.py:115` computes `discovered - done`, so `discovered ⊇ done` is load-bearing. The real archive contains **8 artists that were crawled but appear in no response's neighbour list**. A replacing rewrite drops them and breaks the invariant — **while still reporting the correct frontier size**, because those 8 are in `done` and excluded from the difference either way.

- [ ] **Step 1: Write the failing tests**

```python
# append to builder/tests/test_frontier.py
import json
from pathlib import Path

from artistpath_builder.config import PRODUCTION_ALGORITHM
from artistpath_builder.frontier import rewrite_checkpoint


def _checkpoint(tmp_path, algorithm, done, discovered) -> Path:
    path = tmp_path / "checkpoint.json"
    path.write_text(
        json.dumps(
            {"algorithm": algorithm, "done": sorted(done), "discovered": sorted(discovered)},
            sort_keys=True,
        )
    )
    return path


def test_rewrite_unions_and_preserves_done_as_a_subset(tmp_path, config):
    # A crawled artist nobody names must survive the rewrite.
    path = _checkpoint(tmp_path, config.algorithm, done={A, D}, discovered={A, D})
    stats = rewrite_checkpoint(path, config, referenced={A, B, C})
    state = json.loads(path.read_text())
    assert set(state["done"]) <= set(state["discovered"])
    assert D in set(state["discovered"])
    assert stats == {"done": 2, "discovered": 4, "frontier": 2}


def test_rewrite_is_idempotent(tmp_path, config):
    path = _checkpoint(tmp_path, config.algorithm, done={A}, discovered={A})
    first = rewrite_checkpoint(path, config, referenced={A, B})
    after_first = path.read_text()
    second = rewrite_checkpoint(path, config, referenced={A, B})
    assert first == second
    assert path.read_text() == after_first


def test_rewrite_refuses_a_checkpoint_from_another_algorithm(tmp_path, config):
    path = _checkpoint(tmp_path, PRODUCTION_ALGORITHM, done={A}, discovered={A})
    with pytest.raises(ValueError, match="refusing"):
        rewrite_checkpoint(path, config, referenced={B})


def test_rewrite_backs_up_the_original_first(tmp_path, config):
    path = _checkpoint(tmp_path, config.algorithm, done={A}, discovered={A})
    original = path.read_text()
    rewrite_checkpoint(path, config, referenced={A, B})
    assert (tmp_path / "checkpoint.json.bak").read_text() == original
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_frontier.py -k rewrite`
Expected: FAIL — `ImportError: cannot import name 'rewrite_checkpoint'`

- [ ] **Step 3: Write the implementation**

```python
# append to builder/src/artistpath_builder/frontier.py
import json
from pathlib import Path

from artistpath_builder.config import PRODUCTION_ALGORITHM


def rewrite_checkpoint(
    checkpoint_path: Path,
    config: BuilderConfig,
    referenced: set[str],
) -> dict[str, int]:
    """Union `referenced` into the checkpoint's `discovered` set.

    UNION, never replace (CEXR-7b): `discovered` must stay a superset of `done`
    because `Crawler.crawl` rebuilds its queue as `discovered - done`. The real
    archive holds artists that were crawled but that no response names, and a
    replacing rewrite would drop them while still reporting the right frontier
    size — the reported number cannot catch this, so the invariant is asserted
    directly by test.

    Backs the original up first: the checkpoint is the only record of a
    completed crawl and there is no second copy.
    """
    state = json.loads(checkpoint_path.read_text())
    stored = state.get("algorithm", PRODUCTION_ALGORITHM)
    if stored != config.algorithm:
        raise ValueError(
            f"checkpoint {checkpoint_path} was written under {stored!r}; "
            f"refusing to rewrite it under {config.algorithm!r} (RC-H3)"
        )

    done = set(state.get("done", []))
    discovered = set(state.get("discovered", [])) | referenced | done

    backup = checkpoint_path.with_name(checkpoint_path.name + ".bak")
    backup.write_bytes(checkpoint_path.read_bytes())

    payload = json.dumps(
        {
            "algorithm": config.algorithm,
            "done": sorted(done),
            "discovered": sorted(discovered),
            "exhausted": bool(state.get("exhausted", False)),
        },
        sort_keys=True,
    )
    checkpoint_path.write_text(payload)
    return {
        "done": len(done),
        "discovered": len(discovered),
        "frontier": len(discovered - done),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_frontier.py`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/frontier.py builder/tests/test_frontier.py
git commit -m "CEX-1: union the reconstructed frontier into the checkpoint"
git push
```

---

### Task 3: `artistpath-build refrontier` CLI subcommand

**Files:**
- Modify: `builder/src/artistpath_builder/cli.py`
- Modify: `builder/tests/test_cli.py`

**Interfaces:**
- Consumes: `reconstruct_referenced`, `rewrite_checkpoint` from Tasks 1–2.
- Produces: CLI `artistpath-build refrontier --checkpoint PATH [--algorithm ALG] [--archive-dir DIR]`, exit 0, printing the three counts.

- [ ] **Step 1: Write the failing test**

```python
# append to builder/tests/test_cli.py
import json

from artistpath_builder.cli import main
from artistpath_builder.config import CANDIDATE_ALGORITHM

A, B = ("a" * 36, "b" * 36)


def test_refrontier_recovers_the_frontier_from_the_archive(tmp_path, capsys):
    prefix = f"similar/listenbrainz/{CANDIDATE_ALGORITHM}/"
    archive_dir = tmp_path / "archive"
    (archive_dir / prefix).mkdir(parents=True)
    (archive_dir / prefix / f"{A}.json").write_text(
        json.dumps([{"artist_mbid": B, "name": "B", "score": 90}])
    )
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text(
        json.dumps({"algorithm": CANDIDATE_ALGORITHM, "done": [A], "discovered": [A]})
    )

    exit_code = main(
        [
            "refrontier",
            "--checkpoint",
            str(checkpoint),
            "--archive-dir",
            str(archive_dir),
            "--algorithm",
            CANDIDATE_ALGORITHM,
        ]
    )

    assert exit_code == 0
    state = json.loads(checkpoint.read_text())
    assert set(state["discovered"]) == {A, B}
    assert "frontier" in capsys.readouterr().out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_cli.py -k refrontier`
Expected: FAIL — `invalid choice: 'refrontier'`

- [ ] **Step 3: Write the implementation**

Add the command function next to `cmd_crawl` in `cli.py`:

```python
def cmd_refrontier(args) -> int:
    """Rebuild the checkpoint's `discovered` set from the archive (ULC-F3).

    Offline: reads archived responses only, never the network.
    """
    config = _config(args)
    source = ListenBrainzSource(config)
    referenced = reconstruct_referenced(_archive(args), config, source)
    stats = rewrite_checkpoint(Path(args.checkpoint), config, referenced)
    print(
        f"done {stats['done']} | discovered {stats['discovered']} | "
        f"frontier {stats['frontier']}"
    )
    return 0
```

Add the import at the top of `cli.py`:

```python
from artistpath_builder.frontier import reconstruct_referenced, rewrite_checkpoint
```

Register the subparser beside `p_crawl`:

```python
    p_refrontier = sub.add_parser("refrontier")
    p_refrontier.add_argument("--checkpoint", default="./checkpoint.json")
    p_refrontier.add_argument(
        "--algorithm",
        default=None,
        help="which algorithm's archive tree to scan; default production's",
    )
    add_archive_args(p_refrontier)
    p_refrontier.set_defaults(func=cmd_refrontier)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_cli.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/cli.py builder/tests/test_cli.py
git commit -m "CEX-1: artistpath-build refrontier"
git push
```

---

### Task 4: `CEX-2` — bound fetching, not discovery

**Files:**
- Modify: `builder/src/artistpath_builder/crawl.py:126,141-146`
- Modify: `builder/tests/test_crawl.py:97-103`
- Modify: `builder/src/artistpath_builder/cli.py:65`

**Interfaces:**
- Produces: `target_artist_count` now caps **artists fetched** (`len(self._done)`), not artists discovered.

**⚠ `tests/test_crawl.py:97-103` (`test_discovery_stops_at_target_count`) encodes the OLD semantics and must be rewritten. Rewriting it IS the red test** — do not delete it.

**⚠ `CEXR-12`:** the existing condition `len(self.discovered) <= target` is **always true**, because the inner break capped `discovered` at exactly `target`. Today's crawl only ever stops when the queue empties. This adds the first bound that can fire.

- [ ] **Step 1: Rewrite the test to encode the new semantics**

```python
# replace tests/test_crawl.py:97-103 entirely
def test_target_caps_fetches_and_the_frontier_is_still_recorded(tmp_path, config):
    # CEX-2: target_artist_count bounds artists FETCHED, not artists
    # discovered. The old bound discarded neighbours at the target, which is
    # ULC-F3: the frontier was never recorded, so a resume rebuilt an empty
    # queue and exited 0 processed while reading as success.
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=2
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([A])

    assert len(crawler._done) == 2
    assert len(crawler.discovered) > len(crawler._done)
    assert crawler.discovered >= crawler._done
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_crawl.py -k target_caps_fetches`
Expected: FAIL — `assert 2 > 2`, because `discovered` is capped at the target rather than growing past it.

- [ ] **Step 3: Write the implementation**

In `crawl.py`, change the loop condition at line 126:

```python
        # CEX-2: the bound is on artists FETCHED, not artists discovered.
        # Bounding discovery meant the frontier past the target was never
        # recorded (ULC-F3), so a later resume had nothing to resume from.
        while queue and len(self._done) < self.config.target_artist_count:
```

and the neighbour loop at lines 141-146:

```python
            for neighbour in self._neighbours(payload, mbid):
                if neighbour not in self.discovered:
                    self.discovered.add(neighbour)
                    queue.append(neighbour)
```

In `cli.py:65`, fix `CEXR-13` so `--target 0` is not silently ignored:

```python
    if target is not None:
        overrides["target_artist_count"] = target
```

- [ ] **Step 4: Run the full builder suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS. **If another test fails, it is a caller depending on the old meaning — that is `CEX-G2`'s sweep surfacing early. Fix it and record it; do not weaken the new test.**

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/crawl.py builder/src/artistpath_builder/cli.py builder/tests/test_crawl.py
git commit -m "CEX-2: bound the crawl on fetches, so the frontier survives"
git push
```

---

### Task 5: `CEX-3` — refuse loudly, and never misfire

**Files:**
- Modify: `builder/src/artistpath_builder/crawl.py`
- Modify: `builder/src/artistpath_builder/cli.py`
- Modify: `builder/tests/test_crawl.py`

**Interfaces:**
- Produces: `class FrontierExhausted(RuntimeError)` in `crawl.py`; checkpoint gains an `exhausted: bool` key.

**⚠ `CEXR-5` — the refusal CAN misfire, and the spec's original argument was wrong.** "A genuinely exhausted graph empties its queue *during* the run" does not survive the checkpoint: `crawl.py:115` rebuilds the queue every invocation, so a run that legitimately exhausted the graph saves a checkpoint indistinguishable from the `ULC-F3` state. The `exhausted` flag is what distinguishes them **across runs**.

- [ ] **Step 1: Write the failing tests**

```python
# append to builder/tests/test_crawl.py
from artistpath_builder.crawl import FrontierExhausted


def test_raises_when_the_frontier_is_empty_but_more_was_asked_for(tmp_path):
    # The ULC-F3 signature: discovered == done, target above done.
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=99
    )
    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [A, B], "discovered": [A, B]})
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    with pytest.raises(FrontierExhausted, match="refrontier"):
        crawler.crawl([])


def test_does_not_raise_when_the_bootstrap_supplies_new_work(tmp_path):
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=99
    )
    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [A], "discovered": [A]})
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([C])
    assert C in crawler._done


def test_does_not_raise_when_the_graph_was_genuinely_exhausted(tmp_path):
    # CEXR-5: an idempotent re-run after a completed crawl must not be
    # mistaken for ULC-F3.
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=99
    )
    (tmp_path / "checkpoint.json").write_text(
        json.dumps({"done": [A, B], "discovered": [A, B], "exhausted": True})
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([])  # must not raise


def test_a_completed_crawl_records_that_it_exhausted_the_graph(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert json.loads((tmp_path / "checkpoint.json").read_text())["exhausted"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_crawl.py -k "exhaust or supplies_new_work"`
Expected: FAIL — `ImportError: cannot import name 'FrontierExhausted'`

- [ ] **Step 3: Write the implementation**

In `crawl.py`, add the exception beside `TransientFetchError`:

```python
class FrontierExhausted(RuntimeError):
    """Asked for more artists than are known, with nothing left to crawl.

    ULC-F3's signature. The damage was never that the crawl stopped — it is
    that it stopped while logging `0 processed` and exiting 0, which reads as
    success. Distinguished from a genuinely exhausted graph by the
    checkpoint's `exhausted` flag (CEXR-5): without it, an idempotent re-run
    after a completed crawl is indistinguishable from the broken state.
    """
```

Track the flag in `__init__` (after `self.discovered`):

```python
        self._exhausted: bool = state.get("exhausted", False)
```

Return it from `_load_checkpoint`:

```python
        return {
            "done": set(state.get("done", [])),
            "discovered": set(state.get("discovered", [])),
            "exhausted": state.get("exhausted", False),
        }
```

and add `"exhausted": False` to the default return of `_load_checkpoint`.

In `crawl()`, after the bootstrap-seeding loop and before `processed = 0`:

```python
        if (
            not queue
            and not self._exhausted
            and len(self._done) < self.config.target_artist_count
        ):
            raise FrontierExhausted(
                f"target is {self.config.target_artist_count} but only "
                f"{len(self._done)} artists are done and the frontier is empty. "
                "The checkpoint records no undiscovered artists, which is "
                "ULC-F3: the frontier past the old target was never recorded. "
                "Rebuild it from the archive first:\n"
                "  artistpath-build refrontier --checkpoint <path> "
                "--archive-dir <dir> --algorithm <alg>"
            )
```

At the end of `crawl()`, record the terminal condition before saving:

```python
        self._exhausted = not queue
        self._save_checkpoint()
```

and include it in `_save_checkpoint`'s payload:

```python
                    "exhausted": self._exhausted,
```

In `cli.py`, catch it at the boundary (`CEXR-14`) so the remedy is printed rather than a traceback:

```python
def cmd_crawl(args) -> int:
    config = _config(args)
    bootstrap = json.loads(Path(args.bootstrap).read_text())
    crawler = Crawler(
        config=config,
        archive=_archive(args),
        source=ListenBrainzSource(config),
        fetcher=http_fetcher(config),
        checkpoint_path=Path(args.checkpoint),
    )
    try:
        crawler.crawl([row["mbid"] for row in bootstrap])
    except FrontierExhausted as exc:
        raise SystemExit(str(exc)) from exc
    if crawler.failures:
        logging.warning("%d artists failed permanently", len(crawler.failures))
    return 0
```

Import `FrontierExhausted` alongside the existing `crawl` imports in `cli.py`.

- [ ] **Step 4: Run the full builder suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/crawl.py builder/src/artistpath_builder/cli.py builder/tests/test_crawl.py
git commit -m "CEX-3: a crawl that cannot extend now refuses instead of exiting 0"
git push
```

---

### Task 6: `CEX-4` — atomic checkpoint writes

**Files:**
- Modify: `builder/src/artistpath_builder/crawl.py:218-229`
- Modify: `builder/tests/test_crawl.py`

**Why (`CEXR-10`):** `_save_checkpoint` is a bare `write_text`, rewritten ~85 times during a four-hour run. A crash or full disk mid-write truncates the only record of the crawl. The spec makes this argument itself as grounds for backing up before `refrontier`, then did not apply it to the run.

- [ ] **Step 1: Write the failing test**

```python
# append to builder/tests/test_crawl.py
def test_checkpoint_is_written_via_a_temp_file_then_renamed(tmp_path, config, monkeypatch):
    # A truncated checkpoint is the only unrecoverable failure in a 4-hour run.
    seen: list[str] = []
    real_replace = os.replace

    def spy(src, dst):
        seen.append(str(src))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])

    assert seen, "checkpoint was not written through os.replace"
    assert all(src.endswith(".tmp") for src in seen)
    assert json.loads((tmp_path / "checkpoint.json").read_text())["done"]
```

Add `import os` to the test file's imports.

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_crawl.py -k temp_file`
Expected: FAIL — `AssertionError: checkpoint was not written through os.replace`

- [ ] **Step 3: Write the implementation**

Add `import os` to `crawl.py` and replace the body of `_save_checkpoint`:

```python
    def _save_checkpoint(self) -> None:
        # Written temp-then-rename: this file is rewritten every
        # checkpoint_every fetches across a multi-hour run, and it is the only
        # record of what has been done. A truncated write loses the crawl
        # (CEXR-10). os.replace is atomic on the same filesystem.
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "algorithm": self.config.algorithm,
                "done": sorted(self._done),
                "discovered": sorted(self.discovered),
                "exhausted": self._exhausted,
            },
            sort_keys=True,
        )
        temp = self.checkpoint_path.with_name(self.checkpoint_path.name + ".tmp")
        temp.write_text(payload)
        os.replace(temp, self.checkpoint_path)
```

- [ ] **Step 4: Run the full builder suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/crawl.py builder/tests/test_crawl.py
git commit -m "CEX-4: write the checkpoint atomically"
git push
```

---

### Task 7: `CEX-5` — resolve the ALG-E / ALG-B contradiction

**Files:**
- Modify: `builder/src/artistpath_builder/config.py:17`
- Modify: `builder/src/artistpath_builder/cli.py:274,314`

**Why:** `config.py:17` calls ALG-E "the adopted 75k archive's algorithm", but `ApiConfig.graph_path` (`api/…/config.py:24`) serves `graph-msw-tu50.bin`, whose manifest records `contribution_3` — **ALG-B**. `config.py:17` is the stale side. A live defect independent of this track; steps 4–7 trip over it.

**⚠ Do NOT change the `algorithm` default.** Flipping it is the re-crawl decision and it is the owner's (`config.py:56-58`).

- [ ] **Step 1: Fix the three comments**

`config.py:17` — replace the trailing comment:

```python
PRODUCTION_ALGORITHM = (  # ALG-E — the ORIGINAL production crawl's algorithm
```

and add below the closing parenthesis of `CANDIDATE_ALGORITHM`:

```python
# ⚠ ALG-B is the ADOPTED map's lineage: graph-msw-tu50.bin was built from the
# ALG-B archive (its manifest records contribution_3), and ApiConfig.graph_path
# serves it. `algorithm` below still DEFAULTS to ALG-E, deliberately — flipping
# that default is the re-crawl decision and is the owner's — so every command
# touching the adopted lineage must pass --algorithm explicitly. CEX-R5.
```

`cli.py:274` — replace the crawl `--algorithm` help text:

```python
        help="source algorithm; default is ALG-E, NOT the adopted map's ALG-B",
```

`cli.py:314` — replace the stale `--cap-strategy` help text:

```python
        help="cap rule; default config's (trimmed_union since the MSW- adoption)",
```

- [ ] **Step 2: Verify nothing else repeats the stale claim**

Run: `git grep -n "adopted 75k archive" -- builder/ api/ docs/`
Expected: no hits outside frozen execution logs and handoffs, which are **correct for their own date and must not be edited**.

- [ ] **Step 3: Run the full builder suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS (comments only)

- [ ] **Step 4: Commit**

```bash
git add builder/src/artistpath_builder/config.py builder/src/artistpath_builder/cli.py
git commit -m "CEX-5: the adopted lineage is ALG-B, not ALG-E"
git push
```

---

### Task 8: `CEX-M1` — measure the p99 rescale and edge saturation

**Files:**
- Modify: `builder/src/artistpath_builder/pipeline.py:94-110`
- Modify: `builder/tests/test_pipeline_rescale.py`

**Why (`CEXR-3`):** `rescale_scores` normalises on the 99th percentile of **this build's** edges and feeds `w_sim·(1−similarity)`, the router's primary term. The extension adds millions of low-co-occurrence edges, which pulls the percentile down, raises every rescaled similarity, and pushes more edges to saturate at exactly 1.0 — the "free similarity" defect `config.py:169-177` carries as open. **In plain terms: more hops may become free, so more of the route is decided by tie-breaks than by similarity.** Without this, nothing in the track would notice.

- [ ] **Step 1: Write the failing test**

```python
# append to builder/tests/test_pipeline_rescale.py
import logging


def test_rescale_logs_the_scale_and_the_saturated_share(caplog):
    # CEX-M1: the p99 scale is population-dependent and prices the router's
    # primary term. Comparing two builds needs it as a figure, not a guess.
    from artistpath_builder.pipeline import rescale_scores

    with caplog.at_level(logging.INFO, logger="artistpath_builder.pipeline"):
        rescale_scores([1.0] * 99 + [1000.0], strategy="p99_log_clip", damping=0.0)

    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "p99" in messages
    assert "saturated" in messages
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pipeline_rescale.py -k saturated`
Expected: FAIL — `AssertionError` on `"p99" in messages`

- [ ] **Step 3: Write the implementation**

**⚠ `rescale_scores` has no "end of function" both paths reach, and no `rescaled` variable.**
Its `p99_log_clip` branch **returns an inline list comprehension** (`pipeline.py:108-110`) and
the other path raises. So this is a small refactor, not an append. Replace the `return` at
`pipeline.py:108-110` with:

```python
        rescaled = [min(1.0, math.log1p(max(0.0, v)) / log_scale) for v in raw]
        # CEX-M1: both figures are population-dependent and price the router's
        # primary term (w_sim). Logged so two builds can be compared rather
        # than assumed.
        saturated = sum(1 for value in rescaled if value >= 1.0)
        logger.info(
            "rescale p99 scale=%.6g | saturated edges %d of %d (%.3f%%)",
            scale,
            saturated,
            len(rescaled),
            100.0 * saturated / len(rescaled),
        )
        return rescaled
```

`len(rescaled)` cannot be zero here — `rescale_scores` returns early on an empty input at
`pipeline.py:91-92` — so no zero-division guard is needed.

- [ ] **Step 4: Run the full builder suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/pipeline.py builder/tests/test_pipeline_rescale.py
git commit -m "CEX-M1: log the p99 scale and saturated-edge share"
git push
```

---

### Task 9: Snapshot the archive, then run `CEX-G1`

**This is an operational gate, not code. It runs once and is recorded, never in CI.**

**Files:**
- Create: `builder/analysis/2026-08-08-cex-g1/g1_result.md`

**⚠ Step 1 is the owner's precondition for the whole track.** After the crawl appends, today's graph **cannot be rebuilt from source** — `build_from_archive` reads everything under the algorithm prefix and has no "build only this population" option. The snapshot is what makes this reversible.

- [ ] **Step 1: Snapshot the archive** (size and free space are in the spec's §4 step 0)

```bash
cp -r /c/dev/music-app/builder/scratch/grt-archive-algb \
      /c/dev/music-app/builder/scratch/grt-archive-algb.pre-cex-snapshot
```

- [ ] **Step 2: Verify the snapshot is complete before trusting it**

```bash
find /c/dev/music-app/builder/scratch/grt-archive-algb.pre-cex-snapshot/similar -name '*.json' | wc -l
```
Expected: `75000`. **If it is not exactly 75000, stop and do not proceed to the crawl.**

- [ ] **Step 3: Back up the checkpoint**

```bash
cp /c/dev/music-app/builder/scratch/checkpoint-algb-full.json \
   /c/dev/music-app/builder/scratch/checkpoint-algb-full.json.pre-cex
```

- [ ] **Step 4: Run `refrontier` and check `CEX-G1`**

```bash
cd /c/dev/music-app/builder
UV_LINK_MODE=copy PYTHONUNBUFFERED=1 uv run artistpath-build refrontier \
  --checkpoint scratch/checkpoint-algb-full.json \
  --archive-dir scratch/grt-archive-algb \
  --algorithm session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30
```

**`CEX-G1` passes only if `frontier` is exactly the `reconstruction.frontier_size` recorded in `builder/analysis/2026-08-07-cex-frontier/cex_frontier.json`.** A disagreement means the reconstruction is wrong — **stop and diagnose; do not crawl.**

- [ ] **Step 5: Assert the invariant `CEX-G1` cannot see**

```bash
UV_LINK_MODE=copy uv run python -u -c "
import json
s=json.load(open('scratch/checkpoint-algb-full.json'))
done,disc=set(s['done']),set(s['discovered'])
print('done',len(done),'discovered',len(disc),'frontier',len(disc-done))
assert done <= disc, 'CEXR-7b: done is no longer a subset of discovered'
print('done is a subset of discovered: OK')
"
```

- [ ] **Step 6: Record the outcome and commit**

Write `g1_result.md` with the three counts, the `CEX-G1` pass/fail, the snapshot path and its file count. Then:

```bash
git add builder/analysis/2026-08-08-cex-g1/
git commit -m "CEX-G1: frontier reconstructed and checked against the baseline"
git push
```

---

### Task 10: The crawl — **HANDOFF SEAM after this task**

**This is operational. ~4 hours. Run it detached with `python -u` semantics or it will look dead.**

- [ ] **Step 1: Confirm the target arithmetic before starting**

75,000 done + 42,302 frontier = **117,302**. Under `CEX-2` the target caps **fetches**, so this crawls exactly the frontier. **`CEXR-11`:** permanent fetch failures keep `_done` below target, so the loop dips into newly discovered artists to make up the shortfall — the final population's composition depends on the failure count. Record the failure count.

- [ ] **Step 2: Run the crawl**

```bash
cd /c/dev/music-app/builder
UV_LINK_MODE=copy PYTHONUNBUFFERED=1 uv run artistpath-build crawl \
  --bootstrap scratch/bootstrap.json \
  --checkpoint scratch/checkpoint-algb-full.json \
  --archive-dir scratch/grt-archive-algb \
  --algorithm session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30 \
  --target 117302 2>&1 | tee scratch/cex-crawl.log
```

- [ ] **Step 3: Verify it actually crawled**

```bash
find scratch/grt-archive-algb/similar -name '*.json' | wc -l
```
Expected: ~117,302. **If it printed `0 processed`, `CEX-3` failed to fire — stop and diagnose.**

- [ ] **Step 4: Commit the log and hand off**

```bash
git add builder/analysis/2026-08-08-cex-g1/
git commit -m "CEX-: crawl extended to 117,302"
git push
```

> **⚠ SEAM. Retire the session here.** The archive is now a committed durable artifact rather than a live understanding. The next session reads this plan, the spec, and the `g1_result.md` cold. Write a handoff note per `closeout` before stopping.

---

### Task 11: Fame, re-census, build — **OWNER STOP at the end**

**Operational. Every command passes `--algorithm` explicitly (`CEXR-2`): `similar_prefix` selects the tree from `config.algorithm`, `_config` defaults to ALG-E, and there is no `RC-H3` guard on the build side.**

- [ ] **Step 1: Cost the re-census before running it (`CEXR-9`)**

The un-listenable keep-check is **per-artist** against rate-limited services, and `ULC-F2`'s coverage store means you pay only for genuinely new artists — which is the entire extension. **Measure the rate on the first 500 artists and extrapolate. Report the estimate before running the full pass.** If it lands in hours rather than minutes, tell the owner and treat it as a second seam.

- [ ] **Step 2: Fetch fame for the new artists**

```bash
UV_LINK_MODE=copy PYTHONUNBUFFERED=1 uv run artistpath-build fame \
  --archive-dir scratch/grt-archive-algb \
  --algorithm session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30
```

Batches at 1000 per request and resumes past existing records, so this is seconds.

- [ ] **Step 3: Re-census `unlistenable` over the new population**

**`unlistenable` only.** `pipeline.py:279-284` states all three drop classes are strict subsets and applying all three is identical to applying this one; the baseline census bears it out. **Re-verify the subset relation over the NEW population rather than inheriting it.**

- [ ] **Step 4: Build, and expect rejection**

```bash
UV_LINK_MODE=copy PYTHONUNBUFFERED=1 uv run artistpath-build build \
  --archive-dir scratch/grt-archive-algb \
  --algorithm session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30 \
  --require-fame \
  --out scratch/graph-cex-117k.bin 2>&1 | tee scratch/cex-build.log
```

**`check_acceptance` WILL reject, on BOTH bounds** — nodes `(47_000, 71_000)` and edges `(1_050_000, 1_580_000)` (`acceptance.py:170-171`); it collects every violation before raising. **Record both actual values from the log.**

- [ ] **Step 5: Record `CEX-M1` and stop**

From `cex-build.log`, record the **p99 scale** and the **saturated-edge share**, and compare them to the adopted build. **If the saturated share rose materially, that is a path-quality change and therefore the owner's, not a build-log footnote.**

> **⚠ OWNER STOP. Do not widen the acceptance bounds.** `acceptance.py:139`: a new crawl is a new artifact identity, not a bound to widen quietly. `MSW-G3` is the worked precedent and there too the recalibration was the owner's. **Report both actual counts, both bounds, and `CEX-M1`'s two figures, and wait.**

---

## Self-Review

**Spec coverage.** `CEX-1` → Tasks 1–3. `CEX-2` → Task 4. `CEX-3` → Task 5. `CEX-4` → Task 6. `CEX-5` → Task 7. `CEX-M1` → Task 8. Step 0 snapshot + `CEX-G1` → Task 9. Steps 4–7 → Tasks 10–11. `CEX-G2` (the `--target` caller sweep) is folded into Task 4 Step 4, where a failing suite surfaces it. Seams at Tasks 10 and 11 match spec §6.

**Review findings.** `CEXR-1` needs **no task** — its remedy (seeding) was *removed* from the design at spec §3 rather than implemented, so there is nothing here to build. `CEXR-2` → Task 11 preamble. `CEXR-3` → Task 8. `CEXR-4` → Task 11 Step 4. `CEXR-5` → Task 5. `CEXR-6` → Task 11 Step 3 (drop lists) — **the `load_deezer_ids` half is NOT fixed by this plan and stays open**; it is a coverage regression, not a build failure, and belongs to §5's readable list. `CEXR-7a/b` → Tasks 1, 2, 9 Step 5. `CEXR-8` → Task 9 framing. `CEXR-9` → Task 11 Step 1. `CEXR-10` → Task 6. `CEXR-11` → Task 10 Step 1. `CEXR-12`/`13` → Task 4. `CEXR-14` → Task 5.

**Type consistency.** `reconstruct_referenced` and `rewrite_checkpoint` are named identically in Tasks 1–3, and are reached in Task 9 through the `refrontier` CLI rather than by name. `FrontierExhausted` is used identically in Tasks 5 and 10. The checkpoint's `exhausted` key is written in Tasks 2, 5 and 6 and read in Task 5.

**Known gap, stated rather than hidden:** `CEXR-6`'s `load_deezer_ids` finding is **not** remediated here. Every new artist gets `""` and falls back to name-based clip resolution (`BYP-13`). It needs its own track and is recorded in the spec's §5.
