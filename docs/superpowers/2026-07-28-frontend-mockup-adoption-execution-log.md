# Frontend mockup adoption — execution log, 2026-07-28

**Role: ACTIVE — all 13 tasks complete.** The retained record for
[`plans/2026-07-28-frontend-mockup-adoption.md`](plans/2026-07-28-frontend-mockup-adoption.md),
governed by
[`specs/2026-07-28-frontend-mockup-adoption-design.md`](specs/2026-07-28-frontend-mockup-adoption-design.md).
**Fresher than the plan on status; where they disagree, this wins.** Does not state project
status — that is [`NEXT.md`](NEXT.md).

**Owns no path-quality figures.** No routing, graph, cost function or weight was touched, and
the path-quality pause is intact.

Branch `frontend-mockup-adoption`, 9 commits, pushed.

---

## 1. State at the seam — end of Task 7

| | Before | After |
|---|---|---|
| Frontend unit tests | 80 in 13 files | **91 in 15 files** |
| API tests | 214 | **217** |
| Lint | 1 warning (`vite.config.ts`, pre-existing) | **1 warning, same one** |
| Snyk (`frontend/src`, `api/src`) | — | **0 issues, both** |

**This table is the only copy of these counts.** Three documents restated the equivalent
figures during the password-removal work and disagreed until the doc audit caught it; cite this
section rather than copying from it.

The 11 new frontend tests are: `useEndpoints` 3, `PlayButton` 4, `ArtistCard` 3, `LandingPage` 1.
The 3 new API tests are the artist-lookup route's.

**What is visible in the app and what is not.** The landing screen is finished at both widths and
every card on the journey carries the mockup's treatment. **The loading screen and the reroll
message are built but not wired** — Task 12 does that — so the path page still renders the old
`Building your path…` line. Nothing is broken; the redesign is simply not visible end to end.

## 2. Decisions

The nine owner decisions are recorded in the spec's §2 and are **not restated here**. What
follows is what execution decided.

- **The Snyk scan ran at the seam rather than at Task 13**, where the plan put it. Deferring it
  would have pushed a standing security instruction across a session boundary for no gain, and
  it costs two tool calls. Both packages clean.
- **The committed design export was excluded from oxlint** (`frontend/.oxlintrc.json`,
  `ignorePatterns: ["design/**"]`). Committing it per `UI-1` put four files we do not own into
  the linter's path and added eight warnings to every run. Neither the spec nor the plan
  anticipated this; it is a consequence of `UI-1` rather than a defect in it.
- **A comment key in `.oxlintrc.json` was reverted.** oxlint's schema rejects unknown fields,
  including `//`. Worth knowing: **`npm run lint` exited 0 while failing to parse its own
  config**, so a malformed lint config is silent here.

## 3. Defects found in the plan itself

Distinct from defects in the code. All three are corrected in the plan or were corrected in
flight.

1. **`w-13 h-13` is not a Tailwind default size.** Caught by the plan's own self-review before
   execution and corrected in place to `w-[52px] h-[52px]` in Tasks 7 and 9. Task 9 is unrun —
   **the successor must apply the same correction there**, and the plan says so at the code block.
2. **Task 5's test snippet assumed a bare `render` with `MemoryRouter`.** `LandingPage.test.tsx`
   actually has a `setup()` helper. The real helper was used. This is the **same class** as the
   `renderAt` imprecision the plan's self-review flagged for Task 12 — and it means that flag
   should be read as a general instruction rather than a note about one file: **read the test
   file before writing tests into it.**
3. **The plan's Task 13 was the only place Snyk appeared**, which put it after the seam. Moved.

## 4. Closeout findings against this session's own output

**`B3` found a vacuous test, and it was mine.** This is the finding of the session.

`useEndpoints.test.tsx` carried a test named *"a failed lookup yields nulls and never throws"* —
the test guarding `UI-7`, which is the rule that a decorative name lookup must never be able to
turn a working page into an error page. Mutation testing removed the `.catch(() => null)` that
*implements* `UI-7` and **the suite stayed green at 3/3**.

The mechanism is the documented one: when `Promise.all` rejects, `.then` never runs, so state
stays at its **initial** value of `null` — which is precisely what the assertion read. The test
would have passed against code with no error handling whatsoever.

