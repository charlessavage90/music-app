"""Binary CSR artifact.

One immutable file, versioned in S3, loaded into memory at API boot. Never a
database (spec section 3). Byte-identical output for identical input is a
hard requirement — it is how archive replay is verified.

Layout, all little-endian:

    offset  type          meaning
    0       char[4]       magic 'APG1'
    4       uint32        format version
    8       uint32        artist count N
    12      uint32        edge count E
    16      uint64        metadata JSON length J
    24      int32[N+1]    offsets
    ...     int32[E]      neighbours
    ...     float32[E]    scores
    ...     uint8[E]      edge types
    ...     char[J]       metadata JSON (UTF-8)

ADDING A NEW PIECE OF PER-ARTIST METADATA
  Written down because it was spread across six files and three docstrings,
  and three changes (`deezer_ids`, `fame_lb`, `LUX-4`) each rediscovered it.
  Nothing here BLOCKS a new field: `FORMAT_VERSION` stays 1 because the keys
  are additive, and J is a uint64, so there is no practical size limit.

  The nine steps, in order:
    1. Extract it offline into a dated payload (pattern: the scripts under
       builder/analysis/, e.g. 2026-09-05-lux4-extract/).
    2. Ship it as frozen, sha-pinned package data with a loader module
       (pattern: deezer_ids.py, dsp_links.py, artist_facts.py).
    3. Add a DEFAULTED field to `Graph` -- frozen probes call `build_graph`
       positionally and an empty list must keep their artifacts byte-identical.
    4. Project it onto node order INSIDE `build_graph`, never in the caller:
       node ids are assigned there, and a caller ordering it itself would be
       re-deriving `sorted(...)` and could silently disagree.
    5. Pass the map to `build_graph` from `pipeline.py` as a DICT.
    6. Write it here, guarded by `any(...)` -- see the warning at the write
       site -- and read it back with `.get(key, [])`, never `meta[key]`.
    7. Record it in `RECORDED_METADATA_KEYS` (tests/test_pipeline_mirrors.py),
       which fails until you make a per-mirror decision. That guard exists
       because steps 1-6 change what every ERA_PINNED_CALLER builds while
       leaving every test green -- which is how the first two slipped through.
    8. Read it in the api (`graph_store.py`). A key read through a
       BOUNDS-CHECKED accessor may be shorter than N; a key indexed directly
       in the cost function must have its length checked. Copy the right one.
    9. Expose it on `ArtistOut` (three wire positions) and render it.

  THE TWO COSTS, neither of which is avoidable:
    - A REBUILD AND A DEPLOY. The artifact is prebuilt and immutable, so no
      metadata reaches users without one, plus a new ARTISTPATH_GRAPH_SHA256
      taken from the manifest (never transcribed by hand, `DEP-24`).
    - RE-EXTRACTION REFRESHES EVERYTHING, and this is the trap. The dump is a
      dated snapshot, gitignored, and MusicBrainz rotates it. Re-running an
      extraction to add one field also picks up every upstream change to the
      fields already shipped, so "add a field" silently becomes "refresh all
      of them". To isolate, extract the new field alone and merge it into the
      existing frozen payload rather than regenerating that payload.

  ⚠ `artist_facts` IS THE CHEAP PLACE TO ADD A FACT, and it is deliberately
  open-ended: a new key inside its per-artist dict needs NONE of steps 3-9 --
  only a re-extraction, a rebuild, and frontend rendering. The price is that
  the dict repeats its key NAMES once per artist, so each new fact costs
  roughly (len(name) + 3) x N bytes of pure overhead. Measured 2026-09-06:
  as a list of dicts it is 4.27 MB against 2.37 MB as parallel arrays and
  1.54 MB with the categoricals interned. The list-of-dicts shape was kept
  because 1.9 MB on a 22.7 MB artifact changes no decision and the artifact is
  never sent to a browser. REVISIT THAT IF GENRE TAGS LAND (`LUX-E6`): a list
  per artist is a different order of magnitude, and it is the case that would
  justify the parallel-array shape under a new key.
"""

from __future__ import annotations

import json
import struct

import numpy as np

from artistpath_builder.graph import Graph

MAGIC = b"APG1"
FORMAT_VERSION = 1
_HEADER = struct.Struct("<4sIIIQ")


