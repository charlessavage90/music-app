"""Resolve clips for the candidate tail's DSP-linked artists, and emit the list.

DIAGNOSTIC plus a LIST. It applies the ALREADY-ADOPTED rule (frozen 2026-08-01)
to the candidate population; it does not reopen the rule, set a bar, or adopt
anything. The owner ruled on 2026-08-02 that the rule needs no re-validation on
this population, and why: it rests on claims about MusicBrainz completeness,
not on which artists are in the graph.

SCOPE -- why 491 and not 9,987
  The rule drops iff no release group AND no Discogs release AND NOT (DSP link
  AND a clip resolves). An artist with no DSP link is cut whatever the clip
  says. Of the candidate's 9,987-artist no-release tail, 3,003 already carry a
  frozen verdict from today's census and 6,493 of the remainder have no DSP
  link, so only 491 need a network lookup. Verified against tail_clips.py:162,
  which selects the same way.

IMPORTED, NEVER RESTATED
  `name_path`, `id_path` and the pauses come from tail_clips.py, which in turn
  imports `same_artist` from the app. Two resolvers would be two chances for
  the candidate list and today's list to disagree for reasons unrelated to the
  artists.

THE SNAPSHOT HAZARD APPLIES HERE TOO
  This is a 2026-08-02 snapshot and must never be re-resolved at build time:
  `build_from_archive` is offline by a hard rule and spec §9 requires
  byte-identical builds.

NAME SOURCE
  Names come from the built ALG-B cells -- what the app would display and
  therefore what it would search. The ID path is the instrument check on the
  name path; the gap between them is this population's BYP-13 rate.

Run from `builder/` (~20 min, resumable, checkpoint every 25):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-candidate-tail-census/ctc_clips.py
"""

from __future__ import annotations

import json
import sys
import time

