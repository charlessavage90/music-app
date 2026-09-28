"""DRP-AM1 critique, probe 1: structural facts on A0 (graph-lba-a6.bin). Routes nothing.

Answers the arithmetic parts of DRP-Q2 (floor), DRP-Q3 (degree headroom), DRP-Q4 (what the
C1 conjunction demands of 40 pairs; spread of A0's famous-pair medians, parsed from the
COMMITTED graph_descriptives.out.txt, not re-run) and DRP-Q5 (trigger arithmetic).

Draws no pair (the DRP seed 20260928 is never used here), builds no arm, constructs no
added edge. Run from api/:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-drp-prereg-critique/drp_structural_probe.py
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A0 = Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin")
A0_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
GD_OUT = ROOT / "builder/analysis/2026-09-27-issue-200-graph-descriptives/graph_descriptives.out.txt"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


got = sha(A0)
side = json.loads(A0.with_name(A0.name + ".json").read_text(encoding="utf-8"))["sha256"]
if not (got == side == A0_SHA):
    print(f"REFUSING: {got} / sidecar {side} / pin {A0_SHA}", file=sys.stderr)
    sys.exit(2)
print(f"sha256 OK {A0.name} {got} (== sidecar == pin)")

from artistpath_api import pathfinding as pf  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402

assert (ROOT / "api/src").resolve() in Path(pf.__file__).resolve().parents
print(f"pathfinding: {Path(pf.__file__).resolve()}")

payload = A0.read_bytes()
store = GraphStore.from_bytes(payload)
hdr = struct.Struct("<4sIIIQ")
_m, _v, n, e, meta_len = hdr.unpack_from(payload)
cur = hdr.size + (n + 1) * 4 + e * 4 + e * 4
etypes = np.frombuffer(payload[cur: cur + e], dtype="<u1")
meta = json.loads(payload[cur + e: cur + e + meta_len])
fame = meta["fame_lb"]
measured = np.array([v is not None for v in fame])
pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
pop = store.pop_raw  # float32 as the router holds it
deg = np.diff(store.offsets).astype(np.int64)
cfg = ApiConfig()

print("\n## A0 identity-level facts (measured)")
print(f"N {n:,}  CSR entries {e:,}  undirected edges {e // 2:,}  metadata keys {sorted(meta)}")
print(f"edge_types unique values: {sorted(set(etypes.tolist()))}")
print(f"degree: min {deg.min()} max {deg.max()} median {np.median(deg):.0f}; nodes at 50: {(deg == 50).sum():,}")
# CSR symmetry (score equality both directions)
src = np.repeat(np.arange(n), deg)
key_f = src.astype(np.int64) * n + store.neighbours
key_r = store.neighbours.astype(np.int64) * n + src
of, orr = np.argsort(key_f), np.argsort(key_r)
print(f"CSR symmetric (u->v iff v->u): {bool(np.array_equal(key_f[of], key_r[orr]))}; "
      f"scores equal both directions: {bool(np.array_equal(store.scores[of], store.scores[orr]))}")
print(f"rows sorted by neighbour id: "
      f"{all(np.all(np.diff(store.neighbours[store.offsets[i]:store.offsets[i+1]]) > 0) for i in range(n))}")

print("\n## DRP-Q2: pop_raw range and the floor (measured)")
print(f"pop_raw dtype {pop.dtype}; min {float(pop.min())!r}; max {float(pop.max())!r}; "
      f"count == 1.0: {(pop == 1.0).sum()}; count == 0.0: {(pop == 0.0).sum()}")
print(f"cfg.floor_relax_known {cfg.floor_relax_known!r}; 0.15*6 = {cfg.floor_relax_known * 6!r}; "
      f"0.15*7 = {cfg.floor_relax_known * 7!r}")
for k in range(0, 9):
    ex = [pf.Exclusion(node=0, reason=pf.KNOWN)] * k
    print(f"  k={k}: effective_floor_raw(base=max pop_raw) = "
          f"{pf.effective_floor_raw(float(pop.max()), ex, cfg)!r}")

T1 = np.flatnonzero(measured & (pctl >= 0.99))
T2 = np.flatnonzero(measured & (pctl >= 0.95) & (pctl < 0.99))
MID = np.flatnonzero(measured & (pctl >= 0.30) & (pctl <= 0.70))
print(f"pools: T1 {len(T1):,}  T2 {len(T2):,}  MID {len(MID):,}")
print("| pool | pop_raw p10 | p50 | p90 | max | min |")
print("|---|---|---|---|---|---|")
for lab, ids in (("T1", T1), ("T2", T2), ("MID", MID)):
    p = pop[ids].astype(np.float64)
    print(f"| {lab} | {np.percentile(p,10):.3f} | {np.median(p):.3f} | {np.percentile(p,90):.3f} "
          f"| {p.max():.3f} | {p.min():.3f} |")
print("\nShare of ALL unordered within-pool pairs whose floor is still NON-ZERO at press k "
      "(floor_raw = max(0, min(pop_s, pop_t) - 0.15k) > 0):")
print("| pool | k=0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |")
print("|---|---|---|---|---|---|---|---|---|")
for lab, ids in (("T1", T1), ("T2", T2), ("MID", MID)):
    p = np.sort(pop[ids].astype(np.float64))
    m = len(p)
    row = []
    for k in range(8):
        thr = cfg.floor_relax_known * k
        # pairs with min > thr  <=> both > thr
        a = int((p > thr).sum())
        row.append(a * (a - 1) / (m * (m - 1)))
    print(f"| {lab} | " + " | ".join(f"{x:.3f}" for x in row) + " |")

print("\n## DRP-Q3 support: degree headroom (measured)")
for lab, ids in (("T1 centres", T1),):
    d = deg[ids]
    print(f"{lab}: shipped degree min {d.min()} median {np.median(d):.0f} max {d.max()}; "
          f"headroom to 60 min {60 - d.max()}")
below90 = np.flatnonzero(measured & (pctl < 0.90))
d = deg[below90]
print(f"possible partners (measured pctl < 0.90, {len(below90):,} nodes): shipped degree "
      f"p10 {np.percentile(d,10):.0f} median {np.median(d):.0f} p90 {np.percentile(d,90):.0f}; "
      f"share with shipped degree <= 49 (headroom > 10 under the 60 bound): {(d <= 49).mean():.4f}")
print("pop_raw by fame band (for the jump/floor price on a famous->partner hop):")
print("| fame band | n | pop_raw median | p10 | p90 |")
print("|---|---|---|---|---|")
for lo, hi in ((0.99, 1.01), (0.95, 0.99), (0.85, 0.90), (0.70, 0.85), (0.50, 0.70), (0.0, 0.50)):
    ids = np.flatnonzero(measured & (pctl >= lo) & (pctl < hi))
    p = pop[ids].astype(np.float64)
    print(f"| [{lo}, {hi}) | {len(ids):,} | {np.median(p):.3f} | {np.percentile(p,10):.3f} | "
          f"{np.percentile(p,90):.3f} |")

print("\n## DRP-Q4: the committed A0 per-pair output (parsed, not re-run)")
rows = {"FAMOUS": [], "MID": []}
section = None
for line in GD_OUT.read_text(encoding="utf-8").splitlines():
    if line.startswith("### FAMOUS: per pair"):
        section = "FAMOUS"
    elif line.startswith("### MID: per pair"):
        section = "MID"
    elif line.startswith("### Summary"):
        section = None
    elif section and re.match(r"^\| \d+ \|", line):
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows[section].append([float(cells[i]) for i in (3, 4, 5, 6)])
for s, r in rows.items():
    a = np.array(r)
    assert a.shape == (40, 4), a.shape
    d10, d0 = a[:, 2], a[:, 0]
    diff = d10 - d0
    mad = lambda x: float(np.median(np.abs(x - np.median(x))))  # noqa: E731
    print(f"{s}: d10 median {np.median(d10):.3f} sd {d10.std(ddof=1):.4f} MAD {mad(d10):.4f}; "
          f"d10-d0 median {np.median(diff):+.3f} sd {diff.std(ddof=1):.4f} MAD {mad(diff):.4f}; "
          f"pairs with d10 <= d0-0.05: {(diff <= -0.05).sum()}; |d10-d0| < 0.015: {(np.abs(diff) < 0.015).sum()}; "
          f"d10 < 0.94: {(d10 < 0.94).sum()}")

print("\n## DRP-Q4: what DRP-C1(2) demands of 40 pairs (arithmetic, not a measurement)")
print("Model: m of 40 pairs have D << -N_noise (movers), the rest D ~ 0. A resampled median of 40")
print("(mean of order stats 20 and 21) is <= -N_noise iff >= 21 movers are drawn, or exactly 20")
print("when the movers' D <= -2*N_noise. Pass needs P(bootstrap median > -N_noise) <= alpha.")
def binom_cdf(k, nn, p):
    return sum(math.comb(nn, i) * p**i * (1 - p)**(nn - i) for i in range(0, k + 1))
for alpha, lab in ((0.025, "97.5th pct (two-sided 95 %)"), (0.05, "95th pct (one-sided 95 %)")):
    for need, lab2 in ((20, ">= 21 movers"), (19, ">= 20 movers")):
        mmin = next(m for m in range(41) if binom_cdf(need, 40, m / 40) <= alpha)
        print(f"  upper bound = {lab}, resample needs {lab2}: minimum movers m = {mmin} of 40")

print("\n## DRP-Q5: the DRP-SW trigger arithmetic")
for nn in (40, 36, 30):
    ok = [c for c in range(nn + 1) if not (c / nn < 0.90)]
    print(f"  n={nn}: identity share < 0.90 fires at <= {min(ok) - 1} identical, i.e. >= {nn - min(ok) + 1} changed")
print("  Statistic 2 (|median of M_S1P0(0)-M_A0(0)| >= 0.05) requires the median to be non-zero; with")
print("  >= 21 of 40 differences exactly 0 (identical first paths) the median is 0, so statistic 2 can")
print("  only fire when <= 20 of 40 are identical: identity share <= 0.50, which already fires statistic 1.")
