# Team review at the Gate 1 → Gate 2 boundary — 2026-07-26

**Role: AUTHORITATIVE for its own measurements and for the triage recorded here.** The
gate-boundary team review CLAUDE.md schedules at Gate 1 → 2 after a period of real use.
Gate 1 was discharged 2026-07-26; this ran the same day, **before** any implementation plan
was written.

Identifiers are namespaced **`TR-n`** — verified unused across the repository before
allocation, and disjoint from `C`, `F`, `A`, `R`, `T3-`, `TF-`, `MKS-`, `ASC-`, `BYP-`,
`DRV-`, `CNS-`, `STC-`, `SYN-`, `CWD-`, `DLV-`, `CLM-`, `FMS-` and `DEP-`.

**Consequences live in the design** — `specs/2026-07-26-gate2-deploy-and-telemetry-design.md`
(`DEP-`). Where this document and the amended design disagree, **the design governs**; this
is the record of how it came to be amended.

**Nothing here touches routing, weights, the cost function or the graph. The path-quality
pause is intact.**

---

## 1. What was reviewed, and how

Four reviewers, run as parallel general-purpose subagents with role briefs: **architect**,
**security**, **quality/testing**, **frontend**. The graph analyst was **not** staffed —
CLAUDE.md includes it only when a scoring question is open, and none is.

**Frontend was staffed explicitly**, per the roadmap's own meta-lesson that three
backend-focused reviewers once missed an entire defect class. That decision paid: Track D
(§5) exists because of it and would not otherwise have been proposed.

**Each reviewer was told not to trust the design's prose and to verify its claims against
source.** Three of the four ran code — truncating artifacts, timing `find_journey` at
depth, probing a live API, and running all four test suites — rather than reading only.

**Owner decisions taken on the results, same day:** frontend becomes a fourth track; a
single CloudWatch billing alarm moves from Gate 3 into Gate 2; `npm run test:e2e` becomes a
mandatory manual step in the deploy runbook; accessibility stays Gate-3 backlog on the
owner's knowledge that no one in the group uses a screen reader; Track D is fenced at six
items and link previews are excluded.

## 2. `TR-1` — the design's flagship defect was misdiagnosed, and its prescribed test could not fail

**This is the most valuable thing the review produced, and it is a correction to work done
earlier the same day.**

`DEP-10` claimed a truncated artifact "currently loads successfully and serves wrong
answers," reasoning that `np.frombuffer` without a `count=` argument yields a short array.
**It does not.** Two reviewers established this independently by experiment, and the
controlling session then re-ran it rather than relaying it:

```
frac=0.999  RAISES JSONDecodeError    frac=0.5  RAISES JSONDecodeError
frac=0.99   RAISES JSONDecodeError    frac=0.2  RAISES JSONDecodeError
frac=0.9    RAISES JSONDecodeError
```

**Mechanism:** the metadata JSON blob is the **last** section of the APG1 layout. Any tail
truncation — which is what a short S3 fetch produces — destroys the JSON, and `json.loads`
raises before the short arrays reach any caller. The original reasoning stopped one section
early.

**`TR-2` — the consequence was worse than the error.** The design's §9 instructed that the
test "must assert that a short artifact **raises**, not that a good one loads." **That test
passes today, against unmodified source.** Written to that brief, Track A would have shipped
a green, vacuous test under the design's own flagship verification item — the `FMS-P1`
pattern the F1 execution log already records once, recurring in a document whose §8
explicitly asks for that verification.

**`TR-3` — there is a genuinely silent corruption case, and it is not truncation.** A header
whose `N` disagrees with the metadata length loads clean. Measured:

```
MISMATCH: *** LOADED SILENTLY *** header_N=4 artist_count=2
          len(pop_raw)=2  len(offsets)=5  len(degree_hub_penalty)=4
```

`pop_raw` and `degree_hub_penalty` end up **different lengths**, and both are indexed by
node id in the cost function. The guard is one assertion, `len(meta["mbids"]) == n`.

