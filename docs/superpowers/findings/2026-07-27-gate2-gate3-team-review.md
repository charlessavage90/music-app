# Gate 2 → Gate 3 team review — 2026-07-27

**Role: AUTHORITATIVE for its own measurements and triage.** The record of the Gate 2 → 3
boundary review, commissioned by the owner on 2026-07-27 after the Gate 2 cutover and the first
real phone run. Four reviewers —
architect, security, quality, frontend — each with the code open, read-only. The graph analyst
was **deliberately not staffed**: no scoring question is open and path quality is PAUSED, so
staffing it would have invited work inside the pause.

**This document owns no path-quality figures** and states none; those live in
`2026-07-21-scoring-adjudication.md`. The performance numbers here are its own measurements,
labelled as such, and carry the provenance caveat in the "Weakest link" section: **they are
from a dev laptop, not the App Runner container.**

**What this review is asked to decide.** Not "is this good code." The project has passed Gate 2
(friends & family, behind HTTP basic auth) and Gate 3 is public — anyone, unauthenticated, at
unknown volume, including hostile traffic. The question is: **what is currently protected only by
the password and by nobody knowing the URL, and what happens to each when the password comes
off?**

---

## 1. Measured

All four reviewers ran code. Suites, from `C:\dev\music-app`:

| builder | api | infra | frontend unit | frontend e2e |
|---|---|---|---|---|
| 115 ✅ | 195 ✅ | 58 ✅ | 80 ✅ | 5 ✅ |

The e2e run is new — the last closeout did not cover it; it required starting the API by hand
against `graph-t15-tiebreakfix.bin` (`/health` → `4cb84ef9…`, 74,193 artists, 898,006 edges).
Nothing failed, errored, or skipped. This independently re-confirms the migration's "all four
suites green from `C:\dev`" claim and adds the e2e layer.

**Two reviewers independently measured request cost and converged.**

Architect, per-request latency on the adopted 75k artifact (dev laptop, CPython 3.12):

| endpoint pair | path latency |
|---|---|
| two of the 200 most popular artists | 1–7 ms |
| two uniformly random artists | median 419 ms, max 783 ms |
| two of the 400 least popular artists | min 339 / median 711 / max 859 ms |

Security, concurrency ladder, same artifact:

| concurrent requests | throughput | p50 latency | max |
|---|---|---|---|
| 1 | 1.76 req/s | 0.57 s | 0.57 s |
| 5 | 1.52 req/s | 3.29 s | 3.29 s |
| 20 | 1.65 req/s | 10.97 s | 12.13 s |
| 40 | 1.53 req/s | 18.22 s | 25.73 s |

Throughput is **flat at ~1.5 req/s regardless of concurrency** — one Python process, GIL-bound
Dijkstra, capped at two App Runner instances. `/health` under 40 concurrent path requests
returned 200 OK in **22.09 s**, against a 5 s health-check timeout.

Other measurements, verified by construction:

- A 2,000,000-element `sources` array costs 442 ms and buffers ~70 MB before validation rejects
  it. `exclude`, the field beside it in `models.py`, **is** bounded with the correct reasoning in
  its comment; `sources` is not.
- A 20 MB request of junk exclusion ids returned **200 OK** and emitted **20,007,147 bytes** of
  CloudWatch telemetry (amplification 1:1, measured; no log retention set anywhere).
- The "Find path" button renders at **2.75 : 1** contrast, against a 4.5 : 1 minimum.
- Neither `build_default_app` (the production API entrypoint) nor `sync_frontend.main` (the deploy
  publisher) is imported by any test — grepped clean across `api/`, `infra/`, `frontend/`.
- APG1 length validation covers `mbids` only; `popularity`, `names`, `disambiguations`, and
  neighbour ids are not bounds-checked. Constructed short-array artifacts load clean.

---

## 2. What I infer — in plain terms

**Four things converge on one conclusion: the password is doing far more than access control,
and Gate 3 is the act of deleting it.**

- **One person with a laptop can take the site down and keep it down.** Not a bill attack — spend
  is capped at two instances. Forty open connections suffice. The slowness feeds back: `/health`
  misses its 5 s window, five failures at a 10 s interval, App Runner replaces the instance, load
  shifts to the other, which fails the same way. The site does not degrade — it cycles.
