# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-28 (late night), on the Track 3 execution closeout.**

---

## Next

> ## 🔓 Path-quality work is UNPAUSED — owner decision, 2026-07-28.
>
> His goal, in his words: improve the frequency of obscure artists (and/or reduce the
> frequency of very famous artists) in path interiors, **especially when the bypass
> buttons are used.**

**Track 3 is EXECUTED and read (2026-07-28). The next action is the owner's decision, and
nothing is scheduled.**

**What he is deciding.** Track 3 produced a candidate that passes both pre-registered
criteria — but for a *different* trade than the one it set out to test: roughly **7
mostly-obscure artists against today's ~13 mostly-famous**. Whether that is better is
"what counts as better", which is his, and it sits on a real tension between two recorded
values in [`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) — value 1 counts novelty
absolutely and is satisfied; value 2 wants bypass to *lengthen* and add novelty, and the
lengthening half fails. **No blind listen, no adoption and no further arms are scheduled**;
all three are his.

The verdict in its fixed wording, and no summary may soften it: *DD-R1 fired on the letter;
the mechanism claim (depth-priced descent) is UNRESOLVED because DD-C6 flags every arm;
what exists is a measured candidate for a different trade, and that trade is the owner's to
judge.*

- Handoff: [`2026-07-28-HANDOFF-track3-executed.md`](2026-07-28-HANDOFF-track3-executed.md)
- Record: [`2026-07-28-track3-depth-descent-execution-log.md`](2026-07-28-track3-depth-descent-execution-log.md)
- Figures and the deliverable: `builder/analysis/2026-07-28-track3-depth-descent/`
  (`REPORT.md`)
- PR: **#46** (branch `track3-depth-descent`)

**Two structural findings that outlive the decision**, both in the execution log: superstar
endpoints have **zero** edges below the top popularity decile, so famous-to-famous journeys
cannot be routed through obscure interiors **at any price** — confirmed at device level, the
arms delivered nothing on them at any strength. And where obscure routes exist they are
*shorter* than what production delivers, so the router is not avoiding them for distance.

**The named successor is now STARTED — owner's trigger pulled 2026-07-29:** the
**thresholded toll** (execution log §7) is pre-registered as **Track 3b**
([`specs/2026-07-29-track3b-thresholded-toll-preregistration.md`](specs/2026-07-29-track3b-thresholded-toll-preregistration.md),
branch `product-requirements-baseline`, with `PRODUCT-REQUIREMENTS.md` — the owner's
Must/Should/Expect restatement that now governs where it and `WHAT-GOOD-LOOKS-LIKE.md`
disagree). No arm has run; first prerequisite is the TB-P1 analyst protocol review,
**dispatched on the owner's word**. Same-day owner rulings recorded there: REQ-Q1 (payload
currency = fame, with conditions), and the famous-pair structural gap (DD-F1) is **ruled a
defect, not an accepted limitation** — its remedy is graph-side and separately decided
(cap-selection simulation agreed as the feasibility step; unstarted).

*Prior track, for context only:* `builder/analysis/2026-07-28-asc5-path-ascent/` (ASC-5,
discharged; PR #45, merged) is what shaped Track 3's design.

**Decided 2026-07-28 and recorded at the tripwire (`acceptance.py`): the 33 nameless
artists are DROPPED, not backfilled.** The remediation is a standing build rule, not yet
implemented; the acceptance check stays in force and still blocks any production rebuild
until it lands. Implementing it belongs to whichever session next touches the builder ahead
of a rebuild.

**Still owed by the owner, unchanged by any of this:**

1. **The use-the-app test** — [`TEST-QUEUE.md`](TEST-QUEUE.md), the **QUEUED (latest)**
   entry (the redesign, against `https://musicapp.cmiller.io`), including the phone half.
   **Still untested as of the Track 3 closeout.**
2. **The iPhone script** — carried inside that same entry; still the single most valuable
   unrun test on the project.
3. **The `--prune` publish pass** — see the deferral table; ripe from about 2026-07-29.

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). |

## Closed — do not re-plan or re-investigate

