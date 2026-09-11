"""`LBD-AM5` pre-measurement — do the drop lists cover the SERVED population `V`?

`lbd_population_coverage.py`'s shape (the `LBD-AM4-3` measurement), over `V` — the node set of
`graph-msw-tu50.bin` — instead of `P`. Run BEFORE the amendment is written, because its
drop-list clause turns on the answer and nothing on disk records it for `V`.

For each candidate list in the builder's package data:

  1. does its censused population cover `V`?  (only the un-listenable list carries a census;
     `pipeline.py` raises `PopulationNotCensused` on an archive artist it never evaluated —
     the emitter only ever writes members of `V`, so covering `V` is covering the archive)
  2. how many members of `V` would it drop?

And one identity check, because it is the cheapest proof that `V` was read correctly: `V ∩ P`
must equal the pinned pre-existing set (`cxr_preexisting_mbids.txt`) exactly, which is how
`cxr_added_set.py` defined that file. `V − P` is counted and listed.

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u analysis/2026-09-10-lbd-served-population/lbv_coverage.py

Reads `builder/scratch/` by absolute path from the MAIN tree; writes only its JSON beside itself.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
SERVED = SCRATCH / "graph-msw-tu50.bin"
CXA = SCRATCH / "graph-cxa-adopted.bin"
DATA = REPO / "builder" / "src" / "artistpath_builder" / "data"
PREEXISTING = Path(r"D:\unsung-large-data\lbd-inputs\cxr_preexisting_mbids.txt")
PREEXISTING_SHA = "768054b7e84769346193336ec7e9b3496af92d0d3e8d4ae2fb287057912b5229"

LISTS = (
    "unlistenable_drop_algb_20260809.json",  # the payload LBD-AM4 built the fixed-population arms with
    "unlistenable_drop_algb_20260805.json",  # the payload the served lineage was built with (graph-lux4.bin.json)
    "no_release_drop_algb_20260802.json",
    "featured_credit_drop_algb_20260803_am1.json",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verified_nodes(path: Path) -> tuple[set[str], str]:
    manifest = json.loads(path.with_suffix(".bin.json").read_text(encoding="utf-8"))
    payload = path.read_bytes()
    digest = sha256_bytes(payload)
    if digest != manifest["sha256"]:
        raise SystemExit(f"REFUSING: {path.name} sha256 {digest} != sidecar {manifest['sha256']}")
    return set(GraphStore.from_bytes(payload).mbids), digest


def main() -> int:
    v, v_sha = verified_nodes(SERVED)
    p, p_sha = verified_nodes(CXA)
    pre_bytes = PREEXISTING.read_bytes()
    if sha256_bytes(pre_bytes) != PREEXISTING_SHA:
        raise SystemExit(f"REFUSING: {PREEXISTING.name} is not the pinned pre-existing set")
    pre = {line.strip() for line in pre_bytes.decode("utf-8").splitlines() if line.strip()}
    if v & p != pre:
        raise SystemExit(f"REFUSING: V ∩ P ({len(v & p):,}) is not the pinned pre-existing set ({len(pre):,})")
    v_only = sorted(v - p)
    print(f"V = {SERVED.name} sha256 {v_sha}  nodes {len(v):,};  V ∩ P = pre-existing {len(pre):,} (exact);  V − P {len(v_only)}")

    out: dict = {
        "served": {"artifact": SERVED.name, "sha256": v_sha, "nodes": len(v)},
        "extended": {"artifact": CXA.name, "sha256": p_sha, "nodes": len(p)},
        "V_intersect_P_equals_pinned_preexisting": True,
        "preexisting": {"file": str(PREEXISTING), "sha256": PREEXISTING_SHA, "count": len(pre)},
        "V_minus_P": {"count": len(v_only), "mbids": v_only},
        "lists": {},
    }
    for name in LISTS:
        payload = (DATA / name).read_bytes()
        doc = json.loads(payload)
        drop = set(doc["drop_mbids"])
        row: dict = {"sha256": sha256_bytes(payload), "drop_list_size": len(drop), "drops_from_V": len(drop & v)}
        population = doc.get("population")
        if isinstance(population, dict) and "mbids" in population:
            censused = set(population["mbids"])
            row["censused"] = len(censused)
            row["V_uncovered"] = len(v - censused)
        else:
            row["censused"] = None
            row["V_uncovered"] = None  # no guard on this list
        out["lists"][name] = row
        print(f"  {name:<46} censused {row['censused']!s:>7}  V uncovered {row['V_uncovered']!s:>6}  drops from V {row['drops_from_V']}")
    (HERE / "lbv_coverage.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
