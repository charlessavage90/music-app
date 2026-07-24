"""P8b probe 4: how much can C2 actually discriminate on this pair set?

The arm-scorer README flags that production P scores C2 exactly at the threshold
minimum. A criterion the BASELINE already passes cannot supply evidence that a
candidate is better -- it can only fail a candidate that is worse. This probe
quantifies the headroom, using ONLY arm P (whose paths are already in the record; the
brief permits P and nothing else).

Reported per analysis pair:
  * the minimum interior fame at d15 and d20 (the depths C2 reads)
  * the margin to B_unk in log10 fame units, signed
  * whether the pair's C2 hit (if any) is carried by a MATCHED artist or by an
    UNMATCHED one scored at the fame floor -- A12's residual, since a pass carried by
    absence rests entirely on the absence assumption

Also reports the interior-count denominators so the "fewer-but-obscurer" payload guard
C4 can be read against a real baseline.

Run from `api/` (score.py's b_unk import chain needs artistpath_api on the path):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-24-track2-p8b-harness-review/probe_c2_headroom.py
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCORER = HERE.parent / "2026-07-24-track2-arm-scorer"
PROXY = HERE.parent / "2026-07-24-track2-fame-proxy-wikipedia"
sys.path.insert(0, str(SCORER))

C2_DEPTHS = (15, 20)
C1_DEPTHS = (10, 15, 20)


def main() -> int:
    doc = json.loads((HERE / "paths_P.json").read_text(encoding="utf-8"))
    famedoc = json.loads((HERE / "fame_P.json").read_text(encoding="utf-8"))
    F = famedoc["fame"]
    rows = famedoc["rows"]
    b_raw = int(json.loads((PROXY / "score.json").read_text(encoding="utf-8"))
                ["b_unk"]["threshold"])
    B = math.log10(1.0 + b_raw)

    names = doc["node_names"]
    held = set(doc["held_out_pairs"])
    analysis = [p for p in doc["pairs"] if p not in held]
    P = doc["paths"]["P"]

    def interiors(path):
        return [names[str(n)] for n in path[1:-1]] if path else []

    per_pair = []
    for pair in analysis:
        cell = {}
        best = None
        for d in C2_DEPTHS:
            ints = interiors(P[pair][str(d)])
            vals = [(F[n], n) for n in ints]
            lo = min(vals) if vals else None
            cell[f"d{d}_min_F"] = None if lo is None else round(lo[0], 4)
            cell[f"d{d}_min_artist"] = None if lo is None else lo[1]
            cell[f"d{d}_n_interiors"] = len(ints)
            if lo is not None and (best is None or lo[0] < best[0]):
                best = lo
        margin = None if best is None else round(best[0] - B, 4)
        carrier = None
        if best is not None and best[0] < B:
            carrier = "unmatched (F=0, absence assumption)" if not rows[best[1]].get(
                "matched") else "matched"
        per_pair.append({
            "pair": pair, **cell,
            "min_F_over_C2_depths": None if best is None else round(best[0], 4),
            "min_artist": None if best is None else best[1],
            "margin_to_B_unk": margin,
            "reaches": bool(best is not None and best[0] < B),
            "hit_carried_by": carrier,
        })

    reaching = [r for r in per_pair if r["reaches"]]
    failing = [r for r in per_pair if not r["reaches"]]
    near = [r for r in failing if r["margin_to_B_unk"] is not None
            and r["margin_to_B_unk"] <= 0.15]

    out = {
        "artifact_sha256": doc["artifact_sha256"],
        "arm": "P (production) only -- no experimental arm run",
        "B_unk_fame_units": round(B, 4),
        "B_unk_pageviews": b_raw,
        "C2_threshold_pairs": 4,
        "per_pair": per_pair,
        "summary": {
            "P_reaches": len(reaching),
            "of": len(analysis),
            "reaching_pairs": [r["pair"] for r in reaching],
            "reaching_carried_by_unmatched":
                [r["pair"] for r in reaching
                 if r["hit_carried_by"] and r["hit_carried_by"].startswith("unmatched")],
            "failing_pairs_margin_above_B_unk":
                {r["pair"]: r["margin_to_B_unk"] for r in failing},
            "failing_pairs_within_0.15_of_B_unk": [r["pair"] for r in near],
            "median_margin_of_failing_pairs":
                (statistics.median([r["margin_to_B_unk"] for r in failing])
                 if failing else None),
        },
        "read": (
            "C2 is a FLOOR that production already clears. Its evidential value is "
            "one-sided: it can fail a candidate that reaches FEWER pairs than P, and it "
            "cannot distinguish a candidate that reaches more. §3's Attack 1 (the famous "
            "ladder) is therefore closed by C2 only against a ladder that also loses P's "
            "existing reach; a ladder that leaves P's 4 reaching pairs alone passes C2 "
            "unchanged. On this pair set the discriminating load sits on C1 and C3."),
    }
    (HERE / "probe_c2_headroom.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
