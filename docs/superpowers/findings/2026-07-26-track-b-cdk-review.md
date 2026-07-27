# `DEP-33` — team review re-run against the deployed CDK stack

**Role: AUTHORITATIVE for its own findings and triage.** Run 2026-07-26, after Track B was
built **and deployed**. This discharges `DEP-33`, whose requirement was that the Gate 1 → 2
team review be re-run against the CDK stack **before cutover** — seven of the original
review's blocking findings concerned a design rather than code, because `infra/` did not
exist when it ran.

**Four reviewers: architect (`ARC-`), security (`SEC-`), quality (`QUA-`), frontend
(`FRO-`).** The graph analyst was deliberately **not** staffed — no scoring question is open,
and path-quality work remains paused. Identifier series verified disjoint from `DEP-`, `TR-`,
`TKA-`, `TKD-`, `TKB-`, `FMS-`, `CNS-`.

**45 findings: 10 blocking, 20 cheap fixes, 8 deferred with conditions, 7 recorded as
correct-but-untested.** Nothing found invalidates the deploy. Everything blocking concerns
what happens on the **next** deploy or to the **first** user, not to the running stack.

> **This document owns no path-quality figures.** The operational figures it does own
> (mutation counts, test counts) are measurements of this review and are cited from here.

---

## §1 The headline: ten of nineteen mutations went green

Quality broke the source nineteen ways and ran the suites. **Ten mutations passed
undetected** — the suite could not distinguish the mutated stack from the real one.

| mutation | caught? |
|---|---|
| viewer function's password comparison **inverted** | **no** |
| synth-time credential substitution **silently no-ops** | **no** |
| password function **detached from the site's default behaviour** | **no** |
| clip table renamed | **no** |
| artifact bucket `RETAIN` → `DESTROY` | **no** |
| billing threshold hardcoded, ignoring its input | **no** |
| versioning moved from the artifact bucket to the SPA bucket | **no** |
| image tag pinned to `latest`, ignoring `image_tag` | **no** |
| container port changed | **no** |
| middleware narrowed to GET-only / exempting `/track` / search-only | **no** (×3) |
| `ARTISTPATH_CORS_ORIGINS` deleted | yes |
| `grant_read` widened to the whole bucket | yes |
| `authorization` added to the origin-request allow-list | yes (CDK synth raises) |
| `/health` exemption deleted | yes |
| middleware's `403` replaced by pass-through | yes |

**Both mutation checks the Track B session ran itself replicate and are genuinely held.**
The failure was not that its checks were wrong — it was **generalising from two spot checks
to a suite**. Quality's own caveat is important and is retained: nineteen hand-picked
mutations are a **lower bound** on the vacuity, not a measurement of it.

> **This is the fourth instance of the project's signature defect** after `FMS-P1`, `TR-2`
> and `TKB-4`, and the first where the vacuity was *distributed* — no single test was
> obviously vacuous; the suite simply had holes where the properties were.

---

## §2 Blocking — the next session's first work, in this order

Ordered by *what breaks and how silently*, not by reviewer.

| # | id | what it is | why this rank |
|---|---|---|---|
| 1 | `QUA-2` | **Nothing asserts the password function is attached to the site's default behaviour.** Detaching it leaves the API gated and the entire site publicly readable. | The only **silent** one. Every other blocker locks somebody out, so it gets found. This one works perfectly for the owner and is open to the internet. The runbook's one `expect 401` check runs at deploy and never again. |
| 2 | `ARC-1` | **`-c stage=storage` against the deployed stack deletes eight resources including the CloudFront distribution.** Synthesised and diffed. | A deleted distribution does not return with the same domain, so **every link ever shared dies permanently**. The guard is a sentence in a README (`"Subsequent deploys skip this section"`), not a mechanism, and §2 is the *first* deploy command an operator meets. |
| 3 | `FRO-2` | **Nobody can log in.** The credential is `artistpath:<password>`; the browser asks for a username and nothing states it. The 401 body is empty. | Wastes the first friend's attempt entirely. Also: in-app browsers (WhatsApp, Instagram) frequently never show the auth dialog — flagged as risk, not measurement, since no phone was available. |
| 4 | `FRO-1` | **A returning visitor gets a permanently blank page after any redeploy.** `s3 sync` sets no `Cache-Control`, the default behaviour is `CachingOptimized`, and `--delete` removes the hashed asset the stale `index.html` points at. | **Verified live**: an object uploaded exactly as the runbook syncs it returns `ETag` and `Last-Modified` and **no `Cache-Control`**, so browsers fall back to heuristic freshness. No error boundary, so the symptom is a white screen with no text. |
| 5 | `QUA-1` | **The password function has no behavioural test** — the only test asserts three substrings appear in its source. | Inverting the gate (right password → 401, none → served) passed all 18 tests. This is the whole of `DEP-4`. Found independently by all three of `ARC-3`, `QUA-1`, `FRO-5`. |
| 6 | `QUA-3` | **The origin-secret middleware is tested on one endpoint.** | Narrowing it to exempt `/track` passed 185 tests — and `/track` is the endpoint whose unrate-limited catalogue calls are the gate's stated reason for existing. Narrowing it to GET-only leaves `POST /api/path`, the expensive Dijkstra, ungated. |
| 7 | `ARC-2` | **Design §5's 90-day CloudWatch retention was never implemented and is in no tracking document.** App Runner's log groups default to **Never Expire**. | The completeness-failure shape `CLAUDE.md` names: not decided against, simply dropped. Telemetry is `DEP-2`'s entire sink and it accumulates unbounded under a $25 alarm measuring the wrong thing. CDK cannot create these groups; it is two runbook commands. |
| 8 | `ARC-4` | **Hardcoded physical names (`artistpath-clips`, `artistpath-api`) plus `RETAIN` means the stack cannot be recreated.** | Any teardown orphans two globally-named resources and the next `cdk deploy` fails `AlreadyExists`, discovered at the worst moment. |
| 9 | `QUA-4` | ✅ **ALREADY FIXED — do not re-do.** The runbook's own gate figure was wrong — it said 17 infra tests; there are 18. | With no CI the runbook *is* the regression gate. A wrong expected count trains the operator to stop reading counts, which is the only thing that would catch a deleted assertion. Found by `ARC-10` too. **Closed in `6f49ab9`** (the closeout that committed this review), which **deleted** the expected counts rather than correcting them — the same reasoning, taken one step further. `infra/README.md` §7 now states the gate is that each suite exits 0. |
| 10 | `FRO-4` | **No step anywhere proves the SPA fallback works**, and §8 contains no authenticated request to the site at all. | It proves the gate rejects; it never proves it admits. `TR-5` is the finding two reviewers found independently and it would ship unverified. |

