# Plan — `DEP-33` blocker remediation, then Track C

**Role: ACTIVE plan.** Identifier series `RMD-`, verified disjoint from `DEP-`, `TR-`,
`TKA-`, `TKD-`, `TKB-`, `FMS-`, `CNS-`, `ARC-`, `SEC-`, `QUA-`, `FRO-`, `BYP-` by
repo-wide grep, 2026-07-27 (no matches).

**Governing inputs**, in precedence order:

1. [`findings/2026-07-26-track-b-cdk-review.md`](../findings/2026-07-26-track-b-cdk-review.md)
   §2 — the ranked blocker queue this plan executes.
2. [`2026-07-26-HANDOFF-track-b-complete.md`](../2026-07-26-HANDOFF-track-b-complete.md) —
   the seven must-not-revert claims. **This plan reverses one of them on new evidence; see
   `RMD-6`.**
3. [`2026-07-26-gate2-track-b-execution-log.md`](../2026-07-26-gate2-track-b-execution-log.md)
   §1 (deployed identity), §4 (must-not-revert), §6 (environment traps).

**No routing, weight, graph or cost-function change. `pathfinding.py` is not opened.** The
path-quality pause is intact and nothing here is a resume signal.

---

## §0 Why there is no factor table

`CLAUDE.md` requires one of any plan comparing variants. **This plan compares nothing and
runs no experimental arm** — every task is a defect fix with a binary done-condition. The
table is omitted deliberately, not forgotten. The analogous discipline that *does* apply
here is the mutation gate: every test this plan adds must be shown to go **red** before it
is allowed to count, per `TKB-4`'s lesson that a green result from a new instrument is not
evidence until it has been shown to go red.

## §1 Scope

**Nine of the review's ten blockers, one new finding, and two of security's pre-share
picks.**

