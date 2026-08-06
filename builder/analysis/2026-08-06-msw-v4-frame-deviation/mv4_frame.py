"""MSW-V4: the shipped-vs-CRE fame-percentile frame deviation, in router units.

FIGURES ONLY, NO VERDICTS. Answers the three parts of `MSW-V4`
(`docs/superpowers/plans/2026-08-05-msw-package-adoption.md` Task 10 Step 4):

  1. distribution of |pctl_shipped - pctl_CRE_frame| over the new artifact's nodes
  2. the per-hop ramp cost difference that implies at r = 0.01, k in {1, 10, 20}
  3. those differences against the other cost terms' magnitudes on real edges

THE TWO CURRENCIES BEING COMPARED, read off the source, not off the brief:

  pctl_shipped   `api/src/artistpath_api/graph_store.py::fame_percentiles`
                 frame = THIS artifact's non-null fame_lb_raw values
                 formula = |{f < v}| / (N_nonnull - 1)      [lower-tail anchored]
                 nulls priced 0.0 and EXCLUDED from the frame

  pctl_CRE_frame `builder/analysis/2026-08-02-fame-instrument/fi_stats.py::Frame`
                 as used by `cre_common.Ruler` (the listened arm's ruler)
                 frame = the ADOPTED artifact's non-null values (N = 74,151)
                 formula = (|{f < v}| + (|{f = v}| + 1)/2) / N_nonnull  [mid-rank]
                 v above the frame max takes pctl(max)              [FAM-AM1.6]

  So the deviation is TWO knobs, not one: the frame POPULATION and the
  percentile ESTIMATOR differ. This script reports the headline difference and
  decomposes it one knob at a time, via the intermediate

  pctl_mid_newframe   CRE's mid-rank formula applied to the NEW artifact's frame.

    |shipped - mid_newframe|  = estimator effect  (population held constant)
    |mid_newframe - CRE|      = population effect (estimator held constant)

RAW VALUES ARE HELD CONSTANT throughout: every column maps the NEW artifact's
own fame_lb_raw value. The union snapshot's raw values are used only to measure
value drift, reported separately as a deviation that is NOT MSW-V4's subject.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-06-msw-v4-frame-deviation/mv4_frame.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# The CRE harness's own module supplies the ruler; imported, never re-derived.
sys.path.insert(0, str(ROOT / "builder/analysis/2026-08-03-cap-reevaluation"))
sys.path.insert(0, str(ROOT / "api/src"))

import cre_common  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402

NEW = ROOT / "builder/scratch/graph-msw-tu50.bin"
NEW_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"

R = cre_common.RAMPS["P1a"]  # 0.01, the adopted ramp
KS = (1, 10, 20)

OUT = HERE / "mv4_frame.json"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def q(x: np.ndarray) -> dict:
    """The shape of a distribution, not just its mean."""
    if len(x) == 0:
        return {"n": 0}
    return {
        "n": int(len(x)),
        "mean": float(np.mean(x)),
        "p50": float(np.percentile(x, 50)),
        "p75": float(np.percentile(x, 75)),
        "p90": float(np.percentile(x, 90)),
        "p95": float(np.percentile(x, 95)),
        "p99": float(np.percentile(x, 99)),
        "max": float(np.max(x)),
    }


def mass_near_zero(x: np.ndarray) -> dict:
    return {
        f"frac_le_{t}": float(np.mean(x <= t))
        for t in (0.001, 0.005, 0.01, 0.02, 0.05, 0.10)
    }


def main() -> None:
    got = sha256_file(NEW)
    if got != NEW_SHA:
        raise SystemExit(f"WRONG ARTIFACT: expected {NEW_SHA}, got {got}")

    store = GraphStore.from_bytes(NEW.read_bytes())
    n_nodes = len(store.mbids)

    # Raw fame values, straight out of the artifact metadata blob. GraphStore
    # keeps only the percentile, so re-read the blob for the raw column.
    payload = NEW.read_bytes()
    meta_len = int(np.frombuffer(payload[16:24], dtype="<i8")[0])
    meta = json.loads(payload[-meta_len:].decode("utf-8"))
    fame_raw = meta["fame_lb"]
    if len(fame_raw) != n_nodes:
        raise SystemExit("fame_lb length != node count")

    is_null = np.array([v is None for v in fame_raw])
    vals = np.array([0 if v is None else int(v) for v in fame_raw], dtype=np.int64)
    nonnull = ~is_null

    # --- column A: the shipped percentile, from the shipped function itself ---
    shipped = GraphStore.fame_percentiles(fame_raw)
    if store.fame_lb_pctl is None or not np.allclose(shipped, store.fame_lb_pctl):
        raise SystemExit("recomputed shipped pctl != the one GraphStore serves")

    # --- column C: the CRE ruler's frame, same raw values mapped through it ---
    ruler = cre_common.Ruler()
    cre = np.asarray(ruler._frame.pctl(vals), dtype=np.float64)

    # --- column B: CRE's estimator on the NEW artifact's frame (one knob) ---
    from fi_stats import Frame  # noqa: E402  (frozen FAM-AM1.6 implementation)

    new_frame = Frame(vals[nonnull])
    mid_newframe = np.asarray(new_frame.pctl(vals), dtype=np.float64)

    # ---------------- part 1: the distributions ----------------
    # Main population: the 58,746 non-null nodes, where the raw value is a real
    # measurement and only the frame/estimator differs.
    d_head = np.abs(shipped - cre)[nonnull]
    d_est = np.abs(shipped - mid_newframe)[nonnull]
    d_pop = np.abs(mid_newframe - cre)[nonnull]
    signed = (shipped - cre)[nonnull]

    # Node classes: present in / absent from the retired adopted artifact. The
    # CRE Frame maps out-of-frame values fine, so absence does not make the
    # comparison undefined -- but the two populations differ and the split is
    # reported because the brief asks for it explicitly.
    adopted_store = cre_common.load_adopted()
    adopted_mbids = set(adopted_store.mbids)
    in_adopted = np.array([m in adopted_mbids for m in store.mbids])

    # Nulls: shipped prices them 0.0; the CRE ruler's DEVICE prices a
    # snapshot-present null at frame.pctl(0) and a snapshot-absent node at 0.5
    # (cre_common pin 2). Reported separately -- null pricing is a different
    # deviation from the frame deviation MSW-V4 asks about.
    null_rows = []
    for i in np.flatnonzero(is_null):
        m = store.mbids[i]
        null_rows.append(
            {
                "status_in_cre_snapshot": ruler.status_of(m),
                "shipped": float(shipped[i]),
                "cre_device": float(ruler.device_pctl_of(m)),
            }
        )
    null_by_status: dict[str, dict] = {}
    for st in ("measured", "null", "absent"):
        sel = [r for r in null_rows if r["status_in_cre_snapshot"] == st]
        if sel:
            diffs = np.array([abs(r["shipped"] - r["cre_device"]) for r in sel])
            null_by_status[st] = {
                "n": len(sel),
                "abs_diff": q(diffs),
                "cre_device_pctl_example": sel[0]["cre_device"],
            }

    # Raw-value drift against the snapshot -- NOT MSW-V4's subject, measured so
    # the frame comparison cannot be blamed for it.
    snap = json.loads(cre_common.SNAPSHOT.read_text(encoding="utf-8"))
    same = diff = missing = 0
    for i, m in enumerate(store.mbids):
        if is_null[i]:
            continue
        sv = snap.get(m, "__absent__")
        if sv == "__absent__":
            missing += 1
        elif sv is None or int(sv) != int(vals[i]):
            diff += 1
        else:
            same += 1

    # ---------------- part 2: ramp cost difference ----------------
    ramp_diff = {
        f"k={k}": q(R * k * d_head) | mass_near_zero(R * k * d_head)
        for k in KS
    }
    # The ramp TERM's own magnitude, for scale.
    ramp_term = {
        f"k={k}": q(R * k * shipped[nonnull]) for k in KS
    }

    # ---------------- part 3: the other cost terms on real edges ----------
    cfg = ApiConfig()
    scores = store.scores.astype(np.float64)
    src = np.repeat(np.arange(n_nodes), np.diff(store.offsets))
    dst = store.neighbours
    pop = store.pop_raw.astype(np.float64)

    t_sim = cfg.w_sim * (1.0 - scores)
    t_jump = cfg.w_jump * np.abs(pop[src] - pop[dst])
    t_hub = cfg.w_degree_hub * store.degree_hub_penalty[dst]
    static = t_sim + t_jump + t_hub + cfg.w_hop

    # The floor term is request-dependent: floor_raw = min(pop of the two chosen
    # artists), relaxed by cfg.floor_relax_known per `known` press. Evaluated at
    # three representative floors over the real pop_raw of every edge head.
    floors = {
        "floor_raw=p50_of_pop_raw": float(np.percentile(pop, 50)),
        "floor_raw=p90_of_pop_raw": float(np.percentile(pop, 90)),
        "floor_raw=max_pop_raw": float(np.max(pop)),
    }
    floor_terms = {
        name: q(cfg.w_floor * np.maximum(0.0, f - pop[dst]))
        for name, f in floors.items()
    }

    result = {
        "artifacts": {
            "new_candidate": {"file": NEW.name, "sha256": got, "nodes": n_nodes,
                              "directed_arcs": int(len(dst))},
            "cre_frame_source": {"file": cre_common.ADOPTED.name,
                                 "sha256": cre_common.ADOPTED_SHA,
                                 "frame_n": ruler.frame_n},
        },
        "populations": {
            "new_nodes": n_nodes,
            "new_nonnull_fame": int(nonnull.sum()),
            "new_null_fame": int(is_null.sum()),
            "new_nodes_present_in_adopted": int(in_adopted.sum()),
            "new_nodes_absent_from_adopted": int((~in_adopted).sum()),
        },
        "raw_value_drift_vs_snapshot_NOT_MSW_V4": {
            "identical": same, "differing": diff, "absent_from_snapshot": missing,
        },
        "part1_abs_diff_shipped_vs_cre_frame": {
            "all_nonnull": q(d_head) | mass_near_zero(d_head),
            "present_in_adopted": q(np.abs(shipped - cre)[nonnull & in_adopted]),
            "absent_from_adopted": q(np.abs(shipped - cre)[nonnull & ~in_adopted]),
            "signed_shipped_minus_cre": {
                "mean": float(np.mean(signed)),
                "p50": float(np.percentile(signed, 50)),
                "p05": float(np.percentile(signed, 5)),
                "p95": float(np.percentile(signed, 95)),
                "frac_shipped_higher": float(np.mean(signed > 0)),
            },
        },
        "part1_decomposition": {
            "estimator_effect_shipped_vs_midrank_same_frame": q(d_est),
            "population_effect_midrank_new_vs_adopted_frame": q(d_pop),
        },
        "part1_nulls_separate": {
            "n": int(is_null.sum()),
            "by_cre_snapshot_status": null_by_status,
        },
        "part2_ramp_cost_difference_r0.01": ramp_diff,
        "part2_ramp_term_own_magnitude_r0.01": ramp_term,
        "part3_other_terms_per_edge": {
            "weights": {
                "w_sim": cfg.w_sim, "w_jump": cfg.w_jump, "w_floor": cfg.w_floor,
                "w_avoid": cfg.w_avoid, "w_degree_hub": cfg.w_degree_hub,
                "w_hop": cfg.w_hop,
                "w_known_ramp_fame_pctl_default": cfg.w_known_ramp_fame_pctl,
                "floor_relax_known": cfg.floor_relax_known,
                "avoid_penalty": cfg.avoid_penalty, "avoid_decay": cfg.avoid_decay,
            },
            "sim_term": q(t_sim),
            "jump_term": q(t_jump),
            "hop_term_constant": cfg.w_hop,
            "degree_hub_term": q(t_hub),
            "static_sum_sim_jump_hub_hop": q(static),
            "floor_term_at_representative_floors": floor_terms,
            "avoid_term_values": {
                "hop1": cfg.w_avoid * cfg.avoid_penalty,
                "hop2": cfg.w_avoid * cfg.avoid_penalty * cfg.avoid_decay,
                "beyond_radius": 0.0,
            },
        },
    }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
