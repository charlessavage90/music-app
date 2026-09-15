"""`LBA-` stage 2, step 3 — build ONE emitted cell, instrumented for peak RSS, under scaled
acceptance criteria, and serialise it.

Shape taken from `../2026-09-10-lbd-served-population/lbv_build.py`, which this is a forward copy
of in the parts that carry over. Four differences, each deliberate:

  1. ONE build, not two. Every arm is a CENSUS build with `require_fame=False` (`LBA-D5`): no
     fame is fetched here, nothing is scored, no journey is generated. So there is no listenable
     build, no fame overlay archive and none of `LBD-AM5-4`'s three fame checks.
  2. `instrumented_build` instead of `run_build` — `LBA-G2`'s missing half. The instrument is
     `../2026-09-14-lbd-s4-stage1/stage2_build_instrument.py`, written and self-tested at stage 1.
     ONE BUILD PER PROCESS: `PeakWorkingSetSize` never falls, so a second build in one process
     would read the first one's peak. The instrument refuses rather than trusting the caller.
  3. `LBA-G2` IS READ BEFORE THE BUILD, from all builds instrumented so far (`LBA-AM2`(a), (d)).
     The first build has no fit and proceeds unconditionally — the gate is SILENT, not permissive
     (`LBA-AM2`(b)). A cell whose projection exceeds 24 GB is not built, and is recorded as
     "unbuilt for a resource reason" with §2.6's three barred conclusions attached. NO CELL IS
     STOPPED ON ANY OTHER GROUND (`LBA-D8`).
  4. Three population rules, and the un-listenable filter's state varies with them (`LBA-D7`).

THE FILTER COLUMN, AND WHY IT IS SAID RATHER THAN INFERRED (§2.4). The un-listenable drop list
removes nobody from `V`, nobody from `P`, and nobody from `U` — and those three zeroes do not mean
the same thing. Over `V` and `P` the filter is ON, APPLICABLE and MEASURED INERT, each population
with its own payload. Over `U` the census guard REFUSES (`unlistenable_drop.py` raises
`PopulationNotCensused` for any archive holding artists the census never evaluated), so a `U` arm
must set `drop_unlistenable=False` and the filter is OFF. In a configuration dump those look
identical. This script records the state per arm, in words, in the result JSON and the manifest.

⚠ AND THE TWO OTHER DROP STAGES HAVE NO GUARD AT ALL. `drop_no_release_tail` and
`drop_featured_credit` do not raise on an uncensused population — over `U` they silently
UNDER-FILTER rather than refusing. That is the failure that makes no noise, so it is recorded
explicitly per arm rather than left to be inferred from a `True`.

ACCEPTANCE IS SCALED HERE, NEVER `PRODUCTION_ACCEPTANCE`, and every bound is derived from a
quantity known INDEPENDENTLY of the build being checked — see `criteria_for` below, where each
bound carries its own derivation and the two that are deliberately weak say so.

Touches no shipped code under `builder/src`. Writes nothing under `builder/scratch/`.

    cd C:/dev/music-app/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy
      uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_build.py --arm A2
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))
sys.path.insert(0, str(HERE.parent / "2026-09-07-degree-ceiling-falsifier"))
sys.path.insert(0, str(HERE.parent / "2026-09-10-lbd-supply"))
sys.path.insert(0, str(HERE.parent / "2026-09-14-lbd-s4-stage1"))

import artistpath_api.graph_store as gs  # noqa: E402
from artistpath_builder.acceptance import AcceptanceCriteria, check_acceptance  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.artifact import serialise  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.manifest import build_manifest, write_manifest  # noqa: E402
from dcf_ceiling_sweep import ReadOnlyArchive, hub_stats  # noqa: E402  (imported, not copied)

from lbd_source import LbdBulkSource  # noqa: E402
from s4_common import bare_size_of_artifact, bare_size_of_graph, sha256_of  # noqa: E402
# `s4_instrument` is a FORWARD COPY of stage 1's `stage2_build_instrument`, fixing a name
# collision that made every real build die at teardown (`_Sampler` shadowed `Thread._stop`).
# It IMPORTS the fit rule, the 24 GB bar and the unit-safe row reader from the stage-1 module
# unchanged and redefines only the sampler and `instrumented_build`. See its docstring.
from s4_instrument import (  # noqa: E402
    instrumented_build,
    project_peak_rss,
    record_point,
    rows_from_archive_manifest,
)

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
SERVED = SCRATCH / "graph-msw-tu50.bin"
ARCHIVES = Path(r"C:\unsung-fast\lbd-archives")
ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
DATA = REPO / "builder" / "src" / "artistpath_builder" / "data"
POINTS = HERE / "_points.json"          # the running instrumented point set LBA-G2 projects from
PROJECTIONS = HERE / "_projections.json"  # every projection taken, in the order it was taken

SERVED_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"

# §2.1's ascending archive-neighbour-row order (`LBA-AM2`(c)); `rows` is stage 1's count and is
# re-read from each archive's own manifest before use, never trusted from here.
ARMS = {
    "A2": {"rule": "V", "threshold": 7, "order": 1, "population": 58838},
    "A4": {"rule": "P", "threshold": 10, "order": 2, "population": 88685},
    "A5": {"rule": "P", "threshold": 7, "order": 3, "population": 88685},
    "A6": {"rule": "P", "threshold": 3, "order": 4, "population": 88685},
    "A7": {"rule": "U", "threshold": 10, "order": 5, "population": 366996},
    "A8": {"rule": "U", "threshold": 7, "order": 6, "population": 456469},
    "A9": {"rule": "U", "threshold": 3, "order": 7, "population": 679232},
}

# `LBA-D7`. The payload is valid only for the population it censused.
DROP_STATE = {
    "V": {"drop_unlistenable": True, "list": "unlistenable_drop_algb_20260805.json",
          "column": "on, inert (20260805)",
          "why": "the 20260805 payload censused V and drops none of it (LBD-AM5-3 owns the count): "
                 "the filter is ON, APPLICABLE and removes nobody"},
    "P": {"drop_unlistenable": True, "list": "unlistenable_drop_algb_20260809.json",
          "column": "on, inert (20260809)",
          "why": "the 20260809 payload censused P and drops none of it (LBD-AM4-3 owns the count): "
                 "the filter is ON, APPLICABLE and removes nobody"},
    "U": {"drop_unlistenable": False, "list": None,
          "column": "off, uncensused",
          "why": "no committed payload censused U, and unlistenable_drop.py raises "
                 "PopulationNotCensused for any archive holding artists the census never "
                 "evaluated — so the filter is OFF. This is ABSENT-BECAUSE-REFUSED, not "
                 "inert-because-applicable, and it is §2.4's dangerous term: the arms that grow "
                 "the population are exactly the arms in which the quality filter stops operating"},
}

# Asserted equal to the served map's recorded configuration, knob by knob. `drop_unlistenable` is
# handled separately below because it is the one knob a U arm must differ on, and a blanket
# assertion would either refuse every U arm or hide the difference.
HELD_CONSTANT = ("algorithm", "cap_strategy", "union_top_j", "union_degree_ceiling",
                 "similarity_rescale", "similarity_damping", "filter_special_purpose",
                 "drop_no_release_tail", "drop_featured_credit")

# The §2.8 failure-signature detectors (acceptance.py group 1). They describe a DEFECT'S SHAPE,
# not a population's size, so they carry over unscaled at every population rule.
DETECTOR_NAMES = ("Radiohead", "The Beatles", "Coldplay", "R.E.M.")


def served_map() -> dict:
    digest = sha256_of(SERVED)
    if digest != SERVED_SHA:
        raise SystemExit(f"REFUSING: {SERVED.name} sha256 {digest} != the pinned {SERVED_SHA}")
    manifest = json.loads(SERVED.with_suffix(".bin.json").read_text(encoding="utf-8"))
    return {"sha256": digest, "manifest": manifest,
            "nodes": manifest["artists"], "edges": manifest["edges"]}


def criteria_for(arm: str, rule: str, population: int, served: dict, ceiling: int) -> tuple[AcceptanceCriteria, dict]:
    """Scaled criteria, each bound from a quantity known INDEPENDENTLY of this build.

    NEVER `PRODUCTION_ACCEPTANCE`: its node and edge bands are centred on the served artifact and
    every arm above `V` breaches them by construction. Widening them for an experimental control
    would be recalibrating a production bound to admit a new artifact, which §8 records as risk
    acceptance and the OWNER'S decision — not something a stage-2 script may do silently.
    """
    notes: dict[str, str] = {}

    # NODES, upper: hard and physical. The emitter writes a payload only for a member of the arm's
    # own population, and the largest-component prune only REMOVES, so the population size is an
    # upper bound no correct build can cross.
    node_high = population
    if rule == "U":
        # NODES, lower: DELIBERATELY WEAK, AND LABELLED. §2.4 states that the largest-component
        # prune "removes a small fraction of V and of P ... and its effect over U is UNMEASURED,
        # because U has a fringe neither smaller population has." So no calibrated floor exists
        # for a U arm. A tight one invented here would refuse a CORRECT build after half an hour,
        # and correcting a bound after seeing a build's value is exactly what §8 calls risk
        # acceptance and the owner's. 50 % is a GROSS-LOSS TRIPWIRE, not a calibrated bound.
        node_low = int(0.5 * population)
        notes["node_count"] = ("gross-loss tripwire only: the prune's effect over U is unmeasured "
                               "(§2.4), so no calibrated floor exists and a tight one would refuse "
                               "a correct build")
        # EDGES, lower: the only floor that is TRUE for a U arm without measuring the prune. Every
        # node surviving the prune has degree >= 1 (U's minimum-degree floor is 1 and is held
        # constant across all three U arms, §2.1), so CSR entries >= N >= node_low.
        edge_low = node_low
        notes["edge_count"] = ("gross-loss tripwire only: CSR entries >= N after the prune, since "
                               "U's minimum-degree floor is 1. It cannot see a cap-rule revert on "
                               "a U arm; the upper bound and the median-degree bound do")
    else:
        # V and P: §2.4 records the prune as removing a small fraction of each, with the counts
        # owned by the two build READMEs — so the production tolerance (about -20 %) around the
        # arm's own population is calibrated rather than invented. This is the V-row precedent
        # `lbv_build.py` used, applied to each rule's own population.
        node_low = int(0.8 * population)
        edge_low = int(0.8 * served["edges"])
        notes["edge_count"] = ("0.8 x the served map's CSR entries — the smallest comparable BUILT "
                               "map on the record. Generous by design: it is the gross-loss "
                               "tripwire, and on this row it is also what would see a silent "
                               "cap-rule revert (acceptance.py's CXA- note)")
    # EDGES, upper: the physical ceiling — every node of the population at the degree ceiling.
    # UNITS: `Graph.edge_count` and every sidecar's "edges" count CSR ENTRIES, each connection in
    # BOTH directions, so the ceiling is N x c and NOT N x c / 2. `lbv_build.py` records a first
    # run refused on a correct map for carrying the `// 2`; it was corrected from the UNIT, never
    # from the build's value.
    edge_high = population * ceiling

    criteria = AcceptanceCriteria(
        canonical_names=DETECTOR_NAMES,
        famous_sample=25,
        famous_median_degree_floor=25.0,
        famous_min_degree_floor=8,
        node_count=(node_low, node_high),
        edge_count=(edge_low, edge_high),
        # Supply moves median degree by design; only a value the ceiling cannot permit is a defect.
        median_degree=(1.0, float(ceiling)),
    )
    notes["famous_detectors"] = ("unscaled at every population rule: acceptance.py group 1 "
                                "describes a defect's SHAPE, not a population's size")
    notes["basis"] = (f"population {population:,} (rule {rule}, known before the build); served map "
                      f"{served['nodes']:,} nodes / {served['edges']:,} CSR entries; degree ceiling {ceiling}")
    return criteria, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    args = ap.parse_args(argv)
    arm = args.arm
    spec = ARMS[arm]
    rule = spec["rule"]
    drop = DROP_STATE[rule]
    archive_root = ARCHIVES / f"S4-{arm}"
    out_json = HERE / f"s4_build_{arm}.json"
    artifact = ARTIFACTS / f"LBA-{arm}.bin"

    if out_json.exists():
        raise SystemExit(f"REFUSING: {out_json.name} already exists — one build per cell")

    # --- identities, before anything is read ---------------------------------------------------
    archive_manifest_path = archive_root / "MANIFEST.json"
    archive_manifest = json.loads(archive_manifest_path.read_text(encoding="utf-8"))
    if archive_manifest.get("lba_arm") != f"LBA-{arm}":
        raise SystemExit(f"REFUSING: {archive_manifest_path} is not LBA-{arm}")
    params = archive_manifest["parameters"]
    if (params["threshold"], params["limit"]) != (spec["threshold"], 100):
        raise SystemExit("REFUSING: the archive's tokens are not this arm's")
    if archive_manifest["population"]["count"] != spec["population"]:
        raise SystemExit("REFUSING: the archive's population count is not this arm's")
    served = served_map()
    rows = rows_from_archive_manifest(archive_manifest_path)
    print(f"[s4] LBA-{arm}  rule {rule}  threshold {spec['threshold']}  "
          f"archive neighbour rows {rows:,} (pre-cap, two per pair — NOT CSR entries)", flush=True)
    print(f"[s4] filter: {drop['column']}", flush=True)

    # --- LBA-G2, READ BEFORE THE BUILD (LBA-AM2(a), (d)) ---------------------------------------
    points = json.loads(POINTS.read_text(encoding="utf-8")) if POINTS.exists() else []
    projection = project_peak_rss(points, rows)
    projection_record = {
        "arm": f"LBA-{arm}", "taken_utc": datetime.now(timezone.utc).isoformat(),
        "unit": "archive neighbour rows, pre-cap, two per pair — NEVER CSR entries",
        "instrumented_builds_so_far": [p["arm"] for p in points],
        **projection,
    }
    history = json.loads(PROJECTIONS.read_text(encoding="utf-8")) if PROJECTIONS.exists() else []
    history.append(projection_record)
    PROJECTIONS.write_text(json.dumps(history, indent=2), encoding="utf-8")

    if not projection["projectable"]:
        print(f"[s4] LBA-G2 is SILENT for this cell: {projection['note']}", flush=True)
    else:
        print(f"[s4] LBA-G2 projection {projection['projected_peak_rss_gib']} GiB "
              f"({projection['basis']}); bar 24 GiB; fires={projection['fires']}", flush=True)
        if projection["fires"]:
            stopped = {
                "arm": f"LBA-{arm}", "status": "unbuilt for a resource reason",
                "stopped_by": "LBA-G2", "bar_gib": 24, "projection": projection_record,
                "barred_conclusions": [
                    "No map-level read: LBA-M1, LBA-M2 and LBA-M3 are graph-level and are simply "
                    "unread for this cell. Its table-level population and pair counts stand.",
                    "No inference that the rule is unservable: build_from_archive holds neighbour "
                    "objects in a Python dict during its first pass, which is a property of the "
                    "BUILDER, not of GraphStore. 'We could not build it here' and 'it is too big "
                    "to serve' are different claims and the second needs LBA-M1.",
                    "No cross-population comparison at this threshold at the map level.",
                ],
                "note": "A resource fact, LBD-G4's shape — NOT a finding about anything.",
                "finished_utc": datetime.now(timezone.utc).isoformat(),
            }
            out_json.write_text(json.dumps(stopped, indent=2), encoding="utf-8")
            print(f"[s4] LBA-{arm} STOPPED by LBA-G2 — unbuilt for a resource reason. "
                  f"Wrote {out_json.name}", flush=True)
            return 0

    # --- configuration: LBA-D5 and LBA-D7, held-constant knobs asserted against the served map --
    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        require_fame=False,
        drop_unlistenable=drop["drop_unlistenable"],
        **({"unlistenable_list_path": DATA / drop["list"]} if drop["list"] else {}),
    )
    served_config = served["manifest"]["config"]
    differs = {k: (getattr(config, k), served_config[k])
               for k in HELD_CONSTANT if getattr(config, k) != served_config[k]}
    if differs:
        raise SystemExit(f"REFUSING: held-constant knobs differ from the served map: {differs}")
    if config.drop_unlistenable != drop["drop_unlistenable"]:
        raise SystemExit("REFUSING: the un-listenable knob is not this rule's")
    if rule != "U" and served_config["drop_unlistenable"] is not True:
        raise SystemExit("REFUSING: the served map did not apply the un-listenable filter")
    if drop["list"] and not (DATA / drop["list"]).exists():
        raise SystemExit(f"REFUSING: {drop['list']} is not in the package data")
    unguarded = {
        "drop_no_release_tail": config.drop_no_release_tail,
        "drop_featured_credit": config.drop_featured_credit,
    }
    print(f"[s4] held-constant knobs equal the served map's; unguarded drop stages {unguarded}"
          + ("  ⚠ NO CENSUS GUARD over U — these two under-filter silently rather than refusing"
             if rule == "U" else ""), flush=True)

    source = LbdBulkSource(config)
    arm_archive = ReadOnlyArchive(LocalArchive(archive_root))

    # --- the build, instrumented -----------------------------------------------------------------
    graph, build_log, point = instrumented_build(
        config, arm_archive, source, arm=f"LBA-{arm}", archive_neighbour_rows=rows)
    for line in build_log:
        print(f"  builder: {line}", flush=True)
    points = record_point(POINTS, point)
    degrees = np.diff(graph.offsets).astype(np.int64)
    whole = hub_stats(degrees, graph.mbids)
    print(f"[s4] built: nodes {graph.artist_count:,}  CSR entries {graph.edge_count:,}  "
          f"peak RSS {point.peak_rss_bytes / 1024**3:.3f} GiB  ({point.wall_clock_s / 60:.1f} min)",
          flush=True)

    # --- scaled acceptance, then serialise ------------------------------------------------------
    ceiling = config.union_degree_ceiling
    criteria, criteria_notes = criteria_for(arm, rule, spec["population"], served, ceiling)
    check_acceptance(graph, criteria)
    bare_from_graph = bare_size_of_graph(graph)
    payload = serialise(graph)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(payload)
    build_inputs = {
        "archive_dir": str(archive_root),
        "archive_manifest_sha256": sha256_of(archive_manifest_path),
        "population_rule": rule,
        "unlistenable_filter": drop["column"],
        "amendment": "LBA- stage 2",
    }
    manifest = build_manifest(graph, config, payload, point.wall_clock_s, build_inputs)
    write_manifest(artifact, manifest)
    reloaded = gs.GraphStore.load(artifact)
    if sha256_of(artifact) != manifest["sha256"] or len(reloaded.mbids) != graph.artist_count:
        raise SystemExit("BUG: the written artifact does not round-trip")
    if not np.array_equal(reloaded.offsets, graph.offsets):
        raise SystemExit("BUG: the written artifact lost structure on reload")
    bare = bare_size_of_artifact(artifact)
    if bare["bare_artifact_bytes"] != bare_from_graph["bare_artifact_bytes"]:
        raise SystemExit("BUG: the bare size differs between the graph in hand and the decoded artifact")
    if bare["additive_keys_present"]:
        raise SystemExit(f"BUG: a fame-free census build carries additive keys {bare['additive_keys_present']}")
    print(f"[s4] wrote {artifact}  sha256 {manifest['sha256']}  "
          f"on disk {len(payload) / 1e6:.1f} MB  bare {bare['bare_artifact_bytes'] / 1e6:.1f} MB", flush=True)

    result = {
        "arm": f"LBA-{arm}",
        "plain_sentence": PLAIN[arm],
        "population_rule": rule,
        "population_rule_exposure": ("LBA-X6 — U's membership moves with the threshold, so a U-row "
                                     "threshold comparison has the population as a DEPENDENT "
                                     "variable and is not one-column in the sense V and P are"
                                     if rule == "U" else None),
        "threshold": spec["threshold"],
        "filter": drop["column"],
        "filter_meaning": drop["why"],
        "unguarded_drop_stages": unguarded,
        "unguarded_drop_stages_note": ("drop_no_release_tail and drop_featured_credit have NO census "
                                       "guard: over U they silently UNDER-FILTER rather than refusing"
                                       if rule == "U" else "both applicable over this population"),
        "build_order_position": spec["order"],
        "script_sha256": sha256_of(Path(__file__)),
        "instrument_sha256": sha256_of(HERE / "s4_instrument.py"),
        "instrument_note": ("s4_instrument.py — a forward copy of stage 1's "
                            "stage2_build_instrument.py, fixing a Thread._stop name collision "
                            "that made every real build raise at teardown. The fit rule, the "
                            "24 GB bar and the row reader are IMPORTED from the stage-1 module "
                            "unchanged."),
        "stage1_instrument_sha256": sha256_of(
            HERE.parent / "2026-09-14-lbd-s4-stage1" / "stage2_build_instrument.py"),
        "archive": {"root": str(archive_root),
                    "manifest_sha256": sha256_of(archive_manifest_path),
                    "payloads": archive_manifest["counts"]["payloads_written"],
                    "neighbour_rows": rows,
                    "population_absent_from_arm": archive_manifest["counts"]["P_absent_from_arm"]},
        "lba_g2": {"read_before_the_build": True, **projection_record},
        "peak_rss": point.as_dict(),
        "built": {
            "nodes_after_largest_component_prune": int(graph.artist_count),
            "csr_entries": int(graph.edge_count),
            "connections_degree_sum_over_2": whole["edges"],
            "median_degree": float(statistics.median(degrees.tolist())),
            "max_degree": whole["max_degree"],
            "ceiling_binds": whole["max_degree"] >= ceiling,
            "bound_holds": whole["max_degree"] <= ceiling,
            "retention_vs_population": round(graph.artist_count / spec["population"], 5),
            "wall_clock_s": round(point.wall_clock_s, 1),
            "builder_log": build_log,
        },
        "bare_artifact": bare,
        "artifact": {"path": str(artifact), "sha256": manifest["sha256"],
                     "serialised_bytes": len(payload)},
        "acceptance": {"criteria": dataclasses.asdict(criteria), "notes": criteria_notes,
                       "passed": True, "production_acceptance_used": False},
        "config": {k: getattr(config, k) for k in HELD_CONSTANT}
        | {"drop_unlistenable": config.drop_unlistenable,
           "unlistenable_list_path": drop["list"], "require_fame": False},
        "held_constant_equal_to_served_config": True,
        "units": ("csr_entries and every sidecar's 'edges' = each connection in BOTH directions; "
                  "connections_degree_sum_over_2 = counted once; archive.neighbour_rows = pre-cap, "
                  "two per pair. Three different units — never compared across."),
        "not_taken_here": ["LBA-M2", "LBA-M3", "LBA-M4", "LBA-M5"],
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[s4] wrote {out_json.name}  ({len(points)} instrumented build(s) now on the record)", flush=True)
    return 0


# Quoted verbatim from §2.2, fixed before any result existed.
PLAIN = {
    "A2": "the same artists, but a connection is kept when three different people's listening "
          "supports it instead of four",
    "A4": "every artist the deeper crawl found, at ListenBrainz's own bar",
    "A5": "every artist the deeper crawl found, at the three-listener bar",
    "A6": "every artist the deeper crawl found, at the two-listener bar",
    "A7": "every artist anywhere in ListenBrainz's listening data who gets a connection at "
          "ListenBrainz's own bar — not just the ones our crawl happened to discover",
    "A8": "the same, at the three-listener bar",
    "A9": "the same, at the two-listener bar",
}


if __name__ == "__main__":
    sys.exit(main())
