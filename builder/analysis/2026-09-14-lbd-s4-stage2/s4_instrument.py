"""`LBA-G2`'s peak-RSS instrument — a FORWARD COPY of stage 1's, with one defect fixed and the
self-test extended to the path that defect was on.

WHY IT EXISTS. `../2026-09-14-lbd-s4-stage1/stage2_build_instrument.py` raises on every real
build, at teardown:

    TypeError: 'Event' object is not callable
      ... threading.py, _wait_for_tstate_lock -> self._stop()
      ... stage2_build_instrument.py:127, in stop -> self.join(timeout=5)

**`_Sampler` subclasses `threading.Thread` and assigns `self._stop = threading.Event()`.**
`Thread._stop` is a real method of the base class, which CPython calls internally from
`join()` -> `_wait_for_tstate_lock()`. The assignment shadows it with an `Event`, so the first
`join()` after a thread has finished tries to call the Event and dies. It is a name collision
with a private base-class method, not a logic error, and it fires only on the path where the
sampler is actually started and then stopped — which is EVERY REAL BUILD and NO PART OF THE
STAGE-1 SELF-TEST.

WHY THE SELF-TEST MISSED IT, recorded because it is the more useful half. Stage 1's check 2
exercises the double-call guard by pre-populating `_ALREADY_BUILT` and calling
`instrumented_build(None, None, None, ...)`. The guard raises at the TOP of the function —
before `_Sampler` is ever constructed or started. So no self-test path reached `sampler.stop()`,
and the instrument was pronounced "written and self-tested" having never run a build to
completion. Stage 1's own handoff records the lesson one step short of this: *"the self-test for
the build instrument was itself wrong at first and failed the instrument for being correct. A
test can be as wrong as the thing it tests."* It can also be INCOMPLETE in a way that reads as
green, which is what happened here.

WHY A FORWARD COPY RATHER THAN AN EDIT. Stage 1's directory is a committed record and its README
states the self-test was run and passed, quoting its output. Editing that module in place would
silently invalidate that statement and the sha the stage-1 record carries. The 2026-08-09
precedent refuses re-running a frozen script in place, and this is the same shape. The stage-1
module is UNCHANGED and is superseded for any future use by this file.

WHAT IS COPIED AND WHAT IS REDEFINED. Everything pure is IMPORTED from the stage-1 module and is
therefore provably identical — the ctypes counters, `working_set`, `peak_working_set`,
`BuildPoint`, `_LogCapture`, `rows_from_archive_manifest`, `record_point`, `project_peak_rss` and
`LBA_G2_BAR_BYTES`. **`LBA-AM2`(d)'s fit rule and the 24 GB bar are untouched and not re-typed
here.** Only `_Sampler` and `instrumented_build` are redefined, and the guard list is this
module's own.

    python s4_instrument.py --self-test
"""
from __future__ import annotations

import argparse
import logging
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-09-14-lbd-s4-stage1"))

# Imported, never re-typed: the fit rule, the bar, the unit-safe row reader and the counters.
from stage2_build_instrument import (  # noqa: E402,F401
    LBA_G2_BAR_BYTES,
    BuildPoint,
    _LogCapture,
    peak_working_set,
    project_peak_rss,
    record_point,
    rows_from_archive_manifest,
    working_set,
)


class _Sampler(threading.Thread):
    """Cross-check and trajectory. Never the reported peak.

    THE FIX: the stop flag is `_stop_event`, not `_stop`. `threading.Thread._stop` is a real
    method of the base class and CPython calls it from `join()`; shadowing it with an `Event`
    makes every `join()` raise `TypeError: 'Event' object is not callable`.
    """

    def __init__(self, interval_s: float = 0.25) -> None:
        super().__init__(daemon=True)
        self.interval_s = interval_s
        self.samples: list[tuple[float, int]] = []
        self._stop_event = threading.Event()

    def run(self) -> None:
        t0 = time.monotonic()
        while not self._stop_event.is_set():
            self.samples.append((round(time.monotonic() - t0, 2), working_set()))
            self._stop_event.wait(self.interval_s)

    def stop(self) -> None:
        self._stop_event.set()
        self.join(timeout=5)


_ALREADY_BUILT: list[str] = []


