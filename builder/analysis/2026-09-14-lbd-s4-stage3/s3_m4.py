"""`LBA-M4` -- playability. ESTIMATED on every arm, and the report says so wherever it appears.

PLAIN SENTENCE (section 4): of the artists in this map, and of the ones it adds beyond what the
app serves today, what share would the un-listenable rule throw out -- and how confident is that
number?

WHY EVERYTHING HERE IS AN ESTIMATE. `LBA-G3` FIRED AT STAGE 1: the projected offline census pass
is multiples of its 6-hour bar, so THE PASS IS NOT STARTED AND NONE IS OWED. Every verdict below
is CARRIED from an earlier census, against an EARLIER MusicBrainz snapshot than the pinned
`20260905-002519` one. Section 4 reserves the word "exact" for freshly evaluated artists, and
after `LBA-G3` THERE IS NO FRESH SHARE AT ALL -- on any arm. The split by verdict source is
reported anyway, precisely so that zero is visible rather than inferred.

THE CLASS is `ULC-D2`: no sole-credited substantial release group. It is read from the coverage
store's `d2` field, where True means IN the class (`ulf_census.py`: `rec["d2"] = substantial[m]
== 0`). THE STORE IS READ AND NEVER WRITTEN HERE, and its sha256 is recorded before and after to
prove it -- it is ACTIVE data that the census scripts read AND write, so "we did not touch it" is
a claim that has to be evidenced rather than asserted.

THE DROP is class share x the within-class drop rate the two committed censuses measured, and
BOTH RATES ARE REPORTED AS A RANGE RATHER THAN AVERAGED, because they were taken on different
populations. Their figures are owned by the two census payloads and are read from them here
rather than transcribed.

THREE BOUNDS, all stated beside every figure (`LBA-X2`, section 4):

  1. IT IS AN OVER-ESTIMATE of what the app genuinely cannot play, by `ULC-F4`'s mechanism: the
     keep-check's criterion is the NAME-search route while the app resolves IDENTITY FIRST, so
     the rule can call an artist unlistenable whom the app would play on its first attempt. The
     size of that over-drop on the two committed payloads is owned by the LUX-E1 drift-source
     README section 6.2; ON `U` IT IS UNBOUNDED, because nobody has measured it there.
  2. THE CARRIED VERDICTS ARE UN-RE-RUN. Both committed payloads carry drop verdicts inherited
     from the earlier no-release and featured-credit rules, holding no clip record. Unmeasured,
     not zero.
  3. THE WITHIN-CLASS DROP RATE IS BEING EXTRAPOLATED OUTSIDE THE POPULATIONS IT WAS MEASURED
     ON. Reporting both rates as a range is honest about their spread; it is NOT a control for
     applying either to `U`, and no sentence may treat it as one.

`LBA-AM3-3` -- COVERAGE IS UNEVEN ACROSS THE LATTICE, and the split falls exactly on the arms
this measurement exists to size. On `LBA-A1`-`A6` stage 1 section 2 measured ZERO population
members absent from the store, so the class share is carried-measured over a COMPLETE population
and only the drop is extrapolated. On `LBA-A7`/`A8` a large majority of the population is absent
from the store entirely, and the store's own rule is "absence of a field means UNKNOWN, never
false" -- so there BOTH the class share and the drop are extrapolated, over a population most of
which no census has ever evaluated. EVERY TABLE CARRIES A COVERAGE COLUMN PER ARM, and no
sentence compares a `U`-row class share with a `V`- or `P`-row one as though both were measured
on the same basis.

`LBA-G4`, and `LBA-AM3-2`'s disqualifier. The gate fires when the class share over
`nodes(arm) - V` exceeds the class share over `nodes(arm) & V` by >= 10 PERCENTAGE POINTS --
within the arm, which is where `LBA-AM1-A5` moved the baseline. Section 5 requires both shares
from the SAME CENSUS PASS, THE SAME DUMP AND THE SAME ARM; with no pass run, the "same arm" half
holds and the "same pass, same dump" half does not. So `LBA-AM3-2` measures the residual
confound instead of arguing about it: THE VERDICT-SOURCE MIX OF BOTH SUBSETS IS REPORTED BESIDE
THE GATE, and if their shares of `cex-recensus-2026-08-09`-sourced verdicts DIFFER BY >= 10
PERCENTAGE POINTS the gate is REPORTED UNREADABLE for that arm -- only the two class shares,
descriptively, with the mix beside them. The disqualifier can only ever WITHHOLD a gate result,
never produce one. `LBA-G4` is `n/a` on the `V` row, NOT zero: its subject is the artists an arm
adds beyond `V`, and for a `V` arm that set is empty -- a share of nothing, not a share of zero,
and printing 0 would read as PERFECTLY PLAYABLE.

EFFECT SIZE: `LBA-G4`'s 10 points, on the ADDED half only. The whole-population share is
reported descriptively, no threshold.

    python -u s3_m4.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import s3_common as C

HERE = Path(__file__).resolve().parent
STORE = C.REPO / "builder" / "analysis" / "census-coverage" / "ulf_coverage.json"
PAYLOADS = {
    "ulc/ulf-census-2026-08-05":
        C.REPO / "builder" / "src" / "artistpath_builder" / "data"
        / "unlistenable_drop_algb_20260805.json",
    "cex-recensus-2026-08-09":
        C.REPO / "builder" / "src" / "artistpath_builder" / "data"
        / "unlistenable_drop_algb_20260809.json",
}
# `LBA-AM3-2`'s disqualifier is written against this source specifically.
AM3_SRC = "cex-recensus-2026-08-09"
G4_BAR_PP = 10.0
AM3_DISQUALIFIER_PP = 10.0


def class_stats(mbids, artists: dict) -> dict:
    """Class share over the COVERED part, with the coverage that produced it beside it.

    The share is never computed over the whole set as though absence were a verdict: the store's
    own rule is that absence of a field means UNKNOWN, never false.
    """
    covered = [m for m in mbids if "d2" in artists.get(m, {})]
    in_class = [m for m in covered if artists[m]["d2"] is True]
    src = {}
    for m in covered:
        s = artists[m].get("d2_src", "unrecorded")
        src[s] = src.get(s, 0) + 1
    n = len(mbids)
    return {
        "n": n,
        "covered": len(covered),
        "coverage_share": round(len(covered) / n, 6) if n else None,
        "in_class_of_covered": len(in_class),
        "class_share_of_covered": round(len(in_class) / len(covered), 6) if covered else None,
        "verdict_source_mix_of_covered": {k: round(v / len(covered), 6) for k, v in
                                          sorted(src.items())} if covered else {},
        "verdict_source_counts": dict(sorted(src.items())),
        "freshly_evaluated_against_pinned_dump": 0,
    }


def main() -> None:
    t0 = time.time()
    before = C.sha256_of(STORE)
    store = json.loads(STORE.read_text("utf-8"))
    artists = store["artists"]
    print(f"[m4] coverage store {len(artists):,} artists, sha256 {before[:16]}...")
    print(f"[m4] store status: {store['status']}")

    drop_rates = {}
    for label, path in PAYLOADS.items():
        c = json.loads(path.read_text("utf-8"))["counts"]
        drop_rates[label] = {"class": c["class"], "drop": c["drop"],
                             "within_class_drop_rate": round(c["drop"] / c["class"], 6),
                             "source": path.name}
    lo = min(v["within_class_drop_rate"] for v in drop_rates.values())
    hi = max(v["within_class_drop_rate"] for v in drop_rates.values())
    print(f"[m4] within-class drop rate range (NEVER averaged): {lo:.4f} - {hi:.4f}")

    v_set = set(C.read_mbid_file(C.POP_V))
    arms = {}
    for arm, meta in C.ARMS.items():
        t = time.time()
        store_g = C.load_arm(arm)
        nodes = list(store_g.mbids)
        kept = [m for m in nodes if m in v_set]
        added = [m for m in nodes if m not in v_set]

        whole = class_stats(nodes, artists)
        row = {
            "arm": arm,
            "sentence": C.SENTENCE[arm],
            "population_rule": meta["rule"],
            "threshold": meta["threshold"],
            "filter": meta["filter"],
            "whole_population_DESCRIPTIVE_no_threshold": whole,
            "estimated_drop_share_of_whole_population": (
                None if whole["class_share_of_covered"] is None else
                [round(whole["class_share_of_covered"] * lo, 6),
                 round(whole["class_share_of_covered"] * hi, 6)]),
            "kept_from_V": class_stats(kept, artists),
            "added_beyond_V": class_stats(added, artists),
            "basis": ("class share carried-measured over a COMPLETE population; only the drop "
                      "is extrapolated (stage 1 section 2 measured zero uncovered)"
                      if meta["rule"] in ("V", "P") else
                      "BOTH the class share and the drop are extrapolated, over a population "
                      "most of which no census has ever evaluated (LBA-AM3-3)"),
        }

        # `LBA-G4`, within the arm, on the estimate.
        a, k = row["added_beyond_V"], row["kept_from_V"]
        if a["n"] == 0:
            row["LBA-G4"] = {"result": "n/a",
                            "why": ("the gate's subject is the artists this arm adds beyond V, "
                                    "and on a V arm that set is EMPTY -- a share of nothing, "
                                    "not a share of zero (LBA-AM1-A5). Printing 0 would read as "
                                    "perfectly playable, which is the opposite of not measured")}
        else:
            mix_a = a["verdict_source_mix_of_covered"].get(AM3_SRC, 0.0)
            mix_k = k["verdict_source_mix_of_covered"].get(AM3_SRC, 0.0)
            skew_pp = round(100 * abs(mix_a - mix_k), 4)
            delta_pp = round(100 * (a["class_share_of_covered"] - k["class_share_of_covered"]), 4)
            unreadable = skew_pp >= AM3_DISQUALIFIER_PP
            row["LBA-G4"] = {
                "added_class_share_of_covered": a["class_share_of_covered"],
                "kept_class_share_of_covered": k["class_share_of_covered"],
                "delta_pp": delta_pp,
                "bar_pp": G4_BAR_PP,
                f"{AM3_SRC}_share_added": round(mix_a, 6),
                f"{AM3_SRC}_share_kept": round(mix_k, 6),
                "provenance_skew_pp": skew_pp,
                "disqualifier_bar_pp": AM3_DISQUALIFIER_PP,
                "result": ("UNREADABLE for this arm (LBA-AM3-2): the two subsets draw from the "
                           "censuses in materially different proportions, so a dump column has "
                           "re-entered a comparison LBA-AM1-A5 made one column wide. Only the "
                           "two class shares stand, descriptively, with the mix beside them"
                           if unreadable else
                           ("FIRES (ESTIMATE)" if delta_pp >= G4_BAR_PP
                            else "does not fire (ESTIMATE)")),
                "label": "ESTIMATE -- no census pass was run; every verdict is carried",
            }
        arms[arm] = row
        g4 = row["LBA-G4"].get("result")
        print(f"[m4] {arm} ({meta['rule']}) coverage {whole['coverage_share']:.4f} "
              f"class(covered) {whole['class_share_of_covered']:.4f}  LBA-G4: {g4[:38]}"
              f" ({time.time() - t:.1f}s)")

    after = C.sha256_of(STORE)
    if before != after:
        raise SystemExit("REFUSING: the coverage store changed during this read. It is ACTIVE "
                         "data and this stage must not write it.")
    print(f"[m4] coverage store unchanged: {after[:16]}...")

    C.write_json(HERE / "s3_m4.json", {
        "measurement": "LBA-M4 -- playability, ESTIMATED on every arm",
        "why_estimated": ("LBA-G3 fired at stage 1: the projected offline census pass is "
                          "multiples of its 6-hour bar, so no pass was started and none is "
                          "owed. Every verdict is carried, against an earlier MusicBrainz "
                          "snapshot than the pinned 20260905-002519 one. There is NO freshly "
                          "evaluated artist on any arm."),
        "coverage_store": {"path": str(STORE), "sha256_before": before, "sha256_after": after,
                           "artists": len(artists), "status": store["status"],
                           "written_by_this_stage": False},
        "within_class_drop_rate": {"range_never_averaged": [lo, hi], "measured": drop_rates},
        "bounds": [
            "LBA-X2(b) / ULC-F4: an OVER-estimate of what the app cannot play -- the keep-check "
            "uses the name-search route while the app resolves identity first. Sized on the two "
            "committed payloads by the LUX-E1 drift-source README section 6.2; UNBOUNDED on U.",
            "The carried verdicts are un-re-run: both payloads carry verdicts inherited from the "
            "earlier no-release and featured-credit rules, holding no clip record. Unmeasured, "
            "not zero.",
            "The within-class drop rate is extrapolated outside the populations it was measured "
            "on. The range is honest about their spread; it is NOT a control for applying either "
            "to U.",
        ],
        "arms": arms,
    }, __file__)
    print(f"[m4] done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