- **The clip system has no failure signal at any layer**, found independently by three reviewers
  from three directions. When Deezer rate-limits our shared egress IP, the code cannot tell
  "throttled" from "no such track", so it falls through and tries twice more — **tripling** our
  outbound rate and hardening the block. Meanwhile the user sees a card light up for a fraction of
  a second and revert. No message, no retry. The API's own telemetry comment says three distinct
  failures look visually identical; the person who most needs to tell them apart is the user, and
  cannot. Silent-music-failure is the single most likely stranger experience.
- **The guards are well tested; the wiring that switches them on is not tested at all.** Deleting
  the graph-checksum verification, the shared clip cache, or the request timeout — three one-line
  changes to `app.py:195-209` — leaves **all 448 tests green**. Separately, `sync_frontend.main`
  can be made to publish files in the wrong order (the bug that gives returning visitors a blank
  page) and all 58 infra tests still pass, because the ordering test asserts the order of a
  returned list, not of the actual upload calls. This is the exact shape the record already names:
  "somebody could have left the whole site open and not one test would have failed."
- **iOS may not play audio at all, and nothing can currently tell the owner.** The code never
  starts the sound in the same synchronous turn as the tap — it awaits a URL round-trip first,
  which is the specific thing iPhone Safari refuses. Desktop Chrome permits it (why nothing caught
  it), and Playwright launches Chrome with the autoplay policy disabled (why no test can catch
  it).

**One item where deferring costs more than acting:** every shared link is pinned to the
auto-generated `*.cloudfront.net` domain, which can never be recreated, moved between accounts, or
migrated off CloudFront. Gate 3 multiplies shared links by orders of magnitude. A custom domain
now costs a certificate and a DNS record; later it cannot rescue links already in circulation.

**A trap on the Gate 3 action itself:** the password and the deep-link routing are the *same*
CloudFront function, attached to both behaviours. Removing it to open the gate would 403 every
shared journey link, because the default behaviour serves a private S3 bucket with no object at
`/path/<mbid>/<mbid>`. `infra/README.md` has no Gate 3 section, so the removal procedure is
currently written down nowhere.

---

## 3. Findings, by reviewer

Severity is stated **and** whether it bites *at Gate 3 specifically* or is a general improvement
Gate 3 does not force. `file:line` citations are the reviewers'; verify before acting.

**Identifiers are namespaced `G3-`** (Gate 2→3 review), the reviewer encoded in the letter —
`G3-A` architect, `G3-S` security, `G3-Q` quality, `G3-F` frontend. Cite them in that form: bare
`A1`/`F2`/`C1` collide with Track 2 arms, closeout items, and the earlier reviews' own findings
(`TR-`, `ARC-`/`SEC-`/`QUA-`/`FRO-`). Forward-only — these are fixed at first commit.

### Architecture

| ID | Sev | Gate-3? | Finding |
|---|---|---|---|
| G3-A1 | HIGH | blocking | Request CPU cost is caller-chosen and varies ~100–300×, on one GIL-bound process capped at 2 instances. `pathfinding.py:113-142`, sync `def` at `app.py:103`, single worker `Dockerfile:22`, `max_size=2` `stack.py:159-165`. |
| G3-A2 | HIGH | blocking | No rate limiting anywhere (no WAF, no CloudFront rule). The only throttle is the password, which `viewer_function.js:5-9` documents *in source* as the compensating control for the clip fan-out. |
| G3-A3 | HIGH | blocking | Cost ceiling and capacity ceiling are the same knob (`max_size=2`), so fixing G3-A1 deletes the only automatic cost control. Sole detector is a 6-hour-period billing email; no throttle, no kill switch, no log retention. |
| G3-A4 | HIGH | blocking | Under Deezer 429s, clip resolution triples its own outbound rate (`clips.py:178-184` treats 429 as a miss and falls through hit→search→iTunes). No backoff, no circuit breaker. |
| G3-A5 | MEDIUM | irreversible | Site welded to the auto-generated CloudFront domain (`stack.py:331-333`); no custom domain, cert, or Route 53 anywhere. **The one item where the cost of deferring is unbounded and the cost of acting now is near zero.** |
| G3-A6 | MEDIUM | no | APG1 consistency check covers only `mbids`; the exact skew its own comment describes (`popularity` short) loads clean and 500s per-artist. Neighbour ids unchecked. Fix: three length asserts. |
| G3-A7 | MEDIUM | no | Nothing tests the two APG1 parsers against each other; a builder-side layout change surfaces first at production boot (fails closed → bad deploy, not corruption). |
| G3-A8 | MEDIUM | no | Fixed mutable S3 graph key: a wrong upload detonates at the next instance replacement, not at upload time. Content-addressed keys would make it atomic. |
| G3-A9 | MEDIUM | no | CloudFront caches nothing under `/api/*`, including `/api/artists/search`, which is a pure function of an immutable graph — the legitimate half of the keystroke load is cacheable. |

