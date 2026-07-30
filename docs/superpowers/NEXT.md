# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-29, on the graph-rebuild Track A closeout.**

---

## Next

> ## The next experiment is TRACK B — the cap-selection simulation, at production scale.
>
> Entry point is the handoff:
> [`2026-07-29-HANDOFF-graph-rebuild-track-a.md`](2026-07-29-HANDOFF-graph-rebuild-track-a.md).
>
> **Track A is done, and the `ALG-B` re-crawl has since been RUN** (owner's instruction,
> overnight 2026-07-29 → 30). A full `ALG-B` archive and a built `ALG-B` graph now exist;
> **nothing is adopted.** Both questions the trial left open are answered — see `GRT-P4`
> below — and the answers put the cap simulation on the critical path rather than after it:
> **every figure is at `k = 50`, and the stranding is heavily cap-dependent.** It needs its
> own plan and pre-registration, it runs **offline** from the archive now on disk, and it
> must price `MKS-5b`'s hub cost, which nothing has yet measured.
>
> **Adoption remains PARKED and is the owner's**, and it still owes a blind listen
> (`REQ-38`).

**Graph rebuild Track A is EXECUTED (2026-07-29).** Record:
[`2026-07-29-graph-rebuild-track-a-execution-log.md`](2026-07-29-graph-rebuild-track-a-execution-log.md);
plan `plans/2026-07-29-graph-rebuild-track-a.md`; pre-registration
`specs/2026-07-29-algb-trial-build-preregistration.md`, committed before any arm ran;
figures `builder/analysis/2026-07-29-algb-trial-build/`. Branch `graph-rebuild-planning`.

**Three builder changes shipped**, all defaults untouched: the nameless-artist drop rule,
`--algorithm` selection for trial runs, and algorithm-scoped archive keys (`RC-H3`). A full
production rebuild now passes `check_acceptance`.

In brief for orientation only, and **no summary may keep one half without the other**:
`ALG-B` **does** strand obscure artists (`RC-R1`, unchanged — supply, not reciprocation),
**and** the trial build confirms R.E.M.'s degree collapse is real and larger than sampled
(**6** connections against **47** in a coverage-matched control). **But the predicted build
refusal did not happen**, and the reason is the finding that matters: **the guard cannot see
the collapse it was written for** (`GRT-P2`) — popularity *is* score-weighted in-degree, so a
collapsing artist loses the popularity that would have put it in the sample the degree floor
inspects. R.E.M. falls from popularity rank 7 to 62 and the check looks past it. **Not
established at production scale.** `AS-R3` still stands: replacement graph, not a patch, and
nothing measures whether its new edges are any *good* (`REQ-38`).

**The requirements baseline is unchanged since 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (`REQ-`) governs where it and
[`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) disagree (its §10 lists the
disagreements). `DD-F1` — the famous-pair structural gap — is **a defect, not an accepted
limitation**.

## PARKED — owner's explicit decision; his trigger, never a session's

- **The candidate-pool product decision** — whether a shortened-but-obscure bypass
  candidate (Track 3's DD-A2 or a TB arm) ships at all.
- **The one-statistic cross-track recompute** that must precede any DD-vs-TB comparison.
- **Any blind listen on a router-only candidate** — the listen is deferred to the full
  stack (graph + device).
- **The `ALG-B` re-crawl itself** — 4¼ hours, a new archive, a new graph, and it retires the
  existing path-quality figures. His call, and it owes a blind listen before adoption. **Its
  price is now measured rather than suspected, and both blockers that made it unbuildable
  are cleared** (2026-07-29): the drop rule has landed and the algorithm is selectable. What
  it now owes is a judgement, not engineering — plus `GRT-P2`'s open question of whether the
  acceptance guard still covers the artists it names at production scale.

**Still owed by the owner, unchanged:**

1. **The use-the-app test** — [`TEST-QUEUE.md`](TEST-QUEUE.md), the **QUEUED (latest)**
   entry (the redesign, against `https://musicapp.cmiller.io`), including the phone half.
2. **The iPhone script** — carried inside that entry; still the single most valuable unrun
   test on the project.
3. **The `--prune` publish pass** — ripe since 2026-07-29; see the deferral table.

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). |

## Closed — do not re-plan or re-investigate

- **The source `algorithm` parameter is a CLOSED ENUM of six values** (validated live,
  `CS-P0e`). `limit` cannot exceed 100; `threshold` cannot go below 10 and production is
  already there. **Do not propose raising the candidate-list length or lowering the
  threshold — neither is possible.**
