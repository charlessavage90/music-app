"""Re-extract all four id/fact maps over the `LBA-A6` candidate's population.

WHY, and it is the owner's ruling of 2026-09-21. The three shipped maps are frozen snapshots
extracted over the ADOPTED artifact's population — today's served map. Measured over the
candidate's node set they cover 40.87 % / 51.24 % / 37.49 % / 73.55 %, and over the **29,485
artists the candidate adds** only 11.41 % / 15.25 % / 10.10 % / 26.99 %. A missing Deezer id
degrades to name search, which is the `BYP-13` surface — a card playing a different artist of the
same name — concentrated on exactly the artists the use gate will be looking at hardest.
`deezer_ids.py`'s own docstring anticipates this: *"Before an `ALG-B` artifact is ever served,
re-extract over its population."*

A FORWARD COPY, NEVER AN EDIT IN PLACE, on the 2026-08-09 precedent. The frozen extractors
(`2026-08-02-dsp-ids/dsp_ids.py`, `2026-09-05-lux4-extract/lux4_extract.py`) are **imported, not
copied**, so every parsing rule here is theirs byte for byte: `host_of`, `id_tail`,
`is_artist_url`, `normalise_id`, `facts_of`, `clean_date` and the `DSP` host table. New dated
package data is written beside the old; **no existing dated file is touched.**

⚠ ONE KNOB, DELIBERATELY. The only thing that changes is the POPULATION. In particular Deezer
keeps `dsp_ids.py`'s original rule — a numeric tail, with no `is_artist_url` check, which
`lux4_extract.py` later added for Spotify and Apple. Applying it to Deezer too would probably be
an improvement, and it is deliberately NOT done here: it would make this a two-column change and
there would be no way afterwards to attribute a coverage difference to the population alone.
Recorded as a deferral instead.

POPULATION: strictly additive, and that is deliberate. It is the candidate's node set UNION the
served map's UNION every key the three existing maps already hold. The owner asked for the
candidate's node set; taking the union as well costs nothing (the dump read dominates) and means
**no lineage can regress** — the candidate keeps 57,909 of the served map's artists but not all
58,838, so a candidate-only extraction would silently drop ids for 929 artists the served map
still contains. The frozen extractors used a superset for the same reason.

The candidate's node set is read from `LBA-A6-bare.bin`, pinned by sha256 and already proved
byte-identical in node order to the candidate build (`README.md` §3a) — so this does not need the
candidate serialised first.

Read-only, offline, no network. One pass over the 17 GB artist dump; the two frozen scripts record
~2 minutes and "minutes" respectively for the same pass.

    cd C:/dev/music-app/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-21-lbd-s4-a6-candidate/cand_ids_extract.py
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for _p in (REPO / "api" / "src", HERE.parent / "2026-09-05-lux4-extract"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from artistpath_api.graph_store import GraphStore  # noqa: E402
from lux4_extract import (  # noqa: E402  IMPORTED, NOT COPIED — these are the frozen rules
    DSP,
    facts_of,
    host_of,
    id_tail,
    is_artist_url,
    normalise_id,
)

DUMP = REPO / "builder/scratch/mb-json-dumps/artist/mbdump/artist"
SERVED = REPO / "builder/scratch/graph-msw-tu50.bin"
SERVED_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
CANDIDATE_BARE = Path(r"C:\unsung-fast\lbd-artifacts\LBA-A6-bare.bin")
CANDIDATE_BARE_SHA = "f35cb19d935d53a184173d006791334b42b0b64ee9b7593b1c3ab1029b7c8d6d"

SRC = REPO / "builder" / "src" / "artistpath_builder"
DATA = SRC / "data"
STAMP = "20260921"
OUT = HERE / "cand_ids_extract.json"

OLD = {
    "deezer": DATA / "deezer_artist_ids_20260802.json",
    "dsp": DATA / "dsp_links_20260905.json",
    "facts": DATA / "artist_facts_20260905.json",
}
NEW = {
    "deezer": DATA / f"deezer_artist_ids_{STAMP}.json",
    "dsp": DATA / f"dsp_links_{STAMP}.json",
    "facts": DATA / f"artist_facts_{STAMP}.json",
}

_DUMP_DESC = "MusicBrainz JSON artist dump, 2026-07-28 (the same dump the 2026-08-02 and 2026-09-05 extractions read)"
_POPULATION = (
    "union of the LBA-A6 candidate's node set (87,394, from LBA-A6-bare.bin f35cb19d...), the "
    "served artifact graph-msw-tu50.bin (43dd82bb...), and every key the 2026-08-02 and "
    "2026-09-05 maps already held. Strictly additive: no lineage this project has ever built "
    "loses an id it previously had."
)
_SOURCE = "analysis/2026-09-21-lbd-s4-a6-candidate/cand_ids_extract.py"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha_items(m: dict) -> str:
    """`make_package_data.py`'s identity sha, reproduced exactly."""
    return hashlib.sha256(
        json.dumps(sorted(m.items()), sort_keys=True).encode()
    ).hexdigest()


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def _pin(module: Path, constant: str, value: str) -> None:
    """Rewrite one string constant in place. `make_package_data.py`'s helper."""
    text = io.open(module, encoding="utf-8").read()
    pattern = re.compile(rf'^{constant} = "[^"]*"$', re.MULTILINE)
    if not pattern.search(text):
        raise SystemExit(f"{module.name}: no assignment for {constant}")
    io.open(module, "w", encoding="utf-8").write(pattern.sub(f'{constant} = "{value}"', text))


