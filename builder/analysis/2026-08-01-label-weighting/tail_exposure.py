"""Does the app actually DELIVER the no-release tail? -- the exposure follow-up.

DIAGNOSTIC ONLY. Not a WGT- criterion, not a TAS- criterion, NOT pre-registered,
no bar, licenses nothing, adopts nothing. Same standing as `tail_sample.py`
beside it (outside the WGT- pre-registration by its section 8) and as
`tas_frame_split.py`. If any figure here is ever to gate a decision it needs its
own pre-registration designed cold.

WHY IT EXISTS
  `TAIL-SAMPLE.md` records the owner's manual verdicts on 20 artists drawn from
  the no-release population: 18 of 20 not journey-worthy. That is a POPULATION
  fact. It does not say the app ever shows one to anyone, and whether it does
  decides what kind of problem this is:
    - if journeys never deliver them, it is not a live defect at all -- it is a
      prerequisite for the obscurity push (DD-F1/REQ-37), because succeeding at
      that push is what would start delivering them;
    - if journeys do deliver them, it is a live defect with a measurable rate.
  Nobody had measured it.

THE COMPOSITION WARNING THIS PROBE EXISTS TO RAISE (COH-2/COH-3 again)
  The delivered subset need not resemble its population. COH-3 measured exactly
  this trap in the other direction: obscure artists that journeys actually pass
  through were far better labelled than the obscure population at large. So the
  18-of-20 rate MUST NOT be assumed to carry over to the artists the router
  picks -- routing favours high-degree, higher-popularity nodes, which is a
  different population. This probe reports the delivered set by name so the
  question can be put to the owner on the right sample.

IMPORTED, NOT REIMPLEMENTED
  population predicate  -- tail_sample.py's exact expression (rel_rg_raw plus a
                           Discogs bucket through rel_artist_index_raw)
  pair classes          -- tas_signal.edge_class over tas_common.fame_frame,
                           the same rule the TAS- draw uses
  router                -- api pathfinding.find_path at production ApiConfig(),
                           the call TAS-AM5a proved the TAS- fork equivalent to
  substrate             -- the ADOPTED artifact, sha asserted on load (map side,
                           per TAS-AM2). Never compared with a capture-side figure.

INSTRUMENT CHECKS, both hard (the run aborts rather than reporting)
  1. the artifact sha256 must equal ADOPTED_SHA
  2. the population must reproduce TAIL-SAMPLE.md's committed 7,686 exactly

Runtime ~6 min: 1,200 Dijkstra runs over the full 74k-node graph.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (str(_TAS), str(ROOT / "api" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tas_common import ADOPTED, ADOPTED_SHA, fame_frame, graph_mbids  # noqa: E402
from tas_signal import edge_class  # noqa: E402

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_path  # noqa: E402

OUT = HERE / "tail_exposure.json"
# TWO independent draws, deliberately. A single seed's rate would be false
# precision: the first two draws run disagreed by ~2 points on `fo` and `oo`
# while both returned exactly zero on `ff`. Reporting one seed would have made
# a seed-sensitive rate look exact and would have hidden that the `ff` zero is
# the one figure that replicated.
SEEDS = ("20260801-tail-exposure", "20260801-tail-famous")
PER_CLASS = 400
COMMITTED_POPULATION = 7686  # TAIL-SAMPLE.md; a mismatch aborts the run
CLASSES = ("ff", "fo", "oo")


def no_release_ids(store) -> set[int]:
    """tail_sample.py's predicate, expressed once."""
    rg = json.loads((_REL / "rel_rg_raw.json").read_text(encoding="utf-8"))
    index = json.loads((_REL / "rel_artist_index_raw.json").read_text(encoding="utf-8"))
    discogs = json.loads((_REL / "rel_discogs_raw.json").read_text(encoding="utf-8"))

    def has_discogs(mbid: str) -> bool:
        did = (index.get(mbid) or {}).get("discogs")
        return bool(did and discogs.get(did))

    return {i for i, m in enumerate(store.mbids)
            if not rg.get(m) and not has_discogs(m)}


