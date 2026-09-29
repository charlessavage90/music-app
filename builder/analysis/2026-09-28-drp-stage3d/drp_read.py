"""DRP- stage 3d: every criterion, gate and read of the #200 lattice, from the committed cell JSON.

Governing document: docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md
(`DRP-`), executed from the body: §3 (currency, nulls), §4 (pair sets, the uniform drop rule), §5
(criteria DRP-C1..C13), §6 (DRP-G8, the one gate recorded at *complete*), §7 (outcomes and the reads
DRP-R0..R13), §2.4 (the jump-relaxation deferral condition), §2.7 (the floor-attribution flag),
§2.10 (DRP-SW's trigger). Choices the body leaves to 3d are fixed in the stage-3d execution log,
task 1, committed before this script first ran; each is cited below as "3d choice N".

Routes nothing. Reads the eight committed cell files (identity checked against the shas the stage-3b
and stage-3c READMEs pin, after CRLF->LF normalisation: autocrlf checkouts hash differently), stage
3a's pair draw, N_noise and headroom files, and stage 3c's frontier count. Loads both map artifacts
read-only, sha-verified, for the fame frame (lba-a6's, one ruler for every cell by DRP-G3) and the
added-edge set.

Sealing (§8): node ids, pair indices and counts only. No artist is named.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-28-drp-stage3d/drp_read.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
STAGE3B = HERE.parent / "2026-09-28-drp-stage3b"
STAGE3C = HERE.parent / "2026-09-28-drp-stage3c"
sys.path.insert(0, str(STAGE3B))
from drp_sweep import CELLS, CELLS_DIR, RULES, SETS, STAGE3A, load_map  # noqa: E402
import drp_common as dc  # noqa: E402
from drp_common import BAND, BOOT_N, BOOT_SEED, FAMOUS, MAX_K  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.evaluation import top_degree_node_set  # noqa: E402

OUT_JSON = HERE / "drp_results.json"

# The committed LF shas, as the stage-3b README (DRP-S0 row) and stage-3c README (DRP-S1 row) pin them.
CELL_SHA = {
    "DRP-S0P0": "339998556fcd91f9287a026746e2fe7185cbaa44eb25129135a61b35d588a113",
    "DRP-S0P1": "f4dd248ddee3969a790a2857c430289dad7777906a104e58054a7949a3ea1aac",
    "DRP-S0P2": "d54dd214dd707db966bb81596ba7419413211c40b1a4171bca47a4b0ca327ffe",
    "DRP-S0P3": "25262a0a9baf2a4bd23159b35b8f4216baa8ed437567933f4a04d5e10039e006",
    "DRP-S1P0": "a35b9fd3a0e61bc91dd9ded4c3f083d2b390bf6532a42e05e8c2353837ca42b9",
    "DRP-S1P1": "113b8d926cb4a031eacfc7f411ffcef98eb9f842bc7d8667db1f154a90623814",
    "DRP-S1P2": "a8fb47ef4bd77ff28331488635be991e1ffdf65161f7201527435afdea44e78e",
    "DRP-S1P3": "2937eee2a38026259d3a9e3d50b8b4cca58a6d50f7e1cd11789303268400d4ad",
}
FRONTIER_SHA = "a99f793d6239a2bb3ec69e1d23cdd5f3502b9bd6fad80b3cc784408719e94669"
A0 = "DRP-S0P0"
NON_ANCHOR = [c for c in CELLS if c != A0]
# §2.2's isolating baselines, one column away.
BASELINES = {
    "DRP-S0P1": ["DRP-S0P0"], "DRP-S0P2": ["DRP-S0P1"], "DRP-S1P0": ["DRP-S0P0"],
    "DRP-S1P1": ["DRP-S1P0", "DRP-S0P1"], "DRP-S1P2": ["DRP-S1P1", "DRP-S0P2"],
    "DRP-S0P3": ["DRP-S0P0"], "DRP-S1P3": ["DRP-S1P0", "DRP-S0P3"],
}
BAR_D = -0.05          # DRP-C1 conjunct 1
BAR_C2 = 0.70          # DRP-C2
C6_QUARTER = 0.25      # DRP-C6 floor
C6_MIN_A0 = 4          # DRP-AM5-I12 guard
G8_MIN = 30            # DRP-G8
SW_BAR = 0.90          # DRP-SW trigger
FLOOR_PP = 0.10        # §2.7 floor-attribution flag
C4_RISE = 0.05         # §3 / CRE- §0.4 trigger
R13_MISSING = 0.05     # DRP-R13
TOP_FAME = 0.99        # DRP-C6
# DRP-R9(v)'s yardsticks (3d choice 7): CRE critique F7's realised median w_sim*(1-sim) on chosen
# edges at presses 10-20, builder/analysis/2026-08-03-cre-prereg-critique/cre-analyst-critique.md:213.
CRE_F7_RAMP_003 = 0.6466
CRE_F7_RAMP_010 = 1.1331


def lf_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def med(xs) -> float:
    xs = [x for x in xs if x == x]
    return float(np.median(xs)) if xs else float("nan")


def rnd(x, n=5):
    if x is None:
        return None
    if isinstance(x, float):
        return None if x != x else round(x, n)
    return x


# ---- loading -----------------------------------------------------------------------------------
def load_cells() -> dict:
    cells = {}
    for cell, spec in CELLS.items():
        path = CELLS_DIR / f"{cell}.json"
        got = lf_sha(path)
        if got != CELL_SHA[cell]:
            dc.refuse(f"{cell}: LF sha {got} != pinned {CELL_SHA[cell]}")
        obj = json.loads(path.read_text(encoding="utf-8"))
        if obj["cell"] != cell or obj["supply"] != spec["supply"] or obj["pricing"] != spec["pricing"]:
            dc.refuse(f"{cell}: header does not match drp_sweep.CELLS")
        idx = {}
        for p in obj["pairs"]:
            for k, d in enumerate(p["depths"]):
                if d["k"] != k:
                    dc.refuse(f"{cell}: depth record out of order")
            idx[(p["set"], p["rule"], p["i"])] = p
        if len(idx) != len(SETS) * len(RULES) * 40:
            dc.refuse(f"{cell}: {len(idx)} (set, rule, pair) records")
        cells[cell] = {"obj": obj, "idx": idx}
        print(f"cell OK  {cell}  LF sha {got[:12]}…  graph {obj['graph_sha256'][:8]}", flush=True)
    return cells


def feasible(p: dict, k: int) -> bool:
    """§4: infeasible if the journey is None, has no interior, or the ladder has stopped."""
    ds = p["depths"]
    return k < len(ds) and ds[k]["path"] is not None and len(ds[k]["path"]) > 2


def path_at(p: dict, k: int):
    return p["depths"][k]["path"] if feasible(p, k) else None


# ---- §4: the uniform drop rule (3d choice 1) ---------------------------------------------------
def drop_set(cells: dict) -> set:
    union = set()
    for cell, c in cells.items():
        listed = {tuple(x) for x in c["obj"]["dropped_in_this_cell"]}
        mine = set()
        for (s, r, i), p in c["idx"].items():
            for k in range(MAX_K + 1):
                if not feasible(p, k):
                    mine.add((s, r, i, k))
        if listed != mine:
            dc.refuse(f"{cell}: dropped_in_this_cell ({len(listed)}) != recomputed ({len(mine)}): "
                      f"{sorted(listed ^ mine)[:5]}")
        union |= listed
    return union


def survives(drop: set, s: str, r: str, i: int, ks) -> bool:
    return all((s, r, i, k) not in drop for k in ks)


def band_pairs(drop: set, s: str, r: str) -> list[int]:
    """Pairs entering the band statistic: all four band depths, and depth 0, survive in all eight."""
    out = [i for i in range(40) if survives(drop, s, r, i, (0,) + BAND)]
    return out


# ---- the fame reads ----------------------------------------------------------------------------
class Frame:
    def __init__(self, m: dc.Map) -> None:
        self.pl = m.pl
        self.measured = m.measured

    def vals(self, path) -> list[float]:
        return [self.pl[v] for v in path[1:-1] if self.measured[v]]

    def M(self, p: dict, ks) -> float:
        """§5: median fame_lb_pctl over the pooled interior slots of the depths (measured only, §3)."""
        pooled = []
        for k in ks:
            pooled += self.vals(p["depths"][k]["path"])
        return float(np.median(pooled)) if pooled else float("nan")

    def top(self, path) -> float:
        """DRP-C11's X: highest interior, shipped pctl with nulls at 0.0 (DRP-AM5-O2)."""
        return max(self.pl[v] for v in path[1:-1])


