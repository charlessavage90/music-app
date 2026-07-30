# Removing the password: load hardening and a Cloudflare front door

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Role: COMPLETE except `PW-9` — executed through `PW-8` and DEPLOYED 2026-07-28; the
password is off and `https://musicapp.cmiller.io` is live.** Marked 2026-07-30 by a doc
audit: this line read ACTIVE for two days after the work shipped. **`PW-9` (the
concurrency ladder) is the one unrun task, deliberately open** — gated on the owner's
approval, blocks nothing, and tracked in `NEXT.md`, which owns its status; do not read
this plan as having live next actions. *(Original role: ACTIVE — the governing document
for this work.)* It supersedes nothing. It implements a **subset** of
`findings/2026-07-27-gate2-gate3-team-review.md`, which remains AUTHORITATIVE for the
findings themselves and their triage. Where this plan describes a finding, the review
wins.

**Goal:** Make the live app safe to run without the shared password, so friends and family can
use it by following a link — **without opening Gate 3**.

**Architecture:** The password is currently doing three jobs: access control, rate limiting, and
throttling the clip fan-out to Deezer/iTunes. This plan replaces the second and third with real
mechanisms and then removes the password. A Cloudflare free-tier front door on a subdomain the
owner already controls takes over rate limiting (replacing the AWS WAF the review assumed); the
API gains bounded requests, a catalogue circuit breaker, and a health check that cannot be
starved. CloudFront and App Runner are unchanged in shape — `max_size=2` stays exactly as it is,
deliberately.

**Tech stack:** Python 3.12 / FastAPI / Pydantic v2 (`api/`), AWS CDK v2 in Python (`infra/`),
CloudFront Functions (JS 2.0), Cloudflare free tier (DNS, WAF, Rate Limiting, Transform Rules),
pytest, node (for the viewer-function tests).

---

## Identifiers

**Tasks are namespaced `PW-` (password withdrawal).** Verified unused: `grep -n '\bPW-[0-9]'`
across the repo returns zero matches. Do not reuse `A1`–`A9`, `S1`–`S7`, `Q1`–`Q8`, `F1`–`F11`
bare — those are the review's, and bare forms collide with Track 2 arms, closeout items, and the
`TR-`/`ARC-`/`SEC-`/`QUA-`/`FRO-`/`DEP-`/`MIG-` series. Cite review findings in their `G3-` form.
**Forward-only: nothing here is renamed once committed.**

## Why there is no factor table

`CLAUDE.md` requires a factor table in any plan comparing variants. **This plan compares
nothing** — it is remediation against a fixed set of named findings, with one arm. There is no
baseline to isolate and no result to read. The check that replaces it is the per-task
verification step: every task states what must be true afterwards and how it is observed.

## Claims checked against the repo before writing

Per `CLAUDE.md`, every file, function, and config value below was grepped or read. All resolve.

| Claim | Verified at | Result |
|---|---|---|
| `sources` unbounded, `exclude` bounded at 200 | `api/src/artistpath_api/models.py:16`, `:21` | Confirmed |
| No rate limiting of any kind | grep `waf\|rate_limit\|throttl` over `infra/` | Zero hits |
| 429 is indistinguishable from a miss | `clips.py:178-184` (`except Exception: return {}`) | Confirmed |
| A throttled Deezer is asked three times | `clips.py:196-219` (`_preview_url` → `_search` → `_from_deezer` → `_from_itunes`) | Confirmed |
| `/health` is a sync `def` | `app.py:181-182` | Confirmed |
| Single uvicorn worker | `api/Dockerfile:22` — no `--workers` | Confirmed |
| Gate and SPA fallback are one function | `infra/src/artistpath_infra/viewer_function.js` | Confirmed |
| SPA calls the API relatively | `frontend/src/api/client.ts:3` — `?? '/api'` | Confirmed |
| No `cloudfront.net` literal in code | full-tree grep incl. gitignored dirs | Zero hits |
| `DeployInputs` carries `site_password` | `stack.py:46`, `infra/app.py:65`, `tests/test_stack.py:19` | Confirmed, three call sites |
| Log retention is a **manual runbook step**, not code | `infra/README.md` §5a | Confirmed — see PW-8 |

**One correction to the review, and it is in our favour.** G3-A3 says "no log retention set
anywhere." That is true *of the code* but `infra/README.md` §5a is a required manual step setting
90 days, added 2026-07-27. Whether it was actually run against the live service is unknown.
PW-8 verifies rather than assumes.

## Global constraints

- **The site hostname is `musicapp.cmiller.io`.** Chosen 2026-07-28; the owner has confirmed it
  is permanent, which is what closes G3-A5 rather than merely deferring it. It reaches the code
  only through `ARTISTPATH_SITE_HOSTNAME` in `infra/.env.deploy` — **never hardcode it**; the
  test fixtures use `artistpath.test.invalid` deliberately.
- **Cloudflare free-tier allowance, confirmed in the owner's dashboard 2026-07-28:** 1 rate
  limiting rule, 5 custom security rules, 3 page rules, cache settings. **None in use today.**
  PW-6 spends the single rate-limiting rule. The five custom rules are deliberately left unspent
  as headroom — they are the lever if one IP-keyed rule proves too blunt, and spending them now
  would be adding controls with no evidence they are needed.
- **`UV_LINK_MODE=copy` is NOT required in `C:\dev\music-app`** — measured during the migration.
  It is still required in the old OneDrive tree. `CLAUDE.md` still states it unconditionally;
  that is migration Task 12's business and must not be "fixed" here.
- **`PYTHONIOENCODING=utf-8`** on anything printing artist names.
- **`python -u` / `PYTHONUNBUFFERED=1`** on any backgrounded job, or it writes a 0-byte log and
  looks dead.
- **Branch off `main`, push the branch on the first commit, open a draft PR early.** Nothing is
  committed directly to `main`.
- **Run the package's suite before every commit**, from the package directory:
  `uv run --extra dev pytest -q` (`api/`, `infra/`), `npm test` (`frontend/`).
- **`max_size=2` in `stack.py:159-165` must not be raised by this work.** It is the cost ceiling.
  The capacity problem is being met by shedding load at the edge, not by scaling — which is
  precisely why G3-A3 (the knob that caps the bill is the knob that caps capacity) does not fire.
  A future session "helpfully" raising it deletes the only automatic spend control.
- **Every magic number goes in `ApiConfig`** (`api/src/artistpath_api/config.py`) or
  `DeployInputs` (`infra/src/artistpath_infra/stack.py`). Nowhere else.
- **Quantities name their currency** — see `CLAUDE.md`. Nothing here is popularity- or
  degree-derived, so the rule is satisfied by not introducing any.

---

## Handoff seam — read this before starting

This plan is **nine tasks**, which is past the point `CLAUDE.md` says a controller's context
starts to matter. It has **one seam, after PW-4**, chosen at authoring time:

> **PW-1 → PW-4 (Track A) is pure API work.** No AWS, no Cloudflare, no credentials, no owner
> involvement. Its output is committed, tested code that is independently valuable and safe to
> merge on its own — the request bounds and the circuit breaker improve the app whether or not
> the password ever comes off.
>
> **PW-5 → PW-9 (Track B) is the front door.** It needs the owner's AWS account and his
> Cloudflare dashboard, and it is where the password actually comes off.

**Retire the session at the seam.** Append to the execution log per task, not at the end. A
material mid-flight amendment is also a seam.

## Order is a safety property, not a preference

Track B is ordered so that **every step before PW-7 is additive and reversible, with the password
still on.** The certificate and alternate domain (PW-5) do not disturb the existing hostname.
The Cloudflare front door (PW-6) is verified end to end *while still password-protected*. Only
PW-7 removes the password, and by then the rate limiting it is replacing is already live and
observed working.

**Do not reorder to remove the password earlier.** The whole point is that the replacement
throttle is proven before the existing one is withdrawn.

---

# Track A — API hardening

## Task PW-1: Bound the request surface

Closes **G3-S3** (*a request can carry an unlimited list of artists, and we read all of it before
checking there are only two*) and the amplification half of **G3-S4** (*attacker-supplied text is
copied verbatim into the logs, which are billed per gigabyte*).

These are one task because they are one fix: the 20 MB of CloudWatch the review measured came
from unbounded id strings being echoed into the telemetry line at `app.py:130`. Bounding the
strings closes both.

**Files:**
- Modify: `api/src/artistpath_api/models.py`
- Modify: `api/src/artistpath_api/config.py`
- Modify: `api/src/artistpath_api/app.py` (add body-size middleware)
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `ApiConfig.max_body_bytes: int`. No signature changes.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_app.py`:

```python
def test_an_oversized_sources_array_is_rejected_by_the_schema():
    # G3-S3: a 2,000,000-element array cost 442 ms and buffered ~70 MB before
    # the `len(...) != 2` check in build_path rejected it. The bound has to be
    # in the schema, which runs before the handler, not in the handler.
    client, store = _client()
    r = client.post("/api/path", json={"sources": ["x"] * 5000, "exclude": []})
    assert r.status_code == 422


def test_an_oversized_exclusion_id_is_rejected():
    # G3-S4: ExclusionIn.id is echoed verbatim into the telemetry line, so an
    # unbounded string is a log-volume amplifier billed per GB, not only a
    # parse cost. Measured at 1:1 amplification.
    client, store = _client()
    r = client.post(
        "/api/path",
        json={
            "sources": [store.mbids[0], store.mbids[2]],
            "exclude": [{"id": "z" * 5000, "reason": "dislike"}],
        },
    )
    assert r.status_code == 422


