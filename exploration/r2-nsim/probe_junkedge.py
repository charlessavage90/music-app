"""EXPLORATORY: are high-score / low-overlap links junk by the rater's lights?"""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'kit')); sys.path.insert(0, str(HERE))
from qlook import Ctx
from r2nsim_core import _shared
ctx = Ctx(); sh = _shared(ctx)
off, nbr, sc, jac, nsim = sh['off'], sh['nbr'], sh['sc'], sh['jac'], sh['nsim']
R, S, J, N = [], [], [], []
for line in (HERE.parent / 'kit/step_cache.jsonl').read_text(encoding='utf-8').splitlines():
    d = json.loads(line)
    if d['r'] not in (0, 1, 2, 3): continue
    a, b = d['k'].split(' || ')
    u = ctx.id_by_name.get(a.lower()); v = ctx.id_by_name.get(b.lower())
    if u is None or v is None: continue
    lo, hi = off[u], off[u+1]; j = lo + np.searchsorted(nbr[lo:hi], v)
    if j >= hi or nbr[j] != v: continue
    R.append(d['r']); S.append(sc[j]); J.append(jac[j]); N.append(nsim[j])
R, S, J, N = map(np.array, (R, S, J, N)); bad = R <= 1
for jl, jh in [(0, .02), (.02, .05), (.05, .1), (.1, 1.1)]:
    for sl, sh_ in [(0, .6), (.6, .9), (.9, 1.1)]:
        m = (J >= jl) & (J < jh) & (S >= sl) & (S < sh_)
        if m.sum() >= 15: print(f'jac[{jl},{jh}) raw[{sl},{sh_}) n={m.sum():4d} mean={R[m].mean():.2f} bad={bad[m].mean():.0%} zero={np.mean(R[m]==0):.0%}')
print('share of all map edges with jac<0.05:', np.mean(jac < 0.05))
