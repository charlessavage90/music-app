# Retained execution log — `DFA-`, the degree floor at admission, and `LBD-AM1`

**Role: RETAINED EXECUTION LOG for the `DFA-` probe and the `LBD-AM1` amendment. ACTIVE.**
**Owns no figures.** The probe's are owned by
[`../../builder/analysis/2026-09-07-degree-floor-at-admission/README.md`](../../builder/analysis/2026-09-07-degree-floor-at-admission/README.md);
the reachability read's by
[`../../builder/analysis/2026-09-07-lbd-am1-residual-reachability/README.md`](../../builder/analysis/2026-09-07-lbd-am1-residual-reachability/README.md);
the ceiling probe's by its own README; Track B's by its results document and `cb_scores.json`.
Every one is cited by section and none is restated here. It states no project status —
[`NEXT.md`](NEXT.md) owns that.

Work ran 2026-09-07; closed out 2026-09-08. Branch `dfa-degree-floor-at-admission`, PR #110.

---

## 1. Decisions, with reasoning

1. **Ran the `DCF-` bridge configuration, not its primary one.** The bridge applies the
   re-censused un-listenable payload through the shipped per-invocation override and so
   reproduces the `CXA` artifact's population exactly. That is what puts every figure on
   `CXR-P2`'s ruler and makes the ceiling-lift comparator legitimate. **Cost, accepted and
   recorded:** `DCF-`'s larger-population primary arms are not reproduced and nothing here is
   comparable to them.

2. **Implemented the variant by rebinding `pipeline.trimmed_union_cap` for the duration of one
   arm**, rather than editing shipped code or reconstructing the post-cap stages in the
   harness. Every other stage of `build_from_archive` is then shipped code at shipped
   defaults. **The alternative considered and rejected** was capturing `adjacency`/`ranking`
   once and re-running the post-cap steps per arm — cheaper, but it would have made the
   component prune and node ordering a reconstruction rather than the builder's own, which is
   the weakest link `DCF-` §5 had to work around.

3. **The far end's degree is read live, at the moment of deletion.** Only that reading
   delivers the guarantee the candidate is named for: no artist above `F` can be carried to or
   below `F`. A frozen pre-trim reading protects only the already-fragile. **This was argued
   before the run and then measured**, and the measurement agreed — recorded so a later reader
   sees the choice was not made by preferring the better number.

4. **Node processing order held at the shipped one**, because holding every other knob at
   default includes holding the order at default.

5. **Ran a set-identity check that nothing asked for.** The sweep found the floor and the
   ceiling lift moving the same *number* of artists out of the dead-end group. Equinumerous is
   not identical, and only identity supports "the floor buys the ceiling lift's benefit". The
   sweep's records held counts, so this needed its own three builds. It is the single most
   load-bearing result of the probe.

6. **Commissioned the `ml-graph-analyst` derivation after the arms were built and before the
   comparison was written.** Deliberate sequencing: the cost side could otherwise have been
   framed first and checked afterwards. It was asked for arithmetic and explicitly not for a
   recommendation, that being outside its remit and the owner's parked decision.

7. **Ran the two follow-ups the derivation named rather than filing them.** Both were reads on
   arms already built, about six minutes. One replaced the derivation's only extrapolation
   with an exact measurement; the other computed the statistic that actually works.

8. **Declined to annotate the `DCF-` README on its own behalf**, then did so when the owner
   asked — as a pointer, with every number in it left as measured and its read explicitly not
   rewritten.

9. **Named the new result branch `R12`, not `LBD-R12`.** §9's series is bare `R1`–`R11` and
   this extends it; `LBD-R1` already names the track's central risk hypothesis, so an
   `LBD-R12` beside it would read as its sibling. Reasoning recorded in §12's register row.

10. **Put `LBD-AM1` on this branch rather than a branch off `main`**, because it pins a sha256
    of a file that exists only here. **Consequence a reader needs:** it reaches `main` when
    PR #110 merges, and until then a session working the `LBD-` track from its own branch will
    not see it.

## 2. Defects found — in the instructions and in my own output, not in the code

- **My instrument gate's red half encoded a prediction about the rule rather than a property
  of the instrument, and the run reported FAIL.** An over-full artist meeting an exempt edge
  deletes its next-weakest non-exempt edge instead of staying over-full, so the ceiling still
  binds at the lower floors. **The original gate block is left exactly as the run wrote it**;
  the correction is a dated addendum beside it. The ceiling holding is a measured result,
  reported as one, not a gate outcome.
- **A docstring of mine described Track B's companion column as a mass scored against a fixed
  set.** It is a set-overlap fraction. Caught by the derivation, then **verified in source
  before acting on it** rather than taken from the report. Corrected in place with the
  correction dated.
- **I conflated two different windows in three places** — the spread between each reported
  value and its upper bound, and the width of the admissible range — and caught it while
  checking my own text against the recorded arithmetic, before committing.
