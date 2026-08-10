"""`CXA-` Task 1: the FOURTH acceptance artifact — mutual k-NN over the 117k archive.

**Why this exists.** `acceptance.py`'s recalibration protocol requires the band to be
"checked against four known artifacts rather than centred on one". The `CXA-` plan's Task 1
table has three filled rows and one marked **NOT RUN**: a mutual-kNN build of the *extended*
(117,302-response) ALG-B archive. Without it the proposed band has never been shown to
discriminate the **cap rule** on the population it will actually govern — only the crawl
size. The `MSW-` band was checked against a mutual-kNN build of the *75k* archive; that row
does not transfer, because both the crawl and the drop payload have moved since.

**One knob.** Everything here matches the shipped `JFX-B` build — algorithm ALG-B, the
recensused ULF- payload, `require_fame=True`, `max_neighbours_per_artist=50` — and differs
in `cap_strategy` alone. That is what makes the row an isolating baseline rather than a
second confounded build.

**It does NOT serialise, deliberately.** The row needs a node count, an edge count and a
verdict; it does not need a 23 MB artifact nobody will deploy. `build_from_archive` and
`check_acceptance` are imported and called UNCHANGED — this script owns no build logic and
no criteria of its own, so it cannot drift from the pipeline the way a mirrored harness can.

**The bounds are not modified.** `PRODUCTION_ACCEPTANCE` is run as shipped, and the
PROPOSED band is evaluated separately via `dataclasses.replace` so both verdicts are
visible. Widening is an adoption decision and is the owner's (`CXA-S1`; `MSW-G3` precedent).

Usage:

    cd builder && UV_LINK_MODE=copy PYTHONUNBUFFERED=1 uv run python \\
      analysis/2026-08-10-cxa-acceptance-bounds/mknn_build.py
"""
from __future__ import annotations

import json
import logging
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "builder/src"))

from artistpath_builder.acceptance import (  # noqa: E402
    PRODUCTION_ACCEPTANCE,
    ArtifactRejected,
    check_acceptance,
)
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.pipeline import build_from_archive  # noqa: E402
from artistpath_builder.sources.listenbrainz import ListenBrainzSource  # noqa: E402

ARCHIVE_DIR = ROOT / "builder/scratch/grt-archive-algb"
PAYLOAD = ROOT / "builder/analysis/2026-08-09-cex-recensus/ulf_droplist_algb.json"

# PROPOSED at CXA- Task 1, ±20 % around the JFX-B build. NOT adopted — recorded
# here so this probe's verdict is reproducible against the numbers it tested.
# The owner's decision at CXA-S1 governs what actually lands in acceptance.py.
PROPOSED = replace(
    PRODUCTION_ACCEPTANCE,
    node_count=(70_900, 106_400),
    edge_count=(1_295_000, 1_942_000),
)


def _verdict(graph, criteria, label: str) -> dict:
    try:
        check_acceptance(graph, criteria)
    except ArtifactRejected as exc:
        logging.warning("%s: REJECTED", label)
        for line in str(exc).splitlines():
            logging.warning("  %s", line)
        return {"passed": False, "rejection_verbatim": str(exc)}
    logging.info("%s: ACCEPTED", label)
    return {"passed": True, "rejection_verbatim": None}


def main() -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    for path, what in ((ARCHIVE_DIR, "archive"), (PAYLOAD, "ULF- payload")):
        if not path.exists():
            raise SystemExit(f"{what} not found: {path}")

    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        # THE one knob. Everything else matches the JFX-B build.
        cap_strategy="mutual_knn",
        unlistenable_list_path=PAYLOAD,
        require_fame=True,
    )

    started = time.monotonic()
    graph = build_from_archive(
        config, LocalArchive(ARCHIVE_DIR), ListenBrainzSource(config)
    )
    elapsed = time.monotonic() - started

    degrees = np.diff(graph.offsets).astype(np.int64)
    result = {
        "what": "mutual k-NN build of the extended ALG-B archive (CXA- Task 1, "
        "the fourth acceptance artifact)",
        "artists": graph.artist_count,
        "edges": graph.edge_count,
        "median_degree": statistics.median(degrees.tolist()),
        "elapsed_seconds": round(elapsed, 1),
        "config": {
            "algorithm": config.algorithm,
            "cap_strategy": config.cap_strategy,
            "max_neighbours_per_artist": config.max_neighbours_per_artist,
            "require_fame": config.require_fame,
            "unlistenable_list_path": str(PAYLOAD),
        },
        "serialised": False,
    }
    logging.info(
        "built: %d artists, %d edges, median degree %s, %.0fs",
        graph.artist_count,
        graph.edge_count,
        result["median_degree"],
        elapsed,
    )

    result["against_shipped_bounds"] = _verdict(
        graph, PRODUCTION_ACCEPTANCE, "shipped bounds (unwidened)"
    )
    result["against_proposed_bounds"] = _verdict(
        graph, PROPOSED, "PROPOSED bounds (CXA- Task 1, not adopted)"
    )
    result["proposed_bounds"] = {
        "node_count": list(PROPOSED.node_count),
        "edge_count": list(PROPOSED.edge_count),
    }

    out = HERE / "mknn_result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    logging.info("wrote %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
