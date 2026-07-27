"""Which knob bounds BoilTheFrog's degree? A 2x2 factor table.

SYN-6 states that separating "reciprocity" from "bounded degree" needs a
cap_strategy that does not exist in artistpath. BoilTheFrog has NO reciprocity
test and IS degree-bounded, so it is a candidate for that missing strategy --
but only if the bounding comes from a knob artistpath could actually turn.

FACTOR TABLE
  variant   cap (edges/source)   selection criterion        isolating baseline
  A         4                    popularity proximity       -- (SHIPPED)
  B         4                    similarity rank            A  (criterion only)
  C         20 (= all)           popularity proximity       A  (cap only)
  D         20 (= all)           similarity rank            B  (cap only) / C (criterion only)

HELD CONSTANT, and why the intervention cannot change it:
  - min_popularity = 30. Membership is decided before edge selection, so no
    variant can admit or exclude a node. Verified: node counts move only via
    which targets get chosen, never via the floor.
  - The source's own list length. Spotify's related-artists returns at most 20
    (measured: p50 = 20, max = 20). Variant C/D "uncapped" therefore means
    "capped at 20 by the source, not by us" -- this is the ceiling that limits
    how far the comparison transfers, and it is stated rather than assumed.
  - No reciprocity test in ANY variant. That is the whole point: reciprocity is
    absent throughout, so any bounding observed is achieved without it.
"""

from collections import defaultdict, Counter
import statistics

import btf_graph_measure as M


def build(popularity, edge_lists, artist_bl, edge_bl, cap, criterion):
    adj = defaultdict(set)
    nodes = set()
    for node, raw in edge_lists.items():
        if node in artist_bl or popularity.get(node, 0) < M.MIN_POPULARITY:
            continue
        nodes.add(node)
        good = [e for e in raw
                if e not in artist_bl and e not in edge_bl[node]
                and popularity.get(e, 0) >= M.MIN_POPULARITY]
        if criterion == "rank":
            kept = good[:cap]
        else:
            pop = popularity[node]
            kept = [e for _, e in sorted(
                (1 + M.POP_WEIGHT * abs(pop - popularity[e]) / 100.0, e)
                for e in good)[:cap]]
        for t in kept:
            nodes.add(t)
            adj[node].add(t)
            adj[t].add(node)
    for n in nodes:
        adj.setdefault(n, set())
    return adj


def main():
    artist_bl, edge_bl = M.load_blacklist()
    popularity, names = M.load_nodes()
    edge_lists = M.load_edges()

    print(f"\n{'='*94}")
    print("FACTOR TABLE -- no variant applies a reciprocity test")
    print(f"{'='*94}")
    print(f"{'var':>4} {'cap':>4} {'criterion':>12} {'nodes':>8} {'edges':>9} "
          f"{'mean':>6} {'p99':>5} {'MAX':>6} {'%deg<=2':>8} {'top1% pop':>10}")

    results = {}
    for var, cap, crit in [("A", 4, "pop"), ("B", 4, "rank"),
                           ("C", 20, "pop"), ("D", 20, "rank")]:
        adj = build(popularity, edge_lists, artist_bl, edge_bl, cap, crit)
        degs = sorted(len(v) for v in adj.values())
        n = len(degs)
        low = sum(1 for d in degs if d <= 2)
        by_deg = sorted(adj, key=lambda x: -len(adj[x]))[:max(1, n // 100)]
        t1pop = statistics.mean(popularity.get(x, 0) for x in by_deg)
        label = "pop-proximity" if crit == "pop" else "sim-rank"
        print(f"{var:>4} {cap:>4} {label:>12} {n:>8,} {sum(degs)//2:>9,} "
              f"{statistics.mean(degs):>6.2f} {degs[int(n*.99)]:>5} "
              f"{max(degs):>6} {100.0*low/n:>7.2f}% {t1pop:>10.1f}")
        results[var] = (adj, degs)

    print(f"\n{'='*94}")
    print("READ OF THE TABLE")
    print(f"{'='*94}")
    a_max, b_max = max(results["A"][1]), max(results["B"][1])
    c_max, d_max = max(results["C"][1]), max(results["D"][1])
    print(f"  criterion effect at cap=4  (A vs B): max degree {a_max} -> {b_max}")
    print(f"  criterion effect at cap=20 (C vs D): max degree {c_max} -> {d_max}")
    print(f"  cap effect on pop-proximity (A vs C): max degree {a_max} -> {c_max}")
    print(f"  cap effect on sim-rank      (B vs D): max degree {b_max} -> {d_max}")

    # Who are the hubs in the uncapped sim-rank variant? (the artistpath shape)
    adjD = results["D"][0]
    print("\n  highest-degree artists under D (cap=20, sim-rank) -- "
          "the 'everyone points at the famous' shape:")
    for x in sorted(adjD, key=lambda y: -len(adjD[y]))[:8]:
        print(f"    {len(adjD[x]):>5}  {names.get(x,'?')} (pop {popularity.get(x,0)})")

    adjC = results["C"][0]
    print("\n  highest-degree artists under C (cap=20, pop-proximity):")
    for x in sorted(adjC, key=lambda y: -len(adjC[y]))[:8]:
        print(f"    {len(adjC[x]):>5}  {names.get(x,'?')} (pop {popularity.get(x,0)})")


if __name__ == "__main__":
    main()
