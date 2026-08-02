"""Is a --target-capped trial crawl readable at all? Calibration for AS-H2.

`AS-H2` asks whether `ALG-B` strands more obscure artists than production. The
agreed instrument is a `--target`-capped trial crawl on `ALG-B`, built, so the
stranding question is answered before anyone spends the full re-crawl.

**This script does not measure ALG-B and touches no network.** It measures
whether the *instrument* works, using the production archive alone, and it
exists because a capped crawl has a confound that would otherwise be discovered
after the crawl rather than before it:

    `crawl.py` stops discovering at the cap but keeps fetching everything
    already discovered (`done == discovered == target`, verified against the
    production checkpoint). So every artist IS fetched — but an artist
    processed late has most of its own candidates discovered *after* the cap
    bound, so those candidates were never fetched and cannot be nodes. Under
    mutual k-NN an edge needs both endpoints, so those artists lose edges to
    the crawl's stopping point rather than to anything about the algorithm.

That truncation lands on the outer BFS shell, and **the two arms discover in
different orders**, so the shell differs per arm. It is therefore an
uncontrolled variable that appears only in one arm — the shape `CLAUDE.md`'s
factor table exists to catch.

The proposed fix is to read only on **closed** nodes: an artist all of whose
parsed candidates were themselves fetched. For those, degree-after-mutual-k-NN
is determined by the data, not by where the crawl stopped. This script tests
the two things that fix depends on, both answerable offline:

  Q1  How many closed nodes does a capped crawl at target N leave, and how are
      they spread across popularity? A read set that is large overall but empty
      below the median cannot answer a question about obscure artists.

  Q2  Do closed nodes actually reproduce their production degree? This is the
      validity condition. If a closed node's degree in the trial graph differs
      from its degree in the full 75k build, "closed" does not mean what the
      design claims and the instrument is unfit regardless of Q1.

Both arms of the real comparison run the SAME pipeline, so anything Q2 finds
here is a property of capped crawling itself and applies to both.

Offline by construction: it replays archived responses and injects no fetcher.
Determinism: it reproduces `crawl.py`'s ordering exactly (sorted resume,
bootstrap order, `popleft`, break on cap) — see `_replay`, which is the one
place this script duplicates production logic and says so.

Ruler: popularity strata come from the FULL build's `pop_pctl_full`, a
percentile rank, never from `pop_raw` (a value — log §2.12 records that
conflation). Trial-graph popularity is NOT used as a ruler: in-degree inside a
3,000-node graph is a different quantity from in-degree inside 75,000.

Usage (from builder/):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-trial-crawl-calibration/calibrate.py
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import deque
from collections.abc import Iterator
from pathlib import Path

import numpy as np

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.graph import Graph
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

SCRATCH = Path(__file__).resolve().parents[2] / "scratch"
ARCHIVE_DIR = SCRATCH / "graph-archive"
BOOTSTRAP = SCRATCH / "bootstrap.json"
OUT_DIR = Path(__file__).resolve().parent
FULL_CACHE = OUT_DIR / "full-build-degrees.json"

# Targets to calibrate. The real trial crawl pays ~1 request per artist, so N
# is the cost knob: these bracket "too small to read" and "no longer cheap".
TARGETS = (1_000, 2_000, 3_000, 5_000)

# Popularity bands, as (label, low_pctl, high_pctl) over pop_pctl_full.
# Deliberately stratum-aware: AS-H1 records two reads that did not fire because
# they assumed the bands would agree, so no band is collapsed into another here.
BANDS = (
    ("top 0.1%", 99.9, 100.0),
    ("top 1%", 99.0, 99.9),
    ("top 10%", 90.0, 99.0),
    ("upper half", 50.0, 90.0),
    ("lower half", 0.0, 50.0),
)


class SubsetArchive:
    """Read-only view of an archive restricted to one set of artists.

    Lets `build_from_archive` assemble the graph a capped crawl would have
    produced, through the real pipeline, with no crawl and no network.
    """

    def __init__(self, inner: LocalArchive, prefix: str, allowed: set[str]) -> None:
        self._inner = inner
        self._prefix = prefix
        self._allowed = allowed

    def _permitted(self, key: str) -> bool:
        if not key.startswith(self._prefix) or not key.endswith(".json"):
            return False
        return key[len(self._prefix) : -len(".json")] in self._allowed

    def put(self, key: str, payload: bytes) -> None:  # pragma: no cover
        raise RuntimeError("SubsetArchive is read-only")

    def get(self, key: str) -> bytes | None:
        return self._inner.get(key) if self._permitted(key) else None

    def has(self, key: str) -> bool:
        return self._permitted(key) and self._inner.has(key)

    def keys(self) -> Iterator[str]:
        for key in self._inner.keys():
            if self._permitted(key):
                yield key


def _bootstrap_mbids() -> list[str]:
    data = json.loads(BOOTSTRAP.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for field in ("mbids", "artist_mbids", "artists"):
            if field in data:
                data = data[field]
                break
    return [item if isinstance(item, str) else item["mbid"] for item in data]


def _replay(
    archive: LocalArchive,
    source: ListenBrainzSource,
    bootstrap: list[str],
    target: int,
) -> tuple[set[str], dict[str, list[str]]]:
    """Reproduce `crawl.py`'s BFS against the archive, capped at `target`.

    DUPLICATES production logic on purpose: the whole point is to predict what
    the real crawler would fetch, so the ordering rules must match
    `Crawler.crawl` exactly. Kept in step by hand — if `crawl.py`'s stopping
    rule changes, this is wrong and its answers are void.
    """
    done: set[str] = set()
    discovered: set[str] = set()
    candidates: dict[str, list[str]] = {}
    queue: deque[str] = deque()

    for mbid in bootstrap:
        if mbid not in discovered:
            discovered.add(mbid)
            queue.append(mbid)

    while queue and len(discovered) <= target:
        mbid = queue.popleft()
        if mbid in done:
            continue
        payload = archive.get(f"similar/{source.name}/{mbid}.json")
        if payload is None:
            continue  # never fetched by the production crawl either
        done.add(mbid)
        neighbours = [n.mbid for n in source.parse(payload, exclude_mbid=mbid)]
        candidates[mbid] = neighbours
        for neighbour in neighbours:
            if len(discovered) >= target:
                break
            if neighbour not in discovered:
                discovered.add(neighbour)
                queue.append(neighbour)

    return done, candidates


def _degrees(graph: Graph) -> dict[str, int]:
    counts = np.diff(graph.offsets).astype(np.int64)
    return {mbid: int(counts[i]) for i, mbid in enumerate(graph.mbids)}


def _full_build(config: BuilderConfig, archive: LocalArchive, source) -> dict:
    """Degrees and percentile ruler from the whole archive. Cached: ~2 min."""
    if FULL_CACHE.is_file():
        print(f"full build: reusing {FULL_CACHE.name}", flush=True)
        return json.loads(FULL_CACHE.read_text(encoding="utf-8"))

    print("full build: assembling 75k graph from archive (~2 min)...", flush=True)
    graph = build_from_archive(config, archive, source)
    degrees = _degrees(graph)

    # pop_pctl_full: percentile RANK of pop_raw within the full build. pop_raw
    # is a value and must never be read as a rank (log §2.12).
    order = np.argsort(np.asarray(graph.pop_raw, dtype=np.float64), kind="stable")
    pctl = np.empty(len(order), dtype=np.float64)
    pctl[order] = np.linspace(0.0, 100.0, len(order))
    pop_pctl_full = {mbid: float(pctl[i]) for i, mbid in enumerate(graph.mbids)}

    payload = {
        "artists": graph.artist_count,
        "edges": graph.edge_count,
        "degrees": degrees,
        "pop_pctl_full": pop_pctl_full,
    }
    FULL_CACHE.write_text(json.dumps(payload), encoding="utf-8")
    print(f"full build: {graph.artist_count} artists, {graph.edge_count} edges",
          flush=True)
    return payload


def _band_of(pctl: float) -> str | None:
    """Band containing `pctl`. Half-open [low, high) so bands cannot overlap;
    the top band is closed at 100.0 so the single most popular artist lands
    somewhere rather than being silently dropped."""
    for label, low, high in BANDS:
        in_band = low <= pctl <= high if high == 100.0 else low <= pctl < high
        if in_band:
            return label
    return None


def main() -> int:
    # Era-pinned. This probe predates the no-release drop adopted 2026-08-01,
    # and every figure it committed was produced without it. Left at the
    # default, a re-run would silently build a cleaned graph and disagree with
    # its own record. See builder/analysis/README.md.
    config = BuilderConfig(drop_no_release_tail=False)
    archive = LocalArchive(ARCHIVE_DIR)
    source = ListenBrainzSource(config)
    prefix = f"similar/{source.name}/"

    if not ARCHIVE_DIR.is_dir():
        print(f"archive not found: {ARCHIVE_DIR}", file=sys.stderr)
        return 1

    full = _full_build(config, archive, source)
    full_degrees: dict[str, int] = full["degrees"]
    pop_pctl_full: dict[str, float] = full["pop_pctl_full"]

    bootstrap = _bootstrap_mbids()
    print(f"bootstrap: {len(bootstrap)} seed artists", flush=True)

    results = []
    for target in TARGETS:
        done, candidates = _replay(archive, source, bootstrap, target)
        closed = {
            mbid
            for mbid, neighbours in candidates.items()
            if all(n in done for n in neighbours)
        }

        trial = build_from_archive(
            config, SubsetArchive(archive, prefix, done), source
        )
        trial_degrees = _degrees(trial)

        # Q2: closed nodes that survived into the trial graph, compared with
        # the same artist's degree in the full build.
        comparable = [m for m in sorted(closed) if m in trial_degrees
                      and m in full_degrees]
        deltas = [trial_degrees[m] - full_degrees[m] for m in comparable]
        exact = sum(1 for d in deltas if d == 0)

        # Q1: where the closed read set sits in popularity.
        per_band: dict[str, int] = {label: 0 for label, _l, _h in BANDS}
        unrulered = 0
        for mbid in comparable:
            pctl = pop_pctl_full.get(mbid)
            if pctl is None:
                unrulered += 1
                continue
            band = _band_of(pctl)
            if band:
                per_band[band] += 1

        row = {
            "target": target,
            "fetched": len(done),
            "trial_nodes": trial.artist_count,
            "trial_edges": trial.edge_count,
            "closed": len(closed),
            "closed_in_trial_graph": len(comparable),
            "degree_exact_match": exact,
            "degree_delta_median": statistics.median(deltas) if deltas else None,
            "degree_delta_mean": (
                round(statistics.mean(deltas), 3) if deltas else None
            ),
            "degree_delta_min": min(deltas) if deltas else None,
            "degree_delta_max": max(deltas) if deltas else None,
            "closed_by_band": per_band,
            "closed_without_ruler": unrulered,
        }
        results.append(row)
        print(
            f"target {target:>5}: fetched {len(done):>5} | trial nodes "
            f"{trial.artist_count:>5} edges {trial.edge_count:>6} | closed "
            f"{len(closed):>4} (readable {len(comparable):>4}) | degree exact "
            f"{exact}/{len(comparable)}",
            flush=True,
        )
        print(f"                bands: {per_band}", flush=True)

    out = OUT_DIR / "calibration-results.json"
    out.write_text(
        json.dumps(
            {
                "archive": str(ARCHIVE_DIR),
                "full_build": {"artists": full["artists"], "edges": full["edges"]},
                "config_algorithm": config.algorithm,
                "targets": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nwrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