Fixed by making the case **mixed** — one lookup fails, one succeeds — and asserting the
*surviving* one still lands, which can only happen if the failure was swallowed per-promise.
Verified in both directions: green on correct code, red with the catch removed.

> **A both-fail test cannot be made non-vacuous here**, because the failure state and the initial
> state are byte-identical. That is now a comment in the test file, so the obvious "improvement"
> is not made later.

Two things this is worth recording for:

- It is the **fifth** documented instance of this class on the project, and the first found by
  mutation rather than by review. Review had already passed it — I wrote it, read it back, and
  committed it.
- **It was written test-first and went red before implementation.** A red-first test is not
  automatically a real test: this one went red because the module did not exist, not because the
  behaviour was absent. Red-on-missing-module is a weaker signal than red-on-wrong-behaviour, and
  nothing in the TDD cycle distinguishes them.

**`B2` reachability: `useEndpoints` has no non-test importer.** Expected at this seam — Task 12
wires it into `PathPage` — and named here so a cold session finding an unimported hook does not
have to guess whether it is unfinished or abandoned. It is unfinished. `PlayButton` is imported
by `ArtistCard`.

## 5. Corrections to the prior record

**None.** No previously-recorded claim was overturned by this work.

## 6. Gate outcomes

| Gate | Outcome |
|---|---|
| Existing tests pass unchanged at every task | **PASS** — checked per task; 80 → 91 is purely additive |
| `getByLabelText('From')` survives the uppercase label | **PASS** — `UI-3`'s CSS-only approach held, 6/6 unchanged |
| Build (`tsc -b` + Vite) | **PASS** |
| Snyk, both packages | **PASS**, 0 issues |
| `docs-lint.sh` | **3 hard failures, all mine, all fixed** — the plan lacked a role marker, and neither new document was classified in `docs/README.md` |
| e2e suite | **NOT RUN.** Needs a live API and is scheduled at Task 13. |

**The unrun e2e gate is the honest weak point of this seam.** `e2e/responsive.spec.ts` is the
only thing that exercises the `UI-5` locator change at a real 390px viewport, and jsdom computes
no layout — so 91 green unit tests are entirely consistent with a card that looks wrong on a
phone. Nothing here has been seen in a browser.

## 7. Measurements with no other home

- **DM Sans self-hosted**: two woff2 subsets, 18.22 kB (latin-ext) + 36.93 kB (latin) = 55.15 kB.
  Replaces two `preconnect`s and a stylesheet request to `fonts.googleapis.com`.
- **Production JS** 247.48 → 250.55 kB (gzip 79.21 → 80.20). **CSS** 17.10 → 24.93 kB
  (gzip 4.38 → 5.73).
- **D6, the standing context layer.** Unconditional **43,692 characters**; conditional
  **2,120 lines**. **Both deltas exactly 0** — this work touched no `CLAUDE.md`, no `.claude/`,
  no `memory/`. Baseline is the password-removal log's §D6 table, and it is directly comparable.
- **A5, processes**: ports 8000, 5173, 8138 and 8139 all free at the seam. Nothing was started by
  this session and nothing was left running.

## 8. What the successor must not get wrong

1. **Do not "improve" the mixed failure test in `useEndpoints.test.tsx`** back into a both-fail
   test. The comment explains why; §4 above is the evidence.
2. **Apply `w-[52px] h-[52px]` in Task 9**, not the plan's `w-13 h-13`.
3. **Read `PathPage.test.tsx` before writing Task 12's tests.** The plan names `renderAt`; verify
   its real signature. Task 5 hit exactly this and the plan's snippet was wrong.
4. **Do not add `viewport-fit=cover`** (`UI-D3`). The `env(safe-area-inset-bottom)` in
   `PlayerBar.tsx` is deliberately inert and the deferral in `NEXT.md` stands.
5. **`UI-8`: this work will be the next FRONTEND publish**, which is the `--prune` deferral's
   trigger — `infra/src/artistpath_infra/sync_frontend.py`, not the next `cdk deploy`.

---

# Tasks 8–13 — second session, 2026-07-28 (night)

