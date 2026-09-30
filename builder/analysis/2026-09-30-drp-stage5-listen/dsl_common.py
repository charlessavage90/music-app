"""Shared paths and constants for the `DSL-` blind listen (`DRP-AM7`), stage 5 of the #200 remedy.

Governing document: `docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md`,
§14 `DRP-AM7` (sub-items `-1`..`-12`). It wins wherever anything here disagrees with it.

**Adapted by copy** from `builder/analysis/2026-09-22-lba-a6-blind-listen/` (`DRP-AM7-12`), whose
files stay frozen as the `LAL-` record. From that directory this harness imports only PURE functions
(`lal_prescreen.draw`, `rank_key`; `lal_pool_am7.presented_endpoints`) and reads its pair and pool
files as DATA, sha-pinned. The routing is the lattice's own code, imported unchanged
(`dsl_journeys.py`), so `DSL-G1` tests the code that produced the stage-3 result.

Every input pin is a sha256 of **LF-normalised** bytes: this repo checks out with `autocrlf=true`,
so a working copy's raw bytes hash differently from the committed blob (stage-3d handoff).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ANALYSIS = ROOT / "builder" / "analysis"

SEALED_DIR = ROOT / ".superpowers" / "dsl"   # gitignored; side-identifying output only

LAL_DIR = ANALYSIS / "2026-09-22-lba-a6-blind-listen"
DRP_3A = ANALYSIS / "2026-09-27-drp-stage3a"
DRP_3B = ANALYSIS / "2026-09-28-drp-stage3b"

# ---- pinned inputs (DRP-AM7-2), LF-normalised sha256 -------------------------------------------
KNOWN_POOL = LAL_DIR / "lal_am7_known.json"          # step 1: the artists he vetted by name
KNOWN_POOL_SHA = "22f4fe351fbb1975a05b65735e8b0a20032f00dc943dac7f890277ed53ec5c27"
FAMILIAR = LAL_DIR / "lal_am7_familiar.json"          # step 6 Gate N: counts, never excludes
FAMILIAR_SHA = "5f386d74f58219c732a91cfe218fb9b99ee9e625b0256414b568b6b862c5487f"
LAL_PAIRS = LAL_DIR / "lal_pairs.json"                # step 2: LAL-'s eight primaries
LAL_PAIRS_SHA = "2aaa21f99ce9ed080dfa99a629c1b8f0a6ba0653ffae232129789283d15e7201"
G5_LOG = LAL_DIR / "lba_g5_pair_log.md"               # step 2: his unblinded use of today's map
G5_LOG_SHA = "8cd286afb9544987d327eff80cf464c1415af77ba67e953f3e0dac1ff2e31e56"
EXPLORATION_PAIRS = ROOT / "exploration" / "pairs-used.txt"   # step 2: the practice room
EXPLORATION_PAIRS_SHA = "6fbcefd5be05838c1fc134ef98299f382efa880a3fc9edc0f939562f08455f8f"
DRP_PAIRS = DRP_3A / "drp_pairs.json"                 # step 3: the lattice's pairs, banned as pairs
DRP_PAIRS_SHA = "b1f9f50d7c1ce2597cfaac25c5534766c2e41ce3d0242cbf7f3cdad94b9ef472"
CELL_A0 = DRP_3B / "cells" / "DRP-S0P0.json"          # DSL-G1's reference journeys
CELL_A0_SHA = "339998556fcd91f9287a026746e2fe7185cbaa44eb25129135a61b35d588a113"
CELL_S1P3 = DRP_3B / "cells" / "DRP-S1P3.json"
CELL_S1P3_SHA = "2937eee2a38026259d3a9e3d50b8b4cca58a6d50f7e1cd11789303268400d4ad"

# ---- this listen's own files ------------------------------------------------------------------
G1_RESULT = HERE / "dsl_g1.json"                      # DSL-G1's outcome; counts only
# The post-strike pair file (DRP-AM7-2 step 9). Pinned here, by commit, after the owner's strike;
# empty until then, so generation refuses rather than running on an un-struck draw.
DSL_PAIRS = HERE / "dsl_pairs.json"
DSL_PAIRS_SHA = ""

# ---- DRP-AM7 constants -------------------------------------------------------------------------
ROLES = ("incumbent", "challenger")   # today's app (A0), DRP-S1P3. Sealed, never shown.
TIERS = ("DRP-T1", "DRP-T2")          # drp_common.STRATA's famous bands, read from there
DEPTHS = (5, 10, 20)                  # DRP-AM7-3
TOKENS = ("L", "R")
PAIRS_PER_TIER = 4                    # DRP-AM7-2 step 8
RESERVES_PER_TIER = 2
PAIRS_PER_LISTEN = PAIRS_PER_TIER * len(TIERS)
MIN_INTERIOR = 3                      # Gate L
MARGIN = 8                            # DRP-AM7-7: ceil(0.3 * 24)
UNDERPOWERED_CLIP_ROWS = 8
CLIPS_PER_ARTIST = 3
AXES = {"q1": "coherence", "q2": "novelty"}   # DSL-Q1, DSL-Q2
STRENGTHS = ("slight", "strong")              # DSL-Q3
IDENTIFY = ("no", "yes_left", "yes_right")    # DSL-Q4
DSL_P_MIN_N = 10                              # DRP-AM7-8
DSL_E_MIN_MARKS = 8                           # DRP-AM7-9 (S5R-4)
DSL_E_RATIO = 1.5
FAME_BANDS = ((0.60, 0.70), (0.70, 0.80), (0.80, 0.90), (0.90, 0.99))   # DRP-AM7-8, half-open


def sha256_lf(path: Path) -> str:
    """sha256 of the file's bytes with CRLF normalised to LF: the committed blob's identity."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def pinned_text(path: Path, sha: str) -> str:
    got = sha256_lf(path)
    if got != sha:
        raise SystemExit(f"REFUSING: {path.name} sha256 (LF) {got} is not the pinned {sha}")
    return path.read_text(encoding="utf-8")


def pinned_json(path: Path, sha: str):
    return json.loads(pinned_text(path, sha))


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
