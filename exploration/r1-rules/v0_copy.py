"""Sanity: my copy of the shipped router, no ceiling. Must reproduce baseline/today."""
from rules_common import setup_common, find_journey
def setup(ctx): setup_common(ctx)
def journey(ctx, s, t, pressed, prev):
    return find_journey(ctx, s, t, pressed, 1.0)
