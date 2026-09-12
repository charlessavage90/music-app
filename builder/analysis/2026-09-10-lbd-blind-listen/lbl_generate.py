"""`LBL-` journey generation for one listen: both maps, gated, sealed and page outputs split.

Governing: `LBD-AM5-5`. **Run by the mechanics-only runner session on listen day, never by the
session that prepared it** (`GBL-` harness log §3.4 — the outputs are the listen's own inputs).

Journeys are production `find_journey` over each map under `ApiConfig` defaults (the `JFX-`
precedent: no mirror). The press rule is `cre_ladder.victim_key` over the map's own fame percentile
— imported, not retyped — after the shipped api modules are imported, so the frozen copy that
`cre_ladder` puts on `sys.path` can never shadow them (asserted).

Every gate is a `SystemExit` carrying its own message. A traceback is a harness fault, not a gate.

  G1 identity    each map's bytes match its sidecar AND the sha pinned in `lbl_maps.json`
  G2 production  the served map routes identically to the artifact the deploy serves
  G3 pairs       `lbl_pairs.json` is the file `LBD-AM5-5` pins
  G4 run state   `LBD-AM5-5`'s substitutions, in order: (a) an endpoint is not in both maps,
                 (b) the endpoints are directly connected in either map, (c) the pair does not reach
                 d0/d10/d20 on both maps with an interior artist at each — next reserve, in order;
                 reserves exhausted -> stop
  G5 differential  the two maps do not return the same journey everywhere
  G6 page leak   the page document has exactly the designed shape and no arm-identifying text

Names, disambiguations and (in `lbl_clips.py`) clip lookups come from the SERVED map for both
sides, by MBID: the two maps harvest names from different sources, and a spelling difference would
be a tell. Every presented artist is a member of `V`, so the served map knows them all.

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u analysis/2026-09-10-lbd-blind-listen/lbl_generate.py --listen 1
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

from lbl_common import (
    DEPTHS,
    LISTENS,
    MAPS_PIN,
    MIN_INTERIOR_BY_LISTEN,
    PAIRS_BY_LISTEN,
    PAIRS_PER_LISTEN,
    PRODUCTION,
    ROLES,
    ROOT,
    SERVED,
    SIDE_ASSIGNMENT_BY_LISTEN,
    TOKENS,
    in_dir,
    load_map,
    sealed_path,
    sha256_of,
    use_api_src,
)

use_api_src()
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.evaluation import path_metrics, top_degree_node_set  # noqa: E402
from artistpath_api.pathfinding import KNOWN, Exclusion, find_journey  # noqa: E402

import artistpath_api.pathfinding as _shipped_pathfinding  # noqa: E402

sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"))
from cre_ladder import victim_key  # noqa: E402

if not Path(_shipped_pathfinding.__file__).resolve().is_relative_to((ROOT / "api" / "src").resolve()):
    raise SystemExit("HARNESS FAULT: artistpath_api.pathfinding is not the shipped module")

MAX_DEPTH = max(DEPTHS)
HUB_FRACTION = 0.01   # top-1 % by DEGREE — never fame, never popularity

# Substrings that would identify a map, scanned over the structure this module writes and NEVER
# over artist names or disambiguations, which the graph supplies and the owner is meant to read.
FORBIDDEN_PAGE_TOKENS = ("incumbent", "challenger", "served", "msw", "tu50", "lux4", "A0V", "A5V",
                         "LBD", "threshold", "production")
PAGE_SCHEMA = {
    "root": {"listen", "pairs"},
    "pair": {"key", "a", "b", "rows"},
    "row": {"depth", "L", "R"},
    "side": {"artists"},
    "artist": {"mbid", "name", "disambiguation"},
}


def routing_identical(a, b) -> bool:
    """Everything `find_journey` reads, compared array by array."""
    if list(a.mbids) != list(b.mbids):
        return False
    for field in ("offsets", "neighbours", "scores", "pop_raw", "fame_lb_pctl", "degree_hub_penalty"):
        if not np.array_equal(np.asarray(getattr(a, field)), np.asarray(getattr(b, field))):
            return False
    return True


def press_key(store, raw_fame: list):
    """`victim_key` wants NaN at artists ListenBrainz reported no listeners for (they sort last);
    `fame_lb_pctl` gives those 0.0, so the raw blob is the only source for the mask (`JFX-`)."""
    measured = np.array([np.nan if v is None else 1.0 for v in raw_fame], dtype=np.float64)
    return victim_key(measured * np.asarray(store.fame_lb_pctl, dtype=np.float64), store.pop_raw, store.mbids)


def ladder(store, s: int, t: int, key, cfg) -> dict[int, tuple[list[int], str, list[int]]]:
    """The all-`known` ladder to MAX_DEPTH, keeping the depths the listen presents.

    Each kept depth is (path, kind, the artists pressed before it, in press order). A depth is
    absent when the ladder cannot reach it: no path, or a path with no interior artist to press.
    """
    excludes: list = []
    out: dict[int, tuple[list[int], str, list[int]]] = {}
    for k in range(MAX_DEPTH + 1):
        result = find_journey(store, s, t, excludes, cfg)
        if result is None:
            break
        path, kind = list(result[0]), result[1]
        interior = path[1:-1]
        if k in DEPTHS and interior:
            out[k] = (path, kind, [e.node for e in excludes])
        if not interior:
            break
        excludes = excludes + [Exclusion(node=min(interior, key=key), reason=KNOWN)]
    return out


def adjacent(store, a: int, b: int) -> bool:
    return any(n == b for n, _ in store.neighbours_of(a))


def check_pair(maps: dict, keys: dict, pair: dict, cfg, min_interior: int = 1) -> tuple[str | None, dict]:
    """`LBD-AM5-5`'s (a), (b), (c) in that order. Returns (reason or None, ladders by role).

    `min_interior` is gate (c)'s bar, per listen (`MIN_INTERIOR_BY_LISTEN`). Listen 1 ran at 1, and
    the findings note §4.1 is the record of what that cost; `LBD-AM6` raises it for listen 2. The
    default is 1 so the frozen listen-1 behaviour is what an un-parameterised call still gets.
    """
    a, b = pair["a"]["mbid"], pair["b"]["mbid"]
    for role in ROLES:
        store = maps[role]["store"]
        if a not in store.id_by_mbid or b not in store.id_by_mbid:
            return "(a) an endpoint is not a node of both maps", {}
    for role in ROLES:
        store = maps[role]["store"]
        if adjacent(store, store.id_by_mbid[a], store.id_by_mbid[b]):
            return "(b) the endpoints are directly connected in one map", {}
    ladders = {}
    for role in ROLES:
        store = maps[role]["store"]
        ladders[role] = ladder(store, store.id_by_mbid[a], store.id_by_mbid[b], keys[role], cfg)
        if any(d not in ladders[role] for d in DEPTHS):
            return "(c) the pair does not reach every depth with an interior artist in one map", {}
        if any(len(ladders[role][d][0]) - 2 < min_interior for d in DEPTHS):
            return (f"(c) the pair does not reach every depth with {min_interior} interior artists "
                    "in one map"), {}
    return None, ladders


def choose_pairs(primary: list[dict], reserve: list[dict], check) -> tuple[list[tuple[dict, dict]], list[dict]]:
    """Fill each primary slot, in order, from the primary pair or the next unused reserve.

    `check(pair) -> (reason | None, ladders)`. Pure apart from `check`, so the substitution rule is
    tested without a map.
    """
    queue = list(reserve)
    chosen: list[tuple[dict, dict]] = []
    substitutions: list[dict] = []
    for slot, pair in enumerate(primary, 1):
        candidate = pair
        while True:
            reason, ladders = check(candidate)
            if reason is None:
                chosen.append((candidate, ladders))
                break
            if not queue:
                raise SystemExit(
                    f"RUN STATE: slot {slot} ({candidate['a']['name']} → {candidate['b']['name']}) failed "
                    f"{reason[:3]} and the reserves are exhausted. Stop and report to the owner; he supplies "
                    f"a pair. No read exists until eight pairs are complete.")
            substitutions.append({"slot": slot, "replaced": f"{candidate['a']['name']} → {candidate['b']['name']}",
                                  "reason": reason})
            candidate = queue.pop(0)
    return chosen, substitutions


def hidden_metrics(store, path: list[int], ruler: dict, hub_mbids: set[str]) -> dict:
    """Recorded, sealed, decides nothing. Fame on ONE fixed ruler (the served map's percentile, by
    MBID; None where ListenBrainz reported no listeners); hubs frozen on the served map."""
    interior = path[1:-1]
    top_set = {i for i, m in enumerate(store.mbids) if m in hub_mbids}
    pm = path_metrics(store, path, top_set)
    return {
        "fame_pctl_interior_fixed_ruler": [ruler.get(store.mbids[v]) for v in interior],
        "payload": sum(1 for v in interior if v not in top_set),
        "top1pct_degree_frac": pm.top1pct_degree_frac,
        "length": pm.length,
    }


def _check_keys(node: dict, kind: str) -> None:
    extra = set(node) - PAGE_SCHEMA[kind]
    missing = PAGE_SCHEMA[kind] - set(node)
    if extra or missing:
        raise SystemExit(f"PAGE LEAK GUARD: {kind} keys extra {sorted(extra)} missing {sorted(missing)} — "
                         f"an undesigned field is a leak whatever it holds")


def assert_page_data_clean(doc: dict) -> None:
    """(1) exactly the designed shape; (2) no forbidden text anywhere this module writes, with the
    graph's own names and disambiguations blanked first."""
    _check_keys(doc, "root")
    scrubbed = {"listen": doc["listen"], "pairs": []}
    for pair in doc["pairs"]:
        _check_keys(pair, "pair")
        rows = []
        for row in pair["rows"]:
            _check_keys(row, "row")
            sides = {}
            for tok in TOKENS:
                _check_keys(row[tok], "side")
                for artist in row[tok]["artists"]:
                    _check_keys(artist, "artist")
                sides[tok] = {"artists": [{"mbid": a["mbid"], "name": "", "disambiguation": ""}
                                          for a in row[tok]["artists"]]}
            rows.append({"depth": row["depth"], **sides})
        scrubbed["pairs"].append({"key": pair["key"], "a": "", "b": "", "rows": rows})
    blob = json.dumps(scrubbed, ensure_ascii=False)
    for tok in FORBIDDEN_PAGE_TOKENS:
        if tok.lower() in blob.lower():
            raise SystemExit(f"PAGE LEAK GUARD: page data contains {tok!r}")


