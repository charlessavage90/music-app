"""Fast fixed schedule of fame ceilings by press count."""
import os
SCHED = [float(x) for x in os.environ.get("R1_SCHED", "1.0,0.95,0.90,0.80,0.70,0.60,0.50,0.45,0.40,0.35,0.30").split(",")]
from rules_common import setup_common, ceiling_journey
def setup(ctx): setup_common(ctx)
def journey(ctx, s, t, pressed, prev):
    c = SCHED[min(len(pressed), len(SCHED) - 1)]
    return ceiling_journey(ctx, s, t, pressed, c)[0]
