# `CXA-` execution log — adopting the extended 117k graph, 2026-08-10

**Role: RETAINED REASONING for the `CXA-` adoption.** What was decided and why. It owns no
status (`NEXT.md`) and no figures — those live in
`builder/analysis/2026-08-09-jfx-prereg-critique/README.md` (the `JFX-` measurement) and
`builder/analysis/2026-08-10-cxa-acceptance-bounds/README.md` (the fourth acceptance
artifact). Cited, never restated.

Governing: [`plans/2026-08-10-cxa-graph-adoption.md`](plans/2026-08-10-cxa-graph-adoption.md).
Branch `crawl-extension-design`, **PR #91**.

**The adoption is COMPLETE and DEPLOYED.** All nine tasks ran; both owner stops were taken
by the owner.

---

## §1 What the owner decided, and when

- **`CXA-S1` (the acceptance bound values), taken 2026-08-10.** He accepted the proposed
  ±20 % band after being shown the four-artifact sensitivity table.
- **`CXA-S2` (go/no-go on the deploy), taken 2026-08-10.** He instructed the deploy, and
  separately instructed that PR #92's UI fix be included and that the frontend sync run
  with `--prune`.

**The `--prune` decision is his and is recorded as his**, with his reasoning: the site does
not have enough activity for the `FRO-1` window to matter at this stage. The window is real
— `--prune` adds `--delete` to the **asset pass, which runs before the new `index.html`** —
but it is much narrower than the original defect, because `index.html` is now served
`no-cache` and a returning browser revalidates rather than holding a stale copy
heuristically. Verified by reading `sync_frontend.plan_upload`, not assumed.

## §2 The fourth acceptance artifact, and why it was built

The plan's Task 1 table had three filled rows and one marked **NOT RUN**. The session-start
scope check fired on it: it is a ~25-minute build that could change the numbers the owner
was about to approve, so it ran before the values went to him rather than after.

**It mattered more than "the protocol says four".** The three filled rows all vary the same
thing — **crawl size**. None of them tests whether the band can still tell a healthy **cap
rule** from a reverted one. And the `MSW-` comment in `acceptance.py` records that the
*previous* band could **not**: mutual k-NN on the 75k archive sat inside it at 732,832 edges.

The fourth row (81,749 artists / 905,558 edges) is rejected by the new band on **edges**,
by roughly 30 %. **Its node count sits INSIDE the node band.** So the edge floor alone
separates a silent cap-rule revert from a shipped artifact — recorded in a warning beside
the number, because a future session widening that floor to admit a build would remove the
protection without any test going red.

**One knob.** Same archive, same `ULF-` payload, same k=50; `mutual_knn` instead of
`trimmed_union`. That is what makes it an isolating baseline rather than a second confounded
build.

## §3 Defects in the plan itself, found by executing it

**None of these changed an outcome. All three are plan claims that did not survive contact
with the code**, which is why `CLAUDE.md`'s "grep every function, file and config value a
plan names" step exists.

1. **Task 2 named one constant to move; three had to.** `test_shipped_candidate_list_matches_the_frozen_snapshot`
   pins count, population **and** sha against whatever `UNLISTENABLE_DROP_LISTS` resolves to.
   `CANDIDATE_COUNT` (15,708 → 27,262) and `CANDIDATE_POPULATION` (75,000 → 117,302) moved
   with the sha. Executed as written, the suite would have gone red on what the plan called a
   one-line change. Recorded at the pins so the next repoint sees all three.
2. **Task 3's "the manifest will record `passed: true`" is false.** `build_manifest` has no
   acceptance key at all — the `JFX-` diagnostic script added that block itself. `cmd_build`
   proves acceptance passed by *writing the file*; it raises before serialising otherwise.
3. **Task 3 is NOT "the first exercise of the `manifest.py` fix on the real path".** That fix
   coerces a `Path` in `unlistenable_list_path`; the Task 3 build deliberately passes no
   override, so the field is `null` and the branch never runs. The fix still fires only on
   override builds.

**And one in the runbook, which is the `DEP-34` class:** `infra/README.md` §4 named
`graph-msw-tu50.bin` inline as "today's adopted artifact". `ApiConfig.graph_path` moved at
Task 4, so that line went stale in the same commit — and it is a value someone pastes.
Fixed, with a temporary block flagging the trunk/production disagreement, deleted once
`CXA-S2` was taken.

**Task 7's "set `ARTISTPATH_GRAPH_SHA256` from the sidecar" is also not an operator step** —
`infra/app.py` derives it via `_sidecar_sha256()` from `ARTISTPATH_DEPLOY_SIDECAR`. That is
`DEP-24`'s rule enforced in code rather than asked of a human. Harmless; the correct action
is to set the sidecar path, which was done.

## §4 The gates

- **`CXA-G1` — PASS, byte-identically.** The rebuild through the normal CLI, with **no**
  `--unlistenable-list` override, produced `bc0431c4…8e7ece46` — identical to the artifact
  every `JFX-` figure was measured on. Its manifest records `unlistenable_list_path: null`,
  which is the proof that matters: the shipped **default** now reproduces the measured build,
  rather than a per-invocation flag doing it.
- **`CXA-G2` — PASS, verified from inside the built image**, not from the branch, as the plan
  required. The container reports `graph_path` ending `graph-cxa-adopted.bin` **and**
  `w_known_ramp_fame_pctl = 0.01`, so the must-not-revert claim survived into the artifact
  that actually runs.

