"""`LAL-` journey generation: both maps, gated, sealed and page outputs split (`LBA-AM6-3`, `-5`, `-6`).

**Run by the mechanics-only RUNNER session on listen day, never by the preparation session** — the
outputs are the listen's own inputs, and the preparation session has seen map-labelled output.

Adapted by copy from listen 2's `lbl_generate.py`. The ladder itself is `lal_journeys.py`, the SAME
module the pre-screen ran, so generation reproduces the screened journeys by construction.

Every gate is a `SystemExit` carrying its own message. A traceback is a harness fault, not a gate.

  G1 identity    each map's bytes match its sidecar AND `lal_maps.json`'s pin
  G2 production  the served map routes identically to the pinned production twin
  G3 pairs       `lal_pairs.json` is the file `lal_common.LAL_PAIRS_SHA` pins (post-strike)
  G4 run state   `LBA-AM6-3`'s substitutions, in order: (a) an endpoint is not in both maps,
                 (b) the endpoints are directly connected in either map, (c) Gate L — next
                 reserve, in order; reserves exhausted -> stop
  G4' asserted   Gates D and N, which the pre-screen passed deterministically: a failure means the
                 maps or the code moved, and generation STOPS (no substitution)
  G5 differential  the page does not serve one map against itself
  G6 ids         the two artifacts record no DIFFERENT Deezer id for any shared MBID (`LBA-AM6-6`)
  G7 page leak   the page document has exactly the designed shape and no map-identifying text

Names, disambiguations and clip ids are ONE source per artist, whichever side it appears on
(`LBA-AM6-6`): the candidate artifact where it holds the artist, otherwise the served artifact.

    cd <tree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u analysis/2026-09-22-lba-a6-blind-listen/lal_generate.py
"""
from __future__ import annotations

import dataclasses
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import (  # noqa: E402
    DEPTHS,
    LAL_PAIRS,
    LAL_PAIRS_SHA,
    MIN_INTERIOR,
    PAIRS_PER_LISTEN,
    ROLES,
    TOKENS,
    GBL_CANDIDATES,
    in_dir,
    load_map,
    load_pinned_maps,
    read_pins,
    sealed_path,
    sha256_of,
    use_api_src,
)
from lal_journeys import adjacent, ladder, press_key  # noqa: E402

use_api_src()
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.evaluation import path_metrics, top_degree_node_set  # noqa: E402

HUB_FRACTION = 0.01   # top-1 % by DEGREE — never fame, never popularity

# Substrings that would identify a map, scanned over the structure this module writes and NEVER
# over artist names or disambiguations, which the graph supplies and the owner is meant to read.
# No bare "A6": it is a hex digraph and occurs inside MBIDs.
FORBIDDEN_PAGE_TOKENS = ("incumbent", "challenger", "served", "candidate", "msw", "tu50", "lux4",
                         "lba-a6", "LBA", "threshold", "production")
PAGE_SCHEMA = {
    "root": {"pairs"},
    "pair": {"key", "a", "b", "rows"},
    "row": {"depth", "L", "R"},
    "side": {"artists"},
    "artist": {"mbid", "name", "disambiguation"},
}


def routing_identical(a, b) -> bool:
    """Everything `find_journey` reads, compared array by array."""
    if list(a.mbids) != list(b.mbids):
        return False
    for f in ("offsets", "neighbours", "scores", "pop_raw", "fame_lb_pctl", "degree_hub_penalty"):
        if not np.array_equal(np.asarray(getattr(a, f)), np.asarray(getattr(b, f))):
            return False
    return True


def interiors(ladders: dict, store, d: int) -> list[str]:
    return [store.mbids[v] for v in ladders[d][0][1:-1]]


def check_pair(maps: dict, keys: dict, pair: dict, cfg) -> tuple[str | None, dict]:
    """G4 (a), (b), (c) in that order. Returns (reason or None, ladders by role)."""
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
        if any(d not in ladders[role] or len(ladders[role][d][0]) - 2 < MIN_INTERIOR for d in DEPTHS):
            return f"(c) Gate L: fewer than {MIN_INTERIOR} interior artists at some depth in one map", {}
    return None, ladders


