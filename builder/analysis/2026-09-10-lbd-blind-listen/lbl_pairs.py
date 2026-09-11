"""`LBL-` pair draw — one fixed rule, run once, before anything is built (`LBD-AM5`).

THE RULE. Fixed before this script first ran; the commit adding this file precedes the commit
adding its output, and that ordering is the evidence.

  1. POOL. The owner's familiarity-ranked artists — `gbl_pair_candidates.json`'s `usable` list,
     in its committed order (listening time from his 2026-08-04 Spotify export, derived by
     `gbl_pairs.py`). No export is read here; the raw export never enters the repo.
  2. EXCLUDE EVERY `GBL-AM1` ENDPOINT (`gbl_pairs_approved.json`, sha-pinned). He heard journeys
     between those artists in the `GBL-` listen and audited them card by card in `CAU-`, and
     the served map is the lineage of the arm he heard. A journey he remembers identifies a
     side, and the blind is the one thing this protocol cannot recover once spent.
  3. KEEP an artist only if it resolved to one MBID in both `GBL-` maps (`status == "ok"`), that
     MBID is a node of the served map, and it has at least one partner inside the served
     population in `LBD-A0`'s derived table. The last is necessary for the artist to be a node of
     `LBD-A0V`, not sufficient; the generation gates catch the rest mechanically.
  4. PAIR GREEDILY IN POOL ORDER. Each artist pairs with the EARLIEST still-unpaired artist it is
     not directly connected to in the served map; otherwise it waits. `gbl_pairs.py` paired
     neighbours in the familiarity ranking so both ends are demonstrably known (REQ-41); the
     adjacency screen is `GBL-` results §6.5 (adjacent famous endpoints left nothing to judge).
     The same screen is applied to each built `LBD-` arm at generation, so the pairs finally
     heard are non-adjacent in both maps of their comparison.
  5. DEAL. Pairs in creation order go alternately to listen 1 (served map vs `LBD-A0V`) and
     listen 2 (`LBD-A0V` vs `LBD-A5V`), eight each; the next eight alternately become four
     ORDERED reserves each. Alternation keeps the two listens' familiarity spread level.
     Listen 2 gets its own pairs because a pair heard in listen 1 would carry the same memory
     tell into it.

Deterministic: no randomness, no journey computed, no `LBD-` map opened (none exists yet).

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run --with duckdb python -u analysis/2026-09-10-lbd-blind-listen/lbl_pairs.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from lbl_common import (
    A0_MANIFEST,
    A0_PARQUET,
    GBL_APPROVED,
    GBL_APPROVED_SHA,
    GBL_CANDIDATES,
    PAIRS_PER_LISTEN,
    RESERVES_PER_LISTEN,
    SERVED,
    in_dir,
    sha256_of,
    verified_store,
)

NEEDED = 2 * (PAIRS_PER_LISTEN + RESERVES_PER_LISTEN)


def gbl_endpoints() -> set[str]:
    digest = sha256_of(GBL_APPROVED)
    if digest != GBL_APPROVED_SHA:
        raise SystemExit(f"REFUSING: {GBL_APPROVED.name} sha256 {digest} != GBL-AM1's {GBL_APPROVED_SHA}")
    approved = json.loads(GBL_APPROVED.read_text(encoding="utf-8"))
    return {p[side]["mbid"] for p in approved["pairs"] for side in ("a", "b")}


def pool_records(candidates: dict, excluded_endpoints: set[str], served_nodes: set[str]) -> list[dict]:
    """Steps 1-3a: every usable artist, in committed order, with an exclusion reason or none."""
    records = []
    for rank, r in enumerate(candidates["usable"], 1):
        v0, g = r.get("v0_nodes") or [], r.get("g_nodes") or []
        mbid = v0[0]["mbid"] if len(v0) == 1 else None
        rec = {"rank": rank, "name": r["name"], "mbid": mbid, "minutes": round(r["ms_played"] / 60_000)}
        if r.get("status") != "ok" or len(v0) != 1 or len(g) != 1 or g[0]["mbid"] != mbid:
            rec["excluded"] = "not one MBID in both GBL- maps"
        elif mbid in excluded_endpoints:
            rec["excluded"] = "GBL-AM1 endpoint"
        elif mbid not in served_nodes:
            rec["excluded"] = "not a node of the served map"
        records.append(rec)
    return records


def a0_partners_in_served(mbids: list[str], served_nodes: set[str], memory_limit_gb: int) -> dict[str, int]:
    """Distinct partners inside the served population in `LBD-A0`'s derived table (both halves)."""
    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{int(memory_limit_gb)}GB'")
    con.execute("CREATE TABLE v(mbid VARCHAR)")
    con.executemany("INSERT INTO v VALUES (?)", [(m,) for m in sorted(served_nodes)])
    con.execute("CREATE TABLE c(mbid VARCHAR)")
    con.executemany("INSERT INTO c VALUES (?)", [(m,) for m in mbids])
    pq = A0_PARQUET.as_posix()
    rows = con.execute("""
        SELECT m, count(DISTINCT p) FROM (
            SELECT mbid0 AS m, mbid1 AS p FROM read_parquet(?)
             WHERE mbid0 IN (SELECT mbid FROM c) AND mbid1 IN (SELECT mbid FROM v)
            UNION ALL
            SELECT mbid1 AS m, mbid0 AS p FROM read_parquet(?)
             WHERE mbid1 IN (SELECT mbid FROM c) AND mbid0 IN (SELECT mbid FROM v)
        ) GROUP BY m
    """, [pq, pq]).fetchall()
    con.close()
    return {m: int(n) for m, n in rows}


