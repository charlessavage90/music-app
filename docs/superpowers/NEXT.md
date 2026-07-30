# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-30, on the Track B design closeout.**

---

## Next

> ## The next work is TRACK B's RUNS AND READS — `CB-5` then `CB-6`, in a fresh session.
>
> Entry point is the handoff:
> [`2026-07-30-HANDOFF-track-b-design.md`](2026-07-30-HANDOFF-track-b-design.md).
>
> **Track B's design phase is DONE through its named seam.** The plan
> (`plans/2026-07-30-graph-rebuild-track-b.md`) carries the owner's 2026-07-30 scope
> rulings in §0 — **cap-RULE selection, not k-tuning; the degree bound is a scoping
> constraint of this track, not a settled product conclusion; the uncapped row is a
> reference barred from selection**. The pre-registration
> (`specs/2026-07-30-track-b-cap-selection-preregistration.md`, `CRS-`, amended
> `A1`–`A5` pre-scoring) is committed; every instrument gate has run green **and** red.
> The runs are offline, deterministic, and under an hour of compute. **Three
> order-sensitive obligations bind the successor** — scorer dry-run first,
> `ALG-E`-`MK50`'s `C5` scored before any other `C5` (`CRS-A2`), reads in the prereg's
> own order — the handoff lists them.
>
> **Adoption of anything remains PARKED and is the owner's**, and it still owes a blind
> listen (`REQ-38`).

**The `LBS` semantics note is AUTHORITATIVE for the source algorithm's parameters**
(`findings/2026-07-30-lb-algorithm-semantics.md`): read from LB's own source, corrects the
2024 staff forum comment twice, supersedes every earlier paraphrase. `contribution` — the
one token separating `ALG-B` from production — is a per-user cap; `LBS-4` gives the
mechanism-shaped account of `RC-R1`'s stranding as labelled inference.

**The requirements baseline is unchanged since 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (`REQ-`) governs where it and
[`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) disagree (its §10 lists the
disagreements). `DD-F1` remains **a defect, not an accepted limitation** — and the
prereg's §0 bearing table now says, per family, which cap rules can even address it.

## PARKED — owner's explicit decision; his trigger, never a session's

- **The candidate-pool product decision** — whether a shortened-but-obscure bypass
  candidate (Track 3's DD-A2 or a TB arm) ships at all.
- **The one-statistic cross-track recompute** that must precede any DD-vs-TB comparison.
- **Any blind listen on a router-only candidate** — the listen is deferred to the full
  stack (graph + device).
- **`ALG-B` adoption** — the archive and artifact exist (`GRT-P4`); what remains parked is
  adoption, which retires the existing path-quality figures and owes a blind listen
  (`REQ-38`). Track B's `CRS-C6` and `CRS-R3` are direct inputs to it.
- **Re-evaluating bounded-degree itself** (router-priced unbounded graphs) — opened as a
  legitimate future track by the owner's 2026-07-30 ruling (plan §0), his trigger, and it
  would owe its own blind listen. Track B's uncapped reference row exists to give it
  measured baselines.

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
  threshold — neither is possible.** Parameter semantics are now `LBS-`'s, from source.
- **`CS-P0c` must not be cited as "no cap rule can fix `DD-F1`"** — its own text scopes it
  to rules selecting from a node's own list, and `CB-P1` measured the reverse direction:
  the union family's raw material exists in the tens of thousands. The prereg's §0 table
  owns per-family bearing; **only `banded_quota` union cells bear on `DD-F1`** among
  selectable rules, and a `CRS-C5` null elsewhere is confirmation, not a finding.
- **The `--target`-capped trial crawl is RETIRED as the instrument for `AS-H2`** — retired
  for that question, not for all questions (it remains the only way to reach component
  membership). Do not re-propose it for stranding.
- **Track 2, Track 2F and the ceiling toll are exhausted nulls. Do not re-run any of them.**
- **Track 3's and Track 3b's results are closed** — do not re-run their arms or re-litigate
  TB-R2.
- **The routing-side toll family is closed for descent claims**; any explicit
  length-preserving constraint is a **new device needing its own pre-registration**, which
  must consume `TB-P5H-7` at design time.
- **Loosening the both-ways cap without a simulated bound is rejected** (`MKS-5b`) — and
  **Track B is that simulation being run**, not a violation of it. `CS-P0f` and `RC-A2`
  are consumed at its design time (prereg §0).
- **Famous-pair first-path fame is barred as a scoring criterion** (PLA-R1) — the Track B
  prereg resolves its applicability from its grounds: presence-of-obscure is measured,
  fame-of-interior never is.
- **The nameless-artist question is decided** (drop; implemented, `GR-1`, standing rule).
- **The builder-side p99 rescale stays parked** (DD-R2's trigger never fired).
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
- **The `acceptance.py` blank-name check** — do not weaken it to unblock a build. And
  `GRT-P2` stands: the guard is blind to a severe famous-artist collapse at any scale;
  strengthening it is an unclaimed design question, not part of Track B.
- **The mirror's two device knobs (`w_known_ramp_pctl`, `w_known_thresh_pctl`) stay 0.0.**
- **`BuilderConfig.algorithm` still carries `contribution_5`**; changing it *is* the
  re-crawl decision. Likewise `max_neighbours_per_artist = 50` and
  `cap_strategy = "mutual_knn"` — **Track B is analysis-only and moves no default**.

## Deferred, with conditions

| Finding | Condition |
|---|---|
| **Track B runs and reads** (`CB-5`/`CB-6`) | **The named next work.** Fresh session, prereg read cold, order-sensitive obligations in the handoff. |
| ✅ **Re-scoring `rc_raw_records.json` at a different `k`** | **DISCHARGED 2026-07-30 by supersession** — both full archives are on disk, so the cells answer the question directly (prereg §0). Struck, kept for the record. |
| **`CRS-A5` endpoint re-verification** | **One request at `CB-5` scoring time**, before the descriptive `C6` companion is used; descriptive only either way. |
| **The `LBS` `filter` token's meaning** | **Accepted, won't chase** — absent from current upstream master, and it cannot bear on the `ALG-B` decision (both arms carry `filter_True`). Reopen only if a permitted value differing in `filter` ever needs one-knob attribution. |
| **13 pre-existing Snyk findings under `builder/analysis/`** | **Accepted, won't fix**, reopening condition unchanged: if a frozen probe is un-frozen and edited, or `listen.html` is ever served. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. The Track B harness complies (reads via `ReadOnlyArchive`). |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| **`TB-P5H-7`** | **If any successor bypass-device pre-registration is written.** `CRS` is not one. |
| **The candidate-pool recompute** | **If the owner picks up the parked candidate decision.** |
| The `--prune` publish pass | **Ripe since 2026-07-29** — `sync_frontend.py --prune --skip-build` once nobody still holds the previous `index.html`. |
| **The rate limit's headroom** | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1.** |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
