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

---

## 16. Task 15 blind listening test — RESULT (2026-07-22)

Executed per `docs/superpowers/2026-07-22-HANDOFF-blind-test.md` by a session held
deliberately blind: it read the handoff, Part C and Part D of `session-start`, and
nothing else. It did **not** read the sweep findings, adjudication claims 41–45, or §15
of this log before the verdict below was written and committed. That ordering was the
owner's instruction, so that the recorded wording could not be shaded by knowing what
it implied.

### Mapping (randomised before serving, unblinded only after the verdict)

| Frontend | API | Arm | sha256 |
|---|---|---|---|
| `localhost:5175` | `:8000` | **`d025`** | `2811e87d1c900e4ec233317c05143ccaec5a3f0e1fb3c531c04455594bb27e65` |
| `localhost:5174` | `:8001` | **`capfix`** | `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237` |

Both checksums verified against the file and its manifest sidecar before serving. The
URLs were presented to the owner in randomised order (5174 first), because he held a
prior from the Task 0 test about which port had won there.

**Differential check passed before handover**: the same query (Miles Davis → Daft Punk)
returned paths of length 5 and 8 with different mbid sequences across the two stacks, so
the two stacks were demonstrably serving different artifacts and not one artifact against
itself.

### Verdict: `capfix` (served on 5174)

The owner's report, **verbatim**:

