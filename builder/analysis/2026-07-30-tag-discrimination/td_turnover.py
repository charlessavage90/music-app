"""TD-2: transfer function from per-artist top-50 swaps to surviving-edge turnover.

The question
------------
`TAS-4` (prereg §2) kills the build-time architecture "if at every lambda the
median artist swaps <= 2 of 50". Its own bound says the built consequence of a
given swap rate is NOT derivable from the swap rate alone, because mutual k-NN
kills edge (u,v) when EITHER endpoint drops it. This module measures the
conversion empirically on the real candidate-list / mutuality distribution.

What it does NOT use: tag data. The tag frame does not exist yet, so the
reranking here is a synthetic field with tunable magnitude, run in six arms that
isolate the two structural factors the tag signal could differ on — WHERE the
swaps fall (boundary vs anywhere in the list) and WHETHER the two endpoints
reorder together (a shared agreement signal is symmetric by construction).
The transfer function is a property of the graph's mutuality structure, not of
the field; the field only sets how many swaps occur.

Factor table (one row per arm, one column per knob that varies):

    arm            placement of swaps      endpoint correlation   knob
    BND-n          forced, at the k=50     n/a (deterministic)    n
                   boundary exactly
    W10-IND-n      within +-10 of the      independent            n
                   boundary
    W10-SYM-n      within +-10 of the      symmetric (shared)     n
    UNI-IND-n      anywhere in the list    independent            n
    UNI-SYM-n      anywhere in the list    symmetric (shared)     n
    MULT-IND-lam   noise-driven            independent            lam
    MULT-SYM-lam   noise-driven            symmetric (shared)     lam

    Isolating baselines: W10-SYM-n's is W10-IND-n (differs in the correlation
    column only); UNI-IND-n's is W10-IND-n (differs in the placement column
    only); MULT-SYM-lam's is MULT-IND-lam. BND-n has no one-column neighbour
    and is read only as the lower bound on placement, never as a correlation
    result.

    Held constant: the archive, the candidate lists, the emitted scores, k=50,
    the tie-break (lowest MBID == lowest id, since ids are assigned in
    sorted-MBID order). Only `ranking` / the selected set moves, which is
    exactly the seam `mutual_knn_cap`'s `ranking` argument exposes. Nothing is
    built; the largest-component prune is NOT applied (see --verify, which
    quantifies what that omits).

Null model: for every arm, the measured edge loss is compared against the
independent-uniform-drop prediction  sum_edges (p_u + p_v - p_u*p_v) / |E|,
where p_u is the arm's OWN realised per-node drop fraction. That is what
turnover would be if swaps were spread uniformly over each node's top-50 and
uncorrelated across endpoints, so the ratio isolates placement + correlation
from the raw swap count.

Run from `builder/` (after td_capture.py):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/td_turnover.py \
        --capture <path.npz> --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
SCRATCH = HERE.parent.parent / "scratch"
sys.path.insert(0, str(ROOT / "builder" / "src"))

from artistpath_builder.artifact import deserialise  # noqa: E402

# The adopted artifact (identity by checksum; several graphs exist in scratch/
# and they are NOT interchangeable). It is reported for context only: it was
# built 2026-07-23, before `_assemble` gained the nameless-artist drop, so the
# simulation substrate is the Track B ALG-E MK50 rebuild of the SAME archive,
# which is what the instrument check below reproduces exactly.
ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
MK50_CELL = SCRATCH / "cb-cells" / "ALG-E-mutual_knn-k50.bin"
K = 50


# ---------------------------------------------------------------- hashing
def _mix(x: np.ndarray) -> np.ndarray:
    """splitmix64 finaliser. Deterministic uniform field from an integer key."""
    x = x.astype(np.uint64, copy=True)
    x ^= x >> np.uint64(30)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27)
    x *= np.uint64(0x94D049BB133111EB)
    x ^= x >> np.uint64(31)
    return x


def uniform_field(a: np.ndarray, b: np.ndarray, n: int, seed: int,
                  symmetric: bool) -> np.ndarray:
    """Uniform[0,1) per directed pair (a,b). If symmetric, f(u,v) == f(v,u)."""
    u = a.astype(np.int64)
    v = b.astype(np.int64)
    if symmetric:
        lo = np.minimum(u, v)
        hi = np.maximum(u, v)
    else:
        lo, hi = u, v
    key = (lo * np.int64(n) + hi).astype(np.uint64) ^ np.uint64(seed)
    h = _mix(key) >> np.uint64(11)
    return h.astype(np.float64) / float(1 << 53)


# ---------------------------------------------------------------- structure
class Capture:
    def __init__(self, path: Path) -> None:
        z = np.load(path, allow_pickle=True)
        self.offsets = z["offsets"]
        self.cand = z["cand"]
        self.rank = z["rank"]
        self.mbids = list(z["mbids"])
        self.n = len(self.mbids)
        self.lengths = np.diff(self.offsets)
        self.total = int(self.offsets[-1])
        self.node = np.repeat(np.arange(self.n, dtype=np.int64), self.lengths)
        # Baseline order: (-ranking, lowest id) within node, exactly
        # mutual_knn_cap's key.  lexsort: last key is primary.
        order = np.lexsort((self.cand, -self.rank, self.node))
        self.s_node = self.node[order]
        self.s_cand = self.cand[order].astype(np.int64)
        self.s_rank = self.rank[order]
        self.pos = np.arange(self.total, dtype=np.int64) - np.repeat(
            self.offsets[:-1], self.lengths
        )
        self.s_key = self.s_node * self.n + self.s_cand
        self.topk_count = np.minimum(self.lengths, K)
        self.binds = self.lengths > K  # selection has a choice to make


def mutual_undirected(cap: Capture, mask: np.ndarray) -> np.ndarray:
    """Undirected keys of edges surviving mutual k-NN under `mask`."""
    keys = np.sort(cap.s_key[mask])
    u = cap.s_node[mask]
    v = cap.s_cand[mask]
    rev = v * cap.n + u
    idx = np.searchsorted(keys, rev)
    idx[idx >= keys.size] = 0
    ok = keys[idx] == rev
    sel = ok & (u < v)
    return np.sort(u[sel] * cap.n + v[sel])


def swaps_per_node(cap: Capture, base_mask: np.ndarray,
                   new_mask: np.ndarray) -> np.ndarray:
    base_keys = np.sort(cap.s_key[base_mask])
    nk = cap.s_key[new_mask]
    idx = np.searchsorted(base_keys, nk)
    idx[idx >= base_keys.size] = 0
    kept = base_keys[idx] == nk
    kept_per_node = np.bincount(cap.s_node[new_mask][kept], minlength=cap.n)
    return cap.topk_count - kept_per_node


# ---------------------------------------------------------------- arms
def mask_window(cap: Capture, n_swap: int, window: int | None,
                seed: int, symmetric: bool | None) -> np.ndarray:
    """Drop n_swap from the top-50 and promote n_swap from the tail.

    window=None    -> unrestricted (drops from anywhere in the top-50,
                      promotions from anywhere in the tail)
    window=w       -> drops restricted to positions [K-w, K), promotions to
                      positions [K, K+w)
    symmetric=None -> deterministic boundary choice (the lowest-ranked kept are
                      dropped, the highest-ranked dropped are promoted)
    """
    mask = cap.pos < K
    field = (None if symmetric is None
             else uniform_field(cap.s_node, cap.s_cand, cap.n, seed, symmetric))
    off = cap.offsets
    for u in np.flatnonzero(cap.binds):
        a, b = off[u], off[u + 1]
        L = b - a
        if window is None:
            dpool = np.arange(0, K)
            ppool = np.arange(K, L)
        else:
            dpool = np.arange(max(0, K - window), K)
            ppool = np.arange(K, min(L, K + window))
        m = min(n_swap, dpool.size, ppool.size)
        if m == 0:
            continue
        if field is None:
            drop = dpool[-m:]
            promo = ppool[:m]
        else:
            fd = field[a + dpool]
            fp = field[a + ppool]
            drop = dpool[np.argsort(fd, kind="stable")[:m]]
            promo = ppool[np.argsort(-fp, kind="stable")[:m]]
        mask[a + drop] = False
        mask[a + promo] = True
    return mask


def mask_multiplicative(cap: Capture, lam: float, seed: int,
                        symmetric: bool) -> np.ndarray:
    """rank' = rank * (1 + lam * agreement), agreement ~ U[0,1).

    Same functional form as the prereg §1 selection rule; the agreement field
    is synthetic, so this fixes the SIZE of the reordering, not its content.
    """
    field = uniform_field(cap.s_node, cap.s_cand, cap.n, seed, symmetric)
    newrank = cap.s_rank * (1.0 + lam * field)
    order = np.lexsort((cap.s_cand, -newrank, cap.s_node))
    newpos = np.empty(cap.total, dtype=np.int64)
    newpos[order] = np.arange(cap.total, dtype=np.int64) - np.repeat(
        cap.offsets[:-1], cap.lengths
    )
    return newpos < K


# ---------------------------------------------------------------- scoring
def score(cap: Capture, base_mask: np.ndarray, base_edges: np.ndarray,
          new_mask: np.ndarray, label: str) -> dict:
    sw = swaps_per_node(cap, base_mask, new_mask)
    sw_b = sw[cap.binds]
    new_edges = mutual_undirected(cap, new_mask)
    lost = int(base_edges.size
               - np.isin(base_edges, new_edges, assume_unique=True).sum())
    gained = int(new_edges.size
                 - np.isin(new_edges, base_edges, assume_unique=True).sum())

    # Independent-uniform-drop null, using this arm's OWN realised drop rates.
    p = np.zeros(cap.n)
    nz = cap.topk_count > 0
    p[nz] = sw[nz] / cap.topk_count[nz]
    eu = base_edges // cap.n
    ev = base_edges % cap.n
    pu, pv = p[eu], p[ev]
    null_lost = float((pu + pv - pu * pv).sum())

    med = float(np.median(sw_b))
    deg = np.bincount(eu, minlength=cap.n) + np.bincount(ev, minlength=cap.n)
    edge_wt_rate = float((p * deg).sum() / deg.sum())
    return {
        "arm": label,
        "median_swaps_binding": med,
        "mean_swaps_binding": float(sw_b.mean()),
        "mean_swaps_all_nodes": float(sw.mean()),
        "edge_weighted_drop_rate": round(edge_wt_rate, 5),
        "edges_before": int(base_edges.size),
        "edges_after": int(new_edges.size),
        "lost": lost,
        "gained": gained,
        "lost_frac": round(lost / base_edges.size, 5),
        "gained_frac": round(gained / base_edges.size, 5),
        "turnover_frac": round((lost + gained) / base_edges.size, 5),
        "jaccard": round((base_edges.size - lost) / (base_edges.size + gained), 5),
        "null_lost_frac": round(null_lost / base_edges.size, 5),
        "amplification_vs_median": (
            round((lost / base_edges.size) / (med / K), 3) if med else None
        ),
        "measured_over_null": round(lost / null_lost, 3) if null_lost else None,
    }


def _artifact_edge_keys(g, idx_of: dict, n: int) -> np.ndarray:
    nb = g.neighbours
    off = g.offsets
    ids = np.array([idx_of[m] for m in g.mbids], dtype=np.int64)
    src = np.repeat(ids, np.diff(off))
    dst = ids[nb.astype(np.int64)]
    sel = src < dst
    return np.sort(src[sel] * n + dst[sel])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--out", default=str(HERE / "td_turnover.json"))
    args = ap.parse_args()

    cap = Capture(Path(args.capture))
    base_mask = cap.pos < K
    base_edges = mutual_undirected(cap, base_mask)
    eu, ev = base_edges // cap.n, base_edges % cap.n

    report: dict = {
        "capture_nodes": cap.n,
        "directed_candidates": cap.total,
        "candidate_list_length": {
            "mean": round(float(cap.lengths.mean()), 2),
            "median": int(np.median(cap.lengths)),
            "max": int(cap.lengths.max()),
            "share_gt_50": round(float((cap.lengths > 50).mean()), 5),
            "share_eq_100": round(float((cap.lengths >= 100).mean()), 5),
        },
        "nodes_list_gt_50": int(cap.binds.sum()),
        "mutual_edges_pre_prune": int(base_edges.size),
        "edges_incident_on_binding_node_share": round(
            float((cap.binds[eu] | cap.binds[ev]).mean()), 5),
        "edges_with_both_ends_binding_share": round(
            float((cap.binds[eu] & cap.binds[ev]).mean()), 5),
    }

    # Mutuality by rank position: the mechanism behind attenuation.
    keys = np.sort(cap.s_key)
    rev = cap.s_cand * cap.n + cap.s_node
    idx = np.searchsorted(keys, rev)
    idx[idx >= keys.size] = 0
    listed_back = keys[idx] == rev
    tk = cap.pos < K
    tkeys = np.sort(cap.s_key[tk])
    idx2 = np.searchsorted(tkeys, rev)
    idx2[idx2 >= tkeys.size] = 0
    mut_dir = tk & (tkeys[idx2] == rev)
    partner_topk = tkeys[idx2] == rev
    prof = {}
    for lo, hi in [(0, 5), (5, 10), (10, 20), (20, 30), (30, 40), (40, 45),
                   (45, 50), (50, 55), (55, 60), (60, 70), (70, 100)]:
        sel = (cap.pos >= lo) & (cap.pos < hi)
        if not sel.any():
            continue
        prof[f"{lo}-{hi}"] = {
            "entries": int(sel.sum()),
            "partner_lists_me": round(float(listed_back[sel].mean()), 4),
            "partner_ranks_me_top50": round(float(partner_topk[sel].mean()), 4),
        }
    report["mutuality_by_rank_position"] = prof
    report["mutual_share_of_top50_slots"] = round(
        float(mut_dir.sum()) / float(tk.sum()), 5)

    if args.verify:
        sha_ad = hashlib.sha256(ADOPTED.read_bytes()).hexdigest()
        assert sha_ad == ADOPTED_SHA, f"adopted sha mismatch: {sha_ad}"
        gad = deserialise(ADOPTED.read_bytes())
        dad = np.diff(gad.offsets)
        cmb = set(cap.mbids)
        amb = set(gad.mbids)
        report["adopted_artifact"] = {
            "file": ADOPTED.name,
            "sha256": sha_ad,
            "artists": int(gad.artist_count),
            "directed_edge_slots": int(gad.edge_count),
            "undirected_edges": int(gad.edge_count // 2),
            "degree_mean": round(float(dad.mean()), 2),
            "degree_median": int(np.median(dad)),
            "degree_p99": int(np.percentile(dad, 99)),
            "degree_max": int(dad.max()),
            "nodes_in_adopted_not_in_capture": len(amb - cmb),
            "nodes_in_capture_not_in_adopted": len(cmb - amb),
        }

        # GREEN instrument check: the simulation substrate must reproduce the
        # Track B ALG-E MK50 cell EXACTLY on that cell's node set.
        gm = deserialise(MK50_CELL.read_bytes())
        idx_of = {m: i for i, m in enumerate(cap.mbids)}
        missing = [m for m in gm.mbids if m not in idx_of]
        art_keys = _artifact_edge_keys(gm, idx_of, cap.n)
        keep = np.zeros(cap.n, dtype=bool)
        keep[[idx_of[m] for m in gm.mbids]] = True
        sim_in = base_edges[keep[eu] & keep[ev]]
        report["instrument_check_green"] = {
            "file": MK50_CELL.name,
            "sha256": hashlib.sha256(MK50_CELL.read_bytes()).hexdigest(),
            "artifact_artists": int(gm.artist_count),
            "artifact_undirected_edges": int(art_keys.size),
            "capture_nodes_missing_from_artifact_side": len(missing),
            "sim_edges_restricted_to_artifact_nodes": int(sim_in.size),
            "exact_match": bool(art_keys.size == sim_in.size
                                and np.array_equal(art_keys, sim_in)),
            "edges_dropped_by_largest_component_prune": int(
                base_edges.size - art_keys.size),
        }
        print(json.dumps(report["instrument_check_green"], indent=2))
        print(json.dumps(report["adopted_artifact"], indent=2))

    rows = []
    for n_swap in (1, 2, 3, 5, 10):
        rows.append(score(cap, base_mask, base_edges,
                          mask_window(cap, n_swap, n_swap, 0, None),
                          f"BND-{n_swap}"))
        for sym, tag in ((False, "IND"), (True, "SYM")):
            rows.append(score(cap, base_mask, base_edges,
                              mask_window(cap, n_swap, 10, 101, sym),
                              f"W10-{tag}-{n_swap}"))
            rows.append(score(cap, base_mask, base_edges,
                              mask_window(cap, n_swap, None, 202, sym),
                              f"UNI-{tag}-{n_swap}"))
        print(f"... n={n_swap} done", flush=True)

    for lam in (0.05, 0.1, 0.25, 0.5, 1.0, 2.0):
        for sym, tag in ((False, "IND"), (True, "SYM")):
            rows.append(score(cap, base_mask, base_edges,
                              mask_multiplicative(cap, lam, 303, sym),
                              f"MULT-{tag}-{lam}"))
        print(f"... lam={lam} done", flush=True)

    report["arms"] = rows
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    hdr = ("arm", "med", "mean", "lost%", "gain%", "turn%", "null%", "amp", "m/n")
    print("{:<16}{:>6}{:>7}{:>8}{:>8}{:>8}{:>8}{:>7}{:>7}".format(*hdr))
    for r in rows:
        print("{:<16}{:>6.1f}{:>7.2f}{:>8.3f}{:>8.3f}{:>8.3f}{:>8.3f}{:>7}{:>7}".format(
            r["arm"], r["median_swaps_binding"], r["mean_swaps_binding"],
            100 * r["lost_frac"], 100 * r["gained_frac"], 100 * r["turnover_frac"],
            100 * r["null_lost_frac"],
            r["amplification_vs_median"] or 0, r["measured_over_null"] or 0))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
