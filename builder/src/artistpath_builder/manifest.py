"""Build provenance, written as a sidecar next to every artifact.

Four graphs once sat in builder/scratch/ with no record of which commit built
them, and were compared as though they differed in one variable. They differed
in two, and that invalidated two separate analyses. Every build now records
what produced it.

A sidecar rather than an APG1 header field: the artifact format is the
builder/api contract and is deliberately not changed in this phase.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from artistpath_builder.config import BuilderConfig


def _git_commit() -> str:
    """Current HEAD, or "unknown" outside a git checkout."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and len(commit) == 40 else "unknown"


def _json_safe(value):
    """Coerce a config value to something `json.dumps` accepts.

    `BuilderConfig.unlistenable_list_path` is a `Path`, and `dataclasses.asdict`
    preserves it as one — so the manifest write raised
    `TypeError: Object of type WindowsPath is not JSON serializable` for any build
    that set it. That had never fired: every build using `--unlistenable-list` so
    far was REJECTED by acceptance before serialising, and every build that got
    as far as a manifest used the shipped default of `None`. The first adoption
    build off a censused payload would have hit it, AFTER the ~28 minutes of work,
    with the artifact already on disk and no record of what produced it.

    Found 2026-08-09 by the `JFX-` diagnostic build, which is the first build to
    both set the flag and reach this line.
    """
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    return value


def build_manifest(
    graph, config: BuilderConfig, payload: bytes, elapsed_seconds: float
) -> dict:
    """Everything needed to reproduce or identify this artifact."""
    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "elapsed_seconds": round(elapsed_seconds, 1),
        "artists": graph.artist_count,
        "edges": graph.edge_count,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "config": _json_safe(dataclasses.asdict(config)),
    }


def write_manifest(artifact_path: Path, manifest: dict) -> None:
    """Write `<artifact>.json` beside the artifact."""
    sidecar = artifact_path.with_suffix(artifact_path.suffix + ".json")
    sidecar.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
