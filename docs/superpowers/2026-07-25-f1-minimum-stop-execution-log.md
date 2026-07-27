# Execution log — F1, every journey gets at least one stop, 2026-07-25

**Role: COMPLETE.** The retained record of the F1 implementation. **F1 was discharged
2026-07-26** — its condition was an observation and the observation happened; see
[`NEXT.md`](NEXT.md), which owns status. *(This log read `Role: ACTIVE` until 2026-07-27.)* Distilled from the
subagent-driven ledger at `.superpowers/sdd/2026-07-25-f1-minimum-stop/progress.md`,
which is **gitignored and now deleted** — this document is what survives.

Governing design: [`specs/2026-07-25-f1-minimum-stop-design.md`](specs/2026-07-25-f1-minimum-stop-design.md).
Plan: [`plans/2026-07-25-f1-minimum-stop.md`](plans/2026-07-25-f1-minimum-stop.md).
Branch `f1-min-stop`, **PR #23, open and not merged.**

**Figures are cited, not restated.** The graph figures this work rests on are owned by
[`findings/2026-07-25-mutual-knn-stranding.md`](findings/2026-07-25-mutual-knn-stranding.md).

Identifiers are namespaced **`FMS-`** — disjoint from `C`, `F`, `A`, `R`, `T3-`, `TF-`,
`MKS-`, `ASC-` and `BYP-`, and from the bare `D`/`P` series already load-bearing in
`findings/2026-07-23-track2-protocol-analyst-review.md` and
`specs/2026-07-23-track2-preregistration.md`. **An earlier draft of this document used bare
`D1`–`D4` and `P1`–`P3` and collided with both**; the documentation audit caught it within
the hour and it was renamed before this document was cited anywhere.

---

## 1. What shipped

The router runs its normal search. **If the result is exactly the two chosen artists**, it
runs again with their direct connection forbidden. A route found is the forced stop; no
route means the two cards are returned with `stop_rule = "adjacent_only"`, and the page
renders a line between the cards saying they are next to each other.

**The detour is chosen by the existing cost function, unrestricted.** This is the load-
bearing decision and the reason the work was allowed to proceed during the path-quality
pause: any *new* rule for picking the inserted artist would be scoring, and scoring is
paused. Two consequences were accepted rather than tuned away — detour length varies (§6
owns the spread) and a famous pair gets a famous stop (`Radiohead → Weezer` inserts The
Beatles). Both are queued as use-the-app questions because no offline metric can settle
them.

`stop_rule` is a wire contract: snake_case on the wire, `stopRule` in the frontend,
typed as a closed three-literal union on both sides. It is a status, not a
popularity- or degree-derived quantity, so the currency-in-the-name convention does
not apply — noted because that exemption will be questioned.

## 2. Decisions taken, with reasoning

**FMS-D1 — the message was built now rather than deferred.** The owner's original question was
whether the forcing could ship with the explanatory line deferred. It could: a status field
on the response is the seam, because only the router can know a stop was forced (once
inserted, the result is indistinguishable from any other path). The recommendation changed
after measurement — the pairs that cannot be given a stop turned out to include recognisable
artists a person might plausibly search (`Doves → Elbow`, `Dizzee Rascal → The Streets`,
`Serge Gainsbourg → Charlotte Gainsbourg`), not the exotic corner first assumed. **Owner
chose to build it.**

**FMS-D2 — the session's own exposure estimate was wrong and was corrected.** The first read
weighted by how many such pairs exist in the graph and concluded a user would have to go out
of their way to meet one. That conflated *rare in the graph* with *rare in use*. The owner's
push for the artist names is what exposed it. Recorded because the error is reusable: **a
per-pair rate is not an exposure rate when users do not select uniformly.**

**FMS-D3 — Tasks 4 and 5 of the plan were merged into one dispatch.** The plan had Task 4 ending
with a deliberate typecheck failure that Task 5 resolved. A reviewer would rightly call an
intermediate non-building commit a defect, and the split carried little review value since
both halves are one prop added and consumed. Controller decision, not escalated: internal
process with no bearing on shipped behaviour.

**FMS-D4 — F1 is deliberately NOT marked discharged.** Its condition is anchored to an
observable (execution log of 2026-07-25, §16 — cite it, do not restate it), and that
observation is the owner running the queued entry. Marking it closed on the strength of a
passing test suite would repeat the exact failure that §16 documents.

## 3. Defects found in the plan itself

All three were in the plan, which this session wrote; none were implementation errors.

**FMS-P1 — the verification's central check was tautological.** It compared `find_journey`
against `find_path` for non-adjacent pairs, but `find_journey` re-runs `find_path` with
identical arguments and returns it unchanged in exactly that case. It could not fail, and it
never exercised the detour branch — the only branch the work added. Found by the task
review. The loop is kept, **relabelled honestly as a guard on the early return**, and a new
check samples adjacent pairs from the CSR arrays where the new code actually runs.

**FMS-P2 — "adjacent implies the direct edge is cheapest" is false.** The replacement check
asserted that any adjacent pair must hit the new branch. A weak direct connection can cost
more than two strong hops, so the cheapest route between neighbours can already run through
a third artist; `Tina Malia → Lafa Taylor` routes via Bassnectar and `natural` is correct
there. The implementer hit the assertion and **stopped rather than softening it**, which is
the only reason this was caught. The check now partitions by what the search actually
returns, and the premise error is recorded in the script so it cannot cost a third round.

**FMS-P3 — a figure was restated under a citation pointing at the wrong identifier.** The
`find_journey` docstring made an artist-level claim while citing `MKS-6`, which owns
pair-level figures; the artist-level owner is `MKS-3`. Found by the final whole-branch
review. Both restatements removed; nothing in this branch restates a figure.

