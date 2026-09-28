"""DRP- stage 3a: DRP-G1 (router-harness identity) or DRP-G1r (its red control). A0 only.

DRP-G1 (§6): on A0, over graph-descriptives' 80 pairs (its FAMOUS and MID sets, seed 20260927),
any field graph_descriptives.py:249-261 prints per pair -- the medians at d0, d5, d10 and d20 at
3 dp ('-' where the ladder stopped), d20 - d0, interior n at d0 and d20, the stop rule at d0, the
ladder stop (rule and k) -- differs from graph_descriptives.out.txt on any pair. Exact equality.

DRP-G1r (§6): the same harness with w_known_ramp_fame_pctl = 0.015 (outside the lattice's
0.01/0.02/0.03) must diverge from the committed output on >= 1 of the 80 pairs. Records only
"diverged: yes/no" and the count. No journey is kept.

Writes drp_g1.json or drp_g1r.json: per-pair match booleans and the verdict. No interior is named
or kept: the compared rows carry endpoint names and interior MEDIANS only, which is what the
committed graph-descriptives output already holds.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-drp-stage3a/drp_g1.py g1     # or g1r
"""
from __future__ import annotations

import dataclasses
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
from drp_common import (A0_GRAPH, A0_SHA, GD_OUT, HERE, PF_FILE, ApiConfig, Map,  # noqa: E402
                        ladder, replication_pairs, write_json)

MODE = sys.argv[1] if len(sys.argv) > 1 else ""
if MODE not in ("g1", "g1r"):
    print("usage: drp_g1.py g1|g1r", file=sys.stderr)
    sys.exit(64)
DEPTHS = (0, 5, 10, 20)

m = Map(A0_GRAPH, A0_SHA)
print(f"pathfinding: {PF_FILE}")
cfg = ApiConfig()
if MODE == "g1r":
    cfg = dataclasses.replace(cfg, w_known_ramp_fame_pctl=0.015)
print(f"mode {MODE}; w_known_ramp_fame_pctl {cfg.w_known_ramp_fame_pctl}")

# committed rows, parsed exactly as the stage-1 critique's probe parsed them
GD_ROWS: dict[str, list[list[str]]] = {}
sec = None
for line in GD_OUT.read_text(encoding="utf-8").splitlines():
    if line.startswith("### FAMOUS: per pair"):
        sec = "FAMOUS"
    elif line.startswith("### MID: per pair"):
        sec = "MID"
    elif line.startswith("###"):
        sec = None
    elif sec and line.startswith("| ") and not line.startswith("| #"):
        GD_ROWS.setdefault(sec, []).append([c.strip() for c in line.strip("|").split("|")])
assert len(GD_ROWS["FAMOUS"]) == 40 and len(GD_ROWS["MID"]) == 40


def row(i: int, s: int, t: int, lad: list) -> list[str]:
    """graph_descriptives.py:249-261, field for field."""
    d = {}
    for k in DEPTHS:
        if k < len(lad) and lad[k][0] is not None:
            p = lad[k][0]
            d[k] = {"median": m.interior_median(p), "n": len(p) - 2, "rule": lad[k][1]}
    last = lad[-1]
    if last[0] is None:
        stop = f"no_path at k={len(lad) - 1}"
    elif len(last[0]) <= 2:
        stop = f"empty_interior at k={len(lad) - 1}"
    else:
        stop = "-"
    cell = [f"{d[k]['median']:.3f}" if k in d else "-" for k in DEPTHS]
    delta = f"{d[20]['median'] - d[0]['median']:+.3f}" if 0 in d and 20 in d else "-"
    ln = f"{d[0]['n'] if 0 in d else '-'}/{d[20]['n'] if 20 in d else '-'}"
    return [str(i), f"{m.store.names[s]} ({m.pctl[s]:.3f})", f"{m.store.names[t]} ({m.pctl[t]:.3f})",
            *cell, delta, ln, d[0]["rule"] if 0 in d else "-", stop]


fam, mid = replication_pairs(m)
result = {"mode": MODE, "graph_sha256": m.sha, "ramp": cfg.w_known_ramp_fame_pctl, "sets": {}}
diverged = 0
for name, pairs in (("FAMOUS", fam), ("MID", mid)):
    t0 = time.time()
    flags = []
    for i, (s, t) in enumerate(pairs, 1):
        lad = ladder(m, cfg, s, t, "primary")
        mine = row(i, s, t, lad)
        ok = mine == GD_ROWS[name][i - 1]
        flags.append(ok)
        if not ok:
            diverged += 1
            if MODE == "g1":  # a G1 failure must be diagnosable; endpoint names + medians only
                print(f"  DIVERGES {name} {i}:\n    mine {mine}\n    gd   {GD_ROWS[name][i - 1]}")
        if i % 10 == 0:
            print(f"  {name} {i}/40  {time.time() - t0:.0f}s", flush=True)
    result["sets"][name] = {"match": flags}

if MODE == "g1":
    result["verdict"] = "PASS" if diverged == 0 else "FAIL"
    print(f"DRP-G1: {80 - diverged} of 80 pairs identical; verdict {result['verdict']}")
else:
    result["diverging_pairs"] = diverged
    result["verdict"] = "PASS (red control fired)" if diverged >= 1 else "FAIL (G1 blind to the ramp)"
    for s in result["sets"].values():  # G1r keeps the count only
        s.pop("match")
    print(f"DRP-G1r: diverged {'yes' if diverged else 'no'}; count {diverged}; verdict {result['verdict']}")
digest = write_json(HERE / f"drp_{MODE}.json", result)
print(f"wrote drp_{MODE}.json sha256 {digest}")