from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
_WGT = HERE.parent / "2026-08-01-label-weighting"
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
for _p in (str(_WGT), str(_TAS), str(ROOT / "api" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tail_clips import PAUSE_DEEZER, id_path, name_path  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402

SCRATCH = ROOT / "builder" / "scratch"
CELLS = SCRATCH / "cb-cells"
MB_ARTIST = SCRATCH / "mb-json-dumps" / "artist" / "mbdump" / "artist"
CENSUS = HERE / "ctc_census.json"
FROZEN = HERE.parent / "2026-08-01-label-weighting" / "tail_droplist.json"
OUT = HERE / "ctc_clips.json"
DROPLIST = HERE / "ctc_droplist.json"
CKPT = HERE / "ctc_clips.checkpoint.json"
CKPT_EVERY = 25

DSP_HOSTS = {
    "open.spotify.com": "spotify", "spotify.com": "spotify",
    "music.apple.com": "apple", "itunes.apple.com": "apple",
    "deezer.com": "deezer", "tidal.com": "tidal", "listen.tidal.com": "tidal",
}


def host_of(url: str) -> str:
    if "://" not in url:
        return ""
    host = url.split("/")[2].lower()
    return host[4:] if host.startswith("www.") else host


def names_from_cells(wanted: set[str]) -> dict[str, str]:
    """mbid -> display name, from the built ALG-B cells, manifests verified."""
    names: dict[str, str] = {}
    for path in sorted(CELLS.glob("ALG-B-*.bin")):
        manifest = json.loads(Path(f"{path}.json").read_text(encoding="utf-8"))
        recorded = manifest.get("sha256") or manifest.get("artifact_sha256")
        if sha256(path.read_bytes()).hexdigest() != recorded:
            raise SystemExit(f"{path.name}: manifest mismatch")
        store = GraphStore.load(path)
        for i, mbid in enumerate(store.mbids):
            if mbid in wanted and mbid not in names:
                names[mbid] = store.names[i]
        if len(names) == len(wanted):
            break
    return names


def dsp_links(wanted: set[str]) -> dict[str, dict]:
    """One MB artist-dump pass: DSP platforms and the Deezer/Apple ids."""
    found: dict[str, dict] = {}
    began = time.time()
    with MB_ARTIST.open(encoding="utf-8") as fh:
        for line in fh:
            record = json.loads(line)
            mbid = record.get("id")
            if mbid not in wanted:
                continue
            dsps: set[str] = set()
            ids: dict[str, str] = {}
            for rel in record.get("relations") or []:
                url = (rel.get("url") or {}).get("resource")
                if not url:
                    continue
                host = host_of(url)
                if host in DSP_HOSTS:
                    platform = DSP_HOSTS[host]
                    dsps.add(platform)
                    tail = url.rstrip("/").split("/")[-1]
                    if platform in ("deezer", "apple") and tail:
                        ids.setdefault(platform, tail)
            found[mbid] = {"dsp": sorted(dsps), "ids": ids}
            if len(found) == len(wanted):
                break
    print(f"  artist pass: {len(found):,} of {len(wanted):,} in "
          f"{(time.time() - began) / 60:.1f} min", flush=True)
    return found


def main() -> None:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    decided = set(frozen["drop_mbids"]) | set(frozen["keep_mbids"])

    tail = set(census["tail_mbids"])
    new = tail - decided
    print(f"candidate tail {len(tail):,}; already decided {len(tail & decided):,}; "
          f"new {len(new):,}", flush=True)

    signals = dsp_links(new)
    targets = sorted(m for m in new if signals[m]["dsp"])
    print(f"DSP-linked, needing a lookup: {len(targets):,}", flush=True)

    names = names_from_cells(set(targets))

    done: dict[str, dict] = {}
    if CKPT.exists():
        done = json.loads(CKPT.read_text(encoding="utf-8"))["done"]
        print(f"resuming: {len(done):,} already checked", flush=True)

    pending = [m for m in targets if m not in done]
    for n, mbid in enumerate(pending, 1):
        name = names.get(mbid, "")
        record: dict = {"name": name, "dsp": signals[mbid]["dsp"]}
        time.sleep(PAUSE_DEEZER)
        record["name_path"] = name_path(name) if name.strip() else {
            "resolves": False, "refused": ["no name"], "matched_artist_id": None
        }
        deezer_id = signals[mbid]["ids"].get("deezer")
        if deezer_id:
            time.sleep(PAUSE_DEEZER)
            record["id_path"] = id_path(deezer_id)
            record["mb_deezer_id"] = deezer_id
        done[mbid] = record
        if n % CKPT_EVERY == 0 or n == len(pending):
            CKPT.write_text(json.dumps({"done": done}), encoding="utf-8")
            print(f"  {n:,}/{len(pending):,} checked", flush=True)

    # --- the rule, applied -------------------------------------------------
    resolves = {m for m, r in done.items() if r["name_path"].get("resolves")}
    refused = {m for m, r in done.items()
               if not r["name_path"].get("resolves") and r["name_path"].get("refused")}
    keep_new = sorted(resolves)
    drop_new = sorted(m for m in new if m not in resolves)

    # BYP-13: name path landed on a DIFFERENT Deezer artist than MB recorded.
    checked = [r for r in done.values()
               if r.get("mb_deezer_id") and r["name_path"].get("matched_artist_id")]
    wrong = [r for r in checked
             if r["name_path"]["matched_artist_id"] != r["mb_deezer_id"]]
    byp13 = round(len(wrong) / len(checked), 4) if checked else None

    payload = {
        "status": ("DIAGNOSTIC plus a list. Applies the rule frozen 2026-08-01 to "
                   "the candidate population. Adopts nothing."),
        "snapshot": "2026-08-02. Never re-resolve at build time (spec §9).",
        "scope": {
            "candidate_tail": len(tail),
            "already_decided_by_the_2026_08_01_list": len(tail & decided),
            "new": len(new),
            "dsp_linked_and_checked": len(targets),
            "cut_without_a_lookup": len(new) - len(targets),
        },
        "clips": {
            "resolved": len(resolves),
            "did_not_resolve": len(targets) - len(resolves) - len(refused),
            "refused_service_declined_not_a_miss": len(refused),
        },
        "byp13_wrong_artist_rate": byp13,
        "byp13_denominator": len(checked),
        "verdict_new_artists_only": {"drop": len(drop_new), "keep": len(keep_new)},
        "platforms": dict(Counter(
            p for m in targets for p in signals[m]["dsp"]
        ).most_common()),
        "per_artist": done,
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    combined = sorted(set(frozen["drop_mbids"]) & tail | set(drop_new))
    DROPLIST.write_text(
        json.dumps(
            {
                "status": ("Candidate-side drop list, 2026-08-02. The rule is the "
                           "one adopted 2026-08-01, applied to the ALG-B "
                           "population. Never re-resolve at build time."),
                "rule": frozen["rule"],
                "population": "union of the twelve built ALG-B cells",
                "counts": {
                    "tail": len(tail),
                    "drop": len(combined),
                    "keep": len(tail) - len(combined),
                    "carried_from_the_2026_08_01_list": len(set(frozen["drop_mbids"]) & tail),
                    "new_here": len(drop_new),
                },
                "drop_mbids": combined,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    digest = sha256(json.dumps(combined, sort_keys=True).encode()).hexdigest()
    print(f"\nresolved {len(resolves):,} of {len(targets):,} checked; "
          f"{len(refused):,} refused")
    print(f"BYP-13 wrong-artist rate: {byp13} over {len(checked):,}")
    print(f"CANDIDATE DROP LIST: {len(combined):,} of {len(tail):,} tail "
          f"({len(tail) - len(combined):,} kept)")
    print(f"drop-list sha256 (sorted mbids): {digest}")
    print(f"-> {OUT.name}, {DROPLIST.name}")


if __name__ == "__main__":
    main()
