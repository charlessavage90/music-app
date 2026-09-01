"""CEX- re-census, offline half: the class per ARCHIVE population, and `ULC-F2`.

FORWARD COPY of `../2026-08-05-ulf-census/ulf_census.py`, run for plan Task 11
Step 3 over the extended 117,302-artist ALG-B archive. The original is a FROZEN
record of what was executed on 2026-08-05 and is not re-run: it writes its
outputs beside itself, one of which (`ulf_census.json`) is committed, and it
stamps everything it learns `ulf-census-2026-08-05`. Re-running it in place
would overwrite that record AND write a false provenance date into the shared
coverage store, whose whole design is per-field provenance.

TWO DIFFERENCES FROM THE ORIGINAL, and they are the only ones:
  * `STAMP` names this run, so coverage records say who wrote them.
  * outputs land in THIS directory (they are `HERE`-relative, so this follows
    from the copy rather than from an edit).
Every path it reads is `HERE.parent`-relative and so still resolves to the same
inputs. The detector, the population rule, the carry logic and the subset
assertion are byte-identical — that is the point of a copy over an edit.

Applies the ULF- rule's detector (`ULC-D2`, inherited verbatim — spec
2026-08-05-unlistenable-filter-rule.md §ULF-1) to both archive populations,
carries every frozen prior verdict forward (ULF-3, supersession without
reversal), and emits the worklist for the network half (`ulf_clips.py`).
No network here; the clip stage is the only networked step.

POPULATION IDENTITY (`ULC-F1`)
  The census population is the ARCHIVE's artist set — what a crawl extension
  grows and what `build_from_archive` reads — NOT any built graph's node set.
  The prior censuses used graph populations; a build-time identity check
  against those would false-refuse on pre-prune artists. Each population's
  identity (count + sha256 over sorted MBIDs + members) goes into the frozen
  payload, and `unlistenable_drop.py` refuses to build any archive containing
  artists outside it.

COVERAGE REUSE AND WRITE-BACK (`ULC-F2`)
  The ULC- census already computed `ULC-D2` over the 90,159-artist union of
  five graph populations (`ulc_flags.json` owns the membership; the universe
  is re-derived here from the same five sha-verified artifacts, because the
  membership list alone cannot say who was EVALUATED and found negative).
  Dump passes run only for archive artists outside both that universe and the
  coverage store — and everything this census learns is WRITTEN BACK to
  `builder/analysis/census-coverage/ulf_coverage.json`, so a future crawl
  extension pays dump passes only for genuinely new artists. That store is
  ACTIVE data, not a frozen probe output: censuses read it and write it.

PRIOR VERDICTS CARRY (ULF-3)
  Clip resolution is an artist-level fact, so verdicts carry per ARTIST
  across populations (the 2026-08-02 census already carried 2,712 this way).
  The two prior classes are globally disjoint (zero release-group credits vs
  some-but-never-sole), so no artist can hold two verdicts. This script
  ASSERTS the subset property the ULF-3 supersession argument rests on —
  every prior-verdict artist present in an archive must be in that archive's
  ULC-D2 class — and exits rather than freeze anything if it fails.

SOURCES, all local, no network:
  the two archives (flat production layout + ALG-B sub-tree, RC-H3)
  five graph artifacts, sha-verified (the ULC- universe reconstruction)
  MB release-group dump   (17 GiB)  credit split and types, delta only
  MB release dump        (322 GiB)  track counts, delta only
  MB artist dump          (16 GiB)  DSP links, Discogs id, Deezer id — full
                                    union, because the prior censuses never
                                    persisted their artist-pass results
                                    (the exact ULC-F2 defect)

  ⚠ The original said the release dump was ~17 GiB. It is 322 GiB — measured
  on disk 2026-08-09, not sparse and not compressed; the ~17 figure is the
  compressed download size. It is ~90% of the bytes a run reads and therefore
  sets the floor on the offline half's cost, so the wrong figure invites a
  five-minute estimate for an hour-long job. "Delta only" narrows the JSON
  work, never the scan: all three passes read their file end to end.

  The 2026-08-05 run over the 75k archive took 3,638 s wall (recorded in that
  directory's `ulf_census.json`). Expect the same order here — the delta grows
  matching work, not I/O.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-09-cex-recensus/ulf_census.py
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

from artistpath_builder.artifact import deserialise
from artistpath_builder.config import PERMITTED_ALGORITHMS, PRODUCTION_ALGORITHM

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
SCRATCH = ROOT / "builder" / "scratch"
DUMPS = SCRATCH / "mb-json-dumps"
COVERAGE = HERE.parent / "census-coverage" / "ulf_coverage.json"

RG_DUMP = DUMPS / "release-group" / "mbdump" / "release-group"
REL_DUMP = DUMPS / "release" / "mbdump" / "release"
ART_DUMP = DUMPS / "artist" / "mbdump" / "artist"

ALG_B = PERMITTED_ALGORITHMS[1]
ARCHIVES = {
    PRODUCTION_ALGORITHM: (SCRATCH / "graph-archive", ""),
    ALG_B: (SCRATCH / "grt-archive-algb", f"{ALG_B}/"),
}

# The ULC- universe: same five artifacts, same verification (ulc_census.py).
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
UNIVERSE_ARTIFACTS = {
    "ULC-P1": (SCRATCH / "cre-cells" / "E-S0.bin", None),
    "ULC-P2": (SCRATCH / "cre-cells" / "B-S0.bin", None),
    "ULC-P3": (SCRATCH / "cre-cells" / "E-S1.bin", None),
    "ULC-P4": (SCRATCH / "cre-cells" / "B-S1.bin", None),
    "ULC-P5": (SCRATCH / "graph-t15-tiebreakfix.bin", ADOPTED_SHA),
}
ULC_FLAGS = HERE.parent / "2026-08-05-unlistenable-class" / "ulc_flags.json"

# Prior frozen verdicts (ULF-3). Drop lists from package data (what ships);
# keeps from the committed probe outputs where the package payload lacks them
# (the ALG-B no-release keeps are tail − drop by construction).
PKG_DATA = ROOT / "builder" / "src" / "artistpath_builder" / "data"
TAIL_DROPLIST = HERE.parent / "2026-08-01-label-weighting" / "tail_droplist.json"
CTC_CENSUS = HERE.parent / "2026-08-02-candidate-tail-census" / "ctc_census.json"
CTC_DROPLIST = HERE.parent / "2026-08-02-candidate-tail-census" / "ctc_droplist.json"
FCF_LISTS = {
    PRODUCTION_ALGORITHM: PKG_DATA / "featured_credit_drop_20260803_am1.json",
    ALG_B: PKG_DATA / "featured_credit_drop_algb_20260803_am1.json",
}
NR_LISTS = {
    PRODUCTION_ALGORITHM: PKG_DATA / "no_release_drop_20260801.json",
    ALG_B: PKG_DATA / "no_release_drop_algb_20260802.json",
}

PRIMARY_OK = {"Album", "EP", "Single"}

# Same DSP set as tail_signals.py / ctc_census.py — matched, not reinvented.
DSP_HOSTS = {
    "open.spotify.com": "spotify", "spotify.com": "spotify",
    "music.apple.com": "apple", "itunes.apple.com": "apple",
    "deezer.com": "deezer", "tidal.com": "tidal", "listen.tidal.com": "tidal",
}
_DISCOGS_ID = re.compile(r"discogs\.com/artist/(\d+)")
_DEEZER_ID = re.compile(r"deezer\.com/artist/(\d+)")

STAMP = "cex-recensus-2026-08-09"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def population_sha(mbids) -> str:
    return hashlib.sha256(
        json.dumps(sorted(mbids), sort_keys=True).encode()
    ).hexdigest()


def enumerate_archive(algorithm: str) -> tuple[set[str], dict[str, str]]:
    """Archive artist set + names harvested from neighbour rows (streaming).

    Mirrors pipeline.py's RC-H3 layout rule: production reads the flat tree
    and skips nested sub-trees; every other algorithm reads its own sub-tree.
    """
    root, scope = ARCHIVES[algorithm]
    tree = root / "similar" / "listenbrainz"
    if scope:
        tree = tree / scope.rstrip("/")
    if not tree.is_dir():
        raise SystemExit(f"{algorithm}: no archive tree at {tree}")
    mbids: set[str] = set()
    names: dict[str, str] = {}
    for path in tree.iterdir():
        if path.suffix != ".json" or not path.is_file():
            continue
        mbids.add(path.stem)
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for row in rows if isinstance(rows, list) else []:
            m = row.get("artist_mbid")
            name = row.get("name")
            if m and name and m not in names:
                names[m] = name
    log(f"{algorithm[:30]}…: {len(mbids):,} archived artists, "
        f"{len(names):,} names harvested")
    return mbids, names


def load_universe() -> set[str]:
    """The ULC- census's evaluated set, re-derived from the same artifacts."""
    universe: set[str] = set()
    for pid, (path, pinned) in UNIVERSE_ARTIFACTS.items():
        payload = path.read_bytes()
        actual = hashlib.sha256(payload).hexdigest()
        expected = pinned
        if expected is None:
            sidecar = path.with_suffix(path.suffix + ".json")
            expected = json.loads(sidecar.read_text(encoding="utf-8"))["sha256"]
        if actual != expected:
            raise SystemExit(f"{pid}: checksum mismatch for {path.name} — "
                             "refusing to reconstruct the universe from the "
                             "wrong artifact")
        universe |= set(deserialise(payload).mbids)
    log(f"ULC- universe reconstructed: {len(universe):,} artists")
    return universe


