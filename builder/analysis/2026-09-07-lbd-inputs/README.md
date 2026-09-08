# `LBD-` inputs — what the track will run on, pinned, and three reads over it

**Role: FIGURES OWNER for the `LBD-` track's inputs. ACTIVE.** Every number below is owned
here and **cited elsewhere, never restated** — by
[`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](../../../docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
which is the governing document for the track's criteria and owns no figures of its own.

Task 1 of [`plans/2026-09-06-lb-dump-exploration.md`](../../../docs/superpowers/plans/2026-09-06-lb-dump-exploration.md),
run 2026-09-07 from a worktree. **Descriptive: no criterion, no gate, nothing adopted, no arm
run.** The three reads exist to bound things the track would otherwise discover late and
expensively.

The scripts are **frozen** — stdlib plus DuckDB, no project imports, except
`cxr_added_set.py` which deliberately uses the **shipped** `GraphStore` so it cannot disagree
with what the API loads. Everything they produce lands under `D:\unsung-large-data\`;
**nothing is written into `builder/scratch/`** (`LBD-D8`), which is read by absolute path.

| script | what it does |
|---|---|
| `cxr_added_set.py` | verifies both artifacts against their manifest sidecars, derives and pins the `CXR` added set and the pre-existing set |
| `dump_reads.py` | the dump's identity, `R-SUPPLY`, and `R-USERS` |
| `inputs_extract.py` | verifies and extracts `mbdump`, builds three parquet frames, and `R-FEAT` |

---

## 1. Inputs, pinned

### The ListenBrainz Spark/parquet dump — the corpus the whole track runs on

| | |
|---|---|
| where | `D:\unsung-large-data\listenbrainz-spark-dump-2647-20260901-000002-full\` |
| `SCHEMA_SEQUENCE` | `1` — matches the incremental `LBD-P1` opened, so that probe's schema reading carries over |
| `TIMESTAMP` | `2026-09-01 00:00:02.462107+00:00` |
| parquet files | 1,409 |
| **listens (rows)** | **2,708,495,599** |
| licence | `COPYING` = CC0 1.0 Universal, read from the file |

**Row schema** (one file described, all 1,409 written by the same job): `listened_at`,
`created`, `user_id`, `recording_msid`, `artist_name`, `artist_credit_id`, `release_name`,
`release_mbid`, `recording_name`, `recording_mbid`, `artist_credit_mbids` (`VARCHAR[]`).

**Compressed bytes per column**, from the parquet footers — no scan, and worth having because
it is what makes a column-selective read cheap and a careless one expensive:

| column | GB | | column | GB |
|---|---:|---|---|---:|
| `recording_msid` | 47.6 | | `release_name` | 22.0 |
| `recording_mbid` | 40.3 | | `artist_name` | 16.3 |
| `release_mbid` | 29.4 | | `created` | 6.1 |
| `recording_name` | 27.6 | | `artist_credit_id` | 5.6 |
| `artist_credit_mbids` | 25.8 | | `user_id` | 4.6 |
| | | | `listened_at` | 3.3 |

> ### ⚠ The plan's verify-then-extract step could NOT be run, and this is the substitute
>
> Task 1 step 1 says to verify
> `listenbrainz-spark-dump-2647-20260901-000002-full.tar` against its published sha256
> **before** extracting, and to refuse on mismatch. **That tar is not on disk** — only its
> extracted directory is — so the published checksum could not be checked and **this input's
> identity does not rest on it.** Nothing was deleted by this session; the tar was already
> absent when the session began.
>
> What stands in its place: `SCHEMA_SEQUENCE`, `TIMESTAMP` and the file count above all match
> what a dump 2647 cut on 2026-09-01 should carry, and the row count is consistent with the
> 2.70 billion sitewide figure `LBD-P2` recorded from ListenBrainz's own API.
> **That is corroboration, not verification.** A later session that needs the stronger
> guarantee must re-download the tar; until then, **no claim in this track may rest on the
> dump being byte-identical to the published one**, only on its being internally consistent
> and pinned by path.
>
> The two figures a reader should not confuse: the plan names the tar's published sha256, and
> that string is **not** evidence about the directory on disk.

**Incrementals are deliberately NOT applied** in `LBD-S1`–`S3`. The 2026-09-01 cut is the
pinned input for the whole exploration; freshness is an `LBD-S4` question. The one-day
incremental 2653 that `LBD-P1` and `LBD-P2` measured is a **different file** and its figures
are not this dump's.

### The MusicBrainz side-tables

| | |
|---|---|
| source | `https://data.metabrainz.org/pub/musicbrainz/data/fullexport/20260905-002519/mbdump.tar.bz2` |
| size | 7,501,059,582 bytes |
| **published sha256** | `5cd98ffa443e2fde3517d36417d6c1d67960025058ba1411291bb7e1adcd3292`, from `SHA256SUMS` in the same directory |
| verified | **yes** — recomputed after download and matched before extraction |
| `SCHEMA_SEQUENCE` | **31** |
| `TIMESTAMP` | `2026-09-05 00:25:20.132352+00` |

**The two schema sequences are different numbers and both matter.** The listens dump is at
`SCHEMA_SEQUENCE` 1 (ListenBrainz's own) and this MusicBrainz dump is at 31. **They are
unrelated counters** and neither says anything about the other.

**And 31 is the number that validates the column order above.** MusicBrainz's master branch
declares `ACTIVE_SCHEMA_SEQUENCE { 31 }` in `lib/DBDefs/Default.pm`, read 2026-09-07 — the same
sequence this dump carries. So `CreateTables.sql` at master *is* this dump's schema, and the
column order was not read from a newer or older one. Had they differed, the extraction would
have needed the tagged schema instead.

> **Both files are at the archive ROOT, not under `mbdump/`.** Plan Task 1 step 3 implies
> otherwise; extracting `mbdump/SCHEMA_SEQUENCE` fails with "Not found in archive". The root
> also carries `COPYING`, `README` and `REPLICATION_SEQUENCE`, and they are the first members
> in the stream, so pulling them is seconds rather than the full decompression the tables need.

`20260905-002519` was `LATEST` when read on 2026-09-07, and is the dump the plan names.

> **⚠ The first download failed verification, and the refuse-on-mismatch rule is why that was
> caught.** An interrupted transfer was resumed with `curl -C -`, which appended 269,193,216
> bytes of duplicate content: the file was **7,770,252,798** bytes and hashed
> `dbdc0b3ea9f50f35c43623f906f6a683561a2da263583e5cfff92d953dfa54a9`. It was deleted and
> re-downloaded without resume. **A size check alone would have caught this one; a session
> that had skipped the hash and trusted a resumed download would have built every frame below
> from a corrupt archive.**

**Column order was read from MusicBrainz's own schema, not from the plan** — fetched from
`admin/sql/CreateTables.sql` at metabrainz/musicbrainz-server master on 2026-09-07.

| table | columns | column order as verified |
|---|---:|---|
| `artist` | **19** | `id, gid, name, sort_name, begin_date_{year,month,day}, end_date_{year,month,day}, type, area, gender, comment` (14th)`, edits_pending, last_updated, ended, begin_area, end_area` |
| `artist_credit` | 7 | `id, name, artist_count, ref_count, created, edits_pending, gid` |
| `artist_credit_name` | 5 | `artist_credit, position, artist, name, join_phrase` |
| `recording` | 9 | `id, gid, name, artist_credit, length, comment, edits_pending, last_updated, video` |

> **⚠ The `artist` row is a correction to this session's own first reading, and the shape of
> the mistake generalises.** `artist` carries an **inline `CHECK` constraint** in the DDL
> immediately after `ended`, and **two more columns follow it** — `begin_area` and `end_area`.
> A reader who stops at the first constraint counts seventeen. This session did, and wrote
> "all four tables matched the plan" before the parser rejected the file for having nineteen.
>
> **The columns actually consumed here are unaffected** — `gid` is 2nd, `name` 3rd, `comment`
> 14th, all ahead of the constraint — so no frame was built wrong. But a session that had
> declared `ignore_errors` or `null_padding` to get past the sniffer would have silently
> shifted every column after position 17 and never seen it. **A schema read is not finished at
> the first `CHECK`.**

**Encoding, and it matters for exactly one column.** These are PostgreSQL `COPY … TO` TEXT
dumps: tab-delimited, `\N` for NULL, and backslash escapes for tab, newline and backslash. Real
newlines never appear inside a field, so row splitting is safe with no quoting. The escapes are
undone afterwards, **not at parse time** — letting DuckDB's own `escape` consume the
backslashes would silently alter `join_phrase`, which is the one column whose exact bytes
decide the featured-artist weight (`R-FEAT` below, and `LBDR-F2`).

### The frames produced

All three land in `D:\unsung-large-data\lbd-inputs\`, sorted so a rebuild is byte-comparable.

| frame | rows | size | sha256 | what consumes it |
|---|---:|---:|---|---|
| `recording_length.parquet` | 40,076,669 | 1,433.4 MB | `5d5abc2e2ab711d38e115432b1f970495b7fb978666ffd475250f0b1a60b3550` | the session-gap duration, `COALESCE(length/1000, 180)` |
| `artist_credit.parquet` | 7,174,298 | 219.8 MB | `ba94ed932c7505b2831eecf4ee009e5a67c98d244dcad1a01de95dbebce109ac` | the credit fan-out and the featured-artist weight |
| `artist_identity.parquet` | 2,976,554 | 158.1 MB | `02b4c8ddb67436a294879c272cfa9751ad6992e1010092ae5dcecebdc5a79b23` | the archive emitter's `name` and `comment`, later |

**The credit frame lost no rows to its joins.** It has exactly as many rows as
`artist_credit_name` itself, so every credit line resolved to both an artist and a credit.
Had it not, the fan-out would silently drop artists from every pair computation downstream.

`artist_credit.parquet` matches the shape ListenBrainz builds in its own
`data/postgres/artist_credit.py` — `artist_credit_id, artist_mbid, position, join_phrase` —
which is what lets the reimplementation join exactly as their SQL does.

### The `CXR` added set — the fixed artist set `LBD-C2` is measured over

Derived by loading **both artifacts through the shipped `GraphStore`**, each sha256-verified
against its own `.bin.json` manifest sidecar first. Artifacts under `builder/scratch/` are
gitignored and **not interchangeable**; the sha is the only identity they have.

| | |
|---|---|
| served map | `graph-msw-tu50.bin`, sha256 `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` — **matched** its manifest |
| the extended map | `graph-cxa-adopted.bin`, sha256 `bc0431c4b55a2137e945b280270de7e7dc700e3dcf60f3656f6f97598e7ece46` — **matched** its manifest |
| **added set** | **29,892 MBIDs** → `D:\unsung-large-data\lbd-inputs\cxr_added_mbids.txt`, sha256 `bfed95ef74b0665c50b1532708091b4e43fab36247db391d04064870659a4339` |
| **pre-existing set** | **58,793 MBIDs** → `cxr_preexisting_mbids.txt`, sha256 `768054b7e84769346193336ec7e9b3496af92d0d3e8d4ae2fb287057912b5229` |

**The degree figures this reproduces are `CXR-P2`'s and are owned by
[`../2026-09-01-cxr-regression-diagnosis/`](../2026-09-01-cxr-regression-diagnosis/) — not
restated here.** They were recomputed only as a check that the read is being taken correctly,
and they **reproduce exactly**, including the share at or below two connections that the plan
review's Q4 derived independently. Treat a failure to reproduce them as a broken environment,
not a new finding.

**Every arm reads these two files.** The sets are pinned once and never re-derived per arm,
because re-deriving them is a way for the denominator to move without anyone noticing.

---

## 2. `R-SUPPLY` — do the added artists appear in the listening data at all?

> **Plain sentence: of the ~29,900 artists the crawl extension added — the ones that arrived
> with almost no connections — how many does anyone in ListenBrainz's data listen to at all,
> and how many are listened to by enough different people to be able to clear the score
> threshold?**

**This bounds the whole track**, which is why it runs before any arm rather than after.
The `LBD-` track exists to find out whether the added artists' sparsity is *our rules* or
*the listening data*. There is a third possibility neither of those covers: **the artists may
simply not be in the corpus.** An artist nobody played can gain no edge at any threshold and
any cap, so a null result over such artists says nothing about either explanation. Derivation
item 11, which named this unmeasured and costed it at one join.

**The distinct-user count is arithmetic on ListenBrainz's own SQL, not an estimate.** Each
user contributes at most `contribution` to a pair (`LEAST(SUM(similarity), contribution)`),
and the threshold is applied as `HAVING score > threshold` — strict, over an integer. So a
pair needs at least ⌈(threshold+1)/contribution⌉ **distinct** users before it can survive at
all: **4** at `ALG-B`'s parameters (threshold 10, contribution 3), and **1** at the floored
threshold the corner arm uses.

Measured over the whole pinned dump, 35.3 minutes of wall-clock. Per-artist counts are written
to `D:\unsung-large-data\lbd-inputs\cxr_added_dump_supply.parquet`.

| | count | share of 29,892 |
|---|---:|---:|
| **appear in the corpus at all** | **29,848** | **99.85 %** |
| appear in *mapped* listens — the population ListenBrainz's job actually reads | 29,847 | 99.85 % |
| **absent from the corpus entirely** | **44** | **0.15 %** |

**Distinct listeners per added artist**, over mapped listens:

| distinct listeners | artists | share |
|---|---:|---:|
| 0 (includes the 44 absent) | 45 | 0.15 % |
| 1 | 31 | 0.10 % |
| 2–3 | 38 | 0.13 % |
| **≥ 4 — the arithmetic minimum to clear threshold 10** | **29,778** | **99.62 %** |
| ≥ 10 | 29,600 | 99.02 % |
| ≥ 50 | 24,768 | 82.86 % |

Quantiles over the 29,848 present: p10 = 36, p25 = 66, **median = 126**, p75 = 243, p90 = 443.

### What this establishes

**The added artists are in ListenBrainz's listening data, and not marginally.** All but 44 of
them appear, and 99.62 % have at least the four distinct listeners a pair mathematically
requires before it could survive `ALG-B`'s threshold at all. The typical one has 126 distinct
listeners.

**This closes off the third explanation before the track can be confused by it.** The `LBD-`
track contrasts two accounts of why these artists arrived nearly unconnected: *our rules* or
*the listening data*. A third was available and unmeasured — that the artists are simply not
in the corpus — and it would have looked exactly like the second while meaning something
completely different. It is now ruled out at 0.15 %. **A later null on the supply criterion is
therefore about the listening or the rules, and cannot be dismissed as absence.** That is the
read the pre-registration's §9 fixes as `R6` rather than `R7`.

### What this does NOT establish

**Having four listeners is necessary, not sufficient, and the gap between the two is the whole
of `LBD-S2`.** A pair's score needs four listeners who each played *both* artists inside one
listening session. An artist with 126 listeners who never played them next to any single other
artist consistently still ends with no edge. **Nothing here measures co-occurrence**, which is
the pair computation itself.

So this read raises the prior that supply exists without establishing it, and **it must not be
cited as evidence that any arm will move `LBD-C2`.** The direction it genuinely settles is the
negative one: a null cannot be explained away by absence.

**One caveat on the denominator.** Membership is read from the `artist_credit_mbids` column,
which is how the listens name their artists; ListenBrainz's job instead joins
`artist_credit_id` to its own credit frame. The two are populated from the same MusicBrainz
data and the one-day probe measured their coverage within 0.2 points of each other, so they
are expected to agree — **but they were not compared here**, and a small disagreement at the
obscure end would move the 0.15 % rather than the 99.62 %.

---

## 3. `R-FEAT` — is the 0.25 featured-artist weight live on this corpus?

> **Plain sentence: ListenBrainz weights an artist at a quarter when the credit's join phrase
> is one of eight literals. MusicBrainz stores join phrases *with* their surrounding spaces,
> and ListenBrainz compares them untrimmed. So how often does that comparison actually fire
> on the real table?**

The plan review found that `' feat. '` does not match the literal `'feat.'`, making the term
close to dead code in ListenBrainz's production job — and that an implementer who trims (the
natural thing to do, since the constants "obviously" mean featured artists) diverges from
ListenBrainz on **every multi-artist credit in the corpus**. The mechanism was verified from
source by that review; **the share was not measured, and this is that measurement.**

**It does not change the reimplementation.** Fidelity to ListenBrainz's behaviour is required
whether the term is live or dead, and the pre-registration's §6 fixes the synthetic fixture
against the SQL either way. What this figure tells a later reader is **how much of `LBD-C1`
could possibly turn on getting it wrong**.

Measured over all 7,174,298 rows of the credit frame.

| | rows | share |
|---|---:|---:|
| with a non-empty join phrase | 3,356,535 | 46.786 % |
| **matching ListenBrainz's literals as ListenBrainz compares them** | **882** | **0.0123 %** |
| matching only if the phrase were trimmed first | 712,878 | 9.9366 % |

**Ratio: 808×.** That is the size of the divergence an implementer introduces by trimming.

The ten most common join phrases that contain one of the eight literals:

| rows | phrase |
|---:|---|
| 639,747 | `' feat. '` |
| 39,868 | `' ft. '` |
| 24,286 | `' featuring '` |
| 5,819 | `' feat.'` |
| 1,135 | `' duet with '` |
| 717 | `'feat.'` |
| 579 | `' ft.'` |
| 380 | `'feat. '` |
| 90 | `'featuring'` |
| 74 | `'ft.'` |

### Read

**The featured-artist weight is very nearly dead code in ListenBrainz's production job.** It
fires on 882 of 7.17 million credit lines. The single most common featured phrase in
MusicBrainz, `' feat. '` with a leading and trailing space, occurs 639,747 times and matches
**none** of ListenBrainz's eight literals, all of which are unspaced. Only the 717 credits
that happen to store `'feat.'` with no spacing at all are weighted.

This confirms the review's mechanism finding with a magnitude, and it settles the standing
project reading that the weight means "0.25 for a featured artist". **The code says that; this
corpus does not.** Two documents reason from that reading — a findings note and the comment
above `drop_featured_credit` in `config.py`. Neither is wrong about the code, and **neither is
in scope to change here**; recorded so the next reader of either knows.

### What this changes, and what it does not

**It does not change the reimplementation.** Fidelity to ListenBrainz's behaviour is the
requirement whether the term is live or dead, and the pre-registration's §6 fixes the synthetic
fixture against their SQL either way. **A "sensible" implementation that trims would apply a
quarter-weight to 712,878 credit lines that ListenBrainz weights at 1**, and the resulting gap
would surface at the fidelity criterion as a difference the design has pre-authorised calling
lineage drift. That is precisely the error that would otherwise surface never.

**It does bound how much of that criterion can turn on getting it wrong**, which is the reason
to measure it before the criterion is read rather than after.

---

## 4. `R-USERS` — the heavy-user census (`LBD-R9`, cheap half)

> **Plain sentence: which accounts hold the listening, and could a handful of heavy users or
> bots be shaping the pairs?**

**This decides nothing**, by design — plan Task 1 step 5 says so explicitly, and whether a
user-level filter becomes an arm is a decision the pre-registration declines to take. Taking
it later would need a fresh pre-registration, because by then results exist.

**90,606 distinct accounts** hold the 2,708,495,599 listens.

| | listens | share |
|---|---:|---:|
| largest single account | 4,784,019 | 0.177 % |
| top 20 accounts | 53,786,938 | 1.986 % |
| top 100 accounts | 164,731,560 | 6.082 % |
| top 1,000 accounts | 622,158,680 | 22.971 % |

Listens per account: **median 1,379**, p90 88,934, p99 354,905, p99.9 1,139,343.

### Read

**Concentration is real but moderate, and no single account dominates.** The largest holds
under a fifth of one percent of all listens, and the twenty largest under two percent
together. ListenBrainz's own `contribution` cap already bounds what any one account can add to
a single pair, at 3 under `ALG-B`'s parameters — so an account with a million listens can still
move any given pair's score by at most 3.

**⚠ The extreme bot `LBD-P1` saw is NOT in this input, and the reason is a date.** That probe
found an account logging 1,512,318 listens in a single day, on the incremental covering
2026-09-05 to 2026-09-06. **This dump was cut on 2026-09-01**, four days earlier, and no
account in it has an all-history total consistent with sustaining that rate. So the pinned
corpus does not contain that spike. **Do not carry `LBD-P1`'s bot figure into any statement
about this dump** — the two files are different inputs, and this is exactly the confusion
`crawl-resume`'s "archives and graphs are not interchangeable" rule exists to prevent.

**This decides nothing**, per plan Task 1 step 5. Whether a user-level filter becomes an arm is
a decision the pre-registration explicitly declines to take, and taking it after results exist
would need a fresh pre-registration. Whether ListenBrainz filters such accounts upstream of its
own similarity job is still unchecked; it is not visible from the dump.

---

## 5. What is NOT established here

- **Nothing about the similarity computation.** No arm ran, no pair table exists, no graph was
  built. Every one of `LBD-C1`, `LBD-C2`, `LBD-C3` and `LBD-M1` is unmeasured.
- **The dump's byte-identity to the published tar** — see the warning in §1. The inputs are
  pinned by path and internally consistent; they are not checksum-verified against
  ListenBrainz.
- **Whether the added artists' listens are *co-occurring* in the way similarity needs.**
  `R-SUPPLY` counts listens and listeners per artist. Whether those listeners *also* played
  other artists inside a session is the pair computation itself, and is `LBD-S2`'s.
- **The size or run time of the all-history aggregation.** Still the track's largest unmeasured
  quantity; the pre-registration gates it (`LBD-G4`) rather than estimating it.
- ~~**Anything about `recording_gid_redirect`.** `LBDR-F4` notes Task 1 omits it, and this
  session did not add it: the recording table does not resolve redirects, so a share of
  `recording_mbid` values in the listens will not join and will fall back to the 180-second
  default duration. **Deferred to `LBD-S2`, where the unmatched share is measurable against
  the frame that consumes it** — measuring it here would need the join this session does not
  yet build. The plan's Task 3 already says to record that share.~~
  **✅ DISCHARGED 2026-09-08 by `LBD-` Task 3.** The redirect table was extracted from the
  same pinned `mbdump` and the frame rebuilt as LB builds it
  (`data/postgres/recording.py:16-33`), so the omission no longer exists. Its **effect** was
  then measured directly rather than argued, by running the same user slice with and without
  the redirect arm: the difference is a small fraction of one percent of pairs.
  **Figures are owned by [`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md)
  §1 and are not restated here.** Struck rather than deleted: the deferral was tracked and
  discharged, which is a different thing from never having been recorded.

## 6. One cross-reference correction for a later reader

Plan Task 4 step 2 says to confirm the pinned archive's identity "in the `LUX-E1` README".
There are **two** `LUX-E1` analysis directories and the snapshot is pinned in
[`../2026-09-05-lux-e1-armb/README.md`](../2026-09-05-lux-e1-armb/README.md) §2 (`AM2`), not
in `2026-09-05-lux-e1-drift-source/`, which does not mention it. Both
`grt-archive-algb.pre-cex-snapshot` and the live `grt-archive-algb` tree exist in the main
tree; they are **not** interchangeable, and the snapshot is the one the served map was built
from.
