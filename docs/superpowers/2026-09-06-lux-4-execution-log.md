# `LUX-4` execution log — through the artifact, 2026-09-06

**Role: RETAINED EXECUTION LOG for `L4-T1`–`L4-T11` — the WHOLE plan. ACTIVE.** *(§1–§7 are
the first session's, through the artifact; §8–§13 were appended 2026-09-08 by the second, which
finished the plan. This line said `L4-T1`–`L4-T7` until then, and a reader who trusted it would
have stopped at the halfway point.)* Reasoning and corrections
only; git carries what each task did and the code carries how. **Owns no figures** — the
`LUX-4` payload and coverage figures live in
[`builder/analysis/2026-09-05-lux4-extract/README.md`](../../builder/analysis/2026-09-05-lux4-extract/README.md),
the artifact identity and `LUX-E5` in
[`builder/analysis/2026-09-05-lux-4-rebuild/README.md`](../../builder/analysis/2026-09-05-lux-4-rebuild/README.md),
and the drop-list drift in
[`builder/analysis/2026-09-05-lux-e1-drift-source/README.md`](../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md).
Cited by section, never restated.

Branch `lux-4-links-info-card`, PR #105. Handoff:
[`2026-09-06-HANDOFF-lux-4-artifact.md`](2026-09-06-HANDOFF-lux-4-artifact.md).

---

## 1. The decision that governed the session, and it was the owner's

**`L4-T1` was written to stop for an owner decision on the acceptance bounds. He overruled
the escalation itself**, and the rule he set is now recorded at both code sites and in the
plan:

> Moving a bound so a **new, never-served** artifact can be adopted is risk acceptance and
> his — that is what `MSW-` (`4b55144`) and `CXA-` (`c4cfbb1`) both were. Moving one to
> **re-admit the artifact already in production** is bookkeeping and a session's. The
> mechanical test: *is the new bound derived from something known independently of the build
> that went red?*

**This reversed a position taken earlier in the same session.** The plan escalated, and the
first message of this session escalated with it. His argument — bounds are a regression
tripwire, and a tripwire calibrated for a population that no longer exists is simply broken —
holds, and checking it produced §2's first defect.

**The same rule fired a second time, in the other direction.** The Deezer-id gap (§4) was
first written up as "the owner's call, and its own track". It is not: the fix is obvious, the
sequencing is methodology, and only the deploy needs his hands. Corrected in place at
`36a0696`, and the entry given a success condition rather than being left as a flag.

**Both are the same error** — transferring work while it looks like deference — and both were
caught by the owner rather than by the session.

## 2. Defects found in the plan itself — four, in four different ways

Every one was caught by checking against the repository, and none by reading the plan
carefully. **The remaining tasks (`L4-T8`–`L4-T11`) are unverified.**

> **⚠ FORWARD CORRECTION, 2026-09-08 — both sentences above have moved, and the section below
> is deliberately left as written.** There were **five**, not four: `L4-T10` claimed the
> frontend already mapped `snake_case` artists at the API boundary and it did not, which is
> **§8**. And `L4-T8`–`L4-T11` are **no longer unverified** — they were executed, each value
> they name grepped first, and the plan is finished. The warning was correct and load-bearing
> when written; it is discharged, not overturned.

| # | Task | The defect | How it would have failed |
|---|---|---|---|
| 1 | `L4-T1` | Named commit `3aa61f0` for the acceptance band. That is the **retired 75k map's** band and rejects the served map on **both** bounds. The correct source is `4b55144`, ten minutes later; the trap is that the live artifact's manifest records `git_commit: 3aa61f0` because the build ran there and the bounds moved right after. | Self-revealing — the failing test would have stayed red. Cost a cycle, not an artifact. |
| 2 | `L4-T2` | Said to reuse `dsp_ids.py`'s population. That is the union of the two **2026-08-02-era** artifacts, and the served map — built four days later from a later ALG-B crawl — has artists in neither. | **Silent.** Links and facts missing for 4.6% of every journey, with nothing going red. |
| 3 | `L4-T5` | Had `pipeline.py` project the maps onto node order. `build_graph`'s own docstring rules that out for `fame_lb_raw`: node ids are assigned *inside* it, so a caller pre-ordering re-derives `sorted(...)` and can silently disagree. `mbids` is not even in scope there. | Immediate — `NameError`. Also named `tests/test_pipeline.py`, which does not exist. |
| 4 | `L4-T7` | Its control arm reuses `armb_sha.py` and expects byte-identical. **`L4-T5`, in the same plan, made that impossible** — that script calls `build_from_archive`, which now wires the maps unconditionally. The factor table names an arm with "maps not wired"; once they are wired, no such arm exists. | The control would have failed on a **correct** artifact, and the plan says STOP on that. |

