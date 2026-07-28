# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-28 (late night), on the ASC-5 / Track 3 closeout.**

---

## Next

> ## 🔓 Path-quality work is UNPAUSED — owner decision, 2026-07-28.
>
> His goal, in his words: improve the frequency of obscure artists (and/or reduce the
> frequency of very famous artists) in path interiors, **especially when the bypass
> buttons are used.**

**The next action: execute Track 3 from its pre-registration, in a fresh session reading it
cold** — [`specs/2026-07-28-track3-depth-descent-preregistration.md`](specs/2026-07-28-track3-depth-descent-preregistration.md).
Discharge order (its §4): **DD-P2 → DD-P1 → DD-P3 → DD-P4**, then arms. Nothing in it
schedules a blind listen, a rebuild, or any owner spend.

- Handoff: [`2026-07-28-HANDOFF-track3-preregistered.md`](2026-07-28-HANDOFF-track3-preregistered.md)
- Record: [`2026-07-28-asc5-path-ascent-execution-log.md`](2026-07-28-asc5-path-ascent-execution-log.md)
- Evidence that shaped it: `builder/analysis/2026-07-28-asc5-path-ascent/` (ASC-5 is
  **discharged** — famous-pair first-path interiors are structurally forced; the bypass
  ladder's popularity profile is flat to d20; the jump price is immaterial at path level)
- PR: **#45** (branch `asc5-path-ascent-reread`)

**Decided 2026-07-28 and recorded at the tripwire (`acceptance.py`): the 33 nameless
artists are DROPPED, not backfilled.** The remediation is a standing build rule, not yet
implemented; the acceptance check stays in force and still blocks any production rebuild
until it lands. Implementing it belongs to whichever session next touches the builder ahead
of a rebuild.

**Still owed by the owner, unchanged by any of this:**

1. **The use-the-app test** — [`TEST-QUEUE.md`](TEST-QUEUE.md), the **QUEUED (latest)**
   entry (the redesign, against `https://musicapp.cmiller.io`), including the phone half.
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
- **The builder-side p99 rescale stays parked** until Track 3 answers: DD-R2 names it the
  next candidate on a Track 3 null with headroom present.
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
| **Nameless-artist drop rule** (decision made: drop) | **Before the next production rebuild.** The acceptance check is the forcing function. |
| The `--prune` publish pass | **Ripe from ~2026-07-29** (a day after the redesign publish). `sync_frontend.py --prune --skip-build` once nobody still holds the previous `index.html`. Cost of skipping: a few kB of orphans; cost of running early: a white screen for a returning visitor (`FRO-1`). |
| **The rate limit's headroom** — two users behind one IP could collide | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1**, which measures headroom where it matters — at bypass depth on Track 3's pairs. A standalone first-path version is only owed if someone wants to lean on PLA-R1's "arithmetic" reading beyond what DD-P1 covers. |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
| The `STC-6` lower-threshold re-crawl probe | If Track 3 nulls with headroom present (DD-R2), it is the other graph-side candidate beside the rescale. |
