"""Census of degree-1 and degree-2 nodes in the adopted 75k artifact.

READ-ONLY. Reads the adopted APG1 artifact and the crawl archive's key list;
writes nothing but its own JSON output. Rebuilds nothing, routes nothing,
changes no config.

Why these two sets are worth naming (structural, not measured here):

  - **degree 1** — `DRV-4` in `docs/superpowers/findings/2026-07-25-consulting-derivations.md`:
    an interior card needs a neighbour on each side, so a degree-1 node can only
    ever appear as one of the two artists the user typed. The app can never
    introduce anyone to it.
  - **degree 2** — reachable as an interior, but only on the single route through
    its two neighbours, so it is deliverable only if the router happens to price
    that exact detour.

Population, and why this script counts both (`DRV-4`'s open question — which
denominator `MKS-3`'s 9.3 % is against):

    build_from_archive (builder/src/artistpath_builder/pipeline.py:131,184) sets
    `known = set(payloads)` — the artists holding their OWN archived similarity
    response — and keeps a neighbour edge only `if n.mbid in known`. So a
    discovered-but-never-crawled artist is never a node. **Every artifact node
    is a crawled artist.** The two candidate denominators are therefore nested,
    not disjoint: artifact nodes (post special-purpose filter, post mutual-kNN
    cap, post largest-component prune) vs archived responses (the full crawled
    population). Both are printed and written.

Run from `api/` (it imports the API's reader, which is the code the app runs):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-26-low-degree-census/extract_low_degree.py

Artifact identity is asserted, not assumed: several graphs exist in
builder/scratch/ and they are not interchangeable (`DRV-1` is the record of what
happens when a measurement forgets that).
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

HERE = Path(__file__).resolve().parent
ARCHIVE = Path(__file__).resolve().parents[2] / "scratch" / "graph-archive" / "similar"


def load() -> tuple[GraphStore, str]:
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
    print(f"  sha256 {got}")
    return GraphStore.load(cfg.graph_path), got


def crawled_population() -> int | None:
    """Count archived similarity responses = the crawled population.

    Returns None if the archive is not on this machine; the artifact-node
    denominator still works, and the script says which one it could compute.
    """
    if not ARCHIVE.exists():
        return None
    return sum(1 for _ in ARCHIVE.rglob("*.json"))


def main() -> None:
    s, sha = load()
    off = np.asarray(s.offsets, dtype=np.int64)
    deg = np.diff(off)
    n = len(deg)
    pop = np.asarray(s.pop_raw, dtype=np.float64)

    crawled = crawled_population()
    print(f"\nartifact nodes          {n}")
    print(f"archived responses      {crawled if crawled is not None else 'archive not present'}")

    # Name collisions: a name shared by two or more nodes. The fame proxy
    # resolves by NAME (Wikipedia has no MBID index), so two nodes sharing a
    # name necessarily receive the SAME fame figure — which is wrong for at
    # least one of them whenever the sharers are different acts. This is the
    # single largest thing that could make the deliverable list misleading, so
    # it is flagged per row rather than counted in aggregate (P8b F8 keys the
    # join by mbid for the same reason).
    by_name: dict[str, list[int]] = defaultdict(list)
    for i, nm in enumerate(s.names):
        by_name[nm.strip().lower()].append(i)

    rows_by_degree: dict[int, list[dict]] = {1: [], 2: []}
    for target in (1, 2):
        for i in np.flatnonzero(deg == target):
            i = int(i)
            name = s.names[i]
            key = name.strip().lower()
            sharers = [j for j in by_name[key] if j != i]
            rows_by_degree[target].append({
                "mbid": s.mbids[i],
                "name": name,
                "disambiguation": s.disambiguations[i] or "",
                "degree": target,
                "pop_raw": float(pop[i]),
                "nameless": not name.strip(),
                # Recorded so the deliverable can flag it; never used to score.
                "name_shared_with": [
                    {"mbid": s.mbids[j], "degree": int(deg[j]),
                     "disambiguation": s.disambiguations[j] or ""}
                    for j in sharers
                ],
                "neighbours": [
                    {"mbid": s.mbids[int(v)], "name": s.names[int(v)],
                     "degree": int(deg[int(v)])}
                    for v in s.neighbours[off[i]:off[i + 1]]
                ],
            })

    d1, d2 = rows_by_degree[1], rows_by_degree[2]
    print(f"\ndegree 1                {len(d1)}")
    print(f"degree 2                {len(d2)}")
    print(f"degree 1 or 2           {len(d1) + len(d2)}")

    print("\n=== fractions, both denominators (DRV-4) ===")
    for label, rows in (("degree 1", d1), ("degree 2", d2), ("degree <=2", d1 + d2)):
        line = f"{label:<12} {100 * len(rows) / n:>6.2f}% of artifact nodes"
        if crawled:
            line += f"   {100 * len(rows) / crawled:>6.2f}% of crawled artists"
        print(line)

    nameless = [r for r in d1 + d2 if r["nameless"]]
    shared = [r for r in d1 + d2 if r["name_shared_with"]]
    print(f"\nnameless in the two sets       {len(nameless)}")
    print(f"name shared with another node  {len(shared)}")

    out = {
        "artifact_sha256": sha,
        "artifact_nodes": n,
        "archived_responses": crawled,
        "denominator_note": (
            "Every artifact node is a crawled artist (pipeline.py:131,184 — a node "
            "must hold its own archived response). The two denominators are nested: "
            "artifact nodes are the crawled population minus special-purpose "
            "filtering, minus nodes left edgeless by the mutual-kNN cap, minus the "
            "largest-component prune."
        ),
        "counts": {"degree_1": len(d1), "degree_2": len(d2)},
        "nameless": len(nameless),
        "name_collisions": len(shared),
        "degree_1": d1,
        "degree_2": d2,
    }
    dest = HERE / "low_degree.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
