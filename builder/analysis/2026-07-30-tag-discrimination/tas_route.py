"""`TAS-5`: would a coherence term change the journeys the app builds?

SUBSTRATE: THE ADOPTED ARTIFACT (`TAS-AM2`). `TAS-5` asks what the APP routes
today, so it runs on `graph-t15-tiebreakfix.bin`, sha-asserted on load -- never on
the pre-cap `ALG-E` capture that `TAS-2`/`TAS-3`/`TAS-4` use. `TAS-AM2`'s standing
constraint: NO READ MAY COMPARE A CAPTURE-SIDE FIGURE AGAINST AN ARTIFACT-SIDE ONE.

THE PATHFINDER IS FORKED, NOT PATCHED. `find_path_coh` is a copy of
`api/src/artistpath_api/pathfinding.py`'s `find_path` with ONE added term:

    + w_coh * (1 - agreement(u, v))

`w_coh` DOES NOT EXIST in `ApiConfig` and this file does not propose adding one.
It is harness-local. Shipping it would be a config default change, which is an
adoption, which this probe does not license.

THE FORK OMITS `excludes`, `avoidance_map`, `effective_floor_raw` and
`forbidden_edge` because no arm uses a bypass. That omission is PROVED equivalent
by `TAS-AM5a` -- identical paths to production `find_path` at `w_coh = 0` over the
FULL §3 draw, on the real artifact -- not argued to be. **If `TAS-AM5a` fails,
nothing this file produces counts, and `main()` aborts rather than reporting.**

KILL for the router-side architecture: ONLY if journeys are unchanged in EVERY
class at EVERY weight. A pooled bar is explicitly rejected -- a small overall
change concentrated in famous-to-famous is a signal worth chasing, and
famous-to-famous is where `DD-F1` lives.

UNCHANGED means the identical artist sequence, in order, endpoints included. A
path of the same length through different artists is a change; so is the same set
in a different order. Path COST is NOT compared: it necessarily moves whenever
`w_coh > 0`, and reading that as an effect would be an artefact of the instrument.

STANDING CAUTION (§2): three consecutive attempts to change router behaviour by
changing prices returned nulls -- Track 2's repricing family, Track 3b's
thresholded toll, and Track B's `R2` (quota edges present and declined at
production weights). A `TAS-5` null is therefore WEAK evidence about tags
specifically and must NOT be reported as "tags do not work"; it is consistent with
"this router shrugs off new terms", which `TAS-3` and `TAS-4` are what distinguish
it from.

NO OUTCOME READ ON A PARTIAL GRID (§5). A half-run `TAS-5` is worth zero, not half.

Run from `builder/` (~10-15 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_route.py
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json

from tas_common import ADOPTED, ADOPTED_SHA, HERE, neutral_for, resolved_agreement
from tas_pairs import draw_pairs
from tas_tags import label_sets

OUT = HERE / "tas_route.json"
WEIGHT_MULTIPLES = [0.0, 0.25, 0.5, 1.0, 2.0]
CLASSES = ("ff", "fo", "oo")


def load_adopted():
    """The adopted artifact, sha-asserted. A wrong artifact looks like a right one."""
    from artistpath_api.graph_store import GraphStore

    payload = ADOPTED.read_bytes()
    got = hashlib.sha256(payload).hexdigest()
    if got != ADOPTED_SHA:
        raise SystemExit(f"artifact sha mismatch: expected {ADOPTED_SHA}, got {got}")
    return GraphStore.from_bytes(payload)


def _neutral_and_neighbours(store, u: int, labels: dict[str, set[str]]):
    """One artist's neighbour list, its own label set, and its per-artist neutral.

    THE NEUTRAL IS PER-ARTIST, VIA THE ONE RESOLUTION PATH -- not a hardcoded
    constant. An earlier draft in the implementation plan inlined a constant here,
    which would have made the routing arm use a different neutral rule from the
    selection arm while both documents claimed they shared one.
    """
    neighbours = list(store.neighbours_of(u))
    u_set = labels.get(store.mbids[u], set())
    cand_sets = [labels.get(store.mbids[v], set()) for v, _ in neighbours]
    return neighbours, u_set, neutral_for(u_set, cand_sets)


def find_path_coh(store, source, target, cfg, labels, w_coh):
    """`find_path` with one added per-edge coherence term. See module docstring."""
    if source == target:
        return [source]

    base_floor_raw = min(float(store.pop_raw[source]), float(store.pop_raw[target]))

    dist = {source: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        pop_raw_u = float(store.pop_raw[u])
        neighbours, u_set, neutral = _neutral_and_neighbours(store, u, labels)
        for v, sim in neighbours:
            pop_raw_v = float(store.pop_raw[v])
            a = resolved_agreement(u_set, labels.get(store.mbids[v], set()), neutral)
            cost = (
                cfg.w_sim * (1.0 - float(sim))
                + cfg.w_jump * abs(pop_raw_u - pop_raw_v)
                + cfg.w_floor * max(0.0, base_floor_raw - pop_raw_v)
                + cfg.w_degree_hub * float(store.degree_hub_penalty[v])
                + cfg.w_hop
                + w_coh * (1.0 - a)
            )
            nd = d + cost
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if target not in prev:
        return None
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1]


def agreement_cost_of(path, store, labels) -> float:
    """Total (1 - agreement) along a path. `TAS-AM5b`'s comparison quantity."""
    total = 0.0
    for u, v in zip(path, path[1:]):
        _, u_set, neutral = _neutral_and_neighbours(store, u, labels)
        total += 1.0 - resolved_agreement(
            u_set, labels.get(store.mbids[v], set()), neutral
        )
    return total


