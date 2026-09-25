# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. **One exception: the
STANDING FACT block below is preserved in place across every rewrite** — it is a durable fact
about the deployment, not status, and it is the only thing here that a rewrite must carry
forward rather than replace.

**"Rewritten wholesale" means the outgoing block LEAVES, and that is not what happened for
five weeks.** Sessions rewrote the top block and demoted the old one into an archive kept
inline, then went on annotating those archived blocks at each closeout — so the file grew
monotonically from 150 lines on 2026-07-30 to **2,063** on 2026-09-05, of which 1,738 were
superseded status. **The outgoing block now moves to
[`NEXT-ARCHIVE.md`](NEXT-ARCHIVE.md) and is frozen there**, and anything in it that still
binds is distilled into the registries below *before* it goes — that distillation is the step
whose absence made keeping the whole block feel necessary. `closeout` `A2-next` owns the
procedure. **This document** is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
Track B's live in `findings/2026-07-30-track-b-cap-selection-results.md` (and its raw
`cb_scores.json`); the adopted graph's stay in
`findings/2026-07-21-scoring-adjudication.md`. Cited, never restated.

**It owns no git state either, and that is the same rule, not a second one.** Merge state,
which branches exist, what commits landed — `git` and `gh` are authoritative for all of it,
and `session-start` §C checks them anyway. **The cadence writes this file BEFORE the merge**
(work → `closeout` → the owner merges), so any merge state written here is false by
construction within the hour, and every fresh session then opens by reporting a discrepancy
that is really the process working. So: name the branch and PR number as **addresses**, and
write the owner's remaining actions as an **ordered sequence** — never as a position in one.
**A session finding this file silent on merge state has found the design, not a defect.**

> ## 📍 STANDING FACT — THE APP'S ADDRESS IS `https://unsung.fm`, since 2026-09-03
>
> The domain was bought 2026-09-02 and cut over 2026-09-03: ACM certificate swapped,
> CloudFront alias flipped, `viewer_function.js` re-synthed. **`musicapp.cmiller.io` 301s here
> with the path preserved**, so every link already shared still works. Status blocks below
> dated before 2026-09-03 name the old host and are left as written — they record what was
> live at the time. **This note survives a `closeout` rewrite: it is a standing fact about the
> deployment, not status.** The runbook is `infra/README.md` §1a.
>
> ⚠ **The app is still NAMED "Artist Path" in the DEPLOYED UI.** Only the address moved. The
> rename to "Unsung.fm" was **approved 2026-09-08** and is built on the `UXR-` branch — do not
> assume it has been deployed.

**Last updated: 2026-09-25, at the closeout that ADOPTED `LBA-A6`.** The live site is unchanged
(image and frontend `759e80c`, graph `graph-lux4.bin`). **`ApiConfig.graph_path` now names
`graph-lba-a6.bin`** on branch `charlessavage90/candidate-map-adoption-decision`. That is an
address; `git`/`gh` own the merge state.

# THE NEW MAP IS ADOPTED. THE NEXT ACTION IS THE OWNER'S: MERGE, THEN DEPLOY IT.

**`LBA-G5` PASSED and the owner ADOPTED the candidate on 2026-09-25.** His verdict is recorded verbatim,
with its reading against his pre-written criterion, in
[`2026-09-21-lbd-s4-a6-adoption-execution-log.md`](2026-09-21-lbd-s4-a6-adoption-execution-log.md) Task 6.
The artifact's identity is owned by `builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md`. The
current handoff is [`2026-09-25-HANDOFF-lba-a6-adoption.md`](2026-09-25-HANDOFF-lba-a6-adoption.md).

**THE REMAINING ACTIONS, in this order. This file does not record how far down the list anyone has
got.**

