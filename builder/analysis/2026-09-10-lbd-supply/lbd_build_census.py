"""`LBD-` Task 7 — build one emitted arm through the SHIPPED builder and census it.

The build is `build_from_archive` in-process (`LBD-D7`): nothing serialised, no acceptance
check, `PRODUCTION_ACCEPTANCE` untouched. The configuration is `LBD-AM4-3`'s, which is the
ceiling probe's §4 bridge-arm configuration plus `require_fame=False`:

    BuilderConfig(algorithm=CANDIDATE_ALGORITHM,        # drop-list lineage, not the arm
                  require_fame=False,                   # LBD-D4
                  drop_unlistenable=True,               # LBD-AM4-3: measured inert on P
                  unlistenable_list_path=<20260809>)    # the re-censused payload, via override
    # every other knob at its BuilderConfig default — cap rule, top-j, ceiling, rescale

What is measured, per arm (`LBD-AM4-4`):

  * nodes, edges, max/mean degree; largest-component retention against P's 88,685;
  * `LBD-M1` — nodes per fame band (five equal-count bands by `fame_lb` from the CXA
    artifact's own metadata, "unknown" where null), against P's band sizes; descriptive;
  * `LBD-C2b` inputs — degree of every artist in the added set (29,892), its LBD-AM1 residual
    stratum and complement, and the pre-existing set (58,793), with an absent artist counted
    as degree 0 exactly as the pre-registration's section 3 fixes. `set_stats` is IMPORTED
    from the ceiling probe so the statistic is the bridge control's own definition:
    `share_le_2` is over PRESENT artists, `share_le_2_or_absent` over the whole set — the
    latter is the pre-registered quantity;
  * every drop-stage count the builder logs (special-purpose, nameless, the three lists),
    so "the lists are inert on P" is observed in the build rather than assumed from the
    coverage probe;
  * the p99 rescale's log line.

Per-artist degrees for the pinned sets are written beside the results so `LBD-G2`'s paired
comparison can be computed between arms without rebuilding (`lbd_c2b_compare.py`).

Reads `builder/scratch/` by absolute path from the MAIN tree, opens the arm archive through a
`ReadOnlyArchive` whose `put()` raises (`GRT-A1`), and writes only its JSON (`LBD-D8`).

    cd <worktree>/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \\
      uv run python -u analysis/2026-09-10-lbd-supply/lbd_build_census.py \\
        --arm A0 --archive C:/unsung-fast/lbd-archives/A0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(REPO / "api" / "src"))
sys.path.insert(0, str(HERE.parent / "2026-09-07-degree-ceiling-falsifier"))

import artistpath_api.graph_store as gs  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.pipeline import build_from_archive  # noqa: E402
from dcf_ceiling_sweep import ReadOnlyArchive, hub_stats, set_stats  # noqa: E402  (imported, not copied)

from lbd_source import LbdBulkSource  # noqa: E402

SCRATCH = Path(r"C:\dev\music-app\builder\scratch")
CXA = SCRATCH / "graph-cxa-adopted.bin"
INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
PINNED = {
    "added": (INPUTS / "cxr_added_mbids.txt", "bfed95ef74b0665c50b1532708091b4e43fab36247db391d04064870659a4339"),
    "preexisting": (INPUTS / "cxr_preexisting_mbids.txt", "768054b7e84769346193336ec7e9b3496af92d0d3e8d4ae2fb287057912b5229"),
    "residual": (INPUTS / "cxr_residual_mbids.txt", "fa8d85cc12131f3cd39ecebeb5da0d52a1236104acbcbabf20232c72b4f43a08"),
}
ULF_20260809 = REPO / "builder" / "src" / "artistpath_builder" / "data" / "unlistenable_drop_algb_20260809.json"
BANDS = 5


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pinned(name: str) -> list[str]:
    path, sha = PINNED[name]
    actual = sha256_of(path)
    if actual != sha:
        raise SystemExit(f"REFUSING: {path.name} sha256 {actual} != pinned {sha}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def population_and_bands() -> tuple[list[str], dict[str, str], str]:
    """P from the artifact, and each member's fame band from the artifact's own metadata.

    The blob is located exactly as `graph_store.py` locates it (the `lbd_c1_sample.py`
    precedent), and the shipped parser's node order is checked against it.
    """
    manifest = json.loads(CXA.with_suffix(".bin.json").read_text(encoding="utf-8"))
    payload = CXA.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != manifest["sha256"]:
        raise SystemExit(f"REFUSING: {CXA.name} sha256 {digest} != sidecar {manifest['sha256']}")
    store = gs.GraphStore.load(CXA)
    magic, version, n, e, meta_len = gs._HEADER.unpack_from(payload)
    cursor = gs._HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor : cursor + meta_len])
    if list(meta["mbids"]) != list(store.mbids):
        raise SystemExit("REFUSING: metadata mbids disagree with the shipped parser")
    fame = meta.get("fame_lb") or [None] * n
    # Five equal-count bands over the non-null values, sorted (fame, mbid) so ties are
    # deterministic; band 0 the least-listened, band 4 the most; "unknown" for nulls.
    known = sorted((f, m) for m, f in zip(store.mbids, fame) if f is not None)
    band_of: dict[str, str] = {m: "unknown" for m, f in zip(store.mbids, fame) if f is None}
    per = len(known) // BANDS
    for i, (_f, m) in enumerate(known):
        band_of[m] = str(min(i // per, BANDS - 1))
    return sorted(store.mbids), band_of, digest


class LogCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(record.getMessage())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=("A0", "A2"))
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    out = args.out or (HERE / f"lbd_build_{args.arm}.json")

    manifest_path = args.archive / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["arm"] != f"LBD-{args.arm}":
        raise SystemExit(f"REFUSING: {manifest_path} is {manifest['arm']}, not LBD-{args.arm}")
    print(f"[build] arm {args.arm}  archive {args.archive}  MANIFEST sha256 {sha256_of(manifest_path)}", flush=True)

    population, band_of, cxa_sha = population_and_bands()
    if manifest["population"]["artifact_sha256"] != cxa_sha:
        raise SystemExit("REFUSING: the archive was emitted over a different population artifact")
    added = load_pinned("added")
    pre = load_pinned("preexisting")
    residual = set(load_pinned("residual"))
    if not residual <= set(added):
        raise SystemExit("REFUSING: residual set is not a subset of the added set")
    pset = set(population)
    if not (set(added) | set(pre)) == pset or len(added) + len(pre) != len(pset):
        raise SystemExit("REFUSING: added + pre-existing does not partition P")
    print(f"[build] P {len(population):,} = added {len(added):,} (residual {len(residual):,}) + pre-existing {len(pre):,}", flush=True)

    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        require_fame=False,
        drop_unlistenable=True,
        unlistenable_list_path=ULF_20260809,
    )
    source = LbdBulkSource(config)
    archive = ReadOnlyArchive(LocalArchive(args.archive))

    capture = LogCapture()
    logging.getLogger("artistpath_builder").addHandler(capture)
    logging.getLogger("artistpath_builder").setLevel(logging.INFO)
    started = time.monotonic()
    graph = build_from_archive(config, archive, source)
    elapsed = time.monotonic() - started
    logging.getLogger("artistpath_builder").removeHandler(capture)
    for line in capture.lines:
        print(f"  builder: {line}", flush=True)

    degrees = np.diff(graph.offsets).astype(np.int64)
    degrees_by_mbid = {m: int(degrees[i]) for i, m in enumerate(graph.mbids)}
    nodes = set(graph.mbids)
    if not nodes <= pset:
        raise SystemExit(f"BUG: {len(nodes - pset)} built nodes are outside P")

    whole = hub_stats(degrees, graph.mbids)
    complement = [m for m in added if m not in residual]
    result = {
        "arm": f"LBD-{args.arm}",
        "amendment": "LBD-AM4 — fixed population P; bridge-arm drop-list configuration; require_fame=False",
        "archive": {"root": str(args.archive), "manifest_sha256": sha256_of(manifest_path),
                    "payloads": manifest["counts"]["payloads_written"],
                    "neighbour_rows": manifest["counts"]["neighbour_rows_written"],
                    "P_absent_from_arm": manifest["counts"]["P_absent_from_arm"]},
        "population": {"artifact": CXA.name, "sha256": cxa_sha, "count": len(population)},
        "config": {
            "algorithm": config.algorithm, "cap_strategy": config.cap_strategy,
            "union_top_j": config.union_top_j, "union_degree_ceiling": config.union_degree_ceiling,
            "similarity_rescale": config.similarity_rescale, "similarity_damping": config.similarity_damping,
            "filter_special_purpose": config.filter_special_purpose,
            "drop_no_release_tail": config.drop_no_release_tail, "drop_featured_credit": config.drop_featured_credit,
            "drop_unlistenable": config.drop_unlistenable, "unlistenable_list_path": ULF_20260809.name,
            "require_fame": config.require_fame,
        },
        "elapsed_seconds": round(elapsed, 1),
        "builder_log": capture.lines,
        "whole_graph": whole,
        "largest_component_retention_vs_P": round(len(nodes) / len(population), 5),
        "ceiling_binds": whole["max_degree"] >= config.union_degree_ceiling,
        "bound_holds": whole["max_degree"] <= config.union_degree_ceiling,
        "sets": {
            "added": set_stats(degrees_by_mbid, added),
            "residual": set_stats(degrees_by_mbid, [m for m in added if m in residual]),
            "complement": set_stats(degrees_by_mbid, complement),
            "preexisting": set_stats(degrees_by_mbid, pre),
        },
        "M1_nodes_by_fame_band": {},
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    for band in [str(b) for b in range(BANDS)] + ["unknown"]:
        in_p = [m for m in population if band_of[m] == band]
        built = sum(1 for m in in_p if m in nodes)
        result["M1_nodes_by_fame_band"][band] = {
            "P": len(in_p), "built": built, "share_retained": round(built / len(in_p), 5) if in_p else None,
        }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    out.with_suffix(".degrees.json").write_text(json.dumps({
        "added": {m: degrees_by_mbid.get(m, 0) for m in added},
        "preexisting": {m: degrees_by_mbid.get(m, 0) for m in pre},
    }), encoding="utf-8")
    s = result["sets"]
    print(f"[build] {args.arm}: nodes {whole['nodes']:,}  edges {whole['edges']:,}  max deg {whole['max_degree']}  "
          f"retention {result['largest_component_retention_vs_P']:.4f}  ({elapsed / 60:.1f} min)", flush=True)
    for name in ("added", "residual", "complement", "preexisting"):
        r = s[name]
        print(f"  {name:<12} n {r['n']:>6,}  median {r.get('median_degree', float('nan')):>5}  "
              f"<=2|absent {r['share_le_2_or_absent']:.4f}  <=2 present {r.get('share_le_2', float('nan')):.4f}  "
              f"=1 {r.get('share_eq_1', float('nan')):.4f}  absent {r['share_absent']:.4f}", flush=True)
    print(f"[build] wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
