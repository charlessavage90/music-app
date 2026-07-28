# Execution log — removing the password, 2026-07-28

**Role: ACTIVE — the retained execution log for
[`plans/2026-07-28-password-removal-load-hardening.md`](plans/2026-07-28-password-removal-load-hardening.md).**
Appended per task, not at closeout. Where this log and `NEXT.md` disagree about status, **this
log is fresher and wins** — fix `NEXT.md` rather than working around it.

**Scope: Track A only (PW-1 → PW-4).** Track B has not started. **The password is still on.**

---

## What this is for, in one line

The shared password is doing three jobs — access control, rate limiting, and throttling the clip
fan-out to Deezer/iTunes. Track A replaces the third and part of the second inside the API.
Track B replaces the rest at a Cloudflare front door and then removes the password.

## Scope decision, and it is the owner's

He asked for **the minimum set of load-related findings that would allow removing the password**,
explicitly **not** Gate 3. The set was derived from the Gate 2→3 review and agreed before any
code: `G3-A2`, `G3-A1`, `G3-A3`, `G3-A4`/`G3-S2`, `G3-S3`, `G3-S4`, `G3-S7`.

Two review findings were argued *out* of scope and both readings survived:

- **`G3-A3` (the knob that caps the bill is the knob that caps capacity) does not fire**, because
  the capacity problem is being met by shedding load at the edge rather than by scaling.
  `max_size=2` stays exactly as it is. **A future session raising it deletes the only automatic
  spend control.**
- **`G3-A1`'s capacity half is deferred, not closed.** Cloudflare's per-IP limit stops one person
  with a loop; it cannot help with a dozen legitimate friends, because each is a different IP
  behaving reasonably. At ~1.5 path req/s that is enough to saturate the server. Deferred with a
  condition in the plan.

The owner supplied two inputs that changed the design: he already runs **Cloudflare free tier**
with a domain he owns, which replaces the AWS WAF the review assumed at zero cost; and he
confirmed **`musicapp.cmiller.io` is permanent**, which closes `G3-A5` as a side effect rather
than deferring it. He deferred the iPhone check (`G3-F2`) to a friend after this ships.

---

## PW-1 — bound the request surface (`G3-S3`, `G3-S4` amplification half) ✅

Commit `5221f90`.

**Decision: these are one task, not two.** The 20 MB of CloudWatch the review measured came from
unbounded id strings being echoed verbatim into the telemetry line at `app.py:130`. Bounding the
strings closes both findings; treating them separately would have produced two half-fixes.

**Finding — a vacuous test, caught by the red step.** The first version of
`test_an_oversized_sources_array_is_rejected_by_the_schema` **passed before the fix existed**.
`build_path` already raises 422 for "alpha supports exactly two source artists" — but it raises it
*after* the whole array has been parsed and materialised, which is the entire finding. Asserting
`status_code == 422` cannot tell the two apart.

Rewritten to assert the rejection came from the **schema**: FastAPI returns a *list* of pydantic
errors for a schema violation and a *string* for `HTTPException`'s message. **This is the second
time this session's red step has earned its keep** — see PW-4.

**Decisions taken:**
- `_MBID_MAX = 64`, not 36. An id that is merely *unknown* should reach the handler and get a
  readable 404, not become a schema error.
- `sources` bounded at 8, not 2, so the handler's readable "exactly two" 422 stays reachable for
  the realistic mistake.
- `reason` bounded but **deliberately not a `Literal`**. `test_an_unrecognised_reason_is_still_coerced_to_dislike`
  already pins the fallback-to-dislike behaviour, and tightening it is a behaviour change this
  task was not making.
- The body guard reads **Content-Length only**. Chunked bodies stay bounded by the schema alone —
  deferred, conditioned on CloudFront and Cloudflare both sending the header.

## PW-2 — `/health` off the thread pool (`G3-A1`'s feedback loop) ✅

Commit `5b1dcfd`.

**This is the derivation the review missed, and it is one keyword.** `/health` was a sync `def`,
so FastAPI ran it in Starlette's thread pool — the *same* pool as `build_path`. That is why it
measured 22.09 s at 40 concurrent: **not CPU starvation, queueing.** App Runner's health check
times out at 5 s with an unhealthy threshold of 5, so the origin was replacing instances under
load and shifting that load onto the other one, which failed identically. The site did not
degrade; it cycled.

**It does not make the app faster.** It stops slow becoming an outage. Recorded here because a
one-word change reads as trivial and a future session may drop it.

