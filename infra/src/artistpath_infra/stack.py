"""One stack: SPA bucket, artifact bucket, clip table, ECR, App Runner,
CloudFront, billing alarm.

Constructs are added task by task; see
docs/superpowers/plans/2026-07-26-track-b-infrastructure.md.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_apprunner as apprunner
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
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
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    self.spa_bucket
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                function_associations=fn_association,
            ),
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=api_origin,
                    viewer_protocol_policy=(
                        cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                    ),
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    # Caching a re-signed clip URL resurrects C2 (TR-6).
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy(
                        self,
                        "ApiOriginRequestPolicy",
                        query_string_behavior=(
                            cloudfront.OriginRequestQueryStringBehavior.all()
                        ),
                        # Authorization is deliberately NOT forwarded: the
                        # browser attaches it to same-origin fetches, the
                        # viewer function checks it at the edge, and it has no
                        # business reaching the API.
                        header_behavior=(
                            cloudfront.OriginRequestHeaderBehavior.allow_list(
                                "x-journey-id", "content-type"
                            )
                        ),
                        cookie_behavior=cloudfront.OriginRequestCookieBehavior.none(),
                    ),
                    function_associations=fn_association,
                ),
            },
            default_root_object="index.html",
            # NO error_responses: it is distribution-level and would rewrite
            # the API's own errors too. The SPA fallback is in the viewer
            # function, which is per-behaviour (TKB-2).
        )

        topic = sns.Topic(self, "AlarmTopic")
        topic.add_subscription(sns_subscriptions.EmailSubscription(deploy.alarm_email))
        # AWS/Billing is published only in us-east-1, and only once billing
        # alerts are enabled in the account's billing preferences — without
        # that the alarm sits in INSUFFICIENT_DATA forever (prerequisite P3).
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

        cdk.CfnOutput(
            self, "SiteUrl", value=f"https://{self.distribution.domain_name}"
        )
        cdk.CfnOutput(
            self, "ApiOriginUrl", value=f"https://{self.service.attr_service_url}"
        )
        cdk.CfnOutput(
            self, "ArtifactBucketName", value=self.artifact_bucket.bucket_name
        )
        cdk.CfnOutput(self, "SpaBucketName", value=self.spa_bucket.bucket_name)
        cdk.CfnOutput(self, "EcrRepositoryUri", value=self.repo.repository_uri)
        cdk.CfnOutput(
            self, "DistributionId", value=self.distribution.distribution_id
        )
