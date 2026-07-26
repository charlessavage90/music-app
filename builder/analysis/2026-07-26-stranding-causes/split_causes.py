"""Why each low-degree artist is low-degree: cap-stranded vs crawl-frontier.

READ-ONLY. Reads the crawl archive and a dump of the adopted artifact's node
table; writes only its own JSON. Rebuilds nothing, routes nothing, adopts
nothing, changes no config.

The question. `findings/2026-07-26-low-degree-census.md` counts the artists the
app can never introduce anyone to (degree 1) or can only reach down a single
corridor (degree 2). That set mixes two causes with nothing in common but their
symptom:

  (a) CAP-STRANDED — the artist has a full candidate list of artists that ARE in
      the graph, and almost none of them rank it back. Its degree is destroyed
      by the mutual-kNN reciprocity rule. `MKS-2`'s worked example is Meat Loaf:
      50 candidates, 1 reciprocated.
  (b) CRAWL-FRONTIER — the artist sits at the edge of the snowball crawl, so few
      of its candidates were ever crawled. Its degree would stay low under any
      cap rule, because there is nothing there to keep.

Method. The candidate model is `reciprocity.py`'s, imported rather than copied,
so there is one implementation of the builder's cap and it keeps its validation
gate (six artists whose predicted neighbour sets must match the shipped graph).

**One correction to that model, and it is load-bearing here.** `reciprocity.py`
takes the candidate population to be the set of archived responses. The builder
does not: `pipeline.build_from_archive` computes `known = set(payloads)` and then
`known -= excluded`, dropping MusicBrainz special-purpose placeholders BEFORE any
ranking (`pipeline.py:131-152`). Modelling that population one member too large
does two things — it lets a placeholder occupy a slot in someone's top-50 and
push a real candidate out, and it inflates the candidate-pool count, **which is
the exact quantity this split keys on.** So the exclusion is imported from the
builder and applied to `reciprocity.KNOWN`. Both models are gated: `validate()`
runs before and after the correction, and the modelled degree is compared with
the artifact's own degree for all ~12k measured artists, not six.

Run from `builder/`, after `dump_artifact_nodes.py` has run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-stranding-causes/split_causes.py

`pop_raw` selects WHO TO SHOW and ranks nothing — log §2.11. It is carried here
only so the report can pick the rows the owner will actually read, exactly as the
census used it, and it is sound for that because popularity is accumulated before
the cap: the reciprocity rule destroys degree and leaves popularity untouched.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

from artistpath_builder.pipeline import is_special_purpose
from artistpath_builder.sources.listenbrainz import harvest_identities

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

HERE = Path(__file__).resolve().parent
RECIPROCITY = HERE.parent / "2026-07-25-mutual-knn-stranding" / "reciprocity.py"


def import_reciprocity():
    """Import the 2026-07-25 candidate model unmodified, with its gate intact.

    Its ARCHIVE path is relative to `builder/` and `KNOWN` is computed at import
    time, so this must run with `builder/` as the working directory. Importing
    rather than copying means there is still exactly one implementation of the
    builder's cap.
    """
    spec = importlib.util.spec_from_file_location("reciprocity", RECIPROCITY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["reciprocity"] = mod
    spec.loader.exec_module(mod)
    return mod


def special_purpose_mbids(rec) -> set[str]:
    """The placeholder entities the builder drops before ranking.

    Streams the archive rather than materialising it: `harvest_identities` takes
    an iterable, and the full payload set does not need to be resident.
    """
    files = sorted(rec.ARCHIVE.glob("*.json"))
    identities = harvest_identities(p.read_bytes() for p in files)
    return {
        mbid
        for mbid, (_name, disambiguation) in identities.items()
        if is_special_purpose(disambiguation)
    }


def uncapped_pool(rec, mbid: str) -> tuple[int, int]:
    """An artist's own candidate counts: (offered by the source, in-population).

    Both are needed and they answer different questions. `n_offered` is how many
    similar artists the SOURCE named for this artist at all; `n_pool` is how many
    of those the builder could actually use, i.e. that were themselves crawled.
    A large gap means the artist's neighbours sit outside the crawl — the
    frontier case. A small `n_offered` means the source itself knows almost
    nothing about the artist, which no amount of crawling fixes and which is a
    different problem wearing the same symptom.

    `top_k` truncates to K and so cannot answer either. The in-population filter
    matches `top_k`'s exactly — same `KNOWN` test, same self-exclusion, same list
    semantics (duplicates kept). The `min(pool, K) == len(top_k)` assertion in
    `main` is what proves it matches.
    """
    f = rec.ARCHIVE / f"{mbid}.json"
    if not f.exists():
        return -1, -1
    rows = json.loads(f.read_text(encoding="utf-8"))
    offered = [r for r in rows if r.get("artist_mbid") and r.get("artist_mbid") != mbid]
    pool = sum(1 for r in offered if r["artist_mbid"] in rec.KNOWN)
    return len(offered), pool


def main() -> None:
    nodes = json.loads((HERE / "artifact_nodes.json").read_text(encoding="utf-8"))
    if nodes["artifact_sha256"] != ADOPTED_SHA256:
        raise SystemExit(
            "node dump is not from the adopted graph.\n"
            f"  expected {ADOPTED_SHA256}\n  got      {nodes['artifact_sha256']}"
        )
    node_mbids = nodes["mbids"]
    node_names = nodes["names"]
    node_degree = nodes["degree"]
    node_pop = nodes["pop_raw"]
    in_graph = set(node_mbids)
    print(f"artifact verified via node dump, sha256 {ADOPTED_SHA256}")
    print(f"artifact nodes {len(node_mbids)}")

    rec = import_reciprocity()
    print(f"\narchived responses {len(rec.KNOWN)}, k = {rec.K}")
    print("gate 1 — the 2026-07-25 model, unmodified:")
    rec.validate()

    excluded = special_purpose_mbids(rec)
    in_archive = {m for m in excluded if m in rec.KNOWN}
    print(f"\nspecial-purpose placeholders: {len(excluded)} seen, "
          f"{len(in_archive)} of them hold an archived response")
    rec.KNOWN = rec.KNOWN - excluded
    rec.top_k.cache_clear()
    print(f"corrected candidate population {len(rec.KNOWN)}")
    print("gate 2 — the same model with the builder's exclusion applied:")
    rec.validate()

    # ---- the measured population: every artifact node with degree <= 2 -------
    targets = [i for i, d in enumerate(node_degree) if d <= 2]
    target_mbid = {node_mbids[i] for i in targets}
    n_d1 = sum(1 for i in targets if node_degree[i] == 1)
    print(f"\nmeasured population: degree <= 2 = {len(targets)}")
    print(f"  degree 1 {n_d1}   degree 2 {len(targets) - n_d1}")

    # ---- one pass over the archive, kept to integer ids ----------------------
    # Two structures come out of it and neither holds a parsed response:
    #   own_candidates[t]  the target's own top-K
    #   ranked_back[t]     every artist whose own top-K contains the target
    # n_reciprocated is |own_candidates & ranked_back| — that is the mutual rule.
    crawled_sorted = sorted(rec.KNOWN)
    crawled_ids = {m: n for n, m in enumerate(crawled_sorted)}
    own_candidates: dict[int, list[int]] = {}
    ranked_back: dict[int, set[int]] = defaultdict(set)
    target_ids = {crawled_ids[m] for m in target_mbid if m in crawled_ids}

    print("\nscanning archive...")
    for seen, mbid in enumerate(crawled_sorted, start=1):
        top = rec.top_k(mbid)
        if top is None:
            continue
        me = crawled_ids[mbid]
        ids = [crawled_ids[d] for d, _n, _s in top]
        if me in target_ids:
            own_candidates[me] = ids
        for other in ids:
            if other in target_ids:
                ranked_back[other].add(me)
        if seen % 5000 == 0:
            # Bound memory: the cache holds a parsed top-K per file touched,
            # and this pass touches every one of them.
            rec.top_k.cache_clear()
            print(f"  {seen}/{len(crawled_sorted)}", flush=True)
    rec.top_k.cache_clear()

    crawled_in_graph = [m in in_graph for m in crawled_sorted]

    # ---- per-artist rows ----------------------------------------------------
    rows = []
    pool_mismatch = []
    degree_mismatch = []
    for i in targets:
        mbid = node_mbids[i]
        cid = crawled_ids.get(mbid)
        if cid is None or cid not in own_candidates:
            pool_mismatch.append({"mbid": mbid, "why": "no archived response"})
            continue

        cands = own_candidates[cid]
        n_cand = len(cands)
        n_offered, n_pool = uncapped_pool(rec, mbid)
        if min(n_pool, rec.K) != n_cand:
            pool_mismatch.append({"mbid": mbid, "pool": n_pool, "top_k": n_cand})

        back = ranked_back.get(cid, set())
        n_recip = len(set(cands) & back)
        if n_recip != node_degree[i]:
            degree_mismatch.append({
                "mbid": mbid, "name": node_names[i],
                "modelled": n_recip, "artifact": node_degree[i],
            })

        rows.append({
            "mbid": mbid,
            "name": node_names[i],
            "degree": node_degree[i],
            "pop_raw": node_pop[i],
            # How many similar artists the SOURCE named for this artist at all.
            "n_offered": n_offered,
            # ...of those, how many were themselves crawled, so the builder
            # could actually use them. The gap is the crawl frontier.
            "n_pool": n_pool,
            # ...capped to K: the list the reciprocity rule actually judged.
            "n_candidates": n_cand,
            # ...of those, how many are artifact NODES rather than merely
            # crawled. The gap is whoever the cap or the component prune removed.
            "n_candidates_in_graph": sum(1 for c in cands if crawled_in_graph[c]),
            # ...and how many ranked this artist back. This is its degree.
            "n_reciprocated": n_recip,
            # Everyone who lists this artist in their own top-K, whether or not
            # it lists them. Not part of the mutual rule — recorded because the
            # frontier/cap question is "would this degree survive ANY cap rule",
            # and a one-directional rule would keep exactly these. An artist
            # nobody lists is beyond the reach of any rule; one that 30 artists
            # list is stranded only by the both-ways requirement.
            "n_ranked_by_others": len(back),
        })

    print(f"\nrows measured {len(rows)}")
    print(f"gate 3 — uncapped pool consistent with top_k: "
          f"{len(pool_mismatch)} mismatches (must be 0)")
    print(f"gate 4 — modelled degree equals artifact degree: "
          f"{len(degree_mismatch)} disagreements over {len(rows)} artists")
    if pool_mismatch:
        for m in pool_mismatch[:10]:
            print("   ", m)
        raise SystemExit("ABORTING: the uncapped-pool filter does not match top_k")
    for m in degree_mismatch[:20]:
        print("   ", m)

    out = {
        "artifact_sha256": ADOPTED_SHA256,
        "artifact_nodes": len(node_mbids),
        "archived_responses": len(rec.KNOWN) + len(in_archive),
        "candidate_population": len(rec.KNOWN),
        "special_purpose_excluded": len(in_archive),
        "k": rec.K,
        "degree_disagreements": degree_mismatch,
        "rows": rows,
    }
    dest = HERE / "causes.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
