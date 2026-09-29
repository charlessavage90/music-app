"""EXPLORATORY. Parameterised edge-cost variant; params from env R1 (JSON).

edge cost = today_static + m*(reform - today_static) + (w_climb0 + w_climb*k)*max(0, fame_v - fame_u)
            with m = clip(mix0 + mix_per*k, 0, 1)
reform    = w_rank*(log1p(rank_uv)+log1p(rank_vu))/2   (mutual rank; 0 when each is the other's #1)
          + w_sim*(1-sim**sim_pow) + w_lift*mean_sim_v  (PMI-ish: hubs everyone is ~1.0 to pay more)
          + w_jump*|dpop_raw| + w_hop
node cost = today's floor + ramp (optional) + (w_deg + w_deg_k*k)*log(deg_v) + w_fame_k*k*fame_v
"""
import json
import os
from array import array

import numpy as np

import engine

P = dict(mix0=1.0, mix_per=0.0, w_rank=0.0, w_sim=3.0, w_jump=1.0, w_hop=0.02, sim_pow=1.0,
         w_lift=0.0, w_climb=0.0, w_climb0=0.0, w_desc=0.0, w_deg=0.0, w_deg_k=0.0,
         w_fame_k=0.0, fame_thr=0.0, thr_per=0.0, thr_min=0.5, keep_floor=1, keep_ramp=1)
P.update(json.loads(os.environ.get("R1", "{}")))


def setup(ctx):
    E = engine.prep(ctx)
    cfg = ctx.cfg
    src, nbr = E["src"], E["nbr"]
    today = engine.today_static(E, cfg)
    ref = (P["w_rank"] * (np.log1p(E["rank"]) + np.log1p(E["rank_rev"])) / 2
           + P["w_sim"] * (1 - E["sc"] ** P["sim_pow"])
           + P["w_lift"] * E["mean_sim"][nbr]
           + P["w_jump"] * np.abs(E["pop"][src] - E["pop"][nbr]) + P["w_hop"])
    up = np.maximum(0.0, E["fame"][nbr] - E["fame"][src])
    ctx.A = array("d", (today + P["w_climb0"] * up).tolist())
    ctx.D = array("d", (ref - today).tolist())
    ctx.C = array("d", (P["w_climb"] * up).tolist())
    ctx.logdeg = np.log(np.maximum(E["deg"], 1))


def journey(ctx, s, t, pressed, prev):
    E = ctx.E
    k = len(pressed)
    cfg = ctx.cfg
    base = min(E["pop"][s], E["pop"][t])
    floor = max(0.0, base - cfg.floor_relax_known * k)
    nc = np.zeros(E["n"])
    if P["keep_floor"]:
        nc += cfg.w_floor * np.maximum(0.0, floor - E["pop"])
    if P["keep_ramp"]:
        nc += cfg.w_known_ramp_fame_pctl * k * E["fame"]
    thr = max(P["thr_min"], P["fame_thr"] - P["thr_per"] * k) if P["thr_per"] else P["fame_thr"]
    # thresholded fame toll: only artists above the (optionally falling) threshold pay, scaled 0..1
    nc += (P["w_deg"] + P["w_deg_k"] * k) * ctx.logdeg + P["w_fame_k"] * k * np.maximum(0.0, E["fame"] - thr) / (1 - thr)
    m = min(1.0, max(0.0, P["mix0"] + P["mix_per"] * k))
    return engine.journey_with(E, s, t, (ctx.A, ctx.D, m, ctx.C, k), nc.tolist(), pressed)
