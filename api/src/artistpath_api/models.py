"""Request/response schemas for the HTTP API."""

from __future__ import annotations

from pydantic import BaseModel


class ExclusionIn(BaseModel):
    id: str          # artist MBID
    reason: str      # "dislike" or "known"


class PathRequest(BaseModel):
    sources: list[str]           # artist MBIDs; alpha passes exactly two
    exclude: list[ExclusionIn] = []


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
    stop_rule: str


class TrackOut(BaseModel):
    preview_url: str
    title: str
    cover_url: str
