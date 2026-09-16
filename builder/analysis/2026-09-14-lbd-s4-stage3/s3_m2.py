"""`LBA-M2` -- what happens to the artists the app serves today.

PLAIN SENTENCE (section 4, fixed before any result existed): of the artists the app can reach
today, how many are simply not in this map at all -- and of the ones that are, for how many have
fewer than half the artists we show as similar to them survived?

TWO HALVES, both reported by fame band (five equal-count bands on the SERVED artifact's own
`fame_lb`, band 0 least-listened; `LBA-X7` confines every by-band figure to the served
population).

  1. ABSENT. Members of `V` with no node in the arm's map, split by CAUSE -- "no pair at all in
     the arm's table" against "pruned with the largest component" -- because they are different
     failures. A third cause, the emitter's no-identity-row skip, is separated out rather than
     folded into either: those artists DO have pairs, so filing them under "no pair at all"
     would be false. It is single figures on every arm.

  2. MATERIALLY CHANGED. For an artist in both maps, with `A` its neighbour set in the SERVED
     map, `B` its neighbour set in the ARM's map and `c` their intersection:

         R = c / |A|, gated at R < 0.5
         "fewer than half the artists we show as similar to them are still there"

     THE STATISTIC IS RETENTION, NOT JACCARD, and the difference is not cosmetic. `LBA-AM1-A1`
     and `LBA-AM1-A6` replaced Jaccard on 2026-09-14, before any arm ran, for two reasons: at
     equal list lengths a Jaccard of 0.5 fires when a THIRD of the list changed, not half, so
     the bar and its own plain sentence disagreed at authoring time; and Jaccard is bounded
     above by the ratio of the two list lengths, so an arm holding a longer list is penalised
     for holding one. Retention's denominator is the served list alone and has no such bound.

FOUR RAW QUANTITIES RECORDED PER ARTIST and five shares reported per arm (`LBA-AM1-A6`, the
critique's controls C-beta and C-gamma adopted in full):

  * `R`            -- the gated statistic.
  * `R_avail`      -- intersection / the number of served neighbours that are IN THE ARM'S MAP
                      AT ALL. "Of the artists we show today that this map could have chosen, how
                      many did it keep?" THE CONTROL THAT SEPARATES "it chose differently" from
                      "it was never available to choose". `R_avail - R` is non-zero exactly when
                      some served neighbour was outside the arm's population.
  * `b_out` share  -- the arm's neighbours that are NOT artists the app serves today, over the
                      arm list's length.
  * forced share   -- the share of the common set whose two list lengths differ by more than 2x.
                      THE NULL MODEL FOR THE RETIRED JACCARD READ, reported so its bound stays
                      visible and a later reader cannot re-adopt it unknowingly.
  * denominator both ways -- the changed count as a share of the common set AND as a share of
                      `V`, so the absent half and the changed half compose additively. Without
                      this the two halves trade off: an arm that loses more served artists gets
                      a BETTER-looking changed share, because the artists whose neighbourhood
                      moved most have been removed from the denominator.

`overlap@10`, ungated and descriptive: the share of the served map's ten strongest neighbours
still present in the arm's list. A pure re-ranking scores R = 1.0 and is invisible to every
membership statistic, and the top of the list is what a journey actually walks through. NO
THRESHOLD ATTACHES TO IT.

TWO COMPARISONS, and they carry different baggage.

  * AGAINST THE SERVED MAP. `LBA-X4` (the data bundle: a corpus roughly three times the size,
    the absent `filter_True` stage, today's msid->mbid mapping, the uncredited band-member class
    and our deterministic tie-break) and `LBA-X5` (artists took part in the served build's cap
    step that no arm here can include) TRAVEL WITH EVERY FIGURE. No sentence credits or blames
    any one component of either.
  * ARM TO ARM WITHIN A POPULATION ROW (`LBA-AM1-A7`). Both sides share a population and an
    emitter, so the population cause and the `LBA-X4` bundle are absent BY CONSTRUCTION. This is
    the only `LBA-M2` comparison in the design that isolates the threshold -- and on the `U` row
    `LBA-X6` still applies, because there the population moves WITH the threshold.

EFFECT SIZE: none. Section 4 fixes this as reported descriptively, no threshold. A map that
changes a lot is what adoption IS; whether that change is acceptable is the owner's product
judgment. THIS SCRIPT ATTACHES NO BAR AND THE REPORT MUST NOT DESCRIBE A HIGH FIGURE AS A
FAILURE OR A LOW ONE AS A PASS.

    python -u s3_m2.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

import s3_common as C

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"


def neighbour_slices(store):
    """offsets as a plain list of (start, end) is slower than slicing the arrays directly."""
    return store.offsets, store.neighbours, store.scores


def compare(base, other, base_label: str, other_label: str, band_of: dict,
            v_mbids: set, raw_path: Path | None = None) -> dict:
    """Every `LBA-M2` statistic for `other` measured against `base`.

    Works in BASE node-id space: the other map's neighbour ids are mapped through mbid into base
    ids, and -1 marks a neighbour the base map does not contain at all -- which is exactly
    `b_out`'s subject when the base is the served map.
    """
    base_ids = {m: i for i, m in enumerate(base.mbids)}
    other_ids = {m: i for i, m in enumerate(other.mbids)}

    # other node id -> base node id, or -1 when the base map has no such artist.
    other_to_base = np.full(len(other.mbids), -1, dtype=np.int64)
    for m, oi in other_ids.items():
        bi = base_ids.get(m)
        if bi is not None:
            other_to_base[oi] = bi
    # base node id -> is this artist in the other map at all? -- `R_avail`'s denominator.
    in_other = np.zeros(len(base.mbids), dtype=bool)
    for m, bi in base_ids.items():
        if m in other_ids:
            in_other[bi] = True
    # OTHER node id -> is this artist one the app serves today? `b_out` is a property of the
    # arm's own neighbour list against `V`, so it is computed in the OTHER map's id space and
    # never through the base mapping: on an arm-to-arm comparison a neighbour absent from the
    # baseline arm may still be an artist the app serves, and mapping first would miscount it.
    other_is_served = np.array([m in v_mbids for m in other.mbids], dtype=bool)

    b_off, b_nb, b_sc = neighbour_slices(base)
    o_off, o_nb, _o_sc = neighbour_slices(other)

    common = [(m, bi, other_ids[m]) for m, bi in base_ids.items() if m in other_ids]
    common.sort(key=lambda t: t[1])

    n = len(common)
    idx = np.empty(n, dtype=np.int32)
    len_a = np.empty(n, dtype=np.int16)
    len_b = np.empty(n, dtype=np.int16)
    inter = np.empty(n, dtype=np.int16)
    b_out = np.empty(n, dtype=np.int16)
    avail = np.empty(n, dtype=np.int16)
    ov10 = np.empty(n, dtype=np.float32)

    for k, (_m, bi, oi) in enumerate(common):
        a = b_nb[b_off[bi]: b_off[bi + 1]]
        o = o_nb[o_off[oi]: o_off[oi + 1]]
        mapped = other_to_base[o]
        bset = set(mapped[mapped >= 0].tolist())
        aset = set(a.tolist())

        idx[k] = bi
        len_a[k] = len(aset)
        len_b[k] = len(o)
        inter[k] = len(aset & bset)
        b_out[k] = len(o) - int(other_is_served[o].sum())
        avail[k] = int(in_other[a].sum())
        # The base map's ten strongest neighbours, by score. Ties fall to whatever order a
        # stable argsort gives; with <= 50 neighbours and a strict top-10 cut that cannot move
        # the share by more than one neighbour, and nothing is gated on it.
        sc = b_sc[b_off[bi]: b_off[bi + 1]]
        top = a[np.argsort(-sc, kind="stable")[:10]].tolist()
        ov10[k] = sum(1 for x in top if x in bset) / max(1, min(10, len(aset)))

    r = inter.astype(np.float64) / np.maximum(1, len_a)
    r_avail = np.where(avail > 0, inter.astype(np.float64) / np.maximum(1, avail), np.nan)
    b_out_share = b_out.astype(np.float64) / np.maximum(1, len_b)
    forced = (len_b.astype(np.float64) > 2 * len_a) | (len_a.astype(np.float64) > 2 * len_b)

    if raw_path is not None:
        RAW.mkdir(exist_ok=True)
        np.savez_compressed(raw_path, base_node=idx, len_a=len_a, len_b=len_b,
                            intersection=inter, b_out=b_out, avail=avail)

    bands = np.array([band_of.get(base.mbids[i], "outside-V") for i in idx])

    def bucket(mask) -> dict:
        k = int(mask.sum())
        if k == 0:
            return {"common": 0}
        return {
            "common": k,
            "changed_R_below_0.5": int((r[mask] < 0.5).sum()),
            "changed_share_of_common": round(float((r[mask] < 0.5).mean()), 6),
            "R_zero": int((r[mask] == 0).sum()),
            "R_zero_share_of_common": round(float((r[mask] == 0).mean()), 6),
            "R_median": round(float(np.median(r[mask])), 6),
            "R_mean": round(float(r[mask].mean()), 6),
            "R_avail_median": round(float(np.nanmedian(r_avail[mask])), 6),
            "R_avail_mean": round(float(np.nanmean(r_avail[mask])), 6),
            "b_out_share_mean": round(float(b_out_share[mask].mean()), 6),
            "forced_share": round(float(forced[mask].mean()), 6),
            "overlap_at_10_mean": round(float(ov10[mask].mean()), 6),
            "len_a_median": int(np.median(len_a[mask])),
            "len_b_median": int(np.median(len_b[mask])),
        }

    all_mask = np.ones(n, dtype=bool)
    out = {
        "base": base_label,
        "arm": other_label,
        "base_nodes": len(base.mbids),
        "arm_nodes": len(other.mbids),
        "overall": bucket(all_mask),
        "by_band": {b: bucket(bands == b) for b in ["0", "1", "2", "3", "4", "unknown"]},
    }
    outside = int((bands == "outside-V").sum())
    if outside:
        # `LBA-X7`: the fame ruler is the SERVED artifact's, so it cannot reach an artist the
        # served map does not contain. On an arm-to-arm comparison above rule `V` most of the
        # common set is outside it, and those artists are reported as one unbanded bucket
        # rather than silently dropped from the by-band table.
        out["by_band"]["outside-V (no served fame ruler, LBA-X7)"] = bucket(bands == "outside-V")
    return out


def absent_half(served, arm_store, arm: str, v_list: list, band_of: dict) -> dict:
    """The two absent causes section 4 names, plus the emitter's no-identity-row skip."""
    arm_nodes = set(arm_store.mbids)
    table = C.table_mbids(arm)
    no_id = C.no_identity_row_mbids(arm)

    absent, no_pair, pruned, noid = [], [], [], []
    for m in v_list:
        if m in arm_nodes:
            continue
        absent.append(m)
        if m in no_id:
            noid.append(m)
        elif m in table:
            pruned.append(m)
        else:
            no_pair.append(m)

    def by_band(members) -> dict:
        counts = {b: 0 for b in ["0", "1", "2", "3", "4", "unknown"]}
        for m in members:
            counts[band_of.get(m, "unknown")] += 1
        return counts

    if len(no_pair) + len(pruned) + len(noid) != len(absent):
        raise SystemExit(f"REFUSING: {arm} absent causes do not partition the absent set")

    return {
        "V": len(v_list),
        "absent": len(absent),
        "absent_share_of_V": round(len(absent) / len(v_list), 6),
        "cause_no_pair_in_arm_table": len(no_pair),
        "cause_pruned_with_largest_component": len(pruned),
        "cause_no_identity_row": len(noid),
        "arm_table_payloads": len(table),
        "by_band": {
            "absent": by_band(absent),
            "no_pair_in_arm_table": by_band(no_pair),
            "pruned_with_largest_component": by_band(pruned),
        },
    }


