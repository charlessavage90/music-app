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

Five variables are required and two are optional. **The two secrets must never be
committed** — a password in a CDK source file is in the repository's history permanently.

| variable | required | what it is |
|---|---|---|
| `ARTISTPATH_DEPLOY_PASSWORD` | yes | the shared site password |
| `ARTISTPATH_DEPLOY_ORIGIN_SECRET` | yes | long random string; CloudFront sends it to App Runner |
| `ARTISTPATH_DEPLOY_BILLING_USD` | yes | billing alarm threshold, in dollars |
| `ARTISTPATH_DEPLOY_ALARM_EMAIL` | yes | where the alarm goes (confirm the SNS subscription email once) |
| `ARTISTPATH_DEPLOY_IMAGE_TAG` | no | defaults to `latest`; set it per §2 |
| `ARTISTPATH_DEPLOY_GRAPH_KEY` | no | defaults to `graph-t15-tiebreakfix.bin` |
| `ARTISTPATH_DEPLOY_SIDECAR` | no | defaults to `../builder/scratch/graph-t15-tiebreakfix.bin.json` |

The graph's sha256 is **not** a variable: `app.py` reads it from the sidecar. Never
transcribe it by hand (`DEP-24`, `TR-10`) — its failure signature is "refuses to boot",
during a cutover.

## 2. First deploy only — the storage stage

**The very first deploy is staged, and skipping this wastes twenty minutes** (`TKB-7`). App
Runner cannot be created until its image is in ECR *and* the graph is in S3 — and ECR does
not exist until CDK creates it. Creating everything at once gives `CREATE_FAILED` on the
service and rolls the whole stack back, **deleting the ECR repository you just pushed to**.

```bash
cd infra
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
UV_LINK_MODE=copy npx cdk bootstrap aws://$ACCOUNT/us-east-1
UV_LINK_MODE=copy npx cdk deploy ArtistpathStack -c stage=storage
```

That creates the two buckets, the clip table, the ECR repository and the billing alarm —
**no App Runner instance, so nothing is billing by the hour yet.** Then do §3 (push the
image) and §4 (upload the artifact), and only then run the full deploy in §5.

Subsequent deploys skip this section entirely.

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
