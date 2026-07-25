"""Artifact-side measurements for the 2026-07-25 mutual-kNN stranding finding.

READ-ONLY. Reads the adopted APG1 artifact only; writes nothing, rebuilds
nothing. Owns the degree-by-popularity table, the bridge counts, and the
name-collision count in
`docs/superpowers/findings/2026-07-25-mutual-knn-stranding.md`.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-25-mutual-knn-stranding/degree_and_bridges.py

Artifact identity is asserted, not assumed: several graphs exist in
builder/scratch/ and they are not interchangeable.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict

import numpy as np

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"


def load() -> GraphStore:
    cfg = ApiConfig()
    digest = hashlib.sha256()
    with open(cfg.graph_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    got = digest.hexdigest()
    if got != ADOPTED_SHA256:
        raise SystemExit(
            f"artifact is not the adopted graph.\n  expected {ADOPTED_SHA256}\n"
            f"  got      {got}\nSee findings/2026-07-23-tiebreak-fix-adoption.md."
        )
    print(f"artifact verified: {cfg.graph_path}")
    return GraphStore.load(cfg.graph_path)


def bridges(off: np.ndarray, nbr: np.ndarray, n: int) -> list[tuple[int, int]]:
    """Every edge whose removal disconnects the graph, by iterative Tarjan.

    Iterative rather than recursive: 74k nodes overflows CPython's stack.
    A bridge is exactly an adjacent pair with no alternative route, which is
    what makes it the set where a forced detour (F1) is impossible.
    """
    disc = np.full(n, -1, dtype=np.int64)
    low = np.zeros(n, dtype=np.int64)
    timer = 0
    found: list[tuple[int, int]] = []
    for root in range(n):
        if disc[root] != -1:
            continue
        disc[root] = low[root] = timer
        timer += 1
        stack = [[root, -1, int(off[root])]]
        while stack:
            frame = stack[-1]
            u, pu, i = frame
            if i < off[u + 1]:
                frame[2] = i + 1
                v = int(nbr[i])
                if v == pu:  # simple graph: the parent edge occurs once
                    continue
                if disc[v] == -1:
                    disc[v] = low[v] = timer
                    timer += 1
                    stack.append([v, u, int(off[v])])
                elif disc[v] < low[u]:
                    low[u] = disc[v]
            else:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    low[p] = min(low[p], low[u])
                    if low[u] > disc[p]:
                        found.append((p, u))
    return found


def main() -> None:
    s = load()
    off = np.asarray(s.offsets, dtype=np.int64)
    nbr = np.asarray(s.neighbours, dtype=np.int64)
    n = len(off) - 1
    deg = np.diff(off)
    pop = np.asarray(s.pop_raw, dtype=np.float64)

    print(f"\nnodes = {n}, undirected edges = {len(nbr) // 2}")

    print("\n=== surviving connections by popularity decile ===")
    print(f"{'decile':>9} {'median':>7} {'mean':>7} {'% deg<=2':>9} {'n':>7}")
    qs = np.percentile(pop, np.arange(0, 101, 10))
    for i in range(10):
        m = (pop >= qs[i]) & (pop < qs[i + 1]) if i < 9 else (pop >= qs[i])
        d = deg[m]
        print(
            f"{i * 10:>4}-{(i + 1) * 10:<4} {np.median(d):>7.0f} {d.mean():>7.1f}"
            f" {100 * (d <= 2).mean():>8.1f}% {m.sum():>7}"
        )

    br = bridges(off, nbr, n)
    leaf = sum(1 for a, b in br if deg[a] == 1 or deg[b] == 1)
    print("\n=== pairs with no possible detour (bridge edges) ===")
    print(f"total                              {len(br)}")
    print(f"  one artist has a single edge     {leaf}")
    print(f"  both artists have 2+ edges       {len(br) - leaf}")

    thr = np.percentile(pop, 90)
    print("\n=== no-detour pairs, both endpoints top-10% by popularity ===")
    for a, b in sorted(
        (p for p in br if pop[p[0]] >= thr and pop[p[1]] >= thr),
        key=lambda p: -min(pop[p[0]], pop[p[1]]),
    ):
        print(
            f"  {s.names[a]} (deg {deg[a]}) <-> {s.names[b]} (deg {deg[b]})"
        )

    by_name: dict[str, list[int]] = defaultdict(list)
    for i, nm in enumerate(s.names):
        by_name[nm.lower()].append(i)
    dupes = {k: v for k, v in by_name.items() if len(v) > 1}
    involved = sum(len(v) for v in dupes.values())
    print("\n=== name collisions (unexamined; recorded only) ===")
    print(f"names appearing more than once: {len(dupes)}")
    print(f"artists involved: {involved} ({100 * involved / n:.2f}%)")


if __name__ == "__main__":
    main()
