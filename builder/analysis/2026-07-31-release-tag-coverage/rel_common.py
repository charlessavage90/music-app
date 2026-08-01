"""Shared loading and the aggregation device for the release-tag probe (REL-).

SCOPE: descriptive. Adopts nothing, fixes no criterion, changes no weight,
default, currency or vocabulary. Governing document:
docs/superpowers/specs/2026-07-31-release-tag-coverage-preregistration.md

THE QUESTION (spec section 0)
  For artists carrying NO genre label today, does aggregating the tags on
  their RELEASES produce labels -- specifically in the obscure tail, since a
  frame that only thickens labels where labels are already good changes
  nothing for TAS-6.

IMPORTED, NEVER REIMPLEMENTED
  Band membership, the fame frame and genre normalisation come through the
  TAS- import chain (tas_common -> ct_common -> fp_common -> cb_metrics),
  which carries the adopted artifact's sha256 assertion with it. Two readers
  would be two chances to disagree, and this record has to be comparable with
  COH-2's coverage table rather than merely adjacent.

F0 IS THE COMMITTED FRAME AND THIS FILE MUST NOT REDEFINE IT (spec section 1)
  The MusicBrainz ARTIST dump carries artist-level tags for every artist.
  Using them to define F0 would silently move "unlabelled", and every coverage
  figure below with it, for a reason that has nothing to do with aggregation.
  F0 stays tas_tags.label_sets(). The artist dump's tags are read in exactly
  one place -- REL-7 -- which supplies a tolerance and never a population.

THE VALIDITY FILTER IS THE DORMANT TERM (spec section 1)
  It is INERT in F0 (no aggregation, so no filter applies) and ACTIVE in every
  arm -- the same shape as w_floor in the Track 2 pre-registration's section 0
  and the neutral rule in TAS- section 1. Fixed here, before any run, pinned
  by test_rel_common.py, and it must not move after a result exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent

_TAS = HERE.parent / "2026-07-30-tag-discrimination"
if str(_TAS) not in sys.path:
    sys.path.insert(0, str(_TAS))

from tas_common import (  # noqa: E402,F401
    ADOPTED,
    ADOPTED_SHA,
    BAND_ORDER,
    band_of,
    fame_frame,
    graph_mbids,
    load_partial,
    norm_genre,
    save_partial,
)

SCRATCH = HERE.parent.parent / "scratch"
MB_ARTIST = SCRATCH / "mb-json-dumps" / "artist" / "mbdump" / "artist"
MB_RELEASE_GROUP = (
    SCRATCH / "mb-json-dumps" / "release-group" / "mbdump" / "release-group"
)
DISCOGS_RELEASES = (
    SCRATCH / "discogs-data-dump" / "discogs_20260601_releases.xml"
)

# Discogs' Various Artists. A release credited to it carries a curator's
# genres, not any one artist's.
DISCOGS_VARIOUS = "194"

# Fixed before any run. Broadcast sessions carry a station's framing; the
# secondary types below carry a compiler's, a venue's or a remixer's.
EXCLUDED_PRIMARY = frozenset({"broadcast"})
EXCLUDED_SECONDARY = frozenset(
    {
        "compilation",
        "live",
        "dj-mix",
        "mixtape/street",
        "remix",
        "interview",
        "spokenword",
        "audiobook",
        "audio drama",
    }
)


def f0_label_sets() -> dict[str, set[str]]:
    """The committed baseline frame: LB genre-tags UNION Wikidata P136.

    Deliberately NOT recomputed from the artist dump -- see the module
    docstring. This is the one definition of "labelled today".
    """
    from tas_tags import label_sets  # noqa: PLC0415 -- import cost is real

    return label_sets()


def lb_genre_sets() -> dict[str, set[str]]:
    """The LISTENBRAINZ HALF of F0 alone -- no Wikidata P136.

    Exists for REL-7 only (REL-AM1). Comparing the MusicBrainz artist dump
    against full F0 would compare MB genres against LB genres UNION P136,
    which differ by an entire source: the result measures P136's contribution,
    not snapshot drift. REL-C1's tolerance is that figure, so getting it wrong
    stops the liveness check ever going red.

    NOT a population. F0 stays f0_label_sets(); see the module docstring.
    """
    from tas_tags import OUT_RAW as LB_RAW  # noqa: PLC0415

    lb = load_partial(LB_RAW)
    out: dict[str, set[str]] = {}
    for mbid in graph_mbids():
        record = lb.get(mbid)
        labels = {norm_genre(g) for g in (record or {}).get("genres", [])}
        out[mbid] = {label for label in labels if label}
    return out


def rg_is_attributable(record: dict) -> bool:
    """Is this release group safely THIS artist's own work? (spec section 1)

    Sole artist credit, not a broadcast, and none of the excluded secondary
    types. A split or collaboration attributes the other party's genres; a
    compilation attributes a curator's. Both raise coverage while making the
    labels worse -- the failure a coverage number structurally cannot show.
    """
    credits = record.get("artist-credit") or []
    if len(credits) != 1:
        return False
    if (record.get("primary-type") or "").casefold() in EXCLUDED_PRIMARY:
        return False
    secondary = {s.casefold() for s in (record.get("secondary-types") or [])}
    return not (secondary & EXCLUDED_SECONDARY)


def rg_artist_id(record: dict) -> str | None:
    """The sole credited artist's MBID, or None when there is not exactly one."""
    credits = record.get("artist-credit") or []
    if len(credits) != 1:
        return None
    return ((credits[0] or {}).get("artist") or {}).get("id")


def labels_from(record: dict, field: str) -> set[str]:
    """Normalised label set from a dump record's `tags` or `genres` list.

    Empty normalised labels are dropped: norm_genre returns "" for a
    punctuation-only label, and an empty string would read as a genre shared
    by every artist carrying one -- a false agreement.
    """
    out = {norm_genre(item["name"]) for item in (record.get(field) or []) if item.get("name")}
    return {label for label in out if label}


def discogs_is_attributable(artist_ids: list[str]) -> bool:
    """Sole credited Discogs artist, and not Various Artists.

    The caller passes ids from <artists> only, never <extraartists>: that
    block's roles are Producer / Written-By / Mastered By / Lacquer Cut By,
    and a mastering engineer is not the genre of the record.
    """
    return len(artist_ids) == 1 and artist_ids[0] != DISCOGS_VARIOUS


def aggregate(per_release: list[set[str]]) -> set[str]:
    """An artist's aggregated label set: the union over their releases.

    Minimum support is ONE release (spec section 1). The median unlabelled
    lower-half artist has 2 release groups, so a >= 2 threshold would discard
    most of the target population by construction -- it would measure
    prolificacy, not tagging. Support counts are emitted alongside by the
    collectors so the fragility stays visible.
    """
    out: set[str] = set()
    for labels in per_release:
        out |= labels
    return out


def jaccard(a: set[str], b: set[str]) -> float | None:
    """Overlap of two label sets, or None when either side is empty.

    None means "cannot be scored", never "disagrees". REL-3 counts those
    separately rather than folding them in as zeros.
    """
    if not a or not b:
        return None
    return len(a & b) / len(a | b)
