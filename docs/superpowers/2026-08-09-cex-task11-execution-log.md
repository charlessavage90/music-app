# Retained execution log — `CEX-` Task 11, `SEL-`, and the `JFX-` pre-registration, 2026-08-09

**Role: RETAINED EXECUTION LOG.** Reasoning behind the work, not a record of what each task
did — git has that. **Owns no figures.** Task 11's belong to
`builder/analysis/2026-08-09-cex-recensus/README.md`; the standing-layer numbers in §7 are
the exception the `closeout` D6 rule requires to live here.

Session governed by [`plans/2026-08-08-crawl-extension.md`](plans/2026-08-08-crawl-extension.md)
Task 11, entered from [`2026-08-08-HANDOFF-cex-crawl.md`](2026-08-08-HANDOFF-cex-crawl.md).
Branch `crawl-extension-design`, PR #91.

---

## 1. What this session did, in one paragraph

Executed Task 11 end to end — cost the re-census, fetched fame, re-censused the extended
population, assembled the drop lists, built, and stopped at the owner stop where acceptance
rejected on both bounds. Added one shipped-code capability (a per-invocation drop-list
override) because Step 4 could not otherwise run. Rebuilt the pre-crawl graph to give
`CEX-M1` a baseline it did not have. Then, on the owner's questions, wrote and committed a
pre-registration for measuring what the extension does to journeys. **Nothing was adopted,
no default was flipped, and no artifact was shipped.**

## 2. Three defects in the plan itself

**(a) Task 11 Step 4 could not run as written, and would have failed for a reason easily
mistaken for the designed one.** Step 3 says "re-census `unlistenable`" and Step 4 says
"build, and expect rejection". Between them sit two unstated steps: assembling the drop-list
payloads, and getting the ALG-B payload where the builder reads it. Without them
`unlistenable_drop.py` **refuses** — the `ULC-F1` population check — rather than producing
the acceptance rejection the plan predicts. Since the plan primes the reader to expect a
rejection, that refusal would plausibly have been logged as the designed outcome.

**(b) Step 5's comparison had no baseline, because Task 8 is what created the instrument.**
Step 5 says compare `CEX-M1` to the adopted build. The adopted build predates the logging
Task 8 added, so no such figure existed. Resolved by rebuilding the pre-crawl graph from the
snapshot — which **reproduced the adopted artifact exactly**, making the comparison a true
one rather than a near one.

**(c) The plan's `2>&1 | tee` was load-bearing and my PowerShell translation dropped half of
it.** `Tee-Object` captures stdout; the builder logs through Python's `logging`, i.e. stderr.
`cex-build.log` was never created. The figures survived only because the harness captures
stderr independently. **Recorded because the same substitution will look correct next time.**

## 3. Decisions taken, with reasoning

**Forward copies of the census scripts, not re-runs in place.** The 2026-08-05 scripts write
outputs beside themselves — one committed — and stamp everything they learn
`ulf-census-2026-08-05`. Re-running would have overwritten a frozen record *and* written a
false provenance date into the shared coverage store, whose entire design is per-field
provenance. Copies differ only in header, `STAMP`, and one hardcoded `censused` date.

**A per-invocation override rather than repointing the default.** The obvious fix for (a) was
to repoint `CANDIDATE_UNLISTENABLE_DROP_LIST_PATH`. Rejected on measurement: `pipeline.py`
refuses only on artists **outside** the censused set, so a *larger* list applied to a
*smaller* archive passes silently. The pre-crawl 75,000 is a strict subset of today's 117,302
(verified: zero dropped out), so repointing would have quietly changed every future build
from the snapshot — and would have changed it, the two lists disagreeing on 62 shared
artists from clip-availability drift alone. A behaviour change with a long fuse and no error.

**That decision then paid for itself the same session.** The baseline rebuild needed *no
flag*, precisely because ALG-B's shipped default still pointed at the 75,000-artist list. Had
it been repointed, the baseline would have silently used the 117k list and the `CEX-M1`
comparison would have been circular with nothing failing.

**Owner ruling — the `JFX-G1b` bar is 67%, not the 50% first proposed.** Reached by
translating the bar out of experiment coordinates: *how many presses may it take on the new
map to reach the distance twenty presses reaches today.* 67% ≈ no more than 50% more presses,
anchored on **REQ-18** (a handful, not dozens). The session proposed 50%, then argued against
its own number on that REQ-18 reading before he ruled.

**Owner ruling — `JFX-C2`'s threshold was withdrawn, not filled.** It gates nothing, so a bar
could only decide in advance which differences the write-up calls material. `MSW-V2`'s
report-row precedent governs. **A deliberate narrowing of what the document decides.**

**Measure the compound change, not the isolated cause.** Going adopted → extended bundles new
waypoints, new edges on old nodes, and a global reweighting. For *what does a person get now*
the compound is correct; isolating causes needs a third arm and a code knob that does not
exist. Recorded in the pre-registration's §0 so no read can claim the isolated version.

## 4. Gate and check outcomes

