"""CS-P0b -- WHERE the downward-edge defect actually lives, by popularity band.

Read-only. Asserts the artifact sha256. No arm runs here.

WHY THIS EXISTS. CS-P0 reproduced DD-F1 on the five named superstars (zero neighbours
below the top decile, every one) and simultaneously found that only 12.2% of top-decile
artists have zero downward edges -- mean 8.6, median 6. Those two facts are both true
and point in opposite directions, so "famous artists have no downward edges" is either
imprecise or wrong depending on where the line is drawn.

That matters BEFORE any arm is designed, not after: an intervention aimed at the top
decile is aimed at a population that is 87.8% not-defective, and a cap-selection change
could move that population a long way while leaving the superstars -- the pair class
REQ-33..REQ-37 and the owner's ruling are actually about -- exactly where they are.
Naming the target population wrongly is the "uncontrolled variable" failure in its
population form.

So: downward-edge counts as a function of popularity percentile, banded, plus the
same curve for the strictest reading (edges below the artist's OWN percentile).

CURRENCY. `pop_pctl` is computed here by ranking; `pop_raw` is never read as a rank.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/cs_p0b_gradient.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
OUT = HERE / "cs_p0b_gradient.json"

# Upper edge of each band, in percentile. Deliberately finer at the top, because
# CS-P0 located the disagreement there.
BANDS = (
    (0.900, 0.990, "top decile, below top 1%"),
    (0.990, 0.999, "top 1%, below top 0.1%"),
    (0.999, 0.9999, "top 0.1%, below top 0.01%"),
    (0.9999, 1.0001, "top 0.01%"),
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    sorted_values = values[order]
    start = 0
    for end in range(1, len(sorted_values) + 1):
        if end == len(sorted_values) or sorted_values[end] != sorted_values[start]:
            if end - start > 1:
                ranks[order[start:end]] = ranks[order[start:end]].mean()
            start = end
    return ranks / max(1, len(values) - 1)


def main() -> int:
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print(f"ARTIFACT MISMATCH\n  expected {EXPECT}\n  actual {actual}", file=sys.stderr)
        return 2

    from artistpath_api.graph_store import GraphStore

    graph = GraphStore.load(GRAPH)
    pop_pctl = percentile_ranks(np.asarray(graph.pop_raw, dtype=np.float64))
    offsets = graph.offsets
    neighbours = graph.neighbours

    rows = []
    for low, high, label in BANDS:
        ids = np.flatnonzero((pop_pctl >= low) & (pop_pctl < high))
        if len(ids) == 0:
            rows.append({"band": label, "artists": 0})
            continue
        below_decile = np.empty(len(ids), dtype=np.int64)
        below_own = np.empty(len(ids), dtype=np.int64)
        below_median = np.empty(len(ids), dtype=np.int64)
        degree = np.empty(len(ids), dtype=np.int64)
        for j, node in enumerate(ids):
            start, end = int(offsets[node]), int(offsets[node + 1])
            nbr_pctl = pop_pctl[neighbours[start:end].astype(np.int64)]
            degree[j] = end - start
            below_decile[j] = int((nbr_pctl < 0.90).sum())
            below_own[j] = int((nbr_pctl < pop_pctl[node]).sum())
            below_median[j] = int((nbr_pctl < 0.50).sum())
        rows.append({
            "band": label,
            "pctl_range": [low, min(high, 1.0)],
            "artists": int(len(ids)),
            "mean_degree": round(float(degree.mean()), 3),
            "zero_downward_share": round(float((below_decile == 0).mean()), 6),
            "mean_edges_below_top_decile": round(float(below_decile.mean()), 3),
            "median_edges_below_top_decile": float(np.median(below_decile)),
            "mean_edges_below_median": round(float(below_median.mean()), 3),
            "mean_edges_below_own_pctl": round(float(below_own.mean()), 3),
        })

    report = {
        "artifact": {"sha256": actual, "artists": int(graph.artist_count)},
        "arm": "CS-0 (production control)",
        "note": "Bands are disjoint. 'downward' = neighbour below the 90th percentile.",
        "bands": rows,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
