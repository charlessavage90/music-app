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
⚠ *Denominator corrected per TB-P5H-4: the ceiling's 23 cells are 23 **of the 24 the
arms score** — the ceiling probe inherited Track 3's drop set (`Openzone Bar →
Gjallarhorn@d20`), which TB's own run does not have. Immaterial to the gate; material to
any "of the 23" statement. And per TB-P5H-5 the ceiling is not a per-cell bound in either
direction — the arms cross it on up to 7/23 cells, because exclusion sets differ.*

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
  TB-A1 passes TB-C2 and misses TB-C1. ⚠ *This sentence originally read "the gradient is
  non-monotone in `w` again" — **corrected per TB-P5H-3**: the primary gradient is
  **strictly monotone decreasing** (0.626 / 0.475 / 0.213), the opposite of Track 3's
  mid-rung peak, and "again" asserted a continuity the figures do not have.* The
  monotone decay is what running out of headroom at d5 predicts — at strength the path
  is near-maximally obscure by d5, and the victim-supply mechanism
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

## §4 — TB-P5: the harness review. DISCHARGED.

Report: `builder/analysis/2026-07-29-track3b-thresholded-toll/TB-P5-harness-review.md`
(persisted verbatim from the reviewer); probes `tb_p5_probe_{rewalk,rescore,aux}.py`,
Snyk clean. **12 findings — 2 HIGH, 5 MED, 5 LOW — and 32 claims verified clean, with a
complete independent reproduction:** an independently written percentile, Dijkstra, walk
and victim rule (built from `ApiConfig` + `pathfinding.py` + the prereg §1 text, not from
`mirror.py`) returned **0 path mismatches across all 432 scored snapshot cells**, and 86
headline figures re-derived without importing `score_tb.py` agree to ≤ 2.2 × 10⁻¹⁶.

**What the findings add to the tables, none of it changing which read fires:**

- **TB-P5H-1 (HIGH):** TB-A2's TB-C1 pass is carried by two of eight pairs — removing
  either sinks it (margins 0.080 primary / 0.040 counterfactual). **TB-A3's pass is
  robust** (worst leave-one-out −1.334; all eight pairs individually clear −1.0).
- **TB-P5H-2 (HIGH):** TB-C2 is pooling-unstable for TB-A1/TB-A3 (the printed secondary
  *inverts* the ladder ordering); **TB-A2's TB-C2 failure is the one pooling-stable
  result** (0.446–0.475 under all four poolings). The §7 read is insensitive to the whole
  pooling family because TB-C6 flags every arm.
- **TB-P5H-3/4/5:** two wording defects in this log's own §2–§3, corrected in place and
  marked; the ceiling is not a per-cell bound in either direction.
- **TB-P5H-6:** the A11 exposure quantified — unmatched share rises with dose (7.1 % →
  24.1 % at TB-A3); the pre-registered counterfactual bounds only the flagged 18.5 % of
  it. The criteria stand as registered; the size is now on record.
- **TB-P5H-7:** no §7 read consumes the fact that both TB-C1-passing arms also miss
  TB-C2 — stated in §5 below so it cannot be lost, and carried as a design item for any
  successor pre-registration.

## §5 — The verdict, in the shape it must be summarised in everywhere

**TB-R2 fired on the letter, and TB-P5 verifies it is the only read whose condition
holds.** TB-A2 and TB-A3 pass TB-C1 — TB-A3 robustly, and as the first arm in either
track whose pass survives on Wikipedia-matched artists alone — but **every TB-C1-passing
arm is TB-C6-flagged in both windows**, and both also miss TB-C2's per-pair primary
(0.475 / 0.213 against 0.5), which no pre-registered read consumes and is therefore
stated here (TB-P5H-7). **The pre-committed reading: the toll family cannot produce
length-preserving descent on this graph — the thresholded form was its best case**, so no
further toll-shaped term may claim descent without an explicit length-preserving
constraint, and any such constraint is a new device needing its own pre-registration.
**The mechanism question Track 3 left UNRESOLVED is resolved, negatively, for this device
family**: even with obscure interiors toll-free, the router prefers dropping famous
interiors to replacing them, and at strength the walk's own bypass victims start coming
from the obscure supply itself (0 → 56 of 240 across the ladder — TB-P1 F4's dynamic,
measured). **The candidate pool for the owner's product decision is DD-A2 and the best TB
arm, judged on requirements terms where shortening is priced by him, not by a criterion;
that judgement is his, is not scheduled here, and any cross-track candidate comparison
must be recomputed under one statistic first** (the prereg's comparability guard — TB and
DD scores use different cell statistics and hop definitions). This wording is fixed; no
summary may soften it. TB-R0, TB-R1 and TB-R3 do not apply.

## §6 — Closeout record (2026-07-29)

**Suites (D4), run not asserted:** builder **115 passed**, api **217 passed**, frontend
**107 passed** — identical to the Track 3 closeout's counts, the check that shipped code
was untouched by this track (the only committed-file change outside docs and the analysis
directory is `mirror.py`'s additive, default-off term; TB-G1 at 212/212 is the direct
evidence).

**A4 — default-flip inapplicable by design, stated not skipped:** `w_known_thresh_pctl`
defaults 0.0 and **must stay there** — analysis mirror, nothing adopted; unshipped is the
premise.

**A5 — no listener on 8000, 5173, 8138 or 8139.** Nothing started, nothing left running;
this session's background jobs (arms, fame fetch, suites) all completed. No queued item
needs a local server.

**A3 — deferrals swept, conditions re-tested:** the A11-flag deferral came due this track
and is **discharged** (TB-G4, struck in `NEXT.md`'s table); the **nameless drop rule is
now DUE** (its condition is the rebuild plan, which is the next work — carried into the
plan's scope via the handoff); `--prune` ripe since today, owner's; two new deferrals
recorded with conditions (`TB-P5H-7`; the candidate-pool recompute).

**B2 — reachability:** every new module is a CLI entry in the directory README's script
table; `tb_p1_probe_ceiling` is additionally imported by `tb_p3_ceiling` (one
implementation of the ceiling, deliberate). No orphans.

**B3 — vacuous-test check, discharged in the strongest available form:** TB-G2 carried an
explicit non-vacuity check (d1 differs from P on 11–12/16 pairs per arm — the gate can
fire on the thing adjacent to it), and TB-P5 independently reproduced the entire run
(0/432) and every headline figure without importing the scorer. No new suite tests were
written; the criteria live in analysis scripts whose vacuity is what TB-P5 exists to test.

**B4 — prose-vs-code:** performed by TB-P5 across the runner, scorer and mirror (32
verified-clean claims), and it caught two prose defects in this log's own §2–§3
(TB-P5H-3/4), both corrected in place and marked — the fifth recorded instance here of a
cold reader finding defects in documentation its author had just written.

**B5 — stale-description sweep incl. `.claude/`:** the mirror change is analysis-only, so
no agent definition describes it wrongly; `CLAUDE.md`'s what-is-better orient row was the
one stale description found (it named WGLL alone after WGLL stopped governing alone) —
corrected, delta below. `NEXT.md` rewritten with no figures.

**B1 — lint + audit:** `docs-lint.sh` hard checks **passed**; candidates were
weight-constants coinciding with adjudication decimals, handed to the auditor.
`doc-auditor` dispatched post-edit (avoiding Track 3's race); outcome recorded in the PR
when it reported.

**D6 — the standing context layer:** unconditional **44,113 characters (delta +340 from
43,773)**; conditional **2,121 lines (delta 0)**. The +340 is the orient-row correction
above — reported to the owner with the wording and the option to revert, per the D6 rule
that a correction costing net characters is his to ratify. Nothing added to `memory/`.

**D1/D3:** tree clean at commit; no artifact adopted or created — the one artifact in
play remains `graph-t15-tiebreakfix.bin`, sha256 asserted by every script.

**D5:** PR opened from `requirements-track3b`; body carries the gate outcomes, the
verdict pointer, deferrals, and the closed list.
