"""Reconstruct the crawl frontier the checkpoint never recorded (ULC-F3).

`crawl.py` used to stop RECORDING neighbours once discovery reached the target,
so the frontier beyond it was lost and a resume rebuilt an empty queue. The
frontier is recoverable offline: every archived response lists its neighbours.

Enumeration goes through `pipeline.similar_prefix` — the same definition `fame`
and `build` use — rather than a private walk. A second copy of that rule is the
divergence class `test_pipeline_mirrors.py` exists to guard.
"""

from __future__ import annotations

import logging

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
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
