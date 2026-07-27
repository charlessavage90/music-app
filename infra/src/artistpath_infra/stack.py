"""One stack: SPA bucket, artifact bucket, clip table, ECR, App Runner,
CloudFront, billing alarm.

Constructs are added task by task; see
docs/superpowers/plans/2026-07-26-track-b-infrastructure.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import aws_cdk as cdk
from aws_cdk import aws_apprunner as apprunner
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
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
        # Scoped to the one key, not to the bucket.
        self.artifact_bucket.grant_read(instance_role, deploy.graph_key)
        self.clip_table.grant(instance_role, "dynamodb:GetItem", "dynamodb:PutItem")

        graph_uri = f"s3://{self.artifact_bucket.bucket_name}/{deploy.graph_key}"

        def _env(name: str, value: str):
            return apprunner.CfnService.KeyValuePairProperty(name=name, value=value)

        # L1 CfnService rather than aws_apprunner_alpha: the alpha module is a
        # second versioned dependency that must track aws-cdk-lib, and this
        # stack needs five of its properties.
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
