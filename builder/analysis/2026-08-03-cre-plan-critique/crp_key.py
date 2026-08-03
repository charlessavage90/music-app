"""CRP-3: the CRE-S2 deletion key -- label supply, the zero-agreement tie mass,
and the node-local neutral median.

Review instrument for the CRE execution-plan critique (2026-08-03). READ ONLY.
No frozen file is edited; five_frames() / idf are the committed machinery,
imported.

Measures, on the adopted artifact (the substrate CRE-D1 uses and the closest
available proxy for a cleaned ALG-E cell):

  A  W4 label coverage overall and among high-degree nodes -- how many nodes
     have FEWER THAN TWO measured agreements, i.e. fall through plan pin 1's
     neutral-median rule to GLOBAL_NEUTRAL_FALLBACK and rank by pure LB
     similarity (the S2 device is a no-op there).
  B  the zero-agreement tie mass: share of labelled-labelled edges whose
     rarity-weighted W4 agreement is EXACTLY 0.  Under a multiplicative key
     `strength * a` every one of those collapses to key 0.0 and is ordered by
     the MBID tie-break, not by similarity.
  C  the node-local neutral median: its spread across nodes, and whether it is
     fame-correlated (which decides whether the two endpoints of an unlabelled
     edge apply materially different deletion pressure).
  D  ALG-B cells: share of nodes with no W4 frame entry AT ALL, because the
     committed tag frames are built over the ADOPTED graph's mbids only.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-cre-plan-critique/crp_key.py
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B = ROOT / "builder/analysis"
for p in (B / "2026-07-30-tag-discrimination", B / "2026-07-31-release-tag-coverage",
          B / "2026-07-30-coherence-tag-probe", B / "2026-07-30-track-b-cap-selection",
          B / "2026-07-30-fame-proxy-coverage", B / "2026-08-02-fame-instrument"):
    sys.path.insert(0, str(p))
sys.path.insert(0, str(ROOT / "api/src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402
from fi_stats import Frame                          # noqa: E402
from tas_common import GLOBAL_NEUTRAL_FALLBACK      # noqa: E402
from tas_frame_split import five_frames             # noqa: E402

SCRATCH = ROOT / "builder/scratch"
GRAPH = SCRATCH / "graph-t15-tiebreakfix.bin"
SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
SNAP = B / "2026-08-02-fame-instrument/fi_union_snapshot.json"
CELLS = SCRATCH / "cb-cells"


def main() -> None:
    assert hashlib.sha256(GRAPH.read_bytes()).hexdigest() == SHA
    print("artifact sha OK", flush=True)
    store = GraphStore.load(GRAPH)
    N = store.artist_count
    deg = np.diff(np.asarray(store.offsets)).astype(np.int64)
    snap = json.loads(SNAP.read_text(encoding="utf-8"))

    frame = Frame(np.array([snap[m] for m in store.mbids if snap.get(m) is not None],
                           dtype=np.int64))
    fp = np.full(N, np.nan)
    for i, m in enumerate(store.mbids):
        v = snap.get(m)
        if v is not None:
            fp[i] = float(frame.pctl(np.array([v]))[0])

    t0 = time.time()
    W4 = five_frames()["W4"]
    print(f"W4 built in {time.time() - t0:.0f}s; artists in frame={len(W4)}", flush=True)

    labels = [W4.get(m, set()) for m in store.mbids]
    size = np.array([len(s) for s in labels], dtype=np.int64)
    df: Counter = Counter()
    for s in labels:
        for lab in s:
            df[lab] += 1
    idf = {lab: math.log(N / c) for lab, c in df.items()}

    def wagree(a: set, b: set):
        if not a or not b:
            return None
        wu = sum(idf.get(x, 0.0) for x in (a | b))
        if wu <= 0:
            return None
        return sum(idf.get(x, 0.0) for x in (a & b)) / wu

    out: dict = {
        "nodes": int(N),
        "W4_labelled_nodes": int((size > 0).sum()),
        "W4_coverage": float((size > 0).mean()),
        "GLOBAL_NEUTRAL_FALLBACK": GLOBAL_NEUTRAL_FALLBACK,
    }

    # ---- per-node measured agreements over its own neighbour row ----
    n_measured = np.zeros(N, dtype=np.int64)
    med = np.full(N, np.nan)
    zero_edges = 0
    measured_edges = 0
    unlabelled_edges = 0
    offs = np.asarray(store.offsets)
    nbrs = np.asarray(store.neighbours)
    for u in range(N):
        lo, hi = int(offs[u]), int(offs[u + 1])
        vals = []
        for pos in range(lo, hi):
            v = int(nbrs[pos])
            a = wagree(labels[u], labels[v])
            if a is None:
                continue
            vals.append(a)
        n_measured[u] = len(vals)
        if len(vals) >= 2:
            med[u] = statistics.median(vals)
        if u % 20000 == 0:
            print(f"  node {u}/{N} ({time.time() - t0:.0f}s)", flush=True)

    # directed-edge tallies (each undirected edge counted twice; ratios unaffected)
    src = np.repeat(np.arange(N), deg)
    dst = nbrs.astype(np.int64)
    und = src < dst
    uu, vv = src[und], dst[und]
    for a_i, b_i in zip(uu.tolist(), vv.tolist()):
        a = wagree(labels[a_i], labels[b_i])
        if a is None:
            unlabelled_edges += 1
        else:
            measured_edges += 1
            if a == 0.0:
                zero_edges += 1

    out["undirected_edges"] = int(len(uu))
    out["edges_unlabelled_endpoint"] = unlabelled_edges
    out["edges_unlabelled_share"] = unlabelled_edges / len(uu)
    out["edges_measured"] = measured_edges
    out["edges_agreement_exactly_zero"] = zero_edges
    out["share_of_measured_edges_exactly_zero"] = zero_edges / max(measured_edges, 1)
    out["share_of_all_edges_with_key_exactly_zero"] = zero_edges / len(uu)

    fell_through = int((n_measured < 2).sum())
    out["nodes_with_fewer_than_2_measured_agreements"] = fell_through
    out["share_nodes_falling_back_to_GLOBAL_NEUTRAL"] = fell_through / N

    hi_deg = deg >= 40
    out["nodes_degree_ge_40"] = int(hi_deg.sum())
    out["share_of_degree_ge_40_nodes_falling_back"] = float(
        (n_measured[hi_deg] < 2).mean()) if hi_deg.any() else None

    ok = ~np.isnan(med)
    out["node_neutral_median"] = {
        "n_nodes_with_a_median": int(ok.sum()),
        "p10": float(np.percentile(med[ok], 10)),
        "p50": float(np.percentile(med[ok], 50)),
        "p90": float(np.percentile(med[ok], 90)),
        "min": float(med[ok].min()),
        "max": float(med[ok].max()),
    }
    both = ok & ~np.isnan(fp)
    if both.sum() > 100:
        x, y = fp[both], med[both]
        out["node_neutral_median"]["pearson_vs_fame_lb_pctl"] = float(
            np.corrcoef(x, y)[0, 1])
        lowf = both & (fp <= 0.50)
        hif = both & (fp >= 0.75)
        out["node_neutral_median"]["median_at_fame_pctl_le_0.50"] = float(
            np.median(med[lowf]))
        out["node_neutral_median"]["median_at_fame_pctl_ge_0.75"] = float(
            np.median(med[hif]))

    # the two endpoints of an unlabelled edge apply DIFFERENT keys: quantify
    diffs = []
    for a_i, b_i in zip(uu.tolist(), vv.tolist()):
        if wagree(labels[a_i], labels[b_i]) is not None:
            continue
        ma = med[a_i] if not np.isnan(med[a_i]) else GLOBAL_NEUTRAL_FALLBACK
        mb = med[b_i] if not np.isnan(med[b_i]) else GLOBAL_NEUTRAL_FALLBACK
        diffs.append(abs(ma - mb))
    if diffs:
        d = np.array(diffs)
        out["unlabelled_edge_endpoint_key_multiplier_gap"] = {
            "n_edges": int(len(d)),
            "p50_abs_gap": float(np.percentile(d, 50)),
            "p90_abs_gap": float(np.percentile(d, 90)),
            "share_gap_gt_0.10": float((d > 0.10).mean()),
        }

    # ---- D: ALG-B cells and the adopted-only tag frame ----
    adopted_set = set(store.mbids)
    dcov = {}
    for name, fn in (("ALG-B-MK50", "ALG-B-mutual_knn-k50.bin"),
                     ("ALG-B-TUw-50-50", "ALG-B-trimmed_union-d50-j50.bin"),
                     ("ALG-E-TUw-50-50", "ALG-E-trimmed_union-d50-j50.bin")):
        p = CELLS / fn
        if not p.exists():
            continue
        ms = GraphStore.load(p).mbids
        outside = sum(1 for m in ms if m not in adopted_set)
        nolab = sum(1 for m in ms if not W4.get(m))
        dcov[name] = {
            "nodes": len(ms),
            "outside_adopted_mbid_set": outside,
            "outside_share": outside / len(ms),
            "no_W4_label": nolab,
            "no_W4_label_share": nolab / len(ms),
        }
    out["cells_tag_frame_coverage"] = dcov

    (HERE / "crp_key.json").write_text(json.dumps(out, indent=1, sort_keys=True),
                                       encoding="utf-8")
    print(json.dumps(out, indent=1, sort_keys=True))
    print("\nwrote crp_key.json")


if __name__ == "__main__":
    main()
