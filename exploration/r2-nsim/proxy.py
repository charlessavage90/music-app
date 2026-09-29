"""EXPLORATORY unrated proxy: per press, share of steps with low shared-neighbour overlap (jac<0.05),
median step jac, cached rater mean where the step is already cached (coverage shown). Reads run jsons."""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'kit')); sys.path.insert(0, str(HERE))
from qlook import Ctx
from common import setup_common
from shared import edge_jaccard
ctx = Ctx(); setup_common(ctx); r = ctx._r1
jac = edge_jaccard(r['off'], r['nbr'], ctx.n); off, nbr = r['off'], r['nbr']
cache = {}
for line in (HERE.parent / 'kit/step_cache.jsonl').read_text(encoding='utf-8').splitlines():
    d = json.loads(line); cache[d['k']] = d['r']
def J(u, v):
    lo, hi = off[u], off[u+1]; j = lo + np.searchsorted(nbr[lo:hi], v)
    return float(jac[j]) if j < hi and nbr[j] == v else 0.0
def key(u, v):
    a, b = sorted((ctx.names[u], ctx.names[v])); return f'{a} || {b}'
for f in sys.argv[1:]:
    import re
    m = re.fullmatch(r'(?:\.\./exploration/)?([A-Za-z0-9_-]+)/runs/([A-Za-z0-9_.-]+\.json)', f.replace(chr(92), '/'))
    if not m: raise SystemExit('expected <exploration-dir>/runs/<name>.json')
    q = HERE.parent / m.group(1) / 'runs' / m.group(2)
    d = json.loads(q.read_text(encoding='utf-8'))
    print(f'\n{q.name}: press | low-overlap steps | med jac | cached rating (coverage) | len famous/mid')
    for k in (0, 1, 2, 3, 5, 7, 10):
        lows, js, rs, n, lf, lm = [], [], [], 0, [], []
        for row in d['rows']:
            lad = row['ladder']
            if k >= len(lad) or not lad[k]['path']: continue
            p = lad[k]['path']; (lf if row['tag'] == 'famous' else lm).append(len(p))
            for u, v in zip(p, p[1:]):
                x = J(u, v); js.append(x); lows.append(x < 0.05); n += 1
                c = cache.get(key(u, v))
                if isinstance(c, int): rs.append(c)
        print(f'  {k:2d} | {np.mean(lows):.0%} | {np.median(js):.3f} | {np.mean(rs)/3 if rs else float("nan"):.2f} ({len(rs)/max(1,n):.0%}) | {np.mean(lf):.1f}/{np.mean(lm):.1f}')
