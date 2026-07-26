# F1 Minimum-Stop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every journey returns at least one artist between the two chosen, or says on screen why it cannot.

**Architecture:** The router runs its normal search; if the result is exactly the two chosen artists, it runs again with the direct connection forbidden. Success is the forced stop; failure falls back to the two-card path. The outcome is reported to the frontend as a three-valued `stop_rule`, because a forced stop is indistinguishable from an ordinary path once inserted. No new scoring, no new weight, no rebuild.

**Tech Stack:** Python 3 / FastAPI / numpy (api), React 19 / TypeScript / Vitest (frontend). Design: [`../specs/2026-07-25-f1-minimum-stop-design.md`](../specs/2026-07-25-f1-minimum-stop-design.md).

## Global Constraints

- **`UV_LINK_MODE=copy` on every `uv` command.** OneDrive breaks hardlinks; without it the command fails.
- **Run `uv` from inside the package** (`api/`), never the repo root. Each package has its own `.venv`.
- **Do not touch `ApiConfig`, the cost function weights, or the graph artifact.** Path-quality work is paused by owner decision. This task adds a constraint over the *result*, not a scoring change. If a step seems to need a new weight, stop and report — it means the design was wrong.
- **Do not restate F1's success condition.** It is owned by `../2026-07-25-gate1-clips-and-ux-execution-log.md` §16. Cite that section; never paraphrase it. Two prior deferral conditions drifted in exactly that copying.
- **The three `stop_rule` values are exactly `"natural"`, `"forced"`, `"adjacent_only"`.** Wire format is snake_case (`stop_rule`); the frontend uses camelCase (`stopRule`), matching `preview_url` → `previewUrl`.
- **Branch is `f1-min-stop`, already pushed.** Commit per task. Do not commit to `main`.
- **Endpoints are never skipped.** Existing behaviour: hard exclusions never remove the two chosen artists. Nothing here may change that.

---

### Task 1: The router can forbid one edge

**Files:**
- Modify: `api/src/artistpath_api/pathfinding.py:76-138` (`find_path`)
- Test: `api/tests/test_pathfinding.py`

**Interfaces:**
- Consumes: `make_store(names, pop_raw, undirected_edges)` from `tests/conftest.py`; `ApiConfig` from `artistpath_api.config`.
- Produces: `find_path(store, source, target, excludes, cfg, forbidden_edge=None) -> list[int] | None`, where `forbidden_edge` is `tuple[int, int] | None` and is undirected — `(a, b)` also blocks `(b, a)`. Default `None` preserves today's behaviour exactly.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_pathfinding.py`:

```python
def test_forbidden_edge_routes_around_the_direct_link():
    # 0-1 direct and strong; 0-2-1 available. Forbidding 0-1 must use 2.
    store = make_store(
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    assert find_path(store, 0, 1, [], CFG) == [0, 1]
    assert find_path(store, 0, 1, [], CFG, forbidden_edge=(0, 1)) == [0, 2, 1]


def test_forbidden_edge_is_undirected():
    store = make_store(
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    # Given the other way round, the same edge must still be blocked.
    assert find_path(store, 0, 1, [], CFG, forbidden_edge=(1, 0)) == [0, 2, 1]


def test_forbidding_the_only_link_yields_no_path():
    # B hangs off A by a single edge, as ~6,400 real artists do.
    store = make_store(
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9)],
    )
    assert find_path(store, 0, 1, [], CFG, forbidden_edge=(0, 1)) is None


def test_omitting_forbidden_edge_changes_nothing():
    store = make_store(
        names=list("ABCDE"), pop_raw=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)] + [(0, 2, 0.2)],
    )
    assert find_path(store, 0, 4, [], CFG) == find_path(
        store, 0, 4, [], CFG, forbidden_edge=None
    )
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pathfinding.py -k forbidden
```

Expected: FAIL — `TypeError: find_path() got an unexpected keyword argument 'forbidden_edge'`.

- [ ] **Step 3: Add the parameter**

In `pathfinding.py`, change the `find_path` signature and the neighbour loop. The signature becomes:

```python
def find_path(
    store: GraphStore,
    source: int,
    target: int,
    excludes: list[Exclusion],
    cfg: ApiConfig,
    forbidden_edge: tuple[int, int] | None = None,
) -> list[int] | None:
```

