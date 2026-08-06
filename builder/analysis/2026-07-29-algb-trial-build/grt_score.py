"""GRT scoring: build both arms and evaluate the pre-registered reads.

Governing document:
docs/superpowers/specs/2026-07-29-algb-trial-build-preregistration.md

Committed before any result exists. Separate from collection so it can be
re-run without re-hitting the service.

Reads, each with its threshold taken from artistpath_builder.acceptance rather
than retyped (a transcribed threshold is a threshold that drifts):

    GRT-G2  arm integrity      >= 95% of discovered artists fetched
    GRT-G3  readability        per-read; a read whose subject is not in the
                               readable core is VOID, never a result
    GRT-C1  R.E.M. degree      vs famous_min_degree_floor (8)
    GRT-C2  canonical names    absent from AB but present in A0
    GRT-C3  top-25 degrees     median vs 25.0, min vs 8, BOTH arms side by side
    GRT-C4  component membership, as a RATE, stratified by fame band  [PRIMARY]

Why cmd_build is bypassed: a capped 3,000-node graph cannot satisfy
PRODUCTION_ACCEPTANCE's node_count of 60,000-90,000, so it would refuse both
arms for a reason that has nothing to do with the algorithm. There is
deliberately no CLI escape hatch, so the clauses are evaluated individually.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

from artistpath_builder.acceptance import PRODUCTION_ACCEPTANCE as ACC
from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import deserialise
from artistpath_builder.config import (
    PERMITTED_ALGORITHMS,
    PRODUCTION_ALGORITHM,
    BuilderConfig,
)
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

ALG_B = PERMITTED_ALGORITHMS[1]
TARGET = 3_000
MIN_BAND_MEMBERS = 30  # RC-G2: an under-populated band is not read.
STRANDING_BAR = 2.0    # GRT-C4 effect size: >= 2x A0's rate is material.

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"
PRODUCTION_ARCHIVE = SCRATCH / "graph-archive"

# The popularity ruler and the fame-band frame. Percentile RANK over the
# adopted artifact (pop_pctl convention); pop_raw is a value, never a rank.
ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

BANDS = (
    ("top 0.1%", 0.999, 1.0001),
    ("top 1%", 0.99, 0.999),
    ("top 10%", 0.90, 0.99),
    ("upper half", 0.50, 0.90),
    ("lower half", 0.0, 0.50),
)


def _ruler() -> dict[str, float]:
    """mbid -> popularity percentile rank on the ADOPTED artifact."""
    payload = ADOPTED.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != ADOPTED_SHA:
        raise SystemExit(f"adopted artifact mismatch: {actual} != {ADOPTED_SHA}")
    graph = deserialise(payload)
    pop = np.asarray(graph.pop_raw, dtype=np.float64)
    order = pop.argsort(kind="stable")
    pctl = np.empty_like(pop)
    pctl[order] = np.arange(len(pop)) / (len(pop) - 1)
    return {mbid: float(pctl[i]) for i, mbid in enumerate(graph.mbids)}


def _band(pctl: float | None) -> str | None:
    if pctl is None:
        return None
    for name, low, high in BANDS:
        if low <= pctl < high:
            return name
    return None


class SubsetArchive:
    """An archive view restricted to one arm's own crawled artists.

    Necessary, and its absence was a real defect caught by a dry run on A0
    before AB finished collecting. `build_from_archive` reads EVERY key under
    its prefix, so pointing the control arm at the production archive built
    the whole 74,157-node graph rather than the 3,000-node capped one — which
    destroys the coverage matching the control exists to provide, and made two
    derived figures visibly impossible (a negative exclusion rate and a fetch
    rate above 1).

    Applied to BOTH arms so they are symmetric. For AB it is a near no-op,
    since that archive holds only AB's crawl; for A0 it is what makes the arm
    a control at all.
    """

    def __init__(self, inner, allowed_mbids: set[str], prefix: str) -> None:
        self._inner = inner
        self._allowed = allowed_mbids
        self._prefix = prefix

    def _permitted(self, key: str) -> bool:
        if not key.startswith(self._prefix) or not key.endswith(".json"):
            return False
        mbid = key[len(self._prefix) : -len(".json")]
        return "/" not in mbid and mbid in self._allowed

    def put(self, key: str, payload: bytes) -> None:
        raise RuntimeError("SubsetArchive is read-only")

    def get(self, key: str):
        return self._inner.get(key) if self._permitted(key) else None

    def has(self, key: str) -> bool:
        return self._permitted(key) and self._inner.has(key)

    def keys(self):
        for key in self._inner.keys():
            if self._permitted(key):
                yield key


def _arm_config(arm: str) -> tuple[BuilderConfig, object]:
    """Config plus an archive view holding ONLY this arm's crawled artists."""
    fetched = _fetched_mbids(arm)
    # Era-pinned in both arms. This probe predates the no-release drop adopted
    # 2026-08-01 AND the featured-credit filter (2026-08-03) AND the
    # un-listenable filter (2026-08-05, ULF-); its GRT-P4 anchors were
    # produced without any of them, and Track B reproduces them. Left at the
    # defaults, a re-run would build cleaned graphs and disagree with the
    # record. See builder/analysis/README.md.
    # Era pin 2026-08-06 (MSW- adoption): cap_strategy and require_fame both
    # flipped at that adoption. This probe's GRT-P4 anchors were built under
    # mutual k-NN with no fame stage, and its archives have never had `fame`
    # run against them — so left at the new defaults a re-run would build a
    # different cap AND refuse outright on missing fame coverage.
    if arm == "AB":
        cfg = BuilderConfig(
            algorithm=ALG_B,
            target_artist_count=TARGET,
            drop_no_release_tail=False,
            drop_featured_credit=False,
            drop_unlistenable=False,
            cap_strategy="mutual_knn",
            require_fame=False,
        )
        base = LocalArchive(SCRATCH / "grt-archive-algb")
        prefix = f"similar/listenbrainz/{ALG_B}/"
    else:
        cfg = BuilderConfig(
            algorithm=PRODUCTION_ALGORITHM,
            target_artist_count=TARGET,
            drop_no_release_tail=False,
            drop_featured_credit=False,
            drop_unlistenable=False,
            cap_strategy="mutual_knn",
            require_fame=False,
        )
        base = OverlayReader(
            LocalArchive(PRODUCTION_ARCHIVE), LocalArchive(SCRATCH / "grt-overlay-alge")
        )
        prefix = "similar/listenbrainz/"
    return cfg, SubsetArchive(base, fetched, prefix)


