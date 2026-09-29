"""EXPLORATORY: solo (single-process) routing time of a variant file, replaying a run's press
sequence at presses 0, 3, 5, 10. Also checks the variant reproduces the run's journeys.
usage (from api/): uv run python ../exploration/r2-simple/timeit_r2.py VARIANT.py RUN.json"""
from pathlib import Path as _P
def safe(f):
    """Refuse paths outside exploration/ (these scripts only read kit run files)."""
    q = _P(f).resolve(); base = _P(__file__).resolve().parents[1]
    if base not in q.parents:
        raise SystemExit(f"refusing path outside exploration/: {f}")
    return q

import json, statistics, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kit"))
from qlook import Ctx, load_variant
ctx = Ctx(); mod = load_variant(sys.argv[1])
if hasattr(mod, "setup"): mod.setup(ctx)
d = json.loads(safe(sys.argv[2]).read_text(encoding="utf-8"))
ts, same, tot = [], 0, 0
for r in d["rows"]:
    lad = r["ladder"]; pressed = []
    for k, st in enumerate(lad):
        if k in (0, 3, 5, 10):
            prev = lad[k-1]["path"] if k else None
            t0 = time.perf_counter(); p = mod.journey(ctx, r["source"], r["target"], list(pressed), prev)
            ts.append(time.perf_counter() - t0); tot += 1; same += (p == st["path"])
        if "victim" in st: pressed.append(st["victim"])
print(f"{Path(sys.argv[1]).name}: solo secs median {statistics.median(ts):.3f}  p90 {sorted(ts)[int(.9*len(ts))]:.3f}  max {max(ts):.3f}; reproduces run {same}/{tot}")
