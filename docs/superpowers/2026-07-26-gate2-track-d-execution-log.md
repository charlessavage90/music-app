# Gate 2 — Track D execution log, 2026-07-26

**Role: COMPLETE.** The record of Track D — the frontend track — executed 2026-07-26 from
[`plans/2026-07-26-track-d-frontend.md`](plans/2026-07-26-track-d-frontend.md). Identifiers
are namespaced **`TKD-`**; checked against `TKA-`, `TR-`, `DEP-`, `FMS-`, `CLM-`, `STC-`,
`CNS-`, `MKS-`, `SYN-`, `CWD-`, `DRV-`, `BYP-`, `ASC-` and `TF-` — no collision.

**Touches no routing weight, no cost-function term, no graph, no `ApiConfig` default.**
`api/` and `builder/` were not edited; their suites are unchanged at 180 and 115, which is
the check rather than the claim. **The path-quality pause is intact and this track is not a
resume signal.**

**Suites:** frontend **65 → 77**, e2e **3 → 4**, api 180, builder 115. Snyk `snyk_code_scan`
on `frontend/`: **0 issues**. Eight tasks, executed inline, all seven fenced items landed.

---

## 1. What was built

Seven items — the owner's six (`TR-16`) plus a seventh he accepted the same day after
running the Track A use-the-app entry.

| task | item | commit |
|---|---|---|
| 1 | Responsive layout | `2347a56` |
| 2 | Typing over a chosen artist un-chooses them | `d01e75d` |
| 3 | Search failure vocabulary | `38df398` |
| 4 | iOS input attributes | `bafd110` |
| 5 | Request timeouts and a retry | `5a0c27f` |
| 6 | Surfacing a refused `play()` | `d14ecaf` |
| 7 | Catch-all route | `110ab88` |

## 2. `TKD-1` — `TR-16`'s evidence was wrong and its conclusion was right

`TR-16` states that `grep` over `frontend/src` returns **zero** hits for any breakpoint or
media query. **It returns six**, all `@media (max-width: 1024px)`, in `src/App.css`. The
conclusion survives intact, because `App.css` was imported by nothing and none of its
selectors (`#center`, `#next-steps`, `#docs`, `#spacer`) existed in any component: dead Vite
scaffold, deleted in Task 1.

**The consequence is the part worth keeping.** Any verification of the layout fix phrased as
"grep for a media query" **would have passed before the fix**. That is the `FMS-P1` / `TR-2`
vacuous-check pattern, and it is why Task 1 was verified by measuring rendered geometry in a
real browser instead. `TR-16` also lists safe-area insets among the zero hits and is right
there — but `index.html` already carried the viewport meta tag, so nothing blocked responsive
CSS from taking effect.

## 3. `TKD-2` — the spec written to avoid the vacuous-check pattern reproduced it

**Task 1's e2e spec passed on its first RED run.** The plan warns about this pattern three
times; it happened anyway, in the one task written to prevent it.

The cause: the spec measured `page.locator('ol li .font-semibold').first()` — the **first**
card, which is a journey **endpoint**, and endpoints carry no bypass buttons. Those buttons
are precisely the non-shrinkable elements that cause the squeeze. At 390 px an endpoint card
needs ≈ 160 px against ≈ 338 px available and was never broken; an interior card needs ≈ 377
px and is. Assertion 3 had used `.nth(1)` correctly, so one assertion in the same spec was
already on the right element.

Every assertion now targets an interior card. **What caught it was running the RED, not
review** — the spec is self-consistent and reads correctly.

**Also recorded: the page-level horizontal-overflow assertion passed both before and after.**
Flex children with `min-w-0` shrink rather than overflow, so the page never scrolled
sideways even at zero name width. It is retained as a guard against a future fixed-width
regression, but it is **not** the assertion that carries this spec, and it should not be
quoted as evidence the layout was ever fixed.

## 4. `TKD-3` — `DEP-30` was not fully fixed, and it blocked this task

Track A moved Playwright's `outputDir` from `frontend/test-results` to `../.playwright-results`
to escape OneDrive's file locking. **The repo root is under OneDrive too.** The run therefore
still fails with `EPERM: operation not permitted, rmdir` whenever a previous run left
artifacts behind — observed on **two consecutive runs** here, blocking Task 1's verification
until cleared by hand.

That defeats `DEP-30`'s own stated purpose, quoted in the config it patched: *"a manually-run
regression gate that errors on its default invocation is a gate people stop running."* It
errored on its default invocation; it just needed a prior run to do it.

