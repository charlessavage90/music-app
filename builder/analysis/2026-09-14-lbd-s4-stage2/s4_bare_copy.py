"""A BARE re-serialisation of an artifact that carries additive metadata keys — so that all nine
arms' BOOT MEMORY is measured on the same kind of object.

WHY THIS EXISTS. `LBA-AM1`'s finding `LBA-AM1-A12` corrected `LBA-M1`'s **bytes** definition for
exactly one reason: **no census build of `LBA-A1` or `LBA-A3` was ever serialised.** Their only
artifacts (`LBD-A0V.bin`, `LBD-A5V.bin`) were built for a listen and carry the additive keys, so
comparing their on-disk size against seven fame-free census builds would compare seven arms against
two that are larger for a reason that is not the arm. A12 solved that for bytes by DECODING.

**The same defect exists one row down, in boot memory, and decoding does not solve it there.**
`LBA-G1`(a) is *the census build's measured median peak x `metadata_ratio`, plus `framework_rss`*.
For the two reused arms there is no census build to load, and loading their fame-carrying artifacts
instead would then multiply by `metadata_ratio` a figure that ALREADY CONTAINS metadata — inflating
the two CONTROL arms' projected resident cost and making them look like the worst cells in the
lattice. That is a visible, decision-relevant error in the arms the design uses as its baseline.

**What this script does, and what it is careful not to be.** It DECODES the artifact, empties the
five additive lists, and RE-SERIALISES. It does not rebuild: no archive is read, no `BuilderConfig`
is applied, `build_from_archive` is never called. `LBA-D9` forbids REBUILDING `LBA-A1` and
`LBA-A3` — because a rebuild would introduce a build-date column the factor table does not have —
and a re-serialisation of an already-decoded graph introduces no such column. The CSR arrays, the
node order, the scores and `popularity` are the committed build's own bytes, unchanged.

**It is checked rather than asserted:** the bare copy's own bare-artifact size must equal the size
computed by decoding the ORIGINAL, which is `LBA-M1`'s definition arrived at by a second route.

    uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_bare_copy.py \
      --artifact C:/unsung-fast/lbd-artifacts/LBD-A0V.bin --label LBA-A1
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))

import numpy as np  # noqa: E402

from artistpath_builder.artifact import deserialise, serialise  # noqa: E402

from s4_common import bare_size_of_artifact, bare_size_of_graph, sha256_of  # noqa: E402

ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
ADDITIVE = ("deezer_ids", "fame_lb_raw", "spotify_ids", "apple_ids", "artist_facts")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", type=Path, required=True)
    ap.add_argument("--label", required=True)
    args = ap.parse_args(argv)

    original = bare_size_of_artifact(args.artifact)
    graph = deserialise(args.artifact.read_bytes())
    stripped = dataclasses.replace(graph, **{k: [] for k in ADDITIVE})
    payload = serialise(stripped)
    out = ARTIFACTS / f"{args.label}-bare.bin"
    out.write_bytes(payload)

    check = bare_size_of_artifact(out)
    if check["additive_keys_present"]:
        raise SystemExit(f"BUG: the bare copy still carries {check['additive_keys_present']}")
    if check["bare_artifact_bytes"] != original["bare_artifact_bytes"] != len(payload):
        raise SystemExit(f"BUG: bare sizes disagree — decoded original {original['bare_artifact_bytes']}, "
                         f"bare copy {check['bare_artifact_bytes']}, bytes written {len(payload)}")
    # The map itself must not have moved: this is a re-serialisation, not a rebuild.
    round_trip = deserialise(payload)
    for field in ("mbids", "names", "disambiguations", "pop_raw"):
        if list(getattr(round_trip, field)) != list(getattr(graph, field)):
            raise SystemExit(f"BUG: {field} moved in the bare copy")
    for field in ("offsets", "neighbours", "scores", "edge_types"):
        if not np.array_equal(np.asarray(getattr(round_trip, field)), np.asarray(getattr(graph, field))):
            raise SystemExit(f"BUG: {field} moved in the bare copy")

    record = {
        "label": args.label,
        "source_artifact": str(args.artifact),
        "source_sha256": sha256_of(args.artifact),
        "source_additive_keys": original["additive_keys_present"],
        "source_serialised_bytes": original["serialised_bytes_on_disk"],
        "bare_artifact": str(out),
        "bare_sha256": sha256_of(out),
        "bare_bytes": len(payload),
        "bare_size_matches_decoded_original": True,
        "structure_identical_to_source": True,
        "method": "decode, empty the five additive lists, re-serialise — NOT a rebuild: no archive "
                  "is read and build_from_archive is never called, so no build-date column is "
                  "introduced and LBA-D9's prohibition is untouched",
        "why": "LBA-G1(a) multiplies a census build's peak by metadata_ratio; loading a "
               "fame-carrying artifact instead would scale a figure that already contains metadata",
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha256_of(Path(__file__)),
    }
    (HERE / f"s4_bare_copy_{args.label}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"[bare] {args.label}: {args.artifact.name} ({original['serialised_bytes_on_disk'] / 1e6:.1f} MB, "
          f"keys {original['additive_keys_present']}) -> {out.name} ({len(payload) / 1e6:.1f} MB, no keys)",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
