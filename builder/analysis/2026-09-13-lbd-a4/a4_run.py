"""`LBD-A4` — the pairing-delta arm. Driver only; every computation is a frozen script's.

`LBD-A4` differs from `LBD-A0` in ONE token: pairing. Pre-registration section 0's factor
table gives `days` 7500, `session` 300, `contribution` 3, `threshold` 10, `limit` 100,
pairing **distinct**, isolating baseline `LBD-A0` -- "pairing only".

WHY THIS IS A DRIVER AND NOT A NEW IMPLEMENTATION. `--pairing distinct` is already in
`../2026-09-08-lbd-similarity/lbd_similarity.py` as `T3-D7`, and its fixture asserts it in
BOTH the naive and the algebraic form against hand-derived expected values. Nothing about
the computation is new here, and nothing in this file computes anything: it invokes that
script once per user bucket, combines, and derives, in the same three stages and with the
same flags the `LBD-A0` pass used. Its own record is the per-stage manifests those scripts
write, not anything this file prints.

THE ONE TOKEN, AND HOW THE PASS KEEPS IT TO ONE.

  same stage 0        `C:\\unsung-fast\\lbd-listens.parquet`, sha256 `6d77a681...07707c08`,
                      the SAME file `LBD-A0`'s buckets read. Stage 0 is pre-pairing --
                      `lbd_similarity.py`'s own comment at the three-path dispatch says
                      "NOTHING before this point differs between any of the five arms" --
                      so reusing it is exactness, not thrift. Its manifest records
                      `"pairing": "listen"` because that was the invocation's parameter
                      string; the stage does not branch on it.
  same side-tables    `D:\\unsung-large-data\\lbd-inputs`, redirects applied, and unread on
                      this path anyway: `register_frames` is skipped under `--from-listens`.
  chunking, and it   `user_id % 128` at an 8 GB limit, where `LBD-A0`'s pass used 64 at 12
  is NOT "same"       GB. the PRE-REGISTRATION'S section 1 establishes -- read off LB's own
                      SQL -- that chunking by `user_id` is EXACT at ANY modulus (this is
                      `LBD-D2`'s chunked form; `LBD-D2` itself is the decision to run on
                      DuckDB here, and names chunking only as the fallback) -- every stage through `user_contribtion_mbids` partitions by
                      user, and only the final cross-user SUM crosses a boundary, which
                      `combine_sql` re-sums once. So this is a RESOURCE setting and not a
                      token of the arm: it cannot move a figure, only the wall clock and the
                      memory. Set from a measurement on this machine (README section 4), not
                      inherited: 12 GB of 31.7 GB was killed under system memory pressure
                      with other work live, and mod 128 at 8 GB peaks at 7.64 GB.
  same derivation     `lbd_derive.py`'s `A0` row IS `(threshold 10, limit 100)`, which is
                      `LBD-A4`'s pair. See `--stage derive` below for why that is the right
                      call and what it costs in the manifest.

SCRIPT SHA, AND THE ONE DIFFERENCE FROM `LBD-A0`'S PASS THAT IS NOT PAIRING. `LBD-A0`'s
partials carry `script_sha256` `40f9ee03...` (commit `1cb49c6`); this pass carries
`eeb3c87b...` (commit `dda02a9`). The whole diff between them is the `--created-before`
diagnostic knob added for the `LBD-G1` diagnosis, and it lives entirely inside
`register_listens` -- which is stage 0, and which `--from-listens` does not call at all.
So the difference is inert on this path by construction, not by inspection alone. Recorded
because a reader comparing two manifests will see two shas and is owed the reason.

RESUMABLE. A bucket whose manifest already exists is skipped, so an interrupted pass
restarts where it stopped. Delete a manifest to force its bucket to re-run.

    cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u analysis/2026-09-13-lbd-a4/a4_run.py --stage buckets
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIMILARITY = HERE.parent / "2026-09-08-lbd-similarity" / "lbd_similarity.py"
DERIVE = HERE.parent / "2026-09-08-lbd-similarity" / "lbd_derive.py"

LISTENS = Path(r"C:\unsung-fast\lbd-listens.parquet")
PARTIALS = Path(r"C:\unsung-fast\lbd-partials-a4")
PAIRS = Path(r"C:\unsung-fast\lbd-pairs-a4")
TEMP = Path(r"C:\unsung-fast\duckdb-temp")

# Chunking is a RESOURCE decision, not a measurement one: the pre-registration's section 1
# establishes, from LB's own SQL, that chunking by `user_id` is EXACT at any modulus, because
# every stage through `user_contribtion_mbids` partitions by user and only the final cross-user
# SUM crosses a boundary. (`LBD-D2` is the decision to run on DuckDB and names chunking as the
# fallback; the exactness proof is the pre-registration's, not that decision's.) So these two are
# free to be whatever this machine can actually sustain, and they are set from a measurement
# on this machine rather than from the `LBD-A0` pass's settings -- see the README's section 4.
BUCKETS = 128
MEMORY_GB = 8

# Pre-registration section 0, the `LBD-A4` row. Every one of these except `pairing` is
# `LBD-A0`'s value.
ARM = ["--days", "7500", "--session", "300", "--contribution", "3",
       "--threshold", "10", "--limit", "100", "--skip", "30",
       "--pairing", "distinct"]


def run(args: list[str], *, label: str, check: bool = True) -> float | None:
    t0 = time.time()
    print(f"[a4] >>> {label}", flush=True)
    proc = subprocess.run([sys.executable, "-u", *args], text=True)
    wall = time.time() - t0
    if proc.returncode != 0:
        if not check:
            print(f"[a4] !!! {label} exit {proc.returncode} after {wall/60:.1f} min", flush=True)
            return None
        raise SystemExit(f"[a4] FAILED {label} (exit {proc.returncode}) after {wall/60:.1f} min")
    print(f"[a4] <<< {label}  {wall/60:.1f} min", flush=True)
    return wall


def _bucket(mod: int, rem: int, out: Path, *, memory_gb: int, check: bool) -> float | None:
    return run([str(SIMILARITY), "--from-listens", str(LISTENS), "--emit-partial",
                "--user-mod", str(mod), "--user-rem", str(rem),
                "--memory-limit-gb", str(memory_gb), "--temp-dir", str(TEMP),
                "--row-group-size", "100000", "--out", str(out), *ARM],
               label=f"bucket mod {mod} rem {rem}", check=check)


def stage_buckets(*, mod: int = BUCKETS, memory_gb: int = MEMORY_GB) -> None:
    """One partial per user bucket, resumably.

    THE SPLIT FALLBACK. A bucket that dies -- DuckDB's own OOM, or the harness killing it
    under system memory pressure, which is what ended the first attempt -- is re-run as four
    sub-buckets at `mod * 4`. That is exact for the same reason the chunking is: the four
    sub-buckets partition the parent's users and nothing but the final cross-user SUM crosses
    a boundary. `LBD-A0`'s own loop carried the same fallback and never fired it.
    """
    PARTIALS.mkdir(parents=True, exist_ok=True)
    done = skipped = split = 0
    t0 = time.time()
    for rem in range(mod):
        out = PARTIALS / f"p{rem}.parquet"
        if out.with_suffix(".manifest.json").exists():
            skipped += 1
            continue
        if _bucket(mod, rem, out, memory_gb=memory_gb, check=False) is not None:
            done += 1
            continue
        print(f"[a4] splitting bucket {rem} into 4 at mod {mod * 4}", flush=True)
        for k in range(4):
            sub_rem = rem + k * mod
            sub = PARTIALS / f"p{rem}s{k}.parquet"
            if sub.with_suffix(".manifest.json").exists():
                continue
            _bucket(mod * 4, sub_rem, sub, memory_gb=memory_gb, check=True)
        split += 1
    print(f"[a4] buckets: {done} run, {skipped} already present, {split} split, "
          f"{(time.time() - t0)/60:.1f} min", flush=True)


def stage_combine(memory_gb: int = MEMORY_GB) -> None:
    """`T_A4` -- the cross-user re-sum at `HAVING score > 0`, no rank cut.

    Exactly `LBD-A0`'s route: the pre-registration's section 1 materialises the aggregate at
    the lowest threshold any arm uses and derives the arm from it, so the threshold and the
    rank cut are applied once, in one place, by the same code that applied them for `A0`.
    """
    out = PAIRS / "aggregate" / "T_A4.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    run([str(SIMILARITY), "--combine", (PARTIALS / "p*.parquet").as_posix(),
         "--aggregate-only", "--memory-limit-gb", str(memory_gb),
         "--temp-dir", str(TEMP), "--out", str(out), *ARM],
        label="combine -> T_A4")


def stage_derive() -> None:
    """`LBD-A4` = `T_A4` filtered `score > 10`, ranked per `mbid0`, `rank <= 100`.

    `lbd_derive.py --arm A0` IS that pair of tokens -- its `ARMS` table reads
    `"A0": (10, 100)` -- so this invokes the frozen derivation rather than adding an `A4`
    row to a frozen script. The cost is that `A4.manifest.json` records `"arm": "A0"`. That
    field names the (threshold, limit) row, and `derived_from` names `T_A4.parquet` with its
    sha256, which is what identifies the arm. Not an error, and not to be "fixed": editing
    the frozen script to relabel it would change the script that produced `LBD-A0`'s own
    numbers.
    """
    out = PAIRS / "A4" / "A4.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    run([str(DERIVE), "--table", str(PAIRS / "aggregate" / "T_A4.parquet"),
         "--arm", "A0", "--out", str(out),
         "--memory-limit-gb", "24", "--temp-dir", str(TEMP)],
        label="derive -> A4")


def stage_summary() -> None:
    """Collect the per-bucket manifests into one record. Reads, never recomputes.

    COVERAGE IS CHECKED, NOT ASSUMED. Every partial's manifest carries its own
    `(user_mod, user_rem)`, and the set of them must cover every user exactly once or the
    combine silently under- or double-counts. `residues_cover_all_users` is that check,
    expanded to the finest modulus present.
    """
    rows = [json.loads(mf.read_text(encoding="utf-8"))
            for mf in sorted(PARTIALS.glob("p*.manifest.json"))]
    if not rows:
        print("[a4] no bucket manifests yet", flush=True)
        return
    finest = max(r["user_mod"] for r in rows)
    covered: list[int] = []
    for r in rows:
        step = finest // r["user_mod"]
        covered.extend(r["user_rem"] + i * r["user_mod"] for i in range(step))
    print(json.dumps({
        "buckets_present": len(rows),
        "finest_modulus": finest,
        "residues_cover_all_users": sorted(covered) == list(range(finest)),
        "residues_duplicated": len(covered) != len(set(covered)),
        "partial_rows_total": sum(r["rows"] for r in rows),
        "wall_clock_s_summed": round(sum(r["wall_clock_s"] for r in rows), 1),
        "peak_rss_gb_max": max(r["peak_rss_gb"] for r in rows),
        "peak_spill_gb_summed": round(sum(r["peak_spill_gb"] for r in rows), 1),
        "peak_spill_gb_max": max(r["peak_spill_gb"] for r in rows),
        "script_sha256": sorted({r["script_sha256"] for r in rows}),
        "pairing": sorted({r["params"]["pairing"] for r in rows}),
        "from_listens": sorted({r["from_listens"] for r in rows}),
    }, indent=2), flush=True)


STAGES = {"buckets": stage_buckets, "combine": stage_combine,
          "derive": stage_derive, "summary": stage_summary}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--memory-gb", type=int, default=None,
                    help="override the per-stage DuckDB limit; a resource knob, never a token")
    args = ap.parse_args(argv)
    fn = STAGES[args.stage]
    if args.memory_gb and fn in (stage_buckets, stage_combine):
        fn(memory_gb=args.memory_gb)
    else:
        fn()
    return 0


if __name__ == "__main__":
    sys.exit(main())
