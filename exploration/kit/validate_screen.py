"""Show the coherence screen can fail: real journeys vs the same journeys scrambled.

Three versions of every baseline journey at presses 0 and 10:
  real      - as routed
  shuffled  - same middle artists, order shuffled (endpoints kept)
  swapped   - each middle artist replaced by a random artist of about the same fame (+-2 pctl)
The screen is only worth using if real scores well above both.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/validate_screen.py \
        ../exploration/baseline/runs/today.json
"""
from __future__ import annotations

import bisect
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qlook import Ctx, step_key  # noqa: E402
import rate  # noqa: E402


PRESSES = tuple(int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["0", "10"]))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ctx = Ctx()
    run = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    rng = random.Random(7)
    order = sorted(range(ctx.n), key=lambda v: ctx.pl[v])
    sorted_p = [ctx.pl[v] for v in order]

    def same_fame(v):
        lo = bisect.bisect_left(sorted_p, ctx.pl[v] - 0.02)
        hi = bisect.bisect_right(sorted_p, ctx.pl[v] + 0.02)
        return order[rng.randrange(lo, hi)]

    versions = {"real": [], "shuffled": [], "swapped": []}
    for r in run["rows"]:
        for d in r["ladder"]:
            if d["k"] not in PRESSES or not d["path"] or len(d["path"]) < 4:
                continue
            p = d["path"]
            mid = p[1:-1]
            sh = mid[:]
            while sh == mid:
                rng.shuffle(sh)
            versions["real"].append(p)
            versions["shuffled"].append([p[0]] + sh + [p[-1]])
            versions["swapped"].append([p[0]] + [same_fame(v) for v in mid] + [p[-1]])
    steps = [(u, v) for ps in versions.values() for p in ps for u, v in zip(p, p[1:])]
    rated = rate.rate_steps(ctx, steps)
    for name, ps in versions.items():
        scores = [rated[step_key(ctx, u, v)] for p in ps for u, v in zip(p, p[1:])]
        num = [x for x in scores if isinstance(x, int)]
        per_journey = []
        for p in ps:
            s = [rated[step_key(ctx, u, v)] for u, v in zip(p, p[1:])]
            s = [x for x in s if isinstance(x, int)]
            if s:
                per_journey.append(sum(s) / len(s) / 3)
        print(f"{name:>9}: {len(ps)} journeys, {len(scores)} steps, mean step {sum(num)/len(num):.2f}/3, "
              f"bad (0-1) {sum(x <= 1 for x in num)/len(num)*100:.0f}%, unknown {sum(x == 'U' for x in scores)/len(scores)*100:.0f}%")
    # discrimination: how often does the real journey outscore its shuffled / swapped twin
    def jscore(p):
        s = [rated[step_key(ctx, u, v)] for u, v in zip(p, p[1:])]
        s = [x for x in s if isinstance(x, int)]
        return sum(s) / len(s) if s else None
    for other in ("shuffled", "swapped"):
        wins = ties = n = 0
        for a, b in zip(versions["real"], versions[other]):
            sa, sb = jscore(a), jscore(b)
            if sa is None or sb is None:
                continue
            n += 1
            wins += sa > sb
            ties += sa == sb
        print(f"real beats {other} twin in {wins}/{n} journeys ({ties} ties)")


if __name__ == "__main__":
    main()
