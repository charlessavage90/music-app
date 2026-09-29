"""EXPLORATORY: compact per-press summary of runs, plus sub-floor step count ('fallback'),
mid-pair over-dive, and victim replacement (same rule as r1-rules/replace_check.py).
usage (from api/): uv run python ../exploration/r2-simple/stats.py MIN_SIM runs/a.json ..."""
from pathlib import Path as _P
def safe(f):
    """Refuse paths outside exploration/ (these scripts only read kit run files)."""
    q = _P(f).resolve(); base = _P(__file__).resolve().parents[1]
    if base not in q.parents:
        raise SystemExit(f"refusing path outside exploration/: {f}")
    return q

import json, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kit"))
from qlook import Ctx
ctx = Ctx()
floor = float(sys.argv[1])
import numpy as np
_off = np.asarray(ctx.store.offsets); BEST = np.maximum.reduceat(np.asarray(ctx.store.scores), _off[:-1])
def below(p, u, v):
    x = ctx.sim(u, v)
    if x >= floor: return False
    for e in (p[0], p[-1]):
        if e in (u, v) and x >= BEST[e]: return False
    return True
med = lambda xs: statistics.median(xs) if xs else float('nan')
for f in sys.argv[2:]:
    d = json.loads(safe(f).read_text(encoding='utf-8'))
    rows = d['rows']
    print(f"== {Path(f).stem}")
    print(" k | famous | mid  | len  | weak | top10 | midDive | subfloor journeys")
    for k in (0, 1, 2, 3, 5, 10):
        fam, mid, ln, wk, top, dive, sub = [], [], [], [], [], [], 0
        for r in rows:
            lad = r['ladder']
            if k >= len(lad) or not lad[k]['path']: continue
            p = lad[k]['path']; inter = [v for v in p[1:-1] if ctx.measured[v]]
            ln.append(len(p)); wk.append(min(ctx.sim(u, v) for u, v in zip(p, p[1:])))
            if any(below(p, u, v) for u, v in zip(p, p[1:])): sub += 1
            if not inter: continue
            m = med([ctx.pl[v] for v in inter])
            if r['tag'] == 'famous':
                fam.append(m); top.append(sum(ctx.pl[v] >= .9 for v in p[1:-1]) / len(p[1:-1]))
            else:
                mid.append(m); lo = min(ctx.pl[p[0]], ctx.pl[p[-1]])
                dive.append(sum(ctx.pl[v] < lo - 0.2 for v in inter) / len(inter))
        print(f"{k:>2} | {med(fam)*100:6.1f} | {med(mid)*100:4.1f} | {sum(ln)/len(ln):4.1f} | {med(wk):.2f} | {sum(top)/max(1,len(top))*100:4.0f}% | {sum(dive)/max(1,len(dive))*100:5.0f}% | {sub}/{len(ln)}")
    hit = tot = 0; early = []
    subtot = 0; alltot = 0
    for r in rows:
        lad = r['ladder']
        for k in range(len(lad) - 1):
            x = lad[k].get('victim'); nxt = lad[k + 1]['path']
            if x is None or not nxt: continue
            ok = any(ctx.sim(x, v) >= .5 or ctx.sim(v, x) >= .5 for v in nxt[1:-1] if ctx.pl[v] < ctx.pl[x])
            tot += 1; hit += ok
            if k < 5: early.append(ok)
        for st in lad:
            if st['path']:
                alltot += 1; p = st['path']
                subtot += any(below(p, u, v) for u, v in zip(p, p[1:]))
    secs = [st['secs'] for r in rows for st in r['ladder']]
    print(f"replace {hit}/{tot}={hit/tot:.0%} (p1-5 {sum(early)/len(early):.0%}); journeys with a step < {floor}: {subtot}/{alltot}; secs median {med(secs):.2f} max {max(secs):.2f}")
