# `DEP-33` blocker remediation — execution log

**Role: ACTIVE record of this work.** Identifiers `RMD-`. Plan:
[`plans/2026-07-27-dep33-blocker-remediation.md`](plans/2026-07-27-dep33-blocker-remediation.md).
Governing review:
[`findings/2026-07-26-track-b-cdk-review.md`](findings/2026-07-26-track-b-cdk-review.md) §2.
PR #30 on `gate2-dep33-blockers`.

**Appended per task, not at closeout.** Decisions and reasoning, not narration.

**No routing, weight, graph or cost-function change. `pathfinding.py` is not opened.** The
path-quality pause is intact.

---

## §0 The three read-only AWS checks that preceded the plan

Run 2026-07-27 at the owner's instruction, before any planning. They closed two open
questions and found one new defect. **The account and region were confirmed via
`sts get-caller-identity` before anything was read**, and match the deployed identity owned by
[`2026-07-26-gate2-track-b-execution-log.md`](2026-07-26-gate2-track-b-execution-log.md) §1 —
which owns those values and is cited, not restated, here and below.

### `RMD-A` — the billing alarm is `OK`, and its deferral closes

`ArtistpathStack-BillingAlarm3477AF51-uUQwQTv33BoM`: `StateValue: OK`, on the real datapoint
`13.85` against threshold `25.0`, `treat_missing_data: notBreaching`.

**Why this was owed:** the Track B handoff records that the alarm has never fired and its
failure mode is *silence* — an alarm stuck in `INSUFFICIENT_DATA` looks exactly like an alarm
with nothing to report. It asked for confirmation within ~12 hours of the deploy. **It is not
silent: it has a real datapoint, so the metric is flowing and prerequisite P3 took.**

**What it does NOT settle.** `EstimatedCharges` read `13.85` at both 26/07 20:00 and 27/07
02:00 — flat, and covering only a few hours of App Runner running. That is billing lag, not a
run rate. **`DEP-17` stays unmeasured** and two identical datapoints are not a trend.

### `RMD-B` — `ARC-2` confirmed live, not merely absent from source

All five CloudWatch log groups report `retentionInDays: null` — **Never Expire**:

- `/aws/apprunner/artistpath-api/40e4a1cf…/{application,service}`
- `/aws/apprunner/apprunner-availability-probe/546fc1dc…/{application,service}` (`TKB-8`'s
  leftovers, as the handoff said)
- `/aws/lambda/ArtistpathStack-CustomS3AutoDeleteObjectsCustomRes-…`

The API's application group has a stream with an event at ~06:20 EDT today, so it is live and
accumulating. `storedBytes` reads 0 on every group, which is CloudWatch's reporting lag and
**should not be read as "empty"** — the stream timestamp contradicts it.

This closes item 2 of review §7's "unverified" list for retention specifically.

### `RMD-C` — `QUA-2`'s premise, measured on its load-bearing half

Review §7 flagged rank 1's central claim as *an inference about CloudFront's behaviour model,
not a measurement*. Read-only, against the distribution named in Track B's log §1:

| behaviour | viewer-request fns | Lambda@Edge | TrustedSigners | TrustedKeyGroups |
|---|---|---|---|---|
| default (the site) | **1** | 0 | disabled | disabled |
| `/api/*` | **1** (same fn) | 0 | disabled | disabled |

**So the viewer function is the sole access control on the site.** There is no signed-URL, no
signed-cookie and no second function behind it. The one step still unmeasured is that
CloudFront with no viewer-request function serves the origin — which is CloudFront's defining
behaviour, and measuring it would mean detaching the gate on the live distribution. **Not
done, and must not be.**

**Rank 1 stands unchanged.** Also re-confirmed live in passing: the `/api/*` behaviour pins
cache policy `4135ea2d-6df8-44a3-9df3-4b5a84be39ad` (managed `CachingDisabled`) — must-not-
revert claim #4, the one that stops `C2` returning as an apparent regression in closed work.

### `RMD-D` — NEW DEFECT: `ARTISTPATH_CORS_ORIGINS` is absent in production

**`cloudformation detect-stack-drift` → `DRIFTED`, 1 resource.** `ApiService`
(`AWS::AppRunner::Service`), three property differences:

| path | expected | actual | real? |
|---|---|---|---|
| `…/RuntimeEnvironmentVariables/4` | `{"Name":"ARTISTPATH_CORS_ORIGINS","Value":""}` | `null` (**REMOVE**) | **yes** |
| `/InstanceConfiguration/Memory` | `2 GB` | `2048` | no — App Runner unit normalisation |
| `/InstanceConfiguration/Cpu` | `1 vCPU` | `1024` | no — same |

**Confirmed by direct measurement, so it does not rest on drift detection being right.** Live
probe of the App Runner origin's `/health` (the one path exempt from the origin secret):

| `Origin:` sent | response | `access-control-allow-origin` |
|---|---|---|
| `http://localhost:5173` | 200 | **`http://localhost:5173`** |
| `https://evil.example` | 200 | *absent* |
| *(none)* | 200 | *absent* |

