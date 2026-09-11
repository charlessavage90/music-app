"""Unblind AFTER every answer is on disk: `LBD-AM5-5`'s tally, `LBL-R1`–`LBL-R4`, and the
ear-tracking table. Mechanical only — the write-up belongs to a further fresh session.

    cd <worktree>/builder && UV_LINK_MODE=copy uv run python \\
      analysis/2026-09-10-lbd-blind-listen/lbl_unblind.py --listen 1
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys

from lbl_common import AXES, DEPTHS, LISTENS, MARGIN, in_dir, sealed_path

# LBD-AM5-5's plain sentences, quoted; [axis] is substituted.
SENTENCES = {
    1: {
        "LBL-R1": "Journeys from our own recomputation are better on [axis], and no worse on the other.",
        "LBL-R2": "My ear cannot tell our recomputed lists from ListenBrainz's own.",
        "LBL-R3": "The lists ListenBrainz published give better journeys on [axis].",
        "LBL-R4": "Too many rows were lost to clip problems to read this listen.",
    },
}


class RunIncomplete(SystemExit):
    pass


def axis_read(rows: dict, mapping: dict, question: str) -> dict:
    """One axis over all pairs x depths: clear picks per role, lost rows, and the axis verdict."""
    picks = {"challenger": 0, "incumbent": 0}
    lost = 0
    for key, m in mapping.items():
        for d in map(str, DEPTHS):
            entry = rows[key][d]
            pick = entry[question]
            if pick in m:
                picks[m[pick]] += 1
            elif entry.get("clip_blocked"):
                lost += 1
    margin = picks["challenger"] - picks["incumbent"]
    if margin >= MARGIN:
        verdict = "challenger_better"
    elif -margin >= MARGIN:
        verdict = "incumbent_better"
    elif lost >= MARGIN:
        verdict = "underpowered"
    else:
        verdict = "no_detectable_difference"
    return {"rows": len(mapping) * len(DEPTHS), "clear_picks": picks, "margin_toward_challenger": margin,
            "clip_blocked_no_preference_rows": lost, "bar": MARGIN, "verdict": verdict}


def listen_read(axes: dict[str, dict]) -> tuple[str, list[str]]:
    """`LBL-R1`–`R4` from the two axis verdicts. Returns (read, the axes the sentence names)."""
    worse = [name for name, a in axes.items() if a["verdict"] == "incumbent_better"]
    better = [name for name, a in axes.items() if a["verdict"] == "challenger_better"]
    if worse:
        return "LBL-R3", worse          # includes a split: a loss on either axis is FAIL
    if better:
        return "LBL-R1", better
    if any(a["verdict"] == "underpowered" for a in axes.values()):
        return "LBL-R4", []
    return "LBL-R2", []


def tally(state: dict, mapping: dict) -> dict:
    missing = [f"{k}:d{d}" for k in mapping for d in DEPTHS
               if not all(state["rows"].get(k, {}).get(str(d), {}).get(q) for q in AXES)]
    missing += [f"{k}:pair" for k in mapping if k not in state["pairs"]]
    if missing:
        raise RunIncomplete(f"LBD-AM5-5 run state unmet — no read exists. Missing: {missing}")
    axes = {AXES[q]: axis_read(state["rows"], mapping, q) for q in AXES}
    read, named = listen_read(axes)
    return {"axes": axes, "read": read, "axes_named": named}


def sentence(listen: int, read: str, named: list[str]) -> str:
    return SENTENCES[listen][read].replace("[axis]", " and ".join(named) if named else "[axis]")


def ear_tracking(state: dict, sealed: dict) -> dict:
    """For each row with a clear pick on an axis: did the picked side also win each hidden metric?
    Fame on the fixed ruler, interiors ListenBrainz reported no listeners for excluded; a row where
    either side has no measured interior is unreadable on fame, not favourable. Decides nothing."""
    out = {}
    mapping = sealed["mapping"]
    for q, axis in AXES.items():
        c = {"rows": 0, "fame_rows": 0, "fame_lower": 0, "payload_higher": 0,
             "top1pct_degree_frac_lower": 0, "length_longer": 0}
        for key, m in mapping.items():
            for d in map(str, DEPTHS):
                pick = state["rows"][key][d][q]
                if pick not in m:
                    continue
                c["rows"] += 1
                a = sealed["journeys"][m[pick]][key][d]["metrics"]
                b = sealed["journeys"][m[{"L": "R", "R": "L"}[pick]]][key][d]["metrics"]

                def mean_fame(mm):
                    vals = [f for f in mm["fame_pctl_interior_fixed_ruler"] if f is not None]
                    return statistics.mean(vals) if vals else None

                fa, fb = mean_fame(a), mean_fame(b)
                if fa is not None and fb is not None:
                    c["fame_rows"] += 1
                    c["fame_lower"] += fa < fb
                c["payload_higher"] += a["payload"] > b["payload"]
                c["top1pct_degree_frac_lower"] += a["top1pct_degree_frac"] < b["top1pct_degree_frac"]
                c["length_longer"] += a["length"] > b["length"]
        out[axis] = c
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", type=int, required=True, choices=LISTENS)
    args = ap.parse_args(argv)
    state = json.loads(in_dir(f"lbl_listen{args.listen}_verdicts.json").read_text("utf-8"))
    sealed = json.loads(sealed_path(f"lbl_listen{args.listen}_sealed.json").read_text("utf-8"))
    out = tally(state, sealed["mapping"])
    out["sentence"] = sentence(args.listen, out["read"], out["axes_named"])
    out["ear_tracking"] = ear_tracking(state, sealed)
    out["mapping_unsealed"] = sealed["mapping"]
    out["maps"] = sealed["maps"]
    out["substitutions"] = sealed["substitutions"]
    in_dir(f"lbl_listen{args.listen}_result.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"read: {out['read']}; wrote lbl_listen{args.listen}_result.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
