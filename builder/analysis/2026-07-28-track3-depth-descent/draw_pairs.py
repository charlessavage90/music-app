"""DD-P2 — the Track 3 pair set. Twelve pairs, fixed before any arm runs.

Pre-registration: `docs/superpowers/specs/2026-07-28-track3-depth-descent-preregistration.md` §4.

Two rules the pre-registration could not fix itself, resolved here and committed
BEFORE any arm (see the execution log, DD-P2):

**(1) The carry-over count.** DD-P2 says "the 4 Track 2 analysis pairs with famous
endpoints". Measured on the adopted artifact there are **6**, not 4 — the document
asserts something about the world that is not true. The count 4 is load-bearing (it
makes 12 pairs, the 8/4 split, and the deliberate minority of the all-famous slice);
*which* 4 is not. Rule adopted: **the first 4 both-famous pairs in the frozen
`ANALYSIS_PAIRS` order** in `2026-07-23-track2-sweep/verify_mirror.py`. That ordering
was committed 2026-07-23, before Track 3 existed, so it cannot have been chosen to
suit a Track 3 result — which is the only property the tie-break needs.

**(2) The held-out composition.** "8 analysis / 4 held-out, assigned by the same seed"
does not say how the four are spread. An unstratified draw can empty a group, so the
split is stratified: **2 carry-over, 1 famous->mid, 1 mid->mid** held out. Two of the
carry-overs go because the all-famous slice is the least informative for the owner's
goal — PLA-R1 showed famous-pair first paths are structurally forced, and famous-pair
first-path fame is *barred* as a criterion (§7) — and because the pre-registration's
own rationale wants that slice in the minority. Analysis therefore holds
2 all-famous / 3 famous->mid / 3 mid->mid, and each group keeps an anchor in both
halves. No criterion in the pre-registration reads the held-out set; it is
confirmatory only.

Band edges, half-open so the bands are disjoint:
    famous  pctl >= 0.90     (DD-P1's top decile)
    mid     pctl in [0.50, 0.90)

Exclusions (DD-P2): degree-1 endpoints, and any pair with no guard-compliant path.
The second subsumes `MKS-6` exactly — a no-detour pair is precisely one where guard G
cannot produce an interior — so it is tested directly rather than by table lookup.

Read-only w.r.t. shipped code. Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/draw_pairs.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

SEED = 20260728
FAMOUS_MIN = 0.90
MID_LO, MID_HI = 0.50, 0.90
N_PER_GROUP = 4

# Stratified held-out counts, per rule (2) above.
HELD_OUT = {"carry_over": 2, "famous_mid": 1, "mid_mid": 1}


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"      # DD-G3
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from verify_mirror import ANALYSIS_PAIRS

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = ctx.pctl
    degree = np.diff(store.offsets)
    n = len(store.mbids)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    # Guard G ON — the pair set must be drawable under the regime every arm walks in.
    guard_cfg = SweepConfig.production().with_(guard_min_intermediary=True)

    def guard_compliant(src: int, dst: int) -> bool:
        path = find_path_mirror(store, src, dst, [], guard_cfg, ctx)
        return path is not None and len(path) >= 3

    # ---- carry-over: first 4 both-famous pairs in the frozen Track 2 order ----
    carry: list[tuple[str, str]] = []
    for a, b in ANALYSIS_PAIRS:
        ia, ib = by_name[a], by_name[b]
        if pctl[ia] >= FAMOUS_MIN and pctl[ib] >= FAMOUS_MIN:
            carry.append((a, b))
    print(f"both-famous Track 2 analysis pairs found: {len(carry)}")
    for a, b in carry:
        print(f"    {a} -> {b}")
    assert len(carry) >= N_PER_GROUP, "fewer both-famous carry-over candidates than needed"
    carry = carry[:N_PER_GROUP]
    print(f"  -> carrying the first {N_PER_GROUP} in frozen order\n")

    # ---- deterministic draw for the two new groups ----
    # Sorted-MBID order is the base ordering (DD-P2), so the candidate lists do not
    # depend on artifact node numbering.
    mbid_order = sorted(range(n), key=lambda i: store.mbids[i])
    eligible = [i for i in mbid_order if degree[i] > 1]
    famous_pool = [i for i in eligible if pctl[i] >= FAMOUS_MIN]
    mid_pool = [i for i in eligible if MID_LO <= pctl[i] < MID_HI]
    print(f"pools (degree > 1): famous {len(famous_pool):,}   mid {len(mid_pool):,}\n")

    used: set[int] = {by_name[x] for p in carry for x in p}
    rng = random.Random(SEED)
    rejects = {"degenerate": 0, "no_guard_path": 0}

    def draw(group: str, src_pool: list[int], dst_pool: list[int]) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        while len(out) < N_PER_GROUP:
            s = rng.choice(src_pool)
            t = rng.choice(dst_pool)
            if s == t or s in used or t in used:
                rejects["degenerate"] += 1
                continue
            if not guard_compliant(s, t):
                rejects["no_guard_path"] += 1
                continue
            used.add(s)
            used.add(t)
            out.append((store.names[s], store.names[t]))
            print(f"  {group}: {store.names[s]} -> {store.names[t]}   "
                  f"pctl {pctl[s]:.4f} / {pctl[t]:.4f}   deg {degree[s]} / {degree[t]}")
        return out

    print("drawing famous -> mid:")
    famous_mid = draw("famous_mid", famous_pool, mid_pool)
    print("\ndrawing mid -> mid:")
    mid_mid = draw("mid_mid", mid_pool, mid_pool)
    print(f"\nrejected during the draw: {rejects}")

    groups = {"carry_over": carry, "famous_mid": famous_mid, "mid_mid": mid_mid}

    # ---- stratified held-out split, same seed ----
    split_rng = random.Random(SEED)
    analysis: list[tuple[str, str]] = []
    held: list[tuple[str, str]] = []
    for g in ("carry_over", "famous_mid", "mid_mid"):
        pairs = list(groups[g])
        idx = list(range(len(pairs)))
        split_rng.shuffle(idx)
        h = set(idx[: HELD_OUT[g]])
        for k, p in enumerate(pairs):
            (held if k in h else analysis).append(p)

    assert len(analysis) == 8 and len(held) == 4, (len(analysis), len(held))

    def describe(p: tuple[str, str]) -> dict:
        ia, ib = by_name[p[0]], by_name[p[1]]
        return {
            "pair": f"{p[0]} -> {p[1]}",
            "src": p[0], "dst": p[1],
            "src_mbid": store.mbids[ia], "dst_mbid": store.mbids[ib],
            "src_pctl": float(pctl[ia]), "dst_pctl": float(pctl[ib]),
            "src_degree": int(degree[ia]), "dst_degree": int(degree[ib]),
        }

    group_of = {p: g for g, ps in groups.items() for p in ps}
    doc = {
        "artifact_sha256": digest,
        "seed": SEED,
        "band_edges": {"famous_min": FAMOUS_MIN, "mid": [MID_LO, MID_HI]},
        "carry_over_rule": (
            "first 4 both-famous pairs in the frozen Track 2 ANALYSIS_PAIRS order; "
            "6 qualified, the pre-registration said 4"
        ),
        "held_out_rule": {"stratified": HELD_OUT},
        "rejects": rejects,
        "groups": {g: [f"{a} -> {b}" for a, b in ps] for g, ps in groups.items()},
        "analysis_pairs": [dict(describe(p), group=group_of[p]) for p in analysis],
        "held_out_pairs": [dict(describe(p), group=group_of[p]) for p in held],
    }
    out_path = HERE / "pairs.json"
    out_path.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\n--- ANALYSIS ({len(analysis)}) ---")
    for p in analysis:
        print(f"  [{group_of[p]:<10}] {p[0]} -> {p[1]}")
    print(f"--- HELD OUT ({len(held)}) ---")
    for p in held:
        print(f"  [{group_of[p]:<10}] {p[0]} -> {p[1]}")
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
