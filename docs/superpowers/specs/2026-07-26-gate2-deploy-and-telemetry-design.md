# Gate 2 — AWS deploy and bypass telemetry (design)

**Role: ACTIVE.** The governing design for Gate 2's deploy, owner-approved 2026-07-26.
**⚠ STATUS, 2026-07-26 — `Track A` IS IMPLEMENTED; the rest is not.** The original
"nothing here is implemented yet" is **struck**, not deleted, because several §4 and §5
passages are written in the future tense and still read as pending. Built and merged:
`DEP-10`–`DEP-13`, `DEP-25`–`DEP-28`, `DEP-30`, `/health`, and both telemetry events;
**`DEP-16` is DISCHARGED** by the round-trip verification. Record:
[`../2026-07-26-gate2-track-a-execution-log.md`](../2026-07-26-gate2-track-a-execution-log.md)
(`TKA-`), PR #27. **Tracks D, B and C remain unbuilt**, and `DEP-33` still requires the
team review re-run against the CDK stack before cutover. Where this and the roadmap
([`../plans/2026-07-21-alpha-rollout-roadmap.md`](../plans/2026-07-21-alpha-rollout-roadmap.md))
disagree on Gate 2 sequencing, **this document governs** — the two deviations are named
explicitly in §1 and §8.

Identifiers are namespaced **`DEP-n`** — verified unused across the repository before
allocation, and disjoint from `C`, `F`, `A`, `R`, `T3-`, `TF-`, `MKS-`, `ASC-`, `BYP-`,
`DRV-`, `CNS-`, `STC-`, `SYN-`, `CWD-`, `DLV-`, `CLM-` and `FMS-`.

**This document owns no measured figures.** It sets no threshold, adopts nothing, and
changes no routing weight, no graph, and no cost function.

**Path-quality work remains paused by owner decision.** §5 explains why building telemetry
is not a resumption of it, and that reasoning is load-bearing rather than a disclaimer.

---

## 0. What this is

Gate 2 of the roadmap is *friends & family*: roughly 5–20 known people, deployed on AWS.
This design covers three things in one piece of work:

1. **Deploy** the app to AWS so it has a URL that survives this machine being off.
2. **Harden** the API where deploying it is what makes a latent defect real.
3. **Collect bypass telemetry**, pulled forward from the roadmap's Phase 7, because the
   signal is worth having from the first handful of users rather than the first hundred.

**CI is deliberately out of scope**, at the owner's instruction. The roadmap schedules CI
before deploy and gives its reason (with several users you stop noticing regressions), and
it also records the counter-option as open judgment call 2 — "if seeing it live matters
more, deploy can go first; at Gate-2 scale the regression risk is tolerable." **This is
that branch being taken deliberately, not overlooked.** `DEP-15` records what that costs.

## 1. Decisions taken, and whose they were

| # | Decision | Whose | Note |
|---|---|---|---|
| `DEP-1` | Hosting is **App Runner + S3 + CloudFront + DynamoDB**, region `us-east-1` | Owner | The roadmap's recorded Phase 5 shape. Keeps one long-lived process with the graph in memory, which is the architecture's premise. |
| `DEP-2` | Telemetry sink is **structured JSON on stdout → CloudWatch Logs** | Owner | App Runner ships stdout automatically, so this is the only option with no new infrastructure. Promoting to S3 later is a config change, not a redesign. |
| `DEP-3` | **All of roadmap Phase 3 except CI** rides along | Owner | Two of its items are *caused by* deploying (see §4); the rest are small enough that splitting them costs more than doing them. |
| `DEP-4` | Access is a **shared password in a CloudFront Function** | Owner | Not authentication. Its purpose is narrow and stated in §2. |
| `DEP-5` | **CloudFront's default domain**; no custom domain, no ACM certificate | Owner | Adding one later is an alias record and a certificate, not a redesign. |
| `DEP-6` | Journey correlation is a **client-generated id sent as an HTTP header** | Session | Decided rather than escalated: it is instrumentation, and the product-facing property it could have damaged (shareable URLs stay clean) is preserved. Reversible in one line. |
| `DEP-7` | The telemetry event logs **facts, not computed metrics** | Session | Reasoning in §5. This is the one design choice most worth arguing with. |

