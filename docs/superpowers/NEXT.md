# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-29, on the algorithm-selection closeout.**

---

## Next

> ## The next session WRITES THE GRAPH REBUILD PLAN, cold from the committed record.
>
> Entry point is the handoff:
> [`2026-07-29-HANDOFF-algorithm-selection.md`](2026-07-29-HANDOFF-algorithm-selection.md).
> **The task order changed on 2026-07-29 — read it before assuming the old one.** The
> cap-selection simulation is no longer first; it is third.
>
> **The agreed next experiment is `AS-H2`'s trial crawl** — a `--target`-capped crawl on
> `ALG-B`, built, to measure stranding before anyone commits 4¼ hours. Recommended and
> **not run.** It is methodology, not a decision awaiting the owner.

**Algorithm selection is EXECUTED and read (2026-07-29).** Record:
[`2026-07-29-algorithm-selection-execution-log.md`](2026-07-29-algorithm-selection-execution-log.md);
pre-registration `specs/2026-07-29-algorithm-selection-preregistration.md`, committed before
any arm ran; figures `builder/analysis/2026-07-29-cap-selection-sim/`. Branch
`graph-rebuild-plan`, PR #48.

In brief for orientation only, and **no summary may soften either half**: `ALG-B`
(`days_7500 · contribution_3`, one parameter from production) is the **named re-crawl
candidate** — it lifts obscure-candidate yield at the very top where production offers
almost nothing. **But `AS-H2`: it returns 58% fewer candidates for obscure artists, so it
plausibly strands MORE of them**, and `AS-R3` fires — it is a **replacement graph, not a
patch**, so every path-quality figure this project holds was measured on the current
setting. Nothing measures whether its new edges are any *good* (`REQ-38`).

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
  existing path-quality figures. His call, and it owes a blind listen before adoption.

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
  demonstrate its bound by simulation first. ⚠ **`CS-P0f` explains what that rule is
  actually doing** — the source `score` is symmetric, so mutual k-NN adds no similarity
  evidence and cuts the famous→obscure direction 87.4% of the time. **That is not a licence
  to change it**; `MKS-5b` is untouched.
- **The cap-selection simulation is RE-ORDERED, not cancelled** — still owed under
  `MKS-5b`, now the third strand of the rebuild plan. `CS-P0c` showed it cannot fix `DD-F1`.
- **Famous-pair first-path fame is barred as a scoring criterion** (PLA-R1).
- **The nameless-artist question is decided** (drop). Implementation comes due in the
  rebuild plan.
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
  implement the drop rule.
- **The mirror's two device knobs (`w_known_ramp_pctl`, `w_known_thresh_pctl`) stay 0.0**
  — analysis-only; nothing is adopted; TB-G1 is the evidence production is untouched.
- **`BuilderConfig.algorithm` still carries `contribution_5`** — `ALG-B` is a candidate,
  not an adoption. Changing it *is* the re-crawl decision.

## Deferred, with conditions

| Finding | Condition |
|---|---|
| **Stranding under `ALG-B`** (`AS-H2`) | **Before any adoption decision** — the trial crawl above. The candidate-supply drop is measured; its graph-level effect is not. |
| **Stratum-aware reads** (`AS-H1`) | **If any successor algorithm pre-registration is written** — two of five reads did not fire because they assumed the popularity bands would agree. |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| **Nameless-artist drop rule** (decision made: drop) | **Before the next production rebuild — DUE: the rebuild plan must schedule it.** |
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
| ✅ `score_t3.py` A11-flag deferral | **DISCHARGED 2026-07-29** — TB-G4, verified by TB-P5. Struck, kept for the record. |
| ✅ **`STC-6`** lower-threshold re-crawl probe | **KILLED 2026-07-29** — no lower threshold exists (`CS-P0e`). Struck, kept for the record. |
