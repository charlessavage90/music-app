# `LUX-1`/`LUX-2`/`LUX-3` execution log — retained

**Role: RETAINED EXECUTION LOG** for `docs/superpowers/plans/2026-09-04-launch-ux-1-3.md`
(governed by `docs/superpowers/specs/2026-09-03-launch-ux-scope.md`). **Owns no figures and no
status.** `LUX-E4`'s numbers belong to
`builder/analysis/2026-09-04-lux-e4-candidate-counts/README.md` — cited below, never restated.
Status lives in `NEXT.md`, not here.

**Why this file exists.** The session that ran this plan kept a detailed ledger
(`.superpowers/sdd/2026-09-04-launch-ux-1-3/progress.md`) recording every ruling and deferral as
it happened. That directory is gitignored and dies with the session — this repo's own
convention (`CLAUDE.md`, "retained execution log") is that a ruling worth making is worth
keeping past the session that made it. This document distils that ledger into the permanent
record. The final whole-branch review flagged its absence as finding **I4**; this file is the
fix.

Branch: `launch-ux-1-3`. Seven tasks (`LUX-T1`–`LUX-T7`) shipped one bypass control, the
skipped-artists panel (frontend, then on the path response), a "try another track" control, and
one pre-registered measurement (`LUX-E4`). Model policy for the whole run (owner, 2026-09-04):
subagents default to Sonnet, Opus only with a clear reason — used once, below.

---

## 1. Every ruling, in the order made

Each ruling below carries what it costs **if it turns out to have been wrong** — none of them
were, but that was not knowable at the time each was made, which is the point of writing the
cost down before finding out.

**PF-1 — the plan's two task chains are not independent; execute strictly in order.**
The plan's Handoff section claimed `LUX-T1`–`T3` and `LUX-T4`–`T6` "share no file" and could run
in parallel. False: `LUX-T6` edits `ArtistCard.tsx`, `JourneyList.tsx` and `ArtistCard.test.tsx`,
all three of which `LUX-T1` also edits. **Decision:** execute strictly `T1→T2→T3→T4→T5→T6→T7`
and never run two tasks in parallel; the plan's Handoff paragraph was corrected in the same
commit as `LUX-T6`. *Cost if wrong:* none to correctness — this is strictly more conservative
than the plan and only forgoes parallelism the plan wrongly advertised.

**PF-2 — `LUX-T4` alone leaves the api suite red; it needs a temporary bridge.**
`LUX-T4` changes what `ClipResolver.resolve()` returns, and `app.py`'s only non-test caller is
not updated until `LUX-T5`. The plan's `LUX-T4` Step 6 claimed the suite would pass; it would
not have. **Decision:** `LUX-T4` carries a two-line bridge in `app.py` (read `.clip` off the new
`Resolution`, keeping behaviour identical) that `LUX-T5` replaces with the real index/count
wiring, rather than merging the two tasks into one dispatch (which would have put the cache
rewrite and the endpoint change on one review surface, and `LUX-T4` was already the plan's
largest diff). *Cost if wrong:* a throwaway two-line edit in `LUX-T4` that `LUX-T5` overwrites —
harmless either way.

