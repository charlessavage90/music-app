"""`LBL-` listen 2 differential PRE-SCREEN — run BEFORE `LBD-AM6` is written.

⚠ **THIS FILE'S OUTPUTS ARE MAP-LABELLED.** `lbl_prescreen2.json` records, per candidate pair and
depth, how long each map's journey was. A blind runner who read it could match a length to a side
and unblind the listen. Both outputs are on the runner brief's do-not-read list, and the session
that runs this may not run the listen or write it up (`LBD-AM6`).

WHAT THIS IS FOR. Listen 1 tied (`LBL-R2`), and its findings note §3 measured the limiting factor:
the rows the owner could not call were rows where he knew everyone on both sides, and two pairs ran
three or four steps with nothing to judge. This screens candidate pairs on two properties, neither
of which is a direction:

  (1) every depth on both maps carries at least MIN_INTERIOR interior artists — the findings note
      §4.1 defect, a journey long enough to have a shape;
  (2) the two maps' interior artist SETS differ at at least MIN_DIFFERING_DEPTHS of the three
      depths — a pair on which the maps agree everywhere cannot inform a comparison between them.

Survivors are ranked by FEWEST interior artists the owner is known to be familiar with (findings
note §4.2). **Selection is on the MAGNITUDE of difference and on familiarity only, never on which
map is longer, more obscure, or in any way better.** Nothing here reads a verdict.

THE POOL RULE is `lbl_pairs.py`'s, with three departures, each recorded in the output:

  D1  Listen 1's eight PRIMARY endpoints are excluded AT ARTIST LEVEL. He has heard journeys
      between those artists on `LBD-A0V`, which is listen 2's incumbent, so a remembered interior
      would identify a side — the same argument `lbl_pairs.py` step 2 makes for `GBL-AM1`.
  D2  Listen 1's four RESERVE pairs are excluded AS PAIRS, not as artists. No substitution fired in
      listen 1, so none was ever heard; the artists carry no memory and stay in the pool.
  D3  `lbl_pairs.py` step 3 required a partner inside the served population in `LBD-A0`'s derived
      table, a cheap NECESSARY condition for membership of `LBD-A0V` when no `LBD-` map existed
      yet. Both maps now exist, so membership is checked directly against them. Strictly tighter,
      and it needs no DuckDB pass.

Adjacency is screened in BOTH listen-2 maps; the served map is no longer a party to the comparison
and is read only for names and for the endpoint-membership check that keeps `lbl_clips.py` able to
resolve every card.

The previously-dealt listen-2 pairs in `lbl_pairs.json` are NOT excluded: no journey on them was
ever generated and no verdict exists, so re-drawing one spends nothing. `LBD-AM6` supersedes that
table.

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-10-lbd-blind-listen/lbl_prescreen2.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from lbl_common import (
    DEPTHS,
    GBL_APPROVED,
    GBL_APPROVED_SHA,
    GBL_CANDIDATES,
    PAIRS_FILE,
    PAIRS_SHA,
    SERVED,
    in_dir,
    load_map,
    sha256_of,
    use_api_src,
    verified_store,
)

# Both maps' sha256s as `builder/analysis/2026-09-10-lbd-served-population/README.md` §5 records
# them. Identity pins, not figures: `load_map` refuses an artifact unless its bytes match both the
# pin and its own sidecar.
A0V = Path(r"C:\unsung-fast\lbd-artifacts\LBD-A0V.bin")
A0V_SHA = "494c53d52654f6918a4176eef91f291558b0e56d71a4ea16c8070ad8ba3e34bb"
A5V = Path(r"C:\unsung-fast\lbd-artifacts\LBD-A5V.bin")
A5V_SHA = "2d34746e2cc8a6596ee15e390eea5a14ea7f13ede4ec2ba0608475157653ae63"

MAPS = ("A0V", "A5V")
MIN_INTERIOR = 3                 # findings note §4.1
MIN_DIFFERING_DEPTHS = 2         # of len(DEPTHS)
WANTED = 12                      # 8 primary + 4 ordered reserves


def familiarity_mbids(candidates: dict) -> set[str]:
    """Every artist the owner's export gives listening time for, however its MBID resolved.

    `usable` plus `ambiguous`: an artist whose MBID was ambiguous is no less familiar to him. This
    set only COUNTS familiar interiors; it excludes nothing.
    """
    out: set[str] = set()
    for key in ("usable", "ambiguous"):
        for r in candidates.get(key, []):
            for node in (r.get("v0_nodes") or []) + (r.get("g_nodes") or []):
                if node.get("mbid"):
                    out.add(node["mbid"])
    return out


def pool_records(candidates: dict, gbl_endpoints: set[str], listen1_endpoints: set[str],
                 nodes: dict[str, set[str]]) -> list[dict]:
    """`lbl_pairs.py` steps 1-3 with departures D1 and D3. One record per export artist, in order."""
    records = []
    for rank, r in enumerate(candidates["usable"], 1):
        v0, g = r.get("v0_nodes") or [], r.get("g_nodes") or []
        mbid = v0[0]["mbid"] if len(v0) == 1 else None
        rec = {"rank": rank, "name": r["name"], "mbid": mbid, "minutes": round(r["ms_played"] / 60_000)}
        if r.get("status") != "ok" or len(v0) != 1 or len(g) != 1 or g[0]["mbid"] != mbid:
            rec["excluded"] = "not one MBID in both GBL- maps"
        elif mbid in gbl_endpoints:
            rec["excluded"] = "GBL-AM1 endpoint"
        elif mbid in listen1_endpoints:
            rec["excluded"] = "listen-1 primary endpoint (D1)"
        elif mbid not in nodes["served"]:
            rec["excluded"] = "not a node of the served map"
        elif mbid not in nodes["A0V"] or mbid not in nodes["A5V"]:
            rec["excluded"] = "not a node of both listen-2 maps (D3)"
        records.append(rec)
    return records


def draw(eligible: list[dict], adjacent_in_either, forbidden_pairs: set) -> list[dict]:
    """`lbl_pairs.py` step 4, uncapped, with adjacency in EITHER listen-2 map and D2's pair bans.

    Pure apart from `adjacent_in_either(a_mbid, b_mbid) -> bool`, so the rule is tested with no map.
    """
    unpaired: list[dict] = []
    pairs: list[dict] = []
    for rec in eligible:
        partner = None
        for u in unpaired:
            if adjacent_in_either(u["mbid"], rec["mbid"]):
                rec.setdefault("skipped_as_adjacent_to", []).append(u["name"])
                continue
            if frozenset((u["mbid"], rec["mbid"])) in forbidden_pairs:
                rec.setdefault("skipped_as_listen1_reserve_with", []).append(u["name"])
                continue
            partner = u
            break
        if partner is None:
            unpaired.append(rec)
        else:
            unpaired.remove(partner)
            pairs.append({"a": partner, "b": rec})
    return pairs


def screen(per_map: dict) -> tuple:
    """The two gates, over interior MBID lists by map and depth. Returns (reason or None, detail).

    `per_map[map][depth]` is absent when that map's ladder could not reach the depth with an
    interior artist at all — G4 (c)'s condition, which is a rejection here too.
    """
    detail: dict = {"interior_len": {}, "sets_differ": {}, "depths_reached": {}}
    for m in MAPS:
        detail["depths_reached"][m] = sorted(per_map.get(m, {}))
        detail["interior_len"][m] = {str(d): len(per_map.get(m, {}).get(d, [])) for d in DEPTHS}
    for m in MAPS:
        for d in DEPTHS:
            if d not in per_map.get(m, {}):
                return f"a map does not reach d{d} with an interior artist", detail
            if len(per_map[m][d]) < MIN_INTERIOR:
                return f"a map has fewer than {MIN_INTERIOR} interior artists at some depth", detail
    for d in DEPTHS:
        detail["sets_differ"][str(d)] = set(per_map[MAPS[0]][d]) != set(per_map[MAPS[1]][d])
    n = sum(detail["sets_differ"].values())
    detail["differing_depths"] = n
    if n < MIN_DIFFERING_DEPTHS:
        return f"the two maps' interiors differ at fewer than {MIN_DIFFERING_DEPTHS} of {len(DEPTHS)} depths", detail
    return None, detail


def familiarity(per_map: dict, familiar: set) -> dict:
    """Distinct interior artists across both maps and all depths, and how many he is familiar with."""
    interiors: set = set()
    for m in MAPS:
        for d in DEPTHS:
            interiors |= set(per_map.get(m, {}).get(d, []))
    known = interiors & familiar
    return {"distinct_interior": len(interiors), "familiar_interior": len(known),
            "familiar_fraction": round(len(known) / len(interiors), 4) if interiors else 0.0}


def rank_key(row: dict) -> tuple:
    """Fewest familiar interiors first. Every tie-break is deterministic and direction-blind."""
    f = row["familiarity"]
    return (f["familiar_interior"], f["familiar_fraction"], row["a"]["rank"] + row["b"]["rank"],
            row["a"]["mbid"])


def write_md(out: dict, survivors: list) -> None:
    c = out["counts"]
    t = out["thresholds"]
    lines = [
        "# `LBL-` listen 2 — differential pre-screen",
        "",
        "⚠ **MAP-LABELLED — a blind runner must not read this file or `lbl_prescreen2.json`.**",
        "",
        f"Written by `lbl_prescreen2.py` (sha256 `{out['script_sha256'][:8]}…`) before `LBD-AM6` "
        f"existed. Gates: every depth on both maps carries at least {t['min_interior_per_depth']} "
        f"interior artists, and the two maps' interior sets differ at at least "
        f"{t['min_differing_depths']} of {len(t['depths'])} depths. Survivors are ranked by fewest "
        "familiar interior artists. Selection is on the magnitude of difference and on familiarity; "
        "never on direction.",
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
              "| rank | A | B | familiar interiors / distinct | depths where the maps differ |",
              "|---|---|---|---:|---:|"]
    for i, r in enumerate(survivors, 1):
        f = r["familiarity"]
        lines.append(f"| {i} | {r['a']['name']} | {r['b']['name']} | "
                     f"{f['familiar_interior']}/{f['distinct_interior']} | "
                     f"{r['detail']['differing_depths']} |")
    lines.append("")
    in_dir("lbl_prescreen2.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-pairs", type=int, default=0, help="screen only the first N drawn pairs (smoke)")
    args = ap.parse_args(argv)

    use_api_src()
    from artistpath_api.config import ApiConfig
    from lbl_generate import adjacent, ladder, press_key

    digest = sha256_of(GBL_APPROVED)
    if digest != GBL_APPROVED_SHA:
        raise SystemExit(f"REFUSING: {GBL_APPROVED.name} sha256 {digest} != GBL-AM1's {GBL_APPROVED_SHA}")
    approved = json.loads(GBL_APPROVED.read_text(encoding="utf-8"))
    gbl_endpoints = {p[side]["mbid"] for p in approved["pairs"] for side in ("a", "b")}

    pairs_sha = sha256_of(PAIRS_FILE)
    if pairs_sha != PAIRS_SHA:
        raise SystemExit(f"REFUSING: {PAIRS_FILE.name} sha256 {pairs_sha} != LBD-AM5-5's {PAIRS_SHA}")
    committed = json.loads(PAIRS_FILE.read_text(encoding="utf-8"))
    listen1_endpoints = {p[s]["mbid"] for p in committed["listen1"]["primary"] for s in ("a", "b")}
    forbidden_pairs = {frozenset((p["a"]["mbid"], p["b"]["mbid"])) for p in committed["listen1"]["reserve"]}

    candidates_sha = sha256_of(GBL_CANDIDATES)
    candidates = json.loads(GBL_CANDIDATES.read_text(encoding="utf-8"))
    familiar = familiarity_mbids(candidates)

    served_store, _m, served_sha = verified_store(SERVED)
    maps = {"A0V": load_map(A0V, A0V_SHA), "A5V": load_map(A5V, A5V_SHA)}
    nodes = {"served": set(served_store.mbids), "A0V": set(maps["A0V"]["store"].mbids),
             "A5V": set(maps["A5V"]["store"].mbids)}
    print(f"[pre] served sha256 {served_sha} nodes {len(nodes['served']):,}", flush=True)
    for m in MAPS:
        print(f"[pre] {m} sha256 {maps[m]['sha256']} nodes {len(nodes[m]):,}", flush=True)
    print(f"[pre] familiarity set {len(familiar):,} MBIDs; listen-1 primary endpoints excluded "
          f"{len(listen1_endpoints)}; reserve pairs banned {len(forbidden_pairs)}", flush=True)

    records = pool_records(candidates, gbl_endpoints, listen1_endpoints, nodes)
    eligible = [r for r in records if "excluded" not in r]

    def adjacent_in_either(a: str, b: str) -> bool:
        for m in MAPS:
            store = maps[m]["store"]
            if adjacent(store, store.id_by_mbid[a], store.id_by_mbid[b]):
                return True
        return False

    drawn = draw(eligible, adjacent_in_either, forbidden_pairs)
    print(f"[pre] pool {len(records)}; eligible {len(eligible)}; drew {len(drawn)} candidate pairs",
          flush=True)

    cfg = ApiConfig()
    keys = {m: press_key(maps[m]["store"], maps[m]["raw_fame"]) for m in MAPS}
    to_screen = drawn[: args.limit_pairs] if args.limit_pairs else drawn
    rows = []
    for i, pair in enumerate(to_screen, 1):
        a, b = pair["a"]["mbid"], pair["b"]["mbid"]
        per_map: dict = {}
        for m in MAPS:
            store = maps[m]["store"]
            lad = ladder(store, store.id_by_mbid[a], store.id_by_mbid[b], keys[m], cfg)
            per_map[m] = {d: [store.mbids[v] for v in path[1:-1]] for d, (path, _k, _p) in lad.items()}
        reason, detail = screen(per_map)
        fam = familiarity(per_map, familiar)
        rows.append({"a": pair["a"], "b": pair["b"], "detail": detail, "familiarity": fam,
                     "rejected": reason, "kept": reason is None})
        print(f"[pre] {i}/{len(to_screen)} {pair['a']['name']} -> {pair['b']['name']}: "
              + ("KEPT" if reason is None else f"rejected — {reason}")
              + f" (familiar interiors {fam['familiar_interior']}/{fam['distinct_interior']})",
              flush=True)

    survivors = sorted([r for r in rows if r["kept"]], key=rank_key)
    rejection_counts: dict = {}
    for r in rows:
        if r["rejected"]:
            rejection_counts[r["rejected"]] = rejection_counts.get(r["rejected"], 0) + 1

    out = {
        "what": "LBL- listen 2 differential pre-screen, run before LBD-AM6 was written",
        "warning": "MAP-LABELLED. A blind runner must not read this file.",
        "script_sha256": sha256_of(Path(__file__)),
        "thresholds": {"min_interior_per_depth": MIN_INTERIOR,
                       "min_differing_depths": MIN_DIFFERING_DEPTHS,
                       "depths": list(DEPTHS), "wanted": WANTED},
        "inputs": {
            "candidates": {"file": GBL_CANDIDATES.name, "sha256": candidates_sha,
                           "familiarity_mbids": len(familiar)},
            "gbl_am1": {"file": GBL_APPROVED.name, "sha256": GBL_APPROVED_SHA,
                        "endpoints_excluded": len(gbl_endpoints)},
            "committed_pairs": {"file": PAIRS_FILE.name, "sha256": pairs_sha},
            "served_map": {"file": SERVED.name, "sha256": served_sha, "nodes": len(nodes["served"])},
            "A0V": {"file": A0V.name, "sha256": maps["A0V"]["sha256"], "nodes": len(nodes["A0V"])},
            "A5V": {"file": A5V.name, "sha256": maps["A5V"]["sha256"], "nodes": len(nodes["A5V"])},
        },
        "departures_from_lbl_pairs_rule": {
            "D1": "listen-1 primary endpoints excluded at artist level",
            "D2": "listen-1 reserve pairs banned as pairs, their artists kept",
            "D3": "membership checked against both listen-2 maps instead of LBD-A0's table proxy",
        },
        "counts": {
            "pool": len(records), "eligible": len(eligible), "drawn": len(drawn),
            "screened": len(to_screen), "survivors": len(survivors), "wanted": WANTED,
            "sufficient": len(survivors) >= WANTED,
        },
        "exclusion_counts": {},
        "rejection_counts": rejection_counts,
        "pool": records,
        "candidates_in_draw_order": rows,
        "survivors_ranked": [{"a": r["a"], "b": r["b"], "familiarity": r["familiarity"],
                              "detail": r["detail"]} for r in survivors],
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    for rec in records:
        reason = rec.get("excluded", "eligible")
        out["exclusion_counts"][reason] = out["exclusion_counts"].get(reason, 0) + 1

    in_dir("lbl_prescreen2.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    write_md(out, survivors)
    print(f"[pre] survivors {len(survivors)} of {len(to_screen)} screened; "
          f"{'ENOUGH' if len(survivors) >= WANTED else 'NOT ENOUGH'} for {WANTED}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
