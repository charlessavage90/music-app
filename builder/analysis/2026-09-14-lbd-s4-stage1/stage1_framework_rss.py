"""`LBA-` stage 1, step 2(a) -- measure `framework_rss`.

s4's definition: "resident of a booted `build_default_app` process minus the store's own
contribution, measured once on the served artifact. **This term has never been measured in
this project**, and `LBA-G1`(a) cannot be evaluated without it."

s5 restates why it matters: `LBA-G1`(a)'s original bar deducted one flat 30% to cover the
interpreter, the framework, the clip cache AND the metadata a census build omits -- four terms
that scale differently. `LBA-AM1` finding `LBA-AM1-A2` replaced that with measured terms, of
which this is one. `LBA-G1`(a) reads:

    projected shipped peak RSS = census build's measured median peak x metadata_ratio
                                 + framework_rss                       <= 1.6 GB

so what is wanted here is the framework's **additive** contribution to a booted process.

METHOD, determined from the shipped app rather than chosen. `build_default_app` (app.py:330)
does four things that cost memory: `load_graph` -> `GraphStore`, `ArtistSearch(store, cfg)`,
an `httpx.AsyncClient` + `InMemoryClipCache` + `ClipResolver`, and `create_app` -> `FastAPI`
with its middleware. This measures all four ADDITIVELY in ONE process, taking a working-set
snapshot after each stage, with the framework imported FIRST. Both the current working set and
the running peak are recorded at every stage.

⚠ TWO INSTRUMENT DEFECTS WERE FOUND AND FIXED HERE, BOTH OF WHICH RETURNED A PLAUSIBLE NUMBER.
Recorded because "confident prose about correct code" is this project's characteristic failure
and a wrong instrument is its close cousin.

  1. **Three separate processes, each importing `artistpath_api.app`.** That module is the only
     one pulling FastAPI, starlette, pydantic and httpx (checked from source: `artifact_source`,
     `config`, `graph_store`, `search` and `clips` import no web framework). So the framework
     loaded in the `store` baseline too and **cancelled in the subtraction**. Reported
     framework_rss = 0.1 MiB, with a NEGATIVE component.
  2. **`PeakWorkingSetSize` differenced across processes.** The peak is a whole-process
     high-water mark, and `load_graph` reads the entire artifact into `bytes` and parses it, so
     its transient peak sits well above its steady state. Importing the framework afterwards
     reuses freed pages and never exceeds that earlier mark -- so the framework's cost was
     invisible under the graph's peak. Reported framework_rss = 0.4 MiB against a process that
     demonstrably loads 384 framework modules.

  The fix for both: ONE process, framework first, and DIFFERENCE THE CURRENT WORKING SET at
  stage boundaries. The peak is still recorded, but it is reported, never differenced.

⚠ `framework_rss` IS NOT POPULATION-INDEPENDENT, and the decomposition is what makes that
visible. `ArtistSearch.__init__` holds `[normalise(n) for n in store.names]` (search.py:27) --
one Python string per artist. A figure measured on the served map's 58,838 artists understates
an arm several times larger. The per-artist search term below is what a later session scales;
the module and app-object terms are what it holds constant.

    cd api && uv run python ..\\builder\\analysis\\2026-09-14-lbd-s4-stage1\\stage1_framework_rss.py \\
        --out ..\\builder\\analysis\\2026-09-14-lbd-s4-stage1\\framework_rss.json
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
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


def _counters() -> _PROCESS_MEMORY_COUNTERS:
    # GetCurrentProcess returns the pseudo-handle (HANDLE)-1. Without an explicit restype
    # ctypes truncates it to a 32-bit int on 64-bit Windows and the call fails.
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


def snapshot() -> tuple[int, int]:
    c = _counters()
    return int(c.WorkingSetSize), int(c.PeakWorkingSetSize)


def measure_once() -> dict:
    """One process, five ordered stages, framework imported FIRST."""
    stages: list[dict] = []

    def mark(label: str, note: str) -> None:
        ws, peak = snapshot()
        stages.append({"stage": label, "working_set": ws, "peak": peak, "note": note})

    mark("baseline", "interpreter + this script, before any artistpath import")

    # 1. The framework, imported before anything else so its cost cannot hide under the
    #    graph's transient parse peak.
    import httpx  # noqa: F401
    from fastapi import FastAPI  # noqa: F401

    from artistpath_api.app import create_app
    from artistpath_api.clips import ClipResolver, InMemoryClipCache
    from artistpath_api.config import ApiConfig
    from artistpath_api.search import ArtistSearch
    mark("framework_imported", "fastapi + starlette + pydantic + httpx + the api package")

    cfg = ApiConfig()
    from artistpath_api.artifact_source import load_graph

    store = load_graph(cfg.graph_path, cfg.graph_sha256)
    mark("store_loaded", "load_graph -> GraphStore over the served artifact")

    search = ArtistSearch(store, cfg)
    mark("search_built", "ArtistSearch: one normalised Python str per artist (SCALES)")

    client = httpx.AsyncClient(timeout=cfg.clip_http_timeout)

    async def fetch_json(url: str, params: dict) -> dict:  # never called
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch_json)
    app = create_app(store, search, resolver, cfg)
    mark("app_created", "httpx client + in-memory clip cache + resolver + FastAPI + middleware")

    ws = [s["working_set"] for s in stages]
    return {
        "artists": len(store.names),
        "graph_path": cfg.graph_path,
        "routes": len(app.routes),
        "stages": stages,
        "deltas": {
            "framework_modules": ws[1] - ws[0],
            "store": ws[2] - ws[1],
            "search": ws[3] - ws[2],
            "app_objects": ws[4] - ws[3],
        },
        "final_working_set": ws[4],
        "process_peak": stages[-1]["peak"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--repeats", type=int, default=3)
    args = ap.parse_args(argv)

    if args.child:
        print(json.dumps(measure_once()))
        return 0

    runs = []
    for rep in range(args.repeats):
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--child"],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        runs.append(payload)
        d = payload["deltas"]
        print(f"[rss] rep {rep + 1}  modules {d['framework_modules']:>12,}"
              f"  store {d['store']:>12,}  search {d['search']:>11,}"
              f"  app {d['app_objects']:>10,}  final {payload['final_working_set']:>13,}",
              flush=True)

    def med(key: str) -> int:
        return int(statistics.median(r["deltas"][key] for r in runs))

    modules, store_d, search_d, app_d = (med("framework_modules"), med("store"),
                                         med("search"), med("app_objects"))
    artists = runs[0]["artists"]
    framework_rss = modules + app_d + search_d

    out = {
        "task": "LBA- stage 1, step 2(a) -- framework_rss",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "machine": f"the owner's Windows 11 workstation; Python {sys.version.split()[0]}, api/.venv",
        "metric": "WorkingSetSize differenced at stage boundaries within ONE process, "
                  "framework imported first; PeakWorkingSetSize reported, never differenced",
        "artifact": runs[0]["graph_path"],
        "artifact_artists": artists,
        "repeats": args.repeats,
        "median_deltas_bytes": {
            "framework_modules": modules,
            "store": store_d,
            "search": search_d,
            "app_objects": app_d,
        },
        "framework_rss_bytes": framework_rss,
        "framework_rss_mib": round(framework_rss / 1024 / 1024, 1),
        "framework_rss_definition": "s4: a booted process minus the store's own contribution "
                                    "= framework modules + ArtistSearch + the app objects",
        "population_dependence": {
            "constant_bytes": modules + app_d,
            "constant_mib": round((modules + app_d) / 1024 / 1024, 1),
            "scaling_bytes_per_artist": round(search_d / artists, 1),
            "scaling_term": "ArtistSearch holds one normalised Python str per artist "
                            "(search.py:27)",
            "note": "s4 defines framework_rss on the served artifact. Applying THIS single "
                    "figure to a larger arm understates it; apply constant + per-artist x N.",
        },
        "median_final_working_set_bytes": int(statistics.median(
            r["final_working_set"] for r in runs)),
        "median_process_peak_bytes": int(statistics.median(r["process_peak"] for r in runs)),
        "runs": runs,
    }
    if args.out:
        args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"\n[rss] framework modules   {modules:>13,} B  ({modules / 1048576:.1f} MiB)")
    print(f"[rss] store (the graph)   {store_d:>13,} B  ({store_d / 1048576:.1f} MiB)")
    print(f"[rss] ArtistSearch        {search_d:>13,} B  "
          f"({search_d / artists:.1f} B/artist -- SCALES)")
    print(f"[rss] app objects         {app_d:>13,} B  ({app_d / 1048576:.1f} MiB)")
    print(f"[rss] framework_rss     = {framework_rss:>13,} B  "
          f"({framework_rss / 1048576:.1f} MiB)")
    print(f"[rss]   of which constant {modules + app_d:>13,} B, "
          f"scaling {search_d / artists:.1f} B/artist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
