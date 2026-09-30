"""How a journey is generated — ONE module, used by `DSL-G1`, the pre-screen AND generation.

`DRP-AM7-2` step 6 requires the pre-screen to generate *"exactly as `DRP-AM7-3` will"*, and `DSL-G1`
requires the listen's generator to be the code the lattice measured. Both are true by construction:
every journey in this harness comes from `side_ladder`, which calls the lattice's own
`drp_sweep.run_ladder` — imported, never copied — on the lattice's own maps (`drp_sweep.load_map`,
which verifies each artifact against its sidecar and pin, and refuses `DRP-S1` unless `DRP-G3`
passed on it).

- **incumbent** (today's app, `DRP-S0P0`): the `DRP-S0` map, `ceiling=False`.
- **challenger** (`DRP-S1P3`): the `DRP-S1` map, `ceiling=True`, schedule `drp_common.f_max`, with
  stage 3b's certified relaxation (`drp_sweep.ceiling_step`).

Both: the primary press rule (`m.key`'s minimum over the interior, every press `KNOWN`, exclusions
cumulative), under `ApiConfig` defaults — the pricing both cells use (`drp_sweep.cell_cfg`).
"""
from __future__ import annotations

import sys

from dsl_common import DEPTHS, DRP_3A, DRP_3B, ROLES

for _p in (str(DRP_3A), str(DRP_3B)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import drp_common as dc  # noqa: E402
import drp_sweep  # noqa: E402

SUPPLY = {"incumbent": "DRP-S0", "challenger": "DRP-S1"}
CELL = {"incumbent": "DRP-S0P0", "challenger": "DRP-S1P3"}
CEILING = {"incumbent": False, "challenger": True}

for _role in ROLES:
    _spec = drp_sweep.CELLS[CELL[_role]]
    if _spec["supply"] != SUPPLY[_role] or _spec["ceiling"] != CEILING[_role] or _spec["ramp"] is not None:
        raise SystemExit(f"HARNESS FAULT: {CELL[_role]} is not what DRP-AM7-1's factor table says")


def cfg():
    """Both cells route under `ApiConfig` defaults (`DRP-AM7-1`); asserted against the lattice."""
    a, b = drp_sweep.cell_cfg(CELL["incumbent"]), drp_sweep.cell_cfg(CELL["challenger"])
    if a != b or a != dc.ApiConfig():
        raise SystemExit("HARNESS FAULT: the two cells do not share ApiConfig defaults")
    return a


def load_maps() -> dict:
    """Both sides' maps, each verified against its sidecar and pin by the lattice's own loader."""
    return {role: drp_sweep.load_map(SUPPLY[role]) for role in ROLES}


def side_ladder(role: str, m, s: int, t: int, config, ceiling: bool | None = None,
                schedule=None) -> list[dict]:
    """The full primary ladder, presses 0..20, for one side. Overriding `ceiling` or `schedule` is
    for `DSL-G1`'s red control and the tests only; the listen always uses the role's own."""
    return drp_sweep.run_ladder(m, config, s, t, "primary", None,
                                CEILING[role] if ceiling is None else ceiling,
                                dc.f_max if schedule is None else schedule)


def at_depths(lad: list[dict], depths=DEPTHS) -> dict[int, dict]:
    """The presented depths the ladder reached with an interior-bearing journey. A depth absent
    here fails Gate L / substitution (d)."""
    out = {}
    for d in depths:
        if d < len(lad) and lad[d].get("path") is not None and len(lad[d]["path"]) > 2:
            out[d] = lad[d]
    return out


def adjacent(m, a: int, b: int) -> bool:
    return any(n == b for n, _ in m.store.neighbours_of(a))
