"""`DCF-` — the falsifier Q4 named and did not run.

`builder/analysis/2026-09-06-lbd-plan-review/measurement-derivation.md` Q4
attributes most of the `CXR` added set's sparsity to OUR `union_degree_ceiling`
of 50 rather than to ListenBrainz's lists, and names the falsifier verbatim:

    "a build of the extended archive with `union_degree_ceiling` raised,
     showing the added set's share-<=2 stays near 34%."

This runs it. One archive (the EXTENDED ALG-B tree, the one
`graph-cxa-adopted.bin` was built from), one knob (`union_degree_ceiling`),
several values, every other `BuilderConfig` knob at its shipped default except
the two experimental controls named below. Each arm's isolating baseline is the
`ceiling=50` control, which differs from it in exactly one column.

SCOPE, and it is narrow on purpose
  This is a STRUCTURAL probe over graphs built in memory. It measures degree.
  It does NOT route: no path is built, no `CRS-C4` hub transit is computed, no
  routing criterion of any pre-registration is evaluated, and nothing here
  adopts or proposes anything. The cap-rule decision is parked and the owner's
  (`specs/2026-09-06-own-similarity-design.md` §9).

THIS KNOB IS NOT NEW AND THIS PROBE MUST NOT PRESENT IT AS NEW
  Track B swept it. `TUw-50-100` is this exact rule at ceiling 100, isolated
  against `TUw-50-50` by the ceiling alone, scored on both archives against a
  committed pre-registration — and it FIRED `CRS-C4`'s material hub-transit bar
  on the broad famous class. Figures:
  `docs/superpowers/findings/2026-07-30-track-b-cap-selection-results.md`
  and its raw `cb_scores.json`. Cited there, never restated here.

  The gap this probe covers, and the only one: both Track B sweeps predate the
  crawl extension, so neither archive's graphs contained the ~29,900 added
  artists, and no criterion in either pre-registration measures that set's
  degree or its dead-end share. That set is the whole subject here.

TWO DELIBERATE DEPARTURES FROM A SHIPPING CONFIG, held constant across arms
  require_fame=False       the ALG-B fame tree is framed on a smaller
                           population; `load_fame` refuses rather than
                           defaulting (MSW-G3), and fame is read by no figure
                           here.
  drop_unlistenable=False  the shipped guard REFUSES on a population the ULF-
                           census never evaluated (ULC-F1); the error message
                           names this flag as "an experimental control and
                           never a shipping configuration".
  Consequence, stated so it is not read past: these arms are NOT byte-comparable
  to `graph-cxa-adopted.bin`, which was built with both True. The within-build
  pre-existing set is the reference, never the committed artifact's figures.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-07-degree-ceiling-falsifier/dcf_ceiling_sweep.py \
        --ceilings 50 100 200 20000
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import statistics
import sys
import time
from pathlib import Path

import numpy as np

from artistpath_builder.archive import LocalArchive, RawArchive
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"

# The EXTENDED ALG-B tree — 117,302 payloads, the one graph-cxa-adopted.bin was
# built from. NOT the `.pre-cex-snapshot` sibling: NEXT.md pins that one for any
# build of the SERVED lineage, and the added artists this probe is about exist
# only in the extended tree. Reading the wrong one would measure nothing.
ARCHIVE = SCRATCH / "grt-archive-algb"

# The two committed artifacts that DEFINE the added / pre-existing split. Read
# through the shipped GraphStore (cxr_census.py precedent) and sha-verified
# against their own manifest sidecars first: artifacts under scratch/ are
# gitignored and not interchangeable, so the sidecar is their only identity.
OLD = SCRATCH / "graph-msw-tu50.bin"  # the served map, 58,838 artists
NEW = SCRATCH / "graph-cxa-adopted.bin"  # the extended map, 88,685 artists


class ArchiveWriteRefused(RuntimeError):
    """Something tried to write into a read-only archive."""


class ReadOnlyArchive:
    """Wraps an archive and refuses every write (GRT-A1).

    Standing condition on every analysis harness that opens a real archive: the
    production archive is irreplaceable and the ALG-B crawl cost 7.6 hours. This
    harness only ever reads, so `put()` firing is a bug here, never a finding.
    """

    def __init__(self, inner: RawArchive) -> None:
        self._inner = inner

    def put(self, key: str, payload: bytes) -> None:
        raise ArchiveWriteRefused(
            f"the DCF- ceiling sweep tried to write {key!r}. It is read-only by "
            "design; do not relax this guard."
        )

    def get(self, key: str):
        return self._inner.get(key)

    def has(self, key: str) -> bool:
        return self._inner.has(key)

    def keys(self):
        return self._inner.keys()


def verify_against_sidecar(path: Path) -> dict:
    """Refuse to read an artifact whose bytes disagree with its own manifest."""
    sidecar = path.with_suffix(".bin.json")
    if not sidecar.is_file():
        raise FileNotFoundError(f"no manifest sidecar beside {path.name}")
    manifest = json.loads(sidecar.read_text(encoding="utf-8"))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest.get("sha256"):
        raise ValueError(
            f"{path.name} sha256 {digest[:12]}… does not match its sidecar's "
            f"{str(manifest.get('sha256'))[:12]}…. Artifacts under scratch/ are "
            "not interchangeable; do not proceed."
        )
    logger.info(
        "verified %s  sha %s…  artists %s  edges %s",
        path.name, digest[:12], manifest.get("artists"), manifest.get("edges"),
    )
    return manifest


def population_split() -> tuple[list[str], list[str], dict]:
    """The `CXR` added / pre-existing split, from the two committed artifacts.

    Parsed by the SHIPPED GraphStore rather than a second parser here, which is
    the cxr_census.py precedent and the reason its figures can be compared.
    """
    sys.path.insert(0, str(HERE.parent.parent.parent / "api" / "src"))
    from artistpath_api.graph_store import GraphStore  # noqa: PLC0415

    old_manifest = verify_against_sidecar(OLD)
    new_manifest = verify_against_sidecar(NEW)

    old = GraphStore.load(OLD)
    new = GraphStore.load(NEW)
    old_set = set(old.mbids)
    added = [m for m in new.mbids if m not in old_set]
    pre_existing = [m for m in new.mbids if m in old_set]

    identity = {
        "old": {"file": OLD.name, "sha256": old_manifest["sha256"],
                "artists": len(old.mbids)},
        "new": {"file": NEW.name, "sha256": new_manifest["sha256"],
                "artists": len(new.mbids)},
        "added": len(added),
        "pre_existing": len(pre_existing),
    }
    logger.info("split: added %d, pre-existing %d", len(added), len(pre_existing))
    return added, pre_existing, identity


def set_stats(degrees_by_mbid: dict[str, int], mbids: list[str]) -> dict:
    """Degree figures for one MBID set inside one build.

    `share_absent` is the half a degree distribution cannot express: an artist
    the build dropped entirely (a drop list, or the largest-component prune) has
    no degree at all, and counting only the present ones would flatter every arm
    that strands more of them.
    """
    present = [degrees_by_mbid[m] for m in mbids if m in degrees_by_mbid]
    absent = len(mbids) - len(present)
    if not present:
        return {"n": len(mbids), "n_present": 0, "share_absent": 1.0}
    arr = np.asarray(present, dtype=np.int64)
    return {
        "n": len(mbids),
        "n_present": len(present),
        "share_absent": round(absent / len(mbids), 5),
        "median_degree": float(statistics.median(present)),
        "mean_degree": round(float(arr.mean()), 3),
        "p10_degree": int(np.percentile(arr, 10)),
        "p90_degree": int(np.percentile(arr, 90)),
        "max_degree": int(arr.max()),
        # The dead-end share: an artist with <= 2 connections can rarely be an
        # interior card, and one with exactly 1 never can, because a journey
        # enters and leaves every artist in the middle (CXR-M5).
        "share_le_2": round(float(np.mean(arr <= 2)), 5),
        "share_eq_1": round(float(np.mean(arr == 1)), 5),
        # Counted over the WHOLE set, absent artists included, so the two
        # denominators cannot be mixed up downstream.
        "share_le_2_or_absent": round((int(np.sum(arr <= 2)) + absent) / len(mbids), 5),
    }


def hub_stats(degrees: np.ndarray, mbids: list[str]) -> dict:
    """The cost side: `CRS-C3`'s concentration measure, same definition.

    `top1pct_degree_mass_frac` is lifted from
    `builder/analysis/2026-07-30-track-b-cap-selection/cb_metrics.py` unchanged
    — share of all edge ENDPOINTS held by the top 1% of nodes BY DEGREE. Degree,
    never fame and never popularity (§2.6).

    ⚠ Track B's own weakest-link applies here too: on a cell where thousands of
    nodes sit AT the ceiling, membership of the "own top 1% by degree" set is
    arbitrary among tied degrees. That is the control arm exactly. The mass
    figure is stable; the membership is not.
    """
    total = int(degrees.sum())
    cut = max(1, int(round(len(degrees) * 0.01)))
    top = np.argsort(-degrees, kind="stable")[:cut]
    at_ceiling_ties = int(np.sum(degrees == degrees[top].min()))
    return {
        "nodes": len(degrees),
        "edges": total // 2,
        "mean_degree": round(float(degrees.mean()), 3),
        "median_degree": float(np.median(degrees)),
        "p99_degree": int(np.percentile(degrees, 99)),
        "max_degree": int(degrees.max()),
        "top1pct_degree_mass_frac": round(float(degrees[top].sum()) / total, 5),
        "top1pct_cut_size": cut,
        "nodes_tied_at_the_top1pct_boundary_degree": at_ceiling_ties,
    }


def run_arm(ceiling: int, added: list[str], pre_existing: list[str]) -> dict:
    """Build one arm through the SHIPPED build_from_archive and measure it."""
    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,  # ALG-B — the extended archive's lineage
        union_degree_ceiling=ceiling,  # THE ONE COLUMN THAT VARIES
        require_fame=False,
        drop_unlistenable=False,
    )
    source = ListenBrainzSource(config)
    archive = ReadOnlyArchive(LocalArchive(ARCHIVE))

    started = time.monotonic()
    graph = build_from_archive(config, archive, source)
    elapsed = time.monotonic() - started

    degrees = np.diff(graph.offsets).astype(np.int64)
    degrees_by_mbid = {m: int(degrees[i]) for i, m in enumerate(graph.mbids)}

    arm = {
        "union_degree_ceiling": ceiling,
        "is_control": ceiling == 50,
        "elapsed_seconds": round(elapsed, 1),
        "config": {
            "algorithm": config.algorithm,
            "cap_strategy": config.cap_strategy,
            "union_top_j": config.union_top_j,
            "union_degree_ceiling": config.union_degree_ceiling,
            "similarity_rescale": config.similarity_rescale,
            "similarity_damping": config.similarity_damping,
            "filter_special_purpose": config.filter_special_purpose,
            "drop_no_release_tail": config.drop_no_release_tail,
            "drop_featured_credit": config.drop_featured_credit,
            "drop_unlistenable": config.drop_unlistenable,
            "require_fame": config.require_fame,
        },
        "whole_graph": hub_stats(degrees, graph.mbids),
        "added": set_stats(degrees_by_mbid, added),
        "pre_existing": set_stats(degrees_by_mbid, pre_existing),
    }
    # Does the ceiling still bind at this value, or has the top-j union become
    # the operative bound? An arm where it no longer binds is the upper bound on
    # what ANY ceiling change could deliver, and must be reported as such.
    arm["ceiling_binds"] = arm["whole_graph"]["max_degree"] >= ceiling
    arm["bound_holds"] = arm["whole_graph"]["max_degree"] <= ceiling
    print(
        f"  ceiling {ceiling:>6}  built in {elapsed / 60:.1f} min  "
        f"nodes {arm['whole_graph']['nodes']:,}  edges {arm['whole_graph']['edges']:,}  "
        f"max deg {arm['whole_graph']['max_degree']:,}  "
        f"ADDED median {arm['added']['median_degree']:.0f} "
        f"<=2 {100 * arm['added']['share_le_2']:.2f}% "
        f"absent {100 * arm['added']['share_absent']:.2f}%",
        flush=True,
    )
    return arm


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ceilings", type=int, nargs="+", default=[50, 100, 200, 20_000],
        help="union_degree_ceiling values to build; 50 is the shipped control",
    )
    parser.add_argument("--out", default=str(HERE / "dcf_results.json"))
    args = parser.parse_args()

    if 50 not in args.ceilings:
        raise SystemExit(
            "refusing to run without the ceiling=50 control: every raised arm's "
            "isolating baseline is the shipped ceiling on the SAME archive, and "
            "without it no arm differs by exactly one column."
        )

    added, pre_existing, identity = population_split()
    out = Path(args.out)

    results = {
        "probe": "DCF- — does raising union_degree_ceiling move the CXR added "
                 "set's dead-end share?",
        "archive": {
            "dir": str(ARCHIVE),
            "payloads": sum(
                1 for k in LocalArchive(ARCHIVE).keys()
                if k.startswith(f"similar/listenbrainz/{CANDIDATE_ALGORITHM}/")
                and k.endswith(".json")
            ),
        },
        "artifacts": identity,
        "arms": [],
    }
    print(f"archive payloads: {results['archive']['payloads']:,}", flush=True)

    # Sequential and re-read per arm: build_from_archive has no seam to inject a
    # cap step into, so each arm pays the full parse. Results are flushed after
    # every arm so a long run that dies late still yields what it finished.
    for ceiling in args.ceilings:
        print(f"\n=== arm: union_degree_ceiling={ceiling} ===", flush=True)
        results["arms"].append(run_arm(ceiling, added, pre_existing))
        out.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")

    # --- instrument gate, both halves -----------------------------------
    # A green result from an instrument never shown to go red is not evidence.
    by_ceiling = {a["union_degree_ceiling"]: a for a in results["arms"]}
    control = by_ceiling[50]
    green = control["bound_holds"]  # CRS-G2's check: the rule's stated bound
    raised = [a for c, a in by_ceiling.items() if c > 50]
    red = bool(raised) and all(a["whole_graph"]["max_degree"] > 50 for a in raised)
    results["gate"] = {
        "green_control_bound_holds": green,
        "green_note": "control max degree <= 50, the rule's stated bound (CRS-G2)",
        "red_knob_is_wired": red,
        "red_note": "every raised arm exceeds degree 50, so the ceiling really "
                    "reached trimmed_union_cap and the instrument can move",
        "passed": green and red,
    }
    out.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(f"\ngate: green={green} red={red} -> {'PASS' if green and red else 'FAIL'}")
    print(f"wrote {out}")
    return 0 if (green and red) else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
