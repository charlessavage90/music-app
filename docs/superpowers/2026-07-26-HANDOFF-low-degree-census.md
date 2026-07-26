# Handoff — the degree-1 / degree-2 census, 2026-07-26

**Written at a clean seam. Nothing is in flight.** The work is finished, committed and
pushed; PR #25. Aimed at a session that has never seen this work.

Governing documents, in order: the execution log
[`2026-07-26-low-degree-census-execution-log.md`](2026-07-26-low-degree-census-execution-log.md),
then the findings
[`findings/2026-07-26-low-degree-census.md`](findings/2026-07-26-low-degree-census.md), then
the deliverable `builder/analysis/2026-07-26-low-degree-census/REPORT.md`. **Where they
disagree, the execution log wins.**

## What is now true that was not

**Recognisable artists are stranded where the app can never introduce anyone to them.** An
artist with one connection cannot be an interior card, so it can only ever appear as one of
the two the user typed. Named examples are in the findings document; counts are owned by the
analysis directory. `DRV-4` stated this structurally and it is now measured.

**`DRV-4`'s denominator question is closed** — the two populations are nested, not
alternatives, and the choice is immaterial. Do not re-open it.

## Which documents are now wrong, and in which direction

- **Nothing is *wrong*.** No prior claim is overturned. This is additive.
- **`specs/2026-07-23-track2-preregistration.md` A11 gained a SCOPE NOTE** in three places.
  **A11 itself is unchanged and Track 2's result stands.** The A-series still runs A1–A19 —
  **there is no A20, and a well-meaning editor must not create one** to "tidy" the note into
  the amendment sequence. It is deliberately not an amendment.
- **`docs/README.md`** gained one row.

## Claims that must NOT be reverted by a well-meaning editor

1. **The screen-leak estimates and the crawl-coverage-gap reading are WITHDRAWN, not
   caveated.** They read as a plausible, quantified finding, and an editor may be tempted to
   restore them with a warning attached. They cannot be separated from misidentification with
   this instrument — the two strongest apparent leaks were *Ryan Gosling* and an anime. The
   consulting session asked for the coverage reading specifically; it was right that the
   question matters and wrong that this instrument could answer it. The question survives as
   an open question with no owner (findings §4).
2. **The bulk-SPARQL approach is abandoned, not unfinished.** `sparql_candidates.py` and
   `verify_sparql_recall.py` are imported by nothing **on purpose**. Do not wire them in, and
   do not "finish" them: two of three miss-causes are easy to fix, which is the trap. The
   real reason is that the canonical resolver's precision comes from opensearch's *ranking*,
   so any bulk replacement needs a disambiguation rule of its own and A11's validation stops
   describing the instrument.
3. **`pop_raw` selects who to ask and ranks nothing.** If a future edit sorts any output by
   it, that reintroduces §2.11's error.
4. **The cut was deliberately not deepened** (owner's call). Deepening it with the same
   instrument would inherit the same contamination.

## What has already been updated — do not re-edit

`docs/README.md` (one row), the A11 scope note (three placements, mutually consistent), the
findings document, the execution log, `TEST-QUEUE.md` (one entry), and
`builder/analysis/2026-07-26-low-degree-census/README.md`. Memory gained one file,
`stop-refining-instrumental-artifacts.md`, and one index line.

## What I know that is not in the durable record

Checked deliberately, and the list came back with three items — all now folded in above or
into the log rather than left here. Restated for a cold reader:

- **`CNS-` is a slightly awkward prefix and the awkwardness is deliberate.** It stands for
  "consulting session" and `CNS-1` is theirs, but `CNS-2` is this session's, filed under the
  same prefix on the owner's explicit instruction not to mint a second prefix for one item.
  The findings document says attribution is per-item, not per-prefix. **Do not "fix" this by
  renaming.**
- **The `title_disambiguator` / `different_title` classifier is this session's invention**,
  not part of A11. It lives in `report.py` and is a *diagnostic*, not a scoring rule. If it
  ever becomes load-bearing it needs its own validation.
- **Why the poll ran at 2 workers and not more**, and why the numbers in the log's §7 should
  be trusted over any observed burst speed: sustained concurrency triggers cumulative
  throttling that a short burst does not reveal, and the canonical resolver converts a
  throttle into a *fame-floor score*. Going faster does not just slow down, it silently
  fabricates obscurity.

## The open decision, and what I would do

**None of this session's work carries an open decision that blocks anything.** The one
genuine decision is the owner's and is not urgent:

**Should the resolver consult the artifact's disambiguation?** *(Plain: should the fame
lookup use the short description the graph already stores, so it stops confusing a band
called War with Axl Rose?)*

**What I would do if I were continuing: not this, not yet.** It reaches under half the
matched rows and misses both worst cases, which have an empty disambiguation — so it is a
partial fix to a diagnostic instrument, and it touches A11, which is adopted and validated.
The cheaper and more honest move already taken is that every suspect row is flagged inline
for the reader. **What would change my mind:** a decision to use this proxy as a *scoring*
input on a low-degree population, at which point flagging is not enough and the instrument
needs fixing properly, with its own pre-registration.

**Success condition for the exposure residual:** if any future work re-opens `R0` or
re-scores Track 2, it runs this session's classifier per cell *first*, to check whether a
misidentified interior is pivotal to a specific cell. That is the one thing deliberately not
checked, because checking it is re-scoring.

## What was decided against

- **Deepening the popularity cut** — instrumental precision with no decision attached.
- **Fixing the bulk-SPARQL filter** — see above; abandoned on principle, not on effort.
- **Running the disambiguation check** — reaches under half the rows, misses the worst cases,
  and touches an adopted instrument.
- **Re-scoring Track 2** — the exposure was bounded from committed artifacts instead.
- **Minting a second identifier prefix** for `CNS-2` — owner's instruction.

## Nothing is in flight

No dispatched subagents, no background jobs, no half-written directories. The tree is clean.
`resolve.log` is gitignored deliberately (a transcript, not a result); `fame_cache.json` **is
committed** and is what makes re-resolution cheap — do not delete it.
