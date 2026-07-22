# Phase 2 — Revised Plan (2026-07-22)

**Role: ACTIVE. Supersedes the remaining tasks of
[`2026-07-21-phase2-path-quality.md`](2026-07-21-phase2-path-quality.md).**
Tasks 1–13 of that plan stand as executed. Tasks 14–16 are amended here. Where this
document and the original disagree, **this document governs.**

**This is a redirection, issued by the project owner after a full review of the Phase 2
record.** The sections marked **CLOSED** are decisions already taken. They are not open
questions, and they are not to be re-argued, re-litigated, or "checked" before being
applied. Apply them.

**No figures appear in this document.** The quantitative record remains
`findings/2026-07-21-scoring-adjudication.md`. The audit trail remains
`../2026-07-21-phase2-execution-log.md`.

---

## 1. Why this exists

Phase 2 is 13 of 16 tasks complete and roughly 5–8 hours from done. Nothing is wrong with
the work: the tests pass, the gates that were meant to hold held, and the review process
caught real defects in the plan itself.

What the review found is a proportion problem, not a correctness problem. Ten of sixteen
tasks built measurement apparatus before a single graph was rebuilt, and the structural
defect that most plausibly explains the product's core complaint — routes funnelling
through the famous core — was found by Track B in one task and is **still switched off by
default.** The cheapest experiment that could change the adoption decision has never been
run.

This plan runs it first, removes the one remaining item with unbounded cost and no
demonstrated payoff, and takes Phase 2 to close.

**Standing rule adopted for the rest of this project:** on any question that ends in a
number, run the cheapest experiment that could change the decision *before* writing a
plan.

---

## 2. CLOSED decisions — apply, do not evaluate

### C-1. The bad-path screen is cancelled.

Not deferred again. Cancelled.

It failed its gate at Task 5, was deferred once (D6), re-deferred once (D9), carries three
known defects, and its calibration set contains a path mislabelled as good. Its only
identified viable signal is recorded as self-obsoleting once the Task 13 rescale lands —
which it now has.

**Do:** leave `badpath.py` and its tests in the tree, unreferenced, with a module-level
note that the screen was cancelled and why, citing this section. Close the three deferred
`badpath.py` findings in execution-log §7 as *cancelled with the screen*. Remove the
screen rework from §6 open items.

**"Unreferenced" requires edits — make them deliberately, before Task 15, not mid-run.**
`export_paths.py` imports and calls `screen_path`, and Task 15's harness spec still emits a
`flagged_paths` count. Remove both call sites and the count; keep the module and its tests.
A cancelled screen left wired into the harness is how it gets silently re-adopted.

**Do not:** attempt a rework, propose an alternative signal, or ask whether the
cancellation should be reconsidered given new information from Task 14.

### C-2. Adoption criterion 5 is replaced, not dropped.

The original criterion 5 was *"read paths show no junk hops and `flagged_paths` does not
rise."* The second clause dies with the screen. The first clause was always a proxy for
"does this sound right to a human."

**Replacement criterion 5:** the project owner uses the candidate artifact in the running
app and judges the paths acceptable. The exported HTML from `export_paths.py` supports
that judgement; it does not substitute for it.

This is a *strengthening* of the criterion, and it must be recorded as such in the findings
document. All six criteria still apply. "No candidate beats the control" remains a
pre-authorised outcome.

### C-3. Open items 2 and 3 close by decision, not by investigation.

- **The topological verdict has no error bar** (one rewire realisation). **Accepted as
  directional.** Do not run additional draws. Record in the findings document that the
  direction is relied upon and the magnitude is not.
- **The production router's excess hub-seeking is unexplained.** Task 0 below either
  answers it or it is accepted as open and carried into Phase 1.

Neither item gates the branch merge.

### C-4. Task 16's deletion requirement stands.

The losing option is removed from each config knob and raises, not left as a supported
mode. Unchanged from the original plan.

---

## 3. Task 0 — run this before Task 14

**This is the cheapest experiment that could change the adoption decision, and it has never
been run.** Everything downstream is calibrated by its result.

It is not a detour: `capfix` is one of Task 15's six arms. This builds it early and attaches
a listening session and a routing-time probe.

