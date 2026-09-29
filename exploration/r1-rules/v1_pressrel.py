"""Press-relative ceiling: no middle artist more famous than the least famous artist pressed so far
(minus MARGIN). Relaxed minimally when it disconnects."""
import os
from rules_common import setup_common, ceiling_journey
MARGIN = float(os.environ.get("R1_MARGIN", "0.0"))
def setup(ctx): setup_common(ctx)
def journey(ctx, s, t, pressed, prev):
    if not pressed:
        return ceiling_journey(ctx, s, t, pressed, 1.0)[0]
    c = min(ctx.pl[x] for x in pressed) - MARGIN
    return ceiling_journey(ctx, s, t, pressed, c)[0]
