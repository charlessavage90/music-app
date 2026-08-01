"""`TAS-AM5b` (liveness), `TAS-AM5c` (null control), and `TAS-6`'s ROUTING half.

SUBSTRATE: THE ADOPTED ARTIFACT (`TAS-AM2`), same as `tas_route.py`. `TAS-6`'s two
halves measure the two architectures separately AND ARE NEVER COMBINED: the
selection half in `tas_guard.json` is on the pre-cap `ALG-E` capture, this one is
on the artifact, and `TAS-AM2` forbids reading one against the other.

TAS-6 IS REPORTED, NEVER A SUCCESS SIGNAL. Adverse at a >= 10% reduction. **The
SELECTION half is ALREADY ADVERSE and bars an adoption recommendation whatever
this file reports** -- that is §5's read and it is not softened by anything here.

`TAS-AM5b` IS NOT THE WITHDRAWN RED CHECK. The original -- shuffle labels, demand
large change -- was withdrawn as UNACHIEVABLE by `TAS-AM3`: randomising labels
destroys overlap rather than randomising it, so every correct null control must
report a small number. DO NOT "FIX" THIS TO MAKE A SHUFFLE FIRE.

`TAS-AM5b`'s reference is COMPUTED INDEPENDENTLY, not borrowed. `agreement_only_path`
is a plain Dijkstra whose only cost is `(1 - agreement)`; every production term is
dropped. That is what makes it an external reference rather than the instrument
checking itself, and it is why no threshold is needed: at a dominating weight
`find_path_coh` must reach that same optimum exactly.

TOTALS ARE COMPARED, NOT NODE SEQUENCES. At a dominating weight the remaining terms
act purely as a tie-break among equally coherent paths, so requiring an identical
sequence would fail on ties that are not defects.

`tas_guard.py` IS NOT MODIFIED. It holds the committed selection-side record, and
re-running it to add routing output would rewrite `tas_guard.json`.

Run from `builder/` (~25-35 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_route_guard.py
"""

from __future__ import annotations

import argparse
import heapq
import json
from pathlib import Path

from tas_common import HERE, fame_frame, resolved_agreement
from tas_guard import is_adverse, permuted_labels_among_labelled
from tas_pairs import draw_pairs
from tas_route import (
    CLASSES,
    WEIGHT_MULTIPLES,
    _neutral_and_neighbours,
    agreement_cost_of,
    find_path_coh,
    load_adopted,
)
from tas_tags import label_sets

OUT = HERE / "tas_route_guard.json"
DOMINATING_MULTIPLE = 1e6
SUB_DECILE = 0.10
NULL_SEED = 909
TOLERANCE = 1e-9


def agreement_only_path(store, source, target, labels):
    """Dijkstra with cost = (1 - agreement) ALONE. `TAS-AM5b`'s reference.

    Every production term is dropped, so this optimum is computed WITHOUT
    find_path_coh -- which is what makes it an external reference.
    """
    if source == target:
        return [source], 0.0
    dist = {source: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        neighbours, u_set, neutral = _neutral_and_neighbours(store, u, labels)
        for v, _sim in neighbours:
            nd = d + (
                1.0
                - resolved_agreement(u_set, labels.get(store.mbids[v], set()), neutral)
            )
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None, float("inf")
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1], dist[target]


def sub_decile_interior_count(paths, mbids, frame_pctl) -> int:
    """Interior artists below the tenth fame percentile, endpoints EXCLUDED.

    Endpoints are excluded deliberately: an obscure endpoint is the user's own
    choice, not something the router supplied. TAS-6 asks what routing delivers.

    An artist ABSENT from the fame frame is not counted. Defaulting it to 0.0
    would silently class every unframed node obscure -- the defect tas_select.py
    records against the capture/artifact node-set delta.
    """
    total = 0
    for path in paths:
        for node in path[1:-1]:
            pctl = frame_pctl.get(mbids[node])
            if pctl is not None and pctl < SUB_DECILE:
                total += 1
    return total


def _grid(store, cfg, labels, pairs, index):
    """Per-class change rates and sub-decile interiors at every weight."""
    base = {
        (a, b): find_path_coh(store, index[a], index[b], cfg, labels, 0.0)
        for a, b, _ in pairs
    }
    out: dict[str, dict] = {}
    for mult in WEIGHT_MULTIPLES:
        w_coh = mult * cfg.w_sim
        by_class: dict[str, list[bool]] = {c: [] for c in CLASSES}
        paths = []
        for a, b, cls in pairs:
            arm = find_path_coh(store, index[a], index[b], cfg, labels, w_coh)
            by_class[cls].append(base[(a, b)] != arm)
            if arm:
                paths.append(arm)
        changed = sum(sum(v) for v in by_class.values())
        n = sum(len(v) for v in by_class.values())
        out[str(mult)] = {
            "changed_share_by_class": {
                c: round(sum(v) / len(v), 4) if v else None for c, v in by_class.items()
            },
            "changed_share_pooled_FOR_THE_NULL_RATIO_ONLY": round(changed / n, 4),
            "sub_decile_interiors": sub_decile_interior_count(
                paths, store.mbids, fame_frame()
            ),
        }
        print(f"  w_coh={mult}x: {out[str(mult)]['changed_share_by_class']}", flush=True)
    return out, base


