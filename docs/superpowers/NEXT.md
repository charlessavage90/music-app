# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-28, after `PW-8`.**

---

## Next

> ## 🔓 The site password is GONE, and the site is public.
>
> **`https://musicapp.cmiller.io`** — no username, no password. Confirmed in a real browser on
> a new device in an incognito window, 2026-07-28, which is what rules out cached credentials.
> **Send anyone the URL and nothing else.**
>
> The old `d2n3xqz3pttguf.cloudfront.net` address **redirects** and keeps its query string, so
> every link shared before today still works.

**One thing is owed and it is the owner's: the queued use-the-app test**
([`TEST-QUEUE.md`](TEST-QUEUE.md), the 2026-07-28 entry). It carries the **iPhone script**,
which is the only unanswered question that matters — no test, emulator or Android device can
tell us whether a clip plays at all on an iPhone, and `G3-F1` means a failure there is silent.

**`PW-9` is the only unrun task in the plan** — the concurrency ladder against the live
origin. It is gated on the owner's approval, not on readiness. It is not a blocker for
anything currently planned.

Record: [`2026-07-28-password-removal-execution-log.md`](2026-07-28-password-removal-execution-log.md).
Plan: [`plans/2026-07-28-password-removal-load-hardening.md`](plans/2026-07-28-password-removal-load-hardening.md).
Runbook: `infra/README.md` — **§1a is the front door, §8a is how to re-verify it.**

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The password coming off is *not* Gate 3. The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). This work implemented the **minimum load-related subset** that let the password come off, and nothing more. |

## Closed — do not re-plan or re-investigate

- **The OneDrive migration is COMPLETE, all twelve tasks.** Task 9 discharged by restore;
  Tasks 10 and 11 **closed by owner decision** (the old tree is kept indefinitely as an
  archive — he will delete it himself if he ever wants the space); Task 12 done. **Nothing on
  this axis is owed by anyone.** The old tree is **never the working tree** — do not edit it.
- **`G3-A5`** — closed by the move to `musicapp.cmiller.io`, a hostname the owner has
  confirmed permanent.
- **`G3-A2`** — closed by the Cloudflare rate limit.
- **`G3-S7`** — closed by `PW-7`. The gate was **replaced, not deleted**.
- **`G3-A3` does not fire** under a shed-load-at-the-edge design. Argued out before any code.
  Do not re-add it to the blocking set.
- **In-app browsers (WhatsApp, Instagram) suppressing the auth dialog** — a listed Gate 2
  risk, **now structurally impossible**: there is no dialog.
- **`RMD-6`, `RMD-11`, `RMD-12`, `RMD-13`, `FRO-1`, `FRO-4`**, the `DEP-33` blockers, the
  Gate 1 clip work, **Track 1**, **Track 2 / 2F / the ceiling toll**.
  - ⚠ **One exception, live:** `BYP-13` — a card playing a clip by a *different artist of the
    same name*. Not path-quality work and **not inside the pause**.

## Must not be changed, and each has a reason

- **`max_size=2` (`stack.py`)** — it is the **cost ceiling**, not a capacity setting, and it
  is the only automatic spend control there is. Raising it deletes that, with a billing email
  up to six hours late as the sole detector. It reads like the obvious capacity fix. It is not.
- **App Runner is excluded from CDK tagging** — tagging it forces a replacement that
  **cannot succeed** (explicit `service_name`; CloudFormation builds the replacement first).
  Measured by a real deploy that failed and rolled back. `test_app_runner_is_deliberately_left_untagged`
  pins it.
- **The ACM validation `CNAME` at Cloudflare** — ACM reuses it to auto-renew. Delete it and
  the certificate silently fails to renew in ~13 months and the site goes down.
- **The rate limit is `10 / 10 s`, not the plan's `30 / 60 s`** — the Cloudflare plan offers
  only 10-second periods. Do **not** rescale it linearly to `5 / 10 s`; see `infra/README.md`
  §1a for why.

## Deferred, with conditions

| Finding | Condition |
|---|---|
| **The rate limit's headroom** — one fast user peaked at 6 requests/10 s against a limit of 10, so **two behind one IP would be blocked** | **Before sharing beyond friends and family.** Carrier-grade NAT puts strangers on one address. The five unspent Cloudflare rules are the lever. ⚠ The 6 was measured while stress-testing, *not* reading paths — treat it as an upper bound on an attentive user, not typical use. |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** Rotating means changing Cloudflare and redeploying *together*; between the two the site refuses everyone. Anyone holding it can bypass the rate limit. |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service.** Nothing restores them; the two `tag-resource` calls are in `infra/README.md` §7. |
| The `--prune` publish pass | **The next FRONTEND publish** (`sync_frontend.py`), not the next `cdk deploy`. ⚠ **Corrected 2026-07-28** — the Track B handoff said `PW-5`'s deploy was the trigger. It was not: `PW-5`–`PW-7` were infrastructure-only and never touched the SPA bucket, which still holds the cutover's objects. |
| Medium CSRF in `react-router@7.18.1` | Revisit **only if** the app adopts React Router's unstable RSC APIs. Not exploitable without them. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is **inert** | **Only if someone adds `viewport-fit=cover`.** Latent, not live. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every path CloudFront and Cloudflare can produce. |
| **`G3-S4`'s disclosure half** — what the app records about visitors, and that it says so nowhere | **The owner's call.** The amplification half (log volume) is closed. Now more pressing: the visitors are strangers. |

---

## Path quality is PAUSED — owner decision, 2026-07-25

**A separate track from the gates, and it is stopped. Resuming it is the owner's trigger,
never a session's.**

- Track 2 and Track 2F **both returned nulls**; the ceiling *ordering* measurement came back
  **WIDE**. **Nothing adopted, no shipped code changed, no blind listen run.**
- **Track 2F's full-strength toll re-run is already EXECUTED. Do not run it again.**
- **The live candidate is a builder-side p99 rescale, and it is NOT pre-registered. Do not
  start it.**

**If it is ever resumed, the entry point is
[`2026-07-26-RESUME-BRIEF-path-quality.md`](2026-07-26-RESUME-BRIEF-path-quality.md)** — read
it in full first. It is not itself a resume signal.

**Before acting on any path-quality claim**, read
[`2026-07-22-phase1-execution-log-and-graph-defect.md`](2026-07-22-phase1-execution-log-and-graph-defect.md)
§2 — and §2.12 first, because it retracts a central claim of §2.9. The three quantities that
are not interchangeable (**degree ≠ popularity ≠ fame**) are live hazards.
