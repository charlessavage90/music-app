"""`LBA-M1`'s query-cost pair set — drawn ONCE, after the built arms are known, and sha-pinned
BEFORE any timing is taken.

§4 fixes the drawing rule before any arm is built, and states plainly that the set "cannot be
drawn until stage 2 says which arms exist, which is stated here so the ordering is not discovered
later". This script is that draw:

  * 200 pairs
  * `random.Random(20260914)`
  * from the artists present in EVERY built arm AND in the served map, so that no arm is measured
    on pairs another could not route
  * a pair whose endpoints are adjacent in ANY map is redrawn, because `find_journey`'s
    forced-detour branch is a different code path and would time a different thing

HOW "REDRAWN" IS IMPLEMENTED, stated so it is not a later question. Drawing one pair at a time and
re-testing it would need one adjacency lookup per draw per map, which means holding every map open
at once. Instead a POOL is drawn in seed order, every candidate is tested against each map in a
single pass over that map, and the pool is then walked IN DRAW ORDER taking the first 200
candidates adjacent in no map. That is exactly "draw, discard if adjacent, draw again" — the same
sequence, with the tests batched — and it is deterministic under the fixed seed. If the pool runs
out the pool is extended with the next block from the same generator, never reseeded.

Maps are opened ONE AT A TIME. Nine `GraphStore`s at once is gigabytes for no reason.

    uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_pairset.py
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))

import artistpath_api.graph_store as gs  # noqa: E402

from s4_common import sha256_of  # noqa: E402

ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
SERVED = Path(r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin")
SEED = 20260914
N_PAIRS = 200
POOL_BLOCK = 2000

# `LBA-A1` and `LBA-A3` are the reused arms (`LBA-D9`); the rest are stage 2's, and only those
# actually built are included — a cell `LBA-G2` stopped is absent, which is what "every BUILT arm"
# means.
REUSED = {"LBA-A1": ARTIFACTS / "LBD-A0V.bin", "LBA-A3": ARTIFACTS / "LBD-A5V.bin"}
BUILT_CANDIDATES = ["A2", "A4", "A5", "A6", "A7", "A8", "A9"]


def maps_in_play() -> dict[str, Path]:
    out = dict(REUSED)
    for arm in BUILT_CANDIDATES:
        path = ARTIFACTS / f"LBA-{arm}.bin"
        result = HERE / f"s4_build_{arm}.json"
        if not result.exists():
            continue
        record = json.loads(result.read_text(encoding="utf-8"))
        if record.get("status") == "unbuilt for a resource reason":
            continue
        if not path.exists():
            raise SystemExit(f"REFUSING: {result.name} reports a build but {path} is absent")
        out[f"LBA-{arm}"] = path
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "s4_pairset.json")
    args = ap.parse_args(argv)

    arms = maps_in_play()
    print(f"[pairset] maps in play: served + {', '.join(sorted(arms))}", flush=True)

    # --- pass 1: the common artist set -----------------------------------------------------------
    common: set[str] | None = None
    per_map = {}
    for label, path in [("served", SERVED), *sorted(arms.items())]:
        store = gs.GraphStore.load(path)
        mbids = set(store.mbids)
        per_map[label] = len(mbids)
        common = mbids if common is None else (common & mbids)
        del store
        print(f"[pairset] {label}: {len(mbids):,} artists  running intersection {len(common):,}", flush=True)
    assert common is not None
    pool_source = sorted(common)
    if len(pool_source) < 2:
        raise SystemExit("REFUSING: the common artist set is too small to draw a pair from")

    # --- draw the pool, in seed order -------------------------------------------------------------
    rng = random.Random(SEED)
    candidates: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    while len(candidates) < POOL_BLOCK:
        a = rng.choice(pool_source)
        b = rng.choice(pool_source)
        if a == b:
            continue
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(key)

    # --- test every candidate against every map, one map at a time --------------------------------
    adjacent_in_any = [False] * len(candidates)
    adjacency_by_map: dict[str, int] = {}
    for label, path in [("served", SERVED), *sorted(arms.items())]:
        store = gs.GraphStore.load(path)
        index = {m: i for i, m in enumerate(store.mbids)}
        hits = 0
        for k, (a, b) in enumerate(candidates):
            ia, ib = index[a], index[b]
            lo, hi = store.offsets[ia], store.offsets[ia + 1]
            if ib in store.neighbours[lo:hi]:
                if not adjacent_in_any[k]:
                    adjacent_in_any[k] = True
                hits += 1
        adjacency_by_map[label] = hits
        del store, index
        print(f"[pairset] {label}: {hits} of {len(candidates)} pool candidates are adjacent", flush=True)

    kept = [c for c, adj in zip(candidates, adjacent_in_any) if not adj][:N_PAIRS]
    if len(kept) < N_PAIRS:
        raise SystemExit(f"REFUSING: only {len(kept)} non-adjacent pairs in a pool of {len(candidates)} — "
                         f"extend POOL_BLOCK from the same generator rather than reseeding")

    lines = [f"{a}\t{b}" for a, b in kept]
    pair_file = HERE / "s4_pairset.tsv"
    pair_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pair_sha = sha256_of(pair_file)

    record = {
        "task": "LBA-M1 query-cost pair set",
        "rule": ("200 pairs, random.Random(20260914), from the artists present in EVERY built arm "
                 "and in the served map; a pair adjacent in ANY map is redrawn"),
        "seed": SEED,
        "n_pairs": len(kept),
        "pool_drawn": len(candidates),
        "pool_adjacent_in_at_least_one_map": sum(adjacent_in_any),
        "adjacent_candidates_by_map": adjacency_by_map,
        "maps": {label: str(path) for label, path in [("served", SERVED), *sorted(arms.items())]},
        "artists_per_map": per_map,
        "common_artists": len(pool_source),
        "pair_file": str(pair_file),
        "pair_file_sha256": pair_sha,
        "drawn_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha256_of(Path(__file__)),
        "note": "Written and sha-pinned BEFORE any timing is taken (§4).",
    }
    args.out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"[pairset] {len(kept)} pairs -> {pair_file.name}  sha256 {pair_sha}", flush=True)
    print(f"[pairset] common artists across every map: {len(pool_source):,}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
