"""Issue #200: ruler versus map. Descriptive decomposition only. Decides nothing.

Answers `../2026-09-27-issue-200-graph-descriptives/README.md` §3, first bullet: is the
lba-a6 "top 1 % walled in" figure (Measurement A there) a property of the map's EDGES or
of the fame-percentile RULER it was measured with? Scores each map's edges with each
map's percentiles over the artists the two maps share, plus two recomputed shared-only
frames that split the ruler into population and snapshot.

Currency on every figure: FAME PERCENTILE (ListenBrainz listener rank within a named
frame), always via the shipped `GraphStore.fame_percentiles`. Not pop_raw, not degree.
Every table line names its frame.

Factor table (fixed before the run; see README "Instrument"):
  RVM-1   lux4 edges    frame lux4 full, lux4 snapshot             all lux4
  RVM-2   lba-a6 edges  frame lba-a6 full, lba-a6 snapshot         all lba-a6
  RVM-1s  lux4 edges    frame lux4 full                            shared
  RVM-2s  lba-a6 edges  frame lba-a6 full                          shared
  RVM-3   lba-a6 edges  frame lux4 full                            shared
  RVM-6   lux4 edges    frame lba-a6 full                          shared
  RVM-4   lba-a6 edges  frame shared-only recomputed, lba-a6 snap  shared
  RVM-5   lba-a6 edges  frame shared-only recomputed, lux4 snap    shared

No routing, no weights, no ApiConfig. No command-line arguments are read.

Run from `api/`:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-issue-200-ruler-vs-map/ruler_vs_map.py

REFUSES (exit 2) if either artifact's sha256 disagrees with its own sidecar or with
the pinned value, before reading anything from it.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
import time
from pathlib import Path

import numpy as np

T0 = time.time()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # this worktree
SCRATCH = Path("C:/dev/music-app/builder/scratch")
NEW = SCRATCH / "graph-lba-a6.bin"  # adopted 2026-09-25
NEW_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
OLD = SCRATCH / "graph-lux4.bin"  # served before 2026-09-25
OLD_SHA = "fd92a7352afb7321e80f3818262d08169fcfb3af1d6841d7ccfca0f5e5740369"

# Fixed before the run.
BARS = (0.9, 0.5)  # neighbour "exit" bars, fame percentile
TIERS = (("top decile", 0.90), ("top 1 %", 0.99))  # centre thresholds
VERDICT_SHARE = 2 / 3  # one move owns the change if >= this in BOTH orderings


def verify(path: Path, expect: str) -> str:
    """sha256 must equal the sidecar's top-level `sha256` AND the pinned value."""
    sidecar = path.with_name(path.name + ".json")
    want = json.loads(sidecar.read_text(encoding="utf-8"))["sha256"]
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != want or got != expect:
        print(f"REFUSING: {path.name} sha256 {got}; sidecar {want}; pinned {expect}",
              file=sys.stderr)
        sys.exit(2)
    print(f"sha256 OK  {path.name}  {got}  (matches sidecar and pin)")
    return got


# ---- identity FIRST: nothing below is read before both checks pass ----
SHA = {NEW: verify(NEW, NEW_SHA), OLD: verify(OLD, OLD_SHA)}

from artistpath_api import graph_store as _gs_mod  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402

_API_SRC = (ROOT / "api" / "src").resolve()
_gs_file = Path(_gs_mod.__file__).resolve()
assert _API_SRC in _gs_file.parents, f"graph_store loaded from {_gs_file}, not {_API_SRC}"
print(f"graph_store: {_gs_file}")


def raw_fame(payload: bytes, n: int) -> list:
    """`fame_lb` straight from the APG1 metadata blob (GraphStore drops raw values).

    Copied from ../2026-09-27-issue-200-graph-descriptives/graph_descriptives.py.
    """
    header = struct.Struct("<4sIIIQ")
    magic, _v, hn, e, meta_len = header.unpack_from(payload)
    assert magic == b"APG1" and hn == n
    cursor = header.size + (hn + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor: cursor + meta_len])
    fame = meta.get("fame_lb")
    assert fame is not None and len(fame) == n, "artifact carries no/short fame_lb"
    return fame


def load(path: Path):
    payload = path.read_bytes()
    store = GraphStore.from_bytes(payload)
    fame = raw_fame(payload, store.artist_count)
    pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
    # Identity check: the store's percentiles ARE the shipped staticmethod's output.
    assert np.array_equal(pctl, GraphStore.fame_percentiles(fame))
    measured = np.array([v is not None for v in fame], dtype=bool)
    return store, fame, pctl, measured