## 2. Topology

**One CloudFront distribution, two origins.**

```
                     ┌── default behaviour ──→  S3 (private, OAC)   — built SPA
browser ──→ CloudFront ─┤
     (password gate)     └── /api/* ───────────→  App Runner        — FastAPI + graph
                                                        │
                                                        ├─→ S3      — APG1 artifact (boot)
                                                        ├─→ DynamoDB — clip identity cache
                                                        └─→ stdout  — CloudWatch Logs
```

> **⚠ CORRECTED 2026-07-26 by the team review — `DEP-8` as written contained TWO false
> claims.** Record: `findings/2026-07-26-gate1-gate2-team-review.md` `TR-7`, `TR-8`. Both
> were caught by two reviewers independently. **Do not implement the struck text.**

**`DEP-8` — the single-origin choice removes CORS rather than configuring it.** The browser
talks to one origin, so no cross-origin request is made in normal operation.
`api/src/artistpath_api/config.py`'s CORS block anticipates this ("Not needed when the SPA
is proxied same-origin").

- **~~`cors_origins` goes unset in production.~~** **FALSE.** Verified at `config.py:60-68`:
  **unset yields the dev default** `http://localhost:5173`, so the deployed API would
  advertise that origin. The empty tuple requires setting `ARTISTPATH_CORS_ORIGINS` **to the
  empty string**. The CDK stack sets it explicitly. Near-harmless in effect — but a plan
  written faithfully from the original sentence produces the wrong config and, because
  same-origin means no preflight ever fires, nothing would reveal it.
- **~~The API is not reachable except through CloudFront, so the gate cannot be
  sidestepped.~~** **FALSE, and two other decisions rested on it.** App Runner publishes its
  own public `*.awsapprunner.com` URL and has no OAC equivalent, so the password gate
  protects the SPA and not the API. **Fix: CloudFront injects a shared origin-secret header
  on both behaviours and a FastAPI middleware rejects requests lacking it** — roughly ten
  lines and one CDK property. VPC ingress is *not* an alternative here: CloudFront VPC
  origins do not support App Runner. `DEP-17`'s cost reasoning is only true once this lands.

**`TR-5` — the SPA needs a CloudFront fallback, or every shared link 403s.** The default
behaviour serves a private S3 bucket, which holds no object at `/path/<mbid>/<mbid>`. The
distribution needs `errorResponses` mapping **403 and 404 → `/index.html` with status 200**.
**This is invisible locally**, because Vite serves `index.html` for unmatched paths — so it
would pass every local check and fail on the first thing a friend does. It breaks the
property CLAUDE.md gives as the *reason* path state lives in the URL.

**`TR-6` — the `/api/*` behaviour must pin its cache policy, and one failure is silent.**
CloudFront's defaults are wrong three ways: caching the freshly re-signed clip URL would
**resurrect C2 — "clips die after a while"** (closed 2026-07-25, marked do-not-re-plan, and
it would be diagnosed as a regression in closed work); dropping query strings makes every
search return whatever `q` was cached first; and `GET`-only methods 405 the path POST. Pin
`CACHING_DISABLED`, `ALLOW_ALL` methods, and an origin request policy that forwards the
query string **and** the journey-id header of `DEP-6` — CloudFront strips unlisted headers.

**`TR-7` (cont.) — two buckets, not one, and scoped IAM.** The SPA bucket sits behind OAC;
the artifact bucket has **no CloudFront origin at all**, or the graph becomes a 14 MB
download to anyone who guesses a filename that is printed in several committed documents.
The App Runner instance role is scoped to the single artifact key and to `GetItem`/`PutItem`
on the one clip table. App Runner needs **two** roles — an access role for the ECR pull and
an instance role for runtime; do not merge them.

**The password gate, stated at its real strength.** A CloudFront Function on viewer-request
compares an HTTP basic-auth header against one shared secret, and returns 401 otherwise.
**It is a shared secret in a function body, not authentication.** It gives no per-user
identity and secures nothing. **The secret is supplied at deploy time** (a CDK context
value or environment variable) and **is never committed to git** — a password in a CDK
source file would be in the repository's history permanently. Its purpose is specific: every card view fires a clip lookup
against Deezer/iTunes with no rate limiting of our own — `clips.py`'s own module docstring
flags upstream rate limiting as a live rather than theoretical risk — and a rate-limited
catalogue presents as **silent cards**, which is visually identical to the C1 wrong-artist
defect that was closed on 2026-07-25. The gate exists so that a forwarded link cannot
produce a symptom that would be diagnosed as a regression in already-closed work.

