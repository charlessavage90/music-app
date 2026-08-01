"""TD-1: capture the pre-cap candidate lists + ranking for the ALG-E archive.

Why this exists
---------------
`TAS-4` measures how many of an artist's OWN top-50 change under a reranking.
Its bound (prereg §2, `TAS-4`) says the built consequence "is not derivable from
`TAS-4` alone", because mutual k-NN kills an edge when EITHER endpoint drops it.
This module captures the exact inputs the cap step receives so that the
per-artist-swap -> surviving-edge-turnover transfer function can be measured on
the real candidate-list and mutuality distribution rather than assumed.

It REUSES `_capture_pipeline` from the Track B harness (cb_run_cells.py:185) —
same code path, same archive, byte-deterministic — and does not reimplement any
pipeline stage. The archive is opened through `ReadOnlyArchive` inside that
helper (GRT-A1).

Output: an .npz of int-id CSR arrays (offsets / candidate ids / ranking values)
so the simulation runs are seconds rather than minutes. Nothing is built and no
artifact is written.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/td_capture.py --out <path.npz>
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
TRACK_B = HERE.parent / "2026-07-30-track-b-cap-selection"
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "src"))
sys.path.insert(0, str(TRACK_B))

from cb_run_cells import _capture_pipeline  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", default="ALG-E")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t0 = time.monotonic()
    adjacency, ranking, pop = _capture_pipeline(args.archive)
    print(f"captured {len(adjacency)} nodes in {time.monotonic() - t0:.1f}s")

    # IDs in sorted-MBID order, matching every other ordering decision in the
    # builder (design §9). Because ids are assigned in sorted-MBID order, the
    # "lowest MBID" tie-break is exactly "lowest id".
    mbids = sorted(adjacency)
    index = {m: i for i, m in enumerate(mbids)}
    n = len(mbids)

    lengths = np.fromiter((len(adjacency[m]) for m in mbids), dtype=np.int64, count=n)
    offsets = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(lengths, out=offsets[1:])
    total = int(offsets[-1])

    cand = np.empty(total, dtype=np.int32)
    rank = np.empty(total, dtype=np.float64)
    score = np.empty(total, dtype=np.float32)
    cursor = 0
    for m in mbids:
        r = ranking[m]
        for dst, sc in adjacency[m].items():
            cand[cursor] = index[dst]
            rank[cursor] = r[dst]
            score[cursor] = sc
            cursor += 1
    assert cursor == total

    popv = np.fromiter((pop[m] for m in mbids), dtype=np.float64, count=n)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        offsets=offsets,
        cand=cand,
        rank=rank,
        score=score,
        pop=popv,
        mbids=np.array(mbids, dtype=object),
    )
    print(f"nodes={n} directed_candidates={total} -> {out}")
    print(f"total {time.monotonic() - t0:.1f}s")


if __name__ == "__main__":
    main()
