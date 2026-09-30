"""`DSL-` differential PRE-SCREEN and pair draw — `DRP-AM7-2`, committed BEFORE its first run.

⚠ **THIS FILE'S OUTPUTS ARE SIDE-LABELLED.** `dsl_prescreen.json` and `dsl_prescreen.md` record, per
candidate pair and depth, how long each side's journey was and what differed. A blind runner who read
them could match a length or an artist to a side. Both are on the runner brief's do-not-read list,
and the session that runs this may not run the listen or write it up (`DRP-AM7-5`).
`dsl_pairs_drawn.json` carries endpoint names, MBIDs, tiers and pool ranks only, and is what the
owner strikes from.

**Run only after `DSL-G1` has passed** (`dsl_g1.json` verdict PASS); it refuses otherwise.

THE RULE, verbatim in substance from `DRP-AM7-2` — the governing text wins where this differs:

  *Plain: take famous artists the owner has told us he knows, pair them up within each fame tier,
  drop anything he has already heard or used, and keep only pairs where the two sides give genuinely
  different journeys in artists he does not know, without ever looking at which side is less famous
  or better.*

  1. POOL. `lal_am7_known.json`'s `pool`, in its committed order, restricted to the famous tiers on
     A0: `DRP-T1` and `DRP-T2`, exactly as `drp_common.STRATA` bounds them (measured fame only, as
     `drp_common.stratum_pool` reads them). Pool rank = position in the known pool.
  2. EXCLUDED AT ARTIST LEVEL: every endpoint `LBA-AM6-2` step 2 excludes
     (`lal_pool_am7.presented_endpoints`); `LAL-`'s eight primaries (`lal_pairs.json`); every endpoint
     in `lba_g5_pair_log.md` (names, resolved with the app's `normalise` to EVERY matching node on A0
     — a homonym is over-excluded, the safe direction); every endpoint in `exploration/pairs-used.txt`.
  3. EXCLUDED AS PAIRS, artists kept: every pair in `drp_pairs.json`, all strata.
  4. MEMBERSHIP: both endpoints are nodes of both maps (asserted).
  5. PAIRING, within a tier: greedily in pool order, each artist with the earliest still-unpaired
     artist of its tier not directly connected in EITHER map, and not a step-3 pair
     (`lal_prescreen.draw`, imported unchanged, run once per tier).
  6. PRE-SCREEN: both sides generated exactly as `DRP-AM7-3` will (`dsl_journeys.side_ladder`), at d5,
     d10 and d20. Gate L: >= 3 interior artists at every depth on both sides (a depth the ladder does
     not reach with an interior artist fails it). Gate D: the interior SETS differ at every depth.
     Gate N: at every depth the symmetric difference holds >= 1 artist absent from the familiarity
     list (`lal_am7_familiar.json` plus the known pool, `LBA-AM7-3`), which counts and never excludes.
  7. RANKING: `lal_prescreen.rank_key`, imported unchanged — most unfamiliar differing artists, then
     fewest familiar interiors, then pool rank, then MBID. Symmetric in the two sides.
  8. SELECTION: per tier, the first 4 are primaries and the next 2 ordered reserves. A tier with too
     few takes all it has, and the other tier fills the shortfall in its own rank order. Fewer than
     12 survivors across both tiers: stop and report (exit 2); nothing is selected.
  9. The owner's strike (endpoint names only) is applied afterwards by `dsl_pairs_final.py`.

    cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \\
      ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_prescreen.py [--limit-pairs N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dsl_common import (  # noqa: E402
    DEPTHS, DRP_PAIRS, DRP_PAIRS_SHA, EXPLORATION_PAIRS, EXPLORATION_PAIRS_SHA, FAMILIAR, FAMILIAR_SHA,
    G1_RESULT, G5_LOG, G5_LOG_SHA, KNOWN_POOL, KNOWN_POOL_SHA, LAL_DIR, LAL_PAIRS, LAL_PAIRS_SHA,
    MIN_INTERIOR, PAIRS_PER_TIER, RESERVES_PER_TIER, ROLES, TIERS, in_dir, pinned_json, pinned_text,
    sha256_lf)

if str(LAL_DIR) not in sys.path:
    sys.path.insert(0, str(LAL_DIR))

WANTED_PER_TIER = PAIRS_PER_TIER + RESERVES_PER_TIER
WANTED = WANTED_PER_TIER * len(TIERS)
G5_LINE = re.compile(r"^- (.+?) → (.+?)\s+\(rerolls: \d+\)")


# ---- step 2's sources, pure --------------------------------------------------------------------
def g5_names(text: str) -> set[str]:
    """Endpoint names from the use-gate log's pair lines (`- A → B  (rerolls: N)`)."""
    out: set[str] = set()
    for line in text.splitlines():
        m = G5_LINE.match(line.strip())
        if m:
            out.update((m.group(1).strip(), m.group(2).strip()))
    return out


