"""`LBD-` Task 4 — the diagnosis result `R1` demands when `LBD-G1` fires.

`LBD-G1` fired on 2026-09-09 (top-band pooled rate below 0.60; figure owned by README §5).
Result `R1` in the pre-registration says: the reimplementation is presumed wrong, stop and
diagnose, and the arms are NOT read. This script is the diagnosis. It reads nothing that is
not already on disk, and it reads NO supply criterion -- `LBD-C2a` stays untaken.

It decomposes every pair ListenBrainz's archive list holds for a sampled artist into where
our pipeline lost it, using the fact that `T` (score >= 1, no cap) is a superset of every arm:

    matched            in our top-N for the artist (the LBD-C1 definition)
    below_cut          in our A0 union list, but ranked past N
    rank_cut           score > 10 in T, but neither partition's rank <= 100 kept it
    below_threshold    1 <= score <= 10 in T
    absent             not in T at all -- the pair never co-occurred in our corpus in a form
                       that survives sessioning

and, for every truth pair present in T, compares OUR score with LB's own `score` field. A
systematic ratio is a different finding from a reshuffle: the first says the corpus or the
job differs in what it counts, the second says the lists are near-ties at the cut.

It also reports overlap at ranks 10 / 25 / 50, which the C1 definition (cut at N) cannot see,
and fixes a reporting defect in `lbd_reads.py`: artists whose archive list is EMPTY yield a
NaN share, and a NaN inside `sorted()` scrambles the order, so the per-artist quantiles that
read printed on 2026-09-09 are wrong (p75 below the median in three bands). The pooled rate,
which `LBD-G1` reads, does not touch those values and is unaffected.

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-08-lbd-similarity/lbd_c1_diagnose.py \\
        --a0 C:/unsung-fast/lbd-pairs/A0/A0.parquet --t C:/unsung-fast/lbd-pairs/aggregate/T.parquet
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
SAMPLE = Path(__file__).resolve().parent / "lbd_c1_sample.tsv"
THRESHOLD = 10  # LBD-A0's, and LB's deployed


def q(vals: list[float], p: float) -> float:
    if not vals:
        return float("nan")
    v = sorted(vals)
    i = p * (len(v) - 1)
    lo, hi = int(i), min(int(i) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a0", type=Path, required=True)
    ap.add_argument("--t", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--memory-limit-gb", type=int, default=12)
    ap.add_argument("--temp-dir", type=Path, default=Path(r"C:/unsung-fast/duckdb-temp"))
    args = ap.parse_args(argv)
    out = args.out or args.a0.with_name("c1_diagnosis.json")

    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{args.memory_limit_gb}GB'")
    con.execute(f"PRAGMA temp_directory='{args.temp_dir.as_posix()}'")
    con.execute("PRAGMA preserve_insertion_order=false")

    rows = SAMPLE.read_text(encoding="utf-8").splitlines()[1:]
    sample = [(r.split("\t")[0], int(r.split("\t")[1])) for r in rows]
    con.execute("CREATE TABLE sample(mbid VARCHAR, band INTEGER)")
    con.executemany("INSERT INTO sample VALUES (?,?)", sample)

    algo_dir = sorted(p for p in (SNAPSHOT / "similar").glob("*/*") if p.is_dir())[0]
    truth = []
    empty = {b: 0 for b in range(5)}
    for mbid, band in sample:
        entries = json.loads((algo_dir / f"{mbid}.json").read_text(encoding="utf-8"))
        if not entries:
            empty[band] += 1
        for rank, e in enumerate(entries, start=1):
            truth.append((mbid, band, e["artist_mbid"], rank, int(e["score"]), len(entries)))
    con.execute("CREATE TABLE truth(artist VARCHAR, band INTEGER, partner VARCHAR, lb_rank INTEGER, lb_score INTEGER, n INTEGER)")
    con.executemany("INSERT INTO truth VALUES (?,?,?,?,?,?)", truth)
    print(f"[diag] truth {len(truth):,} pairs over {len(sample):,} artists; empty archive lists by band {empty}", flush=True)

    def union_sql(table: Path) -> str:
        t = table.as_posix()
        return f"""
            SELECT s.mbid AS artist, s.band, p.mbid1 AS partner, p.score
              FROM sample s JOIN read_parquet('{t}') p ON p.mbid0 = s.mbid
            UNION ALL
            SELECT s.mbid AS artist, s.band, p.mbid0 AS partner, p.score
              FROM sample s JOIN read_parquet('{t}') p ON p.mbid1 = s.mbid
        """

    # Our A0 union list, ranked exactly as the C1 read ranks it.
    con.execute(f"""CREATE TABLE ours AS
        SELECT artist, band, partner, score,
               row_number() OVER (PARTITION BY artist ORDER BY score DESC, partner) AS rn
          FROM ({union_sql(args.a0)})""")
    # Every pair in T touching a sampled artist, at any score >= 1.
    con.execute(f"CREATE TABLE tt AS SELECT artist, band, partner, score FROM ({union_sql(args.t)})")
    print(f"[diag] ours(A0) {con.execute('SELECT count(*) FROM ours').fetchone()[0]:,} rows; "
          f"T rows touching sample {con.execute('SELECT count(*) FROM tt').fetchone()[0]:,}", flush=True)

    # ---- the decomposition of every truth pair
    con.execute(f"""CREATE TABLE decomp AS
        SELECT tr.artist, tr.band, tr.partner, tr.lb_rank, tr.lb_score, tr.n,
               o.rn AS our_rn, o.score AS our_a0_score, t.score AS our_t_score,
               CASE
                 WHEN o.rn IS NOT NULL AND o.rn <= tr.n THEN 'matched'
                 WHEN o.rn IS NOT NULL                   THEN 'below_cut'
                 WHEN t.score > {THRESHOLD}              THEN 'rank_cut'
                 WHEN t.score IS NOT NULL                THEN 'below_threshold'
                 ELSE 'absent'
               END AS outcome
          FROM truth tr
          LEFT JOIN ours o ON o.artist = tr.artist AND o.partner = tr.partner
          LEFT JOIN tt t ON t.artist = tr.artist AND t.partner = tr.partner""")

    result: dict = {"a0": str(args.a0), "t": str(args.t), "empty_archive_lists_by_band": empty, "bands": {}}
    cats = ["matched", "below_cut", "rank_cut", "below_threshold", "absent"]
    print("\n== where each ListenBrainz list entry ended up in our pipeline (share of the band's truth rows)")
    print("  band   rows   " + "  ".join(f"{c:>15}" for c in cats))
    for band in range(5):
        tot = con.execute("SELECT count(*) FROM decomp WHERE band=?", [band]).fetchone()[0]
        shares = {}
        for c in cats:
            k = con.execute("SELECT count(*) FROM decomp WHERE band=? AND outcome=?", [band, c]).fetchone()[0]
            shares[c] = k / tot if tot else float("nan")
        result["bands"][band] = {"truth_rows": tot, "outcome_share": shares}
        print(f"  {band:>4} {tot:>7,}  " + "  ".join(f"{shares[c]:>15.4f}" for c in cats))

    # ---- score ratio on every truth pair that exists in T
    print("\n== our T score / LB's score, on truth pairs present in T (median, p10, p90), and the share where ours is lower")
    print("  band   pairs   median     p10     p90   ours<LB")
    for band in range(5):
        vals = [r[0] for r in con.execute(
            "SELECT our_t_score::DOUBLE / lb_score FROM decomp WHERE band=? AND our_t_score IS NOT NULL AND lb_score > 0", [band]).fetchall()]
        lower = sum(1 for v in vals if v < 1) / len(vals) if vals else float("nan")
        result["bands"][band]["score_ratio"] = {"pairs": len(vals), "median": q(vals, .5), "p10": q(vals, .1), "p90": q(vals, .9), "share_ours_lower": lower}
        print(f"  {band:>4} {len(vals):>7,}  {q(vals,.5):>7.3f} {q(vals,.1):>7.3f} {q(vals,.9):>7.3f}   {lower:>7.4f}")

    # ---- overlap at fixed ranks, pooled by band, over artists whose LB list has >= k entries
    print("\n== overlap of our top-k with LB's top-k (pooled by band; artists with N >= k)")
    print("  band     k=10     k=25     k=50    k=100")
    for band in range(5):
        row = {}
        for k in (10, 25, 50, 100):
            m, tot = con.execute(f"""
                SELECT coalesce(sum(CASE WHEN o.rn <= {k} THEN 1 ELSE 0 END),0), count(*)
                  FROM truth tr LEFT JOIN ours o ON o.artist=tr.artist AND o.partner=tr.partner
                 WHERE tr.band=? AND tr.n >= {k} AND tr.lb_rank <= {k}""", [band]).fetchone()
            row[k] = m / tot if tot else float("nan")
        result["bands"][band]["overlap_at_k"] = row
        print(f"  {band:>4}  " + "  ".join(f"{row[k]:>7.4f}" for k in (10, 25, 50, 100)))

    # ---- list lengths: LB's N against our A0 union length, and the score at the cut
    print("\n== list length and score at the cut (medians by band): LB's N, our A0 union length, LB's min score, our score at rank N")
    print("  band   LB N   ours   LB min   ours@N")
    for band in range(5):
        r = con.execute("""
            WITH per AS (
              SELECT s.mbid, any_value(tr.n) AS n, min(tr.lb_score) AS lb_min,
                     (SELECT count(*) FROM ours o WHERE o.artist=s.mbid) AS our_len,
                     (SELECT score FROM ours o WHERE o.artist=s.mbid AND o.rn = any_value(tr.n)) AS our_at_n
                FROM sample s JOIN truth tr ON tr.artist=s.mbid WHERE s.band=? GROUP BY s.mbid)
            SELECT median(n), median(our_len), median(lb_min), median(our_at_n) FROM per""", [band]).fetchone()
        result["bands"][band]["lengths"] = {"lb_n_median": r[0], "our_len_median": r[1], "lb_min_score_median": r[2], "our_score_at_n_median": r[3]}
        print(f"  {band:>4}  {r[0]:>5}  {r[1]:>5}  {r[2]:>7}  {r[3]}")

    # ---- the corrected per-artist distribution: empty lists EXCLUDED and counted
    print("\n== per-artist top-N share, empty archive lists excluded (the corrected reporting)")
    print("  band  n_scored  median     p10     p25     p75")
    for band in range(5):
        vals = [r[0] for r in con.execute("""
            SELECT sum(CASE WHEN outcome='matched' THEN 1 ELSE 0 END)::DOUBLE / any_value(n)
              FROM decomp WHERE band=? GROUP BY artist HAVING any_value(n) > 0""", [band]).fetchall()]
        result["bands"][band]["per_artist_share"] = {"n_scored": len(vals), "median": q(vals, .5), "p10": q(vals, .1), "p25": q(vals, .25), "p75": q(vals, .75)}
        print(f"  {band:>4}  {len(vals):>8}  {q(vals,.5):>6.4f}  {q(vals,.1):>6.4f}  {q(vals,.25):>6.4f}  {q(vals,.75):>6.4f}")

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\n[diag] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
