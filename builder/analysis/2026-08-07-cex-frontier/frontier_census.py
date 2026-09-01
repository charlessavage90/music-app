"""CEX- baseline: reconstruct the lost ALG-B frontier and place two named artists.

Offline and read-only. Reads the ALG-B archive, its checkpoint, the frozen drop
payloads and the adopted artifact; writes one JSON of results beside itself.

This is `ULC-F3`'s recovery step run as a measurement, BEFORE the `refrontier`
command exists. When that command lands it must reproduce `frontier_size` here
exactly; that equality is the command's acceptance test (`CEX-T1`).

ERA-PINNED. The paths and the algorithm below name the 2026-08-07 state:
the ALG-B archive at 75,000 responses and `graph-msw-tu50.bin` as the adopted
artifact. Do not repoint them at a later archive — this script's value is that
it records the pre-extension baseline. A post-extension census is a NEW script.

    UV_LINK_MODE=copy uv run python -u frontier_census.py
"""

from __future__ import annotations

import json
import struct
from collections import Counter
from pathlib import Path

SCRATCH = Path(__file__).resolve().parents[2] / "scratch"
DATA = Path(__file__).resolve().parents[2] / "src" / "artistpath_builder" / "data"
HERE = Path(__file__).resolve().parent

# ALG-B, the candidate algorithm — and the one the ADOPTED map was built under.
# BuilderConfig.algorithm still defaults to ALG-E; see the spec's CEX-R2.
ALGB = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)
ARCH = SCRATCH / "grt-archive-algb" / "similar" / "listenbrainz" / ALGB
CHECKPOINT = SCRATCH / "checkpoint-algb-full.json"
ARTIFACT = SCRATCH / "graph-msw-tu50.bin"
HEADER = struct.Struct("<4sIIIQ")

# The two artists the owner named as missing, 2026-08-07.
NAMED = {
    "goose-jam-band": "b925a474-d245-4217-bc13-2e153d82bebb",
    "commander-cody": "2d67f7f4-1e85-4278-bac6-424e6204a8b9",
}
PHISH = "e01646f2-2a04-450d-8bf2-0d993082e058"


def artifact_mbids(path: Path) -> set[str]:
    payload = path.read_bytes()
    magic, _version, n, e, meta_len = HEADER.unpack_from(payload)
    if magic != b"APG1":
        raise ValueError(f"not an APG1 artifact: {path}")
    cursor = HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor : cursor + meta_len])
    return set(meta["mbids"]), n, e


def main() -> None:
    result: dict = {"algorithm": ALGB, "archive": str(ARCH)}

    checkpoint = json.loads(CHECKPOINT.read_text())
    done = set(checkpoint["done"])
    discovered = set(checkpoint["discovered"])
    result["checkpoint"] = {
        "done": len(done),
        "discovered": len(discovered),
        "recorded_frontier": len(discovered - done),  # 0 — this IS ULC-F3
    }

    shipped, n_nodes, n_edges = artifact_mbids(ARTIFACT)
    result["artifact"] = {"nodes": n_nodes, "edges": n_edges}

    drops: dict[str, set[str]] = {}
    for label, filename in [
        ("no_release", "no_release_drop_algb_20260802.json"),
        ("featured_credit", "featured_credit_drop_algb_20260803_am1.json"),
        ("unlistenable", "unlistenable_drop_algb_20260805.json"),
    ]:
        blob = json.loads((DATA / filename).read_text())
        drops[label] = set(blob.get("drop_mbids", []))

    # `unlistenable` supersedes `no_release` (ULF-); the shipped build applies
    # it together with `featured_credit`.
    applied = drops["unlistenable"] | drops["featured_credit"]
    crawled_not_shipped = done - shipped
    result["gap_75k_to_artifact"] = {
        "crawled_not_shipped": len(crawled_not_shipped),
        "on_a_drop_list": len(crawled_not_shipped & applied),
        "lost_otherwise": len(crawled_not_shipped - applied),
        "drop_list_sizes": {k: len(v) for k, v in drops.items()},
    }

    # --- the reconstruction itself -----------------------------------------
    refs: Counter[str] = Counter()
    unparseable = 0
    files = sorted(ARCH.glob("*.json"))
    for path in files:
        try:
            rows = json.loads(path.read_bytes())
        except ValueError:
            unparseable += 1
            continue
        for row in rows:
            mbid = row.get("artist_mbid")
            if mbid:
                refs[mbid] += 1

    frontier = set(refs) - done
    result["reconstruction"] = {
        "responses_read": len(files),
        "unparseable": unparseable,
        "distinct_mbids_referenced": len(refs),
        "frontier_size": len(frontier),
    }

    buckets = Counter()
    for mbid in frontier:
        count = refs[mbid]
        if count == 1:
            buckets["1"] += 1
        elif count == 2:
            buckets["2"] += 1
        elif count <= 5:
            buckets["3-5"] += 1
        elif count <= 20:
            buckets["6-20"] += 1
        else:
            buckets[">20"] += 1
    result["frontier_by_inbound_refs"] = dict(buckets)

    # --- the two named artists ---------------------------------------------
    named: dict[str, dict] = {}
    for label, mbid in NAMED.items():
        named[label] = {
            "mbid": mbid,
            "crawled": mbid in done,
            "shipped": mbid in shipped,
            "in_frontier": mbid in frontier,
            "inbound_refs": refs.get(mbid, 0),
        }
    # Goose's only two neighbours under ALG-B are Phish and Fleet Foxes, both
    # crawled and shipped — and neither points back. That asymmetry, not the
    # crawl's size, is why growth cannot reach Goose (CEX-R1).
    phish_rows = json.loads((ARCH / f"{PHISH}.json").read_bytes())
    named["goose-jam-band"]["phish_list_length"] = len(phish_rows)
    named["goose-jam-band"]["phish_lowest_score"] = min(
        row.get("score", 0) for row in phish_rows
    )
    named["goose-jam-band"]["goose_in_phish_list"] = any(
        row.get("artist_mbid") == NAMED["goose-jam-band"] for row in phish_rows
    )
    result["named_artists"] = named

    out = HERE / "cex_frontier.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
