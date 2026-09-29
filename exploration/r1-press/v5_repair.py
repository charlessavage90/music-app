"""v5 local repair (best-so-far shape). A press keeps the journey and re-routes only the smallest
window around the pressed artist x, through artists at least MARGIN (percentile) less famous
than x; escalates window / extra hops / margin before anything else; never regenerates from
scratch unless every local option fails (then: constrained global route below x's fame, then
today's router). W_HOP > 0.02 discourages journeys growing."""
import os
from lib import route, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.10"))
W_HOP = float(os.environ.get("R1_WHOP", "0.02"))
W_X = float(os.environ.get("R1_WX", "0.0"))
LADDER = [(1, 0), (1, 1), (2, 0), (2, 1), (1, 2), (2, 2), (3, 2), (3, 3), (4, 4)]
_LOGNAME = os.path.basename(os.environ.get("R1_LOG", ""))  # debug log, confined to ./runs/
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", _LOGNAME) if _LOGNAME else None


def _log(msg):
    if LOG:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def repair(ctx, prev, pressed, margins=None):
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    bonus = {}
    if W_X:
        nb, sc = ctx.row(x)
        bonus = {v: W_X * s_ for v, s_ in zip(nb, sc)}
    for m in (margins or (MARGIN, MARGIN / 2, 0.0)):
        cap = ctx.pl[x] - m
        for w, extra in LADDER:
            a, b = max(0, i - w), min(len(prev) - 1, i + w)
            keep = set(prev[:a + 1]) | set(prev[b:])
            allowed = lambda v: v not in ps and v not in keep and ctx.pl[v] <= cap
            seg = route(ctx, prev[a], prev[b], allowed, bonus=bonus, w_hop=W_HOP,
                        banned_edge={prev[a], prev[b]}, max_hops=(b - a) + extra)
            if seg:
                return prev[:a] + seg + prev[b + 1:], f"ok m={m} w={w} e={extra}"
    return None, None


def journey(ctx, s, t, pressed, prev):
    if prev is None:
        return baseline(ctx, s, t, pressed)
    p, how = repair(ctx, prev, pressed)
    if p:
        _log(how)
        return p
    x = pressed[-1]
    ps = set(pressed)
    p = route(ctx, s, t, lambda v: v not in ps and ctx.pl[v] <= ctx.pl[x], banned_edge={s, t}, w_hop=W_HOP)
    if p:
        _log(f"global {ctx.names[s]}->{ctx.names[t]} x={ctx.names[x]}")
        return p
    _log(f"fallback {ctx.names[s]}->{ctx.names[t]} x={ctx.names[x]}")
    return baseline(ctx, s, t, pressed)
