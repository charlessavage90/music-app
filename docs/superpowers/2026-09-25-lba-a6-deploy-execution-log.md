# `LBA-A6` production deploy — execution log, 2026-09-25

**Role: RETAINED REASONING for the deploy that put `LBA-A6` (`graph-lba-a6.bin`) on unsung.fm.**
What was run, what each gate returned, and what was checked rather than assumed. **It owns no
status** (`NEXT.md`). **It owns exactly one figure: the #142 production query-cost reading in §5**,
because the document that owns the stage-2 query-cost figures
(`builder/analysis/2026-09-14-lbd-s4-stage2/README.md`) is a finished record and is not edited.
The artifact's identity is owned by `builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md`;
the adoption by [`2026-09-21-lbd-s4-a6-adoption-execution-log.md`](2026-09-21-lbd-s4-a6-adoption-execution-log.md)
Task 6.

Branch `charlessavage90/deploy-lba-a6-production`, off `main` at `b3e197b` (the merge of #234).

---

## §1 The instructions, and what was corrected before anything ran

The owner handed this session a nine-step sequence written by a docs-only consultant session and
asked for it to be validated against source before execution. Five corrections were raised; the
consultant accepted all five, and the owner cleared the run.

1. **The diff has four expected rows, not three.** The instance role's read statement is scoped to
   the object key (`stack.py`, `grant_read(instance_role, deploy.graph_key)`), so every map change
   moves IAM. The instruction said "anything else is a stop", which would have stopped on a row the
   same step depended on. Corrected: four expected rows, stop on a fifth, **show the owner the IAM
   delta before passing `--require-approval never`** — the precondition both earlier map swaps
   recorded (`CXA-` log §6, `CXR-` handoff item 2) and the instruction's README sentence dropped.
2. **Test gates before `cdk deploy`, not after.** §7's suites and image scan gate nothing once the
   stack has moved. Drift, `/health` and the front-door checks stay after, because they need it.
3. **A graph-only rollback must also roll the frontend back.** The landing's sample journeys are
   measured on the served map (Bad Bunny → Chappell Roan: 8 stops on the old map, 3 on this one),
   so an API-only revert leaves the landing advertising journeys the map does not build. The
   consultant's refinement, adopted: name the exact commit, `e5d8850`.
4. **#142 needed a method and a home.** Method in §5. Home: here, plus a comment closing #142 —
   the stage-2 README is finished and is not edited.
5. **§8's sidecar check cannot see the wrong artifact** (runbook §8's own ⚠). Added an assertion
   against the candidate README's independently recorded identity.

## §2 Pre-deploy — build, upload, gates

