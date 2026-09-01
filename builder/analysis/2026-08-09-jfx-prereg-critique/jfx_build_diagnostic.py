"""Build the `JFX-B` diagnostic artifact: acceptance REJECTS, and we serialise anyway.

**Governing document:** `docs/superpowers/specs/2026-08-09-journey-fame-exposure-preregistration.md`
§1, as amended by `JFX-AM1.12` — which exists because §1 described this script in the
present tense before it had been written.

**What this is for.** `graph-cex-117k.bin` does not exist: `cmd_build` runs
`check_acceptance` before `serialise`, and the extended population is rejected on both
bounds (artists 88,685 against [47,000, 71,000]; edges 1,618,164 against
[1,050,000, 1,580,000]). That rejection is the DESIGNED outcome of `CEX-` Task 11 and an
owner stop. `JFX-` needs the artifact anyway, to measure what a person would get if the
bounds were widened.

**So this mirrors `cmd_build`'s build-and-emit SEQUENCE — config, `build_from_archive`,
`check_acceptance`, `serialise`, write, manifest — differing in one step: it catches
`ArtifactRejected`, records the rejection VERBATIM in the manifest, and serialises anyway.**

It is **not** a drop-in replacement for `cmd_build` and does not try to be: it builds its
`BuilderConfig` directly from three explicit inputs rather than going through `cli._config`,
so `--target`, `--cap-strategy` and the S3 archive options are **not** available here. That
is deliberate — this script exists to emit one specific artifact, and every knob it does not
expose is a knob that cannot silently differ from the pre-registered arm.

- **The gate is not modified and the bounds are not widened.** `check_acceptance` and
  `PRODUCTION_ACCEPTANCE` are imported and called unchanged. Widening them is an adoption
  decision and is the owner's (`MSW-G3` is the precedent, and there too it was his).
- **The artifact is byte-identical to one `cmd_build` would emit after a bounds change**
  (determinism, spec §9 — demonstrated 2026-08-09 when the snapshot rebuild reproduced the
  adopted artifact exactly). So if `JFX-` supports adoption, THIS artifact ships; no rebuild.
- **The manifest is stamped so it can never be mistaken for a passing build.**

**⚠ `--algorithm` IS REQUIRED, deliberately (`CEXR-2`).** `BuilderConfig.algorithm` defaults
to **ALG-E**, while the adopted map's lineage is **ALG-B**; there is no `RC-H3` guard on the
build side, so a defaulted build reads the wrong population, may pass acceptance, and
describes a population nobody asked for. This script refuses rather than defaulting.

Usage:

    cd builder && UV_LINK_MODE=copy PYTHONUNBUFFERED=1 uv run python \\
      analysis/2026-08-09-jfx-prereg-critique/jfx_build_diagnostic.py \\
      --archive-dir scratch/grt-archive-algb \\
      --algorithm alg-b \\
      --unlistenable-list <censused ULF- payload for the extended population> \\
      --out scratch/graph-cex-117k.bin
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "builder/src"))

from artistpath_builder.acceptance import (  # noqa: E402
    PRODUCTION_ACCEPTANCE,
    ArtifactRejected,
    check_acceptance,
)
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.artifact import serialise  # noqa: E402
from artistpath_builder.config import (  # noqa: E402
    CANDIDATE_ALGORITHM,
    PRODUCTION_ALGORITHM,
    BuilderConfig,
)
from artistpath_builder.manifest import build_manifest, write_manifest  # noqa: E402
from artistpath_builder.pipeline import build_from_archive  # noqa: E402
from artistpath_builder.sources.listenbrainz import ListenBrainzSource  # noqa: E402

ALGORITHMS = {"alg-b": CANDIDATE_ALGORITHM, "alg-e": PRODUCTION_ALGORITHM}


def _within_repo(raw: str, what: str) -> Path:
    """Resolve a CLI path and confine it to the repository tree.

    The operator supplies these paths themselves, so this is not a trust
    boundary in the usual sense — but a mistyped `../..` on `--out` would
    write a 400 MB artifact somewhere unexpected, and a build takes ~17
    minutes to discover that. Confining to the tree makes the typo fail in
    milliseconds instead. Also clears the Snyk CWE-23 finding on this file.
    """
    resolved = Path(raw).expanduser().resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        raise SystemExit(
            f"{what}: refusing a path outside the repository tree.\n"
            f"  given:    {raw}\n  resolved: {resolved}\n  tree:     {ROOT}"
        ) from None
    return resolved


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument(
        "--algorithm",
        required=True,
        choices=sorted(ALGORITHMS),
        help="REQUIRED (CEXR-2). BuilderConfig defaults to ALG-E; the adopted "
        "map's lineage is ALG-B. Nothing downstream catches a defaulted build.",
    )
    p.add_argument(
        "--unlistenable-list",
        required=True,
        help="REQUIRED. The censused ULF- payload for THIS population. Per "
        "SEL-, it is a per-invocation override and never a shipped default.",
    )
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    out = _within_repo(args.out, "--out")
    if out.exists():
        raise SystemExit(
            f"REFUSING: {out} already exists. Builds are deterministic, so an "
            "existing artifact is either identical (nothing to do) or from a "
            "different input (and overwriting it destroys the only copy)."
        )
    payload_list = _within_repo(args.unlistenable_list, "--unlistenable-list")
    if not payload_list.is_file():
        raise SystemExit(f"--unlistenable-list: no such file: {payload_list}")
    archive_dir = _within_repo(args.archive_dir, "--archive-dir")
    if not archive_dir.is_dir():
        raise SystemExit(f"--archive-dir: no such directory: {archive_dir}")

    config = BuilderConfig(
        algorithm=ALGORITHMS[args.algorithm],
        unlistenable_list_path=payload_list,
        # MSW- Task 9's third plan defect: without this the build emits a
        # FAMELESS artifact and exits 0. JFX scores on fame; a fameless
        # artifact would route without the ramp and read as a flat gradient.
        require_fame=True,
    )

    started = time.monotonic()
    graph = build_from_archive(
        config, LocalArchive(archive_dir), ListenBrainzSource(config)
    )

    # The ONE difference from cmd_build. The gate runs unchanged; only our
    # response to it differs. A rejection is expected here and is not an error.
    rejection: str | None = None
    try:
        check_acceptance(graph, PRODUCTION_ACCEPTANCE)
    except ArtifactRejected as exc:
        rejection = str(exc)
        logging.warning(
            "acceptance REJECTED this graph, as designed. Serialising anyway "
            "for JFX- measurement. Verbatim reason recorded in the manifest."
        )
        for line in rejection.splitlines():
            logging.warning("  rejected: %s", line)

    payload = serialise(graph)
    elapsed = time.monotonic() - started
    out.write_bytes(payload)

    manifest = build_manifest(graph, config, payload, elapsed)
    manifest["acceptance"] = {
        "passed": rejection is None,
        "criteria": "PRODUCTION_ACCEPTANCE (unmodified — bounds NOT widened)",
        "rejection_verbatim": rejection,
        "why_serialised_anyway": (
            "JFX- diagnostic artifact, per the JFX- pre-registration §1 and "
            "JFX-AM1.12. Acceptance was run unchanged and its verdict is "
            "recorded above. Adoption requires the owner to widen the bounds; "
            "this artifact is byte-identical to a post-widening rebuild."
        ),
        "DO_NOT_DEPLOY": rejection is not None,
    }
    write_manifest(out, manifest)

    logging.info(
        "wrote %s: %d artists, %d edges, %.1f MB, %.0fs — acceptance %s",
        out,
        graph.artist_count,
        graph.edge_count,
        len(payload) / 1e6,
        elapsed,
        "PASSED" if rejection is None else "REJECTED (recorded, not suppressed)",
    )
    if rejection is not None:
        print("\n" + "=" * 72)
        print("ACCEPTANCE REJECTED — this artifact MUST NOT be deployed as-is.")
        print("The rejection is the designed outcome and is in the manifest.")
        print("=" * 72)
        print(rejection)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