> Here is my feedback, sessions identified by port number. In general, both sessions did seem to include a lot of hubs, but there is a detectable difference, and it becomes most noticeable when using the bypass feature. My gut tells me to some extent, this is expected. The first path is most likely to route through hubs / well-known artists, but using either bypass *should* result in more "creative" routes that involve less well-known artists and require a longer path (more steps). I'll pause here and say that these conclusions are my gut instinct, not data-driven, but I'd also say that this is desired behavior and replicates to some degree the original boilthefrog product behavior. With that stated, here is my specific feedback:
> 5174 feels like the superior option based on the experience. A good example to look at is The Shins pathed to System of a Down.
>
> 5174 produced a 6 artist path. After 4 bypasses, the path length started to grow to 6 length. After 7 bypasses, it jumped to 11. 9 bypasses reduced the path length back to 8, but started to show me artists I was unfamiliar with.
>
> Same start and end, 5175 produced a 4 artist path, and length didn't change until the 7th bypass, which only lengthened to 5. The next several bypasses only swapped out the artist that I bypassed, keeping the rest of the path the same, and just swapping the one well-known artist for another well-known artist. I pushed it further and further, and really at no point did the path avoid well-known artists or lengthen beyond 7 artists.
>
> I recognize the above feedback focuses on bypass. I don't know if there is any bias built into focusing on that area, so I also ran several paths and avoided using bypass. Some challenges in truly testing here because some examples of obscure artists that I know of weren't found in the system (e.g. Bee Caves) and using obscure artists that I *don't* know well creates a challenge where it's hard for me to tell how good the path is (Chinese Pianist Lang Lang is a good example of an obscure artist that I had a hard time evaluating).
>
> Routing Orville Peck to Kendrick Lamar produced pretty similar paths:
> http://localhost:5174/path/437b356d-88f1-4dde-af5e-dec1c9d7dde4/381086ea-f511-4aba-bdf9-71c753dc5077
> http://localhost:5175/path/437b356d-88f1-4dde-af5e-dec1c9d7dde4/381086ea-f511-4aba-bdf9-71c753dc5077
>
> Routing Young Gun Silver Fox to Gorguts also produced seemingly fairly similar paths:
> http://localhost:5174/path/2e111d6d-fce9-46ff-b33a-7eed7300f9d4/a95ef44c-aeda-4222-9d57-10b28240e634
> http://localhost:5175/path/2e111d6d-fce9-46ff-b33a-7eed7300f9d4/a95ef44c-aeda-4222-9d57-10b28240e634
>
> Routing Young Gun Silver Fox to Tony Williams was the best example I could find where the first generated path had real differences:
> http://localhost:5174/path/2e111d6d-fce9-46ff-b33a-7eed7300f9d4/b6a30b58-6b00-47c4-a031-c62a6981461f
> http://localhost:5175/path/2e111d6d-fce9-46ff-b33a-7eed7300f9d4/b6a30b58-6b00-47c4-a031-c62a6981461f
>
> I'm not familiar with Tony Williams, so it's hard to say for sure which artists within this path (on his side) are considered hubs. 5174 had a longer path that included several names I'm familiar with (Sinatra, Ray Charles), but also several artists on the Young Gun side that I don't think are as well known. 5175 produced a shorter path, that routed through Vulfpeck. My own music tastes may bias me, but to me Vulfpeck feels like a hub, and this path seems to transition faster to hubs (tricky because it's shorter)
>
> Summarizing a lot of "thinking out loud", my gut tells me 5174 is superior, but the conclusion is less directly related to the number of hubs found, and more drawn from the overall experience of generating paths, what the paths look like, and how the bypass function changes the paths. Hubs still appear quite frequently in both

Translating ports to arms, and nothing else: **the owner preferred `capfix` over `d025`.**

### Notes recorded alongside the verdict

- The verdict is explicitly **not** a hub-count judgement. The owner states hubs appear
  frequently in both arms, and that his preference derives from bypass behaviour and
  overall path experience rather than from hub incidence.
- The **discriminating channel was bypass**, not the first generated path. On three
  no-bypass A/B comparisons he judged the arms similar (Orville Peck → Kendrick Lamar;
  Young Gun Silver Fox → Gorguts) with one showing real differences (Young Gun Silver
  Fox → Tony Williams). This is a channel the sweep did not measure and the test was not
  designed around; it emerged from use.
- The owner **volunteered a prior mid-report** about desired bypass behaviour, citing
  boilthefrog as the reference. He flagged it himself as gut instinct rather than data, and
  flagged the possible bias of concentrating on bypass. Recorded as stated; **not
  adjudicated here.**

  **Stated precisely, in his own correction of this log's first draft** — which had
  paraphrased it as "first paths *should* favour hubs", and he rejected that wording:

  > I'd adjust that to: first paths are *expected* to favor hubs more so than bypassed
  > paths. When tuning and adjusting, we're not aiming for a result like "first paths
  > should never hit hubs". Part of our desired behavior however is that more bypasses
  > (and especially bypasses of hubs) should result in fewer and fewer hubs in each
  > iteration. This is something to explore in more depth at a later date.

  The distinction is load-bearing for anyone tuning later: the target is a **monotone
  decline in hub incidence across successive bypasses**, not a hub-free first path. A
  tuning run that suppressed hubs in the first path would satisfy the paraphrase and miss
  the actual goal.
- **Coverage limits he raised**: some obscure artists are absent from the graph (e.g. Bee
  Caves), and obscure artists he does not know well (e.g. Lang Lang) are hard for him to
  evaluate. Both bound how far a listening test can probe the obscure tail.
- The pre-registered known limitation — that the arms differ in edge structure and a
  determined search could distinguish them — was disclosed to the owner up front. He did
  not report having identified the arms.

**Run once. This result stands.** Per the handoff and §15, a second listening test is
forbidden regardless of what the metrics say.

---

## 17. Task 16 — adopt (2026-07-22). Phase 2 closes.

Executed inline rather than by subagent. The revised plan §7 lists Task 16 as
"subagent + reviewer, mechanical"; that is a permission, not a requirement, and the task
turned out to be nine edits plus three suite runs, below the threshold where delegation
pays for its own context transfer. The plan's stated worry about delegated work — *bad
reporting about correct code*, three times this phase — argues for doing and verifying in
one place when the task is this size.

### Adopted configuration

`BuilderConfig` defaults are now the `capfix` arm:

| Knob | Adopted | Deleted |
|---|---|---|
| `cap_strategy` | `mutual_knn` | `pre_symmetrise` — raises |
| `similarity_rescale` | `p99_log_clip` | `percentile_rank` — raises |
| `similarity_damping` | `0.0` | nothing — see below |

**C-4 discharged, with one scope narrowing the owner approved.** Task 16 Step 1 said to
delete the loser from *each of the three* knobs. Spec §8 risk 4 names only
`similarity_rescale`; `config.py`'s own comments marked `cap_strategy` and
`similarity_rescale`. Nothing marked damping, which is a continuous axis rather than a
two-option switch — deleting it would have removed `damped_strength` entirely. **Decision:
delete the two enum losers, keep damping as a supported float defaulting to 0.0.** The
plan's "each knob" over-reached relative to both the spec and the code.

Enforcement is a `BuilderConfig.__post_init__` raise, not just a comment, so a config
carried over from a sweep script fails loudly instead of silently selecting removed code.
`rescale_scores`'s `percentile_rank` branch and `pipeline.py`'s `pre_symmetrise` truncation
are deleted, not commented out.

### Two defects found while executing, both real, both fixed

**1. The test fixtures were never actually committed.** `.gitignore` had `*.bin` with
`!tests/fixtures/*.bin` as the exemption, and `CLAUDE.md` asserted that "a fresh clone has
the test fixtures." Both were wrong: **a gitignore pattern containing a slash is anchored
to the directory holding the `.gitignore`**, so `!tests/fixtures/*.bin` only ever matched a
top-level `tests/fixtures/` that does not exist. `api/tests/fixtures/graph-fixture.bin` was
untracked, so **the API suite could not run on a fresh clone at all.** Fixed to
`!**/tests/fixtures/*.bin`; both fixtures now committed; `builder/scratch/` still ignored.

This is the shape CLAUDE.md warns about — a document asserting something about the world
that is not true — and it survived because nobody had cloned fresh.

**2. The Snyk Low CWE-23 in `api/eval/export_paths.py` is fixed**, not accepted. Revised
plan §5 required one or the other and flagged that it had twice been misreported as
pre-existing. It was new on this branch. The output path is now resolved against the repo
root and refused if it escapes; verified by running a `../../../../evil.json` argument and
seeing it rejected. **Behaviour change worth knowing:** a relative output path is now
interpreted relative to the repo root, not the current working directory.

### Fixtures regenerated from the adopted graph

Source: `builder/scratch/graph-t15-capfix.bin`
(`c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237`).

| Artifact | sha256 | In git |
|---|---|---|
| `builder/scratch/graph-5k.bin` (5000 nodes) | `3029aaa2cdddc158e8d4ccb254a8df75b2f12fdca622f860cdf2572e322ecf64` | no — gitignored dev graph |
| `{builder,api}/tests/fixtures/graph-fixture.bin` (500 nodes) | `a45d160aeafdfe46a5b584d78b37b54f5fbae116d365ae454cac97ae4d927750` | **yes, now** |

### Gates

- **All three suites green**: builder 93 passed, api 116 passed, frontend 31 passed.
- **One fixture-dependent assertion updated, not weakened.** `test_fixture_has_real_artists`
  asserted `artist_count == 200`; the plan specifies `--size 500`, so the expectation moved
  to 500. The assertion still pins an exact count.
- **New tests added** rather than only changed: the adopted defaults are pinned
  (`test_phase2_adopted_defaults`), and both deleted options are asserted to raise
  (`test_losing_options_are_deleted_not_supported`,
  `test_percentile_rank_was_deleted_and_raises`). Tests for the deleted `percentile_rank`
  implementation were removed with it.
- **Snyk clean**: 0 issues across `builder/src/artistpath_builder`, `api/src/artistpath_api`,
  and `api/eval`.

### Carried to Phase 1, with success conditions (roadmap Phase 1 section)

1. **The p99 ceiling defect survives adoption.** The adopted rescale is still the clip. The
   rank transform that removes the ceiling *lost* the blind test, so the defect is real but
   not obviously worth fixing by that route. **Success condition:** a rescale that removes
   the ceiling and wins or ties a blind listen, or an explicit recorded decision to keep it.
2. **Bypass hub-decline is unmeasured.** The channel that decided this phase's adoption is
   one the sweep never measured. **Success condition:** a hub-incidence-versus-bypass-count
   measurement exists, and C3's fix moves it.

Also filed: **C3 is reclassified in the roadmap** from a UX item to the pathfinding defect
that leads Phase 1, per revised plan §6.

### What should not be re-litigated

`capfix` is adopted on two independent blind listening tests (§12, §16). Damping was tested
at 0.25 / 0.5 / 0.75 and rejected. The overlap-family metrics are not trustworthy at these
effect sizes (adjudication §6 claims 41–42) — that is a finding about the *instrument*, and
it would have held identically had it favoured `capfix`. A third listening test is
forbidden.

---

## 18. Closeout — §6 and §7 resolved, every deferral given an address (2026-07-22)

Revised plan §5 requires §7 triaged into "fix now" and "not doing", both lists retained.
Closeout A3 requires every open finding to carry a **success condition**. This section is
both. **Nothing below is left as an unranked backlog item.**

### §6 open items — final status

| # | Item | Status |
|---|---|---|
| 1 | Bad-path screen rework | **KILLED.** See below. |
| 2 | The null result has no error bar | **OPEN → Phase 1.** Success condition: *before any decision leans on the configuration-model null more heavily than Task 14's narrowed sweep did.* If nothing ever leans on it harder, it never needs the error bar and the item expires unactioned — that is a legitimate terminal state. |
| 3 | Production router's excess hub-seeking is unexplained | **OPEN → Phase 1, accepted as unexplained.** Revised plan §2 pre-authorised exactly this: Task 0 either answers it or it is carried. It was not answered. Success condition: *C3's routing-weight work either explains the excess or measures that it no longer exists.* Suspected to be the popularity term; still unproven. |
| 4 | Task 16 must delete the losing option from each knob | **DONE**, with one approved narrowing — damping keeps its knob (§17). |

**Item 1 is killed, not deferred again.** The bad-path screen was cancelled by revised plan
§2 C-1. It is genuinely unwired: `screen_path` is imported by nothing but its own tests, and
`run_baseline.py`'s header states it is deliberately not imported. This is a **kill on a
closed path, not on a count** — the rework was deferred twice (D6, D9), and D9 already
recorded the reason its only viable signal self-obsoletes: the ceiling-hop signal
(claim 33) becomes uninformative once the rescale removes the ceiling tie-mass.

That reasoning has now partly inverted and it does not revive the item. The adopted arm
**kept** the clip, so the ceiling tie-mass still exists and the signal is not obsolete after
all. The screen stays killed anyway, because its calibration set was independently defective
(claim 32) and the module never earned its place in the product. **If the premise changes —
if a future phase wants a bad-path screen — this is a revival decision with the reasoning
above, not an archaeology project.**

### §7 triage

**FIXED NOW (1 item).**

- **Snyk Low CWE-23, `api/eval/export_paths.py`.** Fixed in §17, not accepted. Output paths
  resolve against the repo root and are refused if they escape; verified by running a
  traversal argument. Revised plan §5 required fix-or-accept, and flagged that it had twice
  been misreported as pre-existing. It was new on this branch.

**NOT DOING — `badpath.py` and its tests (3 items).** Success condition: **closed, won't
fix.** The module is cancelled and unwired. Fixing a docstring contradiction, an
endpoint-incident hop, and a test that passes via the wrong signal, all inside dead code, is
work with no consumer. These reopen only if the screen is revived, and they are listed here
so a revival starts from a known defect list rather than a clean-looking module:
- signal 2 iterates endpoint-incident hops though the docstring claims interior-only
- module docstring and threshold comment assert contradictory things (§4.4 overturned the former)
- `test_badpath.py`'s blank-name test passes via the wrong signal

**NOT DOING — hygiene (3 items).** Success condition: **closed, won't fix.** Unused imports
in plan-prescribed test blocks; `manifest.py`'s untyped `graph` parameter and its timing
exclusions. None has a failure mode.

**CARRIED to Phase 4 (CI + tests) — test-coverage gaps (7 items).** Success condition:
**each is closed when Phase 4's test pass covers it, or explicitly dropped there.** Phase 4
already owns "missing regression tests" in the roadmap, so these join a queue that exists
rather than creating one. They are real gaps in live code, which is why they are not
"won't fix":
- `test_evaluation.py` — the degree-1 Adamic–Adar guard is never exercised
- `test_diagnostics.py` — `corr_score_log_degree` uncovered, despite being the field that exposed the v2/v3 discrepancy
- `test_stats.py` — Holm with duplicate p-values untested, so the documented tie-break is unverified
- `test_panel.py` — nothing constructs two differently-ordered stores, which is Task 6's entire purpose
- `panel.py` — `by_name` has no duplicate-name guard
- Task 11 — no end-to-end test that the build drops filtered nodes
- `test_graph.py` — the mutual k-NN symmetry test uses an already-symmetric fixture, so it cannot distinguish enforcing from preserving. **Now more load-bearing than when filed:** mutual k-NN is the adopted cap strategy, not one of two options.

**CARRIED to Phase 4 — dependency hygiene (1 item).** `scipy>=1.14` has no upper bound and
no tracked lockfile pins it. Success condition: **closed when CI pins a resolved dependency
set.** A CI pipeline that cannot reproduce its own dependency versions is the actual defect;
fixing the bound alone would not.

### Closeout checks that produced nothing

Recorded because a silent check is indistinguishable from a skipped one.

- **B2 reachability.** Modules added this phase: `manifest.py`, `diagnostics.py`,
  `panel.py`, `export_paths.py` are all imported by live callers. `nulls.py` and `stats.py`
  are imported only by their own tests — **not orphans in the "built but never wired" sense:
  both are research tooling invoked manually, and both produced findings that are in the
  record** (the configuration-model null; the sweep's paired tests, sweep results §9).
  `badpath.py` is the deliberate cancellation above.
- **B3 vacuous-test spot check.** Three mutations, all caught by name-appropriate tests:
  disabling the `cap_strategy` guard failed `test_losing_options_are_deleted_not_supported`;
  removing the p99 clip's ceiling clamp failed
  `test_p99_log_clip_reproduces_the_legacy_expression_exactly`; turning mutual k-NN into
  union k-NN failed three `test_graph.py` tests including the degree bound. No vacuous test
  found among the invariants that matter.
- **Figure drift.** Two doc restatements of the zero-cost-hop share were converted to
  citations (roadmap; `builder/.../config.py`). **Two figures in `config.py` were left as
  literals deliberately** — the 78.7 % / 99.98 % clamp shares in the damping note are a
  hazard warning at the point of use, and a developer about to raise damping needs the
  magnitude in front of them, not a link. The completed Phase 2 plan's own restatement was
  left alone: it is a historical record of what the plan said.
