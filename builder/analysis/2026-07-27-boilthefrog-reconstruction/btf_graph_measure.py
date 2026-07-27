"""Reconstruct BoilTheFrog's built graph from its committed crawl data.

Mirrors new_crawler/artist_graph.py::load_graph exactly, with ONE deliberate
omission that cannot be reproduced from this repo:

  skip_artists_with_no_tracks -- the track lists lived in the rocksdb, which is
  not committed. Every artist here is therefore treated as HAVING tracks. This
  makes the reconstruction an UPPER BOUND on node count and (weakly) on degree.

Everything else is faithful:
  min_popularity      = 30      membership floor, applied to node AND edge endpoint
  max_edges_per_artist = 4      per-source out-edge cap
  weight = 1 + pop_weight * |pop_src - pop_dst| / 100.0
  selection: sort by (weight, target_id) ascending, keep first 4
  symmetrisation: undirected union (nx.Graph)
  blacklist.csv applied (2 artists, 1 edge)

Also computes the counterfactual the source carries but switches off:
  simple_edges = True -- keep the first 4 by SIMILARITY RANK instead.
"""

import json
import os
from collections import defaultdict, Counter, deque

BTF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "btf")
G2 = os.path.join(BTF, "new_crawler", "g2")

MIN_POPULARITY = 30
MAX_EDGES_PER_ARTIST = 4
POP_WEIGHT = 100.0


def to_aid(uri_or_aid):
    if uri_or_aid:
        fields = uri_or_aid.split(":")
        if len(fields) == 3:
            return fields[2]
    return uri_or_aid


def load_blacklist():
    artist_bl, edge_bl = set(), defaultdict(set)
    with open(os.path.join(BTF, "new_crawler", "blacklist.csv")) as f:
        for line in f:
            line = line.strip()
            if not line or line[0] == "#":
                continue
            fields = [x.strip() for x in line.split(",")]
            if len(fields) > 1 and fields[0] == "artist":
                artist_bl.add(to_aid(fields[1]))
            elif fields[0] == "edge" and len(fields) > 2:
                a1, a2 = to_aid(fields[1]), to_aid(fields[2])
                edge_bl[a1].add(a2)
                edge_bl[a2].add(a1)
    return artist_bl, edge_bl