Now `os.tmpdir()`, which is genuinely outside sync — the same reasoning and the same remedy
as `vite.config.ts`'s `cacheDir`, which carries a comment saying exactly this. **`DEP-30`
should be read as discharged only from this commit**, not from Track A's.

## 5. `TKD-4` — the seventh item, and what it actually was

Found by the owner in ordinary use, 2026-07-26, and **misattributed in the first telling in
two ways that both matter**:

- **It is not a race with the autocomplete.** The owner reported it as "click Find Path
  before the search box populates". Waiting for the dropdown does not help: `onSelect` was
  called from exactly one place, `choose()`, which runs only when a dropdown entry is
  **clicked**. Text and selection were separate state and nothing reconciled them. So
  "make search faster" would have fixed nothing, and a test written around the debounce
  timer would have tested the wrong thing.
- **The "New path" prefill did not introduce it.** `git log -S` puts the divergence in
  `56aac27`, the original landing page; `fd3b771` added only the `initial` seed. Before the
  prefill both boxes started empty, so the button started disabled and you had to pick from
  the dropdown at least once — the same stale window existed after that first pick, it was
  just much harder to reach. Reverting or reworking the prefill would not have fixed it.

The fix widens `onSelect` to `Artist | null`. **The button going dead is the signal** — no
new copy was added, because the disabled control already says it.

**RED evidence:** `Received element is not disabled`, twice. That is the defect stated
exactly.

## 6. `TKD-5` — a refused `play()` goes through the existing error channel

`Player.play()` discarded the promise, so an autoplay-policy refusal or a decode failure left
a card asserting "▮▮▮ now playing" over silence.

It is routed into the **existing** `onError` channel rather than a new one. `usePlayer.onError`
already owns the right response — one silent retry with a freshly signed URL, then clear —
and the team review confirmed all four player invariants hold there with unit coverage. A
second failure channel would have needed its own retry policy and would have put those
invariants back in play. From the journey's side a refused `play()` and a dead source are the
same event: no audio is coming.

**Do not "simplify" this into a separate callback.** Both e2e playback specs were re-run
green against the real service after the change, in addition to the unit suites.

## 7. `TKD-6` — the timeout values are chosen, not measured

8 s search, 20 s path, 10 s track. Path is longest because Dijkstra at depth plus a cold App
Runner instance is the slow case. **No measurement backs these**, and the honest condition for
revisiting them is the telemetry `duration_ms` field Track A added having real data. That is a
Gate 3 note.

The wrapper uses its **own** controller and throws `TimeoutError` rather than aborting the
caller's signal. This is load-bearing and easy to undo by accident: `usePath` returns early
when it sees its own signal aborted, so a timeout that aborted the caller would be silently
swallowed and the page would sit on "Building your path…" forever — the exact defect being
fixed. A pinning test holds that line.

**RED evidence:** `Test timed out in 5000ms` — the request hung and nothing cut it off, which
is the defect itself rather than a proxy for it.

## 8. `TKD-7` — a suite count that did not match, and was not made to match

Task 7 ended at **77**, not the **78** its plan entry predicted. Investigated rather than
closed by adding a test, per the plan's own instruction that a mismatch is a signal and not a
number to make true.

The plan budgeted Task 7 at two tests and its Step 1 specified one. Summing what was actually
added — 3 + 2 + 1 + 3 + 2 + 1 = 12 — against a measured baseline of 65 gives 77, and the test
**file** count is unchanged at 12. So nothing was lost; the budget was wrong. **77 is the
correct total** and supersedes the plan's 78 wherever they disagree.

## 9. `TKD-8` — two tests passed before their fix, and both are recorded as guards

Per the `TKA-2` precedent, a knowingly-passing check is named rather than allowed to look
like a RED run:

- **"a caller's own abort is not reported as a timeout"** (Task 5) passes pre-fix because the
  caller's signal was previously passed straight through. It guards `TKD-6`'s distinction.
- **"a rejected `play()` on a disposed player reaches nobody"** (Task 6) passes pre-fix
  because nothing reached anybody. It guards the disposed-player invariant against the fix
  that makes rejections reach *somebody* — the exact invariant most at risk from Task 6.

Neither is evidence that its task worked. The tests that are: the two named in §5 and §7.

## 10. Decisions taken against

Recorded because they leave no other artifact.

- **A jsdom test for the responsive layout.** jsdom computes no layout and applies no media
  queries, so such a test could only assert class strings — implementation, not behaviour, and
  passing for the wrong reason. Hence the e2e. This is the reason Task 1 adds **zero** unit
  tests, which otherwise looks like an omission.
