"""`LBA-` stage 1 -- the cheap probe: how many artists does the pair table actually name?

The handoff records this as the design's one genuinely unknown quantity: "no document on the
record states how many artists the full pair table names ... the cheapest thing that could
change the design". It is cheaper than that. `U` at threshold 10 and `U` at threshold 3 are
distinct-artist counts over `A0.parquet` and `A5.parquet` -- two tables that already exist and
were sha-verified by task 1. Seconds each, no scan of the 21 GB `T`.

These are TABLE-LEVEL populations: `U`'s definition in s2.1 is "after the standard drop lists,
after the largest-component prune", and the prune needs a build. A table-level count is a
SUPERSET of the built node count, which is the conservative direction for a feasibility gate --
it over-estimates the census cost `LBA-G3` reads.

Checks the nesting the execution log derives: `U`(10) must be a subset of `U`(3).

    C:\\unsung-fast\\lbd-venv\\Scripts\\python.exe -u stage1_u_probe.py --out u_probe.json
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb

TABLES = {
    # label: (path, threshold, the LBA- arm whose U population this is)
    "U(threshold 10)": (r"C:\unsung-fast\lbd-pairs\A0\A0.parquet", 10, "LBA-A7"),
    "U(threshold 3)": (r"C:\unsung-fast\lbd-pairs\A5\A5.parquet", 3, "LBA-A9"),
}

POPULATIONS = {
    "V": r"C:\unsung-fast\lbd-archives\population_msw_mbids.txt",
    "P": r"C:\unsung-fast\lbd-archives\population_cxa_mbids.txt",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--memory-limit-gb", type=int, default=24)
    ap.add_argument("--temp-dir", type=Path, default=Path(r"D:/unsung-large-data/duckdb-temp"))
    args = ap.parse_args(argv)

    args.temp_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{args.memory_limit_gb}GB'")
    con.execute(f"PRAGMA temp_directory='{args.temp_dir.as_posix()}'")
    con.execute("PRAGMA preserve_insertion_order=false")

    results: dict[str, dict] = {}
    for label, (raw, threshold, arm) in TABLES.items():
        p = Path(raw).as_posix()
        t0 = time.time()
        pairs, artists = con.execute(f"""
            SELECT count(*),
                   (SELECT count(*) FROM (
                        SELECT mbid0 AS m FROM read_parquet('{p}')
                        UNION
                        SELECT mbid1 AS m FROM read_parquet('{p}')
                   ))
              FROM read_parquet('{p}')
        """).fetchone()
        wall = time.time() - t0
        results[label] = {
            "table": raw, "threshold": threshold, "arm": arm,
            "pairs": pairs, "artists_table_level": artists,
            "archive_neighbour_rows_unrestricted": 2 * pairs,
            "wall_clock_s": round(wall, 1),
        }
        print(f"[probe] {label:<18} pairs {pairs:>12,}  distinct artists {artists:>10,}"
              f"  ({wall:.1f} s)", flush=True)

    # The nesting the execution log derives, checked rather than assumed.
    a0 = Path(TABLES["U(threshold 10)"][0]).as_posix()
    a5 = Path(TABLES["U(threshold 3)"][0]).as_posix()
    t0 = time.time()
    (leak,) = con.execute(f"""
        WITH u10 AS (SELECT mbid0 AS m FROM read_parquet('{a0}')
                     UNION SELECT mbid1 FROM read_parquet('{a0}')),
             u3  AS (SELECT mbid0 AS m FROM read_parquet('{a5}')
                     UNION SELECT mbid1 FROM read_parquet('{a5}'))
        SELECT count(*) FROM (SELECT m FROM u10 EXCEPT SELECT m FROM u3)
    """).fetchone()
    nesting = {
        "claim": "U(10) is a subset of U(3) -- a looser bar cannot drop a pair a tighter bar kept",
        "members_of_U10_absent_from_U3": leak,
        "holds": leak == 0,
        "wall_clock_s": round(time.time() - t0, 1),
    }
    print(f"[probe] nesting check: {leak} members of U(10) absent from U(3) "
          f"-- {'HOLDS' if leak == 0 else 'FAILS'}", flush=True)

    # How much of U(3) lies outside the two pinned populations -- the quantity that drives
    # the union, and with it LBA-G3's census cost.
    pops = {}
    for name, raw in POPULATIONS.items():
        members = [ln.strip() for ln in Path(raw).read_text(encoding="utf-8").splitlines() if ln.strip()]
        con.execute(f"CREATE OR REPLACE TEMP TABLE pop_{name} (m VARCHAR)")
        con.executemany(f"INSERT INTO pop_{name} VALUES (?)", [(m,) for m in members])
        pops[name] = len(members)

    t0 = time.time()
    union_total, u3_only, v_only, p_only = con.execute(f"""
        WITH u3 AS (SELECT mbid0 AS m FROM read_parquet('{a5}')
                    UNION SELECT mbid1 FROM read_parquet('{a5}')),
             un AS (SELECT m FROM u3 UNION SELECT m FROM pop_V UNION SELECT m FROM pop_P)
        SELECT (SELECT count(*) FROM un),
               (SELECT count(*) FROM (SELECT m FROM u3
                                      EXCEPT SELECT m FROM pop_V
                                      EXCEPT SELECT m FROM pop_P)),
               (SELECT count(*) FROM (SELECT m FROM pop_V EXCEPT SELECT m FROM u3)),
               (SELECT count(*) FROM (SELECT m FROM pop_P EXCEPT SELECT m FROM u3))
    """).fetchone()
    union = {
        "definition": "U(3) UNION V UNION P -- the union of all nine cells' populations, "
                      "by the nesting above",
        "union_members": union_total,
        "in_U3_only": u3_only,
        "in_V_but_not_U3": v_only,
        "in_P_but_not_U3": p_only,
        "V_size": pops["V"], "P_size": pops["P"],
        "wall_clock_s": round(time.time() - t0, 1),
    }
    print(f"[probe] union of all nine populations (table level): {union_total:,}", flush=True)

    out = {
        "task": "LBA- stage 1 -- U population probe (proposal 1, run before the instruments)",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "caveat": "TABLE-LEVEL populations. U's definition applies the drop lists and the "
                  "largest-component prune, both of which need a build. These counts are a "
                  "superset of the built node count -- conservative for LBA-G3.",
        "duckdb_version": duckdb.__version__,
        "tables": results,
        "nesting_check": nesting,
        "union": union,
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n[probe] written to {args.out}", flush=True)
    return 0 if nesting["holds"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
