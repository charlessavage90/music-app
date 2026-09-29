"""v6 local repair, fast and never resetting. A press keeps the journey and re-routes the
smallest window (pred..succ, then +-2, +-3) around the pressed artist x through artists at most
cap = pctl(x) - MARGIN famous, with a pull toward a target band (pctl(x) - MARGIN) so the descent is
one layer at a time rather than a dive; a repair may add at most MAXEXTRA artists. If nothing
qualifies, the margin shrinks, then the fame cap is lifted (band pull only). Only if the window
cannot be re-routed at all does it fall back to today's router."""
import os
from lib import route2, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.10"))
W_BAND = float(os.environ.get("R1_WBAND", "1.0"))
W_HOP = float(os.environ.get("R1_WHOP", "0.02"))
MAXEXTRA = int(os.environ.get("R1_MAXEXTRA", "2"))
W_X = float(os.environ.get("R1_WX", "0.0"))
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
    simx = {}
    if W_X:
        nb, sc = ctx.row(x)
        simx = dict(zip(nb, sc))
    for m, capped in ((MARGIN, True), (MARGIN / 2, True), (0.0, True), (MARGIN, False)):
        target = max(0.0, pl[x] - m)
        cap = target if capped else 1.01
        nodecost = lambda v: W_BAND * abs(pl[v] - target) + W_X * (1.0 - simx.get(v, 0.0))
        for w in (1, 2, 3):
            a, b = max(0, i - w), min(len(prev) - 1, i + w)
            keep = set(prev[:a + 1]) | set(prev[b:])
            allowed = lambda v: v not in ps and v not in keep and pl[v] <= cap
            seg, _ = route2(ctx, prev[a], prev[b], allowed, nodecost=nodecost, w_hop=W_HOP,
                            banned_edge={prev[a], prev[b]})
            if seg and len(seg) - 1 <= (b - a) + MAXEXTRA:
                return prev[:a] + seg + prev[b + 1:], f"ok m={m} capped={capped} w={w}"
    return None, None


def journey(ctx, s, t, pressed, prev):
    if prev is None:
        return baseline(ctx, s, t, pressed)
    p, how = repair(ctx, prev, pressed)
    if p:
        _log(how)
        return p
    _log(f"fallback {ctx.names[s]}->{ctx.names[t]} x={ctx.names[pressed[-1]]}")
    return baseline(ctx, s, t, pressed)