`search_artists` and `build_path` **must stay sync** — they do real work and would block the
event loop. Only `/health` qualifies: three in-memory attribute reads, no I/O.

Two tests, because the regression is a keyword: an introspection test that catches `async def`
reverted to `def`, and a behavioural one that saturates the pool. **The behavioural one genuinely
times out without the fix**, so it is not vacuous.

## PW-3 — a throttled catalogue is not a missing track (`G3-A4`, `G3-S2`) ✅

Commit `7d7216d`.

**Design decision: the classification lives in the injected fetcher, not in `clips.py`.** That
module's existing broad `except` carries a comment explaining it must not name httpx's exception
types. `build_default_app`'s `fetch_json` is the only place in the app that knows status codes, so
it raises `CatalogueUnavailable` on 429/5xx and `clips.py` owns a type without owning a transport.

**Falling through to a *different* catalogue is untouched** — that is the fallback working, not
amplification. Only repeat calls to the service already refusing us stop.

The three pre-existing outage tests pass unchanged, because they raise *generic* exceptions, which
are still swallowed as misses. That is the correct boundary and it was verified rather than
assumed.

## PW-4 — circuit-break a refusing catalogue (`G3-A4`, `G3-S2`) ✅

Commit `5738e0b`.

**A design error in the plan, caught by a test written before the implementation.** The plan reset
the failure count when the cooldown expired, with a comment asserting that *was* half-open
behaviour with one probe. **It is not.** A full reset admits a further `threshold` requests every
cooldown, so a permanently dead catalogue costs five calls a minute rather than one. The count now
stays at the threshold: the next real request is the probe, and one failure re-opens immediately.

**The two integration tests were written after the implementation**, so they were not trusted
green — verified by mutating `is_open` to always fall through, confirming both go red, and
reverting. Recorded because this project's rule is that a green result from a new instrument is
not evidence until it has been shown to go red.

**Per-process, unsynchronised, deliberately.** A breaker shared through DynamoDB would be a write
on every clip request, which is the load it exists to avoid. At `max_size=2` the worst case is
twice the configured rate.

`ClipResolver`'s `breaker` parameter is **optional**, so every existing call site kept working
without edit.

---

## Closeout findings — the ritual caught two things the work did not

**`A4` (default-flip) found an untested wiring path, and it is `G3-Q1`'s exact shape.**
`build_default_app` constructs `ClipResolver` with **no** breaker argument and relies on the
constructor default to arm one — while **every** breaker test injected one explicitly. A default
that stopped arming the breaker would have left the whole of PW-4 dead in production with every
test still green. That is the defect class the Gate 2→3 review named twice and the class this
project keeps producing.

Closed by `test_a_resolver_built_without_one_still_gets_a_breaker`, which exercises the *default*
path. Verified non-vacuous by mutation — raising the default threshold to 10⁹ produced 8 calls to
a refusing Deezer against an expected 5, and the test failed.

**`D1` (clean tree) was run too early and reported a false green.** The tree was clean when
checked, then the `A4` fix dirtied it, and nothing re-checked. Caught by the `B1` doc audit, which
found the resulting test-count contradiction between this log and the handoff. **The ordering
lesson is real: D1 belongs after Part B's fixes land, which is what the skill says and what this
closeout did not do.**

## State at the seam

**All four suites green**, run 2026-07-28 from `C:\dev\music-app`:

| builder | api | infra | frontend unit |
|---|---|---|---|
| 115 ✅ | **214 ✅** (was 195; +19) | 58 ✅ | 80 ✅ |

**This table owns the api count. Nothing else restates it** — `docs/README.md` and the handoff
cite it, because the three disagreed for exactly as long as it took the audit to notice.

Frontend e2e not run — it needs a hand-started API and nothing in Track A touches the frontend.

**Snyk Code on `api/`: one Low, pre-existing, not from this work.** A hardcoded credential in
`tests/test_origin_secret.py:47` — one of the three the Gate 2→3 review already triaged as
non-issues. Not fixed: a hardcoded credential in a test is deliberate here, for the reason
`test_viewer_function.py`'s docstring gives (a value derived the way the source derives it moves
in lockstep with a mutation and the test stays green).

**Nothing is running on any port. No graph was rebuilt, no artifact touched, no config default
flipped, no AWS or Cloudflare state changed. The live site is exactly as it was.**

## What a Track B session must not get wrong

