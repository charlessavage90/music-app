# `LBD-S4` stage 3 — execution log (`LBA-`)

**Role: ACTIVE — the retained reasoning log for `LBA-D8` stage 3.** It owns **no figures**:
those are [`builder/analysis/2026-09-14-lbd-s4-stage3/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage3/README.md)'s.
Stage 1's and stage 2's are their own READMEs' and are cited, never restated.

**Governing:** [`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), including §11's `LBA-AM1`, `LBA-AM2` and this stage's `LBA-AM3`. Where these notes and
it disagree, **it governs and this log is wrong**.

**Appended per task, not at closeout** — `CLAUDE.md`'s rule for what makes a handoff cheap.
Decisions and reasoning, not narration.

**Scope, from the owner, 2026-09-15:** `LBA-M2`, `M3`, `M4`, `M5` over the eight sized arms; the
§7 reads that state licenses; the go/no-go report. **No build, no census, no fame fetch, no
listen, no shipped code.** `LBA-A9` stays unbuilt and unread at map level.

---

## Task 0 — the scope check, before anything ran

`session-start`'s check re-run against the owner's eight steps at his instruction.

**It does not fire in the stop-and-do-something-cheaper sense, and that is recorded as a result
rather than skipped as a formality.** Stage 2's six builds are merged; every remaining
measurement is arithmetic over artifacts already on disk. There is no apparatus being built here
to answer a question a cruder test would settle.

**Three things it did yield.**

1. **A weighting the report must carry up front.** `LBA-R1` handed the decision to
   `LBA-M2`/`M3`/`M4`. Two have since lost force for structural reasons: `LBA-M5` cannot
   discriminate between arms at all (`LBA-AM1-O2`), and `LBA-M4`'s authority is **uneven** — on
   `LBA-A1`–`A6` every population member carries a verdict (stage 1 §2 measured zero uncovered),
   while on `LBA-A7`/`A8` most of the population has none, and the coverage store's own rule is
   *"absence of a field means UNKNOWN, never false."* **The decision concentrates on `LBA-M2`**,
   plus `LBA-M3`'s two admissible cells and `LBA-M4` on the `P` row. **Reporting, not a proposal:
   steps 4 and 5 run as specified — `LBA-D8` bars reducing the design.**
2. **An ordering adopted inside `LBA-M2`:** the `V`-row arm-to-arm comparison runs **first**. It
   is the only comparison free of *both* population movement and the `LBA-X4` data bundle, and
   `LBA-R4-V` names it as the `V` row's only threshold evidence. Banks the cleanest slice first,
   which matters under the owner's hand-off-at-the-last-completed-step instruction.
3. **A claims-check correction to task 1** — see task 1.

**Recorded as the owner's, not adjudicated here:** his step 6 asks for what the estimated
`LBA-M4` would say *if read as measured*. §7 bars `LBA-R8`/`R9` without the *censused* state, so
this is a change of practice against a committed document and goes into `LBA-AM3` with his
instruction and its date — **never as a silent report**.

---

## Task 1 — the pins, verified before anything was read (`LBA-D9`)

**Result: 20 checks, all match. Nothing was refused.** Figures and digests are the stage-3
README's §0; nothing is restated here.

**The owner's step 1 named 8 artifact digests. It needed 20, and the gap was not cosmetic.**
Three families of object were being conflated under one name:

- **the eight BARE artifacts** (`LBA-<arm>-bare.bin`) — what `LBA-M1` sized and what stage 3
  decodes. Digests in `s4_sizing.json`'s `artifact_sha256`, cross-checked against
  `s4_bare_copy_LBA-<arm>.json`'s `bare_sha256`.
- **the six BUILT artifacts** (`LBA-<arm>.bin`, arms `A2` and `A4`–`A8`) — digests in
  `s4_build_<arm>.json`'s `artifact.sha256`. **Different files with different digests**, e.g.
  `LBA-A1`'s bare copy is `e566ceaf…` while nothing named `LBA-A1.bin` exists at all.
