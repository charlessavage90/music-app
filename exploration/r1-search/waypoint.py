"""r1-search 'waypoint': route A -> w -> B through one obscure artist w chosen to sit in the middle.

Press 0 = today's router. Press k: fame target c_k = min(fame A, fame B) - STEP*k (floor FLOOR).
w = argmin over artists with fame <= c_k of  dA(w) + dB(w) + MU * dP(w)
  (d = similarity-only distance, 3*(1-sim)+0.02 per step; P = the artist just pressed).
Each half is then the cheapest route under similarity cost + BETA * max(0, fame - c_half)
where c_half = c_k + SLACK. Loops between halves are cut. EXPLORATORY."""
import os
import numpy as np
from scipy.sparse.csgraph import dijkstra
from common import setup_common, exclude, mat, rev_weights, walk, BIG

W_SIM = 3.0
W_HOP = float(os.environ.get("R1_HOP", "0.02"))
BASE = os.environ.get("R1_BASE", "sim")
STEP = float(os.environ.get("R1_STEP", "0.06"))
FLOOR = float(os.environ.get("R1_FLOOR", "0.15"))
SCHED = os.environ.get("R1_SCHED", "abs")
DELTA = float(os.environ.get("R1_DELTA", "0.08"))
JUNK = float(os.environ.get("R1_JUNK", "0"))  # artists below this fame are never used (data-quality guard)
MU = float(os.environ.get("R1_MU", "0.5"))
BETA = float(os.environ.get("R1_BETA", "4"))
SLACK = float(os.environ.get("R1_SLACK", "0.1"))
BAR = float(os.environ.get("R1_BAR", "0"))  # links weaker than this (fame-neutral similarity) are unusable


def setup(ctx):
    setup_common(ctx)
    r = ctx._r1
    r["base"] = W_SIM * (1 - (r["sc"] if BASE == "sim" else r["nsim"])) + W_HOP
    if BAR > 0:
        r["base"] = np.where(r["nsim"] < BAR, BIG, r["base"])


def today(ctx, s, t, pressed):
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None


def journey(ctx, s, t, pressed, prev):
    k = len(pressed)
    if k == 0:
        return today(ctx, s, t, [])
    r = ctx._r1
    pc = r["pc"]
    if SCHED == "rel" and prev is not None and len(prev) > 2:
        # relative: aim DELTA below the median fame of the journey just rejected
        c = max(FLOOR, float(np.median([pc[v] for v in prev[1:-1]])) - DELTA)
    else:
        c = max(FLOOR, min(pc[s], pc[t]) - STEP * k)
    base = exclude(ctx, r["base"], pressed, keep=(s, t))
    M = mat(ctx, base)
    MT = mat(ctx, rev_weights(ctx, base))
    dA = dijkstra(M, indices=s)
    dB = dijkstra(MT, indices=t)
    dP = dijkstra(M, indices=pressed[-1])  # from the pressed artist (its own in-edges are BIG)
    score = dA + dB + MU * dP
    bad = (pc > c) | ~np.isfinite(score) | (score >= BIG)
    bad[[s, t]] = True
    bad |= pc < JUNK
    bad[list(pressed)] = True
    score = np.where(bad, np.inf, score)
    w = int(np.argmin(score))
    if not np.isfinite(score[w]):
        return today(ctx, s, t, pressed)
    ch = c + SLACK
    pv = pc[r["nbr"]]
    soft = base + BETA * np.maximum(0.0, pv - ch)
    ends = np.isin(r["nbr"], [s, t, w])
    soft[ends] = base[ends]
    if JUNK > 0:
        soft[(pv < JUNK) & ~ends] = BIG
    Ms = mat(ctx, soft)
    _, p1 = dijkstra(Ms, indices=s, return_predecessors=True)
    _, p2 = dijkstra(mat(ctx, rev_weights(ctx, soft)), indices=t, return_predecessors=True)
    h1 = walk(p1, s, w)
    h2 = walk(p2, t, w)
    if h1 is None or h2 is None:
        return today(ctx, s, t, pressed)
    h2 = h2[::-1]  # w ... t
    path = h1 + h2[1:]
    # cut loops: keep the first occurrence, jump to the last occurrence
    out, seen = [], {}
    i = 0
    last = {v: j for j, v in enumerate(path)}
    while i < len(path):
        v = path[i]
        out.append(v)
        i = last[v] + 1
    if len(out) <= 2:
        return today(ctx, s, t, pressed)
    return out
