"""Per press: new cards (not on the previous journey) more than 40 pts below the pressed artist,
and the share of presses producing one. Fail-check: a synthetic run where a card is replaced by
the least famous artist in the map must flag."""
import json, sys
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
for f in sys.argv[1:]:
    q = Path(f).resolve()
    if BASE not in q.parents:
        raise SystemExit("path outside exploration/")
    d = json.loads(q.read_text(encoding="utf-8"))
    hits = tot = 0
    ex = []
    for r in d["rows"]:
        lad = r["ladder"]
        for k in range(len(lad) - 1):
            if "victim" not in lad[k] or not lad[k + 1]["path"]:
                continue
            vx = lad[k]["pctl"][lad[k]["path"].index(lad[k]["victim"])]
            old = set(lad[k]["path"])
            new = [(n, p) for v, n, p in zip(lad[k + 1]["path"], lad[k + 1]["names"], lad[k + 1]["pctl"]) if v not in old]
            tot += 1
            bad = [(n, round(p * 100)) for n, p in new if p < vx - 0.40]
            if bad:
                hits += 1
                ex.append((r["source_name"], k + 1, round(vx * 100), bad))
    print(f"{q.name}: presses with a new card >40 pts below the pressed artist: {hits}/{tot}")
    for e in ex[:4]:
        print("   ", e)
