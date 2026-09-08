"""`LBD-` Task 1 — derive and PIN the `CXR` added artist set.

The set `LBD-C2` is measured over: MBIDs present in `graph-cxa-adopted.bin` and
absent from `graph-msw-tu50.bin`, read through the SHIPPED `GraphStore` exactly as
`builder/analysis/2026-09-01-cxr-regression-diagnosis/cxr_census.py` does. A second
parser here could disagree with what the API actually loads, which is the defect
class the `JFX-` mirror re-verification exists to catch.

Both artifacts are sha256-verified against their own `.bin.json` manifest sidecars
before being read. Artifacts under `builder/scratch/` are gitignored and NOT
interchangeable; the sha is the only identity they have.

Writes the pinned MBID list (sorted, newline-delimited) to
`D:\\unsung-large-data\\lbd-inputs\\cxr_added_mbids.txt` and prints its sha256.
Nothing is written into `builder/scratch/` (`LBD-D8`).

Run from the worktree's `api/` so the shipped parser is importable:

    cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-07-lbd-inputs/cxr_added_set.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from artistpath_api.graph_store import GraphStore

# The MAIN tree's scratch, read by absolute path. This script runs from a worktree
# (`LBD-` plan global constraints); the worktree has no `builder/scratch/`.
SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
OLD = SCRATCH / "graph-msw-tu50.bin"  # the served map
NEW = SCRATCH / "graph-cxa-adopted.bin"  # CXA-, adopted 2026-08-10, reverted 2026-09-01

OUT_DIR = Path(r"D:\unsung-large-data\lbd-inputs")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verified_load(path: Path) -> GraphStore:
    """Load an artifact only after its bytes match its manifest sidecar."""
    manifest = json.loads(path.with_suffix(".bin.json").read_text())
    expected = manifest["sha256"]
    actual = sha256_file(path)
    if actual != expected:
        raise SystemExit(
            f"REFUSING TO READ {path.name}: sha256 {actual} != manifest {expected}"
        )
    print(f"  {path.name:<26} sha256 {actual}  OK  ({manifest['artists']:,} artists)")
    return GraphStore.load(path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Verifying artifact identity against manifest sidecars")
    old = verified_load(OLD)
    new = verified_load(NEW)

    old_ids = set(old.mbids)
    added = sorted(m for m in new.mbids if m not in old_ids)
    common = [m for m in new.mbids if m in old_ids]

    print()
    print(f"served map   {len(old.mbids):>7,} artists")
    print(f"cxa-adopted  {len(new.mbids):>7,} artists")
    print(f"ADDED        {len(added):>7,}   pre-existing {len(common):>7,}")

    # Degree of the added set in the artifact they were added by, so this file's
    # figures are checkable against CXR-P2's owner rather than merely asserted.
    degrees = np.diff(new.offsets).astype(np.int64)
    new_ids = {m: i for i, m in enumerate(new.mbids)}
    d_added = degrees[np.array([new_ids[m] for m in added], dtype=np.int64)]
    d_common = degrees[np.array([new_ids[m] for m in common], dtype=np.int64)]
    for label, arr in (("added", d_added), ("pre-existing", d_common)):
        share_le2 = 100.0 * float((arr <= 2).sum()) / len(arr)
        print(
            f"  {label:<13} n={len(arr):>7,}  median {np.median(arr):>5.1f}  "
            f"mean {arr.mean():>6.2f}  share<=2 {share_le2:>6.2f}%"
        )

    out = OUT_DIR / "cxr_added_mbids.txt"
    out.write_text("\n".join(added) + "\n", encoding="utf-8")
    print()
    print(f"wrote {out}")
    print(f"  rows   {len(added):,}")
    print(f"  sha256 {sha256_file(out)}")

    # Also pin the pre-existing set: item 8 of the derivation's list makes it the
    # within-arm reference in every arm, and it must be the same set every time.
    out_pre = OUT_DIR / "cxr_preexisting_mbids.txt"
    out_pre.write_text("\n".join(sorted(common)) + "\n", encoding="utf-8")
    print(f"wrote {out_pre}")
    print(f"  rows   {len(common):,}")
    print(f"  sha256 {sha256_file(out_pre)}")


if __name__ == "__main__":
    sys.exit(main())
