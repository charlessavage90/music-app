"""`LBA-M3` -- the added artists' supply.

PLAIN SENTENCE (section 4, fixed before any result existed): of the artists the deeper crawl
added -- the ones that arrived with almost no connections -- what share are still dead ends in
this map?

THE STATISTIC is the track's own, unchanged: SHARE AT OR BELOW 2 CONNECTIONS over the pinned
added set, WITH AN ARTIST ABSENT FROM THE MAP COUNTED AS 0 (`LBD-C2b`'s `share_le_2_or_absent`).
Share-absent is reported SEPARATELY, because absent and present-with-degree-1 are different
outcomes. Median degree is reported and is NOT gated on -- `LBD-G2`'s own rule: it bootstraps to
a single value at this resolution and moves by a whole unit under the population confound alone.

UNIT: connections, i.e. the artist's degree in the arm's BUILT map, each connection counted once.
Not CSR entries (which count both directions) and not archive neighbour rows.

FOUR STRATA.

  * `added` (29,892), the pinned set -- the subject.
  * `preexisting` (58,793), the WITHIN-ARM CONTROL, the first of `LBD-G2`'s two.
  * `residual` (5,967) and its `complement` (23,925) -- the `LBD-AM1` split, DESCRIPTIVE. The
    residual set is the added artists still at two or fewer connections when our own degree
    ceiling does not bind.
  * `nodes(arm) - V` -- `LBA-AM1-A10`'s fourth stratum, DESCRIPTIVE and derived per arm. The
    three pinned strata are all subsets of the extended crawl's population, so NONE of them can
    see the artists a `U` rule adds beyond it -- which is the only thing `LBA-A7`-`A9` exist to
    test. It cannot be pinned (`LBA-X6`), so it carries no bar; its membership is recorded by
    count and by sha256 over its sorted MBIDs, the same way this track pins every other
    gitignored set.

THE SECOND CONTROL is the arm's own TABLE-LEVEL figure -- `LBD-C2a`'s statistic over the same
added set, from the arm's derived pair table rather than its built map. It is a property of the
THRESHOLD ALONE: all three arms at a given threshold derive from one table, so the three
population rules share a table-level figure and it cannot distinguish them. Taken by running the
frozen `../2026-09-08-lbd-similarity/lbd_reads.py --mode c2a` UNEDITED on each of the three
tables. Its `A0` (threshold 10) run reproduces that README's committed figures exactly, which is
this instrument's green check against a FROZEN RECORD rather than against another figure from
this session.

WHERE `LBD-G2`'s BAR MAY BE READ, resolved by `LBA-AM1-A9` before anything ran and NOT by a
session holding results:

  * ONE-COLUMN THRESHOLD ATTRIBUTION on exactly two arms -- `LBA-A5` and `LBA-A6`, each against
    `LBA-A4`. Bar >= 1 percentage point, admissible only with both controls reported.
  * On the `U` row: computed and reported, NEVER read as a one-column attribution, with
    `LBA-X6` beside it -- there the population moves WITH the threshold.
  * On the `V` row: the statistic is 1.0 BY CONSTRUCTION. The added set is exactly the artists
    the extended crawl has and the served map does not, so no member of it is in `V` and the
    emitter writes a payload only for a member of the arm's population. Every threshold
    difference on this row is identically zero, so the bar is UNFIREABLE and the value is
    reported as `n/a` rather than as a finding. A null that cannot be anything else is not
    evidence (the `CRS-C3` shape).

    THE 1.0 IS COMPUTED HERE, NOT ASSERTED. If the arithmetic ever disagreed with the
    construction argument, the construction argument would be the thing that is wrong.

    python -u s3_m3.py
"""

from __future__ import annotations

import hashlib
import json
import statistics
import time
from pathlib import Path

import numpy as np

import s3_common as C

HERE = Path(__file__).resolve().parent

# The arm's derived pair table, by threshold. All three arms at a threshold share one table, so
# the table-level control is a property of the threshold column and of nothing else.
TABLE_C2A = {
    10: Path(r"C:\unsung-fast\lbd-pairs\A0\c2a.json"),
    7: Path(r"C:\unsung-fast\lbd-pairs\T7\c2a.json"),
    3: Path(r"C:\unsung-fast\lbd-pairs\A5\c2a.json"),
}
MEMBERSHIP_OUT = Path(r"C:\unsung-fast\lbd-artifacts\s3_stratum4")


def summarise(degrees: list, name: str) -> dict:
    """`LBD-C2b`'s summary, in `lbd_reads.py`'s own shape so the two levels read alike."""
    vals = sorted(degrees)
    n = len(vals)
    if n == 0:
        return {"set": name, "n": 0}
    return {
        "set": name,
        "n": n,
        "share_le_2_or_absent": round(sum(1 for v in vals if v <= 2) / n, 6),
        "count_le_2_or_absent": sum(1 for v in vals if v <= 2),
        "share_absent": round(sum(1 for v in vals if v == 0) / n, 6),
        "count_absent": sum(1 for v in vals if v == 0),
        "median_degree_REPORTED_NOT_GATED": statistics.median(vals),
    }


