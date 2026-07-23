# Pre-Track-2 structural guards — implementation plan

**Role: ACTIVE plan. Written 2026-07-23 by an outside consulting session, after the
Track 2 pre-registration landed and before any Track 2 work begins.**

This plan is **not** Track 2. It is a short, self-contained chunk of structural work that
must land **between** the Track 2 pre-registration and the Track 2 sweep, because two of
its items have a deadline that expires the moment the sweep harness is written.

**Run `session-start` as normal.** (The Fable engagement that produced the
pre-registration was told to skip it; that exception does not apply here.)

**Figures rule.** This plan restates no measured figure. Everything is cited by section
into `../2026-07-22-phase1-execution-log-and-graph-defect.md` (the "log") or
`../findings/2026-07-21-scoring-adjudication.md` (the "adjudication"). Assertion
thresholds you write in code are code constants, not restatements — same allowance the
Track 2 pre-registration takes in its own figures-rule note.

**Provenance of this plan.** Written by a session that read the project record and the
Track 2 pre-registration but **did not read the source**. Every claim below about what
the code contains is therefore second-hand — from CLAUDE.md, the log, or the
pre-registration's §0 resolution check. **Verify before acting on any of it.** If a
claim here doesn't resolve against the repo, the repo wins and this plan is the defect.

---

## 1. Why this exists

Read `2026-07-23-track2-preregistration.md` §0 before starting. Its most valuable
finding is that `w_floor` is **inert in the production baseline and becomes live only in
the arms that succeed** — a term that turns itself on, silently converting every
"one-knob" arm into a two-knob change. That was caught before the sweep rather than
after, which is the difference between a design correction and a retraction.

This plan generalises that catch, plus four others, into structural guards. The
motivating history, in one paragraph:

- The most expensive defect in the project (log §2.8) was invisible to the entire
  automated apparatus. Radiohead was deleted from the graph and famous artists collapsed
  to near-minimum degree while **every test passed** (log §2.3). It was found by a human
  comparing a metric's output to his own perception of named artists.
- The same unit error has occurred three times in different clothes: degree ≠ fame
  (log §2.6), popularity ≠ fame (log §2.11), raw popularity ≠ percentile (log §2.12).
- Interpretations have been reversed repeatedly; measurements never have (log §2.13).

Each guard below closes one of those classes **mechanically**, so it survives a session
boundary and doesn't depend on anyone remembering to be careful.

---

## 2. Scope boundary — read this before opening any file

### In scope

Six work items, §4 below. All are small. The whole chunk is well under the handoff
threshold in CLAUDE.md, so it is **one session with one closeout** — do not split it.

### Explicitly NOT in scope

- **Building the Track 2 sweep harness.** Not yours.
- **Running any Track 2 arm**, or any part of the factorial.
- **Running the §5 fame-proxy validation test**, or fetching any Deezer data.
- **Track 2's prerequisites P1–P8** (pre-registration §7). They belong to the Track 2
  session. One exception is noted in G1 below.
- **Changing the substance of the pre-registration.** You may correct one stated
  ambiguity (G5a) and register it in the doc map (G5b). Nothing else.
- **Re-litigating anything closed in log §4 / §4.1**, or the `capfix` adoption.
- **Clips (C1/C2), frontend UX, deployment.** Roadmap items, untouched.

### Adjacent, not yours

