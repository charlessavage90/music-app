"""`LBD-AM5-1` — emit `LBD-A0` or `LBD-A5` over the SERVED population `V`, through the Task 6
emitter UNEDITED.

`../2026-09-10-lbd-supply/emit_archive.py` is frozen research code whose population is a module
constant (`CXA`) and whose arm table is `ARM_TOKENS`. This wrapper verifies the emitter is the
committed file (sha256 prefix recorded in the supply README), repoints those two constants and the
population file at `V`, and calls its `main` — so the filter, the sort, the payload shape and the
determinism are the emitter's own, and "the same emitter" is a checked statement. The one field the
emitter hard-codes that would now be false — its `amendment` string — is rewritten in the manifest
afterwards, beside the map token `LBD-A0V` / `LBD-A5V`; payload bytes are untouched.

RUN ALONE (DuckDB; see the task 6–7 log's access-violation trap).

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run --with duckdb python -u analysis/2026-09-10-lbd-served-population/lbv_emit.py --arm A0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUPPLY = HERE.parent / "2026-09-10-lbd-supply"
sys.path.insert(0, str(SUPPLY))

import emit_archive  # noqa: E402

SERVED = Path(r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin")
PAIRS = {"A0": Path(r"C:\unsung-fast\lbd-pairs\A0\A0.parquet"), "A5": Path(r"C:\unsung-fast\lbd-pairs\A5\A5.parquet")}
TOKENS = {"A0": {"threshold": 10, "limit": 100}, "A5": {"threshold": 3, "limit": 100}}
MAP_TOKEN = {"A0": "LBD-A0V", "A5": "LBD-A5V"}
EMITTER_SHA_PREFIX = "484f9415"   # builder/analysis/2026-09-10-lbd-supply/README.md, "Scripts"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(TOKENS))
    ap.add_argument("--memory-limit-gb", type=int, default=8)
    args = ap.parse_args(argv)

    emitter_sha = sha256_of(Path(emit_archive.__file__))
    if not emitter_sha.startswith(EMITTER_SHA_PREFIX):
        raise SystemExit(f"REFUSING: emit_archive.py sha256 {emitter_sha} is not the committed Task 6 emitter")

    emit_archive.CXA = SERVED
    emit_archive.POPULATION_FILE = emit_archive.ARCHIVES / "population_msw_mbids.txt"
    emit_archive.ARM_TOKENS = dict(TOKENS)
    out = emit_archive.ARCHIVES / MAP_TOKEN[args.arm].removeprefix("LBD-")
    rc = emit_archive.main(["--arm", args.arm, "--pairs", str(PAIRS[args.arm]), "--out", str(out),
                            "--memory-limit-gb", str(args.memory_limit_gb)])
    if rc:
        return rc

    manifest_path = out / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["population"]["artifact"] != SERVED.name:
        raise SystemExit("BUG: the emitter did not read the served population")
    manifest["amendment"] = "LBD-AM5-1 — population V = graph-msw-tu50.bin's node set; filter after the derived cut, never re-ranked"
    manifest["map_token"] = MAP_TOKEN[args.arm]
    manifest["wrapper_script_sha256"] = sha256_of(Path(__file__))
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[lbv-emit] {MAP_TOKEN[args.arm]}: manifest rewritten with its amendment and map token", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
