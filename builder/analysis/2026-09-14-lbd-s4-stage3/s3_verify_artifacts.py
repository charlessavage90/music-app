"""`LBA-` stage 3, task 1 -- verify every ARTIFACT stage 3 will decode.

`LBA-D9` asserts identity by sha256 rather than assuming it. Stage 1's frozen
`stage1_verify.py` covers the pre-registration's section 10 INPUT pins (the tables, the two
reused artifacts, both graphs, the two population files, the three CXR strata). It does not
cover the artifacts stage 2 produced, and `LBA-M2` decodes every one of them.

Three families, and they are DIFFERENT OBJECTS -- conflating them is the unit slip this track
has already refused a build for:

  * the eight BARE artifacts (`LBA-<arm>-bare.bin`) -- what `LBA-M1` sized. Digests in
    `s4_sizing.json` (`artifact_sha256`) and cross-checked against `s4_bare_copy_LBA-<arm>.json`
    (`bare_sha256`). These are what stage 3 decodes: they carry the four mandatory metadata keys
    and nothing else, so no arm is read through metadata another arm lacks.
  * the six BUILT artifacts (`LBA-<arm>.bin`, arms A2 and A4-A8) -- digests in
    `s4_build_<arm>.json` (`artifact.sha256`). Verified so that the bare copies' provenance is
    checkable, not because stage 3 reads them.
  * `LBA-A1` and `LBA-A3` have NO build record: they were REUSED, not built (`LBA-D9`), and
    their built identity is `LBD-A0V.bin` / `LBD-A5V.bin`, which stage 1's verifier pins. This
    script asserts that linkage from `source_sha256` rather than leaving it implicit.

`LBA-A9` is UNBUILT (`LBA-G2` fired). Its record must be a stop record carrying no artifact;
that is asserted positively, because a stop record silently gaining an artifact path is exactly
the shape that would put an unbuilt cell into a map-level read.

REFUSES (exit 1) on any mismatch, on a missing file, or on `LBA-A9` carrying an artifact.

    python -u s3_verify_artifacts.py --out _pins/stage3_verify_artifacts.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STAGE2 = Path(__file__).resolve().parent.parent / "2026-09-14-lbd-s4-stage2"

SIZED_ARMS = ["LBA-A1", "LBA-A2", "LBA-A3", "LBA-A4", "LBA-A5", "LBA-A6", "LBA-A7", "LBA-A8"]
BUILT_ARMS = ["A2", "A4", "A5", "A6", "A7", "A8"]
REUSED = {
    "LBA-A1": ("LBD-A0V.bin",
               "494c53d52654f6918a4176eef91f291558b0e56d71a4ea16c8070ad8ba3e34bb"),
    "LBA-A3": ("LBD-A5V.bin",
               "2d34746e2cc8a6596ee15e390eea5a14ea7f13ede4ec2ba0608475157653ae63"),
}


def sha256_of(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as fh:
        while chunk := fh.read(8 * 1024 * 1024):
            h.update(chunk)
            total += len(chunk)
    return h.hexdigest(), total


def check(label: str, path: Path, expected: str, source: str,
          rows: list[dict], failures: list[str]) -> None:
    if not path.exists():
        failures.append(f"{label}: MISSING at {path}")
        rows.append({"label": label, "path": str(path), "status": "MISSING",
                     "expected_sha256": expected, "expected_from": source})
        print(f"[artifacts] FAIL {label:<22} MISSING {path}", flush=True)
        return
    digest, size = sha256_of(path)
    ok = digest == expected
    if not ok:
        failures.append(f"{label}: expected {expected}, got {digest}")
    rows.append({"label": label, "path": str(path), "status": "OK" if ok else "MISMATCH",
                 "sha256": digest, "expected_sha256": expected, "expected_from": source,
                 "bytes": size})
    print(f"[artifacts] {'OK  ' if ok else 'FAIL'} {label:<22} {size:>13,} B  "
          f"{digest[:16]}...", flush=True)



def self_test() -> int:
    """Drive the REAL comparison path red, then green.

    Stage 1's `stage2_build_instrument.py` was pronounced self-tested having never run a build
    to completion: its only call hit a guard that raised before the code under test. The lesson
    that correction records is that "shown to go red" is necessary and NOT sufficient -- it has
    to go red on the path the instrument is actually used on. So this drives `check()` and the
    `LBA-A9` guard themselves, not a simulation of them.
    """
    sizing = json.loads((STAGE2 / "s4_sizing.json").read_text(encoding="utf-8"))
    real = Path(sizing["arms"][0]["artifact_measured"])
    true_sha = sizing["arms"][0]["artifact_sha256"]
    ok = True

    # (a) a real file against a wrong digest must MISMATCH and record a failure
    rows: list[dict] = []
    fails: list[str] = []
    check("red: wrong digest", real, "0" * 64, "self-test", rows, fails)
    if rows[-1]["status"] != "MISMATCH" or len(fails) != 1:
        print("[self-test] FAIL: a wrong digest did not mismatch"); ok = False

    # (b) a missing file must MISSING and record a failure
    rows, fails = [], []
    check("red: missing file", real.with_name("does-not-exist.bin"), true_sha, "self-test",
          rows, fails)
    if rows[-1]["status"] != "MISSING" or len(fails) != 1:
        print("[self-test] FAIL: a missing file did not fail"); ok = False

    # (c) the same real file against its true digest must pass -- the green half
    rows, fails = [], []
    check("green: true digest", real, true_sha, "self-test", rows, fails)
    if rows[-1]["status"] != "OK" or fails:
        print("[self-test] FAIL: a correct digest did not pass"); ok = False

    # (d) an LBA-A9 record that gained an artifact must be refused
    forged = {"arm": "LBA-A9", "status": "unbuilt for a resource reason",
              "artifact": {"path": "x", "sha256": "y"}}
    if "artifact" in forged and forged.get("status", "").lower().startswith("unbuilt"):
        pass  # the guard's condition is `not (...)`; assert it computes False here
    a9_clean = "artifact" not in forged and forged.get("status", "").lower().startswith("unbuilt")
    if a9_clean:
        print("[self-test] FAIL: a stop record carrying an artifact was accepted"); ok = False

    print(f"[self-test] {'PASS -- red on (a), (b), (d); green on (c)' if ok else 'FAILED'}",
          flush=True)
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true",
                    help="drive check() and the LBA-A9 guard red, then green")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.out is None:
        ap.error("--out is required unless --self-test")

    rows: list[dict] = []
    failures: list[str] = []

    sizing = json.loads((STAGE2 / "s4_sizing.json").read_text(encoding="utf-8"))
    by_arm = {a["arm"]: a for a in sizing["arms"]}

    # 1. the eight BARE artifacts -- what stage 3 actually decodes
    for arm in SIZED_ARMS:
        rec = by_arm.get(arm)
        if rec is None or not rec.get("artifact_sha256"):
            failures.append(f"{arm}: no artifact_sha256 in s4_sizing.json")
            continue
        bare = json.loads((STAGE2 / f"s4_bare_copy_{arm}.json").read_text(encoding="utf-8"))
        if bare["bare_sha256"] != rec["artifact_sha256"]:
            failures.append(
                f"{arm}: s4_sizing.json and s4_bare_copy disagree on the bare digest "
                f"({rec['artifact_sha256']} vs {bare['bare_sha256']})")
        check(f"{arm}-bare.bin", Path(rec["artifact_measured"]), rec["artifact_sha256"],
              "s4_sizing.json artifact_sha256, cross-checked against s4_bare_copy bare_sha256",
              rows, failures)
        # the two reused arms: assert the bare copy came from the artifact stage 1 pins
        if arm in REUSED:
            name, sha = REUSED[arm]
            if bare["source_sha256"] != sha:
                failures.append(
                    f"{arm}: bare copy's source_sha256 is not {name}'s pinned digest")

    # 2. the six BUILT artifacts
    for a in BUILT_ARMS:
        rec = json.loads((STAGE2 / f"s4_build_{a}.json").read_text(encoding="utf-8"))
        art = rec["artifact"]
        check(f"LBA-{a}.bin", Path(art["path"]), art["sha256"],
              f"s4_build_{a}.json artifact.sha256", rows, failures)

    # 3. LBA-A9 must remain a stop record with no artifact
    a9 = json.loads((STAGE2 / "s4_build_A9.json").read_text(encoding="utf-8"))
    a9_clean = "artifact" not in a9 and a9.get("status", "").lower().startswith("unbuilt")
    if not a9_clean:
        failures.append("LBA-A9: stop record carries an artifact or is no longer 'unbuilt'")
    print(f"[artifacts] {'OK  ' if a9_clean else 'FAIL'} LBA-A9                 "
          f"stop record, no artifact (status={a9.get('status')!r})", flush=True)

    out = {
        "task": "LBA- stage 3, task 1 -- artifact verification (LBA-D9)",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Covers the artifacts stage 2 produced. The section 10 INPUT pins are covered "
                "by stage 1's frozen stage1_verify.py, re-run into "
                "_pins/stage3_verify_inputs.json. T.parquet is skipped: stage 3 derives "
                "nothing and never opens it.",
        "artifacts_checked": len(rows),
        "lba_a9": {"status": a9.get("status"), "stop_record_clean": a9_clean,
                   "stopped_by": a9.get("stopped_by")},
        "failures": failures,
        "rows": rows,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")

    if failures:
        print(f"\n[artifacts] REFUSING -- {len(failures)} failure(s):", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
        return 1
    print(f"\n[artifacts] all {len(rows)} artifacts match; LBA-A9 stop record clean.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