### Security

| ID | Sev | Gate-3? | Finding |
|---|---|---|---|
| G3-S1 | HIGH | blocking | Same as G3-A1, measured as a hard ~1.5 req/s ceiling for the whole internet + the health-check cascade (40 concurrent → `/health` 22 s). Total self-sustaining outage for the cost of 40 sockets. |
| G3-S2 | HIGH | blocking | Clip endpoint is an unauthenticated outbound proxy: every request, cache hit included, fires a live Deezer/iTunes call from the shared egress IP (`clips.py:201-204`, by design per `config.py:94-98`). One `while true` loop silences clips for everyone. |
| G3-S3 | MEDIUM | blocking | `PathRequest.sources` has no `max_length`; a 70 MB array is fully materialised before the 2-source check. `ExclusionIn.id` likewise unconstrained; no body-size limit anywhere. |
| G3-S4 | MEDIUM | no | Unbounded attacker strings written verbatim to CloudWatch (`app.py:130`), no retention, billed per GB. Secondary: raw bypass counts let an outsider poison the Phase 7 "ground truth" telemetry. |
| G3-S5 | MEDIUM | no | No CloudFront access logging (diagnosis-by-probe stops working with strangers), no response-headers policy (no HSTS/CSP — and `ArtistCard.tsx:43` interpolates a remote `coverUrl` into inline CSS), no WAF. |
| G3-S6 | LOW | no (pre-existing) | API container runs as root (`Dockerfile`, no `USER`). One line; contained by App Runner isolation and a near-empty instance role. |
| G3-S7 | LOW | operational | The password and the SPA fallback are one CloudFront function; deleting it to open Gate 3 403s every shared link. Removal procedure unwritten. |

### Quality

| ID | Sev | Gate-3? | Finding |
|---|---|---|---|
| G3-Q1 | HIGH | blocking | `build_default_app` (`app.py:195-209`) has zero coverage; three separate one-line mutations — drop the sha256 check, force `InMemoryClipCache`, drop the HTTP timeout — each pass all 448 tests. This is DEP-24 / QUA-2's shape: every guard tested, the wiring that arms them untested. |
| G3-Q2 | HIGH | blocking | `sync_frontend.main` free to ignore the plan it built; swapping the asset/index upload order passes all 58 infra tests including the one named for that bug, because it asserts list order not call order. FRO-1's second form. |
| G3-Q3 | MEDIUM | no | `/health`'s artifact-identity assertion is vacuous: `source_sha256` is `''` for every test fixture, so the assert is `'' == ''`. Hardcoding `graph_sha256=""` passes all 195 api tests. |
| G3-Q4 | MEDIUM | relevant | The cold-start timeout UI (`PathStatus.tsx:26-39`) and its retry counter (`usePath.ts:28,35`) are unreachable by any test; deleting either strands the first stranger of the day on a cold instance. |
| G3-Q5 | MEDIUM | decision | No CI (`.github/` absent — a recorded deliberate position, DEP-3/15), so the strongest tests (5 Playwright specs) are the least likely to run: excluded from `npm test`, need a hand-started API the config does not launch. |
| G3-Q6 | LOW-MED | no | Builder↔api APG1 lockstep has no binding test; a consistently-applied metadata key rename passes both suites and `KeyError`s at the next real boot (loud, but at deploy time). Same conclusion as G3-A7. |
| G3-Q7 | LOW | no | `badpath.py` (cancelled) and `evaluation.py` (offline analysis) ship in the API image; 117 tests maintain a cancelled feature. Dead weight, deliberate per docstrings. |
| G3-Q8 | NIT | no | Stale count in `test_frozen_script_aliases.py:5` — docstring says "Sixteen of those scripts import the shipped classes"; measured now, **51** `.py` files under `builder/analysis/` import `artistpath_api` by an actual import statement (53 *mention* it, 2 of those in comments; the "four import `hub_node_set`" half is correct). Same miscount class the migration plan §4 recorded ("read 16 until corrected"); count with `grep -F` per variant. Side note from the same reviewer: `builder/tests/fixtures/graph-fixture.bin` is a 124 KB committed binary **no builder test reads** (only the api copy is read). |