- [ ] **Step 1 — first, pull Task 15 Step 1 forward and do it here.**

Task 0 as originally written depended on code that does not exist. `load_or_freeze_hub_set`,
`hub-nodes-control.json`, and the `w_jump = 0` router are all created by **Task 15 Step 1's
wholesale rewrite of `run_baseline.py`**, which has not run. The current file is still the
Task 3 stopgap, calling `hub_node_set(store, 0.01)` directly with no freezing and no cache.

Do that rewrite now, exactly as Task 15 Step 1 specifies, with two modifications:

- Apply **C-1** while writing it: no `screen_path` call, no `flagged_paths` count. Do not
  write the cancelled screen into a brand-new file and then remove it a task later.
- Note that this is the one genuinely code-shaped step in Task 0, so per §7 it is
  subagent-and-reviewer work, unlike the rest of the task.

Beyond unblocking Task 0, this means the probe below runs through **the same code path Task
15 will use**. Otherwise Task 0 produces `hubfrac` from a throwaway script, Task 15 produces
it from the harness, and any discrepancy between the two is unexplainable.

Task 15 Step 1 is then already done; do not repeat it.

- [ ] **Step 2 — build BOTH `control` and `capfix`.**

Build two 75k artifacts with exactly the configurations Task 15 Step 2 specifies for its
arms 1 and 2 — `control` (`pre_symmetrise`) and `capfix` (`mutual_knn`), every other knob
at its current default. Pass config in the build script; do not edit tracked config files.
Write both manifest sidecars. Two builds, roughly a minute total (execution log §8).

**Building `control` here is not optional and not redundant.** It is required by Steps 3
and 4 below, and it is the same artifact Task 15 reuses. One build solves both.

- [ ] **Step 3 — anchor the frozen hub set on `control`, before routing anything.**

`load_or_freeze_hub_set` writes `hub-nodes-control.json` on first use, and every later arm
reads it. The file does not exist yet. **If `capfix` routes first it becomes the anchor,**
and since its max degree is bounded at 50 against the control's four-figure maximum, its
top-1%-by-degree is a materially different artist set. Every `hubfrac` in Task 15 would
then be measured against a degree-compressed hub definition — which is precisely the
"a variant wins by compressing its degree distribution" failure the frozen set exists to
prevent.

Route one throwaway query on `control` to force the freeze, or freeze it explicitly. Then
confirm the file exists and record its artist count before any `capfix` query runs.

**Commit `hub-nodes-control.json`.** It is frozen evaluation data, generated once and
immutable thereafter — the same class of artifact as `panel.json`, which is tracked. It is
not gitignored. It is also the single file that makes all six arms comparable: if it is
lost or regenerated in a later session, the next arm to run silently re-anchors it, which
is the exact failure this step exists to prevent, displaced in time.

**Also check, and record:** `control` filters the special-purpose entities (the knob now
defaults on), so it is *not* byte-identical to `graph-75k-v3.bin`, whose hub set produced
the baseline in `findings/2026-07-22-configuration-model-null.md`. Report the overlap
between the two hub sets. If it differs by more than a handful of nodes, Step 4's
comparison against that baseline carries a caveat and must say so.

- [ ] **Step 4 — serve BOTH artifacts, blind, and hand over.**

Serve `control` and `capfix` on two ports. **Do not tell the owner which is which** —
record the mapping in a file and hand over only the two URLs.

Two reasons this matters. First, the app has been dogfooded against the 5k dev graph; a
75k-vs-5k comparison would confound the cap fix with a 15× larger graph, and the whole
point of Task 0 is a one-factor test. Second, criterion 5 is a subjective judgement made by
someone who knows what he hopes to see. Blinding costs nothing here and removes the
largest available bias.

**The blind is imperfect, and that is acceptable.** `capfix` drops roughly 800 artists, so
searching for a missing one identifies the instance. Not worth engineering around. Record
the limitation in the log up front; if the owner does notice mid-session, that is a note in
the record, not an invalidation of the judgement.

- [ ] **Step 5 — OWNER: twenty minutes of use, across both.** 🛑

