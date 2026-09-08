# Handoff — `LUX-4` complete, the wire and the card, 2026-09-08

**Role: ACTIVE — this is the CURRENT handoff FOR THE `LUX-4` TRACK.** Nothing supersedes it.
Supersedes [`2026-09-06-HANDOFF-lux-4-artifact.md`](2026-09-06-HANDOFF-lux-4-artifact.md)
on **everything** — that handoff's remaining tasks are all done. It does **not** state project
status: for that read [`NEXT.md`](NEXT.md), which owns it.

⚠ **A SECOND track is live and has its own current handoff** —
[`2026-09-07-HANDOFF-lbd-preregistration.md`](2026-09-07-HANDOFF-lbd-preregistration.md) for
`LBD-`, being worked in a worktree at `C:\Users\charl\worktrees\music-app-lbd` on `lbd-task3`.
**Neither supersedes the other** and neither blocks the other.

**A SEAM handoff — the plan's last task, and the plan is finished.** The degradation tell did
not fire. Branch `lux-4-wire-and-card`, **PR #112** — both are addresses; `git` and `gh` own
what has landed.

---

## Start here

**Nothing in `LUX-4` is left to build.** `L4-T1`–`L4-T11` are all done, across two PRs
(#105 for the artifact, #112 for the wire and the card).

**What is assigned to the owner** is unchanged in shape and order — merge, deploy, then the
queued tests — but this work adds to the middle of it. `NEXT.md` owns that sequence.

⚠ **The deploy is not API-only.** The artifact changes to `graph-lux4.bin`, so both `s3 cp`
lines run and a `cdk diff` showing `ARTISTPATH_GRAPH` / `ARTISTPATH_GRAPH_SHA256` change is
**expected here** rather than being the `DEP-34` warning firing. `infra/README.md` §4 and §5
now say so at the point of use. Take the checksum from the sidecar (`DEP-24`).

**Two test-queue entries are now live** (2026-09-04 and 2026-09-08) and **both are blocked on
the same deploy**, so they are one sitting rather than two.

## What this session did

`L4-T8`, `L4-T9`, `L4-T10`, `L4-T11`, cold from the `L4-T7` seam. Reasoning and figures are in
the retained log, [`2026-09-06-lux-4-execution-log.md`](2026-09-06-lux-4-execution-log.md)
§8–§13 — cited, not restated here.

1. **`L4-T8`** — the api reads the three additive APG1 keys through bounds-checked accessors.
2. **`L4-T9`** — `ArtistOut` carries `spotify_id`, `apple_id`, `facts`. Wire contract.
3. **`L4-T10`** — both streaming services on every card, a missing id degrading to a search
   link. Plus the boundary mapper the plan wrongly assumed existed (below).
4. **`L4-T11`** — the structured facts line, the deploy note, the queue entry.

## Claims an editor must NOT revert

- **The plan was wrong about the repository a FIFTH time, and `NEXT.md` now says five.** The
  handoff before this one said four; that was true when written. `L4-T10` step 6 claims the
  API layer "already maps snake_case at the boundary" — **it does not**, and did not. Artists
  were cast straight through. Do not re-introduce the cast, and do not "simplify"
  `artistFrom` away: a declared `spotifyId` over a `spotify_id` object is `undefined` at
  runtime, and `undefined` renders as a **search link exactly as a genuine absence does**, so
  the defect is invisible in the only place anyone would look.
- **`ArtistOut` reaches the wire in FOUR positions, not three.** The plan names three;
  `GET /api/artists/search` is the fourth. All four come from `app.py`'s single `artist_out`
  helper, which now carries a comment saying so. **Do not add a second construction site.**
- **The accessors are `spotify_id_of` / `apple_id_of` / `facts_of`, and they return `None`,
  not `""`.** Both differ from the plan deliberately. The naming matches the file's one
  precedent, `deezer_id_of`, and avoids a bare form one character from the field name whose
  typo yields a truthy bound method. The return type differs *from* `deezer_id_of` because
  these three go straight onto the wire, where null means "render a search link".
- **The facts line WRAPS. Do not restore `truncate`.** Under it the line lost its life span on
  most real artists at 390px. `e2e/responsive.spec.ts` pins this and **was shown to go red**
  under `truncate` before being trusted.
- **`L4-D3` — render only what is present, no placeholder rows — shipped by assertion**, as
  the plan permits while `LUX-E2` is blocked. That is not an oversight to "fix" with an
  "Unknown" row.

## Two things that are NOT owed, and read as if they might be

- **`LUX-E2` is still BLOCKED** on its damaged `TAS-` sample. This did not touch it and did
  not unblock it. If it later finds a field too sparse in the obscure half, the consequence is
  a **designed empty state in `ArtistInfo.tsx` — a frontend edit, not a rebuild.** The
  artifact carries the data either way, which is what made `L4-D3` safe to take now.
- **The Deezer id gap deferral has NOT come due.** Its condition is *the first rebuild after
  `LUX-4` merges*. No rebuild happened here, so it stays open and unchanged.

## What I know that is not in the durable record

1. **`NEXT.md` got a surgical edit, not the wholesale rewrite `closeout` A2-next prescribes.**
   Deliberate, and the reason is the live `LBD-` worktree: `CLAUDE.md` says a one-paragraph
   strike reconciles in either merge order and a wholesale rewrite does not. Only the `LUX-4`
   paragraph changed. **The next session to close out with no concurrent track should do the
   full rewrite** — the outgoing block still needs demoting to `NEXT-ARCHIVE.md`, and that
   step is now one closeout in arrears.
2. **The truncation defect was found by taking a screenshot, not by any test**, with all
   suites green, `tsc` clean and 8 e2e passing. The reusable form is in the log §11 and is the
   rendering twin of §7's "survey a field's value distribution before writing its first
   consumer": **look at the real thing on real data before believing a green suite about a
   visual change.**
3. **A date claim was wrong by one day and was corrected at closeout** — comments said the
   keys are absent from artifacts built before 2026-09-05; `git log -S` puts the writing
   commit at 2026-09-06. Trivial, but it is the "confident prose about correct code" class,
   and it was in a comment two future readers would have trusted.
4. **Snyk was blocked for the first half of the session** (expired credentials, MCP
   "User not authenticated", CLI `SNYK-0005 401`) and `L4-T9` was committed with the scan
   recorded as **owed, not waived**. The owner re-authed mid-session; both packages then
   scanned clean on this diff. **Two pre-existing findings were left alone deliberately**: one
   Low in `api/tests/test_origin_secret.py` (last touched 2026-08-06) and four in
   `frontend/design/*/support.js` vendored mockups. Neither is in this diff and neither is
   shipped first-party code.
5. **The `L4-T11` step-8 queue entry and the `TEST-QUEUE.md` live count were both written.**
   The count was re-counted to TWO rather than carried forward, per that file's own rule.

## Nothing is in flight

No background jobs, no dispatched subagents still working, no half-written directories. **Ports
8000 and 5173 are both free** — the API this session ran on `graph-lux4.bin` was stopped, and
nothing was left detached, because both queued tests exercise the deployed site rather than a
local server. The working tree is clean and everything is pushed.
