# Documentation map

**Role: AUTHORITATIVE.** The current classification of every document in `docs/`. Where
another document disagrees with this one about a document's role, this wins.

**Read this before citing any document in `docs/`.** It says which documents are
authoritative, which are historical, and which must never be used as context.

Every document here has exactly one **role**. The role determines how much you can
trust it and whether you may act on it.

| Role | Meaning |
|---|---|
| **AUTHORITATIVE** | Current and correct. Cite it. If another document disagrees, this one wins. |
| **ACTIVE** | Work in progress. Current intent, but not yet reality. |
| **COMPLETE** | Describes work that shipped. Accurate as history; may not describe the code today. |
| **HISTORICAL** | Superseded. Retained so the reasoning can be audited. **Do not cite. Do not act on.** |
| **NARRATIVE** | Written for humans, not for engineering. **Never use as context for development.** |
| **EXTERNAL** | Not ours. Third-party reference material. **Not project documentation.** |

---

## The one rule that matters most

**Measured figures about similarity scoring, hub-seeking, and path quality live in
exactly one file:**

> ### `superpowers/findings/2026-07-21-scoring-adjudication.md`

Every other document **cites it by section number and does not restate its numbers.**
Its **§6** is a table marking 27 prior claims as upheld, overturned, or unresolved —
check there before trusting any scoring claim you find anywhere else.

This rule exists because five documents each kept their own copy of the same figures
and drifted into three mutually contradictory positions. Two separate analyses were
invalidated before anyone noticed. **Restating a correct number is still a violation** —
that is how the drift began.

---

## Current state

