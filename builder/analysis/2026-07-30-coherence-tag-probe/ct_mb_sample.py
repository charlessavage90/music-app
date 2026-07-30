"""COH-2 route B + THE KILL GATE: MusicBrainz genre/tag coverage, banded sample.

WHAT THIS MEASURES
  MusicBrainz can carry tags and curated genres for every MBID -- in
  principle it has none of Wikidata's item cap. In practice tagging is
  volunteer effort and may thin in exactly the obscure tail where the fame
  proxy is already blind (FPC-3). The full artifact at the MB web service's
  1 req/s is ~21 hours, so this is a stratified sample: min(300, band size)
  per band, seeded, from the sorted band lists -- deterministic.

THE INSTRUMENT, DECIDED NOW
  Any step-2 coherence score uses an artist's GENRE SET: MusicBrainz genres
  UNION Wikidata P136 (normalised per ct_common.norm_genre). Raw MB tags are
  reported as a descriptive column only -- they are not the instrument, and
  a tags-based variant would be a new probe, not a re-read of this one.

KILL GATE, FIXED BEFORE ANY FETCH
  Step 2 runs ONLY IF union-genre coverage (>= 1 MB genre or >= 1 P136
  statement; denominator = ALL sampled artists in the band) in the LOWER
  HALF band is >= 50%. Otherwise the probe STOPS and the kill is the result:
  the instrument's raw material is dark on most of the region the product
  exists to serve -- the Wikipedia failure mode twice (execution log §7's
  own warning), and nothing should be built on it.
    Why 50%: an instrument dark on half the tail cannot score the paths a
  successful obscurity push would deliver (FPC-9's route is the live
  example), and Wikipedia's own tail figure is 27.4% -- a bar materially
  above it, low enough that a genuinely-covering source passes.
    Precision: n = 300 gives a 95% CI half-width of <= 5.7 points at p = 0.5.
  The gate fires on the point estimate; a result within 6 points of the bar
  is reported as within noise of the bar, and the verdict is flagged fragile.

PREDICTION (weaker than the gate, falsifiable)
  Union lower-half coverage lands ABOVE Wikipedia's 27.4% EN-article figure
  -- tagging an artist is cheaper than writing an article about them.
  Refuted if <= 27.4%. The gate outcome itself I do not predict; genuinely
  uncertain, which is why the probe exists.

BOTH DENOMINATORS (GRT-P4)
  all sampled, and MB-resolved (HTTP 200) -- deleted MBIDs exist in the
  artifact (the nameless-node class) and a 404 is an answer, not a gap.

Run from `builder/` (route A first -- the union column reads its output):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-coherence-tag-probe/ct_mb_sample.py
"""

from __future__ import annotations

import argparse
import json
import random

from ct_common import (
    BAND_ORDER,
    HERE,
    band_of,
    fame_frame,
    fetch_mb_artists,
    load_partial,
    mb_genre_set,
    mb_tag_set,
)

P136_RAW = HERE / "ct_wikidata_genres.json"
OUT_RAW = HERE / "ct_mb_sample_raw.json"
OUT = HERE / "ct_coverage.json"

SEED = 20260730
PER_BAND = 300
GATE_BAND = "lower half"
GATE_BAR = 0.50
NOISE_HALF_WIDTH = 0.06


def sample_mbids(frame: dict[str, float]) -> dict[str, list[str]]:
    bands: dict[str, list[str]] = {b: [] for b in BAND_ORDER}
    for mbid in sorted(frame):
        bands[band_of(frame[mbid])].append(mbid)
    rng = random.Random(SEED)
    return {b: sorted(rng.sample(v, min(PER_BAND, len(v)))) for b, v in bands.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="first N per band, for a smoke run")
    args = ap.parse_args()

    frame = fame_frame()
    p136 = json.loads(P136_RAW.read_text(encoding="utf-8"))
    sampled = sample_mbids(frame)
    if args.limit:
        sampled = {b: v[: args.limit] for b, v in sampled.items()}
    flat = [m for b in BAND_ORDER for m in sampled[b]]

    done = load_partial(OUT_RAW)
    done = fetch_mb_artists(flat, done, OUT_RAW, label="mb-sample")

    summary: dict[str, dict] = {}
    print(
        f"\n{'band':>12} {'n':>5} {'resolved':>9} {'MB genre':>9} {'MB tag':>8} "
        f"{'P136':>6} {'UNION':>7} {'union/resolved':>15}"
    )
    for b in BAND_ORDER:
        mbids = sampled[b]
        n = len(mbids)
        resolved = [m for m in mbids if done.get(m, {}).get("status") == 200]
        genre = sum(1 for m in mbids if mb_genre_set(done.get(m)))
        tag = sum(1 for m in mbids if mb_tag_set(done.get(m)))
        p136_hit = sum(1 for m in mbids if p136.get(m))
        union = sum(1 for m in mbids if mb_genre_set(done.get(m)) or p136.get(m))
        union_resolved = sum(
            1 for m in resolved if mb_genre_set(done.get(m)) or p136.get(m)
        )
        summary[b] = {
            "n": n,
            "resolved": len(resolved),
            "mb_genre": genre,
            "mb_tag": tag,
            "p136": p136_hit,
            "union_genre": union,
            "union_genre_of_resolved": union_resolved,
        }
        print(
            f"{b:>12} {n:>5} {len(resolved) / n:>8.1%} {genre / n:>8.1%} "
            f"{tag / n:>7.1%} {p136_hit / n:>5.1%} {union / n:>6.1%} "
            f"{(union_resolved / len(resolved)) if resolved else 0:>14.1%}"
        )

    g = summary[GATE_BAND]
    rate = g["union_genre"] / g["n"]
    verdict = "PROCEED to step 2" if rate >= GATE_BAR else "KILL -- step 2 does not run"
    fragile = abs(rate - GATE_BAR) < NOISE_HALF_WIDTH
    print(f"\nKILL GATE ({GATE_BAND}, union genre / all sampled): "
          f"{rate:.1%} against a {GATE_BAR:.0%} bar -> {verdict}")
    if fragile:
        print("  NOTE: within noise of the bar (±6 points at n=300); "
              "verdict stands but is fragile, and the report must say so.")

    out = {
        "seed": SEED,
        "per_band": PER_BAND,
        "gate": {
            "band": GATE_BAND,
            "bar": GATE_BAR,
            "rate": round(rate, 4),
            "verdict": verdict,
            "within_noise": fragile,
        },
        "bands": summary,
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n-> {OUT_RAW.name}, {OUT.name}")


if __name__ == "__main__":
    main()