def test_an_oversized_exclusion_reason_is_rejected():
    # `reason` is normalised to dislike/known in _to_exclusions, but the RAW
    # value is what app.py logs. Bounding it at the normalisation would not
    # bound the log line.
    client, store = _client()
    r = client.post(
        "/api/path",
        json={
            "sources": [store.mbids[0], store.mbids[2]],
            "exclude": [{"id": store.mbids[1], "reason": "z" * 5000}],
        },
    )
    assert r.status_code == 422


def test_a_body_over_the_limit_is_refused_before_parsing():
    # The schema bounds cannot fire until the whole body has been read into
    # memory. This is the cheap guard in front of that.
    client, store = _client()
    r = client.post(
        "/api/path",
        content=b'{"sources":[],"exclude":[]}' + b" " * (CFG.max_body_bytes + 1),
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 413


def test_an_ordinary_two_artist_request_still_works():
    # The half a bounds test cannot see on its own: a limit set too tight
    # refuses real traffic, and every test above passes when it does.
    client, store = _client()
    r = client.post(
        "/api/path",
        json={
            "sources": [store.mbids[0], store.mbids[2]],
            "exclude": [{"id": store.mbids[1], "reason": "dislike"}],
        },
    )
    assert r.status_code == 200
```

- [ ] **Step 2: Run them and confirm they fail**

```bash
cd api && uv run --extra dev pytest -q -k "oversized or body_over or ordinary_two_artist"
```

Expected: the four bound tests FAIL (they return 200 or 422-for-the-wrong-reason);
`test_an_ordinary_two_artist_request_still_works` PASSES already. That last one failing now
means the fixture is wrong, not the code.

- [ ] **Step 3: Add the bounds to `models.py`**

Replace `ExclusionIn` and `PathRequest`:

```python
from typing import Annotated, Literal

from pydantic import BaseModel, Field

# Long enough for a 36-character MBID with headroom, short enough that 200 of
# them cannot amplify into a meaningful log line. Not exactly 36: an id that is
# merely unknown should reach the handler and be skipped (or 404) with a
# message a person can read, rather than become a schema error.
_MBID_MAX = 64

Mbid = Annotated[str, Field(max_length=_MBID_MAX)]


class ExclusionIn(BaseModel):
    # Both fields are bounded because both are echoed VERBATIM into the
    # telemetry line (app.py's "exclude" key), so an unbounded string here is a
    # log-volume amplifier as well as a parse cost — measured at 1:1 into
    # CloudWatch, billed per GB, with no other sink (G3-S3, G3-S4).
    id: Mbid
    # Normalised to DISLIKE/KNOWN in app.py's _to_exclusions, but logged RAW,
    # so the bound belongs here and not at the normalisation. Deliberately NOT
    # a Literal: an unrecognised reason currently falls back to DISLIKE rather
    # than failing the request, and changing that is a behaviour change this
    # task is not making.
    reason: str = Field(max_length=16)


class PathRequest(BaseModel):
    # Bounded for the same reason `exclude` was, and it was the gap beside it:
    # a 2,000,000-element array cost 442 ms and buffered ~70 MB before the
    # `len(...) != 2` check in build_path rejected it (G3-S3). Alpha passes
    # exactly two. 8 rather than 2 so the handler's readable 422 ("alpha
    # supports exactly two source artists") stays reachable for the realistic
    # mistake, instead of being replaced by a schema error.
    sources: list[Mbid] = Field(max_length=8)
    # Bounded because avoidance_map runs a fresh graph traversal per entry
    # (pathfinding.py), so an unbounded list is arbitrary attacker-controlled
    # CPU on a GIL-bound handler. 200 is above the deepest real use recorded
    # (a 100-press dogfooding run) with headroom. TR-12 / DEP-25.
    exclude: list[ExclusionIn] = Field(default_factory=list, max_length=200)
```

- [ ] **Step 4: Add the body limit to `config.py`**

In the `ApiConfig` dataclass, after the `--- search ---` block:

```python
    # --- request bounds (G3-S3) -----------------------------------------
    # A body larger than this is refused before it is parsed. The schema bounds
    # in models.py cannot fire until the whole body has been read into memory,
    # which is the cost being avoided. 64 KiB is ~30x the largest legitimate
    # request (200 exclusions at 64 bytes of id plus JSON overhead).
    max_body_bytes: int = 64 * 1024
```

- [ ] **Step 5: Add the middleware to `app.py`**

In `create_app`, immediately after the `add_middleware(CORSMiddleware, ...)` call and **before**
the `if cfg.origin_secret:` block:

```python
    @app.middleware("http")
    async def limit_body_size(request: Request, call_next):
        """Refuse an oversized body before Starlette reads it into memory.

        Content-Length only. A chunked request without the header still gets
        buffered and is bounded only by the schema — recorded as a deferral in
        this plan rather than fixed, because CloudFront and Cloudflare both
        send Content-Length and reading the stream to count it would cost more
        than the case is worth (G3-S3).
        """
        declared = request.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > cfg.max_body_bytes:
            return JSONResponse({"detail": "request body too large"}, status_code=413)
        return await call_next(request)
```

- [ ] **Step 6: Run the tests**

```bash
cd api && uv run --extra dev pytest -q
```

Expected: all five new tests PASS, and the full suite stays green (195 before this task).

- [ ] **Step 7: Commit**

```bash
git add api/src/artistpath_api/models.py api/src/artistpath_api/config.py \
        api/src/artistpath_api/app.py api/tests/test_app.py
git commit -m "PW-1: bound the request surface (G3-S3, G3-S4 amplification half)"
```

---

## Task PW-2: Take `/health` off the thread pool

Closes the **feedback-loop half of G3-A1** (*the site does not slow down under load, it restarts
itself*).

`/health` is a sync `def`, so FastAPI runs it in Starlette's thread pool — the same 40-slot pool
that runs `build_path`. That is why the review measured it at 22.09 s under 40 concurrent path
requests, against App Runner's 5 s health-check timeout: not CPU starvation, **queueing**. Five
misses at a 10 s interval and App Runner replaces the instance, load shifts to the other, which
fails identically. A coroutine runs on the event loop and never queues behind a saturated pool.

**This is one keyword and it is load-bearing.** It does not make the app faster under load; it
stops slow from becoming an outage. Do not drop it as trivial.

**`search_artists` and `build_path` must stay sync `def`.** They do real work; on the event loop
they would block every other request. Only `/health` qualifies, because it reads three in-memory
attributes and returns.

**Files:**
- Modify: `api/src/artistpath_api/app.py:181-190`
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing. `/health`'s response body is unchanged.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_app.py` (add `import asyncio`, `import inspect`, `import threading`,
and `import anyio` at the top):

```python
def test_health_is_a_coroutine_so_it_never_queues_for_a_thread():
    # G3-A1's feedback loop. /health shares Starlette's thread pool with
    # build_path; the review measured it at 22.09 s under 40 concurrent path
    # requests against a 5 s App Runner timeout, and five misses replace the
    # instance. Asserted by introspection as well as behaviourally because the
    # regression is a single keyword: `async def` reverted to `def` is
    # invisible to every test that does not saturate the pool first.
    client, _ = _client()
    route = next(r for r in client.app.routes if getattr(r, "path", "") == "/health")
    assert inspect.iscoroutinefunction(route.endpoint), (
        "/health is a sync def and will queue behind saturated path requests"
    )


def test_health_answers_while_every_thread_pool_slot_is_occupied():
    """The behavioural half: the property, not the keyword.

    Occupies every thread-pool slot with a blocking sync endpoint, then asks
    for /health. A sync /health cannot answer until a slot frees, which is the
    22.09 s the review measured. A coroutine answers immediately.
    """
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    from artistpath_api.app import create_app

    client, _ = _client()
    app = client.app

    release = threading.Event()

    @app.get("/blocking-probe")
    def blocking_probe():  # sync on purpose: it consumes a pool slot
        release.wait(timeout=10)
        return {"ok": True}

    async def exercise():
        limiter = anyio.to_thread.current_default_thread_limiter()
        original = limiter.total_tokens
        limiter.total_tokens = 2  # saturate cheaply rather than spawning 40
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as ac:
                blockers = [
                    asyncio.create_task(ac.get("/blocking-probe")) for _ in range(2)
                ]
                await asyncio.sleep(0.2)  # let both claim their slot
                r = await asyncio.wait_for(ac.get("/health"), timeout=2.0)
                assert r.status_code == 200
                release.set()
                await asyncio.gather(*blockers)
        finally:
            release.set()
            limiter.total_tokens = original

    asyncio.run(exercise())
```

- [ ] **Step 2: Run them and confirm they fail**

```bash
cd api && uv run --extra dev pytest -q -k "health_is_a_coroutine or health_answers_while"
```

Expected: the first FAILS on the assertion message; the second FAILS with
`asyncio.TimeoutError` after 2 s. **If the second passes before the fix, stop** — the pool was
not actually saturated and the test is vacuous.

- [ ] **Step 3: Make `/health` a coroutine**

In `api/src/artistpath_api/app.py`, replace the `/health` handler:

```python
    @app.get("/health")
    async def health() -> HealthOut:
        # `async def`, deliberately and load-bearingly (G3-A1). A sync def runs
        # in Starlette's 40-slot thread pool — the same pool as build_path — so
        # under concurrent path requests /health queues rather than answers:
        # measured at 22.09 s against App Runner's 5 s timeout, and five misses
        # replace the instance while the other one inherits the load and fails
        # the same way. The site did not degrade, it cycled.
        #
        # Safe on the event loop because this reads three in-memory attributes
        # and does no I/O. search_artists and build_path do NOT qualify: on the
        # event loop they would block every other request.
        #
        # Deliberately NOT under /api — App Runner's health checker reaches the
        # origin directly, not through the CloudFront /api/* behaviour.
        return HealthOut(
            status="ok",
            graph_sha256=store.source_sha256,
            artists=store.artist_count,
            edges=len(store.neighbours),
        )
```

- [ ] **Step 4: Run the tests**

```bash
cd api && uv run --extra dev pytest -q
```

Expected: both new tests PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/app.py api/tests/test_app.py
git commit -m "PW-2: /health off the thread pool, breaking G3-A1's restart cascade"
```

---

## Task PW-3: Tell a throttled catalogue apart from a missing track

First half of **G3-A4 / G3-S2** (*when Deezer throttles us we cannot tell that from "no such
track", so we ask three times instead of once and harden the block*).

`_get` swallows every exception into `{}` (`clips.py:178-184`), so a 429 looks exactly like a
404. `resolve` then falls through cache-hit → search → iTunes, meaning **one user request
becomes two Deezer calls plus one iTunes call** while Deezer is already refusing us. This is the
specific thing `viewer_function.js`'s own comment names as the reason the password exists.

The fix keeps the injection boundary the existing comment defends: this module still must not
name httpx's exception types. The **injected fetcher** classifies the transport failure and
raises a type this module owns.

**Files:**
- Modify: `api/src/artistpath_api/clips.py`
- Modify: `api/src/artistpath_api/app.py` (`build_default_app`'s `fetch_json`)
- Test: `api/tests/test_clips.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `clips.CatalogueUnavailable(Exception)`. `ClipResolver.resolve` keeps its signature
  `async def resolve(self, mbid: str, artist_name: str) -> Clip | None`. PW-4 consumes
  `CatalogueUnavailable`.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_clips.py`:

```python
import pytest

from artistpath_api.clips import CatalogueUnavailable


def _counting_fetcher(behaviour):
    """Record every outbound call and reply per-URL from `behaviour`."""
    calls = []

    async def fetch(url, params):
        calls.append(url)
        result = behaviour(url)
        if isinstance(result, Exception):
            raise result
        return result

    return fetch, calls


@pytest.mark.anyio
async def test_a_throttled_deezer_is_not_asked_again_for_the_same_artist():
    # G3-A4: the cached-identity path re-signs a URL through /track. When that
    # comes back 429, falling through to _search asks the SAME service twice
    # more — 3 outbound calls per user request, against a service that is
    # already refusing us. One call is the correct number.
    cfg = ApiConfig()
    cache = InMemoryClipCache()
    await cache.put(
        "mbid-1",
        TrackIdentity(source="deezer", track_id="99", title="t", cover_url="c"),
    )

    def behaviour(url):
        if "deezer" in url:
            raise CatalogueUnavailable("429")
        return {}

    fetch, calls = _counting_fetcher(behaviour)
    resolver = ClipResolver(cfg, cache, fetch)

    clip = await resolver.resolve("mbid-1", "Some Artist")

    assert clip is None
    deezer_calls = [c for c in calls if "deezer" in c]
    assert len(deezer_calls) == 1, f"asked a throttled Deezer {len(deezer_calls)} times"


@pytest.mark.anyio
async def test_a_track_that_left_the_catalogue_still_falls_through_to_a_search():
    # The half the fix must not break. A 404 for a withdrawn track is a genuine
    # miss and re-searching is correct — that is what keeps a card playable
    # when a track disappears. Only *unavailability* stops the fall-through.
    cfg = ApiConfig()
    cache = InMemoryClipCache()
    await cache.put(
        "mbid-1",
        TrackIdentity(source="deezer", track_id="99", title="t", cover_url="c"),
    )

    def behaviour(url):
        if url.endswith("/99"):
            return {}  # withdrawn track: no "preview" key
        if "deezer.com/search" in url:
            return {
                "data": [
                    {
                        "preview": "https://cdn/p.mp3",
                        "id": 7,
                        "title": "New",
                        "artist": {"name": "Some Artist", "picture_medium": "c"},
                    }
                ]
            }
        return {}

    fetch, calls = _counting_fetcher(behaviour)
    resolver = ClipResolver(cfg, cache, fetch)

    clip = await resolver.resolve("mbid-1", "Some Artist")

    assert clip is not None and clip.preview_url == "https://cdn/p.mp3"


@pytest.mark.anyio
async def test_a_throttled_deezer_still_falls_through_to_itunes_on_a_cold_artist():
    # Falling through to a DIFFERENT service is not amplification — it is the
    # fallback working. Only repeat calls to the refusing service are the bug.
    cfg = ApiConfig()

    def behaviour(url):
        if "deezer" in url:
            raise CatalogueUnavailable("429")
        return {
            "results": [
                {
                    "previewUrl": "https://itunes/p.m4a",
                    "trackId": 5,
                    "trackName": "T",
                    "artistName": "Some Artist",
                    "artworkUrl100": "c",
                }
            ]
        }

    fetch, calls = _counting_fetcher(behaviour)
    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch)

    clip = await resolver.resolve("mbid-cold", "Some Artist")

    assert clip is not None and clip.source == "itunes"
    assert len([c for c in calls if "deezer" in c]) == 1
