"""DRP- stage 3a: A0's two random-press runs, N_noise, DRP-G6 (power) and DRP-G7 (floor dead in
the band). A0 only, at ApiConfig() defaults. No arm is routed.

§5: N_noise = max(0.015, U) per famous stratum, where U is the 97.5th percentile of
|median over pairs of Δ| across 10,000 pair-bootstrap resamples, Δ = M_A0,rand(s=1)(band) −
M_A0,rand(s=2)(band). M(band) = the median fame_lb_pctl over the pooled interior slots of presses
7-10 (the CRE-C1 aggregation), measured interiors only (nulls counted, excluded; §3). Bootstrap
pinned as DRP-C1(2)'s: a fresh numpy.random.default_rng(20260928) per stratum;
rng.integers(0, n, size=(10000, n)) over the pairs in committed draw order; numpy.median per
resample; numpy.percentile (linear) at 97.5 of |medians|. Δ's pair set: the pairs whose four band
depths are feasible under BOTH s=1 and s=2 on A0 (§4).
DRP-G6 fires if N_noise > 0.025 in either famous stratum: stop before any arm is swept.

DRP-G7 (§6): the shipped effective_floor_raw returns non-zero for any drawn pair at k = 7 (seven
KNOWN exclusions), or max(pop_raw) > 1, or floor_relax_known != 0.15 -> stop.

Journeys (node ids) go to OUT; the committed output holds per-pair M values and verdicts only.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-drp-stage3a/drp_noise.py
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
from drp_common import (A0_GRAPH, A0_SHA, BAND, BOOT_N, BOOT_SEED, FAMOUS, G6_BAR,  # noqa: E402
                        HERE, INSTRUMENT_FLOOR, KNOWN, OUT, ApiConfig, Exclusion, Map,
                        effective_floor_raw, feasible, ladder, random_rng, write_json)

m = Map(A0_GRAPH, A0_SHA)
cfg = ApiConfig()
pairs = json.loads((HERE / "drp_pairs.json").read_text(encoding="utf-8"))
print(f"ApiConfig(): w_known_ramp_fame_pctl {cfg.w_known_ramp_fame_pctl}; floor_relax_known "
      f"{cfg.floor_relax_known}")

# ---- DRP-G7 ------------------------------------------------------------------------------------
g7 = {"floor_relax_known": cfg.floor_relax_known, "max_pop_raw": float(np.max(m.store.pop_raw)),
      "nonzero_at_k7": []}
dummy7 = [Exclusion(node=0, reason=KNOWN)] * 7  # effective_floor_raw counts reasons, not nodes
for sname, st in pairs["strata"].items():
    for p in st["pairs"]:
        base = min(float(m.store.pop_raw[p["source"]]), float(m.store.pop_raw[p["target"]]))
        f7 = effective_floor_raw(base, dummy7, cfg)
        if f7 != 0.0:
            g7["nonzero_at_k7"].append([sname, p["i"], f7])
g7_fire = bool(g7["nonzero_at_k7"]) or g7["max_pop_raw"] > 1 or cfg.floor_relax_known != 0.15
g7["verdict"] = "FAIL (stop; amendment)" if g7_fire else "PASS"
print(f"DRP-G7: {g7['verdict']} (max pop_raw {g7['max_pop_raw']}; non-zero at k=7: "
      f"{len(g7['nonzero_at_k7'])})")


def m_band(m: Map, lad) -> float:
    vals = [m.pl[v] for k in BAND for v in lad[k][0][1:-1] if m.measured[v]]
    return float(np.median(vals)) if vals else float("nan")


result = {"graph_sha256": m.sha, "DRP-G7": g7, "strata": {}}
journeys = {}
for sname in FAMOUS:
    t0 = time.time()
    rows = []
    for p in pairs["strata"][sname]["pairs"]:
        i, s, t = p["i"], p["source"], p["target"]
        lads = {seed: ladder(m, cfg, s, t, "random", random_rng(seed, sname, i)) for seed in (1, 2)}
        journeys[f"{sname}:{i}"] = {str(seed): [[path, stop] for path, stop in lad]
                                    for seed, lad in lads.items()}
        ok = all(feasible(lads[seed], k) for seed in (1, 2) for k in BAND)
        row = {"i": i, "band_feasible_both": ok}
        if ok:
            row["M_s1"], row["M_s2"] = m_band(m, lads[1]), m_band(m, lads[2])
            row["delta"] = row["M_s1"] - row["M_s2"]
            row["band_nulls"] = sum(1 for seed in (1, 2) for k in BAND
                                    for v in lads[seed][k][0][1:-1] if not m.measured[v])
        rows.append(row)
        if (i + 1) % 10 == 0:
            print(f"  {sname} {i + 1}/40  {time.time() - t0:.0f}s", flush=True)
    delta = np.array([r["delta"] for r in rows if r["band_feasible_both"]], dtype=np.float64)
    n = delta.size
    rng = np.random.default_rng(BOOT_SEED)
    med = np.median(delta[rng.integers(0, n, size=(BOOT_N, n))], axis=1)
    U = float(np.percentile(np.abs(med), 97.5))
    n_noise = max(INSTRUMENT_FLOOR, U)
    result["strata"][sname] = {"pairs": rows, "n_delta": int(n), "median_delta": float(np.median(delta)),
                               "U": U, "N_noise": n_noise}
    print(f"{sname}: Δ over {n} pairs; median Δ {np.median(delta):+.4f}; U {U:.5f}; "
          f"N_noise {n_noise:.4f}", flush=True)

g6_fire = any(v["N_noise"] > G6_BAR for v in result["strata"].values())
result["DRP-G6"] = {"bar": G6_BAR, "verdict": "FIRED (stop before any arm; report to the owner)"
                    if g6_fire else "PASS"}
print(f"DRP-G6: {result['DRP-G6']['verdict']}")
d = write_json(HERE / "drp_noise.json", result)
j = write_json(OUT / "drp_noise_journeys.json", journeys)
print(f"wrote drp_noise.json sha256 {d}\nwrote {OUT / 'drp_noise_journeys.json'} sha256 {j}")
