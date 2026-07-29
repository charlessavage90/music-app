# Handoff — Track 3 executed and read, 2026-07-28

**Role: ⚠ SUPERSEDED 2026-07-29 on next actions** by
[`2026-07-29-HANDOFF-requirements-track3b.md`](2026-07-29-HANDOFF-requirements-track3b.md)
— the owner's decision this handoff said was pending has been taken and reframed: the
requirements were rewritten (`PRODUCT-REQUIREMENTS.md`), Track 3b ran to a read (TB-R2),
the candidate decisions are PARKED, and the next work is graph-rebuild planning. Its Track
3 record and do-not-revert list stand unchanged. *(Original role line: ACTIVE, the CURRENT
handoff.)* Supersedes
[`2026-07-28-HANDOFF-track3-preregistered.md`](2026-07-28-HANDOFF-track3-preregistered.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**This is a seam handoff, not mid-flight.** Track 3 ran to a read: all prerequisites
discharged, all gates closed, DD-R1 fired, both analyst reviews complete, and the owner's
consultant review closed on all six of its items. Nothing is in flight, no subagent is
running, no server is up, no port is listening. PR **#46** carries branch
`track3-depth-descent`.

## What the successor should know first

**The result is a candidate for a trade, not a discharged mechanism.** Fixed wording, and
it must not be softened anywhere: *DD-R1 fired on the letter; the mechanism claim
(depth-priced descent) is UNRESOLVED because DD-C6 flags every arm; what exists is a
measured candidate for a different trade — ~7 mostly-obscure artists against ~13
mostly-famous — and that trade is the owner's to judge.*

**Nothing is scheduled.** No blind listen, no adoption, no further arms. All are the
owner's, and he has not ruled.

## Claims overturned — do not let a well-meaning editor revert these

- **DD-A4 and DD-A5 are struck** (DD-D4). They are bit-identical to DD-A2/DD-A3 at every
  scored depth and would fail DD-G2. Do not re-add them to reach the pre-registration's
  "six arms".
- **The pair set is `pairs_v2.json`, not `pairs.json`.** The re-draw is the DD-P1 remedy
  executed with headroom as a draw-time precondition, because the trigger is unsatisfiable
  by construction (DD-D3). `pairs.json` is retained as the record of the first draw.
- **The all-famous anchors are UNSCORED by design** and the held-out set **gates nothing**.
  Promoting held-out to a gate after seeing the analysis result is the specific move
  pre-registration exists to prevent.
- **RETRACTED: production "fails DD-C2 in the negative direction / its middles get more
  famous with depth."** The sign is not robust across poolings (log §8). Production's
  gradient is *indistinguishable from zero* — still a DD-C2 failure, materially weaker
  claim. **Do not restore the stronger wording**; it was in an owner-facing message and is
  corrected.
- **CORRECTED: "guard G is constant in fact"** → untested by exposure. All 42 activations
  come from two unscored anchor pairs with adjacent endpoints.
- **DD-D8 must appear in any summary of the result**: ~45 % of DD-A2's fame movement is
  carried by artists at the A11 fame floor; matched-only it reads −0.709 and would not pass.
  Omitting it is misleading by selection, not a simplification.

## Already updated — do not re-edit

`NEXT.md`, `docs/README.md` (execution log, analysis directory, this handoff, and the
pre-registration's row amended to record that it was executed and amended), `TEST-QUEUE.md`,
the previous handoff's role line, and `builder/analysis/2026-07-28-track3-depth-descent/README.md`.
`CLAUDE.md` and `memory/` are untouched — nothing in this work changed a working convention.

## What I know that is not in the durable record

- **`docs-lint.sh`'s figure candidates against the Track 3 log are false positives.** It
  flags `0.01`, `0.02`, `0.10`, `0.020`, `0.098`, `0.143` as adjudication figures; they are
  the device's `w` values, `w_hop`, and DD-C4 deltas. Do not "fix" them into citations.
- **The bare-identifier collisions the lint reports (`A0`–`A19`, `B1`–`B3`) are pre-existing
  Track 2/closeout collisions, not Track 3's.** The `DD-` namespace held with zero
  collisions, which is the pre-registration's own rule working.
- **`fame_cache.json` grew by ~370 entries** across the two fame runs and is committed. It
  is a network cache keyed by name — that is correct per P8b F8, not the defect DD-G4 names.
  A future track on mid-band pairs will mostly hit it.
- **Decided against, with reasons**, so it is not re-derived: adding a `--pairs-file` flag
  to the committed Track 2 walker (rejected — `run_arms_t3.py` imports `walk` instead, so no
  Track 2 file changes and every Track 2 figure still reproduces); repairing DD-C2's missing
  length control after seeing the result (rejected — that is the move pre-registration
  prevents; recorded as a stated gap instead); reconciling this session's per-pair DD-C2
  figures with the harness review's differing ones (rejected — every conclusion holds under
  both, so recorded rather than reconciled).
- **The DD-P3 ordering lesson is the transferable one.** The pre-registration scheduled its
  own analyst review *third*, after the pair draw and the headroom run — and nearly
  everything that review found was derivable from the document plus the artifact with no
  measurements at all. **Put the protocol review first in any future pre-registration's
  prerequisites.** This is a recommendation to the owner, not an adopted rule; it is not in
  `CLAUDE.md` and must not be added there by a session.

## The open decision, and what I would do

The owner's, and genuinely his: whether ~7 mostly-obscure artists beat ~13 mostly-famous.
It sits on a real tension between WGLL value 1 (novelty is an absolute count — satisfied,
1.5 → 3.1) and value 2 (bypass should *lengthen* and add novelty — the lengthening half
fails).

**If I were continuing and the decision were mine:** I would not spend a blind listen on
DD-A2 as it stands. Its DD-C1 pass is half floor-carried and its length effect is the
confound the track failed to resolve, so a listen would be adjudicating a candidate we
already know is mis-specified. I would put the **thresholded toll** (log §7) through its own
pre-registration first — it is length-neutral exactly where DD-D5's confound lives, so it
tests the mechanism claim Track 3 could not — and spend the ear once, on whichever of the
two survives its own gates. That is a recommendation, not a decision, and the owner has not
been asked to rule on it.
