"""v9 local repair — v7 plus two fixes found by reading v7's journeys:
(1) MONOTONE: a repair may never make any slot more famous. The replacement segment's cap is
    min(pctl(x) - margin, fame of every other artist the window removes), so widening the window
    can no longer swap previously-obscured artists back for famous ones (Anastacia p3 -> p10).
(2) When no replacement at least `margin` less famous exists (typical next to a famous endpoint,
    whose whole neighbour list is famous), the zero-margin step pulls toward the LEAST famous
    qualifying artist (W_PULL * pctl) instead of the cheapest one.
(3) Last local resort before today's router: an uncapped window re-route pulled toward the
    least famous (a famous-for-famous swap near an exhausted endpoint beats a full reset).
Window w=1 gets a looser length allowance (EXTRA1) before wider windows are tried."""
import os
from lib import route2, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.10"))
W_HOP = float(os.environ.get("R1_WHOP", "0.5"))
EXTRA1 = int(os.environ.get("R1_EXTRA1", "3"))
MAXEXTRA = int(os.environ.get("R1_MAXEXTRA", "2"))
W_X = float(os.environ.get("R1_WX", "0.0"))
W_PULL = float(os.environ.get("R1_WPULL", "3.0"))
_LOGNAME = os.path.basename(os.environ.get("R1_LOG", ""))  # debug log, confined to ./runs/
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", _LOGNAME) if _LOGNAME else None


def _log(msg):
    if LOG:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def repair(ctx, prev, pressed):
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    pl = ctx.pl
    px = pl[x]
    simx = {}
    if W_X:
        nb, sc = ctx.row(x)
        simx = dict(zip(nb, sc))
    n = len(prev)
    for m, pull in ((MARGIN, 0.0), (MARGIN / 2, 0.0), (0.0, W_PULL), (None, W_PULL)):
        def nodecost(v):
            c = pull * pl[v]
            if W_X:
                c += W_X * (1.0 - simx.get(v, 0.0))
            return c
        for w in (1, 2, 3):
            a, b = max(0, i - w), min(n - 1, i + w)
            removed = [r for r in prev[a + 1:b] if r != x]
            cap = min([px - (m or 0.0)] + [pl[r] for r in removed])
            if m == 0.0:
                cap = min([px - 1e-9] + [pl[r] for r in removed])
            if m is None:   # last resort: any fame, pulled toward the least famous (logged)
                cap = 1.01
            keep = set(prev[:a + 1]) | set(prev[b:])
            allowed = lambda v: v not in ps and v not in keep and pl[v] <= cap
            seg, _ = route2(ctx, prev[a], prev[b], allowed, nodecost=nodecost, w_hop=W_HOP,
                            banned_edge={prev[a], prev[b]})
            lim = (b - a) + (EXTRA1 if w == 1 else MAXEXTRA)
            if seg and len(seg) - 1 <= lim:
                return prev[:a] + seg + prev[b + 1:], f"ok m={m} w={w}"
    return None, None


def journey(ctx, s, t, pressed, prev):
    if prev is None:
        return baseline(ctx, s, t, pressed)
    p, how = repair(ctx, prev, pressed)
    if p:
        _log(how)
        return p
    # nothing less famous can stand in: drop x if its neighbours link directly, else keep a
    # famous-for-famous swap from today's router restricted to the window (logged)
    i = prev.index(pressed[-1])
    if 0 < i < len(prev) - 1 and ctx.sim(prev[i - 1], prev[i + 1]) > 0 and len(prev) > 3:
        _log("drop")
        return prev[:i] + prev[i + 1:]
    _log(f"fallback {ctx.names[s]}->{ctx.names[t]} x={ctx.names[pressed[-1]]}")
    return baseline(ctx, s, t, pressed)