```

If `pytest.mark.anyio` is not already configured in this package, use whatever async-test marker
`api/tests/test_clips.py` already uses — check the top of that file before writing, and match it
rather than introducing a second convention.

- [ ] **Step 2: Run them and confirm they fail**

```bash
cd api && uv run --extra dev pytest -q -k "throttled or left_the_catalogue"
```

Expected: the two `throttled` tests FAIL on the call-count assertion (they will show 2 or 3).
`test_a_track_that_left_the_catalogue_still_falls_through_to_a_search` PASSES already — it is
the regression guard, and it failing now means the fixture is wrong.

- [ ] **Step 3: Add the exception type and re-raise it in `_get`**

In `api/src/artistpath_api/clips.py`, after the `FetchJson` type alias:

```python
class CatalogueUnavailable(Exception):
    """The catalogue refused to answer — throttling or an outage, not a miss.

    Raised by the INJECTED fetcher, never by this module. Naming httpx's
    exception types here would couple the resolver to the transport, which is
    the reason `_get` was broad in the first place; classifying at the fetcher
    keeps that boundary while giving this layer the one distinction it needs.

    The distinction is the whole of G3-A4: a 429 that reads as "no such track"
    makes `resolve` ask the same refusing service twice more, tripling our
    outbound rate exactly when it must fall.
    """
```

Replace `_get`'s body (keep the existing docstring, and add the final paragraph):

```python
        try:
            return await self._fetch(url, params)
        except CatalogueUnavailable:
            # NOT swallowed. This is the one failure the caller must be able to
            # tell from a miss, because the correct response to it is to stop
            # calling rather than to try harder (G3-A4).
            raise
        except Exception:
            # Deliberately broad: the fetcher is injected, so this layer
            # cannot name the transport's exception types without coupling
            # to httpx. Observability for this is a Gate 2 item.
            return {}
```

- [ ] **Step 4: Handle it in `resolve` and `_search`**

Replace `resolve`'s cached-identity branch and `_search` in `clips.py`:

```python
        if identity is not None:
            try:
                url = await self._preview_url(identity)
            except CatalogueUnavailable:
                # The catalogue is throttling us, not missing the track.
                # Falling through to _search would ask the SAME service twice
                # more for the same artist and harden the block (G3-A4). The
                # card is silent for this request; the identity stays cached,
                # so the next request costs one call again once we are let
                # back in.
                return None
            if url:
                return Clip(url, identity.title, identity.cover_url, identity.source)
            # The track has left the catalogue. Identity is stable, not
            # permanent, so fall through and find the artist another one.
```

```python
    async def _search(self, artist_name: str) -> tuple[TrackIdentity, str] | None:
        """Try each catalogue once, skipping any that is refusing us.

        Falling through to a DIFFERENT service is not amplification — it is the
        fallback doing its job. Only repeat calls to the service that is
        already saying no are the defect (G3-A4).
        """
        try:
            found = await self._from_deezer(artist_name)
        except CatalogueUnavailable:
            found = None
        if found is not None:
            return found
        try:
            return await self._from_itunes(artist_name)
        except CatalogueUnavailable:
            return None
```

- [ ] **Step 5: Classify the failure in the production fetcher**

In `api/src/artistpath_api/app.py`, `build_default_app` — add `CatalogueUnavailable` to the
`from artistpath_api.clips import (...)` list and replace `fetch_json`:

```python
    async def fetch_json(url: str, params: dict) -> dict:
        r = await client.get(url, params=params)
        # The only place in the app that knows httpx status codes, which is why
        # the classification lives here rather than in clips.py (G3-A4). 429 is
        # the measured case; 5xx is the same instruction — stop calling — from
        # a different cause.
        if r.status_code == 429 or r.status_code >= 500:
            raise CatalogueUnavailable(f"{r.status_code} from {url}")
        r.raise_for_status()
        return r.json()
