"""The TAS pair set -- fresh draw, this probe's own (spec section 3).

OBSCURE-ENDPOINT CLASSES ARE INCLUDED BY THE OWNER'S EXPLICIT TRIGGER,
2026-07-30. NEXT.md parks the `x lower` redraw as his call; this pulls it, for
this probe only. Track B's committed draw is untouched and its classes stay the
record for its own reads.

CLASSES CARRIED END TO END (CRS-A1): Track B's draw returned a sorted set and
discarded each pair's class, making three pre-registered quantities uncomputable
until it was fixed mid-flight. Every pair here carries its label.

NO ATTRITION GUARD, AND NONE IS NEEDED. Track B restricted its draw to pairs
routable in every compared cell because its cells were DIFFERENT GRAPHS. Nothing
here is rebuilt: TAS-5 routes ONE graph under different weights. Only the largest
connected component is retained, so a path exists between any two artists the
draw can offer and no cell can lose a pair.

THIS IS THE PRE-REGISTERED SEED. td_pathedges.py deliberately used a different
one (`20260730-tdcal`) so its calibration run would not consume this draw.
Consuming it here is the intended use.

DETERMINISM: `graph_mbids()` is sorted before sampling. Without that the draw
would depend on dict insertion order and the seed would not reproduce.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_pairs.py
"""

from __future__ import annotations

import json
import random

from tas_common import HERE, fame_frame, graph_mbids
from tas_signal import edge_class

OUT = HERE / "tas_pairs.json"
SEED = "20260730-tas"
PER_CLASS = 40
MIN_READABLE_PER_CLASS = 20
CLASSES = ("ff", "fo", "oo")


def draw_pairs() -> list[tuple[str, str, str]]:
    """(mbid_lo, mbid_hi, class) triples, PER_CLASS of each where readable."""
    frame = fame_frame()
    mbids = sorted(m for m in graph_mbids() if m in frame)
    rng = random.Random(SEED)
    buckets: dict[str, set[tuple[str, str, str]]] = {c: set() for c in CLASSES}
    attempts = 0
    while any(len(v) < PER_CLASS for v in buckets.values()) and attempts < 2_000_000:
        attempts += 1
        a, b = rng.sample(mbids, 2)
        cls = edge_class(frame[a], frame[b])
        if len(buckets[cls]) < PER_CLASS:
            lo, hi = sorted((a, b))
            buckets[cls].add((lo, hi, cls))
    out: list[tuple[str, str, str]] = []
    for cls in CLASSES:
        pairs = sorted(buckets[cls])
        # A class below the floor is reported UNREADABLE, never pooled into
        # another -- CRS-G3's rule, and section 3 fixes the floor at draw time.
        out.extend(pairs if len(pairs) >= MIN_READABLE_PER_CLASS else [])
    return out


def main() -> None:
    pairs = draw_pairs()
    counts = {c: sum(1 for p in pairs if p[2] == c) for c in CLASSES}
    OUT.write_text(
        json.dumps(
            {
                "seed": SEED,
                "per_class_target": PER_CLASS,
                "min_readable_per_class": MIN_READABLE_PER_CLASS,
                "counts": counts,
                "unreadable": [c for c, n in counts.items() if n == 0],
                "pairs": pairs,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(counts, flush=True)


if __name__ == "__main__":
    main()
