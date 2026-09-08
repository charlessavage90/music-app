"""`DFA-` — a degree floor at admission, instead of raising the ceiling.

EXTENDS the `DCF-` probe beside it; it is NOT a new instrument. Pinned inputs,
provenance check, instrument-gate discipline and every read convention are
IMPORTED from `dcf_ceiling_sweep.py` rather than copied, so "the same read" is
a fact about the code and not a claim in prose. See §1 of this probe's README.

WHY THIS ARM, given `DCF-` already ran
  `DCF-` §4 measured what lifting `union_degree_ceiling` buys on `CXR-P2`'s own
  ruler, and what it costs in restored edges, hub attachment and
  `top1pct_degree_mass_frac`. Those figures are owned there, cited here, and
  never restated. The shape of the result is what motivates this arm: the
  benefit is carried by a few thousand edges and the cost is carried by all of
  them. So this arm asks whether the benefit survives when only the edges that
  carry it are exempted:

      exempt an edge from the DEGREE TRIM when deleting it would leave the
      artist at the FAR end with <= F connections.

  Ceiling held at the shipped 50, every other knob at default, F swept over
  1, 2 and 3. This is the "degree floor at admission" candidate named in
  `specs/2026-09-06-own-similarity-design.md` §9.

SCOPE, and it is the same narrow one as `DCF-`
  Graphs built in memory, nothing serialised, archives read-only. NO PATH IS
  BUILT, no `CRS-C4` hub transit is computed, no routing criterion of any
  pre-registration is evaluated, nothing is adopted and no rule change is
  proposed. A candidate-supply gain is NOT a delivered-connection gain. The
  cap-rule decision is parked and the owner's (design §9) and owes a blind
  listen (`REQ-38`) before any adoption whatever these numbers say.
  "Hub" here means TOP DECILE BY DEGREE within the arm's own built graph —
  never fame, never `pop_raw` (§2.6).

RELATION TO THE SHIPPED RULE, and what it costs in fidelity
  `trimmed_union_cap` in `builder/src/artistpath_builder/graph.py` is NOT
  modified and no shipped builder path is touched. `floored_trimmed_union_cap`
  below is a copy of that function's body with ONE added condition inside the
  deletion loop. The top-j selection, the union, `symmetrise`, the `strength`
  helper, the node processing order and both tie-breaks are reproduced exactly.

  The fidelity cost of a copy is drift: if the shipped rule changes, this one
  silently does not. That is why F=0 is run as an arm and asserted equal to the
  shipped control build (`DFA-G1`). A drift that mattered would break it.

  It is substituted into the shipped pipeline by rebinding
  `artistpath_builder.pipeline.trimmed_union_cap` for the duration of one arm,
  so every other stage of `build_from_archive` — payload parse, drop lists,
  rescale, symmetrise, largest-component prune — is the shipped code running
  shipped defaults. Nothing on disk is edited.

THE TWO ORDER CHOICES, STATED — because the result depends on them
  1. WHEN the far end's degree is read. `live` (PRIMARY) reads it at the moment
     of deletion; `fixed` reads a frozen pre-trim degree. Live is primary
     because it is the only one that DELIVERS a floor: under live, no artist
     whose pre-trim degree exceeds F can be carried to or below F by the trim,
     which is the guarantee the candidate is named for. Under fixed, an artist
     at F+5 is never protected and five over-full neighbours can still strip it
     to zero.
  2. THE ORDER over-full nodes are processed. `shipped` (PRIMARY) is
     `trimmed_union_cap`'s own `(-pre-trim degree, mbid)`; `ascending` reverses
     the degree key. Shipped is primary because holding every other knob at
     default includes holding the processing order at default.

  Both alternatives are RUN, at F=2, so the sensitivity is measured rather than
  asserted.

DEPARTURES FROM A SHIPPING CONFIG — identical to `DCF-`'s BRIDGE arms
  require_fame=False        fame is read by no figure here and cannot change
                            edge survival, so it is inert (MSW-G3 refuses).
  drop_unlistenable=True    via the SHIPPED per-invocation override, with the
                            re-censused ALG-B payload. This reproduces
                            `graph-cxa-adopted.bin`'s own population exactly,
                            which is what puts every figure here on `CXR-P2`'s
                            ruler and comparable to `DCF-` section 4. `DCF-`'s
                            larger-population PRIMARY arms are NOT reproduced.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-07-degree-floor-at-admission/dfa_degree_floor.py
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
DCF = HERE.parent / "2026-09-07-degree-ceiling-falsifier"
sys.path.insert(0, str(DCF))

from artistpath_builder import pipeline as shipped_pipeline  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.graph import _desc, symmetrise  # noqa: E402
from artistpath_builder.sources.listenbrainz import ListenBrainzSource  # noqa: E402

# The frozen `DCF-` harness. Imported, never copied: the pinned archive, the
# artifact identity check, the added/pre-existing split and every read
# convention below are that probe's own code, so this probe cannot drift from
# it by transcription. Importing is safe — its work is all under a __main__
# guard.
from dcf_ceiling_sweep import (  # noqa: E402
    ARCHIVE,
    ReadOnlyArchive,
    hub_stats,
    neighbour_sets,
    population_split,
    restored_edge_composition,
    set_stats,
    top_decile_by_degree,
)

logger = logging.getLogger(__name__)

# The re-censused ALG-B un-listenable payload, 117,302 artists censused. Applied
# through the shipped per-invocation override; see the module docstring for why
# HEAD's default cannot build this archive with the drop on. Package data, not
# a scratch file, so it travels with the repo.
ULF_PAYLOAD = (
    HERE.parent.parent
    / "src"
    / "artistpath_builder"
    / "data"
    / "unlistenable_drop_algb_20260809.json"
)


def floored_trimmed_union_cap(
    adjacency,
    top_j: int,
    degree_ceiling: int,
    *,
    ranking,
    floor: int,
    floor_mode: str = "live",
    node_order: str = "shipped",
    telemetry: dict | None = None,
):
    """`trimmed_union_cap` with a degree floor at the far end of each deletion.

    A COPY of the shipped function with one added condition, and the copy is
    deliberate: the shipped path is not modified. Everything up to the trim
    loop — the top-j selection with its lowest-MBID tie-break, the union, the
    symmetrise, the `strength` helper — is reproduced exactly.

    THE ONE CHANGE. The shipped trim takes the `excess` weakest edges of an
    over-full node and deletes them unconditionally. Here a deletion is REFUSED
    when it would leave the artist at the FAR end with <= `floor` connections,
    and the next-weakest candidate is considered instead. Only the far end is
    tested: the near end is over the ceiling by construction and cannot be near
    a floor.

    CONSEQUENCE, and it is the arm's whole cost side: `degree <= degree_ceiling`
    IS NO LONGER GUARANTEED. A node all of whose weakest edges are exempt stays
    over the ceiling. The shipped rule's BOUND comment does not survive this
    change, and the arm's max degree is reported for exactly that reason.

    Single pass is still sufficient for the same reason as the shipped rule:
    deletion only ever lowers a degree, so a node at or under the ceiling when
    it is processed cannot rise above it afterwards — and an exemption granted
    on the far end's live degree only becomes more true as that degree falls.

    `floor=0` exempts nothing and must reproduce `trimmed_union_cap` exactly.
    That identity is asserted on real data by the gate rather than argued here.
    """
    if set(ranking) != set(adjacency):
        raise ValueError(
            "ranking must cover exactly the nodes of adjacency; top-j "
            "selection over a different node set is undefined"
        )
    if floor_mode not in {"live", "fixed"}:
        raise ValueError(f"unknown floor_mode {floor_mode!r}")
    if node_order not in {"shipped", "ascending"}:
        raise ValueError(f"unknown node_order {node_order!r}")

    keep: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(edges, key=lambda dst: (-ranking[node][dst], dst))
        keep[node] = set(ranked[:top_j])

    unioned: dict[str, dict[str, float]] = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in keep[node] or node in keep.get(dst, set()):
                unioned[node][dst] = score
    result = symmetrise(unioned)

    def strength(u: str, v: str) -> float:
        return max(
            ranking.get(u, {}).get(v, float("-inf")),
            ranking.get(v, {}).get(u, float("-inf")),
        )

    # Frozen BEFORE any deletion: `fixed` mode reads the far end's degree from
    # here, so it is a static property of the unioned graph and independent of
    # processing order. `live` mode reads `len(result[v])` instead.
    pre_trim_degree = {node: len(edges) for node, edges in result.items()}

    if node_order == "shipped":
        # `trimmed_union_cap`'s own order. Note the key is evaluated once by
        # `sorted`, so it is the PRE-TRIM degree in both implementations.
        order = sorted(result, key=lambda n: (-len(result[n]), n))
    else:
        order = sorted(result, key=lambda n: (len(result[n]), n))

    exempted = 0
    exempt_nodes: set[str] = set()
    for node in order:
        excess = len(result[node]) - degree_ceiling
        if excess <= 0:
            continue
        candidates = sorted(result[node], key=lambda v: (strength(node, v), _desc(v)))
        removed = 0
        for victim in candidates:
            if removed >= excess:
                break
            if floor > 0:
                far = (
                    len(result[victim])
                    if floor_mode == "live"
                    else pre_trim_degree[victim]
                )
                if far - 1 <= floor:
                    exempted += 1
                    exempt_nodes.add(victim)
                    continue
            result[node].pop(victim, None)
            result[victim].pop(node, None)
            removed += 1

    if telemetry is not None:
        over = [n for n, e in result.items() if len(e) > degree_ceiling]
        telemetry.update(
            {
                "floor": floor,
                "floor_mode": floor_mode,
                "node_order": node_order,
                "deletions_refused_by_the_floor": exempted,
                "distinct_artists_protected_at_least_once": len(exempt_nodes),
                "nodes_left_above_the_ceiling_before_the_prune": len(over),
                "max_degree_after_the_trim_before_the_prune": max(
                    (len(e) for e in result.values()), default=0
                ),
            }
        )
    return result


def build_arm(
    label: str,
    floor: int | None,
    floor_mode: str,
    node_order: str,
    added: list[str],
    pre_existing: list[str],
) -> tuple[dict, dict]:
    """Build one arm through the SHIPPED `build_from_archive` and measure it.

    `floor=None` is the CONTROL: the shipped `trimmed_union_cap` runs untouched.
    Otherwise the cap function is rebound for the duration of this build only.
    Every other stage is shipped code at shipped defaults.
    """
    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        union_degree_ceiling=50,  # HELD at the shipped value in every arm
        require_fame=False,
        drop_unlistenable=True,
        unlistenable_list_path=ULF_PAYLOAD,
    )
    source = ListenBrainzSource(config)
    archive = ReadOnlyArchive(LocalArchive(ARCHIVE))

    telemetry: dict = {}
    original = shipped_pipeline.trimmed_union_cap
    if floor is not None:

        def _capped(adjacency, top_j, degree_ceiling, *, ranking):
            return floored_trimmed_union_cap(
                adjacency,
                top_j,
                degree_ceiling,
                ranking=ranking,
                floor=floor,
                floor_mode=floor_mode,
                node_order=node_order,
                telemetry=telemetry,
            )

        shipped_pipeline.trimmed_union_cap = _capped
    try:
        started = time.monotonic()
        graph = shipped_pipeline.build_from_archive(config, archive, source)
        elapsed = time.monotonic() - started
    finally:
        shipped_pipeline.trimmed_union_cap = original

    degrees = np.diff(graph.offsets).astype(np.int64)
    degrees_by_mbid = {m: int(degrees[i]) for i, m in enumerate(graph.mbids)}
    hub_set, hub_boundary = top_decile_by_degree(degrees, graph.mbids)

    arm = {
        "label": label,
        "floor": floor,
        "floor_mode": None if floor in (None, 0) else floor_mode,
        "node_order": None if floor in (None, 0) else node_order,
        "is_control": floor is None,
        "elapsed_seconds": round(elapsed, 1),
        "config": {
            "algorithm": config.algorithm,
            "cap_strategy": config.cap_strategy,
            "union_top_j": config.union_top_j,
            "union_degree_ceiling": config.union_degree_ceiling,
            "similarity_rescale": config.similarity_rescale,
            "drop_no_release_tail": config.drop_no_release_tail,
            "drop_featured_credit": config.drop_featured_credit,
            "drop_unlistenable": config.drop_unlistenable,
            "require_fame": config.require_fame,
        },
        "cap_telemetry": telemetry or None,
        "whole_graph": hub_stats(degrees, graph.mbids),
        "top_decile_by_degree": hub_boundary,
        "added": set_stats(degrees_by_mbid, added),
        "pre_existing": set_stats(degrees_by_mbid, pre_existing),
        # Handed to the ml-graph-analyst: the shape question it is asked cannot
        # be answered from summary statistics.
        "degree_histogram": {
            str(k): v for k, v in sorted(Counter(int(d) for d in degrees).items())
        },
    }
    print(
        f"  {label:<22} built in {elapsed / 60:.1f} min  "
        f"nodes {arm['whole_graph']['nodes']:,}  "
        f"edges {arm['whole_graph']['edges']:,}  "
        f"max deg {arm['whole_graph']['max_degree']:,}  "
        f"top1pct {arm['whole_graph']['top1pct_degree_mass_frac']:.5f}  "
        f"ADDED median {arm['added']['median_degree']:.0f} "
        f"<=2 {100 * arm['added']['share_le_2']:.2f}% "
        f"absent {100 * arm['added']['share_absent']:.2f}%",
        flush=True,
    )
    return arm, {
        "added_nbrs": neighbour_sets(graph, set(added)),
        "degrees_by_mbid": degrees_by_mbid,
        "hub_set": hub_set,
        "mbids": list(graph.mbids),
        "degrees": degrees,
    }


def top1pct_set(state: dict) -> set[str]:
    """One arm's own top 1% of nodes BY DEGREE, as a set of MBIDs."""
    degrees, mbids = state["degrees"], state["mbids"]
    cut = max(1, int(round(len(degrees) * 0.01)))
    order = np.argsort(-degrees, kind="stable")[:cut]
    return {mbids[int(i)] for i in order}


