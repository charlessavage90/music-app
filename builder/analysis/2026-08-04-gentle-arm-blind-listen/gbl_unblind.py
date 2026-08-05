"""Unblind AFTER all verdicts are on disk: the §5 tally and the §7
ear-tracking table. Mechanical only -- the write-up is a session's job."""
from __future__ import annotations

import json
import statistics
import sys

from gbl_common import DEPTHS, in_dir, sealed_path

DEEP = ("10", "20")
MARGIN = 5           # spec §5: the 3-of-10 bar scaled to 16 rows, rounded up
BRANCH_SENTENCES = {  # spec §5, quoted
    "G_better": "The rebuilt app digs, and the journeys still sound like journeys.",
    "V0_better": "Today's app sounds better despite not digging.",
    "no_detectable_difference":
        "My ear cannot tell them apart where the numbers could.",
}


class RunIncomplete(SystemExit):
    pass


def tally(rows: dict, mapping: dict) -> dict:
    missing = [f"{k}:d{d}" for k in mapping for d in map(str, DEPTHS)
               if rows.get(k, {}).get(d) is None]
    if missing:
        raise RunIncomplete(
            f"spec §5 run state unmet -- no read exists. Missing: {missing}")
    picks = {"G": 0, "V0": 0}
    for k, m in mapping.items():
        for d in DEEP:
            p = rows[k][d]
            if p in m:                      # "L"/"R" -> arm; "none" skipped
                picks[m[p]] += 1
    margin = abs(picks["G"] - picks["V0"])
    if margin >= MARGIN:
        branch = "G_better" if picks["G"] > picks["V0"] else "V0_better"
    else:
        branch = "no_detectable_difference"
    d0 = {"G": 0, "V0": 0}
    for k, m in mapping.items():
        p = rows[k]["0"]
        if p in m:
            d0[m[p]] += 1
    return {"deep_rows": len(mapping) * len(DEEP), "clear_picks": picks,
            "margin": margin, "branch": branch,
            "branch_sentence": BRANCH_SENTENCES[branch],
            "d0_anchor_picks_excluded_from_tally": d0}


def ear_tracking(rows: dict, sealed: dict) -> dict:
    """§7: for each deep row with a clear pick, did the picked side also win
    each hidden metric? Fame compares measured interiors only.

    `fame_rows` is reported separately from `rows` deliberately. The censoring
    blind spot (findings §3) is live: a journey that digs deeper delivers more
    artists the ruler cannot read, and those interiors are dropped rather than
    scored -- treating an unreadable artist as maximally obscure would
    manufacture the very trend this table exists to check. Where one side has no
    measured interior at all, the row is UNREADABLE on fame, not favourable, and
    is excluded from fame_rows so the fraction has an honest denominator.
    """
    counts = {"fame_lower": 0, "fame_rows": 0, "payload_higher": 0,
              "top1pct_degree_frac_lower": 0, "length_longer": 0, "rows": 0}
    mapping = sealed["mapping"]
    for k, m in mapping.items():
        for d in DEEP:
            p = rows[k][d]
            if p not in m:
                continue
            counts["rows"] += 1
            picked, other = m[p], m[{"L": "R", "R": "L"}[p]]
            a = sealed["arms"][picked]["pairs"][k][d]["metrics"]
            b = sealed["arms"][other]["pairs"][k][d]["metrics"]

            def mean_fame(mm):
                vals = [f for f in mm["fame_pctl_interior"] if f is not None]
                return statistics.mean(vals) if vals else None

            fa, fb = mean_fame(a), mean_fame(b)
            if fa is not None and fb is not None:
                counts["fame_rows"] += 1
                if fa < fb:
                    counts["fame_lower"] += 1
            if a["payload"] > b["payload"]:
                counts["payload_higher"] += 1
            if a["top1pct_degree_frac"] < b["top1pct_degree_frac"]:
                counts["top1pct_degree_frac_lower"] += 1
            if a["length"] > b["length"]:
                counts["length_longer"] += 1
    return counts


def main() -> int:
    verdicts = json.loads(in_dir("gbl_verdicts.json").read_text("utf-8"))
    sealed = json.loads(sealed_path("gbl_sealed.json").read_text("utf-8"))
    out = tally(verdicts["rows"], sealed["mapping"])
    out["ear_tracking"] = ear_tracking(verdicts["rows"], sealed)
    out["mapping_unsealed"] = sealed["mapping"]
    out["claims"] = verdicts["claims"]
    in_dir("gbl_result.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"branch: {out['branch']} (margin {out['margin']} of "
          f"{out['deep_rows']} deep rows); wrote gbl_result.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
