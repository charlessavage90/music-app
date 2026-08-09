# `CEX-` execution log — plan Tasks 1–10, 2026-08-08

**Role: ACTIVE reasoning record for the `CEX-` execution session.** Distinct from
[`2026-08-08-cex-design-execution-log.md`](2026-08-08-cex-design-execution-log.md), which is
the *design* session's and remains the authority for the design decisions. This one covers
executing the plan. Status lives in [`NEXT.md`](NEXT.md); figures for the crawl and the gate
live in `builder/analysis/2026-08-08-cex-g1/` — **cited, never restated.**

Executed **inline, not via subagent fan-out** (the retiring design session's recommendation:
every task is sequential, four touch `cli.py`, and each carried its own code).

---

## 1. Gate outcomes

| Gate | Outcome |
|---|---|
| **`CEX-G1`** — reconstruction reproduces the baseline `frontier_size` exactly | **PASSED.** 42,302, exact. Detail: `analysis/2026-08-08-cex-g1/g1_result.md` |
| **`CEX-G2`** — `--target` caller sweep complete, frozen probes era-pinned | **PASSED, and it found two callers.** §3 below |
| Acceptance bounds (both) | **NOT REACHED** — Task 11, and an owner stop by design |
| Snyk, builder package | Clean, run after every code task |

**The crawl completed clean:** 42,292 fetched this run, 0 failures, 42,292 × HTTP 200, 3.86
hours. Figures owned by `analysis/2026-08-08-cex-g1/crawl_result.md`.

## 2. Defects found in the plan itself

The plan was prescriptive and largely correct. Three defects, one of which could not run.

**(a) `CEX-M1`'s test fixture was impossible.** The plan's test called
`rescale_scores([1.0] * 99 + [1000.0], …)`. That branch takes **log-space** input and `expm1`s
it back to raw, so `1000.0` meant *e*¹⁰⁰⁰ and raised `OverflowError` — not the predicted
assertion failure. Corrected to feed `log1p` of those values, the contract every caller has
used since Task 14, after which it went red exactly as the plan said. Two assertions were
added so the fixture proves it saturates one edge rather than only that something was logged.

**(b) `CEXR-14` was mapped to Task 5 but no test was specified for it.** The finding is that
`FrontierExhausted`'s message *carries the remedy*, so it must reach the operator as a message
rather than a traceback — precisely the kind of behaviour that rots silently. A test was added.

**(c) `CEX-G2` was folded into "Task 4 Step 4: run the suite", which cannot discharge it.**
The suite stayed **green** through the semantics change. See §3 — the sweep is the gate, and a
passing suite is not evidence for it.

## 3. `CEX-G2` — the finding worth carrying

`target_artist_count` changed meaning from artists **discovered** to artists **fetched**. The
sweep found two frozen probes depending on the old meaning, and **they needed different pins**:

- **`2026-07-29-algb-trial-build/grt_run.py`** crawls with `target_artist_count=3_000`. Unlike
  the `MSW-` and `ULF-` era pins, **no config value restores the old behaviour** — it lived in
  `crawl.py`'s loop and was deleted, not defaulted. So the pin is a **refusal**: `run_arm`
  raises unless passed `accept_new_target_semantics=True`. Its record stands and needs no
  re-run.
- **`2026-07-29-trial-crawl-calibration/calibrate.py`** does not crawl and does not read
  `target_artist_count` — **a config-field sweep clears it entirely.** But its `_replay` helper
  is a **hand-written copy of `crawl.py`'s stopping rule**, and its own docstring declared its
  answers void if that rule ever changed. Left deliberately on the old rule (it exists to
  reproduce its own committed cells, and the `--target`-capped trial crawl was retired as an
  instrument on 2026-07-29) and annotated at the function.

> **The general shape, recorded in `builder/analysis/README.md`: a caller can depend on a rule
> without naming any identifier the rule uses.** `test_pipeline_mirrors.py` fires when
> `BuilderConfig` gains a field; a stopping rule that moved inside a loop body adds no field.
> Only reading the mirrors found it.

## 4. Defects in this session's own work, caught before they shipped

Both were **tests that passed while testing nothing** — the class `closeout` B3 exists for.
Both were caught by the same habit: run the new test against the old code before trusting it.

