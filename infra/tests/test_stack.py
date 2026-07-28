"""Synth assertions. These run with no AWS account and no credentials.

Every test here holds a property some finding paid for. Where that is true the
finding id is in the test name or a comment — deleting the assertion without
reading it re-opens the defect.
"""

from dataclasses import replace

import aws_cdk as cdk
from aws_cdk.assertions import Template

from artistpath_infra.stack import APP_TAG_VALUE, ArtistpathStack, DeployInputs

DEPLOY = DeployInputs(
    graph_key="graph-test.bin",
    graph_sha256="0" * 64,
    origin_secret="test-origin-secret",
    site_password="test-password",
    billing_alarm_usd=25.0,
    alarm_email="nobody@example.com",
    image_tag="test",
    site_hostname="artistpath.test.invalid",
    certificate_arn="arn:aws:acm:us-east-1:000000000000:certificate/test",
)


def template(**overrides) -> Template:
    """Synthesise the stack, optionally varying one DeployInputs field.

    The overrides exist for a specific class of vacuous test (QUA-7, QUA-9): an
    assertion that a value equals the one DEPLOY happens to carry passes just as
    well when the stack hardcodes it and ignores its input. Synthesising twice
    with different inputs is what tells those apart.
    """
    app = cdk.App()
    deploy = replace(DEPLOY, **overrides) if overrides else DEPLOY
    stack = ArtistpathStack(
        app, "Test", deploy=deploy, env=cdk.Environment(region="us-east-1")
    )
    return Template.from_stack(stack)


def _resource_by_logical_id_prefix(type_: str, prefix: str) -> dict:
    """CDK appends a hash to logical ids, so match on the construct id prefix.

    Needed because `has_resource_properties` passes if ANY resource of the type
    matches — which is QUA-6: the versioning assertion below was satisfied by
    either bucket, so moving versioning from the artifact bucket to the SPA
    bucket passed.
    """
    matches = {
        lid: r
        for lid, r in template().find_resources(type_).items()
        if lid.startswith(prefix)
    }
    assert len(matches) == 1, f"expected one {prefix}* {type_}, got {list(matches)}"
    return next(iter(matches.values()))


def test_the_stack_synthesises():
    assert template().to_json()["Resources"]


def test_the_storage_only_stage_omits_the_service_and_the_distribution():
    # TKB-7: the first deploy cannot create App Runner — the image is not in
    # ECR yet and the graph is not in S3 yet, so it would CREATE_FAILED and
    # roll the whole stack back, taking the ECR repository with it.
    app = cdk.App()
    stack = ArtistpathStack(
        app,
        "Storage",
        deploy=replace(DEPLOY, include_service=False),
        env=cdk.Environment(region="us-east-1"),
    )
    storage = Template.from_stack(stack)
    assert storage.find_resources("AWS::AppRunner::Service") == {}
    assert storage.find_resources("AWS::CloudFront::Distribution") == {}
    # But the pieces the image push and the artifact upload need must exist,
    # and so must the alarm — it is the thing you least want to forget.
    assert len(storage.find_resources("AWS::S3::Bucket")) == 2
    assert len(storage.find_resources("AWS::ECR::Repository")) == 1
    assert len(storage.find_resources("AWS::CloudWatch::Alarm")) == 1


def test_the_artifact_bucket_is_versioned_because_it_is_the_only_second_copy():
    # TR-9: acceptance.py refuses to rebuild the adopted artifact, so the only
    # other copy is gitignored on one OneDrive-synced machine.
    #
    # QUA-6: this asserted only that SOME bucket was versioned, so moving
    # versioning to the SPA bucket — which is rebuilt from source on every
    # deploy and needs none — passed. Both halves are named now.
    artifact = _resource_by_logical_id_prefix("AWS::S3::Bucket", "ArtifactBucket")
    spa = _resource_by_logical_id_prefix("AWS::S3::Bucket", "SpaBucket")

    assert artifact["Properties"]["VersioningConfiguration"] == {"Status": "Enabled"}
    assert "VersioningConfiguration" not in spa["Properties"]


