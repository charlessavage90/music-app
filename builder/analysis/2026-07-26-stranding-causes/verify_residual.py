"""Reproduce the two settled explanations for the model/artifact residual.

READ-ONLY. `REPORT.md`'s gate section makes two specific numeric claims about
why the modelled degree and the artifact's degree disagree. This script is what
makes them checkable; without it they are assertions.

  1. **The builder drops MusicBrainz placeholder entities before ranking and
     `reciprocity.py` does not.** Claim: modelling that population one member too
     large produced 17 disagreements, and applying the builder's own exclusion
     brings it to 10.
  2. **The builder drops rows carrying no similarity score; `reciprocity.py`
     keeps them as zero.** Claim: this cannot matter, because there are no such
     rows in the archive at all.

The ten that survive both sit at the rank-50 boundary of a partner's list and
were left alone deliberately - see `REPORT.md`. This script does not chase them.

Run from `builder/`, after `split_causes.py`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-stranding-causes/verify_residual.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import split_causes as sc

HERE = Path(__file__).resolve().parent


def disagreements(rec, node_mbids, node_degree) -> int:
    """Count artists whose modelled degree differs from the artifact's."""
    targets = {node_mbids[i] for i, d in enumerate(node_degree) if d <= 2}
    ranked_back: dict[str, set[str]] = defaultdict(set)
    own: dict[str, list[str]] = {}
    for mbid in sorted(rec.KNOWN):
        top = rec.top_k(mbid)
        if top is None:
            continue
        ids = [d for d, _n, _s in top]
        if mbid in targets:
            own[mbid] = ids
        for other in ids:
            if other in targets:
                ranked_back[other].add(mbid)
    rec.top_k.cache_clear()

    degree_of = {node_mbids[i]: d for i, d in enumerate(node_degree)}
    return sum(
        1
        for m in targets
        if m in own
        and len(set(own[m]) & ranked_back.get(m, set())) != degree_of[m]
    )


def main() -> None:
    nodes = json.loads((HERE / "artifact_nodes.json").read_text(encoding="utf-8"))
    if nodes["artifact_sha256"] != sc.ADOPTED_SHA256:
        raise SystemExit("node dump is not from the adopted graph")
    node_mbids, node_degree = nodes["mbids"], nodes["degree"]

    rec = sc.import_reciprocity()

    print("=== claim 1: the placeholder exclusion ===")
    before = disagreements(rec, node_mbids, node_degree)
    print(f"  disagreements WITHOUT the builder's exclusion: {before}")

    excluded = sc.special_purpose_mbids(rec)
    rec.KNOWN = rec.KNOWN - excluded
    rec.top_k.cache_clear()
    after = disagreements(rec, node_mbids, node_degree)
    print(f"  placeholders dropped: {len(excluded)}")
    print(f"  disagreements WITH the builder's exclusion:    {after}")
    print(f"  accounted for by the exclusion: {before - after}")

    print("\n=== claim 2: rows carrying no similarity score ===")
    total_rows = missing_score = 0
    for f in sorted(rec.ARCHIVE.glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            total_rows += 1
            if r.get("score") is None:
                missing_score += 1
    print(f"  rows in the archive: {total_rows}")
    print(f"  rows with no score:  {missing_score}")
    print("  -> the builder/model difference on this cannot bite"
          if missing_score == 0 else "  -> IT BITES; the report is wrong")


if __name__ == "__main__":
    main()
