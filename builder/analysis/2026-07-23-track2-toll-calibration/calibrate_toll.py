"""Calibrate the T1 expressway toll for the Track 2 pre-registration.

Discharges PR-C of `docs/superpowers/findings/2026-07-23-track2-protocol-analyst-review.md`:
"re-measure the toll as a fraction of `w_hop` after D1's fix is chosen."

D1 established that P3's rule (`s_max` just above the largest non-ceiling score) makes
the toll ~1.4 % of `w_hop` and therefore inert. The replacement prices a ceiling edge as
though its similarity were some pre-registered `s_toll < 1`. This script measures what
that price means in the graph's own terms, so the pre-registered levels are grounded
rather than picked.

Owns only NEW quantities. The ceiling-edge count, the largest non-ceiling score and the
score grid are owned by the analyst review's M1 and are cited, never recomputed here.

Run from `api/`:
    UV_LINK_MODE=copy uv run python ../builder/analysis/2026-07-23-track2-toll-calibration/calibrate_toll.py
"""

import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "api" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

# Production constants, read from api/src/artistpath_api/config.py (cited, not guessed).
W_SIM = 3.0
W_HOP = 0.02

# Candidate toll levels, expressed as the similarity a ceiling edge is priced at.
CANDIDATE_S_TOLL = (0.99, 0.95, 0.90, 0.80)


def main() -> None:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore

    store = GraphStore.load(GRAPH)
    n = store.artist_count
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    scores = np.asarray(store.scores, dtype=np.float64)

    # Average-rank percentile over the popularity array (pre-registration P6).
    order = np.argsort(pop, kind="stable")
    ranks = np.empty(n, dtype=np.float64)
    srt = pop[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and srt[j + 1] == srt[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2.0
        i = j + 1
    pctl = ranks / (n - 1)

    src = np.repeat(np.arange(n, dtype=np.int64), np.diff(store.offsets))
    dst = np.asarray(store.neighbours, dtype=np.int64)
    hi = pctl >= 0.90
    top_incident = hi[src] | hi[dst]
    lateral = hi[src] & hi[dst]

    ceiling = scores >= 1.0

    # --- Q1: the similarity distribution a toll is competing against -----------
    qs = (0.10, 0.25, 0.50, 0.75, 0.90, 0.99)
    print("Q1  edge-similarity quantiles (what an alternative hop costs)")
    print(f"{'set':<28}{'n':>10}   " + "".join(f"p{int(q*100):<7}" for q in qs))
    for name, mask in (
        ("all edges", np.ones(len(scores), dtype=bool)),
        ("top-decile incident", top_incident),
        ("lateral (both >= p90)", lateral),
    ):
        row = "".join(f"{np.quantile(scores[mask], q):<8.4f}" for q in qs)
        print(f"{name:<28}{int(mask.sum()):>10}   {row}")

    # --- Q2: how much expressway each famous node has -------------------------
    deg = np.diff(store.offsets).astype(np.int64)
    ceil_deg = np.bincount(src[ceiling], minlength=n).astype(np.int64)
    top_nodes = np.where(hi)[0]
    print("\nQ2  ceiling edges per node (the expressway's local size)")
    print(f"  all nodes          : mean {ceil_deg.mean():.3f}  median {np.median(ceil_deg):.1f}  max {ceil_deg.max()}")
    print(f"  top-decile nodes   : mean {ceil_deg[top_nodes].mean():.3f}  median {np.median(ceil_deg[top_nodes]):.1f}  max {ceil_deg[top_nodes].max()}")
    with_any = int((ceil_deg[top_nodes] > 0).sum())
    print(f"  top-decile nodes with >= 1 ceiling edge: {with_any} of {top_nodes.size} ({100*with_any/top_nodes.size:.2f} %)")
    print(f"  their mean degree  : {deg[top_nodes].mean():.2f}")

    # --- Q3: what each candidate toll actually buys ---------------------------
    print("\nQ3  candidate toll levels")
    print(f"{'s_toll':<9}{'toll':<10}{'x w_hop':<10}{'pctile of top-decile-incident edges at or below s_toll':<10}")
    for s_toll in CANDIDATE_S_TOLL:
        toll = W_SIM * (1.0 - s_toll)
        frac = float((scores[top_incident] <= s_toll).mean())
        print(f"{s_toll:<9.2f}{toll:<10.4f}{toll / W_HOP:<10.2f}{100 * frac:<10.2f} %")

    # P3-as-written, for the record: the level D1 rejected.
    s_max_p3 = float(scores[~ceiling].max())
    toll_p3 = W_SIM * (1.0 - s_max_p3)
    print(f"\n  P3 as written (s_max just above largest non-ceiling score):")
    print(f"    toll = {toll_p3:.3e} = {100 * toll_p3 / W_HOP:.2f} % of w_hop   <- D1: inert")

    # --- Q4: is the ceiling on the surface a path would actually traverse? -----
    # Q2 says most top-decile nodes carry no ceiling edge at all. Paths are not
    # drawn uniformly from that decile, so the question that decides whether T1
    # has any purchase is whether saturation concentrates where routing goes.
    print("\nQ4  does the ceiling sit where paths run?")
    for lo, hi_q, label in ((0.90, 0.99, "p90-p99 by degree"), (0.99, 1.01, "top 1 % by degree")):
        dq_lo, dq_hi = np.quantile(deg, lo), (np.quantile(deg, hi_q) if hi_q <= 1.0 else deg.max() + 1)
        band = np.where((deg >= dq_lo) & (deg < dq_hi))[0]
        if band.size:
            print(f"  {label:<20} n={band.size:>6}  mean ceiling edges {ceil_deg[band].mean():>6.2f}  "
                  f"with >= 1: {100 * (ceil_deg[band] > 0).mean():>5.1f} %")

    by_name: dict[str, int] = {}
    for idx, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[idx] > pop[prev]:
            by_name[nm] = idx
    endpoints = [
        "Miles Davis", "Daft Punk", "The Shins", "Wishbone Ash", "Metallica",
        "Taylor Swift", "Radiohead", "The Beatles", "Muse", "Coldplay", "Madonna",
        "Bob Dylan", "Pink Floyd", "Aphex Twin", "Arctic Monkeys", "Johnny Cash",
        "Michael Jackson", "Gorillaz", "System of a Down", "R.E.M.",
        "The Rolling Stones", "Linkin Park", "Nirvana", "CROOVE",
    ]
    found = [(nm, by_name[nm]) for nm in endpoints if nm in by_name]
    ids = np.array([i for _, i in found], dtype=np.int64)
    print(f"\n  pre-registered endpoints ({len(found)} of {len(endpoints)} resolved):")
    print(f"    mean ceiling edges {ceil_deg[ids].mean():.2f}   with >= 1: "
          f"{int((ceil_deg[ids] > 0).sum())} of {ids.size}   mean degree {deg[ids].mean():.1f}")
    saturated = sorted(((int(ceil_deg[i]), nm) for nm, i in found), reverse=True)[:8]
    print("    most ceiling-saturated endpoints: "
          + ", ".join(f"{nm} ({c})" for c, nm in saturated))


if __name__ == "__main__":
    main()
