"""DRP- stage 3c: DRP-C10's per-pair frontier count (#200). Descriptive; decides nothing.

Governing document: docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md
(`DRP-`), executed from the body: §5 DRP-C10 ("per pair, the count of added edges within one hop of
the band journeys' nodes"), §5 "The depth band" (presses 7-10), §2.4 (the jump-relaxation deferral
condition this count feeds) and §7 DRP-R0 / DRP-R2 (which cite it, the latter "on A0").

Stage 3a deferred this half of DRP-C10 to 3c because it needs the band journeys (stage-3a log,
task 2). It is computed for all eight cells, since DRP-R2 asks for it on A0: on a DRP-S0 cell it
says where the added exits WOULD sit beside today's journeys, and `used` is 0 by construction.

Per (cell, set, rule, pair), over the depths of the band at which the cell returned an
interior-bearing journey (`band_depths`; §4's cross-cell drop rule is 3d's, at *complete*):

  nodes             every node on those journeys, endpoints included
  incident_all      added edges with at least one end in `nodes`
  incident_interior added edges with at least one end in the journeys' interiors (endpoints out)
  used              added edges the journeys traverse

Both incident counts are kept because the source and target of a DRP-T1 pair are themselves added-
edge centres, so `incident_all` counts the exits at the endpoints and `incident_interior` does not.
Which one a read uses is the read's (3d's) choice, not this script's.

"Added edges" are the DRP-S1 map's edges absent from lba-a6, taken from the two CSRs by node id;
the count is checked against drp_g3.json's structural half, which stage 3a derived independently.

Sealing (§8): node ids and counts only; no name is resolved.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-28-drp-stage3c/drp_c10_frontier.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
STAGE3B = HERE.parent / "2026-09-28-drp-stage3b"
sys.path.insert(0, str(STAGE3B))
from drp_sweep import CELLS, CELLS_DIR, RULES, SETS, STAGE3A, load_map  # noqa: E402
import drp_common as dc  # noqa: E402
from drp_common import BAND  # noqa: E402


def added_edges(a0: dc.Map, s1: dc.Map) -> set[tuple[int, int]]:
    if a0.mbids != s1.mbids:
        dc.refuse("node sets differ by id between lba-a6 and DRP-S1 (DRP-G3 should have caught this)")
    out = set()
    for u in range(s1.n):
        a_row = a0.nbr[a0.off[u]:a0.off[u + 1]]
        s_row = s1.nbr[s1.off[u]:s1.off[u + 1]]
        if len(s_row) == len(a_row):
            continue
        for v in set(s_row) - set(a_row):
            out.add((min(u, v), max(u, v)))
    return out


def main() -> None:
    a0 = load_map("DRP-S0")
    s1 = load_map("DRP-S1")
    added = added_edges(a0, s1)
    g3 = json.loads((STAGE3A / "drp_g3.json").read_text(encoding="utf-8"))
    want_n = g3["DRP-C10"]["added_edges"]
    if len(added) != want_n:
        dc.refuse(f"{len(added)} added edges from the CSR diff != drp_g3.json's {want_n}")
    print(f"added edges: {len(added)} (== drp_g3.json)", flush=True)
    by_node: dict[int, list[tuple[int, int]]] = {}
    for e in added:
        for x in e:
            by_node.setdefault(x, []).append(e)

    def incident(nodes: set[int]) -> int:
        return len({e for x in nodes for e in by_node.get(x, ())})

    def count(depths_: list) -> dict:
        nodes, interior, used, band = set(), set(), set(), []
        for d in depths_:
            path_ = d["path"]
            if d["k"] not in BAND or path_ is None or len(path_) <= 2:
                continue
            band.append(d["k"])
            nodes.update(path_)
            interior.update(path_[1:-1])
            used.update((min(a, b), max(a, b)) for a, b in zip(path_, path_[1:]))
        return {"band_depths": band, "nodes": len(nodes), "incident_all": incident(nodes),
                "incident_interior": incident(interior), "used": len(used & added)}

    # Red control, through the same counter as every real row: a band journey whose one interior
    # edge is an added edge must count it used and incident; outside the band it must count nothing.
    u, v = min(added)
    x = next(i for i in range(s1.n) if i not in by_node)
    y = next(i for i in range(x + 1, s1.n) if i not in by_node)
    red_in = count([{"k": 8, "path": [x, u, v, y]}])
    red_out = count([{"k": 3, "path": [x, u, v, y]}])
    if red_in["used"] != 1 or red_in["incident_interior"] < 1 or red_out["incident_all"] != 0:
        dc.refuse(f"red control failed: in-band {red_in}, out-of-band {red_out}")
    print(f"red control fired as it must: in-band {red_in}", flush=True)

    cells_out, cell_shas = {}, {}
    for cell, spec in CELLS.items():
        path = CELLS_DIR / f"{cell}.json"
        cell_shas[cell] = dc.sha256_of(path)
        obj = json.loads(path.read_text(encoding="utf-8"))
        want = (s1 if spec["supply"] == "DRP-S1" else a0).sha
        if obj["graph_sha256"] != want:
            dc.refuse(f"{cell}: routed on {obj['graph_sha256'][:8]}, expected {want[:8]}")
        rows = []
        for p in obj["pairs"]:
            row = count(p["depths"])
            if spec["supply"] == "DRP-S0" and row["used"]:
                dc.refuse(f"{cell}: a journey on lba-a6 traverses an added edge, which cannot exist there")
            rows.append({"set": p["set"], "rule": p["rule"], "i": p["i"], **row})
        cells_out[cell] = rows
        print(f"{cell}: {len(rows)} (set, rule, pair) rows", flush=True)
    obj = {"what": "DRP-C10 per-pair frontier count (§5); descriptive, no read",
           "band": list(BAND), "added_edges": len(added),
           "lba_a6_sha256": a0.sha, "drp_s1_sha256": s1.sha, "cell_file_sha256": cell_shas,
           "script_sha256": dc.sha256_of(Path(__file__)), "red_control": red_in, "sets": list(SETS), "rules": list(RULES),
           "cells": cells_out}
    d = dc.write_json(HERE / "drp_c10_frontier.json", obj)
    print(f"wrote drp_c10_frontier.json sha256 {d}")


if __name__ == "__main__":
    main()