def assert_d_and_n(pair: dict, per_role: dict[str, dict[int, list[str]]], familiar: set) -> None:
    """G4'. The pre-screen passed these deterministically; generation asserts, never substitutes."""
    for d in DEPTHS:
        a, b = set(per_role[ROLES[0]][d]), set(per_role[ROLES[1]][d])
        if a == b:
            raise SystemExit(f"G4' FAILED (Gate D) at d{d} for {pair['a']['name']} → {pair['b']['name']}: "
                             "the maps or the code moved since the pre-screen. Stop and report.")
        if not ((a ^ b) - familiar):
            raise SystemExit(f"G4' FAILED (Gate N) at d{d} for {pair['a']['name']} → {pair['b']['name']}: "
                             "the maps or the code moved since the pre-screen. Stop and report.")


def choose_pairs(primary: list[dict], reserve: list[dict], check):
    """Fill each primary slot, in order, from the primary pair or the next unused reserve."""
    queue = list(reserve)
    chosen, substitutions = [], []
    for slot, pair in enumerate(primary, 1):
        candidate = pair
        while True:
            reason, ladders = check(candidate)
            if reason is None:
                chosen.append((candidate, ladders))
                break
            if not queue:
                raise SystemExit(
                    f"RUN STATE: slot {slot} failed {reason[:3]} and the reserves are exhausted. Stop and "
                    "report to the owner; he supplies a pair, which must pass the same gates. No read "
                    "exists until eight pairs are complete.")
            substitutions.append({"slot": slot, "replaced": f"{candidate['a']['name']} → {candidate['b']['name']}",
                                  "reason": reason})
            candidate = queue.pop(0)
    return chosen, substitutions


def conflicting_deezer_ids(served, candidate) -> list[str]:
    """G6. MBIDs both artifacts hold for which both record a Deezer id and the ids differ."""
    out = []
    for mbid, i in candidate.id_by_mbid.items():
        j = served.id_by_mbid.get(mbid)
        if j is None:
            continue
        a, b = candidate.deezer_id_of(i), served.deezer_id_of(j)
        if a and b and a != b:
            out.append(mbid)
    return sorted(out)


def artist_source(served, candidate):
    """`LBA-AM6-6`: one answer per artist, whichever side presents it. Name and disambiguation from
    the candidate where it holds the artist, otherwise the served map; Deezer id from the candidate
    where it records one, otherwise the served map's, otherwise "" (the resolver then searches by
    name)."""
    def info(mbid: str) -> tuple[str, str, str]:
        ci = candidate.id_by_mbid.get(mbid)
        si = served.id_by_mbid.get(mbid)
        home, idx = (candidate, ci) if ci is not None else (served, si)
        deezer = (candidate.deezer_id_of(ci) if ci is not None else "") or \
                 (served.deezer_id_of(si) if si is not None else "")
        return home.names[idx], home.disambiguations[idx], deezer
    return info


def hidden_metrics(store, path: list[int], other_interior: set[str], cand_ruler: dict, served_ruler: dict,
                   served_nodes: set[str], hub_mbids: set[str], familiar: set[str]) -> dict:
    """`LBA-AM6-5`: recorded, sealed, decides nothing.

    Fame on the candidate's own `fame_lb_pctl` (the only ruler covering every artist either side can
    present, `LBA-X7`) and on the served ruler where defined; None where ListenBrainz reported no
    listeners or the ruler's map lacks the artist. Hubs are frozen on the served map by MBID.
    """
    interior = [store.mbids[v] for v in path[1:-1]]
    top_set = {i for i, m in enumerate(store.mbids) if m in hub_mbids}
    pm = path_metrics(store, path, top_set)
    mine_only = set(interior) - other_interior
    return {
        "fame_pctl_interior_candidate_ruler": [cand_ruler.get(m) for m in interior],
        "fame_pctl_interior_served_ruler": [served_ruler.get(m) for m in interior],
        "presented_not_in_served_map": sum(1 for m in [store.mbids[v] for v in path] if m not in served_nodes),
        "differing_unfamiliar_on_this_side": len(mine_only - familiar),
        "non_hub_interior": sum(1 for v in path[1:-1] if v not in top_set),
        "top1pct_degree_frac": pm.top1pct_degree_frac,
        "length": pm.length,
    }


