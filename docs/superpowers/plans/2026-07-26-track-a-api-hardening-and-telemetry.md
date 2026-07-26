# Track A — API hardening and telemetry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use **superpowers:executing-plans** for this plan — **inline, not subagent-driven.** Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Why inline, stated so the next session does not have to re-derive it.** The tasks are
> **strictly sequential**: Task 2 consumes Task 1's `from_bytes`, Task 4 consumes Task 3's
> async cache, Tasks 8–9 consume Task 7's emitter, and eight of the ten tasks edit the same
> two files (`app.py`, `clips.py`). There is no independent work to fan out, so subagents
> would serialise anyway while paying a **cold context re-derivation per task, ten times,
> over the same handful of files**. The plan is also highly prescriptive — complete code,
> exact paths, exact test bodies, exact expected pass counts — so a fresh reviewer's
> marginal value per task is low, and the risk subagents would absorb is **already absorbed
> by the per-task gates**: a red/green cycle that names *why* the test must fail, plus a
> full-suite run with an exact expected count after every task.
>
> **The counting gates specifically favour a warm controller.** If a run reports 166 instead
> of 167, someone who watched the previous nine tasks can tell a broken test from a
> miscounted plan; a cold subagent cannot.
>
> **When to switch:** **Track D** (the six frontend items) is the opposite shape — largely
> independent, different files, no shared interfaces — and subagent fan-out is the better
> call there. Switch if that plan is what you are executing, not this one.

**Goal:** Fix six real API defects and add bypass telemetry, entirely without AWS, so the app is strictly better even if the deploy never happens.

**Architecture:** All work is inside `api/` plus three small `frontend/` edits. The artifact parser gains bounds checks and an injectable load seam; the clip cache becomes async and stops turning infrastructure blips into 500s; the path endpoint gains input guards; two structured-JSON event types go to stdout, which App Runner ships to CloudWatch for free.

**Tech Stack:** Python 3.12+, FastAPI, pydantic v2, numpy, boto3, pytest (`asyncio_mode = "auto"`, so async tests need no decorator); React 19 + TypeScript + Vitest.

## Governing documents — read these first, in this order

1. **`docs/superpowers/specs/2026-07-26-gate2-deploy-and-telemetry-design.md`** — the design (`DEP-`). **Read its §12 amendments before anything else**; several original claims are struck and corrected in place.
2. **`docs/superpowers/findings/2026-07-26-gate1-gate2-team-review.md`** — the review that produced those corrections (`TR-`).
3. `CLAUDE.md` — repo conventions.

**Where this plan and the design disagree, the design governs.** This plan implements Track A of the design's §11 only.

## Global Constraints

