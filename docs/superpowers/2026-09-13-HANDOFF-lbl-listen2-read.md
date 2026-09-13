# Handoff — `LBL-` listen 2 run and read, 2026-09-13

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-12-HANDOFF-lbl-listen2-prep.md`](2026-09-12-HANDOFF-lbl-listen2-prep.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The listen was served, unblinded, read and written up; the map rows and the
pre-registration's status marker are updated. Nothing is half-finished and nothing is in flight.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
the **`LBD-AM5`** block at the end of §10 **as amended by `LBD-AM6`**, and §12's register rows.
**The result:** [`findings/2026-09-13-lbl-listen2-results.md`](findings/2026-09-13-lbl-listen2-results.md).
**Retained log:** [`2026-09-13-lbl-listen2-read-execution-log.md`](2026-09-13-lbl-listen2-read-execution-log.md).

---

## What happened

`LBD-A0V` (ListenBrainz's own four-listener bar) against `LBD-A5V` (the two-listener bar), eight
new pairs, three depths, two questions, blind. **The read is `LBL-R2` — the tie.** Both axes came
out two rows apart against a bar of eight; no row was lost to a clip problem. **Figures live in
the findings note and are restated nowhere**, including here.

**Nothing is adopted, no default changed, no shipped code touched.**

## Which documents are now wrong, and in which direction

All of these were **correct when written** and are false only because the listen has since run.
**All have already been fixed** — listed so a successor does not re-edit them:

| document | was | now |
|---|---|---|
| `docs/README.md`, pre-registration row | "Listen 2 is registered … and it is UNRUN" | struck, EXECUTED marker added |
| `docs/README.md`, blind-listen harness row | "Listen 2's materials are prepared and the listen is UNRUN" | struck, listen-2 raw record named |
| `docs/README.md`, listen-1 findings row | no forward pointer | points at listen 2, with the no-carry bar restated |
| `docs/README.md`, `2026-09-12-HANDOFF-…-prep` row | "ACTIVE — the CURRENT handoff" | superseded on next actions by this note |
| the pre-registration, §12 `LBD-AM6` row | "and none has been generated since" | struck, EXECUTED status marker added **beside** the entry, per §12's own rule |
| `NEXT.md` | top block described listen 2 as prepared and unrun | rewritten; the outgoing block demoted to `NEXT-ARCHIVE.md` |

**Two new documents** — the findings note and the execution log — with `docs/README.md` rows.

## Claims that must NOT be reverted by a well-meaning editor

- **`LBL-R2` is the read, and it is final.** `GBL-` §5's run-once rule now binds **both** listen
  verdicts. Neither may be re-listened on any protocol. A future listen would be new pairs under a
  new amendment and is nobody's to start.
- **No verdict carries across the two listens.** A listen-2 tie says nothing about `LBD-A5V`
  against the **served** map — that comparison was never run.
- **`REQ-41` bars reading either tie as equivalence**, and "passed" and "failed" are both barred.
- **`LBD-X6` bars generalising listen 2's result to the cheaper pairing form** until `LBD-A4` has
  run and `R10` has been read. **`LBD-X4` is listen 1's term and must not be imported into a
  listen-2 sentence** — both listen-2 maps see the served population `V`.
- **No adoption on either outcome.** `S4` owns adoption, the population rule, API sizing, the fame
  source and the refresh procedure; `V` is an experimental control, never a population rule.
- **The `LBD-AM6-5` strength counts and the ear-tracking metrics decide nothing**, carry no
  threshold, and no branch reads them. Do not re-tally anything on strength — least of all
  listen 1, which never asked.
- **Listen 1's bar of one interior artist stays as it was.** `LBD-AM6-3` raised it to three for
  listen 2 only; listen 1's value is the frozen record of how that listen ran.

## What I know that is not in the durable record

**Nothing about the listen itself** — the findings note and the execution log carry all of it,
including the figures, the five identical cells, the run state and the instrument verification.
Three items that are *now* recorded but were not until this session wrote them down, flagged so a
successor knows where they came from rather than re-deriving them:

1. **A first runner session was stood down before serving anything**, because it had read project
   status during orientation. This is on the **owner's account**, given to this session on
   2026-09-13; no repository artifact records it and that session committed nothing. Execution log
   §1. The generalisable half: a runner must not read `NEXT.md`, `RUNNER-BRIEF.md` already says so,
   and a session reaches the brief only *after* orienting.
2. **The sealed record is gitignored and was living only in the runner's disposable worktree.**
   `lbl_listen2_sealed.json` is the only source of the per-map journeys and the hidden metrics;
   `lbl_listen2_result.json` copies the mapping but not those, so removing that worktree would
   have made them unrecoverable. **Mitigated 2026-09-13: both it and `lbl_listen2_clips.json`
   were copied into the main tree's `.superpowers/lbl/`**, the same gitignored location, so they
   no longer depend on a worktree anyone may reasonably delete. No convention changed — the seal
   stays out of git, which is the point of it.
   ⚠ **Listen 1's equivalent is already gone.** `lbl_listen1_sealed.json` is on disk nowhere
   reachable (checked 2026-09-13 across both trees). What survives of listen 1 is enough for its
   read to stand — the verdicts, the stimulus in `lbl_listen1_page_data.json`, the mapping and
   the ear-tracking counts in `lbl_listen1_result.json`, and §1.3 of its findings note — but
   **its per-map journeys cannot be recomputed**, so no new question may be asked of them. Stated
   as a fact, not a defect to repair: nothing proposes to ask one.
3. **A `DLS-T1` observation was banked** in
   [`findings/2026-09-10-documentation-layer-strategy.md`](findings/2026-09-10-documentation-layer-strategy.md)
   §6b as **`DLS-T1-X6`**: this session opened a spec six times, every one through Bash and none
   through the `Read` tool, and its own instrument log nonetheless carries a `path_glob_match` for
   `.claude/rules/plans.md` — which `DLS-T1-X4`'s controlled pair says should not happen. **It is
   unruled and is not scored toward `C1` in either direction.** It is not this session's read to
   take and it was not taken.

## Owed, and by whom

**The owner's, in `NEXT.md`'s order** — that document owns the sequence and this note does not
restate where he is in it. In outline: the queued use-the-app tests, the merge, and then what
follows the `LBD-` track. **No session proposes a route**; the findings note's §6 sets out what the
result leaves open and recommends nothing.

**Nobody's, until he decides:** `S4`, `LBD-A4`, and any further listen. The findings note's §4
records eight instrument items so that a future protocol has them — as material, not as a proposal.

## For the next session

- **Read the findings note before anything that cites it**, and cite it by section; it owns the
  listen-2 figures and nothing else may restate one.
- **`docs-lint` hard checks pass and a `doc-auditor` pass over this diff returned no findings**
  (2026-09-13). Do not re-run either on the same diff.
- **No Snyk scan was owed**: this session wrote no first-party code in a Snyk-supported language,
  only Markdown.
