"""CB-2: structural metrics for one built cell.

Governing plan: docs/superpowers/plans/2026-07-30-graph-rebuild-track-b.md

Read-only over emitted artifacts. Computes no criterion and makes no
comparison beyond the descriptive overlap columns -- CB-4 fixes the criteria
and CB-6 reads them, so scoring can be re-run and reviewed without rebuilding.

THREE LESSONS FROM PRIOR TRACKS ARE BUILT IN RATHER THAN REMEMBERED

  GRT-P4  Stranding carries BOTH denominators. The two archives' BFS frontiers
          diverge (ALG-B never crawled 31% of the adopted artifact's artists),
          so "absent from the component" against the adopted frame conflates
          NEVER CRAWLED with STRANDED. That draft reported 55.8% where the
          real figure was 7.0%.
  GRT-P1  Component exclusion carries an ABSOLUTE DIFFERENCE as well as a
          ratio. A ratio against a zero baseline is undefined and returned
          "not decisive" in every band at trial scale.
  §2.6    Currency in the name. `top1pct_degree_frac` is already taken -- it is
          a PATH metric (fraction of interior nodes in the frozen
          top-1%-by-degree set) and lives in cb_paths.py. The graph-level
          concentration measure here is `top1pct_degree_mass_frac`, a
          different quantity with a different name on purpose.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-track-b-cap-selection/cb_metrics.py --gate
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path

import numpy as np

from artistpath_builder.acceptance import PRODUCTION_ACCEPTANCE as ACC
from artistpath_builder.acceptance import ArtifactRejected, check_acceptance
from artistpath_builder.artifact import deserialise

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"

ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

ALG_B_KEY = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)
ARCHIVE_RESPONSES = {
    "ALG-E": SCRATCH / "graph-archive" / "similar" / "listenbrainz",
    "ALG-B": SCRATCH / "grt-archive-algb" / "similar" / "listenbrainz" / ALG_B_KEY,
}

# The RC-A2 / GRT-P2 artists: three collapse under ALG-B at k=50 and fall out
# of the sample the degree floor inspects. Radiohead is the control that does
# not collapse; The Beatles anchors the very top.
TRACERS = ("R.E.M.", "Pixies", "The xx", "PJ Harvey", "Radiohead", "The Beatles")

BANDS = (
    ("top 0.1%", 0.999, 1.0001),
    ("top 1%", 0.99, 0.999),
    ("top 10%", 0.90, 0.99),
    ("upper half", 0.50, 0.90),
    ("lower half", 0.0, 0.50),
)

# Reference builds, for the instrument gate. Figures published in
# docs/superpowers/2026-07-29-graph-rebuild-track-a-execution-log.md §7b;
# cited here as the gate's expectations, not restated as findings.
REFERENCE_CELLS = {
    "ALG-E": {
        "path": SCRATCH / "graph-dropnameless-verify.bin",
        "pre_prune": 74_957,
        "expect": {
            "exclusion_rate": 0.0107,
            "tracer_degrees": {"R.E.M.": 47, "Pixies": 41, "The xx": 35, "Radiohead": 50},
            "lower_half_stranded": 0.0008,
        },
    },
    "ALG-B": {
        "path": SCRATCH / "graph-algb-full.bin",
        "pre_prune": 74_966,
        "expect": {
            "exclusion_rate": 0.0867,
            "tracer_degrees": {"R.E.M.": 6, "Pixies": 3, "The xx": 1, "Radiohead": 48},
            "lower_half_stranded": 0.0700,
        },
    },
}


def fame_frame() -> dict[str, float]:
    """Percentile RANK over the adopted artifact -- the fixed frame.

    Band membership must not move with the thing being measured, so every cell
    is scored against the adopted graph's ranking rather than its own. Note the
    currency: this is a PERCENTILE, and `pop_raw` is a VALUE. §2.12.
    """
    payload = ADOPTED.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != ADOPTED_SHA:
        raise SystemExit(f"adopted artifact mismatch: {actual} != {ADOPTED_SHA}")
    graph = deserialise(payload)
    pop = np.asarray(graph.pop_raw, dtype=np.float64)
    order = pop.argsort(kind="stable")
    pctl = np.empty_like(pop)
    pctl[order] = np.arange(len(pop)) / (len(pop) - 1)
    return {m: float(pctl[i]) for i, m in enumerate(graph.mbids)}


def crawled_mbids(archive: str) -> set[str]:
    """Artists whose OWN response this archive holds."""
    return {p.stem for p in ARCHIVE_RESPONSES[archive].glob("*.json")}


def band_of(p: float) -> str | None:
    for name, lo, hi in BANDS:
        if lo <= p < hi:
            return name
    return None


def top_degree_node_set(graph, fraction: float = 0.01) -> set[str]:
    """The top-`fraction`-by-DEGREE mbids of this graph. Degree, not fame."""
    degrees = np.diff(graph.offsets).astype(np.int64)
    cut = max(1, int(round(len(degrees) * fraction)))
    order = np.argsort(-degrees, kind="stable")[:cut]
    return {graph.mbids[int(i)] for i in order}


def score_cell(graph, frame: dict[str, float], crawled: set[str],
               pre_prune: int,
               production_top_degree: set[str] | None = None) -> dict:
    """Every structural quantity for one cell. No criterion, no verdict."""
    degrees = np.diff(graph.offsets).astype(np.int64)
    pop = np.asarray(graph.pop_raw, dtype=np.float64)
    order = np.argsort(-pop, kind="stable")
    present = set(graph.mbids)
    deg_list = degrees.tolist()

    # --- degree profile / hub structure ---------------------------------
    total_degree = int(degrees.sum())
    cut = max(1, int(round(len(degrees) * 0.01)))
    top_by_degree = np.argsort(-degrees, kind="stable")[:cut]
    this_top_set = {graph.mbids[int(i)] for i in top_by_degree}

    hub = {
        "mean_degree": round(float(degrees.mean()), 3) if len(degrees) else 0.0,
        "median_degree": float(statistics.median(deg_list)) if deg_list else 0.0,
        "p99_degree": int(np.percentile(degrees, 99)) if len(degrees) else 0,
        "max_degree": int(degrees.max()) if len(degrees) else 0,
        # Share of all edge ENDPOINTS held by the top 1% of nodes BY DEGREE.
        # Distinct from PathMetrics.top1pct_degree_frac, which counts path
        # interiors -- different quantity, different name (§2.6).
        "top1pct_degree_mass_frac": round(
            float(degrees[top_by_degree].sum()) / total_degree, 5
        ) if total_degree else 0.0,
        "degree_le_1_share": round(
            sum(1 for d in deg_list if d <= 1) / max(1, len(deg_list)), 5
        ),
        "degree_below_acceptance_floor_share": round(
            sum(1 for d in deg_list if d < ACC.famous_min_degree_floor)
            / max(1, len(deg_list)), 5
        ),
    }
    if production_top_degree is not None:
        overlap = len(this_top_set & production_top_degree)
        hub["top_degree_node_set_overlap_with_production"] = round(
            overlap / max(1, len(production_top_degree)), 5
        )

    # --- component exclusion: ABSOLUTE and ratio (GRT-P1) ----------------
    excluded = pre_prune - graph.artist_count
    exclusion = {
        "pre_prune": pre_prune,
        "kept": graph.artist_count,
        "excluded_absolute": excluded,
        "exclusion_rate": round(excluded / pre_prune, 5) if pre_prune else 0.0,
    }

    # --- stranding by band, BOTH denominators (GRT-P4) -------------------
    members: dict[str, list[str]] = {name: [] for name, _lo, _hi in BANDS}
    for mbid, p in frame.items():
        band = band_of(p)
        if band:
            members[band].append(mbid)

    per_band = {}
    for name, _lo, _hi in BANDS:
        ms = members[name]
        in_arm = [m for m in ms if m in crawled]
        stranded = [m for m in in_arm if m not in present]
        per_band[name] = {
            "in_adopted_frame": len(ms),
            "crawled_by_this_archive": len(in_arm),
            "never_crawled": len(ms) - len(in_arm),
            "crawled_then_stranded": len(stranded),
            "stranded_share_of_crawled": round(len(stranded) / max(1, len(in_arm)), 5),
            "absent_share_of_frame": round(
                (len(ms) - len(in_arm) + len(stranded)) / max(1, len(ms)), 5
            ),
        }

    # --- tracers ---------------------------------------------------------
    name_to_index = {}
    for i, nm in enumerate(graph.names):
        name_to_index.setdefault(nm, i)
    rank_of = {int(node): r for r, node in enumerate(order.tolist())}

    tracers = {}
    for nm in TRACERS:
        i = name_to_index.get(nm)
        if i is None:
            tracers[nm] = {"in_component": False}
            continue
        rank = rank_of[i]
        tracers[nm] = {
            "in_component": True,
            "degree": int(degrees[i]),
            "popularity_rank": rank,
            "inside_top25_sample": rank < ACC.famous_sample,
            "below_acceptance_floor": int(degrees[i]) < ACC.famous_min_degree_floor,
        }

    # --- would check_acceptance pass? DESCRIPTIVE ONLY -------------------
    # Context for GRT-P2 (the guard is blind to a severe collapse, because a
    # collapsing artist loses the popularity that put it in the sample). Never
    # a criterion here, and a pass is not evidence of health.
    try:
        check_acceptance(graph, ACC)
        acceptance = {"passes": True, "problems": []}
    except ArtifactRejected as exc:
        acceptance = {"passes": False, "problems": str(exc).splitlines()[1:]}

    return {
        "nodes": graph.artist_count,
        "edges": graph.edge_count,
        "hub_structure": hub,
        "component_exclusion": exclusion,
        "band_stranding": per_band,
        "tracers": tracers,
        "acceptance_descriptive": acceptance,
    }


def gate() -> dict:
    """CB-2's instrument gate: reproduce published figures for BOTH reference
    builds.

    Two independently produced graphs agreeing with already-published numbers
    is green and red in one step -- a scorer bug that moves a number cannot
    match both. Tolerances are 1e-3 on rates (the published values are rounded
    in prose) and exact on integer degrees.
    """
    frame = fame_frame()
    production_top = top_degree_node_set(
        deserialise(REFERENCE_CELLS["ALG-E"]["path"].read_bytes())
    )

    results = {}
    ok_all = True
    for label, spec in REFERENCE_CELLS.items():
        graph = deserialise(spec["path"].read_bytes())
        scored = score_cell(graph, frame, crawled_mbids(label), spec["pre_prune"],
                            production_top_degree=production_top)
        expect = spec["expect"]

        checks = {
            "exclusion_rate": abs(
                scored["component_exclusion"]["exclusion_rate"] - expect["exclusion_rate"]
            ) < 1e-3,
            "lower_half_stranded": abs(
                scored["band_stranding"]["lower half"]["stranded_share_of_crawled"]
                - expect["lower_half_stranded"]
            ) < 1e-3,
        }
        for nm, deg in expect["tracer_degrees"].items():
            checks[f"degree_{nm}"] = scored["tracers"][nm].get("degree") == deg

        passed = all(checks.values())
        ok_all = ok_all and passed
        results[label] = {"checks": checks, "passed": passed, "scored": scored}
        print(f"{label}: {'PASS' if passed else 'FAIL'} — "
              f"exclusion {scored['component_exclusion']['exclusion_rate']}, "
              f"lower-half stranded "
              f"{scored['band_stranding']['lower half']['stranded_share_of_crawled']}, "
              f"R.E.M. degree {scored['tracers']['R.E.M.'].get('degree')}")
        for nm, val in checks.items():
            if not val:
                print(f"    MISMATCH: {nm}")

    results["gate_passed"] = ok_all
    (HERE / "cb_metrics_gate.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    if not args.gate:
        raise SystemExit("cb_metrics is a library; --gate runs its instrument check")
    out = gate()
    raise SystemExit(0 if out["gate_passed"] else 1)