- ⛔ **Repair + retune is DONE. Track 1 was adopted; Track 2 (2026-07-24) and Track 2F
  (2026-07-25) both returned nulls; the ceiling **ordering** measurement (2026-07-25) came
  back **WIDE** — nothing adopted at any point.** Current handoff:
  [`superpowers/2026-07-25-HANDOFF-track2f-and-headroom.md`](superpowers/2026-07-25-HANDOFF-track2f-and-headroom.md),
  which supersedes the 2026-07-24 one **on next actions only**. **The execution log's last two
  entries are fresher than any handoff.** Track 2F ran the ceiling toll at full strength — the
  previous handoff's own recommendation, now executed — and exhausted that mechanism with its
  bound holding, which Track 2's corner arm never managed. The half it structurally could not
  reach, the ceiling's *ordering*, was then measured read-only and is WIDE. **Live candidate: a
  builder-side p99 rescale, still un-pre-registered and blocked behind the nameless-artist
  decision.** **Next action is the owner's.** **Before that rescale is pre-registered, read
  [`superpowers/findings/2026-07-25-router-ascent-gradient.md`](superpowers/findings/2026-07-25-router-ascent-gradient.md)** —
  a re-reading of the P8b review's ascent measurement, which argues the rescale is likelier to
  yield *better-chosen famous* artists than *more obscure* ones, and names two re-reads of
  already-committed runs that would settle it without a rebuild. It owns no figures and
  proposes no arm. The defect record and diagnosis below remain essential reading before touching
  Phase 1 — the three conflated quantities it warns about are still live hazards.
  **Read [`superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md`](superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md)
  §2 before any Phase 1 work — and read §2.12 first, because it retracts a central claim of
  §2.9 and corrects §2.10 and §2.11.**
  - **What is settled.** Two real defects in the **adopted-at-the-time** artifact (figures
    owned by the sections cited, not restated here): the most popular artists were among
    the least connected, caused by an MBID tie-break over p99-clipped scores (§2.8); and
    famous→obscure edges were depleted well below a structure-preserving null, caused by
    the mutual-k-NN reciprocity rule (§2.10). Routed paths never present an artist below a
    very high popularity percentile, at any bypass depth, on either graph tested (§2.9). ⚠ **All of §2.9–§2.12's tables were measured on `graph-t15-capfix.bin`, not the adopted artifact** — see `superpowers/findings/2026-07-25-consulting-derivations.md` `DRV-1`. The conclusions are argued to survive (`DRV-2`); the individual figures must not be quoted as facts about the running app until re-measured.
  - **What it is NOT.** Not primarily a graph problem. Obscure artists are a small, fixed
    number of hops from every famous artist tested, and even the most-connected famous
    artists have a handful of admissible `known` substitutes (exact counts: §2.12).
    **§2.12 concludes this is a cost-function problem** — the router prices the exits
    correctly and declines them.
  - **Three quantities that are not interchangeable** and have each caused an error here:
    **degree ≠ fame** (§2.6), **popularity ≠ fame** at the top of the distribution (§2.11),
    and **raw popularity ≠ percentile** (§2.12). Do not trust any
    `top1pct_degree_frac` (named `hubfrac` before 2026-07-23) or payload figure,
    and check which currency a claim is in before acting on it.
  - **Decided 2026-07-23:** the owner chose **repair + retune** — governing design
    `superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md`; its §1
    also records the nine-names verdict (in-graph popularity ≠ fame at the top,
    confirmed) and the owner's relaxation of the listening-test prohibition.
  - **Track 1 is DONE, 2026-07-23: the §2.8 tie-break is fixed and the rebuilt artifact
    is adopted.** The app now routes on `graph-t15-tiebreakfix.bin` — identity and
    verification in `superpowers/findings/2026-07-23-tiebreak-fix-adoption.md` (the
    authoritative record for the adopted artifact's checksum). Radiohead is back;
    famous-artist neighbourhoods are score-ranked, not MBID-ranked.
  - **Track 2 is COMPLETE and returned R0, a full null, 2026-07-24.** All 15 arms scored over
    two stages; the best reached −0.177 against a −1.0 threshold. **Nothing adopted, no shipped
    code changed, no blind listen run.** Firmest finding, and it needs no fame measurement: the
    **floor device is never pivotal** — the two floor arms are byte-identical to their base
    across every scored cell while the floor term fires 3× more often than production's, so the
    only depth-graduated device in the cost function cannot do its job. **R0 does NOT license
    "the repricing family is exhausted"** — A17(c)'s falsifier fired. Figures are owned by
    `builder/analysis/2026-07-24-track2-arm-scorer/`; the execution log narrates them.
- **Gate 1 (personal use).** Phase 2 (path quality) is **COMPLETE**, 2026-07-22. All 16
  tasks executed on branch `phase2-path-quality`. The blind listening test was run and the
  owner adopted the **`capfix`** arm — `cap_strategy="mutual_knn"`,
  `similarity_rescale="p99_log_clip"`, `similarity_damping=0.0`. See execution log §16
  (verdict) and §17 (adoption). **That adoption is not overturned** — but §2 of the Phase 1
  log is information that was not available when it was made.
- **Phase 1 resumed 2026-07-23; Track 1 is done and adopted, and Track 2 has now run and
  returned a null.** C3
  (`w_floor` is a no-op; `known` degrades to a bare hard exclusion — a *pathfinding*
  defect rather than the UX item it was filed as) is now folded into Track 2's
  cost-function retune, per
  `superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md` §4. Current
  sequencing: see that spec and
  `superpowers/2026-07-23-repair-and-retune-execution-log.md`. **Clips (C1, C2) and the four
  frontend UX items are DONE and CLOSED 2026-07-25** — built in PR #19, completed in PR #20,
  and **confirmed in use**. ⚠ **C1 is nonetheless not fully closed:**
  [`superpowers/findings/2026-07-25-bypass-depth-use-run.md`](superpowers/findings/2026-07-25-bypass-depth-use-run.md)
  `BYP-13` records a card that played a clip by a *different artist of the same name*, found in
  use on 2026-07-25. C1 was closed on a worked example where a band name collided with a song
  title; this is an **artist-name collision aggravated by a rename**, a different route to the
  same failure, and it is live. Not path-quality work, not paused. Record:
  `superpowers/2026-07-25-gate1-clips-and-ux-execution-log.md` (§15–§19 carry the clip
  closure and two playback defects found in that use). **F1 — zero-intermediary paths — is
  the remaining Gate 1 item**: the owner has decided every journey needs at least one stop.
  Implementation has landed, on branch `f1-min-stop` — design
  `superpowers/specs/2026-07-25-f1-minimum-stop-design.md`, plan
  `superpowers/plans/2026-07-25-f1-minimum-stop.md` — and it is not inside the path-quality
  pause (§16). Not yet closed: closure needs the queued use-the-app check (plan Task 6),
  which only the owner can run.
  Two items carry in from Phase 2 with success conditions; see the roadmap's Phase 1 section.
- **Two Phase 2 predictions did not survive measurement**, and older prose still asserts
  them. Damping ("C4") was tested at 0.25 / 0.5 / 0.75 and **rejected** — the undamped arm
  won. Neighbour-set Jaccard was **not** adopted as the primary objective; the
  overlap-family metrics sign-flip between slices at these effect sizes (adjudication §6
  claims 41–42). The p99 ceiling defect **survives adoption** and is carried to Phase 1.
- `superpowers/plans/2026-07-22-phase2-revised-plan.md` governed Tasks 14–16 and supersedes
  the remaining tasks of the 2026-07-21 plan. Both are now historical.

---

## Every document, by role

### Authoritative

| Document | Covers |
|---|---|
| `superpowers/findings/2026-07-21-scoring-adjudication.md` | **All** scoring, hub-seeking, and path-quality figures. The single quantitative record. |
| `superpowers/WHAT-GOOD-LOOKS-LIKE.md` | **What the owner means by a better path.** Calibration for the blind listening test — this project's strongest evidence class, which decided the graph twice where the offline metrics decided it zero times. Read before interpreting any listening verdict, **and before designing anything that scores a path**: it holds no thresholds and must not be mined for any, but a criterion that contradicts a value in it is wrong (worked example: the Track 2 pre-registration's C4). |
| `superpowers/findings/2026-07-22-phase2-sweep-results.md` | Every figure from the Phase 2 six-arm sweep. Owns its numbers; linked from the adjudication's §6 (claims 41–45). |
| `superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | Gate structure and phase ordering. Its C4 is a pointer only — it holds no figures. |
| `superpowers/findings/2026-07-23-tiebreak-fix-adoption.md` | Identity (sha256) and verification record of the **adopted** 75k artifact, post tie-break fix. |
| `superpowers/findings/2026-07-22-configuration-model-null.md` | Authoritative for its own figures — the exact configuration-model null referenced by Phase 1 log §2.10/§7.1 item 1. |
| `superpowers/findings/2026-07-23-track2-protocol-analyst-review.md` | **AUTHORITATIVE for its own §2 measurements; ADVISORY on the protocol.** The `ml-graph-analyst` review of the Track 2 pre-registration, discharging its prerequisite **P8** and the design's §4.6 review gate. Verifies the pre-registration's §0 resolution table **in code**, and raises numbered protocol observations (O-series) and recommendations (PR-series) that the Track 2 session must read before running any arm. Scope is the **protocol only** — the harness is a separate review (P8b). Remit is derivation, not judgement: it says nothing about whether the experiment is worth running. Measurements: `builder/analysis/2026-07-23-track2-protocol-review/`. |
| `superpowers/findings/2026-07-23-a0-gate-analyst-review.md` | **AUTHORITATIVE for its own measurements; ADVISORY on the protocol.** The `ml-graph-analyst` review of the step-4 A0-vs-P result. Establishes that the raw floor's *value* is arm-invariant but its *effect* is not (a first-path change alters who gets bypassed, and that carries to depth); that the unconditional dead-bound is **7** `known` bypasses, not 6; that the d0–d2 floor asymmetry between a diving arm and production is real and large; and it corrects the claim-23 wording before it enters the adjudication. Figures: `builder/analysis/2026-07-23-track2-a0-review/`. |
| `../builder/analysis/2026-07-24-track2-p8b-harness-review/` | **AUTHORITATIVE for its own measurements; ADVISORY on the harness.** The `ml-graph-analyst` review of the Track 2 **Stage A scorer**, discharging pre-registration prerequisite **P8b** — the companion to the P8 protocol review above, and the gate that stood between the harness and the arms. Verdict: fit to run stage 1, not fit to run stage 2 as it then stood. Fourteen findings, two HIGH. **Owns** the blank-name and duplicate-name figures, the floor-lifetime depths, and the measurement showing the `X` arm does not bound what §1.4 claims. **Not a `findings/` document, deliberately** — a second copy would restate its figures, which the rule above forbids; cite this directory. Its consequences live in pre-registration **A17–A19**. |
| `../builder/analysis/2026-07-25-track2f-toll-ladder/` | **AUTHORITATIVE for its own measurements.** The Track 2F dose-response ladder on the similarity-ceiling toll, run 2026-07-25 after Track 2's A17(b) established that the toll had only ever run at half its intended magnitude. **Owns** the ladder's `C1`–`C4` figures, the isolating contrasts, and **`TF-D1`, the ceiling-hop usage measurement** — the finding that production takes 85 % of its hops on ceiling edges and that no price drives that below 28.86 %, because those hops are structurally forced. Result **`TFR0`**, a null on the primary criterion at `M*` = −0.198; **nothing adopted**. Unlike Track 2's corner arm, **its bound holds** (`TFR4`), so the null may be stated at mechanism strength. **Not a `findings/` document, deliberately** — a second copy would restate its figures. Cite this directory. |
| `../builder/analysis/2026-07-25-ceiling-ordering-headroom/` | **AUTHORITATIVE for its own measurements.** How much edge ordering the p99 clip destroys, measured read-only from the archive on 2026-07-25 — the untested half of the ceiling hypothesis that Track 2F's toll structurally could not reach. **Decision rule committed before the measurement ran** (`0e39522`); verdict **WIDE**, median erased cost spread **10.01 × `w_hop`** against a 1 × threshold, and **100 % of the pre-registered endpoints above 7.5 ×** — a magnitude Track 2F proved changes routing. Carries an **identity gate**: the in-memory rebuild reproduces the adopted artifact's sha256, so the figures are about the graph in use. **Owns** the mechanism statement — at a fully saturated node the similarity term contributes nothing, so the router discriminates on popularity alone. Licenses *pre-registering* the builder-side rescale; **not** adoption. Cite this directory. |
| `superpowers/findings/2026-07-25-mutual-knn-stranding.md` | **AUTHORITATIVE for its own measurements. Records a mechanism; proposes nothing.** Why recognisable artists (Meat Loaf, Elbow, The Cult, The Streets, Nada Surf, Pretenders) hold one or a handful of connections: `mutual_knn` requires both artists to rank each other in their top 50, so an artist whose nearest neighbours are all more listened-to than it loses every edge in both directions. **Owns** the reciprocity figures (`MKS-3`: 43.7 % mean survival, 9.3 % of artists left with ≤1 edge), the degree-by-popularity table (`MKS-4`), and the no-detour pair counts (`MKS-6`: 6,599 total, 203 non-leaf) that make **F1 unsatisfiable for those pairs on this artifact**. **Distinct from the tie-break fix** (`MKS-5`), which repaired the very top and left this band untouched. **The mechanism itself is NOT new — cite Phase 1 log §2.10, which isolates the reciprocity rule by factorial and owns those figures; this document's `MKS-5a` records that an earlier draft wrongly claimed otherwise.** What is new is the per-artist view (§2.10 measures a distribution, not who is affected) and the F1 consequence. Explicitly **not** evidence that a looser rule would be better — `mutual_knn` won a blind listen, and §2.10's coupling (dropping reciprocity restores unbounded degree) binds any redesign (`MKS-5b`). Nothing adopted; the path-quality pause is intact. Measurements: `builder/analysis/2026-07-25-mutual-knn-stranding/`. |
| `superpowers/findings/2026-07-26-low-degree-census.md` | **AUTHORITATIVE for its own interpretation; OWNS NO FIGURES** — every quantity belongs to `../builder/analysis/2026-07-26-low-degree-census/`, whose `REPORT.md` is the deliverable. **Cite that directory for any number.** Which artists can never appear mid-journey: an artist with one connection can only ever be one of the two the user typed, so the app can never introduce anyone to it (`DRV-4` stated this as structural and unmeasured; this measures it). **Closes three open questions**: `DRV-4`'s denominator (the two populations are **nested, not alternatives** — `pipeline.py:131,184` make every artifact node a crawled artist, and the fractions differ immaterially); that the count is post-largest-component-prune (confirmed observationally, not argued); and that non-artist entities are excluded (checked, not assumed — the nameless nodes are the one contaminant). Fame is the **adopted proxy unchanged** (§5 + A11 + A15, imported not reimplemented); **graph popularity ranks nothing** (§2.11) and was used only to screen who to ask — sound because popularity is accumulated *before* the mutual-kNN cap, so the reciprocity rule destroys degree and leaves popularity untouched. **Does not establish** that the lists are the true top of all low-degree artists: the cut was deliberately not deepened (owner's call), and a famous artist with low in-graph popularity is carried as a **candidate crawl-coverage gap**, not filed as instrument noise. Carries **`CNS-1`** in §3, recorded in passing per the `MKS-7` precedent: an artist can be unfindable under the name users know it by, because the graph stores one name and no aliases (Pretenders / The Pretenders). Nothing rebuilt, adopted or proposed; the pause is intact. |
| `superpowers/findings/2026-07-26-stranding-causes.md` | **AUTHORITATIVE for its own interpretation; OWNS NO FIGURES** — every quantity belongs to `../builder/analysis/2026-07-26-stranding-causes/`, whose `REPORT.md` is the deliverable. **Cite that directory for any number.** Separates *why* the degree-1/degree-2 artists are low-degree, which the census (above) counted but did not explain. Identifiers **`STC-`**. **`STC-1`: the crawl-frontier cause, as usually phrased, is nearly empty** — the dominant cause is that the source named almost no similar artists for them at all, and `STC-2` records that practically everything it did name had already been crawled. **`STC-3` is the reading rule**: the set is dominated by unfixable artists *by headcount* and by rule-fixable ones *by who anyone would recognise*, the two are almost perfectly stratified by popularity, and quoting either alone misleads. **`STC-4` is the strongest thing cutting against a cap-rule change** — most of the set is named by four artists or fewer, so even the most permissive rule reaches few of them, and the ones it does reach are all at the popular end. **`STC-6` corrects a claim an earlier draft of this document made**: SOURCE-THIN means "nothing above the co-occurrence threshold **we chose**" (`BuilderConfig.algorithm`), not "the source knows nothing" — so a lower-threshold re-crawl is inside project control, with an unmeasured payoff; the length limit was checked and provably cannot cause short lists. **`STC-5` records a limitation in `reciprocity.py`** (it does not model the builder's special-purpose exclusion), corrected here, **not invalidating** `findings/2026-07-25-mutual-knn-stranding.md`. The boundary between the populations is the session's stated choice and the report prints eleven alternatives. Nothing rebuilt, adopted or proposed; the pause is intact. |
| `../CLAUDE.md` | How to work in this repo: commands, architecture, conventions. |

### Active

| Document | Covers |
|---|---|
| `superpowers/2026-07-21-phase2-execution-log.md` | **The audit trail for Phase 2.** Every decision and why, defects found in the plan and in the prior record, gate pass/fail state, open items, deferred findings. **§16 is the blind-test verdict; §17 the adoption; §18 the closeout triage; §19 the fixture-seed defect found after closeout — which supersedes §17's checksums.** Where any other document disagrees with §16–19 **on Phase 2**, this wins. **No longer the freshest truth in this directory** — as of 2026-07-23 that is `2026-07-23-repair-and-retune-execution-log.md` and `findings/2026-07-23-tiebreak-fix-adoption.md`, which govern current status and the adopted artifact. Marked ACTIVE rather than COMPLETE because Phase 1 consumes its carried-forward items. |
| `superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | *(also listed as Authoritative)* Its Phase 1 section gives the **phase structure**, including the two items carried in from Phase 2 with success conditions; current sequencing within Phase 1 is governed by the 2026-07-23 repair+retune spec, not this document. |
| `superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md` | ⛔ **Start here for Phase 1, and read §2 before any implementation.** One document by design: the **graph-structure defect that halted the work** (§2 — facts, discovery mechanism, suspected cause; deliberately no solutioning) **plus** the full Phase 1 progress record (§3 — including two independent ML-analyst reviews and what each overturned), what is closed (§4), artifacts (§5), and state of play (§6). Splitting it would let the progress record be picked up without the context that stopped it. **Owns its figures** — cite from here, do not restate. |
| `superpowers/2026-07-22-HANDOFF-phase1.md` | Written at Phase 2 closeout for a cold session: what was overturned and must not be reverted, and what the previous session knew that is not otherwise in the record. **Superseded on Phase 1 status by the log above** — that document governs where they disagree. Still valid on Phase 2 outcomes. |
| `superpowers/2026-07-23-HANDOFF-track2.md` | **SUPERSEDED 2026-07-24** by `2026-07-23-HANDOFF-track2.md`'s successor below — its loose ends are closed or folded forward. Retained for audit; do not act on it. *(Original role: loose ends written at the 2026-07-23 mid-track retirement.)* |
| `superpowers/2026-07-24-HANDOFF-track2.md` | **SUPERSEDED 2026-07-24 by `2026-07-24-HANDOFF-track2-scorer.md` below** — its one open unit (the sweep) is now half-built (the scorer exists) and re-described there. Retained for audit; do not act on it. *(Original role: fame-proxy/sweep seam handoff, P4 closed, A11 committed.)* |
| `superpowers/2026-07-24-HANDOFF-track2-scorer.md` | **SUPERSEDED 2026-07-24 (same day) by `2026-07-24-HANDOFF-track2-complete.md` below.** Its open unit — P8b, then the arms — is closed: P8b was discharged and all 15 arms ran. Its "no factorial arm has run" statements are now false. Retained for audit; **do not act on it.** *(Original role: handoff at the scorer/P8b seam.)* |
| `superpowers/2026-07-25-HANDOFF-track2f-and-headroom.md` | **The CURRENT handoff, 2026-07-25 — written at the Track 2F / headroom completion seam.** Track 2F ran the ceiling toll at full strength and returned **`TFR0`**, a null at `M*` = −0.198 — but **its bound holds**, unlike Track 2's corner arm, so the toll mechanism can be declared exhausted rather than merely untested at fifteen points. The ceiling's *ordering*, which no router-side arm can reach, was then measured read-only and came back **WIDE** (median 10.01 × `w_hop` erased). **Nothing adopted, no shipped code changed, no blind listen run, no threshold touched, no rebuild.** Carries the mechanism statement, the four things a successor must not get wrong, the open decision with the session's position, and what was decided *against*. Supersedes the 2026-07-24 handoff **on next actions only**. **Read the execution log's last three entries first**; where they disagree, the log wins. A seam handoff, not mid-flight. |
| `superpowers/2026-07-24-HANDOFF-track2-complete.md` | **⚠ PARTLY SUPERSEDED 2026-07-25** by the handoff above — **on next actions only.** Track 2's own result is untouched and this is still the record of it, but its §4 recommendation has been **executed** (that is Track 2F) and its §2 claim that the toll "has never run at full strength" is **no longer true**. Both are marked inline as well as bannered. *(Original role: the Track 2 completion-seam handoff, 2026-07-24.)* **Written at the completion seam.** The sweep ran to completion and returned **R0, a full null**: 15 arms, best at −0.177 against a −1.0 threshold, **nothing adopted, no shipped code changed, no blind listen run**. Carries what R0 does and does **not** license (A17(c)'s falsifier fired, so it does not reach "the family is exhausted"), the firmest finding (the floor device is never pivotal), the open owner decision with the session's recommendation, and the **three items now queued behind one rebuild**. **Read the execution log's Track 2 section first**; where they disagree, the log wins. A seam handoff, not mid-flight. |
| `superpowers/findings/2026-07-25-consulting-derivations.md` | **AUTHORITATIVE for `DRV-1` only; everything else is a labelled hypothesis with a named check.** Written when a consulting session was asked what it knew that was not written down. **`DRV-1` is verified and matters: every table in Phase 1 log §2.9–§2.12 was computed on `graph-t15-capfix.bin`, while the app has run `graph-t15-tiebreakfix.bin` since 2026-07-23** — the scripts assert capfix's checksum, and `known_viability.py` was committed six hours *before* the tie-break artifact was adopted. The visible tell needs no tooling: §2.12's worked example is "The Beatles have 7 of 7 neighbours admissible", and `MKS-5` records the Beatles holding the full 50 on the adopted graph. **`DRV-2` argues this is a provenance defect, not a refutation** — the pricing leg is artifact-independent and the exposed legs move in the direction that *strengthens* §2.12 — **but any specific §2.9–§2.12 figure quoted as a fact about the current app is unsupported**, which this map's Current State does. Re-running two committed read-only scripts settles it. `DRV-3`–`DRV-7` are unmeasured derivations recorded at hypothesis strength: the descent is a **round trip** and §2.12 priced it one-way; a **degree-1 artist can never be an interior card**, so it is undeliverable as a discovery; §2.12's substitute counts may be **leaf-inflated**; the **staircase model** that generated `BYP-11`; and **three discriminating signals go flat at the famous endpoints**, leaving popularity alone. §3 carries the session's opinions, fenced off from the findings. **§4 is the calibration**: the same session made three confident wrong claims that the owner caught, all from reasoning over summaries when the data was available — and it names which two hypotheses are most likely to fail the same way. Nothing adopted; the pause is intact. |
| `superpowers/findings/2026-07-25-bypass-depth-use-run.md` | **AUTHORITATIVE for its own measurements — the owner's own use of the shipped app, 2026-07-25.** **Two runs of 100 bypass presses** on one pair (Bob Dylan → Metallica): run 1 with the buttons mixed, run 2 **`dislike` only**. Dogfooding, not an experiment — one pair, one listener, nothing scored or pre-registered, and §1 states every protocol defect up front. **The headline (`BYP-3`): across 200 presses the app never presented an artist who is obscure by any ordinary reading** — floors of 372k and 168k Spotify monthly listeners. `dislike` finds more unfamiliar artists (10 v 7) and reaches ~2× deeper, confirming a prediction this document fixed *before* run 2 ran. **`BYP-11` is the most consequential reading**: genre departure precedes obscurity by ~50 presses, so the router appears to escape the famous stratum by crossing genres rather than descending within one — measured against `WHAT-GOOD-LOOKS-LIKE` value 8, that is buying novelty with incoherence. **`BYP-9`, confirmed and reproduced:** `dislike` held the path at 3 cards for nine consecutive presses, which at 3 cards is *forced* 1:1 swapping — the shape value 6 says `dislike` should show least. **`BYP-13` is a live defect and the most actionable item: a card played a clip by a different artist of the same name** (FERG / A$AP Ferg), which is **C1's class reached by a different route, so C1 is not fully closed** — not path-quality work, not paused. **Read §4 before citing any length claim**: `BYP-4` was written, corrected, then partly restored, and the settled statement is *an upward trend with large non-monotone excursions*. **Explicitly does NOT refute §2.9** — that is graph-popularity percentile, this is Spotify listeners. §9 records the second-opinion instrument's **failure mode** (name-based lookup returns the wrong entity for a renamed artist, and fails toward flattering the result) and `BYP-14` records that manual press-logging does not scale and was **mostly unnecessary** — a single-mechanism run is fully reconstructible by replaying truncations of one URL. §10 carries the length series and the reproducible URLs. The pause is intact; nothing proposed. |
| `superpowers/findings/2026-07-25-router-ascent-gradient.md` | **A re-reading of a committed measurement, not a new one — and it deliberately OWNS NO FIGURES.** The P8b harness review measured, one hop out from every node, how often the router's cheapest next step moves toward a *more popular* artist: for the production-like arm it is far above the share of the graph's own edges that point upward. That measurement is currently reachable only as **A17(c)**, a bound on how the corner arm `X` may be read, inside a pre-registration whose track returned a null — so nobody re-reads it. Its `ASC-1` (the router climbs about four times in five where the graph offers a coin flip) is a **single-arm measurement against a structural null** and is clean. Its `ASC-2` (the sweep's most aggressive dive-cheapening corner ascends *more*) is **explicitly confounded — three columns, not one** — and supports "the corner does not dive", never *why*. `ASC-3`/`ASC-4` are labelled **inference**: no arm in Track 2 or 2F was directional (the jump term is `w_jump·\|Δpop\|`, symmetric; the toll binds on the edge; the floor is one-sided on level, not direction), so the pull survives the whole span of repricing and probably originates outside the popularity terms — with `w_sim` the leading candidate, because similarity and popularity share a source. **Does not reopen §2.12**; sits underneath it. Names one cheap decisive test (`ASC-5`): re-read the gradient at path level and read the `X`-vs-`A7` contrast that already exists in the Track 2 run — **both re-reads of committed runs, no rebuild.** Figures owned by `../builder/analysis/2026-07-24-track2-p8b-harness-review/`; quoted in A17(c). Nothing adopted; the pause is intact. |
| `superpowers/TEST-QUEUE.md` | The async **use-the-app queue**. `closeout` appends; `session-start` reads it and flags stale entries. Catches the defect class tests structurally cannot. |
| `superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md` | **The governing design for resuming Phase 1** (owner-approved 2026-07-23). Track 1: builder fix for the §2.8 tie-break, rebuild, adopt by structural equivalence. Track 2: cost-function retune (currencies included) on the repaired graph, `known` mechanism, one blind listen. Records the owner's 2026-07-23 decisions in §1. |
| `superpowers/2026-07-23-repair-and-retune-execution-log.md` | Retained execution log for the repair+retune work. Track 1 record, the pre-Track-2 guards, and Track 2 continues it. |
| `superpowers/specs/2026-07-23-track2-preregistration.md` | **The Track 2 pre-registration.** Fixes the factor table, primary outcome, effect sizes, pair set, and the read of every possible result *including the null*, before any arm runs — the commit timestamp is the evidence it came first. Where it disagrees with the repair+retune design spec it says so inline (its §8 indexes the five disagreements); those are design corrections, not scope changes. Also the worked example for two CLAUDE.md rules (dormant-term check, pre-registration gate). **AMENDED 2026-07-23/24 — read §9 first:** eleven amendments (A1–A11). **A1–A7 predate any arm; A8 and A9 were made after the A0 gate ran, and A11 after the P4 pilot** — the ones that postdate a result (still before any factorial arm) — A8 resolves that gate (the floor column stays off; the first-path check is referenced to both P and A0), A9 gives the remaining gates effect sizes. **A10 fixes §5's fame-proxy sample before any label was collected** (an S1/S3 overlap that made the sample 29 not 33, and a false claim that S1's labels already existed). Six amendments (A1–A6) on the analyst review's D1–D3 and D5 — the first three had left arms provably incapable of moving; A6 fixes the fame-proxy scoring rule before the owner's one-shot labels are spent. §9's closing table lists what the amendments do **not** discharge (D4, D6, D7, PR-A, PR-B) with success conditions. Its §7 prerequisites are now P1, P4–P8; **P2 is discharged and P3 is withdrawn — do not execute either. P4 RESOLVED (A11): Deezer `nb_fan` failed §5 (2 pre-registered falsifiers); and Wikipedia pageviews fired the coverage falsifier — so the adopted fame proxy is Wikipedia pageviews with an unmatched interior scored at the fame floor (0), the owner's decision replacing §5's owner-labelling fallback, guarded at d15/d20. See A11 and the repair+retune execution log.** |
| `superpowers/plans/2026-07-23-pre-track2-guards.md` | Six structural guards (G1–G6) that had to land between the pre-registration and the Track 2 sweep. **Executed 2026-07-23; do not execute again.** Outcomes in the repair+retune execution log under "Pre-Track-2 guards". |
| `superpowers/specs/2026-07-25-track2f-toll-full-strength-preregistration.md` | **The Track 2F pre-registration**, committed before any arm ran and **EXECUTED 2026-07-25 — do not execute again.** Governs the ceiling-toll dose-response ladder and nothing else. Reuses Track 2's `C1`–`C4` by citation, unchanged; its `TF` identifier series is namespaced and collision-free. Carries a **continuation trigger with its own effect size** (a rebuild decision is not an adoption decision), and **three structural bounds stated before the run** — the toll tests the ceiling's *cheapness* and never its *ordering*, eight of the 24 endpoints are fully saturated so their first hop is unchangeable at any price, and a static toll cannot address F2's depth clause. Result and figures: `builder/analysis/2026-07-25-track2f-toll-ladder/`; narration in the repair+retune execution log's Track 2F entry. |
| `superpowers/specs/2026-07-25-f1-minimum-stop-design.md` | **The F1 design** (every journey needs at least one stop). Mechanism: run the search as today; if the result is exactly the two chosen artists, run it again with their direct connection forbidden — the existing cost function chooses the detour, so this is not path-quality work. Defines the `stop_rule` wire field (`natural` / `forced` / `adjacent_only`) and cites `findings/2026-07-25-mutual-knn-stranding.md` (`MKS-6`) for why some pairs cannot be given a stop at all. **Implementation has landed** on `f1-min-stop`, per the plan below; still ACTIVE because closure awaits the owner's queued use-the-app check, not because the design is unsettled. |

