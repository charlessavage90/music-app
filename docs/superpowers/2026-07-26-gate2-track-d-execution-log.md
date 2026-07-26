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

## 11. What this does not cover

- **No real phone has run this.** The layout is verified at a 390 × 844 **emulated** viewport
  in headless Chromium. Safari's rendering, the iOS keyboard actually honouring
  `autocorrect="off"`, and `env(safe-area-inset-bottom)` resolving to a non-zero value on a
  notched device are all **unverified** — the emulator reports zero for the inset. That is the
  queued use-the-app entry's job and it is the reason it asks for a phone specifically.
- **The timeout copy has never been seen in use**, because provoking it needs a server that
  accepts and never answers. It is unit-tested and visually unverified.
- **`TKD-3` is fixed for this machine's OneDrive layout.** A checkout outside OneDrive never
  had the problem and is unaffected either way.
