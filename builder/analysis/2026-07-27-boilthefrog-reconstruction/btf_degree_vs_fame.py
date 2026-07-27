"""Degree vs popularity in BoilTheFrog's shipped graph, plus in/out-degree split.

The question this answers for artistpath: BoilTheFrog has NO reciprocity test,
yet its max degree is small. What bounds it?

Hypothesis: selecting each artist's 4 neighbours by POPULARITY PROXIMITY means
famous artists are only ever chosen by other famous artists, so the
"everyone points at The Beatles" in-degree blowup cannot happen.
"""

import json
import os
from collections import defaultdict, Counter

import btf_graph_measure as M


def main():
    artist_bl, edge_bl = M.load_blacklist()
    popularity, names = M.load_nodes()
    edge_lists = M.load_edges()

    # rebuild, tracking direction this time
    out_deg = Counter()
    in_deg = Counter()
    adj = defaultdict(set)
    nodes = set()

    for node, raw in edge_lists.items():
        if node in artist_bl or popularity.get(node, 0) < M.MIN_POPULARITY:
            continue
        nodes.add(node)
        good = [
            e for e in raw
            if e not in artist_bl
            and e not in edge_bl[node]
            and popularity.get(e, 0) >= M.MIN_POPULARITY
        ]
        pop = popularity[node]
        weighted = sorted(
            (1 + M.POP_WEIGHT * abs(pop - popularity.get(e, 0)) / 100.0, e) for e in good
        )
        kept = [e for _, e in weighted[:M.MAX_EDGES_PER_ARTIST]]
        out_deg[node] = len(kept)
        for t in kept:
            nodes.add(t)
            in_deg[t] += 1
            adj[node].add(t)
            adj[t].add(node)

    for n in nodes:
        adj.setdefault(n, set())

    print(f"nodes {len(nodes):,}")
    print(f"\nout-degree (capped at 4 by construction): "
          f"{dict(sorted(Counter(out_deg[n] for n in nodes).items()))}")

    ind = [in_deg[n] for n in nodes]
    ind_s = sorted(ind)
    print(f"in-degree: min {min(ind)} p50 {ind_s[len(ind)//2]} "
          f"p90 {ind_s[int(len(ind)*.9)]} p99 {ind_s[int(len(ind)*.99)]} max {max(ind)}")

    # ---- degree by popularity band ----
    print(f"\n{'='*74}")
    print("DEGREE BY SPOTIFY POPULARITY BAND (shipped graph)")
    print(f"{'='*74}")
    print(f"{'pop band':>10} {'artists':>9} {'mean deg':>9} {'med deg':>8} "
          f"{'max deg':>8} {'% deg<=2':>9} {'mean in':>8}")
    bands = [(30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 89), (90, 100)]
    for lo, hi in bands:
        sel = [n for n in nodes if lo <= popularity.get(n, 0) <= hi]
        if not sel:
            continue
        degs = [len(adj[n]) for n in sel]
        degs_s = sorted(degs)
        low = sum(1 for d in degs if d <= 2)
        print(f"{lo:>4}-{hi:<5} {len(sel):>9,} {sum(degs)/len(degs):>9.2f} "
              f"{degs_s[len(degs_s)//2]:>8} {max(degs):>8} "
              f"{100.0*low/len(sel):>8.2f}% "
              f"{sum(in_deg[n] for n in sel)/len(sel):>8.2f}")

    # ---- who are the most famous artists, and what degree do they have? ----
    print(f"\n{'='*74}")
    print("THE 20 MOST POPULAR ARTISTS IN THE GRAPH -- are they hubs?")
    print(f"{'='*74}")
    top_pop = sorted(nodes, key=lambda n: -popularity.get(n, 0))[:20]
    print(f"{'pop':>4} {'deg':>4} {'in':>4} {'out':>4}  name")
    for n in top_pop:
        print(f"{popularity.get(n,0):>4} {len(adj[n]):>4} {in_deg[n]:>4} "
              f"{out_deg[n]:>4}  {names.get(n,'?')}")

    # ---- correlation ----
    import statistics
    xs = [popularity.get(n, 0) for n in nodes]
    ys = [len(adj[n]) for n in nodes]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
    print(f"\nPearson r(popularity, degree) = {num/den:+.4f}")

    # ---- top 1% by degree: what is their popularity? ----
    by_deg = sorted(nodes, key=lambda n: -len(adj[n]))
    top1 = by_deg[:max(1, len(nodes) // 100)]
    print(f"\ntop 1% by degree ({len(top1):,} artists): "
          f"mean popularity {statistics.mean([popularity.get(n,0) for n in top1]):.1f}, "
          f"mean degree {statistics.mean([len(adj[n]) for n in top1]):.1f}")
    print(f"whole graph: mean popularity {statistics.mean(xs):.1f}, "
          f"mean degree {statistics.mean(ys):.2f}")


if __name__ == "__main__":
    main()