**`/health` reports artifact identity, not just liveness.** It returns the loaded graph's
sha256, artist count and edge count. This is App Runner's health-check target, and it makes
*which graph is live* answerable over HTTP. The repository's standing hazard is that
eighteen artifacts sit in `builder/scratch/` and are not interchangeable — every analysis
script asserts a checksum for exactly this reason. This applies that discipline to
production.

## 3. Graph delivery and boot

**`ARTISTPATH_GRAPH` learns to accept an `s3://bucket/key` URI**, alongside the local paths
it takes today. Anything without the scheme keeps working unchanged, so local development
and the test suite are untouched.

> **Deviation from the roadmap, deliberate.** Phase 5 specifies "real S3 graph loading with
> `GRAPH_VERSION`". One variable holding an explicit key delivers the same "swap the graph
> via one env var" story with no template assembly and nothing to get subtly wrong. If the
> owner prefers the roadmap's shape, it is a small change and does not affect anything else
> in this design.

**`ARTISTPATH_GRAPH_SHA256` is verified after fetch, and the service refuses to boot on a
mismatch.** Optional locally; **required in production**. A conclusion drawn from the wrong
artifact looks exactly like a correct one, and this is the deployment-shaped version of the
checksum gate every script in `builder/analysis/` already carries.

**`DEP-9` — the artifact is not in git and this is a real operational constraint, not a
footnote.** `.gitignore` excludes `*.bin`. Uploading the adopted artifact to S3 is a
**manual prerequisite** performed once from a machine that has it, and the plan must name
it as a task rather than assume it. Identity is the checksum in
[`../findings/2026-07-23-tiebreak-fix-adoption.md`](../findings/2026-07-23-tiebreak-fix-adoption.md),
which owns that figure.

## 4. Robustness — roadmap Phase 3, minus CI

Each item below was **verified in source** while writing this design, not taken from the
roadmap's description. Two of them are caused by deploying; one was already built and needs
no work; one is not on the roadmap's list at all.

| item | status found | what changes |
|---|---|---|
| Artifact length validation | **real defect, worsened by S3** | see `DEP-10` |
| Non-blocking DynamoDB | **real defect** | see `DEP-11` |
| Cache failure handling | **real defect, not on the roadmap's list** | see `DEP-12` |
| `from == target` guard | **absent** | see `DEP-13` |
| Invalid `reason` coercion | **already implemented** | nothing — `app.py` coerces any unrecognised reason to `dislike` |
| Request logging, latency, clip success rate | absent | delivered by §5, same mechanism |

> **⚠ CORRECTED 2026-07-26 by the team review — the claim below was WRONG, and it was this
> document's flagship §4 defect.** Record: `findings/2026-07-26-gate1-gate2-team-review.md`
> `TR-1`–`TR-4`. Established by experiment, twice independently and then re-run by this
> session. **Read the corrected version that follows the struck text; do not implement the
> struck version.**

**~~`DEP-10` — a truncated artifact currently loads successfully and serves wrong answers.~~**
~~On a short buffer `np.frombuffer` without `count` yields a shorter array, not an error.~~

**`DEP-10`, corrected — a truncated artifact RAISES, and the real silent case is a different
one.** Every truncation tested raises `JSONDecodeError`, because **the metadata JSON blob is
the last section of the layout**: any tail truncation — which is what a short S3 fetch
produces — destroys the JSON, and `json.loads` raises before the short arrays reach a caller.
The original reasoning stopped one section short of the format.

**Three things this changes, and the third is the real defect:**

1. **The fix is still wanted, but for error clarity rather than silence.** A truncated fetch
   currently fails boot with an unhandled `JSONDecodeError` naming nothing about truncation,
   in a service whose health check exists to report artifact identity. Compute the expected
   total byte length from the header's `N`, `E` and metadata length, check it before parsing,
   and pass `count=` to every `frombuffer` call.
