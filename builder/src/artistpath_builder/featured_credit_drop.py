"""The frozen featured-credit drop lists (FCF- rule, 2026-08-03).

Drop an artist who is credited on release groups but never as the sole
artist, has no Discogs main-artist release, and fails the keep-check (a
commercial-DSP link exists AND a clip resolves). The rule document —
docs/superpowers/specs/2026-08-03-featured-credit-filter-rule.md — was
committed before the keep-check's network results existed; this module
applies its output and never re-derives it.

Why the class exists at all: a MusicBrainz *credit* creates the node,
quarter-weight co-listens on other artists' tracks create its similarity
edges (LBS-1, FEATURED_ARTIST_WEIGHT 0.25), and the no-release rule keeps it
because credits count as release groups. These artists are in the graph
without ever having been listened to as artists. The no-release rule only
evaluates artists with ZERO release groups, so the class is structurally
invisible to it — the two drops are disjoint by construction.

Everything structural here mirrors no_release_drop.py, deliberately and
line-for-line where possible — one list per censused population, selected by
`BuilderConfig.algorithm`; an uncensused population refuses to build rather
than borrowing a list (conditional on the flag, so era-pinned probes still
build); the lists are dated snapshots shipped as package data because
`build_from_archive` never touches the network and spec §9 requires
byte-identical output. That module's docstring carries the full argument;
this one does not restate it.
"""

from __future__ import annotations

import json

from functools import lru_cache
from pathlib import Path

from artistpath_builder.config import CANDIDATE_ALGORITHM, PRODUCTION_ALGORITHM

_DATA = Path(__file__).parent / "data"

# sha256 of json.dumps(sorted(drop_mbids), sort_keys=True), as recorded in
# the execution log and the probe output's own sha256_over_sorted_mbids key.
FEATURED_DROP_LIST_SHA256 = (
    "0f337de2b5c1fcfab64b4efd690826e269206a5db3b8142bb5776af4d9b3655c"
)
CANDIDATE_FEATURED_DROP_LIST_SHA256 = (
    "b8d230e6ffc7d0f5789b5dbc05fefb0b564bbddfc2590f478aa21e218fbed6f0"
)

# The _am1 suffix is FCF-AM1 (owner-ruled 2026-08-03): a Discogs exemption
# requires a SOLE-credit release, so shared album-level credits no longer
# exempt. The pre-amendment freeze remains in the probe directory.
FEATURED_DROP_LIST_PATH = _DATA / "featured_credit_drop_20260803_am1.json"
CANDIDATE_FEATURED_DROP_LIST_PATH = _DATA / "featured_credit_drop_algb_20260803_am1.json"

# Censused populations only. An algorithm absent here has no list, and that is
# a refusal rather than a fallback — see no_release_drop.py's docstring.
FEATURED_DROP_LISTS: dict[str, Path] = {
    PRODUCTION_ALGORITHM: FEATURED_DROP_LIST_PATH,
    CANDIDATE_ALGORITHM: CANDIDATE_FEATURED_DROP_LIST_PATH,
}


class NoFeaturedCreditListForAlgorithm(ValueError):
    """Raised when a build would have to half-apply another population's list.

    Deliberately fatal, for the same recorded reason as
    NoDropListForAlgorithm: borrowing a neighbouring population's list is
    silent and invisible in the built artifact.
    """


@lru_cache(maxsize=None)
def load_featured_credit_drop_mbids(algorithm: str) -> frozenset[str]:
    """MBIDs the FCF- rule removes from a build of `algorithm`'s archive.

    Raises `NoFeaturedCreditListForAlgorithm` if that population has never
    been censused for this class.
    """
    path = FEATURED_DROP_LISTS.get(algorithm)
    if path is None:
        censused = "\n  ".join(sorted(FEATURED_DROP_LISTS))
        raise NoFeaturedCreditListForAlgorithm(
            f"no featured-credit drop list has been censused for algorithm "
            f"{algorithm!r}.\n"
            "Refusing to build rather than apply another population's list — "
            "the same defect class no_release_drop.py refuses for.\n"
            "Either census this population (see "
            "builder/analysis/2026-08-03-featured-credit-filter/) or build "
            "with drop_featured_credit=False, which is an experimental "
            "control and never a shipping configuration.\n"
            f"Censused populations:\n  {censused}"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return frozenset(payload["drop_mbids"])
