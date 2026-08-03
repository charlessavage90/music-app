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
