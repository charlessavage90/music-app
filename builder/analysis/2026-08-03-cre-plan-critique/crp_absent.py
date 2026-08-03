"""CRP-2: what the snapshot-absent nodes ARE, and the multiplicative deletion key.

Review instrument for the CRE execution-plan critique (2026-08-03). READ ONLY.

Part A -- is the union snapshot exactly (adopted node set) U (ALG-B-MK50 node
set)?  If so, a node that a union/uncapped cell keeps but both MK50 builds
stranded was never in the fetch population at all: "absent" is a population
artifact, not "no recorded listeners".  Plan pin 2's justification turns on
which of the two it is.

Part B -- structural profile of the absent nodes on the ALG-E TU cell (degree,
in-graph popularity rank), i.e. how reachable the router finds them.

Part C -- plan pin 1's degeneracy claim: "a constant multiplier preserves the
order and the tie rule".  Tested in IEEE double on the adopted artifact's own
edge scores at c = GLOBAL_NEUTRAL_FALLBACK = 0.15, and on the worst case
(adjacent doubles).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-cre-plan-critique/crp_absent.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FAME = ROOT / "builder/analysis/2026-08-02-fame-instrument"
sys.path.insert(0, str(ROOT / "api/src"))

SCRATCH = ROOT / "builder/scratch"
ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
CELLS = SCRATCH / "cb-cells"
SNAPSHOT = FAME / "fi_union_snapshot.json"


def store_of(path: Path):
    from artistpath_api.graph_store import GraphStore

    return GraphStore.load(path)


def main() -> None:
    raw = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    snap = set(raw)

    adopted = store_of(ADOPTED)
    algb50 = store_of(CELLS / "ALG-B-mutual_knn-k50.bin")
    a_set, b_set = set(adopted.mbids), set(algb50.mbids)
    union = a_set | b_set

    out: dict = {
        "snapshot_keys": len(snap),
        "adopted_nodes": len(a_set),
        "algb_mk50_nodes": len(b_set),
        "adopted_union_algb": len(union),
        "snapshot_equals_adopted_union_algb_mk50": snap == union,
        "in_snapshot_not_in_union": len(snap - union),
        "in_union_not_in_snapshot": len(union - snap),
    }
    print(json.dumps({k: out[k] for k in out}, indent=1))

    # ---- Part B: the absent nodes on the ALG-E TU cell ----
    tu = store_of(CELLS / "ALG-E-trimmed_union-d50-j50.bin")
    deg = np.diff(np.asarray(tu.offsets))
    pop = np.asarray(tu.pop_raw, dtype=np.float64)
    absent_idx = np.array([i for i, m in enumerate(tu.mbids) if m not in snap],
                          dtype=np.int64)
    present_idx = np.array([i for i in range(len(tu.mbids))
                            if i not in set(absent_idx.tolist())], dtype=np.int64)
    out["ALG-E-TU_absent_profile"] = {
        "n_absent": int(len(absent_idx)),
        "n_nodes": int(len(tu.mbids)),
        "absent_median_degree": float(np.median(deg[absent_idx])),
        "present_median_degree": float(np.median(deg[present_idx])),
        "absent_max_degree": int(deg[absent_idx].max()),
        "absent_median_pop_raw": float(np.median(pop[absent_idx])),
        "present_median_pop_raw": float(np.median(pop[present_idx])),
        "absent_share_of_edge_endpoints": float(
            deg[absent_idx].sum() / deg.sum()),
    }
    print("\nALG-E-TU absent-node profile:",
          json.dumps(out["ALG-E-TU_absent_profile"], indent=1))

    # ---- Part C: does x -> fl(x * c) preserve strict order? ----
    c = 0.15  # tas_common.GLOBAL_NEUTRAL_FALLBACK
    scores = np.unique(np.asarray(adopted.scores, dtype=np.float64))
    prod = scores * c
    collapses = int((np.diff(prod) == 0.0).sum())
    inversions = int((np.diff(prod) < 0.0).sum())

    # worst case: adjacent doubles across a decade of magnitudes
    worst_collapse = 0
    tested = 0
    rng = np.random.default_rng(20260803)
    base = rng.uniform(1e-6, 1.0, size=200_000)
    nxt = np.nextafter(base, np.inf)
    tested = len(base)
    worst_collapse = int(((base * c) == (nxt * c)).sum())

    out["multiplicative_key_fp"] = {
        "constant": c,
        "distinct_artifact_scores": int(len(scores)),
        "collapses_among_distinct_artifact_scores": collapses,
        "order_inversions": inversions,
        "adjacent_double_pairs_tested": tested,
        "adjacent_double_pairs_that_collapse_at_c": worst_collapse,
        "adjacent_double_collapse_rate": worst_collapse / tested,
        "note": "x -> fl(x*c) is monotone non-decreasing for c > 0, so an "
                "inversion is impossible; a COLLAPSE of two distinct values "
                "is possible and its rate is measured on adjacent doubles.",
    }
    print("\nmultiplicative key (c=0.15):",
          json.dumps(out["multiplicative_key_fp"], indent=1))

    (HERE / "crp_absent.json").write_text(
        json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print("\nwrote crp_absent.json")


if __name__ == "__main__":
    main()
