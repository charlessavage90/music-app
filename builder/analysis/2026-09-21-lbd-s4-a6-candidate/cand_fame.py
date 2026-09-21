"""`LBA-` §8 item 1, part one — run the `fame` stage over `P` for the `LBA-A6` candidate.

THE ONE THING THIS SCRIPT EXISTS TO GET RIGHT: it must not touch stage 2's archive.
`C:\\unsung-fast\\lbd-archives\\S4-A6` is a pinned instrument input behind committed stage-2 and
stage-3 results. The shipped `fame` stage writes `fame/<mbid>.json` INTO the archive it is given,
so pointing it at `S4-A6` would mutate a pinned artifact and silently invalidate every figure
those two stages recorded. Instead the records go into a SEPARATE directory and the build composes
the two read-only, which is `lbv_build.py`'s `FameOverlayArchive` pattern (`LBD-AM5-4`), reused
rather than reinvented.

`S4-A6`'s `MANIFEST.json` sha256 is asserted BEFORE and AFTER, and the archive is additionally
opened through `ReadOnlyArchive` (`GRT-A1`) so any write attempt raises rather than lands.

The mbid set is `archive_artists(...)`, exactly what the shipped `cmd_fame` uses — a superset of
the built node set by construction, which is the property `load_fame` needs so it cannot come up
short at build time. §6 step 7. `LBA-M5` part 2 estimated this arm at 88 batches.

    cd C:/dev/music-app/builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-21-lbd-s4-a6-candidate/cand_fame.py
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))
sys.path.insert(0, str(HERE.parent / "2026-09-07-degree-ceiling-falsifier"))
sys.path.insert(0, str(HERE.parent / "2026-09-10-lbd-supply"))

from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_builder.fame import fetch_fame, lb_fame_fetcher  # noqa: E402
from artistpath_builder.pipeline import archive_artists  # noqa: E402
from dcf_ceiling_sweep import ReadOnlyArchive  # noqa: E402  (imported, not copied)
from lbd_source import LbdBulkSource  # noqa: E402

ARCHIVE = Path(r"C:\unsung-fast\lbd-archives\S4-A6")
FAME_DIR = Path(r"C:\unsung-fast\lbd-archives\S4-A6-fame")
DATA = REPO / "builder" / "src" / "artistpath_builder" / "data"
OUT = HERE / "cand_fame.json"

# From stage 2's own record, `s4_build_A6.json` -> archive.manifest_sha256. Never re-derived here.
ARCHIVE_MANIFEST_SHA = "950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3"
# `LBA-D7`: the P payload, and no other. The owner named it as a hard bar.
DROP_LIST = "unlistenable_drop_algb_20260809.json"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if OUT.exists():
        raise SystemExit(f"REFUSING: {OUT.name} already exists — one fame pass per candidate")

    manifest_path = ARCHIVE / "MANIFEST.json"
    before = sha256_of(manifest_path)
    if before != ARCHIVE_MANIFEST_SHA:
        raise SystemExit(
            f"REFUSING: {manifest_path} sha256 {before} != stage 2's pinned {ARCHIVE_MANIFEST_SHA}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("lba_arm") != "LBA-A6":
        raise SystemExit(f"REFUSING: {manifest_path} is not LBA-A6")
    params = manifest["parameters"]
    if (params["threshold"], params["limit"]) != (3, 100):
        raise SystemExit(f"REFUSING: the archive's tokens are not LBA-A6's: {params}")
    if manifest["population"]["count"] != 88685:
        raise SystemExit("REFUSING: the archive's population count is not P's")
    print(f"[fame] S4-A6 archive verified against stage 2's pin: {before[:16]}…", flush=True)
    print(f"[fame] arm LBA-A6  threshold {params['threshold']}  limit {params['limit']}  "
          f"population P ({manifest['population']['count']:,})", flush=True)

    config = BuilderConfig(
        algorithm=CANDIDATE_ALGORITHM,
        require_fame=False,          # irrelevant to the fetch; the build sets it True
        drop_unlistenable=True,
        unlistenable_list_path=DATA / DROP_LIST,
    )
    source = LbdBulkSource(config)

    arm_archive = ReadOnlyArchive(LocalArchive(ARCHIVE))
    mbids = sorted(archive_artists(arm_archive, config, source))
    print(f"[fame] {len(mbids):,} artists with an archived similarity response "
          f"(a superset of the built node set, by construction)", flush=True)

    FAME_DIR.mkdir(parents=True, exist_ok=True)
    fame_archive = LocalArchive(FAME_DIR)   # the ONLY writable handle in this script

    started = time.monotonic()
    report = fetch_fame(
        fame_archive, mbids, lb_fame_fetcher(config),
        pause_seconds=config.request_delay_seconds,
    )
    elapsed = time.monotonic() - started
    print(f"[fame] {report.fetched:,} fetched ({report.nulls:,} null), "
          f"{report.skipped:,} already recorded, {report.total:,} total, {elapsed:.0f}s", flush=True)
    if report.total != len(mbids):
        raise SystemExit(
            f"REFUSING: fame covered {report.total} of {len(mbids)} — a partial pass is not a pass"
        )

    after = sha256_of(manifest_path)
    if after != before:
        raise SystemExit("BUG: stage 2's archive manifest changed during the fame pass")
    print(f"[fame] S4-A6 archive manifest UNCHANGED: {after[:16]}…", flush=True)

    OUT.write_text(json.dumps({
        "task": "LBA- §8 item 1 — the fame stage over P for the LBA-A6 candidate",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "arm": "LBA-A6",
        "population_rule": "P",
        "plain_sentence": "every artist the deeper crawl found, at the two-listener bar",
        "source_archive": {
            "root": str(ARCHIVE),
            "manifest_sha256_before": before,
            "manifest_sha256_after": after,
            "unchanged": True,
            "opened": "ReadOnlyArchive (GRT-A1) — every write raises",
        },
        "fame_archive": {
            "root": str(FAME_DIR),
            "why_separate": "the shipped fame stage writes into the archive it is given; S4-A6 is "
                            "a pinned instrument input behind committed stage-2 and stage-3 "
                            "results, so the records go beside it and the build composes the two "
                            "read-only (FameOverlayArchive, LBD-AM5-4's pattern)",
        },
        "mbid_set": {
            "n": len(mbids),
            "rule": "archive_artists(...) — exactly what the shipped cmd_fame uses; a superset of "
                    "the built node set so load_fame cannot come up short",
        },
        "report": {
            "fetched": report.fetched, "nulls": report.nulls,
            "skipped": report.skipped, "total": report.total,
            "elapsed_s": round(elapsed, 1),
        },
        "drop_list": DROP_LIST,
        "script_sha256": sha256_of(Path(__file__)),
    }, indent=2), encoding="utf-8")
    print(f"[fame] wrote {OUT.name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
