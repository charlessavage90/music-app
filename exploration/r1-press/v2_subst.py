"""v2 substitute-then-stitch: replace the pressed artist x with one of its own less-famous
neighbours y (pctl(y) <= pctl(x) - MARGIN), stitched pred -> (<=1 link) -> y -> (<=1 link) -> succ.
Choose y minimising 3(1-sim(x,y)) + stitched segment cost. Length grows by at most 2 per press."""
import os
from lib import route, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.10"))
NCAND = int(os.environ.get("R1_NCAND", "20"))
STITCH = int(os.environ.get("R1_STITCH", "2"))   # max hops pred->y and y->succ


def seg_cost(ctx, p):
    pop = ctx.store.pop_raw
    return sum(3 * (1 - ctx.sim(u, v)) + abs(float(pop[u]) - float(pop[v])) + 0.02 for u, v in zip(p, p[1:]))


def journey(ctx, s, t, pressed, prev):
    if prev is None or pressed[-1] not in prev:
        return baseline(ctx, s, t, pressed)
    x = pressed[-1]
    i = prev.index(x)
    pred, succ = prev[i - 1], prev[i + 1]
    ps = set(pressed)
    keep = set(prev) - {x}
    cap = ctx.pl[x] - MARGIN
    nb, sc = ctx.row(x)
    cands = sorted([(s_, y) for y, s_ in zip(nb, sc) if y not in ps and y not in keep and ctx.pl[y] <= cap],
                   reverse=True)[:NCAND]
    best = None
    for sxy, y in cands:
        allowed = lambda v: v not in ps and v not in keep and v != y and ctx.pl[v] <= ctx.pl[x]
        a = route(ctx, pred, y, allowed, max_hops=STITCH)
        if not a:
            continue
        b = route(ctx, y, succ, lambda v: allowed(v) and v not in a, max_hops=STITCH)
        if not b:
            continue
        c = 3 * (1 - sxy) + seg_cost(ctx, a) + seg_cost(ctx, b)
        if best is None or c < best[0]:
            best = (c, a + b[1:])
    if best:
        return prev[:i - 1] + best[1] + prev[i + 2:]
    return baseline(ctx, s, t, pressed)
