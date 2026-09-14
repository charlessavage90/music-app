"""`LBA-` stage 1 -- derive the threshold-7 table, the one cell that does not already exist.

Thresholds 10 and 3 are already materialised and sha-verified (`A0.parquet`, `A5.parquet`);
threshold 7 is not. `LBA-D4`: every arm is a pure filter and window over `T`, and
`lbd_derive.py` is run UNEDITED.

"Unedited" is met the way `lbv_derive_a5.py` established it under `LBD-AM5-2`: this wrapper
IMPORTS `lbd_derive` and extends its `ARMS` table with the one new entry, so the SQL that runs
is `derive_sql`'s -- byte-identical to the SQL that derived `LBD-A0`..`LBD-A3` and `LBD-A5`.
Both script sha256s are recorded in the manifest.

NAMING: the entry is `T7`, never `A7`. `LBA-A7` is threshold 10 over the `U` population, and a
bare `A7` is already Track 2's. `CLAUDE.md`: no two load-bearing objects share an identifier.

Threshold 7 is the three-listener bar (s2.1): ceil((7+1)/3) = 3 distinct listeners, the only
quantity in which it is a middle value.

RUN ALONE: two DuckDB processes side by side on this machine ended in an access violation
(`2026-09-10-lbd-task67-execution-log.md`, Step 2).

    C:\\unsung-fast\\lbd-venv\\Scripts\\python.exe -u stage1_derive_t7.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIMILARITY = HERE.parent / "2026-09-08-lbd-similarity"
sys.path.insert(0, str(SIMILARITY))

import lbd_derive  # noqa: E402

T = Path(r"C:\unsung-fast\lbd-pairs\aggregate\T.parquet")
T_SHA = "03d47b05afd781d48ff6dab2784c9fbfcba30740e5d7e87b22e9aee2620aa08a"
OUT = Path(r"C:\unsung-fast\lbd-pairs\T7\T7.parquet")
THRESHOLD, LIMIT = 7, 100


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    # `T`'s identity was asserted by task 1; assert it again here so this script refuses on
    # its own rather than trusting an earlier step's output.
    print(f"[t7] verifying {T} ...", flush=True)
    got = sha256_of(T)
    if got != T_SHA:
        raise SystemExit(f"REFUSING: T.parquet is {got}, pinned {T_SHA}")
    print("[t7] T verified.", flush=True)

    if "T7" in lbd_derive.ARMS:
        raise SystemExit("REFUSING: lbd_derive.ARMS already defines T7; it must not.")
    lbd_derive.ARMS["T7"] = (THRESHOLD, LIMIT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    rc = lbd_derive.main(["--table", str(T), "--arm", "T7", "--out", str(OUT)])
    if rc != 0:
        return rc

    manifest = OUT.with_suffix(".manifest.json")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["wrapper"] = "stage1_derive_t7.py"
    data["wrapper_script_sha256"] = sha256_of(Path(__file__))
    data["arm_note"] = ("LBA- stage 1: the threshold-7 table. Feeds LBA-A2 (V), LBA-A5 (P) and "
                        "LBA-A8 (U). Named T7, never A7 -- LBA-A7 is threshold 10 over U.")
    data["distinct_listeners_required"] = -(-(THRESHOLD + 1) // 3)  # ceil((t+1)/contribution)
    manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[t7] manifest updated: {manifest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
