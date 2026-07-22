"""The frozen evaluation panel, keyed by MBID.

The panel this replaces drew random NODE INDICES under a fixed seed. Indices
are assigned in sorted-MBID order over whatever survives the largest-component
prune, so any change to the node set shifts them and the "frozen" panel
silently compares different artists between runs.

Four strata. The three aggregated ones total 130 pairs; `hand_picked` is
qualitative only and is NEVER pooled into an aggregate — it was adversarially
selected on the d=0 graph, so regression to the mean guarantees it improves
under any variant.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402

N_RANDOM = 50
N_OBSCURE = 50
N_POPULARITY_WEIGHTED = 30

# Held-out counts per stratum. Computed only AFTER a candidate is chosen on the
# remaining 100, and used solely for adoption criterion 6.
HELD_OUT = {"random": 12, "obscure": 12, "popularity_weighted": 6}

OBSCURE_MAX_DEGREE = 5

# Pairs that produced known-bad or known-good paths in real use. Qualitative
# only. Resolved by name at generation time; missing names are skipped with a
# warning rather than failing the build.
HAND_PICKED_NAMES = [
    ("Miles Davis", "Daft Punk"),
    ("Burzum", "Dolly Parton"),
    ("Cayetana", "Coheed and Cambria"),
    ("Young Gun Silver Fox", "The Format"),
    ("Miles Davis", "Stan Getz"),
    ("Ella Fitzgerald", "Justin Timberlake"),
    ("Radiohead", "Dolly Parton"),
    ("Aphex Twin", "Johnny Cash"),
]


def _sample_pairs(candidates, n, rng, weights=None):
    """Draw `n` distinct unordered pairs from `candidates`."""
    seen: set[tuple[int, int]] = set()
    pairs: list[tuple[int, int]] = []
    attempts = 0
    while len(pairs) < n and attempts < n * 1000:
        attempts += 1
        a, b = rng.choice(candidates, size=2, replace=False, p=weights)
        a, b = int(a), int(b)
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        pairs.append((a, b))
    return pairs


def generate_panel(store: GraphStore, rng: np.random.Generator) -> dict:
    """Build the panel from a reference graph. Run ONCE; commit the result."""
    n = store.artist_count
    degrees = np.diff(store.offsets)
    all_nodes = np.arange(n)

    obscure = np.where(degrees <= OBSCURE_MAX_DEGREE)[0]
    if obscure.size < 2:
        obscure = all_nodes

    # Popularity-weighted: uniform sampling over 75k nodes is dominated by the
    # obscure tail, so without this stratum the panel never tests the
    # mainstream -> mainstream case real users actually query.
    pop = np.asarray(store.popularity, dtype=np.float64)
    weights = pop / pop.sum() if pop.sum() > 0 else None

    drawn = {
        "random": _sample_pairs(all_nodes, N_RANDOM, rng),
        "obscure": _sample_pairs(obscure, N_OBSCURE, rng),
        "popularity_weighted": _sample_pairs(
            all_nodes, N_POPULARITY_WEIGHTED, rng, weights=weights
        ),
    }

    by_name = {name: i for i, name in enumerate(store.names)}
    hand = []
    for src, dst in HAND_PICKED_NAMES:
        if src in by_name and dst in by_name and by_name[src] != by_name[dst]:
            hand.append((by_name[src], by_name[dst]))

    strata: dict[str, list[dict]] = {}
    for name, pairs in drawn.items():
        held = HELD_OUT.get(name, 0)
        strata[name] = [
            {
                "from": store.mbids[a],
                "to": store.mbids[b],
                "from_name": store.names[a],
                "to_name": store.names[b],
                "held_out": i < held,
            }
            for i, (a, b) in enumerate(pairs)
        ]
    strata["hand_picked"] = [
        {
            "from": store.mbids[a],
            "to": store.mbids[b],
            "from_name": store.names[a],
            "to_name": store.names[b],
            "held_out": False,
        }
        for a, b in hand
    ]

    return {
        "note": (
            "Frozen MBID-keyed panel. hand_picked is qualitative only and must "
            "never be pooled into an aggregate."
        ),
        "aggregated_strata": ["random", "obscure", "popularity_weighted"],
        "strata": strata,
    }


def load_panel(path: str | Path) -> dict:
    panel = json.loads(Path(path).read_text(encoding="utf-8"))
    if "strata" not in panel:
        raise ValueError("malformed panel: missing 'strata' key")
    return panel


def resolve_pairs(
    store: GraphStore,
    panel: dict,
    stratum: str,
    held_out: bool | None = None,
) -> tuple[list[tuple[int, int]], list[str]]:
    """Resolve MBID pairs to node ids for one graph.

    `held_out=None` returns every pair, `False` the analysis slice, `True` the
    held-out slice. Unresolvable MBIDs are REPORTED, never silently skipped —
    a variant with a different node set must be visible, not papered over.
    """
    pairs: list[tuple[int, int]] = []
    dropped: list[str] = []
    for entry in panel["strata"].get(stratum, []):
        if held_out is not None and bool(entry.get("held_out")) != held_out:
            continue
        a = store.id_by_mbid.get(entry["from"])
        b = store.id_by_mbid.get(entry["to"])
        unresolved = False
        if a is None:
            dropped.append(entry["from"])
            unresolved = True
        if b is None:
            dropped.append(entry["to"])
            unresolved = True
        if unresolved:
            continue
        pairs.append((a, b))
    return pairs, dropped
