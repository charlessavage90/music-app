# Handoff — the `MSW-` map switch, builder and API sides complete at Seam 2, 2026-08-05

**Role: SUPERSEDED on next actions, 2026-08-06, by
[`2026-08-06-HANDOFF-msw-task8-midflight.md`](2026-08-06-HANDOFF-msw-task8-midflight.md)** —
which is the CURRENT handoff. **This document remains authoritative for Seam 2's own
internals** (Tasks 1–7: what was built, the six do-not-revert claims, the two operational
facts). Four of those six claims have since been verified by exercise rather than assertion;
the successor names which. Supersedes
[`2026-08-05-HANDOFF-ulf-filter-fix.md`](2026-08-05-HANDOFF-ulf-filter-fix.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**A seam handoff.** Tasks 1–7 of 12 complete at the plan's own Seam 2, chosen at authoring
time. The tree is clean, no listener on any port, nothing in flight.

**Branch** `msw-package-adoption-plan`, draft PR **#81** open. **The next action is WORK**:
Task 8. Nothing is waiting on the owner except the D6 decision below.

---

## What this work is, and the one thing that must not be misremembered

Shipping `ULC-A4` — candidate data set + trimmed-union connection rule + gentle fame ramp —
as the production map and router, with the merged un-listenable filter on.

**⚠ This adoption is an owner OVERRIDE of the standing `GBL-` null**, whose pre-registered
consequence was *"production stands and Option A closes without adoption"* (margin 3 against
a bar of 5). The owner took it knowingly on 2026-08-05. **Neither `GBL-` nor `CAU-`
licensed it** — `CAU-` §6 bars comparison with today's app at any strength, and `GBL-` §5's
run-once rule still binds that verdict. The authority is his and is recorded as his.
Full reasoning: execution log §0. **Do not describe this work as evidence-backed adoption.**

Governing/operational document:
[`plans/2026-08-05-msw-package-adoption.md`](plans/2026-08-05-msw-package-adoption.md).
Reasoning: [`2026-08-05-msw-execution-log.md`](2026-08-05-msw-execution-log.md).

## What is done

Tasks 1–7. The builder can build with the trimmed-union rule, fetch ListenBrainz listener
counts into the archive, refuse a build whose fame coverage has drifted, and carry
`fame_lb` in the artifact. The API can read that key, rank it at boot, and price a
`known` ramp on it, refusing to boot if the ramp is live over a fameless artifact.

**Nothing is adopted and nothing the owner can press has changed.** `cap_strategy` =
`mutual_knn`, `require_fame` = `False`, `w_known_ramp_fame_pctl` = `0.0`, `graph_path`
unchanged, no artifact built, frontend untouched.

## Which documents are now wrong, and in which direction

- **None known to overstate.** `NEXT.md`, `docs/README.md`, `CLAUDE.md` and the previous
  handoff's role line are all updated.
- **`CLAUDE.md`'s Graph shape section (§"Graph shape") is INCOMPLETE, deliberately.** It
  describes mutual k-NN as the cap without mentioning `trimmed_union`. That is accurate
  about what *ships* today and becomes **false at Task 11**, when the default flips. It is
  listed in Task 11 Step 0 rather than pre-corrected, because correcting it now would make
  the standing layer describe a world that does not yet exist.

## Claims that must NOT be reverted by a well-meaning editor

1. **`require_fame` defaults to `False`, and that is deliberate** (a plan deviation, log
   Task 4). Until the router reads fame, a fame-less build is genuinely valid. Do not
   "fix" it to `True` before Task 11 — it would break every era-pinned analysis caller.
2. **`MSW-G2`'s comment says the mirror's "never as `+ 0.0`" rule is not meaningful here.**
   That is measured, not an oversight: at k = 0 the multiplier is exactly 0.0, so adding
   the term is numerically identical to skipping it. Do not restore the inherited phrasing.
3. **The fame percentile frame is the served artifact's OWN population**, not the `CRE-`
   harness's fixed ruler against the retired artifact. Deviation 2; a shipped ruler pinned
   to a retired artifact goes stale at every adoption.
4. **Nulls take percentile 0.0 and are excluded from the frame.** Including them would make
   a poorly-covered population look uniformly famous — the metric would improve as coverage
   got worse.
5. **The `GBL-` banner is a qualification, not a reversal.** Do not strengthen it: `CAU-`
   may not be used to reopen that comparison.
6. **`trimmed_union` does not reopen `pre_symmetrise`**, which remains deleted on evidence
   and is deliberately absent from `PERMITTED_CAP_STRATEGIES` rather than listed-and-rejected.

## What has already been updated — do not re-edit

`NEXT.md` (new top block); `docs/README.md` (rows for the plan and the execution log,
plus the amended `GBL-` results row); the previous handoff's role line; `CLAUDE.md` (APG1
key list, cost function, depth-graduated-device claim); `.claude/agents/ml-graph-analyst.md`
(seventh cost term); `.claude/agents/doc-auditor.md` (check G2);
`findings/2026-08-04-gentle-arm-blind-listen-results.md` (forward banner only — no finding
altered).

## What I know that is not in the durable record

**Two operational facts, folded in here so the record is whole:**

- The `MSW-G1` byte-identity script is a **scratch file, not committed** — it lives in this
  session's scratchpad and will evaporate. Its content is trivial to recreate (build a
  fixed synthetic archive under default config, sha256 the serialised bytes) and its
  *result* is in the log with the hash. Recreate rather than hunt for it.
- **Two vacuous tests were found by perturbation, and the technique is the transferable
  part.** Both were tests whose stated purpose was to pin an invariant, both were green,
  and neither could fail. Assume the next one exists: perturb before believing a gate.

## Owed, and by whom

- **Owner:** one decision only — **D6**. This session spent **+236 unconditional characters**
  on `CLAUDE.md` correcting three descriptions the work invalidated. Roughly 150 of that is
  strict correction; roughly 86 is a new clause explaining the additive-key rule (*"the last
  two are additive keys, omitted when empty, and the version is NOT bumped for them"*). The
  correction half is the session's call and is taken. **The 86 is growth and is his** — the
  case for it is that a future session adding a ninth key that bumps `FORMAT_VERSION` breaks
  every existing artifact including the served one, and nothing else in the standing layer
  says so. Trimming it is one edit if he declines.
- **Next session (Task 8, and its FIRST step):** **back up `fi_union_snapshot.json` and its
  manifest** before any fetch runs. Gitignored, single-machine, ~93k artists to refetch if
  lost. This is the cheapest-to-lose dependency in the plan.
- **Task 11 Step 0, non-negotiable:** era-pin `cap_strategy="mutual_knn"` **and**
  `require_fame=False` in `grt_score.py`, `calibrate.py`, `cre_build.py`, and correct
  `CLAUDE.md`'s Graph shape section in the same commit.
- **`MSW-V4` at Seam 3:** `ml-graph-analyst` dispatch on the percentile-frame deviation,
  derivation only.
- **Seam 3 is an OWNER STOP.** Verification results (`MSW-V1`–`V4`) go to him before any
  default is flipped, even though the direction is already decided.
- **Unchanged and not `MSW-`:** `ULC-F3` (crawl resume cannot extend) still blocks any crawl
  extension; `ULC-F4` (keep-check name resolution) is its own track.
