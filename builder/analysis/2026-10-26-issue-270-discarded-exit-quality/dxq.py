"""Issue #270, DXQ-: the less-listened exits the fifty-connection limit deleted, against the kept ones.

A descriptive measurement. IT DECIDES NOTHING: no journey is routed, nothing is changed or proposed.
The design (groups DXQ-K/KL/D/DH/DS1, assertions DXQ-A1..A4, measures DXQ-M1..M8 and every summary
statistic) is fixed in this directory's README.md, committed before any figure existed.

Instrument: `../2026-09-27-issue-200-trim-supply/trim_supply.py`, executed UNMODIFIED with
`runpy.run_path`; this script only computes on the globals it leaves. Its refusals (exit 2/3)
propagate. Router weights are read from the shipped `ApiConfig()` at run time.

No command-line arguments. Refuses (exit 2) on a graph-drp-s1.bin sha mismatch before reading
anything of its own; refuses (exit 3) if `w_degree_hub != 0.0` or an assertion fails.

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-10-26-issue-270-discarded-exit-quality/dxq.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import runpy
import sys
import time
from pathlib import Path

import numpy as np

T0 = time.monotonic()
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TRIM_SUPPLY = HERE.parent / "2026-09-27-issue-200-trim-supply" / "trim_supply.py"
DRP_S1 = Path(r"C:\unsung-fast\drp-stage3a\graph-drp-s1.bin")
DRP_S1_SHA = "418fe6660795f735c7dfe1960e65300c15f4401db2a15186fb6439d646dda15f"
DRP_G3_JSON = HERE.parent / "2026-09-27-drp-stage3a" / "drp_g3.json"
CENTRE_CUT, BAR = 0.99, 0.9
GROUPS = ("K", "KL", "D", "DH", "DS1")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def refuse(msg: str, code: int) -> None:
    print(f"REFUSING (dxq): {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


# ---- identity of this script's own input, FIRST -------------------------------------------------
s1_sha = sha256_of(DRP_S1)
s1_side = json.loads(DRP_S1.with_name(DRP_S1.name + ".json").read_text(encoding="utf-8"))["sha256"]
if not (s1_sha == s1_side == DRP_S1_SHA):
    refuse(f"graph-drp-s1.bin sha256 {s1_sha}; sidecar {s1_side}; pin {DRP_S1_SHA}", 2)
print(f"[dxq] sha256 OK  graph-drp-s1.bin {s1_sha} (== sidecar == pin)", flush=True)

sys.path.insert(0, str(REPO / "api" / "src"))
import artistpath_api.config as _cfgmod  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402

if (REPO / "api" / "src").resolve() not in Path(_cfgmod.__file__).resolve().parents:
    refuse(f"artistpath_api.config loaded from {_cfgmod.__file__}, not this worktree", 3)
cfg = ApiConfig()
W = {k: float(getattr(cfg, k)) for k in ("w_sim", "w_jump", "w_floor", "w_hop", "w_avoid",
                                         "w_degree_hub", "w_known_ramp_fame_pctl")}
print(f"[dxq] ApiConfig ({Path(_cfgmod.__file__).resolve()}): {W}", flush=True)
if W["w_degree_hub"] != 0.0:
    refuse(f"w_degree_hub = {W['w_degree_hub']} != 0.0; the price would rest on a degree the "
           "counterfactual changes (README, held constant)", 3)

# ---- the build and every reproduction assertion: trim_supply.py, unmodified ---------------------
print(f"[dxq] trim_supply.py sha256 {sha256_of(TRIM_SUPPLY)}; executing unmodified via runpy\n"
      f"{'-' * 100}", flush=True)
G = runpy.run_path(str(TRIM_SUPPLY))  # SystemExit (2/3) propagates
print(f"{'-' * 100}\n[dxq] trim_supply.py completed; computing DXQ- on its globals", flush=True)

CAP, S3, keep, remover = G["CAP"], G["S3"], G["keep"], G["remover"]
store, pctl, measured = G["store"], G["pctl"], G["measured"]
mbids, idx, nodes, served = G["mbids"], G["idx"], G["nodes"], G["served"]
trim_in, ranking, trim_out = CAP["trim_in"], CAP["ranking"], CAP["trim_out"]
strength = G["strength"]
m_before, m_after, g_sha = G["m_before"], G["m_after"], G["g_sha"]
N = store.artist_count
off = np.asarray(store.offsets, dtype=np.int64)
nb = np.asarray(store.neighbours, dtype=np.int64)
sc = np.asarray(store.scores, dtype=np.float32)
deg_served = np.diff(off)
pop = np.asarray(store.pop_raw, dtype=np.float32).astype(np.float64)

centre_idx = [int(i) for i in np.flatnonzero(measured & (pctl >= CENTRE_CUT))]
centres = [mbids[i] for i in centre_idx]
centre_set = set(centres)
print(f"[dxq] centres (measured fame_lb_pctl >= {CENTRE_CUT}): {len(centres)}", flush=True)

# ---- DRP-S1 added edges -------------------------------------------------------------------------
from artistpath_api.graph_store import GraphStore  # noqa: E402

s1_bytes = DRP_S1.read_bytes()
if sha256_bytes(s1_bytes) != DRP_S1_SHA:
    refuse("graph-drp-s1.bin bytes read != pin", 2)
s1 = GraphStore.from_bytes(s1_bytes)
del s1_bytes
s1_mbids = list(s1.mbids)
s1_off = np.asarray(s1.offsets, dtype=np.int64)
s1_nb = np.asarray(s1.neighbours, dtype=np.int64)
s1_map = np.array([idx.get(m, -1) for m in s1_mbids], dtype=np.int64)
if (s1_map < 0).any():
    refuse(f"{int((s1_map < 0).sum())} graph-drp-s1.bin nodes not in lba-a6", 3)


def pair_codes(o, n, mapping=None):
    src = np.repeat(np.arange(len(o) - 1, dtype=np.int64), np.diff(o))
    dst = n
    if mapping is not None:
        src, dst = mapping[src], mapping[dst]
    a, b = np.minimum(src, dst), np.maximum(src, dst)
    return np.unique(a * N + b)


lba_pairs = pair_codes(off, nb)
s1_pairs = pair_codes(s1_off, s1_nb, s1_map)
added = np.setdiff1d(s1_pairs, lba_pairs, assume_unique=True)
del s1, s1_off, s1_nb, lba_pairs, s1_pairs
added_by_centre: dict[str, set[str]] = {c: set() for c in centres}
added_no_centre = 0
added_touching = 0
for code in added.tolist():
    a, b = mbids[code // N], mbids[code % N]
    hit = False
    for c, v in ((a, b), (b, a)):
        if c in centre_set:
            added_by_centre[c].add(v)
            hit = True
    if hit:
        added_touching += 1
    else:
        added_no_centre += 1
drp_c10 = json.loads(DRP_G3_JSON.read_text(encoding="utf-8"))["DRP-C10"]["added_edges"]
print(f"[dxq] graph-drp-s1.bin edges not in lba-a6: {len(added):,}; touching a centre "
      f"{added_touching:,}; touching none {added_no_centre:,}; DRP-C10 (drp_g3.json) added_edges "
      f"{drp_c10:,}", flush=True)

# ---- per-edge records ---------------------------------------------------------------------------
MEAS = ("capv", "lscore", "sim", "deg_served", "deg_pre", "m3b", "fame", "rank", "rank_frac",
        "m7", "floor_ub")
REC = {g: {m: [] for m in MEAS + ("cidx",)} for g in GROUPS}
excl = {"K_null_fame": 0, "deleted_null_fame": 0, "deleted_non_node": 0}
deg_pre_cache: dict[str, int] = {}
m3b_cache: dict[str, int] = {}
a1_checked = a1_fail = 0
a2_miss = {"D": 0, "DS1": 0, "K": 0}
a3_fail = 0
max_lscore_dev = 0.0
per_centre: list[dict] = []
diag_neg_gap_centres = {"sim": [], "capv": []}
a4_fail = {"sim": 0, "capv": 0}


def emitted(c: str, v: str) -> float:
    return max(trim_in[c].get(v, 0.0), trim_in[v].get(c, 0.0))


for ci, (c, c_i) in enumerate(zip(centres, centre_idx)):
    # DXQ-A1 on every kept edge (all served neighbours, whatever their fame)
    row = range(off[c_i], off[c_i + 1])
    for e in row:
        v = mbids[nb[e]]
        a1_checked += 1
        if np.float32(emitted(c, v)) != sc[e]:
            a1_fail += 1
    ranked = sorted(ranking[c], key=lambda d: (-ranking[c][d], d))
    rank_of = {d: r + 1 for r, d in enumerate(ranked)}
    L = len(ranked)
    s4 = set(trim_out[c])
    s5 = served(c_i)
    if s4 != s5:
        refuse(f"S4 != S5 at centre {c}", 3)
    deleted = S3[c] - s4
    groups: dict[str, list[str]] = {"K": [], "KL": [], "D": [], "DH": [], "DS1": []}
    n_k_null = n_del_null = n_del_nonnode = 0
    for v in sorted(s5):
        if not measured[idx[v]]:
            n_k_null += 1
            continue
        groups["K"].append(v)
        if pctl[idx[v]] < BAR:
            groups["KL"].append(v)
    nbr_deleted_below = 0
    for v in sorted(deleted):
        i = idx.get(v)
        if i is None:
            n_del_nonnode += 1
            continue
        if not measured[i]:
            n_del_null += 1
            continue
        if pctl[i] < BAR:
            groups["D"].append(v)
            if remover.get((c, v)) == v:
                nbr_deleted_below += 1
        else:
            groups["DH"].append(v)
    dset = set(groups["D"])
    for v in added_by_centre[c]:
        if v not in dset:
            a3_fail += 1
    groups["DS1"] = sorted(added_by_centre[c] & dset)
    excl["K_null_fame"] += n_k_null
    excl["deleted_null_fame"] += n_del_null
    excl["deleted_non_node"] += n_del_nonnode

    vals: dict[str, dict[str, list[float]]] = {}
    for g, members in groups.items():
        vals[g] = {m: [] for m in MEAS}
        for v in members:
            vi = idx[v]
            capv = strength(c, v)
            ls_f = math.expm1(capv)
            ls = round(ls_f)
            max_lscore_dev = max(max_lscore_dev, abs(ls_f - ls))
            sim = float(np.float32(emitted(c, v)))
            if v not in deg_pre_cache:
                deg_pre_cache[v] = len(S3.get(v, set()) & nodes)
                m3b_cache[v] = len(keep.get(v, set()) & centre_set)
            r = rank_of.get(v)
            if r is None and g in a2_miss:
                a2_miss[g] += 1
            rec = {
                "capv": capv, "lscore": float(ls), "sim": sim,
                "deg_served": float(deg_served[vi]), "deg_pre": float(deg_pre_cache[v]),
                "m3b": float(m3b_cache[v]), "fame": float(pctl[vi]),
                "rank": float(r) if r is not None else math.nan,
                "rank_frac": r / L if r is not None else math.nan,
                "m7": W["w_sim"] * (1.0 - sim) + W["w_jump"] * abs(pop[c_i] - pop[vi]) + W["w_hop"],
                "floor_ub": W["w_floor"] * max(0.0, pop[c_i] - pop[vi]),
            }
            for m, x in rec.items():
                vals[g][m].append(x)
                REC[g][m].append(x)
            REC[g]["cidx"].append(ci)

    # DXQ-M6 / DXQ-A4
    pc = {"centre_mbid": c, "fame_lb_pctl": float(pctl[c_i]), "ranked_list_len": L,
          "K_null_fame_excluded": n_k_null, "deleted_null_fame_excluded": n_del_null,
          "deleted_non_node_excluded": n_del_nonnode,
          "D_deleted_by_neighbour_ceiling": nbr_deleted_below}
    for g in GROUPS:
        pc[f"n_{g}"] = len(groups[g])
    for cur in ("sim", "capv"):
        if groups["K"] and groups["D"]:
            gap = min(vals["K"][cur]) - max(vals["D"][cur])
            pc[f"M6_gap_{cur}"] = gap
            if gap < 0:
                diag_neg_gap_centres[cur].append(c)
                if nbr_deleted_below == 0:
                    a4_fail[cur] += 1
        else:
            pc[f"M6_gap_{cur}"] = math.nan
        pc[f"M6_K_spread_{cur}"] = (max(vals["K"][cur]) - min(vals["K"][cur])) if groups["K"] else math.nan
    # DXQ-M5: best-ranked deleted exit
    dr = [x for x in vals["D"]["rank"] if not math.isnan(x)]
    pc["M5_best_D_rank"] = min(dr) if dr else math.nan
    # DXQ-M8
    if groups["D"] and groups["K"]:
        j = min(range(len(groups["K"])), key=lambda t: (vals["K"]["m7"][t], groups["K"][t]))
        m7e, fe = vals["K"]["m7"][j], vals["K"]["fame"][j]
        pc["M8_estar_mbid"] = groups["K"][j]
        ks = []
        for m7v, fv in zip(vals["D"]["m7"], vals["D"]["fame"]):
            den = W["w_known_ramp_fame_pctl"] * (fe - fv)
            ks.append((m7v - m7e) / den if den > 0 else math.inf)
        pc["M8_kstar_min"] = min(ks)
    else:
        pc["M8_estar_mbid"] = ""
        pc["M8_kstar_min"] = math.nan
    # per-centre medians
    for g in GROUPS:
        for m in MEAS:
            a = np.asarray([x for x in vals[g][m] if not math.isnan(x)], dtype=float)
            pc[f"med_{g}_{m}"] = float(np.median(a)) if len(a) else math.nan
    per_centre.append(pc)

# ---- assertions ---------------------------------------------------------------------------------
print(f"\n[dxq] DXQ-A1 emitted similarity (float32) == served score on every kept edge at every "
      f"centre: {a1_fail == 0} ({a1_checked:,} edges checked, {a1_fail} mismatches)")
print(f"[dxq] DXQ-A2 deleted exits not in the centre's own ranked list: D {a2_miss['D']}, "
      f"DS1 {a2_miss['DS1']} (expected 0); K (reference, M5) {a2_miss['K']}")
print(f"[dxq] DXQ-A3 added edges touching a centre that are not in that centre's DXQ-D: {a3_fail} "
      f"(edges touching a centre {added_touching:,}; DRP-C10 added_edges {drp_c10:,})")
print(f"[dxq] DXQ-A4 negative-gap centres with no below-0.9 edge deleted by the neighbour's "
      f"ceiling: sim {a4_fail['sim']}, cap ranking value {a4_fail['capv']} (negative-gap centres: "
      f"sim {len(diag_neg_gap_centres['sim'])}, capv {len(diag_neg_gap_centres['capv'])})")
print(f"[dxq] listening score reconstructed as round(expm1(cap ranking value)): max |deviation| "
      f"{max_lscore_dev:.3g}", flush=True)
if a1_fail:
    refuse("DXQ-A1 failed", 3)
if a3_fail:
    refuse("DXQ-A3 failed", 3)
if a4_fail["sim"] or a4_fail["capv"]:
    refuse("DXQ-A4 failed", 3)


# ---- summaries ----------------------------------------------------------------------------------
def qt(a: np.ndarray, p: float) -> float:
    """numpy 'linear' percentile, defined where +inf is present (an inf bracket gives inf)."""
    a = np.sort(np.asarray(a, dtype=float))
    n = len(a)
    if n == 0:
        return math.nan
    h = (n - 1) * p / 100.0
    lo = int(math.floor(h))
    hi = min(lo + 1, n - 1)
    t = h - lo
    if t == 0 or a[lo] == a[hi]:
        return float(a[lo])
    if math.isinf(a[lo]) or math.isinf(a[hi]):
        return math.inf
    return float(a[lo] + t * (a[hi] - a[lo]))


def pooled(a) -> dict:
    a = np.asarray([x for x in a if not math.isnan(x)], dtype=float)
    if not len(a):
        return {"n": 0}
    return {"median": qt(a, 50), "p10": qt(a, 10), "p25": qt(a, 25), "p75": qt(a, 75),
            "p90": qt(a, 90), "mean": float(a.mean()), "n": int(len(a))}


def across(a) -> dict:
    a = np.asarray([x for x in a if not math.isnan(x)], dtype=float)
    return {"median": qt(a, 50), "p10": qt(a, 10), "p90": qt(a, 90), "n_centres": int(len(a))}


def centre_meds(g: str, m: str) -> np.ndarray:
    return np.asarray([pc[f"med_{g}_{m}"] for pc in per_centre], dtype=float)


def paired(g_other: str, m: str) -> dict:
    d = centre_meds("D", m) - centre_meds(g_other, m)
    d = d[~np.isnan(d)]
    out = across(d)
    out["share_negative"] = float((d < 0).mean()) if len(d) else math.nan
    return out


MEASURE_GROUPS = {
    "M1_cap_ranking_value": ("capv", GROUPS), "M1_listening_score": ("lscore", GROUPS),
    "M2_emitted_similarity": ("sim", GROUPS),
    "M3a_served_degree": ("deg_served", GROUPS), "M3a_pre_ceiling_degree": ("deg_pre", GROUPS),
    "M3b_centres_in_own_top50": ("m3b", ("D", "KL", "DS1")),
    "M4_fame_percentile": ("fame", GROUPS),
    "M5_rank_in_centre_list": ("rank", ("D", "DS1", "K")),
    "M5_rank_over_list_length": ("rank_frac", ("D", "DS1", "K")),
    "M7_router_price": ("m7", GROUPS), "M7_floor_upper_bound": ("floor_ub", GROUPS),
}
COMPARE = ("KL", "DH", "K", "DS1")
RES: dict = {"groups": {}, "comparisons": {}}
for name, (m, gs) in MEASURE_GROUPS.items():
    RES["groups"][name] = {}
    for g in gs:
        RES["groups"][name][g] = {"centre_weighted": across(centre_meds(g, m)),
                                  "pooled": pooled(REC[g][m])}
    RES["comparisons"][name] = {f"D_minus_{o}": paired(o, m) for o in COMPARE if o in gs}

# extras
SIM_BINS = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
for g in GROUPS:
    a = np.asarray(REC[g]["sim"])
    sh = {f"[{lo}, {hi})": float(((a >= lo) & (a < hi)).mean()) if len(a) else math.nan
          for lo, hi in SIM_BINS}
    sh["exactly 1.0"] = float((a == 1.0).mean()) if len(a) else math.nan
    RES["groups"]["M2_emitted_similarity"][g]["pooled_bin_shares"] = sh
    f = np.asarray(REC[g]["fame"])
    RES["groups"]["M4_fame_percentile"][g]["pooled_band_shares"] = {
        f"[{lo}, {hi})": float(((f >= lo) & (f < hi)).mean()) if len(f) else math.nan
        for lo, hi in ((0.8, 0.9), (0.5, 0.8), (0.0, 0.5))}
for g in ("D", "KL", "DS1"):
    a = np.asarray(REC[g]["m3b"])
    RES["groups"]["M3b_centres_in_own_top50"][g]["pooled_share_ge_10"] = \
        float((a >= 10).mean()) if len(a) else math.nan
RANK_BUCKETS = [(1, 50), (51, 100), (101, 250), (251, 500), (501, 1000), (1001, math.inf)]
for g in ("D", "DS1", "K"):
    a = np.asarray([x for x in REC[g]["rank"] if not math.isnan(x)])
    RES["groups"]["M5_rank_in_centre_list"][g]["pooled_bucket_shares"] = {
        ("> 1000" if math.isinf(hi) else f"{lo}-{hi}"): float(((a >= lo) & (a <= hi)).mean())
        if len(a) else math.nan for lo, hi in RANK_BUCKETS}
RES["groups"]["M5_rank_in_centre_list"]["best_ranked_D_exit_per_centre"] = across(
    [pc["M5_best_D_rank"] for pc in per_centre])


def gap_summary(key: str) -> dict:
    a = np.asarray([pc[key] for pc in per_centre], dtype=float)
    a = a[~np.isnan(a)]
    out = across(a)
    out["share_exactly_0"] = float((a == 0).mean()) if len(a) else math.nan
    out["share_negative"] = float((a < 0).mean()) if len(a) else math.nan
    return out


RES["M6"] = {cur: {"gap_weakest_kept_minus_strongest_deleted": gap_summary(f"M6_gap_{cur}"),
                   "K_spread_strongest_minus_weakest_kept": gap_summary(f"M6_K_spread_{cur}")}
             for cur in ("sim", "capv")}
RES["M6"]["A4"] = {"negative_gap_centres_sim": len(diag_neg_gap_centres["sim"]),
                   "negative_gap_centres_capv": len(diag_neg_gap_centres["capv"]),
                   "violations_sim": a4_fail["sim"], "violations_capv": a4_fail["capv"]}

kst = np.asarray([pc["M8_kstar_min"] for pc in per_centre], dtype=float)
n_D_noK = sum(1 for pc in per_centre if pc["n_D"] and not pc["n_K"])
kst = kst[~np.isnan(kst)]
M8 = {"centres_with_D": int(sum(1 for pc in per_centre if pc["n_D"])),
      "centres_with_D_but_no_K_excluded": n_D_noK,
      "w_known_ramp_fame_pctl": W["w_known_ramp_fame_pctl"]}
for lab, div in (("1x", 1.0), ("2x", 2.0), ("3x", 3.0)):
    a = kst / div
    s = across(a)
    s["share_le_10"] = float((a <= 10).mean()) if len(a) else math.nan
    s["share_le_20"] = float((a <= 20).mean()) if len(a) else math.nan
    s["share_finite"] = float(np.isfinite(a).mean()) if len(a) else math.nan
    M8[lab] = s
M8["diagnostic_centres_kstar_le_0"] = int((kst <= 0).sum())
RES["M8"] = M8


# ---- print --------------------------------------------------------------------------------------
def f(x) -> str:
    if isinstance(x, float):
        if math.isinf(x):
            return "inf"
        if math.isnan(x):
            return "nan"
        return f"{x:.4f}"
    return str(x)


print(f"\n{'=' * 100}\n## DXQ- summaries (centres {len(centres)})")
print(f"exclusions: {excl}")
for name, block in RES["groups"].items():
    print(f"\n### {name}")
    for g, s in block.items():
        if g == "best_ranked_D_exit_per_centre":
            print(f"  best-ranked D exit per centre: " + "  ".join(f"{k} {f(v)}" for k, v in s.items()))
            continue
        cw, po = s["centre_weighted"], s["pooled"]
        print(f"  {g:4s} centre-weighted: " + "  ".join(f"{k} {f(v)}" for k, v in cw.items()))
        print(f"       pooled:          " + "  ".join(f"{k} {f(v)}" for k, v in po.items()))
        for extra in ("pooled_bin_shares", "pooled_band_shares", "pooled_share_ge_10",
                      "pooled_bucket_shares"):
            if extra in s:
                v = s[extra]
                print(f"       {extra}: " + ("  ".join(f"{k} {f(x)}" for k, x in v.items())
                                             if isinstance(v, dict) else f(v)))
    for cmp_, s in RES["comparisons"][name].items():
        print(f"  paired {cmp_}: " + "  ".join(f"{k} {f(v)}" for k, v in s.items()))
print("\n### M6")
for cur in ("sim", "capv"):
    for k2, s in RES["M6"][cur].items():
        print(f"  {cur} {k2}: " + "  ".join(f"{k} {f(v)}" for k, v in s.items()))
print(f"  A4: {RES['M6']['A4']}")
print("\n### M8")
for k2, v in RES["M8"].items():
    print(f"  {k2}: " + ("  ".join(f"{k} {f(x)}" for k, x in v.items()) if isinstance(v, dict) else f(v)))


# ---- write --------------------------------------------------------------------------------------
def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        x = float(o)
        return "inf" if math.isinf(x) else (None if math.isnan(x) else x)
    if isinstance(o, np.integer):
        return int(o)
    return o


out = {
    "identity": {"graph-lba-a6.bin": g_sha, "S4-A6 MANIFEST.json before": m_before,
                 "S4-A6 MANIFEST.json after": m_after, "graph-drp-s1.bin": s1_sha,
                 "trim_supply.py": sha256_of(TRIM_SUPPLY)},
    "api_config_weights": W,
    "centres": len(centres),
    "exclusions": excl,
    "assertions": {"A1": {"pass": a1_fail == 0, "edges_checked": a1_checked, "mismatches": a1_fail},
                   "A2": {"misses_D": a2_miss["D"], "misses_DS1": a2_miss["DS1"],
                          "misses_K_reference": a2_miss["K"]},
                   "A3": {"pass": a3_fail == 0, "violations": a3_fail,
                          "added_edges_total": int(len(added)),
                          "added_edges_touching_a_centre": added_touching,
                          "added_edges_touching_no_centre": added_no_centre,
                          "DRP_C10_added_edges": drp_c10},
                   "A4": RES["M6"]["A4"]},
    "listening_score_reconstruction_max_dev": max_lscore_dev,
    "results": RES,
}
(HERE / "dxq_results.json").write_text(json.dumps(clean(out), indent=1) + "\n", encoding="utf-8",
                                       newline="\n")
cols = list(per_centre[0].keys())
with (HERE / "dxq_centres.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for pc in per_centre:
        w.writerow({k: ("inf" if isinstance(v, float) and math.isinf(v) else
                        "" if isinstance(v, float) and math.isnan(v) else v) for k, v in pc.items()})
print(f"\n[dxq] wrote dxq_results.json sha256 {sha256_of(HERE / 'dxq_results.json')}")
print(f"[dxq] wrote dxq_centres.csv sha256 {sha256_of(HERE / 'dxq_centres.csv')}")
print(f"[dxq] wall time {(time.monotonic() - T0) / 60:.1f} min")
