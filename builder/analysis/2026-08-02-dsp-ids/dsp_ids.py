"""Extract MusicBrainz-recorded Deezer artist IDs for the graph population.

WHY THIS EXISTS
  `BYP-13` is a live user-facing defect: a card plays a clip by a DIFFERENT
  ARTIST OF THE SAME NAME, because the app resolves clips by searching the
  artist's name. Measured at 9.4% (denominator 160) and 6.1% (denominator 49).

  A MusicBrainz-recorded Deezer artist ID points at that exact artist, so a
  clip found through it cannot be the wrong same-named artist. This extracts
  those IDs so the builder can carry them in the APG1 metadata blob.

  The resolution path itself is not new: `tail_clips.py:137` `id_path()` already
  asks Deezer for a specific artist's top track with no name matching anywhere.
  It was built as the instrument check that MEASURED the defect. This promotes
  its input into the artifact.

DEEZER ONLY, DELIBERATELY
  MusicBrainz also records Apple/iTunes artist IDs. Over the artists the app
  actually delivers, Deezer alone covers 92.9% of card impressions and adding
  Apple takes it to 94.1% -- 1.2 points. The Deezer ID path is MEASURED; an
  Apple-ID-to-iTunes-lookup path is plausible but has never been run here.
  Shipping unproven data nothing consumes taxes every build and every boot, so
  the Apple column is measured (see the coverage table) and not shipped.

ONE MAP FOR ANY ARCHIVE -- AND THAT IS NOT THE DROP-LIST MISTAKE
  The no-release drop list is per-archive because it encodes a DECISION ABOUT A
  POPULATION: which artists this crawl should lose. A Deezer ID is a PROPERTY OF
  AN ARTIST -- an MBID maps to the same Deezer artist whatever similarity
  archive is being built. So one map is correct here where one list was wrong
  there.

  The asymmetry that matters if this is ever questioned: a MISSING id degrades
  to today's name search, which is exactly today's behaviour, whereas a wrong
  drop list silently removes the wrong artists. This fails safe; that failed
  silent.

  The map covers the UNION of the adopted graph and the ALG-B candidate graph,
  so a build from either archive is covered and the cap re-evaluation cannot
  trip a coverage condition mid-experiment. The ALG-B graph is the 2026-07-30
  full build, which predates the no-release drop and the nameless fix, so its
  population is a SUPERSET of anything a final ALG-B build produces. A superset
  is safe by construction: an MBID absent from a given build is a no-op. That is
  the same reasoning the candidate tail census used for its own population.

  An artist outside the union still gets no id and falls back to name search --
  a coverage gap, never a wrong answer.

A DATED SNAPSHOT, like the drop list
  The dump is a 2026-07-28 MusicBrainz export. The build must never re-resolve
  these over the network: `build_from_archive` is offline by a hard rule and
  spec section 9 requires byte-identical builds. Refreshing is a deliberate act.

Read-only, offline, no network. ~2 minutes over the 16 GB artist dump.
"""
from __future__ import annotations

import json
import sys

