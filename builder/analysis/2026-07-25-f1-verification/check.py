"""Verify F1 against the adopted artifact. READ-ONLY; changes nothing.

Design: docs/superpowers/specs/2026-07-25-f1-minimum-stop-design.md section 7.
Run from api/:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-25-f1-verification/check.py

Fix round 1 (2026-07-25): the original check 3 sampled random NODE pairs and
skipped every pair whose least-cost path already had two cards. Every pair
that reached the comparison therefore took find_journey's early return
(len(path) != 2 -> return path, STOP_NATURAL), which just re-runs find_path
with identical arguments and hands the result straight back. before == after
and rule == "natural" held BY CONSTRUCTION -- the loop could not fail, and it
never exercised the detour branch (the only branch this change actually
added). It is kept below, relabelled as a guard on the early-return line, not
evidence about the real graph. Check 4 is the new check that exercises the
detour branch, sampling adjacent pairs directly from the CSR arrays instead
of random node pairs (random pairs are essentially never adjacent, which is
why the detour branch never ran before).

Also fixed: the name lookup was last-writer-wins on a lowercased dict, so an
ambiguous name (this graph has 1,283 duplicated names -- MKS-7 in
findings/2026-07-25-mutual-knn-stranding.md) could silently resolve to the
wrong artist. It now raises loudly, naming every candidate, instead.

Fix round 2 (2026-07-25): round 1's check 4 asserted that no graph-adjacent
pair could ever come back STOP_NATURAL. That is also false, and for the same
kind of reason as round 1's premise error: GRAPH ADJACENCY (an edge exists)
is not the same claim as "the direct edge is the cheapest route between
them." w_sim dominates the cost function (w_sim=3.0 vs w_hop=0.02), so a
direct edge with mediocre similarity can cost more than a two-hop detour
through a highly-similar intermediate -- Tina Malia -> Lafa Taylor is a real
example: a genuine 0.476-similarity edge loses to the two-hop route via
Bassnectar. When that happens, find_path's own least-cost answer already has
a stop in it, and find_journey correctly reports natural rather than
forcing anything. Check 4 now partitions adjacent pairs by what find_path
(not adjacency) actually returns, and only the two-card case is the F1
branch this feature added.

Sample sizes cut from round 1 (200 -> 40 for check 3, 150 -> 100 for check 4)
because the script was too slow to be run more than once.
"""

import hashlib
import random

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import (
    STOP_ADJACENT_ONLY,
    STOP_FORCED,
    STOP_NATURAL,
    find_journey,
    find_path,
)

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

