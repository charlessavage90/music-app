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
from td_turnover import K, Capture, mask_multiplicative, mutual_undirected, uniform_field

OUT = HERE / "tas_guard.json"

ADVERSE_FRACTION = 0.10  # spec TAS-6
SHUFFLE_SEED = 20260730

# The seed and symmetry td_turnover's committed MULT-SYM arms were run at.
# TAS-AM3a compares against those figures, so this must not drift.
TD2_MULT_SEED = 303

# TAS-AM3b, fixed in the amendment BEFORE the control ran: at or above this
# ratio, TAS-4's turnover cannot be attributed to genre structure.
AM3B_UNSAFE_RATIO = 0.50

# WITHDRAWN with the naive shuffle. Was never pre-registered -- the spec's red
# check fixed no number, and this was a liveness line chosen by the session.
RED_LIVENESS_TURNOVER = 5 * TAS4_KILL_TURNOVER

SUB_DECILE = 0.10  # context only, not a criterion


def randomised_labels(labels: dict[str, set[str]], seed: int) -> dict[str, set[str]]:
    """WITHDRAWN by TAS-AM3. Shuffles label sets between ALL artists.

    Retained, not deleted: its figure is cited in TAS-AM3 as the evidence that
    the direction was known before the amendment was written, so the function
    that produced it must stay runnable. Do not use it as a control -- it moves
    two knobs, because it changes WHICH artists are labelled and so halves the
    count of pairs where the rule acts.
    """
    rng = random.Random(seed)
    keys = sorted(labels)
    values = [labels[k] for k in keys]
    rng.shuffle(values)
    return dict(zip(keys, values))


def permuted_labels_among_labelled(
    labels: dict[str, set[str]], seed: int
) -> dict[str, set[str]]:
    """TAS-AM3b's control: permute label sets among LABELLED artists only.

    Holds fixed exactly which artists carry labels -- and therefore the number
    of pairs where the device acts, its symmetry, and the set-size
    distribution. One knob moves: which labels a given artist holds.
    """
    rng = random.Random(seed)
    labelled = sorted(k for k, v in labels.items() if v)
    values = [labels[k] for k in labelled]
    rng.shuffle(values)
    out = dict(labels)
    out.update(zip(labelled, values))
    return out


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


def _am3a_equivalence(cap: Capture) -> dict:
    """TAS-AM3a: prove the ranking path IS td_turnover's, and can move a lot.

    Passes only if the mask is bit-identical to mask_multiplicative AND the
    turnover reproduces the committed TD-2 MULT-SYM figures to five decimals.
    A large response is thereby demonstrated against a fixed external
    reference rather than against a threshold someone chose.
    """
    committed = {
        row["arm"]: row["turnover_frac"]
        for row in json.loads((HERE / "td_turnover.json").read_text(encoding="utf-8"))["arms"]
    }
    base_edges = mutual_undirected(cap, cap.pos < K)
    cells: dict[str, dict] = {}
    for lam in (value for value in LAMBDAS if value > 0):
        field = uniform_field(cap.s_node, cap.s_cand, cap.n, TD2_MULT_SEED, True)
        mask = mask_tag(cap, field, lam)
        identical = bool(np.array_equal(mask, mask_multiplicative(cap, lam, TD2_MULT_SEED, True)))
        turnover = edge_turnover(base_edges, mutual_undirected(cap, mask))
        measured = round(turnover["turnover_share"], 5)
        expected = committed[f"MULT-SYM-{lam}"]
        cells[str(lam)] = {
            "mask_bit_identical": identical,
            "turnover": measured,
            "td2_committed_turnover": expected,
            "reproduces": identical and measured == expected,
        }
        print(f"  lambda={lam}: bit-identical={identical} "
              f"turnover={measured} vs TD-2 {expected}", flush=True)
    return {
        "reference": "td_turnover.json MULT-SYM arms (synthetic symmetric field, "
                     f"seed {TD2_MULT_SEED})",
        "per_lambda": cells,
        "passes": all(cell["reproduces"] for cell in cells.values()),
    }


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

    print("TAS-AM3a: liveness and equivalence against the committed TD-2 field:", flush=True)
    am3a = _am3a_equivalence(cap)

    print("TAS-AM3b: null control, labels permuted among labelled artists only:", flush=True)
    permuted = permuted_labels_among_labelled(labels, SHUFFLE_SEED)
    labelled_keys = [k for k, v in labels.items() if v]
    null_moved = sum(1 for k in labelled_keys if permuted[k] != labels[k])
    _null_base, null_arms = _arms(cap, agreement_field(cap, permuted), pctl)
    null_ratio = {
        lam: round(null_arms[lam]["turnover_share"] / real_arms[lam]["turnover_share"], 4)
        for lam in real_arms
    }

    print("WITHDRAWN naive shuffle, re-run for the record only:", flush=True)
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
        "tas_am3a_liveness_and_equivalence": am3a,
        "tas_am3b_null_control": {
            "seed": SHUFFLE_SEED,
            "labelled_artists_whose_labels_moved": null_moved,
            "per_lambda_turnover": {lam: cell["turnover_share"] for lam, cell in null_arms.items()},
            "real_per_lambda_turnover": {
                lam: cell["turnover_share"] for lam, cell in real_arms.items()
            },
            "null_over_real": null_ratio,
            "attribution_unsafe_threshold": AM3B_UNSAFE_RATIO,
            "attribution_unsafe": any(v >= AM3B_UNSAFE_RATIO for v in null_ratio.values()),
            "note": "A SMALL null is the CORRECT result, not a failure (TAS-AM3b). "
                    "Below the threshold, report the ratio and nothing more -- no "
                    "claim about tags is licensed by this control.",
        },
        "withdrawn_naive_shuffle": {
            "status": "WITHDRAWN by TAS-AM3; re-run for the record only, never a check",
            "seed": SHUFFLE_SEED,
            "artists_whose_labels_moved": moved,
            "liveness_threshold_turnover": RED_LIVENESS_TURNOVER,
            "liveness_threshold_is_pre_registered": False,
            "per_lambda_turnover": {lam: cell["turnover_share"] for lam, cell in red_arms.items()},
            "fired": all(value >= RED_LIVENESS_TURNOVER for value in red_turnovers),
            "why_withdrawn": "Shuffling labels destroys genre overlap rather than "
                             "randomising it, so no randomised frame can produce large "
                             "turnover for a Jaccard device. It also moves two knobs: it "
                             "changes WHICH artists are labelled.",
        },
    }
    Path(args.out).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
