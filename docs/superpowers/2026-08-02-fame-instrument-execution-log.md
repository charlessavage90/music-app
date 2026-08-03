# Fame-instrument adoption — execution log

**Role: ACTIVE retained execution log** for the work governed by
`specs/2026-08-02-fame-instrument-adoption-preregistration.md` (`FAM-`). Appended per
task, not only at closeout. Figures live in the probe outputs and the eventual findings
document — cited here, never restated, except where a disclosure requires the number on
the page (`FAM-AM1` head).

## §1 — Context and the owner's half (2026-08-02)

The owner ruled, in conversation, before any of this existed: the cap re-evaluation's
scope includes the data-set switch; its primary outcome is the bypass obscurity gradient
(`REQ-42` shape); and the fame instrument is fixed **first**. He then chose currency
option (b) — ListenBrainz listener counts, MBID-keyed — and **no re-read** of prior
fame-scored results. All four rulings are recorded in the pre-registration's §0. The
delegation pattern (controller + Opus subagents for execution, `ml-graph-analyst` for
design critique) is his suggestion, adopted with the division recorded in §5 there.

Also settled in that conversation, for the cap re-evaluation to inherit (its prereg is
NOT yet written and nothing here pre-empts it): candidate families (a)–(d) including the
owner-triggered tag-based degree limiter (`NEXT.md` deferral row) and router-priced
unbounded as staged comparison data; coverage as guard-only at ~10,000; hubness-rising-
with-depth as the per-arm kill; LB similarity as the sole source of edge existence with
tags only re-ordering, re-weighting, or removing.

## §2 — Design critique before the run (2026-08-02)

Dispatched the `ml-graph-analyst` against the committed pre-registration (commit
`560b233`) before any fetch. Full text: `builder/analysis/2026-08-02-fame-instrument/
fam-prereg-critique.md`. Every severity-A and severity-B finding was accepted and is
normatively dispositioned in `FAM-AM1`; the table below is the complete disposition list.

| Finding | Disposition |
|---|---|
| A1 stability bar in a dead zone | `FAM-AM1.1` — per-band Spearman + p99 |Δpctl| bar |
| A2 nothing validates tail ordering | **Escalated to the owner** (his time); deliberately not resolved in AM1 |
| A3 ≥10× gate blind to sub-decade error | `FAM-AM1.4d` — Spearman ≥ 0.8 over all confirmed artists |
| A4 pair bar is ~15 effective units | `FAM-AM1.4b/4c` — 10-pair readability floor, per-artist trace |
| A5 unflagged name-ambiguous hand reads | `FAM-AM1.4a` — MBID resolution before any value read |
| B1 distinct-count bar tests the median | `FAM-AM1.2` — quantisation-step bars, per band |
| B2 no effect size, sequencing blocks one | `FAM-AM1.3` — measured step carried as a 10× floor on the cap re-eval |
| B3 only the largest atom barred | `FAM-AM1.2b` — top-5 combined bar |
| B4 FAM-3 cannot see the blind spot | `FAM-AM1.5` — relabelled smoke test |
| B5 three tracers enrich toward under-ranking | `FAM-AM1.5` — 8-of-9 pass, disclosed |
| C1–C3 percentile/lower-half definitions | `FAM-AM1.6` — exact formulae |
| C4 ALG-B-only remainder unmeasured | `FAM-AM1.2c` — FAM-2 computed on it |
| C5 population-vs-descent confound | `FAM-AM1.7` — named as owed to the cap re-eval factor table |
| D1 vintage bias | `FAM-AM1.7` — carried hazard |
| D2 snapshot identity | `FAM-AM1.7` — ruler = file + sha; re-fetch owes its own FAM-5 |
| D3 non-uniform scale sensitivity | `FAM-AM1.7` — descriptive companion read added |
| D4 three criteria foreseeable from disk | `FAM-AM1` head — full disclosure of what was computed |
| D5 nulls shrink denominators | `FAM-AM1.8` — dual all/matched reporting with null counts |

