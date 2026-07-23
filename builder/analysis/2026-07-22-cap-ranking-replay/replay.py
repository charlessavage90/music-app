"""M — dual-cap replay. Reproduces build_from_archive up to pipeline.py:218,
then branches on ONE knob: whether the top-k ranking sees clipped or unclipped
scores. Everything else identical (same archive, damping 0.0, same p99, same
k, same tie-break, same symmetrise, same LCC).

Read-only: imports the shipped pure functions, modifies nothing.
"""
import sys, time, array, json, hashlib
from pathlib import Path
import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "builder" / "src"))
sys.path.insert(0, str(ROOT / "api" / "src"))

from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.listenbrainz import ListenBrainzSource, harvest_identities
from artistpath_builder.pipeline import is_special_purpose
from artistpath_builder.graph import symmetrise, largest_component
from artistpath_api.graph_store import GraphStore

t0 = time.time()
def log(*a):
    print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)

cfg = BuilderConfig()
assert cfg.similarity_damping == 0.0 and cfg.max_neighbours_per_artist == 50
K = cfg.max_neighbours_per_artist
src = ListenBrainzSource(cfg)

ARCH = ROOT / "builder" / "scratch" / "graph-archive" / "similar" / "listenbrainz"
files = sorted(p.name for p in ARCH.iterdir() if p.name.endswith(".json"))
log(f"archive files: {len(files)}")

payloads = {}
for i, fn in enumerate(files):
    payloads[fn[:-5]] = (ARCH / fn).read_bytes()
    if (i + 1) % 20000 == 0:
        log(f"  read {i+1}")
log("payloads read")

identities = harvest_identities(payloads.values())
log(f"identities: {len(identities)}")

known = set(payloads)
excluded = {m for m, (_n, dis) in identities.items() if is_special_purpose(dis)}
known -= excluded
log(f"known after special-purpose filter: {len(known)}  (excluded {len(excluded)})")

mbids = sorted(known)
N = len(mbids)
idx = {m: i for i, m in enumerate(mbids)}   # integer order == lexicographic MBID order

# --- pass 1/2, replicating pipeline.py:156-192 with damping = 0.0 ------------
# damped_strength(cooc, _, _, 0.0) == log1p(max(0, cooc)); mass unused at d=0.
esrc = array.array("i"); edst = array.array("i"); estr = array.array("d")
offsets = array.array("i", [0])
import math
for i, m in enumerate(mbids):
    neigh = [n for n in src.parse(payloads[m], exclude_mbid=m) if n.mbid not in excluded]
    scored = [(n.mbid, math.log1p(max(0.0, n.score))) for n in neigh if n.mbid in known]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))          # pipeline.py:187
    d = {}                                                      # pipeline.py:210-213 (dict; last wins)
    for dst, v in scored:
        d[dst] = v
    for dst, v in d.items():
        esrc.append(i); edst.append(idx[dst]); estr.append(v)
    offsets.append(len(edst))
    if (i + 1) % 20000 == 0:
        log(f"  scored {i+1}")
del payloads
esrc = np.frombuffer(esrc, dtype=np.int32); edst = np.frombuffer(edst, dtype=np.int32)
estr = np.frombuffer(estr, dtype=np.float64); offsets = np.frombuffer(offsets, dtype=np.int32)
E = len(edst)
log(f"pre-cap directed edges: {E}")

# --- rescale, replicating pipeline.py:85-101 --------------------------------
raw = np.expm1(np.maximum(0.0, estr))
scale = float(np.percentile(raw, 99))
log_scale = math.log1p(scale)
clip = np.minimum(1.0, np.log1p(np.maximum(0.0, raw)) / log_scale)
log(f"p99 raw={scale:.6f}  log_scale={log_scale:.6f}  frac at ceiling={(clip>=1.0).mean():.4f}")

# --- top-k under each ranking input -----------------------------------------
def top_k_sets(rank_values):
    out = []
    for i in range(N):
        a, b = int(offsets[i]), int(offsets[i + 1])
        if b - a <= K:
            out.append(set(edst[a:b].tolist()))
        else:
            o = np.lexsort((edst[a:b], -rank_values[a:b]))[:K]   # (-value, dst_id)
            out.append(set(edst[a:b][o].tolist()))
    return out

def run_arm(label, rank_values):
    tk = top_k_sets(rank_values)
    log(f"{label}: top-k computed")
    adj = {i: {} for i in range(N)}
    for e in range(E):
        u = int(esrc[e]); v = int(edst[e])
        if v in tk[u] and u in tk[v]:
            adj[u][v] = float(clip[e])          # clipped scores emitted in BOTH arms
    del tk
    kept = sum(len(x) for x in adj.values())
    adj = symmetrise(adj)
    keep = largest_component(adj)
    deg = {n: len({d for d in adj[n] if d in keep}) for n in keep}
    Efinal = sum(deg.values())
    log(f"{label}: mutual edges={kept}  LCC N={len(keep)}  E={Efinal}")
    return keep, deg, adj

# --- correctness check: Arm 1 must reproduce capfix --------------------------
cap = GraphStore.load(ROOT / "builder" / "scratch" / "graph-t15-capfix.bin")
log(f"capfix reference: N={cap.artist_count} E={len(cap.neighbours)}")

keep1, deg1, adj1 = run_arm("ARM1(clipped)", clip)
ok = (len(keep1) == cap.artist_count) and (sum(deg1.values()) == len(cap.neighbours))
log(f"ARM1 reproduces capfix N and E: {ok}")
mb_keep1 = {mbids[i] for i in keep1}
log(f"ARM1 mbid set == capfix mbid set: {mb_keep1 == set(cap.mbids)}")