- **`UV_LINK_MODE=copy` on every `uv` command.** The repo is under OneDrive; hardlinks fail without it. Run from inside `api/`.
- **`PYTHONIOENCODING=utf-8`** on anything that prints artist names.
- **Full test command:** `UV_LINK_MODE=copy uv run --extra dev pytest -q` from `api/`.
- **Baseline suite state, measured 2026-07-26:** api **153 passed**, builder 115, frontend 64, e2e 3. Any task that reduces these without explanation is wrong.
- **No new Python dependency.** `asyncio.to_thread` replaces aioboto3 deliberately (`DEP-11`).
- **Touch no routing weight, no cost-function term, no graph build.** Path-quality work is paused by owner decision. `pathfinding.py` is edited **only** at `find_journey`/`build_path` input-guard level, never in the cost function.
- **Quantities carry their currency in their name** — `pop_raw`, never `popularity`, for new code. Two names are exempt as wire contracts: the `popularity` key in APG1 metadata and in the API's JSON response.
- **Every new test must fail against unmodified source before you implement.** `DEP-20`/`TR-2`: this plan's predecessor prescribed a test that passed before the fix. Step 2 of every task exists for this reason — **do not skip it, and do not accept a "fails" that fails for the wrong reason.**
- **Branch:** work continues on `gate2-deploy-and-telemetry` (PR #27). Commit per task.

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `api/src/artistpath_api/graph_store.py` | APG1 parsing; gains bounds checks and a `from_bytes` seam | Modify |
| `api/src/artistpath_api/artifact_source.py` | Fetch bytes from a local path or `s3://`, verify sha256, build the store | **Create** |
| `api/src/artistpath_api/telemetry.py` | Structured-JSON event emission and journey-id validation | **Create** |
| `api/src/artistpath_api/clips.py` | Async cache protocol; guarded cache calls; null-field coercion | Modify |
| `api/src/artistpath_api/config.py` | `graph_sha256` setting | Modify |
| `api/src/artistpath_api/models.py` | Bound `exclude`; `HealthOut` | Modify |
| `api/src/artistpath_api/app.py` | Input guards, `/health`, telemetry emission, CORS header allowance | Modify |
| `api/tests/test_graph_store.py` | Bounds-check tests | Modify |
| `api/tests/test_artifact_source.py` | Load-seam and checksum tests | **Create** |
| `api/tests/test_telemetry.py` | Event-shape and journey-id validation tests | **Create** |
| `frontend/src/api/client.ts` | Generate and send the journey id | Modify |
| `frontend/playwright.config.ts` | `outputDir` outside the synced tree (`DEP-30`) | Modify |

---

## Task 1: Artifact bounds checks

**Files:**
- Modify: `api/src/artistpath_api/graph_store.py:86-123`
- Test: `api/tests/test_graph_store.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `GraphStore.from_bytes(payload: bytes) -> GraphStore`, used by Task 2. `GraphStore.load(path)` keeps its current signature and delegates.

**Why this task's test is unusually easy to get wrong.** `json.JSONDecodeError` **subclasses `ValueError`**, and a truncated artifact already raises it. So `pytest.raises(ValueError)` **passes today, before any fix** — that is exactly the vacuous test `TR-2` records. **The tests below match on the message**, which is what makes them fail first.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_graph_store.py`:

```python
import json
import struct

import pytest

from artistpath_api.graph_store import GraphStore

_HEADER = struct.Struct("<4sIIIQ")


def _build_apg1(n_header: int, mbids: list[str], offsets: list[int],
                neighbours: list[int], scores: list[float]) -> bytes:
    """Assemble an APG1 payload, allowing header/metadata disagreement on purpose."""
    meta = {
        "mbids": mbids,
        "names": [m.upper() for m in mbids],
        "disambiguations": ["" for _ in mbids],
        "popularity": [0.5 for _ in mbids],
    }
    blob = json.dumps(meta).encode()
    e = len(neighbours)
    body = (
        struct.pack(f"<{len(offsets)}i", *offsets)
        + struct.pack(f"<{e}i", *neighbours)
        + struct.pack(f"<{e}f", *scores)
        + bytes(e)
    )
    return _HEADER.pack(b"APG1", 1, n_header, e, len(blob)) + body + blob


def _good() -> bytes:
    return _build_apg1(2, ["a", "b"], [0, 1, 2], [1, 0], [0.9, 0.9])


def test_good_artifact_still_loads():
    store = GraphStore.from_bytes(_good())
    assert store.artist_count == 2


def test_truncated_artifact_raises_a_truncation_error(tmp_path):
    payload = _good()
    p = tmp_path / "t.bin"
    p.write_bytes(payload[: len(payload) - 8])
    with pytest.raises(ValueError, match="truncated"):
        GraphStore.load(p)


def test_over_long_artifact_raises(tmp_path):
    p = tmp_path / "t.bin"
    p.write_bytes(_good() + b"garbage!")
    with pytest.raises(ValueError, match="length"):
        GraphStore.load(p)


def test_header_and_metadata_length_disagreement_raises():
    # Header claims 4 nodes; metadata describes 2. This is the case that
    # currently loads SILENTLY and leaves pop_raw and degree_hub_penalty at
    # different lengths, both indexed by node id (TR-3).
    payload = _build_apg1(4, ["a", "b"], [0, 1, 1, 1, 1], [0], [0.9])
    with pytest.raises(ValueError, match="inconsistent"):
        GraphStore.from_bytes(payload)
```

- [ ] **Step 2: Run the tests and verify they fail — and check WHY**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_graph_store.py -k "truncated or over_long or disagreement" -v`

Expected: all three FAIL. `test_good_artifact_still_loads` fails with `AttributeError: type object 'GraphStore' has no attribute 'from_bytes'`. The truncation test fails because the raised `JSONDecodeError` message does **not** contain "truncated". The disagreement test fails because nothing raises at all.

**Stop and re-read this task if the truncation test passes.** That means you matched on the exception type rather than the message, and you have reproduced `TR-2`.

- [ ] **Step 3: Implement the bounds checks**

In `api/src/artistpath_api/graph_store.py`, replace the body of `load` (lines 86-123) with:

```python
    @classmethod
    def load(cls, path: str | Path) -> "GraphStore":
        return cls.from_bytes(Path(path).read_bytes())

    @classmethod
    def from_bytes(cls, payload: bytes) -> "GraphStore":
        """Parse an APG1 payload.

        Every bounds check here already exists in the builder's writer
        (builder/src/artistpath_builder/artifact.py) and was missing from this
        reader. The two parsers had drifted, undetected, in the half that is
        about to start fetching over a network — see the team review's TR-4.
        """
        if len(payload) < _HEADER.size:
            raise ValueError("artifact truncated: shorter than header")
        magic, version, n, e, meta_len = _HEADER.unpack_from(payload)
        if magic != _MAGIC:
            raise ValueError(f"bad magic: expected {_MAGIC!r}, got {magic!r}")
        if version != _FORMAT_VERSION:
            raise ValueError(f"unsupported artifact version {version}")

        # Sections are fixed-width and the metadata blob is last, so the total
        # length is fully determined by the header. A short read is truncation;
        # a long one means the file is not what the header describes.
        expected = _HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1 + meta_len
        if len(payload) < expected:
            raise ValueError(
                f"artifact truncated: header describes {expected} bytes, got {len(payload)}"
            )
        if len(payload) > expected:
            raise ValueError(
                f"artifact length mismatch: header describes {expected} bytes, "
                f"got {len(payload)}"
            )

        cursor = _HEADER.size

        def take(count: int, dtype: str, size: int) -> np.ndarray:
            nonlocal cursor
            end_ = cursor + count * size
            # count= is load-bearing: without it a short buffer yields a SHORTER
            # array rather than an error.
            arr = np.frombuffer(payload[cursor:end_], dtype=dtype, count=count)
            cursor = end_
            return arr

        offsets = take(n + 1, "<i4", 4)
        neighbours = take(e, "<i4", 4)
        scores = take(e, "<f4", 4)
        take(e, "<u1", 1)  # edge_types — unused in alpha (all behavioural)
        meta = json.loads(payload[cursor : cursor + meta_len])

        # The header's N and the metadata's length are two independent
        # statements of the same fact. When they disagree the artifact loads
        # clean and leaves pop_raw and degree_hub_penalty at different lengths,
        # both indexed by node id in the cost function (TR-3).
        if len(meta["mbids"]) != n:
            raise ValueError(
                f"artifact inconsistent: header says {n} nodes, "
                f"metadata has {len(meta['mbids'])}"
            )

        return cls(
            mbids=meta["mbids"],
            names=meta["names"],
            disambiguations=meta["disambiguations"],
            # "popularity" is the APG1 wire key and cannot be renamed without
            # invalidating every existing artifact — the format is the
            # builder/api contract. Only the in-memory name carries the basis.
            pop_raw=np.asarray(meta["popularity"], dtype=np.float32),
            offsets=offsets,
            neighbours=neighbours,
            scores=scores,
        )
```

- [ ] **Step 4: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **157 passed** (153 baseline + 4 new).

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/graph_store.py api/tests/test_graph_store.py
git commit -m "Add APG1 bounds checks the builder already had (DEP-10 corrected, TR-3, TR-4)"
```

---

## Task 2: The `load_graph` seam, `s3://` support, and the checksum gate

**Files:**
- Create: `api/src/artistpath_api/artifact_source.py`
- Create: `api/tests/test_artifact_source.py`
- Modify: `api/src/artistpath_api/config.py` (after line 22)
- Modify: `api/src/artistpath_api/app.py:95-109` (`build_default_app`)

**Interfaces:**
- Consumes: `GraphStore.from_bytes` (Task 1).
- Produces: `load_graph(uri: str, expected_sha256: str = "", reader: Callable[[str], bytes] = default_reader) -> GraphStore`, and `ApiConfig.graph_sha256: str`. Task 7 uses `GraphStore.source_sha256`.

**Why the seam exists.** `build_default_app` is referenced by nothing in the test suite — it has **zero coverage** — and `ApiConfig` reads the environment at two different times (`graph_path` at import, `cors_origins` per instance), so the obvious `monkeypatch.setenv` test **passes for the wrong reason** (`TR-11`). Injecting the reader is what keeps Track A genuinely AWS-free.

- [ ] **Step 1: Write the failing tests**

Create `api/tests/test_artifact_source.py`:

```python
import hashlib

import pytest

from artistpath_api.artifact_source import load_graph, parse_s3_uri
from tests.test_graph_store import _good


def test_parses_an_s3_uri_into_bucket_and_key():
    assert parse_s3_uri("s3://my-bucket/graphs/g.bin") == ("my-bucket", "graphs/g.bin")


def test_rejects_a_non_s3_uri():
    with pytest.raises(ValueError, match="not an s3"):
        parse_s3_uri("/local/path.bin")


def test_loads_through_an_injected_reader():
    payload = _good()
    store = load_graph("s3://b/k.bin", reader=lambda uri: payload)
    assert store.artist_count == 2


def test_accepts_a_matching_checksum_and_records_it():
    payload = _good()
    digest = hashlib.sha256(payload).hexdigest()
    store = load_graph("s3://b/k.bin", expected_sha256=digest, reader=lambda uri: payload)
    assert store.source_sha256 == digest


def test_refuses_to_load_on_a_checksum_mismatch():
    payload = _good()
    with pytest.raises(ValueError, match="checksum mismatch"):
        load_graph("s3://b/k.bin", expected_sha256="0" * 64, reader=lambda uri: payload)


def test_empty_expected_checksum_skips_verification():
    payload = _good()
    store = load_graph("s3://b/k.bin", expected_sha256="", reader=lambda uri: payload)
    assert store.artist_count == 2
```

- [ ] **Step 2: Run and verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_artifact_source.py -v`
Expected: collection error — `ModuleNotFoundError: No module named 'artistpath_api.artifact_source'`.

- [ ] **Step 3: Add the `source_sha256` field to `GraphStore`**

In `api/src/artistpath_api/graph_store.py`, add to the dataclass field list, immediately after `degree_hub_penalty` (line 36):

```python
    # sha256 of the bytes this store was parsed from, when known. Empty for a
    # store built in a test. Reported by /health so "which graph is live" is
    # answerable over HTTP — eighteen artifacts sit in builder/scratch/ and are
    # not interchangeable.
    source_sha256: str = ""
```

- [ ] **Step 4: Create the module**

Create `api/src/artistpath_api/artifact_source.py`:

```python
"""Fetch an APG1 artifact from a local path or S3, and verify it before use.

The reader is injected so the URI parsing and both checksum branches are
testable with no AWS account and no credentials — which is what makes Track A
of the deploy design genuinely AWS-free (DEP-18, DEP-28).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from artistpath_api.graph_store import GraphStore

BytesReader = Callable[[str], bytes]

_S3_SCHEME = "s3://"


def parse_s3_uri(uri: str) -> tuple[str, str]:
    """Split `s3://bucket/key/with/slashes` into ("bucket", "key/with/slashes")."""
    if not uri.startswith(_S3_SCHEME):
        raise ValueError(f"not an s3 uri: {uri!r}")
    remainder = uri[len(_S3_SCHEME) :]
    bucket, _, key = remainder.partition("/")
    if not bucket or not key:
        raise ValueError(f"not an s3 uri: {uri!r}")
    return bucket, key


def default_reader(uri: str) -> bytes:
    """Read from S3 when the URI says so, otherwise from the filesystem.

    boto3 is imported lazily so that local development and the whole test suite
    never require it to be configured.
    """
    if uri.startswith(_S3_SCHEME):
        import boto3

        bucket, key = parse_s3_uri(uri)
        return boto3.client("s3").get_object(Bucket=bucket, Key=key)["Body"].read()
    return Path(uri).read_bytes()


def load_graph(
    uri: str,
    expected_sha256: str = "",
    reader: BytesReader = default_reader,
) -> GraphStore:
    """Fetch, verify, and parse an artifact.

    An empty `expected_sha256` skips verification, which is the local-development
    case. Production sets it: a conclusion drawn from the wrong artifact looks
    exactly like a correct one.
    """
    payload = reader(uri)
    digest = hashlib.sha256(payload).hexdigest()
    if expected_sha256 and digest != expected_sha256:
        raise ValueError(
            f"artifact checksum mismatch: expected {expected_sha256}, got {digest}"
        )
    store = GraphStore.from_bytes(payload)
    store.source_sha256 = digest
    return store
```

- [ ] **Step 5: Add the config setting**

In `api/src/artistpath_api/config.py`, immediately after the `graph_path` field (line 22), add:

```python
    # Expected sha256 of the artifact. Empty skips verification (local dev);
    # production sets it and the service refuses to boot on a mismatch. The
    # value is in the artifact's manifest sidecar — do not transcribe it by
    # hand (DEP-24).
    graph_sha256: str = os.environ.get("ARTISTPATH_GRAPH_SHA256", "")
```

- [ ] **Step 6: Wire it into the production entrypoint**

In `api/src/artistpath_api/app.py`, add the import at the top and replace line 98 (`store = GraphStore.load(cfg.graph_path)`):

```python
from artistpath_api.artifact_source import load_graph
```

```python
    store = load_graph(cfg.graph_path, cfg.graph_sha256)
```

The now-unused `GraphStore` import stays — `create_app` still takes one as a parameter type.

- [ ] **Step 7: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **163 passed**.

- [ ] **Step 8: Commit**

```bash
git add api/src/artistpath_api/artifact_source.py api/src/artistpath_api/graph_store.py \
        api/src/artistpath_api/config.py api/src/artistpath_api/app.py \
        api/tests/test_artifact_source.py
git commit -m "Add an injectable load seam with s3:// support and a checksum gate (DEP-28)"
```

---

## Task 3: Make the clip cache async

**Files:**
- Modify: `api/src/artistpath_api/clips.py:70-135` (protocol and both implementations), `:179` and `:191` (call sites in `resolve`)
- Test: `api/tests/test_clips.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `ClipCache.get`/`.put` are now `async def`. Task 4 guards these same call sites.

**Why.** `get_track` is the **only** `async def` route in the app (`app.py:80`, against `def` at `:59` and `:63`), so it alone runs on the event loop — and it is the one calling blocking boto3. A path view fires 8–10 clip lookups, so with `ARTISTPATH_CLIP_CACHE=dynamo` the app freezes for **everyone** during each cold lookup.

- [ ] **Step 1: Write the failing test**

Append to `api/tests/test_clips.py`:

```python
async def test_dynamo_cache_round_trips_through_the_resolver():
    """Drives DynamoClipCache through ClipResolver rather than calling it directly.

    The existing FakeTable tests call .get/.put straight, so nothing exercised
    the cache through the code path production uses (TR-11).
    """
    cfg = ApiConfig()
    table = FakeTable(
        item={
            "mbid": "m1",
            "source": "deezer",
            "track_id": "77",
            "title": "T",
            "cover_url": "c",
        }
    )
    cache = DynamoClipCache(cfg, table)

    async def fetch_json(url, params):
        return {"preview": "https://signed.example/x.mp3"}

    resolver = ClipResolver(cfg, cache, fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.preview_url == "https://signed.example/x.mp3"
    assert clip.title == "T"
```

- [ ] **Step 2: Run and verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_clips.py -k round_trips -v`

Expected: FAIL. `resolve` calls `self._cache.get(mbid)` synchronously; today that returns a `TrackIdentity`, so the test may pass *before* the change — **if it does, that is fine and expected for this one task**, because the behaviour under test is preserved across the refactor. The genuine failure appears in step 4 once the cache is async and `resolve` has not been updated. Note this task is a refactor with a characterisation test, not a defect fix.

- [ ] **Step 3: Make the protocol and implementations async**

In `api/src/artistpath_api/clips.py`, add `import asyncio` at the top, then replace lines 70-135:

```python
class ClipCache(Protocol):
    async def get(self, mbid: str) -> TrackIdentity | None: ...
    async def put(self, mbid: str, identity: TrackIdentity) -> None: ...


class InMemoryClipCache:
    """Dev/test cache. Not shared across processes."""

    def __init__(self) -> None:
        self._store: dict[str, TrackIdentity] = {}

    async def get(self, mbid: str) -> TrackIdentity | None:
        return self._store.get(mbid)

    async def put(self, mbid: str, identity: TrackIdentity) -> None:
        self._store[mbid] = identity


class DynamoClipCache:
    """Production cache: DynamoDB with a 30-day TTL (spec 5.1).

    Stores track *identity* only. A signed preview URL must never be written
    here: the TTL is 30 days and the signature expires far sooner (measurement:
    the roadmap's confirmed-diagnoses C2), which is what made every cache hit
    past the first hour serve dead audio.

    The boto3 resource is created lazily on first use, so constructing the
    cache (and therefore booting the app) never requires AWS to be reachable.

    Both methods are async and hand the blocking boto3 call to a worker thread.
    The clip endpoint is the only async route in the app, so a synchronous
    round trip here blocks the event loop for every concurrent user (DEP-11).
    asyncio.to_thread is used deliberately in preference to adding aioboto3 —
    a thread fixes this without a new dependency.
    """

    def __init__(self, cfg: ApiConfig, table=None) -> None:
        self._cfg = cfg
        self._table = table

    def _get_table(self):
        if self._table is None:
            import boto3

            self._table = boto3.resource("dynamodb").Table(self._cfg.clip_table_name)
        return self._table

    def _get_sync(self, mbid: str) -> TrackIdentity | None:
        item = self._get_table().get_item(Key={"mbid": mbid}).get("Item")
        # Items written before C2 carry a long-expired URL and no track id.
        # They cannot be re-resolved, so they are a miss and get overwritten.
        if not item or "track_id" not in item:
            return None
        return TrackIdentity(
            source=item["source"],
            track_id=item["track_id"],
            title=item["title"],
            cover_url=item["cover_url"],
        )

    def _put_sync(self, mbid: str, identity: TrackIdentity) -> None:
        ttl = int(time.time()) + self._cfg.clip_ttl_days * 86400
        self._get_table().put_item(
            Item={
                "mbid": mbid,
                "source": identity.source,
                "track_id": identity.track_id,
                "title": identity.title,
                "cover_url": identity.cover_url,
                "ttl": ttl,
            }
        )

    async def get(self, mbid: str) -> TrackIdentity | None:
        return await asyncio.to_thread(self._get_sync, mbid)

    async def put(self, mbid: str, identity: TrackIdentity) -> None:
        await asyncio.to_thread(self._put_sync, mbid, identity)
```

- [ ] **Step 4: Update the two call sites in `resolve`**

In `api/src/artistpath_api/clips.py`, line 179 becomes `identity = await self._cache.get(mbid)` and line 191 becomes `await self._cache.put(mbid, identity)`.

**Do not skip this step and rely on the tests.** An un-awaited coroutine is **truthy**, so `if identity is not None:` would take the cache-hit branch on every request, pass a coroutine into `_preview_url`, and — because `_get` swallows broadly — degrade to a **silent card** rather than an error.

- [ ] **Step 5: Update existing direct-call tests**

The existing `FakeTable` tests call `cache.get(...)` / `cache.put(...)` directly. Add `await` to each and make the enclosing test `async def`. Search: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_clips.py -v` and fix each failure.

- [ ] **Step 6: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **164 passed**.

- [ ] **Step 7: Commit**

```bash
git add api/src/artistpath_api/clips.py api/tests/test_clips.py
git commit -m "Make the clip cache async so Dynamo cannot block the event loop (DEP-11)"
```

---

## Task 4: Stop cache and catalogue failures becoming 500s

**Files:**
- Modify: `api/src/artistpath_api/clips.py` — `resolve` (lines 172-192), `_from_deezer` (~222-226), `_from_itunes` (~244-247)
- Test: `api/tests/test_clips.py`

**Interfaces:**
- Consumes: the async `ClipCache` from Task 3.
- Produces: no signature change.

**Why.** `ClipResolver.resolve` routes every *catalogue* call through the guarded `_get` but calls the **cache** unguarded, so a DynamoDB blip becomes a 500 on the clip endpoint — the one outcome `clips.py`'s own module docstring forbids. Two sub-cases matter separately: a `get` failure should be a **miss**, but a `put` failure happens *after* a successful lookup, so the correct behaviour is to **return the clip anyway** (`DEP-26`). Separately, a catalogue field that is present-but-null flows into `TrackOut`, whose fields are typed `str`, producing the same 500.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_clips.py`:

```python
class ExplodingCache:
    """A cache whose every operation fails, like DynamoDB throttling."""

    def __init__(self, fail_get=True, fail_put=True):
        self.fail_get = fail_get
        self.fail_put = fail_put

    async def get(self, mbid):
        if self.fail_get:
            raise RuntimeError("dynamo unavailable")
        return None

    async def put(self, mbid, identity):
        if self.fail_put:
            raise RuntimeError("dynamo throttled")


_DEEZER_OK = {
    "data": [
        {
            "preview": "https://p.example/x.mp3",
            "id": 5,
            "title": "Song",
            "artist": {"name": "Some Artist", "picture_medium": "cover"},
        }
    ]
}


async def test_a_failing_cache_read_is_treated_as_a_miss():
    cfg = ApiConfig()

    async def fetch_json(url, params):
        return _DEEZER_OK

    resolver = ClipResolver(cfg, ExplodingCache(fail_get=True, fail_put=False), fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.preview_url == "https://p.example/x.mp3"


async def test_a_failing_cache_write_still_returns_the_clip():
    """The catalogue lookup already succeeded; losing the clip to a cache
    write failure would discard something we are holding."""
    cfg = ApiConfig()

    async def fetch_json(url, params):
        return _DEEZER_OK

    resolver = ClipResolver(cfg, ExplodingCache(fail_get=False, fail_put=True), fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.title == "Song"


async def test_a_null_title_from_the_catalogue_does_not_crash():
    cfg = ApiConfig()

    async def fetch_json(url, params):
        return {
            "data": [
                {
                    "preview": "https://p.example/x.mp3",
                    "id": 5,
                    "title": None,
                    "artist": {"name": "Some Artist", "picture_medium": None},
                }
            ]
        }

    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.title == ""
    assert clip.cover_url == ""
```

- [ ] **Step 2: Run and verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_clips.py -k "failing_cache or null_title" -v`
Expected: three FAIL — two with `RuntimeError` propagating out of `resolve`, one with `clip.title` being `None` rather than `""`.

- [ ] **Step 3: Guard the cache calls**

In `api/src/artistpath_api/clips.py`, replace the body of `resolve` (lines 179-192) with:

```python
        # A cache failure must never reach the caller. The endpoint's contract
        # is a clip or silence, never a 500 (see this module's docstring), and
        # in production the cache is DynamoDB, which can throttle (DEP-12).
        try:
            identity = await self._cache.get(mbid)
        except Exception:
            identity = None

        if identity is not None:
            url = await self._preview_url(identity)
            if url:
                return Clip(url, identity.title, identity.cover_url)
            # The track has left the catalogue. Identity is stable, not
            # permanent, so fall through and find the artist another one.

        found = await self._search(artist_name)
        if found is None:
            return None
        identity, url = found
        # A write failure happens AFTER a successful lookup, so the clip is
        # already in hand. Losing it to a cache error would discard work we
        # have done and silence a card that plays perfectly well (DEP-26).
        try:
            await self._cache.put(mbid, identity)
        except Exception:
            pass
        return Clip(url, identity.title, identity.cover_url)
```

- [ ] **Step 4: Coerce null catalogue fields**

In `_from_deezer`, replace the `TrackIdentity(...)` construction with:

```python
                identity = TrackIdentity(
                    source="deezer",
                    track_id=str(track_id),
                    # `or ""` not a .get default: these keys can be present
                    # with a JSON null, and TrackOut's fields are typed str,
                    # so None here becomes a 500 at the endpoint.
                    title=str(row.get("title") or ""),
                    cover_url=str(artist.get("picture_medium") or ""),
                )
```

In `_from_itunes`, likewise:

```python
                identity = TrackIdentity(
                    source="itunes",
                    track_id=str(track_id),
                    title=str(row.get("trackName") or ""),
                    cover_url=str(row.get("artworkUrl100") or ""),
                )
```

- [ ] **Step 5: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **167 passed**.

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/clips.py api/tests/test_clips.py
git commit -m "Never let a cache or null catalogue field become a 500 (DEP-12, DEP-26)"
```

---

## Task 5: Input guards on the path endpoint

**Files:**
- Modify: `api/src/artistpath_api/app.py:62-77` (`build_path`), `api/src/artistpath_api/app.py:23-30` (`_to_exclusions`), `api/src/artistpath_api/models.py:15-17`
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: nothing.
- Produces: no signature change.

**Why.** `from == target` currently returns a **one-card journey labelled `natural`** (`pathfinding.py:89-90`, then `:189-191`). And `exclude` is unbounded and undeduplicated while `avoidance_map` runs a fresh graph traversal **per entry** (`pathfinding.py:60`), so one large POST buys arbitrary CPU on a GIL-bound handler. The cap is 200 — above the owner's own 100-press dogfooding run, with headroom.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_app.py`:

```python
def test_same_artist_for_both_endpoints_is_rejected():
    client, store = _client()
    mbid = store.mbids[0]
    r = client.post("/api/path", json={"sources": [mbid, mbid], "exclude": []})
    assert r.status_code == 422


def test_an_over_long_exclude_list_is_rejected():
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    excludes = [{"id": store.mbids[1], "reason": "dislike"} for _ in range(201)]
    r = client.post("/api/path", json={"sources": [a, b], "exclude": excludes})
    assert r.status_code == 422


def test_duplicate_exclusions_are_collapsed():
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    dupes = [{"id": store.mbids[1], "reason": "dislike"} for _ in range(50)]
    r = client.post("/api/path", json={"sources": [a, b], "exclude": dupes})
    assert r.status_code == 200


def test_an_unrecognised_reason_is_still_coerced_to_dislike():
    """Pins behaviour the deploy design relies on and nothing tested (TR-7).

    Tightening ExclusionIn.reason to a Literal is the natural tidy-up and would
    silently turn this 200 into a 422 for any client sending a stale reason.
    """
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    r = client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": store.mbids[1], "reason": "BANANA"}]},
    )
    assert r.status_code == 200
```

- [ ] **Step 2: Run and verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_app.py -k "same_artist or over_long or duplicate or unrecognised" -v`
Expected: `same_artist` FAILs (returns 200), `over_long` FAILs (returns 200). `duplicate` and `unrecognised` **pass already** — they are pinning tests for behaviour that is currently correct and must stay correct.

- [ ] **Step 3: Bound the exclude list**

In `api/src/artistpath_api/models.py`, replace lines 15-17:

```python
class PathRequest(BaseModel):
    sources: list[str]           # artist MBIDs; alpha passes exactly two
    # Bounded because avoidance_map runs a fresh graph traversal per entry
    # (pathfinding.py), so an unbounded list is arbitrary attacker-controlled
    # CPU on a GIL-bound handler. 200 is above the deepest real use recorded
    # (a 100-press dogfooding run) with headroom. TR-12 / DEP-25.
    exclude: list[ExclusionIn] = Field(default_factory=list, max_length=200)
```

and add `Field` to the pydantic import at line 7:

```python
from pydantic import BaseModel, Field
```

- [ ] **Step 4: Deduplicate, and guard the endpoints**

In `api/src/artistpath_api/app.py`, replace `_to_exclusions` (lines 23-30):

```python
def _to_exclusions(store: GraphStore, raw: list[ExclusionIn]) -> list[Exclusion]:
    """Resolve wire exclusions to node ids, keeping the last reason per artist.

    Deduplicated because avoidance_map takes a max() per node, so a repeated
    dislike already changes nothing — it only costs another graph traversal.
    """
    by_node: dict[int, str] = {}
    for e in raw:
        node = store.id_by_mbid.get(e.id)
        if node is None:
            continue
        by_node[node] = e.reason if e.reason in (DISLIKE, KNOWN) else DISLIKE
    return [Exclusion(node, reason) for node, reason in by_node.items()]
```

In `build_path`, insert after `source, target = ids` (line 69):

```python
        if source == target:
            raise HTTPException(
                422, "pick two different artists — a journey needs somewhere to go"
            )
```

- [ ] **Step 5: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **171 passed**.

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/app.py api/src/artistpath_api/models.py api/tests/test_app.py
git commit -m "Guard the path endpoint's inputs (DEP-13, DEP-25, TR-12)"
```

---

## Task 6: `/health` reporting artifact identity

**Files:**
- Modify: `api/src/artistpath_api/models.py` (append), `api/src/artistpath_api/app.py` (new route)
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: `GraphStore.source_sha256` (Task 2).
- Produces: `GET /health` returning `HealthOut`.

**Why.** App Runner needs a health-check target, and making it report *which artifact is live* applies to production the checksum discipline every analysis script here already follows. **Path is `/health`, not `/api/health`** — it must be reachable without going through the CloudFront `/api/*` behaviour, because App Runner's own checker calls the origin directly.

- [ ] **Step 1: Write the failing test**

Append to `api/tests/test_app.py`:

```python
def test_health_reports_artifact_identity():
    client, store = _client()
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["artists"] == store.artist_count
    assert body["edges"] == len(store.neighbours)
    assert body["graph_sha256"] == store.source_sha256
```

- [ ] **Step 2: Run and verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_app.py -k health -v`
Expected: FAIL with 404.

- [ ] **Step 3: Add the response model**

Append to `api/src/artistpath_api/models.py`:

```python
class HealthOut(BaseModel):
    status: str
    # Identity of the artifact actually loaded, so "which graph is live" is
    # answerable over HTTP. Eighteen artifacts sit in builder/scratch/ and are
    # not interchangeable; a conclusion from the wrong one looks correct.
    graph_sha256: str
    artists: int
    edges: int
```

- [ ] **Step 4: Add the route**

In `api/src/artistpath_api/app.py`, add `HealthOut` to the `models` import block, then add inside `create_app`, immediately before `return app`:

```python
    @app.get("/health")
    def health() -> HealthOut:
        # Deliberately NOT under /api — App Runner's health checker reaches the
        # origin directly, not through the CloudFront /api/* behaviour.
        return HealthOut(
            status="ok",
            graph_sha256=store.source_sha256,
            artists=store.artist_count,
            edges=len(store.neighbours),
        )
```

- [ ] **Step 5: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **172 passed**.

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/app.py api/src/artistpath_api/models.py api/tests/test_app.py
git commit -m "Add /health reporting which artifact is live"
```

---

> ## 🔶 HANDOFF SEAM — retire the session here if it is long
>
> Tasks 1-6 are the defect fixes; Tasks 7-9 are the telemetry feature. Everything
> above is committed, the suite is green at 172, and **the app is strictly better
> than it was even if nothing else is built** (`DEP-18`). A fresh session resumes at
> Task 7 by reading this plan and the design's §5. Per CLAUDE.md, prefer a planned
> boundary here over discovering one at Task 9.

---

## Task 7: The telemetry emitter

**Files:**
- Create: `api/src/artistpath_api/telemetry.py`
- Create: `api/tests/test_telemetry.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `emit(event: dict) -> None` and `safe_journey_id(raw: str | None) -> str`, both used by Tasks 8 and 9.

**Why the id is validated.** `journey_id` is client-controlled and is about to be written into structured logs. Unvalidated, a crafted header injects a **second, fabricated log record** that later analysis reads as a real journey — into the very data §5 exists to collect (`DEP-27`/`TR-14`).

- [ ] **Step 1: Write the failing tests**

Create `api/tests/test_telemetry.py`:

```python
import json

from artistpath_api.telemetry import emit, safe_journey_id


def test_accepts_a_well_formed_journey_id():
    assert safe_journey_id("abc12345-XYZ") == "abc12345-XYZ"


def test_replaces_a_missing_journey_id():
    assert safe_journey_id(None) == "unknown"


def test_replaces_an_over_long_journey_id():
    assert safe_journey_id("a" * 65) == "unknown"


def test_replaces_a_journey_id_with_forbidden_characters():
    # A newline plus JSON punctuation is how a second log record gets injected.
    assert safe_journey_id('x"}\n{"event":"path"') == "unknown"


def test_emits_one_line_of_valid_json(capsys):
    emit({"event": "path", "journey_id": "j1", "nested": {"a": 1}})
    out = capsys.readouterr().out
    assert out.count("\n") == 1
    assert json.loads(out) == {"event": "path", "journey_id": "j1", "nested": {"a": 1}}


def test_a_value_containing_json_punctuation_is_escaped_not_injected(capsys):
    emit({"event": "path", "name": 'Bad" }\n{"event":"fake'})
    out = capsys.readouterr().out
    assert out.count("\n") == 1
    assert json.loads(out)["name"] == 'Bad" }\n{"event":"fake'
```

- [ ] **Step 2: Run and verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_telemetry.py -v`
Expected: collection error — `ModuleNotFoundError: No module named 'artistpath_api.telemetry'`.

- [ ] **Step 3: Create the module**

Create `api/src/artistpath_api/telemetry.py`:

```python
"""Structured-JSON telemetry on stdout.

App Runner ships stdout to CloudWatch Logs with no configuration, which is why
this is the whole telemetry mechanism and there is no client, no buffer and no
new infrastructure (DEP-2).

Events carry FACTS, never computed metrics. Routing is deterministic, so any
quality metric can be derived offline from the logged inputs against the frozen
top-1%-by-degree set — and choosing which metric production computes would be a
scoring decision taken while path-quality work is paused (DEP-7).
"""

from __future__ import annotations

import json
import re

# Bounded and charset-restricted because the value arrives in a client-supplied
# header and lands in a log line that analysis will parse (DEP-27).
_JOURNEY_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")

UNKNOWN_JOURNEY = "unknown"


def safe_journey_id(raw: str | None) -> str:
    """Return the id if it is well-formed, else a constant placeholder."""
    if raw and _JOURNEY_ID.match(raw):
        return raw
    return UNKNOWN_JOURNEY


def emit(event: dict) -> None:
    """Write one event as a single line of JSON.

    json.dumps, never string formatting: a value containing a newline and JSON
    punctuation would otherwise inject a second, fabricated record into the
    telemetry this exists to collect.
    """
    print(json.dumps(event, separators=(",", ":"), default=str), flush=True)
```

- [ ] **Step 4: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **178 passed**.

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/telemetry.py api/tests/test_telemetry.py
git commit -m "Add the structured-JSON telemetry emitter with a bounded journey id (DEP-27)"
```

---

## Task 8: Emit the `path` event

**Files:**
- Modify: `api/src/artistpath_api/app.py` — `build_path`
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: `emit`, `safe_journey_id` (Task 7).
- Produces: the `path` event shape consumed by offline analysis.

- [ ] **Step 1: Write the failing test**

Append to `api/tests/test_app.py`:

```python
import json


def test_path_request_emits_a_telemetry_event(capsys):
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": store.mbids[1], "reason": "known"}]},
        headers={"x-journey-id": "journey-0001"},
    )
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("{")]
    events = [json.loads(ln) for ln in lines]
    path_events = [e for e in events if e["event"] == "path"]
    assert len(path_events) == 1
    ev = path_events[0]
    assert ev["journey_id"] == "journey-0001"
    assert ev["source"]["mbid"] == a
    assert ev["target"]["mbid"] == b
    assert ev["bypass_depth"] == 1
    assert ev["known_count"] == 1
    assert ev["dislike_count"] == 0
    assert ev["stop_rule"] in ("natural", "forced", "adjacent_only")
    assert [p["mbid"] for p in ev["path"]][0] == a
    assert isinstance(ev["duration_ms"], (int, float))
```

- [ ] **Step 2: Run and verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_app.py -k emits_a_telemetry -v`
Expected: FAIL — no lines starting with `{`, so `path_events` is empty.

- [ ] **Step 3: Emit the event**

In `api/src/artistpath_api/app.py`, add at the top:

```python
import time

from fastapi import FastAPI, HTTPException, Request, Response

from artistpath_api.telemetry import emit, safe_journey_id
```

Change the `build_path` signature to take the request, and wrap the call:

```python
    @app.post("/api/path")
    def build_path(req: PathRequest, request: Request) -> PathResponse:
        if len(req.sources) != 2:
            raise HTTPException(422, "alpha supports exactly two source artists")
        ids = [store.id_by_mbid.get(m) for m in req.sources]
        if any(i is None for i in ids):
            raise HTTPException(404, "unknown artist")
        source, target = ids
        if source == target:
            raise HTTPException(
                422, "pick two different artists — a journey needs somewhere to go"
            )
        excludes = _to_exclusions(store, req.exclude)
        started = time.perf_counter()
        journey = find_journey(store, source, target, excludes, cfg)
        duration_ms = (time.perf_counter() - started) * 1000.0
        if journey is None:
            raise HTTPException(409, "no path avoiding those artists")
        path, stop_rule = journey

        emit(
            {
                "event": "path",
                "journey_id": safe_journey_id(request.headers.get("x-journey-id")),
                "source": {"mbid": store.mbids[source], "name": store.names[source]},
                "target": {"mbid": store.mbids[target], "name": store.names[target]},
                # The full accumulated list is what makes a walk reconstructible
                # from a single event, without depending on neighbouring records.
                "exclude": [{"id": e.id, "reason": e.reason} for e in req.exclude],
                "bypass_depth": len(req.exclude),
                "dislike_count": sum(1 for e in req.exclude if e.reason == DISLIKE),
                "known_count": sum(1 for e in req.exclude if e.reason == KNOWN),
                # Logged although reproducible from the inputs, so offline
                # analysis can VERIFY that the deployed router reproduces what
                # the user actually saw — config or artifact drift is a failure
                # class this project has met before (DEP-14).
                "path": [
                    {"mbid": store.mbids[n], "name": store.names[n]} for n in path
                ],
                "stop_rule": stop_rule,
                "duration_ms": round(duration_ms, 2),
            }
        )

        return PathResponse(
            artists=[artist_out(n) for n in path], stop_rule=stop_rule
        )
```

- [ ] **Step 4: Allow the header through CORS**

Still in `api/src/artistpath_api/app.py`, change the middleware's `allow_headers` (line 45):

```python
        allow_headers=["content-type", "x-journey-id"],
```

Without this, any cross-origin use preflights the custom header and is rejected. Production is same-origin so no preflight fires — which is exactly why this would surface later, at the worst moment.

- [ ] **Step 5: Run the full suite**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: **179 passed**.

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/app.py api/tests/test_app.py
git commit -m "Emit the path telemetry event (DEP-2, DEP-14)"
```

---

## Task 9: Emit the `clip` event, and send the journey id from the browser

**Files:**
- Modify: `api/src/artistpath_api/app.py` — `get_track`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/playwright.config.ts`
- Test: `api/tests/test_app.py`, `frontend/src/api/client.test.ts`

**Interfaces:**
- Consumes: `emit`, `safe_journey_id` (Task 7).
- Produces: nothing later depends on.

**Why the clip event carries the journey id too.** Without it you cannot ask "did *this* journey have silent cards" — and three independent mechanisms produce a silent card, all visually identical to each other, to upstream rate limiting, and to the closed C1 defect. This event is the only instrument that separates them (`TR-15`).

- [ ] **Step 1: Write the failing API test**

Append to `api/tests/test_app.py`:

```python
def test_track_request_emits_a_clip_event(capsys):
    client, store = _client()
    client.get(
        f"/api/artists/{store.mbids[0]}/track",
        headers={"x-journey-id": "journey-0002"},
    )
    events = [
        json.loads(ln)
        for ln in capsys.readouterr().out.splitlines()
        if ln.startswith("{")
    ]
    clip_events = [e for e in events if e["event"] == "clip"]
    assert len(clip_events) == 1
    ev = clip_events[0]
    assert ev["journey_id"] == "journey-0002"
    assert ev["mbid"] == store.mbids[0]
    assert ev["resolved"] is False   # the test fetcher returns no clip
    assert ev["source"] is None
    assert isinstance(ev["duration_ms"], (int, float))
```

- [ ] **Step 2: Run and verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_app.py -k clip_event -v`
Expected: FAIL — `clip_events` is empty.

- [ ] **Step 3: Emit the clip event**

In `api/src/artistpath_api/app.py`, replace `get_track`:

```python
    @app.get("/api/artists/{mbid}/track")
    async def get_track(mbid: str, request: Request, response: Response):
        node = store.id_by_mbid.get(mbid)
        if node is None:
            raise HTTPException(404, "unknown artist")
        started = time.perf_counter()
        clip = await resolver.resolve(mbid, store.names[node])
        duration_ms = (time.perf_counter() - started) * 1000.0

        emit(
            {
                "event": "clip",
                "journey_id": safe_journey_id(request.headers.get("x-journey-id")),
                "mbid": mbid,
                "name": store.names[node],
                "resolved": clip is not None,
                # Which catalogue answered. Three separate mechanisms produce a
                # silent card and they are visually identical; this is what
                # separates them (TR-15).
                "source": clip.source if clip else None,
                "duration_ms": round(duration_ms, 2),
            }
        )

        if clip is None:
            response.status_code = 204
            return None
        return TrackOut(
            preview_url=clip.preview_url, title=clip.title, cover_url=clip.cover_url
        )
```

`Clip` does not currently carry `source`. In `api/src/artistpath_api/clips.py`, add it to the dataclass (line 45-51):

```python
@dataclass(frozen=True, slots=True)
class Clip:
    """What a card plays. Short-lived: `preview_url` is signed and expires."""

    preview_url: str
    title: str
    cover_url: str
    source: str = ""  # "deezer" | "itunes" — for telemetry, not for the wire
```

and pass it at both `return Clip(...)` sites inside `resolve`: `Clip(url, identity.title, identity.cover_url, identity.source)`.

- [ ] **Step 4: Send the id from the browser**

In `frontend/src/api/client.ts`, add after the `BASE` constant:

```typescript
/**
 * One id per page session, so a sequence of bypass presses reads as one walk.
 *
 * Deliberately NOT in the URL: path state is the shareable artifact and the
 * bug-report artifact, and an analytics id has no business in it. Resets on
 * reload, so one human walk can log as two — the full exclusion list is in
 * every event, so walks stay reconstructible regardless.
 */
const JOURNEY_ID = crypto.randomUUID().slice(0, 32);

function withJourney(headers: Record<string, string> = {}): Record<string, string> {
  return { ...headers, 'x-journey-id': JOURNEY_ID };
}
```

Then add the header to both `buildPath` and `getTrack`:

```typescript
  const r = await fetch(`${BASE}/path`, {
    method: 'POST',
    headers: withJourney({ 'content-type': 'application/json' }),
    body: JSON.stringify({ sources, exclude }),
    signal,
  });
```

```typescript
  const r = await fetch(`${BASE}/artists/${encodeURIComponent(mbid)}/track`, {
    signal,
    headers: withJourney(),
  });
```

- [ ] **Step 5: Add the frontend test**

Append to `frontend/src/api/client.test.ts`:

```typescript
it('sends a journey id header on both calls', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true, status: 200, json: async () => ({ artists: [], stop_rule: 'natural' }),
  });
  vi.stubGlobal('fetch', fetchMock);

  await buildPath(['a', 'b'], []);
  const headers = fetchMock.mock.calls[0][1].headers;
  expect(headers['x-journey-id']).toMatch(/^[A-Za-z0-9-]{8,64}$/);
});
```

- [ ] **Step 6: Fix the Playwright output directory**

In `frontend/playwright.config.ts`, add to the top-level config object:

```typescript
  // Outside the OneDrive-synced tree: the default location fails with
  // EPERM on rmdir, and a manually-run regression gate that errors on its
  // default invocation is a gate people stop running (DEP-30, TR-17).
  outputDir: '../.playwright-results',
```

Add `.playwright-results/` to `.gitignore`.

- [ ] **Step 7: Run everything**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd ../frontend && npm test && npm run build
```

Expected: api **180 passed**; frontend **65 passed**; build succeeds.

- [ ] **Step 8: Commit**

```bash
git add api/src/artistpath_api/app.py api/src/artistpath_api/clips.py api/tests/test_app.py \
        frontend/src/api/client.ts frontend/src/api/client.test.ts \
        frontend/playwright.config.ts .gitignore
git commit -m "Emit the clip event and send the journey id from the browser (TR-15, TR-17)"
```

---

## Task 10: Verify the telemetry round-trip against the real graph

**Files:** none modified — this is the verification `DEP-16` requires before telemetry is used for anything.

**Why.** The design's §5 rests on production routing being identical to analysis routing. `DEP-14` logs the resulting path so the failure is *detectable* rather than assumed. **This must pass before any conclusion is drawn from telemetry**, and it is cheap.

- [ ] **Step 1: Boot the API on the adopted artifact**

```bash
cd api
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run uvicorn artistpath_api.app:build_default_app \
  --factory --port 8000
```

- [ ] **Step 2: Confirm `/health` reports the adopted artifact**

```bash
curl -s http://127.0.0.1:8000/health
```

Expected: `graph_sha256` matching the value in `docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`, which **owns that figure — read it from there, do not transcribe it from anywhere else.** `artists` and `edges` must match the manifest sidecar `builder/scratch/graph-t15-tiebreakfix.bin.json`.

- [ ] **Step 3: Make a path request and capture the event**

Search two artists via `GET /api/artists/search?q=…`, take their mbids, and POST to `/api/path`. Copy the emitted `path` event from the server's stdout.

- [ ] **Step 4: Replay the event's inputs offline and compare**

Write a throwaway script under the scratch directory that loads the same artifact via `load_graph`, calls `find_journey` with the event's `source`, `target` and `exclude`, and asserts the resulting mbid sequence equals the event's `path`.

- [ ] **Step 5: Record the result**

If it reproduces, `DEP-16` is discharged — record that in the execution log. **If it does not, stop**: telemetry cannot be used for any conclusion until the divergence is explained, and that is a finding, not a bug to work around.

- [ ] **Step 6: Run the e2e suite, now a mandatory gate**

```bash
cd frontend && npm run test:e2e
```

Expected: 3 passed against the live API. Per `DEP-30` this is now a required manual step before any deploy.

---

## Definition of done for Track A

- [ ] All four suites green: **api 180**, builder 115, frontend 65, e2e 3.
- [ ] `snyk_code_scan` run on `api/` (the global instruction bites once first-party code is modified) and any finding fixed and rescanned until clean.
- [ ] `DEP-16` discharged by Task 10, or its failure recorded as a finding.
- [ ] Execution log started at `docs/superpowers/2026-07-26-gate2-track-a-execution-log.md`, appended **per task**, not at closeout.
- [ ] PR #27 updated.

**Then Track D** (frontend, six fenced items), then Track B (infrastructure), then Track C (cutover). Both AWS-free tracks land before infrastructure so the deploy ships an already-fixed app.