from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
for _p in (ROOT / "api" / "src", HERE.parent / "2026-07-30-coherence-tag-probe"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402
from ct_common import ADOPTED, ADOPTED_SHA  # noqa: E402

DUMP = ROOT / "builder/scratch/mb-json-dumps/artist/mbdump/artist"

# The ALG-B candidate graph, 2026-07-30 full build. Pinned by sha because
# several graphs sit in builder/scratch/ and they are NOT interchangeable --
# the sidecar manifest is the only way to know which one is on disk.
CANDIDATE = ROOT / "builder/scratch/graph-algb-full.bin"
CANDIDATE_SHA = "d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f"

# Host table verbatim from tail_signals.py, which is the reference
# implementation. The `www.` strip in host_of is LOAD-BEARING: without it every
# www.deezer.com link misses and Deezer coverage reads as exactly zero. That
# happened on the first run of this measurement and the implausible zero is what
# caught it.
DSP = {"open.spotify.com": "spotify", "spotify.com": "spotify",
       "music.apple.com": "apple", "itunes.apple.com": "apple",
       "deezer.com": "deezer", "tidal.com": "tidal",
       "listen.tidal.com": "tidal"}

BANDS = ["top 1%", "90-99%", "50-90%", "10-50%", "bottom 10%"]


def host_of(url: str) -> str:
    if "://" not in url:
        return ""
    h = url.split("/")[2].lower()
    return h[4:] if h.startswith("www.") else h


def band_of(pctl: float) -> str:
    if pctl >= 99.0:
        return "top 1%"
    if pctl >= 90.0:
        return "90-99%"
    if pctl >= 50.0:
        return "50-90%"
    if pctl >= 10.0:
        return "10-50%"
    return "bottom 10%"


def main() -> None:
    if sha256(ADOPTED.read_bytes()).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch -- refusing to extract")
    if sha256(CANDIDATE.read_bytes()).hexdigest() != CANDIDATE_SHA:
        raise SystemExit("candidate artifact mismatch -- refusing to extract")
    if not DUMP.exists():
        raise SystemExit(f"artist dump not found at {DUMP}")

    store = GraphStore.load(ADOPTED)
    candidate = GraphStore.load(CANDIDATE)
    adopted_set = set(store.mbids)
    candidate_set = set(candidate.mbids)
    graph = adopted_set | candidate_set
    print(f"adopted {len(adopted_set):,}  candidate {len(candidate_set):,}  "
          f"union {len(graph):,}  candidate-only {len(candidate_set - adopted_set):,}",
          flush=True)

    # Popularity PERCENTILE, computed here. pop_raw is a value, never a rank.
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    order = pop.argsort()
    ranks = np.empty(len(pop))
    ranks[order] = np.arange(len(pop)) / max(1, len(pop) - 1) * 100.0
    band_by_mbid = {m: band_of(float(ranks[i])) for i, m in enumerate(store.mbids)}

    deezer: dict[str, str] = {}
    discarded: list[dict] = []
    apple: dict[str, str] = {}
    seen_in_dump: set[str] = set()
    scanned = 0
    with DUMP.open(encoding="utf-8") as f:
        for line in f:
            scanned += 1
            if scanned % 500_000 == 0:
                print(f"  ...{scanned:,} scanned, {len(deezer):,} deezer ids",
                      flush=True)
            d = json.loads(line)
            mbid = d.get("id")
            if mbid not in graph:
                continue
            seen_in_dump.add(mbid)
            for r in d.get("relations") or []:
                url = (r.get("url") or {}).get("resource")
                if not url:
                    continue
                platform = DSP.get(host_of(url))
                if platform not in ("deezer", "apple"):
                    continue
                # Strip any query string: MusicBrainz records Apple links with
                # locale parameters (?l=en) often enough to matter.
                tail = url.split("?")[0].rstrip("/").split("/")[-1]
                if not tail:
                    continue
                if platform == "deezer":
                    # Deezer's artist endpoint takes a NUMERIC id. A handful of
                    # recorded links end in a name slug ("anggun") rather than
                    # an id; requesting those returns 404, which would fail safe
                    # into name search but spend a call to get there. Discarded
                    # at extraction so the shipped map is uniformly usable.
                    if not tail.isdigit():
                        discarded.append({"mbid": mbid, "url": url})
                        continue
                    deezer.setdefault(mbid, tail)
                else:
                    apple.setdefault(mbid, tail)

    print(f"scanned {scanned:,} rows; matched {len(seen_in_dump):,} graph artists",
          flush=True)

    total: Counter = Counter()
    d_band: Counter = Counter()
    a_band: Counter = Counter()
    e_band: Counter = Counter()
    for m in store.mbids:
        b = band_by_mbid[m]
        total[b] += 1
        if m in deezer:
            d_band[b] += 1
        if m in apple:
            a_band[b] += 1
        if m in deezer or m in apple:
            e_band[b] += 1

    hdr = (f"{'band':<12}{'artists':>9}{'deezer':>9}{'apple':>9}"
           f"{'either':>9}{'deezer %':>10}")
    print()
    print(hdr)
    print("-" * len(hdr))
    for b in BANDS:
        t = total[b]
        print(f"{b:<12}{t:>9,}{d_band[b]:>9,}{a_band[b]:>9,}{e_band[b]:>9,}"
              f"{(d_band[b] / t * 100 if t else 0):>9.1f}%")
    t = sum(total.values())
    print("-" * len(hdr))
    print(f"{'adopted':<12}{t:>9,}{sum(d_band.values()):>9,}{sum(a_band.values()):>9,}"
          f"{sum(e_band.values()):>9,}{sum(d_band.values()) / t * 100:>9.1f}%")

    # Candidate-only artists carry no popularity in the adopted graph, so they
    # cannot be banded against it. Reported as their own line rather than
    # silently folded into a band they are not in.
    cand_only = candidate_set - adopted_set
    cand_only_d = sum(1 for m in cand_only if m in deezer)
    print(f"{'ALG-B only':<12}{len(cand_only):>9,}{cand_only_d:>9,}"
          f"{sum(1 for m in cand_only if m in apple):>9,}"
          f"{sum(1 for m in cand_only if m in deezer or m in apple):>9,}"
          f"{cand_only_d / len(cand_only) * 100:>9.1f}%")
    print("-" * len(hdr))
    print(f"{'UNION':<12}{len(graph):>9,}{len(deezer):>9,}{len(apple):>9,}"
          f"{'':>9}{len(deezer) / len(graph) * 100:>9.1f}%")

    payload = {
        "status": "Frozen 2026-08-02 snapshot of MusicBrainz artist->Deezer "
                  "artist id. Never re-resolved at build time (spec section 9; "
                  "build_from_archive is offline by a hard rule).",
        "purpose": "Resolve clips by artist identity instead of by name, so a "
                   "card cannot play a different artist of the same name "
                   "(BYP-13).",
        "dump": "MusicBrainz JSON artist dump, 2026-07-28",
        "population": "union of the adopted graph and the ALG-B candidate graph (2026-07-30 full build, pre-drop, so a superset of any final ALG-B build)",
        "substrate_candidate": {"file": CANDIDATE.name, "sha256": CANDIDATE_SHA},
        "substrate": {"file": ADOPTED.name, "sha256": ADOPTED_SHA},
        "counts": {
            "union_artists": len(graph),
            "adopted_artists": len(adopted_set),
            "candidate_artists": len(candidate_set),
            "matched_in_dump": len(seen_in_dump),
            "deezer_ids": len(deezer),
            "apple_ids_measured_not_shipped": len(apple),
            "either": sum(e_band.values()),
            "deezer_links_discarded_not_numeric": len(discarded),
        },
        "coverage_by_popularity_percentile_band": {
            b: {"artists": total[b], "deezer": d_band[b],
                "apple": a_band[b], "either": e_band[b]}
            for b in BANDS
        },
        "discarded_non_numeric_deezer_links": discarded,
        "sha256_over_sorted_items": sha256(
            json.dumps(sorted(deezer.items()), sort_keys=True).encode()
        ).hexdigest(),
        "deezer_ids": dict(sorted(deezer.items())),
    }
    out = HERE / "dsp_ids.json"
    out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"\nwrote {out.name}  sha256(items)={payload['sha256_over_sorted_items']}")


if __name__ == "__main__":
    main()
