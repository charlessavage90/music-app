"""The fame fetch stage (`MSW-`, Task 3).

The instrument is the one adopted by `FAM-`: ListenBrainz
`POST /1/popularity/artist` -> `total_user_count`, stored as `fame_lb_raw`.

Two properties carry most of the weight here.

**A null is a RESULT, not a gap.** ListenBrainz returns not-found artists with
counts set to null rather than omitting them, so a null means "measured, and
nobody has listened" — maximal obscurity under the novelty-likelihood
construct, never a missing measurement (`FAM-` §1, `FAM-AM1`.8). If resume
treated a stored null as unfetched, every null would be re-fetched on every
run forever, and the stage would never terminate against a population with
any real absences in it.

**The network lives here and nowhere downstream.** `build` reads these records
off the archive, exactly as it reads similarity responses, so the offline-build
rule (spec §9, proved by the replay test's raising fetcher) survives the
addition of a network-sourced quantity.
"""

import hashlib
import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.fame import (
    MissingFameError,
    fame_key,
    fetch_fame,
    load_fame,
    seed_fame,
)

A, B, C = ("a" * 36, "b" * 36, "c" * 36)


def _record(archive, mbid):
    return json.loads(archive.get(fame_key(mbid)))


def test_fetch_writes_one_record_per_mbid(tmp_path):
    archive = LocalArchive(tmp_path)

    def fetcher(batch):
        return {m: 7 for m in batch}

    report = fetch_fame(archive, [A, B], fetcher, batch_size=50, today="2026-08-05")
    assert report.fetched == 2
    assert report.skipped == 0
    assert _record(archive, A) == {"fame_lb_raw": 7, "fetched": "2026-08-05"}


def test_a_null_is_stored_as_a_measured_absence(tmp_path):
    archive = LocalArchive(tmp_path)

    def fetcher(batch):
        return {m: None for m in batch}

    fetch_fame(archive, [A], fetcher, batch_size=50, today="2026-08-05")
    assert _record(archive, A)["fame_lb_raw"] is None
    assert archive.has(fame_key(A)), "a null must occupy its key, or resume loops"


def test_resume_skips_existing_records_including_nulls(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put(fame_key(A), b'{"fame_lb_raw": null, "fetched": "2026-08-02"}')
    seen = []

    def fetcher(batch):
        seen.extend(batch)
        return {m: 1 for m in batch}

    report = fetch_fame(archive, [A, B], fetcher, batch_size=50, today="2026-08-05")
    assert seen == [B], "a stored null must not be re-fetched"
    assert report.fetched == 1
    assert report.skipped == 1
    # and the pre-existing record is untouched, keeping its own fetch date
    assert _record(archive, A) == {"fame_lb_raw": None, "fetched": "2026-08-02"}


def test_an_mbid_the_server_omits_is_recorded_as_null(tmp_path):
    # Defensive: the documented contract is that nulls come back explicitly,
    # but a silently truncated batch must not leave a hole that the next run
    # reads as "never asked". Absent from the response == null, recorded.
    archive = LocalArchive(tmp_path)

    def fetcher(batch):
        return {batch[0]: 5}  # B omitted entirely

    fetch_fame(archive, [A, B], fetcher, batch_size=50, today="2026-08-05")
    assert _record(archive, B)["fame_lb_raw"] is None


def test_fetch_batches_at_the_configured_size(tmp_path):
    archive = LocalArchive(tmp_path)
    sizes = []

    def fetcher(batch):
        sizes.append(len(batch))
        return {m: 1 for m in batch}

    mbids = [f"{i:04d}" + "d" * 32 for i in range(25)]
    fetch_fame(archive, mbids, fetcher, batch_size=10, today="2026-08-05")
    assert sizes == [10, 10, 5]


def test_fetch_requests_in_sorted_order(tmp_path):
    archive = LocalArchive(tmp_path)
    seen = []

    def fetcher(batch):
        seen.extend(batch)
        return {m: 1 for m in batch}

    fetch_fame(archive, [C, A, B], fetcher, batch_size=50, today="2026-08-05")
    assert seen == [A, B, C]


def test_load_fame_returns_values_by_mbid(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put(fame_key(A), b'{"fame_lb_raw": 12, "fetched": "2026-08-05"}')
    archive.put(fame_key(B), b'{"fame_lb_raw": null, "fetched": "2026-08-05"}')
    assert load_fame(archive, [A, B]) == {A: 12, B: None}


def test_load_fame_raises_naming_what_is_missing(tmp_path):
    archive = LocalArchive(tmp_path)
    archive.put(fame_key(A), b'{"fame_lb_raw": 3, "fetched": "2026-08-05"}')
    with pytest.raises(MissingFameError) as excinfo:
        load_fame(archive, [A, B, C])
    message = str(excinfo.value)
    assert "2" in message, "the count of missing artists"
    assert B in message and C in message


def test_seed_imports_a_verified_snapshot(tmp_path):
    archive = LocalArchive(tmp_path / "archive")
    snapshot = tmp_path / "snap.json"
    snapshot.write_text(json.dumps({A: 12, B: None}))
    report = seed_fame(
        archive,
        snapshot,
        expected_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        fetched="2026-08-02",
    )
    assert report.seeded == 2
    assert _record(archive, A) == {"fame_lb_raw": 12, "fetched": "2026-08-02"}
    assert archive.has(fame_key(B))


def test_seed_refuses_a_snapshot_whose_sha_does_not_match(tmp_path):
    # The snapshot IS the instrument's identity (FAM-AM1.7): the adopted object
    # is the dated file plus its sha256. Importing an unverified one would put
    # values of unknown provenance into an artifact that routes on them.
    archive = LocalArchive(tmp_path / "archive")
    snapshot = tmp_path / "snap.json"
    snapshot.write_text(json.dumps({A: 12}))
    with pytest.raises(ValueError, match="sha256"):
        seed_fame(archive, snapshot, expected_sha256="0" * 64, fetched="2026-08-02")
    assert not archive.has(fame_key(A)), "nothing may be written before verifying"


def test_seed_does_not_overwrite_a_fresher_record(tmp_path):
    archive = LocalArchive(tmp_path / "archive")
    archive.put(fame_key(A), b'{"fame_lb_raw": 99, "fetched": "2026-08-05"}')
    snapshot = tmp_path / "snap.json"
    snapshot.write_text(json.dumps({A: 12}))
    report = seed_fame(
        archive,
        snapshot,
        expected_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        fetched="2026-08-02",
    )
    assert _record(archive, A)["fame_lb_raw"] == 99
    assert report.seeded == 0
    assert report.skipped == 1