def bootstrap_ub(D: np.ndarray) -> float:
    """DRP-C1(2), pinned by DRP-AM1-F3."""
    n = len(D)
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, n, size=(BOOT_N, n))
    return float(np.percentile(np.median(D[idx], axis=1), 95))


def loo(D: np.ndarray) -> list[float]:
    ms = [float(np.median(np.delete(D, j))) for j in range(len(D))]
    return [min(ms), max(ms)]


def c1_block(F: Frame, cells, drop, cell, s, r, n_noise) -> dict:
    """DRP-C1's D and G per pair, its conjunction, and item 4's companions (also used for C7, C8)."""
    pairs = band_pairs(drop, s, r)
    D, G, head, rows = [], [], 0, []
    for i in pairs:
        pc, pa = cells[cell]["idx"][(s, r, i)], cells[A0]["idx"][(s, r, i)]
        mcb, mab = F.M(pc, BAND), F.M(pa, BAND)
        mc0, ma0 = F.M(pc, (0,)), F.M(pa, (0,))
        d, g = mcb - mab, (mcb - mc0) - (mab - ma0)
        if d != d or g != g:
            dc.refuse(f"{cell} {s} {r} pair {i}: band median unmeasurable (all-null interiors)")
        D.append(d)
        G.append(g)
        head += mab <= 1 - n_noise
        rows.append({"i": i, "D": rnd(d), "G": rnd(g)})
    D, G = np.array(D), np.array(G)
    n = len(D)
    out = {"n": n, "pairs": rows}
    if n == 0:
        return out
    mD, mG = float(np.median(D)), float(np.median(G))
    ub = bootstrap_ub(D)
    out.update({
        "median_D": rnd(mD), "median_G": rnd(mG), "boot_ub_D": rnd(ub),
        "conj1": mD <= BAR_D, "conj2": ub <= -n_noise, "conj3": mG <= -n_noise,
        "n_D_le_bar": int((D <= BAR_D).sum()), "n_absD_lt_noise": int((np.abs(D) < n_noise).sum()),
        "loo_median_D": [rnd(x) for x in loo(D)],
        "headroom_to_rise": head, "n_D_ge_plus_noise": int((D >= n_noise).sum()),
    })
    out["pass"] = out["conj1"] and out["conj2"] and out["conj3"]
    return out


