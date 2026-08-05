# `CAU-` scoring and write-up — execution log, 2026-08-05

**Role: COMPLETE.** The reasoning behind scoring the coherence audit and writing it up.
**Owns no figures and no status** — figures live in
[`findings/2026-08-05-coherence-audit-results.md`](findings/2026-08-05-coherence-audit-results.md),
status in [`NEXT.md`](NEXT.md). Cited, never restated.

**Session role:** the fresh session required by
[`2026-08-05-HANDOFF-cau-audit-run.md`](2026-08-05-HANDOFF-cau-audit-run.md) — it did not
design, build or run the audit, so scoring it is not marking its own work.

---

## 1. ✅ The build-and-run chunk's log was written by that session, not backfilled here

**Superseded 2026-08-05 (later), and the way it was closed is the reusable part.** This
section originally recorded the missing log as a permanent gap: `GBL-` produced four execution
logs and `CAU-` produced none, and backfilling it from another session's commits would have
produced something that reads like a record and is actually a guess.

**The owner then pointed out that the session which did the work was still live.** That
dissolves the problem entirely — `closeout` A1 sits in Part A precisely because the context
dies with the session, and it had not died. It wrote its own log:
[`2026-08-05-cau-audit-build-and-run-execution-log.md`](2026-08-05-cau-audit-build-and-run-execution-log.md),
committed `d4f7f85`. Primary source, not reconstruction.

**It was asked under a read bar, and that bar is the transferable bit.** It wrote from its own
memory and its own commits, having read none of: the findings note, `cau_result.json`, the
sealed note, this log, the current handoff, `NEXT.md`'s top block, **or any commit message
after `adafde1`** — the last of those being the real hazard, since `git log` is a session's
first move and the intervening messages state the outcome outright. Knowing what a design
choice produced reshapes the recollection of why it was made; the bar is the sealed-note
problem running in the other direction.

**It returned things nothing else would have.** Eleven defects where the handoff listed five,
seven owner statements that never reached a file, and a gate that was **never reached** —
none of which is derivable from the commits. Three of its items corrected documents this
session had already written; see §6.

**The general lesson, and it cost nothing to learn:** *"the session that did the work is gone"*
is an assumption worth testing before accepting any gap it implies.

## 2. Decisions taken

**2.1 Ran the scorer before reading the pre-registration.** The handoff's command block puts
it first and the reading order second. Followed as written: the scorer is figures-only and
enforces its own gates, so there is no path by which reading it first shapes a bar.

**2.2 Verified one load-bearing claim before building on the handoff** (`session-start`'s
third check). The handoff asserts the scorer evaluates `CAU-G1` first and alone and excludes
control-adjacent slots. Checked at `cau_score.py:57-60` (early return, `readings: null`) and
`:66-68` (the scored pool derived by exclusion, not hard-coded). Claim held. **`D_all = 53` is
computed, not asserted** — which matters, because a hard-coded 53 would have been
indistinguishable in the output and impossible to falsify from the result file.

**2.3 Reported `CAU-C3`'s pre-registered reading as it stands, and disagreed with it in the
same breath.** The trigger fired and the pre-registration attaches a specific meaning to that
("unfamiliarity, not clip length, was the barrier; the §0 diagnosis is wrong"). The free-text
notes say something the document's binary did not anticipate: eight of the nine can't-tells
record that there was **nothing to listen to**.

The options were to report the pre-registered reading as satisfied, to discard it, or to
report it and argue against it. **Took the third.** A pre-registration's value is that its
reads cannot be reshaped by results; deleting one because the result is inconvenient destroys
exactly that, and endorsing a reading the evidence contradicts is worse. Naming it as a defect
in that read — an unanticipated third cause — leaves both on the record for a later reader to
weigh.

**2.4 Declined to split the 53 slots by depth.** The owner observed, after reading the
analysis, that the `GBL-` depths were chosen against the production graph and may be wrong for
a graph that reaches novelty faster. **A depth split would have been two new denominators
chosen after seeing a directional claim** — precisely what §5 forbids and what the handoff
bars ("never invent a criterion to accommodate it"). The number would have taken a minute to
produce. Recorded here because a later session will find the split obviously computable and
should know it was considered and refused.

**2.5 Committed the analysis before opening the sealed note, and appended the response rather
than revising above it.** The handoff's ordering. The commit boundary (`184b3ac`, then
`4bdc583`) is the evidence. **The convergence this bought is the chunk's most valuable single
outcome** — see §3.

**2.6 Wrote the filter addendum as a new section rather than editing §2.2.** The owner
corrected a framing in §2.2 (the point of the app is finding coherent novel artists, not
playing a clip). Editing it in place would have broken the "nothing above §5 was revised"
guarantee for a cosmetic gain. Recorded in the addendum instead.

## 3. What the commit boundary bought, stated because it is the reusable part

The independent read and the owner's sealed note reached **the same mechanism, and named the
same worked artist** (Rick Davies) without either having seen the other. Had the note been
read first, this would have been his hypothesis with a session's agreement attached — worth
very little, and indistinguishable from the failure the seal exists to prevent.

**The procedure that produced it is cheap and should be reused wherever the owner has a strong
prior:** he writes his view, it is committed unread, the analysis is committed, then the seal
opens. The cost is one extra commit.

## 4. Defects found

