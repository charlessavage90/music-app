"""`WAV-`: the within-artist vote read. Criteria and bars: README.md, committed first.

Two marked copies from the frozen `wgt_grid.py`, both equivalence-checked at run
time before any new figure is read (WAV-0b / WAV-0e):

- the evidence mass assembly (`with_release=False` path), extended to RETURN the
  raw per-(artist, label) strengths the committed function discards after damping
  -- `e_rel` needs them uncapped, because `S_CAP` flattens exactly the many-vote
  artists the owner's question is about;
- `frame_pass`, extended with the `evidence_rel` measure (and its all-ones
  degeneracy twin `rel_ones`) and parameterised over measures so the `W0` pass
  only computes what the scorable-population derivation needs.

Run from `builder/` (see README for the capture regeneration first):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-within-artist-votes/wav_read.py \
        --capture <scratchpad>/alge_capture.npz
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
_WGT = HERE.parent / "2026-08-01-label-weighting"
_FAM = HERE.parent / "2026-08-02-fame-instrument"
for _p in (_WGT,):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import wgt_grid  # noqa: E402  -- inserts the tas/rel dirs on its own sys.path

from tas_common import GLOBAL_NEUTRAL_FALLBACK, fame_frame, graph_mbids, norm_genre  # noqa: E402
from tas_frame_split import five_frames  # noqa: E402
from tas_select import LAMBDAS, edge_turnover, mask_tag  # noqa: E402
from tas_signal import iqr  # noqa: E402
from tas_weighting import idf_table, spearman  # noqa: E402
from td_turnover import Capture, mutual_undirected  # noqa: E402

OUT = HERE / "wav_read.json"
FAME_LB = _FAM / "fi_union_snapshot.json"
LEAK_BAR = 0.50
TOL = 5e-5

# Committed values reproduced as instrument checks (WAV-0b/0e); sources named.
COMMITTED_GATE = {"EV-A_votes": 0.4345, "EV-G_rg_count": 0.4983}  # wgt_grid.json WGT-1


# ------------------------------------------------------- masses (marked copy)

def masses() -> dict[str, dict[str, dict[str, float]]]:
    """Marked copy of wgt_grid.evidence_weights' per-source mass assembly
    (with_release=False). Kept byte-faithful in behaviour; WAV-0e proves it."""
    from rel_artist_dump import OUT_INDEX as ARTIST_INDEX
    from rel_discogs import OUT_RAW as DISCOGS_RAW
    from rel_rg_dump import OUT_RAW as RG_RAW
    from tas_wikidata import OUT_RAW as WD_RAW

    votes = json.loads((_WGT / "wgt_artist_votes.json").read_text(encoding="utf-8"))
    wd = json.loads(WD_RAW.read_text(encoding="utf-8"))
    rg = json.loads(RG_RAW.read_text(encoding="utf-8"))
    index = json.loads(ARTIST_INDEX.read_text(encoding="utf-8"))
    discogs = json.loads(DISCOGS_RAW.read_text(encoding="utf-8"))

    per: dict[str, dict[str, dict[str, float]]] = {}
    for m in graph_mbids():
        src: dict[str, dict[str, float]] = {}
        src["A"] = {lab: max(float(v), 0.0)
                    for lab, v in (votes.get(m) or {}).items()}
        src["W"] = {norm_genre(g): 1.0
                    for g in ((wd.get(m) or {}).get("genres") or []) if norm_genre(g)}
        g_counts: Counter = Counter()
        for rec in rg.get(m) or []:
            if not rec.get("a"):
                continue
            for lab in set(rec.get("g") or []) | set(rec.get("t") or []):
                g_counts[lab] += 1
        src["G"] = dict(g_counts)
        did = (index.get(m) or {}).get("discogs")
        bucket = discogs.get(did or "") or {}
        src["D"] = {lab: 1.0
                    for lab in set(bucket.get("g") or []) | set(bucket.get("s") or [])}
        per[m] = src
    return per


def strength_of(src: dict[str, dict[str, float]], lab: str) -> float:
    """Committed combined strength, no-degradation form (the committed gate
    degraded nothing; WAV-0e re-verifies that before this is trusted)."""
    return (src["A"].get(lab, 0.0) + src["W"].get(lab, 0.0)
            + src["G"].get(lab, 0.0) + src["D"].get(lab, 0.0))


def leaks_of(per: dict) -> dict[str, float | None]:
    """The committed WGT-1 mass-leak statistic, recomputed for WAV-0e."""
    frame = fame_frame()
    out: dict[str, float | None] = {}
    for key, name in (("A", "EV-A_votes"), ("G", "EV-G_rg_count")):
        xs, ys = [], []
        for m, src in per.items():
            if m not in frame:
                continue
            if any(src[k] for k in src):
                xs.append(frame[m])
                ys.append(sum(src.get(key, {}).values()))
        out[name] = spearman(np.array(xs), np.array(ys))
    return out


def abs_table(per: dict) -> dict[str, dict[str, float]]:
    """The committed absolute e(a, l), rebuilt from the mass copy (WAV-0e
    compares this against wgt_grid.evidence_weights' own output)."""
    e_all: dict[str, dict[str, float]] = {}
    for m, src in per.items():
        labs = set().union(*(src[k].keys() for k in src)) if src else set()
        e_m: dict[str, float] = {}
        for lab in labs:
            s = strength_of(src, lab)
            if s <= 0:
                s = 1.0
            e_m[lab] = min(1.0, math.log1p(s) / math.log1p(wgt_grid.S_CAP))
        e_all[m] = e_m
    return e_all


def rel_table(per: dict) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """e_rel(a, l) = log1p(s) / log1p(s_max(a)), capped at 1; s_max <= 1 -> all
    1.0 (no usable ordering: degrade to rarity, the dark-tail rule). Returns the
    table and per-artist s_max (the frame-filter floor needs it)."""
    rel: dict[str, dict[str, float]] = {}
    smax: dict[str, float] = {}
    for m, src in per.items():
        labs = set().union(*(src[k].keys() for k in src)) if src else set()
        s_by: dict[str, float] = {}
        for lab in labs:
            s = strength_of(src, lab)
            s_by[lab] = 1.0 if s <= 0 else s
        mx = max(s_by.values(), default=0.0)
        smax[m] = mx
        if mx <= 1.0:
            rel[m] = {lab: 1.0 for lab in s_by}
        else:
            n = math.log1p(mx)
            rel[m] = {lab: min(1.0, math.log1p(s) / n) for lab, s in s_by.items()}
    return rel, smax


def rel_for(rel: dict, smax: dict, m: str, labels: set[str]) -> dict[str, float]:
    """Frame filter with the within-artist analogue of the committed s=1 floor."""
    base = rel.get(m, {})
    mx = smax.get(m, 0.0)
    floor = 1.0 if mx <= 1.0 else min(1.0, math.log1p(1.0) / math.log1p(mx))
    return {lab: base.get(lab, floor) for lab in labels}


# ------------------------------------------------------- pass (marked copy)

def wav_pass(cap: Capture, labels: dict[str, set[str]], idf: dict[str, float],
             e_abs_all: dict, rel: dict, smax: dict,
             measures: tuple[str, ...]) -> dict:
    """Marked copy of wgt_grid.frame_pass: parameterised measures, plus the
    evidence_rel measure and its all-ones twin. Neutral rule unchanged."""
    sets = [labels.get(m, set()) for m in cap.mbids]
    need_abs = "evidence" in measures
    need_rel = "evidence_rel" in measures or "rel_ones" in measures
    evs = ([wgt_grid.e_for(e_abs_all, m, labels.get(m, set())) for m in cap.mbids]
           if need_abs else None)
    rels = ([rel_for(rel, smax, m, labels.get(m, set())) for m in cap.mbids]
            if need_rel else None)

    fields = {k: np.empty(cap.total, dtype=np.float64) for k in measures}
    raw: dict[str, list[list[tuple[int, float]]]] = {k: [] for k in measures}
    strengths: list[list[float]] = []
    owners: list[int] = []

    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if lo == hi:
            continue
        own = sets[u]
        e_u = evs[u] if need_abs else None
        r_u = rels[u] if need_rel else None
        vals: dict[str, list[float | None]] = {k: [] for k in measures}
        for pos in range(lo, hi):
            c = int(cap.s_cand[pos])
            cand = sets[c]
            if not own or not cand:
                for k in measures:
                    vals[k].append(None)
                continue
            inter, union = own & cand, own | cand
            if "plain" in measures:
                vals["plain"].append(len(inter) / len(union))
            r_un = sum(idf.get(x, 0.0) for x in union)
            r_in = sum(idf.get(x, 0.0) for x in inter)
            rar = (r_in / r_un) if r_un > 0 else None
            if "rarity" in measures:
                vals["rarity"].append(rar)
            if need_abs:
                e_c = evs[c]
                un = sum(idf.get(x, 0.0) * max(e_u.get(x, 0.0), e_c.get(x, 0.0))
                         for x in union)
                inn = sum(idf.get(x, 0.0) * min(e_u[x], e_c[x]) for x in inter)
                vals["evidence"].append((inn / un) if un > 0 else None)
            if need_rel:
                r_c = rels[c]
                if "evidence_rel" in measures:
                    un = sum(idf.get(x, 0.0) * max(r_u.get(x, 0.0), r_c.get(x, 0.0))
                             for x in union)
                    inn = sum(idf.get(x, 0.0) * min(r_u[x], r_c[x]) for x in inter)
                    vals["evidence_rel"].append((inn / un) if un > 0 else None)
                if "rel_ones" in measures:
                    # the degeneracy twin: weights forced to 1 -> must equal rarity
                    un = sum(idf.get(x, 0.0) * 1.0 for x in union)
                    inn = sum(idf.get(x, 0.0) * 1.0 for x in inter)
                    vals["rel_ones"].append((inn / un) if un > 0 else None)
        for k in measures:
            got = [(i, v) for i, v in enumerate(vals[k]) if v is not None]
            neutral = (statistics.median([v for _i, v in got]) if len(got) >= 2
                       else GLOBAL_NEUTRAL_FALLBACK)
            for i, v in enumerate(vals[k]):
                fields[k][lo + i] = neutral if v is None else v
            raw[k].append(got)
        strengths.append([float(cap.s_rank[pos]) for pos in range(lo, hi)])
        owners.append(u)
        if u % 15000 == 0:
            print(f"    pass {u}/{cap.n}", flush=True)

    return {"fields": fields, "raw": raw, "strengths": strengths, "owners": owners}


def cell_stats(data: dict, key: str, scorable: set[int]) -> dict:
    spreads, pairs = [], []
    for u, got, strength in zip(data["owners"], data["raw"][key], data["strengths"]):
        if u not in scorable:
            continue
        s = iqr([v for _i, v in got])
        if s is None:
            continue
        spreads.append(s)
        pairs.extend((strength[i], v) for i, v in got)
    x = np.array([a for a, _ in pairs])
    y = np.array([b for _, b in pairs])
    return {"median_iqr": round(statistics.median(spreads), 4) if spreads else None,
            "spearman_vs_similarity": round(spearman(x, y), 4) if pairs else None}


def turnover_between(cap: Capture, f_base: np.ndarray, f_arm: np.ndarray) -> dict:
    out = {}
    for lam in LAMBDAS:
        base = mutual_undirected(cap, mask_tag(cap, f_base, lam))
        arm = mutual_undirected(cap, mask_tag(cap, f_arm, lam))
        out[str(lam)] = edge_turnover(base, arm)["turnover_share"]
    return out


def mean_weight_leaks(cap_frame_labels: dict[str, set[str]], e_abs_all: dict,
                      rel: dict, smax: dict) -> dict:
    """WAV-3: per-artist mean W4 weight vs fame, both schemes, both rulers."""
    lb = json.loads(FAME_LB.read_text(encoding="utf-8"))
    old = fame_frame()
    rows = {"abs": {}, "rel": {}}
    for m, labs in cap_frame_labels.items():
        if not labs:
            continue
        ea = wgt_grid.e_for(e_abs_all, m, labs)
        er = rel_for(rel, smax, m, labs)
        rows["abs"][m] = sum(ea.values()) / len(ea)
        rows["rel"][m] = sum(er.values()) / len(er)

    def rho(vals: dict[str, float], fame: dict) -> tuple[float | None, int]:
        xs, ys = [], []
        for m, v in vals.items():
            f = fame.get(m)
            if f is None:
                continue
            xs.append(float(f))
            ys.append(v)
        return spearman(np.array(xs), np.array(ys)), len(xs)

    lb_abs, n_lb = rho(rows["abs"], lb)
    lb_rel, _ = rho(rows["rel"], lb)
    old_abs, n_old = rho(rows["abs"], old)
    old_rel, _ = rho(rows["rel"], old)
    return {
        "binding_fame_lb_raw": {
            "n_artists": n_lb,
            "evidence_abs": round(lb_abs, 4) if lb_abs is not None else None,
            "evidence_rel": round(lb_rel, 4) if lb_rel is not None else None},
        "descriptive_retired_frame": {
            "n_artists": n_old,
            "evidence_abs": round(old_abs, 4) if old_abs is not None else None,
            "evidence_rel": round(old_rel, 4) if old_rel is not None else None,
            "note": "continuity with the committed WGT-1 gate only; no criterion "
                    "consumes the retired construct"},
    }


# ---------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    t0 = time.time()

    # ---- WAV-0a: provenance ----
    digest = hashlib.sha256(Path(args.capture).read_bytes()).hexdigest()
    if digest != wgt_grid.CAPTURE_SHA:
        raise SystemExit(f"WAV-0a FAILED: capture sha {digest} != "
                         f"{wgt_grid.CAPTURE_SHA}")
    print("WAV-0a PASS: capture sha matches the recorded value", flush=True)

    cap = Capture(Path(args.capture))
    frames = five_frames()

    # ---- WAV-0e: the mass copy reproduces the committed instrument ----
    per = masses()
    got_leaks = leaks_of(per)
    for k, want in COMMITTED_GATE.items():
        g = got_leaks.get(k)
        if g is None or abs(round(g, 4) - want) > 1e-3:
            raise SystemExit(f"WAV-0e FAILED: leak {k} {g} != committed {want}")
        if abs(g) >= LEAK_BAR:
            raise SystemExit(f"WAV-0e FAILED: {k} would degrade; committed run "
                             "degraded nothing")
    mine = abs_table(per)
    theirs, gate = wgt_grid.evidence_weights(False)
    if mine != theirs:
        bad = sum(1 for m in mine if mine[m] != theirs.get(m))
        raise SystemExit(f"WAV-0e FAILED: e(a,l) copy diverges on {bad} artists")
    print(f"WAV-0e PASS: mass copy == committed evidence table "
          f"(leaks {got_leaks})", flush=True)

    rel, smax = rel_table(per)

    # ---- W0 restricted pass: the committed scorable population ----
    print("[W0 restricted pass]", flush=True)
    idf0, _df0 = idf_table(frames["W0"], cap.n)
    d0 = wav_pass(cap, frames["W0"], idf0, mine, rel, smax, ("plain",))
    scorable = {u for u, got in zip(d0["owners"], d0["raw"]["plain"])
                if iqr([v for _i, v in got]) is not None}
    committed_split = json.loads(
        (HERE.parent / "2026-07-30-tag-discrimination" / "tas_frame_split.json")
        .read_text(encoding="utf-8"))
    w0_plain = cell_stats(d0, "plain", scorable)["median_iqr"]
    want = committed_split["frames"]["W0"]["median_iqr"]
    if abs(w0_plain - want) > TOL:
        raise SystemExit(f"WAV-0b FAILED: W0 plain {w0_plain} != committed {want}")
    print(f"WAV-0b (W0 half) PASS: plain median_iqr {w0_plain}; "
          f"population {len(scorable)} lists", flush=True)

    # ---- W4 pass, all measures ----
    print("[W4 pass]", flush=True)
    idf4, _df4 = idf_table(frames["W4"], cap.n)
    d4 = wav_pass(cap, frames["W4"], idf4, mine, rel, smax,
                  ("plain", "rarity", "evidence", "evidence_rel", "rel_ones"))

    # ---- WAV-0d: degeneracy — all-ones weights == rarity, elementwise ----
    if not np.array_equal(d4["fields"]["rel_ones"], d4["fields"]["rarity"]):
        n_bad = int((d4["fields"]["rel_ones"] != d4["fields"]["rarity"]).sum())
        raise SystemExit(f"WAV-0d FAILED: all-ones evidence_rel diverges from "
                         f"rarity on {n_bad} slots")
    print("WAV-0d PASS: all-ones weights reproduce rarity elementwise", flush=True)

    # ---- WAV-0b: committed W4 cells reproduce ----
    committed = json.loads((_WGT / "wgt_grid.json").read_text(encoding="utf-8"))
    w4c = committed["frames"]["W4"]["cells"]
    cells = {k: cell_stats(d4, k, scorable)
             for k in ("plain", "rarity", "evidence", "evidence_rel")}
    for k in ("plain", "rarity", "evidence"):
        for stat in ("median_iqr", "spearman_vs_similarity"):
            if abs(cells[k][stat] - w4c[k][stat]) > TOL:
                raise SystemExit(f"WAV-0b FAILED: W4 {k} {stat} "
                                 f"{cells[k][stat]} != {w4c[k][stat]}")
    ev_turn = turnover_between(cap, d4["fields"]["plain"], d4["fields"]["evidence"])
    for lam, share in ev_turn.items():
        want = w4c["evidence"]["selection_turnover_vs_plain"][lam]["turnover_share"]
        if abs(share - want) > TOL:
            raise SystemExit(f"WAV-0b FAILED: evidence turnover lambda={lam} "
                             f"{share} != {want}")
    print("WAV-0b PASS: committed W4 plain/rarity/evidence cells and evidence "
          "turnovers reproduced", flush=True)

    # ---- WAV-0c + the readings ----
    rel_vs_plain = turnover_between(cap, d4["fields"]["plain"],
                                    d4["fields"]["evidence_rel"])
    rel_vs_rarity = turnover_between(cap, d4["fields"]["rarity"],
                                     d4["fields"]["evidence_rel"])
    for name, t in (("vs_plain", rel_vs_plain), ("vs_rarity", rel_vs_rarity)):
        if t["0.0"] != 0.0:
            raise SystemExit(f"WAV-0c FAILED: lambda=0 turnover {name} != 0")
    print("WAV-0c PASS: lambda=0 turnover exactly 0", flush=True)

    leaks = mean_weight_leaks(
        {m: frames["W4"].get(m, set()) for m in cap.mbids}, mine, rel, smax)

    # ---- verdicts, per the committed README ----
    wav1 = rel_vs_rarity["1.0"]
    wav2 = round(cells["evidence_rel"]["spearman_vs_similarity"]
                 - cells["rarity"]["spearman_vs_similarity"], 4)
    lb = leaks["binding_fame_lb_raw"]
    wav3_ok = (lb["evidence_rel"] is not None and lb["evidence_abs"] is not None
               and abs(lb["evidence_rel"]) < LEAK_BAR
               and abs(lb["evidence_rel"]) < abs(lb["evidence_abs"]))
    verdicts = {
        "WAV-1_movement": {"turnover_rarity_to_rel_lambda1": wav1,
                           "bar": ">= 0.01", "pass": wav1 >= 0.01},
        "WAV-2_redundancy": {"rho_sim_rel_minus_rarity": wav2,
                             "bar": "<= +0.010", "pass": wav2 <= 0.010},
        "WAV-3_fame_shape": {"binding": lb, "bar": "|rel| < 0.50 and |rel| < |abs|",
                             "pass": bool(wav3_ok)},
    }
    all_pass = all(v["pass"] for v in verdicts.values())

    out = {
        "capture_sha256": digest,
        "population_lists": len(scorable),
        "cells_W4": cells,
        "evidence_rel_turnover_vs_plain": rel_vs_plain,
        "evidence_rel_turnover_vs_rarity": rel_vs_rarity,
        "mean_weight_fame_leaks": leaks,
        "committed_leak_reproduction": {k: round(v, 4)
                                        for k, v in got_leaks.items()},
        "verdicts": verdicts,
        "decision": ("ALL PASS: measured grounds for the CRE- amendment (README "
                     "consequence mapping)" if all_pass else
                     "FAIL: rarity stands; the read is closed (README consequence "
                     "mapping)"),
        "note": "Criteria fixed in README.md and committed before this ran. "
                "DIAGNOSTIC for the CRE-S2 ranking device only; nothing else "
                "consumes these figures.",
        "runtime_min": round((time.time() - t0) / 60, 1),
    }
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nwrote {args.out}", flush=True)
    for k, v in verdicts.items():
        print(f"{k}: {'PASS' if v['pass'] else 'FAIL'} {v}", flush=True)
    print(out["decision"], flush=True)


if __name__ == "__main__":
    main()
