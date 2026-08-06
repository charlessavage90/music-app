# Handoff — the `MSW-` map switch, Task 8 complete (mid-flight), 2026-08-06

**Role: SUPERSEDED on next actions** by
[`2026-08-06-HANDOFF-msw-task10-midflight.md`](2026-08-06-HANDOFF-msw-task10-midflight.md)
(2026-08-06, Task 10 half done). **It remains authoritative for Task 8's own internals** — the
fame-coverage run, its two command defects, and the Tasks 1–7 verification table. Supersedes
[`2026-08-05-HANDOFF-msw-seam2.md`](2026-08-05-HANDOFF-msw-seam2.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**⚠ A MID-FLIGHT handoff, not a seam.** The plan's seams are at Tasks 5/7/10/12; this stops at
**Task 8 of 12**, two tasks short of Seam 3. Retired on the owner's call after he asked whether
there was a structural reason not to continue — there was, and it is recorded below rather than
left implicit. `session-start`'s cold-read check applies: **state back what you believe the
situation is before acting on this note.**

**Branch** `msw-package-adoption-plan`, draft PR **#81**. HEAD `f7c0117`. Tree clean, no
listener on 8000 or 5173, nothing in flight.

---

## Why this stopped here rather than at Seam 3

Not the degradation tell in its defined forms — no figure was re-requested, no tracked item
dropped, no firm claim revised under questioning. The reason is **what Task 9 is**: it builds a
gitignored artifact whose only identity is a sha256 recorded by hand into a sidecar and the log.
A session interrupted between building that artifact and recording its identity hands its
successor a file it cannot identify — and this project has already been damaged by exactly that
("several graphs exist and are not interchangeable"). Stopping *before* that task costs nothing;
stopping inside it is expensive.

Against that, this is an unusually clean stopping point: committed, pushed, clean tree, **no
artifact built, no gitignored state written**, and nothing learned that is not in the committed
log. That is why this note is short — there is no live understanding to transfer.

**Three slips this session made, recorded because the rate matters more than any one of them:**
a failed `Edit` string match, a `git commit -- -m` pathspec ordering error, and — the one that
counts — first testing the boot-refusal guard by re-stating its condition inline instead of
calling `create_app`, which would have passed identically had the `raise` been deleted. Caught
and redone unprompted, but it is the same vacuous-check class this branch keeps finding.

## What is done

**Task 8 complete and committed** (`f7c0117`). Fame coverage over the candidate archive:
75,000 of 75,000. Full counts, provenance and reasoning are in the execution log's **Task 8**
section — cited, not restated here.

**Tasks 1–7 were verified rather than taken on trust**, at the owner's explicit instruction (see
"Standing instruction" below). Six claims exercised, four perturbed until red. **Nothing found
wrong in the previous session's code.** The verification table is in the log.

## Standing instruction from the owner, 2026-08-05 — carry this forward

> *"The last session was not long-lived, but seemed to make a few errors along the way. Verify
> its work as you go."*

**This is not discharged by Task 8's verification pass.** It is a standing instruction about how
to treat inherited work on this branch, and it should govern Tasks 9–12 as well. Recorded here
because it was said in conversation and exists in no other file.

## Every number computed that is not in the retained log

Enumerated rather than filtered — the mid-flight rule. All of the Task 8 figures are in the log.
These three were computed and were **not** written down until now:

- **D6 standing layer, absolute:** **45,569 characters unconditional / 2,459 lines conditional.**
  Against `main`'s 45,333 / 2,417 that is **+236 / +42** — independently reproducing the Seam 2
  session's reported split, which is a corroboration of its arithmetic, not a new cost.
  **This session's own delta is zero**; it touched no standing-layer file.
- **The served artifact's sha256 was checked against its sidecar during verification** and
  matched (`4cb84ef9…`). This is the identity `CLAUDE.md` and the tiebreak-fix findings note
  already own — recorded here only as *"it was checked and it matched"*, never as a new figure.
- **Test suite counts at this HEAD:** 220 builder, 254 api. Frontend **was not run** — no
  frontend file has been touched on this branch.

## Decided against, with reasons — these leave no artifact and evaporate first

