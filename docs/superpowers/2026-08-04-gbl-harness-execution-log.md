# `GBL-` harness execution log — 2026-08-04 (later)

**Role: COMPLETE.** The reasoning behind building the gentle-arm blind listen harness
(plan Tasks 1–8). Companion to
[`2026-08-04-gbl-planning-execution-log.md`](2026-08-04-gbl-planning-execution-log.md),
which covers the design of the same listen and is **not** superseded by this — the two
cover different chunks of work.

**Owns no figures and no status.** Status lives in [`NEXT.md`](NEXT.md). The `CRE-`
figures this listen follows from live in
`findings/2026-08-04-cap-reevaluation-results.md`, cited and never restated.

**The listen has NOT been run.** This log covers building the instrument only. No journey
was generated on either arm, `gbl_generate.py` has never been executed, and no verdict
exists.

---

## 1. What this session was, and what it deliberately did not see

Executed the committed plan inline (`executing-plans`), on branch
`gentle-arm-blind-listen`, per the owner's model ruling recorded in the planning handoff.
Eight tasks, one owner gate at Task 3, one handoff seam after Task 8.

**The seam is the load-bearing constraint on everything below.** The plan bars this
session from running generation against the real artifacts, because a session that has
seen the candidate arm's journeys cannot then write an honest instrument for judging them
blind. Every consequence of that constraint is recorded in §5; it is the single largest
piece of residual risk this session hands forward, and it is deliberate rather than an
oversight.

## 2. Defects found in the governing documents

### 2.1 `GBL-CORR1` — the spec's §5 branch table carried the pre-scaling bar

Found during orientation, before any code existed. §5's prose, its worked examples (9–4
fires, 10–6 does not) and its arithmetic (16 × 0.3 = 4.8, rounded up) all carried the
scaled **≥ 5**. The branch table three lines below still carried **≥ 3 / ≥ 3 / < 3**, left
behind when the owner scaled the workload from five pairs to eight at his pre-run review.

A reader consulting the table alone would have read 10–6 as firing — against the spec's
own worked example, in the document that governs wherever the plan disagrees.

**Corrected on the owner's instruction** as `GBL-CORR1`, in a `GBL-CORR` series kept
deliberately disjoint from `GBL-AM`: it moves no bar, and calling it an amendment would
misrepresent a transcription fix as a design change. Made before any journey existed and
before any listen, so no result could have shaped it.

**Now defended mechanically:** `test_gbl_unblind.py` pins 8–5 as the null and 9–4 as a
fire. The code and the table cannot drift apart again without a red test.

### 2.2 Six defects in the plan's own code

The plan carried complete code per task, and six pieces of it were wrong. All are
methodology or correctness, none changes what the listen decides, and each is recorded at
its commit. Two are worth reading:

- **The blind guard would have aborted on a band name.** `assert_page_data_clean`
  substring-scanned the whole page document for `"ramp"`, `"arm"` and `"candidate"`. Those
  appear inside real artist names — The Cramps, Louis Armstrong — and the runner brief
  forbids working around a gate, so a single unlucky interior artist would have stopped the
  listen with a message about arm identity leaking. Replaced with a strictly stronger
  guard: an exact key-schema check (an undesigned field fails on its own merits, whatever
  it holds) plus the substring scan over the structure the module writes, with
  graph-supplied names blanked first. Regression test uses The Cramps.
- **The ear-tracking table would have flattered the arm under test.** `ear_tracking`
  counted a row where one side had no measured interior as simply not-`fame_lower`, which
  reads as *the picked side was not less famous*. The truth is *we could not tell*. The
  censoring blind spot (`CRE-` findings §3) is live and falls hardest on exactly the
  journeys that dig deepest, so the miscount was biased rather than merely noisy. Fame rows
  now carry their own denominator (`fame_rows` beside `fame_lower`).

