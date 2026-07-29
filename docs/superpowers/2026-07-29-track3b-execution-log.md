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

## §3 — TB-P4 and the arms. RUN COMPLETE, SCORED. ⚠ NO VERDICT IS READ IN THIS SECTION.

**This section states measurements only. The pre-registration orders TB-P5 (the harness
review) before any verdict is read; TB-P5 has not yet reported as of this section, so any
sentence here that looks like a verdict is provisional and is superseded by §4.**

**Harness.** `mirror.py` gained `w_known_thresh_pctl` (live-only, edge-relaxation target,
target exempt, knee constant `KNOWN_THRESH_PCTL_KNEE = 0.90`). **TB-G1 re-earned:
212/212 cells byte-identical** with the device off. Snyk clean (0 issues) on all new
scripts. Runner and scorer are new modules importing committed code; no committed Track
2/3 file changed except `mirror.py`'s additive term.

**The run.** 4 arms × 16 pairs × 21 depths, ~9 minutes. **TB-G2 PASS** (d0 identical to
P on all 16 pairs, every arm) **with non-vacuity held** (d1 differs from P on 11–12
pairs per arm). **Zero A13 drops** — unlike Track 3, no cell went guard-infeasible, so
all 24 C1-window analysis cells score. Guard G fired 42 times in every arm including P —
the same two unscored adjacent anchors as Track 3; no scored-pair activation.

**Scores (figures owned by `tb_scores.json`; criteria as amended).**

| arm | w | TB-C1 all | neg % | matched | counterfactual | C1? | TB-C2 per-pair | pooled | C2? | TB-C5/cell | TB-C5b | TB-C6 C1w | TB-C6 d5 | TB-C4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | 0 | 0.000 | 0 % | 0.000 | 0.000 | — | +0.015 | −0.048 | — | 1.54 | 24 | 0.00 | 0.00 | 1.000 |
| TB-A1 | 0.10 | −0.554 | 67 % | −0.372 | −0.471 | — | **+0.626** | +0.352 | **PASS** | 2.00 | 12 | **−3.67** ⚠ | −1.00 | 0.947 |
| TB-A2 | 0.30 | **−1.080** | 88 % | −0.769 | **−1.040** | **PASS** | +0.475 | +0.457 | — | 4.00 | 6 | **−4.96** ⚠ | −2.88 ⚠ | 0.807 ⚠ |
| TB-A3 | 1.00 | **−1.709** | 96 % | −1.068 | −1.375 | **PASS** | +0.213 | +0.485 | — | 6.08 | 0 | **−5.62** ⚠ | −4.38 ⚠ | 0.670 ⚠ |

**Mechanical observations, no verdict:**

- **No arm passes TB-C1 and TB-C2 together.** TB-A2/TB-A3 pass TB-C1 (including the
  counterfactual); both miss TB-C2's per-pair primary (0.475 / 0.213 against 0.5).
  TB-A1 passes TB-C2 and misses TB-C1. The gradient is **non-monotone in `w`** again —
  at strength the path is near-maximally obscure by d5, and the victim-supply mechanism
  (§0's row) is live: **sub-decile victims 0 → 3 → 14 → 56 across the ladder**, the
  first direct measurement of TB-P1 F4's predicted dynamic.
- **TB-C6 flags every arm, in both windows** (TB-A1's d5 window sits exactly at −1.00,
  the flag boundary; its C1-window −3.67 flags it regardless).
- **TB-C1(ii) fires on TB-A2**: matched-only −0.769 misses −1.0, so the fixed wording
  applies — *the pass is carried substantially by artists with no English Wikipedia
  article*. The counterfactual (i) nonetheless holds (−1.040). TB-A3's matched-only is
  −1.068 — the first arm in either track whose pass survives on matched artists alone.
- **TB-C5b (the REQ-Q1 degree diagnostic, first use): P's scored interiors include 24
  distinct top-1%-degree artists; TB-A3's include 0.** The device moves the journey off
  the well-connected stepping stones entirely at strength.
- **TB-C4 (interior hops, gates nothing): 1.000 → 0.947 → 0.807 → 0.670.** P's interior
  hops are ceiling-saturated at exactly 1.000 (DD-P3H's side fact, reproduced); the
  drops at TB-A2/A3 are large.

**Next: TB-P5, the harness review — dispatched before any read, per §5's amended order.**
