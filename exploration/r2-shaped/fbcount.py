"""EXPLORATORY. Count journeys in a v2 run that equal what today's router gives with the same presses
(= the engine fell back, or coincidence). Run from api/."""
import sys, json
sys.path.insert(0, '../exploration/kit')
from pathlib import Path
from qlook import Ctx
BASE = Path(__file__).resolve().parents[1]
ctx = Ctx()
for f in sys.argv[1:]:
    q = Path(f).resolve()
    if BASE not in q.parents: raise SystemExit("refusing")
    d = json.loads(q.read_text(encoding="utf-8")); same = tot = 0; ex = []
    for r in d["rows"]:
        pressed = []
        for step in r["ladder"]:
            if step["k"] > 0:
                tot += 1
                res = ctx.find_journey(ctx.store, r["source"], r["target"], ctx.known(pressed), ctx.cfg)
                if res and res[0] == step["path"]:
                    same += 1; ex.append((r["source_name"], step["k"]))
            if "victim" in step: pressed.append(step["victim"])
    print(f"{q.stem}: {same}/{tot} identical to today's router; e.g. {ex[:8]}")
