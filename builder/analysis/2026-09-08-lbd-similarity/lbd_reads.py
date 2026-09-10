"""`LBD-` Task 4 — the two reads the pre-registration fixes, taken in its order.

    --mode c1    LBD-C1, fidelity, against the pinned pre-CEX archive snapshot
    --mode c2a   LBD-C2a, pair-table candidate supply for the CXR added set

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-08-lbd-similarity/lbd_reads.py \\
        --mode c1 --pairs D:/unsung-large-data/lbd-pairs/A0/A0.parquet

ORDER MATTERS AND IS NOT A PREFERENCE. Result `R1` in the pre-registration's section 9 says
the fidelity read presupposes only `fidelity-read`, and that `T-materialised is NOT required
and the fidelity run should precede the arm reads for exactly this reason`: if `LBD-G1` fires,
the arms already derived from `T` are NOT read, because they inherit the same defect. So c1
is taken and judged before c2a is taken.

--------------------------------------------------------------------------------------
LBD-C1 -- fidelity
--------------------------------------------------------------------------------------

Plain sentence (pre-registration section 2, fixed before any result existed):

  > when we compute similarity the way ListenBrainz says it does, using their own listens,
  > how much of what they told us about each artist do we get back?

"Our top-N" is defined there, and the definition is worth more than any threshold below it:

  > the UNION of both lexical partitions for that artist -- every pair in which the artist
  > appears as either mbid0 or mbid1 -- ordered by score descending with the MBID as
  > tie-break, cut at N = the length of the archive's own list for that artist.

The alternative reading (the artist's own `mbid0` half, which is what the SQL literally
emits per partition) carries a construction ceiling far below 1.0 that is WORSE for famous
artists, so a perfect reimplementation would fail the criterion. That is the wrong
instrument regardless of where a floor is set.

REPORTED TWO WAYS, BOTH REQUIRED (section 2):
  - a per-artist overlap distribution -- median, p10, p25, p75 BY BAND, never one mean; and
  - a POOLED row-level rate (matched rows / total rows) by band.
The pooled rate exists because served list lengths differ by roughly 5x-7x between the
most- and least-listened bands, so a per-artist share has far coarser resolution at the
obscure end.

`LBD-G1` fires on the POOLED rate in the TOP band below 0.60. Plain: for the best-covered,
most-listened artists, we get back less than three in five of what ListenBrainz told us.

--------------------------------------------------------------------------------------
LBD-C2a -- pair-table candidate supply, the PRIMARY supply statistic
--------------------------------------------------------------------------------------

Plain sentence (section 3):

  > how many other artists does ListenBrainz's listening data offer as a candidate
  > connection for each of these artists, before any of our own rules touch it?

Per added artist, the number of distinct partners in the arm's derived pair table. This is
what `LBD-R1` is read off, because it is upstream of `LBD-X1` (our degree ceiling) entirely.

DENOMINATOR AND ABSENCE (section 3): all 29,892, with an artist absent from the arm's table
counted as degree 0, so the figures are comparable with the `CXR-P2` reference. Share-absent
is reported SEPARATELY, because absent and present-with-degree-1 are different outcomes.

STATISTIC: the share at or below 2 connections -- plain, what fraction are still dead ends.
MEDIAN DEGREE IS REPORTED AND IS NOT GATED ON: it bootstraps to a single value at this
resolution, moves by a whole unit under the population confound alone, and flips between
random halves of the same data.

`LBD-AM1` additionally requires the same figure over two strata -- the RESIDUAL set (added
artists still at <= 2 connections when our own degree ceiling does not bind) and its
complement -- IN ADDITION TO the whole-set figure, which continues to be evaluated over all
29,892 exactly as section 3 states. The amendment adds a reporting requirement, no gate and
no effect size. Its named failure mode is `R12`: if the whole set clears the bar while the
residual set does not move, the report must say so in those words.

The pre-existing set is reported in every arm as the within-arm reference (`LBD-G2`'s second
condition), because a larger population alone moves the supply reading in the direction that
flatters every arm (`LBD-X2`).

THIS SCRIPT COMPUTES AND PRINTS. IT DOES NOT DECIDE. `LBD-G1`'s and `LBD-G2`'s readings are
the README's and the owner's.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import duckdb

MAIN_TREE = Path(r"C:\dev\music-app")
SNAPSHOT = MAIN_TREE / "builder" / "scratch" / "grt-archive-algb.pre-cex-snapshot"
INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
SAMPLE = Path(__file__).resolve().parent / "lbd_c1_sample.tsv"

ADDED = INPUTS / "cxr_added_mbids.txt"
PREEXISTING = INPUTS / "cxr_preexisting_mbids.txt"
RESIDUAL = INPUTS / "cxr_residual_mbids.txt"


def connect(memory_limit_gb: int, temp_dir: Path) -> duckdb.DuckDBPyConnection:
    temp_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{memory_limit_gb}GB'")
    con.execute(f"PRAGMA temp_directory='{temp_dir.as_posix()}'")
    con.execute("PRAGMA preserve_insertion_order=false")
    return con


def quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    i = q * (len(sorted_vals) - 1)
    lo, hi = int(i), min(int(i) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (i - lo)


# ---------------------------------------------------------------------------------------
# LBD-C1
# ---------------------------------------------------------------------------------------

def read_c1(con: duckdb.DuckDBPyConnection, pairs: Path, out: Path) -> dict:
    rows = SAMPLE.read_text(encoding="utf-8").splitlines()[1:]
    sample = [(r.split("\t")[0], int(r.split("\t")[1])) for r in rows]
    print(f"[c1] sample {len(sample):,} artists from {SAMPLE.name}", flush=True)

    algo_dirs = sorted(p for p in (SNAPSHOT / "similar").glob("*/*") if p.is_dir())
    algo_dir = algo_dirs[0]

    # The archive's own list for each sampled artist: the N we cut to, and the truth set.
    truth: dict[str, list[str]] = {}
    for mbid, _ in sample:
        f = algo_dir / f"{mbid}.json"
        entries = json.loads(f.read_text(encoding="utf-8"))
        truth[mbid] = [e["artist_mbid"] for e in entries]
    lens = [len(v) for v in truth.values()]
    print(f"[c1] archive lists: total {sum(lens):,} rows, min {min(lens)}, max {max(lens)}", flush=True)

    con.execute("CREATE TABLE sample(mbid VARCHAR, band INTEGER)")
    con.executemany("INSERT INTO sample VALUES (?,?)", sample)

    # The UNION of both lexical partitions, ranked score DESC with the MBID as tie-break.
    # row_number, not rank: the definition says "cut at N", an exact count.
    q = f"""
        WITH u AS (
            SELECT s.mbid AS artist, p.mbid1 AS partner, p.score
              FROM sample s JOIN read_parquet('{pairs.as_posix()}') p ON p.mbid0 = s.mbid
             UNION ALL
            SELECT s.mbid AS artist, p.mbid0 AS partner, p.score
              FROM sample s JOIN read_parquet('{pairs.as_posix()}') p ON p.mbid1 = s.mbid
        )
        SELECT artist, partner,
               row_number() OVER (PARTITION BY artist ORDER BY score DESC, partner) AS rn
          FROM u
    """
    ours: dict[str, list[str]] = {}
    for artist, partner, rn in con.execute(q).fetchall():
        ours.setdefault(artist, []).append(partner)
    print(f"[c1] our table covers {len(ours):,} of {len(sample):,} sampled artists", flush=True)

    per_band_shares: dict[int, list[float]] = {}
    per_band_pooled: dict[int, list[int]] = {}
    absent = 0
    for mbid, band in sample:
        want = truth[mbid]
        n = len(want)
        got = ours.get(mbid, [])
        if not got:
            absent += 1
        top_n = got[:n]
        matched = len(set(top_n) & set(want))
        per_band_shares.setdefault(band, []).append(matched / n if n else float("nan"))
        p = per_band_pooled.setdefault(band, [0, 0])
        p[0] += matched
        p[1] += n

    result = {"pairs": str(pairs), "sample": str(SAMPLE), "absent_from_our_table": absent, "bands": {}}
    print()
    print("  band   n     pooled     median      p10      p25      p75")
    for band in sorted(per_band_shares):
        vals = sorted(per_band_shares[band])
        m, tot = per_band_pooled[band]
        pooled = m / tot if tot else float("nan")
        row = {
            "n": len(vals),
            "pooled_matched_rows": m,
            "pooled_total_rows": tot,
            "pooled_rate": pooled,
            "median": quantile(vals, 0.5),
            "p10": quantile(vals, 0.10),
            "p25": quantile(vals, 0.25),
            "p75": quantile(vals, 0.75),
        }
        result["bands"][band] = row
        print(f"  {band:>4} {len(vals):>5}   {pooled:>7.4f}   {row['median']:>7.4f}  "
              f"{row['p10']:>7.4f}  {row['p25']:>7.4f}  {row['p75']:>7.4f}")

    top = max(result["bands"])
    result["G1_top_band_pooled"] = result["bands"][top]["pooled_rate"]
    result["G1_floor"] = 0.60
    result["G1_fires"] = result["bands"][top]["pooled_rate"] < 0.60
    print()
    print(f"  LBD-G1: top band (band {top}) pooled rate = "
          f"{result['G1_top_band_pooled']:.4f}, floor 0.60 -> "
          f"{'FIRES -- STOP AND DIAGNOSE' if result['G1_fires'] else 'does not fire'}")
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


# ---------------------------------------------------------------------------------------
# LBD-C2a
# ---------------------------------------------------------------------------------------

def _load_set(path: Path) -> list[str]:
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def degrees(con: duckdb.DuckDBPyConnection, pairs: Path, mbids: list[str], label: str) -> dict[str, int]:
    con.execute(f"CREATE OR REPLACE TABLE q_{label}(mbid VARCHAR)")
    con.executemany(f"INSERT INTO q_{label} VALUES (?)", [(m,) for m in mbids])
    q = f"""
        WITH u AS (
            SELECT s.mbid AS artist, p.mbid1 AS partner
              FROM q_{label} s JOIN read_parquet('{pairs.as_posix()}') p ON p.mbid0 = s.mbid
             UNION ALL
            SELECT s.mbid AS artist, p.mbid0 AS partner
              FROM q_{label} s JOIN read_parquet('{pairs.as_posix()}') p ON p.mbid1 = s.mbid
        )
        SELECT artist, count(DISTINCT partner) FROM u GROUP BY artist
    """
    found = dict(con.execute(q).fetchall())
    return {m: int(found.get(m, 0)) for m in mbids}


def summarise(deg: dict[str, int], name: str) -> dict:
    vals = sorted(deg.values())
    n = len(vals)
    absent = sum(1 for v in vals if v == 0)
    le2 = sum(1 for v in vals if v <= 2)
    row = {
        "set": name,
        "n": n,
        "share_le_2": le2 / n if n else float("nan"),
        "count_le_2": le2,
        "share_absent": absent / n if n else float("nan"),
        "count_absent": absent,
        "median_degree_REPORTED_NOT_GATED": statistics.median(vals) if vals else float("nan"),
        "p25": quantile([float(v) for v in vals], 0.25),
        "p75": quantile([float(v) for v in vals], 0.75),
    }
    print(f"  {name:<28} n={n:>7,}  share<=2 {row['share_le_2']:.4f}  "
          f"absent {row['share_absent']:.4f}  median {row['median_degree_REPORTED_NOT_GATED']}")
    return row


def read_c2a(con: duckdb.DuckDBPyConnection, pairs: Path, out: Path) -> dict:
    added = _load_set(ADDED)
    residual = set(_load_set(RESIDUAL))
    pre = _load_set(PREEXISTING)
    print(f"[c2a] added {len(added):,}  residual {len(residual):,}  pre-existing {len(pre):,}", flush=True)

    deg_added = degrees(con, pairs, added, "added")
    deg_pre = degrees(con, pairs, pre, "pre")

    res = {m: d for m, d in deg_added.items() if m in residual}
    comp = {m: d for m, d in deg_added.items() if m not in residual}

    print()
    result = {
        "pairs": str(pairs),
        "whole_set": summarise(deg_added, "added (whole set)"),
        "residual": summarise(res, "  LBD-AM1 residual"),
        "complement": summarise(comp, "  LBD-AM1 complement"),
        "preexisting_reference": summarise(deg_pre, "pre-existing (reference)"),
    }
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    # Per-artist degrees, so the paired comparison LBD-G2 names ("paired sign test over the
    # fixed 29,892") can be computed between arms without re-reading the pair tables.
    out.with_suffix(".degrees.json").write_text(
        json.dumps({"added": deg_added, "preexisting": deg_pre}), encoding="utf-8"
    )
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=("c1", "c2a"))
    ap.add_argument("--pairs", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--memory-limit-gb", type=int, default=24)
    ap.add_argument("--temp-dir", type=Path, default=Path(r"D:/unsung-large-data/duckdb-temp"))
    args = ap.parse_args(argv)

    out = args.out or args.pairs.with_name(f"{args.pairs.stem}.{args.mode}.json")
    con = connect(args.memory_limit_gb, args.temp_dir)
    if args.mode == "c1":
        read_c1(con, args.pairs, out)
    else:
        read_c2a(con, args.pairs, out)
    print(f"\n[{args.mode}] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
