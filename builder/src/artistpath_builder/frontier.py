"""Reconstruct the crawl frontier the checkpoint never recorded (ULC-F3).

`crawl.py` used to stop RECORDING neighbours once discovery reached the target,
so the frontier beyond it was lost and a resume rebuilt an empty queue. The
frontier is recoverable offline: every archived response lists its neighbours.

Enumeration goes through `pipeline.similar_prefix` — the same definition `fame`
and `build` use — rather than a private walk. A second copy of that rule is the
divergence class `test_pipeline_mirrors.py` exists to guard.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import PRODUCTION_ALGORITHM, BuilderConfig
from artistpath_builder.pipeline import similar_prefix
from artistpath_builder.sources.base import SimilaritySource

logger = logging.getLogger(__name__)


def reconstruct_referenced(
    archive: RawArchive,
    config: BuilderConfig,
    source: SimilaritySource,
) -> set[str]:
    """Every MBID named as a neighbour by any archived response.

    Sorted iteration: the result is a set, but a deterministic read order keeps
    logging and any future short-circuit reproducible (spec section 9).
    """
    prefix = similar_prefix(config, source)
    referenced: set[str] = set()
    scanned = 0
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix) : -len(".json")]
        if "/" in mbid:
            # A scoped sub-tree nested under the flat production layout —
            # another algorithm's data, never this reconstruction's.
            continue
        payload = archive.get(key)
        if payload is None:
            continue
        try:
            referenced.update(
                neighbour.mbid for neighbour in source.parse(payload, exclude_mbid=mbid)
            )
        except ValueError:
            logger.warning("unparseable similarity payload for %s", mbid)
            continue
        scanned += 1
    logger.info(
        "scanned %d responses, %d distinct mbids referenced", scanned, len(referenced)
    )
    return referenced


def rewrite_checkpoint(
    checkpoint_path: Path,
    config: BuilderConfig,
    referenced: set[str],
) -> dict[str, int]:
    """Union `referenced` into the checkpoint's `discovered` set.

    UNION, never replace (CEXR-7b): `discovered` must stay a superset of `done`
    because `Crawler.crawl` rebuilds its queue as `discovered - done`. The real
    archive holds artists that were crawled but that no response names, and a
    replacing rewrite would drop them while still reporting the right frontier
    size — the reported number cannot catch this, so the invariant is asserted
    directly by test.

    Backs the original up first: the checkpoint is the only record of a
    completed crawl and there is no second copy.
    """
    state = json.loads(checkpoint_path.read_text())
    stored = state.get("algorithm", PRODUCTION_ALGORITHM)
    if stored != config.algorithm:
        raise ValueError(
            f"checkpoint {checkpoint_path} was written under {stored!r}; "
            f"refusing to rewrite it under {config.algorithm!r} (RC-H3)"
        )

    done = set(state.get("done", []))
    discovered = set(state.get("discovered", [])) | referenced | done

    backup = checkpoint_path.with_name(checkpoint_path.name + ".bak")
    backup.write_bytes(checkpoint_path.read_bytes())

    payload = json.dumps(
        {
            "algorithm": config.algorithm,
            "done": sorted(done),
            "discovered": sorted(discovered),
            "exhausted": bool(state.get("exhausted", False)),
        },
        sort_keys=True,
    )
    checkpoint_path.write_text(payload)
    return {
        "done": len(done),
        "discovered": len(discovered),
        "frontier": len(discovered - done),
    }
