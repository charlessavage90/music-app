"""Evaluate one artifact over the frozen panel.

Usage:
    cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python \\
        eval/run_baseline.py <graph.bin> <label> [--held-out]

Writes eval/results-<label>.json with per-pair metric vectors, so paired
significance tests run later without re-routing 130 paths.

The bad-path screen (artistpath_api.badpath) is cancelled (plan §2 C-1) and is
deliberately not imported here: this harness measures the FULL router and a
w_jump = 0 router only, never the screen.
"""

from __future__ import annotations

import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from artistpath_api.config import ApiConfig
from artistpath_api.evaluation import (
    PathMetrics,
    hub_node_set,
    path_metrics,
    summarise,
)
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path
from diagnostics import artifact_diagnostics, frozen_hub_diagnostics
from panel import load_panel, resolve_pairs

AGGREGATED = ("random", "obscure", "popularity_weighted")
HUB_SET_CACHE = Path(__file__).parent / "hub-nodes-control.json"


def load_or_freeze_hub_set(store: GraphStore) -> set[int]:
    """Hub set frozen by MBID from the control build.

    A per-graph top-1% threshold moves between builds (363 vs 278 measured),
    so a variant could "improve" purely by compressing its degree distribution.
    """
    if HUB_SET_CACHE.exists():
        mbids = json.loads(HUB_SET_CACHE.read_text(encoding="utf-8"))
        return {store.id_by_mbid[m] for m in mbids if m in store.id_by_mbid}
    nodes = hub_node_set(store, 0.01)
    HUB_SET_CACHE.write_text(
        json.dumps(sorted(store.mbids[i] for i in nodes)), encoding="utf-8"
    )
    return nodes


def main() -> int:
    graph_path, label = sys.argv[1], sys.argv[2]
    held_out = "--held-out" in sys.argv

    store = GraphStore.load(graph_path)
    panel = load_panel(Path(__file__).parent / "panel.json")
    hub_nodes = load_or_freeze_hub_set(store)

    full_cfg = ApiConfig()
    # w_jump = 0 removes the popularity channel entirely: w_floor is a proven
    # no-op and w_hub is dormant, so cost reduces to w_sim*(1-sim) + w_hop.
    # Popularity is derived from the scores, so it is NOT frozen across arms
    # even with identical weights (spec §6.1).
    no_jump_cfg = dataclasses.replace(full_cfg, w_jump=0.0)

    output: dict = {"label": label, "graph": graph_path, "held_out": held_out}
    output["diagnostics"] = artifact_diagnostics(store, cap=50)
    # DESCRIPTIVE ONLY (revised plan §2, amendment 8's criterion-3 discussion) —
    # explains why hubfrac moved, is not itself a pass/fail criterion. See
    # frozen_hub_diagnostics' docstring.
    hub_diag = frozen_hub_diagnostics(store, hub_nodes)
    output["frozen_hub_diagnostics"] = hub_diag
    print(
        f"{label:22s} frozen hubs present={hub_diag['frozen_hubs_present']:3d} "
        f"mean_degree={hub_diag['mean_frozen_hub_degree']:.1f}"
    )

    for router_name, cfg in (("full", full_cfg), ("w_jump_0", no_jump_cfg)):
        per_pair: list[dict] = []
        metrics: list[PathMetrics] = []
        started = time.time()
        for stratum in AGGREGATED:
            pairs, dropped = resolve_pairs(
                store, panel, stratum, held_out=held_out
            )
            if dropped:
                print(f"WARNING {stratum}: {len(dropped)} unresolvable mbids: {dropped[:3]}")
            for a, b in pairs:
                path = find_path(store, a, b, [], cfg)
                if not path or len(path) < 3:
                    continue
                m = path_metrics(store, path, hub_nodes)
                metrics.append(m)
                per_pair.append(
                    {
                        "stratum": stratum,
                        "from": store.mbids[a],
                        "to": store.mbids[b],
                        **dataclasses.asdict(m),
                    }
                )
        output[router_name] = {
            "per_pair": per_pair,
            "summary": summarise(metrics),
            "seconds": round(time.time() - started, 1),
        }
        s = output[router_name]["summary"]
        print(
            f"{label:22s} {router_name:9s} n={s.get('n', 0):3d} "
            f"AA {s.get('mean_adamic_adar', 0):.4f}  "
            f"OC {s.get('mean_overlap_coefficient', 0):.4f}  "
            f"hubfrac {s.get('mean_hubfrac', 0):.4f}  "
            f"ceiling {s.get('mean_ceiling_hops', 0):.3f}  "
            f"len {s.get('mean_length', 0):.1f}"
        )

    suffix = "-heldout" if held_out else ""
    out = Path(__file__).parent / f"results-{label}{suffix}.json"
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
