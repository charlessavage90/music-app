"""What else do we know about the no-release tail? -- the owner's suggested counts.

DIAGNOSTIC ONLY. Not pre-registered, no bar, licenses nothing, adopts nothing.
Same standing as `tail_sample.py` and `tail_exposure.py` beside it.

THE QUESTION IT SIZES
  The owner is weighing a "has a release" filter on the 7,686 graph artists with
  no MusicBrainz release group and no Discogs release. He accepts it would carry
  false positives where MusicBrainz is simply incomplete, and asked how large
  that loss is before deciding. His two "journey-worthy" picks from
  TAIL-SAMPLE.md were both artists with REAL releases that MusicBrainz does not
  document, so the loss is a SOURCE COVERAGE quantity, not a modelling one.

  Every count below is a cheap local proxy for "there is a catalogue here that
  MusicBrainz missed". None is ground truth.

WHY EACH POPULATION IS REPORTED TWICE
  A bare "38% have a Spotify link" is uninterpretable. Every figure is reported
  for the no-release population AND for the rest of the graph, so the reader can
  see whether a signal is characteristic of the tail or just characteristic of
  MusicBrainz. That comparison is the whole point: the tail is expected to be
  thinner on EVERY field, because an artist whose releases nobody entered is an
  artist nobody curated. A signal only helps if the tail's rate is high in
  absolute terms, not merely lower than the baseline.

THE HAZARD IN THE STRONGEST-LOOKING SIGNAL
  A commercial-DSP link (Spotify / Apple / Deezer / Tidal) is the best evidence
  here that a real catalogue exists, because those platforms require a
  distributor. It is NOT evidence the artist is journey-worthy: the owner
  rejected 5 of the 7 clip-resolving artists in his sample. Necessary, not
  sufficient -- the same shape as the clip cross-reference in `tail_exposure.py`.

SOURCE
  `builder/scratch/mb-json-dumps/artist/mbdump/artist`, the 17.2 GiB MB artist
  JSON dump (2026-07-28 snapshot, same vintage as the REL- record). Single
  streaming pass, ~4 min. No network.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (str(_TAS), str(ROOT / "api" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tas_common import ADOPTED, ADOPTED_SHA  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402

DUMP = ROOT / "builder/scratch/mb-json-dumps/artist/mbdump/artist"
OUT = HERE / "tail_signals.json"
COMMITTED_POPULATION = 7686

# A link on one of these implies a DISTRIBUTOR put the catalogue there, so it is
# the strongest local evidence that releases exist which MusicBrainz has not
# recorded. Kept separate from the self-publish hosts below, which prove only
# that the artist posted something themselves.
DSP = {"open.spotify.com": "spotify", "spotify.com": "spotify",
       "music.apple.com": "apple", "itunes.apple.com": "apple",
       "deezer.com": "deezer", "tidal.com": "tidal",
       "listen.tidal.com": "tidal"}
SELF_PUBLISH = {"bandcamp.com": "bandcamp", "soundcloud.com": "soundcloud",
                "music.youtube.com": "youtube_music", "youtube.com": "youtube"}
DISCOGS = {"discogs.com": "discogs"}


def host_of(url: str) -> str:
    if "://" not in url:
        return ""
    h = url.split("/")[2].lower()
    return h[4:] if h.startswith("www.") else h


def main() -> None:
    if sha256(ADOPTED.read_bytes()).hexdigest() != ADOPTED_SHA:
        raise SystemExit("artifact mismatch")
    if not DUMP.exists():
        raise SystemExit(f"artist dump not found at {DUMP}")
    store = GraphStore.load(ADOPTED)

    rg = json.loads((_REL / "rel_rg_raw.json").read_text(encoding="utf-8"))
    index = json.loads((_REL / "rel_artist_index_raw.json").read_text(encoding="utf-8"))
    discogs = json.loads((_REL / "rel_discogs_raw.json").read_text(encoding="utf-8"))

    def has_discogs_releases(mbid: str) -> bool:
        did = (index.get(mbid) or {}).get("discogs")
        return bool(did and discogs.get(did))

    graph = set(store.mbids)
    nore = {m for m in store.mbids
            if not rg.get(m) and not has_discogs_releases(m)}
    if len(nore) != COMMITTED_POPULATION:
        raise SystemExit(f"population {len(nore)} != committed {COMMITTED_POPULATION}")
    print(f"graph {len(graph)}, no-release {len(nore)}", flush=True)

    # per-artist observed signals, filled from the dump
    seen: dict[str, dict] = {}
    scanned = 0
    with DUMP.open(encoding="utf-8") as f:
        for line in f:
            scanned += 1
            if scanned % 250_000 == 0:
                print(f"  ...{scanned:,} artists scanned, {len(seen):,} matched",
                      flush=True)
            # cheap reject before the parse: the mbid must appear literally
            d = json.loads(line)
            mbid = d.get("id")
            if mbid not in graph:
                continue
            dsps: set[str] = set()
            selfpub: set[str] = set()
            has_discogs_link = False
            ids: dict[str, str] = {}
            for r in d.get("relations") or []:
                url = (r.get("url") or {}).get("resource")
                if not url:
                    continue
                h = host_of(url)
                if h in DSP:
                    p = DSP[h]
                    dsps.add(p)
                    tail = url.rstrip("/").split("/")[-1]
                    if p in ("deezer", "apple") and tail:
                        ids.setdefault(p, tail)
                elif h in SELF_PUBLISH:
                    selfpub.add(SELF_PUBLISH[h])
                elif h in DISCOGS:
                    has_discogs_link = True
            seen[mbid] = {
                "dsp": sorted(dsps),
                "self_publish": sorted(selfpub),
                "discogs_link": has_discogs_link,
                "ids": ids,
                "mb_genres": len(d.get("genres") or []),
                "mb_tags": len(d.get("tags") or []),
                "type": d.get("type"),
            }
            if len(seen) == len(graph):
                break

    print(f"scanned {scanned:,} dump artists; matched {len(seen):,} of {len(graph):,}",
          flush=True)

    def tally(ids: set[str], label: str) -> dict:
        n = len(ids)
        c: Counter = Counter()
        per_platform: Counter = Counter()
        types: Counter = Counter()
        for m in ids:
            s = seen.get(m)
            if s is None:
                c["absent_from_dump"] += 1
                continue
            if s["dsp"]:
                c["any_dsp"] += 1
            if s["self_publish"]:
                c["any_self_publish"] += 1
            if s["dsp"] or s["self_publish"]:
                c["any_listenable_link"] += 1
            if s["discogs_link"]:
                c["discogs_link"] += 1
            if s["mb_genres"]:
                c["has_mb_genre"] += 1
            if s["mb_tags"]:
                c["has_mb_tag"] += 1
            if s["ids"].get("deezer"):
                c["deezer_id"] += 1
            if s["ids"].get("apple"):
                c["apple_id"] += 1
            if not (s["dsp"] or s["self_publish"] or s["discogs_link"]
                    or s["mb_genres"] or s["mb_tags"]):
                c["no_signal_at_all"] += 1
            for p in s["dsp"]:
                per_platform[p] += 1
            for p in s["self_publish"]:
                per_platform[p] += 1
            types[s["type"] or "(none)"] += 1
        out = {"population": n,
               "counts": dict(c),
               "shares": {k: round(v / n, 4) for k, v in c.items()},
               "per_platform": dict(per_platform.most_common()),
               "artist_type": dict(types.most_common(8))}
        print(f"\n[{label}] n={n}")
        for k in ("any_dsp", "any_self_publish", "any_listenable_link",
                  "discogs_link", "has_mb_genre", "has_mb_tag",
                  "deezer_id", "apple_id", "no_signal_at_all", "absent_from_dump"):
            if k in c:
                print(f"  {k:<22} {c[k]:>6}  ({c[k]/n:.2%})")
        print(f"  per platform: {dict(per_platform.most_common())}")
        print(f"  artist type:  {dict(types.most_common(6))}")
        return out

    rest = graph - nore
    result = {
        "scope": ("DIAGNOSTIC ONLY -- not pre-registered, no bar, licenses nothing. "
                  "Every count is a local PROXY for 'a catalogue exists that MB "
                  "missed', never ground truth."),
        "dump": {"path": str(DUMP), "snapshot": "2026-07-28",
                 "artists_scanned": scanned},
        "substrate": {"file": ADOPTED.name, "sha256": ADOPTED_SHA},
        "no_release_tail": tally(nore, "no-release tail"),
        "rest_of_graph": tally(rest, "rest of the graph (baseline)"),
        "reading_note": (
            "The tail is expected to be thinner on EVERY field -- an artist whose "
            "releases nobody entered is an artist nobody curated. A signal is only "
            "useful if the tail's ABSOLUTE rate is high, not merely lower than the "
            "baseline. And a DSP link is necessary-not-sufficient evidence of "
            "journey-worthiness: the owner rejected 5 of the 7 clip-resolving "
            "artists in his 20-artist sample."),
    }
    # --- candidate rules, scored against the owner's own 20 verdicts ---------
    # NOT a bar and NOT a selection procedure. n = 20 with TWO positives, so
    # this sample can separate "the bare filter loses his keepers" from "these
    # refinements do not" -- and nothing finer. It CANNOT rank the refinements
    # against each other; their differing cut counts here are noise. Choosing
    # between them needs a pre-registration designed cold.
    sample_path = HERE / "tail_sample.json"
    verdict_path = HERE / "TAIL-SAMPLE.md"
    rules_out: dict = {}
    if sample_path.exists() and verdict_path.exists():
        import re
        sample = json.loads(sample_path.read_text(encoding="utf-8"))["sample"]
        txt = verdict_path.read_text(encoding="utf-8")
        verdicts = {int(m.group(1)): m.group(2) for m in
                    re.finditer(r"^#(\d+):.*?Journey:\s*([YN])", txt, re.M | re.S)}

        def clip_ok(row) -> bool:
            c = row.get("clip")
            return bool(c.get("resolves") if isinstance(c, dict) else c)

        rules = {
            "bare_no_release": lambda s, r: True,
            "no_release_and_no_dsp_link": lambda s, r: not s.get("dsp"),
            "no_release_and_no_listenable_link":
                lambda s, r: not (s.get("dsp") or s.get("self_publish")),
            "no_release_and_not(dsp_link_and_clip)":
                lambda s, r: not (s.get("dsp") and clip_ok(r)),
        }
        for name, fn in rules.items():
            cut = [i for i, r in enumerate(sample, 1)
                   if fn(seen.get(r["mbid"], {}), r)]
            rules_out[name] = {
                "cuts_of_20": len(cut),
                "false_positives": [i for i in cut if verdicts.get(i) == "Y"],
                "population_cut": sum(
                    1 for m in nore if fn(seen.get(m, {}), {"clip": None}))
                if "clip" not in name else None,
            }
        print("\ncandidate rules vs the owner's 20 verdicts "
              "(n=20, 2 positives -- cannot rank the refinements):")
        for k, v in rules_out.items():
            print(f"  {k:<40} cuts {v['cuts_of_20']:>2}/20  "
                  f"false positives: {v['false_positives'] or 'NONE'}  "
                  f"population cut: {v['population_cut']}")

    result["candidate_rules"] = rules_out
    result["candidate_rules_caveat"] = (
        "n=20 with 2 positives. Separates 'the bare filter loses both keepers' "
        "from 'the refinements do not' and NOTHING FINER. The refinements' "
        "differing cut counts are noise at this n. Not a bar; choosing among "
        "them needs a pre-registration designed cold. Note #7 (Third Eye John): "
        "a DSP LINK exists but the owner found the pages carry no playable "
        "content and the clip did not resolve -- which is why the link and the "
        "clip are complementary rather than redundant.")

    # Per-artist detail for the tail only (7,686 rows). Retained deliberately:
    # it is what any follow-up needs -- the ID-based clip check reads the ids,
    # and testing a candidate rule against the owner's 20 verdicts needs the
    # per-artist signals rather than the aggregate.
    idx_of = {m: i for i, m in enumerate(store.mbids)}
    result["tail_detail"] = {
        m: {**seen[m], "name": store.names[idx_of[m]]}
        for m in sorted(nore) if m in seen
    }
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