Immediately after the `hard = ...` line, normalise the edge so the check is a cheap
set membership in both directions:

```python
    # Undirected: forbidding (a, b) must also forbid (b, a). Used to force a
    # detour when the least-cost path is the two chosen artists and nothing
    # else (F1). Empty in the ordinary case, so this costs one set lookup.
    banned: set[tuple[int, int]] = set()
    if forbidden_edge is not None:
        a, b = forbidden_edge
        banned = {(a, b), (b, a)}
```

Inside `for v, sim in store.neighbours_of(u):`, directly after the existing
`if v in hard: continue`, add:

```python
            if (u, v) in banned:
                continue
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pathfinding.py
```

Expected: PASS, including every pre-existing test in the file.

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/pathfinding.py api/tests/test_pathfinding.py
git commit -m "Let the router search with one connection forbidden"
```

---

### Task 2: Decide the journey and report which case it was

**Files:**
- Modify: `api/src/artistpath_api/pathfinding.py` (append after `find_path`)
- Test: `api/tests/test_pathfinding.py`

**Interfaces:**
- Consumes: `find_path(..., forbidden_edge=...)` from Task 1.
- Produces:
  - Module constants `STOP_NATURAL = "natural"`, `STOP_FORCED = "forced"`, `STOP_ADJACENT_ONLY = "adjacent_only"`.
  - `find_journey(store, source, target, excludes, cfg) -> tuple[list[int], str] | None` — returns `(path, stop_rule)`, or `None` when `find_path` itself finds nothing (hard exclusions disconnect the endpoints), which the caller still turns into a 409.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_pathfinding.py`. Add `find_journey`, `STOP_NATURAL`, `STOP_FORCED`, `STOP_ADJACENT_ONLY` to the existing import from `artistpath_api.pathfinding`:

```python
def test_journey_with_its_own_stop_is_left_alone():
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    assert find_journey(store, 0, 2, [], CFG) == ([0, 1, 2], STOP_NATURAL)


def test_two_neighbours_get_a_stop_forced_between_them():
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    path, rule = find_journey(store, 0, 1, [], CFG)
    assert rule == STOP_FORCED
    assert path[0] == 0 and path[-1] == 1
    assert len(path) >= 3


def test_two_neighbours_with_nothing_between_them_fall_back():
    # B's only connection is to A, so no stop can exist.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9)],
    )
    assert find_journey(store, 0, 1, [], CFG) == ([0, 1], STOP_ADJACENT_ONLY)


def test_a_stop_is_never_forced_through_a_bypassed_artist():
    # C is the only possible stop, and the user has rejected it.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    excludes = [Exclusion(node=2, reason=DISLIKE)]
    assert find_journey(store, 0, 1, excludes, CFG) == ([0, 1], STOP_ADJACENT_ONLY)


def test_journey_returns_none_when_exclusions_disconnect_the_endpoints():
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 2, 0.9), (2, 1, 0.9)],
    )
    excludes = [Exclusion(node=2, reason=DISLIKE)]
    assert find_journey(store, 0, 1, excludes, CFG) is None


def test_forcing_a_stop_never_drops_the_two_chosen_artists():
    # Excluding an endpoint has never removed it, and the second search must
    # not change that. Design section 6, test 5.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    excludes = [Exclusion(node=0, reason=DISLIKE), Exclusion(node=1, reason=KNOWN)]
    path, _rule = find_journey(store, 0, 1, excludes, CFG)
    assert path[0] == 0 and path[-1] == 1
```

The import line at the top of the file becomes:

```python
from artistpath_api.pathfinding import (
    DISLIKE,
    KNOWN,
    STOP_ADJACENT_ONLY,
    STOP_FORCED,
    STOP_NATURAL,
    Exclusion,
    find_journey,
    find_path,
)
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pathfinding.py -k journey
```

Expected: FAIL — `ImportError: cannot import name 'find_journey'`.

- [ ] **Step 3: Implement `find_journey`**

Append to `pathfinding.py`, after `find_path`:

