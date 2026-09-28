"""DRP- stage 3b gates on the DRP-S0 row: DRP-G4, DRP-G5, DRP-G9 (a)-(f) with every red control,
and one harness-identity check of this stage's own. Reads the shards drp_sweep.py wrote; routes
only where a gate or red control says to, and keeps counts, never journeys, from those calls.

Governing: the pre-registration's §6 rows for DRP-G4, DRP-G5 and DRP-G9 (executed from the body),
§7 *swept* (a cell is swept when its ladders are done and G4, G5 and, for a ceiling cell, G9 pass).

H0 — harness identity (this session's decision, methodology): the generalised ladder must equal
stage 3a's drp_common.ladder, which DRP-G1 validated against the committed graph-descriptives
output. Checked two ways: drp_common.ladder re-run on A0 under the primary rule for DRP-T1, DRP-T2
and DRP-C8, compared path for path; and the A0 random-rule shards for DRP-T1/DRP-T2 against
stage 3a's seed-1 random journeys (drp_noise_journeys.json, sha committed in its README).

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-28-drp-stage3b/drp_gates_3b.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from drp_sweep import (CELLS, RULES, SETS, SHARDS, STAGE3A, cell_cfg, ceiling_step,  # noqa: E402
                       dc, interior_bearing, load_map, passed_list_ok)
from drp_common import (CEILING, DISLIKE, KNOWN, MAX_K, Exclusion, bottleneck,  # noqa: E402
                        ceiling_excludes, find_journey)

NOISE_JOURNEYS = dc.OUT / "drp_noise_journeys.json"
NOISE_SHA = "3d71ed00d76ccfd8b92b67ec50fe62941ccbb26775aac79c24834b6bedb802d1"
ROW = sys.argv[1] if len(sys.argv) > 1 else "DRP-S0"
MODE = sys.argv[2:]
ANCHOR = f"{ROW}P0"
RAMPS = [f"{ROW}P1", f"{ROW}P2"]
CEIL = f"{ROW}P3"


def shard(cell: str, sname: str, rule: str, identity: bool = False) -> dict:
    tag = f"{cell}__{sname}__{rule}" + ("__identity" if identity else "")
    return json.loads((SHARDS / f"{tag}.json").read_text(encoding="utf-8"))


def paths(sh: dict) -> dict:
    return {p["i"]: [d["path"] for d in p["depths"]] for p in sh["pairs"]}


def user_list(depths: list, k: int) -> list:
    return [Exclusion(node=depths[j]["victim"], reason=KNOWN) for j in range(k)]


m = load_map(ROW)
store = m.store
out: dict = {"row": ROW, "graph_sha256": m.sha}
harness = {shard(c, s, r)["harness_sha256"] for c in (ANCHOR, *RAMPS, CEIL) for s in SETS for r in RULES}
harness |= {shard(CEIL, s, r, True)["harness_sha256"] for s in SETS for r in RULES}
if len(harness) != 1:
    dc.refuse(f"shards were written by different harness versions: {sorted(harness)}")
out["harness_sha256"] = harness.pop()

A = {(s, r): shard(ANCHOR, s, r) for s in SETS for r in RULES}
AP = {key: paths(sh) for key, sh in A.items()}


# ---- DRP-G9 (one function, run per (set, rule) in parallel: `g9 SET RULE`) ----------------------
def g9_run(keys) -> dict:
    cfgc = cell_cfg(CEIL)
    b0 = {(sname, r["i"]): r["b0"] for sname, rows in
          json.loads((STAGE3A / "drp_headroom.json").read_text(encoding="utf-8"))["maps"][ROW]["strata"].items()
          for r in rows}
    g9 = {k: [] for k in ("a", "b", "c", "d", "e", "f")}
    red = {"e_press1_at_0.99_diverged": 0, "schedule_diverged_somewhere": 0, "f_dislike_fired": 0}
    n_relaxed = 0
    modes: dict = {}  # search mode per relaxed press; "bisected" means certification failed
    for key in keys:
        sname, rule = key
        ident = paths(shard(CEIL, sname, rule, True))
        for p in shard(CEIL, sname, rule)["pairs"]:
            i, s, t, dep = p["i"], p["source"], p["target"], p["depths"]
            base = AP[key][i]
            # (a) F_max = 1.0 everywhere reproduces the P0 cell at every press
            if ident[i] != base:
                g9["a"].append([*key, i])
            # (e) presses 0-3 identical to the P0 cell
            for k in range(4):
                if (dep[k]["path"] if k < len(dep) else "absent") != (base[k] if k < len(base) else "absent"):
                    g9["e"].append([*key, i, k])
            if [d["path"] for d in dep] != base:
                red["schedule_diverged_somewhere"] += 1
            # (e) red: press 1 with the ceiling at 0.99 must diverge from P0 on >= 1 pair
            if len(base) > 1 and base[0] is not None and len(base[0]) > 2:
                a0_lad = A[key]["pairs"][[q["i"] for q in A[key]["pairs"]].index(i)]["depths"]
                res, *_ = ceiling_step(m, cfgc, s, t, user_list(a0_lad, 1), 0.99)
                if (list(res[0]) if res else None) != base[1]:
                    red["e_press1_at_0.99_diverged"] += 1
            for k, d in enumerate(dep):
                ux = user_list(dep, k)
                # (f) the exact list passed, recorded at call time
                if not d["g9f_ok"]:
                    g9["f"].append([*key, i, k])
                if d["c"] is None:
                    if not math.isinf(bottleneck(m, s, t, {e.node for e in ux})):
                        g9["d"].append([*key, i, k, "no ceiling admitted, yet a bottleneck exists"])
                    continue
                # (b) no interior above its recorded c
                if d["path"] is not None and any(m.pl[v] > d["c"] for v in d["path"][1:-1]):
                    g9["b"].append([*key, i, k])
                # (d) c >= b0 at every press
                if b0[(sname, i)] is not None and d["c"] < b0[(sname, i)]:
                    g9["d"].append([*key, i, k, "c < b0"])
                if d["r"] > 0:
                    n_relaxed += 1
                    # (d) c equals the independent minimax bottleneck under this press's user list
                    if d["c"] != bottleneck(m, s, t, {e.node for e in ux}):
                        g9["d"].append([*key, i, k, "c != bottleneck"])
                    # (c) the next-lower distinct percentile below c, not below F_max(k), admits none
                    j = int(np.searchsorted(m.distinct, d["c"], side="left"))
                    lower = max(float(m.distinct[j - 1]), d["fmax"]) if j > 0 else d["fmax"]
                    if interior_bearing(find_journey(store, s, t, ux + ceiling_excludes(m, lower, s, t), cfgc)):
                        g9["c"].append([*key, i, k, "the next-lower ceiling admits a journey"])
                    # and the upper side, re-routed here rather than read from the sweep's record
                    if not interior_bearing(find_journey(store, s, t, ux + ceiling_excludes(m, d["c"], s, t), cfgc)):
                        g9["c"].append([*key, i, k, "the recorded c admits no journey"])
                    modes[d["search"]] = modes.get(d["search"], 0) + 1
                # (f) red: the ceiling passed as DISLIKE at press 10 must fail the check
                if k == 10:
                    bad = ux + [Exclusion(node=e.node, reason=DISLIKE)
                                for e in ceiling_excludes(m, d["c"], s, t)]
                    if not passed_list_ok(m, cfgc, s, t, bad, ux, k):
                        red["f_dislike_fired"] += 1
        print(f"  G9 {key} done", flush=True)
    return {"g9": g9, "red": red, "n_relaxed": n_relaxed, "modes": modes}


G9_DIR = SHARDS.parent / "gates"  # partials stay outside the repo; the combined verdict is committed
if MODE:
    if len(MODE) != 3 or MODE[0] != "g9" or (MODE[1], MODE[2]) not in A:
        dc.refuse("usage: drp_gates_3b.py ROW [g9 SET RULE]")
    res = g9_run([(MODE[1], MODE[2])])
    res["harness_sha256"] = out["harness_sha256"]
    dc.write_json(G9_DIR / f"g9__{MODE[1]}__{MODE[2]}.json", res)
    print(f"DRP-G9 partial {MODE[1:]}: { {k: len(v) for k, v in res['g9'].items()} } reds {res['red']}")
    sys.exit(0)


# ---- H0 ----------------------------------------------------------------------------------------
if ROW == "DRP-S0":
    cfg0 = cell_cfg(ANCHOR)
    h0 = {"primary_vs_drp_common_ladder": [], "random_vs_stage3a_noise": []}
    for sname in ("DRP-T1", "DRP-T2", "DRP-C8"):
        pairs = {p["i"]: p for p in A[(sname, "primary")]["pairs"]}
        for i, p in pairs.items():
            ref = [path for path, _stop in dc.ladder(m, cfg0, p["source"], p["target"], "primary")]
            if ref != AP[(sname, "primary")][i]:
                h0["primary_vs_drp_common_ladder"].append([sname, i])
    if dc.sha256_of(NOISE_JOURNEYS) != NOISE_SHA:
        dc.refuse("stage 3a's noise journeys do not match their committed sha")
    noise = json.loads(NOISE_JOURNEYS.read_text(encoding="utf-8"))
    for sname in ("DRP-T1", "DRP-T2"):
        for i, got in AP[(sname, "random")].items():
            ref = [path for path, _stop in noise[f"{sname}:{i}"]["1"]]
            if ref != got:
                h0["random_vs_stage3a_noise"].append([sname, i])
    h0["verdict"] = "PASS" if not any(h0[k] for k in h0) else "FAIL"
    out["H0"] = h0
    print(f"H0 harness identity: {h0['verdict']} {h0}", flush=True)

# ---- DRP-G4 ------------------------------------------------------------------------------------
g4 = {"violations": [], "red_press1_diverged": {}}
for cell in (*RAMPS, CEIL):
    upto = 3 if cell == CEIL else 0
    red = 0
    for key in A:
        got = paths(shard(cell, *key))
        for i, base in AP[key].items():
            for k in range(upto + 1):
                b = base[k] if k < len(base) else "absent"
                g = got[i][k] if k < len(got[i]) else "absent"
                if b != g:
                    g4["violations"].append([cell, *key, i, k])
            if cell != CEIL and len(base) > 1 and len(got[i]) > 1 and base[1] != got[i][1]:
                red += 1
    if cell != CEIL:
        g4["red_press1_diverged"][cell] = red
red_ok = all(v >= 1 for v in g4["red_press1_diverged"].values())
g4["verdict"] = "PASS" if not g4["violations"] and red_ok else "FAIL"
g4["red_control"] = "fired" if red_ok else "BLIND"
out["DRP-G4"] = g4
print(f"DRP-G4: {g4['verdict']}; violations {len(g4['violations'])}; press-1 red "
      f"{g4['red_press1_diverged']}", flush=True)

# ---- DRP-G5 ------------------------------------------------------------------------------------
g5 = {"violations": [], "red_ceiling_as_known_fired": 0}
for cell in (*RAMPS, CEIL):
    ramp = cell_cfg(cell).w_known_ramp_fame_pctl
    for key in A:
        for p in shard(cell, *key)["pairs"]:
            for k in (1, 10):
                if k >= len(p["depths"]) or p["depths"][k]["path"] is None:
                    continue
                d = p["depths"][k]
                sigma = sum(float(store.fame_lb_pctl[v]) for v in d["path"][1:-1])
                if abs(ramp * d["n_known_passed"] * sigma - ramp * k * sigma) > 1e-9:
                    g5["violations"].append([cell, *key, p["i"], k])
                if cell == CEIL and k == 10:  # red: the ceiling passed as KNOWN
                    k_red = d["n_known_passed"] + d["n_ceiling"]
                    if abs(ramp * k_red * sigma - ramp * k * sigma) > 1e-9:
                        g5["red_ceiling_as_known_fired"] += 1
g5["verdict"] = "PASS" if not g5["violations"] else "FAIL"
g5["red_control"] = "fired" if g5["red_ceiling_as_known_fired"] >= 1 else "BLIND"
out["DRP-G5"] = g5
print(f"DRP-G5: {g5['verdict']}; red (ceiling as KNOWN) fired on {g5['red_ceiling_as_known_fired']}",
      flush=True)

parts = []
for key in A:
    f = G9_DIR / f"g9__{key[0]}__{key[1]}.json"
    if not f.exists():
        dc.refuse(f"DRP-G9 partial missing: {f.name}; run `g9 {key[0]} {key[1]}` first")
    parts.append(json.loads(f.read_text(encoding="utf-8")))
    if parts[-1]["harness_sha256"] != out["harness_sha256"]:
        dc.refuse(f"{f.name} was computed on another harness version")
g9 = {k: sum((pt["g9"][k] for pt in parts), []) for k in ("a", "b", "c", "d", "e", "f")}
red = {k: sum(pt["red"][k] for pt in parts) for k in parts[0]["red"]}
n_relaxed = sum(pt["n_relaxed"] for pt in parts)
modes: dict = {}
for pt in parts:
    for k, v in pt["modes"].items():
        modes[k] = modes.get(k, 0) + v
g9_viol = sum(len(v) for v in g9.values())
reds_ok = all(v >= 1 for v in red.values())
out["DRP-G9"] = {"violations": g9, "n_relaxed_presses_checked": n_relaxed, "search_modes": modes, "red_controls": red,
                 "verdict": "PASS" if g9_viol == 0 and reds_ok else "FAIL",
                 "red_control": "all fired" if reds_ok else "BLIND"}
print(f"DRP-G9: {out['DRP-G9']['verdict']}; violations per condition "
      f"{ {k: len(v) for k, v in g9.items()} }; relaxed presses checked {n_relaxed} {modes}; reds {red}", flush=True)

d = dc.write_json(HERE / f"drp_gates_{ROW}.json", out)
print(f"wrote drp_gates_{ROW}.json sha256 {d}")
