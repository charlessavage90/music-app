"""Builder's APG1 writer must still emit exactly the file the api's tests read.

`builder/` writes APG1 and `api/` reads it, and the two packages share no code
by design: the format is the contract, kept in lockstep by hand. Every other
artifact test here round-trips a graph through this package's OWN writer and
reader, which proves they agree with each other and says nothing about whether
either still agrees with the api. A change made to both halves here in lockstep
passes all of them.

The committed fixture is a fixed point outside that loop. It is byte-identical
in both packages (asserted below), the api's suite parses it through
`GraphStore`, and `api/tests/test_apg1_fixture_lockstep.py` pins what the api
reader decodes from it. So if this package's writer re-emits the fixture byte
for byte, writer and api reader still meet at the same bytes — without either
package importing the other.

If a format change is intended, this failing is the reminder that it is a
two-package change: regenerate both fixture copies (`artistpath-build
fixture`), update the api reader, and re-derive the api test's literals.
"""

from __future__ import annotations

from pathlib import Path

from artistpath_builder.artifact import deserialise, serialise

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "graph-fixture.bin"
# A data file, not code: reading the api's copy couples nothing but the repo
# layout, and it is what makes "the file the api reads" literally true.
API_FIXTURE = (
    Path(__file__).resolve().parents[2] / "api" / "tests" / "fixtures" / "graph-fixture.bin"
)


def _first_difference(a: bytes, b: bytes) -> str:
    for offset, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f"first differing byte at offset {offset}: {x:#04x} != {y:#04x}"
    return f"one is a prefix of the other: lengths {len(a)} != {len(b)}"


def test_builder_writer_re_emits_the_committed_fixture_byte_for_byte():
    committed = FIXTURE.read_bytes()
    rewritten = serialise(deserialise(committed))
    assert rewritten == committed, (
        "builder's APG1 writer no longer reproduces the committed fixture — "
        "the api reads that file, so writer and reader have drifted. "
        + _first_difference(rewritten, committed)
    )


def test_builder_and_api_fixture_copies_are_identical():
    builder_copy = FIXTURE.read_bytes()
    api_copy = API_FIXTURE.read_bytes()
    assert builder_copy == api_copy, (
        "the two committed graph-fixture.bin copies differ, so the writer "
        "check above no longer covers the file the api reads. "
        + _first_difference(builder_copy, api_copy)
    )
