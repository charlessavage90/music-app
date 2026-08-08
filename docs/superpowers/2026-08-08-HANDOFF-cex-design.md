# Handoff — the `CEX-` crawl-extension design and plan, 2026-08-08

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-07-HANDOFF-bypass-tray-ux.md`](2026-08-07-HANDOFF-bypass-tray-ux.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The design and the plan are committed; nothing is in flight; no port is
listening; the degradation tell did not fire. **The successor executes the plan cold — that is
the intended shape, not a fallback.**

Reasoning: [`2026-08-08-cex-design-execution-log.md`](2026-08-08-cex-design-execution-log.md).
Governing document: [`specs/2026-08-07-crawl-extension-design.md`](specs/2026-08-07-crawl-extension-design.md).
Operational document: [`plans/2026-08-08-crawl-extension.md`](plans/2026-08-08-crawl-extension.md).
Branch `crawl-extension-design`, **PR #91**.

---

## Start here

1. **Read the spec's §10 first.** It is the amendment log, and it tells you which parts of the
   design were falsified before you arrived. Reading §3 without it is reading a corrected
   claim without knowing it was corrected.
2. **Then the plan, Task 1.** It is prescriptive: complete code, complete tests, exact
   commands, expected output.
3. **Do not re-derive the diagnosis.** The two named artists are settled — see below.

## Documents that are now wrong, and in which direction

**The staleness runs one way: things this track proved impossible are still described as
possible in older documents.**

- **`config.py:17` is stale in the tree right now.** It calls ALG-E "the adopted 75k archive's
  algorithm"; the adopted map is **ALG-B**. **Not yet fixed — it is plan Task 7.** Until then,
  a reader of `config.py` will draw the wrong conclusion about which archive matters.
- **`cli.py:314`'s `--cap-strategy` help says "mutual_knn until adoption"** — stale since the
  `MSW-` adoption. Same task.
- **Older handoffs and execution logs naming `ULC-F3` as "blocks any crawl extension" are
  correct for their own date** and must not be edited. The block is real and this track
  removes it.

## Claims that must NOT be reverted by a well-meaning editor

- **Seeding a named artist does not work.** Falsified by a matched-pair build (zero-node,
  zero-edge delta) and again at three degree ceilings. `CEX-T6` is **withdrawn**. Do not
  reinstate it, and do not "fix" the spec's §3 back to its original argument — that argument
  used half the algorithm.
- **Growth thickens the obscure tail; it does not thin it.** `CXS-C1` rose monotonically. An
  earlier claim in this session's own conversation said the opposite and is **withdrawn**.
- **The `CXS-` cohort is frozen at the 25k frame deliberately.** Re-deriving "the obscure half"
  per cell would measure the moving ruler, not the artists. Do not "improve" it.
- **`CXS-AM1` was written before any figure existed.** Do not re-read it as a post-hoc
  adjustment; the commit timestamps are the evidence.
- **`target_artist_count` now means artists FETCHED** (after plan Task 4). The old bound
  provably never fired.
- **`refrontier` must UNION into `discovered`, never replace it.** `CEX-G1` cannot catch a
  replacing rewrite — it reports the right frontier size while breaking `done ⊆ discovered`.
- **Step 6 re-censuses `unlistenable` only.** The other two classes are strict subsets.
- **The archive snapshot is the owner's precondition for the whole track**, not a nicety.

## Already updated — do not redo

`docs/README.md` (**five new rows** — the spec, the `CXS-` pre-registration, the plan, this
handoff and the execution log — **plus a correction to the bypass-tray handoff's row, which had
gone on claiming to be the current handoff**), `NEXT.md` (rewritten, previous block marked
superseded), the previous handoff's role line, the spec (rewritten with its §10 log), the
plan's role marker and its Task 8 code (both found at this closeout — see below).

## What I know that is not in the durable record

**Checked rather than asserted. Two items, both now folded into the execution log's §8 rather
than left here** — the mtime span that makes `CXS-`'s subsets legitimate, and the 8× spread in
build times that makes any single timeout a bad bet.

One thing worth repeating because it will bite a successor writing a probe: **a 10-minute tool
timeout killed a harness mid-run and skipped its `finally` block**, leaving a seeded file in
the shared archive. `finally` does not survive SIGTERM. **Write probes that never mutate the
archive** — the `RawArchive` protocol makes an in-memory overlay trivial, and both surviving
harnesses use one.

## Anything in flight

**Nothing.** No subagents beyond this closeout's `doc-auditor`, no background jobs, no
listeners: ports 8000, 5173 and 5174 were swept and are **free**. No dev server was started
this session and none was left behind.

**The archive is at exactly 75,000 responses, verified** — a probe mutated it mid-session and
the revert was confirmed by count.

## What I would do if I were continuing

**Task 1 of the plan, inline rather than by subagent fan-out.** Every task is sequential, four
of them touch `cli.py`, and each already carries its code and tests — so a fresh subagent per
task would re-derive the codebase cold to type in code that is already written.

**Two things I would not do:** do not start the crawl before `CEX-G1` passes and the snapshot
is verified at exactly 75,000 files, and do not widen the acceptance bounds when the build is
rejected — that is the owner's, with `MSW-G3` as precedent.

## Open, and not this session's

- **The cap-rule question.** Track B priced both sides; whether faintly-connected artists are
  worth a cap change is the owner's and touches the adopted `MSW-` package.
- **The search defect (`CEX-R3`).** Its own track. **The only lever that addresses "I cannot
  find this artist" for artists that are present**, and it needs no rebuild.
- **`CEXR-6`'s `load_deezer_ids` half.** No population argument, so every new artist falls back
  to name-based clip resolution (`BYP-13`). A coverage regression, not a build failure. Its own
  track, and the plan's self-review says so rather than hiding it.
- **`DD-F1`.** A router finding. No crawl size and no cap setting addresses it.
