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


class TrackOut(BaseModel):
    preview_url: str
    title: str
    cover_url: str
