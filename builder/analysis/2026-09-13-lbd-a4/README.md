# `LBD-A4` — the pairing-delta arm, and `R10`

**Role: FIGURES OWNER for `LBD-A4` — its `LBD-C1` fidelity reading, its edge count, and the
`R10` read taken against them. ACTIVE.** It sits beside, and never restates, the `LBD-A0`
full-history pass's own README
([`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md)), which
owns every `LBD-A0`–`LBD-A3` figure this document compares against and is **cited by section,
never copied**.

> ### ⚠ UNRUN AT THIS COMMIT
>
> **Nothing below §1 holds a measurement yet.** This document is committed before the pass
> runs so that the route, the one-token argument and the read of every possible result are on
> the record first. Sections marked **PENDING** are written after the pass and are the only
> ones that will carry numbers.

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
| the chunking | `user_id % 64`, which `LBD-D2` establishes is **exact**, not an approximation: every stage through `user_contribtion_mbids` partitions by `user_id` |
| the threshold and rank cut | applied once, by `lbd_derive.py`, whose `A0` row **is** `(threshold 10, limit 100)` — `LBD-A4`'s own pair |
| the `LBD-C1` sample | the same pinned 3,000 artists, `lbd_c1_sample.tsv`, against the same pinned snapshot `grt-archive-algb.pre-cex-snapshot` |

**Named exposure — the two passes carry different script shas, and pairing is not the whole
of why.** `LBD-A0`'s partials record `script_sha256` `40f9ee03…` (commit `1cb49c6`); this
pass records `eeb3c87b…` (commit `dda02a9`). **The entire diff between those two commits is
the `--created-before` diagnostic knob** added for the `LBD-G1` diagnosis, and it lives
wholly inside `register_listens` — **stage 0, which `--from-listens` never calls.** So it is
inert on this path by construction. Stated because a reader comparing two manifests sees two
shas and is owed the reason rather than an assurance.

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

## §4 — The pass — PENDING

## §5 — `LBD-C1` on `LBD-A4` — PENDING

## §6 — Edge count — PENDING

## §7 — `R10`, read against §3 — PENDING

## §8 — What is NOT established here — PENDING
