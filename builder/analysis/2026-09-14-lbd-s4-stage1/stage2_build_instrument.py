"""`LBA-` step 2(b) -- the peak-RSS instrument `LBA-G2` needs, for the stage-2 build wrapper.

s10 records it as NOT-YET-BUILT: "**Peak-RSS instrumentation in the build wrapper does not
exist** (`LBA-AM1`, finding `LBA-AM1-A3`). No build on the record reports a memory figure --
checked across both build READMEs and every committed JSON beside them on 2026-09-14 -- so
**`LBA-G2` cannot be evaluated until stage 2 adds it.** A few lines in `lbv_build.py`'s shape."

This is those few lines, as a FORWARD COPY in this session's own directory. It touches no
shipped code under `builder/src` and it does not modify `lbv_build.py`, whose outputs are a
frozen record (the 2026-08-09 precedent: re-running a frozen script in place is refused).

Stage 2 imports `instrumented_build` in place of `lbv_build.run_build`, which it mirrors
exactly -- same `LogCapture` seam, same return shape plus the peak.

--------------------------------------------------------------------------------------------
WHAT `LBA-G2` READS, AND THE UNIT
--------------------------------------------------------------------------------------------
s5: "the arm's projected build peak RSS exceeds **24 GB**, projected from a fit over every
build already instrumented in this stage, in **archive neighbour rows**."

⚠ **ARCHIVE NEIGHBOUR ROWS -- pre-cap, two per pair -- NEVER CSR entries.** Three edge units
are in play in this track and the served-population README s0 records a build refused once for
writing a bound in one unit and checking it in another. `record_point` takes the row count from
the archive `MANIFEST.json`'s own `counts.neighbour_rows_written`, which is the emitter's
figure, so the unit cannot be re-derived wrongly at the call site.

--------------------------------------------------------------------------------------------
ONE BUILD PER PROCESS -- a requirement, not a convenience
--------------------------------------------------------------------------------------------
`PeakWorkingSetSize` is a whole-process high-water mark and never falls. With two builds in one
process the second build's peak is contaminated by the first, and a large build followed by a
small one reports the large one's peak twice. `lvb_build.py` ran two builds per process, which
was fine because it recorded no memory. **Stage 2 must not.**

`instrumented_build` refuses if it is called twice in one process, rather than trusting the
caller to remember.

A sampling thread runs alongside and records the trajectory. It is a CROSS-CHECK and the
peak reported is the kernel's, not the sampler's: a sampler can miss a sharp spike between
ticks, and it is that spike `LBA-G2` exists to catch.

--------------------------------------------------------------------------------------------
SELF-TEST -- the instrument is shown to go RED before any figure from it is believed
--------------------------------------------------------------------------------------------
A green reading from a new instrument is not evidence until the instrument has been shown to
move. `--self-test` allocates a known number of megabytes and asserts the instrument sees them
within tolerance, then asserts the double-call guard fires. Run it before stage 2 trusts a
single figure from this module.

    python stage2_build_instrument.py --self-test
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


class _PROCESS_MEMORY_COUNTERS(ctypes.Structure):
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


def _memory_counters() -> _PROCESS_MEMORY_COUNTERS:
    # GetCurrentProcess returns the pseudo-handle (HANDLE)-1; without an explicit restype
    # ctypes truncates it to 32 bits on 64-bit Windows and the call fails.
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wt.HANDLE
    kernel32.GetCurrentProcess.argtypes = []
    handle = kernel32.GetCurrentProcess()
    for dll, name in ((kernel32, "K32GetProcessMemoryInfo"),
                      (ctypes.WinDLL("psapi", use_last_error=True), "GetProcessMemoryInfo")):
        fn = getattr(dll, name, None)
        if fn is None:
            continue
        fn.restype = wt.BOOL
        fn.argtypes = [wt.HANDLE, ctypes.POINTER(_PROCESS_MEMORY_COUNTERS), wt.DWORD]
        c = _PROCESS_MEMORY_COUNTERS()
        c.cb = ctypes.sizeof(c)
        if fn(handle, ctypes.byref(c), c.cb):
            return c
    raise OSError(f"GetProcessMemoryInfo failed (last error {ctypes.get_last_error()})")


def working_set() -> int:
    return int(_memory_counters().WorkingSetSize)


def peak_working_set() -> int:
    return int(_memory_counters().PeakWorkingSetSize)


class _Sampler(threading.Thread):
    """Cross-check and trajectory. Never the reported peak."""

    def __init__(self, interval_s: float = 0.25) -> None:
        super().__init__(daemon=True)
        self.interval_s = interval_s
        self.samples: list[tuple[float, int]] = []
        self._stop = threading.Event()

    def run(self) -> None:
        t0 = time.monotonic()
        while not self._stop.is_set():
            self.samples.append((round(time.monotonic() - t0, 2), working_set()))
            self._stop.wait(self.interval_s)

    def stop(self) -> None:
        self._stop.set()
        self.join(timeout=5)


class _LogCapture(logging.Handler):
    """`lbv_build.py`'s seam, unchanged -- the builder prints only non-zero drop counts."""

    def __init__(self) -> None:
        super().__init__()
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(record.getMessage())


