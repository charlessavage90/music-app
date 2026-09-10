# Handoff — `LBD-` Task 3 complete, Task 4 mid-flight, 2026-09-08

**Role: SUPERSEDED on next actions, 2026-09-10**, by
[`2026-09-10-HANDOFF-lbd-task4-owner-stop.md`](2026-09-10-HANDOFF-lbd-task4-owner-stop.md) —
Task 4 finished and the owner stop was reached. Its must-not-be-reverted list still stands;
**its "open decision" section is overtaken** (the bucket-4 failure was the memory limit, not
a heavy tail — see the successor). *(Was: ACTIVE — the CURRENT handoff.)* Superseded
[`2026-09-07-HANDOFF-lbd-preregistration.md`](2026-09-07-HANDOFF-lbd-preregistration.md) on
next actions **for the `LBD-` track only**. It does **not** supersede
[`2026-09-06-HANDOFF-lux-4-artifact.md`](2026-09-06-HANDOFF-lux-4-artifact.md), which remains
current for `LUX-4`. It does **not** state project status: for that read
[`NEXT.md`](NEXT.md), which owns it.

⚠ **MID-FLIGHT.** The plan's seam is *after* Task 4. Task 4 is **not** finished — no arm has
been read, `LBD-C1` is unmeasured, and the owner stop was not reached. Retired at the owner's
instruction, not because a degradation tell fired.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
now including `LBD-AM1` **and `LBD-AM2`** in its §12. The design and plan stay unedited.
**Retained log:** [`2026-09-08-lbd-task34-execution-log.md`](2026-09-08-lbd-task34-execution-log.md)
— read it; it carries every wrong turn with its cause, and there were many.

---

## Start here

**Bucket 4 of the pair pass runs out of memory. That is the only thing between you and `T`.**

Everything upstream is done and verified. Run:

```
builder/analysis/2026-09-08-lbd-similarity/lbd_similarity.py --emit-partial \
  --from-listens C:/unsung-fast/lbd-listens.parquet --user-mod 64 --user-rem <k> ...
```

for the remaining buckets, then `--combine 'C:/unsung-fast/lbd-partials/*.parquet'` to get
`T`. Then `lbd_derive.py` for `LBD-A0`–`LBD-A3`, then `lbd_reads.py --mode c1` **before**
`--mode c2a` (result `R1`: if `LBD-G1` fires, the arms are not read at all).

**Run it detached** (`Start-Process`), not through the harness — see "in flight" below.

---

## What is on disk and must not be rebuilt

