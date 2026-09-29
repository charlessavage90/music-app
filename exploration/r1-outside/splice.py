"""EXPLORATORY. 'Splice' — replace only the pressed artist, RP3beta-style.

Celma's long-tail navigation + RP3beta: among artists that bridge the pressed artist's two
neighbours in the journey (a -> w -> b), pick w maximising sim(a,w)*sim(w,b) / wdeg(w)^beta,
restricted to w less famous than the pressed artist. If no single bridge exists, try a two-artist
bridge (a -> w1 -> w2 -> b). If neither exists, fall back to today's router. The rest of the
journey is kept — so a press changes one stop, and that stop gets less famous.
"""
import router


def make(beta=1.0, two_hop=True, require_less_famous=True, gap=0.0):
    def setup(ctx):
        router.precompute(ctx)
        ctx.nset = [None] * ctx.n

    def nb(ctx, u):
        if ctx.nset[u] is None:
            a, b = ctx.off[u], ctx.off[u + 1]
            ctx.nset[u] = dict(zip(ctx.nbr[a:b], ctx.sc[a:b]))
        return ctx.nset[u]

    def journey(ctx, s, t, pressed, prev):
        if not pressed:
            return ctx.find_journey(ctx.store, s, t, [], ctx.cfg)[0]
        v = pressed[-1]
        if prev is None or v not in prev:
            return ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)[0]
        i = prev.index(v)
        a, b = prev[i - 1], prev[i + 1]
        banned = set(pressed) | set(prev)
        pl, wd = ctx.pl, ctx.wdeg
        cap = (pl[v] - gap) if require_less_famous else 2.0
        Na, Nb = nb(ctx, a), nb(ctx, b)
        best, bw = -1.0, None
        for w, sa in Na.items():
            if w in banned or pl[w] >= cap:
                continue
            sb = Nb.get(w)
            if sb is None:
                continue
            sc = sa * sb / (max(wd[w], 1.0) ** beta)
            if sc > best:
                best, bw = sc, [w]
        if bw is None and two_hop:
            for w1, sa in Na.items():
                if w1 in banned or pl[w1] >= cap:
                    continue
                N1 = nb(ctx, w1)
                for w2, sb in Nb.items():
                    if w2 in banned or w2 == w1 or pl[w2] >= cap:
                        continue
                    s12 = N1.get(w2)
                    if s12 is None:
                        continue
                    sc = (sa * s12 * sb) ** (2 / 3) / (max(wd[w1], 1.0) * max(wd[w2], 1.0)) ** (beta / 2)
                    if sc > best:
                        best, bw = sc, [w1, w2]
        if bw is None:
            ctx.fallbacks = getattr(ctx, "fallbacks", 0) + 1
            return ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)[0]
        return prev[:i] + bw + prev[i + 1:]

    return setup, journey
