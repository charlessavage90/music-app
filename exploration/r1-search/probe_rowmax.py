import sys; sys.path.insert(0,'../exploration/kit')
from qlook import Ctx
import numpy as np
ctx=Ctx(); pc=ctx.pctl
off=np.asarray(ctx.off); sc=np.asarray(ctx.sc)
rm=np.maximum.reduceat(sc, off[:-1]); rmed=np.array([np.median(sc[off[i]:off[i+1]]) for i in range(ctx.n)])
for lo,hi in ((0.99,1.01),(0.95,0.99),(0.8,0.95),(0.5,0.8),(0.2,0.5),(0,0.2)):
    m=(pc>=lo)&(pc<hi); print(lo,hi, 'rowmax q25/50/75',np.percentile(rm[m],[25,50,75]).round(2),'rowmedian',np.percentile(rmed[m],[25,50,75]).round(2))
