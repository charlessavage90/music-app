"""Behaviour of the TCE-C1 statistic (median of Delta_R) as a function of the thin
base rate b. PURE ARITHMETIC over the statistic's definition -- reads no archive, no
artifact, no MusicBrainz dump, and computes no actual base rate. It answers "what can
this statistic do", never "what does the data say".

Delta_R = p_top - p_rest
  p_top  = (# thin in ranks 1..10) / 10
  p_rest = (# thin in ranks 11..L) / (L - 10)

Null model: an artist's list of length L contains T ~ Binomial(L, b) thin neighbours,
placed uniformly at random among the L ranks, so X = (# thin in top 10) | T is
Hypergeometric(L, T, 10).

Enrichment model: T's marginal is unchanged (the same artists are thin); only the
PLACEMENT is biased, by Fisher's noncentral hypergeometric with odds ratio psi. psi=1
is the null. This is the within-list framing the pre-registration's SS0 insists on.

Run: cd builder && UV_LINK_MODE=copy uv run python analysis/2026-08-06-tce-c1-statistic-behaviour/tce_c1_behaviour.py
(stdlib only; any python3 works)
"""

from math import comb, exp
from collections import defaultdict

TOP = 10
L_GRID = [30, 50, 100]
L_MIX = list(range(30, 101))  # uniform mixture, used where the real L distribution is unknown
B_GRID = [0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.247]


# ---------------------------------------------------------------- distributions
def binom_pmf(n, p):
    return [comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n + 1)]


def fnch_pmf(L, T, n, psi):
    """Fisher's noncentral hypergeometric: n draws from L, T successes, odds ratio psi.
    psi = 1 -> central hypergeometric. psi = inf handled by caller."""
    lo, hi = max(0, n - (L - T)), min(n, T)
    w = {}
    tot = 0.0
    for x in range(lo, hi + 1):
        v = comb(T, x) * comb(L - T, n - x) * (psi**x)
        w[x] = v
        tot += v
    return {x: v / tot for x, v in w.items()}


def delta_dist(L, b, psi=1.0):
    """Exact pmf of Delta_R over the joint (T, X). Returns {delta: prob}."""
    rest = L - TOP
    out = defaultdict(float)
    for T, pT in enumerate(binom_pmf(L, b)):
        if pT < 1e-18:
            continue
        for x, px in fnch_pmf(L, T, TOP, psi).items():
            out[round(x / TOP - (T - x) / rest, 12)] += pT * px
    return dict(out)


def mix(dists, weights=None):
    n = len(dists)
    weights = weights or [1.0 / n] * n
    out = defaultdict(float)
    for d, w in zip(dists, weights):
        for k, v in d.items():
            out[k] += w * v
    return dict(out)


# ---------------------------------------------------------------- summaries
def quantile(d, q):
    """Lower quantile of a discrete distribution: smallest v with CDF(v) >= q."""
    c = 0.0
    for v in sorted(d):
        c += d[v]
        if c >= q - 1e-12:
            return v
    return max(d)


def mean(d):
    return sum(v * p for v, p in d.items())


def tail(d, thr):
    return sum(p for v, p in d.items() if v >= thr - 1e-12)


def band(m):
    if m >= 0.10:
        return "enriched"
    if m >= 0.05:
        return "INDETERMINATE"
    if m > -0.05:
        return "null"
    return "depleted"


# ---------------------------------------------------------------- (a) null behaviour
print("=" * 100)
print("(a) NULL DISTRIBUTION OF Delta_R  (psi = 1, no enrichment)")
print("=" * 100)
print(
    f"{'b':>6} {'L':>6} {'mean':>9} {'MEDIAN':>9} {'band':>14} "
    f"{'P(D=0)':>8} {'P(D>=.05)':>10} {'P(D>=.10)':>10} {'q75':>7} {'q90':>7} {'q95':>7}"
)
for b in B_GRID:
    for L in L_GRID:
        d = delta_dist(L, b)
        print(
            f"{b:>6.3f} {L:>6} {mean(d):>9.5f} {quantile(d,0.5):>9.4f} {band(quantile(d,0.5)):>14} "
            f"{d.get(0.0,0.0):>8.3f} {tail(d,0.05):>10.4f} {tail(d,0.10):>10.4f} "
            f"{quantile(d,0.75):>7.3f} {quantile(d,0.90):>7.3f} {quantile(d,0.95):>7.3f}"
        )
    dm = mix([delta_dist(L, b) for L in L_MIX])
    print(
        f"{b:>6.3f} {'MIX':>6} {mean(dm):>9.5f} {quantile(dm,0.5):>9.4f} {band(quantile(dm,0.5)):>14} "
        f"{dm.get(0.0,0.0):>8.3f} {tail(dm,0.05):>10.4f} {tail(dm,0.10):>10.4f} "
        f"{quantile(dm,0.75):>7.3f} {quantile(dm,0.90):>7.3f} {quantile(dm,0.95):>7.3f}"
    )
    print()

