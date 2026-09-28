"""DRP-AM1 critique, probe 2: A0 only, shipped defaults. A PROXY for N_noise and a partial DRP-G1.

NOT the document's draw: the DRP pair set (seed 20260928, strata T1/T2/MID) is never drawn here.
Pairs are graph-descriptives' own FAMOUS set (seed 20260927, both endpoints >= 0.95), regenerated
by that script's rule (copied below), i.e. the DRP-C8 replication set, which mixes the two DRP
famous strata. No arm is built or routed; ApiConfig() is never modified.

Per pair, three ladders to press 10 on A0 with the shipped find_journey:
  - primary: cre_ladder.victim_key (imported), as graph-descriptives did;
  - random interior, s = 1 and s = 2, one random.Random(f"DRP:{s}:FAMOUS:{i}") instance per pair
    (i = 0-based pair index), consumed once per press by rng.randrange(len(interior)). This is ONE
    reading of DRP §4's companion rule, which does not say whether the instance is per pair or per
    press, the index base, or the draw call.

Computes M(band) = median fame_lb_pctl over pooled interior slots at presses 7..10 (nulls excluded),
Delta = M_rand(s=1) - M_rand(s=2), U = 97.5th pct of |median over pairs of Delta| over 10,000 pair
bootstrap resamples (numpy default_rng(20260928) -- the document does not name the generator).

Also checks the victim_key ladder against graph_descriptives.out.txt at d0/d5/d10 (3 dp), d0
interior count and d0 stop rule: a partial run of DRP-G1's comparison on the FAMOUS half.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-drp-prereg-critique/drp_noise_proxy.py
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import struct
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A0 = Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin")
A0_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
GD_OUT = ROOT / "builder/analysis/2026-09-27-issue-200-graph-descriptives/graph_descriptives.out.txt"
SEED_GD = 20260927
BAND = (7, 8, 9, 10)
MAX_K = 10


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


got = sha(A0)
side = json.loads(A0.with_name(A0.name + ".json").read_text(encoding="utf-8"))["sha256"]
if not (got == side == A0_SHA):
    print(f"REFUSING: {got} / sidecar {side}", file=sys.stderr)
    sys.exit(2)
print(f"sha256 OK {A0.name} {got}")

from artistpath_api import pathfinding as _pf  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import KNOWN, Exclusion, find_journey  # noqa: E402

_pf_file = Path(_pf.__file__).resolve()
assert (ROOT / "api/src").resolve() in _pf_file.parents, _pf_file
sys.path.insert(0, str(ROOT / "builder/analysis/2026-08-03-cap-reevaluation"))
from cre_ladder import victim_key  # noqa: E402
assert Path(sys.modules["artistpath_api.pathfinding"].__file__).resolve() == _pf_file
assert sys.modules["artistpath_api.pathfinding"].find_journey is find_journey
print(f"pathfinding: {_pf_file}")

payload = A0.read_bytes()
store = GraphStore.from_bytes(payload)
hdr = struct.Struct("<4sIIIQ")
_m, _v, n, e, ml = hdr.unpack_from(payload)
cur = hdr.size + (n + 1) * 4 + e * 4 + e * 4 + e
fame = json.loads(payload[cur: cur + ml])["fame_lb"]
del payload
pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
measured = np.array([v is not None for v in fame])
cfg = ApiConfig()
print(f"ApiConfig() ramp {cfg.w_known_ramp_fame_pctl} floor_relax_known {cfg.floor_relax_known}")

# graph-descriptives' draw, copied (FAMOUS is drawn first from one Random(SEED) instance)
ids = np.arange(store.artist_count)
famous_pool = [int(i) for i in ids[measured & (pctl >= 0.95)]]
rng = random.Random(SEED_GD)
seen, pairs = set(), []
while len(pairs) < 40:
    s, t = rng.sample(famous_pool, 2)
    k = frozenset((s, t))
    if k in seen:
        continue
    seen.add(k)
    pairs.append((s, t))

fame_measured = np.where(measured, pctl, np.nan)
vkey = victim_key(fame_measured, store.pop_raw, store.mbids)


def ladder(s, t, chooser):
    ex, out = [], {}
    for k in range(MAX_K + 1):
        res = find_journey(store, s, t, ex, cfg)
        if res is None:
            break
        path, rule = res
        out[k] = (path, rule)
        interior = path[1:-1]
        if not interior:
            break
        ex = ex + [Exclusion(node=chooser(interior), reason=KNOWN)]
    return out


def med(vals):
    v = [float(pctl[x]) for x in vals if measured[x]]
    return float(np.median(v)) if v else float("nan")


def band_m(lad):
    if not all(k in lad and lad[k][0][1:-1] for k in BAND):
        return float("nan")
    return med([x for k in BAND for x in lad[k][0][1:-1]])


# parse committed FAMOUS rows
gd = []
sec = False
for line in GD_OUT.read_text(encoding="utf-8").splitlines():
    if line.startswith("### FAMOUS: per pair"):
        sec = True
    elif line.startswith("### MID: per pair"):
        sec = False
    elif sec and re.match(r"^\| \d+ \|", line):
        c = [x.strip() for x in line.strip("|").split("|")]
        gd.append({"d0": c[3], "d5": c[4], "d10": c[5], "n0": c[8].split("/")[0], "rule0": c[9]})
assert len(gd) == 40

t0 = time.time()
rows = []
for i, (s, t) in enumerate(pairs):
    lv = ladder(s, t, lambda it: min(it, key=vkey))
    r1 = random.Random(f"DRP:1:FAMOUS:{i}")
    l1 = ladder(s, t, lambda it: it[r1.randrange(len(it))])
    r2 = random.Random(f"DRP:2:FAMOUS:{i}")
    l2 = ladder(s, t, lambda it: it[r2.randrange(len(it))])
    rows.append((s, t, lv, l1, l2))
    if (i + 1) % 10 == 0:
        print(f"  {i + 1}/40  {time.time() - t0:.0f}s", flush=True)

print("\n## Partial DRP-G1: victim_key ladder vs graph_descriptives.out.txt (FAMOUS half, d0/d5/d10)")
mism = 0
for i, (s, t, lv, _l1, _l2) in enumerate(rows):
    mine = {f"d{k}": f"{med(lv[k][0][1:-1]):.3f}" for k in (0, 5, 10)}
    mine["n0"] = str(len(lv[0][0]) - 2)
    mine["rule0"] = lv[0][1]
    diff = {k: (mine[k], gd[i][k]) for k in mine if mine[k] != gd[i][k]}
    if diff:
        mism += 1
        print(f"  pair {i + 1}: MISMATCH {diff}")
print(f"pairs matching on every compared field: {40 - mism} of 40")

print("\n## N_noise proxy (random-press seed 1 vs seed 2, band 7-10 pooled)")
m_v = np.array([band_m(r[2]) for r in rows])
m_1 = np.array([band_m(r[3]) for r in rows])
m_2 = np.array([band_m(r[4]) for r in rows])
m_v0 = np.array([med(r[2][0][0][1:-1]) for r in rows])
ok = ~(np.isnan(m_1) | np.isnan(m_2))
delta = (m_1 - m_2)[ok]
print(f"pairs with all band depths feasible on both seeds: {int(ok.sum())} of 40")
print(f"victim_key M_A0(band): median {np.nanmedian(m_v):.4f}; pairs with M_A0(band) > 0.985: "
      f"{int((m_v > 0.985).sum())}; <= 0.985: {int((m_v <= 0.985).sum())}")
print(f"victim_key M_A0(band) - M_A0(0): median {np.nanmedian(m_v - m_v0):+.4f} "
      f"sd {np.nanstd(m_v - m_v0, ddof=1):.4f}")
print(f"random s1 M(band) median {np.median(m_1[ok]):.4f}; s2 {np.median(m_2[ok]):.4f}")
print(f"Delta per pair: median {np.median(delta):+.4f} sd {delta.std(ddof=1):.4f} "
      f"MAD {np.median(np.abs(delta - np.median(delta))):.4f}; exactly 0: {(delta == 0).sum()}; "
      f"|Delta| >= 0.05: {(np.abs(delta) >= 0.05).sum()}")
brng = np.random.default_rng(20260928)
nn = len(delta)
meds = np.array([np.median(delta[brng.integers(0, nn, nn)]) for _ in range(10_000)])
U = float(np.percentile(np.abs(meds), 97.5))
print(f"U = 97.5th pct of |bootstrap median of Delta| = {U:.4f};  N_noise proxy = max(0.015, U) = "
      f"{max(0.015, U):.4f};  DRP-G6 (> 0.025) would fire on this proxy: {max(0.015, U) > 0.025}")
# how the same statistic splits by the DRP famous strata, where the pair falls in one
for lab, lo, hi in (("both >= 0.99 (T1-like)", 0.99, 1.01), ("both in [0.95, 0.99) (T2-like)", 0.95, 0.99)):
    sel = [j for j, (s, t, *_r) in enumerate(rows)
           if lo <= pctl[s] < hi and lo <= pctl[t] < hi and ok[j]]
    print(f"  pairs {lab}: {len(sel)}")
print(f"wall {time.time() - t0:.0f}s")
