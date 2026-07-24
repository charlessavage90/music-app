"""Resolve the owner's 2026-07-23 F3/F6 bypass URLs against the adopted artifact.

Discharges prerequisite **P1** of the Track 2 pre-registration: pair 8 of the analysis
set is "the owner's F6 bypass pair, captured from his 2026-07-23 test URLs". The URLs
were supplied by the owner directly; the execution log's claim that they lived in the
branch/PR thread was wrong (no PR carries any comment).

Reports names for the endpoints and for every bypassed artist, in URL order.

**Currency warning, deliberately in the output:** the percentile printed here is the
*in-graph* popularity percentile. Log §2.11 establishes that in-graph popularity is NOT
fame at the top of the distribution, and the Track 2 sweep is scored on an external fame
proxy for exactly that reason. These percentiles describe where the router placed an
artist, not how well-known they are.

Run from `api/`:
    UV_LINK_MODE=copy uv run python ../builder/analysis/2026-07-23-f6-trace-capture/resolve_trace.py
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

F6 = (
    "http://localhost:5173/path/561d854a-6a28-4aa7-8c99-323e6ce46c2a/"
    "056e4f3e-d505-4dad-8ec1-d04f521cbb56"
    "?dislike=164f0d73-1234-4e2c-8743-d77bf2191051%2C5dcdb5eb-cb72-4e6e-9e63-b7bace604965"
    "%2Ce795e03d-b5d5-4a5f-834d-162cfb308a2c%2Cafb680f2-b6eb-4cd7-a70b-a63b25c763d5"
    "%2C54799c0e-eb45-4eea-996d-c4d71a63c499%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b"
    "%2Ccc7d4686-ea02-45fd-956e-94c1a322558c%2Cac2d1c91-3667-46aa-9fe7-170ca7fce9e2"
    "%2C487bfd74-71bf-46dd-b89c-80b7a0f06f2f%2Cb95ce3ff-3d05-4e87-9e01-c97b66af13d4"
    "%2C4d5447d7-c61c-4120-ba1b-d7f471d385b9%2Cf27ec8db-af05-4f36-916e-3d57f91ecf5e"
    "%2Cc3f28da8-662d-4f09-bdc7-3084bf685930%2C1946a82a-f927-40c2-8235-38d64f50d043"
    "%2C2fddb92d-24b2-46a5-bf28-3aed46f4684c%2Cc98d40fd-f6cf-4b26-883e-eaa515ee2851"
    "%2Cc7020c6d-cae9-4db3-92a7-e5c561cbad50%2Cb2029169-2574-4305-820f-252a5fde3697"
    "%2C596ffa74-3d08-44ef-b113-765d43d12738%2C859d0860-d480-4efd-970c-c05d5f1776b8"
    "%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d%2C9c9f1380-2516-4fc9-a3e6-f9f61941d090"
    "%2C45a663b5-b1cb-4a91-bff6-2bef7bbfdd76%2C985c709c-7771-4de3-9024-7bda29ebe3f9"
    "%2Cb017a7ae-e5ee-4675-bb13-c83346134971%2C64b94289-9474-4d43-8c93-918ccc1920d1"
    "&known=17b53d9f-5c63-4a09-a593-dde4608e0db9%2C109958eb-a335-4c5e-907e-597ff4c6af46"
    "%2Cabd506e1-6f2b-4d6f-b937-92c267f6f88b%2C1f43d76f-8edf-44f6-aaf1-b65f05ad9402"
    "%2Ca66999a7-ae5c-460e-ba94-1a01143ae847%2Cbe407b02-f3e6-4ed5-9489-f8e5f0ab36dc"
    "%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2C99ea432a-e3d8-42cb-9d5e-db316a6a8458"
    "%2C6f1de078-6684-4792-820d-2ffad64c15ed%2C5441c29d-3602-4898-b1a1-b77fa23b8e50"
    "%2C83d91898-7763-47d7-b03b-b92132375c47%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d"
    "%2Cc5eb9407-caeb-4303-b383-6929aa94021c%2C6d7b7cd4-254b-4c25-83f6-dd20f98ceacd"
    "%2C5b11f4ce-a62d-471e-81fc-a69a8278c7da%2C678d88b2-87b0-403b-b63d-5da7465aecc3"
)

F3 = (
    "http://localhost:5173/path/561d854a-6a28-4aa7-8c99-323e6ce46c2a/"
    "056e4f3e-d505-4dad-8ec1-d04f521cbb56"
    "?dislike=164f0d73-1234-4e2c-8743-d77bf2191051%2C5dcdb5eb-cb72-4e6e-9e63-b7bace604965"
    "%2Ce795e03d-b5d5-4a5f-834d-162cfb308a2c%2Cafb680f2-b6eb-4cd7-a70b-a63b25c763d5"
    "&known=17b53d9f-5c63-4a09-a593-dde4608e0db9%2C109958eb-a335-4c5e-907e-597ff4c6af46"
    "%2Cabd506e1-6f2b-4d6f-b937-92c267f6f88b%2C1f43d76f-8edf-44f6-aaf1-b65f05ad9402"
    "%2Ca66999a7-ae5c-460e-ba94-1a01143ae847%2Cbe407b02-f3e6-4ed5-9489-f8e5f0ab36dc"
    "%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2C99ea432a-e3d8-42cb-9d5e-db316a6a8458"
    "%2C6f1de078-6684-4792-820d-2ffad64c15ed%2C5441c29d-3602-4898-b1a1-b77fa23b8e50"
    "%2C83d91898-7763-47d7-b03b-b92132375c47"
)


def parse(url: str) -> tuple[str, str, list[str], list[str]]:
    u = urlparse(url)
    parts = [p for p in u.path.split("/") if p]
    src, dst = parts[-2], parts[-1]
    q = parse_qs(u.query)

    def lst(key: str) -> list[str]:
        raw = q.get(key, [""])[0]
        return [x for x in unquote(raw).split(",") if x]

    return src, dst, lst("dislike"), lst("known")


def main() -> None:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore

    store = GraphStore.load(GRAPH)
    n = store.artist_count
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    order = np.argsort(pop, kind="stable")
    ranks = np.empty(n, dtype=np.float64)
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

    def show(mbid: str) -> str:
        k = idx.get(mbid)
        if k is None:
            return f"  !! NOT IN GRAPH  {mbid}"
        return f"  {store.names[k]:<34} pctl {pctl[k]:.4f}  raw {pop[k]:.4f}"

    f6_src, f6_dst, f6_dis, f6_kno = parse(F6)
    f3_src, f3_dst, f3_dis, f3_kno = parse(F3)

    print("=== ENDPOINTS ===")
    print("from:")
    print(show(f6_src))
    print("to:")
    print(show(f6_dst))
    print(f"\nsame pair in both URLs: {(f3_src, f3_dst) == (f6_src, f6_dst)}")
    print(f"F3 is a prefix of F6 — dislikes: {f6_dis[:len(f3_dis)] == f3_dis}"
          f"   knowns: {f6_kno[:len(f3_kno)] == f3_kno}")
    print(f"F3 depth: {len(f3_dis) + len(f3_kno)} bypasses "
          f"({len(f3_dis)} dislike, {len(f3_kno)} known)")
    print(f"F6 depth: {len(f6_dis) + len(f6_kno)} bypasses "
          f"({len(f6_dis)} dislike, {len(f6_kno)} known)")

    missing = [m for m in [f6_src, f6_dst, *f6_dis, *f6_kno] if m not in idx]
    print(f"\nall {len([f6_src, f6_dst, *f6_dis, *f6_kno])} mbids resolve: {not missing}")
    if missing:
        print("  MISSING:", missing)

    print("\n=== DISLIKED, in URL order ===")
    for k, m in enumerate(f6_dis, 1):
        mark = "  <- F3 snapshot ends here" if k == len(f3_dis) else ""
        print(f"{k:>3}." + show(m) + mark)

    print("\n=== KNOWN, in URL order ===")
    for k, m in enumerate(f6_kno, 1):
        mark = "  <- F3 snapshot ends here" if k == len(f3_kno) else ""
        print(f"{k:>3}." + show(m) + mark)

    print("\nNOTE: percentiles above are IN-GRAPH popularity, not fame (log 2.11).")
    print("The two signals are separate URL params, so the interleaving of dislike")
    print("and known presses is NOT recoverable — only the order within each list.")


if __name__ == "__main__":
    main()