```

- [ ] **Step 6: Run the tests**

```bash
cd api && uv run --extra dev pytest -q
```

Expected: the three new tests PASS; full suite green.

- [ ] **Step 7: Commit**

```bash
git add api/src/artistpath_api/clips.py api/src/artistpath_api/app.py api/tests/test_clips.py
git commit -m "PW-3: distinguish a throttled catalogue from a missing track (G3-A4, G3-S2)"
```

---

## Task PW-4: Stop calling a catalogue that is refusing us

Second half of **G3-A4 / G3-S2**. PW-3 stops one request costing three calls. This stops the
*next* thousand requests each costing one, which is what actually keeps the block in place.

Per-process and unsynchronised across instances — adequate at `max_size=2`, and deliberately not
in DynamoDB: a shared breaker would be a write on every clip request, which is the load it
exists to avoid.

**Files:**
- Create: `api/src/artistpath_api/breaker.py`
- Modify: `api/src/artistpath_api/config.py`
- Modify: `api/src/artistpath_api/clips.py`
- Test: `api/tests/test_breaker.py`

**Interfaces:**
- Consumes: `clips.CatalogueUnavailable` (PW-3).
- Produces: `breaker.CatalogueBreaker(threshold: int, cooldown_s: float, now: Callable[[], float] = time.monotonic)`
  with `is_open(source: str) -> bool`, `record_failure(source: str) -> None`,
  `record_success(source: str) -> None`. `ClipResolver.__init__` gains a trailing optional
  parameter `breaker: CatalogueBreaker | None = None` — **optional so every existing call site in
  `app.py` and the test suite keeps working unchanged.**

- [ ] **Step 1: Write the failing tests**

Create `api/tests/test_breaker.py`:

```python
"""The catalogue circuit breaker (G3-A4 / G3-S2).

Time is injected rather than slept, so these are deterministic and instant. A
breaker tested with real sleeps is a breaker whose cooldown nobody re-checks.
"""

from artistpath_api.breaker import CatalogueBreaker


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


def test_a_healthy_source_is_never_open():
    b = CatalogueBreaker(threshold=3, cooldown_s=60.0, now=FakeClock())
    assert not b.is_open("deezer")


def test_it_opens_only_after_the_threshold_is_reached():
    # Off-by-one matters: opening at the first failure would silence cards for
    # a minute over one transient error, which is worse than the defect.
    clock = FakeClock()
    b = CatalogueBreaker(threshold=3, cooldown_s=60.0, now=clock)
    b.record_failure("deezer")
    b.record_failure("deezer")
    assert not b.is_open("deezer")
    b.record_failure("deezer")
    assert b.is_open("deezer")


def test_it_closes_again_once_the_cooldown_has_passed():
    clock = FakeClock()
    b = CatalogueBreaker(threshold=2, cooldown_s=60.0, now=clock)
    b.record_failure("deezer")
    b.record_failure("deezer")
    assert b.is_open("deezer")
    clock.advance(59.0)
    assert b.is_open("deezer")
    clock.advance(2.0)
    assert not b.is_open("deezer")


def test_a_success_clears_the_count():
    # Without this, scattered failures over hours eventually trip the breaker
    # on a service that is working perfectly well.
    b = CatalogueBreaker(threshold=3, cooldown_s=60.0, now=FakeClock())
    b.record_failure("deezer")
    b.record_failure("deezer")
    b.record_success("deezer")
    b.record_failure("deezer")
    assert not b.is_open("deezer")


def test_the_two_catalogues_are_independent():
    # The whole value of the fallback is that one service being down leaves the
    # other usable.
    b = CatalogueBreaker(threshold=1, cooldown_s=60.0, now=FakeClock())
    b.record_failure("deezer")
    assert b.is_open("deezer")
    assert not b.is_open("itunes")
```

Append to `api/tests/test_clips.py`:

```python
@pytest.mark.anyio
async def test_an_open_breaker_makes_no_outbound_call_at_all():
    # The point of the whole task: after the threshold, a refusing service stops
    # being called rather than being called once per request forever.
    cfg = ApiConfig()

    def behaviour(url):
        if "deezer" in url:
            raise CatalogueUnavailable("429")
        return {}

    fetch, calls = _counting_fetcher(behaviour)
    breaker = CatalogueBreaker(threshold=2, cooldown_s=60.0)
    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch, breaker=breaker)

    for _ in range(5):
        await resolver.resolve("mbid-cold", "Some Artist")

    deezer_calls = [c for c in calls if "deezer" in c]
    assert len(deezer_calls) == 2, (
        f"kept calling a refusing Deezer {len(deezer_calls)} times; "
        "the breaker should have stopped it after 2"
    )
```

- [ ] **Step 2: Run them and confirm they fail**

```bash
cd api && uv run --extra dev pytest -q -k "breaker or open_breaker"
```

Expected: all FAIL with `ModuleNotFoundError: artistpath_api.breaker`.

- [ ] **Step 3: Write the breaker**

Create `api/src/artistpath_api/breaker.py`:

```python
"""A per-source circuit breaker for the clip catalogues (G3-A4 / G3-S2).

Per-process and unsynchronised across instances. That is adequate at
`max_size=2` and is deliberate: a breaker shared through DynamoDB would be a
write on every clip request, which is the load this exists to avoid. With two
instances the worst case is twice the configured rate, which is still bounded
and still far below the fan-out it replaces.

Time is injected so the cooldown is testable without sleeping.
"""

from __future__ import annotations

import time
from collections.abc import Callable


class CatalogueBreaker:
    def __init__(
        self,
        threshold: int,
        cooldown_s: float,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._threshold = threshold
        self._cooldown_s = cooldown_s
        self._now = now
        self._failures: dict[str, int] = {}
        self._opened_at: dict[str, float] = {}

    def is_open(self, source: str) -> bool:
        """Is this source in its cooldown, and therefore not to be called?"""
        opened = self._opened_at.get(source)
        if opened is None:
            return False
        if self._now() - opened >= self._cooldown_s:
            # ⚠ CORRECTED DURING EXECUTION 2026-07-28. This block originally
            # also did `self._failures.pop(source, None)`, with a comment
            # claiming a full reset *was* the half-open behaviour. It is not:
            # resetting the count admits a further `threshold` requests every
            # cooldown, so a permanently dead catalogue costs five calls a
            # minute rather than one. Leaving the count at the threshold makes
            # the next real request the probe, and a single failure re-opens.
            # Caught by test_the_request_after_a_cooldown_is_the_probe_and_a_
            # failure_reopens, which was written before the implementation.
            self._opened_at.pop(source, None)
            return False
        return True

    def record_failure(self, source: str) -> None:
        count = self._failures.get(source, 0) + 1
        self._failures[source] = count
        if count >= self._threshold:
            self._opened_at[source] = self._now()

    def record_success(self, source: str) -> None:
        """Clear the count. Without this, scattered failures over hours trip
        the breaker on a service that is working."""
        self._failures.pop(source, None)
        self._opened_at.pop(source, None)
```

- [ ] **Step 4: Add the tunables to `config.py`**

In `ApiConfig`, in the `--- clips ---` block after `clip_search_limit`:

```python
    # --- clip circuit breaker (G3-A4 / G3-S2) ---------------------------
    # Consecutive unavailable responses from ONE catalogue before we stop
    # calling it. 5 rather than 1 or 2: a single transient error must not
    # silence every card for a minute, which would be worse than the defect.
    clip_breaker_threshold: int = 5
    # How long to leave it alone. 60 s is a judgement, not a measurement —
    # neither catalogue documents its window. The next request after the
    # cooldown is the probe; if it fails the breaker re-opens immediately.
    clip_breaker_cooldown_s: float = 60.0
```

- [ ] **Step 5: Wire it into `ClipResolver`**

In `clips.py`, change the constructor and add the guards:

```python
    def __init__(
        self,
        cfg: ApiConfig,
        cache: ClipCache,
        fetch_json: FetchJson,
        breaker: CatalogueBreaker | None = None,
    ) -> None:
        self._cfg = cfg
        self._cache = cache
        self._fetch = fetch_json
        # Optional so every existing call site keeps working. Constructed from
        # cfg when absent, so production gets one without app.py having to
        # know it exists.
        self._breaker = breaker or CatalogueBreaker(
            threshold=cfg.clip_breaker_threshold,
            cooldown_s=cfg.clip_breaker_cooldown_s,
        )
```

Add `from artistpath_api.breaker import CatalogueBreaker` to the imports.

Then give `_get` a source-aware wrapper. Add this method and use it from `_preview_url`,
`_from_deezer`, and `_from_itunes` in place of `_get`:

```python
    async def _get_from(self, source: str, url: str, params: dict) -> dict:
        """`_get`, but skipping a source that is in its cooldown.

        Raises CatalogueUnavailable without calling out when the breaker is
        open, so every caller's existing handling of that exception applies
        unchanged — the breaker adds no new control flow anywhere else.
        """
        if self._breaker.is_open(source):
            raise CatalogueUnavailable(f"{source} breaker open")
        try:
            body = await self._get(url, params)
        except CatalogueUnavailable:
            self._breaker.record_failure(source)
            raise
        self._breaker.record_success(source)
        return body
```

In `_preview_url`, use `self._get_from("deezer", ...)` on the Deezer branch and
`self._get_from("itunes", ...)` on the iTunes branch. In `_from_deezer` use
`self._get_from("deezer", ...)`; in `_from_itunes` use `self._get_from("itunes", ...)`.

Add the import to `api/tests/test_clips.py`:
`from artistpath_api.breaker import CatalogueBreaker`.

- [ ] **Step 6: Run the tests**

```bash
cd api && uv run --extra dev pytest -q
```

Expected: all six new tests PASS; full suite green.

- [ ] **Step 7: Commit and open the PR**

```bash
git add api/src/artistpath_api/breaker.py api/src/artistpath_api/config.py \
        api/src/artistpath_api/clips.py api/tests/test_breaker.py api/tests/test_clips.py
git commit -m "PW-4: circuit-break a refusing clip catalogue (G3-A4, G3-S2)"
git push -u origin HEAD
```

---

> # ⛔ HANDOFF SEAM — retire the session here
>
> Track A is complete, committed, and independently valuable. Everything above improves the app
> whether or not the password ever comes off, and nothing above touches AWS or Cloudflare.
>
> **Before handing off:** append the per-task decisions to the retained execution log, open the
> draft PR if it is not open, and confirm all four suites are green (`api`, `builder`, `infra`,
> `frontend`).
>
> **The next session starts cold at PW-5** and needs: the owner's AWS credentials, his Cloudflare
> dashboard, and `infra/.env.deploy`.

---

# Track B — the front door

## Task PW-5: Certificate and custom domain on CloudFront

Closes **G3-A5** (*the site is welded to an address AWS generated, which can never be moved to
different infrastructure*) as a side effect of the front-door move. The owner has confirmed the
subdomain is permanent, which is what converts this from "deferring the hostname decision" into
"the hostname decision is made."

**Additive and reversible.** The existing `*.cloudfront.net` address keeps working throughout,
the password stays on, and nothing about routing, the graph or clips changes.

**The certificate is created out of band and its ARN passed in.** CDK could request one, but
validation would block the deploy on a DNS record only the owner can add, and `synth` must stay
offline — the whole infra suite runs with no credentials (see `deploy_stage.py`'s docstring).

**Files:**
- Modify: `infra/src/artistpath_infra/stack.py` (`DeployInputs`, the `Distribution`)
- Modify: `infra/app.py`
- Modify: `infra/tests/test_stack.py`
- Modify: `infra/README.md` (new section between §1 and §2)

**Interfaces:**
- Consumes: nothing from Track A.
- Produces: `DeployInputs.site_hostname: str` and `DeployInputs.certificate_arn: str`. PW-7
  consumes `site_hostname`.

- [ ] **Step 1: Owner action — request the certificate**

In **us-east-1** (CloudFront accepts certificates from no other region):

```bash
aws acm request-certificate --region us-east-1 \
  --domain-name "$ARTISTPATH_SITE_HOSTNAME" \
  --validation-method DNS \
  --query CertificateArn --output text
```

Then read the validation record and add it at Cloudflare:

```bash
aws acm describe-certificate --region us-east-1 --certificate-arn "$ARN" \
  --query "Certificate.DomainValidationOptions[].ResourceRecord"
```

> **The validation CNAME must be set to DNS-only (grey cloud) at Cloudflare.** A proxied record
> answers with Cloudflare's own address and ACM never validates. This is the single most common
> way this step stalls.

Wait for `Status: ISSUED`:

```bash
aws acm describe-certificate --region us-east-1 --certificate-arn "$ARN" \
  --query "Certificate.Status" --output text
```

- [ ] **Step 2: Write the failing tests**

Append to `infra/tests/test_stack.py`:

```python
def test_the_distribution_serves_the_custom_hostname():
    # G3-A5: without an alternate domain name CloudFront 403s any request whose
    # Host is not its own generated address, so Cloudflare cannot be put in
    # front at all. Asserted against an OVERRIDDEN value, not DEPLOY's, so an
    # assertion that happens to match the fixture cannot pass vacuously.
    t = template(site_hostname="probe.example.org")
    t.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {"DistributionConfig": {"Aliases": ["probe.example.org"]}},
    )