- **Duplicating the bypass buttons across breakpoints.** A `hidden sm:flex` / `flex sm:hidden`
  pair is the obvious way to build this and would have broken `e2e/path.spec.ts`: it resolves a
  bypass button by role inside `ol li`, and Playwright strict mode fails on a locator matching
  two elements. One copy, reordered with `order-last` + `w-full` and released by `sm:`.
- **Turning the bypass buttons into icons on phones** to keep one row. Rejected: "✕ Not for
  me" and "✓ I know them" are two signals the owner has said mean different things, and an
  unlabelled icon pair is where that distinction goes to die. This is the one genuine design
  decision in Track D and it is the owner's to overrule.
- **Fixing `vite.config.ts`'s triple-slash lint warning.** Pre-existing, unrelated, and
  outside the fence. It is the only lint output and it is not new.
- **Accessibility, link previews, path-latency work.** Fenced out by the owner at the review
  and deferred to Gate 3. Not revisited.

## 10a. `TKD-10` — closeout B3 found a vacuous test guarding a real hole

**The mutation check earned its place here, and it is the one item in this closeout that
changed shipped code.**

Two of Track D's tests passed before their fix and were recorded under `TKD-8` as guards.
B3 mutation-tested both:

- **"a caller's own abort is not reported as a timeout" — CAUGHT the mutation.** Genuine.
- **"a rejected `play()` on a disposed player reaches nobody" — SURVIVED it.** Removing the
  `!this.disposed` guard entirely did not turn it red. It passes because `dispose()` sets
  `errorCb = undefined`, so the call is a no-op regardless of the flag: **it passed via a
  different signal than the one it named**, which is this project's documented failure class.

**Diagnosing why exposed a real defect, not just a weak test.** Neither mechanism covers the
StrictMode revival path: `dispose()` clears the flag and the callback, then `onError(newCb)`
re-subscribes and *revives* the instance — so a rejection from the **superseded** `play()`
passes both checks and reaches the new handler, which buys it a retry. That restarts playback
after the page has navigated away, which is precisely the defect `dispose()` was built to
prevent and which `Player.ts`'s own class docstring describes. Reached by a different route.

**RED evidence:** `expected "vi.fn()" to not be called at all, but actually been called 1
times`.

**Fix:** `play()` captures the handler that is live at call time and fires only if it is
still installed *and* the player is not disposed. **Consequence worth keeping:** with the
capture in place the previously-vacuous test now also goes red under the same mutation, so
both tests are meaningful rather than one.

This is narrow — it needs a rejected `play()` in flight across a remount — and it was never
observed in use. It is recorded rather than downplayed because the class has bitten here
before.

## 11a. `TKD-9` — Track D's headline item cannot be tested by use until Track C

**Recorded because the first version of this track's use-the-app entry asked the owner to
open the app on his phone, and he cannot.** The app runs only on his Windows desktop; there
is no hosted URL, and a phone cannot reach another machine's `localhost`. The entry was
corrected before it was run and `TEST-QUEUE.md`'s header now carries a standing constraint
forbidding phone-dependent steps until cutover.

**The general shape is worth more than the incident.** Track D was ordered *before* Track B
so the deploy would ship a phone-usable app rather than putting a broken one in front of
friends (`DEP-29`) — which is sound, and unchanged. But it has a consequence nobody stated at
the time: **the verification of the responsive work necessarily comes after the thing it was
sequenced ahead of.** Track D can be built before the deploy; it cannot be *confirmed* before
it. Any residual risk in the phone layout therefore rides into cutover with it, and the honest
reading of "Track D is done" is *done and desk-checked*, not *done and confirmed in use*.

This is **not** an argument for reordering — building it first is still right, because the
alternative is shipping a known-broken phone layout. It is an argument for expecting a
follow-up entry after cutover, and for not treating the queue's silence in the interim as
evidence.

An optional bridge exists and was offered rather than taken unilaterally: binding the dev
server to the LAN so a phone on the same wifi can reach it. It needs a firewall allow and it
is the owner's call.

## 11. What this does not cover

- **No real phone has run this, and none can until the deploy** (`TKD-9`). The layout is
  verified at a 390 × 844 **emulated** viewport in headless Chromium. Safari's rendering, the
  iOS keyboard actually honouring `autocorrect="off"`, and `env(safe-area-inset-bottom)`
  resolving to a non-zero value on a notched device are all **unverified** — the emulator
  reports zero for the inset, so the space the player bar reserves has never been exercised.
- **The timeout copy has never been seen in use**, because provoking it needs a server that
  accepts and never answers. It is unit-tested and visually unverified.
