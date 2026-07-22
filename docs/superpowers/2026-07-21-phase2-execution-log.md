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

---

## 11. Addendum — Task 13 tie handling (2026-07-22)

**D12. Rank-transform tie handling: average rank, not the plan's sequential rank.**
Delegated to the graph analyst at the owner's request, then accepted. The plan prescribed
strictly sequential ranks; raw scores are co-occurrence counts and 99.99 % of them are
tied, so that assigned distinct costs to provably identical edges. Evidence and figures
are in adjudication §4.5 and claim rows 36–38. Decisive argument was structural: sequential
ranking is a function of array *order*, so a later cap-strategy change would silently
re-price 99.99 % of edges while staying deterministic and topology-identical.

**D13. The coarse-signal measurement goes in the main findings record**, not only here —
adjudication §4.5. It bounds how much precision any similarity-based tuning can carry.

### A correction to this log's own reporting

An earlier figure reported to the owner during this work — "179 distinct similarity
values" — **was wrong**. 179 is the count of values appearing exactly once; there are
**5,304** distinct values. Caught by the analyst before it reached the findings record.
It mattered: 179 levels implies a cost quantum of 0.0169, the real one is 0.00057.
Recorded because this log's purpose is defeated if it only lists other people's errors.

### Additions to §8 (operational facts)

| Measurement | Value | Note |
|---|---|---|
| `find_path`, one query, **obscure** pair | **~3.0 s** | Roughly double a random pair. Task 15 routes all strata across six artifacts |
| Warm 75k build, post-Task-12 code | 28.9–29.2 s | Unchanged from the Task 1 baseline |
| Cold 75k build (first after idle) | **397 s** | OneDrive cache, not a regression — two immediate re-runs returned to ~28 s |

### Addition to §9 (environment traps)

**A hung process looks identical to a slow one.** A verification job sat for 13 minutes
having accumulated 4.67 s of CPU, and showed **zero CPU movement across a 20-second
sample** — it was blocked, not computing. Dijkstra is CPU-bound, so flat CPU is the
diagnostic. Sampling `(Get-Process -Id N).CPU` twice separates the two cases in seconds;
waiting on the log alone does not. Two long jobs in this phase hung this way and were
only found by checking.

---

## 12. Task 0 — the cap-fix listening test (2026-07-22)

**Result: `capfix` preferred, blind, decisively. Fork row 1.**

### Setup

Two 75k artifacts, built from the same archive at commit `08c2831`, differing in exactly
one knob — where the neighbour cap is applied. Everything else identical: same entity
filter, same rescale (`p99_log_clip`), same damping (0.0), same scoring.

| Arm | `cap_strategy` | artists | edges | sha256 |
|---|---|---|---|---|
| `arm1-control` | `pre_symmetrise` | 74,991 | 4,101,222 | `d3016bc06dd9e62de9e6edff3206ca9a3d8366243ca18b2588c0a7063042f57a` |
| `arm2-capfix` | `mutual_knn` | 74,191 | 898,314 | `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237` |

Served blind on two ports behind two frontends; the owner was given only two URLs and did
not know the mapping. Instance A = `arm2-capfix` (:5175), Instance B = `arm1-control`
(:5174). Mapping was written before serving and unblinded only after the verdict.

`arm1-control`'s hash is byte-identical to the `graph-control.bin` built at commit
`db6844a`, before the average-rank change landed — free confirmation that `d197d8e` did
not touch the `p99_log_clip` path.

### Verdict (owner, verbatim in substance)

> "Little doubt in my mind that instance A is better. The 'famous core' problem is less
> pronounced (though natural hub artists still show up in paths), the paths are longer,
> and when using a bypass, the paths generally seem to trend longer and incorporate less
> well-known artists the more a bypass is used. I don't want to claim perfection or
> completion, but the difference in behavior was noticeable immediately — on the first
> tested path."

**Three observations, all mechanistically consistent with bounding degree after
symmetrisation** — removing hubs' ability to act as universal shortcuts lengthens paths,
surfaces less-known artists, and compounds under repeated bypass. None of this was
suggested to the owner in advance.

