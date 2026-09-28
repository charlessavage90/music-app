"""DRP- stage 3b: the DRP-S0 row's sweeps (A0, DRP-S0P1, DRP-S0P2, DRP-S0P3). Decides nothing.

Governing document: docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md
(`DRP-`), executed from the body: §2.1 (the cells; DRP-P3's schedule, exclusion set and
relaxation), §4 (the ladder, both press rules, the pair sets), §5 DRP-C9 (term accounting), §8
stage 3b (Seam B: one committed JSON per cell holding the artifact sha, the cell id, per-depth
journeys as node ids, per-term stats and the dropped set).

Routing is the SHIPPED find_journey, loaded and identity-asserted by stage 3a's drp_common (§4).
Every instrument drp_common provides is reused, never retyped: the pair set, victim_key, the
random-press generator, ceiling_excludes, f_max, the feasibility rule.

Sealing (§8): committed outputs hold node ids only. Nothing here resolves an interior name.

Two subcommands:

    shard CELL SET RULE [--identity]  -> OUT3B/shards/<CELL>__<SET>__<RULE>[__identity].json
    merge CELL                        -> HERE/cells/<CELL>.json   (the committed Seam-B file)

`--identity` is DRP-G9(a)'s run (a DRP-P3 cell with F_max = 1.0 at every press); its shard is
read by the gate script only and never merged into a cell.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-28-drp-stage3b/drp_sweep.py shard DRP-S0P0 DRP-T1 primary
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
STAGE3A = HERE.parent / "2026-09-27-drp-stage3a"
sys.path.insert(0, str(STAGE3A))
import drp_common as dc  # noqa: E402
from drp_common import (A0_GRAPH, A0_SHA, CEILING, DISLIKE, KNOWN, MAX_K, ApiConfig,  # noqa: E402
                        Exclusion, Map, avoidance_map, ceiling_excludes,
                        effective_floor_raw, f_max, find_journey, random_rng)

OUT3B = Path(r"C:\unsung-fast\drp-stage3b")
SHARDS = OUT3B / "shards"
CELLS_DIR = HERE / "cells"
SETS = ("DRP-T1", "DRP-T2", "DRP-MID", "DRP-C8")
RULES = ("primary", "random")
RANDOM_SEED = 1  # §4: seed 1 in every cell (seed 2 was A0-only, for N_noise, at 3a)

# §2.1 / §2.2. Pricing overrides are the ramp alone; every other ApiConfig field at its default.
# The DRP-S1 cells are listed so 3c reuses one harness; this session runs none of them (§8 seams).
CELLS = {
    "DRP-S0P0": {"supply": "DRP-S0", "pricing": "DRP-P0", "ramp": None, "ceiling": False},
    "DRP-S0P1": {"supply": "DRP-S0", "pricing": "DRP-P1", "ramp": 0.02, "ceiling": False},
    "DRP-S0P2": {"supply": "DRP-S0", "pricing": "DRP-P2", "ramp": 0.03, "ceiling": False},
    "DRP-S0P3": {"supply": "DRP-S0", "pricing": "DRP-P3", "ramp": None, "ceiling": True},
    "DRP-S1P0": {"supply": "DRP-S1", "pricing": "DRP-P0", "ramp": None, "ceiling": False},
    "DRP-S1P1": {"supply": "DRP-S1", "pricing": "DRP-P1", "ramp": 0.02, "ceiling": False},
    "DRP-S1P2": {"supply": "DRP-S1", "pricing": "DRP-P2", "ramp": 0.03, "ceiling": False},
    "DRP-S1P3": {"supply": "DRP-S1", "pricing": "DRP-P3", "ramp": None, "ceiling": True},
}


def cell_cfg(cell: str) -> ApiConfig:
    ramp = CELLS[cell]["ramp"]
    return ApiConfig() if ramp is None else ApiConfig(w_known_ramp_fame_pctl=ramp)


def load_map(supply: str) -> Map:
    if supply == "DRP-S0":
        return Map(A0_GRAPH, A0_SHA)
    s1_sha = json.loads((STAGE3A / "drp_s1_build.json").read_text(encoding="utf-8"))["artifact_sha256"]
    g3 = json.loads((STAGE3A / "drp_g3.json").read_text(encoding="utf-8"))
    if g3["verdict"] != "PASS" or g3["artifact_sha256"] != s1_sha:
        dc.refuse("DRP-G3 has not passed on this artifact; the arm is not swept")
    return Map(dc.S1_GRAPH, s1_sha)


def interior_bearing(res) -> bool:
    return res is not None and len(res[0]) > 2


# ---- one press of a ceiling cell (§2.1 DRP-P3 row) ---------------------------------------------
def ceiling_step(m: Map, cfg, s: int, t: int, user_ex: list, fm: float):
    """F_max(k) first (DRP-AM5-F1); otherwise the lowest distinct percentile ABOVE it at which the
    shipped find_journey returns an interior-bearing journey. Returns (res, passed, c, r, calls).

    The search is a bisection over the frame's distinct percentiles above fm. It relies on one
    property, argued from source and checked by DRP-G9(c): whether find_journey returns an
    interior-bearing journey depends only on whether an s-t path with >= 1 interior avoids the
    excluded set (find_path returns the cheapest path; a two-card one triggers the detour with the
    direct edge forbidden, pathfinding.py:219-231), and raising c only shrinks that set.
    If no ceiling admits one, the press is routed with the user exclusions alone and the (pair,
    depth) falls under §4's drop rule (DRP-AM2 item 1); c and r are then None.
    """
    passed = user_ex + ceiling_excludes(m, fm, s, t)
    res = find_journey(m.store, s, t, passed, cfg)
    calls = 1
    if interior_bearing(res):
        return res, passed, fm, 0.0, calls
    cands = m.distinct[m.distinct > fm]
    top = user_ex + ceiling_excludes(m, float(cands[-1]), s, t)
    res_top = find_journey(m.store, s, t, top, cfg)
    calls += 1
    if not interior_bearing(res_top):
        return find_journey(m.store, s, t, user_ex, cfg), user_ex, None, None, calls + 1
    lo, hi, best = 0, len(cands) - 1, (res_top, top)
    while lo < hi:
        mid = (lo + hi) // 2
        trial = user_ex + ceiling_excludes(m, float(cands[mid]), s, t)
        r_mid = find_journey(m.store, s, t, trial, cfg)
        calls += 1
        if interior_bearing(r_mid):
            hi, best = mid, (r_mid, trial)
        else:
            lo = mid + 1
    c = float(cands[lo])
    res, passed = best
    return res, passed, c, c - fm, calls


# ---- DRP-G9(f)'s per-press check, recorded at call time on the exact list passed --------------
def passed_list_ok(m: Map, cfg, s: int, t: int, passed: list, user_ex: list, k: int) -> bool:
    n_known = sum(1 for e in passed if e.reason == KNOWN)
    n_dislike = sum(1 for e in passed if e.reason == DISLIKE)
    n_other = sum(1 for e in passed if e.reason not in (KNOWN, CEILING))
    base = min(float(m.store.pop_raw[s]), float(m.store.pop_raw[t]))
    same_floor = effective_floor_raw(base, passed, cfg) == effective_floor_raw(base, user_ex, cfg)
    avoid = avoidance_map(m.store, [e.node for e in passed if e.reason == DISLIKE], cfg)
    return n_known == k and n_dislike == 0 and n_other == 0 and same_floor and not avoid


# ---- DRP-C9: per-term cost along the returned path (DRP-AM5-I14) -------------------------------
def edge_score(m: Map, u: int, v: int) -> float:
    lo, hi = m.off[u], m.off[u + 1]
    j = lo + int(np.searchsorted(m.store.neighbours[lo:hi], v))
    assert j < hi and m.nbr[j] == v, f"no edge {u}-{v}"
    return float(m.store.scores[j])


def term_costs(m: Map, cfg, path: list, passed: list) -> dict:
    """Each term of pathfinding.py:155-170, summed over the path's edges, recomputed from cfg, the
    request's k (the KNOWN entries actually passed) and the shipped effective_floor_raw."""
    st = m.store
    s, t = path[0], path[-1]
    floor_raw = effective_floor_raw(min(float(st.pop_raw[s]), float(st.pop_raw[t])), passed, cfg)
    avoid = avoidance_map(st, [e.node for e in passed if e.reason == DISLIKE], cfg)
    ramp = cfg.w_known_ramp_fame_pctl * sum(1 for e in passed if e.reason == KNOWN)
    acc = dict.fromkeys(("sim", "jump", "floor", "avoid", "hub", "hop", "ramp"), 0.0)
    sims = []
    for u, v in zip(path, path[1:]):
        sim = edge_score(m, u, v)
        sims.append(sim)
        pu, pv = float(st.pop_raw[u]), float(st.pop_raw[v])
        acc["sim"] += cfg.w_sim * (1.0 - sim)
        acc["jump"] += cfg.w_jump * abs(pu - pv)
        acc["floor"] += cfg.w_floor * max(0.0, floor_raw - pv)
        acc["avoid"] += cfg.w_avoid * avoid.get(v, 0.0)
        acc["hub"] += cfg.w_degree_hub * float(st.degree_hub_penalty[v])
        acc["hop"] += cfg.w_hop
        if ramp != 0.0 and v != t:
            acc["ramp"] += ramp * float(st.fame_lb_pctl[v])
    return {"terms": acc, "sim_edges": sims, "floor_raw": floor_raw}


