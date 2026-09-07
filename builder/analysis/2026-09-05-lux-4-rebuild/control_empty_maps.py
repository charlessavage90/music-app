"""The control arm: post-LUX-4 code, LUX-4 maps off, must reproduce the served map.

⚠ WHY THIS FILE EXISTS. `L4-T7` step 1 said to reuse
`analysis/2026-09-05-lux-e1-armb/armb_sha.py` as the control and expect
BYTE-IDENTICAL to 43dd82bb. That stopped being possible at `L4-T5`: that script
calls `build_from_archive`, which now wires the LUX-4 maps unconditionally, so
it can never reproduce the pre-LUX-4 bytes again. The plan's factor table names
a control arm with "link/fact maps empty (maps not wired)" -- and once they ARE
wired, no such arm exists, because there is deliberately no config knob to turn
them off (recorded at the `deezer_ids` call site: they change no edge, no score
and no node, so a factor table has nothing to hold constant).

Patching the two loaders is the only remaining way to build the pre-LUX-4
output from post-LUX-4 code, so that is what this does. It is a CONTROL, not a
shipping path: nothing here may ever be used to produce an artifact that is
served.

WHAT IT PROVES, and what `verify.py` proves instead:
  This arm isolates the CODE PATH -- with the new maps empty, every stage from
  `L4-T1` to `L4-T6` still produces exactly the artifact it produced before any
  of them existed. It is evidence about the builder.
  `verify.py` isolates the OUTPUT -- the shipping artifact minus its three new
  keys is byte-identical to the served one. It is evidence about the artifact,
  and it is the stronger of the two.
  They can fail independently, which is the reason to run both on a change that
  ends in a deploy.

Bypasses `check_acceptance` for the same reason `armb_sha.py` does and with the
same safety argument: acceptance governs whether a build is ADMITTED, never what
it CONTAINS, so skipping it cannot change a byte of the comparison. (Since
`L4-T1` the shipped bounds admit this population anyway; the bypass is kept so
this arm stays valid if they are ever recalibrated again.)

Run from `builder/`. ~5 minutes.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from artistpath_builder import pipeline as pipeline_mod
from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import serialise
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

LIVE_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
LIVE_ARTISTS = 58838
LIVE_EDGES = 1315684

DATA = Path("src/artistpath_builder/data")
PINNED_ARCHIVE = Path("scratch/grt-archive-algb.pre-cex-snapshot")
PINNED_PAYLOAD = DATA / "unlistenable_drop_algb_20260805.json"


def main() -> int:
    for p in (PINNED_ARCHIVE, PINNED_PAYLOAD):
        if not p.exists():
            print(f"FATAL: missing pinned input {p}", file=sys.stderr)
            return 2

    # The intervention, and the only one: both LUX-4 loaders return nothing, so
    # `build_graph` receives empty maps, emits empty lists, and `serialise`
    # omits all three keys. Everything else -- archive, drop list, algorithm,
    # cap rule, fame -- is pinned exactly as the live map was built.
    pipeline_mod.load_dsp_links = lambda: ({}, {})
    pipeline_mod.load_artist_facts = lambda: {}

    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,  # ALG-B, explicit per CEX-R5
        cap_strategy="trimmed_union",
        require_fame=True,
        unlistenable_list_path=PINNED_PAYLOAD,
    )
    graph = build_from_archive(
        config, LocalArchive(PINNED_ARCHIVE), ListenBrainzSource(config)
    )

    if graph.spotify_ids or graph.apple_ids or graph.artist_facts:
        print("FATAL: the loaders were not actually patched out", file=sys.stderr)
        return 2

    payload = serialise(graph)
    sha = hashlib.sha256(payload).hexdigest()

    print()
    print(f"artists  built {graph.artist_count:>9,}  live {LIVE_ARTISTS:>9,}")
    print(f"edges    built {graph.edge_count:>9,}  live {LIVE_EDGES:>9,}")
    print(f"sha      built {sha}")
    print(f"         live  {LIVE_SHA}")
    print()
    if sha == LIVE_SHA:
        print("CONTROL PASSED: byte-identical -- L4-T1..T6 reach no part of the graph")
        return 0
    print("CONTROL FAILED: something in L4-T1..T6 changed what a build produces.")
    print("STOP. No later step in L4-T7 is valid until this is explained.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
