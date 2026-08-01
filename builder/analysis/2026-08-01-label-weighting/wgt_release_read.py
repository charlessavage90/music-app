"""`WGT-4`: the three release-level scoping readings and the four-branch rule.

Pre-registration §4. Run only after the release pass has streamed the WHOLE
dump -- a number from a partial pass is not a `WGT-4` figure, and this script
refuses to run while the checkpoint file still exists.

  4a  incremental reach   -- artists gaining their FIRST label from releases,
                             beyond everything the committed sources reach.
                             Bar: >= 742 artists (1% of the census population).
  4b  incremental evidence -- do pressings change which candidates look
                             coherent? Within-list Spearman of the evidence
                             scheme with vs without the uncollapsed EV-R
                             candidate, W1 lists. Material iff share below
                             0.99 exceeds 0.25 (the rarity anchor).
  4c  reissue confound    -- Spearman(mean releases per release group, fame).
                             >= 0.37 collapses EV-R to presence-per-RG.

The decision rule's four branches are enumerated in the pre-registration and
this script prints which one fired; it decides nothing beyond that.

Run from `builder/` (~10 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-01-label-weighting/wgt_release_read.py \
        --capture <path>/alge_capture.npz
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (_TAS, _REL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from tas_common import GLOBAL_NEUTRAL_FALLBACK, fame_frame  # noqa: E402
from tas_frame_split import five_frames  # noqa: E402
from tas_weighting import idf_table, spearman  # noqa: E402
from td_turnover import Capture  # noqa: E402

from wgt_grid import CAPTURE_SHA, describe, evidence_weights  # noqa: E402
from wgt_evidence import CKPT, OUT_RELEASE  # noqa: E402

OUT = HERE / "wgt_release_read.json"

REACH_BAR = 742          # 1% of the 74,193 census population
MATERIAL_SHARE = 0.25    # the rarity anchor, tas_weighting.json reading C
REISSUE_BAR = 0.37       # the frame's own label-count leak, reading B


def ev_field(cap: Capture, labels: dict[str, set[str]],
             idf: dict[str, float], e_all: dict[str, dict[str, float]],
             floor: float) -> np.ndarray:
    """Resolved evidence-scheme agreement for every slot, one frame."""
    sets = [labels.get(m, set()) for m in cap.mbids]
    evs = [{lab: e_all.get(m, {}).get(lab, floor) for lab in labels.get(m, set())}
           for m in cap.mbids]
    field = np.empty(cap.total, dtype=np.float64)
    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if lo == hi:
            continue
        own, e_u = sets[u], evs[u]
        vals: list[float | None] = []
        for pos in range(lo, hi):
            c = int(cap.s_cand[pos])
            cand, e_c = sets[c], evs[c]
            if not own or not cand:
                vals.append(None)
                continue
            union, inter = own | cand, own & cand
            den = sum(idf.get(x, 0.0) * max(e_u.get(x, 0.0), e_c.get(x, 0.0))
                      for x in union)
            num = sum(idf.get(x, 0.0) * min(e_u[x], e_c[x]) for x in inter)
            vals.append((num / den) if den > 0 else None)
        got = [v for v in vals if v is not None]
        neutral = (statistics.median(got) if len(got) >= 2
                   else GLOBAL_NEUTRAL_FALLBACK)
        for i, v in enumerate(vals):
            field[lo + i] = neutral if v is None else v
        if u % 15000 == 0:
            print(f"    field {u}/{cap.n}", flush=True)
    return field


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    if CKPT.exists():
        raise SystemExit("checkpoint still present -- the release pass has not "
                         "finished, and a partial-pass number is not a WGT-4 figure")
    import hashlib
    digest = hashlib.sha256(Path(args.capture).read_bytes()).hexdigest()
    if digest != CAPTURE_SHA:
        raise SystemExit(f"capture sha mismatch: {digest}")

    release = json.loads(OUT_RELEASE.read_text(encoding="utf-8"))
    frames = five_frames()
    fame = fame_frame()

    # ---- 4a: incremental reach beyond every committed source ----
    gained = [m for m, rec in release.items()
              if rec["labels"] and not frames["W6"].get(m)]
    r4a = {"artists_gaining_first_label": len(gained), "bar": REACH_BAR,
           "fired": len(gained) >= REACH_BAR}
    print(f"WGT-4a: {len(gained)} artists gain a first label "
          f"(bar {REACH_BAR}) -> {'REACH' if r4a['fired'] else 'no reach case'}",
          flush=True)

    # ---- 4c: the reissue confound ----
    xs, ys = [], []
    for m, rec in release.items():
        if m not in fame or not rec["rgs"]:
            continue
        xs.append(fame[m])
        ys.append(sum(rec["rgs"].values()) / len(rec["rgs"]))
    rho_c = spearman(np.array(xs), np.array(ys))
    r4c = {"spearman_mean_releases_per_rg_vs_fame": round(rho_c, 4),
           "bar": REISSUE_BAR, "fired": abs(rho_c) >= REISSUE_BAR,
           "artists": len(xs)}
    print(f"WGT-4c: reissue-vs-fame spearman {rho_c:.4f} (bar {REISSUE_BAR}) "
          f"-> {'COLLAPSE to presence-per-RG' if r4c['fired'] else 'uncollapsed ok'}",
          flush=True)

    # ---- 4b: incremental evidence on W1 lists ----
    cap = Capture(Path(args.capture))
    idf, _df = idf_table(frames["W1"], cap.n)
    import math
    floor = math.log1p(1.0) / math.log1p(8.0)
    print("  building evidence WITHOUT EV-R", flush=True)
    e_without, gate_without = evidence_weights(False)
    print("  building evidence WITH the uncollapsed EV-R candidate", flush=True)
    e_with, gate_with = evidence_weights(True)
    f_without = ev_field(cap, frames["W1"], idf, e_without, floor)
    f_with = ev_field(cap, frames["W1"], idf, e_with, floor)

    rhos = []
    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if hi - lo < 3 or not frames["W1"].get(cap.mbids[u]):
            continue
        r = spearman(f_without[lo:hi], f_with[lo:hi])
        if r is not None:
            rhos.append(r)
    dsc = describe(rhos)
    r4b = {"within_list_spearman_with_vs_without": dsc,
           "material_share_bar": MATERIAL_SHARE,
           "material": dsc["share_below_0.99"] > MATERIAL_SHARE}
    print(f"WGT-4b: share below 0.99 = {dsc['share_below_0.99']} "
          f"(bar {MATERIAL_SHARE}) -> "
          f"{'MATERIAL' if r4b['material'] else 'not material'}", flush=True)

    # ---- the four-branch rule, enumerated in the pre-registration ----
    if r4a["fired"]:
        branch = ("1: EV-R ADMITTED on reach"
                  + (", collapsed per-RG (4c fired)" if r4c["fired"] else ""))
        admitted = True
    elif r4b["material"] and not r4c["fired"]:
        branch, admitted = "2: EV-R ADMITTED on evidence", True
    elif r4b["material"] and r4c["fired"]:
        branch, admitted = ("3: EXCLUDED -- ordering movement is fame-shaped; "
                            "recorded as a leak finding"), False
    else:
        branch, admitted = ("4: release-group preference CONFIRMED under the "
                            "weighting lens; EV-R never exists"), False

    Path(args.out).write_text(json.dumps({
        "note": "WGT-4, pre-registration §4. The branch below is the rule "
                "firing, not a judgement.",
        "WGT-4a": r4a, "WGT-4b": r4b, "WGT-4c": r4c,
        "ev_r_leak_gate_context": gate_with["spearman_vs_fame_labelled_artists"],
        "branch": branch, "ev_r_admitted": admitted,
    }, indent=1), encoding="utf-8")
    print(f"\nBRANCH {branch}\nwrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
