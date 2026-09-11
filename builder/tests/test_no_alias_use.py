"""No new code against the pre-2026-07-23 read-only aliases.

The 2026-07-23 rename put the currency in every identifier and kept read-only
aliases under the old names purely so the frozen scripts in `builder/analysis/`
keep executing (mapping table: `builder/analysis/README.md`). CLAUDE.md: never
write new code against an alias. Nothing enforced that, and an alias reads
exactly like the quantity it replaced — which is the misreading the rename
exists to prevent.

This package holds one alias, `Graph.popularity`. The scan covers everything
here except `analysis/`, and is by TOKEN, not by text: comments and strings
may name the old identifiers (history is legitimately discussed), code may not.

`popularity` is also the APG1 wire key, so for it only attribute reads
(`x.popularity`) and definitions (`def popularity`) count; a dict key or a
string literal is the wire contract, not the alias. `getattr(x, "popularity")`
evades the scan — accepted, since nothing writes attribute access that way by
accident.

The api package holds its own aliases and its own copy of this test. The two
share no code by design.
"""

from __future__ import annotations

import tokenize
from collections import Counter
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# Every Python directory in this package except `analysis/` (the frozen
# scripts the aliases exist for). Explicit rather than a walk of the package
# root, which would descend into `scratch/`'s multi-GB dumps and `.venv`.
SCAN_ROOTS = ("src", "tests")

ALIASES = frozenset({"popularity"})
ATTRIBUTE_ONLY = frozenset({"popularity"})

# (path relative to builder/, old name) -> exact number of uses. Exact, so a
# second use inside an allowed file still fails, and a removed alias leaves a
# stale entry that fails too.
ALLOWED: dict[tuple[str, str], int] = {
    # The definition.
    ("src/artistpath_builder/graph.py", "popularity"): 1,
    # The test that keeps the alias resolving and read-only for the frozen
    # scripts (a read, and an attempted write that must raise).
    ("tests/test_graph.py", "popularity"): 2,
}

_SKIP = frozenset(
    {tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT}
)


def _alias_uses(path: Path) -> Counter[str]:
    uses: Counter[str] = Counter()
    previous = ""
    with tokenize.open(path) as source:
        for token in tokenize.generate_tokens(source.readline):
            if token.type == tokenize.NAME and token.string in ALIASES:
                if token.string not in ATTRIBUTE_ONLY or previous in (".", "def"):
                    uses[token.string] += 1
            if token.type not in _SKIP:
                previous = token.string
    return uses


def _scan() -> dict[tuple[str, str], int]:
    found: dict[tuple[str, str], int] = {}
    for root in SCAN_ROOTS:
        root_dir = PACKAGE_ROOT / root
        assert root_dir.is_dir(), f"scan root {root_dir} is missing; the scan would pass vacuously"
        for path in sorted(root_dir.rglob("*.py")):
            relative = path.relative_to(PACKAGE_ROOT).as_posix()
            for name, count in _alias_uses(path).items():
                found[(relative, name)] = count
    return found


def test_no_code_outside_the_allowlist_uses_a_pre_rename_alias():
    found = _scan()
    unexpected = {
        key: count for key, count in found.items() if count > ALLOWED.get(key, 0)
    }
    assert not unexpected, (
        "code uses a pre-2026-07-23 alias; use the new name "
        "(mapping: builder/analysis/README.md). (path, alias) -> uses found: "
        f"{unexpected}"
    )


def test_the_alias_allowlist_has_no_stale_entries():
    found = _scan()
    stale = {key: count for key, count in ALLOWED.items() if found.get(key, 0) < count}
    assert not stale, (
        "allowlist entries no longer match the code — shrink them, and if the "
        f"alias itself was removed, delete its entries: {stale}; found {found}"
    )
