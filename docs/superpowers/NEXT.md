# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-29, on the requirements + Track 3b closeout.**

---

## Next

> ## The next session PLANS THE GRAPH REBUILD — owner's instruction, 2026-07-29.
>
> Routing-side devices are exhausted for his goal (below), so the goal now runs through
> how the map is built. Entry points and constraints are in the handoff:
> [`2026-07-29-HANDOFF-requirements-track3b.md`](2026-07-29-HANDOFF-requirements-track3b.md).
> The agreed first task is the **cap-selection simulation from the archive** — it is also
> `MKS-5b`'s required demonstration. **The nameless-artist drop rule comes due inside this
> plan** (its condition: before the next production rebuild); `acceptance.py` stays
> unweakened.

**The requirements baseline changed 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (identifiers `REQ-`) is the owner's
Must/Should/Expect restatement and **governs where it and `WHAT-GOOD-LOOKS-LIKE.md`
disagree** (its §10 lists the disagreements). Same-day rulings recorded there: payload
currency is fame with conditions (`REQ-Q1`), and the famous-pair structural gap (`DD-F1`)
is **a defect, not an accepted limitation** — most user-entered endpoints are famous, so
that pair class carries the app's implied promise.

**Track 3b is EXECUTED and read (2026-07-29, same day as its pre-registration): TB-R2
fired.** The verdict in its fixed wording lives in
[`2026-07-29-track3b-execution-log.md`](2026-07-29-track3b-execution-log.md) §5 and no
summary may soften it. In brief for orientation only: the toll family cannot produce
length-preserving descent on this graph; the thresholded form was its best case; the
mechanism question Track 3 left unresolved is resolved **negatively** for routing-side
toll devices. All prerequisites ran in the amended order — protocol review first, harness
review before the read — and the harness review reproduced the run completely and
independently. Record: the execution log; figures:
`builder/analysis/2026-07-29-track3b-thresholded-toll/`. Branch: `requirements-track3b`
(PR opened at this closeout).

## PARKED — owner's explicit decision, 2026-07-29; his trigger, never a session's

- **The candidate-pool product decision** — whether a shortened-but-obscure bypass
  candidate (Track 3's DD-A2 or a TB arm) ships at all, judged on requirements terms
  where shortening is priced by him, not by a criterion.
- **The one-statistic cross-track recompute** that must precede any DD-vs-TB comparison
  (cheap; no new walks; see the handoff).
- **Any blind listen on a router-only candidate** — the agreed sequencing defers the
  listen to the full stack (graph + device).

**Still owed by the owner, unchanged:**

1. **The use-the-app test** — [`TEST-QUEUE.md`](TEST-QUEUE.md), the **QUEUED (latest)**
   entry (the redesign, against `https://musicapp.cmiller.io`), including the phone half.
2. **The iPhone script** — carried inside that entry; still the single most valuable
   unrun test on the project.
3. **The `--prune` publish pass** — ripe since 2026-07-29; see the deferral table.

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). |

## Closed — do not re-plan or re-investigate

- **Track 2, Track 2F and the ceiling toll are exhausted nulls. Do not re-run any of them.**
- **Track 3's results are closed** (DD-A4/DD-A5 struck; pair set `pairs_v2.json`; anchors
  unscored; held-out gates nothing) **and Track 3b's results are now closed on the same
  terms** — do not re-run its arms or re-litigate TB-R2.
- **The routing-side toll family is closed for descent claims**: no toll-shaped bypass
  term may claim length-preserving descent; any explicit length-preserving constraint is a
  **new device needing its own pre-registration**, which must consume `TB-P5H-7` (TB-C2's
  gap in the read structure) at design time.
- **Loosening the both-ways cap is rejected** (`MKS-5b`); any targeted alternative must
  demonstrate its bound by simulation first.
- **Famous-pair first-path fame is barred as a scoring criterion** (PLA-R1).
- **The nameless-artist question is decided** (drop). Implementation comes due in the
  rebuild plan, above.
- **The builder-side p99 rescale stays parked** (DD-R2's trigger never fired); same for
  the `STC-6` re-crawl as a standalone — both are candidate *inputs* to the rebuild plan,
  not commitments.
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

## Deferred, with conditions

| Finding | Condition |
|---|---|
| **Nameless-artist drop rule** (decision made: drop) | **Before the next production rebuild — NOW DUE: the rebuild plan is the next work and must schedule it.** |
| **`TB-P5H-7`** — TB-C2's failure by TB-C1-passing arms is consumed by no pre-registered read | **If any successor bypass-device pre-registration is written** — its reads must consume every criterion combination. |
| **The candidate-pool recompute** (one statistic across DD and TB arms) | **If the owner picks up the parked candidate decision.** |
| The `--prune` publish pass | **Ripe since 2026-07-29** — `sync_frontend.py --prune --skip-build` once nobody still holds the previous `index.html`. Cost of skipping: a few kB of orphans; cost of running early: a white screen for a returning visitor (`FRO-1`). |
| ✅ `score_t3.py` A11-flag deferral | **DISCHARGED 2026-07-29** — TB-G4: the Track 3b scorer reads the flag; verified by TB-P5. Struck, kept for the record. |
| **The rate limit's headroom** — two users behind one IP could collide | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1**; a standalone version only if someone leans on PLA-R1's "arithmetic" reading beyond DD-P1's cover. |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
| The `STC-6` lower-threshold re-crawl probe | An input to the rebuild plan, not a standalone item — decided there. |
