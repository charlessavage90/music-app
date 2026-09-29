"""Each press steers the journey through less famous artists who share many of their neighbours, so it digs steadily while each step still sounds like the last.

EXPLORATORY (r2-nsim finalist A). Press 0 = today's router. After a press: similarity is scored
fame-neutrally (each link against the weaker artist's best link) plus shared-neighbour overlap;
a journey-shaped fame ceiling (artists near either endpoint may stay as famous as it, 20 points
less per hop inward) and a soft pull toward a press target that falls 8 points per press from the
pressed artist's fame, never below half the less famous endpoint; a pull toward similar,
less famous stand-ins for the pressed artist; junk at the very bottom of the scale is charged, and so are links whose two artists share almost no
neighbours.
Settings are baked in; see r2nsim_core.py for the price formula.
"""
from r2nsim_core import Router

SETTINGS = dict(A_NSIM=3.0, A_JAC=3.0, J0=0.15, HOP=0.3, BETA=4.0, GAMMA=6.0, LOWF=0.6,
                JUNKP=0.05, JUNK=2.0, RPL=0.8, G=0.2, AH=0.005, STEP=0.08, FLOOR=0.1, CF=0.5, LMAX=11,
                LOWJ=0.05, LOWJPEN=1.5)
_KEY = "_r2nsim_dig_overlap"


def setup(ctx):
    if getattr(ctx, _KEY, None) is None:
        setattr(ctx, _KEY, Router(ctx, **SETTINGS))


def journey(ctx, s, t, pressed, prev):
    setup(ctx)
    return getattr(ctx, _KEY).journey(s, t, list(pressed), prev)
