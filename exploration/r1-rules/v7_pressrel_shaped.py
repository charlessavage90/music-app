"""Press-relative ceiling + journey-shaped loosening near the endpoints (v6 router).
Centre ceiling c: after each press, (1-c) = MULT * (1 - c_prev_or_pressed_fame), compounding,
starting from the fame of the first artist pressed. So pressing a 99.8 artist allows <=99.4,
then <=98.2, 94.6, 83.8 ... (MULT=3). Endpoint neighbourhoods may still reach endpoint fame."""
import os
import v6_layered as L
MULT = float(os.environ.get("R1_MULT", "3"))
def setup(ctx): L.setup(ctx)
def journey(ctx, s, t, pressed, prev):
    c = 1.0
    for x in pressed:
        c = min(c, ctx.pl[x])
        c = max(0.0, 1.0 - MULT * (1.0 - c))
    while True:
        p = L.route(ctx, s, t, pressed, c)
        if p is not None and len(p) == 2:
            p = L.route(ctx, s, t, pressed, c, forbidden=True) or p
        if p is not None and len(p) > 2:
            return p
        if c >= 1.0:   # still blocked: drop the similarity rule, then give up
            p = L.route(ctx, s, t, pressed, 1.0, minsim=0.0)
            if p is not None and len(p) == 2:
                p = L.route(ctx, s, t, pressed, 1.0, forbidden=True, minsim=0.0) or p
            return p
        c = min(1.0, c + 0.05)