# ---- the ladder (§4), generalised over the cell ------------------------------------------------
def run_ladder(m: Map, cfg, s: int, t: int, rule: str, rng, ceiling: bool, schedule) -> list:
    """Presses 0..MAX_K, every press KNOWN, exclusions cumulative; stops after a None journey or an
    empty interior. Identical to drp_common.ladder when `ceiling` is False (the victim chain and
    every find_journey call), which the gate script re-asserts against drp_common.ladder itself."""
    user_ex: list = []
    out = []
    for k in range(MAX_K + 1):
        rec = {"k": k}
        if ceiling:
            fm = schedule(k)
            res, passed, c, r, calls = ceiling_step(m, cfg, s, t, user_ex, fm)
            rec.update(fmax=fm, c=c, r=r, calls=calls,
                       g9f_ok=passed_list_ok(m, cfg, s, t, passed, user_ex, k),
                       n_ceiling=sum(1 for e in passed if e.reason == CEILING))
        else:
            passed = user_ex
            res = find_journey(m.store, s, t, passed, cfg)
        rec["n_known_passed"] = sum(1 for e in passed if e.reason == KNOWN)
        if res is None:
            rec.update(path=None, stop="none")
            out.append(rec)
            break
        path, stop = list(res[0]), res[1]
        rec.update(path=path, stop=stop, **term_costs(m, cfg, path, passed))
        out.append(rec)
        interior = path[1:-1]
        if not interior:
            break
        if rule == "primary":
            victim = min(interior, key=m.key)
        elif rule == "random":
            victim = interior[rng.randrange(len(interior))]
        else:
            raise ValueError(rule)
        rec["victim"] = victim  # a node id; DRP-G9(c)/(d) rebuild each press's user list from it
        user_ex = user_ex + [Exclusion(node=victim, reason=KNOWN)]
    return out


