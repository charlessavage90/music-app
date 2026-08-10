# `JFX-` execution log — the arms ran, 2026-08-09/10

**Role: REASONING RECORD for the `JFX-` run.** Why things were done, what was decided, what
went wrong. **It owns no figures** — those live in
`builder/analysis/2026-08-09-jfx-prereg-critique/README.md`, cited by section, never
restated. It **does** own the D6 standing-layer numbers, which the closeout rule requires
to live here.

Governing: `specs/2026-08-09-journey-fame-exposure-preregistration.md` as amended by
`JFX-AM1`. Successor plan: `plans/2026-08-10-cxa-graph-adoption.md`.

---

## §1 The sequencing decision, and it was the session-start scope check firing

The inherited position (previous handoff, "what I would do if I were continuing") put the
**routing harness first** and the artifact build second. `session-start`'s cheapest-experiment
check fired on it — the check explicitly applies harder to an inherited plan, because the sunk
cost is what suppresses it.

**Proposed instead, and the owner took it: build the artifact first, then compute everything
that needs no routing, then write the harness.** The reasoning is that `JFX-C5` and `JFX-C4`
are pure set operations over the two node sets, and `C5` fires §4 read 6 — *"stop, independent
of everything above"*. If `C5` had failed, the harness would never have needed writing.

