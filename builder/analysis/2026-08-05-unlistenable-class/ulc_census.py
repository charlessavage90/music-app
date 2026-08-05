"""ULC-C1: census the un-listenable class across five populations.

DIAGNOSTIC ONLY. Adopts nothing, changes no default, touches no shipped code.
Governing document: docs/superpowers/specs/2026-08-05-unlistenable-class-preregistration.md
-- it fixes every predicate and every bar BEFORE this ran, and it governs
wherever this script disagrees.

WHAT IS COUNTED (pre-registration section 1.3)
  rg_total            release-group credits of any shape
  rg_sole             credits where this artist is the ONLY credited artist
  rg_sole_primary     of those, primary-type in {Album, EP, Single} and no
                      secondary types
  rg_sole_substantial of those, carrying >= 1 release of >= 2 total tracks

THE PREDICATES, all fixed in advance -- see ULC-B8: reported, NEVER selected
from after the fact.
  ULC-D2  PRIMARY, and the one ULC-G1 evaluates (ULC-AM3, owner-ruled):
          rg_sole_substantial == 0 -- "has never put out anything of their own
          that is more than a single track"
  ULC-D0  rg_sole_primary == 0        (the pre-AM3 primary, retained as a rung)
  ladder  rg_sole_primary <= 1, <= 2
  ULC-D1  ULC-D2 AND a supporting-musician relation (ULC-AM1(b)) -- a strict
          SUBSET of D2, so it cannot move ULC-G1's branch

THE UNKNOWN-TRACK-COUNT AMBIGUITY (ULC-AM3, and it is NOT adjudicated here)
  A sole+primary release group with no release in the dump has an unknown track
  count. Primary reading follows the owner's asymmetry ruling and treats unknown
  as NOT substantial; `ULC_D2_alt` reports the opposite reading; the count of
  affected artists is reported in both. If it is small the question is moot.

POPULATION NOTE THAT MUST TRAVEL (section 0.3)
  ULC-P5 is the artifact the app actually serves and it carries NEITHER drop
  flag -- it predates the drop wiring. It has no isolating baseline and is
  reported alone. Mixing it into a cross-archive sentence is barred (ULC-B4).

SOURCES, all local, no network:
  MB release-group dump   ~18 GiB    the credit split and types
  MB release dump         ~17 GiB    track counts, joined by release-group id
  MB artist dump          ~17 GiB    supporting-musician relations

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-unlistenable-class/ulc_census.py
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from artistpath_builder.artifact import deserialise

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
SCRATCH = ROOT / "builder" / "scratch"
DUMPS = SCRATCH / "mb-json-dumps"

RG_DUMP = DUMPS / "release-group" / "mbdump" / "release-group"
REL_DUMP = DUMPS / "release" / "mbdump" / "release"
ART_DUMP = DUMPS / "artist" / "mbdump" / "artist"

# Section 0.1. P5's sha is the adopted artifact's, asserted rather than read
# from a sidecar -- findings/2026-07-23-tiebreak-fix-adoption.md owns it.
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
POPULATIONS = {
    "ULC-P1": (SCRATCH / "cre-cells" / "E-S0.bin", None),
    "ULC-P2": (SCRATCH / "cre-cells" / "B-S0.bin", None),
    "ULC-P3": (SCRATCH / "cre-cells" / "E-S1.bin", None),
    "ULC-P4": (SCRATCH / "cre-cells" / "B-S1.bin", None),
    "ULC-P5": (SCRATCH / "graph-t15-tiebreakfix.bin", ADOPTED_SHA),
}

PRIMARY_OK = {"Album", "EP", "Single"}
SUPPORTING_RELATIONS = {
    "member of band",
    "instrumental supporting musician",
    "instrument",
    "vocal",
    "performer",
}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_populations() -> tuple[dict[str, set[str]], dict[str, dict]]:
    """Node sets, each verified against its manifest sidecar (section 0.1)."""
    sets: dict[str, set[str]] = {}
    provenance: dict[str, dict] = {}
    for pid, (path, pinned_sha) in POPULATIONS.items():
        payload = path.read_bytes()
        actual = hashlib.sha256(payload).hexdigest()
        expected = pinned_sha
        sidecar = path.with_suffix(path.suffix + ".json")
        if expected is None:
            if not sidecar.exists():
                raise SystemExit(f"{pid}: no manifest sidecar beside {path.name}")
            expected = json.loads(sidecar.read_text(encoding="utf-8"))["sha256"]
        if actual != expected:
            raise SystemExit(
                f"{pid}: checksum mismatch for {path.name}.\n"
                f"  expected {expected}\n  actual   {actual}\n"
                "Refusing to census an artifact that is not the one named. A "
                "conclusion drawn from the wrong artifact looks exactly like a "
                "correct one."
            )
        graph = deserialise(payload)
        sets[pid] = set(graph.mbids)
        provenance[pid] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": actual,
            "nodes": len(sets[pid]),
        }
        log(f"{pid}: {len(sets[pid]):,} nodes, sha verified")
    return sets, provenance


def pass_release_groups(universe: set[str]) -> tuple[dict[str, dict], dict[str, str]]:
    """Credit shape per artist, restricted to the union of node sets."""
    counts: dict[str, dict] = {m: {"rg_total": 0, "rg_sole": 0, "rg_sole_primary": 0}
                               for m in universe}
    sole_primary_rg: dict[str, str] = {}  # release-group id -> sole artist mbid
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
    log(f"  release-groups scanned: {seen:,} (done); "
        f"sole+primary of interest: {len(sole_primary_rg):,}")
    return counts, sole_primary_rg


def pass_releases(sole_primary_rg: dict[str, str]) -> dict[str, int]:
    """Max total track count per release group of interest (ULC-AM3 decision 1)."""
    best: dict[str, int] = {}
    seen = 0
    with REL_DUMP.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            seen += 1
            if seen % 1_000_000 == 0:
                log(f"  releases scanned: {seen:,}")
            record = json.loads(line)
            rg = record.get("release-group") or {}
            rg_id = rg.get("id")
            if rg_id not in sole_primary_rg:
                continue
            total = sum(int(m.get("track-count") or 0)
                        for m in (record.get("media") or []))
            if total > best.get(rg_id, 0):
                best[rg_id] = total
    log(f"  releases scanned: {seen:,} (done); "
        f"release-groups with a release found: {len(best):,}")
    return best


def pass_artists(universe: set[str]) -> dict[str, dict]:
    """Supporting-musician relations per artist (ULC-AM1(b))."""
    out: dict[str, dict] = {}
    seen = 0
    with ART_DUMP.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            seen += 1
            if seen % 1_000_000 == 0:
                log(f"  artists scanned: {seen:,}")
            record = json.loads(line)
            mbid = record.get("id")
            if mbid not in universe:
                continue
            kinds: dict[str, int] = {}
            for rel in (record.get("relations") or []):
                t = rel.get("type")
                if t in SUPPORTING_RELATIONS:
                    kinds[t] = kinds.get(t, 0) + 1
            out[mbid] = {
                "supporting": sum(kinds.values()),
                "kinds": kinds,
                "type": record.get("type"),
            }
    log(f"  artists scanned: {seen:,} (done); matched {len(out):,}")
    return out


def main() -> None:
    started = time.time()
    sets, provenance = load_populations()
    universe: set[str] = set().union(*sets.values())
    log(f"union of all five node sets: {len(universe):,} artists")

    log("pass 1/3 -- release-group dump")
    counts, sole_primary_rg = pass_release_groups(universe)
    log("pass 2/3 -- release dump")
    tracks = pass_releases(sole_primary_rg)
    log("pass 3/3 -- artist dump")
    artists = pass_artists(universe)

    # Fold the track-count join back per artist.
    for mbid in universe:
        counts[mbid]["rg_sole_substantial"] = 0
        counts[mbid]["rg_sole_unknown_tracks"] = 0
    for rg_id, mbid in sole_primary_rg.items():
        total = tracks.get(rg_id)
        if total is None:
            counts[mbid]["rg_sole_unknown_tracks"] += 1
        elif total >= 2:
            counts[mbid]["rg_sole_substantial"] += 1

    def flags(mbid: str) -> dict[str, bool]:
        c = counts[mbid]
        d2 = c["rg_sole_substantial"] == 0
        return {
            "ULC-D2": d2,
            "ULC-D2-alt": d2 and c["rg_sole_unknown_tracks"] == 0,
            "ULC-D0": c["rg_sole_primary"] == 0,
            "ladder-le1": c["rg_sole_primary"] <= 1,
            "ladder-le2": c["rg_sole_primary"] <= 2,
            "ULC-D1": d2 and artists.get(mbid, {}).get("supporting", 0) > 0,
        }

    all_flags = {m: flags(m) for m in universe}
    names = list(next(iter(all_flags.values())).keys())

    per_population = {}
    for pid, members in sets.items():
        n = len(members)
        row = {"nodes": n}
        for name in names:
            hit = sum(1 for m in members if all_flags[m][name])
            row[name] = {"n": hit, "rate": hit / n if n else None}
        row["unknown_track_artists"] = sum(
            1 for m in members if counts[m]["rg_sole_unknown_tracks"] > 0
        )
        per_population[pid] = row

    validation = json.loads((HERE / "ulc_validation.json").read_text(encoding="utf-8"))
    v1 = validation["ULC_V1"]
    # ULC-AM4: Four Tet is an identity doubt, not an availability one.
    four_tet = "3bcff06f-675a-451f-9075-99e8657047e8"
    v1_target = {m: a for m, a in v1.items() if m != four_tet}
    v2 = validation["ULC_V2"]

    def capture(pool: dict) -> dict:
        out = {}
        for name in names:
            caught = [m for m in pool if all_flags.get(m, {}).get(name)]
            out[name] = {"caught": len(caught), "of": len(pool)}
        out["per_artist"] = {
            pool[m]["name"]: {
                "in_universe": m in all_flags,
                **{k: v for k, v in counts.get(m, {}).items()},
                "supporting_relations": artists.get(m, {}).get("supporting"),
                **{name: all_flags.get(m, {}).get(name) for name in names},
            }
            for m in pool
        }
        return out

    payload = {
        "status": "diagnostic only -- adopts nothing, fixes no criterion, sets no bar",
        "governing": "specs/2026-08-05-unlistenable-class-preregistration.md",
        "provenance": provenance,
        "universe": len(universe),
        "ULC_C1_per_population": per_population,
        "ULC_V1_capture": capture(v1_target),
        "ULC_V2_capture": capture(v2),
        "elapsed_seconds": round(time.time() - started, 1),
    }
    out = HERE / "ulc_census.json"
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"wrote {out.name} in {payload['elapsed_seconds']}s")

    print("\n--- ULC-V1 capture (target class, 6 artists) ---", flush=True)
    for name in names:
        c = payload["ULC_V1_capture"][name]
        print(f"  {name:12} {c['caught']}/{c['of']}", flush=True)
    print("\n--- rate per population ---", flush=True)
    for pid, row in per_population.items():
        print(f"  {pid}  nodes={row['nodes']:,}  "
              f"D2={row['ULC-D2']['rate']:.2%}  D0={row['ULC-D0']['rate']:.2%}  "
              f"D1={row['ULC-D1']['rate']:.2%}", flush=True)


if __name__ == "__main__":
    main()
