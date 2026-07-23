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
    metadata = json.dumps(
        {
            "mbids": graph.mbids,
            "names": graph.names,
            "disambiguations": graph.disambiguations,
            # "popularity" is the APG1 wire key. It CANNOT be renamed without
            # invalidating every existing artifact and breaking the api-side
            # parser in lockstep — the format is the contract. Only the
            # in-memory identifier carries the currency (`pop_raw`).
            "popularity": graph.pop_raw,
        },
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
    )
