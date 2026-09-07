# `LUX-4` execution log — through the artifact, 2026-09-06

**Role: RETAINED EXECUTION LOG for `L4-T1`–`L4-T7`. ACTIVE.** Reasoning and corrections
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
