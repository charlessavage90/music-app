"""Median fame of middle artists EXCLUDING the two cards next to the endpoints (famous pairs / mid),
at presses 0,3,5,10. Fail-check: on today's run it must stay ~99 (it does not move there)."""
import json, statistics, sys
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
for f in sys.argv[1:]:
    q = Path(f).resolve()
    if BASE not in q.parents:
        raise SystemExit("path outside exploration/")
    d = json.loads(q.read_text(encoding="utf-8"))
    out = []
    for k in (0, 1, 3, 5, 10):
        fam, mid = [], []
        for r in d["rows"]:
            if k >= len(r["ladder"]) or not r["ladder"][k]["path"]:
                continue
            pc = r["ladder"][k]["pctl"][2:-2]
            if pc:
                (fam if r["tag"] == "famous" else mid).append(statistics.median(pc))
        out.append(f"p{k} {statistics.median(fam)*100:.1f}/{statistics.median(mid)*100:.1f}")
    print(q.name, " | ".join(out))