**PF-3 — the plan's own test code names helpers that do not exist.** `LUX-T4`'s illustrative
tests call `make_resolver(deezer_rows=…)`; the real helper is `_resolver(responses, cache=None,
breaker=None)` in `test_clips.py`. `LUX-T5`'s tests name `MBID_WITH_CLIP`, which `test_app.py`
does not define. **Decision:** the plan's test code is illustrative of intent, not literal —
implementers adapt each test to the host module's existing fixture style, preserving the
assertion and the docstring exactly, since those carry the intent. **This wave additionally
corrects the plan text itself** (§ below, "the plan is an active document, not a frozen
record") rather than leaving the correction only in the session ledger. *Cost if wrong:* a
reviewer flags a test that reads differently from the plan; the assertion is what matters and
is preserved either way.

**Task 1 — the two-button-era text in two frozen files is correct as written and must not be
"fixed."** `frontend/design/2026-08-07-bypass-tray/*.dc.html` (a design mockup) and
`builder/analysis/2026-07-23-f6-trace-capture/resolve_trace.py:149` (a probe script that must
keep reproducing its own committed figures) both still describe two bypass signals.
**Decision:** leave both alone. A frozen artifact's value is that it is frozen — it records what
was true when it was written, not what is true now. *Cost if wrong:* two files keep text that
correctly describes the era they belong to, which is not a cost.

**Task 2 — fix the "transport failure mislabelled as not-in-graph" defect immediately, rather
than parking it because `LUX-T3` deletes the file it lives in.** `useBypassedArtists` (the
`LUX-2a` hook, deliberately temporary) cached a network timeout identically to a 404 in a
module-scope cache that never invalidates, permanently mislabelling a real, present artist as
"no longer in the map" for the rest of the session. `LUX-T3` structurally removes the ambiguity
(the server becomes authoritative), so the defect has a one-task lifespan and — since `LUX-T2`
and `LUX-T3` land in the same PR — can never reach a deployed user. **Decision:** fix it anyway
(~8 lines, using the `ApiError.status === 404` distinction `client.getArtist` already exposed).
Two reasons: a commit would otherwise stand in history where the app states something false to
a user about a real artist, and "the next task deletes it" is exactly the reasoning that leaves
a defect in when the next task slips. *Cost if wrong:* one fix round spent on code that the very
next task deletes anyway — bounded and small.

**Task 4 — this one review runs on Opus, against the standing Sonnet default.** Clear reason,
per the owner's "Opus only with a clear reason": `LUX-T4`'s diff restructures a **production**
clip cache with a 30-day TTL and the code talking to two rate-limited external catalogues. Its
failure modes are the kind a green suite does not show — a signed URL reaching the cache and
later serving dead audio, a cold path quietly costing two round trips, or a breaker interaction
that converts a rate-limit into hammering. Every other review in this plan stayed on Sonnet.
*Cost if wrong:* one more expensive review than strictly needed, spent on the plan's riskiest
diff — a low-cost way to be wrong.

**Task 4 — promote the reviewer's Minor #5 (no candidate de-duplication) and fix it in the same
round, on the spec's authority rather than the plan's.** The task reviewer classified missing
dedup as a Minor outside `LUX-T4`'s brief, which is correct reading the brief alone. But the
**spec** governs where the two disagree, and spec §3's decision reads "let a user try a
**different** clip by the same artist" — a duplicate is not a different clip. Two concrete
harms decided it: (a) the name-search path (used for artists with no recorded Deezer id — a
population that skews obscure, i.e. exactly who the app exists to serve) can return one
recording several times under different track ids, so "try another track" could replay the same
song; (b) undeduplicated counts would inflate `LUX-E4`'s measurement of how many cards can offer
another track, and that measurement's threshold is a re-prioritisation trigger that is the
**owner's** call — a measurement feeding an owner decision must not be knowingly inflated.
*Cost if wrong:* a small amount of work beyond the plan's letter, and a dedup rule that could in
principle merge two genuinely distinct recordings that happen to share a title (see §2 below —
this was accepted, not overlooked).

**Task 4 — defer the `_dedupe_by_title` docstring gap to this final wave rather than spending a
second fix round on it.** The docstring documented only the risk of over-merging distinct
recordings, not the more common opposite gap (title-folding does not strip bracketed suffixes,
so "Song" and "Song (Remastered 2011)" survive as two candidates) — a defect of *absence*, which
`CLAUDE.md` names as the kind no grep can find. **Decision:** batch it into the final
whole-branch review's single fix wave rather than a fourth one-line round. *Cost if wrong:* the
gap stayed undocumented until this wave, entirely within the same unmerged branch — now
discharged (see §2 below).

---

## 2. Deferred findings and their success conditions

Some of these were fixed in this wave; they are listed anyway so this file is the complete
record of everything that was ever open, not just what is still open.

| Finding | Status after this wave | Success condition for revisiting |
|---|---|---|
| `decodeExclusions` does not dedupe an id appearing in **both** the `dislike` and `known` lists (a hand-edited legacy URL could emit two `<li>` with the same React key). | **Still open, not reachable by pressing anything** in the current UI. | Revisit only if a legacy two-list URL is ever observed producing a duplicate row, or if `exclusions.ts` is touched for another reason first. |
| `unresolved` was not deduplicated the way `bypassed` is (a hand-built request repeating one bad id yielded a duplicate React key and a redundant panel row). | **Fixed this wave** — `_to_exclusions` in `api/src/artistpath_api/app.py` now dedupes `unresolved`, preserving first-seen order, with a new test. | Closed. |
| The test-name-promises-more-than-the-assertion defect in `test_the_track_endpoint_reports_how_many_candidates_exist` (`api/tests/test_app.py`) and in `test_the_candidate_list_is_cached_so_a_second_index_costs_no_search` (`api/tests/test_clip_identity.py`). | **Fixed this wave** — both now assert the thing their names promise, proven red/green for the first. | Closed. |
| The `_dedupe_by_title` docstring documented only the over-merging risk, not the bracketed-suffix gap. | **Fixed this wave** — one sentence added; behaviour unchanged. | Closed. |
| The ambiguous "candidate 2" comment in `clips.py` (index 1, or the second item?). | **Fixed this wave** — reworded to "the second candidate". | Closed. |
| Twelve stale two-signal-era comments and two READMEs describing a tray/two buttons that no longer exist. | **Fixed this wave.** | Closed. |
| `_fold` does not strip bracketed suffixes (**behaviour**, not the docstring that describes it). | **Deliberately NOT fixed.** The bound may be what the owner wants — collapsing "Song" and a genuinely different live/alternate recording sharing that exact title is also a risk, and this wave was not asked to re-litigate the trade-off. | Revisit if a user reports "try another track" handing back the same song again. |
| The Dynamo shape check (`_get_sync`) guards the container (`"tracks" not in item`) but not the four payload keys inside each track entry. | **Deliberately NOT fixed.** A missing key degrades to a cache miss on that read, which is the correct, fail-safe behaviour — the aperture is wider than the pre-`LUX-3` check but the failure mode is identical in kind. | Revisit only if a malformed Dynamo item is ever observed to raise rather than degrade to a clean miss. |
| No test exists for "the same artist bypassed twice." | **Deliberately NOT fixed** as its own test. Behaviour was traced from source by two independent reviewers and is correct (the artist appears once, since `by_node`/`order` in `_to_exclusions` already dedupe per node). The coverage that actually matters — that the panel renders correctly at all from real path state — is `PathPage.test.tsx`'s new bypassed-artist test (this wave, item 16 of the final fix wave), which no level of testing exercised before. | Add a dedicated "same artist twice" test only if this exact path is ever implicated in a real bug report; the traced-correct behaviour does not currently justify one. |

---

## 3. ⚠ Operational note for the deployer — read before deploying this branch

**On deploy, every existing item in the live clip cache becomes a miss at once**, because the
DynamoDB item shape changed (`LUX-3`: a single flat track became a `tracks` list). The **first**
view of each artist after deploy therefore costs a Deezer **search** rather than a cheap
`/track` re-sign — the same number of external calls per card, but against a rate-limited
catalogue rather than a cheap re-sign endpoint, so the practical cost is higher even though the
call count is unchanged. Item size in the table also grows, up to `clip_search_limit`× the old
size (candidates are now stored as a list rather than one flat record).

**No infrastructure change is needed.** The table is `PAY_PER_REQUEST` (no capacity to
provision), TTL-keyed on `ttl` (the old shape drains itself in `clip_ttl_days`, unaided — there
is deliberately no migration), and the IAM grant is only `GetItem`/`PutItem` (no schema
change to authorize). **This is spec-sanctioned, not a defect** — §3's own precedent for the
cache-shape change is "pre-`C2` items are treated as a miss and overwritten; use it, do not
write a migration," and `LUX-3` follows that precedent deliberately.

This belongs on `TEST-QUEUE.md` or an equivalent pre-deploy checklist so a deployer sees it
before, not after, flipping the switch — it was otherwise nowhere a deployer would look.

---

## 4. Snyk — owed and undischarged

Per `CLAUDE.md`, `snyk_code_scan` is owed over new/modified first-party code in a
Snyk-supported language — which covers every `api/` file this plan touched
(`app.py`, `clips.py`, `models.py`) and this wave's further edits to the same files.
**`snyk_code_scan` is unauthenticated in this environment** ("User not authenticated. Please run
'snyk_auth' first") and authentication is an interactive browser flow that is the repo owner's
to run, not a session's. This was verified directly against the tool at Task 1 and remained true
for every task and for this final wave — it is the **only** such gap across the whole branch.
**Action owed:** the owner runs `snyk_auth`, then a session runs `snyk_code_scan` over
`api/src/artistpath_api/` (`app.py`, `clips.py`, `models.py` at minimum) and fixes anything it
reports.

---

## 5. The shared-link contract — traced end to end, and intact

The branch's most load-bearing external promise is that a link shared before `LUX-1` shipped
keeps resolving exactly as it did. Traced hop by hop on the final tree, across all commits in
this branch and this wave's additional edits:

- **`frontend/src/lib/exclusions.ts` has zero diff across the entire branch.** `decodeExclusions`
  still reads both `?dislike=` and `?known=`; `addExclusion` still writes whichever reason it is
  handed.
- **`api/src/artistpath_api/pathfinding.py` has zero diff across the entire branch.**
  `avoidance_map()`, the two `floor_relax_*` values and `w_known_ramp_fame_pctl` are all
  untouched — the `dislike` mechanism still exists and still behaves exactly as before, only the
  UI control that could produce it is gone.
- **`models.py`'s `reason` field stays a bare `str`, not a `Literal["known"]`** — narrowing it
  would have made `dislike` a validation error rather than a still-honoured wire value, silently
  breaking every link that carries one.
- **The new `bypassed` ordering (`LUX-2b`) is reason-agnostic.** `_to_exclusions` orders by press
  order regardless of which reason a press carried, so a `dislike` exclusion reaches the new
  route-history panel exactly as a `known` one does — there is no code path that treats the two
  reasons differently once bypassed.

Regression coverage exists at every layer for this claim (`exclusions.ts`'s own tests,
`test_app.py`'s exclusion tests, and the e2e `known=` URL assertion in `path.spec.ts`). No
finding in this branch, in any task review, or in the final whole-branch review touched this
contract.

---

## 6. Cross-references

- Plan: `docs/superpowers/plans/2026-09-04-launch-ux-1-3.md` (this wave corrected its `PF-3`
  gap and added the candidate-dedup note — see that document's Handoff section).
- Spec: `docs/superpowers/specs/2026-09-03-launch-ux-scope.md` (this wave added a `⚠` at §5
  pointing at `LUX-E4`'s figures README, described qualitatively — see §5.4 there).
- `LUX-E4` measurement, figures owner: `builder/analysis/2026-09-04-lux-e4-candidate-counts/README.md`.
  **Cited, never restated**: the pre-registered threshold could not be read (its denominator was
  empty — the router delivered no lower-half artist onto any card at all in the sample run), and
  that same run found the underlying 120-pair `TAS-` sample damaged on the currently-served map,
  with the attrition concentrated almost entirely on the two obscure pair classes. Both facts are
  qualitative and load-bearing for anyone planning `LUX-4`; neither is a number, so neither is
  restated further than this.
