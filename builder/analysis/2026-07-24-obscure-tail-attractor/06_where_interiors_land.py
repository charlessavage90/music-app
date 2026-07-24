"""Where do cross-genre path interiors actually land? Tests whether ANY single
community (not just chillhop) is a dominant cross-genre corridor/attractor.
Compares each community's share of realised interiors to its degree-weighted
null share; reports the top enrichers."""
from __future__ import annotations
import sys
from collections import Counter
from pathlib import Path
import numpy as np

API_SRC = Path(__file__).resolve().parents[3] / "api" / "src"
sys.path.insert(0, str(API_SRC))
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.pathfinding import find_path  # noqa: E402

GRAPH = Path(__file__).resolve().parents[3] / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
OUT = Path(__file__).resolve().parent
store = GraphStore.load(GRAPH)
cfg = ApiConfig()
pop = store.pop_raw.astype(np.float64)
degrees = np.diff(store.offsets.astype(np.int64))
membership = np.load(OUT / "membership.npy")
name_to_id = {}
for i, nm in enumerate(store.names):
    name_to_id.setdefault(nm, i)

SEEDS = {"classical":"Erik Satie","jazz":"Louis Armstrong","country":"Willie Nelson",
    "metal":"Opeth","hiphop":"Eminem","reggae":"Bob Marley & The Wailers",
    "soul":"Marvin Gaye","trance":"Tiësto","jpop":"LiSA","idm":"Aphex Twin",
    "rock":"Metallica","chillhop":"saib."}
sid = {g: name_to_id[n] for g,n in SEEDS.items()}
seed_comms = {membership[i] for i in sid.values()}

interior_comm = Counter()
total = 0
for ga in SEEDS:
    for gb in SEEDS:
        if ga==gb or ga=="chillhop" or gb=="chillhop": continue
        path = find_path(store, sid[ga], sid[gb], [], cfg)
        if not path or len(path)<3: continue
        for n in path[1:-1]:
            interior_comm[int(membership[n])] += 1
            total += 1

slots_total = int(degrees.sum())
print(f"total cross-genre interior nodes = {total}")
print(f"{'comm':>5} {'count':>6} {'share%':>7} {'null%':>7} {'enrich':>7} {'is_seed':>7}  hint")
comm_hint = {}
for ci in interior_comm:
    members = np.where(membership==ci)[0]
    top = sorted(members, key=lambda i:-pop[i])[:2]
    comm_hint[ci] = "/".join(store.names[i] for i in top)
for ci, cnt in sorted(interior_comm.items(), key=lambda x:-x[1]):
    share = cnt/total
    null = int(degrees[membership==ci].sum())/slots_total
    print(f"{ci:>5} {cnt:>6} {share*100:>6.2f}% {null*100:>6.2f}% "
          f"{share/null:>6.2f}x {'Y' if ci in seed_comms else '':>7}  {comm_hint[ci]}")
