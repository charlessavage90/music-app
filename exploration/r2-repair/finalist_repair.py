"""Pressing Dig deeper keeps your journey and re-routes only the few cards around the artist you pressed, through similar but less famous artists, so the journey gets more obscure where you press without growing much.

EXPLORATORY (r2-repair finalist A, "local repair"). Self-contained: settings baked in, no env vars.
Interface: journey(ctx, s, t, pressed, prev) as in exploration/kit/qlook.py. Press 0 = today's router.
Press k = repair(journey(pressed[:-1]), pressed[-1]) -- the app replays the `known` list in order.
How a press works (x = pressed artist):
  1. "band": re-route a window of 1..4 cards either side of x. Every new card is at least 10 points
     less famous than x (the card next to an endpoint included); the router prefers cards 12+ points
     below x, pays for cards more than 35 points below (and never admits cards 50+ below), prefers
     x's own similar artists, and takes no step weaker than similarity 0.6.
  2. "reach" (x next to an endpoint): a famous endpoint's neighbours are often all famous, so that
     card may stay famous, but the 1..4 cards behind it must each come back 10 points less famous.
  3. "pull0"/"pull1": if nothing less famous fits, take the least famous similar option (famous-for-
     famous next to an exhausted endpoint), in the interior never more famous than x.
  4. last resorts: drop x if its neighbours link directly; else an uncapped windowed swap. Never
     a regeneration from scratch (a reset would undo every earlier press).
  Monotone: across a window the new cards' fames, sorted, may not exceed the old ones anywhere.
  Length budget: max(press-0 length + 3, 10); an over-long detour is paid for by dropping cards whose
  neighbours link directly. Routing: hop-bounded Dijkstra, typically < 0.1 s, worst ~2.5 s per press.
"""
import heapq


def route_h(ctx, s, t, allowed, nodecost=None, max_hops=4, w_sim=3.0, w_jump=1.0, w_hop=0.02,
            banned_edge=None, max_pops=40000, minsim=0.0, minsim_s=None, minsim_t=None):
    """Cheapest s->t path with at most max_hops hops; interior v must satisfy allowed(v, h) where h is
    the hop index at which v is entered (1-based). If allowed returns 2, v is admitted only as the
    last stop before t (it may expand to t and nothing else). Pareto pruning: a node popped with h hops is skipped
    if it was already popped with <= h hops (Dijkstra pops in cost order, so that label dominates).
    Returns (path, cost) or (None, None)."""
    pop = ctx.store.pop_raw
    off, nbr, sc = ctx.off, ctx.nbr, ctx.sc
    # lookahead: a node entered at hop max_hops-1 must touch t; at max_hops-2 it must be 2 steps away
    L1 = set(nbr[off[t]:off[t + 1]])
    L2 = set()
    if max_hops >= 3:
        for y in L1:
            L2.update(nbr[off[y]:off[y + 1]])
    best_h = {}                      # node -> min hops popped so far
    pq = [(0.0, 0, s, -1, False)]    # (cost, hops, node, parent label idx, last-only)
    labels = []                      # (node, parent label idx)
    pops = 0
    while pq:
        d, h, u, par, lastonly = heapq.heappop(pq)
        bh = best_h.get(u)
        if bh is not None and bh <= h:
            continue
        if not lastonly:
            best_h[u] = h
        labels.append((u, par))
        me = len(labels) - 1
        if u == t:
            p = []
            i = me
            while i != -1:
                p.append(labels[i][0])
                i = labels[i][1]
            return p[::-1], d
        pops += 1
        if pops > max_pops or h >= max_hops:
            continue
        pu = float(pop[u])
        h1 = h + 1
        last = h1 == max_hops
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            lo = False
            if v == t:
                pass
            else:
                if last or lastonly:
                    continue
                if h1 == max_hops - 1:
                    if v not in L1:
                        continue
                elif h1 == max_hops - 2 and v not in L2:
                    continue
                ok = allowed(v, h1)
                if not ok:
                    continue
                lo = ok == 2
            if banned_edge and u in banned_edge and v in banned_edge:
                continue
            ms = minsim
            if minsim_s is not None and u == s:
                ms = minsim_s
            elif minsim_t is not None and v == t:
                ms = minsim_t
            if sc[j] < ms:
                continue
            bv = best_h.get(v)
            if bv is not None and bv <= h1:
                continue
            c = w_sim * (1.0 - sc[j]) + w_jump * abs(pu - float(pop[v])) + w_hop
            if nodecost is not None and v != t:
                c += nodecost(v)
            heapq.heappush(pq, (d + c, h1, v, me, lo))
    return None, None