def test_the_distribution_uses_the_supplied_certificate():
    t = template(certificate_arn="arn:aws:acm:us-east-1:111111111111:certificate/probe")
    t.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {
            "DistributionConfig": {
                "ViewerCertificate": {
                    "AcmCertificateArn": (
                        "arn:aws:acm:us-east-1:111111111111:certificate/probe"
                    )
                }
            }
        },
    )
```

- [ ] **Step 3: Run them and confirm they fail**

```bash
cd infra && uv run --extra dev pytest -q -k "custom_hostname or supplied_certificate"
```

Expected: FAIL — `TypeError` on the unexpected `DeployInputs` keyword.

- [ ] **Step 4: Add the fields and wire the distribution**

In `stack.py`, add to `DeployInputs` after `image_tag`:

```python
    # The permanent public name. G3-A5: until 2026-07-28 the site was welded to
    # CloudFront's generated domain, which cannot be recreated, moved between
    # accounts, or migrated off CloudFront — so every link ever shared was
    # pinned to infrastructure rather than to a name we control.
    site_hostname: str = ""
    # us-east-1 ACM certificate for site_hostname. Requested out of band and
    # passed in: CDK could request it, but DNS validation would block synth on
    # a record only the operator can add, and synth must stay offline.
    certificate_arn: str = ""
```

Add the import at the top of `stack.py`:

```python
from aws_cdk import aws_certificatemanager as acm
```

In the `cloudfront.Distribution(...)` call, add after `default_root_object="index.html",`:

```python
            # Empty means "generated domain only", which is what the storage
            # stage and every test that does not care about the hostname get.
            domain_names=[deploy.site_hostname] if deploy.site_hostname else None,
            certificate=(
                acm.Certificate.from_certificate_arn(
                    self, "SiteCertificate", deploy.certificate_arn
                )
                if deploy.certificate_arn
                else None
            ),
```

In `infra/app.py`, add to the `DeployInputs(...)` call:

```python
        site_hostname=_require("ARTISTPATH_SITE_HOSTNAME"),
        certificate_arn=_require("ARTISTPATH_CERTIFICATE_ARN"),
```

In `infra/tests/test_stack.py`, add both fields to the `DEPLOY` fixture with placeholder values
(`site_hostname="artistpath.test.invalid"`,
`certificate_arn="arn:aws:acm:us-east-1:000000000000:certificate/test"`).

- [ ] **Step 5: Run the suite**

```bash
cd infra && uv run --extra dev pytest -q
```

Expected: both new tests PASS; all 58 existing tests stay green.

- [ ] **Step 6: Owner action — set the variables and deploy**

Add to `infra/.env.deploy`:

```
ARTISTPATH_SITE_HOSTNAME=<the subdomain>
ARTISTPATH_CERTIFICATE_ARN=<the ARN from step 1>
```

Then, per `infra/README.md` §5:

```bash
cd infra && UV_LINK_MODE=copy uv run cdk diff     # read it before deploying
cd infra && UV_LINK_MODE=copy uv run cdk deploy
```

**Read the diff before accepting it.** Expect exactly two changes to the distribution: `Aliases`
and `ViewerCertificate`. **Anything else — especially a distribution replacement — is a stop.**
A replaced distribution gets a new generated domain and every existing link dies permanently
(`ARC-1`, and it is why `deploy_stage.py` exists).

- [ ] **Step 7: Gate — the old address still works**

```bash
curl -s -o /dev/null -w '%{http_code}\n' -u "artistpath:$PASSWORD" \
  https://d2n3xqz3pttguf.cloudfront.net/