- **The instruction for `LBD-AM1` assumed the identity check's record held artist IDs. It held
  counts only.** The list was produced by re-running that probe's own script with emission
  added; every pre-existing value reproduced exactly. Stated in the amendment rather than
  writing "taken from the committed record" unqualified.
- **The instruction's framing of the residual set was stronger than the probes support** — "no
  rule of ours deleting anything", "no cap-rule change can touch". Both probes held the union
  width constant and kept the drop lists, and that width still deletes a large share of
  candidate edges before the trim runs. Written as "what raising the degree ceiling cannot
  reach", with the narrower scope stated in all three places.

## 3. Gate outcomes, including the failure

| gate | outcome |
|---|---|
| `DFA-` instrument gate, green half — `F=0` reproduces the shipped control build | **PASS** |
| green half — control max degree within the shipped bound | **PASS** |
| **red half as written** — every floored arm exceeds the ceiling | **FAIL.** Wrong as an assertion about all arms; see §2 |
| red half, corrected — more edges than the control and a non-zero restored count | **PASS** on every floored arm |
| identity check re-run — every committed value reproduces | **PASS**, byte-equal apart from the added key |
| reachability harness — three structural checks, each raising rather than reporting | **PASS** (subset, count against the committed record, copy hashes equal) |
| `scripts/docs-lint.sh` | **hard checks passed**; 150 restated-figure candidates, all pre-existing, none from this diff |
| builder suite | **286 passed** |
| api suite | **275 passed**, one pre-existing Starlette deprecation warning |
| frontend suite | **not run** — nothing under `frontend/` changed |

## 4. Corrections to the prior record

1. **`top1pct_degree_mass_frac` is saturation-degenerate.** Where at least 1 % of nodes sit at
   the degree bound it reduces algebraically to the bound over a hundred times mean degree and
   cannot see edge arrangement. **This reaches two existing records:** the `DCF-` README's
   ceiling-50/100/200 arms, which now carry a forward-correction note at its §3 and a bullet
   in its "what is NOT established" list; and Track B's `CRS-C3`.
2. **`CRS-C3` was structurally unable to fire on any selectable cell.** Its reported null is
   arithmetically correct and carried no information about concentration. Track B's results
   document is unedited and carries a forward correction at its head. **Three limits travel
   with that finding everywhere it is written:** it says nothing about `CRS-C4` hub transit, a
   routing measure over built paths; it overturns none of Track B's conclusions, which rest on
   its other criteria and where `C3` was a flag rather than a gate; and it is not evidence
   about any cap rule.
3. **A deferred condition came due and was discharged here.** `docs/README.md`'s row for the
   `LBD-` pre-registration still said the ceiling's effect on the added set was unmeasured.
   `DCF-` measured it. The row now carries the correction by pointer. **The pre-registration's
   own `LBD-X1` is deliberately NOT edited** — that amendment belongs to `LBD-` Task 3, and
   §12 now exists to hold it.

**None of the above must be reverted by a later editor.** In every case the arithmetic was
always right; what was wrong was what it could be read as evidence of, so a future reader will
find no contradiction to resolve and may mistake the notes for noise.

## 5. Operational measurements with no other home

- **Build cost:** the first arm took 9.2 minutes against 0.8 for every subsequent one, on an
  identical configuration. That is a cold page cache over the archive's 117,302 files, not the
  instrument. Budget one cold build per session, not per arm.
- **Total compute:** thirteen in-memory builds across four runs, plus one DuckDB join over
  Task 1's per-artist output. No artifact was written and nothing was serialised.
- **`D6` standing context layer:** unconditional **51,694 characters**, conditional **2,551
  lines**. **Both deltas ZERO** — this branch touched no `CLAUDE.md`, no `.claude/` file, and
  no memory file. Measured against `C:\Users\charl\.claude\projects\C--dev-music-app\memory`.

## 6. Deferred, with conditions

| item | condition |
|---|---|
| The variant cap is a copy of the shipped rule and copies drift | Detected by the `F=0` identity arm, **but only when the probe is re-run**. Discharged if the floor is ever promoted, which removes the copy |
| No concentration cost is established and none is ruled out | Discharged by a measure that is not saturation-degenerate on these arms. The overlap statistic bounds the **identity** of the top-degree set only, not its mass |
| Nothing about routing | Discharged only by building paths and re-measuring `CRS-C4`. Not attempted. **Track B's result stands against any looser bound until then** |
| `LBD-X1` still states the ceiling's effect on the added set is unmeasured | **`LBD-` Task 3's**, per `NEXT.md`. §12 of the pre-registration now exists to hold that amendment, which makes the task smaller |
| Snyk did not scan this session's five new scripts | Covered by the **owner's ruling of 2026-09-07**, which deferred `builder/analysis/` scans on the grounds that none of it is live, with the revisit condition being **promotion into shipped code** — which nothing here proposes. The Snyk MCP server also failed to connect this session, so a scan was not available in any case. Reviewed by hand and reported as such, not as clean |
