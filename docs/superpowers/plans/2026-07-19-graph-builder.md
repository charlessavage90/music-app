# Graph Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a compact, deterministic artist-similarity graph artifact from ListenBrainz data, with every raw API response archived so the graph can be rebuilt forever without network access.

**Architecture:** A standalone Python package (`builder/`) with no dependency on the rest of the app. It crawls a similarity source behind a `SimilaritySource` protocol, archives every raw response verbatim, then assembles a symmetrised graph, keeps the largest connected component, and serialises it to a single binary CSR artifact. Everything downstream consumes that artifact and nothing else.

**Tech Stack:** Python 3.12+ (3.14.3 available locally), `uv` for dependency management, `pytest`, `httpx`, `boto3`, `numpy`.

**Spec:** `docs/superpowers/specs/2026-07-19-artist-path-alpha-design.md`. Where this plan and the spec disagree, the spec wins — raise it rather than improvising.

## Amendment 2 — 2026-07-20: popularity moves to the spark dump

**Tasks 2–10 are implemented and committed.** From here the code is the source of truth; the task bodies below are the record of how it was built. This amendment describes a change applied to that working code.

**Trigger.** An instrumented trial crawl measured the per-artist stats endpoint at **~22.8s per call** against ~1.1s for similarity, with rate-limit headers showing we were *not* throttled (findings §6a). Stats accounted for ~95% of crawl time and made 75k artists a ~21-day job.

**Change.** Popularity is no longer fetched per artist. It is derived offline from the 191GB ListenBrainz spark dump (new Task 12). Three consequences:

1. **The crawler fetches similarity only.** `stats_key()` and the second fetch are removed. Crawl drops to ~1.3s per artist — ~27 hours serial, ~7 hours at 4-way concurrency.
2. **Names and disambiguation are harvested from similarity responses.** Every neighbour row carries `name` and `comment`, so dropping the stats call forces the harvesting that was previously deferred — and delivers disambiguation for free, closing the known deviation recorded in the self-review.
3. **The two pipelines are independent.** The similarity crawl and the popularity job both feed the graph build and neither blocks the other. The crawl can run before Task 12 exists.

**Superseded:** Task 6's stats fetching, Task 9's `_archived_stats`, and Task 11's assumption that popularity lives in the archive.

---

## Amendment 3 — 2026-07-20: popularity is in-degree, not the spark dump

**Amendment 2's spark-dump plan is withdrawn before implementation.** Inspecting real dump files (a 235MB sample and a 216MB incremental listens dump) showed the approach could not work, and a cheap validation found a better one.

**What the dumps revealed (findings §6c–6e):**
- Raw listen records carry a MusicBrainz artist ID on **0.03%** of rows — they hold free-text names and Spotify IDs. Aggregating them to per-artist popularity is impossible.
- The 235MB *sample* dump does contain a pre-aggregated, MBID-keyed popularity table, but only ~5,255 artists. Too small to be the source, but perfect as **ground truth** for validating a proxy.
- Deezer `nb_fan`, tested as a fallback, correlated **0.089** with ListenBrainz popularity — it measures a different listener population, which the ListenBrainz-derived similarity graph must not be mixed with.

**What was adopted (findings §6f):** score-weighted in-degree of the similarity graph — the summed similarity of edges pointing at an artist. Validated at Spearman ~0.50 against the 5,255 ground-truth artists, free to compute, and the only popularity measure on the same population as the similarity data.

**Consequences for the code (all applied):**
1. `popularity.py` and `test_popularity.py` are **deleted**. There is no dump ingestion, no listen aggregation, no popularity table.
2. `build_from_archive(config, archive, source)` computes in-degree internally and takes **no popularity argument**.
3. The `popularity` CLI command and `build --popularity` flag are removed. `build` needs only the archive.
4. Dead code from the withdrawn stats approach — `artist_stats_url`, `parse_artist_stats`, the `artist_stats_url` config field and their tests — is removed.

**This makes Task 12 (spark-dump popularity pipeline) unnecessary; it is withdrawn.** The builder's public surface is now: `bootstrap → crawl → build → fixture`, with popularity emerging from the graph during `build`.

---

## Global Constraints

Every task's requirements implicitly include these. All are copied from the spec.

- **Archiving is non-negotiable** (spec §3.1 step 2). Raw responses are archived verbatim as they are fetched. It must not be deferred as an optimisation.
- **A rebuild from archive, with the network unavailable, must produce a byte-identical graph** (spec §9). This is the acceptance test for the whole plan.
- **Edges are typed.** Alpha emits exactly one type, `BEHAVIOURAL = 0`, but the format carries `edge_types: uint8` per edge (spec §3.1).
- **The builder takes a *list* of sources.** Alpha configures exactly one (spec §3.1).
- **Similarity is symmetrised.** One-way edges create dead ends (spec §3.1 step 4).
- **Only the largest connected component is kept.** This guarantees a path exists between any two artists the UI can offer, so "no path" can only ever result from user exclusions (spec §3.1 step 5).
- **Target ~75,000 artists.** Expected artifact size 40–80MB (spec §3.1).
- **Last.fm must never become load-bearing** — it is non-commercial-only and the roadmap includes paid tiers (spec §1). Do not add it as a source in this plan.
- **Depth over breadth** (spec §2.1). Do not add album or track handling. Do not add a second source.
- **Determinism.** Artists are sorted by MBID and assigned integer IDs in that order; neighbour lists are sorted by neighbour ID; JSON is written with `sort_keys=True` and `separators=(",", ":")`. Without this, byte-identical replay is impossible.

---

## File Structure

```
builder/
  pyproject.toml
  README.md
  src/artistpath_builder/
    __init__.py
    config.py            # BuilderConfig — all tunables, no magic numbers elsewhere
    models.py            # SimilarArtist, BootstrapArtist, ArtistStats, EdgeType
    archive.py           # RawArchive protocol; LocalArchive + S3Archive
    sources/
      __init__.py
      base.py            # SimilaritySource protocol
      listenbrainz.py    # ListenBrainz Labs client + response parsing
      seeds.py           # Seed artist list acquisition (top artists by listens)
    crawl.py             # Resumable, checkpointed, rate-limited crawler
    graph.py             # Symmetrise + largest connected component
    artifact.py          # CSR binary serialisation / deserialisation
    cli.py               # Entry points
  tests/
    conftest.py
    fixtures/
      similar_artists_sample.json   # RECORDED from the real API in Task 1
      seed_artists_sample.json      # RECORDED from the real API in Task 1
    test_archive.py
    test_listenbrainz.py
    test_seeds.py
    test_crawl.py
    test_graph.py
    test_artifact.py
    test_replay.py
docs/superpowers/findings/2026-07-19-listenbrainz-probe.md   # written in Task 1
```

Responsibilities are split so that the two things most likely to change — the shape of the upstream API, and where archives live — are each isolated behind one interface. `graph.py` and `artifact.py` are pure functions over in-memory data with no I/O, which is what makes them cheap to test.

---

## Task 1: Spike — probe the real API and record fixtures ✅ COMPLETE

**Done 2026-07-19, commit `355737d`. Verdict: GO.** Findings: `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md`. Tasks 2, 5, 6, 7, 9 and 11 were amended in response — chiefly, the sitewide endpoint caps at 1,000 artists so seeding became snowball discovery, and popularity moved to a per-artist endpoint. The steps below are retained as the record of what was probed.

**This task was a gate.** Spec §8.1 names similarity-data acquisition as the primary risk and requires it be settled before app code exists. Nothing else in this plan may start until this task's findings are reviewed by a human. Its deliverable is knowledge and recorded fixtures, not production code.

Two things are genuinely unknown and must be resolved by observation, not assumption:
1. The exact JSON shape returned by the ListenBrainz Labs `similar-artists` endpoint.
2. How to obtain ~75k seed artists with listen counts for popularity.

**Files:**
- Create: `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md`
- Create: `builder/tests/fixtures/similar_artists_sample.json`
- Create: `builder/tests/fixtures/seed_artists_sample.json`

**Interfaces:**
- Consumes: nothing.
- Produces: two recorded JSON fixtures used verbatim by Tasks 4 and 5, and a findings document that may amend this plan.

- [ ] **Step 1: Probe the similarity endpoint with a known artist**

Radiohead's MBID is `a74b1b7f-71a5-4011-9441-d0b5e4122711`.

```bash
curl -s -H "User-Agent: artistpath-builder/0.1 (charlessavagemiller@gmail.com)" \
  "https://labs.api.listenbrainz.org/similar-artists/json?artist_mbids=a74b1b7f-71a5-4011-9441-d0b5e4122711&algorithm=session_based_days_7500_session_300_contribution_5_threshold_10_limit_100_filter_True_skip_30" \
  | tee builder/tests/fixtures/similar_artists_sample.json | head -c 2000
```

Expected: a JSON array or object containing similar artists. **Record exactly what comes back**, including if it is an error.

- [ ] **Step 2: If the above returns an error, try the simpler algorithm**

```bash
curl -s -H "User-Agent: artistpath-builder/0.1 (charlessavagemiller@gmail.com)" \
  "https://labs.api.listenbrainz.org/similar-artists/json?artist_mbids=a74b1b7f-71a5-4011-9441-d0b5e4122711&algorithm=session_based_days_7500_session_30" \
  | tee builder/tests/fixtures/similar_artists_sample.json | head -c 2000
```

Record which algorithm string worked. It becomes `BuilderConfig.algorithm` in Task 2.

- [ ] **Step 3: Determine the response field names**

From the recorded fixture, answer in the findings doc:
- What field holds the neighbour's MBID?
- What field holds the similarity score, and what is its range? (If scores are raw counts rather than 0–1, normalisation is required and Task 4 must handle it.)
- Is the artist's name included, or does it require a second lookup?
- How many neighbours are returned by default?

- [ ] **Step 4: Probe for a seed artist list with listen counts**

```bash
curl -s -H "User-Agent: artistpath-builder/0.1 (charlessavagemiller@gmail.com)" \
  "https://api.listenbrainz.org/1/stats/sitewide/artists?count=100&range=all_time" \
  | tee builder/tests/fixtures/seed_artists_sample.json | head -c 2000
```