**Also fix before the URL is shared** (security's own pick, not formally blocking):

- **`SEC-1`** — a non-ASCII byte in the origin-secret header returns **500**, not 403.
  `hmac.compare_digest` raises on non-ASCII `str`. **Reproduced independently at the ASGI
  layer by the controlling session**: `TypeError: comparing strings with non-ASCII
  characters is not supported`. Not a bypass — it fails closed — but it is an
  unauthenticated remote way to write tracebacks into the telemetry log group. Fix: compare
  bytes.
- **`SEC-5`** — no autoscaling cap, so the account default (max 25 instances) applies. The
  origin secret rejects requests *inside* the container, after App Runner has counted and
  scaled on them. `DEP-17`'s claim that the gate stands between a forwarded link and an
  unbounded bill is true through CloudFront and **false at the API origin** — the same shape
  `TR-7` corrected once already.

---

## §3 Corrections to the record

**`TKB-7`'s stated mechanism is wrong; its conclusion is right.** `TKB-7` says a failed
create *"rolls the whole stack back, deleting the ECR repository you just pushed to."* The
repository carries `DeletionPolicy: Retain` — verified in the synthesised template — so
CloudFormation should retain it. The staged first deploy is still correct, but the real
justification is the reverse: a rollback **orphans fixed-name resources that then block the
retry** (`ARC-4`). Recorded so nobody removes the staging on the strength of a mechanism
that does not hold. *(Architect could not verify AWS's exact create-rollback semantics and
stated the conclusion both ways; neither could the controlling session.)*

**The Track B session's Task 11 Step 2 claim is overstated.** It says every command in the
runbook was verified to resolve. The read-only AWS commands were; the test-count line
(`QUA-4`) and the `cd` chain (`QUA-5`/`ARC-9` — the four mandatory gates do not execute as
pasted, since each `cd` is root-relative and none returns) were not.

**`infra/app.py` is a third place hardcoding the adopted graph's filename**, alongside
`api/config.py`. `closeout` A4's default-flip check knows about `ApiConfig` and does not know
about `infra/app.py`. The next graph adoption will flip one and not the other (`ARC-7`).

---

## §4 Cheap fixes, not blocking

> ✅ **`ARC-9`/`QUA-5` are ALREADY FIXED — do not re-do.** Closed in `6f49ab9` alongside
> `QUA-4`: `infra/README.md` §7's four gates now each start
> `cd "$(git rev-parse --show-toplevel)/<pkg>"`, so they execute as pasted.

`ARC-5` clip table name is a literal in two packages with nothing binding them (one line:
pass `table_name` through as an env var, which also closes half of `ARC-4`) · `ARC-6`
`image_tag` defaults to `latest`, contradicting the runbook's own rule · `ARC-7` graph key
and sidecar are independent inputs · ~~`ARC-9`/`QUA-5` the runbook's `cd` chain~~ (fixed,
above) · `ARC-11` the
actual secret file (`infra/.env.deploy`) is documented nowhere · `ARC-14` `max_image_count=5`
bounds the rollback window · `ARC-15` `VITE_API_BASE` is inlined at build time and §6 does
not check it (verified latent, not live) · `SEC-2` the origin-secret gate **fails open** if
the variable is ever dropped, and `/docs`/`/openapi.json` are live · `SEC-3` both secrets sit
in plaintext in `infra/cdk.out/` **inside the OneDrive tree**, and `str.replace` substitutes
the credential into the function's own comment · `SEC-6` `/health` discloses artifact
identity unauthenticated · `SEC-7` no security response headers · `FRO-3` an edge 401 on
`/api/*` presents as *every card silent* — visually identical to the C1 defect the gate
exists to prevent · `FRO-5` the viewer function's test is substring-only · `FRO-7` every
delivery-path failure is a blank page; static fallback markup in `index.html` would give a
friend something to read out · `QUA-6` `RETAIN` unasserted and the versioning test matches
*any* bucket · `QUA-7` the billing-threshold test passes with the value hardcoded · `QUA-8`
the table name is unasserted · `QUA-9` image tag and port unasserted · `QUA-10` `infra/app.py`
has **no test at all**, so `TKB-7`'s protection rides on an unverified context string · 
`QUA-11` the gates are documented *after* the deploy they gate.

