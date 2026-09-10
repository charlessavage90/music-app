"""`LBD-` Task 4 — draw and PIN the `LBD-C1` fidelity sample.

The pre-registration's section 2 fixes this sample, and `LBDR-F7` is why it is drawn by an
explicit script rather than inline at read time:

  > 3,000 artists drawn by MBID from the pinned snapshot
  > `C:\\dev\\music-app\\builder\\scratch\\grt-archive-algb.pre-cex-snapshot`, by path, its
  > identity confirmed against the `LUX-E1` README before the draw -- NOT from the live
  > archive tree, which gained tens of thousands of response files after the served map was
  > built. Stratified into five equal bands by `fame_lb_raw` from the served artifact's
  > metadata, 600 per band, drawn with `random.Random(20260907)` over the sorted MBID list,
  > AND THE RESULTING LIST IS COMMITTED AS A FILE WITH ITS sha256 BEFORE TASK 4 RUNS.

So the output lands in this analysis directory (committed, in git) as well as under `D:\\`,
and its sha256 is printed and recorded in the README. Nothing is written into
`builder/scratch/` (`LBD-D8`); the snapshot and the artifact are read by absolute path.

--------------------------------------------------------------------------------------
WHY THIS READS THE METADATA BLOB DIRECTLY, AND WHY THAT IS NOT A SECOND PARSER
--------------------------------------------------------------------------------------

Task 1 loaded both artifacts through the SHIPPED `GraphStore` precisely so a second parser
could not disagree with what the API loads. This script cannot do only that, and the reason
is in the shipped code:

    fame_lb_pctl: np.ndarray | None = None   # graph_store.py:52
    # ... `pctl` in the name because it is a RANK, never a value -- the raw
    # counts are not kept, since nothing routes on them.

`GraphStore` DISCARDS the raw listener counts. It keeps only the percentile, and
`fame_percentiles` gives **null fame the value 0.0** while excluding it from the frame -- so
a null and a genuinely least-listened artist are indistinguishable downstream. The
pre-registration bands on `fame_lb_raw` and this script must exclude nulls, so the raw list
is required and the shipped store cannot supply it.

So the blob is read directly AND THEN PROVED TO AGREE with the shipped parser, on both
things it could disagree about:

  1. `meta["mbids"]` is identical, in order, to `store.mbids`; and
  2. `GraphStore.fame_percentiles(raw)` reproduces `store.fame_lb_pctl` exactly.

If either fails the script refuses. That is strictly stronger than using either route alone:
it is the raw values the pre-registration asks for, plus a proof that they are the same
values the API is serving from.

Run it from the worktree's `api/` so the shipped parser is importable:

    cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \\
      ../builder/analysis/2026-09-08-lbd-similarity/lbd_c1_sample.py

ELIGIBILITY, stated because the pre-registration's sentence does not settle it and a later
reader must not have to guess. An artist is eligible when it (a) has a similarity response
file in the pinned snapshot -- without one there is nothing to be faithful TO -- and (b)
carries a non-null `fame_lb`, without which it cannot be banded. Both exclusion counts are
printed and recorded, so the denominator is visible rather than implied.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

MAIN_TREE = Path(r"C:\dev\music-app")
SNAPSHOT = MAIN_TREE / "builder" / "scratch" / "grt-archive-algb.pre-cex-snapshot"
SERVED = MAIN_TREE / "builder" / "scratch" / "graph-msw-tu50.bin"

# Pinned by Task 1's README, which matched it against the artifact's own manifest sidecar.
SERVED_SHA256 = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"

SEED = 20260907
BANDS = 5
PER_BAND = 600

OUT_REPO = Path(__file__).resolve().parent / "lbd_c1_sample.tsv"
OUT_D = Path(r"D:\unsung-large-data\lbd-inputs\lbd_c1_sample.tsv")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "api" / "src"))
    from artistpath_api import graph_store as gs

    if not SNAPSHOT.is_dir():
        raise SystemExit(f"pinned snapshot not found: {SNAPSHOT}")

    print(f"[c1] served artifact  {SERVED}")
    actual = sha256_of(SERVED)
    if actual != SERVED_SHA256:
        raise SystemExit(
            f"REFUSING: served artifact sha256 {actual} != pinned {SERVED_SHA256}.\n"
            "Artifacts under builder/scratch/ are gitignored and NOT interchangeable."
        )
    print(f"[c1] sha256 matches   {actual}")

    payload = SERVED.read_bytes()
    store = gs.GraphStore.from_bytes(payload) if hasattr(gs.GraphStore, "from_bytes") else gs.GraphStore.load(SERVED)

    # The raw metadata blob, located exactly as graph_store.py locates it.
    magic, version, n, e, meta_len = gs._HEADER.unpack_from(payload)
    cursor = gs._HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor : cursor + meta_len])
    fame_raw = meta.get("fame_lb")
    if not fame_raw:
        raise SystemExit("served artifact carries no fame_lb; cannot band")

    # --- the two agreement proofs -------------------------------------------------
    if list(meta["mbids"]) != list(store.mbids):
        raise SystemExit("REFUSING: metadata mbids disagree with the shipped parser")
    recomputed = gs.GraphStore.fame_percentiles(fame_raw)
    if store.fame_lb_pctl is None or not np.array_equal(recomputed, store.fame_lb_pctl):
        raise SystemExit("REFUSING: fame_percentiles(raw) does not reproduce store.fame_lb_pctl")
    print(f"[c1] agreement proved: mbids identical, fame_percentiles(raw) == store.fame_lb_pctl")

    mbids = list(store.mbids)

    # (a) the snapshot's own population: one response file per artist it holds a list for.
    algo_dirs = sorted(p for p in (SNAPSHOT / "similar").glob("*/*") if p.is_dir())
    if len(algo_dirs) != 1:
        raise SystemExit(f"expected exactly one algorithm dir, found {len(algo_dirs)}: {algo_dirs}")
    algo_dir = algo_dirs[0]
    print(f"[c1] algorithm dir    {algo_dir.name}")
    in_snapshot = {p.stem for p in algo_dir.glob("*.json")}
    print(f"[c1] snapshot artists {len(in_snapshot):,}")

    eligible: list[tuple[str, int]] = []
    no_file = 0
    no_fame = 0
    for i, mbid in enumerate(mbids):
        if mbid not in in_snapshot:
            no_file += 1
            continue
        v = fame_raw[i]
        if v is None:
            no_fame += 1
            continue
        eligible.append((mbid, int(v)))

    print(f"[c1] served artists   {len(mbids):,}")
    print(f"[c1] excluded, no snapshot response file : {no_file:,}")
    print(f"[c1] excluded, fame_lb null              : {no_fame:,}")
    print(f"[c1] ELIGIBLE                            : {len(eligible):,}")

    # Five equal bands by fame_lb_raw -- equal-COUNT quintiles of the eligible population,
    # band 0 the least-listened and band 4 the most. The sort key carries the MBID so ties
    # on fame land deterministically.
    eligible.sort(key=lambda t: (t[1], t[0]))
    n_e = len(eligible)
    bounds = [round(n_e * b / BANDS) for b in range(BANDS + 1)]

    rng = random.Random(SEED)
    drawn: list[tuple[str, int, int]] = []
    band_ranges: list[dict] = []
    for b in range(BANDS):
        members = eligible[bounds[b] : bounds[b + 1]]
        pool = sorted(m for m, _ in members)  # draw over the SORTED MBID list
        if len(pool) < PER_BAND:
            raise SystemExit(f"band {b} has {len(pool)} artists, fewer than {PER_BAND}")
        picked = rng.sample(pool, PER_BAND)
        fame_of = dict(members)
        drawn.extend((m, b, fame_of[m]) for m in picked)
        lo, hi = members[0][1], members[-1][1]
        band_ranges.append({"band": b, "pool": len(pool), "fame_lb_raw_min": lo, "fame_lb_raw_max": hi})
        print(f"[c1] band {b}: pool {len(pool):,}  fame_lb_raw {lo}..{hi}  drew {PER_BAND}")

    drawn.sort()
    body = "\n".join(
        ["mbid\tband\tfame_lb_raw"] + [f"{m}\t{b}\t{f}" for m, b, f in drawn]
    ) + "\n"

    OUT_REPO.write_text(body, encoding="utf-8")
    OUT_D.parent.mkdir(parents=True, exist_ok=True)
    OUT_D.write_text(body, encoding="utf-8")

    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    print(f"[c1] wrote {len(drawn):,} artists")
    print(f"[c1] SAMPLE SHA256 {digest}")

    OUT_REPO.with_suffix(".identity.json").write_text(
        json.dumps(
            {
                "sample_sha256": digest,
                "seed": SEED,
                "bands": BANDS,
                "per_band": PER_BAND,
                "n": len(drawn),
                "snapshot": str(SNAPSHOT),
                "algorithm_dir": algo_dir.name,
                "served_artifact": str(SERVED),
                "served_sha256": SERVED_SHA256,
                "snapshot_artists": len(in_snapshot),
                "served_artists": len(mbids),
                "excluded_no_response_file": no_file,
                "excluded_fame_null": no_fame,
                "eligible": len(eligible),
                "band_ranges": band_ranges,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
