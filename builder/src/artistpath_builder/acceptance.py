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
backfilling names by MBID, was declined — and is also impossible: the three
most popular nameless MBIDs return "Artist not found" from MusicBrainz,
checked by the owner 2026-07-29. They are deleted or merged upstream
entities that survive in the similarity data.)

✅ **DISCHARGED 2026-07-29 (`GR-1`/`GR-4`).** The drop rule is implemented in
`pipeline.py` and a full rebuild from the production archive passes this
check. It removes 36 artists where the emitted graph showed 33 — the rule
runs pre-prune, over a larger population — and 3 further nodes are pruned as
stranded neighbours of dropped ones. Struck, kept for the record.

**The tripwire stays, and is now a standing build rule rather than a
deferral:** any future crawl can mint new nameless nodes the same way. Do
not weaken the check to unblock a build.

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
#
# CROOVE was struck 2026-08-05 by owner decision. It was here under group 2
# only — pair 8 (Nirvana → CROOVE) of a track closed 2026-07-25 — and the
# ULF- filter now drops CROOVE from every build: three sole albums, all
# secondary-type Soundtrack (outside ULC-D2's shape), no MB DSP link, and
# the app's own resolver plays nothing for them (measured, not assumed —
# ULF- execution log §7). Leaving the pin would have blocked every
# production-criteria build to protect a card that is silent today. Group 1,
# the §2.8 deletion detectors, is untouched: those four names are famous,
# kept by every filter, and remain the cheap repeat-detector.
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
    #
    # RECALIBRATED 2026-08-06 for the `MSW-` map switch, on the owner's
    # decision after the Task 9 build was refused by the previous values.
    # This is the "update deliberately" case the paragraph above names, not a
    # quiet widening: the tolerance is UNCHANGED at about ±20 %, and only the
    # centre moved, from the retired 75k map (74,193 / 898,006) to the
    # candidate one. Both previous values were breached for reasons that are
    # properties of the adopted package, each traced to exactly one knob:
    #
    #   - the edge ceiling was never compatible with `trimmed_union`, which
    #     is non-reciprocal by construction and so roughly doubles E. The
    #     LISTENED arm (`CRE-` cell B-S1) recorded MORE edges than the build
    #     this refused — it would have been rejected by the old ceiling too.
    #     Mutual k-NN on the same archive gives 732,832, inside the old band.
    #   - the node floor is crossed by `drop_unlistenable` ALONE, which did
    #     not exist when B-S1 was built and is the change being adopted for.
    #
    # Both figures are owned by the MSW- execution log's Task 9 section and
    # `builder/analysis/2026-08-03-cap-reevaluation/cre_builds.json`.
    #
    # Sensitivity is preserved, and the band is checked against four known
    # artifacts rather than centred on one: the new build and the listened
    # arm B-S1 both sit INSIDE it, while the retired 75k map and a mutual-kNN
    # build of the candidate archive both fall OUTSIDE — which is correct
    # after adoption, and is why the frozen calibration probe at
    # builder/analysis/2026-07-23-acceptance-bounds/check.py is era-pinned to
    # the pre-adoption values rather than following this change.
    #
    # RECALIBRATED 2026-08-10 for the `CXA-` adoption of the extended archive,
    # ON THE OWNER'S DECISION AT `CXA-S1`, TAKEN 2026-08-10, after the JFX-B
    # build was refused by the MSW- values above. Recalibration is his, per §6
    # of the JFX- pre-registration and the MSW-G3 precedent — the same
    # protocol as that entry and for the same reason: the tolerance is
    # UNCHANGED at about ±20 %, only the centre moved, and only the two bounds
    # that actually failed were touched. Both breaches trace to exactly ONE
    # knob — the archive going 75,000 → 117,302 responses (`CEX-`). No cost
    # function, cap rule or drop rule moved with it.
    #
    # Sensitivity is preserved, and the band is checked against FOUR known
    # artifacts rather than centred on one — each count read from its own
    # manifest sidecar rather than carried from a document:
    #
    #   ACCEPT  JFX-B, the new build         88,685 / 1,618,164
    #   reject  today's adopted MSW- map     58,838 / 1,315,684  ← on NODES
    #   reject  retired pre-MSW mutual-kNN   74,193 /   898,006  ← on EDGES
    #   reject  mutual-kNN of THIS archive   81,749 /   905,558  ← on EDGES
    #
    # ⚠ The fourth row is what this recalibration ADDED, and it is the only
    # one that varies the CAP RULE rather than the crawl size: same archive,
    # same ULF- payload, same k=50, `mutual_knn` instead of `trimmed_union`.
    # It exists because the MSW- band could NOT discriminate the cap rule —
    # the comment above records mutual k-NN on the 75k archive at 732,832
    # edges, INSIDE the then-current band. Here the edge floor rejects it by
    # roughly 30 %, while its node count (81,749) sits INSIDE the node band.
    # So after this change the EDGE FLOOR is the only bound standing between a
    # silent cap-rule revert and a shipped artifact; the node bound cannot see
    # it. Weaken the edge floor and that protection is gone.
    # Figures: builder/analysis/2026-08-10-cxa-acceptance-bounds/.
    #
    # RESTORED 2026-09-05 (`L4-T1`) to the MSW- values above — REVERT
    # CLEANUP, not a recalibration. The `CXR-` revert of 2026-09-01 moved
    # what is SERVED back to `graph-msw-tu50.bin` and moved none of the three
    # things calibrated around the extended population: the drop-list default,
    # the archive, and these bounds. The consequence was measured by `LUX-E1`:
    # a CORRECT rebuild of the live map was refused before `serialise` and
    # never written. Mechanism and figures:
    # builder/analysis/2026-09-05-lux-e1-drift-source/README.md §4.
    #
    # ⚠ WHY THIS IS NOT THE OWNER DECISION THE TWO ENTRIES ABOVE WERE, and the
    # distinction is the one to apply next time: MSW- and CXA- each moved a
    # bound so a NEW, never-served artifact could be adopted — risk acceptance,
    # and his. This restores the band that admitted the artifact ALREADY IN
    # PRODUCTION, whose counts are facts about what is running today, read from
    # its own manifest sidecar. Nothing is being admitted that his ear has not
    # already passed. The test that separates the two cases: is the new bound
    # derived from something known INDEPENDENTLY of the build that went red?
    # Here, yes. Taken by a session on the owner's explicit instruction
    # (2026-09-05) that bounds tracking a deliberate population change are
    # mechanical. NO BOUND WAS INVENTED OR WIDENED TO FIT A BUILD.
    #
    # Sensitivity is preserved, checked against the same four known artifacts,
    # and `tests/test_acceptance.py` now asserts all four verdicts:
    #
    #   ACCEPT  the served MSW- map          58,838 / 1,315,684
    #   reject  JFX-B, the REVERTED adoption 88,685 / 1,618,164  ← on BOTH
    #   reject  retired pre-MSW mutual-kNN   74,193 /   898,006  ← on BOTH
    #   reject  mutual-kNN of THIS archive   81,749 /   905,558  ← on BOTH
    #
    # ⚠ The cap-rule tripwire the CXA- entry above installed SURVIVES: its
    # warning was that the edge floor is the only bound that can see a silent
    # cap-rule revert. The restored floor of 1,050,000 rejects both mutual-kNN
    # rows (898,006 and 905,558) by roughly 15%, so the protection is intact
    # under this band too — it is not being traded away for the node floor.
    # The second row is what the CXA- values got WRONG after the revert: they
    # ACCEPTED the artifact the owner's listening test rejected.
    #
    # PREVIOUS (CXA- extended pop): node_count=(70_900, 106_400),
    #                               edge_count=(1_295_000, 1_942_000)
    # PREVIOUS (retired 75k map):   node_count=(60_000, 90_000),
    #                               edge_count=(700_000, 1_100_000)
    node_count=(47_000, 71_000),
    edge_count=(1_050_000, 1_580_000),
    # UNCHANGED and deliberately so: median degree PASSED on the candidate
    # build, and again on the JFX-B build (whose rejection names only the two
    # counts) and on the mutual-kNN row above, at 7. Only the two bounds that
    # actually failed were moved.
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
    # interior card that the bypass control will still operate on.
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