def instrumented_build(config, archive, source, *, arm: str, archive_neighbour_rows: int,
                       _build_fn=None) -> tuple[object, list[str], BuildPoint]:
    """`lbv_build.run_build` plus the peak. ONE CALL PER PROCESS.

    `_build_fn` is a seam for the self-test ONLY, and it exists because of the defect this file
    fixes: with no way to inject a trivial build, no test could reach `sampler.stop()`, which is
    exactly where the instrument was broken. It defaults to the shipped `build_from_archive` and
    no caller in stage 2 passes it.
    """
    if _ALREADY_BUILT:
        raise RuntimeError(
            "REFUSING: instrumented_build has already run in this process (for "
            f"{_ALREADY_BUILT[0]}). PeakWorkingSetSize never falls, so a second build's peak "
            "would be contaminated by the first. Stage 2 runs one build per process."
        )
    _ALREADY_BUILT.append(arm)

    if _build_fn is None:
        from artistpath_builder.pipeline import build_from_archive
        _build_fn = build_from_archive

    before = working_set()
    sampler = _Sampler()
    sampler.start()

    capture = _LogCapture()
    log = logging.getLogger("artistpath_builder")
    log.addHandler(capture)
    log.setLevel(logging.INFO)
    started = time.monotonic()
    try:
        graph = _build_fn(config, archive, source)
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


def _self_test() -> int:
    """The stage-1 checks are NOT repeated here; this adds the one they could not reach."""
    global _ALREADY_BUILT
    print("[self-test] A. does a build run END TO END, through sampler start and stop?", flush=True)
    print("[self-test]    (this is the path the stage-1 instrument dies on)", flush=True)

    def fake_build(config, archive, source):
        # Allocate and touch, so the sampler thread has something real to see and the check
        # proves it RAN rather than merely that it was constructed.
        blob = bytearray(128 * 1024 * 1024)
        for i in range(0, len(blob), 4096):
            blob[i] = 1
        time.sleep(1.0)
        return "graph-sentinel"

    _ALREADY_BUILT = []
    try:
        graph, lines, point = instrumented_build(
            None, None, None, arm="self-test", archive_neighbour_rows=1_000_000,
            _build_fn=fake_build)
    except TypeError as exc:
        print(f"[self-test]    FAILED, and this is the stage-1 defect: {exc}", flush=True)
        return 1
    if graph != "graph-sentinel":
        print("[self-test]    FAILED: the build's return value was not passed through.", flush=True)
        return 1
    if point.peak_rss_bytes <= 0:
        print("[self-test]    FAILED: no peak was recorded.", flush=True)
        return 1
    if not point.samples:
        print("[self-test]    FAILED: the sampler thread recorded nothing.", flush=True)
        return 1
    if point.sampler_max > point.peak_rss_bytes:
        print("[self-test]    FAILED: the sampler exceeded the kernel's own peak.", flush=True)
        return 1
    print(f"[self-test]    build returned, peak {point.peak_rss_bytes / 1024**2:.1f} MiB, "
          f"{len(point.samples)} samples, sampler max within the kernel peak: OK", flush=True)

    print("[self-test] B. does the double-call guard still fire AFTER a real build?", flush=True)
    try:
        instrumented_build(None, None, None, arm="second", archive_neighbour_rows=1,
                           _build_fn=fake_build)
    except RuntimeError as exc:
        print(f"[self-test]    guard fired: {str(exc)[:60]}...", flush=True)
    else:
        print("[self-test]    FAILED: a second build in one process was allowed.", flush=True)
        return 1

    print("[self-test] C. is the imported fit rule the stage-1 one, unchanged?", flush=True)
    two = project_peak_rss([{"archive_neighbour_rows": 10_000_000, "peak_rss_bytes": 4 * 1024**3},
                            {"archive_neighbour_rows": 20_000_000, "peak_rss_bytes": 7 * 1024**3}],
                           52_254_182)
    red = project_peak_rss([{"archive_neighbour_rows": 10_000_000, "peak_rss_bytes": 6 * 1024**3},
                            {"archive_neighbour_rows": 20_000_000, "peak_rss_bytes": 12 * 1024**3}],
                           52_254_182)
    ok = (abs(two["projected_peak_rss_gib"] - 16.676) < 0.01 and not two["fires"]
          and red["fires"] and LBA_G2_BAR_BYTES == 24 * 1024**3)
    print(f"[self-test]    green {two['projected_peak_rss_gib']} GiB fires={two['fires']}; "
          f"red {red['projected_peak_rss_gib']} GiB fires={red['fires']}; bar 24 GiB: "
          f"{'OK' if ok else 'FAILED'}", flush=True)
    if not ok:
        return 1

    print("\n[self-test] all three checks pass; the teardown path stage 1 never reached is "
          "now covered.", flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    ap.error("nothing to do; pass --self-test")
