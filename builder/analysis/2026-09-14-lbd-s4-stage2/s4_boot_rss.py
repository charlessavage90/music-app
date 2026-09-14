"""`LBA-M1` — boot memory: peak RSS of a process that loads ONE artifact through the shipped
`GraphStore` and nothing else.

ONE LOAD PER PROCESS, for the same reason `instrumented_build` refuses a second call:
`PeakWorkingSetSize` is a whole-process high-water mark and never falls, so a second load in one
process would read the first one's peak. The caller runs this script once per repeat.

It serves BOTH calibration and measurement, which is why it is its own script:

  * `metadata_ratio` (`LBA-M1`'s calibration block) — median peak of a `GraphStore`-only load of
    `graph-lux4.bin` divided by the same for `graph-msw-tu50.bin`. The two are IDENTICAL in artist
    count and in CSR entries and differ only in the three `LUX-4` additive keys, so the ratio
    isolates the metadata term. It must be MEASURED and not assumed: the same pair differs by
    1.336x in serialised bytes, and resident cost does not track bytes, because `GraphStore` holds
    those keys as Python `list[str]` and `list[dict]` while the CSR arrays stay as numpy.
  * each arm's boot memory, three repeats, median reported, then scaled to the shipped artifact by
    that ratio. §4: "the raw census figure is never compared with `LBA-G1`(a)'s bar directly."

⚠ `LBA-G1`(a)'s multiplicand is THIS peak — a `GraphStore` LOAD — and NOT `LBA-G2`'s BUILD peak.
Two different peaks with similar names. `metadata_ratio` is itself a ratio of `GraphStore`-only
loads, which is what settles it.

    uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_boot_rss.py \
      --artifact C:/unsung-fast/lbd-artifacts/LBA-A2.bin --label LBA-A2 --repeat 1 --out <json>
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))
sys.path.insert(0, str(HERE.parent / "2026-09-14-lbd-s4-stage1"))

from stage2_build_instrument import peak_working_set, working_set  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--repeat", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    # The api package is imported BEFORE the baseline is taken, so the figure is the STORE's
    # contribution and not the store plus the import cost of `graph_store` itself. The stage-1
    # `framework_rss` measurement differenced at stage boundaries within one process for the same
    # reason, and its execution log records two instrument defects that each came from getting
    # this boundary wrong.
    import artistpath_api.graph_store as gs

    before_ws = working_set()
    before_peak = peak_working_set()
    started = time.monotonic()
    store = gs.GraphStore.load(args.artifact)
    elapsed = time.monotonic() - started
    after_ws = working_set()
    after_peak = peak_working_set()

    record = {
        "label": args.label,
        "artifact": str(args.artifact),
        "repeat": args.repeat,
        "artists": len(store.mbids),
        "csr_entries": int(len(store.neighbours)),
        "working_set_before_load": before_ws,
        "working_set_after_load": after_ws,
        "working_set_delta": after_ws - before_ws,
        "process_peak_before_load": before_peak,
        # THE REPORTED FIGURE: the whole process's peak after the load. It is the quantity
        # `LBA-G1`(a) scales, and it is the kernel's own high-water mark, never a difference.
        "process_peak_after_load": after_peak,
        "process_peak_after_load_mib": round(after_peak / 1024**2, 2),
        "load_seconds": round(elapsed, 3),
        "measured_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"[boot] {args.label} r{args.repeat}: peak {record['process_peak_after_load_mib']:.2f} MiB  "
          f"artists {record['artists']:,}  csr {record['csr_entries']:,}  {elapsed:.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
