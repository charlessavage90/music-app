# Handoff — password removal Track A complete, at the Track B seam, 2026-07-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-27-HANDOFF-migration-phase-d.md`](2026-07-27-HANDOFF-migration-phase-d.md) **as the
document to read first, and on next actions for *this* body of work only.** It does **not** state
project status: for that read [`NEXT.md`](NEXT.md), which owns it.

> **⚠ Read this before assuming the supersession is total — it is not.** The migration handoff's
> **Tasks 9, 10 and 11 are NOT superseded and remain owed.** Task 9 (confirm Backblaze completed
> an upload covering `C:\dev`) still gates Task 11, and Task 11 is still the irreversible deletion
> of the rollback tree. This work touched none of it. Two live bodies of work, two handoffs;
> this one is newer and is where a session should start, but it does not discharge the other.

**Written at a seam** — the plan's own named Track A/Track B seam, not a mid-flight retirement.
Track A is complete, committed and verified. **Nothing is in flight: no subagents, no background
jobs, no listeners on any port.**

**Track A is MERGED to `main`** — PR #39, merge commit `1117d35`, 2026-07-28. Suites re-run on
`main` after the merge: api 214, infra 58. **Start Track B on a fresh branch off `main`**; the
`password-removal-load-hardening` branch is merged and spent (it still exists only because
deleting it was blocked by the tool-permission classifier — deleting it is safe, its commits are
in `main`).
Plan: [`plans/2026-07-28-password-removal-load-hardening.md`](plans/2026-07-28-password-removal-load-hardening.md).
Record: [`2026-07-28-password-removal-execution-log.md`](2026-07-28-password-removal-execution-log.md).

---

## Your job

**Track B, PW-5 → PW-9.** One thing blocks PW-5 and it is the owner's: an ACM certificate for
`musicapp.cmiller.io`, in **us-east-1**, status `ISSUED`. Commands are in the plan at PW-5 step 1.

**The password is still on, and the live site is completely unchanged by this work.**

## What a cold session would get wrong

- **The password must stay on until PW-7.** Every Track B step before it is additive and
  reversible **on purpose**: if the Cloudflare configuration is wrong, the existing gate is still
  protecting the site while that is discovered. **Do not reorder to remove it earlier**, and do
  not treat the ordering as bureaucratic.
- **`max_size=2` in `stack.py:159-165` must NOT be raised.** It reads like an obvious capacity
  fix and it is the cost ceiling. The capacity problem is deliberately being met by shedding load
  at the edge rather than by scaling — which is the *only* reason `G3-A3` (cost ceiling and
  capacity ceiling are the same knob) does not fire. Raising it deletes the only automatic spend
  control, whose sole detector is a billing email up to six hours late.
- **`G3-S7`'s fix is a swap, not a deletion.** The viewer function goes on refusing; it changes
  *what it asks*. Deleting the gate would also delete the SPA fallback and 403 every shared link.
  Replacing it keeps the test coverage rather than discarding it.
- **PW-6 step 6 check 4 is not optional and is easy to skim past.** It confirms the Cloudflare
  secret header actually reaches the origin **while the password is still on**. PW-7 makes the
  site depend on that header; finding out it never arrives *after* the password is gone is the
  precise failure this ordering exists to prevent.
- **`MIG-10` / migration Task 12 is still deliberately NOT done.** Six documents still say the
  project lives under OneDrive, and that is still true of the tree that is still the rollback.
  Do not "fix" them, and do not read this work's edits as licence to.

## What is overturned and must not be reverted

- **A design claim in this project's own plan was wrong and is corrected in place.** The plan
  originally reset the circuit breaker's failure count when its cooldown expired, with a comment
  asserting that *was* half-open behaviour. It is not: a full reset admits another `threshold`
  requests every cooldown, so a permanently dead catalogue costs five calls a minute rather than
  one. The corrected behaviour — count stays at the threshold, next real request is the probe,
  one failure re-opens — is what ships. **Do not "simplify" it back.**
