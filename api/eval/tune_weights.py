"""Tune the cost-function weights against the objective harness (Tier-2).

Instead of hand-picking weights, define a scalar objective from the measured
metrics and let Bayesian optimisation (Optuna) search the weight space. Pairs
are split train/test so the tuned weights are checked for generalisation, not
just fit to the panel.

Objective (maximised), all per-path metrics averaged over the train panel:
    score = bottleneck_similarity                 # smoothness — keep high
          - LAMBDA_HUB * max_interior_hub_penalty # avoid famous crossroads
          - LAMBDA_LEN * length_deviation         # land near TARGET_LEN

These three coefficients ENCODE THE PRODUCT TRADE-OFF and are meant to be
argued about — they are constants here, printed on every run, and the per-metric
results are reported so the trade-off struck is visible, not hidden in a scalar.

Usage:
    cd api && UV_LINK_MODE=copy uv run --extra tune python eval/tune_weights.py \
        [graph.bin] [n_trials] [n_pairs_per_stratum]
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import optuna

from artistpath_api.config import ApiConfig
from artistpath_api.evaluation import degree_percentile_threshold, path_metrics, summarise
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path

SEED = 7  # distinct from the baseline panel (seed 42) so we don't tune on it
TARGET_LEN = 7.0
LAMBDA_HUB = 1.0
LAMBDA_LEN = 0.3


def build_pairs(store, n_each, rng):
    n = store.artist_count
    degrees = np.diff(store.offsets)
    obscure = np.where(degrees <= 5)[0]
    pairs = []
    while len([p for p in pairs if p[2] == "random"]) < n_each:
        a, b = int(rng.integers(n)), int(rng.integers(n))
        if a != b:
            pairs.append((a, b, "random"))
    while len([p for p in pairs if p[2] == "obscure"]) < n_each and len(obscure) > 1:
        a, b = (int(x) for x in rng.choice(obscure, size=2, replace=False))
        if a != b:
            pairs.append((a, b, "obscure"))
    return pairs


def evaluate(store, pairs, cfg, hub_threshold):
    metrics, max_hubpens = [], []
    for a, b, _ in pairs:
        path = find_path(store, a, b, [], cfg)
        if path and len(path) >= 2:
            metrics.append(path_metrics(store, path, hub_threshold))
            interior = path[1:-1]
            max_hubpens.append(
                max((float(store.hub_penalty[n]) for n in interior), default=0.0)
            )
    s = summarise(metrics)
    s["mean_max_hubpen"] = (sum(max_hubpens) / len(max_hubpens)) if max_hubpens else 0.0
    return s


def score(s):
    if not s:
        return -1e9
    len_dev = min(1.0, abs(s["mean_length"] - TARGET_LEN) / TARGET_LEN)
    return s["mean_bottleneck_sim"] - LAMBDA_HUB * s["mean_max_hubpen"] - LAMBDA_LEN * len_dev


def report(label, s):
    print(
        f"  {label:14s} score {score(s):+.3f} | "
        f"hub-traversal {s['hub_traversal_rate']*100:5.1f}% | "
        f"max-hubpen {s['mean_max_hubpen']:.3f} | "
        f"len {s['mean_length']:5.1f} | "
        f"bottleneck-sim {s['mean_bottleneck_sim']:.3f}"
    )


def main():
    graph = sys.argv[1] if len(sys.argv) > 1 else "../builder/scratch/graph-75k.bin"
    n_trials = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    n_each = int(sys.argv[3]) if len(sys.argv) > 3 else 12

    store = GraphStore.load(graph)
    hub_threshold = degree_percentile_threshold(store, 0.01)
    rng = np.random.default_rng(SEED)
    all_pairs = build_pairs(store, n_each * 2, rng)  # 2x, split in half
    rng.shuffle(all_pairs)
    split = len(all_pairs) // 2
    train, test = all_pairs[:split], all_pairs[split:]

    print(f"{store.artist_count:,} artists | hub threshold {hub_threshold} | "
          f"{len(train)} train / {len(test)} test pairs")
    print(f"objective: smoothness - {LAMBDA_HUB}*hubpen - {LAMBDA_LEN}*len_dev "
          f"(target len {TARGET_LEN})")

    base = ApiConfig()

    def objective(trial):
        cfg = replace(
            base,
            w_sim=trial.suggest_float("w_sim", 0.5, 6.0),
            w_jump=trial.suggest_float("w_jump", 0.0, 4.0),
            w_floor=trial.suggest_float("w_floor", 0.0, 4.0),
            w_hop=trial.suggest_float("w_hop", 0.0, 0.5),
            w_hub=trial.suggest_float("w_hub", 0.0, 8.0),
        )
        return score(evaluate(store, train, cfg, hub_threshold))

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(
        direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED)
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best = replace(base, **study.best_params)
    print("\n=== baseline (current production weights, w_hub=0) ===")
    report("train", evaluate(store, train, base, hub_threshold))
    report("test", evaluate(store, test, base, hub_threshold))
    print("\n=== tuned weights ===")
    for k in ("w_sim", "w_jump", "w_floor", "w_hop", "w_hub"):
        print(f"  {k} = {getattr(best, k):.3f}")
    report("train", evaluate(store, train, best, hub_threshold))
    report("test", evaluate(store, test, best, hub_threshold))


if __name__ == "__main__":
    main()