**The generalisable one is #4:** a plan's factor table can be invalidated by an earlier task in
the same plan. Nothing in the authoring rules catches that, because the table is checked
against the repository as it stood when the plan was written.

## 3. Decisions taken, with reasoning

- **`L4-T1b` was added to the plan.** A deferral's condition (*"before the `LUX-4` rebuild"*)
  had already fired once during `LUX-E1` and been recorded as unhonoured. The plan had no task
  for it. Discharged here rather than deferred a third time.
- **Recording, not refusal, for manifest mismatches** (owner, 2026-09-05). Noted at both sites
  that a gate here *could* fire in the first seconds — both inputs are known before any work —
  so the deferral's "kills a long build at the end" worry applies to the acceptance bounds and
  not to this check. The reason to wait is that a reflexively-reached escape hatch removes the
  protection it guards. **A session must not add the gate on its own.**
- **A new extraction script rather than editing `2026-08-02-dsp-ids/dsp_ids.py`.** Its outputs
  are pinned by `deezer_ids.py`; re-running it over a different population breaks the shipped
  map's reproduction claim. A frozen probe's value is that it is frozen.
- **`artist_facts` ships as a list of dicts, not parallel arrays.** Measured trade-off recorded
  at the contract point in `artifact.py`'s docstring. The dict shape lets a new fact skip six
  of the nine steps; it costs repeated key names per artist. **Revisit for `LUX-E6`** — the
  RSS multiplier, not the byte count, is what governs there.
- **Deezer ids deliberately NOT re-extracted.** Refreshing that key would change the
  artifact's existing `deezer_ids` and break `L4-T7`'s control arm, whose whole job is to
  prove this change touches nothing that already existed.
- **The two extraction payloads are gitignored** (owner, 2026-09-06). Nothing unique is lost;
  the cost is stated in the directory's `.gitignore` rather than left to be discovered.

## 4. Findings that are work, not notes — both with conditions

- **`ULC-F4`** — the un-listenable keep-check measures the **name** search while the app
  resolves by **identity** first (`clips.py` `_search`, shipped `aff8fb5`, three days *before*
  the census). Both drop lists therefore drop artists the app can play. **Owner's**; needs a
  re-census, a rebuild and its own pre-registration. Figures: drift-source README §6.
- **The Deezer id gap** — the shipped id map was extracted over a population predating the
  served map, so a slice of served artists can only resolve clips by name search, which is the
  `BYP-13` exposure. **A session's work.** *Condition: the first rebuild after `LUX-4`
  merges.* Figures and the expected recovery: lux4-extract README §4.

## 5. Corrections to the prior record

- **The dump is the 2026-07-29 export**, per its own `TIMESTAMP`, and is **CC0 1.0** per its
  own `COPYING` — no restriction on redistributing what is extracted. Every docstring here
  said "2026-07-28", a date carried forward from `dsp_ids.py`. Corrected forward only; the
  frozen probe is untouched. ⚠ **Not settled by that file: tag/genre data is supplementary
  rather than core, so its licence must be read from the tag dump's own `COPYING` before
  `LUX-E6` is scoped.**
- **The drift-source README's "nothing returns" is 0 by construction**, not evidence that
  HEAD's drop list is a strict refinement. On equal footing the reversals are near-symmetric.
  Corrected in §6 of the document that owns it.
- **Build cost: neither "~40 s" nor "~23 min" is usable.** Two rebuilds this session, both
  recorded in the rebuild README §5.