2. **The test must assert the specific error the fix introduces** — see §9, also corrected.
3. **`TR-3` is the genuinely silent case and this document did not name it.** A header whose
   `N` disagrees with the metadata length **loads clean**, leaving `pop_raw` and
   `degree_hub_penalty` at *different lengths* while both are indexed by node id in the cost
   function. **Guard: one assertion, `len(meta["mbids"]) == n.`**

**`TR-4` — the fix already exists in the other package.** `builder/.../artifact.py:87-103`
raises on both truncation cases; `api/.../graph_store.py:99-110` has no bounds checks at all.
The two independent APG1 parsers have **already drifted, undetected**, in the reader that is
about to start fetching over a network. That is the concrete answer to whether
lockstep-by-hand is a liability, and it belongs in the record rather than in a comment.

**`DEP-11` — sync boto3 on the async event loop.** `DynamoClipCache.get` and `.put` are
synchronous and are called from inside the async clip endpoint, so every clip lookup blocks
the whole event loop. Invisible with one user; with several it stalls everyone's requests,
and clips are the most frequent call the app makes. **Fix: `ClipCache` becomes an async
protocol**, `InMemoryClipCache` becomes trivially async, and `DynamoClipCache` wraps its two
boto3 calls in `asyncio.to_thread`. **No new dependency** — deliberately not aioboto3, which
would add a dependency to fix a problem a thread already fixes.

**`DEP-12` — cache failures currently become 500s, and this is not on the roadmap's list.**
`ClipResolver.resolve` routes every *catalogue* call through `_get`, which swallows failures
by design, but calls `self._cache.get` and `self._cache.put` **unguarded**. In development
that is unreachable because the in-memory cache cannot fail. In production a DynamoDB blip
becomes a 500 on the clip endpoint — the single outcome `clips.py`'s docstring says must
never occur ("a clip is decorative … must produce a silent card and never a 500"). **Cache
failures are treated as a miss.**

**`DEP-13` — `from == target` yields a one-card journey labelled as ordinary.** `find_path`
returns `[source]` for that case and `find_journey` labels the result `natural`; the code
comments the degenerate case explicitly. **It becomes a 422.**

## 5. Telemetry

### The design choice worth arguing with

**`DEP-7` — the event logs facts, and every quality metric is derived offline.** The
alternative — computing `PathMetrics` inline and logging the numbers — was considered and
rejected on three grounds:

1. **Routing is deterministic.** Given the artifact, the config and the request, the path is
   exactly reproducible. Any metric, including ones not yet invented, can be computed
   offline from the logged inputs against the **frozen** top-1%-by-degree set, which is
   where `evaluation.py` says that set belongs.
2. **Choosing production's metric is a scoring decision, and scoring is paused.** Baking
   `top1pct_degree_frac` into shipped code would take a position on a contested question
   during a pause on exactly that question.
3. **The expensive metrics are the ones the record says do not work.** Adamic–Adar and the
   overlap coefficient dominate `path_metrics`' cost and are, per Phase 1 log §3.8 and
   `WHAT-GOOD-LOOKS-LIKE` value 8, the **worst** predictors of the owner's verdict. Paying
   per-request latency for them would be paying most for the least informative channel.

### Why this is not a resumption of path-quality work

Telemetry **collects**; it does not change routing, weights, the graph, the cost function,
or any threshold, and it adopts nothing. It is also the instrument the record repeatedly
names as the one that would settle this class of question — `findings/2026-07-22-phase2-sweep-results.md`
§0 item 5 (real usage at volume, against a 130-pair frozen panel), and `WHAT-GOOD-LOOKS-LIKE`
values 2 and 4, both of which say telemetry is what would test them. **Building the
instrument is not running the experiment.** Any *use* of this data to justify a routing
change is path-quality work, is behind the pause, and needs its own pre-registration.

### Events

**`path` — one per `POST /api/path`:**

| field | why |
|---|---|
| `ts`, `journey_id` | ordering, and grouping presses into one walk |
| `source`, `target` | mbid **and** name |
| `exclude[]` | the full accumulated list with reasons — what makes the walk reconstructible |
| `dislike_count`, `known_count`, `bypass_depth` | derived, but makes queries possible without parsing |
| `path[]` | mbid **and** name per artist |
| `stop_rule` | how F1 resolved: `natural`, `forced`, or `adjacent_only` |
| `duration_ms` | the roadmap's "path latency" item |

