"""POST-HOC exploration — NOT part of the pre-registered §5 protocol.

Run after the pageviews proxy fired the coverage falsifier, to test one idea the owner
asked about: is Wikipedia *absence* itself a usable obscurity signal? i.e. does
"no English-Wikipedia article" track "the owner has never heard of them"?

Nothing here scores an arm or changes the pre-registered verdict. It reinterprets the
committed data (labels.json + pageview_counts.json) under the encoding "absent = fame
floor (0)" and reports how well that separates the buckets. Exploratory, labelled as such.
"""

import json
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEEZER = HERE.parent / "2026-07-23-track2-fame-proxy"
NEVER, HEARD, KNOW = "never heard of", "heard of", "know well"


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    wins = sum((1.0 if a > b else 0.5 if a == b else 0.0) for a, b in product(pos, neg))
    return wins / (len(pos) * len(neg))


def main():
    labels = json.loads((DEEZER / "labels.json").read_text(encoding="utf-8"))
    pv = json.loads((HERE / "pageview_counts.json").read_text(encoding="utf-8"))
    views = {r["query"]: r["pageviews"] for r in pv["rows"]}

    # Encoding under test: absent -> 0 (rock-bottom fame). Present -> its pageviews.
    rows = []
    for name, lab in labels.items():
        v = views.get(name)
        rows.append({"name": name, "bucket": lab["bucket"], "stratum": lab["stratum"],
                     "matched": v is not None, "views_floor0": v if v is not None else 0})

    # 1) Does absence predict "never heard of"?
    absent = [r for r in rows if not r["matched"]]
    present = [r for r in rows if r["matched"]]
    print("=== Absence vs owner label ===")
    print(f"  absent : {len(absent)}  buckets={_counts(absent)}")
    print(f"  present: {len(present)}  buckets={_counts(present)}")
    p_never_given_absent = sum(r["bucket"] == NEVER for r in absent) / len(absent)
    print(f"  P(never heard of | absent) = {p_never_given_absent:.2f}")

    # 2) With absent=0, can the proxy separate 'known at all' from 'never heard of'?
    #    This is the C1/C2-relevant question: detecting the obscure tail.
    known_at_all = [r["views_floor0"] for r in rows if r["bucket"] in (HEARD, KNOW)
                    and r["stratum"] != "S4"]
    never = [r["views_floor0"] for r in rows if r["bucket"] == NEVER and r["stratum"] != "S4"]
    a_detect = auc(known_at_all, never)
    print("\n=== Obscurity detection (absent=0), S4 excluded ===")
    print(f"  AUC(known-at-all > never-heard) = {a_detect:.3f}  "
          f"(n={len(known_at_all)} vs {len(never)})")

    # 3) For reference, the same detection AUC restricted to MATCHED only (no absence signal)
    km = [r["views_floor0"] for r in present if r["bucket"] in (HEARD, KNOW) and r["stratum"] != "S4"]
    nm = [r["views_floor0"] for r in present if r["bucket"] == NEVER and r["stratum"] != "S4"]
    print(f"  (matched-only, for contrast)     = {auc(km, nm):.3f}  (n={len(km)} vs {len(nm)})")

    # 4) Option B burden: how many artists would need owner labels if we only
    #    hand-label what Wikipedia misses.
    print("\n=== Option B (hybrid) labelling burden, this sample ===")
    print(f"  Wikipedia covers {len(present)}/{len(rows)} = {len(present)/len(rows):.0%}; "
          f"owner would label the {len(absent)} misses ({len(absent)/len(rows):.0%}).")


def _counts(rs):
    from collections import Counter
    return dict(Counter(r["bucket"] for r in rs))


if __name__ == "__main__":
    main()