- **`test_pipeline_mirrors.py` had a hole that three changes have now gone through.** Its
  guard fires on a new `BuilderConfig` field; its docstring says outright that a stage added
  with *no* config knob slips past. `deezer_ids` (2026-08-02), `fame_lb` (2026-08-05) and
  `LUX-4` are all that shape, and none of the first two appears anywhere in that file.
  `RECORDED_METADATA_KEYS` now pins the emitted key set, with the per-mirror decision recorded.

## 6. Gate outcomes

| Gate / eval | Outcome |
|---|---|
| `L4-T1` acceptance gate | **PASSED** — the served map is admitted by its own bounds again, verified by a real build |
| `L4-T7` control arm | **PASSED** — byte-identical, using a replacement arm; the plan's own arm was unusable |
| `L4-T7` verification | **PASSED** — 16 checks, two independent families |
| **`LUX-E3`** | **RUN, descriptive.** Spotify ahead of Apple in every band → the feature is "both services" |
| **`LUX-E5`** | **PASSED** with large headroom. Nothing dropped; `area` stays |
| `LUX-E2` | **BLOCKED**, unchanged — damaged `TAS-` sample. Per-field population coverage is **not** a substitute read |

## 7. Operational measurements with no other home

- Three separate 17 GB extraction passes were run where one would have done. All three data
  defects were visible in a single survey of the value distributions after the first pass;
  each was found and fixed serially. **Survey a field's value distribution before writing its
  first consumer.**
- **Mutation testing at closeout (B3) found a vacuous test in this session's own work.** The
  acceptance-bounds table used three real artifacts, all of which fail the *edge* bound too —
  so widening the node band to admit every artifact ever built here left the test green. Three
  synthetic rows now isolate each bound; both mutations go red.
- `docs-lint` hard checks pass. Its `CAND` output is pre-existing threshold constants in
  frozen pre-registrations, none from this diff.
- **D6:** unconditional layer **51,694 characters** (from 51,656, **+38**); conditional
  **2,549 lines** (from 2,548, **+1**). Both deltas are corrections of statements that had
  become false by omission — `CLAUDE.md`'s APG1 key list and the `ml-graph-analyst` definition's
  metadata-blob description, the latter already stale since `fame_lb` in August. **Nothing
  net-new was added to either layer, so nothing there is owed to the owner.**

---

# `L4-T8` – `L4-T11` — the wire and the card, 2026-09-08

**A second session, cold, from the `L4-T7` seam.** PR #105 had merged, so all of `L4-T1`–
`L4-T7` was on `main`; this branched `lux-4-wire-and-card` off `origin/main` and is **PR #112**.
The `LBD-` track was live concurrently in a worktree at `C:\Users\charl\worktrees\music-app-lbd`
on `lbd-task3` — separate branch, separate index, no shared files, and nothing here touched
`NEXT.md`.

## 8. The fifth plan defect, and it was the same shape as the other four

The handoff's warning — *"the plan was wrong four times, in four different ways, and every one
was caught by checking against the repo rather than by reading carefully"* — held for a fifth.

**`L4-T10` step 6:** *"camelCase — the API layer already maps snake_case at the boundary; check
how `candidateCount` is mapped and follow it."* **It does not.** `client.ts` maps `Track`
(`candidate_count` to `candidateCount`) and `PathResponse` (`stop_rule` to `stopRule`), but
artists were **cast straight through** — `as Artist[]`, `as Artist` — which worked only
because no `Artist` field had ever been multi-word. `LUX-4` adds the first three.

**Why this one was dangerous rather than merely wrong.** Declaring `spotifyId` on `Artist`
while the object carried `spotify_id` compiles, passes every unit test that constructs an
`Artist` literal, and yields `undefined` at runtime — which `spotifyUrl` renders as a **search
link**, exactly as a genuine absence does. The failure is invisible in the only place anyone
would look. The four earlier defects announced themselves; this one would have shipped.

**Fix:** `ArtistWire` to `artistFrom` to `Artist`, applied at all four wire positions. Tests
pin the mapping, the `bypassed` path (its own code path, and the one that would drift alone),
and an api older than the frontend.

