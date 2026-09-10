"""`LBD-AM4-3` — do the served lineage's drop lists cover the fixed population `P`?

Run BEFORE the amendment was written (2026-09-10), because the amendment's drop-list
decision turns on the answer and nothing on disk recorded it.

`P` is the node set of `graph-cxa-adopted.bin`, sha256-verified against its manifest sidecar
and read through the SHIPPED `GraphStore` (the `cxr_added_set.py` precedent — never a second
parser). For each candidate drop list in the builder's package data, two questions:

  1. does its censused population cover `P`?  (`pipeline.py` raises `PopulationNotCensused`
     on any archive artist the census never evaluated; only the un-listenable list carries
     a census — the other two have no guard and would silently under-filter)
  2. how many members of `P` would it drop?

Run from the worktree's `api/` so the shipped parser is importable:

    cd <worktree>/api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u ../builder/analysis/2026-09-10-lbd-supply/lbd_population_coverage.py

Reads `builder/scratch/` by absolute path from the MAIN tree (`LBD-D8`); writes only its
JSON beside itself.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from artistpath_api.graph_store import GraphStore

HERE = Path(__file__).resolve().parent
SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
CXA = SCRATCH / "graph-cxa-adopted.bin"
DATA = HERE.parent.parent / "src" / "artistpath_builder" / "data"

LISTS = (
    "unlistenable_drop_algb_20260809.json",  # the re-censused payload (117,302)
    "unlistenable_drop_algb_20260805.json",  # the current DEFAULT (75,000)
    "no_release_drop_algb_20260802.json",
    "featured_credit_drop_algb_20260803_am1.json",
)


def verified_nodes(path: Path) -> tuple[set[str], str]:
    manifest = json.loads(path.with_suffix(".bin.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest["sha256"]:
        raise SystemExit(f"REFUSING: {path.name} sha256 {digest} != sidecar {manifest['sha256']}")
    store = GraphStore.load(path)
    return set(store.mbids), digest


def main() -> None:
    nodes, digest = verified_nodes(CXA)
    print(f"{CXA.name}  sha256 {digest}  nodes {len(nodes):,}")
    out: dict = {"artifact": CXA.name, "sha256": digest, "nodes": len(nodes), "lists": {}}
    for name in LISTS:
        payload = json.loads((DATA / name).read_text(encoding="utf-8"))
        drop = set(payload["drop_mbids"])
        row: dict = {"drop_list_size": len(drop), "drops_from_P": len(drop & nodes)}
        population = payload.get("population")
        if isinstance(population, dict) and "mbids" in population:
            censused = set(population["mbids"])
            row["censused"] = len(censused)
            row["P_uncovered"] = len(nodes - censused)
        else:
            row["censused"] = None
            row["P_uncovered"] = None  # no guard on this list
        out["lists"][name] = row
        print(f"  {name:<46} censused {row['censused']!s:>7}  P uncovered {row['P_uncovered']!s:>6}  drops from P {row['drops_from_P']}")
    (HERE / "lbd_population_coverage.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
