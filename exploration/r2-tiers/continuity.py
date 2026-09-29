"""Per press: share of the new journey's middle artists that were also in the previous journey's
middle (continuity), plus how many middle artists changed. Fail-check: same measure against the
previous journey of a *different* pair (should be ~0)."""
import json, sys, statistics
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
def load(f):
    q = Path(f).resolve()
    if BASE not in q.parents:
        raise SystemExit(f"refusing path outside exploration/: {f}")
    return json.loads(q.read_text(encoding="utf-8"))
def share(cur, old):
    mid = cur[1:-1]
    return sum(v in set(old[1:-1]) for v in mid) / len(mid) if mid else float("nan")
for f in sys.argv[1:]:
    rows = load(f)["rows"]
    per = {}
    fail = []
    for i, r in enumerate(rows):
        lad = r["ladder"]
        other = rows[(i + 1) % len(rows)]["ladder"]
        for k in range(1, len(lad)):
            a, b = lad[k]["path"], lad[k - 1]["path"]
            if a and b:
                per.setdefault(k, []).append(share(a, b))
            if k < len(other) and a and other[k - 1]["path"]:
                fail.append(share(a, other[k - 1]["path"]))
    ks = sorted(per)
    allv = [x for k in ks for x in per[k]]
    print(f"{Path(f).name}: kept-from-previous  " + " ".join(f"p{k}:{statistics.mean(per[k]):.0%}" for k in ks)
          + f"  | mean {statistics.mean(allv):.0%}  | fail-check (other pair) {statistics.mean(fail):.0%}")
