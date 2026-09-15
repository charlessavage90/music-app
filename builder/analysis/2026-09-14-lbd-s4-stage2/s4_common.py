"""`LBA-` stage 2 — the two quantities every stage-2 script must compute IDENTICALLY.

`LBA-M1`'s bytes definition is the reason this module exists. §4 (revised under `LBA-AM1`,
finding `LBA-AM1-A12`) defines the arm's size as the BARE-ARTIFACT size:

    24 + 4(N+1) + 9 * E_csr + len(bare metadata JSON)

where *bare* is the four MANDATORY metadata keys only — `mbids`, `names`, `disambiguations`,
`popularity` — and the other five (`deezer_ids`, `fame_lb`, `spotify_ids`, `apple_ids`,
`artist_facts`) are additive and omitted when empty by `artifact.py`'s `serialise`.

WHY IT IS COMPUTED BY DECODING AND NEVER BY REBUILDING. Seven arms are built here and two are
reused (`LBA-D9`), and the two reused artifacts carry ALL FIVE additive keys, because they were
built for a listen. Comparing their on-disk bytes against seven fame-free builds would compare
seven arms against two that are about a third larger FOR A REASON THAT IS NOT THE ARM — and
`LBA-D9` forbids rebuilding them. Decoding gives the same number for all nine.

The header is `artifact.py`'s `<4sIIIQ>` = 24 bytes; then `int32[N+1]`, `int32[E]`, `float32[E]`,
`uint8[E]` — 4 + 4 + 1 = 9 bytes per CSR ENTRY. UNITS: `E_csr` is CSR entries, each connection in
BOTH directions, which is what every manifest sidecar's "edges" records and what `Graph.edge_count`
holds. It is NOT the "connections" unit (degree sum / 2), and it is NOT archive neighbour rows.
Three edge units are in play in this track and the served-population README §0 records a build
refused once for confusing two of them.

The JSON encoding is `serialise`'s own — `sort_keys=True`, `separators=(",", ":")`,
`ensure_ascii=False` — and `deserialise` returns `popularity` as a plain Python list straight from
`json.loads`, so re-dumping it reproduces the original bytes exactly rather than approximating them.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

_HEADER_BYTES = 24
_BYTES_PER_CSR_ENTRY = 9  # int32 neighbour + float32 score + uint8 edge type
_MANDATORY_KEYS = ("mbids", "names", "disambiguations", "popularity")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def bare_metadata_bytes(mbids, names, disambiguations, pop_raw) -> int:
    """`serialise`'s metadata blob with the five additive keys absent."""
    meta = {
        "mbids": list(mbids),
        "names": list(names),
        "disambiguations": list(disambiguations),
        "popularity": list(pop_raw),
    }
    assert set(meta) == set(_MANDATORY_KEYS)
    return len(json.dumps(meta, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def bare_artifact_bytes(n_artists: int, e_csr: int, metadata_bytes: int) -> int:
    return _HEADER_BYTES + 4 * (n_artists + 1) + _BYTES_PER_CSR_ENTRY * e_csr + metadata_bytes


def bare_size_of_graph(graph) -> dict:
    """For a graph in hand (a fresh build). Same arithmetic as `bare_size_of_artifact`."""
    meta_bytes = bare_metadata_bytes(graph.mbids, graph.names, graph.disambiguations, graph.pop_raw)
    return {
        "artists": int(graph.artist_count),
        "csr_entries": int(graph.edge_count),
        "bare_metadata_json_bytes": meta_bytes,
        "bare_artifact_bytes": bare_artifact_bytes(int(graph.artist_count), int(graph.edge_count), meta_bytes),
    }


def bare_size_of_artifact(path: Path) -> dict:
    """For an artifact on disk — the two reused arms, and every built one re-read from its file.

    Imports `deserialise` lazily so this module can be used without the builder package importable.
    """
    from artistpath_builder.artifact import deserialise

    payload = Path(path).read_bytes()
    graph = deserialise(payload)
    out = bare_size_of_graph(graph)
    out["serialised_bytes_on_disk"] = len(payload)
    # Mirrors `serialise`'s own two guards EXACTLY and they are not the same guard: truthiness of
    # the list for `deezer_ids` and `fame_lb`, `any(...)` for the three `LUX-4` keys — because once
    # the pipeline runs those three are node-indexed and therefore never empty, only full of ""
    # and {}. `artifact.py` records that difference as "the whole guard".
    present = []
    if graph.deezer_ids:
        present.append("deezer_ids")
    if graph.fame_lb_raw:
        present.append("fame_lb")
    for key, value in (("spotify_ids", graph.spotify_ids), ("apple_ids", graph.apple_ids),
                       ("artist_facts", graph.artist_facts)):
        if any(value):
            present.append(key)
    out["additive_keys_present"] = present
    return out
