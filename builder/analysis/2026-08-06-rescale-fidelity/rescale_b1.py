"""B1 — what does `p99_log_clip` leave the router able to distinguish?

DESCRIPTIVE. No arms, no hypothesis, no threshold, and it licenses no
adoption. It measures the behaviour of a function that is already shipped,
the way one would read a config value - which is why it carries no
pre-registration. Anything COMPARING rescales would need one.

The router's similarity term is `w_sim * (1 - similarity)` with w_sim = 3.0,
and `similarity` is the RESCALED value stored in the artifact. So the
question that matters is not "how much information does the log destroy" in
the abstract, but "how much cost leverage is left, next to the other terms
the router weighs at the same moment".

Run from `api/`:
  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    ../builder/analysis/2026-08-06-rescale-fidelity/rescale_b1.py
"""
import json
import math
import os

import numpy as np
from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = "../builder/scratch/graph-msw-tu50.bin"
SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
ARCHIVE = ("../builder/scratch/grt-archive-algb/similar/listenbrainz/"
           "session_based_days_7500_session_300_contribution_3_threshold_10_"
           "limit_100_filter_True_skip_30/")

g = GraphStore.load(GRAPH)
cfg = ApiConfig()
assert g.source_sha256 in ("", SHA), "artifact mismatch"
deg = np.diff(g.offsets)
S = g.scores
out = {}

print(f"artifact: {g.artist_count} artists, {len(S)} directed edges")
print(f"w_sim={cfg.w_sim}  w_hop={cfg.w_hop}  "
      f"w_known_ramp_fame_pctl={cfg.w_known_ramp_fame_pctl}")
print()

# --- 1. How much of the 0-1 range is actually used, and what clips? -------
clipped = float((S >= 0.9999).mean())
print("=== 1. THE STORED SIMILARITY DISTRIBUTION ===")
print(f"  edges pinned at 1.0 (clipped): {100*clipped:.2f}%")
for q in (1, 5, 25, 50, 75, 95, 99):
    print(f"  p{q:<3} = {np.percentile(S, q):.3f}")
out["pct_edges_clipped_at_1"] = round(100 * clipped, 3)
out["score_percentiles"] = {f"p{q}": round(float(np.percentile(S, q)), 4)
                            for q in (1, 5, 25, 50, 75, 95, 99)}

# --- 2. Within ONE artist's neighbourhood, what can the router see? -------
# This is the choice the router actually makes: standing on artist v, which
# neighbour do I step to?
spreads, top_ties = [], 0
for v in range(g.artist_count):
    a, b = g.offsets[v], g.offsets[v + 1]
    if b - a < 2:
        continue
    row = S[a:b]
    spreads.append(float(row.max() - row.min()))
    if float((row >= 0.9999).sum()) > 1:
        top_ties += 1
spreads = np.array(spreads)
print()
print("=== 2. WITHIN ONE ARTIST'S NEIGHBOURHOOD ===")
print(f"  median spread (best neighbour - worst): {np.median(spreads):.3f}")
print(f"  => similarity cost leverage across the WHOLE neighbourhood: "
      f"{cfg.w_sim * np.median(spreads):.3f}")
print(f"  artists with 2+ neighbours tied at the 1.0 ceiling: "
      f"{100*top_ties/len(spreads):.2f}%")
out["median_within_artist_spread"] = round(float(np.median(spreads)), 4)
out["median_cost_leverage_whole_neighbourhood"] = round(
    float(cfg.w_sim * np.median(spreads)), 4)
out["pct_artists_with_tied_top_neighbours"] = round(100 * top_ties / len(spreads), 3)

# --- 3. What the router is weighing that AGAINST ---------------------------
print()
print("=== 3. THE COMPETING TERMS, AT THE SAME MOMENT ===")
ramp20 = cfg.w_known_ramp_fame_pctl * 20
print(f"  similarity, best vs worst neighbour (median artist): "
      f"{cfg.w_sim*np.median(spreads):.3f}")
print(f"  fame ramp at 20 presses, famous vs unknown neighbour: {ramp20:.3f}")
print(f"  one extra hop:                                       {cfg.w_hop:.3f}")
out["ramp_at_20_presses_full_fame_range"] = round(ramp20, 4)
out["w_hop"] = cfg.w_hop

# --- 4. Raw space: what was thrown away? ----------------------------------
# Sample raw scores from the archive and map them through the shipped rescale.
raws = []
for i in range(0, g.artist_count, 11):
    p = ARCHIVE + g.mbids[i] + ".json"
    if not os.path.exists(p):
        continue
    with open(p, encoding="utf-8") as fh:
        raws.extend(r["score"] for r in json.load(fh))
raws = np.array(raws, dtype=float)
p99 = float(np.percentile(raws, 99))
ls = math.log1p(p99)
print()
print("=== 4. RAW -> RESCALED (sampled {} edges, p99 = {:.0f}) ===".format(
    len(raws), p99))
print(f"  {'raw':>8} {'rescaled':>10} {'sim cost':>10}")
for s in (25, 50, 100, 200, 400, 918, 2000, 5000):
    r = min(1.0, math.log1p(s) / ls)
    print(f"  {s:>8} {r:>10.3f} {cfg.w_sim*(1-r):>10.3f}")
out["raw_p99"] = round(p99, 1)
out["raw_to_rescaled"] = {str(s): round(min(1.0, math.log1p(s)/ls), 4)
                          for s in (25, 50, 100, 200, 400, 918, 2000, 5000)}
out["pct_raw_edges_at_or_above_p99"] = round(100 * float((raws >= p99).mean()), 3)

with open(os.path.join(HERE, "rescale_b1.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)
print()
print("wrote rescale_b1.json")
