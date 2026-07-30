"""CB-1: build one graph per (archive, cap rule, parameters) cell.

Governing plan: docs/superpowers/plans/2026-07-30-graph-rebuild-track-b.md
Scope rulings (§0 there): this is cap-RULE selection, not k-tuning. The degree
bound is a scoping constraint of THIS track, not a settled product conclusion.
The `uncapped` rule is a DESCRIPTIVE REFERENCE ROW, barred from selection.

Analysis only. Nothing here writes to builder/src, changes a default, or adopts
anything. Both archives are opened through ReadOnlyArchive, whose put() raises
(GRT-A1: the production archive is irreplaceable, and the ALG-B archive cost
7.6 hours).

WHAT IS IMPORTED RATHER THAN REIMPLEMENTED
  damped_strength, rescale_scores  (pipeline)
  harvest_identities, is_special_purpose
  mutual_knn_cap, symmetrise, largest_component, build_graph  (graph)
  serialise  (artifact)
Only the STAGE ORDER is restated here, because build_from_archive has no seam
to inject a different cap step into. `_assemble` mirrors it exactly; the
identity gate below is what proves the mirror is faithful rather than merely
believed.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-track-b-cap-selection/cb_build_variants.py --gate
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import time
from collections import defaultdict
from pathlib import Path

from artistpath_builder.archive import LocalArchive, RawArchive
from artistpath_builder.artifact import serialise
from artistpath_builder.config import PERMITTED_ALGORITHMS, PRODUCTION_ALGORITHM, BuilderConfig
from artistpath_builder.graph import (
    Adjacency,
    Graph,
    build_graph,
    largest_component,
    mutual_knn_cap,
    symmetrise,
)
from artistpath_builder.models import ArtistStats
from artistpath_builder.pipeline import (
    damped_strength,
    is_special_purpose,
    rescale_scores,
)
from artistpath_builder.sources.listenbrainz import ListenBrainzSource, harvest_identities

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"
CELLS = SCRATCH / "cb-cells"

ALG_B = PERMITTED_ALGORITHMS[1]

ARCHIVES = {
    "ALG-E": SCRATCH / "graph-archive",
    "ALG-B": SCRATCH / "grt-archive-algb",
}
ALGORITHMS = {"ALG-E": PRODUCTION_ALGORITHM, "ALG-B": ALG_B}

# Reference builds the instrument gate reproduces. Values read from each
# build's committed manifest sidecar; the execution log §7b owns them in prose.
REFERENCE = {
    "ALG-E": {
        "sha256": "73feffa03856f55dda134b84aa5ee40073495ae16f27e8116a4d961b65a69faa",
        "artists": 74_157,
        "edges": 897_620,
    },
    "ALG-B": {
        "sha256": "d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f",
        "artists": 68_467,
        "edges": 811_784,
    },
}


class ArchiveWriteRefused(RuntimeError):
    """Something tried to write into a read-only archive."""


class ReadOnlyArchive:
    """Wraps an archive and refuses every write (GRT-A1).

    This harness only ever reads, so unlike grt_run.py's overlay there is
    nowhere for a write to legitimately go: put() firing here is a bug in this
    module, not a finding about coverage.
    """

    def __init__(self, inner: RawArchive) -> None:
        self._inner = inner

    def put(self, key: str, payload: bytes) -> None:
        raise ArchiveWriteRefused(
            f"cap-selection harness tried to write {key!r}. It is read-only by "
            "design; do not relax this guard."
        )

    def get(self, key: str):
        return self._inner.get(key)

    def has(self, key: str) -> bool:
        return self._inner.has(key)

    def keys(self):
        return self._inner.keys()


# --------------------------------------------------------------------------
# Cap rules. Each takes (adjacency, ranking, pop) and returns a new adjacency.
#
# `ranking` holds UNCLIPPED strengths (Phase 1 §2.8: the p99 clip ties the top
# ~1% at exactly 1.0, and ranking tied values lets the MBID tie-break decide
# which neighbours a saturated artist keeps). `pop` is log-scaled
# score-weighted in-degree, computed BEFORE any cap and therefore identical
# across every rule cell within an archive.
#
# Every rule states its bound in its docstring, per §0 ruling 2.
# --------------------------------------------------------------------------


def cap_mutual_knn(adjacency: Adjacency, ranking: Adjacency, pop: dict[str, float],
                   *, k: int) -> Adjacency:
    """Incumbent. Edge (u,v) survives iff v is in u's top-k AND u in v's top-k.

    BOUND: degree <= k by construction. Delegates to the shipped function
    unchanged, so the k=50 cell is production's own code path.
    """
    return mutual_knn_cap(adjacency, k, ranking=ranking)


def _top_j(ranking: Adjacency, adjacency: Adjacency, j: int,
           key) -> dict[str, set[str]]:
    """Each node's top-j neighbours under `key`. Ties break on lowest MBID."""
    chosen: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(edges, key=lambda dst: key(node, dst))
        chosen[node] = set(ranked[:j])
    return chosen


