"""r1-search 'splice': Dig deeper as LOCAL REPAIR of the journey, not a reroute.

Press 0 = today's router. On a press of artist p (between L and R in the previous journey), search
all 1- and 2-artist bridges L -> w1 [-> w2] -> R through the map, every bridge artist less famous
than p, unused, unpressed, and score
    sum over bridge steps of (1 - similarity)  +  LAM * sum of bridge fame pctl
    - MU * (similarity of w to p, if they are neighbours)      [the replacement resembles p]
Every bridge step must have similarity >= BAR. The rest of the journey is kept, so pressing never
throws away the parts the listener did not object to. Fallback: today's router.
EXPLORATORY."""
import os

LAM = float(os.environ.get("R1_LAM", "1.5"))
MU = float(os.environ.get("R1_MU", "0.5"))
BAR = float(os.environ.get("R1_BAR", "0.35"))
TWO = float(os.environ.get("R1_TWO", "0.15"))   # extra charge for a 2-artist bridge
MARGIN = float(os.environ.get("R1_MARGIN", "0.0"))


def setup(ctx):
    ctx._nbrset = None


def nb(ctx, u):
    a, b = ctx.off[u], ctx.off[u + 1]
    return ctx.nbr[a:b], ctx.sc[a:b]


def bridge(ctx, L, R, p, banned, cap):
    pl = ctx.pl
    simp = dict(zip(*nb(ctx, p)))
    Rn, Rs = nb(ctx, R)
    toR = dict(zip(Rn, Rs))
    best = None
    Ln, Ls = nb(ctx, L)
    for w1, s1 in zip(Ln, Ls):
        if s1 < BAR or w1 in banned or pl[w1] >= cap:
            continue
        base = (1 - s1) + LAM * pl[w1] - MU * simp.get(w1, 0.0)
        sR = toR.get(w1)
        if sR is not None and sR >= BAR:
            sc = base + (1 - sR)
            if best is None or sc < best[0]:
                best = (sc, [w1])
        W2n, W2s = nb(ctx, w1)
        for w2, s2 in zip(W2n, W2s):
            if s2 < BAR or w2 in banned or w2 == w1 or pl[w2] >= cap:
                continue
            sR2 = toR.get(w2)
            if sR2 is None or sR2 < BAR:
                continue
            sc = base + (1 - s2) + (1 - sR2) + LAM * pl[w2] - MU * simp.get(w2, 0.0) + TWO
            if best is None or sc < best[0]:
                best = (sc, [w1, w2])
    return best


def step(ctx, prev, p, pressed):
    i = prev.index(p)
    L, R = prev[i - 1], prev[i + 1]
    banned = set(pressed) | set(prev)
    cap = ctx.pl[p] - MARGIN
    b = bridge(ctx, L, R, p, banned, cap)
    if b is None:
        return None
    return prev[:i] + b[1] + prev[i + 1:]


def today(ctx, s, t, pressed):
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None


def journey(ctx, s, t, pressed, prev):
    if not pressed:
        return today(ctx, s, t, [])
    p = pressed[-1]
    if prev is None or p not in prev[1:-1]:
        return today(ctx, s, t, pressed)
    out = step(ctx, prev, p, pressed)
    return out if out is not None else today(ctx, s, t, pressed)
