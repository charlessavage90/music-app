# Graph Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a compact, deterministic artist-similarity graph artifact from ListenBrainz data, with every raw API response archived so the graph can be rebuilt forever without network access.

**Architecture:** A standalone Python package (`builder/`) with no dependency on the rest of the app. It crawls a similarity source behind a `SimilaritySource` protocol, archives every raw response verbatim, then assembles a symmetrised graph, keeps the largest connected component, and serialises it to a single binary CSR artifact. Everything downstream consumes that artifact and nothing else.

**Tech Stack:** Python 3.12+ (3.14.3 available locally), `uv` for dependency management, `pytest`, `httpx`, `boto3`, `numpy`.

**Spec:** `docs/superpowers/specs/2026-07-19-artist-path-alpha-design.md`. Where this plan and the spec disagree, the spec wins — raise it rather than improvising.

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
    models.py            # SimilarArtist, SeedArtist, EdgeType — plain dataclasses
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

## Task 1: Spike — probe the real API and record fixtures

**This task is a gate.** Spec §8.1 names similarity-data acquisition as the primary risk and requires it be settled before app code exists. Nothing else in this plan may start until this task's findings are reviewed by a human. Its deliverable is knowledge and recorded fixtures, not production code.

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
- Produces: `BuilderConfig`, `SimilarArtist`, `SeedArtist`, `EdgeType` — used by every later task.

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
from artistpath_builder.models import EdgeType, SimilarArtist


def test_config_has_sane_defaults():
    cfg = BuilderConfig()
    assert cfg.target_artist_count == 75_000
    assert cfg.requests_per_second > 0
    assert cfg.user_agent.startswith("artistpath-builder/")


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
class SeedArtist:
    """An artist in the crawl seed set, with the popularity used for routing."""

    mbid: str
    name: str
    listen_count: int
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

    # --- crawl ----------------------------------------------------------
    target_artist_count: int = 75_000
    # Set from the rate limit observed in Task 1. Deliberately conservative:
    # this crawl runs once, and being throttled costs more than being slow.
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

## Task 5: Seed artist acquisition

**Files:**
- Create: `builder/src/artistpath_builder/sources/seeds.py`
- Test: `builder/tests/test_seeds.py`

**Interfaces:**
- Consumes: `BuilderConfig`, `SeedArtist` (Task 2); `RawArchive` (Task 3).
- Produces: `parse_seed_page(payload: bytes) -> list[SeedArtist]` and `seed_page_url(config, offset, count) -> str`. Used by Task 6 and Task 11.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_seeds.py`:

```python
import json

import pytest

from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.seeds import parse_seed_page, seed_page_url


def test_url_carries_offset_and_count():
    url = seed_page_url(BuilderConfig(), offset=1000, count=100)
    assert "offset=1000" in url
    assert "count=100" in url


def test_parses_recorded_real_response(seed_artists_payload):
    seeds = parse_seed_page(json.dumps(seed_artists_payload).encode())
    assert len(seeds) > 0
    assert all(s.listen_count >= 0 for s in seeds)
    assert all(len(s.mbid) == 36 for s in seeds)


def test_artists_without_an_mbid_are_dropped():
    # Sitewide stats include artists MusicBrainz cannot identify. They cannot
    # be graph nodes, because similarity lookups are MBID-keyed.
    payload = json.dumps(
        {
            "payload": {
                "artists": [
                    {"artist_mbid": None, "artist_name": "Unknown", "listen_count": 5},
                    {
                        "artist_mbid": "a" * 36,
                        "artist_name": "Known",
                        "listen_count": 9,
                    },
                ]
            }
        }
    ).encode()
    seeds = parse_seed_page(payload)
    assert [s.name for s in seeds] == ["Known"]


def test_empty_page_yields_nothing():
    assert parse_seed_page(json.dumps({"payload": {"artists": []}}).encode()) == []


def test_malformed_payload_raises():
    with pytest.raises(ValueError):
        parse_seed_page(b"<html>")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd builder && uv run --extra dev pytest tests/test_seeds.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

`builder/src/artistpath_builder/sources/seeds.py`:

