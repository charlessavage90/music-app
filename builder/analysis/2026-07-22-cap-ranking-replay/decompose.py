"""Decompose ARM1 degree: is the coordinator's ~25% joint-survival arithmetic right?

Re-derives the pre-cap arrays (cached), then measures:
  - ceiling-pool size per node (does the tie-break bind at all?)
  - graph-wide reciprocity (the pure-A quantity), as a null for the top-25 figures
  - observed ARM1 degree vs MBID percentile r(u), among saturated nodes
  - a corrected survival model and its residual
"""
import sys, time, array, math
from pathlib import Path
import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
SCR = Path("C:/Users/charl/AppData/Local/Temp/claude/C--Users-charl-OneDrive-Claude-Projects-music-app/938e040a-82a4-4782-bdf6-a8373a2970ae/scratchpad")
sys.path.insert(0, str(ROOT / "builder" / "src")); sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.listenbrainz import ListenBrainzSource, harvest_identities
from artistpath_builder.pipeline import is_special_purpose
from artistpath_builder.graph import symmetrise, largest_component
from artistpath_api.graph_store import GraphStore

t0 = time.time()
def log(*a): print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)

cfg = BuilderConfig(); K = cfg.max_neighbours_per_artist
CACHE = SCR / "precap.npz"
if CACHE.exists():
    z = np.load(CACHE, allow_pickle=True)
    esrc, edst, estr, offsets, mbids = z["esrc"], z["edst"], z["estr"], z["offsets"], list(z["mbids"])
    log("cache loaded")
else:
    src = ListenBrainzSource(cfg)
    ARCH = ROOT / "builder" / "scratch" / "graph-archive" / "similar" / "listenbrainz"
    payloads = {p.name[:-5]: p.read_bytes() for p in sorted(ARCH.iterdir()) if p.name.endswith(".json")}
    log(f"payloads {len(payloads)}")
    identities = harvest_identities(payloads.values())
    known = set(payloads) - {m for m, (_n, d) in identities.items() if is_special_purpose(d)}
    excluded = {m for m, (_n, d) in identities.items() if is_special_purpose(d)}
    mbids = sorted(known); idx = {m: i for i, m in enumerate(mbids)}
    a1 = array.array("i"); a2 = array.array("i"); a3 = array.array("d"); off = array.array("i", [0])
    for i, m in enumerate(mbids):
        neigh = [n for n in src.parse(payloads[m], exclude_mbid=m) if n.mbid not in excluded]
        scored = [(n.mbid, math.log1p(max(0.0, n.score))) for n in neigh if n.mbid in known]
        scored.sort(key=lambda p: (-p[1], p[0]))
        d = {}
        for dst, v in scored: d[dst] = v
        for dst, v in d.items(): a1.append(i); a2.append(idx[dst]); a3.append(v)
        off.append(len(a2))
    esrc = np.frombuffer(a1, np.int32).copy(); edst = np.frombuffer(a2, np.int32).copy()
    estr = np.frombuffer(a3, np.float64).copy(); offsets = np.frombuffer(off, np.int32).copy()
    np.savez(CACHE, esrc=esrc, edst=edst, estr=estr, offsets=offsets, mbids=np.array(mbids))
    log("cache written")

N = len(mbids); E = len(edst); idx = {m: i for i, m in enumerate(mbids)}
raw = np.expm1(np.maximum(0.0, estr))
scale = float(np.percentile(raw, 99)); log_scale = math.log1p(scale)
clip = np.minimum(1.0, np.log1p(np.maximum(0.0, raw)) / log_scale)
isceil = clip >= 1.0
L = np.diff(offsets).astype(np.int64)
ceilpool = np.add.reduceat(isceil.astype(np.int64), offsets[:-1]) * (L > 0)
r = np.arange(N) / (N - 1)
log(f"N={N} E={E} p99={scale}")

# ---- how widely does the tie-break bind? -----------------------------------
print("\n=== does the top-k tie-break bind at all? ===", flush=True)
print(f"nodes with |out| > k(50)          : {(L > K).sum():6d}  ({(L>K).mean():.3f}) -- any truncation happens", flush=True)
print(f"nodes with ceiling pool > k(50)   : {(ceilpool > K).sum():6d}  ({(ceilpool>K).mean():.3f}) -- top-50 is FULLY MBID-arbitrary", flush=True)
print(f"nodes with 0 < ceilpool <= k      : {((ceilpool > 0) & (ceilpool <= K)).sum():6d}  -- all ceiling edges guaranteed selected", flush=True)
print(f"nodes with ceilpool == 0          : {(ceilpool == 0).sum():6d}", flush=True)

