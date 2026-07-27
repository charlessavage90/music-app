"""One stack: SPA bucket, artifact bucket, clip table, ECR, App Runner,
CloudFront, billing alarm.

Constructs are added task by task; see
docs/superpowers/plans/2026-07-26-track-b-infrastructure.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_s3 as s3
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
        # acceptance.py refuses to rebuild the adopted artifact, so the upload
        # is its only second copy (TR-9) — hence RETAIN as well.
        self.artifact_bucket = s3.Bucket(
            self,
            "ArtifactBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # Key and TTL attribute names are fixed by clips.py's DynamoClipCache;
        # the table name matches ApiConfig.clip_table_name's default, so the
        # service needs no override for it.
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

        self.repo = ecr.Repository(
            self,
            "ApiRepo",
            repository_name="artistpath-api",
            image_scan_on_push=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            lifecycle_rules=[ecr.LifecycleRule(max_image_count=5)],
        )