def load_coverage() -> dict:
    if COVERAGE.exists():
        store = json.loads(COVERAGE.read_text(encoding="utf-8"))
        log(f"coverage store: {len(store['artists']):,} artists on file")
        return store
    return {
        "status": (
            "ACTIVE coverage store (ULC-F2), not a frozen probe output: "
            "censuses READ this and WRITE BACK what they freshly learn, so "
            "an expansion pays dump passes only for genuinely new artists. "
            "Each signal field carries its own provenance; absence of a "
            "field means UNKNOWN, never false."
        ),
        "artists": {},
    }


def pass_release_groups(wanted: set[str]):
    counts = {m: {"rg_total": 0, "rg_sole": 0, "rg_sole_primary": 0}
              for m in wanted}
    sole_primary_rg: dict[str, str] = {}
    seen = 0
    with RG_DUMP.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            seen += 1
            if seen % 1_000_000 == 0:
                log(f"  release-groups scanned: {seen:,}")
            record = json.loads(line)
            credits = record.get("artist-credit") or []
            ids = [c["artist"]["id"] for c in credits]
            relevant = [m for m in set(ids) if m in counts]
            if not relevant:
                continue
            sole = len(ids) == 1
            primary_ok = (record.get("primary-type") in PRIMARY_OK
                          and not (record.get("secondary-types") or []))
            for mbid in relevant:
                counts[mbid]["rg_total"] += 1
            if sole and ids[0] in counts:
                mbid = ids[0]
                counts[mbid]["rg_sole"] += 1
                if primary_ok:
                    counts[mbid]["rg_sole_primary"] += 1
                    sole_primary_rg[record["id"]] = mbid
    log(f"  release-groups: {seen:,} scanned; "
        f"sole+primary of interest: {len(sole_primary_rg):,}")
    return counts, sole_primary_rg


