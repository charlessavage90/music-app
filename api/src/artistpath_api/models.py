"""Request/response schemas for the HTTP API."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

# Long enough for a 36-character MBID with headroom, short enough that 200 of
# them cannot amplify into a meaningful log line. Deliberately not exactly 36:
# an id that is merely UNKNOWN should reach the handler and be skipped (or
# 404) with a message a person can read, rather than become a schema error.
_MBID_MAX = 64

Mbid = Annotated[str, Field(max_length=_MBID_MAX)]


class ExclusionIn(BaseModel):
    # Both fields are bounded because both are echoed VERBATIM into the
    # telemetry line (app.py's "exclude" key), so an unbounded string here is a
    # log-volume amplifier as well as a parse cost — measured at 1:1 into
    # CloudWatch, which has no other sink and is billed per GB (G3-S3, G3-S4).
    id: Mbid         # artist MBID
    # Normalised to DISLIKE/KNOWN by app.py's _to_exclusions, but logged RAW,
    # so the bound belongs here and not at the normalisation. Deliberately NOT
    # a Literal: an unrecognised reason currently falls back to DISLIKE rather
    # than failing the request, and changing that is a behaviour change.
    reason: str = Field(max_length=16)   # "dislike" or "known"


class PathRequest(BaseModel):
    # Bounded for the same reason `exclude` was, and it was the gap beside it:
    # a 2,000,000-element array cost 442 ms and buffered ~70 MB before the
    # `len(...) != 2` check in build_path rejected it (G3-S3). Alpha passes
    # exactly two. 8 rather than 2 so the handler's readable 422 ("alpha
    # supports exactly two source artists") stays reachable for the realistic
    # mistake, instead of being replaced by a schema error nobody can act on.
    sources: list[Mbid] = Field(max_length=8)   # artist MBIDs; alpha passes two
    # Bounded because avoidance_map runs a fresh graph traversal per entry
    # (pathfinding.py), so an unbounded list is arbitrary attacker-controlled
    # CPU on a GIL-bound handler. 200 is above the deepest real use recorded
    # (a 100-press dogfooding run) with headroom. TR-12 / DEP-25.
    exclude: list[ExclusionIn] = Field(default_factory=list, max_length=200)


class ArtistFacts(BaseModel):
    """The structured MusicBrainz fields LUX-4 carries, all optional.

    WIRE CONTRACT. Every field is optional because the extraction pass finds
    different subsets per artist, and `L4-D3` renders only what is present with
    no placeholder rows — so a null here is "show nothing", never "Unknown".

    A prose description is DROPPED, not deferred (spec §4.5), and genre tags
    are DEFERRED with `LUX-E6` as their entry condition (§4.6). Neither is a
    gap to fill in here.
    """

    type: str | None = None       # "Group", "Person", …
    country: str | None = None    # ISO code, e.g. "GB"
    area: str | None = None       # human-readable, e.g. "United Kingdom"
    begin: str | None = None      # "1995" or "1995-03-01"
    end: str | None = None
    ended: bool | None = None


class ArtistOut(BaseModel):
    mbid: str
    name: str
    disambiguation: str
    popularity: float
    # LUX-4. Additive: a client that ignores them gets exactly the pre-LUX-4
    # behaviour, and a pre-LUX-4 ARTIFACT serves them as null — which is the
    # state production is in until this deploys.
    #
    # Ids are platform id TAILS, not URLs (`L4-D2`): the frontend composes the
    # URL, so a scheme change is a frontend edit rather than a graph rebuild.
    # null does NOT mean "no button" — it means "render a search link"
    # (spec §4.1 option A). The app routes to obscure artists, so the
    # missing-id case is disproportionately the population this exists to
    # serve, and a card showing one service while silently dropping the other
    # reads as the artist being absent from it.
    #
    # These field names are a wire contract and cannot be renamed.
    spotify_id: str | None = None
    apple_id: str | None = None
    facts: ArtistFacts | None = None


class PathResponse(BaseModel):
    artists: list[ArtistOut]
    # Whether the journey needed a stop forced into it, and whether one was
    # possible. Wire contract, so snake_case; the frontend reads it as
    # stopRule. Values are pathfinding.STOP_*.
    stop_rule: Literal["natural", "forced", "adjacent_only"]
    # The artists a bypass removed, in PRESS ORDER. They are hard-excluded and
    # so are absent from `artists`; without this the UI has nowhere to read
    # their names from (REQ-46). Additive: a client that ignores it is fine.
    bypassed: list[ArtistOut] = Field(default_factory=list)
    # Exclusion ids that resolved to no artist. The router ignored them, so the
    # path is built as if those presses never happened — reported rather than
    # dropped so the UI can say so instead of lying (LUX-D2).
    unresolved: list[str] = Field(default_factory=list)


class TrackOut(BaseModel):
    preview_url: str
    title: str
    cover_url: str
    # How many playable tracks this artist has, so the UI can hide a "try
    # another" control that would do nothing. Additive: a client that ignores
    # it gets exactly the pre-LUX-3 behaviour.
    candidate_count: int = 1


class HealthOut(BaseModel):
    status: str
    # Identity of the artifact actually loaded, so "which graph is live" is
    # answerable over HTTP. Many artifacts sit in builder/scratch/ and they are
    # not interchangeable; a conclusion from the wrong one looks correct.
    graph_sha256: str
    artists: int
    edges: int


class MetaOut(BaseModel):
    """What the landing page may say about the map. UXR-D8.

    A subset of HealthOut, served under /api because /health is not reachable
    through CloudFront by design. Additive; nothing consumes it but the badge.
    """

    artists: int
    graph_sha256: str
