# Handoff — `LUX-E4` closed, `LUX-E1` run, and `LUX-4` planned, 2026-09-05

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-05-HANDOFF-doc-layer.md`](2026-09-05-HANDOFF-doc-layer.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** All three pieces of work concluded; the degradation tell did not fire.
**No app code changed** — this was a maintenance session that also ran one offline eval. Its
closeout was the maintenance tier, with `A2` (this note) added because the session produced a
seam the tier assumes it will not.

Branches `lux-e4-closure` (**PR #103, merged**) and `lux-e1-arm-b` (**PR #104**).

---

## Start here

**One thing is assigned and it is the owner's**, and it blocks the next session's first task:

**`L4-T1` — the acceptance-bounds decision.** `check_acceptance` runs before `serialise`, and
its bounds were recalibrated for the reverted 117k population, so **a correct rebuild of the
served map is refused and never written**. Recalibrate the bounds back (the plan's
recommendation, read from git at `3aa61f0b`, never invented), or wire the `--criteria` hook
`cmd_build` already reads but no argument supplies. Everything in `LUX-4` waits on it.

Then execute [`plans/2026-09-05-lux-4-links-and-info-card.md`](plans/2026-09-05-lux-4-links-and-info-card.md).
**Recommended execution: inline, not subagent-driven** — the tasks are strictly sequential, so
fan-out buys nothing and each cold subagent re-derives the same six files. The plan names its
own seams at `L4-T7` and `L4-T9`.

## What this session did

1. **`LUX-E4` is CLOSED** and its threshold retired as mis-specified. Its *read* is untouched:
   **UNDEFINED, never a pass.**
2. **`LUX-E1` RAN and returned BYTE-IDENTICAL.** `LUX-4`'s gate is discharged.
3. **The `LUX-4` implementation plan is written**, 11 tasks, unstarted.
4. **`snyk` is authenticated and on `PATH`**; the owed `api/` scan is discharged and clean.

## Claims an editor must NOT revert

- **`LUX-E4`'s read is UNDEFINED, not passed.** Only its *threshold* was retired — because
  `LUX-3`'s control renders nothing when there is no second track, so no result could have
  changed whether it ships. Do not restore "a re-prioritisation trigger that is the owner's".
- **`LUX-E4`'s empty denominator is `DD-F1`, not a new finding.** `TAS-6`'s routing half
  measured zero sub-decile journey interiors on the same 120-pair sample on 2026-07-30. **Do
  not re-open it as a fresh path-quality question**, and do not re-run `LUX-E4`.
- **`LUX-E1` arm A was not run and does not need to be.** Both its inputs are identified.
- **There are THREE `CXA-` leftovers, not one** — drop-list pointer, archive tree, acceptance
  bounds. The revert moved the map and moved none of them.
- **The `LUX-E1` probe adopts nothing and moved no default.** Both pins are per-invocation.
- **The rebuild is ~40 s, not ~23 min.** The live manifest records `elapsed_seconds: 39.2` and
  that timer spans the whole build. The old figure is struck in three places; do not restore it.
- **`LUX-E2` is BLOCKED**, not merely owed: its threshold is stated over exactly the population
  the damaged `TAS-` sample removes.

## What has already been updated — do not re-edit

`NEXT.md` (gate discharged, three leftovers, snyk struck, the fired deferral), the scope
document's §5 (`LUX-E4` closed, `LUX-E1-AM2`, `LUX-E1`'s read, `LUX-E2`'s blocker, the cost
correction), `docs/README.md` (three new rows, three forward corrections), and both analysis
READMEs. The **frozen** `2026-09-04` handoff and execution log were left frozen; their
corrections went forward into their map rows.

## What I know that is not in the durable record

**Two things, and both are now written down here rather than left in the session:**

1. **The `LUX-4` plan's code claims were each grepped against the tree while authoring** — the
   MB dump's record shape, `dsp_ids.py`'s `DSP` map and its line-160 filter, `deezer_ids.py`'s
   pattern, `artifact.py`'s additive-key discipline, `graph_store.py`'s length rule and why
   `deezer_ids` is exempt from it, `ArtistCard.tsx`'s gate, and `ArtistOut`'s three wire
   positions. **The doc-auditor did not re-verify them** (it read the plan at header and task
   boundaries only, and said so). So they rest on this session's checking, not on a second
   reader's — worth a spot-check at `L4-T2` before trusting the payload shapes.
2. **`L4-T1`'s recommendation (recalibrate rather than add a flag) is a position, not a
   menu.** The reasoning: the bounds are stale in exactly the way the drop list and archive
   were, and Option B leaves every future build of the served lineage needing a flag to work.
   Argue with it rather than re-deriving it.

**Nothing is in flight.** No background jobs, no dispatched subagents, no half-written
directories, no dev servers (ports 8000 and 5173 both clear).

## The RCA the owner asked for, since it is not elsewhere

**Why the revert was incomplete:** adoption changed two sides — what is *served*
(`ApiConfig`) and what a rebuild *produces* (drop-list default, acceptance bounds, archive).
The revert commit `7e64265` touched only the first; nothing under `builder/`. Its verification
was `/health`, which is correct for the serving side and **structurally cannot see build-input
drift**. The adoption plan had a revert *criterion* but no revert *procedure* — it judged the
revert path "not the expected one" — and its §3 listed what must **not** be reverted without
ever listing what a reversion must **include**. Sharpest detail: that same plan's Task 7 warned
that *"a wholesale revert is self-consistent and passes"* the `/health` check. The warning was
written three weeks before the revert used exactly that check.

**The rule worth adopting:** a revert criterion and a revert procedure are written together or
neither is. And a rollback's exit check must include a **build-side** step — rebuild and
confirm the sha, which is 40 seconds and would have caught all three leftovers on 2026-09-01.