**Caveat recorded as stated:** natural hub artists still appear; this is not claimed as
perfection or completion.

### Why this carries weight

Blind, one-factor, and decided on the first tested path. The cap defect had been known
since Task 12 and was still switched off by default; this is the first time its effect on
the actual product complaint was observed rather than inferred from metrics.

### Consequence — fork row 1

The inverted cap was the core defect. **Task 15 is now about incremental gains, not about
finding the fix.** Per the revised plan: run it as written, but do not agonise over a
marginal winner — if no arm clearly beats `capfix`, adopt `capfix` and close.

### Note on a single controller probe

Before handover, one verification query (`Miles Davis → Daft Punk`) returned 5 nodes on
`capfix` against 6 on control — i.e. *shorter* on that one pair, opposite to the owner's
general impression across several pairs. One pair is not a trend and the two are not in
conflict, but it is recorded rather than dropped: path length is not monotonic in the fix,
and Task 15's `mean_length` will measure it properly.

### Task 0 Step 6 — routing-time probe, both artifacts

Analysis slice (100 pairs), frozen control-anchored hub set throughout, five router
configurations per artifact. Numbers are in the adjudication (§6 claims 39–40); the
operational points are here.

- **`capfix` corroborates the blind verdict quantitatively.** All three effects the owner
  reported from twenty minutes of use — less hub traversal, longer paths, less-known
  interior artists — are present in the measurements, from a build-time change alone.
- **The `w_jump` suspicion in claim 35 is largely refuted.** Zeroing the popularity term
  moves control's hubfrac only modestly. It contributes; it is not the main driver.
- **`w_hub` is dormant at its default of 0 and is a very large lever**, but buying hubfrac
  with it costs a roughly tenfold collapse in Adamic–Adar — paths routed through hops with
  almost no shared neighbours. Bracketed rather than guessed, per plan. Values recorded as
  "binds on this artifact"; the penalty is per-graph normalised and does not transfer.
- **Counter-intuitive detail worth keeping:** on control, `w_jump = 0` lowers hubfrac while
  *raising* max interior degree. The two measures disagree; neither alone describes
  "hubbiness."

**Operational facts for Task 15:**

| | |
|---|---|
| Panel pairs unresolvable on `capfix` | 2 of 100 |
| Frozen hub MBIDs absent from `capfix` | 1 of 751 |
| Routing cost, control | ~200 s per router pass (100 pairs) |
| Routing cost, `capfix` | ~35 s per router pass — ~5× cheaper, it carries a fifth of the edges |

The five `mutual_knn` arms in Task 15 will therefore be far cheaper than the control arm.

**Caveat stated rather than glossed:** the topological baseline in
`findings/2026-07-22-configuration-model-null.md` was measured on the v3/control-family
graph. Comparing `capfix` against it is cross-graph and not like-for-like. On `control` the
comparison is valid and confirms the excess. Measuring BFS on `capfix` would close this and
costs about 40 s, but it is a new measurement and Phase 2 is not opening one.

---

## 13. Pre-registration of the criteria resolution (2026-07-22)

**Recorded so a later reader can verify this was not fitted to a result.**

**When:** 2026-07-22, while Task 14 was still running. **What existed at the time:** the
`control` and `capfix` artifacts and Task 0's results. **What did not exist:** any arm
beyond those two, any Task 15 evidence, any paired test, any comparison table. Arms
`rankfix`, `d025`, `d050` and `d075` had not been built.

**The contradiction being resolved.** The six adoption criteria were drafted to adjudicate
the rescale-and-damping question, before the cap fix was a candidate. Read literally they
reject `capfix` — criterion 3's degree-collapse clause and criterion 4's ceiling threshold
both fail against it — while Step 6 forbids relaxing a criterion to avoid that, and
amendment 7 pre-authorises adopting `capfix` if nothing beats it. All three could not hold.

**Owner decision: resolved by scope, not by softening** (plan §4 amendment 8).
`capfix`'s warrant is Task 0 — blind, one-factor, owner-judged. Criteria 1–4 govern arms
3–6 against their isolating baselines at full strength. The scope narrowed; the bar did not.

