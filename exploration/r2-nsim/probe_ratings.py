"""EXPLORATORY. Which similarity predicts the rater's step score? Uses kit/step_cache.jsonl."""
import sys, json, bisect
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'kit')); sys.path.insert(0, str(HERE))
from qlook import Ctx
from common import setup_common
ctx = Ctx(); setup_common(ctx); r = ctx._r1
off, nbr, sc, nsim, rowmax = r['off'], r['nbr'], r['sc'], r['nsim'], r['rowmax']
def eidx(u, v):
    lo, hi = off[u], off[u+1]; j = lo + np.searchsorted(nbr[lo:hi], v)
    return j if j < hi and nbr[j] == v else -1
rows = []
for line in (HERE.parent / 'kit/step_cache.jsonl').read_text(encoding='utf-8').splitlines():
    d = json.loads(line)
    if d['r'] not in (0, 1, 2, 3): continue
    a, b = d['k'].split(' || ')
    u = ctx.id_by_name.get(a.lower()); v = ctx.id_by_name.get(b.lower())
    if u is None or v is None: continue
    j = eidx(u, v)
    if j < 0: continue
    Nu = set(nbr[off[u]:off[u+1]].tolist()); Nv = set(nbr[off[v]:off[v+1]].tolist())
    jac = len(Nu & Nv) / max(1, len(Nu | Nv))
    pu, pv = ctx.pl[u], ctx.pl[v]
    rows.append((d['r'], sc[j], nsim[j], min(pu, pv), max(pu, pv), jac, min(rowmax[u], rowmax[v]), ctx.measured[u] and ctx.measured[v]))
A = np.array(rows, dtype=float)
R, S, NS, LO, HI, JAC, RM, MEAS = A.T
print('n', len(A), 'mean rating', R.mean())
bad = R <= 1
def tab(x, name, bins):
    print(f'\n{name}:')
    for lo, hi in zip(bins, bins[1:]):
        m = (x >= lo) & (x < hi)
        if m.sum() >= 20:
            print(f'  [{lo:.2f},{hi:.2f}) n={m.sum():5d} mean={R[m].mean():.2f} bad={bad[m].mean():.0%}')
tab(S, 'raw sim', [0, .3, .4, .5, .6, .7, .8, .9, .99, 1.01])
tab(NS, 'nsim', [0, .3, .4, .5, .6, .7, .8, .9, .99, 1.01])
tab(JAC, 'jaccard shared nbrs', [0, .02, .05, .1, .15, .2, .3, .5, 1.01])
tab(LO, 'weaker-end fame', [0, .05, .1, .2, .4, .6, .8, .9, 1.01])
print('\nnsim>=0.9 split by raw sim:')
m0 = NS >= 0.9
for lo, hi in [(0, .4), (.4, .5), (.5, .6), (.6, .7), (.7, .8), (.8, 1.01)]:
    m = m0 & (S >= lo) & (S < hi)
    if m.sum() >= 15: print(f'  raw [{lo},{hi}) n={m.sum()} mean={R[m].mean():.2f} bad={bad[m].mean():.0%}')
print('\nnsim>=0.9 split by jaccard:')
for lo, hi in [(0, .03), (.03, .07), (.07, .15), (.15, .3), (.3, 1.01)]:
    m = m0 & (JAC >= lo) & (JAC < hi)
    if m.sum() >= 15: print(f'  jac [{lo},{hi}) n={m.sum()} mean={R[m].mean():.2f} bad={bad[m].mean():.0%}')
print('\nunmeasured endpoint:', (MEAS == 0).sum(), 'mean', R[MEAS == 0].mean() if (MEAS == 0).any() else None)
# correlations for low-fame steps only
for nm, m in [('all', np.ones(len(A), bool)), ('weaker<0.5', LO < 0.5), ('weaker>=0.9', LO >= .9)]:
    c = lambda x: np.corrcoef(x[m], R[m])[0, 1]
    print(f'{nm:12s} n={m.sum()} corr raw={c(S):.3f} nsim={c(NS):.3f} jac={c(JAC):.3f} geo={c(np.sqrt(S*NS)):.3f} min={c(np.minimum(S*1.6, NS)):.3f} logjac={c(np.log(JAC+.01)):.3f}')
