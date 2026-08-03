# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
Track B's live in `findings/2026-07-30-track-b-cap-selection-results.md` (and its raw
`cb_scores.json`); the adopted graph's stay in
`findings/2026-07-21-scoring-adjudication.md`. Cited, never restated.

**Last updated: 2026-08-02 (night), when the FAME INSTRUMENT WAS FIXED FIRST, per the owner's sequencing ruling: obscurity was REDEFINED as novelty-likelihood (user-relative), `fame_lb_pctl` was ADOPTED as its proxy under a passed validation, and the worldly-fame construct was RETIRED. The owner then ruled a SECOND ordering (2026-08-02, night): the FEATURED-CREDIT FILTER TRACK precedes the cap re-evaluation — the next session's work. The cap re-evaluation pre-registration follows it, written cold by a fresh session, with every owner input already recorded.**

---

## Next

> ## ✅ THE FAME-INSTRUMENT TRACK IS COMPLETE, 2026-08-02 (evening). The cap re-evaluation is UNBLOCKED.
>
> Entry point is the current handoff:
> [`2026-08-02-HANDOFF-fame-instrument.md`](2026-08-02-HANDOFF-fame-instrument.md).
> Reasoning: [`2026-08-02-fame-instrument-execution-log.md`](2026-08-02-fame-instrument-execution-log.md)
> (§1–§9). Governing documents, each with amendments that are part of the record:
> [`specs/2026-08-02-fame-instrument-adoption-preregistration.md`](specs/2026-08-02-fame-instrument-adoption-preregistration.md) (`FAM-`),
> [`specs/2026-08-02-ruler-candidate-shootout-preregistration.md`](specs/2026-08-02-ruler-candidate-shootout-preregistration.md) (`RCS-`),
> [`specs/2026-08-02-novelty-proxy-validation-preregistration.md`](specs/2026-08-02-novelty-proxy-validation-preregistration.md) (`NOV-`).
> Figures live in the committed probe JSONs under
> `builder/analysis/2026-08-02-fame-instrument/` — cited, never restated.
>
> **What stands, in one paragraph.** The owner ruled (2026-08-02): the cap
> re-evaluation's scope includes the data-set switch; its primary outcome is the bypass
> novelty gradient (`REQ-42` shape); and the instrument is fixed first. Under that
> sequencing: ListenBrainz listener counts were validated against *worldly fame* and
> **failed** (`FAM-`, NO ADOPTION); a shootout measured Wikipedia and Deezer also failing
> to order worldly fame (`RCS-`, "no measured candidate orders the tail");
> the owner then **redefined the construct** — obscurity = novelty-likelihood,
> user-relative, audience-pinned (`PRODUCT-REQUIREMENTS.md` Definitions, ratified edit) —
> and the proxy was **adopted under the redefined construct's own one-way validation**
> (`NOV-2`: 15/15 obscure-called artists were novel to him; `NOV-AM1` carries the
> post-result disclosure). **"Fame" in pre-2026-08-02 documents means the retired
> construct; worldly-fame claims are barred from future criteria until an instrument
> exists.**
>
> **⚠ ORDERING RULED BY THE OWNER, 2026-08-02 (night): the FEATURED-CREDIT FILTER TRACK
> runs FIRST — the next session's work — and the cap re-evaluation follows it.** Three
> recorded reasons (design-inputs doc, and the conversation of record): the class is a
> dormant term that activates only in arms that succeed at pushing obscure; the adopted
> gradient currency scores a delivered ghost as a success (obscure-and-novel) while it is
> exactly the bad recommendation the release filter exists to prevent; and the cleanup
> must be held constant across every cell of the comparison — the same held-constant
> principle that censused both drop lists, and the same clean-first-then-compare ordering
> the owner ruled for the drop-rule wiring. Shape: the adopted rule's shape, not a purge
> — a keep-check (commercial-DSP presence + something plays) keeps featured-credit
> artists who are also small real acts (TJ Brown, 8,274 Spotify monthly listeners, is
> the worked keeper case). The detector is offline (primary-artist vs appears-on split
> from the MB release dump on disk); the wiring machinery all exists from the drop rule.
> Rule designed cold; **whether it gets its own small calibration hand-review is the
> owner's spend, flagged not decided.** Evidence: execution log §5/§5a; two worked
> instances (田島賢, TJ Brown) plus the FAM-6 no-page rows.
>
> **After it: the CAP RE-EVALUATION PRE-REGISTRATION, written cold by
> a fresh session, in the adopted currency.** **Its single design-input address is
> [`2026-08-02-cap-reeval-design-inputs.md`](2026-08-02-cap-reeval-design-inputs.md)** —
> the owner's rulings, the candidate families spelled out, the supply×pricing synthesis,
> the blind-listen lineage, the tag constraints, and the labelled hypothesis with its
> cheap first read. Summary of the rulings (execution log §1): candidate families (a)–(d) including the owner-triggered tag-based
> degree limiter and staged router-priced unbounded; coverage as guard-only at ~10,000;
> hubness-rising-with-depth as the per-arm kill; LB similarity the sole source of edge
> existence, tags only re-order/re-weight/remove; router pricing in scope (any pricing
> arm consumes `TB-P5H-7`); gradient claims must exceed 10× the ruler's measured
> quantisation step (`FAM-AM1.3`); the population-vs-descent confound goes in its factor
> table (`FAM-AM1.7`). Design note from the marks: famous-band interiors are ~73% novel
> to the owner (log §8) — the famous band is not a novelty dead zone.
>
> **Owner rulings from this track that must not be re-opened:** no re-read of prior
> fame-scored results; the drop-list population re-scope (`FAM-AM2`); the `RCS-AM1`
> widening (closed five-row list, no third widening); the `NOV-AM1` adoption. Dead
> unless new grounds: Deezer and Wikipedia as fame instruments. Retired, not to be
> re-run: `NOV-1` (mis-designed against its own governing document — log §8).
>
> ---

