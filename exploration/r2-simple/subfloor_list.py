"""EXPLORATORY: which journeys use a step below the floor (after endpoint relaxation), per pair."""
from pathlib import Path as _P
def safe(f):
    """Refuse paths outside exploration/ (these scripts only read kit run files)."""
    q = _P(f).resolve(); base = _P(__file__).resolve().parents[1]
    if base not in q.parents:
        raise SystemExit(f"refusing path outside exploration/: {f}")
    return q

import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kit"))
from qlook import Ctx
ctx = Ctx(); fl = float(sys.argv[1])
off = np.asarray(ctx.store.offsets); BEST = np.maximum.reduceat(np.asarray(ctx.store.scores), off[:-1])
d = json.loads(safe(sys.argv[2]).read_text(encoding='utf-8'))
for r in d['rows']:
    hits = []
    for st in r['ladder']:
        p = st['path']
        bad = [(ctx.names[u], ctx.names[v], round(ctx.sim(u, v), 2)) for u, v in zip(p, p[1:])
               if ctx.sim(u, v) < fl and not any(e in (u, v) and ctx.sim(u, v) >= BEST[e] for e in (p[0], p[-1]))]
        if bad: hits.append((st['k'], bad))
    if hits: print(r['source_name'], '->', r['target_name'], f"{len(hits)} presses;", hits[:1], hits[-1:])
