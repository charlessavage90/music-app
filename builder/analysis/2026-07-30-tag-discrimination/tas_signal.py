"""TAS-1, TAS-2, TAS-3 -- does the tag signal exist, and does it say anything new?

TAS-1 (gate, NARROW and EXPECTED TO PASS): >= 80% of famous-famous connections
  labelled at both ends. This deliberately does NOT inherit COH-2's coverage
  bar. That bar governed a SENSOR -- an instrument scoring every path, where
  tail blindness returns confident wrong readings about artists it cannot
  see. This is an ACTUATOR: where labels are missing it does not act, rather
  than acting wrongly. Silence is safe in a way blindness is not. The real
  hazard -- silence in the tail plus action at the top tilting the app famous
  -- is TAS-6's, which is where it can be caught.
  FAILURE IS NOT A KILL: it means the assumption about WHERE the rule acts is
  wrong, and the device needs redesigning (spec section 5).

TAS-2 (gate): kill only at effectively zero spread -- median IQR < 0.02. A
  spread below 0.10 is a reported weak-signal flag, NOT a kill: at lambda = 2
  a 0.10 spread still moves the multiplier ~20%, ample to reorder candidates
  whose strengths differ by less. TAS-4 measures reordering directly and
  decides.

TAS-3 (DIAGNOSTIC, no threshold): is agreement just similarity wearing a
  different hat? If agreement rises with strength then
  strength * (1 + lambda * agreement) returns EXACTLY the order strength
  alone gave, because multiplying by something increasing in strength cannot
  reorder it. Agreement could range widely, pass TAS-2, and lambda still be
  inert at every value. This is what makes a TAS-4/TAS-5 null interpretable:
  no variation, variation redundant with similarity, or a real independent
  signal the cap and router absorb are three different findings pointing at
  three different next moves.

SUBSTRATE (spec section 8, TAS-AM2): TAS-1 runs on the ADOPTED ARTIFACT --
  it asks about connections the map has, which exist only post-selection.
  TAS-2 and TAS-3 run on the PRE-CAP CAPTURE -- they ask about the candidates
  selection chooses among, which the artifact has already discarded. No read
  may compare a figure from one side against a figure from the other.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_signal.py --capture <path.npz>
"""

from __future__ import annotations

import argparse
import json
import statistics

import numpy as np

from tas_common import ADOPTED, HERE, agreement, fame_frame
from tas_tags import label_sets

OUT = HERE / "tas_signal.json"

TAS2_KILL_IQR = 0.02
TAS2_WEAK_FLAG_IQR = 0.10
TAS1_FF_GATE = 0.80

# Exactly the BANDS boundaries imported from cb_metrics: "top 1%" starts at
# 0.99, "lower half" is 0.0-0.50. Pinned by test so TAS-1 stays comparable
# with COH-2 rather than drifting into a private banding.
TOP_1PCT = 0.99
LOWER_HALF = 0.50

MIN_FOR_QUARTILES = 4


def edge_class(pu: float, pv: float) -> str:
    """ff = both top 1%; oo = both lower half; fo = everything spanning."""
    if pu >= TOP_1PCT and pv >= TOP_1PCT:
        return "ff"
    if pu < LOWER_HALF and pv < LOWER_HALF:
        return "oo"
    return "fo"


def iqr(values: list[float]) -> float | None:
    """Interquartile range, or None when there are too few points.

    None rather than 0.0: fewer than four points cannot form quartiles, and
    returning 0.0 would read as "flat" and push toward a kill on no evidence.
    """
    if len(values) < MIN_FOR_QUARTILES:
        return None
    quartiles = statistics.quantiles(values, n=4)
    return quartiles[2] - quartiles[0]


def spearman(pairs: list[tuple[float, float]]) -> float:
    """Rank correlation. Ties get average ranks, so a flat side gives 0."""
    xs = _ranks([p[0] for p in pairs])
    ys = _ranks([p[1] for p in pairs])
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return 0.0
    return statistics.correlation(xs, ys)


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = average
        i = j + 1
    return ranks


