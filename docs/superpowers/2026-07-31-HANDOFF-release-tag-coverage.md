# Handoff — the release-tag coverage probe (`REL-`), 2026-07-31

**Role: ⚠ SUPERSEDED 2026-07-31 on NEXT ACTIONS ONLY** by
[`2026-07-31-HANDOFF-tas-am3-am4.md`](2026-07-31-HANDOFF-tas-am3-am4.md).
**This document REMAINS AUTHORITATIVE for the `REL-` probe's internals** — its frames, its
aggregation device, its validity filter and its bars. The `REL-` record is complete and
untouched; only "what to do next" moved on. Supersedes
[`2026-07-30-HANDOFF-tag-discrimination.md`](2026-07-30-HANDOFF-tag-discrimination.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**⚠ One qualification on that supersession, and it is load-bearing.** The `REL-` probe is a
**parallel investigation, not a continuation** of `TAS-`. **`TAS-` Tasks 5–8 remain owed and
unrun**, `TAS-6` is still adverse, and the tag-discrimination handoff **remains authoritative
for that track's internals** — its dormant term, its bound-100 bar, its open architecture
decision. Nothing here touched any of them.

**A seam handoff.** The probe ran to completion, both instrument checks passed, nothing is in
flight, no background job is running, no dev server is listening, the tree is clean.

---

## What this was

The owner commissioned a read-only investigation while the `TAS-` session was parked: for
artists with **no genre label today**, can release-tag aggregation from MusicBrainz and
Discogs supply one — **in the obscure tail specifically**, since a frame that only thickens
labels where labels are already good changes nothing for `TAS-6`.

Records, in the order a cold reader should take them:

1. [`specs/2026-07-31-release-tag-coverage-preregistration.md`](specs/2026-07-31-release-tag-coverage-preregistration.md) — governing. **Read §8 first.**
2. [`findings/2026-07-31-release-tag-coverage.md`](findings/2026-07-31-release-tag-coverage.md) — owns every figure.
3. [`2026-07-31-release-tag-coverage-execution-log.md`](2026-07-31-release-tag-coverage-execution-log.md) — reasoning, decided-against, defects.

## Claims a well-meaning editor must NOT revert

- **`REL-3`'s ratio bar is a degenerate pass and is recorded as worthless.** The null median
  is exactly 0.000, so "≥ 3× the null" is a division by zero. The criterion is carried
  entirely by its zero-overlap half. Do not "fix" this by quoting the ratio as a pass.
- **`REL-C2`'s shuffled coverage is HIGHER than the real figure, and that is correct.**
  §4 predicted it in advance. Shuffling ownership relocates coverage rather than destroying
  it. It is barred from being read as evidence about `REL-1`, and the barring is the point.
- **`REL-AM2` was written after `REL-1`'s passing figure was known.** That disclosure stays at
  the amendment's head. Do not tidy it away because the repair was sound.
- **The headline and what cuts against it travel together**, the way `COH-2`/`COH-3` and
  `FPC-2`/`FPC-9` do: `REL-1`'s pass must be quoted with `REL-3`'s fidelity median and with
  the artists neither source reaches (findings `REL-1`, `REL-3`, `REL-4`). Either alone gives
  the wrong answer.
- **Discogs `genre` being 100% filled is a schema constraint, not a coverage achievement.**
  It is why `REL-2` *is* the Discogs arm rather than a caveat on it.
- **Release-level tags are sparser than release-GROUP tags.** I claimed the opposite early
  from one worked example and the census overturned it. The 345 GB release dump is out of
  scope on those grounds and has been deleted.

## What has already been updated — do not re-edit

- `docs/README.md` — the two new `REL-` documents plus this handoff and the execution log are
  classified. **Two stale "CURRENT handoff" claims were corrected**: the coherence-tag-probe
  row still claimed to be current despite its own successor saying otherwise, and the
  tag-discrimination row now points here while retaining its `TAS-` authority.
- `NEXT.md` — rewritten at this closeout.
- `TEST-QUEUE.md` — see C1 note below.

## What I know that is not in the durable record

- **The four dumps live only in `builder/scratch/`** (`mb-json-dumps/artist`,
  `mb-json-dumps/release-group`, `discogs-data-dump/`), are gitignored, and **will not appear
  in a `git worktree`.** Any re-run must point at the main tree explicitly. The MusicBrainz
  `release` dump and both `.tar` files were deleted after measurement.
- **`REL-4` had no home in any collector** and needed both sources joined, so `rel_union.py`
  was written after the fact. It is not a late addition to the criteria — `REL-4` is in the
  committed pre-registration — only to the harness.
- **The `rel_artist_index_raw.json` reuse is deliberate**: the index is a pure function of a
  frozen local file, so the script reuses it rather than re-reading 17 GB. Delete the file to
  force a fresh pass. This bit me once during the `REL-AM1` fix and is now commented.
- **I did not run `session-start`** and said so at the time. This session acted on repository
  state without it.

## The open decision, and what I would do

**Whether `REL-`'s result gets taken into `TAS-`.** The probe shows the unlabelled obscure
population could shrink from 64.6% to 29.0% of the lower half — and that population being
squeezed out is precisely what made `TAS-6` adverse. So the result is *live* for `TAS-`, not
merely interesting.

**What I would do if I were continuing:** not rebuild yet. `REL-3`'s fidelity median is the
number that should govern, and it says the labels land in the right region rather than being
right. Before spending a rebuild and a blind listen, I would want a cheap read on whether a
*coarser* label — agreement at the "shares any genre" level, where `REL-4` measures the two
sources concurring on nearly all artists both reach — is enough for what `TAS-` actually does
with agreement. That is a
question about the device, answerable against the committed `TAS-` harness without any
rebuild, and it would decide whether the richer frame is worth the Track-B-shaped cost.

**It is the owner's trigger either way** — a rebuild spends his ear (`REQ-38`), and a `TAS-`
§1 vocabulary change is an amendment to a frozen document.

## In flight

**Nothing.** No dispatched subagents, no background jobs, no half-written directories, no
listeners on 8000 or 5173.
