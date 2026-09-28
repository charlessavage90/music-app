"""DRP- stage 3a: DRP-C11 (headroom, b0) and DRP-G10 (its instrument check), on both supply maps.
Derivation only; decides nothing. Routes no arm: the only find_journey calls are G10's, which keep
per-pair pass/fail and no journey (DRP-AM5-I7).

DRP-C11 (§5, DRP-AM2 item 2): per drawn pair (all strata and the replication set) and supply
level, with no user exclusions, b0 = the smallest ceiling under which a journey with >= 1 interior
exists: the minimax over interiors, direct s-t edge forbidden, endpoints exempt, nulls at 0.0.
Own heap search (drp_common.bottleneck); never calls find_journey.

DRP-G10 (§6): for any pair and supply level, the shipped find_journey with ceiling exclusions
(every node with fame_lb_pctl > c, strictly, endpoints exempt, reason "ceiling") at c = b0 fails
to return an interior-bearing journey, or returns one at the next-lower distinct percentile.
Exact. If b0 is infinite (no interior-bearing journey exists at all), the check is that
find_journey with no exclusions returns none either.

At Seam A, §2.5's prior table gains the measured b0 distribution per stratum and supply level;
it annotates the priors and cannot change a read.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-drp-stage3a/drp_headroom.py
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
from drp_common import (A0_GRAPH, A0_SHA, HERE, S1_GRAPH, ApiConfig, Map, bottleneck,  # noqa: E402
                        ceiling_excludes, find_journey, write_json)

s1_sha = json.loads((HERE / "drp_s1_build.json").read_text(encoding="utf-8"))["artifact_sha256"]
g3 = json.loads((HERE / "drp_g3.json").read_text(encoding="utf-8"))
if g3["verdict"] != "PASS" or g3["artifact_sha256"] != s1_sha:
    print("REFUSING: DRP-G3 has not passed on this artifact; the arm is not measured", file=sys.stderr)
    sys.exit(2)
pairs = json.loads((HERE / "drp_pairs.json").read_text(encoding="utf-8"))
cfg = ApiConfig()


def interior_bearing(m: Map, s: int, t: int, excl: list) -> bool:
    res = find_journey(m.store, s, t, excl, cfg)
    return res is not None and len(res[0]) > 2


out = {"maps": {}}
for label, path, sha in (("DRP-S0", A0_GRAPH, A0_SHA), ("DRP-S1", S1_GRAPH, s1_sha)):
    m = Map(path, sha)
    t0 = time.time()
    per = {}
    g10_fail = []
    for sname, st in pairs["strata"].items():
        rows = []
        for p in st["pairs"]:
            s, t = p["source"], p["target"]
            b0 = bottleneck(m, s, t, set())
            if math.isinf(b0):
                ok = not interior_bearing(m, s, t, [])
            else:
                at = interior_bearing(m, s, t, ceiling_excludes(m, b0, s, t))
                k = int(np.searchsorted(m.distinct, b0, side="left"))
                assert m.distinct[k] == b0, "b0 is not a node percentile"
                below = interior_bearing(m, s, t, ceiling_excludes(m, float(m.distinct[k - 1]), s, t)) \
                    if k > 0 else False
                ok = at and not below
            if not ok:
                g10_fail.append([sname, p["i"]])
            rows.append({"i": p["i"], "b0": None if math.isinf(b0) else b0, "G10": ok})
        per[sname] = rows
        b = np.array([r["b0"] for r in rows if r["b0"] is not None])
        print(f"{label} {sname}: finite {b.size}/40; b0 min {b.min():.4f} p10 {np.percentile(b, 10):.4f} "
              f"median {np.median(b):.4f} p90 {np.percentile(b, 90):.4f} max {b.max():.4f}; "
              f"G10 fails {sum(1 for r in rows if not r['G10'])}  ({time.time() - t0:.0f}s)", flush=True)
    out["maps"][label] = {"graph_sha256": m.sha, "strata": per, "G10_failures": g10_fail}
    del m

fails = sum(len(v["G10_failures"]) for v in out["maps"].values())
out["DRP-G10"] = {"verdict": "PASS" if fails == 0 else f"FAIL ({fails}); DRP-C11 not reported until fixed"}
print(f"DRP-G10: {out['DRP-G10']['verdict']}")
d = write_json(HERE / "drp_headroom.json", out)
print(f"wrote drp_headroom.json sha256 {d}")