def main() -> None:
    t0 = time.time()
    added = C.read_mbid_file(C.CXR_ADDED)
    pre = C.read_mbid_file(C.CXR_PREEXISTING)
    residual = set(C.read_mbid_file(C.CXR_RESIDUAL))
    v_set = set(C.read_mbid_file(C.POP_V))
    print(f"[m3] added {len(added):,}  pre-existing {len(pre):,}  residual {len(residual):,}  "
          f"V {len(v_set):,}")

    table_level = {}
    for thr, path in TABLE_C2A.items():
        d = json.loads(path.read_text("utf-8"))
        table_level[thr] = {
            "source": str(path),
            "added_share_le_2": round(d["whole_set"]["share_le_2"], 6),
            "preexisting_share_le_2": round(d["preexisting_reference"]["share_le_2"], 6),
            "residual_share_le_2": round(d["residual"]["share_le_2"], 6),
            "complement_share_le_2": round(d["complement"]["share_le_2"], 6),
        }

    MEMBERSHIP_OUT.mkdir(parents=True, exist_ok=True)
    arms = {}
    for arm, meta in C.ARMS.items():
        t = time.time()
        store = C.load_arm(arm)
        deg = np.diff(store.offsets)
        by_mbid = {m: int(deg[i]) for i, m in enumerate(store.mbids)}

        d_added = [by_mbid.get(m, 0) for m in added]
        d_pre = [by_mbid.get(m, 0) for m in pre]
        d_res = [by_mbid.get(m, 0) for m in added if m in residual]
        d_comp = [by_mbid.get(m, 0) for m in added if m not in residual]

        # `LBA-AM1-A10`'s fourth stratum. Every member is in the map by definition, so there is
        # no absent component; the membership is written out and pinned by sha256 because it
        # cannot be pinned in advance -- it is a consequence of the arm (`LBA-X6`).
        s4 = sorted(m for m in store.mbids if m not in v_set)
        d_s4 = [by_mbid[m] for m in s4]
        blob = "\n".join(s4).encode("utf-8")
        s4_sha = hashlib.sha256(blob).hexdigest()
        (MEMBERSHIP_OUT / f"{arm}_nodes_minus_V.txt").write_bytes(blob)

        row = {
            "arm": arm,
            "sentence": C.SENTENCE[arm],
            "population_rule": meta["rule"],
            "threshold": meta["threshold"],
            "filter": meta["filter"],
            "arm_nodes": len(store.mbids),
            "added": summarise(d_added, "added (whole set)"),
            "preexisting_within_arm_control": summarise(d_pre, "pre-existing (control)"),
            "residual_descriptive": summarise(d_res, "LBD-AM1 residual"),
            "complement_descriptive": summarise(d_comp, "LBD-AM1 complement"),
            "stratum4_nodes_minus_V_descriptive": {
                **summarise(d_s4, "nodes(arm) - V (LBA-AM1-A10)"),
                "membership_sha256": s4_sha,
                "membership_file": str(MEMBERSHIP_OUT / f"{arm}_nodes_minus_V.txt"),
            },
            "table_level_second_control": table_level[meta["threshold"]],
        }
        if meta["rule"] == "V":
            row["bar"] = ("n/a -- UNFIREABLE by construction (LBA-AM1-A9). No member of the "
                          "added set is in V, so the statistic is 1.0 on every V arm and every "
                          "threshold difference on this row is identically zero. Computed, not "
                          "asserted.")
        elif meta["rule"] == "U":
            row["bar"] = ("computed and reported, NEVER read as a one-column threshold "
                          "attribution -- LBA-X6: on the U row the population is a dependent "
                          "variable that moves with the threshold")
        else:
            row["bar"] = ("LBD-G2 carried: >= 1 percentage point against LBA-A4, admissible "
                          "with both controls reported. This row carries the only two "
                          "one-column threshold reads the design admits (LBA-AM1-A9)")
        # On a `V` arm the fourth stratum is EMPTY by construction -- the arm's population is
        # `V` itself, so it adds nobody beyond it. That is `LBA-AM1-A10`'s point seen from the
        # other side, and an empty stratum is printed as empty rather than as a share of nothing.
        s4row = row["stratum4_nodes_minus_V_descriptive"]
        s4txt = ("empty" if not s4row["n"]
                 else f"n={s4row['n']:,} {s4row['share_le_2_or_absent']:.4f}")
        arms[arm] = row
        print(f"[m3] {arm} ({meta['rule']}, thr {meta['threshold']}) added "
              f"{row['added']['share_le_2_or_absent']:.4f}  pre "
              f"{row['preexisting_within_arm_control']['share_le_2_or_absent']:.4f}  "
              f"stratum4 {s4txt} ({time.time() - t:.1f}s)")

    # The two one-column threshold reads the design admits, computed here rather than left to
    # the report to subtract. Deltas in percentage points against the isolating baseline.
    base = arms["LBA-A4"]["added"]["share_le_2_or_absent"]
    p_row = {a: round(100 * (arms[a]["added"]["share_le_2_or_absent"] - base), 4)
             for a in ("LBA-A5", "LBA-A6")}
    u_base = arms["LBA-A7"]["added"]["share_le_2_or_absent"]
    u_row = {"LBA-A8": round(100 * (arms["LBA-A8"]["added"]["share_le_2_or_absent"] - u_base), 4)}

    C.write_json(HERE / "s3_m3.json", {
        "measurement": "LBA-M3 -- share at or below 2 connections over the pinned added set, "
                       "absent counted as 0",
        "sets": {"added": len(added), "preexisting": len(pre), "residual": len(residual),
                 "complement": len(added) - len(residual)},
        "table_level_second_control_by_threshold": table_level,
        "arms": arms,
        "LBD_G2_reads": {
            "P_row_one_column_pp_vs_LBA-A4": p_row,
            "U_row_pp_vs_LBA-A7_NOT_ONE_COLUMN": u_row,
            "V_row": "n/a -- unfireable by construction",
            "bar": ">= 1 percentage point with both controls reported; >= 10 without",
        },
    }, __file__)
    print(f"[m3] P-row one-column deltas vs LBA-A4 (pp): {p_row}")
    print(f"[m3] U-row delta vs LBA-A7 (pp, NOT one-column, LBA-X6): {u_row}")
    print(f"[m3] done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
