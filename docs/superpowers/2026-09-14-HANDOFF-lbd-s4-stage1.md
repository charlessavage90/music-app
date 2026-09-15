# Handoff — `LBD-S4` stage 1 complete, 2026-09-14

**Role: ⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-15 by
[`2026-09-15-HANDOFF-lbd-s4-stage2.md`](2026-09-15-HANDOFF-lbd-s4-stage2.md) — `LBA-D8` stage 2
has since RUN. ACTIVE for everything else it records**, and its claims-not-to-revert list still
binds. ⚠ **Its statement that "stage 2 has not begun" is now false**, as is its list of what a
fresh session owes if stage 2 runs — all five items are discharged. **Its `LBA-G2` warning is now
answered:** that gate had no result when this was written and now has one on every cell.
*(Original role:)* **ACTIVE — was the CURRENT handoff until 2026-09-15.** Supersedes
[`2026-09-14-HANDOFF-lbd-s4-prereg.md`](2026-09-14-HANDOFF-lbd-s4-prereg.md) on next actions. It
does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

⚠ **One claim in this note is now known to be wrong, and it matters to anyone reusing the
instrument.** Its task-5 line that the stage-2 peak-RSS instrument was *"written and self-tested"*
is true of what it asserted and **incomplete**: that module raises `TypeError: 'Event' object is
not callable` on **every real build**, and its self-test could not reach the failing path.
`builder/analysis/2026-09-14-lbd-s4-stage2/s4_instrument.py` is the corrected forward copy and
supersedes it for any future use.

**A seam, and a clean one.** `LBA-D8` **stage 1 is complete**; **stage 2 has not begun**. Nothing
was emitted, built or censused, no journey was generated and no listen designed. The successor
reads this cold, which is the condition it was written for.