| Check | Outcome |
|---|---|
| `ULF-3` subset assertion, over the NEW population | **passed** — Task 11 Step 3's "re-verify rather than inherit" |
| Acceptance, extended build | **REJECTED on both bounds — the designed outcome and the owner stop.** Not widened |
| Baseline reproduction of the adopted artifact | **passed BYTE-IDENTICALLY** — see below |
| Acceptance, baseline build | **passed** — first green reading of these bounds; they had only ever been seen red |
| Snyk (`builder/src/artistpath_builder`) | clean, 0 issues |
| Suites | builder 245, api 261 |

### 4.1 `closeout` D3 — artifact provenance, and a stronger result than was first reported

**`builder/scratch/graph-cex-baseline-75k.bin` is BYTE-IDENTICAL to the adopted artifact.**
Both sha256 `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8`, verified at
closeout. Mid-session this was reported as reproducing the adopted build "exactly" on the
strength of matching artist and edge counts; the checksum is the stronger claim and is the
one to cite.

**What it establishes, and it is worth more than the `CEX-M1` baseline it was built for:**
spec §9's determinism requirement demonstrated end to end on a real build, and therefore
**proof that nothing in the build path has moved since the `MSW-` adoption** — not the cap
rule, not the drop lists, not the fame stage, not this session's own override. It also means
the pre-crawl snapshot is a *working* way back rather than a presumed one.

**`graph-cex-117k.bin` does not exist and should not.** Acceptance rejects before
serialising, so the extended build produced no artifact. Nothing to checksum, deliberately.

## 5. Corrections to the prior record

**`CEX-M1`'s saturated-edge share is vacuous by construction** — found by running it. An edge
saturates iff `raw >= percentile(raw, 99)`, and ~1% of any distribution sits at or above its
own 99th percentile. It reads ~1% for any crawl at any size and **cannot detect what it was
pre-registered to detect**. Recorded as a finding rather than as a reading, because a future
session seeing "1.0% both times" would conclude no effect, which the instrument cannot
support. The p99 half **is** informative and is reported.

**The spec's largest-component prune figure was 454 "today"; measured here it is 439.** The
`README` owns the measured value. Not a contradiction worth chasing — different build — but
the measured one is what the comparison uses.

**The `SEL-` findings document records a session error worth keeping**: this session read
`PRODUCTION_ALGORITHM` as "what production serves". It is not — ALG-B is the adopted lineage,
and `config.py:29-33` says so three lines below the constant. The warning `CEX-R5` added did
its job; the session read the constant first. **A warning adjacent to a misleading name does
not neutralise the name.**

## 6. Operational measurements with no other home

Census stage 1 ran **5,819 s**; stage 2 **2h01m** at ~1.32 s/artist with zero refusals. Fame
took **78 s**. The extended build ran ~**17 min**, the baseline **1,029 s** — both dominated
by reading 117k/75k small archive files, not by computation. The MusicBrainz **release dump
is 322 GiB, not the ~17 GiB two census docstrings claimed** — it is ~90% of the bytes a census
reads and therefore sets the floor on its cost; corrected in the live copy, left alone in the
frozen one.

## 7. `closeout` D6 — the standing context layer

Measured against `C:/Users/charl/.claude/projects/C--dev-music-app/memory`.

| Layer | Now | Delta |
|---|---|---|
| **Unconditional** | **45,880 characters** | **0** |
| **Conditional** | **2,475 lines** | **0** |

Previous figures: 45,880 / 2,475 (`2026-08-08-cex-crawl-execution-log.md` §9). **This session
touched neither layer** — no `CLAUDE.md`, `.claude/` or `memory/` edit. **Nothing is owed to
the owner on D6.**

*(The first measurement of this was taken from `builder/` and returned 3,017 / 480 — the
Bash working directory had persisted from an earlier command, so `CLAUDE.md` and `.claude/`
silently did not exist and the numbers counted only `memory/`. That is precisely the failure
D6's own comment warns about, in a form the comment does not name: not a wrong slug, a wrong
**cwd**. Both produce plausible small numbers that can never move.)*

## 8. Open, with conditions

| Item | Condition |
|---|---|
| **`CEX-F1`** — a crawl at/below `--target` exits 0 silently | Before the next crawl extension. **Unchanged, not touched here** |
| **`SEL-R1`** — add an `ADOPTED_ALGORITHM` pointer | Next time shipped code near those constants is edited |
| **`SEL-R2`** — population identity in the other two drop modules | First build needing either filter independently of `unlistenable`, **or** first census where the subset property fails |
| **`SEL-R3`** — a registry replacing the constant triples | Arrival of a third algorithm, **or** a second extension of either archive |
| **`SEL-R4`** — where the naming conventions live | Owner's, and it carries a standing-layer cost |
| **`CEX-M1` is a known-blind instrument** | Fix is measuring post-cap saturation; the `JFX-` artifact would supply it. Due before the next crawl extension |
| **`CEXR-6`'s `load_deezer_ids` half** | Own track. Unchanged |
| **`FE-SNYK-1`** | Org scan limit. Unchanged |

**Nothing killed this session.**
