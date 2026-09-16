"""`LBA-M5` -- what it costs to operate.

PLAIN SENTENCE (section 4): how long does one refresh take, how much disk does it need, and what
exactly would somebody have to run?

REPORTED DESCRIPTIVELY, NO THRESHOLD.

> ⚠ `LBA-AM1-O2`: THIS MEASUREMENT ADDS NO ARM-DISCRIMINATING INFORMATION BEYOND `LBA-M1`'s
> ARTIST COUNT, and no read may treat it as independent evidence about an arm. Parts 1 and 3 are
> IDENTICAL ACROSS ALL EIGHT ARMS -- one pass over one shared table, one corpus. Part 4 is a
> deliverable rather than a measurement. Only part 2 varies, and it is a deterministic function
> of `LBA-M1`'s N. It is a cost statement about a CANDIDATE, not a comparison between candidates.

FOUR PARTS.

  1. THE SIMILARITY PASS -- CITED, NEVER RE-RUN AND NEVER RE-TIMED HERE. The `LBD-A0` pass's
     stage timings, spill and combine are owned by `../2026-09-08-lbd-similarity/README.md`
     section 4; the `LBD-A4` pass's by `../2026-09-13-lbd-a4/README.md` section 4; the hardware
     context -- the dump on a spinning disk and DuckDB's thread-count trap -- by section 4 of
     the first. What a refresh adds over today's pipeline AT THE SERVED POPULATION is this pass
     and nothing else: the archive replay is a cost the pipeline already pays, and its wall
     clocks are owned by `../2026-09-10-lbd-supply/README.md` sections 1 and 2.
     ⚠ AT ANY POPULATION ABOVE `V` THAT SENTENCE NO LONGER HOLDS -- section 6's steps 6 and 7,
     the re-census and the fame fetch, are additional (`LBA-AM1-O3` corrected an internal
     contradiction on exactly this point).

  2. THE FAME FETCH -- ESTIMATED, method fixed in section 4 before any result existed:
     ceil(N / 1000) x (0.2 s + one round trip), N being the arm's measured artist count.
     `MAX_PER_REQUEST = 1000` is the endpoint's own truncation limit (`fame.py:57`) and
     `request_delay_seconds` = 1 / `requests_per_second` = 1 / 5.0 = 0.2 s
     (`builder/.../config.py:74,289-290` -- THE BUILDER'S, not the API's; both packages have a
     `config.py`).
     ⚠ THE ROUND TRIP IS NOT RECOVERABLE EXACTLY FROM THE RECORD, and that is stated rather than
     invented. The one measured fame run on the record took 78 s
     (`docs/superpowers/2026-08-09-cex-task11-execution-log.md` section 6) but THAT LOG DOES NOT
     STATE THE POPULATION IT COVERED. It was one of the two populations that session handled, so
     the per-batch figure is BRACKETED between them rather than asserted -- the same treatment
     `LBA-AM1` gave `framework_rss`: name the missing input, do not guess it.
     THE STAGE IS RESUMABLE, so a refresh pays only for artists with no record. That is the
     difference between a first build and a recurring cost, and it is why the figure below is a
     FIRST-BUILD cost.

  3. DISK AT A STATED CADENCE. The standing corpus and its annual growth, and the re-download
     cadence a deletions-matter policy implies, are the own-similarity design's section 8 and
     are cited from there. The pinned dump's own size and file count are owned by Task 1's
     README section 1. THE CADENCE IS A POLICY CHOICE, NOT A MEASUREMENT: the procedure is
     written for a MONTHLY full refresh, and a different cadence changes only step 1's
     frequency.

  4. THE REFRESH PROCEDURE -- section 6's ten numbered steps, which is the deliverable. It is
     prose and lives in the stage-3 README rather than in this script's JSON.

    python -u s3_m5.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import s3_common as C

HERE = Path(__file__).resolve().parent

MAX_PER_REQUEST = 1000          # fame.py:57, the endpoint's own truncation limit
REQUESTS_PER_SECOND = 5.0       # builder config.py:74
DELAY_S = 1.0 / REQUESTS_PER_SECOND

# The one measured fame run on the record, and the two populations that session handled. The log
# does not say which the 78 s covered, so the per-batch cost is bracketed across both.
MEASURED_FAME_SECONDS = 78.0
MEASURED_FAME_POPULATION_BRACKET = (88_685, 117_302)


def main() -> None:
    lo_pop, hi_pop = MEASURED_FAME_POPULATION_BRACKET
    lo_batches = math.ceil(lo_pop / MAX_PER_REQUEST)
    hi_batches = math.ceil(hi_pop / MAX_PER_REQUEST)
    # More batches for the same 78 s means less time per batch, so the bracket inverts.
    per_batch_hi = MEASURED_FAME_SECONDS / lo_batches
    per_batch_lo = MEASURED_FAME_SECONDS / hi_batches
    rt_lo = max(0.0, per_batch_lo - DELAY_S)
    rt_hi = max(0.0, per_batch_hi - DELAY_S)
    print(f"[m5] measured fame run {MEASURED_FAME_SECONDS:.0f} s over a population between "
          f"{lo_pop:,} and {hi_pop:,}")
    print(f"[m5] => {per_batch_lo:.3f}-{per_batch_hi:.3f} s per batch; round trip "
          f"{rt_lo:.3f}-{rt_hi:.3f} s on top of the fixed {DELAY_S} s pause")

    arms = {}
    for arm, meta in C.ARMS.items():
        store = C.load_arm(arm)
        n = len(store.mbids)
        batches = math.ceil(n / MAX_PER_REQUEST)
        arms[arm] = {
            "arm": arm,
            "sentence": C.SENTENCE[arm],
            "population_rule": meta["rule"],
            "threshold": meta["threshold"],
            "artist_count_source": "stage 2 README section 3b owns N; reproduced here from the "
                                   "artifact as this script's own green check",
            "batches": batches,
            "floor_seconds_rate_limit_only": round(batches * DELAY_S, 1),
            "first_build_seconds_estimate_range": [round(batches * (DELAY_S + rt_lo), 1),
                                                   round(batches * (DELAY_S + rt_hi), 1)],
            "resumable": True,
            "note": "FIRST-BUILD cost. The stage is resumable, so a refresh pays only for "
                    "artists with no record.",
        }
        print(f"[m5] {arm} ({meta['rule']}): {batches} batches, "
              f"{arms[arm]['first_build_seconds_estimate_range'][0]:.0f}-"
              f"{arms[arm]['first_build_seconds_estimate_range'][1]:.0f} s")

    C.write_json(HERE / "s3_m5.json", {
        "measurement": "LBA-M5 -- what it costs to operate. Descriptive, no threshold.",
        "LBA-AM1-O2": ("adds no arm-discriminating information beyond LBA-M1's artist count. "
                       "Parts 1 and 3 are identical across all eight arms; part 4 is a "
                       "deliverable; part 2 is a deterministic function of N. A cost statement "
                       "about a CANDIDATE, not a comparison between candidates."),
        "part1_similarity_pass": {
            "rule": "CITED, never re-run and never re-timed here",
            "owners": [
                "builder/analysis/2026-09-08-lbd-similarity/README.md section 4 (LBD-A0 pass "
                "timings, spill, combine; and the hardware context)",
                "builder/analysis/2026-09-13-lbd-a4/README.md section 4 (LBD-A4 pass)",
                "builder/analysis/2026-09-10-lbd-supply/README.md sections 1 and 2 (the archive "
                "replay wall clocks, a cost the pipeline already pays)",
            ],
            "at_the_served_population": "a refresh adds this pass and nothing else",
            "above_V": "section 6's steps 6 and 7 -- the re-census and the fame fetch -- are "
                       "ADDITIONAL (LBA-AM1-O3)",
        },
        "part2_fame_fetch": {
            "method": "ceil(N / 1000) x (0.2 s + one round trip), fixed in section 4 before any "
                      "result existed",
            "MAX_PER_REQUEST": MAX_PER_REQUEST,
            "requests_per_second": REQUESTS_PER_SECOND,
            "request_delay_seconds": DELAY_S,
            "round_trip_seconds_bracket": [round(rt_lo, 3), round(rt_hi, 3)],
            "round_trip_basis": ("the one measured fame run on the record, 78 s "
                                 "(2026-08-09-cex-task11-execution-log.md section 6). THAT LOG "
                                 "DOES NOT STATE THE POPULATION IT COVERED, so the per-batch "
                                 "figure is bracketed across the two populations that session "
                                 "handled rather than asserted."),
            "arms": arms,
        },
        "part3_disk": {
            "rule": "cited, not measured here",
            "owners": ["docs/superpowers/specs/2026-09-06-own-similarity-design.md section 8 "
                       "(the standing corpus, its annual growth, and the re-download cadence a "
                       "deletions-matter policy implies)",
                       "builder/analysis/2026-09-07-lbd-inputs/README.md section 1 (the pinned "
                       "dump's own size and file count)"],
            "cadence": "MONTHLY full refresh -- A POLICY CHOICE, NOT A MEASUREMENT. A different "
                       "cadence changes only step 1's frequency.",
        },
        "part4_refresh_procedure": "section 6's ten steps; prose, in the stage-3 README section 5",
    }, __file__)


if __name__ == "__main__":
    main()
