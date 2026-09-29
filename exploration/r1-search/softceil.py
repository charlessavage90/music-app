"""Control for r1-search: similarity-only cost + soft fame ceiling that falls with presses.
No waypoint. Press 0 = today's router. EXPLORATORY."""
import os
import numpy as np
from common import setup_common, journey_from, exclude

W_SIM = 3.0
W_HOP = float(os.environ.get("R1_HOP", "0.02"))
BASE = os.environ.get("R1_BASE", "sim")
BETA = float(os.environ.get("R1_BETA", "10"))
STEP = float(os.environ.get("R1_STEP", "0.08"))
FLOOR = float(os.environ.get("R1_FLOOR", "0.15"))
SCHED = os.environ.get("R1_SCHED", "abs")
DELTA = float(os.environ.get("R1_DELTA", "0.08"))


def target(ctx, s, t, k):
    e = min(ctx.pl[s], ctx.pl[t])
    return max(FLOOR, e - STEP * k)


def setup(ctx):
    setup_common(ctx)
    r = ctx._r1
    r["base"] = W_SIM * (1 - (r["sc"] if BASE == "sim" else r["nsim"])) + W_HOP


def cost(ctx, c, t):
    r = ctx._r1
    pv = r["pc"][r["nbr"]]
    w = r["base"] + BETA * np.maximum(0.0, pv - c)
    w[r["nbr"] == t] = r["base"][r["nbr"] == t]
    return w


def journey(ctx, s, t, pressed, prev):
    k = len(pressed)
    if k == 0:
        res = ctx.find_journey(ctx.store, s, t, [], ctx.cfg)
        return res[0] if res else None
    if SCHED == "rel" and prev is not None and len(prev) > 2:
        c = max(FLOOR, float(np.median([ctx.pl[v] for v in prev[1:-1]])) - DELTA)
    else:
        c = target(ctx, s, t, k)
    w = exclude(ctx, cost(ctx, c, t), pressed, keep=(s, t))
    return journey_from(ctx, w, s, t)
