"""v3 local repair with an escalation ladder (never silently regenerate from scratch).
Keep prev; re-route the smallest window around the pressed artist x through artists with
pctl <= pctl(x) - MARGIN, allowing progressively more extra hops / wider windows; then halve the
margin; baseline regeneration only as the very last resort (logged)."""
import os
from lib import route, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.10"))
W_X = float(os.environ.get("R1_WX", "0.0"))
W_FAME = float(os.environ.get("R1_WFAME", "0.0"))
LADDER = [(1, 0), (1, 1), (2, 0), (1, 2), (2, 1), (2, 2), (3, 2)]
LOG = os.environ.get("R1_LOG")


def _log(msg):
    if LOG:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def journey(ctx, s, t, pressed, prev):
    if prev is None or pressed[-1] not in prev:
        return baseline(ctx, s, t, pressed)
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    bonus = {}
    if W_X:
        nb, sc = ctx.row(x)
        bonus = {v: W_X * s_ for v, s_ in zip(nb, sc)}
    for m in (MARGIN, MARGIN / 2, 0.0):
        cap = ctx.pl[x] - m
        for w, extra in LADDER:
            a, b = max(0, i - w), min(len(prev) - 1, i + w)
            keep = set(prev[:a + 1]) | set(prev[b:])
            allowed = lambda v: v not in ps and v not in keep and ctx.pl[v] <= cap
            seg = route(ctx, prev[a], prev[b], allowed, w_fame=W_FAME, bonus=bonus,
                        banned_edge={prev[a], prev[b]}, max_hops=(b - a) + extra)
            if seg:
                _log(f"ok m={m} w={w} e={extra}")
                return prev[:a] + seg + prev[b + 1:]
    _log("fallback")
    return baseline(ctx, s, t, pressed)
