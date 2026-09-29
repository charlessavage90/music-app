import sys; sys.path.insert(0,'../exploration/kit'); sys.path.insert(0,'../exploration/r1-rules')
from qlook import Ctx
from rules_common import rank_sims
ctx=Ctx(); rs=rank_sims(ctx)
import bisect
def info(a,b):
    u,v=ctx.lookup(a),ctx.lookup(b)
    nb,sc=ctx.row(u); j=bisect.bisect_left(nb,v)
    if j>=len(nb) or nb[j]!=v: return f"{a}->{b}: no edge"
    jj=ctx.off[u]+j
    nb2,_=ctx.row(v); k=ctx.off[v]+bisect.bisect_left(nb2,u)
    return f"{a}->{b}: sim {sc[j]:.3f} rank_u {rs[jj]:.2f} rank_v {rs[k]:.2f} deg {len(nb)}/{len(nb2)}"
for a,b in [("Louis Prima","BROCKHAMPTON"),("Pink Velvet","Samhain"),("The Vacant Lots","Pink Velvet"),("Stick to Your Guns","Knocked Loose"),("Luke James","PJ Morton"),("Tamia","Luke James"),("Lupe Fiasco","John Legend"),("SOFI","Gallya")]:
    print(info(a,b))
import statistics
print("median sim", statistics.median(ctx.sc))
