"""The frozen no-release-tail drop list (owner decision 2026-08-01, NEXT.md).

Keep a release-less artist only where a commercial-DSP link exists AND a clip
resolves. 7,035 of the 7,686 no-release tail are dropped; 651 are kept. The
rule is ADOPTED — applied here, never re-derived.

The clip half is a **2026-08-01 snapshot** and is deliberately frozen as data.
Re-resolving it at build time would break two hard rules at once:
`build_from_archive` never touches the network, and spec §9 requires
byte-identical output for identical input — a live Deezer lookup would make two
builds of one archive disagree. Refreshing the list is a deliberate act with
its own decision, not a silent build-time behaviour.

The list ships inside the package rather than being read from
`builder/analysis/`, which holds frozen probe code that is not installed with
the builder. `data/no_release_drop_20260801.json` is a verbatim copy of the
probe's output; `DROP_LIST_SHA256` pins it to the value recorded in NEXT.md and
the 2026-08-01 handoff, and the test suite checks it.
"""

from __future__ import annotations

import json

from functools import lru_cache
from pathlib import Path

# sha256 of json.dumps(drop_mbids, sort_keys=True) over the sorted MBIDs, as
# recorded in NEXT.md and docs/superpowers/2026-08-01-HANDOFF-no-release-tail.md.
DROP_LIST_SHA256 = "d876c7baec3626094251503f425f3a5a571e8e0d74ac37bf10e6c37bfb7ac1d3"

DROP_LIST_PATH = Path(__file__).parent / "data" / "no_release_drop_20260801.json"


@lru_cache(maxsize=1)
def load_drop_mbids() -> frozenset[str]:
    """MBIDs the adopted rule removes from every build."""
    payload = json.loads(DROP_LIST_PATH.read_text(encoding="utf-8"))
    return frozenset(payload["drop_mbids"])
