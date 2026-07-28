# Handoff — password removal complete, the site is public, 2026-07-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-28-HANDOFF-password-removal-track-b.md`](2026-07-28-HANDOFF-password-removal-track-b.md)
on next actions **and** on status — that document is now fully spent. It does **not** state
project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**Written at a seam** — the plan's last implemented task, not a mid-flight retirement. `PW-5`
→ `PW-8` are complete, committed, deployed and verified. **Nothing is in flight: no subagents,
no background jobs, no listeners on any port** (8000, 5173, 8138, 8139 all checked free).

**PR [#42](https://github.com/charlessavage90/music-app/pull/42)**, branch
`password-removal-track-b`, five commits. **Not merged.**

Record: [`2026-07-28-password-removal-execution-log.md`](2026-07-28-password-removal-execution-log.md)
— Track B appended per task. Runbook: `infra/README.md` §1a and §8a.

---

## The one-line state

**The site password is gone. `https://musicapp.cmiller.io` is public**, behind a Cloudflare
front door with a rate limit. Confirmed by the owner in a browser, new device, incognito.
**No application code changed** — no routing, no graph, no cost function, no clips.

## Your job

**`PW-9` is the only unrun task** — a concurrency ladder against the live origin. It is gated
on the **owner's approval**, not on readiness, and it blocks nothing.

**The one thing genuinely owed is the queued use-the-app test** ([`TEST-QUEUE.md`](TEST-QUEUE.md),
2026-07-28), which carries the **iPhone script**. Only a person with an iPhone can discharge it.

## Which documents are now wrong, and in which direction

- **Both plans are historical and still read as though nothing has run.**
  `plans/2026-07-28-password-removal-load-hardening.md` and
  `plans/2026-07-26-track-b-infrastructure.md` both contain `-u "artistpath:$PASSWORD"` and
  `ARTISTPATH_DEPLOY_PASSWORD`. **Leave them.** They are records of intent at the time; the
  execution log wins on what happened.
- **The plan is wrong in two places that matter, and both are corrected in the log rather
  than in the plan:**
  - `PW-6` check 4 aims at the wrong leg — it cannot be verified at the origin, because
    CloudFront forwards only `x-journey-id` and `content-type` to App Runner.
  - `PW-6`'s rate-limit period assumes 60-second windows. The owner's Cloudflare plan offers
    only 10-second ones.

## What was overturned and must NOT be reverted

- **The rate limit is `10 / 10 s`, not `30 / 60 s`, and must not be rescaled linearly to
  `5 / 10 s`.** A short window is burst-hostile; because the block is also 10 s, `10 / 10 s`
  reproduces the plan's sustained ~0.5 req/s per IP while keeping burst headroom.
- **App Runner is excluded from CDK tagging.** Tagging it forces a replacement that *cannot
  succeed* — explicit `service_name`, and CloudFormation builds the replacement first.
  Measured by a deploy that failed and rolled back.
  `test_app_runner_is_deliberately_left_untagged` pins it; deleting that test re-breaks the
  deploy.
- **`PW-7` replaced the gate, it did not delete it.** Deleting the viewer function's gate also
  deletes the SPA fallback and 403s every shared link.
- **The `--prune` deferral did NOT come due.** The previous handoff said `PW-5`'s deploy was
  the trigger; it is the next **frontend** publish. Corrected in that handoff in place, struck
  rather than deleted.
- **`~1.9 s per path request` is CORRECT** and was briefly and wrongly reported as refuted.
  Latency is driven by the artist **pair** (68 ms → 563 ms), not bypass depth. A single-pair
  probe is not evidence about this.

## What has already been updated — do not re-edit

`NEXT.md` (rewritten wholesale), `TEST-QUEUE.md` (new entry at top), the execution log
(Track B appended, title corrected), `infra/README.md` (§1, §1a, §7, §8, §8a), `docs/README.md`
(three rows), and the previous handoff's role line and `--prune` bullet.

**The doc audit ran and found three HIGH defects. All three are fixed** — §1a's re-verification
block still used the deleted password variable, its abuse loop still sent Basic auth, and the
previous handoff still carried the wrong `--prune` claim.

## What I know that is not in the durable record

**Nothing of substance — the three items below are the residue, and they are small.**

- **The first `429` index varies between 11 and 12** across runs, with window alignment. Now
  written into `infra/README.md`; noting it here because a future reader seeing 12 against a
  documented 11 might file a defect.
- **`cdk diff`'s two methods disagree by design.** The default change-set method does not
  report tag-only changes (4 resources vs 12) but *does* report replacements accurately. Both
  readings are needed. In the execution log; repeated here because it is easy to trip on.
- **`filter event = "path"` returns nothing in CloudWatch Logs Insights** even though
  `stats count() by event` counts them. Use `ispresent(bypass_depth)`. In `infra/README.md` §1a.

## What was decided against

- **Raising `max_size=2`** — it is the cost ceiling, not a capacity knob.
- **Removing App Runner's explicit `service_name`** so CloudFormation could tag it properly.
  It would work, but it is a replacement with real downtime and the name appears in the runbook.
- **Enabling Cloudflare's automatic key exchange / post-quantum origin handshake now.** It
  works — CloudFront already negotiates `X25519MLKEM768` — but it was deferred so `PW-6`'s
  gates ran with one variable rather than two. **It is a genuine small win and is still worth
  enabling**, followed by re-running §8a's four checks.
- **Broadening the rate limit to `starts with /api/path`.** `equals` is correct: `POST
  /api/path` is the only pathfinding route and the frontend requests exactly that.
- **Using `console.log` in the viewer function to observe the front-door header.** A CloudFront
  Function's stdout is what the test harness parses as JSON; it broke 10 tests.
