# fail-check: with b=0 and a press-1 call using NO exclusions, the DP must return today's path when
# today's path length is within [L0, L0+slack] (it is: it IS L0). Checks the DP reproduces Dijkstra.
import os, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H + '/../kit'); sys.path.insert(0, H)
import qlook, fixedlen, numpy as np
ctx = qlook.Ctx(); fixedlen.setup_arrays(ctx)
cfg = ctx.cfg
same = 0; tot = 0
for tag, s, t in qlook.kit_pairs(ctx):
    p = ctx.find_journey(ctx.store, s, t, [], cfg)[0]
    nc = cfg.w_floor * np.maximum(0.0, min(ctx.A_pop[s], ctx.A_pop[t]) - ctx.A_pop); 
    t0 = time.time(); q = fixedlen.exact_hops(ctx, s, t, set(), nc, len(p) - 1, len(p) - 1); dt = time.time() - t0
    tot += 1; same += (p == q)
    if p != q: print('DIFF', [ctx.names[v] for v in p], [ctx.names[v] for v in (q or [])])
print(f'{same}/{tot} identical; last dp {dt:.2f}s')