def depth_D(F, cells, drop, cell, s, r, k) -> dict:
    """D and G at a single depth k, over pairs whose (pair, k) and (pair, 0) survive (3d choice 4)."""
    D, G = [], []
    for i in range(40):
        if not survives(drop, s, r, i, (0, k)):
            continue
        pc, pa = cells[cell]["idx"][(s, r, i)], cells[A0]["idx"][(s, r, i)]
        mck, mak, mc0, ma0 = F.M(pc, (k,)), F.M(pa, (k,)), F.M(pc, (0,)), F.M(pa, (0,))
        if mck == mck and mak == mak:
            D.append(mck - mak)
            G.append((mck - mc0) - (mak - ma0))
    return {"n": len(D), "median_D": rnd(med(D)), "median_G": rnd(med(G))}


# ---- companions --------------------------------------------------------------------------------
def c2(cells, drop, cell, s, pairs) -> dict:
    """DRP-C2: per pair, mean interior count over the band / interior count at press 0; median."""
    band, per_d = [], {k: [] for k in BAND}
    for i in pairs:
        p = cells[cell]["idx"][(s, "primary", i)]
        n0 = len(p["depths"][0]["path"]) - 2
        cnt = {k: len(p["depths"][k]["path"]) - 2 for k in BAND}
        band.append(np.mean([cnt[k] for k in BAND]) / n0)
        for k in BAND:
            per_d[k].append(cnt[k] / n0)
    return {"stat": med(band), "per_depth": {k: med(v) for k, v in per_d.items()}}


def c6(F, cells, cell, s) -> dict:
    """DRP-C6 per depth 0..20; gated at 0..3 (DRP-D4), guard DRP-AM5-I12, primary rule."""
    rows, fires, unreadable = {}, [], []
    for k in range(MAX_K + 1):
        den = cc = ca = 0
        for i in range(40):
            pc, pa = cells[cell]["idx"][(s, "primary", i)], cells[A0]["idx"][(s, "primary", i)]
            if not (feasible(pc, k) and feasible(pa, k)):
                continue
            den += 1
            cc += any(F.pl[v] >= TOP_FAME and F.measured[v] for v in pc["depths"][k]["path"][1:-1])
            ca += any(F.pl[v] >= TOP_FAME and F.measured[v] for v in pa["depths"][k]["path"][1:-1])
        sc, sa = (cc / den if den else float("nan")), (ca / den if den else float("nan"))
        row = {"den": den, "cell_count": cc, "a0_count": ca, "cell_share": rnd(sc), "a0_share": rnd(sa)}
        if k <= 3 and cell != A0:
            if ca < C6_MIN_A0:
                row["gate"] = "unreadable"
                unreadable.append(k)
            else:
                row["gate"] = "fires" if sc < C6_QUARTER * sa else "holds"
                if row["gate"] == "fires":
                    fires.append(k)
        rows[k] = row
    return {"per_depth": rows, "fires_at": fires, "unreadable_at": unreadable, "fires": bool(fires)}