print("Regime boundaries (analytic):")
for b in B_GRID:
    print(
        f"  b={b:<6} P(no thin anywhere in list, L=50)={(1-b)**50:.3f}   "
        f"P(X=0 | Poisson approx)=exp(-10b)={exp(-10*b):.3f}"
    )

# ---------------------------------------------------------------- (b) uniform enrichment
print()
print("=" * 100)
print("(b) SMALLEST UNIFORM ENRICHMENT (odds ratio psi on top-10 placement) THAT MOVES THE MEDIAN")
print("=" * 100)
PSI = [1.0, 1.5, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50, 100, 300, 1000, 10000]
print(f"{'b':>6} {'psi*(med>=+.05)':>16} {'psi*(med>=+.10)':>16} {'median@psi=3':>13} {'median@psi=10':>14} {'median@psi=1e4':>15}")
for b in B_GRID:
    ds = {p: mix([delta_dist(L, b, p) for L in L_MIX]) for p in PSI}
    meds = {p: quantile(ds[p], 0.5) for p in PSI}
    p05 = next((p for p in PSI if meds[p] >= 0.05 - 1e-12), None)
    p10 = next((p for p in PSI if meds[p] >= 0.10 - 1e-12), None)
    print(
        f"{b:>6.3f} {str(p05):>16} {str(p10):>16} "
        f"{meds[3]:>13.4f} {meds[10]:>14.4f} {meds[10000]:>15.4f}"
    )

print()
print("Median vs psi, b=0.05 (mixture L) -- the staircase:")
for p in PSI:
    d = mix([delta_dist(L, 0.05, p) for L in L_MIX])
    print(f"  psi={p:<8} median={quantile(d,0.5):+.4f}  mean={mean(d):+.4f}  band={band(quantile(d,0.5))}")

# ---------------------------------------------------------------- (b2) concentrated effect
print()
print("=" * 100)
print("(b2) CONCENTRATED EFFECT: fraction f of reference artists maximally enriched (psi=1e6),")
print("     the remaining 1-f exactly at null. Median vs f.")
print("=" * 100)
for b in [0.01, 0.03, 0.05, 0.10]:
    d_null = mix([delta_dist(L, b, 1.0) for L in L_MIX])
    d_max = mix([delta_dist(L, b, 1e6) for L in L_MIX])
    print(f"\n  b = {b}   (max-enriched median alone = {quantile(d_max,0.5):+.3f})")
    row = []
    for f in [0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.45, 0.49, 0.50, 0.55, 0.60, 0.80, 1.0]:
        d = mix([d_null, d_max], [1 - f, f])
        row.append((f, quantile(d, 0.5)))
    for f, m in row:
        print(f"    f={f:<5} median={m:+.4f}  band={band(m)}")

# ---------------------------------------------------------------- (c) expectation-relative
print()
print("=" * 100)
print("(c) EXPECTATION-RELATIVE STATISTICS -- null behaviour and sensitivity to concentration")
print("=" * 100)


def midp_dist(L, b, psi=1.0):
    """Distribution of the per-artist mid-p PIT value
       M_R = P_null(X < x) + 0.5 * P_null(X = x),
    where the null reference is the CENTRAL hypergeometric for that artist's own (L, T).
    Under the null E[M] = 0.5 EXACTLY for any discrete null, any L, any T, any b."""
    out = defaultdict(float)
    for T, pT in enumerate(binom_pmf(L, b)):
        if pT < 1e-18:
            continue
        null = fnch_pmf(L, T, TOP, 1.0)
        obs = fnch_pmf(L, T, TOP, psi)
        keys = sorted(null)
        for x, px in obs.items():
            below = sum(null[k] for k in keys if k < x)
            out[round(below + 0.5 * null[x], 12)] += pT * px
    return dict(out)


