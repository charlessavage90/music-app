"""Summarise the sealed per-journey metrics `DRP-AM7-5` records, for `DRP-AM7-10`'s descriptive reads.

**Write-up session only, and only after `dsl_unblind.py`.** Decides nothing: it reads no answer file, so
it cannot re-tally anything (`DRP-AM7-11`). It exists because `dsl_unblind.py` emits the ear-tracking
counts but not the sealed metrics themselves, which `DRP-AM7-10` reports beside the verdict.

Per side and depth: median of each journey's mean interior `fame_lb_pctl` (unmeasured interiors skipped),
median node count, journeys traversing at least one added connection and the total traversed; candidate
side only, the ceiling `c` range and the journeys with relaxation `r` > 0.

    cd api && UV_LINK_MODE=copy uv run python ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_sealed_summary.py
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dsl_common import DEPTHS, in_dir, sealed_path  # noqa: E402


def summarise(sealed: dict) -> dict:
    out: dict = {}
    for role, by_pair in sealed["journeys"].items():
        out[role] = {}
        for d in DEPTHS:
            js = [by_pair[k][str(d)] for k in sorted(by_pair)]
            means = [statistics.fmean(f) for f in
                     ([x for x in j["fame_pctl_interior"] if x is not None] for j in js) if f]
            row = {
                "journeys": len(js),
                "median_mean_interior_fame_pctl": round(statistics.median(means), 4),
                "median_nodes": statistics.median(j["length"] for j in js),
                "journeys_with_added_connection": sum(1 for j in js if j["added_connections_traversed"]),
                "added_connections_traversed": sum(j["added_connections_traversed"] for j in js),
                "unmeasured_interiors": sum(1 for j in js for x in j["fame_pctl_interior"] if x is None),
            }
            cs = [j["ceiling_c"] for j in js if j.get("ceiling_c") is not None]
            if cs:
                row["ceiling_c_min_max"] = [min(cs), max(cs)]
                row["journeys_relaxed"] = sum(1 for j in js if (j.get("relaxation_r") or 0) > 0)
            out[role][str(d)] = row
    return out


def main() -> int:
    sealed = json.loads(sealed_path("dsl_sealed.json").read_text("utf-8"))
    out = {"decides": "nothing (DRP-AM7-10); reads no answer file", "by_role_and_depth": summarise(sealed)}
    in_dir("dsl_sealed_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
