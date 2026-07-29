# Track 3 — the depth-descent device: results

**Owns its figures.** Governing document:
`docs/superpowers/specs/2026-07-28-track3-depth-descent-preregistration.md`; amendments
and their reasoning in `docs/superpowers/2026-07-28-track3-depth-descent-execution-log.md`.
Artifact `graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`.

Scored on **8 analysis pairs**. The **4 held-out pairs are reported in §4 below** and
gate nothing; the **4 all-famous anchors are tabulated in §5, descriptively, and are
excluded from every criterion**. One cell dropped uniformly under A13
(`Openzone Bar -> Gjallarhorn@d20`). Fame matched 710/832 = 85.3 % (reported, not
gated — A12).

---

## The verdict

**DD-R1 fired on the letter.** DD-A2 (`w = 0.03`) passes DD-C1 and DD-C2 with DD-C3
holding.

**The mechanism claim — that the device buys obscurity by pricing depth — is
UNRESOLVED**, because DD-C6 flags every arm: the fame movement is substantially
shortening, not descent.

**What exists is a measured candidate for a *different* trade than the one this
pre-registration set out to test** — roughly **7 mostly-obscure artists against today's
13 mostly-famous** — **and that trade is the owner's to judge, not a criterion's.**

**One further qualifier, found by the harness review and verified independently
(§8): about 45 % of DD-A2's fame movement is carried by artists with no English
Wikipedia article, scored at the fame floor.** Over matched interiors only, DD-A2's
DD-C1 is **−0.709** and would not meet −1.0. The floor is A11's adopted encoding and an
unmatched artist genuinely is *reach*, so this is not a defect — but the pass is a
statement about **unfindable** artists as much as about **less famous** ones, and a
summary omitting it would mislead by selection.

## §1 — Gates

| gate | result |
|---|---|
| **DD-G1** mirror reproduces production byte-identically with the device off | **PASS**, 212/212 cells |
| **DD-G2 / DD-C3** every arm's d0 path identical to P's, anchors included | **PASS**, 16/16 pairs |
| **DD-G3** artifact identity | asserted in every script |
| **DD-G4** fame keyed by mbid; no blank-named scored interior | **PASS** |
| **DD-P3 first half** protocol review | discharged — `DD-P3-analyst-review.md` |
| **DD-P3 second half** harness review (P8b precedent) | **DISCHARGED** — `DD-P3-harness-review.md`; every headline figure reproduced independently, zero disagreements |

⚠ **DD-R1 was first read with DD-P3's second half unclosed** — caught by the owner's
consultant review, not by this session. The harness review is precisely the guard against
a criterion reporting PASS for a reason other than the effect it names.

## §2 — Measured, analysis set

| arm | `w` | DD-C1 | % neg | C1 | DD-C2 | C2 | DD-C5 /cell | DD-C5 distinct | DD-C6 | DD-C4 sim |
|---|---|---|---|---|---|---|---|---|---|---|
| **P** | 0.00 | 0.000 | 0 % | — | **−0.158** | — | 1.52 | 15 | 0.00 | 0.980 |
| **DD-A1** | 0.01 | −0.658 | 83 % | — | +0.275 | — | 1.87 | 21 | **−4.35** ⚠ | 0.837 ⚠ |
| **DD-A2** | 0.03 | **−1.287** | 87 % | **PASS** | **+0.644** | **PASS** | 3.09 | 59 | **−5.74** ⚠ | 0.736 ⚠ |
| **DD-A3** | 0.10 | **−1.923** | 83 % | **PASS** | +0.364 | — | 4.87 | 101 | **−6.52** ⚠ | 0.583 ⚠ |

Realised toll at k = 10, pctl = 1: DD-A1 5× `w_hop`, DD-A2 15×, DD-A3 50× — matching §2's
factor table exactly. Guard G fired 42 times in **every** arm including P and the floor
stayed live on 1.11–1.19 % across all four, neither varying with the knob. ⚠ **Corrected:**
all 42 activations come from just two pairs at all 21 depths — both **unscored anchors
with adjacent endpoints**. No scored pair is adjacent, so guard G had nothing to fire on
at any `w`: DD-P3's finding-10 exposure is **untested rather than disproven**.

## §3 — Exposure map: one row per criterion × the changed knob

The only knob that varies is `w_known_ramp_pctl`; every other term is at production (§0),
corroborated by the invariant guard-G and floor statistics above.

