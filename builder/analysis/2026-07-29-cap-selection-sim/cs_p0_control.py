"""CS-P0 -- the control's degree and downward-edge distribution, from the SHIPPED artifact.

Read-only. Asserts the artifact sha256 (TB-G3 / DD-G3 discipline).

WHY THIS RUNS BEFORE THE PRE-REGISTRATION. Every figure here is a property of the
artifact the app is running today, not a result of the cap-selection experiment. The
pre-registration needs the control's real numbers to set effect sizes against
(CLAUDE.md: "every gate and branch trigger needs its own effect size"). Fixing a
threshold like "max degree <= 250" without knowing the control is 50 or 5,000 is how a
gate ends up unable to tell its finding from noise. No arm runs here; nothing in this
script touches the archive or builds anything.

Three questions:

  (1) THE BOUND, in control currency. Degree distribution under production's rule
      (mutual k-NN, similarity rank, k = 50). This is the number MKS-5b's "demonstrate
      the degree bound by simulation" is a demonstration RELATIVE TO.
  (2) DD-F1, restated in this script's own coordinates. For the most popular artists,
      how many of their edges point at artists outside the top popularity decile?
      DD-F1 says zero for superstar endpoints; this reproduces it independently so the
      simulation's arms have a control to move.
  (3) STRANDING (MKS-3 / BTF-5 currency). Share of artists with <= 2 connections --
      the quantity a non-reciprocal rule is expected to IMPROVE while it risks
      making (1) worse. Both directions matter, so both get measured.

CURRENCY. `pop_raw` is the stored 0-1 log-scaled value and is NOT a percentile
(CLAUDE.md; log SS2.12). Every decile statement below is computed from an explicit
`pop_pctl` derived here by ranking; nothing reads a decile off `pop_raw`.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/cs_p0_control.py
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
OUT = HERE / "cs_p0_control.json"

# The named superstars DD-F1 and the 2026-07-28 queue entry both quote. Kept as a
# named set so the arms can report the SAME artists rather than a re-derived top-N,
# which would move between arms and make the comparison uncontrolled.
SUPERSTARS = (
    "Radiohead",
    "The Beatles",
    "Metallica",
    "Muse",
    "Coldplay",
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile_ranks(values: np.ndarray) -> np.ndarray:
    """Rank-based percentile in [0, 1]. Ties take their average rank.

    Explicitly NOT `pop_raw` rescaled: the log scale compresses the head, so equal
    steps in the value are wildly unequal steps in rank (log SS2.12).
    """
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    # average ranks within tie groups
    sorted_values = values[order]
    start = 0
    for end in range(1, len(sorted_values) + 1):
        if end == len(sorted_values) or sorted_values[end] != sorted_values[start]:
            if end - start > 1:
                ranks[order[start:end]] = ranks[order[start:end]].mean()
            start = end
    return ranks / max(1, len(values) - 1)


def main() -> int:
    if not GRAPH.is_file():
        print(f"MISSING ARTIFACT: {GRAPH}", file=sys.stderr)
        return 2
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print(f"ARTIFACT MISMATCH\n  expected {EXPECT}\n  actual   {actual}", file=sys.stderr)
        return 2

    from artistpath_api.graph_store import GraphStore

    graph = GraphStore.load(GRAPH)
    n = graph.artist_count
    degrees = np.diff(graph.offsets).astype(np.int64)
    pop_raw = np.asarray(graph.pop_raw, dtype=np.float64)
    pop_pctl = percentile_ranks(pop_raw)

    top_decile = pop_pctl >= 0.90
    report: dict[str, object] = {
        "artifact": {"path": str(GRAPH), "sha256": actual, "artists": n,
                     "edges": int(graph.neighbours.size)},
        "arm": "CS-0 (production control: mutual k-NN, similarity rank, k = 50)",
    }

    # (1) THE BOUND
    report["degree"] = {
        "max": int(degrees.max()),
        "p99": float(np.percentile(degrees, 99)),
        "median": float(np.median(degrees)),
        "mean": float(degrees.mean()),
        "configured_k": 50,
        "count_at_or_above_k": int((degrees >= 50).sum()),
        "count_above_k": int((degrees > 50).sum()),
    }

    # (3) STRANDING
    report["stranding"] = {
        "degree_le_2": int((degrees <= 2).sum()),
        "degree_le_2_share": float((degrees <= 2).mean()),
        "degree_eq_1": int((degrees == 1).sum()),
    }

    # (2) DD-F1 -- downward edges out of the top decile
    names = list(graph.names)
    by_name: dict[str, int] = {}
    for i, name in enumerate(names):
        by_name.setdefault(name, i)

    def downward_profile(node: int) -> dict[str, object]:
        start, end = int(graph.offsets[node]), int(graph.offsets[node + 1])
        nbr = graph.neighbours[start:end].astype(np.int64)
        nbr_pctl = pop_pctl[nbr]
        return {
            "name": names[node],
            "degree": int(end - start),
            "pop_pctl": round(float(pop_pctl[node]), 6),
            "neighbours_below_top_decile": int((nbr_pctl < 0.90).sum()),
            "neighbours_below_median": int((nbr_pctl < 0.50).sum()),
            "min_neighbour_pctl": round(float(nbr_pctl.min()), 6) if len(nbr) else None,
        }

    report["superstars"] = []
    for name in SUPERSTARS:
        node = by_name.get(name)
        if node is None:
            report["superstars"].append({"name": name, "found": False})
            continue
        report["superstars"].append(downward_profile(node))

    # Population-level version of the same question, so the five named artists are
    # not the only evidence. For every top-decile artist: how many downward edges?
    top_ids = np.flatnonzero(top_decile)
    downward_counts = np.empty(len(top_ids), dtype=np.int64)
    for j, node in enumerate(top_ids):
        start, end = int(graph.offsets[node]), int(graph.offsets[node + 1])
        nbr = graph.neighbours[start:end].astype(np.int64)
        downward_counts[j] = int((pop_pctl[nbr] < 0.90).sum())
    report["top_decile_population"] = {
        "artists": int(len(top_ids)),
        "with_zero_downward_edges": int((downward_counts == 0).sum()),
        "with_zero_downward_edges_share": float((downward_counts == 0).mean()),
        "mean_downward_edges": float(downward_counts.mean()),
        "median_downward_edges": float(np.median(downward_counts)),
    }

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
