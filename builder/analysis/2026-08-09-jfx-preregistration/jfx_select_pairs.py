"""`JFX-` §2 stage 1: draw the candidate pair set BEFORE `JFX-B` exists.

Governing document: docs/superpowers/specs/2026-08-09-journey-fame-exposure-preregistration.md

Selection only. Routes nothing, measures nothing, and reads no result — it exists
so the sample is fixed by a committed artifact rather than by whoever runs the
arms. Output is committed alongside the pre-registration.

WHY TWO STAGES (§2). The analysed population is the INTERSECTION of both arms'
node sets, and `JFX-B` does not exist yet. So this draws 150 candidates per
stratum from `JFX-A` now; after the build, the first 100 per stratum whose
endpoints survive in both arms are taken IN COMMITTED ORDER. Over-selection is
what stops a shortfall becoming a licence to draw more.

STRATA are cut on `JFX-A`'s raw `fame_lb` — a fixed ruler, chosen before any
result exists, because percentile is population-relative and the two arms have
different populations (§0.1(a)).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-09-jfx-preregistration/jfx_select_pairs.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from artistpath_builder.artifact import deserialise

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
ADOPTED = ROOT / "builder" / "scratch" / "graph-msw-tu50.bin"

SEED = 20260809
PER_STRATUM = 150
FAMOUS_TOP = 0.10
OBSCURE_BOTTOM = 0.50


def main() -> None:
    graph = deserialise(ADOPTED.read_bytes())
    # `fame_lb` is the WIRE key; the in-memory identifier carries its currency.
    # A null is a MEASURED ABSENCE, never a floor (FAM-AM1.8) — so an artist
    # without a measurement cannot be placed in a fame stratum at all, and is
    # excluded from the ENDPOINT pool rather than coerced to 0, which would
    # silently file every unmeasured artist as maximally obscure.
    fame = {
        m: v
        for m, v in zip(graph.mbids, graph.fame_lb_raw)
        if v is not None
    }
    skipped = len(graph.mbids) - len(fame)
    print(f"excluded {skipped:,} artists with no fame measurement from the pool")

    # Sorted before anything else: the draw must not depend on dict ordering,
    # which is an implementation detail and not part of the pre-registration.
    ranked = sorted(fame, key=lambda m: (-fame[m], m))
    n = len(ranked)
    famous = set(ranked[: int(n * FAMOUS_TOP)])
    obscure = set(ranked[int(n * (1.0 - OBSCURE_BOTTOM)) :])
    print(f"population {n:,}  famous {len(famous):,}  obscure {len(obscure):,}")

    rng = random.Random(SEED)
    famous_l, obscure_l = sorted(famous), sorted(obscure)

    def draw(pool_a: list[str], pool_b: list[str], want: int) -> list[list[str]]:
        seen: set[tuple[str, str]] = set()
        out: list[list[str]] = []
        while len(out) < want:
            a, b = rng.choice(pool_a), rng.choice(pool_b)
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            if key in seen:
                continue
            seen.add(key)
            out.append([a, b])
        return out

    strata = {
        "S1": draw(famous_l, famous_l, PER_STRATUM),
        "S2": draw(famous_l, obscure_l, PER_STRATUM),
        "S3": draw(obscure_l, obscure_l, PER_STRATUM),
    }

    payload = {
        "status": (
            "JFX- stage 1 candidate pairs. SELECTION ONLY -- no journey has been "
            "routed and no outcome computed. Stage 2 takes the first 100 per "
            "stratum surviving the intersection with JFX-B, in this order."
        ),
        "governing": (
            "docs/superpowers/specs/2026-08-09-journey-fame-exposure-preregistration.md"
        ),
        "seed": SEED,
        "drawn_from": {
            "artifact": ADOPTED.name,
            "nodes": n,
            "famous_top": FAMOUS_TOP,
            "obscure_bottom": OBSCURE_BOTTOM,
        },
        "per_stratum_candidates": PER_STRATUM,
        "strata": strata,
    }
    out = HERE / "jfx_candidate_pairs.json"
    out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    for name, pairs in strata.items():
        example = pairs[0]
        print(f"{name}: {len(pairs)} pairs, first = {example[0][:8]}…/{example[1][:8]}…")
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
