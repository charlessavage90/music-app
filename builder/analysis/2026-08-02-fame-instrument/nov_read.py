"""NOV-1 read: the owner's known/unknown marks against fame_lb_pctl.

Run only after the marked checklist is committed. Reports the committed
criterion's state (class floor, AUC) and — because prior practice reports
descriptive figures beside an unreadable result — the descriptive AUC,
per-direction splits, and the full inversion list. No CLI arguments.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from fi_stats import Frame

HERE = Path(__file__).resolve().parent
OUT = HERE / "nov_read.json"


def main() -> None:
    snap = json.loads((HERE / "fi_union_snapshot.json").read_text(encoding="utf-8"))
    adopted = set(json.loads(
        (HERE.parent / "2026-07-30-fame-proxy-coverage" / "fp_listenbrainz.json")
        .read_text(encoding="utf-8")).keys())
    frame = Frame(np.array(sorted(v for m, v in snap.items()
                                  if m in adopted and v is not None), dtype=np.int64))
    corpus = json.loads((HERE / "fi_corpus.json").read_text(encoding="utf-8"))
    crows = corpus["rows"] if isinstance(corpus, dict) and "rows" in corpus else corpus
    by_name = {r["name"]: r for r in crows}

    text = (HERE / "fi_novelty_checklist.md").read_text(encoding="utf-8")
    rows = []
    for m in re.finditer(r"^\|\s*\d+\s*\|\s*(.+?)\s*\|\s*\[(.*?)\]\s*\|\s*\[(.*?)\]\s*\|",
                         text, flags=re.M):
        name, known_box, unknown_box = m.group(1), m.group(2), m.group(3)
        known = "x" in known_box.lower()
        unknown = "x" in unknown_box.lower()
        if known == unknown:
            raise SystemExit(f"row not marked exactly once: {name!r}")
        r = by_name[name]
        v = snap[r["mbid"]]
        p = float(frame.pctl(np.array([v]))[0])
        rows.append({"name": name, "region": r["region"], "known": known,
                     "fame_lb_raw": v, "fame_lb_pctl": round(p, 6)})

    known = [r for r in rows if r["known"]]
    unknown = [r for r in rows if not r["known"]]
    conc = ties = 0
    inversions = []
    for k in known:
        for u in unknown:
            if k["fame_lb_pctl"] > u["fame_lb_pctl"]:
                conc += 1
            elif k["fame_lb_pctl"] == u["fame_lb_pctl"]:
                ties += 1
            else:
                inversions.append({"known_below": k["name"],
                                   "unknown_above": u["name"]})
    pairs = len(known) * len(unknown)
    auc = (conc + 0.5 * ties) / pairs if pairs else None

    tail_unknown = sum(1 for r in rows if r["region"] == "tail" and not r["known"])
    famous_known = sum(1 for r in rows if r["region"] == "famous" and r["known"])

    result = {
        "class_counts": {"known": len(known), "unknown": len(unknown)},
        "readability_floor_5_per_class": "UNREADABLE" if min(len(known), len(unknown)) < 5 else "READABLE",
        "committed_read": "UNREADABLE" if min(len(known), len(unknown)) < 5 else None,
        "descriptive_auc_no_verdict": None if auc is None else round(auc, 4),
        "one_way_splits_descriptive": {
            "tail_rows_novel": f"{tail_unknown}/15",
            "famous_rows_known": f"{famous_known}/15",
        },
        "inversions": inversions,
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
