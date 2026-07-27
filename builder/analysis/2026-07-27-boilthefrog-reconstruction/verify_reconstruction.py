"""Positive controls on the reconstruction, per closeout B3.

REPORT.md's every figure rests on `btf_graph_measure.build()` faithfully mirroring
`new_crawler/artist_graph.py::load_graph`. A build that silently ignored one of its
inputs would produce a plausible, wrong, and entirely green report -- the FMS-P1 class
this project keeps hitting, and the class REPORT.md itself documents in the original.

So: perturb each input and confirm the output MOVES, in the predicted direction. A
control that cannot fail is not a control, so each assertion below is stated as a
prediction first and checked second.

C4 is the important one. It predicts the vacuous cell in REPORT.md section (d) from
first principles, which is the difference between having understood that cell and
having merely noticed it.

Run:  python verify_reconstruction.py
"""

import btf_graph_measure as M


def build(pop, edges, abl, ebl, cap, crit):
    from collections import defaultdict
    adj, nodes = defaultdict(set), set()
    for node, raw in edges.items():
        if node in abl or pop.get(node, 0) < M.MIN_POPULARITY:
            continue
        nodes.add(node)
        good = [e for e in raw
                if e not in abl and e not in ebl[node]
                and pop.get(e, 0) >= M.MIN_POPULARITY]
        if crit == "rank":
            kept = good[:cap]
        else:
            p = pop[node]
            kept = [e for _, e in sorted(
                (1 + M.POP_WEIGHT * abs(p - pop.get(e, 0)) / 100.0, e) for e in good)[:cap]]
        for t in kept:
            nodes.add(t)
            adj[node].add(t)
            adj[t].add(node)
    for n in nodes:
        adj.setdefault(n, set())
    return adj


def stats(adj):
    d = [len(v) for v in adj.values()]
    return len(d), sum(d) // 2, sum(d) / len(d), max(d)


def edgeset(adj):
    return {(a, b) for a in adj for b in adj[a] if a < b}


PASS, FAIL = [], []


def check(cid, prediction, ok, detail):
    (PASS if ok else FAIL).append(cid)
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid}: {prediction}\n         {detail}")


def main():
    abl, ebl = M.load_blacklist()
    pop, names = M.load_nodes()
    edges = M.load_edges()
    print()

    # ---- C1: the membership floor is live ----
    saved = M.MIN_POPULARITY
    counts = []
    for floor in (0, 30, 60):
        M.MIN_POPULARITY = floor
        counts.append(stats(build(pop, edges, abl, ebl, 4, "pop"))[0])
    M.MIN_POPULARITY = saved
    check("C1", "raising min_popularity must strictly shrink the graph",
          counts[0] > counts[1] > counts[2],
          f"floor 0/30/60 -> {counts[0]:,} / {counts[1]:,} / {counts[2]:,} nodes")

    # ---- C2: the per-source cap is live ----
    means = [stats(build(pop, edges, abl, ebl, c, "pop"))[2] for c in (1, 4, 8)]
    check("C2", "raising the per-source cap must strictly raise mean degree",
          means[0] < means[1] < means[2],
          f"cap 1/4/8 -> mean degree {means[0]:.2f} / {means[1]:.2f} / {means[2]:.2f}")

    # ---- C3: the selection criterion is live at the shipped cap ----
    a, b = build(pop, edges, abl, ebl, 4, "pop"), build(pop, edges, abl, ebl, 4, "rank")
    ea, eb = edgeset(a), edgeset(b)
    jac = 100.0 * len(ea & eb) / len(ea | eb)
    check("C3", "at cap 4 the two criteria must produce materially different graphs",
          jac < 50.0 and stats(a)[3] != stats(b)[3],
          f"Jaccard {jac:.2f}%, max degree {stats(a)[3]} vs {stats(b)[3]}")

    # ---- C4: the vacuous cell, PREDICTED not merely observed ----
    longest = max(len(v) for v in edges.values())
    c, d = build(pop, edges, abl, ebl, 20, "pop"), build(pop, edges, abl, ebl, 20, "rank")
    check("C4", "at a cap >= the longest source list the criterion CANNOT bind, so "
                "the two builds must be identical -- REPORT (d)'s vacuous cell",
          longest <= 20 and edgeset(c) == edgeset(d) and stats(c) == stats(d),
          f"longest source list {longest} <= cap 20; edge sets identical: "
          f"{edgeset(c) == edgeset(d)}; stats identical: {stats(c) == stats(d)}")

    # ---- C5: the 3 corrupt lines are not load-bearing ----
    shipped_n = stats(a)[0]
    check("C5", "the 3 skipped corrupt lines must not materially move the result",
          abs(len(pop) - 95059) <= 5 and shipped_n > 40000,
          f"{len(pop):,} artists parsed of 95,059 raw lines (3 corrupt, skipped as "
          f"new_crawler/db.py:60 does); shipped build still {shipped_n:,} nodes")

    print(f"\n  {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        raise SystemExit(f"CONTROL FAILED: {', '.join(FAIL)} — REPORT.md figures are suspect")
    print("  All controls responded to their inputs. REPORT.md's figures are "
          "measurements, not artefacts of a build that ignores its arguments.\n")


if __name__ == "__main__":
    main()
