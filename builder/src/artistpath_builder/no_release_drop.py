"""The frozen no-release-tail drop lists (owner decision 2026-08-01, NEXT.md).

Keep a release-less artist only where a commercial-DSP link exists AND a clip
resolves. The rule is ADOPTED — applied here, never re-derived, and never
re-opened. It is also **population-independent**: the owner ruled on
2026-08-02 that it does not need re-validating per archive, because it rests on
claims that hold for any population and no second refinement mechanism exists.

**One list per archive, and never one list for any archive.** The rule is
population-independent; its *output* is not. A drop list is the rule evaluated
against a specific crawl, so each censused population has its own:

    ALG-E (production)  7,035 dropped, censused 2026-08-01
    ALG-B (candidate)   9,501 dropped, censused 2026-08-02

They are not near-copies. Only 2,712 MBIDs are common to both, so applying the
production list to an ALG-B build would drop 4,323 artists the rule keeps there
and miss 6,789 it drops — and would do it silently. That asymmetry is precisely
what a cross-archive comparison must not contain, which is the whole reason the
candidate population was censused. Until 2026-08-02 the builder applied the
production list to whatever archive it was handed; this module is the fix.

**An uncensused population refuses to build rather than borrowing a list.**
Four of the six permitted algorithms have never been censused. Half-applying a
neighbouring population's list is the defect, so `load_drop_mbids` raises
`NoDropListForAlgorithm`. The refusal is conditional on the drop being enabled:
with `drop_no_release_tail=False` any archive builds, which is what the
era-pinned probes under `builder/analysis/` rely on.

The selector is `BuilderConfig.algorithm`, which already decides which archive
sub-tree a build reads (`build_from_archive`). A build's algorithm *is* its
archive identity, so no new config field is needed — and adding one would have
tripped the mirrors guard for a distinction the pipeline already draws.

Both lists are **dated snapshots** and are deliberately frozen as data.
Re-resolving the clip half at build time would break two hard rules at once:
`build_from_archive` never touches the network, and spec §9 requires
byte-identical output for identical input — a live Deezer lookup would make two
builds of one archive disagree. Refreshing a list is a deliberate act with its
own decision, not a silent build-time behaviour.

The lists ship inside the package rather than being read from
`builder/analysis/`, which holds frozen probe code that is not installed with
the builder. Each `data/*.json` is a verbatim copy of a probe's output; the
sha256 beside it pins the content, and the test suite checks both.
"""

from __future__ import annotations

import json

from functools import lru_cache
from pathlib import Path

from artistpath_builder.config import CANDIDATE_ALGORITHM, PRODUCTION_ALGORITHM

_DATA = Path(__file__).parent / "data"

# sha256 of json.dumps(sorted(drop_mbids), sort_keys=True), as recorded in
# NEXT.md and docs/superpowers/2026-08-01-HANDOFF-no-release-tail.md.
DROP_LIST_SHA256 = "d876c7baec3626094251503f425f3a5a571e8e0d74ac37bf10e6c37bfb7ac1d3"
CANDIDATE_DROP_LIST_SHA256 = (
    "81d7ec99ff6602f21ea25b8b4d41241ec24b36150df76fe214dd82b750149971"
)

DROP_LIST_PATH = _DATA / "no_release_drop_20260801.json"
CANDIDATE_DROP_LIST_PATH = _DATA / "no_release_drop_algb_20260802.json"

# Censused populations only. An algorithm absent here has no list, and that is
# a refusal rather than a fallback — see the module docstring.
DROP_LISTS: dict[str, Path] = {
    PRODUCTION_ALGORITHM: DROP_LIST_PATH,
    CANDIDATE_ALGORITHM: CANDIDATE_DROP_LIST_PATH,
}


class NoDropListForAlgorithm(ValueError):
    """Raised when a build would have to half-apply another population's list.

    Deliberately fatal. The alternative — quietly applying the production list
    to an uncensused archive — is the defect this module exists to remove, and
    it is invisible in the built artifact.
    """


@lru_cache(maxsize=None)
def load_drop_mbids(algorithm: str) -> frozenset[str]:
    """MBIDs the adopted rule removes from a build of `algorithm`'s archive.

    Raises `NoDropListForAlgorithm` if that population has never been censused.
    """
    path = DROP_LISTS.get(algorithm)
    if path is None:
        censused = "\n  ".join(sorted(DROP_LISTS))
        raise NoDropListForAlgorithm(
            f"no no-release-tail drop list has been censused for algorithm "
            f"{algorithm!r}.\n"
            "Refusing to build rather than apply another population's list: "
            "the two censused lists share only 2,712 of their MBIDs, so "
            "borrowing one would silently drop artists this rule keeps and "
            "keep artists it drops.\n"
            "Either census this population (see "
            "builder/analysis/2026-08-02-candidate-tail-census/) or build with "
            "drop_no_release_tail=False, which is an experimental control and "
            "never a shipping configuration.\n"
            f"Censused populations:\n  {censused}"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return frozenset(payload["drop_mbids"])