- **`LBA-A1` and `LBA-A3` have no build record**, because `LBA-D9` reused rather than built them;
  their built identity is `LBD-A0V.bin` / `LBD-A5V.bin`. The script asserts that linkage from
  each bare copy's `source_sha256` rather than leaving it implicit.

**Verifying only the eight named would have left the six built artifacts unchecked** while
`LBA-M2` decoded them. Recorded because the correction is the same shape as the unit slip this
track has already refused a build for: a plausible name covering two objects.

**Two instruments, not one.**

1. **Inputs — stage 1's frozen `stage1_verify.py`, re-run unedited**, output
   `_pins/stage3_verify_inputs.json`. **All 13 pins match**; `T_A4.parquet` **absent from every
   searched path**, which `LBA-D1` wants and which is a stronger exclusion guarantee than a
   match. **`T.parquet` deliberately skipped** via the script's own `--skip-large`: stage 3
   derives nothing and never opens it, so hashing 21 GB would buy nothing. Stated rather than
   silently omitted.
2. **Artifacts — `s3_verify_artifacts.py`, new**, output `_pins/stage3_verify_artifacts.json`.
   All 14 match, and **`LBA-A9`'s stop record is asserted clean**: no `artifact` key, status
   still *unbuilt for a resource reason*. That assertion is positive rather than incidental,
   because a stop record quietly gaining an artifact path is precisely the shape that would put
   an unbuilt cell into a map-level read, which §2.6 bars.

**The new instrument was shown RED on the path it is actually used on, before its green was
believed.** `--self-test` drives `check()` itself — a real artifact against a wrong digest
(MISMATCH), a missing file (MISSING), the same artifact against its true digest (OK), and a
forged `LBA-A9` record carrying an artifact (refused). **This is the stage-1 correction applied
rather than cited:** `stage2_build_instrument.py` was pronounced self-tested having never run a
build to completion, because its only call hit a guard that raised before the code under test.
*"Shown to go red" is necessary and not sufficient — it has to go red on the path the instrument
is used on.* The module was patched and then the real verification **re-run**, so the recorded
`script_sha256` is the final module's and not a superseded one.

**Deferred to the end of the script-writing, not forgotten:** the Snyk scan over
`builder/analysis/2026-09-14-lbd-s4-stage3/`, run once when the stage's scripts exist rather
than once per file.

---

## Task 2 — `LBA-AM3`, committed before `LBA-M4` runs

**Three items, none of which moves a bar's value.** The amendment's own text is the record;
this entry is the reasoning that produced it and is not a summary of it.

**Why it had to be committed before task 4 rather than written alongside the report.** §11's
rule is that a bar is never edited and a change of practice arrives dated, with the commit
timestamp as the evidence that it preceded the result. Two of the three items would otherwise
have been resolved by a session **with `LBA-M4`'s numbers in hand** — which is the one moment a
pre-registration exists to take a decision away from. `LBA-M2` and `LBA-M3` depend on none of it,
so nothing was blocked by writing it first.

**The honest-position block was the hard part to write, and it is not `LBA-AM2`'s.** `LBA-AM1`
could say *nothing had run*; `LBA-AM2` could say *the x-axis exists, the y-axis does not*. This
one has two completed stages behind it, so the block enumerates exactly what its author could
already see — every arm's size, boot memory and d0 cost; every arm's coverage-store absence
count; the prune retention on two `U` cells — and states that **no class share, retention figure,
supply share or provenance mix existed**, which is every quantity the three rules govern.

**`LBA-AM3-1`, and it is the item with consequences beyond bookkeeping.** *censused* is
unattainable now that `LBA-G3` has fired, so `LBA-R8` and `LBA-R9` can never be reached within
`LBD-S4` as designed. **The half worth stating plainly: `LBA-R9` is the owner's own exit read** —
the row that records stopping as a complete outcome rather than an abandonment — and the design
cannot hand it to him licensed. His instruction to report the estimated `LBA-M4` as a labelled
sensitivity is recorded **as his, quoted, and dated**, with an explicit statement that it makes
no read reachable. The distinction between *the owner asked for a sensitivity he can weigh* and
*a session took a barred read* is invisible in the output and survives only in the record, which
is the whole reason it is an amendment and not a formatting choice.

