"""`LBD-AM4-5` — the descriptive threshold curve from `T`. NO GATE, NO EFFECT SIZE.

Plain sentence, fixed in the amendment before this ran:

  > before the second build, look at how the number of dead ends among the added artists
  > changes as the strength bar is lowered one notch at a time — so the owner can see
  > whether "accept every connection however weak" is where the gain is, or whether most
  > of it arrives by a bar of 2 or 3.

For each of the four fixed sets (added 29,892; its LBD-AM1 residual stratum 5,967 and
complement 23,925; pre-existing 58,793) and each of sixteen (threshold, limit) cells —
threshold in {0,1,2,3,4,5,7,10}, limit in {100, none} — the share of artists at <= 2 distinct
partners (absent counted as 0), the share absent, the share at exactly 1, and the median
partner count. Every cell is EXACTLY the arm the pre-registration's section 1 would derive at
those tokens: `HAVING score > threshold`, then `rank() OVER (PARTITION BY mbid0 ORDER BY
score DESC) <= limit`.

WHY ONE RANKING SERVES EVERY THRESHOLD. `rank()` orders by score descending inside an
`mbid0` partition; filtering away rows with score <= t removes only rows that sort BELOW
every surviving row, so a surviving row's rank is unchanged. So the window is computed once
over `T` and each cell is a filter on (score, rank). Verified by the green check below rather
than asserted.

GREEN CHECK (the instrument must reproduce what it did not compute): the (10, 100) cell must
equal README section 6's `LBD-A0` row and the (0, 100) cell its `LBD-A2` row — both read from
the committed `c2a.json` files those arms wrote, on all four sets, to the last digit. The
script REFUSES to write the curve if either disagrees.

Pairs in `T` are unique and oriented `mbid0 < mbid1` (checked 2026-09-10 on `A0`: 0 rows with
mbid0 >= mbid1, 0 duplicate pairs), so an artist's partners in the two directions are disjoint
and `count(*)` per direction is a distinct-partner count — the same quantity
`lbd_reads.py:degrees` computes with `count(DISTINCT partner)`.

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run --with duckdb python -u analysis/2026-09-08-lbd-similarity/lbd_threshold_curve.py \\
        --table C:/unsung-fast/lbd-pairs/aggregate/T.parquet \\
        --out-dir C:/unsung-fast/lbd-pairs/curve

RUN ALONE. The first attempt (2026-09-10 19:12, 16 GB limit, default threads) died with an
access violation inside DuckDB's native module twelve minutes in, in the same minute a second
DuckDB process on the machine ran out of its own memory limit; the intermediate it was writing
was left without a footer. Nothing else heavy should run beside this.

Writes nothing into `builder/scratch/` (`LBD-D8`). The ranked-and-filtered intermediate
lands under --out-dir and is identified by sha256 in the JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

import duckdb

INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
ADDED = INPUTS / "cxr_added_mbids.txt"
PREEXISTING = INPUTS / "cxr_preexisting_mbids.txt"
RESIDUAL = INPUTS / "cxr_residual_mbids.txt"
PAIRS = Path(r"C:\unsung-fast\lbd-pairs")

THRESHOLDS = (0, 1, 2, 3, 4, 5, 7, 10)
LIMITS = (100, None)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def load_set(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def col(t: int, limit: int | None) -> str:
    return f"t{t}_l{limit if limit is not None else 'none'}"


def summarise(deg: list[int]) -> dict:
    vals = sorted(deg)
    n = len(vals)
    return {
        "n": n,
        "share_le_2": sum(1 for v in vals if v <= 2) / n,
        "share_absent": sum(1 for v in vals if v == 0) / n,
        "share_eq_1": sum(1 for v in vals if v == 1) / n,
        "median_partners": statistics.median(vals),
        "mean_partners": sum(vals) / n,
    }


def green_check(curve: dict, arm: str, t: int, limit: int) -> list[str]:
    """Compare one cell with the committed c2a.json of the arm it must reproduce."""
    ref = json.loads((PAIRS / arm / "c2a.json").read_text(encoding="utf-8"))
    pairs = (("added", "whole_set"), ("residual", "residual"),
             ("complement", "complement"), ("preexisting", "preexisting_reference"))
    problems = []
    for mine, theirs in pairs:
        cell = curve[mine][col(t, limit)]
        r = ref[theirs]
        for a, b in (("share_le_2", "share_le_2"), ("share_absent", "share_absent"),
                     ("median_partners", "median_degree_REPORTED_NOT_GATED")):
            if abs(cell[a] - r[b]) > 1e-12:
                problems.append(f"{arm} ({t},{limit}) {mine}.{a}: curve {cell[a]} != c2a.json {r[b]}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--memory-limit-gb", type=int, default=12)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--temp-dir", type=Path, default=Path(r"C:/unsung-fast/duckdb-temp"))
    ap.add_argument("--reuse-ranked", action="store_true",
                    help="skip the window pass if ranked_P.parquet already exists")
    args = ap.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.temp_dir.mkdir(parents=True, exist_ok=True)

    t_start = time.monotonic()
    table_sha = sha256_of(args.table)
    print(f"[curve] T {args.table}  sha256 {table_sha}", flush=True)
    if not table_sha.startswith("03d47b05"):
        raise SystemExit("REFUSING: that is not the T the handoff records (03d47b05…)")

    added = load_set(ADDED)
    pre = load_set(PREEXISTING)
    residual = set(load_set(RESIDUAL))
    assert residual <= set(added), "residual set is not a subset of the added set"
    groups = {m: "added_residual" if m in residual else "added_complement" for m in added}
    groups.update({m: "preexisting" for m in pre})
    print(f"[curve] added {len(added):,} (residual {len(residual):,})  pre-existing {len(pre):,}", flush=True)

    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{args.memory_limit_gb}GB'")
    con.execute(f"PRAGMA threads={args.threads}")
    con.execute(f"PRAGMA temp_directory='{args.temp_dir.as_posix()}'")
    con.execute("PRAGMA preserve_insertion_order=false")
    con.execute("CREATE TABLE q(mbid VARCHAR, grp VARCHAR)")
    con.executemany("INSERT INTO q VALUES (?, ?)", list(groups.items()))

    ranked = args.out_dir / "ranked_P.parquet"
    if not (args.reuse_ranked and ranked.is_file()):
        # ONE window pass over T; keep only rows that touch a set member, with the row's rank
        # in its mbid0 partition. The rank is over the FULL partition, never over the filtered
        # rows — that is the property the docstring argues from.
        t0 = time.monotonic()
        con.execute(f"""
            COPY (
                WITH r AS (
                    SELECT mbid0, mbid1, score,
                           rank() OVER (PARTITION BY mbid0 ORDER BY score DESC) AS rk
                      FROM read_parquet('{args.table.as_posix()}')
                )
                SELECT mbid0, mbid1, score, rk FROM r
                 WHERE mbid0 IN (SELECT mbid FROM q) OR mbid1 IN (SELECT mbid FROM q)
            ) TO '{ranked.as_posix()}' (FORMAT PARQUET, ROW_GROUP_SIZE 500000)
        """)
        print(f"[curve] ranked+filtered T written in {(time.monotonic() - t0) / 60:.1f} min", flush=True)
    ranked_rows = con.execute(f"SELECT count(*) FROM read_parquet('{ranked.as_posix()}')").fetchone()[0]
    print(f"[curve] ranked_P rows {ranked_rows:,}", flush=True)

    # Both directions, restricted to set members, then sixteen filtered counts in one pass.
    filters = []
    for t in THRESHOLDS:
        for limit in LIMITS:
            cond = f"score > {t}" + (f" AND rk <= {limit}" if limit is not None else "")
            filters.append(f"count(*) FILTER (WHERE {cond}) AS {col(t, limit)}")
    t0 = time.monotonic()
    rows = con.execute(f"""
        WITH u AS (
            SELECT q.mbid AS artist, r.score, r.rk
              FROM read_parquet('{ranked.as_posix()}') r JOIN q ON r.mbid0 = q.mbid
            UNION ALL
            SELECT q.mbid AS artist, r.score, r.rk
              FROM read_parquet('{ranked.as_posix()}') r JOIN q ON r.mbid1 = q.mbid
        )
        SELECT artist, {", ".join(filters)} FROM u GROUP BY artist
    """).fetchall()
    print(f"[curve] per-artist counts for {len(rows):,} artists in {(time.monotonic() - t0) / 60:.1f} min", flush=True)
    names = [col(t, l) for t in THRESHOLDS for l in LIMITS]
    counts = {row[0]: dict(zip(names, row[1:])) for row in rows}

    sets = {
        "added": added,
        "residual": [m for m in added if m in residual],
        "complement": [m for m in added if m not in residual],
        "preexisting": pre,
    }
    curve: dict = {}
    for set_name, members in sets.items():
        curve[set_name] = {}
        for name in names:
            deg = [counts[m][name] if m in counts else 0 for m in members]
            curve[set_name][name] = summarise(deg)

    problems = green_check(curve, "A0", 10, 100) + green_check(curve, "A2", 0, 100)
    if problems:
        for p in problems:
            print("  RED:", p, flush=True)
        raise SystemExit("REFUSING to write the curve: the instrument does not reproduce A0/A2")
    print("[curve] GREEN: (10,100) reproduces A0's c2a.json and (0,100) reproduces A2's, all four sets", flush=True)

    out = {
        "amendment": "LBD-AM4-5 — descriptive; no gate, no effect size; decides nothing",
        "table": str(args.table), "table_sha256": table_sha,
        "ranked_P_parquet": str(ranked), "ranked_P_sha256": sha256_of(ranked), "ranked_P_rows": ranked_rows,
        "inputs": {p.name: sha256_of(p) for p in (ADDED, PREEXISTING, RESIDUAL)},
        "script_sha256": sha256_of(Path(__file__)),
        "thresholds": THRESHOLDS, "limits": [100, None],
        "green_check": "(10,100)==A0 c2a.json and (0,100)==A2 c2a.json on share_le_2, share_absent, median — passed",
        "curve": curve,
        "wall_clock_s": round(time.monotonic() - t_start, 1),
        "duckdb": duckdb.__version__,
    }
    out_path = args.out_dir / "threshold_curve.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # A markdown rendering, so the README section is a paste and not a transcription.
    lines = []
    for set_name in sets:
        lines.append(f"\n**{set_name}** (n = {curve[set_name][names[0]]['n']:,})\n")
        lines.append("| threshold | limit | share ≤ 2 | share absent | share = 1 | median partners |")
        lines.append("|---:|---|---:|---:|---:|---:|")
        for t in THRESHOLDS:
            for limit in LIMITS:
                c = curve[set_name][col(t, limit)]
                lines.append(f"| {t} | {limit if limit else 'none'} | {c['share_le_2']:.4f} | {c['share_absent']:.4f} | {c['share_eq_1']:.4f} | {c['median_partners']:g} |")
    (args.out_dir / "threshold_curve.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)
    print(f"\n[curve] wrote {out_path}  ({out['wall_clock_s'] / 60:.1f} min)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
