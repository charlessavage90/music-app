"""Journey-shaped ceiling: a global ceiling c (by press schedule) in the centre, loosened near
the two chosen artists. cap(v) = max(c, E(v) + A - G*(h(v)-1)) where h(v) is the graph hop
distance from v to the nearer endpoint and E(v) that endpoint's fame. So the journey may
descend gradually from a famous endpoint into an obscure centre. If blocked, c rises by 0.05
until a journey exists."""
import os
from rules_common import setup_common, find_journey, bfs_hops
SCHED = [float(x) for x in os.environ.get("R1_SCHED", "1.0,0.95,0.90,0.80,0.70,0.60,0.50,0.45,0.40,0.35,0.30").split(",")]
G = float(os.environ.get("R1_G", "0.1"))
A = float(os.environ.get("R1_A", "0.005"))
def setup(ctx): setup_common(ctx)

def caps(ctx, s, t, pressed, c):
    ex = set(pressed)
    ds, dt = bfs_hops(ctx, s, ex, 8), bfs_hops(ctx, t, ex, 8)
    cap = [c] * ctx.n
    es, et = ctx.pl[s], ctx.pl[t]
    for d, e in ((ds, es), (dt, et)):
        for v, h in d.items():
            if h == 0:
                continue
            x = min(1.0, e + A - G * (h - 1))
            if x > cap[v]:
                cap[v] = x
    return cap

def journey(ctx, s, t, pressed, prev):
    c = SCHED[min(len(pressed), len(SCHED) - 1)]
    if c >= 1.0:
        return find_journey(ctx, s, t, pressed, 1.0)
    while True:
        p = find_journey(ctx, s, t, pressed, caps(ctx, s, t, pressed, c))
        if p is not None and len(p) > 2:
            return p
        if c >= 1.0:
            return p
        c = min(1.0, c + 0.05)
