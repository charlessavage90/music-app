"""Shared loading and the agreement device for the tag discrimination probe (TAS-).

SCOPE: descriptive. Adopts nothing, fixes no criterion, changes no weight,
default or currency. Governing document:
docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md

THE DEVICE (spec section 1)
  agreement = Jaccard over normalised genre-label sets. The label set is the
  COH-2 union genre: LB genre-whitelisted tags (a faithful transport for MB
  genres -- COH-5 measured 99.9% identical sets) UNION Wikidata P136, both
  through the FROZEN ct_common.norm_genre. Same vocabulary as the COH-
  coverage figures, so TAS-1 is comparable with them rather than merely
  adjacent. NOT the widest tag union: COH-6 measured that as near-identical
  in the tail, so it would add a second vocabulary for no gain.

THE NEUTRAL RULE IS THE ONE DORMANT TERM (spec section 0)
  Where either artist is unlabelled, agreement takes the MEDIAN agreement
  between that artist and its OWN labelled candidates -- NEVER zero. Zero is
  a positive claim of dissimilarity; applied to missing data it would demote
  unlabelled candidates, which are disproportionately the obscure ones, and
  push DD-F1 the wrong way. Per-artist rather than a global constant because
  agreement levels vary by artist: a metal act's candidates nearly all share
  "metal" and score high, an eclectic act's share little and score low, so a
  single constant would reward unlabelled candidates for one and punish them
  for the other.

  This rule is INERT at lambda = 0 (the multiplier is exactly 1 whatever it
  says) and ACTIVE in every arm -- the same shape as w_floor in the Track 2
  pre-registration's section 0. It is fixed here, before any run, pinned by
  test_tas_common.py, and must not move after a result exists.

WHY neutral_for TAKES THE ARTIST'S OWN SET
  The implementation plan's draft computed the median of each candidate
  against the FIRST candidate rather than against the artist. That is a
  different quantity and it is not the one the spec defines. Corrected here;
  there is exactly one resolution path (resolved_agreement) so the two cannot
  drift apart again.

IMPORTED, NOT REIMPLEMENTED
  Band membership and genre normalisation must be identical to the COH- and
  FPC- records or nothing here is comparable with either. The import chain
  (ct_common -> fp_common -> cb_metrics) carries the adopted artifact's
  sha256 assertion with it.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

# This directory -- deliberately NOT ct_common.HERE, which points at the
# coherence probe. Defined before the import below so nothing shadows it.
HERE = Path(__file__).parent

_COH = HERE.parent / "2026-07-30-coherence-tag-probe"
if str(_COH) not in sys.path:
    sys.path.insert(0, str(_COH))

from ct_common import (  # noqa: E402,F401
    ADOPTED,
    ADOPTED_SHA,
    BAND_ORDER,
    FPC_WIKIDATA,
    band_of,
    fame_frame,
    get_json,
    graph_mbids,
    load_partial,
    norm_genre,
    save_partial,
)

# Used only where an artist has fewer than two labelled candidates, so no
# per-artist median can be formed. Zero is deliberately NOT the fallback --
# see the module docstring and test_the_fallback_is_not_zero.
GLOBAL_NEUTRAL_FALLBACK = 0.15


def agreement(a: set[str], b: set[str]) -> float | None:
    """Jaccard overlap, or None when either side carries no labels.

    None means "unknown", never "dissimilar". Callers resolve it through
    resolved_agreement() so the neutral rule is applied in exactly one place.
    """
    if not a or not b:
        return None
    return len(a & b) / len(a | b)


def neutral_for(own: set[str], candidate_sets: list[set[str]]) -> float:
    """Median agreement between an artist and its own labelled candidates.

    Unlabelled candidates contribute nothing -- they carry no information and
    must not drag the neutral value toward any particular number. An artist
    with no labels of its own can form no median at all and takes the global
    fallback.
    """
    values = [
        value
        for candidate in candidate_sets
        if (value := agreement(own, candidate)) is not None
    ]
    if len(values) < 2:
        return GLOBAL_NEUTRAL_FALLBACK
    return statistics.median(values)


def resolved_agreement(u_set: set[str], v_set: set[str], neutral: float) -> float:
    """agreement() with the neutral rule applied. The ONLY resolution path."""
    value = agreement(u_set, v_set)
    return neutral if value is None else value
