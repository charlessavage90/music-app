"""`LBD-` Task 1 — the MusicBrainz side-tables, extracted and converted to parquet.

Frozen: stdlib + DuckDB only, no project imports. Writes only under
`D:\\unsung-large-data\\` (`LBD-D8`).

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-07-lbd-inputs/inputs_extract.py

ListenBrainz's similarity job joins two frames its own dump builds from MusicBrainz:

  recording_length   recording_mbid -> length, for the session-gap duration
                     (`COALESCE(r.length / 1000, 180)`)
  artist_credit      artist_credit_id -> (artist_mbid, position, join_phrase),
                     the credit fan-out and the featured-artist weight

We rebuild both from `mbdump.tar.bz2` so that every MusicBrainz-derived input carries
ONE snapshot date, and a third frame -- `artist_identity` (gid, name, comment) -- which
the archive emitter needs later to write endpoint-shaped payloads.

COLUMN ORDER IS NOT GUESSED. The TSVs have no header; the order is read from
`admin/sql/CreateTables.sql` in metabrainz/musicbrainz-server, fetched by URL and
checked against the dump's own SCHEMA_SEQUENCE. Verified 2026-09-07:

  artist             id, gid, name, sort_name, begin_date_{y,m,d}, end_date_{y,m,d},
                     type, area, gender, comment (14th), edits_pending, last_updated, ended
  artist_credit      id, name, artist_count, ref_count, created, edits_pending, gid
  artist_credit_name artist_credit, position, artist, name, join_phrase
  recording          id, gid, name, artist_credit, length, comment, edits_pending,
                     last_updated, video

ENCODING. MusicBrainz dumps are PostgreSQL `COPY ... TO` TEXT format: tab-delimited,
`\\N` for NULL, and backslash escapes for tab, newline and backslash. Real newlines are
therefore never present inside a field, so row splitting is safe with no quoting; the
escapes are undone afterwards on the string columns we keep. Reading with DuckDB's own
`escape` would consume the backslashes at parse time and silently change `join_phrase`,
which is the one column whose exact bytes decide the featured-artist weight.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import duckdb

MB_DIR = Path(r"D:\unsung-large-data\mb-20260905")
TARBALL = MB_DIR / "mbdump.tar.bz2"
EXPECTED_SHA = "5cd98ffa443e2fde3517d36417d6c1d67960025058ba1411291bb7e1adcd3292"
OUT_DIR = Path(r"D:\unsung-large-data\lbd-inputs")

WANTED = [
    "mbdump/artist",
    "mbdump/artist_credit",
    "mbdump/artist_credit_name",
    "mbdump/recording",
]

# PostgreSQL COPY TEXT unescaping, applied to kept string columns only.
def unescape(col: str) -> str:
    return (
        f"replace(replace(replace({col}, '\\t', chr(9)), '\\n', chr(10)), '\\\\', '\\')"
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_tarball() -> None:
    print(f"verifying {TARBALL.name} ({TARBALL.stat().st_size:,} bytes)")
    actual = sha256_file(TARBALL)
    if actual != EXPECTED_SHA:
        raise SystemExit(
            f"REFUSING TO EXTRACT: sha256 {actual}\n"
            f"           published SHA256SUMS {EXPECTED_SHA}"
        )
    print(f"  sha256 {actual}  MATCHES published SHA256SUMS")


def extract() -> None:
    if all((MB_DIR / w).exists() for w in WANTED):
        print("all four tables already extracted, skipping")
        return
    print(f"extracting {len(WANTED)} tables from the tarball (bzip2, single-threaded)")
    t = time.time()
    subprocess.run(
        ["tar", "-xjf", str(TARBALL), "-C", str(MB_DIR), "mbdump/SCHEMA_SEQUENCE",
         "mbdump/TIMESTAMP", *WANTED],
        check=True,
    )
    print(f"  extracted in {(time.time()-t)/60:.1f} min")


def tsv(name: str, cols: list[tuple[str, str]]) -> str:
    """A read_csv call for one mbdump TSV, with the column order fixed by schema."""
    spec = ", ".join(f"'{c}': '{t}'" for c, t in cols)
    path = (MB_DIR / "mbdump" / name).as_posix()
    return (
        f"read_csv('{path}', delim='\\t', header=false, quote='', escape='',"
        f" nullstr='\\N', columns={{{spec}}})"
    )


def build_frames(con: duckdb.DuckDBPyConnection) -> dict:
    out = {}

    # --- recording_length: recording_mbid -> length (ms) ---
    print("\nbuilding recording_length")
    t = time.time()
    dst = (OUT_DIR / "recording_length.parquet").as_posix()
    con.execute(
        f"""
        COPY (
            SELECT gid AS recording_mbid, length
              FROM {tsv('recording', [('id','BIGINT'),('gid','VARCHAR'),('name','VARCHAR'),
                                      ('artist_credit','BIGINT'),('length','BIGINT'),
                                      ('comment','VARCHAR'),('edits_pending','BIGINT'),
                                      ('last_updated','VARCHAR'),('video','VARCHAR')])}
             ORDER BY recording_mbid
        ) TO '{dst}' (FORMAT PARQUET)
        """
    )
    out["recording_length"] = frame_stats(con, dst, time.time() - t)

    # --- artist_credit: the credit fan-out LB's job joins on ---
    # Shape fixed by LB's own data/postgres/artist_credit.py:
    #   artist_credit_id, artist_mbid, position, join_phrase
    # join_phrase is kept VERBATIM apart from COPY unescaping -- LB compares it
    # untrimmed against eight literals, and trimming diverges on every multi-artist
    # credit in the corpus (LBDR-F2).
    print("building artist_credit")
    t = time.time()
    dst = (OUT_DIR / "artist_credit.parquet").as_posix()
    con.execute(
        f"""
        COPY (
            SELECT acn.artist_credit           AS artist_credit_id
                 , a.gid                       AS artist_mbid
                 , acn.position                AS position
                 , {unescape('acn.join_phrase')} AS join_phrase
              FROM {tsv('artist_credit_name', [('artist_credit','BIGINT'),('position','BIGINT'),
                                               ('artist','BIGINT'),('name','VARCHAR'),
                                               ('join_phrase','VARCHAR')])} acn
              JOIN {tsv('artist', [('id','BIGINT'),('gid','VARCHAR'),('name','VARCHAR'),
                                   ('sort_name','VARCHAR'),('begin_y','BIGINT'),('begin_m','BIGINT'),
                                   ('begin_d','BIGINT'),('end_y','BIGINT'),('end_m','BIGINT'),
                                   ('end_d','BIGINT'),('type','BIGINT'),('area','BIGINT'),
                                   ('gender','BIGINT'),('comment','VARCHAR'),
                                   ('edits_pending','BIGINT'),('last_updated','VARCHAR'),
                                   ('ended','VARCHAR')])} a
                ON a.id = acn.artist
              JOIN {tsv('artist_credit', [('id','BIGINT'),('name','VARCHAR'),
                                          ('artist_count','BIGINT'),('ref_count','BIGINT'),
                                          ('created','VARCHAR'),('edits_pending','BIGINT'),
                                          ('gid','VARCHAR')])} ac
                ON ac.id = acn.artist_credit
             ORDER BY artist_credit_id, position
        ) TO '{dst}' (FORMAT PARQUET)
        """
    )
    out["artist_credit"] = frame_stats(con, dst, time.time() - t)

    # --- artist_identity: what the archive emitter writes as name/comment ---
    print("building artist_identity")
    t = time.time()
    dst = (OUT_DIR / "artist_identity.parquet").as_posix()
    con.execute(
        f"""
        COPY (
            SELECT gid AS artist_mbid
                 , {unescape('name')}    AS name
                 , {unescape('comment')} AS comment
              FROM {tsv('artist', [('id','BIGINT'),('gid','VARCHAR'),('name','VARCHAR'),
                                   ('sort_name','VARCHAR'),('begin_y','BIGINT'),('begin_m','BIGINT'),
                                   ('begin_d','BIGINT'),('end_y','BIGINT'),('end_m','BIGINT'),
                                   ('end_d','BIGINT'),('type','BIGINT'),('area','BIGINT'),
                                   ('gender','BIGINT'),('comment','VARCHAR'),
                                   ('edits_pending','BIGINT'),('last_updated','VARCHAR'),
                                   ('ended','VARCHAR')])}
             ORDER BY artist_mbid
        ) TO '{dst}' (FORMAT PARQUET)
        """
    )
    out["artist_identity"] = frame_stats(con, dst, time.time() - t)
    return out


def frame_stats(con: duckdb.DuckDBPyConnection, dst: str, elapsed: float) -> dict:
    rows = con.execute(f"SELECT count(*) FROM read_parquet('{dst}')").fetchone()[0]
    p = Path(dst)
    stats = {
        "path": str(p),
        "rows": rows,
        "bytes": p.stat().st_size,
        "sha256": sha256_file(p),
        "seconds": round(elapsed, 1),
    }
    print(f"  rows {rows:>12,}   {stats['bytes']/1e6:8.1f} MB   {elapsed:6.1f} s")
    print(f"  sha256 {stats['sha256']}")
    return stats


def join_phrase_read(con: duckdb.DuckDBPyConnection) -> dict:
    """Is the 0.25 featured weight live on this corpus at all?

    Plain sentence: ListenBrainz weights an artist at a quarter when the credit's
    join phrase is one of eight literals. MusicBrainz stores join phrases WITH their
    surrounding spaces and ListenBrainz compares them untrimmed. So how often does
    that comparison actually fire on the real table?

    Descriptive. It does NOT change the reimplementation, which must reproduce LB's
    behaviour whether the term is live or dead -- it tells a later reader how much of
    LBD-C1 could possibly turn on it. LBDR-F2.
    """
    print("\n" + "=" * 78)
    print("R-FEAT -- is the 0.25 featured weight live on this corpus?")
    print("=" * 78)
    src = (OUT_DIR / "artist_credit.parquet").as_posix()
    lits = ("'feat.', 'ｆｅａｔ.', 'ft.', 'συμμ.', 'duet with', 'featuring',"
            " 'συμμετέχει', 'ｆｅａｔｕｒｉｎｇ'")
    total, exact, trimmed, nonempty = con.execute(
        f"""
        SELECT count(*)
             , count(*) FILTER (WHERE join_phrase IN ({lits}))
             , count(*) FILTER (WHERE trim(join_phrase) IN ({lits}))
             , count(*) FILTER (WHERE join_phrase IS NOT NULL AND join_phrase != '')
          FROM read_parquet('{src}')
        """
    ).fetchone()
    print(f"  credit-name rows                         {total:>12,}")
    print(f"  with a non-empty join phrase             {nonempty:>12,}"
          f"  {100*nonempty/total:6.3f}%")
    print(f"  MATCHING LB's literals AS LB COMPARES    {exact:>12,}"
          f"  {100*exact/total:6.4f}%   <- the weight fires here")
    print(f"  matching only if TRIMMED first           {trimmed:>12,}"
          f"  {100*trimmed/total:6.4f}%   <- what a trimming implementer would hit")
    ratio = (trimmed / exact) if exact else float("inf")
    print(f"\n  trimmed/exact ratio {ratio:,.1f}x"
          f"   -- the size of the divergence if an implementer trims")
    print("\n  most common join phrases containing a listed literal:")
    rows = con.execute(
        f"""
        SELECT join_phrase, count(*) AS n
          FROM read_parquet('{src}')
         WHERE trim(join_phrase) IN ({lits})
      GROUP BY 1 ORDER BY n DESC LIMIT 10
        """
    ).fetchall()
    for jp, n in rows:
        print(f"    {n:>10,}  {jp!r}")
    return {"rows": total, "nonempty": nonempty, "match_exact": exact,
            "match_trimmed": trimmed, "top_phrases": [[jp, n] for jp, n in rows]}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    verify_tarball()
    extract()

    meta = {}
    for name in ("SCHEMA_SEQUENCE", "TIMESTAMP"):
        p = MB_DIR / "mbdump" / name
        meta[name] = p.read_text().strip() if p.exists() else None
        print(f"  mbdump {name:<16} {meta[name]}")

    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='20GB'")
    con.execute("PRAGMA temp_directory='D:/unsung-large-data/duckdb-tmp'")
    con.execute("PRAGMA threads=16")
    con.execute("PRAGMA disable_progress_bar")

    result = {
        "mbdump": {"tarball": str(TARBALL), "sha256": EXPECTED_SHA, **meta},
        "frames": build_frames(con),
        "r_feat": join_phrase_read(con),
    }
    out = OUT_DIR / "inputs_extract.json"
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    sys.exit(main())
