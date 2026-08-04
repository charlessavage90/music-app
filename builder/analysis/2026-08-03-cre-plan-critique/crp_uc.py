"""CRP-4: UC feasibility, C6 frontier cost, and the zero-agreement block at
over-budget nodes.

Review instrument for the CRE execution-plan critique (2026-08-03). READ ONLY.
Routes over EXISTING committed .bin cells; builds nothing, re-runs no Track B
cell, writes only its own JSON here.

  A  runtime: production-weight find_journey on the 22 cb_pairs famous pairs,
     timed on ALG-E-MK50 (capped reference), ALG-E-UC and ALG-B-UC.  Scales the
     plan's "22 pairs x 21 depths" ladder estimate for the UC cells.
  B  the CRE-C6 1-hop frontier: |path nodes U their neighbours| on each cell,
     which is the per-pair BFS the screen has to walk.
  C  the S2 zero-agreement block: at nodes with degree > 50 in the ALG-E-UC
     union pool, how large is the exactly-zero-agreement set relative to the
     excess that has to be deleted -- i.e. at how many over-budget nodes would
     the MBID tie-break alone decide every deletion under a `strength * a` key.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-cre-plan-critique/crp_uc.py
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B = ROOT / "builder/analysis"
for p in (B / "2026-07-30-tag-discrimination", B / "2026-07-31-release-tag-coverage",
          B / "2026-07-30-coherence-tag-probe", B / "2026-07-30-track-b-cap-selection",
          B / "2026-07-30-fame-proxy-coverage"):
    sys.path.insert(0, str(p))
sys.path.insert(0, str(ROOT / "api/src"))

from artistpath_api.config import ApiConfig            # noqa: E402
from artistpath_api.graph_store import GraphStore      # noqa: E402
from artistpath_api.pathfinding import find_journey    # noqa: E402
from tas_frame_split import five_frames                # noqa: E402

SCRATCH = ROOT / "builder/scratch"
CELLS = SCRATCH / "cb-cells"
PAIRS = B / "2026-07-30-track-b-cap-selection/cb_pairs.json"
FAMOUS = ("ff-top01pct", "ff-top1pct")


def famous_pairs():
    doc = json.loads(PAIRS.read_text(encoding="utf-8"))
    return [tuple(t) for t in doc["triples"] if t[0] in FAMOUS]


def main() -> None:
    pairs = famous_pairs()
    assert len(pairs) == 22
    cfg = ApiConfig()
    out: dict = {"n_pairs": len(pairs)}

    for name, fn in (("ALG-E-MK50", "ALG-E-mutual_knn-k50.bin"),
                     ("ALG-E-UC", "ALG-E-uncapped-none.bin"),
                     ("ALG-B-UC", "ALG-B-uncapped-none.bin")):
        path = CELLS / fn
        if not path.exists():
            continue
        store = GraphStore.load(path)
        idx = {m: i for i, m in enumerate(store.mbids)}
        deg = np.diff(np.asarray(store.offsets)).astype(np.int64)
        present = [(a, b) for _c, a, b in pairs if a in idx and b in idx]
        t0 = time.time()
        lens, frontiers = [], []
        for a, b in present:
            r = find_journey(store, idx[a], idx[b], [], cfg)
            if r is None:
                continue
            p, _kind = r
            lens.append(len(p))
            front = set(p)
            for u in p:
                for v, _s in store.neighbours_of(u):
                    front.add(v)
            frontiers.append(len(front))
        el = time.time() - t0
        out[name] = {
            "nodes": int(store.artist_count),
            "undirected_edges": int(deg.sum() // 2),
            "max_degree": int(deg.max()),
            "mean_degree": float(deg.mean()),
            "pairs_routable": len(present),
            "d0_journeys_seconds_total": round(el, 2),
            "seconds_per_journey": round(el / max(len(present), 1), 3),
            "projected_ladder_seconds_22x21": round(
                el / max(len(present), 1) * 22 * 21, 1),
            "d0_path_len_mean": float(np.mean(lens)) if lens else None,
            "one_hop_frontier_mean": float(np.mean(frontiers)) if frontiers else None,
            "one_hop_frontier_max": int(np.max(frontiers)) if frontiers else None,
        }
        print(f"{name}: {out[name]}", flush=True)

    # ---- C: zero-agreement block at over-budget nodes of the UC union pool ----
    uc = GraphStore.load(CELLS / "ALG-E-uncapped-none.bin")
    W4 = five_frames()["W4"]
    N_ad = 74193  # idf denominator: adopted node count (plan pin 5)
    labels = [W4.get(m, set()) for m in uc.mbids]
    dfc: Counter = Counter()
    for s in labels:
        for lab in s:
            dfc[lab] += 1
    idf = {lab: math.log(N_ad / c) for lab, c in dfc.items()}

    def wag(a, b):
        if not a or not b:
            return None
        wu = sum(idf.get(x, 0.0) for x in (a | b))
        if wu <= 0:
            return None
        return sum(idf.get(x, 0.0) for x in (a & b)) / wu

    offs = np.asarray(uc.offsets)
    nbrs = np.asarray(uc.neighbours)
    degs = np.diff(offs).astype(np.int64)
    over = np.flatnonzero(degs > 50)
    rows = []
    for u in over.tolist():
        lo, hi = int(offs[u]), int(offs[u + 1])
        z = 0
        for pos in range(lo, hi):
            a = wag(labels[u], labels[int(nbrs[pos])])
            if a == 0.0:
                z += 1
        rows.append((int(degs[u]) - 50, z))
    if rows:
        exc = np.array([r[0] for r in rows])
        zz = np.array([r[1] for r in rows])
        out["over_budget_zero_block_UC_pool"] = {
            "nodes_over_50": int(len(rows)),
            "median_excess": float(np.median(exc)),
            "median_zero_agreement_edges": float(np.median(zz)),
            "share_nodes_where_zero_block_ge_excess": float((zz >= exc).mean()),
            "note": "where the zero block is at least as large as the excess, "
                    "EVERY deletion at that node is decided by the MBID "
                    "tie-break under a `strength * agreement` key, because all "
                    "those keys are exactly 0.0. UC's pool is a superset of "
                    "TU's top-50-union pool, so this is indicative, not exact.",
        }
        print(out["over_budget_zero_block_UC_pool"], flush=True)

    (HERE / "crp_uc.json").write_text(json.dumps(out, indent=1, sort_keys=True),
                                      encoding="utf-8")
    print("\nwrote crp_uc.json")


if __name__ == "__main__":
    main()