## §5 Deferred, each with its condition

| id | condition to close |
|---|---|
| `SEC-4` | instance role can `List*` the artifact bucket (reads are correctly scoped). Closes when that bucket holds a second thing, or on a least-privilege pass |
| `SEC-8` | password comparison is not constant-time. **Not exploitable** — sub-microsecond signal behind edge scheduling. Closes if `cloudfront-js-2.0`'s `crypto` module is confirmed available |
| `SEC-9` | no access logs, no rate limiting, TLS 1.0 on the default certificate (forced by `DEP-5`). Revisit at the Gate 2 → 3 boundary |
| `SEC-10` | infrastructure identifiers are committed. **Repo is private today.** Becomes material if it is opened |
| `ARC-8` | uploading a graph without redeploying arms a delayed boot failure — the expected sha is baked in at deploy time. Closes when the runbook states the invariant |
| `ARC-12` | `npx cdk` is unpinned — the one unpinned link in the release chain, inconsistent with `DEP-32`'s own reasoning. Closes when pinned |
| `ARC-13` | health-check budget is ~50 s and **boot time has never been measured**. Closes on measuring it, or raising `unhealthy_threshold` |
| `QUA-12` | three brittle assertions. Condition: first CDK minor-version bump, or a second read grant entering the stack |
| `QUA-13` | `hmac.compare_digest` is held by a comment, not a test — not unit-testable. **Permanent review-only invariant**; belongs in a comment at the call site |
| `FRO-6` | `WWW-Authenticate` omits `charset="UTF-8"`; a non-ASCII password would silently never match. Inert if the live password is ASCII |

## §6 What the review cleared

Stating this because the value of a re-review is partly in what it settles.

- **`TR-7` and `TR-8` both landed**, confirmed independently by security and architect
  against the synthesised template, and verified live in both directions (403 without the
  header, 200 with).
- **`TR-6` is closed at both layers** — `CACHING_DISABLED` pinned, and the API sets no
  `Cache-Control`/`ETag` on the track response either, so no browser heuristic cache can
  resurrect C2 by that route.
- **`TKB-2` is a correct catch and its replacement works.** The viewer function's rewrite was
  **executed** against 22 URLs by frontend and 14 by architect: correct for every URL this
  app produces. No `CustomErrorResponses` in the template.
- **`Authorization` is not forwarded to App Runner, and CDK's synth *enforces* that** — the
  mutation adding it raised at synth time. Framework-enforced is stronger than test-enforced.
- Two buckets with correct policies, OAC scoped to this distribution, two separate IAM roles,
  `s3:GetObject` scoped to the single key, no cross-user cache leakage, the graph supply
  chain sound, `exclude` bounded (`TR-12`), `journey_id` bounded and `json.dumps`-emitted
  (`TR-14`), the Dockerfile shipping no secrets and no artifact.
- **The two-stage template is logical-ID stable** — the storage stage is a strict subset with
  no replacement churn. That half of `TKB-7` is unambiguously sound.

## §7 The review's own weakest link

**No reviewer touched AWS.** All four worked from source and local synthesis. The controlling
session closed two of those gaps by measurement — the absent `Cache-Control` (`FRO-1`) and
the 500 (`SEC-1`) — but three classes remain unverified:

1. **`QUA-2`'s central claim** that detaching the function association opens the site is an
   inference about CloudFront's behaviour model, not a measurement.
2. **Live drift.** Whether the deployed stack still matches the synthesised template, whether
   log retention was set by hand, and whether the billing alarm has left `INSUFFICIENT_DATA`
   — its failure mode is silence. Three read-only calls would settle all of it.
3. **Browser behaviour behind the gate.** Whether a browser re-attaches cached basic
   credentials to the SPA's same-origin `fetch()` calls is the mechanism the whole app
   depends on and it has never been exercised by a browser, because the SPA bucket is empty.
   It almost certainly works — and so did `TR-5`.

**Track C's first action closes 2 and 3 together:** load the site in a real browser, enter
the password, confirm a shared `/path/<mbid>/<mbid>` link returns the app and that a path
builds from within it.
