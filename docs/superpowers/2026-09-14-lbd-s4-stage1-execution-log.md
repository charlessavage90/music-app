# `LBD-S4` stage 1 — retained execution log (`LBA-`)

**Role: ACTIVE — the retained execution log for `LBA-D8` stage 1.** Appended **per task**, as the
work happens, not distilled at closeout. Decisions and reasoning; narration belongs nowhere.

**Governing document:** [`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), read cold and in full including §11's `LBA-AM1` register. **It owns every bar, arm,
threshold and read; where this log and it disagree, it governs and this log is wrong.**

**It owns no figures.** Stage 1's figures are owned by
[`builder/analysis/2026-09-14-lbd-s4-stage1/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage1/README.md)
and are cited from here, never restated.

**Scope, from the owner: STAGE 1 ONLY.** No archive emitted, no graph built, no census run, no
stage 2 begun. The stop is a handoff at the stage-1 seam.

---

## Ordering, and why it is not the order the instruction listed

Two re-orderings were proposed at the scope check and approved before any work began. Both are
methodology — what to measure in what order — and **neither changes an arm, a threshold, a
population rule, a bar or the lattice.**

1. **The `U` population counts come before the two instruments (step 2).** The handoff records the
   `U` population's size as *"genuinely unknown ... the cheapest thing that could change the
   design"*. It is cheaper than the plan assumed: `U` at threshold 10 and `U` at threshold 3 are
   distinct-artist counts over `A0.parquet` and `A5.parquet`, **two files that already exist and are
   sha-pinned** — seconds each, no scan of `T`, no new code. Only threshold 7 needs a derivation.
   Neither instrument in step 2 feeds a gate this stage reads (`framework_rss` → `LBA-G1`(a),
   stage 2/3; peak-RSS instrumentation → `LBA-G2`, stage 2), so answering the design's one named
   unknown first costs nothing and de-risks everything after it.

2. **Step 3 (resolving `LBA-G2`'s first projection from the text) comes before step 2(b).** Step
   2(b) builds the instrument that feeds `LBA-G2`; the resolution determines its shape. Resolving
   the text costs a read and precedes writing the code it justifies.

**A derivation that collapses the union, recorded here because it is load-bearing and checkable.**
A pair kept at threshold 10 is kept at threshold 3: lowering the bar adds only pairs with
`3 < score <= 10`, and `rank()` counts strictly-greater rows, so no added pair displaces a kept one.
Hence **`U`(10) ⊆ `U`(7) ⊆ `U`(3)**, and the union of all nine populations is
**`U`(3) ∪ `V` ∪ `P`** — one set computation, not nine. It is checkable rather than assumed: the
three `U` counts must come out in that order or the derivation is wrong and the work stops.

---

## Task 1 — verify every pinned artifact (`LBA-D9`)

**Script:** `builder/analysis/2026-09-14-lbd-s4-stage1/stage1_verify.py`. **Output:** `verify.json`
(all but `T`) and `verify_T.json` (the full set). Refuses on any mismatch.

**Result: every pin matches.** Thirteen files verified against the sha256s the pre-registration's
§10 and the served-population README's §0/§2/§5 record — the two reused artifacts `LBD-A0V`
(= `LBA-A1`) and `LBD-A5V` (= `LBA-A3`), their two archive `MANIFEST.json`s, the two derived tables
`A0.parquet` and `A5.parquet`, the two graphs `V` and `P` are read from, the two pinned population
files, the three pinned `CXR` strata, and `T`. Figures in the README.

**Three things worth recording beyond the pass/fail.**

1. **Two of the pins exist on the record only as 8-character prefixes** — `population_msw_mbids.txt`
   (`b5e0cb94…`) and `population_cxa_mbids.txt` (`1bbff8fc…`). No committed document carries their
   full 64 hex; the served-population README §0 and the supply README §0 each truncate. A 32-bit
   prefix is a weak assertion of identity on its own, so **each was additionally checked against an
   independently recorded line count** — 58,838 for `V` and 88,685 for `P`, from those same two
   sections — and both match. **The full digests are now recorded in the stage-1 README**, so the
   next session that needs them does not have to repeat this.

2. **`T_A4.parquet` is absent from every path it could plausibly occupy.** §10 pins it *"only to be
   excluded"* (`LBA-D1`: every arm derives from `T`, never from `T_A4`). Its absence is a stronger
   guarantee than a match would have been — no arm can derive from a file that is not there — and it
   is recorded as an observation, not a failure. It is 20.66 GB and was evidently removed after the
   `LBD-A4` read; nothing here needs it.

3. **`LBA-D9`'s "their archives" resolves to the two archive `MANIFEST.json` files**, whose shas are
   in the served-population README §2 rather than in §10's thirteen. Verifying the manifest rather
   than re-hashing the archive trees is what the record supports: the manifest is what
   `build_from_archive` pins and what `build_inputs` names.

**No mismatch, so nothing is refused and the work proceeds.**
