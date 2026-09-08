# `UXR-` execution log — the Unsung.fm redesign

**Role: RETAINED EXECUTION LOG for `UXR-T1`–`UXR-T11`. ACTIVE. Owns no figures and no status**
(`NEXT.md` owns status). Appended per task: decisions and reasoning, never narration.
Plan: `plans/2026-09-08-unsung-redesign.md`. Spec: `specs/2026-09-08-unsung-redesign-scope.md`.

Executed inline by the session that wrote the plan (owner's "go", 2026-09-08), warm on every
file it touches; the plan's two handoff seams (after `T5`, after `T8`) are where a fresh
session takes over.

## §1 `UXR-T1` — tokens and faces

- `@fontsource-variable/space-grotesk@5.3.0` installed; both faces self-hosted (`UXR-D11`).
- The `@theme` block replaced wholesale with the role-named palette, plus ten aliases for
  the pre-redesign names (`UXR-D17`). The mechanical check — every `var(--color-*)` referenced
  under `src/` resolves to a definition in `index.css` — printed nothing undefined.
- Two keyframes added (`un-eq`, `un-sheen`) and a `.motion-safe-only` opt-out under
  `prefers-reduced-motion`, so the equaliser and the CTA sheen stop for people who asked them to.
- No behaviour changed; the suite is the check that nothing but colour moved.

## §2 `UXR-T2` — the name

- `Brand` is one accessible object (`role="img"`, `aria-label="Unsung.fm"`) wrapping a
  decorative `<img alt="">` and an `aria-hidden` split wordmark. **The plan's second
  assertion contradicted its own component** (it queried role `img` by name while the
  component carries exactly that role and name); corrected to assert the inner `<img>` is
  decorative and that only one `img` role exists. The plan's intent, not its letter.
- Title, no-JS fallback and favicon link renamed; `public/favicon.svg` (the Vite template's
  bolt) removed. A grep for "Artist Path" under `src/`, `index.html`, `e2e/` is empty; the
  `artistpath:` localStorage key and the package names are identifiers, not the product name.
- **The mark file `frontend/public/unsung-mark.png` did not exist at commit time** — it is
  the owner's export. Every test passes without it; the page shows a broken image until it
  lands.

## §3 `UXR-T3` — the landing page

- Copy is the mockup's verbatim under `UXR-D12` (flagged assumption; the 2026-08-07 lines
  are quoted in a comment at the h1 so reverting is one edit). Labels "Start with" / "End
  with" are the call site's — `ArtistSearch` is unchanged and its own tests still say From/To.
- `SAMPLE_JOURNEYS` and `TEASER` live in **`src/lib/sampleJourneys.ts`, not in
  `LandingPage.tsx` as the plan said**: oxlint's `react/only-export-components` flags constants
  exported from a component file (fast refresh), and the e2e in `T10` wants them without a
  component. `T10`'s import path changes accordingly.
- **A test the new chips broke, and why it matters beyond the test.** "blocks identical
  endpoints" selected the dropdown entry with `findByText('Radiohead')`; the chips now render
  each name as its own text node inside a link, so the query clicked the chip and navigated
  away. Fixed by selecting by role (the entries are buttons, the chips are links). The general
  rule: on a page that names artists in more than one place, query controls by role.
- The three new tests were not run red separately — they went in with the page in one
  batch. They assert text ("3 steps", the h1 copy, five teaser names) that did not exist in
  the old page, so red is by construction; recorded because the plan asked for the run.
- Screenshots at 390 and 1280 match the artboards. The two broken image boxes are the mark
  the owner has not yet exported.

## §4 `UXR-T4` — `GET /api/meta` and the badge

- Route is `async def` with the `/health` reasoning (`G3-A1`) and a test that introspects
  the keyword, because that regression is invisible to any test that does not saturate the
  pool first. Both api and models files are CRLF; edited byte-for-byte to keep them so.
- `getMeta` gets its own 5 s timeout in `TIMEOUT_MS`; the badge floors to the thousand and
  renders nothing on any failure (UI-7). `LandingPage.test.tsx` needed no mock: the real
  `getMeta` rejects in jsdom and the badge's designed failure mode is silence.
- Snyk on `api/`: one finding, the pre-existing Low in `tests/test_origin_secret.py`
  (known, out of scope). Nothing new. api suite 290 green; frontend 171 green.

## §5 `UXR-T5` — player progress and "Stop N of M"

