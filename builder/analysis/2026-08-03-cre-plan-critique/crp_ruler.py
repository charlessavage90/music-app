"""CRP-1: the ruler, the device null price, and snapshot coverage per cell.

Review instrument for the CRE execution-plan critique (2026-08-03). READ ONLY:
opens committed JSONs and gitignored .bin artifacts, writes nothing but its own
JSON in this directory. No Track B cell is re-run or rebuilt.

Answers, quantitatively:
  Q1  plan pin 2 -- device pricing of ruler-null nodes at frame.pctl(0).
      How far below the measured obscure tail does that sit, in TOLL units?
  Q1b snapshot coverage: which cells contain nodes the union snapshot has no
      key for at all (absent != null, but the plan's Ruler conflates them).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-cre-plan-critique/crp_ruler.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FAME = ROOT / "builder/analysis/2026-08-02-fame-instrument"
sys.path.insert(0, str(FAME))
sys.path.insert(0, str(ROOT / "api/src"))

from fi_stats import Frame  # noqa: E402

SCRATCH = ROOT / "builder/scratch"
ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
SNAPSHOT = FAME / "fi_union_snapshot.json"
CELLS = SCRATCH / "cb-cells"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def mbids_of(path: Path) -> list[str]:
    from artistpath_api.graph_store import GraphStore

    return list(GraphStore.load(path).mbids)


def main() -> None:
    got = sha(ADOPTED)
    assert got == ADOPTED_SHA, f"WRONG ARTIFACT {got}"
    print(f"adopted sha ok {got[:12]}...")

    raw = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    print(f"snapshot keys: {len(raw):,}")

    adopted_mbids = mbids_of(ADOPTED)
    vals = np.array(
        [raw[m] for m in sorted(adopted_mbids) if raw.get(m) is not None],
        dtype=np.int64,
    )
    frame = Frame(vals)
    print(f"frame N = {frame.n:,}   (CRE-G1c expects 74,151)")

    null_price = float(frame.pctl(np.array([0]))[0])
    min_val = int(frame.uniq[0])
    min_pctl = float(frame.pctl(np.array([min_val]))[0])

    # Percentile of the obscure measured tail, over the whole snapshot's
    # non-null values mapped through the frame (this is what a CRE cell scores).
    all_vals = np.array([v for v in raw.values() if v is not None], dtype=np.int64)
    all_p = frame.pctl(all_vals)
    qs = {f"p{q}": float(np.percentile(all_p, q)) for q in (0.1, 0.5, 1, 2, 5, 10, 25, 50)}

    out: dict = {
        "frame_n": frame.n,
        "device_null_pctl_frame_pctl_0": null_price,
        "frame_min_raw_value": min_val,
        "frame_min_measured_pctl": min_pctl,
        "frame_largest_tie_atom_over_n": float(frame.counts.max() / frame.n),
        "snapshot_nonnull_mapped_pctl_quantiles": qs,
    }

    # --- toll differentials: r * k * delta_pctl, against the cost-scale anchors
    anchors = {
        "w_hop": 0.02,
        "median_chosen_edge_w_sim_term_probe7_of_critique": 0.0038,
        "quantisation_floor_in_pctl_units": 0.015,
    }
    tolls = {}
    for rname, r in (("r1", 0.01), ("r2", 0.03)):
        for k in (1, 10, 20):
            # null vs the obscurest MEASURED artist
            d_min = r * k * (min_pctl - null_price)
            # null vs the 1st-percentile measured artist
            d_p1 = r * k * (qs["p1"] - null_price)
            # null vs the median artist (what the device is meant to do)
            d_p50 = r * k * (qs["p50"] - null_price)
            tolls[f"{rname}_k{k}"] = {
                "advantage_over_obscurest_measured": d_min,
                "advantage_over_p1_measured": d_p1,
                "advantage_over_median_measured": d_p50,
            }
    out["toll_advantage_of_a_null_node"] = tolls
    out["cost_scale_anchors"] = anchors

    # --- coverage: nodes present in a cell but ABSENT from the snapshot ---
    cover = {}
    cell_files = {
        "adopted (graph-t15-tiebreakfix)": ADOPTED,
        "ALG-E-MK50 (TrackB, pre-drop)": CELLS / "ALG-E-mutual_knn-k50.bin",
        "ALG-E-MK100 (TrackB, pre-drop)": CELLS / "ALG-E-mutual_knn-k100.bin",
        "ALG-E-TUw-50-50 (TrackB, pre-drop)": CELLS / "ALG-E-trimmed_union-d50-j50.bin",
        "ALG-E-UC (TrackB, pre-drop)": CELLS / "ALG-E-uncapped-none.bin",
        "ALG-B-MK50 (TrackB, pre-drop)": CELLS / "ALG-B-mutual_knn-k50.bin",
        "ALG-B-TUw-50-50 (TrackB, pre-drop)": CELLS / "ALG-B-trimmed_union-d50-j50.bin",
        "ALG-B-UC (TrackB, pre-drop)": CELLS / "ALG-B-uncapped-none.bin",
    }
    snap_keys = set(raw)
    nonnull_keys = {m for m, v in raw.items() if v is not None}
    for name, path in cell_files.items():
        if not path.exists():
            cover[name] = {"missing_file": str(path)}
            continue
        ms = mbids_of(path)
        n = len(ms)
        absent = sum(1 for m in ms if m not in snap_keys)
        null_valued = sum(1 for m in ms if m in snap_keys and raw[m] is None)
        measured = sum(1 for m in ms if m in nonnull_keys)
        cover[name] = {
            "nodes": n,
            "absent_from_snapshot": absent,
            "absent_share": absent / n,
            "present_but_null": null_valued,
            "null_share_present": null_valued / n,
            "ruler_null_total": absent + null_valued,
            "ruler_null_total_share": (absent + null_valued) / n,
            "measured": measured,
        }
        print(f"{name:42} n={n:,}  absent={absent:,}  null={null_valued:,}  "
              f"ruler-null total share={(absent+null_valued)/n:.4f}")
    out["cell_snapshot_coverage"] = cover

    (HERE / "crp_ruler.json").write_text(
        json.dumps(out, indent=1, sort_keys=True), encoding="utf-8"
    )
    print("\n" + json.dumps({k: out[k] for k in
          ("frame_n", "device_null_pctl_frame_pctl_0", "frame_min_raw_value",
           "frame_min_measured_pctl", "snapshot_nonnull_mapped_pctl_quantiles",
           "toll_advantage_of_a_null_node")}, indent=1))
    print("\nwrote crp_ruler.json")


if __name__ == "__main__":
    main()
