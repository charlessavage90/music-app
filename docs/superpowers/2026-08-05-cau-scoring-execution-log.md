# `CAU-` scoring and write-up — execution log, 2026-08-05

**Role: COMPLETE.** The reasoning behind scoring the coherence audit and writing it up.
**Owns no figures and no status** — figures live in
[`findings/2026-08-05-coherence-audit-results.md`](findings/2026-08-05-coherence-audit-results.md),
status in [`NEXT.md`](NEXT.md). Cited, never restated.

**Session role:** the fresh session required by
[`2026-08-05-HANDOFF-cau-audit-run.md`](2026-08-05-HANDOFF-cau-audit-run.md) — it did not
design, build or run the audit, so scoring it is not marking its own work.

---

## 1. ⚠ The build-and-run chunk left no retained execution log

**This is a gap in the record, not an omission of this log's.** `GBL-` produced four
execution logs (planning, harness, run, write-up). `CAU-` produced none: the audit was
designed, built, gated, served and judged, and the only durable reasoning is the handoff's
"Defects found during this chunk" section, the four `CAU-AM` amendments, `CAU-CORR1`, and the
commit messages.

**Not backfilled here, deliberately.** Reconstructing another session's reasoning from its
commits produces something that reads like a record and is actually a guess — the exact
failure mode `CLAUDE.md` names as "confident prose about correct code". The four amendments
happen to carry unusually good reasoning inline, which is why the loss is smaller than it
would normally be, and that is luck rather than design.

**What is genuinely unrecoverable:** what was decided *against* while designing the audit,
and any figure computed and not written down. Both are the categories `closeout` A2-mid
exists to enumerate, and no mid-flight retirement occurred to trigger it.

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
- **No previously-recorded claim was overturned by this chunk.** The `GBL-` null stands
  untouched, which is the one thing most at risk of being read otherwise.

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
