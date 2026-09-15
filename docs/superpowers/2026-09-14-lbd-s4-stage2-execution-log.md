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
