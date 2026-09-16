"""`LBA-` stage 3 -- shared loading, pinning and banding for `LBA-M2`..`LBA-M5`.

Holds only what more than one measurement needs, so that no measurement script re-derives a
population, a band or a digest its neighbour already has. Nothing here computes a statistic.

Four things it owns.

  * THE ARM TABLE. Eight sized arms, each with its BARE artifact, its population rule, its
    threshold and its archive root. `LBA-A9` is absent by construction: `LBA-G2` fired, the cell
    is unbuilt, and section 2.6 bars every map-level read of it. A caller asking for it gets a
    KeyError rather than a silent empty arm.
  * ARTIFACT LOADING THROUGH THE SHIPPED PARSER. `GraphStore` from `api/src`, never a local
    re-implementation -- the APG1 format is the contract between the packages and a second
    parser here would be a third copy of it. Every load re-checks the file's sha256 against
    task 4's `_pins/stage3_verify_artifacts.json` and REFUSES on a mismatch, so no statistic can
    be computed from an artifact this stage has not pinned.
  * THE FAME BANDS, by the `LBD-M1` precedent (`../2026-09-10-lbd-supply/lbd_build_census.py`),
    applied to the SERVED artifact: five equal-count bands over the non-null `fame_lb` values,
    sorted `(fame, mbid)` so ties are deterministic; band 0 the least-listened, band 4 the most;
    "unknown" for nulls. Read from the artifact's own metadata blob, located exactly as
    `graph_store.py` locates it, with the shipped parser's node order asserted against it.
    `LBA-X7`: this ruler exists only for artists the SERVED map contains, so no by-band figure
    can say anything about the artists an arm adds.
  * TABLE MEMBERSHIP PER ARM -- the set of MBIDs the arm's archive holds a payload for, which is
    what separates section 4's two absent causes ("no pair at all in the arm's table" from
    "pruned with the largest component"). Taken by scanning the archive rather than from any
    recorded count, and cross-checked against the archive manifest's own `payloads_written`;
    a disagreement REFUSES.

UNITS, because three edge units are live in this track: everything here is in NODES and in
NEIGHBOUR-LIST ENTRIES read out of a built artifact. Archive neighbour rows (pre-cap, two per
pair) belong to `LBA-G2` and appear nowhere in this module.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE1 = HERE.parent / "2026-09-14-lbd-s4-stage1"
STAGE2 = HERE.parent / "2026-09-14-lbd-s4-stage2"
REPO = HERE.parent.parent.parent

ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
ARCHIVES = Path(r"C:\unsung-fast\lbd-archives")
INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")

SERVED = REPO / "builder" / "scratch" / "graph-msw-tu50.bin"
SERVED_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
CXA = REPO / "builder" / "scratch" / "graph-cxa-adopted.bin"
CXA_SHA = "bc0431c4b55a2137e945b280270de7e7dc700e3dcf60f3656f6f97598e7ece46"

POP_V = ARCHIVES / "population_msw_mbids.txt"
POP_P = ARCHIVES / "population_cxa_mbids.txt"
CXR_ADDED = INPUTS / "cxr_added_mbids.txt"
CXR_PREEXISTING = INPUTS / "cxr_preexisting_mbids.txt"
CXR_RESIDUAL = INPUTS / "cxr_residual_mbids.txt"

BANDS = 5

sys.path.insert(0, str(REPO / "api" / "src"))
from artistpath_api import graph_store as gs  # noqa: E402

# arm -> (population rule, threshold, distinct listeners, archive root, filter column).
# The filter column is `LBA-D7`'s: SAID, never inferred from a config dump, because
# "on, inert" and "off, uncensused" look identical in one and mean opposite things (section 2.4).
ARMS: dict[str, dict] = {
    "LBA-A1": dict(rule="V", threshold=10, listeners=4, archive="A0V",
                   filter="on, inert (20260805)", reused="LBD-A0V.bin"),
    "LBA-A2": dict(rule="V", threshold=7, listeners=3, archive="S4-A2",
                   filter="on, inert (20260805)", reused=None),
    "LBA-A3": dict(rule="V", threshold=3, listeners=2, archive="A5V",
                   filter="on, inert (20260805)", reused="LBD-A5V.bin"),
    "LBA-A4": dict(rule="P", threshold=10, listeners=4, archive="S4-A4",
                   filter="on, inert (20260809)", reused=None),
    "LBA-A5": dict(rule="P", threshold=7, listeners=3, archive="S4-A5",
                   filter="on, inert (20260809)", reused=None),
    "LBA-A6": dict(rule="P", threshold=3, listeners=2, archive="S4-A6",
                   filter="on, inert (20260809)", reused=None),
    "LBA-A7": dict(rule="U", threshold=10, listeners=4, archive="S4-A7",
                   filter="off, uncensused", reused=None),
    "LBA-A8": dict(rule="U", threshold=7, listeners=3, archive="S4-A8",
                   filter="off, uncensused", reused=None),
}

# Section 2.2, fixed before any result existed and quoted verbatim wherever an arm is named.
SENTENCE: dict[str, str] = {
    "LBA-A1": "the artists the app serves today, connected by our own recomputation at the same "
              "strength bar ListenBrainz used",
    "LBA-A2": "the same artists, but a connection is kept when three different people's "
              "listening supports it instead of four",
    "LBA-A3": "the same artists, but two people are enough",
    "LBA-A4": "every artist the deeper crawl found, at ListenBrainz's own bar",
    "LBA-A5": "every artist the deeper crawl found, at the three-listener bar",
    "LBA-A6": "every artist the deeper crawl found, at the two-listener bar",
    "LBA-A7": "every artist anywhere in ListenBrainz's listening data who gets a connection at "
              "ListenBrainz's own bar - not just the ones our crawl happened to discover",
    "LBA-A8": "the same, at the three-listener bar",
    "LBA-A9": "the same, at the two-listener bar",
}

# Population rows. The arm-to-arm `LBA-M2` comparison (`LBA-AM1-A7`) runs WITHIN a row, so both
# sides share a population and an emitter and the population cause and the `LBA-X4` data bundle
# are absent from it by construction. `LBA-A9` is not in the `U` row here: it is unbuilt.
ROWS: dict[str, list[str]] = {"V": ["LBA-A1", "LBA-A2", "LBA-A3"],
                              "P": ["LBA-A4", "LBA-A5", "LBA-A6"],
                              "U": ["LBA-A7", "LBA-A8"]}


def sha256_of(path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        while chunk := fh.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def _pinned_bare() -> dict:
    """arm -> (bare artifact path, its pinned sha256), from task 4's own output."""
    pins = json.loads((HERE / "_pins" / "stage3_verify_artifacts.json").read_text("utf-8"))
    out = {}
    for row in pins["rows"]:
        label = row.get("label", "")
        # The bare copies, and ONLY those. The six built artifacts sit in the same file under
        # `LBA-<arm>.bin`; selecting on the `-bare.bin` suffix is what keeps the two families
        # apart here, which is the same separation task 1 had to make explicit.
        if label.endswith("-bare.bin") and row.get("status") == "OK":
            out[label[: -len("-bare.bin")]] = (Path(row["path"]), row["sha256"])
    if set(out) != set(ARMS):
        raise SystemExit(f"REFUSING: pinned bare artifacts {sorted(out)} != arms {sorted(ARMS)}")
    return out


