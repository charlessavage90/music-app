"""Verify F1 against the adopted artifact. READ-ONLY; changes nothing.

Design: docs/superpowers/specs/2026-07-25-f1-minimum-stop-design.md section 7.
Run from api/:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-25-f1-verification/check.py
"""

import hashlib
import random

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import STOP_ADJACENT_ONLY, find_journey, find_path

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

cfg = ApiConfig()
digest = hashlib.sha256()
with open(cfg.graph_path, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
        digest.update(chunk)
assert digest.hexdigest() == ADOPTED_SHA256, "not the adopted artifact"
store = GraphStore.load(cfg.graph_path)
by = {n.lower(): i for i, n in enumerate(store.names)}

# 1. The reported case gains a stop.
a, b = by["radiohead"], by["weezer"]
path, rule = find_journey(store, a, b, [], cfg)
print(f"Radiohead -> Weezer: {len(path)} cards, {rule} -> "
      f"{[store.names[x] for x in path]}")
assert len(path) >= 3, "the reported case still has no stop"

# 2. A stranded pair falls back and says so.
a, b = by["doves"], by["elbow"]
path, rule = find_journey(store, a, b, [], cfg)
print(f"Doves -> Elbow: {len(path)} cards, {rule}")
assert rule == STOP_ADJACENT_ONLY and len(path) == 2

# 3. Ordinary paths are untouched. This is the claim the design rests on.
random.seed(0)
changed = 0
for _ in range(200):
    u, v = random.randrange(store.artist_count), random.randrange(store.artist_count)
    if u == v:
        continue
    before = find_path(store, u, v, [], cfg)
    if before is None or len(before) == 2:
        continue  # the two-card case is exactly what this feature changes
    after, rule = find_journey(store, u, v, [], cfg)
    if after != before or rule != "natural":
        changed += 1
        print(f"CHANGED: {store.names[u]} -> {store.names[v]} ({rule})")
print(f"\nordinary paths altered: {changed} (must be 0)")
assert changed == 0, "a non-adjacent path changed; the design's core claim is false"
print("all checks passed")
