# Handoff — `CEX-` Task 11 complete and stopped at its owner stop, 2026-08-09

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-08-HANDOFF-cex-crawl.md`](2026-08-08-HANDOFF-cex-crawl.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The plan's last task is complete, the track is stopped at the owner stop
it was designed to reach, and a **new governing document** — the `JFX-` pre-registration — is
committed and unrun. That is the condition a pre-registration is written for: the next
session reads it cold. The degradation tell did not fire.

Reasoning: [`2026-08-09-cex-task11-execution-log.md`](2026-08-09-cex-task11-execution-log.md).
Figures: `builder/analysis/2026-08-09-cex-recensus/README.md` — cited, never restated.
Branch `crawl-extension-design`, **PR #91**.

---

## Start here

1. **Nothing is blocked and nothing is half-done.** Task 11 finished; the build was rejected
   on both acceptance bounds, which **is** the designed outcome.
2. **The next action is the owner's**, and the options are in `NEXT.md`.
3. **If the next action is running the `JFX-` arms**, the governing document is
   [`specs/2026-08-09-journey-fame-exposure-preregistration.md`](specs/2026-08-09-journey-fame-exposure-preregistration.md).
   **Read its §0.1 before its §3** — two confounds there bind how every result may be read.

## What is done

Task 11's five steps, all of them. Fame fetched; the extended population re-censused; drop
lists assembled; the build run and rejected; `CEX-M1` recorded against a baseline that
**reproduces the adopted artifact exactly**. One shipped-code addition (below). The `SEL-`
problem statement and the `JFX-` pre-registration, both committed.

**Nothing adopted. No default flipped. No artifact shipped. The live site is untouched and
was never at risk.**

## Documents that are now wrong, and in which direction

- **The plan's Task 11 is COMPLETE.** `docs/README.md` described it as "NOT YET EXECUTED";
  that row is corrected.
- **Anything treating `CEX-M1`'s saturated-edge share as a live measurement is wrong.** It is
  vacuous by construction — see below.
- **The spec's "the prune costs 454 artists today"** is superseded by a measured 439 for the
  comparison actually used. The spec is frozen and is **not** edited.

## Claims that must NOT be reverted by a well-meaning editor

- **`CEX-M1`'s saturated-edge share is VACUOUS, not "unchanged".** An edge saturates iff its
  raw score is at or above the 99th percentile of raw scores, so ~1% of any distribution
  saturates, at any crawl size. Reading 1.0007% → 1.0019% as "no effect" is a conclusion the
  instrument cannot support. **Do not delete the finding and keep the reading.**
- **`unlistenable_list_path` defaults to `None` deliberately and is NOT unshipped work.** It
  is an override, per-invocation by design. The thing that would be a default flip —
  repointing `CANDIDATE_UNLISTENABLE_DROP_LIST_PATH` — is deferred to an adoption decision on
  purpose, because repointing changes every future build from the pre-crawl snapshot
  *silently*. See the execution log §3.
- **The regenerated ALG-E drop list is a BY-PRODUCT and must not be shipped.** Its population
  never changed, yet 30 artists became drops and 43 stopped being drops in four days. The sha
  pin in `unlistenable_drop.py` is what prevents this by accident; **do not update it to
  match.**
- **`JFX-C2` has no threshold on purpose.** It was withdrawn by owner ruling, not forgotten.
- **`JFX-G1b` is 67%, owner-set, before any arm ran.** Do not re-derive it.
- **Everything on the previous handoff's "must not be reverted" list still stands in full** —
  `exhausted: false`, `grt_run.py`'s refusal, `calibrate.py`'s old stopping rule, the ALG-E
  `algorithm` default, and *do not widen the acceptance bounds*.

## Already updated — do not redo

`NEXT.md` (rewritten), `docs/README.md` (four new rows plus two corrections), the previous
handoff's role line, `builder/analysis/census-coverage/.gitignore`, and the `SEL-` findings
document's own "owed at closeout" list — **both items on it are now discharged.**
`TEST-QUEUE.md` was **deliberately not written to** (see below).

## What I know that is not in the durable record

**Nothing of substance.** Two things were folded into the execution log rather than left
here: the D6 mis-measurement from the wrong working directory (§7) and the `2>&1`/`Tee-Object`
translation defect (§2c), both of which will recur for the next session that mixes shells.

One operational note that has now bitten twice and is in neither: **PowerShell mangles a
commit message containing double quotes** when passing it to git as a native argument. Use
`git commit -F <file>`. This cost one failed commit that reported as five bogus pathspec
errors.

## Anything in flight

**Nothing.** No subagents beyond this closeout's `doc-auditor`, no background jobs, **no
listeners: ports 8000, 5173 and 5174 swept and free.** No dev server was started this session
and none was left behind — nothing queued needs one.

**Reversibility is intact.** `builder/scratch/grt-archive-algb.pre-cex-snapshot` still holds
the pre-crawl archive and was exercised this session — the baseline build read it and
reproduced the adopted artifact byte-for-byte, which is stronger evidence than a checksum
that the snapshot is a working way back.

## What I would do if I were continuing

**Run the `JFX-` arms**, in this order, because the first one gates the rest:

1. Build the diagnostic artifact (~17 min) — the script catches the acceptance rejection and
   records it in the manifest rather than suppressing it.
2. Materialise the pair set: first 100 per stratum from the committed candidates, in
   committed order, surviving the intersection. **Report how many were skipped** — a
   non-trivial number means the extension *removed* artists.
3. Route and report **`JFX-G1` first**, then `C6` and `C7`, then the gradients. §4's reads
   are not licensed until both validity checks exist.

**And fold `CEX-M1`'s fix into the same artifact** — measure saturation post-cap, where it is
not vacuous. It costs almost nothing once the artifact exists, and it closes a
known-blind instrument the next crawl would otherwise inherit.

## Open, and not this session's

- **`CEX-F1`**, **`CEXR-6`'s `load_deezer_ids` half**, **`CEX-R3`** (search), **`CLIP-1`**,
  **`FE-SNYK-1`** — all unchanged, all with conditions in the execution log §8.
- **`SEL-R1`–`R4`** — the selector-identity work, deliberately deferred to a dedicated
  maintenance session on the owner's instruction. Problem statement:
  [`findings/2026-08-09-selector-identity-drift.md`](findings/2026-08-09-selector-identity-drift.md).
- **PR #92 is MERGED** (`0a74f1c`) — the landing-page dot fix is on `main` but **not
  deployed**. The live site still shows the defect until he publishes.
