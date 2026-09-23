"""`LBA-AM7-2` and `-3`: the pool candidates and the familiarity list, from the owner's EXTENDED
Spotify history — committed with the amendment, before its first run.

Governing text: `LBA-AM7` in the pre-registration §11. It wins where this differs.

  1. Qualifying stream: an Audio record with an artist name and ms_played >= 30 000.
  2. Per artist: distinct_tracks (distinct spotify_track_uri), plays, years, minutes.
  3. Order: distinct_tracks desc, plays desc, name — breadth of listening, not volume.
  4. Resolution: `artistpath_api.search.normalise` against `names` in BOTH maps; pool-eligible only
     with exactly one node in each and the same MBID; `LBA-AM6-2` step 2's presented endpoints out.
  5. The list shown to him: the first 150 eligible (or `--offset`/`--count` for LBA-AM7-2 step 7),
     names only, numbered. He names the ones he does NOT know (`record`).
  LBA-AM7-3. Familiarity: every artist with >= 1 qualifying stream, every matching node in either
     map (homonyms included), plus the known pool — counts only.

Personal data: only four fields of each stream record are read (artist name, track URI, ms played,
year). Only per-artist derived counts leave this script.

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \\
      analysis/2026-09-22-lba-a6-blind-listen/lal_pool_am7.py build
    ... lal_pool_am7.py record --unknown 3 17 42 --answer "<his reply>"
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import (  # noqa: E402
    GBL_APPROVED,
    GBL_APPROVED_SHA,
    LBL_PAIRS1,
    LBL_PAIRS1_SHA,
    LBL_PAIRS2,
    LBL_PAIRS2_SHA,
    ROLES,
    in_dir,
    load_pinned_maps,
    sha256_of,
    use_api_src,
)

HISTORY_DIR = Path(r"D:\unsung-large-data\Owner's Spotify Extended Streaming History")
MIN_MS = 30_000
LIST_COUNT = 150
CANDIDATES = "lal_am7_candidates.json"   # the eligible artists in order, with derived counts
LIST_MD = "lal_am7_list.md"              # what he reads: numbers and names only
FAMILIAR = "lal_am7_familiar.json"       # MBIDs only
KNOWN = "lal_am7_known.json"             # his answer, verbatim, and the resulting pool


def artist_stats(records: list[dict]) -> list[dict]:
    """Steps 1-3. Pure, so it is tested with no files."""
    agg: dict[str, dict] = {}
    for r in records:
        name = r.get("master_metadata_album_artist_name")
        if not name or (r.get("ms_played") or 0) < MIN_MS:
            continue
        a = agg.setdefault(name, {"name": name, "tracks": set(), "plays": 0, "years": set(), "ms": 0})
        if r.get("spotify_track_uri"):
            a["tracks"].add(r["spotify_track_uri"])
        a["plays"] += 1
        a["years"].add(str(r.get("ts", ""))[:4])
        a["ms"] += int(r["ms_played"])
    out = [{"name": a["name"], "distinct_tracks": len(a["tracks"]), "plays": a["plays"],
            "years": len(a["years"]), "minutes": round(a["ms"] / 60_000)} for a in agg.values()]
    return sorted(out, key=lambda a: (-a["distinct_tracks"], -a["plays"], a["name"]))


def name_index(store, normalise) -> dict[str, list[int]]:
    idx: dict[str, list[int]] = {}
    for i, n in enumerate(store.names):
        idx.setdefault(normalise(n), []).append(i)
    return idx


def resolve(stats: list[dict], stores: dict, indexes: dict, normalise, excluded: dict[str, str]) -> list[dict]:
    """Step 4. Annotates each artist with `mbid` or `excluded`, in order."""
    out = []
    for a in stats:
        q = normalise(a["name"])
        hits = {r: indexes[r].get(q, []) for r in ROLES}
        rec = dict(a)
        if any(len(h) != 1 for h in hits.values()):
            rec["excluded"] = "not exactly one node in both maps"
        else:
            mbids = {stores[r].mbids[hits[r][0]] for r in ROLES}
            if len(mbids) != 1:
                rec["excluded"] = "different MBIDs in the two maps"
            else:
                rec["mbid"] = mbids.pop()
                if rec["mbid"] in excluded:
                    rec["excluded"] = f"endpoint of a presented pair ({excluded[rec['mbid']]})"
        out.append(rec)
    return out


def familiar_mbids(stats: list[dict], stores: dict, indexes: dict, normalise) -> set[str]:
    """`LBA-AM7-3`: every matching node in either map for every artist with a qualifying stream."""
    out: set[str] = set()
    for a in stats:
        q = normalise(a["name"])
        for r in ROLES:
            out.update(stores[r].mbids[i] for i in indexes[r].get(q, []))
    return out


def presented_endpoints() -> dict[str, str]:
    """`LBA-AM6-2` step 2, unchanged: sha-pinned, as `lal_prescreen.py` reads them."""
    def pinned(path, sha):
        if sha256_of(path) != sha:
            raise SystemExit(f"REFUSING: {path.name} is not the pinned file")
        return json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for label, plist in (("GBL-AM1", pinned(GBL_APPROVED, GBL_APPROVED_SHA)["pairs"]),
                         ("LBL listen 1", pinned(LBL_PAIRS1, LBL_PAIRS1_SHA)["listen1"]["primary"]),
                         ("LBL listen 2", pinned(LBL_PAIRS2, LBL_PAIRS2_SHA)["primary"])):
        for p in plist:
            for s in ("a", "b"):
                out.setdefault(p[s]["mbid"], label)
    return out


def read_history() -> list[dict]:
    """Only the four fields this amendment uses are kept from each record."""
    files = sorted(glob.glob(str(HISTORY_DIR / "Streaming_History_Audio_*.json")))
    if not files:
        raise SystemExit(f"no Streaming_History_Audio_*.json under {HISTORY_DIR}")
    keep = ("master_metadata_album_artist_name", "spotify_track_uri", "ms_played", "ts")
    return [{k: r.get(k) for k in keep} for f in files for r in json.loads(Path(f).read_text(encoding="utf-8"))]


def build(offset: int, count: int) -> int:
    use_api_src()
    from artistpath_api.search import normalise

    stats = artist_stats(read_history())
    maps = load_pinned_maps()
    stores = {r: maps[r]["store"] for r in ROLES}
    indexes = {r: name_index(stores[r], normalise) for r in ROLES}
    resolved = resolve(stats, stores, indexes, normalise, presented_endpoints())
    eligible = [a for a in resolved if "excluded" not in a]
    for pos, a in enumerate(eligible, 1):
        a["eligible_position"] = pos
    shown = eligible[offset: offset + count]

    familiar = familiar_mbids(stats, stores, indexes, normalise)
    in_dir(FAMILIAR).write_text(json.dumps({"what": "LBA-AM7-3 familiarity MBIDs",
                                            "mbids": sorted(familiar)}, indent=0) + "\n", encoding="utf-8")
    excl: dict[str, int] = {}
    for a in resolved:
        k = a.get("excluded", "eligible")
        excl[k] = excl.get(k, 0) + 1
    doc = {"what": "LBA-AM7-2: eligible pool candidates in order, derived counts only",
           "script_sha256": sha256_of(Path(__file__)), "qualifying_min_ms": MIN_MS,
           "artists_with_a_qualifying_stream": len(stats), "exclusion_counts": excl,
           "familiarity_mbids": len(familiar), "shown": {"offset": offset, "count": len(shown)},
           "eligible": eligible, "finished_utc": datetime.now(timezone.utc).isoformat()}
    in_dir(CANDIDATES).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [f"# `LBA-AM7` — artists {offset + 1}–{offset + len(shown)}: name every one you do NOT know", ""]
    lines += [f"{a['eligible_position']}. {a['name']}" for a in shown]
    in_dir(LIST_MD).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[am7] {len(stats)} artists with a qualifying stream; {len(eligible)} pool-eligible; "
          f"listed {offset + 1}-{offset + len(shown)}; familiarity {len(familiar)} MBIDs; {excl}", flush=True)
    return 0


def record(unknown: list[int], answer: str) -> int:
    """Steps 5-6. Everything listed and not named unknown is known, in list order."""
    doc = json.loads(in_dir(CANDIDATES).read_text(encoding="utf-8"))
    lo, n = doc["shown"]["offset"], doc["shown"]["count"]
    listed = [a for a in doc["eligible"] if lo < a["eligible_position"] <= lo + n]
    positions = {a["eligible_position"] for a in listed}
    bad = sorted(set(unknown) - positions)
    if bad:
        raise SystemExit(f"not on the list shown: {bad}")
    prior = (json.loads(in_dir(KNOWN).read_text(encoding="utf-8")) if in_dir(KNOWN).exists()
             else {"answers": [], "pool": []})
    prior["answers"].append({"listed": [lo + 1, lo + n], "unknown": sorted(set(unknown)), "verbatim": answer,
                             "recorded_utc": datetime.now(timezone.utc).isoformat()})
    prior["pool"] += [{"name": a["name"], "mbid": a["mbid"]} for a in listed if a["eligible_position"] not in set(unknown)]
    prior["candidates_sha256"] = sha256_of(in_dir(CANDIDATES))
    in_dir(KNOWN).write_text(json.dumps(prior, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[am7] recorded: {len(listed) - len(set(unknown))} known of {len(listed)} listed; pool now {len(prior['pool'])}")
    return 0


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--offset", type=int, default=0)
    b.add_argument("--count", type=int, default=LIST_COUNT)
    r = sub.add_parser("record")
    r.add_argument("--unknown", type=int, nargs="*", default=[])
    r.add_argument("--answer", default="", help="the owner's reply, verbatim")
    args = ap.parse_args(argv)
    return build(args.offset, args.count) if args.cmd == "build" else record(args.unknown, args.answer)


if __name__ == "__main__":
    sys.exit(main())
