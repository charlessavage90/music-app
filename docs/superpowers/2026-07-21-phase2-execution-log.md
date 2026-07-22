# Phase 2 — Execution Log

**Role: ACTIVE.** A running record of what was decided, what went wrong, and what is
still open while `plans/2026-07-21-phase2-path-quality.md` is executed. Updated as work
proceeds. When Phase 2 completes this becomes COMPLETE and is retained as the audit
trail.

**This file holds no scoring, hub-seeking or path-quality figures.** Those live only in
`findings/2026-07-21-scoring-adjudication.md` and the finding documents it links. This
log cites them by section. Operational measurements (wall-clock timings, counts of files)
are recorded here because they are not scoring figures and have no other home.

**Why this file exists.** Phase 2 has produced an unusual number of corrections — to the
plan, to the prior record, and to its own outputs. Most were caught by review rather than
by tests. That is working as intended, but only if the corrections are recoverable later.
The per-task scratch ledger at `.superpowers/sdd/progress.md` is gitignored and would not
survive `git clean -fdx`; this file is the durable copy.

---

## 1. How to read this

| Section | Use it when |
|---|---|
| §2 Decisions | You want to know why the work deviates from the plan as written |
| §3 Defects in the plan | You are about to execute a remaining task and want to know what to distrust |
| §4 Defects in the prior record | You are citing a finding and want to know if it was overturned |
| §5 Gates | You want the pass/fail state of the plan's hard stops |
| §6 Open items | You are deciding what must happen before Phase 2 can close |
| §7 Deferred findings | You are running the final whole-branch review |
| §8 Operational facts | You are estimating how long something will take |
| §9 Environment traps | Something is behaving strangely and you suspect the environment |

---

## 2. Decisions taken

All were put to the project owner and answered explicitly. Where a decision reverses an
earlier one, both are shown.

| # | Decision | Rationale | Consequence |
|---|---|---|---|
| D1 | Work on branch `phase2-path-quality` in the main working tree, **not** a git worktree | `builder/scratch/` is gitignored, so a fresh worktree would not contain the 75k artifacts or the crawl archive that Tracks A and B both need | Isolation is by branch only |
| D2 | Fix the plan document's archive path before starting | The plan's build commands pointed at `builder/archive`, which does not exist | Committed as `6b2059e`; without it Task 1 Step 7 and all six Track B builds fail at the first command |
| D3 | Task 5 Step 6's constant-pinning test: **plan governs**, write it verbatim | A test asserting constants equal their own literals is normally a defect, but here it is a deliberate tripwire on adoption criterion 5 | Test shipped as specified |
| D4 | `nulls.py` docstring corrected to match its code | The plan's prose said scores are "carried along"; the plan's code discards them and writes a constant. Prose and code disagreed | Comment fixed, behaviour unchanged |
| D5 | Added a heterogeneous-degree fixture to the rewire tests | The plan's `_ring_with_hub` fixture has no hub — every node has degree 2 — so degree preservation was only ever tested on a degree-regular graph | Two tests added. Owner chose **not** to rename the misleading fixture, so `_ring_with_hub` stays inaccurate by decision |
| D6 | On the failed bad-path gate: continue Track A, revisit the screen later | The screen is only consumed as adoption criterion 5 in Task 15 | Tasks 6–10 proceeded |
| D7 | Investigate and **correct the record** on the §4.3 contradiction | §4.3 is the authoritative record; leaving a known-wrong claim in it would propagate | Resolved — see §4 |
| D8 | Defer all three open `badpath.py` findings to the screen rework | Fixing internals twice is waste if the screen is being reworked anyway | Findings remain open, tracked in §7 |
| D9 | **Revises D6** — the screen rework moves to *after* Task 13/14, not after Task 7 | New evidence (adjudication §6 claim 33): the only viable signal is a ceiling-hop run, which becomes uninformative once Task 13's rescale removes the ceiling tie-mass. Building it now would calibrate against a defect Track B is about to eliminate | Rework now sits between Task 14 and Task 15 |
| D10 | Ship the configuration-model verdict on a single rewire realisation | The measured gap runs opposite to the alternative hypothesis, so noise would have to reverse its sign, not merely shrink it | Caveat recorded explicitly for later critical review as adjudication §6 claims 34–35 and in the null finding's §4.1 |
| D11 | Defer the Snyk CWE-23 finding to the final whole-branch review | Low severity, in a developer-run CLI | Tracked in §7. **Note: it was twice mislabelled "pre-existing" — it is not.** `api/eval/export_paths.py` is new on this branch |

---

## 3. Defects found in the plan itself

The plan is otherwise detailed and mostly correct; these are the places a worker
executing it literally would have produced something wrong.

