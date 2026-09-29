"""EXPLORATORY: journeys (presses 1-10) that had to use a step below the floor, after the endpoint rule
(an endpoint may use links as strong as its best link to a not-yet-pressed neighbour).
Fail-check: with floor 0.99 nearly every journey must count."""
from pathlib import Path as _P
def safe(f):
    """Refuse paths outside exploration/ (these scripts only read kit run files)."""
    q = _P(f).resolve(); base = _P(__file__).resolve().parents[1]
    if base not in q.parents:
        raise SystemExit(f"refusing path outside exploration/: {f}")
    return q

import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kit"))
from qlook import Ctx
ctx = Ctx(); fl = float(sys.argv[1])
for f in sys.argv[2:]:
    d = json.loads(safe(f).read_text(encoding='utf-8')); n = tot = 0; pairs = set(); steps = []
    for r in d['rows']:
        pressed = []
        for st in r['ladder']:
            if st['k'] >= 1 and st['path']:
                p = st['path']; hard = set(pressed); tot += 1
                def efl(e):
                    nb, sc = ctx.row(e); av = [x for v, x in zip(nb, sc) if v not in hard]
                    return min(fl, max(av)) if av else 0
                fs, ft = efl(p[0]), efl(p[-1])
                bad = [ctx.sim(u, v) for u, v in zip(p, p[1:]) if ctx.sim(u, v) < min(fl, fs if u == p[0] else fl, ft if v == p[-1] else fl)]
                if bad: n += 1; pairs.add(r['source_name']); steps += bad
            if 'victim' in st: pressed.append(st['victim'])
    print(f"{Path(f).stem} floor {fl}: {n}/{tot} journeys used a sub-floor step, in {len(pairs)} pairs {sorted(pairs)}; those steps' sims {sorted(round(x,2) for x in steps)[:12]}")