def q(a, p):
    return float(np.nanpercentile(a, p)) if np.size(a) else float("nan")


def measure(store, frame: np.ndarray, include: np.ndarray) -> dict:
    """Measurement A's metrics on `store`'s edges, scored with `frame`.

    frame:   fame percentile per node of `store`; NaN = not in the frame (null fame in
             the frame's snapshot, or absent from the frame's population).
    include: artist-set restriction per node (all True, or shared-only).
    A node is VALID iff included and in frame. Centres and counted neighbours are
    valid nodes only; everything else is dropped from numerator and denominator.
    Centres left with no valid neighbour are excluded from every figure and counted.
    """
    valid = include & ~np.isnan(frame)
    off, nbr = store.offsets, store.neighbours
    out = {}
    for tier, cut in TIERS:
        centres = np.flatnonzero(valid & (frame >= cut))
        rows = []  # (raw degree, counted n, below0.9, below0.5, null-in-frame dropped, non-included dropped)
        for c in centres:
            nb = nbr[off[c]: off[c + 1]]
            inc = include[nb]
            v = valid[nb]
            fv = frame[nb[v]]
            rows.append((len(nb), int(v.sum()), int((fv < BARS[0]).sum()),
                         int((fv < BARS[1]).sum()), int((inc & ~v).sum()), int((~inc).sum())))
        r = np.array(rows, dtype=np.int64).reshape(-1, 6)
        empty = r[:, 1] == 0
        kept = r[~empty]
        k = len(kept)
        res = {"centres_all": len(centres), "no_valid_nb": int(empty.sum()), "k": k,
               "centre_ids": centres[~empty],
               "raw_deg_med": float(np.median(r[:, 0])) if len(r) else float("nan"),
               "raw_deg_p10": q(r[:, 0], 10), "raw_deg_p90": q(r[:, 0], 90),
               "cnt_med": float(np.median(kept[:, 1])) if k else float("nan"),
               "cnt_p10": q(kept[:, 1], 10), "cnt_p90": q(kept[:, 1], 90),
               "centres_with_null_nb": int((r[:, 4] > 0).sum()),
               "nb_dropped_null": int(r[:, 4].sum()),
               "nb_dropped_nonincluded": int(r[:, 5].sum())}
        for j, bar in enumerate(BARS):
            below = kept[:, 2 + j]
            share = below / kept[:, 1]
            z = int((below == 0).sum())
            res[bar] = {"med": float(np.median(share)), "p10": q(share, 10),
                        "p90": q(share, 90), "mean": float(np.mean(share)),
                        "zero": z, "zero_frac": z / k if k else float("nan"),
                        "cnt_below_med": float(np.median(below))}
        out[tier] = res
    return out