**`clip` — one per track request:** mbid, name, cache hit/miss, which catalogue answered,
resolved or silent, `duration_ms`. This is the roadmap's "clip success rate" item.

**Names are redundant and included anyway.** They are derivable from the mbid via the
artifact; carrying them makes a log line readable in the CloudWatch console without tooling,
which at this scale is the difference between glancing at the data and writing a script.

**`DEP-14` — logging the resulting path is deliberate redundancy.** It is reproducible from
the inputs, so strictly it is unnecessary. It earns its place by letting offline analysis
**verify that the deployed router reproduces what the user actually saw**, which catches
config or artifact drift between production and the analysis machine. That is a failure
class this project has met more than once.

### What it can and cannot answer

**Can:** whether bypassing lengthens the path *and* raises novelty (value 2, both clauses,
which is the form the value requires); whether hubs decline with depth (the roadmap's open
success condition); F2 — whether repeated *know them already* actually reaches more obscure
artists; whether the two buttons behave differently at all; how often F1 fires and how often
it lands on `adjacent_only`, currently unmeasured in real use; clip success rate; latency.

**Cannot, stated now rather than discovered later:**

- **Whether anyone enjoyed a path.** No verdict channel exists; that is still the ear.
- **Value 3 — where a journey stops feeling like a journey.** An abandoned journey and a
  satisfied one are identical from the server: the last request looks the same either way.
  Journey-length distributions are a *hint* confounded with boredom, satisfaction and a
  closed laptop, and must not be read as the ceiling.
- **`BYP-13`'s defect class** — a clip playing a different artist of the same name. That
  needs an ear, and `BYP-13` remains open independently of this work.
- **Fame.** Everything here is in-graph popularity, which §2.11 establishes is not fame at
  the top of the distribution.

### Volume and retention

Full accumulated exclusion lists grow quadratically across a deep walk — a 100-press journey
costs roughly 400KB of logs. Negligible at this scale. If it ever is not, logging only the
newly-added artist works, because the diff is reconstructible within a journey. **Start
self-contained.** CloudWatch retention set to **90 days** to bound cost. No IP addresses, no
user identity, and `journey_id` is a random client-generated value that resets on reload.

## 6. Deploy mechanics

**Infrastructure as a CDK app in Python** under a new `infra/` package with its own
`pyproject.toml` and `.venv`, consistent with `builder/` and `api/`. This keeps the
repository at two languages rather than three.

**Deploys are manual and documented**, since CI is out of scope. Three steps, captured in
`infra/README.md`: build and push the API image to ECR; `cdk deploy`; build the frontend and
sync it to S3 with a CloudFront invalidation. **`UV_LINK_MODE=copy` applies to the new
package like every other** — the repository is under OneDrive.

## 7. Explicitly out of scope

- **CI, GitHub OIDC, and any deploy workflow** — `DEP-3`, owner's instruction.
- **The missing regression tests** the roadmap lists under Phase 4. They are not deleted
  from the roadmap; they stay there.
- **Custom domain and ACM** — `DEP-5`.
- **Cost alarms, autoscaling, abuse handling** — roadmap: "Gate 2 does not need" these.
- **The Gate 2 → 3 content-curation question.** It is a Gate 3 entry condition and is
  untouched by this work.
- **Any routing, weight, graph, or cost-function change.** The pause is intact.

## 8. Risks and weakest links

**`DEP-15` — no CI means no regression gate, and the roadmap's own reasoning says that
bites hardest at exactly this scale.** With one user you notice regressions; with friends
you do not. This design accepts that at the owner's instruction. The mitigation is weak and
should be named as weak: three test suites exist and are run by hand. **If a regression
reaches a friend before it reaches you, this decision is why**, and the roadmap's Phase 4 is
where the fix already lives.

**`DEP-16` — the load-bearing assumption behind §5 is that routing in production is
byte-identical to routing in analysis.** It rests on determinism (spec §9), on the checksum
gate in §3, and on production and analysis reading the same `ApiConfig` defaults. `DEP-14`
exists to detect the failure rather than assume it away. **What would falsify it:** a logged
path that does not reproduce offline from its own logged inputs. That check should be run
once against real data before any conclusion is drawn from telemetry, and it is cheap.

