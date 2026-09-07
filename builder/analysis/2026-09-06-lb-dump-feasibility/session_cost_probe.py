"""`LBD-P2` — what ListenBrainz's session-based similarity job costs per day of listens.

Read-only. Offline. No project imports — a frozen probe.

This is the session and pairing half of
`listenbrainz_spark/similarity/artist.py` (metabrainz/listenbrainz-server,
master, fetched 2026-09-06) transcribed from Spark SQL to DuckDB, with two
deliberate simplifications that make it a COST probe and not a reimplementation:

  * every track is assumed to be `DEFAULT_TRACK_LENGTH` = 180 s, because the
    MusicBrainz recording-length table is not an input here;
  * featured-artist weighting (0.25) and the artist-credit inequality are
    omitted, so a pair is counted 1 per co-occurrence.

Both are restored by the faithful reimplementation the plan schedules
(`LBD-` plan, stage 2). What this measures is the SHAPE of the work —
sessions, pair rows, grouped rows — and how long one day takes on this
machine. Session gap (300 s) and skip (30 s) are production's values.

Two figures are printed for the pair stage because LB's SQL self-joins
LISTENS within a session (`listen_pair_rows_lb_style`) whereas the obvious
optimisation self-joins DISTINCT ARTISTS within a session
(`distinct_artist_pairs`, and everything under "grouped"). The two differ in
how repeat plays inside one session count toward the per-user cap, and stage 2
must decide which semantics it keeps — explicitly, once.

Run (from anywhere; no .venv needed):

    UV_LINK_MODE=copy uv run --with duckdb python -u session_cost_probe.py \
        --dump-dir D:/unsung-large-data/incremental-2653/listenbrainz-spark-dump-2653-20260906-000002-incremental

Figures are owned by README.md beside this file; nothing else restates them.
"""

from __future__ import annotations

import argparse
import os
import time

import duckdb

SESSION_GAP_S = 300
SKIP_S = 30
DEFAULT_TRACK_LENGTH_S = 180
CONTRIBUTION_CAP = 3  # ALG-B's value; only used to count how many user-pairs saturate

# ORDER BY (ts, recording_msid), not ts alone. LB's SQL orders by listened_at
# only, which is not a total order: one user can log several listens in the
# same second (the day's top user logs seventeen a second), and DuckDB then
# assigns LAG/LEAD in whatever order the scan produced. Two runs of this probe
# with ORDER BY ts alone differed in the fourth significant figure. The
# reimplementation (LBD- plan, stage 2) inherits this rule: byte-identical
# output for identical input is a project requirement (spec §9).
SESSIONS_CTE = f"""
WITH l AS (
  SELECT user_id, epoch(listened_at)::BIGINT AS ts, recording_msid, artist_credit_mbids
  FROM read_parquet($glob)
  WHERE recording_mbid IS NOT NULL AND recording_mbid <> ''
), ordered AS (
  SELECT user_id, ts, recording_msid, artist_credit_mbids,
         ts - LAG(ts) OVER w - {DEFAULT_TRACK_LENGTH_S} AS difference
  FROM l WINDOW w AS (PARTITION BY user_id ORDER BY ts, recording_msid)
), sess AS (
  SELECT user_id, artist_credit_mbids,
         COUNT_IF(difference > {SESSION_GAP_S}) OVER w AS session_id,
         LEAD(difference) OVER w < -{SKIP_S} AS skipped
  FROM ordered WINDOW w AS (PARTITION BY user_id ORDER BY ts, recording_msid)
)
"""

SHAPE_QUERY = SESSIONS_CTE + """
, f AS (
  SELECT user_id, session_id, unnest(artist_credit_mbids) AS artist_mbid
  FROM sess WHERE NOT coalesce(skipped, false)
), per_session AS (
  SELECT user_id, session_id, COUNT(*) AS n, COUNT(DISTINCT artist_mbid) AS a
  FROM f GROUP BY 1, 2
)
SELECT COUNT(*)                          AS sessions,
       SUM(n)                            AS listen_rows,
       SUM(n * (n - 1))                  AS listen_pair_rows_lb_style,
       SUM(a * (a - 1) / 2)              AS distinct_artist_pairs,
       quantile_cont(n, 0.5)             AS median_session_len,
       quantile_cont(n, 0.99)            AS p99_session_len,
       MAX(n)                            AS max_session_len,
       quantile_cont(a, 0.5)             AS median_artists_per_session
FROM per_session
"""

GROUPED_QUERY = SESSIONS_CTE + f"""
, f AS (
  SELECT DISTINCT user_id, session_id, unnest(artist_credit_mbids) AS artist_mbid
  FROM sess WHERE NOT coalesce(skipped, false)
), pairs AS (
  SELECT a.user_id, a.artist_mbid AS m0, b.artist_mbid AS m1
  FROM f a JOIN f b USING (user_id, session_id)
  WHERE a.artist_mbid < b.artist_mbid
), up AS (
  SELECT user_id, m0, m1, COUNT(*) AS c FROM pairs GROUP BY 1, 2, 3
)
SELECT COUNT(*)                                   AS user_pair_rows,
       COUNT(DISTINCT (m0, m1))                   AS distinct_pairs,
       COUNT_IF(c >= {CONTRIBUTION_CAP})          AS user_pairs_at_cap
FROM up
"""


def run(con: duckdb.DuckDBPyConnection, query: str, glob: str) -> dict[str, object]:
    cur = con.execute(query, {"glob": glob})
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, cur.fetchone()))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-dir", required=True)
    ap.add_argument("--threads", type=int, default=16)
    args = ap.parse_args()
    glob = os.path.join(args.dump_dir, "*.parquet").replace("\\", "/")

    con = duckdb.connect()
    con.execute(f"PRAGMA threads={args.threads}")

    t0 = time.time()
    for label, query in (("shape", SHAPE_QUERY), ("grouped", GROUPED_QUERY)):
        t1 = time.time()
        for key, value in run(con, query, glob).items():
            shown = f"{value:,.0f}" if isinstance(value, (int, float)) else str(value)
            print(f"{label:8s} {key:28s} {shown}")
        print(f"{label:8s} {'elapsed_s':28s} {time.time() - t1:.1f}")
    print(f"total elapsed_s {time.time() - t0:.1f}")


if __name__ == "__main__":
    main()