Record: the field names, whether `listen_count` is present, and critically **the maximum `count` and `offset` the endpoint permits**. If it caps well below 75,000, that is a finding that changes the plan.

- [ ] **Step 5: Establish the rate limit**

Check response headers for rate-limit hints:

```bash
curl -sI -H "User-Agent: artistpath-builder/0.1 (charlessavagemiller@gmail.com)" \
  "https://api.listenbrainz.org/1/stats/sitewide/artists?count=10&range=all_time"
```

Record any `X-RateLimit-*` headers. These set `BuilderConfig.requests_per_second` in Task 2.

- [ ] **Step 6: Write the findings document**

Create `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md` covering, with evidence:

- Working algorithm string
- Similarity response schema, with a real example
- Score semantics and range
- Seed acquisition method, and whether 75k artists is reachable
- Observed rate limits
- **A go / no-go recommendation.** If seed acquisition caps far below 75k, or similarity coverage looks thin, say so plainly and propose an alternative (spec §8.1 names MusicBrainz relationship data as the substitute). Do not proceed on optimism.

- [ ] **Step 7: Commit**

```bash
git add builder/tests/fixtures docs/superpowers/findings
git commit -m "spike: record real ListenBrainz API responses and probe findings"
```

- [ ] **Step 8: STOP and request human review**

Report the findings and wait. If the answer is no-go, this plan is revised before any further task begins.

---

## Task 2: Project scaffolding, config, and models

**Files:**
- Create: `builder/pyproject.toml`
- Create: `builder/src/artistpath_builder/__init__.py`
- Create: `builder/src/artistpath_builder/config.py`
- Create: `builder/src/artistpath_builder/models.py`
- Create: `builder/tests/conftest.py`
- Test: `builder/tests/test_config.py`

**Interfaces:**
- Consumes: the algorithm string and rate limit recorded in Task 1.
- Produces: `BuilderConfig`, `SimilarArtist`, `BootstrapArtist`, `ArtistStats`, `EdgeType` — used by every later task.

- [ ] **Step 1: Create the project**

`builder/pyproject.toml`:

```toml
[project]
name = "artistpath-builder"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27",
    "boto3>=1.34",
    "numpy>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0"]

[project.scripts]
artistpath-build = "artistpath_builder.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Write the failing test**

`builder/tests/test_config.py`:

```python
from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import ArtistStats, EdgeType, SimilarArtist


def test_config_has_sane_defaults():
    cfg = BuilderConfig()
    assert cfg.target_artist_count == 75_000
    # Task 1 measured 30 requests / 5 seconds. Never exceed 6/s.
    assert 0 < cfg.requests_per_second <= 6.0
    assert cfg.user_agent.startswith("artistpath-builder/")


def test_artist_stats_defaults_disambiguation():
    stats = ArtistStats(mbid="a" * 36, name="A", user_count=10, listen_count=99)
    assert stats.disambiguation == ""


def test_behavioural_edge_type_is_zero():
    # Alpha emits exactly one edge type; downstream reads it as uint8.
    assert EdgeType.BEHAVIOURAL == 0


def test_similar_artist_is_comparable_and_frozen():
    a = SimilarArtist(mbid="a" * 36, name="A", score=0.5)
    b = SimilarArtist(mbid="a" * 36, name="A", score=0.5)
    assert a == b
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.config'`

- [ ] **Step 4: Write the implementation**

`builder/src/artistpath_builder/__init__.py`:

```python
__version__ = "0.1.0"
```

`builder/src/artistpath_builder/models.py`:

```python
"""Plain data carried between builder stages. No I/O, no behaviour."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class EdgeType(IntEnum):
    """Serialised as uint8 per edge.

    Alpha emits only BEHAVIOURAL. The type exists so a second source can be
    added without changing the artifact format (spec section 3.1).
    """

    BEHAVIOURAL = 0
    STRUCTURAL = 1  # reserved: MusicBrainz/Discogs. Not emitted in alpha.
    DESCRIPTIVE = 2  # reserved: shared genre tags. Not emitted in alpha.


@dataclass(frozen=True, slots=True)
class SimilarArtist:
    """One neighbour of some artist, as reported by a similarity source."""

    mbid: str
    name: str
    score: float


@dataclass(frozen=True, slots=True)
class BootstrapArtist:
    """An artist from the sitewide top-1000, used only to start the snowball.

    Carries no popularity: the sitewide endpoint caps at 1000 artists, so
    popularity is fetched per-artist instead (see the Task 1 findings).
    """

    mbid: str
    name: str


@dataclass(frozen=True, slots=True)
class ArtistStats:
    """Per-artist popularity and metadata. One record per graph node."""

    mbid: str
    name: str
    user_count: int  # distinct listeners — the popularity signal (spec 4.1)
    listen_count: int  # plays; archived but NOT used for routing
    disambiguation: str = ""
```

`builder/src/artistpath_builder/config.py`:

```python
"""All builder tunables. No magic numbers anywhere else in the package."""

from __future__ import annotations

from dataclasses import dataclass

from artistpath_builder import __version__

CONTACT_EMAIL = "charlessavagemiller@gmail.com"


@dataclass(frozen=True, slots=True)
class BuilderConfig:
    # --- source ---------------------------------------------------------
    # NOTE: replace with the algorithm string confirmed working in Task 1.
    algorithm: str = (
        "session_based_days_7500_session_300_contribution_5"
        "_threshold_10_limit_100_filter_True_skip_30"
    )
    similar_artists_url: str = "https://labs.api.listenbrainz.org/similar-artists/json"
    sitewide_artists_url: str = "https://api.listenbrainz.org/1/stats/sitewide/artists"

    artist_stats_url: str = "https://api.listenbrainz.org/1/stats/artist"

    # --- crawl ----------------------------------------------------------
    target_artist_count: int = 75_000
    # Task 1 measured X-RateLimit: 30 requests per 5s window (~6/s).
    # Deliberately under it: this crawl runs once, and being throttled costs
    # more than being slow.
    requests_per_second: float = 5.0
    max_retries: int = 5
    timeout_seconds: float = 30.0
    checkpoint_every: int = 500

    # --- graph ----------------------------------------------------------
    max_neighbours_per_artist: int = 50

    # --- output ---------------------------------------------------------
    graph_version: str = "v1"

    @property
    def user_agent(self) -> str:
        return f"artistpath-builder/{__version__} ({CONTACT_EMAIL})"

    @property
    def request_delay_seconds(self) -> float:
        return 1.0 / self.requests_per_second
```

`builder/tests/conftest.py`:

```python
import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def similar_artists_payload() -> dict | list:
    """The real API response recorded in Task 1."""
    return json.loads((FIXTURES / "similar_artists_sample.json").read_text())


@pytest.fixture
def seed_artists_payload() -> dict | list:
    """The real API response recorded in Task 1."""
    return json.loads((FIXTURES / "seed_artists_sample.json").read_text())
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_config.py -v
```

Expected: 3 passed

- [ ] **Step 6: Update `config.py` with Task 1's real values**

Replace `algorithm` and `requests_per_second` with the values the findings document confirmed. If they already match, note that in the commit message.

- [ ] **Step 7: Commit**

```bash
git add builder/
git commit -m "feat(builder): scaffold package with config and models"
```

---

## Task 3: Raw response archive

The mitigation for spec §8.1. Every response is stored verbatim so rebuilds never need the network.

**Files:**
- Create: `builder/src/artistpath_builder/archive.py`
- Test: `builder/tests/test_archive.py`

**Interfaces:**
- Consumes: `BuilderConfig` (Task 2).
- Produces: `RawArchive` protocol with `put(key: str, payload: bytes) -> None`, `get(key: str) -> bytes | None`, `has(key: str) -> bool`, `keys() -> Iterator[str]`. `LocalArchive(root: Path)` and `S3Archive(bucket: str, prefix: str)` implement it. Used by Tasks 6 and 9.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_archive.py`:

```python
import pytest

from artistpath_builder.archive import LocalArchive


