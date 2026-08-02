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
