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
from aws_cdk import aws_certificatemanager as acm
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

# The username half of the shared site credential. It is NOT a secret — the
# password is — and RMD-11 serves it in the 401 body so a visitor knows what to
# type. Named once and substituted into both halves, because a body naming a
# username the gate would reject is FRO-2 with extra steps.
SITE_USERNAME = "artistpath"

# Cost attribution: every resource this stack creates carries `app=<this>`, so
# a Cost Explorer filter can separate this project from anything else sharing
# the account. Named once so the stack and its test cannot drift apart.
APP_TAG_VALUE = "musicapp"


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
    # The permanent public name. G3-A5: until 2026-07-28 the site was welded to
    # CloudFront's generated domain, which cannot be recreated, moved between
    # accounts, or migrated off CloudFront — so every link ever shared was
    # pinned to infrastructure rather than to a name we control.
    site_hostname: str = ""
    # us-east-1 ACM certificate for site_hostname. Requested out of band and
    # passed in: CDK could request it, but DNS validation would block synth on
    # a record only the operator can add, and synth must stay offline.
    certificate_arn: str = ""
    # TKB-7 — the first deploy is a chicken-and-egg: App Runner needs an image
    # that cannot be pushed until ECR exists, and it needs the graph in a
    # bucket that does not exist either. Creating the service in the same pass
    # gives CREATE_FAILED and rolls the whole stack back, taking the ECR
    # repository with it. `cdk deploy -c stage=storage` builds only the pieces
    # the image push and artifact upload need; the default builds everything.
    include_service: bool = True


class ArtistpathStack(cdk.Stack):
    def __init__(
        self, scope: Construct, id_: str, *, deploy: DeployInputs, **kwargs
    ) -> None:
        super().__init__(scope, id_, **kwargs)
        self.deploy = deploy

        # Every taggable resource this account holds belongs to this app, so the
        # tag goes on at the stack and CDK propagates it to each construct.
        # Applied here rather than in app.py so synth tests can see it — a tag
        # added at the App would be invisible to every test in this suite.
        #
        # ⚠ App Runner is EXCLUDED, and this is not a preference. Its Tags
        # property is immutable, so adding one forces a REPLACEMENT — and the
        # service carries an explicit service_name, so the replacement cannot
        # succeed: CloudFormation creates the new resource before deleting the
        # old, and App Runner refuses the duplicate name. Measured on a real
        # deploy, 2026-07-28, which failed and rolled back:
        #   "Service with the provided name already exists: artistpath-api."
        # Retrying cannot help; it is a deadlock, not a transient error.
        # Those two resources are tagged out of band instead — infra/README.md
        # §1, which also records the resulting drift as deliberate.
        cdk.Tags.of(self).add(
            "app",
            APP_TAG_VALUE,
            exclude_resource_types=[
                "AWS::AppRunner::Service",
                "AWS::AppRunner::AutoScalingConfiguration",
            ],
        )

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

        if not deploy.include_service:
            # Storage-only first pass (TKB-7). The billing alarm rides along:
            # it is independent of the service and is the thing you least want
            # to forget.
            self._add_billing_alarm(deploy)
            cdk.CfnOutput(
                self, "ArtifactBucketName", value=self.artifact_bucket.bucket_name
            )
            cdk.CfnOutput(self, "SpaBucketName", value=self.spa_bucket.bucket_name)
            cdk.CfnOutput(self, "EcrRepositoryUri", value=self.repo.repository_uri)
            return

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

        # SEC-5: without this the account default applies — max 25 instances.
        # The origin secret rejects requests INSIDE the container, after App
        # Runner has already counted them and scaled on them, so DEP-17's claim
        # that the gate stands between a forwarded link and an unbounded bill is
        # true through CloudFront and false at the API origin. That is the same
        # shape TR-7 corrected once already: a control that protects the front
        # door while the origin answers on its own public URL.
        #
        # 2 is chosen for friends-and-family, where the expected concurrent load
        # is a handful of people. It is a COST CEILING, not a capacity estimate:
        # if the app is ever shared wider, raise it deliberately rather than
        # discovering it as latency.
        self.autoscaling = apprunner.CfnAutoScalingConfiguration(
            self,
            "ApiAutoScaling",
            auto_scaling_configuration_name="artistpath-api",
            min_size=1,
            max_size=2,
        )

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
                                # ARC-5: passed through rather than left to
                                # match ApiConfig.clip_table_name's default by
                                # coincidence. Until 2026-07-27 "artistpath-clips"
                                # was a literal in two packages with NOTHING
                                # binding them, and a rename on either side is a
                                # runtime error on the first clip lookup, in
                                # production, that no test in either package can
                                # catch. Reading it off the construct means the
                                # table cannot be renamed without this moving.
                                _env("ARTISTPATH_CLIP_TABLE", self.clip_table.table_name),
                                _env("ARTISTPATH_ORIGIN_SECRET", deploy.origin_secret),
                                # Present and EMPTY — but this is now a
                                # statement of intent, NOT the guarantee.
                                #
                                # RMD-6, measured 2026-07-27: an empty-valued
                                # environment variable does not reach a running
                                # App Runner service. Drift detection reported
                                # this one REMOVE'd, and the deployed API was
                                # serving config.py's old dev default. TR-8's
                                # prescription — "set it to empty, never omit
                                # it" — cannot be satisfied by this mechanism.
                                #
                                # The guarantee moved to ApiConfig.cors_origins,
                                # which now defaults to empty, so ARRIVING or
                                # NOT is equally safe. Keep this line anyway: it
                                # documents the intent, and a cross-origin
                                # deployment would set a real value here.
                                _env("ARTISTPATH_CORS_ORIGINS", ""),
                            ],
                        )
                    ),
                ),
            ),
            auto_scaling_configuration_arn=(
                self.autoscaling.attr_auto_scaling_configuration_arn
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
            f"{SITE_USERNAME}:{deploy.site_password}".encode()
        ).decode()
        function_code = (
            (Path(__file__).parent / "viewer_function.js")
            .read_text()
            .replace("__EXPECTED_AUTH__", expected_auth)
            .replace("__EXPECTED_USERNAME__", SITE_USERNAME)
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
            # Empty means "generated domain only", which is what the storage
            # stage and every test that does not care about the hostname get.
            domain_names=[deploy.site_hostname] if deploy.site_hostname else None,
            certificate=(
                acm.Certificate.from_certificate_arn(
                    self, "SiteCertificate", deploy.certificate_arn
                )
                if deploy.certificate_arn
                else None
            ),
            # NO error_responses: it is distribution-level and would rewrite
            # the API's own errors too. The SPA fallback is in the viewer
            # function, which is per-behaviour (TKB-2).
        )

        self._add_billing_alarm(deploy)

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

    def _add_billing_alarm(self, deploy: DeployInputs) -> None:
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
