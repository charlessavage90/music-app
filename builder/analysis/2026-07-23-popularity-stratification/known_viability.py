"""Can the `known` bypass do what §3.4 specifies, for the artists users press it on?

§3.4's owner specification: pressing `known` on artist K should route to an artist
HIGHLY SIMILAR to K but MORE OBSCURE. §3.10 records the gates actually used:
pop drop >= 0.10, and for the waypoint form similarity >= 0.70.

That is a per-node existence question. If K has no neighbour that is both similar
and more obscure, the mechanism is unsatisfiable for K regardless of weights.

Also: how far must you travel from a famous artist to reach anything obscure?
"""
import sys, hashlib
from collections import deque
from pathlib import Path
import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore

CAP = ROOT / "builder" / "scratch" / "graph-t15-capfix.bin"
assert hashlib.sha256(CAP.read_bytes()).hexdigest() == \
    "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237"
g = GraphStore.load(CAP)
pop = g.popularity
order = np.argsort(pop); pct = np.empty(len(pop)); pct[order] = np.arange(len(pop)) / (len(pop) - 1)
deg = np.diff(g.offsets)
DELTA, SIM_GATE = 0.10, 0.70
N = g.artist_count

subs_pop = np.zeros(N, int)      # neighbours >= DELTA more obscure
subs_both = np.zeros(N, int)     # ...and similarity >= SIM_GATE
for i in range(N):
    a, b = int(g.offsets[i]), int(g.offsets[i + 1])
    if b == a:
        continue
    drop = float(pop[i]) - pop[g.neighbours[a:b]]
    ok = drop >= DELTA
    subs_pop[i] = int(ok.sum())
    subs_both[i] = int((ok & (g.scores[a:b] >= SIM_GATE)).sum())

print("=== Can `known` find ANY admissible substitute? (pop drop >= 0.10) ===")
print(f"{'popularity band':16s} {'n':>7s} {'% with ZERO':>12s} {'median #subs':>13s} {'% zero w/ sim gate':>19s}")
BANDS = [(0.999, 1.001, "top 0.1%"), (0.99, 0.999, "p99-99.9"), (0.95, 0.99, "p95-99"),
         (0.90, 0.95, "p90-95"), (0.75, 0.90, "p75-90"), (0.50, 0.75, "p50-75"),
         (0.0, 0.50, "below p50")]
for lo, hi, lbl in BANDS:
    m = (pct >= lo) & (pct < hi) & (deg > 0)
    if not m.sum():
        continue
    print(f"{lbl:16s} {m.sum():7d} {np.mean(subs_pop[m] == 0)*100:11.1f}% "
          f"{np.median(subs_pop[m]):13.0f} {np.mean(subs_both[m] == 0)*100:18.1f}%")

print("\n=== The artists a user is most likely to press `known` on ===")
print(f"{'artist':24s} {'deg':>4s} {'pop pct':>8s} {'#subs':>6s} {'#subs+sim':>10s}  best substitute")
for n in ["The Beatles", "Radiohead", "Coldplay", "Metallica", "Nirvana", "Pink Floyd",
          "Taylor Swift", "The Shins", "Madonna", "Bob Dylan", "Aphex Twin", "Miles Davis"]:
    h = [i for i, x in enumerate(g.names) if x.strip().lower() == n.lower()]
    if not h:
        print(f"{n:24s}  ABSENT FROM GRAPH")
        continue
    i = max(h, key=lambda j: pop[j])
    a, b = int(g.offsets[i]), int(g.offsets[i + 1])
    drop = float(pop[i]) - pop[g.neighbours[a:b]]
    ok = np.where(drop >= DELTA)[0]
    best = "-- none --"
    if len(ok):
        j = ok[np.argmax(g.scores[a:b][ok])]
        v = int(g.neighbours[a:b][j])
        best = f"{g.names[v]} (sim {g.scores[a:b][j]:.3f}, pop pct {pct[v]:.3f})"
    print(f"{n:24s} {deg[i]:4d} {pct[i]:8.3f} {subs_pop[i]:6d} {subs_both[i]:10d}  {best}")

print("\n=== How far from a famous artist to anything below p50? (BFS hops) ===")
def hops_to(i, thresh):
    seen = {i}; q = deque([(i, 0)])
    while q:
        u, d = q.popleft()
        if d > 6:
            return None
        if pct[u] < thresh and u != i:
            return d
        for v in g.neighbours[int(g.offsets[u]):int(g.offsets[u + 1])]:
            v = int(v)
            if v not in seen:
                seen.add(v); q.append((v, d + 1))
    return None

print(f"{'artist':24s} {'->p90':>6s} {'->p75':>6s} {'->p50':>6s}")
for n in ["The Beatles", "Coldplay", "Metallica", "The Shins", "Pink Floyd", "Taylor Swift",
          "saib.", "Stonebank", "CROOVE"]:
    h = [i for i, x in enumerate(g.names) if x.strip().lower() == n.lower()]
    if not h:
        continue
    i = max(h, key=lambda j: pop[j])
    print(f"{n:24s} " + " ".join(f"{str(hops_to(i,t)):>6s}" for t in (0.90, 0.75, 0.50)))
