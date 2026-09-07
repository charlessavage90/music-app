"""Q1/Q3: how much does a FIXED MBID set's degree move when only the population moves?

Two artifacts, same cap rule (trimmed_union, top_j 50, ceiling 50), same algorithm
(ALG-B), same rescale, same drop flags; different crawl population.
Run from api/ so the SHIPPED GraphStore parses both (cxr_census.py precedent).
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from artistpath_api.graph_store import GraphStore

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
OLD = SCRATCH / "graph-msw-tu50.bin"
NEW = SCRATCH / "graph-cxa-adopted.bin"
LUX = SCRATCH / "graph-lux4.bin"

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()

def deg(s: GraphStore) -> np.ndarray:
    return np.diff(s.offsets).astype(np.int64)

def stat(d: np.ndarray) -> str:
    if d.size == 0:
        return "n=0"
    return (f"n={d.size:>6,}  median={np.median(d):>6.1f}  mean={d.mean():>6.2f}  "
            f"share<=2={100.0*np.mean(d <= 2):>6.2f}%  share==1={100.0*np.mean(d == 1):>5.2f}%  "
            f"p10={np.percentile(d,10):>4.0f} p90={np.percentile(d,90):>4.0f}")

def main() -> None:
    for p in (OLD, NEW, LUX):
        print(f"sha256 {sha(p)}  {p.name}")
    old, new, lux = GraphStore.load(OLD), GraphStore.load(NEW), GraphStore.load(LUX)
    d_old, d_new, d_lux = deg(old), deg(new), deg(lux)

    print("\n=== A. reproducibility control: graph-lux4 vs graph-msw-tu50 (same archive snapshot) ===")
    print("mbid lists identical:", old.mbids == lux.mbids)
    print("offsets identical   :", np.array_equal(old.offsets, lux.offsets))
    print("neighbours identical:", np.array_equal(old.neighbours, lux.neighbours))
    print("scores identical    :", np.array_equal(old.scores, lux.scores))
    print("degree stats old :", stat(d_old))
    print("degree stats lux4:", stat(d_lux))

    old_ix = {m: i for i, m in enumerate(old.mbids)}
    new_ix = {m: i for i, m in enumerate(new.mbids)}
    common = [m for m in old.mbids if m in new_ix]
    lost = [m for m in old.mbids if m not in new_ix]
    added = [m for m in new.mbids if m not in old_ix]
    print(f"\n=== B. populations === old {len(old.mbids):,}  new {len(new.mbids):,}  "
          f"common {len(common):,}  lost {len(lost):,}  added {len(added):,}")

    oi = np.array([old_ix[m] for m in common]); ni = np.array([new_ix[m] for m in common])
    do, dn = d_old[oi], d_new[ni]
    print("\n=== C. FIXED SET = the 58,793 MBIDs in both, measured in each artifact ===")
    print("  in OLD :", stat(do))
    print("  in NEW :", stat(dn))
    delta = dn - do
    print(f"  paired delta: median={np.median(delta):+.1f} mean={delta.mean():+.3f} "
          f"|delta| median={np.median(np.abs(delta)):.1f} mean={np.abs(delta).mean():.3f}")
    print(f"  share changed at all: {100.0*np.mean(delta != 0):.2f}%   "
          f"lost>=1 edge: {100.0*np.mean(delta < 0):.2f}%   gained: {100.0*np.mean(delta > 0):.2f}%")
    print(f"  lost artists (fixed set members absent from NEW): {len(lost)}")

    print("\n=== D. STRATIFIED by degree in OLD -- LBD-C2's own statistic on a fixed set ===")
    print(f"{'stratum (deg in OLD)':<24}{'n':>8}{'med OLD':>9}{'med NEW':>9}{'<=2 OLD':>9}{'<=2 NEW':>9}"
          f"{'mean OLD':>10}{'mean NEW':>10}{'med |d|':>9}{'%moved':>8}")
    strata = [("deg == 1", do == 1), ("deg == 2", do == 2), ("deg <= 2", do <= 2),
              ("deg 3-4", (do >= 3) & (do <= 4)), ("deg <= 4", do <= 4),
              ("deg 5-9", (do >= 5) & (do <= 9)), ("deg 10-19", (do >= 10) & (do <= 19)),
              ("deg 20-49", (do >= 20) & (do <= 49)), ("deg == 50 (ceiling)", do == 50),
              ("ALL", np.ones_like(do, dtype=bool))]
    for label, mask in strata:
        a, b = do[mask], dn[mask]
        if a.size == 0:
            continue
        print(f"{label:<24}{a.size:>8,}{np.median(a):>9.1f}{np.median(b):>9.1f}"
              f"{100*np.mean(a<=2):>8.2f}%{100*np.mean(b<=2):>8.2f}%"
              f"{a.mean():>10.2f}{b.mean():>10.2f}{np.median(np.abs(b-a)):>9.1f}"
              f"{100*np.mean(a!=b):>7.1f}%")

    print("\n=== E. ceiling saturation (the trim only bites at degree == ceiling) ===")
    for nm, d in (("old", d_old), ("new", d_new)):
        at = int((d == 50).sum())
        print(f"  {nm}: nodes at degree 50 = {at:,} ({100.0*at/d.size:.2f}% of nodes); "
              f"max degree {d.max()}; edges incident to a deg-50 node = "
              f"{int(d[d == 50].sum()):,} of {int(d.sum()):,} endpoints "
              f"({100.0*d[d==50].sum()/d.sum():.2f}%)")

    print("\n=== F. added set as CXR measured it, for cross-reference ===")
    ai = np.array([new_ix[m] for m in added])
    print("  added in NEW:", stat(d_new[ai]))

    print("\n=== G. resolution of the two LBD-C2 statistics on a set of 29,892 ===")
    da = d_new[ai]
    rng = np.random.default_rng(20260906)
    meds, shares = [], []
    for _ in range(2000):
        s = rng.choice(da, size=da.size, replace=True)
        meds.append(np.median(s)); shares.append(np.mean(s <= 2))
    meds = np.array(meds); shares = np.array(shares)
    print(f"  bootstrap median degree: p2.5={np.percentile(meds,2.5):.2f} "
          f"p97.5={np.percentile(meds,97.5):.2f}  distinct values seen={sorted(set(meds.tolist()))}")
    print(f"  bootstrap share<=2: p2.5={100*np.percentile(shares,2.5):.3f}% "
          f"p97.5={100*np.percentile(shares,97.5):.3f}%  (half-width "
          f"{100*(np.percentile(shares,97.5)-np.percentile(shares,2.5))/2:.3f} pp)")

main()