### Frontend

| ID | Sev | Gate-3? | Finding |
|---|---|---|---|
| G3-F1 | HIGH | blocking | Any clip failure ends in `clear()` — bottom bar vanishes, "now playing" gone, no message, no retry. Three distinct failure routes (`Player.ts:49-51`, `useClip.ts:45,51`, `usePlayer.ts:74-76`) look identical to the user. |
| G3-F2 | HIGH | blocking if confirmed | `play()` is never called in the tap's synchronous turn (`usePlayer.ts:49` awaits a URL first) — the exact thing iOS Safari rejects. Worst reading: no clip ever plays on iPhone and the app never says why. **One tap on a real device confirms or kills it.** |
| G3-F3 | MED-HIGH | relevant | A shared link truncated in transit yields a *different journey* silently — the server skips unknown ids (`app.py:38-39`) and the frontend never notices. Sharing is the Gate 3 distribution mechanism. |
| G3-F4 | MEDIUM | relevant | With a screen reader/keyboard the journey is 8 identically-named buttons; a bypass press drops focus to `body` with no announcement; search results and errors are never announced. Three aria attributes in the whole app. |
| G3-F5 | MEDIUM | no | "Find path", "Clear exclusions", "Try again" render at 2.75 : 1 (measured) — the buttons a first-timer and an error-stranded user must find are the least readable elements on screen. |
| G3-F6 | MEDIUM | no | The search dropdown never closes on blur/outside-click/Escape and covers the "To" field; the first interaction anyone has can select an artist they'd rejected. |
| G3-F7 | LOW-MED | relevant | A shared link shows a near-empty page for up to 20 s without naming the two artists; and with the gate gone, every link previews identically (constant `<title>`, no OG tags). |
| G3-F8 | LOW | no | Play/pause display is driven by app bookkeeping, not audio events — an incoming call / tab switch / Bluetooth pause stops sound while the UI still says "now playing". No MediaSession metadata. |
| G3-F9 | LOW | no | `ApiError` discards the server's message, so same-artist (422) and the 201st-bypass cap arrive as the generic "Something went wrong". |
| G3-F10 | LOW | no | Audio keeps playing through the browser Back button — the one control the project documents as the bypass undo. |
| G3-F11 | LOW | no | "No preview available" conflates three causes and never retries for the page's life. |

---

## 4. Weakest link

**Both capacity reviewers flagged the same one, unprompted: every timing is from a Windows dev
laptop, not a 1-vCPU App Runner container.** The *shape* — flat throughput, linear latency growth,
GIL serialisation — holds anywhere and is what G3-A1/G3-S1 rest on. The absolute per-request cost could
differ by ~2× either way.

**Both converged on the same falsification test, and it is the cheapest decisive experiment
available:** run the concurrency ladder against the live CloudFront origin (with the password) and
read `/health` latency at 40 concurrent. Ten minutes. It decides whether G3-A1/G3-S1 is "add a
rate-limit rule" or "rearchitect", and the roadmap records that concurrency has **never** been
measured against the real deployment.

Secondary: the health-check *cascade* half is inferred from `stack.py:241-250`, not verified
against App Runner's documented behaviour; if the response is gentler than instance replacement,
that half is wrong. The capacity half is not.

Cheaply abandoned if falsified: G3-F2's iOS-specific half (one tap settles it), and G3-F5's contrast
figures (computed from CSS, not sampled from a screenshot).

---

## 5. What was checked and found clean

Stated because negative results stop the next reviewer redoing them, and because several are
where vacuity was expected and not found:

- **Statefulness is genuinely clean** — no per-user/session server state; horizontal scaling is
  not blocked by state. Boot fails closed on every malformed-payload class constructed. Cold start
  is 0.13 s local; `min_size=1` means no cold-start cliff for the first visitor. Memory is not a
  constraint.
- **The destructive-deploy guard is real code, not a runbook sentence** (`deploy_stage.py:60-72`,
  tested) — the prior review's finding is properly closed. Data that matters is `RETAIN` +
  versioned; rollback is documented (`infra/README.md` §9–10).
- **Clip SSRF holds** — mbid resolved against the graph first; `169.254.169.254`, path traversal,
  and junk mbids all 404 with zero outbound calls. The name sent to catalogues comes from
  `store.names`, never the request.
