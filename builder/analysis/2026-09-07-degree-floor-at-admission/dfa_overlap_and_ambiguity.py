"""`DFA-` — the two reads the commissioned derivation named, and could not do from aggregates.

WHY THIS EXISTS. The `ml-graph-analyst` derivation (README §8) established that on every
shipped-ceiling arm here, `top1pct_degree_mass_frac` is algebraically equal to
`ceiling / (100 * mean_degree)` — so it carries no information about hub structure, and the
own-versus-fixed sign flip is forced arithmetic rather than a measurement. It named two things
that would settle what the aggregates cannot, and both need per-arm degrees the sweep did not
serialise:

  1. THE EXACT AMBIGUITY OF THE FIXED-REFERENCE COLUMN. The control's top-1% reference set is
     887 nodes drawn from 9,526 that all sit at degree 50, so WHICH 887 is arbitrary. Recording
     each of those 9,526 nodes' degree in each arm gives the exact min and max of the
     fixed-reference mass over admissible choices — the 887 smallest and the 887 largest. No
     distributional assumption, unlike the derivation's own 95% bound, which is the one place
     it extrapolated.

  2. TRACK B'S ACTUAL COMPANION STATISTIC. `cb_metrics.py:171-174` computes
     `top_degree_node_set_overlap_with_production` = |own_top & reference_top| / |reference_top|
     — a SET OVERLAP FRACTION, not a mass scored against a fixed set. Verified in source
     2026-09-07. `dfa_degree_floor.fixed_reference_mass` is therefore a NEW quantity and its
     docstring's description of Track B was wrong; both are corrected. The overlap is worth
     computing because the derivation showed it responds to exactly what the mass version
     misses: it collapses when the top set MOVES, whereas the mass-against-a-fixed-set column
     reported the ascending-order arm as only 0.7% above the control while its max degree was
     3,055.

     Reference here is the CONTROL arm, the isolating baseline. Track B's was the production
     cell. That difference is named rather than papered over: this is Track B's statistic's
     SHAPE applied to this probe's baseline, not Track B's own figure, and it is not comparable
     to `cb_scores.json`.

Descriptive only, as the rest of the probe: nothing routed, nothing serialised into an
artifact, archive read-only, nothing adopted or proposed.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-07-degree-floor-at-admission/dfa_overlap_and_ambiguity.py
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "2026-09-07-degree-ceiling-falsifier"))

from artistpath_builder import pipeline as shipped_pipeline  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.sources.listenbrainz import ListenBrainzSource  # noqa: E402

from dcf_ceiling_sweep import ARCHIVE, ReadOnlyArchive  # noqa: E402
from dfa_degree_floor import ULF_PAYLOAD, floored_trimmed_union_cap  # noqa: E402

logger = logging.getLogger(__name__)

ARMS = [
    ("control (shipped)", None, "live", "shipped"),
    ("F=1 live/shipped", 1, "live", "shipped"),
    ("F=2 live/shipped", 2, "live", "shipped"),
    ("F=3 live/shipped", 3, "live", "shipped"),
    ("F=2 fixed pre-trim", 2, "fixed", "shipped"),
    ("F=2 ascending order", 2, "live", "ascending"),
]


def build(floor: int | None, floor_mode: str, node_order: str):
    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        union_degree_ceiling=50,
        require_fame=False,
        drop_unlistenable=True,
        unlistenable_list_path=ULF_PAYLOAD,
    )
    original = shipped_pipeline.trimmed_union_cap
    if floor is not None:

        def _capped(adjacency, top_j, degree_ceiling, *, ranking):
            return floored_trimmed_union_cap(
                adjacency, top_j, degree_ceiling, ranking=ranking,
                floor=floor, floor_mode=floor_mode, node_order=node_order,
            )

        shipped_pipeline.trimmed_union_cap = _capped
    try:
        started = time.monotonic()
        graph = shipped_pipeline.build_from_archive(
            config, ReadOnlyArchive(LocalArchive(ARCHIVE)), ListenBrainzSource(config)
        )
    finally:
        shipped_pipeline.trimmed_union_cap = original
    degrees = np.diff(graph.offsets).astype(np.int64)
    print(f"    built in {(time.monotonic() - started) / 60:.1f} min", flush=True)
    return list(graph.mbids), degrees


def top_set(mbids, degrees, frac: float) -> tuple[set[str], int, int]:
    """The top `frac` of nodes by degree, with the boundary degree and tie count."""
    cut = max(1, int(round(len(degrees) * frac)))
    order = np.argsort(-degrees, kind="stable")[:cut]
    boundary = int(degrees[order].min())
    return (
        {mbids[int(i)] for i in order},
        cut,
        int(np.sum(degrees == boundary)),
    )


def main() -> int:
    out: dict = {
        "probe": "DFA- — exact fixed-reference ambiguity, and Track B's actual "
        "companion statistic (set overlap), on the arms already built",
        "commissioned_by": "the ml-graph-analyst derivation, README section 8",
        "reference": "the CONTROL arm's own top 1% by degree. Track B's reference "
        "was its production cell, so this is that statistic's SHAPE on this "
        "probe's baseline and is NOT comparable to cb_scores.json",
        "arms": [],
    }

    print("=== control ===", flush=True)
    c_mbids, c_deg = build(None, "live", "shipped")
    c_top1, c_cut1, c_ties1 = top_set(c_mbids, c_deg, 0.01)
    c_top10, _, _ = top_set(c_mbids, c_deg, 0.10)
    c_index = {m: i for i, m in enumerate(c_mbids)}
    c_boundary = int(min(c_deg[c_index[m]] for m in c_top1))
    # Every node sitting AT the control's top-1% boundary degree. The reference
    # set is an arbitrary `c_cut1` of these, which is the whole ambiguity.
    tied_pool = [m for m in c_mbids if int(c_deg[c_index[m]]) == c_boundary]
    print(
        f"control: cut {c_cut1:,}  boundary degree {c_boundary}  "
        f"nodes at that degree {len(tied_pool):,}  "
        f"(reference is {c_cut1:,} arbitrary members of that pool)",
        flush=True,
    )
    out["reference_set"] = {
        "cut_size": c_cut1,
        "boundary_degree": c_boundary,
        "nodes_at_the_boundary_degree": len(tied_pool),
        "every_reference_node_is_at_the_boundary_degree": all(
            int(c_deg[c_index[m]]) == c_boundary for m in c_top1
        ),
    }

    for label, floor, floor_mode, node_order in ARMS:
        print(f"=== {label} ===", flush=True)
        if label == "control (shipped)":
            mbids, degrees = c_mbids, c_deg
        else:
            mbids, degrees = build(floor, floor_mode, node_order)
        index = {m: i for i, m in enumerate(mbids)}
        two_e = int(degrees.sum())
        own1, cut1, ties1 = top_set(mbids, degrees, 0.01)
        own10, cut10, _ = top_set(mbids, degrees, 0.10)

        # --- exact ambiguity of the fixed-reference mass --------------------
        # Degrees IN THIS ARM of every node in the control's tie pool. The
        # admissible reference sets are exactly the c_cut1-subsets of that pool,
        # so the mass ranges between the c_cut1 smallest and c_cut1 largest.
        pool_degrees = sorted(
            int(degrees[index[m]]) if m in index else 0 for m in tied_pool
        )
        lo = sum(pool_degrees[:c_cut1]) / two_e
        hi = sum(pool_degrees[-c_cut1:]) / two_e
        measured = sum(
            int(degrees[index[m]]) for m in c_top1 if m in index
        ) / two_e

        arm = {
            "label": label,
            "nodes": len(mbids),
            "edges": two_e // 2,
            "mean_degree": round(float(degrees.mean()), 4),
            "max_degree": int(degrees.max()),
            # The derivation's saturation identity, checked here rather than
            # taken on trust: where >=1% of nodes sit at the ceiling, the mass
            # measure equals ceiling / (100 * mean_degree) exactly.
            "top1pct_cut_size": cut1,
            "nodes_tied_at_the_top1pct_boundary_degree": ties1,
            "ties_over_cut": round(ties1 / cut1, 3),
            "top1pct_degree_mass_frac_own": round(
                float(degrees[np.argsort(-degrees, kind="stable")[:cut1]].sum())
                / two_e, 5
            ),
            "saturation_identity_ceiling_over_100_mean": round(
                50.0 / (100.0 * float(degrees.mean())), 5
            ),
            # --- the two commissioned reads ---
            "fixed_reference_mass": {
                "measured": round(measured, 6),
                "min_over_admissible_reference_sets": round(lo, 6),
                "max_over_admissible_reference_sets": round(hi, 6),
                "exact_ambiguity_width": round(hi - lo, 6),
                "note": "exact, not a bound — the admissible sets are exactly "
                "the subsets of the control's tie pool, so the extremes are "
                "its smallest and largest members in this arm",
            },
            "top_degree_node_set_overlap_with_the_control": {
                "top1pct": round(len(own1 & c_top1) / len(c_top1), 5),
                "top_decile": round(len(own10 & c_top10) / len(c_top10), 5),
                "note": "Track B's statistic SHAPE (cb_metrics.py:171-174), "
                "referenced to this probe's control rather than to a "
                "production cell. Not comparable to cb_scores.json",
            },
        }
        out["arms"].append(arm)
        print(
            f"  overlap top1% {arm['top_degree_node_set_overlap_with_the_control']['top1pct']:.5f}  "
            f"decile {arm['top_degree_node_set_overlap_with_the_control']['top_decile']:.5f}  |  "
            f"fixed-ref {measured:.6f} in [{lo:.6f}, {hi:.6f}] width {hi - lo:.6f}  |  "
            f"own {arm['top1pct_degree_mass_frac_own']:.5f} vs identity "
            f"{arm['saturation_identity_ceiling_over_100_mean']:.5f}  "
            f"ties/cut {arm['ties_over_cut']}",
            flush=True,
        )
        (HERE / "dfa_overlap_and_ambiguity.json").write_text(
            json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
        )

    print(f"wrote {HERE / 'dfa_overlap_and_ambiguity.json'}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    raise SystemExit(main())