**(a) `test_fame_keys_are_ignored` was vacuous.** The plan's version put a real fame payload
(`{"total_user_count": 5}`) under `fame/`. That parses to `[]` under *any* walk, so the test
passed with the prefix guard removed entirely — it could not distinguish a scoped walk from a
naive one. Re-shaped to a **similarity-shaped** payload under `fame/`, after which only the
guard keeps it out. Verified by mutation.

**(b) The first e2e test for the landing-page dot defect passed against the broken code.** It
used `elementFromPoint`, the obvious instrument. The dot carries `pointer-events-none`, and
hit-testing **skips such elements**, so that call can never return the dot however it is
painted. Replaced with a test that **samples the rendered pixel**: against the shipped code the
sampled colour is distance **0** from the dot's `#a0d9b4`. Had this not been checked against
the old code it would have shipped as a green guard standing over a live defect.

**(c) `closeout` B3 then found a third, and it was the track's own core change.**
`test_target_caps_fetches_and_the_frontier_is_still_recorded` did **not** pin the loop
condition. Reverting `crawl.py` to bound on *discovered* left all 241 tests **green**. The cause
is the fixture: `FakeFetcher` is a **chain** with fan-out 1, so `discovered` is always
`done + 1` and the two rules are arithmetically indistinguishable under it for **any** target.
The original test did go red when written, but on the *inner break* half of `CEX-2`, not the
bound. Fixed by adding `HubFetcher` — one artist with fan-out 3, where a bound on discovered
stops at `done == 1` and a bound on fetches reaches the target. It now fails the mutation with
`assert 1 == 2`.

**This is the highest-value thing this closeout did**, and it is the exact shape B3 exists for:
a test that was red for a real reason, whose name claimed more than it checked.

**Mutation-checking was applied to every load-bearing test in this work**, not only these three:
the union requirement (`CEXR-7b` — a replacing rewrite reports the *correct* frontier size, so
only the `done ⊆ discovered` assertions catch it), the `exhausted` guard (`CEXR-5`), the CLI
boundary catch, and the `z-20` ordering invariant.

## 5. Decisions taken

- **A ten-artist smoke run before the four-hour crawl.** Proved refrontier → resume → fetch →
  checkpoint end to end for ~4 seconds of cost, and incidentally demonstrated `CEX-2` on real
  data: `discovered` grew past the old cap to 117,306, so four artists were recorded that the
  old code would have discarded.
- **`refrontier` recorded in `cli.py`'s module docstring as a REPAIR step, not a pipeline
  stage.** The docstring enumerates every other command; omitting it would have been a defect
  of absence, which no grep for a stale identifier finds.