def baseline(ctx, s, t, pressed):
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None


P = dict(
    MARGIN=0.1,
    T_OFF=0.12,
    D_OFF=0.35,
    W_F=1.0,
    W_D=1.0,
    W_HOP=0.5,
    LEN_EXTRA=3,
    LEN_MIN=10,
    EXTRA_W=2,
    SWAP_MIN=0.6,
    W_PULL=3.0,
    SHORT_MIN=0.6,
    MAXPOPS=8000,
    W_X=1.0,
    EDGE_MINSIM=None,
    REACH=1,
    BAND_XEDGE=1,
    REACH_W=[2, 3, 4, 5],
    MINSIM=0.6,
    MINSIM_PULL=0.4,
    DIVE_MAX=0.5,
    WINDOWS=[1, 2, 3, 4, 99],
    FULL=0,
    PULL1=1,
    DRIFT=0,
    DRIFT_MARGIN=0.05,
    DRIFT_DROP=0.25,
    DRIFT_MINSIM=0.6,
)

_L0 = {}


def _weak(ctx, seg):
    return min(ctx.sim(u, v) for u, v in zip(seg, seg[1:]))


def _l0(ctx, s, t):
    if (s, t) not in _L0:
        p = baseline(ctx, s, t, [])
        _L0[(s, t)] = len(p) if p else 8
    return _L0[(s, t)]


def _dominated(new, old):
    new, old = sorted(new, reverse=True), sorted(old, reverse=True)
    for k, v in enumerate(new):
        if v > (old[k] if k < len(old) else old[0]) + 1e-9:
            return False
    return True


def repair(ctx, prev, pressed, lmax):
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    pl = ctx.pl
    px = pl[x]
    n = len(prev)
    tgt, lo = px - P["T_OFF"], px - P["D_OFF"]
    nbx, scx = ctx.row(x)
    simx = dict(zip(nbx, scx))
    wx = P["W_X"]

    def band(v):
        return (P["W_F"] * max(0.0, pl[v] - tgt) / 0.1 + P["W_D"] * max(0.0, lo - pl[v]) / 0.1
                + wx * (1.0 - simx.get(v, 0.0)))

    def pull(v):
        return (P["W_PULL"] * pl[v] + P["W_D"] * max(0.0, lo - pl[v]) / 0.1
                + wx * (1.0 - simx.get(v, 0.0)))

    def fit(p):
        p = list(p)
        lim = max(lmax, n)
        while len(p) > lim:
            best, bs = None, -1.0
            for j in range(1, len(p) - 1):
                sj = ctx.sim(p[j - 1], p[j + 1])
                if sj >= P["SHORT_MIN"] and sj + pl[p[j]] > bs:
                    best, bs = j, sj + pl[p[j]]
            if best is None:
                return None
            del p[best]
        return p

    seen = set()
    stages = [(P["MARGIN"], band, "band")]
    if P["REACH"] and (i == 1 or i == n - 2):
        stages.append((P["MARGIN"], pull, "reach"))   # endpoint slot may stay famous; dig the cards behind it
    stages.append((1e-9, pull, "pull0"))
    if P["PULL1"]:
        stages.append((1e-9, pull, "pull1"))   # no dominance: just below x, endpoint slot free
    for m, nc, tag in stages:
        for w in (P["WINDOWS"] if tag != "reach" else P["REACH_W"]):
            if w == 99 and not P["FULL"]:
                continue
            a, b = max(0, i - w), min(n - 1, i + w)
            if (a, b, tag) in seen:
                continue
            seen.add((a, b, tag))
            cap = px - m
            # band: x's slot must drop by the margin even next to an endpoint (BAND_XEDGE=1);
            # pull0: an exhausted endpoint slot takes any neighbour
            xcap = (cap if P["BAND_XEDGE"] else px - 1e-9) if tag == "band" else 1.01
            xedge = (i == 1 and a == 0) or (i == n - 2 and b == n - 1)
            old = [pl[r] for r in prev[a + 1:b] if r != x] + [xcap if xedge else cap]
            if tag == "reach":
                inner = [pl[r] - m for r in prev[a + 1:b] if r != x]
                if not inner or not xedge:
                    continue
                cap = max(inner)
                old = inner + [xcap]
            keep = set(prev[:a + 1]) | set(prev[b:])
            # the card next to an endpoint may stay as famous as its old occupant (x: just below x)
            cap_first = (pl[prev[1]] if prev[1] != x else xcap) if a == 0 else cap
            cap_last = (pl[prev[n - 2]] if prev[n - 2] != x else xcap) if b == n - 1 else cap

            def allowed(v, h, cap=cap, cap_first=cap_first, cap_last=cap_last, keep=keep):
                if v in ps or v in keep:
                    return 0
                f = pl[v]
                if f < px - P["DIVE_MAX"]:
                    return 0
                if f <= cap or (h == 1 and f <= cap_first):
                    return 1
                if f <= cap_last:
                    return 2
                return 0

            base_h = b - a
            hs = [base_h, base_h + P["EXTRA_W"]] if w != 99 else [lmax - 1]
            for hmax in hs:
                seg, _ = route_h(ctx, prev[a], prev[b], allowed, nodecost=nc, max_hops=hmax,
                                 w_hop=P["W_HOP"], banned_edge={prev[a], prev[b]}, max_pops=P["MAXPOPS"],
                                 minsim=P["MINSIM"] if tag == "band" else P["MINSIM_PULL"],
                                 minsim_s=P["EDGE_MINSIM"] if (a == 0 and i == 1) else None,
                                 minsim_t=P["EDGE_MINSIM"] if (b == n - 1 and i == n - 2) else None)
                if not seg:
                    continue
                if tag == "band" and w == 1 and hmax == base_h and _weak(ctx, seg) < P["SWAP_MIN"]:
                    continue
                if tag != "pull1" and not _dominated([pl[v] for v in seg[1:-1]], old):
                    continue
                out = fit(prev[:a] + seg + prev[b + 1:])
                if out:
                    return out, f"{tag} w={w} h={len(seg)-1}/{hmax}"
    return None, None


