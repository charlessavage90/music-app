"""EXPLORATORY. Per press: all-middle fame (should equal the kit's column), inner-middle fame (middle
artists NOT next to an endpoint), mid-pair dive (less famous endpoint minus middle median, points),
length. Reads run JSONs (pctl stored in them; no graph needed)."""
import json, statistics as st, sys
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
def load(f):
    q = Path(f).resolve()
    if BASE not in q.parents: raise SystemExit("refusing path outside exploration/")
    return json.loads(q.read_text(encoding="utf-8"))
med = lambda x: st.median(x) if x else float("nan")
for f in sys.argv[1:]:
    d = load(f); print(f"# {Path(f).stem}")
    print("press | all-mid fam/mid | inner-mid fam/mid | mid dive (pts, + = below lesser endpoint) | len | secs")
    for k in (0, 1, 2, 3, 5, 7, 10):
        af, am, inf_, inm, dive, L, secs = [], [], [], [], [], [], []
        for r in d["rows"]:
            lad = r["ladder"]
            if k >= len(lad) or not lad[k]["path"]: continue
            pc = lad[k]["pctl"]; L.append(len(pc)); secs.append(lad[k]["secs"])
            mid = [x for x in pc[1:-1] if x > 0]; inner = [x for x in pc[2:-2] if x > 0]
            fam = r["tag"] == "famous"
            if mid: (af if fam else am).append(med(mid))
            if inner: (inf_ if fam else inm).append(med(inner))
            if not fam and mid: dive.append((min(pc[0], pc[-1]) - med(mid)) * 100)
        print(f"{k:>5} | {med(af)*100:5.1f} / {med(am)*100:5.1f} | {med(inf_)*100:5.1f} / {med(inm)*100:5.1f} | {med(dive):6.1f} (max {max(dive) if dive else float('nan'):5.1f}) | {sum(L)/len(L):4.1f} | {med(secs):.2f}/{max(secs):.2f}")
