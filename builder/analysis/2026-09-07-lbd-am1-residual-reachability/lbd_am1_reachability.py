"""`LBD-AM1` — how much of the residual set can this track reach even in principle?

WHY THIS EXISTS. `LBD-AM1` amends
`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md` §3 to report
`LBD-C2a` stratified into the RESIDUAL set — the `CXR`-added artists still at two
or fewer connections when our own degree ceiling does not bind — and its
complement. The residual set is the part of the dead-end problem no cap-rule
change can touch, and it is the part `LBD-` uniquely addresses.

That makes one question a bound on the whole track, and it is answerable now
rather than at Task 4: **an artist nobody in ListenBrainz's corpus played can
gain no edge at any threshold and any cap.** Task 1's `R-SUPPLY` measured that
for the added set as a whole (`2026-09-07-lbd-inputs/README.md` §2, which owns
those figures). This asks the same question of the residual stratum alone, by
joining the pinned residual list against Task 1's own per-artist output.

WHAT IT IS NOT. This is not a supply measurement and cannot be read as one.
Having enough distinct listeners is NECESSARY, not sufficient — a pair's score
needs listeners who played BOTH artists inside one session, and nothing here
measures co-occurrence. Task 1's README states that limit for the whole set and
it carries over unchanged to this stratum. The direction this settles is the
negative one: a residual null cannot be explained away by absence.

Frozen harness in Task 1's own style: stdlib + DuckDB only, no project imports,
every input read-only and pinned by sha256.

Run from the repo root:
    uv run --with duckdb python -u \
        builder/analysis/2026-09-07-lbd-am1-residual-reachability/lbd_am1_reachability.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import duckdb

HERE = Path(__file__).parent
INPUTS = Path("D:/unsung-large-data/lbd-inputs")

# The residual set, computed by the DFA- probe and pinned there. Copied into the
# pinned-inputs directory beside the added and pre-existing sets, exactly as §3
# does for those two, so every arm reads it from one place.
DFA_RESIDUAL = (
    HERE.parent / "2026-09-07-degree-floor-at-admission" / "dfa_residual_mbids.txt"
)
DFA_RECORD = (
    HERE.parent / "2026-09-07-degree-floor-at-admission" / "dfa_benefit_identity.json"
)
PINNED_RESIDUAL = INPUTS / "cxr_residual_mbids.txt"

ADDED = INPUTS / "cxr_added_mbids.txt"
SUPPLY = INPUTS / "cxr_added_dump_supply.parquet"

# ALG-B's parameters, from Task 1's README §2: a pair needs at least
# ceil((threshold+1)/contribution) = 4 DISTINCT users before it can survive the
# HAVING clause at all. Arithmetic on ListenBrainz's own SQL, not an estimate.
MIN_USERS_FOR_THRESHOLD = 4


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    for path in (DFA_RESIDUAL, DFA_RECORD, ADDED, SUPPLY):
        if not path.is_file():
            raise SystemExit(f"missing pinned input: {path}")

    # Pin the residual list beside the other two fixed sets, and record both
    # shas: the probe's copy and the pinned copy. They must agree.
    shutil.copyfile(DFA_RESIDUAL, PINNED_RESIDUAL)
    sha_probe = sha256_file(DFA_RESIDUAL)
    sha_pinned = sha256_file(PINNED_RESIDUAL)
    if sha_probe != sha_pinned:
        raise SystemExit("the copy does not match its source")

    residual = [m for m in DFA_RESIDUAL.read_text(encoding="utf-8").split("\n") if m]
    added = [m for m in ADDED.read_text(encoding="utf-8").split("\n") if m]
    added_set = set(added)

    # The residual set must be a subset of the pinned added set, and must match
    # the count the DFA- record committed. Both are structural checks on the
    # extraction, not findings.
    stray = [m for m in residual if m not in added_set]
    committed = json.loads(DFA_RECORD.read_text(encoding="utf-8"))
    committed_count = committed["residual_still_at_two_or_fewer"][
        "under_the_ceiling_lift"
    ]
    if stray:
        raise SystemExit(f"{len(stray)} residual MBIDs are not in the added set")
    if len(residual) != committed_count:
        raise SystemExit(
            f"residual list holds {len(residual)} MBIDs but the committed record "
            f"says {committed_count}"
        )

    con = duckdb.connect()
    con.execute("CREATE TEMP TABLE residual(mbid VARCHAR)")
    con.executemany("INSERT INTO residual VALUES (?)", [(m,) for m in residual])
    con.execute("CREATE TEMP TABLE added(mbid VARCHAR)")
    con.executemany("INSERT INTO added VALUES (?)", [(m,) for m in added])

    supply = str(SUPPLY).replace("\\", "/")

    def counts(table: str, n: int) -> dict:
        row = con.execute(
            f"""
            SELECT count(s.mbid)
                 , count(*) FILTER (WHERE s.rows_mapped > 0)
                 , count(*) FILTER (WHERE s.users_mapped >= {MIN_USERS_FOR_THRESHOLD})
                 , count(*) FILTER (WHERE s.users_mapped >= 10)
                 , count(*) FILTER (WHERE s.users_mapped >= 50)
              FROM {table} t
              LEFT JOIN read_parquet('{supply}') s USING (mbid)
            """
        ).fetchone()
        present, mapped, ge4, ge10, ge50 = row
        quant = con.execute(
            f"""
            SELECT median(s.users_mapped)
                 , quantile_cont(s.users_mapped, 0.10)
                 , quantile_cont(s.users_mapped, 0.90)
              FROM {table} t
              JOIN read_parquet('{supply}') s USING (mbid)
            """
        ).fetchone()
        return {
            "n": n,
            "present_in_the_corpus": present,
            "present_in_mapped_listens": mapped,
            "absent_entirely": n - present,
            "share_absent": round((n - present) / n, 5),
            f"at_least_{MIN_USERS_FOR_THRESHOLD}_distinct_listeners": ge4,
            f"share_at_least_{MIN_USERS_FOR_THRESHOLD}": round(ge4 / n, 5),
            "at_least_10_distinct_listeners": ge10,
            "at_least_50_distinct_listeners": ge50,
            "distinct_listeners_p10_median_p90_over_present": [
                None if quant[1] is None else round(float(quant[1]), 1),
                None if quant[0] is None else round(float(quant[0]), 1),
                None if quant[2] is None else round(float(quant[2]), 1),
            ],
        }

    con.execute(
        "CREATE TEMP TABLE complement AS "
        "SELECT mbid FROM added WHERE mbid NOT IN (SELECT mbid FROM residual)"
    )
    n_complement = con.execute("SELECT count(*) FROM complement").fetchone()[0]

    result = {
        "probe": "LBD-AM1 — what share of the residual set is reachable by the "
        "LBD- track even in principle?",
        "written": "2026-09-07, before any LBD- arm had run",
        "figures_owner": "this file and the README beside it. Task 1's whole-set "
        "figures are owned by builder/analysis/2026-09-07-lbd-inputs/README.md "
        "section 2 and are cited, never restated here",
        "inputs": {
            "residual_list_source": str(DFA_RESIDUAL),
            "residual_list_sha256": sha_probe,
            "residual_list_pinned_at": str(PINNED_RESIDUAL),
            "residual_list_pinned_sha256": sha_pinned,
            "dfa_record": str(DFA_RECORD),
            "dfa_record_sha256": sha256_file(DFA_RECORD),
            "added_set": str(ADDED),
            "added_set_sha256": sha256_file(ADDED),
            "task_1_supply_parquet": str(SUPPLY),
            "task_1_supply_parquet_sha256": sha256_file(SUPPLY),
        },
        "definition": "the residual set is the CXR-added artists still at <= 2 "
        "connections when union_degree_ceiling does not bind — the artists no "
        "cap-rule change can help. Measured on ONE population under ONE cap "
        "rule; it is a pinned MBID list, not a claim about any other build",
        "minimum_distinct_listeners_to_clear_threshold": MIN_USERS_FOR_THRESHOLD,
        "residual": counts("residual", len(residual)),
        "complement": counts("complement", n_complement),
        "limits": [
            "Enough distinct listeners is NECESSARY, not sufficient. A pair's "
            "score needs listeners who played BOTH artists in one session and "
            "nothing here measures co-occurrence. This raises the prior that "
            "supply exists; it does not establish it, and must not be cited as "
            "evidence that any arm will move LBD-C2.",
            "The direction it settles is the negative one: a residual null "
            "cannot be explained away by the artists being absent.",
            "Task 1's denominator caveat carries over unchanged — membership is "
            "read from artist_credit_mbids while LB's job joins "
            "artist_credit_id, and the two were not compared.",
            "This proposes no cap-rule change and depends on none. That "
            "decision is parked and the owner's (design section 9).",
        ],
    }

    dest = HERE / "lbd_am1_reachability.json"
    dest.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    for label in ("residual", "complement"):
        c = result[label]
        print(
            f"{label:<11} n {c['n']:>6,}  absent {c['absent_entirely']:>4,} "
            f"({100 * c['share_absent']:.2f}%)  "
            f">= {MIN_USERS_FOR_THRESHOLD} listeners "
            f"{c[f'at_least_{MIN_USERS_FOR_THRESHOLD}_distinct_listeners']:>6,} "
            f"({100 * c[f'share_at_least_{MIN_USERS_FOR_THRESHOLD}']:.2f}%)  "
            f"listeners p10/median/p90 "
            f"{c['distinct_listeners_p10_median_p90_over_present']}"
        )
    print(f"\nresidual list sha256 {sha_probe}")
    print(f"pinned at {PINNED_RESIDUAL}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