**Decision worth recording:** the fetch was deliberately held until this critique was
read and `FAM-AM1` committed, so every re-specified bar precedes the data it will be
read against. The cost was ~15 minutes; the alternative — amending after figures exist —
is the pattern `TAS-AM3` had to carry a permanent disclosure for.

**Snyk:** owed for the new `fi_*` scripts when they land; the two probes take no CLI
argument, the class every prior no-CLI analysis module contributed zero findings in.
Scan result to be recorded here when run.

## §3 — Union fetch and mechanical criteria (2026-08-02, Opus subagent + controller reads)

Task report honoured its brief in full: both source artifacts sha-verified before the
first request, union exactly 93,067, 94 requests with no retries, blindness rule held
(no named artist's value surfaced anywhere; `FAM-3`/`FAM-4` untouched). Snapshot
`fi_union_snapshot.json` sha256 `d9d6d5d3…`, manifest sidecar committed. **Snyk scan over
the new scripts: 0 issues** (run by the subagent; discharges the §2 note). Figures live
in `fi_validation.json` — cited here, never restated, except where a read requires the
number on the page.

**Controller reads against the committed bars — the reads are the controller's, and two
of five criteria did not read clean:**

- **`FAM-1` FAILS as written**: union coverage 95.580% against the ≥ 99.0% bar. The
  exposure map (computed before escalating, from three on-disk files): **86.8% of the
  4,114 nulls sit on the two frozen drop lists** — artists no build can deliver. On the
  deliverable union (minus both lists, 80,642 artists) coverage is **99.329%**, above the
  bar. The choice between standing on the committed bar and re-scoping the population by
  amendment is **the owner's** — a post-result bar change is the one move a session never
  makes alone. Escalated with both numbers and a labelled recommendation.
- **`FAM-2`: adopted frame passes with ~3.4× margin** (step 0.00147 vs ≤ 0.005; top-5
  lower-half atoms 1.35% vs ≤ 2%). **The `ALG-B`-only remainder splits by denominator**,
  an ambiguity the executor flagged rather than resolved: mapped-percentile steps pass
  (max gap 0.0020), but own-population atom shares exceed the bars (largest atom 1.56%
  as fetched / 1.03% deliverable; top-5 lower-half 6.74% / 4.83%). Substantive meaning:
  candidate-only artists clump at 1–5 listeners, so *within-remainder* ordering at the
  dead end is coarse. The gradient is read in adopted-frame percentiles and does not
  consume within-remainder ordering — but the reading choice is disclosed, not silently
  taken, and the limitation is named in the escalation.
- **`FAM-5`: bars pass and the result is POWERLESS — recorded the `TAS-6`-vacuous way,
  never citable as stability evidence.** Every overlapping value is byte-identical across
  the two fetch dates; the executor treated that as a probable bug in its own work and
  refuted that with a live 12-MBID re-fetch reproducing both files. The endpoint served
  the same aggregate table on 2026-07-30 and 2026-08-02 (a batch-regenerated upstream
  table), so the criterion measured zero elapsed table versions and cannot separate
  "stable" from "same table twice". It *does* rule out fetch nondeterminism. The upstream
  batch-table property strengthens `FAM-AM1.7`'s snapshot-identity rule: between
  regenerations the instrument is frozen upstream; across them, a re-fetch is a new
  instrument.
- `FAM-3` / `FAM-4` remain unread, pending the identity-confirmation step (`FAM-AM1.4a`).

## §4 — Identity resolution, the FAM-6 draw, and the FAM-3/FAM-4 reads (2026-08-02)

Second Opus task delivered the `FAM-6` sample (15 + 10 alternates, seed 20260802,
byte-identical across two runs), the owner checklist (audited: no ruler value anywhere;
strata replaced by opaque group letters so the sheet cannot rank itself — a strengthening
of the blindness rule), and both identity tables with **zero CANNOT_CONFIRM rows**. The
"Love" collision resolved three ways, decisively: the resolved MBID appears in run 2's own
dislike list — it is the node the app itself served. FERG carried forward as excluded per
the prereg. Snyk over the directory: 0 issues.

**Controller reads (`fi_read34.py`, first place these ruler values were read):**

- **`FAM-3` PASSES 9 of 9** — every common-knowledge famous artist at `fame_lb_pctl`
  ≥ 0.997. Smoke test only, per `FAM-AM1.5`; licenses nothing about the blind spot.
- **`FAM-4` FAILS BOTH BARS**: direction agreement 82.35% (28/34) against ≥ 90%, and
  Spearman 0.4915 against ≥ 0.80. Readability was fine (34 pairs ≥ 10 floor). The
  single-artist exception does not fire — six failing pairs spread over six artists
  (Blood Red Shoes in 4, The Human League 2, Porcupine Tree 2, 10cc 2, Quantic 1,
  Nightmares on Wax 1).
- **The failure is systematic, not noise, and it is the construct divergence the
  criterion existed to catch**: every failing pair puts an enthusiast-population act
  (Porcupine Tree, Blood Red Shoes — modest Spotify numbers, heavily scrobbled) above a
  casual-mainstream act (10cc, The Human League, Quantic — millions of casual Spotify
  streamers who do not scrobble). ListenBrainz measures listening among enthusiasts;
  Spotify monthly listeners measures current mainstream reach; in the famous-to-mid band
  they genuinely disagree. Consistent with `FPC-6`'s weak LB↔Wikipedia agreement
  (0.4365 pooled) — three instruments, three orderings, and the hand instrument now
  measured against LB directly at 0.4915.
- **Read state under §4's rules: adoption is BLOCKED as of this read.** No amendment was
  written to soften it. The full verdict awaits `FAM-6` (the owner's tail hand reads,
  checklist delivered), and the decision about what a failed `FAM-4` means for the
  currency is the owner's, presented with options in the conversation of record.

## §5 — FAM-6 and the final verdict: NO ADOPTION (2026-08-02)

The owner ran the checklist the same day. His reads were **committed verbatim before any
comparison was computed** (`d318089`, WGLL bound three). Fifteen confirmed rows after the
replacement chain — every replacement consumed in same-group order per `FAM-AM3`,
including one could-not-confirm alternate. Five sampled deliverable-tail artists had **no
Spotify page at all**, and three confirmed pages read **zero monthly listeners** (zeros
enter the Spearman, excluded from ratio pairs only).

**`FAM-6` FAILS: Spearman 0.4552 against the ≥ 0.70 bar** (n = 15, floor cleared;
descriptive pair companion 65%). Figures: `fi_read6.json`. The failure fingerprint is
`FAM-4`'s again, now in the tail: the failing pairs put enthusiast-scrobbled acts
(Kitchen Cynics, 232 Spotify listeners, in six failing pairs) above regional-mainstream
acts (Muelas de Gallo, 556k, in six; Eneda Tarifa; and December Avenue at **6.8M** Spotify
listeners sits in our obscure quarter). The §2 shared-population hazard is no longer a
carried caveat — it is measured, twice, in both regions, along the same axis.

**Verdict under §4, no judgment involved: `FAM-4` and `FAM-6` both failed → NO ADOPTION,
no silent fallback.** ListenBrainz listener counts measure enthusiast attention, and both
hand-read sets show that ordering diverging from worldly fame — the construct
`PRODUCT-REQUIREMENTS.md` defines — in the famous band and the obscure tail alike. The
currency decision returns to the owner. **One durable asset came out of the failure: a
30-artist hand-read validation corpus** (15 famous-band from 2026-07-25, identity-confirmed;
15 tail from today, identity-confirmed at draw time), committed, reusable by any future
ruler candidate's pre-registration.

### §5a — A late hand read, recorded per WGLL bound three (2026-08-02, after the verdict)

The owner kept digging on **TJ Brown** — the alternate he had marked *could not confirm
identity* — and found the Spotify page via a YouTube stream → Twitter → website → Spotify
chain, with identity corroborated by the MusicBrainz feature credits (QTCinderella,
Lilypichu): **8,274 monthly listeners.** Ruler value 218.

Three consequences, none of them a verdict change:

1. **The `FAM-6` confirmed set is NOT revised.** The replacement procedure was followed
   correctly with the information available at read time, and re-opening a confirmed set
   after the verdict is known is the post-hoc move this discipline exists to bar.
   **Labelled sensitivity check, not a re-read: with TJ Brown added (n = 16) the Spearman
   is 0.4985** against the same 0.70 bar — the verdict is insensitive to the late row.
   The read is recorded here as an addendum row; a future corpus may include it **by
   amendment at design time only**. The running `RCS-` shootout's corpus stays exactly as
   its §1 committed it.
2. **"No Spotify page" outcomes carry detection-effort dependence.** A page can exist and
   be unfindable by reasonable search — TJ Brown took a four-link chain outside Spotify
   to locate. So the five no-page exclusions are "not findable at ordinary effort", not
   "does not exist", and any future read consuming those outcomes inherits that caveat.
3. **The featured-credit class gains a second worked instance.** TJ Brown's MB
   discography is contributions to and features on other artists' work (streamer-adjacent
   releases), the same shape as 田島賢 — in the deliverable population because credits
   count as release groups, invisible on DSPs as a primary act. The candidate-refinement
   row below accumulates.

