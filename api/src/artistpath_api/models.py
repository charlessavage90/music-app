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


class ArtistOut(BaseModel):
    mbid: str
    name: str
    disambiguation: str
    popularity: float


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


class HealthOut(BaseModel):
    status: str
    # Identity of the artifact actually loaded, so "which graph is live" is
    # answerable over HTTP. Many artifacts sit in builder/scratch/ and they are
    # not interchangeable; a conclusion from the wrong one looks correct.
    graph_sha256: str
    artists: int
    edges: int