def test_the_stateful_resources_are_retained_and_the_rebuildable_one_is_not():
    # QUA-6: nothing asserted RETAIN, so flipping the artifact bucket to DESTROY
    # passed — and that bucket holds the only second copy of the adopted graph
    # (TR-9). The clip table and the image repository are retained for the same
    # reason the deploy is staged: losing them is expensive and silent.
    for type_, prefix in [
        ("AWS::S3::Bucket", "ArtifactBucket"),
        ("AWS::DynamoDB::Table", "ClipTable"),
        ("AWS::ECR::Repository", "ApiRepo"),
    ]:
        assert _resource_by_logical_id_prefix(type_, prefix)["DeletionPolicy"] == (
            "Retain"
        ), f"{prefix} must be RETAIN"

    # The SPA bucket is the deliberate exception: it is rebuilt from source by
    # `s3 sync` on every deploy, so retaining it would only orphan it (ARC-4).
    assert (
        _resource_by_logical_id_prefix("AWS::S3::Bucket", "SpaBucket")["DeletionPolicy"]
        == "Delete"
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


def test_the_image_repository_scans_on_push():
    # Scan-on-push is the only automated dependency check in the deployed
    # path: Snyk reads neither uv.lock nor a PEP-621 pyproject.toml (TKB-3).
    template().has_resource_properties(
        "AWS::ECR::Repository",
        {
            "RepositoryName": "artistpath-api",
            "ImageScanningConfiguration": {"ScanOnPush": True},
        },
    )


def _service_env() -> dict[str, str]:
    (service,) = template().find_resources("AWS::AppRunner::Service").values()
    pairs = service["Properties"]["SourceConfiguration"]["ImageRepository"][
        "ImageConfiguration"
    ]["RuntimeEnvironmentVariables"]
    return {p["Name"]: p["Value"] for p in pairs}


def test_the_service_gets_every_environment_variable_the_api_reads():
    got = _service_env()
    assert got["ARTISTPATH_GRAPH_SHA256"] == "0" * 64  # TKA-11
    assert got["ARTISTPATH_CLIP_CACHE"] == "dynamo"
    assert got["ARTISTPATH_ORIGIN_SECRET"] == "test-origin-secret"
    assert "graph-test.bin" in str(got["ARTISTPATH_GRAPH"])


def test_cors_origins_is_present_and_empty_not_merely_unset():
    # TR-8, and this test is CORRECT — it was also not enough, which is the
    # interesting part.
    #
    # RMD-6, 2026-07-27: this assertion passed, the template was right, and
    # production was still wrong. An empty-valued environment variable does not
    # reach a running App Runner service, so the deployed API fell back to
    # config.py's then-default of http://localhost:5173. Nothing in any of the
    # four packages could see that: the gap is between the template and AWS.
    #
    # The guarantee now lives in ApiConfig.cors_origins, which defaults to empty
    # (see api/tests/test_cors.py). This test keeps holding the template's
    # intent; `detect-stack-drift` in the runbook's gates is what holds the
    # deployed reality.
    got = _service_env()
    assert "ARTISTPATH_CORS_ORIGINS" in got
    assert got["ARTISTPATH_CORS_ORIGINS"] == ""


def test_the_service_has_a_scaling_ceiling_and_is_wired_to_it():
    # SEC-5: with no configuration the ACCOUNT default applies — 25 instances.
    # The origin secret rejects requests inside the container, after App Runner
    # has counted and scaled on them, so the gate does not bound the bill at the
    # API origin (the shape TR-7 corrected once already).
    (logical_id, config) = next(
        iter(
            template()
            .find_resources("AWS::AppRunner::AutoScalingConfiguration")
            .items()
        )
    )
    assert config["Properties"]["MaxSize"] == 2

    # A configuration the service does not reference bounds nothing — the same
    # detached-resource shape as QUA-2.
    (service,) = template().find_resources("AWS::AppRunner::Service").values()
    assert service["Properties"]["AutoScalingConfigurationArn"] == {
        "Fn::GetAtt": [logical_id, "AutoScalingConfigurationArn"]
    }


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
    # TR-7: an access role for the ECR pull and an instance role for runtime.
    roles = template().find_resources("AWS::IAM::Role")
    principals = str(
        [
            s["Principal"]
            for r in roles.values()
            for s in r["Properties"]["AssumeRolePolicyDocument"]["Statement"]
        ]
    )
    assert "build.apprunner.amazonaws.com" in principals
    assert "tasks.apprunner.amazonaws.com" in principals


def _distribution() -> dict:
    (dist,) = template().find_resources("AWS::CloudFront::Distribution").values()
    return dist["Properties"]["DistributionConfig"]


def test_the_api_behaviour_disables_caching_or_C2_comes_back():
    # TR-6: CloudFront's default would cache the freshly re-signed clip URL
    # and resurrect "clips die after a while", closed 2026-07-25 and marked
    # do-not-re-plan. It would present as a regression in closed work.
    CACHING_DISABLED = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    (api_behaviour,) = _distribution()["CacheBehaviors"]
    assert api_behaviour["PathPattern"] == "/api/*"
    assert api_behaviour["CachePolicyId"] == CACHING_DISABLED
    assert "POST" in api_behaviour["AllowedMethods"]


def test_the_api_behaviour_forwards_the_query_string_and_the_journey_header():
    (policy,) = template().find_resources("AWS::CloudFront::OriginRequestPolicy").values()
    config = policy["Properties"]["OriginRequestPolicyConfig"]
    # Without this every search returns whatever `q` was cached first (TR-6).
    assert config["QueryStringsConfig"]["QueryStringBehavior"] == "all"
    # CloudFront strips unlisted headers, which would silently drop DEP-6.
    assert "x-journey-id" in str(config["HeadersConfig"]).lower()


def test_the_distribution_has_no_custom_error_responses():
    # TKB-2: errorResponses is distribution-level, so mapping 403/404 to
    # index.html would rewrite the API's own 404 and the origin-secret 403
    # into an HTML page with status 200, and the SPA would parse HTML as
    # JSON. The SPA fallback lives in the viewer function instead, which is
    # attached per behaviour.
    assert "CustomErrorResponses" not in _distribution()


def test_the_viewer_function_gates_on_the_password_and_rewrites_spa_routes():
    (fn,) = template().find_resources("AWS::CloudFront::Function").values()
    code = fn["Properties"]["FunctionCode"]
    assert "authorization" in code
    assert "/index.html" in code
    assert "401" in code


def _viewer_request_arns(behaviour: dict) -> list:
    """The viewer-request functions CloudFront will actually run on a behaviour.

    A function that exists in the template but is associated with nothing runs
    on nothing — which is QUA-2 exactly, and why the substring test above is
    not enough on its own.
    """
    return [
        association["FunctionARN"]
        for association in behaviour.get("FunctionAssociations", [])
        if association["EventType"] == "viewer-request"
    ]


def test_the_password_function_is_attached_to_the_site_itself():
    # QUA-2, rank 1 of the DEP-33 review and the only blocking finding that is
    # SILENT. Detaching the association leaves the API gated (it has its own
    # origin-secret middleware) and the entire site publicly readable, with the
    # site working perfectly for the owner the whole time. The pre-existing test
    # above passes on a detached function: it reads the function's source, which
    # is unchanged by detaching it.
    #
    # Measured against the deployed distribution 2026-07-27: the default
    # behaviour carries exactly one viewer-request function, no Lambda@Edge,
    # TrustedSigners disabled and TrustedKeyGroups disabled — so this function
    # is the SOLE access control on the site, and nothing else would catch its
    # removal.
    (function_id,) = template().find_resources("AWS::CloudFront::Function").keys()
    expected = {"Fn::GetAtt": [function_id, "FunctionARN"]}

    assert _viewer_request_arns(_distribution()["DefaultCacheBehavior"]) == [expected]


def test_the_password_function_is_attached_to_the_api_behaviour_too():
    # The other half of QUA-2. /api/* is a separate behaviour with its own
    # associations, so gating the site and gating the API are two independent
    # facts and each needs its own assertion. The origin-secret middleware is a
    # second layer here, not a substitute: it stops App Runner's public URL
    # being a way round (TR-7), and says nothing about the edge.
    (function_id,) = template().find_resources("AWS::CloudFront::Function").keys()
    expected = {"Fn::GetAtt": [function_id, "FunctionARN"]}

    (api_behaviour,) = _distribution()["CacheBehaviors"]
    assert api_behaviour["PathPattern"] == "/api/*"
    assert _viewer_request_arns(api_behaviour) == [expected]


def test_the_api_origin_carries_the_shared_secret_header():
    custom = [o for o in _distribution()["Origins"] if "CustomOriginConfig" in o]
    assert custom, "no App Runner origin found"
    headers = {
        h["HeaderName"].lower(): h["HeaderValue"]
        for o in custom
        for h in o.get("OriginCustomHeaders", [])
    }
    assert headers.get("x-origin-secret") == "test-origin-secret"


def test_the_artifact_bucket_is_not_an_origin():
    # TR-7: or the graph is a 14 MB download to anyone who guesses the name.
    assert "ArtifactBucket" not in str(_distribution()["Origins"])


def test_the_billing_alarm_uses_the_threshold_it_was_given():
    # DEP-31: DEP-17's success condition is "observe a month of billing", and
    # an alarm is how you observe without remembering to look.
    #
    # QUA-7: asserting Threshold == 25.0 while DEPLOY carries 25.0 passes even
    # when the stack hardcodes 25.0 and ignores its input entirely — which was
    # one of the review's green mutations. Synthesising a second time with a
    # different value is what distinguishes them.
    template().has_resource_properties(
        "AWS::CloudWatch::Alarm",
        {
            "MetricName": "EstimatedCharges",
            "Namespace": "AWS/Billing",
            "Threshold": 25.0,
            "ComparisonOperator": "GreaterThanThreshold",
        },
    )
    template(billing_alarm_usd=99.0).has_resource_properties(
        "AWS::CloudWatch::Alarm", {"Threshold": 99.0}
    )


def test_the_image_tag_and_container_port_are_what_the_service_was_given():
    # QUA-9: neither was asserted, so pinning the image to `latest` regardless
    # of image_tag, and changing the container port, both passed. The tag is the
    # whole of the runbook's rollback story (ARC-6, ARC-14) and a wrong port
    # fails every health check.
    def _image_repository(**overrides) -> dict:
        (service,) = template(**overrides).find_resources(
            "AWS::AppRunner::Service"
        ).values()
        return service["Properties"]["SourceConfiguration"]["ImageRepository"]

    assert _image_repository()["ImageConfiguration"]["Port"] == "8000"

    # The identifier is an Fn::Join, so the tag is asserted as a substring of
    # the rendered intrinsic — and asserted to MOVE with its input.
    assert ":test" in str(_image_repository()["ImageIdentifier"])
    assert ":other-tag" in str(
        _image_repository(image_tag="other-tag")["ImageIdentifier"]
    )


def test_the_clip_table_matches_what_DynamoClipCache_writes():
    # clips.py's _put_sync writes Item={"mbid": ..., "ttl": ...}. A mismatch
    # here is a runtime error that no test in api/ can catch.
    template().has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [{"AttributeName": "mbid", "KeyType": "HASH"}],
            "TimeToLiveSpecification": {"AttributeName": "ttl", "Enabled": True},
            "BillingMode": "PAY_PER_REQUEST",
        },
    )