- **The password is still on and must stay on until PW-7.** Every Track B step before it is
  additive and reversible on purpose: if the Cloudflare configuration is wrong, the existing gate
  is still protecting the site while it is found. **Do not reorder to remove it earlier.**
- **`max_size=2` must not be raised.** See the scope decision above.
- **PW-6 step 6 check 4 is not optional.** It confirms the Cloudflare secret header is actually
  arriving at the origin *while the password is still on*. PW-7 makes the site depend on that
  header; discovering it never arrives after the password is gone is the bad ordering.
- **The Cloudflare free-tier allowance was confirmed in the owner's dashboard on 2026-07-28**: 1
  rate limiting rule, 5 custom security rules, 3 page rules. The five custom rules are
  deliberately left unspent as headroom.
- **`G3-S7`'s fix is a swap, not a deletion.** The viewer function goes on refusing; it changes
  what it asks. That keeps the test coverage instead of deleting it, and it closes the bypass that
  would otherwise make the whole rate limit decorative — `d2n3xqz3pttguf.cloudfront.net` answers
  on its own and is already circulating in shared links. **`stack.py:147-153` records `TR-7`,
  which is this exact mistake one layer down.**
- **A Cloudflare "Cache Everything" rule inherited from another project would silently
  reintroduce `FRO-1`** (returning visitors served a stale `index.html` after a deploy). A
  CloudFront invalidation does not purge Cloudflare. PW-6 step 5 verifies this; the default is
  safe but must be checked, not assumed.

## Owed, and unchanged by this work

The OneDrive migration's **Task 9 → 10 → 11** state is untouched. Task 9 (confirm Backblaze
completed an upload covering `C:\dev`) still gates Task 11, and Task 11 is still the irreversible
deletion of the rollback tree.

---

# Track B — the front door, 2026-07-28

**Written by the session that executed it, appended per task.** Track A stopped at the plan's
named seam; Track B ran `PW-5` → `PW-8` in one session. **`PW-9` is unrun** and is gated on the
owner's approval, not on readiness.

**The title of this file now understates it.** It says "(Track A)". Both tracks are here.

## PW-5 — custom domain and certificate (`G3-A5`) ✅

Certificate `arn:aws:acm:us-east-1:826731842184:certificate/0f61db68-…` for
`musicapp.cmiller.io`, us-east-1, DNS-validated, **ISSUED**, `RenewalEligibility: ELIGIBLE`
once attached. Free.

**The plan's two tests were run RED first** and failed with the predicted `TypeError` on the
unexpected `DeployInputs` keyword.

**⚠ `PW-5` was deployed TWICE. The first attempt failed and rolled back.** The cause was not in
the plan — it was an addition the owner asked for mid-task: tag every resource `app=musicapp`
for cost attribution.

```
UPDATE_FAILED AWS::AppRunner::Service ApiService
"Service with the provided name already exists: artistpath-api."
```

**App Runner's `Tags` property is immutable**, so adding one forces a **replacement**; the
service carries an explicit `service_name`, and CloudFormation creates the replacement *before*
deleting the original. App Runner refuses the duplicate name. **This is a deadlock, not a
transient error — retrying cannot help.**

Nothing was damaged: the failure occurred **before** App Runner was touched, so there was no
outage, the original service stayed `RUNNING`, and the rollback was clean (checked for orphaned
autoscaling revisions — there were none; the concern was unfounded).

**Resolution:** both App Runner resources are excluded from CDK tagging via
`exclude_resource_types` and tagged **out of band** by CLI.
`test_app_runner_is_deliberately_left_untagged` asserts the **absence** and carries the reason,
because closing that "gap" looks obviously correct and re-breaks the deploy. Verified by
mutation: removing the exclusion makes it fail.

**Three measurement lessons, all of which changed what was reported:**

1. **`cdk diff`'s default change-set method does not report tag-only changes.** It showed 4
   resources changing; `--method=template` showed 12. It *does* report replacements accurately.
   **Read both** — one for blast radius, one for coverage.
2. **`cdk deploy … | tee` reports exit code 0 on failure**, because a pipeline's status is the
   last command's. The first failed deploy looked successful to anything checking `$?`. It was
   caught by reading the log. Every later deploy redirected to a file instead.
3. Tagging reaches **12** resources; the 9 it misses are bucket/IAM policies, CloudFront
   `OriginRequestPolicy` and `OriginAccessControl`, an SNS subscription and CDK's auto-delete
   helper — **none taggable in CloudFormation, none billable.**

## PW-6 — Cloudflare front door and rate limiting (`G3-A2`) ✅

