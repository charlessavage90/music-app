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

