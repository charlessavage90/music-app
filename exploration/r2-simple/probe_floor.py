"""EXPLORATORY: how many artists have no link at/above the floor; which kit journeys cross a sub-floor step at p0."""
from pathlib import Path as _P
def safe(f):
    """Refuse paths outside exploration/ (these scripts only read kit run files)."""
    q = _P(f).resolve(); base = _P(__file__).resolve().parents[1]
    if base not in q.parents:
        raise SystemExit(f"refusing path outside exploration/: {f}")
    return q

import sys, json, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kit"))
from qlook import Ctx
ctx = Ctx(); st = ctx.store
off = np.asarray(st.offsets); sc = np.asarray(st.scores)
best = np.maximum.reduceat(sc, off[:-1])
for f in (0.6, 0.7, 0.75): print(f, "nodes with best link below floor:", int((best < f).sum()), "of", len(best))
d = json.loads(safe(sys.argv[1]).read_text(encoding="utf-8"))
for r in d["rows"]:
    p = r["ladder"][0]["path"]
    w = [(ctx.names[u], ctx.names[v], round(ctx.sim(u, v), 2)) for u, v in zip(p, p[1:]) if ctx.sim(u, v) < 0.7]
    if w: print(r["source_name"], "->", r["target_name"], w, "best s/t", round(best[r["source"]],2), round(best[r["target"]],2))
fame = ctx.pctl; meas = np.asarray(ctx.measured)
print("unmeasured:", int((~meas).sum()))
for q in (0.01, 0.03, 0.05):
    idx = np.where(meas & (fame < q))[0]
    print(q, len(idx), [ctx.names[i] for i in np.random.default_rng(1).choice(idx, 25, replace=False)])