def serialise(graph: Graph) -> bytes:
    meta: dict[str, object] = {
        "mbids": graph.mbids,
        "names": graph.names,
        "disambiguations": graph.disambiguations,
        # "popularity" is the APG1 wire key. It CANNOT be renamed without
        # invalidating every existing artifact and breaking the api-side
        # parser in lockstep — the format is the contract. Only the
        # in-memory identifier carries the currency (`pop_raw`).
        "popularity": graph.pop_raw,
    }
    # OMITTED WHEN EMPTY, and the omission is the design rather than laziness.
    # FORMAT_VERSION is not bumped, because both parsers check it for strict
    # equality: bumping it would stop every existing artifact loading, starting
    # with the one the app serves today. So the key is additive — a reader
    # without it ignores it, and a reader with it must tolerate its absence.
    #
    # Writing it unconditionally would also change the bytes of every artifact
    # built by the frozen probe mirrors, whose shas Track B's identity gate
    # pins. That is the divergence class PR #63 closed, and this is the same
    # hazard arriving from the other direction.
    if graph.deezer_ids:
        meta["deezer_ids"] = graph.deezer_ids

    # SAME additive-key discipline as deezer_ids above, and for the same two
    # reasons: FORMAT_VERSION stays 1 because both parsers check it for strict
    # equality, and the key is omitted when empty so every artifact built
    # before fame existed — including the frozen probe mirrors whose shas
    # Track B's identity gate pins — stays byte-identical.
    #
    # "fame_lb" is the WIRE key; the in-memory identifier carries the full
    # currency (`fame_lb_raw`), because a wire key cannot be renamed without
    # invalidating every artifact carrying it. Values are ListenBrainz
    # total_user_count, or JSON null where the instrument measured no
    # listeners — a null is a measured absence, never a floor (FAM-AM1.8), so
    # it must not be coerced to 0 on the way out.
    if graph.fame_lb_raw:
        meta["fame_lb"] = graph.fame_lb_raw

    # LUX-4. SAME additive-key discipline as deezer_ids and fame_lb above and
    # for the same two reasons: FORMAT_VERSION stays 1 because both parsers
    # check it for strict equality, and the keys are omitted when empty so
    # every artifact built before LUX-4 -- including the frozen probe mirrors
    # whose shas Track B's identity gate pins -- stays byte-identical.
    #
    # These are WIRE KEYS and permanent: the api reads them by these exact
    # strings, and renaming one invalidates every artifact carrying it.
    # Values are platform id TAILS, never URLs (`L4-D2`).
    #
    # ⚠ `any(...)`, NOT truthiness of the list, and the difference is the whole
    # guard. Once the pipeline runs these lists are node-indexed and therefore
    # NEVER empty -- they are full of "" and {} when nothing was extracted, and
    # `if graph.spotify_ids:` is true for such a list. That would write the key
    # unconditionally and change the bytes of every artifact with no links.
    if any(graph.spotify_ids):
        meta["spotify_ids"] = graph.spotify_ids
    if any(graph.apple_ids):
        meta["apple_ids"] = graph.apple_ids
    if any(graph.artist_facts):
        meta["artist_facts"] = graph.artist_facts

    metadata = json.dumps(
        meta,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    header = _HEADER.pack(
        MAGIC,
        FORMAT_VERSION,
        graph.artist_count,
        graph.edge_count,
        len(metadata),
    )

    return b"".join(
        [
            header,
            graph.offsets.astype("<i4").tobytes(),
            graph.neighbours.astype("<i4").tobytes(),
            graph.scores.astype("<f4").tobytes(),
            graph.edge_types.astype("<u1").tobytes(),
            metadata,
        ]
    )


def deserialise(payload: bytes) -> Graph:
    if len(payload) < _HEADER.size:
        raise ValueError("artifact truncated: shorter than header")

    magic, version, artist_count, edge_count, metadata_length = _HEADER.unpack_from(
        payload
    )
    if magic != MAGIC:
        raise ValueError(f"bad magic: expected {MAGIC!r}, got {magic!r}")
    if version != FORMAT_VERSION:
        raise ValueError(f"unsupported artifact version {version}")

    cursor = _HEADER.size

    def take(count: int, dtype: str, itemsize: int) -> np.ndarray:
        nonlocal cursor
        end = cursor + count * itemsize
        if end > len(payload):
            raise ValueError("artifact truncated: array extends past end of file")
        array = np.frombuffer(payload[cursor:end], dtype=dtype)
        cursor = end
        return array

    offsets = take(artist_count + 1, "<i4", 4)
    neighbours = take(edge_count, "<i4", 4)
    scores = take(edge_count, "<f4", 4)
    edge_types = take(edge_count, "<u1", 1)

    if cursor + metadata_length > len(payload):
        raise ValueError("artifact truncated: metadata extends past end of file")
    metadata = json.loads(payload[cursor : cursor + metadata_length])

    return Graph(
        mbids=metadata["mbids"],
        names=metadata["names"],
        disambiguations=metadata["disambiguations"],
        pop_raw=metadata["popularity"],  # wire key -> in-memory name
        offsets=offsets,
        neighbours=neighbours,
        scores=scores,
        edge_types=edge_types,
        # .get, not [...]: every artifact built before 2026-08-02 lacks the key,
        # including the one the app serves. Absence means "resolve by name",
        # which is what the app did before this existed.
        deezer_ids=metadata.get("deezer_ids", []),
        # .get for the same reason: every artifact built before 2026-08-05
        # lacks the key. Absence means the artifact cannot support the fame
        # ramp, which the api turns into a refusal to boot ONLY if the ramp is
        # actually switched on.
        fame_lb_raw=metadata.get("fame_lb", []),
        # LUX-4, read with `.get` for the same reason as the two above: the
        # keys are additive and FORMAT_VERSION was not bumped, so every
        # artifact built before today lacks all three -- including the served
        # one. Absence means "no link recorded", which the api renders as a
        # search fallback and an omitted info row.
        spotify_ids=metadata.get("spotify_ids", []),
        apple_ids=metadata.get("apple_ids", []),
        artist_facts=metadata.get("artist_facts", []),
    )