def build_page(listen: int, chosen: list[tuple[dict, dict]], maps: dict, mapping: dict, names) -> dict:
    """`names(mbid) -> (name, disambiguation)` — one source for both sides."""
    def side(role: str, pair: dict, ladders: dict, depth: int) -> dict:
        store = maps[role]["store"]
        path = ladders[role][depth][0]
        artists = []
        for v in path:
            name, disambiguation = names(store.mbids[v])
            artists.append({"mbid": store.mbids[v], "name": name, "disambiguation": disambiguation})
        return {"artists": artists}

    pairs = []
    for pair, ladders in chosen:
        key = f"{pair['a']['mbid']}|{pair['b']['mbid']}"
        a_name, _ = names(pair["a"]["mbid"])
        b_name, _ = names(pair["b"]["mbid"])
        rows = [{"depth": d, "L": side(mapping[key]["L"], pair, ladders, d),
                 "R": side(mapping[key]["R"], pair, ladders, d)} for d in DEPTHS]
        pairs.append({"key": key, "a": a_name, "b": b_name, "rows": rows})
    return {"listen": listen, "pairs": pairs}


def shuffle_mapping(keys: list[str], rng) -> dict[str, dict[str, str]]:
    """Listen 1's rule: each pair drawn independently. It landed 7-1 (findings note §3)."""
    out = {}
    for k in keys:
        roles = list(ROLES)
        rng.shuffle(roles)
        out[k] = dict(zip(TOKENS, roles))
    return out


