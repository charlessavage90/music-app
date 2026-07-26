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

---

## Owed at completion

- `snyk_code_scan` on `api/`, per the global instruction, once first-party code is
  modified — it is. Findings fixed and rescanned until clean.
- Task 10's telemetry round-trip against the real graph, discharging `DEP-16`. **If it does
  not reproduce, that is a finding and telemetry cannot be used for any conclusion** — not
  a bug to work around.
- The e2e suite as a mandatory gate (`DEP-30`).
- A use-the-app queue entry, and PR #27 updated.
