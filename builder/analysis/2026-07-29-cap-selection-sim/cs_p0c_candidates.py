"""CS-P0c -- THE DECISIVE ONE. Do superstars have obscure candidates in the ARCHIVE at all?

Read-only over the crawl archive and the adopted artifact. Builds nothing, adopts
nothing, touches no network.

WHY THIS RUNS BEFORE ANY ARM IS DESIGNED. Every cap rule -- production's mutual k-NN,
BTF-4's popularity-proximity, a reserved-slot quota, anything -- is a rule for CHOOSING
from a candidate list. None of them can select a neighbour the crawl never returned.

So one question sits upstream of the entire cap-selection design:

    For a superstar, does the RAW candidate list contain artists below the top
    popularity decile -- and how many?

  * YES, in healthy numbers -> DD-F1 is a SELECTION defect. The candidates exist and
    the cap discards them. Cap selection is the right lever; MKS-5b's simulation is
    worth designing and the rebuild plan starts there.
  * NO -> DD-F1 is a SOURCE defect. No cap rule can fix it, and the rebuild plan's
    first task should be STC-6 (co-occurrence threshold / re-crawl) instead.

Those readings send the rebuild plan in different directions, which is what makes this
decisive rather than preliminary.

METHOD, and the one thing it is careful about. Candidate popularity is read off the
ADOPTED ARTIFACT (sha256 asserted), which is the trusted source for `pop_raw`. A
candidate that is ABSENT from the artifact is reported in its own bucket -- never
silently treated as obscure. That bucket matters: an absent candidate was dropped by
the special-purpose filter, the mutual-kNN cap or the component prune, and "how many of
a superstar's obscure candidates were dropped entirely" is part of the answer, not noise.

CURRENCY. `pop_pctl` is computed by ranking `pop_raw` over the artifact. `pop_raw` is
never read as a rank (CLAUDE.md; log SS2.12).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/cs_p0c_candidates.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "src"))

ARCHIVE = ROOT / "builder" / "scratch" / "graph-archive"
GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
OUT = HERE / "cs_p0c_candidates.json"

SUPERSTARS = ("Radiohead", "The Beatles", "Metallica", "Muse", "Coldplay")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    sorted_values = values[order]
    start = 0
    for end in range(1, len(sorted_values) + 1):
        if end == len(sorted_values) or sorted_values[end] != sorted_values[start]:
            if end - start > 1:
                ranks[order[start:end]] = ranks[order[start:end]].mean()
            start = end
    return ranks / max(1, len(values) - 1)


def main() -> int:
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print(f"ARTIFACT MISMATCH\n expected {EXPECT}\n actual {actual}", file=sys.stderr)
        return 2
    if not ARCHIVE.is_dir():
        print(f"MISSING ARCHIVE: {ARCHIVE}", file=sys.stderr)
        return 2

    from artistpath_api.graph_store import GraphStore
    from artistpath_builder.archive import LocalArchive
    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.sources.listenbrainz import ListenBrainzSource

    graph = GraphStore.load(GRAPH)
    pop_pctl = percentile_ranks(np.asarray(graph.pop_raw, dtype=np.float64))
    id_of = {m: i for i, m in enumerate(graph.mbids)}
    names = list(graph.names)
    by_name: dict[str, int] = {}
    for i, name in enumerate(names):
        by_name.setdefault(name, i)

    archive = LocalArchive(ARCHIVE)
    config = BuilderConfig()
    source = ListenBrainzSource(config)
    prefix = f"similar/{source.name}/"

    def candidates_of(mbid: str):
        payload = archive.get(f"{prefix}{mbid}.json")
        if payload is None:
            return None
        return source.parse(payload, exclude_mbid=mbid)

    def profile(node: int) -> dict[str, object]:
        mbid = graph.mbids[node]
        cand = candidates_of(mbid)
        if cand is None:
            return {"name": names[node], "archived": False}
        in_artifact_pctl: list[float] = []
        absent = 0
        for neighbour in cand:
            j = id_of.get(neighbour.mbid)
            if j is None:
                absent += 1
            else:
                in_artifact_pctl.append(float(pop_pctl[j]))
        arr = np.array(in_artifact_pctl, dtype=np.float64)
        start, end = int(graph.offsets[node]), int(graph.offsets[node + 1])
        kept = graph.neighbours[start:end].astype(np.int64)
        return {
            "name": names[node],
            "own_pctl": round(float(pop_pctl[node]), 6),
            "kept_degree": int(end - start),
            "kept_below_top_decile": int((pop_pctl[kept] < 0.90).sum()),
            "candidates_returned": len(cand),
            "candidates_absent_from_artifact": absent,
            "candidates_in_artifact": int(arr.size),
            "candidates_below_top_decile": int((arr < 0.90).sum()),
            "candidates_below_median": int((arr < 0.50).sum()),
            "min_candidate_pctl": round(float(arr.min()), 6) if arr.size else None,
            "example_obscure_candidates": [
                names[id_of[c.mbid]]
                for c in cand
                if c.mbid in id_of and pop_pctl[id_of[c.mbid]] < 0.90
            ][:12],
        }

    report: dict[str, object] = {
        "artifact_sha256": actual,
        "archive": str(ARCHIVE),
        "note": (
            "candidates_* are counted BEFORE cap, symmetrisation and component prune "
            "-- what the crawl offered. 'absent_from_artifact' candidates were dropped "
            "by the special-purpose filter, the cap or the prune."
        ),
        "superstars": [],
    }
    for name in SUPERSTARS:
        node = by_name.get(name)
        report["superstars"].append(
            profile(node) if node is not None else {"name": name, "found": False}
        )
        print(f"  done: {name}", flush=True)

    # Population version over the artifact's top 1% by popularity percentile.
    top1 = np.flatnonzero(pop_pctl >= 0.99)
    print(f"top-1% artists: {len(top1)}", flush=True)
    returned, below, absent_counts, kept_below = [], [], [], []
    for count, node in enumerate(top1, 1):
        if count % 200 == 0:
            print(f"  scanned {count}/{len(top1)}", flush=True)
        mbid = graph.mbids[int(node)]
        cand = candidates_of(mbid)
        if cand is None:
            continue
        pctls, absent = [], 0
        for neighbour in cand:
            j = id_of.get(neighbour.mbid)
            if j is None:
                absent += 1
            else:
                pctls.append(float(pop_pctl[j]))
        arr = np.array(pctls, dtype=np.float64)
        returned.append(len(cand))
        absent_counts.append(absent)
        below.append(int((arr < 0.90).sum()) if arr.size else 0)
        start, end = int(graph.offsets[node]), int(graph.offsets[node + 1])
        kept_below.append(int((pop_pctl[graph.neighbours[start:end].astype(np.int64)] < 0.90).sum()))

    below_arr = np.array(below, dtype=np.float64)
    kept_arr = np.array(kept_below, dtype=np.float64)
    report["top_1pct_population"] = {
        "artists_with_archive": len(returned),
        "mean_candidates_returned": round(float(np.mean(returned)), 3),
        "mean_candidates_absent_from_artifact": round(float(np.mean(absent_counts)), 3),
        "mean_candidates_below_top_decile": round(float(below_arr.mean()), 3),
        "median_candidates_below_top_decile": float(np.median(below_arr)),
        "share_with_zero_obscure_candidates": round(float((below_arr == 0).mean()), 6),
        "mean_KEPT_below_top_decile": round(float(kept_arr.mean()), 3),
        "discard_ratio_obscure": (
            round(float(1 - kept_arr.sum() / below_arr.sum()), 6)
            if below_arr.sum() else None
        ),
    }

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