def load_nodes():
    """Bad lines are skipped, matching new_crawler/db.py:60 ('skipped bad line
    in db') -- the crawl data carries 3 truncated lines from unflushed writes."""
    popularity, names = {}, {}
    skipped = 0
    with open(os.path.join(G2, "nodes.js"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except ValueError:
                skipped += 1
                continue
            popularity[a["id"]] = a["popularity"]
            names[a["id"]] = a["name"]
    print(f"nodes.js: skipped {skipped} corrupt line(s)")
    return popularity, names


def load_edges():
    """edges.js: one {source_uri: [target_uri, ...]} per line. Later lines win
    on duplicate sources, matching a rocksdb overwrite."""
    out = {}
    skipped = 0
    with open(os.path.join(G2, "edges.js"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                skipped += 1
                continue
            for src, targets in d.items():
                out[to_aid(src)] = [to_aid(t) for t in targets]
    print(f"edges.js: skipped {skipped} corrupt line(s)")
    return out


def build(popularity, edge_lists, artist_bl, edge_bl, simple_edges=False):
    adj = defaultdict(set)
    nodes = set()

    for node, raw_edges in edge_lists.items():
        if node in artist_bl:
            continue
        if popularity.get(node, 0) < MIN_POPULARITY:
            continue
        nodes.add(node)

        good = [
            e for e in raw_edges
            if e not in artist_bl
            and e not in edge_bl[node]
            and popularity.get(e, 0) >= MIN_POPULARITY
        ]

        if simple_edges:
            kept = good[:MAX_EDGES_PER_ARTIST]
        else:
            pop = popularity[node]
            weighted = sorted(
                (1 + POP_WEIGHT * abs(pop - popularity[e]) / 100.0, e) for e in good
            )
            kept = [e for _, e in weighted[:MAX_EDGES_PER_ARTIST]]

        for t in kept:
            nodes.add(t)
            adj[t].add(node)
            adj[node].add(t)

    for n in nodes:
        adj.setdefault(n, set())
    return adj


def components(adj):
    seen, comps = set(), []
    for start in adj:
        if start in seen:
            continue
        comp, dq = 0, deque([start])
        seen.add(start)
        while dq:
            n = dq.popleft()
            comp += 1
            for m in adj[n]:
                if m not in seen:
                    seen.add(m)
                    dq.append(m)
        comps.append(comp)
    comps.sort(reverse=True)
    return comps


def pct(n, d):
    return 100.0 * n / d if d else 0.0


def report(label, adj, names, popularity):
    degs = [len(v) for v in adj.values()]
    degs_sorted = sorted(degs)
    n = len(degs)
    e = sum(degs) // 2
    comps = components(adj)

    print(f"\n{'=' * 68}\n{label}\n{'=' * 68}")
    print(f"nodes {n:,}   edges {e:,}   mean degree {2.0 * e / n:.2f}")
    print(f"components {len(comps)}   largest {comps[0]:,} "
          f"({pct(comps[0], n):.2f}% of nodes)")
    print(f"degree  min {min(degs)}  p50 {degs_sorted[n // 2]}  "
          f"p90 {degs_sorted[int(n * 0.90)]}  p99 {degs_sorted[int(n * 0.99)]}  "
          f"max {max(degs)}")

    c = Counter(degs)
    print("\n  deg :      count    share    cumulative")
    cum = 0
    for d in range(1, 13):
        cum += c.get(d, 0)
        print(f"  {d:>3} : {c.get(d, 0):>10,}  {pct(c.get(d, 0), n):>6.2f}%  "
              f"{pct(cum, n):>7.2f}%")
    at_least_4 = sum(v for k, v in c.items() if k >= 4)
    print(f"\n  degree >= 4 : {at_least_4:,} ({pct(at_least_4, n):.2f}%)")
    print(f"  degree <= 2 : {sum(v for k, v in c.items() if k <= 2):,} "
          f"({pct(sum(v for k, v in c.items() if k <= 2), n):.2f}%)")

    top = sorted(adj.items(), key=lambda kv: -len(kv[1]))[:10]
    print("\n  highest-degree artists:")
    for aid, nb in top:
        print(f"    {len(nb):>4}  {names.get(aid, '?')} (pop {popularity.get(aid, '?')})")
    return {"nodes": n, "edges": e, "degs": degs}


def main():
    artist_bl, edge_bl = load_blacklist()
    popularity, names = load_nodes()
    edge_lists = load_edges()

    print(f"crawl data: {len(popularity):,} artists in nodes.js, "
          f"{len(edge_lists):,} expanded sources in edges.js")
    print(f"blacklist: {len(artist_bl)} artists, "
          f"{sum(len(v) for v in edge_bl.values()) // 2} edge(s)")

    raw = [len(v) for v in edge_lists.values()]
    print(f"raw similar-list length: min {min(raw)} p50 "
          f"{sorted(raw)[len(raw) // 2]} max {max(raw)}")
    above = sum(1 for p in popularity.values() if p >= MIN_POPULARITY)
    print(f"artists with popularity >= {MIN_POPULARITY}: {above:,} "
          f"({pct(above, len(popularity)):.2f}% of crawled)")

    shipped = build(popularity, edge_lists, artist_bl, edge_bl, simple_edges=False)
    report("SHIPPED  (simple_edges=False: keep 4 closest in POPULARITY)",
           shipped, names, popularity)

    alt = build(popularity, edge_lists, artist_bl, edge_bl, simple_edges=True)
    report("COUNTERFACTUAL  (simple_edges=True: keep 4 top by SIMILARITY RANK)",
           alt, names, popularity)

    # How different are the two edge sets?
    def edgeset(adj):
        return {(a, b) for a in adj for b in adj[a] if a < b}

    es, ea = edgeset(shipped), edgeset(alt)
    inter = len(es & ea)
    print(f"\n{'=' * 68}\nEDGE-SET OVERLAP between the two selection rules\n{'=' * 68}")
    print(f"shipped {len(es):,}   rank-based {len(ea):,}   shared {inter:,}")
    print(f"Jaccard {100.0 * inter / len(es | ea):.2f}%   "
          f"shipped edges also in rank-based: {pct(inter, len(es)):.2f}%")


if __name__ == "__main__":
    main()