def cap_trimmed_union(adjacency: Adjacency, ranking: Adjacency,
                      pop: dict[str, float], *, j: int, d: int,
                      trim: str = "weakest_first",
                      quota: float = 0.2) -> Adjacency:
    """Non-reciprocal: top-j UNION, then a hard degree ceiling of d.

    Union alone bounds nothing (a famous artist appears in unboundedly many
    lists), which is exactly the defect that killed the pre-symmetrise cap --
    configured 50, observed max degree 11,243. The ceiling is what bounds it,
    and it is applied by deleting WHOLE EDGES rather than truncating one
    endpoint's row, because per-node truncation breaks symmetry again.

    BOUND: degree <= d by construction. Single pass suffices: nodes are
    processed in a fixed order and deletion only ever lowers a degree, so a
    node brought to d cannot later rise above it.

    THE TRIM KEY IS NOT A DETAIL -- it decides whether this family can bear on
    DD-F1 at all (CB-P1, consultant item 2 validated 2026-07-30):

      weakest_first   Delete lowest pair-strength first. By CS-P0f symmetry +
                      the source's 100-cap, every reverse-ONLY edge at a
                      superstar scores below its own list's tail, so this trim
                      provably deletes ALL union-added famous->obscure edges
                      wherever the node's own list supplies >= d edges. The
                      family then bears on obscure-end stranding only.
                      (A popularity-proximity trim shares this blindness for a
                      different reason: reverse-only sub-decile edges carry
                      the LARGEST fame gap by construction, so a
                      keep-closest-popularity trim deletes them first too. It
                      is deliberately not implemented; the proximity idea is
                      covered by the proximity_select family.)

      banded_quota    Reserve floor(quota*d) slots at every over-degree node
                      for its strongest partners below the top popularity
                      decile OF THIS BUILD'S OWN POPULATION (a shipped rule
                      cannot consult a frame that only exists in analysis);
                      remaining slots fill by strength. The one implemented
                      trim that can RETAIN famous->obscure edges bounded, and
                      therefore the one union configuration that bears on
                      DD-F1.

    Determinism: nodes processed by (-degree, mbid); deletions ordered by the
    trim key with ties broken on highest neighbour MBID, so the surviving set
    is a function of the input alone.
    """
    if trim not in ("weakest_first", "banded_quota"):
        raise ValueError(f"unknown trim {trim!r}")

    keep = _top_j(ranking, adjacency, j, lambda u, v: (-ranking[u][v], v))

    # Union, then symmetrise on the stronger score, giving an undirected graph.
    unioned: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in keep[node] or node in keep.get(dst, set()):
                unioned[node][dst] = score
    result = symmetrise(unioned)

    # Symmetric strength for the trim order: the pair's stronger unclipped
    # ranking value, so both endpoints agree on which edge is weakest.
    def strength(u: str, v: str) -> float:
        return max(ranking.get(u, {}).get(v, float("-inf")),
                   ranking.get(v, {}).get(u, float("-inf")))

    if trim == "banded_quota":
        # Top-decile threshold over THIS build's own population, by rank.
        # pop is a VALUE (log-scaled), so the cut is taken on sorted rank,
        # never on the value itself (pop_raw is not a percentile, §2.12).
        ranked_pop = sorted(pop.values())
        cut_index = int(len(ranked_pop) * 0.9)
        decile_threshold = ranked_pop[min(cut_index, len(ranked_pop) - 1)]
        reserve = int(quota * d)

    for node in sorted(result, key=lambda n: (-len(result[n]), n)):
        excess = len(result[node]) - d
        if excess <= 0:
            continue
        if trim == "weakest_first":
            doomed = sorted(
                result[node], key=lambda v: (strength(node, v), _desc(v))
            )[:excess]
        else:
            by_strength = sorted(
                result[node], key=lambda v: (-strength(node, v), v)
            )
            sub_decile = [v for v in by_strength if pop[v] < decile_threshold]
            reserved = set(sub_decile[:reserve])
            rest = [v for v in by_strength if v not in reserved]
            kept = set(list(reserved) + rest[: d - len(reserved)])
            doomed = [v for v in by_strength if v not in kept]
        for victim in doomed:
            result[node].pop(victim, None)
            result[victim].pop(node, None)
    return result