@dataclass
class BuildPoint:
    """One instrumented build: `LBA-G2`'s (x, y)."""

    arm: str
    archive_neighbour_rows: int          # x -- pre-cap, two per pair
    peak_rss_bytes: int                  # y
    wall_clock_s: float
    working_set_before: int
    sampler_max: int
    samples: list[tuple[float, int]] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "arm": self.arm,
            "archive_neighbour_rows": self.archive_neighbour_rows,
            "unit": "archive neighbour rows, pre-cap, two per pair -- NOT CSR entries",
            "peak_rss_bytes": self.peak_rss_bytes,
            "peak_rss_gib": round(self.peak_rss_bytes / 1024**3, 3),
            "wall_clock_s": round(self.wall_clock_s, 1),
            "working_set_before": self.working_set_before,
            "sampler_max": self.sampler_max,
            "sampler_within_kernel_peak": self.sampler_max <= self.peak_rss_bytes,
            "samples": self.samples,
        }


_ALREADY_BUILT: list[str] = []


def instrumented_build(config, archive, source, *, arm: str,
                       archive_neighbour_rows: int) -> tuple[object, list[str], BuildPoint]:
    """`lbv_build.run_build` plus the peak. ONE CALL PER PROCESS -- see the module docstring."""
    from artistpath_builder.pipeline import build_from_archive

    if _ALREADY_BUILT:
        raise RuntimeError(
            "REFUSING: instrumented_build has already run in this process (for "
            f"{_ALREADY_BUILT[0]}). PeakWorkingSetSize never falls, so a second build's peak "
            "would be contaminated by the first. Stage 2 runs one build per process."
        )
    _ALREADY_BUILT.append(arm)

    before = working_set()
    sampler = _Sampler()
    sampler.start()

    capture = _LogCapture()
    log = logging.getLogger("artistpath_builder")
    log.addHandler(capture)
    log.setLevel(logging.INFO)
    started = time.monotonic()
    try:
        graph = build_from_archive(config, archive, source)
    finally:
        wall = time.monotonic() - started
        log.removeHandler(capture)
        sampler.stop()

    point = BuildPoint(
        arm=arm,
        archive_neighbour_rows=archive_neighbour_rows,
        peak_rss_bytes=peak_working_set(),
        wall_clock_s=wall,
        working_set_before=before,
        sampler_max=max((v for _, v in sampler.samples), default=0),
        samples=sampler.samples,
    )
    return graph, capture.lines, point


def rows_from_archive_manifest(manifest_path: Path) -> int:
    """The emitter's own figure, so the unit cannot be re-derived wrongly at the call site."""
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    return int(data["counts"]["neighbour_rows_written"])


def record_point(points_path: Path, point: BuildPoint) -> list[dict]:
    """Append one build to the running point set stage 2 projects from."""
    points_path = Path(points_path)
    points = json.loads(points_path.read_text(encoding="utf-8")) if points_path.exists() else []
    points.append(point.as_dict())
    points_path.write_text(json.dumps(points, indent=2), encoding="utf-8")
    return points


LBA_G2_BAR_BYTES = 24 * 1024**3


