"""v4 local repair, v3 plus: a minimum link similarity in repaired segments (relaxed last),
a length budget (journey may grow at most MAXGROW artists over press 0), and a constrained
global fallback (whole journey rerouted with every middle artist below the pressed artist's fame)
instead of an unconstrained regeneration."""
import os
from lib import route, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.10"))
MINSIM = float(os.environ.get("R1_MINSIM", "0.7"))
MAXGROW = int(os.environ.get("R1_MAXGROW", "4"))
W_X = float(os.environ.get("R1_WX", "0.0"))
LADDER = [(1, 0), (1, 1), (2, 0), (2, 1), (1, 2), (2, 2), (3, 2)]
LOG = os.environ.get("R1_LOG")
_P0 = {}


def _log(msg):
    if LOG:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def journey(ctx, s, t, pressed, prev):
    if prev is None:
        p = baseline(ctx, s, t, pressed)
        _P0[(s, t)] = len(p) if p else 0
        return p
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    budget = _P0.get((s, t), len(prev)) + MAXGROW
    bonus = {}
    if W_X:
        nb, sc = ctx.row(x)
        bonus = {v: W_X * s_ for v, s_ in zip(nb, sc)}
    for ms in (MINSIM, 0.0):
        for m in (MARGIN, MARGIN / 2):
            cap = ctx.pl[x] - m
            for w, extra in LADDER:
                a, b = max(0, i - w), min(len(prev) - 1, i + w)
                room = budget - len(prev)
                extra = min(extra, max(room, 0))
                keep = set(prev[:a + 1]) | set(prev[b:])
                allowed = lambda v: v not in ps and v not in keep and ctx.pl[v] <= cap
                seg = route(ctx, prev[a], prev[b], allowed, bonus=bonus, minsim=ms,
                            banned_edge={prev[a], prev[b]}, max_hops=(b - a) + extra)
                if seg:
                    _log(f"ok ms={ms} m={m} w={w} e={extra}")
                    return prev[:a] + seg + prev[b + 1:]
    # constrained global fallback: every middle artist below the pressed artist's fame
    cap = ctx.pl[x]
    p = route(ctx, s, t, lambda v: v not in ps and ctx.pl[v] < cap, banned_edge={s, t})
    if p:
        _log("global")
        return p
    _log("fallback")
    return baseline(ctx, s, t, pressed)
