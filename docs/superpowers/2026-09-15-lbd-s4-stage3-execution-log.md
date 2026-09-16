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
