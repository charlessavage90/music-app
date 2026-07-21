"""Per-artifact structural diagnostics.

Every structural defect this project has found was invisible in the summary
output that existed at the time — the clip ceiling, the cap asymmetry, the
confounded artifact provenance. All of them fall straight out of these numbers.

`nodes_over_cap` in particular makes the cap defect legible: the current output
reports only post-symmetrisation degree, in which a configured cap of 50 and an
observed maximum of 11,243 sit side by side without the contradiction ever
surfacing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402


def artifact_diagnostics(store: GraphStore, cap: int) -> dict:
    """Structural summary of one built artifact."""
    degrees = np.diff(store.offsets)
    pop = np.asarray(store.popularity, dtype=np.float64)
    scores = np.asarray(store.scores, dtype=np.float64)

    saturated = np.isclose(scores, 1.0)
    saturated_dsts = store.neighbours[saturated]

    with np.errstate(divide="ignore", invalid="ignore"):
        log_deg = np.log1p(degrees.astype(np.float64))
        edge_src_degrees = np.repeat(log_deg, degrees)
        corr = (
            float(np.corrcoef(scores, edge_src_degrees)[0, 1])
            if scores.size > 1
            else 0.0
        )

    return {
        "artists": int(store.artist_count),
        "edges": int(scores.size),
        "cap": cap,
        "nodes_over_cap": int((degrees > cap).sum()),
        "max_degree": int(degrees.max()) if degrees.size else 0,
        "degree_p50": float(np.percentile(degrees, 50)) if degrees.size else 0.0,
        "degree_p99": float(np.percentile(degrees, 99)) if degrees.size else 0.0,
        "pop_p25": float(np.percentile(pop, 25)) if pop.size else 0.0,
        "pop_p50": float(np.percentile(pop, 50)) if pop.size else 0.0,
        "pop_p75": float(np.percentile(pop, 75)) if pop.size else 0.0,
        "saturated_edges": int(saturated.sum()),
        "saturated_dst_median_degree": (
            float(np.median(degrees[saturated_dsts])) if saturated_dsts.size else 0.0
        ),
        "corr_score_log_degree": corr if np.isfinite(corr) else 0.0,
    }
