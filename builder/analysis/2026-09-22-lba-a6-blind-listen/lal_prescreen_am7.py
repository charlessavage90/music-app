"""`LBA-AM7-4`: `LBA-AM6-2` steps 4-8 over the owner-vetted pool — committed with the amendment,
before its first run.

⚠ **OUTPUTS MAP-LABELLED** (`lal_am7_prescreen.json`, `.md`): on the runner brief's do-not-read list.
`lal_pairs_drawn_am7.json` carries endpoint names, MBIDs and pool ranks only.

The pool is `lal_am7_known.json`'s `pool`, in order (`LBA-AM7-2` step 6); the familiarity list is
`lal_am7_familiar.json` plus the pool (`LBA-AM7-3`). Everything else — membership, adjacency in
either map, the listen-reserve pair bans, the ladder, Gates L/D/N, the ranking and the 8+4 selection
— is **`lal_prescreen.py`'s committed code, imported unchanged**, and `lal_journeys.py`'s ladder.

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \\
      analysis/2026-09-22-lba-a6-blind-listen/lal_prescreen_am7.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import (  # noqa: E402
    DEPTHS,
    LBL_PAIRS1,
    LBL_PAIRS1_SHA,
    LBL_PAIRS2,
    LBL_PAIRS2_SHA,
    ROLES,
    in_dir,
    load_pinned_maps,
    read_pins,
    sha256_of,
    use_api_src,
)
from lal_pool_am7 import FAMILIAR, KNOWN, presented_endpoints  # noqa: E402
from lal_prescreen import WANTED, draw, familiarity, rank_key, screen, select  # noqa: E402


def pool_from_known(known: dict, excluded: dict[str, str], nodes: dict[str, set[str]]) -> list[dict]:
    """`LBA-AM7-2` step 6 + `LBA-AM6-2` steps 2 and 4, re-checked. Pool rank = position in pool."""
    out = []
    for rank, a in enumerate(known["pool"], 1):
        rec = {"rank": rank, "name": a["name"], "mbid": a["mbid"]}
        if a["mbid"] in excluded:
            rec["excluded"] = f"endpoint of a presented pair ({excluded[a['mbid']]})"
        elif any(a["mbid"] not in nodes[r] for r in ROLES):
            rec["excluded"] = "not a node of both maps"
        out.append(rec)
    return out


def write_md(out: dict, survivors: list) -> None:
    c = out["counts"]
    lines = ["# `LAL-` pre-screen over the `LBA-AM7` pool", "",
             "⚠ **MAP-LABELLED — a blind runner must not read this file or `lal_am7_prescreen.json`.**", "",
             "| | |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k, v in c.items()]
    lines += ["", "| rejected at | pairs |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in sorted(out["rejection_counts"].items())]
    lines += ["", "| rank | A | B | novel differing (d0+d10+d20) | familiar / distinct |", "|---|---|---|---:|---:|"]
    for i, r in enumerate(survivors, 1):
        f = r["familiarity"]
        lines.append(f"| {i} | {r['a']['name']} | {r['b']['name']} | {sum(r['detail']['novel_symdiff'].values())} | "
                     f"{f['familiar_interior']}/{f['distinct_interior']} |")
    in_dir("lal_am7_prescreen.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    use_api_src()
    from artistpath_api.config import ApiConfig
    from lal_journeys import adjacent, ladder, press_key

    known = json.loads(in_dir(KNOWN).read_text(encoding="utf-8"))
    familiar = set(json.loads(in_dir(FAMILIAR).read_text(encoding="utf-8"))["mbids"]) | {a["mbid"] for a in known["pool"]}
    excluded = presented_endpoints()

    def pinned(path, sha):
        if sha256_of(path) != sha:
            raise SystemExit(f"REFUSING: {path.name} is not the pinned file")
        return json.loads(path.read_text(encoding="utf-8"))
    forbidden = {frozenset((p["a"]["mbid"], p["b"]["mbid"]))
                 for p in pinned(LBL_PAIRS1, LBL_PAIRS1_SHA)["listen1"]["reserve"] + pinned(LBL_PAIRS2, LBL_PAIRS2_SHA)["reserve"]}

    maps = load_pinned_maps()
    nodes = {r: set(maps[r]["store"].mbids) for r in ROLES}
    records = pool_from_known(known, excluded, nodes)
    eligible = [r for r in records if "excluded" not in r]

    def adjacent_in_either(a: str, b: str) -> bool:
        return any(adjacent(maps[r]["store"], maps[r]["store"].id_by_mbid[a], maps[r]["store"].id_by_mbid[b]) for r in ROLES)

    drawn = draw(eligible, adjacent_in_either, forbidden)
    print(f"[am7] pool {len(records)}; eligible {len(eligible)}; drew {len(drawn)}; familiarity {len(familiar)}", flush=True)
    cfg = ApiConfig()
    keys = {r: press_key(maps[r]["store"], maps[r]["raw_fame"]) for r in ROLES}
    rows = []
    for i, pair in enumerate(drawn, 1):
        per_map = {}
        for r in ROLES:
            s = maps[r]["store"]
            lad = ladder(s, s.id_by_mbid[pair["a"]["mbid"]], s.id_by_mbid[pair["b"]["mbid"]], keys[r], cfg)
            per_map[r] = {d: [s.mbids[v] for v in path[1:-1]] for d, (path, _k, _p) in lad.items()}
        reason, detail = screen(per_map, familiar)
        rows.append({"a": pair["a"], "b": pair["b"], "detail": detail, "familiarity": familiarity(per_map, familiar),
                     "rejected": reason, "kept": reason is None})
        print(f"[am7] {i}/{len(drawn)}: " + ("KEPT" if reason is None else f"rejected {reason[:1]}"), flush=True)

    survivors = sorted([r for r in rows if r["kept"]], key=rank_key)
    rej: dict = {}
    for r in rows:
        if r["rejected"]:
            k = f"gate {r['rejected'][:1]}"
            rej[k] = rej.get(k, 0) + 1
    selection = select(survivors)
    out = {"what": "LAL- pre-screen over the LBA-AM7 pool", "warning": "MAP-LABELLED. A blind runner must not read this file.",
           "script_sha256": sha256_of(Path(__file__)),
           "prescreen_module_sha256": sha256_of(Path(__file__).with_name("lal_prescreen.py")),
           "journeys_module_sha256": sha256_of(Path(__file__).with_name("lal_journeys.py")),
           "known_sha256": sha256_of(in_dir(KNOWN)), "maps_pin": read_pins(), "depths": list(DEPTHS),
           "counts": {"pool": len(records), "eligible": len(eligible), "drawn": len(drawn), "survivors": len(survivors),
                      "wanted": WANTED, "familiarity_mbids": len(familiar)},
           "rejection_counts": rej, "pool": records, "candidates_in_draw_order": rows,
           "survivors_ranked": [{"a": r["a"], "b": r["b"], "familiarity": r["familiarity"], "detail": r["detail"]} for r in survivors],
           "finished_utc": datetime.now(timezone.utc).isoformat()}
    in_dir("lal_am7_prescreen.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    write_md(out, survivors)
    if selection is None:
        print(f"[am7] NOT ENOUGH: {len(survivors)} survivors. LBA-AM7-2 step 7: list the next 100.", flush=True)
        return 2
    in_dir("lal_pairs_drawn_am7.json").write_text(json.dumps(
        {"what": "LBA-AM7: 8 primaries and 4 ordered reserves, before the owner's strike",
         "note": "Endpoint names, MBIDs and pool ranks only.", "prescreen_script_sha256": out["script_sha256"],
         **selection, "finished_utc": out["finished_utc"]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[am7] ENOUGH: 12 selected into lal_pairs_drawn_am7.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
