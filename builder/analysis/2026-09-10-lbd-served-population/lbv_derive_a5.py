"""`LBD-AM5-2` — derive `LBD-A5` (`score > 3`, ranked per `mbid0`, `rank <= 100`) from `T`.

Runs the Task 4 derivation script UNEDITED (`../2026-09-08-lbd-similarity/lbd_derive.py`): its
`derive_sql` is the pre-registration §1 definition, and its `ARMS` table is extended here with the
one new entry rather than copied, so the SQL that runs is the SQL that derived `LBD-A0`–`LBD-A3`.
Its manifest records that script's sha256 as `script_sha256`; this wrapper adds its own.

Before reading, `T` is verified against its manifest. After writing, the derived table is checked
against the committed descriptive curve (`../2026-09-08-lbd-similarity/threshold_curve.json`, the
(3, 100) cell on all four pinned sets) with the Task 4 `c2a` degree SQL — the curve and this table
are the same object at those tokens, so any disagreement is a derivation defect and the script
refuses. This is the instrument's green check; it is not a criterion.

RUN ALONE: two DuckDB processes side by side on this machine ended in an access violation
(`2026-09-10-lbd-task67-execution-log.md`, Step 2).

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run --with duckdb python -u analysis/2026-09-10-lbd-served-population/lbv_derive_a5.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
SIMILARITY = HERE.parent / "2026-09-08-lbd-similarity"
sys.path.insert(0, str(SIMILARITY))

import lbd_derive  # noqa: E402

T = Path(r"C:\unsung-fast\lbd-pairs\aggregate\T.parquet")
T_MANIFEST = T.with_name("T.manifest.json")
OUT = Path(r"C:\unsung-fast\lbd-pairs\A5\A5.parquet")
CURVE = SIMILARITY / "threshold_curve.json"
INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
PINNED = {
    "added": (INPUTS / "cxr_added_mbids.txt", "bfed95ef74b0665c50b1532708091b4e43fab36247db391d04064870659a4339"),
    "preexisting": (INPUTS / "cxr_preexisting_mbids.txt", "768054b7e84769346193336ec7e9b3496af92d0d3e8d4ae2fb287057912b5229"),
    "residual": (INPUTS / "cxr_residual_mbids.txt", "fa8d85cc12131f3cd39ecebeb5da0d52a1236104acbcbabf20232c72b4f43a08"),
}
THRESHOLD, LIMIT = 3, 100


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def pinned(name: str) -> list[str]:
    path, sha = PINNED[name]
    if sha256_of(path) != sha:
        raise SystemExit(f"REFUSING: {path.name} is not the pinned file")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def partner_counts(table: Path, mbids: list[str]) -> dict[str, int]:
    """Distinct partners per artist over both halves of the table — the `c2a` statistic's input."""
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='12GB'")
    con.execute("PRAGMA temp_directory='C:/unsung-fast/duckdb-temp'")
    con.execute("CREATE TABLE s(mbid VARCHAR)")
    con.executemany("INSERT INTO s VALUES (?)", [(m,) for m in mbids])
    pq = table.as_posix()
    rows = con.execute("""
        SELECT m, count(DISTINCT p) FROM (
            SELECT mbid0 AS m, mbid1 AS p FROM read_parquet(?) WHERE mbid0 IN (SELECT mbid FROM s)
            UNION ALL
            SELECT mbid1 AS m, mbid0 AS p FROM read_parquet(?) WHERE mbid1 IN (SELECT mbid FROM s)
        ) GROUP BY m
    """, [pq, pq]).fetchall()
    con.close()
    return {m: int(n) for m, n in rows}


def main() -> int:
    t_manifest = json.loads(T_MANIFEST.read_text(encoding="utf-8"))
    t_sha = sha256_of(T)
    if t_sha != t_manifest["out_sha256"]:
        raise SystemExit(f"REFUSING: T.parquet sha256 {t_sha} != its manifest")
    print(f"[a5] T verified  sha256 {t_sha}", flush=True)

    lbd_derive.ARMS["A5"] = (THRESHOLD, LIMIT)
    rc = lbd_derive.main(["--table", str(T), "--arm", "A5", "--out", str(OUT),
                          "--memory-limit-gb", "12", "--temp-dir", "C:/unsung-fast/duckdb-temp"])
    if rc:
        return rc

    manifest_path = OUT.with_suffix(".manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest["threshold"], manifest["limit"]) != (THRESHOLD, LIMIT) or manifest["derived_from_sha256"] != t_sha:
        raise SystemExit("BUG: the derived manifest does not record LBD-A5's tokens over this T")

    # --- the green check against the committed curve's (3, 100) cell --------------------------
    curve = json.loads(CURVE.read_text(encoding="utf-8"))
    sets = {"added": pinned("added"), "preexisting": pinned("preexisting")}
    residual = set(pinned("residual"))
    sets["residual"] = [m for m in sets["added"] if m in residual]
    sets["complement"] = [m for m in sets["added"] if m not in residual]
    counts = partner_counts(OUT, sorted(set(sets["added"]) | set(sets["preexisting"])))
    checks = {}
    for name, members in sets.items():
        degrees = sorted(counts.get(m, 0) for m in members)
        share_le_2 = sum(1 for d in degrees if d <= 2) / len(degrees)
        share_absent = sum(1 for d in degrees if d == 0) / len(degrees)
        mid = len(degrees) // 2
        median = float(degrees[mid]) if len(degrees) % 2 else (degrees[mid - 1] + degrees[mid]) / 2
        cell = curve["curve"][name][f"t{THRESHOLD}_l{LIMIT}"]
        # Same counts over the same n: the shares must agree to float precision, not to a rounding.
        ok = (abs(share_le_2 - cell["share_le_2"]) < 1e-12 and abs(share_absent - cell["share_absent"]) < 1e-12
              and median == cell["median_partners"])
        checks[name] = {"share_le_2": share_le_2, "share_absent": share_absent, "median_partners": median,
                        "curve_share_le_2": cell["share_le_2"], "curve_share_absent": cell["share_absent"],
                        "curve_median_partners": cell["median_partners"], "match": ok}
        print(f"[a5] {name:<12} share<=2 {share_le_2:.4f} (curve {cell['share_le_2']:.4f})  "
              f"absent {share_absent:.4f} (curve {cell['share_absent']:.4f})  {'OK' if ok else 'MISMATCH'}", flush=True)
    if not all(c["match"] for c in checks.values()):
        raise SystemExit("REFUSING: LBD-A5 does not reproduce the committed curve's (3, 100) cell")

    manifest["amendment"] = "LBD-AM5-2"
    manifest["wrapper_script_sha256"] = sha256_of(Path(__file__))
    manifest["curve_reproduction"] = checks
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[a5] {manifest['rows']:,} rows; manifest updated; curve reproduced on all four sets", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
