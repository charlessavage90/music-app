"""`LBD-C2b`, `R8`, `R9` — read from the per-artist degrees the builds wrote, in the
pre-registration's order and with BOTH controls (section 3's table, `LBD-G2`'s 1-point bar).

For `LBD-A2` against `LBD-A0`, over the fixed 29,892 (absent = degree 0):

  * `LBD-C2b` — the share at <= 2 connections in the built graph, and its change in
    percentage points; the paired sign test (gained / lost / unchanged) as `lbd_c2a_compare.py`
    reports it for the pair-table level;
  * control 1 — the pre-existing 58,793 as the within-arm reference (`R9`: if it moves by as
    much or more, the movement is a population artefact);
  * control 2 — the arm's own `LBD-C2a` figure, read from the committed `c2a.json`
    (`R8`: if `LBD-C2a` moved and `LBD-C2b` did not, our own ceiling is absorbing the gain);
  * descriptively, the residual stratum and its complement side by side (`LBD-AM4-4`).

Then, per arm, the added-set figures against the ceiling probe's §4 bridge control — read
from that probe's own committed `dcf_results_bridge.json`, ceiling-50 row — reported as
DIFFERENCES (this document's own figures), never as a restatement of the control's numbers.
`CXR-P2` is the same population under the served lineage; the bridge control reproduces it
exactly (ceiling probe README §4), so the difference against the bridge control IS the
difference against `CXR-P2`, and is reported once under both names.

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u analysis/2026-09-10-lbd-supply/lbd_c2b_compare.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = Path(r"C:\unsung-fast\lbd-pairs")
INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
RESIDUAL = INPUTS / "cxr_residual_mbids.txt"
BRIDGE = HERE.parent / "2026-09-07-degree-ceiling-falsifier" / "dcf_results_bridge.json"
ARMS = ("A0", "A2")
BAR_PP = 1.0  # LBD-G2, graph level, both controls reported


def binom_two_sided(k: int, n: int) -> float:
    if n == 0:
        return float("nan")
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(lo + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def share_le2(d: dict[str, int]) -> float:
    return sum(1 for v in d.values() if v <= 2) / len(d)


def share_absent(d: dict[str, int]) -> float:
    return sum(1 for v in d.values() if v == 0) / len(d)


def compare(base: dict[str, int], arm: dict[str, int]) -> dict:
    gained = sum(1 for m in base if arm[m] > base[m])
    lost = sum(1 for m in base if arm[m] < base[m])
    return {
        "n": len(base),
        "share_le_2": share_le2(arm),
        "delta_pp_vs_A0": 100 * (share_le2(arm) - share_le2(base)),
        "share_absent": share_absent(arm),
        "gained": gained, "lost": lost, "unchanged": len(base) - gained - lost,
        "sign_test_p": binom_two_sided(gained, gained + lost),
    }


def main() -> int:
    deg = {a: json.loads((HERE / f"lbd_build_{a}.degrees.json").read_text(encoding="utf-8")) for a in ARMS}
    c2a = {a: json.loads((PAIRS / a / "c2a.json").read_text(encoding="utf-8")) for a in ARMS}
    residual = {line.strip() for line in RESIDUAL.read_text(encoding="utf-8").splitlines() if line.strip()}
    base_added, base_pre = deg["A0"]["added"], deg["A0"]["preexisting"]

    out: dict = {"bar_pp": BAR_PP, "reads": {}}
    print("LBD-C2b — graph level, share <= 2 over all 29,892 (absent = 0), vs LBD-A0; LBD-G2 bar >= 1 pp with both controls\n")
    for a in ARMS:
        added, pre = deg[a]["added"], deg[a]["preexisting"]
        whole = compare(base_added, added)
        res = compare({m: v for m, v in base_added.items() if m in residual}, {m: v for m, v in added.items() if m in residual})
        comp = compare({m: v for m, v in base_added.items() if m not in residual}, {m: v for m, v in added.items() if m not in residual})
        ref = compare(base_pre, pre)
        c2a_whole = c2a[a]["whole_set"]["share_le_2"]
        c2a_delta = 100 * (c2a_whole - c2a["A0"]["whole_set"]["share_le_2"])
        out["reads"][a] = {
            "C2b_whole": whole, "C2b_residual": res, "C2b_complement": comp,
            "control_preexisting": ref,
            "control_C2a_same_arm": {"share_le_2": c2a_whole, "delta_pp_vs_A0": c2a_delta},
        }
        print(f"  {a}  whole     share<=2 {whole['share_le_2']:.4f}  Δ {whole['delta_pp_vs_A0']:+.2f} pp  gained/lost/same {whole['gained']}/{whole['lost']}/{whole['unchanged']}  p {whole['sign_test_p']:.3g}  absent {whole['share_absent']:.4f}")
        print(f"      residual  share<=2 {res['share_le_2']:.4f}  Δ {res['delta_pp_vs_A0']:+.2f} pp  gained/lost/same {res['gained']}/{res['lost']}/{res['unchanged']}  absent {res['share_absent']:.4f}")
        print(f"      complement share<=2 {comp['share_le_2']:.4f}  Δ {comp['delta_pp_vs_A0']:+.2f} pp  absent {comp['share_absent']:.4f}")
        print(f"      pre-existing (control 1) share<=2 {ref['share_le_2']:.4f}  Δ {ref['delta_pp_vs_A0']:+.2f} pp  absent {ref['share_absent']:.4f}")
        print(f"      C2a same arm (control 2) share<=2 {c2a_whole:.4f}  Δ {c2a_delta:+.2f} pp\n")

    # --- R8 / R9, read as written --------------------------------------------------------------
    a2 = out["reads"]["A2"]
    c2a_moved = a2["control_C2a_same_arm"]["delta_pp_vs_A0"] <= -BAR_PP
    c2b_moved = a2["C2b_whole"]["delta_pp_vs_A0"] <= -BAR_PP
    pre_moved_as_much = a2["control_preexisting"]["delta_pp_vs_A0"] <= a2["C2b_whole"]["delta_pp_vs_A0"]
    out["R8"] = {"fires": c2a_moved and not c2b_moved,
                 "text": "LBD-C2a moves but LBD-C2b does not: our own degree ceiling is absorbing the gain; the graph-level null is BARRED from being read as a supply null (LBD-X1); do NOT propose a ceiling change on this evidence"}
    out["R9"] = {"fires": c2b_moved and pre_moved_as_much,
                 "text": "LBD-C2b moves but the pre-existing 58,793 move by as much or more: a population artefact, not a supply gain"}
    out["G2_graph_level"] = {"A2_clears_1pp_bar_with_both_controls": c2b_moved}
    print(f"  LBD-G2 graph level, A2: C2b Δ {a2['C2b_whole']['delta_pp_vs_A0']:+.2f} pp -> {'clears' if c2b_moved else 'does NOT clear'} the 1 pp bar (both controls reported)")
    print(f"  R8 {'FIRES' if out['R8']['fires'] else 'does not fire'}: C2a Δ {a2['control_C2a_same_arm']['delta_pp_vs_A0']:+.2f} pp, C2b Δ {a2['C2b_whole']['delta_pp_vs_A0']:+.2f} pp")
    print(f"  R9 {'FIRES' if out['R9']['fires'] else 'does not fire'}: pre-existing Δ {a2['control_preexisting']['delta_pp_vs_A0']:+.2f} pp vs added Δ {a2['C2b_whole']['delta_pp_vs_A0']:+.2f} pp\n")

    # --- against the bridge control (= CXR-P2's population under the served lineage) ----------
    bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
    ctrl = next(x for x in bridge["arms"] if x["union_degree_ceiling"] == 50)
    out["vs_bridge_control_and_CXR_P2"] = {}
    print("Against the ceiling probe's §4 bridge control (ceiling 50, same P) — DIFFERENCES only; the control's figures are its README's:")
    for a in ARMS:
        build = json.loads((HERE / f"lbd_build_{a}.json").read_text(encoding="utf-8"))
        s = build["sets"]
        row = {
            "added_share_le_2_or_absent_delta_pp": 100 * (s["added"]["share_le_2_or_absent"] - ctrl["added"]["share_le_2_or_absent"]),
            "added_median_delta": s["added"].get("median_degree", 0) - ctrl["added"]["median_degree"],
            "added_share_absent_delta_pp": 100 * (s["added"]["share_absent"] - ctrl["added"]["share_absent"]),
            "preexisting_share_le_2_or_absent_delta_pp": 100 * (s["preexisting"]["share_le_2_or_absent"] - ctrl["pre_existing"]["share_le_2_or_absent"]),
            "preexisting_median_delta": s["preexisting"].get("median_degree", 0) - ctrl["pre_existing"]["median_degree"],
            "nodes_delta": build["whole_graph"]["nodes"] - ctrl["whole_graph"]["nodes"],
            "edges_delta": build["whole_graph"]["edges"] - ctrl["whole_graph"]["edges"],
        }
        out["vs_bridge_control_and_CXR_P2"][a] = row
        print(f"  {a}: added dead-end share {row['added_share_le_2_or_absent_delta_pp']:+.2f} pp, added median {row['added_median_delta']:+g}, "
              f"added absent {row['added_share_absent_delta_pp']:+.2f} pp; pre-existing dead-end {row['preexisting_share_le_2_or_absent_delta_pp']:+.2f} pp, "
              f"median {row['preexisting_median_delta']:+g}; nodes {row['nodes_delta']:+,}, edges {row['edges_delta']:+,}")

    (HERE / "lbd_c2b_compare.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {HERE / 'lbd_c2b_compare.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