class _desc:
    """Sort helper: reverses string order so ties drop the highest MBID first."""

    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value

    def __lt__(self, other: "_desc") -> bool:
        return self.value > other.value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _desc) and self.value == other.value


def cap_proximity_select(adjacency: Adjacency, ranking: Adjacency,
                         pop: dict[str, float], *, k: int,
                         key: str = "popularity_proximity") -> Adjacency:
    """Mutual-kNN mechanism, popularity-proximity selection key (BTF-4 shape).

    BoilTheFrog selects each artist's edges by |delta popularity| ascending --
    `weight = 1 + pop_weight * |dpop| / 100`, `sorted(...)[:cap]`
    (`new_crawler/artist_graph.py::load_graph`, reproduced in
    builder/analysis/2026-07-27-boilthefrog-reconstruction/). At a fixed cap of
    4 that criterion halved max degree (67 -> 38) and cut the <=2-connection
    share from 13.97% to 9.94% against similarity-rank selection.

    THE SHAPE IS ADAPTED, NOT COPIED, and the difference matters: BTF applies
    its criterion to an undirected UNION, which bounds degree only empirically
    (38 at cap 4, 147 uncapped -- its source lists are <=20 by Spotify, so the
    unbounded regime cannot arise there at all; BTF-4). A union here would be
    unbounded, so this rule keeps the both-ways mechanism -- which bounds by
    construction -- and swaps only the ordering key.

    BOUND: degree <= k by construction.

    `key` is a parameter because CB-4 pins the exact form before any
    comparative cell runs. Two are implemented:
      similarity_rank        -- identical to cap_mutual_knn; a self-test that
                                the key plumbing changes nothing on its own.
      popularity_proximity   -- |pop(u) - pop(v)| ascending, the BTF-4 form,
                                monotone in the BTF weight for any positive
                                pop_weight so the ordering is identical.
    """
    if key == "similarity_rank":
        rank_key = lambda u, v: (-ranking[u][v], v)  # noqa: E731
    elif key == "popularity_proximity":
        rank_key = lambda u, v: (abs(pop[u] - pop[v]), v)  # noqa: E731
    else:
        raise ValueError(
            f"selection key {key!r} is not pinned. CB-4 pins the key before any "
            "comparative cell runs; do not invent one here."
        )

    top_k = _top_j(ranking, adjacency, k, rank_key)
    result: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in top_k[node] and node in top_k.get(dst, set()):
                result[node][dst] = score
    return result


def cap_uncapped(adjacency: Adjacency, ranking: Adjacency,
                 pop: dict[str, float]) -> Adjacency:
    """REFERENCE ROW ONLY -- barred from selection (plan §0 ruling 3).

    NO BOUND. Exists so that any future re-evaluation of bounded-degree starts
    from measured baselines rather than a remembered fear, and so the cost of
    un-boundedness is a column instead of an assumption. Never a candidate:
    it re-imports the one risk the blind listen condemned, with no offline
    price for it.
    """
    return {node: dict(edges) for node, edges in adjacency.items()}


RULES = {
    "mutual_knn": cap_mutual_knn,
    "trimmed_union": cap_trimmed_union,
    "proximity_select": cap_proximity_select,
    "uncapped": cap_uncapped,
}
SELECTABLE = ("mutual_knn", "trimmed_union", "proximity_select")


# --------------------------------------------------------------------------
# The assembly, mirroring build_from_archive stage for stage.
# --------------------------------------------------------------------------