The owner uses both and answers one question: **in which, if either, is the "everything
routes through the famous core" problem less pronounced?** "No detectable difference" is a
valid and important answer.

**Judge the sequence of artists, not the clips.** The known clip-resolution defects —
wrong-artist matching and signed-URL expiry against a 30-day cache — are live, unrelated to
anything Phase 2 changes, and are Phase 1's work. They will surface as bad or missing audio
on some cards in *both* instances. Criterion 5 is the one genuinely subjective measurement
in this plan; letting a known unrelated defect colour it would waste the only human
judgement the phase gets.

Unblind afterwards. Record the verdict and the mapping in the execution log with both
sha256s. Do not proceed without it.

- [ ] **Step 6 — the routing-time probe, on BOTH artifacts.**

Route the panel's analysis slice under three routers — production weights, `w_jump = 0`,
and `w_hub` raised off its dormant default — against **both `control` and `capfix`**. No
rebuilds; both artifacts are already loaded.

**Why both.** The excess this probe exists to explain — the production router's `hubfrac`
sitting well above the topological baseline — was measured on the v3/control-family graph.
Probing `capfix` alone answers "does this channel bind on capfix," not "does it explain the
excess we actually recorded."

**Budget ~30–60 minutes, not ~20.** The bracketing below means several `w_hub` values, not
one: two artifacts × (two fixed routers + roughly four `w_hub` values) × the analysis
slice. Partly offset because `capfix` carries about a fifth of the control's edges, so
Dijkstra is far cheaper there and the control dominates the total.

**On the `w_hub` value — do not guess once.** A single arbitrary value that moves nothing is
indistinguishable from "this channel doesn't matter," and that misreading routes you to fork
row 3. Bracket instead: raise `w_hub` until it *demonstrably binds* — until `hubfrac` moves
materially or path quality visibly degrades — then report the range. A negative is only
informative once you have shown the term binds somewhere. If no value binds without wrecking
paths, that is the finding, and it is a real one.

**`w_hub` does not transfer between artifacts, and the report must say so.** The penalty is
log-scaled degree, zeroed at the graph's median and rising to 1.0 at its largest hub — so it
spans 0–1 on both and binds on both, but *at different values*, since `capfix` caps degree
at 50 while the control's runs to four figures. Consequences, both mandatory:

- Compare the two artifacts on **how `hubfrac` responds**, never on a shared `w_hub` value.
  "`w_hub = X` on control vs `w_hub = X` on capfix" is a meaningless comparison.
- Record every bracketed value as **"binds on this artifact,"** never as a tunable to carry
  into Phase 1. A number lifted out of its context is this project's single most repeated
  failure.

Report `hubfrac` for each router and artifact against the topological baseline in
`findings/2026-07-22-configuration-model-null.md`, subject to the Step 3 hub-set caveat.
This targets execution-log §6 open item 3 directly and costs no builds.

- [ ] **Step 7 — record and commit.** Verdict and probe numbers to the execution log; to
      the adjudication's ledger if they bear on a numbered claim.

### The fork

> **RESOLVED 2026-07-22 — row 1 fired.** `capfix` was preferred blind and decisively; the
> verdict and both artifact checksums are in execution-log §12. Consequences: Task 15 is a
> search for *incremental* gains over `capfix`, not for the fix; §4 amendment 3 re-baselines
> the scoring arms accordingly; and Phase 1 keeps its original ordering, since row 2 — which
> would have moved the routing weights ahead of the clip work — did not fire.

| Task 0 result | What it means | Effect on the rest of this plan |
|---|---|---|
| **Problem visibly reduced** by `capfix` alone | The inverted cap was the core defect | Task 15 is now about incremental gains. Run it as written, but do not agonise over a marginal winner — if no arm clearly beats `capfix`, adopt `capfix` and close |
| **Unchanged**, and the probe moves `hubfrac` materially | The defect is at **routing time**, not build time | Task 15 still runs (the rescale question is real), but the routing weights become Phase 1's first work item, ahead of the clip fixes. Record this prominently |
| **Unchanged**, and the probe moves nothing | Neither channel tested so far explains it | Complete Tasks 14–16 on the evidence available, adopt or don't, and close Phase 2 with the anomaly documented as open. Do not open a new investigation inside Phase 2 |

