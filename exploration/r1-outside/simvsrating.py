# How does step similarity relate to the rater's verdict? (all rated steps in the shared cache that
# occur in my rated runs). Uses names -> ids via run JSON, sims via the map.
import json, os, sys, glob, statistics
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H + '/../kit')
import qlook
ctx = qlook.Ctx()
cache = {}
for line in open(H + '/../kit/step_cache.jsonl', encoding='utf-8'):
    try:
        d = json.loads(line); cache[d['k']] = d['r']
    except Exception:
        pass
buck = {}
seen = set()
for f in glob.glob(H + '/runs/*_rated.json') + [H + '/../baseline/runs/today.json']:
    for r in json.load(open(f, encoding='utf-8'))['rows']:
        for d in r['ladder']:
            p = d['path'] or []
            for u, v in zip(p, p[1:]):
                k = qlook.step_key(ctx, u, v)
                if k in seen or not isinstance(cache.get(k), (int, float)):
                    continue
                seen.add(k)
                s = ctx.sim(u, v)
                b = min(int(s * 10), 9) / 10
                buck.setdefault(b, []).append(cache[k])
for b in sorted(buck):
    xs = buck[b]
    print(f"sim {b:.1f}-{b+0.1:.1f}: n={len(xs):4d} mean={statistics.mean(xs):.2f} bad={sum(x<=1 for x in xs)/len(xs):.0%}")