> ## ✅ THE DROP RULE IS WIRED, AND BOTH POPULATIONS NOW HAVE A DROP LIST, 2026-08-02.
>
> Entry point is the current handoff:
> [`2026-08-02-HANDOFF-tail-drop-and-candidate-census.md`](2026-08-02-HANDOFF-tail-drop-and-candidate-census.md).
> Reasoning: [`2026-08-02-tail-drop-wiring-execution-log.md`](2026-08-02-tail-drop-wiring-execution-log.md).
> Figures live in the probe JSON and are **cited, never restated**:
> `builder/analysis/2026-08-02-candidate-tail-census/ctc_census.json`, `ctc_clips.json`,
> `ctc_droplist.json`.
>
> **Three things landed.** The adopted rule is applied in `pipeline.py` before the mass
> computation (PR #62). The divergence that opened between `build_from_archive` and the
> probe harnesses mirroring it is closed, with a guard test that fires when `BuilderConfig`
> gains a field (PR #63). And the candidate population is censused, so **the cleanup can now
> be held genuinely constant across a comparison of the two data sets** — which was the
> uncontrolled variable that motivated all of it.
>
> **✅ THE BLOCKING ITEM IS CLOSED, 2026-08-02 (latest).** The builder no longer applies one
> drop list to whichever archive it is handed: the list is selected by `config.algorithm` —
> the same value that already chooses the archive sub-tree — and an **uncensused population
> refuses to build rather than borrowing another's list**. Both censused lists ship as
> package data, sha-pinned. Nothing now blocks a build from `ALG-B`. See the deferral table.
>
> **The next substantial step is the CAP RE-EVALUATION PRE-REGISTRATION**, written cold by a
> fresh session. Every input now exists — Track B as measured input, the `WGT-` device
> recommendation, and both drop lists. ~~**What it needs from the owner first, because it is
> his column:** how much better a connection rule must be to justify a rebuild, and whether
> the data-set switch is inside its scope or a separate question.~~ *(DISCHARGED 2026-08-02
> evening — both answered, plus the instrument-first sequencing; see the top section.)*
>
> **Two rulings from 2026-08-02 that must not be re-opened:** the drop rule is **not**
> re-validated on the candidate population (execution log §5 — the decisive point is that no
> second refinement mechanism exists, so a measured rate would change nothing), and the
> wiring **deliberately contradicted** the 2026-08-01 handoff's closing instruction, with
> reasoning in execution log §1.
>
> ---

> ## The LABEL WEIGHTING AND EVIDENCE PROBE (`WGT-`) is COMPLETE, 2026-08-01. **Nothing adopted; the next action is the OWNER'S.**
>
> Entry point is the current handoff:
> [`2026-08-01-HANDOFF-label-weighting.md`](2026-08-01-HANDOFF-label-weighting.md).
> Governing document:
> [`specs/2026-08-01-label-weighting-probe-preregistration.md`](specs/2026-08-01-label-weighting-probe-preregistration.md)
> (committed before any figure; `WGT-AM1` pre-results). Figures:
> [`findings/2026-08-01-label-weighting-probe.md`](findings/2026-08-01-label-weighting-probe.md)
> — **its §0 pair must be quoted together**: weighting moves selection well past the owner's
> materiality line, **and** nothing measured says any weighted journey sounds better.
>
> **Four durable outcomes.** The **style column is closed with a mechanism** (§3a — eleven
> readings, all adverse; the recognizable styles are what similarity already knows).
> **Release-level evidence is excluded as fame-shaped** (`WGT-4` Branch 3; the album-level
> preference stands for a sharper reason than first recorded). **The device recommendation
> on record, as INPUT to a future cap re-evaluation pre-registration only: rarity-weighted
> agreement over `W4`** — a `W4` vocabulary change stays a `TAS-` §8 amendment, the owner's
> trigger, blind listen unspent. And **the owner's two manual records landed as data**: 18
> of 20 no-release-tail artists judged not journey-worthy (`TAIL-SAMPLE.md`, the sharpest
> population evidence yet that the tail is substantially credits-not-acts), and his
> style-vocabulary calibration read (`STYLE-VOCABULARY.md`).
>
> **✅ ONE OF THE TWO CANDIDATE TRACKS IS NOW DECIDED, 2026-08-01 (latest): the
> no-release-tail question is CLOSED and a drop rule is ADOPTED** — keep a
> release-less artist only where a commercial-DSP link exists **and** a clip
> resolves; **7,035 of 7,686 dropped**, list frozen at
> `builder/analysis/2026-08-01-label-weighting/tail_droplist.json`. **✅ WIRED into the
> builder 2026-08-02 (PR #62)** — the rule must not be re-litigated, only applied; a
> second list now exists for the candidate population, see the top section.
> Evidence: `tail_signals.json` (the population census
> and the artist-**type** split — the tail is 7.2% Group against 37.9% for the rest
> of the graph), `tail_clips.json` (what plays, plus a **measured 9.4% `BYP-13`
> wrong-artist rate** in the app's own name-based clip resolver, which is a live
> user-facing defect independent of this decision), `tail_exposure.json` (delivery
> rates). The remaining candidate track is below.
>
> **Both candidate tracks have since moved on.** The no-release-tail decision is CLOSED,
> adopted and now wired; the cap re-evaluation pre-registration is the live next step and
> is described in the top section, which supersedes this paragraph. **`TAS-` Task 8
> LANDED** (2026-08-01) — see the `TAS-` section below; nothing is owed on it.
>
> ---
>
> ## The RELEASE-TAG COVERAGE PROBE (`REL-`) is COMPLETE. **`REL-1` PASSED — release aggregation clears `COH-2`'s 50% bar in the obscure tail. Nothing adopted. The next action is the OWNER'S.**
>
> Entry point is the current handoff:
> [`2026-08-01-HANDOFF-tas5-routing.md`](2026-08-01-HANDOFF-tas5-routing.md).
> The `REL-` handoff below is **superseded on next actions** and stays authoritative for its
> own probe's internals.
> [`2026-07-31-HANDOFF-release-tag-coverage.md`](2026-07-31-HANDOFF-release-tag-coverage.md).
> Governing document:
> [`specs/2026-07-31-release-tag-coverage-preregistration.md`](specs/2026-07-31-release-tag-coverage-preregistration.md)
> (`REL-`) — **read its §8 first**; both amendments correct the same conflation and
> **`REL-AM2` was written after the headline figure was known and says so.** Figures:
> [`findings/2026-07-31-release-tag-coverage.md`](findings/2026-07-31-release-tag-coverage.md).
>
> **A parallel investigation commissioned by the owner, not a continuation of `TAS-`.** It
> asked whether aggregating an artist's *release* tags labels the artists carrying no genre
> label today. Census over all 74,193 artists from local dumps; no API, no sampling.
>
> **`REL-1` and what cuts against it must be quoted together** — the same pairing rule as
> `COH-2`/`COH-3` and `FPC-2`/`FPC-9`. The bar cleared and the coverage gain lands in the tail
> (`REL-6` not adverse); **but `REL-3`'s fidelity median is modest, its ratio bar is a
> degenerate pass, and a large minority of the unlabelled tail is reached by neither source.**
> Read the findings' §0 and `REL-3` together before acting.
>
> **`REL-4` inverted the design's framing:** Discogs — the arm expected to be awkward — is the
> stronger source in the obscure tail, and the two independent sources agree on at least one
> label for nearly every artist they both reach. That agreement is the strongest thing in the
> record.
>
> **Nothing adopted, no criterion fixed, no weight, default, currency or vocabulary changed,
> no rebuild, no blind listen spent. `TAS-` §1's vocabulary is UNTOUCHED** — a passing frame is
> a *candidate* for a `TAS-` §8 amendment, never an enactment. **It says nothing about whether
> `TAS-6` would flip**, which needs a rebuild this probe does not license.
>
> ---
>
> ## The TAG DISCRIMINATION PROBE (`TAS-`) is COMPLETE, 2026-08-01 — all eight tasks. **NEITHER ARCHITECTURE HAS AN ADOPTION CASE.** Nothing is owed; the next action is the OWNER'S.
>
> **Findings of record, and the entry point for anything `TAS-`:**
> [`findings/2026-07-30-tag-discrimination.md`](findings/2026-07-30-tag-discrimination.md)
> (Task 8, written 2026-08-01 latest). **It owns the `TAS-` figures** — cite it by section and
> never restate a number from it. **Its §0 must be quoted whole:** both kill bars were cleared
> **and** neither architecture has an adoption case, decided by different pre-registered
> clauses. The premise the thread rested on is **confirmed** — genre agreement discriminates,
> and is not redundant with similarity — so neither null is "the graph already knew".
>
> **⚠ Execute the routing side ONLY from
> [`plans/2026-07-31-tas5-routing-execution-plan.md`](plans/2026-07-31-tas5-routing-execution-plan.md).**
> The older probe plan's Tasks 5, 6 and Task 7's routing halves are **superseded and contain a
> trap**: Task 7 Step 5 instructs the executor to make the randomised-label red check fire and
> stop if it does not — the check `TAS-AM3` **withdrew as unachievable**. Do not follow it.
>
> **The build-time side is barred** — `TAS-6`'s **selection** half is ADVERSE, and §5 says that
> bars an adoption recommendation whatever else shows.
>
> **The router side survives its kill bar on a change that is not about genre.** `TAS-5` did not
> kill: journeys change at every non-zero weight in every class. **But `TAS-AM5c`'s null control
> FIRED** — permuting labels among labelled artists reproduces nearly all of the same change,
> far above the pre-registered clause. **Per `TAS-AM5c`, `TAS-5`'s change CANNOT be attributed
> to genre structure, and every `TAS-5` figure must be quoted carrying that caveat.** Both
> instrument checks passed first (`TAS-AM5a` equivalence, `TAS-AM5b` liveness), so this is a
> real null and not a broken harness.
>
> **⚠ `TAS-6`'s ROUTING half is VACUOUS and must not be read as a pass.** Its baseline count of
> sub-decile interior artists is **zero** — production routing delivers no bottom-decile artist
> mid-journey on any drawn pair — so a 10% reduction cannot be measured and "not adverse" is a
> division-by-zero artifact. That zero is itself a corroboration of `DD-F1`.
>
> Figures: `tas_route.json`, `tas_route_guard.json`. Reasoning: execution log **§16**.
>
> **`TAS-AM4` evaluated the `REL-` enriched frame as a CANDIDATE and licensed a recommendation only.** No candidate is killed and reach rises substantially, but the signal measurably blunts — and that fall held on a fixed population, so it is real rather than composition. **§1's vocabulary is UNCHANGED.** Figures: `tas_frame_eval.json`; reasoning: execution log §13. **`tas_frame_split` has since decomposed that result** — the Discogs **style** column causes the blunting, not the coarse genre column, and `W4` dominates `W6` on reach, spread and redundancy alike (execution log §15). **`W6` must not be the frame any future amendment names.**
>
> Current handoff:
> [`2026-08-01-HANDOFF-tas5-routing.md`](2026-08-01-HANDOFF-tas5-routing.md). The two 2026-07-31
> handoffs and the 2026-07-30 one remain authoritative for their own tracks' internals only.
> Governing document is the pre-registration
> [`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md)
> (`TAS-`), which **wins wherever the plan disagrees**. **Read its §8 first:** `TAS-AM1`
> withdraws `TAS-4`'s original bar as **false** and `TAS-AM2` fixes the substrate per
> criterion.
>
> **The owner picked up the third coherence strand on 2026-07-30** — tag-aware neighbour
> selection, parked below until then. The probe tests the assumption both candidate
> architectures share: whether genre agreement discriminates between the candidates an
> artist already has, or merely restates the similarity score. **Nothing adopted, no
> criterion fixed, no weight, default or currency changed, no rebuild, and no blind listen
> spent.** Two owner decisions taken and recorded: the goal is **coherence, not obscurity**,
> and `TAS-4`'s materiality bar is **1% edge turnover**.
>
> **The architecture question — build-time selection vs router-side pricing — was left OPEN
> for the probe to inform, and the probe has now answered it: NEITHER side has an adoption
> case.** `TAS-4` has now answered the
> build-time half and **did not kill it** — figures in
> `builder/analysis/2026-07-30-tag-discrimination/tas_select.json`, reasoning in §9 of the
> execution log. **`TAS-5` (the router half) has now RUN** — see the top of this section. §5
> requires the two to be read together, and they now can be: the build-time half is barred by
> the adverse guard, and the router half's change is not attributable to genre.
>
> **⚠ TWO STOP-LEVEL RESULTS, both 2026-07-30, both recorded in execution log §10.**
>
> **1. `TAS-6` is ADVERSE** (*"does this make the app worse at reaching unknown artists"*).
> Famous→obscure connections fall at every λ and cross the 10% bar at the top two. Per the
> pre-registration's §5 this **bars any recommendation to adopt, whatever `TAS-4` and `TAS-5`
> show** — it is not outweighed by `TAS-4` having survived. Its denominator is thin; read
> `tas_guard.json` before judging materiality, and note that **no bar may be revisited now
> that a result exists**.
>
> **2. ✅ The red check is RESOLVED — `TAS-4`'s figures ARE believable.** The original check
> was **withdrawn as unachievable** by **`TAS-AM3`** (§8): a Jaccard-overlap device cannot
> produce large change on a randomised label frame, because randomising labels destroys
> overlap rather than randomising it. Its replacement, **`TAS-AM3a`**, passes at every λ —
> the ranking path is **bit-identical** to `td_turnover`'s verified one and reproduces the
> committed `TD-2` figures to five decimals. **Discharged for the SELECTION side by `TAS-AM3a`; the ROUTING
> side is discharged separately by `TAS-AM5a`/`b`, both passed 2026-08-01** — `TAS-AM3`'s
> scope clause could not supply it, because its pass conditions live on the capture while
> `TAS-AM2` puts `TAS-5` on the artifact.
>
> **`TAS-AM3b`'s null control corrected the withdrawn check, against tags** — holding fixed
> which artists are labelled roughly doubles the null, so the withdrawn version had
> overstated how much of `TAS-4`'s turnover came from genre structure. Attribution is still
> not unsafe. **Read `TAS-AM3b`'s clause before quoting the ratio: below the threshold it is
> reported and nothing more, and no claim about tags is licensed by it.**
>
> **`TAS-AM3` is the first amendment appended AFTER results existed** — it says so at its
> head and names the hazard. Read that disclosure before relying on it.
>
> **Tasks 5–7 are DONE (execution log §16), and Task 8 landed 2026-08-01 (latest) — the
> findings document is `findings/2026-07-30-tag-discrimination.md`, its owner-facing read is
> execution log §17, and no probe task remains unrun.**
>
> The coherence tag probe, Track B and the fame-proxy probes are **COMPLETE and their
> records are untouched and remain accurate**; the coherence-tag-probe handoff is superseded
> **on next actions only**.
>
> **Coherence tag probe** (branch `coherence-tag-probe`) — a one-day falsification
> probe of the §7 coherence thread, owner-directed. **Its kill gate fired: tag/genre
> coverage thins in the obscure tail the way Wikipedia's does, and the pre-registered
> retrodiction against the 11 blind verdicts was never run — the verdicts remain an
> unconsumed falsifier.** Findings:
> [`findings/2026-07-30-coherence-tag-probe.md`](findings/2026-07-30-coherence-tag-probe.md)
> (`COH-`). **`COH-2` (the band-level kill) and `COH-3` (the delivered-route
> counterpoint) must be quoted together — either alone gives the wrong answer**, the
> same pairing rule as `FPC-2`/`FPC-9`. Nothing adopted, no criterion fixed, neither
> open decision below settled.
>
> **Track B** — results of record:
> [`findings/2026-07-30-track-b-cap-selection-results.md`](findings/2026-07-30-track-b-cap-selection-results.md).
> The two parked decisions below now have the pre-registered recommendation input it
> existed to produce; **both still owe a blind listen (`REQ-38`) regardless of the
> numbers.**
>
> **Fame-proxy coverage** (branch `fame-proxy-coverage`, PR #53) — descriptive scope
> probes, **nothing adopted, no criterion fixed, no currency changed, Track B untouched**.
> Findings: [`findings/2026-07-30-fame-proxy-coverage.md`](findings/2026-07-30-fame-proxy-coverage.md)
> (`FPC-`). **Read its §0 first: it corrects the premise the work began from** — the
> Wikipedia floor is *not* actively corrupting fame-currency measurements, and **no Track 2
> or Track 3 verdict changes.** What it did establish is a **sequencing** question, now
> parked below.
>
> **Nothing is queued for a working session.**

**The requirements baseline is unchanged since 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (`REQ-`) governs where it and
[`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) disagree (its §10 lists the
disagreements). **`DD-F1` remains a defect, not an accepted limitation** — Track B's `R2`
read measured where it can and cannot be moved; the results note owns that reading.

## PARKED — owner's explicit decision; his trigger, never a session's

- ~~**Whether the fame instrument is fixed BEFORE or AFTER the graph work**~~ — **RULED
  AND DONE 2026-08-02: before, and it was.** The `FPC-2`/`FPC-9` pairing rule stays for
  reading that record. Struck, kept for the record.
- ~~**Whether a currency change re-reads prior fame-scored results**~~ — **RULED
  2026-08-02: NO re-read.** Prior results stand in their measured currency;
  cross-currency comparisons barred. Struck, kept for the record.
- **The coherence thread** — execution log
  [`2026-07-30-fame-proxy-coverage-execution-log.md`](2026-07-30-fame-proxy-coverage-execution-log.md)
  §7. **Its instrument half was probed 2026-07-30 and the kill gate fired** (`COH-`,
  above): §7's own warning — tag coverage thins in the same tail — measured true at
  band level, so no tag-based instrument gets built on this artifact's population as
  measured. What remains parked, still the owner's trigger: the **structural half**
  (the cost function assumes coherence is additive along edges while
  `PRODUCT-REQUIREMENTS`'s second clause is not — untouched, unproposed), and any
  **reopening of the instrument line on a route-population gate** (`COH-3`'s 74.2%
  on delivered interiors is the recorded argument; a reopening is a new
  pre-registration designed cold, never a re-read of the fired gate).
  **⚠ The third strand is NO LONGER PARKED — the owner picked it up 2026-07-30 and it is
  the live work; see "Next" above.** Its caveats below were all carried into the
  pre-registration rather than lost: the reordering limit is stated in `TAS-4`'s bound, the
  self-audit circularity is why the track has no offline scoreboard and ends at a blind
  listen, and the Track-B-shaped cost is why `TAS-` measures before proposing a rebuild.
  **One caveat was measured and turned out to understate the case:** the strand assumed
  selection "reorders candidate lists", which is true — but `TD-2` measured that reordering
  converts to roughly twice as much map change as per-artist counting suggests, because
  every swap also *creates* a connection. Retained below as written.
  *(Original text, superseded on status only:)*
  **A third strand, owner-raised 2026-07-30 after the probe and explicitly flagged
  worth a future session: tag-aware neighbour SELECTION at build time, at the top of
  the graph.** The probe's kill was about *scoring paths*; selection lives where
  candidates are many and labels near-total (top bands 94–100%, `COH-2`), and barely
  operates where labels are dark — the coverage failure and this use are close to
  complementary. Three caveats travel with it: it *reorders* candidate lists and
  cannot add famous→obscure supply (that stays with candidate supply and router
  pricing); tags spent on construction are spent as an evaluator — §7's self-audit
  circularity in new clothes, leaving the 11 blind verdicts as the only independent
  check; and picking it up is Track-B-shaped work — a selection-rule change, so a
  rebuild, a pre-registration with a factor table, and a blind listen (`REQ-38`).
  `COH-5` makes the data side cheap (~47 min for a full tag frame).
- **The cap-rule decision for any rebuild** — Track B's `R1` is its input; adoption of
  any rule owes the blind listen.
- **`ALG-B` adoption** — Track B's `R0`, `R2`, `R3` (`CRS-C6`) are its inputs, beside
  `RC-R1`'s stranding figures; adoption retires the existing path-quality figures and
  owes a blind listen (`REQ-38`).
- **The router-side pricing track** (plan §0 ruling 2) — `R2`'s `ALG-E` null is its
  motivating evidence: the quota edges exist and production weights decline them. Needs
  its own pre-registration, which must consume `TB-P5H-7`.
- **The candidate-pool product decision** — whether a shortened-but-obscure bypass
  candidate (Track 3's DD-A2 or a TB arm) ships at all.
- **The one-statistic cross-track recompute** that must precede any DD-vs-TB comparison.
- **Any blind listen on a router-only candidate** — deferred to the full stack.
- **Re-evaluating bounded-degree itself** (router-priced unbounded graphs) — Track B's
  `UC` reference rows now give it measured baselines; his trigger; owes its own blind
  listen.

**Still owed by the owner:**

1. ✅ **The use-the-app test — DONE 2026-08-02.** The redesign entry was run in full against
   `https://musicapp.cmiller.io`, desktop and phone. Everything passed; journeys he knows well
   were **unchanged**, which was the check that mattered. One incidental finding worth
   carrying: **the loading screen is often too fast to see**, so nothing should be measured or
   redesigned on the assumption a user experiences it.
2. ✅ **The iPhone script — DONE 2026-08-02, and it settled a Gate 3 blocker.** All three
   questions clean: clips play, the bottom bar clears the home indicator, artist-name typing is
   unaffected. **`G3-F2` is FALSIFIED** — see the gate table below.
3. ✅ **The `--prune` publish pass — DONE 2026-08-02.** Two orphaned assets from the
   pre-redesign build deleted; live site verified afterwards. See the deferral table for the
   pre-flight a successor should repeat.

**Nothing is owed by the owner as an action.** What remains for him is decisions only —
merging PR #66 (the fame-instrument branch), and the triggers named in the parked list
and the deferral table.

**Nothing is queued in [`TEST-QUEUE.md`](TEST-QUEUE.md).** Its newest entry (2026-08-02
evening, the fame-instrument track) is N/A — nothing app-facing changed and nothing is
running. The prior entry was checked by the owner on 2026-08-02 and came back clean — the
live site builds journeys and plays clips after the `--prune` pass. Everything else there
is dormant until a graph is rebuilt.

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). **One blocker removed 2026-08-02: `G3-F2` is FALSIFIED** — HIGH, "blocking if confirmed", and the review named the deciding test (*"one tap on a real device confirms or kills it"*). Clips play on a real iPhone. ⚠ **Read what that does not mean:** the code was NOT changed to achieve it — `usePlayer.ts:49` still awaits the URL before `player.play(url)` at line 60, which is exactly the pattern the review flagged. The finding's *description* was accurate; only its *consequence* is removed, and it rests on iOS's current tolerance rather than on the code being correct by construction. **Do not cite this as "the iOS play path is correct."** The rest of the blocking set (`G3-A1`–`G3-A4`, `G3-S1`–`G3-S3`, `G3-Q1`, `G3-Q2`, `G3-F1`) is untouched. |

## Closed — do not re-plan or re-investigate

- **Track B's cells and reads are closed.** Builds are byte-deterministic and the raw
  outputs are committed — do not re-run cells to "check"; re-running is only ever
  instrument work under a harness change that re-fires `CRS-G1`.
- **`R2`'s `ALG-E` null must not be cited as "the quota rule cannot fix `DD-F1`"** — it
  is "the router declines the quota edges *at production weights*"; the pricing track
  above owns the difference.
- **`PS100` ≡ `MK100`, byte-identical, both archives** (`LBS-3`) — one graph, never two
  data points. And **`proximity_select` at bound 50 measured materially worse on
  stranding on both archives** — do not re-propose it as a candidate without new grounds.
- **The pair-set attrition decision is closed** — the `× lower` classes are unreadable
  per `CRS-G3` at the committed draw; a redraw is a new §8 amendment designed cold, the
  owner's trigger if he wants obscure-endpoint path reads.
- **The source `algorithm` parameter is a CLOSED ENUM of six values** (`CS-P0e`);
  `limit` ≤ 100, `threshold` ≥ 10, production already at both edges. Parameter semantics
  are `LBS-`'s, from source (`findings/2026-07-30-lb-algorithm-semantics.md`).
- **`CS-P0c` must not be cited as "no cap rule can fix `DD-F1`"** — scoped to own-list
  selection; the prereg's §0 table owns per-family bearing.
- **The `--target`-capped trial crawl is RETIRED for `AS-H2`** (only).
- **Track 2, Track 2F and the ceiling toll are exhausted nulls. Do not re-run any.**
- **Track 3's and Track 3b's results are closed** — do not re-run their arms or
  re-litigate TB-R2.
- **The routing-side toll family is closed for descent claims**; any explicit
  length-preserving constraint is a new device needing its own pre-registration
  consuming `TB-P5H-7`.
- **Loosening the both-ways cap without a simulated bound was rejected (`MKS-5b`) — and
  Track B is that simulation, now RUN.** Its results note is the record.
- **Famous-pair first-path fame is barred as a scoring criterion** (PLA-R1); Track B's
  prereg resolved its applicability and `CRS-C5` measured presence, not fame.
- **The nameless-artist question is decided** (drop; implemented, `GR-1`).
- **The builder-side p99 rescale stays parked** (DD-R2's trigger never fired).
- **The OneDrive migration is COMPLETE**; the old tree is an archive.
- **`G3-A5`, `G3-A2`, `G3-S7`** closed as recorded; **`G3-A3` does not fire**.
- **`RMD-6`, `RMD-11`, `RMD-12`, `RMD-13`, `FRO-1`, `FRO-4`**, the `DEP-33` blockers, the
  Gate 1 clip work, **Track 1**.
  - ⚠ **One exception:** `BYP-13` — a card playing a clip by a *different artist of
    the same name*. Not path work and not inside any pause. **A fix is BUILT as of
    2026-08-02 and is INERT until a rebuild** — the builder carries MusicBrainz-recorded
    Deezer artist ids in the APG1 metadata blob and the api resolves by identity before
    falling back to name search. **The defect is unchanged in the running app**, which
    serves a pre-2026-08-02 artifact with no ids. It is *reduced*, not closed — see the
    link-quality row in the deferral table.

## Must not be changed, and each has a reason

- **`max_size=2` (`stack.py`)** — the **cost ceiling**, the only automatic spend control.
- **App Runner is excluded from CDK tagging** — tagging forces a replacement that cannot
  succeed; pinned by `test_app_runner_is_deliberately_left_untagged`.
- **The ACM validation `CNAME` at Cloudflare** — delete it and the certificate silently
  fails to renew in ~13 months.
- **The rate limit is `10 / 10 s`, not `30 / 60 s`** — see `infra/README.md` §1a.
- **The `acceptance.py` blank-name check** — do not weaken it to unblock a build. And
  `GRT-P2` stands: the guard is blind to a severe famous-artist collapse at any scale;
  strengthening it is an unclaimed design question, not part of Track B.
- **The mirror's two device knobs (`w_known_ramp_pctl`, `w_known_thresh_pctl`) stay 0.0.**
- **`BuilderConfig.algorithm` still carries `contribution_5`**; changing it *is* the
  re-crawl decision. Likewise `max_neighbours_per_artist = 50` and
  `cap_strategy = "mutual_knn"` — **Track B was analysis-only and moved no default.**

## Deferred, with conditions

| Finding | Condition |
|---|---|
| ✅ **Track B runs and reads** (`CB-5`/`CB-6`) | **DISCHARGED 2026-07-30** — run to completion; results note is the record. Struck, kept for the record. |
| ✅ **`CRS-A5` endpoint re-verification** | **DISCHARGED 2026-07-30** — one request at scoring time, 200, companion delivered descriptive-only. Struck. |
| **`FPC-9`'s falsifier — an obscure-endpoint pair set for floor reach** | **If any realistic candidate device reaches materially more obscurity than production.** `FPC-9` used Track 3's `LIMIT` arm, a ceiling rather than a shippable route, and rests on 62 interiors from one arm on twelve pairs. Falsified by a device that reaches more obscurity *without* approaching `LIMIT`'s interior percentiles. |
| ✅ **`PRODUCT-REQUIREMENTS.md`'s Definitions section does not quantify the proxy's blindness** | **DISCHARGED 2026-08-02 — the condition fired and the edit landed.** The currency decision was made; the Definitions entry now carries `FPC-3`/`FPC-9`'s extent inside the retirement paragraph of the worldly-fame construct (owner-ratified edit). Struck, kept for the record. |
| ✅ **Full-graph MBID-keyed fame values** (`fp_fame_mbid --build`) | **CLOSED 2026-08-02 — the path is known-unreachable, not deferred again.** The currency decision adopted the LB proxy and **retired the worldly-fame construct**, so the condition ("adopts the MBID-keyed proxy") can never fire. Reopening requires a worldly-fame instrument to exist at all, which `RCS-` measured as currently unachievable. Struck, kept for the record. |
| ✅ **MusicBrainz tag/genre coverage as a coherence instrument** | **DISCHARGED 2026-07-30** — the coherence tag probe ran exactly this check and its kill gate fired (`COH-2`, vocabulary-robust per `COH-6`); the retrodiction stayed unrun. Struck, kept for the record. |
| ✅ **Adding `analysis` to builder's `testpaths`** | **DECLINED BY THE OWNER 2026-08-01 — closed, not deferred again.** Its condition fired at the closeout retiring the `TAS-` probe, and he ruled: **frozen code should not be tested by default.** `testpaths` stays `["tests"]` (`builder/pyproject.toml:25`); probe tests run only when a directory is named explicitly. The reasoning is durable rather than circumstantial — probe tests guard research code nothing ships and nobody will edit again, so collecting them would gate unrelated builder merges on a frozen artifact's committed JSON or a vanished scratch capture. **A future probe does not reopen this**; it inherits the same answer. Struck, kept for the record. *(This row carried a count of "34" until 2026-07-30; it was stale, and the count was never this document's to own — read it off `pytest analysis/ -q`.)* |
| **Replacing mutual k-NN with a tag-based degree limiter** | **Owner-raised 2026-07-30, ruled SEPARATE and explicitly NOT ruled out.** Needs its own pre-registration designed cold; mixing it with `TAS-` would make every attribution ambiguous. Track B's `R1a` corroborates the premise — reciprocity in isolation at k = 100 was null on both archives. **Condition: if the owner triggers it**, as with every other cap-adjacent decision. |
| ✅ **`TAS-4` is not believable until the red instrument check runs** | **DISCHARGED 2026-07-31 for the SELECTION side** — the original check was withdrawn as unachievable (`TAS-AM3`) and its replacement `TAS-AM3a` passed at every λ. Struck, kept for the record. |
| ✅ **`TAS-5` is not believable until the ROUTING-side red check runs** | **DISCHARGED 2026-08-01.** `TAS-AM3`'s scope clause could not supply it — its pass conditions live on the pre-cap capture while `TAS-AM2` puts `TAS-5` on the artifact — so `TAS-AM5` constructed one, written **before any routing figure existed**. `TAS-AM5a` (equivalence) and `TAS-AM5b` (liveness) both passed on the full draw. Struck, kept for the record. |
| ✅ **Task 8 — the `TAS-` findings document is unwritten** | **DISCHARGED 2026-08-01 (latest)** — `findings/2026-07-30-tag-discrimination.md`, with the owner-facing read in execution log §17. Both conditions honoured on the page: `TAS-AM5c`'s caveat is carried at `TAS-5`'s section head and repeated at its figures, and `TAS-6`'s routing half is marked **VACUOUS** with its mechanism (`tas_guard.py:111`) rather than read as a pass. Struck, kept for the record. |
| **`TAS-6`'s routing half is unmeasurable on the committed draw** | **If, and only if, an obscure-endpoint draw is ever made for routing.** Its baseline is zero sub-decile interior artists, so no reduction can be measured and "not adverse" is a division-by-zero artifact. Not a defect of the run — a property of what production routing delivers, and a corroboration of `DD-F1`. |
| ✅ **Rarity-weighted agreement is a measured candidate device** | **MEASURED IN FULL 2026-08-01 by the `WGT-` probe** — the single-frame diagnostic became a 15-cell grid; the `WGT-` findings own the result and the device recommendation (rarity over `W4`, input-only). The trigger half stands: adopting any weighted device changes §1, an §8 amendment, the owner's call. Struck as a deferral, kept for the record. |
| **`W4` was never evaluated as a `TAS-` candidate frame** | **If the owner triggers a vocabulary change.** Now further supported: the `WGT-` grid evaluated `W4` under two weighting schemes and it remains the dominant frame; the style column is closed with a mechanism (`WGT-` findings §3a). A `W4` adoption would still be a new §8 amendment designed cold. |
| **Discogs alias expansion** | **If a frame amendment is ever triggered.** Discogs attribution goes through one MB-sourced ID; alias releases are invisible, so every Discogs figure is a lower bound (identical in every cell — no comparison threatened). `discogs_20260701_artists.xml` is already on disk; expansion is an exact ID join, no download, no name matching. |
| **The Discogs `masters` export** | **Iff Discogs support-counting is ever wanted.** Irrelevant to every presence-based use (unions are reissue-proof by construction) and would *lose* tail coverage (single-version releases often have no master); but it is the album-grain collapse that avoids the pressing confound (`WGT-4c`) if Discogs evidence counts are ever proposed. **Owner spot check 2026-08-01 (DSotM, 1000+ releases):** individual pressings accrete stray labels beyond the master's (`art rock`, `classic rock`, `pop rock` beside the master's two) — so the release-built frames carry mild curatorial noise a master build would not, the flip side of the coverage loss. Recorded; changes no measured verdict. |
| ✅ **The no-release-tail product decision** | **DECIDED BY THE OWNER 2026-08-01 — a drop rule is ADOPTED and the list is frozen.** Keep a release-less artist only where a commercial-DSP link exists **and** a clip resolves; **7,035 of 7,686 dropped, 651 kept** (`builder/analysis/2026-08-01-label-weighting/tail_droplist.json`, drop-list sha256 `d876c7ba…`). Struck as an open question; the wiring row below is what remains. |
| ✅ **The drop list is wired into the builder** | **DONE 2026-08-02, PR #62.** `drop_no_release_tail` (default on) applies the frozen list in `pipeline.py` beside the nameless drop, before the mass computation; the list ships as package data pinned by sha256. All three carried constraints are commented at their definitions. **The flag is an experimental control, never a shipping option** — it exists so a build-side experiment can hold the drop constant in a factor table, and so frozen probes can be era-pinned. Struck, kept for the record. |
| ✅ **One list, applied to any archive** | **DISCHARGED 2026-08-02 (latest) — both halves, the per-archive list and the refusal.** The list is selected by `config.algorithm`, which already decides which archive sub-tree a build reads, so a build's algorithm *is* its archive identity and no new `BuilderConfig` field was needed (the mirrors guard stays quiet, and `PERMITTED_ALGORITHMS[1]` still resolves for every frozen probe). Both censused populations ship as sha-pinned package data — `ALG-E` 7,035, `ALG-B` 9,501. The four **uncensused** algorithms raise `NoDropListForAlgorithm` rather than borrowing a list; the refusal is conditional on `drop_no_release_tail` being on, so the era-pinned probes that build uncensused populations with it off are untouched. **The magnitude of the averted defect, since the row understated it:** the two lists share only **2,712** MBIDs, so applying today's to an `ALG-B` build would have dropped **4,323** artists that rule keeps *and* missed **6,789** it drops. Mutation-tested — reinstating the old one-list behaviour turns five tests red. Struck, kept for the record. |
| ✅ **Whether the drop rule needs re-validating on the candidate population** | **RULED BY THE OWNER 2026-08-02: NO, and the reasoning is durable rather than circumstantial.** The rule does not rest on which artists are in the graph. It rests on three claims that hold for any population: release-less artists are generally poor recommendations to surface; the reason not to drop *all* of them is that MusicBrainz is incomplete, not that they are good (**both keepers in his 20 were real artists MB had simply failed to document**); and the DSP-link-plus-clip check is the best false-positive catcher available. **The decisive point is the one that closes it:** a measured false-positive rate on the candidate would change nothing, because no second refinement mechanism exists — so the follow-up question ("and then what?") has no answer, and dropping a large number of bad recommendations is a strong trade even carrying some false positives. **A future session must not propose a second hand sample on transferability grounds.** Distinct from the *magnitude* question — if a candidate tail were a far larger share of its population, that is a different-sized intervention, and `analysis/2026-08-02-candidate-tail-census/` measures it. |
| ⚠ **The Deezer id path inherits MusicBrainz's link accuracy — it is not "strictly better"** | **Before `BYP-13` is described as closed, and before any figure is put on the improvement.** MusicBrainz sometimes links an artist to a *duplicate* Deezer page rather than the real one. Two observed by hand: Radiohead's recorded link has 473 followers and **0 albums** (so it serves nothing and falls back to name search — fails safe), and Orbital's has **20 followers and does serve tracks** — where the id path would replace a correct name-search result with a worse one. Sampled over 60 delivered artists carrying an id: **59 of 60 serve a track from the id**, and 6 of those are thin pages, of which most are *genuinely* obscure artists rather than duplicates. So the new failure mode is real but small against the 9.4% / 6.1% it removes; **the net is clearly positive and the direction of every individual case is not guaranteed.** A session must not restate this as "strictly better by construction" — that claim was made on 2026-08-02 before this was measured, and is withdrawn. Cheap targeted mitigation if wanted: validate links for the top popularity decile only (~7,400 lookups), where a duplicate is both most detectable (expected follower count is high) and most damaging (those artists are delivered most often). |
| ✅ **The Deezer id map covers only the adopted population** | **DISCHARGED 2026-08-02 — the map now covers the UNION of both populations**, so the cap re-evaluation cannot trip a coverage condition mid-experiment. 93,067 artists (adopted 74,193 + `ALG-B` 68,467, overlapping), **39,465 ids**. The `ALG-B` graph used is the 2026-07-30 full build (sha `d008a2b5…`, manifest-verified), which predates the drop rule and the nameless fix and is therefore a **superset** of any final `ALG-B` build — safe by construction, since an MBID absent from a build is a no-op, and the same reasoning the candidate tail census used. Adopted-population coverage is unchanged at 34,988 / 47.2%, which is the consistency check that the union did not perturb it; `ALG-B`-only artists cover 4,477 of 18,874 (**23.7%**), consistent with that population being deader. An artist outside the union still falls back to name search. Struck, kept for the record. |
| **The Deezer id map is a dated snapshot and will age** | **Whenever it is next questioned; no automatic trigger exists.** Frozen 2026-08-02 because `build_from_archive` is offline by a hard rule and spec §9 requires byte-identical builds. A link that goes stale 404s, which `_get` treats as a miss rather than a refusal, so the card degrades to name search rather than going silent (pinned by `test_a_stale_id_falls_back_to_name_search_rather_than_giving_up`). Refreshing is a deliberate act with its own decision. |
| **The featured-credit residual class in the release filter** — artists kept because credits count as release groups, while having no primary-artist existence (two worked instances: 田島賢, TJ Brown; mechanism closed via `LBS-1`'s 0.25 featured weight) | **✅ TRIGGERED BY THE OWNER 2026-08-02 (night) and ORDERED FIRST — it precedes the cap re-evaluation; see the top block.** Designed cold as a new product decision extending the adopted rule, never re-litigating it. Detector is cheap and offline: the primary-vs-appears-on split from the MB release dump on disk. Evidence: execution log §5/§5a. |
| **Known-press telemetry as the novelty proxy's long-run validator** | **When enough `known` presses exist to read.** Named in the Definitions entry and `NOV-` §3; nothing to build now. |
| **A worldly-fame instrument does not exist** | **Accepted; claims in that currency are barred until one does** (Definitions ruling). Reopen only if a product need for worldly fame appears — the `RCS-` corpus and its committed hand values are the reusable starting point. |
| **The TJ Brown late hand read** (8,274 monthly listeners, ruler 218) | **Usable by a future corpus at design time only** — never a post-hoc addition to a read set (log §5a). |
| **`REQ-Q1`'s telemetry revisit condition FIRED and was not taken** | **The owner's call, separately from anything here** — whether live telemetry converges on the offline currency now that a per-mbid source exists. Flagged in the requirements text itself. |
| **Apple/iTunes ids are measured but not shipped** | **If the residual `BYP-13` rate after the Deezer path is judged too high.** Adding them takes delivered-artist coverage from **92.9% to 94.1%** of card impressions — 1.2 points — and the Apple-id-to-iTunes-lookup path has never been run here, unlike the Deezer one (`tail_clips.py:137`). Figures: `builder/analysis/2026-08-02-dsp-ids/dsp_ids.json`. |
| **A blind listen isolating the post-drop graph** (`REQ-38`) | **ANSWERED BY THE OWNER 2026-08-02: not now, and this is a deferral with a condition rather than an open question.** ⚠ **The previous wording — "whether the post-drop graph *owes* a blind listen" — misread `REQ-38`, and a session must not restore that framing.** Read from source, `REQ-38` says blind listening is the **primary evaluation method** and offline metrics must not override listener judgment: a rule about **how a judgment is made when one is being made**, not a debt every graph change incurs. No isolated adoption decision about the post-drop graph is pending, so nothing triggers it. **The owner's decisive argument, and it stands on its own:** every outcome leads to the same place — a pass adopts, and a failure still would not revert to delivering release-less artists, only change the exclusion mechanism. A test whose branches share a direction is not informing a decision. **Corroborating evidence he did not cite:** `TAS-` measured **zero** bottom-decile interior artists across 120 journeys, and the release-less tail sits overwhelmingly in that region — so the dropped artists were largely never delivered, and the drop's audible effect is second-order (shifted marginals, ~109 stranded of 74,193). **The one real cost, named rather than dismissed:** if the cap re-evaluation yields a rebuild, the drop is permanently confounded with the cap change and only the combined result is ever heard. That is why the option is preserved rather than closed. **Condition to spend it:** if the post-drop graph is ever proposed for adoption **as the only change** (the cap re-evaluation returns no rebuild), **or** if a combined rebuild sounds worse and the cause needs decomposing. **The instrument is already preserved** — `drop_no_release_tail` exists as an experimental control so a build can hold the drop constant in a factor table, so deferring costs no future capability. Distinct from the rule's own acceptance, which is closed. |
| **The label-affinity / clustering data asset** | **The owner's trigger.** `wgt_release_raw.json` side-collected record-label credits, countries and years per graph artist; nothing consumes it. His style-vocabulary read adds: for the curated Discogs styles, carrier count alone tracks usability — the clustering idea keeps its value for the open MB tag space, where frequency separates nothing. |
| **Tag clustering as a junk-label filter, owner-raised 2026-08-01** | **Unmeasured; the owner's trigger.** The current whitelist keeps a tag only if MusicBrainz classifies it as a genre — an ontology decision, which is why `british invasion` is discarded despite binding coherent artists. The owner's proposal: a real label's carriers cluster in the map, a junk label's scatter. Frequency alone cannot separate them, since `seen live` and a genuine niche genre are both rare. |
| **One new Snyk Low finding per module added under `builder/analysis/`** — *but only for modules taking a CLI path argument.* **The three added 2026-08-02 (`dsp_ids.py`, `delivered_coverage.py`, `id_quality.py`) contribute NONE**, the same reason `tail_exposure.py` did not: no CLI argument, so no input reaches a path. Full `builder/` scan at that closeout returns **32** — 27 Path Traversal Lows, 3 DOM-XSS in `listen.html`, 2 XML-parser Mediums (row above). | **Recorded, not fixed; extending the acceptance is the owner's.** A CLI `--out` path flows into `pathlib.Path` — the same class as the 13 already accepted here, **now 11 in the `TAS-` directory plus 6 in the `WGT-` directory** (`wgt_grid.py` ×2, `wgt_release_read.py` ×2, `wgt_style_filters.py` ×2). *(Corrected 2026-08-01 latest: this row said **4** and omitted `wgt_style_filters.py`'s two, which a re-scan surfaced. `tail_exposure.py` added the same day contributes **none** — it takes no CLI argument, so no input reaches a path.)* It cannot be meaningfully sanitised: captures deliberately live *outside* the repo, so confining the path breaks intended usage. |
| **Tag-aware selection increases the map's total edge count** | **Before any rebuild pre-registration is written.** Opened by `TAS-4`: Jaccard is symmetric, so genre-sharing artists promote each other and creations exceed deletions at every λ. Mutual k-NN bounds each artist's own list, not the count of mutual pairs, so mean degree rises. Execution log §9.4/§9.5. **⚠ CORRECTED 2026-08-02 — this row previously said `w_degree_hub` "is dormant *because of the current graph's top-degree set*", which reads as the `w_floor` dormant-term confound about to repeat. It is not.** Checked from source: `w_degree_hub = 0.0` (`api/…/config.py:54`) and the term is a plain multiplication in the cost function (`pathfinding.py:135`), with no environment override anywhere — weights are not env-driven. **At a zero coefficient the graph's top-degree set cannot make the term fire, so it cannot switch itself on in the arms that succeed.** What *is* live is a decision, not a confound: the *reason* the weight is zero rests on a property of today's graph (§2.6 — the top-1%-by-degree set is largely insular micro-genre artists, so penalising them is not what you want), and a different connection rule changes that set. **So a rebuild pre-registration should decide `w_degree_hub` deliberately and record the decision — it does not need a control against the term waking up on its own.** |
| **The 11 blind verdicts as a falsifier for any future coherence instrument** | **If the owner reopens the instrument line** (route-population gate, `COH-3`). The corpus is unconsumed; any scoring against it must be pre-registered cold, and `ct_retrodict.py`'s committed-but-unrun rule counts as the first attempt for reporting purposes. `SYN-7` binds. |
| **42 ListenBrainz nulls and 24 MBIDs refused as ambiguous** | **Accepted, won't chase.** Both are recorded in the probe JSON. Reopen only if a criterion is built that depends on those specific artists being scored. |
| **The `× lower` path-read redraw** | **If the owner asks for obscure-endpoint path reads under candidate rules** — a new §8 amendment designed cold; the committed draw's famous classes stay the record. |
| ✅ **The `REL-` release-dump union pass** | **CLOSED 2026-07-31 — the path is known-unreachable, not deferred again.** Its §7 condition was "if and only if `REL-1` lands in 45.0–49.9%". `REL-1` cleared the bar outright, so the condition can never fire for this run. Reopening needs a new pre-registration designed cold. Struck, kept for the record. *(Correction 2026-08-01: this row and the frozen spec's §7 both said the 345 GB dump "was deleted after measurement" — **it was not**; it is on disk at `builder/scratch/mb-json-dumps/release/`, 322 GB, verified. The closure never depended on the deletion and stands. The `WGT-` pre-registration reads the dump for a different question — evidence strength, not coverage — designed cold as this row requires.)* |
| **Whether `REL-`'s frame is taken into `TAS-`** | **The owner's trigger, unchanged.** A `TAS-` §1 vocabulary change is an amendment to a frozen document and a rebuild spends his ear (`REQ-38`). **The cheap read this row asked for has now RUN** — execution log §15, figures `tas_frame_split.json`. It does not settle the trigger, but it changes which frame a decision would be about: the Discogs **style** column, not the coarse genre column, is what costs discrimination, and `W4` (`W1` + Discogs genre only) dominates the previously-evaluated `W6` on reach, spread and redundancy alike. **`W6` should not be the candidate any future amendment names.** `REL-3`'s fidelity median still governs, and nothing measured says `W4` is good enough to adopt. |
| **`REL-3`'s ratio bar is degenerate and must not be reused as written** | **Before any successor pre-registration expresses a bar as a multiple of a null.** The null median was exactly zero, so "≥ 3× the null" was satisfied by a division by zero. A ratio bar needs a stated floor on the denominator, or a difference bar instead. |
| **The `LBS` `filter` token's meaning** | **Accepted, won't chase**; reopen only if a permitted value differing in `filter` ever needs one-knob attribution. |
| **13 pre-existing Snyk findings under `builder/analysis/`** | **Accepted, won't fix**; reopen if a frozen probe is un-frozen and edited, or `listen.html` is ever served. |
| **Two Snyk MEDIUMs, same rule** — `rel_discogs.py:87` **and `ctc_census.py:173`**, insecure XML parser (CWE-611) on `xml.etree.ElementTree.iterparse` over local dumps. *(This row named only the first until 2026-08-02; a full `builder/` scan at closeout found the second, and the analysis below applies identically to both.)* | **INVESTIGATED 2026-08-02, and it splits in two. Accepting the residual is the owner's, as with every row above.** Snyk reports one finding but its message names two hazards ("vulnerable to XXE and DDOS"), and they do not have the same answer here. **Tested empirically on this interpreter (3.12.13) rather than argued from the rule's title:** ① **XXE — NOT APPLICABLE.** An external entity pointing at a local file is *refused outright*: `ParseError: undefined entity`. Nothing leaks. **The cited CWE-611 is not reachable**, which also matches the rule's own scope (*"Python < 3.11"*) against this project's `>= 3.12`. ② **Entity expansion — REACHABLE.** An 11-level billion-laughs shape expanded to 8,192 characters, so the DoS half is real in principle. **Exposure for ② is the argument, and it is the same one the 13 Lows were accepted on:** the input is a 57 GB third-party dump sitting on local disk, read by a frozen offline probe; making it hostile requires local write access, which is a larger problem than a research script consuming memory, and no service parses it. **Deliberately NOT fixed:** the remedy is `defusedxml`, a new dependency, and editing a frozen probe would fire the "13 pre-existing findings" row's own reopen condition. The probe stays frozen. Probe script retained at `builder/analysis/2026-08-02-dsp-ids/` is unrelated; the XXE test itself was throwaway and its result is recorded here rather than kept as code. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. Track B's harness complied throughout (`ReadOnlyArchive`). **Condition fired again 2026-07-30** — the `TAS-`/`TD-` capture reads the archive through the same Track B helper and therefore through `ReadOnlyArchive`; complied, verified at closeout. **Stays open**: it is a standing condition on future harnesses, not a one-off to discharge. |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| **`TB-P5H-7`** | **If any successor bypass-device or router-pricing pre-registration is written.** |
| **The candidate-pool recompute** | **If the owner picks up the parked candidate decision.** |
| ✅ The `--prune` publish pass | **DONE 2026-08-02.** Ran `sync_frontend.py --prune --skip-build` through the module, so it kept the `FRO-1` pass ordering and the between-passes content-type probe. **Two orphans deleted** — `assets/index-C-9fM9tV.js` and `assets/index-C4yz7h5J.css`, the pre-redesign 2026-07-27 build. The bucket is now 7 objects. **The pre-flight that made it safe, and a successor should repeat it:** `--skip-build` publishes `frontend/dist` *as it stands*, so a stale or different `dist/` would have pruned the assets the live page names. Verified first that `dist/index.html` referenced exactly the two hashed assets the **live** page referenced, then ran `aws s3 sync … --delete --dryrun` to see the deletion list before running it for real. Verified after: bucket contents, `200` plus correct `Content-Type` for html/js/css/woff2/svg, and a live search returning Radiohead. Struck, kept for the record. |
| **The rate limit's headroom** | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1.** |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
