"""DD-F1 provenance: the sub-decile degree figures quoted in the execution log.

DD-P3 finding 12: the log quotes a band series for "share of artists with zero edges
below the top decile", and no committed script computed it — the figures came from an
ad-hoc probe. This reproduces them, so the log's numbers have an owner in code.

Band edges are stated explicitly here rather than elided, because the series is only
reproducible under these exact edges (the analyst had to search six schemes to recover
them, and two neighbouring schemes give visibly different numbers).

Read-only. Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/dd_f1_provenance.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

TOP_DECILE = 0.90
BAND_EDGES = (0.90, 0.95, 0.98, 0.99, 0.999, 1.01)   # explicit; see docstring

# The endpoints DD-F1 names individually in the execution log.
NAMED = ["Radiohead", "The Beatles", "Metallica", "Taylor Swift", "Muse", "Coldplay",
         "Miles Davis", "Daft Punk", "Madonna", "Bob Dylan", "Pink Floyd", "Aphex Twin",
         "Megadeth", "Lykke Li"]


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = ctx.pctl
    offsets = np.asarray(store.offsets)
    neighbours = np.asarray(store.neighbours)
    degree = np.diff(offsets)

    # sub-decile degree: neighbours strictly below the top decile, per node
    src = np.repeat(np.arange(len(pctl), dtype=np.int64), degree)
    sub = (pctl[neighbours] < TOP_DECILE).astype(np.int64)
    sub_degree = np.bincount(src, weights=sub, minlength=len(pctl)).astype(np.int64)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    print(f"N = {len(pctl):,}   nodes below the top decile: "
          f"{int((pctl < TOP_DECILE).sum()):,} ({100.0 * (pctl < TOP_DECILE).mean():.2f} %)\n")

    print("DD-F1 band series — sub-decile degree by popularity percentile")
    print(f"{'band':<22}{'n':>7}{'mean sub-deg':>14}{'zero sub-deg':>14}")
    series = []
    for lo, hi in zip(BAND_EDGES, BAND_EDGES[1:]):
        m = (pctl >= lo) & (pctl < hi)
        if not m.any():
            continue
        row = {"lo": lo, "hi": min(hi, 1.0), "n": int(m.sum()),
               "mean_sub_degree": float(sub_degree[m].mean()),
               "zero_frac": float((sub_degree[m] == 0).mean())}
        series.append(row)
        print(f"[{lo:.3f},{min(hi, 1.0):.3f})".ljust(22)
              + f"{row['n']:>7}{row['mean_sub_degree']:>14.2f}"
              + f"{100 * row['zero_frac']:>13.1f} %")

    print("\nendpoints DD-F1 names individually")
    named = {}
    for nm in NAMED:
        i = by_name[nm]
        named[nm] = {"pctl": float(pctl[i]), "degree": int(degree[i]),
                     "sub_degree": int(sub_degree[i])}
        print(f"  {nm:<16} pctl {pctl[i]:.4f}  degree {degree[i]:>3}  "
              f"sub-decile degree {sub_degree[i]:>3}")

    (HERE / "dd_f1_provenance.json").write_text(
        json.dumps({"artifact_sha256": digest, "top_decile": TOP_DECILE,
                    "band_edges": list(BAND_EDGES), "series": series, "named": named},
                   indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {HERE / 'dd_f1_provenance.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