## §5 The merge, and why the image was rebuilt

The owner asked for PR #92's landing-dot fix to be included. It was on `main` only and this
branch predates it; it is **frontend** (`ArtistSearch.tsx`, a `z-10` → `z-20` change), so the
API image cannot carry it and it ships through the frontend sync.

`origin/main` was merged in (clean, no conflicts) and **the image was rebuilt and repushed at
the merged commit `994c203`.** The earlier image `29585c6` was correct for the API and would
have deployed fine — but the tag is the only record of what is running, and deploying a tag
that predates the frontend fix would have made that record misleading. `CXA-G2` was
re-verified on the rebuilt image.

**The merge also reconciled `TEST-QUEUE.md`**, whose topmost heading on this branch still
read `QUEUED` because PR #92's discharge had landed on `main` only. It is now `DONE`. **It
was not discharged a second time.**

## §6 Deploy verification

`cdk diff` was read before `cdk deploy`, per `DEP-34`. It showed **exactly four** changes and
nothing else: the IAM object-read permission, `ARTISTPATH_GRAPH`, `ARTISTPATH_GRAPH_SHA256`
(`43dd82bb…` → `bc0431c4…`), and the image tag. **No credential appeared in the output**, so
§5's warning about the viewer function's source did not apply to this diff.

`--require-approval never` was passed **deliberately and is worth flagging**: CDK defaults to
prompting on IAM broadening, stdin is null here, and the prompt would have hung. The IAM
delta was displayed to the owner in full before the deploy and he had authorised it. A future
session should not treat that flag as routine.

**Verified live, not inferred:** `/health` returns the new sha, 88,685 artists and 1,618,164
edges — a genuine check rather than a self-consistent one, because that sha is `CXA-G1`'s gate
value verified independently, not whatever sidecar the check was handed. A journey built
through the public address returns Radiohead → Nine Inch Nails → Aphex Twin, and a middle
card resolves both a clip and cover art. The served `index.html` names the bundle that was
uploaded and `Content-Type`-checked.

## §7 What must not be reverted by a well-meaning editor

Everything on the `JFX-` handoff's list still stands in full. Restated here only where this
track touched it:

- **The shallower gradient is NOT established.** `D_B − D_A` spans zero. Adoption was taken
  with **no cost demonstrated**, not in spite of a measured one — and this equally does not
  establish the gradients are equal.
- **The d20 famous-to-famous drift is POST-HOC.** It is where to look, never a finding, and
  needs its own pre-registration to become a claim. It is why the test-queue entry points him
  at famous-to-famous pairs.
- **`w_known_ramp_fame_pctl` stays 0.01.** Confirmed in the running image. Moving it in the
  same release would have confounded the use-test.
- **`JFX-B`'s manifest still says `DO_NOT_DEPLOY: true` and that is correct** — it was built
  against the old bounds. The shipped artifact is a *different file* from a *new* build.
- **The ALG-E drop payload did not ship.** Only `UNLISTENABLE_DROP_LISTS[CANDIDATE_ALGORITHM]`
  moved; the `PRODUCTION_ALGORITHM` entry is untouched, verified from the diff.
- **The 75k-era ALG-B payload file stays in `data/`** — three era-pinned probes load it by
  name rather than through the registry. Superseded as a default, **not orphaned**.

## §8 Open, with conditions

- **`SEL-R1`–`R4`** — constants named for a role that moved. Task 2 was the second time this
  was a live trap. **Condition: closed when `CANDIDATE_ALGORITHM` no longer means the
  production lineage.** Still the owner's, still its own maintenance session.
- **The rank-asymmetry idea** — **condition: needs its own pre-registration, and resuming
  path-quality work is the owner's trigger.** Belongs to "improvements", not to this adoption.
- **`builder/analysis/2026-07-23-acceptance-bounds/check.py:33`** — `ROOT` still points at the
  retired OneDrive tree, so that era-pinned probe **cannot execute at all**. Found during Task
  1 and deliberately not fixed: its pinned bound values must not follow this change, and
  whether a probe that cannot run should be repaired or retired is a judgement, not a typo.
  **Condition: closed when it is either repaired or explicitly retired.**
- **`CLIP-1` exposure is expected to RISE** — the newly-crawled population's un-listenable
  class rate is 31.36 % against 24.74 % for the pre-crawl 75,000. The test-queue entry asks
  for new examples by name. **Condition: closed when the owner rules on whether it is worth
  fixing.**
- **`CEX-F1`, `CEXR-6`'s `load_deezer_ids` half, `CEX-R3` (search), `FE-SNYK-1`,
  `SNS-1`** — unchanged and untouched by this track.

## §9 The standing context layer (closeout D6)

**Zero delta in both layers.** `CLAUDE.md` was not touched, `memory/MEMORY.md` was not
touched, and no skill or agent `description:` changed — checked against the working tree, not
inferred from "nothing was intended". Everything this track added went into documents that
load on demand: the execution log, the handoff, `NEXT.md`, `docs/README.md` rows, and an
analysis README.

**Nothing here asks the owner to buy an addition to the layer that taxes every future
session.**

## §10 Security

`snyk_code_scan` was run over the one new first-party source file
(`builder/analysis/2026-08-10-cxa-acceptance-bounds/mknn_build.py`) and returned **0 issues**.
No other first-party code was added; the remaining changes are two constant repoints, a
config default, three test pins and documentation. **`FE-SNYK-1` is untouched — nothing here
went near a frontend dependency**, and every lockfile is unchanged.
