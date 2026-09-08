# `DCF-` execution log — the degree-ceiling falsifier

**Role: RETAINED EXECUTION LOG.** Owns **no figures** — those belong to
[`../../builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md`](../../builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md),
cited by section and never restated here. Owns **no status** — `NEXT.md` does.

**No separate handoff note was written, deliberately.** The work is complete and nothing is
in flight, and the current handoff
([`2026-09-06-HANDOFF-lux-4-artifact.md`](2026-09-06-HANDOFF-lux-4-artifact.md)) is still
correct for next actions — `L4-T8`–`L4-T11` remain the live work and this probe displaces
none of it. A second document claiming to be the current handoff is a defect this project has
already had once, and manufacturing one to satisfy a checklist would be the wrong trade. The
sections below carry what a handoff note would have: what changed, what must not be reverted,
and what is not in the durable record.

---

## 1. What this was

`measurement-derivation.md` Q4 attributed most of the `CXR` added set's sparsity to our own
`union_degree_ceiling` and named a falsifier it did not run. The owner asked for that
falsifier to be run, then added, mid-flight, a composition split of the restored edges and a
per-fame-band read of which cap step deletes an edge.

**Everything is descriptive.** No path was built, no routing criterion was evaluated, no
default was changed, no artifact was serialised, nothing was adopted.

## 2. Decisions, with reasoning

1. **Restarted the sweep after one arm rather than running a second sweep later.** The
   composition split needs adjacency; the first run recorded degrees only. Restarting cost
   ~30 min of completed work against ~90 for a second full sweep.
2. **Extended `q4`'s instrument in a new file rather than editing `q4` in place**, against a
   literal reading of the instruction. `q4` is committed and the `LBD-` review cites its
   outputs; `cb_build_variants.py` carries a standing warning that a changed comparison needs
   a new harness or the old figures stop reproducing. Flagged to the owner at the time as
   overrulable.
3. **Isolated the two cap stages by calling the shipped `trimmed_union_cap` twice** — once
   with a ceiling asserted at run time to be non-binding, once at 50 — rather than
   reconstructing the top-*j* step. This **removes `q4`'s own stated weakest link** rather
   than inheriting it, and it is why §6's figures are the shipped function's own output.
4. **Added bridge arms through `unlistenable_list_path`.** The primary arms could not sit on
   the `CXA` population (below), so their absolute levels were near but not on `CXR-P2`'s
   ruler. Two extra arms put them on it. Run-count is methodology and was not escalated.
5. **Persisted a per-artist table.** Three re-reads had each cost a ~30-minute re-run because
   only aggregates were kept. The mechanism split in §6 was then a read, not a fourth run.

## 3. Corrections to the prior record

**Three documents, in four places, asserted that the added artists' sparsity is *mostly* our
own degree ceiling. Measured, it is the minority cause.** Each now carries a forward-correction note
pointing at the README §4 as figures owner; none had a measured claim rewritten and none
restates a figure.

| document | where |
|---|---|
| `findings/2026-09-06-lbd-plan-review.md` | under the premise heading, and in "What is owed, and by whom" |
| `NEXT.md` | the `LBD-` block |
| `docs/README.md` | the row for the plan review |

**The owner named two of the four places. The other two were found by this closeout's B5 sweep** — the
silent-partial-discharge shape, and the reason B5 exists.

> ⚠ **MUST NOT BE REVERTED.** The overstatement was a *characterisation*, never arithmetic:
> the derivation had already published the count correctly, and the bridge control reproduces
> it exactly. So a future editor comparing the derivation's numbers with the corrected prose
> will find no contradiction and may conclude the notes are spurious. They are not. **What is
> confirmed and must not be softened:** the bilateral-deletion mechanism, its `graph.py`
> citation, and the three consequences the review draws for the `LBD-` pre-registration —
> `LBD-C2`'s population dependence, the ceiling as a dormant term, the two-arm insufficiency.
> Only the magnitude moved.

**A second correction, to this session's own output.** The edge-fate probe's header asserted a
mechanism for the bottom band's top-*j* losses *before the denominators existed*, and the
measurement refuted it. Corrected in the file rather than quietly dropped. Recorded because
the sequence — assert, then measure, then correct — is the failure the plain-sentence
discipline exists to catch, and it happened here in a session that had already been warned by
it once.

## 3b. ⚠ This work fires a check another session left for it

**A concurrent session on `lb-dump-exploration` wrote the `LBD-` pre-registration while this
ran, and anticipated this exactly.** Its handoff
(`2026-09-07-HANDOFF-lbd-preregistration.md`, on that branch, **not on `main` as of this log**)
records that it **deliberately did not read this work**, so that `LBD-X1` was written from the
committed record alone — a second opinion that has absorbed another session's notes is not
independent. That was the right call and nothing here criticises it.

**What it means now.** `LBD-X1` states that the ceiling's effect on the `CXR` added set is
**genuinely unmeasured**, because both Track B sweeps predate the crawl extension. That was
true of the committed record on 2026-09-07. **This work measures exactly that set, so when
`DCF-` lands on `main` the claim goes stale** and the pre-registration would be citing an
absence that no longer exists.

