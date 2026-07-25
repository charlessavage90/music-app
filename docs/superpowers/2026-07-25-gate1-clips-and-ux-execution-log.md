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

**Now approaching due:** **`builder/README.md` is missing** — condition is "written, or
explicitly declined, before Gate 1 closes", and Gate 1 is down to its last items.

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
