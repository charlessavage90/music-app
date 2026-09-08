"""`DCF-` provenance — is `grt-archive-algb` really the tree that built the
extended map, and is the `CXR` added set really new to it?

Written as a separate script so `dcf_ceiling_sweep.py` stays exactly as it ran.

Q4 states the provenance ("the extended archive `grt-archive-algb` (117,302
payloads), the archive `graph-cxa-adopted.bin` was built from") and the sweep
depends on it entirely: the wrong archive would measure nothing. The manifest
sidecars record the build config but NOT the archive directory, so provenance
cannot be read off them — it has to be demonstrated. This demonstrates it by
membership, which needs no trust in either document:

  1. every node of `graph-cxa-adopted.bin` has a payload in the extended tree
     (if any were missing, that tree did not build it);
  2. almost none of the `CXR` added set has a payload in the `.pre-cex-snapshot`
     sibling (if they did, they were not "added by the extension").

Both are file-existence tests over ~118k paths and take seconds.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-07-degree-ceiling-falsifier/dcf_provenance.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"
sys.path.insert(0, str((HERE.parent.parent.parent / "api" / "src").resolve()))

from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM  # noqa: E402

SUBTREE = Path("similar") / "listenbrainz" / CANDIDATE_ALGORITHM
EXTENDED = SCRATCH / "grt-archive-algb" / SUBTREE
PRE_CEX = SCRATCH / "grt-archive-algb.pre-cex-snapshot" / SUBTREE


def main() -> int:
    old = GraphStore.load(SCRATCH / "graph-msw-tu50.bin")
    new = GraphStore.load(SCRATCH / "graph-cxa-adopted.bin")
    old_set = set(old.mbids)
    added = [m for m in new.mbids if m not in old_set]

    result = {
        "extended_tree": str(EXTENDED),
        "pre_cex_tree": str(PRE_CEX),
        "cxa_nodes": len(new.mbids),
        "cxa_nodes_with_a_payload_in_the_extended_tree": sum(
            1 for m in new.mbids if (EXTENDED / f"{m}.json").is_file()
        ),
        "added": len(added),
        "added_with_a_payload_in_the_extended_tree": sum(
            1 for m in added if (EXTENDED / f"{m}.json").is_file()
        ),
        # Expected to be small but NOT necessarily zero: an artist can be
        # crawled and still be absent from the served map (a drop list, or the
        # largest-component prune), and would then read as "added" on the next
        # build without the crawl having discovered them.
        "added_with_a_payload_in_the_pre_cex_tree": sum(
            1 for m in added if (PRE_CEX / f"{m}.json").is_file()
        ),
    }
    result["every_cxa_node_is_in_the_extended_tree"] = (
        result["cxa_nodes_with_a_payload_in_the_extended_tree"] == result["cxa_nodes"]
    )
    (HERE / "dcf_provenance.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    for key, value in result.items():
        print(f"{key}: {value}")
    return 0 if result["every_cxa_node_is_in_the_extended_tree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