| Where | Defect | Resolution |
|---|---|---|
| All build commands | Pointed at `builder/archive`, which does not exist. The archive is `builder/scratch/graph-archive` | Corrected in the plan, commit `6b2059e` (D2) |
| Task 4, `nulls.py` docstring | States rewired scores are "carried along with their edges"; the code discards them and writes a uniform constant | Prose corrected (D4) |
| Task 4, `_ring_with_hub` fixture | Named for a hub it does not contain — a uniform 5-cycle, every node degree 2 | Additional fixture added (D5); name left as-is by owner decision |
| Task 5, two toy fixtures | The brief's own tests fail against the brief's own code. One fixture makes a zero-common-neighbour signal fire unavoidably; the other's pairwise Jaccard is half the threshold it must exceed | Fixtures repaired with the arithmetic shown in the task report; implementation and thresholds untouched |
| Task 6, `resolve_pairs` | When **both** endpoints of a pair are unresolvable, only the first is reported in `dropped` — silently losing the second, contradicting the function's own documented contract | Fixed, test added |
| Task 8, Step 6 | Instructs `git add api/uv.lock`; that file is gitignored and was never tracked, so the step is unsatisfiable as written | Dependency pinned in `pyproject.toml` instead; flagged rather than silently skipped |
| Task 9, reference code | Writes UTF-8 bytes but never declares the charset in the document | `<meta charset="utf-8">` added |
| Task 10, runtime estimate | Assumed ~4s per path; the real figure is well under half that | Actual runtime predicted to within 0.2% once measured (§8) |
| Tasks 2, 3, 7, 8, 9 | Several prescribed test blocks carry an unused `import pytest` or `import numpy as np` | Left as-is; recorded in §7 |

**Pattern worth noting for the remaining tasks.** The plan's *prose and structure* have
been reliable; its *inline toy fixtures* have not. Three of them were arithmetically
impossible. Every remaining task brief should be treated the same way: if a prescribed
test fails against a faithful implementation, the fixture is the suspect, not the code.

---

## 4. Defects found in the prior record

| Claim | Status | Where |
|---|---|---|
| §4.3: "every overlap metric would have scored the bad path well" | **Upheld at the path-aggregate level, overstated as written.** §4.3 never named its reference class, which was the entire disagreement | adjudication §4.4, §6 claim 28 |
| §4.3: the bad path is "a chain of dense, mutually-overlapping micro-neighbourhoods" | **Overturned.** It is a *loose* set bound by ceiling-clipped scores. Overlap metrics are blind to it because the defect lives in the score channel, not the topology | adjudication §4.4, §6 claim 29 |
| Task 5's degree-ratio explanation for why the screen fails | **Overturned for the interior hops**; true only of the entry hop. Task 5's *conclusion* stands, for a corrected reason | adjudication §6 claim 30 |
| "Swap the micro-cluster signal to the overlap coefficient" | **Refuted by measurement.** Do not make that change expecting it to work | adjudication §6 claim 31 |
| Task 5's eight known-good calibration paths | **Overturned in part.** One is the ceiling-chained defect wearing a different face, and is the sweep's sole "false positive" — a true positive on a mislabelled path | adjudication §6 claim 32 |
| findings §2 (hub-seeking is topological), previously struck through | **Reinstated** for shortest-path and similarity-only routing | `findings/2026-07-22-configuration-model-null.md`, §6 claim 22 |
| findings §5.1 (hub-seeking is caused by the scoring) | **Overturned** for that class of router | same, §6 claim 19 |
| Task 7 report: "v2 and v3 differ only in popularity" | **False.** Their topology arrays are byte-identical but their scores are not. Do not treat them as a single-variable pair | corrected inside `.superpowers/sdd/task-7-report.md` |

---

## 5. Gates

The plan names four gates that stop work rather than warn.

| Gate | Status |
|---|---|
| Task 5 Step 5 — the bad-path detector must separate known-bad from known-good | **FAILED.** No threshold separates them; at the shipped thresholds the screen passes everything. Root cause and the refuted fix are in adjudication §4.4. Rework deferred by D9 |
| Task 12 Step 8 — mutual k-NN must retain ≥90% of artists | **PASSED — 98.9%** (74,191 of 74,991 in the largest connected component). Max degree after the cap is exactly 50, against 11,241 under the old strategy on the same run. The reviewer traced the denominator through the code to confirm it is the largest component, not total surviving nodes |
| Task 13 Step 7 / Task 14 Step 5 — the control arm must rebuild `graph-75k-v3.bin` byte-identically | Not yet reached |
| Task 15 Step 7 — the held-out slice must reproduce criteria 1–4 | Not yet reached |

---

## 6. Open items — none of these may be silently dropped

1. **Bad-path screen rework.** Between Task 14 and Task 15 (D9). Must carry: the three
   deferred findings in §7, the defective calibration set (claim 32), and the ceiling-hop
   signal lead (claim 33) with its caveat that the signal self-obsoletes after the
   rescale.
2. **The null result has no error bar.** One rewire realisation, no significance test,
   and the two compared means differ in n. Claims 34–35. Revisit before anything leans
   harder on it than Task 14's narrowed sweep does.
3. **The production router's excess hub-seeking is unexplained.** Claim 35. It sits well
   above the topological baseline and the rewire cannot test it. Suspected to be the
   popularity term, unproven.