**4.1 In the documentation, by `scripts/docs-lint.sh`** — five hard failures, all fixed here:
two `GBL-` execution logs carried a "Session role" line but no document **role marker**
(`docs/README.md` had classified both correctly all along, so this was a marker defect, not a
classification one); and three documents were missing from the doc map entirely — the `CAU-`
pre-registration, the `CAU-` run handoff, and this chunk's findings note. **The map went stale
across the whole `CAU-` track**, not just this session's output.

**4.2 In the builder's filter coverage, found by answering an owner question** — see the
findings note's §6. Not a defect in this chunk's work; a pre-existing gap the audit surfaced.
`drop_no_release_tail` fires only at zero release-group credits and `drop_featured_credit`
only when none are sole, so **a single sole credit exempts an artist from both.** Checked
against both committed `ALG-B` lists: 22 of the 23 artists behind a can't-tell or doesn't-fit
verdict were never in either class. **No fix attempted** — it needs a census and a rule, which
is a track, not a closeout item.

**4.3 A `BYP-13` exposure inside the featured-credit keep-check**, disclosed by the census that
built it and never acted on: keeps are name-path clip resolutions, unfiltered by that census's
own wrong-artist check, and about half of all keeps had no recorded id to check against.
Figures in `fcf_clips.json` / `fcf_clips_am1.json`, which own them. Separable from 4.2 and not
what admitted the artists in 4.2.

## 5. Gate outcomes

| Gate | Outcome |
|---|---|
| `CAU-G1` — can the audit tell a bad recommendation from a good one | **PASS**, and the readings below it are therefore not void |
| Run-state precondition (all 77 judgements present) | **Met**; the scorer refuses a partial run and did not have to |
| `CAU-C1` / `CAU-C2` / `CAU-C3` | Computed; the findings note owns the branches |

**Never reached:** nothing. **Failed and worked around:** nothing.

## 6. Corrections to the prior record

- **`NEXT.md`'s "after scoring" instruction is discharged** — `cau_page_data.json` is
  committed and out of `.gitignore` (`551ed0e`). Struck in place, not deleted.
- **The `GBL-` null stands untouched**, which is the one thing most at risk of being read
  otherwise. Nothing in either chunk overturns it.

**Three corrections came from the build-and-run log (`d4f7f85`) after this session's closeout
had already run, and all three were this session's errors:**

1. **"Never reached: none" was wrong.** The PR body and the gate table said no gate went
   unreached. The **browser render check was never reached** — the Chrome extension was not
   connected, and the build session fell back to `node --check` plus a live endpoint exercise.
   It is also the clearest instrument lesson in the track: a render check is exactly what would
   have caught the one-interior journey that reads to a listener as a rendering failure, which
   the owner instead hit mid-run. Corrected in the PR body.
2. **"No Snyk scan is owed" was right for this chunk and wrong for the branch.** The build
   session added first-party code, scanned it, found **one MEDIUM, adjudicated it a false
   positive** (a dict key literally named `"pass"`), resolved it by renaming the `CAU-C1`
   branches to `meets_bar` / `ambiguous` / `below_bar`, and **rescanned clean**. So the
   branch's Snyk obligation is discharged — but by that session, not by nothing. Corrected in
   the PR body.
3. **`CAU-G1` carries a third weakening, not two.** This session's weakest-link section named
   `CAU-AM1` and `CAU-AM4` as interacting to soften the red control. The build log §5 records a
   third, never written down before: **endpoint-adjacent placement puts each control beside an
   endpoint the owner chose himself and therefore always knows**, so it can be rejected in
   fully familiar context without a lookup. **All three weakenings point the same way.**
   Recorded as findings §7 rather than edited into §3, per that document's revision boundary.

**One correction owed to a document outside this track.** The build log §3.1 records the owner
confirming in conversation that he scored the `GBL-` rows on coherence — *"whether I meant to
or not, that's how I ended up scoring the rows."* The `GBL-` findings note carries that as **a
session's inference from his written notes**; his confirmation upgrades it to a stated fact and
was nowhere in the record. A dated cross-reference has been added there. **No `GBL-` figure,
branch or verdict moves** — the null stands and its run-once rule is untouched.

## 7. Operational notes

- The scorer runs in about a second and needs no artifact, no network and no graph — it reads
  three committed JSONs. A future session can re-run it freely; it is deterministic.
- No dev server was started, no port was bound, no artifact was built or loaded.
- **Standing context layer: unconditional 44,729 characters, conditional 2,183 lines.**
  **Delta 0 on both units** — identical to the figures the `GBL-` harness log §7 recorded, so
  nothing has moved the layer since. No `CLAUDE.md`, skill, agent or memory file was touched
  here. The `NEXT.md` parked-idea addition is in neither layer: `CLAUDE.md` points at `NEXT.md`
  and does not inline it, which is exactly why that row is a pointer.
- **Test suites, D4, all green and run rather than remembered:** builder 164, api 230,
  frontend 107, `CAU-` harness 33.
- **B3 mutation check on this chunk's highest-stakes invariant.** Forcing `CAU-G1` to always
  pass turned `test_g1_failure_voids_everything_and_computes_no_readings` red; removing the
  `CAU-AM3` control-adjacent exclusion turned two `AM3` tests red. Both restored, suite green,
  file byte-identical to HEAD. **The void gate and the 53-slot denominator are genuinely
  tested** — which matters more than usual here, because the previous session's own log records
  a `CAU-` test that passed while testing nothing.
