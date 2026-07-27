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
