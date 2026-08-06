# Handoff — the clip cover-art fix, shipped to production, 2026-08-06

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-06-HANDOFF-msw-adoption.md`](2026-08-06-HANDOFF-msw-adoption.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff, not mid-flight.** The work is finished, deployed and verified.

**Branch** `clip-cover-art-fix`, **PR #85 — OPEN, not merged**, off `main` at `ff6b428`.
Commits `641ced7` (fix) and `9183893` (runbook). Tree clean.

Reasoning: [`2026-08-06-clip-cover-art-execution-log.md`](2026-08-06-clip-cover-art-execution-log.md).

---

## What happened

The owner reported album art loading inconsistently on the live site, clips fine. It was a
real defect and it is fixed and live: `_from_deezer_artist` read the image from
`row["artist"]["picture_medium"]`, which Deezer's `/artist/{id}/top` does not send — only
`/search` does. Every clip resolved by artist id came back with an empty `cover_url`.

**It shipped with the `MSW-` map switch without being caused by it.** The id path only fires
for artists carrying a `deezer_id`, and `graph-msw-tu50.bin` is the first artifact to carry
them. Authored 2026-08-02, detonated 2026-08-06.

Fixed by reading `album.cover_medium`, present on both responses, costing no extra request.
**`artistpath-api:641ced7` is live and verified.** 404 stale Deezer clip-cache entries were
deleted after the deploy so the fix was visible immediately rather than over 30 days.

## ⚠ The most important thing here is NOT the clip fix

**`DEP-34`: an API-only deploy silently reverts the graph.**
`ARTISTPATH_DEPLOY_GRAPH_KEY` defaults to the pre-`MSW-` artifact, `.env.deploy` does not set
it, and it is per-deploy. **This deploy would have rolled the map back to
`graph-t15-tiebreakfix.bin` and undone the previous day's adoption.**

Caught by `cdk diff` before `cdk deploy`. **Nothing downstream would have caught it** — the
runbook's own `/health` check compares the live service against whichever sidecar it is
handed, so a wholesale revert is self-consistent and passes.

**Before the next deploy of any kind, read `infra/README.md` §4 and §5.** They now set
`GRAPH` once and make `cdk diff` a required step with what a clean API-only diff looks like.

## Claims that must NOT be reverted by a well-meaning editor

- **The `/top` fixture in `api/tests/test_clip_cover_art.py` has no picture key, deliberately.**
  Adding one makes the file pass vacuously and re-blinds the suite. Same for the corrected
  fixture in `test_clip_identity.py`.
- **`test_both_deezer_paths_agree_on_the_image` asserts non-emptiness as well as agreement.**
  That second assertion is not redundant — mutation testing showed agreement alone passes
  when both paths are equally broken, which is the exact production failure.
- **The three frozen documents describing the old `picture_medium` behaviour were left alone**
  (`plans/2026-07-20-path-engine-api.md`,
  `findings/2026-07-23-track2-protocol-analyst-review.md`,
  `2026-08-04-gbl-harness-execution-log.md`). They are accurate as history. Do not "fix" them.
- **The `GBL-` harness's 2026-08-04 fixture decision was CORRECT** and is not a missed catch —
  that harness calls the search path, where `picture_medium` genuinely is present. Execution
  log §5 states this precisely; do not rewrite it into a near-miss story.

## Already updated — do not re-edit

`NEXT.md` (new top block), `docs/README.md` (rows for the log and this handoff, and the
previous handoff's row demoted), `TEST-QUEUE.md` (new queued entry), `infra/README.md`.

## What is owed, and by whom

- **The owner: merge PR #85.** Production is running `641ced7` **ahead of `main`**, which is
  the one genuinely untidy thing left.
- **The owner: `DEP-34-FIX`** — make both deploy variables required in `infra/app.py`, as
  `ARC-6` did for the image tag. Should be taken before the next artifact adoption. Until
  then the runbook is the mitigation and it depends on someone reading a diff.
- **The owner: the queued hand test**, now worth running — the screen is no longer
  half-fixed. `TEST-QUEUE.md` topmost entry.
- **Nothing is owed by a session.** No work is in flight, no background job, no local server.

## What I know that is not in the durable record

Nothing material — §1–§10 of the execution log were written as the work happened rather than
at the end. Three things sit only in the closing message and are deliberately not elevated:
the exact `curl` invocations used to sample Deezer (throwaway; the scripts are in a
session scratchpad, not the repo), the observation that Metric still plays a remix on the
live site (that is `CLIP-1`, already recorded and owned elsewhere), and that the two local
servers from the previous session were already stopped before this one began.
