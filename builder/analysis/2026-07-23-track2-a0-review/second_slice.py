"""Stability check for the carry-over finding, on a second slice.

`floor_asymmetry.py` measures under the pre-registered victim policy (most-popular
interior). Metrics in this project have reversed sign between slices, so the carry-over
finding — floor-ON and floor-OFF twins still differing at d >= 10 despite the floor term
being identically zero there — is re-measured under a DIFFERENT, deliberately opposite
deterministic victim policy: **least**-popular interior, ties -> lowest node id.

This is an OFF-PROTOCOL robustness check on a mechanical quantity. It is not a sweep arm,
scores nothing, and its paths are not offered as evidence about any criterion.

Run from `api/`:
    PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \
        ../builder/analysis/2026-07-23-track2-a0-review/second_slice.py
"""

import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
MAX_DEPTH = 20
FAMILIES = [("P", "A0"), ("A6r", "A6"), ("Xr", "X")]


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from verify_mirror import ANALYSIS_PAIRS, HELD_OUT_PAIRS

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    prod = SweepConfig.production().with_(guard_min_intermediary=True)
    ARMS = {
        "P": prod,
        "A0": prod.with_(floor_mode="off", w_floor=0.0),
        "A6r": prod.with_(w_jump=0.3, w_sim=1.5),
        "A6": prod.with_(w_jump=0.3, w_sim=1.5, floor_mode="off", w_floor=0.0),
        "Xr": prod.with_(jump_currency="pctl", w_jump=0.0, w_sim=1.5),
        "X": prod.with_(jump_currency="pctl", w_jump=0.0, w_sim=1.5,
                        floor_mode="off", w_floor=0.0),
    }

    def walk(src, dst, cfg):
        excludes: list = []
        out = []
        for _ in range(MAX_DEPTH + 1):
            path = find_path_mirror(store, src, dst, excludes, cfg, ctx)
            out.append(path)
            if path is None:
                break
            interior = path[1:-1]
            if not interior:
                break
            victim = min(interior, key=lambda v: (pop[v], v))   # LEAST popular
            excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
        return out

    PAIRS = list(ANALYSIS_PAIRS) + list(HELD_OUT_PAIRS)
    res = {k: {} for k in ARMS}
    for a, b in PAIRS:
        for nm, cfg in ARMS.items():
            res[nm][f"{a} -> {b}"] = walk(by_name[a], by_name[b], cfg)

    print("\n=== SECOND SLICE (victim = LEAST-popular interior) ===")
    print("cells where floor-ON != floor-OFF, by depth (12 pairs)")
    print(f"{'depth':>5} " + " ".join(f"{on + ' vs ' + off:>14}" for on, off in FAMILIES))
    for d in range(0, 21):
        cells = []
        for on, off in FAMILIES:
            diff = tot = 0
            for key in res[on]:
                if d < len(res[on][key]) and d < len(res[off][key]):
                    tot += 1
                    if res[on][key][d] != res[off][key][d]:
                        diff += 1
            cells.append(f"{diff}/{tot}")
        print(f"{'d' + str(d):>5} " + " ".join(f"{c:>14}" for c in cells))

    print("\npairs still differing at d20:")
    for on, off in FAMILIES:
        names = [k for k in res[on]
                 if len(res[on][k]) > 20 and len(res[off][k]) > 20
                 and res[on][k][20] != res[off][k][20]]
        print(f"  {on} vs {off}: {names if names else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
