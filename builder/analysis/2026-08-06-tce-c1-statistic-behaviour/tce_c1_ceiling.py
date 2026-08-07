"""Supplement to tce_c1_behaviour.py: the CEILING of TCE-C1 (largest census median of
Delta_R attainable by ANY placement of thin artists, i.e. odds ratio -> infinity and
every reference artist affected), the breakdown fraction f* at which a concentrated
effect first moves the median past +0.10, and the null behaviour of the two proposed
supplementary statistics under concentration.

Same pure-arithmetic scope as its sibling: no archive, no artifact, no dump.
"""

from math import comb
from collections import defaultdict

TOP = 10
L_MIX = list(range(30, 101))


def binom_pmf(n, p):
    return [comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n + 1)]


def fnch_pmf(L, T, n, psi):
    lo, hi = max(0, n - (L - T)), min(n, T)
    w = {x: comb(T, x) * comb(L - T, n - x) * (psi**x) for x in range(lo, hi + 1)}
    tot = sum(w.values())
    return {x: v / tot for x, v in w.items()}


def delta_dist(L, b, psi=1.0):
    rest = L - TOP
    out = defaultdict(float)
    for T, pT in enumerate(binom_pmf(L, b)):
        if pT < 1e-18:
            continue
        for x, px in fnch_pmf(L, T, TOP, psi).items():
            out[round(x / TOP - (T - x) / rest, 12)] += pT * px
    return dict(out)


def mix(ds, ws=None):
    ws = ws or [1.0 / len(ds)] * len(ds)
    out = defaultdict(float)
    for d, w in zip(ds, ws):
        for k, v in d.items():
            out[k] += w * v
    return dict(out)


def quantile(d, q):
    c = 0.0
    for v in sorted(d):
        c += d[v]
        if c >= q - 1e-12:
            return v
    return max(d)


def mean(d):
    return sum(v * p for v, p in d.items())


print("=" * 96)
print("CEILING: the largest value TCE-C1 can take, for a given b, under ANY placement")
print("(odds ratio -> inf, every reference artist affected). L ~ Uniform{30..100}.")
print("=" * 96)
print(f"{'b':>7} {'P(T=0)':>8} {'max median':>11} {'max mean':>9} {'null median':>12} {'reachable +0.10?':>17}")
for b in [0.002, 0.005, 0.0069, 0.008, 0.010, 0.012, 0.0138, 0.015, 0.018, 0.020,
          0.0228, 0.025, 0.030, 0.040, 0.050, 0.080, 0.100]:
    dmax = mix([delta_dist(L, b, 1e9) for L in L_MIX])
    dnull = mix([delta_dist(L, b, 1.0) for L in L_MIX])
    pT0 = sum((1 - b) ** L for L in L_MIX) / len(L_MIX)
    mm = quantile(dmax, 0.5)
    print(
        f"{b:>7.4f} {pT0:>8.3f} {mm:>11.4f} {mean(dmax):>9.4f} {quantile(dnull,0.5):>12.4f} "
        f"{('YES' if mm >= 0.10 else 'NO -- statistic cannot reach the band'):>17}"
    )

print()
print("=" * 96)
print("BREAKDOWN: smallest fraction f of the census that must carry the effect for the")
print("census median to reach +0.10, with the affected artists MAXIMALLY enriched.")
print("=" * 96)
print(f"{'b':>7} {'f* for median>=+0.10':>21} {'f* for median>=+0.05':>21} {'f* for MEAN(Delta)>=+0.10':>26}")
FG = [i / 200 for i in range(201)]
for b in [0.01, 0.02, 0.03, 0.04, 0.05, 0.08, 0.10, 0.15, 0.247]:
    dn, dx = delta_dist_n, delta_dist_x = (
        mix([delta_dist(L, b, 1.0) for L in L_MIX]),
        mix([delta_dist(L, b, 1e9) for L in L_MIX]),
    )
    f10 = f05 = fmean = None
    for f in FG:
        d = mix([dn, dx], [1 - f, f])
        m = quantile(d, 0.5)
        if f05 is None and m >= 0.05 - 1e-12:
            f05 = f
        if f10 is None and m >= 0.10 - 1e-12:
            f10 = f
        if fmean is None and mean(d) >= 0.10 - 1e-12:
            fmean = f
    print(f"{b:>7.3f} {str(f10):>21} {str(f05):>21} {str(fmean):>26}")

print()
print("=" * 96)
print("SUPPLEMENTARY STATISTICS under concentration: null value, and value at fraction f")
print("=" * 96)


def midp_dist(L, b, psi=1.0):
    out = defaultdict(float)
    for T, pT in enumerate(binom_pmf(L, b)):
        if pT < 1e-18:
            continue
        null = fnch_pmf(L, T, TOP, 1.0)
        obs = fnch_pmf(L, T, TOP, psi)
        ks = sorted(null)
        for x, px in obs.items():
            out[round(sum(null[k] for k in ks if k < x) + 0.5 * null[x], 12)] += pT * px
    return dict(out)


for b in [0.01, 0.03, 0.05]:
    dn = mix([midp_dist(L, b, 1.0) for L in L_MIX])
    dx = mix([midp_dist(L, b, 1e9) for L in L_MIX])
    ddn = mix([delta_dist(L, b, 1.0) for L in L_MIX])
    ddx = mix([delta_dist(L, b, 1e9) for L in L_MIX])
    tail_null = sum(p for v, p in dn.items() if v >= 0.95 - 1e-12)
    sd0 = sum(p * (v - 0.5) ** 2 for v, p in dn.items()) ** 0.5
    print(f"\n  b = {b}   null mean mid-p = {mean(dn):.6f}   null sd = {sd0:.4f}   "
          f"null P(mid-p>=0.95) = {tail_null:.4f}")
    print(f"    {'f':>6} {'TCE-C1 median':>14} {'mean Delta':>11} {'mean mid-p':>11} "
          f"{'tail-share':>11} {'tail ratio':>11}")
    for f in [0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0]:
        dmid = mix([dn, dx], [1 - f, f])
        ddel = mix([ddn, ddx], [1 - f, f])
        ts = sum(p for v, p in dmid.items() if v >= 0.95 - 1e-12)
        print(f"    {f:>6.2f} {quantile(ddel,0.5):>+14.4f} {mean(ddel):>+11.4f} "
              f"{mean(dmid):>11.5f} {ts:>11.4f} "
              f"{(ts/tail_null if tail_null else float('nan')):>11.2f}")

print()
print("Algebraic check: Delta_R >= 0.10  <=>  X >= E_null[X] + (1 - 10/L)")
for L in (30, 50, 100):
    for T in (0, 3, 5, 10):
        need = 1 - TOP / L + TOP * T / L
        import math
        xmin = math.ceil(need - 1e-12)
        ok = all(
            ((x / TOP - (T - x) / (L - TOP)) >= 0.10 - 1e-12) == (x >= xmin)
            for x in range(0, min(TOP, T) + 1)
        )
        print(f"  L={L:>3} T={T:>2}: E_null[X]={TOP*T/L:5.2f}  need X >= {xmin}  verified={ok}")
