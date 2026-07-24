"""P4 step 1c: join the owner's blind verdicts to artists and strata -> labels.json.

The verdicts below are keyed by **position in `blind_order.json`**, which is how they were
presented (names only, shuffled). This script maps them back through that order to artist
names and strata, so the mapping is auditable rather than hand-transcribed. Rerunning it
reproduces `labels.json` exactly.

Collected 2026-07-23, blind (no fan count shown; none existed on the machine at the time).
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Verdicts in blind-order position (1..29). Verbatim from the owner.
VERDICTS = {
    1: "never heard of",   2: "heard of",         3: "never heard of",
    4: "never heard of",   5: "never heard of",   6: "never heard of",
    7: "never heard of",   8: "heard of",         9: "never heard of",
    10: "never heard of",  11: "know well",       12: "never heard of",
    13: "never heard of",  14: "never heard of",  15: "know well",
    16: "know well",       17: "know well",       18: "never heard of",
    19: "know well",       20: "know well",       21: "never heard of",
    22: "heard of",        23: "never heard of",  24: "heard of",
    25: "heard of",        26: "know well",       27: "never heard of",
    28: "heard of",        29: "never heard of",
}

BUCKETS = {"know well", "heard of", "never heard of"}


def main():
    order = json.loads((HERE / "blind_order.json").read_text(encoding="utf-8"))["order"]
    sample = json.loads((HERE / "sample.json").read_text(encoding="utf-8"))
    stratum_of = {n: s for s, members in sample["strata"].items() for n in members}

    if set(VERDICTS) != set(range(1, len(order) + 1)):
        raise SystemExit(f"expected verdicts 1..{len(order)}; got {sorted(VERDICTS)}")
    bad = {v for v in VERDICTS.values() if v not in BUCKETS}
    if bad:
        raise SystemExit(f"unknown bucket(s): {bad}")

    labels = {}
    for pos, name in enumerate(order, 1):
        labels[name] = {"bucket": VERDICTS[pos], "stratum": stratum_of[name], "blind_pos": pos}

    (HERE / "labels.json").write_text(
        json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # A quick, human-readable cross-tab, printed only — not part of scoring.
    print("bucket counts:")
    for b in ["know well", "heard of", "never heard of"]:
        names = sorted(n for n, v in labels.items() if v["bucket"] == b)
        print(f"  {b:<16} {len(names):2d}  {', '.join(names)}")
    print("\nby stratum:")
    for s in ["S1", "S2", "S3", "S4"]:
        row = {b: 0 for b in BUCKETS}
        for v in labels.values():
            if v["stratum"] == s:
                row[v["bucket"]] += 1
        print(f"  {s}: know={row['know well']} heard={row['heard of']} never={row['never heard of']}")
    print(f"\n{len(labels)} labels -> labels.json")


if __name__ == "__main__":
    main()
