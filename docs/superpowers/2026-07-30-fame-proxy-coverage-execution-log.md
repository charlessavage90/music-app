# Execution log — fame-proxy coverage probes, 2026-07-30

**Role: RETAINED EXECUTION LOG.** The reasoning behind the work on branch
`fame-proxy-coverage` (PR #53). **Owns no figures** — those live in
`findings/2026-07-30-fame-proxy-coverage.md` (`FPC-` series) and
`../../builder/analysis/2026-07-30-fame-proxy-coverage/`, and are cited by identifier here.

**Scope: descriptive scope probes. Nothing adopted, no criterion fixed, no currency
changed, no shipped code touched.** Track B is untouched throughout.

---

## §1 How this started, and the decision that shaped it

An open discussion about data sources, similarity, fame and coherence surfaced a
structural claim: **one data source is doing three jobs, and two of them are the same
measurement.** Similarity is ListenBrainz co-listening; popularity is score-weighted
in-degree *over that same graph*; fame is a third-party proxy. Popularity ≡ in-degree is
the shared root of `GRT-P2` (the acceptance guard cannot see a collapse it caused),
`DD-F1`/`MKS-5b`, and `w_jump` pricing hops in a currency that is a function of the graph
being routed over.

The owner's argument for looking at ListenBrainz popularity was **coverage, not bias**:
Wikipedia has a built-in floor (no article ⇒ scored at the floor), and the product's target
zone is exactly where that floor sits. **That framing was correct and mine was not** — I
had been evaluating the candidate instrument on bias, where it adds nothing.

**Decision: run descriptive scope probes before writing any plan** (the
`cheapest-experiment-first` memory; the `CS-P0` precedent). No pre-registration, because
these fix no criterion — but **every probe's expectations and read thresholds were
committed before it ran**, which is the honest analogue and which the commit timestamps
evidence.

## §2 Gate outcomes — three pre-committed predictions, three refuted

This is the log's most useful section. Each was fixed in a module docstring and committed
before the run.

| Probe | Prediction | Outcome |
|---|---|---|
| `fp_floor_reach` | floor share among routed interiors RISES with bypass depth | **REFUTED** — it falls monotonically (`FPC-2`) |
| `fp_resolution_gap` | much of the floor is name-resolution failure | **REFUTED** — 5.6% of the checkable floor (`FPC-1`) |
| `fp_agreement` (b) | multilingual adds < 5 coverage points anywhere | **REFUTED** — 7.1 and 6.8 points (`FPC-5`) |
| `fp_agreement` (a) | > half the artifact carries no English article | confirmed (`FPC-3`) |
| `fp_agreement` (c) | strong pooled agreement, weak within band | partly wrong — weak at both (`FPC-6`) |
| `fp_magnitude` | English is an adequate ranking instrument | confirmed at 4.0% vs a < 5% line (`FPC-8`) |
| `fp_floor_reach_t3` | — (falsification test of `FPC-2`) | **FIRED** at 38.7% vs a ≥ 25% bar (`FPC-9`) |

**The correction that matters, and it is recorded at the head of the findings document.**
The case that opened this work — that the Wikipedia floor is *actively corrupting*
fame-currency measurements — **is not what the measurement says**. No Track 2 or Track 3
verdict changes. What survives is `FPC-3` + `FPC-9`: the blindness is **latent**, and it
begins binding precisely when the product succeeds at what `REQ-37`/`DD-F1` demand.

## §3 Decisions taken, with reasoning

1. **Import the fame frame from `cb_metrics` rather than copy it.** Band membership must
   have one definition or nothing here is comparable with Track B, and the
   adopted-artifact sha assertion travels with the import.
2. **Query Wikidata for `P434`; never crawl MusicBrainz for its external links.** Same
   join, 1 req/s (~21 h) against batched WDQS (minutes). Recorded because the owner's
   proposed route was via the MusicBrainz artist page, and the cheap direction is the
   reverse one.
3. **Do not edit the frozen `2026-07-24-.../fetch_pageviews.py`.** Editing it trips the
   reopening condition on the accepted Snyk deferral for the frozen probes. `fp_fame_mbid`
   supersedes it forward-only, changing exactly one knob (resolution) and holding formula,
   window and floor rule constant so any difference is attributable.
4. **Refuse rather than guess on ambiguous Wikidata claims** (`fp_fix_duplicates`). 24 of
   54 multiply-claimed MBIDs are recorded unresolved and scored at the floor. A refused
   answer is auditable; a lucky guess is the defect being fixed.
5. **Test `FPC-2`'s weakest link instead of only naming it.** Track 3's `LIMIT` arm is the
   `w → ∞` min-sum-percentile route — a ceiling, not a candidate — which is what a latent-risk
   claim needs.

## §4 Defects found — including one in my own instrument

**`FPC-11`: the instrument built to remove silent errors reproduced one.** `fp_wikidata`
broke ties between two Wikidata items claiming one `P434` by keeping the one with **more
sitelinks**. Neil Young's MBID is claimed by `Q633` (correct) and `Q25820` (Thomas Young,
physicist — an erroneous upstream claim), and the physicist has more language Wikipedias.
**Caught by the validation pass, not by review** — the fourth time on this project that
running the check beat reading the code. Repaired by preferring a music signal and never
sitelink count.

**A method note worth keeping:** the defect was only visible because `fp_fame_mbid
--validate` compared *entity identity* against the frozen resolver rather than comparing
*scores*. A score comparison would have shown a plausible number and passed.