`QUA-4` (rank 9, the runbook's wrong test count) **is already discharged** — commit
`6f49ab9` deleted the counts rather than correcting them and rewrote the `cd` chain to
`git rev-parse --show-toplevel`, which also closes `ARC-9`/`QUA-5`. §2's table does not say
so. **Do not re-do it**; `RMD-0` below only annotates the record.

**New, found 2026-07-27 by the read-only AWS checks that preceded this plan:**
`ARTISTPATH_CORS_ORIGINS` is **absent from the running service**, so the deployed API is
serving `config.py`'s dev default. Measured, not inferred — see `RMD-6`. This is the fourth
instance of the project's signature defect and the first that **no test in any package could
have caught**, because the gap is between the template and AWS.

## §2 Pre-flight verification — every name this plan uses, resolved

`CLAUDE.md`: *before executing a plan, grep every function, file, and config value it names.*
Done 2026-07-27, against the tree at `86f17dd`.

| name | resolves to | state |
|---|---|---|
| `ApiConfig.cors_origins` | `api/src/artistpath_api/config.py:70-78` | exists; default `http://localhost:5173` |
| `require_origin_secret` | `api/src/artistpath_api/app.py:61-71` | exists; `/health` exempt at `:67` |
| `hmac.compare_digest` call | `api/src/artistpath_api/app.py:67-69` | compares **`str`** — this is `SEC-1` |
| `viewer_function.js` `handler` | `infra/src/artistpath_infra/viewer_function.js:20` | exists; 401 body empty at `:25-32` |
| `__EXPECTED_AUTH__` substitution | `infra/src/artistpath_infra/stack.py:202-209` | username literal `artistpath` at `:203` |
| `fn_association` | `stack.py:216-221`, used at `:239` and `:267` | attached to **both** behaviours |
| `DeployInputs.include_service` | `stack.py:50`, branch at `:108-118` | storage stage returns early |
| `stage=storage` context read | `infra/app.py:46` | exists |
| `image_tag` default | `infra/app.py:59` | `"latest"` — this is `ARC-6` |
| `_SIDECAR` / `graph_key` | `infra/app.py:18-23` / `:51-53` | two independent env vars — `ARC-7` |
| `table_name="artistpath-clips"` | `stack.py:90` **and** `config.py:91` | two literals, nothing binds them — `ARC-5` |
| `repository_name="artistpath-api"` | `stack.py:102`; `service_name` at `:152` | fixed names + `RETAIN` — `ARC-4` |
| log retention construct | **absent from `stack.py` entirely** | `ARC-2`; confirmed live, all 5 groups Never Expire |
| autoscaling configuration | **absent from `stack.py`** | `SEC-5`; account default (25) applies |
| `test_cors_origins_is_present_and_empty_not_merely_unset` | `infra/tests/test_stack.py:108-115` | exists and passes — on the **template** |
| `test_cors_allows_configured_dev_origin` | `api/tests/test_cors.py:25-33` | asserts the dev default; **`RMD-6` must rewrite it** |
| `test_the_viewer_function_gates_on_…` | `infra/tests/test_stack.py:186-192` | substring-only — `QUA-1`/`FRO-5` |
| attachment assertion | **no test asserts `FunctionAssociations`** | confirmed — `QUA-2` |
| `test_origin_secret.py` | `api/tests/test_origin_secret.py` | one endpoint only — `QUA-3` |
| Vite `/api` proxy | `frontend/vite.config.ts:21-23` | dev is same-origin — load-bearing for `RMD-6` |

**Nothing in this plan names something that does not exist.** Two named things are absent by
design and that absence *is* the finding (log retention, autoscaling); both are marked above.

## §3 Handoff seams — named at authoring time

Thirteen tasks across four packages is past the point `CLAUDE.md` says improvisation holds.
**Three stages, two seams.** Each seam is a committed artifact, not a live understanding.

| stage | tasks | seam condition |
|---|---|---|
| **1 — make the suite able to reject** | `RMD-1` … `RMD-5` | All four suites green **and** the review §1 mutation set re-run with the blocker-related rows now red. Commit, push, update the PR body. **Retire the session here.** |
| **2 — deploy safety** | `RMD-6` … `RMD-10` | A `cdk diff` against the deployed stack showing only the intended changes, and drift re-run clean. Commit, push. **Retire the session here.** |
| **3 — the first user** | `RMD-11` … `RMD-13` | `RMD-13` does not complete in this plan — it lands a runbook step that executes at Track C cutover. Stage 3 closes when the other two are done and the step is written. |

**Stage 1 is the one that must not be skipped or reordered into the others.** Its whole
purpose is that stages 2 and 3 land against a suite that can reject them. Doing stage 2
first means changing infrastructure while the suite still ratifies a broken stack.

---

## Stage 1 — make the suite able to reject

### `RMD-0` — annotate the queue (5 minutes, do first)

`QUA-4`, `ARC-9` and `QUA-5` are already fixed by `6f49ab9`. Add a line to the review's §2
and §4 saying so, with the commit hash. **Do not edit the findings' substance** — the
document is authoritative for its own findings; this is a status annotation.

**Done when:** a reader working §2 top-to-bottom cannot start work that is already done.

### `RMD-1` — assert the password function is attached (`QUA-2`, rank 1)

**The only blocker that is silent.** Detaching the function leaves the API gated and the
whole site publicly readable, with every test green and no symptom the owner could see.

**Now partly measured, 2026-07-27:** the deployed default behaviour has exactly one
viewer-request function, no Lambda@Edge, `TrustedSigners` disabled and `TrustedKeyGroups`
disabled — so the function is the **sole** access control on that behaviour. The premise
holds. The last step (CloudFront with no viewer-request function serves the origin) remains
unmeasured and must not be measured by detaching the live function.

**Change:** `infra/tests/test_stack.py`. Assert `FunctionAssociations` on
`DefaultCacheBehavior` **and** on the `/api/*` behaviour, each with `EventType:
viewer-request` and pointing at the stack's one `AWS::CloudFront::Function`.

**Mutation that must go red:** delete `function_associations=fn_association` from
`stack.py:239`. Then separately from `:267`. Both must fail.

### `RMD-2` — test the function's behaviour, not its source (`QUA-1`, `FRO-5`, `ARC-3`, rank 5)

Found independently by three reviewers. `test_stack.py:186-192` asserts three substrings
appear in the function source; inverting the gate passed all 18 tests.

**Change:** a real behavioural test. The function is JS and the suite is pytest, so run it:
extract `FunctionCode` from the synthesised template, and drive `handler(event)` under
`node` (already a hard dependency — CDK needs it). Cases:

| event | expected |
|---|---|
| no `authorization` header | 401 |
| wrong `authorization` value | 401 |
| correct value, `/path/<mbid>/<mbid>` | request returned, `uri` rewritten to `/index.html` |
| correct value, `/api/artists/search` | request returned, `uri` **unchanged** |
| correct value, `/assets/index-abc123.js` | request returned, `uri` **unchanged** |

The last two are `TR-5`'s rewrite rule (`viewer_function.js:42`) and are the only automated
check it will ever have.

**Mutations that must go red:** invert the comparison at `viewer_function.js:24`; make the
synth-time `.replace()` at `stack.py:208` a no-op; drop the `/api/` guard at `:42`.

### `RMD-3` — the origin-secret middleware, on every endpoint (`QUA-3`, rank 6)

`api/tests/test_origin_secret.py` exercises one endpoint. Narrowing the middleware to
GET-only leaves `POST /api/path` — the expensive Dijkstra — ungated; exempting `/track`
un-gates the endpoint whose unrate-limited catalogue calls are the gate's stated reason for
existing.

**Change:** parametrise over every route in `app.py` × the methods each accepts:
`GET /api/artists/search`, `POST /api/path`, `GET /api/artists/{mbid}/track`. Assert 403
without the header and non-403 with it. **Assert `/health` stays exempt** — that is
must-not-revert claim #2 and the test must hold it in both directions.

**Mutations that must go red:** narrow the condition at `app.py:67` to GET-only; add
`/track` to the exemption; delete the `/health` exemption (this one must go red for the
*opposite* reason — the exemption is load-bearing).

### `RMD-4` — `SEC-1`: compare bytes, not strings

`app.py:67-69` passes two `str` to `hmac.compare_digest`, which raises `TypeError` on
non-ASCII. An unauthenticated request with a non-ASCII byte in `x-origin-secret` returns
**500** and writes a traceback into the telemetry log group. It fails closed, so it is not a
bypass.

**Change:** encode both sides — `compare_digest(header.encode("utf-8", "surrogateescape"),
cfg.origin_secret.encode("utf-8"))` or equivalent. Keep the `hmac` call: must-not-revert
claim #7 marks it a permanent review-only invariant, and `QUA-13` says so. **Comparing bytes
is the fix, not a simplification** — the handoff states this explicitly.

**Test, and it needs care:** the handoff records that `TestClient` cannot reproduce this —
httpx rejects the header client-side with `UnicodeEncodeError`. **The test must build the
ASGI scope directly** and call the app, per the handoff's note.

**Mutation that must go red:** revert to comparing `str`.

### `RMD-5` — close the cheap assertion gaps, then re-run the mutation set

`QUA-6` (`RETAIN` unasserted; the versioning test matches *any* bucket), `QUA-7` (billing
threshold passes with the value hardcoded), `QUA-8` (table name unasserted), `QUA-9` (image
tag and port unasserted) are one-line assertions each. They are not blocking individually —
but they are six of the review's green mutations, and without them stage 1's gate is
meaningless.

**Then re-run the review §1 mutation set** and record which rows now go red.

> **One thing to resolve while doing this:** §1's table is ambiguous about its own count.
> Nine single rows plus a middleware row marked "×3" is either ten mutations or twelve,
> and the headline says ten of nineteen. Resolve it by re-running, and record the real
> number. Do not restate "ten" if the re-run disagrees.

**Done when:** every row that maps to a stage-1 fix is red, and any row still green is named
with the finding that governs it.

**⚠ Seam. Commit, push, update the PR body, retire the session.**

---

## Stage 2 — deploy safety

### `RMD-6` — `ARTISTPATH_CORS_ORIGINS` is absent in production (NEW, 2026-07-27)

**This task reverses must-not-revert claim #1. Read this whole entry before touching it.**

**What the record says.** Execution log §4 claim 1 and handoff claim 1: *set it to the empty
string, not omitted; omitting it yields the dev default `http://localhost:5173`; a test holds
it and goes red when the line is deleted — checked by mutation.* All of that is true and the
test at `test_stack.py:108-115` is correct.

**What is actually deployed.** Measured 2026-07-27:

- `cloudformation detect-stack-drift` → `DRIFTED`, one resource, `ApiService`. Property
  difference at `…/RuntimeEnvironmentVariables/4`: expected
  `{"Name":"ARTISTPATH_CORS_ORIGINS","Value":""}`, actual `null`, `DifferenceType: REMOVE`.
- Live probe of the App Runner origin's `/health` (the one path exempt from the origin
  secret): `Origin: http://localhost:5173` → `access-control-allow-origin:
  http://localhost:5173`. **Negative control:** `Origin: https://evil.example` → no such
  header. So the API is *matching* against the dev default, not echoing.

