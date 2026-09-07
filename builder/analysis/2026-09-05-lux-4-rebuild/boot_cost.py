"""`LUX-E5` — what the extra artist metadata costs at API boot.

Plain sentence, fixed in the spec before any result existed: *does the extra
artist information still fit in the memory the running service actually has?*

Threshold, also from the spec: it must fit within the deployed container's
configured memory with headroom for the existing working set. Production is
AWS App Runner at **1 vCPU / 2 GB** (`infra/src/artistpath_infra/stack.py`).
If it does not fit, fields are dropped -- starting with tags, never with
`LUX-E2`'s survivors. Tags are already deferred, so the first droppable thing
is `artist_facts`' `area`.

WHAT THIS MEASURES, AND WHAT IT DOES NOT. It loads the artifact through the
api's own `GraphStore.load` -- the real boot path, not a proxy -- in a fresh
process, and reports peak working set and wall time. It runs on this Windows
workstation, NOT in the deployed Linux container, so treat the absolute numbers
as indicative and the DELTA between the two artifacts as the measurement. The
delta is what the change costs; the baseline is the platform's.

No psutil in the api venv, so peak working set comes from the Win32
`GetProcessMemoryInfo` API via ctypes rather than adding a dependency for one
measurement.

Run from `api/`:
    UV_LINK_MODE=copy uv run python \\
        ../builder/analysis/2026-09-05-lux-4-rebuild/boot_cost.py <artifact>
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import gc
import json
import tracemalloc
import sys
import time
from pathlib import Path

from artistpath_api.graph_store import GraphStore


class _Counters(ctypes.Structure):
    _fields_ = [
        ("cb", wt.DWORD),
        ("PageFaultCount", wt.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


_K32 = ctypes.WinDLL("kernel32")
_PSAPI = ctypes.WinDLL("psapi")
# ⚠ restype MUST be set. Without it ctypes assumes c_int and truncates the
# 64-bit pseudo-handle, GetProcessMemoryInfo returns 0, and the struct stays
# ZEROED -- which reads as "this uses no memory" rather than as an error. That
# is exactly how the first run of this script reported 0 bytes for everything.
_K32.GetCurrentProcess.restype = wt.HANDLE
_PSAPI.GetProcessMemoryInfo.argtypes = [
    wt.HANDLE,
    ctypes.POINTER(_Counters),
    wt.DWORD,
]
_PSAPI.GetProcessMemoryInfo.restype = wt.BOOL


def memory() -> tuple[int, int]:
    """(current working set, peak working set) in bytes. Raises on failure."""
    counters = _Counters()
    counters.cb = ctypes.sizeof(_Counters)
    if not _PSAPI.GetProcessMemoryInfo(
        _K32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise OSError("GetProcessMemoryInfo failed; refusing to report zeros")
    return counters.WorkingSetSize, counters.PeakWorkingSetSize


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    # Confined to the repository tree, and this one IS worth confining. The
    # accepted Path Traversal Lows under builder/analysis/ are capture scripts
    # whose `--out` deliberately writes OUTSIDE the repo, so constraining them
    # would break intended usage. This script only ever reads an artifact from
    # builder/scratch/, so the constraint costs nothing and the finding goes
    # away rather than joining a list of accepted ones.
    root = Path(__file__).resolve().parents[3]
    try:
        # Resolved against the CWD, which is where a relative argument is
        # written from -- resolving against `root` instead silently walks out
        # of the tree for any `../` path and rejects a valid artifact.
        path = Path(sys.argv[1]).resolve()
        path.relative_to(root)
    except ValueError:
        print(f"FATAL: {sys.argv[1]} is outside the repository", file=sys.stderr)
        return 2
    if not path.exists():
        print(f"FATAL: missing {path}", file=sys.stderr)
        return 2

    gc.collect()
    before, _ = memory()
    tracemalloc.start()

    started = time.perf_counter()
    store = GraphStore.load(path)
    elapsed = time.perf_counter() - started

    gc.collect()
    after, peak = memory()

    # ⚠ `GraphStore.load` PARSES the new keys and then discards them -- the api
    # does not retain them until `L4-T8`. Measuring only the load would
    # therefore understate what the running service will hold. So materialise
    # exactly what T8 will keep: three node-indexed Python lists, one of them
    # 58,838 dicts. Python objects are far heavier than their JSON bytes, and
    # that gap is the number LUX-E5 is actually about.
    import struct

    raw = path.read_bytes()
    *_, meta_len = struct.Struct("<4sIIIQ").unpack_from(raw)
    meta = json.loads(raw[len(raw) - meta_len :].decode("utf-8"))
    retained = [
        meta.get("spotify_ids", []),
        meta.get("apple_ids", []),
        meta.get("artist_facts", []),
    ]
    del raw, meta
    gc.collect()
    after_retained, peak_retained = memory()
    # Cross-check on the OS number: tracemalloc counts PYTHON HEAP allocations
    # exactly, so a wild disagreement between the two means one of them is
    # measuring something other than what this claims to.
    traced, traced_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(
        json.dumps(
            {
                "artifact": path.name,
                "artifact_bytes": path.stat().st_size,
                "artists": len(store.mbids),
                "boot_seconds": round(elapsed, 2),
                "rss_before_bytes": before,
                "rss_after_bytes": after,
                "rss_delta_bytes": after - before,
                "peak_working_set_bytes": peak,
                "rss_with_lux4_lists_retained_bytes": after_retained,
                "lux4_retention_cost_bytes": after_retained - after,
                "peak_with_retention_bytes": peak_retained,
                "retained_lengths": [len(x) for x in retained],
                "tracemalloc_current_bytes": traced,
                "tracemalloc_peak_bytes": traced_peak,
                # The keys present tell you which artifact this was without
                # trusting the filename.
                "has_lux4_keys": bool(getattr(store, "spotify_ids", [])),
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