def test_the_clip_table_name_is_the_one_the_api_looks_for():
    # QUA-8: the name was unasserted, so renaming the table passed — and the
    # failure is a runtime error on the first clip lookup, in production.
    assert (
        _resource_by_logical_id_prefix("AWS::DynamoDB::Table", "ClipTable")[
            "Properties"
        ]["TableName"]
        == "artistpath-clips"
    )


def test_the_service_is_told_the_table_name_rather_than_guessing_it():
    # ARC-5: the name was a literal in two packages — here and as
    # ApiConfig.clip_table_name's default — with nothing binding them. It is now
    # passed through as an environment variable read off the construct, so the
    # table cannot be renamed without the service's variable moving with it.
    #
    # This is what closes the gap that the test above cannot: infra/ cannot
    # import api/, so no infra test can see config.py's default. What it CAN do
    # is stop the API needing that default at all.
    (table_id,) = [
        lid
        for lid in template().find_resources("AWS::DynamoDB::Table")
        if lid.startswith("ClipTable")
    ]
    got = _service_env()

    assert "ARTISTPATH_CLIP_TABLE" in got, "the service must not rely on the default"
    # A Ref, not a copied literal: CloudFormation resolves it from the table
    # itself, so the two cannot diverge even in principle.
    assert got["ARTISTPATH_CLIP_TABLE"] == {"Ref": table_id}, got[
        "ARTISTPATH_CLIP_TABLE"
    ]


