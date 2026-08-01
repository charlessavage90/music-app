"""`WGT-5`: the vocabulary on the table -- the owner's eyeball artifact.

Descriptive, no bars. Three deliverables per the pre-registration §5:
per-frame label tables with carrier counts and rarity weights; the Discogs
STYLE column's full frequency table (the ~600 labels the owner asked to see);
and per-source rarity distributions, which answer descriptively whether one
rarity rule over the union treats the sources sanely or one source dominates.

Run from `builder/` (~2 min, no capture needed -- vocabulary statistics are
substrate-independent, as `tas_weighting` reading A records):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-01-label-weighting/wgt_tables.py
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (_TAS, _REL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from tas_common import graph_mbids  # noqa: E402
from tas_frame_split import five_frames  # noqa: E402
from tas_weighting import idf_table  # noqa: E402

OUT_JSON = HERE / "wgt_tables.json"
OUT_MD = HERE / "STYLE-VOCABULARY.md"


def source_columns() -> dict[str, dict[str, set[str]]]:
    """Per-source label sets: F0 (artist page union), F1 (MB release groups),
    F4 (Discogs genre), F5 (Discogs style). Committed helpers only."""
    from rel_artist_dump import OUT_INDEX as ARTIST_INDEX
    from rel_discogs import OUT_RAW as DISCOGS_RAW
    from rel_rg_dump import OUT_RAW as RG_RAW, frame_sets
    from tas_tags import label_sets

    mbids = graph_mbids()
    f0 = label_sets()
    per_artist = json.loads(RG_RAW.read_text(encoding="utf-8"))
    f1 = frame_sets(per_artist, mbids, field="g", strict=True)
    index = json.loads(ARTIST_INDEX.read_text(encoding="utf-8"))
    per_discogs = json.loads(DISCOGS_RAW.read_text(encoding="utf-8"))
    mbid_to_discogs = {m: r["discogs"] for m, r in index.items() if r.get("discogs")}

    def dsets(field: str) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for m in mbids:
            bucket = per_discogs.get(mbid_to_discogs.get(m) or "")
            out[m] = set(bucket[field]) if bucket else set()
        return out

    return {"F0_artist_page": f0, "F1_mb_release_groups": f1,
            "F4_discogs_genre": dsets("g"), "F5_discogs_style": dsets("s")}


def df_of(labels: dict[str, set[str]]) -> Counter:
    df: Counter = Counter()
    for s in labels.values():
        for lab in s:
            df[lab] += 1
    return df


def main() -> None:
    frames = five_frames()
    sources = source_columns()
    n = len(graph_mbids())

    out: dict = {"note": "WGT-5, descriptive, no bars.", "graph_artists": n,
                 "frames": {}, "sources": {}}

    for fname, labels in frames.items():
        idf, df = idf_table(labels, n)
        weights = sorted(idf.values())
        out["frames"][fname] = {
            "distinct_labels": len(df),
            "carriers_median": statistics.median(df.values()) if df else None,
            "singletons": sum(1 for c in df.values() if c == 1),
            "rarity_weight_quartiles": [
                round(weights[len(weights) * q // 4], 3) for q in (1, 2, 3)
            ] if weights else None,
        }

    for sname, labels in sources.items():
        df = df_of(labels)
        idf, _ = idf_table(labels, n)
        vals = sorted(idf.values())
        out["sources"][sname] = {
            "distinct_labels": len(df),
            "artists_reached": sum(1 for s in labels.values() if s),
            "singletons": sum(1 for c in df.values() if c == 1),
            "rarity_weight_median": round(vals[len(vals) // 2], 3) if vals else None,
            "top10": [[lab, c] for lab, c in df.most_common(10)],
        }

    style_df = df_of(sources["F5_discogs_style"])
    genre_df = df_of(sources["F4_discogs_genre"])

    lines = [
        "# The Discogs style vocabulary, in full",
        "",
        f"**{len(style_df)}** distinct style labels reach "
        f"**{out['sources']['F5_discogs_style']['artists_reached']:,}** artists; the "
        f"closed genre list has **{len(genre_df)}** labels reaching "
        f"**{out['sources']['F4_discogs_genre']['artists_reached']:,}**. Every "
        "style-carrying artist also carries a genre (the REL- record), which is why "
        "styles can never add reach — only sharpness, or noise.",
        "",
        "Sorted by carrier count, descending. `weight` is the rarity weight "
        "`ln(N / carriers)` the weighted schemes would give one shared occurrence "
        "of the label.",
        "",
        "| Style | Carriers | Rarity weight |",
        "|---|---|---|",
    ]
    idf_style, _ = idf_table(sources["F5_discogs_style"], n)
    for lab, c in style_df.most_common():
        lines.append(f"| {lab} | {c} | {idf_style[lab]:.2f} |")
    lines += ["", "## The 15 Discogs genres, for contrast", "",
              "| Genre | Carriers |", "|---|---|"]
    for lab, c in genre_df.most_common():
        lines.append(f"| {lab} | {c} |")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {OUT_MD.name} ({len(style_df)} styles) and {OUT_JSON.name}",
          flush=True)


if __name__ == "__main__":
    main()