The other four: the page interpolated MusicBrainz artist names into `innerHTML` (names
carry quotes, ampersands and angle brackets; one containing `</script>` would have served
a blank page); the frozen `GBL-Q1`/`Q2` wording was split across JS string concatenation,
so it did not appear verbatim in the served page and the frozen-wording test silently
tested nothing; the Deezer test fixture read the cover from `album.cover_medium` where the
real parser reads `artist.picture_medium`, so the test passed while the field came back
empty; and `gbl_pairs.py` had an `or "none"` precedence bug making a fallback unreachable
plus an unguarded `sys.path.insert` running once per artist.

**The pattern worth carrying forward:** four of the six were *tests that would have passed
while testing nothing*, which is this project's named characteristic failure. The plan's
own self-review section asserted type consistency between its code and its tests and was
correct about that — type consistency is not the property that was violated.

## 3. Decisions taken

### 3.1 The hub set is frozen on V0 and carried by MBID

**Reversed the plan.** It computed `top_degree_node_set(store, 0.01)` per arm.
`path_metrics`' own docstring requires a *frozen* set rather than a per-graph threshold,
because the top-1%-by-degree cutoff moves between builds and a per-arm threshold lets an
arm score better purely by compressing its degree distribution. Node ids are not shared
between two different artifacts at all, so the two per-arm sets were not comparable in the
first place — and `ear_tracking` compares `top1pct_degree_frac` and `payload` **across**
arms, which is precisely the comparison that needed them comparable.

Now derived once on the adopted artifact and mapped into each arm by MBID; MBIDs absent
from an artifact drop out. Spec §7 does not pin the derivation, so this sat in the
session's column rather than the owner's. **It affects the §7 ear-tracking table only and
decides nothing.**

### 3.2 The remaining Snyk finding is accepted, not silenced

Two LOW path-traversal findings (`python/PT`, CWE-23), both `--export` reaching a read.
One fixed: the export directory is resolved and directory-checked, the two leaf filenames
are module constants input cannot reach, and the join is checked for containment. Re-scan
2 → 1.

The survivor is accepted with the reasoning and a **revival condition** written at the
function itself rather than in a document nobody will open: reading a directory the
operator names at the command line is what the script is *for*, and spec §3 requires that
directory to live outside the repo, so there is no safe root to confine it to. It goes
live again the moment that path arrives from anywhere but the operator's keystrokes.

Re-running against the real export after the refactor produced **byte-identical outputs** —
the determinism check that makes "behaviour-preserving" an observation rather than a claim.

### 3.3 Considered and dropped: validating pair feasibility before the gate

Three of the owner's eight pairs are his own recombinations, and nobody has checked that
any pair produces a journey with enough interior room to judge at depth 20. Checking means
generating, and generating before `GBL-AM1` was committed would have let journey shape
influence pair selection — the exact contamination the pre-registration ordering exists to
prevent.

**Dropped deliberately.** The residual is covered rather than eliminated: generation's
run-state gate refuses to proceed and names any pair that cannot reach all three depths on
both arms, so an unusable pair surfaces before the listen rather than during it. The owner
was told this at the gate.

### 3.4 Considered and dropped: running generation "without looking"

Weighed, because it would have retired §5's residual entirely. Rejected: the artifacts it
writes (`gbl_page_data.json` in the repo, the sealed file outside it) are the listen's own
inputs, the seam assigns their creation to the runner session on listen day, and clip URLs
expire so generation belongs near the listen anyway. Working around a constraint because
it is inconvenient is the move the whole blind protocol exists to make hard.

## 4. Gate outcomes

| Gate | Outcome |
|---|---|
| **Task 3 — owner gate**, pair approval | **PASSED** 2026-08-04. Eight pairs approved; `GBL-AM1` committed with the file's sha256, before `gbl_generate.py` had ever run. |
| Harness test suite (30 tests) | **PASSED.** |
| `scripts/docs-lint.sh` hard checks | **PASSED.** |
| Snyk code scan | 2 LOW → 1 fixed, 1 accepted with a revival condition (§3.2). |
| **The five generation gates** — artifact identity, V0 mirror fidelity, ramp decomposition, arms-genuinely-differ, run-state | **NEVER REACHED.** They fire for the first time in the runner session. See §5. |

