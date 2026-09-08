# `LBD-` plan review — outcome

**Role: ACTIVE, and AUTHORITATIVE for the review's outcome.** This is the readable entry
point for two independent reviews of the `LBD-` design and plan, run 2026-09-06 at the
owner's request before any arm executes.

**It owns no figures.** Every number the reviews produced is owned by
[`builder/analysis/2026-09-06-lbd-plan-review/`](../../../builder/analysis/2026-09-06-lbd-plan-review/README.md)
and is cited from here, never restated. Read that directory for magnitudes; read this for
what the reviews mean and what is now owed.

**It changes no governing document.** The design's §0 and §4, and every task in the plan,
are exactly as they were written. The corrections below are recorded, not applied — by the
owner's ruling that a material amendment to a committed governing document is a handoff seam
and belongs to the author of the pre-registration, not to the reviewing session.

## What was reviewed, and by whom

| review | brief | verdict |
|---|---|---|
| **Claims against the repo** | every path, function, flag and line number the design's §11 and the plan's self-review cite; three load-bearing mechanisms; Task 3's SQL line-by-line against ListenBrainz's own source on master | **Not executable as written.** Eight findings; `LBDR-F1` and `LBDR-F2` are false premises |
| **Measurement derivation** (`ml-graph-analyst`) | is `LBD-C2` population-independent; is overlap the right shape for `LBD-C1`; what effect size clears rebuild noise; do Task 5's arms separate `LBD-R1` from the rules | **§0's population-independence claim is false**, and the two suggested arms cannot support the conclusion they exist to test |

**The two ran independently and did not see each other's work.** They reached the same
blocker by different routes — one by tracing the mechanism, one by grep while measuring
supply. That convergence is why the blocker below is stated as certain rather than likely.

## The blocker — every arm refuses to build, including the control

`BuilderConfig.drop_unlistenable` defaults `True`, and `pipeline.py` raises
`PopulationNotCensused` for any archive containing artists the `ULF-` census never evaluated.
The census is a frozen roll-call carried **inside** the drop-list payload, so pinning
`unlistenable_list_path` does not bypass it — the loader's own docstring says so. Every
`LBD-` arm's population is far larger than that census by construction, since `LBD-C2`
measures exactly the artists a later crawl extension added.

**Plain sentence:** the builder refuses to run at all, on the do-nothing baseline as much as
on the experimental arms, and it does so at Task 7 — after the full-history run and after
every arm's compute has been spent.

**The fix is one line** — `drop_unlistenable=False` pinned on every arm including the
baseline. Task 6 cites `grt_score.py` as its precedent and copies one line of it while
omitting the three beside it that are the reason that harness runs.

**But the fix falsifies a row of the design's §0 factor table** — "the drop lists … pinned
per invocation to the lists the served map was built with" is a constant the arms cannot
hold. It stays constant *across* arms, so it is not a confound; it is no longer the served
map's filtering, and the pre-registration must say so. **A re-census is not required for
this track**, and this therefore does not touch `ULC-F4`.

## The two findings that would never announce themselves

These matter more than the blocker, because the blocker is loud and these are silent.

1. **Task 3's featured-weight bullet describes a different computation from the SQL it
   quotes.** ListenBrainz's window frame defaults such that the row's own join phrase counts,
   which inverts which artist of a "A feat. B" credit is weighted. Task 2's hand-computed
   synthetic fixture — the sub-check design §6 exists to separate "we implemented it wrong"
   from "the inputs differ" — would be derived from the same prose. So the check passes,
   `LBD-R2` is recorded as retired, and the error is booked at `LBD-C1` as pre-authorised
   lineage gap. **It surfaces never.**

2. **`LBD-C1` does not define "our top-N".** If it means the artist's own half of the pair
   table — which is what ListenBrainz's SQL literally emits — then a *perfect*
   reimplementation scores far below 1.0, and scores worse for well-known artists. If it
   means the union of both halves, there is no large construction ceiling. Figures for both
   readings are in the derivation. **Writing down which reading is meant is worth more than
   any threshold the pre-registration could set.**

## What the measurement changes about the track's premise

> **⚠ FORWARD CORRECTION 2026-09-07 — the MAGNITUDE below is superseded by a direct
> measurement; the MECHANISM is not.** This section's plain sentence was written from a
> supply comparison, before the falsifier the derivation names had been run. It has since
> been run — on the extended archive, and on the `CXA` artifact's own population,
> reproduced exactly — and the split it measures moves the characterisation **from a
> majority to a minority**: our degree ceiling is the **smaller** of the two causes of the
> added set's dead ends, and what ListenBrainz's lists do not supply is the larger. So read
> "mostly ours" below as **"partly ours"**.
>
> Figures are owned by
> [`builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md`](../../../builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md)
> §4 — **cited here, never restated.** This document owns no figures and that is unchanged.
>
> **What is CONFIRMED and must not be softened:** the bilateral-deletion mechanism and its
> `graph.py` citation, and that a meaningful share of the added artists have more than two
> candidates and still end as dead ends — the measurement reproduces that count exactly.
> Only the share attributed to our own rule was overstated, and the arithmetic that shows it
> was already in the derivation; what was wrong was the characterisation drawn from it.
> **The three consequences for the pre-registration below are untouched** and all stand:
> `LBD-C2`'s population dependence, the ceiling as a dormant term, and the two-arm
> insufficiency.


**Plain sentence: the sparsity this track exists to fix is, on today's map, mostly ours
rather than ListenBrainz's.**