---

## 4. Tasks 14–16 — amended

**Task 14 — damping in log space.** Unchanged. Two-point confirmation as already narrowed
(D-decision recorded in the execution log). Observe the byte-identity gate; observe the
`expm1` ordering hazard flagged in the original plan's Known Sharp Edge — it has not gone
away.

**Task 15 — build, evaluate, decide.** **Step 1 was pulled forward into Task 0 Step 1 — do
not repeat it.** Otherwise as written, with six amendments:

1. **Rebuild `control` and `capfix` after Task 14 and require the hashes to be unchanged.**
   Task 0 built them *before* Task 14 modified `rescale_scores`'s `p99_log_clip` branch —
   the branch both arms use. The round-trip is exact at `d = 0` and both are `d = 0`, so
   they should be identical. "Should be" is what byte-identity gates exist not to rely on,
   and confirming an artifact's sha256 against its own manifest proves only that the file
   on disk is unchanged, not that the code producing it is. Without this, Task 15 compares
   one pre-Task-14 artifact against five post-Task-14 ones — **the exact two-factor
   confound that invalidated two earlier analyses.** Cost: about a minute. A mismatch is a
   finding, not a nuisance: stop and report it.

2. **Fix the compared pair set once, across all six arms.** `capfix` and the other
   `mutual_knn` arms drop roughly 800 artists, so some panel pairs will not resolve.
   Step 4's code intersects control-with-arm *pairwise*, giving each arm a different `n`
   and median deltas that are not comparable across arms. Instead compute the six-way
   intersection once, before any comparison, and run every paired test on that fixed set.
   Record the size of the intersection and what was dropped.

3. **Re-baseline criteria 1 and 2 for arms 3–6 against `capfix`, not `control`.**

   Task 0 resolved fork row 1: the cap fix won a blind listening test, and the mutual k-NN
   cap cut edge count by roughly three quarters while retaining 98.9 % of artists. Two
   consequences follow, and they point the same way.

   **(a) `control` is the wrong baseline for the scoring arms.** `rankfix`, `d025`, `d050`
   and `d075` all carry `mutual_knn`. Measured against `control`, every one of them is
   scored on a change they *share* — the cap fix, already settled — with the scoring change
   they are meant to isolate riding underneath it invisibly. All four could pass "improves
   over control" on the strength of something none of them contributed. **This is the same
   two-factor confound as amendment 1, in a different costume, and it is the one that
   invalidated two earlier analyses.**

   The paired-test machinery does not change; only which arm goes first. Compare `capfix`
   against `control` (settled by Task 0, reported for completeness) and arms 3–6 against
   `capfix`.

   **(b) Expect Adamic–Adar and overlap coefficient to fall for every `mutual_knn` arm,
   and do not read that as a quality regression.** Both metrics are built from common
   neighbours, so a large edge reduction depresses them mechanically. `capfix` may well
   score *worse* than `control` on criteria 1 and 2 while being the arm already preferred
   in a blind test.

   If that happens, the metrics are confounded by density — not the listening test by
   error. Overlap metrics have already been shown blind to a real failure mode on this
   project (adjudication §4.4), which is why criterion 5 was elevated. **Record the density
   effect explicitly in the findings document** so a future reader does not mistake it for
   evidence against the cap fix.

4. **Criterion 5 applies to `capfix` plus the top two arms after criteria 1–4** — not all
   six, which would cost hours and fatigue the judgement it depends on. `capfix` is now the
   reference arm, having already been judged. Serve them blind, as in Task 0 Step 4.
   Criterion 5 is a **veto, not a selector**: it can reject a metric-winner, never crown a
   metric-loser. If it vetoes the front-runner, judge the next arm rather than reopening the
   metrics.

5. **The harness no longer emits a bad-path count** (C-1). See §5 below.

6. The Step 6 STOP block stands unchanged and in full. Adoption remains a human decision;
   present evidence, do not choose. **Do not relax a criterion to produce a winner.** Note
   that the pre-authorised null outcome now reads **"no candidate beats `capfix`"** — and
   in that case `capfix` is adopted, not `control`.