def exploration_mbids(text: str) -> set[str]:
    """Columns 3 and 4 of every non-comment line of `pairs-used.txt`."""
    out: set[str] = set()
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 4:
            raise SystemExit(f"REFUSING: malformed pairs-used.txt line: {line!r}")
        out.update((cols[2].strip(), cols[3].strip()))
    return out


def resolve_names(names: set[str], all_names: list[str], mbids: list[str], normalise) -> tuple[set[str], list[str]]:
    """EVERY node whose normalised name matches (homonyms over-excluded). Returns (mbids, unmatched)."""
    index: dict[str, list[int]] = {}
    for i, n in enumerate(all_names):
        index.setdefault(normalise(n), []).append(i)
    found, unmatched = set(), []
    for n in sorted(names):
        hits = index.get(normalise(n), [])
        if not hits:
            unmatched.append(n)
        found.update(mbids[i] for i in hits)
    return found, unmatched


def tier_of(pctl: float, measured: bool, strata) -> str | None:
    """`drp_common.STRATA`'s famous bands, read exactly as `stratum_pool` reads them."""
    if not measured:
        return None
    for ident, lo, hi, hi_incl in strata:
        if ident in TIERS and pctl >= lo and (pctl <= hi if hi_incl else pctl < hi):
            return ident
    return None


def pool_records(known: dict, excluded: dict[str, str], tier: dict[str, str | None],
                 nodes: dict[str, set[str]]) -> list[dict]:
    """Steps 1, 2 and 4. One record per known artist, in committed order."""
    out = []
    for rank, a in enumerate(known["pool"], 1):
        rec = {"rank": rank, "name": a["name"], "mbid": a["mbid"]}
        if any(a["mbid"] not in nodes[r] for r in ROLES):
            rec["excluded"] = "not a node of both maps"
        elif tier.get(a["mbid"]) is None:
            rec["excluded"] = "not in DRP-T1 or DRP-T2 on A0"
        elif a["mbid"] in excluded:
            rec["excluded"] = f"excluded endpoint ({excluded[a['mbid']]})"
        else:
            rec["tier"] = tier[a["mbid"]]
        out.append(rec)
    return out


# ---- step 6 ------------------------------------------------------------------------------------
def screen(per_side: dict, familiar: set, depths=DEPTHS) -> tuple:
    """Gates L, D, N in order over interior MBID lists `per_side[role][depth]` (`lal_prescreen.screen`
    at this listen's depths)."""
    detail: dict = {"interior_len": {}, "sets_differ": {}, "novel_symdiff": {}}
    for role in ROLES:
        detail["interior_len"][role] = {str(d): len(per_side.get(role, {}).get(d, [])) for d in depths}
    for role in ROLES:
        for d in depths:
            if d not in per_side.get(role, {}):
                return f"L: a side does not reach d{d} with an interior artist", detail
            if len(per_side[role][d]) < MIN_INTERIOR:
                return f"L: a side has fewer than {MIN_INTERIOR} interior artists at some depth", detail
    for d in depths:
        a, b = set(per_side[ROLES[0]][d]), set(per_side[ROLES[1]][d])
        detail["sets_differ"][str(d)] = a != b
        detail["novel_symdiff"][str(d)] = len((a ^ b) - familiar)
    if not all(detail["sets_differ"].values()):
        return "D: the two sides' interior sets are identical at some depth", detail
    if not all(detail["novel_symdiff"][str(d)] >= 1 for d in depths):
        return "N: at some depth every differing artist is on the familiarity list", detail
    return None, detail


def familiarity(per_side: dict, familiar: set, depths=DEPTHS) -> dict:
    interiors: set = set()
    for role in ROLES:
        for d in depths:
            interiors |= set(per_side.get(role, {}).get(d, []))
    return {"distinct_interior": len(interiors), "familiar_interior": len(interiors & familiar)}


# ---- step 8 ------------------------------------------------------------------------------------
def _endpoint(rec: dict) -> dict:
    return {"name": rec["name"], "mbid": rec["mbid"], "rank": rec["rank"]}


