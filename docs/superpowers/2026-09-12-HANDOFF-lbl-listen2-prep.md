# Handoff — `LBL-` listen 2 prepared under `LBD-AM6`, 2026-09-12

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-11-HANDOFF-lbl-listen1-read.md`](2026-09-11-HANDOFF-lbl-listen1-read.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The pre-screen ran, the amendment is committed, the materials are built and
tested. Nothing is half-finished and nothing is in flight.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
the **`LBD-AM6`** block at the end of §10 and its §12 register row.
**Retained log:** [`2026-09-12-lbl-listen2-prep-execution-log.md`](2026-09-12-lbl-listen2-prep-execution-log.md).
**Pre-screen figures owner:** `builder/analysis/2026-09-10-lbd-blind-listen/lbl_prescreen2.md` —
cite it; do not restate a count from it.
Branch `lbl-listen2-prep`, PR #122 (addresses only; `gh` says where they are).

---

## ⛔ The session that prepared this may not run the listen or write it up

It ran the pre-screen, which generates both maps' journeys for 46 candidate pairs **labelled by
map**. `LBD-AM6`'s preamble states the bar; this repeats it because it is the one thing a
successor could undo by accident.

**Three fresh sessions are needed, in order, and none of them is this one:** a mechanics-only
**runner** working from `RUNNER-BRIEF.md` and nothing else; then, after the owner has listened, a
further fresh session to **write up** the result. Neither may read `lbl_prescreen2.json`,
`lbl_prescreen2.md` or `lbl_prescreen2.py` — they record each map's journey length per pair and
depth, and matching a length against the served page unblinds the listen.

## What a cold reader most needs

1. **The comparison did not change.** Listen 2 is still `LBD-A0V` against `LBD-A5V` — *does
   accepting a connection two listeners support, instead of four, give better journeys?* — with
   `LBL-R1`–`LBL-R4`, their listen-2 plain sentences, the bar of 8 and the 24 rows exactly as
   `LBD-AM5-5` registered them. **What changed is the pairs and the protocol.**
2. **Why.** Listen 1 tied, and its §3 measured the limiting factor rather than guessing it: most
   rows the owner could not call were rows where he knew everyone on both sides, and two pairs ran
   three or four steps with nothing to judge. The instrument, not the question, was the problem.
3. **The pairs were selected by a screen whose rule was committed before it ran** (`855b090`),
   on the **magnitude** of the difference between the two maps' journeys and on **unfamiliarity** —
   **never on direction.** A screen that preferred one map's journeys would have hand-picked the
   pairs that map wins on. If you touch the screen, that is the property to preserve.
4. **Pick strength is asked but the tally does not read it.** The owner's two constraints — ask for
   strength, leave `LBL-R1`–`R4` unchanged — admit only that treatment, since anything reaching the
   tally *is* a change to the reads. There is a test asserting the verdict is invariant under every
   strength answer; it is not decoration.
5. **`LBD-D6` is ruled**, verbatim in `LBD-AM6-7`: `LBD-A4` **waived for listen 2, enforced before
   `S4`**. `NEXT.md`'s deferral row was narrowed accordingly.

## Claims that must NOT be reverted

- **`LBL-R1`–`LBL-R4` and their plain sentences are unchanged.** If a future session finds the
  listen-2 sentences in `lbl_unblind.py` and thinks they were written now, they were not — they are
  quoted from `LBD-AM5-5`'s own table, fixed before any journey existed.
- **Listen 1's schema is frozen and everything is keyed per listen.** `check_pair`'s `min_interior`
  defaults to **1** deliberately; `ROW_EXTRAS_BY_LISTEN[1]` is empty deliberately. Changing either
  to "tidy up" makes the completed listen retroactively incomplete — there is a test over the real
  `lbl_listen1_verdicts.json` guarding it.
- **`RUNNER-BRIEF.md` is now listen 2's.** Listen 1 ran from that file at commit `916bc6f`, which
  is what the listen-1 results note means when it cites the brief. Do not "restore" listen 1's text.
- **`lbl_pairs.json`'s listen-2 table is superseded and was never used.** No journey was generated
  on it; nothing was spent. Listen 2's pairs are `lbl_pairs2.json`.
- **`LBD-X5` and the barred-reads list still stand**, and `LBD-X6` is new: listen 2's result may not
  be generalised to the cheaper pairing form until `LBD-A4` has run and `R10` has been read.
- **`lbl_prescreen2.json` is committed AND forbidden to a runner.** Both halves are deliberate —
  a screen whose evidence is not committed cannot be audited. Do not "fix" this by deleting it.

## What is on disk and must not be rebuilt

Identities owned by `builder/analysis/2026-09-10-lbd-served-population/README.md` §5; paths only
here. Both maps were verified against those checksums twice this session — once by hand at session
start, once by `load_map` on every run.

| | |
|---|---|
| the two listenable maps | `C:\unsung-fast\lbd-artifacts\LBD-A0V.bin`, `LBD-A5V.bin`, each with its `.bin.json` sidecar. **Unchanged; nothing was rebuilt** |
| listen 2's pairs | `lbl_pairs2.json`, sha256 `0a2eca01…`, pinned in `lbl_common.PAIRS2_SHA` and gated by G3 |
| listen 2's page data, clips, verdicts | **do not exist.** Generation has never been run for listen 2 |
| the sealed mapping | **does not exist** for listen 2. `.superpowers/lbl/` holds listen 1's, already unsealed |

## What I know that is not in the durable record

- **The greedy draw is order-dependent**, so the candidate set is a function of the pool order and
  the exclusions. Change any exclusion and every pair changes, not just the affected ones. This is
  in the execution log §9; it is repeated here because it is the thing most likely to be
  rediscovered expensively.
- **Two of the previously-dealt listen-2 pairs came back into the candidate draw and were rejected
  on their merits** — they were not excluded by rule. Nothing turns on it; it is the kind of detail
  a successor would otherwise spend time re-deriving from the output.
- **A vacuous test was found and fixed during closeout**, not during development: the length-gate
  test built its fixture from `MIN_INTERIOR` itself, so it passed at every value of the bar.
  Four tests now pin the bars independently. **If you add a gate here, do not build its test's
  fixture out of its own constant.**
- **Snyk ran clean on the whole blind-listen directory** (0 issues), which also means the expired
  credentials recorded in `NEXT.md`'s Snyk deferral are working again for at least this path. That
  deferral is about the frozen modules under `builder/analysis/` and was **not** discharged here —
  scanning them would produce findings on code nobody may edit, so it stays the owner's trigger.

## In flight

**Nothing.** No server, no listener, no background job — ports 8000, 5173 and 8765 were all clear
at closeout and this session started none. No subagent is running.

## Owed, and by whom

| | |
|---|---|
| **Owner** | **merge PR #122.** |
| **Owner — the next real decision** | **whether to spend listen 2 now.** Everything is prepared; it costs his ear and a sitting. Nothing here starts it, and no session proposes starting it. |
| **Owner — unrelated and still queued** | the **three use-the-app tests** in [`TEST-QUEUE.md`](TEST-QUEUE.md), live since the 2026-09-08 deploy. Untouched by this work. |
| **A fresh, mechanics-only session, when he chooses to listen** | run `RUNNER-BRIEF.md` end to end. It is self-contained; it must read nothing else. |
| **A further fresh session, after the verdict is saved** | the write-up, against `LBD-AM5-5`'s reads and `LBD-AM6`'s descriptive additions. |
| **Before any `S4` arm is pre-registered** | **`LBD-A4` must run and `R10` must be read**, per the owner's `LBD-D6` ruling, and every `S4` arm records which pairing semantics it uses and why. |
