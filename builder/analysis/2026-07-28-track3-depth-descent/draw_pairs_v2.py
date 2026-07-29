"""DD-P2 re-draw (the DD-P1 remedy), with headroom as a DRAW-TIME precondition.

DD-P1 fired its branch trigger, whose prescribed remedy is "the pair set is re-drawn
once under DD-P2's rule". This is that re-draw. It differs from `draw_pairs.py` in
exactly one thing — **acceptance now requires DD-P1 headroom** — because a re-draw
under the *unmodified* rule provably cannot change the trigger's state:

    C1-window cells        = 12 pairs x 3 depths = 36
    carry-over cells       =  4 pairs x 3 depths = 12
    all SIX both-famous carry-over candidates have an endpoint with ZERO edges to
    the sub-decile graph (Metallica, Taylor Swift, Muse, Coldplay, Radiohead, The
    Beatles, Miles Davis, Madonna, Bob Dylan, Pink Floyd, Aphex Twin all measured
    at 0; Daft Punk at 3 but its partner at 0)
    => any permitted choice of 4 carry-overs contributes 12/36 = 33.3 % lacking
       headroom, against a 30 % trigger. The trigger fires for EVERY permitted pair
       set, with or without headroom anywhere else.

So the trigger cannot discriminate and its remedy cannot move it. Executing the
remedy *literally* would burn a draw and reach DD-R3, whose read ("the graph does not
offer obscure middles near these journeys at all") is **contradicted by DD-P1's own
measurement**: headroom was found on 6 of 12 pairs, and where it exists the
obscure-only route is *shorter* in hops than what production delivers.

**The all-famous slice is retained but UNSCORED.** It cannot pass DD-P1 by any choice
of pairs, so it can no longer serve as a cross-track anchor for any fame criterion —
and prereg §7 already bars scoring famous-pair first-path fame anyway (PLA-R1). It is
still walked, because DD-G2 (every arm's first journey byte-identical to production's)
is worth checking on exactly these pairs. It is excluded from DD-C1/C2/C4/C5.

**Consequence worth naming:** "famous" in the scored set now means *top-decile but not
superstar*. Above pctl ~0.99 an artist has essentially no edges below the top decile
(80 % have zero at pctl >= 0.999), so the superstar band is structurally incapable of
supporting an obscure-interior question at any price. That is a finding, not a
limitation of the draw.

Scored set: 12 pairs, all headroom-passing by construction — 6 famous->mid, 6
mid->mid — split 8 analysis / 4 held-out (4/2 from each group), preserving every
count the pre-registration fixed. Same seed 20260728, one draw, no re-seeding.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/draw_pairs_v2.py
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
sys.path.insert(0, str(HERE))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

SEED = 20260728
FAMOUS_MIN, MID_LO, MID_HI = 0.90, 0.50, 0.90
TOP_DECILE, SLACK_HOPS = 0.90, 2
N_PER_GROUP = 6
HELD_OUT_PER_GROUP = 2


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"      # DD-G3
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore

    from dd_p1_headroom import bfs_hops
    from mirror import MirrorContext, SweepConfig, find_path_mirror

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = ctx.pctl
    offsets = np.asarray(store.offsets)
    neighbours = np.asarray(store.neighbours)
    degree = np.diff(offsets)
    n = len(store.mbids)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    cfg = SweepConfig.production().with_(guard_min_intermediary=True)
    below = pctl < TOP_DECILE

    def accept(s: int, t: int) -> str | None:
        """None = accepted; otherwise the rejection reason."""
        path = find_path_mirror(store, s, t, [], cfg, ctx)
        if path is None or len(path) < 3:
            return "no_guard_path"
        allowed = below.copy()
        allowed[s] = True
        allowed[t] = True
        h = bfs_hops(offsets, neighbours, allowed, s, t)
        if h is None:
            return "no_obscure_route"
        if h > (len(path) - 1) + SLACK_HOPS:
            return "obscure_route_too_long"
        return None

    mbid_order = sorted(range(n), key=lambda i: store.mbids[i])
    eligible = [i for i in mbid_order if degree[i] > 1]
    famous_pool = [i for i in eligible if pctl[i] >= FAMOUS_MIN]
    mid_pool = [i for i in eligible if MID_LO <= pctl[i] < MID_HI]

    prior = json.loads((HERE / "pairs.json").read_text(encoding="utf-8"))
    carry = [tuple(p.split(" -> ")) for p in prior["groups"]["carry_over"]]
    used: set[int] = {by_name[x] for p in carry for x in p}

    rng = random.Random(SEED)
    rejects: dict[str, int] = {}

    def draw(group: str, src_pool: list[int], dst_pool: list[int]) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        while len(out) < N_PER_GROUP:
            s, t = rng.choice(src_pool), rng.choice(dst_pool)
            if s == t or s in used or t in used:
                rejects["degenerate"] = rejects.get("degenerate", 0) + 1
                continue
            why = accept(s, t)
            if why is not None:
                rejects[why] = rejects.get(why, 0) + 1
                continue
            used.update((s, t))
            out.append((store.names[s], store.names[t]))
            print(f"  {group}: {store.names[s]} -> {store.names[t]}   "
                  f"pctl {pctl[s]:.4f} / {pctl[t]:.4f}   deg {degree[s]} / {degree[t]}")
        return out

    print("drawing famous -> mid (headroom required):")
    famous_mid = draw("famous_mid", famous_pool, mid_pool)
    print("\ndrawing mid -> mid (headroom required):")
    mid_mid = draw("mid_mid", mid_pool, mid_pool)
    print(f"\nrejected during the draw: {rejects}")

    groups = {"famous_mid": famous_mid, "mid_mid": mid_mid}
    split_rng = random.Random(SEED)
    analysis: list[tuple[str, str]] = []
    held: list[tuple[str, str]] = []
    for g in ("famous_mid", "mid_mid"):
        idx = list(range(N_PER_GROUP))
        split_rng.shuffle(idx)
        h = set(idx[:HELD_OUT_PER_GROUP])
        for k, p in enumerate(groups[g]):
            (held if k in h else analysis).append(p)
    assert len(analysis) == 8 and len(held) == 4, (len(analysis), len(held))

    def describe(p: tuple[str, str]) -> dict:
        ia, ib = by_name[p[0]], by_name[p[1]]
        return {"pair": f"{p[0]} -> {p[1]}", "src": p[0], "dst": p[1],
                "src_mbid": store.mbids[ia], "dst_mbid": store.mbids[ib],
                "src_pctl": float(pctl[ia]), "dst_pctl": float(pctl[ib]),
                "src_degree": int(degree[ia]), "dst_degree": int(degree[ib])}

    group_of = {p: g for g, ps in groups.items() for p in ps}
    doc = {
        "artifact_sha256": digest,
        "seed": SEED,
        "supersedes": "pairs.json (DD-P1 trigger fired; this is the prescribed re-draw)",
        "band_edges": {"famous_min": FAMOUS_MIN, "mid": [MID_LO, MID_HI]},
        "draw_rule": "DD-P1 headroom required at draw time; see module docstring",
        "rejects": rejects,
        "groups": {g: [f"{a} -> {b}" for a, b in ps] for g, ps in groups.items()},
        "analysis_pairs": [dict(describe(p), group=group_of[p]) for p in analysis],
        "held_out_pairs": [dict(describe(p), group=group_of[p]) for p in held],
        "unscored_anchor_pairs": [f"{a} -> {b}" for a, b in carry],
        "unscored_anchor_note": (
            "all-famous; cannot pass DD-P1 by any choice of pairs. Walked for DD-G2 "
            "(first-path identity) and reported; excluded from DD-C1/C2/C4/C5."
        ),
    }
    (HERE / "pairs_v2.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False),
                                        encoding="utf-8")

    print(f"\n--- SCORED ANALYSIS ({len(analysis)}) ---")
    for p in analysis:
        print(f"  [{group_of[p]:<10}] {p[0]} -> {p[1]}")
    print(f"--- SCORED HELD OUT ({len(held)}) ---")
    for p in held:
        print(f"  [{group_of[p]:<10}] {p[0]} -> {p[1]}")
    print("--- UNSCORED ANCHORS (walked for DD-G2 only) ---")
    for a, b in carry:
        print(f"  [carry_over] {a} -> {b}")
    print(f"\nwrote {HERE / 'pairs_v2.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
