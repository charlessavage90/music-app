"""How a journey is generated — ONE module, used by the pre-screen AND by generation.

`LBA-AM6-2` step 6 requires the pre-screen to generate *"exactly as `LBA-AM6-3` will generate
them"*. Putting the ladder in one module both scripts import is what makes that true by
construction rather than by two copies agreeing. Copied from listen 2's `lbl_generate.py`
(`press_key`, `ladder`, `adjacent`), unchanged in behaviour.

Journeys are production `find_journey` under `ApiConfig` defaults. The press rule is
`cre_ladder.victim_key` over the map's OWN fame percentile — imported, not retyped — after the
shipped api modules are imported, so the frozen copy `cre_ladder` puts on `sys.path` can never
shadow them (asserted).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from lal_common import DEPTHS, ROOT, use_api_src

use_api_src()
from artistpath_api.pathfinding import KNOWN, Exclusion, find_journey  # noqa: E402

import artistpath_api.pathfinding as _shipped_pathfinding  # noqa: E402

sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"))
from cre_ladder import victim_key  # noqa: E402

if not Path(_shipped_pathfinding.__file__).resolve().is_relative_to((ROOT / "api" / "src").resolve()):
    raise SystemExit("HARNESS FAULT: artistpath_api.pathfinding is not the shipped module")

MAX_DEPTH = max(DEPTHS)


def press_key(store, raw_fame: list):
    """`victim_key` wants NaN at artists ListenBrainz reported no listeners for (they sort last);
    `fame_lb_pctl` gives those 0.0, so the raw blob is the only source for the mask (`JFX-`)."""
    measured = np.array([np.nan if v is None else 1.0 for v in raw_fame], dtype=np.float64)
    return victim_key(measured * np.asarray(store.fame_lb_pctl, dtype=np.float64), store.pop_raw, store.mbids)


def ladder(store, s: int, t: int, key, cfg) -> dict[int, tuple[list[int], str, list[int]]]:
    """The all-`known` ladder to MAX_DEPTH, keeping the depths the listen presents.

    Each kept depth is (path, kind, the artists pressed before it, in press order). A depth is
    absent when the ladder cannot reach it: no path, or a path with no interior artist to press.
    """
    excludes: list = []
    out: dict[int, tuple[list[int], str, list[int]]] = {}
    for k in range(MAX_DEPTH + 1):
        result = find_journey(store, s, t, excludes, cfg)
        if result is None:
            break
        path, kind = list(result[0]), result[1]
        interior = path[1:-1]
        if k in DEPTHS and interior:
            out[k] = (path, kind, [e.node for e in excludes])
        if not interior:
            break
        excludes = excludes + [Exclusion(node=min(interior, key=key), reason=KNOWN)]
    return out


def adjacent(store, a: int, b: int) -> bool:
    return any(n == b for n, _ in store.neighbours_of(a))
