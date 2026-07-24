"""The Stage A arm definitions, in one place, with their isolating baselines.

Pre-registration §1.4. Kept declarative and separate from the walker so the factor
table can be read off the code and checked against the document — the CLAUDE.md
factor-table discipline applied to the harness rather than to a plan.

**Two stages, and this is a structural property of the design, not a convenience.**
The attachment arms are defined as *W + one knob*, and **W is chosen from the
factorial results by rule R1**. So the sweep cannot be run as one batch:

    stage 1 (11 runs)  P, A0-A7, A1u, X
    -> apply R1 to the stage-1 C1 statistics -> W
    stage 2 (4 runs)   T1a, T1b, FL1, FL2   (each = W + one knob)

`STAGE1` is therefore complete and runnable now; `stage2(W)` builds the rest once W
exists. Nothing here picks W — that is R1's job, on data.

Guard G is ON in every arm including P (§1.2). The byte-identity verification that
required G off was step 2 and is finished.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-07-23-track2-sweep"))

from mirror import PCTL, SweepConfig  # noqa: E402

# §1.2: snapshots. The walk visits every depth 0..20 regardless, so this is a
# recording decision, not a compute cost. Early depths added by amendment A2,
# where the floor device is still alive.
SNAPSHOTS = (0, 1, 2, 3, 5, 7, 10, 15, 20)
MAX_DEPTH = 20

# §2.1: the primary contrast C1 is paired over cells at depth >= 10.
C1_DEPTHS = tuple(d for d in SNAPSHOTS if d >= 10)


@dataclass(frozen=True, slots=True)
class Arm:
    name: str
    cfg: SweepConfig
    baseline: str | None   # the arm differing by exactly one column
    reading: str           # what a contrast against `baseline` is licensed to say
    adoptable: bool = True


def _P() -> SweepConfig:
    """Production, with guard G on. The user-facing comparison baseline."""
    return SweepConfig.production().with_(guard_min_intermediary=True)


P = _P()
_FACTORIAL_BASE = P.with_(w_floor=0.0)  # floor off; A0 is this cell exactly

_CELLS = {
    #            J-cur  J-mag  S-mag   baseline  reading
    "A0": (None, 1.0, 3.0, "P", "anchor (floor off)"),
    "A1": (PCTL, 1.0, 3.0, "A0", "currency alone"),
    "A2": (None, 0.3, 3.0, "A0", "cliff strength alone, raw"),
    "A3": (None, 1.0, 1.5, "A0", "dive barrier alone"),
    "A4": (PCTL, 0.3, 3.0, "A1", "cliff strength under pctl"),
    "A5": (PCTL, 1.0, 1.5, "A1", "dive barrier under pctl"),
    # NB: read the reading against the NAMED baseline, which is one column away.
    # A6/A7 are the "joint magnitude" cells only when read against A0 — that is the
    # two-/three-column package comparison §1.4 warns cannot be attributed to a
    # single knob. Against A2/A4 they are ordinary one-column contrasts.
    "A6": (None, 0.3, 1.5, "A2", "dive barrier under a cheapened cliff, raw"),
    "A7": (PCTL, 0.3, 1.5, "A4", "dive barrier under a cheapened cliff, pctl"),
}


def _factorial() -> list[Arm]:
    arms = []
    for name, (cur, wj, ws, base, reading) in _CELLS.items():
        cfg = _FACTORIAL_BASE.with_(w_jump=wj, w_sim=ws)
        if cur == PCTL:
            cfg = cfg.with_(jump_currency=PCTL)
        arms.append(Arm(name, cfg, base, reading))
    return arms


STAGE1: list[Arm] = [
    Arm("P", P, None, "mirror-and-verify target; user-facing baseline"),
    *_factorial(),
    # A3's diagnostic: exposes how much of any A1 effect is the currency's SCALE
    # rather than its geometry. Explicitly excluded from R1's selection and never
    # adoptable.
    Arm("A1u",
        _FACTORIAL_BASE.with_(jump_currency=PCTL, jump_mean_match=False),
        "A1", "scale component of the currency swap (diagnostic)", adoptable=False),
    # The reachability bound. If X does not move the primary outcome, no arm in
    # this family can — which is what makes the R0 null interpretable.
    Arm("X",
        _FACTORIAL_BASE.with_(jump_currency=PCTL, w_jump=0.0, w_sim=1.5),
        "A7", "cheapest-possible-dive bound (not a candidate)", adoptable=False),
]

# R1 ranges over the eight factorial cells only (§9 A3).
R1_ELIGIBLE = tuple(name for name in _CELLS)

# §1.4's "multi-knob comparisons this design contains, labelled as such". Attribution
# comes only from the one-column chains; a win quoted from one of these cannot be
# assigned to any single knob, and any figure leaving this directory must say which
# comparison produced it.
PACKAGE_CONTRASTS = {
    ("A6", "A0"): "2 columns (J-mag + S-mag), raw",
    ("A7", "A0"): "3 columns (J-cur + J-mag + S-mag)",
    ("FL1", "P"): "floor currency AND everything W carries; isolating chain is P -> A0 -> ... -> W -> FL1",
}


def stage2(w_name: str, w_cfg: SweepConfig) -> list[Arm]:
    """The attachment arms, once R1 has chosen W. Each is W + exactly one knob."""
    return [
        # A1: additive toll on score-1.0 edges. Two magnitudes, so a null is
        # interpretable — a null at an inert magnitude is evidence about nothing.
        Arm("T1a", w_cfg.with_(toll_s=0.95), w_name, "does the p99 ceiling bind (7.5x w_hop)"),
        Arm("T1b", w_cfg.with_(toll_s=0.80), "T1a", "toll magnitude (30x w_hop)"),
        # A2: the depth-graduating device. The relax constant is pre-registered,
        # NOT ApiConfig's — reusing the shipped 0.15 is what left these arms inert.
        Arm("FL1", w_cfg.with_(floor_mode=PCTL, w_floor=1.0), w_name, "percentile floor as depth device"),
        Arm("FL2", w_cfg.with_(floor_mode=PCTL, w_floor=3.0), "FL1", "floor strength"),
    ]


def factor_table() -> str:
    """The factor table, printed from the code that will actually run."""
    rows = [f"{'arm':<5} {'J-cur':<5} {'J-mag':<6} {'S-mag':<6} {'floor':<6} "
            f"{'toll':<5} {'G':<3} {'baseline':<9} reading"]
    for a in STAGE1:
        c = a.cfg
        toll = "-" if c.toll_s is None else f"{c.toll_s}"
        floor = "off" if c.w_floor == 0.0 else f"{c.floor_mode}@{c.w_floor}"
        mm = "" if c.jump_mean_match else " (raw scale)"
        rows.append(f"{a.name:<5} {c.jump_currency + mm:<5} {c.w_jump:<6} {c.w_sim:<6} "
                    f"{floor:<6} {toll:<5} {'on' if c.guard_min_intermediary else 'off':<3} "
                    f"{a.baseline or '-':<9} {a.reading}")
    return "\n".join(rows)


if __name__ == "__main__":
    print(factor_table())
    print(f"\nstage 1: {len(STAGE1)} runs   snapshots: {SNAPSHOTS}   C1 depths: {C1_DEPTHS}")
    print(f"R1 eligible: {R1_ELIGIBLE}")
