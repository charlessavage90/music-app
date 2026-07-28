# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-27, after the phone run passed and the OneDrive migration was
planned.** ⚠ **This was a partial update, not a `closeout`** — see "What is owed" at the
bottom.

---

## Next

**Execute the OneDrive migration plan**, or decide not to yet. Twelve tasks, identifiers
`MIG-`, destination `C:\dev\music-app`:
[`plans/2026-07-27-onedrive-migration.md`](plans/2026-07-27-onedrive-migration.md), handed off
at [`2026-07-27-HANDOFF-onedrive-migration.md`](2026-07-27-HANDOFF-onedrive-migration.md),
PR #35. **It touches no application code, no graph, no routing and no config default.**

**The app is live and the phone run passed.** `https://d2n3xqz3pttguf.cloudfront.net`, username
`artistpath`, password in `infra/.env.deploy`.

**The queue is empty.** The 2026-07-27 entry is DONE **per-step on all six checks** — the first
run against the live site, on an Android Pixel. Sign-in and the shared journey link were both
witnessed by a human for the first time, the link opened by a recipient who had never logged
in. **iOS remains unexercised**: Safari rendering, the iPhone home indicator and iOS keyboard
behaviour are unanswered by anything, and an Android device cannot answer them.

> **Nothing is running on the owner's machine and nothing needs to be.**

Record: [`2026-07-27-gate2-track-c-execution-log.md`](2026-07-27-gate2-track-c-execution-log.md).
PR #33.

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception below (`BYP-13`). |
| **Gate 2 — friends & family** | **All tracks DONE, and the phone run has now passed** (2026-07-27, per-step on all six checks, Android Pixel). The app is on the internet, the gate admits, and **real use has begun**. What remains is the Gate 2 → 3 team review — **its "after a period of real use" condition is closer to met than it has ever been, and recommending it is now live. It is the owner's call and has not been put to him.** Staff the frontend explicitly. |
| **Gate 3 — public** | Not started. |

A team review is scheduled at each gate boundary **after a period of real use** — staff the
frontend explicitly. See `CLAUDE.md`, "When to recommend a review". **Real use has not
happened yet**; the queued entry is the start of it, not a substitute for it.

## Closed — do not re-plan or re-investigate

- **`RMD-6` is CLOSED**, and this reverses the standing warning that stood here since
  2026-07-26. The live API no longer echoes a localhost origin — measured before and after
  the deploy, not assumed. The owner's acceptance of that exposure has expired by being
  fixed.
- **`RMD-11`, `RMD-12`, `RMD-13`'s mechanical half, `FRO-1`, `FRO-4`** — all closed and
  verified against the live distribution. **§8a ran for the first time in the project's
  history**: every previous check proved only that the site *refuses*.
- **The `DEP-33` blockers** — all three stages, PRs #30 and #32.
- **The Gate 1 clip work** (PR #19, #20), all confirmed in use.
  - ⚠ **One exception, live:** `BYP-13` in
    [`findings/2026-07-25-bypass-depth-use-run.md`](findings/2026-07-25-bypass-depth-use-run.md)
    — a card that played a clip by a *different artist of the same name*. Not path-quality
    work and **not inside the pause**.
- **Track 1** (the §2.8 tie-break fix) — done and adopted.
- **Track 2, Track 2F, and the ceiling toll.** See the pause below.

## Corrected here, because this document was wrong

**This file previously said Track C would close the stack drift. It does not** — it closes
the *exposure* only. The empty `ARTISTPATH_CORS_ORIGINS` stays in the template deliberately,
App Runner goes on dropping it, and that drift row is now **permanent by design**.
`infra/README.md` §7 has been corrected to expect three rows rather than two; left alone it
would have fired on every future deploy. Execution log §3.1.

## Deferred, with conditions

| Finding | Condition |
|---|---|
| Medium CSRF in `react-router@7.18.1` | Revisit **only if** the app adopts React Router's unstable RSC APIs. It is not exploitable without them, and this is a Vite SPA with none of that machinery. |
| ~~Mangled punctuation in artist descriptions (The Beatles reads `â€œThe Fab Fourâ€`)~~ | **STRUCK 2026-07-27 — RETRACTED, it was never a defect.** The adopted artifact holds correct UTF-8 (`UK rock band, “The Fab Four”`), read straight out of it after a checksum match; the mangling was in the tool that read the live response. The owner reported it had always rendered correctly and was right. **This removes one of the reasons for a graph rebuild.** |
| The `--prune` publish pass | The next deploy after this one. Skipped at cutover because the bucket was empty. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is **inert** — `index.html` never sets `viewport-fit=cover`, so it is 0 on every device | **Only if someone adds `viewport-fit=cover`.** Latent, not live: the default viewport already avoids the inset, which is why the phone run passed. No fix proposed. Found 2026-07-27. |

## What is owed — this was a partial update, not a `closeout`

Recorded so the next session does not mistake this file for a closed-out one. **Not done:**
the deferral re-test sweep (`A3`), the orphaned-module and vacuous-test sweep, `D6`'s
standing-layer measurement, and the doc-auditor step (`B1`) — though `scripts/docs-lint.sh`
passes. The `TEST-QUEUE` entry, the handoff and this file were updated because they could not
wait; everything else a `closeout` does is still owed.

---

## Path quality is PAUSED — owner decision, 2026-07-25

**This is a separate track from the gates, and it is stopped. Resuming it is the owner's
trigger, never a session's.**

- Track 2 and Track 2F **both returned nulls**. The ceiling *ordering* measurement came back
  **WIDE**. **Nothing adopted, no shipped code changed, no blind listen run, no threshold
  touched, no rebuild.**
- **Track 2F's full-strength toll re-run is already EXECUTED. Do not run it again.**
- **The live candidate is a builder-side p99 rescale, and it is NOT pre-registered. Do not
  start it.** No experimental arm runs before a committed pre-registration.

**If it is ever resumed, the entry point is
[`2026-07-26-RESUME-BRIEF-path-quality.md`](2026-07-26-RESUME-BRIEF-path-quality.md)** —
read it in full first. It is not itself a resume signal. Parked candidates and what each
needs: §0 of [`2026-07-25-HANDOFF-track2f-and-headroom.md`](2026-07-25-HANDOFF-track2f-and-headroom.md).

**Before acting on any path-quality claim**, read
[`2026-07-22-phase1-execution-log-and-graph-defect.md`](2026-07-22-phase1-execution-log-and-graph-defect.md)
§2 — and §2.12 first, because it retracts a central claim of §2.9. The three quantities that
are not interchangeable (**degree ≠ popularity ≠ fame**) are live hazards; `CLAUDE.md`'s
orient table has the short form.
