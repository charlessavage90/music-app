"""Demonstrate the G1 acceptance check at full scale, on both real artifacts.

The in-suite negative case (`tests/test_acceptance.py`) reproduces the §2.8
defect in miniature, where k=4 caps every degree at 4 and the signature is
therefore *deletion* only. This script is the other half: it runs the real
acceptance criteria against the two real 75k artifacts, where the
famous-degree collapse is visible as well, and shows that the criteria
accept the adopted graph and reject the defective one.

⚠ ERA-PINNED 2026-08-06: it now uses `PRE_MSW_ACCEPTANCE`, not
`PRODUCTION_ACCEPTANCE` — see the comment at that definition. The famous-degree
separating statistic, which is this script's actual subject, still tracks
shipped code; only the two global bounds are frozen at their 75k-era values.

`graph-t15-capfix.bin` is the defective artifact: Phase 1 log §2.8 records
that its Arm 1 replay reproduced capfix exactly — N, E, MBID set, and every
per-artist degree — which is what makes it usable as a negative case here.

Figures printed below are measurements, not a record: the artifacts' identity
is owned by findings/2026-07-23-tiebreak-fix-adoption.md and the defect by
Phase 1 log §2.8. Paths hardcoded — a record of what was executed, not a
maintained tool.
"""

import hashlib
import statistics
import sys
from pathlib import Path

import numpy as np
from dataclasses import replace

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "builder" / "src"))
from artistpath_builder.acceptance import (  # noqa: E402
    PRODUCTION_ACCEPTANCE,
    ArtifactRejected,
    check_acceptance,
)
from artistpath_builder.artifact import deserialise  # noqa: E402

# ERA-PINNED 2026-08-06 (MSW- Task 9). PRODUCTION_ACCEPTANCE's node and edge
# bounds were recalibrated from the retired 75k map to the candidate map at the
# map switch. This probe's whole subject is the top-25 median-degree SEPARATING
# STATISTIC, demonstrated on two 75k-era artifacts — so following that change
# would make it report "ADOPTED was rejected but must be accepted" and destroy
# what it was written to show. The two era-dependent global bounds are pinned
# to their pre-adoption values; everything else, including the separating
# statistic itself, deliberately still tracks shipped code.
#
# Same pattern the plan applies to the three BuilderConfig callers at Task 11
# Step 0, and the same reason: an analysis harness must not silently change
# what it measures when a shipped default moves.
PRE_MSW_ACCEPTANCE = replace(
    PRODUCTION_ACCEPTANCE,
    node_count=(60_000, 90_000),
    edge_count=(700_000, 1_100_000),
)

ADOPTED = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
DEFECTIVE = ROOT / "builder" / "scratch" / "graph-t15-capfix.bin"

# Preconditions: log §5 / adoption-record checksums.
SHA = {
    ADOPTED: "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8",
    DEFECTIVE: "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237",
}


def load(path: Path):
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    assert actual == SHA[path], f"{path.name}: sha256 {actual}, expected {SHA[path]}"
    return deserialise(payload)


def separating_statistics(graph) -> str:
    degrees = np.diff(graph.offsets).astype(np.int64)
    order = np.argsort(-np.asarray(graph.popularity, dtype=np.float64), kind="stable")
    sample = degrees[order[: PRE_MSW_ACCEPTANCE.famous_sample]]
    return (
        f"N={graph.artist_count} E={graph.edge_count} "
        f"median_degree={statistics.median(degrees.tolist())} | "
        f"top-{PRE_MSW_ACCEPTANCE.famous_sample} median degree "
        f"{statistics.median(sample.tolist())}, min {int(sample.min())}"
    )


failures = []
for label, path, must_pass in (
    ("ADOPTED  ", ADOPTED, True),
    ("DEFECTIVE", DEFECTIVE, False),
):
    graph = load(path)
    print(f"\n=== {label} {path.name}")
    print(f"    {separating_statistics(graph)}")
    try:
        check_acceptance(graph, PRE_MSW_ACCEPTANCE)
        print("    ACCEPTED")
        if not must_pass:
            failures.append(f"{path.name} was accepted but must be rejected")
    except ArtifactRejected as exc:
        print(f"    REJECTED — {exc}")
        if must_pass:
            failures.append(f"{path.name} was rejected but must be accepted")

print()
if failures:
    print("FAILED:")
    for line in failures:
        print(" -", line)
    raise SystemExit(1)
print("PASS — the criteria accept the adopted artifact and reject the defective one.")
