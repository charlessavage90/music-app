"""Deliverability on ordinary and obscure pairs — the missing arm.

READ-ONLY on the artifact. Production router settings, unchanged. **No arm, no
rebuild, no config change, no adoption, no threshold.** The decision rule is in
`README.md` and was committed before this ran (`8aa6f84`).

**Reuses the committed scorer rather than reimplementing it.** `walk()` and the
production arm `P` are imported from `../2026-07-24-track2-arm-scorer/run_arms.py`
and `arms.py`; nothing committed is modified. The walk, the depth schedule and
the arm are therefore identical to `../2026-07-26-committed-walk-deliverability/`
by construction. Only the pair set differs.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-obscure-pair-deliverability/run_obscure_pairs.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent
ROOT = ANALYSIS.parents[1]
SCORER = ANALYSIS / "2026-07-24-track2-arm-scorer"

sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(SCORER))
sys.path.insert(0, str(ANALYSIS / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

# --- the decision rule, restated so script and document cannot drift ---------
SEED = 20260726
PAIRS_PER_STRATUM = 12
STRATA = {"OBSCURE": (1, 5), "ORDINARY": (6, 15)}
FIRES_FREELY = 0.20  # >= 20% of distinct interiors below 10 connections
FIRES_NOT = 0.05  # <= 5%
LOW_DEGREE = 10  # "low-connection" means fewer than this
MIN_PAIRS_WITH_INTERIOR = 20  # of 24, else the run is unrepresentative


def load_scorer():
    spec = importlib.util.spec_from_file_location("_run_arms", SCORER / "run_arms.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    if digest != ADOPTED_SHA256:
        raise SystemExit(
            f"GATE 1 FAILED — not the adopted artifact.\n"
            f"  expected {ADOPTED_SHA256}\n  got      {digest}"
        )
    print(f"GATE 1 ok — artifact {GRAPH.name}\n  sha256 {digest}")

    run_arms = load_scorer()
    from arms import MAX_DEPTH, SNAPSHOTS, STAGE1
    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion
    from mirror import MirrorContext, find_path_mirror

    P = next(a for a in STAGE1 if a.name == "P")
    print(f"arm: {P.name} — {P.reading}")
    print(f"depths: {SNAPSHOTS} (max {MAX_DEPTH}) — imported, not transcribed")

    store = GraphStore.load(str(GRAPH))
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    degree = np.diff(np.asarray(store.offsets, dtype=np.int64))
    names = list(store.names)
    n_nodes = len(names)
    print(f"nodes {n_nodes}, median degree {int(np.median(degree))}")

    # --- the sample, exactly as the rule fixes it ----------------------------
    named = np.array([bool(nm and nm.strip()) for nm in names])
    print(f"excluded {int((~named).sum())} nameless node(s) — the known contaminant")

    rng = np.random.default_rng(SEED)
    pairs: list[tuple[str, int, int]] = []
    for label, (lo, hi) in STRATA.items():
        pool = np.nonzero((degree >= lo) & (degree <= hi) & named)[0]
        take = rng.choice(pool, size=PAIRS_PER_STRATUM * 2, replace=False)
        print(f"{label:<9} degree {lo}-{hi}: pool {len(pool)}, drew {len(take)}")
        for i in range(0, len(take), 2):
            pairs.append((label, int(take[i]), int(take[i + 1])))

    print(f"\n{len(pairs)} pairs, {len(SNAPSHOTS)} scored depths each\n")

    # --- route ---------------------------------------------------------------
    stats = {"examined": 0, "floor_active": 0}
    walks: dict[str, list] = {}
    for label, a, b in pairs:
        key = f"{names[a]} -> {names[b]}"
        walks[key] = {
            "stratum": label,
            "src_degree": int(degree[a]),
            "dst_degree": int(degree[b]),
            "paths": run_arms.walk(
                store, a, b, P.cfg, ctx, pop,
                find_path_mirror, Exclusion, KNOWN, stats,
            ),
        }

    # --- extract interiors at the scored depths only -------------------------
    instances: list[int] = []
    per_stratum: dict[str, list[int]] = {k: [] for k in STRATA}
    pairs_with_interior = 0
    empty_pairs: list[str] = []
    scored_walks = 0
    for key, rec in walks.items():
        got = False
        for d in SNAPSHOTS:
            path = rec["paths"][d]
            if path is None:
                continue
            scored_walks += 1
            interior = path[1:-1]
            if interior:
                got = True
            instances.extend(interior)
            per_stratum[rec["stratum"]].extend(interior)
        if got:
            pairs_with_interior += 1
        else:
            empty_pairs.append(key)

    distinct = sorted(set(instances))
    deg_of = {i: int(degree[i]) for i in distinct}

    deg1 = [i for i in distinct if deg_of[i] == 1]
    if deg1:
        raise SystemExit(
            "VOID — a degree-1 artist appears as an interior card, which is "
            f"structurally impossible (DRV-4): {[(i, names[i]) for i in deg1[:5]]}"
        )
    print(f"VOID CHECK ok — no degree-1 interior card among {len(distinct)} distinct")

    if pairs_with_interior < MIN_PAIRS_WITH_INTERIOR:
        print(
            f"\n*** UNREPRESENTATIVE: only {pairs_with_interior} of {len(pairs)} pairs "
            f"produced an interior card (rule requires {MIN_PAIRS_WITH_INTERIOR}). "
            "Shares below are NOT a verdict. ***"
        )
    else:
        print(
            f"REPRESENTATIVENESS ok — {pairs_with_interior} of {len(pairs)} pairs "
            "produced interior cards"
        )

    # --- the numbers ---------------------------------------------------------
    dist_degs = [deg_of[i] for i in distinct]
    below = [i for i in distinct if deg_of[i] < LOW_DEGREE]
    le2 = [i for i in distinct if deg_of[i] <= 2]
    inst_below = [i for i in instances if degree[i] < LOW_DEGREE]
    share = len(below) / len(distinct)
    share_le2 = len(le2) / len(distinct)

    def pct(x: int, n: int) -> str:
        return f"{100.0 * x / n:.2f}%"

    print("\n== MEASURED (arm P, ordinary + obscure pairs) ==")
    print(f"scored walks                   {scored_walks}")
    print(f"interior card instances        {len(instances)}")
    print(f"distinct interior artists      {len(distinct)} ({pct(len(distinct), n_nodes)} of artifact)")
    print(f"minimum degree observed        {min(dist_degs)}")
    print(f"maximum degree observed        {max(dist_degs)}")
    print(f"median degree (distinct)       {int(np.median(dist_degs))}")
    print(f"distinct below {LOW_DEGREE}              {len(below)} ({pct(len(below), len(distinct))})")
    print(f"distinct at <= 2               {len(le2)} ({pct(len(le2), len(distinct))})")
    print(f"cards below {LOW_DEGREE}                 {len(inst_below)} of {len(instances)} ({pct(len(inst_below), len(instances))})")
    if empty_pairs:
        print(f"pairs with no interior at all  {len(empty_pairs)}: {empty_pairs}")

    print("\nby stratum (distinct artists)")
    strat_out = {}
    for label, ints in per_stratum.items():
        ds = sorted(set(ints))
        if not ds:
            print(f"  {label:<9} no interior cards")
            strat_out[label] = None
            continue
        b = [i for i in ds if degree[i] < LOW_DEGREE]
        print(f"  {label:<9} {len(ds):>4} distinct, {len(b):>4} below {LOW_DEGREE} "
              f"({pct(len(b), len(ds))}), min degree {min(int(degree[i]) for i in ds)}, "
              f"{len(ints)} cards")
        strat_out[label] = {
            "distinct": len(ds), "below_10": len(b), "cards": len(ints),
            "min_degree": min(int(degree[i]) for i in ds),
        }

    print("\ndegree distribution of distinct interior artists")
    for lo, hi in [(1, 2), (3, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 10**9)]:
        k = sum(1 for d in dist_degs if lo <= d <= hi)
        lab = f"{lo}-{hi}" if hi < 10**9 else f"{lo}+"
        print(f"  {lab:>7}  {k:>5}  {pct(k, len(distinct)):>7}")

    print("\nthe ten lowest-degree artists delivered as an interior card")
    ic = Counter(instances)
    for i in sorted(distinct, key=lambda x: deg_of[x])[:10]:
        print(f"  deg {deg_of[i]:>3}  {names[i]}  (delivered {ic[i]}x)")

    # --- the decision rule ---------------------------------------------------
    if share >= FIRES_FREELY:
        verdict = "APPEAR FREELY"
    elif share <= FIRES_NOT:
        verdict = "DO NOT APPEAR"
    else:
        verdict = "INTERMEDIATE"

    print("\n== DECISION RULE ==")
    print(f"  distinct below {LOW_DEGREE}: {share:.4f}")
    print(f"  APPEAR FREELY >= {FIRES_FREELY} | DO NOT APPEAR <= {FIRES_NOT}")
    print(f"  VERDICT: {verdict}")
    print("  (predicted before the run: INTERMEDIATE, 10-25%)")

    out = {
        "artifact_sha256": digest,
        "arm": "P",
        "seed": SEED,
        "strata": {k: list(v) for k, v in STRATA.items()},
        "pairs": [
            {"stratum": r["stratum"], "pair": k,
             "src_degree": r["src_degree"], "dst_degree": r["dst_degree"]}
            for k, r in walks.items()
        ],
        "scored_walks": scored_walks,
        "interior_instances": len(instances),
        "distinct_interior": len(distinct),
        "min_degree": min(dist_degs),
        "max_degree": max(dist_degs),
        "median_degree_distinct": int(np.median(dist_degs)),
        "distinct_below_10": len(below),
        "distinct_le_2": len(le2),
        "cards_below_10": len(inst_below),
        "share_below_10": share,
        "share_le_2": share_le2,
        "pairs_with_interior": pairs_with_interior,
        "empty_pairs": empty_pairs,
        "by_stratum": strat_out,
        "degree_histogram_distinct": dict(sorted(Counter(dist_degs).items())),
        "verdict": verdict,
    }
    dest = HERE / "obscure_pairs.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
