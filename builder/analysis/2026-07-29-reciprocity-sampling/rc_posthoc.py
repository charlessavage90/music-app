"""RC post-hoc reads. NOT pre-registered -- everything here is labelled as such.

`rc_score.py` and its `rc_scores.json` are the pre-registered read and are left
untouched, so the record shows what the committed design actually produced. This file
holds three things found only after seeing that output. Governing document and its
amendment `RC-A2`:
`docs/superpowers/specs/2026-07-29-reciprocity-sampling-preregistration.md`.

**`RC-P1` -- a denominator defect in the pre-registered scorer, and it biased toward
the null.** `rc_score.py` skips a seed with no usable sampled candidate (`usable == 0`).
Ten of forty below-median seeds returned **zero candidates** under `ALG-B`, so they were
dropped -- removing the maximally stranded artists from the very arm that strands them.
An artist with no candidates has no edges and is dropped by `largest_component`: its
degree is 0, not missing. This recomputes `RC-C1` and `RC-C2` with those seeds included
at `d_hat = 0`, on a denominator fixed to every below-median seed whose production list
was collected. It moves the result AWAY from the null, which is exactly when to show
both numbers rather than the better one.

**`RC-P2` -- the famous side fails acceptance by clauses `RC-C3` did not pre-register.**
`RC-C3` fixed the median against `famous_median_degree_floor`. `PRODUCTION_ACCEPTANCE`
also carries `famous_min_degree_floor = 8` over the top 25 by popularity, and 24
`canonical_names` that must be present in the largest component. Four top-0.1% seeds
reciprocate nothing at all under `ALG-B`, and one is **R.E.M.**, a canonical name. This
reports what those clauses would do. Pre-registering only the median was a gap in the
design, recorded rather than papered over.

**`RC-P3` -- the mechanism, and it is `CS-P0f` at work.** `ALG-B` offers famous artists
more obscure candidates (that is `AS-C1`, its whole appeal). Mutual k-NN then needs the
obscure end to rank the famous artist inside ITS top-50 -- and `ALG-B` gives obscure
artists a very short list. So the edges `ALG-B` adds may be exactly the ones the cap
deletes. This splits each famous seed's sampled candidates by whether the candidate is
in the adopted artifact at all, and reports reciprocation for each side. **Suggestive,
not decisive: it consumes no pre-registered read and would need its own design to
settle.**

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-reciprocity-sampling/rc_posthoc.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "src"))

RECORDS = HERE / "rc_raw_records.json"
SCORES = HERE / "rc_scores.json"
GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
OUT = HERE / "rc_posthoc.json"

K = 50
D_HAT_STRANDED_BELOW = 2.0
# PRODUCTION_ACCEPTANCE clauses RC-C3 did not pre-register.
FAMOUS_MIN_DEGREE_FLOOR = 8
FAMOUS_SAMPLE = 25


def top_k(candidates: list[dict], k: int = K) -> list[str]:
    ranked = sorted(candidates, key=lambda c: (-float(c["score"]), c["mbid"]))
    return [c["mbid"] for c in ranked[:k]]


def main() -> int:
    from artistpath_builder.acceptance import PRODUCTION_ACCEPTANCE

    data = json.loads(RECORDS.read_text(encoding="utf-8"))
    pre = json.loads(SCORES.read_text(encoding="utf-8"))
    seeds = data["seeds"]
    lists = data["candidate_lists"]

    as_records = json.loads(
        (ROOT / "builder" / "analysis" / "2026-07-29-cap-selection-sim"
         / "as_raw_records.json").read_text(encoding="utf-8")
    )
    seed_lists: dict[str, dict[str, list[dict]]] = {"RC-ARM-P": {}, "RC-ARM-B": {}}
    for entry in as_records["records"]:
        arm = {"ALG-E": "RC-ARM-P", "ALG-B": "RC-ARM-B"}.get(str(entry["arm"]))
        if arm and entry.get("status") == 200 and "candidates" in entry:
            seed_lists[arm][str(entry["mbid"])] = entry["candidates"]

    def d_hat(arm: str, mbid: str) -> float | None:
        """Estimated degree. 0.0 when the arm returned no candidates at all --
        no candidates means no edges, which is a degree of zero, not a gap."""
        own = seed_lists[arm].get(mbid)
        if own is None:
            return None
        pool = top_k(own)
        if not pool:
            return 0.0
        drawn = [c for c in seeds[mbid]["arms"][arm]["sampled"] if c in pool]
        usable = recip = 0
        for v in drawn:
            rec = lists[arm].get(v)
            if not rec or rec.get("status") != 200 or "candidates" not in rec:
                continue
            usable += 1
            if mbid in top_k(rec["candidates"]):
                recip += 1
        if not usable:
            return 0.0 if not drawn else None
        return len(pool) * (recip / usable)

    # --- RC-P1: corrected RC-C1 / RC-C2 on a fixed denominator --------------
    below = sorted(
        m for m, s in seeds.items()
        if s["stratum"] == "below_median" and m in seed_lists["RC-ARM-P"]
    )
    rows = []
    for mbid in below:
        p, b = d_hat("RC-ARM-P", mbid), d_hat("RC-ARM-B", mbid)
        if p is None or b is None:
            continue
        rows.append({"mbid": mbid, "name": seeds[mbid]["name"], "prod": p, "algb": b,
                     "algb_returned_nothing": not top_k(
                         seed_lists["RC-ARM-B"].get(mbid, []))})
    share_p = sum(1 for r in rows if r["prod"] < D_HAT_STRANDED_BELOW) / len(rows)
    share_b = sum(1 for r in rows if r["algb"] < D_HAT_STRANDED_BELOW) / len(rows)
    med_p = statistics.median(r["prod"] for r in rows)
    med_b = statistics.median(r["algb"] for r in rows)

    rc_p1 = {
        "seeds": len(rows),
        "seeds_algb_returned_nothing": sum(1 for r in rows if r["algb_returned_nothing"]),
        "pre_registered_seeds": pre["bands"]["below_median"]["seeds_in_both_arms"],
        "share_below_2_production": round(share_p, 4),
        "share_below_2_algb": round(share_b, 4),
        "delta_points": round(100 * (share_b - share_p), 2),
        "median_d_hat_production": med_p,
        "median_d_hat_algb": med_b,
        "ratio": round(med_b / med_p, 4) if med_p else None,
        "pre_registered_delta_points": pre["criteria"]["RC-C1"]["delta_points"],
        "pre_registered_ratio": pre["criteria"]["RC-C2"]["ratio"],
    }
    print("RC-P1 corrected, denominator", len(rows),
          f"(pre-registered read used {rc_p1['pre_registered_seeds']})", flush=True)
    print(f"  share with fewer than 2 connections: "
          f"{share_p*100:.1f}% -> {share_b*100:.1f}% "
          f"({rc_p1['delta_points']:+.1f} points; pre-registered read said "
          f"{rc_p1['pre_registered_delta_points']:+.1f})", flush=True)
    print(f"  median connections: {med_p} -> {med_b} (ratio {rc_p1['ratio']})",
          flush=True)

    # --- RC-P2: the acceptance clauses RC-C3 did not cover ------------------
    famous = sorted(
        (m for m, s in seeds.items() if s["stratum"] == "top_0.1pct"),
        key=lambda m: -float(seeds[m]["own_pctl"]),
    )
    collapsed = []
    for mbid in famous:
        b = d_hat("RC-ARM-B", mbid)
        if b is not None and b < D_HAT_STRANDED_BELOW:
            collapsed.append({
                "name": seeds[mbid]["name"],
                "d_hat_algb": b,
                "d_hat_production": d_hat("RC-ARM-P", mbid),
                "is_canonical": seeds[mbid]["name"] in PRODUCTION_ACCEPTANCE.canonical_names,
            })
    top_sample = [d_hat("RC-ARM-B", m) for m in famous[:FAMOUS_SAMPLE]]
    top_sample = [v for v in top_sample if v is not None]
    rc_p2 = {
        "collapsed_top_0.1pct": collapsed,
        "canonical_names_collapsed": [c["name"] for c in collapsed if c["is_canonical"]],
        "min_d_hat_over_top_25_of_sample": min(top_sample) if top_sample else None,
        "famous_min_degree_floor": FAMOUS_MIN_DEGREE_FLOOR,
        "would_fail_min_degree_clause": bool(
            top_sample and min(top_sample) < FAMOUS_MIN_DEGREE_FLOOR
        ),
    }
    print(f"\nRC-P2: {len(collapsed)} of {len(famous)} top-0.1% seeds reciprocate "
          f"nothing under ALG-B", flush=True)
    for c in collapsed:
        mark = "  <-- CANONICAL, acceptance requires it in the graph" if c["is_canonical"] else ""
        print(f"   {c['name']:24s} production {c['d_hat_production']:5.1f} -> 0.0{mark}",
              flush=True)

    # --- RC-P3: mechanism -- who refuses whom -------------------------------
    from artistpath_api.graph_store import GraphStore

    graph = GraphStore.load(GRAPH)
    in_artifact = set(graph.mbids)
    split = {
        "candidate_in_adopted_artifact": {"sampled": 0, "reciprocated": 0},
        "candidate_absent_from_artifact": {"sampled": 0, "reciprocated": 0},
    }
    for mbid in famous:
        own = seed_lists["RC-ARM-B"].get(mbid)
        if not own:
            continue
        pool = top_k(own)
        for v in seeds[mbid]["arms"]["RC-ARM-B"]["sampled"]:
            if v not in pool:
                continue
            rec = lists["RC-ARM-B"].get(v)
            if not rec or rec.get("status") != 200 or "candidates" not in rec:
                continue
            key = ("candidate_in_adopted_artifact" if v in in_artifact
                   else "candidate_absent_from_artifact")
            split[key]["sampled"] += 1
            if mbid in top_k(rec["candidates"]):
                split[key]["reciprocated"] += 1
    for key, row in split.items():
        row["rate"] = (
            round(row["reciprocated"] / row["sampled"], 4) if row["sampled"] else None
        )
    print("\nRC-P3 (suggestive only): for the most famous artists, does the candidate "
          "point back?", flush=True)
    for key, row in split.items():
        print(f"   {key:36s} sampled {row['sampled']:4d}  points back {row['rate']}",
              flush=True)

    OUT.write_text(
        json.dumps({"rc_p1": rc_p1, "rc_p2": rc_p2, "rc_p3": split,
                    "below_median_rows": rows}, indent=2),
        encoding="utf-8",
    )
    print(f"\nwrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
