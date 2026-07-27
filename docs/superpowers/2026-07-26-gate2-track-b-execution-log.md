# Gate 2 Track B — execution log

**Role: ACTIVE record of Track B.** Identifiers `TKB-`. Plan:
[`plans/2026-07-26-track-b-infrastructure.md`](plans/2026-07-26-track-b-infrastructure.md).
Design: [`specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](specs/2026-07-26-gate2-deploy-and-telemetry-design.md)
(§12 amendments first). Binding review:
[`findings/2026-07-26-gate1-gate2-team-review.md`](findings/2026-07-26-gate1-gate2-team-review.md).

**Status: tasks 1–11 and 13 executed; the stack is DEPLOYED and verified. Task 12
(`DEP-33`'s review re-run) is NOT done and is owed before cutover.** PR #29.

**No routing, weight, graph or cost-function change.** `pathfinding.py` was never opened.
The path-quality pause is intact and nothing here is a resume signal.

---

## §1 What is live

| what | value |
|---|---|
| account / region | `826731842184` / `us-east-1` |
| site (CloudFront) | `https://d2n3xqz3pttguf.cloudfront.net` |
| API origin (App Runner) | `https://3umzhjfxuj.us-east-1.awsapprunner.com` |
| distribution id | `E1S07XVIOW6A22` |
| artifact bucket | `artistpathstack-artifactbucket7410c9ef-b7lbgisct423` |
| SPA bucket | `artistpathstack-spabucket48e1059f-yo67wwanhbpj` |
| image tag deployed | `9f5343d` |
| graph key | `graph-t15-tiebreakfix.bin` |

**The SPA bucket is empty**, so the site returns 403 to an authenticated request. That is
Track C's job, not a defect.

## §2 Verified live, not merely synthesised

Each of these could only be checked against the running stack.

| check | result |
|---|---|
| `/health` vs the manifest sidecar — sha256, artists, edges | **all three match** (`TKA-11` closes) |
| site without the password | **401** |
| App Runner's own URL, no CloudFront header | **403** (`TR-7`) |
| App Runner's own URL with the header | **200** — so the middleware is checking, not just rejecting |
| site with the password, `/api/artists/search` | **200** |
| three different `?q=` values through CloudFront | **three different artists** — query strings are forwarded, not cached-once (`TR-6`) |
| `POST /api/path` through CloudFront | **200**, `Radiohead → Depeche Mode → Daft Punk` — `ALLOW_ALL` methods works |
| clip lookup, twice | **200** both times; the DynamoDB table holds 1 item, so the instance role's `GetItem`/`PutItem` grant is real |
| telemetry in CloudWatch | both event types present |
| `journey_id` in the logged `path` event | **`deployprobe123`** — the header survived CloudFront, so the origin request policy is right and `DEP-6` is intact |

That last one is the check worth keeping: `TR-6` warns CloudFront strips unlisted headers,
and a stripped `x-journey-id` would have degraded telemetry silently — every event landing
with `journey_id: unknown` and nothing failing.

## §3 Findings against the design and against this plan

`TKB-1` … `TKB-8` are stated in full in the plan; this is the index.

| id | one line |
|---|---|
| `TKB-1` | the artifact upload cannot wait for Track C — App Runner loads the graph at boot |
| `TKB-2` | `TR-5`'s prescribed `errorResponses` fix is **distribution-level** and would rewrite the API's own errors into HTML with status 200 |
| `TKB-3` | Snyk reads neither `uv.lock` nor a PEP-621 `pyproject.toml` |
| `TKB-4` | **the scan this plan first prescribed was vacuous** — 0 issues while examining 0 packages |
| `TKB-5` | scan the image instead; 87 dependencies, demonstrably non-vacuous |
| `TKB-6` | 2 highs from `python:3.12-slim` itself; Alpine refused (numpy on musl) |
| `TKB-7` | the first deploy must be staged, or App Runner `CREATE_FAILED` rolls back and deletes the ECR repository just pushed to |
| `TKB-8` | App Runner is closed to new customers; **this account can still use it**, measured |

**`TKB-4` is the one to read.** The plan prescribed a dependency scan, the scan went green,
and the green meant nothing: uv's venvs ship without pip, and the flag that works around that
skips every package it cannot resolve. It was caught by a **positive control** — feeding it
three packages with known high-severity advisories, which also came back clean. Nothing else
in the process would have caught it, and it is the third instance of this shape here after
`FMS-P1` and `TR-2`.

> **The lesson that generalises: a green result from a *new* instrument is not evidence until
> the instrument has been shown to go red.** The existing rule ("every new test must fail
> before its fix") covers tests. It did not cover a *scanner*, a *linter*, or any other
> acquired tool, and that is exactly where this one got through.

## §4 Claims that must NOT be reverted

1. **`ARTISTPATH_CORS_ORIGINS` is set to the empty string, not omitted.** Omitting it yields
   `config.py`'s dev default `http://localhost:5173`. Same-origin means no preflight ever
   fires, so nothing would reveal the mistake (`TR-8`). A test holds it and **goes red when
   the line is deleted** — checked by mutation.
2. **The origin-secret middleware exempts `/health`.** App Runner's health checker reaches
   the origin directly and cannot be given the header; gating it fails every deploy and rolls
   it back. Also held by a mutation-checked test.
3. **The distribution has no `errorResponses`.** See `TKB-2`. The SPA fallback belongs in the
   viewer function, which is per-behaviour.
4. **The `/api/*` behaviour pins `CACHING_DISABLED`.** Caching the re-signed clip URL
   resurrects C2, closed 2026-07-25 and marked do-not-re-plan — it would present as a
   regression in closed work.
5. **`Authorization` is deliberately not in the origin request policy allow-list.** The
   browser attaches it to same-origin fetches, the edge function checks it, and it has no
   business reaching the API.
6. **The artifact bucket has no CloudFront origin and is `RETAIN`.** `TR-7`, `TR-9`.

## §5 What is owed, and what it costs

- **`DEP-33` — the team review re-run against the CDK stack. NOT DONE.** The owner chose to
  deploy first, which is consistent with the finding (it requires the review *before
  cutover*, and cutover is Track C). **It is owed before anyone is sent the URL.**
- **`TR-5`'s SPA fallback is UNVERIFIED.** It cannot be tested until the SPA is synced: with
  an empty bucket every path returns 403 whether the rewrite works or not. **The first thing
  Track C should check** is that a shared journey URL returns 200 — it is the finding two
  reviewers found independently, and the one that would break the property CLAUDE.md gives as
  the reason path state lives in the URL.
- **`DEP-16`'s telemetry round-trip** — replay a logged `path` event offline and confirm the
  path reproduces. There is now real logged data to do it with (§2). Not done.
- **`DEP-17` — cost is unmeasured.** The alarm exists at $25. App Runner at 1 vCPU / 2 GB is
  the dominant line and the first knob to turn down.
- **`TKB-6`** — recheck the base image at each deploy with the container scan.

## §6 Environment notes that cost time

- **`MSYS_NO_PATHCONV=1` is required** for any `aws` command whose argument starts with `/`.
  Git Bash rewrites `/aws/apprunner/...` into a Windows path and the API rejects it with a
  regex validation error that names the parameter but not the cause.
- **The AWS CLI is not on `PATH`** in shells started before it was installed. Full path:
  `C:\Program Files\Amazon\AWSCLIV2\aws.exe`.
- **`JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1`** quiets a Node 20 EOL banner from jsii.
  Node 20 works; jsii wants ≥22.
- **jsii prints an `ENOTEMPTY` rmdir error at process exit** on Windows. It is cleanup noise
  **after** the run and does **not** affect the pytest exit code — verified, because a suite
  whose exit code is unreliable is not a gate.
- Docker Desktop must be running; the daemon is not started by the CLI.

## §7 Cost of the probe

`TKB-8`'s availability probe was a real App Runner service (0.25 vCPU / 0.5 GB, ~5 minutes,
public sample image), created and deleted. Its log groups remain in CloudWatch and are the
only trace. Cents.
