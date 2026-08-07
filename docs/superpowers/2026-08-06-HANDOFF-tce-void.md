# Handoff — the Laura Lee closure and the `TCE-` void run, 2026-08-06

**Role: ⚠ SUPERSEDED on next actions 2026-08-06 (night) by
[`2026-08-06-HANDOFF-tcr-rerun.md`](2026-08-06-HANDOFF-tcr-rerun.md)** — the re-run it
ruled has happened (`TCR-`, computed, nothing enriched) and the stale Vite server it
flagged is gone. **Still authoritative for the void run's internals and its do-not-revert
claims, all of which stand.** *(Original role:)* **ACTIVE — this is the CURRENT handoff.**
Nothing supersedes it. Supersedes
[`2026-08-06-HANDOFF-cocredit-investigation.md`](2026-08-06-HANDOFF-cocredit-investigation.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**A SEAM handoff, not mid-flight.** The probe reached a designed stopping point — a gate fired,
which is an outcome the design provides for — everything is committed, nothing is half-built,
and the owner has ruled the next action. The degradation tell did **not** fire.

Branch `cocredit-relationship-probe`, **draft PR #87**, pushed *(since MERGED 2026-08-07 at `95901d4`)*. Reasoning:
[`2026-08-06-tce-thin-catalogue-execution-log.md`](2026-08-06-tce-thin-catalogue-execution-log.md).
**No shipped code was touched.**

---

## The next action is RULED, not open

**The owner decided (2026-08-06, night), and it is recorded as his:**

- **Option A. `TCE-` is re-run under a NEW pre-registration** — not an amendment — with **gate
  thresholds anchored on externally measured values**, by a **fresh session**.
- **The fired `TCE-` record stands untouched.** Its gate firing is the record. Do not amend
  `TCE-G1`, do not re-band it, do not retro-fit.
- **Option C — a same-name population probe — is DEFERRED until after the re-run.** Deliberately.
  It is not abandoned and not closed.

**This session was told not to draft the new pre-registration. That is the next session's work,
deliberately.** Do not treat its absence as an oversight.

## Documents that are now wrong, and in which direction

**None that I introduced, and none of another session's.** `docs/README.md` gained four rows
(three analysis directories and the new pre-registration); `docs-lint`'s three hard checks pass.

## Claims that must NOT be reverted by a well-meaning editor

- **`TCE-` is VOID and has no outcome.** There is no `TCE-C1`/`C2`/`C3`/`C4`/`C5` and no
  `Δ_R`. **Do not infer a branch**, and do not read "the instrument turned out fine" as a pass.
- **The instrument IS correct and the threshold was wrong.** Both halves travel together.
  Recording only the first would misrepresent a sound tool as broken; recording only the second
  would un-void the probe.
- **`§6` item 1 is PARTIALLY discharged — worked case closed, population question OPEN.** Do
  not simplify this to "the collision hypothesis is dead". The closure's §4a says why.
- **The `Not Up for Discussion` mis-filing is `n = 1`** and licenses no rate. It is **not**
  evidence for the thin-catalogue mechanism, and it is a *different level* from the closure's
  finding — MusicBrainz's own credits, not ListenBrainz's listen resolution.
- **Laura Lee's absence from Khruangbin's list is a truncation artefact**, not an asymmetry.
- **`TCE-C1` was kept, not removed**, when a derivation condemned it. Do not "tidy" it away.

## Already updated — do not redo

`docs/README.md` (four rows), the previous execution log's §6 item 1 (struck in place), the
three `builder/analysis/2026-08-06-*` READMEs, `.gitignore` (two dump-cache rules), `NEXT.md`.

## What I know that is not in the durable record

**Empty, and checked rather than asserted.** Every figure this session reported to the owner
was verified present in a committed file before retirement, on his explicit instruction: the
`TCE-G1` table (`tce_result.json`), the arm sizes, tie share and scan count (`tce_run.log`,
committed for exactly this reason), and the mis-filing (`miscredit.json`, reproducible via
`miscredit_check.py`). **The previous session lost its exploratory figures to a scratchpad;
this one was made to check, and the check found the run log was the only copy.**

## Anything in flight

**Nothing.** No dispatched subagents, no background jobs, no half-written directories.

**⚠ One listener the owner must deal with, because I was blocked from stopping it.** A **stale
Vite dev server on port 5174, PID 249084**, started 2026-08-06 08:24 — long before HEAD. It
survived the 2026-08-06 sweep that stopped 5173 and 8000 **because that sweep checked those two
ports only** and Vite had fallen back to 5174. Nothing queued needs a local server; both live
test-queue entries target the deployed site. Command in the closing message.

## What I would do if I were continuing

**Write the replacement pre-registration, and anchor its gate on artists chosen for having
unambiguous catalogues** — the opposite of the four used here, one of which is a known
same-name case whose ground truth turned out contaminated. Then set every cell's threshold from
a *measured* release-group count with a deliberate margin, rather than inferring one from a
recording count as I did.

**The execution log's §7 is the list of what a re-run must not repeat**, and it is the section
to read before drafting anything.