- **Track 2, Track 2F and the ceiling toll are exhausted nulls. Do not re-run any of them.**
- **Loosening the both-ways cap is rejected** (`MKS-5b`); any targeted alternative must
  demonstrate its bound by simulation first.
- **Famous-pair first-path fame is barred as a scoring criterion** — structurally unable to
  move (PLA-R1, 2026-07-28). This includes any future rescale pre-registration.
- **The nameless-artist question is decided** (drop). What remains is implementation, above.
- **Track 3's own results are closed and must not be re-litigated.** DD-A4/DD-A5 are
  **struck** (bit-identical to DD-A2/DD-A3 at every scored depth) — do not re-add them to
  reach "six arms". The pair set is **`pairs_v2.json`**, the DD-P1 remedy. The all-famous
  anchors are **unscored by design**, and the held-out set **gates nothing** and must never
  be promoted to a gate.
- **The builder-side p99 rescale stays parked.** DD-R2 named it the successor *on a null*;
  Track 3 did **not** null, so its trigger did not fire and the rescale is not next by
  default. Same for the `STC-6` re-crawl.
- **The OneDrive migration is COMPLETE**; the old tree is an archive, never the working tree.
- **`G3-A5`, `G3-A2`, `G3-S7`** closed as recorded; **`G3-A3` does not fire** — do not
  re-add it. In-app-browser auth suppression is structurally impossible (no dialog).
- **`RMD-6`, `RMD-11`, `RMD-12`, `RMD-13`, `FRO-1`, `FRO-4`**, the `DEP-33` blockers, the
  Gate 1 clip work, **Track 1**.
  - ⚠ **One exception, live:** `BYP-13` — a card playing a clip by a *different artist of
    the same name*. Not Track 3 work and not inside any pause.

## Must not be changed, and each has a reason

- **`max_size=2` (`stack.py`)** — the **cost ceiling**, the only automatic spend control.
- **App Runner is excluded from CDK tagging** — tagging forces a replacement that cannot
  succeed; pinned by `test_app_runner_is_deliberately_left_untagged`.
- **The ACM validation `CNAME` at Cloudflare** — delete it and the certificate silently
  fails to renew in ~13 months.
- **The rate limit is `10 / 10 s`, not `30 / 60 s`** — see `infra/README.md` §1a.
- **The `acceptance.py` blank-name check** — do not weaken it to unblock a build;
  implement the drop rule.

## Deferred, with conditions

| Finding | Condition |
|---|---|
| **Nameless-artist drop rule** (decision made: drop) | **Before the next production rebuild.** The acceptance check is the forcing function. **Checked 2026-07-28: not due** — Track 3 did no rebuild. |
| **Track 3b — the thresholded toll**, `w · k · max(0, pctl(v) − 0.90)` | ✅ **TRIGGERED 2026-07-29 — pre-registered** (`specs/2026-07-29-track3b-thresholded-toll-preregistration.md`); no arm run yet. |
| **`score_t3.py` does not read A11's `potentially_notable_unmatched` flag**, which Track 2's scorer does | **Before any further fame-scored arm on mid-band pairs.** ✅ **Came due 2026-07-29** — Track 3b is that arm; its TB-G4 gate is the discharge (the TB scorer must read the flag). |
| The `--prune` publish pass | **Checked 2026-07-28: not yet due — ripe from ~2026-07-29**, i.e. tomorrow. (a day after the redesign publish). `sync_frontend.py --prune --skip-build` once nobody still holds the previous `index.html`. Cost of skipping: a few kB of orphans; cost of running early: a white screen for a returning visitor (`FRO-1`). |
| **The rate limit's headroom** — two users behind one IP could collide | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1**, which measures headroom where it matters — at bypass depth on Track 3's pairs. A standalone first-path version is only owed if someone wants to lean on PLA-R1's "arithmetic" reading beyond what DD-P1 covers. |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
| The `STC-6` lower-threshold re-crawl probe | If Track 3 nulls with headroom present (DD-R2), it is the other graph-side candidate beside the rescale. |