**Task 16 — adopt.** As written.

---

## 5. Closeout — time-boxed

- **Final whole-branch review: one hour, hard stop.** Triage execution-log §7 into "fix
  now" and "not doing." Both lists go into the log. Hygiene findings do not gate the merge.
- **The Snyk Low CWE-23 in `api/eval/export_paths.py`** is fixed or explicitly accepted
  with a reason. It is **not** pre-existing — it is new on this branch, and has twice been
  misreported as pre-existing.
- **Then stop.** Phase 2 closes. The next work is Phase 1, and it is planned separately.

---

## 6. Reclassification for Phase 1

**C3 — `w_floor` is a no-op and `known` degrades to a bare hard exclusion — is a
pathfinding defect, not a UX item.** The roadmap files it under "Phase 1: bypass," next to
button fixes, and that misfiling is part of why it is unscheduled behind sixteen tasks of
graph work.

It is a direct contributor to the founding complaint: rerolls returning artists at the same
popularity band. When Phase 1 is planned, C3 leads it, with the routing-weight work from
**Task 0 Step 6** if the fork sends it there.

Note this in the roadmap at Task 16 Step 5. Do not fix it inside Phase 2.

---

## 7. How to execute this

**Keep subagent-driven execution for implementation. Do not delegate interpretation.**

Tasks 1–13 were executed almost entirely by subagents, with a reviewer per task, and that
worked — it caught arithmetically impossible fixtures, a contract violation, an
unsatisfiable git step, and a docstring contradicting its own code. Nothing here overturns
that pattern. It is retained.

But the remaining work is a different shape. Tasks 1–13 were *write code, test it, report*.
Task 0 and Task 15 are *run a thing, look at the result, and hand a judgement to a human*.
The distinction matters because this project's characteristic failure has not been bad
code — it has been **bad reporting about correct code**, three times, each in a delegated
report: Task 7's prose contradicted its own clean implementation; a distinct-value count
was wrong by an order of magnitude; a Snyk finding was labelled pre-existing twice when it
was new on this branch. All three were caught, but late, and by luck as much as process.

So, per task:

| Task | Mode | Why |
|---|---|---|
| **Task 0** | Controller runs it, or a subagent returns **raw output only** | Its product is an owner judgement. No interpretation layer between the numbers and the person deciding |
| **Task 14** | Subagent + reviewer, as established | A genuine code task with a real sharp edge (the `expm1` round-trip) and a byte-identity gate to catch it |
| **Task 15** | Controller drives; delegate the unattended compute if useful | Steps 3–5 are script runs; Step 6 is the human adoption decision. Do not let a subagent pre-digest the evidence that decision rests on |
| **Task 16** | Subagent + reviewer | Mechanical: defaults, fixtures, docs |

**The rule, stated once:** delegate execution freely; return raw numbers, not conclusions.
Any step whose output feeds the Step 6 STOP block is reported with the figures that produced
it, never as a verdict alone.

**Parallelism: none is available.** Task 0's steps are sequential with a human stop at
Step 5. Tasks 14 → 15 → 16 chain through byte-identity gates. Task 15's six arms must
serialise regardless of who runs them — they share one working tree and `builder/scratch/`,
and the hub set is frozen from whichever arm runs first, so `control` must anchor. Dispatch
for isolation and review quality if you want them; do not expect a speedup.

**One risk specific to delegation here:** a subagent handed Task 0 or Task 14 cold does not
have the reasoning behind §2. The likeliest failure mode is a well-argued proposal to revive
the bad-path screen. **Every brief written from this plan must quote §2 in full.**

---

## 8. What this plan does not change

The Phase 2 process has been sound and the following are explicitly retained:

- The single-source-of-numbers rule.
- The execution log, and the discipline of recording when the plan itself was wrong.
- Pre-registered decision rules, and the standing authorisation to return a null result.
- The remaining hard gates: byte-identity of the control build, and the held-out slice
  reproducing criteria 1–4.
- Never optimise against a screen or a metric.

The instruments built in Tasks 1–10 were expensive. Task 15 is where they pay for
themselves. Finish it.
