"""Does the FAMOUS-TO-FAMOUS stratum still have nowhere to go on the ADOPTED map?

**Why this exists.** `PRODUCT-REQUIREMENTS.md:310-313` records, from `DD-F1`
(2026-07-28), that "superstar endpoints have zero edges below the top popularity
decile", and concludes REQ-37 is "currently unachievable on famous-to-famous pairs at
any router setting". A `JFX-` prereg critique leaned on that to argue the `S1` stratum
is a guaranteed zero and should come out of the gate.

**Three reasons that claim may not transfer, all of which the owner raised:**

1. `DD-F1` was measured on the **pre-`MSW-`** artifact. The cap rule changed
   2026-08-06 from mutual k-NN (edge survives only if BOTH endpoints rank the other
   top-k) to `trimmed_union` (EITHER suffices). An obscure artist ranks a famous one
   highly; the famous one does not reciprocate -- so precisely these edges were the
   ones mutual k-NN destroyed and `trimmed_union` keeps.
2. `DD-F1` is stated in **popularity** currency. `JFX-` scores in **fame**
   (`fame_lb`). CLAUDE.md is explicit that popularity != fame.
3. `DD-F1` predates the 2026-08-02 fame redefinition, so its "fame" is the retired
   worldly construct.

**So this measures BOTH currencies on the adopted artifact**: the popularity version
reproduces `DD-F1`'s own claim on the new map (apples to apples), and the fame version
answers what `JFX-` actually needs.

Reports only. Adopts nothing, decides nothing.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api/src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402

GRAPH = ROOT / "builder/scratch/graph-msw-tu50.bin"
EXPECTED_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"


def _raw_fame_from_metadata(payload: bytes) -> list:
    """Pull the `fame_lb` metadata key straight out of the APG1 blob.

    Mirrors `GraphStore.from_bytes`'s cursor arithmetic rather than importing
    it, because that method deliberately drops the raw values. Header layout is
    fixed by the format: magic, version, N, E, metadata length.
    """
    import struct

    header = struct.Struct("<4sIIIQ")
    magic, version, n, e, meta_len = header.unpack_from(payload)
    if magic != b"APG1":
        raise SystemExit(f"bad magic {magic!r}")
    cursor = header.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor : cursor + meta_len])
    if "fame_lb" not in meta:
        raise SystemExit("artifact carries no fame_lb key")
    return meta["fame_lb"]


def main() -> None:
    payload = GRAPH.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    print(f"artifact: {GRAPH.name}")
    print(f"sha256:   {sha}")
    print(f"expected: {EXPECTED_SHA}")
    if sha != EXPECTED_SHA:
        raise SystemExit("REFUSING: artifact identity does not match. Wrong graph.")
    print("identity: OK\n")

    g = GraphStore.from_bytes(payload)
    n = g.artist_count
    degrees = np.diff(g.offsets).astype(np.int64)

    # ---- the two rulers -------------------------------------------------
    # fame: raw fame_lb, nulls excluded from the ranking population (JFX §2).
    #
    # ⚠ GraphStore does NOT expose raw fame. It computes `fame_lb_pctl` at load
    # and discards the values ("the raw counts are not kept, since nothing
    # routes on them" -- graph_store.py). JFX §2 names "in-memory
    # `fame_lb_raw`", which is a BUILDER field (`Graph.fame_lb_raw`), not
    # anything reachable from the serving store. So the raw values must come
    # from the artifact's own metadata blob, parsed here.
    fame_lb = _raw_fame_from_metadata(payload)
    if len(fame_lb) != n:
        raise SystemExit(f"fame_lb length {len(fame_lb)} != node count {n}")
    fame = np.array(
        [np.nan if v is None else float(v) for v in fame_lb], dtype=np.float64
    )
    measured = ~np.isnan(fame)
    print(f"nodes: {n};  with a fame measurement: {measured.sum()} "
          f"({100 * measured.sum() / n:.2f}%)")

    # popularity: the artifact's pop_raw, DD-F1's currency.
    pop = np.asarray(g.popularity, dtype=np.float64)

    for label, values, valid in (
        ("FAME (fame_lb) -- what JFX scores on", fame, measured),
        ("POPULARITY (pop_raw) -- DD-F1's own currency", pop, np.ones(n, bool)),
    ):
        print("\n" + "=" * 72)
        print(label)
        print("=" * 72)

        vals = values[valid]
        top10_cut = np.quantile(vals, 0.90)
        median_cut = np.quantile(vals, 0.50)

        # endpoint pool: top 10%, exactly as JFX §2 defines S1
        is_top10 = valid & (values >= top10_cut)
        pool = np.flatnonzero(is_top10)
        print(f"top-10% cut: {top10_cut:,.1f}   median cut: {median_cut:,.1f}")
        print(f"top-10% pool: {pool.size} artists\n")

        # For each top-10% artist, where do its neighbours sit?
        frac_below_top10 = np.zeros(pool.size)
        frac_below_median = np.zeros(pool.size)
        n_below_top10 = np.zeros(pool.size, dtype=np.int64)
        zero_below_top10 = 0

        for i, node in enumerate(pool):
            s, e = int(g.offsets[node]), int(g.offsets[node + 1])
            nbrs = g.neighbours[s:e]
            if nbrs.size == 0:
                continue
            nv = values[nbrs]
            nvalid = valid[nbrs]
            usable = nvalid.sum()
            if usable == 0:
                continue
            below10 = int(((nv < top10_cut) & nvalid).sum())
            below50 = int(((nv < median_cut) & nvalid).sum())
            n_below_top10[i] = below10
            frac_below_top10[i] = below10 / usable
            frac_below_median[i] = below50 / usable
            if below10 == 0:
                zero_below_top10 += 1

        print(f"mean degree of the top-10% pool: {degrees[pool].mean():.1f} "
              f"(graph mean {degrees.mean():.1f})")
        print()
        print("Share of a top-10% artist's neighbours that are BELOW the top 10%:")
        for q in (5, 25, 50, 75, 95):
            print(f"   p{q:<3} {np.percentile(frac_below_top10, q) * 100:6.2f}%")
        print(f"   mean {frac_below_top10.mean() * 100:6.2f}%")
        print()
        print("Share BELOW THE MEDIAN (the JFX 'bottom 50%' band):")
        for q in (5, 25, 50, 75, 95):
            print(f"   p{q:<3} {np.percentile(frac_below_median, q) * 100:6.2f}%")
        print(f"   mean {frac_below_median.mean() * 100:6.2f}%")
        print()
        print("DD-F1's literal claim -- 'ZERO edges below the top decile':")
        print(f"   top-10% artists with zero such neighbours: {zero_below_top10}"
              f" of {pool.size} ({100 * zero_below_top10 / pool.size:.2f}%)")
        print(f"   median count of below-top-10% neighbours per artist: "
              f"{np.median(n_below_top10):.0f}")
        print(f"   min / max: {n_below_top10.min()} / {n_below_top10.max()}")


if __name__ == "__main__":
    main()
