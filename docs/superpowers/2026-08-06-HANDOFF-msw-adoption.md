# Handoff — the `MSW-` map switch ADOPTED and DEPLOYED, 2026-08-06

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-06-HANDOFF-msw-seam3.md`](2026-08-06-HANDOFF-msw-seam3.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff, not mid-flight.** The plan is complete — all twelve tasks — and the work is
at its designed stopping point.

**Branch** `msw-adoption-flip`, **PR #83 — MERGED 2026-08-06** at `3458594`, off `main` at
`6139f28`. Adoption commit `a06ab58`. **The branch is spent; new work branches from `main`.**
Tree clean.

---

## What happened

**The owner gave the go at Seam 3** after pressing the candidate configuration locally, and
asked for the rest of the plan including production. Tasks 11 and 12 both ran.

**The map switch is LIVE at `https://musicapp.cmiller.io`.** Four defaults flipped, a new
container image built and pushed, the artifact uploaded, the stack deployed, and the result
verified mechanically.

| Knob | Was | Now |
|---|---|---|
| `ApiConfig.graph_path` | `graph-t15-tiebreakfix.bin` | `graph-msw-tu50.bin` |
| `ApiConfig.w_known_ramp_fame_pctl` | `0.0` | `0.01` |
| `BuilderConfig.cap_strategy` | `mutual_knn` | `trimmed_union` |
| `BuilderConfig.require_fame` | `False` | `True` |

Reasoning and figures: the execution log's **Task 11** and **Task 12** sections. Cited here,
never restated.

## Which documents are now wrong, and in which direction

**None are known-wrong.** `NEXT.md` was rewritten this session; `docs/README.md`'s rows updated;
`CLAUDE.md`'s Graph shape section and `.claude/agents/ml-graph-analyst.md` both corrected **in
the adoption commit**, which is where the plan required them.

**⚠ The direction of staleness has INVERTED, and this is the thing to carry.** For three months
the standing risk was a document claiming something was adopted when it was not. It is now the
opposite: **anything saying "nothing is adopted", "every default is still off", or "the app's
committed defaults are unchanged" is stale if it describes the present.** The same sentence in a
frozen `GBL-`/`CAU-`/`ULC-` findings row is *correct* — it describes what that track did — so
this cannot be fixed by grep. Read for tense before editing.

## Claims that must NOT be reverted by a well-meaning editor

**Everything in the four previous handoffs' lists still stands in full.** Additionally:

1. **This adoption is an OWNER OVERRIDE of the `GBL-` null, not evidence-backed adoption.**
   Margin 3 against a bar of 5; the pre-registered consequence was "production stands". Neither
   `GBL-` nor `CAU-` licensed the override — his authority did. The sentence is fixed in the
   execution log, the PR body and the `w_known_ramp_fame_pctl` comment. **Never soften it into
   "the evidence supported adoption".**
2. **`require_fame=True` means an archive with no `fame` stage now REFUSES to build.** That is
   the designed behaviour, not a regression. Anything replaying a pre-adoption archive must pin
   `require_fame=False` at its own construction site.
3. **The test suites were not weakened to make the flip pass.** 97 tests moved. Default-pinning
   assertions were *flipped to the adopted values* rather than deleted; unrelated knobs were
   pinned off per the existing factor-table-control idiom; `test_cli.py`'s archive gained a real
   `fame/` stage because the CLI deliberately has no flag to turn the requirement off. **Do not
   "simplify" any of those pins away** — each one is what keeps its test testing its subject.
4. **Two of those pins fix silent confounds and are not cosmetic.**
   `test_trimmed_union_supplies_more_edges_than_mutual_knn`'s mutual arm and
   `test_acceptance.py::_build` would both have kept passing while no longer testing anything:
   the first would have compared trimmed_union against itself, the second monkeypatches
   `mutual_knn_cap`, which the trimmed_union path never calls.
5. **`CLIP-1` is NOT a duplicate of `BYP-13` and not a regression.** `BYP-13` is a *different
   artist of the same name*. `CLIP-1` is the *right* artist with a clip that misrepresents them
   — a guest credit or someone else's remix. The un-listenable filter does not touch it either,
   since those artists have real catalogues. Nothing about `MSW-` caused it.
6. **The previous artifact's S3 keys were deliberately left in place.** They are the rollback
   path (`infra/README.md` §9 — redeploy with the old `ARTISTPATH_DEPLOY_GRAPH_KEY`). Do not
   tidy them away.

## What has already been updated — do not re-edit

The execution log (Task 11, Task 12, `CLIP-1`), the plan (all Task 11/12 steps ticked, plus a
correction block above Task 12 Step 1), `NEXT.md`, `TEST-QUEUE.md` (previous entry marked DONE,
one new QUEUED entry), `docs/README.md`'s rows, the previous handoff's role line, this note,
`CLAUDE.md`, and `.claude/agents/ml-graph-analyst.md`.

## What I know that is not in the durable record

**Empty.** Two things that might have lived here are folded in instead: the Cloudflare
User-Agent trap is in the execution log's Task 12 section, and `CLIP-1`'s full statement with
its condition is in its own log section rather than only in conversation.

**Hard stops from previous handoffs are DISCHARGED.** "Do not start Task 11 or flip any default
— Seam 3 is mine" was released by the owner's go. No pre-authorisation was carried forward or
assumed; the deploy was authorised explicitly after being blocked once.

## Anything in flight

**Nothing.** No servers, no background jobs, no half-written directories, no uncommitted files.

The two detached servers from the morning's hand test (ports 5173 and 8000) were **stopped
2026-08-06 on the owner's instruction**, and both ports verified free. He is testing against the
live site from here on — **deliberately, because production writes telemetry to CloudWatch and a
local server writes it to a terminal nobody reads.** That is a reason to prefer the live app for
future hand tests generally, not just this one.

## Owed, and by whom

- **Owner:** the queued hand test on the **live site** (`TEST-QUEUE.md`, topmost entry) — the
  first real use of the new map by a person. Also whether to stop the two local servers, and
  whether the standing layer's growth is acceptable (+333 characters unconditional,
  +6 lines conditional).
- **Next session:** nothing is blocked. `CLIP-1` is the obvious next candidate and is his call.
- **`ULF-3` — re-tested this closeout, and its FIRST HALF HAS NOW COME DUE.** Its condition is
  two-part: *a shipped build has routed on a `ULF-` list* **and** *the era-pinned probes naming
  the old flags are themselves retired or re-pinned*. **First half: SATISFIED** — the deployed
  artifact was built with `drop_unlistenable=True` and is live. **Second half: NOT satisfied** —
  `grt_score.py`, `calibrate.py` and `cre_build.py` still name `drop_no_release_tail` and
  `drop_featured_credit`. **So the deferral stays open, but it is now half-due and must be
  re-tested rather than copied forward again.**
- **Unchanged and not `MSW-`:** `ULC-F3` (crawl resume cannot extend) still blocks any crawl
  extension; `ULC-F4` (keep-check name resolution) is its own track.
- **New deferral, with its condition — the committed test fixtures predate the adopted graph.**
  `api/tests/fixtures/*.bin` and the builder's copy were derived from a pre-`MSW-` artifact and
  carry no `fame_lb`; four api test modules now pin the ramp off because of it. **Condition:
  regenerate when a test needs to exercise fame over real data, or before the next artifact
  adoption, whichever comes first.** Not done here deliberately — regenerating changes what
  every fixture-dependent assertion asserts, which is a separate piece of work from an adoption.
