"""`LBA-` §8 items 1-2 — build the `LBA-A6` CANDIDATE with fame and clip/streaming ids, prove it
is structurally identical to stage 2's build, and check it against `PRODUCTION_ACCEPTANCE`.

THIS IS THE FIRST BUILD IN THE WHOLE TRACK THAT IS A CANDIDATE FOR SERVING. Every build before it
pinned `require_fame=False` and was an experimental control (`LBD-D7`, `LBA-D5`).

IT NEVER WIDENS AN ACCEPTANCE BOUND. §8 item 2 reserves recalibration to the owner — his ruling of
2026-09-05 (`LUX-4`) makes moving a bound so a NEW artifact can be adopted risk acceptance and
therefore his — and a candidate at any population above `V` breaches the node bound BY
CONSTRUCTION. Run bare, it reports exactly which bounds fail and by how much, and stops.

`--serialise` (§8 item 3) refuses without `--acceptance-ruling`, and refuses again if the shipped
`check_acceptance` still rejects the build: **the owner's ruling covers recalibrating the bounds
in `acceptance.py`, never bypassing the check here.** The two guards are separate on purpose — the
first asks whether he decided, the second asks whether the decision was actually implemented.
`ARTISTPATH_GRAPH_SHA256` is READ BACK from the written sidecar and verified against the file on
disk, never carried from a variable and never transcribed (`DEP-24`), and the artifact is reloaded
through the shipped `GraphStore` the way the api will (§6 step 10).

THE STRUCTURAL PROOF, and it is a single sha256 rather than a list of assertions. The candidate is
re-serialised with its five additive metadata lists emptied and the bytes compared to
`LBA-A6-bare.bin`, which stage 2 produced from its own build by exactly that method
(`s4_bare_copy.py`). Byte equality there proves node ORDER and all four CSR arrays
(`offsets`, `neighbours`, `scores`, `edge_types`) plus names, disambiguations and `pop_raw` are
identical — one comparison covering everything `fame` and the id maps must not have moved. The
field-by-field comparison against stage 2's `LBA-A6.bin` is run as well, because a sha tells you
THAT something moved and never WHICH.

Fame comes from the separate directory `cand_fame.py` filled; stage 2's archive is opened
read-only and its manifest sha256 asserted before and after (`GRT-A1`).

    cd C:/dev/music-app/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-21-lbd-s4-a6-candidate/cand_build.py
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

from artistpath_builder.acceptance import (  # noqa: E402
    PRODUCTION_ACCEPTANCE,
    ArtifactRejected,
    _famous_order,
    check_acceptance,
)
import artistpath_api.graph_store as gs  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.artifact import deserialise, serialise  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.manifest import build_manifest, write_manifest  # noqa: E402
from artistpath_builder.pipeline import build_from_archive  # noqa: E402
from dcf_ceiling_sweep import ArchiveWriteRefused, ReadOnlyArchive  # noqa: E402
from lbd_source import LbdBulkSource  # noqa: E402

ARCHIVE = Path(r"C:\unsung-fast\lbd-archives\S4-A6")
FAME_DIR = Path(r"C:\unsung-fast\lbd-archives\S4-A6-fame")
ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
DATA = REPO / "builder" / "src" / "artistpath_builder" / "data"
OUT = HERE / "cand_build.json"

STAGE2_ARTIFACT = ARTIFACTS / "LBA-A6.bin"
STAGE2_BARE = ARTIFACTS / "LBA-A6-bare.bin"
# The candidate itself. A NEW name: stage 2's LBA-A6.bin is a pinned input and is never touched.
ARTIFACT = ARTIFACTS / "LBA-A6-candidate.bin"
# All three from stage 2's own records; never re-derived here.
ARCHIVE_MANIFEST_SHA = "950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3"
STAGE2_ARTIFACT_SHA = "199b9e20a2fea4d998043bca83ed2f10a3696f84f3e5399f960834770f8f290e"
STAGE2_BARE_SHA = "f35cb19d935d53a184173d006791334b42b0b64ee9b7593b1c3ab1029b7c8d6d"

DROP_LIST = "unlistenable_drop_algb_20260809.json"
ADDITIVE = ("deezer_ids", "fame_lb_raw", "spotify_ids", "apple_ids", "artist_facts")
# `LBD-D6` / `LBA-D1`: recorded, not inferred from the config.
PAIRING = {
    "form": "ListenBrainz's own — once per PAIR OF PLAYS within a session",
    "why": "LBA-D1, the owner's ruling of 2026-09-14: it is the only form with any listening "
           "evidence behind it, and both LBL- blind listens were run on maps derived that way, so "
           "a listen-based judgment transfers to this arm and to no other. The cheaper "
           "session-collapsed form is barred for S4 unless it gets its own blind listen.",
    "bar": "LBD-X6 stands. Its condition was discharged 2026-09-13 and R10 FIRED, which confirmed "
           "the bar rather than lifting it. Nothing here licenses a sentence about the cheaper form.",
    "derived_from": "T (sha256 03d47b05…), never T_A4",
}


class FameOverlayArchive:
    """Similarity responses from the arm's archive; `fame/` records from the fame directory.

    `lbv_build.py`'s pattern (`LBD-AM5-4`), which composed the same two halves for `LBD-A0V` and
    `LBD-A5V`. Never writes: both halves arrive wrapped in `ReadOnlyArchive`, and this refuses too
    so the composition cannot become the hole in the guard.
    """

    def __init__(self, similarity, fame) -> None:
        self._similarity = similarity
        self._fame = fame

    def _pick(self, key: str):
        return self._fame if key.startswith("fame/") else self._similarity

    def put(self, key: str, payload: bytes) -> None:
        raise ArchiveWriteRefused(f"cand_build tried to write {key!r}; both halves are read-only")

    def get(self, key: str):
        return self._pick(key).get(key)

    def has(self, key: str) -> bool:
        return self._pick(key).has(key)

    def keys(self):
        yield from self._similarity.keys()
        yield from self._fame.keys()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class LogCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.lines: list[str] = []

    def emit(self, record) -> None:
        self.lines.append(record.getMessage())


def acceptance_report(graph) -> dict:
    """Run `PRODUCTION_ACCEPTANCE` and record EVERY check it applies, passing or failing.

    NO BOUND IS WIDENED, NOR IS ONE PROPOSED. §8 item 2 makes recalibration the owner's.

    ⚠ THE ROW LIST MIRRORS `check_acceptance` CHECK FOR CHECK, and an earlier version of this
    function did not: it tabulated the four bounds its author expected to matter and silently
    omitted the global `median_degree` band, which then failed. The shipped check's own output
    said so and the table did not. A hand-written list of "the bounds that matter" is the same
    defect class as a stale restated figure — so every criterion field is covered here, and
    `criteria_fields_covered` is asserted against the dataclass at the end.
    """
    c = PRODUCTION_ACCEPTANCE
    degrees = np.diff(graph.offsets).astype(np.int64)
    n, e = len(graph.mbids), int(graph.offsets[-1])
    rows = []

    def row(name, measured, lo, hi, unit="", kind="band"):
        ok = (lo is None or measured >= lo) and (hi is None or measured <= hi)
        if ok:
            margin = "—"
        elif lo is not None and measured < lo:
            margin = f"{lo - measured:,.0f} below the floor ({measured / lo * 100:.1f}% of it)"
        else:
            margin = f"{measured - hi:,.0f} above the ceiling ({measured / hi * 100:.1f}% of it)"
        rows.append({"bound": name, "measured": measured, "floor": lo, "ceiling": hi,
                     "unit": unit, "kind": kind, "passes": ok, "margin_if_failed": margin})

    # group 1 — the §2.8 failure-signature detectors. A defect's SHAPE, not a population's size.
    order = _famous_order(graph)[: c.famous_sample]
    famous = degrees[order]
    row("famous median degree", float(statistics.median(famous.tolist())),
        c.famous_median_degree_floor, None, "degree", "detector")
    row("famous min degree", int(famous.min()), c.famous_min_degree_floor, None,
        "degree", "detector")
    blank = sum(1 for name in graph.names if not name.strip())
    row("artists with no name", blank, None, 0, "artists", "detector")
    present = set(graph.names)
    absent = [x for x in c.canonical_names if x not in present]
    row("canonical artists absent from the largest component", len(absent), None, 0,
        "artists", "detector")

    # group 2 — global shape. REGRESSION TRIPWIRES, not detectors: acceptance.py is explicit that
    # the §2.8 defect does not move these, and that they catch a build silently losing the graph.
    row("node count", n, c.node_count[0], c.node_count[1], "artists", "tripwire")
    row("edge count", e, c.edge_count[0], c.edge_count[1], "CSR entries", "tripwire")
    row("median degree", float(statistics.median(degrees.tolist())),
        c.median_degree[0], c.median_degree[1], "degree", "tripwire")

    try:
        check_acceptance(graph, c)
        raised, problems = False, []
    except ArtifactRejected as exc:
        raised, problems = True, str(exc).splitlines()

    covered = {"famous_sample", "famous_median_degree_floor", "famous_min_degree_floor",
               "canonical_names", "node_count", "edge_count", "median_degree"}
    declared = {f.name for f in dataclasses.fields(c)}
    if covered != declared:
        raise SystemExit(
            f"REFUSING: this report does not cover every acceptance criterion. "
            f"uncovered={declared - covered} unknown={covered - declared}"
        )

    failing = [r["bound"] for r in rows if not r["passes"]]
    # The shipped check is the authority; this table must not disagree with it.
    if raised != bool(failing):
        raise SystemExit(
            f"REFUSING: the table says failing={failing} but check_acceptance raised={raised}"
        )

    return {
        "criteria": "PRODUCTION_ACCEPTANCE, UNMODIFIED — no bound widened, none proposed",
        "criteria_fields_covered": sorted(covered),
        "raised_ArtifactRejected": raised,
        "problems_as_the_shipped_check_reports_them": problems,
        "bounds": rows,
        "failing": failing,
        "passing": [r["bound"] for r in rows if r["passes"]],
        "note": "§8 item 2: a candidate at any population above V breaches the node bound BY "
                "CONSTRUCTION. That breach is a decision, not a bug, and it is the owner's "
                "(his 2026-09-05 LUX-4 ruling). This script stops here.",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serialise", action="store_true",
                    help="write the artifact and its manifest sidecar — REFUSED without "
                         "--acceptance-ruling, which only the owner can supply")
    ap.add_argument("--acceptance-ruling", default=None,
                    help="the owner's recorded decision on the failing bounds, verbatim")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.serialise and not args.acceptance_ruling:
        raise SystemExit(
            "REFUSING: --serialise without --acceptance-ruling. A candidate above V fails "
            "PRODUCTION_ACCEPTANCE by construction; serialising anyway is risk acceptance and is "
            "the owner's call (§8 item 2, his LUX-4 ruling of 2026-09-05). Run without "
            "--serialise to get the failing bounds and their margins, and ask him."
        )

    # --- identities, before anything is read ---------------------------------------------------
    manifest_path = ARCHIVE / "MANIFEST.json"
    archive_before = sha256_of(manifest_path)
    if archive_before != ARCHIVE_MANIFEST_SHA:
        raise SystemExit(f"REFUSING: S4-A6 manifest {archive_before} != stage 2's pin")
    for path, expected, label in ((STAGE2_ARTIFACT, STAGE2_ARTIFACT_SHA, "LBA-A6.bin"),
                                  (STAGE2_BARE, STAGE2_BARE_SHA, "LBA-A6-bare.bin")):
        got = sha256_of(path)
        if got != expected:
            raise SystemExit(f"REFUSING: {label} sha256 {got} != stage 2's pinned {expected}")
    print(f"[cand] pins verified: S4-A6 manifest, LBA-A6.bin, LBA-A6-bare.bin", flush=True)

    # --- configuration: stage 2's, with require_fame flipped and NOTHING else ------------------
    base = dict(algorithm=CANDIDATE_ALGORITHM, drop_unlistenable=True,
                unlistenable_list_path=DATA / DROP_LIST)
    census_config = BuilderConfig(require_fame=False, **base)
    config = BuilderConfig(require_fame=True, **base)
    flipped = {f.name for f in dataclasses.fields(BuilderConfig)
               if getattr(config, f.name) != getattr(census_config, f.name)}
    if flipped != {"require_fame"}:
        raise SystemExit(f"REFUSING: the candidate differs from stage 2's config in {flipped}")
    print(f"[cand] config differs from stage 2's census build in exactly {flipped}", flush=True)

    source = LbdBulkSource(config)
    archive = FameOverlayArchive(ReadOnlyArchive(LocalArchive(ARCHIVE)),
                                 ReadOnlyArchive(LocalArchive(FAME_DIR)))

    # --- the build -----------------------------------------------------------------------------
    capture = LogCapture()
    log = logging.getLogger("artistpath_builder")
    log.addHandler(capture)
    log.setLevel(logging.INFO)
    started = time.monotonic()
    try:
        graph = build_from_archive(config, archive, source)
    finally:
        log.removeHandler(capture)
    elapsed = time.monotonic() - started
    for line in capture.lines:
        print(f"  builder: {line}", flush=True)
    n, e = len(graph.mbids), int(graph.offsets[-1])
    print(f"[cand] built: nodes {n:,}  CSR entries {e:,}  ({elapsed / 60:.1f} min)", flush=True)

    archive_after = sha256_of(manifest_path)
    if archive_after != archive_before:
        raise SystemExit("BUG: stage 2's archive manifest changed during the build")

    # --- the structural proof --------------------------------------------------------------------
    bare = dataclasses.replace(graph, **{k: [] for k in ADDITIVE})
    bare_bytes = serialise(bare)
    bare_sha = hashlib.sha256(bare_bytes).hexdigest()
    identical = bare_sha == STAGE2_BARE_SHA
    print(f"[cand] bare re-serialisation sha256 {bare_sha[:16]}…  "
          f"{'IDENTICAL to' if identical else 'DIFFERS FROM'} stage 2's LBA-A6-bare.bin", flush=True)

    # TWO CLASSES, and conflating them was a real risk once the id maps were re-extracted.
    #
    # STRUCTURAL fields ARE the map: node order, the four CSR arrays, names, disambiguations and
    # popularity. Attaching fame or ids must not move ANY of them, and the bare sha above already
    # proves it in one comparison — this loop exists to say WHICH, because a sha cannot.
    #
    # METADATA id fields are EXPECTED to differ from stage 2's artifact after the owner's
    # 2026-09-21 re-extraction, and an earlier version of this script refused on exactly that.
    # They are reported as a delta, never as a failure. The bare comparison is unaffected because
    # it empties all five additive lists before serialising — which is why it is the proof.
    stage2 = deserialise(STAGE2_ARTIFACT.read_bytes())
    STRUCTURAL_LISTS = ("mbids", "names", "disambiguations")
    STRUCTURAL_ARRAYS = ("offsets", "neighbours", "scores", "edge_types")
    METADATA_LISTS = ("deezer_ids", "spotify_ids", "apple_ids", "artist_facts")

    structural_checked, structural_differing = [], []
    for field in STRUCTURAL_LISTS:
        structural_checked.append(field)
        if list(getattr(graph, field)) != list(getattr(stage2, field)):
            structural_differing.append(field)
    for field in STRUCTURAL_ARRAYS:
        structural_checked.append(field)
        if not np.array_equal(np.asarray(getattr(graph, field)),
                              np.asarray(getattr(stage2, field))):
            structural_differing.append(field)
    structural_checked.append("pop_raw")
    if not np.array_equal(np.asarray(graph.pop_raw, dtype=np.float64),
                          np.asarray(stage2.pop_raw, dtype=np.float64)):
        structural_differing.append("pop_raw")

    metadata_delta = {}
    for field in METADATA_LISTS:
        before = sum(1 for v in getattr(stage2, field) if v)
        after = sum(1 for v in getattr(graph, field) if v)
        metadata_delta[field] = {"stage2_artifact": before, "candidate": after,
                                 "delta": after - before}

    print(f"[cand] STRUCTURAL vs stage 2's LBA-A6.bin: {len(structural_checked)} checked, "
          f"{len(structural_differing)} differing {structural_differing}", flush=True)
    for field, d in metadata_delta.items():
        print(f"[cand] metadata  {field:<14} {d['stage2_artifact']:>7,} -> {d['candidate']:>7,} "
              f"({d['delta']:+,})", flush=True)

    if not identical or structural_differing:
        raise SystemExit(
            "REFUSING: attaching fame and ids moved the MAP. Nothing downstream is trustworthy "
            f"if this fires. bare-identical={identical} structural_differing={structural_differing}"
        )

    fame_present = sum(1 for v in graph.fame_lb_raw if v is not None)
    ids = {k: sum(1 for v in getattr(graph, k) if v) for k in
           ("deezer_ids", "spotify_ids", "apple_ids", "artist_facts")}
    full_bytes = len(serialise(graph))
    print(f"[cand] fame present for {fame_present:,} of {n:,} nodes; "
          f"serialised {full_bytes / 1e6:.1f} MB (bare {len(bare_bytes) / 1e6:.1f} MB)", flush=True)

    acceptance = acceptance_report(graph)
    for r in acceptance["bounds"]:
        flag = "PASS" if r["passes"] else "FAIL"
        print(f"[cand] acceptance {flag}  {r['bound']:<24} measured {r['measured']:>12,.1f}  "
              f"floor {r['floor']}  ceiling {r['ceiling']}  {r['margin_if_failed']}", flush=True)

    # --- §8 item 3: serialise, manifest, sidecar, round-trip -----------------------------------
    serialised = None
    if args.serialise:
        if acceptance["raised_ArtifactRejected"]:
            raise SystemExit(
                "REFUSING to serialise: the shipped check still rejects this build.\n  "
                + "\n  ".join(acceptance["problems_as_the_shipped_check_reports_them"])
                + "\nThe owner's ruling covers RECALIBRATING the bounds, not bypassing the check. "
                  "Move the bounds in acceptance.py and re-run, or do not serialise."
            )
        payload = serialise(graph)
        ARTIFACT.write_bytes(payload)
        manifest = build_manifest(
            graph, config, payload, elapsed,
            build_inputs={
                "arm": "LBA-A6",
                "plain_sentence": "every artist the deeper crawl found, at the two-listener bar",
                "population_rule": "P",
                "threshold": 3,
                "pairing": PAIRING,
                "filter": "on, inert (20260809)",
                "drop_list": DROP_LIST,
                "similarity_archive": {"root": str(ARCHIVE),
                                       "manifest_sha256": archive_before},
                "fame_archive": {"root": str(FAME_DIR)},
                "structural_identity": {
                    "bare_sha256": bare_sha,
                    "identical_to": "stage 2's LBA-A6-bare.bin",
                },
                "acceptance": {
                    "criteria": "PRODUCTION_ACCEPTANCE as recalibrated 2026-09-21",
                    "owner_ruling": args.acceptance_ruling,
                },
                "governing_document":
                    "docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md §8, "
                    "with §11 LBA-AM4's LBA-G5 use gate between items 3 and 4",
            },
        )
        write_manifest(ARTIFACT, manifest)
        sidecar = ARTIFACT.with_suffix(ARTIFACT.suffix + ".json")

        # DEP-24: the checksum is READ BACK from the sidecar, never carried from the variable
        # above and never transcribed. If these two ever disagree the sidecar is what boots.
        recorded = json.loads(sidecar.read_text(encoding="utf-8"))["sha256"]
        on_disk = sha256_of(ARTIFACT)
        if recorded != on_disk:
            raise SystemExit(
                f"REFUSING: sidecar sha256 {recorded} != the file on disk {on_disk}"
            )

        # §6 step 10: reload through the SHIPPED GraphStore, the way the api will.
        store = gs.GraphStore.load(ARTIFACT)
        if list(store.mbids) != list(graph.mbids):
            raise SystemExit("REFUSING: the round-tripped artifact's node order is not the build's")
        if store.artist_count != n:
            raise SystemExit("REFUSING: the round-tripped artifact's artist count is not the build's")
        # `GraphStore` does not keep raw fame — it keeps `fame_lb_pctl`, the percentile
        # RANKING computed over the artifact's own population (`graph_store.fame_percentiles`).
        # Asserting that is the sharper check: it is the exact quantity `LBA-AM4` says this
        # candidate acquires at §8 item 1 and that no `LBA-` arm could measure, because every
        # arm built `require_fame=False`. If it is None here, the artifact carries no fame and
        # the use gate would be run against a map without the mechanism it exists to test.
        if store.fame_lb_pctl is None:
            raise SystemExit(
                "REFUSING: the round-tripped artifact carries no fame ranking. The candidate "
                "must carry fame_lb for LBA-G5 to be testing what LBA-AM4 says it tests."
            )
        if len(store.fame_lb_pctl) != n:
            raise SystemExit(
                f"REFUSING: fame_lb_pctl has {len(store.fame_lb_pctl)} entries for {n} nodes"
            )
        round_trip_fame = int(np.count_nonzero(~np.isnan(store.fame_lb_pctl)))

        serialised = {
            "artifact": str(ARTIFACT),
            "sidecar": str(sidecar),
            "bytes": len(payload),
            "sha256_from_sidecar": recorded,
            "sha256_verified_against_file": on_disk == recorded,
            "round_trip": {
                "loaded_through": "the shipped api GraphStore",
                "artists": store.artist_count,
                "node_order_matches_build": True,
                "fame_ranking_present": True,
                "nodes_with_a_fame_percentile": round_trip_fame,
                "note": "equals N by design and is NOT the measured count: graph_store.fame_percentiles gives a measured NULL 0.0 — genuine maximal obscurity under the novelty construct — while EXCLUDING it from the frame, so no NaN survives. The measured count is fame.nodes_with_a_measured_count above.",
            },
            "owner_ruling": args.acceptance_ruling,
        }
        print(f"[cand] serialised {len(payload) / 1e6:.1f} MB -> {ARTIFACT.name}", flush=True)
        print(f"[cand] sidecar written; sha256 READ BACK from it: {recorded}", flush=True)
        print(f"[cand] round-trip through the shipped GraphStore: {store.artist_count:,} artists, "
              f"{round_trip_fame:,} fame records", flush=True)

    OUT.write_text(json.dumps({
        "task": "LBA- §8 items 1-2 — the LBA-A6 candidate build with fame and clip/streaming ids",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "arm": "LBA-A6",
        "plain_sentence": "every artist the deeper crawl found, at the two-listener bar",
        "population_rule": "P",
        "threshold": 3,
        "pairing": PAIRING,
        "filter": "on, inert (20260809)",
        "drop_list": DROP_LIST,
        "config_delta_from_stage2": sorted(flipped),
        "source_archive": {"root": str(ARCHIVE), "manifest_sha256_before": archive_before,
                           "manifest_sha256_after": archive_after, "unchanged": True},
        "fame_archive": {"root": str(FAME_DIR)},
        "built": {"nodes": n, "csr_entries": e, "wall_clock_s": round(elapsed, 1),
                  "serialised_bytes": full_bytes, "bare_serialised_bytes": len(bare_bytes)},
        "structural_identity": {
            "bare_sha256": bare_sha,
            "stage2_bare_sha256": STAGE2_BARE_SHA,
            "byte_identical": identical,
            "method": "re-serialise the candidate with its five additive lists emptied and compare "
                      "to LBA-A6-bare.bin, which stage 2 produced from its own build by exactly "
                      "that method (s4_bare_copy.py). Covers node ORDER and all four CSR arrays "
                      "plus names, disambiguations and pop_raw in one comparison.",
            "structural_fields_checked_against_stage2_artifact": structural_checked,
            "structural_fields_differing": structural_differing,
            "metadata_id_delta_vs_stage2_artifact": metadata_delta,
            "why_metadata_may_differ": "the owner's 2026-09-21 re-extraction repointed the three "
                                       "id/fact maps at new dated package data. Those lists are "
                                       "EXPECTED to differ from stage 2's artifact; the bare "
                                       "comparison empties all five before serialising, which is "
                                       "why it remains the structural proof.",
        },
        "fame": {"nodes_with_a_measured_count": fame_present, "nodes": n,
                 "nulls": n - fame_present,
                 "note": "a null is a MEASURED ABSENCE and is never a floor value (FAM-AM1.8)"},
        "id_coverage": ids,
        "acceptance": acceptance,
        "serialised": serialised,
        "script_sha256": sha256_of(Path(__file__)),
    }, indent=2), encoding="utf-8")
    print(f"[cand] wrote {OUT.name}", flush=True)
    if serialised is None:
        print("[cand] STOPPING before serialisation — the failing bounds are the owner's ruling.",
              flush=True)
    else:
        print(f"[cand] §8 items 1-3 complete. ARTISTPATH_GRAPH_SHA256 is in "
              f"{Path(serialised['sidecar']).name}; do not transcribe it (DEP-24).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