def main() -> None:
    digest = sha256(ADOPTED.read_bytes()).hexdigest()
    if digest != ADOPTED_SHA:
        raise SystemExit(f"artifact mismatch: {digest} != {ADOPTED_SHA}")
    store = GraphStore.load(ADOPTED)
    n = len(store.mbids)

    nore = no_release_ids(store)
    if len(nore) != COMMITTED_POPULATION:
        raise SystemExit(
            f"population {len(nore)} != TAIL-SAMPLE.md's committed "
            f"{COMMITTED_POPULATION}; the inputs have moved, nothing here counts")
    print(f"artifact ok; no-release population reproduces at {len(nore)}", flush=True)

    deg = [int(store.offsets[i + 1] - store.offsets[i]) for i in range(n)]
    pop = store.pop_raw
    order = sorted(range(n), key=lambda i: float(pop[i]))
    pctl = [0.0] * n
    for rank, i in enumerate(order):
        pctl[i] = rank / (n - 1)

    # A degree-1 node can NEVER be a path interior: entering and leaving needs
    # two distinct edges. Those artists are reachable only as an endpoint the
    # user typed, so no routing change can affect them.
    bands: Counter = Counter()
    for i in nore:
        p = pctl[i]
        bands["bottom 10%" if p < 0.10 else "10-50%" if p < 0.50
              else "50-90%" if p < 0.90 else "top 10%"] += 1
    blank = [i for i, nm in enumerate(store.names) if not nm or not nm.strip()]
    structure = {
        "artists": n,
        "no_release": len(nore),
        "no_release_share": round(len(nore) / n, 4),
        "degree_1_cannot_be_interior": sum(1 for i in nore if deg[i] == 1),
        "interior_capable": sum(1 for i in nore if deg[i] >= 2),
        "edge_endpoint_share": round(sum(deg[i] for i in nore) / sum(deg), 4),
        "fame_bands": dict(bands),
        # GR-1 dropped nameless artists, but only a REBUILD applies it and the
        # adopted artifact predates it (TAS-AM1 records the same fact).
        "nameless_in_adopted_artifact": len(blank),
        "nameless_interior_capable": sum(1 for i in blank if deg[i] >= 2),
    }
    print(json.dumps(structure, indent=1), flush=True)

    frame = fame_frame()
    mbids = sorted(m for m in graph_mbids() if m in frame)
    cfg = ApiConfig()
    idx = {m: i for i, m in enumerate(store.mbids)}
    by_seed: dict[str, dict] = {}
    delivered: Counter = Counter()

    for seed in SEEDS:
        rng = random.Random(seed)
        buckets: dict[str, set[tuple[str, str]]] = {c: set() for c in CLASSES}
        attempts = 0
        while any(len(v) < PER_CLASS for v in buckets.values()) and attempts < 5_000_000:
            attempts += 1
            a, b = rng.sample(mbids, 2)
            c = edge_class(frame[a], frame[b])
            if len(buckets[c]) < PER_CLASS:
                buckets[c].add(tuple(sorted((a, b))))

        per_class: dict[str, dict] = {}
        print(f"\ndraw {seed}:", flush=True)
        for cls in CLASSES:
            journeys = touched = interiors = hits = 0
            for a, b in sorted(buckets[cls]):
                path = find_path(store, idx[a], idx[b], [], cfg)
                if not path:
                    continue
                journeys += 1
                inner = path[1:-1]
                interiors += len(inner)
                h = [i for i in inner if i in nore]
                hits += len(h)
                touched += bool(h)
                delivered.update(h)
            per_class[cls] = {
                "journeys": journeys,
                "interiors": interiors,
                "no_release_interiors": hits,
                "interior_share": round(hits / interiors, 5) if interiors else None,
                "journeys_touched": touched,
                "journey_share": round(touched / journeys, 4) if journeys else None,
                # Zero events cannot prove "never". The rule-of-three 95% ceiling
                # is reported instead, so a zero reads as a bound, not a fact.
                "zero_event_95pct_journey_ceiling":
                    round(3 / journeys, 4) if journeys and not touched else None,
            }
            print(f"  {cls}: {json.dumps(per_class[cls])}", flush=True)
        by_seed[seed] = per_class

    pooled = {
        cls: {
            "journeys": sum(by_seed[s][cls]["journeys"] for s in SEEDS),
            "journeys_touched": sum(by_seed[s][cls]["journeys_touched"] for s in SEEDS),
            "interiors": sum(by_seed[s][cls]["interiors"] for s in SEEDS),
            "no_release_interiors":
                sum(by_seed[s][cls]["no_release_interiors"] for s in SEEDS),
        }
        for cls in CLASSES
    }
    for cls, v in pooled.items():
        v["journey_share"] = round(v["journeys_touched"] / v["journeys"], 4)
        v["interior_share"] = round(v["no_release_interiors"] / v["interiors"], 5)
        v["zero_event_95pct_journey_ceiling"] = (
            round(3 / v["journeys"], 5) if not v["journeys_touched"] else None)
    print("\npooled across both draws:", json.dumps(pooled, indent=1), flush=True)

    rows = [{"mbid": store.mbids[i], "name": store.names[i],
             "disambiguation": store.disambiguations[i],
             "pctl": round(pctl[i], 4), "degree": deg[i], "times_delivered": c}
            for i, c in delivered.most_common()]
    print(f"\ndistinct no-release artists delivered: {len(rows)}")

    OUT.write_text(json.dumps({
        "scope": ("DIAGNOSTIC ONLY -- not pre-registered, no bar, licenses "
                  "nothing, adopts nothing."),
        "substrate": {"file": ADOPTED.name, "sha256": ADOPTED_SHA,
                      "note": "ADOPTED artifact, map side per TAS-AM2."},
        "seeds": list(SEEDS),
        "per_class_pairs_per_seed": PER_CLASS,
        "structure": structure,
        "per_class_by_seed": by_seed,
        "per_class_pooled": pooled,
        "delivered_artists": rows,
        "composition_warning": (
            "The 18-of-20 verdict in TAIL-SAMPLE.md was measured on a "
            "POPULATION-stratified sample. COH-3 is the standing precedent that "
            "a delivered subset can differ sharply from its population. These "
            "delivered artists are NOT that sample and carry no verdict."),
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
