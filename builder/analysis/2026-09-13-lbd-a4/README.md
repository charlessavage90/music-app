# `LBD-A4` — the pairing-delta arm, and `R10`

**Role: FIGURES OWNER for `LBD-A4` — its `LBD-C1` fidelity reading, its edge count, and the
`R10` read taken against them. ACTIVE.** It sits beside, and never restates, the `LBD-A0`
full-history pass's own README
([`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md)), which
owns every `LBD-A0`–`LBD-A3` figure this document compares against and is **cited by section,
never copied**.

> ### ✅ RUN 2026-09-13 — `R10` FIRES, on the edge-count half alone
>
> **§1–§3 were committed before the pass ran** (`44417b0`), which is what makes §3's read of
> every possible result a pre-registration rather than a rationalisation. §§4–8 carry the
> figures and were written after.
>
> **`LBD-X6` STANDS — it does not lift.** Its *condition* is discharged; the bar it protects is
> confirmed. See §7.

**Governed by** [`../../docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](../../docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
— §0's arm table (the `LBD-A4` row), §1's run plan, §2's `LBD-C1` definition and sample, and
**§9's `R10` row with its materiality bar** — and by
[`../../docs/superpowers/specs/2026-09-06-own-similarity-design.md`](../../docs/superpowers/specs/2026-09-06-own-similarity-design.md)
`LBD-D6` and §7's `LBD-R4`. Where this document and the pre-registration disagree on a value,
**the pre-registration governs and this document is wrong.**

---

## §1 — What this arm is, in one sentence each

**`LBD-A4`'s plain sentence, fixed in the pre-registration's §0 before any result existed:**

> *count a pair once per session rather than once per pair of plays. Someone playing one
> artist twice and another once currently counts double; this asks whether that choice
> matters.*

**`R10`'s plain sentence, the read this pass exists to take:** *does counting a pair once per
session, instead of once per pair of plays, change either how much of ListenBrainz's own
answer we get back, or how many connections the map has, by enough to matter?*

**Why it runs now.** `LBD-D6` fixes the pairing semantics once, explicitly, and the owner's
ruling of 2026-09-12 — quoted verbatim in the pre-registration's `LBD-AM6-7` — **waived
`LBD-A4` for the `LBL-` listen 2 and enforced it before any `S4` arm is pre-registered.**
`LBD-X6` is the bar that travels with that waiver: listen 2's result holds for ListenBrainz's
own pairing semantics and **may not be generalised to the cheaper form until this arm has run
and `R10` has been read.**

**What this pass does not do**, and none of it is a judgement call: **no graph is built from
`LBD-A4`** — `LBD-C2b` is a graph-level read and is not owed here; **no `S4` design is begun
or proposed**; and **nothing is adopted, no default changed, no shipped code touched.**

## §2 — The one token, and how the pass keeps it to one

Factor-table row, from the pre-registration's §0 — `LBD-A4`'s isolating baseline is `LBD-A0`,
differing in **pairing only**:

| | `days` | `session` | `contribution` | `threshold` | `limit` | `skip` | pairing |
|---|---|---|---|---|---|---|---|
| `LBD-A0` | 7500 | 300 | 3 | 10 | 100 | 30 | listen |
| **`LBD-A4`** | 7500 | 300 | 3 | 10 | 100 | 30 | **distinct** |

**Held constant, and why each is genuinely constant under the intervention** — the pass is a
driver over frozen scripts precisely so that this table is enforced by construction rather
than by care:

| held constant | why this pass cannot change it |
|---|---|
| the listen corpus | **the same stage-0 file**, `C:\unsung-fast\lbd-listens.parquet` sha256 `6d77a681…07707c08`, that `LBD-A0`'s own buckets read. Stage 0 is upstream of pairing — `lbd_similarity.py`'s three-path dispatch comment says *"NOTHING before this point differs between any of the five arms"* — so this is exactness, not thrift |
| the MusicBrainz side-tables | `D:\unsung-large-data\lbd-inputs`, redirects applied — and **unread on this path**: `register_frames` is skipped entirely under `--from-listens` |
| the pair computation | `lbd_similarity.py`'s `--pairing distinct` (`T3-D7`), already present and already fixtured; **no new implementation exists in this directory** |
| the *result* under chunking | `LBD-D2` establishes that chunking by `user_id` is **exact at any modulus** — every stage through `user_contribtion_mbids` partitions by user, and only the final cross-user `SUM` crosses a boundary, which `combine_sql` re-sums once. **The modulus itself is therefore NOT held constant and does not need to be**; see the exposure note below |
| the threshold and rank cut | applied once, by `lbd_derive.py`, whose `A0` row **is** `(threshold 10, limit 100)` — `LBD-A4`'s own pair |
| the `LBD-C1` sample | the same pinned 3,000 artists, `lbd_c1_sample.tsv`, against the same pinned snapshot `grt-archive-algb.pre-cex-snapshot` |

**Named exposure — the two passes carry different script shas, and pairing is not the whole
of why.** `LBD-A0`'s partials record `script_sha256` `40f9ee03…` (commit `1cb49c6`); this
pass records `eeb3c87b…` (commit `dda02a9`). **The entire diff between those two commits is
the `--created-before` diagnostic knob** added for the `LBD-G1` diagnosis, and it lives
wholly inside `register_listens` — **stage 0, which `--from-listens` never calls.** So it is
inert on this path by construction. Stated because a reader comparing two manifests sees two
shas and is owed the reason rather than an assurance.

**Not a confound, but named rather than left silent: this pass chunks differently from
`LBD-A0`'s.** `LBD-A0` ran 64 buckets at a 12 GB DuckDB limit; this pass runs **128 at 8 GB**.
The first attempt at `LBD-A0`'s settings was **killed by the system under memory pressure** —
12 GB of a 31.7 GB machine with other work live — and the setting was then chosen by
measurement rather than guessed: one bucket at mod 128 / 8 GB peaks at **7.64 GB** and takes
1.1 min, which is also a shorter pass in total. **This cannot move a figure.** `LBD-D2`'s
exactness is not a claim about 64 in particular; the partials are unioned and re-summed once,
and `T3-D3`'s integer cast is applied to the completed cross-user sum in `combine_sql`, never
to a partial. What it moves is wall clock and peak memory, which are `LBD-C3` quantities and
are reported as such in §4. **The coverage of the residues is checked, not assumed** — the
summary stage expands every partial's `(user_mod, user_rem)` to the finest modulus present
and asserts they cover every user exactly once, which is the thing a mis-chunked pass would
silently get wrong.

**One inherited condition, and it is not this pass's to discharge.** `LBD-G1` fired on
`LBD-A0` and was overridden by owner decision (`LBD-AM3`); the diagnosis named the input
difference. **`LBD-C1` must never be cited as passed** — for `LBD-A0` or for `LBD-A4`. What
`R10` reads is the **difference** between the two arms' pooled rates on the same sample, and
a lineage gap common to both arms cancels in that difference, which is the whole reason the
comparison is against `LBD-A0` and never against the archive.

## §3 — The read of every possible result, fixed before the pass ran

**`R10`'s materiality bar, quoted from the pre-registration's §9:** *"`LBD-A4` changes
`LBD-C1` or edge count materially → the pairing semantics are load-bearing; record which
every later arm uses and why, per `LBD-D6`. **Material = the `LBD-G2` bar applied to edge
count, or 5 pp on the pooled `LBD-C1` rate.**"*

Resolving each half against its own source, so that neither is resolved after a number exists:

- **`LBD-C1` half — 5 percentage points on the pooled row-level rate.** The pooled rate is
  reported by fame band (§2 of the pre-registration), and `LBD-G1`'s own subject is **the top
  band**. The top band is therefore this read's primary, and all five are reported.
- **Edge-count half — `LBD-G2`'s bar is "≥ 1 percentage point"**, and `LBD-G2` is defined on
  a *share*, not a count. Applied to edge count, the quantity that has a percentage is the
  **relative change in rows** of the arm's derived table, `|A4 − A0| / A0`. **A 1 % relative
  change in edge count fires this half.** Recorded here, before the pass, because the
  pre-registration transports a bar across quantities and does not say which reading of it
  applies; this is the reading, and it is the **more sensitive** of the two candidates, which
  is the direction that cannot flatter a null.

**Either half alone fires `R10`.** The row reads *"changes `LBD-C1` **or** edge count"*.

| result | the read |
|---|---|
| **neither half fires** | `R10` does not fire. *Plain: which of the two ways of counting is used makes no difference worth acting on.* `LBD-X6` is **lifted** — listen 2's result may then be spoken of without the pairing caveat — and `LBD-D6`'s requirement that every `S4` arm record which semantics it uses **still stands**, because it is a bookkeeping rule and not a consequence of this result |
| **either half fires** | `R10` fires. *Plain: the pairing choice is load-bearing and an arm that changes it is not comparable with one that does not.* `LBD-X6` **stands as a permanent term** rather than a temporary one: listen 2's verdict is a verdict about ListenBrainz's own pairing and no sentence may generalise it. Every later arm records which semantics it uses and why, per `LBD-D6` |
| **the two halves disagree** | `R10` fires on the row's own **or**. Both figures are reported side by side and the report says which half fired, since "the pairing is load-bearing for how much of ListenBrainz's answer we reproduce" and "…for how many connections there are" are different facts |

**What no result here can support.** Nothing about routing, path quality or what a listener
would hear — `LBD-A4` is a pair table and no journey is generated from it. Nothing about
adoption: `S4` owns that. And **no re-reading of either `LBL-` verdict**, which `GBL-` §5
makes run-once regardless of what this arm says.

## §4 — The pass

**Three stages, all frozen scripts driven by `a4_run.py`.** `LBD-C3` is descriptive and gates
nothing here; `LBD-G3`'s spill bar was already exceeded on the `LBD-A0` pass and its
prescribed response — the chunked form — is what both passes are.

| stage | output | rows | wall | peak RSS | spill |
|---|---|---:|---:|---:|---:|
| 128 bucket partials | `p0…p127.parquet` | 1,934,651,015 | 178.7 min summed (64–145 s each) | 7.64–8.10 GB | 1,251 GB summed, 30.5 GB max |
| combine (`--aggregate-only`) | `T_A4.parquet`, 20.66 GB, sha256 `e919bc89…` | **689,602,719** | 15.8 min | 12.05 GB | 225 GB |
| derive (threshold 10, cap 100) | `A4.parquet`, sha256 `4ffa4acc…` | **10,823,170** | 50.8 s | — | — |

**The one-token claim, checked at the level of the artefacts rather than the intent.** Across
all 128 bucket manifests: one `script_sha256`, one `pairing` (`distinct`), one `from_listens`
— the stage-0 file `LBD-A0`'s own buckets read. And the residues, expanded to the finest
modulus present, **cover every user exactly once, with no duplication.** That last check is
the one a mis-chunked pass fails silently.

**`T_A4` is 903 rows short of `T`** — 689,602,719, against a `T` whose figure is owned by
[`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md) §5; a
difference of 0.00013 %. This is not a result, and it is exactly what ListenBrainz's SQL
predicts: the distinct form removes duplicate rows *before* the self-join, so it can lower a
pair's score but can never destroy a pair that co-occurred. The only pairs it can delete are
those whose score truncated below 1.

**Not a figure: the partial row count.** 1.93 bn here against the `LBD-A0` pass's 1.77 bn is
the **modulus**, not the pairing — a pair whose listeners fall in two buckets is counted once
per bucket, so finer chunking mechanically inflates the partial total. Confirmed directly
rather than argued: the one bucket run at mod 64 before the chunking changed produced a row
count identical to `LBD-A0`'s bucket 0. Only the combined table is comparable.

### Two instrument faults, both self-inflicted, neither touching a figure

Recorded because a reader comparing logs will find two failed attempts.

1. **The combine failed once on a spill cap, not on memory.** `max_temp_directory_size`
   reached 142.6 GiB and refused. DuckDB sets that to ~90 % of free disk **at the moment the
   connection opens**, and the attempt had been relaunched 15 s after a previous one was
   killed, whose orphaned spill was still on disk. Re-run against a clean temp directory it
   spilled 225 GB under a ~347 GB cap. A property of the restart, not of `LBD-A4`.
2. **The corrected-quantile script faulted under `uv run --with duckdb`** with
   `PyEval_SaveThread: the function must be called with the GIL held` — an interpreter-level
   fault during a module import inside the ephemeral environment, not a defect in the script
   and not a result that can be wrong. Re-run on a dedicated venv at **duckdb 1.5.5, the same
   version every manifest in this track records**, so the instrument is unchanged.

## §5 — `LBD-C1` on `LBD-A4`

Read with the frozen `lbd_reads.py --mode c1` against **the same pinned sample and the same
pinned snapshot** `LBD-A0`'s read used: 3,000 artists from `lbd_c1_sample.tsv`
(content-identical to its committed `sample_sha256` once line endings are normalised), against
`grt-archive-algb.pre-cex-snapshot`. Raw: `A4.c1.json` beside the arm.

**Pooled row-level rate by fame band** — the statistic `LBD-G1` and `R10` both read:

| band | archive rows | `LBD-A4` pooled rate | Δ vs `LBD-A0` (pp) |
|---:|---:|---:|---:|
| 0 | 16,382 | 0.3935 | −0.085 |
| 1 | 25,098 | 0.5353 | −0.100 |
| 2 | 34,212 | 0.5678 | +0.345 |
| 3 | 47,107 | 0.6042 | +0.030 |
| **4 (the gate's subject)** | 57,692 | **0.5900** | **+0.560** |

**`LBD-A0`'s five rates are deliberately not reproduced here.** They are owned by
[`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md) §5, and a
second copy is how figures drift in this project. **The delta is the quantity `R10` reads**
and is owned here; each `LBD-A0` rate is recoverable as this table's rate minus its delta.

**The denominators are identical band for band** — 16,382 / 25,098 / 34,212 / 47,107 / 57,692
in both arms. That is the check that the two reads are over the same sample and the same
archive, rather than merely run by the same script. Our table covers **2,944** of the 3,000
sampled artists; **56** are absent, against `LBD-A0`'s 55.

### ⚠ `LBD-G1` fires on `LBD-A4`, and `LBD-AM3`'s override does not name this arm

**0.5900 < 0.60.** The gate fires, as it did on `LBD-A0`. `LBD-AM3` records the owner's ruling
that the gap is explained by the deployed dataset having been computed on a far smaller
corpus, and that **`LBD-A0`–`LBD-A3` may be read anyway** — an enumeration that does not
include `LBD-A4`, which did not exist when he ruled. **`LBD-C1` is not cited as passed, for
either arm.**

**Why `R10` is nonetheless read here — answered rather than escalated.** Four reasons, the
first load-bearing:

1. **`R10`'s bar is a difference between arms, not a level against the archive** — "5 pp on
   the pooled `LBD-C1` rate". A lineage gap common to both arms cancels in that difference.
   §2 above fixed that framing **before the pass ran**, for exactly this reason.
2. **No new defect is indicated.** `LBD-A4`'s top-band rate is *higher* than `LBD-A0`'s, and
   higher in three bands of five.
3. **The instrument that separates "inputs differ" from "implemented wrong" was re-run on
   this machine before the pass.** `lbd_fixture.py`: eight fidelity checks green, including
   `pairing distinct (T3-D7)` and `algebraic form == naive form, pairing=distinct`, and all
   seven mutants red. That is the same evidence class `LBD-AM3` rested on.
4. **The owner's `LBD-D6` ruling of 2026-09-12 post-dates `LBD-AM3`** and requires `LBD-A4`
   to run and `R10` to be read before any `S4` arm — taken in full knowledge that `LBD-G1`
   had fired and been overridden.

**What remains the owner's, and it is a scope question rather than a measurement one:**
whether `LBD-AM3`'s override extends to `LBD-A4` as a statement about *absolute* fidelity.
**`R10` does not depend on the answer, because `R10` reads a difference.** Nothing here
extends that ruling, and nothing here needs to.

### §5a — The per-artist distribution, and a direct measurement of the mechanism

The pre-registration's §2 requires `LBD-C1` **reported two ways, both required** — the pooled
rate above, and a per-artist overlap distribution by band. This is the second.

**Taken with `lbd_c1_diagnose.py`, not `lbd_reads.py`.** That is not a preference: `lbd_reads.py`
gives an artist with an empty archive list a NaN share, and a NaN inside `sorted()` scrambles
the order. Its quantiles for this run show the same signature the `LBD-A0` README records —
band 0 printing p10 above the median — and **are reproduced nowhere in this document.** The
pooled rate does not touch those values and is unaffected. Empty archive lists here: **5, 2,
1, 0, 0 by band**, which is *identical* to `LBD-A0`'s, as is the truth load of **180,491
archive pairs over 3,000 artists** — independent evidence that both arms were scored against
the same sample and the same snapshot.

| band | artists scored | median | p10 | p25 | p75 | Δ median vs `LBD-A0` |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 595 | 0.538 | 0.000 | 0.250 | 0.714 | −0.013 |
| 1 | 598 | 0.545 | 0.200 | 0.400 | 0.660 | −0.002 |
| 2 | 599 | 0.600 | 0.303 | 0.470 | 0.709 | ±0.000 |
| 3 | 600 | 0.630 | 0.416 | 0.530 | 0.710 | ±0.000 |
| 4 | 600 | 0.640 | 0.470 | 0.570 | 0.710 | ±0.000 |

Quantiles now order correctly in every band, which is the defect's absence made visible.
**The per-artist reading agrees with the pooled one**: the pairing change is invisible at this
resolution in three bands of five and moves the median by at most 1.3 pp in the other two.

**The decomposition, and what it adds beyond agreement.** For the top band, where each
archive entry for a sampled artist is traced to where our pipeline put it, the two arms land
within 0.1 pp of each other on every outcome — matched, below-cut, rank-cut, below-threshold
and absent alike. *Inference, labelled:* the archive's own pairs for these artists fare
identically under either counting rule, so **the half-million edges §6 measures are
overwhelmingly pairs ListenBrainz does not list for them** — the arm is trimming our own
surplus, not losing what LB told us.

**And the mechanism §6 asserts is measured here rather than argued.** The diagnosis compares
our score against ListenBrainz's on every truth pair present in our table. Both arms have
**the same 51,449 comparable pairs** in the top band — as §4 predicts, since the distinct form
cannot destroy a co-occurrence — but the ratio of our score to theirs falls from a median of
2.979 under `LBD-A0`'s counting to **2.790** under `LBD-A4`'s, with p90 falling from 6.316 to
**5.930**. *Plain: counting once per session instead of once per pair of plays makes our
scores about 6 % smaller, and shrinks the long tail of pairs where we scored far above
ListenBrainz by more.* That is exactly the quantity that has to move for half a million pairs
to fall below a fixed strength bar while the pair set itself barely changes, and it closes the
argument in §6 with a measurement instead of an assertion. *(`LBD-A0`'s two ratio figures are
named once here for the comparison; they are owned by
[`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md) §5a.)*

**None of this is a fidelity verdict.** A ratio nearer 1 is *not* evidence that `LBD-A4` is
the more faithful arm: the residual ratio is the corpus-date lineage gap `LBD-AM3` diagnosed,
common to both arms, and `LBD-C1` is not cited as passed for either.

## §6 — Edge count

The arm's derived table, at `LBD-A4`'s own `threshold` 10 and `limit` 100:

| | edges | Δ | relative |
|---|---:|---:|---:|
| **`LBD-A4`** | **10,823,170** | **−517,469** | **−4.563 %** |

`LBD-A0`'s count is owned by
[`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md) §5 and is
named once here — 11,340,639 — because a relative change is unreadable without its base. The
**delta and the relative change are owned here.**

*Plain: counting a pair once per session instead of once per pair of plays removes about one
connection in every twenty-two.*

**The mechanism is checkable rather than asserted**, which matters because §4 showed the same
two arms differing by only 903 rows at the floor. The distinct form cannot delete a
co-occurrence, only weaken one. At `score > 0` almost nothing changes, because a pair needs
only to reach 1. At `score > 10` half a million pairs fall out — the ones that were clearing
ListenBrainz's strength bar **on repeat plays by a single listener**. That is the same knob
`LBD-A0`↔`LBD-A2` already showed carries nearly all the supply movement (figures owned by the
`LBD-A0` README's §6), seen from the other side.

## §7 — `R10`, read against §3

| half | bar (fixed in §3, before the pass) | measured | fires? |
|---|---|---:|---|
| pooled `LBD-C1` rate | 5 pp, any band | **0.560 pp** (largest, top band) | **no** — by a factor of nine |
| edge count | 1 % relative | **4.563 %** | **yes** — by a factor of four and a half |

> ### `R10` FIRES — on the row's own **or**, and on exactly one of its two halves
>
> **The pairing semantics are load-bearing.** Per `R10` and `LBD-D6`: **every later arm
> records which pairing semantics it uses and why.**

This is §3's third row, the disagreement case, which requires both figures side by side and a
statement of which half fired. *In plain terms: which of the two ways of counting you use
barely changes how much of ListenBrainz's own answer you reproduce — but it changes how many
connections the map has, by about one in twenty-two.* The two are not in tension. Fidelity is
scored against the archive's own list for each artist, cut at that list's length, which is
mostly strong pairs surviving either rule; the half-million lost edges are weak ones sitting
just above the strength bar.

### `LBD-X6` STANDS. It does not lift.

`LBD-X6` bars generalising the `LBL-` listen-2 result to the cheaper pairing form *"until
`LBD-A4` has run and `R10` has been read"*. **Both conditions are now met** — and the answer
`R10` returned is that the pairing form **does** change the map materially. So the *condition*
is discharged and **the bar it was protecting is confirmed, not released**: listen 2's result
holds for ListenBrainz's own pairing semantics, and no sentence may generalise it to the
cheaper form. Under §3's other branch — had neither half fired — `LBD-X6` would have lifted.
It did not.

**`LBD-R4`** (design §7, *semantic drift from the cheaper pairing form*) is **retired as a
risk and confirmed as a fact**: the drift is real, it is measured at 4.563 % of edges, and
`LBD-D6`'s requirement that every later arm declare its pairing is what manages it.

## §8 — What is NOT established here

- **Nothing about routing, path quality, or what a listener would hear.** `LBD-A4` is a pair
  table. **No graph was built from it** and no journey was generated.
- **No direction of preference.** `R10` says the choice *matters*. It says **nothing** about
  which pairing form is *better*: fewer edges is not worse, and 4.563 % fewer edges at a fixed
  strength bar is not evidence about journeys in either direction.
- **`LBD-C2a` (supply) was deliberately NOT taken on this arm**, and the temptation is the
  point — it is a single `GROUP BY` over a table that now exists. Its reads (`LBD-G2`,
  `R4`–`R12`) were pre-registered for the four `T`-derived arms, not for this one, and taking
  an unregistered read *after* results exist is what the pre-registration discipline exists to
  prevent. Anyone who wants it owes an amendment first. The same holds for `LBD-C2b` and
  `LBD-M1` on this arm.
- **No adoption, no default changed, no shipped code touched**, and **no `S4` design begun or
  proposed.** `S4` owns adoption, the population rule, API sizing, the fame source and the
  refresh procedure.
- **Neither `LBL-` verdict is re-read or re-listened** (`GBL-` §5), and `REQ-41` still bars
  reading either tie as equivalence.
- **`LBD-C1` is not cited as passed**, for `LBD-A0` or for `LBD-A4`.
- **`lbd_reads.py`'s per-artist quantiles are not reproduced anywhere in this document.** They
  carry the NaN-sort defect the `LBD-A0` README documents, and this run shows the same
  signature — band 0 printing p10 above the median. The corrected distribution the
  pre-registration's §2 also requires is §5a, taken with `lbd_c1_diagnose.py`.
- **A score ratio nearer 1 is not a fidelity verdict** (§5a). The residual ratio is the
  corpus-date lineage gap `LBD-AM3` diagnosed, common to both arms.
