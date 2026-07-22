"""A rejection screen for incoherent paths.

CANCELLED (docs/superpowers/plans/2026-07-22-phase2-revised-plan.md §2 C-1).
Not deferred — cancelled: it failed its Task 5 gate, was deferred twice, carries
three known defects, and its calibration set contains a path mislabelled as
good. Its only identified viable signal is recorded as self-obsoleting once the
Task 13 rescale landed. This module and its tests (`api/tests/test_badpath.py`)
are kept in the tree, intentionally unreferenced by the eval harness and by
`export_paths.py` — do not re-wire `screen_path` into either without reopening
that decision.

NOT AN OBJECTIVE. Never optimise against this. An earlier tuning run improved
every headline metric while routing through unrelated foreign-scene artists and
a MusicBrainz editor account; a detector added to the objective would be gamed
the same way. It lives outside evaluation.py so it cannot be wired into the
optimisation target by accident.

It exists because every overlap-based metric is structurally blind to the
failure this project keeps hitting: a chain of dense, mutually-overlapping
micro-neighbourhoods (a film cast list) scores WELL on Adamic-Adar, on the
overlap coefficient, and on Jaccard (adjudication §4.3).

Three signals, all restricted to INTERIOR nodes — endpoints are user-chosen and
never the router's fault.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from artistpath_api.evaluation import common_neighbours, jaccard
from artistpath_api.graph_store import GraphStore

# MusicBrainz marks placeholder entities this way in the disambiguation field.
# Matching on disambiguation, never on name: 22 nodes have bracketed names and
# 15 of them are real bands ([Alexandros], [dunkelbunt], [:SITD:], ...).
_NON_MUSICAL = re.compile(r"special purpose", re.IGNORECASE)

# Pairwise neighbour-set Jaccard above which two adjacent interior nodes count
# as "the same tight cluster".
#
# NOT calibrated: Task 5 swept this against the known-bad cosine path and a set
# of known-good v3 paths and found no setting that flags the former without
# flagging most of the latter. On the known-bad path this signal runs in the
# WRONG direction — its interior pairs are less overlapping than the good
# paths' — because `jaccard` is bounded by the pair's degree ratio
# (adjudication §4.1) and a cast clique's members have very uneven degrees.
# The value below is the brief's default, retained unfitted. Signals 1 and 2
# also miss that path, so this screen does not currently catch it; treat it as
# unproven rather than as evidence of a clean path.
_MICRO_CLUSTER_JACCARD = 0.5

# Consecutive interior nodes from one cluster before the run is flagged.
_MICRO_CLUSTER_RUN = 3


@dataclass(frozen=True, slots=True)
class BadPathReport:
    flagged: bool
    reasons: list[str] = field(default_factory=list)


def screen_path(store: GraphStore, path: list[int]) -> BadPathReport:
    """Flag a path a human would call incoherent. Interior nodes only."""
    reasons: list[str] = []
    interior = path[1:-1]
    if not interior:
        return BadPathReport(flagged=False, reasons=[])

    for node in interior:
        if _NON_MUSICAL.search(store.disambiguations[node] or ""):
            reasons.append(
                f"non-musical interior entity: {store.names[node]!r}"
            )
        elif not (store.names[node] or "").strip():
            reasons.append(f"non-musical interior entity: unnamed node {node}")

    for u, v in zip(path, path[1:]):
        if len(common_neighbours(store, u, v)) == 0:
            reasons.append(
                f"hop with no common neighbour: "
                f"{store.names[u]!r} -> {store.names[v]!r}"
            )

    run = 1
    for u, v in zip(interior, interior[1:]):
        if jaccard(store, u, v) >= _MICRO_CLUSTER_JACCARD:
            run += 1
            if run >= _MICRO_CLUSTER_RUN:
                reasons.append(
                    f"micro-cluster run of {run} interior nodes ending at "
                    f"{store.names[v]!r}"
                )
                break
        else:
            run = 1

    return BadPathReport(flagged=bool(reasons), reasons=reasons)
