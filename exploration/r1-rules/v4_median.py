"""Quantile ceiling: after each press, ceiling = median fame of the previous journey's middle
artists (cumulative min)."""
import statistics
from rules_common import setup_common, ceiling_journey
def setup(ctx):
    setup_common(ctx); ctx._r1_c = {}
def journey(ctx, s, t, pressed, prev):
    key = (s, t)
    if not pressed:
        ctx._r1_c[key] = 1.0
        return ceiling_journey(ctx, s, t, pressed, 1.0)[0]
    mids = [ctx.pl[v] for v in prev[1:-1]]
    c = min(ctx._r1_c.get(key, 1.0), statistics.median(mids)) if mids else ctx._r1_c.get(key, 1.0)
    p, used = ceiling_journey(ctx, s, t, pressed, c)
    ctx._r1_c[key] = c
    return p