class OverlayReader:
    """Read-only twin of grt_run.OverlayArchive, so scoring sees the same
    responses collection did — production plus the 5 overlay fetches."""

    def __init__(self, base, overlay) -> None:
        self._base, self._overlay = base, overlay

    def put(self, key: str, payload: bytes) -> None:
        raise RuntimeError("OverlayReader is read-only")

    def get(self, key: str):
        found = self._base.get(key)
        return found if found is not None else self._overlay.get(key)

    def has(self, key: str) -> bool:
        return self._base.has(key) or self._overlay.has(key)

    def keys(self):
        seen = set()
        for k in self._base.keys():
            seen.add(k)
            yield k
        for k in self._overlay.keys():
            if k not in seen:
                yield k


def _fetched_mbids(arm: str) -> set[str]:
    """Artists whose OWN response this arm holds — the crawl's `done` set."""
    checkpoint = SCRATCH / (
        "grt-checkpoint-algb.json" if arm == "AB" else "grt-checkpoint-alge.json"
    )
    return set(json.loads(checkpoint.read_text())["done"])


def _arm_payloads(cfg: BuilderConfig, archive, source) -> dict[str, bytes]:
    """The archived responses this arm's build will actually read.

    build_from_archive returns only the pruned graph, so the pre-prune
    population — the denominator of every exclusion rate below — is not
    recoverable from its output. This selects keys by exactly the rule the
    pipeline uses (GR-3's algorithm scoping), so the two cannot diverge
    silently.
    """
    prefix = (
        f"similar/{source.name}/"
        if cfg.algorithm == PRODUCTION_ALGORITHM
        else f"similar/{source.name}/{cfg.algorithm}/"
    )
    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix) : -len(".json")]
        if "/" in mbid:
            continue
        blob = archive.get(key)
        if blob is not None:
            payloads[mbid] = blob
    return payloads