def test_the_distribution_serves_the_custom_hostname():
    # G3-A5: without an alternate domain name CloudFront 403s any request whose
    # Host is not its own generated address, so Cloudflare cannot be put in
    # front at all. Asserted against an OVERRIDDEN value, not DEPLOY's, so an
    # assertion that happens to match the fixture cannot pass vacuously.
    t = template(site_hostname="probe.example.org")
    t.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {"DistributionConfig": {"Aliases": ["probe.example.org"]}},
    )


def test_the_distribution_uses_the_supplied_certificate():
    t = template(certificate_arn="arn:aws:acm:us-east-1:111111111111:certificate/probe")
    t.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {
            "DistributionConfig": {
                "ViewerCertificate": {
                    "AcmCertificateArn": (
                        "arn:aws:acm:us-east-1:111111111111:certificate/probe"
                    )
                }
            }
        },
    )


# Named individually and asserted per resource, because `has_resource_properties`
# passes if ANY resource of the type matches (QUA-6) — a tag that landed on one
# bucket and nothing else would satisfy a looser assertion. Every entry here is
# billable, which is the point of the tag.
_MUST_CARRY_APP_TAG = [
    ("AWS::CloudFront::Distribution", "Distribution"),
    ("AWS::DynamoDB::Table", "ClipTable"),
    ("AWS::S3::Bucket", "SpaBucket"),
    ("AWS::S3::Bucket", "ArtifactBucket"),
    ("AWS::ECR::Repository", "ApiRepo"),
    ("AWS::CloudWatch::Alarm", "BillingAlarm"),
]


