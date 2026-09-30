"""`DSL-` journey generation: both sides, gated, sealed and page outputs split (`DRP-AM7-3`, `-5`, `-6`).

**Run by the mechanics-only RUNNER session on listen day, never by the preparation session** — the
outputs are the listen's own inputs, and the preparation session has seen side-labelled output.

Adapted by copy from `LAL-`'s `lal_generate.py`. Every journey comes from `dsl_journeys.side_ladder`,
the module `DSL-G1` and the pre-screen ran, so generation reproduces the screened journeys by
construction.

Every gate is a `SystemExit` carrying its own message. A traceback is a harness fault, not a gate.

  G1 generator   `dsl_g1.json` says PASS, and was run on THIS `dsl_journeys.py` (LF sha)
  G2 identity    both maps verified against sidecar and pin by the lattice's loader; DRP-S1 only
                 if DRP-G3 passed on it (`drp_sweep.load_map`)
  G3 pairs       `dsl_pairs.json` is the file `dsl_common.DSL_PAIRS_SHA` pins (post-strike)
  G6 metadata    the two artifacts record the SAME name, disambiguation and Deezer id for every
                 MBID (`DRP-AM7-6`) — before any journey, so a refusal spends nothing
  G4 run state   `DRP-AM7-3`'s substitutions, in order: (a) an endpoint is not in both maps,
                 (b) the endpoints are directly connected in either map, (c) Gate L, (d) either
                 side's ladder stops before a presented depth — next reserve of the same tier, then
                 of the other; reserves exhausted -> stop
  G4' asserted   Gates D and N, which the pre-screen passed deterministically: a failure means the
                 maps or the code moved, and generation STOPS
  G5 differential  the page does not serve one side against itself
  G7 page leak   the page document has exactly the designed shape and no side-identifying text

    cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \\
      ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_generate.py [--dry-run]
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dsl_common import (  # noqa: E402
    DEPTHS, DSL_PAIRS, DSL_PAIRS_SHA, FAMILIAR, FAMILIAR_SHA, G1_RESULT, KNOWN_POOL, KNOWN_POOL_SHA,
    MIN_INTERIOR, PAIRS_PER_LISTEN, ROLES, TOKENS, in_dir, pinned_json, sealed_path, sha256_lf)

# Substrings that would identify a side, scanned over the structure this module writes and NEVER
# over artist names or disambiguations, which the graph supplies and the owner is meant to read.
# No bare "a0" or "s1": they are hex digraphs and occur inside MBIDs.
FORBIDDEN_PAGE_TOKENS = ("incumbent", "challenger", "candidate", "today", "ceiling", "s1p3", "s0p0",
                         "drp-", "lba", "tier", "supply", "relax")
PAGE_SCHEMA = {
    "root": {"pairs"},
    "pair": {"key", "a", "b", "rows"},
    "row": {"depth", "L", "R"},
    "side": {"artists"},
    "artist": {"mbid", "name", "disambiguation"},
}


# ---- G6 ----------------------------------------------------------------------------------------
def metadata_conflicts(a, b) -> list[str]:
    """MBIDs whose name, disambiguation or Deezer id differ between the two stores, or that only one
    store holds. `DRP-G3` says there are none; this checks it rather than trusting it."""
    out = []
    bi = b.id_by_mbid
    for mbid, i in a.id_by_mbid.items():
        j = bi.get(mbid)
        if j is None or a.names[i] != b.names[j] or a.disambiguations[i] != b.disambiguations[j] \
                or a.deezer_id_of(i) != b.deezer_id_of(j):
            out.append(mbid)
    out += [m for m in bi if m not in a.id_by_mbid]
    return sorted(out)


def artist_source(store):
    """`DRP-AM7-6`: one answer per artist whichever side presents it. G6 has shown both artifacts
    agree, so today's map's artifact is the one source."""
    def info(mbid: str) -> tuple[str, str, str]:
        i = store.id_by_mbid[mbid]
        return store.names[i], store.disambiguations[i], store.deezer_id_of(i) or ""
    return info


# ---- G4 ----------------------------------------------------------------------------------------
def check_pair(maps: dict, pair: dict, ladder_fn, adjacent_fn, at_depths_fn) -> tuple[str | None, dict]:
    """G4 (a)-(d) in order. `ladder_fn(role, m, s, t)` -> full ladder. Returns (reason, ladders)."""
    a, b = pair["a"]["mbid"], pair["b"]["mbid"]
    for role in ROLES:
        if a not in maps[role].store.id_by_mbid or b not in maps[role].store.id_by_mbid:
            return "(a) an endpoint is not a node of both maps", {}
    for role in ROLES:
        m = maps[role]
        if adjacent_fn(m, m.store.id_by_mbid[a], m.store.id_by_mbid[b]):
            return "(b) the endpoints are directly connected in one map", {}
    ladders = {}
    for role in ROLES:
        m = maps[role]
        lad = ladder_fn(role, m, m.store.id_by_mbid[a], m.store.id_by_mbid[b])
        shown = at_depths_fn(lad)
        if any(len(shown[d]["path"]) - 2 < MIN_INTERIOR for d in shown):
            return f"(c) Gate L: fewer than {MIN_INTERIOR} interior artists at some depth on one side", {}
        if any(d not in shown for d in DEPTHS):
            return "(d) a side's ladder stops before a presented depth", {}
        ladders[role] = lad
    return None, ladders


def choose_pairs(primary: list[dict], reserve: list[dict], check):
    """Fill each primary slot, in order: the primary, else the next unused reserve of its tier, else
    the next unused reserve of the other tier."""
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
            nxt = next((r for r in queue if r["tier"] == pair["tier"]), queue[0])
            queue.remove(nxt)
            substitutions.append({"slot": slot, "replaced": f"{candidate['a']['name']} → {candidate['b']['name']}",
                                  "reason": reason, "same_tier": nxt["tier"] == pair["tier"]})
            candidate = nxt
    return chosen, substitutions


def interiors(maps: dict, ladders: dict, role: str, d: int) -> list[str]:
    return [maps[role].mbids[v] for v in ladders[role][d]["path"][1:-1]]


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


def assert_differential(chosen: list, maps: dict) -> None:
    """G5. Refuse a page that serves one side against itself."""
    def mb(role, lad, d):
        return [maps[role].mbids[v] for v in lad[role][d]["path"]]
    if not any(mb("incumbent", lad, d) != mb("challenger", lad, d) for _p, lad in chosen for d in DEPTHS):
        raise SystemExit("G5 FAILED: the two sides return the same journey everywhere")


# ---- page --------------------------------------------------------------------------------------
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


def deal_mapping(keys: list[str], rng) -> dict[str, dict[str, str]]:
    """`DRP-AM7-4`: sides DEALT 4-4. Which pairs put the challenger on the left is random (system
    source); how MANY do is fixed at half."""
    order = list(keys)
    rng.shuffle(order)
    half = len(order) // 2
    if len(order) % 2 and rng.random() < 0.5:
        half += 1
    left_ch = set(order[:half])
    return {k: ({"L": "challenger", "R": "incumbent"} if k in left_ch
                else {"L": "incumbent", "R": "challenger"}) for k in keys}


def build_page(chosen: list, maps: dict, mapping: dict, info) -> dict:
    def side(role: str, ladders: dict, depth: int) -> dict:
        out = []
        for v in ladders[role][depth]["path"]:
            mb = maps[role].mbids[v]
            name, dis, _ = info(mb)
            out.append({"mbid": mb, "name": name, "disambiguation": dis})
        return {"artists": out}

    pairs = []
    for pair, ladders in chosen:
        key = f"{pair['a']['mbid']}|{pair['b']['mbid']}"
        rows = [{"depth": d, "L": side(mapping[key]["L"], ladders, d),
                 "R": side(mapping[key]["R"], ladders, d)} for d in DEPTHS]
        pairs.append({"key": key, "a": info(pair["a"]["mbid"])[0], "b": info(pair["b"]["mbid"])[0], "rows": rows})
    return {"pairs": pairs}


# ---- sealed ------------------------------------------------------------------------------------
def journey_record(maps: dict, role: str, lad: list[dict], d: int, a0) -> dict:
    """`DRP-AM7-5`'s sealed per-journey record: decides nothing."""
    m = maps[role]
    rec = lad[d]
    path = rec["path"]
    fame = [float(m.pctl[v]) if m.measured[v] else None for v in path[1:-1]]
    added = [(m.mbids[u], m.mbids[v]) for u, v in zip(path, path[1:])
             if not any(n == v for n, _ in a0.store.neighbours_of(u))]
    return {"path_mbids": [m.mbids[v] for v in path], "kind": rec.get("stop"),
            "pressed_mbids": [m.mbids[lad[k]["victim"]] for k in range(d)],
            "fame_pctl_interior": fame, "length": len(path),
            "ceiling_c": rec.get("c"), "relaxation_r": rec.get("r"), "search": rec.get("search"),
            "fmax": rec.get("fmax"),
            "added_connections_traversed": len(added)}


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="run every gate and build the page, then write NOTHING (preparation-session wiring check)")
    args = ap.parse_args(argv)

    # --- G1 --------------------------------------------------------------------------------------
    here = Path(__file__).resolve().parent
    g1 = json.loads(G1_RESULT.read_text(encoding="utf-8")) if G1_RESULT.exists() else {}
    if g1.get("verdict") != "PASS":
        raise SystemExit("G1 FAILED: dsl_g1.json does not record a PASS")
    if g1["harness_sha256_lf"].get("dsl_journeys.py") != sha256_lf(here / "dsl_journeys.py"):
        raise SystemExit("G1 FAILED: dsl_journeys.py changed since DSL-G1 ran; re-run it")

    from dsl_journeys import adjacent, at_depths, cfg, load_maps, side_ladder

    # --- G2, G3 ----------------------------------------------------------------------------------
    maps = load_maps()
    if not DSL_PAIRS_SHA:
        raise SystemExit("G3 FAILED: DSL_PAIRS_SHA is not pinned; the owner's strike has not been committed")
    pairs = pinned_json(DSL_PAIRS, DSL_PAIRS_SHA)
    if len(pairs["primary"]) != PAIRS_PER_LISTEN:
        raise SystemExit(f"G3 FAILED: {len(pairs['primary'])} primary pairs, not {PAIRS_PER_LISTEN}")
    a0, s1 = maps["incumbent"], maps["challenger"]

    # --- G6 --------------------------------------------------------------------------------------
    conflicts = metadata_conflicts(a0.store, s1.store)
    if conflicts:
        raise SystemExit(f"G6 FAILED: the two artifacts disagree on name, disambiguation or Deezer id for "
                         f"{len(conflicts)} MBID(s), first {conflicts[:3]}. Stop and report.")
    print("[dsl] maps verified; DSL-G1 passed on this generator; pairs pinned; metadata identical", flush=True)

    # --- G4, G4' ---------------------------------------------------------------------------------
    config = cfg()
    chosen, substitutions = choose_pairs(
        pairs["primary"], pairs["reserve"],
        lambda p: check_pair(maps, p, lambda role, m, s, t: side_ladder(role, m, s, t, config), adjacent, at_depths))
    for s in substitutions:
        print(f"[dsl] slot {s['slot']}: replaced by a reserve ({s['reason'][:3]})", flush=True)
    known = pinned_json(KNOWN_POOL, KNOWN_POOL_SHA)
    familiar = set(pinned_json(FAMILIAR, FAMILIAR_SHA)["mbids"]) | {a["mbid"] for a in known["pool"]}
    for pair, ladders in chosen:
        assert_d_and_n(pair, {r: {d: interiors(maps, ladders, r, d) for d in DEPTHS} for r in ROLES}, familiar)

    # --- G5 --------------------------------------------------------------------------------------
    assert_differential(chosen, maps)

    # --- sealed record, page ---------------------------------------------------------------------
    info = artist_source(a0.store)
    keys_order = [f"{p['a']['mbid']}|{p['b']['mbid']}" for p, _l in chosen]
    mapping = deal_mapping(keys_order, random.SystemRandom())
    presented = sorted({maps[r].mbids[v] for _p, lad in chosen for r in ROLES for d in DEPTHS for v in lad[r][d]["path"]})
    sealed = {
        "listen": "DSL", "mapping": mapping, "substitutions": substitutions, "side_assignment": "dealt_balanced",
        "pairs_file": {"name": DSL_PAIRS.name, "sha256_lf": DSL_PAIRS_SHA},
        "tiers": {f"{p['a']['mbid']}|{p['b']['mbid']}": p["tier"] for p, _l in chosen},
        "maps": {r: {"sha256": maps[r].sha} for r in ROLES},
        "dsl_g1": {"verdict": g1["verdict"], "harness_sha256_lf": g1["harness_sha256_lf"]},
        "fame_ruler": "fame_lb_pctl, one ruler (DRP-G3); None where ListenBrainz reported no listeners",
        "fame_by_mbid": {mb: (float(a0.pctl[a0.store.id_by_mbid[mb]]) if a0.measured[a0.store.id_by_mbid[mb]] else None)
                         for mb in presented},
        "clip_source": {mb: info(mb)[2] for mb in presented},
        "journeys": {r: {} for r in ROLES},
    }
    for pair, ladders in chosen:
        key = f"{pair['a']['mbid']}|{pair['b']['mbid']}"
        for role in ROLES:
            sealed["journeys"][role][key] = {str(d): journey_record(maps, role, ladders[role], d, a0) for d in DEPTHS}
    page = build_page(chosen, maps, mapping, info)
    assert_page_data_clean(page)
    if args.dry_run:
        print(f"[dsl] DRY RUN: {len(chosen)} pairs, {len(substitutions)} substitution(s), every gate passed; "
              "nothing written", flush=True)
        return 0

    sealed_path("dsl_sealed.json").write_text(json.dumps(sealed, indent=2, ensure_ascii=False), encoding="utf-8")
    in_dir("dsl_page_data.json").write_text(json.dumps(page, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[dsl] {len(chosen)} pairs x {len(DEPTHS)} depths x 2 sides; {len(substitutions)} substitution(s); "
          "sealed mapping written; page data clean", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