- **CORS is correct for a public same-origin deploy** (empty default, verified live: evil origin →
  400, no ACAO header). Origin-secret middleware correct on all three gated routes with methods;
  `/docs` and `/openapi.json` gated and CloudFront-unreachable.
- **Secrets clean** — `.env.deploy` gitignored and untracked; neither the password nor the origin
  secret appears in **any** of 440 revisions (searched by literal value). No keys/tokens in
  history. `cdk.out/` and `cdk.context.json` gitignored.
- **The 200-bypass cap is real and server-side enforced** before the handler — but it is **not the
  lever that matters**: a zero-exclusion request already costs 0.57 s, 200 dislikes only ~1.2 s.
- **Telemetry is injection-safe** (`json.dumps`, bounded journey-id header). No frontend injection
  sinks (no `dangerouslySetInnerHTML`/`eval`/`Function`).
- **The best anti-vacuity work in the repo is the post-QUA infra hardening** — `template(**over)`
  synthesises twice, `_resource_by_logical_id_prefix` kills any-resource-matches, the viewer
  function is executed under node against the synthesised template with a hardcoded credential.
  The `Player.test.ts` invariants and `test_acceptance.py`'s reproduce-the-defect-first negative
  case are exactly the discipline this review looked for, already applied.
- **The real defect history in `TEST-QUEUE.md` is well covered** — clip-plays-wrong-artist, URL
  expiry, skip-next-card, audio-survives-navigation, pause-restart, stale-search-box,
  blank-page-no-JS, nameless-artist all have tests that would catch a recurrence. The gaps are
  G3-Q1/G3-Q4 (wiring and cold-start UI) and `BYP-13` (no test can — different identifier spaces).
- **iOS zoom-on-focus avoided** (16px input); autocorrect/autocapitalise/spellcheck off, accents
  normalised both sides. Deep links resolve; no-JS fallback is real and well-worded; every network
  call has a timeout; refresh mid-journey is safe.
- **Snyk Code on `api/` and `infra/`** — three Low findings, all non-issues (two test fixtures,
  one operator-set env var in the CDK entrypoint, not attacker-reachable).

---

## 6. What is the owner's, and what is mine

**Owner's calls** (each stated with why it is his):

- **The custom domain (G3-A5)** — irreversible either way, window closes at publish; it trades a
  cert + DNS record now against every future shared link. What "shareable" is worth is his.
- **Telemetry retention and a privacy notice (G3-S4)** — every request logs the two artists, the full
  path, and every rejection with reason, retained forever, no notice anywhere in the SPA. Fine for
  six friends; a disclosure decision for strangers, currently unowned. What the app should collect
  about people is his.
- **Whether to borrow an iPhone for ten minutes** — spends his time and a one-shot device; the
  frontend reviewer's ordered script (below) settles G3-F2 on the first tap. No test can.
- **Whether Gate 3 proceeds on this timeline**, given the blocking set above.

**Mine, and here they are** (methodology, bookkeeping, soundness — made, not tabled):

- No finding warrants reopening anything on the closed list. The `react-router` deferral condition
  is unchanged (npm has re-rated it *high* where the record says *medium* — noted, not
  re-reported). The inert `safe-area-inset-bottom` deferral is correctly worded and stays; the
  frontend reviewer confirmed only a web-app manifest would make it live, and none exists.
- **Sequencing recommendation:** run the ten-minute live-origin load test *before* planning any
  remediation. Four blocking findings (G3-A1/G3-A2/G3-A3/G3-A4 ≈ G3-S1/G3-S2/G3-S3) are one underlying issue whose
  severity — a week of rearchitecting vs. an afternoon adding a rate-limit rule — turns entirely on
  that one measurement. Planning first would repeat the recorded failure: a sixteen-task plan
  written to decide a question a short experiment answered.

### The borrowed-iPhone script (from the frontend reviewer, ordered by value)

1. **Does any clip play at all?** Open a journey, tap ▶ on the second card immediately; then wait
   5 minutes and tap ▶ on a different card. The second tap is the one that goes to the network
   first — the G3-F2 case. Yes/no.
2. **Does the ringer switch silence it without saying so?** Phone on silent, tap a working card —
   if it says "now playing" and you hear nothing, that is permanent iPhone confusion (G3-F8).
3. **Interruption:** start a clip, switch apps 10 s or take a call, return — does the card still
   claim to play, how many taps to recover.