def main() -> None:
    lba, lba_fame, lba_pctl, lba_meas = load(NEW)
    lux, lux_fame, lux_pctl, lux_meas = load(OLD)
    print(f"load + identity asserts: {time.time() - T0:.1f}s")

    # ---- MBID alignment
    lux_ix = {m: i for i, m in enumerate(lux.mbids)}
    lba_ix = {m: i for i, m in enumerate(lba.mbids)}
    assert len(lux_ix) == lux.artist_count and len(lba_ix) == lba.artist_count
    lba_to_lux = np.array([lux_ix.get(m, -1) for m in lba.mbids], dtype=np.int64)
    lux_to_lba = np.array([lba_ix.get(m, -1) for m in lux.mbids], dtype=np.int64)
    lba_shared = lba_to_lux >= 0
    lux_shared = lux_to_lba >= 0
    assert lba_shared.sum() == lux_shared.sum()
    n_sh = int(lba_shared.sum())
    print(f"\n## Populations\nlba-a6 N {lba.artist_count:,} (null fame {int((~lba_meas).sum())}); "
          f"lux4 N {lux.artist_count:,} (null fame {int((~lux_meas).sum())}); shared by MBID "
          f"{n_sh:,}; only lba-a6 {lba.artist_count - n_sh:,}; only lux4 {lux.artist_count - n_sh:,}")
    print(f"shared, null in lba-a6 snapshot: {int((lba_shared & ~lba_meas).sum())}; "
          f"null in lux4 snapshot: {int((lux_shared & ~lux_meas).sum())}; null in both: "
          f"{int((lba_shared & ~lba_meas & ~lux_meas[np.maximum(lba_to_lux, 0)]).sum())}")

    # ---- frames, NaN = not in frame
    def with_nan(p, m):
        return np.where(m, p, np.nan)

    f_lux_full_on_lux = with_nan(lux_pctl, lux_meas)
    f_lba_full_on_lba = with_nan(lba_pctl, lba_meas)
    f_lux_full_on_lba = np.full(lba.artist_count, np.nan)
    f_lux_full_on_lba[lba_shared] = f_lux_full_on_lux[lba_to_lux[lba_shared]]
    f_lba_full_on_lux = np.full(lux.artist_count, np.nan)
    f_lba_full_on_lux[lux_shared] = f_lba_full_on_lba[lux_to_lba[lux_shared]]

    # Shared-only recomputed frames, on lba-a6 nodes, via the SHIPPED staticmethod
    sh_nodes = np.flatnonzero(lba_shared)
    sub_lba = [lba_fame[i] for i in sh_nodes]
    sub_lux = [lux_fame[int(lba_to_lux[i])] for i in sh_nodes]
    p4 = GraphStore.fame_percentiles(sub_lba)
    p5 = GraphStore.fame_percentiles(sub_lux)
    f4 = np.full(lba.artist_count, np.nan)
    f5 = np.full(lba.artist_count, np.nan)
    f4[sh_nodes] = np.where([v is not None for v in sub_lba], p4, np.nan)
    f5[sh_nodes] = np.where([v is not None for v in sub_lux], p5, np.nan)
    same_raw = sum(1 for x, y in zip(sub_lba, sub_lux) if x == y)
    print(f"shared artists whose raw fame_lb is IDENTICAL in the two snapshots: "
          f"{same_raw:,} of {len(sub_lba):,}; shared-only percentiles identical across "
          f"snapshots: {bool(np.array_equal(p4, p5))}")
    print(f"shared-only frames: lba-a6 snapshot measured {int((~np.isnan(f4)).sum()):,}; "
          f"lux4 snapshot measured {int((~np.isnan(f5)).sum()):,}")

    all_lba = np.ones(lba.artist_count, dtype=bool)
    all_lux = np.ones(lux.artist_count, dtype=bool)
    variants = [
        ("RVM-1", "lux4", "lux4 full, lux4 snapshot", "all lux4", lux, f_lux_full_on_lux, all_lux),
        ("RVM-2", "lba-a6", "lba-a6 full, lba-a6 snapshot", "all lba-a6", lba, f_lba_full_on_lba, all_lba),
        ("RVM-1s", "lux4", "lux4 full, lux4 snapshot", "shared", lux, f_lux_full_on_lux, lux_shared),
        ("RVM-2s", "lba-a6", "lba-a6 full, lba-a6 snapshot", "shared", lba, f_lba_full_on_lba, lba_shared),
        ("RVM-3", "lba-a6", "lux4 full, lux4 snapshot", "shared", lba, f_lux_full_on_lba, lba_shared),
        ("RVM-6", "lux4", "lba-a6 full, lba-a6 snapshot", "shared", lux, f_lba_full_on_lux, lux_shared),
        ("RVM-4", "lba-a6", "shared-only recomputed, lba-a6 snapshot", "shared", lba, f4, lba_shared),
        ("RVM-5", "lba-a6", "shared-only recomputed, lux4 snapshot", "shared", lba, f5, lba_shared),
    ]
    R = {}
    for vid, edges, frame_name, aset, store, frame, inc in variants:
        t = time.time()
        R[vid] = measure(store, frame, inc)
        R[vid]["meta"] = (edges, frame_name, aset)
        print(f"measured {vid} in {time.time() - t:.1f}s", flush=True)

    # ---- per-variant tables
    print("\n## Measurement A metrics per variant (fame percentile; frame named per column)")
    for tier, _cut in TIERS:
        print(f"\n### {tier} centres (fame pctl >= {_cut:.2f} in the variant's own frame)")
        print("| metric | " + " | ".join(v[0] for v in variants) + " |")
        print("|---|" + "---:|" * len(variants))
        print("| edges | " + " | ".join(R[v[0]]["meta"][0] for v in variants) + " |")
        print("| frame | " + " | ".join(R[v[0]]["meta"][1] for v in variants) + " |")
        print("| artist set | " + " | ".join(R[v[0]]["meta"][2] for v in variants) + " |")

        def row(label, fn):
            print(f"| {label} | " + " | ".join(fn(R[v[0]][tier]) for v in variants) + " |")

        row("centres (valid, >= cut)", lambda r: f"{r['centres_all']:,}")
        row("centres with no counted neighbour (excluded)", lambda r: f"{r['no_valid_nb']}")
        row("centres measured (k)", lambda r: f"{r['k']:,}")
        row("raw degree median (p10, p90)",
            lambda r: f"{r['raw_deg_med']:.0f} ({r['raw_deg_p10']:.0f}, {r['raw_deg_p90']:.0f})")
        row("counted neighbours median (p10, p90)",
            lambda r: f"{r['cnt_med']:.0f} ({r['cnt_p10']:.0f}, {r['cnt_p90']:.0f})")
        row("centres with >= 1 null-in-frame neighbour", lambda r: f"{r['centres_with_null_nb']:,}")
        row("neighbour entries dropped: null in frame", lambda r: f"{r['nb_dropped_null']:,}")
        row("neighbour entries dropped: not shared", lambda r: f"{r['nb_dropped_nonincluded']:,}")
        for bar in BARS:
            row(f"share < {bar}: median", lambda r, b=bar: f"{r[b]['med']:.4f}")
            row(f"share < {bar}: p10", lambda r, b=bar: f"{r[b]['p10']:.4f}")
            row(f"share < {bar}: p90", lambda r, b=bar: f"{r[b]['p90']:.4f}")
            row(f"share < {bar}: mean", lambda r, b=bar: f"{r[b]['mean']:.4f}")
            row(f"ZERO < {bar}: count", lambda r, b=bar: f"{r[b]['zero']:,}")
            row(f"ZERO < {bar}: fraction", lambda r, b=bar: f"{r[b]['zero_frac']:.4f}")
            row(f"median count < {bar}", lambda r, b=bar: f"{r[b]['cnt_below_med']:.0f}")

    # ---- reproduction check against 2026-09-27 figures (graph_descriptives.out.txt)
    print("\n## Reproduction check vs ../2026-09-27-issue-200-graph-descriptives/graph_descriptives.out.txt")
    expect = {  # (variant, tier, bar): (zero count, zero fraction, share median, mean)
        ("RVM-2", "top decile", 0.9): (629, 0.0720, 0.4861, 0.4554),
        ("RVM-2", "top decile", 0.5): (3106, 0.3554, 0.0440, 0.1071),
        ("RVM-2", "top 1 %", 0.9): (381, 0.4359, 0.0208, 0.1075),
        ("RVM-2", "top 1 %", 0.5): (706, 0.8078, 0.0000, 0.0230),
        ("RVM-1", "top decile", 0.9): (63, 0.0107, 0.4600, 0.4541),
        ("RVM-1", "top decile", 0.5): (1097, 0.1867, 0.0606, 0.0939),
        ("RVM-1", "top 1 %", 0.9): (9, 0.0153, 0.1429, 0.1952),
        ("RVM-1", "top 1 %", 0.5): (84, 0.1429, 0.0482, 0.0751),
    }
    ok_all = True
    for (vid, tier, bar), (z, zf, med, mean) in expect.items():
        r = R[vid][tier][bar]
        ok = (r["zero"] == z and f"{r['zero_frac']:.4f}" == f"{zf:.4f}"
              and f"{r['med']:.4f}" == f"{med:.4f}" and f"{r['mean']:.4f}" == f"{mean:.4f}")
        ok_all &= ok
        print(f"{vid} {tier} < {bar}: zero {r['zero']} ({r['zero_frac']:.4f}), median "
              f"{r['med']:.4f}, mean {r['mean']:.4f} -> {'MATCH' if ok else 'MISMATCH'}")
    print(f"all reproduced: {ok_all}")

    # ---- centre-set sizes and overlap
    print("\n## Top-1 % centre sets (shared variants)")
    for vid in ("RVM-1s", "RVM-2s", "RVM-3", "RVM-6", "RVM-4", "RVM-5"):
        print(f"{vid}: {R[vid]['top 1 %']['k']:,} top-1 % centres; "
              f"{R[vid]['top decile']['k']:,} top-decile centres")
    a = set(R["RVM-3"]["top 1 %"]["centre_ids"].tolist())
    b = set(R["RVM-2s"]["top 1 %"]["centre_ids"].tolist())
    print(f"overlap RVM-3 vs RVM-2s (both lba-a6 nodes): |RVM-3| {len(a)}, |RVM-2s| {len(b)}, "
          f"both {len(a & b)}, only RVM-3 {len(a - b)}, only RVM-2s {len(b - a)}, "
          f"Jaccard {len(a & b) / len(a | b):.4f}")
    a = set(R["RVM-3"]["top decile"]["centre_ids"].tolist())
    b = set(R["RVM-2s"]["top decile"]["centre_ids"].tolist())
    print(f"top-decile overlap RVM-3 vs RVM-2s: both {len(a & b)}, only RVM-3 {len(a - b)}, "
          f"only RVM-2s {len(b - a)}, Jaccard {len(a & b) / len(a | b):.4f}")

    # ---- restriction counts
    print("\n## What the shared restriction drops")
    for name, store, sh, pc, me in (("lba-a6", lba, lba_shared, lba_pctl, lba_meas),
                                    ("lux4", lux, lux_shared, lux_pctl, lux_meas)):
        src = np.repeat(np.arange(store.artist_count), np.diff(store.offsets))
        dst = np.asarray(store.neighbours)
        keep = sh[src] & sh[dst]
        und_all = int((src < dst).sum())
        und_rev = int((src > dst).sum())
        und_keep = int((keep & (src < dst)).sum())
        print(f"{name}: CSR entries {len(dst):,}; kept {int(keep.sum()):,}; dropped "
              f"{int((~keep).sum()):,}. undirected (u<v) {und_all:,} [u>v {und_rev:,}]; kept "
              f"{und_keep:,}; dropped {und_all - und_keep:,}")
        for tier, cut in TIERS:
            c = me & (pc >= cut)
            print(f"  {tier} centres in {name} full frame: {int(c.sum()):,}; not shared "
                  f"(dropped) {int((c & ~sh).sum()):,}; kept {int((c & sh).sum()):,}")

    # ---- attribution
    print("\n## Attribution (shared variants; metric differences in fraction units)")
    metrics = [("top 1 %", 0.9, "HEADLINE top-1 % ZERO < 0.9 fraction"),
               ("top 1 %", 0.5, "top-1 % ZERO < 0.5 fraction"),
               ("top decile", 0.9, "top-decile ZERO < 0.9 fraction")]
    for tier, bar, label in metrics:
        M = {v: R[v][tier][bar]["zero_frac"] for v in R}
        C = {v: R[v][tier][bar]["zero"] for v in R}
        total = M["RVM-2s"] - M["RVM-1s"]
        e1, f1 = M["RVM-3"] - M["RVM-1s"], M["RVM-2s"] - M["RVM-3"]  # edges-first
        f2, e2 = M["RVM-6"] - M["RVM-1s"], M["RVM-2s"] - M["RVM-6"]  # frame-first
        es, fs = (e1 + e2) / 2, (f1 + f2) / 2
        pop = M["RVM-2s"] - M["RVM-4"]
        snap = M["RVM-4"] - M["RVM-5"]
        resid = M["RVM-5"] - M["RVM-3"]
        print(f"\n### {label}")
        print("values: " + "; ".join(f"{v} {M[v]:.4f} ({C[v]}/{R[v][tier]['k']})"
                                     for v in ("RVM-1", "RVM-2", "RVM-1s", "RVM-2s", "RVM-3",
                                               "RVM-6", "RVM-4", "RVM-5")))
        print(f"total change RVM-1s -> RVM-2s: {total:+.4f}")
        print("| ordering | edges | edges share | frame | frame share |")
        print("|---|---:|---:|---:|---:|")
        print(f"| edges-first (1s->3->2s) | {e1:+.4f} | {e1 / total:.3f} | {f1:+.4f} | {f1 / total:.3f} |")
        print(f"| frame-first (1s->6->2s) | {e2:+.4f} | {e2 / total:.3f} | {f2:+.4f} | {f2 / total:.3f} |")
        print(f"| average (Shapley) | {es:+.4f} | {es / total:.3f} | {fs:+.4f} | {fs / total:.3f} |")
        print(f"restriction effect: RVM-2 - RVM-2s {M['RVM-2'] - M['RVM-2s']:+.4f}; "
              f"RVM-1 - RVM-1s {M['RVM-1'] - M['RVM-1s']:+.4f}")
        print(f"ruler split of the edges-first frame part ({f1:+.4f}), lba-a6 edges: "
              f"population (2s vs 4) {pop:+.4f} ({pop / f1 if f1 else float('nan'):.3f}); "
              f"snapshot (4 vs 5) {snap:+.4f} ({snap / f1 if f1 else float('nan'):.3f}); "
              f"929 residual (5 vs 3) {resid:+.4f} ({resid / f1 if f1 else float('nan'):.3f})")
        if (tier, bar) == ("top 1 %", 0.9):
            if e1 / total >= VERDICT_SHARE and e2 / total >= VERDICT_SHARE:
                v = "EDGES"
            elif f1 / total >= VERDICT_SHARE and f2 / total >= VERDICT_SHARE:
                v = "FRAME (ruler)"
            else:
                v = f"BOTH (averaged: edges {es / total:.3f}, frame {fs / total:.3f})"
            print(f"VERDICT (rule fixed before run, >= 2/3 in both orderings): {v}")

    print(f"\nrun time {time.time() - T0:.1f}s")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
