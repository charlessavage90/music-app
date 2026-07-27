# Gate 2 Track C — the app reaches the internet

**Role: RETAINED RECORD for Track C.** Reasoning and corrections; not a narration of tasks
(git has those) and not an implementation description (the code has that). Owns no
path-quality figures — those live in `findings/2026-07-21-scoring-adjudication.md`.

**Date: 2026-07-27.** Branch `gate2-track-c`, PR #33. One session, no handoff inside it.

---

## §1. What Track C actually was, versus what it was recorded as

`NEXT.md` described Track C as "sync the SPA to the bucket". That is one of its four parts
and the smallest. Closing `RMD-6` required a **new image**, because the fix lives in
`api/…/config.py` (commit `78524d0`) rather than in the stack — so Track C was a full
deploy: image build and push, stack update, SPA publish, then §8/§8a verification.

This was established by reading `config.py` before planning anything, and it changed the
shape of the work. A session that took the one-line description at face value would have
published the SPA against an API still serving the old CORS default and recorded `RMD-6`
as closed.

## §2. The §6 script — the owner's decision, and what it cost

The retiring stage 3 session put one open decision to the owner: whether to turn
`infra/README.md` §6 into a script before running Track C. He agreed, and it was the first
task.

**Shape.** `infra/src/artistpath_infra/sync_frontend.py`, following `deploy_stage.py`'s
precedent exactly: planning is a pure function, running is a thin shell around it, so every
invariant is testable with no AWS, no credentials and no build. 17 tests.

**Mutation-verified, ten mutations, all caught.** A green test is not evidence until it has
been shown to go red. Each mutation is the real defect or a neighbour: collapse the passes
into one `--delete` sync; publish `index.html` first; drop the `--exclude`; cache
`index.html` for a year; invalidate before publishing; accept a build with no `index.html`;
accept any content type; ignore the AWS fallback; prefer the fallback over the real PATH;
probe `index.html` instead of a script.

**Two things the runbook could only ask an operator to remember are now checked.**

1. **`Content-Type`.** §6 recorded it as a machine-state caveat: `aws s3 sync` guesses from
   the extension, it was correct on the deploy machine on 2026-07-27, re-check if the deploy
   moves machines. A caveat discharged by remembering to discharge it is worth little, and
   its failure is the *same blank page* as `FRO-1` from an unrelated cause. The script reads
   back an uploaded `.js` and refuses. **It probes between the two passes** — assets up,
   nothing naming them yet — which is the last moment the check is free. Measured live
   during the cutover: `text/javascript`.
2. **The AWS CLI off a stale PATH.** Recorded in project memory as a recurring trap and met
   again here: `aws` is on the *machine* PATH, so it works in a new window while a shell
   opened earlier cannot see it at all. Unhandled it is a `FileNotFoundError` partway
   through a publish, after some objects are up.

**`--prune` is off by default**, because deleting old assets while the old `index.html` is
live re-opens `FRO-1` for anyone mid-visit.

## §3. Three corrections to the record, all found by running the procedure

**§3.1 — the drift gate would have fired on every future deploy.** `infra/README.md` §7 said
"expect exactly two normalisation rows on `ApiService`; anything third is real and blocks the
deploy." That was true only until `RMD-6` was fixed. The fix deliberately left the empty
`ARTISTPATH_CORS_ORIGINS` in the template — `stack.py` keeps it as a statement of intent and
the guarantee moved to `ApiConfig.cors_origins` — so App Runner goes on dropping it and the
`REMOVE` row is **permanent by design**.

Measured on both sides of the deploy: before, three rows; after, the same three, with the
exposure gone from the running service. The row's index also moved (`/4` → `/5`) when the
autoscaling configuration landed, so §7 now says match on the variable name, never the path.

**A gate that always fires is one you learn to skip** — the same failure the section's own
note about stale expected test counts is about.

**§3.2 — `NEXT.md` claimed Track C closes the stack drift. It does not.** It closes the
exposure only. Recorded here because the claim is now overturned and a well-meaning editor
should not restore it.

**§3.3 — two deploy traps, neither previously written down.**

