# Gate 2 Track B — Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Role: ACTIVE, not yet executed.** Governing design:
[`../specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](../specs/2026-07-26-gate2-deploy-and-telemetry-design.md)
— **read its §12 amendments first**; several §2–§4 passages are struck in place by them.
Binding review: [`../findings/2026-07-26-gate1-gate2-team-review.md`](../findings/2026-07-26-gate1-gate2-team-review.md)
(`TR-`). Predecessor: Track A (`TKA-`, PR #27) and Track D (`TKD-`, PR #28), both merged.

**Identifiers are namespaced `TKB-`** — verified unused across `docs/`, `api/`, `builder/`
and `frontend/src` before allocation, and disjoint from `DEP-`, `TR-`, `TKA-`, `TKD-`,
`FMS-`, `CNS-`, `BYP-`, `MKS-`, `ASC-`, `STC-`, `CLM-`, `T3-`, `TF-`.

**This document owns no measured figures.** The artifact's sha256, artist count and edge
count are read from the manifest sidecar at deploy time and are never transcribed here
(`DEP-24`). Path-quality work remains paused; nothing in this plan touches `pathfinding.py`,
any weight, the graph, or the cost function.

**Goal:** Put the existing app on AWS behind one CloudFront domain — App Runner serving the
API with the graph loaded from S3, the built SPA on S3, DynamoDB for the clip cache — as
committed CDK source with a manual, documented deploy.

**Architecture:** A CDK app in Python under a new `infra/` package (design §6) synthesising
one stack: two S3 buckets (SPA behind Origin Access Control; artifact bucket with versioning
and **no** CloudFront origin), a DynamoDB clip table, an ECR repository, an App Runner
service with two separate IAM roles, and one CloudFront distribution with two behaviours. A
single CloudFront Function on viewer-request does both the shared-password check and the SPA
fallback rewrite.

**Tech Stack:** AWS CDK v2 (Python, L1 `CfnService` for App Runner), `aws_cdk.assertions`
for template tests, Docker for the API image, uv for both Python packages.

---

## Global Constraints

Every task's requirements implicitly include this section.

- **`UV_LINK_MODE=copy` on every `uv` command.** The repo is under OneDrive; without it uv
  fails on hardlinks. This applies to the new `infra/` package exactly as to `api/` and
  `builder/`.
- **Region `us-east-1`** (`DEP-1`). The billing metric in Task 10 exists only there, which is
  a second reason not to change it.
- **No secret is ever committed.** The shared password and the origin secret are supplied at
  synth time from environment variables. A password in a CDK source file is in the
  repository's history permanently (design §2).
- **No routing, weight, graph, or cost-function change.** `pathfinding.py` is not opened.
  `api/` changes in this plan are limited to `config.py` and `app.py`, for the origin-secret
  middleware only.
- **Every new test must fail against unmodified source before its fix is written** (design
  §9, corrected by `TR-2`). A test that passes before the commit is a defect in the test.
  This project has shipped that defect twice (`FMS-P1`, `TR-2`).
- **PR-driven.** Branch off `main`, push the branch at the first commit, open a draft PR
  early. Nothing is committed to `main` directly.
- **Figures are cited, never restated.** The artifact checksum is owned by
  [`../findings/2026-07-23-tiebreak-fix-adoption.md`](../findings/2026-07-23-tiebreak-fix-adoption.md)
  and is read mechanically from `graph-t15-tiebreakfix.bin.json`.

---

## Three findings made while writing this plan

Recorded here because each changes what a faithful reading of the design would have built.

**`TKB-1` — the design's §11 puts the artifact upload in Track C, and that cannot work.**
§3's `DEP-9` calls the upload a manual prerequisite; §11's table assigns it to Track C. But
App Runner's health check target is `/health`, and `build_default_app` loads the graph at
boot — so a service deployed before the artifact is in S3 **cannot pass a health check and
the deploy rolls back**. The upload is therefore Task 6 of *this* plan, before the service
exists. Track C keeps the frontend sync and the verification list.

**`TKB-2` — `TR-5`'s prescribed fix would break every API error.** `TR-5` asks for
`errorResponses` mapping 403/404 → `/index.html` with status 200. In CloudFront, custom error
responses are a **distribution-level** property — in CDK, `errorResponses` sits on
`Distribution` props, not on `BehaviorOptions` — so it applies to the App Runner origin too.
The API's own 404 (unknown artist) and the 403 from the new origin-secret middleware would
both be rewritten to `index.html` with a 200, and the SPA would parse HTML as JSON. **This
plan implements the SPA fallback in the viewer-request function instead**, which is attached
per behaviour, and asserts in Task 9 that the distribution has **no** `CustomErrorResponses`.
`TR-5`'s *finding* stands in full; only its prescribed mechanism is replaced.

**`TKB-3` — Snyk does not scan this project's Python dependencies, and committing the
lockfile does not by itself change that.** Measured 2026-07-26: `snyk_sca_scan` against
`api/` and `builder/` both return *Could not detect supported target files*. It reads neither
`uv.lock` nor a PEP-621 `pyproject.toml`. The frontend scans fine (`package-lock.json`) and
currently reports one medium — see `TKB-11`. Task 11's runbook therefore exports a
`requirements.txt` from the lockfile at deploy time and scans that. The export is
**deliberately not committed**: it would be a second derived manifest that can drift from
`uv.lock`, and with no CI nothing would notice.

**`TKB-4` — the obvious way to run that scan reports a clean result while scanning nothing,
and this plan originally prescribed it.** Measured 2026-07-26, after the plan was written:

| how the scan was run | result | what it means |
|---|---|---|
| `command=python` (system, has pip), `skip_unresolved=true`, real export | **0 issues** | looks clean |
| same, but the export replaced by `jinja2==2.10`, `urllib3==1.24.1`, `requests==2.19.1` | **0 issues** | **vacuous** — those have well-known high-severity advisories |
| venv **with pip** and the package **installed**, no `skip_unresolved`, `jinja2==2.10` | **7 issues** | the scan is real |

Snyk's pip plugin resolves the tree from an actual environment. A uv-created venv has **no
pip** (`python -m pip` → *No module named pip*), which produces *Failed to test pip project*;
system python has pip but not the packages, which produces *Missing required packages*; and
`skip_unresolved=true` turns that second error into a **green scan of zero packages**. The
file format is irrelevant — hashes, markers and `# via` comments all scan fine.

**Consequence for Task 11:** the runbook must not use `skip_unresolved`. Either install the
export into a throwaway venv that has pip and scan that, or — better, and to be settled in
Task 3 — scan the **built image**, which already contains the installed dependency set and is
the actual release artifact. A step that cannot fail is not a gate, and this repo has now
produced that shape three times (`FMS-P1`, `TR-2`, `TKB-4`).

---

## Prerequisites — the owner runs these, not the implementing session

**None of the AWS-touching tasks (6 onward) can start until these are done.** Measured on
this machine 2026-07-26: Docker 29.5.3 ✓, Node v20.20.2 ✓, `npx cdk` 2.1133.0 ✓,
**`aws` CLI not installed ✗**, therefore no credentials configured.

- [ ] **P1 — Install the AWS CLI v2** (Windows MSI from `awscli.amazonaws.com`, or
      `winget install Amazon.AWSCLI`). Verify: `aws --version`.
- [ ] **P2 — Create an IAM identity and configure credentials.** An IAM Identity Center user
      with `AdministratorAccess` and `aws configure sso`, or an IAM user with access keys and
      `aws configure`. Region `us-east-1`. Verify: `aws sts get-caller-identity` returns an
      account id.
- [ ] **P3 — Enable billing alerts** in the account's Billing preferences. The
      `AWS/Billing EstimatedCharges` metric Task 10 alarms on does not exist until this is
      switched on, and the alarm will sit in `INSUFFICIENT_DATA` forever without it.
- [ ] **P4 — Choose two secrets and one number**, and keep them out of git:
      the shared site password, the CloudFront→App Runner origin secret (any long random
      string), and the billing alarm threshold in USD.

**These are the owner's because they are his AWS account, his credentials, his secrets and
his money.** Everything before Task 6 is AWS-free and can proceed while they are outstanding.

---

## File structure

| file | responsibility |
|---|---|
| `.gitignore` (modify) | stop ignoring `uv.lock`; start ignoring `cdk.context.json` |
| `api/uv.lock`, `builder/uv.lock` (commit existing) | the release dependency set |
| `api/src/artistpath_api/config.py` (modify) | `origin_secret` tunable |
| `api/src/artistpath_api/app.py` (modify) | origin-secret middleware |
| `api/tests/test_origin_secret.py` (create) | its tests |
| `api/Dockerfile`, `api/.dockerignore` (create) | the release artifact |
| `infra/pyproject.toml`, `infra/cdk.json`, `infra/app.py` (create) | CDK entrypoint and deploy-time inputs |
| `infra/src/artistpath_infra/stack.py` (create) | the whole stack |
| `infra/src/artistpath_infra/viewer_function.js` (create) | password check + SPA fallback |
| `infra/tests/test_stack.py` (create) | synth assertions |
| `infra/README.md` (create) | the manual deploy runbook |
| `docs/superpowers/2026-07-26-gate2-track-b-execution-log.md` (create) | the retained record |

---

## Handoff seams — chosen here, at authoring time

Thirteen tasks, past CLAUDE.md's ~8-task threshold.

- **Seam 1 — after Task 5.** Everything AWS-free is committed and green: lockfiles,
  middleware, Dockerfile, CDK source and its synth tests. Nothing is deployed and no money is
  spent. A fresh session can read the CDK source cold.
- **Seam 2 — after Task 12.** The stack is deployed and `/health` answers through CloudFront.
  Track C (cutover) starts from a working URL.
- **`DEP-33`'s review re-run is Task 11 — deliberately mid-track**, before `cdk deploy`.
  Seven of the team review's blocking findings are about a design rather than code because
  `infra/` did not exist; running the re-review after the stack is deployed means finding
  CDK-shaped defects in something already live. Same lesson `TR-1` taught at Track A's
  expense.

---

## Task 1: Commit the lockfiles

**Files:**
- Modify: `.gitignore:18`
- Commit (already on disk, currently ignored): `api/uv.lock`, `builder/uv.lock`

`DEP-32` requires `uv.lock` committed and `uv sync --frozen` in the Dockerfile, because with
no CI the image is the release artifact. `TKA-12` recorded that `.gitignore:18` makes this
unsatisfiable and that fixing it is Track B's first task. The owner accepted the residual
risk (pinned versions, nothing watching them age) on 2026-07-26.

- [ ] **Step 1: Confirm the lockfiles are ignored today**

```bash
git check-ignore -v api/uv.lock builder/uv.lock
```
Expected: two lines, both citing `.gitignore:18`. This is the "fails first" evidence.

- [ ] **Step 2: Delete the ignore rule and add the CDK context rule**

Delete line 18 of `.gitignore` (`uv.lock`) entirely. In its place put:

```gitignore
# uv.lock is COMMITTED, deliberately: with no CI the Docker image is the
# release artifact, so `uv sync --frozen` must install what the tests ran
# against (DEP-32, TKB decision 2026-07-26). Was ignored until Track B.
cdk.context.json
```

- [ ] **Step 3: Confirm they are no longer ignored**

```bash
git check-ignore -v api/uv.lock builder/uv.lock; echo "exit=$?"
```
Expected: no output, `exit=1`.

- [ ] **Step 4: Stage and verify what is being added**

```bash
git add .gitignore api/uv.lock builder/uv.lock
git status --short
```
Expected: exactly three paths. **If anything else appears, stop** — another session is live
in this tree and `git add` has swept its work in (`session-start` §C).

- [ ] **Step 5: Prove the runtime is unaffected**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q
```
Expected: 180 passed. A lockfile commit changes no behaviour; this is the regression guard.

- [ ] **Step 6: Commit**

```bash
git commit -- .gitignore api/uv.lock builder/uv.lock -m "Commit the lockfiles: the image is the release artifact (DEP-32)"
```

---

## Task 2: Reject App Runner requests that did not come through CloudFront

**Files:**
- Modify: `api/src/artistpath_api/config.py` (after the `graph_sha256` block)
- Modify: `api/src/artistpath_api/app.py` (inside `create_app`, after the CORS middleware)
- Test: `api/tests/test_origin_secret.py` (create)

**Interfaces:**
- Produces: `ApiConfig.origin_secret: str` — read by Task 8, which sets the matching
  `ARTISTPATH_ORIGIN_SECRET` environment variable on the service, and by Task 9, which
  injects the same value as the `x-origin-secret` header on both CloudFront behaviours.

`TR-7`: `DEP-8`'s claim that the API is unreachable except through CloudFront is **false**.
App Runner publishes its own public `*.awsapprunner.com` URL and has no OAC equivalent, so
the password gate protects the SPA and not the API. Both `DEP-8`'s CORS reasoning and
`DEP-17`'s cost reasoning rest on that claim.

**`/health` must be exempt.** App Runner's health checker reaches the origin directly, not
through CloudFront — `app.py:151` already carries a comment saying exactly that, which is why
`/health` is not under `/api`. A middleware that gates `/health` makes every deploy fail its
health check and roll back.

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_origin_secret.py
"""The origin secret is what stops App Runner's public URL bypassing the gate
(TR-7). Unset, everything must behave exactly as it did before it existed."""

from dataclasses import replace

from fastapi.testclient import TestClient

from artistpath_api.app import create_app


def _client(store, search, resolver, cfg, secret: str) -> TestClient:
    return TestClient(create_app(store, search, resolver, replace(cfg, origin_secret=secret)))


def test_request_without_the_header_is_refused(store, search, resolver, cfg):
    r = _client(store, search, resolver, cfg, "s3cret").get("/api/artists/search?q=a")
    assert r.status_code == 403


def test_request_with_the_wrong_header_is_refused(store, search, resolver, cfg):
    client = _client(store, search, resolver, cfg, "s3cret")
    r = client.get("/api/artists/search?q=a", headers={"x-origin-secret": "wrong"})
    assert r.status_code == 403


def test_request_with_the_right_header_is_served(store, search, resolver, cfg):
    client = _client(store, search, resolver, cfg, "s3cret")
    r = client.get("/api/artists/search?q=a", headers={"x-origin-secret": "s3cret"})
    assert r.status_code == 200


def test_health_is_exempt_because_app_runner_probes_the_origin_directly(
    store, search, resolver, cfg
):
    # App Runner's health checker does not go through CloudFront and cannot be
    # given the header. Gating /health makes every deploy roll back.
    r = _client(store, search, resolver, cfg, "s3cret").get("/health")
    assert r.status_code == 200


def test_an_empty_secret_disables_the_check_entirely(store, search, resolver, cfg):
    # Local dev and the other 180 tests construct ApiConfig with no secret set.
    r = _client(store, search, resolver, cfg, "").get("/api/artists/search?q=a")
    assert r.status_code == 200
```

**Check `api/tests/conftest.py` for the actual fixture names before writing this file.** If
the fixtures differ, use the ones `test_app.py` uses — do not invent new ones.

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_origin_secret.py
```
Expected: FAIL — `TypeError` from `replace(cfg, origin_secret=...)`, because the field does
not exist yet. That is the correct first failure.

- [ ] **Step 3: Add the config field**

```python
    # Shared secret CloudFront injects on both behaviours; requests arriving at
    # App Runner's own public URL lack it and are refused (TR-7). Empty
    # disables the check, which is local dev and the whole test suite.
    origin_secret: str = os.environ.get("ARTISTPATH_ORIGIN_SECRET", "")
```

- [ ] **Step 4: Add the middleware**

In `create_app`, immediately after the `add_middleware(CORSMiddleware, ...)` block:

```python
    if cfg.origin_secret:

        @app.middleware("http")
        async def require_origin_secret(request: Request, call_next):
            # /health is exempt: App Runner's health checker reaches the origin
            # directly, so gating it fails every deploy (see health() below).
            if request.url.path != "/health" and not hmac.compare_digest(
                request.headers.get("x-origin-secret", ""), cfg.origin_secret
            ):
                return JSONResponse({"detail": "forbidden"}, status_code=403)
            return await call_next(request)
```

Add `import hmac` to the stdlib imports and `from fastapi.responses import JSONResponse` to
the FastAPI imports.

- [ ] **Step 5: Run the tests to verify they pass**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_origin_secret.py
```
Expected: 5 passed.

- [ ] **Step 6: Run the whole suite**

```bash
cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q
```
Expected: 185 passed. Any failure here means the middleware is firing when the secret is
unset, which is the one regression this change can cause.

- [ ] **Step 7: Mutation-check the exemption**

Temporarily delete `request.url.path != "/health" and` and re-run. Expected:
`test_health_is_exempt...` FAILS. Restore it. A test that stays green under this mutation is
not holding the invariant, and this project has shipped that twice.

- [ ] **Step 8: Snyk scan the changed code, per the global instruction**

Run `snyk_code_scan` on `api/`. Fix anything it reports in the new code and rescan until
clean. `hmac.compare_digest` is used rather than `==` deliberately — do not "simplify" it.

- [ ] **Step 9: Commit**

```bash
git commit -- api/src/artistpath_api/config.py api/src/artistpath_api/app.py api/tests/test_origin_secret.py -m "Refuse API requests that did not come through CloudFront (TR-7)"
```

---

## Task 3: The API container image

**Files:**
- Create: `api/Dockerfile`, `api/.dockerignore`

**Interfaces:**
- Produces: an image exposing port 8000, entrypoint
  `uvicorn artistpath_api.app:build_default_app --factory`. Task 8 references port `8000` in
  the App Runner image configuration.

- [ ] **Step 1: Write `api/.dockerignore`**

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
tests/
scratch/
scratch_server.log
eval/
*.bin
requirements.txt
```

`requirements.txt` is listed because Task 11's runbook writes one there transiently for the
Snyk scan and it must never enter the image (`TKB-3`).

- [ ] **Step 2: Write `api/Dockerfile`**

```dockerfile
# The release artifact. With no CI (DEP-3, DEP-15) this image is what ships,
# so it installs the committed lockfile exactly rather than re-resolving
# (DEP-32). `uv sync --frozen` fails loudly if uv.lock and pyproject.toml
# disagree, which is the property being bought.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# pyproject + lock first so the dependency layer caches across source edits.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "artistpath_api.app:build_default_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Build it**

```bash
cd api && docker build -t artistpath-api:local .
```
Expected: success. If `uv sync --frozen` errors that the lockfile is out of date, **do not
pass `--no-frozen`** — regenerate with `UV_LINK_MODE=copy uv lock` on the host, re-run
Task 1's test suite, and amend Task 1's commit.

- [ ] **Step 4: Run it against the real local artifact and check identity**

```bash
docker run --rm -d --name apg -p 8001:8000 \
  -v "//c/Users/charl/OneDrive/Claude Projects/music-app/builder/scratch:/graph:ro" \
  -e ARTISTPATH_GRAPH=/graph/graph-t15-tiebreakfix.bin \
  artistpath-api:local
sleep 15 && curl -s localhost:8001/health
```
Expected: JSON with `status: ok` and a `graph_sha256`.

- [ ] **Step 5: Verify the reported identity against the sidecar, mechanically**

```bash
python -c "import json,urllib.request; \
s=json.load(open('builder/scratch/graph-t15-tiebreakfix.bin.json')); \
h=json.load(urllib.request.urlopen('http://localhost:8001/health')); \
assert h['graph_sha256']==s['sha256'], (h,s['sha256']); \
assert h['artists']==s['artists'], (h,s['artists']); \
print('identity matches the sidecar')"
docker rm -f apg
```
Expected: `identity matches the sidecar`. **Do not read the checksum with your eyes and do
not paste it anywhere** (`DEP-24`, `TR-10`): its failure signature is "refuses to boot",
during a cutover.

- [ ] **Step 6: Commit**

```bash
git commit -- api/Dockerfile api/.dockerignore -m "Add the API image, installing the frozen lockfile (DEP-32)"
```

---

## Task 4: CDK scaffolding and a synth test that fails first

**Files:**
- Create: `infra/pyproject.toml`, `infra/cdk.json`, `infra/app.py`,
  `infra/src/artistpath_infra/__init__.py`, `infra/src/artistpath_infra/stack.py`
- Test: `infra/tests/test_stack.py`

**Interfaces:**
- Produces: `ArtistpathStack(scope, id, *, deploy: DeployInputs)` and the frozen
  `DeployInputs` dataclass carrying `graph_key`, `graph_sha256`, `origin_secret`,
  `site_password`, `billing_alarm_usd`, `alarm_email`, `image_tag`. Tasks 5–10 add
  constructs to this one stack class; every later task's test imports these two names.

- [ ] **Step 1: Write `infra/pyproject.toml`**

```toml
[project]
name = "artistpath-infra"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["aws-cdk-lib>=2.180", "constructs>=10.3"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/artistpath_infra"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
```

- [ ] **Step 2: Write `infra/cdk.json`**

```json
{
  "app": "uv run python app.py",
  "watch": { "exclude": ["**/.venv/**", "**/__pycache__/**"] },
  "context": {
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "@aws-cdk/core:checkSecretUsage": true
  }
}
```

No secret goes in `context` here. Secrets arrive through the environment (Step 3).

- [ ] **Step 3: Write `infra/app.py`**

```python
"""CDK entrypoint. Deploy-time inputs come from the environment, never from
source: a password committed to a CDK file is in git history permanently
(design §2). The graph checksum comes from the artifact's manifest sidecar and
is never transcribed by hand (DEP-24, TR-10)."""

import json
import os
from pathlib import Path

import aws_cdk as cdk

from artistpath_infra.stack import ArtistpathStack, DeployInputs

_SIDECAR = Path(
    os.environ.get(
        "ARTISTPATH_DEPLOY_SIDECAR",
        "../builder/scratch/graph-t15-tiebreakfix.bin.json",
    )
)


def _require(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise SystemExit(f"{name} must be set; see infra/README.md")
    return value


def _sidecar_sha256() -> str:
    if not _SIDECAR.exists():
        raise SystemExit(
            f"{_SIDECAR} not found. The artifact and its sidecar are gitignored; "
            "deploy from a machine that has them (DEP-9)."
        )
    return json.loads(_SIDECAR.read_text())["sha256"]


app = cdk.App()
ArtistpathStack(
    app,
    "ArtistpathStack",
    deploy=DeployInputs(
        graph_key=os.environ.get("ARTISTPATH_DEPLOY_GRAPH_KEY", "graph-t15-tiebreakfix.bin"),
        graph_sha256=_sidecar_sha256(),
        origin_secret=_require("ARTISTPATH_DEPLOY_ORIGIN_SECRET"),
        site_password=_require("ARTISTPATH_DEPLOY_PASSWORD"),
        billing_alarm_usd=float(_require("ARTISTPATH_DEPLOY_BILLING_USD")),
        alarm_email=_require("ARTISTPATH_DEPLOY_ALARM_EMAIL"),
        image_tag=os.environ.get("ARTISTPATH_DEPLOY_IMAGE_TAG", "latest"),
    ),
    env=cdk.Environment(region="us-east-1"),
)
app.synth()
```

- [ ] **Step 4: Write the failing test**

```python
# infra/tests/test_stack.py
import aws_cdk as cdk
from aws_cdk.assertions import Template

from artistpath_infra.stack import ArtistpathStack, DeployInputs

DEPLOY = DeployInputs(
    graph_key="graph-test.bin",
    graph_sha256="0" * 64,
    origin_secret="test-origin-secret",
    site_password="test-password",
    billing_alarm_usd=25.0,
    alarm_email="nobody@example.com",
    image_tag="test",
)


def template() -> Template:
    app = cdk.App()
    stack = ArtistpathStack(app, "Test", deploy=DEPLOY, env=cdk.Environment(region="us-east-1"))
    return Template.from_stack(stack)


def test_the_stack_synthesises():
    assert template().to_json()["Resources"]
```

- [ ] **Step 5: Run it to verify it fails**

```bash
cd infra && UV_LINK_MODE=copy uv run --extra dev pytest -q
```
Expected: FAIL — `ModuleNotFoundError: artistpath_infra.stack`.

- [ ] **Step 6: Write the minimal stack**

```python
# infra/src/artistpath_infra/stack.py
"""One stack: SPA bucket, artifact bucket, clip table, ECR, App Runner,
CloudFront. Constructs are added task by task; see
docs/superpowers/plans/2026-07-26-track-b-infrastructure.md."""

from __future__ import annotations

from dataclasses import dataclass

import aws_cdk as cdk
from constructs import Construct


@dataclass(frozen=True)
class DeployInputs:
    graph_key: str
    graph_sha256: str
    origin_secret: str
    site_password: str
    billing_alarm_usd: float
    alarm_email: str
    image_tag: str


class ArtistpathStack(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, *, deploy: DeployInputs, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)
        self.deploy = deploy
```

`infra/src/artistpath_infra/__init__.py` is empty.

- [ ] **Step 7: Run it to verify it passes**

```bash
cd infra && UV_LINK_MODE=copy uv sync --extra dev && UV_LINK_MODE=copy uv run --extra dev pytest -q
```
Expected: FAIL still — `to_json()["Resources"]` is empty on a stack with no resources.
**That is correct and is the point**: the assertion holds a real property. Leave it failing
and let Task 5 turn it green; do not add a dummy resource to make it pass now.

- [ ] **Step 8: Commit**

```bash
git add infra/ && git commit -- infra/ -m "Scaffold the CDK app (design §6)"
```

---

## Task 5: Storage — two buckets and the clip table

**Files:**
- Modify: `infra/src/artistpath_infra/stack.py`
- Test: `infra/tests/test_stack.py`

**Interfaces:**
- Produces: `self.spa_bucket`, `self.artifact_bucket`, `self.clip_table` on the stack. Task 8
  grants the instance role read on `artifact_bucket` at one key and read/write on
  `clip_table`; Task 9 gives `spa_bucket` an OAC origin.

`TR-7`: **two buckets, not one.** The artifact bucket gets **no CloudFront origin at all**,
or the graph becomes a 14 MB download to anyone who guesses a filename printed in several
committed documents. `TR-9`: the adopted artifact is a single copy that `acceptance.py`
deliberately refuses to rebuild, so the artifact bucket is **versioned** and the upload
becomes its second copy.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_artifact_bucket_is_versioned_because_it_is_the_only_second_copy():
    template().has_resource_properties(
        "AWS::S3::Bucket",
        {"VersioningConfiguration": {"Status": "Enabled"}},
    )


def test_both_buckets_block_all_public_access():
    buckets = template().find_resources("AWS::S3::Bucket")
    assert len(buckets) == 2
    for bucket in buckets.values():
        assert bucket["Properties"]["PublicAccessBlockConfiguration"] == {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True,
        }


def test_the_clip_table_matches_what_DynamoClipCache_writes():
    # clips.py writes Item={"mbid": ..., "ttl": ...}; a mismatch here is a
    # runtime error no test in api/ can catch.
    template().has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [{"AttributeName": "mbid", "KeyType": "HASH"}],
            "TimeToLiveSpecification": {"AttributeName": "ttl", "Enabled": True},
            "BillingMode": "PAY_PER_REQUEST",
        },
    )
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd infra && UV_LINK_MODE=copy uv run --extra dev pytest -q
```
Expected: FAIL — no `AWS::S3::Bucket` in the template.

- [ ] **Step 3: Implement**

Add to `__init__`, after `self.deploy = deploy`:

```python
        self.spa_bucket = s3.Bucket(
            self,
            "SpaBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # No CloudFront origin, ever: the graph is a 14 MB file whose name is
        # printed in several committed documents (TR-7). Versioned because
        # acceptance.py refuses to rebuild the adopted artifact, so the only
        # other copy is gitignored on one OneDrive-synced machine (TR-9).
        self.artifact_bucket = s3.Bucket(
            self,
            "ArtifactBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # Key and TTL attribute names are fixed by clips.py's DynamoClipCache.
        self.clip_table = dynamodb.Table(
            self,
            "ClipTable",
            table_name="artistpath-clips",
            partition_key=dynamodb.Attribute(
                name="mbid", type=dynamodb.AttributeType.STRING
            ),
            time_to_live_attribute="ttl",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )
```

Imports: `from aws_cdk import aws_s3 as s3, aws_dynamodb as dynamodb`.

The table name is hardcoded to match `ApiConfig.clip_table_name`'s default
(`artistpath-clips`), so the service needs no override for it to work.

- [ ] **Step 4: Run to verify they pass**

Expected: 4 passed (including `test_the_stack_synthesises` from Task 4, now green).

- [ ] **Step 5: Commit**

```bash
git commit -- infra/ -m "Add the two buckets and the clip table (TR-7, TR-9)"
```

---

## Task 6: Upload the artifact and its sidecar — owner-run, and it must precede the service

**Files:** none. This is an operational step, recorded as a task because `DEP-9` says a plan
must name it rather than assume it, and `TKB-1` says it cannot wait for Track C.

**Requires P1–P2.**

- [ ] **Step 1: Create the bucket by deploying only storage**

```bash
cd infra
export ARTISTPATH_DEPLOY_ORIGIN_SECRET=... ARTISTPATH_DEPLOY_PASSWORD=... \
       ARTISTPATH_DEPLOY_BILLING_USD=... ARTISTPATH_DEPLOY_ALARM_EMAIL=...
UV_LINK_MODE=copy npx cdk bootstrap aws://<account-id>/us-east-1
UV_LINK_MODE=copy npx cdk deploy ArtistpathStack
```
At this point the stack contains only buckets and a table — pennies per month, and no App
Runner instance is running yet.

- [ ] **Step 2: Upload the artifact and the sidecar together**

```bash
BUCKET=$(aws cloudformation describe-stacks --stack-name ArtistpathStack \
  --query "Stacks[0].Outputs[?OutputKey=='ArtifactBucketName'].OutputValue" --output text)
aws s3 cp builder/scratch/graph-t15-tiebreakfix.bin      "s3://$BUCKET/graph-t15-tiebreakfix.bin"
aws s3 cp builder/scratch/graph-t15-tiebreakfix.bin.json "s3://$BUCKET/graph-t15-tiebreakfix.bin.json"
```

The sidecar goes up too (`TR-10`): it is what makes *which graph is live* answerable without
transcribing a hash. Task 9 adds the `ArtifactBucketName` output — until then, read the name
from the CloudFormation console.

- [ ] **Step 3: Verify the upload byte-for-byte**

```bash
aws s3api head-object --bucket "$BUCKET" --key graph-t15-tiebreakfix.bin \
  --checksum-mode ENABLED --query ContentLength
python -c "import pathlib; print(pathlib.Path('builder/scratch/graph-t15-tiebreakfix.bin').stat().st_size)"
```
Expected: the two numbers are equal, and both equal the sidecar's `bytes` field. A partial
upload presents at boot as a checksum mismatch and a service that will not start.

---

## Task 7: ECR repository

**Files:**
- Modify: `infra/src/artistpath_infra/stack.py`
- Test: `infra/tests/test_stack.py`

**Interfaces:**
- Produces: `self.repo` (`ecr.Repository`). Task 8 references `self.repo.repository_uri` in
  the App Runner image identifier and grants the access role pull rights.

- [ ] **Step 1: Write the failing test**

```python
def test_the_image_repository_scans_on_push_and_keeps_history_bounded():
    template().has_resource_properties(
        "AWS::ECR::Repository",
        {
            "RepositoryName": "artistpath-api",
            "ImageScanningConfiguration": {"ScanOnPush": True},
        },
    )
```

- [ ] **Step 2: Run to verify it fails.** Expected: no `AWS::ECR::Repository`.

- [ ] **Step 3: Implement**

```python
        self.repo = ecr.Repository(
            self,
            "ApiRepo",
            repository_name="artistpath-api",
            image_scan_on_push=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            lifecycle_rules=[ecr.LifecycleRule(max_image_count=5)],
        )
```

Import `aws_ecr as ecr`. Scan-on-push is ECR's own image scanning and is the only automated
dependency check in the deployed path — `TKB-3` records that Snyk does not read `uv.lock`.

- [ ] **Step 4: Run to verify it passes. Step 5: Commit**

```bash
git commit -- infra/ -m "Add the ECR repository"
```

---

## Task 8: App Runner service, with two roles and the right environment

**Files:**
- Modify: `infra/src/artistpath_infra/stack.py`
- Test: `infra/tests/test_stack.py`

**Interfaces:**
- Produces: `self.service` (`apprunner.CfnService`). Task 9 uses
  `self.service.attr_service_url` as the `/api/*` origin.

Three findings bind this task. `TR-8`: **`ARTISTPATH_CORS_ORIGINS` must be set to the empty
string** — leaving it unset yields the dev default `http://localhost:5173`
(`config.py:65-73`), and because same-origin means no preflight ever fires, nothing would
reveal the mistake. `TR-7`: App Runner needs **two** roles — an access role for the ECR pull
(`build.apprunner.amazonaws.com`) and an instance role for runtime
(`tasks.apprunner.amazonaws.com`) — and the instance role is scoped to the single artifact
key and the one table. `TKA-11`: the checksum gate ships off by default and closes only when
the stack is shown in source to set `ARTISTPATH_GRAPH_SHA256` from the sidecar — which
`app.py` (Task 4) does.

**The L1 `CfnService` is used deliberately** rather than `aws_apprunner_alpha`: the alpha
module is a second versioned dependency that must track `aws-cdk-lib`, and this stack needs
five of its properties.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_service_gets_every_environment_variable_the_api_reads():
    env = template().find_resources("AWS::AppRunner::Service")
    (service,) = env.values()
    pairs = service["Properties"]["SourceConfiguration"]["ImageRepository"][
        "ImageConfiguration"
    ]["RuntimeEnvironmentVariables"]
    got = {p["Name"]: p["Value"] for p in pairs}
    assert got["ARTISTPATH_GRAPH_SHA256"] == "0" * 64
    assert got["ARTISTPATH_CLIP_CACHE"] == "dynamo"
    assert got["ARTISTPATH_ORIGIN_SECRET"] == "test-origin-secret"
    assert "graph-test.bin" in str(got["ARTISTPATH_GRAPH"])
    # TR-8: unset yields the dev default http://localhost:5173. It must be
    # present AND empty, and no preflight will ever fire to tell us otherwise.
    assert "ARTISTPATH_CORS_ORIGINS" in got
    assert got["ARTISTPATH_CORS_ORIGINS"] == ""


def test_the_health_check_targets_health_not_the_root():
    template().has_resource_properties(
        "AWS::AppRunner::Service",
        {"HealthCheckConfiguration": {"Protocol": "HTTP", "Path": "/health"}},
    )


def test_the_instance_role_cannot_read_the_whole_artifact_bucket():
    policies = template().find_resources("AWS::IAM::Policy")
    statements = [
        s
        for p in policies.values()
        for s in p["Properties"]["PolicyDocument"]["Statement"]
    ]
    s3_reads = [s for s in statements if "s3:GetObject" in str(s["Action"])]
    assert s3_reads, "no s3 read grant found"
    for statement in s3_reads:
        assert "graph-test.bin" in str(statement["Resource"]), statement


def test_the_two_app_runner_roles_are_not_merged():
    roles = template().find_resources("AWS::IAM::Role")
    principals = {
        s["Principal"]["Service"]
        for r in roles.values()
        for s in r["Properties"]["AssumeRolePolicyDocument"]["Statement"]
    }
    assert "build.apprunner.amazonaws.com" in str(principals)
    assert "tasks.apprunner.amazonaws.com" in str(principals)
```

- [ ] **Step 2: Run to verify they fail.** Expected: no `AWS::AppRunner::Service`.

- [ ] **Step 3: Implement**

```python
        # Two roles, deliberately not merged (TR-7): the access role pulls the
        # image, the instance role is what the running container gets.
        access_role = iam.Role(
            self,
            "ApiAccessRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSAppRunnerServicePolicyForECRAccess"
                )
            ],
        )
        instance_role = iam.Role(
            self,
            "ApiInstanceRole",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
        )
        # Scoped to the one key, not the bucket.
        self.artifact_bucket.grant_read(instance_role, deploy.graph_key)
        self.clip_table.grant(instance_role, "dynamodb:GetItem", "dynamodb:PutItem")

        graph_uri = f"s3://{self.artifact_bucket.bucket_name}/{deploy.graph_key}"

        def _env(name: str, value: str):
            return apprunner.CfnService.KeyValuePairProperty(name=name, value=value)

        self.service = apprunner.CfnService(
            self,
            "ApiService",
            service_name="artistpath-api",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                auto_deployments_enabled=False,
                authentication_configuration=(
                    apprunner.CfnService.AuthenticationConfigurationProperty(
                        access_role_arn=access_role.role_arn
                    )
                ),
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=f"{self.repo.repository_uri}:{deploy.image_tag}",
                    image_repository_type="ECR",
                    image_configuration=(
                        apprunner.CfnService.ImageConfigurationProperty(
                            port="8000",
                            runtime_environment_variables=[
                                _env("ARTISTPATH_GRAPH", graph_uri),
                                _env("ARTISTPATH_GRAPH_SHA256", deploy.graph_sha256),
                                _env("ARTISTPATH_CLIP_CACHE", "dynamo"),
                                _env("ARTISTPATH_ORIGIN_SECRET", deploy.origin_secret),
                                # Present and EMPTY. Unset means the dev default
                                # http://localhost:5173 (TR-8), and same-origin
                                # means no preflight ever fires to reveal it.
                                _env("ARTISTPATH_CORS_ORIGINS", ""),
                            ],
                        )
                    ),
                ),
            ),
            instance_configuration=(
                apprunner.CfnService.InstanceConfigurationProperty(
                    # The dominant cost line (DEP-17, unmeasured). This is the
                    # first knob to turn down if the billing alarm fires.
                    cpu="1 vCPU",
                    memory="2 GB",
                    instance_role_arn=instance_role.role_arn,
                )
            ),
            health_check_configuration=(
                apprunner.CfnService.HealthCheckConfigurationProperty(
                    protocol="HTTP",
                    path="/health",
                    interval=10,
                    timeout=5,
                    healthy_threshold=1,
                    unhealthy_threshold=5,
                )
            ),
        )
        self.service.node.add_dependency(instance_role)
```

Import `aws_iam as iam, aws_apprunner as apprunner`.

- [ ] **Step 4: Run to verify they pass.**

If `test_the_instance_role_cannot_read_the_whole_artifact_bucket` fails with a `Resource`
ending in `/*`, the `grant_read` object-key argument was dropped — fix that rather than
loosening the test.

- [ ] **Step 5: Commit**

```bash
git commit -- infra/ -m "Add the App Runner service, two roles, and an empty CORS origin (TR-7, TR-8)"
```

---

## Task 9: CloudFront — one distribution, two behaviours, one viewer function

**Files:**
- Create: `infra/src/artistpath_infra/viewer_function.js`
- Modify: `infra/src/artistpath_infra/stack.py`
- Test: `infra/tests/test_stack.py`

This task carries `TR-5`, `TR-6`, the password gate (`DEP-4`) and the origin-secret injection
(`TR-7`), plus `TKB-2` — the reason the SPA fallback is in the function rather than in
`errorResponses`.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_api_behaviour_disables_caching_or_C2_comes_back():
    # CloudFront's default would cache the freshly re-signed clip URL and
    # resurrect "clips die after a while", closed 2026-07-25 (TR-6).
    CACHING_DISABLED = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    (dist,) = template().find_resources("AWS::CloudFront::Distribution").values()
    (api_behaviour,) = dist["Properties"]["DistributionConfig"]["CacheBehaviors"]
    assert api_behaviour["PathPattern"] == "/api/*"
    assert api_behaviour["CachePolicyId"] == CACHING_DISABLED
    assert "POST" in api_behaviour["AllowedMethods"]


def test_the_api_behaviour_forwards_the_query_string_and_the_journey_header():
    (dist,) = template().find_resources("AWS::CloudFront::Distribution").values()
    (policy,) = template().find_resources("AWS::CloudFront::OriginRequestPolicy").values()
    config = policy["Properties"]["OriginRequestPolicyConfig"]
    # Without this every search returns whatever `q` was cached first (TR-6).
    assert config["QueryStringsConfig"]["QueryStringBehavior"] == "all"
    headers = str(config["HeadersConfig"]).lower()
    assert "x-journey-id" in headers  # DEP-6; CloudFront strips unlisted headers


def test_the_distribution_has_no_custom_error_responses():
    # TKB-2: errorResponses is distribution-level, so mapping 403/404 to
    # index.html would rewrite the API's own 404 and the origin-secret 403
    # into an HTML page with status 200. The SPA fallback lives in the
    # viewer function instead, which is per-behaviour.
    (dist,) = template().find_resources("AWS::CloudFront::Distribution").values()
    assert "CustomErrorResponses" not in dist["Properties"]["DistributionConfig"]


def test_the_viewer_function_gates_on_the_password_and_rewrites_spa_routes():
    (fn,) = template().find_resources("AWS::CloudFront::Function").values()
    code = fn["Properties"]["FunctionCode"]
    assert "authorization" in code
    assert "/index.html" in code
    assert "401" in code


def test_the_api_origin_carries_the_shared_secret_header():
    (dist,) = template().find_resources("AWS::CloudFront::Distribution").values()
    origins = dist["Properties"]["DistributionConfig"]["Origins"]
    custom = [o for o in origins if "CustomOriginConfig" in o]
    assert custom, "no App Runner origin found"
    headers = {
        h["HeaderName"].lower(): h["HeaderValue"]
        for o in custom
        for h in o.get("OriginCustomHeaders", [])
    }
    assert headers.get("x-origin-secret") == "test-origin-secret"


def test_the_artifact_bucket_is_not_an_origin():
    (dist,) = template().find_resources("AWS::CloudFront::Distribution").values()
    origins = str(dist["Properties"]["DistributionConfig"]["Origins"])
    assert "ArtifactBucket" not in origins  # TR-7
```

- [ ] **Step 2: Run to verify they fail.** Expected: no `AWS::CloudFront::Distribution`.

- [ ] **Step 3: Write the viewer function**

```javascript
// infra/src/artistpath_infra/viewer_function.js
//
// Two jobs on one viewer-request function.
//
// 1. The shared-password gate (DEP-4). This is a shared secret in a function
//    body, not authentication: no per-user identity, secures nothing. Its
//    purpose is narrow — every card view fires an unrate-limited clip lookup
//    against Deezer/iTunes, and a rate-limited catalogue presents as silent
//    cards, visually identical to the C1 defect closed on 2026-07-25.
// 2. The SPA fallback (TR-5). It lives here rather than in errorResponses
//    because those are distribution-level and would rewrite the API's own
//    404s and 403s into an HTML page with status 200 (TKB-2).
//
// __EXPECTED_AUTH__ is substituted at synth time. It is never in git.
function handler(event) {
  var request = event.request;
  var headers = request.headers;

  if (!headers.authorization || headers.authorization.value !== '__EXPECTED_AUTH__') {
    return {
      statusCode: 401,
      statusDescription: 'Unauthorized',
      headers: {
        'www-authenticate': { value: 'Basic realm="artistpath"' },
      },
    };
  }

  // Anything that is not an API call and has no file extension is an SPA
  // route: /path/<mbid>/<mbid> holds no object in S3 and would 403.
  var uri = request.uri;
  if (uri.indexOf('/api/') !== 0 && uri.lastIndexOf('.') <= uri.lastIndexOf('/')) {
    request.uri = '/index.html';
  }
  return request;
}
```

- [ ] **Step 4: Implement the distribution**

```python
        expected_auth = "Basic " + base64.b64encode(
            f"artistpath:{deploy.site_password}".encode()
        ).decode()
        function_code = (
            (Path(__file__).parent / "viewer_function.js")
            .read_text()
            .replace("__EXPECTED_AUTH__", expected_auth)
        )
        viewer_fn = cloudfront.Function(
            self,
            "ViewerFunction",
            code=cloudfront.FunctionCode.from_inline(function_code),
            runtime=cloudfront.FunctionRuntime.JS_2_0,
        )
        fn_association = [
            cloudfront.FunctionAssociation(
                function=viewer_fn,
                event_type=cloudfront.FunctionEventType.VIEWER_REQUEST,
            )
        ]

        api_origin = origins.HttpOrigin(
            self.service.attr_service_url,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
            # The half of TR-7 that stops App Runner's own public URL being a
            # way round the gate. Paired with the middleware in api/app.py.
            custom_headers={"x-origin-secret": deploy.origin_secret},
        )

        self.distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(self.spa_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                function_associations=fn_association,
            ),
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=api_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    # Caching a re-signed clip URL resurrects C2 (TR-6).
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy(
                        self,
                        "ApiOriginRequestPolicy",
                        query_string_behavior=cloudfront.OriginRequestQueryStringBehavior.all(),
                        header_behavior=cloudfront.OriginRequestHeaderBehavior.allow_list(
                            "x-journey-id", "content-type"
                        ),
                        cookie_behavior=cloudfront.OriginRequestCookieBehavior.none(),
                    ),
                    function_associations=fn_association,
                ),
            },
            default_root_object="index.html",
            # NO error_responses: see TKB-2.
        )

        cdk.CfnOutput(self, "SiteUrl", value=f"https://{self.distribution.domain_name}")
        cdk.CfnOutput(self, "ArtifactBucketName", value=self.artifact_bucket.bucket_name)
        cdk.CfnOutput(self, "SpaBucketName", value=self.spa_bucket.bucket_name)
        cdk.CfnOutput(self, "EcrRepositoryUri", value=self.repo.repository_uri)
        cdk.CfnOutput(self, "DistributionId", value=self.distribution.distribution_id)
```

Imports: `base64`, `from pathlib import Path`,
`from aws_cdk import aws_cloudfront as cloudfront, aws_cloudfront_origins as origins`.

**The `Authorization` header is not in the `/api/*` allow-list on purpose.** The browser
attaches it to same-origin `fetch` calls, the viewer function checks it at the edge, and it
has no business reaching the API.

- [ ] **Step 5: Run to verify they pass.**

- [ ] **Step 6: Confirm the secret is not in the repository**

```bash
git grep -n "$ARTISTPATH_DEPLOY_PASSWORD" -- . ; echo "exit=$? (1 means absent)"
```
Expected: `exit=1`. The password reaches the template through the environment only; the
synthesised `cdk.out/` is gitignored (`.gitignore:8`).

- [ ] **Step 7: Commit**

```bash
git commit -- infra/ -m "Add the distribution, the viewer gate and the SPA fallback (TR-5, TR-6, TKB-2)"
```

---

## Task 10: The billing alarm

**Files:**
- Modify: `infra/src/artistpath_infra/stack.py`
- Test: `infra/tests/test_stack.py`

`DEP-31`, the owner's decision: `DEP-17`'s success condition is "observe a month of billing",
and an alarm is how you observe without remembering to look. **Requires P3** — the metric
does not exist until billing alerts are enabled.

- [ ] **Step 1: Write the failing test**

```python
def test_the_billing_alarm_uses_the_threshold_it_was_given():
    template().has_resource_properties(
        "AWS::CloudWatch::Alarm",
        {
            "MetricName": "EstimatedCharges",
            "Namespace": "AWS/Billing",
            "Threshold": 25.0,
            "ComparisonOperator": "GreaterThanThreshold",
        },
    )
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Implement**

```python
        topic = sns.Topic(self, "AlarmTopic")
        topic.add_subscription(sns_subscriptions.EmailSubscription(deploy.alarm_email))
        # AWS/Billing is published only in us-east-1, and only once billing
        # alerts are enabled in account preferences (prerequisite P3).
        cloudwatch.Alarm(
            self,
            "BillingAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Billing",
                metric_name="EstimatedCharges",
                dimensions_map={"Currency": "USD"},
                statistic="Maximum",
                period=cdk.Duration.hours(6),
            ),
            threshold=deploy.billing_alarm_usd,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        ).add_alarm_action(cloudwatch_actions.SnsAction(topic))
```

Imports: `aws_sns as sns, aws_sns_subscriptions as sns_subscriptions,
aws_cloudwatch as cloudwatch, aws_cloudwatch_actions as cloudwatch_actions`.

- [ ] **Step 4: Run to verify it passes. Step 5: Commit**

```bash
git commit -- infra/ -m "Add the billing alarm (DEP-31)"
```

---

## Task 11: The deploy runbook

**Files:**
- Create: `infra/README.md`

Deploys are manual and documented (design §6). This file is the whole operational surface;
if it is wrong, the deploy is wrong.

- [ ] **Step 1: Write `infra/README.md`** covering, in order:

1. **Prerequisites** — P1–P4 above, and the note that the artifact and sidecar are gitignored
   so deploys happen from a machine that has them (`DEP-9`).
2. **Environment variables** — the five `ARTISTPATH_DEPLOY_*` names from Task 4's `app.py`,
   with the warning that the password and origin secret must never be committed and that
   `UV_LINK_MODE=copy` prefixes every `uv` command.
3. **Build and push the image:**

```bash
cd api && docker build -t artistpath-api:$(git rev-parse --short HEAD) .
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag  artistpath-api:$(git rev-parse --short HEAD) <repo-uri>:$(git rev-parse --short HEAD)
docker push <repo-uri>:$(git rev-parse --short HEAD)
export ARTISTPATH_DEPLOY_IMAGE_TAG=$(git rev-parse --short HEAD)
```

   Tag by commit, not `latest`: with no CI, the tag is the only record of what is running.
4. **`cdk deploy`**, and how to read the outputs.
5. **Frontend build and sync** (Track C executes this; documented here because it belongs to
   the runbook):

```bash
cd frontend && npm run build
aws s3 sync dist/ "s3://<spa-bucket>/" --delete
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```
6. **Mandatory manual gates before calling a deploy done** — there is no CI, so these are the
   regression gate:
   - `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q`
   - `cd frontend && npm test && npm run build`
   - `cd frontend && npm run test:e2e` — **`DEP-30` makes this mandatory.** It needs the API
     on `:8000` and starts only the Vite server itself.
   - **Dependency scan** (`TKB-3`), including the reason it looks roundabout:

```bash
# Snyk reads neither uv.lock nor a PEP-621 pyproject.toml — measured
# 2026-07-26, both api/ and builder/ return "no supported target files".
# The export is deliberately NOT committed: a second derived manifest can
# drift from uv.lock, and with no CI nothing would notice.
cd api && UV_LINK_MODE=copy uv export --frozen --no-dev --no-emit-project \
  --format requirements-txt > requirements.txt
# then run snyk_code_scan / snyk SCA against api/requirements.txt
rm requirements.txt
cd ../frontend && npx snyk test   # reads package-lock.json directly
```
7. **Rollback** — redeploy the previous image tag; the artifact bucket is versioned
   (`TR-9`), so a bad graph upload is recoverable by version id.

- [ ] **Step 2: Verify every command in it resolves**

Run each read-only command (`aws --version`, `docker --version`, the `uv export`, the test
suites). Anything that does not resolve is either not-yet-built — say so in the file — or
stale. CLAUDE.md's rule about grepping everything a plan names applies to runbooks with
more force, because a runbook is read under time pressure during a cutover.

- [ ] **Step 3: Commit**

```bash
git commit -- infra/README.md -m "Add the deploy runbook, with the manual gates that stand in for CI"
```

**This is seam 1.** Everything above is committed, green, and cost nothing. If the session is
long by here, retire it: the CDK source and this runbook are readable cold.

---

## Task 12: `DEP-33` — re-run the team review against the CDK stack

**Files:**
- Create: `docs/superpowers/findings/2026-07-26-track-b-cdk-review.md`

**Deliberately before `cdk deploy`, not after** (`TKB-` seam note). Seven of the original
review's blocking findings concern a design rather than code, because `infra/` did not exist;
`DEP-33` requires the re-run before cutover, and doing it after the stack is live means
finding CDK-shaped defects in something already running and already costing money.

- [ ] **Step 1: Recommend the review to the owner and wait.** Reviews are never automatic
      here. `DEP-33` makes this one scheduled rather than discretionary, but the owner still
      decides when it runs. Name what it would change: whether the stack deploys as-is.
- [ ] **Step 2: Staff it as the original was** — architect, security, quality, frontend; the
      graph analyst **not** staffed, since no scoring question is open. Scope: `infra/`,
      `api/Dockerfile`, and the origin-secret middleware.
- [ ] **Step 3: Record findings with fresh identifiers** in the findings file, and triage
      into blocking / cheap / deferred as the original did.
- [ ] **Step 4: Fix everything blocking before Task 13.** Anything deferred gets a success
      condition, per `closeout`'s deferral rule.

---

## Task 13: Deploy, and verify identity end to end

**Requires P1–P4 and Task 6. This is where the money starts.** App Runner bills for a warm
instance continuously from here (`DEP-17`, unmeasured).

- [ ] **Step 1: Deploy**

```bash
cd infra && UV_LINK_MODE=copy npx cdk deploy ArtistpathStack
```
Expected: `CREATE_COMPLETE`, and the five outputs from Task 9.

- [ ] **Step 2: Confirm the service reached the graph**

```bash
aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='artistpath-api']"
```
Expected: `RUNNING`. If it is `CREATE_FAILED`, read the App Runner application logs in
CloudWatch before changing anything: the two likely causes are a checksum mismatch (the
upload in Task 6 was partial) and a missing artifact key, and both say so explicitly.

- [ ] **Step 3: `/health` through CloudFront reports the artifact the sidecar names**

```bash
SITE=$(aws cloudformation describe-stacks --stack-name ArtistpathStack \
  --query "Stacks[0].Outputs[?OutputKey=='SiteUrl'].OutputValue" --output text)
curl -s -u "artistpath:$ARTISTPATH_DEPLOY_PASSWORD" "$SITE/api/../health" -o /dev/null -w "%{http_code}\n"
curl -s -u "artistpath:$ARTISTPATH_DEPLOY_PASSWORD" "https://<app-runner-url>/health"
```

`/health` is deliberately not under `/api`, so it is served by the default behaviour and the
SPA-fallback rule leaves it alone (it has no extension — **verify this**; if the function
rewrites `/health` to `/index.html`, add `/health` to the same exemption the `/api/` prefix
gets, and add a test for it in Task 9).

- [ ] **Step 4: Verify identity against the sidecar mechanically, as in Task 3 Step 5.**
      Same script, pointed at the deployed URL. This is design §9's `/health` check and
      closes `TKA-11`.

- [ ] **Step 5: Confirm the gate actually gates**

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/"                     # expect 401
curl -s -o /dev/null -w "%{http_code}\n" "https://<app-runner-url>/api/artists/search?q=a"  # expect 403
```
The second is `TR-7`'s whole point: App Runner's public URL must refuse a request that did
not come through CloudFront.

- [ ] **Step 6: Record the deployed identity** in the execution log — image tag, graph key,
      stack outputs. Not the password, not the origin secret.

**This is seam 2.** Track C (cutover: frontend sync, design §9's remaining verification list,
the use-the-app queue entry) starts here.

---

## Carried items and what closes them

| item | condition to close |
|---|---|
| `TKA-11` — checksum gate ships off by default | Task 13 Step 4: `/health` on the deployed service reports the sidecar's sha256 |
| `TKA-12` / `DEP-32` — lockfile ignored | Task 1 |
| `DEP-33` — review is design-only | Task 12 |
| `DEP-9` — artifact upload is manual | Task 6; recurs at every graph change |
| `DEP-17` — cost unmeasured | One month of real billing observed; Task 10 is what makes that observable |
| `DEP-16` — prod/analysis routing identity | **Not this track.** The telemetry round-trip, Track C or later |
| `DEP-15` — no regression gate | Roadmap Phase 4, or a regression reaches a user |
| `TKB-3` — no automatic Python dependency scanning | CI exists (roadmap Phase 4), or Snyk gains `uv.lock` support |
| `TKB-11` — `react-router` 7.18.1 CSRF (medium, transitive, fixed in 8.3.0) | **Deferred to Gate 3 by owner decision, 2026-07-26.** A major-version bump touching the routing Track D just changed, against an app with no auth, no cookies and no state-changing requests. Closes when the bump lands, or when a measurement shows the advisory's attack path exists here |

---

## Self-review

**Spec coverage.** Design §2 → Tasks 8, 9 (topology, both `DEP-8` corrections, the password
gate, `/health` reachability). §3 → Tasks 6, 8 (`s3://` URI, checksum from sidecar,
`DEP-9`). §4 → **Track A, already merged**; nothing here re-does it. §5 → Track A. §6 →
Tasks 3, 11 (`infra/` package, three-step manual deploy, `UV_LINK_MODE=copy`). §9 → Tasks 3,
13 (`/health` identity; the path-parity and telemetry round-trip checks are Track C's, and
are named as such). §10 → the carried-items table. §11 → the seam notes. §12 amendments:
`DEP-21`–`DEP-24` → Tasks 6, 8, 9; `DEP-31` → Task 10; `DEP-32` → Tasks 1, 3; `DEP-33` →
Task 12. `DEP-19`, `DEP-20`, `DEP-25`–`DEP-30` are Track A's or Track D's and are merged.

**Gaps I am leaving deliberately, and why.** The frontend S3 sync is documented in Task 11's
runbook but executed in Track C, per design §11 — the plan names it rather than assuming it.
`DEP-16`'s telemetry round-trip needs real logged traffic, which does not exist until people
use the deployed app.

**Type consistency.** `DeployInputs` fields are used verbatim in Tasks 4, 8, 9, 10.
`self.spa_bucket`, `self.artifact_bucket`, `self.clip_table`, `self.repo`, `self.service`,
`self.distribution` are defined in Tasks 5, 7, 8, 9 and consumed only after definition.
`ApiConfig.origin_secret` (Task 2) matches `ARTISTPATH_ORIGIN_SECRET` (Task 8) and the
`x-origin-secret` header (Task 9). The DynamoDB key `mbid` and TTL attribute `ttl` (Task 5)
match `clips.py`'s `_put_sync`. Port `8000` matches the Dockerfile's `EXPOSE`.
