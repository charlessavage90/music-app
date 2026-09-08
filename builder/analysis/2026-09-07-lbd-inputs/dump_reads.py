"""`LBD-` Task 1 — the pinned dump's identity, and two reads over it.

Frozen: stdlib + DuckDB only, no project imports. Reads the parquet dump read-only
and writes its outputs under `D:\\unsung-large-data\\lbd-inputs\\` (`LBD-D8`).

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-07-lbd-inputs/dump_reads.py

Three sections, each with its plain sentence:

  IDENTITY  What exactly is the file we are about to spend the track on?
            Row count and per-column size come from parquet footers, not a scan.

  R-SUPPLY  Of the 29,892 artists the crawl extension added -- the ones that
            arrived with almost no connections -- how many appear in
            ListenBrainz's listens at all, and how many are listened to by
            enough different people to be able to clear the score threshold?

            This BOUNDS THE WHOLE TRACK and is why it runs before any arm. An
            added artist that no one in the corpus played can never gain an
            edge, at any threshold and any cap; that outcome is neither of the
            two explanations `LBD-R1` contrasts. Derivation item 11.

            The user count matters because of how LB scores a pair: each user
            contributes at most `contribution` (3 at ALG-B's parameters), and
            `HAVING score > threshold` is strict on an integer, so a pair needs
            at least ceil((threshold+1)/contribution) DISTINCT users before it
            can survive at all -- 4 users at threshold 10. That is arithmetic on
            LB's own SQL, not an estimate.

  R-USERS   Which accounts hold the listening, and could a handful of heavy
            users or bots be shaping the pairs? (`LBD-R9`, the cheap half.)
            DECIDES NOTHING -- the pre-registration decides whether a user
            filter is an arm.

Nothing here is a criterion and nothing here is a gate.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import duckdb

DUMP_DIR = Path(r"D:\unsung-large-data\listenbrainz-spark-dump-2647-20260901-000002-full")
GLOB = str(DUMP_DIR / "*.parquet").replace("\\", "/")
OUT_DIR = Path(r"D:\unsung-large-data\lbd-inputs")
ADDED = OUT_DIR / "cxr_added_mbids.txt"  # written by cxr_added_set.py

# ALG-B's parameters, the ones the served map's archive was fetched at. Used here
# only to turn the threshold into a minimum distinct-user count.
ALGB_THRESHOLD = 10
ALGB_CONTRIBUTION = 3
MIN_USERS_FOR_THRESHOLD = -(-(ALGB_THRESHOLD + 1) // ALGB_CONTRIBUTION)  # ceil, = 4


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='20GB'")
    con.execute("PRAGMA temp_directory='D:/unsung-large-data/duckdb-tmp'")
    con.execute("PRAGMA threads=16")
    con.execute("PRAGMA disable_progress_bar")  # it floods a redirected log
    return con


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def identity(con: duckdb.DuckDBPyConnection) -> dict:
    section("IDENTITY -- what the pinned input is")
    meta = {}
    for name in ("SCHEMA_SEQUENCE", "TIMESTAMP"):
        p = DUMP_DIR / name
        meta[name] = p.read_text().strip() if p.exists() else None
        print(f"  {name:<18} {meta[name]}")
    for name in ("START_TIMESTAMP", "END_TIMESTAMP"):
        p = DUMP_DIR / name
        if p.exists():
            meta[name] = p.read_text().strip()
            print(f"  {name:<18} {meta[name]}")
        else:
            meta[name] = None
            print(f"  {name:<18} ABSENT -- full dumps carry TIMESTAMP only")

    files, rows = con.execute(
        f"SELECT count(*), sum(num_rows) FROM parquet_file_metadata('{GLOB}')"
    ).fetchone()
    meta["parquet_files"] = files
    meta["rows"] = rows
    print(f"  parquet files      {files:,}")
    print(f"  listens (rows)     {rows:,}")

    print("\n  compressed bytes per column (parquet footers, no scan):")
    cols = con.execute(
        f"SELECT path_in_schema, sum(total_compressed_size) FROM parquet_metadata('{GLOB}')"
        " GROUP BY 1 ORDER BY 2 DESC"
    ).fetchall()
    meta["column_bytes"] = {c: int(b) for c, b in cols}
    for c, b in cols:
        print(f"    {c:<34} {b / 1e9:8.1f} GB")
    return meta


def read_supply(con: duckdb.DuckDBPyConnection) -> dict:
    section("R-SUPPLY -- do the added artists appear in the listens at all?")
    added = [m for m in ADDED.read_text(encoding="utf-8").split("\n") if m]
    print(f"  added set: {len(added):,} MBIDs from {ADDED.name}")
    print(f"  sha256     {sha256_file(ADDED)}")
    con.execute("CREATE TEMP TABLE added(mbid VARCHAR)")
    con.executemany("INSERT INTO added VALUES (?)", [(m,) for m in added])

    t = time.time()
    con.execute(
        f"""
        CREATE TEMP TABLE supply AS
        SELECT a.mbid                                             AS mbid
             , count(*)                                           AS rows_any
             , count(*) FILTER (WHERE l.mapped)                   AS rows_mapped
             , count(DISTINCT l.user_id) FILTER (WHERE l.mapped)  AS users_mapped
          FROM (
                SELECT user_id
                     , (recording_mbid IS NOT NULL AND recording_mbid != '') AS mapped
                     , unnest(artist_credit_mbids) AS mbid
                  FROM read_parquet('{GLOB}')
               ) l
          JOIN added a USING (mbid)
      GROUP BY 1
        """
    )
    elapsed = time.time() - t
    print(f"  scan wall-clock {elapsed / 60:.1f} min")

    n = len(added)
    present_any, present_mapped = con.execute(
        "SELECT count(*), count(*) FILTER (WHERE rows_mapped > 0) FROM supply"
    ).fetchone()
    print()
    print(f"  {'appear at all':<44} {present_any:>7,} / {n:,} = {100*present_any/n:6.2f}%")
    print(f"  {'appear in MAPPED listens (the job sees these)':<44}"
          f" {present_mapped:>7,} / {n:,} = {100*present_mapped/n:6.2f}%")
    print(f"  {'ABSENT from the corpus entirely':<44}"
          f" {n-present_any:>7,} / {n:,} = {100*(n-present_any)/n:6.2f}%")

    print()
    print("  distinct users per added artist, over mapped listens")
    print(f"  (a pair needs >= {MIN_USERS_FOR_THRESHOLD} distinct users to clear"
          f" threshold {ALGB_THRESHOLD} at contribution {ALGB_CONTRIBUTION})")
    buckets = con.execute(
        """
        SELECT sum(CASE WHEN users_mapped = 0 THEN 1 ELSE 0 END)
             , sum(CASE WHEN users_mapped = 1 THEN 1 ELSE 0 END)
             , sum(CASE WHEN users_mapped BETWEEN 2 AND 3 THEN 1 ELSE 0 END)
             , sum(CASE WHEN users_mapped >= 4 THEN 1 ELSE 0 END)
             , sum(CASE WHEN users_mapped >= 10 THEN 1 ELSE 0 END)
             , sum(CASE WHEN users_mapped >= 50 THEN 1 ELSE 0 END)
          FROM supply
        """
    ).fetchone()
    labels = ["0 users", "1 user", "2-3 users", ">= 4 users", ">= 10 users", ">= 50 users"]
    absent = n - present_any
    out = {}
    for label, v in zip(labels, buckets):
        v = int(v or 0)
        # the absent artists are 0-user too, and are not rows in `supply`
        v_total = v + absent if label == "0 users" else v
        out[label] = v_total
        print(f"    {label:<14} {v_total:>7,}  {100*v_total/n:6.2f}%")

    for q in (0.1, 0.25, 0.5, 0.75, 0.9):
        v = con.execute(f"SELECT quantile_cont(users_mapped, {q}) FROM supply").fetchone()[0]
        print(f"    users q{q:<5} {v:,.0f}   (over the {present_any:,} present only)")

    con.execute(
        f"COPY supply TO '{(OUT_DIR / 'cxr_added_dump_supply.parquet').as_posix()}'"
        " (FORMAT PARQUET)"
    )
    print(f"\n  wrote {OUT_DIR / 'cxr_added_dump_supply.parquet'}")
    return {"present_any": present_any, "present_mapped": present_mapped,
            "absent": absent, "buckets": out, "scan_minutes": round(elapsed / 60, 1)}


def read_users(con: duckdb.DuckDBPyConnection) -> dict:
    section("R-USERS -- heavy users and bots (LBD-R9, cheap half). DECIDES NOTHING.")
    t = time.time()
    con.execute(
        f"CREATE TEMP TABLE uc AS SELECT user_id, count(*) AS n"
        f" FROM read_parquet('{GLOB}') GROUP BY 1"
    )
    total, nusers = con.execute("SELECT sum(n), count(*) FROM uc").fetchone()
    print(f"  scan wall-clock {(time.time()-t)/60:.1f} min")
    print(f"  total listens {total:,}   distinct users {nusers:,}")
    print("\n  top 20 accounts")
    cum = 0
    top = []
    for i, (u, cnt) in enumerate(
        con.execute("SELECT user_id, n FROM uc ORDER BY n DESC LIMIT 20").fetchall(), 1
    ):
        cum += cnt
        top.append({"user_id": u, "listens": cnt})
        print(f"    {i:>2}  user {u:<9} {cnt:>12,}  {100*cnt/total:6.3f}%  cum {100*cum/total:6.3f}%")
    print()
    shares = {}
    for k in (20, 100, 1000):
        s = con.execute(f"SELECT sum(n) FROM (SELECT n FROM uc ORDER BY n DESC LIMIT {k})").fetchone()[0]
        shares[k] = 100 * s / total
        print(f"    top {k:>4} accounts hold {s:>14,} listens = {shares[k]:6.3f}%")
    print()
    qs = {}
    for q in (0.5, 0.9, 0.99, 0.999):
        v = con.execute(f"SELECT quantile_cont(n, {q}) FROM uc").fetchone()[0]
        qs[q] = v
        print(f"    listens per account q{q}: {v:,.0f}")
    return {"total_listens": total, "distinct_users": nusers, "top20": top,
            "top_shares_pct": shares, "quantiles": qs}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = connect()
    result = {
        "dump_dir": str(DUMP_DIR),
        "identity": identity(con),
        "r_supply": read_supply(con),
        "r_users": read_users(con),
    }
    out = OUT_DIR / "dump_reads.json"
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
