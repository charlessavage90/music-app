"""v7 (press-relative, compounding rarity ceiling, loosened near endpoints, min step sim 0.4)
plus a LENGTH rule: a journey may not exceed max(len at press 0 + EXTRA, MINLEN) artists;
if it does, the centre ceiling rises 0.05 at a time until it fits."""
import os
import v6_layered as L
MULT = float(os.environ.get("R1_MULT", "3"))
EXTRA = int(os.environ.get("R1_EXTRA", "3"))
MINLEN = int(os.environ.get("R1_MINLEN", "9"))
def setup(ctx):
    L.setup(ctx); ctx._r1_len0 = {}
def _route(ctx, s, t, pressed, c):
    p = L.route(ctx, s, t, pressed, c)
    if p is not None and len(p) == 2:
        p = L.route(ctx, s, t, pressed, c, forbidden=True) or p
    return p
def journey(ctx, s, t, pressed, prev):
    if (s, t) not in ctx._r1_len0:
        p0 = _route(ctx, s, t, [], 1.0)
        ctx._r1_len0[(s, t)] = len(p0) if p0 else 8
    lim = max(ctx._r1_len0[(s, t)] + EXTRA, MINLEN)
    c = 1.0
    for x in pressed:
        c = min(c, ctx.pl[x])
        c = max(0.0, 1.0 - MULT * (1.0 - c))
    fallback = None
    while True:
        p = _route(ctx, s, t, pressed, c)
        if p is not None and len(p) > 2:
            if len(p) <= lim:
                return p
            fallback = fallback or p
        if c >= 1.0:
            if fallback: return fallback
            p = L.route(ctx, s, t, pressed, 1.0, minsim=0.0)
            if p is not None and len(p) == 2:
                p = L.route(ctx, s, t, pressed, 1.0, forbidden=True, minsim=0.0) or p
            return p
        c = min(1.0, c + 0.05)
