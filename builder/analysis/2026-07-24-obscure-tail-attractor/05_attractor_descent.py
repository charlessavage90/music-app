"""Attractor + fame-descent test using the SHIPPED find_path cost function.

(A) Funnel: route all ordered pairs among 12 famous cross-genre seeds under
    ApiConfig defaults. Measure fraction of interior nodes landing in comm40
    (chillhop) / the 130-node blob, vs a degree-weighted null. Enrichment.
(B) Descent: for cross-genre pairs NOT involving chillhop, simulate the app's
    repeated 'known' bypass (exclude all interiors each round -> floor relaxes
    0.15/exclusion, reuse forbidden). Track comm40 funnel per round: does
    descending in fame pull the path INTO chillhop?
(C) Wall test: for every realised edge x->y with y in comm40 and x outside,
    record the similarity on that bridging edge. High-sim entries are coherent
    and NOT suppressible by raising w_sim; low-sim entries are.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

API_SRC = Path(__file__).resolve().parents[3] / "api" / "src"
sys.path.insert(0, str(API_SRC))
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.pathfinding import find_path, Exclusion, KNOWN  # noqa: E402

GRAPH = Path(__file__).resolve().parents[3] / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
OUT = Path(__file__).resolve().parent
store = GraphStore.load(GRAPH)
cfg = ApiConfig()
pop = store.pop_raw.astype(np.float64)
degrees = np.diff(store.offsets.astype(np.int64))
membership = np.load(OUT / "membership.npy")
blob = set(np.load(OUT / "blob_global_ids.npy").tolist())
name_to_id = {}
for i, nm in enumerate(store.names):
    name_to_id.setdefault(nm, i)

SEEDS = {
    "classical": "Erik Satie", "jazz": "Louis Armstrong", "country": "Willie Nelson",
    "metal": "Opeth", "hiphop": "Eminem", "reggae": "Bob Marley & The Wailers",
    "soul": "Marvin Gaye", "trance": "Tiësto", "jpop": "LiSA",
    "idm": "Aphex Twin", "rock": "Metallica", "chillhop": "saib.",
}
sid = {g: name_to_id[n] for g, n in SEEDS.items()}
COMM40 = 40

def sim_between(x, y):
    for k in range(int(store.offsets[x]), int(store.offsets[x + 1])):
        if int(store.neighbours[k]) == y:
            return float(store.scores[k])
    return None

# null: comm40 share of all directed edge-slots (degree-weighted traversal null)
slots_total = int(degrees.sum())
slots_c40 = int(degrees[membership == COMM40].sum())
null_c40 = slots_c40 / slots_total
null_c40_nodes = int((membership == COMM40).sum()) / store.artist_count
print(f"NULL comm40 edge-slot share = {null_c40*100:.3f}%  "
      f"(node-count share {null_c40_nodes*100:.3f}%)")

# ---------- (A) funnel over all cross-genre pairs ----------
genres = list(SEEDS)
tot_interior = 0
c40_interior = 0
blob_interior = 0
wall_sims = []          # sims on edges entering comm40 from outside
per_pair = []
print("\n(A) Baseline funnel (shipped defaults), interiors landing in comm40:")
for i, ga in enumerate(genres):
    for gb in genres:
        if ga == gb:
            continue
        if ga == "chillhop" or gb == "chillhop":
            continue  # endpoint in comm40 trivially; handle separately
        path = find_path(store, sid[ga], sid[gb], [], cfg)
        if not path or len(path) < 3:
            continue
        interior = path[1:-1]
        cm = membership[interior]
        n_c40 = int((cm == COMM40).sum())
        tot_interior += len(interior)
        c40_interior += n_c40
        blob_interior += sum(1 for n in interior if n in blob)
        per_pair.append((ga, gb, len(interior), n_c40))
        # wall: entries into comm40
        for a, b in zip(path[:-1], path[1:]):
            if membership[b] == COMM40 and membership[a] != COMM40:
                wall_sims.append(sim_between(a, b))

print(f"  cross-genre pairs (no chillhop endpoint): {len(per_pair)}")
print(f"  total interior nodes = {tot_interior}")
print(f"  interiors in comm40  = {c40_interior}  ({100*c40_interior/tot_interior:.3f}%)  "
      f"enrichment vs null = {(c40_interior/tot_interior)/null_c40:.2f}x")
print(f"  interiors in blob    = {blob_interior}  ({100*blob_interior/tot_interior:.4f}%)")
pairs_touching = sum(1 for _,_,_,n in per_pair if n>0)
print(f"  pairs whose path touches comm40 at all = {pairs_touching}/{len(per_pair)}")
if wall_sims:
    ws = np.array(wall_sims)
    print(f"  comm40-entry edge sims: n={len(ws)} mean={ws.mean():.3f} "
          f"median={np.median(ws):.3f} min={ws.min():.3f} max={ws.max():.3f}")
else:
    print("  no comm40 entries at all in baseline cross-genre paths")

# show the pairs that DO touch comm40, with the actual path
print("\n  pairs touching comm40 (decoded):")
shown = 0
for ga in genres:
    for gb in genres:
        if ga==gb or ga=="chillhop" or gb=="chillhop": continue
        path = find_path(store, sid[ga], sid[gb], [], cfg)
        if not path: continue
        interior = path[1:-1]
        if any(membership[n]==COMM40 for n in interior) and shown < 12:
            names = " -> ".join(f"{store.names[n]}[c{membership[n]}]" for n in path)
            print(f"    {ga}->{gb}: {names}")
            shown += 1

# ---------- (B) fame-descent: does descending funnel into chillhop? ----------
print("\n(B) Fame-descent (repeated 'known' bypass) — comm40 interior fraction per round:")
DESCENT_PAIRS = [("metal","jazz"), ("classical","hiphop"), ("country","trance"),
                 ("reggae","metal"), ("jpop","soul"), ("idm","country"),
                 ("rock","jazz"), ("hiphop","classical")]
R = 6
for ga, gb in DESCENT_PAIRS:
    excl = []
    fr = []
    minpop = []
    for _ in range(R):
        path = find_path(store, sid[ga], sid[gb], excl, cfg)
        if not path or len(path) < 3:
            fr.append(None); break
        interior = path[1:-1]
        n_c40 = sum(1 for n in interior if membership[n]==COMM40)
        fr.append((n_c40, len(interior)))
        minpop.append(min(pop[n] for n in interior))
        excl += [Exclusion(n, KNOWN) for n in interior]
    frac_str = " ".join(f"{c}/{t}" if isinstance(x,tuple) else "X"
                        for x in fr for (c,t) in [x] ) if False else \
               " ".join((f"{x[0]}/{x[1]}" if x else "X") for x in fr)
    mp = " ".join(f"{m:.2f}" for m in minpop)
    print(f"  {ga}->{gb}: comm40/interior per round = [{frac_str}] ; min interior pop = [{mp}]")

# ---------- (C) idm (adjacent) sensitivity control ----------
print("\n(C) idm<->neighbours descent (Aphex Twin is adjacent to chillhop) — control:")
for gb in ["chillhop","country","metal","jpop"]:
    excl=[]; out=[]
    for _ in range(R):
        path = find_path(store, sid["idm"], sid[gb], excl, cfg)
        if not path or len(path)<3: out.append("X"); break
        interior=path[1:-1]
        out.append(f"{sum(1 for n in interior if membership[n]==COMM40)}/{len(interior)}")
        excl += [Exclusion(n,KNOWN) for n in interior]
    print(f"  idm->{gb}: {out}")
