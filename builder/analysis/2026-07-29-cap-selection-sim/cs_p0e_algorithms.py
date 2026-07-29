"""CS-P0e -- VALIDATE the owner's constraint: which `algorithm` values the source accepts,
and what each one actually returns for a superstar.

NETWORK PROBE. Read-only GETs against the public ListenBrainz Labs endpoint, rate
limited, a handful of requests. This is NOT a crawl and writes nothing to the archive.
`build` remains offline -- that hard rule is untouched (the replay test still proves it).

WHY THIS MATTERS MORE THAN ANYTHING ELSE MEASURED TODAY. CS-P0c found superstars are
offered zero sub-decile candidates within the 100 the crawl requested, and CS-P0d found
famous artists' lists saturate that limit of 100. The remedy that followed -- "re-crawl
asking for longer lists" -- was flagged as the load-bearing UNMEASURED assumption of the
whole rebuild.

The owner's research says that remedy may not exist: the `algorithm` parameter is
claimed to accept only a fixed set of values, whose `limit` is 100 or 50 and never more.
If that is true then:

  * there is no longer list to ask for, at any price;
  * our threshold is already 10, the lower of the two available, so STC-6's
    "lower the co-occurrence threshold" lever has nowhere to go either;
  * and the famous-pair defect cannot be fixed by re-crawling THIS source at all.

That is a hard constraint on the rebuild plan, so it gets validated rather than assumed.

WHAT THIS CHECKS
  (1) The rejection message, from a deliberately invalid algorithm string -- the claimed
      list of accepted values, read from the source rather than from a forum.
  (2) For each accepted value: how many candidates come back for the five superstars,
      and how many are below the 90th popularity percentile of the ADOPTED artifact.
      Same currency as CS-P0c so the numbers are comparable to it.

CURRENCY. Percentiles come from the adopted artifact (sha256 asserted). A returned
candidate absent from the artifact is counted separately, never assumed obscure.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/cs_p0e_algorithms.py
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
OUT = HERE / "cs_p0e_algorithms.json"

ENDPOINT = "https://labs.api.listenbrainz.org/similar-artists/json"
PRODUCTION_ALGORITHM = (
    "session_based_days_7500_session_300_contribution_5"
    "_threshold_10_limit_100_filter_True_skip_30"
)
# The six values the owner's testing reported as accepted. Validated here, not assumed.
CLAIMED = (
    "session_based_days_1825_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30",
    "session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30",
    "session_based_days_9000_session_300_contribution_5_threshold_15_limit_50_skip_30",
    "session_based_days_75_session_300_contribution_5_threshold_10_limit_100_filter_True_skip_30",
    "session_based_days_7500_session_300_contribution_5_threshold_10_limit_100_filter_True_skip_30",
    "session_based_days_1800_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30",
)
# Probes for the question the claimed list implies but does not state: is `limit`
# genuinely un-raisable, or is the list merely a set of PRESETS?
INVENTED = (
    "session_based_days_7500_session_300_contribution_5_threshold_10_limit_500_filter_True_skip_30",
    "session_based_days_7500_session_300_contribution_5_threshold_5_limit_100_filter_True_skip_30",
    "definitely_not_a_real_algorithm",
)

SUPERSTARS = ("Radiohead", "The Beatles", "Metallica", "Muse", "Coldplay")
PAUSE_SECONDS = 1.5  # deliberate: this is someone else's free service


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
        headers={"User-Agent": "artistpath-analysis/1.0 (cap-selection scope probe)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    finally:
        time.sleep(PAUSE_SECONDS)


def main() -> int:
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print("ARTIFACT MISMATCH", file=sys.stderr)
        return 2

    from artistpath_api.graph_store import GraphStore
    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.sources.listenbrainz import ListenBrainzSource

    graph = GraphStore.load(GRAPH)
    pop_pctl = percentile_ranks(np.asarray(graph.pop_raw, dtype=np.float64))
    id_of = {m: i for i, m in enumerate(graph.mbids)}
    names = list(graph.names)
    by_name: dict[str, int] = {}
    for i, name in enumerate(names):
        by_name.setdefault(name, i)
    source = ListenBrainzSource(BuilderConfig())

    report: dict[str, object] = {
        "artifact_sha256": actual,
        "endpoint": ENDPOINT,
        "production_algorithm": PRODUCTION_ALGORITHM,
        "url_shape_confirmed": f"{ENDPOINT}?artist_mbids=<mbid>&algorithm=<algorithm>",
    }

    # (1) Rejection message -- read the accepted list from the source itself.
    radiohead = by_name.get("Radiohead")
    if radiohead is None:
        print("Radiohead not in artifact", file=sys.stderr)
        return 2
    rh_mbid = graph.mbids[radiohead]
    report["radiohead_mbid"] = rh_mbid

    probes = []
    for algorithm in INVENTED:
        status, body = fetch(rh_mbid, algorithm)
        text = body.decode("utf-8", errors="replace")
        probes.append({
            "algorithm": algorithm,
            "status": status,
            "body_head": text[:1200],
        })
        print(f"  probe {algorithm[:60]}... -> {status}", flush=True)
    report["invalid_value_probes"] = probes

    # (2) Each claimed-accepted value, on every superstar.
    results = []
    for algorithm in CLAIMED:
        per_artist = []
        accepted = None
        for name in SUPERSTARS:
            node = by_name.get(name)
            if node is None:
                continue
            status, body = fetch(graph.mbids[node], algorithm)
            if status != 200:
                accepted = False
                per_artist.append({"name": name, "status": status,
                                   "body_head": body.decode("utf-8", "replace")[:300]})
                continue
            accepted = True if accepted is None else accepted
            try:
                neighbours = source.parse(body, exclude_mbid=graph.mbids[node])
            except Exception as exc:  # noqa: BLE001 -- loud, not swallowed
                per_artist.append({"name": name, "parse_error": repr(exc)})
                continue
            pctls, absent = [], 0
            for neighbour in neighbours:
                j = id_of.get(neighbour.mbid)
                if j is None:
                    absent += 1
                else:
                    pctls.append(float(pop_pctl[j]))
            arr = np.array(pctls, dtype=np.float64)
            per_artist.append({
                "name": name,
                "status": status,
                "returned": len(neighbours),
                "absent_from_artifact": absent,
                "below_top_decile": int((arr < 0.90).sum()) if arr.size else 0,
                "below_median": int((arr < 0.50).sum()) if arr.size else 0,
                "min_candidate_pctl": round(float(arr.min()), 6) if arr.size else None,
            })
            print(f"  {algorithm[:48]}... {name}: "
                  f"{len(neighbours)} returned, "
                  f"{int((arr < 0.90).sum()) if arr.size else 0} sub-decile", flush=True)
        results.append({"algorithm": algorithm, "accepted": accepted,
                        "artists": per_artist})
    report["claimed_algorithms"] = results

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