## §5 Corrections to the prior record

- **None to Track 2 or Track 3 verdicts.** `FPC-1` and `FPC-2` point away from any
  re-reading.
- **`CNS-2` is confirmed and quantified, not superseded.** The 2026-07-26 census recorded
  that the name resolver misidentifies short generic names and that *the error inflates
  fame*. `FPC-10` measures it on a routed population (18 wrong entities in 1,090) and the
  direction holds. `FPC-10` cites it rather than presenting the class as new — a gap the
  doc-auditor caught in this closeout.
- **My own framing, corrected in §0 of the findings document** (see §2 above).

## §6 Operational measurements with no other home

- ListenBrainz `POST /1/popularity/artist`: whole artifact in **~75 requests, ~3 s per
  1,000**. `MAX_ITEMS_PER_GET = 1000`, read from `listenbrainz/webserver/views/api_tools.py`
  at master.
- Wikidata WDQS: **latency is highly variable under load** — the same query shape measured
  **4.5 s and 109 s on adjacent batches**. Full join at batch 600 took ~35 min wall clock.
  Collectors resume from disk and back off; a tight retry loop here would be rude and slow.
- Wikimedia pageviews: ~0.4 s/call. The magnitude sample (125 artists, all languages) ran
  ~25 min, dominated by the top band's ~64 languages per artist.
- Suites at closeout: builder **129 passed**, api **217 passed**, frontend **107 passed**
  across 18 files. Run, not recalled.
- Snyk `snyk_code_scan` on the new probe directory: **clean, 0 issues**, run twice (after
  the first six modules and again after `fp_fame_mbid`/`fp_fix_duplicates`).

**D6 — the standing context layer:** unconditional **44,183 characters**, conditional
**2,154 lines**. **This branch's delta is 0 and 0** — it touched no file in `CLAUDE.md`,
`.claude/` or `memory/` (verified by empty `git diff main..HEAD` over those paths). The
movement from 2026-07-29's 44,113 / 2,121 came from Track B's merge, not from here.

## §7 The coherence thread — recorded because it is the largest thing NOT done

**Raised in discussion, deliberately not acted on, and it is the most substantial open
idea this session produced.** Recorded here so it survives the session rather than the
conversation.

**The argument.** Phase 1 §3.8 records that the two metrics built to guard coherence were
the *worst* predictors of the owner's verdicts, and that has hardened into "do not proxy
coherence with a metric." **The record supports something narrower.** Both metrics —
Adamic–Adar and overlap coefficient — are **pure co-neighbour counts on the similarity
graph**. They were auditing the thing they were derived from. The supported conclusion is:
*no metric in the topology's own currency has ever tracked his ear.*

**The supporting observation.** His verbatim notes (§3.9) are not topological. "Avril
Lavigne and Blink-182 hops felt wrong for the path." "The Shins to the White Stripes feels
like a leap that should have at least a step in between." "Kings of Leon → Green Day → CCR
doesn't feel right." Those are **genre, era and scene** judgments.

**The untried instrument.** MusicBrainz tags/genres — MBID-keyed, free, dumped, and
orthogonal to listening behaviour. **Its honest weakness is the same shape as the one this
branch just measured:** tag coverage thins in exactly the obscure tail where the Wikipedia
proxy is already blind. That is the second instance of the same failure mode, and it should
be measured *before* anything is built on tags — the probes in this branch are the template.

**A second, structural half of the same thread**, also unacted:

> **The original design assumed coherence is ADDITIVE along edges.** The cost function is a
> sum of per-edge terms and Dijkstra minimises a sum, so the architecture can only express
> *coherence = sum of local step qualities*. But `PRODUCT-REQUIREMENTS.md`'s own definition
> has two clauses, and the second — *"the whole path reads as one journey that fits its
> endpoints"* — **is not expressible as an edge sum.** A path can have every edge strong and
> still wander out and back.
>
> Weak corroboration, explicitly suggestive rather than evidence (n=11, and the owner said
> hub incidence was not his criterion): in §3.8's agreement table the two **worst**
> predictors of his ear were both edge-local overlap measures and the two **best** were both
> path-level counts. If a non-additive global clause is what decides, a path-level count
> would track it by accident.
>
> Consequence if true: no per-edge graph change can guarantee coherence, which bounds what
> any cap-rule or algorithm work can promise — and an offline coherence instrument would
> have to score **paths, not edges**, which is why the two that failed, failed.

**Neither half is a proposal, and nothing is pre-registered.** Both are the owner's trigger.

## §8 What was decided against, and why

- **Editing `PRODUCT-REQUIREMENTS.md`'s Definitions section** to quantify the proxy's
  blindness. The existing sentence ("blind in the modern-obscure tail") is *true*, so this
  is growth rather than correction, and it is his requirements layer. Deferred with a
  condition (A3) instead.
- **Running `fp_fame_mbid --build`** (full-graph fame values, ~33k pageview requests,
  ~3–4 h). The validation answered the decision-relevant question at a fraction of the
  cost; the full build is only needed once a currency decision exists.
- **A composite fallback proxy** (Wikipedia where an article exists, ListenBrainz below).
  Rejected at design time: it puts a discontinuity at exactly the boundary that matters
  and splices two different constructs.
- **Re-reading any Track 2 / Track 3 result in a new currency.** `FPC-1`/`FPC-2` say
  nothing currently needs it, and deciding it after seeing a recomputed number is what a
  pre-registration exists to prevent.
