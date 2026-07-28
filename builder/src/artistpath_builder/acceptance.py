"""Structural acceptance checks for an emitted artifact.

The rest of the suite asserts things about *functions*. Nothing asserted
anything about the *artifact*, and that gap is exactly the size of the
Phase 1 log §2.8 defect: Radiohead was deleted from the graph and the most
famous artists collapsed to near-minimum degree while every test passed.

These checks run at the emission point (`cli.cmd_build`) and **raise**, so a
graph with that failure signature is never written. They are deliberately not
inside `build_from_archive`: that function is exercised throughout the suite
with miniature archives whose graphs cannot satisfy production invariants,
and the invariants here describe a production *artifact*, not the function.

⚠ **The blank-name check below currently rejects a production rebuild, by
design.** The adopted 75k artifact contains 33 nameless artists (measured:
`builder/analysis/2026-07-24-track2-p8b-harness-review/`, F8). **DECIDED
2026-07-28, by the owner: DROP them** — remove nameless artists during
`build`, before the largest-component prune, so a stranded neighbour of a
dropped node is pruned rather than kept dangling. (The alternative,
backfilling names by MBID, was declined.) The remediation is NOT yet
implemented — this is a standing build rule, not a one-off patch, since any
future crawl can mint new nameless nodes the same way. The tripwire stays
until it lands: a check that refuses is what stops the deferral being
silently forgotten. **Success condition: the drop rule lands in the build
and this check then passes on a rebuild.** Do not weaken the check to
unblock a build; implement the drop.

The criteria are data, not code, so the whole set lives in one place
(`PRODUCTION_ACCEPTANCE`) and a test can substitute a scaled-down set.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

import numpy as np

from artistpath_builder.graph import Graph


class ArtifactRejected(ValueError):
    """An emitted graph violated a structural invariant."""


@dataclass(frozen=True, slots=True)
class AcceptanceCriteria:
    # Artists that must resolve by name. The artifact contains only the
    # largest connected component, so presence here IS presence in the LCC.
    canonical_names: tuple[str, ...]
    # How many top-by-popularity nodes form the "famous" sample, and the
    # degree floors that sample must clear.
    famous_sample: int
    famous_median_degree_floor: float
    famous_min_degree_floor: int
    # Global shape, as (low, high) inclusive bounds.
    node_count: tuple[int, int]
    edge_count: tuple[int, int]
    median_degree: tuple[float, float]


# Canonical artists. Two groups, both load-bearing:
#
#   1. The §2.8 failure signature itself — Radiohead was removed from the
#      graph entirely and The Beatles / Coldplay / R.E.M. fell to single
#      digits. These four are the cheapest possible detector for a repeat.
#   2. Every endpoint the Track 2 pre-registration commits to routing
#      between (specs/2026-07-23-track2-preregistration.md §2.3 — analysis
#      set, held-out set, and the ordered reserve). Asserting them at build
#      time is what makes that document's prerequisite P2 a no-op: an
#      artifact that reaches adoption cannot be missing a pair endpoint.
#
# Pair 8 of the analysis set is the owner's captured bypass pair and is not
# yet identified (pre-registration P1), so it is not represented here.
_CANONICAL_NAMES = (
    "Radiohead",
    "The Beatles",
    "Coldplay",
    "R.E.M.",
    "Miles Davis",
    "Daft Punk",
    "The Shins",
    "Wishbone Ash",
    "Metallica",
    "Taylor Swift",
    "Muse",
    "Madonna",
    "Bob Dylan",
    "Pink Floyd",
    "Aphex Twin",
    "Arctic Monkeys",
    "Johnny Cash",
    "Michael Jackson",
    "Gorillaz",
    "System of a Down",
    "The Rolling Stones",
    "Linkin Park",
    "Nirvana",
    "CROOVE",
)

PRODUCTION_ACCEPTANCE = AcceptanceCriteria(
    canonical_names=_CANONICAL_NAMES,
    # The separating statistic. Measured on the two real 75k artifacts —
    # the adopted one and `graph-t15-capfix.bin`, which log §2.8 records as
    # reproducing the defective arm exactly — the top-25-by-popularity
    # median degree differs by roughly a factor of five. This floor sits
    # about midway between them in ratio terms, so it clears the healthy
    # artifact and rejects the defective one with margin on both sides.
    # Script and figures: builder/analysis/2026-07-23-acceptance-bounds/.
    famous_sample=25,
    famous_median_degree_floor=25.0,
    # A famous artist sitting at ordinary degree is the Radiohead signature
    # one step short of deletion. Just under half the graph has degree < 8,
    # so 8 is "unremarkable" — a top-25 artist must beat it.
    famous_min_degree_floor=8,
    # Global shape is a REGRESSION TRIPWIRE, NOT a §2.8 DETECTOR. Log §2.8
    # is explicit that the global shape does not move: the defective and
    # healthy artifacts agree on N, E and median degree to within a handful
    # of nodes. These bounds catch a different failure — a build that
    # silently loses a large share of the graph — and are deliberately
    # generous. Update them deliberately when the crawl target changes;
    # a new crawl is a new artifact identity, not a bound to widen quietly.
    node_count=(60_000, 90_000),
    edge_count=(700_000, 1_100_000),
    median_degree=(5.0, 25.0),
)


def _degrees(graph: Graph) -> np.ndarray:
    return np.diff(graph.offsets).astype(np.int64)


def _famous_order(graph: Graph) -> np.ndarray:
    """Node ids by descending popularity. Stable, so ties are id-ordered."""
    return np.argsort(-np.asarray(graph.pop_raw, dtype=np.float64), kind="stable")


def check_acceptance(graph: Graph, criteria: AcceptanceCriteria) -> None:
    """Raise ArtifactRejected if the graph violates a structural invariant.

    Every violation is collected before raising: a build that fails three
    ways should say so once, not three runs in a row.
    """
    problems: list[str] = []
    degrees = _degrees(graph)

    # Every artist must have a name, and this check takes no criterion because
    # there is no scaled-down version of it: zero is the only defensible count.
    #
    # A nameless artist cannot be reached through search (`api/…/search.py`: an
    # empty name matches no query, and an empty query returns nothing) and
    # cannot resolve a clip (`api/…/clips.py` passes the name itself as the
    # provider query). So the ONLY way one can ever reach a user is as a blank
    # interior card that the bypass buttons will still operate on.
    #
    # The cause is upstream and silent rather than a parse failure: an artist's
    # name is only ever observed when it appears as *someone else's* neighbour
    # (`sources/listenbrainz.py` — there is no per-artist metadata endpoint),
    # and `pipeline.py` defaults an unseen one to "". Nothing objected, which
    # is the same gap this module was created to close, one instance further on.
    blank = [i for i, name in enumerate(graph.names) if not name.strip()]
    if blank:
        sample = ", ".join(graph.mbids[i] for i in blank[:3])
        problems.append(
            f"{len(blank)} artist(s) carry no name (e.g. {sample}) — "
            f"unsearchable, clipless, and renderable only as a blank card"
        )

    present = set(graph.names)
    missing = [name for name in criteria.canonical_names if name not in present]
    if missing:
        problems.append(
            f"{len(missing)} canonical artist(s) absent from the largest "
            f"connected component: {', '.join(missing)}"
        )

    sample = criteria.famous_sample
    if graph.artist_count < sample:
        problems.append(
            f"graph has {graph.artist_count} artists, fewer than the "
            f"famous sample size {sample}"
        )
    else:
        famous = degrees[_famous_order(graph)[:sample]]
        median_degree = statistics.median(famous.tolist())
        if median_degree < criteria.famous_median_degree_floor:
            problems.append(
                f"top-{sample}-by-popularity median degree {median_degree} is "
                f"below the floor {criteria.famous_median_degree_floor} — the "
                f"§2.8 signature (famous artists collapsing toward minimum "
                f"degree while the global shape stays normal)"
            )
        if int(famous.min()) < criteria.famous_min_degree_floor:
            worst = int(np.argmin(famous))
            node = int(_famous_order(graph)[:sample][worst])
            problems.append(
                f"top-{sample}-by-popularity minimum degree {int(famous.min())} "
                f"is below the floor {criteria.famous_min_degree_floor} "
                f"({graph.names[node]!r})"
            )

    for label, value, (low, high) in (
        ("artist count", graph.artist_count, criteria.node_count),
        ("edge count", graph.edge_count, criteria.edge_count),
        (
            "median degree",
            statistics.median(degrees.tolist()) if graph.artist_count else 0,
            criteria.median_degree,
        ),
    ):
        if not low <= value <= high:
            problems.append(f"{label} {value} outside bounds [{low}, {high}]")

    if problems:
        raise ArtifactRejected(
            "artifact rejected; not written:\n  - " + "\n  - ".join(problems)
        )
