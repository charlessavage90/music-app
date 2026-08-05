# Handoff — the un-listenable class (`ULC-`) is measured and written up, 2026-08-05

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-05-HANDOFF-cau-scoring.md`](2026-08-05-HANDOFF-cau-scoring.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam handoff.** The track ran to its end, the findings note is committed, nothing is in
flight, tree clean, no listener on any port.

**Branch** `unlistenable-class-prereg`, draft PR #78. **The owner has set the next session's
remit: the filter work.**

---

## What is done

`ULC-` is complete. Results of record:
[`findings/2026-08-05-unlistenable-class-results.md`](findings/2026-08-05-unlistenable-class-results.md)
— **it owns the `ULC-` figures**; cite by section, never restate. Reasoning:
[`2026-08-05-ulc-execution-log.md`](2026-08-05-ulc-execution-log.md). Governing document:
[`specs/2026-08-05-unlistenable-class-preregistration.md`](specs/2026-08-05-unlistenable-class-preregistration.md)
(five amendments, each committed before the stage it affects).

## Which documents are now wrong, and in which direction

- **`findings/2026-08-05-coherence-audit-results.md` §6 — CORRECTED, and the correction is now
  IN that note.** Its "22 of 23 never evaluated" counted the audit's own 12 planted controls in the
  denominator; the real figure is 10 of 11, its conclusion is unaffected, and no `CAU-` criterion
  is touched. A callout sits at the head of §6 pointing at `ULC-AM0`; **§6's original text is left
  standing beneath it, unedited**, because it is the record of what was claimed. **Do not "tidy"
  that by editing the numbers in place.**

  > *This session first declined to make that edit, on the grounds that the `CAU-` note owns its
  > own figures. That was the wrong reason — `closeout` B1 is explicit that a finding you have the
  > facts to fix is yours to fix, and authority is never grounds to escalate. The documentation
  > audit caught it: a reader standing in the `CAU-` note had no way to know the figure was
  > disputed. Recorded because the instinct was to be deferential and the effect was to leave a
  > known-wrong figure reading as settled.*
- **Nothing else is stale in the direction of overstating.** `NEXT.md` and `docs/README.md` are
  updated.

## Claims that must NOT be reverted by a well-meaning editor

1. **`ULC-R1` did not fire and no branch is assigned.** Do not "finish" it by swapping the median
   for the mean. The statistic could not see this effect, that is recorded as a design defect
   (results §1.3c), and changing it after seeing which statistic gives the interesting answer is
   the fishing the whole design exists to prevent. **A re-read needs a new pre-registration.**
2. **The looser reading of prereg §4 stays declined** — yes, `A4`−`A3` is complete; adopting that
   reading now means adopting it after seeing which comparison it rescues.
3. **`ULC-V1` is 6, not 7.** Four Tet's can't-tell is an identity doubt, not an availability one
   (`ULC-AM4`). Do not restore him to the target set.
4. **The gate bar is 5 of 6, not 5 of 7 rescaled.** Holding the absolute count was deliberate.
5. **The count and the exposure disagree, and both stay.** A similar share of both maps, but zero
   exposure on production data and substantial exposure on the candidate (§1.2, §1.3). Do not resolve the tension by
   dropping either — that disagreement *is* the finding.
6. **`ULC-P5` never appears in a cross-archive sentence** (`ULC-B4`). Its rate (§1.2) is high because it carries
   neither drop flag, and for no other reason.
7. **Nothing is adopted, no default changed, no shipped code touched.**

## What has already been updated — do not re-edit

- `NEXT.md` — rewritten; carries the owner's revised ordering and his tabling of the
  production-data rebuild.
- `docs/README.md` — four `ULC-` rows added (prereg, findings, log, this handoff).
- The previous handoff's role line now names this one as its successor.

## What I know that is not in the durable record

**Two things, both judgement rather than fact.**

1. **The filter gap is more actionable than the exposure measurement**, and the results note
   presents them side by side. If the next session can only do one thing, it is the filter.
2. **I would not spend a fresh pre-registration on re-reading `ULC-R1`.** The direction is stark
   enough to act on and a licensed branch changes nothing anyone would do. That is in results §4C
   as a recommendation, but the strength of it would not survive a summary.

**Nothing else.** No figure was computed and left unwritten; no option was entertained and dropped
without being logged in the execution log §7.

## Owed, and by whom — the next session's remit

**The owner has set it: the filter work.** From results §5, and the first two are the same
session's job:

- **`ULC-F1` — drop-list keys must carry population identity, not just algorithm.** Do it while
  re-censusing, or a third census is needed later. **Blocks any crawl extension.**
- **`ULC-F2` — the census must write back what it learns**, so each expansion pays only for new
  artists.
- **The filter fix itself**, and note that the obvious version is insufficient: requiring a *sole*
  Discogs credit still would not catch Joey Kramer's drum sample library.
- **Re-censusing both drop lists** follows any rule change — roughly an hour of dump passes.

**Also open and NOT this session's:** `ULC-F3` (crawl resume cannot extend — blocks expansion,
independent of filters) and `ULC-F4` (the `BYP-13` keep-check defect, deferred by the owner to its
own track).

## Decisions the owner has taken that constrain the next sessions

- **The production-data rebuild is TABLED** — he wants to try the candidate map live first, rather
  than change two things. **Consequence he accepted knowingly:** the next live deployment carries
  three changes at once (data, both filters applied for the first time, Deezer ids), so it cannot
  isolate which one moved his experience.
- **Ordering:** write-up → filters → map switch. **No re-crawl is needed for any of it** — the
  candidate archive and a built graph are already on disk.
- **"Switch to the new map" is not yet pinned down** to data-only or the full listened-to package;
  results §4.1 sets out both and their very different costs, and neither has a listen behind it.