**`DEP-17` — cost is estimated, not measured.** App Runner bills for a warm instance and is
the dominant line item. No figure is asserted here; confirm against live pricing before
deploying, and note that the shared-password gate is what stands between a forwarded link
and an unbounded bill.

**Weakest link overall, stated plainly:** this design has never been run. Every defect in §4
was found by reading source, and the same reading produced the claim that invalid-reason
coercion is already built. If one of those readings is wrong, the corresponding task is
either unnecessary or insufficient — and the plan should verify each against the code before
executing it, per CLAUDE.md's rule about grepping everything a plan names.

## 9. Verification

- **Every defect in §4 gets a test that fails before the fix — and "fails before the fix" is
  the requirement, not a figure of speech.**

  > **⚠ CORRECTED 2026-07-26 (`TR-2`).** The original instruction here read: *"the test must
  > assert that a short artifact **raises**, not that a good one loads."* **That test passes
  > today, against unmodified source**, because every truncation already raises
  > `JSONDecodeError` (§4, `DEP-10` corrected). Written to that brief, this task would have
  > shipped a green vacuous test under this document's own flagship verification item — the
  > `FMS-P1` pattern the F1 execution log already records once.
  >
  > **The corrected requirement:** the truncation test asserts the **specific** exception type
  > and message the fix introduces, and a **separate** test covers `TR-3`, the header/metadata
  > length mismatch, which is the case that genuinely loads silently. **Run every new test
  > against unmodified source first and confirm it fails**; a test that passes before the
  > commit is a defect in the test, not evidence about the code.
- **`/health` reports the expected sha256** for the adopted artifact, checked against
  `findings/2026-07-23-tiebreak-fix-adoption.md`.
- **A path built through CloudFront matches one built locally** for the same pair and
  exclusions — the end-to-end form of `DEP-16`.
- **The telemetry round-trip:** take one logged `path` event, replay its inputs offline, and
  confirm the path reproduces. This discharges `DEP-16` and must happen before telemetry is
  used for anything.
- **A use-the-app queue entry** for the deployed URL, per `closeout` — the first entry in a
  while that is genuinely app-facing, since this changes where the app runs.

## 10. Open items carried, with success conditions

| item | condition to close |
|---|---|
| `DEP-15` — no regression gate | Roadmap Phase 4 executed, or a regression reaches a user and the decision is revisited |
| `DEP-16` — prod/analysis routing identity | The §9 telemetry round-trip passes against real logged data |
| `DEP-17` — cost unmeasured | One month of real billing observed |
| **Gate 1 → 2 team review** | Not part of this work and **not blocking it.** CLAUDE.md recommends a team review at gate boundaries after a period of real use; Gate 1 was discharged 2026-07-26 and no review has been run. **Owner's call**, recorded here so it is not lost. |
| `BYP-13` — wrong artist, same name | Independent of this work; still open |
| `CNS-1` — artist unfindable under the name users type | Independent of this work; still open |

## 11. Handoff seams — chosen here, at authoring time

This work is **12–16 tasks**, which is past the threshold where CLAUDE.md requires a plan
to name its own seams before execution rather than discovering one at task 15. **Three
tracks, each ending at a committed artifact rather than a live understanding.**

| track | contents | seam artifact | needs AWS? |
|---|---|---|---|
| **A — API hardening and telemetry** | `DEP-10`–`DEP-13`, `/health`, the `s3://` scheme and checksum gate, both event types, the frontend journey-id header | All three suites green; nothing deployed | **No** |
| **B — Infrastructure** | `api/Dockerfile`, the `infra/` CDK app, ECR, App Runner, S3 buckets, DynamoDB, CloudFront, the password function | `cdk deploy` succeeds; `/health` returns the expected sha256 | Yes |
| **C — Cutover and verification** | Artifact upload, frontend build and sync, §9's verification list, the use-the-app queue entry | A working URL and a closeout | Yes |