**No action was taken on that branch, deliberately** — it is another session's in-flight work,
and its own condition is self-executing: *"before executing Task 3, `git log origin/main` for
`DCF-`; if it has landed, read what it establishes about the added set's degree and record
whether `LBD-X1` needs an amendment — dated, with its reasoning, never an edit to the values."*
That condition is well-formed and now due on merge. **It is recorded here so the trigger is
visible from this side too**, rather than resting on one branch's handoff being read.

⚠ **Both sessions edited `docs/README.md`.** Each used small inserts and appended clauses
rather than a rewrite, so the two reconcile in either merge order — but expect the file in both
PRs.

## 4. Defects found in the instructions, not the code

- **A `tee` in the run pipeline masked a traceback as exit 0.** One run reported success while
  the script had died on a missing import. Exit codes through a pipe are the shell's, not
  Python's; later runs redirect instead.
- **The top-*j* death crosstab was uninterpretable as first computed.** The top fame band
  holds a large share of all edges, so raw death shares are indistinguishable from a base
  rate. A per-fate crosstab was added and the deaths reported as enrichment. **Reported to the
  owner as withheld rather than reported and later retracted** — the numbers had already been
  computed and would have supported a confident wrong sentence.

## 5. Operational measurements with no other home

- Full build of the extended ALG-B archive through `build_from_archive`: **~12 min** per arm
  cold, **~4 min** for the non-binding-ceiling arm, **~0.8 min** for the bridge arms with the
  OS file cache warm. The served map's own manifest records ~39 s, which is not comparable —
  a warm rebuild of a smaller population.
- Edge-fate probe over the 75,000-payload archive: **~25–30 min**, dominated by the parse.
- `scripts/docs-lint.sh` over the corpus: **~2.5 min** on this machine.

## 6. Gate outcomes

| gate | outcome |
|---|---|
| ceiling sweep, green (bound holds) | **PASS** |
| ceiling sweep, red (knob reaches the cap step) | **PASS** |
| edge fate, green (reproduces the served artifact's edge set exactly) | **PASS** |
| edge fate, red (three stages strictly decreasing) | **PASS** |
| bridge arms, both halves | **PASS** |
| `docs-lint` hard checks | **PASS**; `CAND` output is pre-existing constants in frozen pre-registrations, none from this diff |
| `doc-auditor` semantic audit | ⚠ First attempt terminated on a session rate limit. **RE-RUN 2026-09-07 AND COMPLETE**, widened to cover PR #109 as well: [`findings/2026-09-07-doc-audit-two-branch.md`](findings/2026-09-07-doc-audit-two-branch.md). **B1 is now discharged.** Two HIGH cross-branch findings, both anticipated by §3b; one finding in the report is wrong and carries a verified correction banner. |

~~**What is owed because of that**: the semantic half of B1 for this diff.~~ **DISCHARGED
2026-09-07** by the re-run above. Struck, kept for the record. The original text follows,
because it names what was uncovered and that remains true of any future diff here: Specifically unchecked
by any tool — whether the new README's role marker conflicts with anything, whether
`builder/analysis/`'s new files carry dead relative links (**`docs-lint` does not scan
`builder/analysis/`; its `DOCS` is `$ROOT/docs`**, so the figures-owner document this session
created is covered by *nothing* mechanical), and whether documents citing the four corrected
ones are now stale. The manual sweeps in §3 and B5 cover part of it; they are not a
substitute. **Success condition: run `doc-auditor` scoped to this diff at the next session
with budget, before the PR merges.**

## 7. Standing context layer (`closeout` D6)

Measured against `~/.claude/projects/C--dev-music-app/memory`.

- **Unconditional: 51,694 characters — delta 0.** Unchanged from the `LUX-4` closeout.
- **Conditional: 2,551 lines, from 2,549.** The +2 is **not this session's**: no skill, agent
  or memory file was touched here, and `memory/working-style.md` carries an mtime of
  2026-09-06, before this session began.

**Nothing is owed to the owner on either layer.**

## 8. What I know that is not in the durable record

- The 20000 ceiling was chosen to exceed the largest pre-trim degree the plan review had
  observed. It cleared it, but **not by much** — the observed pre-trim maximum on this
  population is within a factor of two of that value, so a future probe on a larger population
  should not assume 20000 is safely non-binding. The script asserts rather than assumes, so it
  will refuse rather than mislead.
- **`drop_no_release_tail` and `drop_featured_credit` have no population guard**, unlike
  `drop_unlistenable`. On the extended archive they silently under-filter. Held constant here
  so the comparison is unaffected, and *not* filed as a deferral because it is already
  recorded in the pipeline's own comments — but nothing measures how much they miss.
- The `.pre-cex-snapshot` archive contains payloads for **55** of the artists the `CXA`
  extension is said to have added. They were crawled earlier and excluded from the served map.
  Not a defect; it means "added" is a statement about artifacts, not about the crawl.