def _tas1(labels: dict[str, set[str]], frame: dict[str, float]) -> dict:
    """Coverage by connection class, on the ADOPTED ARTIFACT (TAS-AM2)."""
    from artistpath_api.graph_store import GraphStore

    store = GraphStore.from_bytes(ADOPTED.read_bytes())
    counts = {cls: [0, 0] for cls in ("ff", "fo", "oo")}
    for u_idx, mbid_u in enumerate(store.mbids):
        pu = frame.get(mbid_u, 0.0)
        u_labelled = bool(labels.get(mbid_u))
        for v_idx, _sim in store.neighbours_of(u_idx):
            mbid_v = store.mbids[v_idx]
            if mbid_v <= mbid_u:
                continue  # count each undirected connection once
            cls = edge_class(pu, frame.get(mbid_v, 0.0))
            counts[cls][1] += 1
            if u_labelled and labels.get(mbid_v):
                counts[cls][0] += 1
    coverage = {c: (n / d if d else None) for c, (n, d) in counts.items()}
    total_n = sum(n for n, _d in counts.values())
    total_d = sum(d for _n, d in counts.values())
    return {
        "coverage_by_class": {c: (round(v, 4) if v is not None else None)
                              for c, v in coverage.items()},
        "edges_by_class": {c: d for c, (_n, d) in counts.items()},
        "coverage_all_edges": round(total_n / total_d, 4) if total_d else None,
        "gate_ff": TAS1_FF_GATE,
        "passes": (coverage["ff"] or 0.0) >= TAS1_FF_GATE,
    }


def _tas2_tas3(labels: dict[str, set[str]], capture_path: str) -> dict:
    """Within-candidate-list spread and collinearity, on the PRE-CAP CAPTURE."""
    z = np.load(capture_path, allow_pickle=True)
    offsets, cand, rank = z["offsets"], z["cand"], z["rank"]
    mbids = list(z["mbids"])

    spreads: list[float] = []
    rho_pairs: list[tuple[float, float]] = []
    identical_order = considered = too_few = 0

    for u_idx, mbid_u in enumerate(mbids):
        u_set = labels.get(mbid_u)
        if not u_set:
            continue
        lo, hi = int(offsets[u_idx]), int(offsets[u_idx + 1])
        values: list[tuple[float, float]] = []
        for pos in range(lo, hi):
            a = agreement(u_set, labels.get(mbids[int(cand[pos])], set()))
            if a is not None:
                values.append((float(rank[pos]), a))
        spread = iqr([a for _s, a in values])
        if spread is None:
            too_few += 1
            continue
        spreads.append(spread)
        rho_pairs.extend(values)
        considered += 1
        # Does ranking by strength already order agreement? If so, the blend
        # cannot reorder anything at any lambda.
        by_strength = [a for _s, a in sorted(values, key=lambda p: -p[0])]
        if by_strength == sorted(by_strength, reverse=True):
            identical_order += 1

    median_iqr = statistics.median(spreads) if spreads else 0.0
    return {
        "lists_considered": considered,
        "lists_excluded_too_few_labelled": too_few,
        "median_iqr": round(median_iqr, 4),
        "mean_iqr": round(statistics.fmean(spreads), 4) if spreads else None,
        "kills": bool(spreads) and median_iqr < TAS2_KILL_IQR,
        "weak_signal_flag": bool(spreads) and median_iqr < TAS2_WEAK_FLAG_IQR,
        "spearman_strength_vs_agreement": round(spearman(rho_pairs), 4) if rho_pairs else None,
        "identical_order_share": round(identical_order / considered, 4) if considered else None,
        "pairs_scored": len(rho_pairs),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True, help="alge_capture.npz from td_capture.py")
    args = ap.parse_args()

    labels = label_sets()
    frame = fame_frame()

    result = {
        "substrate_note": "TAS-1 on the adopted artifact; TAS-2/TAS-3 on the "
                          "pre-cap capture (TAS-AM2). Never compare across.",
        "labelled_nodes": sum(1 for s in labels.values() if s),
        "tas1": _tas1(labels, frame),
        "tas2_tas3": _tas2_tas3(labels, args.capture),
    }
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
