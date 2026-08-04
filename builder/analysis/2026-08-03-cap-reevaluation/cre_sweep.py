"""`CRE-T9`/`CRE-T10` -- the §0.3 ladder over ONE named cell per invocation.

    cre_sweep.py --cell E-S1-P1a

One cell per run, one committed JSON per cell, so any session can stop and hand
off between cells (prereg §4). Writes `cre_sweep_<cell>.json`.

**In-run assertions, both hard failures:**

- **`CRE-G1`(b)** -- a `P1` cell's d0 journey is bit-identical to its
  **supply-matched `P0`** cell's, read from that cell's committed JSON. The `P0`
  cell therefore always sweeps first. Pinned supply-matched by analyst m9: a
  `P1b` cell's §0.2 isolating baseline is its `P1a` sibling, but identity against
  the **device-off** cell is what makes this a device test rather than a ramp-size
  test.
- **`CRE-G2`(b)** -- `assert_cost_decomposition` at k = 1 and k = 10 on every
  `P1` pair, with `masked_edge` set for forced-detour journeys so the replay
  reproduces the second search exactly.

**The exclusion list per depth is reconstructed, and the reconstruction is
checked rather than assumed.** `walk_journey` returns the ladder but not the
victims it pressed, and re-deriving them is a pure function of the paths it
returned and the shared `victim_key` -- there is no other input. The risk is not
the victim rule but the *break* semantics: `walk_journey` stops pressing at an
infeasible or interior-less depth and pads the rest of the ladder with
`(None, "none")`. So the reconstruction mirrors those breaks, and every
reconstructed exclusion is then asserted absent from the interior of its own and
every later depth -- which is an observable consequence of the hard exclusion and
would fire if the wrong victim had been reconstructed.

**Padding is recorded as padding.** Those trailing `(None, "none")` entries are
not measured infeasibility, and a scorer that could not tell them apart would
feed the uniform drop pairs that were never actually infeasible. Each pair
carries `walked_depths` and `termination` so T11 can distinguish them; the
`infeasible` set below counts only depths the ladder actually reached.

**The JSON is written to be read without the graph.** T11 is a figures-only
scorer, so interiors are recorded as MBIDs with their `fame_lb_pctl` values
rather than as cell-local node ids.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time

from cre_common import RAMPS, Ruler, in_dir, use_frozen
from cre_gates import load_cell, surviving_pairs
from cre_ladder import assert_cost_decomposition, victim_key, walk_journey
from cre_mirror import MirrorContext, SweepConfig, term_breakdown

use_frozen("api_src")
from artistpath_api.pathfinding import KNOWN, Exclusion  # noqa: E402

PRICINGS = ("P0", "P1a", "P1b")
G2B_DEPTHS = (1, 10)          # the prereg's k = 1 and k = 10


def split_cell(cell_id: str) -> tuple[str, str]:
    """`E-S2-labelscramble-P0` -> (`E-S2-labelscramble`, `P0`)."""
    for p in PRICINGS:
        if cell_id.endswith(f"-{p}"):
            return cell_id[: -(len(p) + 1)], p
    raise SystemExit(f"cell id {cell_id!r} must end in one of {PRICINGS}")


def config_for(pricing: str) -> SweepConfig:
    cfg = SweepConfig.production()
    if pricing == "P0":
        return cfg
    return cfg.with_(w_known_ramp_fame_pctl=RAMPS[pricing])


def ladder_excludes(ladder, key) -> list[list[Exclusion]]:
    """The exclusions in force at each depth the ladder actually walked.

    Mirrors `walk_journey`'s two break conditions exactly; the returned list is
    shorter than the ladder whenever the ladder was padded.
    """
    out: list[list[Exclusion]] = []
    excludes: list[Exclusion] = []
    for path, _kind in ladder:
        out.append(list(excludes))
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break
        excludes = excludes + [Exclusion(node=min(interior, key=key), reason=KNOWN)]
    return out


def check_reconstruction(ladder, per_depth_excludes) -> None:
    """Tie the reconstruction to observable output: a hard-excluded node cannot
    appear in the interior of the depth that excluded it or any later one."""
    for d, excludes in enumerate(per_depth_excludes):
        path = ladder[d][0]
        if path is None:
            continue
        interior = set(path[1:-1])
        for e in excludes:
            if e.node in interior:
                raise SystemExit(
                    f"exclusion reconstruction is wrong: node {e.node} is excluded "
                    f"at depth {d} yet appears in that depth's interior"
                )


def null_interior_unbypassable(interior_fame: list) -> int:
    """Pin 3's named consequence, made separable and importable.

    The victim rule sorts ruler-null interiors after every measured one, so while
    ANY measured interior exists none of the nulls can be pressed. With no
    measured interior the top-sorted null becomes the victim and the remainder
    stay unbypassable. This is the share of §0.4's "descent partly unmeasurable"
    trend that the victim rule produces MECHANICALLY, independent of any real
    descent -- which is exactly why it is counted rather than inferred.
    """
    unmeasured = sum(1 for f in interior_fame if f is None)
    has_measured = any(f is not None for f in interior_fame)
    return unmeasured if has_measured else max(0, unmeasured - 1)


def depth_row(store, ctx, cfg, ruler, measured, path, kind, excludes) -> dict:
    """One depth of one pair: journey, the two unmeasured classes, pin 3's
    mechanical component, and `CRE-D2`'s per-term shares."""
    if path is None:
        return {"kind": kind, "feasible": False}

    mbids = store.mbids
    interior = path[1:-1]
    n_null = n_absent = 0
    fame: list[float | None] = []
    for v in interior:
        status = ruler.status_of(mbids[v])
        if status == "null":
            n_null += 1
        elif status == "absent":
            n_absent += 1
        f = float(measured[v])
        fame.append(None if math.isnan(f) else f)

    # The two classes are derived from `ruler.status_of`; the fame array is nan
    # on exactly the same nodes. Asserted rather than assumed -- if the arrays
    # ever came apart, every unmeasured-class figure below would be silently
    # attributed to the wrong nodes.
    assert n_null + n_absent == sum(1 for f in fame if f is None), (
        "ruler status and the measured fame array disagree on which interiors "
        "are unmeasured")
    unbypassable = null_interior_unbypassable(fame)

    rows = term_breakdown(store, ctx, cfg, excludes, path)
    total = sum(sum(r.values()) for r in rows)
    shares = ({k: sum(r[k] for r in rows) / total for k in rows[0]}
              if total > 0 else None)

    return {
        "kind": kind,
        "feasible": True,
        "interior_len": len(interior),
        "interior_mbids": [mbids[v] for v in interior],
        "interior_fame_pctl": fame,
        "interiors_null_in_snapshot": n_null,
        "interiors_absent_from_snapshot": n_absent,
        "null_interior_unbypassable": unbypassable,
        "path_cost_total": total,
        "term_shares": shares,
    }


