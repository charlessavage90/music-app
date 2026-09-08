"""`LBD-` Task 3 — the synthetic sub-check for `lbd_similarity.py`.

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-08-lbd-similarity/lbd_fixture.py

WHY THIS FILE EXISTS. Design section 6 makes it the only thing separating "we implemented it
wrong" from "the inputs differ", and section 7 retires `LBD-R2` on it. The pre-registration's
section 6 adds the constraint that decides whether it is worth anything:

  > Its expected values are derived by executing ListenBrainz's quoted SQL by hand -- from
  > the fetched source, never from the plan's prose. The plan's featured-weight sentence
  > describes a different computation from the SQL it quotes, and a fixture built from that
  > sentence would agree with a wrong implementation and disagree with ListenBrainz.

So every expected value below is hand-derived in the DERIVATION block, stage by stage,
against `artist.py` line numbers -- not produced by running the implementation and pasting
the answer. The derivation is written out in full so a reader can check the arithmetic
without trusting either file.

AND THE FIXTURE IS SHOWN TO GO RED BEFORE IT IS ALLOWED TO GO GREEN. Five mutants patch one
thing each into the generated SQL; each must change the output. A fixture that has never
failed is not evidence that anything passed. The two the pre-registration names by hand are
T3-M2 (the window frame) and T3-M1 (the untrimmed comparison); T3-M3 is the DuckDB cast-rounding
divergence found while transcribing; T3-M4 and T3-M5 cover `rank()` and the mapped-listen filter.

--------------------------------------------------------------------------------------
THE FIXTURE
--------------------------------------------------------------------------------------

Five artists, lexically ordered so `mbid0 < mbid1` is readable at a glance:

    A = ...aa   B = ...bb   C = ...cc   D = ...dd   E = ...ee

`artist_credit` frame (artist_credit_id, artist_mbid, position, join_phrase) -- the shape
LB builds in `data/postgres/artist_credit.py`:

    1: (A, 0, '')                       single
    2: (B, 0, '')                       single
    3: (C, 0, '')                       single
    4: (A, 0, 'feat.'), (B, 1, '')      TWO artists, join phrase UNSPACED  -> matches
    5: (A, 0, ' feat. '), (B, 1, '')    TWO artists, join phrase SPACED    -> does NOT match
    6: (D, 0, '')                       single
    7: (E, 0, '')                       single

`recording_length` frame, lengths in ms (`artist.py:23` divides by 1000):

    r1 = 120000 -> 120 s     r2 = 240000 -> 240 s     r4 = 120000 -> 120 s
    r5 =  20000 ->  20 s     r3 ABSENT   -> 180 s (DEFAULT_TRACK_LENGTH)
    r6 ABSENT from `recording_length`, present in `recording_gid_redirect_length` at 240 s

--------------------------------------------------------------------------------------
DERIVATION -- by hand, from `artist.py`, stage by stage
--------------------------------------------------------------------------------------

Notation: `diff` is `artist.py:40`, `skipped` is `LEAD(diff) < -skip` (`:50`, `:136`), and a
row is KEPT only if `skipped` is FALSE (`:63` -- NULL is not FALSE, which is T3-P2).
`skip` = 30, `session` = 300, `contribution` = 3 throughout.

USER 1 -- the plain path, the per-user cap, and T3-P2.
    t=1000  A  r1(120)   diff NULL      skipped: LEAD=80   -> F   KEEP
    t=1200  B  r1(120)   diff   80      skipped: LEAD=280  -> F   KEEP
    t=1600  C  r1(120)   diff  280      skipped: LEAD=80   -> F   KEEP
    t=1800  A  r1(120)   diff   80      skipped: LEAD=580  -> F   KEEP
    t=2500  A  r1(120)   diff  580      skipped: LEAD=NULL -> NULL  DROP   (T3-P2)
    session_id = running COUNT_IF(diff > 300): 0,0,0,0 then 1 on the last row (dropped).
    Session 0 holds A, B, C, A. The self-join (`:69-73`) is unordered and excludes equal
    artist_mbid, so with A twice:
        (A,B) 4   (A,C) 4   (B,C) 2       <- 4, not 2, because A appears twice; T3-P3 doubles all
    cap LEAST(sum, 3):  (A,B) 3   (A,C) 3   (B,C) 2      <- the cap bites here

USER 2 -- the fan-out artefact T3-P1, and the mapped-listen filter.
    t=5000  ac=4 r2(240)  fans to TWO rows: A(pos 0, 'feat.'), B(pos 1, '')
            after_ft_jp over `PARTITION BY user,t,recording_mbid ORDER BY position` with the
            DEFAULT frame (RANGE UNBOUNDED PRECEDING TO CURRENT ROW, `:28,36`):
                A(pos 0): any over {A} -> 'feat.' matches      -> TRUE  -> similarity 0.25
                B(pos 1): any over {A,B} -> still TRUE          -> TRUE  -> similarity 0.25
            BOTH are 0.25. The main artist carries the join phrase; the featured one inherits
            it through the cumulative frame. This is the assertion the pre-registration names.
    t=5100  C  recording_mbid NULL   -> EXCLUDED by `:34-35` before sessioning
    t=5300  D  r1(120)
    t=5500  E  r1(120)
    order (t, msid, position):  A(5000), B(5000), D(5300), E(5500)
        A  diff NULL          skipped: LEAD = B's -240 -> TRUE   DROP   <- P1
        B  diff 5000-5000-240 = -240   skipped: LEAD = 60  -> F   KEEP
        D  diff 5300-5000-240 =   60   skipped: LEAD = 80  -> F   KEEP
        E  diff 5500-5300-120 =   80   skipped: LEAD=NULL  -> NULL DROP  (T3-P2)
    Session 0 holds B (0.25, credit [A,B]) and D (1, credit [D]).
        (B,D) = 0.25*1 + 1*0.25 = 0.5           cap LEAST(0.5,3) = 0.5

USER 3 -- the UNTRIMMED comparison, the 180 s default, a genuine skip, a same-second tie.
    t=9000  ac=5 r2(240)  fans to A(pos 0, ' feat. '), B(pos 1, '')
            ' feat. ' is NOT one of LB's eight literals (they are all unspaced), so
            after_ft_jp is FALSE for A and, cumulatively, FALSE for B.
            BOTH are 1. This is the second assertion the pre-registration names.
    t=9300  D  r3 ABSENT -> COALESCE gives 180
    t=9400  E  r1(120)  msid m12  |  t=9400  C  r4(120)  msid m13   <- same-second tie
    t=20000 A  r1(120)  |  t=20100 B  r1(120)
    order (t, msid, position): A(9000) B(9000) D(9300) E(9400) C(9400) A(20000) B(20100)
        A(9000)   diff NULL                      skipped: LEAD=-240  -> TRUE  DROP
        B(9000)   diff 9000-9000-240   = -240    skipped: LEAD=60    -> F     KEEP
        D(9300)   diff 9300-9000-240   =   60    skipped: LEAD=-80   -> TRUE  DROP  <- a real
                                                  skip: E started 80 s early (LBDR-F5)
        E(9400)   diff 9400-9300-180   =  -80    skipped: LEAD=-120  -> TRUE  DROP
        C(9400)   diff 9400-9400-120   = -120    skipped: LEAD=10480 -> F     KEEP
        A(20000)  diff 20000-9400-120  = 10480   skipped: LEAD=-20   -> F     KEEP
                                                  (-20 is NOT < -30: the boundary is strict)
        B(20100)  diff 20100-20000-120 =  -20    skipped: LEAD=NULL  -> NULL  DROP
    session_id under the RANGE frame: 0 through t=9400; the 10480 gap makes A(20000) session 1.
    Session 0 holds B (1, credit [A,B]) and C (1, credit [C]).  Session 1 holds A alone.
        (B,C) = 1*1 + 1*1 = 2                   cap LEAST(2,3) = 2
    A alone in session 1 produces no pair -- a session of one is silent.

USER 4 -- a SHORT featured track, so the main artist survives T3-P1 and the frame is testable.
    t=30000 ac=4 r5(20)   fans to A(pos 0, 'feat.') and B(pos 1, ''), both 0.25 as in user 2
    t=30100 C  r1(120)  |  t=30300 D  r1(120)
        A(30000)  diff NULL                  skipped: LEAD = -20 -> -20 < -30 is FALSE  KEEP
        B(30000)  diff 30000-30000-20 = -20  skipped: LEAD =  80 -> F                   KEEP
        C(30100)  diff 30100-30000-20 =  80  skipped: LEAD =  80 -> F                   KEEP
        D(30300)  diff 30300-30100-120 = 80  skipped: LEAD=NULL  -> NULL                DROP
    THE 20 s TRACK IS THE POINT: `-20 < -30` is false, so A is not skipped and both members of
    the featured credit reach the self-join. Every other featured credit here loses its first
    row to T3-P1, which would leave T3-M2 undetectable.
    Session 0 holds A (0.25, [A,B]), B (0.25, [A,B]), C (1, [C]).
        (A,B): artist_mbid differs BUT artist_credit_mbids are equal -> EXCLUDED by `:73`
        (A,C) = 0.25*1 * 2 = 0.5      (B,C) = 0.25*1 * 2 = 0.5

USER 5 -- the redirect arm, T3-D6. Sized so the duration decides a skip.
    t=40000 A  r6  |  t=40200 B  r1(120)  |  t=40500 C  r1(120)
    WITH redirects  (r6 -> 240 s):
        A diff NULL   skipped: LEAD = 40200-40000-240 = -40 -> -40 < -30 TRUE   DROP
        B diff -40    skipped: LEAD = 180 -> F   KEEP
        C diff 40500-40200-120 = 180   skipped: NULL   DROP
        Session 0 holds B alone -> NO PAIRS. User 5 contributes nothing.
    WITHOUT redirects (r6 absent -> 180 s):
        A diff NULL   skipped: LEAD = 40200-40000-180 =  20 -> 20 < -30 FALSE   KEEP
        B diff 20     skipped: LEAD = 180 -> F   KEEP
        C diff 180    skipped: NULL   DROP
        Session 0 holds A and B ->  (A,B) = 2      cap LEAST(2,3) = 2

CROSS-USER SUM (`:86`), and T3-D3 is what makes these three lines worth reading:
                       u1    u2    u3    u4    u5      SUM    TRUNC   (CAST would give)
        (A,B)           3     -     -     -     -      3.0      3           3
        (A,C)           3     -     -   0.5     -      3.5      3           4
        (B,C)           2     -     2   0.5     -      4.5      4           5
        (B,D)           -   0.5     -     -     -      0.5      0           1
    Spark's cast to an integral type truncates; DuckDB's rounds. Three of these four rows
    differ between the two, and (B,D) differs in KIND: at `HAVING score > 0` it is excluded
    under truncation and included under rounding. That is T3-D3, caught by M3.

    WITHOUT redirects, user 5 adds 2 to (A,B): 3 + 2 = 5.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lbd_similarity import Params, build_sessioned_index  # noqa: E402

A = "00000000-0000-0000-0000-0000000000aa"
B = "00000000-0000-0000-0000-0000000000bb"
C = "00000000-0000-0000-0000-0000000000cc"
D = "00000000-0000-0000-0000-0000000000dd"
E = "00000000-0000-0000-0000-0000000000ee"

R1 = "11111111-1111-1111-1111-111111111001"
R2 = "11111111-1111-1111-1111-111111111002"
R3 = "11111111-1111-1111-1111-111111111003"  # absent from recording_length -> 180 s
R4 = "11111111-1111-1111-1111-111111111004"
R5 = "11111111-1111-1111-1111-111111111005"
R6 = "11111111-1111-1111-1111-111111111006"  # redirect only

# (artist_credit_id, artist_mbid, position, join_phrase)
ARTIST_CREDIT = [
    (1, A, 0, ""),
    (2, B, 0, ""),
    (3, C, 0, ""),
    (4, A, 0, "feat."),
    (4, B, 1, ""),
    (5, A, 0, " feat. "),
    (5, B, 1, ""),
    (6, D, 0, ""),
    (7, E, 0, ""),
]

# (recording_mbid, length_ms)
RECORDING_LENGTH = [(R1, 120000), (R2, 240000), (R4, 120000), (R5, 20000)]
RECORDING_GID_REDIRECT_LENGTH = [(R6, 240000)]

# (user_id, listened_at_epoch, recording_msid, recording_mbid, artist_credit_id, credit_mbids)
LISTENS = [
    (1, 1000, "m01", R1, 1, [A]),
    (1, 1200, "m02", R1, 2, [B]),
    (1, 1600, "m03", R1, 3, [C]),
    (1, 1800, "m04", R1, 1, [A]),
    (1, 2500, "m05", R1, 1, [A]),
    (2, 5000, "m06", R2, 4, [A, B]),
    (2, 5100, "m07", None, 3, [C]),  # unmapped: excluded by artist.py:34-35
    (2, 5300, "m08", R1, 6, [D]),
    (2, 5500, "m09", R1, 7, [E]),
    (3, 9000, "m10", R2, 5, [A, B]),
    (3, 9300, "m11", R3, 6, [D]),
    (3, 9400, "m12", R1, 7, [E]),
    (3, 9400, "m13", R4, 3, [C]),
    (3, 20000, "m14", R1, 1, [A]),
    (3, 20100, "m15", R1, 2, [B]),
    (4, 30000, "m16", R5, 4, [A, B]),
    (4, 30100, "m17", R1, 3, [C]),
    (4, 30300, "m18", R1, 6, [D]),
    (5, 40000, "m19", R6, 1, [A]),
    (5, 40200, "m20", R1, 2, [B]),
    (5, 40500, "m21", R1, 3, [C]),
]

# ---------------------------------------------------------------------------------------
# EXPECTED. Hand-derived above; never produced by running the implementation.
# ---------------------------------------------------------------------------------------

EXPECTED = {
    # threshold 0, no rank cut, LB's listen pairing, redirects applied. This is `T`.
    "T": [(A, B, 3), (A, C, 3), (B, C, 4)],
    # threshold 3, strict `>` (artist.py:90) drops the two 3s and keeps only the 4.
    "threshold_3": [(B, C, 4)],
    # limit 1 with rank(), not row_number(): (A,B) and (A,C) tie at 3 under mbid0 = A, so
    # BOTH survive `rank <= 1` and mbid0 = A returns two rows for a limit of one.
    "limit_1": [(A, B, 3), (A, C, 3), (B, C, 4)],
    # our own arm (T3-D7): user 1's duplicate A collapses, so (A,B) and (A,C) fall from 3 to 2.
    "distinct": [(A, B, 2), (A, C, 2), (B, C, 4)],
    # T3-D6: without the redirect arm user 5's 240 s track reads as 180 s, its first row stops
    # being skipped, and (A,B) gains that user's 2.
    "no_redirects": [(A, B, 5), (A, C, 3), (B, C, 4)],
}


def build_db(con: duckdb.DuckDBPyConnection, *, redirects: bool) -> None:
    con.execute("CREATE TABLE artist_credit(artist_credit_id BIGINT, artist_mbid VARCHAR, position BIGINT, join_phrase VARCHAR)")
    con.executemany("INSERT INTO artist_credit VALUES (?,?,?,?)", ARTIST_CREDIT)

    rows = list(RECORDING_LENGTH) + (list(RECORDING_GID_REDIRECT_LENGTH) if redirects else [])
    con.execute("CREATE TABLE recording_length(recording_mbid VARCHAR, length BIGINT)")
    con.executemany("INSERT INTO recording_length VALUES (?,?)", rows)

    con.execute(
        "CREATE TABLE artist_similarity_listens("
        "user_id BIGINT, listened_at TIMESTAMP, recording_msid VARCHAR, "
        "recording_mbid VARCHAR, artist_credit_id BIGINT, artist_credit_mbids VARCHAR[])"
    )
    con.executemany(
        "INSERT INTO artist_similarity_listens VALUES (?, to_timestamp(?), ?, ?, ?, ?)",
        LISTENS,
    )


def run(sql: str, *, redirects: bool = True) -> list[tuple[str, str, int]]:
    con = duckdb.connect()
    build_db(con, redirects=redirects)
    rows = con.execute(f"SELECT mbid0, mbid1, score FROM ({sql}) ORDER BY mbid0, mbid1").fetchall()
    con.close()
    return [(a, b, int(s)) for a, b, s in rows]


def sql_for(**kw) -> str:
    apply_threshold = kw.pop("apply_threshold", True)
    apply_limit = kw.pop("apply_limit", True)
    p = Params(**{"days": 7500, "session": 300, "contribution": 3, "threshold": 0,
                  "limit": None, "skip": 30, "pairing": "listen", **kw})
    return build_sessioned_index(
        "artist_similarity_listens", "recording_length", "artist_credit", p,
        apply_threshold=apply_threshold, apply_limit=apply_limit,
    )


# ---------------------------------------------------------------------------------------
# MUTANTS. Each patches ONE thing into the generated SQL and MUST change the output.
# ---------------------------------------------------------------------------------------

MUTANTS = {
    "T3-M1 trimmed join phrase (LBDR-F2b)": (
        "ac.join_phrase IN (", "trim(ac.join_phrase) IN ("
    ),
    "T3-M2 strictly-preceding frame (LBDR-F2a)": (
        "ORDER BY ac.position)",
        "ORDER BY ac.position ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)",
    ),
    "T3-M3 CAST instead of TRUNC (T3-D3)": (
        "TRUNC(SUM(part_score))::BIGINT", "CAST(SUM(part_score) AS BIGINT)"
    ),
    "T3-M4 row_number instead of rank (artist.py:95)": (
        "rank() OVER w AS rank", "row_number() OVER w AS rank"
    ),
    "T3-M5 no mapped-listen filter (artist.py:34-35)": (
        "WHERE l.recording_mbid IS NOT NULL\n                   AND l.recording_mbid != ''",
        "WHERE TRUE",
    ),
    # T3-D8. Reverting to a literal COUNT_IF gives every user's first row a NULL session_id,
    # which then never joins -- so the first listen of every user vanishes from every pair.
    # This mutant is the one the fixture caught on its first run.
    "T3-M6 literal COUNT_IF for session_id (T3-D8)": (
        "SUM(CASE WHEN difference > 300 THEN 1 ELSE 0 END) OVER wr",
        "COUNT_IF(difference > 300) OVER wr",
    ),
}


def main() -> int:
    failures: list[str] = []

    def check(name: str, got, want) -> None:
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            print(f"        expected {want}")
            print(f"        got      {got}")
            failures.append(name)

    print("Fidelity of the transcription -- expected values hand-derived from artist.py\n")
    check("T (threshold 0, no cut, listen pairing)", run(sql_for()), EXPECTED["T"])
    check("threshold 3, strict >", run(sql_for(threshold=3)), EXPECTED["threshold_3"])
    check("limit 1 keeps rank() ties", run(sql_for(limit=1)), EXPECTED["limit_1"])
    check("pairing distinct (T3-D7)", run(sql_for(pairing="distinct")), EXPECTED["distinct"])
    check(
        "no redirects (T3-D6)",
        run(sql_for(), redirects=False),
        EXPECTED["no_redirects"],
    )

    print("\nThe check is shown to go RED -- each mutant must move the answer\n")
    base_sql = sql_for()
    limit_sql = sql_for(limit=1)
    for name, (needle, repl) in MUTANTS.items():
        source, want = (limit_sql, EXPECTED["limit_1"]) if name.startswith("T3-M4") else (base_sql, EXPECTED["T"])
        if needle not in source:
            print(f"  FAIL  {name}: patch target not present in the SQL")
            failures.append(name + " (target missing)")
            continue
        got = run(source.replace(needle, repl))
        moved = got != want
        print(f"  {'RED ' if moved else 'FAIL'}  {name}")
        print(f"        {'-> ' + str(got) if moved else 'did NOT move the answer; the check cannot see this defect'}")
        if not moved:
            failures.append(name + " (undetected)")

    print()
    if failures:
        print(f"FAILED: {len(failures)} -> {failures}")
        return 1
    print("All fidelity checks pass and all six mutants are detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
