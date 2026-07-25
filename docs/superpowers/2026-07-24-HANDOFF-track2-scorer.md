# HANDOFF — Track 2, at the scorer/P8b seam, 2026-07-24

**Role: ACTIVE, short-lived by design.** Written at a **clean seam** (the Stage A scorer is
built, committed, and validated on production; no factorial arm has run), for a session
picking up the **P8b harness review and then the arms** cold. Supersedes
[`2026-07-24-HANDOFF-track2.md`](2026-07-24-HANDOFF-track2.md) (the fame-proxy/sweep seam
handoff), whose open unit — "the sweep" — is now half-built and re-described here.

**This is a seam handoff, not mid-flight.** The degradation tell did not fire; the boundary
(P8b) was named at authoring time and arrived on schedule. The successor does the ordinary
`session-start` ritual — it does **not** need the mid-flight cold-read-back.

Read the record first, where it and this note disagree the record wins:

> **[`2026-07-23-repair-and-retune-execution-log.md`](2026-07-23-repair-and-retune-execution-log.md)**,
> the "Track 2" section — in particular the tail entries from "Seams named before the sweep
> is built" onward (A12, A13, A14, A15/scorer, A16, the two-sided residual).
> Then **pre-registration §9** — the amendment index, now **A1–A19** (A17–A19 added
> 2026-07-24 by the P8b harness review; still before any factorial arm).
> `docs/README.md` classifies every document.

---

## 1. State in three lines

- **The Stage A scorer is complete and committed** in `builder/analysis/2026-07-24-track2-arm-scorer/`
  (`arms.py`, `run_arms.py`, `fame.py`, `score.py`, `verify_resolver_equivalence.py`,
  `band_gap.py`, `README.md`, `fame_cache.json`). It **produces paths → resolves fame →
  scores C1–C6**, all offline and re-runnable. Validated end-to-end on production P.
- **No factorial arm has run.** Artifact untouched, sha256 `4cb84ef9…b061dc8`.
- **The pre-registration is at A16** (was A11 at session start). A12–A16 all predate any arm.

## 2. The open work — P8b, then the arms (this is the whole next unit)

**First: P8b — the `ml-graph-analyst` review of the harness.** §7 prerequisite P8b ("the
review of the harness — not yet due: no harness exists") is now **due**: the harness exists.
This is the named seam. A fresh reviewer reads the scorer cold. **The session that built it
(this one) cannot self-review it, and is additionally blind-listen-ineligible** — see §3.

**Then the arms**, per the execution log's seam entry and the scorer README's "Sequence from
here":
1. `run_arms.py` (no `--arms` filter) → full stage-1 grid (11 runs, ~40 s). `fame.py`.
   `score.py`. Read **R1's selected W** from `scores.json`.
2. `run_arms.py --arms W …` + `stage2(W)` (from `arms.py`) for the 4 attachment arms.
3. Score the winner on the **held-out** set (direction only), then the **blind listen**.

## 3. Two things the successor must carry — verified, not assumed

- **The blind-listen eligibility line.** Whoever has seen an arm result cannot administer the
  blind listen (execution log, "Seams named before the sweep is built"). The protocol solves
  this structurally — sealed arm→label mapping revealed only after verdicts
  (`specs/2026-07-22-c3-known-mechanism-blind-listen.md` §5/§7) — with personnel separation
  as the cheap secondary guard. **Do not re-derive the protocol; it decided the graph twice.**
- **The fame-currency floor is the untested lever.** The attractor analysis cleared the graph
  of being lo-fi-limited, but measured in **raw-popularity** currency where the lo-fi blob
  sits *high*. A fame-currency floor (the sweep's FL arms) could surface high-pop/low-fame
  lo-fi acts on downtempo-adjacent paths. **Watch for this in the blind listen** (A11 caveat).

## 4. What the scorer's own validation showed — figures owned by its README

- **C3 (depth gradient) run on production = 0.164** against a 0.5 threshold — production
  measurably fails F2, now quantified by the instrument that will judge the fix.
- **Flagged for P8b:** C2 = 4/8 is met by production itself, so C2 is near non-discriminating
  on this pair set; C1/C3 carry the load. The reviewer should weigh whether C2's threshold or
  the pair set needs attention.
- **A15 resolver recall fix** recovered Justice/Rainbow/Ye (Kanye West) from the fame floor,
  where they were poisoning P's own baseline medians. `verify_resolver_equivalence.py` proves
  it leaves the §5 validation sample byte-identical.

## 5. Decisions taken this session — do not re-argue (all before any arm)

- **A12** — C6 stops gating (A11 made unmatched = scored, so coverage now marks the obscurity
  the sweep seeks; gating would cap depth). The d15/d20 notability guard is the gating remnant.
- **A13** — guard-infeasible cells dropped from ALL arms uniformly (D7 closed).
- **A14** — WGLL values 8–9 checked against every criterion; two non-gating additions. Nothing
  contradicted.
- **A15** — resolver recall fallback; **mine, because the equivalence is a committed check, not
  an assertion** (see §3/§4).
- **A16** — R5's "the floor would then be load-bearing" was the barred conclusion of the FL1-vs-P
  package comparison; corrected to route through FL1-vs-W.
- **The two-sided fame-proxy residual** (A12 addendum): the proxy miscounts 3 of the 7 visible
  "never heard of" as famous, but the error is **conservative** (only makes C2 harder), so no
  rule changed — recorded as a pre-registered read for a 3-of-8 C2 result.

## 6. Numbers computed and not written down

**None.** Every figure is in a committed file: the scorer README (C3=0.164, resolver
recoveries), `band_gap.json` (6.161/1.093, coverage by bucket), `fame_cache.json` (resolved
fame). The band-gap figures are additionally stated at the A12 discharge point in the exec log
and pre-registration, both citing the arm-scorer dir as owner (B5 disposition, closeout).

## 7. Things the owner said, now in a file

- **Routes to artists with no English Wikipedia article: yes, definitely** — and noted the
  question should not have needed asking. Drove the WGLL trigger widening + values 8–9, and
  A12. Recorded in the execution log's A12 entry and `WHAT-GOOD-LOOKS-LIKE.md` value 1's bound.

## 8. In flight / git

- **Nothing running of mine** at retirement (a `doc-auditor` was dispatched for closeout B1;
  its findings are folded in before this note is final, or named here as an escalation list).
- **Branch `track2-sweep`, off `main`, pushed.** No PR opened yet — see closeout D5.
- **Both consultant sessions (documentation + cold-read adjudicator) are retired.** Their work
  is committed with their attributions (`7b2222e`, `6a7007c`, `f981d1b`). This session owned
  all commits.

## 9. Deferred findings — none came due at this seam

Open, with conditions (details: execution log + pre-registration §9's still-open table):

- **P8b** — due now (the harness exists). The next unit's first step.
- **D4** (partly discharged by A11/A12), **D6**, **PR-B**, **O-series** — the sweep and its
  reporting.
- **F1 zero-intermediary guard** — implemented in the mirror/walker (guard G); its
  success-criterion finalisation is due before the sweep's criterion is locked.
- **Consultant's two doc deferrals** (relocate the plan-review block; supersede Phase 1 log
  §2) — due at **Track 2 adoption**, which has NOT happened.