**The pattern across all three: a confident premise about the graph that the graph
contradicts.** Every one was caught by running against the real artifact, none by reading.

## 4. Gate outcomes

| Gate | Outcome |
|---|---|
| Per-task reviews (Tasks 1, 2, 3, 4+5) | **Passed clean, no fix rounds** |
| Task 6 review | **Failed** — 1 Critical (`FMS-P1`), 1 Minor. Two fix rounds; round 1 blocked on `FMS-P2` |
| Final whole-branch review | **Failed** — 2 Important, 6 Minor. One fix wave, all eight addressed |
| Fix-wave re-review | Passed, no new breakage, verdict ready to merge |
| Real-graph verification | **Passed** — all four checks, 40 s |
| Vacuous-test check (closeout B3) | **Passed** — three deliberate breaks each turned the suite red |

**No gate was worked around.** Suites at closeout: builder 115, api 153, frontend 64;
build and lint clean (one pre-existing `vite.config.ts` warning); Snyk `snyk_code_scan`
over `api/src` 0 issues.

## 5. Corrections to the prior record

- **F1 is no longer "decided but not built."** `CLAUDE.md`'s orient table and
  `2026-07-25-HANDOFF-clip-playback.md` both said so and are now corrected. **A
  well-meaning editor must not revert them.**
- `api/README.md` documented the path response without `stop_rule`. Corrected — it was
  owned by no task, which is how absence-class defects arise.
- The design's §7 asked for a byte-identical comparison against current output that the
  merged script does not perform. The claim holds by construction plus the unchanged
  suites; §7 now records what was asked versus what was done rather than asserting a
  verification nobody ran.

### Added after merge, 2026-07-26 — the evaluation harness does not have F1

Not a correction to this work, which never claimed otherwise: `eval/` was outside F1's
scope and no document said it had changed. It is recorded here because **nothing said it
had not**, and the consequence only bites a future measurement.

`app.py:71` calls `find_journey`. `eval/run_baseline.py:97`, `eval/tune_weights.py:64` and
`eval/export_paths.py:242` all call `find_path` directly, so for a graph-adjacent pair the
harness still gets the two-card result the app no longer returns. **The three then treat that
result differently — read from source, not measured:** `run_baseline.py:98` discards it
(`len(path) < 3: continue`), so the baseline metrics never saw adjacent pairs and still do
not; `tune_weights.py:65` keeps it (`len(path) >= 2`), so Optuna scores paths whose interior
is empty; `export_paths.py` applies no length filter at all, so a two-card path falls past
the no-path guard (`:244`) and is exported as a one-hop cell (`:250`). **Switching the harness to
`find_journey` is therefore not a no-op on any of the three** — it would add to the baseline
pairs that were previously dropped, and replace the degenerate contributions in the other two
with real detours. The pair set is the frozen `panel.json`, not a random sample; **how many
panel pairs are graph-adjacent is unmeasured**, so the size of the effect is unknown in all
three cases. **`FMS-N1`** — `N` for notes added after merge, disjoint from this
document's `FMS-D` (decisions) and `FMS-P` (plan defects).

`.claude/agents/ml-graph-analyst.md` now states this and requires an analyst to say which
of the two it measured. That is a guard, not a fix.

**Open, and the owner's: should the harness call `find_journey`?** Not decided here and
nothing in `eval/` is touched — it changes what every path-quality measurement sees, and
that work is paused. It is also not obviously right: tuning weights against `find_path` is
defensible, because F1 adds no scoring. **Success condition:** settled either way when
path-quality work resumes, before any harness result is read; or closed as "accepted, won't
fix" if the divergence is judged immaterial with that reasoning recorded.

## 6. Operational measurements with no other home

- Real-graph verification: **40 seconds** after sample sizes were cut (the first version
  was slow enough that nobody would run it twice, which makes a check worthless however
  sound it is).
- Adjacent-pair partition, 100 pairs: 2 needed no forcing, 88 forced, 10 could not be
  given a stop. **The 10 is sample-biased and must not be read as a rate** — the script
  draws a random artist then one of their connections, so artists with very few
  connections are over-drawn. The pair-level figure is owned by `MKS-6`.
- Inserted artists per forced stop: min 1, median 1, max 13.

## 7. Standing context layer (closeout D6)

Repo half: **net zero** across this work — `git diff --stat de27410..HEAD` over
`CLAUDE.md`, `.claude/skills/`, `.claude/agents/` showed no change until closeout, whose
only edit is a **correction** of a now-false status line, not an addition.
`memory/` total: **435 lines**.

**One growth item is NOT taken and is left to the owner.** `.claude/agents/ml-graph-analyst.md`
describes the router as plain Dijkstra over the cost function. That is still accurate for
scoring questions, and its cost function was checked and is complete — but the definition
now omits that a two-card result is re-routed, which is inside its remit for *path-quality
metrics*. Adding a line would grow the layer that taxes every session, so it is his call,
not this session's.

## 8. Open, and what I would do

**Nothing is in flight.** No dispatched subagent, no background job, no half-written
directory. The SDD workspace was deleted after the final review, as the ritual directs.

The owner's, in order: **merge PR #23**, then **run the queued use-the-app entry** — that
entry is what discharges F1, and it asks the two questions no measurement can answer
(whether a long forced detour still feels like a journey, and whether a famous pair routing
through The Beatles reads as reasonable). Then **Gate 1 → Gate 2**.

**If continuing, I would not start anything new before that run.** F1 is the last named
Gate 1 item, and every remaining candidate — the p99 rescale above all — sits behind the
path-quality pause, which is his trigger and never a session's.
