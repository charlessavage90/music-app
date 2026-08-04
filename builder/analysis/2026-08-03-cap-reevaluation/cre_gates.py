"""`CRE-T8` -- Stage 2 entry gates: `CRE-G1`(a), `CRE-G1`(c), `CRE-G2`(a).

**Governing document (experimental):** the prereg's §4 Stage 2 block, which wins
wherever this file or the execution plan disagrees with it.

Three gates, run before any depth sweep opens:

- **`CRE-G1`(a)** -- mirror equivalence. On the **E-S0 cleaned substrate** (same
  graph both sides), `cre_ladder.journey` under `SweepConfig.production()` returns
  the same node sequence AND the same stop kind as the production router code,
  `find_journey(store, s, t, [], ApiConfig())`, on every surviving pair. **Exact
  identity is the bar and any divergence is instrument failure** -- the response is
  to fix the harness, never to widen the bar (prereg §4: "the response to divergence
  is fixed and cheap"). B-S0 is run identically and **reported as QA, not gated**:
  the prereg gates E only.
- **`CRE-G1`(c)** -- the ruler-frame assertion (frame N = 74,151). Constructing
  `Ruler` performs it; this file records the value it asserted.
- **`CRE-G2`(a)** -- device liveness at an instrument-only extreme. Per cell
  carrying a `P1` arm, at r = 1.0 (never a candidate), **>= half** of the famous-pair
  journeys must change at d1 against the same cell's `P0` d1. Below half is a dead
  wire and no `P1` null in that cell is readable.

**`CRE-G1`(a) carries a red half, and the reason is this plan's own history.** An
identity gate is the shape that passes vacuously -- a comparison wired to itself,
or one whose loop body never runs, reports a clean 22/22 either way. `CRE-T3`'s
first draft of `CRE-G2`(b) was exactly that defect (it compared the toll formula
against itself and could not fail), and the closeout tamper check found a copied
predicate in `cre_screen`. So the green run is followed by a deliberately perturbed
mirror (`w_hop` moved off production's value), which **must** diverge. A green
without that red is not evidence the comparison works.

`CRE-G2`(a) needs no red half and gets none: its failure direction is "nothing
changed", so a dead comparison reports zero changes and **fails**. It cannot pass
vacuously, which is the asymmetry that decides where the control is worth its cost.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

from cre_common import EXTREME_RAMP, Ruler, famous_pairs, in_dir, use_frozen
from cre_ladder import journey, victim_key
from cre_mirror import MirrorContext, SweepConfig

use_frozen("api_src")
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import KNOWN, Exclusion, find_journey  # noqa: E402

G1A_CELL = "E-S0"          # the prereg's named identity cell (§0.2, E-S0-P0)
G1A_QA_CELL = "B-S0"       # reported, never gated
# The §0.2 cells carrying a `P1` arm. The S2 `P1` cells are absent because
# CRE-D1 fired not_supported -- they do not exist (handoff claim 1).
G2A_CELLS = ("E-S1", "B-S0", "B-S1")
G2A_BAR = 0.5
RED_W_HOP = 0.05           # off production's 0.02; the red half's only change


def load_cell(name: str) -> tuple[dict, GraphStore]:
    """Load a built cell, sha-asserted against its own manifest row."""
    cells = json.loads(in_dir("cre_builds.json").read_text(encoding="utf-8"))["cells"]
    rows = [c for c in cells if c["cell"] == name]
    if len(rows) != 1:
        raise SystemExit(f"expected exactly one manifest row for {name}, got {len(rows)}")
    c = rows[0]
    payload = Path(c["path"]).read_bytes()
    got = hashlib.sha256(payload).hexdigest()
    if got != c["sha256"]:
        raise SystemExit(f"WRONG ARTIFACT for {name}: expected {c['sha256']}, got {got}")
    return c, GraphStore.from_bytes(payload)


def surviving_pairs() -> list[tuple[str, str, str]]:
    """The `CRE-G3` surviving set, read from the committed screen rather than
    re-derived -- one pair set across every cell (prereg §0.2 held-constant row)."""
    lost = json.loads(in_dir("cre_screen.json").read_text(encoding="utf-8"))
    lost_keys = set(lost["CRE_G3"]["pairs_lost"])
    return [(cls, a, b) for cls, a, b in famous_pairs() if f"{a}|{b}" not in lost_keys]


def g1a(store, ctx, pairs, cfg, api_cfg) -> dict:
    """One node-sequence-and-stop-kind identity pass. Returns the full per-pair
    record; the caller decides whether it is a bar or QA."""
    rows, diverged = {}, []
    for cls, a, b in pairs:
        s, t = store.id_by_mbid[a], store.id_by_mbid[b]
        m_path, m_kind = journey(store, s, t, [], cfg, ctx)
        prod = find_journey(store, s, t, [], api_cfg)
        # Production returns None where the mirror returns (None, "none"); the
        # two spellings of "no path" are the same outcome.
        p_path, p_kind = (None, "none") if prod is None else prod
        same = m_path == p_path and m_kind == p_kind
        key = f"{a}|{b}"
        rows[key] = {
            "class": cls,
            "identical": same,
            "mirror_kind": m_kind,
            "production_kind": p_kind,
            "interior_len": (len(m_path) - 2) if m_path else None,
        }
        if not same:
            diverged.append(key)
            rows[key]["mirror_path"] = m_path
            rows[key]["production_path"] = p_path
    return {
        "pairs_compared": len(rows),
        "identical": len(rows) - len(diverged),
        "diverged": diverged,
        "result": "PASS" if not diverged and rows else "FAIL",
        "per_pair": rows,
    }


def g2a(store, ctx, measured, pairs, cfg) -> dict:
    """Device liveness at r = 1.0, d0 -> d1 only.

    d0 is computed once under `P0`: the ramp is not merely zero at k = 0 but not
    added at all (`cre_mirror._dijkstra`), so the two arms share d0 by
    construction and therefore share the victim. That is `CRE-G1`(b)'s claim,
    asserted per sweep run in T9; here it is what makes one d0 legitimate.
    """
    key = victim_key(measured, store.pop_raw, store.mbids)
    hot = cfg.with_(w_known_ramp_fame_pctl=EXTREME_RAMP)
    rows, changed, unreadable = {}, 0, {}
    for cls, a, b in pairs:
        s, t = store.id_by_mbid[a], store.id_by_mbid[b]
        pk = f"{a}|{b}"
        path0, kind0 = journey(store, s, t, [], cfg, ctx)
        if path0 is None:
            unreadable[pk] = "no d0 journey"
            continue
        interior = path0[1:-1]
        if not interior:
            # adjacent_only: there is no victim to press, so there is no d1 and
            # the pair is excluded rather than counted as "did not change".
            unreadable[pk] = f"no d0 interior ({kind0})"
            continue
        victim = min(interior, key=key)
        ex = [Exclusion(node=victim, reason=KNOWN)]
        p0_path, p0_kind = journey(store, s, t, ex, cfg, ctx)
        p1_path, p1_kind = journey(store, s, t, ex, hot, ctx)
        differs = p0_path != p1_path
        rows[pk] = {
            "class": cls,
            "changed": differs,
            "d0_kind": kind0,
            "d1_p0_kind": p0_kind,
            "d1_extreme_kind": p1_kind,
            "d1_p0_len": len(p0_path) if p0_path else None,
            "d1_extreme_len": len(p1_path) if p1_path else None,
        }
        changed += bool(differs)
    denom = len(rows)
    frac = (changed / denom) if denom else 0.0
    return {
        "extreme_ramp": EXTREME_RAMP,
        "bar": G2A_BAR,
        "readable_pairs": denom,
        "changed_at_d1": changed,
        "fraction_changed": frac,
        # No readable pair is a dead wire by default, not a pass.
        "result": "PASS" if denom and frac >= G2A_BAR else "FAIL",
        "unreadable_pairs": unreadable,
        "per_pair": rows,
    }


def main() -> int:
    t0 = time.time()
    ruler = Ruler()                      # CRE-G1(c) asserts inside the constructor
    pairs = surviving_pairs()
    cfg = SweepConfig.production()
    api_cfg = ApiConfig()
    print(f"CRE-G1(c): ruler frame N = {ruler.frame_n} (asserted)", flush=True)
    print(f"pair set: {len(pairs)} surviving famous pairs\n", flush=True)

    doc: dict = {
        "stage": "2 (entry gates)",
        "CRE_G1c": {"ruler_frame_n": ruler.frame_n, "result": "PASS"},
    }

    # --- CRE-G1(a): the gate, then its red half -----------------------------
    c, store = load_cell(G1A_CELL)
    _measured, device = ruler.arrays(store)
    ctx = MirrorContext.build(store, device)
    green = g1a(store, ctx, pairs, cfg, api_cfg)
    green["cell"] = G1A_CELL
    green["sha256"] = c["sha256"]
    print(f"CRE-G1(a) {G1A_CELL}: {green['identical']}/{green['pairs_compared']} "
          f"identical, kinds match -- {green['result']}", flush=True)

    red = g1a(store, ctx, pairs, cfg.with_(w_hop=RED_W_HOP), api_cfg)
    red_ok = red["diverged"] != []
    print(f"  red half (mirror w_hop={RED_W_HOP} vs production 0.02): "
          f"{len(red['diverged'])} pairs diverge -- "
          f"{'PASS' if red_ok else 'FAIL (comparison cannot go red)'}", flush=True)
    doc["CRE_G1a"] = green
    doc["CRE_G1a_red_control"] = {
        "what": "the same comparison with the mirror's w_hop moved off production's",
        "w_hop": RED_W_HOP,
        "pairs_diverging": len(red["diverged"]),
        "result": "PASS" if red_ok else "FAIL",
    }

    # --- CRE-G1(a) on B-S0: reported QA, never a bar ------------------------
    cq, store_q = load_cell(G1A_QA_CELL)
    _mq, device_q = ruler.arrays(store_q)
    qa = g1a(store_q, MirrorContext.build(store_q, device_q), pairs, cfg, api_cfg)
    qa["cell"] = G1A_QA_CELL
    qa["sha256"] = cq["sha256"]
    qa["gated"] = False
    qa["note"] = "The prereg gates E only; this run is reported QA, not a bar."
    print(f"CRE-G1(a) {G1A_QA_CELL} (QA, not gated): "
          f"{qa['identical']}/{qa['pairs_compared']} identical -- {qa['result']}",
          flush=True)
    doc["CRE_G1a_qa"] = qa

    # --- CRE-G2(a): device liveness per P1-carrying cell --------------------
    print("", flush=True)
    per_cell = {}
    already = {G1A_CELL: (c, store), G1A_QA_CELL: (cq, store_q)}
    for name in G2A_CELLS:
        cc, s2 = already[name] if name in already else load_cell(name)
        measured, device_c = ruler.arrays(s2)
        row = g2a(s2, MirrorContext.build(s2, device_c), measured, pairs, cfg)
        row["cell"] = name
        row["sha256"] = cc["sha256"]
        per_cell[name] = row
        print(f"CRE-G2(a) {name:6s}: {row['changed_at_d1']}/{row['readable_pairs']} "
              f"journeys change at d1 (r = {EXTREME_RAMP}) = "
              f"{row['fraction_changed']:.3f} vs bar {G2A_BAR} -- {row['result']}",
              flush=True)
    doc["CRE_G2a"] = per_cell

    doc["seconds"] = round(time.time() - t0, 1)
    in_dir("cre_gates.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"\nwrote cre_gates.json ({doc['seconds']}s)", flush=True)

    # The bars. G1(a) failing means no read opens; a dead red half means the
    # green was never evidence. G2(a) failing bars that cell's P1 nulls only,
    # which is a read-licensing fact for T9 rather than a stop -- reported here
    # and carried in the JSON, never silently.
    failed = []
    if green["result"] != "PASS":
        failed.append("CRE-G1(a)")
    if not red_ok:
        failed.append("CRE-G1(a) red control")
    if failed:
        print(f"\nINSTRUMENT FAILURE: {', '.join(failed)}. Fix the harness; "
              f"no read opens. Do not widen the bar.", flush=True)
        return 1
    dead = [n for n, r in per_cell.items() if r["result"] != "PASS"]
    if dead:
        print(f"\nCRE-G2(a) dead wire in: {', '.join(dead)}. No P1 null is "
              f"readable in those cells; recorded in cre_gates.json.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