- **Fixing the duplicated `fame seed: …` log line.** Real but cosmetic (two call sites, one
  execution). Task 8 is specified *no source changes*, and editing shipped code outside a task's
  remit is its own defect class. **Deferred with a condition**: whichever task next touches
  `cli.py` — likely Task 9, which may add `--cap-strategy`.
- **Backing up to the CDK assets bucket.** CDK-managed; not a durable home for project data.
- **Backing up to a second machine.** None reachable from here.
- **Proceeding into Task 9 with low context.** Reasoning above.
- **Re-running `docs-lint`'s candidate figures as findings.** All pre-existing thresholds in
  preregistration specs; none introduced by this diff.

## Claims that must NOT be reverted by a well-meaning editor

Everything in the Seam 2 handoff's list of six still stands — **and four of them are now
verified by exercise rather than asserted**: the percentile frame's own-population rule, the
null-exclusion, the `trimmed_union` frozen pin, and `require_fame=False`. Do not "tidy" any of
them. Additionally:

1. **`--algorithm` is not optional on `fame` or `build` against the candidate archive.** Without
   it both read the *production* prefix and see 0 artists. `fame` then **exits 0 having done
   nothing**. Both commands are corrected in the plan; do not simplify them back.
2. **The plan's completion check for Task 8 is not sufficient alone** — `fetched + skipped =
   population` passes vacuously at zero. It needs an independently-established population count.
3. **Nulls price at percentile 0.0 and are excluded from the frame.** Measured consequence:
   including them would rank a 10-listener artist at 0.89 instead of 0.0.

## What has already been updated — do not re-edit

`docs/superpowers/2026-08-05-msw-execution-log.md` (new Task 8 section, D6 acceptance, the
verification table); `docs/superpowers/plans/2026-08-05-msw-package-adoption.md` (Task 8 ticked
and corrected, Task 9's command corrected); `NEXT.md`; `docs/README.md`; this note; and the
Seam 2 handoff's role line.

**`CLAUDE.md` was NOT touched and needs no correction yet.** Its "Graph shape" section is still
deliberately incomplete — it describes mutual k-NN without `trimmed_union`, which is accurate
about what ships today and becomes false at **Task 11**, where its correction is already listed.

## Owed, and by whom

- **Owner:** nothing. **D6 was accepted 2026-08-05** and is discharged; `CLAUDE.md` stands as
  committed. **Seam 3 (after Task 10) remains an OWNER STOP** before any default flips.
- **Next session — the next action is WORK: Task 9.** Its Step 1 is a deliberate red-check:
  remove one `fame/<mbid>.json`, confirm `build` refuses by name with `MissingFameError`, restore
  it. **`MSW-G3` has never gone red** — this is its first firing, and the whole point.
  **Commit the artifact's sha256 into the log immediately after building it**, in the same
  session, before doing anything else. That is the failure this handoff exists to prevent.
- **Task 9 may need to add `--cap-strategy` to `cmd_build`** — it does not exist yet
  (`p_build` currently takes only `--out`, `--algorithm` and the archive args). The plan
  anticipates this.
- **Task 11 Step 0, non-negotiable and unchanged:** era-pin `cap_strategy="mutual_knn"` **and**
  `require_fame=False` in `grt_score.py`, `calibrate.py`, `cre_build.py`, and correct
  `CLAUDE.md`'s Graph shape section in the same commit.
- **`MSW-V4` at Seam 3:** `ml-graph-analyst` dispatch on the percentile-frame deviation,
  derivation only.
- **Unchanged and not `MSW-`:** `ULC-F3` (crawl resume cannot extend) still blocks any crawl
  extension; `ULC-F4` (keep-check name resolution) is its own track; `ULF-3`'s first half is
  satisfied by Task 12, so the next closeout must **re-test** it rather than copy it forward.

## Anything in flight

**Nothing.** No background jobs, no dispatched subagents outstanding at the time of writing, no
half-written directories, no servers. The archive at `builder/scratch/grt-archive-algb/` now
carries a populated `fame/` subtree (98,056 records) — that is **finished, gitignored, and
intentional**, not a partial artifact.
