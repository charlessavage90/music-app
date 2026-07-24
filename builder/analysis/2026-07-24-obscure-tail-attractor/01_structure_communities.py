"""Structural characterisation + community detection on the adopted 75k graph.

Artifact: builder/scratch/graph-t15-tiebreakfix.bin
sha256 4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8 (verified externally)

Run from api/ with:
  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run --with igraph python \
    ../builder/analysis/2026-07-24-obscure-tail-attractor/01_structure_communities.py

Owns its figures. Prints a report + writes communities.json for downstream scripts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# api/src on path for the shipped reader
API_SRC = Path(__file__).resolve().parents[3] / "api" / "src"
sys.path.insert(0, str(API_SRC))
from artistpath_api.graph_store import GraphStore  # noqa: E402

GRAPH = Path(__file__).resolve().parents[3] / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
OUT = Path(__file__).resolve().parent

store = GraphStore.load(GRAPH)
N = store.artist_count
offsets = store.offsets.astype(np.int64)
neighbours = store.neighbours.astype(np.int64)
scores = store.scores.astype(np.float64)
pop = store.pop_raw.astype(np.float64)
dhp = np.asarray(store.degree_hub_penalty, dtype=np.float64)
degrees = np.diff(offsets)
E_directed = len(neighbours)

print("=" * 70)
print(f"N nodes = {N}")
print(f"CSR entries (directed edge-slots) = {E_directed}")
print(f"degree: min={degrees.min()} max={degrees.max()} mean={degrees.mean():.2f} "
      f"median={np.median(degrees):.1f}")
for q in (50, 90, 95, 99, 99.9):
    print(f"  degree p{q} = {np.percentile(degrees, q):.1f}")
print(f"pop_raw: min={pop.min():.4f} max={pop.max():.4f} mean={pop.mean():.4f} "
      f"median={np.median(pop):.4f}")

# Build undirected edge list (u<v) from symmetric CSR, dedup.
src = np.repeat(np.arange(N), degrees)
dst = neighbours
mask = src < dst
u = src[mask]
v = dst[mask]
w = scores[mask]
E_undirected = len(u)
print(f"undirected edges (u<v) = {E_undirected}")
# sanity: symmetric CSR => directed slots ~= 2*undirected
print(f"  2*undirected = {2*E_undirected} vs directed slots {E_directed} "
      f"(diff {E_directed - 2*E_undirected})")

import igraph as ig  # noqa: E402

g = ig.Graph(n=N, edges=list(zip(u.tolist(), v.tolist())), directed=False)
g.es["weight"] = w.tolist()

print("\nRunning Louvain (multilevel), weighted ...")
part = g.community_multilevel(weights="weight")
sizes = np.array(part.sizes())
order = np.argsort(sizes)[::-1]
print(f"n communities = {len(sizes)}, modularity = {part.modularity:.4f}")
print("top 15 community sizes:", sizes[order][:15].tolist())

membership = np.array(part.membership)

def top_names(node_ids, k=12):
    ids = sorted(node_ids, key=lambda i: -pop[i])[:k]
    return [f"{store.names[i]}(pop{pop[i]:.2f},deg{int(degrees[i])})" for i in ids]

# Characterise the top communities
comm_report = []
for rank, ci in enumerate(order[:12]):
    members = np.where(membership == ci)[0]
    m = len(members)
    mset = set(members.tolist())
    # internal edges: count undirected edges with both endpoints in community
    in_mask = np.isin(u, members) & np.isin(v, members)
    internal = int(in_mask.sum())
    # total edge-endpoints from these nodes (directed slots)
    total_deg = int(degrees[members].sum())
    # internal directed slots = 2*internal ; external = total_deg - 2*internal
    ext = total_deg - 2 * internal
    density = (2.0 * internal) / (m * (m - 1)) if m > 1 else 0.0
    reciprocity_internal_frac = (2.0 * internal) / total_deg if total_deg else 0.0
    rec = {
        "rank": rank,
        "comm_id": int(ci),
        "size": int(m),
        "internal_edges": internal,
        "internal_density": density,
        "frac_edges_internal": reciprocity_internal_frac,
        "mean_degree": float(degrees[members].mean()),
        "median_degree": float(np.median(degrees[members])),
        "pop_raw_mean": float(pop[members].mean()),
        "pop_raw_median": float(np.median(pop[members])),
        "pop_raw_p90": float(np.percentile(pop[members], 90)),
        "dhp_mean": float(dhp[members].mean()),
        "top_pop_names": top_names(members),
    }
    comm_report.append(rec)
    print(f"\n--- community rank {rank} (id {ci}) size {m} ---")
    print(f"  internal_density={density:.4f} frac_edges_internal={reciprocity_internal_frac:.3f} "
          f"mean_deg={degrees[members].mean():.1f}")
    print(f"  pop_raw mean={pop[members].mean():.3f} median={np.median(pop[members]):.3f} "
          f"dhp_mean={dhp[members].mean():.3f}")
    print("  top-pop members:", ", ".join(top_names(members, 10)))

# Save membership + report for downstream
np.save(OUT / "membership.npy", membership)
with open(OUT / "communities.json", "w", encoding="utf-8") as f:
    json.dump({
        "N": int(N), "E_undirected": int(E_undirected),
        "modularity": float(part.modularity),
        "n_communities": int(len(sizes)),
        "sizes_top20": sizes[order][:20].tolist(),
        "communities": comm_report,
    }, f, indent=2, ensure_ascii=False)
print("\nwrote communities.json + membership.npy")
