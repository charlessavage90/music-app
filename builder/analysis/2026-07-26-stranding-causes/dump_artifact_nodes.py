"""Dump the adopted artifact's node table so builder-side code can read it.

READ-ONLY. Asserts the artifact sha256, then writes mbid/name/degree/pop_raw for
every node. Exists only because `builder/` and `api/` share no code by design —
the APG1 reader lives in `api/`, and the builder's `is_special_purpose` (which
`split_causes.py` must import rather than reimplement) lives in `builder/`. One
of them has to cross the gap as data, and data is the safer direction.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-26-stranding-causes/dump_artifact_nodes.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
HERE = Path(__file__).resolve().parent


def main() -> None:
    path = Path(ApiConfig().graph_path).resolve()
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    got = digest.hexdigest()
    if got != ADOPTED_SHA256:
        raise SystemExit(
            f"artifact is not the adopted graph.\n  expected {ADOPTED_SHA256}\n"
            f"  got      {got}\nSee findings/2026-07-23-tiebreak-fix-adoption.md."
        )
    print(f"artifact verified: {path}\n  sha256 {got}")

    store = GraphStore.load(str(path))
    offsets = np.asarray(store.offsets, dtype=np.int64)
    degree = np.diff(offsets)
    pop_raw = np.asarray(store.pop_raw, dtype=np.float64)

    out = {
        "artifact_sha256": got,
        "nodes": len(store.mbids),
        "mbids": list(store.mbids),
        "names": list(store.names),
        "degree": [int(d) for d in degree],
        "pop_raw": [float(p) for p in pop_raw],
    }
    dest = HERE / "artifact_nodes.json"
    dest.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"nodes {len(store.mbids)}")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