**The instruction in the record is unachievable by that mechanism.** An empty-valued
environment variable does not survive to the running App Runner service. The template is
right, the test is right, and neither can see production.

**Impact today is small and should be stated as such:** everything but `/health` requires the
secret header only CloudFront adds, so a page on a stranger's machine can read `/health` and
nothing else. `/health` discloses artifact identity, which is already logged as `SEC-6`.

**Change, and the first item is the load-bearing one:**

1. **`config.py:74` — default `"http://localhost:5173"` → `""`.** This makes *absence* the
   safe state, so the class cannot recur on any future deploy. **Safe because dev is
   same-origin too**: `frontend/vite.config.ts:21-23` proxies `/api` → `:8000`, so the
   browser only ever talks to `:5173`. The dev default was never needed.
2. **`api/tests/test_cors.py:25-33`** currently asserts the dev default and **will fail** —
   rewrite it to pass an explicit origin via `replace(ApiConfig(), cors_origins=(...))`, and
   keep `test_cors_absent_for_unlisted_origin` as the negative control. Add a test that the
   **default** config allows nothing.
3. **Keep `_env("ARTISTPATH_CORS_ORIGINS", "")` at `stack.py:174`** and keep
   `test_stack.py:108-115`. They now express intent rather than carry the guarantee; update
   both comments to say the guarantee moved to the API default and why.