**`LBA-AM3-2` — the confound is measurable, so it is measured rather than argued about.**
`LBA-G4` wants both class shares from one pass against one dump; with no pass they come from two
censuses against two earlier snapshots. The *same arm* half of `LBA-AM1-A5`'s fix survives
untouched. The failure mode is specific: if the added-beyond-`V` and kept-from-`V` subsets draw
from the two censuses in **different proportions**, a dump column re-enters a comparison that was
deliberately made one column wide. `d2_src` makes that per-artist, so the mix is reported beside
the gate.

**It needed its own effect size and nearly did not get one.** `CLAUDE.md`: a trigger without one
cannot tell the finding it was written for from noise. The first draft said the gate would be
withheld *"if the mix is skewed"*, which is a judgement call handed to a session holding the
numbers — the same defect `LBA-AM1-A9` was written to remove. **Fixed at 10 percentage points**,
chosen as `LBA-G4`'s own bar in `LBA-G4`'s own units: a provenance difference big enough to
account for the gate's firing threshold is big enough to disqualify the comparison. Stated as a
choice, not a measurement. The disqualifier can only ever **withhold** a gate result, never
produce one, so it cannot admit an arm.

**`LBA-AM3-3` — "estimated on every arm" was flattening two different situations.** `LBA-M4`'s
own ⚠ and stage 1 §3 together establish that no arm has a fresh verdict. Neither says that six
arms have a **complete** carried population while two have most of theirs absent from the store
entirely, where the store's rule is *"absence of a field means UNKNOWN, never false."* The
difference falls on exactly the arms `LBA-M4` exists to size, so a coverage column is now
required per arm and cross-row comparison of class shares is barred.

**One accuracy fix made in passing rather than listed.** The header's identifier register still
read *"`LBA-AM1` (the amendment register's first entry)"* — true when written, and by omission
wrong once `LBA-AM2` existed. It now names all three entries and the sub-identifiers minted
inside them. This is the defect class `CLAUDE.md` describes as unfindable by grep, because the
fault is an absence; `LBA-AM2` did not update it and the omission survived a `doc-auditor` pass.

**Banked for the `DLS-T1` read, which `NEXT.md`'s deferral says must consume dated
observations.** Editing
`docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md` in this session caused
`.claude/rules/plans.md` to arrive in context **without being asked for**, mid-task, immediately
after the write. **Observation dated 2026-09-15, session `lbd-s4-stage3`: the path-scoped rule
fired on a spec edit.** Recorded here rather than in `NEXT.md` so the read consumes it from a
dated log; it is one qualifying session, not the three the condition needs.

---

## Task 3 — the scope check, re-run against the owner's eight steps

**Task 0 ran this same check against these same eight steps, in the previous session.** This is a
second, independent run by a session that read the pre-registration cold — his instruction — and
**it reaches the same verdict: it does not fire in the stop-and-do-something-cheaper sense.** That
is recorded as a result rather than skipped, and the agreement between two cold runs is worth more
than either alone. What is new below is item 3; items 1 and 2 restate task 0's conclusions because
this run reached them independently, which is the only reason to write them twice.

**Why not.** The check asks: the task ends in a number — name the cheapest experiment that could
change the decision, and propose running it first. Every one of the eight steps is arithmetic over
artifacts already on disk; there is no apparatus being built here whose question a cruder test
would settle. The expensive thing in this track — a build, a census pass, a fame fetch, a listen —
is barred by the owner's scope and by `LBA-D3`/`LBA-D5`/`LBA-G3`, and none of them is the cheap
alternative to anything being done.

**The one candidate that is genuinely cheaper and genuinely decisive, examined and set aside.**
The stage-2 handoff proposes measuring d0 **on the actual container** rather than converting by
the Gate 2→3 review's 2.5–3.5× multiplier, which was taken on the retired 75k artifact. It is
cheap and it is the right instrument. It is **not** the cheapest experiment that changes *this*
decision, because `LBA-G1` fired on nothing and `LBA-R1` already reads *size is not what decides
this*: a container reading could only move an arm from "fits" to "needs hosting work", which is
`LBA-R2`'s territory and mutually exclusive with a read already taken. It stays where it is — a
deferral row in `NEXT.md` with its own condition — and this session does not build it.