| | |
|---|---|
| **Stage 0 intermediate** | `C:\unsung-fast\lbd-listens.parquet`, **53.9 GB, 2,647,691,119 rows**, 44.3 min to rebuild from the spinning disk. **This is the expensive artifact.** sha256 `6d77a681…07707c08`; built by script sha256 `d0ae2e05…f2c1b798` from the dump pinned at `2026-09-01 00:00:02.462107+00:00`, LB source sha256 `7a8516be…b90de3`. Full manifest beside it — **it is gitignored and a checksum is the only identity it will ever have.** |
| Partials done | `C:\unsung-fast\lbd-partials\p0..p3.parquet` — buckets 0–3 only, algebraic form |
| Testbed | `D:\unsung-large-data\lbd-subset100\` — 100 **hardlinked** dump files, 16 GB addressable, **no extra disk**. A full stage-0 run over it takes ~4 min instead of ~25. **Use it before any full run.** |
| Redirect frame | `D:\unsung-large-data\lbd-inputs\recording_gid_redirect_length.parquet` |
| Fidelity sample | `builder/analysis/2026-09-08-lbd-similarity/lbd_c1_sample.tsv`, sha256 `59747e41…`, **committed, drawn before any read** |

`C:` has ~520 GB free. The owner **approved** staging on `C:`.

---

## The open decision, and what I would do

**The problem:** the pair pass is heavy-tailed. Buckets 0–3 pass (~110 s, 19–25 GB spill
each); bucket 4 dies at 5.5 GiB. `T3-D13`'s algebraic collapse removed a **896×** blow-up on
the corpus's heaviest account, but the tail is broader than that one user.

**What I would do, in order** — not a menu:

1. **Finer buckets for the failures only.** Buckets are exact at any modulus (every stage-1
   window partitions by `user_id`), and the combine step is modulus-agnostic — it globs
   partials. So a failing bucket can be re-run as `--user-mod 256` over the four residues
   that make it up, and mixed with `mod 64` partials in the same combine. **Cheapest thing
   that certainly works.**
2. **If that is still not enough, drop the zero rows.** Adding `HAVING SUM(term) > 0` to the
   partial removes rows whose net contribution is exactly zero (see the log). Safe — zero
   contributes zero to the cross-bucket sum — and it shrinks every partial. I did **not** do
   it: untested at scale, and settling it while packing up is how a shaky conclusion enters
   the record as a decision.
3. **Only then** consider capping session length, and if you do, **pre-register it** — it
   changes what is computed, unlike everything above.

**What I would NOT do:** raise the memory limit. Five separate diagnoses of this OOM were
wrong, and the one that was right showed the process sitting obediently at its limit while a
join build side spilled. Memory was never the binding quantity.

---

## Claims that must NOT be reverted

- **The transcription's thirteen deviations are each load-bearing.** Three were unforeseen and
  two would have corrupted fidelity silently: **DuckDB's cast rounds where Spark's truncates**
  (immediately above a strict threshold), and **DuckDB's `count_if` returns NULL where Spark's
  returns 0**, which deletes **every user's first listen from every pair**. A future editor
  "simplifying" either back to the literal transcription reintroduces a silent defect.
- **The fixture's expected values are hand-derived from LB's SQL**, never from the plan's
  prose, which describes a different computation (`LBDR-F2`). Do not regenerate them from the
  implementation.
- **`LBDR-F4` is discharged with a measurement**, not a caveat — the redirect arm moves a
  small fraction of one percent of pairs. Task 1's README §5 deferral is **struck in place**
  with that discharge. Do not re-open it.
- **`LBD-AM2`** records that `LBD-X1`'s "genuinely unmeasured" sentence is no longer true. It
  **does not weaken `LBD-X1`'s bar** and **does not license a ceiling change** — the cap-rule
  decision stays parked and the owner's.
- **The algebraic form emits rows the naive form does not** — exactly the zero-net pairs.
  Verified: 266 in bucket 0, none negative. `T` is unaffected. **Partial row counts are not
  comparable between the two forms**; only the thresholded result is.

## Already updated — do not redo

`docs/README.md` (one row, the new execution log); Task 1's README §5 (struck); the
pre-registration's §0 and §12 (`LBD-AM2`); `NEXT.md`.

---

## What I know that is not in the durable record

**Numbers computed and not written down anywhere else** (enumerated, not filtered):

- Stage-0 testbed run, 100 files: 195,719,125 rows, 3.88 GB, 2.8 min, **zero spill** with
  narrow frames; 4.1 min / 15.7 GB spill with `VARCHAR`-keyed views; 7.3 min / **111.2 GB
  spill** partitioned.
- Read throughput on `D:`: **128.9 MB/s at 12 threads, 245.9 at 2, 253.6 at 1**; ~35 MB/s
  under three-way contention, disk queue 13–14.
- Stage-1 chunking: `mod 64` → 25,194,958 rows / 73 s / 0.62 GB spill; `mod 16` →
  102,720,181 / 269 s / 16.98 GB spill. Time scales with **rows**, not the per-pass read.
- Heaviest users per bucket: bucket 7 → user 167111 (4,779,043 rows); then 53, 51, 38, 30,
  41, 15, 52 with 4.65M down to 2.60M.
- User 167111: 6,233 sessions; longest **63,072 listens / 1,312 distinct artists**;
  6,709,588,582 naive pair rows vs 7,488,586 algebraic.
- Credit-key hash injectivity, 1-in-64 slice: **430,644 arrays → 430,644 hashes**.
- `recording_length` after the redirect union: **40,691,857** rows; credit frame 7,174,298.
- `msid_ord` overflowed a one-byte ordinal at **477** — one account, 477 distinct recordings
  in a single second.
- D6: unconditional **51,694 characters**, conditional **2,561 lines**. Delta **zero**.

**Decided against, and why** (these leave no artifact and evaporate first):

- **Materialising `sessions_filtered` separately** — built the flag for it, then measured that
  time scales with rows rather than re-reads, so it would be pure I/O for no gain. Dropped.
- **Partitioning stage 0 by user bucket** — spills 111 GB for a 4 GB output. Dropped for a
  flat write plus a filter on read.
- **Hashing `recording_msid`** — ~1-in-6 chance of a collision over 2.4 bn values by the
  birthday bound, which would silently break the total order. Used a dense rank instead.
- **Fewer, larger buckets** — measured no faster and spills 27× more.
- **Raising `memory_limit`** — repeatedly; it was never the binding quantity.

**Said in conversation and not otherwise filed:** the owner approved staging onto `C:` after
being told ~50 GB, then that it might be 70–85 GB; it landed at **53.9 GB**.

## In flight — nothing is running

The detached pair-pass loop **exited** (`ALLDONE=FAIL` at bucket 4). **No process, no
listener, no dev server.** Ports 8000 and 5173 are clear. The partial artifacts on `C:` are
**complete for buckets 0–3 and absent for 4–63** — not half-written.

⚠ **Long runs must be launched detached** (`Start-Process`), not via the harness: it kills
background commands when free physical memory drops, and a large streaming write fills
Windows' *reclaimable* write-back cache. That killed three healthy runs. DuckDB never exceeded
its limit in any of them.

## Owed, and by whom

| | |
|---|---|
| **Successor** | finish the pair pass → `T` → derive arms → `LBD-C1` **then** `LBD-C2a`; then Task 4's README sections 4–6, currently marked *pending* |
| **Successor** | B2, B3, B4 — deliberately deferred here: they want a finished artifact and produce noise against a half-built one |
| **Owner** | merge the open PR; **deploy** (the live site is ~4 days stale); then the queued use-the-app test |
| **Owner** | whether `LBD-` is still where to spend, given the plan review's finding that most of today's sparsity is attributable to our own ceiling rather than to missing listening data. Nothing blocks on it |