- `cdk diff` and `cdk deploy` print the site credential, base64-encoded, as part of the
  viewer function's source. Not a leak in the function — the gate has to hold the credential
  to compare against it — but the deploy output is not safe to paste anywhere.
- `infra/.env.deploy`'s lines are `export NAME=value`. Bash sources it natively; PowerShell
  cannot. A regex anchored on the variable name matches nothing, sets nothing, and surfaces
  as `app.py` naming whichever secret it happens to check first — which reads as "that one
  secret is missing" rather than "none of them loaded". Cost one failed deploy attempt.

## §4. Gate outcomes

All four §7 suites green, run in full: api **195**, builder **115**, infra **58** (41 before
this work), frontend unit **80**, build clean, e2e **5**.

**Container scan:** 87 dependencies, 0 critical, **exactly the two accepted base-image
highs** (`attr/libattr1`, `acl/libacl1`, `TKB-6`) — confirmed by name at the high threshold
rather than inferred from a count. Snyk again recommended the Alpine base the runbook warns
against; not taken.

**§8 verification:** site refuses without the password (401), App Runner refuses a request
that did not come through CloudFront (403), and the live graph matches the sidecar
mechanically on all three of sha256, artist count and edge count.

**§8a ran for the first time in the project's history.** Every prior check proved only that
the site *refuses*. All three pass: the gate admits (200), an authenticated API call through
CloudFront succeeds (200), and `TR-5`'s SPA fallback returns the app shell for a shared
journey link. That closes `RMD-13`/`FRO-4`'s mechanical half. Its browser half remains, and
is now runnable for the first time — see `TEST-QUEUE.md`.

**Log retention** was checked rather than assumed: 90 days on both groups. §5a did not need
re-running because the service was *updated*, not recreated, so the log group names — which
carry the service id — did not change.

## §5. Closed, with the measurement rather than the assertion

- **`RMD-6`.** Before the deploy the live API returned
  `Access-Control-Allow-Origin: http://localhost:5173`. After, no CORS header at all. This
  is the exposure the owner accepted on 2026-07-27 rather than deploy twice; that acceptance
  has now expired by being fixed.
- **`RMD-11`.** The production refusal page reads `username is <strong>artistpath</strong>`,
  and carries no credential in plaintext or base64.
- **`FRO-1`.** Verified on the live distribution: `index.html` is `Cache-Control: no-cache`,
  hashed assets are `public,max-age=31536000,immutable` and `text/javascript`.

## §6. Deferred, each with a success condition

| Finding | Condition |
|---|---|
| Medium CSRF in `react-router@7.18.1` (`SNYK-JS-REACTROUTER-18313151`) | **Revisit only if the app adopts React Router's unstable RSC APIs.** The advisory is exploitable only with those enabled; this is a Vite SPA on `BrowserRouter` with no loaders, actions, fetchers or `Form`, so it does not reach us. The fix is a major bump to 8.3.0 and was declined on cutover day for a non-applicable advisory. |
| Double-encoded text in artist disambiguations — The Beatles reads `UK rock band, â€œThe Fab Fourâ€` | **Next graph rebuild, which is the owner's call.** It is in the adopted artifact, and it is user-visible: `ArtistSearch.tsx:105` renders disambiguation in the search dropdown. Not introduced by Track C; found by reading a live response. |
| Two Low Snyk findings in `infra/` — a hardcoded test fixture value, and `app.py` reading a path from an environment variable | **Accepted, won't fix.** The second is that tool's entire purpose. Neither is in new code. |
| The `--prune` pass | **The next deploy after this one**, once the current `index.html` has been live long enough that nobody holds the previous one. Skipped at cutover because the bucket was empty — nothing to prune and no returning visitor to protect. |

## §7. Not a defect: the default-flip check (A4)

The script added two CLI flags, not config defaults. `--prune` defaults off and that **is**
the shipped behaviour the work intended, per `FRO-1`; `--skip-build` defaults off so the
published bundle is always freshly built. No knob is sitting at a loser's value.

## §8. Standing context layer (D6)

**Unconditional: 42,778 characters — unchanged. Conditional: 1,971 → 1,983 lines, +12,
every line of it granted explicitly by the owner.** Two additions, recorded separately
below because they were decided separately.

