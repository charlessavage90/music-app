"""Side-by-side path comparison as one self-contained HTML file.

RANK IS MANDATORY, NOT DECORATIVE. The defect that invalidated two analyses was
invisible in scores — twelve consecutive 1.0000s — and obvious in rank. A tool
that shows only scores would have missed it, exactly as the original review did.

Showing the DECODED PATH is equally mandatory. The opposite failure also
happened: neighbour rankings improved under a change whose routed paths got
worse. Both views, one screen.

Usage:
    cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python \\
        eval/export_paths.py out.html graph-a.bin graph-b.bin

Cost: this is CPU-bound `find_path` (Dijkstra), not I/O — measured at ~1.55s
per (pair, artifact) on the 75k/4.1M-edge graph, ~99.9% of total wall time.
For N artifacts expect roughly 138 * N * 1.55s. Set PYTHONUNBUFFERED=1 (or
`python -u`) to see the `[progress]` lines and the final per-stage timing
breakdown live rather than only at exit.
"""

from __future__ import annotations

import html
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_path  # noqa: E402
from diagnostics import artifact_diagnostics  # noqa: E402
from panel import load_panel, resolve_pairs  # noqa: E402

_CSS = """
body{font:14px/1.5 system-ui,sans-serif;margin:2rem;background:#fff;color:#111}
table{border-collapse:collapse;width:100%;margin-bottom:2rem}
th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;vertical-align:top}
th{background:#f4f4f4}
.wrap{overflow-x:auto}
.hop{white-space:nowrap}
.ceiling{background:#ffe0e0;font-weight:600}
.hub{color:#a00}
.muted{color:#777;font-size:12px}
@media(prefers-color-scheme:dark){
 body{background:#111;color:#eee}th{background:#222}th,td{border-color:#333}
 .ceiling{background:#4a1f1f}
}
"""


def neighbour_rank(store: GraphStore, u: int, v: int) -> int | None:
    """1-based rank of v within u's neighbour list, ordered by descending score.

    This is the view that makes a saturated ceiling visible: twelve neighbours
    all scoring 1.0000 look identical by score and are ranks 1-12 by position.
    """
    start, end = int(store.offsets[u]), int(store.offsets[u + 1])
    row_ids = store.neighbours[start:end]
    row_scores = store.scores[start:end]
    order = np.argsort(-row_scores, kind="stable")
    for rank, idx in enumerate(order, start=1):
        if int(row_ids[idx]) == v:
            return rank
    return None


def _hops(store: GraphStore, path: list[int], hub_cutoff: int) -> list[dict]:
    degrees = np.diff(store.offsets)
    out = []
    for position, node in enumerate(path):
        previous = path[position - 1] if position else None
        out.append(
            {
                "name": store.names[node] or f"<unnamed {node}>",
                "rank": neighbour_rank(store, previous, node) if previous is not None else None,
                "score": (
                    float(store.scores[
                        int(store.offsets[previous])
                        + int(np.searchsorted(
                            store.neighbours[
                                int(store.offsets[previous]):int(store.offsets[previous + 1])
                            ], node))
                    ])
                    if previous is not None
                    else None
                ),
                "degree": int(degrees[node]),
                "hub": bool(degrees[node] >= hub_cutoff),
            }
        )
    return out


def render_html(artifacts: list[dict], panel_name: str, rows: list[dict]) -> str:
    """One self-contained page. No external assets — it is opened from disk."""
    # Explicit charset declaration, not just UTF-8 bytes on disk: opened as a
    # bare file:// URL, without this a browser can guess the wrong encoding
    # and mojibake exactly the artist names this tool exists to make legible.
    parts = [f'<meta charset="utf-8"><title>artistpath path comparison</title><style>{_CSS}</style>']
    parts.append(f"<h1>Path comparison — panel: {html.escape(panel_name)}</h1>")

    parts.append("<h2>Artifact diagnostics</h2><div class='wrap'><table><tr><th>metric</th>")
    for a in artifacts:
        parts.append(f"<th>{html.escape(a['label'])}</th>")
    parts.append("</tr>")
    keys = sorted({k for a in artifacts for k in a.get("diagnostics", {})})
    for key in keys:
        parts.append(f"<tr><td>{html.escape(key)}</td>")
        for a in artifacts:
            value = a.get("diagnostics", {}).get(key, "")
            shown = f"{value:.4g}" if isinstance(value, float) else str(value)
            parts.append(f"<td>{html.escape(shown)}</td>")
        parts.append("</tr>")
    parts.append("</table></div>")

    parts.append("<h2>Paths</h2><div class='wrap'><table><tr><th>pair</th>")
    for a in artifacts:
        parts.append(f"<th>{html.escape(a['label'])}</th>")
    parts.append("</tr>")
    for row in rows:
        parts.append(f"<tr><td>{html.escape(row['pair'])}</td>")
        for cell in row["cells"]:
            parts.append("<td>")
            for hop in cell["hops"]:
                classes = []
                if hop["score"] is not None and hop["score"] >= 1.0:
                    classes.append("ceiling")
                if hop.get("hub"):
                    classes.append("hub")
                attr = f" class='hop {' '.join(classes)}'" if classes else " class='hop'"
                detail = (
                    f" <span class='muted'>[rank {hop['rank']}, "
                    f"{hop['score']:.4f}, deg {hop['degree']}]</span>"
                    if hop["rank"] is not None
                    else f" <span class='muted'>[deg {hop['degree']}]</span>"
                )
                parts.append(f"<div{attr}>{html.escape(hop['name'])}{detail}</div>")
            if cell.get("note"):
                parts.append(f"<div class='muted'>{html.escape(cell['note'])}</div>")
            parts.append("</td>")
        parts.append("</tr>")
    parts.append("</table></div>")
    return "".join(parts)