def score_arm(arm: str, ruler: dict[str, float]) -> dict:
    cfg, archive = _arm_config(arm)
    source = ListenBrainzSource(cfg)

    graph = build_from_archive(cfg, archive, source)
    degrees = np.diff(graph.offsets).astype(np.int64)
    by_mbid = {mbid: int(degrees[i]) for i, mbid in enumerate(graph.mbids)}
    name_to_mbid = {name: graph.mbids[i] for i, name in enumerate(graph.names)}

    fetched = _fetched_mbids(arm)
    # The archive view is already restricted to this arm's crawl (see
    # SubsetArchive), so the population is exactly what the build read.
    payloads = _arm_payloads(cfg, archive, source)
    population = set(payloads)

    # --- GRT-G3 readable core -------------------------------------------
    # An artist is READABLE when every one of its own top-k candidates was
    # also fetched, so its degree is decided by the data rather than by where
    # the crawl stopped.
    readable: set[str] = set()
    for mbid in population:
        try:
            cands = [n.mbid for n in source.parse(payloads[mbid], exclude_mbid=mbid)]
        except ValueError:
            continue
        top = cands[: cfg.max_neighbours_per_artist]
        if top and all(c in fetched for c in top):
            readable.add(mbid)

    # --- GRT-C4 component membership, as a rate, per band ---------------
    in_component = set(graph.mbids)
    per_band: dict[str, dict] = {}
    band_members: dict[str, list[str]] = defaultdict(list)
    for mbid in readable:
        band = _band(ruler.get(mbid))
        if band:
            band_members[band].append(mbid)
    for band, _low, _high in [(b[0], b[1], b[2]) for b in BANDS]:
        members = band_members.get(band, [])
        if len(members) < MIN_BAND_MEMBERS:
            per_band[band] = {
                "readable_members": len(members),
                "read": False,
                "reason": f"under-populated (< {MIN_BAND_MEMBERS}); RC-G2 refuses to pool",
            }
            continue
        excluded = [m for m in members if m not in in_component]
        per_band[band] = {
            "readable_members": len(members),
            "read": True,
            "excluded": len(excluded),
            "exclusion_rate": round(len(excluded) / len(members), 5),
        }

    # --- GRT-C1 / C2 / C3 ------------------------------------------------
    rem_mbid = name_to_mbid.get("R.E.M.")
    grt_c1 = {
        "subject": "R.E.M.",
        "in_graph": rem_mbid is not None,
        "readable": rem_mbid in readable if rem_mbid else False,
    }
    if rem_mbid is None:
        # Absent from the built graph. Two very different causes, and the
        # read is only meaningful for the second: never fetched at all
        # (coverage artifact of the 3,000 cap) versus fetched but pruned out
        # (an algorithm effect, and RC-P2's actual prediction).
        rem_known = "ea4dfa26-f633-4da6-a52a-f49ea4897b58"
        grt_c1["fetched"] = rem_known in fetched
        grt_c1["verdict"] = (
            "CONFIRMS RC-P2 (fetched, then pruned out of the component)"
            if rem_known in fetched
            else "VOID — R.E.M. never fetched at this target (coverage, not algorithm)"
        )
    elif not grt_c1["readable"]:
        grt_c1["verdict"] = "VOID — R.E.M. not in the readable core (GRT-G3)"
    else:
        deg = by_mbid[rem_mbid]
        grt_c1["degree"] = deg
        grt_c1["floor"] = ACC.famous_min_degree_floor
        grt_c1["verdict"] = (
            "CONFIRMS RC-P2 (below floor)"
            if deg < ACC.famous_min_degree_floor
            else "REFUTES RC-P2 (at or above floor)"
        )

    present_names = set(graph.names)
    grt_c2 = {
        "absent": sorted(n for n in ACC.canonical_names if n not in present_names),
        "present": sum(1 for n in ACC.canonical_names if n in present_names),
        "of": len(ACC.canonical_names),
    }

    pop_order = np.argsort(-np.asarray(graph.pop_raw, dtype=np.float64), kind="stable")
    top = degrees[pop_order[: ACC.famous_sample]]
    grt_c3 = {
        "sample": ACC.famous_sample,
        "median_degree": float(statistics.median(top.tolist())),
        "median_floor": ACC.famous_median_degree_floor,
        "median_passes": statistics.median(top.tolist()) >= ACC.famous_median_degree_floor,
        "min_degree": int(top.min()),
        "min_floor": ACC.famous_min_degree_floor,
        "min_passes": int(top.min()) >= ACC.famous_min_degree_floor,
        "worst_artist": graph.names[int(pop_order[: ACC.famous_sample][int(np.argmin(top))])],
        "all_readable": all(
            graph.mbids[int(i)] in readable for i in pop_order[: ACC.famous_sample]
        ),
    }

    return {
        "arm": arm,
        "algorithm": cfg.algorithm,
        "built_nodes": graph.artist_count,
        "built_edges": graph.edge_count,
        "pre_prune_population": len(population),
        "fetched": len(fetched),
        "readable_core": len(readable),
        # GRT-G2: of everything this arm set out to fetch, what share landed.
        # Read from the crawl record, not inferred from the archive.
        "GRT_G2_fetch_rate": round(
            json.loads((HERE / f"grt_crawl_{arm}.json").read_text())["done"]
            / max(1, json.loads((HERE / f"grt_crawl_{arm}.json").read_text())["discovered"]),
            4,
        ),
        "GRT_C1_rem": grt_c1,
        "GRT_C2_canonical": grt_c2,
        "GRT_C3_top25": grt_c3,
        "GRT_C4_component_by_band": per_band,
        "GRT_C4_overall_exclusion_rate": round(
            1 - graph.artist_count / max(1, len(population)), 5
        ),
    }


