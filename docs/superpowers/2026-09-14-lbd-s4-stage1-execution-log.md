# `LBD-S4` stage 1 — retained execution log (`LBA-`)

**Role: ACTIVE — the retained execution log for `LBA-D8` stage 1.** Appended **per task**, as the
work happens, not distilled at closeout. Decisions and reasoning; narration belongs nowhere.

**Governing document:** [`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), read cold and in full including §11's `LBA-AM1` register. **It owns every bar, arm,
threshold and read; where this log and it disagree, it governs and this log is wrong.**

**It owns no figures.** Stage 1's figures are owned by
[`builder/analysis/2026-09-14-lbd-s4-stage1/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage1/README.md)
and are cited from here, never restated.

**Scope, from the owner: STAGE 1 ONLY.** No archive emitted, no graph built, no census run, no
stage 2 begun. The stop is a handoff at the stage-1 seam.

---

## Ordering, and why it is not the order the instruction listed

Two re-orderings were proposed at the scope check and approved before any work began. Both are
methodology — what to measure in what order — and **neither changes an arm, a threshold, a
population rule, a bar or the lattice.**

1. **The `U` population counts come before the two instruments (step 2).** The handoff records the
   `U` population's size as *"genuinely unknown ... the cheapest thing that could change the
   design"*. It is cheaper than the plan assumed: `U` at threshold 10 and `U` at threshold 3 are
   distinct-artist counts over `A0.parquet` and `A5.parquet`, **two files that already exist and are
   sha-pinned** — seconds each, no scan of `T`, no new code. Only threshold 7 needs a derivation.
   Neither instrument in step 2 feeds a gate this stage reads (`framework_rss` → `LBA-G1`(a),
   stage 2/3; peak-RSS instrumentation → `LBA-G2`, stage 2), so answering the design's one named
   unknown first costs nothing and de-risks everything after it.

