"""The accepted no-release drop list, frozen -- plus what removing it costs.

STATUS: this is an ADOPTED owner decision (2026-08-01), not a diagnostic. The
rule and the population were accepted for the next build. The three scripts
that produced the evidence stay diagnostic; this file freezes their output into
the artifact a build can consume.

THE RULE, as accepted
    Drop a graph artist iff ALL of:
      - no MusicBrainz release group (absent or empty in rel_rg_raw.json), AND
      - no Discogs release through the MB-sourced Discogs id, AND
      - NOT (a commercial-DSP link AND a clip resolves through the app's own
        Deezer->iTunes path)
    i.e. keep a release-less artist only where a distributor put it on Spotify,
    Apple, Deezer or Tidal AND something actually plays.

WHY THE LIST IS FROZEN RATHER THAN RECOMPUTED AT BUILD TIME
  **Determinism (spec section 9) forbids the alternative.** The builder is
  required to produce byte-identical output for identical input, and the crawl
  is the only input it reads -- `build_from_archive` is offline by a hard rule
  with a replay test that injects a raising fetcher to prove it. A drop rule
  that called Deezer during a build would make every build depend on a third
  party's mood, and two builds of the same archive would differ. So the network
  half of this rule is resolved ONCE, here, and the result is committed.

  The consequence, stated rather than discovered later: this list is a
  SNAPSHOT. Clips appear and disappear; a rebuild in six months applies
  2026-08-01's answer. Re-resolving is a deliberate act with its own decision,
  never a silent build-time refresh.

WHAT THIS FILE DOES NOT DO
  It does not modify the builder. Wiring the list into `pipeline.py`'s
  `excluded` set -- beside the nameless drop, which is the exact precedent --
  is a code change owing tests, and no build is pending. The list and its
  condition are recorded in NEXT.md so it cannot be silently skipped.
"""
from __future__ import annotations

import json
import sys
from collections import deque
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
for _p in (_TAS, ROOT / "api" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from tas_common import ADOPTED, ADOPTED_SHA  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402

SIGNALS = HERE / "tail_signals.json"
CLIPS = HERE / "tail_clips.json"
OUT = HERE / "tail_droplist.json"


def largest_component_size(store, dropped: set[int]) -> tuple[int, int]:
    """(size of the largest component, nodes outside it) after removing `dropped`."""
    n = len(store.mbids)
    alive = [i for i in range(n) if i not in dropped]
    seen: set[int] = set()
    best = 0
    for start in alive:
        if start in seen:
            continue
        size = 0
        q = deque([start])
        seen.add(start)
        while q:
            u = q.popleft()
            size += 1
            for v in store.neighbours[store.offsets[u]:store.offsets[u + 1]]:
                v = int(v)
                if v not in seen and v not in dropped:
                    seen.add(v)
                    q.append(v)
        best = max(best, size)
    return best, len(alive) - best


def main() -> None:
    if sha256(ADOPTED.read_bytes()).hexdigest() != ADOPTED_SHA:
        raise SystemExit("artifact mismatch")
    store = GraphStore.load(ADOPTED)
    n = len(store.mbids)

    detail = json.loads(SIGNALS.read_text(encoding="utf-8"))["tail_detail"]
    clips = json.loads(CLIPS.read_text(encoding="utf-8"))["per_artist"]

    rg = json.loads(
        (HERE.parent / "2026-07-31-release-tag-coverage" / "rel_rg_raw.json")
        .read_text(encoding="utf-8"))
    index = json.loads(
        (HERE.parent / "2026-07-31-release-tag-coverage" / "rel_artist_index_raw.json")
        .read_text(encoding="utf-8"))
    discogs = json.loads(
        (HERE.parent / "2026-07-31-release-tag-coverage" / "rel_discogs_raw.json")
        .read_text(encoding="utf-8"))

    def has_discogs_releases(mbid: str) -> bool:
        did = (index.get(mbid) or {}).get("discogs")
        return bool(did and discogs.get(did))

    tail = [m for m in store.mbids if not rg.get(m) and not has_discogs_releases(m)]
    if len(tail) != 7686:
        raise SystemExit(f"tail {len(tail)} != committed 7686")

    def kept(mbid: str) -> bool:
        """Keep iff a DSP link AND a clip resolves. Absent from the artist dump
        (35 artists) means no link was observed, so the artist is dropped."""
        if not (detail.get(mbid) or {}).get("dsp"):
            return False
        rec = clips.get(mbid)
        return bool(rec and rec["name_path"]["resolves"])

    drop = sorted(m for m in tail if not kept(m))
    keep = sorted(m for m in tail if kept(m))
    print(f"tail {len(tail)}  ->  drop {len(drop)}  keep {len(keep)}", flush=True)

    idx = {m: i for i, m in enumerate(store.mbids)}
    drop_ids = {idx[m] for m in drop}

    # What the removal costs in connectivity. APPROXIMATE, and the reason is
    # structural: a real build recomputes masses, scores and the cap from the
    # archive with these artists absent, so selection itself shifts. This
    # simulates removal from the BUILT graph, which is the closest cheap
    # estimate and is a lower bound on churn, never the build's actual answer.
    before_best, before_out = largest_component_size(store, set())
    after_best, after_out = largest_component_size(store, drop_ids)
    survivors = n - len(drop_ids)
    stranded = after_out
    print(f"largest component: {before_best} of {n} before; "
          f"{after_best} of {survivors} surviving after", flush=True)
    print(f"additionally stranded by the drop: {stranded}", flush=True)

    payload = {
        "status": "ADOPTED owner decision, 2026-08-01. Not a diagnostic.",
        "rule": ("drop iff no MB release group AND no Discogs release AND NOT "
                 "(commercial-DSP link AND a clip resolves via the app's "
                 "Deezer->iTunes path)"),
        "snapshot_warning": (
            "The clip half is a 2026-08-01 SNAPSHOT, frozen because spec section 9 "
            "requires byte-identical builds and the builder is offline by a hard "
            "rule. A rebuild later applies this date's answer. Re-resolving is a "
            "deliberate act, never a silent build-time refresh."),
        "inputs": {
            "artifact": ADOPTED.name,
            "artifact_sha256": ADOPTED_SHA,
            "signals": "tail_signals.json",
            "clips": "tail_clips.json",
        },
        "counts": {
            "graph_artists": n,
            "no_release_tail": len(tail),
            "drop": len(drop),
            "keep": len(keep),
        },
        "connectivity_estimate_on_the_BUILT_graph": {
            "note": ("APPROXIMATE -- a real build recomputes masses, scores and "
                     "the cap with these artists absent, so selection shifts. "
                     "Lower bound on churn, not the build's answer."),
            "largest_component_before": before_best,
            "outside_before": before_out,
            "largest_component_after": after_best,
            "additionally_stranded": stranded,
        },
        "drop_mbids": drop,
        "keep_mbids": keep,
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    digest = sha256(json.dumps(drop, sort_keys=True).encode()).hexdigest()
    print(f"drop-list sha256 (sorted mbids): {digest}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
