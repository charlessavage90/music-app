"""RCS §4 -- score candidates W and D against the hand corpus. Figures only.

WHAT THIS DELIBERATELY DOES NOT CONTAIN
  No pass, no fail, no read, no verdict field. RCS §5 splits the work: the
  executor produces figures, the controller reads them against the bars fixed
  in §4 before any value existed. A `read: "FAIL"` written here would be the
  executor doing the controller's job, and it would be doing it from inside the
  session that chose the fetch procedure.

  For the same reason readability is emitted as a COUNT beside the floor
  constant, never as READABLE/UNREADABLE -- §4 says a region short of the floor
  is "reported with its null count, never as a pass or fail".

THE FIGURES, PER CANDIDATE PER REGION
  * non-null rows (and every null with its recorded reason)
  * Spearman against the hand reads over the non-null rows, using the SAME
    spearman as FAM-4/FAM-6 (imported from fi_stats, not reimplemented) so
    this probe's numbers and the LB reference numbers are the same statistic
  * the descriptive >= 10x pair companion, no bar, exactly as fi_read6.py
    forms it: hand-0 rows are excluded from pairs ONLY, never from Spearman
  * for D, both POOLED and TIER-1-ONLY variants (RCS §2: "every figure is
    reported both pooled and tier-1-only")

REFERENCE FIGURES ARE CITED, NOT RESTATED
  The LB comparators are read out of fi_read34.json / fi_read6.json at run
  time and asserted against the values RCS §3 committed. They are labelled as
  reference and carry their source path, so nothing here becomes a second
  home for a figure that already has one.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/rcs_score.py
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fi_stats import spearman  # noqa: E402

OUT = HERE / "rcs_results.json"
READABILITY_FLOOR = 12
RATIO = 10.0

# Committed in RCS §3 before any candidate value existed. Asserted, not trusted.
LB_FAMOUS_SPEARMAN = 0.4915
LB_TAIL_SPEARMAN = 0.4552


def pair_companion(rows: list[dict], key: str) -> dict:
    """>= 10x direction agreement, formed exactly as fi_read6.py forms it."""
    pairs = []
    for a, b in combinations(rows, 2):
        hi, lo = (a, b) if a["hand_value"] >= b["hand_value"] else (b, a)
        if lo["hand_value"] <= 0 or hi["hand_value"] / lo["hand_value"] < RATIO:
            continue
        pairs.append({"higher_hand": hi["name"], "lower_hand": lo["name"],
                      "agrees": hi[key] > lo[key]})
    agree = sum(p["agrees"] for p in pairs)
    return {
        "qualifying_pairs": len(pairs),
        "agreement": None if not pairs else round(agree / len(pairs), 4),
        "failing_pairs": [p for p in pairs if not p["agrees"]],
        "zero_hand_rows_excluded_from_pairs_only":
            [r["name"] for r in rows if r["hand_value"] == 0],
    }


def score(rows: list[dict], key: str) -> dict:
    """One region, one candidate, one row subset. Figures only."""
    scored = [r for r in rows if r[key] is not None]
    nulls = [{"name": r["name"], "reason": r.get("null_reason")}
             for r in rows if r[key] is None]
    out = {
        "rows_in_region": len(rows),
        "non_null_rows": len(scored),
        "null_rows": len(nulls),
        "readability_floor_rows": READABILITY_FLOOR,
        "nulls": nulls,
        "spearman_vs_hand": None,
        "spearman_n": len(scored),
        "descriptive_pair_companion_no_bar": pair_companion(scored, key),
        "scored_rows": [{"name": r["name"], "hand": r["hand_value"], "candidate": r[key],
                         **({"tier": r["tier"]} if "tier" in r else {})}
                        for r in sorted(scored, key=lambda r: -r["hand_value"])],
    }
    if len(scored) >= 2:
        rho = spearman(
            np.array([r["hand_value"] for r in scored], dtype=np.float64),
            np.array([float(r[key]) for r in scored], dtype=np.float64),
        )
        out["spearman_vs_hand"] = None if rho != rho else round(float(rho), 4)
    return out


def references() -> dict:
    read34 = json.loads((HERE / "fi_read34.json").read_text(encoding="utf-8"))
    read6 = json.loads((HERE / "fi_read6.json").read_text(encoding="utf-8"))
    fam = read34["FAM_4"]
    if (fam["spearman_all_confirmed"], read6["spearman"]) != (LB_FAMOUS_SPEARMAN, LB_TAIL_SPEARMAN):
        raise SystemExit("LB reference figures moved since RCS §3 committed them")
    return {
        "_note": "REFERENCE ONLY -- the ruler that failed FAM. Cited from its own "
                 "output files, never recomputed here.",
        "famous": {
            "spearman_vs_hand": fam["spearman_all_confirmed"],
            "descriptive_pair_agreement": fam["agreement"],
            "qualifying_pairs": fam["qualifying_pairs"],
            "source": "builder/analysis/2026-08-02-fame-instrument/fi_read34.json (FAM_4)",
        },
        "tail": {
            "spearman_vs_hand": read6["spearman"],
            "descriptive_pair_agreement":
                read6["descriptive_pair_companion_no_bar"]["agreement"],
            "qualifying_pairs":
                read6["descriptive_pair_companion_no_bar"]["qualifying_pairs"],
            "source": "builder/analysis/2026-08-02-fame-instrument/fi_read6.json",
        },
    }


def main() -> None:
    corpus = json.loads((HERE / "fi_corpus.json").read_text(encoding="utf-8"))
    wiki = json.loads((HERE / "rcs_wikipedia.json").read_text(encoding="utf-8"))["rows"]
    deez = json.loads((HERE / "rcs_deezer.json").read_text(encoding="utf-8"))["rows"]

    corpus_mbids = {r["mbid"] for r in corpus["rows"]}
    for name, rows in (("W", wiki), ("D", deez)):
        if {r["mbid"] for r in rows} != corpus_mbids or len(rows) != 30:
            raise SystemExit(f"candidate {name} does not cover the corpus exactly")

    results = {
        "governing_document":
            "docs/superpowers/specs/2026-08-02-ruler-candidate-shootout-preregistration.md",
        "section": "RCS §4 -- figures. The bars live in the pre-registration; "
                   "this file contains no read of them.",
        "corpus": {"file": "fi_corpus.json", **corpus["checks"]},
        "candidates": {},
        "listenbrainz_reference": references(),
    }

    for region in ("famous", "tail"):
        rows = [r for r in wiki if r["region"] == region]
        results["candidates"].setdefault("W", {"description": wiki_desc()})[region] = \
            score(rows, "W")

    for region in ("famous", "tail"):
        rows = [r for r in deez if r["region"] == region]
        block = results["candidates"].setdefault("D", {"description": deezer_desc()})
        block[region] = {
            "pooled": score(rows, "D"),
            "tier_1_only": score([r for r in rows if r["tier"] == 1], "D"),
            "tier_counts": {
                "tier_1_rows": sum(1 for r in rows if r["tier"] == 1),
                "tier_2_rows": sum(1 for r in rows if r["tier"] == 2),
                "tier_2_accepted": sum(1 for r in rows if r["tier"] == 2 and r["D"] is not None),
            },
            "tier_2_acceptances": [
                {"name": r["name"], "deezer_id": r["deezer_id"], "candidate": r["D"],
                 "evidence": r["tier2_evidence"]}
                for r in rows if r["tier"] == 2 and r["D"] is not None
            ],
        }

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    report(results)
    print(f"\n-> {OUT.name}")


def wiki_desc() -> str:
    return ("W -- MBID-keyed EN Wikipedia pageviews (Wikidata P434 -> EN sitelink -> "
            "pageviews over fp_fame_mbid's window). Values are raw pageview counts; "
            "log10 is monotone so it cannot move a rank correlation.")


def deezer_desc() -> str:
    return ("D -- Deezer nb_fan. Tier 1 = id recorded in MusicBrainz; tier 2 = "
            "name-resolved and corroborated by a shared release title.")


def report(results: dict) -> None:
    ref = results["listenbrainz_reference"]
    print("LB reference (cited): famous spearman "
          f"{ref['famous']['spearman_vs_hand']}, tail {ref['tail']['spearman_vs_hand']}\n")
    for region in ("famous", "tail"):
        print(f"--- {region} ---")
        w = results["candidates"]["W"][region]
        print(f"  W          non-null {w['non_null_rows']}/{w['rows_in_region']}  "
              f"spearman {w['spearman_vs_hand']}  "
              f"pairs {w['descriptive_pair_companion_no_bar']['agreement']} "
              f"over {w['descriptive_pair_companion_no_bar']['qualifying_pairs']}")
        for label in ("pooled", "tier_1_only"):
            d = results["candidates"]["D"][region][label]
            print(f"  D {label:11} non-null {d['non_null_rows']}/{d['rows_in_region']}  "
                  f"spearman {d['spearman_vs_hand']}  "
                  f"pairs {d['descriptive_pair_companion_no_bar']['agreement']} "
                  f"over {d['descriptive_pair_companion_no_bar']['qualifying_pairs']}")


if __name__ == "__main__":
    main()
