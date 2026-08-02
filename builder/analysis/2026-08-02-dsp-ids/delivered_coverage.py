"""Deezer/Apple ID coverage over artists the app ACTUALLY DELIVERS on cards.

Population coverage is the wrong denominator: the router does not deliver
artists uniformly. This routes the 120 committed `TAS-` pairs (40 ff / 40 fo /
40 oo, reused rather than redrawn) with PRODUCTION weights and measures
coverage over the interior artists that actually appear as cards.

Two denominators, and they answer different questions:
  UNIQUE      -- of the distinct artists shown, how many have an ID
  TRAVERSALS  -- of the card impressions, how many have an ID
The second is the one a user experiences, because a famous artist shown on
many journeys counts every time.

Read-only. No network. Routing only.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("C:/dev/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-30-coherence-tag-probe"))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_journey  # noqa: E402
from ct_common import ADOPTED  # noqa: E402

HERE = Path(__file__).parent
PAIRS = ROOT / "builder/analysis/2026-07-30-tag-discrimination/tas_pairs.json"
IDS = HERE / "dsp_ids_by_mbid.json"


def main() -> None:
    store = GraphStore.load(ADOPTED)
    cfg = ApiConfig()
    ids = json.loads(IDS.read_text(encoding="utf-8"))
    pairs = json.loads(PAIRS.read_text(encoding="utf-8"))["pairs"]
    print(f"pairs: {len(pairs)}; production weights", flush=True)

    unique_interior: dict[str, set[str]] = {"ff": set(), "fo": set(), "oo": set()}
    traversals: Counter = Counter()
    trav_with_id: Counter = Counter()
    trav_with_deezer: Counter = Counter()
    routed = 0

    for a, b, cls in pairs:
        si = store.id_by_mbid.get(a)
        ti = store.id_by_mbid.get(b)
        if si is None or ti is None:
            continue
        result = find_journey(store, si, ti, [], cfg)
        if result is None:
            continue
        path, _stop = result
        routed += 1
        # Interiors only: the endpoints are the user's own choices, and a
        # wrong clip there is a different (and more obvious) failure.
        for node in path[1:-1]:
            mbid = store.mbids[node]
            unique_interior[cls].add(mbid)
            traversals[cls] += 1
            flags = ids.get(mbid, "")
            if flags:
                trav_with_id[cls] += 1
            if "d" in flags:
                trav_with_deezer[cls] += 1

    print(f"routed {routed}/{len(pairs)} pairs\n", flush=True)

    hdr = (f"{'class':<8}{'uniq':>7}{'uniq+id':>9}{'uniq %':>9}"
           f"{'trav':>8}{'trav+id':>9}{'trav %':>9}{'trav+dzr %':>12}")
    print(hdr)
    print("-" * len(hdr))
    tot_u = tot_ui = 0
    for cls in ("ff", "fo", "oo"):
        u = unique_interior[cls]
        ui = sum(1 for m in u if ids.get(m))
        tot_u += len(u)
        tot_ui += ui
        t = traversals[cls]
        print(f"{cls:<8}{len(u):>7}{ui:>9}{(ui/len(u)*100 if u else 0):>8.1f}%"
              f"{t:>8}{trav_with_id[cls]:>9}"
              f"{(trav_with_id[cls]/t*100 if t else 0):>8.1f}%"
              f"{(trav_with_deezer[cls]/t*100 if t else 0):>11.1f}%")
    t = sum(traversals.values())
    ti_ = sum(trav_with_id.values())
    td_ = sum(trav_with_deezer.values())
    print("-" * len(hdr))
    print(f"{'ALL':<8}{tot_u:>7}{tot_ui:>9}{(tot_ui/tot_u*100 if tot_u else 0):>8.1f}%"
          f"{t:>8}{ti_:>9}{(ti_/t*100 if t else 0):>8.1f}%"
          f"{(td_/t*100 if t else 0):>11.1f}%")

    out = {
        "substrate": str(ADOPTED),
        "pairs_routed": routed,
        "note": "Interiors only. Endpoints excluded -- they are the user's own picks.",
        "by_class": {
            cls: {
                "unique_interior": len(unique_interior[cls]),
                "unique_with_any_id": sum(1 for m in unique_interior[cls] if ids.get(m)),
                "traversals": traversals[cls],
                "traversals_with_any_id": trav_with_id[cls],
                "traversals_with_deezer_id": trav_with_deezer[cls],
            }
            for cls in ("ff", "fo", "oo")
        },
    }
    (HERE / "delivered_coverage.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print("\nwrote delivered_coverage.json")


if __name__ == "__main__":
    main()
