"""v8 pressed-artist-as-direction: full reroute each press (pressed excluded), but every pressed
artist x makes its less famous neighbours cheaper to visit: bonus W * sim(x,v) for v with
pctl(v) <= pctl(x) - MARGIN. Bonuses accumulate over presses (max per node)."""
import os
from lib import route, baseline

W = float(os.environ.get("R1_W", "1.0"))
MARGIN = float(os.environ.get("R1_MARGIN", "0.05"))


def journey(ctx, s, t, pressed, prev):
    if not pressed:
        return baseline(ctx, s, t, pressed)
    bonus = {}
    for x in pressed:
        nb, sc = ctx.row(x)
        for v, s_ in zip(nb, sc):
            if ctx.pl[v] <= ctx.pl[x] - MARGIN:
                bonus[v] = max(bonus.get(v, 0.0), W * s_)
    ps = set(pressed)
    p = route(ctx, s, t, lambda v: v not in ps, bonus=bonus, banned_edge={s, t})
    return p or baseline(ctx, s, t, pressed)
