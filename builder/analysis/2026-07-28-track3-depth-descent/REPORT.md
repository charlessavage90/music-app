# Track 3 — the depth-descent device: results

**Owns its figures.** Governing document:
`docs/superpowers/specs/2026-07-28-track3-depth-descent-preregistration.md`; amendments
and their reasoning in `docs/superpowers/2026-07-28-track3-depth-descent-execution-log.md`.
Artifact `graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`.

Scored on **8 analysis pairs**; 4 held-out reported separately; 4 all-famous anchors
excluded from every criterion (they cannot pass DD-P1 — execution log §2). One cell
dropped uniformly under A13 (`Openzone Bar -> Gjallarhorn@d20`). Fame matched
710/832 = 85.3 % (reported, not gated — A12).

## Gates

| gate | result |
|---|---|
| **DD-G1** mirror reproduces production byte-identically with the device off | **PASS**, 212/212 cells |
| **DD-G2 / DD-C3** every arm's d0 path identical to P's, anchors included | **PASS**, 16/16 pairs |
| **DD-G3** artifact identity | asserted in every script |
| **DD-G4** fame keyed by mbid; no blank-named scored interior | **PASS** |

## Measured

| arm | `w` | DD-C1 | % neg | C1 | DD-C2 | C2 | DD-C5 /cell | DD-C5 distinct | DD-C6 | DD-C4 sim |
|---|---|---|---|---|---|---|---|---|---|---|
| **P** | 0.00 | 0.000 | 0 % | — | **−0.158** | — | 1.52 | 15 | 0.00 | 0.980 |
| **DD-A1** | 0.01 | −0.658 | 83 % | — | +0.275 | — | 1.87 | 21 | **−4.35** ⚠ | 0.837 ⚠ |
| **DD-A2** | 0.03 | **−1.287** | 87 % | **PASS** | **+0.644** | **PASS** | 3.09 | 59 | **−5.74** ⚠ | 0.736 ⚠ |
| **DD-A3** | 0.10 | **−1.923** | 83 % | **PASS** | +0.364 | — | 4.87 | 101 | **−6.52** ⚠ | 0.583 ⚠ |

Realised toll at k = 10, pctl = 1: DD-A1 5× `w_hop`, DD-A2 15×, DD-A3 50× — matching
§2's factor table exactly. Guard G fired 42 times in **every** arm including P, and the
floor was live on 1.11–1.19 % of relaxations in every arm: neither varies with the knob,
so DD-P3's finding-10 exposure did not materialise and the floor is not silently
interacting.

## Exposure map — one row per criterion × the changed knob

The only knob that varies is `w_known_ramp_pctl`. Every other term is at production
(§0), verified by the invariant guard-G and floor statistics above.

| criterion | crosses the knob? | measured where | reading |
|---|---|---|---|
| **DD-C1** fame of middles at d ≥ 10 | yes, directly | 8 pairs × 3 depths, paired vs P | monotone in `w`; DD-A2 and DD-A3 pass |
| **DD-C2** fame drop d5 → d20 | yes | pooled analysis interiors | **non-monotone** — see below |
| **DD-C3** first path identity | **no** — the term is exactly zero at k = 0 | all 16 pairs at d0 | holds by construction, verified |
| **DD-C4** per-hop similarity | yes | all hops, d ≥ 10 | falls monotonically; **all arms flagged** |
| **DD-C5** obscure artists delivered | yes | interiors below pctl 0.90, d ≥ 10 | rises monotonically |
| **DD-C6** interior count | yes | paired vs P at the same cell | falls monotonically; **all arms flagged** |

## Reads

**DD-R1 fires: an adoptable candidate exists.** DD-A2 passes DD-C1 (−1.287 ≤ −1.0 with
87 % ≥ 75 % of cells negative) and DD-C2 (+0.644 ≥ 0.5) with DD-C3 holding. Run state
presupposed by DD-R1 — all walks scored, uniform drop applied, DD-P1 discharged — is
satisfied in full. **Nothing further is owed for this read.**

**But DD-C6 flags every arm, so DD-C1 may not be read as descent.** DD-A2 shortens the
journey by a mean 5.74 interiors (about 13 → 7). This is the DD-D5 confound arriving
exactly where it was predicted, and it is why DD-C6 was adopted before the run rather
than after seeing this table.

**DD-C4 flags every arm too**, and the drop is large: median per-hop similarity 0.980 → 0.736
at DD-A2, 0.583 at DD-A3. DD-C4 gates nothing by design — the record is explicit that
offline coherence metrics were the *worst* predictors of the owner's verdict — but a
0.244 drop is not a rounding error, and it is precisely what a blind listen exists to
adjudicate.

**Production fails DD-C2 in the negative direction: −0.158.** Its middles get *more*
famous as bypasses accumulate, not less. That is the owner's original complaint,
measured in fame currency on this pair set for the first time.

**DD-C2 is non-monotone in `w`** (0.275 → 0.644 → 0.364). Not noise: at `w = 0.10` the
path is already near-maximally obscure by d5, so there is little room left to descend by
d20. The gradient compresses against its own floor. **DD-A3 is therefore not simply
"more of DD-A2"** — it trades depth-gradient for absolute obscurity.

**DD-R2 does not apply** (it is the null read, and DD-C1 moved past −0.3 in every arm).
**DD-R3 does not apply** (DD-P1 discharged at 100 % headroom).

## What this run cannot settle

Whether a journey of ~7 mostly-obscure artists is **better** than one of ~13 mostly-famous
ones carrying about 1.5 obscure. That is a preference question, it lands on a genuine
tension between two recorded owner values (execution log §4), and no criterion in this
directory can resolve it. **This document schedules no blind listen and no adoption**;
both are the owner's, per prereg §7.
