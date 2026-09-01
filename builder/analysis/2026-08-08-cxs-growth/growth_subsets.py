"""`CXS-`: does growing the crawl thin the obscure tail?

Governing document:
docs/superpowers/specs/2026-08-08-crawl-growth-subset-preregistration.md
(committed at 7f4b77b, amended CXS-AM1 at 43f0ce0, both BEFORE this ran).

Builds the ALG-B graph from the archive as it stood at three real moments in the
crawl, recovered by file mtime. Read-only: archives are supplied through an
in-memory overlay implementing the RawArchive protocol, so nothing is written to
the archive and no cleanup can be skipped by a kill.

    UV_LINK_MODE=copy uv run python -u growth_subsets.py
"""

from __future__ import annotations

import json
import statistics
import time
from collections.abc import Iterator
from pathlib import Path

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

SCRATCH = Path(__file__).resolve().parents[2] / "scratch"
ROOT = SCRATCH / "grt-archive-algb"
ALGB = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)
PREFIX = f"similar/listenbrainz/{ALGB}/"
SIZES = [25_000, 50_000, 75_000]
HERE = Path(__file__).resolve().parent


class SubsetArchive:
    """LocalArchive restricted to an allowed key set. Read-only."""

    def __init__(self, base: LocalArchive, allowed: set[str]) -> None:
        self._base = base
        self._allowed = allowed

    def put(self, key: str, payload: bytes) -> None:
        raise RuntimeError("SubsetArchive is read-only by design")

    def get(self, key: str) -> bytes | None:
        return self._base.get(key) if key in self._allowed else None

    def has(self, key: str) -> bool:
        return key in self._allowed and self._base.has(key)

    def keys(self) -> Iterator[str]:
        yield from sorted(self._allowed)


def build(allowed: set[str], label: str):
    cfg = BuilderConfig(
        algorithm=ALGB,
        drop_unlistenable=False,   # held constant (section 3)
        require_fame=False,        # held constant (section 3)
    )
    started = time.monotonic()
    graph = build_from_archive(
        cfg, SubsetArchive(LocalArchive(ROOT), allowed), ListenBrainzSource(cfg)
    )
    print(f"  {label} built in {time.monotonic() - started:.0f}s", flush=True)
    return graph


def main() -> None:
    print("recovering true crawl order from file mtimes...", flush=True)
    directory = ROOT / "similar" / "listenbrainz" / ALGB
    stamped = sorted(
        (p.stat().st_mtime, p.name) for p in directory.glob("*.json")
    )
    print(f"  {len(stamped)} responses", flush=True)

    cells: dict[int, dict] = {}
    graphs: dict[int, object] = {}
    for size in SIZES:
        allowed = {PREFIX + name for _mtime, name in stamped[:size]}
        graphs[size] = build(allowed, f"CXS-{size // 1000}")

    # --- the cohort, frozen at the CXS-25 frame (section 4) ----------------
    base_graph = graphs[SIZES[0]]
    order = sorted(range(len(base_graph.mbids)), key=lambda i: base_graph.pop_raw[i])
    bottom_half = order[: len(order) // 2]
    cohort = {base_graph.mbids[i] for i in bottom_half}
    print(f"\ncohort frozen at CXS-{SIZES[0] // 1000}: {len(cohort)} artists "
          f"(bottom half by pop_raw)", flush=True)

    for size in SIZES:
        graph = graphs[size]
        idx = {m: i for i, m in enumerate(graph.mbids)}
        degrees = graph.offsets[1:] - graph.offsets[:-1]
        present = [idx[m] for m in cohort if m in idx]
        cohort_degrees = [int(degrees[i]) for i in present]
        absent = len(cohort) - len(present)
        cells[size] = {
            "cell": f"CXS-{size // 1000}",
            "population": size,
            "nodes": len(graph.mbids),
            "edges": int(degrees.sum()),
            "share_at_ceiling": round(float((degrees >= 50).mean()), 4),
            "share_degree_1": round(float((degrees == 1).mean()), 4),
            # CXS-C1 (primary)
            "cohort_median_degree": statistics.median(cohort_degrees),
            "cohort_mean_degree": round(statistics.fmean(cohort_degrees), 2),
            # CXS-C2 (absolute, per CXS-AM1)
            "cohort_absent": absent,
            "cohort_absent_share": round(absent / len(cohort), 4),
        }
        print(json.dumps(cells[size]), flush=True)

    first, last = cells[SIZES[0]], cells[SIZES[-1]]
    mid = cells[SIZES[1]]
    c1_delta = (last["cohort_median_degree"] - first["cohort_median_degree"]) / first[
        "cohort_median_degree"
    ]
    step1 = mid["cohort_median_degree"] - first["cohort_median_degree"]
    step2 = last["cohort_median_degree"] - mid["cohort_median_degree"]

    result = {
        "governing_document": (
            "docs/superpowers/specs/2026-08-08-crawl-growth-subset-preregistration.md"
        ),
        "cohort_size": len(cohort),
        "cells": [cells[s] for s in SIZES],
        "CXS_C1_relative_change": round(c1_delta, 4),
        "CXS_C1_material": abs(c1_delta) >= 0.10,
        "CXS_C1_monotonic": (step1 >= 0 and step2 >= 0) or (step1 <= 0 and step2 <= 0),
        "CXS_C2_final_share": last["cohort_absent_share"],
        "CXS_C2_material": last["cohort_absent_share"] >= 0.01,
    }
    (HERE / "cxs_growth.json").write_text(json.dumps(result, indent=2))

    print("\n=== READ AGAINST THE PRE-REGISTERED THRESHOLDS ===")
    print(f"  CXS-C1 median cohort degree: "
          f"{first['cohort_median_degree']} -> {mid['cohort_median_degree']} -> "
          f"{last['cohort_median_degree']}   ({c1_delta:+.1%})")
    print(f"    material (>=10%): {result['CXS_C1_material']}   "
          f"monotonic: {result['CXS_C1_monotonic']}")
    print(f"  CXS-C2 cohort absent at CXS-75: {last['cohort_absent_share']:.2%}"
          f"   material (>=1%): {result['CXS_C2_material']}")
    print(f"\nwrote {HERE / 'cxs_growth.json'}")


if __name__ == "__main__":
    main()
