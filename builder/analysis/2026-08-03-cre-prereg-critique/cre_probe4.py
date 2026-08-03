"""CRE critique probe 4. READ-ONLY. Q1 (C1 statistic), Q3 (C2 noise), Q6 (population)."""
import hashlib
import json
from collections import Counter

import numpy as np
import sys

sys.path.insert(0, "C:/dev/music-app/api/src")
from artistpath_api.graph_store import GraphStore  # noqa: E402

R = "C:/dev/music-app/builder/analysis/"
SNAP = R + "2026-08-02-fame-instrument/fi_union_snapshot.json"
T3 = R + "2026-07-28-track3-depth-descent/t3_paths.json"
TB = R + "2026-07-29-track3b-thresholded-toll/tb_paths.json"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class Frame:
    def __init__(self, values):
        self.n = int(len(values))
        cnt = Counter(values.tolist())
        self.uniq = np.array(sorted(cnt), dtype=np.int64)
        self.counts = np.array([cnt[int(v)] for v in self.uniq], dtype=np.int64)
        self.less = np.concatenate([[0], np.cumsum(self.counts)[:-1]])
        self.pctl_at = (self.less + (self.counts + 1) / 2.0) / self.n
        self.max_pctl = float(self.pctl_at[-1])

    def pctl(self, v):
        v = np.asarray(v, dtype=np.int64)
        idx = np.searchsorted(self.uniq, v, side="left")
        below = np.where(idx > 0, self.less[np.clip(idx - 1, 0, None)]
                         + self.counts[np.clip(idx - 1, 0, None)], 0)
        present = (idx < len(self.uniq)) & (
            self.uniq[np.clip(idx, 0, len(self.uniq) - 1)] == v)
        eq = np.where(present, self.counts[np.clip(idx, 0, len(self.uniq) - 1)], 0)
        out = (below + (eq + 1) / 2.0) / self.n
        return np.where(v > self.uniq[-1], self.max_pctl, out)


snap = load(SNAP)
frame = Frame(np.array([v for v in snap.values() if v is not None], dtype=np.int64))
pc = {m: float(frame.pctl(np.array([v]))[0])
      for m, v in snap.items() if v is not None}

# ---------- Q6: population comparison ----------
GA = "C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin"
GB = "C:/dev/music-app/builder/scratch/graph-algb-full.bin"
assert hashlib.sha256(open(GA, "rb").read()).hexdigest().startswith("4cb84ef9")
assert hashlib.sha256(open(GB, "rb").read()).hexdigest().startswith("d008a2b5")
sa, sb = GraphStore.load(GA), GraphStore.load(GB)
A, Bset = set(sa.mbids), set(sb.mbids)
print("== Q6: population, in the ADOPTED currency ==")
for lab, mb in (("adopted (ALG-E MK50)", A), ("candidate (ALG-B full)", Bset),
                ("ALG-B only (not in adopted)", Bset - A),
                ("adopted only (not in ALG-B)", A - Bset)):
    vals = np.array([pc[m] for m in mb if m in pc])
    q = np.percentile(vals, [10, 25, 50, 75, 90])
    print(f"  {lab:30s} n={len(mb):6d} ruler-ok={len(vals):6d} "
          f"fame_lb_pctl p10/p25/p50/p75/p90 = " + "/".join(f"{x:.3f}" for x in q))

# ---------- Q1: per-pair delta machinery ----------
def per_pair(doc, band=(10, 15, 20)):
    nm = doc["node_mbids"]
    out = {}
    for arm, pp in doc["paths"].items():
        out[arm] = {}
        for pair, pd in pp.items():
            if pd.get("0") is None:
                continue
            bd = [d for d in band if pd.get(str(d))]
            if not bd:
                continue

            def vals(p):
                return [pc[nm[str(n)]] for n in p[1:-1] if nm.get(str(n)) in pc]

            d0 = vals(pd["0"])
            bv = []
            for d in bd:
                bv += vals(pd[str(d)])
            if not d0 or not bv:
                continue
            out[arm][pair] = float(np.median(bv)) - float(np.median(d0))
    return out