- **The landing-page dot fix went to a worktree off `main`, not this branch.** The crawl was
  running in the main tree against `builder/src`, so switching branches there would have
  reverted the crawler under a running job — and a crash-resume would then have used the
  pre-`CEX-` code. Own branch, own PR (#92).

## 6. Corrections to the prior record

- **`config.py:17` is fixed** (`CEX-R5`). It called ALG-E "the adopted 75k archive's algorithm";
  verified against the artifact rather than the plan — `graph-msw-tu50.bin`'s manifest records
  `contribution_3` (**ALG-B**) and `ApiConfig.graph_path` serves that file. The `algorithm`
  **default is untouched** and stays ALG-E deliberately; flipping it is the owner's.
- **`cli.py`'s `--cap-strategy` help** said "mutual_knn until adoption", stale since `MSW-`.
- **`--target` is described correctly in three places now** — `cli.py`'s help, `builder/README.md`
  and `CLAUDE.md` all said "caps discovery".
- **`ULC-F3` is discharged.** It blocked any crawl extension; the block is removed and the
  extension has happened. Older handoffs naming it as blocking are **correct for their own date
  and must not be edited.**

## 7. Operational measurements with no other home

| | |
|---|---|
| `refrontier` over 75,000 responses | **4m16s** |
| Crawl, 42,292 fetches | **3.86 h**, steady ~3.0/s (config targets 5/s) |
| Archive **before** the crawl | 173,056 files / 890,728,140 bytes — the totals the snapshot was verified against |
| Archive **after** the crawl | Response count owned by `crawl_result.md` §1. **No post-crawl file/byte total was measured**, so none is stated. Free space fell 482 GB → 478 GB across snapshot *and* crawl together |
| Snapshot (robocopy, `/MT:16`) | **78 s** for 173,056 files |
| Crawl log | 2.5 MB, gitignored |

**Ordering, confirmed empirically mid-run:** at 21,510 fetched the MBIDs formed a clean prefix
of the ID space (~2,600 in each of buckets `0`–`7`, 438 in `8`, none above), confirming the
frontier drains in sorted-MBID order and is therefore sampled **without bias toward famous or
well-connected artists**.

## 7b. The closeout audit (`closeout` B1)

`docs-lint` hard checks passed after one fix (this log was unclassified in the map). The
`doc-auditor` returned **three findings; two were valid and are fixed**:

- **The plan's role line still read "NOT YET EXECUTED"** after Tasks 1–10 ran. A reader landing
  there without `NEXT.md` would conclude nothing had happened. Corrected in place, with the old
  wording quoted so the correction is visible rather than silent.
- **`NEXT.md` restated the new population** in its heading and its "last updated" line while
  its own preamble says it owns no figures. Both now cite `crawl_result.md` instead.

**The third was declined, and the reason is worth recording.** It asked for the two archive
rows in §7 to carry matching detail, and supplied a replacement containing **`478,901 files`
and `~3.5 GB`** — figures **this session never measured**. Adopting them would have put invented
numbers into the retained record under an auditor's authority. The row was made consistent the
honest way instead: it now says explicitly that no post-crawl file/byte total was measured.
**A subagent's suggested fix is evidence, not instruction.**

## 8. New finding, NOT fixed — `CEX-F1`

**A crawl whose target is already at or below `done` logs `0 processed` and exits 0, even with
a non-empty frontier.** That is the same silent-success shape `CEX-3` was written to eliminate,
in a case `CEX-3` does not cover: its refusal fires only when the **queue** is empty, and here
the queue has work in it.

**Why it is live now rather than theoretical.** `BuilderConfig.target_artist_count` still
defaults to **75,000** (`config.py`), and the ALG-B checkpoint's `done` is now **117,302**. So
`artistpath-build crawl` run against it **without `--target`** does nothing and says nothing —
with ~11,293 artists waiting in a recorded frontier.

**Verified, not reasoned:** a crawler built with `target=100` over a checkpoint with 120 done
and 11 unfetched returned normally, logging `crawl finished: 0 processed`, and never called the
fetcher.

**The shape is pre-existing** — the old `len(discovered) <= target` bound produced the same
no-op — so this is not a regression introduced by `CEX-2`. What changed is that it is now easy
to hit by accident.

**Deliberately not fixed here.** The candidate remedies are a default change (the owner's, per
A4) or widening `CEX-3`'s refusal, and closeout is the wrong place to add either. A no-op when
you ask for fewer artists than you already have may well be *correct* behaviour — the defect is
that it is indistinguishable from success in the log.

> **Success condition:** discharged when either the completion log distinguishes "nothing to do"
> from "work done", or `target_artist_count`'s default is raised past the served population —
> **or explicitly declined**, which is a legitimate terminal state. **Due before the next crawl
> extension**, which is the first thing that can be silently defeated by it.

## 9. Standing context layer (D6)

Measured against `C:/Users/charl/.claude/projects/C--dev-music-app/memory`.

| | Total | Delta | |
|---|---|---|---|
| **Unconditional** | **45,880 characters** | **−22** | Two corrections, both net-negative |
| **Conditional** | **2,475 lines** | **+10** | `memory/crawl-resume.md`'s body |

Previous figures: 45,902 / 2,465 (`2026-08-08-cex-design-execution-log.md` §9).

**Both unconditional edits are row 1 of D6's table — false about the world — so they were the
session's to make, and both shrank the layer:**

- `CLAUDE.md`'s builder command block said `--target N` **caps discovery**. `CEX-2` made that
  false. **−1 character.**
- `memory/MEMORY.md`'s crawl-resume index line said **"75k crawl DONE"**, which a cold session
  would now read as the ALG-B archive's population — it is 117,302. Rewritten to name the
  *hazard* (populations differ, check the manifest) rather than a number, which is both more
  durable and shorter. **−21 characters.** A first attempt at this line came out **+26**; that
  is growth rather than correction, so it was rewritten rather than reported as a saving.

**The conditional +10 is `memory/crawl-resume.md`'s body**, which now records that there is more
than one archive at more than one size, and that "resumable" was true for interruption and false
for extension until `CEX-` fixed it. Paid only by sessions that recall it.

**Nothing net-new was added to the unconditional layer, so nothing there is owed to the owner.**
