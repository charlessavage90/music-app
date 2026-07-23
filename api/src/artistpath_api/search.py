"""Artist-name autocomplete over the graph's name list.

At 75k names a linear scan is well under a millisecond, so the index is a
plain normalised-name list; prefix matches rank above substring matches, and
both rank by popularity.
"""

from __future__ import annotations

import unicodedata

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore


def normalise(text: str) -> str:
    """Lowercase and strip accents so 'Sigur Ros' matches 'Sigur Rós'."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.lower().strip()


class ArtistSearch:
    def __init__(self, store: GraphStore, cfg: ApiConfig) -> None:
        self._cfg = cfg
        self._store = store
        self._normalised = [normalise(n) for n in store.names]

    def search(self, query: str) -> list[int]:
        q = normalise(query)
        if not q:
            return []
        prefix: list[int] = []
        substring: list[int] = []
        for i, name in enumerate(self._normalised):
            if name.startswith(q):
                prefix.append(i)
            elif q in name:
                substring.append(i)

        pop_raw = self._store.pop_raw
        prefix.sort(key=lambda i: -pop_raw[i])
        substring.sort(key=lambda i: -pop_raw[i])
        return (prefix + substring)[: self._cfg.search_limit]