Pre-registration P7 asks the owner one question ("is ≥1 intermediary a real product
invariant?"). It blocks Track 2 arms, not this work. If the owner is in the loop while
you work, asking it costs nothing and unblocks the next session — but do not treat it as
a deliverable of this plan, and do not act on the answer.

---

## 3. Read first

| Document | What you need from it |
|---|---|
| `../specs/2026-07-23-track2-preregistration.md` | **§0 in full** — the resolution check, the `w_floor` finding, and what does/doesn't exist in shipped code. This is the plan's evidentiary base. |
| `../2026-07-22-phase1-execution-log-and-graph-defect.md` | §2.3 (how the defect was found), §2.6/§2.11/§2.12 (the three conflations), §2.13 (the reversal pattern) |
| `../2026-07-23-repair-and-retune-execution-log.md` | Track 1 record; the closeout doc-audit section and its **deferred items table** — one of those deferrals is closed for free by G2 |
| `../../README.md` (docs map) | The roles, and the "Adding a document" rule you owe in G5b |
| `../../../CLAUDE.md` | The factor-table rule (G3 extends it) and the PR discipline |

---

## 4. Work items

Order: **G1 and G2 first** (they are independent of each other; G1 is more self-contained,
so start there unless you have a reason not to). **G3 and G4** are CLAUDE.md edits — do
them together in one pass. **G5** is bookkeeping at closeout. **G6** is deferrals only.

---

### G1 — Artifact acceptance assertions at build time

**Objective.** The builder refuses to emit an artifact that violates the structural
invariants a usable graph must satisfy, so a repeat of log §2.8 fails loudly at build
time instead of surviving to adoption.

**Why this and not more tests.** The existing suites assert things about *functions*.
Nothing asserts anything about the *artifact*. That gap is exactly the size of the
Radiohead defect.

**Build.** An acceptance check that runs at the end of `build_from_archive` (or
immediately after, in the `build` CLI path — your call, record it) and raises rather than
warns. At minimum it asserts:

1. **Canonical presence.** A named set of artists resolves in the largest connected
   component. Include the Radiohead / Beatles class that log §2.8 records as the
   failure signature, **and** the pair endpoints named in the Track 2 pre-registration
   §2.3 (analysis set, held-out set, and the ordered reserve).
2. **Famous-artist connectivity floor.** The top-N-by-popularity nodes have degree above
   a floor. N and the floor are code constants you choose and justify in a comment
   citing log §2.8's recorded degrees — do not restate those figures in prose.
3. **Global shape bounds.** N, E, LCC size, and median degree inside recorded bounds.
   Source the current values from `../findings/2026-07-23-tiebreak-fix-adoption.md`
   (which owns the adopted artifact's identity) and the log §2.8 Arm 2 topology.

**Done when:**

- [ ] The check runs on every build and raises on violation.
- [ ] **It is demonstrated to catch the real defect, not just to pass.** Construct a
      negative case — the cleanest is to build a small fixture through the pre-Track-1
      code path (ranking on clipped scores) and show the check rejects it. A check that
      has only ever been observed passing is a vacuous test, and `closeout` sweeps for
      those.
- [ ] Both builder test suites green.
- [ ] The canonical set and bounds are in one named place, not scattered.

**Hazards.**

- Do not rebuild or re-adopt the 75k artifact. This item adds a check; it does not
  produce a new graph. Assert against the adopted one by sha256 (established script
  convention) and stop.
- Choose bounds that would have failed the §2.8 artifact and pass the adopted one. If
  you cannot find bounds that separate them, say so in the execution log rather than
  picking loose ones — that result is itself informative.

**Knock-on.** If the canonical set includes the Track 2 endpoints, pre-registration **P2
becomes a no-op** for the next session. Say so explicitly in the execution log so they
don't do it by hand for the second time.

---

### G2 — Put the currency in the name

**Objective.** No quantity in shipped code can be read without knowing its unit. This
closes the class that has produced three separate wrong conclusions.

**The forward-looking half is the important half.** Pre-registration §0 records that
**nothing in `api/src` currently computes popularity percentiles** — that machinery is
about to be written in the Track 2 harness and lands in `ApiConfig` / `pathfinding.py`
at adoption (pre-registration §2.4 R5). If the naming convention exists first, the new
code is born correct and there is nothing to retrofit. If it lands after, you will have
created a *second* generation of ambiguously-named quantities in the project's
highest-stakes code path.

**Do:**

1. Rename degree-based metrics so the basis is in the name — e.g. `hubfrac` →
   `top1pct_degree_frac`, "payload" → `non_top1pct_degree_interior_count`. Use whatever
   exact names read best; the requirement is that *degree* appears, because log §2.6
   records that these were read as fame and were not.
2. Split popularity by currency wherever it appears in the cost path, evaluation, and
   config: `pop_raw` for the raw 0–1 quantity, and reserve `pop_pctl` for percentile.
3. **Write the convention down** — one short paragraph in CLAUDE.md's architecture
   section stating that any popularity- or degree-derived quantity carries its basis in
   its identifier, so the Track 2 session applies it to the percentile machinery it
   writes.
4. The execution log's closeout deferral "CLAUDE.md and `api/README.md` both restate
   `ApiConfig` cost-weight defaults" comes due here — you are touching that text anyway.
   **Convert both to citations** rather than updating two copies.

**Scope — hard boundary.** `api/src/` and `builder/src/` **only**.

**Do NOT touch `builder/analysis/`.** Those scripts are deliberately frozen records of
what was executed, with hardcoded paths, and the project already nearly lost them once
(log §2, closing note). A rename there either breaks them or — worse — leaves them
running while silently meaning something different from the same-named quantity in
shipped code. Instead, add the old→new mapping to a README in that directory so a future
reader comparing an old probe's output against new code knows they are the same
quantity.

**Done when:**

- [ ] Grep finds no bare `pop` / `popularity` identifier in the cost or evaluation paths.
- [ ] The analysis-directory README carries the mapping table.
- [ ] The convention paragraph is in CLAUDE.md.
- [ ] `ApiConfig` weight defaults are cited, not restated, in CLAUDE.md and `api/README.md`.
- [ ] Full test suites green in both packages (`UV_LINK_MODE=copy uv run --extra dev pytest -q`
      from each package directory — see CLAUDE.md's environment note).

**Hazard — do not orphan the pre-registration.** `2026-07-23-track2-preregistration.md`
names metrics in today's vocabulary. If a rename lands without updating it, that document
contains stale identifiers within a day of being written, which is precisely the drift
class the closeout doc audit keeps finding. **Update it in the same commit**, or add a
short mapping note to it. Either is fine; silence is not.

---

### G3 — Extend the factor-table rule with a dormant-term check

**Objective.** Close the confound class the factor table cannot see.

**The argument, from the pre-registration's own best finding.** The factor-table rule
asks *which knobs did I turn*. `w_floor` was not a knob anyone turned — it is inert in
the baseline for a reason (`w_jump` prevents paths from dipping below the floor) that
**the intervention removes**. It would have switched itself on, only in the arms that
worked, and every one-knob attribution in the sweep would have been wrong.

**Do.** Add one paragraph to CLAUDE.md's "Writing and reviewing plans here", §1
(comparisons with an uncontrolled variable), requiring a **third section in every factor
table**:

> **Held constant, and why each is genuinely constant under the intervention.** Enumerate
> every term the comparison holds fixed, and for each, state why the intervention cannot
> change its state. A term that is inert in the baseline *for a reason the intervention
> removes* is not a constant — it is an uncontrolled variable that appears only in the
> arms that succeed.

Cite `specs/2026-07-23-track2-preregistration.md` §0 as the worked example. Keep it to a
paragraph; the existing rule earns its keep by being short.

**Done when:** the rule is in CLAUDE.md with the citation.

---

### G4 — Pre-registration as a gate, not a habit

**Objective.** Make the discipline that worked in log §2.13 C5 mechanical.

**Why now.** Pre-registration is credited with turning a disappointing null into an
actionable one and with saving a blind listen that would have burned the owner's ear on
nothing. It happened because one session thought of it. There is now a committed worked
example to point at, which is what makes a convention stick here.

**Do.** Add to CLAUDE.md, next to G3's paragraph:

> **No experimental arm runs until a pre-registration is committed.** It fixes the
> primary outcome, the effect size, the pair or sample set, and the read of every
> possible result including the null. The git commit timestamp is the evidence that it
> preceded the result — that is the part that cannot be reconstructed afterward. Worked
> example: `specs/2026-07-23-track2-preregistration.md`.

**Done when:** the rule is in CLAUDE.md with the citation.

---

### G5 — Two items of bookkeeping that must not drop

The documented degradation tell in this project is an item quietly falling out of a
tracking document. These are small; do them.

**(a) Relay one ambiguity into the Track 2 record.** The pre-registration applies guard G
(≥1 intermediary) to **all** arms including baseline P (§1.2), while also defining P as
shipped `find_path` and making it the mirror-and-verify target — "the mirror must
reproduce P byte-identically" (§1.4). On the two direct-edge pairs (Radiohead → The
Beatles, Muse → Coldplay) those cannot both hold: guard G changes the path by
construction, and shipped code has no G to compare against.

The fix is trivial — verify the mirror against production **with G off**, then enable G
uniformly across all arms — but it is unstated, and log §3.10 is explicit that
non-identical paths mean *stop, the harness is wrong*. A session executing this literally
either concludes verification failed or quietly skips the check on the two pairs it
matters most for.

Add a sentence saying so, either to the pre-registration (as a dated note, per the doc
map's inline-correction rule) or to the Track 2 plan when it is written. Do not
restructure anything else in that document.

**(b) Register the pre-registration in the doc map.** Its own §0 records this as
housekeeping it was not permitted to do. Add it to `docs/README.md` under Active, with a
one-line role description, per that file's "Adding a document" rule.

**Done when:** both are committed.

---

### G6 — Two guards deliberately deferred, with success conditions

Record these in the execution log as deferrals (closeout A3 discipline). Do not build
them now.

| Deferred | Why not now | Due when |
|---|---|---|
| **Named-entity check as standing practice** — showing the owner the *names* a perceptual metric produces, rather than the number | Pre-registration §5 already implements a stronger version of this for the fame proxy: 33 artists labelled into three buckets **without seeing fan counts**, scored for rank agreement and catastrophic inversions. Inventing a parallel practice now would duplicate it. | **After §5 runs.** Generalise its protocol into `closeout` (as an adoption-time step) and into `TEST-QUEUE.md`'s format, with its measured performance attached. |
| **Artifact provenance registry** — every gitignored `.bin` carries its full build configuration and code commit, and any cross-artifact comparison must cite the rows and count the differing columns | Track 2 Stage A holds the artifact fixed and asserts its sha256, so the post-hoc-comparison confound is not live. The existing checksum table in log §5 is adequate for now. | **When pre-registration §2.4 R0 or R2 fires** and a builder arm (p99 rescale, or the deferred `cap_strategy`) is scheduled — that is when new artifacts appear and log §2.2's two- and three-knob comparison errors become possible again. |

---

## 5. How to execute this plan

**Execute it inline, in one session. Do not fan out to subagents.**

Three reasons specific to this plan:

- **G1 and G2 collide on the same file.** Popularity is computed in
  `builder/.../pipeline.py` during `build`, which is where G1 adds its acceptance check
  and where G2 renames popularity quantities. G3 and G4 are two edits to the *same
  section* of CLAUDE.md. The apparent independence between items does not survive contact
  with the file layout, so parallel execution serialises anyway — with merge risk added.
- **The plan is deliberately not prescriptive at the code level.** It was written by a
  session that did not read the source, so it gives objectives, acceptance criteria, and
  hazards rather than code and tests. That profile needs continuous judgment from
  someone holding the whole scope — deciding the rename set, choosing bounds that
  separate the two artifacts — which is exactly what a per-task subagent lacks.
- **Every item needs the same context** (pre-registration §0, log §2.3/§2.6/§2.11/§2.12,
  CLAUDE.md's rules). Dispatching N agents means paying for that context N times to save
  nothing, since the work serialises regardless.

**Risk points the same way.** G2 is the highest-risk item: a cross-package rename with a
hard boundary (`builder/analysis/` frozen) and a silent failure mode (orphaning the
pre-registration's vocabulary). That is precisely where a subagent with partial context
gets 90 % of it right and misses the boundary. Six items is far under CLAUDE.md's handoff
threshold, so context growth is not a concern here.

**The one condition that flips it:** if G2's rename surface turns out to be much larger
than expected — dozens of call sites across both packages and their suites — delegate the
*mechanical* application of an already-decided rename set. Make the decision as the
controller, then hand out the edit. Never delegate the decision about what to rename.

---

## 6. Git and closeout

- **Branch per CLAUDE.md's PR discipline**, and push on the first commit, not the last.
  If `phase1-repair-and-retune` is still open and unmerged, decide whether to extend it
  or branch fresh from `main` — either is defensible; **record the choice and the reason**
  in the execution log.
- **Append to `2026-07-23-repair-and-retune-execution-log.md` per item, not only at
  closeout** — decisions and reasoning, not narration. Add a "Pre-Track-2 guards" section
  under the existing Track 1 material and above the Track 2 placeholder.
- **Snyk.** Per the global instruction and CLAUDE.md's security section, run
  `snyk_code_scan` over new/modified first-party code, fix what it finds, rescan until
  clean. Note that `main` is already not Snyk-clean by an accepted owner decision (log
  §7.1 item 3) — those three `listen.html` DOM-XSS findings are pre-existing and stay
  accepted; do not re-raise them.
- **Run `closeout` at the end.** Do not skip the `doc-auditor` step. The Track 1 closeout
  records that the judgement call to skip it was overruled by the owner and that this was
  correct — the audit found six High-severity defects in files that session never
  touched, and the worst class was auto-loaded memory carrying stale status.
- **Memory carries pointers, not status.** If you update memory at all, do not write
  phase status or artifact names into it. That exact failure put "Phase 1 is PAUSED" and
  the wrong adopted artifact into every cold session's context once already.

---

## 7. Definition of done for the whole chunk

A fresh Track 2 session, starting cold, finds:

1. A builder that **refuses to emit** an artifact with the log §2.8 failure signature,
   demonstrated against a negative case.
2. Shipped code in which **every popularity- and degree-derived quantity names its
   basis**, a written convention saying new ones must too, and a frozen-analysis mapping
   so old probe output stays interpretable.
3. A factor-table rule that requires **held-constant terms to be justified as genuinely
   constant under the intervention**.
4. A **pre-registration gate** in CLAUDE.md with a committed worked example.
5. A pre-registration whose **mirror-and-verify ambiguity is resolved**, registered in
   the doc map.
6. Two deferrals in the execution log, each with a condition that says when it comes due.

Nothing in Track 2's own scope has been started, and no Track 2 arm has run.
