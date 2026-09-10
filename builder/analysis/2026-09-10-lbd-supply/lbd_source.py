"""`LBD-D3` — the bulk source: a SECOND `SimilaritySource` with its own `name`, never fetched.

`build_from_archive` reads `similar/<source.name>/<config.algorithm>/<mbid>.json`
(`pipeline.py:similar_prefix`) and parses each payload with the source's `parse`. Because this
class is a `ListenBrainzSource` with `name = "lbd"`, the builder reads the `similar/lbd/…`
sub-tree the emitter wrote, with `parse`, `edge_type` and `harvest_identities` unchanged —
nothing in `build` is touched, which is what `LBD-D3` requires.

It is deliberately NOT a seventh `PERMITTED_ALGORITHMS` value: that enum documents what the
Labs endpoint accepts, and a bulk token would falsify the comment above it (design §3).

THE ALGORITHM TOKEN NAMES THE DROP-LIST LINEAGE, NOT THE ARM'S PARAMETERS (plan Task 6). Every
arm's `BuilderConfig` uses `CANDIDATE_ALGORITHM` — the `ALG-B` string, `filter_True` included —
because the three drop-list loaders key on `config.algorithm` and raise on an unknown token.
The arm's real parameters (threshold, limit) live in the archive root's `MANIFEST.json`, and
each arm has its own archive root, so nothing collides under one prefix. Do not "fix" the
token to describe the arm; that breaks every drop list.
"""

from __future__ import annotations

from artistpath_builder.sources.listenbrainz import ListenBrainzSource


class LbdBulkSource(ListenBrainzSource):
    """Our own similarity table, emitted as an archive. Read-only; the network is never used."""

    name = "lbd"

    def request_url(self, mbid: str) -> str:  # pragma: no cover - guard, never a code path
        raise RuntimeError(
            f"LbdBulkSource is never fetched (asked for {mbid!r}). Its payloads are "
            "written by emit_archive.py from a derived pair table; a build that tries "
            "to fetch through it is misconfigured."
        )