def dump_compact(path: Path, obj: dict) -> str:
    """One pair per line: small enough to commit, still diffable pair by pair."""
    import hashlib
    path.parent.mkdir(parents=True, exist_ok=True)
    head = {k: v for k, v in obj.items() if k != "pairs"}
    lines = ["{" + json.dumps(head, ensure_ascii=False)[1:-1] + ', "pairs": [']
    rows = [json.dumps(p, ensure_ascii=False, separators=(",", ":")) for p in obj["pairs"]]
    lines.append(",\n".join(rows))
    lines.append("]}")
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def shard(cell: str, sname: str, rule: str, identity: bool) -> None:
    spec = CELLS[cell]
    if identity and not spec["ceiling"]:
        dc.refuse("--identity is DRP-G9(a)'s run and applies to a DRP-P3 cell only")
    m = load_map(spec["supply"])
    cfg = cell_cfg(cell)
    schedule = (lambda k: 1.0) if identity else f_max
    pairs = json.loads((STAGE3A / "drp_pairs.json").read_text(encoding="utf-8"))
    rows, t0 = [], time.time()
    for p in pairs["strata"][sname]["pairs"]:
        i, s, t = p["i"], p["source"], p["target"]
        rng = random_rng(RANDOM_SEED, sname, i) if rule == "random" else None
        lad = run_ladder(m, cfg, s, t, rule, rng, spec["ceiling"], schedule)
        rows.append({"i": i, "source": s, "target": t, "depths": lad})
        print(f"  {cell} {sname} {rule} pair {i}: {len(lad)} depths  {time.time() - t0:.0f}s", flush=True)
    tag = f"{cell}__{sname}__{rule}" + ("__identity" if identity else "")
    obj = {"cell": cell, "set": sname, "rule": rule, "identity_schedule": identity,
           "graph_sha256": m.sha, "harness_sha256": dc.sha256_of(Path(__file__)),
           "w_known_ramp_fame_pctl": cfg.w_known_ramp_fame_pctl, "seconds": round(time.time() - t0, 1),
           "pairs": rows}
    d = dump_compact(SHARDS / f"{tag}.json", obj)
    print(f"wrote {tag}.json sha256 {d}", flush=True)


