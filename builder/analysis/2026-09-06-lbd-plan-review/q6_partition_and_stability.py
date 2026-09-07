"""(i) what 'our top-N' scores if it is the OWN lexical partition rather than the
       score-truncated union;  (ii) split-half stability of the Q1 drift figures."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import numpy as np
from artistpath_api.graph_store import GraphStore

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
ARCH = SCRATCH / ("grt-archive-algb.pre-cex-snapshot/similar/listenbrainz/"
                  "session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30")

print("=== (i) share of each served list that lies in the artist's OWN lexical partition ===")
own, tot, per = 0, 0, []
lens = []
for e in os.scandir(ARCH):
    if not e.name.endswith(".json"):
        continue
    mb = e.name[:-5]
    rows = json.loads(open(e.path, "rb").read())
    ns = [r["artist_mbid"] for r in rows if r.get("artist_mbid") and r["artist_mbid"] != mb]
    if not ns:
        continue
    o = sum(1 for y in ns if mb < y)
    own += o; tot += len(ns); per.append(o / len(ns)); lens.append(len(ns))
per = np.array(per); lens = np.array(lens)
print(f"  rows {tot:,}   in the owner's own partition {own:,} ({100.0*own/tot:.2f}%)")
print(f"  per-artist share: median {np.median(per):.4f}  mean {per.mean():.4f} "
      f"p10 {np.percentile(per,10):.4f}  p90 {np.percentile(per,90):.4f}")
m = lens >= 100
print(f"  for artists at the 100 ceiling (n={int(m.sum()):,}): median {np.median(per[m]):.4f} "
      f"mean {per[m].mean():.4f}")

print("\n=== (ii) split-half stability of the population-drift figures (Q1) ===")
old = GraphStore.load(SCRATCH / "graph-msw-tu50.bin")
new = GraphStore.load(SCRATCH / "graph-cxa-adopted.bin")
oi = {m_: i for i, m_ in enumerate(old.mbids)}; ni = {m_: i for i, m_ in enumerate(new.mbids)}
common = [m_ for m_ in old.mbids if m_ in ni]
do = np.diff(old.offsets)[[oi[m_] for m_ in common]].astype(np.int64)
dn = np.diff(new.offsets)[[ni[m_] for m_ in common]].astype(np.int64)
# sha1 with usedforsecurity=False: this is a DETERMINISTIC SPLIT-HALF SELECTOR, not a
# digest of anything secret. Kept as sha1 rather than "upgraded" because the algorithm
# decides which MBIDs land in which half -- changing it silently changes the reported
# split-half figures, so the committed numbers would stop reproducing from this script.
h = np.array([int(hashlib.sha1(m_.encode(), usedforsecurity=False).hexdigest()[:2], 16) % 2
              for m_ in common])
for label, mask in (("half A", h == 0), ("half B", h == 1), ("both", np.ones_like(h, bool))):
    a, b = do[mask], dn[mask]
    print(f"  {label}: n={a.size:,}  median {np.median(a):.0f}->{np.median(b):.0f}  "
          f"share<=2 {100*np.mean(a<=2):.2f}%->{100*np.mean(b<=2):.2f}%  "
          f"mean {a.mean():.2f}->{b.mean():.2f}  paired mean d {np.mean(b-a):+.3f}")
    for lo, hi, nm in ((1, 2, "deg<=2"), (1, 4, "deg<=4")):
        s = mask & (do >= lo) & (do <= hi)
        print(f"      {nm}: n={int(s.sum()):,}  median {np.median(do[s]):.0f}->{np.median(dn[s]):.0f}"
              f"  share<=2 {100*np.mean(do[s]<=2):.2f}%->{100*np.mean(dn[s]<=2):.2f}%"
              f"  ({100*np.mean(dn[s]<=2)-100*np.mean(do[s]<=2):+.2f} pp)")