def equivalence_check(store, cfg, labels, pairs, index) -> dict:
    """`TAS-AM5a`: w_coh = 0 must reproduce production `find_path` EXACTLY.

    Every pair in the draw, on the real artifact -- not a sample, not a fixture.
    Any single mismatch voids every TAS-5 figure.
    """
    from artistpath_api.pathfinding import find_path

    mismatches = []
    for a, b, _cls in pairs:
        s, t = index[a], index[b]
        if find_path_coh(store, s, t, cfg, labels, 0.0) != find_path(store, s, t, [], cfg):
            mismatches.append([a, b])
    return {
        "pairs_checked": len(pairs),
        "mismatches": mismatches,
        "passes": not mismatches,
        "what_it_licenses": "The fork's omission of excludes, avoidance_map, "
                            "effective_floor_raw and forbidden_edge -- proved equivalent, "
                            "not argued.",
    }


def main() -> None:
    from artistpath_api.config import ApiConfig

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cfg = ApiConfig()
    store = load_adopted()
    labels = label_sets()
    index = {m: i for i, m in enumerate(store.mbids)}

    drawn = draw_pairs()
    pairs = [p for p in drawn if p[0] in index and p[1] in index]
    if len(pairs) != len(drawn):
        print(f"WARNING: {len(drawn) - len(pairs)} drawn pairs absent from the artifact",
              flush=True)

    equiv = equivalence_check(store, cfg, labels, pairs, index)
    print(f"TAS-AM5a equivalence: {equiv['passes']} "
          f"({len(equiv['mismatches'])} mismatches / {equiv['pairs_checked']})", flush=True)
    if not equiv["passes"]:
        raise SystemExit(
            "TAS-AM5a FAILED -- the fork is not production's path. Every TAS-5 figure "
            "is void. Do not edit the check to pass it; find the drift."
        )

    # The baseline is computed ONCE, not once per weight.
    baseline = {
        (a, b): find_path_coh(store, index[a], index[b], cfg, labels, 0.0)
        for a, b, _ in pairs
    }

    per_weight: dict[str, dict[str, dict]] = {}
    for mult in WEIGHT_MULTIPLES:
        w_coh = mult * cfg.w_sim
        by_class: dict[str, list[bool]] = {c: [] for c in CLASSES}
        for a, b, cls in pairs:
            arm = find_path_coh(store, index[a], index[b], cfg, labels, w_coh)
            by_class[cls].append(baseline[(a, b)] != arm)
        per_weight[str(mult)] = {
            cls: {
                "n": len(v),
                "changed": sum(v),
                "changed_share": round(sum(v) / len(v), 4) if v else None,
            }
            for cls, v in by_class.items()
        }
        print(f"  w_coh={mult}x w_sim: "
              + ", ".join(f"{c} {per_weight[str(mult)][c]['changed']}/"
                          f"{per_weight[str(mult)][c]['n']}" for c in CLASSES),
              flush=True)

    kills = all(
        cell["changed"] == 0
        for mult, classes in per_weight.items()
        if mult != "0.0"
        for cell in classes.values()
    )

    result = {
        "substrate": {
            "file": ADOPTED.name,
            "sha256": ADOPTED_SHA,
            "note": "ADOPTED ARTIFACT per TAS-AM2. Never compare against a capture-side "
                    "figure.",
        },
        "pair_seed": "20260730-tas",
        "weight_multiples_of_w_sim": WEIGHT_MULTIPLES,
        "w_sim": cfg.w_sim,
        "tas_am5a_equivalence": equiv,
        "per_weight": per_weight,
        "tas5_kills": kills,
        "kill_rule": "TAS-5 kills ONLY if unchanged in EVERY class at EVERY weight. A "
                     "pooled bar is explicitly rejected (section 2).",
        "null_caution": "A TAS-5 null is WEAK evidence about tags specifically -- three "
                        "consecutive router repricings have already returned nulls. It "
                        "must not be reported as 'tags do not work'.",
        "still_owed": "TAS-AM5b (liveness) and TAS-AM5c (null control) live in "
                      "tas_route_guard.py, with TAS-6's routing half. No outcome read is "
                      "licensed until those have run (section 5).",
    }
    Path_out = args.out
    with open(Path_out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({"tas5_kills": kills}, indent=1), flush=True)
    print(f"\nwrote {Path_out}")


if __name__ == "__main__":
    main()
