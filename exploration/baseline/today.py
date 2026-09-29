"""Today's app: the shipped find_journey, every press a `known` exclusion."""


def journey(ctx, s, t, pressed, prev):
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None
