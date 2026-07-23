"""Part 1 probe: Radiohead by MBID; capfix degree collapse vs control degree vs popularity."""
import sys, json, struct, hashlib
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path("C:/Users/charl/OneDrive/Claude Projects/music-app/api/src")))
from artistpath_api.graph_store import GraphStore

SCRATCH = Path("C:/Users/charl/OneDrive/Claude Projects/music-app/builder/scratch")

def load(name):
    p = SCRATCH / name
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    g = GraphStore.load(p)
    print(f"{name}  sha256={h[:16]}  N={g.artist_count}  E={len(g.neighbours)}", flush=True)
    return g

cap = load("graph-t15-capfix.bin")
ctl = load("graph-t15-control.bin")
d025 = load("graph-t15-d025.bin")

cap_deg = np.diff(cap.offsets)
ctl_deg = np.diff(ctl.offsets)
d025_deg = np.diff(d025.offsets)

# ---- Q2: Radiohead by MBID -------------------------------------------------
print("\n=== Q2: Radiohead by MBID ===", flush=True)
rh_ids = [i for i, n in enumerate(ctl.names) if n.strip().lower() == "radiohead"]
for i in rh_ids:
    print(f"control: name={ctl.names[i]!r} mbid={ctl.mbids[i]} deg={ctl_deg[i]} pop={ctl.popularity[i]:.4f}", flush=True)
for i in rh_ids:
    m = ctl.mbids[i]
    print(f"  in capfix mbid set? {m in cap.id_by_mbid}", flush=True)
    print(f"  in d025 mbid set?   {m in d025.id_by_mbid}", flush=True)
    if m in cap.id_by_mbid:
        j = cap.id_by_mbid[m]
        print(f"  capfix deg={cap_deg[j]} pop={cap.popularity[j]:.4f}", flush=True)
# also scan capfix names for radiohead-ish
hits = [i for i, n in enumerate(cap.names) if "radiohead" in n.strip().lower()]
print(f"capfix name-substring 'radiohead' hits: {[(cap.names[i], cap.mbids[i], int(cap_deg[i])) for i in hits]}", flush=True)

# ---- node-set relationships ------------------------------------------------
cap_set, ctl_set = set(cap.mbids), set(ctl.mbids)
print(f"\ncapfix-only mbids: {len(cap_set - ctl_set)}   control-only: {len(ctl_set - cap_set)}", flush=True)

# ---- ceiling tie mass ------------------------------------------------------
print("\n=== ceiling (score == 1.0) share ===", flush=True)
for name, g in (("capfix", cap), ("control", ctl), ("d025", d025)):
    s = g.scores
    print(f"{name}: frac at 1.0 = {(s >= 1.0).mean():.4f}  ({int((s>=1.0).sum())} of {len(s)})", flush=True)

# ---- capfix degree collapse: tracks control degree, popularity, or neither? --
print("\n=== capfix degree vs control degree / popularity (shared nodes) ===", flush=True)
shared = [m for m in cap.mbids if m in ctl.id_by_mbid]
ci = np.array([cap.id_by_mbid[m] for m in shared])
ti = np.array([ctl.id_by_mbid[m] for m in shared])
cd = cap_deg[ci].astype(float)
td = ctl_deg[ti].astype(float)
cp = cap.popularity[ci].astype(float)
tp = ctl.popularity[ti].astype(float)

from scipy.stats import spearmanr
print(f"n shared = {len(shared)}", flush=True)
print(f"spearman(capfix_deg, control_deg)   = {spearmanr(cd, td).statistic:+.4f}", flush=True)
print(f"spearman(capfix_deg, capfix_pop)    = {spearmanr(cd, cp).statistic:+.4f}", flush=True)
print(f"spearman(capfix_deg, control_pop)   = {spearmanr(cd, tp).statistic:+.4f}", flush=True)
print(f"spearman(control_deg, control_pop)  = {spearmanr(td, tp).statistic:+.4f}", flush=True)

# retention ratio by control-degree decile
print("\ncapfix_deg by control_deg decile:", flush=True)
q = np.quantile(td, np.linspace(0, 1, 11))
for a in range(10):
    lo, hi = q[a], q[a+1]
    m = (td >= lo) & (td <= hi if a == 9 else td < hi)
    if m.sum() == 0: continue
    print(f"  decile {a+1}: ctl_deg [{lo:.0f},{hi:.0f}) n={m.sum():6d}  median capfix_deg={np.median(cd[m]):6.1f}  mean retention={np.mean(cd[m]/td[m]):.4f}", flush=True)

print("\ncapfix_deg by control_pop decile:", flush=True)
q = np.quantile(tp, np.linspace(0, 1, 11))
for a in range(10):
    lo, hi = q[a], q[a+1]
    m = (tp >= lo) & (tp <= hi if a == 9 else tp < hi)
    if m.sum() == 0: continue
    print(f"  decile {a+1}: pop [{lo:.3f},{hi:.3f}) n={m.sum():6d}  median capfix_deg={np.median(cd[m]):6.1f}  median ctl_deg={np.median(td[m]):8.0f}", flush=True)

# top-degree-in-control cohort
print("\ntop-200 control-degree nodes -> capfix degree:", flush=True)
order = np.argsort(-td)[:200]
print(f"  median capfix_deg={np.median(cd[order]):.1f}  mean={cd[order].mean():.1f}  frac at cap(50)={np.mean(cd[order]>=50):.3f}", flush=True)
print("bottom cohort (control_deg 40-60):", flush=True)
m = (td >= 40) & (td <= 60)
print(f"  n={m.sum()} median capfix_deg={np.median(cd[m]):.1f} frac at cap={np.mean(cd[m]>=50):.3f}", flush=True)
