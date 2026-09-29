"""Predictability: per pair, how often a press makes the middle MORE famous (median rises > 5 pts),
and the worst single rise. Fail-check: a shuffled press order should show many rises."""
import json, sys, statistics, random
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
for f in sys.argv[1:]:
    q = Path(f).resolve()
    if BASE not in q.parents:
        raise SystemExit("refusing path outside exploration/")
    rows = json.loads(q.read_text(encoding="utf-8"))["rows"]
    def meds(r):
        return [statistics.median(l["pctl"][1:-1]) if l["path"] and len(l["path"]) > 2 else None for l in r["ladder"]]
    rises = tot = 0; worst = []
    shuf_r = shuf_t = 0
    rng = random.Random(0)
    for r in rows:
        m = [x for x in meds(r) if x is not None]
        for a, b in zip(m[1:], m[2:]):   # from press 1 on
            tot += 1; rises += b - a > 0.05
        if len(m) > 2:
            worst.append((max(b - a for a, b in zip(m[1:], m[2:])), r["source_name"]))
        sm = m[1:]; rng.shuffle(sm)
        for a, b in zip(sm, sm[1:]):
            shuf_t += 1; shuf_r += b - a > 0.05
    worst.sort(reverse=True)
    print(f"{q.name}: presses that re-famed the middle (>5 pts) {rises}/{tot} = {rises/tot:.0%}; shuffled-order fail-check {shuf_r/shuf_t:.0%}; worst: " +
          ", ".join(f"{n} +{w*100:.0f}" for w, n in worst[:3]))
