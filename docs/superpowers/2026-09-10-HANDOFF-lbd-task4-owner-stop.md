# Handoff — `LBD-` Task 4 complete, the owner stop reached, 2026-09-10

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-08-HANDOFF-lbd-task4-midflight.md`](2026-09-08-HANDOFF-lbd-task4-midflight.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**A SEAM handoff.** The plan's seam is after Task 4 and Task 4 is finished: the pair pass ran
to completion, `T` and the four arms exist, `LBD-C1` and `LBD-C2a` are read, and the design's
owner stop is reached. **Tasks 6 and 7 are conditional on the owner's read of the result and
do not start on a session's initiative.**

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
now with **`LBD-AM3`** in its §12 and beside §8's gate table. The design and plan stay
unedited. **Retained log:** [`2026-09-08-lbd-task34-execution-log.md`](2026-09-08-lbd-task34-execution-log.md)
(this session's entries begin at "Task 4, resumed 2026-09-09"). **Figures:**
[`builder/analysis/2026-09-08-lbd-similarity/README.md`](../../builder/analysis/2026-09-08-lbd-similarity/README.md)
§4–§6, and nowhere else.

---

## What a cold reader most needs

1. **`LBD-G1` FIRED and was OVERRIDDEN, by the owner, after diagnosis.** The top-band
   fidelity rate was below the floor on the pinned corpus. The diagnosis (README §5a–5c) names
   the input difference: ListenBrainz's deployed dataset was computed on roughly a third of
   today's listening corpus, shown by a single-knob rerun on a corpus dated by the dump's
   `created` column, whose three readings were committed before it ran. `LBD-AM3` records the
   override and says in its own text that it was written after a result existed. **Do not
   cite `LBD-C1` as "passed".**
2. **`R4` fires: the listening data is there.** Every arm reduces the added set's dead-end
   share; the corner by 3.34 points on the whole set and **9.54 on the residual stratum**.
   `LBD-R1` is refuted, `R12` does not fire. **The threshold is the lever, not the cap** — the
   cap-removed arm alone does not clear the bar on the whole set.
3. **The band-member class is identified.** About 4 % of the top band's archive entries are
   uncredited individuals (Rammstein's drummer, Meg White, Aerosmith's drummer) whom no job
   over the recording credit can pair — ListenBrainz's deployed job attributed listens to them
   by a mechanism outside the credit. This is the "central but unlistened" class the owner
   observed in July that `CCR-`, `RCC-` and `TCR-` could not attribute. A similarity table
   computed by us contains none of them. Forward notes are in `docs/README.md`'s rows for
   those records.

## Claims that must NOT be reverted

- **The bucket-4 out-of-memory was the pipeline at the margin of a 6 GB limit, not a heavy
  tail.** Measured (README §4). The handoff before this one said the opposite and proposed
  finer buckets for failures only; 12 GB cleared every bucket with no code change. The
  previous handoff's "do not raise the memory limit" was right for stage 0 and wrong for the
  pair pass, and the log says why.
- **`HAVING SUM(term) > 0` on the partial is not a lever** (266 rows of 24.5 M). Capping
  session length is unnecessary. Neither was done.
- **The per-artist quantiles `lbd_reads.py --mode c1` prints are wrong** (NaN from empty
  archive lists inside `sorted()`); the pooled rate the gate reads is unaffected. Corrected
  figures are in README §5 from `lbd_c1_diagnose.py`. The read script itself is deliberately
  unpatched for that — its printed table is superseded, not its gate statistic.
- **`--created-before` is a diagnostic filter and is never set for an arm.** Recorded in every
  manifest.
- **`LBD-G3` fired (1,724 GB summed spill against 500) and `LBD-G4` was moot** — both readings
  are in README §4 and both prescribe the chunked form that was already running. Neither is
  "passed".
- **The 3× score ratio is a lineage fact, not a bug.** Halving it by dating the corpus is the
  evidence; the residual 1.5× is recorded as unexplained in mechanism (older still, or the
  mapping grew) and sized.

## What is on disk and must not be rebuilt

| | |
|---|---|
| stage-0 intermediate, full corpus | `C:\unsung-fast\lbd-listens.parquet`, 53.9 GB, sha256 `6d77a681…` (unchanged) |
| 64 partials | `C:\unsung-fast\lbd-partials\p0..p63.parquet`, 17.1 GiB, one manifest each |
| `T` and the four arms | `C:\unsung-fast\lbd-pairs\aggregate\T.parquet` (`03d47b05…`, 689,603,622 rows) and `…\lbd-pairs\A0..A3\` — sha256s in README §6 |
| the reads | `…\lbd-pairs\A0\c1.json`, `c1_diagnosis.json`; `…\<arm>\c2a.json` and `c2a.degrees.json`; `…\lbd-pairs\c2a_compare.json` |
| dated corpus (`C1-DIAG-1`) | `C:\unsung-fast\lbd-listens-c2024q3.parquet` (`8a60e2f8…`, 901,308,413 rows), `…\lbd-partials-c2024q3\`, `…\lbd-pairs-c2024q3\` — diagnostic only |
| testbed | `D:\unsung-large-data\lbd-subset100\` — unchanged |

All under `C:\unsung-fast\` is gitignored and identified only by the checksums above.
Everything the pre-registration named as landing under `D:\unsung-large-data\lbd-pairs\`
landed on `C:` instead, for speed, with the owner's earlier approval of staging on `C:`.

## Already updated — do not redo

`docs/README.md` (rows for this handoff, the previous one, the log, the pre-registration, and
forward notes on the `TCR-` and `CAU-` rows); the pre-registration (`LBD-AM3`); `NEXT.md`;
`memory/deploy-environment-traps.md` (one trap); the README §4–§6.

## What I know that is not in the durable record

- **Nothing computed is unrecorded.** Every figure this session produced is in README §4–§6
  or in the on-disk JSON named above.
- **Decided against:** narrowing `artist_mbid` to an integer id through the pipeline (an exact
  refactor prepared as a fallback; the measurement said it was unnecessary); partitioning the
  combine and the derive by `mbid0` hash (same); an earlier-dated rerun to pin the residual
  1.5× (changes no decision).
- **Said in conversation and now filed:** the owner chose option 1 (amend and read) from three
  tabled; he asked whether the band-member class was his July observation, and it is.
- **Not done, deliberately:** `LBD-A4` (the pairing arm) — deferred past the owner stop at the
  start of the session because no `R1`–`R9` read depends on it; `LBD-M1` — a `GROUP BY` over
  tables that now exist, Task 6/7's input.

## In flight — nothing is running

No process, no listener, no dev server; ports 8000 and 5173 are clear. Every monitor this
session armed has ended. A `tail.exe` this session orphaned was killed; the trap is in memory.

## Owed, and by whom

| | |
|---|---|
| **Owner** | merge PR #113; then **the read of README §6 and the decision the design's §5 places here**: proceed to Tasks 6–7 (emit an arm, build, `LBD-C2b`, blind listen), pre-register an intermediate threshold first, or stop with the hypothesis refuted. The session's stated preference and reasoning are in the closing report and the log |
| **Owner** | the three live `TEST-QUEUE.md` entries from the 2026-09-08 deploy — untouched by this work |
| **Successor, if he proceeds** | `LBD-A4`; `LBD-M1`; then Task 6/7 under a fresh plan read, with `drop_unlistenable=False` per `LBD-X3` |