```python
# How a journey came to have (or lack) an artist between its two endpoints.
# The frontend cannot re-derive this: once a stop is forced in, the result is
# indistinguishable from an ordinary path. Requirement and success condition:
# docs/superpowers/2026-07-25-gate1-clips-and-ux-execution-log.md section 16.
STOP_NATURAL = "natural"              # the least-cost path already had a stop
STOP_FORCED = "forced"                # the two are neighbours; a stop was inserted
STOP_ADJACENT_ONLY = "adjacent_only"  # neighbours, and nothing connects them both


def find_journey(
    store: GraphStore,
    source: int,
    target: int,
    excludes: list[Exclusion],
    cfg: ApiConfig,
) -> tuple[list[int], str] | None:
    """A path with at least one artist between the endpoints where possible.

    Every journey needs at least one stop (owner's decision, 2026-07-25). When
    the least-cost path is the two chosen artists and nothing else, search again
    with their direct connection forbidden; the same cost function chooses the
    detour, so no new scoring is introduced and this stays outside the paused
    path-quality work.

    Some pairs cannot be given a stop at all: roughly 8 % of artists hold a
    single connection in the graph, so their one neighbour has no route back
    except that connection (findings/2026-07-25-mutual-knn-stranding.md,
    MKS-6). Those fall back to the two-card path and say so rather than
    returning nothing, because a no-path result must only ever come from user
    exclusions.

    The second search re-reads the same exclusions, so a stop is never forced
    through an artist the user has already rejected.
    """
    path = find_path(store, source, target, excludes, cfg)
    if path is None:
        return None
    if len(path) != 2:
        # Includes the degenerate source == target case, which is length 1.
        return path, STOP_NATURAL

    detour = find_path(
        store, source, target, excludes, cfg, forbidden_edge=(source, target)
    )
    if detour is None:
        return path, STOP_ADJACENT_ONLY
    return detour, STOP_FORCED
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pathfinding.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/pathfinding.py api/tests/test_pathfinding.py
git commit -m "Give every journey a stop, or record that it cannot have one"
```

---

### Task 3: Serve `stop_rule` from the path endpoint

**Files:**
- Modify: `api/src/artistpath_api/models.py:25-26` (`PathResponse`)
- Modify: `api/src/artistpath_api/app.py:62-74` (`build_path`)
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: `find_journey` and the three `STOP_*` constants from Task 2.
- Produces: `POST /api/path` responds `{"artists": [...], "stop_rule": "natural" | "forced" | "adjacent_only"}`. The `artists` key and its shape are unchanged.

- [ ] **Step 1: Write the failing tests**

`test_app.py`'s existing `_client()` helper builds a **fixed** three-artist graph
(Radiohead / Muse / Coldplay) and takes no graph argument, so these tests need a
second helper. Add it directly below `_client`, matching the inline construction
already used at `test_app.py:106`:

```python
def _client_over(store):
    """A client over a purpose-built graph, for tests that need a given shape."""

    async def fetch_json(url, params):
        return {}

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(store, ArtistSearch(store, CFG), resolver, CFG))
```

Then append the tests. Note they use `store.mbids[i]`, as every other test in this
file does — do not hand-write MBID strings:

```python
def test_path_response_reports_a_natural_journey():
    # The existing fixture routes Radiohead -> Muse -> Coldplay: already has a stop.
    client, store = _client()
    a, c = store.mbids[0], store.mbids[2]
    body = client.post("/api/path", json={"sources": [a, c], "exclude": []}).json()
    assert body["stop_rule"] == "natural"
    assert len(body["artists"]) >= 3


def test_path_response_reports_a_forced_stop():
    # Radiohead and Muse are directly connected; Coldplay is the way round.
    client, store = _client()
    a, b = store.mbids[0], store.mbids[1]
    body = client.post("/api/path", json={"sources": [a, b], "exclude": []}).json()
    assert body["stop_rule"] == "forced"
    assert len(body["artists"]) >= 3
    assert [x["name"] for x in body["artists"]][0] == "Radiohead"


def test_path_response_reports_two_artists_with_nothing_between():
    # B's only connection is to A, so no stop can exist between them.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9)],
    )
    client = _client_over(store)
    a, b = store.mbids[0], store.mbids[1]
    body = client.post("/api/path", json={"sources": [a, b], "exclude": []}).json()
    assert [x["name"] for x in body["artists"]] == ["A", "B"]
    assert body["stop_rule"] == "adjacent_only"
```

