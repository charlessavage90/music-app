"""FAM-6 read: the owner's tail hand reads against the ruler, per FAM-AM3.

Run only AFTER the filled checklist is committed (the hand reads are recorded
before any comparison is computed — WGLL bound three). This script is the first
place the sampled artists' ruler values are read beside the hand reads.

Confirmed row = a numeric monthly-listeners value and neither box ticked
(zero is a value: a confirmed page with no listeners). Bar: Spearman >= 0.70
over confirmed rows, n >= 12 (else UNREADABLE). Descriptive companion, no bar:
direction agreement on >= 10x pairs (rows with hand == 0 cannot form ratio
pairs and are excluded from the companion only, never from the Spearman).
"""

from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path

import numpy as np

from fi_stats import spearman

HERE = Path(__file__).resolve().parent
OUT = HERE / "fi_read6.json"


def parse_checklist() -> list[dict]:
    text = (HERE / "fi_tail_checklist.md").read_text(encoding="utf-8")
    sections = re.split(r"^### ", text, flags=re.M)[1:]
    rows = []
    for s in sections:
        header = s.splitlines()[0].strip()
        name = re.sub(r"^R?\d+\.\s*", "", header)
        m = re.search(r"\*\*monthly listeners:\*\*\s*([\d,]+)\s*$", s, flags=re.M)
        value = int(m.group(1).replace(",", "")) if m else None
        rows.append({
            "name": name,
            "hand": value,
            "no_identity": "[X] could not confirm identity" in s or "[x] could not confirm identity" in s,
            "no_page": "[X] no Spotify page" in s or "[x] no Spotify page" in s,
        })
    return rows


def main() -> None:
    snap = json.loads((HERE / "fi_union_snapshot.json").read_text(encoding="utf-8"))
    sample = json.loads((HERE / "fi_tail_sample.json").read_text(encoding="utf-8"))
    by_name = {r["name"]: r["mbid"] for r in sample["sample"]}

    rows = parse_checklist()
    confirmed, excluded = [], []
    for r in rows:
        if r["hand"] is not None and not r["no_identity"] and not r["no_page"]:
            confirmed.append({"name": r["name"], "hand": r["hand"],
                              "ruler": snap[by_name[r["name"]]]})
        else:
            reason = ("could_not_confirm_identity" if r["no_identity"]
                      else "no_spotify_page" if r["no_page"] else "left_blank")
            excluded.append({"name": r["name"], "reason": reason})

    n = len(confirmed)
    rho = float(spearman(np.array([r["hand"] for r in confirmed], dtype=np.int64),
                         np.array([r["ruler"] for r in confirmed], dtype=np.int64)))

    pairs = []
    for a, b in combinations(confirmed, 2):
        hi, lo = (a, b) if a["hand"] >= b["hand"] else (b, a)
        if lo["hand"] <= 0 or hi["hand"] / lo["hand"] < 10:
            continue
        pairs.append({"higher_hand": hi["name"], "lower_hand": lo["name"],
                      "agrees": hi["ruler"] > lo["ruler"]})
    agree = sum(p["agrees"] for p in pairs)

    result = {
        "confirmed_rows": n,
        "readability_floor_12": "READABLE" if n >= 12 else "UNREADABLE",
        "spearman": round(rho, 4),
        "bar": ">= 0.70",
        "read": ("UNREADABLE" if n < 12 else "PASS" if rho >= 0.70 else "FAIL"),
        "descriptive_pair_companion_no_bar": {
            "qualifying_pairs": len(pairs),
            "agreement": None if not pairs else round(agree / len(pairs), 4),
            "failing_pairs": [p for p in pairs if not p["agrees"]],
            "zero_hand_rows_excluded_from_pairs_only":
                [r["name"] for r in confirmed if r["hand"] == 0],
        },
        "excluded_rows": excluded,
        "rows": confirmed,
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