def _check_keys(node: dict, kind: str) -> None:
    extra, missing = set(node) - PAGE_SCHEMA[kind], PAGE_SCHEMA[kind] - set(node)
    if extra or missing:
        raise SystemExit(f"PAGE LEAK GUARD: {kind} keys extra {sorted(extra)} missing {sorted(missing)} — "
                         f"an undesigned field is a leak whatever it holds")


def assert_page_data_clean(doc: dict) -> None:
    """(1) exactly the designed shape; (2) no forbidden text anywhere this module writes, with the
    graph's own names and disambiguations blanked first."""
    _check_keys(doc, "root")
    scrubbed = {"pairs": []}
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
    blob = json.dumps(scrubbed, ensure_ascii=False).lower()
    for tok in FORBIDDEN_PAGE_TOKENS:
        if tok.lower() in blob:
            raise SystemExit(f"PAGE LEAK GUARD: page data contains {tok!r}")


def build_page(chosen: list, maps: dict, mapping: dict, info) -> dict:
    """`info(mbid) -> (name, disambiguation, deezer_id)` — one source for both sides."""
    def side(role: str, ladders: dict, depth: int) -> dict:
        store = maps[role]["store"]
        out = []
        for v in ladders[role][depth][0]:
            name, dis, _ = info(store.mbids[v])
            out.append({"mbid": store.mbids[v], "name": name, "disambiguation": dis})
        return {"artists": out}

    pairs = []
    for pair, ladders in chosen:
        key = f"{pair['a']['mbid']}|{pair['b']['mbid']}"
        rows = [{"depth": d, "L": side(mapping[key]["L"], ladders, d),
                 "R": side(mapping[key]["R"], ladders, d)} for d in DEPTHS]
        pairs.append({"key": key, "a": info(pair["a"]["mbid"])[0], "b": info(pair["b"]["mbid"])[0], "rows": rows})
    return {"pairs": pairs}


def deal_mapping(keys: list[str], rng) -> dict[str, dict[str, str]]:
    """`LBA-AM6-4`: sides DEALT to a balanced split. Which pairs put the challenger on the left is
    random (system source); how MANY do is fixed at half."""
    order = list(keys)
    rng.shuffle(order)
    half = len(order) // 2
    if len(order) % 2 and rng.random() < 0.5:
        half += 1
    left_ch = set(order[:half])
    return {k: ({"L": "challenger", "R": "incumbent"} if k in left_ch
                else {"L": "incumbent", "R": "challenger"}) for k in keys}


def assert_differential(chosen: list, maps: dict) -> None:
    """G5. Refuse a page that serves one map against itself."""
    def mbids_of(role, ladders, d):
        return [maps[role]["store"].mbids[v] for v in ladders[role][d][0]]
    if not any(mbids_of("incumbent", lad, d) != mbids_of("challenger", lad, d)
               for _p, lad in chosen for d in DEPTHS):
        raise SystemExit("G5 FAILED: the two maps return the same journey everywhere")