**Owner observation during the hand reads, recorded as a candidate refinement (his
trigger, never a session's):** several sampled tail artists are *featured-credit* artists
— e.g. 田島賢 (`7e4f57b3`), whose discography is video-game-soundtrack contributions.
**Checked against the record: he was never in the no-release tail population** (absent
from `tail_signals.json` and both drop lists) — the adopted rule only evaluates artists
with *zero* MB release groups and no Discogs release, so an artist credited on any
release passes without ever being considered. Not a wiring defect; a scope boundary the
rule was never designed to cover. Extending it (e.g. requiring a primary-artist release)
is a **new product decision, designed cold** — same standing as the tag-based-limiter
row. His FAM-6 experience is the first measurement of the class: 5 of 20 examined
deliverable-tail rows had no Spotify artist page.

**The mechanism, closed by the owner (2026-08-02) and corroborated by `LBS-1` from
source:** TJ Brown's ListenBrainz profile shows **five tracks, none as primary artist** —
and `LBS-1` records that featured credits enter the similarity computation at **0.25
weight** (`FEATURED_ARTIST_WEIGHT`). So the class is structural, end to end: a
MusicBrainz *credit* creates the node, quarter-weight co-listens on *other artists'*
tracks create its similarity edges, and the release filter keeps it because credits count
as release groups. These artists are in the graph without ever having been listened to
*as artists*. **When the owner triggers the filter extension, the detector is cheap and
two-sided:** the primary-vs-appears-on release split is computable offline graph-wide
from the MB release dump already on disk (322 GB, `builder/scratch/mb-json-dumps/release/`),
and the same split exists on the LB side (track count / primary share). Nothing is built
today; this paragraph is the design input.

## §6 — The ruler-candidate shootout: figures and controller reads (2026-08-02)

Executor delivered all four `RCS-` tasks; figures in `rcs_results.json` (verdict-free by
design), raw responses committed, Snyk 0 issues. Two clean instrument cross-checks: WDQS
resolution agreed with the committed `fp_wikidata.json` on all 26 overlapping MBIDs, and
`D`'s famous pair set is identical to the LB read's 34 pairs. Six tier-2 Deezer
acceptances, each with a release-title match on the record.

**Controller reads against the committed §4 bars:**

- **`W` (MBID-keyed Wikipedia) is DEAD under rule 3.** Famous region readable (14/15) and
  **FAILED at Spearman 0.3542** vs ≥ 0.80 — *below the LB ruler it was meant to replace*
  (0.4915 on the same artists). Tail **UNREADABLE** (4/15 non-null; 11 corpus tail
  artists have no Wikidata item carrying their MBID at all). One famous null is the
  known one-directional-link class: Captain Beefheart's Wikidata item points its `P434`
  at MusicBrainz's separate "The Magic Band" artist — verified against both APIs,
  invisible to Wikidata-side coverage checks.
- **`D` (Deezer `nb_fan`): famous region readable and FAILED NARROWLY — Spearman 0.7560
  vs ≥ 0.80** (pair agreement 0.9706 vs LB's 0.8235; markedly better than LB on both
  measures, and still below the bar). **Tail UNREADABLE as committed** (pooled 10/15;
  tier-1-only is n = 4 and carries no information at that size).
- **Rule 4's pre-committed sentence therefore currently stands: "no measured candidate
  orders the tail."**

**The escalation, and why it is the owner's:** the five `D` tail nulls are not Deezer
failures — every one has a plausible exact-name Deezer page. The pre-committed tier-2
corroboration requires a MusicBrainz *release*-title match, and those five artists have
**zero releases** (3–13 standalone recordings each; re-verified against MB) — the truth
side of the check is structurally empty, so the procedure cannot run. The executor
correctly **refused** to widen corroboration to recording titles mid-run, because
candidate `nb_fan` values were already visible and the widening moves `D`'s tail count
in the known-helpful direction across the readability floor. Whether to widen by
amendment (`RCS-AM1`, post-result, permanently disclosed) is a change to a committed
acceptance rule after results are visible — **the `FAM-AM2` class, the owner's call**.
Raw MB payloads for the five rows are retained in `rcs_deezer_raw.json` for that path.

## §7 — `RCS-AM1` executed: the tail stays unreadable, and that is final (2026-08-02)

The owner ruled to widen; `RCS-AM1` was committed before any match was computed, then
executed (`rcs_am1.py`, resolutions and re-read in `rcs_am1.json`). Outcome of the
five closed rows: **one acceptance** — Muelas de Gallo, recording-title match, `nb_fan`
2,987 — and **four final nulls** (Jess Okoro, Acer, DTX, Dorona Alberti: no normalised
recording-title overlap between their MusicBrainz recordings and any exact-name Deezer
candidate's tracks). Per the amendment's own text there is no third widening.

**AM1 tail re-read: 11/15 non-null — still UNREADABLE, one row short of the ≥ 12
floor.** Descriptive figures on the readable 11, reported because they inform the next
decision and bar nothing: Spearman 0.5923 (bar would have been 0.70), pair agreement
83.3% — better than LB's tail (0.4552 / 65%) and below every committed standard.

**Final state of the shootout, all three instruments now measured on the same corpus:**
LB failed both regions (the `FAM-` verdict); Wikipedia is dead (famous 0.3542, below
even LB; tail effectively nonexistent); Deezer is **the best measured instrument in
every cell and passes none** — famous 0.7560 vs 0.80, tail unreadable at 11/15 with
0.5923 on what can be read. **Rule 4's pre-committed sentence now stands definitively:
"no measured candidate orders the tail."** The instrument question returns whole to the
owner; per rule 4 the two-currency design becomes a live option only by his choice.
This is a seam: the fame-instrument track has reached a complete, fully-recorded
conclusion set, and what follows is a design decision, not a measurement.

*(Between §7 and §8 the owner took the design decision: the Definitions ruling —
obscurity redefined as novelty-likelihood, `f59bc2a` — and the `NOV-` validation was
pre-registered against it.)*

## §8 — The NOV-1 read: UNREADABLE, and the criterion was mis-designed (2026-08-02)

The owner's marks (committed verbatim, `c87c4fb`): **4 KNOWN, 26 UNKNOWN** — below the
5-per-class floor, so **`NOV-1` is UNREADABLE as committed.** Figures: `nov_read.json`.

**The controller's design defect, stated plainly:** `NOV-1`'s two-way AUC counts on the
direction the governing Definitions entry explicitly disclaims — *"artists it calls
famous may still be novel to a given user... and no requirement counts on seeing
those."* A criterion that contradicts the governing document is wrong by this project's
own rule, and it was authored the same day as the clause it contradicts. The marks
expose it exactly: **every one of the 44 inversions is a famous-band artist the owner
did not know** (the disclaimed direction), and **the direction the construct actually
requires measured perfect — 15/15 artists the proxy calls obscure were novel to him.**
Descriptive AUC 0.7308, reported with no verdict attached.

**A product finding rides along, and it is the largest single fact of the day:** the
owner knew only 4 of 15 artists from the LB-famous band (top ~3% of the frame). `REQ-41`
("results vary with listener familiarity") is now quantified for the app's primary user:
even the famous end of this graph is ~73% novel to him. The app's novelty headroom is
enormous, and famous-band interiors are not the novelty dead zone the worldly-fame frame
assumed.

Escalated to the owner with the amendment option (`NOV-AM1`: replace the two-way AUC
with the one-way criterion the Definitions actually state), carrying the maximal
disclosure — the amended criterion's result is foreknown to pass — and the reasoning
that saves it: the direction mismatch is derivable from the committed documents alone,
and the clause it corrects toward predates the marks.

## §9 — Adoption (2026-08-02): `fame_lb_pctl` is the novelty-likelihood proxy

**The owner adopted the recommendation.** `NOV-AM1` is committed with its
maximum-strength disclosure; `NOV-1` stands unreadable and retired as mis-designed;
**`NOV-2` reads 15/15 — PASS** — and per the pre-registration's §3, **`fame_lb_pctl` is
ADOPTED** for offline evaluation. The Definitions "pending" clause is struck, citing the
amendment. The fame-instrument track is COMPLETE: construct redefined (owner ruling),
proxy adopted under a passed validation in that construct, worldly fame retired with
claims barred, and the cap re-evaluation unblocked in the adopted currency. What follows
is closeout and the PR; the cap re-evaluation pre-registration is a fresh session's
work, per the standing instruction in `NEXT.md`.

## §10 — Closeout outcomes (2026-08-02, night)

| Check | Outcome |
|---|---|
| A1 log distilled | This document, written per task throughout — no end-of-session reconstruction was needed. |
| A2 handoff | `2026-08-02-HANDOFF-fame-instrument.md`; predecessor's role line edited to name it. |
| A3 deferrals | Two prior rows discharged and struck in place (Definitions quantification — fired and landed; `fp_fame_mbid` build — path known-unreachable, killed under the kill-when-closed rule). Five new rows added, each with a condition. |
| A4 default-flip | **N/A and stated rather than skipped**: zero shipped-code changes this session — no knob exists to flip. The adoption is an evaluation-layer change. |
| A5 ports | No listener on 8000/5173/8138/8139; nothing started, nothing owned, nothing left behind. |
| B1 lint | Hard checks passed. Candidates all short-decimal coincidences, handed to the auditor as input. Auditor dispatched scoped to the diff; outcome recorded below when returned. |
| B2 reachability | New modules are frozen probes under `builder/analysis/2026-08-02-fame-instrument/`; internal imports flow through `fi_stats` (and `fp_common`/`cb_metrics` cross-directory reuse, recorded in the scripts). Nothing in shipped code imports them **by design** (`testpaths` ruling, 2026-08-01). No shipped-code module was created. |
| B3 vacuous tests | No new tests exist to break (frozen-probe convention). The read scripts were instead cross-checked against independent implementations: `fi_stats` reproduced the critique probes' figures exactly, and the executor's pair machinery reproduced the LB read's 34 pairs. |
| B4 prose-vs-code | Docstrings of the six new read/fetch scripts checked against behaviour; the one prose-structure defect this session produced (two log sections inserted mid-section) was caught and fixed in-session, and the auditor was told to re-verify §1–§9 ordering. |
| B5 stale descriptions | `.claude/` and `memory/` swept for fame/Wikipedia claims: clean — the consultant's currency-distinction lines are hazard warnings, true under both constructs. One growth candidate flagged to the owner (a redefinition pointer in `CLAUDE.md`'s orient table), not landed. |
| C1 | N/A entry queued in `TEST-QUEUE.md` (nothing app-facing changed); "(latest)" marker moved per convention. |
| D1 | Tree clean at closeout commit; every artifact either committed or gitignored-with-manifest. |
| D2 | N/A — the graph did not change; fixtures untouched. |
| D3 | Snapshot sha256 `d9d6d5d3…` in the committed manifest; both source artifacts sha-verified before every use (executor reports + `fi_stats`). |
| D4 | **builder 151 passed; api 230 passed; frontend 107 passed** — pasted from runs, not asserted. |
| D6 | Unconditional layer **44,245 chars**, conditional **2,155 lines**. **Both deltas zero**: no `CLAUDE.md`/`.claude/` change on the branch, `memory/` untouched. |