def _assemble(config: BuilderConfig, archive: RawArchive, source,
              cap_step) -> tuple[Graph, dict]:
    """build_from_archive with the cap step injected. Stage order is identical."""
    if config.algorithm == PRODUCTION_ALGORITHM:
        prefix = f"similar/{source.name}/"
    else:
        prefix = f"similar/{source.name}/{config.algorithm}/"

    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix) : -len(".json")]
        if "/" in mbid:
            continue
        payload = archive.get(key)
        if payload is not None:
            payloads[mbid] = payload

    known = set(payloads)
    identities = harvest_identities(payloads.values())

    if config.filter_special_purpose:
        excluded = {
            mbid
            for mbid, (_name, disambiguation) in identities.items()
            if is_special_purpose(disambiguation)
        }
        known -= excluded
    else:
        excluded = set()

    nameless = {
        mbid for mbid, (name, _d) in identities.items() if not name.strip()
    }
    nameless |= known - identities.keys()
    excluded |= nameless
    known -= nameless

    raw_lists: dict[str, list] = {}
    mass: dict[str, float] = {}
    for mbid in sorted(known):
        neighbours = [
            n
            for n in source.parse(payloads[mbid], exclude_mbid=mbid)
            if n.mbid not in excluded
        ]
        raw_lists[mbid] = neighbours
        mass[mbid] = sum(n.score for n in neighbours) or 1.0

    damping = config.similarity_damping
    scored_adjacency: dict[str, list[tuple[str, float]]] = {}
    for mbid in sorted(known):
        mass_a = mass[mbid]
        scored = [
            (n.mbid, damped_strength(n.score, mass_a, mass[n.mbid], damping))
            for n in raw_lists[mbid]
            if n.mbid in known
        ]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        scored_adjacency[mbid] = scored

    flat: list[float] = []
    layout: list[tuple[str, list[str]]] = []
    for mbid, scored in scored_adjacency.items():
        layout.append((mbid, [dst for dst, _ in scored]))
        flat.extend(value for _dst, value in scored)

    rescaled = rescale_scores(
        flat, strategy=config.similarity_rescale, damping=config.similarity_damping
    )

    score_weighted_indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    cursor = 0
    for mbid, dsts in layout:
        edges = {}
        for dst in dsts:
            edges[dst] = rescaled[cursor]
            cursor += 1
        adjacency[mbid] = edges
        for dst, score in edges.items():
            score_weighted_indegree[dst] += score

    ranking: Adjacency = {
        mbid: {dst: strength for dst, strength in scored}
        for mbid, scored in scored_adjacency.items()
    }

    # Cap-invariant popularity for proximity selection: computed here, upstream
    # of every cap, so it is identical across all rule cells of one archive.
    # Log-scaled to match graph._log_scaled's currency (a VALUE, not a rank).
    logs = {m: math.log1p(max(0.0, score_weighted_indegree[m])) for m in adjacency}
    low, high = (min(logs.values()), max(logs.values())) if logs else (0.0, 0.0)
    span = high - low
    pop = {m: ((v - low) / span if span else 0.0) for m, v in logs.items()}

    pre_cap_edges = sum(len(e) for e in adjacency.values())
    adjacency = cap_step(adjacency, ranking, pop)
    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)

    pruned: Adjacency = {
        node: {dst: score for dst, score in edges.items() if dst in keep}
        for node, edges in adjacency.items()
        if node in keep
    }

    stats = [
        ArtistStats(
            mbid=mbid,
            name=identities.get(mbid, ("", ""))[0],
            pop_indegree_scaled=round(score_weighted_indegree[mbid] * 1000),
            listen_count=0,
            disambiguation=identities.get(mbid, ("", ""))[1],
        )
        for mbid in keep
    ]

    diagnostics = {
        "responses_read": len(payloads),
        "nodes_pre_prune": len(adjacency),
        "nodes_kept": len(keep),
        "directed_edges_pre_cap": pre_cap_edges,
        "dropped_nameless": len(nameless & set(payloads)),
    }
    return build_graph(pruned, stats, source.edge_type), diagnostics


def cell_name(archive: str, rule: str, params: dict) -> str:
    tail = "-".join(f"{k}{v}" for k, v in sorted(params.items())) or "none"
    return f"{archive}-{rule}-{tail}"


