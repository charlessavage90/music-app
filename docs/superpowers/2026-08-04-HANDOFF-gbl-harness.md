# Handoff — the `GBL-` blind-listen harness is built, 2026-08-04 (later)

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-04-HANDOFF-gbl-plan.md`](2026-08-04-HANDOFF-gbl-plan.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**This is a SEAM handoff.** The plan is executed to its last task: all 8 tasks committed,
30 harness tests green, branch pushed, draft **PR #77** updated. Nothing is in flight — no
background job, no subagent, no listener on any port (8000/5173/8138/8139/8765 all checked
empty at closeout, and none was started).

**The listen has NOT been run.** No journey exists on either arm. `gbl_generate.py` has
never been executed.

## The next work, and who does it

**A fresh, mechanics-only RUNNER session** executes
`builder/analysis/2026-08-04-gentle-arm-blind-listen/RUNNER-BRIEF.md` and nothing else.
That brief is self-contained by design. **That session must not have executed the plan**,
and must not read `docs/superpowers/findings/`, `NEXT.md`'s result paragraphs, spec §1–§2,
or any execution log — including this one.

After the listen, **the write-up of `gbl_result.json` belongs to a further fresh session**
(the `CRE-` Stage-3 rule: the reader of results did not run them).

## Which documents govern

[`specs/2026-08-04-gentle-arm-blind-listen-design.md`](specs/2026-08-04-gentle-arm-blind-listen-design.md)
(`GBL-`) governs and **wins wherever the plan disagrees**. Its §8 now carries `GBL-AM1`
(the eight approved pairs) and a `GBL-CORR` corrections series. The plan
([`plans/2026-08-04-gentle-arm-blind-listen.md`](plans/2026-08-04-gentle-arm-blind-listen.md))
is **COMPLETE, not live**. Reasoning:
[`2026-08-04-gbl-harness-execution-log.md`](2026-08-04-gbl-harness-execution-log.md) —
read its **§5** before touching anything, it names the one thing that was not verified.

## Claims that must not be reverted

Everything in the previous handoff's list still stands (V0 ≠ `E-S0`; margin ≥ 5 of 16;
`GBL-Q1`/`Q2` wording frozen; clips name-based on **both** arms; runs once; nothing adopts
on any verdict; the four `CRE-R2` qualifiers travel; the re-crawl decision untouched). Six
more from this session:

1. **`GBL-CORR1` is a correction, not an amendment.** §5's branch table said `≥ 3` while
   §5's prose, worked examples and arithmetic said `≥ 5`. The table was the stale half.
   Do not "restore" 3, and do not renumber `GBL-CORR` into the `GBL-AM` series.
2. **The hub set is frozen on V0 and mapped by MBID**, not re-derived per arm. Reverting
   this makes the §7 ear-tracking table's cross-arm comparison meaningless — node ids are
   not shared between artifacts. Log §3.1.
3. **`assert_page_data_clean` must not go back to scanning artist names.** It would abort
   generation on The Cramps or Louis Armstrong. The replacement is stronger, not laxer.
4. **`ear_tracking` reports `fame_rows` beside `fame_lower`.** Collapsing them back
   re-introduces a bias toward the arm under test. Log §2.2.
5. **`GBL-Q1`/`Q2` are each one unbroken string literal in `gbl_page.html`**, with a
   comment saying why. Reflowing them across a `+` silently disables the frozen-wording
   test.
6. **The surviving Snyk LOW is accepted with a revival condition** written at
   `_read_export`. Do not re-accept it silently if that condition is met; fix it.

## Already updated — do not re-edit

`NEXT.md` (new top block; the plan block's next-action discharged), `TEST-QUEUE.md` (new
N/A entry, `(latest)` moved), `docs/README.md` (rows for this handoff and the harness
execution log; the plan handoff's row marked superseded on next actions), the spec's §8
(`GBL-AM1` + `GBL-CORR1`), and PR #77's body.

## What this session knew that is now in the durable record

Execution log §2.2 (all six plan-code defects, with the two that mattered spelled out),
§3.3 and §3.4 (two paths considered and deliberately dropped — pre-gate feasibility
checking, and running generation "without looking"), §5 (the unverified generation path and
exactly what was and was not done about it), and §7 (the standing-layer delta is the
**owner's** memory edit, not this session's).

**Nothing else is held back.**

## One thing owed that is NOT a `GBL-` item

`memory/no-commercialization-ruling.md` (the owner's 2026-08-04 monetization ruling) says
on its face that it is **not yet in the repo record** and that the next writing session
should land it. This session did not: it is a product ruling with no connection to the
blind listen, and it belongs in `PRODUCT-REQUIREMENTS.md` rather than buried in a `GBL-`
closeout. Raised to the owner; still open.

Also still open and not this track's: the **eight `TEST-QUEUE.md` entries dated
2026-07-22 to 2026-07-27**, `QUEUED` and unruled-on across three closeouts now.
