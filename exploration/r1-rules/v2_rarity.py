"""Rarity-multiplying ceiling: after each press the allowed 'top share' shrinks... inverted:
the ceiling c satisfies (1-c) = MULT * (1 - fame of least famous pressed artist). Cumulative."""
import os
from rules_common import setup_common, ceiling_journey
MULT = float(os.environ.get("R1_MULT", "3"))
def setup(ctx): setup_common(ctx)
def journey(ctx, s, t, pressed, prev):
    if not pressed:
        return ceiling_journey(ctx, s, t, pressed, 1.0)[0]
    c = 1.0
    for x in pressed:          # compound: each press multiplies the rarity requirement
        c = min(c, ctx.pl[x])
        c = 1.0 - MULT * (1.0 - c)
    return ceiling_journey(ctx, s, t, pressed, max(c, 0.0))[0]
