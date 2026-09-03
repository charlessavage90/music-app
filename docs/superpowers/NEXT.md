# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
Track B's live in `findings/2026-07-30-track-b-cap-selection-results.md` (and its raw
`cb_scores.json`); the adopted graph's stay in
`findings/2026-07-21-scoring-adjudication.md`. Cited, never restated.

> ## 📍 STANDING FACT — THE APP'S ADDRESS IS `https://unsung.fm`, since 2026-09-03
>
> The domain was bought 2026-09-02 and cut over 2026-09-03: ACM certificate swapped,
> CloudFront alias flipped, `viewer_function.js` re-synthed. **`musicapp.cmiller.io` 301s here
> with the path preserved**, so every link already shared still works. Status blocks below
> dated before 2026-09-03 name the old host and are left as written — they record what was
> live at the time. **This note survives a `closeout` rewrite: it is a standing fact about the
> deployment, not status.** The runbook is `infra/README.md` §1a.
>
> ⚠ **The app is still NAMED "Artist Path" in the UI.** Only the address moved. A rename to
> "Unsung" is scoped but unapproved — do not assume it has happened.

**Last updated: 2026-09-01 (later), when THE OWNER CONFIRMED THE REVERT AND DISCHARGED THE
QUEUE.** The extended 117k graph was reverted earlier the same day after his test fired the
revert criterion he set on 2026-08-10; he has since confirmed the old map is live and
**reported nothing wrong**. **THERE IS NO NEXT ACTION ASSIGNED. Nothing is blocked, no
session owes anything, and the test queue is EMPTY** — zero live items, which is a valid and
common state and never evidence a session forgot. Do not discharge either 2026-09-01 entry
twice, and do not re-queue "tell me how it feels": his long-run evaluation is continuous and
this file explicitly does not hold it (owner ruling, 2026-08-07).
**The landing-dot fix (PR #92) is LIVE and was NOT reverted** — it is frontend and rode the
frontend sync, not the map. **Everything open is his to trigger and none of it blocks
anything else:** **Option C** (same-name population probe), **`SEL-`**, **closing or keeping
the 2026-07-29 famous-to-famous defect ruling**, and the **three candidate path-quality fixes
in the `CXR-` README — each needs its own pre-registration and none may start without him.**
⚠ **One thing is still OPEN rather than done: the first journey, before any press, is
UNEXPLAINED.** His confirmation did not close it and nothing measured accounts for it. It is
not a queue item and not assigned; it must not be quietly dropped.

---

> ## ✅ THE EXTENDED 117k GRAPH IS REVERTED, 2026-09-01 — **AND THE OWNER HAS CONFIRMED IT.** ~~The next action is the OWNER'S and it is USE: confirm the old map is back.~~ *(Discharged 2026-09-01 (later) — he confirmed the old map is live and reported nothing wrong. Everything else this block records still stands.)*
>
> **`https://musicapp.cmiller.io` serves `graph-msw-tu50.bin` again — 58,838 artists,
> 1,315,684 edges, sha `43dd82bb…`.** Verified live from outside, not inferred: `/health`
> reports that identity and a journey builds through the public address. The image tag is
> **unchanged** at `994c203`, so the code, the buttons and the landing page are exactly what
> they were — **only the map moved back.**
>
> **Why.** The owner ran the queued test and reported the extended map *"noticeably worse than
> the old version — much harder to find unknown artists"*, **worse both before pressing
> anything and while digging, mostly while digging**. That is the revert criterion he set on
> 2026-08-10 in the words he set it in. He instructed the revert.
>
> **⚠ The pre-adoption measurements did not contradict him — one of them predicted this, and
> the adoption record read it as a pass.** `JFX-G1b` is a **"the map is broken" stop-gate**
> that **permitted materially more digging than the old map needed to reach the same
> obscurity**, and the extended map used materially more. **Passing it never meant "no
> worse", and no document said otherwise — but nothing said it loudly either.** The permitted
> bound and the realised figure are owned by the `JFX-` results README, `JFX-G1` section —
> **cited, never restated here.**
>
> **The mechanism is measured and owned by
> [`builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md`](../../builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md)**
> — figures cited from there, never restated. Two things, and **the second is a standing trap
> for every future map switch**: the fame ruler the `known` ramp steers on is framed on **the
> served artifact's own population**, so growing the map reprices every artist in it.
>
> **What is UNEXPLAINED, and it is half his report:** nothing measured accounts for the
> **first** journey being worse before any press. `JFX-C1` found no change at depth 0 across
> 297 pairs, and `CXR-P3` found the popularity currency barely moved. **Do not quietly drop
> this half.**
>
> **What must not be reverted by a well-meaning editor:**
>
> - **`graph-cxa-adopted.bin` is still in the bucket and is the REJECTED artifact.** Do not
>   redeploy it as "the newer one". `ApiConfig.graph_path`, its test pin and `infra/README.md`
>   §4 all point at `graph-msw-tu50.bin` deliberately, each with a comment saying why.
> - **The `CEX-` crawl extension itself is NOT reverted and is not wasted.** The 117,302-
>   response archive, the re-censused payload and the acceptance-bound work all stand; what was
>   rejected is *building the served map from it as it stands*.
> - **`w_known_ramp_fame_pctl` stays 0.01.** It was not touched in either direction. Moving it
>   now would confound the confirmation test.
> - **Nothing here resumes path-quality work.** Three candidate fixes are visible in the `CXR-`
>   README and **each needs its own pre-registration and is the owner's trigger to start.**
>
> Handoff: [`2026-09-01-HANDOFF-cxr-revert.md`](2026-09-01-HANDOFF-cxr-revert.md). Reasoning:
> [`2026-09-01-cxr-revert-execution-log.md`](2026-09-01-cxr-revert-execution-log.md). PR #91.

---

> ## ✅ THE EXTENDED 117k GRAPH WAS ADOPTED, DEPLOYED AND LIVE, 2026-08-10 (later). ~~**The next action is the OWNER'S and it is USE.**~~ *(SUPERSEDED by the block above: **it was reverted on 2026-09-01** after the owner's queued test fired his revert criterion. Everything this block records about what was done and why still stands as history; its claim that the extended map is what production serves is **now FALSE**.)*
>
> **`https://musicapp.cmiller.io` now serves a map of 88,685 artists and 1,618,164 edges**,
> built from the extended 117,302-response ALG-B archive — up from 58,838 artists. The owner
> took **`CXA-S1`** (the bound values) and **`CXA-S2`** (the deploy), and separately
> instructed that PR #92's UI fix ship with it and that the frontend sync run **`--prune`**.
>
> **PR #92's landing-dot fix is LIVE.** It was on `main` only; `origin/main` was merged in and
> the image rebuilt at the merged commit so the tag records what actually shipped.
>
> **Both gates passed. `CXA-G1`** — the rebuild through the shipped path, with no
> per-invocation override, is **byte-identical** to the artifact every `JFX-` figure was
> measured on. **`CXA-G2`** — verified **from inside the built image**, not the branch.
>
> **Verified live, not inferred:** `/health` returns the `CXA-G1` sha and both counts; a
> public journey returns Radiohead → Nine Inch Nails → Aphex Twin; a middle card resolves clip
> and cover art.
>
> **⚠ THE DIRECTION OF STALENESS, again:** *"production serves `graph-msw-tu50.bin`"* is now
> **false wherever it describes the present**, and **correct** inside a frozen `JFX-`/`CEX-`
> record describing what that track did. **Read for tense; grep cannot do this.**
>
> **⚠ SIX CLAIMS AN EDITOR MUST NOT REVERT.** **The shallower gradient is NOT established** —
> adoption was taken with **no cost demonstrated**, and this equally does not establish the
> gradients are equal. **The d20 famous-to-famous drift is POST-HOC** — where to look, never a
> finding, which is why the use-test points him there. **`w_known_ramp_fame_pctl` stays 0.01**,
> confirmed in the running image. **`JFX-B`'s `DO_NOT_DEPLOY: true` is still CORRECT** — the
> shipped artifact is a different file from a new build. **The ALG-E drop payload did not
> ship**, and **the 75k-era ALG-B payload stays in `data/`** — three era-pinned probes load it
> by name; superseded as a default, not orphaned.
>
> **⚠ NEW, AND THE MOST LOAD-BEARING THING THIS TRACK ADDED: the EDGE FLOOR in `acceptance.py`
> is now the only bound that can catch a silent cap-rule revert.** The fourth acceptance
> artifact — built here because the plan had it marked NOT RUN — showed the node bound cannot
> see one. **Widening that floor to admit a build removes the protection with nothing going
> red.**
>
> **Figures owned by `builder/analysis/2026-08-09-jfx-prereg-critique/README.md` and
> `builder/analysis/2026-08-10-cxa-acceptance-bounds/README.md` — cited, never restated.**
>
> **Entry point:** the current handoff
> [`2026-08-10-HANDOFF-cxa-adoption.md`](2026-08-10-HANDOFF-cxa-adoption.md). Reasoning:
> [`2026-08-10-cxa-adoption-execution-log.md`](2026-08-10-cxa-adoption-execution-log.md) —
> **its §3 records three defects in the plan itself**, the sharpest being that Task 2 named one
> constant to move when three had to, which would have turned the suite red on what the plan
> called a one-line change. Operational:
> [`plans/2026-08-10-cxa-graph-adoption.md`](plans/2026-08-10-cxa-graph-adoption.md) — now
> **COMPLETE**. Branch `crawl-extension-design`, **PR #91 — open, and now carrying the whole
> track.**
>
> **Nothing is running on any port** — nothing was started this session and nothing was left
> behind; the app was exercised against the live address.
>
> ---

> ## ▶ THE `JFX-` ARMS RAN AND THE OWNER CHOSE TO ADOPT, 2026-08-10. ~~**The next action is WORK: execute the `CXA-` plan, INLINE, in a FRESH session.**~~ *(SUPERSEDED by the block above: **the `CXA-` plan is EXECUTED, COMPLETE and DEPLOYED.** Its six "must not be reverted" claims still stand in full — only its ranking as the next action has moved. ⚠ Its "nothing is adopted, nothing is deployed" is now FALSE of the present and true only of what `JFX-` itself did.)*
>
> **Both gate clauses passed.** `JFX-G1a` and `G1b` PASS, `JFX-C5` passes, journeys
> do not get longer in any of twelve stratum-by-depth cells, and the pre-registered read is
> **§4 read 5** — *the map got bigger and journeys did not measurably change*.
>
> **What this did NOT do: adopt anything, deploy anything, flip any default, or change what any
> user sees.** The live site is untouched and was never in scope. The new artifact is
> gitignored and its manifest says `DO_NOT_DEPLOY: true`, correctly — it was built against the
> old bounds.
>
> **Figures owned by `builder/analysis/2026-08-09-jfx-prereg-critique/README.md` — cited, never
> restated.**
>
> **⚠ THE OWNER'S ADOPTION DECISION AND HIS REVERT CRITERION ARE RECORDED IN `CXA-` §0, TAKEN
> 2026-08-10, AND ARE NOT TO BE RE-LITIGATED.** He adopts and widens the bounds, on the
> reasoning that these metrics are indicators and cannot say whether a change is perceptible.
> His revert trigger — set **before** adoption so it is a trigger and not a rationalisation —
> is *a noticeably worse experience on more than half of tested journeys*, measured by **how
> hard it is to find novel artists**. **"Improvements needed" is a SEPARATE bucket from
> "revert".** He judges revert unlikely.
>
> **⚠ SIX CLAIMS AN EDITOR MUST NOT REVERT.** **The shallower gradient is NOT established** —
> `G1b` tested against the 0.67 bar, never against parity, and `D_B − D_A` spans zero; adoption
> was taken with **no cost demonstrated**, and this equally does not establish the gradients
> are equal. **The d20 famous-to-famous drift is POST-HOC** — three strata, one interval
> clearing zero — and is where to look, never a finding. **`AM1.11` read 9 fires at d20 and the
> gate still stays on the MEDIAN**; promoting the mean is his call. **`CRE-G1(a)` as originally
> run covers the six static cost terms ONLY** — it ran at k = 0 with the ramp knob at 0.0, so
> it is doubly inert on the ramp, and the `JFX-` re-verification is what covers that.
> **`w_known_ramp_fame_pctl` stays at 0.01.** **The regenerated ALG-E drop payload must not
> ship.**
>
> **⚠ THE TRAP IN `CXA-` TASK 2, because it is the one most likely to be got wrong:** repoint
> `UNLISTENABLE_DROP_LISTS[CANDIDATE_ALGORITHM]`, **not** the `PRODUCTION_ALGORITHM` entry —
> ALG-B is the adopted lineage bound to the constant named *candidate* (`SEL-R1`–`R4`,
> deferred and live). `NoUnlistenableListForAlgorithm` will **not** catch a wrong entry; it
> raises on an *absent* one.
>
> **Entry point:** the current handoff
> [`2026-08-10-HANDOFF-jfx-run.md`](2026-08-10-HANDOFF-jfx-run.md). Reasoning:
> [`2026-08-10-jfx-run-execution-log.md`](2026-08-10-jfx-run-execution-log.md) — **its §4
> records a defect in this session's own analysis code that would have silently suppressed a
> pre-registered read at the one depth it fires**, and its §6 records this session
> misreporting build progress from a buffered log until the owner questioned it. Governing:
> [`specs/2026-08-09-journey-fame-exposure-preregistration.md`](specs/2026-08-09-journey-fame-exposure-preregistration.md).
> Operational: [`plans/2026-08-10-cxa-graph-adoption.md`](plans/2026-08-10-cxa-graph-adoption.md).
> Branch `crawl-extension-design`, **PR #91**.
>
> **Nothing is running on any port** — 8000, 5173 and 5174 swept and free.
>
> ---

> ## ▶ `JFX-AM1` IS COMMITTED AND NO ARM HAS RUN, 2026-08-09 (later). ~~**The next action is WORK: the routing harness, in a FRESH session.**~~ *(SUPERSEDED by the block above: **the arms HAVE run.** Its five "must not be reverted" claims still stand in full — only its ranking as the next action has moved.)*
>
> **The owner said "we're doing JFX" and asked for an `ml-graph-analyst` review of the
> pre-registration first. That review, two of his own corrections, and two defects found by
> writing code against the document produced a twelve-clause amendment** — committed before
> any arm ran, which is the whole point of the timestamp.
>
> **What this did NOT do: build an artifact, route a pair, compute a fame statistic, adopt
> anything, or change what any user sees.** The live site is untouched and was never in scope.
>
> **⚠ READ `JFX-AM1` BEFORE §2, §3 OR §4 of the pre-registration.** It changes all three and
> governs where they disagree. **Four clauses change what passes:** the fame quantity is now
> **log-scaled** (`AM1.2`, his decision); **`G1b` is a bounded linear contrast** with a
> viability clause, the ratio having declared an equal map broken far too often on a weak
> denominator (`AM1.5`); **`G1a`'s steps move to one simultaneous band** and gain an effect
> size (`AM1.6`); and **`C6`/`C7` get the effect sizes their branch triggers lacked**
> (`AM1.7`). **`JFX-G1b` stays at 67%** — unchanged deliberately.
>
> **⚠ FIVE CLAIMS AN EDITOR MUST NOT REVERT.** **`DD-F1` is NOT overturned** — it survives in
> **popularity** currency and fails to transfer to **fame**; both halves travel together, and
> collapsing either direction repeats the currency error that caused this. **The
> famous-to-famous measurement is STRUCTURE, not ROUTING** — famous endpoints *can* descend;
> whether journeys *do* is what `JFX-` exists to measure. **The 2026-07-29 defect ruling is
> OPEN** — its precondition changing is not the ruling closing, and that is his. **The `MSW-`
> switch addressing famous-to-famous was BY DESIGN, not incidental** (his correction), and
> **no `MSW-` record mentions it**, so that adoption is written up on narrower grounds than it
> had. **`AM1.10` records an overstatement this session made and then measured false** — a
> shared RNG does not materially move intervals at 10,000 replicates; do not restore the
> stronger claim.
>
> **⚠ THE ROUTING HARNESS DOES NOT EXIST.** `AM1.3` now *names* the instrument — which nothing
> did before — but the code that walks the pair set is unwritten. `jfx_stats.py` supplies the
> tested primitives and **has no consumer yet: unfinished, not abandoned.** The §1 build
> script **now exists** and had never been written despite the spec's present tense
> (`AM1.12`).
>
> **Figures owned by `builder/analysis/2026-08-09-jfx-prereg-critique/README.md` — cited,
> never restated.**
>
> **Entry point:** the current handoff
> [`2026-08-09-HANDOFF-jfx-amendment.md`](2026-08-09-HANDOFF-jfx-amendment.md). Reasoning:
> [`2026-08-09-jfx-prereg-amendment-execution-log.md`](2026-08-09-jfx-prereg-amendment-execution-log.md)
> — **its §2 records this session reversing its own recommendation under owner challenge, and
> its §4 records a claim it had to correct in its own amendment.** Governing document:
> [`specs/2026-08-09-journey-fame-exposure-preregistration.md`](specs/2026-08-09-journey-fame-exposure-preregistration.md).
> Branch `crawl-extension-design`, **PR #91**.
>
> **Nothing is running on any port** — 8000, 5173 and 5174 swept and free.
>
> ---

> ## ▶ `CEX-` TASK 11 IS COMPLETE AND THE TRACK IS AT ITS OWNER STOP, 2026-08-09. ~~**The next action is HIS.**~~ *(SUPERSEDED on next actions by the block above: he chose **Run the `JFX-` arms**, and the next action is now WORK. **Its three "must not be reverted" claims and its `SEL-` item still stand in full** — only its ranking as the next action has moved. ⚠ Its `JFX-` description is **pre-amendment**: `JFX-AM1` changed §2, §3 and §4 on 2026-08-09.)* Nothing is blocked, nothing is half-done.
>
> **The build ran and was REJECTED on BOTH acceptance bounds. That is the designed outcome,
> not a failure to fix, and the bounds were NOT widened.** No artifact was written — acceptance
> rejects before serialising.
>
> **What this did NOT do: adopt anything, deploy anything, or change what any user sees.** The
> live site is untouched and was never at risk.
>
> **Figures are owned by `builder/analysis/2026-08-09-cex-recensus/README.md` — cited, never
> restated.**
>
> **⚠ THREE CLAIMS AN EDITOR MUST NOT REVERT.** **`CEX-M1`'s saturated-edge share is VACUOUS
> by construction**, not "unchanged" — an edge saturates iff its raw score is at or above the
> 99th percentile of raw scores, so ~1% of any distribution saturates at any crawl size;
> reading it as "no effect" is a conclusion the instrument cannot support. **The new
> `unlistenable_list_path` defaulting to `None` is deliberate and is NOT unshipped work** — it
> is a per-invocation override, and flipping the default is an adoption decision on purpose,
> because repointing it changes every future build from the pre-crawl snapshot *silently*.
> **The regenerated ALG-E drop list is a by-product that must not be shipped** — its population
> never changed, yet 30 artists became drops and 43 stopped being drops in four days.
>
> **⚠ A NEW GOVERNING DOCUMENT IS COMMITTED AND UNRUN.**
> [`specs/2026-08-09-journey-fame-exposure-preregistration.md`](specs/2026-08-09-journey-fame-exposure-preregistration.md)
> (`JFX-`) pre-registers the answer to his four product questions — do less famous artists find
> it easier or harder to appear in journeys, does that differ by endpoint fame, does it change
> with bypass depth, does it change journey length. **Its thresholds are his and were set before
> any arm ran** (`G1b` = 67%; `C2`'s threshold withdrawn as inappropriate to a report row).
> **Read its §0.1 before its §3** — two confounds bind every read, and a third has a stated
> direction. **No arm has run.**
>
> **His options, and nothing expires:**
>
> - **Run the `JFX-` arms** — one diagnostic build (~17 min) then routing. It answers the
>   product questions and would close `CEX-M1`'s blindness in the same pass.
> - **Recalibrate the acceptance bounds** and adopt. `MSW-G3` is the precedent and there too it
>   was his. **The artifact would be byte-identical to a post-widening rebuild**, so adoption
>   costs no second build.
> - **Stop the track.** Everything is recorded; nothing is owed.
>
> **Entry point:** the current handoff
> [`2026-08-09-HANDOFF-cex-task11.md`](2026-08-09-HANDOFF-cex-task11.md). Reasoning:
> [`2026-08-09-cex-task11-execution-log.md`](2026-08-09-cex-task11-execution-log.md) — **its §2
> records three defects in the plan itself**, the sharpest being that Task 11 Step 4 could not
> run as written and would have failed with a *refusal* that the plan primes a reader to log as
> the designed *rejection*. Branch `crawl-extension-design`, **PR #91**.
>
> **⚠ SEPARATE AND HIS: `SEL-`.** A problem statement, deliberately not acted on
> ([`findings/2026-08-09-selector-identity-drift.md`](findings/2026-08-09-selector-identity-drift.md)):
> constants named for a role that has since moved, and population identity implemented in one
> of three sibling drop modules. **No live defect is claimed.** He asked for it to be handled
> as its own maintenance session rather than in flight.
>
> **Nothing is running on any port** — 8000, 5173 and 5174 swept and free.
>
> ---

> ## ▶ THE `CEX-` CRAWL IS EXTENDED, 2026-08-08 — new population per `crawl_result.md`. ~~**The next action is WORK: plan Task 11, in a FRESH session. It ends at an OWNER STOP.**~~ *(SUPERSEDED by the block above: **Task 11 IS DONE** and the owner stop is reached. Its "must not be reverted" claims still stand in full; only its ranking as the next action has moved.)*
>
> **Plan Tasks 1–10 are complete and pushed.** The `ULC-F3` block on extending a crawl is
> **discharged**: the bound moved from artists *discovered* to artists *fetched*, so the
> frontier survives; a crawl that cannot extend now **refuses instead of exiting 0**; the
> checkpoint is written atomically; and `artistpath-build refrontier` repairs an older one.
>
> **What this did NOT do: build anything, or adopt anything.** No graph, no artifact, no cost
> function, no router, no frontend. The archive got bigger. **Nothing a user can see has
> changed.**
>
> **Figures are owned by `builder/analysis/2026-08-08-cex-g1/` (`g1_result.md`,
> `crawl_result.md`) — cited, never restated.** `CEX-G1` passed exactly; the crawl completed
> in under four hours with **zero failures** and every response HTTP 200.
>
> **⚠ THE ARCHIVE IS NOW ONE-WAY, AND THE SNAPSHOT IS THE ONLY WAY BACK.** After the append,
> today's graph **cannot be rebuilt from source** — `build_from_archive` reads everything under
> the algorithm prefix. The owner's precondition was met and **verified again after the crawl**:
> `builder/scratch/grt-archive-algb.pre-cex-snapshot` still holds exactly 75,000 responses.
> Both it and the checkpoint backup are gitignored, so `g1_result.md` is their only identity.
>
> **⚠ THREE CLAIMS AN EDITOR MUST NOT REVERT.** `exhausted: false` in the checkpoint is
> **correct** — the crawl stopped on the fetch cap with a non-empty queue, so the graph was not
> crawled out, and ~11,293 artists are now recorded as discovered-but-not-crawled. `grt_run.py`
> **refuses to run**, deliberately: its era pin is a refusal because the old behaviour was
> deleted from a loop body rather than defaulted. `calibrate.py`'s `_replay` is deliberately
> left on the **old** stopping rule, because it exists to reproduce its own committed cells.
>
> **⚠ THE GATE THAT A GREEN TEST SUITE COULD NOT DISCHARGE.** `CEX-G2` was folded into "run the
> suite", and the suite stayed green through the semantics change. The sweep found two frozen
> probes depending on the old meaning — one of them, `calibrate.py`, **names no identifier that
> changed**: it hand-copies the crawler's stopping rule, and its own docstring declared its
> answers void if that rule ever moved. **A caller can depend on a rule without naming
> anything the rule uses**, and `test_pipeline_mirrors.py` cannot see that class.
>
> **What Task 11 must do, and the trap in it:** every command passes `--algorithm`
> **explicitly** (`CEXR-2`) — there is no `RC-H3` guard on the build side, so a defaulted build
> reads ALG-E and could pass acceptance while describing a population nobody asked for. **Cost
> the re-census on 500 artists and report before running the full pass** (`CEXR-9`); it is the
> only uncosted step in the track. **The build WILL be rejected on BOTH acceptance bounds —
> that is the designed outcome and an owner stop. Do not widen them** (`MSW-G3` is the
> precedent, and there too it was the owner's).
>
> **Entry point:** the current handoff
> [`2026-08-08-HANDOFF-cex-crawl.md`](2026-08-08-HANDOFF-cex-crawl.md). Reasoning:
> [`2026-08-08-cex-crawl-execution-log.md`](2026-08-08-cex-crawl-execution-log.md) — **its §4
> records two tests in this session's own work that passed while testing nothing**, both caught
> by running them against the old code first. Governing document:
> [`specs/2026-08-07-crawl-extension-design.md`](specs/2026-08-07-crawl-extension-design.md).
> Operational: [`plans/2026-08-08-crawl-extension.md`](plans/2026-08-08-crawl-extension.md).
> Branch `crawl-extension-design`, **PR #91**.
>
> **Nothing is running on any port** — 8000, 5173 and 5174 swept and free.
>
> **⚠ SEPARATE TRACK, OPEN AND HIS: PR #92 (`landing-dot-z-order`).** The owner found one defect
> while discharging the test queue — the landing page's green indicator dot rendering on top of
> the open artist dropdown — and **verified the fix locally**. It is **not deployed**: the live
> site still shows it until he merges and publishes. Not part of `CEX-`.
>
> ---

---

> ## ▶ THE `CEX-` CRAWL EXTENSION IS DESIGNED AND PLANNED, 2026-08-08 — ~~**the next action is WORK: execute the plan in a FRESH session.**~~ *(SUPERSEDED by the block above: Tasks 1–10 ARE DONE. **Its two "must not be reverted" claims and its `CEX-R1`/`R3`/`R4` findings still stand in full** — only its ranking as the next action has moved. ⚠ Its `config.py:17` warning is now FALSE: Task 7 fixed it.)*
>
> **The owner approved the crawl expansion, conditional on snapshotting the archive so it can
> be reverted.** That snapshot is **plan Task 9 Step 1 and a precondition for the whole
> track**, not a nicety: after the crawl appends, today's graph cannot be rebuilt from source.
>
> **What this session did NOT do: change any shipped code.** The diff is three documents, two
> doc-map rows and two analysis directories. No graph, no artifact, no cost function, no
> router, no frontend.
>
> **⚠ HALF THE ORIGINAL MOTIVATION DISSOLVED UNDER TEN MINUTES OF CHECKING, and this is the
> thing to carry.** The owner named two missing artists. **Commander Cody was never missing** —
> crawled and shipped; he is unfindable because search is literal-substring and the map spells
> him *"& His Lost Planet Airmen"* against the queried *"and the Lost Planet Airmen"*
> (`CEX-R3`, **a search defect, its own track, and the only lever that addresses "I cannot find
> this artist" for artists that are present**). **Goose cannot be in the map at all** — nobody
> among 75,000 artists names them, so growth cannot reach them (`CEX-R1`), and **seeding does
> not work either**: falsified by a matched-pair build with a zero-node, zero-edge delta and
> again at three degree ceilings (`CEX-R4`). **Do not re-plan either as a crawl outcome.**
>
> **⚠ TWO CLAIMS MADE BY THAT SESSION WERE FALSIFIED BY MEASUREMENT AND MUST NOT BE REVERTED.**
> That seeding would work (it does not — the original argument used half the cap algorithm),
> and that growing the crawl would crowd the hubs and thin the obscure tail. **It does the
> opposite:** `CXS-C1` rose monotonically and materially, and hub saturation *fell*. Figures
> owned by `builder/analysis/2026-08-08-cxs-growth/` — cited, never restated.
>
> **⚠ `config.py:17` IS STALE IN THE TREE RIGHT NOW.** It calls ALG-E "the adopted 75k
> archive's algorithm"; the adopted map's lineage is **ALG-B**. Recorded as `CEX-R5`, fixed by
> **plan Task 7**, and live until then. `cli.py:314` carries the same rot.
>
> **Entry point:** the current handoff
> [`2026-08-08-HANDOFF-cex-design.md`](2026-08-08-HANDOFF-cex-design.md) — **read the spec's
> §10 amendment log before its §3**. Reasoning:
> [`2026-08-08-cex-design-execution-log.md`](2026-08-08-cex-design-execution-log.md). Governing
> document: [`specs/2026-08-07-crawl-extension-design.md`](specs/2026-08-07-crawl-extension-design.md).
> Operational: [`plans/2026-08-08-crawl-extension.md`](plans/2026-08-08-crawl-extension.md)
> (11 tasks; seam after Task 10, **owner stop** at the end of Task 11 where acceptance rejects
> on both bounds). Pre-registration: [`specs/2026-08-08-crawl-growth-subset-preregistration.md`](specs/2026-08-08-crawl-growth-subset-preregistration.md)
> — **EXECUTED, do not run again.** Branch `crawl-extension-design`, **PR #91**.
>
> **Nothing is running on any port** — 8000, 5173 and 5174 swept and free. The ALG-B archive is
> verified at exactly **75,000** responses after a probe mutated it mid-session.
>
> ---

> ## ✅ THE NEW BYPASS UX IS LIVE, 2026-08-07 — and `DEP-34-FIX` IS CLOSED. ~~**The next action is the OWNER'S.**~~ *(SUPERSEDED on next actions by the `CEX-` block above: the next action is WORK. **`SNS-1`, Option C and the queued UI test are still his and still outstanding** — that half is unchanged, only its ranking as "the next action" is. ⚠ This block's "THE TEST QUEUE IS EMPTY" was true when written and is **now false**: the bypass-tray entry below it was queued by the same closeout.)*
>
> **The journey cards, the bypass interaction and the landing page were redesigned, merged
> and deployed to `https://musicapp.cmiller.io` the same day.** Frontend only, plus one
> infrastructure guard: **no graph, no artifact, no cost function, no router.** Which artists
> a journey contains is untouched.
>
> **What a person sees.** Both bypass signals moved off the card face into a recessed
> **"Reroute from here"** strip that opens a tray — **Steer away** (*less like this sound*)
> and **Dig deeper** (*Same vibe, less familiar*) — with "Both options rebuild the whole
> journey" said at the moment of choosing. Endpoint cards stay bare. Cards say **`· 0:30`**.
> The landing page leads with a promise and offers **three ready-made journeys** for a first
> visit. A rebuild now confirms itself even when the server answers faster than the eye: the
> message is **held** long enough to read, then the artists that actually changed are
> **ringed**.
>
> **⚠ Three claims an editor must not revert**, detail in the handoff: the strip says
> "Reroute from here" and **not** the design's "Not this step"; the clip-length line stays
> **off** the landing page; and the landing page carries **no mechanism sentence** — all
> three are owner decisions, and two of them are deliberate departures from the supplied
> design.
>
> **`DEP-34-FIX` is DONE.** Both `ARTISTPATH_DEPLOY_GRAPH_KEY` and
> `ARTISTPATH_DEPLOY_SIDECAR` are now required. **Both, not just the key** — the two defaults
> agreed with each other, so requiring one would only have moved the silent revert into the
> checksum. `infra/app.py` had no test at all (`QUA-10`); it has three, all shown red against
> the reinstated defaults before being kept.
>
> **⚠ NEW AND OPEN — `SNS-1`, and it is the owner's because it needs his inbox.** The
> billing alarm's SNS topic has **zero subscriptions**, checked directly rather than inferred
> from the drift report. If the billing alarm fires, nobody is told. **Pre-existing and not
> caused by this deploy**, which touched no CloudFormation — surfaced by this closeout's
> drift gate. `DEP-17` records App Runner billing as unmeasured, so this alarm is the only
> thing watching cost.
>
> **⚠ ONE GATE DID NOT RUN and is not a pass:** the frontend dependency scan
> (`npx snyk test`) hit the org's monthly limit. **Mitigation, not a pass:** no dependency
> manifest changed — every lockfile is byte-identical to `main` — so the last passing scan
> covers this exact set. Tracked as `FE-SNYK-1`.
>
> **✅ THE TEST QUEUE IS EMPTY.** The owner discharged both 2026-08-06 live-site entries on
> 2026-08-07: the `MSW-` map **fully exercised on desktop and mobile, no defects or
> regressions**, and the artwork fix confirmed. **⚠ That is the first evidence of any kind
> that the `MSW-` map holds up in real use by a person — and it does NOT retrospectively
> license the `GBL-` null**, which that adoption overrode knowingly. A new entry is queued
> for the UI above.
>
> **New standing rule in `TEST-QUEUE.md`, from an owner ruling:** that file is for **defects
> and functionality only, never for long-run judgement** of how the app feels. Such an entry
> has no completion state and could never be discharged.
>
> **Entry point:** the current handoff
> [`2026-08-07-HANDOFF-bypass-tray-ux.md`](2026-08-07-HANDOFF-bypass-tray-ux.md). Reasoning:
> [`2026-08-07-bypass-tray-ux-execution-log.md`](2026-08-07-bypass-tray-ux-execution-log.md)
> — **its §3 records four defects in this session's own work**, one of which reached the
> owner as a false claim about the product and was caught by his disbelief. Design export:
> `frontend/design/2026-08-07-bypass-tray/`. Branch `bypass-tray-ux`, **PR #89 MERGED** at
> `a7a8b9a`. **The work is on `main` and in production, so the trunk and the live site
> agree.**
>
> **Nothing is running on any port** — 8000, 5173 and 5174 were swept and are free.
>
> ---

> ## ✅ THE `TCR-` RE-RUN IS COMPUTED, 2026-08-06 (night, later) — ALL GATES PASSED, NO ENRICHMENT ANYWHERE. ~~**The next action is the OWNER'S: nothing is blocked, and Option C is now unblocked.**~~ *(SUPERSEDED on next actions by the block above. **Option C is still unblocked and still his** — that half is unchanged, only its ranking as "the next action" is. The two hand tests it named are **DISCHARGED**, and `DEP-34-FIX` is **CLOSED**.)*
>
> **The owner's Option A ruling was executed as ruled:** a NEW pre-registration
> (`specs/2026-08-06-thin-catalogue-rerun-preregistration.md`, `TCR-`, committed with its
> live-fetched anchors before the counter ran), a fresh session, the fired `TCE-` record
> untouched. **`TCR-G1` passed 5 of 5 externally anchored cells** — total live↔dump drift
> across four orders of magnitude was one release-group — **and the outcomes computed in
> both arms.**
>
> **The result, in one sentence: artists with nothing of their own recorded do NOT crowd
> the top of similar-lists — every licensed signal points the opposite way** (arm A's
> supplements read *depleted*; arm B's primary read is barred by the pinning gate exactly
> as predicted, which is a finding about the drop filters, not a fault). **⚠ No
> pre-registered branch fires as written** — a recorded gap in the carried branch table
> (`C1` null while `C3` landed beyond null at depleted) — **but both adjacent branches
> carry the identical consequence, so the closure is licensed: the thin-catalogue
> hypothesis is unsupported, and the co-credit investigation closes with three mechanisms
> tried (`CCR-`, `RCC-`, `TCR-`) and none explaining the class.** Read the results
> README's §4 before citing any branch.
>
> **⚠ The same-name POPULATION question is STILL OPEN and was NOT touched:** the
> pre-registered eyeball read found top contributors dominated by **correctly resolved
> credited personnel** (the `CAU-` class), not same-name junk — that neither surfaces nor
> closes the population question. **Option C was deferred "until after the re-run"; the
> re-run has happened, so scheduling it is now purely his call.**
>
> **Figures are owned by `builder/analysis/2026-08-06-tcr-thin-catalogue-rerun/` — cited,
> never restated.**
>
> **Entry point:** the current handoff
> [`2026-08-06-HANDOFF-tcr-rerun.md`](2026-08-06-HANDOFF-tcr-rerun.md). Reasoning:
> [`2026-08-06-tcr-rerun-execution-log.md`](2026-08-06-tcr-rerun-execution-log.md).
> Governing document: `specs/2026-08-06-thin-catalogue-rerun-preregistration.md`. Branch
> `cocredit-relationship-probe`, **PR #87 MERGED 2026-08-07** at `95901d4`. **The work is on
> `main`; the branch is spent — new work branches from `main`.**
>
> **The stale Vite server the previous block flagged (port 5174, PID 249084) is GONE** —
> verified at this closeout; nothing further is owed on it.
>
> ---

> ## ~~▶ `TCE-` IS VOID — ITS GATE FIRED, 2026-08-06 (night). **The next action is WORK, and the owner has RULED its remit: RE-RUN under a NEW pre-registration, fresh session.**~~ *(DONE — the ruled re-run happened and is the block above, which owns current state. The `TCE-` record itself remains VOID and untouched, as ruled.)*
>
> **The owner's decision, taken 2026-08-06 (night) and recorded as HIS — do not re-litigate it:**
>
> - **Option A: `TCE-` is re-run under a NEW pre-registration** — **not** an amendment — with
>   **gate thresholds anchored on externally measured values**, by a **fresh session**.
> - **The fired `TCE-` record STANDS UNTOUCHED.** The gate firing is the record. Do not amend
>   `TCE-G1`, do not re-band it, do not retro-fit criteria to it.
> - **Option C (a same-name POPULATION probe) is DEFERRED until after the re-run.**
>   Deliberately. **Not abandoned and not closed.**
> - **The replacement pre-registration was deliberately NOT drafted** by the retiring session.
>   Its absence is intentional, not an oversight.
>
> **What happened.** Three mechanisms have now been tried against the owner's observed class.
> `CCR-` (band membership) and `RCC-` (shared recording credits) both returned null. `TCE-`
> (thin catalogue) **never produced an outcome at all**: `TCE-G1`, its instrument-validation
> gate, ran first and alone and **one of four cells failed**, so the probe is **VOID** and the
> run stopped at phase 3 of 7. **There is no `TCE-C1`/`C2`/`C3`/`C4`/`C5`, no `Δ_R`, and no
> branch may be inferred.**
>
> **⚠ The instrument is CORRECT and the threshold was wrong — both halves travel together.**
> The dump counter agrees **exactly** with the live MusicBrainz API and returns 0 for the
> motivating case; the failing bar was set by reasoning from a *recording* count without
> checking what it implies for *release-groups*. **That does not un-void the probe**, and a
> threshold corrected after seeing the value it failed on is not a threshold. Recalibrating
> after a gate fires has a precedent here — `MSW-G3` — and there too it was the owner's call.
>
> **⚠ THE LAURA LEE PUZZLE IS PARTIALLY DISCHARGED, AND THE HALVES MUST NOT BE COLLAPSED.** The
> same-name collision hypothesis is **dead for Laura Lee** — both Laura Lees resolve separately
> with disjoint coherent lists, so **`BYP-13` is not operating on the graph's edges** — and the
> case cannot reach a user anyway, being dropped from the adopted artifact. **The POPULATION
> question is OPEN**: one correctly-resolved pair demonstrates nothing about a rate. Struck in
> place at the previous execution log's §6 item 1.
>
> **⚠ New evidence pointing at that open item, found by accident.** MusicBrainz **itself**
> mis-files between the two Laura Lees, inconsistently across levels — the *recording* of *Not
> Up for Discussion* under the Khruangbin member, the *release-group* under the soul singer. So
> **`TCE-G1`'s first cell passed partly because of a mis-filing.** `n = 1`; it licenses no rate
> and is **NOT** evidence for the thin-catalogue mechanism.
>
> **Figures are owned by the three `builder/analysis/2026-08-06-{laura-lee-closure,
> tce-c1-statistic-behaviour,tce-thin-catalogue}/` directories — cited, never restated.**
>
> **Entry point:** the current handoff
> [`2026-08-06-HANDOFF-tce-void.md`](2026-08-06-HANDOFF-tce-void.md). Reasoning:
> [`2026-08-06-tce-thin-catalogue-execution-log.md`](2026-08-06-tce-thin-catalogue-execution-log.md)
> — **its §7 lists what a re-run must not repeat and is the section to read before drafting.**
> Governing document (VOID, retained): `specs/2026-08-06-thin-catalogue-edge-preregistration.md`
> with `TCE-AM1` and `TCE-AM2`. Branch `cocredit-relationship-probe`, ~~**draft PR #87 — NOT
> merged.**~~ *(MERGED 2026-08-07 at `95901d4`.)*
>
> **⚠ One thing needs the owner and is not blocked on anything:** a **stale Vite dev server on
> port 5174, PID 249084**, started 08:24 and missed by the earlier sweep, which checked 5173 and
> 8000 only. Nothing queued needs a local server. The retiring session was blocked from stopping
> it; the command is in the handoff.
>
> ---

---

> ## ✅ THE CO-CREDIT INVESTIGATION IS COMPLETE, 2026-08-06 (night) — TWO NULLS, NOTHING ADOPTED. ~~**The next action is the OWNER'S and it is USE: the two queued hand tests, unchanged.**~~ *(SUPERSEDED on next actions by the block above: its open item 1 was taken, and the next action is now ruled WORK. **The two queued hand tests are still outstanding and still his** — that half is unchanged, only its ranking as "the next action" is.)*
>
> **The owner observed that novel artists arriving at depth looked disproportionately like solo
> acts of known bands, and hypothesised that ListenBrainz over-weights similarity between
> artists who record together.** His worked case: Laura Lee, a Khruangbin member with no solo
> releases, at rank 2 on Leon Bridges' list. **The mechanism is confirmed at the source**
> (`LBS-1`: a session pairs listens whose artists *and* credits differ, weight 1 main / 0.25
> featured) **and is confirmed to operate** — but **two independent probes decline to attribute
> the class he saw to it.**
>
> - **`CCR-` — `null`, and INSTRUMENT-LIMITED.** `inc=artist-rels` carries band membership, not
>   shared recording credits, so **Laura Lee scores `False` on it**. **Read as: untested at
>   population scale, and equally unsupported. Both halves travel together** — do not read it
>   as evidence against the hypothesis.
> - **`RCC-` — `null`, and the instrument WAS validated** (it finds the Khruangbin/Leon Bridges
>   collaboration). `RCC-C2` came back `general` with **the sign opposite to the prediction**:
>   ordinary obscure artists show *more* co-credit at rank 1 than the class does.
> - **B1 (the `p99_log_clip` rescale) — descriptive, no pre-registration by design.** It
>   **corrected an overstatement made earlier in the same session**: clipping is minor, ordering
>   survives, and **a rescale change is NOT a low-risk win.**
>
> **Figures are owned by the three `builder/analysis/2026-08-06-*` directories — cited, never
> restated.**
>
> **Entry point:** the current handoff
> [`2026-08-06-HANDOFF-cocredit-investigation.md`](2026-08-06-HANDOFF-cocredit-investigation.md).
> Reasoning: [`2026-08-06-cocredit-investigation-execution-log.md`](2026-08-06-cocredit-investigation-execution-log.md).
> Governing documents: `specs/2026-08-06-cocredit-relationship-preregistration.md` and
> `specs/2026-08-06-shared-recording-preregistration.md` (the latter carrying `RCC-AM1`).
> Branch `cocredit-relationship-probe`, ~~**draft PR #87 — NOT merged.**~~ *(MERGED 2026-08-07 at `95901d4`.)*
>
> **⚠ THIS SESSION RETIRED MID-FLIGHT on the degradation tell**, after four file-or-design
> selection errors — **all four caught and corrected in-session, none reaching a committed
> document uncorrected.** Its handoff is written in the enumerated form: **read its lists
> rather than trusting its judgement**, and note it carries figures that exist in **no** other
> file and will be lost if not re-run.
>
> **Open, each with a success condition in the execution log §6:** ~~the **Laura Lee puzzle**
> (her 214 edge is not a co-credit artefact under the validated definition — a same-name MBID
> collision is live but weakened; **if it holds it is `BYP-13` reaching the graph's edges
> rather than a clip**)~~, **B2** (does an alternative rescale change which artists appear —
> testable without a rebuild, needs a pre-registration), and the **duplicate-artwork detector**
> for `CLIP-1`.
>
> > **◐ THE LAURA LEE PUZZLE IS STRUCK HERE AND ONLY HALF-DISCHARGED — 2026-08-06 (night).**
> > The same-name collision hypothesis is **DEAD for Laura Lee** (so **`BYP-13` is NOT reaching
> > the graph's edges**, and she is dropped from the adopted artifact anyway), and **OPEN as a
> > population question** — one correctly-resolved pair measures no rate. **Do not collapse
> > those two halves in either direction.** Owner's ruling: deferred until after the `TCE-`
> > re-run. Detail in the top block; struck in place at the previous execution log's §6 item 1.
> > *(Added by the closeout audit: this retained block's "superseded on next actions" line
> > updates the ranking, not this claim, and a reader landing here from a citation would have
> > read the item as simply open.)*
>
> **⚠ CLOSED, and not to be re-litigated: widening the drop rule.** The owner ruled it out
> 2026-08-06 — **he does not think Andrew VanWyngarden or Zach Condon should have been dropped**
> — and two nulls now point the same way. `ULF-` already catches the clearest cases.
>
> **`ULF-3` was RE-TESTED at this closeout rather than copied forward, per the instruction
> below: it remains HALF-DUE, unchanged.** Era-pinned probes still name the old flags and all
> three flags are still live in `BuilderConfig`.
>
> ---

> ## ✅ THE CLIP COVER-ART DEFECT IS FIXED, LIVE AND MERGED, 2026-08-06 (later). **The next action is the OWNER'S and it is USE: the queued hand test.** `DEP-34-FIX` is open and is his.
>
> **The owner reported album art loading inconsistently on the live site, clips fine. It was a
> real defect, it is fixed, and `artistpath-api:641ced7` is deployed and verified.**
> `_from_deezer_artist` read the card image from `row["artist"]["picture_medium"]`, which
> Deezer's `/artist/{id}/top` **does not send** — only `/search` does. Every clip resolved by
> artist id came back with an empty image while the clip played perfectly.
>
> **It shipped with the `MSW-` map switch without being caused by it**: the id path fires only
> for artists carrying a `deezer_id`, and `graph-msw-tu50.bin` is the first artifact to carry
> them. Authored 2026-08-02, detonated 2026-08-06. **The `MSW-` adoption is untouched** — the
> graph, its checksum and its counts were verified unchanged after the deploy.
>
> **404 stale clip-cache entries were cleared after the deploy**, so the fix is visible now
> rather than bleeding in over the 30-day TTL. Verified on the live site: two long journeys at
> 0 / 10 / 20 `known` presses, **every card resolving both a clip and an image**.
>
> **Visible change, and it was the owner's call:** Deezer-resolved cards now show an **album
> cover** rather than an artist photograph. iTunes cards always did.
>
> ### ⚠ THE MOST IMPORTANT THING HERE IS NOT THE CLIP FIX — it is `DEP-34`
>
> **An API-only deploy silently reverts the graph.** `ARTISTPATH_DEPLOY_GRAPH_KEY` defaults to
> the pre-`MSW-` artifact, `.env.deploy` does not set it, and it is per-deploy rather than
> per-machine. **This deploy would have rolled the map back and undone the previous day's
> adoption**, from a session with no intention of touching it.
>
> Caught by `cdk diff` before `cdk deploy`. **Nothing downstream would have caught it** — the
> runbook's `/health` check compares the live service against whichever sidecar it is handed,
> so a wholesale revert is self-consistent and passes. `infra/README.md` §1, §4, §5, §0 and §8
> are corrected. **Read §4 and §5 before any future deploy.**
>
> **`DEP-34-FIX` is open and is the owner's:** make both variables required in `infra/app.py`,
> exactly as `ARC-6` did for the image tag five lines below. **Should be taken before the next
> artifact adoption** — until then the mitigation depends on an operator reading a diff.
>
> **Entry point:** the current handoff
> [`2026-08-06-HANDOFF-clip-cover-art.md`](2026-08-06-HANDOFF-clip-cover-art.md). Reasoning:
> [`2026-08-06-clip-cover-art-execution-log.md`](2026-08-06-clip-cover-art-execution-log.md).
> Branch `clip-cover-art-fix`, **PR #85 MERGED 2026-08-06** at `fee46e2`, commits `641ced7`,
> `9183893` and `a3a5217`. **The work is on `main`, so production and the trunk agree.** The
> branch is spent; new work branches from `main`.
>
> **`CLIP-1` is untouched and must not be conflated with this** — that is about *which track*
> a card plays, this was about *which image*. Still the owner's call.
>
> ---

> ## ✅ THE `MSW-` MAP SWITCH IS ADOPTED AND DEPLOYED, 2026-08-06. **The next action is the OWNER'S and it is USE: press the live site.** Nothing is blocked; no session owes anything.
>
> **The new map is LIVE at `https://musicapp.cmiller.io`.** The owner gave the Seam 3 go after
> pressing the candidate locally, and asked for the rest of the plan including production.
> Tasks 11 and 12 both ran. **Four defaults flipped in one commit** (`a06ab58`): the default
> graph, the `known` fame ramp, the builder's cap rule, and the fame requirement. **The knob
> values and the artifact's identity are owned by the execution log's Task 9 and Task 11
> sections and by the manifest sidecar — cited, never restated here.**
>
> **⚠ THIS IS AN OWNER OVERRIDE OF THE `GBL-` NULL.** The null's pre-registered consequence was
> *"production stands and Option A closes without adoption"* (margin 3 against a bar of 5). He
> took the override knowingly on 2026-08-05, on `CAU-`'s coherence pass at his own bar, the
> compromised instrument behind the null, and the `ULF-` filter fix. **Neither `GBL-` nor
> `CAU-` licensed it** — `CAU-` §6 bars comparison at any strength and `GBL-` §5's run-once
> rule still binds. **Never record this as evidence-backed adoption.**
>
> **⚠ THE DIRECTION OF STALENESS HAS INVERTED, and it is the thing to carry.** For three months
> the risk was a document claiming something was adopted when it was not. It is now the
> reverse: **"nothing is adopted" / "every default is still off" is stale wherever it describes
> the present.** The identical sentence inside a frozen `GBL-`/`CAU-`/`ULC-` findings row is
> **correct** — it describes what that track did. **This cannot be fixed by grep; read for
> tense.**
>
> **Entry point:** the current handoff
> [`2026-08-06-HANDOFF-msw-adoption.md`](2026-08-06-HANDOFF-msw-adoption.md);
> [`2026-08-06-HANDOFF-msw-seam3.md`](2026-08-06-HANDOFF-msw-seam3.md) remains authoritative
> for the Task 10 verification internals. Operational document:
> [`plans/2026-08-05-msw-package-adoption.md`](plans/2026-08-05-msw-package-adoption.md) — now
> **COMPLETE**, and carrying a correction block above Task 12 Step 1. Reasoning:
> [`2026-08-05-msw-execution-log.md`](2026-08-05-msw-execution-log.md) — **its §0 is the
> authority record and must be read before describing this work.** Branch `msw-adoption-flip`,
> **PR #83 MERGED 2026-08-06** at `3458594`. **Tasks 11–12 are on `main`, so the adoption is in
> the trunk as well as in production.**
>
> **What is waiting on him, and neither blocks anything:**
>
> - **The queued hand test on the LIVE site** (`TEST-QUEUE.md`, topmost entry). This is the
>   first use of the new map by a person on the real address. **Expect familiar journeys to be
>   DIFFERENT — that is the release, not a fault.**
> - **Two local servers from the morning are still running** (ports 5173 and 8000) and are now
>   redundant. Left up deliberately because he was still testing and asked to be told before
>   anything is stopped.
> - **The standing context layer grew: +333 characters unconditional** (`CLAUDE.md`'s Graph
>   shape correction) **and +6 lines conditional** (`ml-graph-analyst.md`'s body). Neither
>   correction was optional; the size is his call.
>
> **Three defects were found in the plan's own Tasks 11–12 by executing them, and one was
> serious.** Task 12 had **no image-build step** — executing it as written would have shipped
> the new map under the old code, leaving the ramp off in production while every check the plan
> specifies passed. Detail in the execution log's Task 12 section; the plan now carries the
> correction inline.
>
> **New deferral, logged by the owner and NOT acted on: `CLIP-1`.** A clip can be the right
> artist and still misrepresent them — a guest credit or someone else's remix rather than their
> own work. **Distinct from `BYP-13`** (wrong artist of the same name) and from the
> un-listenable class (no catalogue at all). Not new, not caused by this work, not measured.
> Condition and both named examples in the execution log's `CLIP-1` section. **Whether it is
> worth fixing is his call.**
>
> **`ULF-3` is now HALF-DUE** — a shipped build has routed on a `ULF-` list (satisfied), but the
> era-pinned probes still name the old flags (not satisfied). It stays open and must be
> **re-tested** at the next closeout, not copied forward.
>
> **Unchanged and not `MSW-`:** `ULC-F3` still blocks any crawl extension; `ULC-F4` is its own
> track.
>
> ---

> ## ▶ SEAM 3 IS REACHED — `MSW-` TASK 10 IS COMPLETE, 2026-08-06 (night). **The next action is the OWNER'S DECISION: go / no-go on Task 11, which flips the three defaults.**
>
> **Seam 3 is an OWNER STOP.** No default flips, and Task 11 does not begin, without his go.
>
> **A local server is left running for him**, deliberately: `localhost:8000` serving the
> candidate artifact **with the ramp at `0.01`** — i.e. exactly what Task 11 would ship. It runs
> off a **scratchpad factory override, not a committed default**; `config.py` is untouched and
> killing the process returns everything to today's behaviour. `npm run dev` in `frontend/` to
> press it.
>
> **What Task 10 added, and the figures are owned by the execution log's Task 10 section and by
> `builder/analysis/2026-08-05-msw-verification/` — cited, never restated.**
>
> - **`MSW-V1`** (do the artists the coherence audit could not listen to survive?) — **passed**;
>   the stop branch does not fire.
> - **`MSW-V2`** (how often does a journey's middle land on someone with nothing of their own to
>   play?) — measured, **one knob against `ULC-A4`, now machine-asserted**. A **report row, not
>   a gate**: no threshold was pre-registered and **none was supplied**. ⚠ Its paired median
>   reads zero while its mean moves by double digits, because the class is **concentrated in a
>   minority of journeys** — `ULC-R1`'s recorded statistic defect reproducing, deliberately not
>   patched. **Two journeys got worse** and are named.
> - **`MSW-V2B`** (do the journeys you see actually differ from the ones that were listened to?)
>   — **NOT in the plan; folded in on the owner's authorisation**, and it closes the question the
>   previous handoff called the most decision-relevant thing unmeasured. **They do differ, at
>   depth**: on the broader famous-pair set nearly half the journeys change at twenty presses —
>   **but on the eight pairs actually listened to, almost none do.** Both halves travel together.
>   Green anchor and red control both behaved.
> - **`MSW-V3`** (does the app work?) — **yes, on both configurations.** `/health` matches the
>   sidecar, Playwright 5/5, three pairs pressed to ten with the interior changing at every
>   step, **every card resolved a clip and no card was dead**. ⚠ **Audibility is NOT confirmed
>   and is not claimed** — the session cannot listen.
> - **`B2`/`B3`/`B4`** — run, and **`B4` found a real defect in the verifying session's own
>   work** (a docstring asserting held-constants no code checked). Fixed by making the code true.
>
> **⚠ The one thing that survived verification and is the sharpest input to his decision:** an
> artist in the un-listenable class reached a real card, and **his clip resolved perfectly** — to
> a charity-ensemble track that is not his own work. **"The clip resolves" is not "this artist
> has something of their own", and no automated check here can tell them apart.**
>
> **Task 9 outcome:** the candidate artifact is built, deterministic across two runs, and its
> identity is committed. **A third defect was found in the plan's own commands** — the build
> would have produced a **fameless artifact while exiting 0** — fixed per-invocation with a
> `--require-fame` flag, never by flipping the default. **`MSW-G3` fired red for the first
> time.** The build was then **REJECTED by acceptance**, which stopped the track and went to
> the owner; **he took Option A and recalibrated the bounds deliberately** (his decision,
> recorded as his). **Task 10:** `MSW-V1` **passed** with its stop branch not firing, and
> `MSW-V4` returned a bound — including a **premise correction** that the deviation is two
> knobs rather than one.
>
> **Entry point:** the current handoff
> [`2026-08-06-HANDOFF-msw-seam3.md`](2026-08-06-HANDOFF-msw-seam3.md);
> [`2026-08-06-HANDOFF-msw-task10-midflight.md`](2026-08-06-HANDOFF-msw-task10-midflight.md)
> remains authoritative for Task 9's internals and the Option A recalibration,
> [`2026-08-06-HANDOFF-msw-task8-midflight.md`](2026-08-06-HANDOFF-msw-task8-midflight.md)
> for Task 8's, and
> [`2026-08-05-HANDOFF-msw-seam2.md`](2026-08-05-HANDOFF-msw-seam2.md) for Seam 2's.
> Operational document:
> [`plans/2026-08-05-msw-package-adoption.md`](plans/2026-08-05-msw-package-adoption.md)
> (12 tasks, seams at 5/7/10/12). Reasoning:
> [`2026-08-05-msw-execution-log.md`](2026-08-05-msw-execution-log.md) — **its §0 is the
> authority record and must be read before describing this work.** Branch
> `msw-package-adoption-plan`, **PR #81 MERGED 2026-08-06** at `aafcd6e`. **Tasks 1–10 are on
> `main` and every default is still off** — merging landed the capability, it adopted nothing.
> **Tasks 11–12 need a NEW branch off `main`**; the old one is spent.
>
> ~~**⚠ One question is OPEN and is the most decision-relevant thing unmeasured:** `MSW-V4`
> bounds what the router *adds up* and explicitly does not bound what it *chooses*. **No
> journey has been run on this artifact.**~~ *(**CLOSED 2026-08-06 (night) by `MSW-V2B`**, run
> on the owner's authorisation. Journeys have now been run — programmatically and by hand — and
> the deviation **does** change routes at depth on the broader pair set while barely touching
> the listened pairs. Figures in the execution log's Task 10 section.)*
>
> **⚠ THIS ADOPTION IS AN OWNER OVERRIDE OF THE `GBL-` NULL.** The null's pre-registered
> consequence was *"production stands and Option A closes without adoption"* (margin 3
> against a bar of 5). The owner took the override knowingly on 2026-08-05, on `CAU-`'s
> coherence pass at his own bar, the compromised instrument behind the null, and the `ULF-`
> filter fix. **Neither `GBL-` nor `CAU-` licensed it** — `CAU-` §6 bars comparison at any
> strength and `GBL-` §5's run-once rule still binds. **Never record this as
> evidence-backed adoption.**
>
> **What stands, in one paragraph.** Tasks 1–7 build the whole capability and switch none of
> it on. The builder gained the trimmed-union connection rule (ported from the frozen Track B
> implementation and pinned to it by test), a `fame` fetch stage putting ListenBrainz listener
> counts in the archive so `build` stays offline, a refusal to build when fame coverage has
> drifted from the similarity population, and `fame_lb` as an additive APG1 key. The API reads
> that key, ranks it against **the served artifact's own population**, and prices a `known`
> ramp on it, refusing to boot if the ramp is live over a fameless artifact. **`cap_strategy`
> is still `mutual_knn`, `require_fame` is `False`, `w_known_ramp_fame_pctl` is `0.0`, and the
> frontend is untouched.** 224 builder + 254 api tests pass; Snyk clean on both packages.
>
> **What changed 2026-08-06 (later):** the candidate artifact **has now been built** —
> `builder/scratch/graph-msw-tu50.bin`, gitignored, identity owned by the execution log's
> Task 9 section. `cmd_build` gained `--cap-strategy` and `--require-fame`, both
> per-invocation. The **acceptance bounds were recalibrated** on the owner's Option A
> decision (node and edge only; tolerance unchanged, centre moved), and the frozen
> calibration probe at `builder/analysis/2026-07-23-acceptance-bounds/check.py` was
> **era-pinned** so it keeps demonstrating what it was written for. **No default was
> flipped and nothing is adopted.**
>
> **Owner decisions taken, not to be re-litigated:** the full package over data-only
> (`ULC-A2` has never been listened to or audited; the package is what `GBL-` heard and
> `CAU-` judged); and adopt-and-live-with-it rather than spending a fresh listen.
>
> **Task 10's own reasoning** is the execution log's **"Task 10 continued — the successor
> session"** section. **Every earlier handoff's "Claims that must NOT be reverted" list still
> stands in full** — none has been retired by this work.
>
> **Still owed and named:** Task 11 Step 0 must era-pin `cap_strategy` **and** `require_fame`
> in three analysis callers, or they silently change what they build and one refuses outright;
> ~~`MSW-V4` is an `ml-graph-analyst` dispatch at Seam 3~~ *(RUN 2026-08-06 — figures in
> `builder/analysis/2026-08-06-msw-v4-frame-deviation/`; it returned a premise correction,
> two knobs not one)*; **Seam 3 is an OWNER STOP** before any default flips.
> **Note Task 11 Step 0's era-pin list has a fourth sibling that is already DONE:**
> `builder/analysis/2026-07-23-acceptance-bounds/check.py` was era-pinned at Task 9 and
> needs nothing further. ~~One decision is his and is small: the D6 standing-layer cost, in the
> handoff.~~ *(DISCHARGED 2026-08-05 — the owner ACCEPTED the D6 growth; `CLAUDE.md` stands as
> committed. **Nothing is now waiting on him until Seam 3.**)*
>
> ---

> ## ✅ THE `ULF-` FILTER WORK IS COMPLETE, 2026-08-05 (night). ~~**The next action is the OWNER'S: merge draft PR #78 then the `ulc-filter-fix` draft PR**~~ *(BOTH MERGED: #78 at `7961530`, #80 at `fd6b140`)* ~~**and decide which form of the map switch to take**~~ *(DECIDED 2026-08-05: the full listened-to package. That became the `MSW-` track in the block above, which owns current state.)*
>
> **Entry point for anything `ULF-`:** the governing rule document
> [`specs/2026-08-05-unlistenable-filter-rule.md`](specs/2026-08-05-unlistenable-filter-rule.md)
> (committed before any census under the rule existed). Reasoning:
> [`2026-08-05-ulf-filter-fix-execution-log.md`](2026-08-05-ulf-filter-fix-execution-log.md).
> Current handoff: [`2026-08-05-HANDOFF-ulf-filter-fix.md`](2026-08-05-HANDOFF-ulf-filter-fix.md).
> Figures live in the frozen payloads (`builder/src/artistpath_builder/data/unlistenable_drop_*.json`,
> which own their counts and shas) and `builder/analysis/2026-08-05-ulf-census/ulf_census.json` —
> **cited, never restated.**
>
> **What stands, in one paragraph.** One merged filter (`drop_unlistenable`, default on)
> supersedes both earlier drops **without reversing either** — both adopted classes are strict
> subsets of `ULC-D2`'s and every frozen verdict carried; the subset property was verified
> against data, not assumed. The owner ruled the cut line (2026-08-05): **`ULC-D2` as ruled,
> Keith Scott the named residual false negative**; the Discogs exemption is gone (its absence
> is the fix — results §1.4). `ULC-F1` is discharged: the payloads carry the archive population
> and a mismatched population **refuses to build**, exercised against the real archive. `ULC-F2`
> is discharged: the census coverage store reused 90,159 of 98,296 artists on first run. Each
> keep records whether its clip was id-verified — the deferred `ULC-F4` track's measurement,
> collected free, **no read licensed**. A verification build passed acceptance after the owner
> struck **CROOVE** from the canonical list (a closed track's endpoint pin; the app measurably
> plays nothing for them — log §7). **Nothing is adopted, no listen spent, the trial artifact
> is scratch evidence only.**
>
> **Owner decisions taken this session, not to be re-litigated:** the cut line (`ULC-D2` as
> ruled — no soundtrack carve-in, no stricter bar); CROOVE struck (recorded at the site in
> `acceptance.py`). **Still open and NOT this session's:** `ULC-F3` (crawl resume cannot
> extend — still blocks any crawl extension), `ULC-F4` (keep-check name-resolution defect, its
> own track, now with its measurement waiting in the payloads' `keep_clip_provenance`).
>
> **⚠ What this does NOT change:** the `GBL-` null stands (a re-listen on the *filtered*
> candidate package is expressly permitted as a new candidate — that is the owner's §4.1
> decision, not a session's); the production-data rebuild stays TABLED by his 2026-08-05
> ruling; no `ULC-` figure moved.
>
> ---

> ## ✅ THE `ULC-` UN-LISTENABLE-CLASS TRACK IS COMPLETE, 2026-08-05 (evening). ~~**The next action is WORK and its remit is set: THE FILTER FIX.**~~ *(DONE — the `ULF-` block above owns current state; `ULC-F1`/`F2` are struck in results §5.)* ~~The owner's one action is merging draft PR #78.~~ *(Still open, now sequenced with the filter PR — see above.)*
>
> **Results of record, and the entry point for anything `ULC-`:**
> [`findings/2026-08-05-unlistenable-class-results.md`](findings/2026-08-05-unlistenable-class-results.md)
> — **it owns the `ULC-` figures**; its §4 is the options list, §4.1 pins down what "switch to the
> new map" actually costs, §5 the follow-on items with conditions, §7 a correction owed to the
> `CAU-` note. Raw data: `builder/analysis/2026-08-05-unlistenable-class/` — **cited, never
> restated.** Current handoff: [`2026-08-05-HANDOFF-ulc.md`](2026-08-05-HANDOFF-ulc.md).
> Reasoning: [`2026-08-05-ulc-execution-log.md`](2026-08-05-ulc-execution-log.md). Governing
> document:
> [`specs/2026-08-05-unlistenable-class-preregistration.md`](specs/2026-08-05-unlistenable-class-preregistration.md)
> (five amendments, each committed before the stage it affects).
>
> **What stands, in one paragraph.** Two things were measured and **they answer differently, which
> is the result** (figures §1.2 and §1.3, cited and never restated here): how many artists have
> nothing of their own to listen to — a similar share of every cleaned map, slightly *smaller* on
> the candidate data — and how often you actually meet one: **never** on the production data across
> every measured journey, **regularly** on the candidate data, on one journey reaching most of the
> interior. **The class is a routing problem, not a population problem.** The
> gate `ULC-G1` passed `separable`; **`ULC-R1` did NOT fire** — the run state was 95/96 and, more
> importantly, its pre-registered statistic could not see this effect, which is recorded as a design
> defect and **deliberately not patched**. The live site is a separate and worse case — roughly
> double any cleaned build (§1.2) — for the boring reason that it predates both filters. **Nothing is adopted, no default changed, no
> shipped code touched.**
>
> **The next session's remit, set by the owner: the filter work.** `ULC-F1` (drop-list keys must
> carry population identity, or a crawl extension silently under-filters), `ULC-F2` (the census must
> write back what it learns), the filter fix itself — **and note the obvious fix is insufficient**,
> since requiring a *sole* Discogs credit still would not catch a drum sample library — then
> re-censusing both drop lists.
>
> **Owner decisions already taken that constrain what follows:** the production-data rebuild is
> **TABLED** (he wants the candidate map live first, accepting that the next deployment carries
> three changes at once and cannot isolate them); ordering is write-up → filters → map switch; and
> **"switch to the new map" is not yet pinned down** to data-only or the full listened-to package —
> results §4.1 sets out both, and **neither has a listening test behind it.**
>
> **⚠ Two things `ULC-` does NOT do:** it does not reopen the `GBL-` null (`ULC-B2`), and it takes
> no position on which package sounds better. A `worse_on_candidate` reading is **not** evidence
> against the rebuilt graph's listen.
>
> ---

---

> ## ✅ THE `CAU-` COHERENCE AUDIT IS SCORED AND WRITTEN UP, 2026-08-05 (later). **`CAU-` is COMPLETE.** ~~The owner's actions are a DECISION (below) and merging draft PR #77.~~ *(BOTH DISCHARGED: PR #77 merged `cf36435`; the §4 decision was taken — **option B**, which became the `ULC-` track in the top block, which owns current state.)*
>
> **Results of record, and the entry point for anything `CAU-`:**
> [`findings/2026-08-05-coherence-audit-results.md`](findings/2026-08-05-coherence-audit-results.md)
> — **it owns the `CAU-` figures**; its §4 is the options list, §5 the response to the owner's
> sealed note, §6 an addendum on the drop filters. Raw data:
> `builder/analysis/2026-08-04-coherence-audit/cau_judgements.json`, `cau_result.json`,
> `cau_page_data.json` — **cited, never restated. ⚠ One correction against §6: its "22 of 23
> never evaluated" counts the audit's 12 planted controls in the denominator; the real figure is
> 10 of 11 and §6's conclusion is unaffected — `ULC-AM0`.** Handoff, now superseded on next
> actions by [`2026-08-05-HANDOFF-ulc.md`](2026-08-05-HANDOFF-ulc.md):
> [`2026-08-05-HANDOFF-cau-scoring.md`](2026-08-05-HANDOFF-cau-scoring.md). Reasoning, **two
> logs covering the two chunks**:
> [`2026-08-05-cau-audit-build-and-run-execution-log.md`](2026-08-05-cau-audit-build-and-run-execution-log.md)
> (the build and the run, written by that session while it was still live and **before it read
> any result** — its §5 is the design rationale nothing else states, and its §6 records a gate
> that was **never reached**) and
> [`2026-08-05-cau-scoring-execution-log.md`](2026-08-05-cau-scoring-execution-log.md) (the
> scoring and write-up).
>
> **What stands, in one paragraph.** All 77 judgements were scored by a session that did not
> build or run the audit. **`CAU-G1` passed 12 of 12, so nothing below it is void.** `CAU-C1`
> landed on `meets_bar` — **by one card**, and that margin travels with every citation.
> `CAU-C2` did not fire. **`CAU-C3` FIRED**, and the findings note both reports its
> pre-registered reading ("unfamiliarity was the barrier; the audit's own premise is wrong")
> **and argues against it**: eight of the nine can't-tells record that there was **nothing to
> listen to** — session musicians, band members and producers with no solo output — which is a
> third cause the pre-registration's binary did not anticipate. **Both halves are on the record
> deliberately and neither may be deleted to resolve the tension.** The owner's sealed note,
> opened only after the analysis was committed, **reached the same mechanism independently and
> named the same worked artist.** **Nothing is adopted, no default changed, no shipped code
> touched, and the `GBL-` null is untouched.**
>
> **The decision waiting on the owner, and it is his because it is adoption-adjacent and spends
> his time:** which of the findings note's §4 options to take — adopt and live with it (Gate 1
> is personal use, so the blast radius is himself), count the un-listenable class offline
> first, or both. **§4 frames these as sequential and §5 corrects that: they are not.**
>
> **A finding that is not `CAU-` and is the most actionable thing the track produced
> (findings §6):** the class the audit found slipped past **both** drop filters, because
> `drop_no_release_tail` fires only at zero release-group credits and `drop_featured_credit`
> only when none are sole — so **a single sole credit exempts an artist from both.** Verified
> against both committed `ALG-B` lists: 22 of the 23 artists behind a bad or unjudgeable
> verdict were **never evaluated by either rule.** Separately, the featured-credit keep-check
> resolves clips **by name** and about half its keeps had no recorded id to verify against — a
> `BYP-13` exposure its own census disclosed and never acted on.
>
> ### 🅿 Parked by the owner, 2026-08-05 — the novelty/coherence frontier
>
> **Not a next action, not scheduled, and explicitly not confirmed.** Raised in conversation
> after the `CAU-` scoring and parked at his instruction so it survives the session.
>
> The stated goal has always been that **novelty-likelihood rises as bypass count rises**. Its
> unstated companion is that **coherence probably falls** as it rises — so for any given pair
> there is a press count beyond which the journey stops being worth showing, and the two curves
> cross somewhere. Nothing has measured either curve; this is a shape, not a finding. **He is
> explicitly not claiming the rebuilt graph has the gradient, not guessing where any crossing
> point is, and not proposing this as a priority.**
>
> **The design consequence that is already live, and is the reachable half:** the `GBL-` depths
> (0, 10, 20) were chosen against the production graph. If a graph reaches novelty faster, the
> same press count sits at a **different position on each graph's own curve**, so a fixed depth
> is not a matched comparison between two graphs — it is an uncontrolled variable that no
> factor table has carried, because until there was a graph that moved quickly it could not
> bite. **This changes nothing about `GBL-`**, whose null was pre-registered and run-once and
> stands; it is a constraint on any *future* comparison.
>
> ### ✅ The `TEST-QUEUE.md` backlog was a false alarm, and it is closed
>
> **Six consecutive closeouts flagged "eight 2026-07-22→27 entries still `QUEUED` and
> unruled-on". There is no such backlog and there never was.** Discharging an entry in that
> file prepends a `## DONE` heading and **keeps the original `## QUEUED` heading** beneath it,
> so a grep for `## QUEUED` returns discharged entries. All ten such headings (the count itself
> had gone stale at eight) sit directly beneath a `DONE` of the same title. **Zero items are
> outstanding.** The counting rule is now written at the top of `TEST-QUEUE.md` so the next
> closeout does not re-report it.
>
> ~~**Still open, and genuinely so:** the owner's 2026-08-04 **no-commercialization ruling** is in
> memory but not yet in the repo record — it belongs in `PRODUCT-REQUIREMENTS.md`.~~
> **✅ DISCHARGED 2026-08-05 (later), by a documentation session on branch
> `docs-maintenance-0805`.** Landed as **`PRODUCT-REQUIREMENTS.md` §11**: `REQ-43` (no
> commercialization — none or donations only, no ads, no paid features, ever) and **`REQ-44`,
> the owner's condition for recording it — nothing is built on that ruling's consequences
> without confirming with him first.** §11 owns the detail; do not restate it here.
>
> **Two corrections it produced, both against what six closeouts had carried forward.** The
> ruling **supersedes a citable constraint**: `specs/2026-07-19-artist-path-alpha-design.md` §1
> and `plans/2026-07-19-graph-builder.md` both bar Last.fm from becoming load-bearing *because*
> "the roadmap includes paid subscribers", and the current roadmap has no monetization content
> at all. Memory had recorded that rule-out as uncited. And **setlist.fm was never ruled out
> anywhere in the repo**, so nothing reopens for it. **Neither document was edited** — they are
> COMPLETE-role and frozen; the supersession lives in §11 and `docs/README.md`'s rows point at
> it. **`REQ-44` means none of this permits Last.fm work; it permits asking.**
>
> ---

> ## ✅ THE `CAU-` COHERENCE AUDIT WAS JUDGED, 2026-08-05. ~~**The next action is a FRESH SESSION** — it scores `cau_score.py` and writes up the result.~~ *(DONE — scored and written up; see the top block, which owns current state.)*
>
> Entry point is the superseded handoff:
> [`2026-08-05-HANDOFF-cau-audit-run.md`](2026-08-05-HANDOFF-cau-audit-run.md) — **remains
> authoritative for the build-and-run chunk's internals, and unusually load-bearing because
> that chunk left no execution log.** Governing document:
> [`specs/2026-08-04-coherence-audit-preregistration.md`](specs/2026-08-04-coherence-audit-preregistration.md)
> (`CAU-`; four amendments and one correction, **all committed before any judgement
> existed**). Raw record: `builder/analysis/2026-08-04-coherence-audit/cau_judgements.json`
> (committed `cb11b38`, before anything was scored) — **cited, never restated.** Operational
> brief: `builder/analysis/2026-08-04-coherence-audit/CAU-RUN-BRIEF.md`.
>
> ~~**⛔ `cau_owner_notes_SEALED.md` IS SEALED UNTIL THE ANALYSIS IS WRITTEN AND COMMITTED.**~~
> **✅ DISCHARGED 2026-08-05 (later) — the seal held and was opened in the right order.** The
> analysis was committed at `184b3ac`, the note opened afterwards, and the response appended as
> findings §5 at `4bdc583` with nothing above it revised. **The ordering worked and is worth
> reusing:** the independent read reached the owner's mechanism and named the same worked
> artist without having seen his note. *(Original instruction retained below as the record.)*
>
> Reading order, and the handoff owns it: prereg → `cau_judgements.json` → `cau_result.json`
> → **write and COMMIT your own read** → only then open the sealed note, and respond to it in
> a separately headed section. **This is NOT the `GBL-` ordering and the difference is
> deliberate.** `gbl_owner_notes.md` held impressions of what he heard — evidence, read before
> the tally. **This note carries his strong opinions about where the project should go**; he
> said so and asked for this ordering himself. Read first it would steer the write-up rather
> than inform it, and hand him his own view back as though it came from the data. **The commit
> boundary is the evidence the analysis was not shaped by his direction.** Provenance is
> intact: written after judging, **before anything was scored**, committed **unread** at
> `4009707` when no criterion had been computed — the commit timestamp is the evidence, not
> the file's mtime.
>
> **What stands, in one paragraph.** The owner identified a confound in the `GBL-` listen's
> instrument — a 30-second clip of one arbitrary track cannot support a coherence judgement
> about an unfamiliar artist, and that failure activates **only in the arm that succeeds at
> delivering unfamiliar artists**. `CAU-` is the one-arm follow-up it earned: the gentle
> arm's 16 deep journeys, shown whole, every interior card judged *"does this artist belong
> on this journey?"* with **proper listening** for any artist he could not place. **All 77
> judgements are in and committed; `CAU-G1`, `CAU-C1`, `CAU-C2` and `CAU-C3` are all
> uncomputed.** Three things the scoring session must carry: **`CAU-G1` is evaluated first
> and alone** — below 10 of 12 planted artists rejected, the audit is **VOID**, never a weak
> pass; **`D_all` is 53**, not 65 or 77, because the 12 cards sitting beside a planted artist
> were judged next to a fake and are excluded (`CAU-AM3`); and **`CAU-C1`'s middle band is
> deliberately neither pass nor fail** — the audit names no default there and none may be
> supplied. **Nothing is adopted, no default changed, no shipped code touched.**
>
> **⚠ The `GBL-` null is untouched by anything this audit finds.** `GBL-` §5's run-once rule
> still binds that verdict. `CAU-` measures a different thing — per-artist fit on one arm,
> not a journey-level preference between two — and **may not be used to smuggle a comparison
> back in.** §6's barred reads travel with every sentence.
>
> ~~**After scoring:** remove the `cau_page_data.json` line from `.gitignore` and commit it~~
> *(DONE, `551ed0e`.)* ~~**No closeout has been run for this chunk.**~~ *(RUN 2026-08-05
> (later), covering this chunk and the scoring one.)* **The top block owns current state.**
>
> ---

> ## ✅ THE GENTLE-ARM BLIND LISTEN IS RUN, UNBLINDED AND WRITTEN UP, 2026-08-04 (night).

*(Superseded on next actions by the `CAU-` block above; still authoritative for the `GBL-`
result itself, which stands.)*

**Original header and content follow. Last updated: 2026-08-04 (night), when THE LISTEN WAS RUN AND WRITTEN UP. The listen is
SPENT and it returned the pre-registered NULL — margin 3 against a bar of 5. Option A
closes without adoption; production stands; nothing is adopted and no default changed. The
re-crawl half of the 2026-08-04 decision is STILL UNTAKEN and untouched by the null. The
next action is the OWNER'S and it is a decision, not work.**

---

## Next

> ## ▶ THE GENTLE-ARM BLIND LISTEN IS RUN, UNBLINDED AND WRITTEN UP, 2026-08-04 (night). **The listen returned the pre-registered NULL. Option A CLOSES without adoption.** The owner's actions are a DECISION (below) and merging draft PR #77.
>
> **Results of record, and the entry point for anything `GBL-`:**
> [`findings/2026-08-04-gentle-arm-blind-listen-results.md`](findings/2026-08-04-gentle-arm-blind-listen-results.md)
> — **it owns the `GBL-` figures**; its §4 is the options list and its §5 is the barred
> reads. Raw data: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_verdicts.json`,
> `gbl_result.json`, `gbl_owner_notes.md` — **cited, never restated.** The blind runner's
> record: [`2026-08-04-gbl-run-execution-log.md`](2026-08-04-gbl-run-execution-log.md) —
> **its §5, on what the runner saw and on the blind failing, must be read before anything is
> built on the result.** Reasoning for the write-up:
> [`2026-08-04-gbl-writeup-execution-log.md`](2026-08-04-gbl-writeup-execution-log.md).
> Governing document unchanged:
> [`specs/2026-08-04-gentle-arm-blind-listen-design.md`](specs/2026-08-04-gentle-arm-blind-listen-design.md)
> (`GBL-`) — its §5 fixed the read before any journey existed and it was applied, not
> reinterpreted.
>
> **What stands, in one paragraph.** All 8 pairs × 3 depths × both arms were generated,
> presented and judged; the run state §5 requires was met (32 of 32 slots). **On the 16 deep
> rows the margin was 3 against a bar of 5, so the branch is `no_detectable_difference` —
> "my ear cannot tell them apart where the numbers could" — and per §5 that means production
> stands and Option A closes without adoption.** Four things travel with that sentence and
> must never be dropped from it: **the novelty question went 8–0 to the rebuilt package**
> (`GBL-Q1`, unanimous, no no-preferences — but §5 fixed **no threshold for it**, so it is
> data with no pre-registered read and no bar may be chosen now); **five of the seven
> undecided deep rows were undecided because of clip defects**, not because the journeys were
> alike, so the instrument lost resolution rather than finding equivalence; **the blind did
> not hold** — the owner reports it was "almost always really easy to tell which side was the
> new graph", volunteered before he read the result; and **at zero presses he preferred the
> rebuilt app 6–0**, which §5 excludes from the tally and which therefore rescues nothing.
> **Neither arm collapsed into a random walk** (`GBL-Q2`'s collapse clause, empty on all
> eight pairs). **None of the four hidden offline metrics predicted his picks** — fame at 5
> of 9 is a coin flip. **Nothing is adopted, no default changed, no shipped code touched.**
>
> **The decision waiting on the owner, and it is his because it is adoption-adjacent and
> spends his time:** which of the findings note's §4 options to take — accept the null and
> stop, open the clip defect as its own track, or open the whole-path "weird detours"
> observation as a new pre-registered question. **§4's option D (adopt on the novelty sweep)
> I do not think is available**, and the reasoning is in the note.
>
> **⚠ `GBL-` §5's run-once rule now binds: this verdict may not be re-listened.** New
> candidates on new findings still may.
>
> **Two items open and NOT `GBL-`:** the owner's 2026-08-04 no-commercialization ruling is
> in memory but **still not in the repo record** (it belongs in `PRODUCT-REQUIREMENTS.md`);
> and the **eight 2026-07-22→27 `TEST-QUEUE.md` entries** remain `QUEUED` and unruled-on —
> flagged at four consecutive closeouts now.
>
> ---

> ## ✅ THE `GBL-` HARNESS IS BUILT AND THE LISTEN IS READY TO RUN, 2026-08-04 (later). ~~**The owner's one action is STARTING A FRESH, MECHANICS-ONLY RUNNER SESSION**~~ *(DONE — the listen ran, unblinded and was written up; see the top block, which owns current state.)* pointed at `builder/analysis/2026-08-04-gentle-arm-blind-listen/RUNNER-BRIEF.md` — that brief is self-contained and the runner must read nothing else. Branch `gentle-arm-blind-listen`, draft PR #77 (it stays open; merge is a later decision).
>
> Entry point is the current handoff:
> [`2026-08-04-HANDOFF-gbl-harness.md`](2026-08-04-HANDOFF-gbl-harness.md).
> Governing document unchanged:
> [`specs/2026-08-04-gentle-arm-blind-listen-design.md`](specs/2026-08-04-gentle-arm-blind-listen-design.md)
> (`GBL-`; its §8 now carries **`GBL-AM1`**, the eight approved pairs, and a **`GBL-CORR`**
> corrections series). The plan
> ([`plans/2026-08-04-gentle-arm-blind-listen.md`](plans/2026-08-04-gentle-arm-blind-listen.md))
> is **COMPLETE, not live**. Reasoning:
> [`2026-08-04-gbl-harness-execution-log.md`](2026-08-04-gbl-harness-execution-log.md) —
> **its §5 must be read before anything is built on this**.
>
> **What stands, in one paragraph.** The harness is complete and committed: pair
> derivation, both-arm generation behind five hard gates, arm-symmetric clip resolution,
> the side-by-side page with verdicts written to disk, and the run-state-gated tally. **No
> shipped code was touched** — nothing under `api/`, `frontend/` or `builder/src/`. The
> owner approved eight pairs (five from the familiarity proposal, three his own
> recombinations) and they are committed as **`GBL-AM1` with the file's sha256, before
> `gbl_generate.py` had ever run**. **`GBL-CORR1`** corrected §5's branch table, which
> carried the pre-scaling `≥ 3` bar while the same section's prose and worked examples
> carried the scaled `≥ 5`; a test now pins the two together. Six defects in the plan's own
> code were found and fixed, four of them tests that would have passed while testing
> nothing. **⚠ `gbl_generate.py` has never run against the real artifacts** — the seam bars
> it — so its five gates fire for the first time in the runner session; the brief tells the
> runner to distinguish a `SystemExit` (respect it) from a traceback (a harness fault, do
> not debug). ~~**Nothing is adopted, no default changed, and the listen is unspent.**~~
> *(Superseded 2026-08-04 (night): nothing is adopted and no default changed — both still
> true — but **the listen is now SPENT**. All five gates passed on first firing and no pair
> swap was needed. See the top block.)*
>
> **Two items open and NOT `GBL-`:** the owner's 2026-08-04 no-commercialization ruling is
> in memory but **not yet in the repo record** (it belongs in `PRODUCT-REQUIREMENTS.md`);
> and the **eight 2026-07-22→27 `TEST-QUEUE.md` entries** remain `QUEUED` and unruled-on.
>
> ---

> ## ✅ THE GENTLE-ARM BLIND LISTEN (`GBL-`) WAS SPECIFIED AND PLANNED, 2026-08-04 (evening). ~~**The owner's one action is STARTING A FRESH SESSION ON OPUS**~~ *(DONE — the plan is executed; see the top block, which owns current state.)* to execute the plan inline (executing-plans) on branch `gentle-arm-blind-listen` (draft PR #77 — it stays open through execution; merge is a later decision).
>
> Entry point is the current handoff:
> [`2026-08-04-HANDOFF-gbl-plan.md`](2026-08-04-HANDOFF-gbl-plan.md).
> Governing document:
> [`specs/2026-08-04-gentle-arm-blind-listen-design.md`](specs/2026-08-04-gentle-arm-blind-listen-design.md)
> (`GBL-`; committed before any journey exists, and it **wins wherever the plan
> disagrees**). Operational document:
> [`plans/2026-08-04-gentle-arm-blind-listen.md`](plans/2026-08-04-gentle-arm-blind-listen.md)
> (8 tasks). Reasoning:
> [`2026-08-04-gbl-planning-execution-log.md`](2026-08-04-gbl-planning-execution-log.md).
>
> **What stands, in one paragraph.** The owner chose §4 **Option A** (gentle arm only;
> the strong arm is out of scope, a new amendment if ever wanted) and ruled the executor
> model (Opus, fresh session, inline). The listen is the C3 side-by-side format — his
> recorded preference — with journeys generated by the `CRE-G1`(a)-verified mirror, so
> **no shipped code changes before any adoption**. Eight owner-raised pairs from his
> Spotify familiarity (approval is **Task 3, an OWNER GATE**, committed as `GBL-AM1`
> before any journey exists); depths d0/d10/d20; reads fixed pre-run with **margin ≥ 5 of
> 16 deep rows**; run-once. **V0 is the adopted production artifact, deliberately NOT the
> CRE `E-S0` cell** (the drop flags differ — log §2.3). After Task 8 the listen runs in a
> **mechanics-only runner session** (`RUNNER-BRIEF.md`), and the write-up belongs to a
> further fresh session. **Package comparison only — no attribution sentences; nothing
> adopts on any verdict; the four `CRE-R2` qualifiers travel; `REQ-38` is now SCHEDULED
> but still unspent; the re-crawl decision is untouched.**
>
> **Flagged and still standing: the eight 2026-07-22→27 `TEST-QUEUE.md` entries remain
> `QUEUED` and undischarged** (raised 2026-08-04, not yet ruled on).
>
> ---

> ## ✅ THE `CRE-` EXPERIMENT IS COMPLETE, 2026-08-04. ~~**The owner's one action is merging draft PR #75**~~ *(MERGED, `fbecfac`; branch deleted)* — **nothing is waiting on the owner, and no session owes anything.** ~~**The next action is his: a DECISION, not work.**~~ *(DECIDED 2026-08-04 evening — §4 Option A, the gentle arm's blind listen; see the top block, which owns current state.)*
>
> Entry point is the current handoff:
> [`2026-08-04-HANDOFF-cre-stage3-findings.md`](2026-08-04-HANDOFF-cre-stage3-findings.md).
> **Results of record, and the entry point for anything `CRE-`:**
> [`findings/2026-08-04-cap-reevaluation-results.md`](findings/2026-08-04-cap-reevaluation-results.md)
> — **it owns the `CRE-` read**; its §4 is the options list. Raw figures live in
> `builder/analysis/2026-08-03-cap-reevaluation/cre_scores.json` — **cited, never
> restated.** Reasoning: [`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md)
> (§15–§16). Governing document is still the prereg,
> [`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md).
>
> **What stands, in one paragraph.** Two arms passed the primary bar, both on the candidate
> data set: `B-S1-P1a` and `B-S1-P1b` (trimmed union supply, `known` ramp at r₁ and r₂).
> **`CRE-R2` fires for both; `CRE-R0`, `CRE-R1` and `CRE-R3` do not fire; `CRE-R4` finds no
> clear winner**, because its clause (i) fails for both — each arm is the other's
> counterexample — so the findings note presents **options, not a recommendation.** No
> `ALG-E` arm moved the gradient at all. **Four qualifiers travel with every `CRE-R2`
> sentence and must not be dropped:** both passing arms trip §0.4's censoring trigger, so
> their `CRE-C1` is reported **"descent partly unmeasurable" and never as a clean pass**; on
> fully-measured pairs the gentle arm falls below the bar it passed on the full set and the
> strong arm's matched set falls below the readable floor, making it **unreadable rather than
> favourable**; the `w_floor` guard flags all nine supply comparisons, so **no sentence
> credits the connection rule alone**; and `CRE-C5`'s entry condition was never met, so **no
> "tags did this" or "votes did this" sentence is licensed.** **Nothing is adopted, no default
> changed, no shipped code touched, and the blind listen (`REQ-38`) is UNSPENT.**
>
> ~~**The decision waiting on the owner** is which passing arm (if either) is worth a blind
> listen, and whether the candidate data set's advantage justifies the re-crawl it implies.~~
> *(HALF-DISCHARGED 2026-08-04 evening: the listen half is decided — Option A, gentle arm
> only. The re-crawl half is UNTAKEN; see the top block.)*
> Both are his column — adoption, his ear, his risk acceptance. **"The family space is
> exhausted" is a barred read**; the unrun remainder is named in the findings note's §5.3.
>
> **Flagged, and not a `CRE-` item: eight `TEST-QUEUE.md` entries dated 2026-07-22 to
> 2026-07-27 are still marked `QUEUED` and were never discharged.** Some are plausibly
> overtaken by the 2026-08-02 discharge; the queue records nothing to that effect.
>
> ---

> ## ✅ SEAM 3 REACHED, 2026-08-04 — THE CRITERIA FIGURES ARE COMPUTED AND COMMITTED. ~~**The owner's one action is merging draft PR #73**~~ *(MERGED, `eccc73f`; branch deleted)*. ~~The next work is the **Stage-3 findings note**~~ *(WRITTEN — see the top block, which owns current state)*.
>
> Entry point is the superseded handoff:
> [`2026-08-04-HANDOFF-cre-t11-seam3.md`](2026-08-04-HANDOFF-cre-t11-seam3.md), which
> **remains authoritative for Seam 3's own internals**.
> Reasoning: [`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md)
> (§13–§14). Governing document is the prereg,
> [`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md);
> the execution plan is now **COMPLETE**, not live. Figures live in
> `builder/analysis/2026-08-03-cap-reevaluation/cre_scores.json` — **cited, never
> restated.**
>
> **What stands, in one paragraph.** All four criteria are computed per cell over pin 9's
> committed partition, four groups, each with its dropped set committed beside it (read the
> counts from `cre_scores.json`; this document owns no figures). The run-state precondition is met: no specified
> cell is unrun, both Stage-0 branches are committed, and the three `(D1-branch)` cells are
> marked **branch-excluded rather than unrun**. **`cre_r_readable` is `true` — which says
> only that no unrun cell bars a read. No `CRE-R` read is evaluated anywhere in the
> committed output, none has been made, nothing is adopted, and the blind listen (`REQ-38`)
> is unspent.** Two Seam-2 claims were overturned in execution and **must not be reverted**:
> `CRE-C2` genuinely does need graph artifacts (the plan contradicts itself; the prereg
> governs), and the absent-class counter is **live but unfired**, not structurally
> unexercisable — its proof premise bounded the crawl rather than the pruned snapshot
> population.
>
> **The next session must not read a prose summary of the result before opening the JSON.**
> That is what the seam is for: the reader of results must be a session that did not run
> them.
>
> ---

> ## ✅ STAGE 2 GATES AND ALL SIXTEEN SWEEPS ARE COMPLETE, 2026-08-03 (mid-flight — Seam 3 NOT reached). ~~**The owner's one action is merging draft PR #71**~~ *(MERGED, `4f0687d`)*; ~~the next work is `CRE-T11`~~ *(DONE — see the top block, which owns current state)*.
>
> Entry point is the current handoff:
> [`2026-08-03-HANDOFF-cre-run-stage2-midflight.md`](2026-08-03-HANDOFF-cre-run-stage2-midflight.md).
> Reasoning: [`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md)
> (§9–§11). Operational document unchanged —
> [`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md),
> **the prereg governing wherever it disagrees**. Figures live in the seventeen committed
> JSONs under `builder/analysis/2026-08-03-cap-reevaluation/` — cited, never restated.
>
> **What stands, in one paragraph.** The instrument is verified and the device is live:
> **`CRE-G1`(a)** reproduces the production router exactly on all 22 pairs on the E-S0
> substrate, with a **red control** proving that comparison can fail; **`CRE-G1`(c)**
> asserts the ruler frame; **`CRE-G2`(a)** clears its bar in all three `P1`-carrying
> cells; and **`CRE-G1`(b)** and **`CRE-G2`(b)** pass in every swept `P1` cell. **All
> sixteen cells are swept and committed**, nine `ALG-E` and seven `ALG-B`, every pair
> completing the full ladder with no infeasible cell in either data set. **Owed item 1 has
> split**: the null-class counter is live on `ALG-B`, so the Stage-0 zero was a true zero;
> the **absent-class counter is still zero everywhere and that half remains owed**, with a
> position taken but not run (the handoff's open decision). **No `CRE-R` read is licensed
> and none has been made; nothing is adopted; the blind listen (`REQ-38`) is unspent.**
>
> ---

> ## ✅ STAGE 0 AND STAGE 1 COMPLETE at SEAM 1, 2026-08-03. ~~**The owner's one action is merging draft PR #70**~~ *(MERGED, `f3eaec2`)*; ~~the next work is `CRE-T8`~~ *(DONE — see the top block, which owns current state)*.
>
> Entry point is the superseded handoff:
> [`2026-08-03-HANDOFF-cre-run-seam1.md`](2026-08-03-HANDOFF-cre-run-seam1.md), which
> **remains authoritative for Stage 0 and Stage 1's own internals**.
> Reasoning: [`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md)
> (§1–§7). Operational document is unchanged —
> [`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md),
> **the prereg governing wherever it disagrees**. Figures live in the committed JSONs
> under `builder/analysis/2026-08-03-cap-reevaluation/` — cited, never restated.
>
> **What stands, in one paragraph.** `CRE-AM2` was appended to the prereg's §8 and
> committed (`5656602`) **before any stage ran** — the discharged deferral from the
> previous track. Both Stage-0 reads then landed on their pre-registered **expected**
> branches: **`CRE-D3` = `inert_as_expected`** (and its liveness check at the
> instrument-only extreme makes that a *supply* reading, not a dead wire — the device
> demonstrably reroutes journeys and still cannot move the gradient), and **`CRE-D1` =
> `not_supported`**, measured in the **opposite** direction to the hypothesis. **That
> branch is binding: the three `(D1-branch)` cells do not exist and no router-side tag
> arm does; `E-S2-P0` is branch-proof and runs.** Eleven graph cells are built, gated and
> screened — the build mirror is byte-identical to a real `build_from_archive` run on both
> data sets, `S2` is byte-identical to `S1` under a degenerate table (so it is one knob
> away), and all eight non-tag cells reproduce byte-identically across two independent
> runs. **`CRE-G3` 22/22 pairs survive, `CRE-C3` disqualifies nothing, `CRE-C6` screens
> nothing out — every cell proceeds to Stage 2.** **No `CRE-R` read is licensed and none
> has been made; nothing is adopted; the blind listen (`REQ-38`) is unspent.** Four items
> are owed at Stage 2, each with a success condition, in the handoff.
>
> ---

> ## ✅ THE CAP RE-EVALUATION EXECUTION PLAN IS COMPLETE, REVIEWED AND REVISED, 2026-08-03 (night). ~~**The owner's one action is merging draft PR #69**~~ *(MERGED, `2e3b017`)*; ~~the next work is EXECUTION~~ *(STARTED — see the top block, which owns current state)*.
>
> Entry point is the current handoff:
> [`2026-08-03-HANDOFF-cap-reeval-exec-plan.md`](2026-08-03-HANDOFF-cap-reeval-exec-plan.md).
> Reasoning: [`2026-08-03-cap-reeval-exec-plan-execution-log.md`](2026-08-03-cap-reeval-exec-plan-execution-log.md).
> Operational document:
> [`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md)
> (tasks `CRE-T1`–`CRE-T11`; **the prereg governs wherever the plan disagrees**; its
> Revision record maps the review's findings to their changes). Review record:
> `builder/analysis/2026-08-03-cre-plan-critique/` — 1 BLOCKING, 7 MATERIAL, 8 minor,
> 9 verified-clean, **all folded in pre-run** (`da9e49e`); its cell-level figures were
> measured on pre-drop Track B builds and carry that provenance.
>
> **What stands, in one paragraph.** The prereg was verified accurate — every file,
> function, config value and commit it names resolves (plan §Verification record). The
> plan fixes nine executor-column pins pre-run (S2 deletion key with the tuple that
> keeps similarity ordering inside zero-agreement blocks; two separately-priced classes
> of unmeasured artist; the victim-rule total order with its named mechanical
> consequence; the uniform-drop partition that quarantines the staged `UC` cells; the
> guard realised through journey semantics; and the rest in the plan's own section).
> **`CRE-AM2` is specified in the plan but NOT yet appended to the prereg** — the
> executor commits it at T1 Step 2, on the run branch, before any stage runs; it
> resolves `C4`'s binding form at the two anchor cells and moves no bar. Stage order is
> unchanged: `CRE-D3` and `CRE-D1` before any build, screens before any sweep, one
> committed JSON per sweep cell, figures-only scorer, and the Stage-3 findings note
> written by a session that did not run the sweeps.
>
> ---

> ## ✅ THE CAP RE-EVALUATION PRE-REGISTRATION IS COMPLETE AND FROZEN, 2026-08-03 (later). ~~**The owner's one action is merging PR #68**~~ *(MERGED, `cdf0033` — discharged before the exec-plan session started)*; ~~the next work is the EXECUTION PLAN, written by a fresh session~~ *(WRITTEN — see the top block, which owns current state)*.
>
> Entry point is the current handoff:
> [`2026-08-03-HANDOFF-cap-reeval-prereg.md`](2026-08-03-HANDOFF-cap-reeval-prereg.md).
> Reasoning: [`2026-08-03-cap-reeval-prereg-execution-log.md`](2026-08-03-cap-reeval-prereg-execution-log.md).
> Governing document:
> [`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md)
> (`CRE-`; frozen at `3d7b7d6`; **its §9 revision record and two result-bearing
> disclosures must be read before any stage runs**; `CRE-AM1` appended `eec67a8`).
> Review record: `builder/analysis/2026-08-03-cre-prereg-critique/`. The `WAV-`
> within-artist vote read: `builder/analysis/2026-08-03-within-artist-votes/` —
> **CLOSED as FAIL on its own conjunction and never reopened; `CRE-AM1` supersedes its
> consequence on the owner's authority** (the direction question was his column), and
> corrects his recollection: `WGT-` never assessed the within-artist formulation.
>
> **What stands, in one paragraph.** The experiment is fixed before any arm exists:
> primary outcome = the bypass novelty gradient in `fame_lb_pctl` (`REQ-42` shape,
> `FAM-` machinery inherited), on both data sets until a clear winner (`CRE-R4`,
> paired, within-data-set); families (a)–(d) as the owner ruled, `UC` as staged
> reference only; pricing = the known-ramp at 0.01/0.03 (the dominating-regime
> settings were reviewed out); cleanup held constant as both drop flags in every
> cell; `TB-P5H-7` consumed by the joint descent×payload read; `S2`'s ceiling ranking
> carries within-artist vote weighting per `CRE-AM1`, with vote-scramble and
> label-scramble attribution companions at the sweep. Stage order: the two cheap
> Stage-0 reads (`CRE-D3` prior, `CRE-D1` confirmatory — expected branch "not
> supported", disclosed) and the structural screens run before any depth sweep.
> **Nothing is adopted by any outcome; the blind listen (`REQ-38`) stands before any
> adoption; six harness-side dependencies, no shipped code.**
>
> ---

> ## ✅ THE FEATURED-CREDIT FILTER TRACK IS COMPLETE, 2026-08-03; ADOPTION RULED AND ENACTED — **PR #67 MERGED** (`eecc361`). ~~the owner's one action is merging PR #67~~ *(discharged before the next session started)*
>
> Entry point is the current handoff:
> [`2026-08-03-HANDOFF-featured-credit-filter.md`](2026-08-03-HANDOFF-featured-credit-filter.md).
> Reasoning: [`2026-08-03-featured-credit-filter-execution-log.md`](2026-08-03-featured-credit-filter-execution-log.md)
> (§1–§8). Governing document:
> [`specs/2026-08-03-featured-credit-filter-rule.md`](specs/2026-08-03-featured-credit-filter-rule.md)
> (`FCF-`, amended once by `FCF-AM1` — owner-ruled, post-result disclosure on the page).
> Figures live in the committed probe JSONs under
> `builder/analysis/2026-08-03-featured-credit-filter/` — cited, never restated.
>
> **What stands, in one paragraph.** The class the fame-instrument track discovered —
> artists in the graph only through shared release-group credits, never a sole credit,
> no sole-credit Discogs release — is detected offline, keep-checked with the adopted
> rule's own instrument (MB DSP link AND a clip resolves, resolver imported never
> restated), frozen per censused population as sha-pinned package data, and wired behind
> `drop_featured_credit` (default on, factor-table control like its sibling flag). Both
> worked instances drop as fixed in advance — **TJ Brown as a named false positive of
> the DSP-link clause**, which is the residual the owner accepted at adoption. The
> owner's spot checks mid-track exposed the Discogs exemption's shared-credit gap;
> the split measurement vindicated them and `FCF-AM1` closed it. **Declined at
> adoption: the calibration hand-review** — the drop-side false-positive rate is
> accepted as unmeasured; do not re-propose absent new grounds.
>
> **After the merge: the CAP RE-EVALUATION PRE-REGISTRATION, written cold by a fresh
> session, in the adopted currency.** **Its single design-input address is
> [`2026-08-02-cap-reeval-design-inputs.md`](2026-08-02-cap-reeval-design-inputs.md).**
> One input this track adds, recorded in the handoff: **the cleanup is now two flags**
> (`drop_no_release_tail`, `drop_featured_credit`), and holding cleanup constant across
> cells means holding both — the factor table carries them deliberately, never by
> omission. Summary of the standing rulings (fame-instrument execution log §1):
> candidate families (a)–(d) including the owner-triggered tag-based degree limiter and
> staged router-priced unbounded; coverage as guard-only at ~10,000;
> hubness-rising-with-depth as the per-arm kill; LB similarity the sole source of edge
> existence, tags only re-order/re-weight/remove; router pricing in scope (any pricing
> arm consumes `TB-P5H-7`); gradient claims must exceed 10× the ruler's measured
> quantisation step (`FAM-AM1.3`); the population-vs-descent confound goes in its factor
> table (`FAM-AM1.7`); famous-band interiors are ~73% novel to the owner (log §8).
>
> ---

> ## ✅ THE FAME-INSTRUMENT TRACK IS COMPLETE, 2026-08-02 (evening). The cap re-evaluation is UNBLOCKED.
>
> Entry point is the current handoff:
> [`2026-08-02-HANDOFF-fame-instrument.md`](2026-08-02-HANDOFF-fame-instrument.md).
> Reasoning: [`2026-08-02-fame-instrument-execution-log.md`](2026-08-02-fame-instrument-execution-log.md)
> (§1–§9). Governing documents, each with amendments that are part of the record:
> [`specs/2026-08-02-fame-instrument-adoption-preregistration.md`](specs/2026-08-02-fame-instrument-adoption-preregistration.md) (`FAM-`),
> [`specs/2026-08-02-ruler-candidate-shootout-preregistration.md`](specs/2026-08-02-ruler-candidate-shootout-preregistration.md) (`RCS-`),
> [`specs/2026-08-02-novelty-proxy-validation-preregistration.md`](specs/2026-08-02-novelty-proxy-validation-preregistration.md) (`NOV-`).
> Figures live in the committed probe JSONs under
> `builder/analysis/2026-08-02-fame-instrument/` — cited, never restated.
>
> **What stands, in one paragraph.** The owner ruled (2026-08-02): the cap
> re-evaluation's scope includes the data-set switch; its primary outcome is the bypass
> novelty gradient (`REQ-42` shape); and the instrument is fixed first. Under that
> sequencing: ListenBrainz listener counts were validated against *worldly fame* and
> **failed** (`FAM-`, NO ADOPTION); a shootout measured Wikipedia and Deezer also failing
> to order worldly fame (`RCS-`, "no measured candidate orders the tail");
> the owner then **redefined the construct** — obscurity = novelty-likelihood,
> user-relative, audience-pinned (`PRODUCT-REQUIREMENTS.md` Definitions, ratified edit) —
> and the proxy was **adopted under the redefined construct's own one-way validation**
> (`NOV-2`: 15/15 obscure-called artists were novel to him; `NOV-AM1` carries the
> post-result disclosure). **"Fame" in pre-2026-08-02 documents means the retired
> construct; worldly-fame claims are barred from future criteria until an instrument
> exists.**
>
> **~~⚠ ORDERING RULED BY THE OWNER, 2026-08-02 (night): the FEATURED-CREDIT FILTER TRACK
> runs FIRST — the next session's work — and the cap re-evaluation follows it.~~
> DISCHARGED 2026-08-03 — the track ran and completed; see the top block, which owns
> current state. Retained below as the ruling of record.** Three
> recorded reasons (design-inputs doc, and the conversation of record): the class is a
> dormant term that activates only in arms that succeed at pushing obscure; the adopted
> gradient currency scores a delivered ghost as a success (obscure-and-novel) while it is
> exactly the bad recommendation the release filter exists to prevent; and the cleanup
> must be held constant across every cell of the comparison — the same held-constant
> principle that censused both drop lists, and the same clean-first-then-compare ordering
> the owner ruled for the drop-rule wiring. Shape: the adopted rule's shape, not a purge
> — a keep-check (commercial-DSP presence + something plays) keeps featured-credit
> artists who are also small real acts (TJ Brown, 8,274 Spotify monthly listeners, is
> the worked keeper case). The detector is offline (primary-artist vs appears-on split
> from the MB release dump on disk); the wiring machinery all exists from the drop rule.
> Rule designed cold; **whether it gets its own small calibration hand-review is the
> owner's spend, flagged not decided.** Evidence: execution log §5/§5a; two worked
> instances (田島賢, TJ Brown) plus the FAM-6 no-page rows.
>
> **After it: the CAP RE-EVALUATION PRE-REGISTRATION, written cold by
> a fresh session, in the adopted currency.** **Its single design-input address is
> [`2026-08-02-cap-reeval-design-inputs.md`](2026-08-02-cap-reeval-design-inputs.md)** —
> the owner's rulings, the candidate families spelled out, the supply×pricing synthesis,
> the blind-listen lineage, the tag constraints, and the labelled hypothesis with its
> cheap first read. Summary of the rulings (execution log §1): candidate families (a)–(d) including the owner-triggered tag-based
> degree limiter and staged router-priced unbounded; coverage as guard-only at ~10,000;
> hubness-rising-with-depth as the per-arm kill; LB similarity the sole source of edge
> existence, tags only re-order/re-weight/remove; router pricing in scope (any pricing
> arm consumes `TB-P5H-7`); gradient claims must exceed 10× the ruler's measured
> quantisation step (`FAM-AM1.3`); the population-vs-descent confound goes in its factor
> table (`FAM-AM1.7`). Design note from the marks: famous-band interiors are ~73% novel
> to the owner (log §8) — the famous band is not a novelty dead zone.
>
> **Owner rulings from this track that must not be re-opened:** no re-read of prior
> fame-scored results; the drop-list population re-scope (`FAM-AM2`); the `RCS-AM1`
> widening (closed five-row list, no third widening); the `NOV-AM1` adoption. Dead
> unless new grounds: Deezer and Wikipedia as fame instruments. Retired, not to be
> re-run: `NOV-1` (mis-designed against its own governing document — log §8).
>
> ---

> ## ✅ THE DROP RULE IS WIRED, AND BOTH POPULATIONS NOW HAVE A DROP LIST, 2026-08-02.
>
> Entry point is the current handoff:
> [`2026-08-02-HANDOFF-tail-drop-and-candidate-census.md`](2026-08-02-HANDOFF-tail-drop-and-candidate-census.md).
> Reasoning: [`2026-08-02-tail-drop-wiring-execution-log.md`](2026-08-02-tail-drop-wiring-execution-log.md).
> Figures live in the probe JSON and are **cited, never restated**:
> `builder/analysis/2026-08-02-candidate-tail-census/ctc_census.json`, `ctc_clips.json`,
> `ctc_droplist.json`.
>
> **Three things landed.** The adopted rule is applied in `pipeline.py` before the mass
> computation (PR #62). The divergence that opened between `build_from_archive` and the
> probe harnesses mirroring it is closed, with a guard test that fires when `BuilderConfig`
> gains a field (PR #63). And the candidate population is censused, so **the cleanup can now
> be held genuinely constant across a comparison of the two data sets** — which was the
> uncontrolled variable that motivated all of it.
>
> **✅ THE BLOCKING ITEM IS CLOSED, 2026-08-02 (latest).** The builder no longer applies one
> drop list to whichever archive it is handed: the list is selected by `config.algorithm` —
> the same value that already chooses the archive sub-tree — and an **uncensused population
> refuses to build rather than borrowing another's list**. Both censused lists ship as
> package data, sha-pinned. Nothing now blocks a build from `ALG-B`. See the deferral table.
>
> **The next substantial step is the CAP RE-EVALUATION PRE-REGISTRATION**, written cold by a
> fresh session. Every input now exists — Track B as measured input, the `WGT-` device
> recommendation, and both drop lists. ~~**What it needs from the owner first, because it is
> his column:** how much better a connection rule must be to justify a rebuild, and whether
> the data-set switch is inside its scope or a separate question.~~ *(DISCHARGED 2026-08-02
> evening — both answered, plus the instrument-first sequencing; see the top section.)*
>
> **Two rulings from 2026-08-02 that must not be re-opened:** the drop rule is **not**
> re-validated on the candidate population (execution log §5 — the decisive point is that no
> second refinement mechanism exists, so a measured rate would change nothing), and the
> wiring **deliberately contradicted** the 2026-08-01 handoff's closing instruction, with
> reasoning in execution log §1.
>
> ---

> ## The LABEL WEIGHTING AND EVIDENCE PROBE (`WGT-`) is COMPLETE, 2026-08-01. **Nothing adopted; the next action is the OWNER'S.**
>
> Entry point is the current handoff:
> [`2026-08-01-HANDOFF-label-weighting.md`](2026-08-01-HANDOFF-label-weighting.md).
> Governing document:
> [`specs/2026-08-01-label-weighting-probe-preregistration.md`](specs/2026-08-01-label-weighting-probe-preregistration.md)
> (committed before any figure; `WGT-AM1` pre-results). Figures:
> [`findings/2026-08-01-label-weighting-probe.md`](findings/2026-08-01-label-weighting-probe.md)
> — **its §0 pair must be quoted together**: weighting moves selection well past the owner's
> materiality line, **and** nothing measured says any weighted journey sounds better.
>
> **Four durable outcomes.** The **style column is closed with a mechanism** (§3a — eleven
> readings, all adverse; the recognizable styles are what similarity already knows).
> **Release-level evidence is excluded as fame-shaped** (`WGT-4` Branch 3; the album-level
> preference stands for a sharper reason than first recorded). **The device recommendation
> on record, as INPUT to a future cap re-evaluation pre-registration only: rarity-weighted
> agreement over `W4`** — a `W4` vocabulary change stays a `TAS-` §8 amendment, the owner's
> trigger, blind listen unspent. And **the owner's two manual records landed as data**: 18
> of 20 no-release-tail artists judged not journey-worthy (`TAIL-SAMPLE.md`, the sharpest
> population evidence yet that the tail is substantially credits-not-acts), and his
> style-vocabulary calibration read (`STYLE-VOCABULARY.md`).
>
> **✅ ONE OF THE TWO CANDIDATE TRACKS IS NOW DECIDED, 2026-08-01 (latest): the
> no-release-tail question is CLOSED and a drop rule is ADOPTED** — keep a
> release-less artist only where a commercial-DSP link exists **and** a clip
> resolves; **7,035 of 7,686 dropped**, list frozen at
> `builder/analysis/2026-08-01-label-weighting/tail_droplist.json`. **✅ WIRED into the
> builder 2026-08-02 (PR #62)** — the rule must not be re-litigated, only applied; a
> second list now exists for the candidate population, see the top section.
> Evidence: `tail_signals.json` (the population census
> and the artist-**type** split — the tail is 7.2% Group against 37.9% for the rest
> of the graph), `tail_clips.json` (what plays, plus a **measured 9.4% `BYP-13`
> wrong-artist rate** in the app's own name-based clip resolver, which is a live
> user-facing defect independent of this decision), `tail_exposure.json` (delivery
> rates). The remaining candidate track is below.
>
> **Both candidate tracks have since moved on.** The no-release-tail decision is CLOSED,
> adopted and now wired; the cap re-evaluation pre-registration is the live next step and
> is described in the top section, which supersedes this paragraph. **`TAS-` Task 8
> LANDED** (2026-08-01) — see the `TAS-` section below; nothing is owed on it.
>
> ---
>
> ## The RELEASE-TAG COVERAGE PROBE (`REL-`) is COMPLETE. **`REL-1` PASSED — release aggregation clears `COH-2`'s 50% bar in the obscure tail. Nothing adopted. The next action is the OWNER'S.**
>
> Entry point is the current handoff:
> [`2026-08-01-HANDOFF-tas5-routing.md`](2026-08-01-HANDOFF-tas5-routing.md).
> The `REL-` handoff below is **superseded on next actions** and stays authoritative for its
> own probe's internals.
> [`2026-07-31-HANDOFF-release-tag-coverage.md`](2026-07-31-HANDOFF-release-tag-coverage.md).
> Governing document:
> [`specs/2026-07-31-release-tag-coverage-preregistration.md`](specs/2026-07-31-release-tag-coverage-preregistration.md)
> (`REL-`) — **read its §8 first**; both amendments correct the same conflation and
> **`REL-AM2` was written after the headline figure was known and says so.** Figures:
> [`findings/2026-07-31-release-tag-coverage.md`](findings/2026-07-31-release-tag-coverage.md).
>
> **A parallel investigation commissioned by the owner, not a continuation of `TAS-`.** It
> asked whether aggregating an artist's *release* tags labels the artists carrying no genre
> label today. Census over all 74,193 artists from local dumps; no API, no sampling.
>
> **`REL-1` and what cuts against it must be quoted together** — the same pairing rule as
> `COH-2`/`COH-3` and `FPC-2`/`FPC-9`. The bar cleared and the coverage gain lands in the tail
> (`REL-6` not adverse); **but `REL-3`'s fidelity median is modest, its ratio bar is a
> degenerate pass, and a large minority of the unlabelled tail is reached by neither source.**
> Read the findings' §0 and `REL-3` together before acting.
>
> **`REL-4` inverted the design's framing:** Discogs — the arm expected to be awkward — is the
> stronger source in the obscure tail, and the two independent sources agree on at least one
> label for nearly every artist they both reach. That agreement is the strongest thing in the
> record.
>
> **Nothing adopted, no criterion fixed, no weight, default, currency or vocabulary changed,
> no rebuild, no blind listen spent. `TAS-` §1's vocabulary is UNTOUCHED** — a passing frame is
> a *candidate* for a `TAS-` §8 amendment, never an enactment. **It says nothing about whether
> `TAS-6` would flip**, which needs a rebuild this probe does not license.
>
> ---
>
> ## The TAG DISCRIMINATION PROBE (`TAS-`) is COMPLETE, 2026-08-01 — all eight tasks. **NEITHER ARCHITECTURE HAS AN ADOPTION CASE.** Nothing is owed; the next action is the OWNER'S.
>
> **Findings of record, and the entry point for anything `TAS-`:**
> [`findings/2026-07-30-tag-discrimination.md`](findings/2026-07-30-tag-discrimination.md)
> (Task 8, written 2026-08-01 latest). **It owns the `TAS-` figures** — cite it by section and
> never restate a number from it. **Its §0 must be quoted whole:** both kill bars were cleared
> **and** neither architecture has an adoption case, decided by different pre-registered
> clauses. The premise the thread rested on is **confirmed** — genre agreement discriminates,
> and is not redundant with similarity — so neither null is "the graph already knew".
>
> **⚠ Execute the routing side ONLY from
> [`plans/2026-07-31-tas5-routing-execution-plan.md`](plans/2026-07-31-tas5-routing-execution-plan.md).**
> The older probe plan's Tasks 5, 6 and Task 7's routing halves are **superseded and contain a
> trap**: Task 7 Step 5 instructs the executor to make the randomised-label red check fire and
> stop if it does not — the check `TAS-AM3` **withdrew as unachievable**. Do not follow it.
>
> **The build-time side is barred** — `TAS-6`'s **selection** half is ADVERSE, and §5 says that
> bars an adoption recommendation whatever else shows.
>
> **The router side survives its kill bar on a change that is not about genre.** `TAS-5` did not
> kill: journeys change at every non-zero weight in every class. **But `TAS-AM5c`'s null control
> FIRED** — permuting labels among labelled artists reproduces nearly all of the same change,
> far above the pre-registered clause. **Per `TAS-AM5c`, `TAS-5`'s change CANNOT be attributed
> to genre structure, and every `TAS-5` figure must be quoted carrying that caveat.** Both
> instrument checks passed first (`TAS-AM5a` equivalence, `TAS-AM5b` liveness), so this is a
> real null and not a broken harness.
>
> **⚠ `TAS-6`'s ROUTING half is VACUOUS and must not be read as a pass.** Its baseline count of
> sub-decile interior artists is **zero** — production routing delivers no bottom-decile artist
> mid-journey on any drawn pair — so a 10% reduction cannot be measured and "not adverse" is a
> division-by-zero artifact. That zero is itself a corroboration of `DD-F1`.
>
> Figures: `tas_route.json`, `tas_route_guard.json`. Reasoning: execution log **§16**.
>
> **`TAS-AM4` evaluated the `REL-` enriched frame as a CANDIDATE and licensed a recommendation only.** No candidate is killed and reach rises substantially, but the signal measurably blunts — and that fall held on a fixed population, so it is real rather than composition. **§1's vocabulary is UNCHANGED.** Figures: `tas_frame_eval.json`; reasoning: execution log §13. **`tas_frame_split` has since decomposed that result** — the Discogs **style** column causes the blunting, not the coarse genre column, and `W4` dominates `W6` on reach, spread and redundancy alike (execution log §15). **`W6` must not be the frame any future amendment names.**
>
> Current handoff:
> [`2026-08-01-HANDOFF-tas5-routing.md`](2026-08-01-HANDOFF-tas5-routing.md). The two 2026-07-31
> handoffs and the 2026-07-30 one remain authoritative for their own tracks' internals only.
> Governing document is the pre-registration
> [`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md)
> (`TAS-`), which **wins wherever the plan disagrees**. **Read its §8 first:** `TAS-AM1`
> withdraws `TAS-4`'s original bar as **false** and `TAS-AM2` fixes the substrate per
> criterion.
>
> **The owner picked up the third coherence strand on 2026-07-30** — tag-aware neighbour
> selection, parked below until then. The probe tests the assumption both candidate
> architectures share: whether genre agreement discriminates between the candidates an
> artist already has, or merely restates the similarity score. **Nothing adopted, no
> criterion fixed, no weight, default or currency changed, no rebuild, and no blind listen
> spent.** Two owner decisions taken and recorded: the goal is **coherence, not obscurity**,
> and `TAS-4`'s materiality bar is **1% edge turnover**.
>
> **The architecture question — build-time selection vs router-side pricing — was left OPEN
> for the probe to inform, and the probe has now answered it: NEITHER side has an adoption
> case.** `TAS-4` has now answered the
> build-time half and **did not kill it** — figures in
> `builder/analysis/2026-07-30-tag-discrimination/tas_select.json`, reasoning in §9 of the
> execution log. **`TAS-5` (the router half) has now RUN** — see the top of this section. §5
> requires the two to be read together, and they now can be: the build-time half is barred by
> the adverse guard, and the router half's change is not attributable to genre.
>
> **⚠ TWO STOP-LEVEL RESULTS, both 2026-07-30, both recorded in execution log §10.**
>
> **1. `TAS-6` is ADVERSE** (*"does this make the app worse at reaching unknown artists"*).
> Famous→obscure connections fall at every λ and cross the 10% bar at the top two. Per the
> pre-registration's §5 this **bars any recommendation to adopt, whatever `TAS-4` and `TAS-5`
> show** — it is not outweighed by `TAS-4` having survived. Its denominator is thin; read
> `tas_guard.json` before judging materiality, and note that **no bar may be revisited now
> that a result exists**.
>
> **2. ✅ The red check is RESOLVED — `TAS-4`'s figures ARE believable.** The original check
> was **withdrawn as unachievable** by **`TAS-AM3`** (§8): a Jaccard-overlap device cannot
> produce large change on a randomised label frame, because randomising labels destroys
> overlap rather than randomising it. Its replacement, **`TAS-AM3a`**, passes at every λ —
> the ranking path is **bit-identical** to `td_turnover`'s verified one and reproduces the
> committed `TD-2` figures to five decimals. **Discharged for the SELECTION side by `TAS-AM3a`; the ROUTING
> side is discharged separately by `TAS-AM5a`/`b`, both passed 2026-08-01** — `TAS-AM3`'s
> scope clause could not supply it, because its pass conditions live on the capture while
> `TAS-AM2` puts `TAS-5` on the artifact.
>
> **`TAS-AM3b`'s null control corrected the withdrawn check, against tags** — holding fixed
> which artists are labelled roughly doubles the null, so the withdrawn version had
> overstated how much of `TAS-4`'s turnover came from genre structure. Attribution is still
> not unsafe. **Read `TAS-AM3b`'s clause before quoting the ratio: below the threshold it is
> reported and nothing more, and no claim about tags is licensed by it.**
>
> **`TAS-AM3` is the first amendment appended AFTER results existed** — it says so at its
> head and names the hazard. Read that disclosure before relying on it.
>
> **Tasks 5–7 are DONE (execution log §16), and Task 8 landed 2026-08-01 (latest) — the
> findings document is `findings/2026-07-30-tag-discrimination.md`, its owner-facing read is
> execution log §17, and no probe task remains unrun.**
>
> The coherence tag probe, Track B and the fame-proxy probes are **COMPLETE and their
> records are untouched and remain accurate**; the coherence-tag-probe handoff is superseded
> **on next actions only**.
>
> **Coherence tag probe** (branch `coherence-tag-probe`) — a one-day falsification
> probe of the §7 coherence thread, owner-directed. **Its kill gate fired: tag/genre
> coverage thins in the obscure tail the way Wikipedia's does, and the pre-registered
> retrodiction against the 11 blind verdicts was never run — the verdicts remain an
> unconsumed falsifier.** Findings:
> [`findings/2026-07-30-coherence-tag-probe.md`](findings/2026-07-30-coherence-tag-probe.md)
> (`COH-`). **`COH-2` (the band-level kill) and `COH-3` (the delivered-route
> counterpoint) must be quoted together — either alone gives the wrong answer**, the
> same pairing rule as `FPC-2`/`FPC-9`. Nothing adopted, no criterion fixed, neither
> open decision below settled.
>
> **Track B** — results of record:
> [`findings/2026-07-30-track-b-cap-selection-results.md`](findings/2026-07-30-track-b-cap-selection-results.md).
> The two parked decisions below now have the pre-registered recommendation input it
> existed to produce; **both still owe a blind listen (`REQ-38`) regardless of the
> numbers.**
>
> **Fame-proxy coverage** (branch `fame-proxy-coverage`, PR #53) — descriptive scope
> probes, **nothing adopted, no criterion fixed, no currency changed, Track B untouched**.
> Findings: [`findings/2026-07-30-fame-proxy-coverage.md`](findings/2026-07-30-fame-proxy-coverage.md)
> (`FPC-`). **Read its §0 first: it corrects the premise the work began from** — the
> Wikipedia floor is *not* actively corrupting fame-currency measurements, and **no Track 2
> or Track 3 verdict changes.** What it did establish is a **sequencing** question, now
> parked below.
>
> **Nothing is queued for a working session.**

**The requirements baseline is unchanged since 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (`REQ-`) governs where it and
[`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) disagree (its §10 lists the
disagreements). **`DD-F1` remains a defect, not an accepted limitation** — Track B's `R2`
read measured where it can and cannot be moved; the results note owns that reading.

## PARKED — owner's explicit decision; his trigger, never a session's

- ~~**Whether the fame instrument is fixed BEFORE or AFTER the graph work**~~ — **RULED
  AND DONE 2026-08-02: before, and it was.** The `FPC-2`/`FPC-9` pairing rule stays for
  reading that record. Struck, kept for the record.
- ~~**Whether a currency change re-reads prior fame-scored results**~~ — **RULED
  2026-08-02: NO re-read.** Prior results stand in their measured currency;
  cross-currency comparisons barred. Struck, kept for the record.
- **The coherence thread** — execution log
  [`2026-07-30-fame-proxy-coverage-execution-log.md`](2026-07-30-fame-proxy-coverage-execution-log.md)
  §7. **Its instrument half was probed 2026-07-30 and the kill gate fired** (`COH-`,
  above): §7's own warning — tag coverage thins in the same tail — measured true at
  band level, so no tag-based instrument gets built on this artifact's population as
  measured. What remains parked, still the owner's trigger: the **structural half**
  (the cost function assumes coherence is additive along edges while
  `PRODUCT-REQUIREMENTS`'s second clause is not — untouched, unproposed), and any
  **reopening of the instrument line on a route-population gate** (`COH-3`'s 74.2%
  on delivered interiors is the recorded argument; a reopening is a new
  pre-registration designed cold, never a re-read of the fired gate).
  **⚠ The third strand is NO LONGER PARKED — the owner picked it up 2026-07-30 and it is
  the live work; see "Next" above.** Its caveats below were all carried into the
  pre-registration rather than lost: the reordering limit is stated in `TAS-4`'s bound, the
  self-audit circularity is why the track has no offline scoreboard and ends at a blind
  listen, and the Track-B-shaped cost is why `TAS-` measures before proposing a rebuild.
  **One caveat was measured and turned out to understate the case:** the strand assumed
  selection "reorders candidate lists", which is true — but `TD-2` measured that reordering
  converts to roughly twice as much map change as per-artist counting suggests, because
  every swap also *creates* a connection. Retained below as written.
  *(Original text, superseded on status only:)*
  **A third strand, owner-raised 2026-07-30 after the probe and explicitly flagged
  worth a future session: tag-aware neighbour SELECTION at build time, at the top of
  the graph.** The probe's kill was about *scoring paths*; selection lives where
  candidates are many and labels near-total (top bands 94–100%, `COH-2`), and barely
  operates where labels are dark — the coverage failure and this use are close to
  complementary. Three caveats travel with it: it *reorders* candidate lists and
  cannot add famous→obscure supply (that stays with candidate supply and router
  pricing); tags spent on construction are spent as an evaluator — §7's self-audit
  circularity in new clothes, leaving the 11 blind verdicts as the only independent
  check; and picking it up is Track-B-shaped work — a selection-rule change, so a
  rebuild, a pre-registration with a factor table, and a blind listen (`REQ-38`).
  `COH-5` makes the data side cheap (~47 min for a full tag frame).
- **The cap-rule decision for any rebuild** — Track B's `R1` is its input; adoption of
  any rule owes the blind listen.
- **`ALG-B` adoption** — Track B's `R0`, `R2`, `R3` (`CRS-C6`) are its inputs, beside
  `RC-R1`'s stranding figures; adoption retires the existing path-quality figures and
  owes a blind listen (`REQ-38`).
- **The router-side pricing track** (plan §0 ruling 2) — `R2`'s `ALG-E` null is its
  motivating evidence: the quota edges exist and production weights decline them. Needs
  its own pre-registration, which must consume `TB-P5H-7`.
- **The candidate-pool product decision** — whether a shortened-but-obscure bypass
  candidate (Track 3's DD-A2 or a TB arm) ships at all.
- **The one-statistic cross-track recompute** that must precede any DD-vs-TB comparison.
- **Any blind listen on a router-only candidate** — deferred to the full stack.
- **Re-evaluating bounded-degree itself** (router-priced unbounded graphs) — Track B's
  `UC` reference rows now give it measured baselines; his trigger; owes its own blind
  listen.

**Still owed by the owner:**

1. ✅ **The use-the-app test — DONE 2026-08-02.** The redesign entry was run in full against
   `https://musicapp.cmiller.io`, desktop and phone. Everything passed; journeys he knows well
   were **unchanged**, which was the check that mattered. One incidental finding worth
   carrying: **the loading screen is often too fast to see**, so nothing should be measured or
   redesigned on the assumption a user experiences it.
2. ✅ **The iPhone script — DONE 2026-08-02, and it settled a Gate 3 blocker.** All three
   questions clean: clips play, the bottom bar clears the home indicator, artist-name typing is
   unaffected. **`G3-F2` is FALSIFIED** — see the gate table below.
3. ✅ **The `--prune` publish pass — DONE 2026-08-02.** Two orphaned assets from the
   pre-redesign build deleted; live site verified afterwards. See the deferral table for the
   pre-flight a successor should repeat.

**One action is owed by the owner: merging draft PR #69**, which lands the execution
plan and its review record on `main` — the executing session consumes both, and
durability requires the merge. After that, opening the executing session is his too
(fresh session, `/model opus` — Fable is his saved default — then `/session-start` and
"execute the plan"). Everything else remaining for him is decisions only — the triggers
named in the parked list and the deferral table. *(PR #68 was merged 2026-08-03,
`cdf0033`; #67 `eecc361`; #66 `f9f42ce`.)*

**Nothing is queued in [`TEST-QUEUE.md`](TEST-QUEUE.md).** Its newest entry (2026-08-03
night, the execution-plan track) is N/A — nothing app-facing changed and nothing is
running. The prior real check (2026-08-02, post-prune) came back clean. Everything else
there is dormant until a graph is rebuilt.

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). **One blocker removed 2026-08-02: `G3-F2` is FALSIFIED** — HIGH, "blocking if confirmed", and the review named the deciding test (*"one tap on a real device confirms or kills it"*). Clips play on a real iPhone. ⚠ **Read what that does not mean:** the code was NOT changed to achieve it — `usePlayer.ts:49` still awaits the URL before `player.play(url)` at line 60, which is exactly the pattern the review flagged. The finding's *description* was accurate; only its *consequence* is removed, and it rests on iOS's current tolerance rather than on the code being correct by construction. **Do not cite this as "the iOS play path is correct."** The rest of the blocking set (`G3-A1`–`G3-A4`, `G3-S1`–`G3-S3`, `G3-Q1`, `G3-Q2`, `G3-F1`) is untouched. |

## Closed — do not re-plan or re-investigate

- **Track B's cells and reads are closed.** Builds are byte-deterministic and the raw
  outputs are committed — do not re-run cells to "check"; re-running is only ever
  instrument work under a harness change that re-fires `CRS-G1`.
- **`R2`'s `ALG-E` null must not be cited as "the quota rule cannot fix `DD-F1`"** — it
  is "the router declines the quota edges *at production weights*"; the pricing track
  above owns the difference.
- **`PS100` ≡ `MK100`, byte-identical, both archives** (`LBS-3`) — one graph, never two
  data points. And **`proximity_select` at bound 50 measured materially worse on
  stranding on both archives** — do not re-propose it as a candidate without new grounds.
- **The pair-set attrition decision is closed** — the `× lower` classes are unreadable
  per `CRS-G3` at the committed draw; a redraw is a new §8 amendment designed cold, the
  owner's trigger if he wants obscure-endpoint path reads.
- **The source `algorithm` parameter is a CLOSED ENUM of six values** (`CS-P0e`);
  `limit` ≤ 100, `threshold` ≥ 10, production already at both edges. Parameter semantics
  are `LBS-`'s, from source (`findings/2026-07-30-lb-algorithm-semantics.md`).
- **`CS-P0c` must not be cited as "no cap rule can fix `DD-F1`"** — scoped to own-list
  selection; the prereg's §0 table owns per-family bearing.
- **The `--target`-capped trial crawl is RETIRED for `AS-H2`** (only).
- **Track 2, Track 2F and the ceiling toll are exhausted nulls. Do not re-run any.**
- **Track 3's and Track 3b's results are closed** — do not re-run their arms or
  re-litigate TB-R2.
- **The routing-side toll family is closed for descent claims**; any explicit
  length-preserving constraint is a new device needing its own pre-registration
  consuming `TB-P5H-7`.
- **Loosening the both-ways cap without a simulated bound was rejected (`MKS-5b`) — and
  Track B is that simulation, now RUN.** Its results note is the record.
- **Famous-pair first-path fame is barred as a scoring criterion** (PLA-R1); Track B's
  prereg resolved its applicability and `CRS-C5` measured presence, not fame.
- **The nameless-artist question is decided** (drop; implemented, `GR-1`).
- **The builder-side p99 rescale stays parked** (DD-R2's trigger never fired).
- **The OneDrive migration is COMPLETE**; the old tree is an archive.
- **`G3-A5`, `G3-A2`, `G3-S7`** closed as recorded; **`G3-A3` does not fire**.
- **`RMD-6`, `RMD-11`, `RMD-12`, `RMD-13`, `FRO-1`, `FRO-4`**, the `DEP-33` blockers, the
  Gate 1 clip work, **Track 1**.
  - ⚠ **One exception:** `BYP-13` — a card playing a clip by a *different artist of
    the same name*. Not path work and not inside any pause. **A fix is BUILT as of
    2026-08-02 and is INERT until a rebuild** — the builder carries MusicBrainz-recorded
    Deezer artist ids in the APG1 metadata blob and the api resolves by identity before
    falling back to name search. **The defect is unchanged in the running app**, which
    serves a pre-2026-08-02 artifact with no ids. It is *reduced*, not closed — see the
    link-quality row in the deferral table.

## Must not be changed, and each has a reason

- **`max_size=2` (`stack.py`)** — the **cost ceiling**, the only automatic spend control.
- **App Runner is excluded from CDK tagging** — tagging forces a replacement that cannot
  succeed; pinned by `test_app_runner_is_deliberately_left_untagged`.
- **The ACM validation `CNAME` at Cloudflare** — delete it and the certificate silently
  fails to renew in ~13 months.
- **The rate limit is `10 / 10 s`, not `30 / 60 s`** — see `infra/README.md` §1a.
- **The `acceptance.py` blank-name check** — do not weaken it to unblock a build. And
  `GRT-P2` stands: the guard is blind to a severe famous-artist collapse at any scale;
  strengthening it is an unclaimed design question, not part of Track B.
- **The mirror's two device knobs (`w_known_ramp_pctl`, `w_known_thresh_pctl`) stay 0.0.**
- **`BuilderConfig.algorithm` still carries `contribution_5`**; changing it *is* the
  re-crawl decision. Likewise `max_neighbours_per_artist = 50` and
  `cap_strategy = "mutual_knn"` — **Track B was analysis-only and moved no default.**

## Deferred, with conditions

| Finding | Condition |
|---|---|
| ✅ **Track B runs and reads** (`CB-5`/`CB-6`) | **DISCHARGED 2026-07-30** — run to completion; results note is the record. Struck, kept for the record. |
| ✅ **`CRS-A5` endpoint re-verification** | **DISCHARGED 2026-07-30** — one request at scoring time, 200, companion delivered descriptive-only. Struck. |
| **`FPC-9`'s falsifier — an obscure-endpoint pair set for floor reach** | **If any realistic candidate device reaches materially more obscurity than production.** `FPC-9` used Track 3's `LIMIT` arm, a ceiling rather than a shippable route, and rests on 62 interiors from one arm on twelve pairs. Falsified by a device that reaches more obscurity *without* approaching `LIMIT`'s interior percentiles. |
| ✅ **`PRODUCT-REQUIREMENTS.md`'s Definitions section does not quantify the proxy's blindness** | **DISCHARGED 2026-08-02 — the condition fired and the edit landed.** The currency decision was made; the Definitions entry now carries `FPC-3`/`FPC-9`'s extent inside the retirement paragraph of the worldly-fame construct (owner-ratified edit). Struck, kept for the record. |
| ✅ **Full-graph MBID-keyed fame values** (`fp_fame_mbid --build`) | **CLOSED 2026-08-02 — the path is known-unreachable, not deferred again.** The currency decision adopted the LB proxy and **retired the worldly-fame construct**, so the condition ("adopts the MBID-keyed proxy") can never fire. Reopening requires a worldly-fame instrument to exist at all, which `RCS-` measured as currently unachievable. Struck, kept for the record. |
| ✅ **MusicBrainz tag/genre coverage as a coherence instrument** | **DISCHARGED 2026-07-30** — the coherence tag probe ran exactly this check and its kill gate fired (`COH-2`, vocabulary-robust per `COH-6`); the retrodiction stayed unrun. Struck, kept for the record. |
| ✅ **Adding `analysis` to builder's `testpaths`** | **DECLINED BY THE OWNER 2026-08-01 — closed, not deferred again.** Its condition fired at the closeout retiring the `TAS-` probe, and he ruled: **frozen code should not be tested by default.** `testpaths` stays `["tests"]` (`builder/pyproject.toml:25`); probe tests run only when a directory is named explicitly. The reasoning is durable rather than circumstantial — probe tests guard research code nothing ships and nobody will edit again, so collecting them would gate unrelated builder merges on a frozen artifact's committed JSON or a vanished scratch capture. **A future probe does not reopen this**; it inherits the same answer. Struck, kept for the record. *(This row carried a count of "34" until 2026-07-30; it was stale, and the count was never this document's to own — read it off `pytest analysis/ -q`.)* |
| ✅ **Replacing mutual k-NN with a tag-based degree limiter** | **DISCHARGED 2026-08-03 — the owner triggered it** (design-inputs family (c), 2026-08-02) **and it now has its cold-designed pre-registration**: `CRE-S2` (tag-guided ceiling on the union source, one-column isolated, `CRE-AM1`'s vote weighting inside it), with the family's premise tested by `CRE-D1` before the full arm set exists. Struck, kept for the record. |
| ✅ **`TAS-4` is not believable until the red instrument check runs** | **DISCHARGED 2026-07-31 for the SELECTION side** — the original check was withdrawn as unachievable (`TAS-AM3`) and its replacement `TAS-AM3a` passed at every λ. Struck, kept for the record. |
| ✅ **`TAS-5` is not believable until the ROUTING-side red check runs** | **DISCHARGED 2026-08-01.** `TAS-AM3`'s scope clause could not supply it — its pass conditions live on the pre-cap capture while `TAS-AM2` puts `TAS-5` on the artifact — so `TAS-AM5` constructed one, written **before any routing figure existed**. `TAS-AM5a` (equivalence) and `TAS-AM5b` (liveness) both passed on the full draw. Struck, kept for the record. |
| ✅ **Task 8 — the `TAS-` findings document is unwritten** | **DISCHARGED 2026-08-01 (latest)** — `findings/2026-07-30-tag-discrimination.md`, with the owner-facing read in execution log §17. Both conditions honoured on the page: `TAS-AM5c`'s caveat is carried at `TAS-5`'s section head and repeated at its figures, and `TAS-6`'s routing half is marked **VACUOUS** with its mechanism (`tas_guard.py:111`) rather than read as a pass. Struck, kept for the record. |
| **`TAS-6`'s routing half is unmeasurable on the committed draw** | **If, and only if, an obscure-endpoint draw is ever made for routing.** Its baseline is zero sub-decile interior artists, so no reduction can be measured and "not adverse" is a division-by-zero artifact. Not a defect of the run — a property of what production routing delivers, and a corroboration of `DD-F1`. |
| ✅ **Rarity-weighted agreement is a measured candidate device** | **MEASURED IN FULL 2026-08-01 by the `WGT-` probe** — the single-frame diagnostic became a 15-cell grid; the `WGT-` findings own the result and the device recommendation (rarity over `W4`, input-only). The trigger half stands: adopting any weighted device changes §1, an §8 amendment, the owner's call. Struck as a deferral, kept for the record. |
| **`W4` was never evaluated as a `TAS-` candidate frame** | **If the owner triggers a vocabulary change.** Now further supported: the `WGT-` grid evaluated `W4` under two weighting schemes and it remains the dominant frame; the style column is closed with a mechanism (`WGT-` findings §3a). A `W4` adoption would still be a new §8 amendment designed cold. |
| **Discogs alias expansion** | **If a frame amendment is ever triggered.** Discogs attribution goes through one MB-sourced ID; alias releases are invisible, so every Discogs figure is a lower bound (identical in every cell — no comparison threatened). `discogs_20260701_artists.xml` is already on disk; expansion is an exact ID join, no download, no name matching. |
| **The Discogs `masters` export** | **Iff Discogs support-counting is ever wanted.** Irrelevant to every presence-based use (unions are reissue-proof by construction) and would *lose* tail coverage (single-version releases often have no master); but it is the album-grain collapse that avoids the pressing confound (`WGT-4c`) if Discogs evidence counts are ever proposed. **Owner spot check 2026-08-01 (DSotM, 1000+ releases):** individual pressings accrete stray labels beyond the master's (`art rock`, `classic rock`, `pop rock` beside the master's two) — so the release-built frames carry mild curatorial noise a master build would not, the flip side of the coverage loss. Recorded; changes no measured verdict. |
| ✅ **The no-release-tail product decision** | **DECIDED BY THE OWNER 2026-08-01 — a drop rule is ADOPTED and the list is frozen.** Keep a release-less artist only where a commercial-DSP link exists **and** a clip resolves; **7,035 of 7,686 dropped, 651 kept** (`builder/analysis/2026-08-01-label-weighting/tail_droplist.json`, drop-list sha256 `d876c7ba…`). Struck as an open question; the wiring row below is what remains. |
| ✅ **The drop list is wired into the builder** | **DONE 2026-08-02, PR #62.** `drop_no_release_tail` (default on) applies the frozen list in `pipeline.py` beside the nameless drop, before the mass computation; the list ships as package data pinned by sha256. All three carried constraints are commented at their definitions. **The flag is an experimental control, never a shipping option** — it exists so a build-side experiment can hold the drop constant in a factor table, and so frozen probes can be era-pinned. Struck, kept for the record. |
| ✅ **One list, applied to any archive** | **DISCHARGED 2026-08-02 (latest) — both halves, the per-archive list and the refusal.** The list is selected by `config.algorithm`, which already decides which archive sub-tree a build reads, so a build's algorithm *is* its archive identity and no new `BuilderConfig` field was needed (the mirrors guard stays quiet, and `PERMITTED_ALGORITHMS[1]` still resolves for every frozen probe). Both censused populations ship as sha-pinned package data — `ALG-E` 7,035, `ALG-B` 9,501. The four **uncensused** algorithms raise `NoDropListForAlgorithm` rather than borrowing a list; the refusal is conditional on `drop_no_release_tail` being on, so the era-pinned probes that build uncensused populations with it off are untouched. **The magnitude of the averted defect, since the row understated it:** the two lists share only **2,712** MBIDs, so applying today's to an `ALG-B` build would have dropped **4,323** artists that rule keeps *and* missed **6,789** it drops. Mutation-tested — reinstating the old one-list behaviour turns five tests red. Struck, kept for the record. |
| ✅ **Whether the drop rule needs re-validating on the candidate population** | **RULED BY THE OWNER 2026-08-02: NO, and the reasoning is durable rather than circumstantial.** The rule does not rest on which artists are in the graph. It rests on three claims that hold for any population: release-less artists are generally poor recommendations to surface; the reason not to drop *all* of them is that MusicBrainz is incomplete, not that they are good (**both keepers in his 20 were real artists MB had simply failed to document**); and the DSP-link-plus-clip check is the best false-positive catcher available. **The decisive point is the one that closes it:** a measured false-positive rate on the candidate would change nothing, because no second refinement mechanism exists — so the follow-up question ("and then what?") has no answer, and dropping a large number of bad recommendations is a strong trade even carrying some false positives. **A future session must not propose a second hand sample on transferability grounds.** Distinct from the *magnitude* question — if a candidate tail were a far larger share of its population, that is a different-sized intervention, and `analysis/2026-08-02-candidate-tail-census/` measures it. |
| ⚠ **The Deezer id path inherits MusicBrainz's link accuracy — it is not "strictly better"** | **Before `BYP-13` is described as closed, and before any figure is put on the improvement.** MusicBrainz sometimes links an artist to a *duplicate* Deezer page rather than the real one. Two observed by hand: Radiohead's recorded link has 473 followers and **0 albums** (so it serves nothing and falls back to name search — fails safe), and Orbital's has **20 followers and does serve tracks** — where the id path would replace a correct name-search result with a worse one. Sampled over 60 delivered artists carrying an id: **59 of 60 serve a track from the id**, and 6 of those are thin pages, of which most are *genuinely* obscure artists rather than duplicates. So the new failure mode is real but small against the 9.4% / 6.1% it removes; **the net is clearly positive and the direction of every individual case is not guaranteed.** A session must not restate this as "strictly better by construction" — that claim was made on 2026-08-02 before this was measured, and is withdrawn. Cheap targeted mitigation if wanted: validate links for the top popularity decile only (~7,400 lookups), where a duplicate is both most detectable (expected follower count is high) and most damaging (those artists are delivered most often). |
| ✅ **The Deezer id map covers only the adopted population** | **DISCHARGED 2026-08-02 — the map now covers the UNION of both populations**, so the cap re-evaluation cannot trip a coverage condition mid-experiment. 93,067 artists (adopted 74,193 + `ALG-B` 68,467, overlapping), **39,465 ids**. The `ALG-B` graph used is the 2026-07-30 full build (sha `d008a2b5…`, manifest-verified), which predates the drop rule and the nameless fix and is therefore a **superset** of any final `ALG-B` build — safe by construction, since an MBID absent from a build is a no-op, and the same reasoning the candidate tail census used. Adopted-population coverage is unchanged at 34,988 / 47.2%, which is the consistency check that the union did not perturb it; `ALG-B`-only artists cover 4,477 of 18,874 (**23.7%**), consistent with that population being deader. An artist outside the union still falls back to name search. Struck, kept for the record. |
| **The Deezer id map is a dated snapshot and will age** | **Whenever it is next questioned; no automatic trigger exists.** Frozen 2026-08-02 because `build_from_archive` is offline by a hard rule and spec §9 requires byte-identical builds. A link that goes stale 404s, which `_get` treats as a miss rather than a refusal, so the card degrades to name search rather than going silent (pinned by `test_a_stale_id_falls_back_to_name_search_rather_than_giving_up`). Refreshing is a deliberate act with its own decision. |
| ✅ **The featured-credit residual class in the release filter** — artists kept because credits count as release groups, while having no primary-artist existence (two worked instances: 田島賢, TJ Brown; mechanism closed via `LBS-1`'s 0.25 featured weight) | **EXECUTED AND ADOPTION-RULED 2026-08-03 — the `FCF-` rule; see the top block.** The detector ran on the release-**group** dump (cheaper than the release dump the original row guessed at), the keep-check ran with zero refusals, `FCF-AM1` closed the shared-credit exemption gap the owner's spot checks found, and the lists ship as package data behind `drop_featured_credit`. The calibration hand-review was **declined at adoption**. Struck, kept for the record. |
| **Known-press telemetry as the novelty proxy's long-run validator** | **When enough `known` presses exist to read.** Named in the Definitions entry and `NOV-` §3; nothing to build now. |
| **A worldly-fame instrument does not exist** | **Accepted; claims in that currency are barred until one does** (Definitions ruling). Reopen only if a product need for worldly fame appears — the `RCS-` corpus and its committed hand values are the reusable starting point. |
| **The TJ Brown late hand read** (8,274 monthly listeners, ruler 218) | **Usable by a future corpus at design time only** — never a post-hoc addition to a read set (log §5a). |
| **`REQ-Q1`'s telemetry revisit condition FIRED and was not taken** | **The owner's call, separately from anything here** — whether live telemetry converges on the offline currency now that a per-mbid source exists. Flagged in the requirements text itself. |
| **Apple/iTunes ids are measured but not shipped** | **If the residual `BYP-13` rate after the Deezer path is judged too high.** Adding them takes delivered-artist coverage from **92.9% to 94.1%** of card impressions — 1.2 points — and the Apple-id-to-iTunes-lookup path has never been run here, unlike the Deezer one (`tail_clips.py:137`). Figures: `builder/analysis/2026-08-02-dsp-ids/dsp_ids.json`. |
| **A blind listen isolating the post-drop graph** (`REQ-38`) | **ANSWERED BY THE OWNER 2026-08-02: not now, and this is a deferral with a condition rather than an open question.** ⚠ **The previous wording — "whether the post-drop graph *owes* a blind listen" — misread `REQ-38`, and a session must not restore that framing.** Read from source, `REQ-38` says blind listening is the **primary evaluation method** and offline metrics must not override listener judgment: a rule about **how a judgment is made when one is being made**, not a debt every graph change incurs. No isolated adoption decision about the post-drop graph is pending, so nothing triggers it. **The owner's decisive argument, and it stands on its own:** every outcome leads to the same place — a pass adopts, and a failure still would not revert to delivering release-less artists, only change the exclusion mechanism. A test whose branches share a direction is not informing a decision. **Corroborating evidence he did not cite:** `TAS-` measured **zero** bottom-decile interior artists across 120 journeys, and the release-less tail sits overwhelmingly in that region — so the dropped artists were largely never delivered, and the drop's audible effect is second-order (shifted marginals, ~109 stranded of 74,193). **The one real cost, named rather than dismissed:** if the cap re-evaluation yields a rebuild, the drop is permanently confounded with the cap change and only the combined result is ever heard. That is why the option is preserved rather than closed. **Condition to spend it:** if the post-drop graph is ever proposed for adoption **as the only change** (the cap re-evaluation returns no rebuild), **or** if a combined rebuild sounds worse and the cause needs decomposing. **The instrument is already preserved** — `drop_no_release_tail` exists as an experimental control so a build can hold the drop constant in a factor table, so deferring costs no future capability. Distinct from the rule's own acceptance, which is closed. |
| **The label-affinity / clustering data asset** | **The owner's trigger.** `wgt_release_raw.json` side-collected record-label credits, countries and years per graph artist; nothing consumes it. His style-vocabulary read adds: for the curated Discogs styles, carrier count alone tracks usability — the clustering idea keeps its value for the open MB tag space, where frequency separates nothing. |
| **Tag clustering as a junk-label filter, owner-raised 2026-08-01** | **Unmeasured; the owner's trigger.** The current whitelist keeps a tag only if MusicBrainz classifies it as a genre — an ontology decision, which is why `british invasion` is discarded despite binding coherent artists. The owner's proposal: a real label's carriers cluster in the map, a junk label's scatter. Frequency alone cannot separate them, since `seen live` and a genuine niche genre are both rare. |
| **One new Snyk Low finding per module added under `builder/analysis/`** — *but only for modules taking a CLI path argument.* **The three added 2026-08-02 (`dsp_ids.py`, `delivered_coverage.py`, `id_quality.py`) contribute NONE**, the same reason `tail_exposure.py` did not: no CLI argument, so no input reaches a path. Full `builder/` scan at that closeout returns **32** — 27 Path Traversal Lows, 3 DOM-XSS in `listen.html`, 2 XML-parser Mediums (row above). *(2026-08-03 later: `wav_read.py` adds **2** of the same class — `--capture`/`--out` — recorded at its pre-registration commit; the eleven `cre_probe*.py` scripts add none, no CLI path arguments.)* | **Recorded, not fixed; extending the acceptance is the owner's.** A CLI `--out` path flows into `pathlib.Path` — the same class as the 13 already accepted here, **now 11 in the `TAS-` directory plus 6 in the `WGT-` directory** (`wgt_grid.py` ×2, `wgt_release_read.py` ×2, `wgt_style_filters.py` ×2). *(Corrected 2026-08-01 latest: this row said **4** and omitted `wgt_style_filters.py`'s two, which a re-scan surfaced. `tail_exposure.py` added the same day contributes **none** — it takes no CLI argument, so no input reaches a path.)* It cannot be meaningfully sanitised: captures deliberately live *outside* the repo, so confining the path breaks intended usage. |
| ✅ **Tag-aware selection increases the map's total edge count** | **DISCHARGED 2026-08-03 — the condition fired and was satisfied as this row's own text prescribes**: the `CRE-` pre-registration states the owner's sole-source constraint (LB similarity the only source of edge existence; tags only re-order, re-weight or remove), under which the union bounds the count above and the `TAS-4` growth mechanism cannot operate. Struck, kept for the record; the corrected `w_degree_hub` half below stays live reading. *(Original condition:)* **Before any rebuild pre-registration is written.** Opened by `TAS-4`: Jaccard is symmetric, so genre-sharing artists promote each other and creations exceed deletions at every λ. Mutual k-NN bounds each artist's own list, not the count of mutual pairs, so mean degree rises. Execution log §9.4/§9.5. **⚠ CORRECTED 2026-08-02 — this row previously said `w_degree_hub` "is dormant *because of the current graph's top-degree set*", which reads as the `w_floor` dormant-term confound about to repeat. It is not.** Checked from source: `w_degree_hub = 0.0` (`api/…/config.py:54`) and the term is a plain multiplication in the cost function (`pathfinding.py:135`), with no environment override anywhere — weights are not env-driven. **At a zero coefficient the graph's top-degree set cannot make the term fire, so it cannot switch itself on in the arms that succeed.** What *is* live is a decision, not a confound: the *reason* the weight is zero rests on a property of today's graph (§2.6 — the top-1%-by-degree set is largely insular micro-genre artists, so penalising them is not what you want), and a different connection rule changes that set. **So a rebuild pre-registration should decide `w_degree_hub` deliberately and record the decision — it does not need a control against the term waking up on its own.** |
| **The 11 blind verdicts as a falsifier for any future coherence instrument** | **If the owner reopens the instrument line** (route-population gate, `COH-3`). The corpus is unconsumed; any scoring against it must be pre-registered cold, and `ct_retrodict.py`'s committed-but-unrun rule counts as the first attempt for reporting purposes. `SYN-7` binds. |
| **42 ListenBrainz nulls and 24 MBIDs refused as ambiguous** | **Accepted, won't chase.** Both are recorded in the probe JSON. Reopen only if a criterion is built that depends on those specific artists being scored. |
| **The `× lower` path-read redraw** | **If the owner asks for obscure-endpoint path reads under candidate rules** — a new §8 amendment designed cold; the committed draw's famous classes stay the record. |
| ✅ **The `REL-` release-dump union pass** | **CLOSED 2026-07-31 — the path is known-unreachable, not deferred again.** Its §7 condition was "if and only if `REL-1` lands in 45.0–49.9%". `REL-1` cleared the bar outright, so the condition can never fire for this run. Reopening needs a new pre-registration designed cold. Struck, kept for the record. *(Correction 2026-08-01: this row and the frozen spec's §7 both said the 345 GB dump "was deleted after measurement" — **it was not**; it is on disk at `builder/scratch/mb-json-dumps/release/`, 322 GB, verified. The closure never depended on the deletion and stands. The `WGT-` pre-registration reads the dump for a different question — evidence strength, not coverage — designed cold as this row requires.)* |
| **Whether `REL-`'s frame is taken into `TAS-`** | **The owner's trigger, unchanged.** A `TAS-` §1 vocabulary change is an amendment to a frozen document and a rebuild spends his ear (`REQ-38`). **The cheap read this row asked for has now RUN** — execution log §15, figures `tas_frame_split.json`. It does not settle the trigger, but it changes which frame a decision would be about: the Discogs **style** column, not the coarse genre column, is what costs discrimination, and `W4` (`W1` + Discogs genre only) dominates the previously-evaluated `W6` on reach, spread and redundancy alike. **`W6` should not be the candidate any future amendment names.** `REL-3`'s fidelity median still governs, and nothing measured says `W4` is good enough to adopt. |
| **`REL-3`'s ratio bar is degenerate and must not be reused as written** | **Before any successor pre-registration expresses a bar as a multiple of a null.** The null median was exactly zero, so "≥ 3× the null" was satisfied by a division by zero. A ratio bar needs a stated floor on the denominator, or a difference bar instead. |
| **The `LBS` `filter` token's meaning** | **Accepted, won't chase**; reopen only if a permitted value differing in `filter` ever needs one-knob attribution. |
| **13 pre-existing Snyk findings under `builder/analysis/`** | **Accepted, won't fix**; reopen if a frozen probe is un-frozen and edited, or `listen.html` is ever served. |
| **Three Snyk MEDIUMs, same rule** — `rel_discogs.py:87`, `ctc_census.py:173` **and `fcf_discogs_split.py:63`**, insecure XML parser (CWE-611) on `xml.etree.ElementTree.iterparse` over local dumps. *(This row named only the first until 2026-08-02, when a full `builder/` scan found the second; the third was found at the 2026-08-03 closeout scan and the analysis below applies identically to all three — fixing one alone would make the instances inconsistent for no exposure change.)* | **INVESTIGATED 2026-08-02, and it splits in two. Accepting the residual is the owner's, as with every row above.** Snyk reports one finding but its message names two hazards ("vulnerable to XXE and DDOS"), and they do not have the same answer here. **Tested empirically on this interpreter (3.12.13) rather than argued from the rule's title:** ① **XXE — NOT APPLICABLE.** An external entity pointing at a local file is *refused outright*: `ParseError: undefined entity`. Nothing leaks. **The cited CWE-611 is not reachable**, which also matches the rule's own scope (*"Python < 3.11"*) against this project's `>= 3.12`. ② **Entity expansion — REACHABLE.** An 11-level billion-laughs shape expanded to 8,192 characters, so the DoS half is real in principle. **Exposure for ② is the argument, and it is the same one the 13 Lows were accepted on:** the input is a 57 GB third-party dump sitting on local disk, read by a frozen offline probe; making it hostile requires local write access, which is a larger problem than a research script consuming memory, and no service parses it. **Deliberately NOT fixed:** the remedy is `defusedxml`, a new dependency, and editing a frozen probe would fire the "13 pre-existing findings" row's own reopen condition. The probe stays frozen. Probe script retained at `builder/analysis/2026-08-02-dsp-ids/` is unrelated; the XXE test itself was throwaway and its result is recorded here rather than kept as code. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. Track B's harness complied throughout (`ReadOnlyArchive`). **Condition fired again 2026-07-30** — the `TAS-`/`TD-` capture reads the archive through the same Track B helper and therefore through `ReadOnlyArchive`; complied, verified at closeout. **Stays open**: it is a standing condition on future harnesses, not a one-off to discharge. |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| ✅ **`TB-P5H-7`** | **DISCHARGED 2026-08-03 — the condition fired and was consumed.** The `CRE-` pre-registration is the successor router-pricing pre-registration, and it consumes the item as the source requires: the joint descent × delivered-payload outcome has its own pre-registered read (`CRE-C4`, read jointly with `CRE-C1` in every `CRE-R`; `CRE-R3` is the outcome class). Struck, kept for the record. |
| **The candidate-pool recompute** | **If the owner picks up the parked candidate decision.** |
| ✅ The `--prune` publish pass | **DONE 2026-08-02.** Ran `sync_frontend.py --prune --skip-build` through the module, so it kept the `FRO-1` pass ordering and the between-passes content-type probe. **Two orphans deleted** — `assets/index-C-9fM9tV.js` and `assets/index-C4yz7h5J.css`, the pre-redesign 2026-07-27 build. The bucket is now 7 objects. **The pre-flight that made it safe, and a successor should repeat it:** `--skip-build` publishes `frontend/dist` *as it stands*, so a stale or different `dist/` would have pruned the assets the live page names. Verified first that `dist/index.html` referenced exactly the two hashed assets the **live** page referenced, then ran `aws s3 sync … --delete --dryrun` to see the deletion list before running it for real. Verified after: bucket contents, `200` plus correct `Content-Type` for html/js/css/woff2/svg, and a live search returning Radiohead. Struck, kept for the record. |
| **The rate limit's headroom** | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1.** |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
