import sys, json
sys.path.insert(0, '../exploration/kit'); sys.path.insert(0, '../exploration/r1-edgecost')
import qlook, engine, numpy as np
ctx = qlook.Ctx(); E = engine.prep(ctx)
pairs = qlook.kit_pairs(ctx)
for tag, s, t in pairs[:15:3] + pairs[15:17]:
    for u in (s, t):
        a, b = E['off'][u], E['off'][u+1]
        f = E['fame'][E['nbr'][a:b]]
        print(tag, ctx.names[u], f"{ctx.pl[u]*100:.0f}", 'deg', b-a, 'nbr fame pct: min %.2f q25 %.2f med %.2f' % (f.min(), np.quantile(f,.25), np.median(f)), 'n<0.9:', (f<0.9).sum())
# global: rank distribution vs fame
f = E['fame']; src, nbr = E['src'], E['nbr']
top = f[src] > 0.99
print('edges from top1%: share to top10%', (f[nbr][top] > 0.9).mean(), 'mean sim', E['sc'][top].mean())
print('mutual top-5 among top1% edges', ((E['rank'][top]<5)&(E['rank_rev'][top]<5)).mean())