The negative control is what makes this a measurement: the API is **matching** against
`config.py:70-78`'s dev default, not echoing whatever it is asked.

**What this reverses.** Execution log §4 claim 1 and handoff must-not-revert #1 say: set the
variable to the empty string, never omit it; a test holds it and goes red when the line is
deleted. **All of that is true, and none of it reaches production.** An empty-valued
environment variable does not survive to the running App Runner service. `stack.py:174` sets
it; `test_stack.py:108-115` holds it; the service does not have it.

**Impact today is small and is stated as small:** everything but `/health` needs the secret
header only CloudFront adds, so a page on a stranger's machine reads `/health` and nothing
else — and `/health`'s disclosure is already logged as `SEC-6`.

**Impact as a class is the finding.** This is the fourth instance of the project's signature
defect after `FMS-P1`, `TR-2` and `TKB-4`, and the first where the gap is **between the
template and AWS**, which no test in any of the four packages can reach. `TKB-4` taught that a
green result from a new instrument is not evidence until it has been shown to go red. This
teaches the next one: **a correct, mutation-verified test can be green against a template that
production does not match.** Drift detection is the instrument that sees it, it took one call,
and nobody had run it. `RMD-6` adds it to the standing gates.

---

## Stage 1 — make the suite able to reject

### `RMD-0` — the queue is nine blockers, not ten

`QUA-4` (rank 9) and `ARC-9`/`QUA-5` were **already closed** in `6f49ab9`, the closeout that
committed the review itself: `infra/README.md` §7 now deletes the expected test counts rather
than correcting them, and its four gates each start
`cd "$(git rev-parse --show-toplevel)/<pkg>"` so they execute as pasted.

The findings document did not say so, so a session working §2 top-to-bottom would have
started finished work. **Annotated in place** — §2's rank-9 row and a note above §4 — with the
commit hash. The findings' substance is untouched; the document remains authoritative for
its own findings.

### `RMD-1` — `QUA-2`, rank 1: the password function's attachment is now asserted

**Two tests added** to `infra/tests/test_stack.py`, one per behaviour, because the site and
the API are separate `FunctionAssociations` and each is an independent fact:

- `test_the_password_function_is_attached_to_the_site_itself`
- `test_the_password_function_is_attached_to_the_api_behaviour_too`