Established **with the password still on**, which is the whole safety property of the ordering.

**⚠ The rate limit is `10 requests / 10 s`, block `10 s` — NOT the plan's `30 / 60 s`.** The
owner's Cloudflare plan offers **only** 10-second periods, for both window and block.

**It was deliberately NOT rescaled linearly to `5 / 10 s`.** A short window is burst-hostile,
and the plan chose the generous end because friends behind one NAT share an IP. Because the
block is also 10 s, `10 / 10 s` reproduces the plan's *sustained* ~0.5 req/s per IP while
restoring the burst allowance.

**The plan's `~1.9 s per request` figure was challenged and then CONFIRMED.** A first probe
measured ~0.1 s and the session reported the plan contradicted. **That was wrong** — it timed a
single cheap artist pair. The owner's CloudWatch summary (p90 **1916 ms** at bypass depth 0)
is the better evidence, and `duration_ms` measures `find_journey` alone (`app.py:130-132`), so
it is pure compute with no network.

**What actually drives latency is the artist PAIR, not bypass depth.** Measured: flat from 0 to
100 exclusions; but 68 ms (Arctic Monkeys → The Beatles) to 563 ms (Kraftwerk → Fela Kuti) across
pairs. **Consequence for the runbook:** the abuse test must use a *famous* pair, or sequential
requests never reach 10 per 10 s and the test silently proves nothing.

**Check 6.4 — and the plan aims it at the wrong leg.** The plan says to prove the front-door
header reaches **the origin**, suggesting the origin-request allow-list. It never can:
CloudFront forwards only `x-journey-id` and `content-type` to App Runner. **`PW-7` enforces the
header in the viewer function, at the edge**, so that is where it was verified — with a
**control**: through Cloudflare the probe reads `1`, straight to CloudFront it reads `0`. A probe
that always returned `1` would have passed the check exactly as the plan words it.

Instrumented via a temporary response header, **not `console.log`** — a CloudFront Function's
stdout is what the test harness parses as JSON, and logging broke 10 tests. The probe was removed
in `PW-7`, which rewrites that block anyway, so it cost no extra deploy.

**Gate 7b, and it cuts against the threshold.** The owner's browser run peaked at **6 path
requests per 10 s** against a predicted 1.7 — 3.5× the session's estimate. So one fast user is
fine; **two behind one IP would reach 12 and be blocked.** ⚠ The owner then qualified it: he was
*barely looking at the paths*, so **6 is an upper bound on an attentive user, not typical use.**
Recorded in `NEXT.md` as a deferral to re-derive before a public launch.

## PW-7 — the password is gone (`G3-S7`) ✅

**The gate was replaced, not deleted.** It now asks "did this arrive through Cloudflare?" That
keeps the SPA-fallback coverage and closes the bypass that would make `PW-6` decorative: the
generated CloudFront address answers on its own name and never touches the rate limit — **TR-7's
defect one layer up, and this project has already shipped it once.**

All five gates passed against production, plus **one negative test the plan does not call for**:
connecting straight to CloudFront while spoofing `Host: musicapp.cmiller.io` — the fail-closed
branch — returns **403**, does not loop, and does not leak the secret. That is the only route by
which the rate limit could have been evaded.

**Confirmed by the owner in a real browser, on a new device, in an incognito window** — which is
what rules out cached Basic-auth credentials, the confound that would make a still-protected site
look open.

`test_stack.py`'s substring assertion still described the password. It was updated rather than
deleted, with a comment saying why it is **not** the real test: `QUA-1` records that this exact
shape passed an **inverted** gate.

## PW-8 — runbook, retention, and the record ✅

- **Log retention verified against the live service: 90 days on both groups.** §5a had been run.
- **`infra/README.md` §8a renamed and rewritten** — it was "Prove the gate ADMITS" and described
  a password that no longer exists. **Kept, not deleted:** the property it protects is unchanged.
  **Every command in it was then executed verbatim** and returns exactly the documented result.
- §1's variable table, the username note, §8's expectation and §7's drift rows all corrected.

**⚠ A deferral the Track B handoff mis-read.** It said the `--prune` publish deferral came due at
`PW-5`'s deploy. **It did not.** `--prune` belongs to `sync_frontend.py`, the *frontend* publish;
`PW-5`–`PW-7` were infrastructure-only and never touched the SPA bucket, which still holds the
cutover's objects. Verified: `sync_frontend` appears in none of the four deploy logs. The
condition is now stated as **the next frontend publish**.

