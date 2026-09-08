"""`LBD-` Task 3 — ListenBrainz's `build_sessioned_index`, transcribed into DuckDB.

Frozen: stdlib + DuckDB only, no project imports. Writes only under
`D:\\unsung-large-data\\` (`LBD-D8`); `builder/scratch/` is read by absolute path, never
written.

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run --with duckdb python -u builder/analysis/2026-09-08-lbd-similarity/lbd_similarity.py --help

THE SOURCE OF TRUTH IS LISTENBRAINZ'S OWN FILE, NOT ANY PROSE ABOUT IT.
`listenbrainz_spark/similarity/artist.py`, re-fetched from metabrainz/listenbrainz-server
master by URL on 2026-09-08, sha256
`7a8516be7fb0c25b99ef63f3210029c348cf69c987a3ce540f325262e4b90de3` (161 lines) — the same
sha the pre-registration pinned on 2026-09-07, so master has not moved. Line references
below are into that file. A review (`LBDR-F2`) established that the plan's prose describes
a DIFFERENT computation from the SQL it quotes, so prose is not admissible evidence here.

--------------------------------------------------------------------------------------
THE TEN DECLARED DEVIATIONS FROM LB'S SQL. There are no others.
--------------------------------------------------------------------------------------

T3-D1. `to_date` is pinned to the dump's END_TIMESTAMP, not `date.today()` (`artist.py:121`).
    A reproducible run cannot use today. `from_date = to_date - days`.

T3-D2. THE ORDER IS MADE TOTAL. LB orders both windows by `listened_at` alone
    (`artist.py:45,55`), which is not a total order, so `LAG`/`LEAD` are nondeterministic
    on ties -- and ties are the common case, because the `listens` CTE fans one listen out
    into one row per credited artist, all sharing `user_id`, `listened_at` AND
    `recording_msid` (`LBDR-F3`; adding `recording_msid` alone breaks no tie for exactly
    those rows). We order `(listened_at, recording_msid, position)`.

    BUT `session_id` KEEPS LB'S RANGE FRAME. `COUNT_IF(...) OVER w` (`artist.py:49`) has no
    explicit frame, so it is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` over
    `listened_at` -- and under RANGE every peer row at the same `listened_at` is in frame,
    which makes that aggregate WELL-DEFINED under LB's own nondeterministic order. Ordering
    it by our tiebreak instead would silently convert it to ROWS semantics and change it.
    So: two windows. The offset functions take the total order (they are nondeterministic in
    LB no matter what, and we pick a deterministic representative); the aggregate keeps
    RANGE over `listened_at` (it is deterministic in LB, and we preserve that).

T3-D3. `TRUNC(...)::BIGINT` REPLACES `CAST(... AS BIGINT)`, IN BOTH PLACES.
    Spark's cast from a floating type to an integral type TRUNCATES toward zero. DuckDB's
    ROUNDS: verified here 2026-09-08, `CAST(2.7 AS BIGINT)` = 3 and `CAST(0.5 AS BIGINT)` = 1.
    Transcribing the cast literally would inflate every duration (`artist.py:23`) and, far
    worse, every cross-user score across the `HAVING score > threshold` boundary
    (`artist.py:86`). This is the single most consequential line in the file.

T3-D4. `bool_or(...)` replaces Spark's `any(...)` (`artist.py:28`) -- DuckDB spells the boolean
    OR aggregate differently. Both ignore NULLs and both return NULL when every input is
    NULL, which is why LB's `COALESCE(..., 1)` at `:43` is load-bearing and is kept.

T3-D5. `epoch(...)` replaces Spark's `BIGINT(<timestamp>)` (`artist.py:22`). Our `listened_at`
    column is a parquet TIMESTAMP; ListenBrainz stores whole epoch seconds, so the
    conversion is exact and the PARTITION BY at `:36` groups identically either way.

T3-D6. `recording_length` GAINS THE REDIRECT ARM. LB's frame is built by
    `data/postgres/recording.py:16-33` as `recording UNION ALL recording_gid_redirect JOIN
    recording`, so a redirected gid carries its TARGET's length. Task 1 extracted only
    `recording`, which sends every listen on a redirected MBID to the 180 s default and
    shifts `difference`, session boundaries and the skip test one way (`LBDR-F4`). The
    redirect table is in `mbdump` and this run uses it. Pass `--no-redirects` to reproduce
    the un-redirected frame, which is what makes the size of the difference measurable.

T3-D7. `--pairing distinct` IS OURS, NOT LB'S. LB self-joins listens (`artist.py:69-71`);
    `LBD-D6` schedules the cheaper form as an arm. We define it as `SELECT DISTINCT
    user_id, session_id, artist_mbid, credit_key, similarity` before the self-join
    -- exact-duplicate-row removal, which leaves both join predicates untouched and keeps an
    artist credited two different ways as two rows. `LBD-D6` says "self-joins distinct
    artists" and does not pin that tie; this is our pinning of it, and it is a deviation
    because it is an arm rather than a transcription. `--pairing listen` is LB's.

T3-D8. `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` REPLACES `COUNT_IF(...)` FOR `session_id`.
    Spark's `COUNT_IF` is a count and never returns NULL; it returns 0 when nothing in frame
    matches. DuckDB's returns NULL when every predicate in frame is NULL -- verified here
    2026-09-08. That is exactly the state of every user's FIRST row, whose `difference` is
    NULL because `LAG` has nothing to look back at. A NULL `session_id` then never satisfies
    `USING (user_id, session_id)` at `artist.py:71`, so a literal transcription SILENTLY
    DELETES EVERY USER'S FIRST LISTEN from every pair it would have formed. The
    `CASE ... ELSE 0` form makes each input non-NULL and reproduces Spark exactly.

    This one was found by the fixture rather than by reading, and it is the reason the
    fixture asserts on users 1 and 5 -- both of whose first rows are load-bearing. Mutant T3-M6
    reverts it, and must go red.

T3-D9. `hash(artist_credit_mbids)` REPLACES THE LIST ITSELF THROUGH THE WINDOWED STAGES.
    LB carries `artist_credit_mbids` (a `VARCHAR[]`) from `listens` all the way to the
    self-join, where it is used for exactly one thing: the equality predicate
    `s1.artist_credit_mbids != s2.artist_credit_mbids` (`artist.py:73`), which stops two
    artists on the SAME track pairing with each other.

    Carrying a nested type through a ~195-million-row sort partitioned by `user_id` and then
    through a self-join of the same magnitude is what made the `user_id % 16` slice die with
    `failed to allocate ... (7.4 GiB/7.4 GiB used)` AFTER it had already spilled 449 MB:
    DuckDB's out-of-core paths for nested types are materially weaker than for flat ones.
    A BIGINT key costs 8 bytes and spills.

    THIS IS ONLY LEGITIMATE IF IT IS EXACT. A hash collision would make two genuinely
    different credits compare equal, suppressing real pairs -- and it would bias supply
    DOWNWARD, which is the direction that makes this track's central question look answered
    when it is not. So it is verified rather than assumed: `--verify-credit-key` compares
    `count(DISTINCT artist_credit_mbids)` against `count(DISTINCT hash(artist_credit_mbids))`
    over the corpus and REFUSES on any difference. Measured collision-free on a 1-in-64 user
    slice (430,644 distinct arrays, 430,644 distinct hashes) before this was adopted.

T3-D10. THE TWO 36-CHARACTER IDENTIFIER COLUMNS ARE REPLACED, EXACTLY, IN STAGE 0.
    `recording_mbid` and `recording_msid` are the two largest columns in the dump and neither
    survives stage 0.

    `recording_mbid` is used for exactly two things -- the duration LEFT JOIN (`artist.py:30`)
    and the `after_ft_jp` window partition (`:36`) -- and both happen inside stage 0, so it is
    simply not needed afterwards.

    `recording_msid` is used for nothing in LB at all; it is OURS, the tiebreak `T3-D2` adds to
    make LB's non-total order total. The downstream sort is
    `(listened_at, recording_msid, position)` inside `PARTITION BY user_id`, so
    `recording_msid` can only ever break ties among rows sharing a user AND a second. Stage 0
    therefore emits `DENSE_RANK() OVER (PARTITION BY user_id, listened_at ORDER BY
    recording_msid)` -- its ordinal within precisely that group. A dense rank is
    order-preserving on the group it ranks, so ordering by `(listened_at, msid_ord, position)`
    is IDENTICAL to ordering by `(listened_at, recording_msid, position)` within any user.

    NOT a hash, and the difference matters. A 64-bit hash over 2.4 billion near-unique msids
    has roughly a one-in-six chance of at least one collision by the birthday bound, and a
    collision would silently make the order non-total again -- reintroducing exactly the
    nondeterminism `T3-D2` exists to remove. The dense rank has no such failure mode: the
    groups it ranks hold a handful of rows each.

    The fixture's user 3 carries two DIFFERENT listens in the same second, which is the case
    this substitution could break, and it asserts the same answer either way.

--------------------------------------------------------------------------------------
THREE PROPERTIES OF LB'S SQL THAT LOOK LIKE BUGS AND ARE FAITHFULLY REPRODUCED
--------------------------------------------------------------------------------------

T3-P1. THE FAN-OUT EATS ITS OWN FIRST ROW. For an N-artist credit at time t, rows 2..N have
    `difference = t - t - duration = -duration`. `skipped` is `LEAD(difference) <
    -skip` (`:50,136`), so rows 1..N-1 are skipped for any track longer than `skip`
    seconds, and `sessions_filtered` (`:56-63`) drops them. On a 2-artist credit over 30 s
    exactly one artist survives -- the one sorting LAST. Reproduced, and it is why T3-D2's
    tiebreak choice is a recorded decision rather than a detail.

T3-P2. EVERY USER'S LAST LISTEN IS DISCARDED. `LEAD` is NULL there, so `skipped` is NULL and
    `WHERE NOT skipped` (`:63`) drops the row -- SQL three-valued logic, not a filter anyone
    wrote. Reproduced.

T3-P3. THE SELF-JOIN COUNTS EACH PAIR TWICE. `sessions_filtered s1 JOIN sessions_filtered s2`
    (`:69-71`) is unordered, so (X,Y) and (Y,X) both land on the same lexical pair with the
    same product. Every score is therefore 2x what a one-directional join gives, BEFORE the
    per-user cap at `:78` -- which means the cap bites at half the co-listens it appears to.
    Reproduced.

The featured-artist weight is a fourth such property and is asserted by the fixture rather
than described here: see `lbd_fixture.py`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

# `artist.py:10-14`, verbatim.
DEFAULT_TRACK_LENGTH = 180
FEATURED_ARTIST_WEIGHT = 0.25

# `artist.py:28`, verbatim and UNTRIMMED. MusicBrainz stores join phrases with their
# surrounding spaces and LB compares raw, so ' feat. ' does not match 'feat.'. Task 1's
# R-FEAT measured how far apart the trimmed and untrimmed comparisons land on this corpus,
# and the gap is orders of magnitude, not a rounding difference -- so an implementer who
# "fixes" the spacing diverges from LB on essentially every multi-artist credit. FIGURES ARE
# OWNED BY builder/analysis/2026-09-07-lbd-inputs/README.md section 3 AND ARE NOT RESTATED
# HERE. Do not trim. Mutant T3-M1 is what holds this line in place.
FEATURED_JOIN_PHRASES = (
    "feat.",
    "\uff46\uff45\uff41\uff54.",
    "ft.",
    "\u03c3\u03c5\u03bc\u03bc.",
    "duet with",
    "featuring",
    "\u03c3\u03c5\u03bc\u03bc\u03b5\u03c4\u03ad\u03c7\u03b5\u03b9",
    "\uff46\uff45\uff41\uff54\uff55\uff52\uff49\uff4e\uff47",
)

DUMP_END_TIMESTAMP = "2026-09-01 00:00:02.462107+00:00"


@dataclass(frozen=True)
class Params:
    """The six tokens LB's `main()` takes (`artist.py:106`), plus our two arm knobs."""

    days: int = 7500
    session: int = 300
    contribution: int = 3
    threshold: int = 10
    limit: int | None = 100
    skip: int = 30
    pairing: str = "listen"

    @property
    def skip_threshold(self) -> int:
        return -self.skip  # `artist.py:136`. The token says skip_30; the SQL compares < -30.

    @property
    def algorithm(self) -> str:
        # `artist.py:140`, reproduced so an output can name itself in LB's own vocabulary.
        lim = "none" if self.limit is None else self.limit
        return (
            f"session_based_days_{self.days}_session_{self.session}"
            f"_contribution_{self.contribution}_threshold_{self.threshold}"
            f"_limit_{lim}_skip_{self.skip}"
        )


def _phrase_list_sql() -> str:
    return ", ".join("'" + p.replace("'", "''") + "'" for p in FEATURED_JOIN_PHRASES)


def listens_sql(
    listen_table: str,
    metadata_table: str,
    artist_credit_table: str,
) -> str:
    """LB's `listens` CTE (`artist.py:20-36`), plus the two substitutions of `T3-D10`.

    STAGE 0, and it is the one stage that can be materialised cheaply: its only window
    partitions by `(user_id, listened_at, recording_mbid)` -- a SINGLE LISTEN -- so the
    partitions are two or three rows and nothing has to be sorted at scale. Everything that
    needs a big sort happens downstream of it.

    It emits neither 36-character identifier column. Both are replaced exactly, not
    approximately -- see `T3-D10`.
    """
    return f"""
                SELECT l.user_id
                     -- T3-D5: epoch() for Spark's BIGINT(<timestamp>) (`artist.py:22`).
                     , epoch(l.listened_at)::BIGINT AS listened_at
                     -- T3-D3: TRUNC, not CAST -- DuckDB's cast rounds (`artist.py:23`).
                     , TRUNC(COALESCE(r.length / 1000, {DEFAULT_TRACK_LENGTH}))::BIGINT AS duration
                     -- T3-D10: the ordinal of this listen's recording_msid WITHIN its own
                     -- (user, second). The downstream total order is
                     -- (listened_at, recording_msid, position) inside PARTITION BY user_id, so
                     -- recording_msid only ever breaks ties among rows sharing a user AND a
                     -- second -- exactly this group. A dense rank over it is order-preserving
                     -- there, so the substitution is EXACT, and it costs four bytes instead
                     -- of thirty-six.
                     --
                     -- UINTEGER, not UTINYINT: a one-byte ordinal overflowed on real data at
                     -- 477. Some account logged 477 distinct recordings inside a SINGLE
                     -- second -- a bulk import or a bot. Found by running stage 0 over one
                     -- real parquet file; no amount of reading would have produced that
                     -- number.
                     , DENSE_RANK() OVER (PARTITION BY l.user_id, epoch(l.listened_at)
                                          ORDER BY l.recording_msid)::UINTEGER AS msid_ord
                     , ac.position::UTINYINT AS position
                     -- T3-D9: a BIGINT key replaces the VARCHAR[].
                     , hash(l.artist_credit_mbids) AS credit_key
                     , ac.artist_mbid
                     -- `artist.py:43`, hoisted here because `after_ft_jp` is only computable
                     -- inside this stage's window and takes just two values.
                     , COALESCE(IF(
                           bool_or(ac.join_phrase IN ({_phrase_list_sql()})) OVER w,
                           {FEATURED_ARTIST_WEIGHT}, 1), 1)::FLOAT AS similarity
                  FROM {listen_table} l
             LEFT JOIN {metadata_table} r
                 USING (recording_mbid)
                  JOIN {artist_credit_table} ac
                 USING (artist_credit_id)
                 WHERE l.recording_mbid IS NOT NULL
                   AND l.recording_mbid != ''
                -- T3-D4: bool_or for Spark's any(). NO EXPLICIT FRAME, exactly as
                -- `artist.py:28,36` -- the default RANGE UNBOUNDED PRECEDING TO CURRENT ROW is
                -- what makes after_ft_jp true for the row's OWN join phrase as well as its
                -- predecessors'. In MusicBrainz the join phrase is the text FOLLOWING that
                -- artist, so in "A feat. B" it is A -- the MAIN artist -- that carries 'feat.'
                -- and is weighted 0.25, and B is weighted too through the cumulative frame.
                -- Both. The plan's prose said otherwise (`LBDR-F2`).
                WINDOW w AS (PARTITION BY l.user_id, epoch(l.listened_at), l.recording_mbid
                             ORDER BY ac.position)
    """


def sessions_from_listens_sql(listens_source: str, p: Params) -> str:
    """LB's `ordered` -> `sessions` -> `sessions_filtered` (`artist.py:37-63`).

    STAGE 1. This is where the big sort lives -- three window specifications partitioned by
    `user_id` -- and it is what exhausted memory when fed straight from the dump. Fed from a
    materialised stage 0 on fast storage it can be chunked by `user_id` cheaply, because
    re-reading the intermediate is no longer a 127 GB scan of a platter.
    """
    return f"""
            WITH listens AS ({listens_source}
            ), ordered AS (
                SELECT user_id
                     , listened_at
                     , msid_ord
                     , position
                     -- T3-D2: the total order. LB's `ORDER BY listened_at` (`:45`) is not one.
                     , listened_at - LAG(listened_at, 1) OVER wt - LAG(duration, 1) OVER wt
                           AS difference
                     , credit_key
                     , artist_mbid
                     , similarity
                  FROM listens
                WINDOW wt AS (PARTITION BY user_id ORDER BY listened_at, msid_ord, position)
            ), sessions AS (
                SELECT user_id
                     -- T3-D2: LB's RANGE frame over listened_at is KEPT here. Peers at the same
                     -- second are all in frame, which is what makes this aggregate
                     -- well-defined under LB's own order (`artist.py:49`).
                     -- T3-D8: SUM(CASE...) not COUNT_IF -- DuckDB's count_if returns NULL when
                     -- every predicate in frame is NULL, which is every user's first row, and
                     -- a NULL session_id silently drops that listen from the join at `:71`.
                     , SUM(CASE WHEN difference > {p.session} THEN 1 ELSE 0 END) OVER wr
                           AS session_id
                     -- ...while LEAD takes the total order, since it is nondeterministic in
                     -- LB regardless (`artist.py:50`).
                     , LEAD(difference, 1) OVER wt < {p.skip_threshold} AS skipped
                     , credit_key
                     , artist_mbid
                     , similarity
                  FROM ordered
                WINDOW wr AS (PARTITION BY user_id ORDER BY listened_at
                              RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                     , wt AS (PARTITION BY user_id ORDER BY listened_at, msid_ord, position)
            )
                SELECT user_id, session_id, credit_key, artist_mbid, similarity
                  FROM sessions
                 -- T3-P2: NULL `skipped` on each user's last row makes this drop it.
                 WHERE NOT skipped
    """


def sessions_sql(
    listen_table: str,
    metadata_table: str,
    artist_credit_table: str,
    p: Params,
) -> str:
    """Stage 0 and stage 1 composed -- LB's `artist.py:20-63` in one query."""
    return sessions_from_listens_sql(
        listens_sql(listen_table, metadata_table, artist_credit_table), p
    )



def pairs_sql(
    sessions_source: str,
    p: Params,
    *,
    apply_threshold: bool = True,
    apply_limit: bool = True,
) -> str:
    """LB's `user_grouped_mbids` -> output (`artist.py:64-102`), over a sessions source.

    `sessions_source` is any SQL expression yielding
    `(user_id, session_id, credit_key, artist_mbid, similarity)` -- a subquery in the one-shot
    path, or `read_parquet(...)` over a materialised intermediate.
    """
    threshold_clause = (
        f"HAVING score > {p.threshold}" if apply_threshold else "HAVING score > 0"
    )

    # T3-D7: our arm. Exact-duplicate-row removal ahead of the self-join.
    if p.pairing == "distinct":
        pair_cte = f"""
            WITH sessions_filtered AS ({sessions_source}),
            pair_source AS (
                SELECT DISTINCT user_id, session_id, artist_mbid, credit_key, similarity
                  FROM sessions_filtered
            )"""
    elif p.pairing == "listen":
        pair_cte = f"""
            WITH pair_source AS ({sessions_source})"""
    else:
        raise ValueError(f"unknown pairing {p.pairing!r}")

    ranked = f"""
            , ranked_mbids AS (
                SELECT mbid0
                     , mbid1
                     , score
                     -- rank(), NOT row_number(): ties at the cut ALL survive, so an arm may
                     -- return more than `limit` rows for one mbid0 (`artist.py:95`).
                     , rank() OVER w AS rank
                  FROM thresholded_mbids
                WINDOW w AS (PARTITION BY mbid0 ORDER BY score DESC)
            )   SELECT mbid0, mbid1, score
                  FROM ranked_mbids
                 WHERE rank <= {p.limit}"""
    unranked = """
                SELECT mbid0, mbid1, score
                  FROM thresholded_mbids"""
    tail = ranked if (apply_limit and p.limit is not None) else unranked

    return f"""{pair_cte}
            , user_grouped_mbids AS (
                SELECT user_id
                     , IF(s1.artist_mbid < s2.artist_mbid, s1.artist_mbid, s2.artist_mbid) AS lexical_mbid0
                     , IF(s1.artist_mbid > s2.artist_mbid, s1.artist_mbid, s2.artist_mbid) AS lexical_mbid1
                     , s1.similarity * s2.similarity AS similarity
                  FROM pair_source s1
                  JOIN pair_source s2
                 USING (user_id, session_id)          -- T3-P3: unordered, so each pair twice.
                 WHERE s1.artist_mbid != s2.artist_mbid
                   AND s1.credit_key != s2.credit_key
            ), user_contribtion_mbids AS (            -- LB's spelling (`artist.py:74`).
                SELECT user_id
                     , lexical_mbid0 AS mbid0
                     , lexical_mbid1 AS mbid1
                     , LEAST(SUM(similarity), {p.contribution}) AS part_score
                  FROM user_grouped_mbids
              GROUP BY user_id, lexical_mbid0, lexical_mbid1
            ), thresholded_mbids AS (
                SELECT mbid0
                     , mbid1
                     -- T3-D3 again, and this is the consequential one: rounding here would push
                     -- scores across the strict `>` boundary (`artist.py:86,90`).
                     , TRUNC(SUM(part_score))::BIGINT AS score
                  FROM user_contribtion_mbids
              GROUP BY mbid0, mbid1
                {threshold_clause}
            ){tail}
    """


def build_sessioned_index(
    listen_table: str,
    metadata_table: str,
    artist_credit_table: str,
    p: Params,
    *,
    apply_threshold: bool = True,
    apply_limit: bool = True,
) -> str:
    """The one-shot path: LB's whole job, `artist.py:17-103`, stage for stage.

    Identical to composing `sessions_sql` into `pairs_sql`; the fixture asserts the one-shot
    and two-stage paths agree, so the split cannot drift from the whole.
    """
    return pairs_sql(
        sessions_sql(listen_table, metadata_table, artist_credit_table, p),
        p,
        apply_threshold=apply_threshold,
        apply_limit=apply_limit,
    )

def register_frames(con: duckdb.DuckDBPyConnection, inputs: Path, *, redirects: bool) -> None:
    """The two MusicBrainz frames LB reads (`artist.py:130-134`), as DuckDB views."""
    rl = (inputs / "recording_length.parquet").as_posix()
    ac = (inputs / "artist_credit.parquet").as_posix()
    if redirects:
        # T3-D6: LB's own frame resolves redirects (`data/postgres/recording.py:16-33`).
        rgr = (inputs / "recording_gid_redirect_length.parquet").as_posix()
        con.execute(
            f"""CREATE OR REPLACE VIEW recording_length AS
                    SELECT recording_mbid, length FROM read_parquet('{rl}')
                 UNION ALL
                    SELECT recording_mbid, length FROM read_parquet('{rgr}')"""
        )
    else:
        con.execute(
            "CREATE OR REPLACE VIEW recording_length AS "
            f"SELECT recording_mbid, length FROM read_parquet('{rl}')"
        )
    con.execute(
        f"CREATE OR REPLACE VIEW artist_credit AS SELECT * FROM read_parquet('{ac}')"
    )


def register_listens(
    con: duckdb.DuckDBPyConnection,
    dump: Path,
    p: Params,
    *,
    user_mod: int | None = None,
    user_rem: int = 0,
) -> None:
    """`get_listens_from_dump(from_date, to_date)` (`artist.py:128`), windowed by T3-D1.

    The chunk predicate is `LBD-D2`'s fallback and it is EXACT, not an approximation: every
    stage through `user_contribtion_mbids` partitions by `user_id`, so only the final
    cross-user SUM crosses a chunk boundary. Chunks are unioned and re-summed once.
    """
    to_date = datetime.fromisoformat(DUMP_END_TIMESTAMP).replace(tzinfo=None)
    from_date = to_date - timedelta(days=p.days)
    glob = (dump / "*.parquet").as_posix()
    chunk = f"AND user_id % {user_mod} = {user_rem}" if user_mod else ""
    con.execute(
        f"""CREATE OR REPLACE VIEW artist_similarity_listens AS
            SELECT user_id, listened_at, recording_msid, recording_mbid,
                   artist_credit_id, artist_credit_mbids
              FROM read_parquet('{glob}')
             WHERE listened_at >= TIMESTAMP '{from_date.isoformat(sep=" ")}'
               AND listened_at <  TIMESTAMP '{to_date.isoformat(sep=" ")}'
               {chunk}"""
    )


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _working_set_gb() -> float | None:
    """Current working set for this process, GB. None rather than a wrong number.

    argtypes/restype are set EXPLICITLY and the BOOL return is checked. Without them the
    64-bit HANDLE is truncated to c_int and the call silently reports 0 -- which is exactly
    what the first version of this function did, and a peak memory of 0.0 GB is not a
    plausible reading for a query that ran for an hour. LBD-G4 gates on this number, so a
    silent zero would have made the gate unable to fire.
    """
    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.GetCurrentProcess.argtypes = []
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD
        ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        ok = psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
        )
        if not ok:
            return None
        return counters.PeakWorkingSetSize / 2**30
    except Exception:
        return None


def dir_size_gb(path: Path) -> float:
    if not path.exists():
        return 0.0
    total = 0
    for f in path.rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except OSError:
            pass  # DuckDB deletes spill files under us; a vanished file is not an error.
    return total / 2**30


class Sampler(threading.Thread):
    """Poll peak working set and SPILL VOLUME while the query runs.

    Spill has to be sampled DURING the query: DuckDB deletes its temp files on completion,
    so measuring the directory afterwards always reports ~0 and LBD-G3's 500 GB spill bound
    could never fire. The first version of this script measured it afterwards.
    """

    def __init__(self, temp_dir: Path, interval: float = 5.0) -> None:
        super().__init__(daemon=True)
        self.temp_dir = temp_dir
        self.interval = interval
        self.peak_rss_gb = 0.0
        self.peak_spill_gb = 0.0
        self._stop_event = threading.Event()

    def run(self) -> None:
        while not self._stop_event.is_set():
            ws = _working_set_gb()
            if ws is not None:
                self.peak_rss_gb = max(self.peak_rss_gb, ws)
            self.peak_spill_gb = max(self.peak_spill_gb, dir_size_gb(self.temp_dir))
            self._stop_event.wait(self.interval)

    def stop(self) -> None:
        # NOT `self._stop`: threading.Thread ALREADY has a private _stop() method, and
        # shadowing it with an Event makes Thread.join() call the Event and raise
        # "'Event' object is not callable" -- after the query has finished but BEFORE the
        # manifest is written, so the run's identity and timings are lost and the work has
        # to be repeated. That happened once here.
        self._stop_event.set()
        self.join(timeout=self.interval * 2)


def connect(
    memory_limit_gb: int, temp_dir: Path, threads: int | None
) -> duckdb.DuckDBPyConnection:
    temp_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"PRAGMA memory_limit='{memory_limit_gb}GB'")
    con.execute(f"PRAGMA temp_directory='{temp_dir.as_posix()}'")
    if threads:
        con.execute(f"PRAGMA threads={threads}")
    con.execute("PRAGMA preserve_insertion_order=false")
    return con


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="LB's build_sessioned_index in DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--dump",
        type=Path,
        default=Path(
            r"D:/unsung-large-data/listenbrainz-spark-dump-2647-20260901-000002-full"
        ),
    )
    ap.add_argument("--inputs", type=Path, default=Path(r"D:/unsung-large-data/lbd-inputs"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--days", type=int, default=7500)
    ap.add_argument("--session", type=int, default=300)
    ap.add_argument("--contribution", type=int, default=3)
    ap.add_argument("--threshold", type=int, default=10)
    ap.add_argument("--limit", default="100", help="integer, or 'none' for no rank cut")
    ap.add_argument("--skip", type=int, default=30)
    ap.add_argument("--pairing", choices=("listen", "distinct"), default="listen")
    ap.add_argument(
        "--no-redirects", action="store_true", help="T3-D6: reproduce the un-redirected frame"
    )
    ap.add_argument("--user-mod", type=int, default=None)
    ap.add_argument("--user-rem", type=int, default=0)
    ap.add_argument("--memory-limit-gb", type=int, default=24)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--temp-dir", type=Path, default=Path(r"D:/unsung-large-data/duckdb-temp"))
    ap.add_argument(
        "--buckets",
        type=int,
        default=64,
        help="stage 0: partition the output by user_id %% N so stage 1 chunks without rescans",
    )
    ap.add_argument(
        "--emit-listens",
        action="store_true",
        help="stage 0: project the dump once onto fast storage (small windows only)",
    )
    ap.add_argument(
        "--from-listens",
        type=Path,
        default=None,
        help="read a materialised stage 0 instead of the dump",
    )
    ap.add_argument(
        "--emit-sessions",
        action="store_true",
        help="materialise sessions_filtered only (stage 1 of 2); every arm shares it",
    )
    ap.add_argument(
        "--from-sessions",
        type=Path,
        default=None,
        help="do the pair work from a materialised sessions parquet (stage 2 of 2)",
    )
    ap.add_argument(
        "--verify-credit-key",
        action="store_true",
        help="T3-D9: prove hash(artist_credit_mbids) is collision-free on this corpus, then exit",
    )
    ap.add_argument(
        "--aggregate-only",
        action="store_true",
        help="materialise T: HAVING score > 0, no rank cut (pre-registration section 1)",
    )
    args = ap.parse_args(argv)

    limit = None if str(args.limit).lower() == "none" else int(args.limit)
    p = Params(
        args.days, args.session, args.contribution, args.threshold, limit,
        args.skip, args.pairing,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    con = connect(args.memory_limit_gb, args.temp_dir, args.threads)
    register_frames(con, args.inputs, redirects=not args.no_redirects)
    register_listens(con, args.dump, p, user_mod=args.user_mod, user_rem=args.user_rem)

    if args.verify_credit_key:
        # T3-D9's precondition. A difference here invalidates every pair table the
        # narrowed pipeline produces, so this refuses rather than warning.
        rows = con.execute(
            "SELECT count(DISTINCT artist_credit_mbids), count(DISTINCT hash(artist_credit_mbids)) "
            "FROM artist_similarity_listens"
        ).fetchone()
        print(f"[lbd] distinct credit arrays {rows[0]:,}", flush=True)
        print(f"[lbd] distinct hashes        {rows[1]:,}", flush=True)
        if rows[0] != rows[1]:
            raise SystemExit(
                f"REFUSING: hash(artist_credit_mbids) collides on this corpus "
                f"({rows[0]:,} arrays -> {rows[1]:,} hashes). T3-D9 is not exact here and "
                "every pair table built with it under-counts pairs."
            )
        print("[lbd] T3-D9 verified collision-free", flush=True)
        return 0

    # THREE PATHS, and they are the same computation split at the same seam.
    #
    #   default            one shot: listens -> sessions -> pairs
    #   --emit-sessions    stage 1 only, materialising sessions_filtered
    #   --from-sessions    stage 2 only, reading a materialised sessions_filtered
    #
    # The seam is exact rather than convenient: LBD-A0..A3 vary threshold and limit, both
    # applied after the cross-user aggregation, and LBD-A4 varies pairing, applied after
    # sessions_filtered -- so NOTHING before this point differs between any of the five arms.
    # The fixture asserts the one-shot and two-stage paths agree.
    # A materialised stage 0 replaces the dump as the source for everything after it.
    listens_source = (
        f"SELECT * FROM read_parquet('{args.from_listens.as_posix()}')"
        if args.from_listens
        else listens_sql("artist_similarity_listens", "recording_length", "artist_credit")
    )

    if args.emit_listens:
        stage = "emit-listens"
        # PARTITION BY a user bucket. Stage 1's windows all partition by user_id, so a bucket
        # is self-contained: chunking by it is EXACT, and -- unlike `user_id % k` against the
        # dump -- it reads only that bucket's bytes instead of rescanning everything. That is
        # the whole point of materialising stage 0.
        sql = (
            f"SELECT *, (user_id % {args.buckets})::USMALLINT AS ubucket FROM ("
            + listens_sql("artist_similarity_listens", "recording_length", "artist_credit")
            + ")"
        )
    elif args.emit_sessions:
        stage = "emit-sessions"
        sql = sessions_from_listens_sql(listens_source, p)
    elif args.from_sessions:
        stage = "from-sessions"
        sql = pairs_sql(
            f"SELECT * FROM read_parquet('{args.from_sessions.as_posix()}')",
            p,
            apply_threshold=not args.aggregate_only,
            apply_limit=not args.aggregate_only,
        )
    else:
        stage = "one-shot"
        sql = pairs_sql(
            sessions_from_listens_sql(listens_source, p),
            p,
            apply_threshold=not args.aggregate_only,
            apply_limit=not args.aggregate_only,
        )

    print(f"[lbd] stage          {stage}", flush=True)
    print(f"[lbd] algorithm      {p.algorithm}", flush=True)
    print(f"[lbd] pairing        {p.pairing}", flush=True)
    print(f"[lbd] redirects      {not args.no_redirects}", flush=True)
    print(f"[lbd] aggregate_only {args.aggregate_only}", flush=True)
    print(f"[lbd] chunk          mod={args.user_mod} rem={args.user_rem}", flush=True)
    print(f"[lbd] out            {args.out}", flush=True)

    sampler = Sampler(args.temp_dir)
    sampler.start()
    t0 = time.time()
    if args.emit_listens:
        args.out.mkdir(parents=True, exist_ok=True)
        con.execute(
            f"COPY ({sql}) TO '{args.out.as_posix()}' "
            f"(FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (ubucket), "
            f"OVERWRITE_OR_IGNORE, ROW_GROUP_SIZE 1000000)"
        )
    else:
        con.execute(
            f"COPY ({sql}) TO '{args.out.as_posix()}' "
            f"(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 1000000)"
        )
    wall = time.time() - t0
    sampler.stop()

    target = (
        f"{args.out.as_posix()}/**/*.parquet" if args.emit_listens else args.out.as_posix()
    )
    rows = con.execute(f"SELECT count(*) FROM read_parquet('{target}')").fetchone()[0]
    manifest = {
        "script_sha256": sha256_of(Path(__file__)),
        "lb_source_sha256": "7a8516be7fb0c25b99ef63f3210029c348cf69c987a3ce540f325262e4b90de3",
        "dump": str(args.dump),
        "dump_end_timestamp": DUMP_END_TIMESTAMP,
        "inputs": str(args.inputs),
        "redirects_applied": not args.no_redirects,
        "params": asdict(p),
        "algorithm": p.algorithm,
        "stage": stage,
        "from_listens": str(args.from_listens) if args.from_listens else None,
        "aggregate_only": args.aggregate_only,
        "user_mod": args.user_mod,
        "user_rem": args.user_rem,
        "out": str(args.out),
        "out_sha256": None if args.emit_listens else sha256_of(args.out),
        "out_bytes": sum(f.stat().st_size for f in args.out.rglob("*.parquet"))
        if args.emit_listens
        else args.out.stat().st_size,
        "buckets": args.buckets if args.emit_listens else None,
        "rows": rows,
        "wall_clock_s": round(wall, 1),
        "peak_rss_gb": round(sampler.peak_rss_gb, 2),
        "peak_spill_gb": round(sampler.peak_spill_gb, 2),
        "memory_limit_gb": args.memory_limit_gb,
        "duckdb": duckdb.__version__,
        "python": platform.python_version(),
        "finished_utc": datetime.utcnow().isoformat() + "Z",
    }
    manifest_path = (
        args.out / "MANIFEST.json" if args.emit_listens else args.out.with_suffix(".manifest.json")
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(
        f"[lbd] rows {rows:,}  wall {wall / 60:.1f} min  peak RSS {manifest['peak_rss_gb']} GB  peak spill {manifest['peak_spill_gb']} GB",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
