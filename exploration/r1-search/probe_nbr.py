import sys; sys.path.insert(0,'../exploration/kit')
from qlook import Ctx
import numpy as np
ctx=Ctx(); pc=ctx.pctl
off=np.asarray(ctx.off); nbr=np.asarray(ctx.nbr); sc=np.asarray(ctx.sc)
src=np.repeat(np.arange(ctx.n),np.diff(off))
for lo,hi in ((0.99,1.01),(0.95,0.99),(0.8,0.95),(0.5,0.8),(0.2,0.5),(0,0.2)):
    m=(pc[src]>=lo)&(pc[src]<hi)
    pv=pc[nbr[m]]; s=sc[m]
    print(f"src {lo}-{hi}: edges {m.sum()} nbr-pctl q25/50/75 {np.percentile(pv,[25,50,75]).round(2)}  sim med {np.median(s):.2f}  frac nbr<0.9 {np.mean(pv<0.9):.2f} sim of those {np.median(s[pv<0.9]) if (pv<0.9).any() else 0:.2f}  sim of nbr>=0.95 {np.median(s[pv>=0.95]) if (pv>=0.95).any() else 0:.2f}")
