"""How much edge ordering does the p99 clip destroy, and is it enough to route differently?

README owns the question, the decision rule and the figures. The rule was committed at
`0e39522`, before this script produced a number.

Reproduces the adopted build from the archive **in memory**, recovering the one quantity the
artifact does not retain: the unclipped strength of a saturated edge. No artifact is written
-- `serialise()` is called only to hash, and the bytes are discarded.

Two self-checks, both fail-loud, because a wrong replication here would look exactly like a
real measurement:

  1. **Identity gate.** The in-memory graph must serialise to the adopted artifact's sha256.
     That proves this replication is the code path that produced the graph in use.
  2. **Formula gate.** The unclipped expression must agree with the real `rescale_scores`
     on every edge where the `min` does not bind. That proves the only difference is the clip.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
        analysis/2026-07-25-ceiling-ordering-headroom/measure_headroom.py
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import serialise
from artistpath_builder.config import BuilderConfig
from artistpath_builder.graph import (
    build_graph,
    largest_component,
    mutual_knn_cap,
    symmetrise,
)
from artistpath_builder.models import ArtistStats
from artistpath_builder.pipeline import (
    damped_strength,
    is_special_purpose,
    rescale_scores,
)
from artistpath_builder.sources.listenbrainz import (
    ListenBrainzSource,
    harvest_identities,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "builder" / "scratch" / "graph-archive"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

# Cost weights: cited from `api/src/artistpath_api/config.py` (ApiConfig defaults), which is
# where they live and where the mirror reads them. Not restated as new figures.
W_SIM = 3.0
W_HOP = 0.02
CEILING = 1.0


def main() -> int:
    # Era pin 2026-08-06 (MSW- adoption): cap_strategy flipped to
    # "trimmed_union" there. This probe reimplements the cap directly
    # (mutual_knn_cap below) rather than going through build_from_archive, so
    # it was NOT on Task 11's era-pin list — but it reads the default in the
    # assert three lines down, which would fire and stop the probe running.
    # Pinned rather than deleted: the assert stays as the guard it was, and
    # this line is what keeps it true.
    config = BuilderConfig(cap_strategy="mutual_knn")
    assert config.similarity_rescale == "p99_log_clip"
    assert config.cap_strategy == "mutual_knn"
    assert config.max_neighbours_per_artist == 50
    assert config.similarity_damping == 0.0

    source = ListenBrainzSource(config)
    archive = LocalArchive(ARCHIVE)
    prefix = f"similar/{source.name}/"

    print("reading archive ...")
    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if key.startswith(prefix) and key.endswith(".json"):
            p = archive.get(key)
            if p is not None:
                payloads[key[len(prefix): -len(".json")]] = p
    print(f"  {len(payloads):,} archived responses")

    known = set(payloads)
    identities = harvest_identities(payloads.values())
    excluded = {m for m, (_n, dis) in identities.items() if is_special_purpose(dis)} \
        if config.filter_special_purpose else set()
    known -= excluded

    raw_lists, mass = {}, {}
    for mbid in sorted(known):
        nb = [n for n in source.parse(payloads[mbid], exclude_mbid=mbid)
              if n.mbid not in excluded]
        raw_lists[mbid] = nb
        mass[mbid] = sum(n.score for n in nb) or 1.0

    scored_adjacency: dict[str, list[tuple[str, float]]] = {}
    for mbid in sorted(known):
        scored = [(n.mbid, damped_strength(n.score, mass[mbid], mass[n.mbid], 0.0))
                  for n in raw_lists[mbid] if n.mbid in known]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        scored_adjacency[mbid] = scored

    flat, layout = [], []
    for mbid, scored in scored_adjacency.items():
        layout.append((mbid, [d for d, _ in scored]))
        flat.extend(v for _d, v in scored)

    rescaled = rescale_scores(flat, strategy=config.similarity_rescale, damping=0.0)

    # The same expression with the `min` removed. Mirrors `rescale_scores` lines-for-line.
    raw = [math.expm1(max(0.0, v)) for v in flat]
    scale = float(np.percentile(raw, 99))
    log_scale = math.log1p(scale)
    unclipped = [math.log1p(max(0.0, v)) / log_scale for v in raw]

    # GATE 2 -- formula. Agreement wherever the clip does not bind.
    bad = [i for i, (r, u) in enumerate(zip(rescaled, unclipped))
           if r < CEILING and r != u]
    assert not bad, f"formula gate FAILED on {len(bad):,} unclipped edges"
    n_sat = sum(1 for r in rescaled if r >= CEILING)
    print(f"  formula gate ok — agrees on all {len(flat) - n_sat:,} unsaturated edges")
    print(f"  saturated (directed, pre-cap): {n_sat:,} of {len(flat):,} "
          f"= {100 * n_sat / len(flat):.2f} %")

    score_weighted_indegree: dict[str, float] = defaultdict(float)
    adjacency, unclip_adj = {}, {}
    cursor = 0
    for mbid, dsts in layout:
        edges, uedges = {}, {}
        for dst in dsts:
            edges[dst] = rescaled[cursor]
            uedges[dst] = unclipped[cursor]
            cursor += 1
        adjacency[mbid], unclip_adj[mbid] = edges, uedges
        for dst, sc in edges.items():
            score_weighted_indegree[dst] += sc

    ranking = {m: dict(s) for m, s in scored_adjacency.items()}
    adjacency = mutual_knn_cap(adjacency, config.max_neighbours_per_artist, ranking=ranking)
    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)
    pruned = {n: {d: s for d, s in e.items() if d in keep}
              for n, e in adjacency.items() if n in keep}
    stats = [ArtistStats(mbid=m, name=identities.get(m, ("", ""))[0],
                         pop_indegree_scaled=round(score_weighted_indegree[m] * 1000),
                         listen_count=0, disambiguation=identities.get(m, ("", ""))[1])
             for m in keep]
    graph = build_graph(pruned, stats, source.edge_type)

    # GATE 1 -- identity. Hash only; the bytes are discarded, no artifact is written.
    digest = hashlib.sha256(serialise(graph)).hexdigest()
    if digest != ADOPTED_SHA:
        print(f"\n*** IDENTITY GATE FAILED ***\n  got      {digest}\n  expected {ADOPTED_SHA}")
        print("  The archive does not reproduce the adopted graph. Every figure is VOID.")
        return 1
    print(f"  identity gate ok — reproduces the adopted artifact {digest[:8]}...{digest[-7:]}")

    # --- the measurement -------------------------------------------------------------
    # Undirected edge value = max over directions (`symmetrise` keeps the stronger score,
    # and the rescale is monotone, so the max carries across to the unclipped side).
    def uval(a: str, b: str) -> float:
        return max(unclip_adj.get(a, {}).get(b, float("-inf")),
                   unclip_adj.get(b, {}).get(a, float("-inf")))

    # The renormalisation the README pre-registered: same formula, divisor moved from p99
    # to the max, so nothing saturates. k < 1 shrinks every score uniformly.
    u_max = max(unclipped)
    k = log_scale / math.log1p(max(raw))
    print(f"\nrenormalisation factor k = {k:.4f}  "
          f"(largest unclipped value {u_max:.3f} in p99 units)")

    per_node, sat_nodes = {}, []
    for node, edges in pruned.items():
        ceil = [d for d, s in edges.items() if s >= CEILING]
        if len(ceil) < 2:
            continue
        us = [uval(node, d) for d in ceil]
        spread_p99 = W_SIM * (max(us) - min(us))
        per_node[node] = {"n_ceiling": len(ceil), "n_edges": len(edges),
                          "spread_p99_units": spread_p99,
                          "spread_renorm": spread_p99 * k,
                          "fully_saturated": len(ceil) == len(edges)}
        if len(ceil) == len(edges):
            sat_nodes.append(node)

    def report(label: str, nodes: list[str]) -> dict:
        if not nodes:
            print(f"\n{label}: none")
            return {}
        v = sorted(per_node[n]["spread_renorm"] / W_HOP for n in nodes)
        p = sorted(per_node[n]["spread_p99_units"] / W_HOP for n in nodes)
        out = {"n_nodes": len(nodes),
               "median_x_w_hop": statistics.median(v),
               "mean_x_w_hop": statistics.mean(v),
               "p10_x_w_hop": v[len(v) // 10], "p90_x_w_hop": v[-max(1, len(v) // 10)],
               "median_x_w_hop_p99_units": statistics.median(p),
               "frac_over_1x": sum(1 for x in v if x >= 1) / len(v),
               "frac_over_7_5x": sum(1 for x in v if x >= 7.5) / len(v),
               "frac_over_30x": sum(1 for x in v if x >= 30) / len(v)}
        print(f"\n{label}  (n = {len(nodes):,})")
        print(f"  cost spread among a node's own ceiling exits, in multiples of w_hop:")
        print(f"    median {out['median_x_w_hop']:8.2f}   mean {out['mean_x_w_hop']:8.2f}"
              f"   p10 {out['p10_x_w_hop']:7.2f}   p90 {out['p90_x_w_hop']:8.2f}")
        print(f"    >= 1x w_hop: {100 * out['frac_over_1x']:5.1f} %   "
              f">= 7.5x: {100 * out['frac_over_7_5x']:5.1f} %   "
              f">= 30x: {100 * out['frac_over_30x']:5.1f} %")
        return out

    results = {
        "artifact_sha256": digest,
        "saturated_directed_edges": n_sat, "total_directed_edges": len(flat),
        "renormalisation_k": k,
        "all_nodes_with_2plus_ceiling_edges": report(
            "ALL nodes holding >= 2 ceiling edges", sorted(per_node)),
        "fully_saturated_nodes": report(
            "FULLY SATURATED nodes (every exit at the ceiling)", sorted(sat_nodes)),
    }

    name_to_mbid = {}
    for m in pruned:
        nm = identities.get(m, ("", ""))[0]
        if nm:
            name_to_mbid.setdefault(nm, m)
    endpoints = ["Miles Davis", "Daft Punk", "The Shins", "Wishbone Ash", "Metallica",
                 "Taylor Swift", "Radiohead", "The Beatles", "Muse", "Coldplay",
                 "Madonna", "Bob Dylan", "Pink Floyd", "Aphex Twin", "Nirvana", "CROOVE",
                 "Arctic Monkeys", "Johnny Cash", "Michael Jackson", "Gorillaz",
                 "System of a Down", "R.E.M.", "The Rolling Stones", "Linkin Park"]
    ep = [name_to_mbid[n] for n in endpoints
          if n in name_to_mbid and name_to_mbid[n] in per_node]
    results["pre_registered_endpoints"] = report(
        "The 24 PRE-REGISTERED ENDPOINTS (where TF-D1's forced hops live)", ep)

    print("\nper-endpoint detail (spread in multiples of w_hop, renormalised):")
    for nm in endpoints:
        m = name_to_mbid.get(nm)
        if m in per_node:
            r = per_node[m]
            print(f"  {nm:<20} {r['spread_renorm'] / W_HOP:8.2f}   "
                  f"{r['n_ceiling']:>3}/{r['n_edges']:>3} exits at ceiling"
                  f"{'   [FULLY SATURATED]' if r['fully_saturated'] else ''}")

    (HERE / "headroom.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    med = results["all_nodes_with_2plus_ceiling_edges"]["median_x_w_hop"]
    verdict = "WIDE" if med >= 1.0 else "NARROW"
    meaning = ("the clip destroys ordering big enough to flip routing decisions"
               if med >= 1.0 else "re-ranking is smaller than one extra step")
    print(f"\n{'=' * 70}\nDECISION RULE (committed at 0e39522, before this ran):")
    print(f"  median per-node ceiling cost spread = {med:.2f} x w_hop")
    print(f"  -> {verdict}: {meaning}")
    print(f"\nwrote {HERE / 'headroom.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
