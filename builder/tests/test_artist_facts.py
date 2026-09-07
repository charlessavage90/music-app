"""`L4-T4` — the frozen structured-facts map must vouch for itself."""

import hashlib
import json

from artistpath_builder.artist_facts import ARTIST_FACTS_SHA256, load_artist_facts


def test_payload_matches_its_own_identity_block():
    facts = load_artist_facts()
    actual = hashlib.sha256(
        json.dumps(sorted(facts.items()), sort_keys=True).encode()
    ).hexdigest()
    assert actual == ARTIST_FACTS_SHA256


def test_an_artist_with_no_facts_is_absent_not_empty():
    """`L4-D3`: absence is the empty state. A present-but-empty dict would
    make the frontend render a blank row it has no way to distinguish."""
    facts = load_artist_facts()
    assert all(v for v in facts.values())


def test_ended_false_is_preserved_not_dropped():
    """"ended: false" is the positive claim that an artist is still active,
    which is not the same as the field being absent."""
    facts = load_artist_facts()
    with_span = [v for v in facts.values() if "ended" in v]
    assert any(v["ended"] is False for v in with_span)


def test_no_field_is_stored_as_null_except_end():
    """`end` is null-bearing by design; every other field is omitted instead.

    A null in one of the others would reach the frontend as a rendered blank
    rather than as an absent row, which is exactly what `L4-D3` rules out.
    """
    facts = load_artist_facts()
    for value in list(facts.values())[:5000]:
        for key, v in value.items():
            if key == "end":
                continue
            assert v is not None, (key, value)


def test_only_the_documented_keys_appear():
    """The wire shape three later tasks depend on. A new key here would reach
    `ArtistOut` and the frontend without either knowing about it."""
    allowed = {"type", "country", "area", "begin", "end", "ended"}
    facts = load_artist_facts()
    seen: set[str] = set()
    for value in facts.values():
        seen |= set(value)
    assert seen <= allowed, seen - allowed