def exceed_share(L, b, psi=1.0):
    """P(X > E_null[X]) -- the naive 'exceeds its own expectation' statistic, with
    ties (X == E) counted as half."""
    s = 0.0
    for T, pT in enumerate(binom_pmf(L, b)):
        if pT < 1e-18:
            continue
        e = TOP * T / L
        for x, px in fnch_pmf(L, T, TOP, psi).items():
            s += pT * px * (1.0 if x > e + 1e-12 else (0.5 if abs(x - e) < 1e-12 else 0.0))
    return s


def excess_ratio(L, b, psi=1.0):
    """E[X_obs] / E[X_null] -- the enrichment ratio against a structure-preserving null.
    Null value is exactly 1.0."""
    num = den = 0.0
    for T, pT in enumerate(binom_pmf(L, b)):
        if pT < 1e-18:
            continue
        num += pT * sum(x * px for x, px in fnch_pmf(L, T, TOP, psi).items())
        den += pT * (TOP * T / L)
    return num / den if den else float("nan")


print("\nNull values (psi = 1), mixture over L in [30,100]:")
print(f"{'b':>6} {'mean mid-p':>11} {'sd mid-p':>10} {'exceed-share':>13} {'excess ratio':>13} {'P(mid-p>=0.95)':>15}")
for b in B_GRID:
    dm = mix([midp_dist(L, b) for L in L_MIX])
    mu = mean(dm)
    sd = (sum(p * (v - mu) ** 2 for v, p in dm.items())) ** 0.5
    es = sum(exceed_share(L, b) for L in L_MIX) / len(L_MIX)
    er = sum(excess_ratio(L, b) for L in L_MIX) / len(L_MIX)
    print(f"{b:>6.3f} {mu:>11.6f} {sd:>10.4f} {es:>13.4f} {er:>13.6f} {tail(dm,0.95):>15.4f}")

print("\nUnder a CONCENTRATED effect (fraction f maximally enriched), b = 0.03:")
b = 0.03
dn = mix([midp_dist(L, b, 1.0) for L in L_MIX])
dx = mix([midp_dist(L, b, 1e6) for L in L_MIX])
er_n = sum(excess_ratio(L, b, 1.0) for L in L_MIX) / len(L_MIX)
er_x = sum(excess_ratio(L, b, 1e6) for L in L_MIX) / len(L_MIX)
d_null_delta = mix([delta_dist(L, b, 1.0) for L in L_MIX])
d_max_delta = mix([delta_dist(L, b, 1e6) for L in L_MIX])
print(f"{'f':>6} {'TCE-C1 median':>14} {'mean mid-p':>11} {'z(N=10k)':>10} {'z(N=50k)':>10} {'excess ratio':>13}")
for f in [0.0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 1.0]:
    dmix = mix([dn, dx], [1 - f, f])
    mu = mean(dmix)
    sd0 = (sum(p * (v - 0.5) ** 2 for v, p in dn.items())) ** 0.5
    dmed = mix([d_null_delta, d_max_delta], [1 - f, f])
    er = (1 - f) * er_n + f * er_x
    print(
        f"{f:>6.3f} {quantile(dmed,0.5):>+14.4f} {mu:>11.5f} "
        f"{(mu-0.5)/(sd0/10000**0.5):>10.1f} {(mu-0.5)/(sd0/50000**0.5):>10.1f} {er:>13.4f}"
    )

print("\nSanity: E[mid-p] under the null must be exactly 0.5 for every (L, b) cell.")
worst = max(abs(mean(midp_dist(L, b)) - 0.5) for L in (30, 50, 100) for b in (0.01, 0.05, 0.2))
print(f"  max |E[mid-p] - 0.5| over L in (30,50,100) x b in (0.01,0.05,0.2) = {worst:.2e}")

print("\nSanity: E[Delta_R] under the null must be exactly 0.")
worst = max(abs(mean(delta_dist(L, b))) for L in (30, 50, 100) for b in (0.01, 0.05, 0.2))
print(f"  max |E[Delta_R]| = {worst:.2e}")
