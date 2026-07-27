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
- **`UV_LINK_MODE=copy` on every `uv` command** — the repository is under OneDrive.

Verify before starting:

```bash
aws sts get-caller-identity   # must print an account id
docker info > /dev/null && echo "docker ok"
```

## 1. Environment

**Five variables are required and two are optional. The two secrets must never be
committed** — a password in a CDK source file is in the repository's history permanently.

| variable | required | what it is |
|---|---|---|
| `ARTISTPATH_DEPLOY_PASSWORD` | yes | the shared site password |
| `ARTISTPATH_DEPLOY_ORIGIN_SECRET` | yes | long random string; CloudFront sends it to App Runner |
| `ARTISTPATH_DEPLOY_BILLING_USD` | yes | billing alarm threshold, in dollars |
| `ARTISTPATH_DEPLOY_ALARM_EMAIL` | yes | where the alarm goes (confirm the SNS subscription email once) |
| `ARTISTPATH_DEPLOY_IMAGE_TAG` | **yes** | the commit tag being deployed — **never `latest`** (see below) |
| `ARTISTPATH_DEPLOY_GRAPH_KEY` | no | defaults to `graph-t15-tiebreakfix.bin` |
| `ARTISTPATH_DEPLOY_SIDECAR` | no | defaults to `../builder/scratch/graph-t15-tiebreakfix.bin.json` |

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

The graph's sha256 is **not** a variable: `app.py` reads it from the sidecar. Never
transcribe it by hand (`DEP-24`, `TR-10`) — its failure signature is "refuses to boot",
during a cutover.

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

```bash
cd frontend && npm run build
SPA=$(aws cloudformation describe-stacks --stack-name ArtistpathStack \
  --query "Stacks[0].Outputs[?OutputKey=='SpaBucketName'].OutputValue" --output text)
DIST=$(aws cloudformation describe-stacks --stack-name ArtistpathStack \
  --query "Stacks[0].Outputs[?OutputKey=='DistributionId'].OutputValue" --output text)
aws s3 sync dist/ "s3://$SPA/" --delete
aws cloudfront create-invalidation --distribution-id $DIST --paths "/*"
```

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
> **Two rows always report as drifted and are NOT drift.** App Runner normalises
> `Cpu: "1 vCPU"` to `"1024"` and `Memory: "2 GB"` to `"2048"`. Expect exactly those two on
> `ApiService` and nothing else; **anything third is real** and blocks the deploy.
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
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/"        # expect 401 without the password
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