**⚠ The second was priced at +9 and cost +10.** A blank line was missed in the estimate.
Reported because a budget rule whose quoted price is not the paid price is decoration —
the error is small, and the tolerance for it being unremarked is zero.

`closeout`'s A5 carried a premise the cutover falsified. It said "**if C1 queued an item** and
no fresh listener survives, relaunch detached", and the scaling section said "the queued test
needs a server". Both were true while the app ran only on the owner's desktop — every queued
test needed a local server. The newest queued entry exercises the deployed site and needs
nothing running here, so a session following A5 literally would leave a pointless server
behind, which A5's own rule calls a stale artifact waiting to be tested against.

Corrected to "an item **that needs a local server**" — four lines out, four in, no new rule.
That half was the session's to make.

**The +2 is narrative, and it was bought rather than slipped in.** The draft carried two
extra lines saying *why* the rule is now conditional: that an item exercising the deployed
site needs nothing running locally, and that a server started for it is stale by morning.
D6's test for a correction is net ≈ 0 **and no new narrative**, so those two lines were cut,
their cost priced, and the decision put to the owner — who granted them.

**Worth recording that the trim-then-ask was the right order, not bureaucracy.** The bare
qualifier states the rule without saying what makes it conditional, and A5's whole failure
here was a session applying a rule whose premise it had no reason to question. The narrative
is the part that would have prevented it. But which of those two considerations wins is a
budget decision on a layer every `closeout` pays for, and that is not a session's to settle
by writing the lines and reporting the total afterwards.

**Found by `doc-auditor` (B1), on its second pass.** The first pass skipped `.claude/`
entirely on the grounds that this session's own grep of it had come back clean — the exact
inversion of why the sweep was reported. Sent back with that reasoning named, it found this
and the root `README.md` defect in one run.

### §8.1 — the auditor's own scope rule, +10 lines and a model change

**The instrument had a defect, and it was in the definition rather than the run.** Nothing in
`doc-auditor.md` said *what may narrow scope*. Every narrowing criterion it gave was about
**size** ("large completed or historical documents", "exceeds roughly 4,000 lines"), while
`## Scope`'s first line hands scope authority to the caller. Given caller authority, plus
permission to narrow, plus no rule about valid reasons, reading "I already grepped this and it
was clean" as scope guidance follows from the text. The agent was not being lazy; the file
allowed it.

**And the compensation for its own stated blind spot did not reach the expensive layer.** The
definition names absence as its weakness and prescribes working check F mechanically — but
check F is a list of `ls`-able things (README exists, per-package READMEs, a doc index) and
never reaches agent or skill definitions, which is where an absence defect is auto-loaded into
every future session.

Two edits, in **both** the project-local fork and the global copy, per the fork's own
instruction that a shared check is improved in both:

1. `Agent and tooling definitions` in the default scope becomes **never droppable** — in
   place, no new lines.
2. A rule that **size is the only thing that may narrow scope**, that a caller's report of a
   clean sweep moves an area *up* the list rather than off it, and that silently dropping
   default scope is itself a reportable finding.

**`model: haiku` → `model: sonnet`, both copies, the owner's decision.** The observed failure
— deferring to the caller's framing over the caller's explicit instruction — is characteristic
of a smaller model, and this agent is the instrument of last resort for a defect class careful
sessions provably miss. It has now caught High-severity defects on three separate occasions,
twice against sessions that had concluded it was unnecessary. **This changes per-run cost**,
which is why it was his call and not the session's.

## §9. Provenance (D3)

No artifact was built, adopted or compared. The graph is unchanged:
`graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…` per
`findings/2026-07-23-tiebreak-fix-adoption.md`, verified three ways before the deploy (file
against its sidecar, sidecar against that findings document) and once after (live `/health`
against the sidecar). 74,193 artists, 898,006 edges.

**Image `37d559e`** replaced `9f5343d` in App Runner. Digest
`sha256:a0f4eb373b1224131928375e0633764d5cabcd44014ee0848d10735c7565a92b`, identical between
the local build and the ECR push.
