# Retained execution log — `LBL-` listen 2: the run and the read, 2026-09-13

**Role: RETAINED EXECUTION LOG for the `LBL-` listen-2 run and its write-up. ACTIVE.**
**Owns no figures** — those belong to
[`findings/2026-09-13-lbl-listen2-results.md`](findings/2026-09-13-lbl-listen2-results.md)
(the listen), to
[`builder/analysis/2026-09-10-lbd-blind-listen/lbl_prescreen2.md`](../../builder/analysis/2026-09-10-lbd-blind-listen/lbl_prescreen2.md)
(the pre-screen) and to
[`builder/analysis/2026-09-10-lbd-served-population/README.md`](../../builder/analysis/2026-09-10-lbd-served-population/README.md)
(the maps). Cited by section, never restated.

Covers two sessions: the **mechanics-only runner** that served the listen and unblinded it,
and the **write-up session** that read it. Neither prepared the materials; that session's log
is [`2026-09-12-lbl-listen2-prep-execution-log.md`](2026-09-12-lbl-listen2-prep-execution-log.md),
and `LBD-AM6`'s own disclosure bars it from both roles.

---

## 1. The run — what the record shows, and what it does not

The runner session followed `builder/analysis/2026-09-10-lbd-blind-listen/RUNNER-BRIEF.md`
and, per the brief, reported only that the answers and tally were committed. It left **no log
of its own**, which is by design — it was held ignorant of everything except the mechanics,
and a log would have been a place for it to form a view.

⚠ **A first runner session was stood down before it served anything, because it had read
project status during orientation.** Recorded here on the owner's account, given to this
session on 2026-09-13; no artifact in the repository records it, and the stood-down session
committed nothing. It is worth having in the record for two reasons: the blind was protected
by discarding a session rather than by reasoning about how much it had seen, which is the
correct disposal and the cheap one; and it is the second time the orientation ritual and the
runner brief have pulled in opposite directions, a runner being precisely the session type
that must **not** read `NEXT.md`. `RUNNER-BRIEF.md` already forbids it; what failed is that a
session reaches the brief only after orienting.

What the committed record therefore establishes, and all it establishes:

- `fe8ba53` (2026-09-13 12:30:58 −0400) — the owner's saved answers
  (`lbl_listen2_verdicts.json`) and the stimulus as presented (`lbl_listen2_page_data.json`),
  committed **before** unblinding.
- `c9c5264` (12:31:19) — `lbl_listen2_result.json`, the unblinded mapping and mechanical
  tally, committed after. The two-commit order is the evidence that the answers preceded the
  unblinding, and it is why the brief required two commits rather than one.
- **All 24 rows and all 8 pair entries were saved**, with `LBD-AM6`'s `LBL-Q3` and `LBL-Q4`
  answered wherever owed, so `LBD-AM5-5`'s run-state condition is met. `lbl_unblind.py`
  refuses to emit a read otherwise.
- **No substitution fired.** All eight primary pairs from `lbl_pairs2.json` survived
  generation under `LBD-AM6-3`'s raised interior gate of three; the sealed file's
  `substitutions` list is empty and `min_interior_gate` records 3.
- **Sides were dealt, not drawn** — the sealed file records `side_assignment:
  dealt_balanced`, and the mapping is 4–4 as `LBD-AM6-6` requires.
- The two maps are the artifacts `LBD-AM5-2` names, at the sha256s `lbl_maps.json` pins;
  `lbl_common.load_map` refuses any other bytes.

**Not established, and not recoverable:** how long the sitting took, whether it was split,
how many clip refreshes were needed. Nobody was asked to record it and nobody should
reconstruct it now.

## 2. Decisions taken in the write-up

- **Read the amendment before any result.** `LBD-AM6` in full — including the `LBD-D6` ruling
  it quotes verbatim and the pre-screen's selection rule — then `LBD-AM5-5`'s read block, then
  the owner's raw answers, then the hand recomputation, and only then the result JSON. That is
  `GBL-`'s write-up order as the listen-1 log §2 applied it.
- **Recomputed the tally by hand** from `lbl_listen2_verdicts.json` and the unsealed mapping
  in `.superpowers/lbl/lbl_listen2_sealed.json` before `lbl_listen2_result.json` was opened as
  authoritative. It matches cell for cell: coherence 5/7, novelty 4/2, zero clip-blocked rows,
  `LBL-R2`.
- **Verified the instrument rather than trusting it** (`session-start`'s verify-one-claim
  check). `axis_read` and `listen_read` were checked clause by clause against `LBD-AM5-5`, and
  `MARGIN`, `DEPTHS`, `AXES`, `MIN_INTERIOR_BY_LISTEN`, `SIDE_ASSIGNMENT_BY_LISTEN` and
  `ROW_EXTRAS_BY_LISTEN` in `lbl_common.py`, plus `row_complete` in `lbl_page.py` for the
  run-state and strength-refusal rules. All correct as written, and `axis_read` reads only the
  pick and the clip box — `LBD-AM6-5`'s invariance holds by inspection as well as by its test.
- **Measured the dead cells rather than inferring them.** `LBD-AM6-1`'s Gate 2 permits one
  depth per pair at which the two maps agree; comparing the sealed journeys directly showed
  **five** such cells, and the owner's *"Same paths"* notes fall on exactly those five. This is
  the write-up's largest single finding about the instrument and it is arithmetic over the
  sealed file, not an impression.