- `Player.onTimeUpdate` follows the replace-never-accumulate rule of the other two handlers
  and reports duration as 0 while it is NaN, so no consumer divides by NaN. `usePlayer`
  resets position and duration in `clear()` and zeroes position on every `start()`.
- The bar's title comes from the clip cache (`cachedTrack`, a read-only export from
  `useClip`) — never a fetch; the card that owns the clip has resolved it by the time
  anything plays.
- **Seen on the real thing**, not only in the suite: a one-off Playwright script pressed
  play and captured the bar at 390 and 1280 — title, progress line, times, "Stop 2 of 7"
  (hidden below `sm` by design). Deezer previews report ~0:29, and the bar says 0:29 rather
  than the card's nominal 0:30; that is the element's clock and is left honest.
- Frontend 176 green, build and lint clean.

**HANDOFF SEAM — `UXR-T1`–`T5` complete; `T6`–`T11` are the next session's.** Nothing in
flight. The API on :8000 (graph-lux4, with `/api/meta`) and Vite on :5173 were this session's
and are stopped at closeout.

## §6 Closeout at the first seam, 2026-09-08

**Gate outcomes.** No gates in this plan; the per-task checks all passed: every behaviour
test went red before green except `T3`'s three (red by construction, §3); builder 286, api
290, frontend 176 green at closeout; build and lint clean (one pre-existing lint warning in
`vite.config.ts`).

**Defects in the plan itself, `T1`–`T5`** — three, all small, all recorded above: a
self-contradictory test (§2), constants exported from a component file (§3), and a text query
a new chip hijacked (§3). The plan's code was otherwise executable as written.

**Vacuous-test check (B3).** Three guards broken deliberately and each went red: `/api/meta`
reverted to a sync `def` (the coroutine test failed); the badge's floor removed (its
formatting test failed); the `timeupdate` listener never attached (both Player tests failed).
All restored; the diff was empty afterwards.

**Reachability (B2).** `Brand`, `ArtistCountBadge`, `sampleJourneys`, `cachedTrack`, `getMeta`,
`onTimeUpdate` — each imported by at least one non-test module.

**Deferrals (A3).** The Deezer id gap's condition is now armed (`LUX-4` merged) and not
satisfied — recorded in `NEXT.md`'s top block, the registry row untouched. No condition came
due. The spec's §4 items each carry a trigger.

**Default-flip (A4).** No config knob was added; `TIMEOUT_MS.meta` is a constant with one
value, not a switch.

