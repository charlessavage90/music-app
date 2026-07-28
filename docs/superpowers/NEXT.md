# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-27 (evening), at the OneDrive migration's Phase D seam — Phases A–C
executed.** Updated mid-work rather than at a closeout, per this document's own rule that an
execution log which disagrees with it wins and the staleness gets fixed rather than worked
around. The "Closeout state" section below still describes the *previous* closeout and is
unchanged.

**All three owner-owed items below are now discharged and struck.** Each was checked **by
observation, not by reading a document**: the memory slug (item 1), Backblaze (item 2,
2026-07-28), and the two zombie API servers (item 3). **The migration axis carries no owner-owed
item.** Tasks 10 and 11 are closed by owner decision — see item 2 — and **Task 12 is the only
migration task still open; it is a session's to do, not the owner's.**

---

## Next

> **⚠ TWO things are owed and both are the owner's. This section named only one until
> 2026-07-28.** A second, unrelated body of work is now live — **removing the site password** —
> and it is blocked on an owner action of its own: **request an ACM certificate for
> `musicapp.cmiller.io` in us-east-1.** Its handoff is
> [`2026-07-28-HANDOFF-password-removal-track-b.md`](2026-07-28-HANDOFF-password-removal-track-b.md),
> which is now **the handoff to read first**; its plan is
> [`plans/2026-07-28-password-removal-load-hardening.md`](plans/2026-07-28-password-removal-load-hardening.md).
> **It discharges nothing below.** Track A (API hardening) is **MERGED to `main`** — PR #39,
> merge commit `1117d35`, 2026-07-28 — and **the live site and the password are unchanged by it**:
> nothing was deployed. Track B starts on a fresh branch off `main`.
> This is a pointer, not a rewrite — the full rewrite is that plan's task PW-8.

**The OneDrive migration is DONE except for Task 12, and nothing on this axis is owed by the
owner.** Items 1–3 below are all **struck — discharged by observation**, items 1 and 3 on
2026-07-27 (evening) and item 2 on 2026-07-28. **Phase D as planned no longer exists:** the
owner decided on 2026-07-28 that the old tree costs nothing to keep and will be deleted by him
whenever he chooses, which closes Tasks 10 and 11 and makes Phase D's irreversibility moot.

Phases A–C ran on 2026-07-27 and passed —
[`2026-07-27-onedrive-migration-execution-log.md`](2026-07-27-onedrive-migration-execution-log.md)
is the record, and
[`2026-07-27-HANDOFF-migration-phase-d.md`](2026-07-27-HANDOFF-migration-phase-d.md) is the
migration's handoff — **still live for Tasks 9–11, but no longer the *current* handoff**; see
the box above. **The plan itself still reads as though nothing has run**; the log wins. **`C:\dev\music-app` exists, is verified, and works**: all four suites
green from it, all 18 graph artifacts byte-identical, and a running API serving `4cb84ef9…`.
**The OneDrive tree is untouched and is the rollback.** No application code, graph, routing or
config default changed, and no test-queue entry is owed.