def main() -> None:
    from artistpath_api.config import ApiConfig

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cfg = ApiConfig()
    store = load_adopted()
    labels = label_sets()
    frame = fame_frame()
    index = {m: i for i, m in enumerate(store.mbids)}
    pairs = [p for p in draw_pairs() if p[0] in index and p[1] in index]

    # ---- TAS-AM5b: liveness against an independently computed reference ----
    dominating = DOMINATING_MULTIPLE * cfg.w_sim
    failures = []
    for a, b, _cls in pairs:
        s, t = index[a], index[b]
        ref_path, ref_cost = agreement_only_path(store, s, t, labels)
        arm = find_path_coh(store, s, t, cfg, labels, dominating)
        if arm is None or ref_path is None:
            failures.append([a, b, "no path"])
            continue
        got = agreement_cost_of(arm, store, labels)
        if abs(got - ref_cost) > TOLERANCE:
            failures.append([a, b, round(got - ref_cost, 12)])
    liveness = {
        "dominating_w_coh_multiple_of_w_sim": DOMINATING_MULTIPLE,
        "pairs_checked": len(pairs),
        "failures": failures,
        "passes": not failures,
        "compares": "TOTAL (1 - agreement) along the path, NOT the node sequence -- "
                    "tie-safe and threshold-free (TAS-AM5b).",
    }
    print(f"TAS-AM5b liveness: {liveness['passes']} "
          f"({len(failures)} failures / {len(pairs)})", flush=True)
    if not liveness["passes"]:
        raise SystemExit(
            "TAS-AM5b FAILED -- the coherence term is not reaching the cost function. "
            "Every TAS-5 figure is void. Do not proceed."
        )

    # ---- the real grid, then TAS-AM5c's null ----
    print("real frame:", flush=True)
    real, real_base = _grid(store, cfg, labels, pairs, index)
    print("null frame (labels permuted among labelled artists only):", flush=True)
    null_labels = permuted_labels_among_labelled(labels, NULL_SEED)
    null, null_base = _grid(store, cfg, null_labels, pairs, index)

    # At w_coh = 0 the labels cannot matter, so the two baselines must be identical.
    # Free, and it catches a whole class of harness bug.
    baselines_agree = real_base == null_base
    if not baselines_agree:
        raise SystemExit(
            "The real and null baselines differ at w_coh = 0, where labels cannot "
            "affect the cost. The harness is wrong; nothing here counts."
        )

    baseline_sub_decile = real["0.0"]["sub_decile_interiors"]
    tas6 = {
        "baseline_sub_decile_interiors": baseline_sub_decile,
        "by_weight": {
            mult: {
                "sub_decile_interiors": cell["sub_decile_interiors"],
                "change_vs_baseline": (
                    round((cell["sub_decile_interiors"] - baseline_sub_decile)
                          / baseline_sub_decile, 4) if baseline_sub_decile else None
                ),
                "adverse": is_adverse(baseline_sub_decile, cell["sub_decile_interiors"]),
            }
            for mult, cell in real.items() if mult != "0.0"
        },
        "note": "ROUTING half only. The SELECTION half is in tas_guard.json, on the "
                "ALG-E capture, and TAS-AM2 forbids comparing the two. The selection "
                "half is ADVERSE and bars adoption regardless of this.",
    }

    ratios = {
        mult: (
            round(null[mult]["changed_share_pooled_FOR_THE_NULL_RATIO_ONLY"]
                  / real[mult]["changed_share_pooled_FOR_THE_NULL_RATIO_ONLY"], 4)
            if real[mult]["changed_share_pooled_FOR_THE_NULL_RATIO_ONLY"] else None
        )
        for mult in real if mult != "0.0"
    }
    null_control = {
        "seed": NULL_SEED,
        "null_over_real_ratio_by_weight": ratios,
        "reaches_half_at_any_weight": any(r is not None and r >= 0.5
                                          for r in ratios.values()),
        "read": "A SMALL null is the CORRECT result, not a failure. If the ratio reaches "
                "0.5 at any weight, TAS-5's change cannot be attributed to genre "
                "structure and every figure carries that caveat. Below 0.5: report the "
                "ratio and NOTHING MORE -- no claim about tags is licensed by this "
                "control (TAS-AM5c).",
    }

    Path(args.out).write_text(json.dumps({
        "substrate": {"note": "ADOPTED ARTIFACT per TAS-AM2. Never compare against a "
                              "capture-side figure."},
        "baselines_agree_at_zero_weight": baselines_agree,
        "tas_am5b_liveness": liveness,
        "tas_am5c_null_control": null_control,
        "tas6_routing_half": tas6,
        "real_grid": real,
        "null_grid": null,
    }, indent=1), encoding="utf-8")
    print("\n" + json.dumps({"tas6_routing": tas6["by_weight"],
                             "null_ratios": ratios,
                             "null_reaches_half": null_control[
                                 "reaches_half_at_any_weight"]}, indent=1))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
