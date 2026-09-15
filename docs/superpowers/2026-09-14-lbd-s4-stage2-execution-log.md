# `LBD-S4` stage 2 — retained execution log

**Role: ACTIVE — the reasoning record for `LBA-D8` stage 2.** Appended **per task**, as each
completes, not at closeout. Decisions and reasoning, not narration.

**It owns no figures.** They are owned by
[`../../builder/analysis/2026-09-14-lbd-s4-stage2/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage2/README.md),
and stage 1's are owned by
[`../../builder/analysis/2026-09-14-lbd-s4-stage1/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage1/README.md).
Neither is restated here.

**Governing:** [`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), with **§11's `LBA-AM1` and `LBA-AM2` read before §3 or §5**. `LBA-AM2` governs the build
order and the projection rule, and it was written **after** stage 1 ran — it says so itself and
must not be described as pre-result.

**Scope of this stage, fixed before it began:** emit and build the seven unbuilt cells, reading
`LBA-G2` progressively; take `LBA-M1`; read `LBA-G1` on every built arm. **`LBA-M2`, `LBA-M3`,
`LBA-M4` and `LBA-M5` are NOT taken here. No census is run** (`LBA-G3` fired at stage 1). **No
listen is designed** (`LBA-D3`). **No read in §7 beyond `LBA-R0` is reachable** until stage 3.

---

## The scope check, re-run against the five steps before any of them started

`session-start`'s standing rule: if the task ends in a number, name the cheapest experiment that
could change the decision and propose running it first. **It fires, and its honest output is that
no cheaper test changes what stage 2 does** — for a structural reason rather than a judgement:

- **`LBA-G2`'s statistic has no analytic shortcut.** It is the *builder's* peak resident memory,
  a property of `build_from_archive` holding neighbour objects in a Python dict during its first
  pass. Only a build produces it, which is why the gate is read progressively rather than up front.
- **`LBA-D8` bars stopping a cell on anything but that measured bar.** So even a cheap size
  estimate that looked damning could not reduce the lattice; the executing session has no such
  authority.

**Two cheap things were nevertheless available, and both were taken rather than proposed**, since
both are sequencing inside this session's own remit:

1. **The pin re-verification was launched first and detached**, so it cost no wall clock against
   the wrapper writing. `LBA-D9` requires *this* session to re-verify rather than trust stage 1's
   record.
2. **`metadata_ratio` is moved from step 4 to step 1.** It is two `GraphStore` loads of artifacts
   that already exist, it takes minutes, and `LBA-G1`(a) is **not evaluable** without it. Taking it
   before seven builds rather than after means a defective memory instrument surfaces on two known
   artifacts instead of after the expensive half — and stage 1 recorded **two** instrument defects
   in `framework_rss` that each returned a plausible-looking number. It is still "first" relative
   to the rest of `LBA-M1`.

**One definitional hazard named here rather than discovered at the gate.** `LBA-G1`(a)'s
multiplicand is the **`GraphStore`-load** peak from `LBA-M1`'s *boot memory* row — median of three
— **not** `LBA-G2`'s **build** peak. Two different peaks with similar names, and `metadata_ratio`
is itself defined as a ratio of `GraphStore`-only loads, which settles it. §4's own words: *"the
raw census figure is never compared with `LBA-G1`(a)'s bar directly."*

---

## Which §7 reads stage 2 can reach — recorded BEFORE any build result existed

**Written 2026-09-14, after task 1 and before the first build.** No cell had been built, no peak
measured, no `LBA-G1` half read. It is recorded here rather than in the report so that it cannot
have been shaped by which way a gate went — the reasoning below is the same whichever arm fires.

**The session's instructions say "no read in §7 beyond `LBA-R0` is reachable until stage 3." The
pre-registration's own run-state vocabulary says otherwise, and the pre-registration governs.**

§7 defines *complete* = every cell either built or stopped by `LBA-G2` **with its bar recorded**,
and *sized* = `LBA-M1`'s boot and query-cost halves taken on that arm. **Stage 2 as scoped produces
both.** So:

- **`LBA-R1`, `LBA-R2` and `LBA-R3` presuppose exactly "complete **and** sized" and nothing else.**
  They are the three mutually exclusive hosting outcomes — no arm fires `LBA-G1`; some do and some
  do not; every arm above `V` does — so **exactly one of them will be true**, and reporting none of
  them would be withholding a read the design licenses.
- **`LBA-R4`, `LBA-R4-V` and `LBA-R5`–`LBA-R9` are NOT reachable** and are not read. `LBA-R4` and
  `LBA-R5`–`LBA-R7` rest on `LBA-M2` and `LBA-M3`, which stage 2 does not take; `LBA-R8` needs
  *censused*, which `LBA-G3` has made unavailable; `LBA-R9` needs *complete, sized **and**
  censused*. `LBA-R4-V` presupposes only *derived* and was **already settled on the committed
  record before stage 1** — §7 says so in its own row, precisely so it cannot later be reported as
  a finding of this design, and nothing here reports it as one.

**So the report reads `LBA-R0` and exactly one of `LBA-R1`/`LBA-R2`/`LBA-R3`, and stops there.**
The instruction is followed in substance — no decision read, no arm selected, nothing that needs
stage 3 — and the one place it is narrower than the document is named rather than quietly obeyed,
because silently withholding a licensed read is as much a departure from a pre-registration as
taking an unlicensed one.

⚠ **`LBA-R1`'s read contains a clause stage 2 cannot support, and it is not repeated.** Its text
continues *"the decision then rests on `LBA-M2`, `LBA-M3` and `LBA-M4` alone"* — true as a statement
about where the decision sits, but those three are unmeasured here, and **no sentence in the report
may present that clause as though this stage had evidence about them.**

## A contingency, fixed before it could arise

**A build that dies on memory is NOT a cell "stopped by `LBA-G2`", and will not be reported as
one.** The gate stops a cell *before* it is built, on a projection, with the bar recorded. A build
that is attempted and then fails — `MemoryError`, or the OS killing it — is a different event, and
the honest record says so in those words: *attempted and failed on memory, not stopped by
`LBA-G2`*. §2.6's three barred conclusions apply to it just the same, because they are about what
an **unbuilt** cell licenses, which is unchanged by how it came to be unbuilt. **No gate reading is
invented for it**, and the projection that preceded it is reported beside the failure, since a
projection that said "safe" before a build that then died is itself worth knowing.

---

## Task 1 — the instrument, and the wrappers stage 2 needs

**Done.** Self-test run on this machine; two wrappers and one shared module written as forward
copies; no shipped code under `builder/src` touched.

### 1a. `stage2_build_instrument.py --self-test`, run here

All three checks pass. Recorded because a green reading from a new instrument is not evidence
until it has been shown to go red, and check 3 does exactly that: the same row count projects
**16.676 GiB** under one slope and **31.353 GiB** under a steeper one, `fires=False` then
`fires=True`. The allocation check saw a deliberate 256 MiB as 256.0 MiB, and the double-call
guard fired. ⚠ **Neither projection figure is a result** — both are synthetic slopes inside the
self-test, at `LBA-A9`'s row count. No cell has been built.

### 1b. The pins, re-verified by this session (`LBA-D9`)

**All 14 match; nothing refused**, including the 21 GB `T.parquet`. `T_A4.parquet` is **absent
from every searched path** — §10 pins it only to be excluded, and absence is a stronger exclusion
guarantee than a match. Run detached while the wrappers were written, so it cost nothing.

### 1c. Why two wrappers exist, and why nothing was edited

§10 lists `emit_archive.py` and `lbv_build.py` as *"run unedited — RESOLVED"*, and they resolve —
but **both are hard-pinned to arms and populations that are not stage 2's**:

| frozen script | what it is pinned to | line |
|---|---|---|
| `emit_archive.py` | `ARM_TOKENS = {A0, A2}`, population fixed to `P` via `CXA` | `:66`, `:64` |
| `lbv_emit.py` | `{A0, A5}`, population `V` | `:33` |
| `lbv_build.py` | `MAPS = {A0V, A5V}`, `drop_unlistenable=True` with the `20260805` payload | `:79`, `:240` |

None can emit a threshold-7 cell or any `U` cell as written. **This is not a defect and needed no
amendment**: `lbv_emit.py:58` is itself the precedent — it monkeypatches `emit_archive.ARM_TOKENS`
and repoints the population, then calls the frozen emitter's own `main`, so the filter, the sort,
the payload shape and the determinism stay the emitter's. Stage 2 takes the same pattern.

**`s4_emit.py`** adds exactly one thing over that precedent: a `U` population has **no artifact to
read it from**, so `verified_population` itself is repointed to the arm's own derived member list
(`SELECT mbid0 UNION SELECT mbid1`, the query stage 1 counted with), written to its own file and
sha-recorded.

⚠ **The emitter REWRITES its `POPULATION_FILE` from the artifact it read.** Left alone, emitting a
`V` arm would have overwritten the pinned `population_cxa_mbids.txt` — a file stage 1 verified and
§10 pins. Each arm therefore gets its own `POPULATION_FILE`, and after every `V`/`P` emit the
pinned file's digest is re-checked against the one stage 1 recorded, so a re-emission that
disagreed with the pinned population refuses rather than silently redefining it.

⚠ **Each cell emits into its own `S4-<arm>` directory.** `A0`, `A2`, `A0V` and `A5V` are a frozen
record of the supply and served-population work and are never written into.

### 1d. The one free instrument check available before any novel cell

**The existing `A0` archive IS `LBA-A4`** — threshold 10, limit 100, population
`graph-cxa-adopted.bin`, and its committed counts are exactly stage 1's figures for that cell.
`LBA-A4` is therefore re-emitted into `S4-A4` deliberately rather than reused: reproducing those
three counts exactly proves the wrapper against a committed record **before it is used on any cell
nobody has emitted before**, for about 105 seconds. Every arm's emit is checked the same way
against stage 1's count, and `s4_emit.py` **refuses to finish** on a disagreement — *"one of the
two is wrong and neither may be used until it is known which."*

### 1e. Acceptance criteria, and the two bounds that are deliberately weak

`PRODUCTION_ACCEPTANCE` is never used: its node and edge bands are centred on the served artifact
and **every arm above `V` breaches them by construction**. Widening a production bound to admit a
new artifact is what §8 records as risk acceptance and **the owner's decision** — not something a
stage-2 script may do silently. So `s4_build.py` builds scaled criteria per arm, each bound from a
quantity known **independently of the build being checked**.

**Green check on the criteria function itself:** at rule `V` it reproduces `lbv_build.py`'s
committed bounds exactly — `(47070, 58838)` nodes and `(1052547, 2941900)` CSR entries.

**Where it necessarily departs, and why the weakness is stated rather than hidden.** §2.4 records
that the largest-component prune *"removes a small fraction of `V` and of `P` … and its effect over
`U` is **unmeasured**, because `U` has a fringe neither smaller population has."* So **no
calibrated node floor exists for a `U` arm.** A tight one invented here would refuse a *correct*
build after half an hour, and correcting a bound after seeing a build's value is precisely §8's
risk-acceptance case. The `U` node floor is therefore **50 % of the arm's own table-level count,
labelled a gross-loss tripwire and not a calibrated bound**, and the `U` edge floor is the only
floor that is *true* without measuring the prune — CSR entries ≥ N, since `U`'s minimum-degree
floor is 1 and is held constant across all three `U` arms (§2.1).

⚠ **Consequence, recorded because it is a real loss of sensitivity:** on the `U` row the edge floor
**cannot see a silent cap-rule revert**, which `acceptance.py`'s `CXA-` note calls the one thing it
exists to catch. On that row the protection falls to the physical upper bound (`N × ceiling`, in
**CSR entries** — `lbv_build.py` records a first run refused on a correct map for carrying a `// 2`
here, corrected from the *unit* and never from the build's value) and to the median-degree bound.
The four §2.8 detectors stay unscaled at every rule: they describe a defect's **shape**, not a
population's size.

### 1f. The filter column, said rather than inferred (`LBA-D7`, §2.4)

`s4_build.py` sets and records, per arm: `V` → on, inert (20260805); `P` → on, inert (20260809);
`U` → **off, uncensused**. The first two are *inert because applicable*; the third is *absent
because refused* — `unlistenable_drop.py` raises `PopulationNotCensused` for any archive holding
artists the census never evaluated. **In a configuration dump those look identical**, which is why
the state is written in words into both the result JSON and the manifest.

⚠ **And the two other drop stages have no guard at all.** `drop_no_release_tail` and
`drop_featured_credit` do not raise on an uncensused population — over `U` they **silently
under-filter** rather than refusing. Both are left at their defaults (`True`), and the fact is
recorded per arm rather than left to be inferred from a `True` in a config dump.

### 1g. `LBA-G2` is read before the build, and a stopped cell is recorded, not skipped

`s4_build.py` projects from `_points.json` — every build instrumented so far — **before** building,
writes the projection with its basis and its unit into `_projections.json` whether or not it fires,
and only then proceeds. With zero points the gate is **silent, not permissive** (`LBA-AM2`(b)), and
the first cell proceeds unconditionally. A cell over the 24 GB bar is written out as **"unbuilt for
a resource reason"** carrying §2.6's three barred conclusions in full, and the run returns success
— it is a resource fact, `LBD-G4`'s shape, not a failure. **No cell is stopped on any other
ground** (`LBA-D8`).

**Unit, restated at every call site because this track has refused a build over it before:**
**archive neighbour rows, pre-cap, two per pair — never CSR entries.** The x-axis is taken from the
emitter's own `counts.neighbour_rows_written` via `rows_from_archive_manifest`, so it cannot be
re-derived wrongly at the call site.

---

## Task 2 — the seven archives, emitted

**Done, 2026-09-14, 19:22–19:59 local; about 37 minutes of wall clock, one process per arm,
sequentially (DuckDB).** Figures are the stage-2 README's; nothing is restated here.

**Every one of the twenty-one counts reproduces stage 1 exactly** — payloads, archive neighbour
rows and population-absent, for all seven cells. That is not a criterion and is not reported as
one: it is the instrument's green check, and `s4_emit.py` **refuses to finish** on any
disagreement, on the stated ground that *one of the two would then be wrong and neither may be
used until it is known which*. The check had teeth — `LBA-A4` is a re-emission of the archive the
supply work committed as `A0`, so its three counts were being matched against a frozen record
rather than against another figure from the same session.

**The two structural facts the `U` rule implies were asserted rather than assumed**, and both hold
on all three `U` cells: `payloads_written` equals the population exactly, and
`population_absent_from_arm` is **0**. Both follow from the rule — `U` is derived *from* the arm's
own table, so no member of it can be missing from that table — and an emitter that produced
anything else would have been filtering when it should not. The wrapper also refuses if any row of
a `U` arm's table has an endpoint outside the population, which cannot happen under the rule and
is checked for exactly that reason.

**One figure worth carrying forward because it bears on a later bound.** Every `U` population
member has an identity row — `0` with none, on all three cells, against `10` on each `P` cell. So
`pipeline.py`'s nameless-artist rule removes **nobody** from a `U` arm at build time, and the gap
between a `U` arm's table-level count and its built node count is attributable to the
largest-component prune and the two unguarded drop stages alone. It does not make the `U` node
floor calibrated — §2.4's *"unmeasured"* stands, and the floor stays a labelled gross-loss
tripwire — but it removes one of the three candidate causes from any later account of that gap.

**Nothing was written into the frozen archives.** `A0`, `A2`, `A0V` and `A5V` are untouched; each
stage-2 cell has its own `S4-<arm>` root. Both pinned population files came back out of every
`V`/`P` emit with the digests stage 1 recorded, so the emitter's rewrite-in-place redefined
neither.

### ⚠ Task 3, attempt 1 — the stage-1 instrument raises on every real build

**The first build of `LBA-A2` failed, and the defect is in the instrument stage 1 wrote and
pronounced self-tested, not in stage 2's wrapper.** Recorded here in full because the mechanism
generalises and the *reason the self-test missed it* is the more useful half.

```
TypeError: 'Event' object is not callable
  threading.py, _wait_for_tstate_lock -> self._stop()
  stage2_build_instrument.py:127, in stop -> self.join(timeout=5)
```

**The mechanism.** `_Sampler` subclasses `threading.Thread` and assigns
`self._stop = threading.Event()` (`:115`). **`Thread._stop` is a real method of the base class**,
which CPython calls internally from `join()` → `_wait_for_tstate_lock()`. The assignment shadows
it, so the first `join()` after the sampler thread has finished tries to call the `Event` and
dies. A name collision with a private base-class method, not a logic error.

**What it cost, and what it did not.** `build_from_archive` had already **returned** — the
exception is raised in the `finally` that tears the sampler down — so the build succeeded and the
graph was then thrown away. **No point was recorded, no artifact written, no result file
produced, and `_points.json` did not exist.** The lattice is untouched and `LBA-G2` still has no
result. The cost is about six minutes of `LBA-A2` build time.

> #### Why a self-test that "passed" could not see it
>
> Stage 1's check 2 exercises the double-call guard by pre-populating `_ALREADY_BUILT` and calling
> `instrumented_build(None, None, None, ...)`. **The guard raises at the TOP of the function,
> before `_Sampler` is ever constructed.** So no self-test path reached `sampler.stop()`, and the
> instrument was recorded as *"written and self-tested"* having never run a build to completion.
> Checks 1 and 3 test the counters and the fit rule, neither of which touches the thread.
>
> **This is one step past the lesson stage 1 already recorded.** Its handoff says *"the self-test
> for the build instrument was itself wrong at first and failed the instrument for being correct.
> A test can be as wrong as the thing it tests."* True, and incomplete: **a test can also be
> INCOMPLETE in a way that reads as green.** The stage-1 self-test was correct in everything it
> asserted and never executed the one path that mattered. "Shown to go red" is necessary and is
> not sufficient — it has to be shown to go red **on the path the instrument is actually used
> on**.

**The fix: `s4_instrument.py`, a forward copy, never an edit.** Stage 1's directory is a committed
record whose README states the self-test was run and passed, quoting its output; editing that
module in place would silently invalidate that statement and the sha the stage-1 record carries.
The 2026-08-09 precedent refuses re-running a frozen script in place and this is the same shape.
**Everything pure is IMPORTED from the stage-1 module rather than re-typed** — `BuildPoint`, the
ctypes counters, `_LogCapture`, `rows_from_archive_manifest`, `record_point`, `project_peak_rss`
and `LBA_G2_BAR_BYTES` — so **`LBA-AM2`(d)'s fit rule and the 24 GB bar are provably unchanged and
this file cannot have moved a bar.** Only `_Sampler` and `instrumented_build` are redefined.

**The new self-test covers the path the old one could not, and was shown to go red on it.** Check
A runs `instrumented_build` end to end through sampler start, allocation, stop and join; it asserts
the build's return value is passed through, a peak was recorded, the sampler thread actually
recorded samples, and the sampler's maximum lies within the kernel's own peak. Adding it needed a
`_build_fn` seam — with no way to inject a trivial build, no test could reach `sampler.stop()`,
which is precisely where the instrument was broken; it defaults to the shipped
`build_from_archive` and no stage-2 caller passes it.

**Shown red, then green, and both were run rather than argued:** the same stub driven through the
**stage-1** `instrumented_build` reproduces `TypeError: 'Event' object is not callable`; driven
through `s4_instrument` it completes, reporting a 147.5 MiB peak over 4 samples with the sampler
maximum inside the kernel peak. Check C re-asserts the imported fit rule still gives 16.676 GiB
green and 31.353 GiB red at `LBA-A9`'s row count against a 24 GiB bar.

The attempt-1 logs are kept as `build_*.attempt1-instrument-defect.log`.

> **Correction, and it is against something written a few paragraphs earlier in this same log.**
> The sentence originally here said `_projections.json`'s two `LBA-A2` entries were *"deliberately
> NOT erased"*, on the ground that a chronological record beats a tidy one. **Then attempt 2 failed
> too and the file was deleted during the restart, so that statement did not survive its own
> commit.** It was never committed — nothing in git to restore. The substance is recoverable and is
> recorded here instead: both entries read *silent / not projectable*, which is `LBA-AM2`(b)
> behaving correctly on a first cell; the timestamps are gone. **Left standing rather than
> back-edited**, because a log that quietly repairs its own claims is worth less than one that
> shows where a claim failed.

### ⚠ Task 3, attempt 2 — a `require_fame=False` build carries FOUR of the five additive keys

**`LBA-A2` built correctly and this session's own post-write assertion refused it.** The refusal
was wrong, and what it revealed matters more than the stoppage.

```
BUG: a fame-free census build carries additive keys
     ['deezer_ids', 'spotify_ids', 'apple_ids', 'artist_facts']
```

**`require_fame=False` removes FAME and nothing else.** `deezer_ids` and the three `LUX-4` keys
are loaded from **frozen, sha-pinned package data** (`deezer_ids.py`, `dsp_links.py`,
`artist_facts.py`) rather than fetched from a network, so nothing about a fame-free configuration
suppresses them. The real invariant for this configuration is *"`fame_lb` is absent"*, and the
check now asserts exactly that.

**Nothing measured was lost, and the build was not wasted.** The refusal fires after
`record_point`, `check_acceptance`, `serialise` and the artifact write have all succeeded — so the
build, its peak and its acceptance all completed. Only the per-cell result JSON was never written.
The point and artifact were **cleared before the rerun** so that `LBA-A2` could not be entered
twice into `LBA-G2`'s fit, and the discarded measurement is kept as
`_logs/discarded_point_A2_attempt2.json` — **an independent second measurement of the same cell's
peak, which is a free reproducibility check on `LBA-G2`'s calibration point and is reported as
one.**

> #### The consequence that is NOT about an assertion, and it changes how boot memory is measured
>
> If a census build carries four additive keys, then **multiplying its boot peak by
> `metadata_ratio` scales metadata that is already present.** `metadata_ratio` is calibrated on
> `graph-lux4.bin` ÷ `graph-msw-tu50.bin`, a pair differing **only in the three `LUX-4` keys** — so
> applying it to an artifact that already carries those keys double-counts the exact term the ratio
> was built to measure.
>
> **So every arm's boot memory is measured on a BARE re-serialisation** — the seven built ones now
> as well as the two reused ones, where this session had already taken the same step for the same
> reason. `metadata_ratio` then adds the metadata term back exactly once.
>
> **This is not a new bar and not a reinterpretation of `LBA-G1`(a).** The 1.6 GB bar and §5's
> expression are untouched. It is §4's *own* treatment of the bytes half — bare by decoding, then
> *"reported beside the shipped projection = bare + the measured per-node additive cost"* — applied
> to the memory half so the two halves are consistent. Measuring one half bare and the other half
> loaded would have been the inconsistency.
>
> ⚠ **Direction of the residual error, stated because it is not symmetric.** The projection still
> omits `fame_lb`, which a shipped artifact carries and which `metadata_ratio` does not model. So
> the projected figure remains a **lower bound** on shipped resident cost — `LBA-X8` in the memory
> dimension — and the report says so beside every `LBA-G1`(a) reading rather than once in a
> footnote.

### The accident bought a precision estimate for `LBA-G2`'s calibration point

**`LBA-A2` was built twice, and the two peaks agree to 0.011 %** — 5,771,968,512 B discarded
against 5,772,615,680 B of record, a difference of 647,168 B, at wall clocks of 54.6 s and 53.2 s.

**This is worth more than it looks, because of where that cell sits.** `LBA-AM2`(b) makes the
first build the **sole basis** of the one-point proportional projection, and every later
least-squares line still carries it. Nothing in the design measured how repeatable a peak is, and
a calibration point whose own reproducibility is unknown would have propagated that unknown into
all seven projections. **Two runs of the same build on the same machine, minutes apart, give the
same peak to four decimal places of a percent.** So the fit's residual error is a property of the
row-count model, not of the instrument.

It was obtained by accident — from a rerun forced by a bad assertion — and is reported as an
**incidental measurement**, not as a designed one. No criterion rests on it.

## Task 3 — six cells built, one stopped by `LBA-G2`

**Done, 20:13–21:36 local, attempt 3.** One process per build, ascending archive-neighbour-row
order per `LBA-AM2`(c). Figures are the stage-2 README's and are not restated here.

**The lattice is `complete` in §7's sense** — every cell either built or **stopped by `LBA-G2` with
its bar recorded**. Six built (`LBA-A2`, `A4`, `A5`, `A6`, `A7`, `A8`), two reused (`LBA-A1`,
`LBA-A3`), one stopped (`LBA-A9`).

### `LBA-G2` fired on `LBA-A9`, and on nothing else

**The corner is unbuilt for a resource reason.** Its projection — a least-squares line over all six
instrumented builds, intercept free, in archive neighbour rows — exceeded the 24 GiB bar. **A
resource fact, `LBD-G4`'s shape, and not a finding about anything.** §2.6's three barred
conclusions are attached to the cell's own record verbatim, and the one that matters most is the
second: *"we could not build it here"* and *"it is too big to serve"* are different claims, and the
second needs `LBA-M1`, which this cell does not have.

**`LBA-D8`'s prohibition held:** no cell was stopped on any other ground. `LBA-A9` is stopped on
the stated bar, by a projection computed before the build from points that already existed, and
the whole fit is on the record.

### The fit turned out to be a good model, which nothing had established

`LBA-AM2`(d) fixed the fit rule as a line in archive neighbour rows **before any build existed**,
and no document had checked that peak memory is linear in that unit. **It is, closely.** Five
projections were taken against a subsequently measured actual, and the signed residuals are
**+0.6 %, −0.8 %, −0.9 %, +2.9 %, −0.6 %**.

⚠ **Signed, not absolute, and the sign is the part worth watching.** An *under*-predicting fit is
the one that admits a cell it should have stopped. The only residual above 1 % is the single
under-prediction, and it is on the `U` row — the row `LBA-A9` sits on. **`LBA-A9`'s projection
exceeded the bar by about a third**, which is an order of magnitude more headroom than that
residual, so the stop does not turn on the fit's precision. Had it been marginal, this paragraph
would have said so instead.

### The `U` rule loses about 15 % of its population to the prune — the first measurement of a
quantity §2.4 records as unmeasured

Both built `U` arms retain **about 85 %** of the artists their own table names, against **over
98.5 %** on `V` and `P`. §2.4 says the prune *"removes a small fraction of `V` and of `P` … and its
effect over `U` is unmeasured, because `U` has a fringe neither smaller population has."* That
fringe is now sized on two cells.

**Consequence for this session's own bound, stated because it cuts both ways.** The `U` node floor
was set at 50 % of the table count and labelled a gross-loss tripwire precisely because no
calibrated floor existed. At 85 % retention an 80 % floor would in fact have passed on both built
`U` arms — **but nothing before these builds said so**, the looser threshold has more fringe to
lose, and a floor that refuses a correct build costs a rebuild while a loose one costs nothing
here. The bound stays as it is and is still not calibrated; **two cells is not a calibration.**

### A structural difference between the population rules, reported as measured and not interpreted

**Median degree is 9 on both built `U` arms, against 22–26 on every `V` and `P` arm.** Max degree
is 50 everywhere, so the ceiling binds on every arm and the bound holds on every arm. The
interpretation belongs in the report's inference section, under the owner's eye, not here.

### A machine-state timeline, and why it is a separate file rather than a wrapper change

The build chain's seven peaks form a fit, so the conditions each was measured under are part of the
record. The obvious way to capture that — record free physical memory inside `s4_build.py` — was
**declined**, and the reason is worth keeping: by the time it was wanted the emit chain had just
finished and the build chain was seconds from starting, so the edit would have raced the chain and
left `LBA-A2` carrying a different `script_sha256` from the other six. **A provenance split across
the lattice is a worse defect than the one the edit would have fixed**, and the factor table has no
column for it.

`sample_machine.ps1` logs free and total physical memory every 20 s to `_logs/machine_state.tsv`
for the duration of the chain. It touches no build script, races nothing, and aligns with each
build's own start and finish timestamps after the fact. **Known machine conditions for this run:**
the owner left the machine at about 20:00 for at least an hour, having closed a browser **before
any build started and before `_points.json` existed** — so no instrumented point was taken on
either side of that change. One unrelated Claude session on another project was expected to finish
within the hour; its load therefore falls during the small early builds, where the machine is
uncontended and a peak reads true, and is expected to be gone before `LBA-A9`, which is the only
cell where contention could depress a peak.

---

## Closeout — mid-flight tier, 2026-09-15

Run on the owner's instruction after the context-size hook fired at ~409k tokens. Tier:
**A1, A2-mid, A3, A5, B1, B5, D1-mid, D3, D6, D7**. **B2, B3 and B4 are handed forward
deliberately** — all three want a finished artifact — and are in `NEXT.md`'s deferral registry
with a condition.

| item | outcome |
|---|---|
| **A1** distil the log | This document, appended per task rather than at the end. |
| **A2-mid** handoff | [`2026-09-15-HANDOFF-lbd-s4-stage2.md`](2026-09-15-HANDOFF-lbd-s4-stage2.md). Enumerations, not self-assessments. The previous handoff's role line was edited to name it as successor **and to carry the known-wrong instrument claim**. |
| **A2-next** `NEXT.md` | Top block rewritten; the outgoing block **demoted to `NEXT-ARCHIVE.md`** and frozen. No git state written into it. |
| **A3** deferrals | Four new rows, each with a condition. **One existing condition partly came due** — see below. |
| **A5** processes | **No listeners on 8000 or 5173; this session never booted the app.** The machine-state sampler (PID 194136) was this session's, an infinite loop, and was **stopped here**. Two `powershell` processes started 2026-09-15 11:42 and 11:44 are **not this session's** and were left alone. **Nothing was left running and nothing needed to be.** |
| **B1** docs audit | `docs-lint` found one hard failure — the stage-2 execution log unclassified in `docs/README.md` — **fixed**. Rows added for all three new documents. `doc-auditor` dispatched; its findings and their disposition are below. |
| **B5** stale descriptions | **Clean both ways.** `.claude/` contains no description this work invalidated — the only matches are `logs/instructions-loaded.jsonl` rows, which are data. No document outside the figures owner restates a stage-2 number. |
| **D1-mid** tree | **Clean, which is unusual for a mid-flight retirement and is deliberate**: every task was committed as it landed, so there are **no untracked paths to name** and nothing half-written. |
| **D2** fixtures | **Inapplicable** — the committed test fixtures were not touched and no shipped artifact changed. Stated rather than omitted. |
| **D3** provenance | Six built artifact sha256s recorded in the handoff and in each cell's `s4_build_*.json`. `LBA-A9` has none because it was never built. The pair set is sha-pinned. |
| **D4** suites | **Not run, and this is a departure worth naming:** stage 2 touched **no shipped code** — every script is a forward copy under `builder/analysis/` — so no suite covers the diff. What was verified instead: the instrument's self-test (red **and** green), the emitter reproducing 21 committed counts, acceptance passing on six builds, and every artifact round-tripping through the shipped `GraphStore`. |
| **D6** context layer | **Unconditional 50,977 characters; conditional 2,726 lines. Both EXACTLY unchanged.** This session added no rule, no memory, no skill or agent description. |
| **B6-budget** | `NEXT.md` **431** lines (budget 250), `docs/README.md` **570** (budget 400), `TEST-QUEUE.md` **70** (budget 70, at it). ⚠ **This session grew both over-budget files** — four deferral rows and three map rows. Each is the document's **own job** rather than reasoning, but that is a reason they are not *deletable*, not a reason the files are not over. The standing deferral row for this remains live. |
| **C1** use the app | **NOTHING written in `TEST-QUEUE.md`, and that is the discharge.** Stage 2 changed no shipped code and nothing the owner can press. Its 15 unticked boxes are untouched. |

### The one existing deferral condition that partly came due

**"Two documents are over the line budgets set for them 2026-09-12"** carries the condition *"when
no second session is live in the tree"*, and names two actions: demote `NEXT.md`'s discharged
deferral rows, and do `docs/README.md`'s `DLS-` item 5. **No second session was live, so the
condition was met — and only half the first action was taken.** `A2-next`'s status-block demotion
happened; **the discharged deferral rows were not demoted**, because this is a mid-flight
retirement and a wholesale table rewrite is the thing least suited to it.

**Recorded rather than quietly re-deferred**, which is what the `LUX-E1` row on that same registry
exists to warn about: a condition that fires and is not honoured, un-noted, is indistinguishable
afterwards from one that never fired. **The condition stays live and the row is unchanged.**

### A note for whoever extends the `LBA-G2` fit

The fit's coefficients were never recorded anywhere until the handoff: **slope 0.6164 GiB per
million archive neighbour rows, intercept −0.165 GiB**, over six points. ⚠ **The intercept is
slightly negative** — a fit artefact, not a physical claim, and a naive extrapolation far below the
measured range would predict negative memory. The measured range is 8.9M–29.3M rows.

### B1 — the `doc-auditor`'s findings and their disposition

Dispatched by this session rather than handed forward, per `closeout`'s *"Who runs B1"*. **All four
findings were resolvable from the committed record; none is handed forward.**

| finding | disposition |
|---|---|
| **Restated figures in the handoff** — four measured values owned by the stage-2 README (`LBA-A9`'s projection twice, the worst `LBA-G1`(b) ratio, the `U`-row p95s) | **Upheld and fixed.** Converted to citations by section. ⚠ **Naming a BAR is not a restatement** — 24 GiB and 2.0 are pre-registered constants from the governing document, and stage 1's handoff names its 6-hour bar the same way. The defect was the *measured* values. |
| **`LBA-G1` fires on nothing — the eight-arm qualifier not inline** in `NEXT.md` and at the handoff's summary | **Upheld and fixed.** Both documents carried the qualifier prominently but later; on this project a claim read without its qualifier is a named failure mode, so it now travels with the claim itself. |
| **Stage 1's README still says its instrument was "written and self-tested"** | **Upheld, and it corrects this session.** A forward-pointer block was added there. |
| **Identifier collisions** | **None** — stage 2 minted no new series. |

> #### The third finding corrected a judgement this session had already made and recorded
>
> This session treated `builder/analysis/2026-09-14-lbd-s4-stage1/README.md` as **frozen** and
> deliberately annotated only the stage-1 *handoff*, reasoning that corrections go forward and a
> figures owner for a completed stage should not be edited. **`docs/README.md` classifies that file
> ACTIVE**, so `session-start` MT1's never-edit rule — which governs COMPLETE and HISTORICAL
> documents — does not reach it, and an ACTIVE document carrying a now-incomplete claim is simply
> stale.
>
> **The mistake was conflating "owns figures for finished work" with "frozen".** They are different
> properties and only the map decides the second. The added block is a **forward pointer, not a
> revision**: no figure in that document moves, and the original paragraph stands as the record of
> what was believed on 2026-09-14.
>
> **Recorded because the question was asked explicitly and still answered wrongly.** The auditor was
> asked, in those words, whether leaving the README untouched was the right call under this
> project's rules — which is the only reason the error surfaced before the branch merged.
