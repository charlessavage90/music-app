"""Measurements for the `ml-graph-analyst` review of the Track 2 pre-registration.

Discharges prerequisite P8 of `specs/2026-07-23-track2-preregistration.md` §7
and the review gate in the repair+retune design §4.6. Findings and their
interpretation live in
`docs/superpowers/findings/2026-07-23-track2-protocol-analyst-review.md`,
which OWNS these figures — cite that document, never this script.

M1 ceiling/score grid, M2 currency geometry (raw vs percentile edge gaps by
stratum), M3 popularity tie structure, M4 floor saturation on the
pre-registered pairs. Artifact sha256 asserted first, per convention.

Verbatim as executed, aside from this docstring. Paths hardcoded
deliberately: a record of what was run, not a maintained tool.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-23-track2-protocol-review/probe.py
"""

import hashlib, sys
from pathlib import Path
import numpy as np

ROOT = Path(r"C:\Users\charl\OneDrive\Claude Projects\music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
assert hashlib.sha256(GRAPH.read_bytes()).hexdigest() == EXPECT, "WRONG ARTIFACT"

from artistpath_api.graph_store import GraphStore
store = GraphStore.load(GRAPH)
N = store.artist_count
pop = np.asarray(store.pop_raw, dtype=np.float64)
scores = np.asarray(store.scores, dtype=np.float64)

# M1 — ceiling and score grid
ceil = scores >= 1.0
print(int(ceil.sum()), len(scores), float(scores[~ceil].max()),
      1.0 - float(scores[~ceil].max()), np.unique(scores).size)

# P6 percentile: average rank over N
order = np.argsort(pop, kind="stable"); ranks = np.empty(N); sp = pop[order]; i = 0
while i < N:
    j = i
    while j + 1 < N and sp[j + 1] == sp[i]:
        j += 1
    ranks[order[i:j + 1]] = (i + j) / 2.0
    i = j + 1
pctl = ranks / (N - 1)

# M3 — tie structure
u, c = np.unique(pop, return_counts=True)
print(u.size, int(c.max()), float(u[c.argmax()]), int(c[c > 1].sum()))
top = np.where(pctl >= 0.90)[0]
ut, ct = np.unique(pop[top], return_counts=True)
print(top.size, ut.size, int(ct.max()))

# M2 — currency geometry
src = np.repeat(np.arange(N, dtype=np.int64), np.diff(store.offsets))
dst = np.asarray(store.neighbours, dtype=np.int64)
d_raw = np.abs(pop[src] - pop[dst]); d_pct = np.abs(pctl[src] - pctl[dst])
hi = pctl >= 0.90
lateral = hi[src] & hi[dst]; exit_ = (hi[src] | hi[dst]) & ~lateral
deep = (hi[src] | hi[dst]) & ((pctl[src] < 0.5) | (pctl[dst] < 0.5))
for nm, m in (("all", np.ones(len(d_raw), bool)), ("lateral", lateral),
              ("exit", exit_), ("deep", deep)):
    print(nm, int(m.sum()), d_raw[m].mean(), d_pct[m].mean())
print("exit/lateral raw", d_raw[exit_].mean() / d_raw[lateral].mean(),
      "pctl", d_pct[exit_].mean() / d_pct[lateral].mean())

# M4 — floor saturation on the pre-registered pairs
by_name = {}
for i, nm in enumerate(store.names):
    p = by_name.get(nm)
    if p is None or pop[i] > pop[p]:
        by_name[nm] = i
PAIRS = [("Miles Davis", "Daft Punk"), ("The Shins", "Wishbone Ash"),
         ("Metallica", "Taylor Swift"), ("Radiohead", "The Beatles"),
         ("Muse", "Coldplay"), ("Madonna", "Bob Dylan"),
         ("Pink Floyd", "Aphex Twin"), ("Arctic Monkeys", "Johnny Cash"),
         ("Michael Jackson", "Gorillaz"), ("System of a Down", "R.E.M."),
         ("The Rolling Stones", "Linkin Park"), ("Nirvana", "CROOVE")]
for a, b in PAIRS:                      # 0.15 == config.py floor_relax_known
    ia, ib = by_name[a], by_name[b]
    bp, br = min(pctl[ia], pctl[ib]), min(pop[ia], pop[ib])
    print(a, "->", b, round(bp, 4), round(br, 4), int(np.ceil(bp / 0.15)))