def c3(cells, drop, cell, s, pairs_band, top_a0, top_cell) -> dict:
    groups = {"0-2": (0, 1, 2), "7-10": BAND, "20": (20,)}
    out = {}
    for name, ks in groups.items():
        slots = hit_a0 = hit_own = 0
        for i in range(40):
            if not survives(drop, s, "primary", i, ks):
                continue
            p = cells[cell]["idx"][(s, "primary", i)]
            for k in ks:
                for v in p["depths"][k]["path"][1:-1]:
                    slots += 1
                    hit_a0 += v in top_a0
                    hit_own += v in top_cell
        out[name] = {"slots": slots, "share_lba_a6_set": rnd(hit_a0 / slots if slots else float("nan")),
                     "share_own_set": rnd(hit_own / slots if slots else float("nan"))}
    return out


def c4(F, cells, drop, cell, s, pairs_band) -> dict:
    per = {}
    for k in range(MAX_K + 1):
        slots = nulls = 0
        for i in range(40):
            if not survives(drop, s, "primary", i, (k,)):
                continue
            for v in cells[cell]["idx"][(s, "primary", i)]["depths"][k]["path"][1:-1]:
                slots += 1
                nulls += not F.measured[v]
        per[k] = {"null": nulls, "slots": slots}

    def share(ks):
        sl = nl = 0
        for i in pairs_band:
            for k in ks:
                for v in cells[cell]["idx"][(s, "primary", i)]["depths"][k]["path"][1:-1]:
                    sl += 1
                    nl += not F.measured[v]
        return nl / sl if sl else float("nan")
    s0, sb = share((0,)), share(BAND)
    return {"per_depth": per, "share_d0": rnd(s0), "share_band": rnd(sb), "trigger": sb - s0 > C4_RISE}


def c9(cells, drop, cell, s, pairs_band, w_sim) -> dict:
    terms = ("sim", "jump", "floor", "avoid", "hub", "hop", "ramp")
    per = {}
    for k in range(MAX_K + 1):
        shares = {t: [] for t in terms}
        for i in range(40):
            if not survives(drop, s, "primary", i, (k,)):
                continue
            tt = cells[cell]["idx"][(s, "primary", i)]["depths"][k]["terms"]
            tot = sum(tt[t] for t in terms)
            for t in terms:
                shares[t].append(tt[t] / tot if tot else 0.0)
        per[k] = {t: rnd(float(np.mean(v)) if v else float("nan"), 4) for t, v in shares.items()}
    edges = [w_sim * (1 - x) for i in pairs_band for k in BAND
             for x in cells[cell]["idx"][(s, "primary", i)]["depths"][k]["sim_edges"]]
    return {"mean_term_share_per_depth": per, "band_median_wsim_cost": rnd(med(edges), 6),
            "band_edges": len(edges)}


def c11(F, cells, headroom, cell, s, pairs_band, n_noise) -> dict:
    sup = CELLS[cell]["supply"]
    b0 = {row["i"]: row["b0"] for row in headroom["maps"][sup]["strata"][s]}
    fr, nohead = [], 0
    for i in pairs_band:
        pc, pa = cells[cell]["idx"][(s, "primary", i)], cells[A0]["idx"][(s, "primary", i)]
        xc = float(np.median([F.top(pc["depths"][k]["path"]) for k in BAND]))
        xa = float(np.median([F.top(pa["depths"][k]["path"]) for k in BAND]))
        h = xa - b0[i]
        if h >= n_noise:
            fr.append((xa - xc) / h)
        else:
            nohead += 1
    return {"n_with_headroom": len(fr), "n_no_headroom": nohead,
            "median_fraction": rnd(med(fr)), "p25": rnd(float(np.percentile(fr, 25)) if fr else None),
            "p75": rnd(float(np.percentile(fr, 75)) if fr else None)}


def c12(F, cells, drop, cell, s, n_noise) -> dict:
    groups = {"1-6": range(1, 7), "7-10": range(7, 11), "11-20": range(11, 21)}
    out = {}
    for name, ks in groups.items():
        cnt = {"fell": 0, "rose": 0, "substituted": 0, "shortened": 0}
        for k in ks:
            for i in range(40):
                if not survives(drop, s, "primary", i, (k - 1, k)):
                    continue
                p = cells[cell]["idx"][(s, "primary", i)]
                a, b = F.M(p, (k - 1,)), F.M(p, (k,))
                if a != a or b != b:
                    continue
                dlt = b - a
                if dlt <= -n_noise:
                    cnt["fell"] += 1
                elif dlt >= n_noise:
                    cnt["rose"] += 1
                else:
                    prev = set(p["depths"][k - 1]["path"][1:-1])
                    new = any(v not in prev for v in p["depths"][k]["path"][1:-1])
                    cnt["substituted" if new else "shortened"] += 1
        tot = sum(cnt.values())
        out[name] = {"n": tot, **{kk: rnd(v / tot if tot else float("nan"), 4) for kk, v in cnt.items()}}
    return out


