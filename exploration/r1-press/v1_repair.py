"""v1 local repair: keep prev; re-route only pred->succ around the pressed artist, replacement
artists must be less famous than the pressed one (pctl < pctl(x) - MARGIN). Widen window if stuck."""
import os
from lib import route, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.0"))
EXTRA = int(os.environ.get("R1_EXTRA", "3"))   # extra hops allowed beyond the window (0 = length kept)
W_X = float(os.environ.get("R1_WX", "0.0"))    # prefer replacements similar to the pressed artist
W_FAME = float(os.environ.get("R1_WFAME", "0.0"))


def journey(ctx, s, t, pressed, prev):
    if prev is None:
        return baseline(ctx, s, t, pressed)
    x = pressed[-1]
    if x not in prev:
        return baseline(ctx, s, t, pressed)
    i = prev.index(x)
    ps = set(pressed)
    cap = ctx.pl[x] - MARGIN
    bonus = {}
    if W_X:
        nb, sc = ctx.row(x)
        bonus = {v: W_X * s_ for v, s_ in zip(nb, sc)}
    for w in (1, 2, 3):
        a, b = max(0, i - w), min(len(prev) - 1, i + w)
        keep = set(prev[:a + 1]) | set(prev[b:])
        allowed = lambda v: v not in ps and v not in keep and ctx.pl[v] < cap
        seg = route(ctx, prev[a], prev[b], allowed, w_fame=W_FAME,
                    banned_edge={prev[a], prev[b]}, max_hops=(b - a) + EXTRA, bonus=bonus)
        if seg:
            return prev[:a] + seg + prev[b + 1:]
    return baseline(ctx, s, t, pressed)