# Per-stage wall-clock accounting. Added while investigating a review finding
# that a claimed ~7 minute run was attributed to "OneDrive I/O latency" on
# self-contradictory evidence (near-zero shell `user`/`sys` time alongside a
# claimed 138-pair x 2-artifact CPU workload). This times each stage in-process
# so the next person to run this tool (Task 15) gets a real breakdown instead
# of a guess. Kept because it's cheap and directly answers "is this hanging?".
def _new_timings() -> dict[str, float]:
    return {
        "artifact_load": 0.0,
        "panel_load": 0.0,
        "diagnostics": 0.0,
        "hub_cutoffs": 0.0,
        "find_path": 0.0,
        "hops": 0.0,
        "render_and_write": 0.0,
    }


def _print_timings(timings: dict[str, float], total: float, pair_count: int) -> None:
    print(f"\n--- export_paths.py timing breakdown ({pair_count} pairs) ---", flush=True)
    for stage, seconds in timings.items():
        pct = (seconds / total * 100) if total else 0.0
        print(f"  {stage:<16} {seconds:8.3f}s  ({pct:5.1f}%)", flush=True)
    accounted = sum(timings.values())
    print(f"  {'unaccounted':<16} {total - accounted:8.3f}s  ({(total - accounted) / total * 100 if total else 0:5.1f}%)", flush=True)
    print(f"  {'TOTAL':<16} {total:8.3f}s", flush=True)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    out_path = Path(sys.argv[1])
    graph_paths = sys.argv[2:]

    timings = _new_timings()
    run_start = time.perf_counter()

    t0 = time.perf_counter()
    panel = load_panel(Path(__file__).parent / "panel.json")
    timings["panel_load"] += time.perf_counter() - t0
    print(f"[stage] panel loaded ({timings['panel_load']:.3f}s)", flush=True)

    t0 = time.perf_counter()
    stores = [(Path(p).name, GraphStore.load(p)) for p in graph_paths]
    timings["artifact_load"] += time.perf_counter() - t0
    print(f"[stage] artifacts loaded ({timings['artifact_load']:.3f}s)", flush=True)

    cfg = ApiConfig()

    t0 = time.perf_counter()
    artifacts = [
        {"label": label, "diagnostics": artifact_diagnostics(store, cap=50)}
        for label, store in stores
    ]
    timings["diagnostics"] += time.perf_counter() - t0
    print(f"[stage] diagnostics computed ({timings['diagnostics']:.3f}s)", flush=True)

    t0 = time.perf_counter()
    hub_cutoffs = {
        label: int(np.quantile(np.diff(store.offsets), 0.99))
        for label, store in stores
    }
    timings["hub_cutoffs"] += time.perf_counter() - t0
    print(f"[stage] hub cutoffs computed ({timings['hub_cutoffs']:.3f}s)", flush=True)

    rows = []
    pair_count = 0
    for stratum in ("hand_picked", "random", "obscure", "popularity_weighted"):
        for entry in panel["strata"].get(stratum, []):
            pair_count += 1
            if pair_count % 25 == 0:
                print(f"[progress] {pair_count} pairs done ({time.perf_counter() - run_start:.1f}s elapsed)", flush=True)
            cells = []
            for label, store in stores:
                a = store.id_by_mbid.get(entry["from"])
                b = store.id_by_mbid.get(entry["to"])
                if a is None or b is None:
                    cells.append({"label": label, "hops": [],
                                  "note": "endpoint absent from this artifact"})
                    continue
                t0 = time.perf_counter()
                path = find_path(store, a, b, [], cfg)
                timings["find_path"] += time.perf_counter() - t0
                if not path:
                    cells.append({"label": label, "hops": [], "note": "no path"})
                    continue
                t0 = time.perf_counter()
                hops = _hops(store, path, hub_cutoffs[label])
                timings["hops"] += time.perf_counter() - t0
                cells.append({"label": label, "hops": hops})
            rows.append(
                {
                    "pair": f"[{stratum}] {entry['from_name']} -> {entry['to_name']}",
                    "cells": cells,
                }
            )

    t0 = time.perf_counter()
    out_path.write_text(render_html(artifacts, "panel.json", rows), encoding="utf-8")
    timings["render_and_write"] += time.perf_counter() - t0

    total = time.perf_counter() - run_start
    print(f"wrote {out_path} ({out_path.stat().st_size / 1000:.0f} kB)", flush=True)
    _print_timings(timings, total, pair_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