ListenBrainz supplies the added artists with materially more candidate connections than the
served map gives them. The gap is almost entirely our own degree ceiling — the rule that no
artist may hold more than fifty connections — which is enforced by deleting the weakest
edges of over-full artists. `graph.py:251-253` does `result[node].pop(victim)` **and**
`result[victim].pop(node)`: the deletion is bilateral, so the connection is taken from the
obscure artist at the other end too. Its own docstring is explicit that the union alone
bounds nothing and that the ceiling deletes whole edges. A meaningful share of the added
artists have more than two candidates and still end as dead ends.

Three consequences the pre-registration must carry:

- **`LBD-C2` is not population-independent.** Same MBIDs, same cap rule, no knob turned: a
  larger population alone moves the supply reading, and in the direction that flatters every
  arm. An arm that merely produces a bigger map will look like it helped. The derivation
  names the cheapest control, and it is free — read supply at the **pair-table level** as
  well as the graph level, and report the pre-existing artists as a within-arm reference.
- **The degree ceiling is a dormant term, not a constant.** §0 lists it as held constant, but
  its *effect* grows in exactly the arms that succeed — the shape §0 was written to catch,
  appearing inside §0 itself. Nothing in `LBD-` should change the ceiling; the point is only
  that the supply criterion cannot be read as though it were inert.
- **Two arms cannot support `LBD-R1`.** Relaxing the neighbour cap alone only helps if the
  new pairs clear the score threshold; lowering the threshold alone only helps if the new
  pairs survive the cap. **Only the corner where both are relaxed can support "the listening
  data is not there"** — which is the conclusion the risk exists to test. This is the same
  shape as the Track 2 stage-2 corner, where the unrun arms produced the only signal.

## There is no rebuild noise

Two artifacts built a month and several commits apart are identical element for element.
Build variance is zero, so the noise floor for `LBD-C2` is the population drift above, not
run-to-run variation. **Median degree cannot be gated on** — it bootstraps to a single value
at this resolution and flips between random halves. Gate on the share of near-dead-ends
instead; the derivation gives the effect sizes and what each rests on.

## What is owed, and by whom

**The owner's, and only this one:** the `LBD-` track asks whether better similarity data
fixes sparse artists, and the measurement says a substantial part of today's sparsity is
attributable to our own ceiling. ⚠ **CORRECTED 2026-09-07:** this read *"most of today's
sparsity"*; the falsifier has since been run and the ceiling is the **minority** cause — see
the forward-correction note above, and §4 of
[`builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md`](../../../builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md),
which owns the figures. **The decision below is unchanged in shape and its inputs have
moved:** the ceiling now has a smaller case for jumping the queue than this section
implied, and the endpoint's own supply a larger one — which is an argument the `LBD-`
track's premise gets to make, not one against it.
**Whether that changes where to spend** — press on with `LBD-`, or let the
ceiling question jump the queue — cannot be settled by arithmetic. It is not a blocker on
anything; nothing here needs a decision before the pre-registration is written.

**Task 2's author, before the pre-registration is committed** (it cannot be amended once
results exist):

- pin `drop_unlistenable=False` on every arm, and rewrite §0's drop-list row to match
- define "our top-N" for `LBD-C1` explicitly, and choose the fidelity sample from the
  **pinned** snapshot — Task 4 pins it correctly, Task 2 does not name a path at all
- add the both-relaxed corner arm, or state plainly that `LBD-R1` is barred from the reads
- gate on the share of near-dead-ends, report median degree without gating on it
- add the free pair-table-level control to the supply criterion
- adopt the derivation's fourteen-item list, which carries the arithmetic behind each

**A session's, before Task 3 runs:** correct Task 3's featured-weight bullet against
ListenBrainz's source rather than the plan's prose, and derive Task 2's synthetic fixture
from the source too — the whole value of that fixture is that it is independent of the
transcription being checked.

**Deliberately not resolved here, each with its condition:** Tasks 3 and 4 carry further
correctness findings (an ordering that is not total, an omitted redirect table, a missing
filter stage) and Task 6/7 carry an uncosted scale risk. All are in
[`claims-review.md`](../../../builder/analysis/2026-09-06-lbd-plan-review/claims-review.md),
`LBDR-F3`–`LBDR-F8`, each with the task it breaks and the point at which it would surface.

| deferral | success condition |
|---|---|
| `LBDR-F3`, `LBDR-F4`, `LBDR-F5` — ordering, the omitted redirect table, the missing filter stage | **Discharged when the task each names is executed** (`LBDR-F4` at Task 1; `LBDR-F3` and `LBDR-F5` at Task 3), by that task's session reading the finding first. Each is a correction to a step, not a decision. |
| `LBDR-F6` — Task 6/7 have no scale budget, and the archive is read into memory whole | **Discharged when `LBD-M1` produces an arm's artist and neighbour counts** — that is the number the budget needs and the track has not run. Until then it is a named risk, not a defect. |
| `LBDR-F7`, `LBDR-F8` — Task 2's unpinned fidelity sample; stale harness counts in two documents | `LBDR-F7` is in Task 2's list above. `LBDR-F8` is **accepted, won't fix** — the counts are inherited from a stale comment in `config.py` and correcting them is out of this track's scope. |
| The isolating pair of builds that would turn the population-drift figure from an order of magnitude into a constant | **Discharged when the pre-registration either commissions it or states in writing that the order of magnitude is sufficient for its gate.** Costed at ~35 min in the derivation's Q1, which also names the exact pair. Cheap enough that deferring it needs a sentence, not a rationale. |