- **Recorded the cross-listen *no preference* counts, and named the confound in the same
  breath.** Listen 2 could call fewer rows than listen 1 despite carrying all six of its
  fixes. Different maps, different pairs, a different comparison — so it is an observation,
  never a measurement, and it is **not** a re-read of either verdict. It goes in the findings
  note's §0 because a summary that omitted it would be wrong, and it is the reason §4's
  defect list is about *differential* novelty rather than about pair length.
- **Did not code strength or trade-off into anything.** `LBD-AM6-5` fixed the treatment before
  any journey existed: rows are counted, strength is descriptive, no threshold attaches. The
  findings note reports both under headings that say so.
- **Did not propose a route.** The owner's instruction, and `LBD-AM6-8`'s bar on adoption on
  any outcome, put every next step with him. §6 of the findings note states what is open and
  stops.

## 3. What this session did not do

- **No `S4` work, and no proposal of any.** `LBD-D6` as ruled requires `LBD-A4` to run and
  `R10` to be read before any `S4` arm is pre-registered.
- **No further listen proposed.** §4's instrument items are recorded as defects for whatever
  protocol comes next, if one ever does; each would be a pre-registration change and none is
  recommended here.
- **Did not read the map-labelled pre-screen outputs beyond `lbl_prescreen2.md`'s committed
  counts and the ranked survivor table**, which the amendment itself cites. The per-map journey
  lengths in `lbl_prescreen2.json` were not opened, and the findings note says explicitly where
  that leaves a question unbounded (§3).

## 4. Corrections this work made due

Four `docs/README.md` rows, the pre-registration's own §12 entry, the previous handoff's role
line and `NEXT.md`'s top block all asserted that listen 2 was prepared and **unrun**. Every one
was correct when written on 2026-09-12 and false by 2026-09-13:

- **`docs/README.md`, the pre-registration's row** — *"Listen 2 is registered, its materials are
  prepared, and it is UNRUN"* struck, with an **EXECUTED** marker added in `GBL-`'s shape,
  including that `GBL-` §5's run-once rule now binds *both* verdicts;
- **`docs/README.md`, the blind-listen harness directory's row** — *"Listen 2's materials are
  prepared and the listen is UNRUN"* struck, the listen-2 raw record named, and the absence of a
  listen-2 owner-notes file stated so that nothing is inferred from it;
- **`docs/README.md`, the `2026-09-12-HANDOFF-lbl-listen2-prep.md` row** — struck on status with
  the rest preserved, because its "must not be reverted" claims still bind;
- **`docs/README.md`, the listen-1 findings row** — gained a forward pointer to listen 2 **and a
  restatement of the no-carry bar**, so that a reader arriving at listen 1 from a citation cannot
  read the second tie as bearing on the first;
- **the pre-registration's §12 `LBD-AM6` register row** — *"and none has been generated since"*
  struck, with a status marker added **beside** the entry rather than edited into it, per §12's
  own rule. **No value in the document changed**;
- **the previous handoff's role line** — now names this session's handoff as its successor on
  next actions, so the chain reads forwards as well as backwards;
- **`NEXT.md`** — top block rewritten; the outgoing block demoted whole to `NEXT-ARCHIVE.md`,
  with what still binds distilled first into the *Closed* registry and two deferral conditions
  (`DLS-` items 4–6, whose closeout half is now satisfied; `LBD-A4`, which gains `LBD-X6`).

Three rows were **added**: the findings note, this log, and the new handoff.

## 5. `closeout` D6 — the standing context layer

Measured at the end of this work, per D6's commands against the memory directory this
session's own context names (`C:\Users\charl\.claude\projects\C--dev-music-app\memory\`):

| layer | unit | value |
|---|---|---|
| unconditional — `~/.claude/CLAUDE.md` + `CLAUDE.md` + `MEMORY.md` + every loading `description:` | characters | **50,977** |
| conditional — `SKILL.md` and agent bodies, `memory/*.md` bodies | lines | **2,726** |

**This session's delta in both: zero.** It touched no file in either layer — `git diff
--name-only origin/main...HEAD` returns nothing under `CLAUDE.md` or `.claude/`, and nothing
under `memory/`. The unconditional figure is **unchanged from the listen-1 read's 50,977**.
The conditional figure is **+131 lines against that reading, and none of it is this
session's** — it arrived on `main` from the `DLS-` work merged between the two closeouts,
which this branch is based on. Recorded that way rather than as a delta, because attributing
another branch's growth to this one is exactly the drift the two-number rule exists to stop.

## 6. Working notes for a successor

- **The sealed mapping lives outside git**, at `<tree>/.superpowers/lbl/lbl_listen2_sealed.json`
  in the **runner's** worktree (`C:/Users/charl/worktrees/music-app-lbl-listen2-run`), not in
  the main tree. A write-up session reading from the main tree must reach across to it; the
  mapping is also copied into `lbl_listen2_result.json` under `mapping_unsealed`, but the
  sealed file is the only source of the journeys and the metrics, and it is the only way to
  recompute a tally *independently* of the result file.
- **Run the hand tally before opening the result.** It is ten lines of Python over the two
  files and it is the whole value of `GBL-`'s write-up order; opening the result first makes
  the recomputation a confirmation rather than a check.