`C5` passed (figure in the README's `JFX-C1` section, which carries the `C4`/`C5` row), so
the reorder bought nothing this time. **That is the expected outcome of a cheap stop-check
and not an argument against running it.** It cost about four minutes of scripting against a
~2.6-hour routing run.

## §2 `AM1.3`'s precondition was real, and the gate it names could never have caught it

`AM1.3` requires `CRE-G1(a)`'s byte-identity re-verified against today's `pathfinding.py`
before the mirror supplies routing code. Checked, and the concern is concrete:

```
cre_mirror.py    f52cc04  2026-08-03  "mirror copy with the fame-currency ramp"
pathfinding.py   a4ff9c6  2026-08-05  "MSW-: fame-currency known ramp ..."
```

Two independent implementations of the ramp, written two days apart, neither from the other.

**And the original gate was doubly inert on exactly that term.** `cre_gates.main()` calls
`g1a(...)` with `SweepConfig.production()` — ramp knob `0.0` — and `excludes=[]`, i.e. k = 0,
where the term is skipped entirely by both sides. **Re-running the original gate unchanged
today would still pass and still say nothing about the ramp.** That is a property of the
`CRE-` record worth carrying: `CRE-G1(a)` is evidence about the six static cost terms only.

`jfx_g1a_reverify.py` re-runs it strictly stronger: every rung to k = 20 with the ramp live,
same bar (`cre_gates.journeys_identical`, imported not restated), plus a mechanical
weight-parity assertion that fails on an `ApiConfig` `w_` field the mirror lacks **even when
that field's weight is 0.0** — the defect-of-absence class a grep cannot find.

Result in the figures README. Both red controls fired; the ramp control's first divergence
at **k = 1**, which is what proves the rungs above zero are genuinely compared.

## §3 A decision reversed mid-session: the mirror is not used at all

The first draft of `jfx_route.py` routed with production `find_journey` but kept the mirror
for `term_breakdown`, to measure `JFX-C6`'s floor term — production has no cost-decomposition
hook.

**Reversed after the re-verification passed.** Production exports `effective_floor_raw`, and
`C6` only needs one term's sign, so it is now computed from **production's own definition**:
`max(0, effective_floor_raw(...) - pop_raw[v]) > 0` over the returned path's edges. The
harness ends up with no second implementation of anything it measures.

**The claim in the docstring was then weakened deliberately.** An intermediate version said
the mirror "is not used at all", which is false — `cre_ladder` imports `cre_mirror` at module
level to get `victim_key`, so the module loads. The docstring now says *no mirror routing code
is called*, which is true. Recording this because the stronger sentence is the one a later
editor would naturally restore.

## §4 A defect in this session's own analysis code, found by reading output against `AM1.11`

`jfx_report.py` implemented read 9's trigger as *"the median is null AND fewer than half the
pairs moved"*. **That is `AM1.11`'s RATIONALE — why the median lacks power — not its
trigger.** The amendment's actual condition is *"the median is null and the mean's interval
excludes zero (or the converse)"*, and the script computed no interval on the mean at all.

**Consequence, had it not been caught: read 9 would have been silently suppressed at the one
depth where it fires.** At d20, 249 of 297 pairs moved — far more than half — so the wrong
condition was false exactly where the right one is true.

Found by reading the d10/d20 rows against the amendment rather than by any check. Fixed:
`paired_mean_ci` added with the same resampling convention as the frozen estimator, and the
trigger rewritten to the amendment's wording. **This is the "confident prose about correct
code" class inverted — correct prose, wrong code, and only re-reading the source document
caught it.**

## §5 Two defects in code this session did not write, both with tests shown red first

**`manifest.py` could not serialise a `Path`.** Detail in the figures README and in commit
`6cfef67`. The generalisable part: it had never fired because **every build that set
`--unlistenable-list` was rejected by acceptance before serialising, and every build that
reached a manifest used the default `None`.** Two independent conditions each individually
common, their conjunction never met until now. The first adoption build off a censused
payload is exactly the conjunction — i.e. `CXA-` Task 3.

**`jfx_stats.py` could not import itself.** `ROOT = parents[2]` of the *file* resolves to
`builder/`, so it inserted a nonexistent `builder/builder/analysis/...`. **Invisible because
`test_jfx_stats.py` inserts that path itself at line 22 before importing**, and the module
had no other consumer — `JFX-AM1.12` says so in as many words: *"It has no consumer yet."*
The regression test runs the import in a subprocess with a clean path, because importing it
inside the test module could never fail once that module has already fixed the path.

**Both tests were shown red against the original code before being kept.**

## §6 A reporting failure in this session's own output, and the owner caught it

Mid-run I reported the build as *"over an hour, still reading the archive"*. **It was not.**
The build started 23:16:17 and finished its archive read at 23:35:07; I inferred "no progress"
from a 0-byte log file, which was `| tee` holding the pipe — the stdout-buffering trap
`CLAUDE.md` and `session-start` §D both name. `PYTHONUNBUFFERED=1` was set and does not fix
a pipe.

The owner questioned the duration, which is what produced the measurement. **The corrected
account is in the figures README's timing note; the relaunch wrote directly to a file with no
pipe.** Two subsequent measurements — 174 CPU-seconds over 75 minutes, ~390 read-ops/sec —
were real but read against a false baseline, and looked like a stalled I/O-bound process when
they were a finished archive read followed by `serialise()`.

**Carry: a 0-byte log is not a progress signal in this repo, and redirecting to a file rather
than piping is the cheap fix.**

## §7 Gate outcomes

| | Outcome |
|---|---|
| `JFX-G1a` | **PASS** — every step negative, every simultaneous band strictly negative |
| `JFX-G1b` | **PASS** — `D_A` viability clause satisfied (`t_A` 10.60), `T` lower bound > 0 |
| `JFX-C5` | **PASS**, and it ran before the harness existed (§1) |
| `JFX-C6` | Does **not** fire read 7 |
| `JFX-C7` | Does **not** fire read 8; `AM1.7`'s depth-attenuation note fires for **both** arms |
| `AM1.11` read 9 | **FIRES at d20** |
| `CXA-G1`, `G2` | Not reached — they belong to the adoption plan |

**Pre-registered read: §4 read 5.** Deviation from §4's presupposition: it presupposes 300
pairs, and 297 carried both arms at all four depths. Recorded, not redrawn (§2 forbids it).

## §8 Corrections to the prior record

**"The shallower depth gradient" is NOT an established result, and the owner's summary said
it was.** `JFX-G1b` tests `D_B` against **0.67 × `D_A`**, never against parity, so nothing
pre-registered asks whether the gradients differ. Computed as a labelled post-hoc report row:
`D_B − D_A` **spans zero**. The point estimate leans shallower; the data cannot distinguish
the two maps' gradients, and equally cannot establish they are equal.

**This correction moved a decision.** It was made before the adoption decision was taken and
changed its basis from *"accepting a known trade-off"* to *"no cost demonstrated"* — and it
redirected the owner's "try routing changes first" fallback, which would otherwise have
targeted the depth ramp, a device aimed at the gradient that did not move.

**The one effect that is distinguishable is a different quantity**: the d20 *mean* interior
fame, with the median unchanged. Decomposed post-hoc, it lives almost entirely in the
famous–famous stratum. **Both decompositions are labelled in the figures README as not
pre-registered**, and the stratum one carries its own multiplicity caveat — three strata,
three intervals, one clears zero, expected about one time in seven under a true null.

## §9 An answer with no other home: why David Piltch is in the graph

The owner asked, from a worked example. A session bassist, 86 listeners, degree 49, every
neighbour a famous jazz vocalist.

- **Not a filter failure.** He was never in the un-listenable class at all — MusicBrainz
  records a sole-credited substantial release, so `ULF-` correctly never considered him.
- **Not new.** He is in today's adopted map and **absent from the pre-`MSW-` map entirely.**
- **He arrived with the cap rule change on 2026-08-06.** His own list ranks Nina Simone
  **#1**; hers ranks him **#61** — identical raw score (650), wildly different rank. Mutual
  k-NN needed both inside the top 50 and killed the edge. `trimmed_union` needs either.
- **Why he appears at depth:** 86 listeners puts him at the bottom of the fame ruler, so the
  `known` ramp tolls him at almost nothing, while similarity up to 0.975 makes the sim term
  nearly free. Cheap and extremely well-connected is what the router wants after 20 presses.

**This is the co-credit class `CCR-`, `RCC-` and `TCR-` all failed to attribute**, now with a
structural signature: *ranks them #1, ranked #61 back*. The rank-asymmetry idea that follows
from it is deferred in `CXA-` §4 with its condition; it is an **improvement**, not part of
this adoption, and resuming path-quality work is the owner's trigger.

## §10 Operational measurements with no other home

- **Build, cold: 1,686 s** (18m50s archive read + parse; 37 s filters/rescale/prune; 8m39s
  fame read; then serialise). **Warm: 541 s.** Both produced identical bytes. Against the
  recorded 75k baseline of 1,029 s: **1.64× the time for 1.56× the artists — linear.**
  Dominated by file COUNT (~207,000 opens), not by graph size; the stage that processes the
  extra edges is 37 seconds.
- **Routing: ~4.1 pairs/min on `JFX-A`, ~2.3–3.6/min on `JFX-B`**, 300 pairs each, ~2.6 h
  total. Checkpointed every 10 pairs.
- **Disk reads this archive at ~12,400 files/sec**, so I/O throughput was never the
  constraint (§6).

## §11 D6 — the standing context layer

Measured against `C:/Users/charl/.claude/projects/C--dev-music-app/memory`.

| Layer | Now | Delta |
|---|---|---|
| **Unconditional** | **45,880 characters** | **0** |
| **Conditional** | **2,475 lines** | **0** |

Previous figures: 45,880 / 2,475 (`2026-08-09-jfx-prereg-amendment-execution-log.md` §9) —
**identical, compared against the recorded numbers rather than inferred from "nothing was
touched".** This session edited no `CLAUDE.md`, no `.claude/` file and no `memory/` file.
**Nothing is owed to the owner on D6.**
