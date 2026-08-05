"""Shared paths and constants for the CAU- coherence audit.

Governing document:
docs/superpowers/specs/2026-08-04-coherence-audit-preregistration.md, frozen before
generation and amended by CAU-AM1 (whole journeys, 65 interior slots) and CAU-AM2
(bar ratified at 75%; injected artists must sit at graph distance >= 3 from both
displayed neighbours). It wins wherever anything here disagrees with it.

Reuses the frozen CRE- harness and the committed GBL- journeys. No shipped code is
touched and no graph is rebuilt.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

CRE_DIR = ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"
GBL_DIR = ROOT / "builder" / "analysis" / "2026-08-04-gentle-arm-blind-listen"
SEALED_DIR = ROOT / ".superpowers" / "cau"   # gitignored; injection identity only

DEEP = (10, 20)          # spec §2: the deep rows only; d0 is not audited
CELL = "B-S1"            # the G arm's artifact (spec §2)

N_INJECT = 12            # spec §4, unchanged by both amendments
G1_BAR = 10              # CAU-G1: at least 10 of 12 rejected, or the audit is VOID
C1_PASS = 0.75           # CAU-C1 upper branch, ratified by the owner (CAU-AM2)
C1_FAIL = 0.50           # CAU-C1 lower branch
C2_TRIGGER = 3           # CAU-C2: any single journey with >= 3 DOESN'T FIT
C3_TRIGGER = 0.15        # CAU-C3: residual CAN'T TELL above this falsifies §0

MIN_INJECT_DISTANCE = 3  # CAU-AM2: no edge and no shared neighbour

# CAU-AM3: controls sit endpoint-adjacent, so each touches exactly ONE real card,
# and that card is judged but NOT scored. Presented real slots stay 65; D_all is 53.
PRESENTED_REAL = 65
SCORED_REAL = 53

VERDICTS = ("fits", "doesnt_fit", "cant_tell")


def use_cre() -> None:
    p = str(CRE_DIR)
    if p not in sys.path:
        sys.path.insert(0, p)


def _bare(arg: str) -> str:
    if Path(arg).name != arg or arg in ("", ".", ".."):
        raise ValueError(f"expected a bare filename, got {arg!r}")
    return arg


def in_dir(arg: str) -> Path:
    return HERE / _bare(arg)


def gbl_file(arg: str) -> Path:
    return GBL_DIR / _bare(arg)


def sealed_path(arg: str) -> Path:
    name = _bare(arg)
    SEALED_DIR.mkdir(parents=True, exist_ok=True)
    return SEALED_DIR / name


def slot_id(journey_id: str, position: int) -> str:
    """A slot is (journey, position-in-journey). CAU-AM1: the same artist in two
    journeys is two judgements, because fit is contextual."""
    return f"{journey_id}#{position}"
