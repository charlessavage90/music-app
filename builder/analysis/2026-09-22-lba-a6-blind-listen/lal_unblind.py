"""Unblind AFTER every answer is on disk: `LBA-AM6-7`'s tally and `LAL-R1`–`LAL-R4`, plus
`LBA-AM6-8`'s descriptive reads, which decide nothing. Adapted by copy from listen 2's `lbl_unblind.py`.

**Run by the fresh WRITE-UP session only** (`LBA-AM6-5`) — not the runner, not the preparation
session. Mechanical; the findings note is that session's.

    cd <tree>/builder && UV_LINK_MODE=copy uv run python analysis/2026-09-22-lba-a6-blind-listen/lal_unblind.py
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import AXES, DEPTHS, MARGIN, STRENGTHS, UNDERPOWERED_CLIP_ROWS, in_dir, sealed_path  # noqa: E402
from lal_page import VERDICTS, row_complete  # noqa: E402

# LBA-AM6-7's plain sentences, quoted; [axis] is substituted.
SENTENCES = {
    "LAL-R1": "Journeys on the new map are better on [axis], and no worse on the other.",
    "LAL-R2": "My ear cannot tell the new map from today's on these pairs.",
    "LAL-R3": "Today's map gives better journeys on [axis].",
    "LAL-R4": "Too many rows were lost to clip problems to read this listen.",
}
REQ41 = ("REQ-41: 'no difference' in unfamiliar territory is uninformative, not evidence of equivalence. "
         "LAL-R2 is not 'the new map is as good as today's'.")
OTHER = {"L": "R", "R": "L"}


class RunIncomplete(SystemExit):
    pass


def axis_read(rows: dict, mapping: dict, question: str) -> dict:
    """One axis over all pairs x depths. Reads the pick and the clip box ONLY."""
    picks = {"challenger": 0, "incumbent": 0}
    lost = 0
    for key, m in mapping.items():
        for d in map(str, DEPTHS):
            entry = rows[key][d]
            if entry[question] in m:
                picks[m[entry[question]]] += 1
            elif entry.get("clip_blocked"):
                lost += 1
    margin = picks["challenger"] - picks["incumbent"]
    if margin >= MARGIN:
        verdict = "candidate_better"
    elif -margin >= MARGIN:
        verdict = "served_better"
    elif lost >= UNDERPOWERED_CLIP_ROWS:
        verdict = "underpowered"
    else:
        verdict = "no_detectable_difference"
    return {"rows": len(mapping) * len(DEPTHS), "clear_picks": picks, "margin_toward_candidate": margin,
            "clip_blocked_no_preference_rows": lost, "bar": MARGIN, "verdict": verdict}


def listen_read(axes: dict[str, dict]) -> tuple[str, list[str]]:
    """`LAL-R1`–`R4` from the two axis verdicts. A split is FAIL (`LBA-AM6-7`)."""
    worse = [n for n, a in axes.items() if a["verdict"] == "served_better"]
    better = [n for n, a in axes.items() if a["verdict"] == "candidate_better"]
    if worse:
        return "LAL-R3", worse
    if better:
        return "LAL-R1", better
    if any(a["verdict"] == "underpowered" for a in axes.values()):
        return "LAL-R4", []
    return "LAL-R2", []


def tally(state: dict, mapping: dict) -> dict:
    """The primary read. Refuses before the full run state (`LBA-AM6-7`); counts rows, nothing else."""
    missing = [f"{k}:d{d}" for k in mapping for d in DEPTHS
               if not row_complete(state["rows"].get(k, {}).get(str(d)))]
    missing += [f"{k}:pair" for k in mapping if k not in state["pairs"]]
    if missing:
        raise RunIncomplete(f"LBA-AM6-7 run state unmet — no read exists. Missing: {missing}")
    axes = {AXES[q]: axis_read(state["rows"], mapping, q) for q in AXES}
    read, named = listen_read(axes)
    return {"axes": axes, "read": read, "axes_named": named}


def sentence(read: str, named: list[str]) -> str:
    return SENTENCES[read].replace("[axis]", " and ".join(named) if named else "[axis]")


def descriptive(state: dict, mapping: dict) -> dict:
    """`LBA-AM6-8`. DECIDES NOTHING: no threshold, no branch reads any of it."""
    out: dict = {"decides": "nothing — LAL-R1 to LAL-R4 read the row tally only"}
    ident = {str(d): {"no": 0, "yes_right": 0, "yes_wrong": 0} for d in DEPTHS}
    strength = {axis: {s: {"challenger": 0, "incumbent": 0} for s in STRENGTHS} for axis in AXES.values()}
    known = {"by_depth": {str(d): 0 for d in DEPTHS},
             "on_no_preference_rows": {axis: 0 for axis in AXES.values()}}
    tradeoff = 0
    for k, m in mapping.items():
        for d in map(str, DEPTHS):
            e = state["rows"][k][d]
            if e["identify"] == "no":
                ident[d]["no"] += 1
            else:
                said = "L" if e["identify"] == "yes_left" else "R"
                ident[d]["yes_right" if m[said] == "challenger" else "yes_wrong"] += 1
            for q, axis in AXES.items():
                if e[q] in m and e.get(f"{q}_strength") in STRENGTHS:
                    strength[axis][e[f"{q}_strength"]][m[e[q]]] += 1
                if e[q] == "none" and e["known_everyone"]:
                    known["on_no_preference_rows"][axis] += 1
            known["by_depth"][d] += bool(e["known_everyone"])
            tradeoff += e["q1"] in m and e["q2"] in m and e["q1"] != e["q2"]
    out["LAL-Q4_identification"] = ident
    out["LAL-Q3_strength"] = strength
    out["LAL-K_known_everyone"] = known
    out["computed_tradeoff_rows"] = {"rows": tradeoff, "of": len(mapping) * len(DEPTHS)}
    return out


def ear_tracking(state: dict, sealed: dict) -> dict:
    """For each clear pick: did the picked side also win each sealed metric? Fame on the candidate's
    ruler; a row where either side has no measured interior is unreadable on fame. Decides nothing."""
    out = {}
    mapping = sealed["mapping"]

    def mean_fame(mm):
        vals = [f for f in mm["fame_pctl_interior_candidate_ruler"] if f is not None]
        return statistics.mean(vals) if vals else None

    for q, axis in AXES.items():
        c = {"rows": 0, "fame_rows": 0, "fame_lower": 0, "non_hub_interior_higher": 0,
             "top1pct_degree_frac_lower": 0, "length_longer": 0, "more_outside_served_map": 0}
        for key, m in mapping.items():
            for d in map(str, DEPTHS):
                pick = state["rows"][key][d][q]
                if pick not in m:
                    continue
                c["rows"] += 1
                a = sealed["journeys"][m[pick]][key][d]["metrics"]
                b = sealed["journeys"][m[OTHER[pick]]][key][d]["metrics"]
                fa, fb = mean_fame(a), mean_fame(b)
                if fa is not None and fb is not None:
                    c["fame_rows"] += 1
                    c["fame_lower"] += fa < fb
                c["non_hub_interior_higher"] += a["non_hub_interior"] > b["non_hub_interior"]
                c["top1pct_degree_frac_lower"] += a["top1pct_degree_frac"] < b["top1pct_degree_frac"]
                c["length_longer"] += a["length"] > b["length"]
                c["more_outside_served_map"] += a["presented_not_in_served_map"] > b["presented_not_in_served_map"]
        out[axis] = c
    return out


def clip_coverage(sealed: dict, clips: dict) -> dict:
    """Per MAP: presented card slots and those with no clip. Available only after the unblind."""
    out = {}
    for role, journeys in sealed["journeys"].items():
        slots = [mb for key in journeys for d in journeys[key] for mb in journeys[key][d]["path_mbids"]]
        out[role] = {"slots": len(slots), "no_clip": sum(1 for mb in slots if not clips.get(mb))}
    return out


def main() -> int:
    state = json.loads(in_dir(VERDICTS).read_text("utf-8"))
    sealed = json.loads(sealed_path("lal_sealed.json").read_text("utf-8"))
    clips_file = sealed_path("lal_clips.json")
    out = tally(state, sealed["mapping"])
    out["sentence"] = sentence(out["read"], out["axes_named"])
    if out["read"] == "LAL-R2":
        out["REQ-41"] = REQ41
    out["descriptive_only"] = descriptive(state, sealed["mapping"])
    out["descriptive_only"]["ear_tracking"] = ear_tracking(state, sealed)
    if clips_file.exists():
        out["descriptive_only"]["clip_coverage_by_map"] = clip_coverage(sealed, json.loads(clips_file.read_text("utf-8")))
    out["mapping_unsealed"] = sealed["mapping"]
    out["maps"] = sealed["maps"]
    out["substitutions"] = sealed["substitutions"]
    in_dir("lal_result.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"read: {out['read']}; wrote lal_result.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