| criterion | crosses the knob? | measured where | reading |
|---|---|---|---|
| **DD-C1** fame of middles at d ≥ 10 | yes, directly | 8 pairs × 3 depths, paired vs P | monotone in `w`; DD-A2 and DD-A3 pass |
| **DD-C2** fame drop d5 → d20 | yes | pooled analysis interiors | **non-monotone** — see below |
| **DD-C3** first path identity | **no** — term is exactly zero at k = 0 | all 16 pairs at d0 | holds by construction, verified |
| **DD-C4** per-hop similarity | yes | all hops, d ≥ 10 | falls monotonically; **all arms flagged** |
| **DD-C5** obscure artists delivered | yes | interiors below pctl 0.90, d ≥ 10 | rises monotonically |
| **DD-C6** interior count | yes | paired vs P at the same cell | falls monotonically; **all arms flagged** |

## §4 — Held-out confirmation (4 pairs). Gates nothing.

| arm | C1 | % neg | C2 | C5/cell | length vs P |
|---|---|---|---|---|---|
| P | 0.000 | 0 % | +0.180 | 1.75 | 0.00 |
| DD-A1 | −0.828 | 100 % | +0.361 | 1.92 | −3.50 |
| **DD-A2** | **−1.258** | 92 % | **+0.946** | 3.08 | −5.58 |
| DD-A3 | −1.703 | 100 % | +0.768 | 3.92 | −5.83 |

**DD-A2 meets both analysis-set thresholds out-of-sample.** DD-A3 meets them here having
missed DD-C2 on the analysis set (0.364 → 0.768) — carry that as a variance signal, not a
promotion. **Confirmatory only**: never pre-registered as a gate, and converting a
held-out set into one after seeing the analysis result is the move pre-registration exists
to prevent.

## §5 — All-famous anchors (4 pairs). DESCRIPTIVE ONLY. No criterion.

| arm | C1 | % neg | C5/cell | length vs P |
|---|---|---|---|---|
| P | 0.000 | 0 % | **0.00** | 0.00 |
| DD-A1 | −0.098 | 58 % | **0.00** | −1.50 |
| DD-A2 | −0.071 | 58 % | **0.00** | −1.58 |
| DD-A3 | −0.001 | 50 % | **0.00** | −1.50 |

**The device does essentially nothing on famous-to-famous journeys, at any strength.**
Fame movement −0.098 to −0.001 is indistinguishable from zero and *non-monotone* in `w`.
The payload column is **0.00 for every arm including production**: across all 12 anchor
cells, at strengths up to 50× `w_hop`, **not one interior below the top popularity decile
was ever delivered.**

DD-F1 confirmed at the level of the device rather than the graph — the disconnection is
not a price the router declines to pay, there is nothing to buy. **Every measured win in
§2 is on mid-band pairs; the original complaint was about famous pairs.**

## §6 — Other reads

⚠ **RETRACTED — production's negative depth gradient.** This REPORT previously said
production "fails DD-C2 in the negative direction: −0.158 — its middles get *more* famous
as bypasses accumulate", read as the owner's original complaint confirmed in fame
currency. **The sign is not robust.** The single A13-dropped cell is an analysis pair at
d20 only, so DD-C2's two pools come from different pair sets; under three alternative
poolings production reads **+0.076, +0.020, +0.020**. Production's depth gradient here is
**indistinguishable from zero** — still a failure of DD-C2's ≥ 0.5, but a materially
weaker statement than the one made, and the stronger one is withdrawn rather than
restated.

**DD-A2's DD-C2 pass is robust to the same test**: 0.644 / 0.801 / 0.847 / 0.847, every
pooling ≥ 0.5.

**DD-C2 is non-monotone in `w`** (0.275 → 0.644 → 0.364 on analysis). At `w = 0.10` the
path is already near-maximally obscure by d5, so little room remains to descend by d20.
**DD-A3 is not "more of DD-A2"** — and its gradient is largely a **pooling artefact**,
collapsing 0.364 → **+0.016** under length-unweighted pooling.

**DD-C4 flags every arm and the drop is large** (0.980 → 0.736 at DD-A2). It gates nothing
by design — the record is explicit that offline coherence metrics were the *worst*
predictors of the owner's verdict — but a 0.244 drop is not a rounding error, and it is
what a blind listen exists to adjudicate.

**DD-R2 does not apply** (the null read; DD-C1 moved past −0.3 in every arm). **DD-R3 does
not apply** (DD-P1 discharged at 100 % headroom).

## §7 — What this run cannot settle

Whether ~7 mostly-obscure artists beat ~13 mostly-famous ones carrying about 1.5 obscure.
That is a preference question, it lands on a genuine tension between two recorded owner
values (execution log **§4**), and no criterion here can resolve it. **This document
schedules no blind listen, no adoption and no further arms**; all are the owner's, per
prereg §7.

A named successor option — the **thresholded toll**, length-neutral exactly where DD-D5's
confound lives — is recorded **unstarted** at execution log **§7**. It requires its own
pre-registration and is not a tweak to this track.