1. **The owner:** merge the adoption PR (branch above).
2. **Deploy the new map to production**, which needs his go and his AWS hands. Follow `infra/README.md`
   §4 exactly as its ⚠ block for this deploy says: `GRAPH=graph-lba-a6.bin`, **both** `s3 cp` lines,
   and `cdk diff` expected to show the graph variables changing. The image must be built from the
   merged HEAD, because it carries the search fix the new map needs. Then run the §7 sidecar check
   and correct §4's served-artifact line. **In the same deploy session:** take the direct p95
   reading on the container (#142, due now that a larger map ships).
3. **The owner:** press the two `TEST-QUEUE.md` boxes on unsung.fm after that deploy.
4. **Then his choices, none blocking:** #233 (keep the landing's re-measured sample journeys or
   pick new ones) and #200 (deepen obscurity after several Dig-deeper presses; its step 1 becomes
   a session's once the PR merges).
---

**Superseded status blocks live in [`NEXT-ARCHIVE.md`](NEXT-ARCHIVE.md), frozen and never
edited.** They are history, never status; nothing in this document depends on reading them.
Anything from them that still binds is in the registries below.

**The requirements baseline is unchanged since 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (`REQ-`) governs where it and
[`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) disagree (its §10 lists the
disagreements). **`DD-F1` remains a defect, not an accepted limitation** — Track B's `R2`
read measured where it can and cannot be moved; the results note owns that reading.

## PARKED — owner's explicit decision; his trigger, never a session's
- **Option C** (the same-name population probe), **`SEL-`**, **closing or keeping the
  2026-07-29 famous-to-famous defect ruling**, and **the three candidate path-quality fixes in
  the `CXR-` README** (each needs its own pre-registration) — all open, none blocking, all his
  trigger. *(Carried from the 2026-09-08 status block, distilled 2026-09-10.)*

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
  **⚠ The third strand was UNPARKED 2026-07-30 and has since CONCLUDED** — the `TAS-` tag
  discrimination probe ran to all eight tasks and found **neither architecture has an adoption
  case** (see "Closed" below). *Corrected 2026-09-05: this read "it is the live work; see
  'Next' above" for five weeks, and that pointer now dangles — the block it named is in
  `NEXT-ARCHIVE.md`.* Its caveats below were all carried into the
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
- ⚠ ~~**`ALG-B` adoption**~~ — **THIS ALREADY HAPPENED. Corrected 2026-09-05.** `ALG-B` is
  the **adopted map's lineage** and has been since 2026-08-06 — `graph-msw-tu50.bin` was built
  from the `ALG-B` archive (its manifest records `contribution_3`) and `ApiConfig.graph_path`
  serves it. Stated in source, at `builder/…/config.py`: *"⚠ ALG-B is the ADOPTED map's
  lineage."* Left in the parked list it would send a cold session to re-decide a month-old
  decision. **What is still open and must not be conflated with it:** `BuilderConfig.algorithm`
  still *defaults* to ALG-E deliberately, so every command touching the adopted lineage passes
  `--algorithm` explicitly (`CEX-R5`) — flipping that default is the **re-crawl** decision, it
  is his, and it is the entry in "Must not be changed" below. Whether the `REQ-38` blind listen
  this row claimed was owed was ever spent is **his to say, not this document's**; the original
  inputs (Track B's `R0`/`R2`/`R3`, `RC-R1`'s stranding figures) stand as written.
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

**Owner actions, all three discharged 2026-08-02 — kept struck for the record.** *(Heading
corrected 2026-09-05: it read "Still owed by the owner" over three items marked done.)*

1. ✅ **The use-the-app test — DONE 2026-08-02.** The redesign entry was run in full against
   `https://musicapp.cmiller.io`, desktop and phone. Everything passed; journeys he knows well
   were **unchanged**, which was the check that mattered. One incidental finding worth
   carrying: **the loading screen is often too fast to see**, so nothing should be measured or
   redesigned on the assumption a user experiences it.
2. ✅ **The iPhone script — DONE 2026-08-02, and it settled a Gate 3 blocker.** All three
   questions clean: clips play, the bottom bar clears the home indicator, artist-name typing is
   unaffected. **`G3-F2` is FALSIFIED** — see the gate table below.
3. ✅ **The `--prune` publish pass — DONE 2026-08-02.** Two orphaned assets from the
   pre-redesign build deleted; live site verified afterwards. See `NEXT-ARCHIVE.md`'s *The `--prune` publish pass* row for the
   pre-flight a successor should repeat.

~~**One action is owed by the owner: merging draft PR #69.**~~ *(Discharged — #69 merged
2026-08-03 at `2e3b017`. Struck 2026-09-05, having read as a live owner action for a month.
**Current owner actions live in the top block, never here.** This section is the
parked-decision registry; status accumulating in it is what made the whole document grow.)*

