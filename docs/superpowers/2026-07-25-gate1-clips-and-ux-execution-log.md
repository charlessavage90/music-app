# Execution log — Gate 1 leftovers: the clip defects and the frontend UX items

**Role: COMPLETE.** The record of the work on branch `gate1-clips-and-ux` (PR #19),
2026-07-25. Six items, all from the roadmap's Gate 1 / Phase 1 list. **Nothing here touches
path quality**, which is paused by owner decision — no pathfinding, no cost function, no
graph artifact, no weight, no rebuild.

> Figures about scoring and path quality live in
> [`findings/2026-07-21-scoring-adjudication.md`](findings/2026-07-21-scoring-adjudication.md)
> and are neither used nor restated here. This work produced no such figures.

---

## 1. What was done

| Item | Where |
|---|---|
| **C1** — clip played the wrong artist | `api/src/artistpath_api/clips.py` |
| **C2** — clips died after ~an hour | `clips.py`, `config.py`, `frontend/src/hooks/useClip.ts` |
| Navigation off the path page | `frontend/src/routes/PathPage.tsx`, `LandingPage.tsx`, `ArtistSearch.tsx` |
| Card pause button | `frontend/src/components/ArtistCard.tsx`, `player/usePlayer.ts` |
| Audio stops on recompute | `frontend/src/components/JourneyList.tsx`, `player/usePlayer.ts` |
| Bypass hidden on start and end artists | `ArtistCard.tsx`, `JourneyList.tsx` |

**Identifier note.** `C1`/`C2` here are the **roadmap's clip defects**, not Track 2's
success criteria of the same names and not `closeout`'s check IDs. The collision predates
this work and is not renamed, per the forward-only rule.

## 2. Defects found in the governing document

Found by the pre-execution grep sweep, before any code was written. All three are defects
in the **roadmap**, not in the code.

1. **C1's stated cause was stale, and the real defect was worse.** The roadmap records the
   code as taking `data[0]` blindly. It in fact requested `limit: 1` — there was never a
   list to filter. **Consequence:** the roadmap's prescribed fix ("match the returned
   track's artist name") would, applied literally, have converted wrong clips into *no*
   clips for every artist. The fix needed a second half the document does not mention:
   ask for more results.
2. **iTunes carried the same defect and the roadmap does not mention it.** The fallback
   also requested `limit: 1`, with no artist check of any kind. Fixing only the documented
   half would have left the fallback serving wrong artists.
3. **A second copy of the volatile value existed outside the documented location.**
   `useClip.ts` is a module-level cache holding the signed preview URL with no expiry. A
   server-only C2 fix still serves dead audio on a tab left open — which is precisely how
   the defect is encountered. Fixed as part of C2.

**The generalisable point.** All three are the same shape: the roadmap described the defect
accurately *as experienced* and inaccurately *as located*. A diagnosis recorded from the
symptom is not a diagnosis of the code, and the gap only appeared on reading the source.
This is what the "grep every function, file and config value a plan names" rule buys, and
it was worth it here on the first of the three.

## 3. Decisions taken, with reasoning

- **When no track matches the artist, serve nothing.** A silent card is a worse product
  than a playing one and a better one than a wrong one, and the wrongness was the reported
  complaint. Consequence recorded in the test queue so it does not read as a regression.
- **Cache identity, re-resolve the URL per request** rather than caching the URL with a
  short TTL. A TTL would need a number nobody has measured and would fail in the direction
  of silence. This also discharges the roadmap's Gate-3 constraint: proxying and
  pre-signing both need a stable track reference, which is now what is stored.
- **A cold lookup does not pay for a second round trip.** The search response already
  carries a signed URL, so `_search` returns the identity *and* that URL. Guarded by a test.
- **Pre-C2 cache items are a miss, not a migration.** They hold a long-dead URL and no
  track id, so they cannot be re-resolved. They are overwritten on next use.
- **Ten minutes for the browser-side cache.** A judgement inside the lifetime recorded in
  the roadmap's C2, not a measurement of its own. Named as such in the code.
- **`clip_search_limit = 25` is a judgement, not a measurement.** The one documented case
  needed 2. Nobody has measured the worst case. Named as such in `config.py` after the
  prose-versus-code check caught the comment claiming otherwise.
- **Two navigation controls, not one** (owner's decision, after review of the first
  version). "New path" carries the pair back to the landing page prefilled; "Reset path"
  drops the bypasses and keeps the pair. The original single control conflated them.
- **A seeded artist needs both id and name.** The id routes, the name fills the box; half a
  pair would enable "Find path" on an artist that cannot be routed from.

## 4. Decided against

- **A short TTL on the server-side URL cache** to soften the Gate-3 load. It would trade a
  guessed number against the exact failure mode being fixed. The roadmap already accepts
  the load cost as a Gate-3 problem; re-solving it here would foreclose nothing but would
  add a knob whose value nobody can defend.
- **Migrating existing Dynamo cache items.** They contain no track id. There is nothing to
  migrate *to*.
- **Fixing the zero-intermediary case** surfaced in §6. It is pathfinding, and pathfinding
  is paused.
- **Making "Reset path" always visible but disabled.** Rendered only when there is
  something to undo. Reversible in one line if it proves undiscoverable; flagged to owner.

## 5. Gate outcomes

| Gate | Outcome |
|---|---|
| builder / api / frontend suites | **Pass** — see §8 |
| `npm run build` (tsc + vite) | **Pass** |
| `npm run lint` | **Pass** — one pre-existing `vite.config.ts` warning, not from this work |
| Snyk `snyk_code_scan`, both changed trees | **Pass**, 0 issues |
| **B3 mutation check** | **Pass** — six deliberate mutations, all killed; see §7 |
| **Clip survives an hour in real use** | **NOT RUN, and no test can run it.** Queued. |

**Nothing failed and nothing was worked around.**

## 6. Corrections and consequences for the prior record

- The roadmap's **C1 and C2 are fixed in code** but **not confirmed in use**. They are not
  closed until the queued check returns.
- **A path with no interior artists now offers no bypass control at all.** With bypass
  removed from the endpoints, a two-stop path has nothing to press. This is the known
  zero-intermediary famous→famous case (**F1**, candidate for a min-length guard),
  *surfaced* by this work rather than caused by it. No action: it is pathfinding.
- The roadmap's Phase 1 text still opens "**C3 leads this phase**" and prescribes deleting
  `w_floor` and `floor_relax_*`. That is path-quality work and is **under the pause**; the
  document predates the pause by four days and does not say so. A session reading the
  roadmap alone would begin with the one item it must not touch.

## 7. Operational measurements

- **Mutation check (closeout B3), six mutations, all killed:** artist matching disabled
  (4 tests red); cached URL reused instead of re-signed (3 red); pre-C2 cache items
  accepted (1 red); stop-on-recompute removed (1 red); endpoint bypass restored (2 red);
  browser cache expiry removed (1 red). Every guarded invariant has at least one test that
  genuinely fails when it is broken.
- **Standing context layer (closeout D6):** `CLAUDE.md` **net zero** — the orient row's
  stale "next is Gate 1 leftovers" clause was replaced one-for-one, not extended.
  `.claude/skills/` and `.claude/agents/` **untouched**. `memory/` went **404 → 412 lines,
  net +8**: `clip-resolution-bugs.md` was rewritten from "diagnosed, go and fix it" to
  "fixed, not closed". The first rewrite added 25 lines and was **trimmed back below the
  original**, because the file's job shrank when the defects were fixed — the root-cause
  narrative now lives in this log, and memory holds pointers, not detail. The remaining +8
  is the status banner and the live-API risk, which is new information.

## 8. Suite output

```
builder   115 passed
api       133 passed
frontend   42 passed (11 files)
```

## 9. Deferred findings, each with a success condition

**New from this work:**

| Finding | Success condition |
|---|---|
| **C1/C2 confirmed in real use** — the per-track lookup shapes are from published API docs and have never been exercised live; the tests inject a fake fetcher, so a wrong field name passes everything and produces a silent card | The queued use-the-app check returns. **Until then C1 and C2 are fixed-not-closed.** |
| **`clip_search_limit = 25` is unmeasured** | Accepted as a judgement. Revisit only if cards come back silent for artists that obviously have tracks. |
| **Browser clip cache TTL of 10 minutes is unmeasured** | Accepted. Revisit if clips die in use despite the server fix. |
| **"Reset path" is hidden until a bypass is pressed** | Owner's call; one-line change if it proves undiscoverable. |
| **"New path" arrives with empty boxes if the path never loaded** | Accepted, won't fix unless it annoys in use — names come from the loaded path and do not exist before it. |
| **Zero-intermediary paths offer no bypass control** (F1) | Blocked on path work resuming; belongs with the min-length guard. |

**Carried, unchanged, not yet due:** drop-vs-backfill for the 33 nameless artists (owner,
at the rebuild seam); Gate 2 → 3 content curation (owner); `jesus2099` / entity-filter
coverage; the discovery report for non-artist entities.

**DISCHARGED 2026-07-25: `builder/README.md`.** Written, on the owner's instruction, at the
moment its condition came due. Three things worth recording about it:

- **It was never a doc-auditor invention.** It traces to Step 7 of
  `plans/2026-07-19-graph-builder.md`, an unchecked box in a plan the doc map marks
  COMPLETE. The real finding is that a *plan recorded as shipped had an unexecuted step*,
  and nothing noticed until an audit found the gap months later.
- **Its success condition had silently drifted.** The 2026-07-23 repair+retune log set it at
  "when `builder/` is next worked on substantively (Track 2's cap-strategy work, **if it
  ever runs**)"; the 2026-07-24 and 2026-07-25 handoffs restate it as "before Gate 1
  closes". Those are different triggers — the first is now behind the path-quality pause and
  would have deferred this indefinitely; the second is what made it due. **The later
  documents rewrote the condition without marking that they had.** A deferral's condition
  is as load-bearing as the deferral, and this one mutated in the copying.
