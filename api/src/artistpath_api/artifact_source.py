"""Fetch an APG1 artifact from a local path or S3, and verify it before use.

The reader is injected so the URI parsing and both checksum branches are
testable with no AWS account and no credentials — which is what makes Track A
of the deploy design genuinely AWS-free (DEP-18, DEP-28).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from artistpath_api.graph_store import GraphStore

BytesReader = Callable[[str], bytes]

_S3_SCHEME = "s3://"


def parse_s3_uri(uri: str) -> tuple[str, str]:
    """Split `s3://bucket/key/with/slashes` into ("bucket", "key/with/slashes")."""
    if not uri.startswith(_S3_SCHEME):
        raise ValueError(f"not an s3 uri: {uri!r}")
    remainder = uri[len(_S3_SCHEME) :]
    bucket, _, key = remainder.partition("/")
    if not bucket or not key:
        raise ValueError(f"not an s3 uri: {uri!r}")
    return bucket, key


def default_reader(uri: str) -> bytes:
    """Read from S3 when the URI says so, otherwise from the filesystem.

    boto3 is imported lazily so that local development and the whole test suite
    never require it to be configured.
    """
    if uri.startswith(_S3_SCHEME):
        import boto3

        bucket, key = parse_s3_uri(uri)
        return boto3.client("s3").get_object(Bucket=bucket, Key=key)["Body"].read()
    return Path(uri).read_bytes()


def load_graph(
    uri: str,
    expected_sha256: str = "",
    reader: BytesReader = default_reader,
) -> GraphStore:
    """Fetch, verify, and parse an artifact.

    An empty `expected_sha256` skips verification, which is the local-development
    case. Production sets it: a conclusion drawn from the wrong artifact looks
    exactly like a correct one.
    """
    payload = reader(uri)
    digest = hashlib.sha256(payload).hexdigest()
    if expected_sha256 and digest != expected_sha256:
        raise ValueError(
            f"artifact checksum mismatch: expected {expected_sha256}, got {digest}"
        )
    store = GraphStore.from_bytes(payload)
    store.source_sha256 = digest
    return store
