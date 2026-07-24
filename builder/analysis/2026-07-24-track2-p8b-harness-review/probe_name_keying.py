"""P8b probe 2: the harness keys fame by ARTIST NAME. What does the artifact do to that?

`fame.py` builds `fame.json` as {name -> F} and `score.py` reads `F[name]` for every
interior. So two graph nodes sharing a name share a fame value, and a node whose name
is unusable as a query gets whatever the resolver returns for that string.

Probe 1 found 1,058 names shared by 2+ nodes and, separately, 33 nodes whose name is
the EMPTY STRING. This quantifies how routable those nodes are -- i.e. whether this is
a curiosity or a live scoring hazard for the arms that dive.

No arm is run: this is a property of the artifact plus the harness's key choice.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-24-track2-p8b-harness-review/probe_name_keying.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

from artistpath_api.graph_store import GraphStore  # noqa: E402
from mirror import MirrorContext  # noqa: E402


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT
    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    n = len(store.mbids)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    deg = np.diff(store.offsets).astype(np.int64)

    cnt = Counter(store.names)
    blank = [i for i, nm in enumerate(store.names) if not nm.strip()]
    shared = {nm for nm, c in cnt.items() if c > 1 and nm.strip()}
    shared_nodes = [i for i, nm in enumerate(store.names) if nm in shared]

    def summary(ids):
        if not ids:
            return {}
        p = pop[ids]
        q = ctx.pctl[ids]
        d = deg[ids]
        return {
            "n": len(ids),
            "pop_raw": {"min": float(p.min()), "median": float(np.median(p)),
                        "max": float(p.max())},
            "pop_pctl": {"min": float(q.min()), "median": float(np.median(q)),
                         "max": float(q.max())},
            "degree": {"min": int(d.min()), "median": float(np.median(d)),
                       "max": int(d.max())},
        }

    out = {
        "artifact": {"file": GRAPH.name, "sha256": digest, "N": n},
        "blank_name_nodes": {
            **summary(blank),
            "examples_mbid_disambig": [
                {"node": i, "mbid": store.mbids[i],
                 "disambiguation": store.disambiguations[i],
                 "pop_raw": float(pop[i]), "degree": int(deg[i])}
                for i in blank[:6]
            ],
            "why_it_matters": (
                "fame.py would resolve the empty string; has_non_latin('') is False and a "
                "Wikidata label search for '' finds nothing, so such a node scores F = 0 "
                "(the fame floor = maximal reach) AND is not flagged by the A11 notability "
                "guard. All 33 also collapse onto one fame key."),
        },
        "shared_name_nodes": {
            **summary(shared_nodes),
            "distinct_shared_names": len(shared),
            "why_it_matters": (
                "two different artists with the same name receive one fame value, whichever "
                "the resolver returns; C6's `distinct_interiors` under-counts by the same "
                "collapsing. resolve_names() in run_arms.py picks the highest-popularity "
                "duplicate for ENDPOINTS, but interiors are whatever the router visited."),
        },
        # How exposed is the obscure tail? Blank/shared nodes concentrated low in the
        # popularity distribution are exactly where a diving arm goes.
        "population_context": {
            "frac_of_all_nodes_below_pctl_0.10": float((ctx.pctl < 0.10).mean()),
            "frac_of_blank_below_pctl_0.10": (
                float((ctx.pctl[blank] < 0.10).mean()) if blank else None),
            "frac_of_shared_below_pctl_0.10": (
                float((ctx.pctl[shared_nodes] < 0.10).mean()) if shared_nodes else None),
        },
    }
    (HERE / "probe_name_keying.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                 encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
