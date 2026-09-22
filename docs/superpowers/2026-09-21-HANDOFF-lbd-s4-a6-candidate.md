# Handoff — the `LBA-A6` candidate is built and the use gate is the owner's, 2026-09-21

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-16-HANDOFF-lbd-s4-stage3.md`](2026-09-16-HANDOFF-lbd-s4-stage3.md) on next actions. It
does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam, not a mid-flight retirement.** Everything the owner asked for ran to its end. Nothing is
in flight, no background job, no dispatched subagent, no half-written directory.

**It owns no figures.** They are owned by
[`../../builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md`](../../builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md).
Reasoning is [`2026-09-21-lbd-s4-a6-adoption-execution-log.md`](2026-09-21-lbd-s4-a6-adoption-execution-log.md),
appended per task.

---

## What happened

The owner ruled **GO at `LBA-A6`** — population `P`, threshold 3, `LBA-D1` pairing — then gave two
further rulings during the session. All four pieces of work landed.

1. **`LBA-AM4` added to the pre-registration's §11**, committed **before any build work began**,
   which is the property it exists to have. It inserts `LBA-G5`, an unblinded use gate, between §8
   items 3 and 4. **The owner's criterion and his two-day period are recorded verbatim**, written
   before he had seen a single journey on any `LBA-` map.
2. **§8 items 1–3**: fame over `P`, the candidate build, the structural proof, acceptance,
   serialisation, manifest and sidecar.
3. **Acceptance recalibrated** on his ruling — only the three bounds that failed, centres from
   stage 2's §3b.
4. **All four id/fact maps re-extracted** over the candidate's population on his ruling, shipped as
   new dated package data.

## ⚠ The five things a reader is most likely to get backwards

**1. `LBA-G5` is a STOP-GATE, not a quality bar, and a pass is not evidence of anything.** It can
only stop the candidate. `REQ-38` remains owed in full at §8 item 4 and must still be designed
**cold, by a separate session, when no journey exists on either map** (`LBA-D3`). A session citing
a `LBA-G5` pass as evidence of path quality has inverted the amendment.

**2. The acceptance recalibration REJECTS the served map and REJECTS the fallback.** The builder
cannot reproduce `graph-msw-tu50.bin` while these bounds stand — the `LUX-E1` drift shape,
**deliberately re-entered** with the owner's knowledge. It was raised before he ruled. **If the use
gate fails, restore `acceptance.py`'s `PREVIOUS (MSW- restore 2026-09-05)` line BEFORE rebuilding
either map.** `tests/test_acceptance.py` asserts the rejection so it cannot present as a mystery.

**3. The id coverage gap is NOT an `LBA-G5` signal**, before or after the re-extraction. A missing
id degrades to name search — today's behaviour, never a wrong answer. A wrong-artist clip during
the gate is a property of an id snapshot, not of the similarity graph, and the criterion is about
novelty and coherence.

**4. The re-extraction only PARTIALLY discharges the `LUX-4` deferral.** It is discharged for the
candidate's population. **The served lineage's own re-extract remains armed.**

**5. `LBA-A3` differs from the candidate in TWO columns, not one** — population *and* drop-list
payload (§2.1's baseline column). It is a sound fallback; no comparison between them may be
reported as a population effect alone.

## Claims not to revert

- **The candidate is structurally identical to stage 2's `LBA-A6`** — the bare re-serialisation is
  byte-identical and all eight structural fields match. Neither fame nor the new id maps moved the
  map. Every structural figure stages 2 and 3 recorded still describes this artifact.
- **The `CXR-` regression was detected within MINUTES of use.** Four frozen documents say "after
  three weeks"; that is **time-to-report**, not time-to-detect, and the owner corrected it on
  2026-09-21. The correction lives forward in `LBA-AM4`; the four documents are frozen and were not
  edited.
- **Only the three failing bounds moved**, centres from stage 2's §3b — a build recorded six days
  before the candidate existed, which is what satisfies "independent of the build that went red".
- **The re-extraction is strictly additive** and the extractor refuses if it is not.
- **Step 6 of the refresh procedure does not fire at `P`** — the `20260809` payload censused `P`
  with 0 uncovered. Stage-3 README §9 option C reads otherwise; it describes the general refresh.
- `LBD-X6` stands; both `LBL-` verdicts remain run-once and final; `LBD-C1` is never cited as
  passed; `LBA-R8`/`LBA-R9` remain unreachable.

## Three defects found in this session's OWN instruments, all fixed

All three had the same shape — **an instrument reporting something other than what it did** — and
none touched an artifact. Recorded because the shape is the point, not the individual bugs.

1. **The acceptance reporter omitted a bound.** It tabulated four and the shipped check reported
   three failures including `median_degree`, which the table did not have. Caught only because the
   script prints the shipped verdict verbatim beside its own table. Fixed structurally: the report
   now mirrors `check_acceptance` check for check and asserts its covered field set against the
   `AcceptanceCriteria` dataclass.
2. **A guessed attribute name.** `store.fame_lb` does not exist; `GraphStore` keeps `fame_lb_pctl`.
   The correction is better than the intent — it now asserts the fame *ranking* is present and
   sized, which is the exact quantity `LBA-AM4` says the candidate acquires.
3. **A closing line that printed a false statement** — "STOPPING before serialisation",
   unconditionally, in the same output that recorded the artifact and its checksum.

## What I know that is not in the durable record

**Nothing material.** Two small things, recorded here because that is what this section is for:

- The first serialising run died after writing the artifact and sidecar, so those files existed
  briefly from a run that exited non-zero. They were overwritten by the successful run; the
  committed checksum is the successful one's, and the build is deterministic.
- `docs/README.md` had **five stale rows claiming "ACTIVE — the CURRENT handoff"**: the in-chain
  stage-2 row, plus four August ones. **All five are now fixed.** The four were adjudicable after
  all — each file's *own* role line already said SUPERSEDED and named its successor, so the map
  rows simply contradicted the files. ⚠ **The `doc-auditor` recommended track-scoping those four
  instead** (*"ACTIVE — the CURRENT handoff FOR THE `ULF-` TRACK"*), which would have enshrined
  four superseded handoffs as current for their tracks. The files settled it; the recommendation
  was not followed, and the reason is recorded in the rows themselves.
- **The invariant now holds and is cheap to re-check:** exactly one row may begin its role field
  with an unscoped *"ACTIVE — the CURRENT handoff"*, and two more are legitimately track-scoped
  (`UXR-`, `LBD-`):
  ```bash
  grep -cE '^\| `[^`]+` \| \*\*ACTIVE — the CURRENT handoff[.,]' docs/README.md   # must be 1
  ```

## Owed, and by whom

**The owner's**, in this order — per `NEXT.md`'s rule this note does not record how far he has got:

1. **Run the queued use-the-app tests** — `TEST-QUEUE.md`, 15 unticked, untouched by this work.
2. **Merge the candidate PR (#131).**
3. **Decide whether `LBD-AM3`'s override extends to `LBD-A4`** — carried forward, nothing blocked.
4. **RUN `LBA-G5`, the use gate.** Two days of actual use, against his own criterion. The local run
   command is the candidate README §8. **This is the next action.**

**A fresh session's, once he reports the gate's result:**

1. **If it PASSES** — the `REQ-38` listen amendment, designed **cold**, by a session that has seen
   no journey on either map (`LBA-D3`). `GBL-` §5's run-once rule binds its verdict.
2. **If it FAILS** — restore the acceptance bounds first (see warning 2), then the fallback is
   `LBA-A3`. Nothing else is owed but the record.
3. **Either way**, the served lineage's id re-extract remains armed.

## Artifacts (gitignored — checksum is the only identity they will have)

**`LBA-A6-candidate.bin`**, sha256
`28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b`, 39,697,349 bytes, at
`C:\unsung-fast\lbd-artifacts\`, with its sidecar beside it. **Take the checksum from the sidecar,
never from this note** (`DEP-24`).

**New gitignored inputs:** the fame records at `C:\unsung-fast\lbd-archives\S4-A6-fame`. Stage 2's
`S4-A6` archive and `LBA-A6.bin` are **unchanged**, asserted by sha256 before and after every pass.

**Committed, not gitignored:** the three new dated package-data files under
`builder/src/artistpath_builder/data/`. The previous dated files remain on disk and were never
edited.

## Nothing is in flight

No background jobs, no dispatched subagents, no half-written directories. **No listeners on 8000
or 5173** — swept at closeout; this session started no dev server. The working tree is clean and
every task was committed as it landed.

Branch `lbd-s4-a6-adoption`, PR **#131** (`gh` says where it is).
