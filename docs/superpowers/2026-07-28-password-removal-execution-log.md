# Execution log — removing the password (Track A), 2026-07-28

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

## State at the seam

**All four suites green**, run 2026-07-28 from `C:\dev\music-app`:

| builder | api | infra | frontend unit |
|---|---|---|---|
| 115 ✅ | **213 ✅** (was 195; +18) | 58 ✅ | 80 ✅ |

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