- **It carries no figures, deliberately.** It defers to `BuilderConfig`, `CLAUDE.md` and
  `findings/` rather than restating. See §13 for a conflict found while writing it.

## 10. For the next session

- **Path-quality work is still paused.** Nothing here resumes it, and §6's third bullet is
  a trap, not an instruction.
- **PR #19 is open against `main` and not merged.** Merging is fine on the code; the
  use-the-app check is what tells you whether C1 and C2 actually worked.
- **Nothing is in flight.** One subagent (the closeout doc audit) was dispatched and
  completed; its findings are actioned in §11.
- **What I know that is not in the durable record: nothing.** Every judgement is either in
  §3, §4, or a code comment at the point of use.

## 11. Documentation audit (closeout B1)

Full report: [`findings/2026-07-25-doc-audit-gate1-clips-ux.md`](findings/2026-07-25-doc-audit-gate1-clips-ux.md).
Five findings. **Four actioned, one rejected**, plus two the audit missed that were fixed
anyway.

| Finding | Outcome |
|---|---|
| `docs/README.md` still said clips and UX "remain queued" | **Fixed** — now records them built, and fixed-not-closed |
| `docs/README.md` had no role marker in its first ten lines | **Fixed** — marked AUTHORITATIVE |
| `memory/clip-resolution-bugs.md` still read "do not re-investigate, just fix" | **Fixed** — the highest-risk item here, since memory auto-loads into every session and would have sent a cold session to redo shipped work |
| `2026-07-22-HANDOFF-phase1.md` §4 describes clips/UX as outstanding | **Fixed** — inline supersession mark. The top banner already scoped the file to §2–§3, but the doc map's own rule requires the inline mark, since a reader landing mid-document never sees a banner |
| `C1`/`C2` name four distinct objects | **No rename** — forward-only; committed documents stay frozen. Recorded as a hazard in §1 here and in the memory file. The audit's suggestion to namespace *future* clip items is sound and costs nothing to adopt when there is a next one |

