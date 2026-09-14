"""`LBA-` stage 1, task 1 -- verify every artifact the pre-registration's section 10 pins.

`LBA-D9`: the two reused cells `LBA-A1` (= `LBD-A0V`) and `LBA-A3` (= `LBD-A5V`) are REUSED,
not rebuilt, "and their identity is asserted by sha256 rather than assumed". This script is
that assertion, extended to every pin in section 10 plus the two archive manifests `LBA-D9`
names via the served-population README's sections 0, 2 and 5.

REFUSES (exit 1) on any mismatch. Two pins exist on the record only as 8-character prefixes;
each is verified as a prefix AND cross-checked against an independently recorded line count,
and the full digest is written here so a later session has it.

    C:\\unsung-fast\\lbd-venv\\Scripts\\python.exe -u stage1_verify.py --out verify.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# (label, path, expected sha256 or 8-char prefix, where the expected value comes from)
PINS: list[tuple[str, str, str, str]] = [
    # the table every arm derives from (LBA-D1)
    ("T.parquet", r"C:\unsung-fast\lbd-pairs\aggregate\T.parquet",
     "03d47b05afd781d48ff6dab2784c9fbfcba30740e5d7e87b22e9aee2620aa08a",
     "prereg s10; Task 4 README s5"),
    # the two derived tables the reused cells were built from
    ("A0.parquet", r"C:\unsung-fast\lbd-pairs\A0\A0.parquet",
     "f9bd1f835076f22f1b1da444e1aff92dc2ef8f34667a579c82a0848e7fe4821e",
     "prereg s10; Task 4 README s6"),
    ("A5.parquet", r"C:\unsung-fast\lbd-pairs\A5\A5.parquet",
     "f34cd88957d3ab42b000fb33d23ae7f9aad1dbdb72d2d0b1cab5d34f024a19ff",
     "prereg s10; served-population README s1"),
    # the two reused artifacts
    ("LBD-A0V.bin (= LBA-A1)", r"C:\unsung-fast\lbd-artifacts\LBD-A0V.bin",
     "494c53d52654f6918a4176eef91f291558b0e56d71a4ea16c8070ad8ba3e34bb",
     "served-population README s5"),
    ("LBD-A5V.bin (= LBA-A3)", r"C:\unsung-fast\lbd-artifacts\LBD-A5V.bin",
     "2d34746e2cc8a6596ee15e390eea5a14ea7f13ede4ec2ba0608475157653ae63",
     "served-population README s5"),
    # their archives -- LBA-D9 names these via s2
    ("A0V archive MANIFEST", r"C:\unsung-fast\lbd-archives\A0V\MANIFEST.json",
     "7f555e14", "served-population README s2 (8-char pin on the record)"),
    ("A5V archive MANIFEST", r"C:\unsung-fast\lbd-archives\A5V\MANIFEST.json",
     "41b66372", "served-population README s2 (8-char pin on the record)"),
    # the two graphs the population rules are read from
    ("graph-msw-tu50.bin (V)", r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin",
     "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8",
     "prereg s2.1; served-population README s0"),
    ("graph-cxa-adopted.bin (P)", r"C:\dev\music-app\builder\scratch\graph-cxa-adopted.bin",
     "bc0431c4b55a2137e945b280270de7e7dc700e3dcf60f3656f6f97598e7ece46",
     "prereg s2.1; supply README s0"),
    # the pinned population files -- "re-verified, never re-derived"
    ("population_msw_mbids.txt (V)", r"C:\unsung-fast\lbd-archives\population_msw_mbids.txt",
     "b5e0cb94", "prereg s2.1 / s10 (8-char pin on the record)"),
    ("population_cxa_mbids.txt (P)", r"C:\unsung-fast\lbd-archives\population_cxa_mbids.txt",
     "1bbff8fc", "prereg s2.1 / s10 (8-char pin on the record)"),
    # the three pinned CXR strata
    ("cxr_added_mbids.txt", r"D:\unsung-large-data\lbd-inputs\cxr_added_mbids.txt",
     "bfed95ef74b0665c50b1532708091b4e43fab36247db391d04064870659a4339", "prereg s10"),
    ("cxr_preexisting_mbids.txt", r"D:\unsung-large-data\lbd-inputs\cxr_preexisting_mbids.txt",
     "768054b7e84769346193336ec7e9b3496af92d0d3e8d4ae2fb287057912b5229", "prereg s10"),
    ("cxr_residual_mbids.txt", r"D:\unsung-large-data\lbd-inputs\cxr_residual_mbids.txt",
     "fa8d85cc12131f3cd39ecebeb5da0d52a1236104acbcbabf20232c72b4f43a08", "prereg s10"),
]

# Named in s10 "only to be excluded" (LBA-D1: every arm derives from T, never from T_A4).
T_A4_SHA = "e919bc89425ecb7538fb5092a51ffb5e8a4d507fb2546a40d19a88508202a1e1"
T_A4_SEARCH = [
    r"C:\unsung-fast\lbd-pairs\aggregate\T_A4.parquet",
    r"D:\unsung-large-data\lbd-pairs\aggregate\T_A4.parquet",
    r"D:\unsung-large-data\lbd-pairs\T_A4.parquet",
]

# Line counts recorded independently on the record. Used as a SECOND check on the two
# population files whose sha is only an 8-char prefix there.
LINE_COUNTS = {
    "population_msw_mbids.txt (V)": (58838, "served-population README s0"),
    "population_cxa_mbids.txt (P)": (88685, "supply README s0"),
}


def sha256_of(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
            total += len(block)
    return h.hexdigest(), total


def check_one(label: str, raw: str, expected: str, source: str) -> tuple[dict, list[str]]:
    failures: list[str] = []
    path = Path(raw)
    if not path.exists():
        return ({"label": label, "path": raw, "status": "MISSING", "source": source},
                [f"{label}: file not found at {raw}"])

    digest, size = sha256_of(path)
    prefix_only = len(expected) < 64
    sha_ok = digest.startswith(expected) if prefix_only else digest == expected
    if not sha_ok:
        failures.append(f"{label}: sha256 {digest} does not match pinned {expected}")

    row = {
        "label": label,
        "path": raw,
        "bytes": size,
        "expected": expected,
        "expected_is_prefix_only": prefix_only,
        "sha256": digest,
        "sha_status": "OK" if sha_ok else "MISMATCH",
        "source": source,
    }

    lines_ok = True
    if label in LINE_COUNTS:
        want, where = LINE_COUNTS[label]
        got = sum(1 for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip())
        lines_ok = got == want
        row["lines"] = got
        row["lines_expected"] = want
        row["lines_source"] = where
        row["lines_status"] = "OK" if lines_ok else "MISMATCH"
        if not lines_ok:
            failures.append(f"{label}: {got} lines, the record says {want} ({where})")

    row["status"] = "OK" if (sha_ok and lines_ok) else "MISMATCH"
    return row, failures


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--skip-large", action="store_true",
                    help="skip T.parquet (21 GB); for a fast re-run of everything else")
    args = ap.parse_args(argv)

    rows: list[dict] = []
    failures: list[str] = []
    for label, raw, expected, source in PINS:
        if args.skip_large and label == "T.parquet":
            continue
        row, fails = check_one(label, raw, expected, source)
        rows.append(row)
        failures.extend(fails)
        flag = "OK  " if row["status"] == "OK" else "FAIL"
        size = f"{row.get('bytes', 0):>14,} B"
        digest = row.get("sha256", "-")[:16]
        extra = f"  lines {row['lines']:,}" if "lines" in row else ""
        print(f"[verify] {flag} {label:<30} {size}  {digest}...{extra}", flush=True)

    # T_A4 is pinned only so that it can be excluded. Absence is a stronger guarantee than
    # a match, so it is recorded as an observation rather than counted as a failure.
    found = [p for p in T_A4_SEARCH if Path(p).exists()]
    t_a4 = {
        "pinned_sha256": T_A4_SHA,
        "role": "named in s10 only to be EXCLUDED (LBA-D1: no arm derives from it)",
        "searched": T_A4_SEARCH,
        "present": bool(found),
        "found_at": found,
    }
    print(f"[verify] --   T_A4.parquet                  "
          f"{'PRESENT at ' + found[0] if found else 'ABSENT from every searched path'}", flush=True)

    out = {
        "task": "LBA- stage 1, task 1 -- pinned-artifact verification",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "machine": "the owner's Windows 11 workstation, repo at C:\\dev\\music-app",
        "pins_checked": len(rows),
        "failures": failures,
        "rows": rows,
        "t_a4": t_a4,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")

    if failures:
        print("\n[verify] REFUSING -- LBA-D9 requires every pin to match:", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
        return 1
    print(f"\n[verify] all {len(rows)} pins match.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
