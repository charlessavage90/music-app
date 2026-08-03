"""CRP-5: d0 stop kinds per cell, and the guard-vs-journey divergence.

Review instrument for the CRE execution-plan critique (2026-08-03). READ ONLY.

  A  how many of the 22 cb_pairs famous pairs are directly adjacent at d0 in
     each committed cell, and of those how many have NO detour
     (STOP_ADJACENT_ONLY).  This is the population exposed to the difference
     between the mirror's guard_min_intermediary and the plan's journey().
  B  the same pairs under the mirror's guard (find_path_mirror with
     guard_min_intermediary=True), which returns None where journey() returns
     an adjacent_only two-card path -- i.e. the pairs that would vanish from
     the record, and then be deleted from EVERY compared cell by the uniform
     drop rule.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-cre-plan-critique/crp_kinds.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api/src"))
sys.path.insert(0, str(ROOT / "builder/analysis/2026-07-23-track2-sweep"))

from artistpath_api.config import ApiConfig          # noqa: E402
from artistpath_api.graph_store import GraphStore    # noqa: E402
from artistpath_api.pathfinding import find_journey  # noqa: E402
from mirror import MirrorContext, SweepConfig, find_path_mirror  # noqa: E402

SCRATCH = ROOT / "builder/scratch"
CELLS = SCRATCH / "cb-cells"
PAIRS = (ROOT / "builder/analysis/2026-07-30-track-b-cap-selection/cb_pairs.json")
FAMOUS = ("ff-top01pct", "ff-top1pct")

WANT = {
    "adopted": SCRATCH / "graph-t15-tiebreakfix.bin",
    "ALG-E-MK50": CELLS / "ALG-E-mutual_knn-k50.bin",
    "ALG-E-MK100": CELLS / "ALG-E-mutual_knn-k100.bin",
    "ALG-E-TUw-50-50": CELLS / "ALG-E-trimmed_union-d50-j50.bin",
    "ALG-E-UC": CELLS / "ALG-E-uncapped-none.bin",
    "ALG-B-MK50": CELLS / "ALG-B-mutual_knn-k50.bin",
    "ALG-B-MK100": CELLS / "ALG-B-mutual_knn-k100.bin",
    "ALG-B-TUw-50-50": CELLS / "ALG-B-trimmed_union-d50-j50.bin",
    "ALG-B-UC": CELLS / "ALG-B-uncapped-none.bin",
}


def main() -> None:
    doc = json.loads(PAIRS.read_text(encoding="utf-8"))
    pairs = [tuple(t) for t in doc["triples"] if t[0] in FAMOUS]
    cfg_api = ApiConfig()
    guard_cfg = SweepConfig.production().with_(guard_min_intermediary=True)
    out: dict = {}
    for name, path in WANT.items():
        if not path.exists():
            continue
        store = GraphStore.load(path)
        idx = {m: i for i, m in enumerate(store.mbids)}
        ctx = MirrorContext.build(store)
        kinds: Counter = Counter()
        guard_none = 0
        classes_adjacent: Counter = Counter()
        missing = 0
        for cls, a, b in pairs:
            if a not in idx or b not in idx:
                missing += 1
                continue
            s, t = idx[a], idx[b]
            r = find_journey(store, s, t, [], cfg_api)
            if r is None:
                kinds["none"] += 1
                continue
            _p, kind = r
            kinds[kind] += 1
            if kind in ("forced", "adjacent_only"):
                classes_adjacent[cls] += 1
            gp = find_path_mirror(store, s, t, [], guard_cfg, ctx)
            if gp is None:
                guard_none += 1
        out[name] = {
            "nodes": int(store.artist_count),
            "pairs_present": len(pairs) - missing,
            "endpoints_missing_pairs": missing,
            "d0_stop_kinds": dict(kinds),
            "adjacent_at_d0_by_class": dict(classes_adjacent),
            "pairs_lost_under_mirror_guard_true": guard_none,
        }
        print(name, out[name], flush=True)
    (HERE / "crp_kinds.json").write_text(json.dumps(out, indent=1, sort_keys=True),
                                         encoding="utf-8")
    print("\nwrote crp_kinds.json")


if __name__ == "__main__":
    main()
