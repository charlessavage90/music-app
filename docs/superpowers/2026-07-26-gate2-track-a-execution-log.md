# Track A execution log — API hardening and telemetry, 2026-07-26

**Role: ACTIVE.** The retained execution record for Track A of the Gate 2 deploy design.
Identifiers **`TKA-`**, namespaced against `DEP-` (design), `TR-` (team review), `FMS-`,
`CLM-`, `STC-`, `DLV-`, `CNS-`, `SYN-`, `CWD-`, `MKS-`, `DRV-`, `BYP-`.

Governing documents: the plan
[`plans/2026-07-26-track-a-api-hardening-and-telemetry.md`](plans/2026-07-26-track-a-api-hardening-and-telemetry.md),
under the design [`specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](specs/2026-07-26-gate2-deploy-and-telemetry-design.md)
(its **§12 amendments govern**), which was corrected by
[`findings/2026-07-26-gate1-gate2-team-review.md`](findings/2026-07-26-gate1-gate2-team-review.md).

**Touches no routing weight, no cost-function term, no graph build.** The path-quality
pause is intact. `pathfinding.py` is not edited at all — Task 5's guards sit in `app.py`
and `models.py`.

**Branch** `gate2-deploy-and-telemetry`, PR #27. Executed **inline, not subagent-driven**,
per the plan header's own recommendation.

---

## Suite counts, per task

The plan fixes an exact expected count after every task. Every one was hit on the first
run; none needed explanation.

| Task | Expected | Actual | Commit |
|---|---|---|---|
| baseline | 153 | 153 | — |
| 1 — artifact bounds checks | 157 | **157** | `e904ea1` |
| 2 — load seam, `s3://`, checksum | 163 | **163** | `a73d333` |
| 3 — async clip cache | 164 | **164** | `99e942a` |
| 4 — cache/null-field 500s | 167 | **167** | `6f98b2a` |
| 5 — path input guards | 171 | **171** | `3bf7da2` |
| 6 — `/health` | 172 | **172** | `fe25964` |
| 7 — telemetry emitter | 178 | **178** | `8bebea2` |
| 8 — `path` event | 179 | **179** | `ed8c523` |
| 9 — `clip` event + browser id | 180 | **180** | `b950d1c` |
| 10 — round-trip verification | *(no code)* | — | — |

Final: **api 180, builder 115, frontend 65, e2e 3** — all green.

---

## `TKA-1` — the red run is the finding, not the green one

The plan's Global Constraints require every new test to fail against unmodified source
**and for the right reason**, because this plan's predecessor prescribed a check that
passed before any fix (`TR-2`, and `FMS-P1` before it). Recording what the red runs
actually said, since that is the part that cannot be reconstructed afterwards:

- **Task 1, truncation.** Failed with `Expecting ',' delimiter: line 1 column 89` — a
  `JSONDecodeError`. **That message does not contain "truncated".** Since `JSONDecodeError`
  subclasses `ValueError`, a `pytest.raises(ValueError)` would have passed here against
  unmodified source. This is `TR-2` reproduced under controlled conditions and avoided by
  matching on the message. **The corrected `DEP-10` is confirmed by observation, not by
  argument.**
- **Task 1, header/metadata disagreement.** Failed on the missing `from_bytes` rather than
  the plan's predicted "nothing raises at all" — same net effect, and it became the real
  check once `from_bytes` existed.
- **Task 4, null fields.** Failed with `Clip(title=None, cover_url=None)`. This is the
  evidence that `row.get("title", "")` does **not** fix it: the default applies only when
  the key is *absent*, and the catalogue sends the key with a JSON null.
- **Task 5.** The two real guards failed with 200; the two pinning tests
  (`unrecognised_reason`, `duplicate_exclusions`) passed before the change **by design** —
  they pin behaviour that is already correct.

## `TKA-2` — Task 3's verification is a deliberate, named exception

Task 3's step 2 predicts its own test may pass before the change, and it did. That is the
shape the Global Constraints forbid, so it is worth being explicit about why it is not a
recurrence: Task 3 is a **refactor with a characterisation test**, not a defect fix, and
the plan names this in advance rather than discovering it. The genuine failure surfaced at
step 4 as predicted — making the cache async with `resolve` not yet updated produced **nine
failures**.

**What the plan was right to insist on.** An un-awaited coroutine is truthy, so had
`resolve`'s two call sites been left to the tests, `if identity is not None` would have
taken the cache-hit branch on every request and — because `_get` swallows broadly —
degraded to a **silent card** rather than an error. Silent cards are this area's
characteristic failure and are visually identical across three unrelated causes.

## `TKA-3` — the broad cache guards were checked for over-reach

Task 4 wraps the cache calls in `except Exception`. The pre-existing test
`test_a_bug_in_our_own_parsing_is_not_swallowed` still passes, so the guard has not widened
into hiding our own errors — which is the standing worry in `clips.py`'s `_get` docstring
("a renamed field would look exactly like an outage").

## `TKA-4` — claims verified against source before executing

Per the plan's Global Constraints and `session-start`'s third check, every function, file
and config value the plan names was resolved before Task 1. All resolved: `_client()` at
`tests/test_app.py:13`, `make_store` at `tests/conftest.py:11`, `asyncio_mode = "auto"` at
`pyproject.toml:28`, `cdk.out/` already at `.gitignore:8`, `app.py:45` `allow_headers`,
`app.py:23-30` `_to_exclusions`, `graph_store.py:86-123` `load`.

Two that mattered more than a line-number check:

- **`GraphStore` is `@dataclass(slots=True)` and NOT frozen**, so Task 2's
  `store.source_sha256 = digest` is legal — but only because `source_sha256` is added as a
  declared field. Under `slots=True` an undeclared attribute would raise.
- **`pathfinding.py:88` returns `[source]` for `source == target`**, and `:189` labels a
  length-1 path `STOP_NATURAL`. So `DEP-13`'s "one-card journey labelled natural" is
  confirmed in source rather than taken from the design.

## `TKA-5` — the handoff seam at Task 6 was reached and not taken

The plan places a seam after Task 6 and says to retire the session there **if it is long**.
It was not: six tasks, all mechanical, every count hit first time, no degradation tell (no
dropped item, no figure re-requested, no firm claim revised under questioning). Continuing
was a methodology call, which is the session's to make. Recorded so the choice is visible
rather than implicit.

**This log was started at the seam rather than at Task 1**, which is a deviation from the
Definition of Done's "appended per task". The per-task commit messages carry the reasoning
in the interim, so nothing was lost, but the requirement is now met going forward.

## `TKA-6` — `DEP-16` is DISCHARGED: offline routing reproduces what the user was served

Task 10, run against the **adopted** artifact, booted through the production entrypoint.

**Identity gate first.** The service was booted with `ARTISTPATH_GRAPH_SHA256` **set** to
the adopted artifact's digest rather than left empty. That is stronger than the plan asks
for: it exercises the Task 2 checksum gate against the real file, and the service would
have refused to boot on a mismatch. `/health` then returned **all three values — digest,
artist count and edge count — matching** the manifest sidecar
`builder/scratch/graph-t15-tiebreakfix.bin.json` and the document that owns them,
[`findings/2026-07-23-tiebreak-fix-adoption.md`](findings/2026-07-23-tiebreak-fix-adoption.md).
**None of the three is restated here.** An earlier draft of this log restated the artist
and edge counts while explicitly noting it was withholding the digest — the one-figure rule
covers all three equally, and citing two of three is how drift starts (found at closeout
B1).

**The replay.** Two `path` events were emitted through the live API and replayed offline
through `find_journey` against the same artifact, comparing the full mbid sequence and the
stop rule. The replay script **read the events from the server's own log rather than
taking them as arguments** — transcribing them by hand is exactly the step that would hide
a mismatch.

| event | bypass depth | result |
|---|---|---|
| `verify-round-trip-01` | 0 | **REPRODUCES** |
| `verify-round-trip-02` | 2 (one `known`, one `dislike`) | **REPRODUCES** |

Both matched exactly, sequence and stop rule. **The second one is the one that matters**:
a zero-exclusion path would have verified only that the graph loaded, whereas the bypass
case exercises the exclusion resolution, the reason coercion and the dedupe that Task 5
changed. Journeys, for the record: `Radiohead → Coldplay → Adele → Amy Winehouse →
Norah Jones → Miles Davis`, and with two bypasses `Radiohead → Björk → PJ Harvey →
Tom Waits → Miles Davis`.

**What this licenses and what it does not.** It licenses using telemetry as a faithful
record of what the deployed router did — the design's §5 rests on production routing being
identical to analysis routing, and this makes that *checked* rather than assumed. It says
**nothing** about whether the paths are good; that is path-quality work and it is paused.

## `TKA-7` — gates and scans

- **e2e: 3 passed** against the live API (`DEP-30`). The Playwright `outputDir` move was
  effective — no `EPERM` on the OneDrive tree, which was `TR-17`'s concern.
- **`snyk_code_scan`: 0 issues** on `api/` **and** on `frontend/`. The frontend was scanned
  because Task 9 modified `client.ts`; the plan only names `api/`. No rescan was needed
  since nothing was found.

## `TKA-8` — two small deviations from the plan text, both recorded

Neither changes behaviour; both are noted so a reader diffing plan against code is not
puzzled.

1. **`import json` was added to `test_app.py`'s top import block**, not mid-file where the
   plan's Task 8 snippet places it.
2. **The frontend test uses `test(...)`, not the plan's `it(...)`.** The surrounding file
   imports `test` from vitest and uses it throughout; `it` was not imported. Matching the
   file's convention.

Also worth recording as a **non-event**: `crypto.randomUUID()` was flagged before Task 9 as
a possible failure under Vitest's jsdom environment. It worked. No shim needed.

## `TKA-9` — closeout B3: 14 mutations, 13 caught, and the survivor is a false comment

Every invariant this work added was mutated and the guarding test re-run. **Thirteen went
red.** Full list: the three APG1 bounds checks, the checksum mismatch, the journey-id
validation, `emit`'s use of `json.dumps` over string formatting, both cache guards, the
null-field coercion, the same-artist guard, the `exclude` bound, the exclusion dedupe, and
`/health`'s digest.

**One survived: dropping `count=` from `np.frombuffer`.** It is not a missing test — it is
an **unreachable guard with a comment claiming otherwise.** The total-length check runs
first and proves every subsequent slice is exactly the right size, so no payload reaching
`take()` can be short. The comment read *"count= is load-bearing"*; it is defence in depth.
Corrected in place, and the `count=` kept — it is what the code would degrade to if the
length check were ever relaxed.

**This is the `TKA-1` pattern pointing the other way.** There, prose understated what the
code did; here it overstated. Both were caught by execution rather than by reading, which
is the argument for B3 existing.

## `TKA-10` — the two APG1 parsers are still not equivalent, and the builder is now behind

Task 1's docstring claimed *"every bounds check here already exists in the builder's
writer."* **Checked against `builder/…/artifact.py` `deserialise` — false.** The builder
has the magic, version and truncation checks, which is the `TR-4` drift this task was
closing. It does **not** have the two checks that are new to both parsers: the **over-long**
case, and the **header-N vs metadata-length disagreement** (`TR-3`).

So `TR-4`'s "the parsers had drifted" is right about the direction and incomplete about the
extent: **two of the five checks were missing from both sides**, and `deserialise` still
lacks them. A header/metadata mismatch loads clean on the builder side today.

**Not fixed here, deliberately.** This reader is what serves users; the builder's parser is
used by offline tooling on artifacts it just wrote. Recorded with a condition rather than
carried as an unranked worry.

| deferred | success condition |
|---|---|
| `TKA-10` — `deserialise` lacks the over-long and `TR-3` consistency checks | closes when the builder is next modified for any reason, **or** when an artifact is next rebuilt — whichever is first. Accepted-won't-fix is a legitimate answer; the risk is confined to offline tooling. |
| `TKA-11` — the checksum gate ships **off** by default | `ARTISTPATH_GRAPH_SHA256` is empty unless set, and the design requires it *"in production"* with nothing enforcing that. Closes when **the CDK stack is shown in source to set `ARTISTPATH_GRAPH_SHA256` from the manifest sidecar**, re-checked by `DEP-33`'s review re-run before cutover. |

> **`TKA-11a` — the first success condition written for `TKA-11` was VACUOUS, and it was
> caught by running it rather than by reading it.** It said *"closes when Track C confirms
> `/health` returns a non-empty `graph_sha256`."* It cannot: `load_graph` computes the
> digest **unconditionally** and only the *comparison* is gated on `expected_sha256`, so
> `source_sha256` — and therefore `/health` — is populated identically whether verification
> ran or not. Observed directly at closeout A5, when a server started **without** the env
> var reported a full digest.
>
> **This is `FMS-P1` / `TR-2` for the third time in this project, and the first in a
> success condition rather than a test.** The pattern generalises past tests: any check
> that would pass in both the fixed and unfixed world is vacuous, and a deferral's closing
> condition is exactly such a check. Worth carrying into how conditions are written, not
> just tests.
>
> **Not fixed in code, deliberately.** Making `/health` report *whether verification was
> enforced* is a real option and would make the condition checkable over HTTP, but it is a
> new wire field decided during a closeout. Named here so Track B/C can take it
> deliberately.

**`TKA-11` is the A4 default-flip answer.** The knob's empty default is *correct* — local
dev and the whole test suite must boot without it — so this is not unshipped work wearing a
completion badge. But it is one forgotten environment variable away from being dead code in
production, and nothing would say so.

## `TKA-12` — `DEP-32` is blocked by `.gitignore` and Track B must fix that first

`DEP-32` requires `uv.lock` committed and `uv sync --frozen` in the Dockerfile, because
with no CI the image is the release artifact. **`.gitignore:18` ignores `uv.lock`, for both
packages.** So `DEP-32` as written is unsatisfiable until that line changes.

Recorded because this exact shape has bitten here before: closeout D1 notes a previous plan
that instructed staging `api/uv.lock`, was unsatisfiable as written, and ended with the
dependency pinned in `pyproject.toml` instead. **Track B's first task is the `.gitignore`
change, not the Dockerfile.** Found at closeout D1; not fixed here, because committing a
lockfile is a Track B decision with a Track B blast radius.

## `TKA-13` — closeout D6: the standing context layer

**In-repo half: net zero.** `git diff --stat main..HEAD -- CLAUDE.md .claude/skills/
.claude/agents/` is empty. Nothing was added to the layer that taxes every future session.

**Out-of-repo half: `memory/` totals 474 lines**, against **469** last recorded (`CLM-7`,
2026-07-26). The +5 was **not written by this session** — no memory file was created or
edited here. Recorded because D6 exists precisely to add the two halves together, and
`CLM-7`'s finding was that `memory/` grew with the delta recorded nowhere. Whatever added
those five lines did not record them either.

**One change was put to the owner and APPROVED: `CLAUDE.md` now lists
`ARTISTPATH_GRAPH_SHA256`.** The doc audit raised its absence as HIGH, and it was a real
defect of absence — the configuration section named three key API env vars and there are
now four, the new one being the only one whose absence silently disables a boot-time safety
check. Growing this layer is reserved to the owner; the cost and case were reported and he
took it. **Cost: +3 lines net** (the standing layer's only growth in this work; everything
else is net zero).

**`TKA-14` — what was NOT added, and why it is the more useful record.** The owner's first
instruction was to include the **literal sha256 value**. Weighing it surfaced that the
digest already appears in **52 files** — a fact that reframed the question rather than
settling it, and the session's initial "it would be recorded twice" was wrong.

**About 48 of those are executing assertions**, not restatements: the frozen probe scripts
under `builder/analysis/` each define `ADOPTED_SHA256 = …` and assert it against the loaded
artifact. Replication there is *correct* — each script pins its own provenance and fails
loudly if handed another graph — and CLAUDE.md protects those scripts as frozen records.
**So the one-figure rule was never the binding constraint.** The question was whether to add
the first copy of a **different kind**: one read by a human and retyped into a production
config, executed by nothing.

Three arguments carried it, and they are worth keeping because the same choice will recur
at every future adoption:

1. **A checksum compared against a copy is not a check.** Its only correct use is comparison
   against an independent source; two hand-maintained copies guarantee someone eventually
   verifies the wrong pair.
2. **A rebuild splits the copies three ways.** The ~48 frozen scripts *should* keep the old
   digest; the adoption record and sidecar *must* change; `CLAUDE.md` would become the only
   must-update copy with nothing forcing it.
3. **The realistic failure is not the loud one.** A stale digest refuses to boot during a
   cutover — then someone "fixes" it by clearing the env var, and verification is off in
   production silently and permanently. That is `TKA-11` realised, and `DEP-24` exists
   because `TR-9`/`TR-10` flagged hand-transcription as its cause.

**What landed instead is the retrieval instruction, not the value** — same line cost, and it
stays true across every rebuild rather than going stale at the next one.

---

## Owed at completion

- [x] `snyk_code_scan` clean on `api/` and `frontend/` — `TKA-7`.
- [x] `DEP-16` discharged by Task 10 — `TKA-6`.
- [x] Four suites green: api 180, builder 115, frontend 65, e2e 3.
- [x] This log, appended per task from the Task 6 seam onward (`TKA-5` records the
      late start).
- [ ] PR #27 updated.
- [ ] Use-the-app queue entry. **This is the first app-facing Track A change in a while**
      and it deserves a real entry rather than an N/A: three of the six defect fixes are
      reachable by an ordinary user (`from == target` now refused, cache blips no longer
      500 a card, null catalogue fields no longer 500 a card).

**Next: Track D** (frontend, six fenced items) — and the plan is explicit that **Track D is
the condition that reverses the inline recommendation**: it is largely independent work
across different files, so subagent fan-out is the better call there. Then Track B
(infrastructure), then Track C (cutover). **`DEP-33` requires the team review to be re-run
against the CDK stack before cutover** — seven of its findings concern a design rather than
code.