**`DEP-18` — Track A is deliberately first and deliberately AWS-free.** Every defect in §4
is reachable, testable and fixable with no AWS account, no credentials and no spend, and
each one is a genuine defect *today* rather than a deployment artifact. If the deploy stalls
for any reason — cost, credentials, a change of mind about hosting — **Track A still leaves
the app strictly better than it found it.** That is the property that makes it the right
first track, not merely the convenient one.

**Track B is the natural retirement point** if the session running it is long by then: its
output is committed infrastructure code and a deployed stack, both of which a fresh session
can read cold.

> **⚠ AMENDED 2026-07-26 — a FOURTH track was added, and the order changed.** `TR-16`.
> **Track D — frontend**, fenced by the owner at **six items**: responsive layout, search
> failure vocabulary, request timeouts, surfacing a failed `play()`, a catch-all route, and
> the iOS input attributes that stop autocorrect rewriting artist names. It exists because
> the frontend reviewer was staffed explicitly and found there is **no responsive styling
> anywhere in the application** — on a 390 px phone the artist name is squeezed toward zero
> width. **Track D needs no AWS**, so the running order is **A → D → B → C**: both code
> tracks land first, and the deploy then ships an already-fixed app rather than putting a
> phone-broken one in front of friends.

## 12. Amendments — 2026-07-26, after the team review

**All arise from `findings/2026-07-26-gate1-gate2-team-review.md`, which ran before any
implementation plan was written.** Marked inline above as well as listed here.

| # | change | where |
|---|---|---|
| `DEP-19` | `DEP-10`'s premise **corrected** — truncation raises; the silent case is the header/metadata length mismatch (`TR-1`, `TR-3`) | §4 |
| `DEP-20` | §9's truncation test instruction **corrected** — it prescribed a test that passes before the fix (`TR-2`) | §9 |
| `DEP-21` | `DEP-8`'s two false claims **corrected**; origin-secret header added (`TR-7`, `TR-8`) | §2 |
| `DEP-22` | CloudFront SPA fallback and `/api/*` cache policy **added** (`TR-5`, `TR-6`) | §2 |
| `DEP-23` | Two buckets, scoped IAM, App Runner's two roles **added** (`TR-7`) | §2 |
| `DEP-24` | S3 **versioning** on the graph bucket; upload and read the **sidecar manifest** rather than hand-transcribing a sha256 (`TR-9`, `TR-10`) | §3 |
| `DEP-25` | `exclude` bounded at 200 and deduplicated — **re-filed into §4's defect table** by §4's own criterion (`TR-12`) | §4 |
| `DEP-26` | `DEP-12` extended: the `put` path fails *after* a successful lookup, so return the clip anyway; and null upstream fields reach `TrackOut`'s `str` fields (`TR-13`) | §4 |
| `DEP-27` | `journey_id` length- and charset-bounded, emitted via `json.dumps`; the `clip` event carries it too (`TR-14`, `TR-15`) | §5 |
| `DEP-28` | `load_graph(uri, expected_sha, reader)` **injectable seam**, because `build_default_app` has zero coverage and `ApiConfig` reads env at two different times, so the obvious test passes for the wrong reason (`TR-11`) | §4, §6 |
| `DEP-29` | **Track D added**, order becomes A → D → B → C (`TR-16`) | §11 |
| `DEP-30` | **`npm run test:e2e` becomes a mandatory manual deploy step**, plus the `EPERM` fix that makes it runnable by default — converts an existing suite into the regression gate `DEP-15` says does not exist, with no CI (`TR-17`) | §6 |
| `DEP-31` | **One CloudWatch billing alarm pulled from Gate 3 into Gate 2** — `DEP-17`'s success condition is "observe a month of billing", and an alarm is how you observe without remembering to look. Owner's decision | §6, §8 |
| `DEP-32` | `uv.lock` committed, `uv sync --frozen` in the Dockerfile — with no CI the image is the release artifact | §6 |

**Deferred to Gate 3 with their reasoning recorded**, not dropped: path latency at bypass
depth, accessibility, link previews, and the silent dropping of unresolvable exclusion MBIDs.
See the review's §6.

**`DEP-33` — this review must be re-run against the CDK stack before cutover.** Seven of its
blocking findings are about a design rather than about code, because `infra/` does not exist
yet. That is a real limitation of the review, not a caveat on it.