**`TR-4` — the two APG1 parsers have already drifted, in the reader that is about to start
fetching over a network.** `builder/src/artistpath_builder/artifact.py:87-103` **already
raises** on both truncation cases; `api/src/artistpath_api/graph_store.py:99-110` has no
bounds checks at all. This is the concrete answer to whether lockstep-by-hand is a
liability: it has already failed once, undetected. CLAUDE.md names the hazard; the
enforcement is a comment.

**What survives of `DEP-10`:** the fix is still worth making, for **error clarity rather
than silence** — a truncated fetch currently fails boot with an unhandled `JSONDecodeError`
naming nothing about truncation. The task brief and the test must be rewritten to assert the
*specific* error the fix introduces, and to cover `TR-3`, which is the real silent case.

## 3. Blocking — gaps in the design, not defects in the code

Seven, none of which required code to exist. All are amended into the design.

| id | finding | why it blocks |
|---|---|---|
| `TR-5` | **No SPA fallback in the CloudFront design.** The default behaviour serves a private S3 bucket, which holds no object at `/path/<mbid>/<mbid>` | **Every shared journey link 403s on first open.** Found independently by two reviewers. Invisible locally, because Vite serves `index.html` for unmatched paths — so it would have passed every local check and failed on the first thing a friend did. It breaks the property CLAUDE.md gives as the *reason* path state lives in the URL |
| `TR-6` | **No cache policy specified for the `/api/*` behaviour** | CloudFront's default would cache the freshly re-signed clip URL and **resurrect C2 — "clips die after a while"** — closed 2026-07-25 and marked do-not-re-plan. It would present as a regression in closed work, which is the outcome `DEP-8` says the gate exists to prevent. Also drops query strings (every search returns the first cached `q`) and 405s the path POST |
| `TR-7` | **`DEP-8` claim 1 is false**: "the API is not reachable except through CloudFront" | App Runner publishes its own public URL and has no OAC equivalent. The password gate protects the SPA, not the API — and both `DEP-8`'s CORS reasoning and `DEP-17`'s cost reasoning rest on the claim. Fix is a CloudFront origin-secret header checked in middleware; VPC ingress is not available for App Runner CloudFront origins |
| `TR-8` | **`DEP-8` claim 2 is false**: "`cors_origins` goes unset in production" | Verified in `config.py:60-68`: **unset yields the dev default** `http://localhost:5173`. The empty tuple requires setting the variable *to empty*. A plan written faithfully from the design produces the wrong config, and same-origin means no preflight ever fires to reveal it |
| `TR-9` | **The adopted artifact is a single copy that cannot be rebuilt** | `acceptance.py` rejects any build containing a nameless artist and the adopted artifact has some; the module says so by design. So the only copy is gitignored on one OneDrive-synced machine. Wants S3 **versioning** on the graph bucket, and the upload becomes the second copy |
| `TR-10` | **The sidecar manifest already holds what `/health` and the checksum gate need** | `graph-t15-tiebreakfix.bin.json` carries sha256, artist count, edge count and build commit. The design instead asked an operator to hand-transcribe a 64-hex string, whose failure signature is "refuses to boot" **during a cutover**. Upload the sidecar; read identity from it |
| `TR-11` | **`build_default_app` has zero test coverage, and `ApiConfig` reads the environment at two different times** | Track A adds the S3 fetch and both checksum branches to the one function no test touches. `graph_path` and `clip_cache` are plain defaults evaluated at **import**; `cors_origins` uses `default_factory` and is per-instance. So the obvious `monkeypatch.setenv` test **passes for the wrong reason** and the S3 branch ships unexercised. Fix is an injectable seam — `load_graph(uri, expected_sha, reader)` — which also keeps Track A genuinely AWS-free |

## 4. Blocking — cheap code changes

