"""Locate the lo-fi/chillhop seed blob and characterise its community.

Answers: which Louvain community do the known lo-fi 'unknowns' fall in? Is it a
distinct low-fame community, or a low-fame sub-region of a broader genre
community that also holds famous artists?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

API_SRC = Path(__file__).resolve().parents[3] / "api" / "src"
sys.path.insert(0, str(API_SRC))
from artistpath_api.graph_store import GraphStore  # noqa: E402

GRAPH = Path(__file__).resolve().parents[3] / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
OUT = Path(__file__).resolve().parent

store = GraphStore.load(GRAPH)
pop = store.pop_raw.astype(np.float64)
offsets = store.offsets.astype(np.int64)
degrees = np.diff(offsets)
dhp = np.asarray(store.degree_hub_penalty, dtype=np.float64)
membership = np.load(OUT / "membership.npy")

name_to_id: dict[str, int] = {}
for i, nm in enumerate(store.names):
    name_to_id.setdefault(nm, i)

SEEDS = ["saib.", "Purrple Cat", "sleepy fish", "Leavv", "idealism",
         "Miami Nights 1984", "Lazerhawk", "Stonebank", "Toonorth", "CROOVE"]

print("Lo-fi/synthwave seed locations:")
seed_ids = []
for nm in SEEDS:
    i = name_to_id.get(nm)
    if i is None:
        print(f"  {nm}: NOT FOUND")
        continue
    seed_ids.append(i)
    pctl = float((pop < pop[i]).mean() * 100)
    print(f"  {nm}: id={i} comm={membership[i]} pop_raw={pop[i]:.3f} "
          f"(pctl {pctl:.1f}) deg={int(degrees[i])} dhp={dhp[i]:.3f}")

comms, counts = np.unique(membership[seed_ids], return_counts=True)
print("\nSeed community distribution:", dict(zip(comms.tolist(), counts.tolist())))

# Characterise each community the seeds fall in
for ci in comms:
    members = np.where(membership == ci)[0]
    m = len(members)
    # pop distribution of the community
    print(f"\n=== community {ci}: size {m} ===")
    print(f"  pop_raw: mean={pop[members].mean():.3f} median={np.median(pop[members]):.3f} "
          f"p10={np.percentile(pop[members],10):.3f} p90={np.percentile(pop[members],90):.3f}")
    print(f"  degree mean={degrees[members].mean():.1f}  dhp mean={dhp[members].mean():.3f}")
    # most famous members (are there mainstream anchors here?)
    top = sorted(members, key=lambda i: -pop[i])[:15]
    print("  MOST famous members:", ", ".join(
        f"{store.names[i]}({pop[i]:.2f})" for i in top))
    # least famous members
    bot = sorted(members, key=lambda i: pop[i])[:8]
    print("  LEAST famous members:", ", ".join(
        f"{store.names[i]}({pop[i]:.2f})" for i in bot))

# Now: the tight blob. Sub-Louvain within the dominant seed community.
main_ci = comms[np.argmax(counts)]
sub_members = np.where(membership == main_ci)[0]
sub_set = set(sub_members.tolist())
print(f"\n\nSub-clustering community {main_ci} (size {len(sub_members)}) ...")

import igraph as ig  # noqa: E402
src = np.repeat(np.arange(store.artist_count), degrees)
dst = store.neighbours.astype(np.int64)
sc = store.scores.astype(np.float64)
mask = (src < dst) & np.isin(src, sub_members) & np.isin(dst, sub_members)
su, sv, sw = src[mask], dst[mask], sc[mask]
# relabel to compact ids
remap = {g: k for k, g in enumerate(sub_members.tolist())}
inv = sub_members.tolist()
edges = [(remap[a], remap[b]) for a, b in zip(su.tolist(), sv.tolist())]
sg = ig.Graph(n=len(sub_members), edges=edges, directed=False)
sg.es["weight"] = sw.tolist()
sub_part = sg.community_multilevel(weights="weight")
ssizes = np.array(sub_part.sizes())
sorder = np.argsort(ssizes)[::-1]
smem = np.array(sub_part.membership)
print(f"  sub-communities: {len(ssizes)}, sizes top10 {ssizes[sorder][:10].tolist()}, "
      f"modularity {sub_part.modularity:.3f}")

# which sub-community holds the seeds?
seed_local = [remap[i] for i in seed_ids if i in remap]
seed_subc = smem[seed_local]
sc_ids, sc_cnt = np.unique(seed_subc, return_counts=True)
print("  seed sub-community distribution:", dict(zip(sc_ids.tolist(), sc_cnt.tolist())))
blob_subc = sc_ids[np.argmax(sc_cnt)]
blob_local = np.where(smem == blob_subc)[0]
blob_global = [inv[k] for k in blob_local.tolist()]
bg = np.array(blob_global)
print(f"\n  BLOB = sub-community {blob_subc}: size {len(bg)}")
print(f"  pop_raw mean={pop[bg].mean():.3f} median={np.median(pop[bg]):.3f} "
      f"p90={np.percentile(pop[bg],90):.3f} max={pop[bg].max():.3f}")
print(f"  degree mean={degrees[bg].mean():.1f} dhp mean={dhp[bg].mean():.3f}")
top = sorted(bg.tolist(), key=lambda i: -pop[i])[:20]
print("  top-pop blob members:", ", ".join(f"{store.names[i]}({pop[i]:.2f})" for i in top))

np.save(OUT / "blob_global_ids.npy", bg)
with open(OUT / "blob.json", "w", encoding="utf-8") as f:
    json.dump({
        "main_community": int(main_ci),
        "main_community_size": int(len(sub_members)),
        "blob_subcommunity": int(blob_subc),
        "blob_size": int(len(bg)),
        "blob_pop_mean": float(pop[bg].mean()),
        "blob_ids": bg.tolist(),
        "seed_ids": seed_ids,
    }, f, indent=2, ensure_ascii=False)
print("\nwrote blob_global_ids.npy + blob.json")