def c13(cells, drop, cell, s, pairs_band) -> dict:
    per = {}
    for k in range(MAX_K + 1):
        rs = []
        for i in range(40):
            if not survives(drop, s, "primary", i, (k,)):
                continue
            r = cells[cell]["idx"][(s, "primary", i)]["depths"][k]["r"]
            rs.append(r if r is not None else 0.0)
        per[k] = {"n": len(rs), "share_r_pos": rnd(float(np.mean([x > 0 for x in rs])) if rs else None, 4),
                  "median_r": rnd(med(rs))}
    pair_med = []
    for i in pairs_band:
        rr = [cells[cell]["idx"][(s, "primary", i)]["depths"][k]["r"] for k in BAND]
        if any(x is None for x in rr):
            dc.refuse(f"{cell} {s} pair {i}: r is None inside the band")
        pair_med.append(float(np.median(rr)))
    return {"per_depth": per, "band_median_of_pair_median_r": rnd(med(pair_med))}


def floor_share(cells, cell, s, pairs_band) -> float:
    hit = 0
    for i in pairs_band:
        p = cells[cell]["idx"][(s, "primary", i)]
        hit += any(p["depths"][k]["terms"]["floor"] > 0 for k in range(1, 7))
    return hit / len(pairs_band)


# ---- main --------------------------------------------------------------------------------------
def main() -> None:
    a0m = load_map("DRP-S0")
    s1m = load_map("DRP-S1")
    if a0m.mbids != s1m.mbids or not np.array_equal(a0m.pctl, s1m.pctl):
        dc.refuse("the two maps do not share one node set and frame (DRP-G3)")
    F = Frame(a0m)
    top_deg = {"DRP-S0": top_degree_node_set(a0m.store, 0.01), "DRP-S1": top_degree_node_set(s1m.store, 0.01)}
    added = set()
    for u in range(s1m.n):
        a_row = set(a0m.nbr[a0m.off[u]:a0m.off[u + 1]])
        for v in s1m.nbr[s1m.off[u]:s1m.off[u + 1]]:
            if v not in a_row:
                added.add((min(u, v), max(u, v)))
    g3 = json.loads((STAGE3A / "drp_g3.json").read_text(encoding="utf-8"))
    if len(added) != g3["DRP-C10"]["added_edges"]:
        dc.refuse("added-edge set does not match drp_g3.json")

    cells = load_cells()
    noise = json.loads((STAGE3A / "drp_noise.json").read_text(encoding="utf-8"))
    headroom = json.loads((STAGE3A / "drp_headroom.json").read_text(encoding="utf-8"))
    if lf_sha(STAGE3C / "drp_c10_frontier.json") != FRONTIER_SHA:
        dc.refuse("drp_c10_frontier.json sha mismatch")
    frontier = json.loads((STAGE3C / "drp_c10_frontier.json").read_text(encoding="utf-8"))
    gates = {row: json.loads((STAGE3B / f"drp_gates_{row}.json").read_text(encoding="utf-8"))
             for row in ("DRP-S0", "DRP-S1")}
    N = {s: noise["strata"][s]["N_noise"] if "N_noise" in noise["strata"][s] else None for s in FAMOUS}
    if any(v is None for v in N.values()):
        dc.refuse(f"N_noise not found in drp_noise.json strata: {list(noise['strata']['DRP-T1'])}")
    w_sim = ApiConfig().w_sim

    drop = drop_set(cells)
    res = {"what": "DRP- stage 3d: criteria, gates and reads over the eight swept cells (§5-§7)",
           "cell_sha256_lf": CELL_SHA, "lba_a6_sha256": a0m.sha, "drp_s1_sha256": s1m.sha,
           "N_noise": N, "drop_set_size": {r: sum(1 for x in drop if x[1] == r) for r in RULES},
           "drop_set": sorted(list(x) for x in drop)}

    # §7 run state *complete*: all eight swept (gate verdicts), N_noise measured, G8, drop set.
    res["swept_gate_verdicts"] = {row: g.get("verdict") for row, g in gates.items()}

    # DRP-G8
    g8 = {}
    for s in FAMOUS:
        n = len(band_pairs(drop, s, "primary"))
        g8[s] = {"band_readable": n, "readable": n >= G8_MIN}
    res["DRP-G8"] = g8
    print("DRP-G8", g8, flush=True)

    per = {}
    for cell in CELLS:
        per[cell] = {}
        for s in FAMOUS + ("DRP-MID",):
            pb = band_pairs(drop, s, "primary")
            nn = N.get(s, 0.015)
            blk = {"band_readable": len(pb)}
            if cell != A0:
                blk["DRP-C1"] = c1_block(F, cells, drop, cell, s, "primary", nn)
                blk["DRP-C1s"] = depth_D(F, cells, drop, cell, s, "primary", 20)
                blk["DRP-C7"] = c1_block(F, cells, drop, cell, s, "random", nn)
                blk["D_profile"] = {k: depth_D(F, cells, drop, cell, s, "primary", k) for k in range(MAX_K + 1)}
            blk["DRP-C2"] = c2(cells, drop, cell, s, pb)
            blk["DRP-C3"] = c3(cells, drop, cell, s, pb, top_deg["DRP-S0"], top_deg[CELLS[cell]["supply"]])
            blk["DRP-C4"] = c4(F, cells, drop, cell, s, pb)
            blk["DRP-C9"] = c9(cells, drop, cell, s, pb, w_sim)
            blk["M0_median"] = rnd(med([F.M(cells[cell]["idx"][(s, "primary", i)], (0,))
                                        for i in range(40) if survives(drop, s, "primary", i, (0,))]))
            if s in FAMOUS:
                blk["DRP-C6"] = c6(F, cells, cell, s)
                blk["DRP-C12"] = c12(F, cells, drop, cell, s, nn)
                blk["floor_share_presses_1_6"] = rnd(floor_share(cells, cell, s, pb), 4)
                if cell != A0:
                    blk["DRP-C11"] = c11(F, cells, headroom, cell, s, pb, nn)
                if CELLS[cell]["ceiling"]:
                    blk["DRP-C13"] = c13(cells, drop, cell, s, pb)
            per[cell][s] = blk
        # DRP-C8: the replication set, primary rule (N_noise: the lower of the two famous strata's
        # is the same 0.015 carried floor; drp_noise.json records no DRP-C8 value).
        if cell != A0:
            per[cell]["DRP-C8"] = {"DRP-C1": c1_block(F, cells, drop, cell, "DRP-C8", "primary", 0.015)}
        print(f"read {cell}", flush=True)

    # DRP-C2 binding ratio and one-column ratios
    for cell in NON_ANCHOR:
        for s in FAMOUS + ("DRP-MID",):
            b = per[cell][s]["DRP-C2"]
            a = per[A0][s]["DRP-C2"]
            b["ratio_vs_A0"] = rnd(b["stat"] / a["stat"])
            b["ratio_vs_baselines"] = {bl: rnd(b["stat"] / per[bl][s]["DRP-C2"]["stat"]) for bl in BASELINES[cell]}
            b["per_depth_ratio_vs_A0"] = {k: rnd(b["per_depth"][k] / a["per_depth"][k]) for k in BAND}
            b["binding_pass"] = b["stat"] / a["stat"] >= BAR_C2
            if CELLS[cell]["ceiling"]:
                b["per_depth_pass"] = all(b["per_depth"][k] / a["per_depth"][k] >= BAR_C2 for k in BAND)

    # §2.7 floor-attribution flag (3d choice 6)
    for cell in NON_ANCHOR:
        flag = {}
        for s in FAMOUS:
            me = per[cell][s]["floor_share_presses_1_6"]
            flag[s] = {bl: rnd(me - per[bl][s]["floor_share_presses_1_6"], 4) for bl in BASELINES[cell]}
        per[cell]["floor_attribution"] = {"diff_vs_baselines": flag,
                                          "fires": any(abs(v) >= FLOOR_PP for s in FAMOUS for v in flag[s].values())}

    # §7 per-cell outcome, per famous stratum (3d choice 11)
    outcomes = {}
    for cell in NON_ANCHOR:
        outcomes[cell] = {}
        for s in FAMOUS:
            blk, nn = per[cell][s], N[s]
            c1, c2b = blk["DRP-C1"], blk["DRP-C2"]
            c2ok = c2b["binding_pass"] and (c2b.get("per_depth_pass", True))
            if not g8[s]["readable"]:
                o = "UNREADABLE"
            elif blk["DRP-C6"]["fires"]:
                o = "ELIMINATES"
            elif c1["pass"]:
                o = "MOVES" if c2ok else "DELETION"
            elif c1["median_D"] >= nn:
                o = "RISES"
            elif c1["median_D"] <= -nn:
                o = "BELOW BAR"
            else:
                o = "NO MOVEMENT"
            q = []
            if c1["pass"] and abs(blk["DRP-C7"].get("median_D", 0.0)) < nn:
                q.append("i")
            c8 = per[cell]["DRP-C8"]["DRP-C1"]["median_D"]
            if c8 and c1["median_D"] and np.sign(c8) == -np.sign(c1["median_D"]):
                q.append("ii")
            if blk["DRP-C4"]["trigger"]:
                q.append("iii")
            if per[cell]["floor_attribution"]["fires"]:
                q.append("iv")
            if blk["DRP-C9"]["band_median_wsim_cost"] >= CRE_F7_RAMP_010:
                q.append("v")
            if o in ("NO MOVEMENT", "BELOW BAR") and c1["headroom_to_rise"] < c1["n"] / 2:
                q.append("vi")
            if CELLS[cell]["ceiling"]:
                q.append("vii")
            outcomes[cell][s] = {"outcome": o, "qualifiers": q}
    res["outcomes"] = outcomes

    # DRP-R8 for every MOVES cell
    r8 = {}
    for cell in NON_ANCHOR:
        for s in FAMOUS:
            if outcomes[cell][s]["outcome"] != "MOVES":
                continue
            dband = per[cell][s]["DRP-C1"]["median_D"]
            prof = per[cell][s]["D_profile"]
            step = all(abs(prof[k]["median_D"] - dband) < N[s] for k in range(3, MAX_K + 1)
                       if prof[k]["median_D"] is not None)
            r8[f"{cell} {s}"] = "step" if step else "gradient"
    res["DRP-R8"] = r8

    # DRP-R13 per supply level and famous stratum
    r13 = {}
    for sup, (p1, p2, p3) in {"DRP-S0": ("DRP-S0P1", "DRP-S0P2", "DRP-S0P3"),
                              "DRP-S1": ("DRP-S1P1", "DRP-S1P2", "DRP-S1P3")}.items():
        for s in FAMOUS:
            mr = per[p3][s]["DRP-C13"]["band_median_of_pair_median_r"]
            null_ramps = all(outcomes[c][s]["outcome"] in ("NO MOVEMENT", "BELOW BAR") for c in (p1, p2))
            if null_ramps and mr >= R13_MISSING:
                v = "missing supply"
            elif null_ramps and mr < N[s]:
                v = "pricing"
            else:
                v = "mixed"
            r13[f"{sup} {s}"] = {"median_r": mr, "ramp_cells_null": null_ramps, "read": v}
    res["DRP-R13"] = r13

    # DRP-SW trigger / DRP-C5's DRP-S1P0 half (3d choice 12)
    sw = {}
    for s in FAMOUS + ("DRP-MID",):
        den = same = via_added = 0
        shifts = []
        for i in range(40):
            pc, pa = cells["DRP-S1P0"]["idx"][(s, "primary", i)], cells[A0]["idx"][(s, "primary", i)]
            for c in ("DRP-S1P0", A0):
                if cells[c]["idx"][(s, "random", i)]["depths"][0]["path"] != cells[c]["idx"][(s, "primary", i)]["depths"][0]["path"]:
                    dc.refuse(f"{c} {s} {i}: press-0 journey differs between press rules")
            xc, xa = pc["depths"][0]["path"], pa["depths"][0]["path"]
            if xc is None or xa is None:
                continue
            den += 1
            if xc == xa:
                same += 1
            elif any((min(a, b), max(a, b)) in added for a, b in zip(xc, xc[1:])):
                via_added += 1
            mc, ma = F.M(pc, (0,)), F.M(pa, (0,))
            if mc == mc and ma == ma:
                shifts.append(mc - ma)
        share = same / den
        sw[s] = {"den": den, "identical": same, "share_identical": rnd(share, 4),
                 "changed_using_added_edge": via_added, "changed_without_added_edge": den - same - via_added,
                 "median_M0_shift": rnd(med(shifts))}
        if s in FAMOUS:
            sw[s]["fires"] = share < SW_BAR
    res["DRP-SW_trigger"] = {**sw, "DRP-R11_fires": any(sw[s]["fires"] for s in FAMOUS)}

    # DRP-C5 on DRP-MID: the first-path climb (3d choice 9), every cell
    c5mid = {}
    for cell in CELLS:
        top_above = med_above = den = 0
        for i in range(40):
            p = cells[cell]["idx"][("DRP-MID", "primary", i)]
            path = p["depths"][0]["path"]
            if path is None or len(path) <= 2:
                continue
            den += 1
            ends = max(F.pl[path[0]], F.pl[path[-1]])
            top_above += F.top(path) > ends
            m0 = F.M(p, (0,))
            med_above += m0 == m0 and m0 > ends
        c5mid[cell] = {"den": den, "top_above_both": top_above, "M0_above_both": med_above}
    res["DRP-C5_MID"] = c5mid

    # §2.4 deferral condition / DRP-C10 frontier (3d choice 2)
    fr = {}
    for cell in ("DRP-S1P0", "DRP-S1P1", "DRP-S1P2", "DRP-S1P3", A0):
        rows = {(r["set"], r["rule"], r["i"]): r for r in frontier["cells"][cell]}
        blk = {}
        pooled_all = pooled_int = pooled_n = 0
        for s in FAMOUS:
            pb = band_pairs(drop, s, "primary")
            a = sum(rows[(s, "primary", i)]["incident_all"] >= 1 for i in pb)
            b = sum(rows[(s, "primary", i)]["incident_interior"] >= 1 for i in pb)
            u = sum(rows[(s, "primary", i)]["used"] >= 1 for i in pb)
            blk[s] = {"n": len(pb), "with_exit_incident_all": a, "with_exit_incident_interior": b,
                      "traversing_an_added_edge": u}
            pooled_all, pooled_int, pooled_n = pooled_all + a, pooled_int + b, pooled_n + len(pb)
        blk["pooled"] = {"n": pooled_n, "share_incident_all": rnd(pooled_all / pooled_n, 4),
                         "share_incident_interior": rnd(pooled_int / pooled_n, 4)}
        fr[cell] = blk
    r0 = all(outcomes[c][s]["outcome"] != "MOVES" for c in NON_ANCHOR for s in FAMOUS)
    fr["deferral_condition"] = {
        "DRP-R0_fires": r0,
        "met_incident_all": r0 and fr["DRP-S1P0"]["pooled"]["share_incident_all"] >= 0.5,
        "met_incident_interior": r0 and fr["DRP-S1P0"]["pooled"]["share_incident_interior"] >= 0.5}
    res["DRP-C10_frontier"] = fr

    # §7 reads, mechanically
    mv = {c: {s: outcomes[c][s]["outcome"] == "MOVES" for s in FAMOUS} for c in NON_ANCHOR}
    reads = {"DRP-R0": r0}
    for s in FAMOUS:
        s1p0, s0p1, s0p2 = mv["DRP-S1P0"][s], mv["DRP-S0P1"][s], mv["DRP-S0P2"][s]
        crossed = mv["DRP-S1P1"][s] or mv["DRP-S1P2"][s]
        reads[f"DRP-R1 {s}"] = s1p0 and not (s0p1 or s0p2)
        reads[f"DRP-R2 {s}"] = (s0p1 or s0p2) and not s1p0
        reads[f"DRP-R3 {s}"] = crossed and not (s1p0 or s0p1 or s0p2)
        reads[f"DRP-R4 {s}"] = s1p0 and (s0p1 or s0p2)
    reads["DRP-R5"] = [c for c in NON_ANCHOR if mv[c]["DRP-T1"] != mv[c]["DRP-T2"]]
    reads["DRP-R6"] = [f"{c} {s}" for c in NON_ANCHOR for s in FAMOUS if outcomes[c][s]["outcome"] == "DELETION"]
    reads["DRP-R7"] = [f"{c} {s}" for c in NON_ANCHOR for s in FAMOUS if outcomes[c][s]["outcome"] == "ELIMINATES"]
    reads["DRP-R11"] = res["DRP-SW_trigger"]["DRP-R11_fires"]
    reads["DRP-R12"] = [f"{c} {s}" for c in ("DRP-S0P3", "DRP-S1P3") for s in FAMOUS if mv[c][s]]
    reads["succeeds_on_famous_pairs"] = [c for c in NON_ANCHOR if all(mv[c].values())]
    res["reads"] = reads
    res["per_cell"] = per

    OUT_JSON.write_text(json.dumps(res, indent=1, sort_keys=False, default=float) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON.name}", flush=True)
    for cell in NON_ANCHOR:
        for s in FAMOUS:
            c1 = per[cell][s]["DRP-C1"]
            print(f"{cell} {s}: {outcomes[cell][s]}  n={c1['n']} medD={c1['median_D']} ub={c1['boot_ub_D']} "
                  f"medG={c1['median_G']} C2={per[cell][s]['DRP-C2']['ratio_vs_A0']} "
                  f"C6fires={per[cell][s]['DRP-C6']['fires_at']}", flush=True)
    print("reads", json.dumps(reads), flush=True)
    print("SW", json.dumps(res["DRP-SW_trigger"]), flush=True)


if __name__ == "__main__":
    main()
