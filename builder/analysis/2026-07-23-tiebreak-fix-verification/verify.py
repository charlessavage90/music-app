"""Verify the tie-break-fix rebuild against Phase 1 log §2.8 Arm 2.

Asserts (a) the rebuilt artifact reproduces the Arm 2 topology — the
one-knob unclipped-ranking intervention — and (b) everything the fix must
NOT change is unchanged against adopted capfix: emitted scores on shared
edges are bit-identical, popularity ordering is preserved (values shift
only by the min/max renormalisation over a node set that regained
Radiohead).

Expected values are COPIES FOR EXECUTION, cited from Phase 1 log §2.8,
which owns them. Artifact-only; runs in seconds. Paths hardcoded — this is
a record of what was executed, not a maintained tool.
"""

import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore  # noqa: E402

CAPFIX = ROOT / "builder" / "scratch" / "graph-t15-capfix.bin"
NEW = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"

# Preconditions: measure the artifacts we think we have (log §5 checksums).
assert hashlib.sha256(CAPFIX.read_bytes()).hexdigest() == (
    "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237"
)
new_sha = hashlib.sha256(NEW.read_bytes()).hexdigest()

cap = GraphStore.load(CAPFIX)
new = GraphStore.load(NEW)


def node(g: GraphStore, name: str) -> int:
    """Resolve a name to its most popular node (duplicate names exist, §2.2)."""
    idx = [i for i, n in enumerate(g.names) if n == name]
    assert idx, f"{name!r} not found"
    return max(idx, key=lambda i: float(g.popularity[i]))


def degree(g: GraphStore, i: int) -> int:
    return int(g.offsets[i + 1] - g.offsets[i])


# --- (a) Arm 2 topology (all expected values: Phase 1 log §2.8) ------------
deg = np.diff(new.offsets)
assert new.artist_count == 74_193, new.artist_count
assert int(new.scores.size) == 898_006, new.scores.size
assert int(np.median(deg)) == 9, np.median(deg)
frac_lt8 = float((deg < 8).mean())
assert abs(frac_lt8 - 0.449) < 0.002, frac_lt8
assert int(deg.max()) <= 50, deg.max()

expected_degrees = {  # §2.8 Arm 2 column
    "Radiohead": 50,
    "The Beatles": 50,
    "Coldplay": 50,
    "R.E.M.": 47,
}
for name, want in expected_degrees.items():
    got = degree(new, node(new, name))
    assert got == want, f"{name}: degree {got}, expected {want}"
assert not [n for n in cap.names if n == "Radiohead"], (
    "capfix unexpectedly contains Radiohead — wrong baseline artifact?"
)

# --- (b) invariance against capfix ------------------------------------------


def edge_scores(g: GraphStore) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for u in range(g.artist_count):
        mu = g.mbids[u]
        for k in range(int(g.offsets[u]), int(g.offsets[u + 1])):
            out[(mu, g.mbids[int(g.neighbours[k])])] = float(g.scores[k])
    return out


cap_edges = edge_scores(cap)
new_edges = edge_scores(new)
shared = set(cap_edges) & set(new_edges)
assert len(shared) > 890_000, len(shared)
diffs = [k for k in shared if cap_edges[k] != new_edges[k]]
assert not diffs, f"{len(diffs)} shared edges changed score; first: {diffs[:3]}"

shared_mbids = sorted(set(cap.mbids) & set(new.mbids))
pc = np.array([cap.popularity[cap.id_by_mbid[m]] for m in shared_mbids])
pn = np.array([new.popularity[new.id_by_mbid[m]] for m in shared_mbids])
assert float(np.abs(pc - pn).max()) < 0.02, np.abs(pc - pn).max()
# Ordering preserved: rank vectors (double argsort) must correlate ~1.
rc = np.argsort(np.argsort(pc, kind="stable"), kind="stable").astype(float)
rn = np.argsort(np.argsort(pn, kind="stable"), kind="stable").astype(float)
assert float(np.corrcoef(rc, rn)[0, 1]) > 0.9999

print("ALL CHECKS PASSED")
print(f"graph-t15-tiebreakfix.bin sha256 = {new_sha}")
print(f"N={new.artist_count} E={new.scores.size}")
print(f"nodes only in new: {sorted(set(new.mbids) - set(cap.mbids))}")
print(f"shared edges: {len(shared)}  (capfix E={cap.scores.size})")
for name in expected_degrees:
    i = node(new, name)
    print(f"{name}: degree {degree(new, i)}, popularity {float(new.popularity[i]):.3f}")