## 9. Two counts the plan got wrong in the safe direction

- **`ArtistOut` reaches the wire in FOUR positions, not three.** The plan names
  `PathResponse.artists`, `PathResponse.bypassed` and `GET /api/artists/{mbid}`;
  `GET /api/artists/search` is the fourth. `grep -rn "ArtistOut(" api/src/` returns **one**
  construction site (`app.py`'s `artist_out`), which is why all four are consistent for free —
  and that helper now carries a comment saying so, since the property is load-bearing and was
  undocumented.
- **`graph_store.py:70-71`** is the bounds check inside `deezer_id_of`, not the accessor's
  definition. Close enough to follow; recorded because the plan's line references are
  approximate throughout and a future reader should not treat one as exact.

## 10. Three deviations from the plan, all deliberate

| Plan says | Shipped | Why |
|---|---|---|
| `spotify_id(node)` / `facts(node)` | `spotify_id_of` / `apple_id_of` / `facts_of` | The file's one precedent is `deezer_id_of`. The bare form differs from the field `spotify_ids` by one character, and that typo yields a **truthy bound method**, not an error. |
| Tests in `test_graph_store.py` | `test_graph_store_lux4_keys.py` | Mirrors `test_graph_store_deezer_ids.py` and `test_graph_store_fame.py`, which is what the repo already does per additive key. |
| Accessors return `""` (copying `deezer_id_of`) | Return `None` | `deezer_id_of`'s `""` is consumed **inside** the api by the clip resolver, where it already means "fall back to name search". These three go **straight onto the wire**, where the contract is null-means-render-a-search-link. Normalising here keeps the frontend on one code path. |

## 11. The one thing tests could not have found

**The facts line truncated, and the life span was what it lost.** Every unit test passed, all
eight e2e passed, `tsc` and `oxlint` were clean — and a screenshot of a real journey at 390px
showed *"Person · United States · 1933–2…"* and *"English rock band · Group · Uni…"* on most
cards. The dates sit at the end of the natural reading order, behind the longest and least
useful field, so `truncate` ate precisely the most interesting fact.

**Rejected fixes, both for the same reason:** reordering the line so truncation eats the area
instead, and dropping `type` when a disambiguation is present. Each invents a ranking of which
facts matter, which is what `L4-D3` exists to decline. **Shipped:** the line wraps. It shows
all of it and costs one line on the cards that need it.

**The new e2e assertion was shown to go RED before being trusted** — restoring `truncate`
fails it, removing it passes. It measures `scrollWidth` against `clientWidth` in a real layout
engine; jsdom computes no layout, so a unit test here could only have asserted a class name
and would have passed either way (the `FMS-P1` / `TR-2` vacuous-check pattern).

**Reusable lesson, and it is §7's in a different medium:** §7 said *survey a field's value
distribution before writing its first consumer.* This is the rendering equivalent — **look at
the real thing on real data before believing a green suite about a visual change.**

## 12. Gate outcomes

| Gate / check | Outcome |
|---|---|
| api suite | **PASSED** — 288 |
| frontend unit | **PASSED** — 163 across 23 files |
| `tsc -b` + `vite build` | **PASSED** |
| `oxlint` | **PASSED** — one pre-existing `vite.config.ts` warning, untouched |
| builder suite | **PASSED** — 286, untouched by this work, run to confirm no regression |
| Playwright e2e | **PASSED** — 8, against the **real artifact** on `:8000` |
| `e2e/responsive.spec.ts` (TR-16, 390px) | **PASSED**, plus two new assertions in the same file |
| Artifact identity | **VERIFIED** — `graph-lux4.bin` sha256 `fd92a735…` matches its manifest sidecar, and `/health` reports the same |
| Snyk, `api/` | **CLEAN on this diff.** One pre-existing Low in `tests/test_origin_secret.py`, last touched 2026-08-06, untouched here and not fixed |
| Snyk, `frontend/` | **CLEAN on this diff.** Four findings, all in vendored `design/*/support.js` mockups, none in `src/` |

**Snyk was initially blocked** — expired credentials, MCP returning "User not authenticated"
and the CLI `SNYK-0005 401`, exactly as `NEXT.md` recorded. `L4-T9` was committed with the scan
named as **owed, not waived**; the owner re-authed mid-session and both scans then ran.

## 13. What is owed, and to whom

- **The owner's, and nothing here changes his order:** merge, then deploy, then the queued
  tests. **Two** test-queue entries are now live (2026-09-04 and 2026-09-08) and **both are
  blocked on the same deploy**, so they are one sitting. The `TEST-QUEUE.md` live count was
  re-counted rather than carried forward, per that file's own rule.
- **`LUX-E2` is still BLOCKED and this did not touch it.** `L4-D3` shipped by assertion, as
  the plan says it may. If `LUX-E2` later finds a field too sparse in the obscure half, the
  consequence is a **designed empty state in `ArtistInfo.tsx`, not a rebuild** — the artifact
  carries the data either way.
- **The Deezer id gap deferral has NOT come due.** Its condition is *the first rebuild after
  `LUX-4` merges*; no rebuild happened here.
- **Nothing was added to the standing context layer.** `CLAUDE.md`, `memory/MEMORY.md` and
  every skill and agent `description:` are untouched by this diff, so **D6 is zero and nothing
  is owed to the owner** for it.

## 14. Closeout figures and the checks that moved something

**D6, measured against `~/.claude/projects/C--dev-music-app/memory/`.** Unconditional
**51,694 characters — delta ZERO**, identical to §7's figure. Conditional **2,551 lines**
against §7's 2,549: **the +2 is NOT this branch's.** `git diff --name-only origin/main...HEAD`
returns nothing under `CLAUDE.md` or `.claude/`, and the two lines are in
`memory/working-style.md`, modified 2026-09-06 21:59 — outside git, after §7 was written, and
by another session. Attributing it here would have been the easy and wrong thing to record.

**B3 mutation testing — four mutations, all red, none vacuous.** Removing `spotify_id_of`'s
bounds check reddens 3 tests; leaking the in-band `""` instead of normalising to `None`
reddens 1; restoring the artists-are-cast-not-mapped code the plan assumed reddens 3 in
`client.test.ts`; restoring `truncate` reddens the new e2e layout assertion.

**B2 reachability** — every new module (`ArtistInfo`, `StreamingLinks`, `dspUrls`,
`ArtistFacts`) has an inbound import from production code. No orphans.

**B4 found one defect, in this session's own prose.** Comments said the three keys are absent
from artifacts built **before 2026-09-05**; `git log -S 'meta["spotify_ids"]'` puts the writing
commit at **2026-09-06**. Wrong by one day and in the misleading direction — it implied a
2026-09-05 artifact would carry them. Corrected in `graph_store.py` and the test docstring.
Small, and exactly the "confident prose about correct code" class this ritual targets.

**B1 — `docs-lint` hard checks passed; its CAND output is pre-existing threshold constants in
frozen pre-registrations, none from this diff.** `doc-auditor` then found **three live stale
status claims, all caused by this session's own append**: the execution log's own role line and
`docs/README.md`'s row for it both still said `L4-T1`–`L4-T7`, and the 2026-09-06 handoff still
claimed to be current. **A fourth was found by reading rather than by the auditor** — the
`LBD-` handoff's row cross-referenced the superseded `LUX-4` handoff as the other live track's
current note. All four fixed; a map row was added for the successor handoff.

**A4 is inapplicable and that is stated rather than skipped: this work added no config knob.**
`git diff origin/main...HEAD -- api/.../config.py builder/.../config.py` is empty, so there is
no default to flip.

**D2's condition is not met.** The APG1 keys are additive and `FORMAT_VERSION` stays `1`, so
the committed 500-node fixtures are not stale — and `tests/fixtures/graph-fixture.bin` loads
with all three lists empty and every accessor reading absent, which makes it a **real
pre-`LUX-4` artifact exercising the absence path**, not merely an untouched file.

**A5 — ports 8000 and 5173 are both free**, and deliberately so. Neither queued test needs a
local server: both exercise the deployed site.