- **`TKD-3` is fixed for this machine's OneDrive layout.** A checkout outside OneDrive never
  had the problem and is unaffected either way.

## 12. Closeout record, 2026-07-26

| item | outcome |
|---|---|
| **A1** distil log | This document. |
| **A2** handoff note | Written — `2026-07-26-HANDOFF-track-d-complete.md`. |
| **A3** deferrals addressed | Three, all with conditions: timeout values (revisit when `duration_ms` has data, Gate 3); phone verification (trigger: Gate 2 cutover, `TKD-9`); `vite.config.ts` triple-slash lint warning (pre-existing, accepted won't-fix). |
| **A4** default-flip | **Inapplicable, stated rather than skipped.** Track D added no config knob and no env var. `TIMEOUT_MS` is a module constant with one value, not a switch with a loser to delete. |
| **A5** processes released | Two detached listeners, **owned by no session** and started 18:51 — **71 minutes before HEAD**. Verified serving current code rather than assumed: the module served at `:5173` carries Track D's layout class (Vite reloads from disk), and Track D touched **no** `api/` or `builder/` file, so the API's boot-time code is current. **The start-time-vs-HEAD heuristic gives a false alarm for a hot-reloading dev server; what is served is the real check.** |
| **B1** doc audit | Run. Three HIGH, three MEDIUM, one LOW. Five actioned; one declined with reasoning; one escalated to the owner (below). |
| **B2** reachability | `NotFound.tsx` — the only module created — is imported and routed in `App.tsx:3,11`. No orphans. |
| **B3** vacuous-test check | **Found one.** `TKD-10`; the only closeout item that changed shipped code. |
| **B4** prose-versus-code | Checked the comments Track D wrote against their code. One was wrong and is fixed as part of `TKD-10` — the `!this.disposed` comment implied the flag was doing the work, and it was not. |
| **B5** stale-description sweep | **`.claude/` is clean** — the only hit is `closeout/SKILL.md`'s own `npm test` command. `docs/` had one genuinely stale claim, in a **live handoff**: `2026-07-26-HANDOFF-track-a-complete.md` asserted the repo-root `outputDir` "is the `DEP-30` / `TR-17` fix working". Struck in place. **The many per-run suite counts across older logs are NOT restatement violations** — each is a dated measurement inside its own record, not a copy of a figure owned elsewhere. |
| **C1** use-the-app | Queued, then **corrected** — see `TKD-9`. |
| **D1** clean tree | Yes. |
| **D2** fixtures | **Inapplicable** — no graph, artifact or builder change. |
| **D3** artifact provenance | **Inapplicable** — nothing adopted or compared. The running API serves the adopted artifact, sha256 owned by `findings/2026-07-23-tiebreak-fix-adoption.md`; not restated here. |
| **D4** suites | builder 115, api 180, frontend 78, e2e 4. Run, not remembered. |
| **D5** PR | #28. |
| **D6** standing layer | **`git diff --stat main..HEAD -- CLAUDE.md .claude/skills/ .claude/agents/` is EMPTY — Track D added zero lines.** `memory/` totals **474** lines against **469** last recorded (`CLM-7`, 2026-07-26); **Track D wrote none of it**, so the +5 predates this work and is noted for the next sweep rather than attributed here. One HIGH audit finding proposes *adding* to `CLAUDE.md`; it is the owner's call and was not taken. |

**Frontend suite is 78 at closeout, not the 77 recorded in §1** — `TKD-10` added one test. §1
records the count at the end of Task 8; this is the count after closeout.

### The one item escalated rather than actioned

The audit's third HIGH is that `CLAUDE.md`'s "next action" row does not say Track A and
Track D have executed, so a cold session cannot tell from the entry points alone that two
tracks are done and awaiting review. **The finding is correct.** It was not actioned because
the fix grows the budgeted standing layer, and `CLAUDE.md` is explicit that a session never
does that on its own authority. Cost: roughly two lines in an existing row. It is genuinely
maintenance of a row whose job is to change — which is the argument *for* — but that is the
owner's judgement, not this session's.

### One audit finding declined, with reasoning

The audit proposed reordering `TEST-QUEUE.md` so the retained original text of a DONE entry
sits below the newest entry's deferred section. **Declined:** the file's established
convention is newest-first with each DONE entry immediately followed by its own original text
(`*Original queued text follows.*`), used by every prior entry. Reordering one entry to
another rule makes the file less predictable, not more. **The real defect underneath the
finding was actioned** — two headings both claimed "(latest)", which is ambiguous at a glance;
the stale one now says so explicitly.
