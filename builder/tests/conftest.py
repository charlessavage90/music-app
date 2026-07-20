import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def similar_artists_payload() -> dict | list:
    """The real API response recorded in Task 1."""
    return json.loads((FIXTURES / "similar_artists_sample.json").read_text(encoding="utf-8"))


@pytest.fixture
def seed_artists_payload() -> dict | list:
    """The real API response recorded in Task 1."""
    return json.loads((FIXTURES / "seed_artists_sample.json").read_text(encoding="utf-8"))


@pytest.fixture
def artist_listeners_payload() -> dict:
    """The real per-artist stats response recorded in Task 1."""
    return json.loads((FIXTURES / "artist_listeners_sample.json").read_text(encoding="utf-8"))
