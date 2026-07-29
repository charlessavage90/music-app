# Track 3b — the thresholded toll: execution log

**Role: RETAINED EXECUTION LOG for Track 3b.** Appended per task, not only at closeout.
Governing document:
[`specs/2026-07-29-track3b-thresholded-toll-preregistration.md`](specs/2026-07-29-track3b-thresholded-toll-preregistration.md)
— where this log and it disagree about design, **it wins**; where they disagree about
what was *run*, this log wins.

**Owns no figures that belong elsewhere.** Track 3b's measurements are owned by
`builder/analysis/2026-07-29-track3b-thresholded-toll/` and cited from here. The TB-P1
review's figures are owned by its report in that directory.

Discharge order (prereg §5, as amended): **TB-P1 → TB-P2a → TB-P3 → TB-P4 → arms →
TB-P2b → TB-P5 → read.** Artifact throughout: `graph-t15-tiebreakfix.bin`, sha256
`4cb84ef9…b061dc8`.

---

## §1 — TB-P1: analyst protocol review. DISCHARGED, and the pre-registration is amended.

Dispatched 2026-07-29 on the owner's explicit word (Track 3 precedent). Report:
`builder/analysis/2026-07-29-track3b-thresholded-toll/TB-P1-protocol-review.md`; probes
`tb_p1_probe_dose.py`, `tb_p1_probe_ceiling.py`, `tb_p1_probe_dormant.py` (Snyk clean, 0
issues). Derivation only, per its remit.

**Outcome: 15 findings — 4 HIGH, 4 MED, 1 MED–LOW, 6 LOW — and 23 claims verified
clean.** Every finding is amended into the pre-registration, marked in place with its
finding ID; the prereg's **§9** is the amendment index. All amendments were adopted
**before any harness code existed and before any arm ran**, which is what running the
review first was for — and the review's own headline items (F1, F2, F4) were derivable
from the document plus the artifact with no arms, confirming the Track 3 closeout lesson
that motivated the reordering.

**The four HIGH findings, one sentence each:**

1. **F1** — the dose derivation's premise (median interior pctl ≈ 0.998) was a Track 2
   pair-set figure; on this track's own pairs it is 0.9810, the realised ladder is
   ≈4×/13×/43× not 5×/15×/50×, and the per-interior price is dispersed 8× where Track
   3's was near-uniform. Ladder retained: it brackets the per-cell crossover dose.
2. **F2** — TB-P3(b)'s forecast was answerable before any arm: **this device's own
   ceiling also shortens** (mean interior count 6.52 vs P's 13.35, −6.83 paired), so by
   the prereg's own sentence **TB-R2 is the likely outcome**; the length confound is
   halved versus Track 3 (median length share 0.500 vs 0.807), not removed.
3. **F3** — TB-R3's "no dose can beat the limit" inference was invalid (the ceiling
   bounds toll, TB-C1 scores fame, and the pctl→fame map is DD-D6's non-monotone one);
   restated as strong pre-committed evidence, not proof.
4. **F4** — §0 had missed the one term this device genuinely wakes: **0/252 of
   production's bypass victims are sub-decile**, so the baseline never excludes a node
   the device wants, while a descending arm draws victims from — and progressively
   exhausts — the 4–9-interior sub-decile routes it depends on; now a §0 row and a
   per-arm counter.

**Verification by this session, not taken on report:** F4's 0/252 was re-verified by an
independent re-run of `tb_p1_probe_dormant.py` — byte-identical output, including the
LIMIT-vs-ceiling comparison and the TB-P2 fetch sizing (78 distinct ceiling interiors /
48 covered / 30 new / 0 blank-named). F2's figures were checked for internal consistency
against `tb_p1_ceiling.json`; the remaining findings were adopted on the review plus
spot-reading, and TB-P5 (the harness review) remains the second independent instrument
before any verdict.

**What TB-P1 changes about expectations, stated plainly so no later summary can soften
it:** the pre-run forecast now on record says the likeliest end state of this track is
**TB-R2 — the router still shortens even when obscure artists are free** — with the
mechanism question answered *negatively* for the toll family. That is a designed outcome
with a pre-committed reading, not a failure of the track; the run is cheap and proceeds.

## §2 — TB-P2a and TB-P3: the ceiling gate. DISCHARGED — GATE PASSES.

**TB-P2a.** `tb_p3_ceiling.py --emit` recomputed the ceiling paths, **asserting all 35
cells reproduce the review's committed `tb_p1_ceiling.json` stats exactly** (interior
count and median pctl exact, base cost to 1e-9) — the review's figures and this track's
instrument now corroborate each other. Fame fetched for the ceiling's new interiors via
the committed A11 instrument, name cache shared (`tb_ceiling_fame.json`). TB-G4's
blank-name assertion: **PASS** over every scored interior.

**TB-P3(a) — GATE PASSES: −2.554 against −1.0** (mean over 23 analysis C1-window cells
of the ceiling-vs-P mean-interior-fame gap; cell-median variant −2.889; 18/23 cells
clear individually; figures owned by `tb_p3_gate.json`). **The arms run.**

**Two reads worth carrying, neither a criterion.** (1) TB-P1 F3 warned the pctl→fame map
might not deliver: it did — the base-cost-tie-break ceiling reaches −2.55, nearly DD-D6's
obscurity-extreme LIMIT (−2.73), so the fame-currency risk did not materialise on this
pair set. (2) One pair (`Patti Smith → Daniel Herskedal`) has thin fame headroom
(−0.30 to −0.46 per cell) and one (`Openzone Bar → Gjallarhorn`) is marginal — 5 of the
23 cells cannot individually clear −1.0 even at the limit, so a per-cell read of any arm
must not treat those cells as failures of the device. **15 ceiling interiors carry the
A11 potentially-notable flag** — the TB scorer reads the flag (TB-G4) and TB-C1(i)'s
counterfactual will bound them if arms pass.

**Next: TB-P4** — the device into the mirror, TB-G1/TB-G2 re-earned, runner and scorer,
then the arms.
