"""`LBD-P1` — how many listens in a ListenBrainz *Spark/parquet* dump carry MBIDs.

Read-only. Offline once the dump is on disk. No project imports — this is a
frozen probe, and it must keep running after the builder moves on.

The number this exists to measure was recorded in
`docs/superpowers/findings/2026-07-19-listenbrainz-probe.md` §6c as 0.03 % —
on the JSON *listens* dump, whose records carry only what the submitting client
sent. The parquet dump is written by `listenbrainz/listenstore/dump_listenstore.py`
with LB's own `mbid_mapping` joined in, and is the dump the similarity job
reads. The two figures are for different files and are both correct.

Run (from anywhere; no .venv needed):

    UV_LINK_MODE=copy uv run --with pyarrow python -u coverage_probe.py \
        --dump-dir D:/unsung-large-data/incremental-2653/listenbrainz-spark-dump-2653-20260906-000002-incremental

The dump directory holds `N.parquet` files plus `COPYING`, `SCHEMA_SEQUENCE`,
`START_TIMESTAMP`, `END_TIMESTAMP`. Figures are owned by README.md beside this
file; nothing else restates them.
"""

from __future__ import annotations

import argparse
import glob
import os
import statistics

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def load(dump_dir: str) -> pa.Table:
    files = sorted(glob.glob(os.path.join(dump_dir, "*.parquet")))
    if not files:
        raise SystemExit(f"no parquet files under {dump_dir}")
    return pa.concat_tables([pq.read_table(f) for f in files])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-dir", required=True)
    args = ap.parse_args()

    for name in ("START_TIMESTAMP", "END_TIMESTAMP", "SCHEMA_SEQUENCE"):
        path = os.path.join(args.dump_dir, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                print(f"{name}: {fh.read().strip()}")

    t = load(args.dump_dir)
    n = t.num_rows
    print("schema:")
    for field in t.schema:
        print(f"  {field.name}: {field.type}")

    rec = t["recording_mbid"]
    has_rec = pc.sum(pc.and_(pc.is_valid(rec), pc.not_equal(rec, ""))).as_py()
    acm = t["artist_credit_mbids"]
    has_art = pc.sum(
        pc.and_(pc.is_valid(acm), pc.greater(pc.list_value_length(acm), 0))
    ).as_py()
    users = pc.count_distinct(t["user_id"]).as_py()
    flat = pc.list_flatten(acm)
    artists = pc.count_distinct(flat).as_py()

    print(f"listens={n:,} users={users:,}")
    print(f"recording_mbid present: {has_rec:,} ({100 * has_rec / n:.1f}%)")
    print(f"artist_credit_mbids non-empty: {has_art:,} ({100 * has_art / n:.1f}%)")
    print(f"distinct artist mbids: {artists:,}")

    counts = sorted(
        (row["counts"].as_py() for row in pc.value_counts(t["user_id"])), reverse=True
    )
    print(
        "listens/user: median", statistics.median(counts),
        "p90", counts[len(counts) // 10], "max", counts[0],
    )
    acounts = [row["counts"].as_py() for row in pc.value_counts(flat)]
    for k in (1, 2, 5, 10, 50):
        print(f"artists with >= {k} listens: {sum(1 for c in acounts if c >= k):,}")


if __name__ == "__main__":
    main()