def main(argv: list[str] | None = None) -> int:
    import argparse

    from lal_prescreen import familiarity_mbids

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="run every gate and build the page, then write NOTHING (preparation-session wiring check)")
    args = ap.parse_args(argv)

    # --- G1, G2, G3 ------------------------------------------------------------------------------
    maps = load_pinned_maps()
    pins = read_pins()
    twin = load_map(Path(pins["production_twin"]["path"]), pins["production_twin"]["sha256"])
    if not routing_identical(maps["incumbent"]["store"], twin["store"]):
        raise SystemExit("G2 FAILED: the served map does not route identically to the production twin")
    if sha256_of(LAL_PAIRS) != LAL_PAIRS_SHA:
        raise SystemExit(f"G3 FAILED: {LAL_PAIRS.name} is not the pinned pair file")
    pairs = json.loads(LAL_PAIRS.read_text(encoding="utf-8"))
    if len(pairs["primary"]) != PAIRS_PER_LISTEN:
        raise SystemExit(f"G3 FAILED: {len(pairs['primary'])} primary pairs, not {PAIRS_PER_LISTEN}")
    served, cand = maps["incumbent"]["store"], maps["challenger"]["store"]

    # --- G6 (before any journey, so a refusal spends nothing) -------------------------------------
    conflicts = conflicting_deezer_ids(served, cand)
    if conflicts:
        raise SystemExit(f"G6 FAILED: the two artifacts record different Deezer ids for {len(conflicts)} "
                         f"MBID(s), first {conflicts[:3]}. Stop and report.")
    print("[lal] maps verified; production twin identical; pairs pinned; Deezer ids agree", flush=True)

    # --- G4, G4' ---------------------------------------------------------------------------------
    cfg = ApiConfig()
    keys = {role: press_key(maps[role]["store"], maps[role]["raw_fame"]) for role in ROLES}
    chosen, substitutions = choose_pairs(pairs["primary"], pairs["reserve"],
                                         lambda p: check_pair(maps, keys, p, cfg))
    for s in substitutions:
        print(f"[lal] slot {s['slot']}: replaced by the next reserve ({s['reason'][:3]})", flush=True)
    familiar = familiarity_mbids(json.loads(GBL_CANDIDATES.read_text(encoding="utf-8")))
    for pair, ladders in chosen:
        assert_d_and_n(pair, {r: {d: interiors(ladders[r], maps[r]["store"], d) for d in DEPTHS}
                              for r in ROLES}, familiar)

    # --- G5 --------------------------------------------------------------------------------------
    assert_differential(chosen, maps)

    # --- sealed record, page ---------------------------------------------------------------------
    def ruler(m: dict) -> dict:
        s = m["store"]
        return {mb: (None if m["raw_fame"][i] is None else float(s.fame_lb_pctl[i])) for i, mb in enumerate(s.mbids)}
    cand_ruler, served_ruler = ruler(maps["challenger"]), ruler(maps["incumbent"])
    served_nodes = set(served.mbids)
    hub_mbids = {served.mbids[i] for i in top_degree_node_set(served, HUB_FRACTION)}
    info = artist_source(served, cand)

    rng = random.SystemRandom()
    keys_order = [f"{p['a']['mbid']}|{p['b']['mbid']}" for p, _l in chosen]
    mapping = deal_mapping(keys_order, rng)
    sealed = {
        "listen": "LAL", "mapping": mapping, "substitutions": substitutions,
        "side_assignment": "dealt_balanced", "min_interior_gate": MIN_INTERIOR,
        "pairs_file": {"name": LAL_PAIRS.name, "sha256": LAL_PAIRS_SHA},
        "maps": {r: {"path": str(maps[r]["path"]), "sha256": maps[r]["sha256"]} for r in ROLES},
        "production_twin": pins["production_twin"],
        "api_config": {k: v for k, v in dataclasses.asdict(cfg).items() if k.startswith(("w_", "floor", "avoid"))},
        "hub_set_frozen_on": "incumbent (served map), by MBID",
        "fame_rulers": {"candidate": "challenger fame_lb_pctl by MBID", "served": "incumbent fame_lb_pctl by MBID"},
        "clip_source": {mb: info(mb)[2] for p, lad in chosen for r in ROLES
                        for d in DEPTHS for mb in [maps[r]["store"].mbids[v] for v in lad[r][d][0]]},
        "journeys": {r: {} for r in ROLES},
    }
    for pair, ladders in chosen:
        key = f"{pair['a']['mbid']}|{pair['b']['mbid']}"
        for role in ROLES:
            store = maps[role]["store"]
            other = ROLES[1] if role == ROLES[0] else ROLES[0]
            sealed["journeys"][role][key] = {
                str(d): {"path_mbids": [store.mbids[v] for v in ladders[role][d][0]], "kind": ladders[role][d][1],
                         "pressed_mbids": [store.mbids[v] for v in ladders[role][d][2]],
                         "metrics": hidden_metrics(store, ladders[role][d][0],
                                                   set(interiors(ladders[other], maps[other]["store"], d)),
                                                   cand_ruler, served_ruler, served_nodes, hub_mbids, familiar)}
                for d in DEPTHS}
    page = build_page(chosen, maps, mapping, info)
    assert_page_data_clean(page)
    if args.dry_run:
        print(f"[lal] DRY RUN: {len(chosen)} pairs, {len(substitutions)} substitution(s), every gate passed; "
              "nothing written", flush=True)
        return 0

    sealed_path("lal_sealed.json").write_text(json.dumps(sealed, indent=2, ensure_ascii=False), encoding="utf-8")
    in_dir("lal_page_data.json").write_text(json.dumps(page, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[lal] {len(chosen)} pairs x {len(DEPTHS)} depths x 2 maps; {len(substitutions)} substitution(s); "
          "sealed mapping written; page data clean", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