def deal_mapping(keys: list[str], rng) -> dict[str, dict[str, str]]:
    """`LBD-AM6`, findings note §4.6: DEAL the sides to a balanced split instead of drawing them.

    Which pairs put the challenger on the left is still random; how MANY do is not. With an odd
    number of pairs the split is as even as it can be and the extra side is drawn.
    """
    order = list(keys)
    rng.shuffle(order)
    half = len(order) // 2
    if len(order) % 2 and rng.random() < 0.5:
        half += 1
    left_is_challenger = set(order[:half])
    return {k: ({"L": "challenger", "R": "incumbent"} if k in left_is_challenger
                else {"L": "incumbent", "R": "challenger"}) for k in keys}


def assert_differential(chosen: list, maps: dict) -> None:
    """G5. Refuse a page that serves one map against itself — every row would be identical.

    Extracted so it can be tested: this is the guard that a mis-pinned `lbl_maps.json` naming the
    same artifact under both roles cannot reach the owner. It fires on identity everywhere, which
    is what a self-comparison produces, and passes on a single differing row.
    """
    def mbids_of(role: str, ladders: dict, d: int) -> list:
        store = maps[role]["store"]
        return [store.mbids[v] for v in ladders[role][d][0]]

    if not any(mbids_of("incumbent", lad, d) != mbids_of("challenger", lad, d)
               for _pair, lad in chosen for d in DEPTHS):
        raise SystemExit("G5 FAILED: the two maps return the same journey everywhere")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", type=int, required=True, choices=LISTENS)
    args = ap.parse_args(argv)
    listen = args.listen

    # --- G1, G2, G3 ------------------------------------------------------------------------------
    pins = json.loads(MAPS_PIN.read_text(encoding="utf-8"))[f"listen{listen}"]
    maps = {role: load_map(Path(pins[role]["path"]), pins[role]["sha256"]) for role in ROLES}
    served = load_map(SERVED, pins["served_sha256"])
    production = json.loads(PRODUCTION.with_suffix(PRODUCTION.suffix + ".json").read_text(encoding="utf-8"))
    if sha256_of(PRODUCTION) != production["sha256"]:
        raise SystemExit(f"WRONG ARTIFACT: {PRODUCTION.name} does not match its sidecar")
    use_api_src()
    from artistpath_api.graph_store import GraphStore
    if not routing_identical(served["store"], GraphStore.load(PRODUCTION)):
        raise SystemExit(f"G2 FAILED: {SERVED.name} does not route identically to {PRODUCTION.name}")
    pairs_file, pairs_sha = PAIRS_BY_LISTEN[listen]
    if sha256_of(pairs_file) != pairs_sha:
        raise SystemExit(f"G3 FAILED: {pairs_file.name} is not the pinned pair file")
    pair_doc = json.loads(pairs_file.read_text(encoding="utf-8"))
    # Listen 1's file holds both listens' tables; LBD-AM6's file is listen 2's alone.
    pairs = pair_doc[f"listen{listen}"] if f"listen{listen}" in pair_doc else pair_doc
    if len(pairs["primary"]) != PAIRS_PER_LISTEN:
        raise SystemExit(f"G3 FAILED: {len(pairs['primary'])} primary pairs, not {PAIRS_PER_LISTEN}")
    min_interior = MIN_INTERIOR_BY_LISTEN[listen]
    print(f"[lbl] listen {listen}: maps verified; production twin identical; pairs pinned "
          f"({pairs_file.name}); gate (c) bar {min_interior} interior artist(s)", flush=True)

    # --- G4 --------------------------------------------------------------------------------------
    cfg = ApiConfig()
    keys = {role: press_key(maps[role]["store"], maps[role]["raw_fame"]) for role in ROLES}
    chosen, substitutions = choose_pairs(pairs["primary"], pairs["reserve"],
                                         lambda pair: check_pair(maps, keys, pair, cfg, min_interior))
    for s in substitutions:
        print(f"[lbl] slot {s['slot']}: {s['replaced']} replaced by the next reserve ({s['reason'][:3]})", flush=True)

    # --- G5 --------------------------------------------------------------------------------------
    assert_differential(chosen, maps)

    # --- sealed record, page ---------------------------------------------------------------------
    sstore = served["store"]
    ruler = {m: (None if served["raw_fame"][i] is None else float(sstore.fame_lb_pctl[i]))
             for i, m in enumerate(sstore.mbids)}
    hub_mbids = {sstore.mbids[i] for i in top_degree_node_set(sstore, HUB_FRACTION)}

    def names(mbid: str) -> tuple[str, str]:
        i = sstore.id_by_mbid[mbid]
        return sstore.names[i], sstore.disambiguations[i]

    rng = random.SystemRandom()
    keys_order = [f"{p['a']['mbid']}|{p['b']['mbid']}" for p, _l in chosen]
    assignment = SIDE_ASSIGNMENT_BY_LISTEN[listen]
    mapping = (deal_mapping if assignment == "dealt_balanced" else shuffle_mapping)(keys_order, rng)
    sealed = {
        "listen": listen, "mapping": mapping, "substitutions": substitutions,
        "side_assignment": assignment, "min_interior_gate": min_interior,
        "pairs_file": {"name": pairs_file.name, "sha256": pairs_sha},
        "maps": {role: {"path": str(maps[role]["path"]), "sha256": maps[role]["sha256"]} for role in ROLES},
        "api_config": {k: v for k, v in dataclasses.asdict(cfg).items() if k.startswith(("w_", "floor", "avoid"))},
        "hub_set_frozen_on": SERVED.name, "fame_ruler": f"{SERVED.name} fame_lb_pctl by MBID",
        "journeys": {role: {} for role in ROLES},
    }
    for pair, ladders in chosen:
        key = f"{pair['a']['mbid']}|{pair['b']['mbid']}"
        for role in ROLES:
            store = maps[role]["store"]
            sealed["journeys"][role][key] = {
                str(d): {"path_mbids": [store.mbids[v] for v in ladders[role][d][0]], "kind": ladders[role][d][1],
                         "pressed_mbids": [store.mbids[v] for v in ladders[role][d][2]],
                         "metrics": hidden_metrics(store, ladders[role][d][0], ruler, hub_mbids)}
                for d in DEPTHS}
    page = build_page(listen, chosen, maps, mapping, names)
    assert_page_data_clean(page)

    sealed_path(f"lbl_listen{listen}_sealed.json").write_text(json.dumps(sealed, indent=2, ensure_ascii=False), encoding="utf-8")
    in_dir(f"lbl_listen{listen}_page_data.json").write_text(json.dumps(page, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[lbl] listen {listen}: {len(chosen)} pairs x {len(DEPTHS)} depths x 2 maps; "
          f"{len(substitutions)} substitution(s); sealed mapping written; page data clean", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
