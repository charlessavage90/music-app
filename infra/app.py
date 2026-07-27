"""CDK entrypoint.

Deploy-time inputs come from the environment, never from source: a password
committed to a CDK file is in the repository's history permanently (design §2).
The graph checksum comes from the artifact's manifest sidecar and is never
transcribed by hand (DEP-24, TR-10) — its failure signature is "refuses to
boot", during a cutover.
"""

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
# `cdk deploy -c stage=storage` builds only what the image push and the
# artifact upload need. The first deploy must use it: App Runner cannot be
# created before the image is in ECR and the graph is in S3 (TKB-7).
include_service = app.node.try_get_context("stage") != "storage"
ArtistpathStack(
    app,
    "ArtistpathStack",
    deploy=DeployInputs(
        graph_key=os.environ.get(
            "ARTISTPATH_DEPLOY_GRAPH_KEY", "graph-t15-tiebreakfix.bin"
        ),
        graph_sha256=_sidecar_sha256(),
        origin_secret=_require("ARTISTPATH_DEPLOY_ORIGIN_SECRET"),
        site_password=_require("ARTISTPATH_DEPLOY_PASSWORD"),
        billing_alarm_usd=float(_require("ARTISTPATH_DEPLOY_BILLING_USD")),
        alarm_email=_require("ARTISTPATH_DEPLOY_ALARM_EMAIL"),
        image_tag=os.environ.get("ARTISTPATH_DEPLOY_IMAGE_TAG", "latest"),
        include_service=include_service,
    ),
    env=cdk.Environment(region="us-east-1"),
)
app.synth()
