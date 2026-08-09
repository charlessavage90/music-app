"""The frozen un-listenable drop lists (`ULF-` rule, 2026-08-05).

Drop an artist who has never put out anything of their own that is more than
a single track (`ULC-D2`: no sole-credited release group that is primary-type
Album/EP/Single with no secondary types and carries a release of >= 2 tracks),
unless a commercial-DSP link exists AND a clip resolves. Rule document:
docs/superpowers/specs/2026-08-05-unlistenable-filter-rule.md — committed
before any census under the rule existed; this module applies its output and
never re-derives it.

One rule superseding both earlier drops WITHOUT reversing either: the
no-release tail (zero release groups) and the featured-credit class (credits
but never sole) are both strict subsets of this class, and their frozen
keep/drop verdicts carry forward unre-run. The older modules and flags remain
functional for era-pinned probes; their retirement is deferred with a success
condition (ULF-3). Everything structural mirrors no_release_drop.py — one
list per censused population, dated snapshots as sha-pinned package data,
`build_from_archive` offline by a hard rule, spec §9 byte-identical builds —
and that module's docstring carries the full argument.

**What is NEW here, and it is `ULC-F1`: the payload carries the censused
population, not just the drops.** `no_release_drop.py` keys its lists by
algorithm alone, reasoning that a build's algorithm is its archive identity —
true only while one algorithm means one crawl. Extend the crawl and that
lookup *succeeds*, silently handing back a list censused over a smaller
population and leaving every new artist unevaluated. So each `ULF-` payload
records the archive's full artist set at census time (count, sha256 over the
sorted MBIDs, and the members), and the pipeline refuses to build when its
archive contains artists outside that set — the same loud failure an
uncensused algorithm already gets, extended to an uncensused *population*.
The identity is the ARCHIVE artist set, not any built graph's: the archive is
what a crawl extension grows and what `build_from_archive` reads.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from artistpath_builder.config import CANDIDATE_ALGORITHM, PRODUCTION_ALGORITHM

_DATA = Path(__file__).parent / "data"

# sha256 of json.dumps(sorted(drop_mbids), sort_keys=True), recorded in each
# payload's own sha256_over_sorted_drop_mbids key and in the ULF- execution
# log. Frozen 2026-08-05 by analysis/2026-08-05-ulf-census/ulf_droplist.py.
UNLISTENABLE_DROP_SHA256 = (
    "19ae2d038c5266e5999f227a4184a22699991df9a4bdffd2a24418ff249c85b1"
)
CANDIDATE_UNLISTENABLE_DROP_SHA256 = (
    "6b25232f637aa2a4841a81a0cfb251840b7352a3d0eaa36cd63fd04c33627ff3"
)

UNLISTENABLE_DROP_LIST_PATH = _DATA / "unlistenable_drop_20260805.json"
CANDIDATE_UNLISTENABLE_DROP_LIST_PATH = (
    _DATA / "unlistenable_drop_algb_20260805.json"
)

# Censused populations only. An algorithm absent here has no list, and that
# is a refusal rather than a fallback, exactly as in no_release_drop.py.
UNLISTENABLE_DROP_LISTS: dict[str, Path] = {
    PRODUCTION_ALGORITHM: UNLISTENABLE_DROP_LIST_PATH,
    CANDIDATE_ALGORITHM: CANDIDATE_UNLISTENABLE_DROP_LIST_PATH,
}


class NoUnlistenableListForAlgorithm(ValueError):
    """Raised when a build would have to half-apply another population's list.

    Deliberately fatal, for the same recorded reason as
    NoDropListForAlgorithm: borrowing a neighbouring population's list is
    silent and invisible in the built artifact.
    """


class PopulationNotCensused(ValueError):
    """Raised when the archive contains artists the census never evaluated.

    The `ULC-F1` refusal. An algorithm-keyed lookup succeeds after a crawl
    extension and silently under-filters; this failure is the loud
    alternative. The fix is a re-census of the extended population, never a
    build with the stale list.
    """


@dataclass(frozen=True)
class UnlistenableList:
    """One population's frozen census outcome: who was evaluated, who drops."""

    drop_mbids: frozenset[str]
    censused_mbids: frozenset[str]


@lru_cache(maxsize=None)
def load_unlistenable_list(
    algorithm: str, override_path: Path | None = None
) -> UnlistenableList:
    """The `ULF-` list for `algorithm`'s archive, with its censused population.

    Raises `NoUnlistenableListForAlgorithm` if that population has never been
    censused under the rule, and `ValueError` if the payload disagrees with
    its own identity block — a payload that cannot vouch for its population
    must not be trusted for a refusal decision any more than a drop one.

    `override_path` BYPASSES the algorithm lookup entirely rather than
    substituting a path for a known key, so a population with no entry — a
    re-crawl, or an algorithm censused for the first time — can be built
    without editing this module. It is per-invocation by design: a default
    keyed on algorithm alone cannot express two populations of the SAME
    algorithm, which is exactly what a crawl extension produces. Changing
    which list is the DEFAULT is an adoption decision and belongs in the
    adoption commit, never here.

    The population check downstream is NOT bypassed: an overridden payload
    still has to vouch for its own identity, and `pipeline.py` still refuses
    when the archive holds artists the payload never evaluated.
    """
    path = override_path or UNLISTENABLE_DROP_LISTS.get(algorithm)
    if path is None:
        censused = "\n  ".join(sorted(UNLISTENABLE_DROP_LISTS)) or "(none yet)"
        raise NoUnlistenableListForAlgorithm(
            f"no un-listenable drop list has been censused for algorithm "
            f"{algorithm!r}.\n"
            "Refusing to build rather than apply another population's list — "
            "the same defect class no_release_drop.py refuses for.\n"
            "Either census this population under the ULF- rule (spec "
            "2026-08-05) or build with drop_unlistenable=False, which is an "
            "experimental control and never a shipping configuration.\n"
            f"Censused populations:\n  {censused}"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))

    population = payload["population"]
    mbids = population["mbids"]
    digest = sha256(json.dumps(sorted(mbids), sort_keys=True).encode()).hexdigest()
    if len(mbids) != population["count"] or digest != population[
        "sha256_over_sorted_mbids"
    ]:
        raise ValueError(
            f"{path.name}: the population identity block disagrees with "
            "itself (count or sha256 vs the recorded members). The payload "
            "cannot vouch for which population it censused; regenerate it "
            "from the census, never edit it by hand."
        )

    censused_mbids = frozenset(mbids)
    drop_mbids = frozenset(payload["drop_mbids"])
    stray = drop_mbids - censused_mbids
    if stray:
        raise ValueError(
            f"{path.name}: {len(stray)} drop_mbids lie outside the censused "
            "population — a drop the census never evaluated is a "
            "contradiction in the payload, not a bigger list."
        )
    return UnlistenableList(drop_mbids=drop_mbids, censused_mbids=censused_mbids)