**Expect one pre-existing test to change meaning.**
`test_path_respects_a_typed_exclusion` excludes Muse and then routes Radiohead →
Coldplay over the weak direct edge, producing a two-card path. Under this change it
becomes `adjacent_only` (Muse, the only way round, is excluded). Its assertion —
`"Muse" not in names` — still holds, so it should pass untouched. If it fails,
read why before editing it.

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_app.py -k stop
```

Expected: FAIL — `KeyError: 'stop_rule'`.

- [ ] **Step 3: Add the field and use the wrapper**

In `models.py`:

```python
class PathResponse(BaseModel):
    artists: list[ArtistOut]
    # Whether the journey needed a stop forced into it, and whether one was
    # possible. Wire contract, so snake_case; the frontend reads it as
    # stopRule. Values are pathfinding.STOP_*.
    stop_rule: str
```

In `app.py`, change the import on line 19 from `find_path` to `find_journey`, and
replace the body of `build_path` from `path = find_path(...)` onward:

```python
        journey = find_journey(store, source, target, excludes, cfg)
        if journey is None:
            raise HTTPException(409, "no path avoiding those artists")
        path, stop_rule = journey
        return PathResponse(
            artists=[artist_out(n) for n in path], stop_rule=stop_rule
        )
```

- [ ] **Step 4: Run the whole api suite**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q
```

Expected: PASS. If any pre-existing test asserts the exact shape of a path
response, update it to include `stop_rule` — that is a genuine contract change,
not a broken test.

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/models.py api/src/artistpath_api/app.py api/tests/test_app.py
git commit -m "Report on the wire whether a journey got its stop"
```

---

### Task 4: Carry `stopRule` through the frontend to the journey

**Files:**
- Modify: `frontend/src/api/types.ts`
- Modify: `frontend/src/api/client.ts:20-33` (`buildPath`)
- Modify: `frontend/src/hooks/usePath.ts:7-11,32-37`
- Modify: `frontend/src/routes/PathPage.tsx:70`
- Test: `frontend/src/api/client.test.ts`, `frontend/src/hooks/usePath.test.tsx`

**Interfaces:**
- Consumes: the `stop_rule` wire field from Task 3.
- Produces:
  - `export type StopRule = 'natural' | 'forced' | 'adjacent_only'` in `types.ts`.
  - `buildPath(...) -> Promise<{ artists: Artist[]; stopRule: StopRule }>` — **a breaking change from `Promise<Artist[]>`**; `usePath` is the only caller.
  - `PathState` gains `stopRule: StopRule`.
  - `JourneyList` gains a required prop `stopRule: StopRule`.

- [ ] **Step 1: Write the failing tests**

In `frontend/src/api/client.test.ts`, replace the existing
`buildPath unwraps the artists array and sends sources+exclude` test with:

```ts
test('buildPath returns artists and the stop rule, and sends sources+exclude', async () => {
  const fetch = mockFetch(200, {
    artists: [{ mbid: 'x', name: 'A', disambiguation: '', popularity: 0.5 }],
    stop_rule: 'forced',
  });
  const result = await buildPath(['a', 'b'], []);
  expect(result.artists).toHaveLength(1);
  expect(result.stopRule).toBe('forced');
  const body = JSON.parse(fetch.mock.calls[0][1].body);
  expect(body).toEqual({ sources: ['a', 'b'], exclude: [] });
});
```

Read the existing test first and keep its `mockFetch` usage and assertion style —
the `fetch.mock.calls` shape above must match how that file already asserts the
request body.

`frontend/src/hooks/usePath.test.tsx` uses a `Harness` component under
`MemoryRouter`, not `renderHook`. **Two changes are needed there.**

First, surface the new value without disturbing the existing assertions, which read
`getByTestId('state')`. Extend `Harness`:

```tsx
function Harness() {
  const state = usePath();
  return (
    <>
      <div data-testid="state">{state.status}:{state.error ?? ''}:{state.artists.map(a => a.name).join(',')}</div>
      <div data-testid="stop-rule">{state.stopRule}</div>
    </>
  );
}
```

Second — **and this breaks every existing test in the file if missed** — `buildPath`
no longer resolves to an array. Every `mockResolvedValue([...])` in this file must
become the new shape. For example the first test's mock becomes:

```tsx
  vi.spyOn(client, 'buildPath').mockResolvedValue({
    artists: [{ mbid: 'a', name: 'Miles', disambiguation: '', popularity: 1 }],
    stopRule: 'natural',
  });
