"""Q2: the tie-break boundary at the endpoint's 100-row truncation.

The served list is a score-ordered truncation (measured: 99.99% of omitted rows
score at-or-below the partner's served minimum). Where several candidates tie at
that minimum score, the endpoint's choice among them is unrecoverable, so an
exactly-faithful reimplementation still cannot match. Bounds that loss.
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np

ARCH = Path(r"C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot"
            r"\similar\listenbrainz"
            r"\session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30")
GRAPH = Path(r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin")

def main() -> None:
    idx: dict[str, int] = {}
    def gid(m):
        v = idx.get(m)
        if v is None:
            v = len(idx); idx[m] = v
        return v
    nb: dict[int, list[int]] = {}; sc: dict[int, list[int]] = {}
    for e in os.scandir(ARCH):
        if not e.name.endswith(".json"):
            continue
        mb = e.name[:-5]; me = gid(mb)
        rows = json.loads(open(e.path, "rb").read())
        a, s = [], []
        for r in rows:
            am = r.get("artist_mbid")
            if not am or am == mb:
                continue
            a.append(gid(am)); s.append(int(r.get("score") or 0))
        nb[me] = a; sc[me] = s
    N = len(idx)
    print(f"payloads {len(nb):,}  distinct mbids {N:,}")

    smap = {i: dict(zip(nb[i], sc[i])) for i in nb}
    minsc = {i: (min(sc[i]) if sc[i] else None) for i in nb}
    L = {i: len(nb[i]) for i in nb}
    tied_served = {i: (sum(1 for v in sc[i] if v == minsc[i]) if sc[i] else 0) for i in nb}

    # omitted candidates AT the served minimum, observed via the other direction
    tied_omitted = {i: 0 for i in nb}
    for i in nb:
        for y, v in smap[i].items():
            if y in smap and i not in smap[y] and minsc[y] is not None and v == minsc[y]:
                tied_omitted[y] += 1

    full = [i for i in nb if L[i] >= 100]
    print(f"\n=== artists whose served list is at the 100 ceiling: {len(full):,} "
          f"({100.0*len(full)/len(nb):.2f}% of crawled) ===")
    a = np.array([tied_served[i] for i in full])
    b = np.array([tied_omitted[i] for i in full])
    print(f"  served rows tied at the list minimum:  median {np.median(a):.0f}  mean {a.mean():.2f}  p90 {np.percentile(a,90):.0f}  max {a.max()}")
    print(f"  OBSERVED omitted candidates at that same score: median {np.median(b):.0f}  mean {b.mean():.2f}  p90 {np.percentile(b,90):.0f}  max {b.max()}")
    print(f"  share with an ambiguous boundary (>=1 omitted at the min score): {100.0*np.mean(b>0):.2f}%")
    ceil = (100.0 - a + a * a / np.maximum(a + b, 1)) / 100.0
    print(f"  expected overlap ceiling under a random tie-break (UPPER bound):")
    print(f"     median {np.median(ceil):.4f}  mean {ceil.mean():.4f}  p10 {np.percentile(ceil,10):.4f}  p25 {np.percentile(ceil,25):.4f}  min {ceil.min():.4f}")

    # not-full artists: ceiling is 1.0 unless the residue applies
    notfull = [i for i in nb if L[i] < 100]
    print(f"\n=== artists below the ceiling: {len(notfull):,} -> no truncation, ceiling 1.0 "
          f"except for the lineage residue ===")

    # fame bands
    payload = GRAPH.read_bytes()
    ml = int(np.frombuffer(payload[16:20], dtype="<u4")[0])
    meta = json.loads(payload[len(payload)-ml:])
    fame = meta.get("fame_lb") or []
    pairs = [(m, f) for m, f in zip(meta["mbids"], fame) if f is not None and m in idx and idx[m] in nb]
    fv = np.array([f for _, f in pairs], float); gi = np.array([idx[m] for m, _ in pairs])
    qs = np.percentile(fv, [20, 40, 60, 80]); edges = [-np.inf] + list(qs) + [np.inf]
    allceil = np.ones(N)
    for i in full:
        allceil[i] = (100.0 - tied_served[i] + tied_served[i]**2 / max(tied_served[i]+tied_omitted[i], 1)) / 100.0
    print(f"\n=== per-fame-band ceiling on an overlap metric (UPPER bound) ===")
    print(f"{'fame band':<10}{'n':>8}{'share at 100':>14}{'median ceiling':>16}{'mean ceiling':>14}{'p10 ceiling':>13}")
    for k in range(5):
        m = (fv > edges[k]) & (fv <= edges[k+1]); sel = gi[m]
        c = allceil[sel]
        atc = np.mean([L[i] >= 100 for i in sel])
        print(f"{'Q'+str(k+1):<10}{sel.size:>8,}{100*atc:>13.2f}%{np.median(c):>16.4f}{c.mean():>14.4f}{np.percentile(c,10):>13.4f}")

main()
