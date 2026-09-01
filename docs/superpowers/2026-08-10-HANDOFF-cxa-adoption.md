# Handoff — the extended graph is adopted and LIVE, 2026-08-10

**Role: SUPERSEDED — this is NOT the current handoff.** Superseded on **everything**, next
actions *and* status, by [`2026-09-01-HANDOFF-cxr-revert.md`](2026-09-01-HANDOFF-cxr-revert.md):
**the extended graph this note announces as live was REVERTED on 2026-09-01**, on the owner's
pre-set criterion, after three weeks of use. Everything below is accurate as a record of what
was done and why; **its present-tense claims about what production serves are false.**
Supersedes [`2026-08-10-HANDOFF-jfx-run.md`](2026-08-10-HANDOFF-jfx-run.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The `CXA-` track is complete to its last task, deployed, and verified in
production. **The degradation tell did not fire.**

Reasoning: [`2026-08-10-cxa-adoption-execution-log.md`](2026-08-10-cxa-adoption-execution-log.md).
Figures: `builder/analysis/2026-08-09-jfx-prereg-critique/README.md` (the measurement) and
`builder/analysis/2026-08-10-cxa-acceptance-bounds/README.md` (the fourth acceptance
artifact) — cited, never restated. Branch `crawl-extension-design`, **PR #91**.

---

## Start here

1. **The next action is the OWNER'S and it is USE** — the queued entry in
   [`TEST-QUEUE.md`](TEST-QUEUE.md), which carries his own revert criterion back to him.
2. **Nothing is blocked and no session owes anything.** Both owner stops were taken.

## What is done

All nine `CXA-` tasks. The bounds recalibrated on his `CXA-S1` decision; the re-censused
117,302-artist `ULF-` payload shipped and the ALG-B default repointed at it; the artifact
rebuilt through the shipped path and proved byte-identical (`CXA-G1`); the API default
flipped; artifact and sidecar uploaded to S3; the image built, `CXA-G2` verified **from
inside the container**, and pushed; the stack deployed on his `CXA-S2` go; the frontend built
and synced **with `--prune`, his call**; the use-test queued.

**PR #92's landing-dot fix is included and is live** — he asked for it. It was on `main` only;
`origin/main` was merged in and the image rebuilt at the merged commit so the tag records what
actually shipped.

**The live site serves the new map**: `/health` returns the `CXA-G1` sha, 88,685 artists,
1,618,164 edges; a public journey returns Radiohead → Nine Inch Nails → Aphex Twin; a middle
card resolves clip and cover art.

## Documents that are now wrong, and in which direction

- **Anything saying production serves `graph-msw-tu50.bin`.** It does not, as of 2026-08-10.
  The staleness direction is the same one `MSW-` recorded: *"nothing is adopted"* is now the
  stale claim, and the identical sentence inside a frozen `JFX-`/`CEX-` record is **correct**,
  because it describes what that track did. **Read for tense; grep cannot do this.**
- **Anything reading the `G1b` ratio as "the new map's gradient is shallower."** It is a point
  estimate and the difference spans zero.

## Claims that must NOT be reverted by a well-meaning editor

- **The shallower gradient is NOT established.** Adoption was taken with **no cost
  demonstrated**, not in spite of a measured one. Both halves travel together: this equally
  does not establish the gradients are equal.
- **The d20 famous-to-famous drift is POST-HOC** — where to look, never a finding.
- **`w_known_ramp_fame_pctl` stays 0.01.** Confirmed in the running image.
- **`JFX-B`'s manifest still says `DO_NOT_DEPLOY: true` and that is correct.** The shipped
  artifact is a different file from a new build. Do not edit the old manifest.
- **The ALG-E drop payload did not ship**, and the 75k-era ALG-B payload **stays in `data/`**
  — three era-pinned probes load it by name. Superseded as a default, not orphaned.
- **The edge floor in `acceptance.py` is now the ONLY bound that can catch a cap-rule
  revert.** The node bound cannot see one. Widening it to admit a build removes that
  protection silently.
- **Everything on the previous handoff's list still stands in full.**

## Already updated — do not redo

`acceptance.py` (bounds + the four-artifact comment), `unlistenable_drop.py` (repoint), the
shipped payload, three test pins, `ApiConfig.graph_path` and its name pin, `infra/README.md`
§4, `TEST-QUEUE.md`, `NEXT.md`, `docs/README.md`, this handoff and the execution log.

## What I know that is not in the durable record

**Nothing of substance.** Everything is in the execution log, including the three plan
defects (§3), the `--require-approval never` decision (§6), and the `--prune` reasoning (§1).

One operational note that will bite a successor: **`--require-approval never` is NOT routine.**
It was passed because CDK prompts on IAM broadening, stdin is null in this harness, and the
owner had seen the full IAM delta. A session that passes it without showing him the delta has
skipped the check, not automated it.

## Anything in flight

**Nothing.** No background jobs, no subagents. **No listeners: nothing was started on any
port this session and nothing was left behind** — the app was exercised against the live
address, not locally.

## Open, and not this session's

- **The queued use-test** — his, and the only thing outstanding.
- **`SEL-R1`–`R4`**, **the rank-asymmetry idea**, **the dead `ROOT` in
  `analysis/2026-07-23-acceptance-bounds/check.py`**, **`CLIP-1`** (exposure expected to rise)
  — conditions in the execution log §8.
- **`CEX-F1`**, **`CEXR-6`'s `load_deezer_ids` half**, **`CEX-R3`**, **`FE-SNYK-1`**,
  **`SNS-1`** — unchanged and untouched here.
- **The 2026-07-29 famous-to-famous defect ruling** — still open, still his.
- **PR #91 is open and now carries the whole `CXA-` track.** Merging it is the natural next
  bookkeeping step.
