"""For each press: is there a middle artist in the NEW journey who is a close neighbour
(sim >= 0.5) of the pressed artist AND less famous than it? Also mean middle-artist count
that are within 1 hop of the pressed artist. Reads run json; uses the graph for sims."""
import sys, json, bisect, statistics
sys.path.insert(0, '../exploration/kit')
from qlook import Ctx
ctx = Ctx()
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
def safe(f):
    q = Path(f).resolve()
    if BASE not in q.parents:
        raise SystemExit(f'refusing path outside exploration/: {f}')
    return q
for f in sys.argv[1:]:
    d = json.loads(safe(f).read_text(encoding='utf-8'))
    hit, tot, early = 0, 0, []
    for r in d['rows']:
        lad = r['ladder']
        for k in range(len(lad) - 1):
            x = lad[k].get('victim'); nxt = lad[k + 1]['path']
            if x is None or not nxt: continue
            tot += 1
            ok = any(ctx.sim(x, v) >= 0.5 or ctx.sim(v, x) >= 0.5 for v in nxt[1:-1] if ctx.pl[v] < ctx.pl[x])
            hit += ok
            if k < 5: early.append(ok)
    print(f"{f}: similar-and-less-famous replacement {hit}/{tot} = {hit/tot:.0%}; presses 1-5 {sum(early)/len(early):.0%}")

# fail-check: victim of row i vs next journey of row i+1 (unrelated journeys) should score low
d = json.loads(safe(sys.argv[1]).read_text(encoding='utf-8')); rows = d['rows']; hit = tot = 0
for i, r in enumerate(rows):
    o = rows[(i + 1) % len(rows)]['ladder']
    for k in range(min(len(r['ladder']), len(o)) - 1):
        x = r['ladder'][k].get('victim'); nxt = o[k + 1]['path']
        if x is None or not nxt: continue
        tot += 1; hit += any(ctx.sim(x, v) >= 0.5 or ctx.sim(v, x) >= 0.5 for v in nxt[1:-1] if ctx.pl[v] < ctx.pl[x])
print(f"FAIL-CHECK (mismatched journeys, {sys.argv[1]}): {hit}/{tot} = {hit/tot:.0%}")
