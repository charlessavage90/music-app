# Deploying artistpath

**Deploys are manual and documented, because CI is deliberately out of scope**
(design `DEP-3`, owner's instruction; `DEP-15` records what that costs). This file is the
whole operational surface. If it is wrong, the deploy is wrong.

Governing design:
[`../docs/superpowers/specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](../docs/superpowers/specs/2026-07-26-gate2-deploy-and-telemetry-design.md)
— read its §12 amendments first. Plan:
[`../docs/superpowers/plans/2026-07-26-track-b-infrastructure.md`](../docs/superpowers/plans/2026-07-26-track-b-infrastructure.md).

---

## 0. Prerequisites

- **AWS CLI v2**, and an identity in **`us-east-1`**. IAM Identity Center
  (`aws configure sso`) is preferred over static access keys: the credentials are
  short-lived, so nothing long-lived sits on disk.
  **If a deploy fails partway with a credentials error, that is usually just an expired SSO
  session** — `aws sso login` and re-run. `cdk deploy` is idempotent.
- **Billing alerts enabled** in the account's billing preferences. Without it the
  `AWS/Billing` metric does not exist and the alarm sits in `INSUFFICIENT_DATA` forever.
- **Docker running**, for the image build.
- **The artifact and its sidecar on this machine.** Both are gitignored (`DEP-9`), so a
  deploy happens from a machine that has `builder/scratch/graph-t15-tiebreakfix.bin` and
  `…bin.json`. There is no way to fetch them from git.
- **`UV_LINK_MODE=copy` on every `uv` command** — hardlinking fails at `C:\dev\music-app`.
  uv falls back to copying by itself, so this suppresses the warning rather than being
  required. (The repository moved off OneDrive on 2026-07-27.)

Verify before starting:

```bash
aws sts get-caller-identity   # must print an account id
docker info > /dev/null && echo "docker ok"
```

## 1. Environment

**Seven variables are required and two are optional. The two secrets must never be
committed** — a password in a CDK source file is in the repository's history permanently.

| variable | required | what it is |
|---|---|---|
| `ARTISTPATH_FRONT_DOOR_SECRET` | yes | shared secret proving a request came through Cloudflare (`PW-7`). **Must equal the Cloudflare Transform Rule's `x-front-door` value** |
| `ARTISTPATH_DEPLOY_ORIGIN_SECRET` | yes | long random string; CloudFront sends it to App Runner |
| `ARTISTPATH_DEPLOY_BILLING_USD` | yes | billing alarm threshold, in dollars |
| `ARTISTPATH_DEPLOY_ALARM_EMAIL` | yes | where the alarm goes (confirm the SNS subscription email once) |
| `ARTISTPATH_DEPLOY_IMAGE_TAG` | **yes** | the commit tag being deployed — **never `latest`** (see below) |
| `ARTISTPATH_SITE_HOSTNAME` | **yes** | the permanent public name, `musicapp.cmiller.io` (`PW-5`, `G3-A5`) |
| `ARTISTPATH_CERTIFICATE_ARN` | **yes** | us-east-1 ACM certificate for that name (`PW-5`) |
| `ARTISTPATH_DEPLOY_GRAPH_KEY` | no | defaults to `graph-t15-tiebreakfix.bin` |
| `ARTISTPATH_DEPLOY_SIDECAR` | no | defaults to `../builder/scratch/graph-t15-tiebreakfix.bin.json` |

> **The certificate must be in `us-east-1`** — CloudFront accepts one from no other region —
> and it is requested **out of band**, not by CDK. CDK could request it, but DNS validation
> would block the deploy on a record only the operator can add, and `synth` must stay offline
> (`deploy_stage.py`'s docstring).
>
> **⚠ Never delete the ACM validation `CNAME` from Cloudflare.** ACM reuses that same record to
> renew the certificate automatically. Removed, renewal fails silently roughly thirteen months
> later and the site goes down when the certificate expires. It is harmless to keep and must be
> **DNS-only (grey cloud)** — proxied, it answers with Cloudflare's address and ACM never
> validates, which is the single most common way issuance stalls.
>
> A certificate not yet attached to anything reports `RenewalEligibility: INELIGIBLE`. That is
> expected and clears once CloudFront is using it.

Unlike the image tag, both of these are **per-machine and stable**, so they belong in
`infra/.env.deploy` alongside the secrets.

> **`ARTISTPATH_DEPLOY_IMAGE_TAG` became required on 2026-07-27** (`ARC-6`). It defaulted to
> `latest`, which contradicts this runbook's own rule that the tag is the only record of what
> is running — there is no CI to ask.
>
> **This was caught live rather than by reading.** `cdk diff` against the deployed stack showed
> it would repoint the service from its deployed commit tag to `latest`, silently, because
> `infra/.env.deploy` does not set the variable and nothing required it. A synth without it now
> **refuses**, naming the variable.
>
> **The secret file (`infra/.env.deploy`) is gitignored and documented nowhere else**
> (`ARC-11`). It holds the four secrets above and deliberately **not** the image tag — the tag
> is per-deploy, not per-machine, so persisting it is how you deploy the wrong commit.

> **There is no longer a site password, and there is no username.** `PW-7` removed both on
> 2026-07-28: `SITE_USERNAME`, `site_password` and `ARTISTPATH_DEPLOY_PASSWORD` are gone.
> **Send a new visitor the URL and nothing else.** The `RMD-11` / `FRO-2` history — the 401
> page had to name the username, because only the password was ever shared — is retained in
> git and no longer applies to anything live.
>
> ⚠ **`ARTISTPATH_FRONT_DOOR_SECRET` is not a replacement password and must never be given to
> a visitor.** It is how CloudFront tells Cloudflare's traffic from a direct hit on the
> generated CloudFront address, which bypasses the rate limit. Anyone holding it can bypass
> that limit. **Rotating it means changing the Cloudflare Transform Rule and redeploying
> together** — between the two the site refuses everyone, so do them back to back.

The graph's sha256 is **not** a variable: `app.py` reads it from the sidecar. Never
transcribe it by hand (`DEP-24`, `TR-10`) — its failure signature is "refuses to boot",
during a cutover.

## 1a. The Cloudflare front door

Established `PW-6`, 2026-07-28, with the site password still on — **`PW-7` then removed the
password the same day, and this front door is now the only access control there is.** Closes
`G3-A2` (*nothing anywhere limits how many requests one person can send*) at no cost, replacing
the AWS WAF the Gate 2→3 review assumed. Traffic path:

```
browser ──> Cloudflare (musicapp.cmiller.io) ──> CloudFront ──> App Runner
```

| Setting | Value |
|---|---|
| DNS record | `CNAME musicapp` → `d2n3xqz3pttguf.cloudfront.net`, **Proxied (orange)** |
| ACM validation record | `_09d26615…` — **DNS-only (grey), and must stay** |
| SSL/TLS mode | **Full (strict)** |
| Transform Rule | Modify Request Header, static `x-front-door`, value in `ARTISTPATH_FRONT_DOOR_SECRET` |
| Rate limiting | `URI Path equals /api/path`, by IP, **10 requests / 10 s**, Block 10 s |
| HTML caching | **Verified none** on 2026-07-28 — no Cache Rule or Page Rule caches HTML or sets "Cache Everything" |

> **⚠ The rate-limit period is 10 s, not the 60 s the plan specifies.** This Cloudflare plan
> offers **only** 10-second periods, for both the window and the block. **Do not scale the
> plan's `30 / 60 s` linearly to `5 / 10 s`** — a short window is burst-hostile, and the plan
> chose the generous end deliberately because friends behind one office NAT or one mobile
> carrier share an IP. Because the block is also 10 s, `10 / 10 s` reproduces the plan's
> *sustained* cap of ~0.5 req/s per IP while restoring the burst allowance the shorter window
> would otherwise remove.

> **⚠ Measured headroom is thinner than the arithmetic predicted, and this is the number to
> re-derive before Gate 3.** The owner's `PW-6` step 7b run — two journeys, well over 20
> bypasses, **deliberately fast and barely looking at the paths** — peaked at **6 path requests
per 10 s**, against a predicted
> ~1.7. So **one** fast user sits comfortably under 10; **two** behind a single IP would reach
> 12 and be blocked. Acceptable for Gate 2 (a handful of friends, rarely simultaneous).
> **Not obviously acceptable for a public launch**, where carrier-grade NAT puts unrelated
> strangers on one address. The five custom security rules are unspent and are the lever —
> a second rule keyed on something other than raw IP.

> **A CloudFront invalidation does NOT purge Cloudflare.** Today that is harmless because
> nothing caches HTML. If HTML caching is ever enabled, §6's deploy **must** gain a Cloudflare
> purge step, or returning visitors get a stale `index.html` referencing deleted asset hashes —
> `FRO-1`, which is invisible to whoever deploys because it only bites people who visited
> *before* the deploy.

### Re-verifying the front door

```bash
set -a && . ./.env.deploy && set +a
H=$ARTISTPATH_SITE_HOSTNAME; PW=$ARTISTPATH_DEPLOY_PASSWORD

curl -s -o /dev/null -w '%{http_code}\n' "https://$H/"                              # 401
curl -s -o /dev/null -w '%{http_code}\n' -u "artistpath:$PW" "https://$H/"          # 200
curl -s -o /dev/null -w '%{http_code}\n' -u "artistpath:$PW" "https://$H/path/$A/$B"  # 200
curl -s -o /dev/null -w '%{http_code}\n' -u "artistpath:$PW" \
  "https://$H/api/artists/search?q=radiohead"                                        # 200
```

**The rate limit fires, and only on abuse.** Use a *famous* pair — an obscure pair takes ~560 ms
server-side, so sequential requests never reach 10 per 10 s and the test silently proves nothing:

```bash
for i in $(seq 1 60); do
  curl -s -o /dev/null -w '%{http_code} ' -u "artistpath:$PW" \
    -X POST "https://$H/api/path" -H 'content-type: application/json' \
    -d "{\"sources\":[\"$A\",\"$B\"],\"exclude\":[]}"
done; echo
```

Expect ten `200`s then `429`. Measured 2026-07-28: first `429` at request **11**.

**Peak real usage** is read from CloudWatch. Note `filter event = "path"` returns nothing —
use `ispresent(bypass_depth)`, which is what actually distinguishes a path event from a clip
event:

```
fields @timestamp | filter ispresent(bypass_depth)
| stats count() as n by bin(10s) | sort n desc | limit 10
```

## 2. First deploy only — the storage stage

> ## ⛔ SKIP THIS SECTION unless `ArtistpathStack` does not exist yet
>
> **`-c stage=storage` against a deployed stack deletes the CloudFront distribution**, and a
> distribution never returns with the same domain — **every link anyone has been sent breaks
> permanently**, with no rollback. Nine resources go, the distribution among them (`ARC-1`;
> the review measured eight, before `RMD-10` added the autoscaling configuration — the set is
> derived in `tests/test_deploy_stage.py` rather than restated here).
>
> Since 2026-07-27 this **refuses to run** without an explicit confirmation flag, so the
> destructive path is no longer the reachable one. The refusal names what would break. If you
> are reading this on any deploy after the first, go to §3.
>
> Check, rather than remember:
> ```bash
> aws cloudformation describe-stacks --stack-name ArtistpathStack   # exists? skip to §3
> ```

**The very first deploy is staged, and skipping this wastes twenty minutes** (`TKB-7`). App
Runner cannot be created until its image is in ECR *and* the graph is in S3 — and ECR does
not exist until CDK creates it. Creating everything at once gives `CREATE_FAILED` on the
service and rolls the stack back.

```bash
cd infra
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
UV_LINK_MODE=copy npx cdk bootstrap aws://$ACCOUNT/us-east-1
UV_LINK_MODE=copy npx cdk deploy ArtistpathStack \
  -c stage=storage -c confirm-new-stack=true
```

`-c confirm-new-stack=true` is the guard above. It is not a formality: **it is the only thing
between a mistyped repeat of this command and every shared link dying.**

That creates the two buckets, the clip table, the ECR repository and the billing alarm —
**no App Runner instance, so nothing is billing by the hour yet.** Then do §3 (push the
image) and §4 (upload the artifact), and only then run the full deploy in §5.

> **A correction to why this staging is needed** (`ARC-1`, superseding `TKB-7`'s stated
> mechanism). `TKB-7` said a rollback deletes the ECR repository you just pushed to. It does
> not: the repository carries `DeletionPolicy: Retain`, verified in the synthesised template.
> The real reason is the reverse — a rollback **orphans fixed-name resources**
> (`artistpath-api`, `artistpath-clips`), and the next `cdk deploy` then fails
> `AlreadyExists` (`ARC-4`). The staging is still right; only the explanation was wrong, and
> it is recorded so nobody removes the staging on the strength of a mechanism that does not
> hold.

## 3. Build and push the image

Tag by commit, never `latest`: with no CI, the tag is the only record of what is running.

```bash
cd api
TAG=$(git rev-parse --short HEAD)
docker build -t artistpath-api:$TAG .

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REPO=$ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/artistpath-api
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag artistpath-api:$TAG $REPO:$TAG
docker push $REPO:$TAG
export ARTISTPATH_DEPLOY_IMAGE_TAG=$TAG
```

**The ECR repository must exist before the first push** — that is what §2 is for.

## 4. Upload the artifact

**Before App Runner exists**, because it loads the graph at boot: a service created with
nothing in the bucket fails its health check and rolls back.

```bash
BUCKET=$(aws cloudformation describe-stacks --stack-name ArtistpathStack \
  --query "Stacks[0].Outputs[?OutputKey=='ArtifactBucketName'].OutputValue" --output text)
aws s3 cp builder/scratch/graph-t15-tiebreakfix.bin      "s3://$BUCKET/graph-t15-tiebreakfix.bin"
aws s3 cp builder/scratch/graph-t15-tiebreakfix.bin.json "s3://$BUCKET/graph-t15-tiebreakfix.bin.json"
```

The sidecar goes up too: it is what makes *which graph is live* answerable without
transcribing a hash. Verify the upload is complete — a partial one presents at boot as a
checksum mismatch:

```bash
aws s3api head-object --bucket "$BUCKET" --key graph-t15-tiebreakfix.bin --query ContentLength
python -c "import json;print(json.load(open('builder/scratch/graph-t15-tiebreakfix.bin.json'))['bytes'])"
```

## 5. Deploy the full stack

**This is where the money starts:** App Runner bills for a warm instance from here on
(`DEP-17`, unmeasured).

```bash
cd infra
UV_LINK_MODE=copy npx cdk deploy ArtistpathStack
```

Outputs: `SiteUrl` (the CloudFront domain — this is the app), `ApiOriginUrl` (App Runner
direct, used for `/health`), `ArtifactBucketName`, `SpaBucketName`, `EcrRepositoryUri`,
`DistributionId`.

> **`cdk diff` and `cdk deploy` print the site credential to your terminal**, base64-encoded,
> as part of the viewer function's source. That is not a leak in the function — the gate has
> to hold the credential to compare against it — but it does mean the deploy output is not
> safe to paste into an issue, a chat, or a screenshot. Redact `Basic <...>` first.

> **`.env.deploy`'s lines are `export NAME=value`, so it is shell-sourceable and PowerShell
> is not.** `set -a; . ./.env.deploy; set +a` works in bash. In PowerShell the `export `
> prefix must be stripped before each line is split on `=`; a regex anchored on the variable
> name silently matches nothing and every variable stays unset, which surfaces as `app.py`
> naming whichever secret it happens to check first.

If the service reports `CREATE_FAILED`, read the App Runner application logs in CloudWatch
before changing anything. The two likely causes both say so explicitly: a checksum mismatch
(the §4 upload was partial) and a missing artifact key.

### 5a. Set log retention — REQUIRED, and CDK cannot do it

**App Runner creates its own log groups, and they default to *Never Expire*.** Design §5
specified 90 days; it was never implemented and appeared in no tracking document until
`ARC-2` found it. Confirmed live 2026-07-27: every log group in the account was Never Expire.

This matters because telemetry (`DEP-2`) has no other sink, so it accumulates forever under a
billing alarm that measures total spend rather than log storage — the failure is slow and
silent.

```bash
SERVICE_ID=$(aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='artistpath-api'].ServiceId" --output text)

for STREAM in application service; do
  MSYS_NO_PATHCONV=1 aws logs put-retention-policy \
    --log-group-name "/aws/apprunner/artistpath-api/$SERVICE_ID/$STREAM" \
    --retention-in-days 90
done

MSYS_NO_PATHCONV=1 aws logs describe-log-groups \
  --log-group-name-prefix "/aws/apprunner/artistpath-api" \
  --query "logGroups[].{Name:logGroupName,Retention:retentionInDays}"   # expect 90, not null
```

> **`MSYS_NO_PATHCONV=1` is required here** (execution log §6): Git Bash rewrites
> `/aws/apprunner/...` into a Windows path, and the API rejects it with a regex validation
> error that names the parameter but not the cause.
>
> **Re-run this whenever the service is recreated.** The group names contain the service id,
> so a new service means new groups, at Never Expire again. That is why this is a numbered
> step and not a note.

## 6. Build and sync the frontend

**One command. Do not publish by hand.**

```bash
cd infra && UV_LINK_MODE=copy uv run python -m artistpath_infra.sync_frontend
```

It builds the SPA, resolves the bucket and distribution from the stack, and publishes in
the only safe order. Add `--skip-build` to publish `frontend/dist` as it stands, and
`--prune` to also delete assets the new build no longer names — see below for when that is
safe. `--help` lists the rest.

> **Why this is a script and not three commands you type.** It was three commands, and it
> was the only fix in stage 3 held by nothing. Every rule below is now an assertion in
> `infra/tests/test_sync_frontend.py`, and each was checked by reintroducing the defect and
> confirming the suite goes red. **The failure this prevents is invisible from the machine
> that causes it** — you never meet the blank page yourself, only somebody who visited
> before the change does — so "read the section carefully" was never going to be enough.
> The commands themselves live in `sync_frontend.py`'s `plan_upload`; they are deliberately
> not restated here, because a second copy is how the two drift apart.

> **What the order is protecting, because you still need to know.** `FRO-1`, verified live
> by the reviewer: an object uploaded by a plain `aws s3 sync` carries `ETag` and
> `Last-Modified` and **no `Cache-Control`**, so browsers fall back to *heuristic* freshness
> and keep `index.html` for a duration nobody chose. A `--delete` then removes the hashed
> asset that stale copy points at. The visitor's browser asks for a file that no longer
> exists, and there is no error boundary — so the symptom is a **white screen with no
> text**, on a site that works perfectly for everyone else. `no-cache` on `index.html` is
> what stops it recurring; the immutable year on the hashed assets is what makes that cheap.
> `index.html` goes up **last** because it is the only object naming the hashed bundles: it
> is the switch that makes a build live, and thrown early it names files that are not there
> yet.

> **`--prune` is off by default, and that is `FRO-1` too.** Deleting the old assets while
> the old `index.html` is still live re-opens the same window for anyone mid-visit. Prune as
> a **separate, later** run, once the new `index.html` has been live long enough that nobody
> is still holding the previous one. Skipping it costs a few kilobytes of orphaned assets;
> running it too early costs a blank page. **The cutover deploy is the one exception** — the
> bucket is empty, so there is no returning visitor to protect and nothing to prune anyway.

> **The `Content-Type` caveat is now checked rather than remembered.** `aws s3 sync` guesses
> `Content-Type` from the file extension, and that is a property of the deploy *machine*,
> not of this repository — a module script served as `text/plain` is refused by the browser
> and gives the *same* blank page as `FRO-1`, from a completely different cause. The script
> reads back one uploaded `.js` object and refuses if it is not a type a browser will
> execute. **It does this between the two passes**, while the assets are up but nothing
> names them yet, which is the last moment the check is free. It was previously a note
> asking you to re-verify by hand if the deploy ever moved machines.

> **`index.html` carries static fallback markup** (`FRO-7`) inside `<div id="root">`, so a
> delivery failure shows a visitor readable text instead of white. It is verified to survive
> `vite build`, and two Vitest tests hold it: one that a JS-less browser sees words, one that
> React clears it on mount. **If you ever see that text on the live site, the app did not
> load** — that is the message doing its job, not a new defect.

The SPA calls `/api` relative (`frontend/src/api/client.ts`), so it needs no build-time URL.

## 7. The manual gates — there is no CI, so these are the regression gate

**All four, every deploy.** `DEP-30` makes the e2e run mandatory rather than advisory.

**Each block starts from the repo root.** `cd` is not cumulative here — run them as written:

```bash
cd "$(git rev-parse --show-toplevel)/api"      && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd "$(git rev-parse --show-toplevel)/builder"  && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd "$(git rev-parse --show-toplevel)/infra"    && UV_LINK_MODE=copy JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1 uv run --extra dev pytest -q
cd "$(git rev-parse --show-toplevel)/frontend" && npm test && npm run build && npm run test:e2e
```

**The gate is that each exits 0, not that it prints a particular number.** Expected counts
were stated here and went stale within the day — the infra figure was wrong the moment
`TKB-7` added a test, and a wrong expected count trains you to stop reading counts, which is
the only thing that would catch a *deleted* assertion. If you want the counts, run the
suites; they are not transcribed.

`npm run test:e2e` **needs the API running on :8000**; it starts only the Vite server
itself.

**Dependency scan — scan the image, not a manifest.**

```bash
snyk container test artistpath-api:$TAG --file=api/Dockerfile
cd frontend && npx snyk test          # reads package-lock.json directly
```

> **Why the image and not `requirements.txt`.** Snyk reads neither `uv.lock` nor a PEP-621
> `pyproject.toml`, so the obvious workaround is to export a `requirements.txt` and scan
> that. **That workaround silently scans nothing**: uv's venvs ship without pip, and the
> flag that works around *that* skips every package it cannot resolve, so the scan reports
> clean having examined zero packages. It was caught with a positive control — three
> packages with known high-severity advisories also came back clean (`TKB-4`). The image
> scan tested 87 dependencies and found 2 on its first run.
>
> **Known and accepted:** those 2 highs are `attr/libattr1` and `acl/libacl1`, introduced by
> `python:3.12-slim` itself, with no fixed Debian package yet (`TKB-6`). Snyk will suggest an
> Alpine base — **do not take it**: Alpine is musl, and numpy would have to build from
> source.

**Drift detection — the only gate that can see past the template.**

```bash
ID=$(aws cloudformation detect-stack-drift --stack-name ArtistpathStack \
  --query StackDriftDetectionId --output text)
aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id "$ID"          # wait for DETECTION_COMPLETE
aws cloudformation describe-stack-resource-drifts --stack-name ArtistpathStack \
  --stack-resource-drift-status-filters MODIFIED DELETED
```

> **Why this is a gate and not a curiosity.** Every other check here reads the *template* or
> the *source*. On 2026-07-27 the template was right, the test holding it was right and
> mutation-verified, and **production did not match either**: `ARTISTPATH_CORS_ORIGINS` was
> set to the empty string in the stack and simply did not reach the running service, so the
> API served its dev default (`RMD-6`). No test in any of the four packages can see that
> class of gap. One `detect-stack-drift` call found it immediately.
>
> **Five rows across two resources always report as drifted and are NOT drift.**
>
> On `ApiService`:
>
> 1. `/InstanceConfiguration/Cpu` — App Runner normalises `"1 vCPU"` to `"1024"`.
> 2. `/InstanceConfiguration/Memory` — likewise `"2 GB"` to `"2048"`.
> 3. `/SourceConfiguration/.../RuntimeEnvironmentVariables/N` — `ARTISTPATH_CORS_ORIGINS`,
>    expected `""`, actual `null`, `REMOVE`. **The index `N` moves** when the variable list
>    changes, so match on the name, never the path.
> 4. `/Tags`, `REMOVE` — the `app=musicapp` tag, applied by CLI. See below.
>
> On `ApiAutoScaling`, which before 2026-07-28 never appeared here at all:
>
> 5. `/Tags`, `REMOVE` — same tag, same reason.
>
> **Anything sixth is real** and blocks the deploy.
>
> **Rows 4 and 5 are deliberate and were added 2026-07-28** (`PW-5`). Both App Runner
> resources are **excluded from CDK tagging in `stack.py`** and tagged out of band:
>
> ```bash
> aws apprunner tag-resource --region us-east-1 --resource-arn "$ARN" --tags Key=app,Value=musicapp
> ```
>
> **This is not tidiness that can be cleaned up — tagging them through CDK is a deadlock.**
> App Runner's `Tags` property is immutable, so adding one forces a **replacement**; the service
> carries an explicit `service_name`, and CloudFormation creates a replacement *before* deleting
> the original, so App Runner refuses the duplicate name. **Measured, not reasoned:** a real
> deploy on 2026-07-28 failed and rolled back with
> *"Service with the provided name already exists: artistpath-api."* Retrying cannot help.
> `test_app_runner_is_deliberately_left_untagged` pins the exclusion; deleting it re-breaks the
> deploy.
>
> **`REMOVE` here reads from the template's point of view** — the tag exists in AWS and not in
> the template. It does not mean anything was removed.
>
> ⚠ **If either App Runner resource is ever replaced, the CLI tags go with it.** Nothing
> restores them automatically. Re-run the two `tag-resource` calls after any deploy that
> recreates the service.
>
> **The third row was `RMD-6`'s symptom and is now permanent by design** — this section said
> "expect exactly two, anything third is real" until 2026-07-27, which was correct only until
> `RMD-6` was fixed. The fix did not remove the empty variable from the template: `stack.py`
> keeps it deliberately as a statement of intent, and the guarantee moved to
> `ApiConfig.cors_origins`, which now defaults to empty so arriving-or-not is equally safe.
> App Runner still drops it, so it will drift forever. Verified after the Track C deploy:
> the exposure was gone from the running service (`/health` no longer echoes an Origin) while
> this row was still present. **Left as it was, the gate would have fired on every future
> deploy** — and a gate that always fires is one you learn to skip, which is the same failure
> the expected-test-counts note above is about.
>
> **Empty-valued environment variables are the known trap.** If a future variable must mean
> "off", make the *absence* safe in `ApiConfig` rather than relying on an empty value
> arriving — that is what `RMD-6` did.

## 8. Verify the deploy

```bash
API=$(aws cloudformation describe-stacks --stack-name ArtistpathStack \
  --query "Stacks[0].Outputs[?OutputKey=='ApiOriginUrl'].OutputValue" --output text)
SITE=$(aws cloudformation describe-stacks --stack-name ArtistpathStack \
  --query "Stacks[0].Outputs[?OutputKey=='SiteUrl'].OutputValue" --output text)

curl -s "$API/health"                                    # identity of the live graph
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/"        # expect 301 -> musicapp.cmiller.io
curl -s -o /dev/null -w "%{http_code}\n" "$API/api/artists/search?q=a"   # expect 403
```

- **`/health` is not reachable through CloudFront**, and that is not a bug: only `/api/*` is
  routed to App Runner. Check it at `ApiOriginUrl`, which is also where App Runner's own
  health checker reaches it.
- The **403** on the last line is `TR-7` working: App Runner's public URL must refuse a
  request that did not come through CloudFront.
- Confirm the reported identity **mechanically**, never by eye:

```bash
python -c "
import json,sys,urllib.request
s=json.load(open('builder/scratch/graph-t15-tiebreakfix.bin.json'))
h=json.load(urllib.request.urlopen(sys.argv[1]+'/health'))
assert h['graph_sha256']==s['sha256'] and h['artists']==s['artists'] and h['edges']==s['edges']
print('live graph matches the sidecar')" "$API"
```

### 8a. Prove the front door ADMITS — not only that it refuses (`FRO-4`, `RMD-13`)

**Renamed and rewritten at `PW-7`, 2026-07-28.** It previously read "Prove the gate ADMITS" and
described the shared password, which no longer exists. **The section is kept, not deleted** —
the property it protects is unchanged and is the reason it was written.

**Why it exists.** Every check in §8 proves the site *refuses*. Nothing there makes a request
that should be **admitted**, so `TR-5`'s SPA fallback — the rewrite that makes every shared
journey link work at all — could ship having never been exercised against the real
distribution. Review §7 names this one of three classes nobody verified. It almost certainly
works. **So did `TR-5`.**

**The mechanical half** — needs no browser, and is `PW-7`'s step 7 verbatim:

```bash
H=$ARTISTPATH_SITE_HOSTNAME
OLD=d2n3xqz3pttguf.cloudfront.net
# MBID_A / MBID_B: any two artists. Build one journey in the app and copy the
# two ids straight out of the address bar — all path state lives in the URL.

curl -s -o /dev/null -w "%{http_code}\n" "https://$H/"                       # expect 200
curl -s "https://$H/path/$MBID_A/$MBID_B" | grep -c '<div id="root"'          # expect 1
curl -s -o /dev/null -w "%{http_code}\n" "https://$H/api/artists/search?q=beatles"  # expect 200

# The old address must REDIRECT, not refuse — every link shared before PW-7 points at it.
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" "https://$OLD/path/$MBID_A/$MBID_B?known=$MBID_C"   # 301 + query string intact
curl -sL -o /dev/null -w "%{http_code}\n" "https://$OLD/path/$MBID_A/$MBID_B"  # expect 200
```

- Line 1 is the front door admitting. **If this refuses, the site is down for everyone**, and
  no §8 check would have told you.
- Line 2 is `TR-5`: a shared journey link holds no S3 object, so anything other than the SPA's
  entry point means the rewrite is not running on the live distribution.
- Line 3 is the whole `/api/*` behaviour end to end — CloudFront adding the origin secret, App
  Runner accepting it. A 403 here is `TR-7` refusing CloudFront itself.
- Lines 4 and 5 are the reason `PW-7` redirects rather than refusing. **A 403 on the old
  address would break every link already shared**, and the query string carries bypass state,
  so dropping it silently changes the journey the recipient sees.

**And the bypass must stay closed** — this is the check that keeps `PW-6` from being
decorative. Connect straight to CloudFront while claiming to be the real host:

```bash
curl -s -o /dev/null -w "%{http_code}\n" --connect-to "$H:443:$OLD:443" "https://$H/"   # expect 403, NOT a redirect loop
```

A 200 here means anyone who learns the CloudFront address can bypass Cloudflare's rate limit
entirely. A 301 means the no-loop branch is broken. Measured 2026-07-28: **403**, and the
refusal does not contain the secret.

**The browser half — what curl structurally cannot answer.**

1. **Does a path build from inside the app?** The one that matters most. curl fetches one URL;
   it never runs the SPA's own `fetch()` calls.
2. **Do in-app browsers work?** WhatsApp's and Instagram's used to be a real risk because they
   often suppress the Basic-auth dialog. **`PW-7` closed that class entirely** — there is no
   dialog any more, so a link opened from a message behaves like any other link. Recorded
   because it was a listed Gate 2 risk and is now resolved rather than merely untested.
3. **iOS Safari, and whether a clip plays at all on an iPhone.** Unanswered by anything, and
   unanswerable on Android. This is the review's `G3-F2`; the script lives in the current
   `TEST-QUEUE.md` entry.

## 9. Rollback

- **Bad image:** re-deploy with the previous tag — `export ARTISTPATH_DEPLOY_IMAGE_TAG=<old>`
  and `cdk deploy` again.
- **Bad graph:** the artifact bucket is versioned (`TR-9`), so restore the previous version
  id and re-deploy. The bucket is `RETAIN` — deleting the stack does not delete the graph.
- **Bad frontend:** rebuild from the previous commit, `s3 sync` again, invalidate.

## 10. If the stack is ever torn down and recreated

**Read this before deleting the stack, not after.** `ARC-4`: four resources carry fixed
physical names — `artistpath-api` (the ECR repository, the App Runner service, **and** the
autoscaling configuration) and `artistpath-clips` (the DynamoDB table). The repository and the
table are `RETAIN`, as is the artifact bucket. So **deleting the stack orphans them rather
than removing them**, and the next `cdk deploy` fails with `AlreadyExists` on the first one it
reaches.

That failure arrives at the worst possible moment — mid-recreate, with nothing serving — and
it reads as a CDK problem rather than as this. Order matters:

```bash
# 1. What survived the delete, and is therefore in the way.
aws ecr describe-repositories --repository-names artistpath-api
aws dynamodb describe-table   --table-name artistpath-clips
aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='artistpath-api']"
aws apprunner list-auto-scaling-configurations \
  --auto-scaling-configuration-name artistpath-api

# 2. Decide per resource: ADOPT (import into the new stack) or DELETE.
#    The clip table is a cache with a TTL — deleting it costs one repopulation.
#    The ARTIFACT BUCKET IS NOT: it holds the only second copy of the adopted
#    graph (TR-9), and acceptance.py refuses to rebuild it. Never delete it to
#    clear a name conflict; it has no fixed name and is not in the way anyway.

# 3. Only then recreate, storage stage first (§2) — with the confirmation flag,
#    which is legitimate here because the stack really does not exist.
```

> **The safer alternative, if this ever becomes routine:** drop the fixed names and let
> CloudFormation generate them, the way both buckets already work. That is the actual fix for
> `ARC-4` and it is deliberately **not** done here — renaming the live table and repository is
> a migration, not a cleanup, and this plan does not deploy one. This section makes the
> failure recoverable; it does not make it impossible.
