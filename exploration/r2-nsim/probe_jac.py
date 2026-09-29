import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'kit')); sys.path.insert(0, str(HERE))
from qlook import Ctx
from common import setup_common
from shared import edge_jaccard
ctx = Ctx(); setup_common(ctx); r = ctx._r1
jac = edge_jaccard(r['off'], r['nbr'], ctx.n)
pc = r['pc']; lo = np.minimum(pc[r['src']], pc[r['nbr']])
print('edges', len(jac), 'jac median', np.median(jac))
for a, b in [(0, .05), (.05, .2), (.2, .5), (.5, .8), (.8, .9), (.9, .99), (.99, 1.01)]:
    m = (lo >= a) & (lo < b)
    print(f'weaker fame [{a},{b}) n={m.sum()} jac med={np.median(jac[m]):.3f} p25={np.percentile(jac[m],25):.3f} raw med={np.median(r["sc"][m]):.2f} nsim med={np.median(r["nsim"][m]):.2f}')
meas = np.asarray(ctx.measured)
print('unmeasured nodes', (~meas.astype(bool)).sum(), 'pctl<0.05 nodes', (pc < 0.05).sum())
# fail-check of Jaccard: random pairs of nodes (not edges) must have ~0 overlap
rng = np.random.default_rng(0)
import bisect
off, nbr = r['off'], r['nbr']
vals = []
for _ in range(2000):
    u, v = rng.integers(0, ctx.n, 2)
    a = set(nbr[off[u]:off[u+1]].tolist()); b = set(nbr[off[v]:off[v+1]].tolist())
    vals.append(len(a & b) / max(1, len(a | b)))
print('random pairs jac mean', np.mean(vals))
# spot-check two edges
for x, y in [('Louis Prima', 'BROCKHAMPTON'), ('The Beatles', 'The Rolling Stones'), ('Ike & Tina Turner', 'NNB')]:
    u, v = ctx.lookup(x), ctx.lookup(y)
    lo_, hi_ = off[u], off[u+1]; j = lo_ + np.searchsorted(nbr[lo_:hi_], v)
    if j < hi_ and nbr[j] == v:
        a = set(nbr[off[u]:off[u+1]].tolist()); b = set(nbr[off[v]:off[v+1]].tolist())
        print(x, '->', y, 'raw', r['sc'][j], 'nsim', round(r['nsim'][j], 3), 'jac', jac[j], 'direct', len(a & b) / len(a | b), 'pctl', ctx.pl[u], ctx.pl[v])
    else:
        print(x, y, 'no edge')
