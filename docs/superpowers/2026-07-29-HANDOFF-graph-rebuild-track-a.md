# Handoff — graph rebuild Track A executed, 2026-07-29

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-29-HANDOFF-reciprocity.md`](2026-07-29-HANDOFF-reciprocity.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**This is a seam handoff, not mid-flight.** The plan was written and executed to its last
task in one session; every gate was reached and read. Nothing is in flight, no subagent is
running, no server is up on any of the four ports (all swept, all empty), the tree is
clean.

## What happened

The rebuild plan the previous handoff asked for was written
([`plans/2026-07-29-graph-rebuild-track-a.md`](plans/2026-07-29-graph-rebuild-track-a.md))
and then executed inline: six tasks, `GR-1`–`GR-6`. Retained log:
[`2026-07-29-graph-rebuild-track-a-execution-log.md`](2026-07-29-graph-rebuild-track-a-execution-log.md).
Pre-registration for the experiment:
[`specs/2026-07-29-algb-trial-build-preregistration.md`](specs/2026-07-29-algb-trial-build-preregistration.md).

Three builder changes shipped (drop rule, `--algorithm`, algorithm-scoped archive keys),
a full production rebuild passed acceptance, and the `ALG-B` trial build ran against a
coverage-matched control.

## What the next session does

**Its first job is a decision the owner has not yet made, so do not assume one.** The
natural next work is **Track B — the cap-selection simulation** (strand 3, still owed
under `MKS-5b`), which now has two new inputs it must consume: `GRT-P2` (below) and
`RC-A2`. It needs its own plan and its own pre-registration, and it can re-score
`rc_raw_records.json` at different `k` without re-fetching anything.

**But the `ALG-B` re-crawl decision itself is closer than it was, and it is PARKED —
his trigger, never a session's.** What this track added to it is priced evidence, not a
recommendation.

## Overturned or corrected claims a well-meaning editor must not revert

- **`RC-P2` is confirmed on its mechanism and REFUTED on its consequence.** R.E.M. holds
  **6** connections under `ALG-B` against **47** in the coverage-matched control — the
  collapse is real and larger than sampling suggested. **But the build does not refuse.**
  Do not restore any wording that says an `ALG-B` artifact would be rejected by
  `check_acceptance`; at trial scale both predicted clauses pass.
- **`GRT-P2` — and this is the finding to carry forward.** The reason the build does not
  refuse is that **popularity is score-weighted in-degree**, so an artist that loses its
  edges loses its popularity in the same motion — R.E.M. falls from popularity rank 7 to
  rank 62 and drops *out of* the top-25 sample that `famous_min_degree_floor` inspects.
  **The guard is structurally unable to see the collapse it was written for, once the
  collapse is severe enough.** A mild collapse is caught; a total one is invisible.
  **Not established at production scale** — rank among 2,904 is not rank among 74,000 —
  and that is the sharpened live question.
- **`GRT-P1` — `GRT-C4`'s effect size is broken and the null does not fire cleanly.** The
  bar was a ratio (`AB ≥ 2 × A0`) and the control's readable exclusion rate is exactly
  **zero in every band**, so the ratio is undefined and every band returned "not
  decisive" — including one where `ALG-B` strands 2% of readable top-decile artists and
  the control strands none. **The pre-registered verdict is left standing as written.**
  Do not re-label it in either direction. A successor owes an absolute-difference bar.
- **The production archive is NOT closed under one-hop neighbours** (`GRT-A1`). Measured:
  5 of 3,000. Small, but a naive control arm tried to extend the irreplaceable archive
  and was stopped by a structural guard. Any future harness pointing a crawler at
  `builder/scratch/graph-archive/` must wrap it read-only.
- **A full build takes ~29 seconds, not the ~2 minutes** the RC log §6 records.
- **The drop rule removes 36 artists, not 33**, and both figures are correct — they count
  different populations (pre-prune vs emitted). Do not "fix" either. Three real artists
  are pruned as stranded neighbours; that clause now has production evidence.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `docs/README.md` (four new rows), `TEST-QUEUE.md`
(N/A entry), the previous handoff's role line, `acceptance.py`'s deferral (discharged in
place), and the plan's own status line (marked executed).

## What I know that is not otherwise in the durable record

- **`snyk_code_scan` never ran.** The Snyk CLI is unauthenticated here and authenticating
  is a browser flow only the owner can complete. The global instruction requires it on
  new first-party code, so it is **owed on the `GR-1`/`GR-2`/`GR-3` diffs** — flagged in
  each commit message and in the execution log §8, but nothing enforces it. This is the
  one genuinely open hygiene item.
- **Decided against, with reasons**, so a successor does not redo the reasoning:
  target 5,000 for the trial crawl (the calibration shows the top-0.1% readable core is
  **75 artists at both 3,000 and 5,000**, so the extra ~27 minutes buys nothing on the
  famous side, which is where every read lived); running the control arm from a fresh
  archive (would re-fetch 3,000 responses already on disk); a `SubsetArchive`-free scorer
  (see below); touching `k` in response to `RC-A2` (`MKS-5b`).
- **The scorer had a real defect, caught by a dry run against the control arm before the
  trial arm finished collecting.** `build_from_archive` reads *every* key under its
  prefix, so the control was building the whole 74,157-node production graph rather than
  its 3,000-node capped one — which would have restored the exact two-column confound the
  factor table exists to prevent. Two impossible figures exposed it (exclusion rate
  −23.76, fetch rate 1.0017). **The lesson is transferable: dry-run a scorer against the
  cheap arm while the expensive one is still running.** It cost nothing and the fix could
  not have been shaped by a result that did not yet exist.
- **The corrected control cross-validates against an independently written harness** —
  2,959 nodes / 53,902 edges against the trial-crawl calibration's 2,958 / 53,900 at the
  same target. Two harnesses, two sessions, agreeing to within one node. That is the
  strongest evidence the `GRT` pipeline is sound, and it is worth re-running if anything
  in the builder changes.
- **The production crawl's checkpoint no longer exists in this tree** — only the archive
  does. So `GRT-A1`'s mechanism (a resumed crawl rebuilds its frontier as
  `sorted(discovered − done)` rather than in BFS order) is a **hypothesis**, while the
  coverage gap itself is measured fact. Anyone wanting to settle it needs a checkpoint
  that is gone.
- **Nothing the owner said in conversation is missing from a file.** His MusicBrainz check
  on the three nameless MBIDs ("Artist not found" on all three) is recorded in the
  execution log §2 and in `pipeline.py`'s comment, and it is what upgraded the drop
  decision from preference to only-available-option.
- **⚠ ONE THING IS IN FLIGHT, started after this handoff was first written.** A **full
  `ALG-B` crawl to 75,000 artists**, launched late 2026-07-29 on the owner's explicit
  instruction, running detached and owned by nobody:

  ```
  uv run artistpath-build crawl --bootstrap ./scratch/bootstrap.json \
    --archive-dir ./scratch/grt-archive-algb \
    --algorithm <ALG-B> --checkpoint ./scratch/checkpoint-algb-full.json
  ```

  **It is collection only** — it fills `scratch/grt-archive-algb/` and builds nothing,
  adopts nothing, and cannot reach the production archive (`GR-3` scopes the keys).
  **~7.6 hours** at the endpoint's measured speed, and it **resumes cleanly** if
  interrupted: re-run the same command. It began by serving the trial's 3,000 responses
  from disk without a single fetch, which is the expected and correct start.

  **The record's "4¼ hours" for a full crawl is stale** — that was measured when the
  endpoint ran ~4× faster (0.141 s/artist against tonight's 0.367 s including the delay).
  `NEXT.md` still carries the old figure in its PARKED section; treat 7.6 h as current.

  **A fresh checkpoint path was mandatory and this is a live trap for anyone re-running
  it.** Reusing `grt-checkpoint-algb.json` (the trial's, 3,000 discovered / 3,000 done)
  makes the crawl **finish instantly having done nothing** — the pending queue rebuilds as
  `discovered − done` = ∅ and every bootstrap seed is already marked discovered. It looks
  exactly like success.

- **Everything else is finished and static.** Two gitignored trial archives and their
  checkpoints in `builder/scratch/` (`grt-archive-algb/` — now also the destination of the
  running crawl, `grt-overlay-alge/`, `grt-checkpoint-*.json`) plus the verification
  artifact `graph-dropnameless-verify.bin`. All regenerable — the artifact in 29 seconds.
