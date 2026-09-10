"""`LBD-` Task 4 — derive `LBD-A0`..`LBD-A3` from the one materialised table `T`.

The pre-registration's section 1 establishes, from ListenBrainz's own source, that
`threshold` and `limit` are the ONLY two tokens applied strictly after the cross-user
aggregation, and that neither enters the `score` expression. So the four arms are not four
full-history runs -- they are pure filters and window functions over one table:

    T            = thresholded_mbids at the LOWEST threshold any arm uses (0), no rank cut
    LBD-A0       = T filtered score > 10, ranked per mbid0, rank <= 100
    LBD-A1       = T filtered score > 10, NO rank cut
    LBD-A2       = T unfiltered,          ranked per mbid0, rank <= 100
    LBD-A3       = T unfiltered,          NO rank cut  -- i.e. T itself

These are EXACTLY what the SQL would have produced at those parameters, not an
approximation. `LBD-A4` varies pairing, enters the `score` expression, and therefore needs
its own full pass; it is not derived here.

TWO PROPERTIES OF rank() A DERIVATION MUST PRESERVE, or the arms are not what they claim
(pre-registration section 1):

  1. It is `rank()`, NOT `row_number()` (`artist.py:95`). Ties at the cut ALL survive, so an
     arm may return MORE than `limit` rows for one `mbid0`.
  2. The cut partitions on `mbid0` ONLY. An artist therefore also collects the pairs where
     it sorts second and the OTHER artist's cut kept them -- the "up to 2x" the endpoint's
     own docstring describes and `LBS-3` measured. Nothing here re-partitions to "fix" that.

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-08-lbd-similarity/lbd_derive.py \\
        --table D:/unsung-large-data/lbd-pairs/aggregate/T.parquet --arm A0 \\
        --out D:/unsung-large-data/lbd-pairs/A0/A0.parquet
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import duckdb

# (threshold, limit) per arm, from the pre-registration's section 0 factor table.
# LBD-A0 is ALG-B's parameters; the other three vary exactly one or both of these two.
ARMS = {
    "A0": (10, 100),    # control: LB's own settings
    "A1": (10, None),   # cap removed
    "A2": (0, 100),     # threshold floored
    "A3": (0, None),    # the corner -- both relaxed. T itself.
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def derive_sql(table: str, threshold: int, limit: int | None) -> str:
    """`thresholded_mbids` -> `ranked_mbids` (`artist.py:83-102`), over an existing T.

    `T` was materialised with `HAVING score > 0`, so re-applying `score > threshold` here is
    the same predicate on the same integer column -- the strict `>` and the already-truncated
    BIGINT both carry over from the pass that wrote it.
    """
    filtered = f"SELECT mbid0, mbid1, score FROM read_parquet('{table}') WHERE score > {threshold}"
    if limit is None:
        return filtered
    return f"""
        WITH thresholded_mbids AS ({filtered}),
        ranked_mbids AS (
            SELECT mbid0, mbid1, score, rank() OVER w AS rank
              FROM thresholded_mbids
            WINDOW w AS (PARTITION BY mbid0 ORDER BY score DESC)
        )
        SELECT mbid0, mbid1, score FROM ranked_mbids WHERE rank <= {limit}
    """


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True, help="the materialised T parquet")
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--memory-limit-gb", type=int, default=24)
    ap.add_argument("--temp-dir", type=Path, default=Path(r"D:/unsung-large-data/duckdb-temp"))
    args = ap.parse_args(argv)

    threshold, limit = ARMS[args.arm]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.temp_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{args.memory_limit_gb}GB'")
    con.execute(f"PRAGMA temp_directory='{args.temp_dir.as_posix()}'")
    con.execute("PRAGMA preserve_insertion_order=false")

    sql = derive_sql(Path(args.table).as_posix(), threshold, limit)
    print(f"[derive] arm {args.arm}  threshold {threshold}  limit {limit}", flush=True)

    t0 = time.time()
    con.execute(
        f"COPY ({sql}) TO '{args.out.as_posix()}' "
        f"(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 1000000)"
    )
    wall = time.time() - t0

    rows = con.execute(f"SELECT count(*) FROM read_parquet('{args.out.as_posix()}')").fetchone()[0]
    args.out.with_suffix(".manifest.json").write_text(
        json.dumps(
            {
                "arm": args.arm,
                "threshold": threshold,
                "limit": limit,
                "derived_from": str(args.table),
                "derived_from_sha256": sha256_of(Path(args.table)),
                "script_sha256": sha256_of(Path(__file__)),
                "out": str(args.out),
                "out_sha256": sha256_of(args.out),
                "rows": rows,
                "wall_clock_s": round(wall, 1),
                "finished_utc": datetime.utcnow().isoformat() + "Z",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[derive] {args.arm}: {rows:,} rows in {wall/60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
