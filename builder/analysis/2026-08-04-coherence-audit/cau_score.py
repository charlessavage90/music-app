"""CAU- scoring: run AFTER every slot is judged. Mechanical only -- the write-up
is a session's job, and per spec §0 it should be a session that did not run this.

Order is fixed by spec §5: CAU-G1 is evaluated FIRST, and if it fails nothing else
is computed -- a blunt instrument produces no readings, not weak ones.
"""
from __future__ import annotations

import json
import sys

from cau_common import (C1_FAIL, C1_PASS, C2_TRIGGER, C3_TRIGGER, G1_BAR,
                        N_INJECT, in_dir, sealed_path)

# Branch names deliberately avoid "pass"/"fail": CAU-C1's middle branch is
# neither, and the spec forbids the audit picking a side there.
C1_SENTENCES = {
    "meets_bar": "The new artists it digs up genuinely belong in the journey.",
    "ambiguous": ("It is a real improvement in what it finds and a real cost in "
                  "what it gets wrong."),
    "below_bar": "The new artists it digs up are substantially noise.",
}


class RunIncomplete(SystemExit):
    pass


def evaluate(page: dict, judged: dict, sealed: dict) -> dict:
    slots = judged["slots"]
    control = {v["slot"] for v in sealed["injections"].values()}

    all_slots = [f"{j['id']}#{i}"
                 for j in page["journeys"]
                 for i, a in enumerate(j["artists"]) if a["role"] == "interior"]
    absent = [s for s in all_slots if slots.get(s) is None]
    if absent:
        raise RunIncomplete(
            f"spec §5 run state unmet -- no read exists. {len(absent)} slot(s) "
            f"unjudged: {absent[:8]}")

    # --- CAU-G1 first, and alone if it fails -------------------------------
    if len(control) != N_INJECT:
        raise SystemExit(f"sealed file holds {len(control)} controls, expected {N_INJECT}")
    rejected = sum(1 for s in control if slots[s]["verdict"] == "doesnt_fit")
    g1_pass = rejected >= G1_BAR
    out = {
        "CAU_G1": {
            "controls": N_INJECT, "rejected": rejected, "bar": G1_BAR,
            "pass": g1_pass,
            "sentence": ("the audit can tell a bad recommendation from a good one"
                         if g1_pass else
                         "the audit could NOT tell a bad recommendation from a "
                         "good one, so every reading below is VOID"),
        }
    }
    if not g1_pass:
        out["VOID"] = True
        out["readings"] = None
        return out

    # --- the real slots ----------------------------------------------------
    # CAU-AM3: the one real card each control is inserted beside was judged, but
    # it was judged next to a fake artist, so it is not scored. Declared in the
    # pre-registration in advance; the owner is never told which slots these are.
    excluded = {v["excluded_slot"] for v in sealed["injections"].values()
                if v.get("excluded_slot")}
    real = [s for s in all_slots if s not in control and s not in excluded]
    lookup = [s for s in real if slots[s]["looked_up"]]

    def rates(pool):
        n = len(pool)
        c = {v: sum(1 for s in pool if slots[s]["verdict"] == v)
             for v in ("fits", "doesnt_fit", "cant_tell")}
        return {"n": n, **c,
                "fits_frac": (c["fits"] / n) if n else None}

    d_all, d_lookup = rates(real), rates(lookup)
    d_all["excluded_control_adjacent"] = len(excluded)

    frac = d_all["fits_frac"]
    branch = ("meets_bar" if frac >= C1_PASS
              else "below_bar" if frac <= C1_FAIL
              else "ambiguous")

    per_journey = {}
    for s in real:
        if slots[s]["verdict"] == "doesnt_fit":
            j = s.split("#")[0]
            per_journey[j] = per_journey.get(j, 0) + 1
    worst = max(per_journey.values()) if per_journey else 0

    cant = d_all["cant_tell"] / d_all["n"] if d_all["n"] else 0.0

    out["readings"] = {
        "CAU_C1": {"D_all": d_all, "D_lookup": d_lookup,
                   "bar_pass": C1_PASS, "bar_fail": C1_FAIL,
                   "branch": branch, "sentence": C1_SENTENCES[branch]},
        "CAU_C2": {"worst_journey_doesnt_fit": worst, "trigger": C2_TRIGGER,
                   "fires": worst >= C2_TRIGGER,
                   "per_journey": per_journey,
                   "sentence": ("at least one journey carries several artists that "
                                "do not belong" if worst >= C2_TRIGGER else
                                "the ones that do not belong are spread thin")},
        "CAU_C3": {"cant_tell_frac": cant, "trigger": C3_TRIGGER,
                   "fires": cant > C3_TRIGGER,
                   "sentence": ("proper listening still left a large share "
                                "unjudgeable, which falsifies this audit's own "
                                "premise" if cant > C3_TRIGGER else
                                "proper listening resolved almost everything")},
    }
    out["VOID"] = False
    return out


def main() -> int:
    page = json.loads(in_dir("cau_page_data.json").read_text("utf-8"))
    judged = json.loads(in_dir("cau_judgements.json").read_text("utf-8"))
    sealed = json.loads(sealed_path("cau_sealed.json").read_text("utf-8"))
    out = evaluate(page, judged, sealed)
    out["journey_notes"] = judged.get("journey_notes", {})
    out["unsealed_injections"] = sealed["injections"]
    in_dir("cau_result.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    g1 = out["CAU_G1"]
    if out["VOID"]:
        print(f"CAU-G1 FAILED ({g1['rejected']}/{g1['controls']} rejected, bar "
              f"{g1['bar']}): the audit is VOID. wrote cau_result.json", flush=True)
    else:
        r = out["readings"]["CAU_C1"]
        print(f"CAU-G1 passed ({g1['rejected']}/{g1['controls']}); CAU-C1 branch: "
              f"{r['branch']} (fits {r['D_all']['fits_frac']:.1%} of "
              f"{r['D_all']['n']}); wrote cau_result.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
