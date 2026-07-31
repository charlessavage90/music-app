"""TAS-6 (obscurity guard) and the RED instrument check -- SELECTION SIDE ONLY.

TAS-6 IS REPORTED, NEVER A SUCCESS SIGNAL. Adverse at a >= 10% reduction in
famous->obscure supply. An adverse TAS-6 BARS any recommendation to adopt,
whatever TAS-4/TAS-5 show, until a router-side answer exists. It is the guard on
the neutral rule: unlabelled artists are disproportionately obscure, so a
careless treatment of missing labels punishes exactly the artists the product
exists to surface. Growth is not good news it can report -- it is simply not
adverse.

THE RED CHECK. A measurement that has only ever come back green is not evidence
yet. Fed a randomised tag frame -- same labelled share, label sets shuffled
between artists -- the harness must still report large turnover.

  WHAT THE SHUFFLE CONTROLS THAT TD-2'S SYNTHETIC FIELD DID NOT. TD-2 compared
  against a uniform random draw, which differs from the real frame in several
  ways at once. Shuffling the real frame preserves the labelled share (so the
  46% of artists with no labels stay inert), the distribution of label-set
  sizes, and the marginal distribution of agreement values -- while destroying
  the correspondence between genre agreement and graph structure. It is
  therefore a one-column control where TD-2's was not.

  AND THAT MAKES IT MORE THAN A LIVENESS CHECK, WHICH IS A HAZARD. The
  real-vs-shuffled gap is informative about tags, and it is NOT a
  pre-registered criterion. It is reported here as an instrument reading. Any
  read of it as evidence about tags needs its own pre-registration, designed
  cold; this module must not be cited as one.

SUBSTRATE: the pre-cap capture (TAS-AM2, selection side). The routing halves of
both measurements stay in Task 7 -- they need tas_route.py.

Both measurements use the ADOPTED fame frame as a FIXED reference population,
never each arm's own. A variant's own frame would renormalise fame underneath
the comparison (the _log_scaled hazard, graph.py:148).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_guard.py --capture <path.npz>
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np

from tas_common import HERE, fame_frame
from tas_select import LAMBDAS, TAS4_KILL_TURNOVER, agreement_field, edge_turnover, mask_tag
from tas_signal import LOWER_HALF, TOP_1PCT
from tas_tags import label_sets
from td_turnover import K, Capture, mutual_undirected

OUT = HERE / "tas_guard.json"

ADVERSE_FRACTION = 0.10  # spec TAS-6
SHUFFLE_SEED = 20260730

# NOT a pre-registered bar. The spec says the red check must report "large"
# turnover and fixes no number, so this is a harness-liveness line chosen here:
# materially above the TAS-4 kill bar. Named rather than left implicit.
RED_LIVENESS_TURNOVER = 5 * TAS4_KILL_TURNOVER

SUB_DECILE = 0.10  # context only, not a criterion


def randomised_labels(labels: dict[str, set[str]], seed: int) -> dict[str, set[str]]:
    """Shuffle label sets between artists, preserving the labelled share."""
    rng = random.Random(seed)
    keys = sorted(labels)
    values = [labels[k] for k in keys]
    rng.shuffle(values)
    return dict(zip(keys, values))


def is_adverse(baseline: int, arm: int) -> bool:
    if baseline == 0:
        return False
    return (baseline - arm) / baseline >= ADVERSE_FRACTION


def famous_to_obscure(keys: np.ndarray, pctl: np.ndarray, n: int) -> int:
    """Connections with one end in the top 1% and the other in the lower half.

    The spec names this quantity but not its boundary. Fixed here as the literal
    reading, reusing the bands TAS-1 already uses. Deliberately NOT tas_select's
    `fo` class, which is "everything spanning" and includes two mid-tier artists
    -- that would overstate famous->obscure supply. Nodes absent from the fixed
    frame carry NaN and are excluded, since NaN comparisons are False.
    """
    pu, pv = pctl[keys // n], pctl[keys % n]
    lo, hi = np.minimum(pu, pv), np.maximum(pu, pv)
    return int(((hi >= TOP_1PCT) & (lo < LOWER_HALF)).sum())


def touches_sub_decile(keys: np.ndarray, pctl: np.ndarray, n: int) -> int:
    """Context only: connections with at least one end in the bottom 10%."""
    pu, pv = pctl[keys // n], pctl[keys % n]
    return int((np.minimum(pu, pv) < SUB_DECILE).sum())


def _arms(cap: Capture, field: np.ndarray, pctl: np.ndarray) -> tuple[dict, dict]:
    """Baseline plus every lambda > 0 for one tag frame."""
    base_mask = mask_tag(cap, field, 0.0)
    # lambda = 0 must reproduce the baseline for ANY frame -- the multiplier is
    # exactly 1 whatever the field says. Asserting it here re-runs the green
    # check against the shuffled frame too, which the plan did not ask for and
    # which costs nothing.
    assert np.array_equal(base_mask, cap.pos < K), "lambda=0 did not reproduce the baseline"
    base_edges = mutual_undirected(cap, base_mask)

    baseline = {
        "edges": int(base_edges.size),
        "famous_to_obscure": famous_to_obscure(base_edges, pctl, cap.n),
        "touching_sub_decile": touches_sub_decile(base_edges, pctl, cap.n),
    }
    arms: dict[str, dict] = {}
    for lam in (value for value in LAMBDAS if value > 0):
        arm_edges = mutual_undirected(cap, mask_tag(cap, field, lam))
        turnover = edge_turnover(base_edges, arm_edges)
        fo_count = famous_to_obscure(arm_edges, pctl, cap.n)
        arms[str(lam)] = {
            "edges": int(arm_edges.size),
            "turnover_share": round(turnover["turnover_share"], 5),
            "famous_to_obscure": fo_count,
            "famous_to_obscure_change": round(
                (fo_count - baseline["famous_to_obscure"]) / baseline["famous_to_obscure"], 5
            ),
            "adverse": is_adverse(baseline["famous_to_obscure"], fo_count),
            "touching_sub_decile": touches_sub_decile(arm_edges, pctl, cap.n),
        }
        print(f"  lambda={lam}: edges {arm_edges.size}, "
              f"famous->obscure {fo_count} (base {baseline['famous_to_obscure']})", flush=True)
    return baseline, arms


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True, help="alge_capture.npz from td_capture.py")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cap = Capture(Path(args.capture))
    labels = label_sets()
    frame = fame_frame()
    pctl = np.full(cap.n, np.nan, dtype=np.float64)
    for i, mbid in enumerate(cap.mbids):
        value = frame.get(mbid)
        if value is not None:
            pctl[i] = value

    print("TAS-6 (selection half), real tag frame:", flush=True)
    real_base, real_arms = _arms(cap, agreement_field(cap, labels), pctl)

    print("RED check, shuffled tag frame:", flush=True)
    shuffled = randomised_labels(labels, SHUFFLE_SEED)
    moved = sum(1 for k in labels if shuffled[k] != labels[k])
    _red_base, red_arms = _arms(cap, agreement_field(cap, shuffled), pctl)

    red_turnovers = [cell["turnover_share"] for cell in red_arms.values()]
    result = {
        "substrate": "pre-cap capture of the ALG-E archive (TAS-AM2, selection "
                     "side). Routing halves of TAS-6 and the red check remain "
                     "Task 7's. Never compare these figures with TAS-1 or TAS-5.",
        "tas6_selection_half": {
            "definition": "one end in the top 1% by fame percentile, the other "
                          "in the lower half, over the FIXED adopted frame",
            "adverse_threshold": ADVERSE_FRACTION,
            "baseline": real_base,
            "per_lambda": real_arms,
            "adverse_at_any_lambda": any(cell["adverse"] for cell in real_arms.values()),
        },
        "red_check": {
            "seed": SHUFFLE_SEED,
            "artists_whose_labels_moved": moved,
            "liveness_threshold_turnover": RED_LIVENESS_TURNOVER,
            "liveness_threshold_is_pre_registered": False,
            "per_lambda_turnover": {lam: cell["turnover_share"] for lam, cell in red_arms.items()},
            "fired": all(value >= RED_LIVENESS_TURNOVER for value in red_turnovers),
            "note": "The real-vs-shuffled gap is an INSTRUMENT reading, not a "
                    "pre-registered criterion. Reading it as evidence about tags "
                    "needs its own pre-registration, designed cold.",
        },
    }
    Path(args.out).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
