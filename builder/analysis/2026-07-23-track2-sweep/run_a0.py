"""Step 4: A0 vs P — the gate that decides the factorial's shape.

Pre-registration §1.4: A0 is P's weights with `w_floor = 0`, and the **pre-registered
expectation is path-identity to P on the full pair × depth grid**. If identity fails, the
floor is already live on this artifact, adjudication claim 23 does not transfer, and the
factorial must be re-anchored with floor as a fully crossed column — a design revision to
be recorded as a dated amendment BEFORE proceeding (execution log, Track 2 ordering).

Run as a gate, before the other arms — analyst **O7**/**PR-A**. PR-A also asks for the
fraction of examined relaxations carrying a non-zero floor term alongside the identity
result, so that "identity holds but the term is firing" is visible rather than inferred.

**Guard G is ON in both arms** (step 3), per §1.2. Note the consequence recorded as
analyst O8: with G applied to P, this is no longer a comparison against shipped
behaviour on the two direct-edge pairs. The byte-identity check against shipped
`find_path` was step 2, with G off.

Run from `api/`:
    UV_LINK_MODE=copy uv run python ../builder/analysis/2026-07-23-track2-sweep/run_a0.py
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

from verify_mirror import ANALYSIS_PAIRS, HELD_OUT_PAIRS  # noqa: E402


def walk(store, src, dst, cfg, ctx, pop, find_path_mirror, Exclusion, KNOWN, stats=None):
    """Scripted all-`known` walk; returns the path at each depth 0..MAX_DEPTH."""
    excludes: list = []
    out: list[list[int] | None] = []
    for _ in range(MAX_DEPTH + 1):
        path = find_path_mirror(store, src, dst, excludes, cfg, ctx, stats)
        out.append(path)
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break
        victim = min(interior, key=lambda v: (-pop[v], v))
        excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
    return out


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, SweepConfig, find_path_mirror

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    P = SweepConfig.production().with_(guard_min_intermediary=True)
    A0 = P.with_(w_floor=0.0)
    print(f"P : w_floor={P.w_floor}  floor_mode={P.floor_mode}  guard_G={P.guard_min_intermediary}")
    print(f"A0: w_floor={A0.w_floor}  floor_mode={A0.floor_mode}  guard_G={A0.guard_min_intermediary}\n")

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    stats = {"examined": 0, "floor_active": 0}
    total = identical = 0
    divergences: list[str] = []
    infeasible: list[str] = []

    for label, pairs in (("analysis", ANALYSIS_PAIRS), ("held-out", HELD_OUT_PAIRS)):
        print(f"--- {label} set ---")
        for a, b in pairs:
            src, dst = by_name[a], by_name[b]
            per_pair = {"examined": 0, "floor_active": 0}
            p_paths = walk(store, src, dst, P, ctx, pop, find_path_mirror,
                           Exclusion, KNOWN, per_pair)
            a0_paths = walk(store, src, dst, A0, ctx, pop, find_path_mirror,
                            Exclusion, KNOWN)
            stats["examined"] += per_pair["examined"]
            stats["floor_active"] += per_pair["floor_active"]

            n = min(len(p_paths), len(a0_paths))
            first_div = None
            for d in range(n):
                total += 1
                if p_paths[d] == a0_paths[d]:
                    identical += 1
                elif first_div is None:
                    first_div = d
            if len(p_paths) != len(a0_paths):
                first_div = first_div if first_div is not None else n
            if None in p_paths:
                infeasible.append(f"{a} -> {b} @ d{p_paths.index(None)} (P)")

            frac = 100.0 * per_pair["floor_active"] / max(1, per_pair["examined"])
            flag = "IDENTICAL" if first_div is None else f"DIVERGES @ d{first_div}"
            print(f"  {a:>19} -> {b:<16} depths={len(p_paths):>2}  {flag:<16}"
                  f"  floor-term live on {frac:5.2f} % of relaxations")
            if first_div is not None:
                divergences.append(
                    f"{a} -> {b} @ d{first_div}\n"
                    f"      P : {p_paths[first_div] if first_div < len(p_paths) else '<walk ended>'}\n"
                    f"      A0: {a0_paths[first_div] if first_div < len(a0_paths) else '<walk ended>'}"
                )

    pct = 100.0 * stats["floor_active"] / max(1, stats["examined"])
    print(f"\ncells compared: {total}   identical: {identical}")
    print(f"PR-A: P examined {stats['examined']:,} relaxations; "
          f"floor term non-zero on {stats['floor_active']:,} ({pct:.2f} %)")
    if infeasible:
        print("\nguard-infeasible cells (analyst D7):")
        for s in infeasible:
            print(f"  - {s}")

    if divergences:
        print(f"\n*** A0 != P on {len(divergences)} pair(s) ***")
        print("Claim 23 does not transfer. Per section 1.4 the factorial must be")
        print("re-anchored with floor as a fully crossed column, recorded as a dated")
        print("amendment BEFORE any further arm runs.")
        for d in divergences:
            print(f"  {d}")
        return 1

    print("\nA0 == P on every cell. Pre-registered expectation MET:")
    print("the floor does not change outcomes on this artifact, so it is safe as a")
    print("held-constant column and the 2x2x2 factorial stands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