def select(ranked: dict[str, list[dict]]) -> dict | None:
    """Per tier 4 primaries then 2 reserves; a short tier's gap filled from the other tier's next in
    rank order. None when fewer than WANTED survive across both tiers."""
    if sum(len(v) for v in ranked.values()) < WANTED:
        return None
    queues = {t: list(ranked.get(t, [])) for t in TIERS}
    other = {TIERS[0]: TIERS[1], TIERS[1]: TIERS[0]}

    def take(n_per_tier: int) -> list[dict]:
        got = []
        for t in TIERS:
            for _ in range(n_per_tier):
                src = t if queues[t] else other[t]
                row = queues[src].pop(0)
                got.append({"tier": src, "slot_tier": t, "a": _endpoint(row["a"]), "b": _endpoint(row["b"])})
        return got

    return {"primary": take(PAIRS_PER_TIER), "reserve": take(RESERVES_PER_TIER)}


def write_md(out: dict, survivors: dict) -> None:
    c = out["counts"]
    lines = ["# `DSL-` differential pre-screen (`DRP-AM7-2`)", "",
             "⚠ **SIDE-LABELLED — a blind runner must not read this file or `dsl_prescreen.json`.**", "",
             "| | |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in c.items()]
    lines += ["", "| pool exclusion | artists |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(out["exclusion_counts"].items())]
    lines += ["", "| rejected at | pairs |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(out["rejection_counts"].items())]
    for t in TIERS:
        lines += ["", f"## {t} survivors, ranked", "",
                  "| rank | A | B | novel differing (d5+d10+d20) | familiar / distinct |", "|---|---|---|---:|---:|"]
        for i, r in enumerate(survivors[t], 1):
            f = r["familiarity"]
            lines.append(f"| {i} | {r['a']['name']} | {r['b']['name']} | "
                         f"{sum(r['detail']['novel_symdiff'].values())} | {f['familiar_interior']}/{f['distinct_interior']} |")
    in_dir("dsl_prescreen.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-pairs", type=int, default=0, help="screen the first N drawn pairs per tier; writes nothing")
    args = ap.parse_args(argv)

    g1 = json.loads(G1_RESULT.read_text(encoding="utf-8")) if G1_RESULT.exists() else {}
    if g1.get("verdict") != "PASS":
        raise SystemExit("REFUSING: DSL-G1 has not passed (dsl_g1.json). Run dsl_g1.py first.")

    # dsl_journeys first: importing it puts the lattice's directories on sys.path, which drp_common needs.
    from dsl_journeys import adjacent, at_depths, cfg, load_maps, side_ladder
    import drp_common as dc
    from artistpath_api.search import normalise
    from lal_pool_am7 import presented_endpoints
    from lal_prescreen import draw, rank_key

    known = pinned_json(KNOWN_POOL, KNOWN_POOL_SHA)
    familiar = set(pinned_json(FAMILIAR, FAMILIAR_SHA)["mbids"]) | {a["mbid"] for a in known["pool"]}
    maps = load_maps()
    a0 = maps["incumbent"]
    nodes = {r: set(maps[r].mbids) for r in ROLES}

    excluded: dict[str, str] = dict(presented_endpoints())
    for p in pinned_json(LAL_PAIRS, LAL_PAIRS_SHA)["primary"]:
        for s in ("a", "b"):
            excluded.setdefault(p[s]["mbid"], "LAL- primary")
    g5, g5_unmatched = resolve_names(g5_names(pinned_text(G5_LOG, G5_LOG_SHA)), list(a0.store.names), a0.mbids, normalise)
    for mb in g5:
        excluded.setdefault(mb, "LBA-G5 use-gate log")
    for mb in exploration_mbids(pinned_text(EXPLORATION_PAIRS, EXPLORATION_PAIRS_SHA)):
        excluded.setdefault(mb, "practice room (exploration/pairs-used.txt)")
    drp = pinned_json(DRP_PAIRS, DRP_PAIRS_SHA)
    forbidden = {frozenset((p["source_mbid"], p["target_mbid"]))
                 for st in drp["strata"].values() for p in st["pairs"]}

    tier = {mb: tier_of(float(a0.pctl[i]), bool(a0.measured[i]), dc.STRATA) for i, mb in enumerate(a0.mbids)}
    records = pool_records(known, excluded, tier, nodes)
    config = cfg()

    def adjacent_in_either(x: str, y: str) -> bool:
        return any(adjacent(maps[r], maps[r].store.id_by_mbid[x], maps[r].store.id_by_mbid[y]) for r in ROLES)

    rows, drawn_n = [], 0
    for t in TIERS:
        eligible = [r for r in records if r.get("tier") == t]
        drawn = draw(eligible, adjacent_in_either, forbidden)
        drawn_n += len(drawn)
        print(f"[dsl] {t}: eligible {len(eligible)}; drew {len(drawn)} candidate pairs", flush=True)
        for i, pair in enumerate(drawn[: args.limit_pairs] if args.limit_pairs else drawn, 1):
            per_side = {}
            for role in ROLES:
                m = maps[role]
                lad = side_ladder(role, m, m.store.id_by_mbid[pair["a"]["mbid"]], m.store.id_by_mbid[pair["b"]["mbid"]], config)
                per_side[role] = {d: [m.mbids[v] for v in rec["path"][1:-1]] for d, rec in at_depths(lad).items()}
            reason, detail = screen(per_side, familiar)
            rows.append({"tier": t, "a": pair["a"], "b": pair["b"], "detail": detail,
                         "familiarity": familiarity(per_side, familiar), "rejected": reason, "kept": reason is None})
            print(f"[dsl] {t} {i}/{len(drawn)}: " + ("KEPT" if reason is None else f"rejected {reason[:1]}"), flush=True)

    survivors = {t: sorted([r for r in rows if r["kept"] and r["tier"] == t], key=rank_key) for t in TIERS}
    print(f"[dsl] survivors " + ", ".join(f"{t} {len(survivors[t])}" for t in TIERS), flush=True)
    if args.limit_pairs:
        print("[dsl] smoke run: nothing written", flush=True)
        return 0

    rejection_counts: dict = {}
    for r in rows:
        if r["rejected"]:
            k = f"{r['tier']} gate {r['rejected'][:1]}"
            rejection_counts[k] = rejection_counts.get(k, 0) + 1
    exclusion_counts: dict = {}
    for rec in records:
        k = rec.get("excluded", f"eligible {rec.get('tier')}")
        exclusion_counts[k] = exclusion_counts.get(k, 0) + 1
    selection = select(survivors)
    here = Path(__file__).resolve().parent
    out = {
        "what": "DSL- differential pre-screen and pair draw (DRP-AM7-2), committed before its first run",
        "warning": "SIDE-LABELLED. A blind runner must not read this file.",
        "script_sha256_lf": sha256_lf(Path(__file__)),
        "journeys_module_sha256_lf": sha256_lf(here / "dsl_journeys.py"),
        "dsl_g1_verdict": g1["verdict"],
        "map_sha256": {r: maps[r].sha for r in ROLES},
        "g5_names_unmatched_on_A0": g5_unmatched,
        "counts": {"known_pool": len(records), **{f"eligible {t}": sum(r.get("tier") == t for r in records) for t in TIERS},
                   "drawn": drawn_n, "screened": len(rows),
                   **{f"survivors {t}": len(survivors[t]) for t in TIERS}, "wanted": WANTED,
                   "sufficient": selection is not None},
        "exclusion_counts": exclusion_counts,
        "rejection_counts": rejection_counts,
        "pool": records,
        "candidates_in_draw_order": rows,
        "survivors_ranked": {t: [{"a": r["a"], "b": r["b"], "familiarity": r["familiarity"], "detail": r["detail"]}
                                 for r in survivors[t]] for t in TIERS},
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    in_dir("dsl_prescreen.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str),
                                            encoding="utf-8", newline="\n")
    write_md(out, survivors)
    if selection is None:
        print(f"[dsl] NOT ENOUGH: {sum(len(v) for v in survivors.values())} survivors, {WANTED} wanted. Stop and "
              "report; the owner supplies pairs, which must pass the same gates.", flush=True)
        return 2
    doc = {"what": "DRP-AM7-2 step 8: 4 primaries and 2 ordered reserves per tier, before the owner's strike",
           "note": "Endpoint names, MBIDs, tiers and pool ranks only. Nothing here identifies a side.",
           "prescreen_script_sha256_lf": out["script_sha256_lf"], **selection, "finished_utc": out["finished_utc"]}
    in_dir("dsl_pairs_drawn.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8", newline="\n")
    print(f"[dsl] ENOUGH: {WANTED} selected into dsl_pairs_drawn.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
