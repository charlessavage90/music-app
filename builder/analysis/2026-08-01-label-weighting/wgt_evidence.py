"""`WGT-` dump parses: the vote and release-level evidence the committed parses discarded.

WHY THIS EXISTS. `rel_common.labels_from` keeps only `item["name"]` from a dump
record's tag list, so every committed frame is a binary set and the vote counts
MusicBrainz ships beside every tag were thrown away at parse time. `EV-A` needs
them back (artist-page votes), and `WGT-4` needs the release dump streamed once
for the three scoping readings (incremental reach, incremental evidence, the
reissue confound). Discogs needs no pass here: it carries no vote data at all --
verified at schema level 2026-08-01 -- and its presence signal is already in the
committed `rel_discogs_raw.json`. Release-GROUP support (`EV-G`) likewise needs
no pass: it is a count over the committed `rel_rg_raw.json`.

VOTE SEMANTICS. MusicBrainz `count` is net votes and can in principle be zero or
negative (downvoted tags). Stored raw here; the grid clamps at 0 when building
`s(a, l)`, so a downvoted label contributes no strength. Where one normalised
label appears in both `tags` and `genres` the MAX count is kept, never the sum --
the genre entry is the same tag through MusicBrainz's genre whitelist, so summing
would double-count the same people.

THE RELEASE PASS IS RESUMABLE and checkpoint offsets are tracked by summing line
lengths, never `fh.tell()` -- binary iteration read-ahead makes `tell()` point
past the line being processed, so a resume from it would silently skip records.
Per the pre-registration: THE PASS RUNS TO THE END OF THE DUMP REGARDLESS OF ANY
PARTIAL FIGURE; a number from a partial pass is not a `WGT-4` figure.

Single-credit rule: a release counts toward an artist only when the artist credit
names exactly one artist and that artist is in the graph -- the same
attributability shape as `rel_rg_dump`'s strict frame. Untagged releases still
count toward `rgs` (releases per release group), because `WGT-4c`'s reissue
confound needs pressing counts regardless of tagging.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-01-label-weighting/wgt_evidence.py --artist-pass
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-01-label-weighting/wgt_evidence.py --release-pass
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (_TAS, _REL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from rel_common import MB_ARTIST, norm_genre  # noqa: E402
from tas_common import graph_mbids  # noqa: E402

MB_RELEASE = MB_ARTIST.parents[2] / "release" / "mbdump" / "release"
OUT_VOTES = HERE / "wgt_artist_votes.json"
OUT_RELEASE = HERE / "wgt_release_raw.json"
CKPT = HERE / "wgt_release_raw.ckpt.json"

CKPT_EVERY_BYTES = 25 * 1024**3


def votes_from(record: dict, field: str) -> dict[str, int]:
    """Normalised label -> vote count from a dump record's `tags` or `genres`.

    Same normalisation and empty-label rule as the committed `labels_from`,
    keeping the `count` it discards. MAX on collision within one field too --
    two raw names can normalise to one label.
    """
    out: dict[str, int] = {}
    for item in record.get(field) or []:
        name = item.get("name")
        if not name:
            continue
        lab = norm_genre(name)
        if not lab:
            continue
        c = int(item.get("count") or 0)
        if c > out.get(lab, -(10**9)):
            out[lab] = c
    return out


def merged_votes(record: dict) -> dict[str, int]:
    merged = votes_from(record, "tags")
    for lab, c in votes_from(record, "genres").items():
        if c > merged.get(lab, -(10**9)):
            merged[lab] = c
    return merged


def artist_pass() -> None:
    wanted = set(graph_mbids())
    found: dict[str, dict[str, int]] = {}
    began, nbytes = time.time(), 0
    with MB_ARTIST.open("rb") as fh:
        for line in fh:
            nbytes += len(line)
            record = json.loads(line)
            if record.get("id") not in wanted:
                continue
            found[record["id"]] = merged_votes(record)
            if len(found) % 10000 == 0:
                rate = nbytes / max(time.time() - began, 1e-9) / 1e6
                print(f"  {len(found)}/{len(wanted)} matched ({rate:.0f} MB/s)", flush=True)
    OUT_VOTES.write_text(json.dumps(found), encoding="utf-8")
    print(f"artist pass done in {(time.time() - began) / 60:.1f} min; "
          f"{len(found)} artists -> {OUT_VOTES.name}", flush=True)


def release_pass() -> None:
    wanted = set(graph_mbids())
    data: dict[str, dict] = {}
    offset = 0
    if CKPT.exists():
        ck = json.loads(CKPT.read_text(encoding="utf-8"))
        offset, data = ck["offset"], ck["data"]
        print(f"resuming at byte {offset:,} with {len(data)} artists held", flush=True)

    total = MB_RELEASE.stat().st_size
    began, since_ckpt = time.time(), 0
    kept = 0
    with MB_RELEASE.open("rb") as fh:
        fh.seek(offset)
        for line in fh:
            offset += len(line)
            since_ckpt += len(line)
            record = json.loads(line)
            ac = record.get("artist-credit") or []
            if len(ac) == 1:
                artist = (ac[0].get("artist") or {}).get("id")
                if artist in wanted:
                    kept += 1
                    rg = (record.get("release-group") or {}).get("id") or ""
                    bucket = data.setdefault(artist, {"labels": {}, "rgs": {}})
                    bucket["rgs"][rg] = bucket["rgs"].get(rg, 0) + 1
                    for lab in merged_votes(record):
                        bucket["labels"][lab] = bucket["labels"].get(lab, 0) + 1
            if since_ckpt >= CKPT_EVERY_BYTES:
                since_ckpt = 0
                CKPT.write_text(json.dumps({"offset": offset, "data": data}),
                                encoding="utf-8")
                mins = (time.time() - began) / 60
                rate = offset / max(time.time() - began, 1e-9) / 1e6
                eta = (total - offset) / max(rate * 1e6, 1) / 60
                print(f"  {offset / 1e9:.0f}/{total / 1e9:.0f} GB  {rate:.0f} MB/s  "
                      f"{kept} releases kept  {mins:.0f} min in, ~{eta:.0f} min left",
                      flush=True)

    OUT_RELEASE.write_text(json.dumps(data), encoding="utf-8")
    CKPT.unlink(missing_ok=True)
    print(f"release pass done in {(time.time() - began) / 60:.1f} min; "
          f"{len(data)} artists, {kept} releases -> {OUT_RELEASE.name}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artist-pass", action="store_true")
    ap.add_argument("--release-pass", action="store_true")
    args = ap.parse_args()
    if not (args.artist_pass or args.release_pass):
        raise SystemExit("pick a pass: --artist-pass and/or --release-pass")
    if args.artist_pass:
        artist_pass()
    if args.release_pass:
        release_pass()


if __name__ == "__main__":
    main()