def _toy(mbids, adjacency):
    """A GraphStore built by hand, for the self-test. Same dataclass the shipped parser fills."""
    ids = {m: i for i, m in enumerate(mbids)}
    offsets, neighbours, scores = [0], [], []
    for m in mbids:
        for nb, sc in adjacency[m]:
            neighbours.append(ids[nb])
            scores.append(sc)
        offsets.append(len(neighbours))
    return C.gs.GraphStore(
        mbids=list(mbids), names=list(mbids), disambiguations=[""] * len(mbids),
        pop_raw=np.zeros(len(mbids), dtype=np.float32),
        offsets=np.array(offsets, dtype=np.int32),
        neighbours=np.array(neighbours, dtype=np.int32),
        scores=np.array(scores, dtype=np.float32))


def self_test() -> None:
    """Drive `compare()` itself, on the path the measurement actually uses.

    The stage-1 lesson applied rather than cited: `stage2_build_instrument.py` was pronounced
    self-tested having never run a build to completion, because its only call hit a guard that
    raised before the code under test. "Shown to go red" is necessary and not sufficient -- it
    has to go red ON THE PATH THE INSTRUMENT IS USED ON. So this drives `compare()` twice over
    the same base with two different arms, and asserts the gated statistic RED on one and GREEN
    on the other. If retention were computed wrongly, or the gate inverted, one of the two
    directions fails.
    """
    base = _toy(["a", "b", "c", "d"],
                {"a": [("b", 3.0), ("c", 2.0), ("d", 1.0)], "b": [("a", 3.0)],
                 "c": [("a", 2.0)], "d": [("a", 1.0)]})
    served = {"a", "b", "c", "d"}
    bands = {"a": "4", "b": "3", "c": "1", "d": "0"}

    # RED arm: `a` keeps one of its three served neighbours and gains one artist the app does
    # not serve. Retention 1/3 -- below the 0.5 gate -- while `b` keeps everything.
    red = _toy(["a", "b", "x"], {"a": [("b", 3.0), ("x", 9.0)], "b": [("a", 3.0)],
                                 "x": [("a", 9.0)]})
    r = compare(base, red, "base", "red", bands, served)["overall"]
    assert r["common"] == 2, r
    assert r["changed_R_below_0.5"] == 1, r          # `a` fires, `b` does not
    assert r["changed_share_of_common"] == 0.5, r
    assert r["R_zero"] == 0, r
    assert round(r["R_median"], 4) == 0.6667, r      # median of 1/3 and 1
    assert round(r["R_avail_mean"], 4) == 1.0, r     # both kept everything AVAILABLE to them
    assert round(r["b_out_share_mean"], 4) == 0.25, r  # `a` 1/2, `b` 0/1
    assert r["forced_share"] == 0.0, r               # 3 vs 2 and 1 vs 1: neither exceeds 2x
    assert round(r["overlap_at_10_mean"], 4) == 0.6667, r  # `a` 1/3, `b` 1/1
    print("[self-test] RED   arm: retention fires on 1 of 2, R_avail 1.0 -- "
          "the control separates 'chose differently' from 'never available'")

    # GREEN arm: same population as the base, every served neighbour kept. Nothing may fire.
    green = _toy(["a", "b", "c", "d"],
                 {"a": [("b", 3.0), ("c", 2.0), ("d", 1.0)], "b": [("a", 3.0)],
                  "c": [("a", 2.0)], "d": [("a", 1.0)]})
    g = compare(base, green, "base", "green", bands, served)["overall"]
    assert g["common"] == 4, g
    assert g["changed_R_below_0.5"] == 0, g
    assert g["R_mean"] == 1.0 and g["R_avail_mean"] == 1.0, g
    assert g["b_out_share_mean"] == 0.0 and g["overlap_at_10_mean"] == 1.0, g
    print("[self-test] GREEN arm: identical map, nothing fires, every share at its floor")

    # A length pair the retired Jaccard read would have forced below its bar with ZERO
    # contribution from neighbour identity (`LBA-AM1-A6`). Retention is 1.0; the forced-share
    # null model sees it. This is the reason the statistic was changed, asserted rather than
    # described.
    wide = _toy(["a", "b", "c", "d", "e", "f", "g", "h"],
                {"a": [("b", 3.0), ("c", 2.0), ("d", 1.0), ("e", 1.0), ("f", 1.0), ("g", 1.0),
                       ("h", 1.0)], "b": [("a", 3.0)], "c": [("a", 2.0)], "d": [("a", 1.0)],
                 "e": [("a", 1.0)], "f": [("a", 1.0)], "g": [("a", 1.0)], "h": [("a", 1.0)]})
    w = compare(base, wide, "base", "wide", bands, served)["overall"]
    assert w["R_mean"] == 1.0, w                     # every served neighbour kept
    assert w["forced_share"] == 0.25, w              # `a` alone: 7 against 3, past 2x
    print("[self-test] forced-share null model sees a 7-vs-3 length pair at retention 1.0 -- "
          "the bound that retired Jaccard")
    print("[self-test] PASSED")


