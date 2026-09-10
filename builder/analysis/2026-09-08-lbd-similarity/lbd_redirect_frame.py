"""`LBD-` Task 3 (`T3-D6`) — the redirect half of ListenBrainz's `recording_length` frame.

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-08-lbd-similarity/lbd_redirect_frame.py

WHY THIS EXISTS. `LBDR-F4` found that Task 1's extraction omits `recording_gid_redirect`,
and that the omission is not neutral. LB's `RECORDING_LENGTH_DATAFRAME` is built by
`data/postgres/recording.py:16-33` as a UNION of two arms:

    SELECT r.gid::text, r.length, r.id, false AS is_redirect          FROM recording r
     UNION ALL
    SELECT rgr.gid::text, r.length, rgr.new_id, true AS is_redirect   FROM recording_gid_redirect rgr
      JOIN recording r ON rgr.new_id = r.id

so a REDIRECTED gid carries its TARGET recording's length. Without the second arm every
listen on a redirected MBID falls to `DEFAULT_TRACK_LENGTH` = 180 s, which shifts
`difference`, which shifts session boundaries AND the skip test -- a systematic,
one-directional divergence in exactly the stage `LBDR-F3` shows is already fragile.

Task 1's README section 5 deferred this to `LBD-S2` on the ground that the unmatched share is
only measurable against the frame that consumes it. This is `LBD-S2`, so it is taken here
rather than deferred again, and `lbd_similarity.py --no-redirects` reproduces the
un-redirected frame so the size of the difference is MEASURED rather than argued.

COLUMN ORDER IS NOT GUESSED. Read from `admin/sql/CreateTables.sql` at
metabrainz/musicbrainz-server master, fetched by URL 2026-09-08 and checked against the
dump's own SCHEMA_SEQUENCE (both 31, as Task 1 established):

    recording_gid_redirect   gid, new_id, created                       -- THREE columns
    recording                id, gid, name, artist_credit, length,
                             comment, edits_pending, last_updated, video -- NINE columns

Neither column this frame keeps is a string, so unlike Task 1's `join_phrase` there is no
PostgreSQL escape to undo -- `gid` is a UUID and `new_id`/`length` are integers.

Writes `D:\\unsung-large-data\\lbd-inputs\\recording_gid_redirect_length.parquet`. Nothing is
written into `builder/scratch/` (`LBD-D8`).
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import duckdb

MBDUMP = Path(r"D:\unsung-large-data\mb-20260905\mbdump")
INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
OUT = INPUTS / "recording_gid_redirect_length.parquet"

RGR_COLS = [("gid", "VARCHAR"), ("new_id", "BIGINT"), ("created", "VARCHAR")]
REC_COLS = [
    ("id", "BIGINT"), ("gid", "VARCHAR"), ("name", "VARCHAR"),
    ("artist_credit", "BIGINT"), ("length", "BIGINT"), ("comment", "VARCHAR"),
    ("edits_pending", "BIGINT"), ("last_updated", "VARCHAR"), ("video", "VARCHAR"),
]


def tsv(path: Path, cols: list[tuple[str, str]]) -> str:
    """A read_csv for one mbdump TSV, column order fixed by schema.

    quote='' and escape='' are deliberate: these are `COPY ... TO` TEXT dumps, real newlines
    never appear inside a field, and letting DuckDB consume the backslashes at parse time
    would alter string columns. Task 1 established this and the reasoning carries over.
    """
    spec = ", ".join(f"'{n}': '{t}'" for n, t in cols)
    return (
        f"read_csv('{path.as_posix()}', delim='\\t', header=false, quote='', escape='', "
        f"nullstr='\\N', columns={{{spec}}})"
    )


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    rgr = MBDUMP / "recording_gid_redirect"
    rec = MBDUMP / "recording"
    for p in (rgr, rec):
        if not p.is_file():
            raise SystemExit(f"missing mbdump table: {p}")

    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='12GB'")
    con.execute("PRAGMA temp_directory='D:/unsung-large-data/duckdb-temp'")

    t0 = time.time()
    con.execute(
        f"""COPY (
                SELECT rgr.gid AS recording_mbid, r.length AS length
                  FROM {tsv(rgr, RGR_COLS)} rgr
                  JOIN {tsv(rec, REC_COLS)} r ON rgr.new_id = r.id
                 ORDER BY recording_mbid
            ) TO '{OUT.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"""
    )
    wall = time.time() - t0

    rows, nonnull = con.execute(
        f"SELECT count(*), count(length) FROM read_parquet('{OUT.as_posix()}')"
    ).fetchone()

    # The two arms must not collide: LB uses UNION ALL, so a gid appearing in both would
    # fan out every listen on it. Checked rather than assumed.
    rl = INPUTS / "recording_length.parquet"
    overlap = con.execute(
        f"""SELECT count(*) FROM read_parquet('{OUT.as_posix()}') a
             JOIN read_parquet('{rl.as_posix()}') b USING (recording_mbid)"""
    ).fetchone()[0]

    identity = {
        "out": str(OUT),
        "out_sha256": sha256_of(OUT),
        "rows": rows,
        "rows_with_length": nonnull,
        "overlap_with_recording_length": overlap,
        "source_mbdump": str(MBDUMP),
        "schema_sequence": 31,
        "script_sha256": sha256_of(Path(__file__)),
        "wall_clock_s": round(wall, 1),
    }
    (INPUTS / "recording_gid_redirect_length.identity.json").write_text(
        json.dumps(identity, indent=2), encoding="utf-8"
    )
    print(json.dumps(identity, indent=2))
    if overlap:
        print(
            f"\n[WARN] {overlap:,} gids appear in BOTH arms. LB uses UNION ALL, so those "
            "listens fan out. This reproduces LB, but record it."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
