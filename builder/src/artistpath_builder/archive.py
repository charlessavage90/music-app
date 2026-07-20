"""Verbatim storage of raw upstream responses.

Spec section 3.1 step 2: rebuilds replay this archive instead of the network,
which is what makes the crawl a one-time event rather than a dependency.
Payloads are stored exactly as received and are never reformatted.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, runtime_checkable


def _validate_key(key: str) -> None:
    if not key or key.startswith("/") or ".." in key.split("/"):
        raise ValueError(f"unsafe archive key: {key!r}")


@runtime_checkable
class RawArchive(Protocol):
    def put(self, key: str, payload: bytes) -> None: ...
    def get(self, key: str) -> bytes | None: ...
    def has(self, key: str) -> bool: ...
    def keys(self) -> Iterator[str]: ...


class LocalArchive:
    """Filesystem-backed archive. Used for development and tests."""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        _validate_key(key)
        return self._root / key

    def put(self, key: str, payload: bytes) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    def get(self, key: str) -> bytes | None:
        path = self._path(key)
        return path.read_bytes() if path.is_file() else None

    def has(self, key: str) -> bool:
        return self._path(key).is_file()

    def keys(self) -> Iterator[str]:
        for path in sorted(self._root.rglob("*")):
            if path.is_file():
                yield path.relative_to(self._root).as_posix()


class S3Archive:
    """S3-backed archive. Used in CI and for the real crawl."""

    def __init__(self, bucket: str, prefix: str = "raw", client=None) -> None:
        import boto3

        self._bucket = bucket
        self._prefix = prefix.strip("/")
        self._client = client or boto3.client("s3")

    def _full_key(self, key: str) -> str:
        _validate_key(key)
        return f"{self._prefix}/{key}"

    def put(self, key: str, payload: bytes) -> None:
        self._client.put_object(
            Bucket=self._bucket, Key=self._full_key(key), Body=payload
        )

    def get(self, key: str) -> bytes | None:
        from botocore.exceptions import ClientError

        try:
            response = self._client.get_object(
                Bucket=self._bucket, Key=self._full_key(key)
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("NoSuchKey", "404"):
                return None
            raise
        return response["Body"].read()

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def keys(self) -> Iterator[str]:
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=f"{self._prefix}/"):
            for obj in page.get("Contents", []):
                yield obj["Key"][len(self._prefix) + 1 :]