**D6.** Unconditional layer **51,694 characters** (from 51,694, **±0**); conditional **2,561
lines** (from 2,549, **+12**) — `memory/project-state.md` rewritten: a false line ("paying
users", contradicted by `REQ-43` since 2026-08-04) removed, and the owner's two deferred
product ideas from the redesign decisions added. Correction plus recorded intent; nothing in
the unconditional layer moved.

**A5.** Both listeners were this session's (API :8000 on `graph-lux4.bin`, Vite :5173),
started after HEAD; stopped, nothing queued needs one. **C1: nothing written to
`TEST-QUEUE.md`** — the redesign is half built and undeployed; nothing he can press changed.

**B1.** `docs-lint`: one hard failure (this log absent from the map), fixed; candidates are
the standing pre-registration figures, none from this work. `doc-auditor` over the diff: one
High — the plan's role line still said "unstarted" — and one Medium — the plan's `T10` import
named the module `T3` moved the constants out of. Both corrected in place, marked
`⚠ CORRECTED`. The handoff chain, `NEXT.md`'s rename wording and action list, figure
ownership, identifiers and every reference were verified clean.

## §7 `UXR-T6` — the card sheds what it does not need to listen

**Numbered §7, not §6 as the plan says.** The closeout took `## §6` at the first seam, so
every section number in the plan from here is one behind this file. `UXR-T7` appends **§8**.

- **The plan's Step 1 named five test edits and the task needed thirteen.** It covered the two
  Dig-deeper tests, the eyebrow copy and the prop swap, and said nothing about the LUX-4
  block. Removing the facts line and both links from the card also invalidates *a card carries
  links out to both streaming services*, *endpoint cards carry the links too*, *a card with no
  clip still carries the links*, *a card shows the artist facts line* and all three
  "Try another track" tests. Same shape as the plan's three known defects: right about intent,
  incomplete about the repository.
- **What is unasserted between this commit and `UXR-T7`, deliberately:** `REQ-45`'s
  no-rejection wording guard, both streaming links rendering, the facts line rendering, and
  the clip-cycling control. Each is on the interior; each is re-asserted on `ArtistDetail` in
  `T7`. `ArtistInfo.test.tsx` (11 tests) and `StreamingLinks.test.tsx` (6) never stopped
  covering the components themselves — what lapsed is only that *something mounts them*.
- **Two pins `T7`'s planned tests do NOT restore, and must be added there.** (a) *endpoint
  cards carry the links too* — `T7` asserts an endpoint gets no Dig deeper but never that its
  detail still carries both links, and that was a recorded decision (`L4-D3` neighbourhood),
  not an accident. (b) *"Try another track" appears only when there is another track* — `T7`'s
  test of that name asserts only the positive case; the `candidateCount === 1` and silent-card
  directions are dropped. Both are cheap and belong in `ArtistDetail.test.tsx`.
- **A vacuous assertion the plan would have left behind.** It listed three `getByText(/now
  playing/i)` to convert to the `img` role, but `JourneyList.test.tsx` and `PathPage.test.tsx`
  also hold *query*ByText forms asserting the opposite. Converted with them: after the words
  became an equaliser, `queryByText(/now playing/i)` can never match, so "audio stops when the
  path is recomputed" would have passed against a card that never stopped.
- **`PathPage.test.tsx` is left with 3 red, not 4.** The two `renderPlaying` failures were the
  now-playing change, which the plan assigns to this task; only `pressBypass` — `T7`'s — is
  red at this commit.
- **`selected` is reset in the existing `pathKey` effect** beside `stopRef.current()`
  (`UXR-D3`): the open artist may not be on the new path. `onBypass` and `cycleClip` are
  `void`-ed for this commit only; `T7` consumes both.
- **The rail no longer spans the full height.** It runs first dot to last (`top-[41px]
  bottom-[41px]`), which is the mockup. The owner's 2026-07-28 request was *full height, and
  no arrow at the foot*; the no-arrow half is untouched and the comment at the element now
  records both halves and which changed. Flagged to him before the task; one line reverts it.
- **Seen on the real thing** at 390 and 1280 on `graph-lux4` (sha `fd92a735…`, matching the
  sidecar): dots, gradient, eyebrows, detail button, play. Two observations, neither a defect.
  "YOU WERE HEADING HERE" wraps to two lines at 390 — approved copy (`UXR-D15`) in a column
  the second button narrowed; legible, and the copy is his. And `PathIntro` still says the
  Dig deeper control is "along the bottom of their card", which is false from this commit
  until `T8` rewrites it (`UXR-D5`, and `T8` owns it).
- **A screenshot that lied, and the helper fixed so it cannot again.** The first journey shot
  came back with seven empty cover boxes. They were the helper's 2500 ms wait, not the card:
  the covers are background-images from Deezer's CDN, the computed `backgroundImage` was
  correct, and an 8 s run rendered every one. `e2e/screenshot.mjs` now waits for network idle
  as well. Committed separately from the task — it is tooling, not `T6`.
- Card + JourneyList + player: 40 green. Lint clean (the pre-existing `vite.config.ts`
  warning), `tsc -b` and the production build clean.

## §8 `UXR-T7` — the artist detail, docked and as a sheet

**Numbered §8; the plan says §7.** See §7's first note — the offset is permanent.

- **The plan's `ArtistDetail` tests shared one MBID across all five, and the clip cache would
  have bled them.** `useClip` caches on `mbid:index` at module scope with a ten-minute TTL and
  nothing clears it between tests, so the first test's `candidateCount: 1` would have been
  served to the "Try another track" test asserting 3, and that test would have failed for a
  reason having nothing to do with the component. Distinct ids per test, as
  `ArtistCard.test.tsx` has done since `LUX-3` and for the same reason. **This is the fourth
  plan-vs-repository defect in seven tasks**, and the first that would have looked like a
  component bug rather than a test bug.
- **The facts assertion is by fragment, not by the whole line.** The plan asserted
  `/French duo · Group · Versailles · 1995–/` as one text node, which pins `ArtistInfo`'s
  formatting from a second place; `ArtistInfo.test.tsx` owns that and asserts fragments. This
  file asserts only that the detail *mounts* it.
- **Three tests added beyond the plan, two of them the pins §7 recorded as owed.** An
  endpoint's detail still carries both links (a `LUX-4` decision that moved with them, and
  `T7` as written asserted only that an endpoint has no Dig deeper); "Try another track"
  absent at `candidateCount === 1` and on a silent artist (the plan's test is named "only when
  there is another track" but asserted one direction). Plus the ✕ button reporting the close —
  at `lg` the dock has no scrim and no Escape, so it is the only way out.
- **`DetailSheet`'s Escape listener is bound to `open`,** and a second test pins it: a closed
  sheet left mounted must not go on answering Escape for the page behind it.
- **A bare text query in `PathPage.test.tsx` now matches three nodes.** jsdom has no
  breakpoints, so dock and sheet both render and the open artist's name appears on the card
  and twice in the detail. "a bypass press holds the old path" asserted `getByText('Herbie
  Hancock')`; it now reads the card's `data-testid="artist-name"` hook, which is what the
  assertion always meant. Third instance of §3's rule: **on a page that names artists in more
  than one place, query by role or by hook, never by text.**
- **`pressBypass` takes the SECOND detail button, not the first.** The first card is an
  endpoint and its detail has no Dig deeper at all, so the plan's `getByRole` form would have
  opened a detail with nothing to press. The plan flagged this as a conditional; it is
  unconditional in this file — every `pressBypass` caller renders a path whose first card is
  an endpoint.
- **`max-w-[1200px]` on the journey page is pulled FORWARD from `T8`.** The dock is a 400px
  column inside a 620px `<main>`, so at `T7` as planned the journey page scrolled sideways at
  1280 — measured at 249px of horizontal overflow, 0 after. One line moved so the commit
  leaves a working app; `T8` still owns the header restyle inside that width and must not
  re-apply it.
- **Seen on the real thing** on `graph-lux4`: the sheet at 390 over its scrim, the dock at
  1280 sticky beside the rail with the open card ringed and its dot recoloured, "Stop 3 of 7"
  in both. Two knowingly-transient looks until `T8`: the header row and the explainer stretch
  to the new width, and `PathIntro` still says the control is "along the bottom of their
  card".
- Whole unit suite **183 green** (from 176 at the seam, +10 detail, +2 sheet, +3 journey
  list, −8 moved off the card). Lint clean, build clean.
- **Known red outside the unit suite: `e2e/responsive.spec.ts`.** Its `LUX-4` case looks for
  the streaming links *inside an interior card*, and they are in the detail now. `T10` rewrites
  the e2e suite and owns it; it is Playwright, so it is not in `npm test` and does not gate
  this commit.

## §9 `UXR-T8` — the journey header, share, the title and its steps tile

**Numbered §9; the plan says §8.** The offset is the same one §7 records.

- **A `PathPage` test the plan did not mention asserted the old result line.** "the result line
  counts the artists in between" pinned `/we found a path/` **and the singular** for one artist
  between. The plan's replacement test happened to use a three-artist path, so it too rendered
  the singular and would have left the plural unasserted while looking like coverage. Split:
  the old test became "the steps tile uses the singular for one artist in between" (and asserts
  the plural is *absent*), and the new heading test moved to a four-artist path so it pins the
  plural. **Fifth plan-vs-repository defect.**
- **`PathIntro` lost its `count` prop, not just its sentence.** Its tests were rewritten around
  the explainer alone, plus a new one pinning `UXR-D5` from both directions: the copy names
  where the control *is* ("Open any artist in the middle") and no longer says "along the bottom
  of their card". Help that names the old placement is worse than no help — it sends the reader
  to the bottom of a card that has nothing there.
- **Two `ShareButton` tests beyond the plan, both about failure.** A refused clipboard
  (insecure origin, denied permission) must leave the page alone — UI-7's rule for a decoration
  applied to a convenience. And a **dismissed share sheet must not fall through to the
  clipboard**: `navigator.share` rejects when the user swipes it away, and a fall-through would
  claim a copy nobody asked for. The plan's component already returns early; nothing asserted it.
- **`New path` moved from the far left to the right-hand pill group** and lost its arrow, with
  `Brand` taking the left. It is still a `Link` carrying the pair, and still stops the audio on
  click — the two tests that matter (`"new path" goes back to choosing artists` and the reset
  pair) select it by role and were untouched.
- **Seen on the real thing** at 390 and 1280: brand, Share and New path pills, "YOUR JOURNEY",
  the title with its gradient dash, the steps tile reading 5, the corrected explainer, and the
  dock's placeholder line. **The mark now renders** — the owner's export landed in
  `frontend/public/` during this session, so the broken image box §2 and §3 recorded is gone.
- Whole unit suite **188 green**, lint and build clean.

**HANDOFF SEAM — `UXR-T1`–`T8` complete; `T9`–`T11` are the next session's.**
