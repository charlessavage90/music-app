"""No new code against the pre-2026-07-23 read-only aliases.

The 2026-07-23 rename put the currency in every identifier and kept read-only
aliases under the old names purely so the frozen scripts in `builder/analysis/`
keep executing (mapping table: `builder/analysis/README.md`). CLAUDE.md: never
write new code against an alias. `test_frozen_script_aliases.py` keeps the
aliases resolving; nothing stopped new code reading them, and an alias reads
exactly like the quantity it replaced — which is the misreading the rename
exists to prevent.

The scan covers every Python directory in this package (none of `analysis/`
lives here) and is by TOKEN, not by text: comments and strings may name the old
identifiers (history is legitimately discussed, and old result JSON still
carries `"hubfrac"` keys), code may not.

`popularity` is also a live wire name — the APG1 metadata key and `ArtistOut`'s
JSON field — so for it only attribute reads (`x.popularity`) and definitions
(`def popularity`) count; a field declaration, keyword argument, dict key or
parameter name is not the alias. `getattr(x, "hubfrac")` evades the scan —
accepted, since nothing writes attribute access that way by accident.

The builder package holds its own alias and its own copy of this test. The two
share no code by design.
"""

from __future__ import annotations

import tokenize
from collections import Counter
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# Every Python directory in this package. Explicit rather than a walk of the
# package root, which would descend into `.venv`.
SCAN_ROOTS = ("src", "tests", "eval")

ALIASES = frozenset(
    {
        "popularity",         # GraphStore.popularity -> pop_raw
        "hub_penalty",        # GraphStore.hub_penalty -> degree_hub_penalty
        "hubfrac",            # PathMetrics.hubfrac -> top1pct_degree_frac
        "mean_interior_pop",  # PathMetrics.mean_interior_pop -> mean_interior_pop_raw
        "max_interior_pop",   # PathMetrics.max_interior_pop -> max_interior_pop_raw
        "hub_node_set",       # evaluation.hub_node_set -> top_degree_node_set
        # ApiConfig.w_hub -> w_degree_hub. The mapping table lists it, but the
        # rename (e724e40) kept NO alias for it, so it has no allowed use at
        # all: reintroducing the name would be new code under an old name.
        "w_hub",
    }
)
ATTRIBUTE_ONLY = frozenset({"popularity"})

# (path relative to api/, old name) -> exact number of uses. Exact, so a second
# use inside an allowed file still fails, and a removed alias leaves a stale
# entry that fails too.
ALLOWED: dict[tuple[str, str], int] = {
    # The definitions.
    ("src/artistpath_api/graph_store.py", "popularity"): 1,
    ("src/artistpath_api/graph_store.py", "hub_penalty"): 1,
    ("src/artistpath_api/evaluation.py", "hubfrac"): 1,
    ("src/artistpath_api/evaluation.py", "mean_interior_pop"): 1,
    ("src/artistpath_api/evaluation.py", "max_interior_pop"): 1,
    ("src/artistpath_api/evaluation.py", "hub_node_set"): 1,
    # The test that keeps the aliases resolving for the frozen scripts.
    ("tests/test_frozen_script_aliases.py", "popularity"): 1,
    ("tests/test_frozen_script_aliases.py", "hub_penalty"): 1,
    ("tests/test_frozen_script_aliases.py", "hubfrac"): 1,
    ("tests/test_frozen_script_aliases.py", "mean_interior_pop"): 1,
    ("tests/test_frozen_script_aliases.py", "max_interior_pop"): 1,
    ("tests/test_frozen_script_aliases.py", "hub_node_set"): 1,
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