4. **Task 16 Step 1** must delete the losing option from each config knob and raise on
   it — the spec requires the loser be removed, not left as a supported mode.

---

## 7. Deferred review findings — input to the final whole-branch review

Each was raised by a task reviewer, judged non-blocking, and deliberately not fixed.

**Security**
- Snyk Low CWE-23 path traversal, `api/eval/export_paths.py`, output path from `argv`.
  Developer-run CLI, no trust boundary crossed. **Introduced on this branch** despite
  being twice reported as pre-existing (D11).

**Correctness / coverage**
- `badpath.py` — signal 2 iterates every hop including endpoint-incident ones, though the
  module docstring claims all signals are interior-only. A user picking an obscure
  endpoint is flagged for their own choice.
- `badpath.py` — the module docstring and the threshold comment assert contradictory
  things about the same path; §4.4 overturned the former.
- `test_badpath.py` — the blank-name test passes via the wrong signal, so that branch is
  untested.
- `test_evaluation.py` — the degree-1 Adamic–Adar guard is never exercised.
- `test_diagnostics.py` — `corr_score_log_degree` has no coverage, despite being the
  field that exposed the v2/v3 discrepancy.
- `test_stats.py` — no test covers Holm with duplicate p-values, so the documented
  deterministic tie-break is unverified.
- `test_panel.py` — nothing constructs two differently-ordered stores to demonstrate the
  index-shift immunity that is Task 6's entire purpose.
- `panel.py` — `by_name` has no duplicate-name guard (no collision in the current run).
- Task 11 — no end-to-end test that the build actually drops the filtered nodes.
- `test_graph.py` — the mutual k-NN symmetry test uses an already-symmetric fixture, so
  it cannot distinguish *enforcing* equal per-direction weights from merely *preserving*
  them, and the docstring overclaims accordingly. No production consequence:
  `symmetrise()` always runs immediately after the cap.

**Hygiene**
- Unused imports in several plan-prescribed test blocks.
- `scipy>=1.14` has no upper bound and no tracked lockfile pins the resolved version.
- `manifest.py` — the `graph` parameter is untyped; build timing excludes artifact and
  sidecar write.

---

## 8. Operational facts measured this phase

Not scoring figures. Recorded because several plan estimates were wrong and these are the
numbers to plan against.

| Measurement | Value | Note |
|---|---|---|
| Full 75k build from archive | **28.9 s** | The plan's contingency assumed builds might exceed 30 minutes; they do not. All six Track B builds can run interactively |
| Structural diagnostics, one 75k artifact | **0.071 s** | Fully vectorised, no sampling |
| `find_path`, one query on a 75k artifact | **~1.55 s** | CPU-bound Dijkstra. This dominates every evaluation run |
| Configuration-model rewire at 75k | **85.3 s** | Never previously measured. Confirmed by an independent run and by 5k scaling |
| Full null experiment, 130 pairs × 4 routers + rewire | **659 s** | Predicted 660 s from a 3-pair smoke test |
| HTML path export, 138 pairs × 2 artifacts | **429 s**, 99.9% of it `find_path` | All file I/O in the run totals 0.28 s |
| Archive | 75,000 responses, 139,168 harvested identities | `builder/scratch/graph-archive` |

**Implication for Task 15.** It routes the panel across six artifacts. At ~1.55 s per
query that is roughly 20 minutes per evaluation pass, and the `w_jump = 0` comparison arm
doubles it. Plan for it.

---

## 9. Environment traps

- **`UV_LINK_MODE=copy` on every `uv` command.** Already in `CLAUDE.md`; still the first
  thing that breaks.
- **`PYTHONIOENCODING=utf-8` on anything printing artist names.** Names include
  non-Latin-1 characters and the Windows console codec raises on them.
- **Python buffers stdout when redirected here.** A long background job writes a 0-byte
  log and looks dead while running perfectly. Use `python -u` or `PYTHONUNBUFFERED=1` and
  poll the file. **Three subagents lost time to this**; it is the single most common
  failure mode in this phase.
- **MusicBrainz disambiguation strings are not uniform** — casing varies and at least one
  uses an en dash where others use a hyphen. Match on a case-insensitive phrase, never on
  punctuation. Never match placeholder entities on bracketed *names*: 22 nodes have
  bracketed names and 15 are real bands.

---

## 10. Task status

| Task | Status |
|---|---|
| 1 Build timing and provenance manifest | Complete |
| 2 Neighbour-set primitives | Complete |
| 3 PathMetrics rework | Complete |
| 4 Null models | Complete, after two review fixes |
| 5 Bad-path detector | **Implemented but its gate failed.** Rework deferred (D9) |
| 6 MBID-keyed panel | Complete, after one review fix |
| 7 Structural diagnostics | Complete; report prose corrected |
| 8 Paired statistics | Complete |
| 9 Path export tool | Complete, after two review fixes |
| 10 Configuration-model experiment | Complete |
| 11 Entity filter | Complete |
| 12 Mutual k-NN cap | Complete. Gate passed |
| 13 Rescale strategy | In progress |
| 14–16 | Not started |
