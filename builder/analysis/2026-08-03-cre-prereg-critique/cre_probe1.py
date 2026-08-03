"""CRE pre-registration critique, probe 1.

READ-ONLY. Recomputes a CRE-C1-shaped statistic in the ADOPTED currency
(fame_lb_pctl over the frozen union snapshot) from the COMMITTED Track 3 and
Track 3b ladder path node sets. This is a new measurement in the adopted
currency, not a re-read of any prior fame-scored result.

Caveat carried into every read: those ladders ran on graph-t15-tiebreakfix
(pre-cleanup, incumbent MK50), on a different pair draw from cb_pairs.json.
The dispersion it estimates is the ladder's own churn dispersion, which is the
quantity CRE-C1's bar has to clear.
"""
import json
import sys
from collections import Counter

import numpy as np

ROOT = "C:/dev/music-app/"
SNAP = ROOT + "builder/analysis/2026-08-02-fame-instrument/fi_union_snapshot.json"
T3 = ROOT + "builder/analysis/2026-07-28-track3-depth-descent/t3_paths.json"
TB = ROOT + "builder/analysis/2026-07-29-track3b-thresholded-toll/tb_paths.json"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class Frame:
    """Exactly fi_stats.Frame (FAM- adopted machinery), copied read-only."""

    def __init__(self, values):
        self.n = int(len(values))
        cnt = Counter(values.tolist())
        self.uniq = np.array(sorted(cnt), dtype=np.int64)
        self.counts = np.array([cnt[int(v)] for v in self.uniq], dtype=np.int64)
        self.less = np.concatenate([[0], np.cumsum(self.counts)[:-1]])
        self.pctl_at = (self.less + (self.counts + 1) / 2.0) / self.n
        self.max_pctl = float(self.pctl_at[-1])

    def pctl(self, values):
        v = np.asarray(values, dtype=np.int64)
        idx = np.searchsorted(self.uniq, v, side="left")
        below = np.where(idx > 0,
                         self.less[np.clip(idx - 1, 0, None)]
                         + self.counts[np.clip(idx - 1, 0, None)], 0)
        present = (idx < len(self.uniq)) & (
            self.uniq[np.clip(idx, 0, len(self.uniq) - 1)] == v)
        eq = np.where(present, self.counts[np.clip(idx, 0, len(self.uniq) - 1)], 0)
        out = (below + (eq + 1) / 2.0) / self.n
        return np.where(v > self.uniq[-1], self.max_pctl, out)


snap = load(SNAP)
vals = np.array([v for v in snap.values() if v is not None], dtype=np.int64)
frame = Frame(vals)
print(f"frame n_nonnull={frame.n}  n_total={len(snap)}  max_pctl={frame.max_pctl:.6f}")
steps = np.diff(np.concatenate([[0.0], frame.pctl_at]))
print(f"quantisation: median step={np.median(steps):.6f} max step={steps.max():.6f}")


def pctl_of_mbid(m):
    v = snap.get(m, "MISSING")
    if v == "MISSING":
        return None, "unmapped"
    if v is None:
        return None, "ruler_null"
    return float(frame.pctl(np.array([v]))[0]), "ok"


