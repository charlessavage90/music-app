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
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from artistpath_builder.config import BuilderConfig

logger = logging.getLogger(__name__)


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


def resolve_build_inputs(config: BuilderConfig, archive_dir) -> dict:
    """Which FILES this build will actually apply, with their identities.

    The config already records `drop_unlistenable: true` — a flag, not an
    input. The override pointer records `null`, which means "whatever the
    default was that day", and the default is mutable: `CXA-` Task 2 moved the
    ALG-B unlistenable default, the `CXR-` revert did not move it back, and a
    rebuild came to differ from the live map by 31 artists with nothing in any
    manifest able to say so. Establishing that took a hand analysis
    (builder/analysis/2026-09-05-lux-e1-drift-source/).

    Design notes, each a decision rather than an accident:

    - **Hashed over the FILE'S BYTES**, not over a payload key. The three
      families' own hash keys are inconsistent (`sha256_over_sorted_mbids`,
      `sha256_over_sorted_drop_mbids`) and `featured_credit` carries none.
    - **A family whose flag is off is ABSENT**, never null. Absence reads as
      "not applied"; a null would read as "applied, identity unknown", which
      is the exact ambiguity this function exists to remove.
    - **Never raises.** This runs BEFORE the build so it can be logged in the
      first seconds. An unresolvable list is left out and the pipeline raises
      its own well-worded refusal a moment later; a provenance recorder must
      not pre-empt a diagnostic with a worse one.
    - **RECORDING ONLY — a mismatch is not a refusal** (owner, 2026-09-05).
      A gate here could fire in the first seconds rather than at the end, so
      it is cheap to add later; the reason to wait is that an escape hatch
      reached reflexively removes the protection it guards. Revisit once we
      know whether mismatches are routine or rare.
    """
    from artistpath_builder.featured_credit_drop import FEATURED_DROP_LISTS
    from artistpath_builder.no_release_drop import DROP_LISTS
    from artistpath_builder.unlistenable_drop import UNLISTENABLE_DROP_LISTS

    families = (
        ("no_release", config.drop_no_release_tail, DROP_LISTS.get(config.algorithm)),
        (
            "featured_credit",
            config.drop_featured_credit,
            FEATURED_DROP_LISTS.get(config.algorithm),
        ),
        (
            "unlistenable",
            config.drop_unlistenable,
            config.unlistenable_list_path
            or UNLISTENABLE_DROP_LISTS.get(config.algorithm),
        ),
    )

    drop_lists: dict[str, dict] = {}
    for name, applied, path in families:
        if not applied or path is None:
            continue
        try:
            digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        except OSError:
            continue
        drop_lists[name] = {"file": Path(path).name, "sha256": digest}

    # The archive is the other input that drifted, and a path is deliberately
    # all that is recorded: hashing tens of thousands of response files would
    # cost more than the build. Weak identity, but it is exactly what
    # separates `grt-archive-algb.pre-cex-snapshot` from the live archive,
    # which is the confusion that actually occurred.
    return {"archive_dir": str(archive_dir), "drop_lists": drop_lists}


def log_build_inputs(inputs: dict) -> None:
    """Print the resolved inputs at build START, not at the end.

    The whole value of the record is seeing an unintended input in the first
    seconds. A sidecar written after serialisation tells you what you built
    only once you have built it.
    """
    logger.info("archive: %s", inputs.get("archive_dir"))
    for name, entry in sorted(inputs.get("drop_lists", {}).items()):
        logger.info(
            "drop list %-16s %s (%s)", name, entry["file"], entry["sha256"][:12]
        )


def build_manifest(
    graph,
    config: BuilderConfig,
    payload: bytes,
    elapsed_seconds: float,
    build_inputs: dict | None = None,
) -> dict:
    """Everything needed to reproduce or identify this artifact.

    `build_inputs` is DEFAULTED and omitted entirely when absent, for the same
    reason `Graph.deezer_ids` is: a frozen probe
    (analysis/2026-08-09-jfx-prereg-critique/) calls this positionally with
    four arguments, and a key it never wrote must not appear in its manifests.
    """
    manifest = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "elapsed_seconds": round(elapsed_seconds, 1),
        "artists": graph.artist_count,
        "edges": graph.edge_count,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "config": _json_safe(dataclasses.asdict(config)),
    }
    if build_inputs is not None:
        manifest["build_inputs"] = build_inputs
    return manifest


def write_manifest(artifact_path: Path, manifest: dict) -> None:
    """Write `<artifact>.json` beside the artifact."""
    sidecar = artifact_path.with_suffix(artifact_path.suffix + ".json")
    sidecar.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
