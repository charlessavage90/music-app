# Execution log — `DRP-` stage 3d, the results note (#200)

**Role: ACTIVE — the retained execution log for stage 3d** of
[`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8. Appended per task. It owns no status (`NEXT.md` does) and restates no figure the
committed outputs own: each entry points at its output file.

**Governs:** the pre-registration's body (execute-from-body since `DRP-AM5`). **Starts from:** the
stage-3c log's "Seam C" entry ([`2026-09-28-drp-stage3c-execution-log.md`](2026-09-28-drp-stage3c-execution-log.md))
and handoff [`2026-09-28-HANDOFF-drp-stage3c.md`](2026-09-28-HANDOFF-drp-stage3c.md). **Scope, the
owner's words, 2026-09-28:** *"you are picking up next steps on DRP"*.

**§8's condition on who writes 3d:** a session that ran no sweep. This session ran none of 3a, 3b or
3c, and read no sweep session's prose about results (there is none: both READMEs and the Seam C entry
state that no result was read).

---

## Orientation. 2026-09-28

- Tree clean at `acff906` (= `origin/main`), branch `charlessavage90/drp-stage-3d` created by Orca for
  this session. The main tree is on `main`, clean; no other live session found.
- **Cell-file identity checked against the committed blobs, not the working copy.** With
  `core.autocrlf=true` the checked-out cell JSON hashes differently from the committed LF files; every
  committed blob (`git show HEAD:<path> | sha256sum`) equals the sha the stage-3b/3c READMEs pin. The
  reader below normalises CRLF to LF before hashing, and refuses on any mismatch.
- **One handoff claim did not hold.** The stage-3c handoff says 3d "needs neither graph artifact, only
  the committed JSON". The cell files hold journeys as node ids and carry no fame values, so every
  criterion that reads `fame_lb_pctl` needs lba-a6's frame, and `DRP-C5`'s added-edge split needs the
  added-edge set. The reader loads **both artifacts read-only** (sha-verified against sidecar and pin,
  as every earlier stage did) and routes nothing. Not a defect in any result; a gap in the handoff.
- **`drp_c10_frontier.json`'s `cell_file_sha256` records the working-copy (CRLF) shas**, not the
  committed LF shas the READMEs pin. The content is identical; the reader re-derives nothing from
  that field and checks cell identity itself.
- **Stage 3b's relaxation-search departure (`DRP-AM3` item 4), weighed as the Seam C entry asks.**
  Accepted. Admission of an interior-bearing journey is monotone in the ceiling (raising `c` only
  removes exclusions), so a candidate that admits a journey while the next-lower distinct percentile
  admits none is exactly the bisection's answer; both sides were certified by the shipped
  `find_journey` and re-routed by the gate script; no press fell back to bisection. What is lost is
  that (d) is no longer two independent searches meeting at one number. That weakens (d) as an
  independent check of `DRP-C11`'s minimax search; it does not change any `c`, `r` or journey. No
  read below depends on (d) beyond the ceiling cells being readable at all.

## Task 1 — choices left to 3d, fixed before any result is computed. 2026-09-28

**Committed before the reader runs**, so the commit timestamp is the evidence that each choice
preceded every figure. Where the body is explicit it governs and nothing here overrides it; each item
below is a place where it is silent or leaves the choice to 3d by name.

1. **§4's cross-cell drop set** = the union over all eight cells of `dropped_in_this_cell`, per
   press rule. The reader also recomputes infeasibility from each cell's depths (journey `None`, no
   interior, or the ladder stopped) and **refuses** if the two disagree.
2. **`DRP-C10`'s frontier count for §2.4's deferral condition: `incident_all`** (endpoints included).
   Reason: §5's statistic is "added edges within one hop of the band journeys' nodes", and a journey's
   endpoints are its nodes; an added exit at a famous endpoint that the route does not take is exactly
   "an exit that exists and is being priced away", which is what §2.4's condition infers. The
   `incident_interior` count is reported beside it, and the note says whether choosing it would change
   the read. **Read on `DRP-S1P0`, primary rule** (the extra exits at today's pull: the cell whose
   exits a jump relaxation would act on), over the band-readable pairs of **both famous strata pooled**
   ("the famous pairs"), each stratum reported beside. A pair "has added exits" if its count is ≥ 1.
   The other three `DRP-S1` cells are reported, not read.
3. **`M`** (§5) reads the shipped `fame_lb_pctl` of **measured** interiors only (§3: nulls are excluded
   from the median and counted by `DRP-C4`), pooled over interior slots of the depths named.
4. **Per-depth statistics outside the band** (`DRP-C1s` at press 20, the `DRP-R8` profile, `DRP-C3`'s
   20 band, `DRP-C12`) use, at each depth, the pairs whose (pair, depth) survives the drop set — and
   depth 0 as well wherever the statistic subtracts depth 0. Their `n` is reported.
5. **`DRP-C8`'s qualifier `DRP-R9`(ii)** fires if `DRP-C8`'s median `D` has the opposite strict sign to
   the primary median `D` of **either** famous stratum in the same cell. A zero has no sign.
6. **The floor-attribution flag (§2.7)** is computed per famous stratum over that stratum's
   band-readable pairs, primary rule; "fires on the chosen path" = the recomputed `floor` term > 0 at
   any press 1–6. It flags a cell if **either** stratum crosses 10 points against **any** listed
   baseline.
7. **`DRP-R9`(v)** — "past `CRE-`'s dominating-regime figures". **Operationalised as: the band's
   median realised `w_sim·(1−sim)` on chosen edges ≥ the figure CRE critique F7 records at ramp 0.10**,
   the only measured setting F7 places in the dominating regime (0.01 and 0.03 are the ones `CRE-` kept).
   Pooled chosen edges over the band depths, band-readable famous pairs, primary rule. Each cell's
   figure is also placed against F7's 0.03 figure. Stated as a choice: F7's figures are over presses
   10–20 on another map whose similarity scores lba-a6 replaced (§2.4), so the comparison is a flag's
   yardstick and nothing more.
8. **`DRP-C3`'s top-1 %-by-degree set** = the shipped `evaluation.top_degree_node_set(store, 0.01)` on
   lba-a6; "the cell's own" = the same function on the cell's map.
9. **`DRP-C5` on `DRP-MID`** ("does the first path still climb above both endpoints?"): the share of
   pairs whose press-0 highest interior `fame_lb_pctl` exceeds both endpoints', and, beside it, the
   share whose `M(0)` does.
10. **`DRP-C11`'s fraction of headroom**: `X` uses the shipped `fame_lb_pctl` with nulls at 0.0
    (`DRP-AM5-O2`), per band depth the highest interior, then the median over the four band depths.
11. **Outcome precedence (§7)**: UNREADABLE (`DRP-G8`) → ELIMINATES (`DRP-C6` fires, "whatever else
    holds") → if `DRP-C1` passes, MOVES or DELETION by `DRP-C2` (in the `DRP-P3` cells, DELETION also
    if any band depth's per-depth ratio is < 0.70) → otherwise RISES / BELOW BAR / NO MOVEMENT by the
    median `D`, which are exhaustive once `DRP-C1` has failed.
12. **`DRP-SW`'s trigger** reads the primary-rule press-0 journeys; the reader asserts the random
    rule's press-0 journeys are identical (no press has happened yet).
13. **Leave-one-out range** (`DRP-C1` item 4): the minimum and maximum of the median `D` over the `n`
    subsets that drop one band-readable pair.

## Task 2 — the reader. 2026-09-28

- `builder/analysis/2026-09-28-drp-stage3d/drp_read.py`, committed with its output `drp_results.json`
  at `0b80dab`, **before the results note was opened**. It routes nothing. Every input is
  identity-checked (folder README), and it refuses on any mismatch; none fired.
- **The drop set** (task 1, choice 1) matched a recomputation from the journeys in all eight cells.
- **Second-path check:** one MOVES row's median `D` and its count past −0.05 were recomputed by
  separate code from the raw JSON and the `GraphStore`, and agree exactly. **The floor-attribution
  flag reads zero everywhere**, which looked like a possible bug and is not: across five cells and
  33,542 journeys the floor term fires on 200, all of them first paths (press 0), none at presses 1–6.
- Snyk code scan on the folder: 0 issues.
- **No choice from task 1 turned out to decide a read.** Choice 2 (which frontier count): §2.4's
  condition needs `DRP-R0`, which did not fire, and both counts are 100 % anyway. Choice 7 (the
  `DRP-R9`(v) yardstick): every cell sits below both F7 figures. Choice 5 (`DRP-C8`'s sign): the
  signs agree everywhere.

## Task 3 — the results note. 2026-09-28

- [`findings/2026-09-28-drp-lattice-results.md`](findings/2026-09-28-drp-lattice-results.md), in
  `CLAUDE.md`'s four parts. It owns the reading and names no candidate (`DRP-R10`). Every figure in
  it was checked against `drp_results.json` after drafting; six phrasings were corrected where the
  plain sentence had drifted from the number (for example "a third less famous" for a
  thirty-three-point drop).
- **`DRP-R11` does not fire**, so #246's Done-when ("or the trigger does not fire") is met. The PR
  closes it with the reading. **#249's first condition has come due** (a ceiling cell MOVES); its
  second is the owner's at stage 4. A comment on #249 says so.

## Seam D — reached 2026-09-28

Stage 3 is finished. **Next is stage 4, the owner's go/no-go on at most one cell** (§8), with the
results note in hand. Nothing is in flight: no process of this session survives, and no server was
started.

## Closeout at Seam D. 2026-09-28

- A1/A2/A2-next: this log, the handoff, and `NEXT.md`'s top block; the outgoing block was demoted to
  `NEXT-ARCHIVE.md` (nothing in it still bound except the ordered actions and carried items, both
  kept). The stage-3c handoff's role line points forward.
- **A3:** #246's Done-when is met (trigger did not fire); the PR closes it. **#247 closed as not
  planned**: its condition required `DRP-R0` to fire on the complete lattice, and it did not, so it is
  known-unreachable, not deferred. #249: its first condition came due; its second is the owner's
  (comment posted). A4: no config knob. A5: no listener on 8000 or 5173; no process survives.
- **B1:** `docs-lint` hard checks passed (its only candidates in this diff are ramp settings, not
  figures). The `doc-auditor`, scoped to the diff, checked figures against `drp_results.json`,
  identifiers and barred reads, the handoff chain, `NEXT.md`, sealing and completeness: **no defects.**
  The #247 closure landed after it ran and was folded into the note and handoff here.
- B2: `drp_read.py` is an entry point. **B3:** both of the reader's refusal guards shown to go red (a
  wrong pinned cell sha; a dropped list disagreeing with the journeys). B4: docstrings checked against
  the code. B5: no `.claude/` file mentions `DRP-`; the only stale "3d is next" lines are in the two
  superseded handoffs. **B6:** `NEXT.md` 349 lines (budget 250) and `docs/README.md` 641 (budget 400),
  both over before this work (#145). This work added four map rows and one net line to `NEXT.md`.
- C1: nothing the owner can press, so no `TEST-QUEUE.md` entry. D2: no fixture changed. D3: no
  artifact adopted or built; both maps' shas are verified in the reader's run log. D4: builder 292
  passed, api 347 passed; frontend untouched. D6: no standing-layer file in the diff, delta 0.
