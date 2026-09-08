"""LUX-E6 -- tag vocabulary sanity: are the labels fit to show as written?

Governing document: docs/superpowers/specs/2026-09-03-launch-ux-scope.md,
section 5, `LUX-E6`. Plain sentence, fixed there before this ran: *are these
labels fit to show the public as written, or do they need an allowlist first?*
Threshold: DESCRIPTIVE. Adopts nothing, fixes no criterion, changes no
vocabulary. It is the ENTRY CONDITION for the deferred genre-tag work (spec
section 4.6), never a go decision -- that is the owner's.

THE FRAME READ IS F1, and nothing here redefines it. F1 is the frame the
release-tag coverage record (`findings/2026-07-31-release-tag-coverage.md`,
`REL-1`) measured as clearing its bar: F0 (ListenBrainz genre-whitelisted tags
UNION Wikidata P136) plus MusicBrainz release-group GENRES over attributable
release groups only. `F0` and the attributability filter come from the
committed probe outputs; `norm_genre` is imported through the frozen
`ct_common`, never reimplemented (two readers would be two chances to
disagree).

THE POPULATION IS THE SERVED ONE. The `REL-` census ran over the 74,193-node
artifact adopted at the time; the artifact that would carry a genre key today
is `graph-lux4.bin` (sha256 asserted against its manifest sidecar). Any served
artist absent from the frozen raw collections is counted and reported, never
silently treated as unlabelled.

THREE READS, all descriptive:
  (a) the vocabulary -- how many distinct strings would ever render, and the
      shape of their frequency;
  (b) the odd ones -- strings a curator would stop on, found by mechanical
      heuristics AND by source: a label only Wikidata P136 ever contributes
      comes from the one uncurated source in the frame;
  (c) the cards -- a seeded, popularity-stratified sample of real artists with
      exactly the label set a chip row would show.

Run from `builder/` (reads three local raw files; no network):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-08-lux-e6-tag-vocabulary/lux_e6.py
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ANALYSIS = HERE.parent
SCRATCH = ANALYSIS.parent / "scratch"

# Same device as tas_common: the api package is pure Python over numpy, and
# reading the artifact through its reader is what makes "served population"
# mean what the API means by it.
_API_SRC = ANALYSIS.parent.parent / "api" / "src"
_COH = ANALYSIS / "2026-07-30-coherence-tag-probe"
for p in (_API_SRC, _COH):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from artistpath_api.graph_store import GraphStore  # noqa: E402
from ct_common import norm_genre  # noqa: E402  -- frozen; never reimplemented

ARTIFACT = SCRATCH / "graph-lux4.bin"
MANIFEST = SCRATCH / "graph-lux4.bin.json"
TAS_TAGS = ANALYSIS / "2026-07-30-tag-discrimination" / "tas_tags_raw.json"
TAS_WD = ANALYSIS / "2026-07-30-tag-discrimination" / "tas_wikidata_raw.json"
REL_RG = ANALYSIS / "2026-07-31-release-tag-coverage" / "rel_rg_raw.json"

OUT = HERE / "lux_e6.json"
OUT_SAMPLE = HERE / "lux_e6_sample.md"

SEED = 20260908
PER_STRATUM = 10
# Popularity quartiles of the served population, in pop_raw. Raw currency,
# used only to spread the sample; no claim about fame is made from it.
STRATA = ("q1 (least popular)", "q2", "q3", "q4 (most popular)")

# Heuristics a curator would stop on. Mechanical and deliberately crude: the
# point is to surface strings for the eye, not to adjudicate them.
LONG = 28
ODD_CHARS = re.compile(r"[^a-z0-9 &'/+.]")
HAS_DIGIT = re.compile(r"\d")


def load_served() -> GraphStore:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["sha256"]
    if digest != expected:
        raise SystemExit(f"{ARTIFACT.name}: sha256 {digest} != manifest {expected}")
    print(f"artifact {ARTIFACT.name} sha256 {digest[:12]}… matches its manifest")
    return GraphStore.load(ARTIFACT)


def build_f1(store: GraphStore) -> tuple[dict[str, dict[str, set[str]]], dict]:
    """Per served artist: label -> set of sources that contribute it.

    Sources: 'lb' (ListenBrainz genre-whitelisted, a transport for MB genres),
    'wd' (Wikidata P136 -- the one uncurated source), 'rg' (MB release-group
    genres over attributable release groups only). The union of the keys IS
    the F1 label set.
    """
    lb = json.loads(TAS_TAGS.read_text(encoding="utf-8"))
    wd = json.loads(TAS_WD.read_text(encoding="utf-8"))
    rg = json.loads(REL_RG.read_text(encoding="utf-8"))

    per_artist: dict[str, dict[str, set[str]]] = {}
    missing = Counter()
    # The three collections were gathered over the 74,193-node artifact
    # adopted in July. A served artist absent from ALL of them entered the
    # population later (the extended ALG-B crawl) and can carry no label here
    # by construction -- that is a gap in the frozen collections, not a
    # measured absence of tags, and it gets its own denominator.
    reached = 0
    for mbid in store.mbids:
        if mbid in lb or mbid in wd or mbid in rg:
            reached += 1
        labels: dict[str, set[str]] = defaultdict(set)
        rec = lb.get(mbid)
        if mbid not in lb:
            missing["lb"] += 1
        for g in (rec or {}).get("genres", []):
            n = norm_genre(g)
            if n:
                labels[n].add("lb")
        if mbid not in wd:
            missing["wd"] += 1
        for g in (wd.get(mbid) or {}).get("genres", []):
            n = norm_genre(g)
            if n:
                labels[n].add("wd")
        # rel_rg_raw holds only artists with >= 1 release group in the dump;
        # absence there is a measured "no attributable release", not a gap in
        # collection, so it is not counted as missing.
        for release in rg.get(mbid, ()):
            if not release["a"]:
                continue
            for g in release["g"]:
                n = norm_genre(g)
                if n:
                    labels[n].add("rg")
        per_artist[mbid] = dict(labels)
    labelled_reached = sum(
        1 for m, labels in per_artist.items() if labels and (m in lb or m in wd or m in rg)
    )
    return per_artist, {
        "served": len(store.mbids),
        "absent_from_raw": dict(missing),
        "reached by any collection": reached,
        "labelled, among reached": labelled_reached,
        "share labelled, among reached": round(labelled_reached / reached, 4),
    }


def census(per_artist: dict[str, dict[str, set[str]]]) -> dict:
    label_artists: Counter = Counter()
    label_sources: dict[str, set[str]] = defaultdict(set)
    per_artist_counts: list[int] = []
    for labels in per_artist.values():
        per_artist_counts.append(len(labels))
        for label, sources in labels.items():
            label_artists[label] += 1
            label_sources[label] |= sources

    counts = np.array(per_artist_counts)
    labelled = counts[counts > 0]
    freq_bins = {
        "on >= 100 artists": sum(1 for c in label_artists.values() if c >= 100),
        "on 10-99 artists": sum(1 for c in label_artists.values() if 10 <= c < 100),
        "on 2-9 artists": sum(1 for c in label_artists.values() if 2 <= c < 10),
        "on exactly 1 artist": sum(1 for c in label_artists.values() if c == 1),
    }
    # Share of all (artist, label) chip impressions carried by labels at
    # each frequency: a rare odd label matters less if it is rarely SHOWN.
    total_impressions = sum(label_artists.values())
    impressions_by_bin = {
        k: sum(c for c in label_artists.values() if cond(c)) / total_impressions
        for k, cond in {
            "on >= 100 artists": lambda c: c >= 100,
            "on 10-99 artists": lambda c: 10 <= c < 100,
            "on 2-9 artists": lambda c: 2 <= c < 10,
            "on exactly 1 artist": lambda c: c == 1,
        }.items()
    }

    wd_only = {l for l, s in label_sources.items() if s == {"wd"}}
    wd_only_impressions = sum(label_artists[l] for l in wd_only)
    # The cheapest curation: keep a Wikidata label only where the MusicBrainz
    # genre vocabulary (the lb and rg sources) also uses that string somewhere
    # in the corpus. What does it cost in coverage? Only artists whose EVERY
    # label is wd-only lose their chip row.
    lose_all = sum(
        1 for labels in per_artist.values() if labels and all(l in wd_only for l in labels)
    )
    src_mark = lambda l: "".join(sorted(x[0] for x in label_sources[l]))  # noqa: E731
    odd = {
        "long (> %d chars)" % LONG: sorted(f"{l} ·{src_mark(l)}" for l in label_artists if len(l) > LONG),
        "has a digit": sorted(f"{l} ·{src_mark(l)}" for l in label_artists if HAS_DIGIT.search(l)),
        "odd characters": sorted(f"{l} ·{src_mark(l)}" for l in label_artists if ODD_CHARS.search(l)),
        "single character": sorted(f"{l} ·{src_mark(l)}" for l in label_artists if len(l) == 1),
    }

    return {
        "artists": {
            "total": int(counts.size),
            "with >= 1 label": int(labelled.size),
            "share with >= 1 label": round(float(labelled.size / counts.size), 4),
            "labels per labelled artist": {
                "median": float(np.median(labelled)),
                "p90": float(np.percentile(labelled, 90)),
                "max": int(labelled.max()),
                "share with > 6": round(float((labelled > 6).mean()), 4),
            },
        },
        "vocabulary": {
            "distinct labels": len(label_artists),
            "by frequency": freq_bins,
            "chip impressions by label frequency": {
                k: round(v, 4) for k, v in impressions_by_bin.items()
            },
            "top 60": label_artists.most_common(60),
        },
        "sources": {
            "labels contributed ONLY by Wikidata P136": len(wd_only),
            "their share of chip impressions": round(wd_only_impressions / total_impressions, 4),
            "artists who lose their last label if wd-only labels are dropped": lose_all,
            "labels in the MusicBrainz vocabulary (lb or rg contributes)": len(label_artists) - len(wd_only),
            "wd-only, most frequent 40": sorted(
                ((label_artists[l], l) for l in wd_only), reverse=True
            )[:40],
            "wd-only, a seeded 40 of the rest": sorted(
                random.Random(SEED).sample(sorted(wd_only), min(40, len(wd_only)))
            ),
        },
        "odd strings": {k: {"count": len(v), "examples": v[:60]} for k, v in odd.items()},
        "singletons, a seeded 80": sorted(
            random.Random(SEED + 1).sample(
                sorted(l for l, c in label_artists.items() if c == 1),
                min(80, freq_bins["on exactly 1 artist"]),
            )
        ),
    }, label_artists


def sample_cards(
    store: GraphStore,
    per_artist: dict[str, dict[str, set[str]]],
    label_artists: Counter,
) -> str:
    """Seeded, popularity-stratified: what a chip row would actually show."""
    pop = np.asarray(store.pop_raw)
    q = np.quantile(pop, [0.25, 0.5, 0.75])
    stratum_of = np.searchsorted(q, pop, side="right")  # 0..3
    rng = random.Random(SEED)
    lines = [
        "# LUX-E6 sample cards\n",
        f"Seed {SEED}; {PER_STRATUM} artists per popularity quartile of the served "
        "population (`pop_raw`, raw currency, used only to spread the sample). "
        "Marks after a label: `·lb` ListenBrainz genre, `·wd` Wikidata P136, "
        "`·rg` release-group genre; `(n)` = artists carrying that label in the frame.\n",
    ]
    for s, name in enumerate(STRATA):
        idx = [i for i in range(len(store.mbids)) if stratum_of[i] == s]
        pick = rng.sample(idx, PER_STRATUM)
        lines.append(f"\n## {name}\n")
        for i in sorted(pick, key=lambda i: pop[i]):
            mbid = store.mbids[i]
            labels = per_artist[mbid]
            if labels:
                chips = ", ".join(
                    f"**{l}**·{''.join(sorted(x[0] for x in src))} ({label_artists[l]})"
                    for l, src in sorted(labels.items(), key=lambda kv: -label_artists[kv[0]])
                )
            else:
                chips = "*(no label — the empty state)*"
            lines.append(f"- {store.names[i]} · pop_raw {pop[i]:.2f} — {chips}")
    return "\n".join(lines) + "\n"


def main() -> None:
    store = load_served()
    per_artist, coverage = build_f1(store)
    print(f"served {coverage['served']:,}; absent from raw collections: {coverage['absent_from_raw']}; "
          f"reached by any collection {coverage['reached by any collection']:,}, of which labelled "
          f"{coverage['labelled, among reached']:,} ({coverage['share labelled, among reached']:.1%})")
    summary, label_artists = census(per_artist)
    summary["population"] = coverage
    summary["frame"] = "F1 = F0 (LB genre-whitelisted ∪ Wikidata P136) ∪ MB release-group genres, attributable only"
    summary["seed"] = SEED

    a = summary["artists"]
    v = summary["vocabulary"]
    s = summary["sources"]
    print(f"\n(a) artists with >= 1 label: {a['with >= 1 label']:,} / {a['total']:,} "
          f"({a['share with >= 1 label']:.1%}); labels per labelled artist "
          f"median {a['labels per labelled artist']['median']:.0f}, "
          f"p90 {a['labels per labelled artist']['p90']:.0f}, max {a['labels per labelled artist']['max']}, "
          f"share with > 6: {a['labels per labelled artist']['share with > 6']:.1%}")
    print(f"    distinct labels: {v['distinct labels']:,}")
    for k, n in v["by frequency"].items():
        print(f"      {k:>22}: {n:>6,}  ({v['chip impressions by label frequency'][k]:.1%} of chip impressions)")
    print(f"\n(b) labels only Wikidata contributes: {s['labels contributed ONLY by Wikidata P136']:,} "
          f"({s['their share of chip impressions']:.1%} of chip impressions)")
    for k, d in summary["odd strings"].items():
        print(f"    {k:>18}: {d['count']:>5}  e.g. {d['examples'][:8]}")
    print("\n    top 30:", ", ".join(f"{l} ({c})" for l, c in v["top 60"][:30]))

    OUT.write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    OUT_SAMPLE.write_text(sample_cards(store, per_artist, label_artists), encoding="utf-8")
    print(f"\n-> {OUT.name}, {OUT_SAMPLE.name}")


if __name__ == "__main__":
    main()