rng = np.random.default_rng(1)
for tag, path in (("Track 3", T3), ("Track 3b", TB)):
    doc = load(path)
    groups = doc["groups"]
    anchors = set(doc.get("unscored_anchor_pairs", []))
    st = per_pair(doc)
    print(f"\n== Q1: {tag} per-pair C1 deltas in fame_lb_pctl ==")
    print(f"  anchor (all-famous) pairs: {len(anchors)}")
    for arm, m in st.items():
        d = np.array(list(m.values()))
        anch = np.array([v for k, v in m.items() if k in anchors])
        flat = np.mean(np.abs(d) < 0.015)
        neg = np.mean(d <= -0.05)
        print(f"  {arm:8s} all n={len(d):2d} med={np.median(d):+.4f} | "
              f"share |d|<0.015 (no measured movement) = {flat:.2f} | "
              f"share d<=-0.05 = {neg:.2f} | ALL-FAMOUS anchors n={len(anch)}: "
              + " ".join(f"{x:+.3f}" for x in anch))
    # leave-one-out on the median, per arm
    print("  leave-one-out swing of the arm median:")
    for arm, m in st.items():
        d = np.array(list(m.values()))
        loo = [np.median(np.delete(d, i)) for i in range(len(d))]
        print(f"    {arm:8s} median={np.median(d):+.4f} "
              f"LOO range=[{min(loo):+.4f},{max(loo):+.4f}] "
              f"max |swing|={max(abs(np.median(d)-x) for x in loo):.4f}")
    # paired arm-vs-arm difference (R4's 0.015 lead margin)
    arms = list(st)
    print("  paired arm-vs-arm C1 difference, bootstrap at n=22 (pair-level):")
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            a, b = arms[i], arms[j]
            common = [p for p in st[a] if p in st[b]]
            diff = np.array([st[a][p] - st[b][p] for p in common])
            # unpaired: difference of independently bootstrapped medians
            da = np.array([st[a][p] for p in common])
            db = np.array([st[b][p] for p in common])
            idx = rng.integers(0, len(common), size=(5000, 22))
            paired = np.median(diff[idx], axis=1)
            unp_a = np.median(da[rng.integers(0, len(common), size=(5000, 22))], axis=1)
            unp_b = np.median(db[rng.integers(0, len(common), size=(5000, 22))], axis=1)
            unp = unp_a - unp_b
            print(f"    {a:8s} vs {b:8s} n={len(common):2d} "
                  f"median-of-paired-diff sd={paired.std(ddof=1):.4f} | "
                  f"diff-of-medians (unpaired) sd={unp.std(ddof=1):.4f}")

# ---------- Q3: clustered noise on the C2 band-share difference ----------
store = sa
deg = np.diff(store.offsets).astype(np.int64)
k1 = max(1, int(round(0.01 * store.artist_count)))
top1 = np.zeros(store.artist_count, dtype=bool)
top1[np.argsort(-deg, kind="stable")[:k1]] = True
print("\n== Q3: pair-clustered bootstrap of the CRE-C2 band-share difference ==")
for tag, path in (("Track 3", T3), ("Track 3b", TB)):
    doc = load(path)
    for arm, pp in doc["paths"].items():
        rows = []
        for pair, pd in pp.items():
            lo_h = lo_n = hi_h = hi_n = 0
            for d in (0, 1, 2):
                p = pd.get(str(d))
                if p:
                    ids = [int(x) for x in p[1:-1]]
                    lo_h += sum(top1[i] for i in ids)
                    lo_n += len(ids)
            for d in (10, 15, 20):
                p = pd.get(str(d))
                if p:
                    ids = [int(x) for x in p[1:-1]]
                    hi_h += sum(top1[i] for i in ids)
                    hi_n += len(ids)
            if lo_n and hi_n:
                rows.append((lo_h, lo_n, hi_h, hi_n))
        arr = np.array(rows, dtype=float)
        obs = arr[:, 2].sum() / arr[:, 3].sum() - arr[:, 0].sum() / arr[:, 1].sum()
        idx = rng.integers(0, len(arr), size=(5000, 22))
        s = arr[idx]
        boot = (s[:, :, 2].sum(1) / s[:, :, 3].sum(1)
                - s[:, :, 0].sum(1) / s[:, :, 1].sum(1))
        print(f"  {tag} {arm:8s} observed delta={obs:+.4f}  "
              f"pair-clustered bootstrap sd at n=22 = {boot.std(ddof=1):.4f}  "
              f"95%CI=[{np.percentile(boot,2.5):+.4f},{np.percentile(boot,97.5):+.4f}]")
