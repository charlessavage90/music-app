"""THE GATE: the mirror must reproduce production `find_path` byte-identically.

Track 2 execution order step 2. Log §3.10 is explicit that non-identical paths mean
**stop, the harness is wrong** — and per the pre-registration §1.2 note (guards G5a),
that instruction applies to THIS step only, with **guard G disabled**. G is enabled
uniformly afterwards, in step 3.

Protocol per pair: walk the scripted bypass policy (all-`known`, victim = most-popular
interior by in-graph popularity, ties → lowest node id) up to 20 bypasses. At every
depth, call production `find_path` and the mirror with a production-equivalent config
and compare the returned node lists exactly. The exclusion sequence is driven by
production's paths, so the two are asked to answer identical questions.

A pair whose d0 path is a direct edge has no interior and therefore no victim; with
guard G off the walk simply ends at d0. That is expected for the two F1 pairs and is
reported, not treated as a failure.

Run from `api/`:
    UV_LINK_MODE=copy uv run python ../builder/analysis/2026-07-23-track2-sweep/verify_mirror.py
"""

import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

MAX_DEPTH = 20

ANALYSIS_PAIRS = [
    ("Miles Davis", "Daft Punk"),
    ("The Shins", "Wishbone Ash"),
    ("Metallica", "Taylor Swift"),
    ("Radiohead", "The Beatles"),
    ("Muse", "Coldplay"),
    ("Madonna", "Bob Dylan"),
    ("Pink Floyd", "Aphex Twin"),
    ("Nirvana", "CROOVE"),          # pair 8, substituted per amendment A7
]
HELD_OUT_PAIRS = [
    ("Arctic Monkeys", "Johnny Cash"),
    ("Michael Jackson", "Gorillaz"),
    ("System of a Down", "R.E.M."),
    ("The Rolling Stones", "Linkin Park"),
]


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.config import ApiConfig
    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion, find_path

    from mirror import SweepConfig, MirrorContext, find_path_mirror

    store = GraphStore.load(GRAPH)
    cfg = ApiConfig()
    ctx = MirrorContext.build(store)
    mcfg = SweepConfig.production()          # must equal ApiConfig's cost exactly
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    total_cells = 0
    mismatches: list[str] = []
    short_walks: list[str] = []

    for label, pairs in (("analysis", ANALYSIS_PAIRS), ("held-out", HELD_OUT_PAIRS)):
        print(f"--- {label} set ---")
        for a, b in pairs:
            src, dst = by_name[a], by_name[b]
            excludes: list[Exclusion] = []
            depth = 0
            while depth <= MAX_DEPTH:
                prod = find_path(store, src, dst, excludes, cfg)
                mine = find_path_mirror(store, src, dst, excludes, mcfg, ctx)
                total_cells += 1
                if prod != mine:
                    mismatches.append(
                        f"{a} -> {b} @ d{depth}\n"
                        f"    prod: {prod}\n"
                        f"    mine: {mine}"
                    )
                    break
                if prod is None:
                    short_walks.append(f"{a} -> {b}: no path at d{depth}")
                    break
                interior = prod[1:-1]
                if not interior:
                    short_walks.append(
                        f"{a} -> {b}: direct edge, no interior at d{depth} "
                        f"(expected with guard G off)"
                    )
                    break
                victim = min(interior, key=lambda v: (-pop[v], v))
                excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
                depth += 1
            print(f"  {a} -> {b}: {depth} bypasses walked")

    print(f"\ncells compared: {total_cells}")
    if short_walks:
        print("\nwalks that ended early (not failures):")
        for s in short_walks:
            print(f"  - {s}")

    if mismatches:
        print(f"\n*** MISMATCH in {len(mismatches)} pair(s) — STOP, THE HARNESS IS WRONG ***")
        for m in mismatches:
            print(f"  {m}")
        return 1

    print("\nBYTE-IDENTICAL on every cell. Gate passed (guard G off).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
