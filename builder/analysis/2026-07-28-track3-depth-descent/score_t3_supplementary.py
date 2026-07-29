"""Held-out confirmation and the all-famous anchor table. Neither is a criterion.

Two things `score_t3.py` does not produce, both requested by the owner's consultant
review:

**1. Held-out confirmation (4 pairs).** The pre-registration fixes an 8/4 split but
reads no criterion off the held-out half, so `score_t3.py` scores analysis only —
and REPORT.md wrongly said held-out was "reported separately". This computes the same
statistics on the held-out pairs so the analysis result can be checked out-of-sample.
**It gates nothing**: it was not pre-registered as a gate, and turning a confirmation
set into a gate after seeing the analysis result is exactly the move pre-registration
exists to prevent.

**2. The all-famous anchor table (4 pairs), DESCRIPTIVE ONLY.** The anchors are walked
for DD-G2 and excluded from every criterion, because DD-P1 proved they have no
all-obscure route at any price (execution log §2). They are tabulated here because the
owner's original complaint was about famous pairs and the measured wins are all on
mid-band pairs — so "what did the device do to a famous journey" is the first question
anyone asks. **No criterion is evaluated on them and none may be.**

Deliberately a separate module from `score_t3.py`: the pre-registered scorer stays
exactly as it was when it produced the committed result.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/score_t3_supplementary.py
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

C1_DEPTHS = (10, 15, 20)
C1_THRESHOLD, C1_MIN_NEG_FRAC, C2_THRESHOLD, C5_PCTL = -1.0, 0.75, 0.5, 0.90


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext

    store = GraphStore.load(GRAPH)
    pctl = MirrorContext.build(store).pctl

    paths = json.loads((HERE / "t3_paths.json").read_text(encoding="utf-8"))
    fame = json.loads((HERE / "t3_fame.json").read_text(encoding="utf-8"))
    assert paths["artifact_sha256"] == digest
    F, mbids, splits, arms = fame["fame"], paths["node_mbids"], paths["splits"], paths["arms"]

    held = [p for p in paths["pairs"] if splits[p] == "held_out"]
    anchors = list(paths["unscored_anchor_pairs"])

    def cell(arm, pair, d):
        return paths["paths"][arm][pair][str(d)]

    def iF(path):
        return [F[mbids[str(n)]] for n in path[1:-1]]

    def stats_over(pairs: list[str]) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for arm in arms:
            deltas, dlens, payload = [], [], []
            for pair in pairs:
                for d in C1_DEPTHS:
                    pa, pp = cell(arm, pair, d), cell("P", pair, d)
                    if not pa or not pp:
                        continue
                    deltas.append(statistics.mean(iF(pa)) - statistics.mean(iF(pp)))
                    dlens.append((len(pa) - 2) - (len(pp) - 2))
                    payload.append(sum(1 for n in pa[1:-1] if pctl[n] < C5_PCTL))

            def pooled(d):
                return [f for pair in pairs if cell(arm, pair, d) for f in iF(cell(arm, pair, d))]
            f5, f20 = pooled(5), pooled(20)
            c2 = (statistics.median(f5) - statistics.median(f20)) if f5 and f20 else None
            out[arm] = {
                "n_cells": len(deltas),
                "c1_mean": statistics.mean(deltas) if deltas else None,
                "c1_neg_frac": (sum(1 for x in deltas if x < 0) / len(deltas)) if deltas else None,
                "c2_drop": c2,
                "c5_mean": statistics.mean(payload) if payload else None,
                "c6_mean_len_delta": statistics.mean(dlens) if dlens else None,
            }
            out[arm]["c1_meets"] = bool(
                deltas and out[arm]["c1_mean"] <= C1_THRESHOLD
                and out[arm]["c1_neg_frac"] >= C1_MIN_NEG_FRAC)
            out[arm]["c2_meets"] = bool(c2 is not None and c2 >= C2_THRESHOLD)
        return out

    hold, anch = stats_over(held), stats_over(anchors)

    def show(title: str, table: dict, pairs: list[str], note: str) -> None:
        print(f"\n=== {title} ({len(pairs)} pairs) ===")
        for p in pairs:
            print(f"    {p}")
        print(f"  {note}\n")
        print(f"  {'arm':<8}{'cells':>6}{'C1':>9}{'neg%':>7}{'C2':>8}"
              f"{'C5/cell':>9}{'len vs P':>10}")
        for arm in arms:
            r = table[arm]
            print(f"  {arm:<8}{r['n_cells']:>6}{r['c1_mean']:>9.3f}"
                  f"{100 * r['c1_neg_frac']:>6.0f}%{r['c2_drop']:>8.3f}"
                  f"{r['c5_mean']:>9.2f}{r['c6_mean_len_delta']:>+10.2f}")

    show("HELD-OUT CONFIRMATION", hold, held,
         "Confirmatory only. Not pre-registered as a gate; gates nothing.")
    for arm in arms:
        if arm == "P":
            continue
        h = hold[arm]
        print(f"    {arm}: analysis-set thresholds would be "
              f"{'MET' if h['c1_meets'] and h['c2_meets'] else 'NOT met'} here "
              f"(C1 {'y' if h['c1_meets'] else 'n'}, C2 {'y' if h['c2_meets'] else 'n'})")

    show("ALL-FAMOUS ANCHORS — DESCRIPTIVE ONLY, NO CRITERION", anch, anchors,
         "Excluded from every criterion: DD-P1 proved no all-obscure route exists "
         "for these at any price. Do not read a pass/fail here.")

    (HERE / "t3_supplementary.json").write_text(
        json.dumps({"artifact_sha256": digest,
                    "held_out": {"pairs": held, "gates_nothing": True, "results": hold},
                    "anchors": {"pairs": anchors, "descriptive_only": True,
                                "results": anch}}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print(f"\nwrote {HERE / 't3_supplementary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