def merge(cell: str) -> None:
    """The Seam-B file: every (set, rule) shard of one cell, plus the cell's own infeasible set.
    §4's cross-cell drop rule needs all eight cells, so the union is formed at *complete* (3d)."""
    spec = CELLS[cell]
    parts, dropped, shas = {}, [], set()
    for sname in SETS:
        for rule in RULES:
            sh = json.loads((SHARDS / f"{cell}__{sname}__{rule}.json").read_text(encoding="utf-8"))
            assert not sh["identity_schedule"]
            shas.add((sh["graph_sha256"], sh["harness_sha256"]))
            parts.setdefault(sname, {})[rule] = sh["pairs"]
            for p in sh["pairs"]:
                lad = p["depths"]
                for k in range(MAX_K + 1):
                    ok = k < len(lad) and lad[k]["path"] is not None and len(lad[k]["path"]) > 2
                    if not ok:
                        dropped.append([sname, rule, p["i"], k])
    if len(shas) != 1:
        dc.refuse(f"{cell}: shards disagree on graph or harness sha: {sorted(shas)}")
    (gsha, hsha), = shas
    cfg = cell_cfg(cell)
    obj = {"cell": cell, "supply": spec["supply"], "pricing": spec["pricing"],
           "graph_sha256": gsha, "harness_sha256": hsha,
           "w_known_ramp_fame_pctl": cfg.w_known_ramp_fame_pctl,
           "ceiling": "F_max(k) = 1.0 for k <= 3, max(0, 1 - 0.015(k - 3)) for k >= 4" if spec["ceiling"] else None,
           "random_seed": RANDOM_SEED,
           "dropped_in_this_cell": dropped,
           "pairs": [{"set": sname, "rule": rule, **p}
                     for sname in SETS for rule in RULES for p in parts[sname][rule]]}
    d = dump_compact(CELLS_DIR / f"{cell}.json", obj)
    print(f"wrote cells/{cell}.json sha256 {d}  ({len(dropped)} infeasible (set, rule, pair, depth))")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "shard" and len(a) in (4, 5):
        if a[1] not in CELLS or a[2] not in SETS or a[3] not in RULES:
            dc.refuse(f"unknown cell/set/rule: {a[1:4]}")
        shard(a[1], a[2], a[3], identity=(len(a) == 5 and a[4] == "--identity"))
    elif a and a[0] == "merge" and len(a) == 2 and a[1] in CELLS:
        merge(a[1])
    else:
        dc.refuse(__doc__.split("Two subcommands:")[1].split("`--identity`")[0].strip())
