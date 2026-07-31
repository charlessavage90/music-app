"""TD-4: are the edges a reranking deletes the edges journeys route through?

Motivation
----------
TD-2 measured a population deletion rate: at 2 swaps of 50, ~4-5% of the
graph's edges disappear. But mutuality falls steeply with rank position
(0.510 at list positions 0-5, 0.264 at 45-50), and a reranking's deletions sit
near the k=50 boundary. Routed paths were HYPOTHESISED to prefer
high-similarity edges sitting near the TOP of both endpoints' lists, which
would make path-carrying edges much safer than the population figure. That was
unmeasured. This measures it, and reports the rank-position profile of routed
edges against all edges so the hypothesis is testable rather than assumed.

Quantity: the SAFETY RATIO = (deletion rate among edges routes traverse) /
(deletion rate over all edges). 1.0 means routes are hit exactly as often as
chance; below 1.0 means routes are protected; above 1.0 means routes are
preferentially damaged. The population rate is the null model.

ONE SUBSTRATE FOR BOTH HALVES
-----------------------------
Selection simulation AND routing both run on the Track B ALG-E MK50 cell
(`ALG-E-mutual_knn-k50.bin`, sha 73feffa0...a69faa). The adopted artifact
cannot be reproduced from the pipeline capture (it predates the nameless-artist
drop), so using it for routing and the capture for selection would put the two
halves on different node sets. Its counts are reported for context and the
delta is stated, never assumed away. A green check asserts the simulated
selection reproduces the substrate's edge set EXACTLY before anything is
scored.

PAIR SET
--------
This is INSTRUMENT CALIBRATION, not a `TAS-` criterion. It uses its own seed,
`20260730-tdcal`, deliberately NOT the pre-registered `TAS-5` seed
(`20260730-tas`), so this run does not consume the pre-registered draw. The
three class definitions mirror the spec §3 ones so the results read in the same
terms, over the ADOPTED artifact's percentile fame frame as a fixed reference
population (`fame_frame` in cb_metrics, sha-asserted there):

    ff   both endpoints at percentile >= 0.99
    fo   one endpoint >= 0.99, one < 0.50
    oo   both endpoints < 0.50

FAME IS POPULARITY HERE, NOT DEGREE. The frame is the percentile rank of
`pop_raw`; degree is a different quantity and is not used for class membership.

STABILITY
---------
Every arm's safety ratio is also computed on two disjoint halves of the pair
set (even- and odd-indexed pairs). A ratio that does not reproduce across the
two halves is reported as unstable rather than quoted as a point estimate.

ROUTING
-------
`find_journey`, not `find_path` — the app calls `find_journey` (F1, every
journey gets at least one stop), so the edges a user actually traverses are
the ones this collects. `find_path` is collected alongside for comparison
because the pre-registered harness calls it. Production `ApiConfig()` weights,
no bypass signals, no exclusions.

Run from `builder/` (after td_capture.py):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/td_pathedges.py \
        --capture <path.npz> --per-class 300
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
SCRATCH = HERE.parent.parent / "scratch"
TRACK_B = HERE.parent / "2026-07-30-track-b-cap-selection"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(TRACK_B))
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "src"))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_journey, find_path  # noqa: E402

from cb_metrics import fame_frame  # noqa: E402
from td_turnover import (  # noqa: E402
    K,
    Capture,
    mask_window,
    mutual_undirected,
)

SUBSTRATE = SCRATCH / "cb-cells" / "ALG-E-mutual_knn-k50.bin"
SUBSTRATE_SHA = "73feffa03856f55dda134b84aa5ee40073495ae16f27e8116a4d961b65a69faa"
ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
SEED = "20260730-tdcal"  # NOT the pre-registered TAS-5 seed
CLASSES = ("ff", "fo", "oo")


def draw_pairs(frame: dict[str, float], present: set[str],
               per_class: int) -> list[tuple[str, str, str]]:
    """(class, a, b) triples. Own seed; mirrors spec §3's class definitions."""
    rng = random.Random(SEED)
    famous, lower = [], []
    for mbid in sorted(present):
        p = frame.get(mbid)
        if p is None:
            continue
        if p >= 0.99:
            famous.append(mbid)
        elif p < 0.50:
            lower.append(mbid)
    out: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    counts = {c: 0 for c in CLASSES}

    def add(cls: str, a: str, b: str) -> None:
        row = (cls, a, b)
        if a != b and row not in seen and counts[cls] < per_class:
            seen.add(row)
            counts[cls] += 1
            out.append(row)

    while any(counts[c] < per_class for c in CLASSES):
        add("ff", rng.choice(famous), rng.choice(famous))
        add("fo", rng.choice(famous), rng.choice(lower))
        add("oo", rng.choice(lower), rng.choice(lower))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--per-class", type=int, default=300)
    ap.add_argument("--out", default=str(HERE / "td_pathedges.json"))
    args = ap.parse_args()

    payload = SUBSTRATE.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    assert sha == SUBSTRATE_SHA, f"substrate sha mismatch: {sha}"
    store = GraphStore.from_bytes(payload)

    cap = Capture(Path(args.capture))
    base_mask = cap.pos < K
    base_edges = mutual_undirected(cap, base_mask)
    cid = {m: i for i, m in enumerate(cap.mbids)}

    keep = np.zeros(cap.n, dtype=bool)
    store_cid = np.array([cid[m] for m in store.mbids], dtype=np.int64)
    keep[store_cid] = True
    eu, ev = base_edges // cap.n, base_edges % cap.n
    sim_in = base_edges[keep[eu] & keep[ev]]
    src = np.repeat(store_cid, np.diff(store.offsets))
    dst = store_cid[store.neighbours.astype(np.int64)]
    sel = src < dst
    art_keys = np.sort(src[sel] * cap.n + dst[sel])
    green = bool(art_keys.size == sim_in.size and np.array_equal(art_keys, sim_in))
    assert green, "simulated selection does not reproduce the substrate exactly"

    gad = GraphStore.from_bytes(ADOPTED.read_bytes())
    assert hashlib.sha256(ADOPTED.read_bytes()).hexdigest() == ADOPTED_SHA

    report: dict = {
        "substrate": {
            "file": SUBSTRATE.name, "sha256": sha,
            "artists": int(store.artist_count),
            "undirected_edges": int(art_keys.size),
        },
        "adopted_for_context": {
            "file": ADOPTED.name, "sha256": ADOPTED_SHA,
            "artists": int(gad.artist_count),
            "undirected_edges": int(gad.neighbours.size // 2),
            "artists_delta_vs_substrate": int(gad.artist_count - store.artist_count),
            "edges_delta_vs_substrate": int(gad.neighbours.size // 2 - art_keys.size),
        },
        "green_check_selection_reproduces_substrate": green,
        "pair_seed": SEED,
        "pair_seed_note": "not the pre-registered TAS-5 seed 20260730-tas",
    }

    frame = fame_frame()
    present = set(store.mbids)
    triples = draw_pairs(frame, present, args.per_class)
    cfg = ApiConfig()

    t0 = time.monotonic()
    per_pair: list[dict] = []
    stop_rules: Counter = Counter()
    for i, (cls, a, b) in enumerate(triples):
        sa, sb = store.id_by_mbid[a], store.id_by_mbid[b]
        res = find_journey(store, sa, sb, [], cfg)
        assert res is not None, "no path with no exclusions: impossible in the LCC"
        path, rule = res
        stop_rules[rule] += 1

        def to_keys(p: list[int]) -> list[int]:
            out = []
            for u, v in zip(p, p[1:]):
                cu, cv = int(store_cid[u]), int(store_cid[v])
                out.append(min(cu, cv) * cap.n + max(cu, cv))
            return out

        fp = find_path(store, sa, sb, [], cfg)
        per_pair.append({"cls": cls, "a": a, "b": b, "rule": rule,
                         "hops": len(path) - 1, "keys": to_keys(path),
                         "fp_keys": to_keys(fp),
                         "nodes": [int(store_cid[x]) for x in path]})
        if (i + 1) % 100 == 0:
            print(f"routed {i + 1}/{len(triples)} "
                  f"({time.monotonic() - t0:.0f}s)", flush=True)

    def counters(pairs: list[dict], field: str = "keys") -> dict[str, Counter]:
        out = {c: Counter() for c in CLASSES}
        for p in pairs:
            out[p["cls"]].update(p[field])
        return out

    routed = counters(per_pair)
    routed_fp = counters(per_pair, "fp_keys")
    half_a = counters([p for i, p in enumerate(per_pair) if i % 2 == 0])
    half_b = counters([p for i, p in enumerate(per_pair) if i % 2 == 1])

    def pooled(d: dict[str, Counter]) -> Counter:
        c = Counter()
        for k in CLASSES:
            c.update(d[k])
        return c

    all_routed, all_fp = pooled(routed), pooled(routed_fp)
    all_a, all_b = pooled(half_a), pooled(half_b)

    report["routing"] = {
        "pairs": len(triples),
        "per_class": {c: sum(1 for t in triples if t[0] == c) for c in CLASSES},
        "stop_rules_find_journey": dict(stop_rules),
        "mean_hops": round(float(np.mean([p["hops"] for p in per_pair])), 3),
        "mean_hops_by_class": {
            c: round(float(np.mean([p["hops"] for p in per_pair if p["cls"] == c])), 3)
            for c in CLASSES},
        "seconds": round(time.monotonic() - t0, 1),
    }
    report["routed_edges"] = {
        "unique_find_journey": len(all_routed),
        "traversals_find_journey": sum(all_routed.values()),
        "unique_find_path": len(all_fp),
        "unique_by_class": {c: len(routed[c]) for c in CLASSES},
    }

    key_all = np.sort(cap.s_key)
    pos_sorted = cap.pos[np.argsort(cap.s_key)]

    def positions(keys: np.ndarray) -> dict:
        u, v = keys // cap.n, keys % cap.n
        p1 = pos_sorted[np.searchsorted(key_all, u * cap.n + v)]
        p2 = pos_sorted[np.searchsorted(key_all, v * cap.n + u)]
        worse = np.maximum(p1, p2)
        return {
            "edges": int(keys.size),
            "median_worse_position": float(np.median(worse)),
            "mean_worse_position": round(float(worse.mean()), 2),
            "share_worse_pos_ge_45": round(float((worse >= 45).mean()), 4),
            "share_worse_pos_lt_10": round(float((worse < 10).mean()), 4),
        }

    routed_keys = np.array(sorted(all_routed), dtype=np.int64)
    report["rank_position_profile"] = {
        "all_edges": positions(base_edges),
        "routed_edges": positions(routed_keys),
        "routed_edges_by_class": {
            c: positions(np.array(sorted(routed[c]), dtype=np.int64))
            for c in CLASSES},
    }

    arms: list[dict] = []
    specs = [("BND", n, n, None) for n in (1, 2, 3, 5, 10)]
    for n in (1, 2, 3, 5, 10):
        specs += [("W10-IND", n, 10, False), ("W10-SYM", n, 10, True),
                  ("UNI-IND", n, None, False), ("UNI-SYM", n, None, True)]

    node_on_route = np.zeros(cap.n, dtype=bool)
    for p in per_pair:
        node_on_route[p["nodes"]] = True

    for tag, n, window, sym in specs:
        label = f"{tag}-{n}"
        seed = {"BND": 0, "W10-IND": 101, "W10-SYM": 101,
                "UNI-IND": 202, "UNI-SYM": 202}[tag]
        new_edges = mutual_undirected(cap, mask_window(cap, n, window, seed, sym))
        alive = np.isin(base_edges, new_edges, assume_unique=True)
        deleted = base_edges[~alive]
        created = new_edges[~np.isin(new_edges, base_edges, assume_unique=True)]
        pop_rate = deleted.size / base_edges.size

        def rate(counter: Counter) -> tuple[float | None, float | None]:
            ks = np.array(sorted(counter), dtype=np.int64)
            if ks.size == 0:
                return None, None
            m = np.isin(ks, deleted, assume_unique=True)
            trav_hit = sum(counter[int(k)] for k in ks[m])
            return float(m.sum()) / ks.size, trav_hit / sum(counter.values())

        r_uni, r_trav = rate(all_routed)
        r_fp, _ = rate(all_fp)
        r_a, _ = rate(all_a)
        r_b, _ = rate(all_b)
        row = {
            "arm": label,
            "population_deletion_rate": round(pop_rate, 5),
            "population_creation_rate": round(created.size / base_edges.size, 5),
            "routed_unique_edges": len(all_routed),
            "routed_deletion_rate": round(r_uni, 5),
            "safety_ratio": round(r_uni / pop_rate, 3),
            "traversal_weighted_deletion_rate": round(r_trav, 5),
            "traversal_weighted_safety_ratio": round(r_trav / pop_rate, 3),
            "find_path_safety_ratio": round(r_fp / pop_rate, 3),
            "safety_ratio_half_a": round(r_a / pop_rate, 3),
            "safety_ratio_half_b": round(r_b / pop_rate, 3),
        }
        by_class = {}
        for c in CLASSES:
            rc, _ = rate(routed[c])
            ra, _ = rate(half_a[c])
            rb, _ = rate(half_b[c])
            by_class[c] = {
                "unique_edges": len(routed[c]),
                "deletion_rate": round(rc, 5),
                "safety_ratio": round(rc / pop_rate, 3),
                "safety_ratio_half_a": round(ra / pop_rate, 3),
                "safety_ratio_half_b": round(rb / pop_rate, 3),
            }
        row["by_class"] = by_class

        del_set = set(deleted.tolist())
        aff = {c: 0 for c in CLASSES}
        tot_c = {c: 0 for c in CLASSES}
        for p in per_pair:
            tot_c[p["cls"]] += 1
            if any(k in del_set for k in p["keys"]):
                aff[p["cls"]] += 1
        row["journeys_touching_a_deleted_edge"] = {
            c: {"n": aff[c], "of": tot_c[c], "share": round(aff[c] / tot_c[c], 4)}
            for c in CLASSES}
        row["journeys_touching_a_deleted_edge_pooled"] = round(
            sum(aff.values()) / sum(tot_c.values()), 4)

        cu, cv = created // cap.n, created % cap.n
        bu, bv = base_edges // cap.n, base_edges % cap.n
        created_near = float((node_on_route[cu] | node_on_route[cv]).mean())
        base_near = float((node_on_route[bu] | node_on_route[bv]).mean())
        row["created_incident_on_a_routed_node"] = round(created_near, 5)
        row["existing_incident_on_a_routed_node_null"] = round(base_near, 5)
        row["creation_enrichment_near_routes"] = round(created_near / base_near, 3)

        arms.append(row)
        print(f"{label:12} pop={pop_rate:.4f} routed={r_uni:.4f} "
              f"safety={row['safety_ratio']:.3f} "
              f"(a={row['safety_ratio_half_a']:.3f} b={row['safety_ratio_half_b']:.3f}) "
              f"journeys_hit={row['journeys_touching_a_deleted_edge_pooled']:.3f}",
              flush=True)

    report["arms"] = arms
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
