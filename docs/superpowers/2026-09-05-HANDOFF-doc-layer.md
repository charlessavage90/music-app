# Handoff — the doc layer's accumulated history, split out and audited, 2026-09-05

**Role: ⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-05 (later) by
[`2026-09-05-HANDOFF-lux-e1-and-lux-4-plan.md`](2026-09-05-HANDOFF-lux-e1-and-lux-4-plan.md)** —
**its "Start here" is SPENT: item 2, `LUX-E1`, HAS RUN and returned byte-identical, and item 1's
deferral condition fired during that run.** Everything it records about the doc-layer
restructure remains accurate, and its must-not-revert list stands in full. *(Original role:
**ACTIVE — this is the CURRENT handoff.** Nothing supersedes it.)* Supersedes
[`2026-09-04-HANDOFF-lux-1-3.md`](2026-09-04-HANDOFF-lux-1-3.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The work concluded; the degradation tell did not fire. **No app code
changed** — this was a maintenance session throughout, and its closeout was the maintenance
tier. Reasoning is in the commit messages rather than an execution log (that tier skips A1).

Branch `next-md-merge-status`, **PR #102**.

---

## Start here

**Nothing is assigned and nothing is blocked.** Three pieces of work came out of this session
and all three are for a later session; each is recorded where it will be found, not only here.

1. **Record which drop lists built a graph** — builder code, small, purely additive. It is a
   **deferral with a condition** in `NEXT.md`'s table. The owner explicitly wanted this to be
   another session's work.
2. **`LUX-E1` with its new second arm** (`LUX-E1-AM1` in the scope document, committed before
   either arm ran). ~23 min, offline, adopts nothing.
3. **`docs/README.md`'s row discipline** — see "not in the durable record" below.

## What this session changed

- **`NEXT.md`: 2,063 → ~370 lines.** 38 superseded status blocks moved to a new frozen
  `NEXT-ARCHIVE.md`. It had grown monotonically from 150 lines on 2026-07-30 because
  "rewritten wholesale" was being applied to the *top block* while the outgoing block was
  demoted inline and then re-annotated every closeout.
- **`TEST-QUEUE.md`: 1,996 → 141 lines**, same shape, same fix; discharged entries now in
  `archive/TEST-QUEUE-discharged.md`.
- **`closeout` gained `A2-next` and `C1-demote`**, the steps that make both stick — including
  **"distil before you demote"**, whose absence caused the growth. `session-start` §C gained
  the `gh` derivation.
- **`NEXT.md`'s registries audited against source**: 8 stale claims corrected, 17 verified.
- **A new measured finding** about the `CXR-` revert (below).

## Claims an editor must NOT revert

- **`NEXT.md` owns no git state.** Merge state, branch existence, what landed — `gh` and
  `git` own those, and `session-start` §C derives them. Re-adding "PR #N is open and not
  merged" restores the defect: closeout runs *before* the owner merges, so anything written
  there is false within the hour and every fresh session then opens by reporting a false
  alarm.
- **Both archives are FROZEN.** `NEXT-ARCHIVE.md` and `archive/TEST-QUEUE-discharged.md` are
  never edited and never re-annotated. Something load-bearing found in one is a
  **distillation defect to fix forward** in the live document — not a reason to edit the
  archive.
- **`BYP-13`'s fix is LIVE, not inert.** The served artifact `graph-msw-tu50.bin` carries
  `deezer_ids` for all 58,838 artists, read from its own metadata blob. The registry said
  "INERT until a rebuild" and "the defect is unchanged in the running app" for a month. Do
  not restore either.
- **`ALG-B` is the adopted map's lineage** and has been since 2026-08-06 (`config.py` says so
  in as many words). It was listed as a *pending owner decision*; do not put it back.
  Separate from what is still open: `BuilderConfig.algorithm`'s ALG-E **default**, which is
  the re-crawl decision and is his.
- **`cap_strategy` is `trimmed_union`**, not `mutual_knn`.
- **`LUX-E1`'s default arm is predicted RED** — reading arm A alone is uninformative. Arm B
  is the diagnostic one. Do not run A alone and report it as a result.
- **The 31-node figure is owned by
  [`builder/analysis/2026-09-05-lux-e1-drift-source/`](../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md)**
  and is cited, never restated.

## The revert question, since it will come up again

The owner asked whether the `CXR-` revert returned the app to its exact pre-expansion state.
**The map did**: same file, same sha, and every routing weight identical. **Two things did
not**, and both are recorded in `NEXT.md`:

- The landing-dropdown UI fix rode along and was never reverted. Deliberate — he instructed
  it to ship.
- **The running image still defaults to the REJECTED artifact.** Nothing is served wrong
  (production sets `ARTISTPATH_GRAPH` explicitly and `DEP-34-FIX` refuses a synth without the
  key), and any image built from HEAD fixes it — but do not deploy under a stale image tag.
- **The drop list was not reverted either**, which is finding 5 and the origin of
  `LUX-E1-AM1`.

## What has already been updated — do not re-edit

`NEXT.md`, `TEST-QUEUE.md`, `docs/README.md` (three new rows), `closeout` (`A2-next`,
`C1-demote`, `D6`), `session-start` (§C and the test-queue bullet),
`specs/2026-09-03-launch-ux-scope.md` (`LUX-E1-AM1`), and `~/.claude/CLAUDE.md` (two rules,
+888 characters, the owner's call and taken).

## What I know that is not in the durable record

**One thing, and it is a measurement worth keeping.** `docs/README.md` is **336 KB — the
largest document in the project** — and 95% of it is table rows: **275 rows, median 1,180
characters.** It is also the document `CLAUDE.md` tells every session to read first. A probe
of its longest rows against the documents they describe found **15/19, 25/25 and 17/17** of
the identifiers in a row also present in the document: the rows are not routing, they are
restating. That is the one-document rule violated in prose, and it drifts the same way —
last session's audit found a HIGH where the *document* had been updated and its *row* had
not.

**The recommendation, and the owner agreed to leave it to a future session:** do not strip
the map — the summaries genuinely earn their place, they are what lets a reader decide
whether to open a 105 KB execution log. What is missing is a **rule about what belongs in a
row versus in the document** — role, supersession, what it owns, and the one thing a reader
must not get wrong. Applying it going forward is free; retrofitting the **22 rows over 2,000
characters** is about an hour and captures most of the win. Rewriting all 275 is not worth
it. This is now also a deferral with a condition in `NEXT.md`.

**One smell, unchecked and deliberately not concluded on:** there are **74 handoffs to 60
execution logs.** If a handoff is a delta against a retained log there should not be more of
them than logs. That may be entirely explained by mid-flight retirements; I did not check.

**Nothing is in flight.** No subagent is running, no background job, no partial directory.
**Nothing is running on any port** — no server was started this session and none survives.
