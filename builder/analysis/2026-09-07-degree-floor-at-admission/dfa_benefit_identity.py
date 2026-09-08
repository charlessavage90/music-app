"""`DFA-` — is the floor's benefit the SAME benefit the ceiling lift buys?

WHY THIS EXISTS. The main sweep found that F=2 and the non-binding ceiling both
move the added set's dead-end share to the same value and both move the same
NUMBER of artists out of the two-or-fewer group. Equinumerous is not identical,
and only identity supports the reading "the floor buys the ceiling lift's
benefit at a fraction of its cost". `restored_edge_composition` returns counts,
not MBIDs, so the main sweep's records cannot answer it.

This rebuilds three arms on the SAME archive, population and drop lists and
compares the actual artist sets:

    control      shipped cap, union_degree_ceiling = 50
    floor F=2    ceiling held at 50, floor at 2, live far-end degree,
                 shipped node order
    ceiling      shipped cap, union_degree_ceiling = 20000 (does not bind),
                 the upper bound on what ANY ceiling change can deliver

Descriptive only, as the rest of the probe: nothing is routed, nothing is
serialised, the archive is read-only, and nothing here is adopted or proposed.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-07-degree-floor-at-admission/dfa_benefit_identity.py
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

from dcf_ceiling_sweep import ARCHIVE, ReadOnlyArchive, population_split  # noqa: E402
from dfa_degree_floor import ULF_PAYLOAD, floored_trimmed_union_cap  # noqa: E402

logger = logging.getLogger(__name__)


def build(ceiling: int, floor: int | None) -> dict[str, int]:
    """Degrees by MBID for one arm, through the shipped `build_from_archive`."""
    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        union_degree_ceiling=ceiling,
        require_fame=False,
        drop_unlistenable=True,
        unlistenable_list_path=ULF_PAYLOAD,
    )
    original = shipped_pipeline.trimmed_union_cap
    if floor is not None:

        def _capped(adjacency, top_j, degree_ceiling, *, ranking):
            return floored_trimmed_union_cap(
                adjacency, top_j, degree_ceiling, ranking=ranking,
                floor=floor, floor_mode="live", node_order="shipped",
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
    print(
        f"  ceiling {ceiling:>6} floor {floor}  built in "
        f"{(time.monotonic() - started) / 60:.1f} min  nodes {len(graph.mbids):,}",
        flush=True,
    )
    return {m: int(degrees[i]) for i, m in enumerate(graph.mbids)}


def rescued(control: dict[str, int], arm: dict[str, int], added: list[str]) -> set[str]:
    """Added artists at <= 2 connections in the control and above it in this arm.

    An artist ABSENT from an arm has no degree there and is not counted as
    rescued by it — absent and "has one connection" are different states, which
    is the main sweep's own convention (`set_stats`).
    """
    out = set()
    for m in added:
        was, now = control.get(m), arm.get(m)
        if was is not None and was <= 2 and now is not None and now > 2:
            out.add(m)
    return out


def main() -> int:
    added, _pre_existing, identity = population_split()
    print("building three arms", flush=True)
    control = build(50, None)
    floor2 = build(50, 2)
    ceiling = build(20_000, None)

    r_floor = rescued(control, floor2, added)
    r_ceiling = rescued(control, ceiling, added)
    both = r_floor & r_ceiling
    union = r_floor | r_ceiling

    # The artists the CONTROL leaves at <= 2 and each arm still does. If the
    # residual sets are identical too, the two rules disagree about nobody.
    def residual(arm: dict[str, int]) -> set[str]:
        return {
            m for m in added
            if (control.get(m) is not None and control[m] <= 2)
            and (arm.get(m) is None or arm[m] <= 2)
        }

    res_floor, res_ceiling = residual(floor2), residual(ceiling)

    # How MUCH each rule gives the artists it rescues — the half a set identity
    # cannot express. The ceiling lift also enriches artists it does not rescue;
    # the floor may not.
    def degrees_of(arm: dict[str, int], mbids: set[str]) -> dict:
        vals = sorted(arm[m] for m in mbids if m in arm)
        arr = np.asarray(vals, dtype=np.int64)
        return {
            "n": len(vals),
            "median": float(np.median(arr)),
            "mean": round(float(arr.mean()), 3),
            "p90": int(np.percentile(arr, 90)),
            "max": int(arr.max()),
        }

    result = {
        "probe": "DFA- — is the floor's rescued set the SAME set the ceiling "
        "lift rescues, or merely the same size?",
        "artifacts": identity,
        "arms": {
            "control": "shipped cap, union_degree_ceiling=50",
            "floor_f2": "ceiling 50, floor 2, live far-end degree, shipped order",
            "ceiling_20000": "shipped cap, union_degree_ceiling=20000 (does not bind)",
        },
        "rescued_from_the_two_or_fewer_group": {
            "by_the_floor": len(r_floor),
            "by_the_ceiling_lift": len(r_ceiling),
            "by_both": len(both),
            "by_the_floor_only": len(r_floor - r_ceiling),
            "by_the_ceiling_lift_only": len(r_ceiling - r_floor),
            "jaccard": round(len(both) / len(union), 6) if union else None,
            "sets_are_identical": r_floor == r_ceiling,
        },
        "residual_still_at_two_or_fewer": {
            "under_the_floor": len(res_floor),
            "under_the_ceiling_lift": len(res_ceiling),
            "sets_are_identical": res_floor == res_ceiling,
        },
        "degrees_of_the_rescued_artists": {
            "under_the_floor": degrees_of(floor2, both),
            "under_the_ceiling_lift": degrees_of(ceiling, both),
            "note": "same artists, both arms — how much each rule gives them",
        },
        "degrees_of_the_whole_added_set": {
            "control": degrees_of(control, set(added)),
            "under_the_floor": degrees_of(floor2, set(added)),
            "under_the_ceiling_lift": degrees_of(ceiling, set(added)),
            "note": "the enrichment half, which a rescue count cannot show",
        },
    }
    out = HERE / "dfa_benefit_identity.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result["rescued_from_the_two_or_fewer_group"], indent=1))
    print(json.dumps(result["residual_still_at_two_or_fewer"], indent=1))
    print(json.dumps(result["degrees_of_the_rescued_artists"], indent=1))
    print(json.dumps(result["degrees_of_the_whole_added_set"], indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    raise SystemExit(main())
