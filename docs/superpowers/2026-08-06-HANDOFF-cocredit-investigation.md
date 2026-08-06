# Handoff — the co-credit investigation, 2026-08-06

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-06-HANDOFF-clip-cover-art.md`](2026-08-06-HANDOFF-clip-cover-art.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**⚠ A MID-FLIGHT retirement, not a seam handoff** — though the *work* did reach a seam. Both
items the owner approved are finished and committed. The retirement is triggered by the
**degradation tell** (`CLAUDE.md`): this session made four file-or-design selection errors
(two wrong archives, one wrong drop-list variant, one fatal sample rule). **Every one was
caught and corrected in-session**, and none reached a committed document uncorrected — but the
rate is the tell, and the tell is a retirement trigger rather than a resolution to be careful.

**Read this note's enumerations rather than trusting its judgement.** That is the point of the
mid-flight form: the faculty being distrusted is exactly the one that would decide what is
"worth mentioning".

Branch `cocredit-relationship-probe`, **draft PR #87**, pushed. Tree clean.
Reasoning: [`2026-08-06-cocredit-investigation-execution-log.md`](2026-08-06-cocredit-investigation-execution-log.md).
**No shipped code was touched** — nothing under `api/`, `frontend/` or `builder/src/`.

---

## Documents that are now wrong, and in which direction

**None that I introduced, and none of another session's.** `LBS-1`, `CAU-`, `ULF-`, `GBL-` and
the `MSW-` adoption are all untouched. `docs/README.md` gained two rows for the new
pre-registrations (the only two hard `docs-lint` failures, both mine, both fixed).

## Claims that must NOT be reverted by a well-meaning editor

- **`CCR-`'s null is recorded as instrument-limited, and that is not an excuse being made for
  it.** `inc=artist-rels` genuinely cannot see shared recording credits, and Laura Lee — the
  motivating case — scores `False` on it. **Do not "resolve" this by reading the null as
  evidence against the hypothesis.** It is untested at population scale by that probe, and
  equally unsupported by it. Both halves travel together.
- **`CCR-C3` is void and deliberately left uncorrected.** Do not adjust its number; delete
  nothing.
- **`RCC-C2` compares "top of your list vs bottom of your list" across arms**, not "rank 1 vs
  rank 75". That sentence is required by `RCC-AM1` and travels with every citation.
- **B1 carries no pre-registration on purpose.** It reads a shipped function's behaviour. Do
  not retro-fit criteria to it, and do not treat it as licensing a rescale change.
- **The three corrections in the execution log §4 are mine, not another session's.** Do not
  attribute them elsewhere or "restore" the original claims.

## Already updated — do not redo

`docs/README.md` (two new rows), the three `builder/analysis/2026-08-06-*` READMEs, both
pre-registrations, the retained execution log. `docs-lint` hard checks pass.

---

## Every number computed that is NOT written down anywhere

*Enumerated, not filtered for relevance.*

- **MusicBrainz "Laura Lee" name-collision search:** six artists carry that name; the ones I
  read were `70a65cf5…` (soul & gospel singer, US, b. 1945), `aa9c30b4…` ("Queen of Western
  Swing", b. 1920), and `50ef58c4…` (member of Khruangbin, b. 1986-10-14). **Only the first
  and last matter to the open puzzle.**
- **The two Khruangbin + Leon Bridges recording titles I read**: *B-Side* and *Texas Sun*,
  both credited "Khruangbin / Leon Bridges / Austin Jenkins". **The count is owned by
  `builder/analysis/2026-08-06-rcc-shared-recording/README.md`** and is not restated here; the
  titles reached no document.
- **Laura Lee's own archived top-6**, read once and not stored: Leon Bridges 214,
  Tame Impala 204, Khruangbin 133, SAULT 114, Skinshape 109, Unknown Mortal Orchestra 101.
  **This is the evidence weakening the name-collision hypothesis** and only its conclusion is
  in the README.
- **Exploratory depth-census figures** (superseded framing, but the numbers stand): population
  base rate for the centrality-minus-fame class 3.18 % at gap > 0.5; ramp-on vs ramp-off at 20
  presses 34.4 % vs 9.3 %; `fame < 0.3` share at 20 presses 20.8 % against a graph-wide 30.1 %.
  **These live only in this session's conversation and in a scratchpad script**, not in any
  committed analysis directory.
- **Per-artist calibration values** read once: Zach Condon gap +0.915, Charlie Hall +0.706,
  Andrew VanWyngarden +0.673, Panda Bear +0.008, Steven Wilson +0.040.
- **Drop-list status of the named artists:** Andrew VanWyngarden was **KEPT by the keep-check**
  (has a Deezer id, clip resolves); Zach Condon, Panda Bear, Steven Wilson, both Charlie Halls,
  Leon Bridges and Khruangbin were **never evaluated**. Zach Condon and both Charlie Halls
  carry **no Deezer id**, so their clips resolve by name — a `BYP-13` exposure.
- **`CCR-` arm pools before sampling:** the class filter (`fame < 0.20`, `pop_pctl > 0.80`) and
  the control filter (`fame < 0.20`, `pop_pctl < 0.40`) — pool sizes were printed to a log that
  was overwritten by the second run and are **not recoverable without re-running**.

## Everything decided against, and why

- **Widening the drop rule** — tabled by me, withdrawn on the owner's reading before any work.
  Two nulls now also point away.
- **Dispatching `ml-graph-analyst`** — the open questions were arithmetic already written down
  or MusicBrainz lookups, not derivations.
- **Normalising `RCC-` by recording count** — would have divided out the property under test.
- **Reducing `RCC-`'s n to shorten the run** — rejected: n was pre-registered and a partial run
  supports no branch.
- **Amending `CCR-` into the recording test** — rejected; it would have destroyed the record of
  an instrument failure worth keeping.
- **Chasing the Laura Lee name-collision hypothesis to a conclusion** — deliberately stopped at
  "live but weakened". It needs its own pre-registration and I was already retiring.
- **Fixing `CCR-C3`** — recorded as void instead. It carries no branch.

## Anything the owner said in conversation that is not yet in a file

- **He does not think this is a case of "too obscure"** — stated explicitly, and it is in the
  `CCR-` pre-registration's framing but not as a quoted ruling.
- **He does not think Andrew VanWyngarden or Zach Condon should have been dropped by the
  filter.** *(This is the load-bearing one — it is what withdrew the drop-rule option, and it
  is recorded in the execution log §1 but has never been written into `PRODUCT-REQUIREMENTS.md`
  or any rule document.)*
- **He judged the forum thread "5 years old and probably predates their scoring of
  collaborators"** — correct, and confirmed: it concerns the recommendation pipeline, not the
  session-based similarity dataset we consume.
- **He read the Texas Sun duplicate art, looked the artists up, and diagnosed it himself** as a
  genuine co-write rather than a defect. **No file records that the duplicate-art symptom was
  owner-diagnosed rather than session-found.**

## The open decision — and what I would do

**The question:** which of the three open items to take first.

**What I would do if I were continuing: the Laura Lee puzzle.** Not B2. Reasoning, so it can
be argued with rather than re-derived:

- B1 **lowered** B2's value. The router demonstrably still uses the similarity signal (only
  very few edges clip and ordering survives — figures owned by
  `builder/analysis/2026-08-06-rescale-fidelity/README.md`), so a rescale change is a real risk to a live,
  working mechanism rather than a cheap win.
- The Laura Lee case is the **one thing two probes could not explain**, and the hypothesis that
  fits it — a same-named artist's listens landing on the wrong MBID — would be `BYP-13`
  operating on **graph edges** rather than on clips. That is a larger defect than anything
  else on the list, and nothing currently looks for it.
- It is cheap to bound: pick a sample of graph artists whose names collide in MusicBrainz and
  ask whether their similar-lists cohere with the *right* artist. Offline against the archive
  for the coherence half.

**What would change my mind:** if the owner cares more about what the app *does next week* than
about correctness of the map, B2 is the one that could move a user-visible knob, and Laura Lee
is diagnosis rather than improvement.

## Anything in flight

**Nothing.** No dispatched subagents at time of writing beyond the `doc-auditor` run belonging
to this closeout, no background jobs, **no local servers — ports 8000 and 5173 were swept and
both are free.** No half-written directories: all three `builder/analysis/2026-08-06-*`
directories are complete and committed.

**Scratchpad-only artifacts that will evaporate** (session scratchpad, not the repo): the
depth-census and ramp-control scripts behind the figures listed above, and two run logs. **If
those figures are wanted durably, they must be re-run** — the scripts are not in the repo
because they were exploratory, and that is the one thing I would fix given another hour.
