"""`LBD-AM5` Step 2 — build `LBD-A0V` or `LBD-A5V`, census it against the served map, run
`LBD-AM5-4`'s three fame checks, and serialise a listenable map under scaled criteria.

Two builds of the same emitted archive, in-process through the shipped `build_from_archive`:

  1. the CENSUS build — `LBD-AM5-3`'s configuration with `require_fame=False`, exactly the shape
     `lbd_build_census.py` used for the fixed-population arms (only the population and the pinned
     un-listenable file differ, both by amendment);
  2. the LISTENABLE build — the same configuration with `require_fame=True`, reading fame through
     the shipped `load_fame` from an archive view that serves the arm's similarity responses from
     its emitted archive and `fame/<mbid>.json` from `grt-archive-algb.pre-cex-snapshot`, the
     served lineage's archive. Both archives are wrapped read-only (`GRT-A1`).

`LBD-AM5-4`'s checks, each a refusal: (i) every node of the arm is in `V`, and the snapshot holds
a fame record for every member of `V`; (ii) every such record equals the served artifact's own
`fame_lb`; (iii) the listenable build is structurally identical to the census build. Then
`check_acceptance` with SCALED criteria built here from the served map's sidecar counts and the
degree ceiling — quantities known independently of either build — never `PRODUCTION_ACCEPTANCE`;
then `serialise`, `build_manifest`, `write_manifest` to `C:\\unsung-fast\\lbd-artifacts\\`, and a
round-trip load through the shipped `GraphStore`. Nothing is deployed; nothing is written under
`builder/scratch/`.

Before building, the configuration's held-constant knobs are asserted equal to the served map's
recorded configuration, and the three drop-list files' bytes are asserted equal to the ones the
served lineage's rebuild recorded (`graph-lux4.bin.json`). `LBD-AM5`'s factor table says so.

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u analysis/2026-09-10-lbd-served-population/lbv_build.py --map A0V
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import logging
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))
sys.path.insert(0, str(HERE.parent / "2026-09-07-degree-ceiling-falsifier"))
sys.path.insert(0, str(HERE.parent / "2026-09-10-lbd-supply"))

import artistpath_api.graph_store as gs  # noqa: E402
from artistpath_builder.acceptance import AcceptanceCriteria, check_acceptance  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.artifact import serialise  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.fame import fame_key  # noqa: E402
from artistpath_builder.manifest import build_manifest, write_manifest  # noqa: E402
from artistpath_builder.pipeline import build_from_archive  # noqa: E402
from dcf_ceiling_sweep import ArchiveWriteRefused, ReadOnlyArchive, hub_stats, set_stats  # noqa: E402  (imported, not copied)

from lbd_source import LbdBulkSource  # noqa: E402

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
SERVED = SCRATCH / "graph-msw-tu50.bin"
LUX4_SIDECAR = SCRATCH / "graph-lux4.bin.json"
SNAPSHOT = SCRATCH / "grt-archive-algb.pre-cex-snapshot"
ARCHIVES = Path(r"C:\unsung-fast\lbd-archives")
ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
DATA = REPO / "builder" / "src" / "artistpath_builder" / "data"
DROP_LISTS = {
    "unlistenable": "unlistenable_drop_algb_20260805.json",
    "no_release": "no_release_drop_algb_20260802.json",
    "featured_credit": "featured_credit_drop_algb_20260803_am1.json",
}
PREEXISTING = Path(r"D:\unsung-large-data\lbd-inputs\cxr_preexisting_mbids.txt")
PREEXISTING_SHA = "768054b7e84769346193336ec7e9b3496af92d0d3e8d4ae2fb287057912b5229"
COVERAGE = HERE / "lbv_coverage.json"
# Every path a map touches is a constant here, so no command-line text reaches a path.
MAPS = {
    "A0V": {"arm": "LBD-A0", "token": "LBD-A0V", "threshold": 10, "limit": 100,
            "archive": ARCHIVES / "A0V", "artifact": ARTIFACTS / "LBD-A0V.bin",
            "result": HERE / "lbv_build_A0V.json"},
    "A5V": {"arm": "LBD-A5", "token": "LBD-A5V", "threshold": 3, "limit": 100,
            "archive": ARCHIVES / "A5V", "artifact": ARTIFACTS / "LBD-A5V.bin",
            "result": HERE / "lbv_build_A5V.json"},
}
HELD_CONSTANT = ("algorithm", "cap_strategy", "union_top_j", "union_degree_ceiling", "similarity_rescale",
                 "similarity_damping", "filter_special_purpose", "drop_no_release_tail",
                 "drop_featured_credit", "drop_unlistenable")
# The §2.8 failure-signature detectors (acceptance.py, group 1) and its famous-sample floors: they
# describe a defect's shape, not the population's size, so they carry over unscaled.
DETECTOR_NAMES = ("Radiohead", "The Beatles", "Coldplay", "R.E.M.")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


class FameOverlayArchive:
    """Similarity responses from the arm's archive; `fame/` records from the snapshot. Never writes."""

    def __init__(self, similarity, fame) -> None:
        self._similarity = similarity
        self._fame = fame

    def _for(self, key: str):
        return self._fame if key.startswith("fame/") else self._similarity

    def put(self, key: str, payload: bytes) -> None:
        raise ArchiveWriteRefused(f"lbv_build tried to write {key!r}; both archives are read-only here")

    def get(self, key: str):
        return self._for(key).get(key)

    def has(self, key: str) -> bool:
        return self._for(key).has(key)

    def keys(self):
        return self._similarity.keys()


class LogCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(record.getMessage())


def served_map() -> dict:
    """The served artifact: identity, parsed store, degrees, and its raw `fame_lb` by MBID.

    Raw fame is read from the metadata blob located exactly as `graph_store.py` locates it (the
    `lbd_build_census.py` precedent), checked against the shipped parser's node order.
    """
    manifest = json.loads(SERVED.with_suffix(".bin.json").read_text(encoding="utf-8"))
    payload = SERVED.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != manifest["sha256"]:
        raise SystemExit(f"REFUSING: {SERVED.name} sha256 {digest} != sidecar {manifest['sha256']}")
    store = gs.GraphStore.from_bytes(payload)
    _magic, _version, n, e, meta_len = gs._HEADER.unpack_from(payload)
    cursor = gs._HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor : cursor + meta_len])
    if list(meta["mbids"]) != list(store.mbids):
        raise SystemExit("REFUSING: served metadata mbids disagree with the shipped parser")
    if "fame_lb" not in meta or len(meta["fame_lb"]) != n:
        raise SystemExit("REFUSING: the served artifact carries no fame_lb")
    degrees = np.diff(store.offsets).astype(np.int64)
    return {
        "manifest": manifest, "sha256": digest, "store": store,
        "fame": dict(zip(store.mbids, meta["fame_lb"])),
        "degrees": degrees, "degrees_by_mbid": {m: int(degrees[i]) for i, m in enumerate(store.mbids)},
    }


def assert_same_structure(a, b) -> None:
    """`LBD-AM5-4` (iii): fame is metadata; the map itself must not move when it is attached."""
    for field in ("mbids", "names", "disambiguations", "deezer_ids", "spotify_ids", "apple_ids", "artist_facts"):
        if list(getattr(a, field)) != list(getattr(b, field)):
            raise SystemExit(f"REFUSING (iii): {field} differs between the census and listenable builds")
    for field in ("offsets", "neighbours", "scores", "edge_types"):
        if not np.array_equal(np.asarray(getattr(a, field)), np.asarray(getattr(b, field))):
            raise SystemExit(f"REFUSING (iii): {field} differs between the census and listenable builds")
    if not np.array_equal(np.asarray(a.pop_raw, dtype=np.float64), np.asarray(b.pop_raw, dtype=np.float64)):
        raise SystemExit("REFUSING (iii): pop_raw differs between the census and listenable builds")


def run_build(config: BuilderConfig, archive, source) -> tuple[object, list[str], float]:
    capture = LogCapture()
    log = logging.getLogger("artistpath_builder")
    log.addHandler(capture)
    log.setLevel(logging.INFO)
    started = time.monotonic()
    try:
        graph = build_from_archive(config, archive, source)
    finally:
        log.removeHandler(capture)
    return graph, capture.lines, time.monotonic() - started