keep2, deg2, adj2 = run_arm("ARM2(unclipped)", estr)

# --- Radiohead terminal state ------------------------------------------------
RH = "a74b1b7f-71a5-4011-9441-d0b5e4122711"
print("\n=== Radiohead terminal state ===", flush=True)
if RH in idx:
    ri = idx[RH]
    a, b = int(offsets[ri]), int(offsets[ri + 1])
    print(f"in known set: yes; out-list len (known, deduped) = {b-a}", flush=True)
    print(f"  ARM1: mutual-edge count pre-LCC = {len(adj1.get(ri, {}))}  in LCC = {ri in keep1}", flush=True)
    print(f"  ARM2: mutual-edge count pre-LCC = {len(adj2.get(ri, {}))}  in LCC = {ri in keep2}"
          + (f"  degree={deg2[ri]}" if ri in keep2 else ""), flush=True)
    if ri not in keep1:
        # island size in ARM1
        seen = {ri}; stack = [ri]
        while stack:
            n = stack.pop()
            for w in adj1.get(n, {}):
                if w not in seen:
                    seen.add(w); stack.append(w)
        print(f"  ARM1 component containing Radiohead: size {len(seen)} "
              f"({'ISOLATED SINGLETON' if len(seen)==1 else 'small island'})", flush=True)
        if 1 < len(seen) <= 20:
            print("    members:", [f"{identities.get(mbids[x],('?',''))[0]}" for x in sorted(seen)], flush=True)
else:
    print("Radiohead not in known set", flush=True)

# --- per-artist table for the top-25 by capfix popularity --------------------
# Fixed cohort across arms: ranked by capfix popularity, mapped by MBID.
order = np.argsort(-cap.popularity)[:25]
cohort = [cap.mbids[i] for i in order]
cohort_names = [cap.names[i] for i in order]
cohort_pop = [float(cap.popularity[i]) for i in order]
capdeg = np.diff(cap.offsets)
cohort_capdeg = [int(capdeg[i]) for i in order]
# add Radiohead explicitly (absent from capfix, so not in the popularity order)
cohort = [RH] + cohort; cohort_names = ["Radiohead"] + cohort_names
cohort_pop = [float("nan")] + cohort_pop; cohort_capdeg = [0] + cohort_capdeg

# reciprocity lookup: is (v,u) an archived edge?
key = esrc.astype(np.int64) * N + edst.astype(np.int64)
key_sorted = np.sort(key)
def has_edge(u, v):
    p = np.searchsorted(key_sorted, np.int64(u) * N + v)
    return p < len(key_sorted) and key_sorted[p] == np.int64(u) * N + v

print("\n=== top-25 by capfix popularity (+ Radiohead) ===", flush=True)
hdr = f"{'artist':30s} {'pop':>5s} {'capfixD':>7s} {'arm1D':>6s} {'arm2D':>6s} {'|out|':>5s} {'ceilFrac':>8s} {'recipFrac':>9s} {'recip&ceil':>10s}"
print(hdr, flush=True)
rows = []
for m, nm, pp, cd in zip(cohort, cohort_names, cohort_pop, cohort_capdeg):
    if m not in idx:
        print(f"{nm[:30]:30s} {'-':>5s} {'-':>7s} {'-':>6s} {'-':>6s} {'not in known set':>5s}", flush=True)
        continue
    i = idx[m]
    a, b = int(offsets[i]), int(offsets[i + 1])
    L = b - a
    dsts = edst[a:b]
    ceilfrac = float((clip[a:b] >= 1.0).mean()) if L else float("nan")
    rec = np.fromiter((has_edge(int(v), i) for v in dsts), dtype=bool, count=L) if L else np.zeros(0, bool)
    recfrac = float(rec.mean()) if L else float("nan")
    both = float((rec & (clip[a:b] >= 1.0)).sum())
    d1 = deg1.get(i, 0) if i in keep1 else 0
    d2 = deg2.get(i, 0) if i in keep2 else 0
    print(f"{nm[:30]:30s} {pp:5.2f} {cd:7d} {d1:6d} {d2:6d} {L:5d} {ceilfrac:8.3f} {recfrac:9.3f} {both:10.0f}", flush=True)
    rows.append((nm, cd, d1, d2, L, ceilfrac, recfrac))

# --- aggregate arm comparison ------------------------------------------------
print("\n=== aggregate ===", flush=True)
d1a = np.array([deg1.get(i, 0) for i in range(N)])
d2a = np.array([deg2.get(i, 0) for i in range(N)])
in1 = np.array([i in keep1 for i in range(N)])
in2 = np.array([i in keep2 for i in range(N)])
print(f"ARM1 LCC N={in1.sum()}  median deg={np.median(d1a[in1]):.0f}  max={d1a.max()}  frac<8={(d1a[in1]<8).mean():.3f}", flush=True)
print(f"ARM2 LCC N={in2.sum()}  median deg={np.median(d2a[in2]):.0f}  max={d2a.max()}  frac<8={(d2a[in2]<8).mean():.3f}", flush=True)
poprank = {cap.mbids[i]: r for r, i in enumerate(np.argsort(-cap.popularity))}
for lo, hi in [(0, 10), (10, 25), (25, 50), (50, 100), (100, 250), (250, 500), (500, 1000), (1000, 2500)]:
    ids = [idx[m] for m, r in poprank.items() if lo <= r < hi and m in idx]
    print(f"  pop rank {lo+1:5d}-{hi:5d}: median ARM1={np.median(d1a[ids]):5.1f}  median ARM2={np.median(d2a[ids]):5.1f}  n={len(ids)}", flush=True)
log("done")