1. ~~**Confirm the memory slug by observation** — open a session in `C:\dev\music-app` and check
   Claude Code reads `~/.claude/projects/C--dev-music-app`.~~ **✅ DISCHARGED — `MIG-2` is CLOSED,
   not merely mitigated.** Closed in the execution log §11 ("Task 8 CLOSED — the slug was
   confirmed by observation"), and confirmed a further time on 2026-07-27 (evening) by a session
   running from `C:\dev\music-app` that loaded its memory index from
   `~/.claude/projects/C--dev-music-app/`. **This item was already stale when written here; the
   execution log was the fresher document and won.** The duplicate memory directory under the old
   slug is still retained deliberately until Task 11.
2. ~~**Verify Backblaze actually covers `C:\dev`** (Task 9) — folder included, `.bin`/`.json` not
   excluded, and an upload **completed** rather than queued. **This gates Task 11**, the
   deletion of the OneDrive tree.~~ **✅ DISCHARGED 2026-07-28 — `MIG-3` is CLOSED, and it was
   closed by restore rather than by reading a backup UI.** The owner confirmed full coverage and
   then **restored two files** to `C:\Users\charl\Downloads\C\dev\music-app`: the adopted
   artifact `builder/scratch/graph-t15-tiebreakfix.bin` and one crawl-archive record,
   `graph-archive/similar/listenbrainz/00006766-…95ec.json`. Both are **byte-identical to the
   live files** (sha256 and length), and the artifact's hash agrees **four ways** — restored
   file, live file, its manifest sidecar, and `findings/2026-07-23-tiebreak-fix-adoption.md`.
   The JSON is intact as a *record*, not merely as bytes: it parses, holds 72 entries, and every
   `reference_mbid` matches its filename. This settles all three sub-conditions — folder
   included, `.bin`/`.json` not excluded by type or by size at 14 MB, and the upload **completed**
   (bytes the service does not hold cannot be downloaded). **What it does not establish** is
   whole-tree coverage: two files were sampled, not ~75,000. That gap no longer gates anything,
   because Task 11 is closed.

   **Tasks 10 and 11 are CLOSED by owner decision, 2026-07-28, and must not be re-planned.**
   Keeping the OneDrive tree costs essentially nothing, so there is no deadline to delete it;
   the owner will do so himself if he ever needs the space. Task 10 existed **only** to gate
   Task 11 and therefore closes with it. **The consequence a session must not miss: the old tree
   is now permanent-but-archival rather than a rollback awaiting deletion, so `MIG-10`'s
   "those statements are still true" defence has expired** — see Task 12 below.

3. ~~**Kill two zombie API servers before Task 11** (`MIG-11`, execution log §16). Ports **8138**
   and **8139**, PIDs `71076, 59236, 60412, 97220`.~~ **✅ DISCHARGED — `MIG-11` is CLOSED.**
   Measured 2026-07-27 (evening): ports **8138, 8139, 8000 and 5173 are all free**, and all four
   PIDs are **gone**. Nothing is holding the old tree's files open, so the failure mode this item
   guarded against — a partial Task 11 deletion leaving the rollback copy neither present nor
   gone — no longer applies. **Task 11 must still re-check both ports immediately before
   deleting**, since this measurement ages: an old-tree server started after it would reinstate
   the hazard silently. **Do not kill PID 90324 on port 53342** — that is a Home Assistant
   sidecar from another project, and it was never in scope here.

**Task 12 (`MIG-10`) is the one migration task still open, and it is now unblocked.** It was
deferred because ~8 documents say the project lives under OneDrive and that was *true of the tree
that was still the rollback*. **That defence has expired**: with the old tree kept indefinitely as
an archive, those statements are now permanently wrong about the **working** tree and permanently
true about a **dead** copy, and waiting no longer resolves the ambiguity. Two are live defects
rather than stale prose, both in the standing context layer: `CLAUDE.md`'s environment note and
`.claude/agents/ml-graph-analyst.md:175` tell every session the project is under OneDrive and to
prefix every `uv` command with `UV_LINK_MODE=copy`, which `memory/env-onedrive-uv.md` records as
**unnecessary at `C:\dev`**. **Scope it to the live documents only** — `CLAUDE.md`, the two
rituals, `ml-graph-analyst.md`, and the four package READMEs. **The ~30 execution logs, plans and
findings that mention OneDrive are historical and must NOT be edited.**

> **One thing was already fixed rather than left for Task 12, because it was a silently broken
> check rather than stale prose.** `closeout` **D6** defined `M` as the pre-migration memory slug
> — a directory that **still exists**, so it ran clean while computing *both* its numbers against
> a frozen copy that could never move. Corrected 2026-07-28 to `C--dev-music-app`; the corrected
> command was run and both figures moved, which is the evidence the check can now go red. **The
> figures are deliberately not restated here** — re-run D6 for them, since they change at every
> closeout and this document owns none. The two
> memory directories have diverged in 2 of 12 files (`MEMORY.md`, `env-onedrive-uv.md`); the
> old-slug copy is **not** inside the OneDrive tree, so deleting that tree would never have
> removed it — `NEXT.md` and the Track B handoff both implied otherwise and were wrong.

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
| **Gate 2 — friends & family** | **All tracks DONE, and the phone run has now passed** (2026-07-27, per-step on all six checks, Android Pixel). The app is on the internet, the gate admits, and **real use has begun**. The Gate 2 → 3 team review — commissioned by the owner and **DELIVERED 2026-07-27 (evening); do not re-commission or re-recommend it.** Read it before opening Gate 3: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md) (PR #38) — it owns its own findings and their triage. It records Gate-3-blocking issues and, in §6, the owner-facing decisions they raise. **None are actioned and Gate 3 is not opened; the blocking set gates Gate 3, not Phase D.** |
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
