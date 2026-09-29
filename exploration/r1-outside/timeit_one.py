import sys, time
import os; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H+'/../kit'); sys.path.insert(0, H)
import qlook, importlib
ctx = qlook.Ctx()
import numpy as np
for name in sys.argv[1:]:
    mod = qlook.load_variant(name)
    mod.setup(ctx)
    s, t = ctx.lookup('Lupe Fiasco'), ctx.lookup('Kid Rock')
    t0 = time.time(); p = mod.journey(ctx, s, t, [], None); print(name, round(time.time()-t0, 2), [ctx.names[v] for v in p])
w = np.array(ctx.wdeg); print('wdeg pct', np.percentile(w, [0, 1, 10, 50, 90, 99, 100]))