```

and the empty one in `passes decoded exclusions to buildPath` becomes
`mockResolvedValue({ artists: [], stopRule: 'natural' })`. Tests that mock a
*rejection* are unaffected. Then add:

```tsx
test('exposes the stop rule from the response', async () => {
  vi.spyOn(client, 'buildPath').mockResolvedValue({
    artists: [{ mbid: 'a', name: 'A', disambiguation: '', popularity: 0.5 }],
    stopRule: 'adjacent_only',
  });
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('stop-rule')).toHaveTextContent('adjacent_only'));
});
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd frontend && npm test -- client usePath
```

Expected: FAIL — `result.artists is undefined` and `stopRule` undefined.

- [ ] **Step 3: Implement**

`types.ts`, append:

```ts
/** Whether a journey needed a stop forced in, and whether one was possible. */
export type StopRule = 'natural' | 'forced' | 'adjacent_only';

export interface PathResult {
  artists: Artist[];
  stopRule: StopRule;
}
```

`client.ts` — add `PathResult`/`StopRule` to the type import, then:

```ts
export async function buildPath(
  sources: string[],
  exclude: Exclusion[],
  signal?: AbortSignal,
): Promise<PathResult> {
  const r = await fetch(`${BASE}/path`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ sources, exclude }),
    signal,
  });
  if (!r.ok) throw new ApiError(r.status);
  const data = (await r.json()) as { artists: Artist[]; stop_rule: StopRule };
  return { artists: data.artists, stopRule: data.stop_rule };
}
```

`usePath.ts` — extend the state and the resolve handler:

```ts
export interface PathState {
  status: 'loading' | 'ready' | 'error';
  artists: Artist[];
  stopRule: StopRule;
  error?: 'notfound' | 'nopath' | 'unknown';
}
```

Add `StopRule` to the type import. Then change the three places that build state:

```ts
  const [state, setState] = useState<PathState>({
    status: 'loading', artists: [], stopRule: 'natural',
  });
```

```ts
    setState((prev) => ({ status: 'loading', artists: prev.artists, stopRule: prev.stopRule }));
    buildPath([from, to], decodeExclusions(params), controller.signal)
      .then(({ artists, stopRule }) => setState({ status: 'ready', artists, stopRule }))
      .catch((err) => {
        if (controller.signal.aborted) return;
        setState({ status: 'error', artists: [], stopRule: 'natural', error: classify(err) });
      });
```

`PathPage.tsx` line 70 — pass it through:

```tsx
            <JourneyList
              ref={journey}
              artists={state.artists}
              stopRule={state.stopRule}
              onBypass={handleBypass}
            />
```

- [ ] **Step 4: Run tests and the typecheck**

```bash
cd frontend && npm test -- client usePath && npm run build
```

Expected: tests PASS. `npm run build` will FAIL on `JourneyList` not accepting
`stopRule` — that is expected and Task 5 fixes it. Do not add the prop to
`JourneyList` here beyond what Task 5 specifies.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/types.ts frontend/src/api/client.ts frontend/src/hooks/usePath.ts frontend/src/routes/PathPage.tsx frontend/src/api/client.test.ts frontend/src/hooks/usePath.test.tsx
git commit -m "Carry the stop rule from the API to the journey"
```

---

### Task 5: Say so when two artists have nobody between them

**Files:**
- Modify: `frontend/src/components/JourneyList.tsx:13-17,46-68`
- Test: `frontend/src/components/JourneyList.test.tsx`

**Interfaces:**
- Consumes: `StopRule` from Task 4; `JourneyList` prop `stopRule`.
- Produces: nothing downstream. This is the last task.

- [ ] **Step 1: Write the failing tests**

Append to `frontend/src/components/JourneyList.test.tsx`:

```tsx
test('explains itself when the two artists have nobody between them', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  render(<JourneyList artists={artists} stopRule="adjacent_only" onBypass={vi.fn()} />);
  expect(screen.getByText(/next to each other/i)).toBeInTheDocument();
});

test('says nothing on an ordinary journey', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  render(<JourneyList artists={artists} stopRule="natural" onBypass={vi.fn()} />);
  expect(screen.queryByText(/next to each other/i)).not.toBeInTheDocument();
});

test('says nothing when a stop was forced in', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  render(<JourneyList artists={artists} stopRule="forced" onBypass={vi.fn()} />);
  expect(screen.queryByText(/next to each other/i)).not.toBeInTheDocument();
});
```

Every pre-existing `render(<JourneyList ... />)` call in this file also needs
`stopRule="natural"` added, or TypeScript will reject them.

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd frontend && npm test -- JourneyList
```

Expected: FAIL — the note is not rendered.

- [ ] **Step 3: Implement**

Add `StopRule` to the type import in `JourneyList.tsx`, then extend `Props`:

```tsx
interface Props {
  artists: Artist[];
  stopRule: StopRule;
  onBypass: (mbid: string, reason: BypassReason) => void;
  ref?: Ref<JourneyControls>;
}
```

and the signature: `export function JourneyList({ artists, stopRule, onBypass, ref }: Props) {`

Inside the `artists.map` callback, render the note after the card of the first
artist when there is nothing between the two. Replace the `<li>` block with:

```tsx
          <li key={artist.mbid}>
            <ArtistCard
              artist={artist}
              isPlaying={player.currentMbid === artist.mbid && player.isPlaying}
              isCurrent={player.currentMbid === artist.mbid}
              // The two artists you chose are the journey's endpoints; there is
              // nothing to reroute if you reject them.
              isEndpoint={i === 0 || i === artists.length - 1}
              onPlay={player.playFrom}
              onToggle={player.toggle}
              onBypass={onBypass}
              onClipResolved={(mbid, available) =>
                setHasClip((prev) => ({ ...prev, [mbid]: available }))
              }
            />
            {/* Some pairs cannot be given a stop: one of the two holds a single
                connection in the graph, and it is to the other. Saying so beats
                a page with two cards and nothing to press. */}
            {stopRule === 'adjacent_only' && i === 0 && (
              <p className="px-1 py-3 text-sm text-[var(--color-muted)]">
                These two are next to each other — there&rsquo;s no artist in between.
              </p>
            )}
          </li>
```

`--color-muted` is defined at `frontend/src/index.css:8`. Use it as written; do not
introduce a new token.

- [ ] **Step 4: Run the frontend suite and the typecheck**

```bash
cd frontend && npm test && npm run build && npm run lint
```

Expected: all PASS. `npm run build` now succeeds — Task 4's expected type error is
resolved by this task.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/JourneyList.tsx frontend/src/components/JourneyList.test.tsx
git commit -m "Explain a journey with nobody in between"
```

---

### Task 6: Verify against the real graph, and queue it for use

**Files:**
- Create: `builder/analysis/2026-07-25-f1-verification/check.py`
- Modify: `docs/superpowers/TEST-QUEUE.md`

**Interfaces:**
- Consumes: `find_journey` from Task 2.
- Produces: nothing downstream.

**Why this task exists:** the design rests on the claim that non-adjacent paths are
untouched. Unit tests use tiny hand-built graphs where that is true by construction.
This demonstrates it on the artifact the app actually serves.

- [ ] **Step 1: Write the check**

Create `builder/analysis/2026-07-25-f1-verification/check.py`:

```python
"""Verify F1 against the adopted artifact. READ-ONLY; changes nothing.

Design: docs/superpowers/specs/2026-07-25-f1-minimum-stop-design.md section 7.
Run from api/:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-25-f1-verification/check.py
"""

import hashlib
import random

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import STOP_ADJACENT_ONLY, find_journey, find_path

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

cfg = ApiConfig()
digest = hashlib.sha256()
with open(cfg.graph_path, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
        digest.update(chunk)
assert digest.hexdigest() == ADOPTED_SHA256, "not the adopted artifact"
store = GraphStore.load(cfg.graph_path)
by = {n.lower(): i for i, n in enumerate(store.names)}

# 1. The reported case gains a stop.
a, b = by["radiohead"], by["weezer"]
path, rule = find_journey(store, a, b, [], cfg)
print(f"Radiohead -> Weezer: {len(path)} cards, {rule} -> "
      f"{[store.names[x] for x in path]}")
assert len(path) >= 3, "the reported case still has no stop"

# 2. A stranded pair falls back and says so.
a, b = by["doves"], by["elbow"]
path, rule = find_journey(store, a, b, [], cfg)
print(f"Doves -> Elbow: {len(path)} cards, {rule}")
assert rule == STOP_ADJACENT_ONLY and len(path) == 2

# 3. Ordinary paths are untouched. This is the claim the design rests on.
random.seed(0)
changed = 0
for _ in range(200):
    u, v = random.randrange(store.artist_count), random.randrange(store.artist_count)
    if u == v:
        continue
    before = find_path(store, u, v, [], cfg)
    if before is None or len(before) == 2:
        continue  # the two-card case is exactly what this feature changes
    after, rule = find_journey(store, u, v, [], cfg)
    if after != before or rule != "natural":
        changed += 1
        print(f"CHANGED: {store.names[u]} -> {store.names[v]} ({rule})")
print(f"\nordinary paths altered: {changed} (must be 0)")
assert changed == 0, "a non-adjacent path changed; the design's core claim is false"
print("all checks passed")
```

- [ ] **Step 2: Run it**

```bash
cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-25-f1-verification/check.py
```

Expected: all three pass, `ordinary paths altered: 0`.

**If check 3 fails, stop and report.** It means forcing a stop changed a journey it
should not have touched, and the design is wrong rather than the code.

- [ ] **Step 3: Add the use-the-app queue entry**

Insert at the top of `docs/superpowers/TEST-QUEUE.md`, directly under the `---`
that follows the header. Written for the owner — **no identifiers, no jargon**:

```markdown
## QUEUED — 2026-07-25 — journeys now always have someone in the middle

**Ten minutes, no waiting.** Pick two artists who are very close to each other —
`Radiohead → Weezer` is the one you reported, and any two artists you'd expect to
sit right next to each other will do.

**What changed.** Before, a pair like that gave you two cards and nothing to press.
Now the app routes around the direct connection and puts at least one artist in
between. Nothing else about paths changed — any journey that already had someone in
the middle is exactly the journey you got yesterday.

**What to exercise:**

1. **`Radiohead → Weezer`.** It should now have at least one artist between them.
2. **Two or three pairs you already have a feel for**, as a regression check. These
   should be unchanged.
3. **A pair that is very close but obscure** — try `Doves → Elbow`. This one *cannot*
   be given a stop: Elbow has exactly one connection in the whole graph and it is to
   Doves. You should get two cards **plus a line saying they're next to each other
   and there's nobody in between**. The line appearing is the thing to check.

**Two things worth your opinion, because no measurement can settle them:**

- **How long is too long?** Forcing a way round can produce a longer journey than you
  asked for — usually one extra artist, but one test pair produced seven. If that
  feels wrong, say so; it is capped at nothing right now, deliberately.
- **Famous pairs get a famous stop.** `Radiohead → Weezer` routes through The
  Beatles. That is the cheapest way round, not a preference. Worth knowing whether it
  reads as reasonable or as lazy.

**What "wrong" would look like:** a pair that still gives you two cards with no
explanation; a journey between two artists you know that has *changed* when it should
not have; or the "next to each other" line showing up on a normal journey.

**Best bug report:** the URL from the address bar.
```

- [ ] **Step 4: Commit**

```bash
git add builder/analysis/2026-07-25-f1-verification/check.py docs/superpowers/TEST-QUEUE.md
git commit -m "Verify F1 on the real graph and queue it for use"
```

---

## After the last task

- Run the full suites once more: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q`
  and `cd frontend && npm test && npm run build && npm run lint`.
- Run Snyk `snyk_code_scan` over `api/src` and fix anything it reports, per the
  global instruction.
- Open the pull request from `f1-min-stop`. The body carries: a link to this plan and
  to the design; the verification output from Task 6 including `ordinary paths
  altered: 0`; that F1's success condition is cited from the execution log §16 and not
  restated; and that the finding explaining *why* some pairs cannot be given a stop is
  `findings/2026-07-25-mutual-knn-stranding.md`, already merged.
- **Do not mark F1 discharged.** Its condition is satisfied by observation, and the
  queue entry above is the observation. It closes when the owner runs it.