def test_put_then_get_round_trips(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put("similar/abc.json", b'{"hello":"world"}')
    assert archive.get("similar/abc.json") == b'{"hello":"world"}'


def test_get_missing_key_returns_none(tmp_path):
    assert LocalArchive(tmp_path).get("nope.json") is None


def test_has_reports_presence(tmp_path):
    archive = LocalArchive(tmp_path)
    assert not archive.has("k.json")
    archive.put("k.json", b"x")
    assert archive.has("k.json")


def test_keys_lists_everything_written(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put("similar/b.json", b"1")
    archive.put("similar/a.json", b"2")
    assert sorted(archive.keys()) == ["similar/a.json", "similar/b.json"]


def test_payload_is_stored_byte_identical(tmp_path):
    # Archived bytes must never be reformatted. Replay determinism depends
    # on replaying exactly what the server sent.
    archive = LocalArchive(tmp_path)
    payload = b'{"b":2,  "a":1}\n\n'
    archive.put("raw.json", payload)
    assert archive.get("raw.json") == payload


def test_key_traversal_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        LocalArchive(tmp_path).put("../escape.json", b"x")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_archive.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.archive'`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/archive.py`:

```python
"""Verbatim storage of raw upstream responses.

Spec section 3.1 step 2: rebuilds replay this archive instead of the network,
which is what makes the crawl a one-time event rather than a dependency.
Payloads are stored exactly as received and are never reformatted.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, runtime_checkable


def _validate_key(key: str) -> None:
    if not key or key.startswith("/") or ".." in key.split("/"):
        raise ValueError(f"unsafe archive key: {key!r}")


@runtime_checkable
class RawArchive(Protocol):
    def put(self, key: str, payload: bytes) -> None: ...
    def get(self, key: str) -> bytes | None: ...
    def has(self, key: str) -> bool: ...
    def keys(self) -> Iterator[str]: ...


class LocalArchive:
    """Filesystem-backed archive. Used for development and tests."""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        _validate_key(key)
        return self._root / key

    def put(self, key: str, payload: bytes) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    def get(self, key: str) -> bytes | None:
        path = self._path(key)
        return path.read_bytes() if path.is_file() else None

    def has(self, key: str) -> bool:
        return self._path(key).is_file()

    def keys(self) -> Iterator[str]:
        for path in sorted(self._root.rglob("*")):
            if path.is_file():
                yield path.relative_to(self._root).as_posix()


class S3Archive:
    """S3-backed archive. Used in CI and for the real crawl."""

    def __init__(self, bucket: str, prefix: str = "raw", client=None) -> None:
        import boto3

        self._bucket = bucket
        self._prefix = prefix.strip("/")
        self._client = client or boto3.client("s3")

    def _full_key(self, key: str) -> str:
        _validate_key(key)
        return f"{self._prefix}/{key}"

    def put(self, key: str, payload: bytes) -> None:
        self._client.put_object(
            Bucket=self._bucket, Key=self._full_key(key), Body=payload
        )

    def get(self, key: str) -> bytes | None:
        from botocore.exceptions import ClientError

        try:
            response = self._client.get_object(
                Bucket=self._bucket, Key=self._full_key(key)
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("NoSuchKey", "404"):
                return None
            raise
        return response["Body"].read()

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def keys(self) -> Iterator[str]:
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=f"{self._prefix}/"):
            for obj in page.get("Contents", []):
                yield obj["Key"][len(self._prefix) + 1 :]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_archive.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/archive.py builder/tests/test_archive.py
git commit -m "feat(builder): add verbatim raw response archive"
```

---

## Task 4: ListenBrainz similarity source

**Files:**
- Create: `builder/src/artistpath_builder/sources/__init__.py`
- Create: `builder/src/artistpath_builder/sources/base.py`
- Create: `builder/src/artistpath_builder/sources/listenbrainz.py`
- Test: `builder/tests/test_listenbrainz.py`

**Interfaces:**
- Consumes: `BuilderConfig`, `SimilarArtist` (Task 2); the recorded fixture (Task 1).
- Produces: `SimilaritySource` protocol with `request_url(mbid) -> str` and `parse(payload: bytes) -> list[SimilarArtist]`; `ListenBrainzSource` implements it. Used by Task 6.

**Note:** parsing is separated from fetching on purpose. Task 6 owns the network; this task owns the schema. That split is what lets Task 9 replay the archive through the identical parser.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_listenbrainz.py`:

```python
import pytest

from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

RADIOHEAD = "a74b1b7f-71a5-4011-9441-d0b5e4122711"


@pytest.fixture
def source():
    return ListenBrainzSource(BuilderConfig())


def test_request_url_includes_mbid_and_algorithm(source):
    url = source.request_url(RADIOHEAD)
    assert RADIOHEAD in url
    assert BuilderConfig().algorithm in url


def test_parses_recorded_real_response(source, similar_artists_payload):
    """Runs against the response recorded from the live API in Task 1."""
    import json

    neighbours = source.parse(json.dumps(similar_artists_payload).encode())
    assert len(neighbours) > 0
    first = neighbours[0]
    assert len(first.mbid) == 36
    assert 0.0 <= first.score <= 1.0


def test_scores_are_normalised_to_unit_range(source, similar_artists_payload):
    import json

    neighbours = source.parse(json.dumps(similar_artists_payload).encode())
    assert all(0.0 <= n.score <= 1.0 for n in neighbours)
    # The strongest neighbour anchors the scale.
    assert max(n.score for n in neighbours) == pytest.approx(1.0)


def test_empty_response_yields_no_neighbours(source):
    assert source.parse(b"[]") == []


def test_malformed_payload_raises(source):
    with pytest.raises(ValueError):
        source.parse(b"not json")


def test_self_reference_is_dropped(source):
    # An artist must never be its own neighbour: a self-loop is a zero-cost
    # cycle that pathfinding would happily sit inside.
    payload = (
        b'[{"artist_mbid":"' + RADIOHEAD.encode() + b'","name":"Radiohead","score":99}]'
    )
    assert source.parse(payload, exclude_mbid=RADIOHEAD) == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_listenbrainz.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/sources/__init__.py`:

```python
from artistpath_builder.sources.base import SimilaritySource

__all__ = ["SimilaritySource"]
```

`builder/src/artistpath_builder/sources/base.py`:

```python
"""The seam that isolates upstream schema changes (spec section 8.1)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from artistpath_builder.models import EdgeType, SimilarArtist


@runtime_checkable
class SimilaritySource(Protocol):
    name: str
    edge_type: EdgeType

    def request_url(self, mbid: str) -> str:
        """The URL to fetch this artist's neighbours from."""
        ...

    def parse(
        self, payload: bytes, exclude_mbid: str | None = None
    ) -> list[SimilarArtist]:
        """Turn a raw response body into neighbours, scores normalised to 0-1."""
        ...
```

`builder/src/artistpath_builder/sources/listenbrainz.py`:

```python
"""ListenBrainz Labs similar-artists source.

CC0 licensed, MusicBrainz-keyed, published by MetaBrainz in response to
Spotify's November 2024 API deprecations (spec section 1).

IMPORTANT: field names below are taken from the response recorded in Task 1.
If Task 1's findings show different names, correct FIELD_* here — this module
is the only place that knows the upstream schema.
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import EdgeType, SimilarArtist

FIELD_MBID = "artist_mbid"
FIELD_NAME = "name"
FIELD_SCORE = "score"


class ListenBrainzSource:
    name = "listenbrainz"
    edge_type = EdgeType.BEHAVIOURAL

    def __init__(self, config: BuilderConfig) -> None:
        self._config = config

    def request_url(self, mbid: str) -> str:
        query = urlencode(
            {"artist_mbids": mbid, "algorithm": self._config.algorithm}
        )
        return f"{self._config.similar_artists_url}?{query}"

    def parse(
        self, payload: bytes, exclude_mbid: str | None = None
    ) -> list[SimilarArtist]:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed similarity payload: {exc}") from exc

        rows = self._rows(data)
        raw: list[tuple[str, str, float]] = []
        for row in rows:
            mbid = row.get(FIELD_MBID)
            if not mbid or mbid == exclude_mbid:
                continue
            score = row.get(FIELD_SCORE)
            if score is None:
                continue
            raw.append((mbid, row.get(FIELD_NAME) or "", float(score)))

        if not raw:
            return []

        # Upstream scores are unbounded co-occurrence counts, not a unit
        # interval. Normalise per-artist against the strongest neighbour so
        # w_sim in the cost function has a consistent scale across artists.
        highest = max(score for _, _, score in raw)
        if highest <= 0:
            return []

        neighbours = [
            SimilarArtist(mbid=mbid, name=name, score=score / highest)
            for mbid, name, score in raw
        ]
        # Deterministic order: strongest first, MBID breaks ties.
        neighbours.sort(key=lambda n: (-n.score, n.mbid))
        return neighbours[: self._config.max_neighbours_per_artist]

    @staticmethod
    def _rows(data: object) -> list[dict]:
        """The endpoint has returned both a bare array and a wrapped object
        across versions. Accept either rather than breaking on a reshuffle."""
        if isinstance(data, list):
            if data and isinstance(data[0], list):  # [[...]] nesting
                return [row for row in data[0] if isinstance(row, dict)]
            return [row for row in data if isinstance(row, dict)]
        if isinstance(data, dict):
            for key in ("similar_artists", "data", "results"):
                value = data.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
        return []
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_listenbrainz.py -v
```

Expected: 7 passed. **If `test_parses_recorded_real_response` fails, the `FIELD_*` constants do not match the recorded fixture — correct them from the fixture, not by changing the test.**

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/sources builder/tests/test_listenbrainz.py
git commit -m "feat(builder): add ListenBrainz similarity source with score normalisation"
```

---

## Task 5: Bootstrap list and per-artist stats

**Amended after Task 1.** The sitewide endpoint caps at 1,000 artists, so it can only *bootstrap* the snowball, and popularity must come from a per-artist endpoint. See `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md` §2–4.

**Files:**
- Create: `builder/src/artistpath_builder/sources/seeds.py`
- Test: `builder/tests/test_seeds.py`

**Interfaces:**
- Consumes: `BuilderConfig`, `BootstrapArtist`, `ArtistStats` (Task 2).
- Produces: `bootstrap_url(config, offset, count) -> str`, `parse_bootstrap_page(payload) -> list[BootstrapArtist]`, `artist_stats_url(config, mbid) -> str`, `parse_artist_stats(payload) -> ArtistStats | None`. Used by Tasks 6, 9 and 11.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_seeds.py`:

```python
import json

import pytest

from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.seeds import (
    artist_stats_url,
    bootstrap_url,
    parse_artist_stats,
    parse_bootstrap_page,
)


def test_bootstrap_url_carries_offset_and_count():
    url = bootstrap_url(BuilderConfig(), offset=900, count=100)
    assert "offset=900" in url
    assert "count=100" in url


def test_parses_recorded_real_bootstrap_response(seed_artists_payload):
    artists = parse_bootstrap_page(json.dumps(seed_artists_payload).encode())
    assert len(artists) > 0
    assert all(len(a.mbid) == 36 for a in artists)


def test_bootstrap_drops_artists_without_an_mbid():
    # Sitewide stats include artists MusicBrainz cannot identify. They cannot
    # be graph nodes, because similarity lookups are MBID-keyed.
    payload = json.dumps(
        {
            "payload": {
                "artists": [
                    {"artist_mbid": None, "artist_name": "Unknown"},
                    {"artist_mbid": "a" * 36, "artist_name": "Known"},
                ]
            }
        }
    ).encode()
    assert [a.name for a in parse_bootstrap_page(payload)] == ["Known"]


def test_empty_bootstrap_page_yields_nothing():
    assert parse_bootstrap_page(json.dumps({"payload": {"artists": []}}).encode()) == []


def test_stats_url_contains_mbid_and_listeners_path():
    url = artist_stats_url(BuilderConfig(), "a" * 36)
    assert "a" * 36 in url
    assert url.endswith("/listeners")


def test_parses_recorded_real_stats_response(artist_listeners_payload):
    stats = parse_artist_stats(json.dumps(artist_listeners_payload).encode())
    assert stats is not None
    assert stats.user_count > 0
    assert stats.listen_count > 0
    assert len(stats.mbid) == 36


def test_stats_prefers_user_count_over_listen_count(artist_listeners_payload):
    # Spec 4.1: popularity is distinct listeners, not plays. Guards against
    # someone "simplifying" these back into one field.
    stats = parse_artist_stats(json.dumps(artist_listeners_payload).encode())
    assert stats.user_count != stats.listen_count


def test_stats_for_unknown_artist_returns_none():
    payload = json.dumps({"payload": {"artist_mbid": None}}).encode()
    assert parse_artist_stats(payload) is None


def test_malformed_payload_raises():
    with pytest.raises(ValueError):
        parse_bootstrap_page(b"<html>")
    with pytest.raises(ValueError):
        parse_artist_stats(b"<html>")
```

Add the new fixture to `builder/tests/conftest.py`:

```python
@pytest.fixture
def artist_listeners_payload() -> dict:
    """The real per-artist stats response recorded in Task 1."""
    return json.loads((FIXTURES / "artist_listeners_sample.json").read_text())
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_seeds.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/sources/seeds.py`:

```python
"""Bootstrap artist list and per-artist popularity.

The sitewide stats endpoint caps hard at 1,000 artists while advertising
10.4M (Task 1 findings section 2), so it can only seed the snowball. Real
popularity comes per-artist from the listeners endpoint.

Field names are confirmed against responses recorded from the live API.
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import ArtistStats, BootstrapArtist

# Sitewide stats: payload.artists[]
FIELD_MBID = "artist_mbid"
FIELD_NAME = "artist_name"

# Per-artist stats: payload
FIELD_USERS = "total_user_count"
FIELD_LISTENS = "total_listen_count"

# The sitewide endpoint will not serve beyond this, whatever you ask for.
BOOTSTRAP_CEILING = 1000


def bootstrap_url(config: BuilderConfig, offset: int, count: int) -> str:
    query = urlencode({"count": count, "offset": offset, "range": "all_time"})
    return f"{config.sitewide_artists_url}?{query}"


def artist_stats_url(config: BuilderConfig, mbid: str) -> str:
    return f"{config.artist_stats_url}/{mbid}/listeners"


def _payload(raw: bytes, label: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed {label} payload: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"malformed {label} payload: expected object")
    return data.get("payload", {})


def parse_bootstrap_page(payload: bytes) -> list[BootstrapArtist]:
    rows = _payload(payload, "bootstrap").get("artists", [])
    return [
        BootstrapArtist(mbid=row[FIELD_MBID], name=row.get(FIELD_NAME) or "")
        for row in rows
        if row.get(FIELD_MBID)
    ]


def parse_artist_stats(payload: bytes) -> ArtistStats | None:
    """Returns None for artists the endpoint cannot identify."""
    body = _payload(payload, "artist stats")
    mbid = body.get("artist_mbid")
    if not mbid:
        return None
    return ArtistStats(
        mbid=mbid,
        name=body.get("artist_name") or "",
        user_count=int(body.get(FIELD_USERS) or 0),
        listen_count=int(body.get(FIELD_LISTENS) or 0),
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_seeds.py -v
```

Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/sources/seeds.py builder/tests/test_seeds.py builder/tests/conftest.py
git commit -m "feat(builder): add bootstrap list and per-artist popularity stats"
```

---

## Task 6: Snowball crawler

**Amended after Task 1.** The crawler no longer walks a fixed list — it discovers artists by expanding through the similarity graph, because no ranked list of 75k artists is obtainable (findings §2–3).

**Files:**
- Create: `builder/src/artistpath_builder/crawl.py`
- Test: `builder/tests/test_crawl.py`

**Interfaces:**
- Consumes: `BuilderConfig` (Task 2), `RawArchive` (Task 3), `SimilaritySource` (Task 4), `artist_stats_url` (Task 5).
- Produces: `Crawler(config, archive, source, fetcher, checkpoint_path)` with `crawl(bootstrap_mbids: list[str]) -> None`, `similar_key(mbid) -> str`, `stats_key(mbid) -> str`. Used by Tasks 9 and 11.

The crawler's only job is to fill the archive. It does not build a graph. That separation is what makes Task 9's replay test possible.

**Two archive keyspaces**, both filled per artist:
- `similar/{source}/{mbid}.json` — neighbours
- `stats/{mbid}.json` — popularity

**Frontier discipline:** neighbours are queued in the order the source returned them (strongest similarity first, Task 4 sorts deterministically). Breadth-first from the top-1000 bootstrap, so the graph grows outward through the best-connected artists first and stops at `target_artist_count`.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_crawl.py`:

```python
import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler, TransientFetchError
from artistpath_builder.sources.listenbrainz import ListenBrainzSource


A, B, C, D = ("a" * 36, "b" * 36, "c" * 36, "d" * 36)


def _similar(*mbids: str) -> bytes:
    rows = [
        {"artist_mbid": m, "name": m[0].upper(), "score": 100 - i}
        for i, m in enumerate(mbids)
    ]
    return json.dumps(rows).encode()


def _stats(mbid: str, users: int = 10) -> bytes:
    return json.dumps(
        {
            "payload": {
                "artist_mbid": mbid,
                "artist_name": mbid[0].upper(),
                "total_user_count": users,
                "total_listen_count": users * 7,
            }
        }
    ).encode()


class FakeFetcher:
    """Serves a small similarity graph: A -> B -> C -> D."""

    NEIGHBOURS = {A: (B,), B: (A, C), C: (B, D), D: (C,)}

    def __init__(self, fail_times: int = 0):
        self.calls: list[str] = []
        self.fail_times = fail_times

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        if self.fail_times > 0:
            self.fail_times -= 1
            raise TransientFetchError("429 slow down")
        for mbid, neighbours in self.NEIGHBOURS.items():
            if mbid in url:
                return _stats(mbid) if "/listeners" in url else _similar(*neighbours)
        return b"[]"


@pytest.fixture
def config():
    return BuilderConfig(requests_per_second=1000.0, checkpoint_every=1)


def _crawler(tmp_path, config, fetcher, name="checkpoint.json"):
    return Crawler(
        config=config,
        archive=LocalArchive(tmp_path / "archive"),
        source=ListenBrainzSource(config),
        fetcher=fetcher,
        checkpoint_path=tmp_path / name,
    )


def test_crawl_archives_both_similarity_and_stats(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert crawler.archive.has(crawler.similar_key(A))
    assert crawler.archive.has(crawler.stats_key(A))


def test_responses_are_archived_verbatim(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert crawler.archive.get(crawler.similar_key(A)) == _similar(B)


def test_snowball_discovers_artists_beyond_the_bootstrap(tmp_path, config):
    # The whole point of the amendment: starting from A alone must reach D.
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    assert crawler.discovered == {A, B, C, D}


def test_discovery_stops_at_target_count(tmp_path, config):
    cfg = BuilderConfig(
        requests_per_second=1000.0, checkpoint_every=1, target_artist_count=2
    )
    crawler = _crawler(tmp_path, cfg, FakeFetcher())
    crawler.crawl([A])
    assert len(crawler.discovered) == 2


def test_already_archived_artists_are_not_refetched(tmp_path, config):
    crawler = _crawler(tmp_path, config, FakeFetcher())
    crawler.crawl([A])
    before = len(crawler.fetcher.calls)

    resumed = _crawler(tmp_path, config, FakeFetcher(), name="checkpoint2.json")
    resumed.crawl([A])
    assert resumed.fetcher.calls == []
    assert before > 0


def test_transient_failures_are_retried(tmp_path, config):
    fetcher = FakeFetcher(fail_times=2)
    crawler = _crawler(tmp_path, config, fetcher)
    crawler.crawl([A])
    assert crawler.archive.has(crawler.similar_key(A))


def test_exhausted_retries_records_failure_and_continues(tmp_path):
    cfg = BuilderConfig(requests_per_second=1000.0, max_retries=2, checkpoint_every=1)
    crawler = _crawler(tmp_path, cfg, FakeFetcher(fail_times=999))
    crawler.crawl([A])
    # A single bad artist must not abort an 8-hour crawl.
    assert A in crawler.failures
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_crawl.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.crawl'`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/crawl.py`:

```python
"""Resumable, rate-limited crawler.

Fills the archive and nothing else. Graph assembly reads the archive, never
the network — which is what allows a rebuild to be proven offline (spec
section 9).
"""

from __future__ import annotations

import json
import logging
import time
from collections import deque
from collections.abc import Callable
from pathlib import Path

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.base import SimilaritySource
from artistpath_builder.sources.seeds import artist_stats_url

logger = logging.getLogger(__name__)

Fetcher = Callable[[str], bytes]


class TransientFetchError(RuntimeError):
    """Retryable: rate limiting, timeouts, 5xx."""


def http_fetcher(config: BuilderConfig) -> Fetcher:
    """The real network fetcher. Kept out of Crawler so tests inject a fake."""
    import httpx

    client = httpx.Client(
        headers={"User-Agent": config.user_agent},
        timeout=config.timeout_seconds,
        follow_redirects=True,
    )

    def fetch(url: str) -> bytes:
        try:
            response = client.get(url)
        except httpx.RequestError as exc:
            raise TransientFetchError(str(exc)) from exc
        if response.status_code == 429 or response.status_code >= 500:
            raise TransientFetchError(f"HTTP {response.status_code}")
        response.raise_for_status()
        return response.content

    return fetch


class Crawler:
    """Breadth-first snowball over the similarity graph.

    No ranked list of 75k artists exists (Task 1 findings section 2), so the
    frontier is built from the responses themselves.
    """

    def __init__(
        self,
        config: BuilderConfig,
        archive: RawArchive,
        source: SimilaritySource,
        fetcher: Fetcher,
        checkpoint_path: Path,
    ) -> None:
        self.config = config
        self.archive = archive
        self.source = source
        self.fetcher = fetcher
        self.checkpoint_path = Path(checkpoint_path)
        self.failures: list[str] = []
        state = self._load_checkpoint()
        self._done: set[str] = state["done"]
        self.discovered: set[str] = state["discovered"]

    def similar_key(self, mbid: str) -> str:
        return f"similar/{self.source.name}/{mbid}.json"

    def stats_key(self, mbid: str) -> str:
        return f"stats/{mbid}.json"

    def crawl(self, bootstrap_mbids: list[str]) -> None:
        queue: deque[str] = deque()
        for mbid in bootstrap_mbids:
            if mbid not in self.discovered:
                self.discovered.add(mbid)
                queue.append(mbid)
            elif mbid not in self._done:
                queue.append(mbid)

        processed = 0
        while queue and len(self.discovered) <= self.config.target_artist_count:
            mbid = queue.popleft()
            if mbid in self._done:
                continue

            payload = self._archive_or_fetch(
                self.similar_key(mbid), self.source.request_url(mbid), mbid
            )
            self._archive_or_fetch(
                self.stats_key(mbid), artist_stats_url(self.config, mbid), mbid
            )
            self._done.add(mbid)
            processed += 1

            if payload is not None:
                for neighbour in self._neighbours(payload, mbid):
                    if len(self.discovered) >= self.config.target_artist_count:
                        break
                    if neighbour not in self.discovered:
                        self.discovered.add(neighbour)
                        queue.append(neighbour)

            if processed % self.config.checkpoint_every == 0:
                self._save_checkpoint()
                logger.info(
                    "processed %d | discovered %d | queued %d",
                    processed,
                    len(self.discovered),
                    len(queue),
                )

        self._save_checkpoint()
        logger.info(
            "crawl finished: %d processed, %d discovered, %d failures",
            processed,
            len(self.discovered),
            len(self.failures),
        )

    def _neighbours(self, payload: bytes, mbid: str) -> list[str]:
        try:
            return [n.mbid for n in self.source.parse(payload, exclude_mbid=mbid)]
        except ValueError:
            logger.warning("unparseable similarity payload for %s", mbid)
            return []

    def _archive_or_fetch(self, key: str, url: str, mbid: str) -> bytes | None:
        existing = self.archive.get(key)
        if existing is not None:
            return existing
        payload = self._fetch_with_retries(url, mbid)
        if payload is not None:
            self.archive.put(key, payload)
        return payload

    def _fetch_with_retries(self, url: str, mbid: str) -> bytes | None:
        for attempt in range(self.config.max_retries):
            try:
                payload = self.fetcher(url)
            except TransientFetchError as exc:
                backoff = self.config.request_delay_seconds * (2**attempt)
                logger.warning("retry %d for %s: %s", attempt + 1, mbid, exc)
                time.sleep(backoff)
                continue
            time.sleep(self.config.request_delay_seconds)
            return payload

        logger.error("giving up on %s after %d attempts", mbid, self.config.max_retries)
        if mbid not in self.failures:
            self.failures.append(mbid)
        return None

    def _load_checkpoint(self) -> dict[str, set[str]]:
        if not self.checkpoint_path.is_file():
            return {"done": set(), "discovered": set()}
        state = json.loads(self.checkpoint_path.read_text())
        return {
            "done": set(state.get("done", [])),
            "discovered": set(state.get("discovered", [])),
        }

    def _save_checkpoint(self) -> None:
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(
            json.dumps(
                {"done": sorted(self._done), "discovered": sorted(self.discovered)},
                sort_keys=True,
            )
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_crawl.py -v
```

Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/crawl.py builder/tests/test_crawl.py
git commit -m "feat(builder): add resumable snowball crawler"
```

---

## Task 7: Graph assembly

Pure functions over in-memory data. No I/O.

**Files:**
- Create: `builder/src/artistpath_builder/graph.py`
- Test: `builder/tests/test_graph.py`

**Interfaces:**
- Consumes: `SimilarArtist`, `ArtistStats`, `EdgeType` (Task 2).
- Produces: `symmetrise(adjacency) -> dict[str, dict[str, float]]`, `largest_component(adjacency) -> set[str]`, `build_graph(adjacency, stats, edge_type) -> Graph`. `Graph` is a dataclass with `mbids: list[str]`, `names: list[str]`, `popularity: list[float]`, `offsets`, `neighbours`, `scores`, `edge_types` (numpy arrays). Used by Task 8.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_graph.py`:

```python
import numpy as np

from artistpath_builder.graph import build_graph, largest_component, symmetrise
from artistpath_builder.models import ArtistStats, EdgeType

A, B, C, D, E = ("a" * 36, "b" * 36, "c" * 36, "d" * 36, "e" * 36)


def _stats(*mbids_and_users):
    """Popularity is distinct listeners, not plays (spec 4.1)."""
    return [
        ArtistStats(mbid=m, name=m[0].upper(), user_count=u, listen_count=u * 7)
        for m, u in mbids_and_users
    ]


def test_symmetrise_mirrors_one_way_edges():
    # A one-way edge is a dead end: you can reach B from A but never return.
    adjacency = {A: {B: 0.8}, B: {}}
    result = symmetrise(adjacency)
    assert result[B][A] == 0.8


def test_symmetrise_keeps_the_stronger_score():
    adjacency = {A: {B: 0.3}, B: {A: 0.9}}
    result = symmetrise(adjacency)
    assert result[A][B] == 0.9
    assert result[B][A] == 0.9


def test_largest_component_discards_islands():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}, C: {D: 1.0}, D: {C: 1.0}, E: {}}
    assert largest_component(adjacency) == {A, B}


def test_largest_component_is_deterministic_when_sizes_tie():
    # Two components of equal size: the one containing the lowest MBID wins,
    # so the artifact is reproducible.
    adjacency = {A: {B: 1.0}, B: {A: 1.0}, C: {D: 1.0}, D: {C: 1.0}}
    assert largest_component(adjacency) == {A, B}


def test_build_graph_assigns_ids_in_mbid_order():
    adjacency = {B: {A: 1.0}, A: {B: 1.0}}
    graph = build_graph(adjacency, _stats((A, 10), (B, 20)), EdgeType.BEHAVIOURAL)
    assert graph.mbids == [A, B]


def test_csr_offsets_are_valid():
    adjacency = {A: {B: 1.0, C: 0.5}, B: {A: 1.0}, C: {A: 0.5}}
    graph = build_graph(
        adjacency, _stats((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    assert graph.offsets[0] == 0
    assert graph.offsets[-1] == len(graph.neighbours)
    assert len(graph.offsets) == len(graph.mbids) + 1
    assert np.all(np.diff(graph.offsets) >= 0)


def test_every_edge_is_reciprocated_in_csr():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}, C: {A: 0.4}, }
    graph = build_graph(
        symmetrise(adjacency), _stats((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    for src in range(len(graph.mbids)):
        for i in range(graph.offsets[src], graph.offsets[src + 1]):
            dst = int(graph.neighbours[i])
            back = graph.neighbours[graph.offsets[dst] : graph.offsets[dst + 1]]
            assert src in back


def test_neighbours_are_sorted_within_each_row():
    adjacency = {A: {B: 0.1, C: 0.9}, B: {A: 0.1}, C: {A: 0.9}}
    graph = build_graph(
        adjacency, _stats((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    row = graph.neighbours[graph.offsets[0] : graph.offsets[1]]
    assert list(row) == sorted(row)


def test_popularity_is_log_scaled_to_unit_range():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    graph = build_graph(adjacency, _stats((A, 1), (B, 1_000_000)), EdgeType.BEHAVIOURAL)
    assert min(graph.popularity) == 0.0
    assert max(graph.popularity) == 1.0


def test_edges_carry_the_source_edge_type():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    graph = build_graph(adjacency, _stats((A, 10), (B, 20)), EdgeType.BEHAVIOURAL)
    assert np.all(graph.edge_types == EdgeType.BEHAVIOURAL)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_graph.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.graph'`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/graph.py`:

```python
"""Graph assembly: symmetrise, prune to one component, emit CSR.

Pure functions over in-memory data. Determinism is a hard requirement here
(spec section 9) — every ordering decision is explicit.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

import numpy as np

from artistpath_builder.models import ArtistStats, EdgeType

Adjacency = dict[str, dict[str, float]]


@dataclass(slots=True)
class Graph:
    mbids: list[str]
    names: list[str]
    popularity: list[float]
    offsets: np.ndarray  # int32, length len(mbids) + 1
    neighbours: np.ndarray  # int32
    scores: np.ndarray  # float32
    edge_types: np.ndarray  # uint8

    @property
    def artist_count(self) -> int:
        return len(self.mbids)

    @property
    def edge_count(self) -> int:
        return int(self.neighbours.size)


def symmetrise(adjacency: Adjacency) -> Adjacency:
    """Mirror one-way edges, keeping the stronger score.

    Similarity is not mutual: A may list B without B listing A. Left alone,
    those become dead ends during pathfinding (spec section 3.1 step 4).
    """
    result: Adjacency = {node: dict(edges) for node, edges in adjacency.items()}
    for src, edges in adjacency.items():
        for dst, score in edges.items():
            result.setdefault(dst, {})
            result.setdefault(src, {})
            best = max(score, result[dst].get(src, 0.0), result[src].get(dst, 0.0))
            result[src][dst] = best
            result[dst][src] = best
    return result


def largest_component(adjacency: Adjacency) -> set[str]:
    """Return the biggest connected component.

    Keeping only this guarantees a path exists between any two artists the UI
    offers, so a "no path" result can only ever come from user exclusions
    (spec section 3.1 step 5). Ties break on lowest MBID for determinism.
    """
    unvisited = set(adjacency)
    best: set[str] = set()

    for start in sorted(adjacency):
        if start not in unvisited:
            continue
        component: set[str] = set()
        queue = deque([start])
        unvisited.discard(start)
        while queue:
            node = queue.popleft()
            component.add(node)
            for neighbour in adjacency.get(node, {}):
                if neighbour in unvisited:
                    unvisited.discard(neighbour)
                    queue.append(neighbour)
        if len(component) > len(best):
            best = component
    return best


def _log_scaled(listens: list[int]) -> list[float]:
    """Log-scale listen counts to 0-1 (spec section 4.1).

    Raw counts are power-law distributed; a linear scale would make every
    artist outside the top few hundred indistinguishable.
    """
    logs = [math.log1p(max(0, n)) for n in listens]
    low, high = min(logs), max(logs)
    span = high - low
    if span == 0:
        return [0.0] * len(logs)
    return [(value - low) / span for value in logs]


def build_graph(
    adjacency: Adjacency,
    stats: list[ArtistStats],
    edge_type: EdgeType,
) -> Graph:
    """Assemble CSR arrays. IDs are assigned in sorted-MBID order."""
    stats_by_mbid = {record.mbid: record for record in stats}
    mbids = sorted(set(adjacency) & set(stats_by_mbid))
    index = {mbid: i for i, mbid in enumerate(mbids)}

    names = [stats_by_mbid[m].name for m in mbids]
    # Distinct listeners, not plays — see spec section 4.1.
    popularity = _log_scaled([stats_by_mbid[m].user_count for m in mbids])

    offsets = np.zeros(len(mbids) + 1, dtype=np.int32)
    neighbours: list[int] = []
    scores: list[float] = []

    for i, mbid in enumerate(mbids):
        row = [
            (index[dst], score)
            for dst, score in adjacency[mbid].items()
            if dst in index
        ]
        row.sort(key=lambda pair: pair[0])  # deterministic within-row order
        for dst_id, score in row:
            neighbours.append(dst_id)
            scores.append(score)
        offsets[i + 1] = len(neighbours)

    return Graph(
        mbids=mbids,
        names=names,
        popularity=popularity,
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
        edge_types=np.full(len(neighbours), int(edge_type), dtype=np.uint8),
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_graph.py -v
```

Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/graph.py builder/tests/test_graph.py
git commit -m "feat(builder): add graph assembly with symmetrisation and component pruning"
```

---

## Task 8: Binary artifact serialisation

**Files:**
- Create: `builder/src/artistpath_builder/artifact.py`
- Test: `builder/tests/test_artifact.py`

**Interfaces:**
- Consumes: `Graph` (Task 7).
- Produces: `serialise(graph) -> bytes` and `deserialise(payload) -> Graph`. Used by Tasks 9, 10, 11, and by the API in a later plan.

**Format** (all little-endian):

| Offset | Type | Meaning |
|---|---|---|
| 0 | `char[4]` | magic `APG1` |
| 4 | `uint32` | format version (1) |
| 8 | `uint32` | artist count `N` |
| 12 | `uint32` | edge count `E` |
| 16 | `uint64` | metadata JSON length `J` |
| 24 | `int32[N+1]` | offsets |
| … | `int32[E]` | neighbours |
| … | `float32[E]` | scores |
| … | `uint8[E]` | edge types |
| … | `char[J]` | metadata JSON: `{"mbids":[…],"names":[…],"popularity":[…]}` |

- [ ] **Step 1: Write the failing test**

`builder/tests/test_artifact.py`:

```python
import numpy as np
import pytest

from artistpath_builder.artifact import MAGIC, deserialise, serialise
from artistpath_builder.graph import build_graph
from artistpath_builder.models import ArtistStats, EdgeType

A, B, C = ("a" * 36, "b" * 36, "c" * 36)


@pytest.fixture
def graph():
    adjacency = {A: {B: 1.0, C: 0.5}, B: {A: 1.0}, C: {A: 0.5}}
    stats = [
        ArtistStats(mbid=A, name="Alpha", user_count=100, listen_count=700),
        ArtistStats(mbid=B, name="Beta", user_count=50, listen_count=350),
        ArtistStats(mbid=C, name="Gamma", user_count=10, listen_count=70),
    ]
    return build_graph(adjacency, stats, EdgeType.BEHAVIOURAL)


def test_artifact_starts_with_magic(graph):
    assert serialise(graph)[:4] == MAGIC


def test_round_trip_preserves_everything(graph):
    restored = deserialise(serialise(graph))
    assert restored.mbids == graph.mbids
    assert restored.names == graph.names
    assert restored.popularity == pytest.approx(graph.popularity)
    assert np.array_equal(restored.offsets, graph.offsets)
    assert np.array_equal(restored.neighbours, graph.neighbours)
    assert np.array_equal(restored.scores, graph.scores)
    assert np.array_equal(restored.edge_types, graph.edge_types)


def test_serialisation_is_byte_identical_across_runs(graph):
    # The whole replay guarantee (spec section 9) rests on this.
    assert serialise(graph) == serialise(graph)


def test_dtypes_survive_the_round_trip(graph):
    restored = deserialise(serialise(graph))
    assert restored.offsets.dtype == np.int32
    assert restored.neighbours.dtype == np.int32
    assert restored.scores.dtype == np.float32
    assert restored.edge_types.dtype == np.uint8


def test_bad_magic_is_rejected(graph):
    corrupted = b"XXXX" + serialise(graph)[4:]
    with pytest.raises(ValueError, match="magic"):
        deserialise(corrupted)


def test_truncated_payload_is_rejected(graph):
    with pytest.raises(ValueError):
        deserialise(serialise(graph)[:20])
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_artifact.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.artifact'`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/artifact.py`:

```python
"""Binary CSR artifact.

One immutable file, versioned in S3, loaded into memory at API boot. Never a
database (spec section 3). Byte-identical output for identical input is a
hard requirement — it is how archive replay is verified.
"""

from __future__ import annotations

import json
import struct

import numpy as np

from artistpath_builder.graph import Graph

MAGIC = b"APG1"
FORMAT_VERSION = 1
_HEADER = struct.Struct("<4sIIIQ")


def serialise(graph: Graph) -> bytes:
    metadata = json.dumps(
        {
            "mbids": graph.mbids,
            "names": graph.names,
            "popularity": graph.popularity,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    header = _HEADER.pack(
        MAGIC,
        FORMAT_VERSION,
        graph.artist_count,
        graph.edge_count,
        len(metadata),
    )

    return b"".join(
        [
            header,
            graph.offsets.astype("<i4").tobytes(),
            graph.neighbours.astype("<i4").tobytes(),
            graph.scores.astype("<f4").tobytes(),
            graph.edge_types.astype("<u1").tobytes(),
            metadata,
        ]
    )


def deserialise(payload: bytes) -> Graph:
    if len(payload) < _HEADER.size:
        raise ValueError("artifact truncated: shorter than header")

    magic, version, artist_count, edge_count, metadata_length = _HEADER.unpack_from(
        payload
    )
    if magic != MAGIC:
        raise ValueError(f"bad magic: expected {MAGIC!r}, got {magic!r}")
    if version != FORMAT_VERSION:
        raise ValueError(f"unsupported artifact version {version}")

    cursor = _HEADER.size

    def take(count: int, dtype: str, itemsize: int) -> np.ndarray:
        nonlocal cursor
        end = cursor + count * itemsize
        if end > len(payload):
            raise ValueError("artifact truncated: array extends past end of file")
        array = np.frombuffer(payload[cursor:end], dtype=dtype)
        cursor = end
        return array

    offsets = take(artist_count + 1, "<i4", 4)
    neighbours = take(edge_count, "<i4", 4)
    scores = take(edge_count, "<f4", 4)
    edge_types = take(edge_count, "<u1", 1)

    if cursor + metadata_length > len(payload):
        raise ValueError("artifact truncated: metadata extends past end of file")
    metadata = json.loads(payload[cursor : cursor + metadata_length])

    return Graph(
        mbids=metadata["mbids"],
        names=metadata["names"],
        popularity=metadata["popularity"],
        offsets=offsets,
        neighbours=neighbours,
        scores=scores,
        edge_types=edge_types,
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_artifact.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/artifact.py builder/tests/test_artifact.py
git commit -m "feat(builder): add deterministic binary CSR artifact format"
```

---

## Task 9: Offline replay determinism

The acceptance test named in spec §9. It proves the archive is genuinely sufficient.

**Files:**
- Create: `builder/src/artistpath_builder/pipeline.py`
- Test: `builder/tests/test_replay.py`

**Interfaces:**
- Consumes: everything from Tasks 3–8.
- Produces: `build_from_archive(config, archive, source) -> Graph`. Popularity is read from archived `stats/` responses, so no seeds file is needed. Used by Task 11.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_replay.py`:

```python
import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import serialise
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler
from artistpath_builder.models import ArtistStats
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C = ("a" * 36, "b" * 36, "c" * 36)

SIMILAR = {
    A: [(B, "Beta", 10)],
    B: [(A, "Alpha", 10), (C, "Gamma", 5)],
    C: [(B, "Beta", 5)],
}

USERS = {A: 300, B: 200, C: 100}
NAMES = {A: "Alpha", B: "Beta", C: "Gamma"}


def _similar_body(mbid: str) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": n, "name": name, "score": score}
            for n, name, score in SIMILAR[mbid]
        ]
    ).encode()


def _stats_body(mbid: str) -> bytes:
    return json.dumps(
        {
            "payload": {
                "artist_mbid": mbid,
                "artist_name": NAMES[mbid],
                "total_user_count": USERS[mbid],
                "total_listen_count": USERS[mbid] * 7,
            }
        }
    ).encode()


class RecordedFetcher:
    def __init__(self):
        self.calls = 0

    def __call__(self, url: str) -> bytes:
        self.calls += 1
        for mbid in SIMILAR:
            if mbid in url:
                return _stats_body(mbid) if "/listeners" in url else _similar_body(mbid)
        return b"[]"


class ExplodingFetcher:
    """Stands in for having no network at all."""

    def __call__(self, url: str) -> bytes:
        raise AssertionError(f"network was used during replay: {url}")


@pytest.fixture
def config():
    return BuilderConfig(requests_per_second=1000.0)


def test_rebuild_from_archive_is_byte_identical_with_no_network(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)

    # First build: crawls the "network", filling the archive.
    fetcher = RecordedFetcher()
    Crawler(
        config=config,
        archive=archive,
        source=source,
        fetcher=fetcher,
        checkpoint_path=tmp_path / "checkpoint.json",
    ).crawl([A])
    # Two calls per artist (similarity + stats), three artists discovered.
    assert fetcher.calls == 6

    first = serialise(build_from_archive(config, archive, source))

    # Second build: same archive, a fetcher that raises if touched.
    Crawler(
        config=config,
        archive=archive,
        source=source,
        fetcher=ExplodingFetcher(),
        checkpoint_path=tmp_path / "checkpoint2.json",
    ).crawl([A])

    second = serialise(build_from_archive(config, archive, source))

    assert first == second


def _seed_archive(archive, source, mbids):
    for mbid in mbids:
        archive.put(f"similar/{source.name}/{mbid}.json", _similar_body(mbid))
        archive.put(f"stats/{mbid}.json", _stats_body(mbid))


def test_replay_produces_a_connected_graph(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source)
    assert graph.mbids == [A, B, C]
    assert graph.edge_count > 0


def test_popularity_comes_from_archived_user_counts(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source)
    # A has the most distinct listeners, C the fewest (spec 4.1).
    assert graph.popularity[graph.mbids.index(A)] == max(graph.popularity)
    assert graph.popularity[graph.mbids.index(C)] == min(graph.popularity)


def test_artists_missing_from_the_archive_are_skipped(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B])
    # C is absent — a crawl failure. The build must not raise.
    graph = build_from_archive(config, archive, source)
    assert C not in graph.mbids


def test_artist_without_archived_stats_is_skipped(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B])
    archive.put(f"similar/{source.name}/{C}.json", _similar_body(C))
    # C has neighbours but no popularity, so it cannot be routed through.
    graph = build_from_archive(config, archive, source)
    assert C not in graph.mbids
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_replay.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.pipeline'`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/pipeline.py`:

```python
"""Assemble a graph from the archive alone.

This function must never touch the network. Task 9's test enforces that by
injecting a fetcher that raises.
"""

from __future__ import annotations

import logging

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.graph import Adjacency, Graph, build_graph, largest_component, symmetrise
from artistpath_builder.models import ArtistStats
from artistpath_builder.sources.base import SimilaritySource
from artistpath_builder.sources.seeds import parse_artist_stats

logger = logging.getLogger(__name__)


def _archived_stats(archive: RawArchive) -> dict[str, ArtistStats]:
    """Popularity for every artist whose stats response was archived."""
    stats: dict[str, ArtistStats] = {}
    for key in archive.keys():
        if not key.startswith("stats/"):
            continue
        payload = archive.get(key)
        if payload is None:
            continue
        try:
            record = parse_artist_stats(payload)
        except ValueError:
            logger.warning("unparseable stats payload at %s", key)
            continue
        if record is not None:
            stats[record.mbid] = record
    return stats


def build_from_archive(
    config: BuilderConfig,
    archive: RawArchive,
    source: SimilaritySource,
) -> Graph:
    """Assemble a graph from archived responses alone. Never touches the network."""
    stats = _archived_stats(archive)
    # An artist with no popularity cannot be routed through, so it is not a node.
    known = set(stats)
    adjacency: Adjacency = {}
    missing = 0

    for mbid in sorted(known):
        payload = archive.get(f"similar/{source.name}/{mbid}.json")
        if payload is None:
            missing += 1
            continue
        neighbours = source.parse(payload, exclude_mbid=mbid)
        adjacency[mbid] = {n.mbid: n.score for n in neighbours if n.mbid in known}

    if missing:
        logger.warning("%d artists had no archived similarity response", missing)

    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)
    logger.info(
        "largest component: %d of %d artists", len(keep), len(adjacency)
    )

    pruned: Adjacency = {
        node: {dst: score for dst, score in edges.items() if dst in keep}
        for node, edges in adjacency.items()
        if node in keep
    }

    return build_graph(pruned, list(stats.values()), source.edge_type)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_replay.py -v
```

Expected: 5 passed

- [ ] **Step 5: Run the whole suite**

```bash
cd builder && uv run --extra dev pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add builder/src/artistpath_builder/pipeline.py builder/tests/test_replay.py
git commit -m "feat(builder): add offline archive replay with byte-identical guarantee"
```

---

## Task 10: Fixture graph export

The ~500-artist fixture (spec §6.1) that lets the API and UI be developed and tested without the 80MB artifact.

**Files:**
- Create: `builder/src/artistpath_builder/fixture.py`
- Test: `builder/tests/test_fixture.py`

**Interfaces:**
- Consumes: `Graph` (Task 7), `largest_component` (Task 7).
- Produces: `extract_fixture(graph, size, seed_mbid) -> Graph`. Its serialised output is committed to `tests/fixtures/graph-fixture.bin` and consumed by the API plan.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_fixture.py`:

```python
import numpy as np
import pytest

from artistpath_builder.fixture import extract_fixture
from artistpath_builder.graph import build_graph, symmetrise
from artistpath_builder.models import ArtistStats, EdgeType


def _ring(n: int):
    """A connected ring of n artists, so any subset extraction has options."""
    mbids = [f"{i:036d}" for i in range(n)]
    adjacency = {
        m: {mbids[(i + 1) % n]: 0.9, mbids[(i - 1) % n]: 0.8}
        for i, m in enumerate(mbids)
    }
    stats = [
        ArtistStats(
            mbid=m, name=f"Artist {i}", user_count=(n - i) * 100, listen_count=(n - i) * 700
        )
        for i, m in enumerate(mbids)
    ]
    return build_graph(symmetrise(adjacency), stats, EdgeType.BEHAVIOURAL), mbids


def test_fixture_has_requested_size():
    graph, mbids = _ring(50)
    fixture = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    assert fixture.artist_count == 10


def test_fixture_is_connected():
    # A disconnected fixture would make downstream pathfinding tests
    # fail for reasons that have nothing to do with the code under test.
    graph, mbids = _ring(50)
    fixture = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    seen = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for i in range(fixture.offsets[node], fixture.offsets[node + 1]):
            neighbour = int(fixture.neighbours[i])
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    assert len(seen) == fixture.artist_count


def test_fixture_edges_stay_within_bounds():
    graph, mbids = _ring(50)
    fixture = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    assert np.all(fixture.neighbours < fixture.artist_count)
    assert np.all(fixture.neighbours >= 0)


def test_fixture_is_deterministic():
    graph, mbids = _ring(50)
    a = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    b = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    assert a.mbids == b.mbids


def test_requesting_more_than_available_returns_everything():
    graph, mbids = _ring(5)
    fixture = extract_fixture(graph, size=100, seed_mbid=mbids[0])
    assert fixture.artist_count == 5


def test_unknown_seed_raises():
    graph, _ = _ring(5)
    with pytest.raises(KeyError):
        extract_fixture(graph, size=3, seed_mbid="z" * 36)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_fixture.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.fixture'`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/fixture.py`:

```python
"""Extract a small connected sub-graph for local development and tests.

Spec section 6.1: a fresh clone must run without the 80MB artifact, and the
same fixture backs the pathfinding tests.
"""

from __future__ import annotations

from collections import deque

import numpy as np

from artistpath_builder.graph import Graph


def extract_fixture(graph: Graph, size: int, seed_mbid: str) -> Graph:
    """Breadth-first expansion from a seed, so the result is always connected."""
    try:
        start = graph.mbids.index(seed_mbid)
    except ValueError as exc:
        raise KeyError(f"seed artist not in graph: {seed_mbid}") from exc

    chosen: list[int] = []
    seen = {start}
    queue = deque([start])
    while queue and len(chosen) < size:
        node = queue.popleft()
        chosen.append(node)
        row = graph.neighbours[graph.offsets[node] : graph.offsets[node + 1]]
        for neighbour in sorted(int(n) for n in row):  # deterministic
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)

    keep = sorted(chosen)
    remap = {old: new for new, old in enumerate(keep)}

    offsets = np.zeros(len(keep) + 1, dtype=np.int32)
    neighbours: list[int] = []
    scores: list[float] = []
    edge_types: list[int] = []

    for new_id, old_id in enumerate(keep):
        for i in range(graph.offsets[old_id], graph.offsets[old_id + 1]):
            old_neighbour = int(graph.neighbours[i])
            if old_neighbour in remap:
                neighbours.append(remap[old_neighbour])
                scores.append(float(graph.scores[i]))
                edge_types.append(int(graph.edge_types[i]))
        offsets[new_id + 1] = len(neighbours)

    return Graph(
        mbids=[graph.mbids[i] for i in keep],
        names=[graph.names[i] for i in keep],
        popularity=[graph.popularity[i] for i in keep],
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
        edge_types=np.asarray(edge_types, dtype=np.uint8),
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_fixture.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/fixture.py builder/tests/test_fixture.py
git commit -m "feat(builder): add connected fixture sub-graph extraction"
```

---

## Task 11: CLI and the real run

**Files:**
- Create: `builder/src/artistpath_builder/cli.py`
- Create: `builder/README.md`
- Test: `builder/tests/test_cli.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `artistpath-build bootstrap|crawl|build|fixture` commands. `build` writes `graph-{version}.bin`, consumed by the API plan.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_cli.py`:

```python
import json

import pytest

from artistpath_builder.cli import main

A, B = ("a" * 36, "b" * 36)


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def _write_archive(archive_dir):
    similar = archive_dir / "similar" / "listenbrainz"
    stats = archive_dir / "stats"
    similar.mkdir(parents=True)
    stats.mkdir(parents=True)
    for mbid, other, name, users in [(A, B, "Alpha", 100), (B, A, "Beta", 50)]:
        (similar / f"{mbid}.json").write_bytes(
            json.dumps([{"artist_mbid": other, "name": "X", "score": 10}]).encode()
        )
        (stats / f"{mbid}.json").write_bytes(
            json.dumps(
                {
                    "payload": {
                        "artist_mbid": mbid,
                        "artist_name": name,
                        "total_user_count": users,
                        "total_listen_count": users * 7,
                    }
                }
            ).encode()
        )


def test_build_writes_an_artifact(tmp_path):
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"

    exit_code = main(
        ["build", "--archive-dir", str(archive_dir), "--out", str(out)]
    )
    assert exit_code == 0
    assert out.stat().st_size > 0


def test_build_needs_no_seeds_file(tmp_path):
    # Popularity lives in the archive; there is no separate seeds artifact
    # to drift out of sync with it.
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"
    assert main(["build", "--archive-dir", str(archive_dir), "--out", str(out)]) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_cli.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artistpath_builder.cli'`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/cli.py`:

```python
"""Builder entry points.

    artistpath-build bootstrap --out bootstrap.json
    artistpath-build crawl     --bootstrap bootstrap.json --archive-dir ./archive
    artistpath-build build     --archive-dir ./archive --out graph-v1.bin
    artistpath-build fixture   --graph graph-v1.bin --out fixture.bin --size 500

`build` needs no seeds file: popularity is read from the archived stats
responses, so there is no second artifact to drift out of sync.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from artistpath_builder.archive import LocalArchive, S3Archive
from artistpath_builder.artifact import deserialise, serialise
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler, http_fetcher
from artistpath_builder.fixture import extract_fixture
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.sources.seeds import (
    BOOTSTRAP_CEILING,
    bootstrap_url,
    parse_bootstrap_page,
)

PAGE_SIZE = 1000


def _archive(args):
    if args.s3_bucket:
        return S3Archive(args.s3_bucket, args.s3_prefix)
    return LocalArchive(Path(args.archive_dir))


def cmd_bootstrap(args) -> int:
    """Fetch the top artists that seed the snowball.

    The sitewide endpoint serves at most BOOTSTRAP_CEILING artists whatever
    is requested (Task 1 findings section 2), so this is deliberately small.
    """
    config = BuilderConfig()
    fetch = http_fetcher(config)
    artists = []
    offset = 0
    while offset < BOOTSTRAP_CEILING:
        page = parse_bootstrap_page(
            fetch(bootstrap_url(config, offset=offset, count=PAGE_SIZE))
        )
        if not page:
            break
        artists.extend(page)
        offset += PAGE_SIZE

    Path(args.out).write_text(json.dumps([a.__dict__ for a in artists], sort_keys=True))
    logging.info("wrote %d bootstrap artists to %s", len(artists), args.out)
    return 0


def cmd_crawl(args) -> int:
    config = BuilderConfig()
    bootstrap = json.loads(Path(args.bootstrap).read_text())
    crawler = Crawler(
        config=config,
        archive=_archive(args),
        source=ListenBrainzSource(config),
        fetcher=http_fetcher(config),
        checkpoint_path=Path(args.checkpoint),
    )
    crawler.crawl([row["mbid"] for row in bootstrap])
    if crawler.failures:
        logging.warning("%d artists failed permanently", len(crawler.failures))
    return 0


def cmd_build(args) -> int:
    config = BuilderConfig()
    graph = build_from_archive(config, _archive(args), ListenBrainzSource(config))
    payload = serialise(graph)
    Path(args.out).write_bytes(payload)
    logging.info(
        "wrote %s: %d artists, %d edges, %.1f MB",
        args.out,
        graph.artist_count,
        graph.edge_count,
        len(payload) / 1e6,
    )
    return 0


def cmd_fixture(args) -> int:
    graph = deserialise(Path(args.graph).read_bytes())
    seed = args.seed_mbid or graph.mbids[0]
    fixture = extract_fixture(graph, size=args.size, seed_mbid=seed)
    Path(args.out).write_bytes(serialise(fixture))
    logging.info("wrote fixture: %d artists", fixture.artist_count)
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="artistpath-build")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_archive_args(p):
        p.add_argument("--archive-dir", default="./archive")
        p.add_argument("--s3-bucket", default=None)
        p.add_argument("--s3-prefix", default="raw")

    p_bootstrap = sub.add_parser("bootstrap")
    p_bootstrap.add_argument("--out", required=True)
    p_bootstrap.set_defaults(func=cmd_bootstrap)

    p_crawl = sub.add_parser("crawl")
    p_crawl.add_argument("--bootstrap", required=True)
    p_crawl.add_argument("--checkpoint", default="./checkpoint.json")
    add_archive_args(p_crawl)
    p_crawl.set_defaults(func=cmd_crawl)

    p_build = sub.add_parser("build")
    p_build.add_argument("--out", required=True)
    add_archive_args(p_build)
    p_build.set_defaults(func=cmd_build)

    p_fixture = sub.add_parser("fixture")
    p_fixture.add_argument("--graph", required=True)
    p_fixture.add_argument("--out", required=True)
    p_fixture.add_argument("--size", type=int, default=500)
    p_fixture.add_argument("--seed-mbid", default=None)
    p_fixture.set_defaults(func=cmd_fixture)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_cli.py -v
```

Expected: 2 passed

- [ ] **Step 5: Do a small real run**

Prove the pipeline end to end on real data before committing to an overnight crawl.

Note: on Windows, Git Bash's `/tmp` is not the path Windows Python resolves — use a Windows-visible directory such as `./scratch/` for these files.

```bash
cd builder
mkdir -p scratch
uv run artistpath-build bootstrap --out scratch/bootstrap.json
python -c "import json,pathlib; p=pathlib.Path('scratch/bootstrap.json'); rows=json.loads(p.read_text())[:20]; pathlib.Path('scratch/bootstrap-20.json').write_text(json.dumps(rows))"
```

Crawl with a small discovery cap, so the snowball is exercised without a long run:

```bash
ARTISTPATH_TARGET=200 uv run artistpath-build crawl \
  --bootstrap scratch/bootstrap-20.json \
  --archive-dir scratch/archive \
  --checkpoint scratch/cp.json
uv run artistpath-build build --archive-dir scratch/archive --out scratch/graph-small.bin
```

(If `BuilderConfig` does not yet read `target_artist_count` from the environment, temporarily edit the default to 200 for this run and restore it afterwards.)

**Record and report three numbers before going further:**

1. **Component retention** — artists kept after largest-component pruning, as a percentage. Below ~80% means the similarity data is sparser than assumed.
2. **Discovery rate** — distinct artists discovered per artist crawled. This is what determines whether 75,000 is reachable at all, and it is the number the Task 1 findings flagged as the real remaining unknown.
3. **Mean edge count per artist** after pruning.

Stop and report regardless of the outcome. These numbers decide whether the full crawl is worth 8 hours.

- [ ] **Step 6: Verify replay against real archived data**

```bash
cd builder
uv run artistpath-build build --archive-dir scratch/archive --out scratch/graph-small-2.bin
cmp scratch/graph-small.bin scratch/graph-small-2.bin && echo "BYTE IDENTICAL"
```

Expected: `BYTE IDENTICAL`. This is the replay guarantee proven against real archived data rather than fixtures.

- [ ] **Step 7: Write the README**

`builder/README.md` documenting: what the builder produces, the four commands with real examples, that the crawl is resumable and safe to interrupt, and that the archive must never be deleted because it is the rebuild guarantee.

- [ ] **Step 8: Commit**

```bash
git add builder/
git commit -m "feat(builder): add CLI and verify pipeline on real data"
```

- [ ] **Step 9: STOP and report before the full crawl**

The full 75k crawl takes hours and hits a third-party service. Report the small-run results — artist retention, edge density, projected runtime and artifact size — and get a human go-ahead before running it.

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| §3.1 acquire similarity data behind an interface | 1, 4 |
| §3.1 step 2 archive raw responses | 3, 6 |
| §3.1 step 3 select top ~75k by listens | 5, 11 |
| §3.1 step 4 symmetrise | 7 |
| §3.1 step 5 largest connected component | 7, 9 |
| §3.1 step 6 emit CSR + artist table + name index | 7, 8 |
| §3.1 typed edges | 2, 7, 8 |
| §3.1 builder takes a list of sources | 4 (protocol), 11 (wiring) |
| §6.1 ~500-artist fixture graph | 10 |
| §8.1 prove the data first | 1 (gate), 11 step 9 (gate) |
| §9 builder tests | 2–10 |
| §9 archive replay produces byte-identical graph | 8, 9 |
| Determinism | 7, 8, 9, 10 |

**Deferred to the API plan, deliberately:** the normalised name index for autocomplete. It is listed in §3.1 step 6, but it is a search concern whose shape depends on the autocomplete implementation, and the artifact's metadata JSON already carries every name. Building it now would be guessing at requirements. **This is a known gap — carry it into the API plan's first task.**

**Placeholder scan:** no TBDs. The two places carrying real uncertainty — the `FIELD_*` constants in `listenbrainz.py`/`seeds.py` and the `algorithm` string in `config.py` — are resolved by Task 1 before any code depends on them, and are flagged in-code with instructions.

**Type consistency:** `SimilarArtist(mbid, name, score)`, `BootstrapArtist(mbid, name)`, `ArtistStats(mbid, name, user_count, listen_count, disambiguation="")`, and `Graph(mbids, names, popularity, offsets, neighbours, scores, edge_types)` are used with identical names and types in Tasks 2, 4, 5, 7, 8, 9, 10, 11. `similar_key()` and `stats_key()` are defined in Task 6 and their exact string forms (`similar/{source.name}/{mbid}.json`, `stats/{mbid}.json`) are reused in Tasks 9 and 11.

**Known deviation from spec §3.1 step 6 — disambiguation.** The artist table does not carry disambiguation in this plan. The data exists free (the similarity response's `comment` field, e.g. "1980s–1990s US grunge band"), but it describes *neighbours*, so populating an artist's own disambiguation means harvesting it from other artists' responses. That is extra complexity for a UI nicety that only matters when two artists share a name, and §2.1 says path quality comes first. **Deferred, not dropped:** the archive retains every `comment`, so adding it later needs no re-crawl. Carry into Plan 2.

---

## What comes after this plan

Two further plans, written only once this one's data findings are in:

**Plan 2 — Path engine and API.** Loads the artifact into typed arrays; bidirectional Dijkstra; base cost function tuned and **frozen**; then the two bypass signals and progressive floor relaxation tuned on top of the frozen baseline (spec §4.3). Fastify endpoints, clip resolution, DynamoDB cache.

**Plan 3 — Web app and infrastructure.** React + Vite front end, CDK stack, App Runner, GitHub Actions with OIDC.

They are deliberately not written yet. Path quality tuning depends on how good the real graph turns out to be, and the spec's §2.1 makes that quality the thing everything else is subordinate to.