## 5. The one thing this session could not verify, and what was done about it

**`gbl_generate.py` has never been executed against the real artifacts.** The seam forbids
it. Its five hard gates therefore fire for the first time in front of the owner, in a
session that is mechanics-only and forbidden from debugging.

Mitigation, in the runner brief: **a traceback is not a gate.** A `SystemExit` carrying one
of the script's own messages is the experiment speaking and must be respected and reported
verbatim. An `AttributeError`, `TypeError`, `KeyError` or `ImportError` is a wiring fault in
the harness — the runner reports it *as a harness fault rather than a result*, does not
debug it, and does not look at any journey while diagnosing it, because there is no second
blind runner available.

**What reduces the risk without breaching the seam, and was done:** every function, file
and config value the plan names was grepped and resolved before execution (`cre_common`,
`cre_gates`, `cre_ladder`, `cre_sweep`, `cre_mirror`, and the four frozen API imports);
`load_cell`'s own sha assertion and `load_adopted`'s were read rather than assumed;
`path_metrics`, `find_journey`, `ClipResolver.resolve` and `top_degree_node_set` signatures
were checked against their call sites; and both graph artifacts plus the `B-S1.bin.json`
manifest were confirmed present on disk.

**What that does not cover:** anything that only fails with real data in it — a shape
assumption about the ladder, an empty interior at a depth, an arm where every pair is
adjacent. Those are the run-state gate's job, and the run-state gate is one of the five
that has never fired.

## 6. Operational measurements

- Pair derivation over the owner's Spotify export: ~40 s wall clock, 150 artists ranked,
  **125 usable** in both artifacts, 21 missing from one artifact, 4 name-ambiguous.
- Harness test suite: 30 tests, ~3.7 s.
- Snyk code scan over the harness directory: ~30 s per pass, two passes.

## 7. Standing-layer delta (D6)

| | Baseline (planning log §D6) | Now | Delta |
|---|---|---|---|
| Unconditional (characters) | 44,494 | **44,729** | **+235** |
| Conditional (lines) | 2,155 | **2,181** | **+26** |

**Neither delta is this session's.** This session's diff touches no file in the standing
layer — not `CLAUDE.md`, not `.claude/`, not `memory/`. Measured at the start of closeout
the totals were 44,494 / 2,155, exactly the baseline; both moved mid-closeout when the
**owner** added `memory/no-commercialization-ruling.md` and its `MEMORY.md` index line.

Recorded rather than adjusted, because the point of the measurement is that the total is
tracked across sessions regardless of who moved it, and because attributing someone else's
edit to this session — in either direction — is the failure mode `session-start` §C exists
to prevent. The new totals are the next closeout's baseline.

That memory file carries its own instruction — *"Not yet in the repo record — next writing
session should land it"* — which is **not discharged here**. It is a product ruling,
outside this track entirely, and folding it into a `GBL-` closeout commit would bury it.
Raised to the owner in the closing message instead.

## 8. What is owed, and to whom

Nothing is owed by this session. The two seams ahead are the plan's, not deferrals:

1. **The listen** runs in a fresh, mechanics-only runner session from
   `builder/analysis/2026-08-04-gentle-arm-blind-listen/RUNNER-BRIEF.md`. That session must
   not have executed this plan and must not read the `CRE-` findings note, `NEXT.md`'s
   result paragraphs, or spec §1–§2.
2. **The write-up** of `gbl_result.json` belongs to a *further* fresh session — the `CRE-`
   Stage-3 rule: the reader of results did not run them.

**Flagged, and not a `GBL-` item:** the eight `TEST-QUEUE.md` entries dated 2026-07-22 to
2026-07-27 remain `QUEUED` and unruled-on. Raised at the 2026-08-04 closeout, raised again
here, still the owner's call.
