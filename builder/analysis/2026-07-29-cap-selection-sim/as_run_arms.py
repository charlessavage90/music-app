"""AS runner -- fetches the six permitted algorithms over the stratified sample.

Governed by `docs/superpowers/specs/2026-07-29-algorithm-selection-preregistration.md`,
committed before this ran. This script COLLECTS ONLY. It computes no criterion and
makes no comparison; `as_score.py` does that from the raw records this writes, so the
scoring can be re-run and independently reviewed without re-hitting the service.

Network: 200 artists x 6 arms = 1,200 read-only GETs, rate limited. Nothing is written
to the archive -- `build` stays offline and the replay test still proves it.

Design clauses this implements, by number:
  SS1.2  requests are INTERLEAVED BY ARTIST across arms, never arm-by-arm, so any drift
         in the service hits all six arms equally.
  SS2    200 artists, 40 per stratum, fixed seed, drawn from the adopted artifact.
  SS1.5  raw scores are recorded per arm but never compared across arms downstream.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/as_run_arms.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
OUT = HERE / "as_raw_records.json"

ENDPOINT = "https://labs.api.listenbrainz.org/similar-artists/json"
SEED = 20260729  # SS2 -- recorded so the draw is reproducible (design SS9)
PER_STRATUM = 40
PAUSE_SECONDS = 0.4  # ~2.5 req/s; the crawler's own configured rate is 5/s

# SS1 factor table. Keys are the arm identifiers used throughout the pre-registration.
ARMS = {
    "ALG-E": "session_based_days_7500_session_300_contribution_5_threshold_10_limit_100_filter_True_skip_30",
    "ALG-B": "session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30",
    "ALG-A": "session_based_days_1825_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30",
    "ALG-F": "session_based_days_1800_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30",
    "ALG-D": "session_based_days_75_session_300_contribution_5_threshold_10_limit_100_filter_True_skip_30",
    "ALG-C": "session_based_days_9000_session_300_contribution_5_threshold_15_limit_50_skip_30",
}

# SS2 strata, as percentile bounds on the adopted artifact's popularity ranking.
STRATA = (
    ("top_0.1pct", 0.999, 1.0001),
    ("top_1pct_below_0.1pct", 0.99, 0.999),
    ("top_decile_below_1pct", 0.90, 0.99),
    ("pctl_50_to_90", 0.50, 0.90),
    ("below_median", 0.0, 0.50),
)


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


def fetch(mbid: str, algorithm: str) -> tuple[int, bytes]:
    query = urlencode({"artist_mbids": mbid, "algorithm": algorithm})
    request = urllib.request.Request(
        f"{ENDPOINT}?{query}",
        headers={"User-Agent": "artistpath-analysis/1.0 (AS algorithm selection)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except Exception as exc:  # noqa: BLE001 -- recorded, never silently retried
        return -1, repr(exc).encode()
    finally:
        time.sleep(PAUSE_SECONDS)


def main() -> int:
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print("ARTIFACT MISMATCH -- refusing to run", file=sys.stderr)
        return 2

    from artistpath_api.graph_store import GraphStore
    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.sources.listenbrainz import ListenBrainzSource

    graph = GraphStore.load(GRAPH)
    pop_pctl = percentile_ranks(np.asarray(graph.pop_raw, dtype=np.float64))
    source = ListenBrainzSource(BuilderConfig())

    rng = np.random.default_rng(SEED)
    sample: list[tuple[str, int]] = []
    for label, low, high in STRATA:
        ids = np.flatnonzero((pop_pctl >= low) & (pop_pctl < high))
        take = min(PER_STRATUM, len(ids))
        chosen = rng.choice(ids, size=take, replace=False)
        sample.extend((label, int(node)) for node in chosen)
        print(f"stratum {label:24s} population={len(ids):6d} drawn={take}", flush=True)

    print(f"\nsample: {len(sample)} artists x {len(ARMS)} arms = "
          f"{len(sample) * len(ARMS)} requests\n", flush=True)

    records = []
    total = len(sample) * len(ARMS)
    done = 0
    started = time.time()
    for stratum, node in sample:  # SS1.2 -- interleaved by artist
        mbid = graph.mbids[node]
        for arm, algorithm in ARMS.items():
            status, body = fetch(mbid, algorithm)
            done += 1
            entry: dict[str, object] = {
                "arm": arm,
                "stratum": stratum,
                "mbid": mbid,
                "name": graph.names[node],
                "own_pctl": round(float(pop_pctl[node]), 6),
                "status": status,
            }
            if status == 200:
                try:
                    neighbours = source.parse(body, exclude_mbid=mbid)
                    entry["candidates"] = [
                        {"mbid": n.mbid, "score": n.score} for n in neighbours
                    ]
                except Exception as exc:  # noqa: BLE001 -- loud
                    entry["parse_error"] = repr(exc)
            else:
                entry["body_head"] = body.decode("utf-8", "replace")[:200]
            records.append(entry)
            if done % 60 == 0:
                rate = done / max(1e-9, time.time() - started)
                print(f"  {done}/{total}  ({rate:.1f} req/s, "
                      f"~{(total - done) / max(rate, 1e-9) / 60:.1f} min left)",
                      flush=True)

    payload = {
        "artifact_sha256": actual,
        "endpoint": ENDPOINT,
        "seed": SEED,
        "per_stratum": PER_STRATUM,
        "arms": ARMS,
        "interleaved_by_artist": True,
        "records": records,
    }
    OUT.write_text(json.dumps(payload), encoding="utf-8")
    print(f"\nwritten: {OUT}  ({OUT.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
