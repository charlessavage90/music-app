"""One stack: SPA bucket, artifact bucket, clip table, ECR, App Runner,
CloudFront, billing alarm.

Constructs are added task by task; see
docs/superpowers/plans/2026-07-26-track-b-infrastructure.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import aws_cdk as cdk
from constructs import Construct


@dataclass(frozen=True)
class DeployInputs:
    """Everything that varies per deploy, and nothing that does not.

    Secrets live here rather than in source: app.py reads them from the
    environment, so nothing in this repository ever holds one (design §2).
    """

    graph_key: str
    graph_sha256: str
    origin_secret: str
    site_password: str
    billing_alarm_usd: float
    alarm_email: str
    image_tag: str


class ArtistpathStack(cdk.Stack):
    def __init__(
        self, scope: Construct, id_: str, *, deploy: DeployInputs, **kwargs
    ) -> None:
        super().__init__(scope, id_, **kwargs)
        self.deploy = deploy
