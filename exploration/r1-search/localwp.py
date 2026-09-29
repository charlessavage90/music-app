"""r1-search 'localwp': Dig deeper replaces the pressed artist p IN PLACE with an obscure waypoint.

Press 0 = today's router. Press k on p (between L and R in the previous journey):
  c_k = max(FLOOR, min(fame A, fame B) - STEP*k)
  w = argmin over unused, unpressed artists with fame <= c_k of  dL(w) + dR(w) + MU * dP(w)
      (d = similarity distance; dP = distance from the pressed artist, so w resembles p)
  new journey = prev[..L] + route(L -> w) + route(w -> R) + prev[R..]
  where each route uses similarity cost + BETA * max(0, fame - (c_k + SLACK)) and avoids the rest
  of the journey. The listener keeps everything they did not press.
EXPLORATORY."""
import os
import numpy as np
from scipy.sparse.csgraph import dijkstra
from common import setup_common, exclude, mat, rev_weights, walk, BIG

W_SIM = 3.0
W_HOP = float(os.environ.get("R1_HOP", "0.3"))
BASE = os.environ.get("R1_BASE", "sim")
STEP = float(os.environ.get("R1_STEP", "0.06"))
FLOOR = 0.15
MU = float(os.environ.get("R1_MU", "1.0"))
BETA = float(os.environ.get("R1_BETA", "4"))
SLACK = float(os.environ.get("R1_SLACK", "0.1"))


def setup(ctx):
    setup_common(ctx)
    r = ctx._r1
    r["base"] = W_SIM * (1 - (r["sc"] if BASE == "sim" else r["nsim"])) + W_HOP


def today(ctx, s, t, pressed):
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None


def journey(ctx, s, t, pressed, prev):
    k = len(pressed)
    if k == 0:
        return today(ctx, s, t, [])
    p = pressed[-1]
    if prev is None or p not in prev[1:-1]:
        return today(ctx, s, t, pressed)
    r = ctx._r1
    pc = r["pc"]
    i = prev.index(p)
    L, R = prev[i - 1], prev[i + 1]
    c = max(FLOOR, min(pc[s], pc[t]) - STEP * k)
    others = [v for v in prev if v not in (L, R)]
    avoid = list(set(pressed) | set(others))
    base = exclude(ctx, r["base"], avoid, keep=(L, R))
    M = mat(ctx, base)
    MT = mat(ctx, rev_weights(ctx, base))
    dL = dijkstra(M, indices=L)
    dR = dijkstra(MT, indices=R)
    # distance from p: p's own out-edges are intact (only edges INTO avoided nodes are priced BIG)
    dP = dijkstra(M, indices=p)
    score = dL + dR + MU * dP
    bad = (pc > c) | ~np.isfinite(score) | (score >= BIG)
    bad[avoid] = True
    bad[[L, R]] = True
    score = np.where(bad, np.inf, score)
    w = int(np.argmin(score))
    if not np.isfinite(score[w]):
        return today(ctx, s, t, pressed)
    pv = pc[r["nbr"]]
    soft = base + BETA * np.maximum(0.0, pv - (c + SLACK))
    ends = np.isin(r["nbr"], [L, R, w])
    soft[ends] = base[ends]
    _, p1 = dijkstra(mat(ctx, soft), indices=L, return_predecessors=True)
    _, p2 = dijkstra(mat(ctx, rev_weights(ctx, soft)), indices=R, return_predecessors=True)
    h1, h2 = walk(p1, L, w), walk(p2, R, w)
    if h1 is None or h2 is None:
        return today(ctx, s, t, pressed)
    mid = h1 + h2[::-1][1:]          # L ... w ... R
    path = prev[:i - 1] + mid + prev[i + 2:]
    out, last, j = [], {v: q for q, v in enumerate(path)}, 0
    while j < len(path):
        out.append(path[j])
        j = last[path[j]] + 1
    return out if len(out) > 2 else today(ctx, s, t, pressed)
