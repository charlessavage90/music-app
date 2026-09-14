"""`LBA-` stage 2, step 2 — emit each unbuilt cell as an archive the SHIPPED builder can read,
through the Task 6 emitter UNEDITED.

`../2026-09-10-lbd-supply/emit_archive.py` is frozen research code whose population is a module
constant (`CXA`) and whose arm table is `ARM_TOKENS`. `../2026-09-10-lbd-served-population/lbv_emit.py`
established the pattern this file follows: verify the emitter is the committed file, repoint those
constants, call its `main`, then rewrite the manifest's `amendment` line beside the arm token.
Payload bytes are the emitter's own and are never touched.

THREE POPULATION RULES (`LBA-` pre-registration §2.1), and the third is what this wrapper adds
over `lbv_emit.py`:

  `V` — the node set of `graph-msw-tu50.bin`, from the pinned `population_msw_mbids.txt`
  `P` — the node set of `graph-cxa-adopted.bin`, from the pinned `population_cxa_mbids.txt`
  `U` — every artist the ARM'S OWN derived table names as `mbid0` or `mbid1`. There is no
        artifact to read it from, so `verified_population` itself is repointed, and the derived
        population is written to its own file and sha-recorded. `LBA-X6`: `U`'s membership moves
        with the threshold, which is the rule's substance and not a defect.

The un-listenable filter is NOT applied here — it is a build-time knob (`LBA-D7`), and this
script only emits. `s4_build.py` sets it per population rule and records the state per arm.

WARNING — the pinned population files are REWRITTEN by the emitter's `main` (it writes
`POPULATION_FILE` from the artifact it read). Each arm therefore gets its own `POPULATION_FILE`,
and for `V` and `P` the file written is checked against the digest stage 1 verified, so a
re-emission that disagreed with the pinned population refuses rather than silently redefining it.

WARNING — each cell emits into its OWN directory, `S4-<arm>`. The supply and served-population
work's archives (`A0`, `A2`, `A0V`, `A5V`) are a frozen record and are never written into.
`S4-A4` is deliberately a re-emission of what `A0` already holds: reproducing that archive's three
committed counts exactly is this wrapper's green check, taken before it is used on any novel cell.

RUN ALONE (DuckDB; see the task 6-7 log's access-violation trap). One arm per invocation.

    cd C:/dev/music-app/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy
      uv run --with duckdb python -u analysis/2026-09-14-lbd-s4-stage2/s4_emit.py --arm A4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUPPLY = HERE.parent / "2026-09-10-lbd-supply"
sys.path.insert(0, str(SUPPLY))

import duckdb  # noqa: E402

import emit_archive  # noqa: E402  (frozen; repointed, never edited)

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
ARCHIVES = Path(r"C:\unsung-fast\lbd-archives")
PAIRS = Path(r"C:\unsung-fast\lbd-pairs")

# The emitter this wrapper calls. Its sha is checked before anything is repointed: "the same
# emitter" is a checked statement, exactly as `lbv_emit.py` made it one.
EMITTER_SHA_PREFIX = "484f9415"

# The three derived tables, one per strength bar. Their digests are the pre-registration's §10
# pins, re-verified by this session's own run of `stage1_verify.py`.
TABLES = {
    10: {"token": "A0", "path": PAIRS / "A0" / "A0.parquet",
         "sha256": "f9bd1f835076f22f1b1da444e1aff92dc2ef8f34667a579c82a0848e7fe4821e"},
    7: {"token": "T7", "path": PAIRS / "T7" / "T7.parquet",
        "sha256": "252b88d9e2f8e304e035a0befd709ad87c2753d2af4675a0139e71b076520c6c"},
    3: {"token": "A5", "path": PAIRS / "A5" / "A5.parquet",
        "sha256": "f34cd88957d3ab42b000fb33d23ae7f9aad1dbdb72d2d0b1cab5d34f024a19ff"},
}

# The two pinned populations, with the digests stage 1 verified in full (the record carried only
# 8-character prefixes before that).
POPULATIONS = {
    "V": {"artifact": SCRATCH / "graph-msw-tu50.bin",
          "file": ARCHIVES / "population_msw_mbids.txt",
          "file_sha256": "b5e0cb9436208341aa892e68de2e82d0cc0566d2462dec8d0a7502d1baee1836",
          "artifact_sha256": "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8",
          "count": 58838},
    "P": {"artifact": SCRATCH / "graph-cxa-adopted.bin",
          "file": ARCHIVES / "population_cxa_mbids.txt",
          "file_sha256": "1bbff8fcfde78a07d276f727ccaf048c73da4bfd27709b64f6f6894d6d4d2d7b",
          "artifact_sha256": "bc0431c4b55a2137e945b280270de7e7dc700e3dcf60f3656f6f97598e7ece46",
          "count": 88685},
}

# §2.1's lattice, the seven cells stage 2 emits. `LBA-A1` and `LBA-A3` are reused and absent by
# design (`LBA-D9`); rebuilding them would add a build-date column the factor table does not have.
# `expect` is stage 1's own count for the cell, from that stage's figures owner — an instrument
# check, never a criterion: the emitter must reproduce it or this wrapper refuses.
ARMS = {
    "A2": {"threshold": 7, "rule": "V", "expect": {"payloads": 57852, "rows": 8936730, "absent": 986}},
    "A4": {"threshold": 10, "rule": "P", "expect": {"payloads": 86854, "rows": 11274938, "absent": 1831}},
    "A5": {"threshold": 7, "rule": "P", "expect": {"payloads": 87227, "rows": 12523016, "absent": 1458}},
    "A6": {"threshold": 3, "rule": "P", "expect": {"payloads": 87764, "rows": 14793382, "absent": 921}},
    "A7": {"threshold": 10, "rule": "U", "expect": {"payloads": 366996, "rows": 22681278, "absent": 0}},
    "A8": {"threshold": 7, "rule": "U", "expect": {"payloads": 456469, "rows": 29308892, "absent": 0}},
    "A9": {"threshold": 3, "rule": "U", "expect": {"payloads": 679232, "rows": 52254182, "absent": 0}},
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def u_population(pairs: Path, out_file: Path, memory_limit_gb: int) -> list[str]:
    """`U` — every artist the arm's own table names, by the query stage 1 counted with."""
    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{memory_limit_gb}GB'")
    con.execute("PRAGMA temp_directory='C:/unsung-fast/duckdb-temp'")
    p = pairs.as_posix()
    rows = con.execute(f"""
        SELECT m FROM (SELECT mbid0 AS m FROM read_parquet('{p}')
                       UNION SELECT mbid1 FROM read_parquet('{p}'))
        ORDER BY m
    """).fetchall()
    con.close()
    mbids = [r[0] for r in rows]
    out_file.write_text("\n".join(mbids) + "\n", encoding="utf-8")
    return mbids


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--memory-limit-gb", type=int, default=8)
    args = ap.parse_args(argv)
    spec = ARMS[args.arm]
    rule = spec["rule"]
    table = TABLES[spec["threshold"]]
    started = time.monotonic()

    emitter_sha = sha256_of(Path(emit_archive.__file__))
    if not emitter_sha.startswith(EMITTER_SHA_PREFIX):
        raise SystemExit(f"REFUSING: emit_archive.py sha256 {emitter_sha} is not the committed Task 6 emitter")
    pairs_sha = sha256_of(table["path"])
    if pairs_sha != table["sha256"]:
        raise SystemExit(f"REFUSING: {table['path'].name} sha256 {pairs_sha} != the pinned {table['sha256']}")
    print(f"[s4-emit] LBA-{args.arm}: threshold {spec['threshold']}  rule {rule}  "
          f"table {table['token']} sha256 {pairs_sha[:16]}...", flush=True)

    out = ARCHIVES / f"S4-{args.arm}"
    if (out / "MANIFEST.json").exists():
        raise SystemExit(f"REFUSING: {out} already holds a MANIFEST.json — emit writes a fresh archive")

    # --- repoint the frozen emitter's two population constants --------------------------------
    emit_archive.ARM_TOKENS = {table["token"]: {"threshold": spec["threshold"], "limit": 100}}
    if rule == "U":
        pop_file = ARCHIVES / f"population_u_{args.arm}_mbids.txt"
        mbids = u_population(table["path"], pop_file, args.memory_limit_gb)
        pop_sha = sha256_of(pop_file)
        print(f"[s4-emit] U({spec['threshold']}) derived from the arm's own table: {len(mbids):,} artists  "
              f"file sha256 {pop_sha}", flush=True)
        emit_archive.CXA = pop_file
        emit_archive.POPULATION_FILE = pop_file
        emit_archive.verified_population = lambda: (mbids, pop_sha)
        population_expected = len(mbids)
    else:
        pin = POPULATIONS[rule]
        emit_archive.CXA = pin["artifact"]
        emit_archive.POPULATION_FILE = pin["file"]
        population_expected = pin["count"]

    rc = emit_archive.main(["--arm", table["token"], "--pairs", str(table["path"]),
                            "--out", str(out), "--memory-limit-gb", str(args.memory_limit_gb)])
    if rc:
        return rc

    # --- the pinned population files must come back out unchanged -----------------------------
    if rule in POPULATIONS:
        pin = POPULATIONS[rule]
        rewritten = sha256_of(pin["file"])
        if rewritten != pin["file_sha256"]:
            raise SystemExit(f"REFUSING: the emitter rewrote {pin['file'].name} to sha256 {rewritten}, "
                             f"not the pinned {pin['file_sha256']} — the population has been redefined")
        print(f"[s4-emit] pinned {pin['file'].name} unchanged after the emit ({rewritten[:16]}...)", flush=True)

    manifest_path = out / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    counts = manifest["counts"]

    # --- the instrument check: stage 1 predicted every one of these ---------------------------
    got = {"payloads": counts["payloads_written"], "rows": counts["neighbour_rows_written"],
           "absent": counts["P_absent_from_arm"]}
    if got != spec["expect"]:
        raise SystemExit(f"REFUSING: LBA-{args.arm} emitted {got}, stage 1 counted {spec['expect']} — "
                         f"one of the two is wrong and neither may be used until it is known which")
    if manifest["population"]["count"] != population_expected:
        raise SystemExit(f"REFUSING: population count {manifest['population']['count']} != {population_expected}")
    if rule == "U" and (counts["arm_rows_one_end_in_P"] or counts["arm_rows_neither_in_P"]):
        raise SystemExit("REFUSING: a U population must contain BOTH endpoints of every row of its own table")

    manifest["amendment"] = ("LBA- stage 2 — population rule "
                             f"{rule}; the arm's derived cut, filtered to the population and never re-ranked")
    manifest["lba_arm"] = f"LBA-{args.arm}"
    manifest["population_rule"] = rule
    manifest["population_rule_note"] = {
        "V": "the node set of graph-msw-tu50.bin, the served map (pinned file)",
        "P": "the node set of graph-cxa-adopted.bin, the extended crawl (pinned file)",
        "U": "every artist the arm's OWN derived table names as mbid0 or mbid1 — LBA-X6: "
             "U's membership moves with the threshold, so a U-row threshold comparison has the "
             "population as a DEPENDENT variable",
    }[rule]
    manifest["stage1_counts_reproduced"] = spec["expect"]
    manifest["wrapper_script_sha256"] = sha256_of(Path(__file__))
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[s4-emit] LBA-{args.arm}: payloads {got['payloads']:,}  neighbour rows {got['rows']:,}  "
          f"absent {got['absent']:,}  — all three reproduce stage 1  "
          f"({(time.monotonic() - started) / 60:.1f} min)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
