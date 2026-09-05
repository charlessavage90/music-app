"""`LUX-E1` arm B' — rebuild the live map from pinned inputs and compare the sha.

Read-only with respect to anything served. Writes one candidate artifact to
`builder/scratch/` and adopts nothing; moves no default.

Why this exists rather than `artistpath-build build`: the CLI runs
`check_acceptance` BEFORE `serialise`, and `CXA-` Task 1 (`c4cfbb1`)
recalibrated the acceptance bounds for the extended 117k population. A
*correct* rebuild of the 58,838-artist live map is therefore rejected as
"outside bounds [70900, 106400]" and never serialised, so the CLI cannot
produce the sha this eval is defined on. Acceptance governs whether a build is
ADMITTED, not what it CONTAINS, so bypassing it cannot change a byte of the
artifact — which is precisely why the comparison stays valid here.

Run from `builder/`.
"""

import hashlib
import sys
from pathlib import Path

from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import serialise
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.pipeline import build_from_archive

# The live map, from its own manifest sidecar. Never transcribed by hand
# elsewhere; this is the comparison target and the whole point of the eval.
LIVE_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
LIVE_ARTISTS = 58838
LIVE_EDGES = 1315684

DATA = Path("src/artistpath_builder/data")
PINNED_ARCHIVE = Path("scratch/grt-archive-algb.pre-cex-snapshot")
PINNED_PAYLOAD = DATA / "unlistenable_drop_algb_20260805.json"
OUT = Path("scratch/graph-luxe1-armb.bin")


def main() -> int:
    for p in (PINNED_ARCHIVE, PINNED_PAYLOAD):
        if not p.exists():
            print(f"FATAL: missing pinned input {p}", file=sys.stderr)
            return 2

    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,   # ALG-B, explicit per CEX-R5
        cap_strategy="trimmed_union",
        require_fame=True,
        unlistenable_list_path=PINNED_PAYLOAD,
    )
    graph = build_from_archive(
        config, LocalArchive(PINNED_ARCHIVE), ListenBrainzSource(config)
    )
    payload = serialise(graph)
    sha = hashlib.sha256(payload).hexdigest()
    OUT.write_bytes(payload)

    print()
    print(f"artists  built {graph.artist_count:>9,}  live {LIVE_ARTISTS:>9,}  "
          f"{'MATCH' if graph.artist_count == LIVE_ARTISTS else 'DIFFER'}")
    print(f"edges    built {graph.edge_count:>9,}  live {LIVE_EDGES:>9,}  "
          f"{'MATCH' if graph.edge_count == LIVE_EDGES else 'DIFFER'}")
    print(f"bytes    {len(payload):,}")
    print(f"sha256   built {sha}")
    print(f"sha256   live  {LIVE_SHA}")
    print()
    identical = sha == LIVE_SHA
    print("READ: BYTE-IDENTICAL" if identical else "READ: DIFFERENT")
    return 0 if identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