def load_arm(arm: str):
    """The arm's BARE artifact through the shipped `GraphStore`, sha re-checked at load.

    Bare, not built: a census build carries four of the five additive metadata keys and the two
    reused artifacts carry all five, so decoding the built files would read some arms through
    metadata others lack. Stage 2 section 3a made the same choice for the memory half and states
    why; this is that choice applied to the structural half.
    """
    path, pinned = _pinned_bare()[arm]
    actual = sha256_of(path)
    if actual != pinned:
        raise SystemExit(f"REFUSING: {path.name} sha256 {actual} != pinned {pinned}")
    return gs.GraphStore.load(path)


def load_served():
    actual = sha256_of(SERVED)
    if actual != SERVED_SHA:
        raise SystemExit(f"REFUSING: served map sha256 {actual} != pinned {SERVED_SHA}")
    return gs.GraphStore.load(SERVED)


def read_mbid_file(path) -> list:
    return [ln.strip() for ln in Path(path).read_text("utf-8").splitlines() if ln.strip()]


def metadata_blob(path, store) -> dict:
    """The artifact's raw metadata JSON, located exactly as `graph_store.py` locates it.

    The shipped parser's node order is asserted against the blob, which is the `LBD-M1`
    precedent's own guard: it is what makes reading a key the parser does not expose
    (`fame_lb` raw counts) safe rather than a second parser.
    """
    payload = Path(path).read_bytes()
    _magic, _version, n, e, meta_len = gs._HEADER.unpack_from(payload)
    cursor = gs._HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor: cursor + meta_len])
    if list(meta["mbids"]) != list(store.mbids):
        raise SystemExit(f"REFUSING: {Path(path).name} metadata mbids disagree with the parser")
    return meta


def served_fame_bands(store) -> dict:
    """mbid -> band, five equal-count bands over the SERVED artifact's non-null `fame_lb`.

    The `LBD-M1` precedent verbatim. `LBA-X7`: this ruler reaches only artists the served map
    contains, so a by-band figure says nothing about the artists an arm ADDS.
    """
    meta = metadata_blob(SERVED, store)
    fame = meta.get("fame_lb") or [None] * len(store.mbids)
    known = sorted((f, m) for m, f in zip(store.mbids, fame) if f is not None)
    band_of = {m: "unknown" for m, f in zip(store.mbids, fame) if f is None}
    per = len(known) // BANDS
    for i, (_f, m) in enumerate(known):
        band_of[m] = str(min(i // per, BANDS - 1))
    return band_of


def table_mbids(arm: str) -> set:
    """MBIDs the arm's archive holds a payload for -- i.e. present in the arm's own table.

    Scanned, not read off a recorded count, then cross-checked against the archive manifest's
    `payloads_written`. A disagreement REFUSES: it would mean the archive on disk is not the one
    stage 2 measured, and every absent-cause split below would be computed from the wrong set.
    """
    root = ARCHIVES / ARMS[arm]["archive"]
    manifest = json.loads((root / "MANIFEST.json").read_text("utf-8"))
    prefix = root / manifest["archive_prefix"].replace("/", os.sep)
    got = {e.name[:-5] for e in os.scandir(prefix) if e.name.endswith(".json")}
    expected = manifest["counts"]["payloads_written"]
    if len(got) != expected:
        raise SystemExit(f"REFUSING: {arm} archive holds {len(got):,} payloads, "
                         f"manifest says {expected:,}")
    return got


def no_identity_row_mbids(arm: str) -> set:
    """Population members the emitter skipped for having no identity row.

    A third absent cause, small (single figures) and NOT one of section 4's two. Separated so
    that neither of the two it does name is contaminated by it: these artists have pairs in the
    table, so filing them under "no pair at all" would be false.
    """
    root = ARCHIVES / ARMS[arm]["archive"]
    manifest = json.loads((root / "MANIFEST.json").read_text("utf-8"))
    return set(manifest.get("P_with_no_identity_row_mbids") or [])


def write_json(path, payload: dict, script) -> None:
    payload = dict(payload)
    payload["script"] = Path(script).name
    payload["script_sha256"] = sha256_of(script)
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