def per_pair_stats(paths_doc, band_lo=10, band_hi=20):
    """Return {arm: {pair: {'d0':x,'band':y,'delta':d, nulls...}}}."""
    nm = paths_doc["node_mbids"]
    out = {}
    diag = Counter()
    for arm, per_pair in paths_doc["paths"].items():
        out[arm] = {}
        for pair, per_depth in per_pair.items():
            depths = sorted(int(d) for d in per_depth)
            band = [d for d in depths if band_lo <= d <= band_hi
                    and per_depth[str(d)] is not None]
            if 0 not in depths or per_depth.get("0") is None or not band:
                continue

            def interiors(d):
                p = per_depth[str(d)]
                return [] if p is None else p[1:-1]

            def pctls(nodes):
                vals, nulls, unmapped = [], 0, 0
                for n in nodes:
                    m = nm.get(str(n))
                    if m is None:
                        unmapped += 1
                        continue
                    p, st = pctl_of_mbid(m)
                    if st == "ok":
                        vals.append(p)
                    elif st == "ruler_null":
                        nulls += 1
                    else:
                        unmapped += 1
                return vals, nulls, unmapped

            d0v, d0n, d0u = pctls(interiors(0))
            bandv, bandn, bandu = [], 0, 0
            per_depth_med = []
            for d in band:
                v, n_, u_ = pctls(interiors(d))
                bandv += v
                bandn += n_
                bandu += u_
                if v:
                    per_depth_med.append(float(np.median(v)))
            diag["nulls"] += d0n + bandn
            diag["unmapped"] += d0u + bandu
            diag["slots"] += len(d0v) + len(bandv) + d0n + bandn + d0u + bandu
            if not d0v or not bandv:
                continue
            out[arm][pair] = {
                "d0_med": float(np.median(d0v)),
                "band_med_pooled": float(np.median(bandv)),
                "delta_pooled": float(np.median(bandv)) - float(np.median(d0v)),
                "delta_meanofdepthmed": float(np.mean(per_depth_med)) - float(np.median(d0v)),
                "d0_n": len(d0v), "band_n": len(bandv),
                "band_depths": band,
                "d0_len": len(per_depth["0"]),
                "band_len_mean": float(np.mean([len(per_depth[str(d)]) for d in band])),
                "group": None,
            }
    return out, diag


def summarise(tag, doc, groups_key="groups"):
    stats, diag = per_pair_stats(doc)
    groups = doc.get(groups_key, {})
    print(f"\n===== {tag} =====")
    print(f"  ruler nulls={diag['nulls']} unmapped={diag['unmapped']} "
          f"of {diag['slots']} interior slots "
          f"({100*diag['nulls']/max(diag['slots'],1):.2f}% null, "
          f"{100*diag['unmapped']/max(diag['slots'],1):.2f}% unmapped)")
    for arm, per_pair in stats.items():
        ds = np.array([v["delta_pooled"] for v in per_pair.values()])
        if len(ds) == 0:
            continue
        fam = [p for p in per_pair if groups.get(p, "").startswith("famous")]
        dfam = np.array([per_pair[p]["delta_pooled"] for p in fam])
        print(f"  arm {arm:8s} n={len(ds):2d} median={np.median(ds):+.4f} "
              f"mean={ds.mean():+.4f} sd={ds.std(ddof=1):.4f} "
              f"IQR=[{np.percentile(ds,25):+.3f},{np.percentile(ds,75):+.3f}] "
              f"min={ds.min():+.3f} max={ds.max():+.3f} "
              f"| famous n={len(dfam)} med="
              f"{(np.median(dfam) if len(dfam) else float('nan')):+.4f}")
    return stats


s3 = summarise("Track 3 (t3_paths, ramps 0.0/0.01/0.03/0.1)", load(T3))
sb = summarise("Track 3b (tb_paths, thresholded toll)", load(TB))

# ---- noise: bootstrap the median of per-pair deltas at n=22 and n=10 ----
rng = np.random.default_rng(20260803)
for tag, stats in (("T3", s3), ("TB", sb)):
    for arm, per_pair in stats.items():
        ds = np.array([v["delta_pooled"] for v in per_pair.values()])
        if len(ds) < 5:
            continue
        for n in (10, 12, 22):
            draws = rng.choice(ds, size=(20000, n), replace=True)
            meds = np.median(draws, axis=1)
            print(f"  {tag}/{arm:8s} bootstrap median at n={n:2d}: "
                  f"sd={meds.std(ddof=1):.4f} "
                  f"95%CI=[{np.percentile(meds,2.5):+.4f},{np.percentile(meds,97.5):+.4f}]")
    print()
