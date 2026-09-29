"""EXPLORATORY: middle artists that recur across pairs at presses 3-10 (mini-hub check)."""
from pathlib import Path as _P
def safe(f):
    """Refuse paths outside exploration/ (these scripts only read kit run files)."""
    q = _P(f).resolve(); base = _P(__file__).resolve().parents[1]
    if base not in q.parents:
        raise SystemExit(f"refusing path outside exploration/: {f}")
    return q

import json, sys, collections
from pathlib import Path
for f in sys.argv[1:]:
    d = json.loads(safe(f).read_text(encoding='utf-8'))
    c = collections.Counter(); fam = {}
    for r in d['rows']:
        seen = set()
        for st in r['ladder'][3:]:
            for nm, pc in zip(st['names'][1:-1], st['pctl'][1:-1]):
                seen.add(nm); fam[nm] = pc
        c.update(seen)
    print(Path(f).stem, [(n, k, round(fam[n]*100)) for n, k in c.most_common(12)])
