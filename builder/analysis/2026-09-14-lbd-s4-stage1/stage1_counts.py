"""`LBA-` stage 1 proper -- derive and count all nine cells, and read `LBA-G3`.

`LBA-D8` stage 1: "filters and window functions over `T`, plus a `GROUP BY` for each cell's
distinct-artist count and pair count, and the count of union members absent from the census
coverage store. Minutes to a couple of hours, no emission, no build."

Three tables, none re-derived here. The two that the record pins are CHECKED against their
pins and the script refuses on a mismatch; the third has no pin because this session created
it, so its digest is RECORDED rather than verified, and the output says which is which:
    threshold 10 -> A0.parquet   (already existed; LBD-A0)      -- pinned, checked
    threshold  7 -> T7.parquet   (derived by stage1_derive_t7.py, lbd_derive.py unedited)
                                                                -- no pin; digest recorded
    threshold  3 -> A5.parquet   (already existed; LBD-A5)      -- pinned, checked

Three population rules (s2.1):
    V -- the pinned node set of the served map      (58,838 artists)
    P -- the pinned node set of the extended crawl  (88,685 artists)
    U -- every artist the arm's own table names     (derived per arm; LBA-X6)

UNITS. `archive_neighbour_rows` is `LBA-G2`'s unit -- **two per pair, pre-cap** -- and is NEVER
CSR entries. s5's warning: three edge units are in play in this track and the served-population
README s0 records a build refused once for confusing two of them.

GREEN CHECK, not a criterion. `LBA-A1` and `LBA-A3` are `LBD-A0V` and `LBD-A5V`, whose emitted
pair counts, payload counts, neighbour rows and absent-from-table counts are owned by the
served-population README s2 and s3 -- four figures for each of the two arms. This script
reproduces all EIGHT and REFUSES to write its output otherwise, so a disagreement is an
instrument defect caught before any cell is read.

    C:\\unsung-fast\\lbd-venv\\Scripts\\python.exe -u stage1_counts.py --out counts.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb

TABLES = {
    10: (r"C:\unsung-fast\lbd-pairs\A0\A0.parquet",
         "f9bd1f835076f22f1b1da444e1aff92dc2ef8f34667a579c82a0848e7fe4821e"),
    7: (r"C:\unsung-fast\lbd-pairs\T7\T7.parquet", None),   # derived this session
    3: (r"C:\unsung-fast\lbd-pairs\A5\A5.parquet",
        "f34cd88957d3ab42b000fb33d23ae7f9aad1dbdb72d2d0b1cab5d34f024a19ff"),
}

POP_FILES = {
    "V": r"C:\unsung-fast\lbd-archives\population_msw_mbids.txt",
    "P": r"C:\unsung-fast\lbd-archives\population_cxa_mbids.txt",
}

# arm -> (threshold, population rule). s2.1's lattice, in s2.2's order.
ARMS = {
    "LBA-A1": (10, "V"), "LBA-A2": (7, "V"), "LBA-A3": (3, "V"),
    "LBA-A4": (10, "P"), "LBA-A5": (7, "P"), "LBA-A6": (3, "P"),
    "LBA-A7": (10, "U"), "LBA-A8": (7, "U"), "LBA-A9": (3, "U"),
}

# s2.2, quoted verbatim, fixed before any result existed.
SENTENCES = {
    "LBA-A1": "the artists the app serves today, connected by our own recomputation at the same "
              "strength bar ListenBrainz used",
    "LBA-A2": "the same artists, but a connection is kept when three different people's listening "
              "supports it instead of four",
    "LBA-A3": "the same artists, but two people are enough",
    "LBA-A4": "every artist the deeper crawl found, at ListenBrainz's own bar",
    "LBA-A5": "every artist the deeper crawl found, at the three-listener bar",
    "LBA-A6": "every artist the deeper crawl found, at the two-listener bar",
    "LBA-A7": "every artist anywhere in ListenBrainz's listening data who gets a connection at "
              "ListenBrainz's own bar - not just the ones our crawl happened to discover",
    "LBA-A8": "the same, at the three-listener bar",
    "LBA-A9": "the same, at the two-listener bar",
}

# LBA-D7: every arm's row carries this, said rather than inferred from the config.
FILTER_STATE = {"V": "on, inert (20260805)", "P": "on, inert (20260809)", "U": "off, uncensused"}

# s2.1's arithmetic: a pair needs ceil((threshold+1)/contribution) distinct listeners, contribution 3.
LISTENERS = {10: 4, 7: 3, 3: 2}

# Served-population README s2 and s3 -- the green check. (pairs written, payloads, neighbour rows,
# artists of V absent from the table)
GREEN = {
    "LBA-A1": (4_175_136, 57_620, 8_350_272, 1_218),
    "LBA-A3": (4_970_814, 58_197, 9_941_628, 641),
}

COVERAGE = Path(r"C:\dev\music-app\builder\analysis\census-coverage\ulf_coverage.json")

# The two committed offline census passes. `elapsed_seconds` and `coverage.delta_dump_passed_here`
# are each census's own recorded figures (their ulf_census.json); the wall clocks are also in
# `docs/superpowers/2026-08-09-cex-task11-execution-log.md` s6.
CENSUS_POINTS = [
    {"census": "ulc-census-2026-08-05", "elapsed_s": 3638.0, "fresh_artists": 8_137},
    {"census": "cex-recensus-2026-08-09", "elapsed_s": 5819.7, "fresh_artists": 31_450},
]
LBA_G3_BAR_HOURS = 6.0


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--memory-limit-gb", type=int, default=24)
    ap.add_argument("--temp-dir", type=Path, default=Path(r"D:/unsung-large-data/duckdb-temp"))
    args = ap.parse_args(argv)

    # --- inputs, verified before they are read -------------------------------------------
    inputs = {}
    for t, (raw, pinned) in TABLES.items():
        got = sha256_of(Path(raw))
        if pinned and got != pinned:
            raise SystemExit(f"REFUSING: threshold-{t} table is {got}, pinned {pinned}")
        inputs[f"threshold_{t}_table"] = {"path": raw, "sha256": got,
                                          "pinned_on_the_record": bool(pinned)}
        state = "checked against its pin" if pinned else "no pin on the record; recorded"
        print(f"[counts] threshold {t:>2} table  {got[:16]}...  ({state})", flush=True)

    # The coverage store's state BEFORE anything reads it (the handoff: it is active data,
    # the census scripts read AND write it; this session only reads).
    cov_sha_before = sha256_of(COVERAGE)
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov_artists = list(cov["artists"].keys())
    print(f"[counts] coverage store: {len(cov_artists):,} artists, sha {cov_sha_before[:16]}...",
          flush=True)

    args.temp_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{args.memory_limit_gb}GB'")
    con.execute(f"PRAGMA temp_directory='{args.temp_dir.as_posix()}'")
    con.execute("PRAGMA preserve_insertion_order=false")

    pop_sizes = {}
    for name, raw in POP_FILES.items():
        members = [ln.strip() for ln in Path(raw).read_text(encoding="utf-8").splitlines() if ln.strip()]
        con.execute(f"CREATE TEMP TABLE pop_{name} (m VARCHAR)")
        con.executemany(f"INSERT INTO pop_{name} VALUES (?)", [(m,) for m in members])
        pop_sizes[name] = len(members)
        print(f"[counts] population {name}: {len(members):,} artists", flush=True)

    con.execute("CREATE TEMP TABLE cov (m VARCHAR)")
    con.executemany("INSERT INTO cov VALUES (?)", [(m,) for m in cov_artists])

    # --- the nine cells ------------------------------------------------------------------
    rows = []
    for arm, (threshold, rule) in ARMS.items():
        p = Path(TABLES[threshold][0]).as_posix()
        t0 = time.time()
        if rule == "U":
            # Every artist the table names. LBA-X6: this population moves with the threshold.
            pairs, artists = con.execute(f"""
                SELECT (SELECT count(*) FROM read_parquet('{p}')),
                       (SELECT count(*) FROM (SELECT mbid0 AS m FROM read_parquet('{p}')
                                              UNION SELECT mbid1 FROM read_parquet('{p}')))
            """).fetchone()
            absent = None
        else:
            # The emitter writes a pair only when BOTH ends are in the population, and applies
            # the population filter AFTER the threshold and rank cut, never re-ranking inside
            # it (served-population README s2).
            pairs, artists = con.execute(f"""
                WITH kept AS (
                    SELECT t.mbid0, t.mbid1 FROM read_parquet('{p}') t
                     WHERE t.mbid0 IN (SELECT m FROM pop_{rule})
                       AND t.mbid1 IN (SELECT m FROM pop_{rule})
                )
                SELECT (SELECT count(*) FROM kept),
                       (SELECT count(*) FROM (SELECT mbid0 AS m FROM kept
                                              UNION SELECT mbid1 FROM kept))
            """).fetchone()
            absent = pop_sizes[rule] - artists

        # The arm's own population members absent from the census coverage store.
        if rule == "U":
            gap_sql = f"""
                WITH u AS (SELECT mbid0 AS m FROM read_parquet('{p}')
                           UNION SELECT mbid1 FROM read_parquet('{p}'))
                SELECT count(*) FROM (SELECT m FROM u EXCEPT SELECT m FROM cov)
            """
        else:
            gap_sql = f"""
                WITH kept AS (
                    SELECT t.mbid0, t.mbid1 FROM read_parquet('{p}') t
                     WHERE t.mbid0 IN (SELECT m FROM pop_{rule})
                       AND t.mbid1 IN (SELECT m FROM pop_{rule})
                ), a AS (SELECT mbid0 AS m FROM kept UNION SELECT mbid1 FROM kept)
                SELECT count(*) FROM (SELECT m FROM a EXCEPT SELECT m FROM cov)
            """
        (uncovered,) = con.execute(gap_sql).fetchone()

        row = {
            "arm": arm,
            "plain_sentence": SENTENCES[arm],
            "threshold": threshold,
            "distinct_listeners_required": LISTENERS[threshold],
            "population_rule": rule,
            "filter": FILTER_STATE[rule],
            "population_source_size": pop_sizes.get(rule),
            "artists": artists,
            "pairs": pairs,
            "archive_neighbour_rows": 2 * pairs,
            "population_members_absent_from_table": absent,
            "population_absent_from_coverage_store": uncovered,
            "wall_clock_s": round(time.time() - t0, 1),
        }
        if rule == "U":
            row["LBA-X6"] = ("U's membership moves with the threshold; a U-row threshold "
                             "comparison has the population as a dependent variable")
            row["caveat"] = ("TABLE-LEVEL. U's definition applies the drop lists and the "
                             "largest-component prune, both of which need a build. This count "
                             "is an upper bound on the built node count.")
        rows.append(row)
        print(f"[counts] {arm} t{threshold:<2} {rule}  artists {artists:>9,}  pairs {pairs:>12,}"
              f"  rows {2 * pairs:>12,}  uncovered {uncovered:>9,}  ({row['wall_clock_s']} s)",
              flush=True)

    # --- green check, before anything is written -----------------------------------------
    by_arm = {r["arm"]: r for r in rows}
    green = {}
    for arm, (w_pairs, w_payloads, w_rows, w_absent) in GREEN.items():
        r = by_arm[arm]
        got = (r["pairs"], r["artists"], r["archive_neighbour_rows"],
               r["population_members_absent_from_table"])
        green[arm] = {"expected": [w_pairs, w_payloads, w_rows, w_absent], "got": list(got),
                      "match": got == (w_pairs, w_payloads, w_rows, w_absent),
                      "source": "served-population README s2 and s3"}
        print(f"[counts] green check {arm}: {'MATCH' if green[arm]['match'] else 'MISMATCH'}",
              flush=True)
    if not all(g["match"] for g in green.values()):
        raise SystemExit("REFUSING: the reused cells do not reproduce their committed figures; "
                         "this is an instrument defect, not a result.")

    # --- the union of all nine populations, and LBA-G3 ------------------------------------
    a5 = Path(TABLES[3][0]).as_posix()
    a0 = Path(TABLES[10][0]).as_posix()
    t7 = Path(TABLES[7][0]).as_posix()
    # Re-check the nesting the union collapse rests on, for all three pairs.
    nest = {}
    for hi, lo, hp, lp in (("U10", "U7", a0, t7), ("U7", "U3", t7, a5), ("U10", "U3", a0, a5)):
        (leak,) = con.execute(f"""
            WITH h AS (SELECT mbid0 AS m FROM read_parquet('{hp}') UNION SELECT mbid1 FROM read_parquet('{hp}')),
                 l AS (SELECT mbid0 AS m FROM read_parquet('{lp}') UNION SELECT mbid1 FROM read_parquet('{lp}'))
            SELECT count(*) FROM (SELECT m FROM h EXCEPT SELECT m FROM l)
        """).fetchone()
        nest[f"{hi}_subset_of_{lo}"] = {"members_outside": leak, "holds": leak == 0}
    if not all(v["holds"] for v in nest.values()):
        raise SystemExit("REFUSING: the threshold nesting does not hold; the union collapse "
                         "U(3) u V u P is then invalid.")

    t0 = time.time()
    union_total, union_uncovered = con.execute(f"""
        WITH u3 AS (SELECT mbid0 AS m FROM read_parquet('{a5}')
                    UNION SELECT mbid1 FROM read_parquet('{a5}')),
             un AS (SELECT m FROM u3 UNION SELECT m FROM pop_V UNION SELECT m FROM pop_P)
        SELECT (SELECT count(*) FROM un),
               (SELECT count(*) FROM (SELECT m FROM un EXCEPT SELECT m FROM cov))
    """).fetchone()

    # Two-point fit over the two committed offline censuses: elapsed = floor + fresh * rate.
    (c1, c2) = CENSUS_POINTS
    rate = (c2["elapsed_s"] - c1["elapsed_s"]) / (c2["fresh_artists"] - c1["fresh_artists"])
    floor = c1["elapsed_s"] - c1["fresh_artists"] * rate
    projected_s = floor + union_uncovered * rate
    # Sensitivity: the 2026-08-09 pass alone, whole elapsed over its fresh artists, no floor.
    single_rate = c2["elapsed_s"] / c2["fresh_artists"]
    projected_single_s = union_uncovered * single_rate

    g3 = {
        "gate": "LBA-G3",
        "plain_sentence": "working out which artists are unplayable would take too long",
        "bar_hours": LBA_G3_BAR_HOURS,
        "union_members": union_total,
        "union_members_absent_from_coverage_store": union_uncovered,
        "coverage_store_artists": len(cov_artists),
        "two_point_fit": {
            "points": CENSUS_POINTS,
            "scan_floor_s": round(floor, 1),
            "marginal_s_per_artist": round(rate, 6),
            "projected_s": round(projected_s, 1),
            "projected_hours": round(projected_s / 3600, 2),
        },
        "single_point_sensitivity": {
            "basis": "the 2026-08-09 pass alone: whole elapsed over its fresh artists, no floor",
            "s_per_artist": round(single_rate, 6),
            "projected_s": round(projected_single_s, 1),
            "projected_hours": round(projected_single_s / 3600, 2),
        },
        "fires": (projected_s / 3600) > LBA_G3_BAR_HOURS,
        "fires_on_sensitivity": (projected_single_s / 3600) > LBA_G3_BAR_HOURS,
        "wall_clock_s": round(time.time() - t0, 1),
    }
    print(f"\n[counts] union {union_total:,}; absent from coverage store {union_uncovered:,}",
          flush=True)
    print(f"[counts] LBA-G3 projection: {g3['two_point_fit']['projected_hours']} h "
          f"(sensitivity {g3['single_point_sensitivity']['projected_hours']} h), bar "
          f"{LBA_G3_BAR_HOURS} h -- {'FIRES' if g3['fires'] else 'does not fire'}", flush=True)

    cov_sha_after = sha256_of(COVERAGE)
    out = {
        "task": "LBA- stage 1 -- derive and count all nine cells; read LBA-G3",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "duckdb_version": duckdb.__version__,
        "inputs": inputs,
        "coverage_store": {
            "path": str(COVERAGE),
            "artists_before": len(cov_artists),
            "sha256_before": cov_sha_before,
            "sha256_after": cov_sha_after,
            "unchanged": cov_sha_before == cov_sha_after,
            "note": "this session READS the store and never writes it; the census pass is not run",
        },
        "population_sizes": pop_sizes,
        "cells": rows,
        "green_check": green,
        "nesting_check": nest,
        "LBA-G3": g3,
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n[counts] written to {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
