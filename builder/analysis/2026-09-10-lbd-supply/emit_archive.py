"""`LBD-` Task 6 — emit one derived arm as an archive the SHIPPED builder can read.

Under `LBD-AM4-1` the population is FIXED to `P`, the node set of `graph-cxa-adopted.bin`:
a payload is written only for an artist in `P`, and a neighbour row only when BOTH endpoints
are in `P`. The arm's threshold and rank cut are the DERIVED parquet's (sha-pinned; README
section 6 of the Task 4 figures owner) — this script filters, it never re-ranks.

What one payload is (`LBD-D3`): the endpoint's own row shape, using the `FIELD_*` constants
read from `sources/listenbrainz.py` (never transcribed from memory), one row per neighbour,
`name`/`comment` from Task 1's identity frame (`artist_identity.parquet`, the MusicBrainz
artist table). Each pair's two directions are unioned — `T` holds each pair once as
`mbid0 < mbid1`, and the endpoint serves both partitions (`LBS-3`). Deterministic: neighbours
sorted `(-score, mbid)`, files written in sorted-MBID order, `json.dumps(sort_keys=True)`.

An artist in `P` with no identity row gets an empty name; `build`'s nameless rule drops it
(`pipeline.py`, "Nameless artists are dropped, unconditionally"). They are COUNTED here and
reported — if it is more than a handful the identity join is wrong (plan Task 6).

Writes to `--out` (an archive root, one per arm) through the builder's own `LocalArchive`, so
the on-disk layout is the builder's and not a re-implementation of it. Reads `builder/scratch/`
by absolute path from the MAIN tree and never writes into it (`LBD-D8`).

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run --with duckdb python -u analysis/2026-09-10-lbd-supply/emit_archive.py \\
        --arm A0 --pairs C:/unsung-fast/lbd-pairs/A0/A0.parquet \\
        --out C:/unsung-fast/lbd-archives/A0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(REPO / "api" / "src"))  # the shipped GraphStore (cxr_census.py precedent)

from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM  # noqa: E402
from artistpath_builder.sources.listenbrainz import (  # noqa: E402
    FIELD_COMMENT,
    FIELD_MBID,
    FIELD_NAME,
    FIELD_SCORE,
)

from lbd_source import LbdBulkSource  # noqa: E402

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
CXA = SCRATCH / "graph-cxa-adopted.bin"
INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
IDENTITY = INPUTS / "artist_identity.parquet"
INPUTS_EXTRACT = INPUTS / "inputs_extract.json"
T_MANIFEST = Path(r"C:\unsung-fast\lbd-pairs\aggregate\T.manifest.json")
ARCHIVES = Path(r"C:\unsung-fast\lbd-archives")
POPULATION_FILE = ARCHIVES / "population_cxa_mbids.txt"

ARM_TOKENS = {"A0": {"threshold": 10, "limit": 100}, "A2": {"threshold": 0, "limit": 100}}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def verified_population() -> tuple[list[str], str]:
    """`P`, sorted, from the artifact — refused unless its bytes match its sidecar."""
    manifest = json.loads(CXA.with_suffix(".bin.json").read_text(encoding="utf-8"))
    digest = sha256_of(CXA)
    if digest != manifest["sha256"]:
        raise SystemExit(f"REFUSING: {CXA.name} sha256 {digest} != sidecar {manifest['sha256']}")
    store = GraphStore.load(CXA)
    mbids = sorted(store.mbids)
    if len(mbids) != manifest["artists"]:
        raise SystemExit("REFUSING: node count disagrees with the sidecar")
    print(f"[emit] P = {CXA.name}  sha256 {digest}  nodes {len(mbids):,}", flush=True)
    return mbids, digest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARM_TOKENS))
    ap.add_argument("--pairs", type=Path, required=True, help="the arm's DERIVED parquet")
    ap.add_argument("--out", type=Path, required=True, help="archive root for this arm")
    ap.add_argument("--memory-limit-gb", type=int, default=8)
    args = ap.parse_args(argv)
    started = time.monotonic()

    # --- identities of every input, before anything is read ---------------------------------
    arm_manifest = json.loads(args.pairs.with_name(f"{args.arm}.manifest.json").read_text(encoding="utf-8"))
    pairs_sha = sha256_of(args.pairs)
    if pairs_sha != arm_manifest["out_sha256"]:
        raise SystemExit(f"REFUSING: {args.pairs.name} sha256 {pairs_sha} != its manifest {arm_manifest['out_sha256']}")
    if (arm_manifest["threshold"], arm_manifest["limit"]) != (ARM_TOKENS[args.arm]["threshold"], ARM_TOKENS[args.arm]["limit"]):
        raise SystemExit("REFUSING: the parquet's manifest tokens are not this arm's")
    t_manifest = json.loads(T_MANIFEST.read_text(encoding="utf-8"))
    if arm_manifest["derived_from_sha256"] != t_manifest["out_sha256"]:
        raise SystemExit("REFUSING: the arm was not derived from the T on disk")
    identity_sha = sha256_of(IDENTITY)
    extract = json.loads(INPUTS_EXTRACT.read_text(encoding="utf-8"))
    if extract["frames"]["artist_identity"]["sha256"] != identity_sha:
        raise SystemExit("REFUSING: artist_identity.parquet is not Task 1's")
    print(f"[emit] arm {args.arm}  pairs {args.pairs.name} sha256 {pairs_sha}  rows {arm_manifest['rows']:,}", flush=True)

    population, cxa_sha = verified_population()
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    POPULATION_FILE.write_text("\n".join(population) + "\n", encoding="utf-8")
    population_sha = sha256_of(POPULATION_FILE)
    pset = set(population)

    # --- the pairs, both endpoints in P, and the identity frame restricted to P ---------------
    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{args.memory_limit_gb}GB'")
    con.execute("PRAGMA temp_directory='C:/unsung-fast/duckdb-temp'")
    con.execute("CREATE TABLE p(mbid VARCHAR)")
    con.executemany("INSERT INTO p VALUES (?)", [(m,) for m in population])
    pq = args.pairs.as_posix()
    total, both, one_end, none = con.execute(f"""
        SELECT count(*),
               count(*) FILTER (WHERE m0 AND m1),
               count(*) FILTER (WHERE m0 <> m1),
               count(*) FILTER (WHERE NOT m0 AND NOT m1)
          FROM (SELECT (mbid0 IN (SELECT mbid FROM p)) AS m0,
                       (mbid1 IN (SELECT mbid FROM p)) AS m1
                  FROM read_parquet('{pq}'))
    """).fetchone()
    print(f"[emit] arm rows {total:,}: both in P {both:,}  one end {one_end:,}  neither {none:,}", flush=True)
    # --- the neighbour lists are assembled INSIDE DuckDB, both directions, sorted (-score, mbid)
    # per artist, and streamed out in sorted-MBID order. Python never holds the pair table:
    # A2 restricted to P is tens of millions of rows, and a list of Python tuples that size
    # is the wrong shape for a 32 GB machine already running the threshold curve. ----------
    identity = {
        m: (n or "", c or "")
        for m, n, c in con.execute(f"""
            SELECT artist_mbid, name, comment FROM read_parquet('{IDENTITY.as_posix()}')
             WHERE artist_mbid IN (SELECT mbid FROM p)
        """).fetchall()
    }
    no_identity = sorted(m for m in population if m not in identity)
    print(f"[emit] identity rows for P: {len(identity):,}; P members with NO identity row: {len(no_identity):,}", flush=True)

    # One sorted stream — (artist, -score, partner) — grouped by consecutive artist as it is
    # consumed. A sort spills cleanly; a per-group list aggregation did not fit beside the
    # threshold curve on this machine (first attempt, 2026-09-10, out of memory at 8 GB).
    con.execute("PRAGMA preserve_insertion_order=false")
    cur = con.execute(f"""
        WITH k AS (
            SELECT mbid0, mbid1, score FROM read_parquet('{pq}')
             WHERE mbid0 IN (SELECT mbid FROM p) AND mbid1 IN (SELECT mbid FROM p)
        ), u AS (
            SELECT mbid0 AS a, mbid1 AS b, score FROM k
            UNION ALL
            SELECT mbid1 AS a, mbid0 AS b, score FROM k
        )
        SELECT a, b, score FROM u ORDER BY a, score DESC, b
    """)

    # --- write, in sorted-MBID order, through the builder's own archive layout ---------------
    source = LbdBulkSource.__new__(LbdBulkSource)  # only .name is needed here; no config
    prefix = f"similar/{source.name}/{CANDIDATE_ALGORITHM}/"
    archive = LocalArchive(args.out)
    emitted = rows_written = emitted_nameless = 0
    seen: set[str] = set()
    last: str | None = None

    def flush(mbid: str, rows: list[dict]) -> None:
        nonlocal emitted, rows_written, emitted_nameless
        if mbid not in pset:
            raise SystemExit(f"BUG: {mbid} is not in P")
        if mbid in seen or (last is not None and mbid < last):
            raise SystemExit(f"BUG: stream is not sorted by artist at {mbid}")
        seen.add(mbid)
        archive.put(f"{prefix}{mbid}.json", json.dumps(rows, sort_keys=True, ensure_ascii=False).encode("utf-8"))
        emitted += 1
        rows_written += len(rows)
        if mbid not in identity:
            emitted_nameless += 1

    current: list[dict] = []
    while True:
        batch = cur.fetchmany(50000)
        if not batch:
            break
        for a, b, score in batch:
            if a != last:
                if last is not None:
                    flush(last, current)
                current = []
                last = a
            name, comment = identity.get(b, ("", ""))
            current.append({FIELD_MBID: b, FIELD_NAME: name, FIELD_COMMENT: comment, FIELD_SCORE: int(score)})
    if last is not None:
        flush(last, current)
    con.close()
    absent = [m for m in population if m not in seen]
    if rows_written != 2 * both:
        raise SystemExit(f"BUG: wrote {rows_written} neighbour rows, expected {2 * both}")
    elapsed = time.monotonic() - started
    print(f"[emit] payloads {emitted:,}  neighbour rows {rows_written:,}  P absent from arm {len(absent):,}  "
          f"emitted with no identity row {emitted_nameless:,}  ({elapsed / 60:.1f} min)", flush=True)

    manifest = {
        "arm": f"LBD-{args.arm}",
        "amendment": "LBD-AM4 — population fixed to P; filter after the derived cut, never re-ranked",
        "source_name": source.name,
        "archive_prefix": prefix,
        "algorithm_token_is_drop_list_lineage_not_parameters": CANDIDATE_ALGORITHM,
        "parameters": {**t_manifest["params"], **ARM_TOKENS[args.arm]},
        "dump": {"path": t_manifest["dump"], "id": 2647, "end_timestamp": t_manifest["dump_end_timestamp"],
                 "identity_note": "the tar's byte identity is not verified (Task 1 README §1); identity rests on SCHEMA_SEQUENCE/TIMESTAMP/file count"},
        "mbdump": extract["mbdump"],
        "T": {"path": t_manifest["out"], "sha256": t_manifest["out_sha256"], "rows": t_manifest["rows"],
              "lb_source_sha256": t_manifest["lb_source_sha256"], "pass_script_sha256": t_manifest["script_sha256"]},
        "derived_arm": {"path": str(args.pairs), "sha256": pairs_sha, "rows": arm_manifest["rows"],
                        "derive_script_sha256": arm_manifest["script_sha256"]},
        "identity_frame": {"path": str(IDENTITY), "sha256": identity_sha},
        "population": {"artifact": CXA.name, "artifact_sha256": cxa_sha, "file": str(POPULATION_FILE),
                       "file_sha256": population_sha, "count": len(population)},
        "emitter_script_sha256": sha256_of(Path(__file__)),
        "source_script_sha256": sha256_of(HERE / "lbd_source.py"),
        "counts": {
            "arm_rows_total": total, "arm_rows_both_in_P": both, "arm_rows_one_end_in_P": one_end,
            "arm_rows_neither_in_P": none,
            "payloads_written": emitted, "neighbour_rows_written": rows_written,
            "P_absent_from_arm": len(absent), "P_with_no_identity_row": len(no_identity),
            "emitted_with_no_identity_row": emitted_nameless,
        },
        "P_with_no_identity_row_mbids": no_identity,
        "wall_clock_s": round(elapsed, 1),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    (args.out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[emit] wrote {args.out / 'MANIFEST.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
