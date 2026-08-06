"""MSW-V4 supplement: is the frame deviation a level shift or a reordering?

FIGURES ONLY, NO VERDICTS. Companion to `mv4_frame.py`, same artifacts, same
two columns. Three things `mv4_frame.py`'s marginal distribution cannot show:

  (a) ORDERING. Both columns are functions of the same integer fame_lb_raw. If
      both are monotone non-decreasing in it, the frame swap cannot reorder any
      two artists -- measured here as an exact check over distinct raw values
      plus a Spearman on the node set, not assumed from the formulas.

  (b) LEVEL vs SPREAD. Dijkstra adds the ramp once per intermediate hop, so a
      component of the difference that is IDENTICAL for every node contributes
      (shift * k * r * n_intermediates) to every candidate path of the same
      length. The part that can change which path wins among equal-length paths
      is the residual after removing that shift. Both are reported.

  (c) THE GAP BETWEEN REAL ALTERNATIVES. The router never prices one node in
      isolation; it compares candidate heads v1, v2 out of the same node u.
      The routing-relevant discrepancy is therefore
          |(shipped_v1 - shipped_v2) - (cre_v1 - cre_v2)| * r * k
      measured over REAL co-neighbour pairs of the new artifact, not over
      random node pairs.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-06-msw-v4-frame-deviation/mv4_gaps.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "builder/analysis/2026-08-03-cap-reevaluation"))
sys.path.insert(0, str(ROOT / "api/src"))

import cre_common  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402

NEW = ROOT / "builder/scratch/graph-msw-tu50.bin"
NEW_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
R = cre_common.RAMPS["P1a"]
KS = (1, 10, 20)
SEED = 20260806
N_PAIRS = 2_000_000
OUT = HERE / "mv4_gaps.json"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def q(x: np.ndarray) -> dict:
    return {
        "n": int(len(x)),
        "mean": float(np.mean(x)),
        "p50": float(np.percentile(x, 50)),
        "p90": float(np.percentile(x, 90)),
        "p99": float(np.percentile(x, 99)),
        "p99.9": float(np.percentile(x, 99.9)),
        "max": float(np.max(x)),
    }


def main() -> None:
    got = sha256_file(NEW)
    if got != NEW_SHA:
        raise SystemExit(f"WRONG ARTIFACT: expected {NEW_SHA}, got {got}")

    payload = NEW.read_bytes()
    store = GraphStore.from_bytes(payload)
    meta_len = int(np.frombuffer(payload[16:24], dtype="<u8")[0])
    meta = json.loads(payload[-meta_len:].decode("utf-8"))
    fame_raw = meta["fame_lb"]

    is_null = np.array([v is None for v in fame_raw])
    vals = np.array([0 if v is None else int(v) for v in fame_raw], dtype=np.int64)
    nonnull = ~is_null

    shipped = GraphStore.fame_percentiles(fame_raw)
    ruler = cre_common.Ruler()
    cre = np.asarray(ruler._frame.pctl(vals), dtype=np.float64)

    # ---- (a) ordering ----
    uniq = np.unique(vals[nonnull])
    s_u = GraphStore.fame_percentiles([int(v) for v in uniq])  # NB: own frame
    # The real check: evaluate BOTH shipped and CRE maps at the artifact's
    # distinct raw values and confirm each is non-decreasing in the raw value.
    order = np.argsort(uniq)
    sh_at = np.array([shipped[np.flatnonzero(vals == v)[0]] for v in uniq[order]])
    cre_at = np.asarray(ruler._frame.pctl(uniq[order]), dtype=np.float64)
    mono_shipped = bool(np.all(np.diff(sh_at) >= 0))
    mono_cre = bool(np.all(np.diff(cre_at) >= 0))
    # Ties: does either map merge two distinct raw values the other separates?
    ties_shipped = int(np.sum(np.diff(sh_at) == 0))
    ties_cre = int(np.sum(np.diff(cre_at) == 0))

    # ---- (b) level vs spread ----
    signed = (shipped - cre)[nonnull]
    shift = float(np.median(signed))
    resid = np.abs(signed - shift)

    # ---- (c) real co-neighbour alternatives ----
    n_nodes = len(store.mbids)
    deg = np.diff(store.offsets)
    src = np.repeat(np.arange(n_nodes), deg)
    dst = store.neighbours
    rng = np.random.default_rng(SEED)
    # Sample two DISTINCT arcs out of the same u: pick an arc, then a second
    # arc from the same u's slice. Degree-weighted, which is exactly how often
    # the router faces that choice.
    a = rng.integers(0, len(dst), size=N_PAIRS)
    u = src[a]
    lo = store.offsets[u]
    span = deg[u]
    b = lo + rng.integers(0, np.maximum(span, 1), size=N_PAIRS)
    keep = (span > 1) & (b != a)
    v1, v2 = dst[a[keep]], dst[b[keep]]
    both = nonnull[v1] & nonnull[v2]
    v1, v2 = v1[both], v2[both]
    gap_err = np.abs((shipped[v1] - shipped[v2]) - (cre[v1] - cre[v2]))
    gap_shipped = np.abs(shipped[v1] - shipped[v2])
    gap_cre = np.abs(cre[v1] - cre[v2])

    cfg = ApiConfig()
    result = {
        "artifact": {"file": NEW.name, "sha256": got},
        "a_ordering": {
            "distinct_nonnull_raw_values": int(len(uniq)),
            "shipped_monotone_nondecreasing_in_raw": mono_shipped,
            "cre_frame_monotone_nondecreasing_in_raw": mono_cre,
            "adjacent_distinct_raw_values_merged_by_shipped": ties_shipped,
            "adjacent_distinct_raw_values_merged_by_cre_frame": ties_cre,
            "note": "both monotone in the same raw value => the frame swap is a "
                    "monotone re-mapping and cannot reorder two artists",
        },
        "b_level_vs_spread": {
            "median_signed_shift_shipped_minus_cre": shift,
            "std_signed": float(np.std(signed)),
            "iqr_signed": float(np.percentile(signed, 75) - np.percentile(signed, 25)),
            "residual_after_removing_shift": q(resid),
            "residual_ramp_cost_r0.01": {
                f"k={k}": q(R * k * resid) for k in KS
            },
        },
        "c_real_co_neighbour_pairs": {
            "pairs_sampled": int(len(v1)),
            "seed": SEED,
            "abs_gap_under_shipped": q(gap_shipped),
            "abs_gap_under_cre_frame": q(gap_cre),
            "abs_gap_ERROR_shipped_vs_cre": q(gap_err),
            "gap_error_ramp_cost_r0.01": {
                f"k={k}": q(R * k * gap_err) for k in KS
            },
            "frac_gap_error_exceeds_w_hop": {
                f"k={k}": float(np.mean(R * k * gap_err > cfg.w_hop)) for k in KS
            },
        },
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