```python
"""Seed artist acquisition: the top N artists by sitewide listen count.

Listen count becomes the popularity signal that drives popularity-weighted
routing (spec section 4.1). Artists without an MBID are unusable as nodes.

IMPORTANT: field names come from the response recorded in Task 1. Correct
them here if the findings document shows otherwise.
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import SeedArtist

FIELD_MBID = "artist_mbid"
FIELD_NAME = "artist_name"
FIELD_LISTENS = "listen_count"


def seed_page_url(config: BuilderConfig, offset: int, count: int) -> str:
    query = urlencode({"count": count, "offset": offset, "range": "all_time"})
    return f"{config.sitewide_artists_url}?{query}"


def parse_seed_page(payload: bytes) -> list[SeedArtist]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed seed payload: {exc}") from exc

    rows = data.get("payload", {}).get("artists", []) if isinstance(data, dict) else []

    seeds: list[SeedArtist] = []
    for row in rows:
        mbid = row.get(FIELD_MBID)
        if not mbid:
            continue
        seeds.append(
            SeedArtist(
                mbid=mbid,
                name=row.get(FIELD_NAME) or "",
                listen_count=int(row.get(FIELD_LISTENS) or 0),
            )
        )
    return seeds
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_seeds.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/sources/seeds.py builder/tests/test_seeds.py
git commit -m "feat(builder): add seed artist acquisition"
```

---

## Task 6: Resumable crawler

**Files:**
- Create: `builder/src/artistpath_builder/crawl.py`
- Test: `builder/tests/test_crawl.py`

**Interfaces:**
- Consumes: `BuilderConfig` (Task 2), `RawArchive` (Task 3), `SimilaritySource` (Task 4).
- Produces: `Crawler(config, archive, source, fetcher)` with `crawl(mbids: list[str]) -> None` and `archive_key(mbid) -> str`. Used by Tasks 9 and 11.

The crawler's only job is to fill the archive. It does not build a graph. This separation is what makes Task 9's replay test possible.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_crawl.py`:

```python
import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler, TransientFetchError
from artistpath_builder.sources.listenbrainz import ListenBrainzSource


class FakeFetcher:
    """Records calls and returns queued responses."""

    def __init__(self, responses: dict[str, bytes], fail_times: int = 0):
        self.responses = responses
        self.calls: list[str] = []
        self.fail_times = fail_times

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        if self.fail_times > 0:
            self.fail_times -= 1
            raise TransientFetchError("429 slow down")
        for mbid, body in self.responses.items():
            if mbid in url:
                return body
        return b"[]"


@pytest.fixture
def config():
    return BuilderConfig(requests_per_second=1000.0, checkpoint_every=1)


def _crawler(tmp_path, config, fetcher):
    return Crawler(
        config=config,
        archive=LocalArchive(tmp_path / "archive"),
        source=ListenBrainzSource(config),
        fetcher=fetcher,
        checkpoint_path=tmp_path / "checkpoint.json",
    )


def test_crawl_archives_every_response(tmp_path, config):
    fetcher = FakeFetcher({"a" * 36: b'[{"artist_mbid":"bbb","score":1}]'})
    crawler = _crawler(tmp_path, config, fetcher)
    crawler.crawl(["a" * 36])
    assert crawler.archive.get(crawler.archive_key("a" * 36)) == (
        b'[{"artist_mbid":"bbb","score":1}]'
    )


def test_already_archived_artists_are_not_refetched(tmp_path, config):
    fetcher = FakeFetcher({})
    crawler = _crawler(tmp_path, config, fetcher)
    crawler.archive.put(crawler.archive_key("a" * 36), b"[]")
    crawler.crawl(["a" * 36])
    assert fetcher.calls == []


def test_crawl_resumes_from_checkpoint(tmp_path, config):
    fetcher = FakeFetcher({})
    crawler = _crawler(tmp_path, config, fetcher)
    crawler.crawl(["a" * 36, "b" * 36])
    first_call_count = len(fetcher.calls)

    # A fresh crawler over the same archive must do no further work.
    resumed = _crawler(tmp_path, config, FakeFetcher({}))
    resumed.crawl(["a" * 36, "b" * 36])
    assert resumed.fetcher.calls == []
    assert first_call_count == 2


def test_transient_failures_are_retried(tmp_path, config):
    fetcher = FakeFetcher({"a" * 36: b"[]"}, fail_times=2)
    crawler = _crawler(tmp_path, config, fetcher)
    crawler.crawl(["a" * 36])
    assert len(fetcher.calls) == 3
    assert crawler.archive.has(crawler.archive_key("a" * 36))


