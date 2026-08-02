# Handoff — `TAS-` Task 8 and the adopted no-release drop rule, 2026-08-01

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-01-HANDOFF-label-weighting.md`](2026-08-01-HANDOFF-label-weighting.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a SEAM handoff, not mid-flight.** Everything is committed and pushed, nothing is
in flight, no subagent is running, no background job survives, no port is listening, and
the tree is clean. Two pieces of work both reached their end: `TAS-` Task 8 completed the
tag probe, and the no-release tail question became an **adopted decision**.

## What this work is

Two threads, one session. PR **#61**, branch `tas-task8-findings`.

1. **`TAS-` Task 8** — the findings document the probe had owed since Tasks 1–7 finished.
   Record: [`2026-07-30-tag-discrimination-execution-log.md`](2026-07-30-tag-discrimination-execution-log.md)
   §17. Findings: [`findings/2026-07-30-tag-discrimination.md`](findings/2026-07-30-tag-discrimination.md).
   **The `TAS-` probe is now complete through all eight tasks.**
2. **The no-release tail** — from open product question to adopted drop rule. Record:
   [`2026-08-01-label-weighting-execution-log.md`](2026-08-01-label-weighting-execution-log.md)
   §8. Probes: `builder/analysis/2026-08-01-label-weighting/tail_*.py`.

## The six claims that must not be reverted

1. **The drop rule is ADOPTED, not proposed.** Keep a release-less artist only where a
   commercial-DSP link exists **and** a clip resolves: **7,035 of 7,686 dropped, 651 kept**,
   frozen at `tail_droplist.json` (sha over sorted MBIDs `d876c7ba…`). A successor
   **applies** it; it does not re-open the rule.
2. **The drop list is a 2026-08-01 SNAPSHOT and must never be re-resolved at build time.**
   Not a preference — spec §9 requires byte-identical builds and `build_from_archive` is
   offline by a hard rule with a replay test proving it. A build that called Deezer would
   make two builds of one archive disagree.
3. **⚠ The "a filter would cut real artists" argument is REFUTED and must not be revived**
   from the committed delivered-artist list, which is exactly what will tempt the next
   reader. This session made that argument on Sara Quin, Reed Mullin, Mike Kerr, Jason
   Evigan and Gabriela Robin; the owner refuted it on the product's own terms — the app
   recommends things to *listen to*, so the unit is a body of work, not a person, and every
   one of those names is a performer catalogued apart from the band holding the releases.
   The refutation is recorded in `tail_exposure.py`'s docstring beside the list.
4. **`REQ-42` says the obscurity requirement is a GRADIENT, not a floor** — and **the
   `DD-F1` defect ruling is UNAFFECTED**. A famous-to-famous pair cannot move *at all*, and
   a gradient of zero fails `REQ-13` without reference to any band. Do not read `REQ-42` as
   softening the defect.
5. **`REQ-42`'s out-of-sequence placement in §8 is DELIBERATE and is now documented as
   such.** A documentation audit called it a defect; the rule's own category-change clause
   rules that reading out. Do not "fix" it by moving it into §9.
6. **The measured `BYP-13` wrong-artist rate is a live product defect, independent of the
   tail decision.** It survives whatever happens to the drop list, and it is now measured
   rather than suspected. Figures: `tail_clips.json`.

## Already updated — do not re-edit

`NEXT.md` (status block, the `TAS-` section, five deferral rows including two struck, the
Snyk count corrected 4 → 6), `docs/README.md` (one new row, four edited), the `TAS-`
execution log (§17), the `WGT-` execution log (§8), `PRODUCT-REQUIREMENTS.md` (`REQ-42`,
the `DD-F1` annotation, and the identifier-ordering note), the probe plan's role line and
Task 8 checkboxes, both 2026-08-01 handoffs' status lines, and the probe directory
`README.md` (two script rows).

## What I know that is not otherwise in the durable record

- **The rule's only disagreement with the owner's 20 verdicts lands on the one artist he
  found hardest to call.** He said so unprompted about SoulAvenue after seeing the result.
  That is a better outcome than the tally suggests — the rule is not making a confident
  error, it is landing on his own boundary case — but it is n = 1 and the rule was partly
  chosen by looking at those same 20, so it must not be quoted as validation.
- **Three candidate rules all scored zero false positives on the 20.** That sample separates
  "the bare filter loses both keepers" from "the refinements do not" and **nothing finer**;
  their differing cut counts are noise. Choosing among them was never evidence-driven —
  the conjunction was picked because the clip check is what the owner authorised.
- **The delivered-artist composition warning is still true even though the conclusion drawn
  from it was wrong.** Delivered artists really do differ from the population (median degree
  15 vs mostly 1–5). Do not discard the warning along with the refuted inference.
- **`tail_signals.py`'s artist-**type** split was not asked for and is the strongest single
  discriminator found** — the tail is overwhelmingly individual people and untyped entries
  rather than bands. Any successor rule should consider type before adding more link
  sources.
- **The 322 GiB release dump and the 17.2 GiB artist dump are both on disk** under
  `builder/scratch/mb-json-dumps/`. The artist pass is ~4 minutes; the earlier claim that
  the release dump had been deleted was already corrected in `NEXT.md`.
- **Operational:** the clip pass is ~45 min for 1,402 artists with a checkpoint every 25;
  it completed with zero refusals. `PYTHONIOENCODING=utf-8` is required — the tail is full
  of CJK names.

## The open decision, and what I would do

**Whether the post-drop graph owes a blind listen (`REQ-38`) before adoption.** It is in
`NEXT.md`'s table, raised and unanswered, and deliberately separated from the rule's
acceptance, which is closed.

**If I were continuing: I would treat it as owed.** The *rule* was decided on the owner's
own listener judgment, so nothing offline overrode him — but the drop moves every surviving
artist's popularity marginal and reroutes every pair, and nothing has heard the result.
That is a different question from whether the artists deserved dropping.

**What I would not do:** wire the list into the builder before the cap re-evaluation track
resolves. That track may reshape the build, and a drop rule landing first would make its
attributions ambiguous — the same reasoning that keeps the tag-based degree limiter
separate.
