"""TAS-4: would a tag-aware ranking change which neighbours survive selection?

SIMULATED, NOT BUILT. This measures the INPUT to a rebuild, not its output:
mutual selection means one artist's reordering can delete an edge the other
still ranks, so the built consequence is not derivable from here alone. Stated
in the prereg's TAS-4 bound and repeated because it is the easiest thing to
over-read.

KILL for the build-time architecture (AMENDED, TAS-AM1): if at every lambda the
symmetric-difference EDGE TURNOVER is <= 1%.

  Plain: if fewer than one connection in a hundred is different across the whole
  map, no journey will change in a way you could notice. At the original bar,
  about one journey in three would have contained a connection that no longer
  exists.

  The original bar -- "median artist swaps <= 2 of 50" -- is WITHDRAWN AS FALSE
  and is not implemented here. TD-2 measured that swap rate as ~8.4% of all
  connections differing (turnover ~= 2.11x the swap rate: mutual selection is
  near-neutral on deletions, but every swap also PROMOTES a neighbour and
  per-artist swap counting never saw the creations). TD-3 measured the median
  reading 0 while 6.3% of the map moved, because the device is inert wherever
  labels are missing -- the zero-inflated case TAS-1 exists to expect. TD-4
  refuted the remaining defence: routed connections sit DEEPER in both
  endpoints' lists than average, so they are deleted at 1.09-1.26x the
  population rate, never below 1.0.

  The median is therefore RETIRED as this criterion's statistic. It is still
  reported, precisely so TD-3's zero-inflation stays visible in this record
  rather than being taken on trust from another one.

SUBSTRATE (TAS-AM1, TAS-AM2): the PRE-CAP CAPTURE -- the Track B
ALG-E-mutual_knn-k50 cell's inputs, NOT the adopted artifact, which predates the
nameless-artist drop and cannot be reproduced from the pipeline capture. Every
arm here and its lambda=0 baseline sit on that one substrate, so no
arm-to-baseline comparison spans graphs. NO READ MAY COMPARE A FIGURE FROM HERE
AGAINST A TAS-1 OR TAS-5 FIGURE, which are artifact-side.

REUSED, NOT REIMPLEMENTED: `Capture`, `mutual_undirected` and `swaps_per_node`
come from td_turnover.py, whose --verify green check asserts that this exact
reconstruction reproduces ALG-E-mutual_knn-k50.bin edge for edge. The only new
machinery here is the ranking field, which supplies real tag agreement where
td_turnover supplied a synthetic uniform one.

Selection binds ONLY where an artist's own list exceeds k. The share of such
artists, and of edges incident on them, is reported -- the lever cannot reach
further than that.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_select.py --capture <path.npz>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from tas_common import HERE, fame_frame, neutral_for, resolved_agreement
from tas_signal import LOWER_HALF, TOP_1PCT
from tas_tags import label_sets
from td_turnover import K, Capture, mutual_undirected, swaps_per_node

OUT = HERE / "tas_select.json"

# Prereg section 1. lambda = 0 is the isolating baseline and reproduces
# production exactly, not approximately.
LAMBDAS = [0.0, 0.25, 0.5, 1.0, 2.0]

# TAS-AM1. The owner set this materiality line on 2026-07-30 after being shown
# the conversion in journey terms; it is his call, not a derivation.
TAS4_KILL_TURNOVER = 0.01

CLASSES = ("ff", "fo", "oo")


def agreement_field(cap: Capture, labels: dict[str, set[str]]) -> np.ndarray:
    """resolved_agreement for every directed candidate slot, in Capture order.

    The neutral rule is applied through tas_common.neutral_for and
    resolved_agreement -- the ONE resolution path. It is not reimplemented
    here even though an inline median would be faster: it is the
    pre-registration's one dormant term (inert at lambda=0, active in every
    arm), so a second copy would be free to drift from the routing arm's while
    both documents claimed they shared one rule.
    """
    sets = [labels.get(m, set()) for m in cap.mbids]
    field = np.empty(cap.total, dtype=np.float64)
    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if lo == hi:
            continue
        own = sets[u]
        cand_sets = [sets[c] for c in cap.s_cand[lo:hi]]
        neutral = neutral_for(own, cand_sets)
        for i, candidate in enumerate(cand_sets):
            field[lo + i] = resolved_agreement(own, candidate, neutral)
        if u % 10000 == 0:
            print(f"  agreement field {u}/{cap.n}", flush=True)
    return field


def mask_tag(cap: Capture, field: np.ndarray, lam: float) -> np.ndarray:
    """Top-K selection mask under rank' = rank * (1 + lam * agreement).

    Identical in form to td_turnover.mask_multiplicative, which drove the same
    reranking from a synthetic uniform field; the only difference is that this
    field is real tag agreement. Ties break on lowest candidate id, which is
    lowest MBID because ids are assigned in sorted-MBID order (design section
    9) -- exactly mutual_knn_cap's key.

    At lam = 0 the multiplier is exactly 1.0, so this returns the baseline
    selection bit for bit. main() asserts that rather than assuming it.
    """
    newrank = cap.s_rank * (1.0 + lam * field)
    order = np.lexsort((cap.s_cand, -newrank, cap.s_node))
    newpos = np.empty(cap.total, dtype=np.int64)
    newpos[order] = np.arange(cap.total, dtype=np.int64) - np.repeat(
        cap.offsets[:-1], cap.lengths
    )
    return newpos < K


def edge_turnover(base_edges: np.ndarray, arm_edges: np.ndarray) -> dict:
    """Symmetric difference of two undirected edge-key sets (TAS-AM1).

    Deletions and creations are reported SEPARATELY and both are counted.
    Per-artist swap counting sees only the drop; TD-2 measured that every swap
    also promotes a neighbour, and promoted neighbours become surviving
    connections at nearly the same rate.
    """
    deleted_keys = base_edges[~np.isin(base_edges, arm_edges, assume_unique=True)]
    created_keys = arm_edges[~np.isin(arm_edges, base_edges, assume_unique=True)]
    total = int(base_edges.size)
    return {
        "deleted": int(deleted_keys.size),
        "created": int(created_keys.size),
        "turnover_share": (
            (deleted_keys.size + created_keys.size) / total if total else 0.0
        ),
        "deleted_keys": deleted_keys,
        "created_keys": created_keys,
    }


def classify_keys(keys: np.ndarray, pctl: np.ndarray, n: int) -> dict[str, int]:
    """Count packed undirected edge keys by pair class.

    The vectorised twin of tas_signal.edge_class, sharing its boundaries by
    import and pinned against it by test. Nodes absent from the fixed fame
    frame are counted as `unframed` rather than defaulting to percentile 0,
    which would silently class them obscure -- the capture and the adopted
    artifact differ by a handful of nodes (TAS-AM2).
    """
    pu, pv = pctl[keys // n], pctl[keys % n]
    unframed = np.isnan(pu) | np.isnan(pv)
    ff = (pu >= TOP_1PCT) & (pv >= TOP_1PCT)
    oo = (pu < LOWER_HALF) & (pv < LOWER_HALF)
    framed = ~unframed
    counts = {
        "ff": int((ff & framed).sum()),
        "oo": int((oo & framed).sum()),
        "fo": int((~(ff | oo) & framed).sum()),
    }
    counts["unframed"] = int(unframed.sum())
    return counts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True, help="alge_capture.npz from td_capture.py")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cap = Capture(Path(args.capture))
    labels = label_sets()
    frame = fame_frame()  # percentile over the ADOPTED artifact: a FIXED frame

    pctl = np.full(cap.n, np.nan, dtype=np.float64)
    for i, mbid in enumerate(cap.mbids):
        value = frame.get(mbid)
        if value is not None:
            pctl[i] = value

    print(f"capture: {cap.n} nodes, {cap.total} directed candidates", flush=True)
    field = agreement_field(cap, labels)

    base_mask = mask_tag(cap, field, 0.0)
    # Spec section 4's GREEN check on the selection side. Asserted, not assumed:
    # if lambda=0 does not reproduce the baseline, nothing below counts.
    assert np.array_equal(base_mask, cap.pos < K), "lambda=0 did not reproduce the baseline"
    base_edges = mutual_undirected(cap, base_mask)
    base_by_class = classify_keys(base_edges, pctl, cap.n)

    eu, ev = base_edges // cap.n, base_edges % cap.n
    node_labelled = np.array([bool(labels.get(m)) for m in cap.mbids])
    # Where the device actually acts: a slot whose two ends are both labelled
    # got a real Jaccard, everything else got the neutral value.
    acted = node_labelled[cap.s_node] & node_labelled[cap.s_cand]

    per_lambda: dict[str, dict] = {}
    for lam in (value for value in LAMBDAS if value > 0):
        arm_mask = mask_tag(cap, field, lam)
        arm_edges = mutual_undirected(cap, arm_mask)
        turnover = edge_turnover(base_edges, arm_edges)
        swaps = swaps_per_node(cap, base_mask, arm_mask)
        binding_swaps = swaps[cap.binds]
        per_lambda[str(lam)] = {
            "deleted": turnover["deleted"],
            "created": turnover["created"],
            "turnover_share": round(turnover["turnover_share"], 5),
            "edges_after": int(arm_edges.size),
            "deleted_by_class": classify_keys(turnover["deleted_keys"], pctl, cap.n),
            "created_by_class": classify_keys(turnover["created_keys"], pctl, cap.n),
            # Mean, never median (TAS-AM1). The median is carried below only so
            # TD-3's zero-inflation is visible in this record too.
            "mean_swaps_binding": round(float(binding_swaps.mean()), 4),
            "mean_swaps_all_nodes": round(float(swaps.mean()), 4),
            "median_swaps_binding_RETIRED_STATISTIC": float(np.median(binding_swaps)),
        }
        print(f"lambda={lam}: turnover {turnover['turnover_share']:.5f} "
              f"(-{turnover['deleted']} +{turnover['created']})", flush=True)

    result = {
        "substrate": "pre-cap capture of the ALG-E archive; reconstructs "
                     "ALG-E-mutual_knn-k50 (TAS-AM1/TAS-AM2). NOT the adopted "
                     "artifact -- never compare these figures with TAS-1 or TAS-5.",
        "capture_nodes": cap.n,
        "directed_candidates": cap.total,
        "nodes_in_capture_absent_from_fame_frame": int(np.isnan(pctl).sum()),
        "labelled_nodes": int(node_labelled.sum()),
        "labelled_node_share": round(float(node_labelled.mean()), 4),
        "slots_where_the_rule_acts_share": round(float(acted.mean()), 4),
        "baseline_edges": int(base_edges.size),
        "baseline_edges_by_class": base_by_class,
        "binding_artists": int(cap.binds.sum()),
        "binding_share": round(float(cap.binds.mean()), 4),
        "edges_incident_on_binding_node_share": round(
            float((cap.binds[eu] | cap.binds[ev]).mean()), 5),
        "kill_threshold_turnover": TAS4_KILL_TURNOVER,
        "per_lambda": per_lambda,
        "tas4_kills": all(
            cell["turnover_share"] <= TAS4_KILL_TURNOVER for cell in per_lambda.values()
        ),
    }
    Path(args.out).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
