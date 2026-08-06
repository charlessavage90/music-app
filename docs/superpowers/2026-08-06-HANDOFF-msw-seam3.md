# Handoff — the `MSW-` map switch, Seam 3 reached, 2026-08-06

**⚠ SUPERSEDED 2026-08-06 on next actions by
[`2026-08-06-HANDOFF-msw-adoption.md`](2026-08-06-HANDOFF-msw-adoption.md)** — the owner gave
the Seam 3 go, and Tasks 11 and 12 have both run: the map switch is adopted and deployed.
**Remains authoritative for Seam 3's own internals** — the Task 10 verification results
(`MSW-V1`, `MSW-V2`, `MSW-V2B`, `MSW-V3`) and its eight claims-not-to-revert, all of which
still stand. Its Task 11 obligations (Step 0's era-pins, Step 0b's agent-definition
correction) are **discharged**; the Pino Palladino observation it names as the sharpest input
is now tracked as **`CLIP-1`**.

*(Original role:)* **ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-06-HANDOFF-msw-task10-midflight.md`](2026-08-06-HANDOFF-msw-task10-midflight.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**A SEAM handoff, not mid-flight.** Task 10 is complete, Seam 3 is reached, and the work is at
its designed stopping point. **The next action is the owner's decision**, not work.

**Branch** `msw-package-adoption-plan`, **PR #81 — MERGED 2026-08-06** at `aafcd6e` on the
owner's instruction, one seam earlier than the plan intended (it had the merge at Task 12).
**Tasks 1–10 are therefore on `main` with every default still off: merging landed the
capability and adopted nothing.** **Tasks 11–12 start from a NEW branch off `main`** — this one
is spent. Tree clean.
**Two detached servers are deliberately left running** — see "Anything in flight".

---

## What this session did

Picked up the mid-flight handoff, ran `session-start`'s cold-read check, and got the owner's
confirmation before touching anything. He confirmed the `MSW-V2` → `MSW-V3` → Seam 3 sequencing
and **authorised one addition**: the journey-diff measurement `MSW-V4` had named and declined to
run. That became `MSW-V2B`.

Reasoning and figures are in the execution log's **"Task 10 continued — the successor session"**
section, and the raw numbers in `builder/analysis/2026-08-05-msw-verification/`. Cited here,
never restated.

- **`MSW-V2`** — exposure re-measured. A report row, not a gate; **no branch assigned and none
  supplied**.
- **`MSW-V2B`** — the frame deviation **does** change routes at depth. Not in the plan; folded
  in on the owner's authorisation.
- **`MSW-V3`** — the app boots, presses and plays on the new artifact, under both the shipped
  default and the Task 11 configuration.
- **`B2`/`B3`/`B4`** — the three checks the previous handoff deferred, now run against a
  finished artifact.

## Which documents are now wrong, and in which direction

**None are known-wrong.** `NEXT.md` was rewritten this session to point at the owner's decision
rather than at more work, and the previous handoff's role line now names this note. The
execution log, the plan's Task 10 ticks, `TEST-QUEUE.md` and `docs/README.md` are all current.

**`CLAUDE.md` still needs no correction and was not touched.** Its "Graph shape" section remains
accurate about what *ships* today and becomes false only at **Task 11**, where its correction is
already listed in that task's Step 0.

## Claims that must NOT be reverted by a well-meaning editor

**Everything in the three previous handoffs' lists still stands in full** — in particular the
`--require-fame` `store_true` rule, both flags being non-optional on the Task 9 build, the
acceptance recalibration having moved the centre and not the tolerance, `PRE_MSW_ACCEPTANCE`
being era-pinning rather than duplication, `MSW-V4`'s deviation being two knobs, and the
21-node null-pricing gap being deviation 3 rather than 2. Additionally:

1. **`MSW-V2`'s paired median reads zero and that is not an error.** The class is concentrated
   in a minority of journeys, so a median over mostly-identical slots reads zero while the mean
   moves by double digits. This is **`ULC-R1`'s recorded statistic defect reproducing**, which
   `ULC-` results deliberately did not patch. **Do not patch it here, and do not report the
   median alone.** Median, mean and the three sign counts travel together, and the caveat is
   stored beside the figure in the JSON so it cannot be separated from it.
2. **Two `MSW-V2` slots got WORSE.** Tame Impala → Fountains Of Wayne and Led Zeppelin → Guster,
   both at twenty presses. Any summary of `MSW-V2` that omits them is wrong even though every
   number in it is right.
3. **`MSW-V2`'s share is an UNDER-count in a known direction.** 46,382 of the artifact's 58,838
   nodes were never in the census population. A low share is evidence the *known* class was
   removed and is **not** evidence that none remains.
4. **`MSW-V2B`'s result splits and both halves must travel.** Nearly half the broader famous
   pairs change at twenty presses; the eight pairs actually listened to barely move. Neither
   half alone is the finding.
5. **`MSW-V2B` is HYPOTHETICAL until Task 11.** It runs at a ramp of `0.01`. At the shipped
   default of `0.0` the ramp is not added at all and the two arms are identical **by
   construction**. It says nothing about what the app does today.
6. **`MSW-V2B` measures whether journeys DIFFER, never whether they are BETTER.** It carries no
   quality judgement in either direction and is not evidence for or against adoption.
7. **The ramp-on hand run showed zero class artists in 41 cards. That is NOT a measurement.**
   Three pairs is a hand check. `MSW-V2` is the measurement. Recorded explicitly so the number
   cannot later be picked up as though it were one.
8. **"The clip resolves" is not "this artist has music of their own."** Pino Palladino is in the
   un-listenable class, survived the filter, reached a real card, and his clip resolved happily
   to a charity-ensemble track. **No automated check in this pipeline distinguishes the two
   properties.** This is the sharpest input to the Seam 3 decision and must not be softened into
   "no dead cards were found", which is separately true.

## What has already been updated — do not re-edit

The execution log (the Task 10 continued section), the plan (Task 10 Steps 1–4 ticked),
`NEXT.md`, `TEST-QUEUE.md` (one QUEUED entry), the previous handoff's role line, this note, and
`docs/README.md`'s rows.

## What I know that is not in the durable record

**Empty, with one exception that is now folded in rather than left here:** the owner stated in
conversation that he will **take option B — press the app himself before starting the next
session**. That is why two servers are running and why `TEST-QUEUE.md` carries an entry, and it
is recorded in both places rather than only here.

**Pre-authorisations from the previous session did NOT carry forward and were not assumed to.**
The one authorisation this session acted on — folding in `MSW-V2B` — was asked for and given
fresh.

**Hard stops still standing and NOT discharged:**

> do NOT start Task 11 or flip any default — Seam 3 is mine.

> *"The last session was not long-lived, but seemed to make a few errors along the way. Verify
> its work as you go."* — honoured: the handoff's `load_cell` claim was checked against
> `ulc_exposure.py:119` before being relied on, the artifact's sha was recomputed rather than
> trusted, and `require_fame`'s structural inertness was read out of `pipeline.py:434` rather
> than inferred from node counts.

## Anything in flight

**Two detached servers, deliberately, for the owner's option-B hand test.** Nothing owns them;
they survive this session ending.

| Port | PID | What | Started |
|---|---|---|---|
| 8000 | 249336 | API on the candidate artifact, **ramp `0.01`** — the Task 11 configuration | 2026-08-06 08:24 |
| 5173 | 199836 | Vite dev server | 2026-08-06 08:24 |

Both started **after** HEAD, so they serve the work being tested. The ramp is a **scratchpad
factory override** (`msw_v3_rampon.py`, outside the repo); `config.py` is untouched and killing
the processes returns everything to today's behaviour.

**Nothing else.** No background jobs, no half-written directories, no uncommitted files.

## Owed, and by whom

- **Owner:** the Seam 3 decision — go / no-go on Task 11. He has said he will press the app
  first. The report's four options are in the closeout message and the PR body.
- **Next session:** nothing until he decides. If the answer is go, **Task 11 Step 0 first and
  it is non-negotiable** — era-pin `cap_strategy="mutual_knn"` **and** `require_fame=False` in
  `grt_score.py`, `calibrate.py` and `cre_build.py`, and correct `CLAUDE.md`'s Graph shape
  section **in the same commit**. The fourth sibling,
  `builder/analysis/2026-07-23-acceptance-bounds/check.py`, is already era-pinned and needs
  nothing.
- **⚠ A FIFTH Task 11 obligation, found by this closeout's `B5` sweep and NOT previously on
  any list.** `.claude/agents/ml-graph-analyst.md:50` states that *"`w_degree_hub` and
  `w_known_ramp_fame_pctl` both default to 0.0, so both terms are inert unless deliberately
  set."* **That is true today and becomes FALSE at Task 11**, when the ramp default goes to
  `0.01`. It must be corrected **in the same commit as the flip**, alongside `CLAUDE.md`'s
  Graph shape section. Left alone, a dispatched graph analyst is auto-loaded a definition
  telling it the ramp is inert while the app is routing on it.

  **Do not correct it now — it is currently accurate**, and this is a scheduled obligation
  rather than a live defect. Noting it here because it is a **defect of absence**: nothing in
  Task 11's own step list mentions this file, and no grep for a stale identifier can find a
  sentence that has not yet become wrong. **This is the same file, and the same failure shape,
  as the 2026-07-23 incident recorded in `CLAUDE.md`** — which is why the sweep looked at it.
- **Unchanged and not `MSW-`:** `ULC-F3` (crawl resume cannot extend) still blocks any crawl
  extension; `ULC-F4` (keep-check name resolution) is its own track. **`ULF-3`'s first half is
  satisfied by Task 12, which has not run** — so it stays open and must be **re-tested** at the
  next closeout rather than copied forward.
- **Deferred by this session, with its condition:** the un-listenable census covers only 12,456
  of the artifact's 58,838 nodes. **Condition — before Gate 2**, or immediately if the owner's
  hand test finds more than one card of the Pino Palladino shape. Not scheduled; it is option D
  in the Seam 3 report and therefore his call.