- **`G3-A5` is CLOSED, not deferred.** The review listed the CloudFront-domain lock-in as
  deferred-with-unbounded-cost. Moving to `musicapp.cmiller.io`, a hostname the owner has
  confirmed permanent, closes it. It is no longer a reason for anything.
- **`G3-A3` does not fire under this design.** Argued out of scope before any code, and the
  reasoning is above. It is not an oversight and should not be re-added to the blocking set.
- **`G3-S4` is only half addressed, deliberately.** The amplification half (log volume) is
  closed. The **disclosure** half — what the app records about people, and that it says so
  nowhere — is untouched and is the owner's call.

## What I know that is not in the durable record

- **The `--prune` publish deferral comes due at Track B's first deploy.** `NEXT.md` records it as
  "the next deploy after this one", skipped at cutover because the bucket was empty. PW-5 step 6
  is that next deploy. **Nothing in the plan currently reads this deferral**, which is exactly the
  failure mode `closeout` **A3** names — a satisfied condition nobody was scheduled to read.
  Handle it at PW-5 or restate the condition. (Written as `closeout A3` rather than bare `A3`:
  that token already means a Track 2 arm and a Gate 2→3 architect finding.)
- **`docs-lint.sh`'s `CAND` output has a large pre-existing tail** — ~37 restated-figure
  candidates across path-quality documents this work never touched. They do not affect its exit
  code. **Do not read a clean Track A lint as a clean corpus**, and do not start fixing them
  inside this branch; that is a separate, deliberate act.
- **`closeout`'s D6 command names the OLD OneDrive memory path. It still RUNS** — the migration
  deliberately kept a duplicate under the old slug as the rollback — **so it fails silently rather
  than loudly**, which is worse. Measured with the correct path instead
  (`~/.claude/projects/C--dev-music-app/memory`). Same class as `MIG-10`, so it is Task 12's
  business and **not to be fixed early**.
- **⚠ The two memory directories have already DIVERGED**, and this is new information for
  migration Task 11. `MEMORY.md` is **2,631 characters under the old slug and 2,647 under the
  new** — the live copy has been edited since the migration copied it. Consequences, both small
  but real: D6 run with the skill's verbatim path is now wrong, not merely stale; and **the
  retained old-slug copy is no longer a faithful rollback** of memory. Twelve files each side.
  Worth thirty seconds before Task 11 deletes one of them.
- **Frontend e2e was not run.** It needs a hand-started API and nothing in Track A touches the
  frontend. It is not a failure, and it is not evidence either.
- **The suite counts live in the execution log's "State at the seam" table and nowhere else.**
  They were restated in three documents and disagreed for as long as it took the doc audit to
  notice, because `closeout`'s `D1` ran before a later fix dirtied the tree. Cite that table.

## What was decided against

- **AWS WAF.** The review assumed it; the owner already runs Cloudflare free tier with a domain he
  owns, which does the same job for nothing. Do not reintroduce a standing WAF charge without a
  reason the free tier cannot cover.
- **Spending Cloudflare's five custom security rules.** Confirmed available and unused. Left as
  deliberate headroom — they are the lever if one IP-keyed rate-limit rule proves too blunt, and
  spending them now would be adding controls with no evidence they are needed.
- **Making `ExclusionIn.reason` a `Literal`.** It is the natural tidy-up and it is a behaviour
  change: `test_an_unrecognised_reason_is_still_coerced_to_dislike` already pins the
  fallback-to-dislike behaviour that the deploy design relies on.
- **Reading the request stream to bound chunked bodies.** The Content-Length guard covers every
  path CloudFront and Cloudflare can produce; counting the stream costs more than the case is
  worth. Deferred with that condition.
- **Fixing the `CAND` figure tail, and fixing the stale D6 path.** Both out of scope, both
  recorded above rather than silently left.
