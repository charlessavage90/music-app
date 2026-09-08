# `LBD-` Tasks 3 and 4 — retained execution log

**Role: ACTIVE.** The per-task record for `LBD-` Tasks 3 (the reimplementation) and 4 (the
fidelity run and the pair-table read). Appended **per task, as the work happens**, not at
closeout — that is what makes the next session interchangeable with this one rather than
making this one precious.

**It owns no figures and no status.** Task 3's and Task 4's figures are owned by
[`builder/analysis/2026-09-08-lbd-similarity/README.md`](../../builder/analysis/2026-09-08-lbd-similarity/README.md);
Task 1's inputs by
[`builder/analysis/2026-09-07-lbd-inputs/README.md`](../../builder/analysis/2026-09-07-lbd-inputs/README.md);
status by [`NEXT.md`](NEXT.md). Cited, never restated.

**Governing document:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
including `LBD-AM1` in its §12. The design and the plan are **deliberately unedited**; §10
there is the register of what the pre-registration amends in each.

**Worktree:** `C:\Users\charl\worktrees\music-app-lbd`, branch `lbd-task3`. A second session
is live in the main tree on `LUX-4`; separate worktrees mean separate index and HEAD, so the
only genuine contention is machine resources and the three documents nearly every session
touches.

---

## Session opening — the worktree was 24 commits stale, and that mattered

`lbd-task3` sat at `e6d6f94`, the PR #109 merge. `main` had moved 24 commits ahead, and
`LBD-AM1` — the amendment that adds the residual-set stratum to `LBD-C2a` — landed with the
`DFA-` work in that gap. **The worktree's copy of the governing document did not contain the
amendment governing the read this session exists to take.** `NEXT.md` flags exactly this
(`LBD-AM1` "is usable only in a tree that has it — `git log` answers whether yours does"), and
the answer here was no.

`e6d6f94` is an ancestor of `main`, so `git merge --ff-only main` resolved it with no merge
commit and nothing to reconcile. Recorded because the failure mode is silent: every arm would
have run, every figure would have been right, and the stratified read `LBD-AM1` requires would
simply never have been taken.

---

## Task 3 — `lbd_similarity.py`, and what the transcription found

**Committed artefacts:** `builder/analysis/2026-09-08-lbd-similarity/lbd_similarity.py` (the
transcription) and `lbd_fixture.py` (the synthetic sub-check).

### The source was re-fetched, and it had not moved

`listenbrainz_spark/similarity/artist.py` pulled from master by URL, sha256
`7a8516be…b90de3`, 161 lines — **byte-identical to the sha the pre-registration pinned on
2026-09-07.** So the structural finding in its §1 still holds against today's master, and
`threshold` and `limit` remain the only two tokens applied after the cross-user aggregation.
That is what licenses the one-pass restructure: `LBD-A0`–`LBD-A3` are filters over one
materialised table `T`, not four full-history runs.

### Eight deviations, namespaced `T3-D1`–`T3-D8`

The series is namespaced because the design already owns `LBD-D1`–`LBD-D8` as *decisions*,
and the first draft of the script put a bare `D6` (the redirect arm) two lines from a citation
of `LBD-D6` (the pairing semantics) — two different objects, one token. Collision-checked
across every ref before renaming: `T3-D`, `T3-P`, `T3-M` all free.

Five were foreseen by the plan or the review. **Three were not, and two of those would have
silently corrupted the fidelity run:**

- **`T3-D3` — DuckDB's cast rounds where Spark's truncates.** `CAST(<double> AS BIGINT)` gives
  3 for 2.7 here and 1 for 0.5; Spark truncates toward zero. The cast appears twice in LB's
  SQL, and the consequential one is `BIGINT(SUM(part_score))` at `artist.py:86`, immediately
  above `HAVING score > {threshold}`. A literal transcription inflates scores across a strict
  threshold boundary — a pair scoring 10.7 would pass a threshold of 10 that LB fails it on.
  Replaced with `TRUNC(...)::BIGINT` in both places.

- **`T3-D8` — DuckDB's `count_if` returns NULL where Spark's returns 0.** This one was found
  by the fixture, not by reading, and it is the more serious of the two. `session_id` is
  `COUNT_IF(difference > {session}) OVER w`. Every user's **first** row has `difference` NULL,
  because `LAG` has nothing to look back at. DuckDB's `count_if` over an all-NULL frame
  returns NULL (verified directly); Spark's is a count and returns 0. A NULL `session_id` then
  never satisfies `USING (user_id, session_id)` at `artist.py:71` — so a literal transcription
  **silently deletes every user's first listen from every pair it would have formed.** No
  error, no warning, a plausible-looking pair table, and a fidelity deficit that §6 of the
  design pre-authorises calling lineage drift. Replaced with
  `SUM(CASE WHEN … THEN 1 ELSE 0 END)`, which is exact.

- **`T3-D2` — the order is made total, but only where LB's is undefined.** `LBDR-F3` is right
  that `(listened_at, recording_msid)` breaks no tie for the fan-out rows; the key needs
  `position`. But the correction has a second half the review did not need to reach: LB's
  `session_id` aggregate carries **no explicit frame**, so it is `RANGE UNBOUNDED PRECEDING TO
  CURRENT ROW`, under which every peer at the same `listened_at` is in frame — which makes
  that aggregate **well-defined under LB's own nondeterministic order.** Re-ordering it by our
  tiebreak would silently convert it to ROWS semantics and change a value LB computes
  deterministically. So the script uses **two windows**: the offset functions (`LAG`, `LEAD`)
  take the total order, because they are nondeterministic in LB regardless and we are choosing
  a representative; the aggregate keeps RANGE over `listened_at`, because it is not.

`T3-D6` is `LBDR-F4`'s redirect arm, taken rather than deferred — see below. `T3-D1`
(`to_date` pinned), `T3-D4` (`bool_or`), `T3-D5` (`epoch`) and `T3-D7` (`--pairing distinct`,
which is our arm and not a transcription) are the mechanical remainder.

### Three properties of LB's job reproduced rather than fixed

Named `T3-P1`–`T3-P3` in the script. The one worth flagging to a later reader is **`T3-P1`,
the fan-out eating its own first row**: for an N-artist credit, rows 2..N get
`difference = t − t − duration = −duration`, so `skipped` fires on rows 1..N−1 for any track
longer than `skip` seconds and `sessions_filtered` drops them. On a two-artist credit over 30
seconds **exactly one of the two artists survives** — the one sorting last. This is LB's
behaviour, it is reproduced deliberately, and it is why `T3-D2`'s tiebreak is a recorded
decision rather than a detail: the tiebreak decides *which* artist survives.

`T3-P2`: every user's last listen is discarded, because `LEAD` is NULL there and `WHERE NOT
skipped` is not satisfied by NULL. `T3-P3`: the self-join is unordered, so every pair is
counted twice before the per-user cap — which means `contribution` bites at half the
co-listens it appears to.

### The fixture, and the rule it exists to satisfy

The pre-registration's §6 requires the expected values to be derived **by executing LB's SQL
by hand**, because a fixture built from the plan's prose would agree with a wrong
implementation and disagree with ListenBrainz — and would surface **never**. The derivation is
written out stage by stage in the fixture's docstring so it can be checked without trusting
either file.

Five users, twenty-one listens. Both specifics the pre-registration names by hand are
asserted:

- **the window frame** — in "A feat. B" with the phrase stored unspaced, `after_ft_jp` is true
  for **A**, the main artist, because MusicBrainz's join phrase is the text *following* that
  artist and the frame includes the row's own; and true for **B** through the cumulative
  frame. Both weighted 0.25. The plan's prose says the opposite.
- **the untrimmed comparison** — the same credit stored as `' feat. '` matches none of LB's
  eight literals, and both artists stay at weight 1.

Making the frame assertion bite needed a deliberate fixture design decision: every featured
credit long enough to trigger `T3-P1` loses its first row, which is exactly the row the frame
question is about. User 4's track is **20 seconds**, under `skip`, so both members of the
credit survive and the assertion has something to bind to.

**The check was shown to go red before it was allowed to go green.** Six mutants patch one
thing each into the generated SQL — trimmed join phrase, strictly-preceding frame, `CAST` for
`TRUNC`, `row_number` for `rank`, no mapped-listen filter, literal `COUNT_IF` — and each must
move the answer. All six do. A fixture that has never failed is not evidence that anything
passed; `T3-M6` exists because that mutant is the defect the fixture actually caught on its
first run.

### `LBDR-F4`'s redirect table was taken, not deferred

Task 1 §5 deferred `recording_gid_redirect` to `LBD-S2` — this stage — noting the unmatched
share is only measurable against the frame that consumes it. LB's own frame
(`data/postgres/recording.py:16-33`) resolves redirects, so a redirected gid carries its
target's length; without it those listens fall to the 180-second default, which shifts
`difference`, session boundaries **and** the skip test one way. It is the one input difference
that is reproducible rather than irreducible, and design §6 would have pre-authorised calling
it lineage.

The script takes both sides: the redirect arm is on by default and `--no-redirects`
reproduces the un-redirected frame, so the size of the difference is **measurable rather than
argued**. The fixture asserts the two configurations differ, on a user sized so the duration
decides a skip.

---

## Task 4 — the fidelity run

*(appended as it happens)*

### The scale probe, and why it was run before `LBD-G4` rather than instead of it

`LBD-G4` pre-registers a `user_id % 16` slice before the full pass, because the size of `T`
is the one quantity nothing on disk bounds. A 1-in-16 slice is not cheap, so a **1-in-256**
slice was run first — same code path, same pipeline, purely a resource measurement and not an
arm. Figures are owned by the analysis README.

It ran with `--no-redirects`, because the redirect frame was still extracting and durations
shift row counts negligibly. That makes it a **cost measurement and nothing else**; no
criterion is read off it.

**Two measurement defects in this session's own script were found by it, and both would have
disabled a pre-registered gate:**

1. **Peak memory reported `0.0 GB`.** The `ctypes` call had no `argtypes`/`restype`, so the
   64-bit process handle was truncated and the call failed silently — and the failure was not
   checked. `LBD-G4` gates on peak memory above 24 GB, so a silent zero means **the gate can
   never fire.** Fixed: explicit types, and the `BOOL` return is checked.
2. **Spill was measured after the query finished**, by which time DuckDB has deleted its temp
   files — so it always reported ~0. `LBD-G3` fires on spill above 500 GB, so that bound was
   equally unable to fire. Fixed: a sampler thread polls working set and spill volume **during**
   the run and keeps the maxima.

Recorded because the shape generalises and this project has met it before: **an instrument
that reports a comfortable number because it is broken is indistinguishable from one
reporting a comfortable truth.** Both defects produced values on the safe side of their gate.

### Disk starvation, walked into with the warning already read

The `LBD-` handoff records that two long jobs on this machine "saturated `D:` and starved
each other, one to about 1 second of CPU in twenty minutes". This session read that, then ran
the redirect extraction, the 1-in-256 probe and a full-dump scan concurrently — all three
reading `D:`. Measured mid-run: the extraction's `bzip2` had consumed **360 s of CPU in 82
minutes of wall clock, about 7 % utilisation.** It was not wedged; it was starved, by this
session.

The reusable form is narrower than "don't run two jobs". `bzip2` is single-threaded and
CPU-bound on a 7.5 GB file, so it *looks* like it should coexist with anything — the
contention is not for CPU but for **sequential read bandwidth on the same spindle**, against a
scan reading two orders of magnitude more data. **Check what a job contends FOR, not how big
it looks.**

### The dump lives on a spinning disk, and that is the whole cost story

**`D:` is `ST3000DM008` — a 3 TB SATA hard disk. The volume's own label is "Slow Storage".**
Nothing in the plan, the design, the pre-registration or Task 1's README says so; every cost
estimate in the track was written as though storage were uniform.

Measured mid-scan: **~35 MB/s read, with a disk queue length of 13–14.** DuckDB defaults to
one thread per core (24 here) and the dump is 1,409 files, so a dozen threads issue concurrent
reads across the platter and **sequential streaming degrades into seek thrash.** On an SSD
more readers is free; on a platter it is the dominant cost.

This explains the 1-in-256 probe cleanly. The probe read the same ~127 GB of needed columns as
a full pass would, because `user_id % 256 = 0` prunes rows, not bytes — so **almost all of its
63.7 minutes was the scan, and almost none was the per-user work.** The naive reading of that
probe ("64 minutes for 1/256, so 256× that for everything") is wrong by more than two orders
of magnitude, and it is wrong in the direction that would have made the track look impossible.

**It also inverts the pre-registration's fallback.** `LBD-D2`'s chunked form is exact and is
named as the safe option when the full pass is too big — but each chunk **re-reads the entire
dump**, so sixteen chunks is sixteen scans of a 35 MB/s disk. On this hardware the fallback is
the expensive path, not the cheap one. The pre-registration could not have known this; it
predates the measurement.

Two facts that matter for whatever runs next, and neither was known when the plan was written:

- **`C:` is a Samsung 980 PRO NVMe with ~582 GB free**, and `E:` a 970 EVO NVMe with ~300 GB
  free. The dump is 214 GB total; the columns this job needs are a subset of that.
- **DuckDB's spill directory was pointed at `D:`** — the slow disk — by this session's own
  scripts. Every gate the pre-registration sets on spill volume assumed spilling was merely
  large, not that it was landing on the slowest device in the machine.

**Thread count on a platter, measured.** Same query, three thread settings, a different
18-file span each time so nothing was served from the OS cache. Figures owned by the analysis
README. **Cutting DuckDB from 12 threads to 1–2 roughly doubles read throughput**, and the
difference between 1 and 2 is inside the noise. DuckDB defaults to one thread per core, so the
default is the wrong setting here by a factor of two — and the 35 MB/s seen mid-scan was
contention on top of that, not the floor.

**The correction this forces to my own earlier reasoning:** on the strength of the 1-in-256
probe alone I had the full pass somewhere between 14 and 180 hours. Both numbers came from
treating the probe's 63.7 minutes as mostly per-user work. It is mostly scan, the scan is
mostly avoidable overhead, and the honest position is that **the split between the two is
still unmeasured** — which is what the next two runs are for, and why they hold thread count
constant and vary only the slice fraction.

### A third defect in this session's own instruments, and this one destroyed a run

The `Sampler` thread added to fix the previous two stored its stop flag as `self._stop`.
**`threading.Thread` already has a private `_stop()` method**, so `Thread.join()` called the
Event and raised `'Event' object is not callable` — *after* the 30-minute query had finished
but *before* the manifest was written. The parquet survived; the run's recorded identity,
timings and memory figures did not.

Three instrument defects now, all in code written to measure rather than to compute: a memory
reading that was silently zero, a spill reading taken after the evidence was deleted, and a
crash in the fix for both. **The measurement scaffolding has been less reliable than the
transcription it exists to check** — which is an argument for keeping the manifest write
before anything optional, not for writing fewer instruments.

### `LBD-G4`'s own slice could not be run as configured — and the reason is a configuration error, not the data

The pre-registered `user_id % 16` slice was launched with a 20 GB DuckDB memory limit on a
31.7 GB machine and **was killed for exhausting memory.** Its spill directory was **0 bytes at
the time of death**: it grew in RAM rather than spilling.

Nothing else on the machine was implicated — the largest other process held 0.58 GB and 17.3
GB was free once the query died. This was one process, configured wrong by this session.

**Two things worth separating**, because they point in opposite directions:

1. **The configuration error is mine and is fixed.** A memory limit set to two-thirds of
   physical RAM, on a machine with a second session live, leaves no headroom for the query's
   own un-accounted allocations. Re-run at 8 GB with spill on the NVMe.
2. **It is nonetheless evidence about the data.** The 1-in-16 slice's aggregation wants more
   than ~20 GB resident, which is a real fact about the shape of the pair table and is the
   sort of thing `LBD-G4` exists to discover before the full pass rather than during it.

**What must NOT be concluded yet:** that `LBD-G4` fires. Its memory arm is *"the slice
extrapolates to a full-pass peak memory above 24 GB"*, and a killed run yields **no peak
memory reading at all** — the number is missing, not high. Reading a crash as a gate firing
would be inventing a measurement from an absence, which is the same move as reading a broken
instrument's comfortable zero as a comfortable truth. The gate is read off the re-run.

### The gate slice OOMs on its own terms, and the suspect is a column type

Re-run at an 8 GB limit with spill on the NVMe, the `user_id % 16` slice failed with DuckDB's
own error rather than an OS kill:

    OutOfMemoryException: failed to allocate data of size 256.0 KiB (7.4 GiB/7.4 GiB used)

It **had** spilled — 449 MB to the NVMe — and then could not spill further. So this is not
"the limit was too low"; something in the pipeline is not spillable.

**The suspect, stated as a hypothesis before it was tested:** `artist_credit_mbids` is a
`VARCHAR[]`, and it is carried through every windowed stage — a sort of roughly 195 million
rows partitioned by `user_id` — and then through a self-join on `(user_id, session_id)` whose
build side is the same magnitude. DuckDB's out-of-core support for nested types in window and
join operators is materially weaker than for flat ones. The column is used for exactly one
thing: the equality predicate `s1.artist_credit_mbids != s2.artist_credit_mbids` at
`artist.py:73`.

**So the fix under test is to replace it with a `BIGINT` key through those stages** — which is
only legitimate if the substitution is *exact*, not merely usually right. A hash collision
would make two genuinely different credits compare equal and would **silently suppress real
pairs**, in the direction that quietly lowers supply. Tested directly by comparing
`count(DISTINCT artist_credit_mbids)` against `count(DISTINCT hash(artist_credit_mbids))` on
the corpus rather than assuming 64 bits is enough.

**Not yet known, and not to be assumed:** whether the window or the self-join is the actual
consumer. Narrowing the column helps both, so the fix does not depend on resolving that — but
the report must not claim the window was the cause on this evidence.

### `T3-D9` — the LIST column narrowed to a key, and a fixture hole it exposed

`artist_credit_mbids` is a `VARCHAR[]` carried from `listens` to the self-join, where LB uses
it for exactly one thing: `s1.artist_credit_mbids != s2.artist_credit_mbids` (`artist.py:73`),
which stops two artists on the same track pairing with each other. Replaced with
`hash(...) AS credit_key`, a BIGINT, through every windowed stage.

**Verified before adoption, not assumed:** `count(DISTINCT artist_credit_mbids)` against
`count(DISTINCT hash(...))` on a 1-in-64 user slice — 430,644 against 430,644, collision-free.
A collision would make two different credits compare equal and **suppress real pairs**, biasing
supply *downward*, which is the direction that makes this track's central question look
answered when it is not. `--verify-credit-key` now runs that check and **refuses** on any
difference, rather than warning.

**The fixture hole this uncovered is the more interesting half.** A mutant deleting the
same-credit predicate entirely **did not move the answer**, so the fixture had never been
testing `artist.py:73`. The reason: the only two-artist credit in it belonged to a *featured*
pair at weight 0.25, so the suppressed pair was worth 0.125 — and `TRUNC` at the cross-user sum
absorbed it completely. The assertion existed, looked right, and covered nothing.

Fixed by adding a user whose two-artist credit carries **no** join phrase, so both artists
weigh 1 and the suppressed pair is worth 2. Its three artists appear nowhere else, so no
existing expectation moves. Seven mutants now, all red.

**The generalisable form: a rounding or truncation step downstream of an assertion can make
that assertion untestable, and it does so silently.** The mutant is what found it — reading the
fixture would not have, and did not. This is the second time today the mutants caught something
reading the code did not.

### Diagnosed by splitting, not by guessing again: it is the windows

`T3-D9`'s narrowing did **not** fix the OOM — the slice died again at 9.3 GiB. **The hypothesis
that the LIST column was the binding constraint was wrong**, and it is only not a false claim
in this record because it was written down as an untested hypothesis rather than a finding.

Rather than guess a third time, the pipeline was split at its natural seam — `sessions_sql`
(LB's `listens` → `ordered` → `sessions` → `sessions_filtered`, `artist.py:20-63`) and
`pairs_sql` (`:64-102`) — and stage 1 was run alone on the same slice. **It OOMs too, at 9.3
GiB, with no join and no aggregate in the query at all.** So the consumer is the windowed
stages: three window specifications over roughly 195 million rows partitioned by `user_id`.

**The seam is worth having on its own merits, and this is the argument rather than the excuse:**
every arm shares stage 1 exactly. `LBD-A0`–`LBD-A3` vary `threshold` and `limit`, both applied
after the cross-user aggregation; `LBD-A4` varies pairing, applied after `sessions_filtered`.
Nothing before that point differs between any of the five. It is the same move the
pre-registration already makes one stage later when it derives four arms from one `T`. The
fixture asserts the one-shot and two-stage paths agree, so the split cannot drift from the whole.

### The constraint that actually governs what to do next

**Every experiment costs a full scan of the dump.** `user_id % k` prunes *rows*, not *bytes* —
the columns still have to be read to evaluate the predicate — so a 1-in-256 slice and a full
pass read the same ~127 GB. On a 250 MB/s platter that is 20–30 minutes **per attempt,
regardless of how small the slice is.**

That is what makes the pre-registration's chunked fallback unaffordable here, and now with a
number rather than an argument: stage 1 does not fit at 1-in-16, so chunking would need 1-in-32
or finer, and **32 chunks is 32 rescans — north of thirteen hours of reading before any work is
counted.**

**So the intermediate is not an optimisation, it is the thing that makes the track affordable
on this machine**, and that is a measured conclusion rather than a preference. Its size is
**estimated, not measured** — roughly 50 GB, derived from Task 1's per-column compressed sizes
with the two 36-character identifier columns replaced by keys and `artist_mbid` left to
dictionary-encode. **Nobody has written it yet, and the estimate should not be cited as a
figure.**

### `T3-D10` and the three-stage shape, approved by the owner 2026-09-08

The owner approved staging onto `C:`. The pipeline is now three stages, split where the
memory behaviour changes:

| stage | LB's lines | window partitions | why it splits here |
|---|---|---|---|
| **0** `listens_sql` | `:20-36` | one **listen** | tiny partitions, nothing sorted at scale — materialisable |
| **1** `sessions_from_listens_sql` | `:37-63` | one **user** | the big sort; this is what exhausted memory |
| **2** `pairs_sql` | `:64-102` | — | self-join and aggregation |

Stage 0 is written **partitioned by `user_id % 64`**. Every window in stage 1 partitions by
`user_id`, so a bucket is self-contained and chunking by it is exact — and unlike `user_id % k`
against the dump, it reads **only that bucket's bytes** instead of rescanning 127 GB. That is
the entire point of materialising it.

**`T3-D10` — both 36-character identifier columns are dropped, exactly.** `recording_mbid` is
used only for the duration join and the featured-weight partition, both inside stage 0.
`recording_msid` is used for nothing in LB at all — it is *ours*, the tiebreak `T3-D2` adds —
and it can only ever break ties among rows sharing a user *and* a second, so stage 0 emits its
dense rank within exactly that group. A dense rank is order-preserving on the group it ranks,
so the substitution is identical, not approximate.

**Deliberately NOT a hash, and the reason is arithmetic.** A 64-bit hash over ~2.4 billion
near-unique msids has roughly a one-in-six chance of at least one collision by the birthday
bound, and a collision would silently make the order non-total again — reintroducing the exact
nondeterminism `T3-D2` exists to remove. The dense rank has no such failure mode. `T3-D9`'s
hash is safe by the same arithmetic run the other way: ~2 million distinct credit arrays, not
2.4 billion, and it was measured collision-free before adoption rather than assumed.

**A one-byte ordinal was not enough, and only real data said so.** `msid_ord` overflowed at
**477** on the first real file: an account logged 477 distinct recordings inside a single
second — a bulk import or a bot. Widened to four bytes. Reading the code would not have
produced that number, and the end-to-end test on one real file cost about a second.

### `T3-D11` — stage 0 has no window functions at all, and why it took three attempts to get there

**Three wrong models of the memory behaviour, each costing a full scan:**

1. the `VARCHAR[]` column is the constraint — **wrong**, the narrowed pipeline still died;
2. small window partitions are safe — **wrong**, stage 0's partitions are a *single listen*
   and it died at the same 9.3 GiB;
3. implicitly, that DuckDB streams window functions — **wrong**. It **materialises the entire
   input** to a window operator regardless of partition size. That is the actual constraint,
   and none of the three attempts was needed to discover it: it is a property of the engine,
   not of this data.

**The generalisable failure is not carelessness.** Every experiment here costs the same ~127 GB
scan whatever the slice size, so measuring *feels* like the expensive option and reasoning
feels like the cheap one. It is the other way round: one measurement would have cost less than
three wrong guesses did. **When measurement is expensive, that is an argument for measuring
sooner, not for thinking harder first.**

**`T3-D11`: stage 0 now contains no window at all**, rather than smaller ones.

- **The featured-artist flag is precomputed on the credit frame.** LB computes it per listen,
  but the value depends only on which join phrases sit at positions ≤ this one *within that
  credit* — so it is a function of `(artist_credit_id, position)` and nothing else, computable
  once over 7.17M rows instead of billions. **One case is not identical and is stated in the
  code rather than buried:** one user, two listens, same second, same `recording_mbid`,
  *different* credits would have shared a partition in LB. Measurable from the intermediate.
- **The msid ordinal moves to stage 1**, which is chunked by user bucket and therefore small.
- **Both 36-character identifier columns become `UUID`** — which is what they already are, so
  the cast is exact, and canonical-hex string order agrees with 128-bit numeric order so
  sorting is unchanged. 16 bytes instead of 36.

**Then a fourth, different failure: the partitioned write itself.** The windowless stage
streamed correctly and had written **21 GB across all 64 buckets** when the harness killed it
for system memory. A partitioned write holds one open parquet writer per bucket, each buffering
a full row group — so the cost is `buckets x row_group_size x row width`, which at
64 x 1,000,000 is gigabytes that **DuckDB's `memory_limit` does not account for.** Row groups
cut to 20,000. Recorded because the number that mattered was not the memory limit at all.

**And the size estimate moved.** Dropping the windows means carrying the raw msid rather than
a one-byte ordinal, so the intermediate is now expected at **70–85 GB rather than ~50**. The
owner approved staging on `C:` (578 GB free) and was told the number changed.

### A fixture guard that earned its place

Moving the featured-weight logic into the credit frame silently broke two mutants' patch
targets — `T3-M1` and `T3-M2` could no longer find the text they mutate. **They did not fail;
they would have reported nothing at all.** The mutant runner checks `if needle not in source`
and fails loudly, which is the only reason this surfaced. A mutation check that cannot locate
its target is not passing, it is blind, and it looks exactly like passing.

### The testbed, and what one controlled measurement said that four guesses did not

**Built the thing that should have existed before the first wrong guess:** 100 dump files
**hardlinked** into a directory on the same volume — 16 GB addressable, **no extra disk
consumed**, and a full stage-0 run over it costs about four minutes instead of twenty-five.
That single change converts "measuring is expensive" into "measuring is cheap", which is what
had been distorting every decision in this stretch.

Then one controlled comparison: identical query, identical everything, **one variable** — the
write mode.

| write mode | rows out | wall | peak RSS | spill | output |
|---|---:|---:|---:|---:|---:|
| `PARTITION_BY` (64 buckets) | 195,719,125 | 7.3 min | 5.09 GB | **111.2 GB** | 4.33 GB |
| flat | 195,719,125 | 4.1 min | 5.15 GB | **15.7 GB** | 3.36 GB |

**Peak memory was never the problem.** Both runs sit at the 5 GB limit — DuckDB was respecting
`memory_limit` the whole time. The partitioned write **spills 111 GB to produce a 4 GB
output**, and it is that write pressure, not resident memory, that had been killing the
machine. Every earlier fix aimed at the memory limit was aimed at the wrong quantity.

**So stage 0 writes flat**, and stage 1 filters `user_id % 64` on read. A 47 GB intermediate
re-read 64 times from NVMe is roughly 25 minutes in total — affordable, where 64 re-reads of
the dump would have been over twenty-six hours.

**Extrapolated from the testbed** (100 of 1,409 files, and reported as an extrapolation, not a
measurement): ~2.8 billion rows and **~47 GB** for the flat intermediate, close to the original
~50 GB estimate and below the 70–85 GB the windowless design was feared to cost. ~58 minutes.

**The reusable lesson is about proportion, not care.** Four attempts were spent tuning a knob
(`memory_limit`, then `ROW_GROUP_SIZE`) that the measurement shows was never binding. A
hardlinked subset costs seconds to build and would have shown that before any of them. **When
each experiment is expensive, build the cheap experiment first** — the instinct to skip
straight to the real run is exactly backwards.

### `T3-D12` — it was the join build side, and spill went to zero

Measured on the testbed, one variable, everything else held:

| stage-0 frames | wall | peak RSS | spill | out |
|---|---:|---:|---:|---:|
| `VARCHAR`-keyed views over parquet | 4.1 min | 5.15 GB | **15.7 GB** | 3.36 GB |
| **`UUID`-keyed materialised tables** | **2.8 min** | 4.9 GB | **0.0 GB** | 3.88 GB |

**Spill to zero, and 1.5× faster.** `recording_length` is 40M rows keyed on a **36-character
string**, so its hash table did not fit a sane memory limit and DuckDB spilled it — over and
over, once per probe batch, because a *view* is re-read and re-hashed rather than built once.
Two changes, both exact: the key becomes `UUID` (16 fixed bytes — recording MBIDs already ARE
UUIDs, so the cast is lossless, with `TRY_CAST` and a count because a silently NULL key would
drop the duration and re-create the very `LBDR-F4` defect this track already fixed), and both
frames are `CREATE TABLE` rather than views.

**Every earlier diagnosis in this stretch was of a symptom.** The process sat obediently at its
memory limit the whole time; spilling is what DuckDB does *correctly* when a build side does
not fit. Reading "spill" as "memory pressure" is what produced four fixes to `memory_limit`,
`ROW_GROUP_SIZE` and `PARTITION_BY`, none of which touched the cause.

**Extrapolated, and labelled as extrapolation:** ~2.76 bn rows, **~55 GB**, ~40 minutes for the
full dump. The testbed ran `days=20000` and the real run uses `days=7500`, so the true figures
are somewhat smaller.

### The mutants went blind a second time, in a different way

`T3-D11` moved the featured-artist flag out of the query into the credit frame; `T3-D12` then
moved the frame out of the query text entirely into `register_frames`. **Both times `T3-M1`
and `T3-M2` — the two specifics the pre-registration names by hand — stopped being able to
find what they mutate.** They did not fail; they had nothing to report.

The fixture now carries **frame-level mutants** with their own target assertion, alongside the
query-level ones. **A structural refactor silently disarming the checks that guard the
subtlest semantics is now a twice-observed pattern here, not a one-off** — and on both
occasions the only thing that caught it was a guard that fails loudly when a mutation cannot
locate its target. Any mutation-style check needs that guard; without it, blind is
indistinguishable from green.