**Drift has two new permanent rows.** `detect-stack-drift` now reports `/Tags REMOVE` on both
`ApiService` and `ApiAutoScaling` — the latter had never appeared in drift detection at all.
**Measured, not predicted**, and recorded in §7; left alone the gate would have fired on every
future deploy, which is how a gate becomes one you skip.

## State at the end of Track B

| | |
|---|---|
| infra | **63 passed** |
| api | 214 passed |
| docs-lint | hard checks pass |
| Deployed | `ArtistpathStack`, image tag `37d559e` (unchanged — no API code shipped) |
| Live | `https://musicapp.cmiller.io`, **no password** |
| Certificate | ISSUED, in use, renewal ELIGIBLE |

**No application code changed in Track B.** No routing, no graph, no cost function, no clips.
Everything was infrastructure, the viewer function, and documentation.

## What a session picking this up must not get wrong

- **`PW-9` is the only unrun task**, and it is gated on the owner's approval.
- **Gate 3 is NOT open.** The password coming off is not Gate 3; the review's blocking set still
  gates it.
- **Do not raise `max_size=2`**, do not tag App Runner through CDK, do not delete the ACM
  validation CNAME, do not rescale the rate limit to `5 / 10 s`. Each has a measured reason in
  `NEXT.md` and `infra/README.md`.
- **The one thing genuinely owed is the queued iPhone test**, and only a person with an iPhone
  can discharge it.

## Closeout — 2026-07-28, at the seam

**Full ritual.** Ports 8000/5173/8138/8139 all free; nothing started, nothing left running, and
the queued test exercises the deployed site so no local server is needed.

**Suites (D4), all run rather than recalled:** builder **115**, api **214**, infra **63**,
frontend **80**.

**B3 — the gate's invariants were mutation-tested, not trusted green.** Three mutations, all
caught: inverting the comparison (`!==` → `===`) fails **10** tests — that is `QUA-1`'s defect
class, which once passed all 18; dropping the query string from the redirect fails **1**;
removing the no-loop branch fails **2**.

**B1 — the doc audit found three HIGH defects and all three were this session's own work.**
Two were in `infra/README.md` §1a's re-verification block, written at `PW-6` while the password
was still on: `PW-8` corrected §8 and §8a and never returned to §1a, so it still set the deleted
`ARTISTPATH_DEPLOY_PASSWORD` and sent Basic auth. The third was the previous handoff's `--prune`
claim, corrected in `NEXT.md` and here but not at its source. **All three are defects of
omission or of not-going-back — exactly what the audit exists for and what a grep cannot find.**
Fixed, and the corrected §1a block was then executed verbatim.

**D6 — the standing context layer.**

| Layer | Unit | Figure |
|---|---|---|
| Unconditional | characters | **43,692** |
| Conditional | lines | **2,120** |

**Both grew today, and the growth is `CLAUDE.md`'s environment note (+286 characters).** It was
a **correction** — the note said the project lives under OneDrive and that `UV_LINK_MODE=copy` is
required or `uv` fails, and neither was true. A first draft cost +464; it was trimmed by moving
the detail into `memory/env-onedrive-uv.md`, which is conditional. The conditional +13 lines are
the `closeout` D6 path fix and the App Runner tagging narrative.

⚠ **The previous figures in this log are not comparable.** `closeout` D6 named the pre-migration
memory slug, whose directory still exists, so it had been computing both numbers against a frozen
copy that could never move. Corrected 2026-07-28; these are the first figures measured against
the live one.

**A3 — every deferral condition re-tested against reality, not merely confirmed to exist.** None
has come due: no RSC machinery in the frontend (react-router CSRF), no `viewport-fit=cover` in
`index.html` (safe-area inset), the App Runner service was not recreated and its CLI tags are
still present, and `sync_frontend` appears in none of the four deploy logs (`--prune`).

**A4 — three config fields were added** (`front_door_secret`, `site_hostname`,
`certificate_arn`). None is a knob sitting at an old default: `app.py` `_require`s all three, so
production cannot run without them. The `""` defaults exist only so the storage stage and the
tests can synthesise without a certificate.

**D2 is inapplicable** — the graph artifact did not change, so the committed fixtures are not
stale. **D3:** what is live is image tag `37d559e` on the adopted artifact `4cb84ef9…`,
unchanged all day; the ACM certificate is
`arn:aws:acm:us-east-1:826731842184:certificate/0f61db68-cfc6-42e9-938c-70b5b6f081e5`.
