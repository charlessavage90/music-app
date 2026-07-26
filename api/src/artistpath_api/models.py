"""Request/response schemas for the HTTP API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ExclusionIn(BaseModel):
    id: str          # artist MBID
    reason: str      # "dislike" or "known"


class PathRequest(BaseModel):
    sources: list[str]           # artist MBIDs; alpha passes exactly two
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


class TrackOut(BaseModel):
    preview_url: str
    title: str
    cover_url: str