**Three things the check did yield.**

1. **An ordering inside step 2, already adopted at task 0 and re-confirmed here:** the `V`-row
   arm-to-arm comparison runs first. It is the cheapest decisive slice of the decision-carrying
   measurement and the only one free of both population movement and the `LBA-X4` bundle.
2. **A proportion observation about step 4, reported and not acted on.** `LBA-M4` is estimated on
   every arm, its two census-dependent reads are unreachable (`LBA-AM3-1`), and `LBA-AM1-O2`
   already removed `LBA-M5` from arm discrimination — so a session optimising for decision value
   alone would shrink both. **`LBA-D8` bars that**: the executing session does not have the
   authority to reduce the design, and steps 4 and 5 run as specified. Recorded because noticing
   it and staying inside the rule is the thing worth having on the record.
3. **A claims-check correction to step 8.** It names *"the pre-registration's §12 status marker"*.
   **The `LBA-` document has no §12** — its last section is §11, the amendment register, and §12
   belongs to the **`LBD-`** pre-registration (whose §10 and §12 this document's header cites).
   The status marker goes in **§11**, following the `LBD-` §12 convention of a marker beside the
   register rather than a new section. Resolved here rather than at the moment of writing it.

---

## Task 4 (his step 1) — the pins, re-verified by THIS session before anything was read

**Result: 27 checks across two instruments, all match. Nothing was refused.** Digests are the
stage-3 README's §0; nothing is restated here.

**Re-run rather than inherited, and that is the point.** Task 1 verified these yesterday. A
session that reads a conclusion from an artifact it has not itself checked is relying on another
session's memory of a hash, and `CLAUDE.md`'s rule is that a conclusion drawn from the wrong
artifact looks exactly like a correct one. Both instruments were re-run unedited; neither was
modified, so the recorded `script_sha256`s are unchanged from task 1's.

- **Inputs** — stage 1's frozen `stage1_verify.py`, `--skip-large`: **13 pins match**, and
  `T_A4.parquet` **absent from every searched path** (`LBA-D1`). `T.parquet` is skipped
  deliberately: stage 3 derives nothing and never opens it.
- **Artifacts** — `s3_verify_artifacts.py`: **14 match** — eight bare, six built — and
  **`LBA-A9`'s stop record asserted clean**, no `artifact` key, status still *unbuilt for a
  resource reason*.

**His step 1 named 20 objects and both scripts together check 27.** The 20 are exactly his list
(8 bare + 6 built + the served map + 3 CXR strata + 2 population files); the extra 7 are the two
derived tables, the two reused artifacts under their `LBD-` names, the two archive manifests and
the extended-crawl graph, which stage 1's instrument checks as one unit and which there is no
reason to skip.

**One thing checked because it would have been easy to get wrong, and it was already right.**
Every `S4-` archive's path token reads `…threshold_10…` **regardless of the arm's actual
threshold** — it is ListenBrainz's canonical algorithm string, which is drop-list lineage rather
than this arm's parameters. Stage 2 anticipated this: each manifest carries the key
`algorithm_token_is_drop_list_lineage_not_parameters` holding that string verbatim, and the
arm's real parameters sit in `parameters` (`threshold: 7` for `LBA-A2`) with `lba_arm` naming the
cell. **No defect, and no correction is owed** — recorded only so a later reader who sees the
path token does not re-derive the alarm.

---

## Task 5 (his step 2) — `LBA-M2`

**Figures are the stage-3 README's §2 and are not restated here.** This entry is what was decided
and what the numbers cost to believe.

**Two instruments were written, `s3_common.py` and `s3_m2.py`, and neither touches shipped code.**
`GraphStore` is imported from `api/src` rather than re-implemented: the APG1 format is the
contract between the two packages and a third parser here would be a third thing to keep in
lockstep by hand. Every artifact load re-checks its sha256 against task 4's output and refuses on
a mismatch, so no statistic in this stage can be computed from an artifact the stage has not
pinned.

**Decoded BARE, not built, and this is stage 2's choice applied to a second half.** A census build
carries four of the five additive metadata keys and the two reused artifacts carry all five, so
decoding the built files would read some arms through metadata others lack. Stage 2 §3a made
exactly this call for the memory half and said why; the structural half inherits it. **No bar
moves either way** — metadata is not in any `LBA-M2` statistic — which is precisely why it was
worth making the same choice rather than a different one for no reason.

**The self-test drives `compare()` itself, RED and GREEN, on the path the measurement uses.** A
hand-built pair of stores where every expected value is arithmetic: an arm that keeps one of three
served neighbours and gains an unserved one (retention 1/3, the gate fires, `R_avail` still 1.0
because the other two were never available); an identical arm (nothing fires, every share at its
floor); and a 7-against-3 length pair at retention 1.0 that the forced-share null model sees.
**That third case is the reason the statistic is retention and not Jaccard, asserted rather than
described.** This is stage 1's correction applied rather than cited — *"shown to go red" has to be
red on the path the instrument is actually used on.*

**The instrument's green check, and it is a frozen record rather than another figure from this
session.** On the three `V`-row arms, this session's *absent from the arm's own table* count plus
the emitter's no-identity-row skip reproduces **stage 1 §1's committed absent counts exactly, all
three**. The `P`-row and `U`-row arms have no such check because stage 1 counted absence over `P`
and over the arm's own table, not over `V`.

**A third absent cause was separated out rather than folded into one of §4's two.** The emitter
skips a population member with no identity row: five artists on every `V` and `P` arm, none on a
`U` arm. They **do** have pairs in the table, so filing them under *"no pair at all"* would have
been false — and it is exactly those five that reconcile this session's count with stage 1's.

**`b_out` is computed in the arm's own id space, and the first draft had it wrong.** It counts the
arm's neighbours that are not artists the app serves today. Computing it as *"neighbours the base
map does not contain"* is correct when the base **is** the served map and wrong for every
arm-to-arm comparison, where a neighbour absent from the baseline arm may still be served. Caught
before any run; recorded because the wrong version would have produced a plausible number on the
comparison that matters least and a silently wrong one on the comparison `LBA-AM1-A7` added.

**One result is worth naming here because it changes how the rest of the stage reads**, and it is
reported rather than concluded: **the arm-to-arm comparisons are very nearly pure addition.**
Mean retention within every population row is above 0.998 and the gated statistic fires on
essentially nobody. That is stage 1 §1b's threshold nesting surviving the cap and the prune, which
no document had established — nesting was proved at the **table** level, and whether a degree
ceiling of 50 would undo it at the **map** level was open. It did not, because the median degree
on every arm is well under the ceiling. **Consequence for the reads: within a fixed population the
strength bar is close to a one-way addition**, so a difference between two arms measured against
the served map is not a difference in *who is kept*.

⚠ **`LBA-X4` and `LBA-X5` travel with every served-map figure and with none of the arm-to-arm
ones** — which is the whole point of `LBA-AM1-A7` and is asserted in the output JSON rather than
left to the report to remember.

**One descriptive observation, offered as an observation and not a finding.** The 92 served
artists with a null `fame_lb` — the "unknown" band — are absent from **every** arm bar one
artist. No listens means no listener count and no co-listen pairs, so the two absences are the
same absence. It is 0.16 % of `V` and nothing rests on it.

---

## Task 6 (his step 3) — `LBA-M3`

**Figures are the stage-3 README's §3.** This entry is the reasoning.

**The second control did not exist and had to be taken, and that is the only new computation in
this task.** `LBD-G2`'s 1-point bar is admissible **only** with both controls reported: the
pre-existing set as the within-arm reference, and **the arm's own table-level figure**. The
table-level figure existed for threshold 10 (`LBD-A0`, owned by the similarity README §6) and for
**neither** threshold 7 nor threshold 3 — `A5.parquet` was derived for the served-population work
and its `LBD-C2a` read was never taken, and `T7.parquet` was derived at stage 1. Without them the
bar would have been the **10-point** one, and both `P`-row reads would have been unreadable.

**Taken by running the frozen `lbd_reads.py --mode c2a` UNEDITED on each of the three derived
tables**, via `uv run --with duckdb`, which is that script's own documented invocation. No module
was edited and nothing was written under `builder/src`.

**The instrument's green check is against a frozen record.** Re-running it on `A0.parquet`
reproduces the similarity README §6's four committed shares **exactly** — added, residual,
complement and pre-existing. That is a figure nobody in this session could have tuned toward: it
was committed on 2026-09-08.

**A property of the second control worth stating before anyone reads it as arm evidence: it is a
property of the THRESHOLD ALONE.** All three arms at a given threshold derive from one table, so
the three population rules share a table-level figure and **it cannot distinguish them.** It is a
control on the threshold column and on nothing else, which is exactly the column the only two
admissible one-column reads sit in.

**The `V` row's 1.0 is computed, not asserted.** §4 argues from construction that no member of the
added set can be in a `V` arm, so the statistic must be 1.0 and every threshold difference on that
row identically zero. The script computes it anyway and got 1.0000 on all three. **If the
arithmetic had disagreed, the construction argument would have been the thing that was wrong** —
which is the only reason to spend the cycles.

**The fourth stratum is EMPTY on the `V` row, and that is `LBA-AM1-A10` seen from the other side.**
`nodes(arm) − V` is empty for `LBA-A1`–`A3` because those arms' population *is* `V`. It is printed
as empty rather than as a share of nothing, the same distinction `LBA-AM1-A5` made for `LBA-G4`'s
`n/a`.

**The fourth stratum cannot be pinned in advance and so is pinned after the fact.** It is a
consequence of the arm (`LBA-X6`), so its membership is written out per arm and recorded by count
and by **sha256 over its sorted MBIDs** — this track's own convention for a gitignored set, and
the same form §2.1 uses for a population rule. The files live beside the artifacts and a fresh
clone has none of them; the checksum is their identity.

**What the reads are, stated without preferring anything.** Both `P`-row one-column deltas against
`LBA-A4` clear `LBD-G2`'s 1-point bar, with both controls reported. The `U`-row delta is computed
and is **not** a one-column attribution — `LBA-X6` travels with it. The `V` row is `n/a`. **No arm
is preferred here and no threshold is selected; `LBA-D2` reserves that to the owner.**

**One thing the controls do that a single figure would have hidden.** The within-arm control moves
with the threshold too — the pre-existing set's share improves as the bar loosens. The added set
moves **more**, by roughly a factor of three on both `P`-row comparisons. That ratio is what
separates *"this rule helps the artists the track exists to help"* from *"everything got denser"*,
and it is only visible because `LBD-G2` requires the control rather than recommending it.

---

## Task 7 (his step 4) — `LBA-M4`, and `LBA-AM3-2`'s disqualifier fires on every evaluable arm

**Figures are the stage-3 README's §4.** This entry is the reasoning, and one derivation that
changes what `LBA-G4` can mean in this stage.

**The store was read and not written, and that is evidenced rather than asserted.** Its sha256 is
recorded before and after and the script **refuses** if they differ. It is ACTIVE data — the
census scripts read it *and write back* — so "we did not touch it" is exactly the kind of claim
this project requires evidence for.

**Zero freshly evaluated artists on every arm, as stage 1 said there would be.** The split by
verdict source is computed and reported anyway, so the zero is **visible rather than inferred**.

**The within-class drop rates are read from the two committed payloads rather than transcribed**,
and reported as a **range, never averaged** — §4's rule, because they were taken on different
populations.

### `LBA-AM3-2`'s disqualifier fires on all five arms where `LBA-G4` is evaluable

**And it is worth being precise about what that does and does not mean.** The gate is **reported
unreadable** on `LBA-A4`–`A8`: only the two class shares stand, descriptively, with the
verdict-source mix beside them. It is `n/a` on the `V` row, where its subject is empty.

**The disqualifier's value was fixed on 2026-09-15 at ten percentage points, before any
provenance mix had been looked at** — the amendment says so and the commit timestamp is the
evidence. **The measured skew is between 51.7 and 71.3 points.** Nothing was tuned to reach that;
it is five to seven times the bar.

**The derivation that matters, and it is mine rather than an escalation: the skew is STRUCTURAL,
not an accident of these arms.** Every `kept-from-V` subset draws **0.0 %** of its verdicts from
the 2026-08-09 recensus — exactly zero, on all five arms — because the 2026-08-05 census covered
the 75,000-artist `ALG-B` population, which contains `V` entirely, and the recensus only evaluated
artists genuinely new to the store. The `added-beyond-V` subsets draw 51.7–71.3 % from it for the
mirror-image reason. **So under the two censuses that exist, an added-beyond-`V` subset and a
kept-from-`V` subset can NEVER have matching provenance.** `LBA-G4` as `LBA-AM1-A5` redefined it
is therefore **not readable at all in this stage** — and its root cause is the same one that put
`LBA-R8` and `LBA-R9` out of reach: `LBA-G3` fired, so there is no fresh pass to put both subsets
on one footing.

**What this does NOT license, stated because the temptation runs both ways.** The raw within-arm
deltas are **+0.78 to +0.83 points on the `P` row and +30.7 / +31.0 points on the `U` row**. The
disqualifier says those comparisons are **disqualified**, not that the `U`-row figure is wrong.
**Neither "the artists a `U` rule adds are much less playable" nor "they are fine" is licensed by
this stage**, and the report must not imply either. The confound is real and its size is
unmeasured.

**This is the clearest return the pre-registration discipline has paid in this stage.** Without
`LBA-AM3-2`, a session holding these numbers would have read `LBA-G4` as **firing decisively on
the `U` row** — a 31-point delta against a 10-point bar — and would have written it into the
record as a finding about population rules. A provenance difference of fifty to seventy points
could have produced it by itself.

### `LBA-AM3-3`'s coverage column, and what it bars

Coverage is **1.0000 on `LBA-A1`–`A6`** and **0.3547 / 0.2861 on `LBA-A7` / `LBA-A8`**. So the
`U`-row class share is measured on roughly a third of the population and extrapolated to the rest,
where the store's own rule is *"absence of a field means UNKNOWN, never false."* **The `U`-row
whole-population class share is about four times the `V`- and `P`-row ones, and `LBA-AM3-3` bars
comparing them as though both were measured on the same basis.** The report carries the coverage
column beside every figure, which is the bar rather than a courtesy.

---

## Task 8 (his step 5) — `LBA-M5`

**Figures are the stage-3 README's §5.** Nothing here was re-run or re-timed: parts 1 and 3 are
**cited** from the four documents that own them, part 2 is arithmetic over values read from
source, and part 4 is prose.

**`LBA-AM1-O2` is applied rather than noted.** Three of the four parts are identical across all
eight arms, so the only thing that varies is the fame fetch, and it is a deterministic function of
`LBA-M1`'s N. **This measurement is a cost statement about a candidate, not a comparison between
candidates**, and the report says so where it appears.

**One input the record does not contain, named rather than invented.** §4 fixes the fame estimate
as `⌈N / 1000⌉ × (0.2 s + one round trip)`. The batch size and the pause are read from source
(`fame.py:57`; the **builder's** `config.py`, not the API's). **The round trip is not exactly
recoverable**: the one measured fame run on the record took 78 s, and that log does not say which
population it covered. It was one of the two that session handled, so the per-batch cost is
**bracketed across both** — 0.66–0.88 s, giving a round trip of 0.46–0.68 s. This is `LBA-AM1`'s
own treatment of `framework_rss` applied again: **name the missing input, do not guess it.**

**The result makes `LBA-AM1-O2` concrete.** The fame fetch is a first-build cost of well under six
minutes on **every** arm including the largest, and the stage is resumable, so a refresh pays only
for artists with no record. **Nothing in `LBA-M5`'s own four parts separates the arms in a way a
decision could rest on.**

⚠ **The operating cost that does move with the population is not in `LBA-M5`'s arm table at all —
it is §6's step 6, the re-census**, whose projection is stage 1 §3's and is what `LBA-G3` fired
on. Recorded here because a reader comparing the fame column across arms and concluding *"a bigger
map is cheap to operate"* would have read the one part of the cost that does not scale and missed
the one that does.
