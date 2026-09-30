"""Unblind AFTER every answer is on disk: `DRP-AM7-7`'s tally and `DSL-R1`–`DSL-R4`; `DSL-P`, the
fame-proxy read (`DRP-AM7-8`); `DSL-E`, the weak-step position read (`DRP-AM7-9`); and `DRP-AM7-10`'s
descriptive reads, which decide nothing. Adapted by copy from `LAL-`'s `lal_unblind.py`.

**Run by the fresh WRITE-UP session only** (`DRP-AM7-5`) — not the runner, not the preparation
session, not the designing session. Mechanical; the findings note is that session's.

The three reads are INDEPENDENT by construction and by test: the verdict reads picks and the clip box
only; `DSL-P` reads `DSL-M` marks only; `DSL-E` reads `DSL-W` marks only.

    cd api && UV_LINK_MODE=copy uv run python ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_unblind.py
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dsl_common import (AXES, DEPTHS, DSL_E_MIN_MARKS, DSL_E_RATIO, DSL_P_MIN_N, FAME_BANDS, MARGIN,  # noqa: E402
                        ROLES, STRENGTHS, TOKENS, UNDERPOWERED_CLIP_ROWS, in_dir, sealed_path)
from dsl_page import VERDICTS, row_complete  # noqa: E402

# DRP-AM7-7's plain sentences, quoted; [axis] is substituted.
SENTENCES = {
    "DSL-R1": "After several presses, journeys with the ceiling and the extra connections are better on [axis], "
              "and no worse on the other.",
    "DSL-R2": "After several presses, my ear cannot tell the candidate from today's app on these pairs.",
    "DSL-R3": "After several presses, today's app gives better journeys on [axis].",
    "DSL-R4": "Too many rows were lost to clip problems to read this listen.",
}
REQ41 = ("REQ-41: 'no difference' in unfamiliar territory is uninformative, not evidence of equivalence. "
         "DSL-R2 is not 'the candidate is as good as today's', and not 'safe to ship'.")
OTHER = {"L": "R", "R": "L"}
# DRP-AM7-8 and -9's outcome sentences, quoted.
P_SENTENCES = {
    "fires": "Most of the less-famous artists the candidate put in the middle were ones I already know.",
    "does_not_fire": "Most of the less-famous artists the candidate put in the middle were new to me.",
    "unreadable": "Too few artists to say.",
}
E_SENTENCES = {
    "fires": "When the candidate's journey breaks, it is mostly on the step off an endpoint.",
    "does_not_fire": "The candidate's weak steps are not mostly at the ends.",
    "unreadable": "Too few weak steps were marked to say where the candidate breaks.",
}


class RunIncomplete(SystemExit):
    pass


def require_full_run(state: dict, mapping: dict) -> None:
    missing = [f"{k}:d{d}" for k in mapping for d in DEPTHS
               if not row_complete(state["rows"].get(k, {}).get(str(d)))]
    if missing:
        raise RunIncomplete(f"DRP-AM7-7 run state unmet — no read exists. Missing: {missing}")


# ---- the verdict: picks and the clip box ONLY --------------------------------------------------
def axis_read(rows: dict, mapping: dict, question: str) -> dict:
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
        verdict = "today_better"
    elif lost >= UNDERPOWERED_CLIP_ROWS:
        verdict = "underpowered"
    else:
        verdict = "no_detectable_difference"
    return {"rows": len(mapping) * len(DEPTHS), "clear_picks": picks, "margin_toward_candidate": margin,
            "clip_blocked_no_preference_rows": lost, "bar": MARGIN, "verdict": verdict}


def listen_read(axes: dict[str, dict]) -> tuple[str, list[str]]:
    """`DSL-R1`–`R4` from the two axis verdicts. A split is FAIL (`DRP-AM7-7`)."""
    worse = [n for n, a in axes.items() if a["verdict"] == "today_better"]
    better = [n for n, a in axes.items() if a["verdict"] == "candidate_better"]
    if worse:
        return "DSL-R3", worse
    if better:
        return "DSL-R1", better
    if any(a["verdict"] == "underpowered" for a in axes.values()):
        return "DSL-R4", []
    return "DSL-R2", []


def tally(state: dict, mapping: dict) -> dict:
    require_full_run(state, mapping)
    axes = {AXES[q]: axis_read(state["rows"], mapping, q) for q in AXES}
    read, named = listen_read(axes)
    return {"axes": axes, "read": read, "axes_named": named}


def sentence(read: str, named: list[str]) -> str:
    return SENTENCES[read].replace("[axis]", " and ".join(named) if named else "[axis]")


# ---- DSL-P: DSL-M marks ONLY -------------------------------------------------------------------
def _interior(sealed: dict, role: str, key: str, d: str) -> list[str]:
    return sealed["journeys"][role][key][d]["path_mbids"][1:-1]


def _band(f) -> str:
    if f is None:
        return "unmeasured"
    for lo, hi in FAME_BANDS:
        if lo <= f < hi:
            return f"[{lo:.2f}, {hi:.2f})"
    return "below 0.60" if f < FAME_BANDS[0][0] else "0.99 and above"


def proxy_read(state: dict, sealed: dict) -> dict:
    """`DRP-AM7-8`. Population: distinct candidate-side middle artists on no incumbent-side card of the
    same row. Known: marked on ANY card where the artist appears."""
    mapping = sealed["mapping"]
    require_full_run(state, mapping)
    fame = sealed["fame_by_mbid"]
    only = {"challenger": set(), "incumbent": set()}
    cards: dict[str, list[bool]] = {}   # mbid -> marked? per middle card it appears on
    for key, m in mapping.items():
        for d in map(str, DEPTHS):
            ch, inc = _interior(sealed, "challenger", key, d), _interior(sealed, "incumbent", key, d)
            only["challenger"] |= set(ch) - set(inc)
            only["incumbent"] |= set(inc) - set(ch)
            entry = state["rows"][key][d]
            for tok in TOKENS:
                marked = set(entry["known"][tok])
                for mb in _interior(sealed, m[tok], key, d):
                    cards.setdefault(mb, []).append(mb in marked)
    known_any = {mb for mb, v in cards.items() if any(v)}
    mixed = sum(1 for v in cards.values() if any(v) and not all(v))

    def bands(pop: set) -> dict:
        out: dict = {}
        for mb in pop:
            b = out.setdefault(_band(fame.get(mb)), {"n": 0, "known": 0})
            b["n"] += 1
            b["known"] += mb in known_any
        return dict(sorted(out.items()))

    n = len(only["challenger"])
    k = len(only["challenger"] & known_any)
    readable = n >= DSL_P_MIN_N
    fires = readable and k >= n // 2 + 1
    outcome = "unreadable" if not readable else ("fires" if fires else "does_not_fire")
    return {"population": "distinct candidate-side middle artists on no incumbent-side card of the same row",
            "n": n, "known": k, "threshold": n // 2 + 1, "min_n": DSL_P_MIN_N, "readable": readable,
            "fires": fires, "outcome": outcome, "sentence": P_SENTENCES[outcome],
            "licenses": "the owner's rule: a proxy fix goes first, with the lattice re-run. A session does not start it.",
            "artists_marked_on_some_cards_not_others": mixed,
            "by_band_candidate_only": bands(only["challenger"]),
            "by_band_incumbent_only_reference": bands(only["incumbent"])}


# ---- DSL-E: DSL-W marks ONLY -------------------------------------------------------------------
def step_read(state: dict, sealed: dict) -> dict:
    """`DRP-AM7-9`. End step = a step with an endpoint on one side of it (index 0 or the last)."""
    mapping = sealed["mapping"]
    require_full_run(state, mapping)
    per: dict = {r: {"steps": 0, "end_steps": 0, "marks": 0, "end_marks": 0,
                     "by_depth": {str(d): {"marks": 0, "end_marks": 0} for d in DEPTHS}} for r in ROLES}
    for key, m in mapping.items():
        for d in map(str, DEPTHS):
            entry = state["rows"][key][d]
            for tok in TOKENS:
                role = m[tok]
                n_steps = len(sealed["journeys"][role][key][d]["path_mbids"]) - 1
                ends = {0, n_steps - 1}
                p = per[role]
                p["steps"] += n_steps
                p["end_steps"] += len(ends)
                for i in entry["weak"][tok]:
                    p["marks"] += 1
                    p["end_marks"] += i in ends
                    p["by_depth"][d]["marks"] += 1
                    p["by_depth"][d]["end_marks"] += i in ends
    for p in per.values():
        p["end_share_of_steps"] = p["end_steps"] / p["steps"] if p["steps"] else None
        p["end_share_of_marks"] = p["end_marks"] / p["marks"] if p["marks"] else None
    c = per["challenger"]
    readable = c["marks"] >= DSL_E_MIN_MARKS
    fires = (readable and 2 * c["end_marks"] > c["marks"]
             and c["end_share_of_marks"] >= DSL_E_RATIO * c["end_share_of_steps"])
    outcome = "unreadable" if not readable else ("fires" if fires else "does_not_fire")
    return {"rule": f"candidate side: >= {DSL_E_MIN_MARKS} weak-step marks, a strict majority on end steps, "
                    f"and end-step share of marks >= {DSL_E_RATIO} x end-step share of steps",
            "readable": readable, "fires": fires, "outcome": outcome, "sentence": E_SENTENCES[outcome],
            "licenses": "the owner's decision whether to revive #249; nothing is revived by the read",
            "candidate": per["challenger"], "today_reference": per["incumbent"]}


# ---- descriptive (DRP-AM7-10): decides nothing -------------------------------------------------
def descriptive(state: dict, mapping: dict) -> dict:
    out: dict = {"decides": "nothing — DSL-R1 to DSL-R4 read the row tally only"}
    ident = {str(d): {"no": 0, "yes_right": 0, "yes_wrong": 0} for d in DEPTHS}
    strength = {axis: {s: {"challenger": 0, "incumbent": 0} for s in STRENGTHS} for axis in AXES.values()}
    known = {"by_depth": {str(d): 0 for d in DEPTHS}, "on_no_preference_rows": {axis: 0 for axis in AXES.values()}}
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
    out["DSL-Q4_identification"] = ident
    out["DSL-Q3_strength"] = strength
    out["DSL-K_known_everyone"] = known
    out["computed_tradeoff_rows"] = {"rows": tradeoff, "of": len(mapping) * len(DEPTHS)}
    return out


def ear_tracking(state: dict, sealed: dict) -> dict:
    """For each clear pick: did the picked side also have less famous middles, a longer journey, more
    added connections traversed? Decides nothing."""
    out = {}
    mapping = sealed["mapping"]

    def mean_fame(j):
        vals = [f for f in j["fame_pctl_interior"] if f is not None]
        return statistics.mean(vals) if vals else None

    for q, axis in AXES.items():
        c = {"rows": 0, "fame_rows": 0, "fame_lower": 0, "length_longer": 0, "more_added_connections": 0}
        for key, m in mapping.items():
            for d in map(str, DEPTHS):
                pick = state["rows"][key][d][q]
                if pick not in m:
                    continue
                c["rows"] += 1
                a = sealed["journeys"][m[pick]][key][d]
                b = sealed["journeys"][m[OTHER[pick]]][key][d]
                fa, fb = mean_fame(a), mean_fame(b)
                if fa is not None and fb is not None:
                    c["fame_rows"] += 1
                    c["fame_lower"] += fa < fb
                c["length_longer"] += a["length"] > b["length"]
                c["more_added_connections"] += a["added_connections_traversed"] > b["added_connections_traversed"]
        out[axis] = c
    return out


def clip_coverage(sealed: dict, clips: dict) -> dict:
    out = {}
    for role, journeys in sealed["journeys"].items():
        slots = [mb for key in journeys for d in journeys[key] for mb in journeys[key][d]["path_mbids"]]
        out[role] = {"slots": len(slots), "no_clip": sum(1 for mb in slots if not clips.get(mb))}
    return out


def main() -> int:
    state = json.loads(in_dir(VERDICTS).read_text("utf-8"))
    sealed = json.loads(sealed_path("dsl_sealed.json").read_text("utf-8"))
    out = tally(state, sealed["mapping"])
    out["sentence"] = sentence(out["read"], out["axes_named"])
    if out["read"] == "DSL-R2":
        out["REQ-41"] = REQ41
    out["DSL-P"] = proxy_read(state, sealed)
    out["DSL-E"] = step_read(state, sealed)
    d = descriptive(state, sealed["mapping"])
    d["ear_tracking"] = ear_tracking(state, sealed)
    clips_file, tells_file = sealed_path("dsl_clips.json"), sealed_path("dsl_clip_tells.json")
    if clips_file.exists():
        d["clip_coverage_by_side"] = clip_coverage(sealed, json.loads(clips_file.read_text("utf-8")))
    if tells_file.exists():
        d["single_side_clipless_by_row"] = json.loads(tells_file.read_text("utf-8"))["single_side_clipless"]
    out["descriptive_only"] = d
    out["mapping_unsealed"] = sealed["mapping"]
    out["tiers"] = sealed["tiers"]
    out["maps"] = sealed["maps"]
    out["substitutions"] = sealed["substitutions"]
    in_dir("dsl_result.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"read: {out['read']}; DSL-P {out['DSL-P']['outcome']}; DSL-E {out['DSL-E']['outcome']}; "
          "wrote dsl_result.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