def pass_releases(sole_primary_rg: dict[str, str]) -> dict[str, int]:
    best: dict[str, int] = {}
    seen = 0
    with REL_DUMP.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            seen += 1
            if seen % 1_000_000 == 0:
                log(f"  releases scanned: {seen:,}")
            record = json.loads(line)
            rg_id = (record.get("release-group") or {}).get("id")
            if rg_id not in sole_primary_rg:
                continue
            total = sum(int(m.get("track-count") or 0)
                        for m in (record.get("media") or []))
            if total > best.get(rg_id, 0):
                best[rg_id] = total
    log(f"  releases: {seen:,} scanned; RGs with a release: {len(best):,}")
    return best


def pass_artists(wanted: set[str]) -> dict[str, dict]:
    """DSP links, Discogs id and Deezer id for the whole archive union.

    Full-union deliberately: the prior censuses read this dump and never
    persisted the result (the ULC-F2 defect this store now fixes), so there
    is nothing to reuse. ~2.5 min.
    """
    out: dict[str, dict] = {}
    seen = 0
    with ART_DUMP.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            seen += 1
            if seen % 1_000_000 == 0:
                log(f"  artists scanned: {seen:,} (matched {len(out):,})")
            record = json.loads(line)
            mbid = record.get("id")
            if mbid not in wanted:
                continue
            dsps: set[str] = set()
            discogs = deezer = None
            for rel in record.get("relations") or []:
                url = (rel.get("url") or {}).get("resource") or ""
                if "://" in url:
                    host = url.split("/")[2].lower()
                    host = host[4:] if host.startswith("www.") else host
                    if host in DSP_HOSTS:
                        dsps.add(DSP_HOSTS[host])
                if discogs is None:
                    m = _DISCOGS_ID.search(url)
                    if m:
                        discogs = m.group(1)
                if deezer is None:
                    m = _DEEZER_ID.search(url)
                    if m:
                        deezer = m.group(1)
            out[mbid] = {"dsp": sorted(dsps), "discogs": discogs,
                         "deezer": deezer}
            if len(out) == len(wanted):
                break
    log(f"  artists: {seen:,} scanned; matched {len(out):,}/{len(wanted):,}")
    return out


