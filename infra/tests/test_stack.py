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
