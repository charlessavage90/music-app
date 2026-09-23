"""`LAL-` differential PRE-SCREEN and pair draw — `LBA-AM6-2`, committed BEFORE its first run.

⚠ **THIS FILE'S OUTPUTS ARE MAP-LABELLED.** `lal_prescreen.json` and `lal_prescreen.md` record, per
candidate pair and depth, how long each map's journey was and what differed. A blind runner who read
them could match a length or an artist to a side and unblind the listen. Both are on the runner
brief's do-not-read list, and the session that runs this may not run the listen or write it up
(`LBA-AM6-2`, `LBA-AM6-5`). `lal_pairs_drawn.json`, the twelve selected pairs, carries endpoint
names, MBIDs and pool ranks only, and is what the owner strikes from.

THE RULE, verbatim in substance from `LBA-AM6-2` — the governing text wins where this differs:

  *Plain: take artists the owner is known to listen to, pair them up, and keep only pairs on which
  the two maps give genuinely different journeys — different at every depth, and different in
  artists he does not know — without ever looking at which map's journey is longer, more obscure or
  better.*

  1. POOL. `gbl_pair_candidates.json`'s `usable` list, in its committed order. An artist's MBID is
     resolved as listens 1 and 2 resolved it (`lbl_pairs.py`): exactly one MBID, the same in both
     `GBL-` maps; any other resolution cannot be placed on a map and leaves the pool (inherited, and
     recorded per artist).
  2. EXCLUDED AT ARTIST LEVEL — every endpoint of every pair on which journeys were presented to him
     in any blind listen: `GBL-AM1`'s eight pairs (`gbl_pairs_approved.json`, sha-pinned), listen 1's
     eight primaries (`lbl_pairs.json` `listen1.primary`) and listen 2's eight primaries
     (`lbl_pairs2.json` `primary`). No substitution fired in either `LBL-` listen, so the primaries
     are exactly what was heard.
  3. EXCLUDED AS PAIRS, ARTISTS KEPT — every reserve pair of both `LBL-` listens (`lbl_pairs.json`
     `listen1.reserve`, `lbl_pairs2.json` `reserve`). None was ever generated.
     `lbl_pairs.json`'s `listen2` table was superseded by `LBD-AM6` before any journey on it was
     generated; it is neither a presented pair nor a reserve of a listen that ran, and the rule
     does not name it, so it is not excluded.
  4. MEMBERSHIP. Both endpoints are nodes of BOTH maps — the served map and the candidate — read
     from the two artifacts directly.
  5. PAIRING. Greedily in pool order, each artist with the earliest still-unpaired artist to which
     it is NOT directly connected in EITHER map, and which step 3 does not ban. Uncapped: every
     pair the pool yields is screened.
  6. PRE-SCREEN. Both maps' journeys are generated exactly as `LBA-AM6-3` will generate them — the
     same module, `lal_journeys.py`, production `find_journey` under `ApiConfig` defaults at d0, d10
     and d20 along the all-`known` ladder, each map pressing on its OWN fame percentile. Three gates,
     in this order:
       Gate L  at least MIN_INTERIOR (3) interior artists at EVERY depth on BOTH maps; a depth a
               map cannot reach with an interior artist fails it.
       Gate D  the two maps' interior artist SETS differ at ALL THREE depths.
       Gate N  at every depth, the SYMMETRIC DIFFERENCE of the two interior sets contains at least
               one artist absent from the familiarity list. The familiarity list is exactly
               `lbl_prescreen2.py`'s `familiarity_mbids` — `usable` plus `ambiguous` entries'
               `v0_nodes` and `g_nodes` MBIDs — used only to count, never to exclude.
  7. RANKING — magnitude and unfamiliarity, never direction. Survivors ordered by
       (a) the total, summed over the three depths, of symmetric-difference artists absent from the
           familiarity list — most first;
       (b) fewest interior artists the list contains, counted once across both maps and all depths
           (`LBD-AM6-1`'s key);
       (c) pool rank — the sum of the two endpoints' pool ranks, as `lbl_prescreen2.py`'s key;
       (d) MBID — the first endpoint's, then the second's. A total order.
     Nothing in any gate or key reads which side an artist is on, which map is longer, or which is
     more or less famous: every quantity is symmetric in the two maps.
  8. SELECTION. The first 8 are the primaries and the next 4 the ordered reserves. Fewer than 12
     survivors: stop and report — nothing is selected, and the owner supplies pairs, which must
     pass the same gates.
  9. The owner's strike (by endpoint names only) is applied afterwards by `lal_pairs_final.py`.

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u analysis/2026-09-22-lba-a6-blind-listen/lal_prescreen.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import (  # noqa: E402
    DEPTHS,
    GBL_APPROVED,
    GBL_APPROVED_SHA,
    GBL_CANDIDATES,
    LBL_PAIRS1,
    LBL_PAIRS1_SHA,
    LBL_PAIRS2,
    LBL_PAIRS2_SHA,
    MIN_INTERIOR,
    PAIRS_PER_LISTEN,
    RESERVES_PER_LISTEN,
    ROLES,
    in_dir,
    load_pinned_maps,
    read_pins,
    sha256_of,
    use_api_src,
)

WANTED = PAIRS_PER_LISTEN + RESERVES_PER_LISTEN


def familiarity_mbids(candidates: dict) -> set[str]:
    """`lbl_prescreen2.py`'s set, unchanged: every artist the owner's export gives listening time
    for, however its MBID resolved. Counts; excludes nothing."""
    out: set[str] = set()
    for key in ("usable", "ambiguous"):
        for r in candidates.get(key, []):
            for node in (r.get("v0_nodes") or []) + (r.get("g_nodes") or []):
                if node.get("mbid"):
                    out.add(node["mbid"])
    return out


def pool_records(candidates: dict, excluded_endpoints: dict[str, str], nodes: dict[str, set[str]]) -> list[dict]:
    """Steps 1, 2 and 4. One record per `usable` artist, in committed order.

    `excluded_endpoints` maps MBID -> the listen whose presented pair it was an endpoint of.
    """
    records = []
    for rank, r in enumerate(candidates["usable"], 1):
        v0, g = r.get("v0_nodes") or [], r.get("g_nodes") or []
        mbid = v0[0]["mbid"] if len(v0) == 1 else None
        rec = {"rank": rank, "name": r["name"], "mbid": mbid, "minutes": round(r["ms_played"] / 60_000)}
        if r.get("status") != "ok" or len(v0) != 1 or len(g) != 1 or g[0]["mbid"] != mbid:
            rec["excluded"] = "not one MBID in both GBL- maps"
        elif mbid in excluded_endpoints:
            rec["excluded"] = f"endpoint of a presented pair ({excluded_endpoints[mbid]})"
        elif any(mbid not in nodes[role] for role in ROLES):
            rec["excluded"] = "not a node of both maps"
        records.append(rec)
    return records


def draw(eligible: list[dict], adjacent_in_either, forbidden_pairs: set) -> list[dict]:
    """Step 5. Pure apart from `adjacent_in_either(a_mbid, b_mbid) -> bool`."""
    unpaired: list[dict] = []
    pairs: list[dict] = []
    for rec in eligible:
        partner = None
        for u in unpaired:
            if adjacent_in_either(u["mbid"], rec["mbid"]):
                rec.setdefault("skipped_as_adjacent_to", []).append(u["name"])
                continue
            if frozenset((u["mbid"], rec["mbid"])) in forbidden_pairs:
                rec.setdefault("skipped_as_lbl_reserve_with", []).append(u["name"])
                continue
            partner = u
            break
        if partner is None:
            unpaired.append(rec)
        else:
            unpaired.remove(partner)
            pairs.append({"a": partner, "b": rec})
    return pairs


def screen(per_map: dict, familiar: set) -> tuple:
    """Step 6's gates L, D, N in order, over interior MBID lists `per_map[role][depth]`.

    Returns (reason or None, detail). A depth absent from `per_map[role]` is one the ladder could
    not reach with an interior artist, which fails Gate L.
    """
    detail: dict = {"interior_len": {}, "sets_differ": {}, "novel_symdiff": {}}
    for role in ROLES:
        detail["interior_len"][role] = {str(d): len(per_map.get(role, {}).get(d, [])) for d in DEPTHS}
    for role in ROLES:
        for d in DEPTHS:
            if d not in per_map.get(role, {}):
                return f"L: a map does not reach d{d} with an interior artist", detail
            if len(per_map[role][d]) < MIN_INTERIOR:
                return f"L: a map has fewer than {MIN_INTERIOR} interior artists at some depth", detail
    for d in DEPTHS:
        a, b = set(per_map[ROLES[0]][d]), set(per_map[ROLES[1]][d])
        detail["sets_differ"][str(d)] = a != b
        detail["novel_symdiff"][str(d)] = len((a ^ b) - familiar)
    if not all(detail["sets_differ"].values()):
        return "D: the two maps' interior sets are identical at some depth", detail
    if not all(detail["novel_symdiff"][str(d)] >= 1 for d in DEPTHS):
        return "N: at some depth every differing artist is on the familiarity list", detail
    return None, detail


def familiarity(per_map: dict, familiar: set) -> dict:
    """Distinct interior artists across both maps and all depths, and how many are on the list."""
    interiors: set = set()
    for role in ROLES:
        for d in DEPTHS:
            interiors |= set(per_map.get(role, {}).get(d, []))
    return {"distinct_interior": len(interiors), "familiar_interior": len(interiors & familiar)}


def rank_key(row: dict) -> tuple:
    """Step 7: (a) most novel symmetric-difference artists, (b) fewest familiar interiors, (c) pool
    rank, (d) MBIDs. Every term is symmetric in the two maps."""
    novel_total = sum(row["detail"]["novel_symdiff"].values())
    return (-novel_total, row["familiarity"]["familiar_interior"],
            row["a"]["rank"] + row["b"]["rank"], row["a"]["mbid"], row["b"]["mbid"])


def select(survivors_ranked: list[dict]) -> dict | None:
    """Step 8. None when fewer than WANTED survive — the draw stops; nothing is selected."""
    if len(survivors_ranked) < WANTED:
        return None
    strip = lambda r: {"a": _endpoint(r["a"]), "b": _endpoint(r["b"])}  # noqa: E731
    return {"primary": [strip(r) for r in survivors_ranked[:PAIRS_PER_LISTEN]],
            "reserve": [strip(r) for r in survivors_ranked[PAIRS_PER_LISTEN:WANTED]]}


def _endpoint(rec: dict) -> dict:
    """What leaves this script unsealed about an endpoint: nothing a side could be read from."""
    return {"name": rec["name"], "mbid": rec["mbid"], "rank": rec["rank"]}


def write_md(out: dict, survivors: list) -> None:
    c = out["counts"]
    lines = [
        "# `LAL-` differential pre-screen (`LBA-AM6-2`)",
        "",
        "⚠ **MAP-LABELLED — a blind runner must not read this file or `lal_prescreen.json`.**",
        "",
        f"Written by `lal_prescreen.py` (sha256 `{out['script_sha256'][:12]}…`), committed before its "
        "first run. Gates L (≥3 interior artists at every depth on both maps), D (interior sets differ "
        "at all three depths), N (at every depth, a differing artist absent from the familiarity "
        "list). Ranked by magnitude and unfamiliarity; never by direction.",
        "",
        "| | |", "|---|---:|",
        f"| export artists (pool) | {c['pool']} |",
        f"| eligible after exclusions | {c['eligible']} |",
        f"| candidate pairs drawn | {c['drawn']} |",
        f"| pairs screened | {c['screened']} |",
        f"| **survivors** | **{c['survivors']}** |",
        f"| wanted (8 primary + 4 reserve) | {c['wanted']} |",
        "",
        "## Why artists left the pool", "", "| reason | artists |", "|---|---:|",
    ]
    for k, v in sorted(out["exclusion_counts"].items()):
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Why candidate pairs were rejected", "", "| reason | pairs |", "|---|---:|"]
    for k, v in sorted(out["rejection_counts"].items()):
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Survivors, ranked", "",
              "| rank | A | B | novel differing artists (d0+d10+d20) | familiar interiors / distinct |",
              "|---|---|---|---:|---:|"]
    for i, r in enumerate(survivors, 1):
        f = r["familiarity"]
        lines.append(f"| {i} | {r['a']['name']} | {r['b']['name']} | "
                     f"{sum(r['detail']['novel_symdiff'].values())} | "
                     f"{f['familiar_interior']}/{f['distinct_interior']} |")
    lines.append("")
    in_dir("lal_prescreen.md").write_text("\n".join(lines), encoding="utf-8")


def _pinned_json(path: Path, sha: str, label: str) -> dict:
    digest = sha256_of(path)
    if digest != sha:
        raise SystemExit(f"REFUSING: {path.name} sha256 {digest} != {label}'s {sha}")
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-pairs", type=int, default=0,
                    help="screen only the first N drawn pairs (smoke; writes nothing)")
    args = ap.parse_args(argv)

    use_api_src()
    from artistpath_api.config import ApiConfig
    from lal_journeys import adjacent, ladder, press_key

    approved = _pinned_json(GBL_APPROVED, GBL_APPROVED_SHA, "GBL-AM1")
    lbl1 = _pinned_json(LBL_PAIRS1, LBL_PAIRS1_SHA, "LBD-AM5-5")["listen1"]
    lbl2 = _pinned_json(LBL_PAIRS2, LBL_PAIRS2_SHA, "LBD-AM6")
    excluded_endpoints: dict[str, str] = {}
    for label, plist in (("GBL-AM1", approved["pairs"]), ("LBL listen 1", lbl1["primary"]),
                         ("LBL listen 2", lbl2["primary"])):
        for p in plist:
            for s in ("a", "b"):
                excluded_endpoints.setdefault(p[s]["mbid"], label)
    forbidden_pairs = {frozenset((p["a"]["mbid"], p["b"]["mbid"])) for p in lbl1["reserve"] + lbl2["reserve"]}

    candidates_sha = sha256_of(GBL_CANDIDATES)
    candidates = json.loads(GBL_CANDIDATES.read_text(encoding="utf-8"))
    familiar = familiarity_mbids(candidates)

    maps = load_pinned_maps()
    nodes = {role: set(maps[role]["store"].mbids) for role in ROLES}
    for role in ROLES:
        print(f"[pre] {role} {Path(maps[role]['path']).name} sha256 {maps[role]['sha256']} "
              f"nodes {len(nodes[role]):,}", flush=True)
    print(f"[pre] familiarity set {len(familiar):,} MBIDs; presented endpoints excluded "
          f"{len(excluded_endpoints)}; reserve pairs banned {len(forbidden_pairs)}", flush=True)

    records = pool_records(candidates, excluded_endpoints, nodes)
    eligible = [r for r in records if "excluded" not in r]

    def adjacent_in_either(a: str, b: str) -> bool:
        return any(adjacent(maps[r]["store"], maps[r]["store"].id_by_mbid[a], maps[r]["store"].id_by_mbid[b])
                   for r in ROLES)

    drawn = draw(eligible, adjacent_in_either, forbidden_pairs)
    print(f"[pre] pool {len(records)}; eligible {len(eligible)}; drew {len(drawn)} candidate pairs", flush=True)

    cfg = ApiConfig()
    keys = {role: press_key(maps[role]["store"], maps[role]["raw_fame"]) for role in ROLES}
    to_screen = drawn[: args.limit_pairs] if args.limit_pairs else drawn
    rows = []
    for i, pair in enumerate(to_screen, 1):
        a, b = pair["a"]["mbid"], pair["b"]["mbid"]
        per_map: dict = {}
        for role in ROLES:
            store = maps[role]["store"]
            lad = ladder(store, store.id_by_mbid[a], store.id_by_mbid[b], keys[role], cfg)
            per_map[role] = {d: [store.mbids[v] for v in path[1:-1]] for d, (path, _k, _p) in lad.items()}
        reason, detail = screen(per_map, familiar)
        rows.append({"a": pair["a"], "b": pair["b"], "detail": detail,
                     "familiarity": familiarity(per_map, familiar), "rejected": reason, "kept": reason is None})
        print(f"[pre] {i}/{len(to_screen)}: " + ("KEPT" if reason is None else f"rejected {reason[:1]}"), flush=True)

    survivors = sorted([r for r in rows if r["kept"]], key=rank_key)
    print(f"[pre] survivors {len(survivors)} of {len(to_screen)} screened", flush=True)
    if args.limit_pairs:
        print("[pre] smoke run: nothing written", flush=True)
        return 0

    rejection_counts: dict = {}
    for r in rows:
        if r["rejected"]:
            gate = r["rejected"].split(":", 1)[0]
            rejection_counts[f"gate {gate}"] = rejection_counts.get(f"gate {gate}", 0) + 1
    exclusion_counts: dict = {}
    for rec in records:
        k = rec.get("excluded", "eligible")
        exclusion_counts[k] = exclusion_counts.get(k, 0) + 1

    selection = select(survivors)
    out = {
        "what": "LAL- differential pre-screen and pair draw (LBA-AM6-2), committed before its first run",
        "warning": "MAP-LABELLED. A blind runner must not read this file.",
        "script_sha256": sha256_of(Path(__file__)),
        "journeys_module_sha256": sha256_of(Path(__file__).with_name("lal_journeys.py")),
        "maps_pin": read_pins(),
        "thresholds": {"min_interior_per_depth": MIN_INTERIOR, "depths": list(DEPTHS),
                       "differ_at_every_depth": True, "novel_symdiff_at_every_depth": 1, "wanted": WANTED},
        "inputs": {
            "candidates": {"file": GBL_CANDIDATES.name, "sha256": candidates_sha, "familiarity_mbids": len(familiar)},
            "gbl_am1": {"file": GBL_APPROVED.name, "sha256": GBL_APPROVED_SHA},
            "lbl_pairs1": {"file": LBL_PAIRS1.name, "sha256": LBL_PAIRS1_SHA},
            "lbl_pairs2": {"file": LBL_PAIRS2.name, "sha256": LBL_PAIRS2_SHA},
            "presented_endpoints_excluded": len(excluded_endpoints),
            "reserve_pairs_banned": len(forbidden_pairs),
        },
        "counts": {"pool": len(records), "eligible": len(eligible), "drawn": len(drawn),
                   "screened": len(to_screen), "survivors": len(survivors), "wanted": WANTED,
                   "sufficient": selection is not None},
        "exclusion_counts": exclusion_counts,
        "rejection_counts": rejection_counts,
        "pool": records,
        "candidates_in_draw_order": rows,
        "survivors_ranked": [{"a": r["a"], "b": r["b"], "familiarity": r["familiarity"], "detail": r["detail"]}
                             for r in survivors],
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    in_dir("lal_prescreen.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str),
                                            encoding="utf-8")
    write_md(out, survivors)
    if selection is None:
        print(f"[pre] NOT ENOUGH: {len(survivors)} survivors, {WANTED} wanted. Stop and report; the owner "
              "supplies pairs, which must pass the same gates.", flush=True)
        return 2
    drawn_doc = {
        "what": "LBA-AM6-2 step 8: 8 primaries and 4 ordered reserves, before the owner's strike",
        "note": "Endpoint names, MBIDs and pool ranks only. Nothing here identifies a map.",
        "prescreen_script_sha256": out["script_sha256"],
        **selection,
        "finished_utc": out["finished_utc"],
    }
    in_dir("lal_pairs_drawn.json").write_text(json.dumps(drawn_doc, indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    print(f"[pre] ENOUGH: {WANTED} selected into lal_pairs_drawn.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