def main() -> None:
    t0 = time.time()
    served = C.load_served()
    band_of = C.served_fame_bands(served)
    v_list = list(served.mbids)
    v_set = set(v_list)
    print(f"[m2] served map {len(v_list):,} artists; bands ready ({time.time() - t0:.1f}s)")

    # The `V`-row arm-to-arm comparison runs FIRST (task 0's ordering): it is the only
    # comparison free of both population movement and the `LBA-X4` bundle, and `LBA-R4-V`
    # names it as the `V` row's only live threshold evidence.
    stores = {}
    arm_to_arm = []
    for rule in ["V", "P", "U"]:
        arms = C.ROWS[rule]
        for a in arms:
            if a not in stores:
                stores[a] = C.load_arm(a)
        for i, base in enumerate(arms):
            for other in arms[i + 1:]:
                t = time.time()
                res = compare(stores[base], stores[other], base, other, band_of, v_set)
                res["population_rule"] = rule
                res["one_column"] = rule != "U"
                res["note"] = (
                    "LBA-X6: on the U row the population moves WITH the threshold, so this is "
                    "not a one-column comparison in the sense the V and P rows are"
                    if rule == "U" else
                    "one column (threshold only): same pinned population, same emitter, so the "
                    "population cause and the LBA-X4 bundle are absent by construction")
                arm_to_arm.append(res)
                print(f"[m2] arm-to-arm {base} -> {other} ({rule}) "
                      f"{res['overall']['common']:,} common ({time.time() - t:.1f}s)")

    C.write_json(HERE / "s3_m2_armtoarm.json",
                 {"measurement": "LBA-M2, arm-to-arm within a population row (LBA-AM1-A7)",
                  "comparisons": arm_to_arm}, __file__)

    served_cmp = []
    for arm in C.ARMS:
        t = time.time()
        res = compare(served, stores[arm], "served (graph-msw-tu50.bin)", arm, band_of, v_set,
                      raw_path=RAW / f"s3_m2_raw_{arm}.npz")
        res["absent"] = absent_half(served, stores[arm], arm, v_list, band_of)
        res["filter"] = C.ARMS[arm]["filter"]
        res["population_rule"] = C.ARMS[arm]["rule"]
        res["sentence"] = C.SENTENCE[arm]
        ch = res["overall"]["changed_R_below_0.5"]
        res["overall"]["changed_share_of_V"] = round(ch / len(v_list), 6)
        res["overall"]["absent_plus_changed_share_of_V"] = round(
            (ch + res["absent"]["absent"]) / len(v_list), 6)
        served_cmp.append(res)
        print(f"[m2] served -> {arm} common {res['overall']['common']:,} "
              f"changed {ch:,} absent {res['absent']['absent']:,} ({time.time() - t:.1f}s)")

    C.write_json(HERE / "s3_m2_served.json",
                 {"measurement": "LBA-M2 against the served map",
                  "exposures": ["LBA-X4 travels with every figure here (the data bundle)",
                                "LBA-X5 travels with every figure here (the cap-step population "
                                "term)",
                                "LBA-X7 confines every by-band figure to the served population"],
                  "effect_size": "none -- section 4 fixes this as reported descriptively",
                  "arms": served_cmp}, __file__)
    print(f"[m2] done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
