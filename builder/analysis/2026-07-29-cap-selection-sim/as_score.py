"""AS scorer -- computes every criterion, gate and noise floor from the raw records.

Governed by `docs/superpowers/specs/2026-07-29-algorithm-selection-preregistration.md`.
Reads `as_raw_records.json` only; makes no network call, so it can be re-run and
independently reviewed without re-hitting the service.

Implements, by clause:
  SS3   AS-C1 sub-decile yield, AS-C2 novelty/absence, AS-C3 overlap with ALG-E,
        AS-C4 tail, AS-C5 sub-median yield.
  SS4   AS-N noise floor (|ALG-A - ALG-F|, per criterion per stratum); the 3x rule;
        the absolute floor of 1.0 candidate when AS-N is exactly zero.
  SS4   AS-G1 arm integrity (>= 95% HTTP 200); AS-G2 design informativeness.

Two clauses this deliberately enforces rather than assumes:
  SS1.3 AS-C1 is a LOWER BOUND for any arm with non-zero AS-C2, and is labelled as
        such in the output. Candidates absent from the adopted artifact have no
        percentile and cannot be counted as sub-decile.
  SS1.5 Scores are NEVER compared across arms. AS-C4 reports score shape within an
        arm; AS-C3 compares arms through ranks and set overlap only.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-cap-selection-sim/as_score.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
RAW = HERE / "as_raw_records.json"
OUT = HERE / "as_scores.json"

BASELINE = "ALG-E"
NOISE_PAIR = ("ALG-A", "ALG-F")
ARM_LIMIT = {"ALG-C": 50}  # SS1: every other arm is limit_100
DEFAULT_LIMIT = 100
STRATA_ORDER = (
    "top_0.1pct",
    "top_1pct_below_0.1pct",
    "top_decile_below_1pct",
    "pctl_50_to_90",
    "below_median",
)
# SS4 / AS-G2: the strata the informativeness gate reads.
TOP_STRATA = ("top_0.1pct", "top_1pct_below_0.1pct")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    sorted_values = values[order]
    start = 0
    for end in range(1, len(sorted_values) + 1):
        if end == len(sorted_values) or sorted_values[end] != sorted_values[start]:
            if end - start > 1:
                ranks[order[start:end]] = ranks[order[start:end]].mean()
            start = end
    return ranks / max(1, len(values) - 1)


def spearman(a: list[float], b: list[float]) -> float | None:
    """Rank correlation, implemented here to avoid a scipy dependency.

    SS1.5: this is how arms are compared. Raw score magnitudes are not comparable
    across arms; their ORDERING is.
    """
    if len(a) < 3:
        return None

    def ranked(values: list[float]) -> np.ndarray:
        arr = np.asarray(values, dtype=np.float64)
        order = np.argsort(arr, kind="stable")
        ranks = np.empty(len(arr), dtype=np.float64)
        ranks[order] = np.arange(len(arr), dtype=np.float64)
        sorted_values = arr[order]
        start = 0
        for end in range(1, len(sorted_values) + 1):
            if end == len(sorted_values) or sorted_values[end] != sorted_values[start]:
                if end - start > 1:
                    ranks[order[start:end]] = ranks[order[start:end]].mean()
                start = end
        return ranks

    ra, rb = ranked(a), ranked(b)
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> int:
    if not RAW.is_file():
        print(f"MISSING: {RAW} -- run as_run_arms.py first", file=sys.stderr)
        return 2
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print("ARTIFACT MISMATCH", file=sys.stderr)
        return 2

    from artistpath_api.graph_store import GraphStore

    graph = GraphStore.load(GRAPH)
    pop_pctl = percentile_ranks(np.asarray(graph.pop_raw, dtype=np.float64))
    id_of = {m: i for i, m in enumerate(graph.mbids)}

    payload = json.loads(RAW.read_text(encoding="utf-8"))
    if payload["artifact_sha256"] != EXPECT:
        print("RAW RECORDS were collected against a different artifact", file=sys.stderr)
        return 2
    records = payload["records"]

    # index: (mbid, arm) -> record
    by_key = {(r["mbid"], r["arm"]): r for r in records}
    arms = list(payload["arms"].keys())

    # --- AS-G1: arm integrity ------------------------------------------------
    integrity = {}
    for arm in arms:
        rows = [r for r in records if r["arm"] == arm]
        ok = sum(1 for r in rows if r.get("status") == 200 and "candidates" in r)
        share = ok / len(rows) if rows else 0.0
        integrity[arm] = {
            "requests": len(rows),
            "ok": ok,
            "share_ok": round(share, 6),
            "AS-G1_void": share < 0.95,
        }

    # --- per-record criterion values -----------------------------------------
    per: dict[tuple[str, str], dict[str, float]] = {}
    for record in records:
        if record.get("status") != 200 or "candidates" not in record:
            continue
        cand = record["candidates"]
        pctls, absent = [], 0
        for entry in cand:
            j = id_of.get(entry["mbid"])
            if j is None:
                absent += 1
            else:
                pctls.append(float(pop_pctl[j]))
        arr = np.array(pctls, dtype=np.float64)
        scores = [float(entry["score"]) for entry in cand]
        limit = ARM_LIMIT.get(record["arm"], DEFAULT_LIMIT)
        per[(record["mbid"], record["arm"])] = {
            "AS-C1": float((arr < 0.90).sum()) if arr.size else 0.0,
            "AS-C2": float(absent),
            "AS-C5": float((arr < 0.50).sum()) if arr.size else 0.0,
            "returned": float(len(cand)),
            "short_of_limit": 1.0 if len(cand) < limit else 0.0,
            "score_rank1": scores[0] if scores else float("nan"),
            "score_rank50": scores[49] if len(scores) >= 50 else float("nan"),
            "score_last": scores[-1] if scores else float("nan"),
        }

    # --- aggregate by arm x stratum ------------------------------------------
    stratum_of = {r["mbid"]: r["stratum"] for r in records}
    agg: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for arm in arms:
        for stratum in STRATA_ORDER:
            keys = [
                (m, arm)
                for m in {r["mbid"] for r in records if r["stratum"] == stratum}
                if (m, arm) in per
            ]
            if not keys:
                continue
            def mean(field: str) -> float:
                values = [per[k][field] for k in keys]
                values = [v for v in values if not np.isnan(v)]
                return round(float(np.mean(values)), 4) if values else float("nan")

            agg[arm][stratum] = {
                "artists": len(keys),
                "AS-C1_mean": mean("AS-C1"),
                "AS-C2_mean": mean("AS-C2"),
                "AS-C5_mean": mean("AS-C5"),
                "returned_mean": mean("returned"),
                "AS-C4_share_short_of_limit": mean("short_of_limit"),
                "AS-C4_score_rank1_mean": mean("score_rank1"),
                "AS-C4_score_rank50_mean": mean("score_rank50"),
                "AS-C4_score_last_mean": mean("score_last"),
                "AS-C1_is_lower_bound": mean("AS-C2") > 0,
            }

    # --- AS-C3: overlap with the baseline arm --------------------------------
    overlap: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for arm in arms:
        if arm == BASELINE:
            continue
        for stratum in STRATA_ORDER:
            shares, rhos = [], []
            for mbid in {r["mbid"] for r in records if r["stratum"] == stratum}:
                base = by_key.get((mbid, BASELINE))
                other = by_key.get((mbid, arm))
                if not base or not other:
                    continue
                if "candidates" not in base or "candidates" not in other:
                    continue
                base_scores = {c["mbid"]: float(c["score"]) for c in base["candidates"]}
                other_scores = {c["mbid"]: float(c["score"]) for c in other["candidates"]}
                shared = set(base_scores) & set(other_scores)
                union = set(base_scores) | set(other_scores)
                if union:
                    shares.append(len(shared) / len(union))
                if len(shared) >= 3:
                    ordered = sorted(shared)
                    rho = spearman(
                        [base_scores[m] for m in ordered],
                        [other_scores[m] for m in ordered],
                    )
                    if rho is not None:
                        rhos.append(rho)
            overlap[arm][stratum] = {
                "AS-C3_jaccard_mean": round(float(np.mean(shares)), 4) if shares else None,
                "AS-C3_spearman_on_shared_mean": round(float(np.mean(rhos)), 4) if rhos else None,
                "pairs": len(shares),
            }

    # --- AS-N noise floor, and the 3x decision rule --------------------------
    noise: dict[str, dict[str, float]] = defaultdict(dict)
    a_arm, f_arm = NOISE_PAIR
    for stratum in STRATA_ORDER:
        for field in ("AS-C1_mean", "AS-C2_mean", "AS-C5_mean"):
            va = agg.get(a_arm, {}).get(stratum, {}).get(field)
            vf = agg.get(f_arm, {}).get(stratum, {}).get(field)
            if va is None or vf is None:
                continue
            noise[stratum][field] = round(abs(float(va) - float(vf)), 4)

    def decisive(stratum: str, field: str, delta: float) -> tuple[bool, float]:
        """SS4: real only if > 3 x AS-N; absolute floor of 1.0 when AS-N == 0."""
        floor_value = noise.get(stratum, {}).get(field, 0.0)
        bar = 3.0 * floor_value
        if floor_value == 0.0:
            bar = max(bar, 1.0)
        return abs(delta) > bar, round(bar, 4)

    comparisons = []
    for arm in arms:
        if arm == BASELINE:
            continue
        for stratum in STRATA_ORDER:
            base = agg.get(BASELINE, {}).get(stratum, {})
            other = agg.get(arm, {}).get(stratum, {})
            if not base or not other:
                continue
            for field in ("AS-C1_mean", "AS-C5_mean", "AS-C2_mean"):
                delta = float(other[field]) - float(base[field])
                is_real, bar = decisive(stratum, field, delta)
                comparisons.append({
                    "arm": arm,
                    "vs": BASELINE,
                    "stratum": stratum,
                    "criterion": field,
                    "baseline": base[field],
                    "arm_value": other[field],
                    "delta": round(delta, 4),
                    "bar_3x_AS-N": bar,
                    "DECISIVE": is_real,
                })

    # --- AS-G2: design informativeness ---------------------------------------
    g2_rows = [
        c for c in comparisons
        if c["arm"] == "ALG-B" and c["criterion"] == "AS-C1_mean"
        and c["stratum"] in TOP_STRATA
    ]
    g2_pass = any(row["DECISIVE"] and row["delta"] > 0 for row in g2_rows)

    report = {
        "artifact_sha256": actual,
        "governing": "docs/superpowers/specs/2026-07-29-algorithm-selection-preregistration.md",
        "AS-G1_integrity": integrity,
        "AS-G2_informativeness": {
            "rows": g2_rows,
            "PASS": g2_pass,
            "reading": (
                "PASS -> proceed to the SS5 reads. FAIL -> AS-R2 (the null) fires; "
                "a larger sample is NOT the remedy (SS4)."
            ),
        },
        "AS-N_noise_floor": dict(noise),
        "by_arm_by_stratum": {a: dict(v) for a, v in agg.items()},
        "AS-C3_overlap_vs_baseline": {a: dict(v) for a, v in overlap.items()},
        "comparisons_vs_baseline": comparisons,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # --- console summary ------------------------------------------------------
    print("AS-G1 arm integrity")
    for arm, info in integrity.items():
        flag = "VOID" if info["AS-G1_void"] else "ok"
        print(f"  {arm}: {info['ok']}/{info['requests']} 200s ({info['share_ok']:.1%}) {flag}")

    print("\nAS-N noise floor (|ALG-A - ALG-F|)")
    for stratum in STRATA_ORDER:
        if stratum in noise:
            print(f"  {stratum:26s} {noise[stratum]}")

    print("\nAS-C1 mean sub-decile candidates (LOWER BOUND where AS-C2 > 0)")
    header = f"  {'stratum':26s}" + "".join(f"{a:>10s}" for a in arms)
    print(header)
    for stratum in STRATA_ORDER:
        cells = ""
        for arm in arms:
            value = agg.get(arm, {}).get(stratum, {}).get("AS-C1_mean")
            cells += f"{value:>10}" if value is not None else f"{'-':>10}"
        print(f"  {stratum:26s}{cells}")

    print("\nAS-C2 mean candidates absent from our artifact")
    print(header)
    for stratum in STRATA_ORDER:
        cells = ""
        for arm in arms:
            value = agg.get(arm, {}).get(stratum, {}).get("AS-C2_mean")
            cells += f"{value:>10}" if value is not None else f"{'-':>10}"
        print(f"  {stratum:26s}{cells}")

    print(f"\nAS-G2 informativeness gate: {'PASS' if g2_pass else 'FAIL -> AS-R2'}")
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
