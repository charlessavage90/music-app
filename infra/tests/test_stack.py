"""Synth assertions. These run with no AWS account and no credentials.

Every test here holds a property some finding paid for. Where that is true the
finding id is in the test name or a comment — deleting the assertion without
reading it re-opens the defect.
"""

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
    stack = ArtistpathStack(
        app, "Test", deploy=DEPLOY, env=cdk.Environment(region="us-east-1")
    )
    return Template.from_stack(stack)


def test_the_stack_synthesises():
    assert template().to_json()["Resources"]


def test_the_artifact_bucket_is_versioned_because_it_is_the_only_second_copy():
    # TR-9: acceptance.py refuses to rebuild the adopted artifact, so the only
    # other copy is gitignored on one OneDrive-synced machine.
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
    # TR-8: unset yields the dev default http://localhost:5173
    # (config.py's default_factory). The empty tuple requires setting the
    # variable TO empty — and same-origin means no preflight ever fires to
    # reveal the mistake.
    got = _service_env()
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