def project_peak_rss(points: list[dict], rows: int) -> dict:
    """`LBA-AM2`(d)'s fit rule, stated before stage 2 so it is not chosen with results in hand.

    0 points  -- no projection exists; the gate is SILENT, not permissive (`LBA-AM2`(b)).
    1 point   -- proportional, through the origin, and labelled as such.
    2+ points -- least-squares line in archive neighbour rows, intercept free.
    """
    n = len(points)
    if n == 0:
        return {"projectable": False, "basis": "no instrumented build yet",
                "note": "LBA-AM2(b): the first build is unevaluable by LBA-G2 and proceeds "
                        "unconditionally; the gate is silent, not permissive."}
    xs = [p["archive_neighbour_rows"] for p in points]
    ys = [p["peak_rss_bytes"] for p in points]
    if n == 1:
        slope = ys[0] / xs[0]
        projected = slope * rows
        basis = "proportional through the origin (a single instrumented point)"
    else:
        mx = sum(xs) / n
        my = sum(ys) / n
        denom = sum((x - mx) ** 2 for x in xs)
        if denom == 0:
            slope = 0.0
            intercept = my
        else:
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
            intercept = my - slope * mx
        projected = slope * rows + intercept
        basis = f"least-squares line over {n} instrumented builds, intercept free"
    return {
        "projectable": True,
        "basis": basis,
        "points_used": n,
        "archive_neighbour_rows": rows,
        "projected_peak_rss_bytes": int(projected),
        "projected_peak_rss_gib": round(projected / 1024**3, 3),
        "bar_gib": 24,
        "fires": projected > LBA_G2_BAR_BYTES,
    }


def _self_test() -> int:
    """Show the instrument going RED before any figure from it is believed."""
    global _ALREADY_BUILT
    print("[self-test] 1. does the peak move when memory is allocated?", flush=True)
    base = peak_working_set()
    megabytes = 256
    blob = bytearray(megabytes * 1024 * 1024)
    for i in range(0, len(blob), 4096):   # touch every page; untouched pages are not resident
        blob[i] = 1
    after = peak_working_set()
    seen = (after - base) / 1024 / 1024
    print(f"[self-test]    allocated {megabytes} MiB, peak rose by {seen:.1f} MiB", flush=True)
    if seen < megabytes * 0.8:
        print("[self-test]    FAILED: the instrument did not see the allocation.", flush=True)
        return 1
    del blob

    print("[self-test] 2. does the double-call guard fire?", flush=True)
    _ALREADY_BUILT = ["pretend-arm"]
    try:
        instrumented_build(None, None, None, arm="second", archive_neighbour_rows=1)
    except RuntimeError as exc:
        print(f"[self-test]    guard fired: {str(exc)[:60]}...", flush=True)
    else:
        print("[self-test]    FAILED: a second build in one process was allowed.", flush=True)
        return 1
    _ALREADY_BUILT = []

    print("[self-test] 3. does the projection follow LBA-AM2(d)?", flush=True)
    empty = project_peak_rss([], 10_000_000)
    one = project_peak_rss([{"archive_neighbour_rows": 10_000_000,
                             "peak_rss_bytes": 4 * 1024**3}], 20_000_000)
    # slope 3 GiB / 10M rows, intercept 1 GiB -> 1 + 3 * 5.2254 = 16.68 GiB. UNDER the bar,
    # and the expected value is the arithmetic, not a guess: a first version of this test
    # asserted `fires` here and failed the instrument for being correct.
    two = project_peak_rss([{"archive_neighbour_rows": 10_000_000, "peak_rss_bytes": 4 * 1024**3},
                            {"archive_neighbour_rows": 20_000_000, "peak_rss_bytes": 7 * 1024**3}],
                           52_254_182)
    # The gate must also be shown to go RED: same rows, a steeper slope.
    red = project_peak_rss([{"archive_neighbour_rows": 10_000_000, "peak_rss_bytes": 6 * 1024**3},
                            {"archive_neighbour_rows": 20_000_000, "peak_rss_bytes": 12 * 1024**3}],
                           52_254_182)
    ok = (not empty["projectable"]
          and one["projectable"] and abs(one["projected_peak_rss_gib"] - 8.0) < 0.01
          and two["projectable"] and abs(two["projected_peak_rss_gib"] - 16.676) < 0.01
          and not two["fires"]
          and red["projectable"] and red["fires"])
    print(f"[self-test]    0 points -> silent: {not empty['projectable']}", flush=True)
    print(f"[self-test]    1 point  -> {one['projected_peak_rss_gib']} GiB "
          f"({one['basis']})", flush=True)
    print(f"[self-test]    2 points -> {two['projected_peak_rss_gib']} GiB at 52,254,182 rows, "
          f"fires={two['fires']} (expected False)", flush=True)
    print(f"[self-test]    steeper  -> {red['projected_peak_rss_gib']} GiB at the same rows, "
          f"fires={red['fires']} (expected True -- the gate shown going RED)", flush=True)
    if not ok:
        print("[self-test]    FAILED: the projection rule did not behave as specified.",
              flush=True)
        return 1

    print("\n[self-test] all three checks pass; the instrument has been shown to move.",
          flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(_self_test())
    ap.error("nothing to do: this module is imported by the stage-2 build wrapper. "
             "Run --self-test to verify the instrument.")