2. **Step 3 (resolving `LBA-G2`'s first projection from the text) comes before step 2(b).** Step
   2(b) builds the instrument that feeds `LBA-G2`; the resolution determines its shape. Resolving
   the text costs a read and precedes writing the code it justifies.

**A derivation that collapses the union, recorded here because it is load-bearing and checkable.**
A pair kept at threshold 10 is kept at threshold 3: lowering the bar adds only pairs with
`3 < score <= 10`, and `rank()` counts strictly-greater rows, so no added pair displaces a kept one.
Hence **`U`(10) ⊆ `U`(7) ⊆ `U`(3)**, and the union of all nine populations is
**`U`(3) ∪ `V` ∪ `P`** — one set computation, not nine. It is checkable rather than assumed: the
three `U` counts must come out in that order or the derivation is wrong and the work stops.

---

## Task 1 — verify every pinned artifact (`LBA-D9`)

**Script:** `builder/analysis/2026-09-14-lbd-s4-stage1/stage1_verify.py`. **Output:** `verify.json`
(all but `T`) and `verify_T.json` (the full set). Refuses on any mismatch.

**Result: every pin matches.** Thirteen files verified against the sha256s the pre-registration's
§10 and the served-population README's §0/§2/§5 record — the two reused artifacts `LBD-A0V`
(= `LBA-A1`) and `LBD-A5V` (= `LBA-A3`), their two archive `MANIFEST.json`s, the two derived tables
`A0.parquet` and `A5.parquet`, the two graphs `V` and `P` are read from, the two pinned population
files, the three pinned `CXR` strata, and `T`. Figures in the README.

**Three things worth recording beyond the pass/fail.**

1. **Two of the pins exist on the record only as 8-character prefixes** — `population_msw_mbids.txt`
   (`b5e0cb94…`) and `population_cxa_mbids.txt` (`1bbff8fc…`). No committed document carries their
   full 64 hex; the served-population README §0 and the supply README §0 each truncate. A 32-bit
   prefix is a weak assertion of identity on its own, so **each was additionally checked against an
   independently recorded line count** — 58,838 for `V` and 88,685 for `P`, from those same two
   sections — and both match. **The full digests are now recorded in the stage-1 README**, so the
   next session that needs them does not have to repeat this.

2. **`T_A4.parquet` is absent from every path it could plausibly occupy.** §10 pins it *"only to be
   excluded"* (`LBA-D1`: every arm derives from `T`, never from `T_A4`). Its absence is a stronger
   guarantee than a match would have been — no arm can derive from a file that is not there — and it
   is recorded as an observation, not a failure. It is 20.66 GB and was evidently removed after the
   `LBD-A4` read; nothing here needs it.

3. **`LBA-D9`'s "their archives" resolves to the two archive `MANIFEST.json` files**, whose shas are
   in the served-population README §2 rather than in §10's thirteen. Verifying the manifest rather
   than re-hashing the archive trees is what the record supports: the manifest is what
   `build_from_archive` pins and what `build_inputs` names.

**No mismatch, so nothing is refused and the work proceeds.**

## Task 2 — the `U` probe (proposal 1), run before either instrument

**Script:** `stage1_u_probe.py`. **Output:** `u_probe.json`.

**It cost 1.8 seconds of query time.** The design's one genuinely unknown quantity — the handoff:
*"no document on the record states how many artists the full pair table names"* — is a
distinct-artist count over two tables that already existed and had just been sha-verified. Figures
in the README.

**The nesting holds exactly: 0 members of `U`(10) are absent from `U`(3).** So the union of all
nine populations is `U`(3) ∪ `V` ∪ `P` — one set computation rather than nine — and the whole
lattice's population column nests. Re-checked for all three threshold pairs in task 3, all zero.

**Recorded as a limit, not discovered later:** these are **table-level** populations. §2.1 defines
`U` as the artists the table names *"after the standard drop lists, after the largest-component
prune"*, and the prune needs a build. A table-level count is therefore an **upper bound** on the
built node count — the conservative direction for a feasibility gate, since it over-estimates what
a census would cost.

## Task 3 — stage 1 proper: nine cells, and the `LBA-G3` read

**Scripts:** `stage1_derive_t7.py` (the one table that did not exist) and `stage1_counts.py`.
**Output:** `T7.manifest.json`, `counts.json`. Figures in the README.

**The threshold-7 table.** Derived by the wrapper precedent `LBD-AM5-2` established: the wrapper
**imports `lbd_derive` and extends its `ARMS` table** with one entry, so `derive_sql` runs
byte-identical to the SQL that derived `LBD-A0`–`LBD-A3` and `LBD-A5`. Both script sha256s are in
its manifest. **Named `T7`, never `A7`** — `LBA-A7` is threshold 10 over `U`, and a bare `A7` is
already Track 2's; `CLAUDE.md`'s rule that no two load-bearing objects share an identifier applies
to a name a session mints mid-flight exactly as `LBA-AM1`'s own boxed warning records.

**The instrument's green check passed before any cell was read.** `LBA-A1` and `LBA-A3` are
`LBD-A0V` and `LBD-A5V`, whose emitted pair counts, payload counts, neighbour rows and
absent-from-table counts are owned by the served-population README §2 and §3. The script
reproduces **all eight figures exactly** and refuses to write its output otherwise. A disagreement
would have been an instrument defect caught before a result, which is the point; it is a green
check and not a criterion.

**`LBA-G3` fires.** *Plain sentence, §5: working out which artists are unplayable would take too
long.* Its bar is 6 hours and `LBA-AM1`'s finding `LBA-AM1-A11` moved the read to stage 1 precisely
so it could not be discovered six hours into a pass. Projection method, both variants in the README:
a two-point fit over the two committed offline censuses (each records its own elapsed seconds and
its own count of freshly evaluated artists, so floor and marginal rate are solved rather than
assumed), plus a single-point sensitivity from the 2026-08-09 pass alone. **Both are multiples of
the bar.** Consequence, per §5: *the pass is not started*, `LBA-M4`'s class share for the uncovered
part is **estimated** and labelled as such, and the report says which arms carry an estimated class
rather than a measured one.

**The gap is entirely a `U`-row cost, and that is the decision-relevant shape of the result.**
Every artist in `V` and in `P` is already in the coverage store — the per-arm uncovered count is
**0 for all six `V` and `P` arms**. The census cost `LBA-G3` refuses is created by the three `U`
arms alone.

⚠ **This does not make the `V` and `P` arms' class shares *measured* in `LBA-M4`'s sense.** With
the pass not started, nothing is freshly evaluated, so **every verdict those six arms would read is
a carried one**, from the 2026-08-05 and 2026-08-09 censuses against **earlier MusicBrainz
snapshots than the pinned `20260905-002519` one**. `LBA-M4`'s own ⚠ requires the split by verdict
source and reserves the word *exact* for the fresh share; after this read there is no fresh share
at all. Named here so stage 3 does not discover it.

**The coverage store was read and not written.** sha256 identical before and after
(`counts.json`'s `coverage_store` block records both). The handoff flags it as active data that the
census scripts read **and** write; this session runs no census.

## Task 4 — `LBA-G2`'s first projection: the text does **not** settle it, so `LBA-AM2`

**Step 3 of the instruction, taken before the instrument it governs was written.**

**Three committed passages cannot all be acted on**, and with stage 1's counts in hand a fourth
conflict appears that was invisible without them:

- §3 `LBA-D8` stage 1 says *"both `LBA-G2` and `LBA-G3` read off it"*, and §7's `LBA-R0` gives the
  run state `derived`.
- §5's firing clause projects *"from a fit over every build already instrumented in **this
  stage**"* — stage 2 — and §10 says flatly *"`LBA-G2` cannot be evaluated until stage 2 adds it."*
- **§3's stage-2 order (`A1`, `A4`, `A7`, `A2`, …) is not §5's ascending-archive-neighbour-row
  order.** Under §3's order the second cell built is `LBA-A7`, about twice the first built cell's
  archive — a 2× extrapolation from a **single** point, which cannot even define a fit with an
  intercept. §5's ordering rule exists to prevent exactly that.

**`LBA-AM2` is written into §11**, resolving it: `LBA-G2` is read **progressively during stage 2**
and stage 1 supplies only the x-axis; the **first build is unevaluable and proceeds
unconditionally** (the gate is *silent*, not permissive); stage 2 builds in **ascending row
order**; and the fit rule is fixed now — 0 points silent, 1 point proportional-through-the-origin
and labelled, 2+ least-squares with a free intercept. **The 24 GB bar is unchanged and nothing is
reduced.**

**Two things make the resolution cheap rather than a trade.** The first built cell is `LBA-A2`,
whose archive is **between** the two archives `LBD-AM5` already built successfully on this machine
— so the unguarded first build is an interpolation in archive size, not a leap. And `LBA-D8`'s
own rationale is *improved* on, not sacrificed: it was written as though the control had to be
built, but `LBA-A1` and `LBA-A3` are **reused** and both sit on the `V` row, so under ascending
order **the complete `V` row exists after the first build**, and the `P` row — which carries the
only two one-column threshold reads `LBA-AM1-A9` admits — completes earlier than under §3's order.

> ### ⚠ `LBA-AM2` cannot claim `LBA-AM1`'s position, and says so in its own text
>
> `LBA-AM1` could say *"nothing had run"*. **This one cannot.** Stage 1 has run, and the author
> knew every cell's archive-neighbour-row count — which is `LBA-G2`'s x-axis — when writing it.
> What does not exist is the **y-axis**: no build, no peak RSS, no projection for any arm. So it
> spends none of `LBA-G2`'s commit-before-results property, and it is **not** written in ignorance
> of the cells' sizes. Both halves are stated in the amendment rather than left for a reader to
> work out.

## Task 5 — `framework_rss`, and two instrument defects that each returned a plausible number

**Script:** `stage1_framework_rss.py`. **Output:** `framework_rss.json`. Figures in the README §4.

§4 records this term as never measured in this project and `LBA-G1`(a) as unevaluable without it.
**Method determined from the shipped app, not chosen**: `build_default_app` (`app.py:330`) does
four things that cost memory, and all four are measured additively.

**The first two versions were wrong, and both looked right.** This is the project's characteristic
failure — confident output from an instrument nobody made go red — so both are recorded rather
than quietly fixed.

1. **Three processes, each importing `artistpath_api.app`.** Checked from source afterwards: that
   module is the **only** one pulling FastAPI, starlette, pydantic and httpx; `artifact_source`,
   `config`, `graph_store`, `search` and `clips` pull none of it. So the framework was loaded in
   the `store` baseline too and **cancelled in the subtraction**. Reported `framework_rss` = 0.1
   MiB, with one **negative** component — the negative number is the only reason it was caught.
2. **`PeakWorkingSetSize` differenced across processes.** The peak is a whole-process high-water
   mark. `load_graph` reads the entire artifact into `bytes` and parses it, so its transient peak
   sits above its steady state, and the framework imported afterwards reuses freed pages and never
   exceeds that mark. The framework was **invisible underneath the graph's peak**. Reported 0.4 MiB
   for a process that demonstrably loads 384 framework modules — plausible-looking, and wrong.

**The fix for both: one process, framework imported first, and difference the *current* working
set at stage boundaries.** The kernel's peak is still recorded, but reported and never differenced.

**A limit of the measurement, named rather than discovered later.** §4 defines `framework_rss` as a
single figure on the served artifact, but `ArtistSearch.__init__` holds one normalised Python
string per artist (`search.py:27`), so **the term is not population-independent**. The README gives
the decomposition — a constant part and a per-artist part — because applying the single figure to a
larger arm understates exactly the arms `LBA-G1`(a) exists to test. The per-artist term is also the
**noisiest** quantity measured here and is an order of magnitude, not a rate.

## Task 6 — the peak-RSS instrument for stage 2

**Script:** `stage2_build_instrument.py`, a **forward copy** in this session's directory. **No
shipped code under `builder/src` is touched** and `lbv_build.py` is not modified — its outputs are
a frozen record and the 2026-08-09 precedent refuses re-running a frozen script in place.

It mirrors `lbv_build.run_build`'s seam and adds the peak. Three design points worth the record:

- **It refuses a second call in one process.** `PeakWorkingSetSize` never falls, so two builds in
  one process contaminate the second — and `lbv_build.py` ran two per process, which was harmless
  only because it recorded no memory. Stage 2 runs **one build per process**, enforced rather than
  remembered.
- **The x-axis comes from the emitter's own `counts.neighbour_rows_written`**, so the unit cannot
  be re-derived wrongly at the call site. Archive neighbour rows, pre-cap, two per pair.
- **`project_peak_rss` implements `LBA-AM2`(d)** so the fit rule is code, fixed before stage 2 has
  results.

**Shown to go red before any figure from it is believed** (`--self-test`, passing): a deliberately
allocated 256 MiB is seen as 256.0 MiB; the double-call guard fires; and the projection is
exercised **both** under the bar and over it.

⚠ **The self-test's own first version was wrong and failed the instrument for being correct** — it
asserted that a fit of 4 GiB at 10M rows and 7 GiB at 20M would fire at 52.3M rows, when that line
gives 16.68 GiB, comfortably under 24 GB. The expectation is now the arithmetic, and a separate
steeper case supplies the red. Recorded because it is the same shape as the two defects in task 5:
a test can be as wrong as the thing it tests.

## Housekeeping

- **Snyk `snyk_code_scan` over the new analysis directory: 0 issues.** No fix, no rescan needed.
- **A path-scoped rule loaded**, `.claude/rules/plans.md`, when this session opened the
  pre-registration. It carries no guidance of its own and says so. **Recorded because that is
  exactly the observation the `DLS-T1` probe was set up to make** — it fires on opening a spec, and
  it fired.

---

## `closeout` — full ritual

| item | result |
|---|---|
| **A1** distil the log | this document, appended **per task** rather than at the end |
| **A2** handoff note | [`2026-09-14-HANDOFF-lbd-s4-stage1.md`](2026-09-14-HANDOFF-lbd-s4-stage1.md); the predecessor's role line demoted and the map row with it, so the chain reads **forwards** |
| **A2-next** `NEXT.md` | rewritten wholesale; the outgoing block and 22 discharged deferral rows demoted to `NEXT-ARCHIVE.md`. **Git state deliberately absent** — branch and PR named as addresses, the owner's actions as an ordered sequence |
| **A3** deferrals | two conditions re-tested against reality rather than confirmed to exist; **both had come due** — see below |
| **A4** default-flip | **inapplicable** — no config knob added, no default touched, no shipped code changed |
| **A5** processes | **no listener on 8000 or 5173**; nothing to stop and nothing left running. C1 queued nothing, so no server is needed |
| **B1** docs-lint + `doc-auditor` | lint: **2 hard failures, both my own new documents unclassified in the map; fixed, re-run passes.** Auditor: **1 MEDIUM, and a genuine defect of omission** — the stage-1 README is cited by three documents as the figures owner and had **no map row**. The lint could not see it: its `DOCS` root is `docs/`, and the README is under `builder/analysis/`. Fixed. Everything else the auditor checked came back clean, including the two claims most worth doubting — that no document asserts an `LBA-G2` result, and that `LBA-AM2` states its own position honestly |
| **B2** reachability | six new scripts, **0 inbound imports each** — correct for frozen research code, which is run and not imported. **One genuine orphan, deliberately:** `stage2_build_instrument.py` exists to be imported by a stage-2 wrapper that does not exist yet. **Unfinished, not abandoned**, and the handoff names who wires it in |
| **B3** vacuous tests | the only new test is the build instrument's self-test, and it was **shown going red before it was believed** — including once genuinely, when its own expectation was wrong |
| **B4** prose vs code | **three corrections, all in my own output.** `stage1_counts.py` claimed all three tables were sha-**verified** when the threshold-7 table has no pin to check against; it claimed **six** green-check figures when it compares **eight**; and its per-table print said *"verified"* for all three. All three were true-sounding and wrong. Also dropped `verify.json`, a strict subset of `verify_T.json` that the README did not list |
| **B5** stale descriptions | **no `.claude/` or `memory/` file changed.** No figure this work produced is restated outside the stage-1 README, and the README restates none owned elsewhere — the auditor checked this independently |
| **B6** budgets | `NEXT.md` **465 → 435** (budget 250), `docs/README.md` **564 → 567** (budget 400), `TEST-QUEUE.md` **70** (budget 70, at it). See below |
| **C1** use the app | **nothing written in `TEST-QUEUE.md`, and that is the discharge.** This work changed nothing a listener or the owner can press: no shipped code, no default, no deploy |
| **D1** clean tree | clean after the final commit |
| **D2** fixtures | **inapplicable** — no artifact changed and no fixture is affected |
| **D3** provenance | one uncommittable artifact produced, `T7.parquet`, sha256 and row count recorded in the README §0 and the handoff's artifacts table |
| **D4** suites | **builder 290 passed, api 295 passed, frontend 188 passed across 29 files.** Run, not asserted from memory. No shipped code changed, so green was expected — it is evidence that nothing was disturbed, not that anything was proved |
| **D5** PR | opened as a draft against `main` |
| **D6** standing context layer | **unconditional 50,977 characters, conditional 2,726 lines — both EXACTLY unchanged** from the 2026-09-13 figures. This session added no rule, no memory, no skill or agent description |
| **D7** retire | the `/rename` line is in the closing message |

### A3 — the two conditions that had come due

**Both were open items whose conditions had already been satisfied, which is the failure mode A3
names: a satisfied condition nobody reads is indistinguishable from an open one.**

1. **The line-budget row** — condition *"when no second session is live in the tree"*. The
   `SessionStart` repo-state report says no other worktrees; §C found no uncommitted work this
   session did not create. **First time the condition has held.** Its `NEXT.md` half is discharged
   here: the outgoing status block and 22 discharged deferral rows are demoted. Its
   `docs/README.md` half is **`DLS-` item 5's**, not this session's, and stays open.
2. **The `DLS-T1` read** — its row says to record new observations in the findings' §6b, not in
   `NEXT.md`. **Recorded**, as row 6 plus a new caveat `DLS-T1-X7`, from this session's own
   `instructions-loaded.jsonl` rather than from recollection.

⚠ **The observation cuts against the instrument's stated exclusion rule, and it is recorded that
way rather than as a clean hit.** This session opened the pre-registration **exclusively through
Bash**, never once through the `Read` tool, and `plans.md` loaded anyway. That is the second such
row, so `DLS-T1-X1`'s premise — that a Bash-reading session cannot be a qualifying session — is now
contradicted twice. **What it does not settle is the timing:** the load fired ~35 minutes after the
first Bash read, well into the writing phase, so what the trigger keys on is still unknown. Two
loads whose trigger nobody can name are weaker evidence than one whose trigger is known, and the
caveat says so.

### B6 — over budget, reported rather than fixed by compression

`NEXT.md` is **435 lines against a 250-line budget** after the demotions, and the reason is not the
status block: it is the registries. **16 table rows exceed the ~600-character per-row budget**, and
the tables total ~29,200 characters. Those rows are *reasoning* — why a thing was closed, what was
measured, what a future session must not re-propose — attached to documents whose job is to say
*what to do*.

**Not fixed here, deliberately.** The legitimate moves were taken (demote the status block, demote
the discharged rows). The remaining excess would have to come from compressing live prose, which
`B6-budget` and D6 both forbid, or from moving 16 rows' reasoning into findings documents and
leaving pointers — which is a wholesale table rewrite of the file concurrent sessions collide on,
and is `DLS-` item 5's shape. **Recorded as a measurement, with the mechanism named, for whoever
picks that item up.**

`docs/README.md` went **564 → 567**: one row added for the stage-1 README (the auditor's finding),
two for the new handoff and log, one demotion edited in place. It was already 164 lines over budget
before this work and is `DLS-` item 5's to fix.