Both assert the behaviour's viewer-request associations are exactly `[{"Fn::GetAtt":
[<the one CloudFront::Function>, "FunctionARN"]}]`, resolved from the template rather than
hardcoded, so a renamed construct does not silently pass.

**Why the pre-existing test was not enough**, and it is worth stating precisely: it reads the
function's *source* for three substrings. Detaching an association does not change the
function's source. The old test passes on a fully detached function — the site would be open
to the internet with 18 green tests.

**Mutation gate — both mutations run, both caught, each by exactly the right test:**

| mutation | result |
|---|---|
| delete `function_associations=fn_association` from the default behaviour (`stack.py:239`) | **red** — `…attached_to_the_site_itself` fails, 19 others pass |
| delete it from the `/api/*` behaviour (`stack.py:267`) | **red** — `…attached_to_the_api_behaviour_too` fails, 19 others pass |

**"19 others pass" is the point, not an aside.** It reproduces the review's finding exactly:
before these two tests, this mutation was invisible to the entire suite.

`stack.py` verified byte-identical to `HEAD` after reverting both mutations (`git diff --stat`
empty), so no mutation residue reached the commit.

**Suite: infra 18 → 20, green.**

### `RMD-2` — `QUA-1`/`FRO-5`/`ARC-3`, rank 5: the function is now tested by running it

Found independently by three reviewers. The one existing test asserts three substrings appear
in the function's source, so inverting the gate passed all 18 tests.

**New file `infra/tests/test_viewer_function.py`, 7 tests.** The function is JavaScript and
the suite is pytest, so the tests **run it under node** — already a hard dependency of this
package, since CDK synthesises through it. A machine that cannot run these cannot run any
infra test, so the fixture **fails rather than skips** when node is absent: a silent skip is
the same vacuity this file exists to remove.

**Two design choices carry most of the value, and both are deliberate:**

1. **The code comes from the synthesised template, not from `viewer_function.js` on disk.**
   The password is substituted at synth time, and *"synth-time credential substitution
   silently no-ops"* was one of the review's green mutations. Reading the source file would
   not exercise it.
2. **The expected credential is hardcoded** (`Basic YXJ0aXN0cGF0aDp0ZXN0LXBhc3N3b3Jk`), not
   recomputed from `DeployInputs`. Deriving it the way `stack.py` derives it would move in
   lockstep with a mutation to `stack.py` and stay green — precisely what makes a test
   vacuous.

**Coverage:** refusal with no password and with a wrong one; **admission with the right one**
(the half a "does it 401?" test cannot see — without it, a function that refuses *everyone*
passes); `www-authenticate` present so the browser actually prompts; and three `TR-5` rewrite
cases — a shared journey link reaches `/index.html`, an `/api/*` call is not rewritten, a
hashed asset is not rewritten.

**Mutation gate — three run, three caught:**

| mutation | result |
|---|---|
| invert the password comparison (`viewer_function.js:24`) | **red**, 5 tests fail |
| make the synth-time `.replace()` a no-op (`stack.py:208`) | **red**, all 7 error on the placeholder guard |
| drop the `/api/` guard from the rewrite (`viewer_function.js:42`) | **red**, `…api_call_is_not_rewritten` fails |

**The second one is worth reading twice.** Under it, the *old* substring test still passed —
`authorization`, `/index.html` and `401` are all still in a function body that compares
against the literal placeholder `__EXPECTED_AUTH__`, which no browser will ever send. The
deployed site would refuse everybody, and the suite would have been green.

`infra/src/` verified byte-identical to `HEAD` after all three reverts.

**Suite: infra 20 → 27, green.**

### `RMD-3` — `QUA-3`, rank 6: the middleware is tested on every gated route

`api/tests/test_origin_secret.py` exercised **one** endpoint, and the review's mutations
exploited exactly that: narrowing the middleware to GET-only passed 185 tests while leaving
`POST /api/path` — the expensive Dijkstra — ungated.

**Change:** a `GATED_ROUTES` table (method, path, body, served-status) parametrising three
tests — refused without the header, refused with a wrong one, **served with the right one**.
The admitting case matters for the same reason it did in `RMD-2`: without it a middleware
that refuses everything passes, and the API would be dead behind a gate that "works".

Routes covered: `GET /api/artists/search`, `POST /api/path`, `GET /api/artists/{mbid}/track`.
That is every route `app.py` defines except `/health`, whose exemption is asserted separately
and in both directions.

**Mutation gate — three run, three caught:**

| mutation | result |
|---|---|
| narrow the middleware to GET-only | **red** — both `POST /api/path` cases fail |
| exempt `/track` | **red** — both `/track` cases fail |
| delete the `/health` exemption | **red** — the exemption test fails |

The third goes red for the **opposite** reason to the others: `/health` must stay exempt
(must-not-revert #2), because App Runner's health checker reaches the origin directly and
cannot be given the header. Gating it fails every deploy and rolls it back.

**Suite: api 185 → 192, green.**

### `RMD-4` — `SEC-1`: the origin secret is compared as bytes

`hmac.compare_digest` raises `TypeError` on a non-ASCII `str`, so one byte >127 in
`x-origin-secret` returned **500** and wrote a traceback into the telemetry log group —
unauthenticated and remote. It fails closed, so it was never a bypass; it is a log-writing
primitive.

**Fix:** `app.py` now encodes both sides and compares bytes. Starlette decodes header values
as latin-1, so encoding back with latin-1 round-trips the exact bytes from the wire. **The
`hmac` call stays** — `QUA-13` records constant-time comparison as a permanent review-only
invariant, and must-not-revert #7 says comparing bytes is the fix rather than a
simplification of it.

**The test needed a new harness.** The handoff records that `TestClient` cannot reproduce
this: httpx rejects the non-ASCII header client-side with `UnicodeEncodeError` before the app
is reached. `_raw_asgi_status()` builds the ASGI scope directly and drives the app, which is
what a real request does.

**A bypassing harness needs its own control**, so there is a second test asserting the raw
path agrees with `TestClient` on all four cases both can express (no header, wrong header,
right header, `/health`). Without it, a 403 from the harness would prove nothing about the
app.

**Mutation gate:** reverting to `str` comparison → **red**, with the exact error the handoff
predicted: `TypeError: comparing strings with non-ASCII characters is not supported`.

**Suite: api 192 → 194, green.**

### Snyk — clean on what changed, two pre-existing lows recorded

`api/src/artistpath_api`: **0 issues.** `infra`: **2 low, both pre-existing**, neither in code
this work introduced. Recorded rather than fixed, because expanding scope mid-stage is how a
plan stops being the plan:

| issue | where | condition to close |
|---|---|---|
| Hardcoded non-cryptographic secret (`CWE-547`) | `infra/tests/test_stack.py:18` — the `DEPLOY` fixture's constants | Judged a false positive: these are synth-time test constants, and `test_viewer_function.py`'s hardcoded credential is deliberate and documented. Closes if a real credential ever enters a test file |
| Path traversal (`CWE-23`) | `infra/app.py:18` — `ARTISTPATH_DEPLOY_SIDECAR` flows into `pathlib.Path` | Operator-controlled at deploy time on the operator's own machine, so not attacker-reachable. **Fold into `RMD-9`**, which already opens `infra/app.py` for `ARC-7`'s graph-key/sidecar coupling |

### `RMD-5` — the cheap gaps closed, and the mutation set re-run

**Four vacuous assertions strengthened in place** rather than supplemented, because a
near-duplicate beside a weak test leaves the weak one to be trusted later:

- **`QUA-6`** — the versioning test used `has_resource_properties`, which passes if **any**
  bucket matches, so moving versioning to the SPA bucket passed. Both buckets are now named
  via a logical-id-prefix helper, and the SPA bucket is asserted **not** versioned. A second
  test asserts `RETAIN` on the artifact bucket, clip table and image repository, and `Delete`
  on the SPA bucket — the deliberate exception, since it is rebuilt by `s3 sync` every deploy.
- **`QUA-7`** — asserting `Threshold == 25.0` while `DEPLOY` carries `25.0` passes when the
  stack hardcodes it. `template()` now takes overrides, and the test synthesises a second time
  at `99.0`.
- **`QUA-8`** — the table name is asserted. **`ARC-5` is not closed by this**: the literal
  still exists twice, here and in `config.py`, and `infra/` cannot import `api/`. The comment
  says so and points at `RMD-9`.
- **`QUA-9`** — port asserted, and the image tag asserted to **move with its input**, same
  technique as `QUA-7`.

**Then the whole mutation set re-run**, via a harness that applies one mutation, runs that
package's suite, and restores the file in a `finally` — so a crash cannot leave the tree
mutated.

**16 mutations, 0 missed.** Twelve the review recorded as green are now red; four it recorded
as caught are still caught.

| | result |
|---|---|
| the 12 previously-green mutations | **all RED** |
| 4 controls the review recorded as caught | **all still RED** |

**Why controls were included at all:** a suite change can *lose* a property while gaining
others, and nothing else would notice. Re-running only the failures would have measured the
fix without measuring the damage.

> **`QUA-4`'s cousin: §1's own arithmetic does not reconcile, and this is recorded rather
> than papered over.** §1 says *nineteen mutations, ten passed undetected*. Its table lists 10
> rows marked *no* — but one of those rows is three middleware variants, so the rows describe
> **12** undetected mutations, not ten. And 12 undetected plus 5 marked caught is **17**, not
> the stated nineteen: two mutations are not in the table at all. The re-run covers everything
> the table lists, minus one control (*`authorization` added to the origin-request allow-list*)
> which CDK's synth raises on — framework-enforced, so there is no suite behaviour to measure.
> **The two unlisted mutations cannot be re-run, because nothing records what they were.**
> That is a real gap in the review's record and it belongs to whoever reconciles it; this log
> does not invent a number for them.

**Stage 1 gate — met.**

| suite | result |
|---|---|
| builder | 115 passed |
| api | 194 passed (was 185) |
| infra | 30 passed (was 18) |
| frontend unit | 78 passed |
| frontend `npm run build` (incl. `tsc`) | green |
| mutation set | 16/16 caught |

**`npm run test:e2e` was NOT run.** It requires the API listening on `:8000` and nothing in
this stage touched the frontend. Recorded as not-run rather than reported as passing —
`DEP-30` makes it mandatory *per deploy*, and stage 1 does not deploy.

**Working tree checked after the harness: no source residue.** The only modified file was
`infra/tests/test_stack.py`, the intended change.

---

## Stage 2 — deploy safety

### `RMD-6` — the CORS guarantee moved to where absence is safe

**Fixed in source. NOT yet closed in production** — see the gate below.

- **`config.py`** — `cors_origins` now defaults to **empty**, not `http://localhost:5173`.
  Safe because dev is same-origin too: `frontend/vite.config.ts:21-23` proxies `/api` → `:8000`,
  so the browser only ever talks to the Vite origin and no CORS header is involved either way.
  The old default was never needed.
- **`api/tests/test_cors.py`** rewritten. It asserted the dev default, so it had to change —
  it now asserts the default allows **nothing**, plus an admitting case (an explicit origin
  works) and the negative control.
- **`stack.py` and `test_stack.py:108`** keep setting and asserting the empty value, with
  comments demoting it from *the guarantee* to *a statement of intent*. Deleting either would
  lose the record of why.
- **`infra/README.md`** — `detect-stack-drift` added to §7's manual gates, with the two
  always-drifted rows (`Cpu`, `Memory` unit normalisation) named so a real third difference
  stands out.
- **The record corrected in both places that carried the reversed claim**: Track B's execution
  log §4 claim 1 and the handoff's must-not-revert list. Original wording preserved in both,
  annotated rather than rewritten — a frozen document's value is that it is frozen.

**Mutation gate:** restoring the old default → **red** (`test_the_default_config_allows_no_origin_at_all`).

### `RMD-7` — `ARC-1`, rank 2: the storage stage now refuses by default

The guard was a sentence in a README, and §2 is the first deploy command an operator meets —
so the destructive path was also the most reachable one.

**New module `deploy_stage.py` with a pure function**, `resolve_include_service(stage,
confirm)`. It is separate from `app.py` for one reason: `app.py` does its work at import time
and calls `app.synth()`, so nothing in it is testable — which is `QUA-10`, and why `TKB-7`'s
protection rode on an unverified context string. Two strings in, one bool out, testable
without CDK or AWS.

`-c stage=storage` now raises unless `-c confirm-new-stack=true` is also given. **The guard is
a flag rather than an AWS lookup deliberately:** synth must stay offline (the whole infra
suite runs with no credentials), and a check that only works when configured is not a guard.

**5 unit tests**, including that an unrecognised stage token fails toward the *safe* answer —
a typo must not silently drop the distribution.

**Verified through the real entrypoint, not only the unit:**

| invocation | result |
|---|---|
| no stage flag | exit 0 |
| `stage=storage`, unconfirmed | **exit 1**, refusal naming the distribution and the flag |
| `stage=storage`, confirmed | exit 0 |

Runbook §2 now opens with a skip-this-section warning and the check command; it also carries
`ARC-1`'s correction to `TKB-7`'s stated mechanism (ECR is `Retain`, so a rollback **orphans
fixed-name resources** rather than deleting the repository — the staging is right, the old
explanation was not).

### `RMD-8` — `ARC-2`, rank 7: log retention set, live

Design §5 specified 90 days; never implemented, in no tracking document. **Applied to the
live groups**, not merely documented:

| log group | before | after |
|---|---|---|
| `/aws/apprunner/artistpath-api/…/application` | Never Expire | **90** |
| `/aws/apprunner/artistpath-api/…/service` | Never Expire | **90** |

**Left at Never Expire, deliberately:** the two `apprunner-availability-probe` groups
(`TKB-8`'s only trace, empty and will never grow — the probe is gone) and the CDK
auto-delete Lambda group (writes only on stack deletion). Recorded so the next reader knows
it was a decision.

Runbook gains **§5a as a numbered step**, not a note — CDK cannot create these groups, and the
names contain the service id, so **recreating the service silently resets retention to Never
Expire**. Carries the `MSYS_NO_PATHCONV=1` trap.

### `RMD-9` — `ARC-5` closed properly; `ARC-4` made recoverable

**`ARC-5`:** the service is now passed `ARTISTPATH_CLIP_TABLE`, read off the construct, so it
renders as `{"Ref": "ClipTableED47A9EE"}` — CloudFormation resolves it from the table itself
and the two **cannot** diverge, even in principle. `config.py` already read that variable; it
was simply never sent. The test asserts the `Ref`, not a copied literal.

This is what closes the gap the table-name test cannot: `infra/` cannot import `api/`, so no
infra test can see `config.py`'s default. What it can do is stop the API needing that default.

**`ARC-4`:** full de-hardcoding is a migration, not a cleanup — renaming a live table and
repository is not something this plan deploys. **Runbook §10 added** so the failure is
recoverable rather than merely surprising: what survives a stack delete, in what order to
check, and which resource must *never* be deleted to clear a name conflict (the artifact
bucket — `TR-9`'s only second copy of the adopted graph). It names the real fix and says why
it was not taken.

### `RMD-10` — `SEC-5`: a scaling ceiling

`AutoScalingConfiguration` with `MaxSize: 2`, and the service wired to it. Without it the
account default of 25 applies, and the origin secret rejects requests *inside* the container —
after App Runner has counted and scaled on them. `DEP-17`'s claim that the gate bounds the
bill is true through CloudFront and **false at the API origin**, the same shape `TR-7`
corrected once.

**2 is a cost ceiling, not a capacity estimate.** The test asserts both the value **and** that
the service references it — a configuration nothing points at bounds nothing, which is `QUA-2`'s
detached-resource shape again.

### `ARC-6` — found live by the seam gate, and it was not on the plan

**The stage-2 gate is "`cdk diff` shows only the intended changes", and the first run showed a
fourth:** `ImageIdentifier` changing from **the deployed commit tag** (Track B log §1) to
**`:latest`**.

`infra/app.py` defaulted `image_tag` to `latest`, and `infra/.env.deploy` does not set the
variable — so **the next `cdk deploy` would have silently repointed the live service at a
floating tag**, contradicting the runbook's own rule that with no CI the tag is the only
record of what is running. `ARC-6` sits in review §4 as a *cheap, non-blocking* fix; the diff
showed it was one command away from being a live incident.

**Now required** — a synth without it refuses, naming the variable (verified). Runbook §1
updated, including that `.env.deploy` deliberately does **not** carry the tag: it is
per-deploy, not per-machine, and persisting it is how you deploy the wrong commit.

**This is the argument for the gate being a diff rather than a test.** No test in any package
compares the synthesised template against what is actually deployed.

### Stage 2 gate

| check | result |
|---|---|
| builder | 115 passed |
| api | 195 passed |
| infra | 30 → **37** passed |
| frontend unit + build | 78 passed, build green |
| `cdk diff` vs deployed | **only the three intended changes** (autoscaling resource, its ARN on the service, `ARTISTPATH_CLIP_TABLE`) |
| Snyk `api` | 0 issues |
| Snyk `infra` | same 2 pre-existing lows, **no new** |

> **⚠ `RMD-6` is FIXED-NOT-CLOSED, and drift is still DRIFTED. Both are expected and neither
> is done.**
>
> Nothing in stage 2 was deployed. The running service is still on the image tag recorded in
> Track B's log §1, built before
> the `config.py` change, so **the live API still answers a live probe with
> `access-control-allow-origin: http://localhost:5173`** — re-measured after the source fix,
> not assumed. Drift still reports the same three differences on `ApiService` for the same
> reason.
>
> **`RMD-6`'s own done-condition, written in the plan before any of this, was "after
> redeploy".** So this is the plan working, not a surprise — but the defect is live until a
> deploy happens, and a deploy is Track C's step and the owner's call.
>
> The `ARTISTPATH_DEPLOY_IMAGE_TAG` fix means that deploy will now **stop** unless the operator
> names the commit, which is the correct behaviour and a change to the deploy procedure.

---

## Closeout, 2026-07-27

### A4 — the default-flip check, and it has a finding

Five knobs moved. Four are closed; **one is the exact shape A4 exists to catch.**

| knob | old | new | closed? |
|---|---|---|---|
| `ApiConfig.cors_origins` default | `http://localhost:5173` | `""` | **NO — see below** |
| `ARTISTPATH_DEPLOY_IMAGE_TAG` default | `"latest"` | *(required)* | yes — the losing default is deleted, not left selectable |
| `confirm-new-stack` context flag | *(did not exist)* | absence ⇒ refuse | yes — no default to leave stale |
| `ARTISTPATH_CLIP_TABLE` on the service | *(not sent)* | sent as a CFN `Ref` | yes |
| App Runner `MaxSize` | account default (25) | 2 | yes |

> **`cors_origins` is flipped in source and NOT in the running application.** A4's own words:
> *a knob sitting at its old default is unshipped work wearing a completion badge*. The
> deployed service runs an image built before the change, and a live probe re-run at closeout
> still returns the old behaviour. **This work is therefore not closed**, and saying so
> plainly is what A4 asks for instead of marking it complete.
>
> It closes on the next deploy, which is Track C's step.

### A3 — every open item has an address

| item | condition to close |
|---|---|
| **`RMD-6` (CORS) — fixed-not-closed** | A live probe of the origin's `/health` with `Origin: http://localhost:5173` returns **no** `access-control-allow-origin` header. Requires a redeploy; Track C |
| **Stack drift** | Re-run `detect-stack-drift` after that deploy: only the `Cpu`/`Memory` normalisation rows should remain |
| **`RMD-11`, `RMD-12`** (stage 3) | Planned, not started. See the plan |
| **`RMD-13` / `FRO-4`** | Cannot complete before Track C: the SPA bucket is empty, so every path 403s whether the rewrite works or not. The runbook step lands first, executes at cutover |
| **`ARC-4`** — made recoverable, not fixed | Closes when the fixed physical names (`artistpath-api` ×3, `artistpath-clips`) are dropped in favour of generated ones. **That is a migration against live resources, not a cleanup** — so it closes at a moment when recreating the table and repository is acceptable, or never, as an accepted risk with runbook §10 as the mitigation |
| **Snyk `CWE-547`** (`infra/tests/test_stack.py:18`) | Judged a false positive — synth-time test constants. Closes if a real credential ever enters a test file |
| **Snyk `CWE-23`** (`infra/app.py`, sidecar path) | Operator-controlled at deploy time on the operator's own machine. Closes with a least-privilege pass on `infra/app.py`, or **accepted, won't fix** if `ARC-7` is closed some other way |
| **`DEP-16`** telemetry round-trip | Unchanged by this work; still owed. Real logged data now exists to do it with |
| **`DEP-17`** cost | Alarm confirmed working 2026-07-27, but its figure covers only hours of runtime. Closes on a month of billing (`DEP-31`) |
| **The two unlisted mutations** in review §1 | Cannot be re-run — nothing records what they were. Closes only if whoever ran the review reconstructs them |

**Nothing above has come due.** `RMD-6`'s and the drift item's conditions both point at the
same deploy.

### B2 — reachability

One new module, `deploy_stage.py`. Imported by `infra/app.py:16` and called at `:52`, with
its own test file. **Not an orphan.** No other module was created.

### B3 — vacuous-test spot check

**Discharged by the mutation work itself, at more depth than B3 asks for.** 16 mutations
against the invariants that matter, every one confirmed red, with the four already-held
properties re-run as controls. See `RMD-5`.

### B5 — stale-description sweep

**Found one violation, and it was this log's own.** Four restatements of deployed identity —
account, region, distribution id, image tag — which Track B's execution log §1 owns and whose
handoff explicitly says not to restate elsewhere. **Converted to citations.**

Worth recording because it is the drift the one-document rule exists to prevent, and it was
committed by the session that had just written a plan citing that rule. Restating a *currently
correct* figure is still a violation; the image tag in particular would have gone stale at the
next deploy, in a document claiming to describe what is deployed.

Also checked and clean: no test counts restated in `infra/README.md` (`QUA-4`'s fix holds), no
secrets or live URLs added to it.

### B4 — prose-versus-code, and it caught a figure this work invalidated

`deploy_stage.py`'s docstring and `infra/README.md` §2 both said the storage stage deletes
**eight** resources, taken from review §2. **Measured: nine.**

**The review's figure was correct when written, and `RMD-10` invalidated it** by adding an
autoscaling configuration to the service half — in the same session, four tasks earlier. This
is the failure class `CLAUDE.md` names: a change removes a property something unrelated had
silently come to depend on, nothing breaks, no test fails.

**Fixed by deriving rather than restating.** `test_deploy_stage.py` now computes the deleted
set from the two synthesised templates and asserts its **membership** — distribution, service
and viewer function in; every stateful resource out. Adding a service-side resource now updates
the check instead of quietly invalidating prose. Both documents say nine and point at the test.

Other prose checked against code and found accurate: the Vite proxy claim in `config.py`'s
comment (`vite.config.ts:21-23`), `node` being a hard CDK dependency, the hardcoded test
credential's base64, and `app.py` doing its work at import time.

### B1 — documentation audit

Dispatched `doc-auditor`. **Two HIGH findings, both fixed here** — both were adjudicable from
the record, so neither belongs on an escalation list:

1. **`docs/README.md` did not list the two new documents.** They declared their own roles
   correctly but were unreachable from the authoritative map. **Added**, along with the new
   handoff, and the Track B handoff row is now marked superseded-on-next-actions with its
   reversed claim flagged.
2. **`docs/superpowers/NEXT.md` was stale** — it still told the next session to execute the ten
   blockers as its first work. **Rewritten**: stages 1–2 done, stage 3 next, the live `RMD-6`
   exposure called out, and the gate-state row corrected.

The second is the higher-value catch and it is a repeat of a named incident: on 2026-07-26 an
audit found this same row stale, the session had the facts, escalated on authority grounds, and
**the row stayed wrong**. `closeout` B1 was amended after that to say a finding you have the
facts to fix is yours to fix. Fixed here rather than escalated.

The audit confirmed clean: no restated figures, `RMD-` disjoint from every existing series, the
CORS reversal correctly annotated in both places, and prior audit findings actioned.

### D6 — the standing context layer

| layer | measurement | delta |
|---|---|---|
| Unconditional (`CLAUDE.md` + `MEMORY.md` + skill/agent `description:` lines) | **42,778 characters** | **0** |
| Conditional (`SKILL.md` bodies, agent bodies, `memory/*.md` bodies) | **1,971 lines** | **0** |

**This work touched neither layer** — `git diff main...HEAD -- CLAUDE.md .claude/` is empty and
nothing was written to `memory/`. No case to make, because nothing was added.

### D4 — suites

builder **115**, api **195**, infra **38**, frontend **78**, `npm run build` green. Run, not
recalled.

`npm run test:e2e` **not run**: it needs the API on `:8000`, and nothing in either stage touched
the frontend. `DEP-30` makes it mandatory per *deploy*, and nothing was deployed.

### A5 — processes

**No listeners on `:8000` or `:5173`.** Nothing was started by this work and nothing was left
running. Swept by port rather than by task list, since a session sees only its own tasks.

### D2, D3 — not applicable, stated rather than skipped

**D2 (fixtures):** the graph was not touched. No rebuild, no adoption, no artifact comparison —
`pathfinding.py` was never opened and the committed 500-node fixtures are unaffected.

**D3 (provenance):** no artifact was adopted or compared, so there is no new checksum to
record. The identity of what is deployed — graph key, sha256, image tag — is owned by Track B's
execution log §1 and is **cited from here, never restated** (see `B5` above, where restating it
was this log's own defect).

---

## Stage 3 — the first user

**The closeout section above covers stages 1–2 only.** Stage 3 ran in a later session, after
PR #30 merged; this section is appended rather than interleaved so nothing already committed
moves. Branch `gate2-dep33-stage3`.

### `RMD-11` — `FRO-2`, rank 3: nobody was told the username

The 401 now carries a body naming the username. It is substituted at synth time from
`stack.py`'s new **`SITE_USERNAME`** constant — the same constant the admitted credential is
built from — so the page cannot name a username the gate would reject. Naming it discloses
nothing: this is a shared password, not authentication, and the function's own comment has
always said so.

`infra/README.md` §1 now states what to send a new visitor: **URL and password only**, because
the page they hit tells them the username.

**The mutation gate found two weak assertions before they landed, and both were mine.** This is
the argument for running it on your own new tests rather than only on the ones under repair:

| what the assertion was | why it passed the mutation that serves the whole credential |
|---|---|
| `password not in response` | It checks the **plaintext**. Basic auth is base64, not encryption, so a body leaking `Basic YXJ0...` hands over a working credential while containing no plaintext password at all. |
| `username in body` | Satisfied by the page's own `<h1>artistpath</h1>` — the site's **name** passing a check meant for an **instruction**. |

Both were tightened: the username is asserted as marked-up text, and the password check covers
the encoded form and runs against the whole response rather than the body.

**Mutations after the fix — 2, both CAUGHT:** the body serving the credential; the username
substitution silently no-opping (caught by a fixture guard mirroring the existing
`__EXPECTED_AUTH__` one).

### `RMD-12` — `FRO-1` / `FRO-7`, rank 4: the blank page after a redeploy

**Runbook half.** §6 was one `aws s3 sync --delete`. It is now three passes: hashed assets with
a one-year immutable `Cache-Control` and **no `--delete`**, then `index.html` **last** with
`no-cache`, then the invalidation.

**The `--delete` split is an extension of what the plan specified, not something it called
for.** The plan named the cache headers and the ordering. But deleting the previous build's
assets while the previous `index.html` is still live re-opens the identical window for anyone
mid-visit — so the prune is now a separate, later, optional step, with its cost stated (a few
kilobytes of orphans) against the cost of running it early (a blank page). **The cutover deploy
is exempt and says so:** the bucket is empty, so there are no returning visitors to protect.

The machine-state caveat from the stages 1–2 handoff — `aws s3 sync`'s content-type guessing was
verified on *this* machine and is not a repo property — is now **in the runbook** rather than in
a handoff that expires.

**Application half (`FRO-7`).** `frontend/index.html` carries static fallback markup inside
`<div id="root">`. **Verified to survive `vite build` by reading `dist/index.html`**, not
assumed — and the first attempt to verify it read a *stale* `dist/` from before the change,
because `tsc -b && vite build` had failed at the `tsc` step and the build never ran. The
apparent finding, "Vite strips the fallback", was an artifact of reading output that no build
had produced.

**Two design points, both of which a test now holds:**

- **It must live inside `#root`.** React clears the container it owns, so there it disappears on
  mount; placed *beside* `#root` it would be correct on the way in and then sit under the app
  forever. The failure mode is not "the fallback is missing" — it is "the fallback never leaves".
- **The test reads `index.html` through Vite's `?raw`, not `node:fs`.** The first draft broke
  `npm run build`: `tsconfig.app.json` gives `src/` no node types, and adding them so one test
  compiles would let **any** app module import node builtins and still typecheck. `vite/client`
  already declares `?raw`.

**Three tests, all shown red first. Mutation — the fallback moved to a sibling of `#root` —
CAUGHT by all three.** The e2e spec exists because *every other e2e spec passes with the
fallback still on the page*: they look for app elements, and leftover text does not stop those
existing. Its assertion order is deliberate and is itself a finding — the fallback and the
landing page share a heading, so asserting the heading first fails on a Playwright strict-mode
violation, a real detection whose message says nothing about what broke.

### `RMD-13` — `FRO-4`, rank 10: prove the gate admits

**The step is written and cannot complete before Track C**, exactly as the plan anticipated.
`infra/README.md` **§8a**, marked with an hourglass and carrying the reason running it early is
worthless: the bucket is empty, so every path 403s whether the rewrite works or not.

Two halves, and the split is the point:

- **Mechanical (curl):** the gate admits at all; a shared `/path/<mbid>/<mbid>` link returns the
  SPA entry point rather than a 403 (`TR-5` against the real distribution); `/api/*` works end
  to end through CloudFront.
- **Browser, and curl *structurally* cannot do it:** whether the browser re-attaches cached
  basic credentials to the SPA's same-origin `fetch()` calls. `curl -u` re-sends the credential
  explicitly on every request, which is precisely the behaviour in question. The whole app
  depends on this and no browser has ever exercised it.

§8a is also **the trigger the deferred phone section in `TEST-QUEUE.md` has been waiting on
since 2026-07-26**, and it names the in-app-browser risk (WhatsApp, Instagram) as a risk to work
around rather than a defect to fix at Gate 2.

### Stage 3 gate

| check | result |
|---|---|
| builder | **115 passed** |
| api | **195 passed** |
| infra | **41 passed** (38 before this stage) |
| frontend unit | **80 passed** (78 before) |
| `npm run build` | green — and it is what caught the tsconfig defect |
| `npm run test:e2e` | **5 passed** (4 before). Run against the adopted artifact, sha256 `4cb84ef9…`, matched to its sidecar before the run |
| `snyk_code_scan`, infra + frontend | frontend **0**; infra **2 lows, both pre-existing** — `test_stack.py:18` and `app.py:19`, neither in code this stage introduced. Their closing conditions in `A3` are unchanged. |

**No listeners left on `:8000` or `:5173`.** The API was started for the e2e run and stopped;
swept by port afterwards, not by task list.

**Nothing was deployed.** `RMD-6` remains fixed-in-source and live in production. The owner
accepted that exposure on 2026-07-27 rather than deploy twice — the decision the stages 1–2
handoff put to him, resolved in favour of waiting for Track C.