**Verification against the Task 0 measurements**, performed at pre-registration time:

- **Retiring criterion 3's degree-collapse clause is correct.** Measured max interior
  degree is far lower under `mutual_knn` than under `pre_symmetrise` (adjudication §4.6),
  and every arm from 2 onward carries the cap — so the clause would report the cap rather
  than the routing and cannot discriminate among the arms it governs. Degenerate, confirmed
  by measurement rather than assumed.
- **One residual guard is NOT covered by the frozen hub set.** `hubfrac` can fall because
  the router avoids hub artists (wanted) or because those artists are absent from the graph
  (definitional). The frozen set fixes hub *identity* and closes the redefinition attack,
  but does not separate these two. Amendment 4's retention gate measures *overall* artist
  retention and would not catch a selective loss of frozen hub nodes.
  **Guard adopted: report the count of frozen hub MBIDs present, per arm, alongside
  `hubfrac`.** The harness already computes it. Measured for `capfix`: 750 of 751 present,
  so the risk is currently negligible — but it is unmeasured for arms 3–6, and mutual k-NN
  prunes hub edges hardest by construction.
- **"Moves toward the null" needs a defined behaviour for overshoot.** Per-arm nulls make
  overshoot measurable for the first time, and it is live rather than hypothetical.
  Overshoot means the router avoids hubs more than a score-blind walker; pathological
  overshoot looks like the Task 0 `w_hub` sweep — `hubfrac` collapsing with Adamic–Adar
  collapsing alongside it — which criteria 1 and 2 already catch. Treat overshoot as
  passing criterion 3, guarded by 1–2.
- **Criterion 4 will not discriminate among arms 3–6.** All four carry `percentile_rank`,
  and every rank variant eliminates zero-cost routed hops (adjudication §4.5), so all four
  should pass comfortably. It remains the gate certifying the rescale fixed the ceiling; it
  will not choose between `rankfix` and the damping arms.
  **Consequence:** the "Phase 2 ships with the ceiling defect unfixed" fallback occurs only
  if all four rank arms fail criteria 1–3. It is a genuine fallback, not the expected path.

**Superseded wording** (plan §2 C-2): "all six criteria still apply" and "no candidate beats
the control" are both stale and marked as such in the plan.

---

## 14. Task 14 complete, and a caveat on the hub-degree diagnostic (2026-07-22)

**Task 14 — damping in log space. Complete** (`d6fd6a3`, `0fb65ea`). Byte-identity gate
**PASSED**: a build from current code at the legacy config reproduces `graph-75k-v3.bin`
exactly. 93 builder tests; `test_replay.py` unmodified; Snyk clean.

The two-point confirmation reproduces the finding recorded in the adjudication: damping
does not fix the ceiling defect, it flips which way it fails — at `d = 0` the
ceiling-clipped edges point at hubs, at `d = 0.5` at micro-cliques. Cite the adjudication
for figures.

Review found no Critical issues. Three smaller ones, all closed: a stale multiplicative
formula comment that Task 14's own change had falsified (in both `pipeline.py` and
`config.py` — corrected, and it mattered because Task 15 reads those knobs), and two
instances of the report overstating what it verified.

**Fourth occurrence of the same pattern.** A delegated report claimed the gate was
"verified twice, independently" when one build's output had been hashed twice, and
attributed a slow cold build purely to environment without estimating the code's own
contribution. The code was correct both times. This is the failure mode §7 of the revised
plan names, and it has now happened four times — every instance caught by review, none by
tests.

### Caveat on the new hub-degree diagnostic

The plan now reports two numbers per arm alongside `hubfrac`: **frozen hub nodes present**,
and **mean degree over those nodes**. Presence catches hubs being removed from the graph;
mean degree catches them being pruned until they no longer function as hubs. Both are
correct additions and both are effectively free — measured at **well under a millisecond**
per artifact, off the same degree array `artifact_diagnostics` already computes.

