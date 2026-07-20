"""Bootstrap artist list and per-artist popularity.

The sitewide stats endpoint caps hard at 1,000 artists while advertising
10.4M (Task 1 findings section 2), so it can only seed the snowball. Real
popularity comes per-artist from the listeners endpoint.

Field names are confirmed against responses recorded from the live API.
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import BootstrapArtist

# Sitewide stats: payload.artists[]
FIELD_MBID = "artist_mbid"
FIELD_NAME = "artist_name"

# The sitewide endpoint will not serve beyond this, whatever you ask for.
BOOTSTRAP_CEILING = 1000


def bootstrap_url(config: BuilderConfig, offset: int, count: int) -> str:
    query = urlencode({"count": count, "offset": offset, "range": "all_time"})
    return f"{config.sitewide_artists_url}?{query}"


def _payload(raw: bytes, label: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed {label} payload: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"malformed {label} payload: expected object")
    return data.get("payload", {})


def parse_bootstrap_page(payload: bytes) -> list[BootstrapArtist]:
    rows = _payload(payload, "bootstrap").get("artists", [])
    return [
        BootstrapArtist(mbid=row[FIELD_MBID], name=row.get(FIELD_NAME) or "")
        for row in rows
        if row.get(FIELD_MBID)
    ]
