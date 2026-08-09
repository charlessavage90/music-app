# Handoff — the `CEX-` crawl extension, Tasks 1–10 complete, 2026-08-08

**Role: ⚠ SUPERSEDED 2026-08-09 ON NEXT ACTIONS by
[`2026-08-09-HANDOFF-cex-task11.md`](2026-08-09-HANDOFF-cex-task11.md), which is the CURRENT
handoff — Task 11 is now COMPLETE and this note's "Start here" describes work that is done.
Its "Claims that must NOT be reverted" list is NOT superseded and still stands in full.**
*(Original role:)* **ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-08-HANDOFF-cex-design.md`](2026-08-08-HANDOFF-cex-design.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff** — the plan's own seam, after Task 10. The archive is a committed durable
artifact rather than a live understanding, nothing is in flight, no port is listening, and the
degradation tell did not fire. **The successor executes Task 11 cold — that is the intended
shape, not a fallback.**

Reasoning: [`2026-08-08-cex-crawl-execution-log.md`](2026-08-08-cex-crawl-execution-log.md).
Governing document: [`specs/2026-08-07-crawl-extension-design.md`](specs/2026-08-07-crawl-extension-design.md).
Operational document: [`plans/2026-08-08-crawl-extension.md`](plans/2026-08-08-crawl-extension.md).
Branch `crawl-extension-design`, **PR #91**.

---

## Start here

1. **Task 11 of the plan** — fame, re-census, build. It is the last task and it **ends at an
   owner stop**.
2. **Every command in it passes `--algorithm` explicitly** (`CEXR-2`). `_config` defaults to
   ALG-E, `similar_prefix` selects the tree from it, and **there is no `RC-H3` guard on the
   build side** — a defaulted build reads the wrong archive and could pass acceptance while
   describing a population nobody asked for.
3. **Step 1 before Step 3:** cost the re-census on the first 500 artists and report the
   estimate *before* running the full pass (`CEXR-9`). If it lands in hours, that is a second
   seam and the owner's call.

## What is done, and what the numbers are

**Tasks 1–10 are complete and pushed.** `CEX-1` through `CEX-5`, `CEX-M1`, gates `CEX-G1` and
`CEX-G2`, and the crawl. Builder 241 tests, API 261, Snyk clean.

**Figures live in `builder/analysis/2026-08-08-cex-g1/` — `g1_result.md` and `crawl_result.md`.
Cite them; do not restate them here or anywhere else.**

## Documents that are now wrong, and in which direction

- **`ULC-F3` is DISCHARGED.** Older handoffs and execution logs calling it "blocks any crawl
  extension" are **correct for their own date and must not be edited.**
- **`config.py:17` is FIXED** — the previous handoff and `NEXT.md` said it was stale in the
  tree. That is now false, and `NEXT.md` has been rewritten.
- **Anything describing `--target` as capping *discovery* is stale.** Three places were
  corrected (`cli.py` help, `builder/README.md`, `CLAUDE.md`); a fourth class — frozen probes —
  was era-pinned rather than edited.
- **The ALG-B archive is no longer 75,000.** Any present-tense claim that it is describes the
  pre-crawl world. `memory/`'s crawl-resume entry has been corrected.

## Claims that must NOT be reverted by a well-meaning editor

- **`exhausted: false` in the checkpoint is CORRECT.** The crawl stopped on the fetch cap with a
  non-empty queue, so the graph was not crawled out. Do not "fix" it to `true`.
- **`grt_run.py` refuses to run, deliberately.** Its era pin is a refusal rather than a config
  value because the old behaviour was deleted from `crawl.py`'s loop, not defaulted. Do not
  remove the guard to "unbreak" it.
- **`calibrate.py`'s `_replay` is deliberately left on the OLD stopping rule.** It reproduces
  its own committed cells; updating it to match `crawl.py` destroys exactly that.
- **The `algorithm` default stays ALG-E.** Flipping it is the re-crawl decision and is the
  owner's, even though ALG-B is the adopted lineage.
- **Do not widen the acceptance bounds** when the Task 11 build is rejected. `MSW-G3` is the
  precedent and there too it was the owner's.

## Already updated — do not redo

`NEXT.md` (rewritten), `docs/README.md` (two new rows), the previous handoff's role line,
`CLAUDE.md`'s `--target` line, `builder/README.md`, `builder/analysis/README.md` (the `CEX-G2`
pin narrative), `memory/MEMORY.md` and `memory/crawl-resume.md`, and `TEST-QUEUE.md` — whose
top entry the owner **discharged**, so the queue is now empty.

## What I know that is not in the durable record

**Two things, both now folded into the execution log rather than left here** — the empirical
confirmation that the frontier drains in sorted-MBID order (§7), and the observed crawl rate of
~3.0/s against a configured 5/s, which is what makes the 4-hour estimate rather than 2.4.

One thing worth repeating because it will bite a successor: **stopping a background `npm run
dev` task does not free the port.** The wrapper dies and Vite's child node process keeps
listening. Sweep by listener, never by task list — `closeout` A5 says this and it was observed
live this session.

## Anything in flight

**Nothing.** No subagents beyond this closeout's `doc-auditor`, no background jobs, no
listeners: ports 8000, 5173 and 5174 swept and **free**. The crawl finished and exited 0.

**Reversibility is intact and verified after the crawl:** the snapshot at
`builder/scratch/grt-archive-algb.pre-cex-snapshot` still holds exactly 75,000 responses, and
`checkpoint-algb-full.json.pre-cex` is unchanged. Both are gitignored; their identity is
recorded in `g1_result.md`.

## What I would do if I were continuing

**Task 11, Step 1 first and stop there if it is expensive.** The re-census is the only uncosted
step in the whole track and it is per-artist against rate-limited services over ~42,000 genuinely
new artists. Measure 500, extrapolate, report. I would not start the full pass without telling
the owner what it will cost.

Then fame (seconds), re-census, build — and **expect the build to be rejected on both bounds.**
That rejection is the designed outcome, not a failure to fix.

## New and open — `CEX-F1`, found at this closeout

**A crawl whose target is already at or below `done` logs `0 processed` and exits 0, with a
non-empty frontier.** `CEX-3`'s refusal does not cover it — that fires only on an empty queue.
**`target_artist_count` still defaults to 75,000 and `done` is now 117,302**, so
`artistpath-build crawl` without `--target` against this checkpoint does nothing, silently,
with ~11,293 artists waiting.

Verified rather than reasoned; the shape is **pre-existing**, not a `CEX-2` regression. Not
fixed here — the remedies are a default change (the owner's) or widening `CEX-3`, and neither
belongs in a closeout. **Condition and full detail: execution log §8.** Due before the next
crawl extension.

## Open, and not this session's

- **`CEXR-6`'s `load_deezer_ids` half.** No population argument, so every one of the ~42,000 new
  artists falls back to name-based clip resolution (`BYP-13`). A coverage regression, not a build
  failure. Its own track.
- **The search defect (`CEX-R3`).** Its own track, and still **the only lever that addresses "I
  cannot find this artist" for artists that are present.** Needs no rebuild.
- **The cap-rule question**, **`DD-F1`**, and **`CLIP-1`** — all unchanged by this work.
- **PR #92** (`landing-dot-z-order`) is open and unmerged: the landing-page dot fix the owner
  verified locally. Merging and deploying it is his call. It is **not** part of the `CEX-` track.
