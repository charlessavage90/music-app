"""`JFX-AM1.3`'s PRECONDITION: re-verify `CRE-G1(a)` against TODAY's router.

**Why this is not a formality.** `AM1.3` requires that if the `CRE-` mirror supplies
any routing code to the `JFX-` harness, `CRE-G1(a)`'s byte-identity is re-verified
against today's `api/src/artistpath_api/pathfinding.py` first. Checked, and the
concern is real:

    cre_mirror.py     f52cc04  2026-08-03  "mirror copy with the fame-currency ramp"
    pathfinding.py    a4ff9c6  2026-08-05  "MSW-: fame-currency known ramp ..."

The mirror implemented the ramp for the `CRE-` sweep TWO DAYS BEFORE production
landed its own. Neither was written from the other.

**And the original gate could not have caught a ramp divergence.** `cre_gates.g1a`
compares at `excludes=[]` only — k = 0 — where both sides skip the ramp term
entirely (it is "added only when live, never as `+ 0.0`"). So the one term that
differs in provenance is the one term `CRE-G1(a)` never exercised. `JFX-` routes at
k = 0, 5, 10, 20 with the ramp live at `ApiConfig.w_known_ramp_fame_pctl`.

**So this is a STRICTLY STRONGER re-run of the same gate:** the same bar
(`cre_gates.journeys_identical` — node sequence AND stop kind, imported rather than
restated), over a full ladder to depth 20 rather than one rung.

**The ruler frame.** `AM1.3` requires the PRODUCTION frame — `store.fame_lb_pctl`,
ranked against the served artifact's own population — not `cre_common.Ruler`, whose
`FRAME_N = 74_151` is pinned to an external snapshot and would make §0.1(a)'s
confound false and uncheckable. That decision was taken for a design reason; it is
also what makes the two cost expressions arithmetically comparable at all, since
production reads `store.fame_lb_pctl[v]` directly.

**Two red halves, because an identity gate is the shape that passes vacuously**
(`cre_gates`' own reasoning, and `CRE-T3`'s first draft of `CRE-G2(b)` was exactly
that defect). One reproduces `CRE-`'s own red control by moving `w_hop`. The second
is new and is the one that matters here: it perturbs the RAMP, which can only
diverge at k > 0, so it proves the ladder rungs above zero are genuinely compared.

Reports only. Adopts nothing, routes no pre-registered outcome, computes no `JFX-`
statistic. **The pair sample is an instrument check, not an arm** — no outcome value
is produced from it, so it does not touch §2's fixed selection.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CRE = ROOT / "builder/analysis/2026-08-03-cap-reevaluation"
sys.path.insert(0, str(CRE))
sys.path.insert(0, str(ROOT / "api/src"))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import KNOWN, Exclusion, find_journey  # noqa: E402
from cre_gates import journeys_identical  # noqa: E402  -- the bar, not a copy
from cre_ladder import journey, victim_key  # noqa: E402
from cre_mirror import MirrorContext, SweepConfig  # noqa: E402

from jfx_s1_reachability import (  # noqa: E402
    EXPECTED_SHA,
    GRAPH,
    _raw_fame_from_metadata,
)

MAX_K = 20              # JFX's deepest depth (§2)
PAIRS_PER_STRATUM = 10  # instrument check; methodology, not a pre-registered n
SAMPLE_SEED = 20260809  # the prereg's own seed, so the sample is reproducible
RED_W_HOP = 0.05        # CRE-'s own red control value
RED_RAMP = 0.05         # off ApiConfig's 0.01; can only bite at k > 0

CANDIDATES = (
    ROOT / "builder/analysis/2026-08-09-jfx-preregistration/jfx_candidate_pairs.json"
)


def assert_weight_parity(cfg: SweepConfig, api: ApiConfig) -> list[str]:
    """Every `ApiConfig` cost weight has an equal counterpart on the mirror.

    This is the half the empirical test CANNOT do, and the reason it is here is
    `CLAUDE.md`'s defect-of-absence rule: a NEW production cost term whose default
    weight is 0.0 would leave every path identical today while the mirror silently
    lacked the term — a green that means nothing the moment the weight is tuned.
    A missing field fails here even when it is inert.
    """
    checked = []
    for name in sorted(f for f in api.__slots__ if f.startswith("w_")):
        if not hasattr(cfg, name):
            raise SystemExit(
                f"PARITY FAILED: ApiConfig.{name} has NO counterpart on "
                f"SweepConfig. A production cost term the mirror does not "
                f"implement. This fails even if its weight is 0.0 today."
            )
        a, m = getattr(api, name), getattr(cfg, name)
        if a != m:
            raise SystemExit(
                f"PARITY FAILED: {name} is {a} in ApiConfig and {m} on the mirror"
            )
        checked.append(f"{name}={a}")
    for name in ("floor_relax_known", "floor_relax_dislike", "avoid_penalty",
                 "avoid_decay", "avoid_radius"):
        a, m = getattr(api, name), getattr(cfg, name)
        if a != m:
            raise SystemExit(
                f"PARITY FAILED: {name} is {a} in ApiConfig and {m} on the mirror"
            )
        checked.append(f"{name}={a}")
    return checked


def sample_pairs(store: GraphStore) -> list[tuple[str, str, str]]:
    """A reproducible subset of the committed candidates, present in the artifact."""
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    rng = random.Random(SAMPLE_SEED)
    out = []
    for stratum in sorted(doc["strata"]):
        usable = [
            (a, b) for a, b in doc["strata"][stratum]
            if a in store.id_by_mbid and b in store.id_by_mbid
        ]
        for a, b in rng.sample(usable, min(PAIRS_PER_STRATUM, len(usable))):
            out.append((stratum, a, b))
    return out


def ladder_identical(store, ctx, cfg, api_cfg, key, s, t, max_k) -> tuple[int, list]:
    """One all-`known` ladder; compare BOTH routers at every rung.

    The mirror drives victim selection and both routers are handed the SAME
    exclusion list at each rung, so the comparison is of the routers and never
    of two divergent ladders.
    """
    excludes: list = []
    compared, diverged = 0, []
    for k in range(max_k + 1):
        mirror = journey(store, s, t, excludes, cfg, ctx)
        prod = find_journey(store, s, t, excludes, api_cfg)
        compared += 1
        if not journeys_identical(mirror, prod):
            m_path, m_kind = mirror
            p_path, p_kind = (None, "none") if prod is None else prod
            diverged.append({
                "k": k, "mirror_kind": m_kind, "production_kind": p_kind,
                "mirror_path": m_path, "production_path": p_path,
            })
            break  # the ladder is no longer comparable past a divergence
        path, _ = mirror
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break
        excludes = excludes + [Exclusion(node=min(interior, key=key), reason=KNOWN)]
    return compared, diverged


def run(store, ctx, cfg, api_cfg, key, pairs, max_k) -> dict:
    compared, diverged, ladders = 0, [], 0
    for stratum, a, b in pairs:
        s, t = store.id_by_mbid[a], store.id_by_mbid[b]
        c, d = ladder_identical(store, ctx, cfg, api_cfg, key, s, t, max_k)
        compared += c
        ladders += 1
        for row in d:
            diverged.append({"stratum": stratum, "pair": f"{a}|{b}", **row})
    return {
        "ladders": ladders,
        "rungs_compared": compared,
        "diverged": len(diverged),
        "detail": diverged[:5],
    }


def main() -> int:
    payload = GRAPH.read_bytes()
    import hashlib

    sha = hashlib.sha256(payload).hexdigest()
    print(f"artifact: {GRAPH.name}\nsha256:   {sha}")
    if sha != EXPECTED_SHA:
        raise SystemExit("REFUSING: artifact identity does not match.")
    print("identity: OK\n")

    store = GraphStore.from_bytes(payload)
    if store.fame_lb_pctl is None:
        raise SystemExit("artifact carries no fame; the ramp cannot be exercised")

    api_cfg = ApiConfig()
    cfg = SweepConfig.production().with_(
        w_known_ramp_fame_pctl=api_cfg.w_known_ramp_fame_pctl
    )
    print("weight parity, ApiConfig vs mirror:")
    for line in assert_weight_parity(cfg, api_cfg):
        print(f"   {line}")
    if api_cfg.w_known_ramp_fame_pctl == 0.0:
        raise SystemExit(
            "the ramp is OFF in ApiConfig, so this run cannot exercise the term "
            "AM1.3 flagged. That is the whole point of this check."
        )
    print()

    # AM1.3: the PRODUCTION ruler frame, not cre_common.Ruler's pinned FRAME_N.
    fame_pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
    ctx = MirrorContext.build(store, fame_device=fame_pctl)

    # victim_key wants fame with NaN at unmeasured artists, so ruler-null
    # interiors sort after every measured one. `fame_lb_pctl` assigns null
    # artists 0.0 (a VALUE), so the raw blob is the only source for the mask.
    raw = _raw_fame_from_metadata(payload)
    measured = np.array(
        [np.nan if v is None else 1.0 for v in raw], dtype=np.float64
    ) * fame_pctl
    key = victim_key(measured, store.pop_raw, store.mbids)

    pairs = sample_pairs(store)
    print(f"pairs: {len(pairs)} ({PAIRS_PER_STRATUM}/stratum, seed {SAMPLE_SEED}), "
          f"ladders to k = {MAX_K}\n")

    green = run(store, ctx, cfg, api_cfg, key, pairs, MAX_K)
    print(f"GREEN  rungs compared {green['rungs_compared']} over "
          f"{green['ladders']} ladders; diverged {green['diverged']}")
    if green["diverged"]:
        print(json.dumps(green["detail"], indent=1)[:2000])

    # --- red halves: a green above is worthless without these ---------------
    red_hop = run(store, ctx, cfg.with_(w_hop=RED_W_HOP), api_cfg, key,
                  pairs[:6], MAX_K)
    print(f"RED-1  w_hop {RED_W_HOP} (CRE-'s own control): "
          f"diverged {red_hop['diverged']} of {red_hop['rungs_compared']} rungs")

    # Only bites at k > 0, so it proves the ladder above rung zero is live.
    red_ramp = run(store, ctx, cfg.with_(w_known_ramp_fame_pctl=RED_RAMP), api_cfg,
                   key, pairs[:6], MAX_K)
    first_k = min((d["k"] for d in red_ramp["detail"]), default=None)
    print(f"RED-2  ramp {RED_RAMP} (k>0 only): "
          f"diverged {red_ramp['diverged']} of {red_ramp['rungs_compared']} rungs"
          f"; first divergence at k = {first_k}")

    ok = (
        green["diverged"] == 0
        and red_hop["diverged"] > 0
        and red_ramp["diverged"] > 0
        and first_k is not None
        and first_k > 0
    )
    print()
    if not ok:
        print("CRE-G1(a) RE-VERIFICATION: **FAILED**")
        if green["diverged"]:
            print("  the mirror does not reproduce today's router")
        if red_hop["diverged"] == 0 or red_ramp["diverged"] == 0:
            print("  a red control did not fire — the comparison may be vacuous")
        if first_k == 0:
            print("  RED-2 fired at k = 0, where the ramp is not applied at all;"
                  " that is not the ramp being exercised")
        return 1
    print("CRE-G1(a) RE-VERIFICATION: **PASSED**")
    print(f"  identical at every rung to k = {MAX_K}, ramp live at "
          f"{api_cfg.w_known_ramp_fame_pctl}; both red controls fired, RED-2 first"
          f" at k = {first_k}.")
    print("  AM1.3's precondition is discharged: the mirror may supply routing"
          " code to the JFX- harness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
