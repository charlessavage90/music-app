# Handoff — the extended graph is REVERTED and diagnosed, 2026-09-01

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-10-HANDOFF-cxa-adoption.md`](2026-08-10-HANDOFF-cxa-adoption.md) on **everything** —
next actions *and* status, because that handoff's central claim (the extended map is live) is
now false. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**A SEAM handoff.** The work concluded: the revert is deployed and verified, the mechanism is
measured, the record is written. **The degradation tell did not fire.**

Reasoning: [`2026-09-01-cxr-revert-execution-log.md`](2026-09-01-cxr-revert-execution-log.md).
Figures: `builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md`. Branch
`crawl-extension-design`, PR #91 — **the same PR as the adoption**, deliberately.

---

## What happened, in four lines

The owner used the app for three weeks and reported the extended 117k map *"noticeably worse
than the old version — much harder to find unknown artists"*, which is the revert criterion he
set before adoption. He instructed the revert; it is **live and verified from outside**
(58,838 artists, sha `43dd82bb…`, image tag unchanged). The mechanism was then measured
against both artifact files, with predictions committed first.

## Which documents are now wrong, and in which direction

- **`2026-08-10-HANDOFF-cxa-adoption.md`** — everything it says about what production serves
  is false in the "extended map is live" direction. Its role line now names this note as
  successor. Its record of *what was done and why* is intact and correct.
- **`2026-08-10-cxa-adoption-execution-log.md`** and **`plans/2026-08-10-cxa-graph-adoption.md`**
  — same direction, same limit. Both `docs/README.md` rows carry the warning; the documents
  themselves are frozen records and were not rewritten.
- **Nothing in `.claude/` or `CLAUDE.md` went stale** — swept (B5). The `CXA-` closeout had
  already removed crawl sizes from `CLAUDE.md` and pointed artifact identity at the manifest
  sidecar, which is why this revert cost that layer nothing.

## Claims that must NOT be reverted by a well-meaning editor

- **`graph-cxa-adopted.bin` is the REJECTED artifact, not "the newer one".** It is still in the
  S3 bucket and still on disk. `ApiConfig.graph_path`, its test pin and `infra/README.md` §4
  all name `graph-msw-tu50.bin` deliberately, each with a comment saying this slot has moved
  **backwards** once. An editor "updating to the newest artifact" would re-ship the regression.
- **The `CEX-` crawl extension is not reverted and is not wasted.** The 117,302-response
  archive, the re-censused `ALG-B` payload, the fourth acceptance artifact and the acceptance
  bounds all stand. What was rejected is *building the served map from that archive as it
  stands*.
- **`w_known_ramp_fame_pctl` stays 0.01.** Untouched in both directions, so the confirmation
  test is not confounded.
- **The `JFX-` run was not wrong and the adoption was not a mistake in process.** `JFX-G1b` is
  a *"the map is broken"* stop-gate that permitted materially more digging than the old map
  needed for the same obscurity, and the extended map used materially more (both figures owned
  by the `JFX-` results README, `JFX-G1`). **Passing it never meant "no worse."** Do not rewrite
  the `JFX-` record as a failure — rewrite nothing; the reading is what changed.
- **One half of the owner's report is UNEXPLAINED** — the *first* journey, before any press.
  `CXR-P3` did not fire and `JFX-C1` measured no depth-0 change across 297 pairs. **Do not let
  this quietly close** by treating the two confirmed mechanisms as the whole answer.

## What has already been updated — do not re-edit

`NEXT.md` (new top block, header, previous block marked superseded), `TEST-QUEUE.md` (the
2026-08-10 entry discharged with his verdict; a confirmation entry queued), `docs/README.md`
(two new rows, two amended), `config.py` + its test pin + `infra/README.md` §4, the retained
execution log, and the figures directory. PR #91's title and body carry the revert.

## What I know that is not in the durable record

**Two things, and both are now written down here, which is the point of the question.**

1. **The exact revert command sequence is not in one place.** The runbook's §4 and §5 assume a
   *forward* deploy. A graph-only revert is: set `GRAPH` to the target basename, set
   `ARTISTPATH_DEPLOY_GRAPH_KEY` and `_SIDECAR` from it, **skip both `s3 cp` lines** (the
   artifact is already in the bucket), keep `ARTISTPATH_DEPLOY_IMAGE_TAG` at whatever App
   Runner currently reports so the image does not move, then `cdk diff` and `cdk deploy
   --require-approval never`. Read the tag off the live service rather than off git — they can
   differ, and here they did: the running tag was a merge commit on an unmerged branch.
2. **`--require-approval never` is not optional on any graph swap, ever.** The IAM read
   statement is scoped to the object key, so *every* artifact change moves IAM and *every*
   artifact change will prompt. With stdin null the deploy hangs. This was recorded once
   before as a one-off judgement; it is structural.

## The open decision, and what I would do if I were continuing

**The next action is the owner's and it is USE** — the queued confirmation entry. Beyond that,
the open question is *what, if anything, to do about the crawl extension*, and it is his
trigger because it is path-quality work.

**What I would do if I were continuing**, offered as a position to argue with rather than a
menu: **a minimum-connections bar on what a crawl is allowed to contribute to the served map**
is the cheapest of the three candidates and the only one whose effect is predictable from the
figures already measured — it removes the ~6,100 single-connection artists that provably
cannot be interior cards, without touching the fame ruler or the cost function. It would need
its own pre-registration, and the honest weakness is that it treats the symptom the diagnosis
measured rather than the crawl depth that caused it.

**The one I would NOT start first** is re-framing the fame ruler on a fixed population. It is
the more fundamental finding, but it changes a shipped ruler under a live cost function, and
the `CXR-` figures say nothing about what it does to routing.

## Nothing is in flight

No subagent running, no background job, no half-written directory. Ports 8000, 5173 and 5174
are free and no server was started. The tree is clean.
