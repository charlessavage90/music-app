"""RC scorer -- computes RC-G1, RC-G2 and RC-C1..RC-C4 from the collected records.

Governed by `docs/superpowers/specs/2026-07-29-reciprocity-sampling-preregistration.md`
and amendment `RC-A1`, both committed before any arm ran. Every threshold below is quoted
from that document; none is chosen here, and none may be.

Separated from `rc_run.py` so scoring is re-runnable and reviewable without touching the
service -- the AS harness's split, for the same reason.

Reads:
  ../2026-07-29-cap-selection-sim/as_raw_records.json  seed lists, both arms (RC-A1)
  rc_raw_records.json                                  sampled candidates' own lists
  ../../scratch/graph-archive                          RC-G1's 2026-07-20 comparison

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-reciprocity-sampling/rc_score.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "builder" / "src"))

RECORDS = HERE / "rc_raw_records.json"
AS_RECORDS = ROOT / "builder" / "analysis" / "2026-07-29-cap-selection-sim" / "as_raw_records.json"
ARCHIVE = ROOT / "builder" / "scratch" / "graph-archive"
OUT = HERE / "rc_scores.json"

K = 50
ARM_OF_AS_LABEL = {"ALG-E": "RC-ARM-P", "ALG-B": "RC-ARM-B"}

# RC §2 bands, in the AS stratum labels the seed records carry.
BAND_ORDER = (
    "top_0.1pct",
    "top_1pct_below_0.1pct",
    "top_decile_below_1pct",
    "pctl_50_to_90",
    "below_median",
)
BAND_PLAIN = {
    "top_0.1pct": "the very most famous artists",
    "top_1pct_below_0.1pct": "very famous artists",
    "top_decile_below_1pct": "well-known artists",
    "pctl_50_to_90": "moderately known artists",
    "below_median": "obscure artists",
}

# RC §5 RC-G2: a band is readable only at these seed counts, in BOTH arms.
G2_MIN_SEEDS = 15
G2_MIN_SEEDS_LOWER_HALF = 30
# RC §5 RC-G1: fires if more than this share of comparable seeds differ from
# their archived top-50 by more than G1_MEMBER_TOLERANCE members.
G1_SHARE_THRESHOLD = 0.10
G1_MEMBER_TOLERANCE = 5
# RC §4 thresholds. Nothing here is a judgement call; all four are quoted.
C1_MATERIAL_POINTS = 10.0
C1_NULL_POINTS = 3.0
C2_MATERIAL_RATIO = 0.5
C2_NULL_RATIO = 0.85
C3_DEGREE_FLOOR = 25.0  # == PRODUCTION_ACCEPTANCE.famous_median_degree_floor
D_HAT_STRANDED_BELOW = 2.0  # "cannot sit between two others"


def top_k(candidates: list[dict], special: set[str], k: int = K) -> list[str]:
    """Top-k by the production ordering, placeholders removed first.

    `mutual_knn_cap` ranks on unclipped strengths, ties on lowest MBID; at
    damping 0.0 that is monotone in the raw score (pipeline.py:218-226). The
    filter is applied BEFORE the cut, as `build_from_archive` does.
    """
    kept = [c for c in candidates if c["mbid"] not in special]
    kept.sort(key=lambda c: (-float(c["score"]), c["mbid"]))
    return [c["mbid"] for c in kept[:k]]


def main() -> int:
    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.pipeline import is_special_purpose
    from artistpath_builder.sources.listenbrainz import ListenBrainzSource

    data = json.loads(RECORDS.read_text(encoding="utf-8"))
    as_data = json.loads(AS_RECORDS.read_text(encoding="utf-8"))
    source = ListenBrainzSource(BuilderConfig())

    identities: dict[str, list[str]] = data.get("identities", {})
    special = {
        mbid
        for mbid, (_name, comment) in identities.items()
        if is_special_purpose(comment)
    }
    print(f"placeholder entities identified: {len(special)} "
          f"(identity known for {len(identities)} mbids)", flush=True)

    # Seed candidate lists, per arm, straight from the AS records.
    seed_lists: dict[str, dict[str, list[dict]]] = {"RC-ARM-P": {}, "RC-ARM-B": {}}
    seed_meta: dict[str, dict] = {}
    for entry in as_data["records"]:
        arm = ARM_OF_AS_LABEL.get(str(entry["arm"]))
        if arm is None or entry.get("status") != 200 or "candidates" not in entry:
            continue
        seed_lists[arm][str(entry["mbid"])] = entry["candidates"]
        seed_meta[str(entry["mbid"])] = {
            "name": entry["name"],
            "stratum": entry["stratum"],
            "own_pctl": entry["own_pctl"],
        }

    seeds = data["seeds"]
    candidate_lists = data["candidate_lists"]

    # --- RC-G1: archive drift, free ----------------------------------------
    # Compares AS's live production seed lists (2026-07-29) against the archived
    # responses for the same artists (2026-07-20). Only RC-ARM-P's candidate
    # lists come from the archive, so this is the exposure that matters.
    drift_compared = 0
    drift_differing = 0
    drift_detail: list[dict] = []
    for mbid, live in sorted(seed_lists["RC-ARM-P"].items()):
        path = ARCHIVE / "similar" / source.name / f"{mbid}.json"
        if not path.is_file():
            continue
        try:
            archived = source.parse(path.read_bytes(), exclude_mbid=mbid)
        except ValueError:
            continue
        live_top = set(top_k(live, special))
        arch_top = set(
            top_k([{"mbid": n.mbid, "score": n.score} for n in archived], special)
        )
        # Members of today's top-50 absent from the archived one. Directional on
        # purpose: it answers "how much of what the service says now is missing
        # from what we saved", which is the exposure RC-ARM-P carries. An empty
        # side counts as fully changed rather than as agreement.
        if not live_top or not arch_top:
            changed = K
        else:
            changed = len(live_top - arch_top)
        drift_compared += 1
        if changed > G1_MEMBER_TOLERANCE:
            drift_differing += 1
        drift_detail.append({"mbid": mbid, "members_changed": changed})

    drift_share = drift_differing / drift_compared if drift_compared else None
    g1_fired = bool(drift_share is not None and drift_share > G1_SHARE_THRESHOLD)
    print(
        f"RC-G1: {drift_differing}/{drift_compared} seeds differ from their archived "
        f"top-50 by more than {G1_MEMBER_TOLERANCE} members "
        f"({'FIRED' if g1_fired else 'not fired'})",
        flush=True,
    )

    # --- per-seed count, rate, degree --------------------------------------
    per_seed: dict[str, dict[str, dict]] = {"RC-ARM-P": {}, "RC-ARM-B": {}}
    dropped_placeholder = {"RC-ARM-P": 0, "RC-ARM-B": 0}
    unresolved_candidate = {"RC-ARM-P": 0, "RC-ARM-B": 0}

    for arm in ("RC-ARM-P", "RC-ARM-B"):
        for mbid, rec in sorted(seeds.items()):
            own = seed_lists[arm].get(mbid)
            if own is None:
                continue
            pool = top_k(own, special)
            n_cand = len(pool)

            drawn = [c for c in rec["arms"][arm]["sampled"] if c in pool]
            dropped_placeholder[arm] += len(rec["arms"][arm]["sampled"]) - len(drawn)

            reciprocating = 0
            usable = 0
            for v in drawn:
                v_rec = candidate_lists[arm].get(v)
                if not v_rec or v_rec.get("status") != 200 or "candidates" not in v_rec:
                    unresolved_candidate[arm] += 1
                    continue
                usable += 1
                if mbid in top_k(v_rec["candidates"], special):
                    reciprocating += 1

            if not usable:
                continue
            recip = reciprocating / usable
            per_seed[arm][mbid] = {
                "stratum": rec["stratum"],
                "name": rec["name"],
                "n_cand": n_cand,
                "recip": round(recip, 4),
                "d_hat": round(n_cand * recip, 3),
                "sampled_usable": usable,
                "sampled_exhaustive": bool(rec["arms"][arm].get("sampled_is_exhaustive")),
            }

    # --- RC-G2: band sufficiency -------------------------------------------
    bands: dict[str, dict] = {}
    for band in BAND_ORDER:
        in_both = [
            mbid
            for mbid in per_seed["RC-ARM-P"]
            if mbid in per_seed["RC-ARM-B"]
            and per_seed["RC-ARM-P"][mbid]["stratum"] == band
        ]
        floor = G2_MIN_SEEDS_LOWER_HALF if band == "below_median" else G2_MIN_SEEDS
        readable = len(in_both) >= floor
        row: dict = {
            "plain": BAND_PLAIN[band],
            "seeds_in_both_arms": len(in_both),
            "rc_g2_floor": floor,
            "readable": readable,
        }
        if readable:
            for arm in ("RC-ARM-P", "RC-ARM-B"):
                vals = [per_seed[arm][m] for m in in_both]
                row[arm] = {
                    "median_n_cand": statistics.median(v["n_cand"] for v in vals),
                    "mean_recip": round(
                        statistics.mean(v["recip"] for v in vals), 4
                    ),
                    "median_d_hat": statistics.median(v["d_hat"] for v in vals),
                    "share_d_hat_below_2": round(
                        sum(1 for v in vals if v["d_hat"] < D_HAT_STRANDED_BELOW)
                        / len(vals),
                        4,
                    ),
                }
        bands[band] = row
        print(
            f"RC-G2 {band:24s} seeds={len(in_both):3d} floor={floor:2d} "
            f"{'readable' if readable else 'UNREAD -- reported, never pooled'}",
            flush=True,
        )

    # --- RC-C1..RC-C4 -------------------------------------------------------
    criteria: dict[str, dict] = {}
    lower = bands["below_median"]
    if lower["readable"]:
        c1_delta = 100.0 * (
            lower["RC-ARM-B"]["share_d_hat_below_2"]
            - lower["RC-ARM-P"]["share_d_hat_below_2"]
        )
        criteria["RC-C1"] = {
            "plain": "how many obscure artists end up with too few connections to "
                     "appear in the middle of a journey at all",
            "share_below_2_production": lower["RC-ARM-P"]["share_d_hat_below_2"],
            "share_below_2_algb": lower["RC-ARM-B"]["share_d_hat_below_2"],
            "delta_points": round(c1_delta, 2),
            "verdict": (
                "material" if c1_delta >= C1_MATERIAL_POINTS
                else "no material effect" if c1_delta < C1_NULL_POINTS
                else "indeterminate"
            ),
        }
        p_med = lower["RC-ARM-P"]["median_d_hat"]
        b_med = lower["RC-ARM-B"]["median_d_hat"]
        ratio = (b_med / p_med) if p_med else None
        criteria["RC-C2"] = {
            "plain": "whether the typical obscure artist ends up with far fewer "
                     "connections under the new setting",
            "median_d_hat_production": p_med,
            "median_d_hat_algb": b_med,
            "ratio": round(ratio, 4) if ratio is not None else None,
            "verdict": (
                "undefined (production median is zero)" if ratio is None
                else "material" if ratio <= C2_MATERIAL_RATIO
                else "no material effect" if ratio >= C2_NULL_RATIO
                else "indeterminate"
            ),
        }
    else:
        unread = "unread -- RC-G2 not met for the lower half"
        criteria["RC-C1"] = {"verdict": unread}
        criteria["RC-C2"] = {"verdict": unread}

    famous = [
        per_seed["RC-ARM-B"][m]["d_hat"]
        for m in per_seed["RC-ARM-B"]
        if per_seed["RC-ARM-B"][m]["stratum"]
        in ("top_0.1pct", "top_1pct_below_0.1pct")
    ]
    criteria["RC-C3"] = {
        "plain": "whether famous artists keep enough connections for the build to "
                 "accept the result at all",
        "median_d_hat_algb_top_bands": (
            statistics.median(famous) if famous else None
        ),
        "floor": C3_DEGREE_FLOOR,
        "verdict": (
            "unread" if not famous
            else "FAILS -- an ALG-B artifact would be refused by check_acceptance"
            if statistics.median(famous) < C3_DEGREE_FLOOR
            else "passes"
        ),
    }
    criteria["RC-C4"] = {
        "plain": "whether the new setting offers fewer candidates, or the same "
                 "number but fewer that point back",
        "per_band": {
            band: {
                arm: {
                    "median_n_cand": bands[band][arm]["median_n_cand"],
                    "mean_recip": bands[band][arm]["mean_recip"],
                }
                for arm in ("RC-ARM-P", "RC-ARM-B")
            }
            for band in BAND_ORDER
            if bands[band]["readable"]
        },
    }

    payload = {
        "governing_document": data["governing_document"],
        "artifact_sha256": data["artifact_sha256"],
        "rc_g1": {
            "compared": drift_compared,
            "differing": drift_differing,
            "share": round(drift_share, 4) if drift_share is not None else None,
            "threshold_share": G1_SHARE_THRESHOLD,
            "member_tolerance": G1_MEMBER_TOLERANCE,
            "fired": g1_fired,
        },
        "placeholders_dropped_from_sample": dropped_placeholder,
        "sampled_candidates_unresolved": unresolved_candidate,
        "bands": bands,
        "criteria": criteria,
        "per_seed": per_seed,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n--- criteria ---", flush=True)
    for key in ("RC-C1", "RC-C2", "RC-C3"):
        print(f"{key}: {criteria[key].get('verdict')}", flush=True)
    print(f"\nwrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
