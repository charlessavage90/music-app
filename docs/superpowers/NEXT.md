# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-27, at the OneDrive migration's Phase D seam — Phases A–C executed.**
Updated mid-work rather than at a closeout, per this document's own rule that an execution log
which disagrees with it wins and the staleness gets fixed rather than worked around. The
"Closeout state" section below still describes the *previous* closeout and is unchanged.

---

## Next

**The OneDrive migration is at its Phase D seam. Two things are owed, and both are the
owner's.**

Phases A–C ran on 2026-07-27 and passed —
[`2026-07-27-onedrive-migration-execution-log.md`](2026-07-27-onedrive-migration-execution-log.md)
is the record, and
[`2026-07-27-HANDOFF-migration-phase-d.md`](2026-07-27-HANDOFF-migration-phase-d.md) is the
current handoff. **The plan itself still reads as though nothing has run**; the log wins. **`C:\dev\music-app` exists, is verified, and works**: all four suites
green from it, all 18 graph artifacts byte-identical, and a running API serving `4cb84ef9…`.
**The OneDrive tree is untouched and is the rollback.** No application code, graph, routing or
config default changed, and no test-queue entry is owed.

1. **Confirm the memory slug by observation** — open a session in `C:\dev\music-app` and check
   Claude Code reads `~/.claude/projects/C--dev-music-app`. Memory was **copied** there, not
   moved, so a wrong prediction costs nothing; until this is observed **`MIG-2` is mitigated,
   not closed.**
2. **Verify Backblaze actually covers `C:\dev`** (Task 9) — folder included, `.bin`/`.json` not
   excluded, and an upload **completed** rather than queued. **This gates Task 11**, the
   deletion of the OneDrive tree. Until it passes, OneDrive is still the only second copy of
   the unreproducible archive.

3. **Kill two zombie API servers before Task 11** (`MIG-11`, execution log §16). Ports **8138**
   and **8139**, PIDs `71076, 59236, 60412, 97220`, running from the **old** tree's `.venv`
   since 2026-07-20. They hold that tree's files open, so **Task 11's deletion will fail
   partially** — leaving the rollback copy neither present nor gone, its worst state. Stopping
   them was attempted and **blocked by the tool-permission classifier**, so it needs the owner.
   **Do not kill PID 90324 on port 53342** — that is a Home Assistant sidecar from another
   project.

**Then Task 10: work from `C:\dev\music-app` for a few days before anything is deleted.** Phase
D is irreversible and is deliberately not started.

> **OneDrive sync was paused for 24 h on 2026-07-27 and resumes by itself.** Nothing in Phases
> A–C depends on it staying paused.

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

## Closeout state — run 2026-07-27, and this section is the result

**⚠ This section said a closeout had not been run. It was written mid-session and then not
revisited, and the closeout ran afterwards — so it understated what was done. Corrected by
the doc audit that same closeout dispatched.**

**Done:** `A3` (every deferral condition re-tested against reality, not merely confirmed to
exist — see the table above), `A5` (both ports swept; nothing listening, nothing started),
`B1` (**`docs-lint` passes and `doc-auditor` ran, scoped to the diff — it found three HIGH
defects, all fixed**), `B4`, `B5`, `C1`, `D1`, `D3`, `D4` (**builder 115, api 195, infra 58,
frontend 80 — all green**), `D5` (PR #35), `D6` (**unconditional layer delta 0**; conditional
+14 lines in `memory/`).

**Genuinely still owed:** `B2` (reachability) and `B3` (vacuous-test spot check). Both want a
finished artifact and this session produced no code, so they travel with the migration work
rather than being run against nothing. `A4` is inapplicable — no config knob was added.

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
