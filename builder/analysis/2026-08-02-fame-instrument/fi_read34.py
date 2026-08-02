"""FAM-3 and FAM-4 reads, per the prereg's committed bars.

Run only AFTER fi_fam3_identity.json / fi_fam4_identity.json exist (FAM-AM1.4a:
identity is resolved before any ruler value is read — this script is the first
place those artists' ruler values are read). No CLI arguments by design.

FAM-3 (FAM-AM1.5): >= 8 of the 9 fixed names at fame_lb_pctl >= 0.99; every
miss reported with its value. Smoke test: a pass says nothing about the shared
population blind spot.

FAM-4 (FAM-AM1.4): among confirmed, non-excluded hand-read artists (FERG is
excluded by the prereg; NOFX appears once), all unordered pairs whose hand-read
Spotify monthly listeners differ by >= 10x; direction agreement >= 90%;
readability floor 10 pairs; failures traced per artist; plus Spearman >= 0.80
over all confirmed artists (FAM-AM1.4d).
"""

from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path

import numpy as np

from fi_stats import Frame, spearman  # same machinery as the committed figures

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / "fi_union_snapshot.json"
OLD_SNAPSHOT = HERE.parent / "2026-07-30-fame-proxy-coverage" / "fp_listenbrainz.json"
OUT = HERE / "fi_read34.json"


def parse_hand(s: str) -> int:
    """'15M' -> 15_000_000, '372k' -> 372_000, '1,234' -> 1234."""
    m = re.fullmatch(r"([\d,.]+)\s*([kKmM]?)", s.strip())
    if not m:
        raise ValueError(f"unparseable hand read: {s!r}")
    num = float(m.group(1).replace(",", ""))
    mult = {"": 1, "k": 1_000, "m": 1_000_000}[m.group(2).lower()]
    return int(num * mult)


def main() -> None:
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    adopted = set(json.loads(OLD_SNAPSHOT.read_text(encoding="utf-8")).keys())
    frame = Frame(np.array(sorted(v for m, v in snap.items()
                                  if m in adopted and v is not None), dtype=np.int64))

    fam3_rows = json.loads((HERE / "fi_fam3_identity.json").read_text(encoding="utf-8"))["rows"]
    fam4_rows = json.loads((HERE / "fi_fam4_identity.json").read_text(encoding="utf-8"))["rows"]

    fam3 = []
    for row in fam3_rows:
        v = snap[row["resolved_mbid"]]
        p = float(frame.pctl(np.array([v]))[0])
        fam3.append({"name": row["hand_read_name"], "fame_lb_raw": v,
                     "fame_lb_pctl": round(p, 6), "at_or_above_0_99": p >= 0.99})
    fam3_passes = sum(r["at_or_above_0_99"] for r in fam3)

    used, seen = [], set()
    for row in fam4_rows:
        if row["excluded_from_FAM_4_by_prereg"] or row["resolved_mbid"] in seen:
            continue
        seen.add(row["resolved_mbid"])
        used.append({"name": row["hand_read_name"],
                     "hand": parse_hand(row["hand_read_value_as_recorded"]),
                     "ruler": snap[row["resolved_mbid"]]})

    pairs = []
    for a, b in combinations(used, 2):
        hi, lo = (a, b) if a["hand"] >= b["hand"] else (b, a)
        if lo["hand"] <= 0 or hi["hand"] / lo["hand"] < 10:
            continue
        pairs.append({"higher_hand": hi["name"], "lower_hand": lo["name"],
                      "agrees": hi["ruler"] > lo["ruler"]})
    agree = sum(p["agrees"] for p in pairs)
    per_artist_failures: dict[str, int] = {}
    for p in pairs:
        if not p["agrees"]:
            for k in (p["higher_hand"], p["lower_hand"]):
                per_artist_failures[k] = per_artist_failures.get(k, 0) + 1

    rho = spearman(np.array([r["hand"] for r in used], dtype=np.int64),
                   np.array([r["ruler"] for r in used], dtype=np.int64))

    result = {
        "FAM_3": {
            "rows": fam3,
            "passes_at_0_99": fam3_passes,
            "bar": ">= 8 of 9",
            "read": "PASS" if fam3_passes >= 8 else "FAIL",
        },
        "FAM_4": {
            "confirmed_artists": len(used),
            "qualifying_pairs": len(pairs),
            "readability_floor_10_pairs": "READABLE" if len(pairs) >= 10 else "UNREADABLE",
            "agreement": None if not pairs else round(agree / len(pairs), 4),
            "bar_pairs": ">= 0.90 direction agreement",
            "read_pairs": "PASS" if pairs and agree / len(pairs) >= 0.90 else "FAIL",
            "failing_pairs": [p for p in pairs if not p["agrees"]],
            "per_artist_failures": per_artist_failures,
            "spearman_all_confirmed": round(float(rho), 4),
            "bar_spearman": ">= 0.80",
            "read_spearman": "PASS" if rho >= 0.80 else "FAIL",
            "artists": used,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