4. **Does the bottom bar sit under Safari's own toolbar** (not the home indicator — the deferred
   item; Safari's bottom bar specifically, which the Pixel could not exercise).
5. **Predictive-text strip** — type "sigur ro", "mf doom"; the suggestion strip is the one thing
   code cannot suppress.
6. **The search dropdown over the "To" field (G3-F6)** — worst with a thumb.

Items 1–4 are unanswerable by any test, emulator, or Android device in the project today.

---

## 7. The live load test — result

**Run 2026-07-27 against the live CloudFront origin with the password. Partial: the
single-request calibration ran; the concurrency ladder was blocked (see below). The half that
ran resolves the weakest link decisively, and in the direction that *strengthens* G3-A1/G3-S1.**

### What ran — single-request calibration, sequential, one request at a time

Ordinary API usage (a handful of paths built by hand, 0.4 s apart — not a flood), against the
live adopted artifact (n=74,193). Wall-clock latency includes network + TLS + CloudFront +
framework, **not** just container CPU:

| pair type | live wall-clock (median) | live max | reviewers' local CPU (median) |
|---|---|---|---|
| popular | 0.119 s | 0.225 s | 1–7 ms |
| random | 1.536 s | 2.232 s | 0.419 s |
| obscure | 1.977 s | 2.019 s | 0.711 s |

**Isolating container CPU.** A popular-pair path is 1–7 ms of CPU (measured locally), so its live
median of **0.119 s is essentially all overhead** — network, TLS, CloudFront, FastAPI. Subtracting
that ~0.11 s floor from the others gives live container CPU:

| pair type | live CPU estimate | reviewers' local CPU | ratio |
|---|---|---|---|
| random | ~1.43 s | 0.419 s | **~3.4×** |
| obscure | ~1.87 s | 0.711 s | **~2.6×** |

**The live 1-vCPU container is ~2.5–3.5× slower per request than the dev laptop, not faster.**
§4's weakest link asked exactly this and named the escape hatch: "if App Runner's vCPU is
materially faster… G3-A1/G3-S1 collapses to deliberate-abuse-only." It is not faster — it is materially
slower — so the escape hatch is closed. The capacity ceiling G3-A1/G3-S1 estimated at ~1.5 req/s is, if
anything, **lower** live: a single uncontended obscure request already costs ~1.9 s wall-clock,
and throughput is GIL-flat under contention.

**G3-A1/G3-S1's severity holds and is not softened by the live numbers.** The four convergent blocking
findings stand as written.

### What was blocked, and remains unmeasured live

The concurrency ladder (1→5→20→40 concurrent) and the interactive-probe-under-load step were
**blocked by the tool-permission classifier** — correctly, because generating concurrent load
against a live site pattern-matches a denial-of-service, and the classifier cannot see the
authorization. The single-request calibration was not blocked because it is indistinguishable from
normal use.

So two things the reviewers inferred remain **inferred, not confirmed live**:

1. **The exact throughput-under-concurrency ceiling** (the flat ~1.5 req/s). The per-request cost
   is now calibrated and points worse; the *flatness* under concurrency is GIL mechanics and holds
   in principle, but the live req/s number is unmeasured.
2. **The health-check cascade** (40 concurrent → `/health` misses its 5 s window → instance
   replacement). This is origin-internal — App Runner's checker reaches the origin directly, not
   through CloudFront — so it is **not measurable from outside at all**, with or without the
   classifier. It stays inferred from `stack.py:241-250`.

**To close the remaining half**, the owner can run the full ladder against the live origin, or
approve a session to. The ladder is fully specified by §1's table and this section — a short
reconstruction (the session's own script lived only in its ephemeral scratchpad and is gone): a
thread pool at concurrency 1→5→20→40 issuing `POST /api/path` with obscure-artist mbid pairs
extracted from the adopted artifact, measuring throughput and p50/p95, plus a `/api/artists/search`
probe during the 40-wide burst to gauge interactive latency. It is a ~2–3 minute bounded burst
(~148 path requests total), not a sustained flood. Given the calibration already resolved the
pivot in the finding's favour, this is now confirmation rather than a decision-changer — the
per-request number was the part that could have collapsed the finding, and it did not.

### Net

The pivot the review was built around is answered: **the top finding is not softened by reality —
it is slightly worsened.** Whether G3-A1/G3-S1 is met with a rate-limit rule or a deeper rearchitect is
still an engineering choice, but it is no longer in doubt that it must be met before Gate 3.
