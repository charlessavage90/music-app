"""`LBA-M1` — the sizing table, and `LBA-G1`(a). Aggregates only; it measures nothing itself.

Its inputs are produced by three scripts that each run in their own process because each measures
a whole-process peak that never falls:

  `s4_boot_rss.py`   one `GraphStore`-only load per process, three repeats per artifact
  `s4_bare_copy.py`  the bare re-serialisation of the two reused arms (see that script for why)
  `s4_query_cost.py` the d0 timing and `LBA-G1`(b), one process per arm

`metadata_ratio`, from §4's calibration block: the median peak of a `GraphStore`-only load of
`graph-lux4.bin` divided by the same for `graph-msw-tu50.bin`. The pair is IDENTICAL in artist
count and CSR entries (58,838 / 1,315,684, both sidecars) and differs only in the three `LUX-4`
additive keys, so the ratio isolates the metadata term. It is MEASURED because resident cost does
not track bytes: `GraphStore` holds those keys as Python `list[str]` and `list[dict]` while the CSR
arrays stay as numpy.

`framework_rss`, from stage 1 §4 — and the DECOMPOSITION, never the single figure:

    42,680,320 B constant + 23.5 B x N

because `ArtistSearch.__init__` holds one normalised Python string per artist (`search.py:27`), so
the term grows with exactly the arms `LBA-G1` exists to test. Stage 1 records the per-artist figure
as a median of three repeats spanning 0.29-1.45 MB and says to treat it as AN ORDER OF MAGNITUDE,
not a precise rate.

    projected shipped peak RSS = median GraphStore-load peak x metadata_ratio + framework_rss(N)

⚠ The multiplicand is the `GraphStore` LOAD peak, NOT `LBA-G2`'s BUILD peak. §4: "the raw census
figure is never compared with `LBA-G1`(a)'s bar directly."

⚠ `LBA-X8`: every size figure here is a LOWER BOUND on a shipped artifact. Arms build with
`require_fame=False` and without clip ids, so their bytes and their resident cost omit the five
additive keys a shipped artifact carries. `metadata_ratio` is what carries them back, and it was
calibrated on THREE of those five keys, not all five — so the projection is itself a lower bound on
the shipped cost, stated here rather than discovered later.

⚠ `LBA-AM1-O1`: the cap rule bounds every arm by its population, so this statistic moves far more
with the POPULATION column than with the threshold column. `LBA-G1` is in practice a population
gate. It is not degenerate, but a `V`-row null here is NOT evidence that the threshold does not
affect size.

    uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_sizing.py
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))

from s4_common import bare_size_of_artifact, sha256_of  # noqa: E402

ARTIFACTS = Path(r"C:\unsung-fast\lbd-artifacts")
BOOT = HERE / "_boot"

# Stage 1 §4's decomposition. Constant part and per-artist part, never the single 42.0 MiB figure.
FRAMEWORK_RSS_CONSTANT_B = 42_680_320
FRAMEWORK_RSS_PER_ARTIST_B = 23.5

LBA_G1A_BAR_B = int(1.6 * 1000**3)  # 1.6 GB, 80 % of the App Runner instance's 2 GB

ARMS = ["LBA-A1", "LBA-A2", "LBA-A3", "LBA-A4", "LBA-A5", "LBA-A6", "LBA-A7", "LBA-A8", "LBA-A9"]
REUSED = {"LBA-A1", "LBA-A3"}
PLAIN = {
    "LBA-A1": "the artists the app serves today, connected by our own recomputation at the same "
              "strength bar ListenBrainz used",
    "LBA-A2": "the same artists, but a connection is kept when three different people's listening "
              "supports it instead of four",
    "LBA-A3": "the same artists, but two people are enough",
    "LBA-A4": "every artist the deeper crawl found, at ListenBrainz's own bar",
    "LBA-A5": "every artist the deeper crawl found, at the three-listener bar",
    "LBA-A6": "every artist the deeper crawl found, at the two-listener bar",
    "LBA-A7": "every artist anywhere in ListenBrainz's listening data who gets a connection at "
              "ListenBrainz's own bar — not just the ones our crawl happened to discover",
    "LBA-A8": "the same, at the three-listener bar",
    "LBA-A9": "the same, at the two-listener bar",
}
RULE = {"LBA-A1": "V", "LBA-A2": "V", "LBA-A3": "V", "LBA-A4": "P", "LBA-A5": "P", "LBA-A6": "P",
        "LBA-A7": "U", "LBA-A8": "U", "LBA-A9": "U"}
FILTER = {"V": "on, inert (20260805)", "P": "on, inert (20260809)", "U": "off, uncensused"}


def peaks_for(label: str) -> list[int]:
    files = sorted(BOOT.glob(f"{label}_r*.json"))
    return [json.loads(f.read_text(encoding="utf-8"))["process_peak_after_load"] for f in files]


def framework_rss(n_artists: int) -> int:
    return int(FRAMEWORK_RSS_CONSTANT_B + FRAMEWORK_RSS_PER_ARTIST_B * n_artists)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "s4_sizing.json")
    args = ap.parse_args(argv)

    # --- metadata_ratio, the calibration -------------------------------------------------------
    lux4, served = peaks_for("CAL-lux4"), peaks_for("CAL-served")
    if len(lux4) < 3 or len(served) < 3:
        raise SystemExit(f"REFUSING: metadata_ratio needs three repeats of each; have "
                         f"{len(lux4)} lux4 and {len(served)} served")
    lux4_med, served_med = statistics.median(lux4), statistics.median(served)
    metadata_ratio = lux4_med / served_med
    calibration = {
        "definition": "median GraphStore-only load peak of graph-lux4.bin / the same for "
                      "graph-msw-tu50.bin — identical in N and CSR entries, differing only in the "
                      "three LUX-4 additive keys",
        "lux4_peaks_b": lux4, "lux4_median_b": lux4_med,
        "served_peaks_b": served, "served_median_b": served_med,
        "metadata_ratio": round(metadata_ratio, 5),
        "covers": "three of the five additive keys (spotify_ids, apple_ids, artist_facts). It does "
                  "NOT cover deezer_ids or fame_lb, so the projection below is a LOWER bound on a "
                  "shipped artifact's resident cost — LBA-X8, in the memory dimension",
        "framework_rss_decomposition_b": {"constant": FRAMEWORK_RSS_CONSTANT_B,
                                          "per_artist": FRAMEWORK_RSS_PER_ARTIST_B,
                                          "source": "stage 1 README §4; the per-artist term is a "
                                                    "median of three spanning 0.29-1.45 MB and is "
                                                    "an order of magnitude, not a precise rate"},
    }
    print(f"[sizing] metadata_ratio = {metadata_ratio:.5f}  "
          f"(lux4 {lux4_med / 1024**2:.1f} MiB / served {served_med / 1024**2:.1f} MiB)", flush=True)

    # --- per arm ---------------------------------------------------------------------------------
    rows = []
    for arm in ARMS:
        build_json = HERE / f"s4_build_{arm.removeprefix('LBA-')}.json"
        stopped = False
        if arm not in REUSED:
            if not build_json.exists():
                print(f"[sizing] {arm}: no build record — skipped", flush=True)
                continue
            record = json.loads(build_json.read_text(encoding="utf-8"))
            stopped = record.get("status") == "unbuilt for a resource reason"
            if stopped:
                rows.append({"arm": arm, "plain_sentence": PLAIN[arm], "population_rule": RULE[arm],
                             "filter": FILTER[RULE[arm]], "status": "unbuilt for a resource reason",
                             "stopped_by": "LBA-G2", "projection": record.get("projection"),
                             "barred_conclusions": record.get("barred_conclusions"),
                             "lba_m1": None, "lba_g1": None})
                print(f"[sizing] {arm}: unbuilt for a resource reason — LBA-M1 unread", flush=True)
                continue

        # EVERY arm is measured on its BARE re-serialisation, the two reused ones and the seven
        # built ones alike. `require_fame=False` removes FAME ONLY — `deezer_ids` and the three
        # `LUX-4` keys load from frozen package data rather than a fetch — so a census build
        # carries four of the five additive keys, and the two reused arms' artifacts carry all
        # five. Applying `metadata_ratio` to either would scale metadata that is ALREADY THERE,
        # double-counting the very term the ratio was calibrated to measure.
        #
        # This is the same treatment §4 already fixes for the bytes half — bare by decoding, then
        # "reported beside the shipped projection = bare + the measured per-node additive cost" —
        # applied to the memory half so the two halves are consistent. It is not a new bar: the
        # 1.6 GB bar and the expression are untouched.
        artifact = ARTIFACTS / f"{arm}-bare.bin"
        bare = bare_size_of_artifact(artifact)
        if bare["additive_keys_present"]:
            raise SystemExit(f"REFUSING: {artifact.name} carries additive keys — not comparable")

        peaks = peaks_for(arm)
        if len(peaks) < 3:
            raise SystemExit(f"REFUSING: {arm} has {len(peaks)} boot repeats, needs three")
        boot_median = statistics.median(peaks)
        n = bare["artists"]
        fw = framework_rss(n)
        projected = boot_median * metadata_ratio + fw
        fires_a = projected > LBA_G1A_BAR_B

        qc_path = HERE / f"s4_query_cost_{arm}.json"
        qc = json.loads(qc_path.read_text(encoding="utf-8")) if qc_path.exists() else None

        row = {
            "arm": arm,
            "plain_sentence": PLAIN[arm],
            "population_rule": RULE[arm],
            "population_rule_exposure": ("LBA-X6 — U's membership moves with the threshold, so the "
                                         "population is a DEPENDENT variable on this row"
                                         if RULE[arm] == "U" else None),
            "filter": FILTER[RULE[arm]],
            "reused": arm in REUSED,
            "artifact_measured": str(artifact),
            "artifact_sha256": sha256_of(artifact),
            "lba_m1": {
                "artists": n,
                "csr_entries": bare["csr_entries"],
                "connections_each_counted_once": bare["csr_entries"] // 2,
                "bare_artifact_bytes": bare["bare_artifact_bytes"],
                "bare_artifact_mb": round(bare["bare_artifact_bytes"] / 1e6, 2),
                "shipped_projection_bytes": int(bare["bare_artifact_bytes"] * metadata_ratio),
                "boot_peak_repeats_b": peaks,
                "boot_peak_median_b": boot_median,
                "boot_peak_median_mib": round(boot_median / 1024**2, 2),
                "framework_rss_b": fw,
                "projected_shipped_peak_rss_b": int(projected),
                "projected_shipped_peak_rss_mib": round(projected / 1024**2, 2),
                "query_cost": qc["arm"] if qc else None,
                "served_query_cost": qc["served"] if qc else None,
            },
            "lba_g1": {
                "a_projected_shipped_peak_rss_b": int(projected),
                "a_bar_b": LBA_G1A_BAR_B,
                "a_bar": "1.6 GB",
                "a_fires": fires_a,
                "b_ratio_p50": qc["lba_g1b"]["ratio_p50"] if qc else None,
                "b_bar": 2.0,
                "b_fires": qc["lba_g1b"]["fires"] if qc else None,
                "fires": bool(fires_a or (qc and qc["lba_g1b"]["fires"])),
                "consequence_if_fired": ("the arm REQUIRES A HOSTING OR ROUTER CHANGE before it "
                                         "could ship, and that requirement is named in every "
                                         "sentence about it. It stops nothing and the other "
                                         "measurements are still taken."),
            },
        }
        rows.append(row)
        print(f"[sizing] {arm}: {n:,} artists  {bare['csr_entries']:,} CSR  "
              f"bare {bare['bare_artifact_bytes'] / 1e6:.1f} MB  "
              f"boot {boot_median / 1024**2:.1f} MiB  "
              f"projected {projected / 1024**2:.1f} MiB  G1(a) fires={fires_a}"
              + (f"  G1(b) ratio {qc['lba_g1b']['ratio_p50']:.3f} fires={qc['lba_g1b']['fires']}"
                 if qc else "  (no query cost yet)"), flush=True)

    out = {
        "task": "LBA-M1 — map size and what it costs to serve; LBA-G1 read on every built arm",
        "calibration": calibration,
        "arms": rows,
        "bars": {
            "LBA-G1(a)": "projected shipped peak RSS > 1.6 GB (80 % of the App Runner instance's 2 GB)",
            "LBA-G1(b)": "the arm's median d0 query wall-clock > 2x the served map's, same process, "
                         "same pair set; the gate reads the MEDIAN alone and p95 is reported beside it",
        },
        "standing_exposures": {
            "LBA-X8": "every size figure here is a LOWER bound on a shipped artifact: these builds "
                      "carry no fame and no clip ids, and metadata_ratio carries back only three of "
                      "the five additive keys",
            "LBA-AM1-O1": "the cap bounds every arm by its population, so LBA-G1 is in practice a "
                          "POPULATION gate; a V-row null is not evidence the threshold does not "
                          "affect size",
            "LBA-AM1-O4": "the served map's local median d0 was on no document; LBA-M1 supplies it "
                          "as a by-product of its own ratio",
        },
        "not_taken_here": ["LBA-M2", "LBA-M3", "LBA-M4", "LBA-M5"],
        "script_sha256": sha256_of(Path(__file__)),
        "written_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[sizing] wrote {args.out.name}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