| id | finding |
|---|---|
| `TR-12` | **`exclude` is unbounded and undeduplicated, and costs a graph traversal per entry** (`models.py:17`, `app.py:23-30`, `pathfinding.py:60`). One large POST buys arbitrary CPU on a GIL-bound handler, saturating the single warm instance. Fix: `max_length=200` plus dict-keyed dedupe — and the dedupe is independently correct, since `avoidance_map` already takes a `max()` per node. **Re-filed:** the controlling session had parked this under "Gate 2 does not need abuse handling"; the security reviewer argued it belongs in the design's §4 defect table **by §4's own criterion** — a latent defect that *deploying* makes real, because until now that list was only ever populated by our own frontend on localhost. The re-filing was accepted |
| `TR-13` | **`DEP-12` extends further than the design stated.** The unguarded cache call fails on `put` as well as `get` — and `put` fails *after* a successful catalogue lookup, so the correct behaviour is to **return the clip anyway**, not to treat it as a miss. Separately, a catalogue field present-but-null flows into `TrackOut`, whose fields are typed `str`, producing the same 500 the module docstring forbids. Both ride with `DEP-12` |
| `TR-14` | **`journey_id` is client-controlled and destined for structured logs.** Must be length- and charset-bounded and emitted via `json.dumps`, never string formatting, or a crafted header injects fabricated log records into the telemetry the design exists to collect. Cheap now, expensive to retrofit into data already gathered |
| `TR-15` | **The `clip` event needs the journey id too.** Without it you cannot ask "did *this* journey have silent cards" — which is the C1-lookalike question, and the design's §5 already concedes it cannot answer `BYP-13`'s class |

## 5. `TR-16` — Track D exists because the frontend reviewer was staffed

**The design had three tracks: API, infrastructure, cutover. The frontend was not a track,
and it needed to be.**

`grep` over `frontend/src` returns **zero** hits for any breakpoint, media query or
safe-area inset: there is no responsive styling in the application at all. On a 390 px
phone the card row's non-shrinkable elements exceed the available width, so the artist
name — the only content that matters — is squeezed toward zero.