def load_prior_verdicts() -> dict[str, dict]:
    """Per-ARTIST frozen verdicts from all four prior lists (ULF-3)."""
    verdicts: dict[str, dict] = {}

    def add(mbids, verdict, src):
        for m in mbids:
            prior = verdicts.get(m)
            if prior and prior["verdict"] != verdict:
                raise SystemExit(
                    f"{m}: conflicting prior verdicts ({prior['src']} says "
                    f"{prior['verdict']}, {src} says {verdict}) — the "
                    "disjointness argument is wrong and ULF-3 must be "
                    "re-examined before anything freezes"
                )
            verdicts.setdefault(m, {"verdict": verdict, "src": src})

    tail = json.loads(TAIL_DROPLIST.read_text(encoding="utf-8"))
    add(tail["drop_mbids"], "drop", "no-release-2026-08-01")
    add(tail["keep_mbids"], "keep", "no-release-2026-08-01")

    ctc_tail = set(json.loads(CTC_CENSUS.read_text(encoding="utf-8"))["tail_mbids"])
    ctc_drop = set(json.loads(CTC_DROPLIST.read_text(encoding="utf-8"))["drop_mbids"])
    add(ctc_drop, "drop", "no-release-algb-2026-08-02")
    # The ALG-B payload records keeps only as a count; keeps = tail − drop by
    # construction (486 of 9,987).
    add(ctc_tail - ctc_drop, "keep", "no-release-algb-2026-08-02")

    for alg, path in FCF_LISTS.items():
        fcf = json.loads(path.read_text(encoding="utf-8"))
        src = f"fcf-am1-2026-08-03-{'algb' if alg == ALG_B else 'alge'}"
        add(fcf["drop_mbids"], "drop", src)
        add(fcf["keep_mbids"], "keep", src)

    log(f"prior verdicts carried: {len(verdicts):,} artists "
        f"({sum(1 for v in verdicts.values() if v['verdict'] == 'drop'):,} "
        f"drop, {sum(1 for v in verdicts.values() if v['verdict'] == 'keep'):,} keep)")
    return verdicts


