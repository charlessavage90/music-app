"""Discharge two pre-registered checks that must run BEFORE any factorial arm.

Both are computed from already-committed inputs — the owner's blind labels
(`../2026-07-23-track2-fame-proxy/labels.json`) and the Wikipedia pageview counts
(`../2026-07-24-track2-fame-proxy-wikipedia/pageview_counts.json`). No new owner
time, no network.

1. **§2.2's permitted recalibration.** The pre-registration allows exactly one
   adjustment before arms run: if the owner's *know well* and *never heard of* bands
   sit closer than 1.0 log10 apart, every log10 threshold rescales by `band_gap / 1.0`.
   Reported under both defensible readings, because they differ a lot and the
   conservative one is close to the trigger.

2. **Coverage by label bucket** — the measurement A12 rests on. Under amendment A11
   an unmatched artist is *scored* at the fame floor rather than dropped, so match
   failure now correlates with the obscurity the sweep is trying to reach. C6's
   coverage gate was calibrated for the opposite encoding.

Fame is A11's: F(a) = log10(1 + English-Wikipedia annual pageviews), unmatched -> 0.
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = HERE.parent / "2026-07-23-track2-fame-proxy" / "labels.json"
COUNTS = HERE.parent / "2026-07-24-track2-fame-proxy-wikipedia" / "pageview_counts.json"

BUCKETS = ("know well", "heard of", "never heard of")
RECALIBRATION_TRIGGER = 1.0  # §2.2: fires only if the gap is BELOW this


def fame(pageviews: int) -> float:
    """A11's fame scale. An unmatched artist is scored 0 — the fame floor."""
    return math.log10(1.0 + pageviews)


def main() -> None:
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    counts = json.loads(COUNTS.read_text(encoding="utf-8"))
    rows = {r["query"]: r for r in counts["rows"]}

    # Every labelled artist must be present in the fetch, matched or not; a missing
    # row would mean the two committed files disagree about the sample.
    missing = sorted(set(labels) - set(rows))
    assert not missing, f"labelled artists absent from the pageview fetch: {missing}"

    scored: dict[str, list[dict]] = {b: [] for b in BUCKETS}
    for name, meta in labels.items():
        row = rows[name]
        matched = bool(row.get("matched"))
        pv = int(row["pageviews"]) if matched else 0
        scored[meta["bucket"]].append(
            {"name": name, "stratum": meta["stratum"], "matched": matched,
             "pageviews": pv, "F": fame(pv)}
        )

    def median_F(bucket: str, matched_only: bool) -> float:
        vals = [a["F"] for a in scored[bucket] if a["matched"] or not matched_only]
        return statistics.median(vals)

    # Two readings, because they differ by 5x and only one is conservative.
    #  - "as scored": the A11 encoding itself, absent artists at F=0. This is the
    #    currency C1's thresholds are actually applied in.
    #  - "matched only": drops the zeros, so the gap reflects separation among
    #    artists the proxy can genuinely see. Strictly smaller, hence conservative.
    gaps = {}
    for reading, matched_only in (("as_scored", False), ("matched_only", True)):
        gap = median_F("know well", matched_only) - median_F("never heard of", matched_only)
        gaps[reading] = {
            "know_well_median_F": median_F("know well", matched_only),
            "never_heard_median_F": median_F("never heard of", matched_only),
            "band_gap": gap,
            "recalibration_fires": gap < RECALIBRATION_TRIGGER,
        }

    coverage = {}
    for bucket in BUCKETS:
        arts = scored[bucket]
        m = sum(1 for a in arts if a["matched"])
        coverage[bucket] = {"n": len(arts), "matched": m, "rate": m / len(arts)}

    by_stratum: dict[str, dict] = {}
    for arts in scored.values():
        for a in arts:
            s = by_stratum.setdefault(a["stratum"], {"n": 0, "matched": 0})
            s["n"] += 1
            s["matched"] += int(a["matched"])
    for s in by_stratum.values():
        s["rate"] = s["matched"] / s["n"]

    out = {
        "inputs": {"labels": str(LABELS.name), "counts": str(COUNTS.name),
                   "n_labelled": len(labels)},
        "fame_scale": "log10(1 + english wikipedia annual pageviews); unmatched -> 0 (A11)",
        "recalibration_trigger": RECALIBRATION_TRIGGER,
        "band_gap": gaps,
        "coverage_by_bucket": coverage,
        "coverage_by_stratum": by_stratum,
        "unmatched": sorted(a["name"] for arts in scored.values() for a in arts
                            if not a["matched"]),
    }
    (HERE / "band_gap.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                        encoding="utf-8")

    print("§2.2 recalibration check")
    for reading, g in gaps.items():
        verdict = "FIRES" if g["recalibration_fires"] else "does not fire"
        print(f"  {reading:14s} band_gap = {g['band_gap']:.3f} log10  -> {verdict}")
    print("\ncoverage by label bucket (A12's basis)")
    for b, c in coverage.items():
        print(f"  {b:16s} {c['matched']:2d}/{c['n']:2d} = {c['rate']*100:.0f}%")
    print("\ncoverage by stratum")
    for s in sorted(by_stratum):
        c = by_stratum[s]
        print(f"  {s} {c['matched']:2d}/{c['n']:2d} = {c['rate']*100:.0f}%")


if __name__ == "__main__":
    main()