Picked up cold from the Task 7 seam handoff. **All five items in §8 above were applied**; the
`renderAt` warning (§8.3) was checked and **resolved in the plan's favour** — the helper exists
at `PathPage.test.tsx:19` with the signature the plan assumed. Verifying it cost one grep and
is the only reason that is known rather than assumed.

## 9. Final state — all 13 tasks

| | At the seam | Now |
|---|---|---|
| Frontend unit tests | 91 in 15 files | **107 in 18 files** |
| API tests | 217 | **217** (no API code touched) |
| e2e | **NOT RUN** | **5 passed** — the seam's honest weak point, now closed |
| Lint | 1 warning (`vite.config.ts`, pre-existing) | **1 warning, same one** |
| Snyk (`frontend/src`, `frontend/e2e`) | — | **0 issues, both** |
| Production JS / CSS | 250.55 kB / 24.93 kB | **256.74 kB / 27.57 kB** (gzip 81.74 / 6.26) |

**As with §1, this table is the only copy of these counts.** The 16 new tests are:
`PathSkeleton` 3, `RerollNotice` 4, `PathIntro` 5, `PathPage` 4.

## 10. Defects found in the plan's Tasks 8–13

Three, all in test code, none in the design. The plan's own self-review predicted the *class*
of the second and third but not the instances.

1. **Task 11's two count assertions could never have passed.** The plan asserts
   `getByText(/in 3 steps/i)` against a sentence its own component splits across three text
   nodes — the count sits in its own `<span>` for the brighter colour. `getByText` matches a
   node's **own** text children, so no element's text ever reads "in 3 steps". The component is
   right and the assertion was wrong; both now read the line's `textContent`. **Mutation-checked**
   by dropping the plural, which turned it red — this file's standing rule after the vacuous
   `UI-7` test (§4).
2. **Task 12's three test snippets called `renderAt` before spying on `buildPath`**, so they
   would have hit the real client and hung. Rewritten in the file's existing style. A fourth
   case was added pinning that the message names the signal **actually pressed** — the plan
   tested `dislike` only, and the whole point of the feature is that the two buttons differ.
3. **The plan says Task 12 leaves "the existing eight" passing.** There are **seven**.

## 11. The e2e failure, which was a test defect and not the app

`path.spec.ts` failed on first run: it demanded the bypassed artist disappear, and found
`Miles Davis` — the **start** endpoint, which can never be removed.

**Cause.** The spec located the artist name with `page.locator('ol li .font-semibold').nth(1)`.
Task 8 added the endpoint eyebrow ("STARTING ARTIST"), which is **also** `font-semibold`, so
`.nth(1)` silently became the *first* card's name instead of the second's. Fixed to
`getByTestId('artist-name')`.

**This is the same coupling `UI-5` fixed in `responsive.spec.ts`, in a file the fix missed** —
and it was invisible at the seam precisely because e2e was the one gate not run there. The
lesson is not "check the other spec": it is that **a deferred gate hides the defects its own
work created**, and this one was created by the task committed immediately before it.

## 12. Seen in a browser — the seam's weak point, closed

The seam recorded that **nothing had been seen in a browser** and that 91 green jsdom tests were
consistent with a card that looks wrong on a phone. Six screens were captured against the live
API (adopted 75k artifact, sha256 `4cb84ef9…`, verified against `/health` rather than assumed):
landing at 1200px and 390px, the skeleton, the journey at both widths, and a held path mid-reroll.

All six render as designed. **One cosmetic observation, deliberately not changed:** on a first
visit the reroll notice (`pt-24`) lands over the **open explainer** rather than over the journey,
because the explainer occupies that space until dismissed. It is the design as drawn, it
self-corrects once "Got it" is pressed, and moving it is the owner's call — queued as such.

## 13. What a successor must not get wrong

1. **The `--prune` deferral is now due on the next publish of this branch**, not on the next
   `cdk deploy`. `infra/src/artistpath_infra/sync_frontend.py`.
2. **Two servers were left running deliberately** so the queued test is runnable: API on `:8000`
   (PID 93400) and Vite on `:5173` (PID 274380), both started after HEAD. They are recorded in
   the queue entry and owned by nobody.