def main() -> None:
    started = time.time()
    for path in (RG_DUMP, REL_DUMP, ART_DUMP, ULC_FLAGS):
        if not path.exists():
            raise SystemExit(f"missing input: {path}")

    populations: dict[str, set[str]] = {}
    names: dict[str, str] = {}
    for alg in ARCHIVES:
        mbids, harvested = enumerate_archive(alg)
        populations[alg] = mbids
        for m, n in harvested.items():
            names.setdefault(m, n)
    union = set().union(*populations.values())
    log(f"archive union: {len(union):,} artists")

    store = load_coverage()
    covered = {m for m, rec in store["artists"].items() if "d2" in rec}

    # Seed D2 coverage from the ULC- census where the store lacks it.
    ulc_universe = load_universe()
    d2_members = set(json.loads(ULC_FLAGS.read_text(encoding="utf-8"))["ULC-D2"])
    seeded = len(ulc_universe - covered)
    for m in ulc_universe - covered:
        store["artists"].setdefault(m, {})
        store["artists"][m]["d2"] = m in d2_members
        store["artists"][m]["d2_src"] = "ulc-census-2026-08-05"
    covered |= ulc_universe

    delta = union - covered
    log(f"D2 unknown for {len(delta):,} archive artists — dump passes run "
        f"for these only (ULC-F2)")

    if delta:
        log("pass 1/3 — release-group dump (delta)")
        counts, sole_primary_rg = pass_release_groups(delta)
        log("pass 2/3 — release dump (delta)")
        tracks = pass_releases(sole_primary_rg)
        substantial: dict[str, int] = {m: 0 for m in delta}
        unknown: dict[str, int] = {m: 0 for m in delta}
        for rg_id, mbid in sole_primary_rg.items():
            total = tracks.get(rg_id)
            if total is None:
                unknown[mbid] += 1
            elif total >= 2:
                substantial[mbid] += 1
        for m in delta:
            rec = store["artists"].setdefault(m, {})
            rec["d2"] = substantial[m] == 0
            rec["d2_src"] = STAMP
            rec["rg_sole_unknown_tracks"] = unknown[m]

    log("pass 3/3 — artist dump (full union: DSP, Discogs id, Deezer id)")
    signals = pass_artists(union)
    for m, sig in signals.items():
        rec = store["artists"].setdefault(m, {})
        rec.update(dsp=sig["dsp"], discogs=sig["discogs"], deezer=sig["deezer"],
                   signals_src=STAMP)

    def d2(m: str) -> bool:
        return bool(store["artists"].get(m, {}).get("d2"))

    classes = {alg: {m for m in pop if d2(m)} for alg, pop in populations.items()}

    # The subset property ULF-3's supersession argument rests on, asserted
    # against data rather than assumed. Same dumps as every prior census, so
    # containment must be exact; a violation means an adopted verdict would
    # be reversed, and nothing may freeze until that is understood.
    verdicts = load_prior_verdicts()
    for alg, pop in populations.items():
        violators = [m for m, v in verdicts.items()
                     if m in pop and not d2(m)]
        if violators:
            raise SystemExit(
                f"{alg}: {len(violators)} prior-verdict artists are NOT in "
                f"the ULC-D2 class (e.g. {violators[:5]}). The subset "
                "property is violated; ULF-3 must be re-examined."
            )
    log("subset property holds: every prior-verdict artist in both archives "
        "is in the class")

    class_union = set().union(*classes.values())
    fresh = class_union - set(verdicts)
    no_name = {m for m in fresh if m not in names}
    no_dsp = {m for m in fresh - no_name
              if not store["artists"].get(m, {}).get("dsp")}
    worklist = sorted(fresh - no_name - no_dsp)
    log(f"class union {len(class_union):,}: {len(class_union - fresh):,} "
        f"carried, {len(no_name):,} nameless (mechanical drop), "
        f"{len(no_dsp):,} no-DSP (mechanical drop), {len(worklist):,} to "
        "the clip stage")

    COVERAGE.parent.mkdir(exist_ok=True)
    COVERAGE.write_text(
        json.dumps(store, indent=1, sort_keys=True), encoding="utf-8"
    )
    log(f"coverage store written back: {len(store['artists']):,} artists")

    manifest = {
        alg: {
            "count": len(pop),
            "sha256_over_sorted_mbids": population_sha(pop),
        }
        for alg, pop in populations.items()
    }
    (HERE / "ulf_worklist.json").write_text(json.dumps({
        "status": ("input to ulf_clips.py — the fresh class members owed a "
                   "keep-check. Mechanical drops and carried verdicts are "
                   "recorded here for the assembly step, not re-derived."),
        "populations": {alg: sorted(pop) for alg, pop in populations.items()},
        "population_manifest": manifest,
        "classes": {alg: sorted(c) for alg, c in classes.items()},
        "carried_verdicts": {m: verdicts[m] for m in
                             sorted(class_union & set(verdicts))},
        "mechanical_drops": {
            "no_name": sorted(no_name),
            "no_dsp": sorted(no_dsp),
        },
        "worklist": [
            {"mbid": m, "name": names[m],
             "deezer": store["artists"].get(m, {}).get("deezer")}
            for m in worklist
        ],
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    (HERE / "ulf_census.json").write_text(json.dumps({
        "status": ("ULF- census, offline half. Figures for the record; the "
                   "frozen lists are assembled by ulf_droplist.py AFTER the "
                   "clip stage completes."),
        "governing": "specs/2026-08-05-unlistenable-filter-rule.md",
        "population_manifest": manifest,
        "class_per_population": {
            alg: {"n": len(c), "rate": len(c) / len(populations[alg])}
            for alg, c in classes.items()
        },
        "coverage": {
            "store_artists": len(store["artists"]),
            "d2_seeded_from_ulc": seeded,
            "delta_dump_passed_here": len(delta),
        },
        "carry": {
            "carried_verdict_artists_in_class_union":
                len(class_union & set(verdicts)),
            "fresh_class_members": len(fresh),
            "mechanical_no_name": len(no_name),
            "mechanical_no_dsp": len(no_dsp),
            "clip_worklist": len(worklist),
        },
        "elapsed_seconds": round(time.time() - started, 1),
    }, indent=1), encoding="utf-8")
    log(f"wrote ulf_census.json and ulf_worklist.json in "
        f"{round(time.time() - started, 1)}s")


if __name__ == "__main__":
    main()