cfg = ApiConfig()
digest = hashlib.sha256()
with open(cfg.graph_path, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
        digest.update(chunk)
assert digest.hexdigest() == ADOPTED_SHA256, "not the adopted artifact"
store = GraphStore.load(cfg.graph_path)

# Name lookup that fails loudly on ambiguity rather than silently taking
# whichever duplicate was enumerated last.
name_index: dict[str, list[int]] = {}
for i, n in enumerate(store.names):
    name_index.setdefault(n.lower(), []).append(i)


def lookup(name: str) -> int:
    candidates = name_index.get(name.lower())
    if not candidates:
        raise KeyError(name)
    if len(candidates) > 1:
        detail = "; ".join(
            f"{store.names[i]!r} (id={i}, mbid={store.mbids[i]})" for i in candidates
        )
        raise ValueError(
            f"ambiguous name {name!r}: {len(candidates)} artists share it: {detail}"
        )
    return candidates[0]


def has_edge(a: int, b: int) -> bool:
    start, end = int(store.offsets[a]), int(store.offsets[a + 1])
    return b in store.neighbours[start:end]


# 1. The reported case gains a stop.
a, b = lookup("radiohead"), lookup("weezer")
path, rule = find_journey(store, a, b, [], cfg)
print(f"Radiohead -> Weezer: {len(path)} cards, {rule} -> "
      f"{[store.names[x] for x in path]}")
assert len(path) >= 3, "the reported case still has no stop"

# 2. A stranded pair falls back and says so.
a, b = lookup("doves"), lookup("elbow")
path, rule = find_journey(store, a, b, [], cfg)
print(f"Doves -> Elbow: {len(path)} cards, {rule}")
assert rule == STOP_ADJACENT_ONLY and len(path) == 2

# 3. Guard: the early return in find_journey still fires for non-adjacent
# pairs. True by construction -- find_journey re-runs find_path with
# identical arguments and hands the result straight back, so this cannot
# detect a behaviour change in the detour branch. It only catches the
# one-line length guard itself being broken. Check 4 below is the one that
# exercises the branch this change actually added.
random.seed(0)
compared = 0
changed = 0
for _ in range(40):
    u, v = random.randrange(store.artist_count), random.randrange(store.artist_count)
    if u == v:
        continue
    before = find_path(store, u, v, [], cfg)
    if before is None or len(before) == 2:
        continue  # the two-card case is exactly what this feature changes
    compared += 1
    after, rule = find_journey(store, u, v, [], cfg)
    if after != before or rule != STOP_NATURAL:
        changed += 1
        print(f"CHANGED: {store.names[u]} -> {store.names[v]} ({rule})")
print(f"\nearly-return guard: {compared} pairs, {changed} diverged")
assert changed == 0, "the early-return guard itself is broken"

# 4. The branch that actually changed: adjacent pairs, sampled directly from
# the CSR arrays (random node pairs are essentially never adjacent, which is
# why check 3 never touched the detour branch).
#
# GRAPH ADJACENCY DOES NOT MEAN THE DIRECT EDGE IS CHEAPEST. w_sim dominates
# the cost function (w_sim=3.0 vs w_hop=0.02), so a mediocre-similarity
# direct edge can cost more than a two-hop detour through a highly-similar
# intermediate -- find_path's own least-cost answer for a graph-adjacent
# pair can legitimately be 3+ cards, with nothing forced. So adjacent pairs
# are partitioned by what find_path (not adjacency) actually returns: only
# the two-card case is the branch this feature added.
random.seed(1)
n = store.artist_count
edge_pairs: list[tuple[int, int]] = []
seen_pairs: set[tuple[int, int]] = set()
attempts = 0
while len(edge_pairs) < 100 and attempts < 200_000:
    attempts += 1
    u = random.randrange(n)
    start, end = int(store.offsets[u]), int(store.offsets[u + 1])
    if start == end:
        continue
    v = int(store.neighbours[random.randrange(start, end)])
    if u == v or (u, v) in seen_pairs or (v, u) in seen_pairs:
        continue
    seen_pairs.add((u, v))
    edge_pairs.append((u, v))
assert len(edge_pairs) == 100, f"only found {len(edge_pairs)} distinct adjacent pairs"

no_forcing_needed = 0  # before already has a stop (len >= 3): legitimate, not a failure
forced = 0             # before is the bare edge (len == 2); a stop was inserted
no_stop_possible = 0   # before is the bare edge; no detour exists (STOP_ADJACENT_ONLY)
insert_counts: list[int] = []
for u, v in edge_pairs:
    assert has_edge(u, v), f"sampled pair is not actually an edge: {u}, {v}"
    before = find_path(store, u, v, [], cfg)
    assert before is not None, f"no path at all for a graph-adjacent pair: {u}, {v}"
    result = find_journey(store, u, v, [], cfg)
    assert result is not None, f"find_journey returned None for adjacent pair {u}, {v}"
    path, rule = result

    if len(before) >= 3:
        # The cheapest route already detours; adjacency alone said nothing
        # about whether the direct edge would be used.
        no_forcing_needed += 1
        assert rule == STOP_NATURAL, (
            f"adjacent pair {store.names[u]} -> {store.names[v]} already had a "
            f"{len(before)}-card cheapest route but find_journey reported {rule}, "
            "not natural"
        )
        assert path == before, (
            f"adjacent pair {store.names[u]} -> {store.names[v]}: find_journey's "
            f"path {path} differs from find_path's {before} despite reporting natural"
        )
        continue

    # before is the bare two-card edge: the direct connection IS the
    # cheapest route. This is the only case F1's forcing logic can fire on.
    assert len(before) == 2, f"unexpected before length: {before}"
    assert rule != STOP_NATURAL, (
        f"adjacent pair {store.names[u]} -> {store.names[v]}: the direct edge was "
        "the cheapest route, so find_journey should have forced a stop or reported "
        "adjacent_only, not natural"
    )
    if rule == STOP_FORCED:
        forced += 1
        assert len(path) >= 3, f"forced path too short: {path}"
        assert path[0] == u and path[-1] == v, f"forced path endpoints wrong: {path}"
        for i in range(len(path) - 1):
            x, y = path[i], path[i + 1]
            assert has_edge(x, y), f"forced path uses a non-edge: {x} -> {y} in {path}"
        assert not any(
            (path[i], path[i + 1]) in ((u, v), (v, u)) for i in range(len(path) - 1)
        ), f"forced path still uses the direct edge: {path}"
        insert_counts.append(len(path) - 2)
    else:
        assert rule == STOP_ADJACENT_ONLY, f"unexpected rule: {rule}"
        no_stop_possible += 1
        assert path == [u, v], f"adjacent_only path should be exactly [u, v]: {path}"

insert_counts.sort()
if insert_counts:
    mn = insert_counts[0]
    mx = insert_counts[-1]
    mid = len(insert_counts) // 2
    median = (
        insert_counts[mid]
        if len(insert_counts) % 2
        else (insert_counts[mid - 1] + insert_counts[mid]) / 2
    )
else:
    mn = mx = median = None
# This count is a SAMPLING ARTIFACT, not a rate, and must not be read as one.
# edge_pairs is drawn by picking a random artist and then one of ITS edges
# (see the loop above), so an artist with few connections has each of its
# edges drawn far more often than that edge occurs in the graph -- exactly
# the artists MKS-1 describes as strandable. That inflates this sample's
# share of no-stop-possible pairs relative to the graph as a whole. The
# pair-level rate, drawn without that bias, is owned by
# findings/2026-07-25-mutual-knn-stranding.md (MKS-6); do not restate it
# here, and do not average this figure into it.
print(
    f"\nadjacent pairs sampled: {len(edge_pairs)} -> "
    f"no forcing needed: {no_forcing_needed}, forced: {forced}, "
    f"no stop possible in THIS BIASED SAMPLE (see comment above): {no_stop_possible}"
)
print(f"artists inserted per forced stop: min={mn}, median={median}, max={mx}")

print("\nall checks passed")