def uncapped(ctx, prev, pressed):
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    pl = ctx.pl
    n = len(prev)
    for w in (1, 2, 3):
        a, b = max(0, i - w), min(n - 1, i + w)
        keep = set(prev[:a + 1]) | set(prev[b:])
        seg, _ = route_h(ctx, prev[a], prev[b], lambda v, h: v not in ps and v not in keep,
                         nodecost=lambda v: P["W_PULL"] * pl[v] + P["W_D"] * max(0.0, pl[x] - P["D_OFF"] - pl[v]) / 0.1,
                         max_hops=b - a + 1, w_hop=P["W_HOP"], banned_edge={prev[a], prev[b]},
                         max_pops=P["MAXPOPS"])
        if seg:
            return prev[:a] + seg + prev[b + 1:]
    return None


def drift(ctx, path, pressed):
    pl = ctx.pl
    ps = set(pressed)
    done = 0
    path = list(path)
    for j in sorted(range(1, len(path) - 1), key=lambda j: -pl[path[j]]):
        if done >= P["DRIFT"]:
            break
        u, c, v = path[j - 1], path[j], path[j + 1]
        cur = min(ctx.sim(u, c), ctx.sim(c, v))
        floor = max(P["DRIFT_MINSIM"], cur - 0.05)
        onpath = set(path)
        nu, su = ctx.row(u)
        best, bs = None, -1
        for y, s1 in zip(nu, su):
            if y in ps or y in onpath or s1 < floor:
                continue
            if not (pl[c] - P["DRIFT_DROP"] <= pl[y] <= pl[c] - P["DRIFT_MARGIN"]):
                continue
            s2 = ctx.sim(y, v)
            if s2 >= floor and s1 + s2 > bs:
                best, bs = y, s1 + s2
        if best is not None:
            path[j] = best
            done += 1
    return path


def journey(ctx, s, t, pressed, prev):
    if prev is None:
        p = baseline(ctx, s, t, pressed)
        if p and not pressed:
            _L0[(s, t)] = len(p)
        return p
    lmax = max(_l0(ctx, s, t) + P["LEN_EXTRA"], P["LEN_MIN"])
    p, how = repair(ctx, prev, pressed, lmax)
    i = prev.index(pressed[-1])
    if not p:
        if 0 < i < len(prev) - 1 and ctx.sim(prev[i - 1], prev[i + 1]) > 0 and len(prev) > 3:
            p, how = prev[:i] + prev[i + 1:], "drop"
        else:
            p = uncapped(ctx, prev, pressed)
            how = "uncapped" if p else "RESET"
            if not p:
                p = baseline(ctx, s, t, pressed)
    if P["DRIFT"]:
        p = drift(ctx, p, pressed)
    return p
