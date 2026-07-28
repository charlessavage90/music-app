# Frontend mockup adoption — execution log, 2026-07-28

**Role: ACTIVE — Tasks 1–7 of 13 complete.** The retained record for
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
