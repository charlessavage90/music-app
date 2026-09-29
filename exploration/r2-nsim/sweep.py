"""EXPLORATORY sweep shim: Router with overrides from env R2P (JSON)."""
import json, os
from r2nsim_core import Router
P = json.loads(os.environ.get("R2P", "{}"))
def setup(ctx):
    ctx._r2_sweep = Router(ctx, **P)
def journey(ctx, s, t, pressed, prev):
    return ctx._r2_sweep.journey(s, t, list(pressed), prev)
