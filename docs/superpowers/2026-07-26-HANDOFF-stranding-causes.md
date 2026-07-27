# Handoff — why the low-degree artists are low-degree, 2026-07-26

**Role: COMPLETE — superseded on next actions** by [`2026-07-26-HANDOFF-deliverability.md`](2026-07-26-HANDOFF-deliverability.md).
**Still the record of the stranding-causes seam**, and its do-not-revert list stands.
Path-quality work is PAUSED and this is not a resume signal. *(Role line added 2026-07-27.)*

**Written at a clean seam. Nothing is in flight** — no dispatched subagents, no
background jobs, no half-written directories. Committed and pushed; PR #25.
Aimed at a session that has never seen this work.

Governing documents, in order: the execution log
[`2026-07-26-stranding-causes-execution-log.md`](2026-07-26-stranding-causes-execution-log.md),
then [`findings/2026-07-26-stranding-causes.md`](findings/2026-07-26-stranding-causes.md),
then the deliverable `builder/analysis/2026-07-26-stranding-causes/REPORT.md`.
**Where they disagree, the execution log wins.** Identifiers: **`STC-`**.

## What is now true that was not

**The reason recognisable artists are stranded is not the reason most stranded
artists are stranded.** The census counted them; this says why, and the two
causes named in the original framing turned out to be three. `STC-1` is the
headline and `STC-3` is the rule for reading it: the set is dominated by
unreachable artists *by headcount* and by rule-fixable ones *by who anyone would
recognise*, and **neither half may be quoted without the other.**

## Which documents are now wrong, and in which direction

- **Nothing is wrong.** No prior claim is overturned; this is additive.
- **`docs/README.md`** gained one row. **`findings/2026-07-25-mutual-knn-stranding.md`
  is explicitly NOT invalidated** by `STC-5` — see below.

## Claims that must NOT be reverted by a well-meaning editor

1. **`STC-6` is a correction this session made to its own earlier draft, and the
   withdrawn version is the intuitive one.** "The similarity source knows nothing
   about these artists" is **wrong**; it knows nothing *above a co-occurrence
   threshold this project chose* (`BuilderConfig.algorithm` carries
   `threshold_10` and `limit_100`). An editor tidying the prose will be tempted
   to restore the simpler claim. It is false, and the check that kills it is in
   `REPORT.md`.
2. **The length limit is not a confound and this was checked, not assumed.**
   `limit_100` binds for a large minority of artists but **cannot** produce a
   short list, because truncation only shortens long ones. Do not re-open it as
   an objection to `STC-1`.
3. **`STC-5` does not invalidate the 2026-07-25 stranding findings.** The
   `reciprocity.py` limitation is real and corrected here, but the placeholders
   are a single-digit count in the whole crawled population — far too few to move
   any distribution that document reports, and none of its six gated artists is
   affected. Do not attach a warning banner to it.
4. **The ten-artist residual was left deliberately, not overlooked.** See the
   log's D-6. `verify_residual.py` exists so the two settled explanations stay
   checkable; it is not an invitation to chase the rest.
5. **The population boundary is a stated choice, and the eleven-row sensitivity
   table is the point.** Do not replace it with a single number.

## What has already been updated — do not re-edit

`docs/README.md` (one row), the findings document, this handoff, the execution
log, `TEST-QUEUE.md` (one entry), and
`builder/analysis/2026-07-26-stranding-causes/README.md`. **Memory was not
touched** and the standing context layer is net zero.

## What I know that is not in the durable record

Checked deliberately. Three items, all folded in above or into the log rather
than left here — restated for a cold reader:

- **The first version of this report was fluent, self-consistent and wrong in its
  headline.** What caught it was reading the generated output and noticing an
  artist with one candidate who was listed by dozens of others. Reviewing the
  *code* would not have caught it; the missing quantity was never computed.
- **`artifact_nodes.json` is gitignored on purpose**, by a `.gitignore` **inside**
  its directory, which is branch-scoped and therefore invisible from a branch
  where that directory does not exist (`CLM-13`). Do not report it as unbacked;
  regenerate it in seconds instead.
- **Why the run takes ten minutes and cannot easily be made faster:** two full
  archive scans plus a per-artist re-read, over 75,000 files on OneDrive. The
  cache must be cleared periodically or the run is not memory-safe. Going wider
  is not the fix.

## The open decision, and what I would do

**Nothing here blocks anything, and no decision is urgent.** Two success
conditions are parked and neither is due:

- **`STC-5`** — any reuse of `reciprocity.py` that depends on an individual
  artist's candidate list applies the placeholder exclusion first.
- **`STC-6`** — if a re-crawl is ever considered *for any reason*, the
  co-occurrence threshold is examined at the same time, because the crawl is the
  only moment it can be changed.

**What I would do if I were continuing: nothing here.** The measurement is
complete and the next thing this project needs is use, not more analysis. The
genuinely interesting follow-on — what a lower threshold would actually yield —
costs a full re-crawl, and I would not start it without the owner deciding that
the stranded-artist problem is worth that. **What would change my mind:** the
queued use-the-app checks coming back with the owner unable to find or route
through artists he cares about, which would turn an abstract population into a
specific complaint and make the re-crawl question concrete.

## What was decided against

- **Chasing the ten-artist residual** — bounded instead; it cannot move the split.
- **Shipping the fetch-truncation question as open** — it was run, and became
  `STC-6`.
- **Editing `.claude/agents/ml-graph-analyst.md`** — re-read against this work and
  found already correct; it carries no figures by design.
- **Attaching a caveat banner to the 2026-07-25 stranding findings** — `STC-5`
  does not reach it.
- **Proposing any rule change.** `STC-4` measures what one would reach; it does
  not recommend one, and path work is paused regardless.
