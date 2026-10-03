"""`SNW-CH0`: the chance-firing rate and power of `SNW-F`, ESTIMATED BEFORE THE RUN on a synthetic layout.

Reads no answer file. The layout uses only the totals the `DSL-` findings note §3 publishes: today's
side 119 steps and 9 marks, the candidate's 197 steps and 43 marks, 24 journeys a side. How those
steps and marks spread over journeys is not published, so it is assumed: steps as evenly as the totals
allow, marks uniformly at random over each side's steps. Values are synthetic: continuous N(0, 1), and
a four-level version standing in for the rater's 0-3 scale (ties). The three measures are drawn
INDEPENDENT, which makes the any-measure chance rate an upper estimate (real measures correlate).

The run computes the exact rate on the real layout and real values (`snw_test.evaluate`); this
script exists so the pre-registration can state a computed figure rather than an asserted one.

    cd api && UV_LINK_MODE=copy uv run python -u ../builder/analysis/2026-10-03-snw-marks-test/snw_chance_estimate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import snw_test as s  # noqa: E402

LAYOUT = {0: [5] * 23 + [4], 1: [9] * 5 + [8] * 19}   # steps per journey: today 119, candidate 197
MARKS = {0: 9, 1: 43}
REPLICATES = 400          # synthetic datasets per setting
DRAWS = 2000              # null draws inside each evaluate()


def layout(rng, auc: float, discrete: bool) -> s.Steps:
    J, SIDE, I = [], [], []
    j = 0
    for side, lens in LAYOUT.items():
        for n in lens:
            J += [j] * n; SIDE += [side] * n; I += list(range(n)); j += 1
    J, SIDE = np.array(J), np.array(SIDE)
    marked = np.zeros(len(J), bool)
    for side, k in MARKS.items():
        marked[rng.choice(np.nonzero(SIDE == side)[0], size=k, replace=False)] = True
    st = s.Steps(J, np.array(I), SIDE, np.zeros(len(J), bool), np.ones(len(J), bool), marked)
    delta = np.sqrt(2) * NormalDist().inv_cdf(auc)   # AUC of N(-delta,1) below N(0,1)
    for m in s.MEASURES:
        v = rng.normal(size=len(J)) - delta * marked
        st.values[m] = np.digitize(v, [-0.8, 0.0, 0.8]).astype(float) if discrete else v
    return st


def rate(auc: float, discrete: bool, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    fire = {m: 0 for m in s.MEASURES}
    anyf = 0
    for r in range(REPLICATES):
        out = s.evaluate(layout(rng, auc, discrete), n_draws=DRAWS, seed=seed * 1000 + r)
        f = [out["measures"][m]["outcome"] == "fires" for m in s.MEASURES]
        for m, x in zip(s.MEASURES, f):
            fire[m] += x
        anyf += any(f)
    return {"per_measure": {m: fire[m] / REPLICATES for m in s.MEASURES}, "any": anyf / REPLICATES}


def main() -> int:
    out = {"layout": "SNW-CH0 synthetic, from findings 2026-10-01 §3 totals", "replicates": REPLICATES,
           "draws": DRAWS, "results": {}}
    for discrete in (False, True):
        for auc in (0.5, 0.65, 0.70, 0.75, 0.80):
            k = f"{'four_level' if discrete else 'continuous'}_trueAUC_{auc:.2f}"
            out["results"][k] = rate(auc, discrete, seed=int(auc * 100) + 7 * discrete)
            print(k, out["results"][k], flush=True)
    (Path(__file__).parent / "snw_chance_estimate.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
