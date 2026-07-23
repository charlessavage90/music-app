"""Does bypassing ever reach obscure artists? capfix vs rankfix, shipped mechanism.

One knob: the graph (p99_log_clip vs percentile_rank). Same crawl, same cap
strategy, same damping, same router, same pairs, same policy.

Two victim policies, because they answer different questions:
  hubpen  - bypass the highest hub_penalty interior artist (what the 3.8 test did;
            hub_penalty is degree-based, and 2.6 says degree != famous)
  pop     - bypass the most POPULAR interior artist (what the owner's complaint is
            actually about: "everything is well-known")

Caveat recorded rather than hidden: popularity and hub_penalty are both derived
per-graph, so victim selection is not identical across arms. That is a consequence
of the knob under test, not an independent knob.
"""
import sys, hashlib, json
from pathlib import Path
import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path, Exclusion, KNOWN
from artistpath_api.config import ApiConfig

ARMS = {
    "capfix ": ("graph-t15-capfix.bin",
                "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237"),
    "rankfix": ("graph-t15-rankfix.bin",
                "87d9bf7edfc51fb13ee0fdf6a4216d01df7d3aa7f38b66ea9b7b8c2e7addae05"),
}
PAIRS = [("Miles Davis", "Daft Punk"),
         ("The Shins", "Wishbone Ash"),
         ("Metallica", "Taylor Swift")]
SNAPS = [0, 5, 10, 15, 20]
cfg = ApiConfig()


def load(fn, expect):
    p = ROOT / "builder" / "scratch" / fn
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    assert h == expect, f"{fn} checksum mismatch: {h}"
    return GraphStore.load(p)


def nid(store, n):
    i = store.id_by_mbid.get(n)
    if i is not None:
        return i
    hits = [j for j, nm in enumerate(store.names) if nm.strip().lower() == n.lower()]
    return max(hits, key=lambda j: store.popularity[j]) if hits else None


def walk(store, pct, hp, s, t, policy, steps=20):
    excludes, snaps = [], {}
    for step in range(0, steps + 1):
        p = find_path(store, s, t, excludes, cfg)
        if p is None:
            break
        if step in SNAPS:
            snaps[step] = list(p)
        interior = p[1:-1]
        if not interior:
            break
        key = (lambda i: float(hp[i])) if policy == "hubpen" else (lambda i: float(store.popularity[i]))
        excludes.append(Exclusion(max(interior, key=key), KNOWN))
    return snaps


results = {}
for label, (fn, expect) in ARMS.items():
    store = load(fn, expect)
    pop = store.popularity
    order = np.argsort(pop)
    pct = np.empty(len(pop)); pct[order] = np.arange(len(pop)) / (len(pop) - 1)
    hp = store.hub_penalty
    print(f"\n{'='*78}\n{label.strip()}  N={store.artist_count}  E={len(store.neighbours)}"
          f"  median pop={np.median(pop):.3f}", flush=True)
    for policy in ("hubpen", "pop"):
        print(f"\n  --- victim policy: {policy} ---", flush=True)
        for a, b in PAIRS:
            s, t = nid(store, a), nid(store, b)
            if s is None or t is None:
                print(f"    {a} -> {b}: MISSING", flush=True)
                continue
            snaps = walk(store, pct, hp, s, t, policy)
            row = []
            for d in SNAPS:
                p = snaps.get(d)
                if not p or len(p) <= 2:
                    row.append(f"d{d}:  --  ")
                    continue
                v = pct[np.array(p[1:-1])]
                results[(label, policy, a, d)] = (float(v.mean()), float(v.min()), len(p))
                row.append(f"d{d}: {v.mean():.3f}/{v.min():.3f}(n{len(p)})")
            print(f"    {a[:13]:13s}->{b[:13]:13s} " + "  ".join(row), flush=True)
            if 20 in snaps and len(snaps[20]) > 2:
                print(f"        d20: {' -> '.join(store.names[i] for i in snaps[20])}", flush=True)

print(f"\n{'='*78}\nSUMMARY — mean / MIN interior popularity percentile, pooled over the 3 pairs")
print(f"{'graph':9s} {'policy':7s} " + " ".join(f"{'d'+str(d):>15s}" for d in SNAPS), flush=True)
for label in ARMS:
    for policy in ("hubpen", "pop"):
        cells = []
        for d in SNAPS:
            xs = [results[k] for k in results if k[0] == label and k[1] == policy and k[3] == d]
            cells.append(f"{np.mean([x[0] for x in xs]):.3f}/{min(x[1] for x in xs):.3f}"
                         if xs else "     --      ")
        print(f"{label:9s} {policy:7s} " + " ".join(f"{c:>15s}" for c in cells), flush=True)
print("\n(cell = mean interior percentile / lowest single interior artist reached)")