| step | result |
|---|---|
| HEAD | `b3e197b` = `origin/main`; `search.py` exact tier present (`15084fa`); `ApiConfig.graph_path` names `graph-lba-a6.bin` |
| Artifact | main tree `builder/scratch/graph-lba-a6.bin` sha256 equals its sidecar, which equals the candidate README (`28311d81…`) |
| Live before | image `759e80c`, `ARTISTPATH_GRAPH` = `…/graph-lux4.bin`, `RUNNING` |
| §3 image | built and pushed `artistpath-api:b3e197b`, digest `sha256:fba707c4…` |
| §4 upload | `graph-lba-a6.bin` + sidecar; `ContentLength` 39,697,349 = sidecar `bytes`; S3 version `fwToCytLIHlRVAxo5VmlFh81x9xkhjKF` |
| api / builder / infra pytest | exit 0 (347 / 292 / 72 passed) |
| frontend `npm test` + `npm run build` | exit 0 |
| `npm run test:e2e` | **12 passed**, against a local API booted on `graph-lba-a6.bin` by absolute path (`/health` confirmed the sha before the run) |
| `snyk container test` | three highs: the `TKB-6` pair (`attr`, `acl`) and `zlib1g` (#225). **All three `fixedIn: []`, `isUpgradable: false`**, so #225's condition (a fixed Debian package exists) has not come due |
| frontend `npx snyk test` | no vulnerable paths |
| `snyk_code_scan` on this session's one new script (`prod_p95_probe.py`) | two **Low** `python/PT` findings — a command-line path reaching `open()`. **Accepted, not fixed:** the operator running it by hand supplies both paths, so no trust boundary exists for a guard to defend |

## §3 The diff, and the fifth row that was not a change

Plain `cdk diff` showed exactly the four expected rows — the object-read statement moving from
`graph-lux4.bin` to `graph-lba-a6.bin` (same actions, same principal: a swap, not a widening),
`ARTISTPATH_GRAPH`, `ARTISTPATH_GRAPH_SHA256` (`fd92a735…` → `28311d81…`, taken from the sidecar by
`app.py`, never transcribed), and `.ImageIdentifier` (`759e80c` → `b3e197b`) — **plus the line
"Omitted 1 changes because they are likely mangled non-ASCII characters."**

An omitted row cannot be counted as "nothing else" unseen, so it was stopped on. `--strict`
showed it: `ViewerFunction`, whole `FunctionCode` replaced. **Checked, not assumed:** the LIVE
function code (`aws cloudfront get-function --stage LIVE`) and the synthesised template's
`FunctionCode` are **identical — 4,215 characters each, zero differing lines.** The row exists
because CloudFormation's stored template lost the source's non-ASCII comment characters. It is
inert. Earlier deploys that reported "exactly four" never ran `--strict`, so never saw it.
Recorded in runbook §5, with the warning that `--strict` prints the front-door secret (measured:
four occurrences; plain `diff` and `deploy` output: none of the three secrets).

**The owner was shown the IAM delta in full and said "go".** `cdk deploy --require-approval
never`, 15:13:55Z → 15:17:32Z, 195 s, exit 0.

## §4 Post-deploy — every check

| check | result |
|---|---|
| `/health` on `ApiOriginUrl` | sha `28311d81…395d5b`, 87,394 artists, 2,490,728 edges |
| §8 sidecar assert | **pass** |
| independent assert (candidate README: 87,394 artists, sha `28311d81…`) | **pass** — the half that can see a wrong artifact |
| `SiteUrl` / origin search without the secret | 301 / **403** (`TR-7`) |
| Service | image `b3e197b`, `RUNNING`, `CreatedAt` 2026-07-26 — **not recreated**, so the `tag-resource` calls and §5a retention were not re-run (tag `app=musicapp` confirmed present) |
| §6 `sync_frontend` (no `--prune`) | published; `assets/index-BJ_J8PSB.js` served as `text/javascript`; invalidation `/*` |
| §7 drift | exactly the five known rows (Cpu, Memory, `ARTISTPATH_CORS_ORIGINS`, two `/Tags`); **no sixth** |
| §8a front door | `/` 200; `/path/…` root div 1; served bundle `index-BJ_J8PSB.js`; `/api/artists/search` 200; old address 301 with query intact, followed 200; `--connect-to` bypass **403** |
| Done: Bad Bunny → Chappell Roan on production | **3 artists** — Bad Bunny → The Marías → Chappell Roan (landing constant `stops: 3` agrees) |
| Done: "Miles Davis" on production | first result *Miles Davis, jazz trumpeter, bandleader, songwriter*; then Quintet, Sextet |

**Not done here:** §8a's browser half (a path built from inside the app, and iOS Safari). It is
the owner's — the two `TEST-QUEUE.md` boxes queued for this deploy.

## §5 #142 — the query cost on the production container

**Method (the session's call, agreed with the consultant).** The stage-2 pair set,
`builder/analysis/2026-09-14-lbd-s4-stage2/s4_pairset.tsv` (sha256 re-verified `2713e536…`), 200
pairs, d0 (`exclude: []`), POSTed to `https://unsung.fm/api/path` **serially, one request in
flight, at least 1.3 s start-to-start** — under Cloudflare's 10 / 10 s. Timing is the
**server-side `duration_ms`** from the path event in CloudWatch, which brackets exactly
`find_journey`: the quantity stage 2 timed in-process. Events joined to the probe by
`(source.mbid, target.mbid)`, so no real visitor's request can enter the sample.

**Window, so nobody later reads it as a user:** 2026-09-25 **15:20:04Z → 15:29:32Z**, about 0.35
path requests/s, `User-Agent: artistpath-p95-probe/1.0 (#142)`. A first attempt at 15:19Z sent
20 requests that Cloudflare refused with **error 1010** (it blocks Python-urllib's default
user agent); none reached the origin, so they left no event and nothing to exclude.

**n = 200 of 200**: every request returned 200 with a non-empty path, and all 200 events were
matched. **CloudWatch delivered 21 of them several minutes late** (179 visible at +0 min, 200 at
about +3 min) — a query run right after a probe undercounts, and the missing rows are not
dropped. All 200 were served by one instance.

**Measured** (ms; stage-2 local figures are the `LBA-A6` row of that README, same 200 pairs):

| | p50 | p95 | max |
|---|---|---|---|
| **production, server-side `duration_ms`** | **2311.6** | **5511.1** | 9015.7 |
| production, client wall-clock via Cloudflare | 2411.6 | 5616.3 | 9143.3 |
| stage-2 local, `LBA-A6` bare | 657.7 | 1430.4 | — |
| **container ÷ local** | **3.51×** | **3.85×** | |

**What I infer, labelled as inference.**
- **The 2.5–3.5× multiplier understated the container.** This map runs at its top on the median
  and above it at p95. The multiplier came from the retired 75k map on different pairs; this is
  the direct reading #142 asked for, and it replaces the multiplier.
- **It does not reopen `LBA-G1`(b).** That gate is a ratio against the served map *in the same
  process*, so a uniform machine multiplier cancels. It would reopen only if the container
  penalised the larger map disproportionately, which this reading cannot test: the old map was
  not timed on the container on these pairs.
- **In plain terms:** someone who picks two random, not-especially-famous artists waits about
  2.3 s for the first path, 1 in 20 waits over 5.5 s, and the slowest waited 9 s. This pair set
  was drawn at random from the artists common to every map, not from the famous pairs people
  usually pick, so it says nothing about how fast those are.
- **Capacity:** at about 2.3 s of CPU per median request, one instance serves roughly 0.4 such
  requests/s. That tightens the Gate 2→3 review's `G3-A1`/`G3-S1` ceiling (it estimated ~1.5
  req/s); it matters for Gate 3, not for friends-and-family use.

**Weakest link.** One run, serial, one instance, at one time of day: no concurrency and no
repeat. The ratio also assumes the laptop stage 2 ran on still performs as it did on
2026-09-15. It would be falsified by a repeat run landing well away from these figures, or by a
same-pair container timing of `graph-lux4.bin` showing the same multiplier (which would mean the
map size is not the cause).

Raw data, committed: `builder/analysis/2026-09-25-lba-a6-prod-query-cost/` — the probe script,
its per-pair log (`prod_p95.jsonl`), and the CloudWatch events it was joined to
(`cw_path_events.json`, `@ptr` stripped).

## §6 The revert trigger — the owner's answer

**Asked 2026-09-25, after the deploy:** does the `LBA-G5` criterion (pre-registration §11,
`LBA-AM4`) carry forward as the production revert trigger? **His answer, verbatim:**

> past this point, no rule needs to be set. The expectation is that the blind listen and the
> adoption rule caught anything, and it's unlikely that the case will arise to revert at this
> point. The need to revert might come up, but it's useless to try to predict what would drive
> that. Reverting in the future is just owner decision, nothing to predict

**So there is no pre-set revert trigger for `LBA-A6` in production.** A revert is the owner's
decision whenever he makes it, and the mechanics are ready for it: `infra/README.md` §9's
graph-only rollback recipe. **A session must not propose a revert criterion, or read the
`LBA-G5` criterion as one** — the question was put to him and he closed it. This is unlike the
`CXA-` adoption, which carried a pre-set revert criterion (`CXR-` log §1).

## §7 What changed in the runbook

`infra/README.md`: §4's served-artifact line names `graph-lba-a6.bin` and its ⚠ block now reads as
history; §5 gains the four-row rule with the IAM-delta precondition, and the omitted-row check;
§5's stale "redact `Basic <...>`" note replaced with what was measured; §9 gains a graph-only
rollback recipe to `graph-lux4.bin` that includes the frontend from `e5d8850`.
