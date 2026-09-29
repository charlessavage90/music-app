"""Working variant for r2-repair (params via env R2 as JSON; finalists bake them in).
Press = local repair of the stretch around the pressed artist, never a regeneration:
  - length budget: journey never exceeds (press-0 length + LEN_EXTRA);
  - swap-first: try replacing the pressed artist in place (same length) before longer detours;
  - priced instead of hard margin: a hard cap only MARGIN below the pressed artist, then a soft
    band charge (above px-T_OFF costs W_F per 10 pts; below px-D_OFF costs W_D per 10 pts);
  - monotone: no slot of the window may come back more famous than what it replaces;
  - optional drift: up to DRIFT in-place swaps elsewhere that only make a slot less famous.
"""
import json
import os

from lib2 import route_h, baseline

P = dict(MARGIN=0.03, T_OFF=0.10, D_OFF=0.35, W_F=0.5, W_D=1.0, W_X=0.0, W_HOP=0.5,
         LEN_EXTRA=3, EXTRA_W=2, SWAP_MIN=0.6, SEG_MIN=0.0, W_PULL=3.0, SHORT_MIN=0.6, MAXPOPS=8000, EDGE=1, LEN_MIN=10,
         DRIFT=0, DRIFT_MARGIN=0.05, DRIFT_DROP=0.25, DRIFT_MINSIM=0.6)
P.update(json.loads(os.environ.get("R2", "{}")))

_L0 = {}
_LOG = os.environ.get("R2LOG")


def _log(msg):
    if _LOG:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", os.path.basename(_LOG)), "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def _weak(ctx, seg):
    return min(ctx.sim(u, v) for u, v in zip(seg, seg[1:]))


def _l0(ctx, s, t):
    if (s, t) not in _L0:
        p = baseline(ctx, s, t, [])
        _L0[(s, t)] = len(p) if p else 8
    return _L0[(s, t)]


def repair(ctx, prev, pressed, lmax):
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    pl = ctx.pl
    px = pl[x]
    n = len(prev)
    room = max(0, lmax - n)
    simx = {}
    if P["W_X"]:
        nb, sc = ctx.row(x)
        simx = dict(zip(nb, sc))
    tgt, lo = px - P["T_OFF"], px - P["D_OFF"]

    def band(v):
        c = P["W_F"] * max(0.0, pl[v] - tgt) / 0.1 + P["W_D"] * max(0.0, lo - pl[v]) / 0.1
        if simx:
            c += P["W_X"] * (1.0 - simx.get(v, 0.0))
        return c

    def pull(v):
        return P["W_PULL"] * pl[v] + P["W_D"] * max(0.0, lo - pl[v]) / 0.1

    def fit(p):
        """Shortcut pass: drop slots whose neighbours link directly (sim >= SHORT_MIN), most
        famous first, until the journey fits the length budget. None if it cannot."""
        p = list(p)
        lim = max(lmax, n)          # over budget (after a last resort) may never grow further
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

    stages = [(P["MARGIN"], band, "band", (1, 2, 3)), (1e-9, pull, "pull0", (1, 2, 3, 4))]
    edge = i == 1 or i == n - 2
    if edge and P["EDGE"]:
        stages.append((P["MARGIN"], pull, "edge", (1, 2, 3)))
    for m, nc, tag, ws in stages:
        for w in ws:
            a, b = max(0, i - w), min(n - 1, i + w)
            if w > 1 and (a, b) == (max(0, i - w + 1), min(n - 1, i + w - 1)):
                continue
            removed = [r for r in prev[a + 1:b] if r != x]
            cap = min([px - m] + [pl[r] for r in removed])
            keep = set(prev[:a + 1]) | set(prev[b:])
            relax1 = tag == "edge"
            allowed = lambda v, h: v not in ps and v not in keep and (pl[v] <= cap or (relax1 and h == 1))
            base_h = b - a
            # the edge stage routes FROM the endpoint next to x, so hop 1 is the endpoint's neighbour
            src, dst = (prev[a], prev[b]) if (not relax1 or i == 1) else (prev[b], prev[a])
            tries = [base_h, base_h + P["EXTRA_W"]]
            for hmax in tries:
                seg, _ = route_h(ctx, src, dst, allowed, nodecost=nc, max_hops=hmax,
                                 w_hop=P["W_HOP"], banned_edge={prev[a], prev[b]}, max_pops=P["MAXPOPS"])
                if not seg:
                    continue
                if src != prev[a]:
                    seg = seg[::-1]
                wk = _weak(ctx, seg)
                if w == 1 and hmax == base_h and wk < P["SWAP_MIN"]:
                    continue      # weak in-place swap: let the longer detour compete
                if wk < P["SEG_MIN"]:
                    continue
                out = fit(prev[:a] + seg + prev[b + 1:])
                if out:
                    return out, f"{tag} w={w} h={len(seg)-1}/{hmax}"
    return None, None


def uncapped(ctx, prev, pressed):
    """Last resort: any fame, pulled toward the least famous, windows 1..3, no hop limit beyond +3."""
    x = pressed[-1]
    i = prev.index(x)
    ps = set(pressed)
    pl = ctx.pl
    n = len(prev)
    for w in (1, 2, 3):
        a, b = max(0, i - w), min(n - 1, i + w)
        keep = set(prev[:a + 1]) | set(prev[b:])
        seg, _ = route_h(ctx, prev[a], prev[b], lambda v, h: v not in ps and v not in keep,
                         nodecost=lambda v: P["W_PULL"] * pl[v] + P["W_D"] * max(0.0, pl[x] - P["D_OFF"] - pl[v]) / 0.1, max_hops=b - a + 1,
                         w_hop=P["W_HOP"], banned_edge={prev[a], prev[b]}, max_pops=P["MAXPOPS"])
        if seg:
            return prev[:a] + seg + prev[b + 1:]
    return None


def drift(ctx, path, pressed):
    """Up to DRIFT in-place swaps that only make a slot less famous and don't weaken its links."""
    pl = ctx.pl
    ps = set(pressed)
    done = 0
    path = list(path)
    cands = sorted(range(1, len(path) - 1), key=lambda j: -pl[path[j]])
    for j in cands:
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
            if s2 < floor:
                continue
            if s1 + s2 > bs:
                best, bs = y, s1 + s2
        if best is not None:
            path[j] = best
            done += 1
    return path


def journey(ctx, s, t, pressed, prev):
    if prev is None:
        return baseline(ctx, s, t, pressed)
    lmax = max(_l0(ctx, s, t) + P["LEN_EXTRA"], P["LEN_MIN"])
    import time as _t
    t0 = _t.time()
    p, how = repair(ctx, prev, pressed, lmax)
    _log("\t".join([str(len(pressed)), str(how), f"{_t.time()-t0:.2f}",
                    f"{ctx.names[pressed[-1]]}({ctx.pl[pressed[-1]]*100:.0f})",
                    f"len={len(prev)}/{lmax}", f"pos={prev.index(pressed[-1])}"]))
    if not p:
        i = prev.index(pressed[-1])
        if 0 < i < len(prev) - 1 and ctx.sim(prev[i - 1], prev[i + 1]) > 0 and len(prev) > 3:
            p = prev[:i] + prev[i + 1:]
            _log("drop")
        else:
            p = uncapped(ctx, prev, pressed)
            _log("uncapped" if p else "RESET")
            if not p:
                return baseline(ctx, s, t, pressed)
    if P["DRIFT"]:
        p = drift(ctx, p, pressed)
    return p
