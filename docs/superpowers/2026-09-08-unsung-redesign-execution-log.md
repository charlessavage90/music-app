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