def draw(eligible: list[dict], adjacent) -> list[dict]:
    """Step 4. `adjacent(a_mbid, b_mbid) -> bool` is the served map's direct connection."""
    unpaired: list[dict] = []
    pairs: list[dict] = []
    for rec in eligible:
        partner = None
        for u in unpaired:
            if adjacent(u["mbid"], rec["mbid"]):
                rec.setdefault("skipped_as_adjacent_to", []).append(u["name"])
                continue
            partner = u
            break
        if partner is None:
            unpaired.append(rec)
        else:
            unpaired.remove(partner)
            pairs.append({"a": partner, "b": rec})
        if len(pairs) == NEEDED:
            break
    return pairs


def deal(pairs: list[dict]) -> dict:
    """Step 5."""
    n, r = PAIRS_PER_LISTEN, RESERVES_PER_LISTEN
    if len(pairs) < 2 * (n + r):
        raise SystemExit(f"only {len(pairs)} pairs could be drawn; the rule needs {2 * (n + r)}")
    return {
        "listen1": {"primary": pairs[0:2 * n:2], "reserve": pairs[2 * n:2 * (n + r):2]},
        "listen2": {"primary": pairs[1:2 * n:2], "reserve": pairs[2 * n + 1:2 * (n + r):2]},
    }


def _slim(pair: dict) -> dict:
    return {side: {k: pair[side][k] for k in ("name", "mbid", "rank", "minutes")} for side in ("a", "b")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--memory-limit-gb", type=int, default=4)
    args = ap.parse_args(argv)

    excluded_endpoints = gbl_endpoints()
    candidates_sha = sha256_of(GBL_CANDIDATES)
    candidates = json.loads(GBL_CANDIDATES.read_text(encoding="utf-8"))
    store, _manifest, served_sha = verified_store(SERVED)
    served_nodes = set(store.mbids)
    a0_manifest = json.loads(A0_MANIFEST.read_text(encoding="utf-8"))
    a0_sha = sha256_of(A0_PARQUET)
    if a0_sha != a0_manifest["out_sha256"] or (a0_manifest["threshold"], a0_manifest["limit"]) != (10, 100):
        raise SystemExit("REFUSING: A0.parquet is not LBD-A0 as its manifest records it")
    print(f"[pairs] served {SERVED.name} sha256 {served_sha}  nodes {len(served_nodes):,}", flush=True)
    print(f"[pairs] A0.parquet sha256 {a0_sha}  candidates sha256 {candidates_sha}", flush=True)

    records = pool_records(candidates, excluded_endpoints, served_nodes)
    open_mbids = [r["mbid"] for r in records if "excluded" not in r]
    partners = a0_partners_in_served(open_mbids, served_nodes, args.memory_limit_gb)
    for rec in records:
        if "excluded" in rec:
            continue
        rec["a0_partners_in_served"] = partners.get(rec["mbid"], 0)
        if rec["a0_partners_in_served"] == 0:
            rec["excluded"] = "no partner inside the served population in LBD-A0's table"
    eligible = [r for r in records if "excluded" not in r]

    def adjacent(a: str, b: str) -> bool:
        ib = store.id_by_mbid[b]
        return any(n == ib for n, _ in store.neighbours_of(store.id_by_mbid[a]))

    pairs = draw(eligible, adjacent)
    dealt = deal(pairs)
    out = {
        "amendment": "LBD-AM5",
        "rule_script_sha256": sha256_of(Path(__file__)),
        "inputs": {
            "candidates": {"file": GBL_CANDIDATES.name, "sha256": candidates_sha},
            "gbl_am1": {"file": GBL_APPROVED.name, "sha256": GBL_APPROVED_SHA,
                        "endpoints_excluded": len(excluded_endpoints)},
            "served_map": {"file": SERVED.name, "sha256": served_sha, "nodes": len(served_nodes)},
            "lbd_a0_table": {"file": str(A0_PARQUET), "sha256": a0_sha},
        },
        "pool": records,
        "exclusion_counts": {},
        "pairs_in_creation_order": [_slim(p) for p in pairs],
        "listen1": {k: [_slim(p) for p in v] for k, v in dealt["listen1"].items()},
        "listen2": {k: [_slim(p) for p in v] for k, v in dealt["listen2"].items()},
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    for rec in records:
        reason = rec.get("excluded", "eligible")
        out["exclusion_counts"][reason] = out["exclusion_counts"].get(reason, 0) + 1
    in_dir("lbl_pairs.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = ["# `LBL-` pairs — drawn by `lbl_pairs.py`'s fixed rule (`LBD-AM5`)", "",
             f"Pool: {len(records)} familiarity-ranked artists; "
             + ", ".join(f"{k}: {v}" for k, v in sorted(out["exclusion_counts"].items())) + ".", ""]
    for listen, title in (("listen1", "Listen 1 — the served map against `LBD-A0V`"),
                          ("listen2", "Listen 2 — `LBD-A0V` against `LBD-A5V` (not prepared until listen 1 is heard)")):
        for part in ("primary", "reserve"):
            lines += [f"## {title} — {part}", "", "| # | A | B | minutes (A/B) |", "|---|---|---|---|"]
            for i, p in enumerate(out[listen][part], 1):
                lines.append(f"| {i} | {p['a']['name']} | {p['b']['name']} | {p['a']['minutes']}/{p['b']['minutes']} |")
            lines.append("")
    in_dir("lbl_pairs.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[pairs] eligible {len(eligible)}; drew {len(pairs)} pairs; wrote lbl_pairs.json + lbl_pairs.md", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