**Rejected: expanding bare identifiers inside the `TEST-QUEUE.md` entry.** The audit
proposed inserting "C1 (does the clip play the artist on the card?)" into the owner-facing
steps. `closeout` C1 says the opposite in terms — **"Never name an identifier, file or
function in the steps"** — and the entry deliberately contains none in its steps. The three
line numbers cited contain no identifier at all. Following this would have broken the rule
it cited. Recorded because a future reader will otherwise see an unactioned finding and
assume it lapsed.

**Missed by the audit, found and fixed here:** `CLAUDE.md`'s orient table still named the
Gate 1 leftovers as the next action, and `MEMORY.md`'s index line still described the clip
bugs as merely diagnosed. Both are auto-loaded before any session reads a project document,
which makes them the two highest-consequence files in the sweep — and both were missed.
**The lesson is the one already in `closeout` B5:** the audit is a second reader, not the
only one, and the session still owes its own sweep of the auto-loaded layer.

## 12. Post-closeout addition: a failure-mode defect that endangered the check itself

**Added after this log's closeout, on the owner's question about starting the next phase in
parallel.** It is a Gate 2 Phase 3 item ("clip failures degrade to 204 rather than HTTP
500") pulled forward, and the reason is specific rather than convenience.

**What was found.** The API package contains exactly one `raise_for_status()` and **zero**
`try`/`except`, so any non-2xx or network error from either catalogue propagated out as a
500. Pre-existing — but the C2 work interacts with it twice, and both interactions were
introduced here:

1. **The cache-hit path used to make no network call and now makes one**, so the defect
   moved from firing on first resolution to firing on *every repeat view*.
2. **`resolve`'s documented self-heal did not work in production.** It falls through to a
   re-search only when `_preview_url` returns `None`; a withdrawn track is a **404, which
   raises**. The test modelled that case as a 200-with-error-body — a shape Deezer does
   produce — so it passed while the likelier path was broken. **Fixture not matching
   reality**, which is the failure class this project keeps hitting, committed fresh three
   commits after a closeout that had mutation-checked the same file.

**Why it could not wait for the queued check.** Deezer rate-limits; a path view fires 8–10
lookups; re-signing roughly doubles request volume for repeat views. A rate-limit during the
hour-long check returns non-2xx → dead card → **indistinguishable from "the C2 fix failed."**
The check would have been corrupted toward a false negative, and the owner would have had no
way to tell from inside the result.

**Fix.** A guard around the fetch call only — not the parsing, so a renamed field still
surfaces as a bug rather than masquerading as an outage. Five new tests; removing the guard
turns five red, including an app-level 204-not-500 assertion.

**Process note worth keeping.** The mutation check destroyed the fix mid-run: `git checkout
-- <path>` was used to revert a mutation, but the fix was still uncommitted, so the revert
took both. It was caught immediately by the suite and re-applied. **Mutation-testing
uncommitted code needs a copy, not `git checkout`** — the earlier rounds were safe only
because the code under mutation was already committed.

## 13. A conflict in the record, found while writing `builder/README.md`

Two committed documents disagree on how long a rebuild from the archive takes:

- `CLAUDE.md` (line 89): copy the archive and **"rebuild in ~30 s"**.
- `2026-07-25-HANDOFF-track2f-and-headroom.md` §5: the in-memory rebuild from the archived
  responses takes **about the same as the ladder's ~461 s**.

**RESOLVED 2026-07-25 by the closeout doc audit — they are different operations, and the
record already contained the evidence.** The repair-and-retune execution log's ORDERING
HEADROOM entry states that the in-memory rebuild called `serialise()` **only to hash, then
discarded the bytes**, and that `acceptance.py`'s rebuild block was therefore untouched. So
the ~461 s figure is the **analysis harness reconstructing the graph in memory for a
measurement**, not `artistpath-build build` writing an artifact. The two numbers were never
in conflict; nothing in either document said which was which.

**What is still unverified, and is a different claim:** whether `CLAUDE.md`'s **~30 s** is
accurate for the production CLI. Nobody timed it here. It is plausible and it is untested —
so it stays as a figure to check the next time anyone actually rebuilds, not as a known-good
number.

`2026-07-25-HANDOFF-track2f-and-headroom.md` §5 now carries an inline label so the ambiguity
does not spread from the document a successor is most likely to read.

**Method note.** The audit's reconstruction was checked against the cited line before being
accepted, and it turned out to support a *firmer* conclusion than the audit itself drew
("almost certainly different operations" → *definitively* different, since no artifact was
written). Subagent findings are evidence to verify, not conclusions to adopt — in both
directions.

## 14. Second closeout, run on the post-closeout increment

The increment (§12, `builder/README.md`, the WGLL passage) got its own pass rather than
riding on the first closeout's clean result. Four findings, all in this session's own work:

- **The log's sections were out of order.** §12 and §13 were inserted *before* §10 and §11,
  so the document ran 1–9, 12, 13, 10, 11 — and the `builder/README.md` discharge note
  pointed at "§12" for a conflict that had become §13. Fixed by **moving** the sections
  rather than renumbering them, because `TEST-QUEUE.md` cites "§12" and the owner-facing
  pointer should not move to accommodate an internal tidy-up.
- **`api/README.md` described the track endpoint's `204` as meaning "no clip available"**,
  which is now incomplete: `204` also covers a failing or rate-limited catalogue. A defect
  **of omission** — the sentence was true and had stopped being complete, which is the class
  a grep for wrong strings cannot find.
- **The roadmap still listed the 500→204 fix as outstanding Gate 2 work.** Struck through
  with the reason it was pulled forward, so a Gate 2 session does not plan it again.
- **The new guard's docstring restated a figure** (clip lookups per path view) that the
  roadmap's Gate-3 risk section owns. Converted to a citation at the point of use, per the
  rule that an inline hazard figure names the section that owns it so the next sweep
  re-checks it rather than skipping it.

**A4:** no config knob was added by the increment; the guard is unconditional, so nothing
sits at an old default. **B2:** the guard has four call sites, no orphan. **D6:** standing
context layer unchanged by the increment — `CLAUDE.md` net zero, `.claude/` untouched,
`memory/` still 412 lines.

**Session-state note, recorded because nothing else triggers on it.** Three slips in this
session, all mechanical rather than analytical, and the third is the one that matters:

1. §12's `git checkout` destroyed an uncommitted fix (caught by the suite, re-applied).
2. §12 and §13 were inserted out of numeric order in this file.
3. **§14 was then inserted out of order too — the same defect, ten minutes after fixing it
   and while writing the bullet describing it.**

Individually trivial and all caught. Together they are the completeness-failure signature
`CLAUDE.md` names as the degradation tell, and (3) is the clearest form of it: a rule this
session had just written down did not survive its own next edit. **No analytical error is
claimed or implied** — the work in §12 came from reading source, and the record is complete.
But this is the point at which a session should stop, and the owner had already decided the
next phase starts fresh. That decision is correct and this note exists so it is not
re-litigated as over-caution.

## 15. Live verification after merge — the server half works, the browser half does not

**Run after PR #19 merged, while starting the dev servers for the owner's check.** The first
contact this code has ever had with the real services, and it changed the picture in both
directions.

### What was verified working, live

Requesting the same artist's clip twice returns **the same track with a different signature**
— identical track id and title, different `exp` and a completely different `hmac`. That is
re-signing, observed rather than argued, and it discharges the weakest link this branch has
carried since it was written: the per-track lookup shapes were taken from published API docs
and had never been exercised. **They are correct.** The fresh URL was also fetched and
returns `HTTP 206 audio/mpeg`, so it genuinely plays.

Artist matching (C1) also confirmed live: the request returned Radiohead's own track.

### The measurement that changed things

**A Deezer preview signature is valid for 15 minutes.** Measured from the `exp` parameter
against wall clock, twice. The roadmap's confirmed-diagnoses C2 records a URL fetched at
09:41 and dead by 10:12 — consistent with 15 minutes, but it was read here as "somewhat
under an hour", and the browser-side TTL was chosen against that looser reading.

### The defect this exposed, which is in this branch's own work

`useClip`'s effect depends on `[mbid]`. **The 10-minute expiry therefore guards a remount,
never elapsed time on a card that stays mounted.** On a tab left open with no navigation the
effect never re-runs, so `JourneyList`'s `urls` — and through it the player — keep the URL
signed when the card was first drawn. At 15 minutes that URL is dead, and pressing play
reproduces the **original C2 symptom on a page whose server is already fixed**.

**Consequence: the queued hour-long check could not have passed**, and would have returned a
confident false negative attributing failure to the server fix. The queue entry is marked
BLOCKED for question 2; question 1 is unaffected.

**Why the tests did not catch it.** The browser test asserts that a *newly mounted* hook
re-fetches after the TTL, which is true and is what was implemented. Nothing asserts the
behaviour of a component that stays mounted across the expiry, because no test advances time
against a live component. The test was not vacuous — it tested the wrong span.

### What the fix needs, so the next session does not re-derive it

The URL must be fresh **at the moment of play**, not at the moment the card is drawn. Three
options, not chosen here — this is design, and it should not be settled by a session that has
already run two closeouts and recorded the degradation tell:

1. **Re-resolve on play.** The play handler fetches a fresh track, then plays. Direct and
   predictable; must also cover auto-advance on track end, which reads from the same list.
2. **Retry once on audio error.** Covers expiry generically and costs nothing in the common
   case, including the auto-advance path; needs the player seam to surface an error event.
3. **Periodic refresh.** Simplest, but fires for every card whether or not it is ever played,
   and multiplies requests against a service that rate-limits.

(1) and (2) are complementary rather than alternatives. (3) is the one to argue against.

**Standing constraint for whoever does it:** the dev servers are running for the owner's
question-1 check, and editing `frontend/src` hot-reloads his open tab.

## 16. The use-the-app result — C1 closes, and F1's deferral condition is found to have lapsed

**The owner ran question 1 on 2026-07-25.** Queue entry marked DONE there; this section is
the durable half.

### C1 is confirmed in use and closed

Two pieces of evidence, and they are of different strengths — recorded separately because
collapsing them would overstate the result.

1. **The owner's pass: nothing wrong found**, across every card he pressed play on. He
   recorded, unprompted, that **he could not remember which artists had produced wrong clips
   before.** So this is a broad "nothing jumped out", not a retest of the known failure —
   the same distinction the 2026-07-23 entry drew between its strong search result and its
   weak path result, and it is the honest reading.
2. **The targeted retest, run session-side against the live service.** The roadmap's §C1
   worked example is a band whose name is also a song title by a different artist; the old
   code took the first search hit and played the other artist's song. Resolved through the
   running API, the endpoint now returns a track **by the band**, which is precisely the
   result the roadmap predicts a correct implementation gives. Mechanical, so it did not
   need the owner's ear and was not left to it.

(2) is what closes C1: it exercises the documented failing case end-to-end rather than
sampling. Combined with §15's live confirmation that the per-track lookup shapes are correct,
**the "fixed-not-closed" deferral on C1 is discharged.** C2 is untouched by this — its
question is BLOCKED and its browser half is still incomplete.

### F1 was never fixed, and its due condition passed unnoticed

**The owner reported Radiohead → Weezer returning a two-card path with no artists between
them, and said he had thought this was decided unacceptable and fixed.** It was not.

- **Recorded 2026-07-23** as F1 in the repair+retune log's Track 1 results — a *new surface*
  exposed by the tie-break fix, not a regression.
- **Never fixed.** No min-length guard exists in shipped code; `api/` and `frontend/` contain
  no such symbol. §4 of this log decided against it explicitly: *"It is pathfinding, and
  pathfinding is paused."*
- **This work made it more visible without causing it.** Removing bypass from the start and
  end cards was correct on its own terms, but on a path with no interior artists it leaves
  **nothing on the page to press at all.** §6 predicted exactly this and the queue entry
  warned about it; the owner met it anyway and read it as a regression. That is worth more
  than the prediction: a case flagged in a document is not a case handled in the product.

**The defect in the record, which is the part worth keeping.** F1's due condition was
*"before Track 2's success criterion is finalised, since a min-length guard changes what the
sweep optimises."* **Track 2's pre-registration was committed 2026-07-23 and the sweep ran to
completion on 2026-07-24 without F1 ever being decided.** The condition came due, was not
discharged, and nothing fired — then the path-quality pause moved F1 behind a second gate
("blocked on path work resuming"), which reads like an intact deferral and is actually a
lapsed one re-parked under a new condition.

This is the **second** condition-drift found in two days: §9 records `builder/README.md`'s
trigger silently rewritten across three handoffs. Both survived because a deferral's
condition is copied forward as prose by whichever document restates it, and nothing compares
the restatement to the original. The mechanism is identified here; **no fix is proposed, and
inventing one is not this session's call.**

### Status of F1 after this — the requirement is DECIDED, the implementation is DEFERRED

**Owner's decision, 2026-07-25, verbatim: "every journey needs at least one stop."** He
called it unambiguous, and deferred the implementation with the path-quality pause left in
place.

This answers **the first half of F1's original 2026-07-23 instruction** — *"confirm 'a
journey needs ≥1 stop' as a requirement, then check whether Track 2 tuning makes direct paths
rare before adding a guard"*. The second half is now moot in its original form: Track 2 and
Track 2F both returned nulls, so no tuning is coming that could make direct paths rare, and
the guard is the only remaining instrument. **A zero-intermediary path is therefore a defect
against a stated requirement, not a candidate improvement** — a change of status, not of
priority.

**Success condition, written to survive restatement.** The previous condition lapsed silently
(above), so this one is anchored to an observable rather than to an event someone must
notice:

> **F1 is discharged when a path request between two directly-adjacent artists returns at
> least one intermediary, or returns an explicit "these two are neighbours" state that the
> UI renders deliberately.** Verifiable at any time by requesting `Radiohead → Weezer`; it
> currently returns two cards. **No document may restate this condition in other words** —
> cite this section instead. Both prior drifts happened in the restating.

**It is not blocked on the path-quality pause resuming.** The pause covers tuning the cost
function and rebuilding the artifact; this is a structural invariant over the result, which
is the distinction the 2026-07-23 entry drew when it called F1 *"a structural invariant, not
a tuning gradient"*. It is blocked only on the owner scheduling it. Recorded explicitly
because §4 of this log read it as inside the pause, and a future session will otherwise
inherit that reading.

## 17. C2's browser half — the URL is now signed at the moment of play

**Branch `clip-freshness-on-play`.** Closes the defect §15 found in this branch's own work.
Frontend only: no API change, no pathfinding, no graph, no config default.

### What was wrong, restated so the fix is checkable against it

A card resolved its clip once, on mount, and handed the resulting **signed URL** up to the
player, which held it for the life of the card. Signatures last 15 minutes; cards live as
long as the tab. So the player's copy rotted in place, and the 10-minute TTL guarding it
only ever fired on a *remount* — which is why the existing test passed while the real span
was unprotected.

### The change

**The player is given a resolver, not URLs.** `usePlayer(playables, resolveUrl)` now takes a
list of *which artists have a clip* plus a function returning a URL signed now, and calls it
at each start — press-play, and auto-advance on track end alike. `JourneyList` no longer
stores URLs at all; it stores availability, which is what it actually needed. `ArtistCard`'s
`onClipResolved` reports a boolean rather than a URL, so the stale value no longer exists to
be held.

**Plus a one-shot retry on audio error.** `Player` gained `onError`; a failure re-resolves
once and replays, then gives up rather than looping. §15 called these two complementary and
that is right for a specific reason now visible in the code: **`toggle()` must resume the
loaded source rather than re-resolve**, or a new URL resets the element and re-seeks to zero
— the exact regression the card-pause fix removed. So a clip that expires *while paused* is
not covered by resolve-on-play, and the error retry is what covers it.

**Option 3 from §15 (periodic refresh) stayed rejected**, on its own argument: it fires for
cards nobody plays, against a service that rate-limits.

### Two windows now, deliberately distinct

`CLIP_TTL_MS` (10 min) governs **display** — title and cover art, which do not expire.
`PLAYABLE_URL_MAX_AGE_MS` (5 min) governs **playback**. Splitting them is what lets the
player be strict without multiplying lookups for artwork. The 5 minutes is a judgement, not a
measurement, and is commented as such at its definition: it sits well inside the measured
15-minute signature, and shortening it costs request volume against a rate-limited service.

### Verification

TDD throughout — every test was watched failing first, and the five that mattered failed
because the resolver did not exist rather than because of a typo.

| Check | Result |
|---|---|
| Frontend suite | **52 passed**, 11 files |
| `npm run build` (tsc + vite) | **Pass** |
| `npm run lint` | **Pass** — only the pre-existing `vite.config.ts` warning |
| Snyk `snyk_code_scan` on `frontend/src` | **Pass**, 0 issues |
| **Mutation check** | **Both killed.** Widening `PLAYABLE_URL_MAX_AGE_MS` to 24 h killed exactly the two expiry tests and nothing else; removing the one-shot retry guard killed exactly the anti-loop test. |

**The test that matters is `JourneyList`'s "a card left mounted past the signature lifetime
re-signs before playing"** — it advances the clock against a component that stays mounted,
which §15 identified as the span no test covered. It is the one that fails if this fix is
ever undone.

### What this does *not* establish

**It has not been exercised against the live service.** The suite proves the browser asks
again; only use lands the whole chain. That is the queue's question 2, now unblocked — and
the same "fixture may not match reality" caveat that §15 discharged for the server half
applies here until it returns.