4. **Add `detect-stack-drift` to the runbook's manual gates** (`infra/README.md` §7). It is
   the only instrument in this project that can see a template-vs-AWS gap, it took one call,
   and nobody had run it. Note in the runbook that `Cpu`/`Memory` always report drifted —
   App Runner normalises `1 vCPU`/`2 GB` to `1024`/`2048` — so those two rows are expected
   and are **not** drift.
5. **Correct the record**: execution log §4 claim 1, and a line in the handoff's must-not-
   revert list. State the measurement, not just the conclusion.

**Done when:** a live probe of `/health` with `Origin: http://localhost:5173` returns **no**
`access-control-allow-origin` header, after redeploy.

### `RMD-7` — the storage-stage footgun (`ARC-1`, rank 2)

`-c stage=storage` against the deployed stack deletes eight resources including the
CloudFront distribution — synthesised and diffed by the reviewer. **A deleted distribution
does not come back with the same domain, so every link ever shared dies permanently.** The
guard today is a sentence in `infra/README.md`; §2 is the *first* deploy command an operator
meets.

**Change:** make it a mechanism. `infra/app.py:46` reads the context flag with no check that
the stack is new. Options, in the order I would try them: refuse to synth the storage stage
if the stack already exists (`include_service=False` plus a deployed stack is always a
mistake); or gate it behind a second explicit context flag whose name states the
consequence. **Add a test** — `QUA-10` records that `infra/app.py` has no test at all, so
`TKB-7`'s protection currently rides on an unverified context string.

**Mutation that must go red:** flip the storage-stage guard off.

### `RMD-8` — log retention was never implemented (`ARC-2`, rank 7)

Design §5 specified 90 days. It is in no tracking document — the completeness-failure shape
`CLAUDE.md` names. **Confirmed live 2026-07-27:** all five log groups report
`retentionInDays: null` (Never Expire), including the two `apprunner-availability-probe`
leftovers from `TKB-8`. Telemetry is `DEP-2`'s entire sink and accumulates unbounded under a
$25 alarm that measures something else.

**Change:** CDK cannot create App Runner's log groups (App Runner creates them), so this is
two runbook commands — `aws logs put-retention-policy` for the two `artistpath-api` groups.
**Put them in the runbook as a numbered post-deploy step, not a note**, and state that they
must be re-run if the service is ever recreated (a new service id means new group names).

**Environment trap:** `MSYS_NO_PATHCONV=1` is required — the group names start with `/aws/`
and Git Bash rewrites them into a Windows path (execution log §6).

**While there:** decide the two probe groups. They hold `TKB-8`'s only trace and cost
effectively nothing. Deleting them is fine; leaving them is fine. Just record which.

### `RMD-9` — fixed physical names and the unbound table name (`ARC-4` + `ARC-5`, rank 8)

`ARC-5` is one line and closes half of `ARC-4`, so they go together.

**`ARC-5`:** `artistpath-clips` is a literal in `stack.py:90` and again in `config.py:91`,
with nothing binding them. Pass the table name through as an env var on the service, the way
every other config value already travels. **Then assert it** (`QUA-8`).

**`ARC-4`:** `repository_name="artistpath-api"` (`stack.py:102`) and
`service_name="artistpath-api"` (`:152`), plus `RETAIN` on the repo and both retained
buckets, means any teardown orphans globally-named resources and the next `cdk deploy` fails
`AlreadyExists` — discovered at the worst moment. Full de-hardcoding is larger than this
plan; **at minimum, document the recreate procedure in the runbook** (what to delete by hand,
in what order) so the failure is recoverable rather than merely surprising.

### `RMD-10` — `SEC-5`: no autoscaling cap

The account default (max 25 instances) applies. The origin secret rejects requests *inside*
the container, **after** App Runner has counted and scaled on them. `DEP-17`'s claim that the
gate stands between a forwarded link and an unbounded bill is true through CloudFront and
false at the API origin — the same shape `TR-7` corrected once.