> **⚠ CORRECTED 2026-07-26 by Track D (`TKD-1`) — this paragraph's evidence is wrong and its
> conclusion is right.** Two corrections, both verified against source:
>
> 1. **`grep` returns six hits, not zero** — `@media (max-width: 1024px)` in
>    `frontend/src/App.css`. The conclusion survives because that file was imported by
>    nothing and none of its selectors existed in any component: dead Vite scaffold, deleted
>    by Track D. **The consequence is the part that matters — any verification of the layout
>    fix phrased as "grep for a media query" passes BEFORE the fix**, which is the `FMS-P1` /
>    `TR-2` vacuous-check pattern. Track D therefore verified by rendered geometry in a real
>    browser: the interior artist name measured **0 px** at 390 px wide before, 200 px after.
> 2. **The viewport meta tag already existed** in `frontend/index.html`. Nothing was blocking
>    responsive CSS from taking effect; only the CSS was missing. Safe-area insets were
>    genuinely absent, so that part of the claim stands.
>
> The squeeze itself is confirmed, and the fix landed in Track D (PR #28). Alongside it: a search that
finds nothing and a search that *failed* render identically as nothing; no request carries a
timeout, so a cold instance shows "Building your path…" indefinitely; and a rejected
`play()` is discarded, leaving a card asserting "now playing" over silence.

**Owner's decision:** Track D is in Gate 2, fenced at **six items** — responsive layout,
search failure vocabulary, request timeouts, surfacing a failed `play()`, a catch-all
route, and the iOS input attributes that stop autocorrect rewriting artist names.

**`TR-17` — the review's best value-for-effort finding is not a defect.** The e2e suite
already passes against the **real adopted artifact**, and promoting `npm run test:e2e` to a
mandatory manual step in the deploy runbook converts an existing suite into the regression
gate `DEP-15` says does not exist — **with no CI and no new tests.** It needs one `EPERM`
fix to be runnable on its default invocation. Accepted by the owner.

## 6. Declined, deferred, and why

**Recorded so the reasoning is auditable, per this project's practice of keeping decisions
taken *against*.**

| item | disposition |
|---|---|
| Path latency growth with bypass depth | **Gate-3 backlog.** Measured and real, but the roadmap says plainly that Gate 2 does not need high concurrency. Recorded because the new `duration_ms` field will make it visible, and it should not then be read as a regression |
| Accessibility (ARIA, keyboard, focus management) | **Gate-3 backlog**, on the owner's knowledge that no one in the group uses a screen reader. Recorded, not lost |
| Link previews (per-path `<title>`, Open Graph) | **Gate-3 backlog.** Considered for Track D and excluded by the owner when the fence was drawn |
| Silent dropping of unresolvable exclusion MBIDs | **Gate-3 backlog.** Requires a graph swap to bite, and none is scheduled. The telemetry `exclude[]` field surfaces it if it happens |
| Deleting `evaluation.py` / `badpath.py` from the API package | **Not worth doing.** They are deliberately retained for the frozen analysis scripts; `closeout`'s orphaned-module sweep owns that call, not a review. **But** one line belongs in the deploy record, because with no CI "153 tests pass" is the whole regression signal and part of that number covers code production never runs |
| Committing `uv.lock` | **Accepted into Track B**, not deferred. Every API dependency is an open-ended `>=` and `uv.lock` is gitignored, so two builds of one commit differ. With no CI the image *is* the release artifact |
| Textbook security items | **Declined explicitly**: search-endpoint DoS (measured, trivial), MBID format validation (used only as dict keys), CSS injection via cover art (the attacker would have to be Deezer), timing attack on the gate's password comparison. Calibration to a 5–20 person private deployment was requested and delivered |

## 7. What the review confirmed sound

Stated because a review that reports only problems misrepresents the system.

- **All four recently-fixed player invariants hold in the code as written**, each with unit
  coverage: a finished clip advancing to the card below, audio stopping on New path / Reset
  path / bypass, pause-then-resume continuing rather than restarting, and disposed-player
  revival.
- **All four suites pass**, including the e2e specs against the real adopted artifact:
  api 153, builder 115, frontend 64, e2e 3. **`snyk_code_scan` on `api/`: 0 issues.**
- **The dependency-injection claim in CLAUDE.md is true** — no API test needs an artifact
  file or the network.
- **Cold start is a non-issue.** The artifact loads in well under a second; the design was
  right not to engineer for it.
- **`DEP-11`, `DEP-12`, `DEP-13` are all true as described**, and **invalid-`reason`
  coercion really is already implemented** — verified independently by two reviewers. The
  design's §4 was right about four of its five claims; `TR-1` is the fifth.
- **Determinism is well covered on the builder side**, which is what `DEP-16` rests on.

## 8. Weakest link, and what cuts against this review

**Seven of the blocking findings are about a design rather than about code, because
`infra/` does not exist yet.** They are unverifiable until written, and **this review should
be re-run against the CDK stack before cutover** — that is a real limitation, not a caveat.

**The strongest single argument in the review is one the reviewers made three times
independently:** three two-sided contracts — API↔frontend JSON, the cache protocol, and the
APG1 binary — are each verified on both sides by tests whose fixtures **encode the same
assumption as the code**. `TR-4` is that argument proven on the one contract where drift
already happened. If the argument is wrong anywhere, it is wrong about the JSON contract,
where the e2e specs cover more than the reviewer credited.

**Calibration on the controlling session's own work.** The design's §4 verified five claims
against source; four held under independent review and one — its flagship — did not. The
error was reasoning that stopped one section short of the format layout, and it was caught
only because reviewers were told to run the code rather than read it. **The lesson is not
"read more carefully": it is that a claim about runtime behaviour should be executed, and
that a verification instruction which does not name the *specific* failure it expects can be
satisfied by code that never changed.**