- **The `--target`-capped trial crawl is RETIRED as the instrument for `AS-H2`** — its
  readable core is structurally famous (3 artists below the median at target 3,000), so it
  cannot answer a question about obscure artists. **Retired for that question, not for all
  questions:** it remains the only way to reach component membership (`RC-H1`). Do not
  re-propose it for stranding.
- ~~**`STC-6`** — the lower-threshold re-crawl probe.~~ **KILLED 2026-07-29**: its
  condition became *known-unreachable* (no lower threshold exists), which the closeout
  standing rule makes a kill rather than a reschedule. Struck, kept for the record.
- **Track 2, Track 2F and the ceiling toll are exhausted nulls. Do not re-run any of them.**
- **Track 3's and Track 3b's results are closed** — do not re-run their arms or re-litigate
  TB-R2.
- **The routing-side toll family is closed for descent claims**; any explicit
  length-preserving constraint is a **new device needing its own pre-registration**, which
  must consume `TB-P5H-7` at design time.
- **Loosening the both-ways cap is rejected** (`MKS-5b`); any targeted alternative must
  demonstrate its bound by simulation first. ⚠ **Two findings now bear on it and neither
  changes it.** `CS-P0f`: the source `score` is symmetric, so mutual k-NN adds no similarity
  evidence and cuts the famous→obscure direction 87.4% of the time. `RC-A2`: under `ALG-B`
  four of forty top-0.1% artists sit at rank 50–97 in their own candidates' lists, just
  outside the cut. **Neither is a licence to change `k`**; both are inputs to the
  cap-selection simulation.
- **The cap-selection simulation is RE-ORDERED, not cancelled** — still owed under
  `MKS-5b`, the third strand of the rebuild plan. `CS-P0c` showed it cannot fix `DD-F1`, and
  `RC-A2` shows it **interacts with any algorithm change** rather than composing with it.
- **Famous-pair first-path fame is barred as a scoring criterion** (PLA-R1).
- **The nameless-artist question is decided** (drop). Implementation comes due in the
  rebuild plan, and it now **gates that plan's own first build**.