**Change:** add an `AutoScalingConfiguration` with a low `MaxSize` (2 is ample for
friends-and-family) and assert it. Security flagged this as fix-before-sharing.

**⚠ Seam. `cdk diff` against the deployed stack, drift re-run, commit, push, retire.**

---

## Stage 3 — the first user

### `RMD-11` — nobody can log in (`FRO-2`, rank 3)

The credential is `artistpath:<password>` (`stack.py:203`). The browser asks for a username;
**nothing anywhere states it**, and the 401 body is empty (`viewer_function.js:25-32`). The
first friend's first attempt is wasted.

**Change:** give the 401 a body that names the username. It is a shared password, not
authentication — the function's own comment says so — so naming the username discloses
nothing. Serve minimal HTML with the username and a line saying the password was shared
separately.

**Also flagged, and it stays a risk rather than a measurement:** in-app browsers (WhatsApp,
Instagram) frequently never show the auth dialog. No phone was available to the reviewer.
**This is the deferred phone section in `TEST-QUEUE.md` finally becoming runnable** — its
trigger was the Gate 2 cutover.

### `RMD-12` — a returning visitor gets a blank page after any redeploy (`FRO-1`, rank 4)

**Verified live by the reviewer:** an object uploaded exactly as the runbook syncs it returns
`ETag` and `Last-Modified` and **no `Cache-Control`**, so browsers fall back to heuristic
freshness. The default behaviour is `CachingOptimized`, and `--delete` removes the hashed
asset the stale `index.html` points at. No error boundary, so the symptom is a white screen
with no text.

**Change:** two-pass sync in the runbook — hashed assets with a long immutable max-age,
then `index.html` with `no-cache`, uploaded **last**. Also `FRO-7`: put static fallback
markup in `index.html` so a delivery failure gives a friend something to read out instead of
a blank page.

**Machine-state caveat from the handoff:** `aws s3 sync`'s content-type guessing was checked
on this machine and is correct (`.js → text/javascript`). That is not a repo property —
re-check if the deploy moves machines, because a module script served as `text/plain` is
refused and gives the *same* blank page.

### `RMD-13` — prove the gate admits, not just that it rejects (`FRO-4`, rank 10)

The runbook proves the gate returns 401 without a password. **No step anywhere makes an
authenticated request to the site**, so `TR-5`'s SPA fallback — found independently by two
reviewers — would ship unverified.

**This task cannot complete before Track C**, because the SPA bucket is empty and every path
returns 403 whether the rewrite works or not. What lands now is the *step*:

1. Load the site in a real browser, enter the password.
2. Confirm a shared `/path/<mbid>/<mbid>` link returns the app, not a 403 or a blank page.
3. Confirm a path builds from within it — that exercises whether the browser re-attaches
   cached basic credentials to the SPA's same-origin `fetch()` calls, which is the mechanism
   the whole app depends on and which no browser has ever exercised.

Review §7 names 3 as one of three classes nobody verified. **It almost certainly works — and
so did `TR-5`.**

---

## §4 What this plan does NOT do

- **Track C itself** (syncing the SPA). This plan ends where Track C begins; `RMD-12` and
  `RMD-13` prepare it.
- **`ARC-4` in full.** De-hardcoding every physical name is larger than this plan; `RMD-9`
  takes the one-line half and documents the rest.
- **The eight deferred findings in review §5.** Each has a condition; none has come due.
  Re-check `SEC-10` (repo is private today) if that ever changes.
- **`DEP-16`'s telemetry round-trip** and **`DEP-17`'s cost measurement.** Both still owed,
  both cheap now that real logged data exists. `DEP-17` in particular: the billing alarm was
  confirmed `OK` on a real datapoint 2026-07-27, but the figure covers only a few hours of
  the service running, so it is not yet a run rate.
- **Anything path-quality.** Paused by owner decision.

## §5 Record corrections this plan owes

Tracked here so they cannot drop out — that is the completeness-failure shape.

| what | where |
|---|---|
| `QUA-4`, `ARC-9`, `QUA-5` already fixed by `6f49ab9` | review §2 and §4 (`RMD-0`) |
| must-not-revert claim #1 reversed on measurement | execution log §4, handoff list (`RMD-6`) |
| §1's mutation count resolved | review §1 (`RMD-5`) |
| billing alarm confirmed `OK`, deferral closed | handoff's "not in the durable record" list |
| log retention confirmed Never Expire **live** | review §7 item 2 — that gap is now closed |
| drift detection added to the standing gates | `infra/README.md` §7 (`RMD-6`) |
