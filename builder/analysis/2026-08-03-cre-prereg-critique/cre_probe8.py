"""CRE critique probe 8. READ-ONLY. Q4: is the ramp in a regime that can matter
without dominating? Compares the ramp toll against the OTHER cost terms as they
are realised on chosen path edges in the committed Track 3 / 3b ladders."""
import hashlib
import json
import sys

import numpy as np

sys.path.insert(0, "C:/dev/music-app/api/src")
from artistpath_api.config import ApiConfig        # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402

GA = "C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin"
assert hashlib.sha256(open(GA, "rb").read()).hexdigest().startswith("4cb84ef9")
st = GraphStore.load(GA)
N = st.artist_count
cfg = ApiConfig()
sim_of = {}
for u in range(N):
    for v, s in st.neighbours_of(u):
        sim_of[(u, v)] = float(s)

R = "C:/dev/music-app/builder/analysis/"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


print("== realised per-edge cost terms on CHOSEN path edges, by arm and depth band ==")
for tag, f in (("Track 3", R + "2026-07-28-track3-depth-descent/t3_paths.json"),
               ("Track 3b", R + "2026-07-29-track3b-thresholded-toll/tb_paths.json")):
    doc = load(f)
    ramps = doc.get("ramps") or doc.get("ws")
    for arm, pp in doc["paths"].items():
        for lab, depths in (("d0", (0,)), ("d10-20", (10, 15, 20))):
            sims, jumps = [], []
            for pair, pd in pp.items():
                for d in depths:
                    p = pd.get(str(d))
                    if not p:
                        continue
                    for a, b in zip(p, p[1:]):
                        sims.append(cfg.w_sim * (1.0 - sim_of.get((a, b), 0.0)))
                        jumps.append(cfg.w_jump * abs(float(st.pop_raw[a])
                                                      - float(st.pop_raw[b])))
            if not sims:
                continue
            print(f"  {tag} {arm:8s} (w={ramps.get(arm)}) {lab:7s} "
                  f"mean w_sim*(1-sim)={np.mean(sims):.4f} "
                  f"median={np.median(sims):.4f} | mean w_jump*|dpop|={np.mean(jumps):.4f} "
                  f"| w_hop={cfg.w_hop}")

print("\n== ramp toll per interior, r * k * fame_lb_pctl, at pctl 0.99 ==")
print(f"  {'r':>6s} " + " ".join(f"k={k:<7d}" for k in (1, 3, 5, 10, 20)))
for r in (0.01, 0.03, 0.05, 0.10, 0.15, 1.0):
    print(f"  {r:6.2f} " + " ".join(f"{r*k*0.99:<9.3f}" for k in (1, 3, 5, 10, 20)))
print("\n  For scale: production w_hop = 0.02; the w_sim term on the edges the "
      "router ACTUALLY chose is printed above (production arm, d0).")
