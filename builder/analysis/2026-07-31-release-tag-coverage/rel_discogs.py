"""The Discogs pass: frames F4 and F5, and the second half of REL-2.

WHAT MAKES DISCOGS DIFFERENT, AND WHY IT CHANGES THE SHAPE OF THE QUESTION
  Discogs `<genres>` measured 100% non-empty on both dump samples. That is not
  a coverage figure -- it is a SCHEMA CONSTRAINT: a release cannot be
  submitted without a genre. So unlike MusicBrainz, where the open question is
  "did anyone bother to tag this", the Discogs arm collapses entirely to the
  two ceiling questions REL-2 asks: can we find the artist, and do they have
  releases listed.

  REL-2 IS THEREFORE NOT A CAVEAT ON THE DISCOGS FIGURES -- IT IS THE WHOLE
  DISCOGS ARM. Spec section 2: any F4/F5/F6 figure quoted without REL-2 beside
  it is misreported.

TWO VOCABULARIES, MEASURED SEPARATELY AND NEVER MERGED
  `genre` is a closed 15-value list (Rock, Electronic, Pop, Jazz...) and
  `style` is a ~600-value one. They are F4 and F5 and stay separate columns:
  merging Discogs genre into any agreement statistic would inflate it badly,
  since nearly every guitar band agrees on "Rock". Neither enters the frozen
  TAS- vocabulary; that would be a TAS- section 8 amendment and this document
  does not make one.

MAPPING IS BY ID, NEVER BY NAME
  The Discogs artist id comes from MusicBrainz's own url-rel (rel_artist_dump).
  Name matching is explicitly REJECTED, not deferred (spec section 7): it is
  the population-mismatch trap that killed every external popularity source.

Run from `builder/` (measured 22.2 min), AFTER rel_artist_dump.py:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-31-release-tag-coverage/rel_discogs.py
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from xml.etree import ElementTree as ET

from rel_common import (
    BAND_ORDER,
    DISCOGS_RELEASES,
    HERE,
    band_of,
    discogs_is_attributable,
    f0_label_sets,
    fame_frame,
    graph_mbids,
    norm_genre,
)
from rel_artist_dump import OUT_INDEX as ARTIST_INDEX

OUT_RAW = HERE / "rel_discogs_raw.json"
OUT = HERE / "rel_discogs.json"


def _labels(release: ET.Element, container: str) -> list[str]:
    node = release.find(container)
    if node is None:
        return []
    out = {norm_genre(el.text) for el in node if el.text}
    return sorted(label for label in out if label)


def collect(wanted: set[str]) -> dict[str, dict]:
    """One streaming pass over the 61.6 GB XML, accumulating UNIONS in place.

    THE FIRST VERSION STORED ONE DICT PER (artist, release) AND WAS KILLED BY
    THE OS at ~13M of ~20M releases, having accumulated ~5M records. Nothing
    downstream ever needed that granularity: REL-C2's shuffle operates on
    RELEASE GROUPS, not on Discogs releases, so per-release detail here was
    pure cost. Folding each release into the artist's running union bounds
    memory at 74k artists x a few small sets.

    Counts are kept because REL-2's ceiling needs "has >= 1 attributable
    release", and n_all - n_attr is what the filter costs on the Discogs side.
    """
    per_artist: dict[str, dict] = defaultdict(
        lambda: {"g": set(), "s": set(), "n_attr": 0, "n_all": 0}
    )
    began = time.time()
    seen = kept = 0
    # `elem.clear()` alone is NOT enough: the emptied <release> shells stay
    # attached to the root as siblings, so the tree still grows without bound
    # over ~20M releases. Holding the root and clearing it too is what actually
    # bounds memory.
    context = ET.iterparse(str(DISCOGS_RELEASES), events=("start", "end"))
    _event, root = next(context)
    for event, elem in context:
        if event != "end" or elem.tag != "release":
            continue
        seen += 1
        artists = elem.find("artists")
        ids = (
            [a.findtext("id") for a in artists if a.findtext("id")]
            if artists is not None
            else []
        )
        # <extraartists> is deliberately never consulted: its roles are
        # Producer / Written-By / Mastered By / Lacquer Cut By.
        mine = [i for i in ids if i in wanted]
        if mine:
            attributable = discogs_is_attributable(ids)
            genres = _labels(elem, "genres") if attributable else ()
            styles = _labels(elem, "styles") if attributable else ()
            for artist_id in mine:
                bucket = per_artist[artist_id]
                bucket["n_all"] += 1
                if attributable:
                    bucket["n_attr"] += 1
                    bucket["g"].update(genres)
                    bucket["s"].update(styles)
                kept += 1
        elem.clear()
        root.clear()
        if seen % 1_000_000 == 0:
            mins = (time.time() - began) / 60
            print(f"  {seen:,} releases, {kept:,} kept, "
                  f"{len(per_artist):,} artists ({mins:.1f} min)", flush=True)
    print(f"  pass done: {seen:,} releases in "
          f"{(time.time() - began) / 60:.1f} min, {kept:,} kept", flush=True)
    return {
        k: {"g": sorted(v["g"]), "s": sorted(v["s"]),
            "n_attr": v["n_attr"], "n_all": v["n_all"]}
        for k, v in per_artist.items()
    }


def main() -> None:
    frame = fame_frame()
    mbids = graph_mbids()
    f0 = f0_label_sets()

    index = json.loads(ARTIST_INDEX.read_text(encoding="utf-8"))
    mbid_to_discogs = {
        m: rec["discogs"] for m, rec in index.items() if rec.get("discogs")
    }
    print(f"{len(mbid_to_discogs)}/{len(mbids)} artists carry a Discogs id")

    per_discogs = collect(set(mbid_to_discogs.values()))
    OUT_RAW.write_text(json.dumps(per_discogs), encoding="utf-8")

    def sets_for(field: str) -> dict[str, set[str]]:
        """Collector already applied the strict filter -- see collect()."""
        out: dict[str, set[str]] = {}
        for mbid in mbids:
            discogs_id = mbid_to_discogs.get(mbid)
            bucket = per_discogs.get(discogs_id) if discogs_id else None
            out[mbid] = set(bucket[field]) if bucket else set()
        return out

    f4 = sets_for("g")
    f5 = sets_for("s")

    # --- REL-2: the full ceiling, both halves and their product
    print(f"\n{'band':>12} {'unlab':>7} {'has id':>8} {'id+releases':>12} {'product':>8}")
    rel2: dict[str, dict] = {}
    for b in BAND_ORDER:
        band_mbids = [m for m in mbids if band_of(frame[m]) == b]
        unlab = [m for m in band_mbids if not f0[m]]
        if not unlab:
            continue
        has_id = [m for m in unlab if mbid_to_discogs.get(m)]
        has_rel = [
            m
            for m in has_id
            if (per_discogs.get(mbid_to_discogs[m]) or {}).get("n_attr", 0) > 0
        ]
        rel2[b] = {
            "unlabelled": len(unlab),
            "with_discogs_id": len(has_id),
            "with_id_share": round(len(has_id) / len(unlab), 4),
            "with_attributable_release": len(has_rel),
            "product_share": round(len(has_rel) / len(unlab), 4),
        }
        print(f"{b:>12} {len(unlab):>7} {len(has_id) / len(unlab):>7.1%} "
              f"{len(has_rel):>12} {len(has_rel) / len(unlab):>7.1%}")

    # --- F4 / F5 coverage, on the COH-2 denominator
    print(f"\n{'band':>12} {'n':>7} {'F0':>7} {'F4':>7} {'F5':>7}")
    cover: dict[str, dict] = {}
    for b in BAND_ORDER:
        band_mbids = [m for m in mbids if band_of(frame[m]) == b]
        n = len(band_mbids)
        if not n:
            continue
        row = {
            "n": n,
            "F0": sum(1 for m in band_mbids if f0[m]),
            "F4": sum(1 for m in band_mbids if f0[m] or f4[m]),
            "F5": sum(1 for m in band_mbids if f0[m] or f5[m]),
        }
        cover[b] = {
            k: v if k == "n" else {"count": v, "share": round(v / n, 4)}
            for k, v in row.items()
        }
        print(f"{b:>12} {n:>7} {row['F0'] / n:>6.1%} {row['F4'] / n:>6.1%} "
              f"{row['F5'] / n:>6.1%}")

    OUT.write_text(
        json.dumps(
            {
                "artists_with_discogs_id": len(mbid_to_discogs),
                "rel_2_ceiling": rel2,
                "coverage": cover,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"\n-> {OUT.name}, {OUT_RAW.name}")


if __name__ == "__main__":
    main()