# ---- pure-A quantity graph-wide (the null for the top-25 recipFrac) --------
key = np.sort(esrc.astype(np.int64) * N + edst.astype(np.int64))
rev = edst.astype(np.int64) * N + esrc.astype(np.int64)
p = np.searchsorted(key, rev)
recip = (p < len(key)) & (key[np.minimum(p, len(key) - 1)] == rev)
print("\n=== pure-A: reciprocal listing, graph-wide (independent of any cap) ===", flush=True)
print(f"fraction of ALL pre-cap directed edges that are reciprocated: {recip.mean():.4f}", flush=True)
per_node = np.zeros(N); cnt = np.add.reduceat(recip.astype(np.int64), offsets[:-1]) * (L > 0)
per_node[L > 0] = cnt[L > 0] / L[L > 0]
print(f"per-node reciprocity fraction: median={np.median(per_node[L>0]):.3f} mean={per_node[L>0].mean():.3f}", flush=True)
cap = GraphStore.load(ROOT / "builder" / "scratch" / "graph-t15-capfix.bin")
order = np.argsort(-cap.popularity)
for lo, hi in [(0, 25), (25, 100), (100, 1000), (1000, 10000)]:
    ids = [idx[cap.mbids[i]] for i in order[lo:hi] if cap.mbids[i] in idx]
    print(f"  pop rank {lo+1:5d}-{hi:5d}: mean reciprocity={per_node[ids].mean():.3f}  mean ceilpool={ceilpool[ids].mean():5.1f}  mean |out|={L[ids].mean():5.1f}", flush=True)
poor = np.argsort(per_node[L > 0])
print(f"  graph-wide bottom quartile reciprocity = {np.quantile(per_node[L>0], 0.25):.3f}", flush=True)

# ---- rebuild ARM1 to get degrees, then test the survival model -------------
def top_k_sets(vals):
    out = []
    for i in range(N):
        a, b = int(offsets[i]), int(offsets[i + 1])
        if b - a <= K: out.append(set(edst[a:b].tolist()))
        else: out.append(set(edst[a:b][np.lexsort((edst[a:b], -vals[a:b]))[:K]].tolist()))
    return out
tk = top_k_sets(clip)
adj = {i: {} for i in range(N)}
for e in range(E):
    u = int(esrc[e]); v = int(edst[e])
    if v in tk[u] and u in tk[v]: adj[u][v] = 1.0
adjs = symmetrise(adj); keepset = largest_component(adjs)
deg1 = np.array([len(adj[i]) for i in range(N)])   # pre-LCC mutual degree (== final degree for kept nodes)
log("ARM1 rebuilt")

sat = ceilpool > K
print("\n=== ARM1 degree vs MBID percentile r(u), among nodes where the tie-break FULLY binds ===", flush=True)
print(f"n saturated nodes = {sat.sum()}", flush=True)
for lo, hi in [(0.0, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .5), (.5, .6), (.6, .7), (.7, .8), (.8, .9), (.9, 1.0)]:
    m = sat & (r >= lo) & (r < hi)
    if m.sum(): print(f"  r(u) [{lo:.1f},{hi:.1f}): n={m.sum():5d}  median deg={np.median(deg1[m]):5.1f}  mean={deg1[m].mean():5.1f}", flush=True)
from scipy.stats import spearmanr
print(f"  spearman(deg, r(u)) among saturated = {spearmanr(deg1[sat], r[sat]).statistic:+.4f}", flush=True)
print(f"  spearman(deg, r(u)) among UNsaturated = {spearmanr(deg1[~sat], r[~sat]).statistic:+.4f}", flush=True)

# ---- corrected model: partner-guarantee decomposition -----------------------
print("\n=== corrected survival model for the top-25 cohort ===", flush=True)
print(f"{'artist':28s} {'r(u)':>5s} {'obs':>4s} {'lottery partners':>16s} {'guaranteed partners':>19s} {'pred':>5s}", flush=True)
RH = "a74b1b7f-71a5-4011-9441-d0b5e4122711"
coh = [RH] + [cap.mbids[i] for i in order[:25]]
nm = ["Radiohead"] + [cap.names[i] for i in order[:25]]
tot_obs = tot_pred = 0
for m, name in zip(coh, nm):
    if m not in idx: continue
    i = idx[m]; a, b = int(offsets[i]), int(offsets[i + 1])
    sel = sorted(tk[i])
    lot = sum(1 for v in sel if ceilpool[v] > K)
    gua = len(sel) - lot
    # P(u in top50(v)) for a lottery partner v: u must be among the 50 lowest MBIDs
    # of v's ceiling pool; modelled as Binomial(ceilpool(v)-1, r(u)) < 50.
    from scipy.stats import binom
    pr = sum(binom.cdf(K - 1, max(int(ceilpool[v]) - 1, 1), r[i]) for v in sel if ceilpool[v] > K)
    pred = gua + pr
    tot_obs += deg1[i]; tot_pred += pred
    print(f"{name[:28]:28s} {r[i]:5.3f} {deg1[i]:4d} {lot:16d} {gua:19d} {pred:5.1f}", flush=True)
print(f"\ncohort total observed={tot_obs}  model-predicted={tot_pred:.0f}  "
      f"naive-independence prediction={25*len(coh)*0.5*0.5:.0f} (0.25*50 each)", flush=True)
log("done")
