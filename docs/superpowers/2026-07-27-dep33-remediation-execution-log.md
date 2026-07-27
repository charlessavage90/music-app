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
questions and found one new defect. **Account `826731842184` / `us-east-1`, confirmed via
`sts get-caller-identity` before anything was read** — the identity check the execution log's
§1 makes load-bearing.

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
not a measurement*. Distribution `E1S07XVIOW6A22`, read-only:

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