```

**Pass condition: `200`.** Any other code means the deploy disturbed the live site and must be
rolled back per `infra/README.md` §9 before continuing. This is binary — there is no
"mostly working" reading of it.

- [ ] **Step 8: Commit**

```bash
git add infra/src/artistpath_infra/stack.py infra/app.py infra/tests/test_stack.py
git commit -m "PW-5: custom domain and certificate on the distribution (G3-A5)"
```

---

## Task PW-6: Put Cloudflare in front — with the password still on

Closes **G3-A2** (*nothing anywhere limits how many requests one person can send*). This is the
task that replaces the AWS WAF the review assumed, at no cost.

**The password stays on throughout this task.** That is the safety property: if any part of the
Cloudflare configuration is wrong, the existing gate is still protecting the site while it is
found. Nothing here is code; the deliverable is configuration plus a runbook section that makes
it reproducible.

**Files:**
- Modify: `infra/README.md` — new section **§1a. The Cloudflare front door**, placed after §1.

**Interfaces:**
- Consumes: `site_hostname` from PW-5, live.
- Produces: a Cloudflare Transform Rule injecting a secret header, consumed by PW-7.

- [ ] **Step 1: Confirm the free-tier allowance before designing around it**

In the Cloudflare dashboard, check **Security → WAF → Rate limiting rules**: how many rules the
plan permits, and which periods and actions are selectable.

> **Do not proceed on the assumption of one rule.** Cloudflare changes plan features, and the
> rest of this task is sized for a single IP-keyed rule. If the allowance differs, record what it
> actually is in §1a and adjust step 4 rather than carrying a stale number forward.

- [ ] **Step 2: DNS and TLS**

- **DNS → Records:** `CNAME` for the subdomain → `d2n3xqz3pttguf.cloudfront.net`, **Proxied
  (orange cloud)**.
- **SSL/TLS → Overview:** **Full (strict)**. Anything less lets Cloudflare accept an invalid
  origin certificate, which defeats the point of PW-5.

- [ ] **Step 3: Inject the front-door secret**

Generate a secret and keep it with the other deploy secrets:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add it to `infra/.env.deploy` as `ARTISTPATH_FRONT_DOOR_SECRET=…` — **PW-7 needs the same value**
— and confirm `.env.deploy` is still gitignored and untracked:

```bash
git check-ignore -v infra/.env.deploy && git ls-files --error-unmatch infra/.env.deploy
```

Expected: the first prints a rule, the second fails with "did not match any file". That
combination is the check; either one alone is not.

**Rules → Transform Rules → Modify Request Header:** add a static header
`x-front-door: <the secret>` on all incoming requests.

Nothing checks this header yet. That is deliberate — it goes live one task before it is enforced,
so enforcement never depends on a change made in the same step.

- [ ] **Step 4: The rate limiting rule**

**Security → WAF → Rate limiting rules.** One rule:

- **Match:** `URI Path equals /api/path`
- **Counting:** by IP address
- **Period:** 60 seconds
- **Requests:** **30**
- **Action:** Block, for 60 seconds

**Why `/api/path` alone and not `/api/*`.** From the traced request pattern: loading a journey
from scratch is roughly 27 requests — per-keystroke search on two artist boxes, one path, and one
clip lookup per card (`ArtistCard.tsx:26` → `useClip` fires on mount, not on tap). A rule over
`/api/*` would spend its whole budget on cheap keystroke traffic and throttle *typing* while
leaving pathfinding — the ~1.9 s-per-request endpoint that is the actual capacity ceiling —
unprotected.

**Why 30.** A user pressing bypass every 5 seconds issues 12 path requests a minute. 30 is
generous for one person and caps a single IP at 0.5 req/s against a server ceiling of roughly
1.5. The upper end of the sensible range rather than the lower, because friends behind one office
NAT or the same mobile carrier share an IP.

- [ ] **Step 5: Verify Cloudflare is not caching HTML**

**Caching → Cache Rules**, and **Rules → Page Rules**. Confirm **no rule caches HTML or sets
"Cache Everything"** for this hostname.

> **This is not a formality.** Cloudflare's default is safe — it caches static extensions and
> not HTML — but a "Cache Everything" rule inherited from another project on this account would
> silently reintroduce **FRO-1**: returning visitors served a stale `index.html` referencing
> deleted asset hashes, i.e. a blank page after every deploy. It bites only people who visited
> *before* a deploy, which is exactly why it went undetected the first time. A CloudFront
> invalidation does not purge Cloudflare.

Record the finding in §1a either way — "verified no HTML caching on <date>" is the artifact.

- [ ] **Step 6: Gate — the site works through the new hostname, with the password**

```bash
# 1. The new hostname serves the app, and still demands the password.
curl -s -o /dev/null -w '%{http_code}\n' https://$ARTISTPATH_SITE_HOSTNAME/
# expect 401

curl -s -o /dev/null -w '%{http_code}\n' -u "artistpath:$PASSWORD" \
  https://$ARTISTPATH_SITE_HOSTNAME/
# expect 200

# 2. A shared journey link resolves through the SPA fallback.
curl -s -o /dev/null -w '%{http_code}\n' -u "artistpath:$PASSWORD" \
  "https://$ARTISTPATH_SITE_HOSTNAME/path/$MBID_A/$MBID_B"
# expect 200

# 3. The API answers through the new hostname.
curl -s -o /dev/null -w '%{http_code}\n' -u "artistpath:$PASSWORD" \
  "https://$ARTISTPATH_SITE_HOSTNAME/api/artists/search?q=radiohead"
# expect 200

# 4. The secret header is arriving at the origin. Nothing enforces it yet, so
#    this is the only chance to catch a Transform Rule that is not firing
#    BEFORE PW-7 makes the site depend on it.
curl -s -u "artistpath:$PASSWORD" "https://$ARTISTPATH_SITE_HOSTNAME/api/artists/search?q=a" \
  -o /dev/null -w '%{http_code}\n'
```

For check 4, confirm the header is actually present by reading the App Runner application log for
that request, or temporarily add `x-front-door` to the allow-list in `ApiOriginRequestPolicy`
(`stack.py:313-317`) and echo it. **Do not skip this check.** PW-7 makes the site unreachable if
the header is not arriving, and discovering that after the password is gone is the bad ordering.

**Pass condition: all four exactly as annotated.** Any deviation stops the task.

- [ ] **Step 7: Gate — the rate limit fires, and only on abuse**

Two measurements, and **both** must hold:

```bash
# Abuse: 60 path requests in under 60 s from one IP must be blocked.
for i in $(seq 1 60); do
  curl -s -o /dev/null -w '%{http_code} ' -u "artistpath:$PASSWORD" \
    -X POST "https://$ARTISTPATH_SITE_HOSTNAME/api/path" \
    -H 'content-type: application/json' \
    -d "{\"sources\":[\"$MBID_A\",\"$MBID_B\"],\"exclude\":[]}"
done; echo
```

**Pass condition: at least one `429` appears, and it appears at or before the 40th request.**
A run of 60 × `200` means the rule is not matching — most likely the path pattern.

Then, by hand in a browser: **build a journey and press bypass 20 times over about two minutes.**

**Pass condition: zero blocks.** A single 429 during ordinary use means 30 is too tight; raise it
and re-run both halves. Do not raise it above 60 without re-deriving the arithmetic in step 4 —
above that a single IP can saturate the server on its own and the rule stops being a limit.

- [ ] **Step 8: Write §1a and commit**

Add **§1a. The Cloudflare front door** to `infra/README.md` covering: the DNS record and its
proxy state, the SSL mode, the Transform Rule and which variable holds its secret, the rate
limiting rule with the arithmetic behind 30, the HTML-caching verification and its date, and the
gate commands from steps 6 and 7 as the re-verification procedure.

Note explicitly in §1a: **the ACM validation CNAME must stay DNS-only**, and **a CloudFront
invalidation does not purge Cloudflare** — if HTML caching is ever enabled, the deploy in §6 must
gain a purge step.

```bash
git add infra/README.md
git commit -m "PW-6: Cloudflare front door and rate limiting (G3-A2), password still on"
```

---

## Task PW-7: Swap the password for the front-door check

Closes **G3-S7** (*the password and the shared-link routing are the same piece of code, so
removing one breaks the other*). **This is the task that removes the password.**

The gate is not deleted — it is **replaced**. The viewer function goes on refusing, but it now
asks "did this arrive through Cloudflare?" instead of "does this carry the shared password?".
That keeps the test coverage rather than deleting it, and it closes the bypass that would
otherwise make PW-6 decorative: `d2n3xqz3pttguf.cloudfront.net` answers on its own, that address
is already circulating in shared links and browser histories, and a request to it never touches
Cloudflare's rate limit.

**This project has already made this exact mistake once.** `stack.py:147-153` records `TR-7`:
App Runner published its own public URL, so the CloudFront gate protected the front door while
the origin answered around it. Doing it again one layer up is the same defect at a different
altitude.

**Files:**
- Modify: `infra/src/artistpath_infra/viewer_function.js`
- Modify: `infra/src/artistpath_infra/stack.py`
- Modify: `infra/app.py`
- Modify: `infra/tests/test_stack.py`, `infra/tests/test_viewer_function.py`

**Interfaces:**
- Consumes: `DeployInputs.site_hostname` (PW-5), the `x-front-door` header (PW-6).
- Produces: `DeployInputs.front_door_secret`, replacing `site_password`. `SITE_USERNAME` and
  `REFUSAL_BODY` are removed.

- [ ] **Step 1: Write the failing tests**

Replace the `--- the gate ---` and `--- the refusal has to be usable by a person ---` sections of
`infra/tests/test_viewer_function.py` with the block below. **Keep the `--- the SPA fallback
(TR-5) ---` section exactly as it is** — those three tests are the reason this is a swap and not
a deletion — but drop the `VALID_AUTH` argument from their `_request(...)` calls and pass
`secret=SECRET` instead.

Also update the fixture's placeholder assertions: `__EXPECTED_AUTH__` and `__EXPECTED_USERNAME__`
no longer exist; assert `__FRONT_DOOR_SECRET__` and `__SITE_HOSTNAME__` are absent instead.

```python
# The Cloudflare-injected value from test_stack.py's DEPLOY fixture. Hardcoded
# rather than recomputed from DeployInputs, for the reason in the module
# docstring: a value derived the way stack.py derives it moves in lockstep with
# a mutation to stack.py and the test stays green.
SECRET = "test-front-door-secret"
HOSTNAME = "artistpath.test.invalid"


def _request(uri: str, secret: str | None = None, host: str | None = None,
             querystring: dict | None = None) -> dict:
    headers = {}
    if secret is not None:
        headers["x-front-door"] = {"value": secret}
    headers["host"] = {"value": host or HOSTNAME}
    return {"uri": uri, "headers": headers, "querystring": querystring or {}}


# --- the gate ---------------------------------------------------------------


def test_a_request_that_did_not_come_through_cloudflare_is_refused():
    # The bypass this task exists to close: the generated CloudFront address
    # answers on its own and never touches Cloudflare's rate limit, and that
    # address is already in circulation.
    result = run_handler(_request("/", secret=None))
    assert "statusCode" in result and result["statusCode"] in (301, 403)


def test_a_request_with_the_wrong_secret_is_refused():
    result = run_handler(_request("/", secret="wrong"))
    assert "statusCode" in result and result["statusCode"] in (301, 403)


def test_a_request_through_cloudflare_is_admitted():
    # The half an "does it refuse?" test cannot see. Without this, a function
    # that refuses everyone passes, and so does one that admits everyone.
    result = run_handler(_request("/", secret=SECRET))
    assert "statusCode" not in result, result
    assert result["uri"] == "/index.html"


def test_the_old_cloudfront_address_redirects_rather_than_refusing():
    # Every link shared before this change points at the generated address.
    # A 403 would break all of them; a redirect pulls them through Cloudflare
    # instead, which is also what puts them under the rate limit.
    result = run_handler(
        _request("/path/abc/def", secret=None, host="d2n3xqz3pttguf.cloudfront.net")
    )
    assert result["statusCode"] == 301
    assert result["headers"]["location"]["value"] == (
        "https://" + HOSTNAME + "/path/abc/def"
    )


def test_the_redirect_preserves_the_query_string():
    # Bypass state lives in the query string (/path/:from/:to?dislike=…&known=…),
    # so dropping it silently changes the journey the recipient sees — G3-F3's
    # shape, arriving by a different route.
    result = run_handler(
        _request(
            "/path/abc/def",
            secret=None,
            host="d2n3xqz3pttguf.cloudfront.net",
            querystring={"dislike": {"value": "xyz"}, "known": {"value": "pqr"}},
        )
    )
    location = result["headers"]["location"]["value"]
    assert "dislike=xyz" in location and "known=pqr" in location


def test_arriving_at_the_right_host_without_the_secret_does_not_loop():
    # If the Transform Rule is ever removed, redirecting to the host we are
    # already on is an infinite redirect. Fail closed instead — a broken site
    # is recoverable, a redirect loop looks like a broken site AND hides why.
    result = run_handler(_request("/", secret=None, host=HOSTNAME))
    assert result["statusCode"] == 403


def test_the_refusal_does_not_disclose_the_secret():
    # Same class as the password disclosure this replaces: the cheapest way to
    # write a helpful refusal is to name the thing that was missing.
    response = json.dumps(run_handler(_request("/", secret=None, host=HOSTNAME)))
    assert SECRET not in response
```

- [ ] **Step 2: Run them and confirm they fail**

```bash
cd infra && uv run --extra dev pytest -q tests/test_viewer_function.py
```

Expected: the new gate tests FAIL; the three SPA-fallback tests also fail (they now pass
`secret=` to a function that still wants `authorization`). That is correct — they are being
carried across, not rewritten.

- [ ] **Step 3: Rewrite the viewer function**

Replace `infra/src/artistpath_infra/viewer_function.js` in full:

```js
// Two jobs on one viewer-request function.
//
// 1. The front-door check (PW-7, replacing DEP-4's shared password). This is
//    not authentication and never was: it is a shared secret in a function
//    body. Its purpose is narrower than the password's and more precise —
//    ensure every request has passed through Cloudflare, where the rate limit
//    lives. Without it the generated CloudFront address answers directly and
//    the rate limit is decorative, which is TR-7's defect one layer up: a
//    control on the front door while the origin answers on its own name.
//
//    A request WITHOUT the secret is redirected to the real hostname rather
//    than refused, because the overwhelmingly likely cause is a link shared
//    before this change. A 403 would break every one of them. The exception is
//    a request that already carries the right Host — there, a redirect is an
//    infinite loop, so it fails closed.
//
// 2. The SPA fallback (TR-5). Without it every shared journey link 403s: the
//    default behaviour serves a private S3 bucket, which holds no object at
//    /path/<mbid>/<mbid>. It lives here rather than in the distribution's
//    errorResponses because those are distribution-level and would rewrite
//    the API's own 404s and the origin-secret 403 into an HTML page with
//    status 200 (TKB-2).
//
// __FRONT_DOOR_SECRET__ and __SITE_HOSTNAME__ are substituted at synth time
// from DeployInputs. The secret is never in git.

var REFUSAL_BODY =
  '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<title>artistpath</title></head>' +
  '<body style="font-family:system-ui,sans-serif;max-width:32rem;' +
  'margin:4rem auto;padding:0 1rem;line-height:1.5">' +
  '<h1>artistpath</h1>' +
  '<p>This request did not arrive through the front door, so it was refused.</p>' +
  '<p>If you followed a link and reached this page, please report it.</p>' +
  '</body></html>';

// CloudFront Functions give the query string as an object and provide no
// serialiser. Bypass state lives in it (/path/:from/:to?dislike=…&known=…), so
// a redirect that drops it silently changes the journey the recipient sees.
function queryString(qs) {
  var parts = [];
  for (var key in qs) {
    var v = qs[key];
    if (v.multiValue) {
      for (var i = 0; i < v.multiValue.length; i++) {
        parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(v.multiValue[i].value));
      }
    } else {
      parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(v.value));
    }
  }
  return parts.length ? '?' + parts.join('&') : '';
}

function handler(event) {
  var request = event.request;
  var headers = request.headers;

  var supplied = headers['x-front-door'] && headers['x-front-door'].value;
  if (supplied !== '__FRONT_DOOR_SECRET__') {
    var host = headers.host && headers.host.value;
    if (host === '__SITE_HOSTNAME__') {
      // Already on the right name and still no secret: Cloudflare has been
      // bypassed, or the Transform Rule is gone. Redirecting here would loop.
      return {
        statusCode: 403,
        statusDescription: 'Forbidden',
        headers: { 'content-type': { value: 'text/html; charset=utf-8' } },
        body: { encoding: 'text', data: REFUSAL_BODY },
      };
    }
    return {
      statusCode: 301,
      statusDescription: 'Moved Permanently',
      headers: {
        location: {
          value: 'https://__SITE_HOSTNAME__' + request.uri + queryString(request.querystring),
        },
      },
    };
  }

  // Anything that is not an API call and has no file extension is an SPA
  // route: /path/<mbid>/<mbid> holds no S3 object.
  //
  // /health needs no case here. Only /api/* is routed to App Runner, so
  // /health is not reachable through CloudFront at all — it is reached at the
  // App Runner origin URL, which is where App Runner's own health checker
  // reaches it and where design §9's identity check is run.
  var uri = request.uri;
  if (uri.indexOf('/api/') !== 0 && uri.lastIndexOf('.') <= uri.lastIndexOf('/')) {
    request.uri = '/index.html';
  }
  return request;
}
```

- [ ] **Step 4: Update the stack**

In `stack.py`: delete the `SITE_USERNAME` constant, replace `site_password: str` in
`DeployInputs` with `front_door_secret: str`, and replace the substitution block:

```python
        function_code = (
            (Path(__file__).parent / "viewer_function.js")
            .read_text()
            .replace("__FRONT_DOOR_SECRET__", deploy.front_door_secret)
            .replace("__SITE_HOSTNAME__", deploy.site_hostname)
        )
```

Delete the `base64` import and the `expected_auth` computation — both become unused.

In `infra/app.py`, replace the `site_password` line:

```python
        front_door_secret=_require("ARTISTPATH_FRONT_DOOR_SECRET"),
```

In `infra/tests/test_stack.py`, replace `site_password="test-password"` with
`front_door_secret="test-front-door-secret"` and set
`site_hostname="artistpath.test.invalid"` in `DEPLOY` so it matches `HOSTNAME` in the viewer
tests.

Then grep for stragglers and fix every hit:

```bash
grep -rn "site_password\|SITE_USERNAME\|ARTISTPATH_DEPLOY_PASSWORD\|EXPECTED_AUTH" \
  infra/ api/ docs/superpowers/plans/ --include="*.py" --include="*.js" --include="*.md"
```

> **`CLAUDE.md`'s rename rule applies here and it is not the grep.** *"A rename's blast radius
> includes every document that describes the quantity, not only those that use the name"* — the
> check is whether every place that should describe the front door still describes it correctly,
> **including by omission**. `infra/README.md` §8a is named "Prove the gate ADMITS"; it describes
> a password that no longer exists. That is PW-8's business, and a grep for `site_password` will
> not find it.

- [ ] **Step 5: Run the suites**

```bash
cd infra && uv run --extra dev pytest -q
```

Expected: all viewer-function tests PASS, all 58+ stack tests green.

- [ ] **Step 6: Owner action — deploy**

```bash
cd infra && UV_LINK_MODE=copy uv run cdk diff    # expect ONLY the function body to change
cd infra && UV_LINK_MODE=copy uv run cdk deploy
```

- [ ] **Step 7: Gate — the password is gone and nothing else is**

```bash
# 1. No password, and the app loads.
curl -s -o /dev/null -w '%{http_code}\n' https://$ARTISTPATH_SITE_HOSTNAME/
# expect 200

# 2. A shared journey link, no password.
curl -s -o /dev/null -w '%{http_code}\n' \
  "https://$ARTISTPATH_SITE_HOSTNAME/path/$MBID_A/$MBID_B"
# expect 200

# 3. The old address redirects and keeps the query string.
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' \
  "https://d2n3xqz3pttguf.cloudfront.net/path/$MBID_A/$MBID_B?known=$MBID_C"
# expect: 301 https://<hostname>/path/<A>/<B>?known=<C>

# 4. Following that redirect lands on the journey.
curl -sL -o /dev/null -w '%{http_code}\n' \
  "https://d2n3xqz3pttguf.cloudfront.net/path/$MBID_A/$MBID_B"
# expect 200

# 5. The rate limit still fires — the same loop as PW-6 step 7, now with no -u.
```

**Pass conditions: all five exactly as annotated, and gate 5 must still block at or before the
40th request.** If gate 5 no longer fires, **roll back immediately** (`infra/README.md` §9): the
password is gone and the thing replacing it is not working, which is the one state this ordering
exists to prevent.

- [ ] **Step 8: Commit**

```bash
git add infra/src/artistpath_infra/viewer_function.js infra/src/artistpath_infra/stack.py \
        infra/app.py infra/tests/test_stack.py infra/tests/test_viewer_function.py
git commit -m "PW-7: replace the shared password with a Cloudflare front-door check (G3-S7)"
```

---

## Task PW-8: Runbook, log retention, and the record

The half `CLAUDE.md` warns a grep cannot find: documents that **describe** the password still
describe it correctly only if someone reads them.

**Files:**
- Modify: `infra/README.md` (§0, §5a, §7, §8, §8a)
- Modify: `docs/superpowers/NEXT.md`
- Modify: `docs/superpowers/TEST-QUEUE.md`
- Create: `docs/superpowers/2026-07-28-password-removal-execution-log.md` (if not already started
  at PW-1 — it should have been)

- [ ] **Step 1: Verify log retention is actually set**

The review's G3-A3 says "no log retention set anywhere". That is true of the code, but
`infra/README.md` §5a is a required manual step setting 90 days. **Whether it was run against the
live service is unknown — measure it:**

```bash
MSYS_NO_PATHCONV=1 aws logs describe-log-groups \
  --log-group-name-prefix "/aws/apprunner/artistpath-api" \
  --query "logGroups[].{Name:logGroupName,Retention:retentionInDays}"
```

**Pass condition: every group shows `90`.** A `null` means Never Expire and §5a was never run —
run it now, from §5a, verbatim. `MSYS_NO_PATHCONV=1` is required: Git Bash rewrites
`/aws/apprunner/...` into a Windows path and the API rejects it with a regex error that names the
parameter but not the cause.

- [ ] **Step 2: Correct every section of `infra/README.md` that describes the password**

- **§0 Prerequisites** — add the Cloudflare account and the ACM certificate.
- **§5a** — unchanged, but note it was verified on this date and by whom.
- **§7 The manual gates** — the drift check. The distribution now has `Aliases` and
  `ViewerCertificate`; confirm the expected-row count is still correct or update it. It expects
  three rows as of 2026-07-27.
- **§8 Verify the deploy** — every `-u artistpath:$PASSWORD` becomes an unauthenticated request.
- **§8a "Prove the gate ADMITS"** — **rename and rewrite.** It exists because until 2026-07-27
  every check proved only that the site *refuses*. The gate it names is gone; the equivalent
  check now is *"prove the front door admits and the old address redirects"* — PW-7's step 7.
  **Do not delete this section.** The property it protects is the reason it was written.

- [ ] **Step 3: Rewrite `NEXT.md`**

`NEXT.md` is rewritten wholesale, never appended to. It must now say: the password is off, what
the front door is, that Gate 3 is **not** open and the review's blocking set still gates it, and
that `max_size=2` is deliberate and must not be raised. **Carry the migration's Task 9 / Task 10
/ Task 11 state forward unchanged** — this work does not touch it.

- [ ] **Step 4: Queue the use-the-app test**

Append a `QUEUED` entry to `docs/superpowers/TEST-QUEUE.md`, newest first, in the file's
established plain-language register — what changed, what to press, what "wrong" looks like.

It must carry: the new address, **no password**, that journeys must be unchanged (nothing about
routing, the graph, or the cost function moved), that old links still work via redirect, and
**the iPhone script from the review's §6** — the owner deferred it to a friend after this work,
and this queue entry is where it lands. Name it as its own numbered section so it cannot be read
as optional.

- [ ] **Step 5: Commit and mark the PR ready**

```bash
git add infra/README.md docs/superpowers/
git commit -m "PW-8: runbook, retention verification, and the record"
git push
```

---

## Task PW-9: Acceptance — the concurrency ladder against the live origin

The review's §7 left one half unmeasured: the ladder was **blocked by the tool-permission
classifier**, correctly, because generating concurrent load against a live site pattern-matches a
denial-of-service and the classifier cannot see the authorization.

**This task needs the owner's explicit approval to run, and he may prefer to run it himself.**
The review's §4 says the calibration already resolved the pivot, so this is **confirmation, not a
decision input** — if it cannot be run, the work still stands and this becomes a deferral with
the condition below.

- [ ] **Step 1: Get explicit approval, in writing, in the execution log**

- [ ] **Step 2: Run the ladder**

Reconstructed from the review's §1 table and §7 (the original script lived in an ephemeral
scratchpad and is gone): a thread pool at concurrency 1 → 5 → 20 → 40 issuing `POST /api/path`
with obscure-artist MBID pairs extracted from the adopted artifact, measuring throughput and
p50/p95, plus an `/api/artists/search` probe during the 40-wide burst. **~148 path requests
total, a bounded 2–3 minute burst, not a sustained flood.** Write it to the scratchpad; it is
instrumentation, not a deliverable.

**Run it against the App Runner origin URL directly, not through Cloudflare** — otherwise the
rate limit blocks it and the measurement is of Cloudflare, not of the server. The origin secret
is needed; take it from `.env.deploy`.

- [ ] **Step 3: Read the result against a pre-stated threshold**

Fixed **before** the run, so it cannot be reshaped to fit one:

| Reading | Threshold | What it means |
|---|---|---|
| `/health` latency at 40 concurrent | **< 5 s** | PW-2 worked: App Runner's health check cannot miss, so the restart cascade cannot start. This is the primary outcome. |
| `/health` latency at 40 concurrent | **≥ 5 s** | PW-2 did **not** close the cascade. The work still stands — the rate limit means 40 concurrent should not be reachable — but record it as a live deferral, not a pass. |
| Throughput at 40 concurrent | any value | **Recorded, not gated.** The ceiling is a property of one GIL-bound process and this work does not change it. A number here that looks bad is not a failure of this plan. |

- [ ] **Step 4: Record and commit**

Write the result into the execution log and, if `/health` held under 5 s, into `NEXT.md` as the
closing evidence for this work.

---

## Deferred, with conditions

Every item carries a condition, per `closeout`'s deferral rule. An unranked backlog is what this
table exists to not be.

| Deferred | Condition to revisit |
|---|---|
| **G3-A1's capacity half** — the server handles ~1.5 path requests/s and a dozen simultaneous friends can saturate it legitimately. Per-IP rate limiting cannot help; each of them is a different IP behaving reasonably. | **The owner reports multi-second waits with several people using it at once**, or telemetry shows sustained >1 req/s on `/api/path`. The fix is more processes or a cheaper pathfinder, and it is a real piece of work. |
| **Chunked request bodies** bypass the Content-Length check in PW-1 and are bounded only by the schema, after buffering. | **A request with no `content-length` header ever appears in the logs.** CloudFront and Cloudflare both send it, so this is currently unreachable. |
| **G3-S4's disclosure half** — every request records both artists, the whole journey, and every rejection, with no notice anywhere in the app. PW-1 bounds the volume; it does not address what is collected. | **The owner's decision, and removing the password widens who it applies to.** Revisit before Gate 3 at the latest. |
| **G3-F2 / the iPhone script** — the code may mean no clip ever plays on an iPhone, and G3-F1 means a failure says nothing. | **Deferred by the owner on 2026-07-28**, to a friend testing after this ships. Queued in PW-8 step 4. One tap settles it. |
| **G3-Q1 / G3-Q2** — the guards are tested, the wiring that arms them is not. | Unchanged by this work; still gates Gate 3. |
| **PW-9's ladder**, if not run. | **The owner approves a run**, or the app is about to be shared beyond friends and family. |

## What this work does NOT do

Stated because a summary that omits what cuts against it is wrong even when every number in it is
right.

- **It does not open Gate 3.** It does reduce the blocking set, so "no closer to Gate 3" would be
  false — but **Gate 3 is a state, not a score**, and no number of closed findings opens it. The
  itemised tally, so a reader can check the arithmetic rather than take it:

  | Review blocking finding | Plain sentence | Status after this plan |
  |---|---|---|
  | `G3-A2` | nothing limits how many requests one person can send | **closed** — PW-6 |
  | `G3-A4` / `G3-S2` | a throttled catalogue is asked three times, not once | **closed** — PW-3, PW-4 |
  | `G3-S3` | a request can carry an unlimited list | **closed** — PW-1 |
  | `G3-A3` | the knob capping the bill is the knob capping capacity | **does not fire** — load is shed at the edge, `max_size=2` unchanged |
  | `G3-A1` / `G3-S1` | request cost is caller-chosen; the server does one at a time | **half** — PW-2 closes the restart cascade; the ~1.5 req/s capacity half is **deferred** above. `G3-S1` is the same finding measured differently and has no separate task. |
  | `G3-Q1` | the guards are tested, the wiring arming them is not | **untouched** |
  | `G3-Q2` | the publisher can ignore its own upload order | **untouched** |
  | `G3-F1` | a clip failure tells the user nothing | **untouched** |
  | `G3-F2` | clips may never play on an iPhone | **untouched** — deferred to a borrowed device |

  So: six closed, one that does not fire, one half, four untouched. **The four untouched still
  gate Gate 3**, and two of them (`G3-F1`, `G3-F2`) are what a stranger would actually meet.
- **It does not make the app faster.** PW-2 stops slow becoming an outage. Nothing here raises
  the ~1.5 req/s ceiling, and PW-6 deliberately *reduces* what one person can ask for.
- **It does not change anything about which artists you get.** No routing, no graph, no cost
  function, no weight, no threshold. A journey built after this work is the same journey as
  before it — that is the single most valuable thing for the owner to confirm in PW-8's queue
  entry.