~~**Nothing is queued in [`TEST-QUEUE.md`](TEST-QUEUE.md).**~~ *(FALSE since 2026-09-04;
struck 2026-09-05. **This document must not state the queue's contents at all** — the same rule
as merge state. `TEST-QUEUE.md` owns it and `session-start` reads it. **Since 2026-09-12 a live
item is an unticked `- [ ]` box** — that file is a checklist now, and the "topmost heading" rule
this note used to give applies only to the two archives, where discharged prose entries keep their
old heading.)*

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.
*(Verified 2026-09-05 — still the password-removal plan's only unrun task.)*

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`, #196). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). **One blocker removed 2026-08-02: `G3-F2` is FALSIFIED** — HIGH, "blocking if confirmed", and the review named the deciding test (*"one tap on a real device confirms or kills it"*). Clips play on a real iPhone. ⚠ **Read what that does not mean:** the code was NOT changed to achieve it — `usePlayer.ts:49` still awaits the URL before `player.play(url)` at line 60, which is exactly the pattern the review flagged. The finding's *description* was accurate; only its *consequence* is removed, and it rests on iOS's current tolerance rather than on the code being correct by construction. **Do not cite this as "the iOS play path is correct."** **What remains open is tracked in the GitHub milestone *Gate 3 — public*** — re-checked against the code 2026-09-24 and filed as issues: `G3-A1`/`S1` capacity (#172), `G3-A2`'s headroom residual (#173), `G3-S2` (#174), `G3-Q1` (#175), `G3-Q2` (#176), `G3-F1` (#177), `G3-S4` (#178). *(This row said the rest of the blocking set was "untouched" until 2026-09-24; PW-1–PW-7 had fixed `G3-A4` and `G3-S3` and closed `G3-A2` as recorded — see *Closed* below.)* |

## Closed — do not re-plan or re-investigate

- **`LBA-A6` is ADOPTED (2026-09-25), and both of its human verdicts are run-once and final**:
  `LAL-R1` (the blind listen) and `LBA-G5` (the use gate). Neither is re-run or re-read, and no
  verdict carries across listens. Reasons: `LBA-AM5`, `LBA-AM6-10`, execution log Task 6.
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
    the same name*. Not path work and not inside any pause. The builder carries
    MusicBrainz-recorded Deezer artist ids in the APG1 metadata blob and the api resolves by
    identity before falling back to name search.
    **⚠ CORRECTED 2026-09-05. This entry read "a fix is BUILT and is INERT until a rebuild"
    and "the defect is unchanged in the running app, which serves a pre-2026-08-02 artifact
    with no ids". Both have been FALSE since 2026-08-06**, when the `MSW-` rebuild landed:
    the served artifact `graph-msw-tu50.bin` (sha `43dd82bb…`) carries **`deezer_ids` for all
    58,838 artists**, read from the artifact's own metadata blob rather than inferred.
    **The fix is LIVE.** It is *reduced*, not closed — the id path inherits MusicBrainz's
    link accuracy; the link-quality deferral (issue #158) is unaffected and still
    governs.

## Must not be changed, and each has a reason
- **Both `LBL-` blind-listen verdicts are RUN-ONCE and FINAL** (`GBL-` §5). Listen 1 (served map
  against `LBD-A0V`, 2026-09-11) and listen 2 (`LBD-A0V` against `LBD-A5V`, 2026-09-13) each read
  **`LBL-R2`, the tie**. Neither may be re-listened on any protocol; **no verdict carries across
  them**; `REQ-41` bars reading either as equivalence; and **neither adopts anything** — `S4` owns
  adoption and `V` is an experimental control, never a population rule. Figures and barred reads:
  [`findings/2026-09-11-lbl-listen1-results.md`](findings/2026-09-11-lbl-listen1-results.md) and
  [`findings/2026-09-13-lbl-listen2-results.md`](findings/2026-09-13-lbl-listen2-results.md) §5.
  ⚠ **`LBD-X6` bars generalising listen 2's result to the cheaper pairing form — and it STILL
  DOES.** Its condition (*"until `LBD-A4` has run and `R10` has been read"*) was **discharged
  2026-09-13**, and `R10` **fired**, so the bar is **confirmed rather than lifted**. Reading the
  met condition as a lifted bar inverts the result.
- **Every `S4` arm records which pairing semantics it uses and why** (`LBD-D6`). This stopped
  being bookkeeping on **2026-09-13**: `LBD-A4` ran and **`R10` fired** on the edge-count half,
  so the pairing form is **load-bearing** and two arms differing in it are not comparable.
  `LBD-R4` is thereby retired as a risk and confirmed as a fact. Figures:
  [`../../builder/analysis/2026-09-13-lbd-a4/README.md`](../../builder/analysis/2026-09-13-lbd-a4/README.md) §§6–7.
  ⚠ **`R10` says the choice MATTERS; it says nothing about which form is BETTER.**
- **`LBD-G1` also fires on `LBD-A4` (2026-09-13), and `LBD-AM3`'s override does NOT name that
  arm** — it enumerates `LBD-A0`–`LBD-A3`. `R10` was read anyway because its bar is a
  *difference between arms*, so a lineage gap common to both cancels; the reasoning is the
  `LBD-A4` README's §5. **Whether the override extends to `LBD-A4` as an ABSOLUTE fidelity
  statement is the owner's and is open.** Do not widen it silently. **`LBD-C1` is not cited as
  passed for either arm.**
- **`LBD-C2a`, `LBD-C2b` and `LBD-M1` were deliberately NOT taken on `LBD-A4`.** Their reads
  (`LBD-G2`, `R4`–`R12`) were pre-registered for the four `T`-derived arms only; taking one now,
  with results in hand, needs an amendment first.
- **`LBD-G1` fired (2026-09-09) and was overridden by owner decision (`LBD-AM3`, 2026-09-10)
  after a diagnosis.** The 0.5844 reading and the 0.60 floor both stand; the arms were read
  anyway. Never cite `LBD-C1` as "passed", and never re-read that gate on the dated corpus for
  the record — `C1-DIAG-1` is a diagnostic. `--created-before` in `lbd_similarity.py` is
  likewise diagnostic and is never set for an arm.
- **`LBD-AM4` (2026-09-10): the build-stage population is an EXPERIMENTAL CONTROL, not a
  population rule.** `LBD-A0`/`A2` were built over exactly the extended map's 88,685 artists so
  each differs from the ceiling probe's bridge control in the data alone; `S4` decides the
  shipped population separately. **`drop_unlistenable=True` via the `20260809` override
  supersedes `LBD-X3`'s `False` for that population ONLY** (measured inert: zero drops in both
  builds); `LBD-X3` stays right for any arm over the table's own population. **`LBD-A3` is
  barred from building**, not deferred. And the `A0`-vs-served-map gap is a bundle of lineage
  terms — never cite it as the reimplementation's effect.
- **`LBD-AM5` (2026-09-10) and the `LBL-` listen 1 (2026-09-11): the same shape, one level up.**
  The served population `V` is an **experimental control, not a population rule** — `S4` still
  owns the shipped population, the fame source, API sizing and a refresh procedure, and **no
  listen outcome adopts anything.** **`LBD-X4` and `LBD-X5` travel with every listen-1
  sentence**: 439 artists took part in the served build's cap step and could not in
  `LBD-A0V`'s, and the served-vs-`LBD-A0V` data gap is a bundle (corpus age, the absent
  `filter_True`, today's mapping, the uncredited band-member class, our tie-break) — **no
  attribution to "the data", and none inside the bundle.** **The listen-1 verdict may not be
  re-listened** (`GBL-` §5's run-once rule); a further listen is a new amendment on new pairs. **`LBD-AM6` (2026-09-12) is that amendment**, and adds two bars of its
  own: the pairs were selected on the **magnitude** of the two maps' difference and on
  unfamiliarity, **never on direction** — a screen that saw direction would invalidate the listen;
  and **`LBD-X6`**, listen 2's result may not be generalised to the cheaper pairing form until
  `LBD-A4` has run and `R10` has been read. **Pick strength is recorded but never tallied.**
  The drop list for `V` is the served lineage's `20260805` file, never `LBD-AM4`'s `20260809`,
  which would drop 31 served artists. **The owner's closing note changed no number** — the
  findings note's §1.5 carries the arithmetic — and his "slight"/"strong" wording is not a
  strength coding and must not be tallied as one.
- **`top1pct_degree_mass_frac` is saturation-degenerate** (2026-09-08): where at least 1 % of
  nodes sit at the degree bound it reduces to the bound over a hundred times mean degree and
  cannot see edge arrangement. The `DCF-` README's forward note names which of its own arms the
  measure is valid on; its numbers are untouched.
- **`CRS-C3` was structurally unable to fire on any selectable Track B cell** (2026-09-08), so
  its null carried no information about concentration. Track B's results document is unedited
  and carries the correction at its head. It says nothing about `CRS-C4`, overturns none of
  Track B's conclusions, and is not evidence about any cap rule.
- **Pin `--archive-dir scratch/grt-archive-algb.pre-cex-snapshot` for any build of the served
  lineage.** The ALG-B archive tree gained tens of thousands of response files after the served
  map was built; an unpinned rebuild reads the extended crawl (`CXA-` leftover).
- **Rulings of 2026-09-04, not to be re-litigated or re-discharged:** the 2026-09-03 address
  test (run and passed), either 2026-09-01 test-queue entry, and the depth-0 half of the
  owner's revert report — NOT a defect and NOT open work. That closed them as items and
  overturned no measurement: `CXR-P3`'s null and the diagnosis README's "unexplained by anything
  here" remain exactly true. And do not re-queue "tell me how it feels" (owner ruling,
  2026-08-07): his long-run evaluation is continuous and `TEST-QUEUE.md` does not hold it.

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
  re-crawl decision. (Verified 2026-09-05: `PRODUCTION_ALGORITHM` = ALG-E, `…contribution_5…`.)
- ⚠ **`cap_strategy` is `trimmed_union`, NOT `mutual_knn`** — corrected 2026-09-05. This entry
  read `mutual_knn` because it was written before `MSW-` flipped it on 2026-08-06, and the
  block recording that flip was demoted into the archive without the registry being updated.
  It is the first distillation defect the split found, and it is the exact shape the archive
  header warns about. The live knobs are **`union_top_j = 50` and `union_degree_ceiling = 50`**;
  `max_neighbours_per_artist = 50` is still set but is **ignored under `trimmed_union`**, so
  reading it as the live degree bound is wrong. `mutual_knn` remains supported, and every
  pre-2026-08-06 figure was measured under it — **check which rule a claim is in.**

## Deferred, with conditions — now GitHub issues

**Since 2026-09-24 every open deferral is a GitHub issue**, not a row here: labelled `deferred` (or `bug` /
`security` where that is its kind), with its condition, whose it is, and what done means in the body.
Conventions and the lifecycle are owned by [`ISSUES.md`](ISSUES.md); the registry as it stood is frozen in
[`NEXT-ARCHIVE.md`](NEXT-ARCHIVE.md) (block dated 2026-09-24). **Re-test the conditions, not only list them:**

```bash
gh issue list --state open --label deferred --limit 100
gh issue list --state open --label agent-ready   # condition met and a session's: dispatchable
```

## Accepted residuals and standing conditions — decisions, not work

Not issues, because nothing here is to be done: each is accepted, or binds future work as a standing
condition. **A new accepted residual is an issue closed as *not planned*** (`ISSUES.md` §4); a new standing
condition goes in *Must not be changed* above.

| Finding | Condition |
|---|---|
| **A worldly-fame instrument does not exist** | **Accepted; claims in that currency are barred until one does** (Definitions ruling). Reopen only if a product need for worldly fame appears — the `RCS-` corpus and its committed hand values are the reusable starting point. |
| **The TJ Brown late hand read** (8,274 monthly listeners, ruler 218) | **Usable by a future corpus at design time only** — never a post-hoc addition to a read set (log §5a). |
| **One new Snyk Low finding per module added under `builder/analysis/`** — *but only for modules taking a CLI path argument.* **The three added 2026-08-02 (`dsp_ids.py`, `delivered_coverage.py`, `id_quality.py`) contribute NONE**, the same reason `tail_exposure.py` did not: no CLI argument, so no input reaches a path. Full `builder/` scan at that closeout returns **32** — 27 Path Traversal Lows, 3 DOM-XSS in `listen.html`, 2 XML-parser Mediums (issue #168). *(2026-08-03 later: `wav_read.py` adds **2** of the same class — `--capture`/`--out` — recorded at its pre-registration commit; the eleven `cre_probe*.py` scripts add none, no CLI path arguments.)* | **Recorded, not fixed; extending the acceptance is the owner's.** A CLI `--out` path flows into `pathlib.Path` — the same class as the 13 already accepted here, **now 11 in the `TAS-` directory plus 6 in the `WGT-` directory** (`wgt_grid.py` ×2, `wgt_release_read.py` ×2, `wgt_style_filters.py` ×2). *(Corrected 2026-08-01 latest: this row said **4** and omitted `wgt_style_filters.py`'s two, which a re-scan surfaced. `tail_exposure.py` added the same day contributes **none** — it takes no CLI argument, so no input reaches a path.)* It cannot be meaningfully sanitised: captures deliberately live *outside* the repo, so confining the path breaks intended usage. |
| **42 ListenBrainz nulls and 24 MBIDs refused as ambiguous** | **Accepted, won't chase.** Both are recorded in the probe JSON. Reopen only if a criterion is built that depends on those specific artists being scored. |
| **`REL-3`'s ratio bar is degenerate and must not be reused as written** | **Before any successor pre-registration expresses a bar as a multiple of a null.** The null median was exactly zero, so "≥ 3× the null" was satisfied by a division by zero. A ratio bar needs a stated floor on the denominator, or a difference bar instead. |
| **The `LBS` `filter` token's meaning** | **Accepted, won't chase**; reopen only if a permitted value differing in `filter` ever needs one-knob attribution. |
| **13 pre-existing Snyk findings under `builder/analysis/`** | **Accepted, won't fix**; reopen if a frozen probe is un-frozen and edited, or `listen.html` is ever served. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. Track B's harness complied throughout (`ReadOnlyArchive`). **Condition fired again 2026-07-30** — the `TAS-`/`TD-` capture reads the archive through the same Track B helper and therefore through `ReadOnlyArchive`; complied, verified at closeout. **Stays open**: it is a standing condition on future harnesses, not a one-off to discharge. |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:12` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |

