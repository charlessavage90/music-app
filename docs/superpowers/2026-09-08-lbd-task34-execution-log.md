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