def g1b(cell_id: str, graph_cell: str, per_pair: dict) -> dict:
    """`CRE-G1`(b): d0 identical to the supply-matched `P0` cell's d0."""
    base_id = f"{graph_cell}-P0"
    path = in_dir(f"cre_sweep_{base_id}.json")
    if not path.exists():
        raise SystemExit(
            f"{cell_id} needs its supply-matched baseline {base_id} to have swept "
            f"first (CRE-G1(b)); {path.name} is not committed yet."
        )
    base = json.loads(path.read_text(encoding="utf-8"))["per_pair"]
    diverged = []
    for key, row in per_pair.items():
        mine, theirs = row["depths"][0], base[key]["depths"][0]
        if (mine.get("interior_mbids") != theirs.get("interior_mbids")
                or mine["kind"] != theirs["kind"]
                or mine["feasible"] != theirs["feasible"]):
            diverged.append(key)
    if diverged:
        raise SystemExit(
            f"CRE-G1(b) FAILED for {cell_id}: d0 differs from {base_id} on "
            f"{len(diverged)} pairs ({diverged[:3]}...). The ramp is zero at k = 0 "
            f"and is not added at all, so the device is firing at the wrong depth."
        )
    return {"baseline_cell": base_id, "pairs_checked": len(per_pair),
            "result": "PASS"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", required=True, help="e.g. E-S1-P1a")
    args = ap.parse_args()
    cell_id = args.cell
    graph_cell, pricing = split_cell(cell_id)

    t0 = time.time()
    ruler = Ruler()
    manifest, store = load_cell(graph_cell)
    measured, device = ruler.arrays(store)
    ctx = MirrorContext.build(store, device)
    cfg = config_for(pricing)
    pairs = surviving_pairs()
    key = victim_key(measured, store.pop_raw, store.mbids)
    print(f"{cell_id}: {store.artist_count} artists, {len(pairs)} pairs, "
          f"ramp = {cfg.w_known_ramp_fame_pctl}", flush=True)

    per_pair: dict[str, dict] = {}
    infeasible: list[list] = []
    g2b_checks = 0
    for cls, a, b in pairs:
        s, t = store.id_by_mbid[a], store.id_by_mbid[b]
        ladder = walk_journey(store, s, t, cfg, ctx, measured, store.pop_raw,
                              store.mbids)
        per_depth_excludes = ladder_excludes(ladder, key)
        check_reconstruction(ladder, per_depth_excludes)

        depths = []
        for d, (path, kind) in enumerate(ladder):
            if d < len(per_depth_excludes):
                row = depth_row(store, ctx, cfg, ruler, measured, path, kind,
                                per_depth_excludes[d])
                row["walked"] = True
                if path is None:
                    infeasible.append([f"{a}|{b}", d])
            else:
                # Padding: the ladder stopped pressing before this depth. NOT
                # measured infeasibility -- see the module docstring.
                row = {"kind": "none", "feasible": False, "walked": False}
            depths.append(row)

        walked = len(per_depth_excludes)
        last_path, last_kind = ladder[walked - 1]
        if last_path is None:
            termination = "infeasible"
        elif not last_path[1:-1]:
            termination = "adjacent_only"
        else:
            termination = "completed"

        # CRE-G2(b) on a P1 cell: the toll the harness charges is the toll the
        # formula says. The SAME assertion is run on P0 cells as a plain
        # instrument check -- clause (1) ties the recorded term shares to the
        # search's own accumulated cost, and T11 reads P0 shares too, so leaving
        # them unverified would trust exactly the arithmetic that produces the
        # baseline every candidate is measured against. It is deliberately NOT
        # called `G2(b)`: that identifier is pre-registered for the device test,
        # and two load-bearing objects do not share an identifier here.
        for d in G2B_DEPTHS:
            if d < walked and ladder[d][0] is not None:
                path_d, kind_d = ladder[d]
                assert_cost_decomposition(
                    store, ctx, cfg, per_depth_excludes[d], path_d,
                    masked_edge=(s, t) if kind_d == "forced" else None)
                g2b_checks += 1

        per_pair[f"{a}|{b}"] = {
            "class": cls,
            "endpoints": [a, b],
            "walked_depths": walked,
            "termination": termination,
            "depths": depths,
        }

    doc = {
        "cell": cell_id,
        "graph_cell": graph_cell,
        "artifact_sha256": manifest["sha256"],
        "data_set": manifest["data_set"],
        "supply": manifest["supply"],
        "cap_rule": manifest["cap_rule"],
        "agreement_kind": manifest.get("agreement_kind"),
        "pricing": pricing,
        "w_known_ramp_fame_pctl": cfg.w_known_ramp_fame_pctl,
        "staged_reference_barred_from_candidacy": manifest[
            "staged_reference_barred_from_candidacy"],
        "pop_log_low": manifest["diagnostics"]["pop_log_low"],
        "pop_log_high": manifest["diagnostics"]["pop_log_high"],
        "ruler_frame_n": ruler.frame_n,
        "max_depth": len(ladder) - 1,
        "pairs": len(per_pair),
        "infeasible_cells": infeasible,
        "CRE_G2b": (
            {"assertions_run": g2b_checks, "depths": list(G2B_DEPTHS),
             "result": "PASS"}
            if cfg.w_known_ramp_fame_pctl else
            {"result": "N/A (P0 -- no device to test)",
             "p0_decomposition_check": {
                 "what": ("the same assert_cost_decomposition, run as an "
                          "instrument check so this cell's term shares are "
                          "verified against the search's own accumulated cost; "
                          "NOT the pre-registered CRE-G2(b)"),
                 "assertions_run": g2b_checks,
                 "depths": list(G2B_DEPTHS),
                 "result": "PASS"}}),
        "per_pair": per_pair,
    }
    if cfg.w_known_ramp_fame_pctl != 0.0:
        doc["CRE_G1b"] = g1b(cell_id, graph_cell, per_pair)
    else:
        doc["CRE_G1b"] = {"result": "N/A (this cell IS a P0 baseline)"}

    doc["seconds"] = round(time.time() - t0, 1)
    in_dir(f"cre_sweep_{cell_id}.json").write_text(
        json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  {len(infeasible)} infeasible (pair, depth) cells; "
          f"G1(b) {doc['CRE_G1b']['result']}; "
          f"G2(b) {g2b_checks} assertions", flush=True)
    print(f"wrote cre_sweep_{cell_id}.json ({doc['seconds']}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