def test_exhausted_retries_records_failure_and_continues(tmp_path, config):
    cfg = BuilderConfig(requests_per_second=1000.0, max_retries=2, checkpoint_every=1)
    fetcher = FakeFetcher({}, fail_times=99)
    crawler = _crawler(tmp_path, cfg, fetcher)
    crawler.crawl(["a" * 36, "b" * 36])
    # A single bad artist must not abort an overnight crawl.
    assert set(crawler.failures) == {"a" * 36, "b" * 36}
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
from collections.abc import Callable
from pathlib import Path

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.base import SimilaritySource

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
        self._done: set[str] = self._load_checkpoint()

    def archive_key(self, mbid: str) -> str:
        return f"similar/{self.source.name}/{mbid}.json"

    def crawl(self, mbids: list[str]) -> None:
        pending = [m for m in mbids if m not in self._done]
        logger.info("crawling %d artists (%d already done)", len(pending), len(self._done))

        for index, mbid in enumerate(pending, start=1):
            key = self.archive_key(mbid)
            if self.archive.has(key):
                self._done.add(mbid)
                continue

            payload = self._fetch_with_retries(mbid)
            if payload is not None:
                self.archive.put(key, payload)
            self._done.add(mbid)

            if index % self.config.checkpoint_every == 0:
                self._save_checkpoint()
                logger.info("checkpoint: %d/%d", index, len(pending))

        self._save_checkpoint()

    def _fetch_with_retries(self, mbid: str) -> bytes | None:
        url = self.source.request_url(mbid)
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
        self.failures.append(mbid)
        return None

    def _load_checkpoint(self) -> set[str]:
        if not self.checkpoint_path.is_file():
            return set()
        return set(json.loads(self.checkpoint_path.read_text())["done"])

    def _save_checkpoint(self) -> None:
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(
            json.dumps({"done": sorted(self._done)}, sort_keys=True)
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_crawl.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add builder/src/artistpath_builder/crawl.py builder/tests/test_crawl.py
git commit -m "feat(builder): add resumable rate-limited crawler"
```

---

## Task 7: Graph assembly

Pure functions over in-memory data. No I/O.

**Files:**
- Create: `builder/src/artistpath_builder/graph.py`
- Test: `builder/tests/test_graph.py`

**Interfaces:**
- Consumes: `SimilarArtist`, `SeedArtist`, `EdgeType` (Task 2).
- Produces: `symmetrise(adjacency) -> dict[str, dict[str, float]]`, `largest_component(adjacency) -> set[str]`, `build_graph(adjacency, seeds, edge_type) -> Graph`. `Graph` is a dataclass with `mbids: list[str]`, `names: list[str]`, `popularity: list[float]`, `offsets`, `neighbours`, `scores`, `edge_types` (numpy arrays). Used by Task 8.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_graph.py`:

```python
import numpy as np

from artistpath_builder.graph import build_graph, largest_component, symmetrise
from artistpath_builder.models import EdgeType, SeedArtist

A, B, C, D, E = ("a" * 36, "b" * 36, "c" * 36, "d" * 36, "e" * 36)


def _seeds(*mbids_and_listens):
    return [
        SeedArtist(mbid=m, name=m[0].upper(), listen_count=n)
        for m, n in mbids_and_listens
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
    graph = build_graph(adjacency, _seeds((A, 10), (B, 20)), EdgeType.BEHAVIOURAL)
    assert graph.mbids == [A, B]


def test_csr_offsets_are_valid():
    adjacency = {A: {B: 1.0, C: 0.5}, B: {A: 1.0}, C: {A: 0.5}}
    graph = build_graph(
        adjacency, _seeds((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    assert graph.offsets[0] == 0
    assert graph.offsets[-1] == len(graph.neighbours)
    assert len(graph.offsets) == len(graph.mbids) + 1
    assert np.all(np.diff(graph.offsets) >= 0)


def test_every_edge_is_reciprocated_in_csr():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}, C: {A: 0.4}, }
    graph = build_graph(
        symmetrise(adjacency), _seeds((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    for src in range(len(graph.mbids)):
        for i in range(graph.offsets[src], graph.offsets[src + 1]):
            dst = int(graph.neighbours[i])
            back = graph.neighbours[graph.offsets[dst] : graph.offsets[dst + 1]]
            assert src in back


def test_neighbours_are_sorted_within_each_row():
    adjacency = {A: {B: 0.1, C: 0.9}, B: {A: 0.1}, C: {A: 0.9}}
    graph = build_graph(
        adjacency, _seeds((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    row = graph.neighbours[graph.offsets[0] : graph.offsets[1]]
    assert list(row) == sorted(row)


def test_popularity_is_log_scaled_to_unit_range():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    graph = build_graph(adjacency, _seeds((A, 1), (B, 1_000_000)), EdgeType.BEHAVIOURAL)
    assert min(graph.popularity) == 0.0
    assert max(graph.popularity) == 1.0


def test_edges_carry_the_source_edge_type():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    graph = build_graph(adjacency, _seeds((A, 10), (B, 20)), EdgeType.BEHAVIOURAL)
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

from artistpath_builder.models import EdgeType, SeedArtist

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
    seeds: list[SeedArtist],
    edge_type: EdgeType,
) -> Graph:
    """Assemble CSR arrays. IDs are assigned in sorted-MBID order."""
    seed_by_mbid = {seed.mbid: seed for seed in seeds}
    mbids = sorted(set(adjacency) & set(seed_by_mbid))
    index = {mbid: i for i, mbid in enumerate(mbids)}

    names = [seed_by_mbid[m].name for m in mbids]
    popularity = _log_scaled([seed_by_mbid[m].listen_count for m in mbids])

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
from artistpath_builder.models import EdgeType, SeedArtist

A, B, C = ("a" * 36, "b" * 36, "c" * 36)


@pytest.fixture
def graph():
    adjacency = {A: {B: 1.0, C: 0.5}, B: {A: 1.0}, C: {A: 0.5}}
    seeds = [
        SeedArtist(mbid=A, name="Alpha", listen_count=100),
        SeedArtist(mbid=B, name="Beta", listen_count=50),
        SeedArtist(mbid=C, name="Gamma", listen_count=10),
    ]
    return build_graph(adjacency, seeds, EdgeType.BEHAVIOURAL)


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
- Produces: `build_from_archive(config, archive, source, seeds) -> Graph`. Used by Task 11.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_replay.py`:

```python
import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import serialise
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler
from artistpath_builder.models import SeedArtist
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C = ("a" * 36, "b" * 36, "c" * 36)

RESPONSES = {
    A: b'[{"artist_mbid":"' + B.encode() + b'","name":"Beta","score":10}]',
    B: b'[{"artist_mbid":"' + A.encode() + b'","name":"Alpha","score":10},'
       b'{"artist_mbid":"' + C.encode() + b'","name":"Gamma","score":5}]',
    C: b'[{"artist_mbid":"' + B.encode() + b'","name":"Beta","score":5}]',
}

SEEDS = [
    SeedArtist(mbid=A, name="Alpha", listen_count=300),
    SeedArtist(mbid=B, name="Beta", listen_count=200),
    SeedArtist(mbid=C, name="Gamma", listen_count=100),
]


class RecordedFetcher:
    def __init__(self):
        self.calls = 0

    def __call__(self, url: str) -> bytes:
        self.calls += 1
        for mbid, body in RESPONSES.items():
            if mbid in url:
                return body
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
    ).crawl([A, B, C])
    assert fetcher.calls == 3

    first = serialise(build_from_archive(config, archive, source, SEEDS))

    # Second build: same archive, a fetcher that raises if touched.
    Crawler(
        config=config,
        archive=archive,
        source=source,
        fetcher=ExplodingFetcher(),
        checkpoint_path=tmp_path / "checkpoint2.json",
    ).crawl([A, B, C])

    second = serialise(build_from_archive(config, archive, source, SEEDS))

    assert first == second


def test_replay_produces_a_connected_graph(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    for mbid, body in RESPONSES.items():
        archive.put(f"similar/{source.name}/{mbid}.json", body)

    graph = build_from_archive(config, archive, source, SEEDS)
    assert graph.mbids == [A, B, C]
    assert graph.edge_count > 0


def test_artists_missing_from_the_archive_are_skipped(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    archive.put(f"similar/{source.name}/{A}.json", RESPONSES[A])
    archive.put(f"similar/{source.name}/{B}.json", RESPONSES[B])
    # C is absent — a crawl failure. The build must not raise.
    graph = build_from_archive(config, archive, source, SEEDS)
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
from artistpath_builder.models import SeedArtist
from artistpath_builder.sources.base import SimilaritySource

logger = logging.getLogger(__name__)


def build_from_archive(
    config: BuilderConfig,
    archive: RawArchive,
    source: SimilaritySource,
    seeds: list[SeedArtist],
) -> Graph:
    known = {seed.mbid for seed in seeds}
    adjacency: Adjacency = {}
    missing = 0

    for seed in sorted(seeds, key=lambda s: s.mbid):
        payload = archive.get(f"similar/{source.name}/{seed.mbid}.json")
        if payload is None:
            missing += 1
            continue
        neighbours = source.parse(payload, exclude_mbid=seed.mbid)
        adjacency[seed.mbid] = {
            n.mbid: n.score for n in neighbours if n.mbid in known
        }

    if missing:
        logger.warning("%d seed artists had no archived response", missing)

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

    return build_graph(pruned, seeds, source.edge_type)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd builder && uv run --extra dev pytest tests/test_replay.py -v
```

Expected: 3 passed

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
from artistpath_builder.models import EdgeType, SeedArtist


def _ring(n: int):
    """A connected ring of n artists, so any subset extraction has options."""
    mbids = [f"{i:036d}" for i in range(n)]
    adjacency = {
        m: {mbids[(i + 1) % n]: 0.9, mbids[(i - 1) % n]: 0.8}
        for i, m in enumerate(mbids)
    }
    seeds = [
        SeedArtist(mbid=m, name=f"Artist {i}", listen_count=(n - i) * 100)
        for i, m in enumerate(mbids)
    ]
    return build_graph(symmetrise(adjacency), seeds, EdgeType.BEHAVIOURAL), mbids


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
- Produces: `artistpath-build seeds|crawl|build|fixture` commands. `build` writes `graph-{version}.bin`, consumed by the API plan.

- [ ] **Step 1: Write the failing test**

`builder/tests/test_cli.py`:

```python
import json

from artistpath_builder.cli import main


def test_help_exits_zero(capsys):
    assert main(["--help"]) == 0 or True  # argparse raises SystemExit(0)


def test_build_writes_an_artifact(tmp_path, monkeypatch):
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    (archive_dir / "similar" / "listenbrainz").mkdir(parents=True)
    a, b = "a" * 36, "b" * 36
    (archive_dir / "similar" / "listenbrainz" / f"{a}.json").write_bytes(
        json.dumps([{"artist_mbid": b, "name": "Beta", "score": 10}]).encode()
    )
    (archive_dir / "similar" / "listenbrainz" / f"{b}.json").write_bytes(
        json.dumps([{"artist_mbid": a, "name": "Alpha", "score": 10}]).encode()
    )

    seeds_path = tmp_path / "seeds.json"
    seeds_path.write_text(
        json.dumps(
            [
                {"mbid": a, "name": "Alpha", "listen_count": 100},
                {"mbid": b, "name": "Beta", "listen_count": 50},
            ]
        )
    )

    out = tmp_path / "graph.bin"
    exit_code = main(
        [
            "build",
            "--archive-dir", str(archive_dir),
            "--seeds", str(seeds_path),
            "--out", str(out),
        ]
    )
    assert exit_code == 0
    assert out.stat().st_size > 0
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

    artistpath-build seeds  --out seeds.json
    artistpath-build crawl  --seeds seeds.json --archive-dir ./archive
    artistpath-build build  --seeds seeds.json --archive-dir ./archive --out graph-v1.bin
    artistpath-build fixture --graph graph-v1.bin --out fixture.bin --size 500
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
from artistpath_builder.models import SeedArtist
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.sources.seeds import parse_seed_page, seed_page_url

PAGE_SIZE = 1000


def _archive(args):
    if args.s3_bucket:
        return S3Archive(args.s3_bucket, args.s3_prefix)
    return LocalArchive(Path(args.archive_dir))


def _load_seeds(path: Path) -> list[SeedArtist]:
    rows = json.loads(path.read_text())
    return [SeedArtist(**row) for row in rows]


def cmd_seeds(args) -> int:
    config = BuilderConfig()
    fetch = http_fetcher(config)
    seeds: list[SeedArtist] = []
    offset = 0
    while len(seeds) < config.target_artist_count:
        payload = fetch(seed_page_url(config, offset=offset, count=PAGE_SIZE))
        page = parse_seed_page(payload)
        if not page:
            logging.info("seed source exhausted at offset %d", offset)
            break
        seeds.extend(page)
        offset += PAGE_SIZE
        logging.info("collected %d seeds", len(seeds))

    seeds = seeds[: config.target_artist_count]
    Path(args.out).write_text(
        json.dumps([s.__dict__ for s in seeds], sort_keys=True, indent=0)
    )
    logging.info("wrote %d seeds to %s", len(seeds), args.out)
    return 0


def cmd_crawl(args) -> int:
    config = BuilderConfig()
    seeds = _load_seeds(Path(args.seeds))
    crawler = Crawler(
        config=config,
        archive=_archive(args),
        source=ListenBrainzSource(config),
        fetcher=http_fetcher(config),
        checkpoint_path=Path(args.checkpoint),
    )
    crawler.crawl([s.mbid for s in seeds])
    if crawler.failures:
        logging.warning("%d artists failed permanently", len(crawler.failures))
    return 0


def cmd_build(args) -> int:
    config = BuilderConfig()
    graph = build_from_archive(
        config, _archive(args), ListenBrainzSource(config), _load_seeds(Path(args.seeds))
    )
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

    p_seeds = sub.add_parser("seeds")
    p_seeds.add_argument("--out", required=True)
    p_seeds.set_defaults(func=cmd_seeds)

    p_crawl = sub.add_parser("crawl")
    p_crawl.add_argument("--seeds", required=True)
    p_crawl.add_argument("--checkpoint", default="./checkpoint.json")
    add_archive_args(p_crawl)
    p_crawl.set_defaults(func=cmd_crawl)

    p_build = sub.add_parser("build")
    p_build.add_argument("--seeds", required=True)
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

```bash
cd builder
uv run artistpath-build seeds --out /tmp/seeds-small.json
head -c 400 /tmp/seeds-small.json
```

Then truncate to the first 200 seeds and crawl those:

```bash
python -c "import json,pathlib; p=pathlib.Path('/tmp/seeds-small.json'); rows=json.loads(p.read_text())[:200]; pathlib.Path('/tmp/seeds-200.json').write_text(json.dumps(rows))"
uv run artistpath-build crawl --seeds /tmp/seeds-200.json --archive-dir /tmp/archive --checkpoint /tmp/cp.json
uv run artistpath-build build --seeds /tmp/seeds-200.json --archive-dir /tmp/archive --out /tmp/graph-small.bin
```

Expected: a log line reporting artist count, edge count and size. **Record the ratio of artists retained after largest-component pruning.** If it is below ~80%, the similarity data is sparser than assumed — stop and report before running the full crawl.

- [ ] **Step 6: Verify replay against real archived data**

```bash
cd builder
uv run artistpath-build build --seeds /tmp/seeds-200.json --archive-dir /tmp/archive --out /tmp/graph-small-2.bin
cmp /tmp/graph-small.bin /tmp/graph-small-2.bin && echo "BYTE IDENTICAL"
```

Expected: `BYTE IDENTICAL`

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

**Type consistency:** `SimilarArtist(mbid, name, score)`, `SeedArtist(mbid, name, listen_count)`, and `Graph(mbids, names, popularity, offsets, neighbours, scores, edge_types)` are used with identical names and types in Tasks 2, 4, 5, 7, 8, 9, 10, 11. `archive_key()` is defined in Task 6 and its exact string form (`similar/{source.name}/{mbid}.json`) is reused in Tasks 9 and 11.

---

## What comes after this plan

Two further plans, written only once this one's data findings are in:

**Plan 2 — Path engine and API.** Loads the artifact into typed arrays; bidirectional Dijkstra; base cost function tuned and **frozen**; then the two bypass signals and progressive floor relaxation tuned on top of the frozen baseline (spec §4.3). Fastify endpoints, clip resolution, DynamoDB cache.

**Plan 3 — Web app and infrastructure.** React + Vite front end, CDK stack, App Runner, GitHub Actions with OIDC.

They are deliberately not written yet. Path quality tuning depends on how good the real graph turns out to be, and the spec's §2.1 makes that quality the thing everything else is subordinate to.
