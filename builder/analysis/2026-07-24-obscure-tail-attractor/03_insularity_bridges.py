"""Community insularity landscape + the chillhop community/blob bridging role.

Two questions:
  (a) Is comm40 (chillhop) a distinctively dense/insular community, or one of many?
  (b) Can it act as a CROSS-GENRE bridge at all? Measure external edges, the
      similarity on those bridges, and which communities it connects to. A blob
      that is ~all-internal edges cannot be an attractor for other genres' paths;
      one with many high-sim external edges could be.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

API_SRC = Path(__file__).resolve().parents[3] / "api" / "src"
sys.path.insert(0, str(API_SRC))
from artistpath_api.graph_store import GraphStore  # noqa: E402

GRAPH = Path(__file__).resolve().parents[3] / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
OUT = Path(__file__).resolve().parent

store = GraphStore.load(GRAPH)
N = store.artist_count
pop = store.pop_raw.astype(np.float64)
offsets = store.offsets.astype(np.int64)
degrees = np.diff(offsets)
dhp = np.asarray(store.degree_hub_penalty, dtype=np.float64)
membership = np.load(OUT / "membership.npy")
blob = np.load(OUT / "blob_global_ids.npy")
blob_set = set(blob.tolist())

# undirected edges + community endpoints
src = np.repeat(np.arange(N), degrees)
dst = store.neighbours.astype(np.int64)
sc = store.scores.astype(np.float64)
m = src < dst
u, v, w = src[m], dst[m], sc[m]
cu, cv = membership[u], membership[v]

# (a) landscape: per community size, pop, dhp, internal edge fraction
print("Community landscape (all with size>=300), sorted by dhp_mean desc:")
print(f"{'comm':>5} {'size':>6} {'pop_mn':>7} {'dhp_mn':>7} {'intern%':>8}  label-hint(top pop)")
comms = np.unique(membership)
rows = []
for ci in comms:
    members = np.where(membership == ci)[0]
    if len(members) < 300:
        continue
    internal = int(((cu == ci) & (cv == ci)).sum())
    total_deg = int(degrees[members].sum())
    frac_int = 2.0 * internal / total_deg if total_deg else 0.0
    top = sorted(members, key=lambda i: -pop[i])[:3]
    hint = "/".join(store.names[i] for i in top)
    rows.append((float(dhp[members].mean()), int(ci), len(members),
                 float(pop[members].mean()), frac_int, hint))
for dhp_mn, ci, sz, pop_mn, frac_int, hint in sorted(rows, reverse=True):
    print(f"{ci:>5} {sz:>6} {pop_mn:>7.3f} {dhp_mn:>7.3f} {frac_int*100:>7.1f}%  {hint}")

# (b) comm40 + blob bridging
def bridge_report(label, node_set):
    ns = set(int(x) for x in node_set)
    members = np.array(sorted(ns))
    internal = (np.isin(u, members) & np.isin(v, members))
    ext_a = (np.isin(u, members) & ~np.isin(v, members))
    ext_b = (~np.isin(u, members) & np.isin(v, members))
    ext = ext_a | ext_b
    n_int = int(internal.sum())
    n_ext = int(ext.sum())
    total_slots = int(degrees[members].sum())
    print(f"\n=== {label}: size {len(members)} ===")
    print(f"  internal undirected edges = {n_int}")
    print(f"  external (bridge) edges    = {n_ext}")
    print(f"  frac of edge-slots internal = {2*n_int/total_slots:.3f}")
    if n_ext:
        ext_sims = w[ext]
        int_sims = w[internal]
        print(f"  bridge sim: mean={ext_sims.mean():.3f} median={np.median(ext_sims):.3f} "
              f"max={ext_sims.max():.3f} p90={np.percentile(ext_sims,90):.3f}")
        print(f"  internal sim: mean={int_sims.mean():.3f} median={np.median(int_sims):.3f}")
        # which communities do bridges land in?
        other = np.where(ext_a, cv, np.nan)
        other = np.where(ext_b, cu, other)
        other = other[~np.isnan(other)].astype(int)
        oc, ocnt = np.unique(other, return_counts=True)
        top_targets = sorted(zip(oc.tolist(), ocnt.tolist()), key=lambda x: -x[1])[:8]
        print("  top bridge-target communities (comm:count):", top_targets)
        # distinct external communities reached
        print(f"  distinct external communities reached = {len(oc)}")

comm40 = np.where(membership == 40)[0]
bridge_report("comm40 (chillhop)", comm40)
bridge_report("blob (130 chillhop core)", blob)
