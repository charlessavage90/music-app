"""v7 local repair (v3a semantics, fast, never resetting). A press keeps the journey and re-routes
the smallest window around the pressed artist x (pred..succ, then +-2, +-3) through artists at
least MARGIN percentile below x; a repair may add at most MAXEXTRA artists. Optional pulls:
W_X toward artists similar to x (REQ-27 'highly similar'), W_DIVE against diving more than DIVE
below x in one press. Escalation: halve margin, zero margin, then lift the cap (fame pull only);
today's router only if the window cannot be re-routed at all."""
import os
from lib import route2, baseline

MARGIN = float(os.environ.get("R1_MARGIN", "0.10"))
W_HOP = float(os.environ.get("R1_WHOP", "0.5"))
MAXEXTRA = int(os.environ.get("R1_MAXEXTRA", "2"))
W_X = float(os.environ.get("R1_WX", "0.0"))
W_DIVE = float(os.environ.get("R1_WDIVE", "0.0"))
DIVE = float(os.environ.get("R1_DIVE", "0.3"))
W_FAME_FREE = 1.0
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
    floor = px - DIVE

    for m, capped in ((MARGIN, True), (MARGIN / 2, True), (0.0, True), (MARGIN, False)):
        cap = px - m if capped else 1.01
        wf = 0.0 if capped else W_FAME_FREE

        def nodecost(v):
            c = wf * pl[v]
            if W_X:
                c += W_X * (1.0 - simx.get(v, 0.0))
            if W_DIVE and pl[v] < floor:
                c += W_DIVE * (floor - pl[v])
            return c

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
