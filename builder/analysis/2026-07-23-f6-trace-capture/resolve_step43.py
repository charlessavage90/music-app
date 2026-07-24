"""The owner's 43rd bypass — who he bypassed, and where the router went next.

He logged a URL one step beyond the F6 capture ("one step further than Max Richter")
but did not know whom he had bypassed to get there. The URL is F6 plus exactly one
appended `dislike`, so the new MBID identifies the bypassed artist.

Because all path state lives in the URL and `find_path` is a pure full regeneration,
the paths he saw at both states are exactly reconstructable — exclusion ORDER does not
matter (hard exclusions are a set; the floor depends only on the per-reason counts).

Run from `api/`:
    UV_LINK_MODE=copy uv run python ../builder/analysis/2026-07-23-f6-trace-capture/resolve_step43.py
"""

import hashlib
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "api" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

from resolve_trace import F6  # noqa: E402  (same directory; owns the F6 URL)

STEP43 = F6.replace(
    "%2C64b94289-9474-4d43-8c93-918ccc1920d1&known=",
    "%2C64b94289-9474-4d43-8c93-918ccc1920d1"
    "%2Cc2e36518-9c3b-4dcb-82ad-a3fc7fe99c67&known=",
)


def parse(url: str) -> tuple[str, str, list[str], list[str]]:
    u = urlparse(url)
    parts = [p for p in u.path.split("/") if p]
    q = parse_qs(u.query)

    def lst(key: str) -> list[str]:
        return [x for x in unquote(q.get(key, [""])[0]).split(",") if x]

    return parts[-2], parts[-1], lst("dislike"), lst("known")


def main() -> None:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"

    from artistpath_api.config import ApiConfig
    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion, find_path

    store = GraphStore.load(GRAPH)
    cfg = ApiConfig()
    n = len(store.mbids)
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    order = np.argsort(pop, kind="stable")
    ranks = np.empty(n)
    srt = pop[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and srt[j + 1] == srt[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2.0
        i = j + 1
    pctl = ranks / (n - 1)

    idx = {m: k for k, m in enumerate(store.mbids)}

    src6, dst6, dis6, kno6 = parse(F6)
    src7, dst7, dis7, kno7 = parse(STEP43)
    assert (src6, dst6) == (src7, dst7)
    assert dis7[:-1] == dis6 and kno7 == kno6, "step43 is not F6 + one dislike"

    new_mbid = dis7[-1]
    k = idx[new_mbid]
    print(f"F6      : {len(dis6)} dislike + {len(kno6)} known = {len(dis6)+len(kno6)} bypasses")
    print(f"step 43 : {len(dis7)} dislike + {len(kno7)} known = {len(dis7)+len(kno7)} bypasses")
    print("\n=== THE ARTIST YOU BYPASSED (the 27th dislike) ===")
    print(f"  {store.names[k]}   in-graph pctl {pctl[k]:.4f}   raw {pop[k]:.4f}")
    print(f"  mbid {new_mbid}")

    def route(dis: list[str], kno: list[str]) -> list[int] | None:
        ex = [Exclusion(node=idx[m], reason=DISLIKE) for m in dis]
        ex += [Exclusion(node=idx[m], reason=KNOWN) for m in kno]
        return find_path(store, idx[src6], idx[dst6], ex, cfg)

    for label, dis, kno in (("F6 (42 bypasses)", dis6, kno6),
                            ("step 43", dis7, kno7)):
        path = route(dis, kno)
        print(f"\n=== PATH AT {label} ===")
        if path is None:
            print("  no path")
            continue
        for pos, node in enumerate(path):
            tag = "  " if 0 < pos < len(path) - 1 else "* "
            print(f"  {tag}{store.names[node]:<32} pctl {pctl[node]:.4f}")
        interior = path[1:-1]
        if interior:
            ps = [pctl[v] for v in interior]
            print(f"  interior: {len(interior)}   min pctl {min(ps):.4f}   median {np.median(ps):.4f}")

    print("\n(* = endpoint. Percentiles are IN-GRAPH popularity, not fame — log §2.11.)")


if __name__ == "__main__":
    main()