**It owns no figures.** They are owned by
[`builder/analysis/2026-09-14-lbd-s4-stage1/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage1/README.md).
Reasoning is [`2026-09-14-lbd-s4-stage1-execution-log.md`](2026-09-14-lbd-s4-stage1-execution-log.md).

---

## What happened

**Governing document unchanged:** `specs/2026-09-14-lbd-s4-adoption-preregistration.md` (`LBA-`).
**One amendment was added — `LBA-AM2`, §11** — and it must be read before anything in §3 or §5.

1. **Every pinned artifact verified** (`LBA-D9`): 14 files, all match, nothing refused.
2. **All nine cells derived and counted.** The threshold-7 table was the only one that did not
   exist; `lbd_derive.py` was run unedited via the `LBD-AM5-2` wrapper pattern. The two reused
   cells reproduce **all eight** of their committed figures — the instrument's green check, and a
   refusal condition.
3. **`LBA-G3` FIRES** — *working out which artists are unplayable would take too long* — on both
   its two-point fit and its single-point sensitivity, each a multiple of the 6-hour bar.
4. **`framework_rss` measured**, for the first time in this project.
5. **The stage-2 peak-RSS instrument written** and self-tested, as a forward copy.

## ⚠ The four things a reader is most likely to get backwards

**1. `LBA-G3` firing is a resource fact, not a finding about any arm.** It says the offline census
pass would take too long to run here; it says **nothing** about whether any map is good, servable
or worth adopting. Its consequence is narrow and pre-committed: the pass is not started, and
`LBA-M4`'s class share for the uncovered part is **estimated** and labelled.

**2. The six `V` and `P` arms are fully covered by the census store — and that still does NOT give
them a *measured* class share.** Their uncovered count is 0, so no census work is owed for them.
But with no pass run, **nothing is freshly evaluated**, so every verdict they would read is a
**carried** one, from censuses taken against **earlier MusicBrainz snapshots than the pinned
`20260905-002519`**. `LBA-M4`'s own ⚠ reserves the word *exact* for the fresh share; after this read
there is **no fresh share at all**. Do not let "0 uncovered" read as "measured".

**3. `LBA-G2` has NO result, and `LBA-R0` is not reachable from stage 1.** Stage 1 produced
`LBA-G2`'s **x-axis** (archive neighbour rows per cell) and nothing else. Its y-axis — an
instrumented build peak — does not exist for any cell. `LBA-AM2`(a) settles this; §3's *"both
`LBA-G2` and `LBA-G3` read off it"* is read as *stage 1 produces the input*, which is literally
true of `LBA-G3` and true only of the x-axis for `LBA-G2`.

**4. Every `U` figure is TABLE-LEVEL and is an upper bound.** §2.1 defines `U` after the drop lists
and after the largest-component prune; the prune needs a build. Conservative in the right direction
for a feasibility gate, and **not** a node count.

## `LBA-AM2`, and the one thing about it a successor must not smooth over

It resolves two conflicts in the committed text: how `LBA-G2`'s first projection is obtained, and
which of two stated stage-2 orders governs (§3's `A1, A4, A7, …` is **not** §5's ascending
archive-neighbour-row order, and under §3's the second build is a 2× extrapolation from a single
point). It fixes the fit rule as code, **changes no bar, and reduces nothing.**

> **It cannot claim `LBA-AM1`'s position and says so in its own text.** `LBA-AM1` could say
> *"nothing had run"*. `LBA-AM2` was written **after stage 1 ran**, by an author who knew every
> cell's row count — `LBA-G2`'s x-axis. What did not exist is the **y-axis**. So it spends none of
> `LBA-G2`'s commit-before-results property, and it is **not** written in ignorance of the cells'
> sizes. **Do not later describe it as having been written before results existed.**

## Claims not to revert

- **`LBA-D8`'s prohibition stands: a cell is stopped only on `LBA-G2`'s stated bar.** Not for being
  dominated, not for cost. `LBA-A9` is the corner and the only cell that can say *"there is no
  bigger map to have inside these rules."*
- **`LBA-A1` and `LBA-A3` are reused, sha-verified, not rebuilt** — rebuilding adds a build-date
  column the factor table does not have.
- **Ascending build order costs `LBA-D8`'s rationale nothing.** Both reused cells sit on the `V`
  row, so the complete `V` row exists **after the first build**, and the `P` row — which carries the
  only two one-column threshold reads `LBA-AM1-A9` admits — completes earlier than under §3's order.
- **`framework_rss` is not population-independent.** Use the README's decomposition (a constant part
  plus a per-artist part), not the single figure, for any arm larger than the served map. The
  per-artist term is the noisiest quantity measured and is an order of magnitude, not a rate.
- **One build per process in stage 2.** `PeakWorkingSetSize` never falls; the instrument enforces
  this rather than trusting the caller.
- **Nothing here re-reads any `LBD-` criterion**, `LBD-C1` is not cited as passed, `LBD-X6` stands,
  and the two `LBL-` verdicts remain run-once.

## What I know that is not in the durable record

1. **Stage 1 is minutes, not hours.** DuckDB prunes columns, so a cell costs seconds against the
   21 GB `T`. The threshold-7 derivation took 54 s; every count in the nine-cell table took under
   1.5 s. The only slow item in the whole session was hashing `T` (21 GB). **Budget stage 2 on the
   builds, not on the queries.**
2. **Two instrument defects in `framework_rss` each returned a plausible-looking number**, and the
   first was caught only because one component came out negative. Both are written up in the
   execution log's task 5. If a successor re-measures memory anywhere, read that first.
3. **The self-test for the build instrument was itself wrong at first** and failed the instrument
   for being correct. A test can be as wrong as the thing it tests.
4. **`git add -A` is blocked by a hook here** and the block aborts the *whole* Bash call — including
   anything that ran before it in the same command. An append that preceded a blocked `git add` in
   one invocation silently did not happen; it was caught by grepping the file afterwards. **Commit
   with a pathspec, and keep file writes in their own call.**
5. **A path-scoped rule fired** — `.claude/rules/plans.md` loaded when this session opened the
   pre-registration. That is the `DLS-T1` probe's observation, and it is now made.
6. **The duckdb venv is `C:\unsung-fast\lbd-venv`**; the api package's own `.venv` is what
   `framework_rss` must be measured in.

## Nothing is in flight

No background jobs, no dispatched subagents, no half-written directories, no listeners on 8000 or
5173 — this session booted no app beyond the three short in-process `framework_rss` measurements,
each of which exited. **No graph was built, no archive emitted, no pass run, no census run.** The
census coverage store was **read and not written**; its sha256 is identical before and after.

## Artifacts

| what | where | identity |
|---|---|---|
| the threshold-7 derived table | `C:\unsung-fast\lbd-pairs\T7\T7.parquet` | sha256 `252b88d9e2f8e304e035a0befd709ad87c2753d2af4675a0139e71b076520c6c`, 14,654,446 rows |

Gitignored and absent from a fresh clone. Everything else this session produced is committed.

## Owed, and by whom

**The owner's**, in this order — and per `NEXT.md`'s rule this note does not record how far down the
list he has got:

1. **Run the queued use-the-app tests** — `TEST-QUEUE.md`, **15 unticked boxes**, live since the
   2026-09-08 deploy and untouched by this work.
2. **Merge the `lbd-s4-adoption-prereg` PR (#126)** if not already, then **this stage-1 PR**.
3. **Decide whether `LBD-AM3`'s override extends to `LBD-A4`** as a statement about *absolute*
   fidelity. Carried forward; nothing here depends on it.
4. **Decide whether stage 2 runs.** Stage 1 is complete and stage 2 is the expensive half — seven
   builds, the largest 5.3× the biggest archive ever built on this machine. **Stopping here remains
   a complete outcome** and no session proposes a route.

**A fresh session's, if he says run stage 2**, in this order:

1. **Read `LBA-AM2` before §3 or §5.** It governs the build order and the projection rule.
2. **Wire `stage2_build_instrument.instrumented_build` into the build wrapper.** One build per
   process — the instrument refuses otherwise. Run its `--self-test` once on the machine first.
3. **Draw the `LBA-M1` query-cost pair set** — 200 pairs, `random.Random(20260914)`, from artists
   present in **every** built arm and in the served map, redrawing adjacent pairs, **written to a
   file with its sha256 before any timing is taken**. It cannot be drawn until the built arms are
   known, which is why it is here and not in stage 1.
4. **Emit and build in ascending archive-neighbour-row order** (the README §6 gives the sequence),
   reading `LBA-G2` progressively. The first build is unevaluable and proceeds unconditionally.
5. **`LBA-G1`(a) is now evaluable** — `framework_rss` exists — but still needs `metadata_ratio`,
   which is `LBA-M1`'s other calibration measurement and has **not** been taken. Take it before
   reading that gate.

Branch `lbd-s4-stage1` (`gh` says where its PR is).
