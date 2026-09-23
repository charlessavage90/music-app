"""Shared paths and constants for the `LAL-` blind listen (`LBA-AM6`).

Governing document: `docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md`, §11,
`LBA-AM6` (sub-items `-1`..`-11`). It wins wherever anything here disagrees with it.

**Adapted by copy** from `builder/analysis/2026-09-10-lbd-blind-listen/` (`LBA-AM6-11`), whose files
stay frozen as the record of listens 1 and 2 and are imported from nowhere here. What is read from
that directory is DATA — the two listens' pair files, sha-pinned — never code.

Reads `builder/scratch/` and `C:\\unsung-fast\\lbd-artifacts\\` by absolute path and never writes
into either.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

SEALED_DIR = ROOT / ".superpowers" / "lal"   # gitignored; map-identifying output only

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
SERVED = SCRATCH / "graph-msw-tu50.bin"       # `ApiConfig.graph_path`'s default — the incumbent
PRODUCTION = SCRATCH / "graph-lux4.bin"        # what the deploy serves; routing-identical (gated)
CANDIDATE = Path(r"C:\unsung-fast\lbd-artifacts\LBA-A6-candidate.bin")   # the challenger

GBL_DIR = ROOT / "builder" / "analysis" / "2026-08-04-gentle-arm-blind-listen"
GBL_CANDIDATES = GBL_DIR / "gbl_pair_candidates.json"
GBL_APPROVED = GBL_DIR / "gbl_pairs_approved.json"
# `GBL-AM1`'s binding artifact, as that amendment records it.
GBL_APPROVED_SHA = "9831f77f8263894855726ac010908fb7b87e25aabfe83d54d3c39687f3ab623c"

LBL_DIR = ROOT / "builder" / "analysis" / "2026-09-10-lbd-blind-listen"
LBL_PAIRS1 = LBL_DIR / "lbl_pairs.json"      # listen 1's primaries and reserves (`LBD-AM5-5`)
LBL_PAIRS1_SHA = "da2ad2d71f5ee2f517a25477d9ba0899763f4066c20ae24aa0b4c5700062c3c9"
LBL_PAIRS2 = LBL_DIR / "lbl_pairs2.json"     # listen 2's primaries and reserves (`LBD-AM6`)
LBL_PAIRS2_SHA = "0a2eca01c22985991da0d3628b42d8021c4089ec81227a4b786a6c613c9be0f7"

MAPS_PIN = HERE / "lal_maps.json"   # written by `lal_pin_maps.py` from the sidecars, never by hand

# The post-strike pair file (`LBA-AM6-2` step 9). Pinned here, by commit, after the owner's strike;
# empty until then, so generation refuses rather than running on an un-struck draw.
LAL_PAIRS = HERE / "lal_pairs.json"
LAL_PAIRS_SHA = "b28d1d2b3db099f6fa4b25eb1edfbd67fc91ebbd5212fb80ea1241f695433a24"   # owner's strike 2026-09-23: none

ROLES = ("incumbent", "challenger")   # served map, `LBA-A6` candidate. Roles are sealed, never shown.
DEPTHS = (0, 10, 20)                  # `LBA-AM6-3`
TOKENS = ("L", "R")
PAIRS_PER_LISTEN = 8                  # `LBA-AM6-2` step 8
RESERVES_PER_LISTEN = 4
MIN_INTERIOR = 3                      # `LBA-AM6-2` Gate L: at every depth, on both maps
MARGIN = 8                            # `LBA-AM6-7`: ceil(0.3 * 24)
UNDERPOWERED_CLIP_ROWS = 8            # `LBA-AM6-7`: no-preference rows carrying the clip-problem box
CLIPS_PER_ARTIST = 3                  # `LBA-AM6-4`
AXES = {"q1": "coherence", "q2": "novelty"}   # `LAL-Q1`, `LAL-Q2`
STRENGTHS = ("slight", "strong")              # `LAL-Q3`
IDENTIFY = ("no", "yes_left", "yes_right")    # `LAL-Q4`


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar(path: Path) -> dict:
    return json.loads(path.with_suffix(path.suffix + ".json").read_text(encoding="utf-8"))


def use_api_src() -> None:
    p = str(ROOT / "api" / "src")
    if p not in sys.path:
        sys.path.insert(0, p)


def read_pins() -> dict:
    return json.loads(MAPS_PIN.read_text(encoding="utf-8"))


def load_map(path: Path, pinned_sha: str) -> dict:
    """One map for the listen: refused unless its bytes match BOTH its sidecar and the pinned sha.

    Also returns the raw `fame_lb` from the metadata blob (the shipped `GraphStore` keeps only
    percentiles), located exactly as `graph_store.py` locates it and checked against its node order:
    the press rule needs to know which artists ListenBrainz reported no listeners for.
    """
    use_api_src()
    import artistpath_api.graph_store as gs

    manifest = sidecar(path)
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
    return {"path": path, "sha256": digest, "store": store, "raw_fame": list(meta["fame_lb"]),
            "deezer_ids": list(meta.get("deezer_ids") or [])}


def load_pinned_maps() -> dict:
    """Both roles' maps from `lal_maps.json`, each verified against its sidecar and its pin."""
    pins = read_pins()
    return {role: load_map(Path(pins[role]["path"]), pins[role]["sha256"]) for role in ROLES}


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