def test_every_billable_resource_carries_the_app_tag():
    # Cost attribution: without this a Cost Explorer filter cannot separate this
    # project from anything else in the account, and the billing alarm is the
    # only spend control there is.
    resources = template().to_json()["Resources"]
    want = {"Key": "app", "Value": APP_TAG_VALUE}
    missing = []

    for type_, prefix in _MUST_CARRY_APP_TAG:
        matches = [
            lid
            for lid, r in resources.items()
            if r["Type"] == type_ and lid.startswith(prefix)
        ]
        assert len(matches) == 1, f"expected one {prefix}* {type_}, got {matches}"
        tags = resources[matches[0]].get("Properties", {}).get("Tags") or []
        if want not in tags:
            missing.append((type_, matches[0], tags))

    assert not missing, f"resources missing {want}: {missing}"


def test_app_runner_is_deliberately_left_untagged():
    # This asserts an ABSENCE, and it is load-bearing. Adding `app=musicapp` to
    # these two looks like an obvious omission and closing it is a deadlock:
    # App Runner's Tags property is immutable, so a tag forces a REPLACEMENT,
    # and the service has an explicit service_name, so CloudFormation cannot
    # create the replacement before deleting the original —
    #   "Service with the provided name already exists: artistpath-api."
    # Measured on a real deploy that failed and rolled back, 2026-07-28. The
    # two are tagged out of band instead; the drift is deliberate and recorded
    # in infra/README.md §1. Delete this test and the next deploy fails.
    resources = template().to_json()["Resources"]
    want = {"Key": "app", "Value": APP_TAG_VALUE}

    for type_, prefix in [
        ("AWS::AppRunner::Service", "ApiService"),
        ("AWS::AppRunner::AutoScalingConfiguration", "ApiAutoScaling"),
    ]:
        matches = [
            lid
            for lid, r in resources.items()
            if r["Type"] == type_ and lid.startswith(prefix)
        ]
        assert len(matches) == 1, f"expected one {prefix}* {type_}, got {matches}"
        tags = resources[matches[0]].get("Properties", {}).get("Tags") or []
        assert want not in tags, (
            f"{matches[0]} must NOT carry {want} — it forces an impossible "
            "replacement; see this test's comment"
        )