def fixed_reference_mass(
    reference_set: set[str], mbids: list[str], degrees: np.ndarray
) -> dict:
    """`top1pct_degree_mass_frac` scored against a FIXED node set.

    Track B's companion column scored every cell against one artifact's top
    nodes rather than each cell's own. The two scorings answer different
    questions and can rank arms differently; this computes the fixed one so
    both can be reported. The reference set here is the CONTROL arm's own top
    1% by degree — the isolating baseline, which is the analogue of Track B's
    single-artifact reference.
    """
    index = {m: i for i, m in enumerate(mbids)}
    present = [index[m] for m in reference_set if m in index]
    total = int(degrees.sum())
    held = int(degrees[present].sum()) if present else 0
    return {
        "reference_nodes_resolved_in_this_arm": len(present),
        "reference_nodes_absent_from_this_arm": len(reference_set) - len(present),
        "top1pct_degree_mass_frac_fixed_reference": (
            round(held / total, 5) if total else 0.0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--floors", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--out", default=str(HERE / "dfa_results.json"))
    args = parser.parse_args()

    if not ULF_PAYLOAD.is_file():
        raise SystemExit(f"missing the re-censused ULF payload at {ULF_PAYLOAD}")

    added, pre_existing, identity = population_split()
    added_set = set(added)
    out = Path(args.out)

    results = {
        "probe": "DFA- — a degree floor at admission, instead of raising the "
        "ceiling: exempt an edge from the degree trim when deleting it would "
        "leave the FAR end with <= F connections",
        "extends": "builder/analysis/2026-09-07-degree-ceiling-falsifier/",
        "archive": {
            "dir": str(ARCHIVE),
            "payloads": sum(
                1
                for k in LocalArchive(ARCHIVE).keys()
                if k.startswith(f"similar/listenbrainz/{CANDIDATE_ALGORITHM}/")
                and k.endswith(".json")
            ),
        },
        "unlistenable_list_path": str(ULF_PAYLOAD),
        "artifacts": identity,
        "arms": [],
    }
    print(f"archive payloads: {results['archive']['payloads']:,}", flush=True)

    # The control runs FIRST and unmodified: every floored arm's restored-edge
    # split and its fixed-reference concentration are taken against it.
    plan: list[tuple[str, int | None, str, str]] = [
        ("control (shipped)", None, "live", "shipped"),
        ("F=0 identity", 0, "live", "shipped"),
    ]
    plan += [(f"F={f} live/shipped", f, "live", "shipped") for f in args.floors]
    plan += [
        ("F=2 fixed pre-trim", 2, "fixed", "shipped"),
        ("F=2 ascending order", 2, "live", "ascending"),
    ]

    control_state: dict | None = None
    reference_set: set[str] = set()
    for label, floor, floor_mode, node_order in plan:
        print(f"\n=== arm: {label} ===", flush=True)
        arm, state = build_arm(label, floor, floor_mode, node_order, added, pre_existing)
        if control_state is None:
            control_state = state
            reference_set = top1pct_set(state)
        else:
            arm["restored_vs_control"] = restored_edge_composition(
                control_state["added_nbrs"],
                control_state["degrees_by_mbid"],
                state["added_nbrs"],
                state["degrees_by_mbid"],
                added_set,
                state["hub_set"],
            )
            arm["edges_added_vs_control"] = (
                arm["whole_graph"]["edges"] - results["arms"][0]["whole_graph"]["edges"]
            )
            comp = arm["restored_vs_control"]
            print(
                f"    restored {comp['restored_edges_total']:,} edges to added "
                f"artists — {100 * comp['share_to_a_hub']:.1f}% to a top-decile "
                f"hub; {comp['left_the_two_or_fewer_group']['total']:,} left the "
                f"<=2 group",
                flush=True,
            )
        arm["fixed_reference_concentration"] = fixed_reference_mass(
            reference_set, state["mbids"], state["degrees"]
        )
        results["arms"].append(arm)
        out.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")

    # --- instrument gate, both halves ---------------------------------------
    # A green result from an instrument never shown to go red is not evidence.
    by_label = {a["label"]: a for a in results["arms"]}
    control, identity_arm = by_label["control (shipped)"], by_label["F=0 identity"]

    green_identity = (
        control["whole_graph"] == identity_arm["whole_graph"]
        and control["added"] == identity_arm["added"]
        and control["pre_existing"] == identity_arm["pre_existing"]
        and control["degree_histogram"] == identity_arm["degree_histogram"]
        and identity_arm["restored_vs_control"]["restored_edges_total"] == 0
    )
    green_bound = control["whole_graph"]["max_degree"] <= 50

    floored = [by_label[f"F={f} live/shipped"] for f in args.floors]
    red = bool(floored) and all(
        a["whole_graph"]["max_degree"] > 50
        and a["whole_graph"]["edges"] > control["whole_graph"]["edges"]
        for a in floored
    )
    results["gate"] = {
        "green_f0_build_reproduces_the_shipped_control": green_identity,
        "green_f0_note": "a floor of 0 exempts nothing, so the floored cap must "
        "reproduce trimmed_union_cap's build exactly — same whole-graph, added, "
        "pre-existing and degree-histogram figures, and zero restored edges. "
        "This is what detects drift between the copy and the shipped rule",
        "green_control_bound_holds": green_bound,
        "green_bound_note": "control max degree <= 50, the shipped rule's stated "
        "bound (CRS-G2's check)",
        "red_knob_is_wired": red,
        "red_note": "every floored arm exceeds degree 50 AND holds more edges "
        "than the control, so the floor really reached the trim and the "
        "instrument can move. Exceeding the ceiling is the arm's own cost, not "
        "a defect: exemptions leave nodes over-full",
        "passed": green_identity and green_bound and red,
    }
    out.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"\ngate: green_f0={green_identity} green_bound={green_bound} red={red} -> "
        f"{'PASS' if results['gate']['passed'] else 'FAIL'}"
    )
    print(f"wrote {out}")
    return 0 if results["gate"]["passed"] else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