def main() -> None:
    ruler = _ruler()
    out = {"target": TARGET, "arms": {}}
    for arm in ("A0", "AB"):
        out["arms"][arm] = score_arm(arm, ruler)

    # --- GRT-C4 the comparison the design licenses: AB vs A0 -------------
    comparison = {}
    for band, _low, _high in [(b[0], b[1], b[2]) for b in BANDS]:
        a0 = out["arms"]["A0"]["GRT_C4_component_by_band"].get(band, {})
        ab = out["arms"]["AB"]["GRT_C4_component_by_band"].get(band, {})
        if not (a0.get("read") and ab.get("read")):
            comparison[band] = {"read": False, "reason": "a band unread in one or both arms"}
            continue
        base, trial = a0["exclusion_rate"], ab["exclusion_rate"]
        ratio = (trial / base) if base > 0 else None
        comparison[band] = {
            "read": True,
            "A0_exclusion_rate": base,
            "AB_exclusion_rate": trial,
            "ratio": round(ratio, 3) if ratio is not None else None,
            "bar": STRANDING_BAR,
            "verdict": (
                "DECISIVE — material stranding"
                if ratio is not None and ratio >= STRANDING_BAR
                else "NOT DECISIVE (reported with its figure; not 'no effect')"
            ),
        }
    out["GRT_C4_comparison"] = comparison

    (HERE / "grt_scores.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
