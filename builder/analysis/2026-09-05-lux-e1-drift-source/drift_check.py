"""Which build-side inputs drifted between the served map and HEAD?

Answers one question cheaply, before spending LUX-E1's ~23-minute rebuild:
does the ALG-B unlistenable drop list that HEAD now defaults to differ, ON
THE SERVED POPULATION, from the one graph-msw-tu50.bin was actually built
with?  Absolute list sizes are misleading -- the new list was censused over
the extended 117k population, so most of its extra entries name artists that
are not in the served 58,838-node graph at all and would be a no-op.

Read-only.  Touches nothing served.  Run from builder/.
"""

import json
import struct
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "src" / "artistpath_builder" / "data"
GRAPH = Path(__file__).resolve().parents[2] / "scratch" / "graph-msw-tu50.bin"

# The list graph-msw-tu50.bin was built with, and the one HEAD defaults to.
BUILT_WITH = DATA / "unlistenable_drop_algb_20260805.json"
HEAD_DEFAULT = DATA / "unlistenable_drop_algb_20260809.json"

_HEADER = struct.Struct("<4sIIIQ")  # matches api/.../graph_store.py


def drop_set(path: Path) -> tuple[set[str], dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return set(payload["drop_mbids"]), payload


def served_population(path: Path) -> set[str]:
    raw = path.read_bytes()
    *_, meta_len = _HEADER.unpack_from(raw)
    meta = json.loads(raw[len(raw) - meta_len :].decode("utf-8"))
    return set(meta["mbids"])


def main() -> None:
    old, old_payload = drop_set(BUILT_WITH)
    new, new_payload = drop_set(HEAD_DEFAULT)
    graph = served_population(GRAPH)

    print(f"built-with  {BUILT_WITH.name}: {len(old):,} drops over a "
          f"{old_payload['population']['count']:,} population")
    print(f"HEAD default {HEAD_DEFAULT.name}: {len(new):,} drops over a "
          f"{new_payload['population']['count']:,} population")
    print(f"  only in built-with: {len(old - new):,}")
    print(f"  only in HEAD's:     {len(new - old):,}")
    print(f"\nserved population: {len(graph):,}")
    print(f"  in the served graph AND newly dropped by HEAD's list: {len((new - old) & graph):,}")
    print(f"  dropped by built-with but not by HEAD's (would return): {len((old - new) & graph):,}")


if __name__ == "__main__":
    main()