3. **The iPhone script is still unrun and still owed.** It was carried forward into the newest
   queue entry; nothing in this work touches or answers it.

---

# Owner changes and the deploy — same session, 2026-07-28 (night)

The owner used the local build, asked for three changes, added one telemetry field, and
approved the deploy. All of it landed in the same session as Tasks 8–13.

## 14. What the owner changed after using it

Three cosmetic/copy changes (`UI-14`) and one telemetry change (`UI-15`).

- **The landing clip-length line was removed**, the decorative three-dot rail above it kept.
  The test was **inverted rather than deleted** — it now asserts the line is absent, so
  restoring it is a deliberate act rather than an accident.
- **The landing intro was rewritten.** The brief was to explain the **how** at user level and
  tie to coherence, explicitly **not** to promise obscurity. That bound is the owner's and it
  is correct: the first path between two famous artists is expected to be famous
  (`WHAT-GOOD-LOOKS-LIKE.md` value 9), so a front page promising unfamiliar artists writes a
  cheque the first screen does not cash. Obscurity is introduced by the bypass explainer on
  the journey page, which is unchanged.
  - **The old sentence described the wrong product.** "Name two artists and hear a smooth
    path between them" names only smoothness, which is `WHAT-GOOD-LOOKS-LIKE.md`'s
    description of **boilthefrog**'s goal; this project's is "smooth *and* progressively
    unfamiliar". Noticing that is what produced the option set.
  - **`listeners share` was verified before shipping, not assumed** — edges come from
    ListenBrainz similar-artists (`builder/…/sources/listenbrainz.py`) and every edge in the
    artifact is behavioural (`graph_store.py:150`). The claim on the front page is literal.
- **The journey rail spans full height and the arrow at its foot is gone.** The loading
  screen's rail was deliberately **left alone** — it is a different element that animates
  top-to-bottom and never carried the arrow.
- **`path_length` is now logged as an explicit integer.** Log Insights cannot aggregate over
  the length of a JSON array, so every `by path_length` query previously needed an offline
  pass. **It is not a `DEP-7` metric**: it is cardinality of the response, not a scoring
  choice, and `bypass_depth` is the exact precedent — also an integer count of an array that
  is itself logged in full.

**Spec §7's copy table was annotated, not rewritten.** That table is frozen so a *session*
cannot reshape copy to fit what it built; it is not a constraint on the owner changing his
own product. Both old strings are struck through in place with the reasoning beside them.

## 15. The deploy

