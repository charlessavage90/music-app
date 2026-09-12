"""Shared paths and constants for the `LBL-` blind listen (`LBD-AM5`).

Governing document: `docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`,
the `LBD-AM5` block in §10 and its §12 register row. It wins wherever anything here disagrees
with it. The protocol is the `GBL-` one (`specs/2026-08-04-gentle-arm-blind-listen-design.md`)
with the corrections its own results note (§6) records for the next listen; the harness is
modelled on `builder/analysis/2026-08-04-gentle-arm-blind-listen/`, which is frozen and is
imported from nowhere here.

Reads `builder/scratch/` by absolute path from the MAIN tree and never writes into it.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

SEALED_DIR = ROOT / ".superpowers" / "lbl"   # gitignored; arm-identifying output only

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
SERVED = SCRATCH / "graph-msw-tu50.bin"       # `ApiConfig.graph_path`'s default; population V
PRODUCTION = SCRATCH / "graph-lux4.bin"        # what the deploy serves; routing-identical (gated)

GBL_DIR = ROOT / "builder" / "analysis" / "2026-08-04-gentle-arm-blind-listen"
GBL_CANDIDATES = GBL_DIR / "gbl_pair_candidates.json"
GBL_APPROVED = GBL_DIR / "gbl_pairs_approved.json"
# `GBL-AM1`'s binding artifact, as that amendment records it.
GBL_APPROVED_SHA = "9831f77f8263894855726ac010908fb7b87e25aabfe83d54d3c39687f3ab623c"

A0_PARQUET = Path(r"C:\unsung-fast\lbd-pairs\A0\A0.parquet")
A0_MANIFEST = A0_PARQUET.with_name("A0.manifest.json")

DEPTHS = (0, 10, 20)          # the GBL- depths
TOKENS = ("L", "R")
PAIRS_PER_LISTEN = 8
RESERVES_PER_LISTEN = 4

PAIRS_FILE = HERE / "lbl_pairs.json"
PAIRS_SHA = "da2ad2d71f5ee2f517a25477d9ba0899763f4066c20ae24aa0b4c5700062c3c9"   # LBD-AM5-5
MAPS_PIN = HERE / "lbl_maps.json"   # each listen's two maps and their sha256s, from the Step 2 build records

# LBD-AM5-5. The challenger is the LBD- map; the incumbent is the other. Arm roles are written ONLY
# to the sealed file. Listen 2 is added here only after the owner has heard listen 1.
ROLES = ("incumbent", "challenger")
LISTENS = (1,)
MARGIN = 8                    # ceil(0.3 * 24): GBL-'s scaling rule over 8 pairs x 3 depths
CLIPS_PER_ARTIST = 3          # CAU- §2.3: one clip is not enough for an unfamiliar artist
AXES = {"q1": "coherence", "q2": "novelty"}   # LBL-Q1, LBL-Q2


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def use_api_src() -> None:
    p = str(ROOT / "api" / "src")
    if p not in sys.path:
        sys.path.insert(0, p)


def verified_store(path: Path):
    """(GraphStore, sidecar manifest, sha256) — refused unless the bytes match the sidecar.

    Artifacts under `scratch/` are gitignored and not interchangeable; the sidecar is their
    only identity. Parsed by the SHIPPED `GraphStore`, never a second parser.
    """
    use_api_src()
    from artistpath_api.graph_store import GraphStore

    manifest = json.loads(path.with_suffix(path.suffix + ".json").read_text(encoding="utf-8"))
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != manifest["sha256"]:
        raise SystemExit(f"REFUSING: {path.name} sha256 {digest} != sidecar {manifest['sha256']}")
    store = GraphStore.from_bytes(payload)
    if len(store.mbids) != manifest["artists"]:
        raise SystemExit(f"REFUSING: {path.name} node count disagrees with its sidecar")
    return store, manifest, digest


def load_map(path: Path, pinned_sha: str) -> dict:
    """One map for a listen: refused unless its bytes match BOTH its sidecar and the pinned sha.

    Also returns the raw `fame_lb` from the metadata blob (the shipped `GraphStore` keeps only
    percentiles), located exactly as `graph_store.py` locates it and checked against its node order:
    the press rule needs to know which artists ListenBrainz reported no listeners for.
    """
    use_api_src()
    import artistpath_api.graph_store as gs

    manifest = json.loads(path.with_suffix(path.suffix + ".json").read_text(encoding="utf-8"))
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != manifest["sha256"] or digest != pinned_sha:
        raise SystemExit(f"WRONG ARTIFACT: {path.name} sha256 {digest}; sidecar {manifest['sha256']}; "
                         f"pinned {pinned_sha}")
    store = gs.GraphStore.from_bytes(payload)
    _magic, _version, n, e, meta_len = gs._HEADER.unpack_from(payload)
    cursor = gs._HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor : cursor + meta_len])
    if list(meta["mbids"]) != list(store.mbids):
        raise SystemExit(f"WRONG ARTIFACT: {path.name} metadata disagrees with the shipped parser")
    if store.fame_lb_pctl is None or "fame_lb" not in meta:
        raise SystemExit(f"WRONG ARTIFACT: {path.name} carries no fame; the router's ramp cannot price it")
    return {"path": path, "sha256": digest, "store": store, "raw_fame": list(meta["fame_lb"])}


def _bare(arg: str) -> str:
    if Path(arg).name != arg or arg in ("", ".", ".."):
        raise ValueError(f"expected a bare filename, got {arg!r}")
    return arg


def in_dir(arg: str) -> Path:
    return HERE / _bare(arg)


def sealed_path(arg: str) -> Path:
    name = _bare(arg)
    SEALED_DIR.mkdir(parents=True, exist_ok=True)
    return SEALED_DIR / name