**They must be reported as descriptive diagnostics, never as pass/fail for arms 3–6.**
Measured on the two existing artifacts, mean hub degree falls by more than an order of
magnitude under the cap, and the capped arm's maximum hub degree is exactly the configured
cap. Every arm from 2 onward is capped, so the number will sit near-constant across arms
3–6 and reports **the cap, not the routing** — which is precisely why the original
degree-collapse clause was retired. Used as a criterion it would reintroduce that
degeneracy under a new name.

**The sharper point:** neutering hubs is what the cap does *by design*, and it is what won
the blind listening test. A low mean hub degree is evidence the fix is working, not
evidence of damage. The metric cannot distinguish beneficial from pathological neutering on
its own — it needs the same pairing as overshoot, where criteria 1 and 2 catch the
pathological form because a graph pruned past usefulness takes Adamic–Adar down with it.

Their job is to explain **why** `hubfrac` moved, so a reader can separate "routed around
hubs" from "hubs were absent" from "hubs were pruned flat."

---

## 15. PRE-REGISTRATION — the `d025` vs `capfix` blind listening test (2026-07-22)

**Written before the test was run. No listening evidence for `d025` exists at the time of
writing.** The arms are built and the metrics are complete and committed
(`findings/2026-07-22-phase2-sweep-results.md`); nobody has heard `d025`. Recorded now so a
later reader can verify the readings were not fitted to a result.

### Why a listening test is the right instrument here

**This is the Task 0 mechanism** — blind, one-factor, owner-judged — which revised plan §4
amendment 8 already recognises as a warrant class in its own right. `capfix`'s own warrant
*is* a blind listen (execution log §12). `d025` is being held to **the same standard, not a
lower one.**

**It is not criterion 5 used as a selector.** Criterion 5 remains a veto. This is the
mechanism that decided `capfix` in the first place, applied to a second candidate.

**What justifies seeking further evidence after an inconvenient result.** This is the third
time this phase that evidence has been sought following an unwelcome outcome, and that
pattern deserves suspicion. The asymmetry that licenses it here: the sweep disqualified an
**instrument**, not an arm. Adamic–Adar and the overlap coefficient sign-flip between
slices at these effect sizes (§6 claim 41), and the specific claim that the rescale costs
overlap is an analysis-slice artifact that reverses on held-out (§6 claim 42). That finding
would have held identically had it favoured `capfix` — it is about the metric, not the
candidate. Criterion 6 failed on precisely the channel shown to be unstable.

### Pre-registered readings — fixed in advance

| Verdict | Action |
|---|---|
| **`d025` clearly better** | **Adopt `d025`.** Record that criterion 6 failed on a channel shown to be unstable, that the package comparison reproduced on `hubfrac` and `ceiling_hops` across both slices, and that the Task 0 mechanism resolved it. **Show the working; do not bury it.** |
| **No detectable difference** | **Adopt `capfix`**, per the pre-registered null outcome. The ceiling defect is carried to Phase 1 as an open item **with a success condition**. |
| **`capfix` better** | **Adopt `capfix`.** Phase 2 closes on strong evidence. |

### Run once

**The test runs once. If the result is disliked, it stands. A second listening test is
forbidden.** Under the "no detectable difference" and "`capfix` better" readings the
pre-registered null outcome is unchanged from before this test existed, so the test cannot
manufacture a win — it can only confirm the existing answer or overturn it on the same
evidence class that produced it.

### Conditions

- Blind, two ports, mapping written to a file **before** serving; the owner receives two
  bare URLs and no framing.
- Judge the **artist sequences, not the clips** — the clip-resolution defects are live in
  both arms, unrelated to Phase 2, and are Phase 1's work.
- The blind is imperfect: the arms differ in edge structure, so a determined search could
  distinguish them. Acceptable, and recorded here in advance rather than discovered after.

### Session hygiene

The session that produced the analysis is **not** running the test. It knows which artifact
is which and authored the analysis the test may overturn. A session knowing only "serve
these two files, hand over two URLs" is structurally cleaner — this is about the integrity
of the owner's ear, not about that session's conduct. Handover: `2026-07-22-HANDOFF-blind-test.md` (committed; `.superpowers/` is gitignored).
