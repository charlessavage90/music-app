"""Shared paths and constants for the GBL- blind listen harness.

Governing document: docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md.
It wins wherever anything here disagrees with it. Reuses the frozen CRE- harness;
figures (ramp size, sha256s) are imported from it, never restated here.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

CRE_DIR = ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"
SEALED_DIR = ROOT / ".superpowers" / "gbl"   # gitignored; arm-identifying output only

DEPTHS = (0, 10, 20)      # spec §3: d0 anchor + the two deep rows
TOKENS = ("L", "R")
ARMS = ("V0", "G")        # never written into page-facing output


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


def sealed_path(arg: str) -> Path:
    name = _bare(arg)
    SEALED_DIR.mkdir(parents=True, exist_ok=True)
    return SEALED_DIR / name