PR #43 merged to `main` as `d68ef7a`; image `d68ef7a`; SPA published. Docs followed on
`post-deploy-doc-sync` (PR #44).

**`cdk diff` before deploying was worth the two minutes**: it showed exactly one change, the
App Runner image tag `37d559e` → `d68ef7a`, which established in advance that this was an
in-place **update** and not a service replacement — the condition the App Runner tag deferral
keys on. Confirmed after the fact by reading the tags back.

| Gate | Outcome |
|---|---|
| `cdk deploy` | **PASS** — `UPDATE_COMPLETE`, 171.3 s, no IAM or security-group diff |
| §8, the site refuses | **PASS** — site root `301`, App Runner direct `403` (`TR-7`) |
| §8, graph identity, mechanical | **PASS** — live `/health` matches the sidecar on sha256, artists and edges |
| §8a, the front door **admits** | **PASS** — root `200`, `TR-5` SPA fallback on a cold journey link, `/api/*` `200` |
| §8a, old address still works | **PASS** — `301` with query string intact, follows to `200` |
| App Runner CLI tags | **PASS** — survived; deferral tested and **did not fire** |
| New route live through the front door | **PASS** — `GET /api/artists/{mbid}` |
| Live bundle is this build | **PASS** — served `index.html` names `index-BLZUsNpG.js`, matching the local build hash |
| Browser on the live site | **PASS** — renders correctly, **zero console errors** |

**The strongest check is not in the runbook.** A journey built against production returned the
**identical eight artists in the identical order** as the same journey locally — which is
direct evidence for the claim every queue entry has had to make on trust, that routing did not
move. Recommend adding it to §8; it costs one `curl` and it is the only check here that tests
the thing users would actually notice.

**`path_length` was verified end to end**, not merely deployed: a real journey against
production was read back out of CloudWatch as `"path_length":8`, agreeing with its
eight-element array.

**Both environment traps in `memory/deploy-environment-traps.md` fired exactly as recorded** —
the AWS CLI is not on the shell PATH (it is at `C:\Program Files\Amazon\AWSCLIV2\aws.exe`),
and the `/aws/apprunner/...` log-group name needs `MSYS2_ARG_CONV_EXCL='*'` or MSYS rewrites
it into a Windows path. The memory was correct on both and cost nothing to apply.

## 16. Measurements

- **Deploy**: CloudFormation 171.3 s; total `cdk deploy` 189.4 s.
- **Production routing**: `duration_ms 21.31` for an 8-artist path at `bypass_depth 0`.
  ⚠ `duration_ms` times the Dijkstra call **only** — not clip resolution and not transport —
  so it is not comparable to how long the page feels.
- **Bundle after the owner's changes**: JS 256.52 kB (gzip 81.72), CSS 27.45 kB (gzip 6.24).
- **Suites at closeout**: builder **115**, api **217**, frontend **107 in 18 files**.
- **D6, the standing context layer**: unconditional **43,692 characters**; conditional
  **2,120 lines**. **Both deltas exactly 0** against §7's baseline — no `CLAUDE.md`, no
  `.claude/`, no `memory/` was touched by any of this.

## 17. Deferrals — state at closeout

| Deferral | State |
|---|---|
| The `--prune` publish pass | ⚠ **TRIGGERED, and now owed as a SEPARATE LATER RUN.** The publish deliberately omitted it: `infra/README.md` §6 is explicit that pruning *during* a publish re-opens the `FRO-1` blank-page window for anyone mid-visit. `NEXT.md` carries the corrected wording. |
| App Runner CLI tags vanish if the service is replaced | **Tested against reality and did not fire** — the service was updated, not replaced; `app=musicapp` read back present. |
| Rate-limit headroom before sharing beyond friends and family | Unchanged. Not due. |
| Front-door secret rotation; `react-router` CSRF; `env(safe-area-inset-bottom)`; chunked-body bounding; `G3-S4` disclosure | All unchanged and none came due. |

**`UI-D3` held throughout**: `env(safe-area-inset-bottom)` is still inert and
`viewport-fit=cover` is still absent.

## 18. Closeout findings against this session's own output

**Three, and the pattern across them is that the mechanical checks passed on all three.**

1. **`B5` — `docs/README.md`'s row for the demoted handoff restated its own stale status.**
   The `HISTORICAL` banner was prepended and the old row body survived, so one row asserted
   both "superseded and spent" *and* "Tasks 8–13 are not started, and nothing is deployed".
   `docs-lint.sh` passed it: a row can be internally contradictory and satisfy every
   mechanical check, because each half is individually well-formed.
2. **`B1` — the plan and the spec were still marked `ACTIVE` after the deploy**, the plan
   still reading "Tasks 8–13 are outstanding". Found by `doc-auditor`, both HIGH, both real.
   **The session had already updated `docs/README.md`'s rows for these same two documents**,
   so the map said COMPLETE and the territory said ACTIVE — and the territory is what a cold
   session opens first.
3. **`B4` verified the load-bearing prose rather than assuming it.** `RerollNotice`'s comment
   claims `dislike` penalises the *neighbourhood* decaying over `avoid_radius`, and `known`
   relaxes the floor *more aggressively*. Both true: `avoidance_map` decays over
   `cfg.avoid_radius`, and `floor_relax_known` (0.15) exceeds `floor_relax_dislike` (0.08).
   The user-facing explainer is therefore accurate to the router, which the spec requires.

**Finding 2 is the one worth carrying forward, and it is the third instance of this class
here.** A self-run grep could not have found it: nothing was *wrong* to search for, the role
lines were simply not updated. `CLAUDE.md` already records that "a grep for stale names cannot
find a name that is not there"; this is the same defect wearing a different hat — **a grep for
stale status cannot find a status that was never changed.** It is also a specific new failure
mode worth naming: **updating the index and not the indexed document**, which feels like
completion because the thing you were reading is now correct.