### Complete

| Document | Covers |
|---|---|
| `superpowers/specs/2026-07-21-phase2-path-quality-design.md` | Phase 2 design. **IMPLEMENTED and adopted 2026-07-22** (`capfix`); §8 risk 4 discharged. Supersedes the roadmap's Phase 2 content only. Its open questions were answered by the sweep — do not read it as a live agenda. |
| `superpowers/plans/2026-07-21-phase2-path-quality.md` | Phase 2 implementation, 16 tasks. **All executed; do not execute again.** Tasks 14–16 were superseded mid-flight by the revised plan below. Several of its inline test fixtures are arithmetically wrong — see the execution log §3 before trusting one. |
| `superpowers/plans/2026-07-22-phase2-revised-plan.md` | The mid-flight amendment governing Phase 2 Tasks 14–16, written by the owner after a full review. **Retained as the record of *why* the last three tasks differ from the original plan** — its §6 is what reclassified C3 into Phase 1. |
| `superpowers/specs/2026-07-19-artist-path-alpha-design.md` | Original alpha design. Still the reference for determinism (§9) and the `APG1` format. |
| `superpowers/specs/2026-07-20-stage3-web-frontend-design.md` | Frontend design. |
| `superpowers/plans/2026-07-19-graph-builder.md` | Builder implementation. Shipped. |
| `superpowers/plans/2026-07-20-path-engine-api.md` | API implementation. Shipped. |
| `superpowers/plans/2026-07-20-stage3-web-frontend.md` | Frontend implementation. Shipped. |
| `superpowers/findings/2026-07-22-doc-audit-context-layer.md` | Documentation audit, navigation layer. |
| `superpowers/findings/2026-07-22-doc-audit-technical-record.md` | Documentation audit, specs and plans. |
| `superpowers/2026-07-25-gate1-clips-and-ux-execution-log.md` | **The record of the Gate 1 clip and frontend-UX work, 2026-07-25** (PR #19). Both clip defects and all four dogfooding UX items. Carries three defects found **in the roadmap itself** — its stated cause for the wrong-artist bug was inaccurate as *located*, and its prescribed fix applied literally would have silenced every card. Also the mutation-check result, the deferred findings with success conditions, and the note that **C1/C2 are fixed but not closed** until the queued use-the-app check returns. Touches no routing, no graph, no weight. |
| `superpowers/findings/2026-07-25-doc-audit-gate1-clips-ux.md` | `doc-auditor` report from the 2026-07-25 closeout (B1). Five findings, four actioned; **its recommendation to expand bare identifiers inside `TEST-QUEUE.md`'s steps was rejected** — `closeout` C1 forbids naming identifiers in owner-facing steps, and the entry correctly has none. Its identifier census and previous-findings check are the parts worth citing. |
| `superpowers/2026-07-25-f1-minimum-stop-execution-log.md` | **The record of the F1 work, 2026-07-25** (PR #23) — every journey now gets at least one stop, or says why it cannot. Identifiers namespaced **`FMS-`**. Carries the four decisions with reasoning, **three defects found in the plan itself** (`FMS-P1` a verification check that could not fail; `FMS-P2` the false premise that adjacency implies the direct edge is cheapest; `FMS-P3` a figure restated under a citation pointing at the wrong identifier), the gate outcomes **including two failed reviews**, and the operational measurements it owns. **Restates no figure it does not own**; the graph figures are `findings/2026-07-25-mutual-knn-stranding.md`'s. Touches no weight, no config knob, no graph. |
| `superpowers/2026-07-25-HANDOFF-f1-minimum-stop.md` | **The CURRENT handoff for Gate 1, 2026-07-25** — written at a clean seam, nothing in flight. Supersedes `2026-07-25-HANDOFF-clip-playback.md` **on F1 only**. Records that F1 is **built but NOT discharged** (its condition is an observation — the queued use-the-app entry), the four things a successor must not get wrong, and what was decided against. |
| `superpowers/findings/2026-07-25-doc-audit-f1.md` | `doc-auditor` report from the 2026-07-25 F1 closeout (B1). Seven High, two Medium. **Its highest-value findings were two fresh identifier collisions in the F1 execution log itself** (`D1`–`D4` against the protocol review's defect series, `P1`–`P3` against the Track 2 prerequisites), caught within the hour and renamed to `FMS-` before the document was cited anywhere — the clearest instance yet of the rule that the audit is not skippable. All seven High actioned. |
| `superpowers/plans/2026-07-23-track1-tiebreak-remediation.md` | Track 1 implementation plan. **Executed 2026-07-23; do not execute again.** Outcomes in `2026-07-23-repair-and-retune-execution-log.md`. |
| `superpowers/specs/2026-07-22-c3-bypass-diagnostic-experiment.md` | C3 diagnostic protocol. **Executed** (Stage 0); Stage 1 superseded by Track 2. Results in the Phase 1 log §3. |
| `superpowers/specs/2026-07-22-c3-known-mechanism-blind-listen.md` | C3 `known`-mechanism blind-listen protocol. **Executed**, verdicts recorded. Results in the Phase 1 log §3.6–§3.9; the A-vs-C re-run condition is the 2026-07-23 spec §4.4. |
| `superpowers/findings/2026-07-26-doc-audit-context-layer-maintenance.md` | `doc-auditor` report from the 2026-07-26 closeout (B1), covering PR #26. Two High, two Medium. Its most valuable finding was the **absence class it was specifically pointed at**: `2026-07-25-HANDOFF-clip-playback.md` §5 still recommended "build F1 next" as a live position, unmarked, in a document whose top banner a mid-document reader never sees — actioned. **One of its findings is refuted and must not be re-actioned:** it carried forward a previous audit's claim that this map lacks a `**Role: AUTHORITATIVE**` marker in its first ten lines; the marker is on **line 3** and has been throughout. Its `export_paths.py` line-reference correction was right and was applied to both `FMS-N1` and `CLM-5`. Its `CLM-7` finding — that naming a gap without enumerating it leaves the successor no way in — produced the four-file table now in that log's §4. |
| `superpowers/2026-07-26-context-layer-maintenance-execution-log.md` | **The record of the skills-and-agents work, 2026-07-26** (PR #26). Identifiers namespaced **`CLM-`**. Touches no code, no graph, no weight. Exists mainly because closeout **D6** requires the standing-layer delta in a retained log rather than only in commit messages — §4 is that record, and it is where `CLM-7` was found: **`memory/` grew 435 → 469 lines with the delta recorded nowhere**, which is exactly the blind spot D6 names `memory/` for. Also carries **`CLM-5`** (a claim this session committed and then corrected: `FMS-N1`'s "adjacency is rare" was an inference presented as fact, and wrong twice over), **`CLM-6`** (`CLAUDE.md` may be wrong that `SKILL.md` **bodies** load unconditionally — if so D6 over-counts; not acted on, it is the owner's call, and the cheap check is named), **`CLM-1`–`CLM-4`** (four decisions taken *against*, which leave no other artifact), and **`CLM-8`–`CLM-10`** (what the session knew that was otherwise unwritten, including the owner's evidence that A5's detached relaunch survives a terminal closing). **`CLM-13` withdraws a claim from this log's own §7**: a file reported as unbacked is deliberately ignored by a `.gitignore` *inside* its directory, which the session could not see because it checked from a branch where that directory does not exist. **Whether a file is ignored is branch-dependent when the rule governing it is branch-scoped** — a trap that recurs across `builder/analysis/`'s dated directories, and one that `git status` alone cannot answer. |
| `superpowers/2026-07-26-stranding-causes-execution-log.md` | **The record of the stranding-causes work, 2026-07-26** (PR #25). Identifiers **`STC-`**. Touches no code, no graph, no weight. Carries the six decisions with reasoning — including **`STC-1` as a defect in the task's own framing** (the "crawl-frontier" cause it named is nearly empty, and the name invites a remedy that reaches almost none of the population it appears to name), and **D-4, the first report being fluent, self-consistent and wrong in its headline** until the source-offered denominator was added. Four gate outcomes, two of them designed to abort. **`STC-6` records a claim this session committed to draft and then corrected**, having run the falsifier it had named as open rather than shipping the open question. The two success conditions live here. |
| `superpowers/2026-07-26-HANDOFF-stranding-causes.md` | **The CURRENT handoff for this branch, 2026-07-26** — a clean seam, nothing in flight. Supersedes `2026-07-26-HANDOFF-low-degree-census.md` **on next actions only**; the census handoff is still the record of its own work. Carries the five claims a well-meaning editor must not revert, what the session knew that was otherwise unwritten, and the open position with what it would do. |
| `superpowers/plans/2026-07-25-f1-minimum-stop.md` | F1 implementation plan, six tasks. **Executed 2026-07-25** on branch `f1-min-stop`; do not execute again. Design: `superpowers/specs/2026-07-25-f1-minimum-stop-design.md`. Task 6's verification script and use-the-app queue entry are the observation that closes F1 — the plan itself says not to mark F1 discharged until the owner runs it. |

### Partly historical — check before citing

| Document | Status |
|---|---|
| `superpowers/findings/2026-07-19-listenbrainz-probe.md` | **Superseded for scoring and normalisation** (it describes per-artist normalisation, deleted in `284366c`). Everything else — endpoint schema, rate limits, the 1,000-artist sitewide cap, the §6d–6f popularity-source eliminations — is still valid and load-bearing. **Read §6d–6f at its actual scope:** it eliminates external **popularity** from the **routing cost terms** (§6e's reason is that `|pop(a) − pop(b)|` and the floor compare two nodes of one graph, so the quantity must be defined on that graph's population), and §6f marks even that *"an alpha decision, not a permanent one"* with a named replacement condition. It says nothing about **fame**, a different currency — an external fame source has already passed a gate (Wikipedia pageviews, pre-registration amendment A11). **External fame sources are gated, not banned;** this row's earlier wording had been read three times as a general barrier. |
| `superpowers/findings/2026-07-21-architecture-review-and-path-baseline.md` | **Superseded for scoring and metrics.** Retained as narrative history of how the reviews unfolded. Its architect and QA findings in §1 (clip 500s, artifact length validation, sync boto3 on the event loop) are **not** superseded and remain actionable. |

### Narrative — never use as context

| Document | Status |
|---|---|
| `how-we-map-similar-artists.md` | A dev-blog journal of the modelling journey, written for humans. **Never cite it, never use it as context, never instruct development from it.** It is not maintained to the standard of project context and will lag reality. Update it when there is major progress worth journalling; correct factual errors when found. |

### External — not project documentation

| Document | Status |
|---|---|
| `reference/` | Third-party material consulted during early planning. **Not project documentation and not for routine context.** See `reference/README.md`. |

---

## Where else information lives

- **Persistent memory** — outside the repo, loaded into every session, at
  `~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app/memory/`. The
  `MEMORY.md` *inside that directory* is the index; each sibling file holds one fact.
  Memory holds **pointers and working preferences, not figures**.
- **`.claude/agents/ml-graph-analyst.md`** — a reusable analysis-only subagent for graph,
  scoring, and metric questions. It has no `Edit` tool by design.
- **`.claude/agents/doc-auditor.md`** — the project-local fork of the global auditor, and it
  **shadows** the one in `~/.claude/agents/` inside this repo (project scope outranks user
  scope). It carries two checks the global one does not: **I**, the identifier census — no
  two load-bearing objects may share a name, and owner-facing text may not use a bare
  letter-number token without its plain-language sentence; and **J**, reads-of-results
  completeness for pre-registrations. It reports and never edits, and it may never propose
  renaming an identifier in a committed document. Dispatched by `closeout` B1.
- **The code is the truth about the code.** Where a document and the source disagree
  about behaviour, the source wins — and the document is a defect to be fixed.

---

## Adding a document

State its role in the first ten lines. Add it to the table above. If it supersedes
something, put a banner on what it supersedes **and mark the superseded claims inline**,
not only at the top of the file — a reader who lands mid-document never sees the banner.