- **The builder-side p99 rescale stays parked** (DD-R2's trigger never fired) — a candidate
  *input* to the rebuild plan, not a commitment.
- **The OneDrive migration is COMPLETE**; the old tree is an archive, never the working tree.
- **`G3-A5`, `G3-A2`, `G3-S7`** closed as recorded; **`G3-A3` does not fire**.
- **`RMD-6`, `RMD-11`, `RMD-12`, `RMD-13`, `FRO-1`, `FRO-4`**, the `DEP-33` blockers, the
  Gate 1 clip work, **Track 1**.
  - ⚠ **One exception, live:** `BYP-13` — a card playing a clip by a *different artist of
    the same name*. Not path work and not inside any pause.

## Must not be changed, and each has a reason

- **`max_size=2` (`stack.py`)** — the **cost ceiling**, the only automatic spend control.
- **App Runner is excluded from CDK tagging** — tagging forces a replacement that cannot
  succeed; pinned by `test_app_runner_is_deliberately_left_untagged`.
- **The ACM validation `CNAME` at Cloudflare** — delete it and the certificate silently
  fails to renew in ~13 months.
- **The rate limit is `10 / 10 s`, not `30 / 60 s`** — see `infra/README.md` §1a.
- **The `acceptance.py` blank-name check** — do not weaken it to unblock a build;
  implement the drop rule. **It now blocks trial builds too, which is the point.**
- **The mirror's two device knobs (`w_known_ramp_pctl`, `w_known_thresh_pctl`) stay 0.0**
  — analysis-only; nothing is adopted; TB-G1 is the evidence production is untouched.
- **`BuilderConfig.algorithm` still carries `contribution_5`** — `ALG-B` is a candidate,
  not an adoption. Changing it *is* the re-crawl decision.

## Deferred, with conditions

| Finding | Condition |
|---|---|
| ✅ **Component membership under `ALG-B`** (`RC-H1`) | **DISCHARGED 2026-07-29** at trial scale — `GRT-C4`. `ALG-B` excludes readable artists from the largest component in three of four comparable bands where `ALG-E` excludes none (whole-population 3.20% vs 1.37%). ⚠ **The pre-registered ratio bar is undefined against a zero baseline and returned "not decisive" everywhere** (`GRT-P1`); the figures stand, the threshold verdict does not. Struck, kept for the record. |
| ✅ **`RC-P2`'s predicted build refusal** | **DISCHARGED 2026-07-29 — REFUTED, and the reason supersedes it.** No refusal: both clauses pass. R.E.M.'s degree collapse is confirmed (47 → 6) but the guard cannot see it (`GRT-P2`). Struck, kept for the record; replaced by the live item below. |
| ✅ **`GRT-P2` — does the acceptance guard cover the artists it names?** | **DISCHARGED 2026-07-30 — CONFIRMED BLIND at production scale** (`GRT-P4`). On a real 68,467-node `ALG-B` graph, R.E.M. holds 6 connections at popularity rank 38, Pixies 3 at rank 5,730, The xx 1 at rank 12,317 — **all outside the top-25 sample the degree floor inspects, and the build passes**. `acceptance.py` cannot detect this failure mode at any scale. **Do not weaken it**; strengthening it is a design question of its own and is not proposed. Struck, kept for the record. |
| ✅ **`GRT-P1` — `GRT-C4`'s effect size** | **DISCHARGED 2026-07-30** — the broken ratio bar was a *trial-scale* artifact of a zero baseline. At production scale the baseline is non-zero (1.07%) and the pre-registered 2× bar works as written: `ALG-B` excludes at **8.12×**, decisively material. A successor pre-registering a zero-baseline-capable read is still the tidier fix but is no longer blocking. Struck, kept for the record. |
| **The cap-selection simulation at production scale** (`MKS-5b`, strand 3) | **Before any `ALG-B` adoption decision — now the decisive next experiment, not a follow-up.** Every `GRT-P4` figure is at `k = 50`, and `GRT-P3` measured `ALG-B`'s stranding as heavily cap-dependent. The overnight archive makes this answerable **offline, at full scale**. Must consume `RC-A2` and price `MKS-5b`'s hub cost, which no probe here has measured. |
| **`snyk_code_scan` never ran on the `GR-1`/`GR-2`/`GR-3` diffs** | **Whenever the Snyk CLI is authenticated** (`snyk auth` is a browser flow only the owner can complete). Required by the global instruction on new first-party code. |
| ✅ **`RC-H3`** — the archive key does not encode the algorithm | **DISCHARGED 2026-07-29** (`GR-3`) — production keeps the flat layout, every other algorithm gets a sub-tree, and the checkpoint refuses a mismatched resume. Struck, kept for the record. |
| ✅ **No way to select the algorithm for a build** | **DISCHARGED 2026-07-29** (`GR-2`) — `--algorithm` on both `crawl` and `build`, validated against the closed enum. The default is unchanged and flipping it is still the re-crawl decision. Struck, kept for the record. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. Measured at 5 escapes per 3,000 artists. |
| **Re-scoring `rc_raw_records.json` at a different `k`** — full candidate lists were stored to make this possible without new requests | **If the cap-selection simulation is designed** (strand 3); consume `RC-A2` at design time. |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| ✅ **Nameless-artist drop rule** | **DISCHARGED 2026-07-29** (`GR-1`/`GR-4`) — implemented in `pipeline.py`, and a full production rebuild passes `check_acceptance`. Removes 36 pre-prune (the emitted graph showed 33 — different populations, both correct) plus 3 stranded neighbours. The owner's MusicBrainz check settled it beyond preference: all three sampled nameless MBIDs return "Artist not found", so backfilling was never available. The tripwire stays as a standing build rule. Struck, kept for the record. |
| **`TB-P5H-7`** — TB-C2's failure by TB-C1-passing arms is consumed by no pre-registered read | **If any successor bypass-device pre-registration is written.** |
| **The candidate-pool recompute** (one statistic across DD and TB arms) | **If the owner picks up the parked candidate decision.** |
| The `--prune` publish pass | **Ripe since 2026-07-29** — `sync_frontend.py --prune --skip-build` once nobody still holds the previous `index.html`. |
| **The rate limit's headroom** — two users behind one IP could collide | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1.** |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
| ✅ **Stranding under `ALG-B`** (`AS-H2`), connection-count half | **DISCHARGED 2026-07-29** — measured by `RC`; `RC-R1` fired on both the pre-registered and the corrected read. Struck, kept for the record. Its component-membership half is live above as `RC-H1`. |
| ✅ **Stratum-aware reads** (`AS-H1`) | **DISCHARGED 2026-07-29** — the successor algorithm pre-registration was written and honoured it: `RC` keeps all five fame bands separate and `RC-G2` refuses to pool an under-populated band. Struck, kept for the record. |
| ✅ `score_t3.py` A11-flag deferral | **DISCHARGED 2026-07-29** — TB-G4, verified by TB-P5. Struck, kept for the record. |
| ✅ **`STC-6`** lower-threshold re-crawl probe | **KILLED 2026-07-29** — no lower threshold exists (`CS-P0e`). Struck, kept for the record. |