def build_variant(archive: str, rule: str, params: dict,
                  *, write: bool = True) -> dict:
    """Build one cell and return its manifest (sha256, counts, timing)."""
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r}; known: {sorted(RULES)}")

    config = BuilderConfig(algorithm=ALGORITHMS[archive])
    source = ListenBrainzSource(config)
    raw = ReadOnlyArchive(LocalArchive(ARCHIVES[archive]))

    fn = RULES[rule]
    cap_step = lambda a, r, p: fn(a, r, p, **params)  # noqa: E731

    started = time.monotonic()
    graph, diagnostics = _assemble(config, raw, source, cap_step)
    elapsed = time.monotonic() - started

    payload = serialise(graph)
    manifest = {
        "cell": cell_name(archive, rule, params),
        "archive": archive,
        "algorithm": config.algorithm,
        "rule": rule,
        "params": params,
        "selectable": rule in SELECTABLE,
        "artists": graph.artist_count,
        "edges": graph.edge_count,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "elapsed_seconds": round(elapsed, 1),
        "diagnostics": diagnostics,
    }
    if write:
        CELLS.mkdir(parents=True, exist_ok=True)
        target = CELLS / f"{manifest['cell']}.bin"
        target.write_bytes(payload)
        target.with_suffix(".bin.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
    return manifest


def gate() -> dict:
    """CB-1's instrument gate: green half AND red half.

    A green identity from an instrument never shown to go red is not evidence.
    """
    results = {}

    for archive in ("ALG-E", "ALG-B"):
        expected = REFERENCE[archive]
        got = build_variant(archive, "mutual_knn", {"k": 50}, write=False)
        ok = (
            got["sha256"] == expected["sha256"]
            and got["artists"] == expected["artists"]
            and got["edges"] == expected["edges"]
        )
        results[f"green_{archive}"] = {
            "expected": expected,
            "got": {k: got[k] for k in ("sha256", "artists", "edges")},
            "byte_identical": ok,
        }
        print(f"GREEN {archive}: {'PASS' if ok else 'FAIL'} "
              f"({got['artists']} artists, {got['edges']} edges, {got['sha256'][:12]}…)")

    red = build_variant("ALG-E", "mutual_knn", {"k": 49}, write=False)
    changed = red["sha256"] != REFERENCE["ALG-E"]["sha256"]
    results["red_k49"] = {
        "sha256": red["sha256"],
        "artists": red["artists"],
        "edges": red["edges"],
        "differs_from_production": changed,
    }
    print(f"RED   ALG-E k=49: {'PASS' if changed else 'FAIL'} "
          f"({red['artists']} artists, {red['edges']} edges, {red['sha256'][:12]}…)")

    results["gate_passed"] = all(
        results[f"green_{a}"]["byte_identical"] for a in ("ALG-E", "ALG-B")
    ) and changed
    (HERE / "cb_gate.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    return results


def bound_check() -> dict:
    """Every SELECTABLE rule must demonstrate its degree bound (plan §0 ruling 2).

    The identity gate above exercises mutual_knn only -- it is the one rule
    that delegates to shipped code. The two harness-local rules have no
    reference build to be byte-checked against, so what is verified instead is
    the property the plan requires of a candidate: that its stated bound
    actually holds on a real graph. A rule whose bound leaks is not a
    candidate, and finding that out at CB-5 would be finding it out late.

    The uncapped reference row is deliberately NOT bound-checked: it has no
    bound, which is the point of it (§0 ruling 3).
    """
    import numpy as np

    cases = [
        ("mutual_knn", {"k": 50}, 50),
        ("trimmed_union", {"j": 50, "d": 50}, 50),
        ("trimmed_union", {"j": 50, "d": 50, "trim": "banded_quota"}, 50),
        ("proximity_select", {"k": 50}, 50),
    ]
    results = {}
    ok_all = True
    for rule, params, bound in cases:
        manifest = build_variant("ALG-E", rule, params, write=True)
        cell = CELLS / f"{manifest['cell']}.bin"
        from artistpath_builder.artifact import deserialise

        graph = deserialise(cell.read_bytes())
        degrees = np.diff(graph.offsets)
        observed = int(degrees.max())
        holds = observed <= bound
        ok_all = ok_all and holds
        row = {
            "params": params,
            "stated_bound": bound,
            "observed_max_degree": observed,
            "bound_holds": holds,
            "artists": manifest["artists"],
            "edges": manifest["edges"],
            "mean_degree": round(float(degrees.mean()), 2),
        }
        results[manifest["cell"]] = row
        print(f"{manifest['cell']:45} max degree {observed:>5} (bound {bound}) "
              f"{'PASS' if holds else 'FAIL'} — {manifest['artists']} artists, "
              f"{manifest['edges']} edges, mean {row['mean_degree']}")

    results["bound_check_passed"] = ok_all
    (HERE / "cb_bound_check.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true", help="run the instrument gate")
    parser.add_argument("--bound-check", action="store_true",
                        help="verify every selectable rule's stated degree bound")
    parser.add_argument("--archive", choices=sorted(ARCHIVES))
    parser.add_argument("--rule", choices=sorted(RULES))
    parser.add_argument("--params", default="{}", help="JSON dict of rule params")
    args = parser.parse_args()

    if args.gate:
        out = gate()
        raise SystemExit(0 if out["gate_passed"] else 1)
    if args.bound_check:
        out = bound_check()
        raise SystemExit(0 if out["bound_check_passed"] else 1)
    if not (args.archive and args.rule):
        raise SystemExit("need --gate, or both --archive and --rule")
    print(json.dumps(build_variant(args.archive, args.rule,
                                   json.loads(args.params)), indent=2, sort_keys=True))