def paired_change(arm_degrees: dict[str, int], served_degrees: dict[str, int], mbids: list[str]) -> dict:
    deltas = [arm_degrees.get(m, 0) - served_degrees[m] for m in mbids]
    return {
        "n": len(mbids),
        "gained": sum(1 for d in deltas if d > 0),
        "lost": sum(1 for d in deltas if d < 0),
        "same": sum(1 for d in deltas if d == 0),
        "median_delta": float(statistics.median(deltas)),
        "mean_delta": round(float(np.mean(deltas)), 3),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True, choices=sorted(MAPS))
    args = ap.parse_args(argv)
    spec = MAPS[args.map]
    token = spec["token"]
    archive_root = spec["archive"]
    out_json = spec["result"]

    # --- identities -----------------------------------------------------------------------------
    archive_manifest_path = archive_root / "MANIFEST.json"
    archive_manifest = json.loads(archive_manifest_path.read_text(encoding="utf-8"))
    served = served_map()
    if archive_manifest.get("map_token") != token or archive_manifest["arm"] != spec["arm"]:
        raise SystemExit(f"REFUSING: {archive_manifest_path} is not {token}")
    if archive_manifest["population"]["artifact_sha256"] != served["sha256"]:
        raise SystemExit("REFUSING: the archive was emitted over a different population artifact")
    params = archive_manifest["parameters"]
    if (params["threshold"], params["limit"]) != (spec["threshold"], spec["limit"]):
        raise SystemExit("REFUSING: the archive's tokens are not this map's")
    print(f"[lbv] {token}  archive MANIFEST sha256 {sha256_of(archive_manifest_path)}", flush=True)
    print(f"[lbv] served {SERVED.name} sha256 {served['sha256']}  nodes {len(served['store'].mbids):,}", flush=True)

    v = set(served["store"].mbids)
    pre_bytes = PREEXISTING.read_bytes()
    if hashlib.sha256(pre_bytes).hexdigest() != PREEXISTING_SHA:
        raise SystemExit("REFUSING: the pre-existing set is not the pinned file")
    pre = [line.strip() for line in pre_bytes.decode("utf-8").splitlines() if line.strip()]
    v_minus_p = json.loads(COVERAGE.read_text(encoding="utf-8"))["V_minus_P"]["mbids"]
    if not set(pre) <= v or not set(v_minus_p) <= v or len(pre) + len(v_minus_p) != len(v):
        raise SystemExit("REFUSING: pre-existing + (V − P) does not partition V")

    # --- configuration: LBD-AM5-3, held-constant knobs asserted against the served map ----------
    drop_list_shas = {k: sha256_of(DATA / f) for k, f in DROP_LISTS.items()}
    lux4_lists = json.loads(LUX4_SIDECAR.read_text(encoding="utf-8"))["build_inputs"]["drop_lists"]
    for k, f in DROP_LISTS.items():
        if lux4_lists[k]["file"] != f or lux4_lists[k]["sha256"] != drop_list_shas[k]:
            raise SystemExit(f"REFUSING: the {k} list is not the served lineage's recorded file")
    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        require_fame=False,
        drop_unlistenable=True,
        unlistenable_list_path=DATA / DROP_LISTS["unlistenable"],
    )
    served_config = served["manifest"]["config"]
    differs = {k: (getattr(config, k), served_config[k]) for k in HELD_CONSTANT if getattr(config, k) != served_config[k]}
    if differs:
        raise SystemExit(f"REFUSING: held-constant knobs differ from the served map: {differs}")
    source = LbdBulkSource(config)

    # --- 1. the census build ---------------------------------------------------------------------
    arm_archive = ReadOnlyArchive(LocalArchive(archive_root))
    census, census_log, census_s = run_build(config, arm_archive, source)
    for line in census_log:
        print(f"  builder: {line}", flush=True)
    degrees = np.diff(census.offsets).astype(np.int64)
    degrees_by_mbid = {m: int(degrees[i]) for i, m in enumerate(census.mbids)}
    nodes = set(census.mbids)
    if not nodes <= v:
        raise SystemExit(f"BUG (i): {len(nodes - v)} built nodes are outside V")
    whole = hub_stats(degrees, census.mbids)
    print(f"[lbv] census: nodes {whole['nodes']:,}  edges {whole['edges']:,}  retention vs V "
          f"{len(nodes) / len(v):.4f}  ({census_s / 60:.1f} min)", flush=True)

    # --- 2. the listenable build, and LBD-AM5-4's checks ----------------------------------------
    snapshot = ReadOnlyArchive(LocalArchive(SNAPSHOT))
    missing = [m for m in sorted(v) if not snapshot.has(fame_key(m))]
    if missing:
        raise SystemExit(f"REFUSING (i): the snapshot holds no fame record for {len(missing)} members of V, "
                         f"e.g. {missing[:3]} — re-run the fame stage (LBD-AM5-4)")
    mismatched = []
    for m in sorted(v):
        value = json.loads(snapshot.get(fame_key(m)))["fame_lb_raw"]
        if value != served["fame"][m]:
            mismatched.append((m, value, served["fame"][m]))
    if mismatched:
        raise SystemExit(f"REFUSING (ii): {len(mismatched)} snapshot fame records differ from the served "
                         f"artifact's fame_lb, e.g. {mismatched[:3]} — these are not the served map's records")
    print(f"[lbv] fame (i) records present for all {len(v):,} members of V; (ii) all equal the served map's", flush=True)

    config_f = dataclasses.replace(config, require_fame=True)
    listenable, listenable_log, listenable_s = run_build(config_f, FameOverlayArchive(arm_archive, snapshot), source)
    assert_same_structure(census, listenable)
    if list(listenable.fame_lb_raw) != [served["fame"][m] for m in listenable.mbids]:
        raise SystemExit("BUG: the listenable build's fame is not the served map's, artist by artist")
    print(f"[lbv] fame (iii) listenable build structurally identical to the census build  "
          f"({listenable_s / 60:.1f} min)", flush=True)
    del census

    # --- scaled acceptance, serialise, write, round-trip ---------------------------------------
    served_nodes, served_edges = served["manifest"]["artists"], served["manifest"]["edges"]
    ceiling = config.union_degree_ceiling
    criteria = AcceptanceCriteria(
        canonical_names=DETECTOR_NAMES,
        famous_sample=25,
        famous_median_degree_floor=25.0,
        famous_min_degree_floor=8,
        # The emitter can write no artist outside V, so V's size is a hard upper bound; the lower
        # bound is the production tolerance (about -20 %) around the served count.
        node_count=(int(0.8 * served_nodes), served_nodes),
        # Denser is this intervention's expected direction, so the upper bound is the physical one:
        # every node of V at the degree ceiling. UNITS: `Graph.edge_count` and the sidecar's "edges"
        # count CSR entries, i.e. each connection in BOTH directions — so the ceiling is N x c, not
        # N x c / 2. (`hub_stats`' "edges" is the other unit, degree sum / 2.) The first run carried
        # `// 2` and was refused on a correct map; corrected from the unit, never from the build's
        # value — execution log, Step 2.
        edge_count=(int(0.8 * served_edges), served_nodes * ceiling),
        # Supply moves median degree by design; only a value outside what the ceiling permits is a defect.
        median_degree=(1.0, float(ceiling)),
    )
    check_acceptance(listenable, criteria)
    payload = serialise(listenable)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    artifact = spec["artifact"]
    artifact.write_bytes(payload)
    build_inputs = {
        "archive_dir": str(archive_root),
        "archive_manifest_sha256": sha256_of(archive_manifest_path),
        "fame_records": {"archive_dir": str(SNAPSHOT), "rule": "LBD-AM5-4 — the served map's own records, by MBID"},
        "drop_lists": {k: {"file": f, "sha256": drop_list_shas[k]} for k, f in DROP_LISTS.items()},
        "amendment": "LBD-AM5",
    }
    manifest = build_manifest(listenable, config_f, payload, census_s + listenable_s, build_inputs)
    write_manifest(artifact, manifest)
    reloaded = gs.GraphStore.load(artifact)
    if sha256_of(artifact) != manifest["sha256"] or len(reloaded.mbids) != listenable.artist_count:
        raise SystemExit("BUG: the written artifact does not round-trip")
    if reloaded.fame_lb_pctl is None or not np.array_equal(reloaded.offsets, listenable.offsets):
        raise SystemExit("BUG: the written artifact lost fame or structure on reload")
    print(f"[lbv] wrote {artifact}  sha256 {manifest['sha256']}  {len(payload) / 1e6:.1f} MB", flush=True)

    # --- the record -----------------------------------------------------------------------------
    result = {
        "map": token,
        "arm": spec["arm"],
        "amendment": "LBD-AM5",
        "script_sha256": sha256_of(Path(__file__)),
        "archive": {"root": str(archive_root), "manifest_sha256": sha256_of(archive_manifest_path),
                    "payloads": archive_manifest["counts"]["payloads_written"],
                    "neighbour_rows": archive_manifest["counts"]["neighbour_rows_written"],
                    "V_absent_from_arm": archive_manifest["counts"]["P_absent_from_arm"]},
        "served": {"artifact": SERVED.name, "sha256": served["sha256"], "nodes": served_nodes, "edges": served_edges,
                   "whole_graph": hub_stats(served["degrees"], served["store"].mbids),
                   "sets": {"preexisting": set_stats(served["degrees_by_mbid"], pre),
                            "V_minus_P": set_stats(served["degrees_by_mbid"], v_minus_p)}},
        "config": {k: getattr(config, k) for k in HELD_CONSTANT} | {
            "unlistenable_list_path": DROP_LISTS["unlistenable"], "require_fame_census": False,
            "require_fame_listenable": True},
        "held_constant_equal_to_served_config": True,
        "drop_lists_equal_to_served_lineage": True,
        "census": {
            "elapsed_seconds": round(census_s, 1),
            "builder_log": census_log,
            "whole_graph": whole,
            "retention_vs_V": round(len(nodes) / len(v), 5),
            "ceiling_binds": whole["max_degree"] >= ceiling,
            "bound_holds": whole["max_degree"] <= ceiling,
            "sets": {"preexisting": set_stats(degrees_by_mbid, pre), "V_minus_P": set_stats(degrees_by_mbid, v_minus_p)},
            "preexisting_paired_vs_served": paired_change(degrees_by_mbid, served["degrees_by_mbid"], pre),
        },
        "fame": {
            "i_snapshot_records_missing_for_V": 0,
            "ii_records_differing_from_served_fame_lb": 0,
            "iii_listenable_structurally_identical_to_census": True,
            "nulls_among_arm_nodes": sum(1 for x in listenable.fame_lb_raw if x is None),
            "listenable_builder_log": listenable_log,
            "listenable_elapsed_seconds": round(listenable_s, 1),
        },
        "acceptance": {"criteria": dataclasses.asdict(criteria), "passed": True,
                       "production_acceptance_used": False},
        "artifact": {"path": str(artifact), "sha256": manifest["sha256"], "bytes": len(payload),
                     "artists": listenable.artist_count,
                     "edge_count_csr_entries_both_directions": listenable.edge_count},
        "units": "whole_graph.edges (census and served) = connections counted once (degree sum / 2); "
                 "artifact.edge_count_csr_entries_both_directions and every sidecar's 'edges' = twice that",
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    out_json.with_suffix(".degrees.json").write_text(json.dumps({
        "preexisting": {m: degrees_by_mbid.get(m, 0) for m in pre},
        "V_minus_P": {m: degrees_by_mbid.get(m, 0) for m in v_minus_p},
    }), encoding="utf-8")
    for name in ("preexisting", "V_minus_P"):
        a, s = result["census"]["sets"][name], result["served"]["sets"][name]
        print(f"  {name:<12} n {a['n']:>6,}  median {a.get('median_degree')} (served {s.get('median_degree')})  "
              f"<=2|absent {a['share_le_2_or_absent']:.4f} (served {s['share_le_2_or_absent']:.4f})", flush=True)
    print(f"[lbv] wrote {out_json.name}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
