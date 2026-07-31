"""The MusicBrainz RELEASE-GROUP pass: frames F1, F2 and F3.

WHY THE RELEASE GROUP AND NOT THE RELEASE
  Release-level tags measured 13.5% non-empty against release-group's 42.4%
  (spec section 0). Tagging in MusicBrainz attaches to the album concept, not
  to a particular pressing -- so the release group is both the better-filled
  frame AND the conservative aggregation unit, since it collapses reissues and
  a fat back catalogue cannot inflate an artist's label set. The 345 GB
  release dump is out of scope (spec section 7) and has been deleted.

WHAT IS STORED, AND WHY IT IS PER-RELEASE RATHER THAN PRE-AGGREGATED
  One record per (artist, release group), each carrying its own label sets and
  its attributability flag. Every frame is then derived from one structure --
  and REL-C2's shuffle NEEDS the per-release granularity, because it permutes
  which artist owns which release while preserving each artist's release
  count. A pre-aggregated union could not be shuffled.

Run from `builder/` (~5 min), AFTER rel_artist_dump.py:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-31-release-tag-coverage/rel_rg_dump.py
"""

from __future__ import annotations

import json
import time
from collections import defaultdict

from rel_common import (
    BAND_ORDER,
    HERE,
    MB_RELEASE_GROUP,
    band_of,
    f0_label_sets,
    fame_frame,
    graph_mbids,
    labels_from,
    rg_artist_id,
    rg_is_attributable,
)

OUT_RAW = HERE / "rel_rg_raw.json"
OUT = HERE / "rel_rg.json"


def collect(wanted: set[str]) -> dict[str, list[dict]]:
    """One streaming pass over the 18 GB dump.

    Only release groups with EXACTLY ONE credited artist can be attributed at
    all, but multi-credit ones are still recorded (flagged) because F3, the
    permissive frame, counts them and REL-5 prices the difference.
    """
    per_artist: dict[str, list[dict]] = defaultdict(list)
    began = time.time()
    nbytes = seen = kept = 0
    with MB_RELEASE_GROUP.open("rb") as fh:
        for line in fh:
            nbytes += len(line)
            seen += 1
            record = json.loads(line)
            credits = record.get("artist-credit") or []
            genres = sorted(labels_from(record, "genres"))
            tags = sorted(labels_from(record, "tags"))
            attributable = rg_is_attributable(record)
            # Permissive frame counts every credited artist; strict counts the
            # sole-credit case only. One walk covers both.
            for credit in credits:
                mbid = ((credit or {}).get("artist") or {}).get("id")
                if mbid not in wanted:
                    continue
                per_artist[mbid].append(
                    {
                        "g": genres,
                        "t": tags,
                        "a": attributable and rg_artist_id(record) == mbid,
                    }
                )
                kept += 1
            if seen % 250_000 == 0:
                rate = nbytes / max(time.time() - began, 1e-9) / 1e6
                print(f"  {seen:,} release groups, {kept:,} kept "
                      f"({rate:.0f} MB/s)", flush=True)
    print(f"  pass done: {seen:,} release groups in "
          f"{(time.time() - began) / 60:.1f} min, {kept:,} kept", flush=True)
    return dict(per_artist)


def frame_sets(
    per_artist: dict[str, list[dict]], mbids: list[str], *, field: str, strict: bool
) -> dict[str, set[str]]:
    """Aggregated label set per artist under one frame."""
    out: dict[str, set[str]] = {}
    for mbid in mbids:
        labels: set[str] = set()
        for rg in per_artist.get(mbid, ()):
            if strict and not rg["a"]:
                continue
            labels |= set(rg[field])
        out[mbid] = labels
    return out


def coverage_table(
    mbids: list[str],
    frame: dict[str, float],
    f0: dict[str, set[str]],
    frames: dict[str, dict[str, set[str]]],
) -> dict:
    """Share of ALL artists in each band carrying >= 1 label, per frame.

    Denominator is every artist in the band -- the same denominator COH-2
    used, which is what makes REL-1 comparable with it rather than adjacent.
    """
    names = ["F0"] + list(frames)
    header = f"{'band':>12} {'n':>7}" + "".join(f"{n:>8}" for n in names)
    print(f"\n{header}")
    out: dict[str, dict] = {}
    for b in BAND_ORDER:
        band_mbids = [m for m in mbids if band_of(frame[m]) == b]
        n = len(band_mbids)
        if not n:
            continue
        row = {"n": n, "F0": sum(1 for m in band_mbids if f0[m])}
        for name, sets in frames.items():
            row[name] = sum(1 for m in band_mbids if f0[m] or sets[m])
        out[b] = {k: (v if k == "n" else {"count": v, "share": round(v / n, 4)})
                  for k, v in row.items()}
        cells = "".join(f"{row[name] / n:>7.1%} " for name in names)
        print(f"{b:>12} {n:>7} {cells}")
    return out


def main() -> None:
    frame = fame_frame()
    mbids = graph_mbids()
    f0 = f0_label_sets()

    per_artist = collect(set(mbids))
    OUT_RAW.write_text(json.dumps(per_artist), encoding="utf-8")

    frames = {
        "F1": frame_sets(per_artist, mbids, field="g", strict=True),
        "F2": frame_sets(per_artist, mbids, field="t", strict=True),
        "F3": frame_sets(per_artist, mbids, field="g", strict=False),
    }
    table = coverage_table(mbids, frame, f0, frames)

    lower = table["lower half"]
    print(f"\nREL-1 (F1, lower half, all artists): "
          f"{lower['F1']['share']:.1%} against a 50.0% bar "
          f"-> {'PASS' if lower['F1']['share'] >= 0.50 else 'BELOW BAR'}")
    print(f"REL-5 (F3 - F1, the validity filter's cost): "
          f"{(lower['F3']['share'] - lower['F1']['share']) * 100:+.1f} points")

    gains = {
        b: round(table[b]["F1"]["share"] - table[b]["F0"]["share"], 4)
        for b in table
    }
    print(f"REL-6 gains by band (F1 - F0): "
          + ", ".join(f"{b} {g * 100:+.1f}" for b, g in gains.items()))

    OUT.write_text(
        json.dumps(
            {
                "coverage": table,
                "rel_6_gain_points": gains,
                "artists_with_any_rg": sum(1 for m in mbids if per_artist.get(m)),
                "artists_with_attributable_rg": sum(
                    1 for m in mbids if any(rg["a"] for rg in per_artist.get(m, ()))
                ),
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"-> {OUT.name}, {OUT_RAW.name}")


if __name__ == "__main__":
    main()