def _repoint(module: Path, constant: str, filename: str) -> None:
    """Move a *_PATH constant onto the new dated file, leaving the old file on disk."""
    text = io.open(module, encoding="utf-8").read()
    pattern = re.compile(
        rf'^({constant} = Path\(__file__\)\.parent / "data" / )"[^"]*"$', re.MULTILINE
    )
    if not pattern.search(text):
        raise SystemExit(f"{module.name}: no path assignment for {constant}")
    io.open(module, "w", encoding="utf-8").write(pattern.sub(rf'\1"{filename}"', text))


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"REFUSING: {OUT.name} already exists — one extraction per candidate")
    for path, expected, label in ((SERVED, SERVED_SHA, "graph-msw-tu50.bin"),
                                  (CANDIDATE_BARE, CANDIDATE_BARE_SHA, "LBA-A6-bare.bin")):
        got = sha256_of(path)
        if got != expected:
            raise SystemExit(f"REFUSING: {label} sha256 {got} != pinned {expected}")
    if not DUMP.exists():
        raise SystemExit(f"REFUSING: artist dump not found at {DUMP}")
    for key, path in NEW.items():
        if path.exists():
            raise SystemExit(f"REFUSING: {path.name} already exists — never overwrite dated data")

    served_mbids = list(GraphStore.load(SERVED).mbids)
    cand_mbids = list(GraphStore.load(CANDIDATE_BARE).mbids)
    served_set, cand_set = set(served_mbids), set(cand_mbids)

    old_payloads = {k: json.loads(p.read_text(encoding="utf-8")) for k, p in OLD.items()}
    old_deezer = old_payloads["deezer"]["deezer_ids"]
    old_spotify = old_payloads["dsp"]["spotify_ids"]
    old_apple = old_payloads["dsp"]["apple_ids"]
    old_facts = old_payloads["facts"]["artist_facts"]
    prior_keys = set(old_deezer) | set(old_spotify) | set(old_apple) | set(old_facts)

    population = cand_set | served_set | prior_keys
    added = [m for m in cand_mbids if m not in served_set]
    print(f"[ids] candidate {len(cand_set):,}  served {len(served_set):,}  "
          f"prior-map keys {len(prior_keys):,}  population {len(population):,}", flush=True)
    print(f"[ids] candidate-only artists: {len(added):,}", flush=True)

    deezer: dict[str, str] = {}
    spotify: dict[str, str] = {}
    apple: dict[str, str] = {}
    facts: dict[str, dict] = {}
    seen: set[str] = set()
    rejected: Counter = Counter()
    scanned = 0
    started = time.monotonic()

    with DUMP.open(encoding="utf-8") as f:
        for line in f:
            scanned += 1
            if scanned % 500_000 == 0:
                print(f"  ...{scanned:,} scanned, {len(deezer):,} deezer, "
                      f"{len(spotify):,} spotify, {len(apple):,} apple, "
                      f"{len(facts):,} facts", flush=True)
            d = json.loads(line)
            mbid = d.get("id")
            if mbid not in population:
                continue
            seen.add(mbid)

            f_ = facts_of(d)
            if f_:
                facts.setdefault(mbid, f_)

            for r in d.get("relations") or []:
                url = (r.get("url") or {}).get("resource")
                if not url:
                    continue
                platform = DSP.get(host_of(url))
                if platform == "deezer":
                    # `dsp_ids.py`'s ORIGINAL rule, unchanged on purpose — see the
                    # module docstring's "ONE KNOB" paragraph.
                    tail = id_tail(url)
                    if not tail or not tail.isdigit():
                        rejected["deezer"] += 1
                        continue
                    deezer.setdefault(mbid, tail)
                elif platform in ("spotify", "apple"):
                    ident = normalise_id(platform, id_tail(url)) if is_artist_url(url) else ""
                    if not ident:
                        rejected[platform] += 1
                        continue
                    (spotify if platform == "spotify" else apple).setdefault(mbid, ident)

    elapsed = time.monotonic() - started
    print(f"[ids] scanned {scanned:,} dump rows in {elapsed / 60:.1f} min; "
          f"matched {len(seen):,} of {len(population):,} population artists", flush=True)

    # --- strictly additive: nothing the old maps held may be lost ------------------------------
    lost = {
        "deezer": sorted(set(old_deezer) - set(deezer))[:5],
        "spotify": sorted(set(old_spotify) - set(spotify))[:5],
        "apple": sorted(set(old_apple) - set(apple))[:5],
        "artist_facts": sorted(set(old_facts) - set(facts))[:5],
    }
    lost_counts = {
        "deezer": len(set(old_deezer) - set(deezer)),
        "spotify": len(set(old_spotify) - set(spotify)),
        "apple": len(set(old_apple) - set(apple)),
        "artist_facts": len(set(old_facts) - set(facts)),
    }
    if any(lost_counts.values()):
        raise SystemExit(
            f"REFUSING: the re-extraction LOSES coverage the shipped maps already had. "
            f"counts={lost_counts} examples={lost}. The population is a superset, so this can "
            f"only mean a parsing rule changed — which this script is written not to do."
        )
    print("[ids] strictly additive: every MBID the three shipped maps held is still present",
          flush=True)

    def cover(m, keys):
        return sum(1 for k in keys if k in m)

    coverage = {}
    for name, new_m, old_m in (("deezer_ids", deezer, old_deezer),
                               ("spotify_ids", spotify, old_spotify),
                               ("apple_ids", apple, old_apple),
                               ("artist_facts", facts, old_facts)):
        coverage[name] = {
            "map_size": {"before": len(old_m), "after": len(new_m)},
            "served_map_pct": {"before": round(cover(old_m, served_mbids) / len(served_mbids) * 100, 2),
                               "after": round(cover(new_m, served_mbids) / len(served_mbids) * 100, 2)},
            "candidate_pct": {"before": round(cover(old_m, cand_mbids) / len(cand_mbids) * 100, 2),
                              "after": round(cover(new_m, cand_mbids) / len(cand_mbids) * 100, 2)},
            "added_artists_pct": {"before": round(cover(old_m, added) / len(added) * 100, 2),
                                  "after": round(cover(new_m, added) / len(added) * 100, 2)},
            "candidate_count_after": cover(new_m, cand_mbids),
        }
        c = coverage[name]
        print(f"[ids] {name:<14} candidate {c['candidate_pct']['before']:>6.2f}% -> "
              f"{c['candidate_pct']['after']:>6.2f}%   added artists "
              f"{c['added_artists_pct']['before']:>6.2f}% -> {c['added_artists_pct']['after']:>6.2f}%",
              flush=True)

    # --- write the dated package data; never touch the existing dated files --------------------
    _write(NEW["deezer"], {
        "status": f"Frozen {STAMP[:4]}-{STAMP[4:6]}-{STAMP[6:]} snapshot. MusicBrainz artist -> "
                  "Deezer artist id. Never re-resolved at build time: build_from_archive is "
                  "offline by a hard rule and spec section 9 requires byte-identical output.",
        "purpose": "Resolve clips by artist identity instead of by name, so a card cannot play a "
                   "different artist of the same name (BYP-13).",
        "dump": _DUMP_DESC,
        "population": _POPULATION,
        "ids_are_numeric": "Deezer artist endpoint takes a numeric id. Links ending in a name "
                           "slug are discarded at extraction, exactly as the 2026-08-02 map did.",
        "source": _SOURCE,
        "sha256_over_sorted_items": _sha_items(deezer),
        "deezer_ids": deezer,
    })
    _write(NEW["dsp"], {
        "status": f"Frozen {STAMP[:4]}-{STAMP[4:6]}-{STAMP[6:]} snapshot. MusicBrainz artist -> "
                  "Spotify and Apple Music artist id. Never re-resolved at build time.",
        "purpose": "Deep-link a journey card to the artist on each service. Ids, not URLs "
                   "(L4-D2): the frontend composes the URL.",
        "dump": _DUMP_DESC,
        "population": _POPULATION,
        "ids_are_normalised": "Apple ids are the bare numeric form; MusicBrainz records the same "
                              "artist as .../657515 and .../id657515 and both normalise here.",
        "source": _SOURCE,
        "spotify_ids_sha256": _sha_items(spotify),
        "apple_ids_sha256": _sha_items(apple),
        "spotify_ids": spotify,
        "apple_ids": apple,
    })
    _write(NEW["facts"], {
        "status": f"Frozen {STAMP[:4]}-{STAMP[4:6]}-{STAMP[6:]} snapshot of structured "
                  "MusicBrainz artist fields. Never re-resolved at build time.",
        "purpose": "Orient a listener on a journey card without prose.",
        "dump": _DUMP_DESC,
        "population": _POPULATION,
        "absence_is_the_empty_state": "An artist with no facts is absent; a missing field is "
                                      "omitted rather than null.",
        "source": _SOURCE,
        "artist_facts_sha256": _sha_items(facts),
        "artist_facts": facts,
    })

    _pin(SRC / "deezer_ids.py", "DEEZER_IDS_SHA256", _sha_items(deezer))
    _repoint(SRC / "deezer_ids.py", "DEEZER_IDS_PATH", NEW["deezer"].name)
    _pin(SRC / "dsp_links.py", "SPOTIFY_IDS_SHA256", _sha_items(spotify))
    _pin(SRC / "dsp_links.py", "APPLE_IDS_SHA256", _sha_items(apple))
    _repoint(SRC / "dsp_links.py", "DSP_LINKS_PATH", NEW["dsp"].name)
    _pin(SRC / "artist_facts.py", "ARTIST_FACTS_SHA256", _sha_items(facts))
    _repoint(SRC / "artist_facts.py", "ARTIST_FACTS_PATH", NEW["facts"].name)
    print("[ids] package data written and all four sha constants re-pinned from the same read",
          flush=True)

    OUT.write_text(json.dumps({
        "task": "re-extract the id and fact maps over the LBA-A6 candidate's population",
        "ruling": "the owner's, 2026-09-21 — partially discharges NEXT.md's LUX-4 deferral",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "dump": _DUMP_DESC,
        "population": {
            "rule": _POPULATION,
            "candidate": len(cand_set), "served": len(served_set),
            "prior_map_keys": len(prior_keys), "total": len(population),
            "candidate_only_artists": len(added),
        },
        "one_knob": "population only. Deezer keeps dsp_ids.py's original numeric-tail rule with "
                    "no is_artist_url check; adding it would be a second column and is deferred.",
        "scan": {"dump_rows": scanned, "matched": len(seen),
                 "elapsed_s": round(elapsed, 1), "rejected_relations": dict(rejected)},
        "strictly_additive": {"lost_from_shipped_maps": lost_counts},
        "coverage": coverage,
        "written": {k: str(v) for k, v in NEW.items()},
        "previous_left_untouched": {k: str(v) for k, v in OLD.items()},
        "script_sha256": sha256_of(Path(__file__)),
    }, indent=2), encoding="utf-8")
    print(f"[ids] wrote {OUT.name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
