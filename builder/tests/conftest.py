import json
from hashlib import sha256
from pathlib import Path

import pytest

from artistpath_builder import unlistenable_drop
from artistpath_builder.unlistenable_drop import load_unlistenable_list

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def install_ulf_list(monkeypatch, tmp_path):
    """Install a tmp-path ULF- drop list for an algorithm.

    The un-listenable filter (unlistenable_drop.py) is default-on and its
    payload must cover the archive's population (ULC-F1), so any test that
    builds a synthetic archive with the flag on needs a list censusing that
    archive. Tests exercising OTHER features pin drop_unlistenable=False
    instead — the same factor-table-control idiom as the sibling flags.
    """

    def install(algorithm, censused, drop=(), keep=(), mutate=None, register=True):
        # register=False writes the payload but leaves it OUT of the registry,
        # for the per-invocation override (SEL-, 2026-08-09): the case it exists
        # for is a population the algorithm-keyed registry cannot name.
        ordered = sorted(censused)
        payload = {
            "rule": "ULF- (test fixture)",
            "censused": "2026-08-05",
            "population": {
                "count": len(ordered),
                "sha256_over_sorted_mbids": sha256(
                    json.dumps(ordered, sort_keys=True).encode()
                ).hexdigest(),
                "mbids": ordered,
            },
            "drop_mbids": sorted(drop),
            "keep_mbids": sorted(keep),
        }
        if mutate:
            mutate(payload)
        stem = f"ulf_{algorithm.replace('/', '_')}"
        path = tmp_path / f"{stem}{'' if register else '_override'}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        if register:
            monkeypatch.setitem(
                unlistenable_drop.UNLISTENABLE_DROP_LISTS, algorithm, path
            )
        load_unlistenable_list.cache_clear()
        return path

    yield install
    load_unlistenable_list.cache_clear()


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
